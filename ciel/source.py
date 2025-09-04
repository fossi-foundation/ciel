# Copyright 2025 The American University in Cairo
#
# Modified from the Volare project
#
# Copyright 2022-2023 Efabless Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import re
import sys
from dataclasses import dataclass
from typing import Dict, ClassVar, List, Tuple, Type, Callable

import click
import httpx

from .github import GitHubSession, RepoInfo
from .common import Version, date_from_iso8601


@dataclass
class Asset:
    content: str
    filename: str
    url: str


class DataSource(object):
    factory: ClassVar[Dict[str, Type["DataSource"]]] = {}
    default: ClassVar["DataSource"]

    def __init__(self, argument: str):
        raise NotImplementedError()

    def get_available_versions(self, pdk: str) -> List[Version]:
        raise NotImplementedError()

    def get_downloads_for_version(
        self, version: Version
    ) -> Tuple[httpx.Client, List[Asset]]:
        raise NotImplementedError()


class GitHubReleasesDataSource(DataSource):
    def __init__(self, repo_id: str):
        self.session = GitHubSession()
        self.repo = RepoInfo.from_id(repo_id)

    def get_available_versions(self, pdk: str) -> List[Version]:
        page = 1
        last = self.session.api(
            self.repo,
            "/releases",
            "get",
            params={"page": 1, "per_page": 100},
        )
        releases = last
        while len(last) == 100:
            page += 1
            last = self.session.api(
                self.repo,
                "/releases",
                "get",
                params={"page": page, "per_page": 100},
            )
            releases += last

        versions = []
        commit_rx = re.compile(r"released on ([\d\-\:TZ]+)")
        for release in releases:
            if release["draft"]:
                continue

            family, hash = release["tag_name"].rsplit("-", maxsplit=1)

            if pdk != family:
                continue

            upload_date = date_from_iso8601(release["published_at"])
            commit_date = None

            commit_date_match = commit_rx.search(release["body"])
            if commit_date_match is not None:
                commit_date = date_from_iso8601(commit_date_match[1])

            remote_version = Version(
                name=hash,
                pdk=family,
                commit_date=commit_date,
                upload_date=upload_date,
                prerelease=release["prerelease"],
            )
            versions.append(remote_version)

        versions.sort(reverse=True)
        if len(versions) == 0:
            raise ValueError(
                f"No versions found for '{pdk}' on github.com/{self.repo.id}"
            )
        return versions

    def get_downloads_for_version(
        self, version: Version
    ) -> Tuple[httpx.Client, List[Asset]]:
        release = self.session.api(
            self.repo,
            f"/releases/tags/{version.pdk}-{version.name}",
            "get",
        )

        assets = release["assets"]
        zst_files = []
        for asset in assets:
            if asset["name"].endswith(".tar.zst"):
                content = asset["name"][:-8]
                zst_files.append(
                    Asset(content, asset["name"], asset["browser_download_url"])
                )
        return (self.session, zst_files)


DataSource.factory["github-releases"] = GitHubReleasesDataSource


class StaticWebDataSource(DataSource):
    def __init__(self, base_url: str):
        self.session = GitHubSession()
        self.base_url = base_url

    def get_available_versions(self, pdk: str) -> List[Version]:
        req = self.session.request("GET", self.base_url + f"/{pdk}/manifest.json")
        try:
            req.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ValueError(
                    f"No versions found for '{pdk}' at '{self.base_url}'"
                ) from None
            else:
                raise e from None
        try:
            manifest = req.json()
        except ValueError as e:
            raise ValueError(f"Request {req.url} returned invalid JSON: {e}") from None

        versions = []
        for version in manifest["versions"]:
            remote_version = Version(
                name=version["version"],
                pdk=manifest["pdk"],
                commit_date=date_from_iso8601(version["date"]),
                prerelease=version.get("prerelease", False),
            )
            versions.append(remote_version)

        versions.sort(reverse=True)
        if len(versions) == 0:
            raise ValueError(f"No versions found for '{pdk}' on '{self.base_url}'")
        return versions

    def get_downloads_for_version(
        self, version: Version
    ) -> Tuple[httpx.Client, List[Asset]]:
        req = self.session.request(
            "GET", self.base_url + f"/{version.pdk}/{version.name}/manifest.json"
        )
        try:
            req.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ValueError(
                    f"Manifest for '{version.pdk}/{version.name}' at '{self.base_url}'"
                ) from None
            else:
                raise e from None
        try:
            manifest = req.json()
        except ValueError as e:
            raise ValueError(f"Request {req.url} returned invalid JSON: {e}") from None

        assets = []
        for asset in manifest["assets"]:
            assets.append(Asset(**asset))
        return (self.session, assets)


DataSource.factory["static-web"] = StaticWebDataSource


def data_source_cb(
    ctx: click.Context,
    param: click.Parameter,
    value: str,
):
    source_id = value
    elements = source_id.split(":", maxsplit=1)
    if len(elements) != 2:
        print(
            "Data source must be in the format '{{class_id}}:{{argument}}' where class_id is one of:",
            file=sys.stderr,
        )
        for id in DataSource.factory:
            print(f"* {id}", file=sys.stderr)
        ctx.exit(-1)
    cls_id, target = elements
    cls = DataSource.factory.get(cls_id)
    if cls is None:
        print(
            f"Unknown data source class '{cls_id}', must be one of:",
            file=sys.stderr,
        )
        for id in DataSource.factory:
            print(f"* {id}", file=sys.stderr)
        ctx.exit(-1)
    return cls(target)


def opt_data_source(function: Callable) -> Callable:
    function = click.option(
        "--data-source",
        default="static-web:https://fossi-foundation.github.io/ciel-releases",
        envvar=["CIEL_DATA_SOURCE"],
        required=False,
        show_default=True,
        help="The data source to use for operations that may require contacting a remote server, in the format '{class_id}:{argument}'",
        callback=data_source_cb,
    )(function)
    return function

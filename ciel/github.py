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
import os
import sys
import click
import subprocess
from datetime import datetime
from dataclasses import dataclass
from typing import Any, ClassVar, Optional, Callable

import httpx
import ssl
from .__version__ import __version__


@dataclass
class RepoInfo:
    owner: str
    name: str

    @classmethod
    def from_id(self, id_str: str) -> "RepoInfo":
        return RepoInfo(*id_str.split("/", maxsplit=1))

    @property
    def id(self):
        return f"{self.owner}/{self.name}"

    @property
    def link(self):
        return f"https://github.com/{self.id}"

    @property
    def api(self):
        return f"https://api.github.com/repos/{self.id}"


opdks_repo = RepoInfo(
    os.getenv("OPDKS_REPO_OWNER", "RTimothyEdwards"),
    os.getenv("OPDKS_REPO_NAME", "open_pdks"),
)

ihp_repo = RepoInfo(
    os.getenv("IHP_REPO_OWNER", "IHP-GmbH"),
    os.getenv("IHP_REPO_NAME", "IHP-Open-PDK"),
)


class GitHubSession(httpx.Client):
    class Token(object):
        override: ClassVar[Optional[str]] = None

        @classmethod
        def get_gh_token(Self) -> Optional[str]:
            token = None

            # 0. Lowest priority: ghcli
            try:
                token = subprocess.check_output(
                    ["gh", "auth", "token"],
                    encoding="utf8",
                ).strip()
            except Exception:
                pass

            # 1. Higher priority: environment GITHUB_TOKEN
            env_token = os.getenv("GITHUB_TOKEN")
            if env_token is not None and env_token.strip() != "":
                token = env_token

            # 2. Highest priority: the -t flag
            if Self.override is not None:
                token = Self.override

            return token

    def __init__(
        self,
        *,
        follow_redirects: bool = True,
        github_token: Optional[str] = None,
        ssl_context=None,
        **kwargs,
    ):
        if ssl_context is None:
            try:
                import truststore

                ssl_context = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            except ImportError:
                pass

        try:
            super().__init__(
                follow_redirects=follow_redirects,
                verify=ssl_context,
                **kwargs,
            )
        except ValueError as e:
            if "Unknown scheme for proxy URL" in e.args[0] and "socks://" in e.args[0]:
                print(
                    f"Invalid SOCKS proxy: Ciel only supports http://, https:// and socks5:// schemes: {e.args[0]}",
                    file=sys.stderr,
                )
                exit(-1)
            else:
                raise e from None
        github_token = github_token or GitHubSession.Token.get_gh_token()
        self.github_token = github_token

        raw_headers = {
            "User-Agent": type(self).get_user_agent(),
        }
        if github_token is not None:
            raw_headers["Authorization"] = f"Bearer {github_token}"
        self.headers = httpx.Headers(raw_headers)

    def api(
        self,
        repo: RepoInfo,
        endpoint: str,
        method: str,
        *args,
        **kwargs,
    ) -> Any:
        url = repo.api + endpoint
        req = self.request(method, url, *args, **kwargs)
        req.raise_for_status()
        try:
            return req.json()
        except ValueError as e:
            raise ValueError(f"Request {req.url} returned invalid JSON: {e}") from None

    @classmethod
    def get_user_agent(Self) -> str:
        return f"ciel/{__version__}"


def get_commit_date(
    commit: str,
    repo: RepoInfo,
    session: Optional[GitHubSession] = None,
) -> Optional[datetime]:
    if session is None:
        session = GitHubSession()

    try:
        response = session.api(repo, f"/commits/{commit}", "get")
    except httpx.HTTPError:
        return None

    date = response["commit"]["author"]["date"]
    commit_date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
    return commit_date


def set_token_cb(
    ctx: click.Context,
    param: click.Parameter,
    value: Optional[str],
):
    GitHubSession.Token.override = value


def opt_github_token(function: Callable) -> Callable:
    function = click.option(
        "-t",
        "--github-token",
        default=None,
        required=False,
        expose_value=False,
        show_default=True,
        help="Replace the token used for GitHub requests, which is by default the value of the environment variable GITHUB_TOKEN or None.",
        callback=set_token_cb,
    )(function)
    return function

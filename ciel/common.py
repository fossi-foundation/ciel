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
import shutil
import pathlib
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, List

from .families import Family

# -- Assorted Helper Functions
ISO8601_FMT = "%Y-%m-%dT%H:%M:%SZ"


def date_to_iso8601(date: datetime) -> str:
    return date.strftime(ISO8601_FMT)


def date_from_iso8601(string: str) -> datetime:
    return datetime.strptime(string, ISO8601_FMT)


def mkdirp(path):
    return pathlib.Path(path).mkdir(parents=True, exist_ok=True)


# -- API Variables

# -- PDK Root Management
VOLARE_DEFAULT_HOME = os.path.join(os.path.expanduser("~"), ".ciel")
VOLARE_RESOLVED_HOME = os.getenv("PDK_ROOT") or VOLARE_DEFAULT_HOME


def _get_current_version(pdk_root: str, pdk: str) -> Optional[str]:
    current_file = os.path.join(get_ciel_dir(pdk_root, pdk), "current")
    current_file_dir = os.path.dirname(current_file)
    mkdirp(current_file_dir)
    version = None
    try:
        version = open(current_file).read().strip()
    except FileNotFoundError:
        pass

    return version


def get_ciel_home(pdk_root: Optional[str] = None) -> str:
    return pdk_root or VOLARE_RESOLVED_HOME


def get_ciel_dir(pdk_root: str, pdk: str) -> str:
    return os.path.join(pdk_root, "ciel", pdk)


def get_versions_dir(pdk_root: str, pdk: str) -> str:
    return os.path.join(get_ciel_dir(pdk_root, pdk), "versions")


@dataclass
class Version(object):
    name: str
    pdk: str
    commit_date: Optional[datetime] = None
    upload_date: Optional[datetime] = None
    prerelease: bool = False

    def __lt__(self, rhs: "Version"):
        return (self.commit_date or datetime.min) < (rhs.commit_date or datetime.min)

    def __str__(self) -> str:
        return self.name

    def is_installed(self, pdk_root: str) -> bool:
        version_dir = self.get_dir(pdk_root)
        return os.path.isdir(version_dir)

    def is_current(self, pdk_root: str) -> bool:
        return self.name == _get_current_version(pdk_root, self.pdk)

    def get_dir(self, pdk_root: str) -> str:
        return os.path.join(get_versions_dir(pdk_root, self.pdk), self.name)

    def unset_current(self, pdk_root: str):
        if not self.is_installed(pdk_root):
            return
        if not self.is_current(pdk_root):
            return

        for variant in Family.by_name[self.pdk].variants:
            try:
                os.unlink(os.path.join(pdk_root, variant))
            except FileNotFoundError:
                pass

        current_file = os.path.join(get_ciel_dir(pdk_root, self.pdk), "current")
        os.unlink(current_file)

    def uninstall(self, pdk_root: str):
        if not self.is_installed(pdk_root):
            raise ValueError(
                f"Version {self.name} of the {self.pdk} PDK is not installed."
            )

        self.unset_current(pdk_root)

        version_dir = self.get_dir(pdk_root)

        shutil.rmtree(version_dir)

    @classmethod
    def get_current(Self, pdk_root: str, pdk: str) -> Optional["Version"]:
        current_version = _get_current_version(pdk_root, pdk)
        if current_version is None:
            return None

        return Version(current_version, pdk)

    @classmethod
    def get_all_installed(Self, pdk_root: str, pdk: str) -> List["Version"]:
        versions_dir = get_versions_dir(pdk_root, pdk)
        mkdirp(versions_dir)
        return [
            Version(
                name=version,
                pdk=pdk,
            )
            for version in os.listdir(versions_dir)
            if os.path.isdir(os.path.join(versions_dir, version))
        ]


def resolve_version(
    version: Optional[str],
    tool_metadata_file_path: Optional[str],
) -> str:
    """
    Takes an optional version and tool_metadata_file_path.

    If version is set, it is returned.

    If not, tool_metadata_file_path is checked if it exists.

    If not specified, ./tool_metadata.yml and ./dependencies/tool_metadata.yml
    are both checked if they exist.

    If none are specified, execution is halted.

    Otherwise, the resulting metadata file is parsed for an open_pdks version,
    which is then returned.
    """
    if version is not None:
        return version

    import yaml

    if tool_metadata_file_path is None:
        tool_metadata_file_path = os.path.join(".", "tool_metadata.yml")
        if not os.path.isfile(tool_metadata_file_path):
            tool_metadata_file_path = os.path.join(
                ".", "dependencies", "tool_metadata.yml"
            )
            if not os.path.isfile(tool_metadata_file_path):
                raise FileNotFoundError(
                    "Any of ./tool_metadata.yml or ./dependencies/tool_metadata.yml not found. You'll need to specify the file path or the commits explicitly."
                )

    tool_metadata = yaml.safe_load(open(tool_metadata_file_path).read())

    open_pdks_list = [tool for tool in tool_metadata if tool["name"] == "open_pdks"]

    if len(open_pdks_list) < 1:
        raise ValueError("No entry for open_pdks found in tool_metadata.yml")

    version = open_pdks_list[0]["commit"]

    return version

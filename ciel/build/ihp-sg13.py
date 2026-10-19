# Copyright 2025 Ciel Contributors
#
# Adapted from the Volare project
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
from datetime import datetime, timezone
from typing import Dict, List, Optional

from rich.console import Console

from ..common import (
    get_ciel_dir,
    mkdirp,
)
from ..families import Family
from .common import fetch_sources, install_build, trivial_build

FAMILY_INFO = Family.by_name["freepdk45"]


def build(
    pdk_root: str,
    pdk_variant: str,
    version: str,
    jobs: int = 1,
    clear_build_artifacts: bool = True,
    include_libraries: Optional[List[str]] = None,
    using_repos: Optional[Dict[str, str]] = None,
):
    console = Console()
    if include_libraries is not None:
        console.log(
            "Note: all libraries will be acquired as part of the trivial PDK build."
        )

    if using_repos is None:
        using_repos = {}

    build_directory = os.path.join(
        get_ciel_dir(pdk_root, FAMILY_INFO.name), "build", version
    )
    timestamp = datetime.now(timezone.utc).strftime(
        f"build_{FAMILY_INFO.name}-%Y-%m-%d-%H-%M-%S"
    )
    log_dir = os.path.join(build_directory, "logs", timestamp)
    mkdirp(log_dir)

    console.log(f"Logging to '{log_dir}'…")

    source_path = fetch_sources(
        console, FAMILY_INFO, build_directory, version, jobs, using_repos.get("ihp")
    )
    trivial_build(FAMILY_INFO, build_directory, source_path)
    install_build(console, FAMILY_INFO, build_directory, pdk_root, version)

    if clear_build_artifacts:
        shutil.rmtree(build_directory)

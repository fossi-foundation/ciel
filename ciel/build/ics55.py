# Copyright 2026 Ckristian Duran
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
import subprocess
from datetime import datetime
from typing import Optional, List, Tuple, Dict
from concurrent.futures import ThreadPoolExecutor

from rich.console import Console
from rich.progress import Progress

from .git_multi_clone import GitMultiClone
from ..families import Family
from ..github import ics55_open_repo
from ..common import (
    Version,
    get_ciel_dir,
    mkdirp,
)


def get_ics55(
    version, build_directory, jobs=1, repo_path=None
) -> Tuple[str, Optional[str], Optional[str]]:
    try:
        console = Console()

        if repo_path is None:
            with Progress() as progress:
                with ThreadPoolExecutor(max_workers=jobs) as executor:
                    gmc = GitMultiClone(build_directory, progress)
                    ics_future = executor.submit(
                        GitMultiClone.clone,
                        gmc,
                        ics55_open_repo.link,
                        version,
                    )
                    repo = ics_future.result()
                    current_task = progress.add_task("Updating submodules…", total=100)
                    repo.init_submodule(
                        callback=lambda x: progress.update(current_task, completed=x)
                    )
                    repo_path = repo.path
            console.log(f"Done fetching {ics55_open_repo.name}.")
        else:
            console.log(f"Using ICS55 at {repo_path} unaltered.")

        return repo_path

    except subprocess.CalledProcessError as e:
        print(e)
        print(e.stderr)
        exit(-1)


def build_ics(build_directory, ics55_path, log_dir):
    # """Build"""
    try:
        shutil.rmtree(os.path.join(build_directory, "ics55"))
    except FileNotFoundError:
        pass

    # Execute the install
    console = Console()
    def run_sh(script, log_to):
        output_file = open(log_to, "w")
        try:
            subprocess.check_call(
                ["bash", "-c", script],
                cwd=ics55_path,
                stdout=output_file,
                stderr=output_file,
                stdin=open(os.devnull),
            )
        except subprocess.CalledProcessError as e:
            console.log(
                f"An error occurred while building the PDK. Check {log_to} for more information."
            )
            raise e

    config_log = os.path.join(log_dir, "config.log")
    console.log(f"Downloading and installing PDK. Logging into {config_log}")
    run_sh("make openpdk", log_to=config_log)

    shutil.copytree(
        os.path.join(ics55_path, "ics55"),
        os.path.join(build_directory, "ics55"),
        ignore=lambda dir, files: (
            files if ".git" in os.path.split(dir) else [".git", ".DS_Store"]
        ),
    )


def install_ics(build_directory, pdk_root, version):
    console = Console()
    with console.status("Adding build to list of installed versions…"):
        ics55_family = Family.by_name["ics55"]

        version_directory = Version(version, "ics55").get_dir(pdk_root)
        if (
            os.path.exists(version_directory)
            and len(os.listdir(version_directory)) != 0
        ):
            backup_path = version_directory
            it = 0
            while os.path.exists(backup_path) and len(os.listdir(backup_path)) != 0:
                it += 1
                backup_path = Version(f"{version}.bk{it}", "ics55").get_dir(
                    pdk_root
                )
            console.log(
                f"Build already found at {version_directory}, moving to {backup_path}…"
            )
            shutil.move(version_directory, backup_path)

        console.log("Copying…")
        mkdirp(version_directory)

        for variant in ics55_family.variants:
            variant_build_path = os.path.join(build_directory, variant)
            variant_install_path = os.path.join(version_directory, variant)
            if os.path.isdir(variant_build_path):
                shutil.copytree(variant_build_path, variant_install_path)

    console.log("Done.")


def build(
    pdk_root: str,
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
        get_ciel_dir(pdk_root, "ics55"), "build", version
    )
    timestamp = datetime.now().strftime("build_ics55-%Y-%m-%d-%H-%M-%S")
    log_dir = os.path.join(build_directory, "logs", timestamp)
    mkdirp(log_dir)

    console.log(f"Logging to '{log_dir}'…")

    ics55_path = get_ics55(version, build_directory, jobs, using_repos.get("ics"))
    build_ics(build_directory, ics55_path, log_dir)
    install_ics(build_directory, pdk_root, version)

    if clear_build_artifacts:
        shutil.rmtree(build_directory)

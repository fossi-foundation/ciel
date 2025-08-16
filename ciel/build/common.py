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
import re
import shutil
import subprocess

from ciel.github import GitHubSession


def get_backup_path(at_path: str):
    backup_path = at_path
    ctr = -1
    while os.path.exists(backup_path):
        ctr += 1
        postfix = f".bak{str(ctr) * bool(ctr)}"
        backup_path = f"{at_path}{postfix}"
    return backup_path


def open_pdks_fix_makefile_provenance(at_path: str):
    backup_path = get_backup_path(at_path)
    shutil.move(at_path, backup_path)

    fix_fi = False

    unpatched_rx = re.compile(r"[^$]\${(\w+)_COMMIT\}")

    with open(backup_path, "r") as file_in, open(at_path, "w") as file_out:
        for line in file_in:
            # This patch makes it so the subshells parse this as an assignment
            # and not as a command. (a=b valid, a = b not valid)
            if "_COMMIT = `" in line:
                line = line.replace("_COMMIT = ", "_COMMIT=")
            # This patch makes it so the _COMMIT assignment is propagated to
            # the next if block instead of the next if block being run in
            # another subshell.
            if fix_fi:
                file_out.write(line.replace("fi", "fi ; \\"))
                fix_fi = False
            else:
                file_out.write(line)
            if "_COMMIT=`" in line:
                fix_fi = True
            # This patch fixes the _COMMIT interpolation being at the Makefile
            # level rather than the shell level.
            if "download.sh" in line:
                file_out.write(unpatched_rx.sub(r" $${\1_COMMIT}", line))
            else:
                file_out.write(line)


def open_pdks_patch_gnu_sed(at_path: str):
    backup_path = get_backup_path(at_path)
    shutil.move(at_path, backup_path)

    with open(backup_path, "r") as file_in, open(at_path, "w") as file_out:
        for line in file_in:
            file_out.write(line.replace("${SED} -i ", "${SED} -i.bak "))


def patch_open_pdks(at_path: str):
    """
    This functions applies various patches based on the current version of
    open_pdks in use.
    """
    head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=at_path, encoding="utf8"
    ).strip()

    def is_ancestor(commit: str):
        nonlocal head, at_path
        return (
            subprocess.call(
                ["git", "merge-base", "--is-ancestor", commit, head],
                stdout=open(os.devnull, "w"),
                stderr=open(os.devnull, "w"),
                cwd=at_path,
            )
            == 0
        )

    can_build = is_ancestor(
        "c74daac794c83327e54b91cbaf426f722574665c"
    )  # First one with --with-reference
    if not can_build:
        print(
            f"Commit {head} cannot be built using Ciel: the minimum version of open_pdks buildable with Ciel is 1.0.381."
        )
        exit(-1)

    gf180mcu_sources_ok = is_ancestor("c1e2118846fd216b2c065a216950e75d2d67ccb8")
    if not gf180mcu_sources_ok:
        print(
            "Fixing gf180mcu Makefile.in provenance…",
        )
        open_pdks_fix_makefile_provenance(
            os.path.join(at_path, "gf180mcu", "Makefile.in")
        )

    download_script_ok = is_ancestor(
        "ebffedd16788db327af050ac01c3fb1558ebffd1"
    )  # download script fix
    if not download_script_ok:
        print("Replacing download.sh…")
        session = GitHubSession()
        r = session.get(
            "https://raw.githubusercontent.com/RTimothyEdwards/open_pdks/ebffedd16788db327af050ac01c3fb1558ebffd1/scripts/download.sh"
        )
        with open(os.path.join(at_path, "scripts", "download.sh"), "wb") as f:
            f.write(r.content)

    sky130_sources_ok = is_ancestor("274040274a7dfb5fd2c69e0e9c643f80507df3fe")
    if not sky130_sources_ok:
        print(
            "Fixing sky130 Makefile.in provenance…",
        )
        open_pdks_fix_makefile_provenance(
            os.path.join(at_path, "sky130", "Makefile.in")
        )

    gnu_sed_used = is_ancestor("636a08dc4a137a40050d086ac00b63d2be323520")
    if gnu_sed_used:
        print("Patching GNU sed-only syntax in sky130 Makefile…")
        open_pdks_patch_gnu_sed(os.path.join(at_path, "sky130", "Makefile.in"))

# Copyright 2025 The American University in Cairo
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
import sys
import json
import shutil

import httpx
import click
from rich.console import Console

from .__version__ import __version__
from .common import (
    Version,
    get_ciel_home,
)
from .click_common import (
    opt_pdk_root,
    arg_version,
)
from .manage import (
    print_installed_list,
    print_remote_list,
    enable,
    fetch,
    optimize,
)
from .build import (
    build_cmd,
    push_cmd,
)
from .github import opt_github_token
from .source import opt_data_source
from .families import Family


@click.command("output")
@opt_pdk_root
def output_cmd(pdk_root, pdk_family):
    """Outputs the currently enabled PDK version.

    If not outputting to a tty, the output is either the version string
    unembellished, or, if no current version is enabled, an empty output with an
    exit code of 1.
    """

    version = Version.get_current(pdk_root, pdk_family)
    if sys.stdout.isatty():
        if version is None:
            print(
                f"No version of the PDK {pdk_family} is currently enabled at {pdk_root}."
            )
            print("Invoke ciel --help for assistance installing and enabling versions.")
            exit(1)
        else:
            print(f"Installed: {pdk_family} v{version.name}")
            print("Invoke ciel --help for assistance installing and enabling versions.")
    else:
        if version is None:
            exit(1)
        else:
            print(version.name, end="")


@click.command("prune")
@opt_pdk_root
@click.option(
    "--yes",
    is_flag=True,
    callback=lambda c, _, v: not v and c.abort(),
    expose_value=False,
    prompt="Are you sure? This will delete all non-enabled versions of the PDK from your computer.",
)
def prune_cmd(pdk_root, pdk_family):
    """Removes all PDKs other than, if it exists, the one currently set as 'enabled' in the PDK root."""

    pdk_versions = Version.get_all_installed(pdk_root, pdk_family)
    for version in pdk_versions:
        if version.is_current(pdk_root):
            continue
        try:
            version.uninstall(pdk_root)
            print(f"Deleted {version}.")
        except Exception as e:
            print(f"Failed to delete {version}: {e}", file=sys.stderr)


@click.command("optimize")
@opt_pdk_root
@arg_version
def optimize_cmd(pdk_root, pdk_family, version):
    """
    [Experimental] This command attempts to save space by converting identical
    files across variants for the specified version to symbolic links.

    This will save space for some items such as GDS and LIB files, but may have
    some side effects with your own tools. Use at your own discretion.

    Requires a POSIX or POSIX-compatible operating system.
    """

    recovered = optimize(pdk_root, Version(version, pdk_family))

    console = Console()
    console.print(f"[bold]{recovered / (1 << 20):.2f}[/bold] MiB recovered.")


@click.command("optimize-all")
@opt_pdk_root
def optimize_all_cmd(pdk_root, pdk_family):
    """
    [Experimental] This command attempts to save space by converting identical
    files across variants for all versions of a specific PDK family to symbolic
    links.

    This will save space for some items such as GDS and LIB files, but may have
    some side effects with your own tools. Use at your own discretion.

    Requires a POSIX or POSIX-compatible operating system.
    """

    recovered = 0
    for version in Version.get_all_installed(pdk_root, pdk_family):
        recovered += optimize(pdk_root, version)

    console = Console()
    console.print(f"[bold]{recovered / (1 << 20):.2f}[/bold] MiB recovered.")


@click.command("rm")
@opt_pdk_root
@click.option(
    "--yes",
    is_flag=True,
    callback=lambda c, _, v: not v and c.abort(),
    expose_value=False,
    prompt="Are you sure? This will delete this version of the PDK from your computer.",
)
@arg_version
def rm_cmd(pdk_root, pdk_family, version):
    """Removes the PDK version specified."""

    version_object = Version(version, pdk_family)
    try:
        version_object.uninstall(pdk_root)
        print(f"Deleted {version}.")
    except Exception as e:
        print(f"Failed to delete: {e}", file=sys.stderr)
        exit(1)


@click.command("ls")
@opt_data_source
@opt_github_token
@opt_pdk_root
def list_cmd(data_source, pdk_root, pdk_family):
    """Lists PDK versions that are locally installed. JSON if not outputting to a tty."""

    pdk_versions = Version.get_all_installed(pdk_root, pdk_family)

    if sys.stdout.isatty():
        console = Console()
        print_installed_list(
            pdk_root,
            pdk_family,
            data_source=data_source,
            console=console,
            installed_list=pdk_versions,
        )
    else:
        print(json.dumps([version.name for version in pdk_versions]), end="")


@click.command("ls-remote")
@opt_github_token
@opt_data_source
@opt_pdk_root
def list_remote_cmd(data_source, pdk_root, pdk_family):
    """Lists PDK versions that are remotely available. JSON if not outputting to a tty."""

    try:
        pdk_versions = data_source.get_available_versions(pdk_family)

        if sys.stdout.isatty():
            console = Console()
            print_remote_list(pdk_root, pdk_family, console, pdk_versions)
        else:
            for version in pdk_versions:
                print(version.name)
    except ValueError as e:
        if sys.stdout.isatty():
            console = Console()
            console.print(f"[red]{e}")
        else:
            print(f"{e}", file=sys.stderr)
        sys.exit(-1)
    except httpx.HTTPStatusError as e:
        if sys.stdout.isatty():
            console = Console()
            console.print(f"[red]Encountered an error when polling version list: {e}")
        else:
            print(f"Failed to get version list: {e}", file=sys.stderr)
        sys.exit(-1)
    except httpx.NetworkError as e:
        if sys.stdout.isatty():
            console = Console()
            console.print(
                "[red]You don't appear to be connected to the Internet. ls-remote cannot be used."
            )
        else:
            print(f"Failed to connect to remote server: {e}", file=sys.stderr)
        sys.exit(-1)


@click.command("path")
@opt_pdk_root
@arg_version
def path_cmd(pdk_root, pdk_family, version):
    """
    Prints the path of the ciel PDK root.

    If a version is provided over the commandline, it prints the path to this
    version instead.
    """
    if version is not None:
        version = Version(version, pdk_family)
        print(version.get_dir(pdk_root), end="")
    else:
        print(get_ciel_home(pdk_root))


@click.command("enable")
@opt_data_source
@opt_github_token
@opt_pdk_root
@click.option(
    "-l",
    "--include-libraries",
    multiple=True,
    default=None,
    help="Libraries to include. You can use  l multiple times to include multiple libraries. Pass 'all' to include all of them. A default of 'None' uses a default set for the particular PDK.",
)
@arg_version
def enable_cmd(
    data_source,
    pdk_root,
    pdk_family,
    version,
    include_libraries,
):
    """
    Activates a given installed PDK version.
    """

    if include_libraries == ():
        include_libraries = None

    console = Console()

    try:
        enable(
            pdk_root,
            pdk_family,
            version,
            include_libraries=include_libraries,
            output=console,
            data_source=data_source,
        )
    except Exception as e:
        console.print(f"[red]{e}")
        exit(-1)


@click.command("fetch")
@opt_data_source
@opt_github_token
@opt_pdk_root
@click.option(
    "-l",
    "--include-libraries",
    multiple=True,
    default=None,
    help="Libraries to include. You can use -l multiple times to include multiple libraries. Pass 'all' to include all of them. A default of 'None' uses a default set for the particular PDK.",
)
@arg_version
def fetch_cmd(
    data_source,
    pdk_root,
    pdk_family,
    version,
    include_libraries,
):
    """
    Fetches a PDK to Ciel's store without setting it as the "enabled" version
    in ``PDK_ROOT``.
    """

    if include_libraries == ():
        include_libraries = None

    console = Console()

    try:
        version = fetch(
            data_source=data_source,
            pdk_root=pdk_root,
            pdk=pdk_family,
            version=version,
            include_libraries=include_libraries,
            output=console,
        )
        print(version.get_dir(pdk_root), end="")

    except Exception as e:
        console.print(f"[red]{e}")
        exit(-1)


@click.command("ls-pdks")
def list_pdks_cmd():
    """Lists PDK families and variants. JSON if not outputting to a tty"""
    result = {}
    if sys.stdout.isatty():
        console = Console()
        for family in Family.by_name.values():
            console.print(f"[bold]{family.name}")
            for variant in family.variants:
                console.print(
                    f"- {variant}{' (default)' * (variant == family.default_variant)}"
                )
    else:
        for family in Family.by_name.values():
            result[family.name] = family.variants
        print(json.dumps(result), end="")


@click.group(
    context_settings={
        "max_content_width": max(shutil.get_terminal_size().columns, 80),
    }
)
@click.version_option(
    __version__,
    message="""Ciel v%(version)s ©2022-2025 Efabless Corporation and Contributors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this program except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.""",
)
def cli():
    pass


cli.add_command(output_cmd)
cli.add_command(optimize_cmd)
cli.add_command(optimize_all_cmd)
cli.add_command(prune_cmd)
cli.add_command(rm_cmd)
cli.add_command(build_cmd)
cli.add_command(push_cmd)
cli.add_command(path_cmd)
cli.add_command(list_cmd)
cli.add_command(list_remote_cmd)
cli.add_command(enable_cmd)
cli.add_command(fetch_cmd)
cli.add_command(list_pdks_cmd)

try:
    import ssl  # noqa: F401
except ModuleNotFoundError as e:
    print(
        f"Your version of Python 3 was not built with a required module: '{e.name}'",
        file=sys.stderr,
    )
    print(
        "Please install Python 3 with all (optional) dependencies using your operating system's package manager.",
        file=sys.stderr,
    )
    print("This is a fatal error. Ciel will now quit.", file=sys.stderr)
    exit(-1)


if __name__ == "__main__":
    cli()

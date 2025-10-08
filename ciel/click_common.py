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
from functools import partial
from typing import Callable, Optional

import click

from .common import (
    CIEL_RESOLVED_HOME,
    resolve_pdk_family,
    resolve_version,
)
from .families import Family

opt = partial(click.option, show_default=True)


class VersionArgument(click.Argument):
    def make_metavar(self, ctx: Optional[click.Context] = None):
        return "<VERSION>"

    def set_tool_metadata_file_path(
        self,
        ctx: click.Context,
        param: click.Parameter,
        value: Optional[str],
    ):
        self.tool_metadata_file_path = value

    def process_value(self, ctx, value):
        try:
            # handle sentinels in click ≥ 8.3.0
            if hasattr(value, "name") and value.name == "UNSET":
                value = None
            tool_metadata_file_path = None
            if "tool_metadata_file_path" in ctx.params:
                tool_metadata_file_path = ctx.params["tool_metadata_file_path"]
                del ctx.params["tool_metadata_file_path"]
            resolved = resolve_version(value, tool_metadata_file_path)
        except FileNotFoundError:
            resolved = None
        return super().process_value(ctx, resolved)


def arg_version(f):
    version_param = VersionArgument(["version"], required=True)
    f = click.option(
        "-f",
        "--metadata-file",
        "tool_metadata_file_path",
        default=None,
        expose_value=False,
        callback=version_param.set_tool_metadata_file_path,
        help="Explicitly define a tool metadata file instead of searching for a metadata file",
    )(f)
    f.__click_params__.append(version_param)
    return f


class PDKOption(click.Option):
    def get_usage_pieces(self, ctx):
        return [f"<--pdk-family {'|'.join(Family.by_name)}>"]

    def process_value(self, ctx: click.Context, value):
        value = self.type_cast_value(ctx, value)

        if self.required and self.value_is_missing(value):
            raise click.MissingParameter(
                message=f"A PDK family or variant must be specified. The following families are supported: {', '.join(Family.by_name)}",
                ctx=ctx,
                param=self,
            )

        if self.callback is not None:
            value = self.callback(ctx, self, value)

        try:
            resolved = resolve_pdk_family(value)
        except ValueError as e:
            raise click.BadParameter(str(e), ctx=ctx, param=self)

        return resolved


def opt_pdk_root(function: Callable):
    function = opt(
        "--pdk-family",
        "--pdk",
        cls=PDKOption,
        required=True,
        envvar=["PDK_FAMILY", "PDK"],
        help="A valid PDK family or variant (the latter of which is resolved to a family). If the environment PDK_FAMILY or PDK are set, they are used as secondary sources for this value.",
    )(function)
    function = opt(
        "--pdk-root",
        required=False,
        default=CIEL_RESOLVED_HOME,
        help="Path to the PDK root",
    )(function)
    return function


def opt_build(function: Callable):
    function = opt(
        "-l",
        "--include-libraries",
        multiple=True,
        default=None,
        help="Libraries to include. You can use -l multiple times to include multiple libraries. Pass 'all' to include all of them. A default of 'None' uses a default set for the particular PDK.",
    )(function)
    function = opt(
        "-j",
        "--jobs",
        default=1,
        help="Specifies the number of commands to run simultaneously.",
    )(function)
    function = opt(
        "--sram/--no-sram",
        default=True,
        hidden=True,
        expose_value=False,
    )(function)
    function = opt(
        "--clear-build-artifacts/--keep-build-artifacts",
        default=False,
        help="Whether or not to remove the build artifacts. Keeping the build artifacts is useful when testing.",
    )(function)
    function = opt(
        "-r",
        "--use-repo-at",
        default=None,
        multiple=True,
        hidden=True,
        type=str,
        help="Use this repository instead of cloning and checking out, in the format repo_name=/path/to/repo. You can pass it multiple times to replace multiple repos. This feature is intended for ciel and PDK developers.",
    )(function)
    return function


def opt_push(function: Callable):
    function = opt(
        "-o",
        "--owner",
        default="fossi-foundation",
        help="Artifact Upload Repository Owner",
    )(function)
    function = opt(
        "-r",
        "--repository",
        default="ciel-releases",
        help="Artifact Upload Repository",
    )(function)
    function = opt(
        "--pre/--prod", default=False, help="Push as pre-release or production"
    )(function)
    function = opt(
        "-L",
        "--push-library",
        "push_libraries",
        multiple=True,
        default=None,
        help="Push only libraries in this list. You can use -L multiple times to include multiple libraries. Pass 'None' to push all libraries built.",
    )(function)
    return function

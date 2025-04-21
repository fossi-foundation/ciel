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
)
from .families import Family

opt = partial(click.option, show_default=True)


def pdk_cb(
    ctx: click.Context,
    param: click.Parameter,
    value: Optional[str],
):
    try:
        resolved = resolve_pdk_family(value)
    except ValueError as e:
        raise click.BadParameter(str(e), ctx, param)
    if resolved is None:
        raise click.BadParameter(
            f"A PDK family or variant must be specified. The following families are supported: {', '.join(Family.by_name)}"
        )


def opt_pdk_root(function: Callable):
    function = opt(
        "--pdk-family",
        "--pdk",
        required=False,  # Requirement handled by callback
        callback=pdk_cb,
        help="A valid PDK family or variant (the latter of which is resolved to a family).",
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
    function = opt("-o", "--owner", default="efabless", help="Repository Owner")(
        function
    )
    function = opt("-r", "--repository", default="volare", help="Repository")(function)
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

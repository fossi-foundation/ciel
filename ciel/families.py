# Copyright 2026 Ciel Contributors
#
# Adapted from Volare
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
import fnmatch
from dataclasses import dataclass
from typing import Iterable, List, Dict, Optional, Set, ClassVar

from .github import RepoInfo, opdks_repo, ihp_repo


@dataclass
class Family(object):
    by_name: ClassVar[Dict[str, "Family"]] = {}
    by_variant: ClassVar[Dict[str, "Family"]] = {}

    name: str
    variants: List[str]
    all_libraries: List[str]
    repo: RepoInfo
    # lol no implicitly unwrapped optionals
    default_variant: str = None  # type: ignore
    default_includes: Dict[str, List[str]] = None  # type: ignore

    def __post_init__(self):
        if self.default_variant is None:
            self.default_variant = self.variants[0]
        if self.default_includes is None:
            self.default_includes = {"*": self.all_libraries.copy()}

        Family.by_name[self.name] = self
        for variant in self.variants:
            Family.by_variant[variant] = self

    def resolve_libraries(
        self,
        input: Optional[Iterable[str]],
        variant: str,
    ) -> Set[str]:
        if input is None:
            input = ("default",)
        final_set: Set[str] = set()
        for element in input:
            if element.lower() == "all":
                final_set = set(self.all_libraries)
                return final_set
            elif element.lower() == "default":
                for pattern, includes in self.default_includes.items():
                    if fnmatch.fnmatch(variant, pattern):
                        final_set = final_set.union(includes)
            elif element in self.all_libraries:
                final_set.add(element)
            else:
                raise ValueError(f"Unknown library {element} for PDK {self.name}")
        return final_set


Family(
    name="sky130",
    variants=["sky130A", "sky130B"],
    default_variant="sky130A",
    all_libraries=[
        "sky130_fd_io",
        "sky130_fd_pr",
        "sky130_ml_xx_hd",
        "sky130_fd_sc_hd",
        "sky130_fd_sc_hdll",
        "sky130_fd_sc_lp",
        "sky130_fd_sc_hvl",
        "sky130_fd_sc_ls",
        "sky130_fd_sc_ms",
        "sky130_fd_sc_hs",
        "sky130_sram_macros",
        "sky130_fd_pr_reram",
    ],
    default_includes={
        "*": [
            "sky130_fd_io",
            "sky130_fd_pr",
            "sky130_fd_sc_hd",
            "sky130_fd_sc_hvl",
            "sky130_ml_xx_hd",
            "sky130_sram_macros",
        ],
        "sky130B": ["sky130_fd_pr_reram"],
    },
    repo=opdks_repo,
)

Family(
    name="gf180mcu",
    variants=["gf180mcuA", "gf180mcuB", "gf180mcuC", "gf180mcuD"],
    default_variant="gf180mcuD",
    all_libraries=[
        "gf180mcu_fd_io",
        "gf180mcu_fd_pr",
        "gf180mcu_fd_sc_mcu7t5v0",
        "gf180mcu_fd_sc_mcu9t5v0",
        "gf180mcu_fd_ip_sram",
        "gf180mcu_osu_sc_gp12t3v3",
        "gf180mcu_osu_sc_gp9t3v3",
        "gf180mcu_as_sc_mcu7t3v3",
        "gf180mcu_re_efuse",
        "gf180mcu_ocd_io",
        "gf180mcu_ocd_ip_sram",
        "gf180mcu_ocd_alpha_small",
        "gf180mcu_ocd_alpha_large",
        "gf180mcu_ocd_alpha_misc",
    ],
    default_includes={
        "*": [
            "gf180mcu_fd_io",
            "gf180mcu_fd_pr",
            "gf180mcu_fd_sc_mcu7t5v0",
            "gf180mcu_fd_sc_mcu9t5v0",
            "gf180mcu_fd_ip_sram",
        ]
    },
    repo=opdks_repo,
)

Family(
    name="ihp-sg13",
    variants=["ihp-sg13g2"],
    all_libraries=[
        "sg13g2_io",
        "sg13g2_pr",
        "sg13g2_sram",
        "sg13g2_stdcell",
    ],
    default_includes={
        "ihp-sg13g2": [
            "sg13g2_io",
            "sg13g2_pr",
            "sg13g2_sram",
            "sg13g2_stdcell",
        ],
    },
    repo=ihp_repo,
)


def resolve_pdk_family(selector: str):
    """
    :returns:
        If selector is a valid PDK family, the same string.

        If selector is a valid PDK variant, the family the variant belongs to.

        If the selector is invalid, a ValueError will be raised. "ihp_sg13g2"
        will resolve to "ihp-sg13g2" however for some semblance of backwards
        compatibility with previous versions of Ciel/Volare.
    """
    if selector == "ihp_sg13g2":
        selector = "ihp-sg13"

    if selector in Family.by_name:
        return selector

    for pdk_family in Family.by_name.values():
        if selector in pdk_family.variants:
            return pdk_family.name

    raise ValueError(f"'{selector}' is not a valid PDK family or variant.")


def resolve_pdk_variant(selector: Optional[str]):
    """
    :returns:
        If selector is a valid PDK variant, the same string.

        If selector is a valid PDK family, the default variant of said PDK.

        If selector is None, the function will simply return None.

        If the selector is invalid, a ValueError will be raised.
    """
    if selector is None:
        return None

    if selector in Family.by_variant:
        return str(selector)

    if family := Family.by_name.get(selector):
        return family.default_variant

    raise ValueError(f"'{selector}' is not a valid PDK family or variant.")

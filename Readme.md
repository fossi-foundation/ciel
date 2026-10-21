<h1 align="center">🌌 Ciel</h1>
<p align="center">
    <a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License: Apache 2.0"/></a>
    <a href="https://www.python.org"><img src="https://img.shields.io/badge/Python-3.8-3776AB.svg?style=flat&logo=python&logoColor=white" alt="Python ≥3.8" /></a>
    <img src="https://github.com/fossi-foundation/ciel/actions/workflows/ci.yml/badge.svg?branch=main" alt="CI Status" />
    <a href="https://fossi-chat.org"><img src="https://img.shields.io/badge/Community-FOSSi%20Chat-1bb378?logo=element" alt="Invite to FOSSi Chat"/></a>
</p>

<p align="center">Ciel is a version manager (and builder) for builds of open-source process design kits (PDKs).</p>

# Requirements

## macOS
Get [Homebrew](https://brew.sh) then:

```sh
brew install python3
```

## Debian and Ubuntu
Debian 11+ or Ubuntu 20.04+ is required.

```sh
sudo apt-get update
sudo apt-get install python3 python3-pip
```

## RHEL and Derivatives
RHEL 8+ or compatible operating system required.
```sh
sudo yum install -y python3 python3-pip
```


# Installation and Upgrades
```sh
# To install (or upgrade)
python3 -m pip install --user --upgrade --no-cache-dir ciel

# To verify it works
ciel --version
```

# About the builds

Ciel aims to support all kinds of open-source process design kits, so long
as they are laid out in the
[Open PDKs](https://github.com/fossi-foundation/open_pdks) format. Some PDKs
do not come in this format by default, so build scripts are added to `open_pdks`
to bring them into conformity, in which case open_pdks is transitively
responsible for their provenance (i.e. the versions of the PDK are identified
by the Open PDKs hash.)

This section lists supported PDKs and their identifiers: (You can list
supported standard cell libraries by using `ciel ls-libs --pdk <identifier>`)

* Manufacturable (AMS)
    * [Google/SkyWater (130nm) Open Source PDK](https://github.com/fossi-foundation/skywater-pdk) — `sky130`
        * Identified by [Open PDKs](https://github.com/fossi-foundation/open_pdks) hash.
    * [Google/GlobalFoundries GF180MCU Open Source PDK](https://github.com/fossi-foundation/gf180mcu-pdk) - `gf180mcu`
        * Identified by [Open PDKs](https://github.com/fossi-foundation/open_pdks) hash.
    * [IHP (130nm) Open Source PDK](https://github.com/IHP-GmbH/IHP-Open-PDK) - `ihp-sg13`
        * Identified by upstream repo hash, which is already in the Open PDKs
          format.
* Predictive/Academic
    * [FreePDK45](https://github.com/rjordans/freepdk45-open-pdks) - `freepdk45`
        * Identified by hash in [Roel Jordans](https://github.com/rjordans)'
          repo which lays it out in the Open PDKs format and adds LibreLane
          support.
        * Originally developed by NCSU - ([src](https://eda.ncsu.edu/freepdk/freepdk45/))

## Included libraries

<!-- Regenerate library list using `python3 -m ciel _update_readme_lib_table Readme.md` -->

<!-- START LIBRARIES -->
<table>
<tr>
<th>sky130</th>
<th>gf180mcu</th>
<th>ihp-sg13</th>
<th>freepdk45</th>
</tr>
<tr>
<td>sky130_fd_io</td>
<td>gf180mcu_as_sc_mcu7t3v3</td>
<td>sg13cmos5l_io</td>
<td>fakeram45</td>
</tr>
<tr>
<td>sky130_fd_pr</td>
<td>gf180mcu_fd_io</td>
<td>sg13cmos5l_sram</td>
<td>nangate45</td>
</tr>
<tr>
<td>sky130_fd_pr_reram</td>
<td>gf180mcu_fd_ip_sram</td>
<td>sg13cmos5l_stdcell</td>
<td>-</td>
</tr>
<tr>
<td>sky130_fd_sc_hd</td>
<td>gf180mcu_fd_pr</td>
<td>sg13g2_io</td>
<td>-</td>
</tr>
<tr>
<td>sky130_fd_sc_hdll</td>
<td>gf180mcu_fd_sc_mcu7t5v0</td>
<td>sg13g2_pr</td>
<td>-</td>
</tr>
<tr>
<td>sky130_fd_sc_hs</td>
<td>gf180mcu_fd_sc_mcu9t5v0</td>
<td>sg13g2_sram</td>
<td>-</td>
</tr>
<tr>
<td>sky130_fd_sc_hvl</td>
<td>gf180mcu_ocd_alpha_large</td>
<td>sg13g2_stdcell</td>
<td>-</td>
</tr>
<tr>
<td>sky130_fd_sc_lp</td>
<td>gf180mcu_ocd_alpha_misc</td>
<td>-</td>
<td>-</td>
</tr>
<tr>
<td>sky130_fd_sc_ls</td>
<td>gf180mcu_ocd_alpha_small</td>
<td>-</td>
<td>-</td>
</tr>
<tr>
<td>sky130_fd_sc_ms</td>
<td>gf180mcu_ocd_io</td>
<td>-</td>
<td>-</td>
</tr>
<tr>
<td>sky130_ml_xx_hd</td>
<td>gf180mcu_ocd_ip_sram</td>
<td>-</td>
<td>-</td>
</tr>
<tr>
<td>sky130_sram_macros</td>
<td>gf180mcu_ocd_sc_rt12t3v3</td>
<td>-</td>
<td>-</td>
</tr>
<tr>
<td>-</td>
<td>gf180mcu_osu_sc_gp12t3v3</td>
<td>-</td>
<td>-</td>
</tr>
<tr>
<td>-</td>
<td>gf180mcu_osu_sc_gp9t3v3</td>
<td>-</td>
<td>-</td>
</tr>
<tr>
<td>-</td>
<td>gf180mcu_re_efuse</td>
<td>-</td>
<td>-</td>
</tr>
</tr>
</table>
<!-- END LIBRARIES -->

# Usage
Ciel requires a so-called **PDK Root**. This PDK root can be anywhere on your computer, but by default it's the folder `~/.ciel` in your home directory. If you have the variable `PDK_ROOT` set, ciel will use that instead. You can also manually override both values by supplying the `--pdk-root` commandline argument.

## Listing All Available PDKs
To list all available pre-built PDK families hosted in this repository, you can just invoke `ciel ls-remote --pdk-family <pdk-family>`.

```sh
$ ciel ls-remote --pdk-family sky130
Pre-built sky130 PDK versions
├── 44a43c23c81b45b8e774ae7a84899a5a778b6b0b (2022.08.16) (enabled)
├── e8294524e5f67c533c5d0c3afa0bcc5b2a5fa066 (2022.07.29) (installed)
├── 41c0908b47130d5675ff8484255b43f66463a7d6 (2022.04.14) (installed)
├── 660c6bdc8715dc7b3db95a1ce85392bbf2a2b195 (2022.04.08)
├── 5890e791e37699239abedfd2a67e55162e25cd94 (2022.04.06)
├── 8fe7f760ece2bb49b1c310e60243f0558977dae5 (2022.04.06)
└── 7519dfb04400f224f140749cda44ee7de6f5e095 (2022.02.10)

$ ciel ls-remote --pdk-family gf180mcu
Pre-built gf180mcu PDK versions
└── 120b0bd69c745825a0b8b76f364043a1cd08bb6a (2022.09.22)
```

It includes a hash of the commit of the relevant repo used for that particular build, the date that this commit was created, and whether you already installed this PDK and/or if it is the currently enabled PDK.

## Listing Installed PDKs
Typing `ciel ls --pdk-family <pdk-family>` in the terminal shows you your PDK Root and the PDKs you currently have installed.

```sh
$ ciel ls --pdk-family sky130
/home/test/ciel/sky130/versions
├── 44a43c23c81b45b8e774ae7a84899a5a778b6b0b (2022.08.16) (enabled)
├── e8294524e5f67c533c5d0c3afa0bcc5b2a5fa066 (2022.07.29)
└── 41c0908b47130d5675ff8484255b43f66463a7d6 (2022.04.14)
```

(If you're not connected to the Internet, the release date of the commit will not be included.)


## Downloading and Enabling PDKs
You can enable a particular sky130 PDK by invoking `ciel enable --pdk-family <pdk-family> <open_pdks commit hash>`. This will automatically download that particular version of the PDK, if found, and set it as your currently used PDK.

For example, to activate a build of sky130 using open_pdks `7519dfb04400f224f140749cda44ee7de6f5e095`, you invoke `ciel enable --pdk-family sky130 7519dfb04400f224f140749cda44ee7de6f5e095`, as shown below:

```sh
$ ciel enable --pdk-family sky130 7519dfb04400f224f140749cda44ee7de6f5e095
Downloading pre-built tarball for 7519dfb04400f224f140749cda44ee7de6f5e095… ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
Unpacking…                                                                  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
PDK version 7519dfb04400f224f140749cda44ee7de6f5e095 enabled.
```

## Building PDKs
For special cases, you may have to build the PDK yourself, which Ciel does support.

You'll need Magic installed and in PATH. You can either do that manually or, if you have [Nix](https://nixos.org), invoke `nix shell github:fossi-foundation/nix-eda#magic` before building.

You can invoke `ciel build --help` for more options. Be aware, the built PDK won't automatically be enabled and you'll have to `ciel enable` the appropriate version.

# License
The Apache License, version 2.0. See 'License'.


Ciel is based on [Volare](https://github.com/efabless/volare) by Efabless
Corporation:

```
Copyright 2022-2025 Efabless Corporation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

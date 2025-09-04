<h1 align="center">🌌 Ciel</h1>
<p align="center">
    <a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License: Apache 2.0"/></a>
    <img src="https://github.com/fossi-foundation/ciel/actions/workflows/ci.yml/badge.svg?branch=main" alt="CI Status" />
    <a href="https://fossi-chat.org"><img src="https://img.shields.io/badge/Community-FOSSi%20Chat-1bb378?logo=element" alt="Invite to FOSSi Chat"/></a>
    <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code Style: Black"/></a>
</p>

<p align="center">Ciel is a version manager (and builder) for builds of open-source process design kits (PDKs).</p>

# Requirements
* Python 3.8+ with PIP
* macOS or GNU/Linux

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
In its current inception, ciel supports builds of **sky130** and **gf180mcu** PDKs using [Open_PDKs](https://github.com/efabless/open_pdks), including the following libraries:

|sky130|gf180mcu|ihp-sg13g2|
|-|-|-|
|sky130_fd_io|gf180mcu_fd_io|sg13g2_io|
|sky130_fd_pr|gf180mcu_fd_pr|sg13g2_pr|
|sky130_fd_pr_reram|gf180mcu_fd_pr|sg13g2_pr|
|sky130_fd_sc_hd|gf180mcu_fd_sc_mcu7t5v0|sg13g2_stdcell|
|sky130_ml_xx_hd|gf180mcu_fd_sc_mcu9t5v0|-|
|sky130_fd_sc_hvl|gf180mcu_osu_sc_gp9t3v3|-|
|sky130_fd_sc_lp|gf180mcu_osu_sc_gp12t3v3|-|
|sky130_fd_sc_ls|-|-|
|sky130_fd_sc_ms|-|-|
|sky130_fd_sc_hs|-|-|
|sky130_sram_macros|gf180mcu_fd_ip_sram|sg13g2_sram|

Builds for sky130 and gf180mcu are identified by their [**open_pdks**](https://github.com/rtimothyedwards/open_pdks) commit hashes. Builds for ihp-sg13g2 are identified by their [**IHP-Open-PDK**](https://github.com/ihp-gmbh/ihp-open-pdk) commit hashes.

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

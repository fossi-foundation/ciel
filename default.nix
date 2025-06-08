# Copyright 2024 Efabless Corporation
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
{
  flake ? null,
  lib,
  buildPythonPackage,
  click,
  pyyaml,
  rich,
  httpx,
  pcpp,
  zstandard,
  truststore,
  poetry-core,
}:
buildPythonPackage {
  pname = "ciel";
  version = (builtins.fromTOML (builtins.readFile ./pyproject.toml)).tool.poetry.version;
  format = "pyproject";

  src = if (flake != null) then flake else ./.;
  doCheck = false;

  nativeBuildInputs = [
    poetry-core
  ];


  dependencies =
    [
      click
      pyyaml
      rich
      httpx
      pcpp
      zstandard
      truststore
    ]
    ++ httpx.optional-dependencies.socks;

  meta = {
    mainProgram = "ciel";
    description = "Version manager and builder for open-source PDKs";
    homepage = "https://github.com/donn/ciel";
    license = lib.licenses.asl20;
    platforms = lib.platforms.darwin ++ lib.platforms.linux;
  };
}

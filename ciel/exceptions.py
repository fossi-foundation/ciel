# Copyright 2026 The American University in Cairo
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
"""
Ciel-specific exception classes.

All exceptions inherit from their appropriate standard-library base class so
that existing code that catches ``ValueError``, ``RuntimeError``, etc. continues
to work without modification.  New callers can catch the ciel-specific
sub-classes for finer-grained error handling.
"""


class InvalidPDKError(ValueError):
    """Raised when a PDK family name or variant selector is not recognised."""


class UnknownLibraryError(ValueError):
    """Raised when a library name is not part of a PDK family."""


class VersionNotFoundError(RuntimeError):
    """Raised when a requested PDK version cannot be located (locally or remotely)."""


class VersionNotInstalledError(ValueError):
    """Raised when an operation requires a version to be installed but it is not."""


class DownloadError(RuntimeError):
    """Raised when a remote download fails with an unexpected HTTP error."""


class UnpackError(IOError):
    """Raised when extracting a downloaded tarball fails."""


class NoVersionsFoundError(ValueError):
    """Raised when a data source returns no versions for the requested PDK."""


class InvalidResponseError(ValueError):
    """Raised when a remote server returns an unexpected or malformed response."""


class ToolMetadataError(ValueError):
    """Raised when ``tool_metadata.yml`` is missing a required entry."""


class MissingCredentialsError(TypeError):
    """Raised when a required credential (e.g. a GitHub token) was not supplied."""


# Backward-compatible alias – previously defined in manage.py and exported
# from the top-level package.  New code should use VersionNotFoundError.
VersionNotFound = VersionNotFoundError

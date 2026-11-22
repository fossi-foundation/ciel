import io
import os
import tarfile
import tempfile
import unittest
from typing import Any, List, Tuple
from unittest import mock

import httpx
import zstandard as zstd
from rich.console import Console

from ciel import manage
from ciel.common import Version
from ciel.manage import fetch
from ciel.source import Asset, DataSource

VERSION = "0123456789abcdef0123456789abcdef01234567"
TECH_README = "sky130A/libs.tech/README"


def make_common_tarball() -> bytes:
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w") as tf:
        payload = b"technology files\n"
        info = tarfile.TarInfo(TECH_README)
        info.size = len(payload)
        tf.addfile(info, io.BytesIO(payload))
    return zstd.ZstdCompressor().compress(raw.getvalue())


class StubDataSource(DataSource):
    def __init__(self, tarball: bytes):
        self.tarball = tarball

    def get_downloads_for_version(
        self, version: Version
    ) -> Tuple[httpx.Client, List[Asset]]:
        client = httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, content=self.tarball)
            )
        )
        asset = Asset(
            "common", "common.tar.zst", "https://example.invalid/common.tar.zst"
        )
        return client, [asset]


class FetchTarballHandleTest(unittest.TestCase):
    def test_tarball_is_closed_before_it_is_deleted(self) -> None:
        # Windows refuses to delete a file that still has an open handle
        # ([WinError 32]), so fetch() must close the downloaded tarball
        # before its cleanup unlinks it.
        opened: List[Any] = []
        real_open = zstd.open

        def spy_open(*args: Any, **kwargs: Any) -> Any:
            stream = real_open(*args, **kwargs)
            opened.append(stream)
            return stream

        with tempfile.TemporaryDirectory() as pdk_root:
            with mock.patch.object(manage.zstd, "open", spy_open):
                fetch(
                    pdk_root,
                    "sky130",
                    VERSION,
                    data_source=StubDataSource(make_common_tarball()),
                    include_libraries=[],
                    output=Console(file=io.StringIO()),
                )

            self.assertEqual(len(opened), 1)
            self.assertTrue(opened[0].closed)

            unpacked = os.path.join(
                Version(VERSION, "sky130").get_dir(pdk_root), TECH_README
            )
            self.assertTrue(os.path.isfile(unpacked))


if __name__ == "__main__":
    unittest.main()

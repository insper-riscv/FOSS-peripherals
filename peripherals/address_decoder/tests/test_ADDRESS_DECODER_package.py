import pytest

import lib
from test_GENERICS_package import GENERICS


class ADDR_DECODER(lib.Package):
    children = [
        GENERICS
    ]


@pytest.mark.synthesis
def test_ADDR_DECODER_package_synthesis():
    ADDR_DECODER.build_vhd()


if __name__ == "__main__":
    lib.run_test(__file__)
import pytest

import lib


class GENERIC_OP_DECODER(lib.Package):
    pass


@pytest.mark.synthesis
def test_GENERIC_OP_DECODER_package_synthesis():
    GENERIC_OP_DECODER.build_vhd()


if __name__ == "__main__":
    lib.run_test(__file__)
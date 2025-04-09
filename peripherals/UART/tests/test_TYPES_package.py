import pytest

import lib


class TYPES(lib.Package):
    pass


@pytest.mark.synthesis
def test_TYPES_package_synthesis():
    TYPES.build_vhd()


if __name__ == "__main__":
    lib.run_test(__file__)
import os
import random

import pytest
from cocotb.binary import BinaryValue

import lib
from test_GENERICS_package import GENERICS


class GENERIC_MUX_8X1(lib.Entity):
    _package = GENERICS

    selector = lib.Entity.Input_pin
    source_1 = lib.Entity.Input_pin
    source_2 = lib.Entity.Input_pin
    source_3 = lib.Entity.Input_pin
    source_4 = lib.Entity.Input_pin
    source_5 = lib.Entity.Input_pin
    source_6 = lib.Entity.Input_pin
    source_7 = lib.Entity.Input_pin
    source_8 = lib.Entity.Input_pin
    destination = lib.Entity.Output_pin



@pytest.mark.synthesis
def test_GENERIC_MUX_8X1_synthesis():
    GENERIC_MUX_8X1.build_vhd()
    GENERIC_MUX_8X1.build_netlistsvg()


if __name__ == "__main__":
    lib.run_test(__file__)
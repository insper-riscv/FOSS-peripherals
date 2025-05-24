library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

package types is
  
  type op_cs_pair is record
    op   : std_logic_vector;
    ctrl : std_logic_vector;
  end record;

  type op_cs_map is array (natural range <>) of op_cs_pair;

end package types;

package body types is
end package body types;
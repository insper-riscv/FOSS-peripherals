library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

package types is

  -- Two-dimensional matrix for operation-to-control signal mapping
  type operation_mapping_matrix is array (natural range <>, natural range <>) of std_logic_vector;

  type vector_array is array (natural range <>) of std_logic_vector;

  -- Helper function to convert std_logic_vector to string (for debug)
  function slv_to_string(slv: std_logic_vector) return string;

end package types;

package body types is

  -- Convert std_logic_vector to string
  function slv_to_string(slv: std_logic_vector) return string is
    variable result: string(1 to slv'length);
    variable j: integer := 1;
  begin
    for i in slv'range loop
      case slv(i) is
        when '0' => result(j) := '0';
        when '1' => result(j) := '1';
        when 'U' => result(j) := 'U';
        when 'X' => result(j) := 'X';
        when 'Z' => result(j) := 'Z';
        when '-' => result(j) := '-';
        when others => result(j) := '?';
      end case;
      j := j + 1;
    end loop;
    return result;
  end function;
  
end package body types;
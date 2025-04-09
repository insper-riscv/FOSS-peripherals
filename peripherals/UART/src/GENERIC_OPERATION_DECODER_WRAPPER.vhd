library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;
use work.types.all;
use std.textio.all;

entity generic_operation_decoder_wrapper is
  generic (
    -- Width parameters
    OP_WIDTH             : natural := 7;
    CONTROL_SIGNAL_WIDTH : natural := 3;
    MAPPING_NUM          : natural := 4;
    
    -- Individual operation values (up to 16 mappings supported)
    OP_0                : integer := 0;
    OP_1                : integer := 0;
    OP_2                : integer := 0;
    OP_3                : integer := 0;
    OP_4                : integer := 0;
    OP_5                : integer := 0;
    OP_6                : integer := 0;
    OP_7                : integer := 0;
    OP_8                : integer := 0;
    OP_9                : integer := 0;
    OP_10               : integer := 0;
    OP_11               : integer := 0;
    OP_12               : integer := 0;
    OP_13               : integer := 0;
    OP_14               : integer := 0;
    OP_15               : integer := 0;
    
    -- Individual control signal values (up to 16 mappings supported)
    CTRL_0              : integer := 0;
    CTRL_1              : integer := 0;
    CTRL_2              : integer := 0;
    CTRL_3              : integer := 0;
    CTRL_4              : integer := 0;
    CTRL_5              : integer := 0;
    CTRL_6              : integer := 0;
    CTRL_7              : integer := 0;
    CTRL_8              : integer := 0;
    CTRL_9              : integer := 0;
    CTRL_10             : integer := 0;
    CTRL_11             : integer := 0;
    CTRL_12             : integer := 0;
    CTRL_13             : integer := 0;
    CTRL_14             : integer := 0;
    CTRL_15             : integer := 0;
    
    -- Default control signal as an integer
    DEFAULT_CONTROL      : integer := 0;
    
    -- Debug level (0=none, 1=basic, 2=verbose)
    DEBUG_LEVEL          : natural := 1
  );
  port (
    -- Operation to decode
    operation            : in std_logic_vector(OP_WIDTH downto 0);
    
    -- Control signal output
    control_signal       : out std_logic_vector(CONTROL_SIGNAL_WIDTH downto 0)
  );
end entity generic_operation_decoder_wrapper;

architecture Behavioral of generic_operation_decoder_wrapper is
  -- Convert individual generics to arrays internally
  signal operation_vectors : vector_array(0 to MAPPING_NUM-1)(OP_WIDTH downto 0);
  signal control_vectors   : vector_array(0 to MAPPING_NUM-1)(CONTROL_SIGNAL_WIDTH downto 0);
  
  -- Matrix for the decoder
  signal op_to_control_map : operation_mapping_matrix(0 to MAPPING_NUM-1, 0 to 1);
    
  -- Default control signal as std_logic_vector
  constant default_control_slv : std_logic_vector(CONTROL_SIGNAL_WIDTH downto 0) :=
    std_logic_vector(to_unsigned(DEFAULT_CONTROL, CONTROL_SIGNAL_WIDTH+1));
    
  -- Internal signal for debug reporting
  signal control_signal_internal : std_logic_vector(CONTROL_SIGNAL_WIDTH downto 0);
  
  -- Helper procedure to convert integers to std_logic_vector and assign to signal array
  procedure init_arrays is
  begin
    -- Initialize operation vectors
    operation_vectors(0) <= std_logic_vector(to_unsigned(OP_0, OP_WIDTH+1));
    operation_vectors(1) <= std_logic_vector(to_unsigned(OP_1, OP_WIDTH+1)) when MAPPING_NUM > 1 else (others => '0');
    operation_vectors(2) <= std_logic_vector(to_unsigned(OP_2, OP_WIDTH+1)) when MAPPING_NUM > 2 else (others => '0');
    operation_vectors(3) <= std_logic_vector(to_unsigned(OP_3, OP_WIDTH+1)) when MAPPING_NUM > 3 else (others => '0');
    operation_vectors(4) <= std_logic_vector(to_unsigned(OP_4, OP_WIDTH+1)) when MAPPING_NUM > 4 else (others => '0');
    operation_vectors(5) <= std_logic_vector(to_unsigned(OP_5, OP_WIDTH+1)) when MAPPING_NUM > 5 else (others => '0');
    operation_vectors(6) <= std_logic_vector(to_unsigned(OP_6, OP_WIDTH+1)) when MAPPING_NUM > 6 else (others => '0');
    operation_vectors(7) <= std_logic_vector(to_unsigned(OP_7, OP_WIDTH+1)) when MAPPING_NUM > 7 else (others => '0');
    operation_vectors(8) <= std_logic_vector(to_unsigned(OP_8, OP_WIDTH+1)) when MAPPING_NUM > 8 else (others => '0');
    operation_vectors(9) <= std_logic_vector(to_unsigned(OP_9, OP_WIDTH+1)) when MAPPING_NUM > 9 else (others => '0');
    operation_vectors(10) <= std_logic_vector(to_unsigned(OP_10, OP_WIDTH+1)) when MAPPING_NUM > 10 else (others => '0');
    operation_vectors(11) <= std_logic_vector(to_unsigned(OP_11, OP_WIDTH+1)) when MAPPING_NUM > 11 else (others => '0');
    operation_vectors(12) <= std_logic_vector(to_unsigned(OP_12, OP_WIDTH+1)) when MAPPING_NUM > 12 else (others => '0');
    operation_vectors(13) <= std_logic_vector(to_unsigned(OP_13, OP_WIDTH+1)) when MAPPING_NUM > 13 else (others => '0');
    operation_vectors(14) <= std_logic_vector(to_unsigned(OP_14, OP_WIDTH+1)) when MAPPING_NUM > 14 else (others => '0');
    operation_vectors(15) <= std_logic_vector(to_unsigned(OP_15, OP_WIDTH+1)) when MAPPING_NUM > 15 else (others => '0');
    
    -- Initialize control vectors
    control_vectors(0) <= std_logic_vector(to_unsigned(CTRL_0, CONTROL_SIGNAL_WIDTH+1));
    control_vectors(1) <= std_logic_vector(to_unsigned(CTRL_1, CONTROL_SIGNAL_WIDTH+1)) when MAPPING_NUM > 1 else (others => '0');
    control_vectors(2) <= std_logic_vector(to_unsigned(CTRL_2, CONTROL_SIGNAL_WIDTH+1)) when MAPPING_NUM > 2 else (others => '0');
    control_vectors(3) <= std_logic_vector(to_unsigned(CTRL_3, CONTROL_SIGNAL_WIDTH+1)) when MAPPING_NUM > 3 else (others => '0');
    control_vectors(4) <= std_logic_vector(to_unsigned(CTRL_4, CONTROL_SIGNAL_WIDTH+1)) when MAPPING_NUM > 4 else (others => '0');
    control_vectors(5) <= std_logic_vector(to_unsigned(CTRL_5, CONTROL_SIGNAL_WIDTH+1)) when MAPPING_NUM > 5 else (others => '0');
    control_vectors(6) <= std_logic_vector(to_unsigned(CTRL_6, CONTROL_SIGNAL_WIDTH+1)) when MAPPING_NUM > 6 else (others => '0');
    control_vectors(7) <= std_logic_vector(to_unsigned(CTRL_7, CONTROL_SIGNAL_WIDTH+1)) when MAPPING_NUM > 7 else (others => '0');
    control_vectors(8) <= std_logic_vector(to_unsigned(CTRL_8, CONTROL_SIGNAL_WIDTH+1)) when MAPPING_NUM > 8 else (others => '0');
    control_vectors(9) <= std_logic_vector(to_unsigned(CTRL_9, CONTROL_SIGNAL_WIDTH+1)) when MAPPING_NUM > 9 else (others => '0');
    control_vectors(10) <= std_logic_vector(to_unsigned(CTRL_10, CONTROL_SIGNAL_WIDTH+1)) when MAPPING_NUM > 10 else (others => '0');
    control_vectors(11) <= std_logic_vector(to_unsigned(CTRL_11, CONTROL_SIGNAL_WIDTH+1)) when MAPPING_NUM > 11 else (others => '0');
    control_vectors(12) <= std_logic_vector(to_unsigned(CTRL_12, CONTROL_SIGNAL_WIDTH+1)) when MAPPING_NUM > 12 else (others => '0');
    control_vectors(13) <= std_logic_vector(to_unsigned(CTRL_13, CONTROL_SIGNAL_WIDTH+1)) when MAPPING_NUM > 13 else (others => '0');
    control_vectors(14) <= std_logic_vector(to_unsigned(CTRL_14, CONTROL_SIGNAL_WIDTH+1)) when MAPPING_NUM > 14 else (others => '0');
    control_vectors(15) <= std_logic_vector(to_unsigned(CTRL_15, CONTROL_SIGNAL_WIDTH+1)) when MAPPING_NUM > 15 else (others => '0');
    
    -- Build the mapping matrix
    for i in 0 to MAPPING_NUM-1 loop
      op_to_control_map(i, 0) <= operation_vectors(i);
      op_to_control_map(i, 1) <= control_vectors(i);
    end loop;
  end procedure;

begin
  -- Initialize arrays
  init_arrays;
  
  -- Instantiate the actual decoder
  decoder_inst : entity work.generic_operation_decoder
    generic map (
      OP_WIDTH               => OP_WIDTH,
      CONTROL_SIGNAL_WIDTH   => CONTROL_SIGNAL_WIDTH,
      MAPPING_NUM            => MAPPING_NUM,
      OP_TO_CONTROL_MAP      => op_to_control_map,
      DEFAULT_CONTROL_SIGNAL => default_control_slv
    )
    port map (
      operation              => operation,
      control_signal         => control_signal_internal
    );
    
  -- Connect internal signal to output
  control_signal <= control_signal_internal;
  
  -- Debug process
  debug_proc: process(operation, control_signal_internal)
  begin
    if DEBUG_LEVEL > 0 then
      report "DECODER: Input operation = " & slv_to_string(operation);
      report "DECODER: Output control_signal = " & slv_to_string(control_signal_internal);
      
      if DEBUG_LEVEL > 1 then
        report "DECODER: Checking against " & integer'image(MAPPING_NUM) & " mappings";
        for i in 0 to MAPPING_NUM-1 loop
          report "DECODER: Mapping " & integer'image(i) & 
                 ": operation=" & slv_to_string(operation_vectors(i)) & 
                 " -> control=" & slv_to_string(control_vectors(i));
        end loop;
      end if;
    end if;
  end process;
end architecture Behavioral;
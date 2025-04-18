-- =============================================================================
-- Entity: GPIO_OPERATION_DECODER
-- Description:
--   Decodes read/write operations for a memory-mapped GPIO peripheral.
--   Supports direction and output control, interrupt mask configuration,
--   and interrupt status clearing. Provides a multiplexer selector for readback.
-- =============================================================================

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

library WORK;

-- -----------------------------------------------------------------------------
-- Entity Declaration
-- -----------------------------------------------------------------------------
entity GPIO_OPERATION_DECODER is
  generic (
    -- Width of the address bus
    ADDR_WIDTH : natural := 4
  );
  port (
    -- Bus interface
    address : in  std_logic_vector(ADDR_WIDTH - 1 downto 0);
    -- Write control signal
    write   : in  std_logic;
    -- Read control signal 
    read    : in  std_logic;
    -- GPIO write operations
    wr_dir  : out std_logic; -- Write to DIRECTION register (input/output configuration)
    wr_out  : out std_logic; -- Write to OUTPUT register (any operation type)
    wr_op   : out std_logic_vector(1 downto 0); -- Write Output Selector (LOAD, SET, CLEAR, TOGGLE)

    -- GPIO interrupt configuration
    wr_irq_mask  : out std_logic; -- Write to IRQ mask register
    wr_rise_mask : out std_logic; -- Write to rising-edge IRQ mask
    wr_fall_mask : out std_logic; -- Write to falling-edge IRQ mask
    wr_irq_clr   : out std_logic; -- Write-1-to-clear interrupt status

    -- Read selector (used by output multiplexer)
    rd_sel : out std_logic_vector(2 downto 0)
  );
end entity;

-- -----------------------------------------------------------------------------
-- Architecture Definition
-- -----------------------------------------------------------------------------
architecture RTL of GPIO_OPERATION_DECODER is

  -- ===========================================================================
  -- WRITE Address Map Direction and Output Control
  -- ===========================================================================
  constant ADDR_WR_DIR      : std_logic_vector(3 downto 0) := "0000";
  constant ADDR_WR_OUT_LOAD : std_logic_vector(3 downto 0) := "0001";
  constant ADDR_WR_OUT_SET  : std_logic_vector(3 downto 0) := "0010";
  constant ADDR_WR_OUT_CLR  : std_logic_vector(3 downto 0) := "0011";
  constant ADDR_WR_OUT_TGL  : std_logic_vector(3 downto 0) := "0100";
  -- ===========================================================================
  -- WRITE Address Map Interrupt Control
  -- ===========================================================================
  constant ADDR_WR_IRQ_MASK  : std_logic_vector(3 downto 0) := "0101";
  constant ADDR_WR_RISE_MASK : std_logic_vector(3 downto 0) := "0110";
  constant ADDR_WR_FALL_MASK : std_logic_vector(3 downto 0) := "0111";
  constant ADDR_WR_IRQ_CLR   : std_logic_vector(3 downto 0) := "1000";

  -- ===========================================================================
  -- READ Address Map Registers and Pins
  -- ===========================================================================
  constant ADDR_RD_DIR       : std_logic_vector(3 downto 0) := "1001";
  constant ADDR_RD_OUT       : std_logic_vector(3 downto 0) := "1010";
  constant ADDR_RD_PINS     : std_logic_vector(3 downto 0) := "1011";
  constant ADDR_RD_IRQ_STAT  : std_logic_vector(3 downto 0) := "1100";
  constant ADDR_RD_IRQ_MASK  : std_logic_vector(3 downto 0) := "1101";
  constant ADDR_RD_RISE_MASK : std_logic_vector(3 downto 0) := "1110";
  constant ADDR_RD_FALL_MASK : std_logic_vector(3 downto 0) := "1111";

begin

  -----------------------------------------------------------------------------
  -- WRITE DECODING
  -----------------------------------------------------------------------------

  -- Enable write to DIRECTION register
  wr_dir <= write when address = ADDR_WR_DIR else '0';

  -- Enable write to OUTPUT register for any OUT operation type
  wr_out <= write when address = ADDR_WR_OUT_LOAD or
                      address = ADDR_WR_OUT_SET or
                      address = ADDR_WR_OUT_CLR or
                      address = ADDR_WR_OUT_TGL else '0';

  -- Select output operation type (LOAD, SET, CLEAR, TOGGLE)
  with address select
    wr_op <= "00" when ADDR_WR_OUT_LOAD, -- LOAD
             "01" when ADDR_WR_OUT_SET,  -- SET
             "10" when ADDR_WR_OUT_CLR,  -- CLEAR
             "11" when ADDR_WR_OUT_TGL,  -- TOGGLE
             "00" when others;           -- default: LOAD

  -- Enable write to IRQ mask register
  wr_irq_mask  <= write when address = ADDR_WR_IRQ_MASK  else '0';
  -- Enable write to rising-edge IRQ mask register  
  wr_rise_mask <= write when address = ADDR_WR_RISE_MASK else '0';
  -- Enable write to falling-edge IRQ mask register
  wr_fall_mask <= write when address = ADDR_WR_FALL_MASK else '0';
  -- Enable write to IRQ status clear register
  wr_irq_clr   <= write when address = ADDR_WR_IRQ_CLR   else '0';

  -----------------------------------------------------------------------------
  -- READ DECODING (selector for multiplexer)
  -----------------------------------------------------------------------------
  with address select
    rd_sel <= "000" when ADDR_RD_DIR,        -- 000 = DIRECTION register
              "001" when ADDR_RD_OUT,        -- 001 = OUTPUT register
              "010" when ADDR_RD_PINS,       -- 010 = INPUT register
              "011" when ADDR_RD_IRQ_STAT,   -- 011 = IRQ STATUS
              "100" when ADDR_RD_IRQ_MASK,   -- 100 = IRQ MASK
              "101" when ADDR_RD_RISE_MASK,  -- 101 = RISE MASK
              "110" when ADDR_RD_FALL_MASK,  -- 110 = FALL MASK
              "111" when others;             -- 111 = NOP / HIGH-Z

end architecture;

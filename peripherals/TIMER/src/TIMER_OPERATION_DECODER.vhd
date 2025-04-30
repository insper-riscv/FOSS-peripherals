-- =============================================================================
-- Entity: TIMER_OPERATION_DECODER
-- Description:
--   Decodes read / write accesses for a memory-mapped Timer-/PWM-peripheral.
--   Generates one-hot write-enables, a counter-input selector, and a
--   read-multiplexer selector.
-- =============================================================================

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

-- -----------------------------------------------------------------------------
-- Entity Declaration
-- -----------------------------------------------------------------------------
entity TIMER_OPERATION_DECODER is
  port (
    -- Bus interface 
    address : in  std_logic_vector(3 downto 0);  -- 4-bit address from CPU
    write   : in  std_logic;                     -- Active-high write strobe
    read    : in  std_logic;                     -- Active-high read  strobe

    -- Vector of write enables (see bit-map below) 
    wr_en   : out std_logic_vector(8 downto 0);

    -- Counter input selector (cnt_sel)
    cnt_sel : out std_logic;

    -- Read selector for the peripheral read-back multiplexer
    rd_sel  : out std_logic_vector(2 downto 0)
  );
end entity TIMER_OPERATION_DECODER;

-- -----------------------------------------------------------------------------
-- Architecture Definition
-- -----------------------------------------------------------------------------
architecture RTL of TIMER_OPERATION_DECODER is

  -- ===========================================================================
  -- WRITE-ENABLE VECTOR BIT MAP  (wr_en)
  -- ===========================================================================
  --   Bit : Purpose
  --   ----+------------------------------------------------------------
  --    0  | WR_START_STOP  – Start / Stop register
  --    1  | WR_MODE        – Hold-mode enable
  --    2  | WR_PWM_EN      – PWM output enable
  --    3  | WR_LOAD_TIMER  – Load current counter value
  --    4  | WR_LOAD_TOP    – Load TOP register
  --    5  | WR_LOAD_DUTY   – Load DUTY-CYCLE register
  --    6  | WR_IRQ_MASK    – Global overflow-interrupt mask
  --    7  | WR_OVF_CLR     – Read-to-clear overflow status (pulse on read)
  --    8  | WR_RESET       – Reset the timer
  -- ===========================================================================
  constant WR_START_STOP_I : integer := 0;
  constant WR_MODE_I       : integer := 1;
  constant WR_PWM_EN_I     : integer := 2;
  constant WR_LOAD_TIMER_I : integer := 3;
  constant WR_LOAD_TOP_I   : integer := 4;
  constant WR_LOAD_DUTY_I  : integer := 5;
  constant WR_IRQ_MASK_I   : integer := 6;
  constant WR_OVF_CLR_I    : integer := 7;
  constant WR_RESET_I     : integer := 8; 

  -- ===========================================================================
  -- WRITE Address Map  (0000 … 0110)
  -- ===========================================================================
  constant ADDR_WR_START_STOP : std_logic_vector(3 downto 0) := "0000";
  constant ADDR_WR_MODE       : std_logic_vector(3 downto 0) := "0001";
  constant ADDR_WR_PWM_EN     : std_logic_vector(3 downto 0) := "0010";
  constant ADDR_WR_LOAD_TIMER : std_logic_vector(3 downto 0) := "0011";
  constant ADDR_WR_LOAD_TOP   : std_logic_vector(3 downto 0) := "0100";
  constant ADDR_WR_LOAD_DUTY  : std_logic_vector(3 downto 0) := "0101";
  constant ADDR_WR_IRQ_MASK   : std_logic_vector(3 downto 0) := "0110";
  constant ADDR_WR_RESET      : std_logic_vector(3 downto 0) := "0111"; 

  -- ===========================================================================
  -- READ Address Map  (1000 … 1110)
  -- ADDR_RD_CONFIGS is a read-back of the configs where bit 0 is the start/stop bit, bit 1 is the mode bit,
  -- bit 2 is the PWM enable bit and bit 3 is the interruption enable bit.
  -- ===========================================================================
  constant ADDR_RD_TIMER      : std_logic_vector(3 downto 0) := "1000";
  constant ADDR_RD_TOP        : std_logic_vector(3 downto 0) := "1001";
  constant ADDR_RD_DUTY       : std_logic_vector(3 downto 0) := "1010";
  constant ADDR_RD_CONFIGS       : std_logic_vector(3 downto 0) := "1011";
  constant ADDR_RD_PWM        : std_logic_vector(3 downto 0) := "1100";
  constant ADDR_RD_OVF_STATUS : std_logic_vector(3 downto 0) := "1101"; -- r-to-c

begin

  -- -----------------------------------------------------------------------------
  -- WRITE DECODING : generate one-cycle write-enable strobes
  -- -----------------------------------------------------------------------------
  wr_en(WR_START_STOP_I) <= write when address = ADDR_WR_START_STOP else '0';
  wr_en(WR_MODE_I)       <= write when address = ADDR_WR_MODE       else '0';
  wr_en(WR_PWM_EN_I)     <= write when address = ADDR_WR_PWM_EN     else '0';
  wr_en(WR_LOAD_TIMER_I) <= write when address = ADDR_WR_LOAD_TIMER else '0';
  wr_en(WR_LOAD_TOP_I)   <= write when address = ADDR_WR_LOAD_TOP   else '0';
  wr_en(WR_LOAD_DUTY_I)  <= write when address = ADDR_WR_LOAD_DUTY  else '0';
  wr_en(WR_IRQ_MASK_I)   <= write when address = ADDR_WR_IRQ_MASK   else '0';
  wr_en(WR_RESET_I)      <= write when address = ADDR_WR_RESET      else '0'; 

  -- Read-to-clear overflow flag (pulse aligned with the READ)
  wr_en(WR_OVF_CLR_I)    <= read  when address = ADDR_RD_OVF_STATUS else '0';

  

  -- -----------------------------------------------------------------------------
  -- COUNTER INPUT SELECTOR (cnt_sel)
  --   0 = use “counter + 1”
  --   1 = load external value (WR_LOAD_TIMER)
  -- -----------------------------------------------------------------------------
  cnt_sel <= '1' when (address = ADDR_WR_LOAD_TIMER and write = '1') else '0';

  -- -----------------------------------------------------------------------------
  -- READ-BACK OPERATION: multiplexer selector (rd_sel)
  -- -----------------------------------------------------------------------------
  with address select
    rd_sel <= "000" when ADDR_RD_TIMER,       -- 000 = Current counter
              "001" when ADDR_RD_TOP,         -- 001 = TOP register
              "010" when ADDR_RD_DUTY,        -- 010 = DUTY-CYCLE register
              "011" when ADDR_RD_CONFIGS,     -- 011 = Configs bits
              "100" when ADDR_RD_PWM,         -- 100 = PWM output
              "101" when ADDR_RD_OVF_STATUS,  -- 110 = Overflow status (r-to-c)
              "111" when others;              -- 111 = RESERVED / NOP

end architecture RTL;

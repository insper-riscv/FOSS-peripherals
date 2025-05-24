library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity generic_baud_generator_enhanced is
    generic (
        COUNTER_WIDTH     : natural := 16;
        FRACTIONAL_WIDTH  : natural := 8   -- Width of fractional part
    );
    port (
        clk               : in  std_logic;
        reset             : in  std_logic;
        
        -- Integer part of baud divisor
        baud_div_i        : in  unsigned(COUNTER_WIDTH-1 downto 0);
        
        -- Fractional part of baud divisor (for fine-tuning)
        baud_frac_i       : in  unsigned(FRACTIONAL_WIDTH-1 downto 0);
        
        -- Enable fractional mode
        fractional_en_i   : in  std_logic;
        
        -- Baud tick output
        tick              : out std_logic;
        
        -- Debug/monitoring
        counter_debug_o   : out unsigned(COUNTER_WIDTH-1 downto 0)
    );
end entity generic_baud_generator_enhanced;

architecture Behavioral of generic_baud_generator_enhanced is
    -- Main counter
    signal counter : unsigned(COUNTER_WIDTH-1 downto 0) := (others => '0');
    
    -- Fractional accumulator for sub-clock precision
    signal frac_accumulator : unsigned(FRACTIONAL_WIDTH-1 downto 0) := (others => '0');
    
    -- Internal tick generation
    signal tick_internal : std_logic := '0';
    
    -- Effective divisor calculation
    signal effective_divisor : unsigned(COUNTER_WIDTH-1 downto 0);
    signal should_adjust : std_logic;
    
begin
    -- Debug output
    counter_debug_o <= counter;
    
    -- Calculate if we should adjust the divisor this cycle (fractional compensation)
    -- This implements a simple sigma-delta approach for fractional division
    should_adjust <= '1' when (fractional_en_i = '1' and 
                              frac_accumulator >= (2**(FRACTIONAL_WIDTH-1))) else '0';
    
    -- Effective divisor is either base divisor or base divisor - 1 (for fractional)
    effective_divisor <= baud_div_i - 1 when should_adjust = '1' else baud_div_i;
    
    process(clk)
    begin
        if rising_edge(clk) then
            if reset = '1' then
                counter <= (others => '0');
                frac_accumulator <= (others => '0');
                tick_internal <= '0';
            else
                -- Default tick to 0
                tick_internal <= '0';
                
                -- Main counter logic
                if counter >= effective_divisor then
                    counter <= (others => '0');
                    tick_internal <= '1';
                    
                    -- Update fractional accumulator when tick occurs
                    if fractional_en_i = '1' then
                        frac_accumulator <= frac_accumulator + baud_frac_i;
                    end if;
                else
                    counter <= counter + 1;
                end if;
            end if;
        end if;
    end process;
    
    -- Output the tick
    tick <= tick_internal;
    
end architecture Behavioral; 
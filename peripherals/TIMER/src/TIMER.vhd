library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

library WORK;

entity TIMER is
    generic (
        -- Data Bus Width
        DATA_WIDTH : integer := 32
    );
    port (
        -- Clock Signal
        clock       : in  std_logic;
        -- Clear Signal
        clear       : in  std_logic; 
        -- Data Inputed from the Processor
        data_in     : in  STD_LOGIC_VECTOR(DATA_WIDTH-1 downto 0);
        -- GPIO Address accessed by the Processor
        address     : in  STD_LOGIC_VECTOR(3 downto 0);
        -- Write Signal
        write       : in  std_logic; 
        -- Read Signal
        read        : in  std_logic; 
        -- Data Outputed to the Processor
        data_out    : out STD_LOGIC_VECTOR(DATA_WIDTH-1 downto 0);
        -- Interrupt Request Signal (active high)
        irq         : out std_logic;
        -- PWM Output Signal (Pulse Width Modulation)
        pwm        : out std_logic
    );
end entity;

architecture RTL of TIMER is
    -----------------------------------------------------------------------------
    -- Internal Control Signals
    -----------------------------------------------------------------------------
    signal wr_en   : std_logic_vector(8 downto 0); -- Write enable signals
    signal cnt_sel : std_logic;             -- Counter input selector
    signal rd_sel  : std_logic_vector(2 downto 0); -- Readback selector 
    -----------------------------------------------------------------------------
    -- Register Signals
    -----------------------------------------------------------------------------
    signal top_reg  : std_logic_vector(DATA_WIDTH-1 downto 0); -- Top register
    signal duty_reg : std_logic_vector(DATA_WIDTH-1 downto 0); -- Duty register

    -----------------------------------------------------------------------------
    -- State Signals
    -----------------------------------------------------------------------------
    signal start_signal : std_logic; -- Start/Stop signal for the timer
    signal mode_signal  : std_logic; -- Mode signal for the timer
    signal pwm_en       : std_logic; -- PWM enable signal
    signal overflow      : std_logic; -- Overflow signal (active high)
    signal overflow_prev   : std_logic;  -- registered copy of overflow
    signal overflow_pulse  : std_logic;  -- 1-cycle edge pulse
    signal irq_mask  : std_logic; -- IRQ mask register
    signal overflow_status : std_logic; -- Overflow status signal
    signal pwm_out       : std_logic; -- PWM output signal
    signal pwm_alu      : std_logic; -- PWM ALU output signal
    signal irq_vec       : std_logic_vector(0 downto 0); -- IRQ vector signal

    ---------------------------------------------------------------------------
    -- Multiplexer Signals
    ---------------------------------------------------------------------------
    signal mux_cnt : std_logic_vector(DATA_WIDTH-1 downto 0); -- Mux output for cnt_sel
    signal mux_out : std_logic_vector(DATA_WIDTH-1 downto 0); -- Mux output for data_out
    signal configs_readback : std_logic_vector(DATA_WIDTH-1 downto 0); -- Config register output
    signal pwm_readback : std_logic_vector(DATA_WIDTH-1 downto 0); -- PWM readback signal
    signal overflow_readback : std_logic_vector(DATA_WIDTH-1 downto 0); -- Overflow readback signal
    ---------------------------------------------------------------------------
    -- Counter Signals
    ---------------------------------------------------------------------------
    signal counter : std_logic_vector(DATA_WIDTH-1 downto 0); -- Counter value
    signal next_counter : std_logic_vector(DATA_WIDTH-1 downto 0); -- Next counter value




begin

    -------------------------------------------------------------------------------
    -- TIMER_OPERATION_DECODER  
    -------------------------------------------------------------------------------
    U_TIMER_OPERATION_DECODER : entity work.TIMER_OPERATION_DECODER
        port map (
            address => address,
            write   => write,
            read    => read,
            wr_en   => wr_en,
            cnt_sel => cnt_sel,
            rd_sel  => rd_sel
        );
    
    -------------------------------------------------------------------------------
    -- Start/Stop Flip-Flop
    -- This flip-flop is used to control the start and stop of the timer.
    -- When the start signal is '1', the timer starts counting. When it is '0',
    -- the timer stops counting.
    -------------------------------------------------------------------------------
    U_START_STOP : entity WORK.GENERIC_FLIP_FLOP
        port map (
            clock       => clock,
            clear       => clear,
            enable      => wr_en(0), -- Enable signal for the flip-flop
            source      => data_in(0), -- Data input to the flip-flop. 1 for start, 0 for stop.
            destination => start_signal -- Enable signal for the timer
        );

    -------------------------------------------------------------------------------
    -- Mode Flip-Flop
    -- This flip-flop is used to control the mode of the timer.
    -- When the mode signal is '1', the timer operates in hold mode. When it is '0',
    -- the timer operates in auto-reset.
    -------------------------------------------------------------------------------
    U_MODE : entity WORK.GENERIC_FLIP_FLOP
        port map (
            clock       => clock,
            clear       => clear,
            enable      => wr_en(1), -- Enable signal for the flip-flop
            source      => data_in(0), -- Data input to the flip-flop. 1 for hold mode, 0 for auto-reset.
            destination => mode_signal -- Mode signal for the timer
        );
    
    ---------------------------------------------------------------------------
    -- Mux Counter Selector
    -- Loads or increments the counter based on the cnt_sel signal.
    -- If cnt_sel is '1', the counter is loaded with the data_in value.
    -- If cnt_sel is '0', the counter is incremented by 1.
    ---------------------------------------------------------------------------
    U_MUX_CNT_SEL : entity WORK.GENERIC_MUX_2X1
        generic map (
            DATA_WIDTH => DATA_WIDTH
        )
        port map (
            selector    => cnt_sel, -- Counter selector signal
            source_1    => next_counter, -- Source 0 for the multiplexer (next counter value)
            source_2    => data_in, -- Source 1 for the multiplexer (data input)
            destination => mux_cnt -- Mux output for the counter selector
        );

    ---------------------------------------------------------------------------
    -- Counter Register
    -- This register holds the current value of the timer counter.
    -- Clear signal resets the counter to zero. It clears on system reset, on timer reset or 
    -- when the overflow signal is high and the mode signal is auto-reset.
    -- Counter enabled on load or when the start signal is high and there is no overflow in hold mode. 
    ------------------------------------------------------------------------------
    U_COUNTER_REG : entity WORK.GENERIC_REGISTER
        generic map (
            DATA_WIDTH => DATA_WIDTH
        )
        port map (
            clock       => clock,
            clear       => clear or wr_en(8) or (overflow and not(mode_signal)), -- Clear signal for the register
            enable       => wr_en(3) or (start_signal and not(overflow and mode_signal)), -- Enable signal for the register
            source     => mux_cnt, -- Data input to the register (mux output)
            destination    => counter -- Data output from the register (current counter value)
        );
    ----------------------------------------------------------------------------
    -- Constant Adder
    -- This adder is used to increment the counter by 1.
    ------------------------------------------------------------------------------
    U_CONSTANT_ADDER : entity WORK.GENERIC_ADDER
        generic map (
            DATA_WIDTH => DATA_WIDTH,
            DEFAULT_SOURCE_2 => 1 -- Constant value to add (1)
        )
        port map (
            source_1    => counter, -- Current counter value
            destination => next_counter -- Next counter value (incremented by 1)
        );

    --------------------------------------------------------------------------
    -- Top Register
    -- It is used to set the maximum count value for the timer. As default, it is set to 0xFFFFFFFF and it clears to the same value.
    -- It is loaded with the data_in value when the wr_en(4) signal is high.
    --------------------------------------------------------------------------
    U_TOP_REG : entity WORK.GENERIC_REGISTER
        generic map (
            DATA_WIDTH => DATA_WIDTH,
            CLEAR_VALUE => '1' -- Clear value for the register (all bits set to 1)
        )
        port map (
            clock       => clock,
            clear       => clear,
            enable       => wr_en(4), -- Enable signal for the register
            source     => data_in, -- Data input to the register
            destination    => top_reg -- Data output from the register
        );

    ---------------------------------------------------------------------------
    -- Overflow Detection Unity
    -- Overflow occurs when the counter reaches the top value.
    ---------------------------------------------------------------------------
    U_COUNTER_OVERFLOW : entity WORK.COUNTER_OVERFLOW
        generic map (
            DATA_WIDTH => DATA_WIDTH
        )
        port map (
            counter_value => counter, -- Current counter value
            top_value     => top_reg, -- Top register value
            overflow      => overflow -- Overflow signal (active high)
        );
    
    ---------------------------------------------------------------------------
    -- IRQ Mask Register
    -- This register holds the IRQ mask value.
    -- It is loaded with the data_in value when the wr_en(6) signal is high.
    -- The IRQ mask is used to enable or disable the overflow interrupt.
    ---------------------------------------------------------------------------
    U_IRQ_MASK_REG : entity WORK.GENERIC_FLIP_FLOP
        port map (
            clock       => clock,
            clear       => clear,
            enable       => wr_en(6), -- Enable signal for the register
            source     => data_in(0), -- Data input to the register
            destination    => irq_mask -- Data output from the register (IRQ mask value)
        );

    -- ============================================================================
    -- REGISTER THE PREVIOUS OVERFLOW
    -- 
    -- ============================================================================
    U_OVF_PREV : entity WORK.GENERIC_FLIP_FLOP
        port map (
        clock       => clock,
        clear       => clear,
        enable      => '1',          -- always capture
        source      => overflow,     -- current overflow level
        destination => overflow_prev -- previous cycle value
    );
    overflow_pulse <= overflow and not overflow_prev;
    ---------------------------------------------------------------------------
    -- Overflow Status Register
    -- This register holds the overflow status of the timer.
    -- It is cleared on read or when the overflow signal is high.
    ---------------------------------------------------------------------------
    U_IRQ_STATUS_REG : entity WORK.GENERIC_FLIP_FLOP
        port map (
            clock       => clock,
            clear       => clear or wr_en(7), -- Clear signal for the register
            enable       => overflow_pulse, -- Enable signal for the register (overflow signal)
            source     => '1', 
            destination    => overflow_status -- Data output from the register (overflow status)
        );

    ---------------------------------------------------------------------------
    -- MUX IRQ Selector
    -- IRQ signal is selected based on the IRQ mask value.
    -- If the IRQ mask is '1', the IRQ signal is asserted when overflow occurs.
    -- If the IRQ mask is '0', the IRQ signal is not asserted.
    -- This is used to enable or disable the overflow interrupt.
    -------------------------------------------------------------------------------
    U_MUX_IRQ_SEL : entity WORK.GENERIC_MUX_2X1
        generic map (
            DATA_WIDTH => 1
        )
        port map (
            selector    => irq_mask, -- convert std_logic to std_logic_vector(0 downto 0)
            source_1    => (0 => '0'),  -- if not enabled no IRQ. 
            source_2    => (0 => overflow_status), -- if enabled, IRQ is asserted when overflow occurs.
            destination => irq_vec
        );
    irq <= irq_vec(0); -- Assign the IRQ signal to the output

    ---------------------------------------------------------------------------
    -- Duty Register
    -- This register holds the duty cycle value for the PWM output.
    -- It is loaded with the data_in value when the wr_en(5) signal is high.
    -- The duty cycle value is used to control the width of the PWM pulse.
    ---------------------------------------------------------------------------
    U_DUTY_REG : entity WORK.GENERIC_REGISTER
        generic map (
            DATA_WIDTH => DATA_WIDTH
        )
        port map (
            clock       => clock,
            clear       => clear,
            enable       => wr_en(5), -- Enable signal for the register
            source     => data_in, -- Data input to the register
            destination    => duty_reg -- Data output from the register
        );

    ---------------------------------------------------------------------------
    -- PWM Enable Flip-Flop
    -- This flip-flop is used to control the PWM output.
    -- When the PWM enable signal is '1', the PWM output is enabled. When it is '0',
    -- the PWM output is disabled.
    ------------------------------------------------------------------------------
    U_PWM_EN : entity WORK.GENERIC_FLIP_FLOP
        port map (
            clock       => clock,
            clear       => clear,
            enable      => wr_en(2), -- Enable signal for the flip-flop
            source      => data_in(0), -- Data input to the flip-flop. 1 for PWM enable, 0 for PWM disable.
            destination => pwm_en -- PWM enable signal for the timer
        );
    ---------------------------------------------------------------------------
    -- PWM ALU
    -- This ALU is used to compare the current counter value with the duty cycle value.
    -- It outputs a signal indicating whether the counter is less than the duty cycle.
    -- This signal is used to control the PWM output.
    ---------------------------------------------------------------------------
    U_PWM_ALU : entity WORK.ALU_GE_UNSIGNED
        generic map (
            DATA_WIDTH => DATA_WIDTH
        )
        port map (
            source_1    => counter, -- Current counter value
            source_2    => duty_reg, -- Duty cycle value
            ge         => pwm_alu -- PWM output signal (1 when counter < duty cycle)
        );

    ---------------------------------------------------------------------------
    -- PWM Tristate Buffer
    -- This buffer is used to control the PWM output signal.
    -- When the PWM enable signal is '1', the PWM output is driven by the PWM ALU.
    ---------------------------------------------------------------------------
    U_PWM_TRISTATE : entity WORK.TRISTATE_BUFFER_1BIT
        port map (
            data_in  => not(pwm_alu), -- Data input to the buffer (PWM ALU output)
            enable   => pwm_en, -- Enable signal for the buffer (PWM enable signal)
            data_out => pwm_out -- Data output from the buffer (PWM output signal)
        );
    pwm <= pwm_out; -- Assign the PWM output signal to the output
    ---------------------------------------------------------------------------
    -- Mux Output Selector
    -- This multiplexer selects the output data based on the read signal and the rd_sel signal.
    -- If read is '1', the output is selected based on the rd_sel signal.
    -- If read is '0', the output is selected based on the cnt_sel signal.
    ---------------------------------------------------------------------------
    configs_readback <= (31 downto 4 => '0') & (irq_mask & pwm_en & mode_signal & start_signal); -- Concatenate the registers for the multiplexer
    pwm_readback <= (31 downto 1 => '0') & pwm_out; -- Concatenate the PWM output for the multiplexer
    overflow_readback <= (31 downto 1 => '0') & overflow; -- Concatenate the overflow status for the multiplexer
    U_MUX_OUT_SEL : entity WORK.GENERIC_MUX_8X1
        generic map (
            DATA_WIDTH => DATA_WIDTH
        )
        port map (
            selector    => rd_sel, -- Read selector signal
            source_1    => counter, -- Source 0 for the multiplexer (current counter value)
            source_2    => top_reg, -- Source 1 for the multiplexer (top register value)
            source_3    => duty_reg, -- Source 2 for the multiplexer (duty cycle value)
            source_4    =>  configs_readback, -- Source 3 for the multiplexer (config register value)
            source_5    => pwm_readback , -- Source 4 for the multiplexer (not used)
            source_6    => overflow_readback, -- Source 5 for the multiplexer (not used)
            source_7    => (others => '0'), -- Source 6 for the multiplexer (not used)
            source_8    => (others => '0'), -- Source 7 for the multiplexer (not used)
            destination => data_out -- Mux output for the data_out signal
        );
end architecture;
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

library WORK;


entity GPIO is
    generic (
        --! Largura dos vetores de dados
        DATA_WIDTH : integer := 32
    );
    port (
        --! Clock do Processador
        clock       : in  std_logic;
        --! Reset Sincrono dos Registradores
        clear     : in  std_logic; 
        --! Vetor de dados de Entrada
        data_in  : in  STD_LOGIC_VECTOR(DATA_WIDTH-1 downto 0);
        --! Flag de Habilita Direção, Escrita e Leitura
        dir_enable    : in  std_logic;
        write_enable   : in  std_logic;
        read_enable   : in  std_logic;
        --! Seletor de Load, set, clear e toggle
        op_out  :    in  STD_LOGIC_VECTOR(1 downto 0);
        --! Vetor de dados de Saída
        data_out : out STD_LOGIC_VECTOR(DATA_WIDTH-1 downto 0);
        --! Pinos da GPIO
        gpio_pins : inout std_logic_vector(DATA_WIDTH-1 downto 0)
    );

end GPIO;

architecture RTL of GPIO is
    -- Controla each a direção de cada pino ('1' = output, '0' = input)
    signal reg_dir : std_logic_vector(DATA_WIDTH - 1 downto 0) := (others => '0');
    -- Guarda os valores de saída dos pinos
    signal reg_out : std_logic_vector(DATA_WIDTH-1 downto 0) := (others => '0');
    --! Sinais de entrada para o MUX
    signal mux_input_1 : std_logic_vector(DATA_WIDTH-1 downto 0);
    signal mux_input_2 : std_logic_vector(DATA_WIDTH-1 downto 0);
    signal mux_input_3 : std_logic_vector(DATA_WIDTH-1 downto 0);
    signal mux_input_4 : std_logic_vector(DATA_WIDTH-1 downto 0);
    signal mux_output  : std_logic_vector(DATA_WIDTH-1 downto 0);

begin
   
    
    --! Definir os valores das entradas do MUX
    mux_input_1 <= data_in;               --! LOAD (00)
    mux_input_2 <= reg_out OR data_in;  --! SET (01)
    mux_input_3 <= reg_out AND NOT data_in; --! CLEAR (10)
    mux_input_4 <= reg_out XOR data_in; --! TOGGLE (11)

    -- Mux de Operação de Output
    MUX_OUT: entity WORK.GENERIC_MUX_4X1
        generic map (
            DATA_WIDTH => DATA_WIDTH
        )
        port map (
            selector   => op_out,
            source_1   => mux_input_1,
            source_2   => mux_input_2,
            source_3   => mux_input_3,
            source_4   => mux_input_4,
            destination => mux_output
        );

    --! Registrador que armazena a direção de cada pino.
    REG_DIR : GENERIC_REGISTER
        generic map (
            DATA_WIDTH => DATA_WIDTH
        )
        port map (
            clock       => clock,
            clear       => clear,
            enable      => dir_enable,
            source      => data_in,
            destination => reg_dir
        );

    --! Registrador que armazena os valores de saida de cada pino.
    REG_OUT : GENERIC_REGISTER
        generic map (
            DATA_WIDTH => DATA_WIDTH
        )
        port map (
            clock       => clock,
            clear       => clear,
            enable      => write_enable,
            source      => mux_output,
            destination => reg_out
        );

    --! Registrador que armazena os valores de entrada de cada pino.
    REG_IN : GENERIC_REGISTER
        generic map (
            DATA_WIDTH => DATA_WIDTH
        )
        port map (
            clock       => clock,
            clear       => clear,
            enable      => read_enable,
            source      => gpio_pins,
            destination => data_out
        );
    
    --! Registrador que armazena os valores de entrada de cada pino.
    TRISTATE_BUFFER_GPIO : GENERIC_TRISTATE_BUFFER
        generic map (
            DATA_WIDTH => DATA_WIDTH
        )
        port map (
            data_in       => out_reg,
            enable       => dir_reg,
            data_out      => gpio_pins
        );
end architecture;
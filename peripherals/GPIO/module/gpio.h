#ifndef GPIO_H
#define GPIO_H

#include <stdint.h>
#include <stddef.h>

/* ---------------------------------------------------------------------------
 * Base address ‑‑ change to match your memory map.
 * ---------------------------------------------------------------------------
 */
#ifndef GPIO_BASE_DEFAULT
#define GPIO_BASE_DEFAULT   0x40000000u
#endif

/* ---------------------------------------------------------------------------
 * Write Operations Offset
 * ---------------------------------------------------------------------------
 */
#define GPIO_WR_DIR_OFFSET        (0x0u << 2)    // 0000
#define GPIO_WR_OUT_LOAD_OFFSET   (0x1u << 2)    // 0001 
#define GPIO_WR_OUT_SET_OFFSET    (0x2u << 2)    // 0010 
#define GPIO_WR_OUT_CLR_OFFSET    (0x3u << 2)    // 0011 
#define GPIO_WR_OUT_TGL_OFFSET    (0x4u << 2)    // 0100 
#define GPIO_WR_IRQ_MASK_OFFSET   (0x5u << 2)    // 0101 
#define GPIO_WR_RISE_MASK_OFFSET  (0x6u << 2)    // 0110 
#define GPIO_WR_FALL_MASK_OFFSET  (0x7u << 2)    // 0111 
#define GPIO_WR_IRQ_CLR_OFFSET    (0x8u << 2)    // 1000 

/* ---------------------------------------------------------------------------
 * Read Operations Offset
 * ---------------------------------------------------------------------------
 */
#define GPIO_RD_DIR_OFFSET        (0x9u << 2)    // 1001 
#define GPIO_RD_OUT_OFFSET        (0xAu << 2)    // 1010 
#define GPIO_RD_PINS_OFFSET      (0xBu << 2)     // 1011 
#define GPIO_RD_IRQ_STAT_OFFSET   (0xCu << 2)    // 1100 
#define GPIO_RD_IRQ_MASK_OFFSET   (0xDu << 2)    // 1101 
#define GPIO_RD_RISE_MASK_OFFSET  (0xEu << 2)    // 1110 
#define GPIO_RD_FALL_MASK_OFFSET  (0xFu << 2)    // 1111 

/* ---------------------------------------------------------------------------
 * Configuration Structure for Init
 * --------------------------------------------------------------------------
 */
typedef struct {
    uint32_t direction;      // Direction mask: 1 = output, 0 = input
    uint32_t irq_mask;       // Interrupt mask: 1 = enable, 0 = disable
    uint32_t irq_rise_mask;  // Rising edge mask: 1 = enable, 0 = disable
    uint32_t irq_fall_mask;  // Falling edge mask: 1 = enable, 0 = disable
} gpio_config_t;



/* ---------------------------------------------------------------------------
 * Functions
 * --------------------------------------------------------------------------
 */
void      gpio_init(uintptr_t base_addr, const gpio_config_t *cfg); // Initialize GPIO with base address and configuration
void      gpio_set_direction(uint32_t dir_mask);   // Set Direction of Pins: 1 = output, 0 = input
void      gpio_load_pins(uint32_t value);          // Load whole port with value
void      gpio_set_pins(uint32_t mask);            // Set selected bits to 1
void      gpio_clear_pins(uint32_t mask);          // Clear selected bits to 0
void      gpio_toggle_pins(uint32_t mask);         // Invert selected bits
void      gpio_irq_set_mask(uint32_t mask);        // Set IRQ of Pins: 1 = enable, 0 = disable
void      gpio_irq_set_rise_mask(uint32_t mask);   // Set rising edge IRQ of Pins: 1 = enable, 0 = disable
void      gpio_irq_set_fall_mask(uint32_t mask);   // Set falling edge IRQ of Pins: 1 = enable, 0 = disable
void      gpio_irq_clear(uint32_t mask);           // Clear IRQ status


uint32_t  gpio_read_dir(void);                      // Read back direction configuration
uint32_t  gpio_read_output(void);                   // Read back output register value
uint32_t  gpio_read_pins(void);                     // Read back pins value     
uint32_t  gpio_read_irq_status(void);               // Get IRQ status of Pins: 1 = active, 0 = inactive
uint32_t  gpio_read_irq_mask(void);                 // Get IRQ mask of Pins: 1 = enabled, 0 = disabled
uint32_t  gpio_read_irq_rise_mask(void);            // Get rising edge IRQ mask of Pins: 1 = enabled, 0 = disabled
uint32_t  gpio_read_irq_fall_mask(void);            // Get falling edge IRQ mask of Pins: 1 = enabled, 0 = disabled
#endif

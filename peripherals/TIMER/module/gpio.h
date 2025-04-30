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
#define GPIO_WR_DIR_OFFSET        (0x0u << 2)    // 0000: Write Direction Register
#define GPIO_WR_OUT_LOAD_OFFSET   (0x1u << 2)    // 0001: Load Output Register
#define GPIO_WR_OUT_SET_OFFSET    (0x2u << 2)    // 0010: Set Output Bits
#define GPIO_WR_OUT_CLR_OFFSET    (0x3u << 2)    // 0011: Clear Output Bits
#define GPIO_WR_OUT_TGL_OFFSET    (0x4u << 2)    // 0100: Toggle Output Bits
#define GPIO_WR_IRQ_MASK_OFFSET   (0x5u << 2)    // 0101: Write IRQ Mask
#define GPIO_WR_RISE_MASK_OFFSET  (0x6u << 2)    // 0110: Write Rising Edge Mask
#define GPIO_WR_FALL_MASK_OFFSET  (0x7u << 2)    // 0111: Write Falling Edge Mask

/* ---------------------------------------------------------------------------
 * Read Operations Offset
 * ---------------------------------------------------------------------------
 */
#define GPIO_RD_DIR_OFFSET        (0x8u << 2)    // 1000: Read Direction
#define GPIO_RD_OUT_OFFSET        (0x9u << 2)    // 1001: Read Output Register
#define GPIO_RD_PINS_OFFSET       (0xAu << 2)    // 1010: Read Input Pins
#define GPIO_RD_IRQ_STAT_OFFSET   (0xBu << 2)    // 1011: Read IRQ Status
#define GPIO_RD_IRQ_MASK_OFFSET   (0xCu << 2)    // 1100: Read IRQ Mask
#define GPIO_RD_RISE_MASK_OFFSET  (0xDu << 2)    // 1101: Read Rising Edge Mask
#define GPIO_RD_FALL_MASK_OFFSET  (0xEu << 2)    // 1110: Read Falling Edge Mask

/* ---------------------------------------------------------------------------
 * Configuration Structure
 * ---------------------------------------------------------------------------
 */
typedef struct {
    uint32_t direction;       // 1 = output, 0 = input
    uint32_t irq_mask;        // 1 = enabled, 0 = disabled
    uint32_t irq_rise_mask;   // 1 = rising enabled, 0 = disabled
    uint32_t irq_fall_mask;   // 1 = falling enabled, 0 = disabled
} gpio_config_t;

/* ---------------------------------------------------------------------------
 * Functions
 * ---------------------------------------------------------------------------
 */
void      gpio_init(uintptr_t base_addr, const gpio_config_t *cfg);

void      gpio_set_direction(uint32_t dir_mask);
void      gpio_load_pins(uint32_t value);
void      gpio_set_pins(uint32_t mask);
void      gpio_clear_pins(uint32_t mask);
void      gpio_toggle_pins(uint32_t mask);
void      gpio_irq_set_mask(uint32_t mask);
void      gpio_irq_set_rise_mask(uint32_t mask);
void      gpio_irq_set_fall_mask(uint32_t mask);

uint32_t  gpio_read_dir(void);
uint32_t  gpio_read_output(void);
uint32_t  gpio_read_pins(void);
uint32_t  gpio_read_irq_status(void);
uint32_t  gpio_read_irq_mask(void);
uint32_t  gpio_read_irq_rise_mask(void);
uint32_t  gpio_read_irq_fall_mask(void);

#endif

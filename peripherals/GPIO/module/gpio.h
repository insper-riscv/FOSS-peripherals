#ifndef GPIO_H
#define GPIO_H

#include <stdint.h>
#include <stddef.h>

/* ---------------------------------------------------------------------------
 * Base address — change to match your memory map.
 * ---------------------------------------------------------------------------
 */
#ifndef GPIO_BASE_DEFAULT
#define GPIO_BASE_DEFAULT   0x40000000u
#endif

/* ---------------------------------------------------------------------------
 * Read and Write Register Offsets
 * ---------------------------------------------------------------------------
 */
#define GPIO_DIR_OFFSET        (0x0u << 2)    // 0000: Direction Register
#define GPIO_OUT_LOAD_OFFSET   (0x1u << 2)    // 0001: Output Register (load)
#define GPIO_OUT_SET_OFFSET    (0x2u << 2)    // 0010: Output Register (set)
#define GPIO_OUT_CLR_OFFSET    (0x3u << 2)    // 0011: Output Register (clear)
#define GPIO_OUT_TGL_OFFSET    (0x4u << 2)    // 0100: Output Register (toggle)
#define GPIO_IRQ_MASK_OFFSET   (0x5u << 2)    // 0101: IRQ Mask Register
#define GPIO_RISE_MASK_OFFSET  (0x6u << 2)    // 0110: Rising Edge Mask Register
#define GPIO_FALL_MASK_OFFSET  (0x7u << 2)    // 0111: Falling Edge Mask Register

/* ---------------------------------------------------------------------------
 * Read Only Register and Pins Offset
 * ---------------------------------------------------------------------------
 */
#define GPIO_IRQ_STAT_OFFSET   (0x8u << 2)    // 1000: IRQ Status Register
#define GPIO_PINS_OFFSET       (0x9u << 2)    // 1001: Pins Offset


/* ---------------------------------------------------------------------------
 * Configuration Structure
 * ---------------------------------------------------------------------------
 */
typedef struct {
    uint32_t direction;       // 1 = output, 0 = input
    uint32_t irq_mask;        // 1 = enabled, 0 = disabled
    uint32_t irq_rise_mask;   // 1 = rising enabled
    uint32_t irq_fall_mask;   // 1 = falling enabled
} gpio_config_t;

/* ---------------------------------------------------------------------------
 * Functions Skeletons
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

#endif // GPIO_H

#include "gpio.h"

// Default base address for GPIO peripheral
static uintptr_t gpio_base = GPIO_BASE_DEFAULT;

// Macro to access GPIO Memory Region (offset + base address) 
#define REG(off)  (*(volatile uint32_t *)(gpio_base + (off)))


/* ---------------------------------------------------------------------------
 * GPIO Configuration
 * 1. Set the base address
 * 2. Set the direction of the GPIO pins
 * 3. Set the interrupt mask
 * 4. Set the rising edge interrupt mask
 * --------------------------------------------------------------------------*/
void gpio_init(uintptr_t base_addr, const gpio_config_t *cfg){
    // 1. Set the base address
    gpio_base = base_addr;
    if (cfg == NULL)  return;
    // 2. Set the direction of the GPIO pins
    REG(GPIO_WR_DIR_OFFSET)        = cfg->direction;
    // 3. Set the interrupt mask
    REG(GPIO_WR_IRQ_MASK_OFFSET)  = cfg->irq_mask;
    // 4. Set the rising edge interrupt mask
    REG(GPIO_WR_RISE_MASK_OFFSET) = cfg->irq_rise_mask;
    // 5. Set the falling edge interrupt mask
    REG(GPIO_WR_FALL_MASK_OFFSET) = cfg->irq_fall_mask;
}

/* ---------------------------------------------------------------------------
 * Direction Configuration: 1 = output, 0 = input
 * --------------------------------------------------------------------------*/
void gpio_set_direction(uint32_t dir_mask){
    REG(GPIO_WR_DIR_OFFSET) = dir_mask;
}

/* ---------------------------------------------------------------------------
 * OUTPUT register helpers
 *   LOAD    ‑ Load whole port with a value
 *   SET     ‑ Set selected bits to 1
 *   CLEAR   ‑ Clear selected bits to 0
 *   TOGGLE  ‑ Invert selected bits
 * --------------------------------------------------------------------------*/
void gpio_load_pins(uint32_t value)   { REG(GPIO_WR_OUT_LOAD_OFFSET) = value; }
void gpio_set_pins(uint32_t mask)     { REG(GPIO_WR_OUT_SET_OFFSET)  = mask;  }
void gpio_clear_pins(uint32_t mask)   { REG(GPIO_WR_OUT_CLR_OFFSET)  = mask;  }
void gpio_toggle_pins(uint32_t mask)  { REG(GPIO_WR_OUT_TGL_OFFSET)  = mask;  }

/* ---------------------------------------------------------------------------
 * Interrupt control
 * --------------------------------------------------------------------------*/
void gpio_irq_set_mask(uint32_t mask)      { REG(GPIO_WR_IRQ_MASK_OFFSET)  = mask; }
void gpio_irq_set_rise_mask(uint32_t mask) { REG(GPIO_WR_RISE_MASK_OFFSET) = mask; }
void gpio_irq_set_fall_mask(uint32_t mask) { REG(GPIO_WR_FALL_MASK_OFFSET) = mask; }


/* ---------------------------------------------------------------------------
 * Read‑back helpers
 * --------------------------------------------------------------------------
 */
uint32_t gpio_read_dir(void)     { return REG(GPIO_RD_DIR_OFFSET);   }
uint32_t gpio_read_output(void) { return REG(GPIO_RD_OUT_OFFSET);   }
uint32_t gpio_read_pins(void)   { return REG(GPIO_RD_PINS_OFFSET); }
uint32_t gpio_read_irq_status(void) { return REG(GPIO_RD_IRQ_STAT_OFFSET); }
uint32_t gpio_read_irq_mask(void) { return REG(GPIO_RD_IRQ_MASK_OFFSET); }
uint32_t gpio_read_irq_rise_mask(void) { return REG(GPIO_RD_RISE_MASK_OFFSET); }
uint32_t gpio_read_irq_fall_mask(void) { return REG(GPIO_RD_FALL_MASK_OFFSET); }

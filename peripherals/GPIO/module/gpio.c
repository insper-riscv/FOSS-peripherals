#include "gpio.h"


/* ---------------------------------------------------------------------------
 * GPIO Initialization
 * ---------------------------------------------------------------------------
 */
void gpio_init(uintptr_t base_addr, const gpio_config_t *cfg){
    gpio_base = base_addr;
    if (cfg == NULL) return;

    MEMO(GPIO_DIR_OFFSET)        = cfg->direction;
    MEMO(GPIO_IRQ_MASK_OFFSET)  = cfg->irq_mask;
    MEMO(GPIO_RISE_MASK_OFFSET) = cfg->irq_rise_mask;
    MEMO(GPIO_FALL_MASK_OFFSET) = cfg->irq_fall_mask;
}

/* ---------------------------------------------------------------------------
 * Direction Configuration: 1 = output, 0 = input
 * ---------------------------------------------------------------------------
 */
void gpio_set_direction(uint32_t dir_mask) {MEMO(GPIO_DIR_OFFSET) = dir_mask;}

/* ---------------------------------------------------------------------------
 * OUTPUT MEMOister helpers
 * ---------------------------------------------------------------------------
 */
void gpio_load_pins(uint32_t value)   { MEMO(GPIO_OUT_LOAD_OFFSET) = value; }
void gpio_set_pins(uint32_t mask)     { MEMO(GPIO_OUT_SET_OFFSET)  = mask;  }
void gpio_clear_pins(uint32_t mask)   { MEMO(GPIO_OUT_CLR_OFFSET)  = mask;  }
void gpio_toggle_pins(uint32_t mask)  { MEMO(GPIO_OUT_TGL_OFFSET)  = mask;  }

/* ---------------------------------------------------------------------------
 * Interrupt configuration
 * ---------------------------------------------------------------------------
 */
void gpio_irq_set_mask(uint32_t mask)      { MEMO(GPIO_IRQ_MASK_OFFSET)  = mask; }
void gpio_irq_set_rise_mask(uint32_t mask) { MEMO(GPIO_RISE_MASK_OFFSET) = mask; }
void gpio_irq_set_fall_mask(uint32_t mask) { MEMO(GPIO_FALL_MASK_OFFSET) = mask; }

/* ---------------------------------------------------------------------------
 * Read-back functions
 * ---------------------------------------------------------------------------
 */
uint32_t gpio_read_dir(void)             { return MEMO(GPIO_DIR_OFFSET);        }
uint32_t gpio_read_output(void)          { return MEMO(GPIO_OUT_LOAD_OFFSET);        }
uint32_t gpio_read_pins(void)            { return MEMO(GPIO_PINS_OFFSET);       }
uint32_t gpio_read_irq_mask(void)        { return MEMO(GPIO_IRQ_MASK_OFFSET);   }
uint32_t gpio_read_irq_rise_mask(void)   { return MEMO(GPIO_RISE_MASK_OFFSET);  }
uint32_t gpio_read_irq_fall_mask(void)   { return MEMO(GPIO_FALL_MASK_OFFSET);  }

/* ---------------------------------------------------------------------------
 * Read-Clear functions
 * ---------------------------------------------------------------------------
 */
uint32_t gpio_read_irq_status(void)      { return MEMO(GPIO_IRQ_STAT_OFFSET);   }
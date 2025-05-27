#ifndef TIMER_H
#define TIMER_H

#include <stdint.h>
#include <stddef.h>

// ----------------------------------------------------------------------------
// Base Address (Change according to memory map)
// ----------------------------------------------------------------------------
#ifndef TIMER_BASE
#define TIMER_BASE  0x3000u
#endif

// ----------------------------------------------------------------------------
// Word-Aligned Register Offsets
// ----------------------------------------------------------------------------
#define TIMER_CONFIG_OFFSET      (0x0u << 2)
#define TIMER_TIMER_LOAD_OFFSET  (0x1u << 2)
#define TIMER_TIMER_RESET_OFFSET (0x2u << 2)
#define TIMER_TOP_OFFSET         (0x3u << 2)
#define TIMER_DUTY_CYCLE_OFFSET        (0x4u << 2)
#define TIMER_OVF_STATUS_OFFSET  (0x5u << 2)
#define TIMER_PWM_OFFSET         (0x6u << 2)
#define TIMER_PRESCALER_OFFSET   (0x7u << 2)

// ----------------------------------------------------------------------------
// Memory Access Macro
// ----------------------------------------------------------------------------
#define MEMO(offset) (*(volatile uint32_t *)(TIMER_BASE + (offset)))

// ----------------------------------------------------------------------------
// Config Register Bit Positions
// ----------------------------------------------------------------------------
#define TIMER_CFG_START_BIT     0
#define TIMER_CFG_MODE_BIT      1
#define TIMER_CFG_PWM_EN_BIT    2
#define TIMER_CFG_IRQ_MASK_BIT  3

// ----------------------------------------------------------------------------
// Timer Configuration Structure
// ----------------------------------------------------------------------------
typedef struct {
    uint32_t start;        // 1 = start enabled
    uint32_t mode;         // 1 = hold mode, 0 = wrap
    uint32_t pwm_enable;   // 1 = enable PWM
    uint32_t irq_mask;     // 1 = enable IRQ
    uint32_t top;          // Top value for counter
    uint32_t duty;         // PWM duty cycle
    uint32_t prescaler;    // Prescaler value
    uint32_t initial_value; // Preload value for counter
} timer_config_t;



// ----------------------------------------------------------------------------
// Configure all timer registers in one call using a config struct
// ----------------------------------------------------------------------------
void timer_configure(uintptr_t base, const timer_config_t *cfg);

// ----------------------------------------------------------------------------
// Individual Write Functions
// ----------------------------------------------------------------------------
void timer_write_config_reg(uintptr_t base, uint32_t config_word);
void timer_write_top(uintptr_t base, uint32_t top);
void timer_write_duty(uintptr_t base, uint32_t duty);
void timer_write_prescaler(uintptr_t base, uint32_t prescaler);
void timer_write_counter(uintptr_t base, uint32_t value);
void timer_reset_counter(uintptr_t base);

// ----------------------------------------------------------------------------
// Individual Read Functions
// ----------------------------------------------------------------------------
uint32_t timer_read_counter(uintptr_t base);
uint32_t timer_read_top(uintptr_t base);
uint32_t timer_read_duty(uintptr_t base);
uint32_t timer_read_prescaler(uintptr_t base);
uint32_t timer_read_config(uintptr_t base);
uint32_t timer_read_pwm(uintptr_t base);
uint32_t timer_read_status(uintptr_t base);


#endif // TIMER_H

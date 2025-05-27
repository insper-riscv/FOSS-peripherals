#include "timer.h"

void timer_configure( const timer_config_t *cfg) {
    if (!cfg) return;

    // Set prescaler first to stabilize tick domain
    timer_write_prescaler( cfg->prescaler);

    // Write top and duty values
    timer_write_top( cfg->top);
    timer_write_duty( cfg->duty);

    // Preload the counter with the initial value
    timer_write_counter( cfg->initial_value);

    // Construct config word from individual bits
    uint32_t config_word = 0;
    config_word |= (cfg->start     & 0x1) << TIMER_CFG_START_BIT;
    config_word |= (cfg->mode      & 0x1) << TIMER_CFG_MODE_BIT;
    config_word |= (cfg->pwm_enable & 0x1) << TIMER_CFG_PWM_EN_BIT;
    config_word |= (cfg->irq_mask  & 0x1) << TIMER_CFG_IRQ_MASK_BIT;

    timer_write_config_reg(config_word);
}



// ----------------------------------------------------------------------------
// Write Register Functions
// ----------------------------------------------------------------------------
void timer_write_config_reg(uint32_t config_word) {MEMO(TIMER_CONFIG_OFFSET) = config_word;}

void timer_write_top( uint32_t top) {MEMO(TIMER_TOP_OFFSET) = top;}

void timer_write_duty( uint32_t duty) {MEMO(TIMER_DUTY_CYCLE_OFFSET) = duty;}

void timer_write_prescaler( uint32_t prescaler) {MEMO(TIMER_PRESCALER_OFFSET) = prescaler;}

void timer_write_counter( uint32_t value) {MEMO(TIMER_TIMER_LOAD_OFFSET) = value;}

void timer_reset_counter(void) {MEMO(TIMER_TIMER_RESET_OFFSET) = 0;}

// ----------------------------------------------------------------------------
//  Read-back functions
// ----------------------------------------------------------------------------
uint32_t timer_read_counter(void) {return MEMO(TIMER_TIMER_LOAD_OFFSET);}

uint32_t timer_read_top(void) {return MEMO(TIMER_TOP_OFFSET);}

uint32_t timer_read_duty(void) {return MEMO(TIMER_DUTY_CYCLE_OFFSET);}

uint32_t timer_read_prescaler(void) { return MEMO(TIMER_PRESCALER_OFFSET);}

uint32_t timer_read_config(void) {return MEMO(TIMER_CONFIG_OFFSET);}

uint32_t timer_read_pwm(void) {return MEMO(TIMER_PWM_OFFSET);}

/* ---------------------------------------------------------------------------
 * Read-Clear functions
 * ---------------------------------------------------------------------------
 */

uint32_t timer_read_status(void) {return MEMO(TIMER_OVF_STATUS_OFFSET);}

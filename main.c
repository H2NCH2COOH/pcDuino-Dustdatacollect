/*---------------------------------------------------------------------------*/
#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/eeprom.h>
#include <util/delay.h>
#include <commonconfig.h>

#include <stdio.h>
#include <string.h>

#include "lcd.h"
#include "task.h"
#include "timer.h"
#include "display.h"

#define DUST_DDR    DDRE
#define DUST_PORT   PORTE
#define DUST_PIN    PINE
#define DUST_BIT    0

#define BUTTON_DDR    DDRE
#define BUTTON_PORT   PORTE
#define BUTTON_PIN    PINE
#define BUTTON_BIT    1
#define button_down() (!(BUTTON_PIN&(1<<BUTTON_BIT)))

typedef uint32_t count_t;
typedef uint32_t sum_t;

#define COUNT_1S    977UL
#define COUNT_3S    2930UL
#define COUNT_10S   9766UL
#define COUNT_30S   29297UL

static char init_str[]="   STARTING...  ";
static char str[17]={0};

#define DATA_AVE_NUM    10
static count_t old_data[DATA_AVE_NUM-1]={0};
static uint8_t new_data_ptr=0;
static uint8_t old_data_number=0;

static count_t dust_count=0;
static count_t dust_low_c=0;

static uint8_t bar_c=0;
static char empty_bar[]="                ";

static count_t countdown_1s=0;
static count_t countdown_3s=0;
static count_t countdown_10s=0;

static uint8_t button_short_press=0;
static uint8_t button_long_press=0;

#define HISTORY_NUMBER          12
#define HISTORY_GEN_INTERVAL    10
#define HISTORY_VIEW_INTERVAL   12
#define HISTORY_BUF_SIZE        (HISTORY_NUMBER*HISTORY_VIEW_INTERVAL+10)
static count_t history[HISTORY_BUF_SIZE]={0};
static uint8_t history_p=0;

#define EEPROM_DATA_TYPE    ((uint8_t*)10)
#define DATA_TYPE_NUM       3
#define DATA_TYPE_UG        0
#define DATA_TYPE_PC        1
#define DATA_TYPE_DY        2
static char* data_type_background[]=
    {
        "ug/m3:    %6ld",
        "pcs/283ml:%6ld",
        "DylosEq:  %6ld"
    };
static char data_type_select[]="Data Mode Select";
static char* data_type_name[]=
    {
        "     ug/m3      ",
        "    pcs/283ml   ",
        "Dylos Equivalent"
    };
/*---------------------------------------------------------------------------*/
static count_t data_convert(count_t data,uint8_t type)
{
    double ret=0;
    double d=(double)data;
    switch(type)
    {
        case DATA_TYPE_UG:
            ret+=6e-9;
            ret*=d;
            ret-=3e-7;
            ret*=d;
            ret+=0.3195;
            ret*=d;
            break;
        case DATA_TYPE_PC:
            ret=62500.0/COUNT_30S;
            ret*=d;
            break;
        case DATA_TYPE_DY:
            ret=d*15;
            break;
        default:
            ret=(double)d;
            break;
    }
    
    return (count_t)ret;
}
/*---------------------------------------------------------------------------*/
static TIMER_HANDLER(TH_countdown_1s)
{
    if(countdown_1s<=0)
    {
        countdown_1s=0;
        remove_timer_handler(TH_countdown_1s);
    }
    else
    {
        --countdown_1s;
    }
}

static TIMER_HANDLER(TH_countdown_3s)
{
    if(countdown_3s<=0)
    {
        countdown_3s=0;
        remove_timer_handler(TH_countdown_3s);
    }
    else
    {
        --countdown_3s;
    }
}

static TIMER_HANDLER(TH_countdown_10s)
{
    if(countdown_10s<=0)
    {
        countdown_10s=0;
        remove_timer_handler(TH_countdown_10s);
    }
    else
    {
        --countdown_10s;
    }
}
/*---------------------------------------------------------------------------*/
static TASK(T_button)
{
    static uint8_t pressing=0;
    
    if(button_short_press==1)
    {
        button_short_press=0;
    }
    
    if(button_long_press==1)
    {
        button_long_press=0;
    }
    
    if(countdown_1s==0&&pressing==0&&button_down())
    {
        pressing=1;
        countdown_3s=COUNT_3S;
        add_timer_handler(TH_countdown_3s);
    }
    
    if(pressing==1&&(COUNT_3S-countdown_3s)>10)
    {
        if(!button_down())
        {
            pressing=0;
            
            countdown_1s=COUNT_1S;
            add_timer_handler(TH_countdown_1s);

            button_short_press=1;
            remove_timer_handler(TH_countdown_3s);
            countdown_3s=0;
        }
        else if(countdown_3s==0)
        {
            pressing=0;
            
            countdown_1s=COUNT_1S;
            add_timer_handler(TH_countdown_1s);
            
            button_long_press=1;
        }
    }
}
/*---------------------------------------------------------------------------*/
static TASK(T_history)
{
    static count_t current_display_value=0;
    static uint8_t current_display_type=0;
    
    if(button_short_press)
    {
        countdown_10s=COUNT_10S;
        add_timer_handler(TH_countdown_10s);
        
        static uint8_t current_history=1;
        
        if(get_display_state()!=DISPLAY_STATE_HISTORY)
        {
            current_history=1;
        }
        
        sprintf(str,"History: %2dh Ago",current_history);
        update_display_str(DISPLAY_STATE_HISTORY,0,0,str);
        
        uint8_t t=
            (
                HISTORY_BUF_SIZE+
                history_p-1-
                current_history*HISTORY_VIEW_INTERVAL
            )%HISTORY_BUF_SIZE;
        
        sum_t sum=0;
        uint8_t i=0,j,c=0;
        for(i=0;i<HISTORY_VIEW_INTERVAL;++i)
        {
            j=(t+i)%HISTORY_BUF_SIZE;
            if(history[j]>0)
            {
                sum+=history[j];
                ++c;
            }
        }
        if(c>0)
        {
            sum=(count_t)(sum/c);
        }
        else
        {
            sum=0;
        }
        
        eeprom_busy_wait();
        uint8_t type=eeprom_read_byte(EEPROM_DATA_TYPE);
        sprintf(str,data_type_background[type],data_convert(sum,type));
        update_display_str(DISPLAY_STATE_HISTORY,0,1,str);
        current_display_value=sum;
        current_display_type=type;
        
        switch_display_state(DISPLAY_STATE_HISTORY);
        
        ++current_history;
        if(current_history>HISTORY_NUMBER)
        {
            current_history=1;
        }
    }
    
    if(countdown_10s==0)
    {
        switch_display_state(DISPLAY_STATE_REALTIME);
    }
    
    if(get_display_state()==DISPLAY_STATE_HISTORY)
    {
        eeprom_busy_wait();
        uint8_t type=eeprom_read_byte(EEPROM_DATA_TYPE);
        if(current_display_type!=type)
        {
            sprintf
            (
                str,
                data_type_background[type],
                data_convert(current_display_value,type)
            );
            update_display_str(DISPLAY_STATE_HISTORY,0,1,str);
            current_display_type=type;
        }
    }
}
/*---------------------------------------------------------------------------*/
static TASK(T_type_select)
{
    static uint8_t selecting=0;
    
    static count_t last_countdown_10s=0;
    static uint8_t last_display_state=0;
    
    if(selecting==0)
    {
        if(button_long_press)
        {
            selecting=1;
            
            last_countdown_10s=countdown_10s;
            remove_timer_handler(TH_countdown_10s);
            countdown_10s=COUNT_10S;
            add_timer_handler(TH_countdown_10s);
            
            last_display_state=get_display_state();
            
            remove_task(T_history);
            
            eeprom_busy_wait();
            uint8_t type=eeprom_read_byte(EEPROM_DATA_TYPE);
            
            update_display_str
            (
                DISPLAY_STATE_TYPESELEC,0,0,data_type_select
            );
            update_display_str
            (
                DISPLAY_STATE_TYPESELEC,0,1,data_type_name[type]
            );
            
            switch_display_state(DISPLAY_STATE_TYPESELEC);
        }
    }
    else
    {
        if(countdown_10s==0)
        {
            countdown_10s=last_countdown_10s;
            if(countdown_10s>0)
            {
                add_timer_handler(TH_countdown_10s);
            }
            
            switch_display_state(last_display_state);
            
            add_task(T_history);
            
            selecting=0;
        }
        else if(button_long_press||button_short_press)
        {
            countdown_10s=COUNT_10S;
            add_timer_handler(TH_countdown_10s);
            
            eeprom_busy_wait();
            uint8_t type=eeprom_read_byte(EEPROM_DATA_TYPE);
            
            type=(type+1)%DATA_TYPE_NUM;
            
            eeprom_busy_wait();
            eeprom_write_byte(EEPROM_DATA_TYPE,type);
            
            update_display_str
            (
                DISPLAY_STATE_TYPESELEC,0,1,data_type_name[type]
            );
        }
    }
}
/*---------------------------------------------------------------------------*/
static TIMER_HANDLER(TH_dust_data_collect)
{
    ++dust_count;
    
    if(!(DUST_PIN&(1<<DUST_BIT)))
    {
        ++dust_low_c;
    }
    
    if(dust_count>=(COUNT_30S/17*(bar_c+1)))
    {
        ++bar_c;
    }
}

static TASK(T_bar_update)
{
    static uint8_t last_bar_c=0;
    if(last_bar_c!=bar_c)
    {
        if(bar_c>0)
        {
            uint8_t st=get_display_state();
            if(st==DISPLAY_STATE_REALTIME||st==DISPLAY_STATE_STARTING)
            {
                update_display_char(st,bar_c-1,1,255);
            }
            else
            {
                update_display_char(DISPLAY_STATE_REALTIME,bar_c-1,1,255);
            }
        }
        last_bar_c=bar_c;
    }
}

static TASK(T_dust_calc)
{
    count_t loc_dust_count;
    count_t loc_dust_low_c;
    
    static count_t current_display_value=0;
    static uint8_t current_display_type=0;
    
    loc_dust_count=dust_count;
    loc_dust_low_c=dust_low_c;
    
    if(loc_dust_count>=COUNT_30S)
    {
        bar_c=0;
        
        dust_count=0;
        dust_low_c=0;
         
        sum_t sum=0;
        uint8_t i=0;
        for(i=0;i<DATA_AVE_NUM-1;++i)
        {
            if(i>=old_data_number)
            {
                break;
            }
            sum+=old_data[i];
        }
        sum+=loc_dust_low_c;

        count_t ave=sum/(old_data_number+1);
        
        old_data[new_data_ptr]=loc_dust_low_c;
        new_data_ptr=(new_data_ptr+1)%(DATA_AVE_NUM-1);
        ++old_data_number;
        if(old_data_number>=DATA_AVE_NUM)
        {
            old_data_number=DATA_AVE_NUM-1;
        }
        
        eeprom_busy_wait();
        uint8_t type=eeprom_read_byte(EEPROM_DATA_TYPE);
        
        sprintf(str,data_type_background[type],data_convert(ave,type));
        current_display_value=ave;
        current_display_type=type;
        update_display_str(DISPLAY_STATE_REALTIME,0,0,str);
        update_display_str(DISPLAY_STATE_REALTIME,0,1,empty_bar);
        
        if(get_display_state()==DISPLAY_STATE_STARTING)
        {
            switch_display_state(DISPLAY_STATE_REALTIME);
            
            add_task(T_button);
            add_task(T_history);
  		add_task(T_type_select);
        }
        
        static uint16_t history_interval_c=0;
        if(++history_interval_c>HISTORY_GEN_INTERVAL)
        {
            history_interval_c=0;
            
            history[history_p]=ave;
            history_p=(history_p+1)%HISTORY_BUF_SIZE;
        }
    }
    
    if(get_display_state()==DISPLAY_STATE_REALTIME)
    {
        eeprom_busy_wait();
        uint8_t type=eeprom_read_byte(EEPROM_DATA_TYPE);
        if(current_display_type!=type)
        {
            sprintf
            (
                str,
                data_type_background[type],
                data_convert(current_display_value,type)
            );
            update_display_str(DISPLAY_STATE_REALTIME,0,0,str);
            current_display_type=type;
        }
    }
}
/*---------------------------------------------------------------------------*/
static void main_init(void)
{
    CLI();
    
    display_init(DISPLAY_STATE_STARTING);
    
    DUST_DDR&=~(1<<DUST_BIT);
    DUST_PORT&=~(1<<DUST_BIT);
    
    BUTTON_DDR&=~(1<<BUTTON_BIT);
    BUTTON_PORT|=(1<<BUTTON_BIT);
    
    TCCR0=(1<<CS01)|(1<<CS00);//fclk/32
    TIMSK|=(1<<TOIE0);
}

int main(void)
{
    main_init();
    
    eeprom_busy_wait();
    uint8_t type=eeprom_read_byte(EEPROM_DATA_TYPE);
    if(type>=DATA_TYPE_NUM)
    {
        eeprom_busy_wait();
        eeprom_write_byte(EEPROM_DATA_TYPE,0);
    }
    
    update_display_str(DISPLAY_STATE_STARTING,0,0,init_str);
    
    add_timer_handler(TH_dust_data_collect);
    
    add_task(T_dust_calc);
    add_task(T_bar_update);
    
    SEI();
    
    while(TRUE)
    {
        do_tasks();
    }

    return 0;
}
/*---------------------------------------------------------------------------*/

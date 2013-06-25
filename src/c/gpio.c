#include <stdlib.h>
#include <stdio.h>

#include "gpio.h"

#define GPIO_MODE_FILE_FORMAT "/sys/devices/virtual/misc/gpio/mode/gpio%d"
#define GPIO_PIN_FILE_FORMAT "/sys/devices/virtual/misc/gpio/pin/gpio%d"

static char name_buff[128];

void set_gpio_mode(int pin,int mode)
{
    FILE* f_mode;
    
    sprintf(name_buff,GPIO_MODE_FILE_FORMAT,pin);
    f_mode=fopen(name_buff,"w");
    if(f_mode==NULL)
    {
        fprintf(stderr,"Unable to open gpio mode file: %s\n",name_buff);
        return;
    }
    
    fwrite((mode==LOW)? "0":"1",1,1,f_mode);
    
    fflush(f_mode);
    fclose(f_mode);
}

int get_gpio_pin(int pin)
{
    FILE* f_pin;
    int c;
    
    sprintf(name_buff,GPIO_PIN_FILE_FORMAT,pin);
    f_pin=fopen(name_buff,"r");
    if(f_pin==NULL)
    {
        fprintf(stderr,"Unable to open gpio pin file: %s\n",name_buff);
        return -1;
    }
    
    c=fgetc(f_pin);
    fclose(f_pin);
    
    if(c=='0')
    {
        return LOW;
    }
    else if(c=='1')
    {
        return HIGH;
    }
    else
    {
        return -1;
    }
}

void set_gpio_pin(int pin,int level)
{
    FILE* f_pin;
    
    sprintf(name_buff,GPIO_PIN_FILE_FORMAT,pin);
    f_pin=fopen(name_buff,"w");
    if(f_pin==NULL)
    {
        fprintf(stderr,"Unable to open gpio pin file: %s\n",name_buff);
        return;
    }
    
    fwrite((level==LOW)? "0":"1",1,1,f_pin);
    
    fflush(f_pin);
    fclose(f_pin);
}

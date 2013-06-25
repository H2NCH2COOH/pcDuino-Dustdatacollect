#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <signal.h>
#include <sys/time.h>

#include "gpio.h"

#define DUST_PIN 4

#define DUST_COUNT_MAX 30000

static long dust_count=0;
static long dust_low_c=0;

#define OLD_DATA_NUMBER 9
static long old_data[OLD_DATA_NUMBER]={0};
static int old_data_ptr=0;

static struct itimerval olditv;

static char feed_id[]="393295424";
static char channel_id[]="test2";
static char xapikey[]="1K23Oupn3VhdrkY1CqpZ7IkBpTpHLCiqAN6ZcTsSC7NIXSBs";

void start_timer(void)
{
    struct itimerval itv;
    itv.it_interval.tv_sec=0;
    itv.it_interval.tv_usec=1000;
    itv.it_value.tv_sec=1;
    itv.it_value.tv_usec=0;
    
    setitimer(ITIMER_REAL,&itv,&olditv);
}

void signal_timer_handler(int s)
{
    int i,dc=0;
    long sum=0;
    
    ++dust_count;
    if(get_gpio_pin(DUST_PIN)==LOW)
    {
        ++dust_low_c;
    }
    
    if(dust_count>=DUST_COUNT_MAX)
    {
        for(i=0;i<OLD_DATA_NUMBER;++i)
        {
            if(old_data[i]>=0)
            {
                sum+=old_data[i];
                ++dc;
            }
        }
        
        sum+=dust_low_c;
        old_data[old_data_ptr]=dust_low_c;
        old_data_ptr=(old_data_ptr+1)%OLD_DATA_NUMBER;
        
        double p=(double)sum;
        p/=(dc+1);
        p/=dust_count;
        p*=100;
        time_t t;
        time(&t);
        printf("Dust Data: %lg%% at %s",p,ctime(&t));
        char cmd[512];
        sprintf(cmd,"curl api.xively.com/v2/feeds/%s/datastreams/%s -H X-ApiKey:%s -X PUT --data \"{\\\"id\\\":\\\"%s\\\",\\\"current_value\\\":\\\"%lg\\\"}\"",feed_id,channel_id,xapikey,channel_id,p);
        system(cmd);
        
        dust_count=0;
        dust_low_c=0;
    }
}

int main(int argc,char *argv[])
{
    int i;
    
    set_gpio_mode(DUST_PIN,INPUT);
    
    for(i=0;i<OLD_DATA_NUMBER;++i)
    {
        old_data[i]=-1;
    }
    
    signal(SIGALRM,signal_timer_handler);
    start_timer();
    
    while(1);
    
    return 0;
}

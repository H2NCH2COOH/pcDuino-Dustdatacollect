import sys
import signal
import time

import urllib
import urllib2

import gpio

DUST_PIN=4

DUST_COUNT_MAX=30000
dust_count=0
dust_low_c=0

OLD_DATA_NUMBER=9
old_data=[]

feed_id="393295424"
channel_id="test2"
xapikey="1K23Oupn3VhdrkY1CqpZ7IkBpTpHLCiqAN6ZcTsSC7NIXSBs"


def timer_handler(signum,frame):
    global dust_count
    global dust_low_c
    
    ++dust_count
    if(gpio.get_gpio_pin(DUST_PIN)==LOW):
        ++dust_low_c
    
    sum=0
    if(dust_count>=DUST_COUNT_MAX):
        for i in old_data:
            if(i>=0):
                sum+=i
                ++dc;
        
        sum+=dust_low_c/dust_count
        old_data.append(dust_low_c/dust_count)
        old_data.remove(0)
        
        p/=(dc+1);
        p*=100;
        
        print("Dust Data: %f%% at %s"%(p,time.ctime()));
        
        while(True):
            req=urllib2.Request
            (
                url="api.xively.com/v2/feeds/%s/datastreams/%s"%(feed_id,channel_id),
                headers={"X-ApiKey":xapikey},
                data="{\"id\":\"%s\",\"current_value\":\"%f\"}"%(channel_id,p)
            )
            req.get_method=lambda: 'PUT'
            
            result=urllib2.urlopen(req)
            
            if(result.getcode()==200):
                break
        
        dust_count=0;
        dust_low_c=0;

signal.signal(signal.SIGALRM,timer_handler)
signal.setitimer(signal.ITIMER_REAL,1,0.001)

def nop():
    return

while(True):
    nop()
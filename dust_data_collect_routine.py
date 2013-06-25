import sys
import signal
import time
import threading

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

def send_data(data):
    try:
        req=urllib2.Request
        (
            "api.xively.com/v2/feeds/%s/datastreams/%s"%(feed_id,channel_id),
            {"X-ApiKey":xapikey},
            "{\"id\":\"%s\",\"current_value\":\"%f\"}"%(channel_id,data)
        )
        req.get_method=lambda: 'PUT'
        
        result=urllib2.urlopen(req)
        
    except Exception as e:
        print(str(e))

def timer_handler(signum,frame):
    global dust_count
    global dust_low_c
    
    dust_count+=1
    if(gpio.get_gpio_pin(DUST_PIN)==gpio.LOW):
        dust_low_c+=1
    
    if(dust_count>=DUST_COUNT_MAX):
        sum=0
        dc=0
        for i in old_data:
            if(i>=0):
                sum+=i
                dc+=1
        
        sum+=dust_low_c/dust_count
        old_data.append(dust_low_c/dust_count)
        if(dc>=OLD_DATA_NUMBER):
            old_data.remove(0)
        
        p=sum/(dc+1)*100
        
        print("Dust Data: %f%% at %s"%(p,time.ctime()))
        
        threading.Thread(send_data,(p))
        
        dust_count=0
        dust_low_c=0

gpio.set_gpio_mode(DUST_PIN,gpio.INPUT)

signal.signal(signal.SIGALRM,timer_handler)
signal.setitimer(signal.ITIMER_REAL,1,0.001)

def nop():
    return

while(True):
    nop()

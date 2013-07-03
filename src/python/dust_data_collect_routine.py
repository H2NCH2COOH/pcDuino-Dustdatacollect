import sys
import signal
import time
import threading

import urllib
import urllib2

import dbus
from dbus.mainloop.glib import DBusGMainLoop

import gpio

DUST_PIN=4

DUST_COUNT_MAX=30000
dust_count=0
dust_low_c=0

OLD_DATA_NUMBER=19
old_data=[]

collector_obj=None

class Collector(dbus.service.Object):
    def __init__(self,obj_path):
        dbus.service.Object.__init__(self,dbus.SessionBus(),obj_path)
    
    @dbus.service.signal(
        dbus_interface="cn.kaiwenmap.airsniffer.pcDuino.Collector",
        signature="ds"
    )
    def NewDustData(self,data,time):
        "NOP"


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
        
        dust_count=0
        dust_low_c=0
        
        print("Dust Data: %f%% at %s"%(p,time.ctime()))
        
        #threading.Thread(target=send_data,args=(p,)).start()
        collector_obj.NewDustData(p,time.ctime())

def ctrl_brk_handler(signum,frame):
    signal.setitimer(signal.ITIMER_REAL,0,0)
    print("\nExit dust data collect routine")
    sys.exit(0)

def nop():
    return

if __name__=='__main__':
    signal.signal(signal.SIGINT,ctrl_brk_handler)
    
    gpio.set_gpio_mode(DUST_PIN,gpio.INPUT)
    
    DBusGMainLoop(set_as_default=True)
    collector_obj=Collector("/cn/kaiwenmap/airsniffer/pcDuino/Collector")

    signal.signal(signal.SIGALRM,timer_handler)
    signal.setitimer(signal.ITIMER_REAL,1,0.001)

    while(True):
        #nop()
        signal.pause()

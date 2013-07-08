import sys
import signal
import time

import urllib
import urllib2

import dbus
from dbus import service
from dbus.mainloop.glib import DBusGMainLoop
import gobject

import gpio

DUST_PIN=4

DUST_COUNT_MAX=30000
dust_count=0
dust_low_c=0

OLD_DATA_NUMBER=19
old_data=[]

collector_obj=None

mainloop=None

class Collector(dbus.service.Object):
    def __init__(self,obj_path):
        dbus.service.Object.__init__(self,dbus.SessionBus(),obj_path)
    
    @dbus.service.signal(
        dbus_interface="cn.kaiwenmap.airsniffer.pcDuino.Collector",
        signature="ds"
    )
    def NewDustData(self,data,time):
        pass
    
    @dbus.service.method(
        dbus_interface="cn.kaiwenmap.airsniffer.pcDuino.Collector",
        in_signature="",
        out_signature=""
    )
    def Stop(self):
        ctrl_brk_handler(None,None)
        


def timer_handler(signum,frame):
    global dust_count
    global dust_low_c
    
    dust_count+=1
    pin=gpio.get_gpio_pin(DUST_PIN)
    if(pin==gpio.LOW):
        dust_low_c+=1
    
    if(dust_count>=DUST_COUNT_MAX):
        s=0.0
        dc=0
        for i in old_data:
            s+=i
            dc+=1
        
        s+=((dust_low_c+0.0)/dust_count)
        
        old_data.append((dust_low_c+0.0)/dust_count)
        if(dc>=OLD_DATA_NUMBER):
            old_data.pop(0)
        
        p=s/(dc+1)*100.0
        
        dust_count=0
        dust_low_c=0
        
        print("Dust Data: %f%% at %s"%(p,time.ctime()))
        
        #threading.Thread(target=send_data,args=(p,)).start()
        collector_obj.NewDustData(p,time.ctime())

def ctrl_brk_handler(signum,frame):
    signal.setitimer(signal.ITIMER_REAL,0,0)
    mainloop.quit()


if __name__=='__main__':
    if len(sys.argv)>1:
        arg=sys.argv[1].lower()
    else:
        arg=""
    
    if arg=="-i" or arg=="--ignore-sigint":
        signal.signal(signal.SIGINT,signal.SIG_IGN)
    else:
        signal.signal(signal.SIGINT,ctrl_brk_handler)
    
    gpio.set_gpio_mode(DUST_PIN,gpio.INPUT)
    
    DBusGMainLoop(set_as_default=True)
    name=dbus.service.BusName("cn.kaiwenmap.airsniffer.pcDuino.Collector",dbus.SessionBus())
    mainloop=gobject.MainLoop()
    
    collector_obj=Collector("/cn/kaiwenmap/airsniffer/pcDuino/Collector")
    
    signal.signal(signal.SIGALRM,timer_handler)
    signal.setitimer(signal.ITIMER_REAL,1,0.001)
    
    print("Enter Collector routine")
    mainloop.run()
    print("Exit Collector routine")


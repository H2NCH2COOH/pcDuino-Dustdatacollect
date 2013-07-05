import sys
import os
import signal
import time
import subprocess

import urllib
import urllib2

import dbus
from dbus import service
from dbus.mainloop.glib import DBusGMainLoop
import gobject

mainloop=None

main_obj=None
collector_obj=None
sender_obj=None

class Main(dbus.service.Object):
    def __init__(self,obj_path):
        dbus.service.Object.__init__(self,dbus.SessionBus(),obj_path)
    
    @dbus.service.method(
        dbus_interface="cn.kaiwenmap.airsniffer.pcDuino.Main",
        in_signature="",
        out_signature=""
    )
    def Stop(self):
        ctrl_brk_handler(None,None)


def ctrl_brk_handler(signum,frame):
    signal.setitimer(signal.ITIMER_REAL,0,0)
    print("Exit Main routine")
    mainloop.quit()

def start_routine(routine,silence=False,sudo=False):
    argv=[]
    if sudo:
        argv.append("sudo")
    argv.append("python")
    argv.append(routine+"_routine.py")
    
    out=None
    if silence:
        out=open(os.devnull)
    
    print "Opening sub routine: "+routine
    
    subp=subprocess.Popen(
        argv,
        stdout=out,
        stderr=None,
        stdin=open(os.devnull)
    )
    
    return subp

if __name__=="__main__":
    signal.signal(signal.SIGINT,ctrl_brk_handler)
    
    DBusGMainLoop(set_as_default=True)
    bus=dbus.SessionBus()
    name=dbus.service.BusName("cn.kaiwenmap.airsniffer.pcDuino.Main",bus)
    mainloop=gobject.MainLoop()
    
    main_obj=Main("/cn/kaiwenmap/airsniffer/pcDuino/Main")
    
    start_routine("collector")
    start_routine("sender")
    
    time.sleep(5)
    
    collector_obj=bus.get_object(
        "cn.kaiwenmap.airsniffer.pcDuino.Collector",
        "/cn/kaiwenmap/airsniffer/pcDuino/Collector"
    )
    sender_obj=bus.get_object(
        "cn.kaiwenmap.airsniffer.pcDuino.Sender",
        "/cn/kaiwenmap/airsniffer/pcDuino/Sender"
    )
    
    print "Enter Main routine"
    mainloop.run()


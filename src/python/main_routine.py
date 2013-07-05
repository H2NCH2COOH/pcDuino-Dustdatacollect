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

collector=None
sender=None

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


class SubRoutine:
    def __init__(self,name,silence=False,sudo=False):
        self.name=name
        self.obj=None
        self.proc=None
        
        argv=[]
        if sudo:
            argv.append("sudo")
        argv.append("python")
        argv.append(self.name.lower()+"_routine.py")
        argv.append("-i")
        
        out=None
        if silence:
            out=open(os.devnull)
        
        #print "Opening sub routine: "+routine
        
        self.proc=subprocess.Popen(
            argv,
            stdout=out,
            stderr=None,
            stdin=open(os.devnull)
        )
        
        time.sleep(2)
        
        self.obj=dbus.SessionBus().get_object(
            "cn.kaiwenmap.airsniffer.pcDuino."+self.name,
            "/cn/kaiwenmap/airsniffer/pcDuino/"+self.name
        )
    
    def stop(self):
        if self.obj is not None:
            self.obj.Stop(dbus_interface="cn.kaiwenmap.airsniffer.pcDuino."+self.name)
        else:
            self.proc.terminate()
        self.proc.wait()

def ctrl_brk_handler(signum,frame):
    signal.setitimer(signal.ITIMER_REAL,0,0)
    mainloop.quit()


if __name__=="__main__":
    signal.signal(signal.SIGINT,ctrl_brk_handler)
    
    DBusGMainLoop(set_as_default=True)
    bus=dbus.SessionBus()
    name=dbus.service.BusName("cn.kaiwenmap.airsniffer.pcDuino.Main",bus)
    mainloop=gobject.MainLoop()
    
    main_obj=Main("/cn/kaiwenmap/airsniffer/pcDuino/Main")
    
    collector=SubRoutine("Collector")
    sender=SubRoutine("Sender")
    
    print "Enter Main routine"
    mainloop.run()
    
    collector.stop()
    sender.stop()
    
    print("Exit Main routine")


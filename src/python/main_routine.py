import sys
import os
import signal
import time
import subprocess

import urllib
import httplib

import json

import dbus
from dbus import service
from dbus.mainloop.glib import DBusGMainLoop
import gobject

CHECK_CONFIG_INTERVAL=300 #in seconds
CONFIG_SERVER="kaiwenmap.cn"
CONFIG_URL="/setting/%s"

device_id=None

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
        out_signature="s"
    )
    def GetDeviceId(self):
        if device_id is None:
            read_device_id()
        return device_id
    
    @dbus.service.method(
        dbus_interface="cn.kaiwenmap.airsniffer.pcDuino.Main",
        in_signature="",
        out_signature=""
    )
    def Stop(self):
        ctrl_brk_handler(None,None)


class SubRoutine:
    def __init__(self,name,silence=False):
        self.name=name
        self.obj=None
        self.proc=None
        self.silence=silence
        
        self.start()
    
    def start(self):
        argv=[]
        argv.append("python")
        argv.append(self.name.lower()+"_routine.py")
        argv.append("-i")
        
        out=None
        if self.silence:
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
        if (self.proc is not None) and (not self.proc.poll()):
            if self.obj is not None:
                self.obj.Stop(dbus_interface="cn.kaiwenmap.airsniffer.pcDuino."+self.name)
            else:
                self.proc.terminate()
            self.proc.wait()
        
        self.proc=None
        self.obj=None
            

def read_device_id():
    global device_id
    
    try:
        f=open("device.id","r");
    except IOError as e:
        sys.stderr.write(
            "Error reading device.id!\n"+
            "Main routine exit!\n"+
            str(e)+"\n"
        )
        sys.exit(1)
    
    device_id=f.readline().strip()
    f.close()

def ctrl_brk_handler(signum,frame):
    signal.setitimer(signal.ITIMER_REAL,0,0)
    mainloop.quit()

def timer_handler(signum,frame):
    print("Check for config")

def check_config():
    conn=httplib.HTTPConnection(CONFIG_SERVER)
    conn.request("GET",CONFIG_URL%device_id)
    resp=conn.getresponse()
    conn.close()
    
    if resp.status!=200:
        return
    
    config=json.loads(resp.read())
    action=config.get("action","nothing")
    data=config.get("data",{})
    
    if action=="reboot":
        #TODO: reboot
        pass
    elif action=="update":
        #TODO: update
        pass
    elif action=="script":
        if "script" in data:
            script=data["script"]
            #TODO: run script
        else:
            return
    else:
        return


if __name__=="__main__":
    read_device_id()
    print(
        "+----------------------------------+\n"+
        "|Device Id:\t"+device_id+"\t           |\n"+
        "+----------------------------------+"
    )
    
    signal.signal(signal.SIGINT,ctrl_brk_handler)
    
    DBusGMainLoop(set_as_default=True)
    bus=dbus.SessionBus()
    name=dbus.service.BusName("cn.kaiwenmap.airsniffer.pcDuino.Main",bus)
    mainloop=gobject.MainLoop()
    
    main_obj=Main("/cn/kaiwenmap/airsniffer/pcDuino/Main")
    
    collector=SubRoutine("Collector")
    sender=SubRoutine("Sender")
    
    signal.signal(signal.SIGALRM,timer_handler)
    signal.setitimer(signal.ITIMER_REAL,CHECK_CONFIG_INTERVAL,CHECK_CONFIG_INTERVAL)
    
    print("Enter Main routine")
    mainloop.run()
    
    collector.stop()
    sender.stop()
    
    print("Exit Main routine")


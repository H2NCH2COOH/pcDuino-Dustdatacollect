import sys
import subprocess
import signal
import time

import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import gobject

wifi_set_up_helper_obj=None

mainloop=None

class WiFiSetUpHelper(dbus.service.Object):
    def __init__(self,obj_path):
        dbus.service.Object.__init__(self,dbus.SessionBus(),obj_path)
    
    @dbus.service.method(
        dbus_interface="cn.kaiwenmap.airsniffer.pcDuino.WiFiSetUpHelper",
        in_signature="",
        out_signature=""
    )
    def Stop(self):
        ctrl_brk_handler(None,None)


def ctrl_brk_handler(signum,frame):
    signal.setitimer(signal.ITIMER_REAL,0,0)
    mainloop.quit()


if __name__=="__main__":
    if len(sys.argv)>1:
        arg=sys.argv[1].lower()
    else:
        arg=""
    
    if arg=="-i" or arg=="--ignore-sigint":
        signal.signal(signal.SIGINT,signal.SIG_IGN)
    else:
        signal.signal(signal.SIGINT,ctrl_brk_handler)
    
    DBusGMainLoop(set_as_default=True)
    bus=dbus.SessionBus()
    name=dbus.service.BusName("cn.kaiwenmap.airsniffer.pcDuino.WiFiSetUpHelper",bus)
    mainloop=gobject.MainLoop()
    
    wifi_set_up_helper_obj=WiFiSetUpHelper("/cn/kaiwenmap/airsniffer/pcDuino/WiFiSetUpHelper")
    
    service=subprocess.Popen(["sudo","python","wifi_set_up_service.py"])
    
    print("Enter WiFiSetUpHelper routine")
    mainloop.run()
    
    service.send_signal(signal.SIGINT)
    service.wait()
    print("Exit WiFiSetUpHelper routine")


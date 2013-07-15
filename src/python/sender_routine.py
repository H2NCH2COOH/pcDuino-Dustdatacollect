import sys
import signal
import time

import httplib

import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import gobject

SENDING_INTERVAL=300 #in seconds

newest_data=None

coeff_mult=1.0
coeff_add=0.0

feed_id="393295424"
channel_id="test2"
xapikey="1K23Oupn3VhdrkY1CqpZ7IkBpTpHLCiqAN6ZcTsSC7NIXSBs"

sender_obj=None

mainloop=None

class Sender(dbus.service.Object):
    def __init__(self,obj_path):
        dbus.service.Object.__init__(self,dbus.SessionBus(),obj_path)
    
    @dbus.service.method(
        dbus_interface="cn.kaiwenmap.airsniffer.pcDuino.Sender",
        in_signature="",
        out_signature=""
    )
    def SendNow(self):
        signal.setitimer(signal.ITIMER_REAL,1,SENDING_INTERVAL)
    
    @dbus.service.method(
        dbus_interface="cn.kaiwenmap.airsniffer.pcDuino.Sender",
        in_signature="",
        out_signature=""
    )
    def Stop(self):
        ctrl_brk_handler(None,None)
    
    @dbus.service.method(
        dbus_interface="cn.kaiwenmap.airsniffer.pcDuino.Sender",
        in_signature="dd",
        out_signature=""
    )
    def Calibrate(self,mult_by,add_by):
        coeff_mult*=mult_by
        coeff_add*=mult_by
        coeff_add+=add_by

def send_data(data):
    data*=coeff_mult
    data+=coeff_add
    
    try:
        url="/v2/feeds/%s/datastreams/%s"%(feed_id,channel_id)
        body="{\"id\":\"%s\",\"current_value\":\"%f\"}"%(channel_id,data)
        header={"X-ApiKey":xapikey}
        
        while True:
            conn=httplib.HTTPConnection("api.xively.com")
            conn.request("PUT",url,body,header)
            resp=conn.getresponse()
            conn.close()
            if resp.status==200:
                break
    except Exception as e:
        sys.stderr.write(
            "-------------------------------------------------------\n"+
            "Exception in sending data:\n "+
            str(e)+"\n"+
            "-------------------------------------------------------\n"
        )

def timer_handler(signum,frame):
    global newest_data
    
    if not newest_data:
        return
    
    print "Sending Data: %f"%newest_data
    send_data(newest_data)

def ctrl_brk_handler(signum,frame):
    signal.setitimer(signal.ITIMER_REAL,0,0)
    mainloop.quit()

def dbus_signal_handler(data,time):
    global newest_data
    
    newest_data=data
    print "New data coming in: %f%% at %s"%(data,time)


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
    name=dbus.service.BusName("cn.kaiwenmap.airsniffer.pcDuino.Sender",bus)
    mainloop=gobject.MainLoop()
    
    sender_obj=Sender("/cn/kaiwenmap/airsniffer/pcDuino/Sender")
    
    bus.add_signal_receiver(
        handler_function=dbus_signal_handler,
        signal_name="NewDustData",
        dbus_interface="cn.kaiwenmap.airsniffer.pcDuino.Collector"
    )
    
    signal.signal(signal.SIGALRM,timer_handler)
    signal.setitimer(signal.ITIMER_REAL,SENDING_INTERVAL,SENDING_INTERVAL)
    
    print "Enter Sender routine"
    mainloop.run()
    print("Exit Sender routine")


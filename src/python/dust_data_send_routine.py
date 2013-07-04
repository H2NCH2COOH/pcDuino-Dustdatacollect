import sys
import signal
import time

import urllib
import urllib2

import dbus
from dbus.mainloop.glib import DBusGMainLoop
import gobject

SENDING_INTERVAL=300 #in seconds

newest_data=None

feed_id="393295424"
channel_id="test2"
xapikey="1K23Oupn3VhdrkY1CqpZ7IkBpTpHLCiqAN6ZcTsSC7NIXSBs"

def send_data(data):
    try:
        url="http://api.xively.com/v2/feeds/%s/datastreams/%s"%(feed_id,channel_id)
        data="{\"id\":\"%s\",\"current_value\":\"%f\"}"%(channel_id,data)
        
        req=urllib2.Request(url,data)
        req.add_header("X-ApiKey",xapikey)
        req.get_method=lambda: 'PUT'
        
        result=urllib2.urlopen(req)
        
    except Exception as e:
        print("Exception! "+str(e))

def timer_handler(signum,frame):
    global newest_data
    
    if not newest_data:
        return
    
    send_data(newest_data)

def ctrl_brk_handler(signum,frame):
    signal.setitimer(signal.ITIMER_REAL,0,0)
    print("\nExit dust data send routine")
    sys.exit(0)

def dbus_signal_handler(data,time):
    global newest_data
    
    newest_data=data
    print "New data coming in: %f%% at %s"%(data,time)


if __name__=="__main__":
    signal.signal(signal.SIGINT,ctrl_brk_handler)
    
    DBusGMainLoop(set_as_default=True)
    bus=dbus.SessionBus()
    bus.add_signal_receiver(
        handler_function=dbus_signal_handler,
        signal_name="NewDustData",
        dbus_interface="cn.kaiwenmap.airsniffer.pcDuino.Collector"
    )
    
    signal.signal(signal.SIGALRM,timer_handler)
    signal.setitimer(signal.ITIMER_REAL,SENDING_INTERVAL,SENDING_INTERVAL)
    
    gobject.MainLoop().run()

import sys
import signal
import time

import urllib
import urllib2

import dbus
from dbus.mainloop.glib import DBusGMainLoop

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


if __name__=="__main__":
    signal.signal(signal.SIGINT,ctrl_brk_handler)
    
    DBusGMainLoop(set_as_default=True)
    
    signal.signal(signal.SIGALRM,timer_handler)
    signal.setitimer(signal.ITIMER_REAL,300,300)
    
    bus=dbus.SessionBus()
    collector_obj=bus.get_object(
        "cn.kaiwenmap.airsniffer.pcDuino.Collector",
        "/cn/kaiwenmap/airsniffer/pcDuino/Collector"
    )
    collector_iface=dbus.Interface(
        collector_obj,
        "cn.kaiwenmap.airsniffer.pcDuino.Collector"
    )
    collector_iface.connect_to_signal(
        signal_name="NewDustData",
        handler_function=dbus_signal_handler,
        dbus_interface="cn.kaiwenmap.airsniffer.pcDuino.Collector"
    )
    

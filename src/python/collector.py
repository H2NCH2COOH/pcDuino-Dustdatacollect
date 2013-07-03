class Collector(dbus.service.Object):
    def __init__(self,obj_path):
        dbus.service.Object.__init__(self,dbus.SessionBus(),obj_path)
    
    @dbus.service.signal(
        dbus_interface="cn.kaiwenmap.airsniffer.pcDuino.Collector",
        signature="ds"
    )
    def NewDustData(self,data,time):
        "NOP"
    
    
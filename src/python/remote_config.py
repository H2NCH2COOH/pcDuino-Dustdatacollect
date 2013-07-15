import httplib

import json

from main_routine import device_id
from main_routine import sub_routines
from main_routine import SubRoutine

import update

CONFIG_SERVER="kaiwenmap.cn"
CONFIG_URL="/setting/%s"

def check():
    conn=httplib.HTTPConnection(CONFIG_SERVER)
    conn.request("GET",CONFIG_URL%device_id)
    resp=conn.getresponse()
    conn.close()
    
    if resp.status!=200:
        return
    
    config=json.loads(resp.read())
    action=config.get("action","nothing").lower()
    data=config.get("data",{})
    
    do_config(action,data)

def do_config(action,data):
    #=========================================================================#
    if action=="reboot":
        for name in sub_routines:
            sub_routines[name].stop()
            sub_routines[name].start()
        #TODO: do anything else
    #=========================================================================#
    elif action=="update":
        update.update()
    #=========================================================================#
    elif action=="script":
        if "script" in data:
            script=data["script"]
            with open("temp_script","w") as tsf:
                tsf.write(script)
                subprocess.call(["chmod","+x","temp_script"])
                subprocess.call(["temp_script"])
        else:
            return
    #=========================================================================#
    elif action=="calibrate":
        if "Sender" in sub_routines:
            mult=data.get("mult_by",1.0)
            add=data.get("add_by",0.0)
            sub_routines["Sender"].getInterface().Calibrate(mult,add)
    #=========================================================================#
    else:
        return

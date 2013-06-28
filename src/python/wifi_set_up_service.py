import socket
import urllib
import signal
import sys

from connect_to_wifi import connect_to_wifi

HOST=""
PORT=80

PAGE='''
<html>
    <head>
        <title>Set up WiFi connection</title>
    </head>
    <body>
        <h3>Set up WiFi connection</h3>
        <p>Only works with WiFi with WPA-PSK</p>
        
        <form name="setup" action="/" method="post">
            SSID:<br />
            <input type="text" name="ssid" /><br />
            Key:<br />
            <input type="text" name="key" /><br />
            <input type="submit" value="Set up" />
        </form>
    </body>
</html>
'''

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind((HOST,PORT))
s.listen(1)

def ctrl_break_handler(signum,frame):
    global s
    s.close()
    sys.exit(0)
    
signal.signal(signal.SIGINT,ctrl_break_handler)

ssid=None
key=None

while True:
    conn,addr=s.accept()
    try:
        data=conn.recv(2048)
        if data:
            if data.startswith("GET / HTTP"):
                conn.send(PAGE)
            elif data.startswith("POST / HTTP"):
                info=data.split("\r\n\r\n")[1]
                info=info.strip()
                for i in info.split('&'):
                    if i.startswith("ssid="):
                        ssid=i[5:]
                    elif i.startswith("key="):
                        key=i[4:]
                conn.send(
                    '''
                    <html>
                        <h1>WiFi connection set</h1>
                        Please wait for the device to connect to the wifi
                    </html>
                    '''
                )
                
                ssid=urllib.unquote(ssid)
                key=urllib.unquote(key)
                print "Connect to WiFi with SSID: %s, and key: %s"%(ssid,key)
                connect_to_wifi(ssid,key)
    except Exception as e:
        conn.close()


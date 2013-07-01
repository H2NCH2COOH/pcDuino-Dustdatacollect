import sys

HIGH=1
LOW =0

OUTPUT=1
INPUT =0

GPIO_MODE_FILE_FORMAT="/sys/devices/virtual/misc/gpio/mode/gpio%d"
GPIO_PIN_FILE_FORMAT="/sys/devices/virtual/misc/gpio/pin/gpio%d"

def set_gpio_mode(pin,mode):
    name=GPIO_MODE_FILE_FORMAT%pin
    try:
        f_mode=open(name,"w")
    except IOError as e:
        sys.stderr.write(str(e)+"\n")
    
    f_mode.write(str(mode))
    
    f_mode.flush()
    f_mode.close()

def get_gpio_pin(pin):
    name=GPIO_PIN_FILE_FORMAT%pin
    try:
        f_pin=open(name,"r");
    except IOError as e:
        sys.stderr.write(str(e)+"\n")
        return -1
    
    c=f_pin.read(1)
    
    f_pin.close()
    
    if(c=="0"):
        return LOW;
    elif(c=="1"):
        return HIGH;
    else:
        return -1;

def set_gpio_pin(pin,level):
    name=GPIO_PIN_FILE_FORMAT%pin
    try:
        f_pin=open(name,"w")
    except IOError as e:
        sys.stderr.write(str(e)+"\n")
    
    f_pin.write(str(level))
    
    f_pin.flush();
    f_pin.close();

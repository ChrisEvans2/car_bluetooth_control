import pydbus
import os

# call bluetooth detection function
bus = pydbus.SystemBus()
adapter = bus.get('org.bluez', '/org/bluez/hci0')
mngr = bus.get('org.bluez', '/')
connect = False

# begin to detect the bluetooth whether is connected
while connect == False:
    mngd_objs = mngr.GetManagedObjects()
    for path in mngd_objs:
        con_state = mngd_objs[path].get('org.bluez.Device1', {}).get('Connected', False)
        if con_state:
            addr = mngd_objs[path].get('org.bluez.Device1', {}).get('Address')
            name = mngd_objs[path].get('org.bluez.Device1', {}).get('Name')
            print(f'Device {name} [{addr}] is connected')
            connect = True

# "/home/pi/Desktop/yaogan_test3_15.py" this is the absolute path
# of the python file of game handle control
order = "python3 /home/pi/stick_ctrl/yaogan_test3_17.py"
os.system(order)

import pygame
from control import gpio
import time
import pyaudio
import wave
import pydbus

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
'''
该手柄控制的代码是
右边摇杆前后与旋转
左边遥感左右平移
且包括了所有按键按下print对应按键的功能（请ctrl+f检索 button_list 关键词）
-----2022.10.9 YYJ built on the basis of Actor
'''


# This is a simple class that will help us print to the screen
# It has nothing to do with the joysticks, just outputting the
# information.
class TextPrint:
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 20)

    def prints(self, screen, textString):
        textBitmap = self.font.render(textString, True, BLACK)
        screen.blit(textBitmap, [self.x, self.y])
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15

    def indent(self):
        self.x += 10

    def unindent(self):
        self.x -= 10




class Car:
    def __init__(self):
        self.font = pygame.font.Font(None, 20)
        self.m = gpio.Mecanum_wheel()
        self.speed = 0

    def prints(self, screen, textString, position):
        textBitmap = self.font.render(textString, True, BLACK)
        screen.blit(textBitmap, position)

    # about the argument: angle use arg[0];  forward speed use arg[5],it corresponds to the left shoulder key
    #                     backward speed use arg[2],it corresponds to the right shoulder key;  the translate speed use arg[3]         
           
    def move_rigid(self, arg):
        speed = round(-(arg[4]) * 2000)
        angle = round(arg[3] * 75)
        translation = round(arg[0] * 1300)
        
        if abs(speed) < 20 and abs(angle) < 5 and abs(translation) < 5:
            self.prints(screen, "The car still stop",[10,490])
        if speed > 10:
            self.prints(screen,"the car is running forward at {} speed".format(speed),[10,500])
        if speed < 10:
            self.prints(screen, "the car is running back at {} speed".format(speed), [10,500])
            
        if angle < 5:
            self.prints(screen,"the turning left angle is {}".format(angle), [10,510])
        if angle > 5:
            self.prints(screen,"the turning right angle is {}".format(angle), [10,510])
        if translation > 0:
            self.prints(screen,"the translation right speed is {}".format(translation),[10,520])
        if translation < 0:
            self.prints(screen,"the translation left speed is {}".format(translation),[10,520])
        if speed < 0:
            self.m.car_contr(speed,translation,angle)
        else:
            self.m.car_contr(speed,translation,-angle)

def music(wf):
    CHUNK = 1024
    # read the voice file from the directory
    # read data
    data = wf.readframes(CHUNK)
    # create player
    p = pyaudio.PyAudio()

    # get various parameters of voice file
    FORMAT = p.get_format_from_width(wf.getsampwidth())
    CHANNELS = wf.getnchannels()
    RATE = wf.getframerate()
    
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    frames_per_buffer=CHUNK,
                    output=True)
    # play stream (3) read the audio data into the audio stream accroding to the block of 1024 and play it
    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(CHUNK)


while True:
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
    # time.sleep(7)
    print("connected")
    pygame.init()
    # Loop until the user clicks the close button.
    done = False
    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    # Get ready to print
    textPrint = TextPrint()


    CHUNK = 1024
    # read the voice file from the directory
    wf = wave.open('/home/pi/stick_ctrl/car_sound.wav', 'rb')
    relex_wf = wave.open('/home/pi/stick_ctrl/relex.wav', 'rb')
    compe_wf = wave.open('/home/pi/stick_ctrl/competitive.wav', 'rb')
    # read data
    data = wf.readframes(CHUNK)
    # create player
    p = pyaudio.PyAudio()

    # -------- Main Program Loop -----------
    while done == False:
        # EVENT PROCESSING STEP
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                done = True  # Flag that we are done so we exit this loop
            # Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
            if event.type == pygame.JOYBUTTONDOWN:
                print("Joystick button pressed.")
            if event.type == pygame.JOYBUTTONUP:
                print("Joystick button   released.")
        axis_list1 = []
        button_list1 = []
        car = Car()
        relex = False
        FORMAT = p.get_format_from_width(wf.getsampwidth())
        CHANNELS = wf.getnchannels()
        RATE = wf.getframerate()
        joystick_count = pygame.joystick.get_count()
        for i in range(joystick_count):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            name = joystick.get_name()
            axes = joystick.get_numaxes()
            for i in range(axes):  
                axis = joystick.get_axis(i)
                axis_list1.append(axis)
            if axis_list1[2] == -1 and axis_list1[5] == -1:
                # open audio stream， output=True indicates audio output
                stream = p.open(format=FORMAT,

                                channels=CHANNELS,
                                rate=RATE,
                                frames_per_buffer=CHUNK,
                                output=True)
                # play stream (3) read the audio data into the audio stream accroding to the block of 1024 and play it
                while len(data) > 0:
                    stream.write(data)
                    data = wf.readframes(CHUNK)
                
                while done == False:
                    times = False
                    size = [500, 700]
                    screen = pygame.display.set_mode(size)

                    pygame.display.set_caption("My Game")
                    for event in pygame.event.get():  # User did something
                        if event.type == pygame.QUIT:  # If user clicked close
                            done = True
                    #####################################
                    screen.fill(WHITE)
                    textPrint.reset()
                    axis_list = []
                    button_list = []
                    for i in range(joystick_count):
                        #joystick = pygame.joystick.Joystick(i)
                        #joystick.init()
                        textPrint.prints(screen, "Number of joysticks: {}".format(joystick_count))
                        textPrint.prints(screen, "Joystick {}".format(i))
                        textPrint.indent()
                        # Get the name from the OS for the controller/joystick
                        name = joystick.get_name()
                        textPrint.prints(screen, "Joystick name: {}".format(name))

                        # Usually axis run in pairs, up/down for one, and left/right for
                        # the other.
                        axes = joystick.get_numaxes()
                        textPrint.prints(screen, "Number of axes: {}".format(axes))
                        textPrint.indent()
                        buttons = joystick.get_numbuttons()
                        for i in range(buttons):        # 遍历按键 
                            button = joystick.get_button(i)
                            textPrint.prints(screen, "Button {:>2} value: {}".format(i, button)) # pygame窗口显示按键
                            button_list.append(button)     # 将前面4个按键加入列表
                        textPrint.unindent()
                        
                        if button_list[0]:  #button A
                            print("A")
                        elif button_list[1]:  #buttonB
                            print("B")
                        elif button_list[2]:  #buttonX
                            print("X")
                        elif button_list[3]:  #buttonY
                            print("Y")
                        elif button_list[4]:  #buttonLB
                            print("LB")
                        elif button_list[5]:  #buttonRB
                            print("RB")
                        elif button_list[6]:  #buttonBack
                            print("Back")
                        elif button_list[7]:  #buttonStart
                            print("Start")
                        elif button_list[8]:  #buttonLS
                            print("LS")
                        elif button_list[9]:  #buttonRS
                            print("RS")
                            
                        for i in range(axes):  # as the same as the above
                            axis = joystick.get_axis(i)
                            textPrint.prints(screen, "Axis {} value: {:>6.3f}".format(i,axis))
                            axis_list.append(axis)
                        textPrint.unindent()
                        car.move_rigid(axis_list)
                    pygame.display.flip()
                    clock.tick(20)
            buttons = joystick.get_numbuttons()
    pygame.quit()
    time.sleep(10)

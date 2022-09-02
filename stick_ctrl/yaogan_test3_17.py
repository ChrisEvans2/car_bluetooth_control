import pygame
from control import gpio
import time
import pyaudio
import wave
import pydbus

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)




# This is a simple class that will help us print to the screen
# It has nothing to do with the joysticks, just outputting the
# information.
class TextPrint:
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 20)

    def print(self, screen, textString):
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
    def move_inertia(self,arg):
        max_speed = 2000
        forward_a = round((arg[5]+1) * 110)
        back_speed = round(-(arg[2]+1) * 90)
        accelerate = forward_a + back_speed
        stick_a = 70
        mini_a = 5
        angle = round(arg[0] * 75) #100/12
        translation = round(arg[3] * 1300)
        self.speed += accelerate
        if accelerate == 0:
            if self.speed > 0:
                if self.speed >= 50:
                    self.speed -= stick_a
                else:
                    self.speed -= mini_a
            else:
                if self.speed <= -50:
                    self.speed += stick_a
                else:
                    self.speed += mini_a
        if self.speed >= max_speed:
            self.speed = max_speed
        if self.speed <= -max_speed:
            self.speed = -max_speed
        if -20 <= self.speed <= 20:
            self.speed = 0
        
        if abs(self.speed) < 20 and abs(angle) < 5 and abs(translation) < 5:
            self.prints(screen, "The car still stop",[10,490])
        if self.speed > 10:
            self.prints(screen,"the car is running forward at {} speed".format(self.speed),[10,500])
        if self.speed < 10:
            self.prints(screen, "the car is running back at {} speed".format(self.speed), [10,500])
        if angle < 5:
            self.prints(screen,"the turning left angle is {}".format(angle), [10,510])
        if angle > 5:
            self.prints(screen,"the turning right angle is {}".format(angle), [10,510])
        if translation > 0:
            self.prints(screen,"the translation right speed is {}".format(translation),[10,520])
        if translation < 0:
            self.prints(screen,"the translation left speed is {}".format(translation),[10,520])
        if self.speed >= 0:
            self.m.car_contr(self.speed,translation,-angle)
        else :
            self.m.car_contr(self.speed,translation,angle)
    def move_rigid(self, arg):
        forward_speed = round((arg[5]+1) * 1000)
        back_speed = round(-(arg[2]+1) * 1000)
        speed = forward_speed + back_speed
        angle = round(arg[0] * 75)
        translation = round(arg[3] * 1300)
        
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

# def music(wf):
#     CHUNK = 1024
#     # read the voice file from the directory
#     # read data
#     data = wf.readframes(CHUNK)
#     # create player
#     p = pyaudio.PyAudio()
# 
#     # get various parameters of voice file
#     FORMAT = p.get_format_from_width(wf.getsampwidth())
#     CHANNELS = wf.getnchannels()
#     RATE = wf.getframerate()
#     
#     stream = p.open(format=FORMAT,
#                     channels=CHANNELS,
#                     rate=RATE,
#                     frames_per_buffer=CHUNK,
#                     output=True)
#     # play stream (3) read the audio data into the audio stream accroding to the block of 1024 and play it
#     while len(data) > 0:
#         stream.write(data)
#         data = wf.readframes(CHUNK)


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
    time.sleep(7)
    print("connected")
    pygame.init()
    # pygame.mixer.init()
    # car_sound = pygame.mixer.Sound("/home/pi/stick_ctrl/car_sound.wav")

    # Set the width and height of the screen [width,height]
    

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

        # DRAWING STEP
        # First, clear the screen to white. Don't put other drawing commands
        # above this, or they will be erased with this command.
#         screen.fill(WHITE)
#         textPrint.reset()
        #################################
        # use to delive the arguement to the car control function
        axis_list1 = []
        button_list1 = []
        car = Car()
        relex = False
        
        # get various parameters of voice file
        FORMAT = p.get_format_from_width(wf.getsampwidth())
        CHANNELS = wf.getnchannels()
        RATE = wf.getframerate()

        
        ##################################
        # Get count of joysticks
        joystick_count = pygame.joystick.get_count()

#         textPrint.print(screen, "Number of joysticks: {}".format(joystick_count))
#         textPrint.indent()

        # For each joystick:
        for i in range(joystick_count):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()

#             textPrint.print(screen, "Joystick {}".format(i))
#             textPrint.indent()

            # Get the name from the OS for the controller/joystick
            name = joystick.get_name()
#             textPrint.print(screen, "Joystick name: {}".format(name))

            # Usually axis run in pairs, up/down for one, and left/right for
            # the other.
            axes = joystick.get_numaxes()
#             textPrint.print(screen, "Number of axes: {}".format(axes))
#             textPrint.indent()

            # the handel has 6 axes
            # in this "THUNDEROBOT" game handle
            # arg0: left rocker X-axis;  arg1: left rocker Y-axis;    arg2: left shoulder key
            # arg3: right rocker X-axis;  arg4: right rocker Y-axis;    arg2: right shoulder key
            for i in range(axes):  
                axis = joystick.get_axis(i)
#                 textPrint.print(screen, "Axis {} value: {:>6.3f}".format(i,axis))
                axis_list1.append(axis)
#             textPrint.unindent()
            # print(axis_list1)
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
                        textPrint.print(screen, "Number of joysticks: {}".format(joystick_count))
                        textPrint.print(screen, "Joystick {}".format(i))
                        textPrint.indent()
                        # Get the name from the OS for the controller/joystick
                        name = joystick.get_name()
                        textPrint.print(screen, "Joystick name: {}".format(name))

                        # Usually axis run in pairs, up/down for one, and left/right for
                        # the other.
                        axes = joystick.get_numaxes()
                        textPrint.print(screen, "Number of axes: {}".format(axes))
                        textPrint.indent()
                        buttons = joystick.get_numbuttons()
                        for i in range(buttons):
                            button = joystick.get_button(i)
#                             textPrint.print(screen, "Button {:>2} value: {}".format(i, button))
                            button_list.append(button)
#                         textPrint.unindent()
                        #print("no\nnono")
                        for i in range(axes):  # as the same as the above
                            axis = joystick.get_axis(i)
                            textPrint.print(screen, "Axis {} value: {:>6.3f}".format(i,axis))
                            axis_list.append(axis)
                        textPrint.unindent()
                        car.move_rigid(axis_list)
                        #print(axis_list)
                        
#                         textPrint.print(screen, "Number of buttons: {}".format(buttons))
#                         textPrint.indent()
                        
                        
                    pygame.display.flip()
                    clock.tick(20)
            buttons = joystick.get_numbuttons()
            # textPrint.print(screen, "Number of buttons: {}".format(buttons))
            # textPrint.indent()
            #
            for i in range(buttons):
                button = joystick.get_button(i)
                button_list1.append(button)
            if button_list1[1]:
                done = True
            #     textPrint.print(screen, "Button {:>2} value: {}".format(i, button))
            # textPrint.unindent()
            #
            # # Hat switch. All or nothing for direction, not like joysticks.
            # # Value comes back in an array.
            # hats = joystick.get_numhats()
            # textPrint.print(screen, "Number of hats: {}".format(hats))
            # textPrint.indent()
            #
            # for i in range(hats):
            #     hat = joystick.get_hat(i)
            #     textPrint.print(screen, "Hat {} value: {}".format(i, str(hat)))
            # textPrint.unindent()
            #
            # textPrint.unindent()

        # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT

        # Go ahead and update the screen with what we've drawn.
#         pygame.display.flip()
# 
#         # Limit to 20 frames per second
#         clock.tick(20)
    
    # Close the window and quit.
    # If you forget this line, the program will 'hang'
    # on exit if running from IDLE.
    pygame.quit()
    time.sleep(10)

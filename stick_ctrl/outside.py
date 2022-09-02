import pygame

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

    def printf(self, screen, textString):
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
        
        
        
pygame.init()

# Set the width and height of the screen [width,height]
size = [500, 700]
screen = pygame.display.set_mode(size)

pygame.display.set_caption("My Game")

# Loop until the user clicks the close button.

flag = False
# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# Initialize the joysticks
pygame.joystick.init()

# Get ready to print
textPrint = TextPrint()
# read whether the handle is connected
while flag == False:
    for event in pygame.event.get():  # User did something
        if event.type == pygame.QUIT:  # If user clicked close
            flag = True  # Flag that we are done so we exit this loop
    count = pygame.joystick.get_count()
    screen.fill(WHITE)
    textPrint.reset()
    textPrint.printf(screen,"number of joystick is {},you need to connect".format(count))
    textPrint.indent()
    pygame.display.flip()
    clock.tick(20)
    if count == 1:
        flag = True
print("ok")
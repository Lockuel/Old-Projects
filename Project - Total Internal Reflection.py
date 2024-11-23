# Importing required modules then intialising pygame
import sys, pygame, pygame.freetype, math
pygame.init()

# Defining the size of the screen and some useful variables
size = width, height = 1080, 720
speed = [1, 1]
black = 0, 0, 0
bluish = 140, 150, 200
grey = 100, 100, 100
white = 255, 255, 255
n1 = 1.0003
n2 = 1.5
criticalAngle = math.asin(n1 / n2)
initAngle = 30
gap = 150
wheight = [height / 2 - gap, height / 2 + gap]

# Creating the base screen to display on
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Total Internal Reflection Tool")

# Class creates a tracer object with no base return.
# Works by sending a tracer bouncing along the initial angle within the bounds
# of the medium, drawing lines at each collision and working out if a new tracer should be generated.
# If the angle is below the critical angle and is hitting a bound of the material, creates new
# tracer with refracted angle and a proportion of the brightness, if not simply bounces.
# Terminates upon hitting edge of screen or end of material.
class Tracer:
    # Makes the tracer depending on input
    def __init__(self, x, y, angle, top, bottom, velocity, brightness):
        self.lastPos = (x, y)
        self.nextPos = (x, y)
        self.x = x
        self.y = y
        # python.math uses radians, which are uncomfortable for most, so imput and display is in
        # degrees, thus a few conversions are needed throughout the code
        self.angle = (angle) * math.pi / 180 
        self.bounds = (top, bottom)
        self.velocity = velocity
        self.brightness = brightness

    # Bunch of getters and one setter for the core variables  
    def get_angle(self):
        return self.angle
    
    def set_angle(self, angle):
        self.angle = angle

    def get_velocity(self):
        return self.velocity

    def get_brightness(self):
        return self.brightness
    
    def trace(self):
        finish = False
        # Loops movement until hitting the edge of screen, or leaving the x bounds of the material
        while self.x < width - (width / 4) and finish == False:
            # Moves x at constant, moves either up or down
            self.x = self.x + math.sin(self.angle) 
            self.y = self.y + math.cos(self.angle) * self.velocity

            # The same, but checks for y collision. For some reason repeating the code like this really improved performace
            while self.y >= self.bounds[0] and self.y <= self.bounds[1] and self.x < width - (width / 4):
                self.x = self.x + (math.sin(self.angle))
                self.y = self.y + (math.cos(self.angle) * self.velocity)

            # Checks if at edge of screen. If not, draws line and prepares to make another tracer.
            if self.bounds != (0, height):
                self.lastPos = self.nextPos
                self.nextPos = (self.x, self.y)
                pygame.draw.line(screen, (self.brightness , self.brightness, self.brightness), self.lastPos, self.nextPos, width = 4)

                # Checks if it should refract. If so, calculates new angle, and brightness for the new tracer then creates it.
                if self.angle < critAngle.get_value() / 180 * math.pi:
                    newAngle = math.asin(math.sin(self.angle) * glassRI.get_value() / n1)

                    # Pygame doesn't really listen to alpha values, so shifted colour closer to background as brightness dropped as a work around
                    edgeBrightness = self.brightness - ((self.angle / (critAngle.get_value() / 180 * math.pi)) * (self.brightness - 100))
                    edge = Tracer(self.x, self.y , newAngle * 180 / math.pi, 0, height, self.velocity, edgeBrightness)

                    # Saftey net for float values causing issues
                    if self.brightness - 100 > 0:
                        self.brightness = self.brightness - ((1 - (self.angle / (critAngle.get_value() / 180 * math.pi))) * (self.brightness - 100))
                    else:
                        self.brightness = 100

                    # Calls refracted beam to trace.
                    edge.trace()

                
            else:
                # If at screen edge, draws new line like normal, then maps how far off grey the beam is onto blue for its new colour
                self.lastPos = self.nextPos
                self.nextPos = (self.x, self.y)
                newBrightness = 100 / self.brightness
                pygame.draw.line(screen, ((255 - (newBrightness * (255 - bluish[0]))), (255 - (newBrightness * (255 - bluish[1]))), (255 - (newBrightness * (255 - bluish[2])))), self.lastPos, self.nextPos, width = 4)
                # Terminates all loops.
                finish = True
                break

            # Reflects off surface
            self.velocity = self.velocity * -1

# Class creates a button object with no base return.
# Displays the name of a variable, and it's current value on a two tone background
# lights up when either side is highlighted unless the colour is light grey which does nothing.
# Decreases value if left side is clicked, increases if right side is clicked
class Controls:
    # Initialises variables, a surface for the button, a freetype font, and collision boxes for the left and right side
    def __init__(self, name, x, y, variable, leftCol, rightCol):
        self.name = name
        self.x = x
        self.y = y

        self.var = variable
        self.leftCol = leftCol
        self.rightCol = rightCol

        self.left = pygame.Rect(x, y, 100, 50)
        self.right = pygame.Rect(x + 100, y, 100, 50)

        self.buttonText = pygame.freetype.SysFont("ariel", 20)
        
        self.button = pygame.surface.Surface((200, 50))

    # Getter for the variable stored
    def get_value(self):
        return self.var

    # Modifies the variable by a value)
    def update(self, value):
        self.var = round(self.var + value, 2)

    # Sets the variable to a value    
    def extUpdate (self, value):
        self.var = value

    # Checks if the mouse collides with the left and right side, lights them up if it does
    def mouseover (self, point):
        if self.left.collidepoint(point) and self.leftCol != (200, 200, 200):
            self.leftCol = (255, 60, 50)
        elif self.leftCol != (200, 200, 200):
            self.leftCol = (200, 60, 50)
        if self.right.collidepoint(point) and self.rightCol != (200, 200, 200):
            self.rightCol = (60, 255, 50)
        elif self.rightCol != (200, 200, 200):
            self.rightCol = (60, 200, 50)

    # Renders the button    
    def draw(self):
        # Draws the background and blits it to the main screen
        pygame.draw.rect(self.button, self.leftCol, left)
        pygame.draw.rect(self.button, self.rightCol, right)
        pygame.draw.rect(self.button, (30, 30, 30), around, width = 4) 
        screen.blit(self.button, (self.x,self.y))

        # Aligns the text to the box (middle x, offset y), then renders name and variable 
        offset = self.buttonText.get_rect(self.name)
        self.buttonText.render_to(screen, (self.x + (200 - offset.width) / 2, self.y + 10), self.name, (50, 50, 50))
        offset = self.buttonText.get_rect(str(self.var))
        self.buttonText.render_to(screen, (self.x + (200 - offset.width) / 2, self.y + 30), str(self.var), (50,50,50))
        

# Creation of needed Rects for buttons
tube = pygame.Rect(0, wheight[0] , width - width / 4, wheight[1] - wheight[0])
left = pygame.Rect(0, 0 , 100, 50)
right = pygame.Rect(100, 0 , 100, 50)
around = pygame.Rect(0, 0, 200, 50)

# Initialising buttons
initialAngle = Controls("Initial Angle", width - width / 5, 25, initAngle, (200, 60, 50), (60, 200, 50))
glassRI = Controls("Medium RI", width - width / 5, 150, n2, (200, 60, 50), (60, 200, 50))
tubeSize = Controls("Zoom", width - width / 5, 275,  gap, (200, 60, 50), (60, 200, 50))
numbBeams = Controls("Number of Beams", width - width / 5, 400, 1, (200, 60, 50), (60, 200, 50))
refAngle = Controls("Angle of Refraction", width - width / 5, 525,  round(math.asin(math.sin(initAngle * math.pi / 180) * glassRI.get_value() / n1) * 180 / math.pi), (200, 200, 200), (200, 200, 200))
critAngle = Controls("Critical Angle", width - width / 5, 650, round(criticalAngle * 180 / math.pi), (200, 200, 200), (200, 200, 200))

# Putting the buttons into a list for easy looping
buttons = [initialAngle, glassRI, tubeSize, critAngle, refAngle, numbBeams]

while 1:
    # Gets the mouse pointer, then checks if it overlaps with any button.
    point = pygame.mouse.get_pos()
    for event in pygame.event.get():
        # Also allows for quitting out
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # If the mouse is clicked over a button, and it isn't past min/max, updates value approprately
        # Putting this code in the actual button class caused heavy lag, so was kept here
        if event.type == pygame.MOUSEBUTTONDOWN:
            if initialAngle.right.collidepoint(point) and initialAngle.get_value() < 90:
                initialAngle.update(1)
            elif initialAngle.left.collidepoint(point) and initialAngle.get_value() > 1:
                initialAngle.update(-1)
            elif tubeSize.right.collidepoint(point) and tubeSize.get_value() < height / 2 - 10:
                tubeSize.update(10)
            elif tubeSize.left.collidepoint(point) and tubeSize.get_value() > 50:
                tubeSize.update(-10)
            elif glassRI.right.collidepoint(point) and glassRI.get_value() < 2:
                glassRI.update(0.05)
            elif glassRI.left.collidepoint(point) and glassRI.get_value() > 1.1:
                glassRI.update(-0.05)
            elif numbBeams.right.collidepoint(point) and numbBeams.get_value() < 11:
                numbBeams.update(1)
            elif numbBeams.left.collidepoint(point) and numbBeams.get_value() > 1:
                numbBeams.update(-1)

    # Updates critical angle first to prevent math errors            
    critAngle.extUpdate(round(math.asin(n1/glassRI.get_value())* 180 / math.pi, ndigits = 2))

    # Updates display for angle of refraction, both above and below critical angle
    if initialAngle.get_value() < critAngle.get_value():
        refAngle.extUpdate(round(math.asin(math.sin(initialAngle.get_value() * math.pi / 180) * glassRI.get_value() / n1) * 180 / math.pi, 2))
    else:
        refAngle.extUpdate("No refraction")

    # Fill background
    screen.fill(bluish)

    # Update visual bounds for material
    wheight = [height / 2 - tubeSize.get_value(), height / 2 + tubeSize.get_value()]
    tube = pygame.Rect(0, wheight[0] , width - width/4, wheight[1]-wheight[0])
    pygame.draw.rect(screen, grey, tube)

    # Generates beams up to variable, starting from the middle
    modBase = round((tubeSize.get_value() - 10) / 5)
    mod = 0
    count = 1
    pos = height / 2
    # Flips if it is placing above or below each time, increases radius from middle every second loop
    for beam in range(numbBeams.get_value() ):
        if count % 2 != 0:
            pos = (height / 2) + (mod * -1)
        else:
            mod = mod + modBase
            pos = height / 2 + mod
        start = Tracer(0, pos, initialAngle.get_value(), wheight[0], wheight[1], 1, 255)
        start.trace()
        count += 1

    # Loops over buttons to check mouseover for colour shift, then draws them.
    for b in buttons:
        b.mouseover(point)
        b.draw()

    # Finally draws a small rectangle around the medium to clean up 'dim' beams width poking out obviously and finishes rendering
    cleanup = pygame.Rect(0,  wheight[0] - 2, width + 1 - width / 4, wheight[1]-wheight[0] +2)
    pygame.draw.rect(screen,bluish,cleanup, width = 2)
    pygame.display.flip()

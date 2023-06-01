import tkinter as tk
import math
import random

# Set up tkinter window
root = tk.Tk()
root.title("Gravity Simulation")
w, h = 700, 700
canvas = tk.Canvas(root, width=w, height=h, bg='black')
canvas.pack()

# Define the spatial boundaries of the simulation in meters
l, r, b, t = -1e9, 1e9, -1e9, 1e9
rw = r - l
rh = t - b

# Define physical constant in SI units
G = 6.674e-11           # Gravitational constant
m_earth = 5.9726e24     # Mass of the Earth
r_earth = 6.371e6 * 5   # Radius of the Earth (increased for better visualization)
m_moon = 7.342e22       # Mass of the Moon
r_moon = 1.737e6 * 5    # Radius of the Moon (increased for better visualization)
R_moon = 3.84467e8      # Radius of the Moon's orbit around Earth
v_moon = 1022           # Orbital velocity of the Moon
r_asteroid = 1e6 * 5    # Radius of the asteroid (increased for better visualization)

# Prompt the user for the asteroid's initial parameters
asteroid_x0 = float(input("Enter asteroid's initial x-coordinate (default is 4e8):") or 4e8)
asteroid_y0 = float(input("Enter asteroid's initial y-coordinate (default is 4e8):") or 4e8)
asteroid_vx0 = float(input("Enter asteroid's initial x-velocity  (default is 300):") or 300)
asteroid_vy0 = float(input("Enter asteroid's initial y-velocity  (default is -300):") or -300)

# Create container for debris from potential collision
debris_list = []

class Body:
    """ 
    Class representing celestial bodies. 
    Each body is characterized by position, velocity, radius, mass, and color. 
    """
    def __init__(self, x, y, v_x, v_y, radius, mass, color):
        self.x, self.y = x, y
        self.v_x, self.v_y = v_x, v_y
        self.radius = radius
        self.mass = mass
        self.color = color
        self.body = canvas.create_oval(*convert_to_pixel(self.x - self.radius, self.y - self.radius), 
                                        *convert_to_pixel(self.x + self.radius, self.y + self.radius), 
                                        fill=self.color)
    def move(self, dx, dy):
        """Update the position of the body on the canvas """
        canvas.move(self.body, dx * (w / rw), -dy * (h / rh))

class Debris(Body):
    """ 
    Subclass of Body representing debris particles from a collision.  
    It has an additional attribute 'lifespan', and its move method is overridden.
    """
    def __init__(self, x, y, v_x, v_y, radius, color):
        super().__init__(x, y, v_x, v_y, radius, 0, color)
        self.lifespan = 100   # Set number of frames to exist

    def move(self, dt):
        """Update the position of the body on the canvas """
        x_0, y_0 = self.x, self.y
        self.x  += self.v_x * dt
        self.y  += self.v_y * dt
        dx = self.x - x_0
        dy = self.y - y_0
        canvas.move(self.body, dx * (w / rw), -dy * (h / rh))
        self.lifespan -= 1

def convert_to_pixel(x, y):
    """Convert coordinates from simulation space (SI units) to screen space (pixels)."""
    x_scl = w / rw
    y_scl = h / rh
    pix_x = (x - l) * x_scl
    pix_y = h - (y - b) * y_scl
    return pix_x, pix_y

def collide(body1, body2):
    """Detect collision between two bodies."""
    R = ((body1.x - body2.x)**2 + (body1.y - body2.y)**2)**0.5
    return R < (body1.radius + body2.radius)

def explode(body):
    """Replace a collided body with 50 debris particles shooting off in random directions."""
    for i in range(50):
        angle = random.uniform(0, 2*math.pi)
        speed = random.uniform(1e3, 1e4)
        v_x = speed * math.cos(angle)
        v_y = speed * math.sin(angle)
        debris = Debris(body.x, body.y, v_x, v_y, body.radius/10, body.color)
        debris_list.append(debris)
    canvas.delete(body.body)

def step(body1, body2, dt):
    """
    Update the position and velocity of body1 due to gravitational interaction with body2.
    The calculations are based on Newton's law of universal gravitation.
    """
    
    x_0, y_0 = body1.x, body1.y
    R = ((body1.x - body2.x)**2 + (body1.y - body2.y)**2)**0.5
    a_x = -G * body2.mass * (body1.x - body2.x) / R**3
    a_y = -G * body2.mass * (body1.y - body2.y) / R**3
    body1.v_x += a_x * dt
    body1.v_y += a_y * dt
    body1.x  += body1.v_x * dt
    body1.y  += body1.v_y * dt
    dx = body1.x - x_0
    dy = body1.y - y_0
    body1.move(dx, dy)

def animation():
    """
    Continuously update the simulation every 40 ms.
    
    1. Calculate the motion of the Moon due to Earth's gravity.
    2. Calculate the motion of the asteroid due to both Earth's and Moon's gravity.
    3. Update and animate the debris from any collision.
    4. Detect and handle collisions between the celestial bodies.
    """
    
    dt = 6 * 60 * 60 
    step(moon, earth, dt)
    step(asteroid, earth, dt)
    step(asteroid, moon, dt)
    
    for debris in debris_list[:]:
        debris.move(dt)
        if debris.lifespan <= 0:
            canvas.delete(debris.body)
            debris_list.remove(debris)
    
    if collide(moon, asteroid):
        explode(moon)
        explode(asteroid)
        
    if collide(earth, moon):
        explode(moon)

    if collide(earth, asteroid):
        explode(asteroid)
        
    root.after(40, animation)

# Initialize the celestial bodies with their initial parameters
earth = Body(0, 0, 0, 0, r_earth, m_earth, 'blue')  
moon = Body(R_moon, 0, 0, v_moon, r_moon, m_moon, 'gray')
asteroid = Body(asteroid_x0, asteroid_y0, asteroid_vx0, asteroid_vy0, r_asteroid, 0, 'white') 

root.after(0, animation)
root.mainloop()

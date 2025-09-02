from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import random
import math

# Game variables
NUM_STARS = 100

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
GRID_LENGTH = 600

# Player UFO variables
star_positions = [(random.randint(-GRID_LENGTH, GRID_LENGTH), random.randint(GRID_LENGTH + 50, WINDOW_HEIGHT - 10)) for _ in range(NUM_STARS)]
ufo_x = 0
ufo_y = GRID_LENGTH - 50  # Lower UFO closer to the grid 
ufo_z = 50
ufo_speed = 15

# Camera variables
camera_pos = (0, 500, 500)
fovY = 120
camera_mode_3d = False  # Toggle between 2D overhead and 3D pilot view

# Game objects
bullets = []
diamonds = []

# Game state
score = 0
health = 100
game_over = False
spawn_timer = 0
difficulty_level = 1

# Bullet class
class Bullet:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.speed = 20
        self.active = True

# Diamond class
class Diamond:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.speed = 0.7  # Much slower falling speed
        self.rotation = 0
        self.active = True

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_diamond(diamond):
    glPushMatrix()
    glTranslatef(diamond.x, diamond.y, diamond.z)
    glRotatef(diamond.rotation, 1, 1, 0)  # Rotate around x and y axis
    
    # Set diamond color 
    glColor3f(0, 0.8, 1)
    
    # Create diamond shape using two pyramids 
    # Top pyramid
    glBegin(GL_TRIANGLES)
    # Front face
    glVertex3f(0, 0, 35)    # top point (increased from 30)
    glVertex3f(-25, -18, 0) # bottom left (increased from -20, -15)
    glVertex3f(25, -18, 0)  # bottom right (increased from 20, -15)
    
    # Right face
    glVertex3f(0, 0, 35)    # top point
    glVertex3f(25, -18, 0)  # front right
    glVertex3f(0, -30, 0)   # back point (increased from -25)
    
    # Back face
    glVertex3f(0, 0, 35)    # top point
    glVertex3f(0, -30, 0)   # back point
    glVertex3f(-25, -18, 0) # front left
    
    # Left face
    glVertex3f(0, 0, 35)    # top point
    glVertex3f(-25, -18, 0) # front left
    glVertex3f(25, -18, 0)  # front right
    glEnd()
    
    # Bottom pyramid
    glBegin(GL_TRIANGLES)
    # Front face
    glVertex3f(0, 0, -35)   # bottom point (increased from -30)
    glVertex3f(25, -18, 0)  # top right
    glVertex3f(-25, -18, 0) # top left
    
    # Right face
    glVertex3f(0, 0, -35)   # bottom point
    glVertex3f(0, -30, 0)   # back point
    glVertex3f(25, -18, 0)  # front right
    
    # Back face
    glVertex3f(0, 0, -35)   # bottom point
    glVertex3f(-25, -18, 0) # front left
    glVertex3f(0, -30, 0)   # back point
    
    # Left face
    glVertex3f(0, 0, -35)   # bottom point
    glVertex3f(-25, -18, 0) # front left
    glVertex3f(25, -18, 0)  # front right
    glEnd()
    
    glPopMatrix()

def draw_ufo():
    glPushMatrix()
    glTranslatef(ufo_x, ufo_y, ufo_z)
    
    # Main UFO body (dome)
    glColor3f(0.8, 0.8, 0.9)
    glPushMatrix()
    glTranslatef(0, 0, 20)
    gluSphere(gluNewQuadric(), 40, 10, 10)
    glPopMatrix()
    
    # UFO base/disk
    glColor3f(0.6, 0.6, 0.8)
    glPushMatrix()
    glScalef(1, 1, 0.3)
    gluSphere(gluNewQuadric(), 60, 15, 8)
    glPopMatrix()
    
    # Wing extensions (left and right)
    glColor3f(0.7, 0.7, 0.85)
    
    # Left wing
    glPushMatrix()
    glTranslatef(-80, 0, 0)
    glScalef(0.8, 0.3, 0.2)
    glutSolidCube(60)
    glPopMatrix()
    
    # Right wing
    glPushMatrix()
    glTranslatef(80, 0, 0)
    glScalef(0.8, 0.3, 0.2)
    glutSolidCube(60)
    glPopMatrix()
    
    # Small rectangular details on wings (yellow boxes from sketch)
    glColor3f(1, 1, 0)
    
    # Left wing details
    glPushMatrix()
    glTranslatef(-100, 15, 5)
    glutSolidCube(8)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(-100, -15, 5)
    glutSolidCube(8)
    glPopMatrix()
    
    # Right wing details
    glPushMatrix()
    glTranslatef(100, 15, 5)
    glutSolidCube(8)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(100, -15, 5)
    glutSolidCube(8)
    glPopMatrix()
    
    # Central details
    glPushMatrix()
    glTranslatef(-15, 40, 5)
    glutSolidCube(10)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(15, 40, 5)
    glutSolidCube(10)
    glPopMatrix()
    
    # Bottom engine details
    glPushMatrix()
    glTranslatef(-20, -60, -10)
    glutSolidCube(12)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(20, -60, -10)
    glutSolidCube(12)
    glPopMatrix()
    
    glPopMatrix()

def draw_bullet(bullet):
    glPushMatrix()
    glTranslatef(bullet.x, bullet.y, bullet.z)
    glColor3f(1, 1, 0)  # Yellow bullets
    glutSolidSphere(6, 8, 8)  # Bigger bullet size (increased from 3 to 6)
    glPopMatrix()

def spawn_diamond():
    """Spawn a new diamond at random position from the entire top edge of the grid"""
    # Random X position across the entire width of the grid
    x = random.randint(-GRID_LENGTH + 30, GRID_LENGTH - 30)
    # Start from the top edge (far end)
    y = -GRID_LENGTH + 20
    # Random height for visual variety
    z = random.randint(15, 80)
    diamonds.append(Diamond(x, y, z))

def idle():
    global spawn_timer
    # Spawn diamonds even less frequently for level-1
    spawn_timer += 1
    if spawn_timer >= random.randint(720, 1080):  # Random spawn between 12-18 seconds
        spawn_diamond()
        spawn_timer = 0
    
    # Update bullets
    for bullet in bullets[:]:
        bullet.y -= bullet.speed  # Bullets go toward the viewer (bottom)
        if bullet.y < -GRID_LENGTH:
            bullets.remove(bullet)
    
    # Update diamonds
    for diamond in diamonds[:]:
        diamond.y += 0.25  # Falling speed remains slow
        diamond.rotation += 3
        
        # Remove diamonds that reach the UFO side (lower grid boundary)
        if diamond.y > GRID_LENGTH:
            diamonds.remove(diamond)
    
    glutPostRedisplay()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

    # Draw stars on the black background only in overhead view
    if not camera_mode_3d:
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glColor3f(1, 1, 1)
        glPointSize(2)
        glBegin(GL_POINTS)
        for x, y in star_positions:
            glVertex2f(x + WINDOW_WIDTH // 2, y)
        glEnd()
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    setupCamera()

    # Draw the grid (game floor)
    glBegin(GL_QUADS)
    glColor3f(0.2, 0.2, 0.4)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glEnd()
    
    # Draw grid lines
    glColor3f(0.3, 0.3, 0.5)
    glBegin(GL_LINES)
    for i in range(-GRID_LENGTH, GRID_LENGTH + 1, 100):
        glVertex3f(i, -GRID_LENGTH, 1)
        glVertex3f(i, GRID_LENGTH, 1)
        glVertex3f(-GRID_LENGTH, i, 1)
        glVertex3f(GRID_LENGTH, i, 1)
    glEnd()
    
    # Draw game objects
    if not game_over:
        # In 3D pilot view, don't draw the UFO since we're inside it
        if not camera_mode_3d:
            draw_ufo()
    
    for bullet in bullets:
        draw_bullet(bullet)
    
    for diamond in diamonds:
        draw_diamond(diamond)
    
    # Draw UI
    camera_mode_text = "3D Pilot View" if camera_mode_3d else "Overhead View"
    draw_text(10, 770, f"Your Score: {score}")
    draw_text(10, 740, f"Health: {health}%")
    draw_text(10, 710, f"Level: {difficulty_level}")
    draw_text(10, 680, f"Camera: {camera_mode_text}")
    draw_text(10, 650, "Controls: WASD/Arrow Keys to move, Space/Mouse to shoot, C to toggle camera")
    
    if game_over:
        draw_text(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2, "GAME OVER!")
        draw_text(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 - 30, f"Final Score: {score}")
        draw_text(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 - 60, "Press R to restart")
    
    glutSwapBuffers()

def setupCamera():
    """
    Configures the camera's projection and view settings.
    Uses a perspective projection and positions the camera to look at the target.
    """
    glMatrixMode(GL_PROJECTION)  # Switch to projection matrix mode
    glLoadIdentity()  # Reset the projection matrix
    
    if camera_mode_3d:
        # 3D pilot view - narrower field of view for more realistic perspective
        gluPerspective(75, 1.25, 0.1, 1500)
    else:
        # Overhead view - wider field of view
        gluPerspective(fovY, 1.25, 0.1, 1500)
    
    glMatrixMode(GL_MODELVIEW)  # Switch to model-view matrix mode
    glLoadIdentity()  # Reset the model-view matrix

    if camera_mode_3d:
        # 3D pilot view - camera positioned inside UFO cockpit looking forward
        # Camera is at UFO position but slightly elevated and forward
        pilot_x = ufo_x
        pilot_y = ufo_y + 60  # Slightly forward from UFO center
        pilot_z = ufo_z + 40  # Elevated inside the cockpit
        
        # Look towards the far end of the grid where diamonds spawn
        gluLookAt(pilot_x, pilot_y, pilot_z,      # Camera position (pilot's eyes)
                  pilot_x, pilot_y - 200, pilot_z,  # Look straight ahead towards far end
                  0, 0, 1)                         # Up vector (z-axis)
    else:
        # Overhead view - original camera position
        x, y, z = camera_pos
        gluLookAt(x, y, z,  # Camera position
                  0, 0, 0,  # Look-at target
                  0, 0, 1)  # Up vector (z-axis)

def keyboardListener(key, x, y):
    global ufo_x, ufo_y, game_over, score, health, bullets, spawn_timer, difficulty_level, diamonds, camera_mode_3d
    
    if game_over:
        if key == b'r':  # Reset game
            ufo_x = 0
            ufo_y = GRID_LENGTH - 180  # Always reset to far end
            score = 0
            health = 100
            game_over = False
            spawn_timer = 0
            difficulty_level = 1
            bullets.clear()
            diamonds.clear()
            camera_mode_3d = False  # Reset to overhead view
        return
    
    # Toggle camera mode with C key
    if key == b'c' or key == b'C':
        camera_mode_3d = not camera_mode_3d
        return
    
    # UFO stays at the bottom, only allow left/right movement
    if key == b'a' or key == b'A':
        if ufo_x > -GRID_LENGTH + 100:
            ufo_x -= ufo_speed
    if key == b'd' or key == b'D':
        if ufo_x < GRID_LENGTH - 100:
            ufo_x += ufo_speed
    # Shoot bullet (Space key)
    if key == b' ':
        # Fire from head shooters (center front)
        bullets.append(Bullet(ufo_x - 15, ufo_y + 40, ufo_z + 5))
        bullets.append(Bullet(ufo_x + 15, ufo_y + 40, ufo_z + 5))

def specialKeyListener(key, x, y):
    """
    Handles special key inputs (arrow keys) for UFO movement.
    """
    global ufo_x, ufo_y
    if game_over:
        return
    if key == GLUT_KEY_LEFT:
        if ufo_x > -GRID_LENGTH + 100:
            ufo_x -= ufo_speed
    if key == GLUT_KEY_RIGHT:
        if ufo_x < GRID_LENGTH - 100:
            ufo_x += ufo_speed

def mouseListener(button, state, x, y):
    """
    Handles mouse inputs for firing bullets (left click).
    """
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN and not game_over:
        # Fire from head shooters
        bullets.append(Bullet(ufo_x - 15, ufo_y + 40, ufo_z + 5))
        bullets.append(Bullet(ufo_x + 15, ufo_y + 40, ufo_z + 5))

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GL_DEPTH)  # Enable depth testing
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"THE ULTIMATE UFO")
    
    glEnable(GL_DEPTH_TEST)  # Enable depth testing for proper 3D rendering
    glClearColor(0, 0, 0.1, 1)
    
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    glutMainLoop()

if __name__ == "__main__":
    main()
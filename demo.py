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
bombs = []  # New bombs list

# Game state
score = 0
health = 100
game_over = False
spawn_timer = 0
bomb_spawn_counter = 0  # Counter for bomb spawning ratio
difficulty_level = 1
level = 1  # Add level variable
max_level = 20

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

# Bomb class
class Bomb:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.speed = 0.7  # Same base speed as diamonds
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

def draw_bomb(bomb):
    glPushMatrix()
    glTranslatef(bomb.x, bomb.y, bomb.z)
    glRotatef(bomb.rotation, 0, 0, 1)  # Rotate around z axis for bombs
    
    # Set bomb color - pure black
    glColor3f(0, 0, 0)
    # Main bomb body (sphere)
    glutSolidSphere(25, 10, 10)
    # Add some spikes/details to make it look dangerous
    glColor3f(0, 0, 0)
    # Top spike
    glPushMatrix()
    glTranslatef(0, 0, 25)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 3, 0, 15, 6, 1)
    glPopMatrix()
    # Bottom spike  
    glPushMatrix()
    glTranslatef(0, 0, -25)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 3, 0, 15, 6, 1)
    glPopMatrix()
    # Side spikes
    glPushMatrix()
    glTranslatef(25, 0, 0)
    glRotatef(90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 2, 0, 10, 6, 1)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(-25, 0, 0)
    glRotatef(-90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 2, 0, 10, 6, 1)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0, 25, 0)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 2, 0, 10, 6, 1)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0, -25, 0)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 2, 0, 10, 6, 1)
    glPopMatrix()
    
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

def spawn_bomb():
    """Spawn a new bomb at random position from the entire top edge of the grid"""
    # Random X position across the entire width of the grid
    x = random.randint(-GRID_LENGTH + 30, GRID_LENGTH - 30)
    # Start from the top edge (far end)
    y = -GRID_LENGTH + 20
    # Random height for visual variety
    z = random.randint(15, 80)
    bombs.append(Bomb(x, y, z))

def idle():
    global spawn_timer, score, level, difficulty_level, bomb_spawn_counter, health, game_over
    
    # Leveling system: update level based on score
    level = min(max_level, score // 50 + 1)
    difficulty_level = level
    
    # Spawn diamonds and bombs with 5:1 ratio
    spawn_timer += 1
    spawn_interval = max(1500 - (level - 1) * 60, 300)  # Faster spawn for higher levels
    
    if spawn_timer >= random.randint(spawn_interval, spawn_interval + 300):
        # Spawn diamond
        spawn_diamond()
        bomb_spawn_counter += 1
        
        # Every 5th spawn, also spawn a bomb
        if bomb_spawn_counter >= 5:
            spawn_bomb()
            bomb_spawn_counter = 0
            
        spawn_timer = 0
    
    # Update bullets
    for bullet in bullets[:]:
        bullet.y -= bullet.speed
        if bullet.y < -GRID_LENGTH:
            bullets.remove(bullet)
    
    # Update diamonds
    diamond_speed = 0.15 + (level - 1) * 0.1  # Increase speed by 0.1 per level
    for diamond in diamonds[:]:
        diamond.y += diamond_speed
        diamond.rotation += 3
        if diamond.z < 30:
            diamonds.remove(diamond)
            continue
        if diamond.y > GRID_LENGTH:
            diamonds.remove(diamond)
    
    # Update bombs with same speed increase as diamonds
    bomb_speed = 0.15 + (level - 1) * 0.1  # Same speed progression as diamonds
    for bomb in bombs[:]:
        bomb.y += bomb_speed
        bomb.rotation += 2  # Slightly different rotation speed
        if bomb.z < 30:
            bombs.remove(bomb)
            continue
        if bomb.y > GRID_LENGTH:
            bombs.remove(bomb)
    
    # Bullet-diamond collision and scoring
    for bullet in bullets[:]:
        for diamond in diamonds[:]:
            distance = ((bullet.x - diamond.x)**2 + (bullet.y - diamond.y)**2 + (bullet.z - diamond.z)**2)**0.5
            if distance < 30:
                bullets.remove(bullet)
                diamonds.remove(diamond)
                score += 2
                break
    
    # Bullet-bomb collision and penalty
    for bullet in bullets[:]:
        for bomb in bombs[:]:
            distance = ((bullet.x - bomb.x)**2 + (bullet.y - bomb.y)**2 + (bullet.z - bomb.z)**2)**0.5
            if distance < 35:  # Slightly larger collision radius for bombs
                bullets.remove(bullet)
                bombs.remove(bomb)
                score = max(0, score - 5)  # Penalty for shooting bombs
                health = max(0, health - 10)  # Health penalty (fixed 10 points)
                if health <= 0:
                    game_over = True
                break
    
    # UFO-bomb collision (direct hit or wing hit)
    # Define wing positions relative to UFO
    wing_offsets = [(-80, 0, 0), (80, 0, 0)]  # Left and right wings
    wing_collision_radius = 50  # Same as UFO body for simplicity
    for bomb in bombs[:]:
        # Check collision with UFO body
        ufo_distance = ((ufo_x - bomb.x)**2 + (ufo_y - bomb.y)**2 + (ufo_z - bomb.z)**2)**0.5
        wing_hit = False
        for wx, wy, wz in wing_offsets:
            wing_x = ufo_x + wx
            wing_y = ufo_y + wy
            wing_z = ufo_z + wz
            wing_distance = ((wing_x - bomb.x)**2 + (wing_y - bomb.y)**2 + (wing_z - bomb.z)**2)**0.5
            if wing_distance < wing_collision_radius:
                wing_hit = True
                break
        if ufo_distance < 50 or wing_hit:
            bombs.remove(bomb)
            health = max(0, health - 10)  # Reduce health by fixed 10 points
            score = max(0, score - 10)  # Score penalty for direct hit
            if health <= 0:
                game_over = True
    
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
    
    for bomb in bombs:
        draw_bomb(bomb)
    
    # Draw UI
    camera_mode_text = "3D Pilot View" if camera_mode_3d else "Overhead View"
    draw_text(10, 770, f"Your Score: {score}")
    draw_text(10, 740, f"Health: {health}%")
    draw_text(10, 710, f"Level: {level}")
    draw_text(10, 680, f"Camera: {camera_mode_text}")
    draw_text(10, 650, "Controls: AD/Arrow Keys to move, Space/Mouse to shoot, C to toggle camera")
    draw_text(10, 620, "WARNING: Avoid shooting bombs!")
    
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
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        # Pilot view: camera behind and above UFO, looking toward falling diamonds
        gluLookAt(ufo_x, ufo_y + 120, ufo_z + 60,  # Camera behind and above UFO, facing diamonds
                  ufo_x, ufo_y - 100, ufo_z,      # Look toward falling diamonds
                  0, 0, 1)                        # Up vector
    else:
        # Overhead view - original camera position
        gluPerspective(fovY, 1.25, 0.1, 1500)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        x, y, z = camera_pos
        gluLookAt(x, y, z, 0, 0, 0, 0, 0, 1)

def keyboardListener(key, x, y):
    global ufo_x, ufo_y, game_over, score, health, bullets, spawn_timer, difficulty_level, diamonds, bombs, camera_mode_3d, bomb_spawn_counter
    if game_over:
        if key == b'r':
            ufo_x = 0
            ufo_y = GRID_LENGTH - 180
            score = 0
            health = 100
            game_over = False
            spawn_timer = 0
            bomb_spawn_counter = 0
            difficulty_level = 1
            bullets.clear()
            diamonds.clear()
            bombs.clear()
        return
    # Toggle camera mode with 'C' key
    if key == b'c':
        camera_mode_3d = not camera_mode_3d
    # UFO stays at the bottom, only allow left/right movement
    moved = False
    margin = 15  # Allow UFO to reach closer to grid edge
    if key == b'a':
        if ufo_x < GRID_LENGTH - margin:
            ufo_x += ufo_speed
            moved = True
    if key == b'd':
        if ufo_x > -GRID_LENGTH + margin:
            ufo_x -= ufo_speed
            moved = True
    # Shoot bullet (Space key)
    if key == b' ':
        bullets.append(Bullet(ufo_x - 15, ufo_y + 40, ufo_z + 5))
        bullets.append(Bullet(ufo_x + 15, ufo_y + 40, ufo_z + 5))

def specialKeyListener(key, x, y):
    """
    Handles special key inputs (arrow keys) for UFO movement.
    """
    global ufo_x, ufo_y
    margin = 15
    if game_over:
        return
    if key == GLUT_KEY_LEFT:
        if ufo_x < GRID_LENGTH - margin:
            ufo_x += ufo_speed
    if key == GLUT_KEY_RIGHT:
        if ufo_x > -GRID_LENGTH + margin:
            ufo_x -= ufo_speed

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
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(100, 10)  
    glutCreateWindow(b"THE ULTIMATE UFO")
    glEnable(GL_DEPTH_TEST)
    glClearColor(0, 0, 0.1, 1)
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    glutMainLoop()

if __name__ == "__main__":
    main()
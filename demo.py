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
ufo_y = GRID_LENGTH - 100  # Far end (top of grid)
ufo_z = 50
ufo_speed = 15

# Camera variables
camera_pos = (0, 500, 500)
fovY = 120

# Game objects
bullets = []
diamonds = []
bombs = []

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
        self.speed = 2 + difficulty_level * 0.5
        self.active = True
        self.rotation = 0

# Bomb class
class Bomb:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.speed = 1.2 + difficulty_level * 0.3
        self.active = True
        self.rotation = 0

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

def draw_ufo():
    """Draw UFO based on the provided sketch"""
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
    gluSphere(gluNewQuadric(), 3, 6, 6)
    glPopMatrix()

def draw_diamond(diamond):
    glPushMatrix()
    glTranslatef(diamond.x, diamond.y, diamond.z)
    glRotatef(diamond.rotation, 0, 0, 1)
    glRotatef(diamond.rotation * 0.7, 1, 0, 0)
    glColor3f(0, 1, 1)  # Cyan diamonds
    
    # Create diamond shape using two pyramids
    glBegin(GL_TRIANGLES)
    # Top pyramid
    for i in range(4):
        angle1 = i * 90 * math.pi / 180
        angle2 = ((i + 1) % 4) * 90 * math.pi / 180
        x1, y1 = 15 * math.cos(angle1), 15 * math.sin(angle1)
        x2, y2 = 15 * math.cos(angle2), 15 * math.sin(angle2)
        
        glVertex3f(0, 0, 20)  # Top point
        glVertex3f(x1, y1, 0)
        glVertex3f(x2, y2, 0)
        
        # Bottom pyramid
        glVertex3f(0, 0, -20)  # Bottom point
        glVertex3f(x2, y2, 0)
        glVertex3f(x1, y1, 0)
    glEnd()
    glPopMatrix()

def draw_bomb(bomb):
    glPushMatrix()
    glTranslatef(bomb.x, bomb.y, bomb.z)
    glRotatef(bomb.rotation, 1, 1, 0)
    glColor3f(1, 0, 0)  # Red bombs
    glutSolidCube(25)
    
    # Add spikes to make it look dangerous
    glColor3f(0.8, 0, 0)
    glPushMatrix()
    glTranslatef(15, 0, 0)
    glutSolidCone(5, 15, 4, 1)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(-15, 0, 0)
    glRotatef(180, 0, 1, 0)
    glutSolidCone(5, 15, 4, 1)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(0, 15, 0)
    glRotatef(-90, 1, 0, 0)
    glutSolidCone(5, 15, 4, 1)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(0, -15, 0)
    glRotatef(90, 1, 0, 0)
    glutSolidCone(5, 15, 4, 1)
    glPopMatrix()
    
    glPopMatrix()

def spawn_objects():
    global spawn_timer, difficulty_level
    spawn_timer += 1
    
    # Spawn diamonds and bombs at random intervals
    if spawn_timer % (60 - difficulty_level * 5) == 0:  # Faster spawning with higher difficulty
        x = random.randint(-GRID_LENGTH + 100, GRID_LENGTH - 100)
        y = -GRID_LENGTH + 100  # Spawn near the viewer
        z = random.randint(20, 100)
        if random.random() < 0.7:  # 70% chance for diamond
            diamonds.append(Diamond(x, y, z))
        else:  # 30% chance for bomb
            bombs.append(Bomb(x, y, z))

def update_game_objects():
    global score, health, game_over, difficulty_level
    
    # Update bullets
    for bullet in bullets[:]:
        bullet.y += bullet.speed  # Bullets go toward the far end
        if bullet.y > GRID_LENGTH:
            bullets.remove(bullet)
    # Update diamonds
    for diamond in diamonds[:]:
        diamond.y += diamond.speed  # Diamonds go toward the far end
        diamond.rotation += 5
        if diamond.y > GRID_LENGTH:
            diamonds.remove(diamond)
            health -= 5  # Lose health for missing diamonds
    # Update bombs
    for bomb in bombs[:]:
        bomb.y += bomb.speed  # Bombs go toward the far end
        bomb.rotation += 3
        if bomb.y > GRID_LENGTH:
            bombs.remove(bomb)
    
    # Check bullet-diamond collisions
    for bullet in bullets[:]:
        for diamond in diamonds[:]:
            distance = math.sqrt((bullet.x - diamond.x)**2 + (bullet.y - diamond.y)**2 + (bullet.z - diamond.z)**2)
            if distance < 25:
                bullets.remove(bullet)
                diamonds.remove(diamond)
                score += 10
                break
    
    # Check bullet-bomb collisions
    for bullet in bullets[:]:
        for bomb in bombs[:]:
            distance = math.sqrt((bullet.x - bomb.x)**2 + (bullet.y - bomb.y)**2 + (bullet.z - bomb.z)**2)
            if distance < 30:
                bullets.remove(bullet)
                bombs.remove(bomb)
                score -= 5  # Penalty for shooting bombs
                break
    
    # Check UFO-diamond collisions
    for diamond in diamonds[:]:
        distance = math.sqrt((ufo_x - diamond.x)**2 + (ufo_y - diamond.y)**2 + (ufo_z - diamond.z)**2)
        if distance < 50:
            diamonds.remove(diamond)
            score += 15  # Bonus for collecting directly
    
    # Check UFO-bomb collisions
    for bomb in bombs[:]:
        distance = math.sqrt((ufo_x - bomb.x)**2 + (ufo_y - bomb.y)**2 + (ufo_z - bomb.z)**2)
        if distance < 50:
            bombs.remove(bomb)
            health -= 20
    
    # Update difficulty level
    difficulty_level = 1 + score // 100
    
    # Check game over
    if health <= 0:
        game_over = True

def keyboardListener(key, x, y):
    global ufo_x, ufo_y, game_over, score, health, bullets, diamonds, bombs, spawn_timer, difficulty_level
    
    if game_over:
        if key == b'r':  # Reset game
            ufo_x = 0
            ufo_y = GRID_LENGTH - 100  # Always reset to far end
            score = 0
            health = 100
            game_over = False
            spawn_timer = 0
            difficulty_level = 1
            bullets.clear()
            diamonds.clear()
            bombs.clear()
        return
    
    # UFO stays at the bottom, only allow left/right movement
    # Move left (A key)
    if key == b'a':
        if ufo_x > -GRID_LENGTH + 100:
            ufo_x -= ufo_speed
    # Move right (D key)
    if key == b'd':
        if ufo_x < GRID_LENGTH - 100:
            ufo_x += ufo_speed
    
    # Move left (A key)
    if key == b'a':
        if ufo_x > -GRID_LENGTH + 100:
            ufo_x -= ufo_speed
    
    # Move right (D key)
    if key == b'd':
        if ufo_x < GRID_LENGTH - 100:
            ufo_x += ufo_speed
    
    # Shoot bullet (Space key)
    if key == b' ':
        bullets.append(Bullet(ufo_x, ufo_y + 50, ufo_z))

def specialKeyListener(key, x, y):
    global ufo_x, ufo_y
    
    if game_over:
        return
    
    # UFO stays at the bottom, only allow left/right movement
    if key == GLUT_KEY_LEFT:
        if ufo_x > -GRID_LENGTH + 100:
            ufo_x -= ufo_speed
    if key == GLUT_KEY_RIGHT:
        if ufo_x < GRID_LENGTH - 100:
            ufo_x += ufo_speed

def mouseListener(button, state, x, y):
    # Left mouse button fires a bullet
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN and not game_over:
        bullets.append(Bullet(ufo_x, ufo_y + 50, ufo_z))

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    x, y, z = camera_pos
    gluLookAt(x, y, z, 0, 0, 0, 0, 0, 1)

def idle():
    if not game_over:
        spawn_objects()
        update_game_objects()
    glutPostRedisplay()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

    # Draw stars on the black background (above the play field)
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
        draw_ufo()
    
    for bullet in bullets:
        draw_bullet(bullet)
    
    for diamond in diamonds:
        draw_diamond(diamond)
    
    for bomb in bombs:
        draw_bomb(bomb)
    
    # Draw UI
    draw_text(10, 770, f"THE ULTIMATE UFO - Score: {score}")
    draw_text(10, 740, f"Health: {health}%")
    draw_text(10, 710, f"Level: {difficulty_level}")
    draw_text(10, 680, "Controls: WASD/Arrow Keys to move, Space/Mouse to shoot")
    
    if game_over:
        draw_text(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2, "GAME OVER!")
        draw_text(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 - 30, f"Final Score: {score}")
        draw_text(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 - 60, "Press R to restart")
    
    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"THE ULTIMATE UFO - Shooting Game")
    
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
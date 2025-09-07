last_level = 1  # Track previous level for boss spawn reset
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import random
import math
import time

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
hearts = []  # New hearts list
gifts = []  # New 4x shooting gifts list
boss_bullets = []  # Boss bullets list

# Boss/Enemy variables
boss_active = False
boss_x = 0
boss_y = -GRID_LENGTH + 50  # Opposite side of the grid from UFO
boss_z = 50
boss_health = 100
boss_shoot_timer = 0
boss_shoot_interval = 120  # Boss shoots every 120 frames (about 2 seconds at 60fps)
boss_spawn_timer = 0
boss_last_ufo_x = 0  # Track UFO position for predictive shooting
boss_spawned_this_level = False
boss_next_spawn_score = 0

# Game state
score = 0
health = 100
game_over = False
spawn_timer = 0
bomb_spawn_counter = 0  # Counter for bomb spawning ratio
heart_spawn_counter = 0  # Counter for heart spawning ratio
diamond_spawn_counter = 0  # Counter for diamonds spawned
difficulty_level = 1
level = 1  # Add level variable
max_level = 20

# 4x Shooting power-up variables
four_x_active = False
four_x_timer = 0
four_x_start_time = 0
four_x_duration = 10  # 10 seconds, real time

# Bullet class
class Bullet:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.speed = 20
        self.active = True

# Boss Bullet class
class BossBullet:
    def __init__(self, x, y, z, dx, dy, dz):
        self.x = x
        self.y = y
        self.z = z
        self.dx = dx
        self.dy = dy
        self.dz = dz

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

# Heart class
class Heart:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.speed = 0.7  # Same as diamonds and bombs
        self.rotation = 0
        self.active = True

# Gift class for 4x shooting power-up
class Gift:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.speed = 0.7  # Same as other objects
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

def draw_boss():
    """Draw the boss enemy with purple color #a742f5"""
    glPushMatrix()
    glTranslatef(boss_x, boss_y, boss_z)
    
    # Boss color - purple #a742f5
    boss_r = 0xa7 / 255.0  # 167/255
    boss_g = 0x42 / 255.0  # 66/255
    boss_b = 0xf5 / 255.0  # 245/255
    
    # Main boss body - larger and more intimidating than player UFO
    glColor3f(boss_r, boss_g, boss_b)
    
    # Boss main dome (larger than player)
    glPushMatrix()
    glTranslatef(0, 0, 30)
    gluSphere(gluNewQuadric(), 60, 12, 12)
    glPopMatrix()
    
    # Boss base/disk (larger)
    glPushMatrix()
    glScalef(1.2, 1.2, 0.4)
    gluSphere(gluNewQuadric(), 80, 20, 10)
    glPopMatrix()
    
    # Boss weapon arms (menacing extensions)
    glColor3f(boss_r * 0.8, boss_g * 0.8, boss_b * 0.8)  # Slightly darker
    
    # Left weapon arm
    glPushMatrix()
    glTranslatef(-100, 0, 10)
    glScalef(1.2, 0.4, 0.3)
    glutSolidCube(70)
    glPopMatrix()
    
    # Right weapon arm
    glPushMatrix()
    glTranslatef(100, 0, 10)
    glScalef(1.2, 0.4, 0.3)
    glutSolidCube(70)
    glPopMatrix()
    
    # Boss weapon cannons (glowing red)
    glColor3f(1, 0, 0)  # Red for danger
    
    # Left cannon
    glPushMatrix()
    glTranslatef(-120, 20, 15)
    gluCylinder(gluNewQuadric(), 8, 6, 25, 8, 1)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(-120, -20, 15)
    gluCylinder(gluNewQuadric(), 8, 6, 25, 8, 1)
    glPopMatrix()
    
    # Right cannon
    glPushMatrix()
    glTranslatef(120, 20, 15)
    gluCylinder(gluNewQuadric(), 8, 6, 25, 8, 1)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(120, -20, 15)
    gluCylinder(gluNewQuadric(), 8, 6, 25, 8, 1)
    glPopMatrix()
    
    # Boss central eye/core (glowing)
    glColor3f(1, 0.2, 0.2)  # Bright red core
    glPushMatrix()
    glTranslatef(0, 0, 35)
    glutSolidSphere(15, 10, 10)
    glPopMatrix()
    
    # Additional menacing spikes around the boss
    glColor3f(boss_r * 0.6, boss_g * 0.6, boss_b * 0.6)
    
    # Front spikes
    for i in range(6):
        angle = i * 60  # 60 degrees apart
        spike_x = 70 * math.cos(math.radians(angle))
        spike_y = 70 * math.sin(math.radians(angle))
        glPushMatrix()
        glTranslatef(spike_x, spike_y, 0)
        glRotatef(angle, 0, 0, 1)
        gluCylinder(gluNewQuadric(), 4, 0, 20, 6, 1)
        glPopMatrix()
    
    glPopMatrix()

def draw_boss_bullet(bullet):
    """Draw boss bullets - different from player bullets"""
    glPushMatrix()
    glTranslatef(bullet.x, bullet.y, bullet.z)
    glColor3f(1, 0, 0)  # Red boss bullets
    # Make boss bullets larger and more menacing
    glutSolidSphere(10, 8, 8)
    
    # Add some glowing effect around the bullet
    glColor3f(1, 0.5, 0.5)
    glutWireSphere(12, 6, 6)
    
    glPopMatrix()

def spawn_boss():
    """Spawn the boss at a random time during levels 2+"""
    global boss_active, boss_x, boss_y, boss_z, boss_health, boss_spawn_timer, boss_shoot_interval
    
    if level >= 2 and not boss_active:
        # Random chance to spawn boss (increases with level)
        spawn_chance = (level - 1) * 0.001  # 0.1% at level 2, 0.2% at level 3, etc.
        if random.random() < spawn_chance:
            boss_active = True
            boss_x = ufo_x
            boss_y = -ufo_y  # Place boss at the exact opposite Y position of the UFO
            boss_z = 50
            # Set boss health by level range for gradual difficulty
            if 2 <= level <= 5:
                boss_health = 40
            elif 6 <= level <= 10:
                boss_health = 80
            elif 11 <= level <= 15:
                boss_health = 120
            elif 16 <= level <= 19:
                boss_health = 160
            elif level == 20:
                boss_health = 200
            else:
                boss_health = 40  # Default for safety
            boss_spawn_timer = 0
            # Adjust boss shooting frequency based on level (faster shooting at higher levels)
            boss_shoot_interval = max(60, 180 - (level * 10))  # Minimum 60 frames, decreases with level

def update_boss():
    global boss_x
    # Boss only tracks UFO's X position (left/right), not Y or Z
    if boss_x < ufo_x:
        boss_x = min(boss_x + ufo_speed, ufo_x)
    elif boss_x > ufo_x:
        boss_x = max(boss_x - ufo_speed, ufo_x)
    # Boss stays at fixed Y (opposite of UFO) and fixed Z

def boss_shoots_at_ufo():
    # Calculate direction from boss to UFO
    dir_x = ufo_x - boss_x
    dir_y = ufo_y - boss_y
    dir_z = ufo_z - boss_z
    length = math.sqrt(dir_x**2 + dir_y**2 + dir_z**2)
    if length == 0:
        length = 1  # Prevent division by zero
    # Set boss bullet speed by level range (reduced for easier gameplay)
    if 2 <= level <= 5:
        speed = 3
    elif 6 <= level <= 10:
        speed = 4
    elif 11 <= level <= 15:
        speed = 5
    elif 16 <= level <= 19:
        speed = 6
    elif level == 20:
        speed = 7
    else:
        speed = 3  # Default for safety
    dx = dir_x / length * speed
    dy = dir_y / length * speed
    dz = dir_z / length * speed
    boss_bullets.append(BossBullet(boss_x, boss_y, boss_z, dx, dy, dz))

def update_boss_bullets():
    for bullet in boss_bullets[:]:
        bullet.x += bullet.dx
        bullet.y += bullet.dy
        bullet.z += bullet.dz
        # Remove if out of bounds
        if (abs(bullet.x) > GRID_LENGTH + 100 or abs(bullet.y) > GRID_LENGTH + 100 or bullet.z < 0 or bullet.z > WINDOW_HEIGHT):
            boss_bullets.remove(bullet)

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

def draw_gift(gift):
    glPushMatrix()
    glTranslatef(gift.x, gift.y, gift.z)
    glRotatef(gift.rotation, 1, 1, 1)  # Rotate around all axes for a spinning effect
    
    # Main gift box - golden color
    glColor3f(1, 0.8, 0)  # Gold color
    glutSolidCube(30)
    
    # Gift ribbon - red color
    glColor3f(1, 0, 0)  # Red color
    
    # Horizontal ribbon
    glPushMatrix()
    glScalef(1.1, 0.1, 0.1)
    glutSolidCube(30)
    glPopMatrix()
    
    # Vertical ribbon
    glPushMatrix()
    glScalef(0.1, 1.1, 0.1)
    glutSolidCube(30)
    glPopMatrix()
    
    # Bow on top
    glPushMatrix()
    glTranslatef(0, 0, 20)
    glColor3f(0.8, 0, 0)  # Darker red for bow
    glutSolidSphere(8, 8, 8)
    glPopMatrix()
    
    # "4X" text indicator - draw small cubes to represent 4X
    glColor3f(1, 1, 0)  # Yellow for visibility
    
    # Draw small indicator cubes around the gift
    positions = [(-20, -20, 0), (20, -20, 0), (-20, 20, 0), (20, 20, 0)]
    for px, py, pz in positions:
        glPushMatrix()
        glTranslatef(px, py, pz)
        glutSolidCube(4)
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
    # If 4x shooting is active, make them glow brighter
    if four_x_active:
        glColor3f(1, 1, 0.2)  # Brighter yellow when 4x is active
    else:
        glColor3f(1, 1, 0)
    
    # Left wing details (wing shooters)
    glPushMatrix()
    glTranslatef(-100, 15, 5)
    glutSolidCube(8)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(-100, -15, 5)
    glutSolidCube(8)
    glPopMatrix()
    
    # Right wing details (wing shooters)
    glPushMatrix()
    glTranslatef(100, 15, 5)
    glutSolidCube(8)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(100, -15, 5)
    glutSolidCube(8)
    glPopMatrix()
    
    # Central details (head shooters)
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

def draw_heart(heart):
    glPushMatrix()
    glTranslatef(heart.x, heart.y, heart.z)
    glRotatef(heart.rotation, 0, 0, 1)
    glColor3f(1, 0, 0)  # Red color
    # Draw heart as a 3D red sphere (circular heart)
    glutSolidSphere(15, 16, 16)
    glPopMatrix()

def is_spawn_position_clear(x, y, z, min_dist=60):
    for obj in diamonds + bombs + hearts + gifts:
        dist = ((x - obj.x)**2 + (y - obj.y)**2 + (z - obj.z)**2)**0.5
        if dist < min_dist:
            return False
    return True

def spawn_diamond():
    global diamond_spawn_counter
    for _ in range(10):  # Try up to 10 times to find a clear spot
        x = random.randint(-GRID_LENGTH + 30, GRID_LENGTH - 30)
        y = -GRID_LENGTH + 20
        z = random.randint(15, 80)
        if is_spawn_position_clear(x, y, z):
            diamonds.append(Diamond(x, y, z))
            diamond_spawn_counter += 1
            return

def spawn_bomb():
    for _ in range(10):
        x = random.randint(-GRID_LENGTH + 30, GRID_LENGTH - 30)
        y = -GRID_LENGTH + 20
        z = random.randint(15, 80)
        if is_spawn_position_clear(x, y, z):
            bombs.append(Bomb(x, y, z))
            return

def spawn_heart():
    for _ in range(10):
        x = random.randint(-GRID_LENGTH + 30, GRID_LENGTH - 30)
        y = -GRID_LENGTH + 20
        z = random.randint(15, 80)
        if is_spawn_position_clear(x, y, z):
            hearts.append(Heart(x, y, z))
            return

def spawn_gift():
    for _ in range(10):
        x = random.randint(-GRID_LENGTH + 30, GRID_LENGTH - 30)
        y = -GRID_LENGTH + 20
        z = random.randint(15, 80)
        if is_spawn_position_clear(x, y, z):
            gifts.append(Gift(x, y, z))
            return

def shoot_bullets():
    """Shoot bullets based on current power-up state"""
    if four_x_active:
        # Shoot from all 4 positions: 2 head shooters + 2 wing shooters
        # Head shooters (front of UFO)
        bullets.append(Bullet(ufo_x - 15, ufo_y + 40, ufo_z + 5))
        bullets.append(Bullet(ufo_x + 15, ufo_y + 40, ufo_z + 5))
        # Wing shooters (left and right wings) - positioned at wing locations
        bullets.append(Bullet(ufo_x - 100, ufo_y + 15, ufo_z + 5))  # Left wing shooter
        bullets.append(Bullet(ufo_x + 100, ufo_y + 15, ufo_z + 5))  # Right wing shooter
    else:
        # Normal shooting: only head shooters
        bullets.append(Bullet(ufo_x - 15, ufo_y + 40, ufo_z + 5))
        bullets.append(Bullet(ufo_x + 15, ufo_y + 40, ufo_z + 5))

def idle():
    # ...existing code...
    global boss_reward_given
    if 'boss_reward_given' not in globals():
        boss_reward_given = False
    # ...existing code...
    # Place UFO-bomb and UFO-heart collision logic here, after global declarations
    global health, game_over
    # UFO-bomb collision: decrease health by 10% for each bomb hit
    for bomb in bombs[:]:
        ufo_distance = ((ufo_x - bomb.x)**2 + (ufo_y - bomb.y)**2 + (ufo_z - bomb.z)**2)**0.5
        if ufo_distance < 50:  # Adjust radius as needed for your UFO/bomb size
            bombs.remove(bomb)
            health = max(0, health - 10)
            if health <= 0:
                game_over = True

    # UFO-heart collision: increase health by 10% for each heart collected
    for heart in hearts[:]:
        ufo_distance = ((ufo_x - heart.x)**2 + (ufo_y - heart.y)**2 + (ufo_z - heart.z)**2)**0.5
        if ufo_distance < 50:  # Adjust radius as needed for your UFO/heart size
            hearts.remove(heart)
            health = min(100, health + 10)
    global spawn_timer, score, level, difficulty_level, bomb_spawn_counter, heart_spawn_counter
    global four_x_active, four_x_timer, diamond_spawn_counter, four_x_start_time
    global boss_active, boss_spawned_this_level, boss_next_spawn_score
    global boss_health, boss_x, boss_y, boss_z, boss_shoot_timer, boss_shoot_interval
    
    # IMPORTANT: If game is over, only update the display - don't update any game logic
    if game_over:
        glutPostRedisplay()
        return
    
    # Update 4x shooting timer
    if four_x_active:
        if time.time() - four_x_start_time >= four_x_duration:
            four_x_active = False
            four_x_start_time = 0
    
    # Leveling system: update level based on score
    global last_level
    level = min(max_level, score // 50 + 1)
    difficulty_level = level

    # Reset boss spawn for every new level (from level 2+)
    if level >= 2 and level != last_level:
        boss_spawned_this_level = False
        boss_next_spawn_score = 0
    last_level = level

    # Boss spawn logic
    if level >= 2:
        if not boss_active and not boss_spawned_this_level:
            if boss_next_spawn_score == 0:
                # Pick a random score offset for boss spawn in this level
                boss_next_spawn_score = score + random.randint(10, 40)
            if score >= boss_next_spawn_score:
                spawn_boss()
                boss_active = True
                boss_spawned_this_level = True
                boss_reward_given = False  # Reset reward flag only when new boss spawns
    else:
        boss_active = False
        boss_spawned_this_level = False
        boss_next_spawn_score = 0
        
    # Spawn diamonds, bombs, hearts, and gifts
    spawn_timer += 1
    spawn_interval = max(1000 - (level - 1) * 60, 200)  # Faster spawn for higher levels & more frequent diamonds
    if spawn_timer >= random.randint(spawn_interval, spawn_interval + 300):
        spawn_diamond()
        bomb_spawn_counter += 1
        heart_spawn_counter += 1
        
        # Every 30th diamond, spawn a gift (4x power-up)
        if diamond_spawn_counter % 30 == 0 and diamond_spawn_counter > 0:
            spawn_gift()
        
        # Every 5th spawn, also spawn a bomb
        if bomb_spawn_counter >= 5:
            spawn_bomb()
            bomb_spawn_counter = 0
        # Every 10th spawn, also spawn a heart
        if heart_spawn_counter >= 10:
            spawn_heart()
            heart_spawn_counter = 0
        spawn_timer = 0
    
    # Update bullets
    for bullet in bullets[:]:
        bullet.y -= bullet.speed
        if bullet.y < -GRID_LENGTH:
            bullets.remove(bullet)
    
    # Update boss bullets
    update_boss_bullets()

    # Boss shooting logic
    if boss_active:
        update_boss()  # Update boss position
        boss_shoot_timer += 1
        if boss_shoot_timer >= boss_shoot_interval:
            boss_shoots_at_ufo()
            boss_shoot_timer = 0
    
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
    
    # Update hearts with same speed increase as diamonds and bombs
    heart_speed = 0.15 + (level - 1) * 0.1
    for heart in hearts[:]:
        heart.y += heart_speed
        heart.rotation += 2
        if heart.z < 30:
            hearts.remove(heart)
            continue
        if heart.y > GRID_LENGTH:
            hearts.remove(heart)
    
    # Update gifts with same speed as other objects
    gift_speed = 0.15 + (level - 1) * 0.1
    for gift in gifts[:]:
        gift.y += gift_speed
        gift.rotation += 4  # Faster rotation for gifts to make them more noticeable
        if gift.z < 30:
            gifts.remove(gift)
            continue
        if gift.y > GRID_LENGTH:
            gifts.remove(gift)
    
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
    
    # Player bullet-boss collision
    if boss_active:
        for bullet in bullets[:]:
            boss_distance = ((bullet.x - boss_x)**2 + (bullet.y - boss_y)**2 + (bullet.z - boss_z)**2)**0.5
            if boss_distance < 80:  # Boss is larger, so larger collision radius
                bullets.remove(bullet)
                # Reduce boss health by correct percentage based on level group
                if 2 <= level <= 5:
                    percent = 0.25
                elif 6 <= level <= 10:
                    percent = 0.20
                elif 11 <= level <= 15:
                    percent = 0.15
                elif 16 <= level <= 19:
                    percent = 0.10
                elif level == 20:
                    percent = 0.05
                else:
                    percent = 0.25  # Default for safety
                damage = int(boss_health * percent)
                if damage < 1:
                    damage = 1
                boss_health = max(0, boss_health - damage)
                score += 5  # Bonus points for hitting boss
                if boss_health <= 0 and not boss_reward_given:
                    boss_active = False
                    # Health reward by level range
                    if 2 <= level <= 5:
                        health_reward = 20
                    elif 6 <= level <= 10:
                        health_reward = 40
                    elif 11 <= level <= 15:
                        health_reward = 60
                    elif 16 <= level <= 19:
                        health_reward = 80
                    elif level == 20:
                        health_reward = 100
                    else:
                        health_reward = 20
                    health = min(100, health + health_reward)
                    boss_health = 100  # Reset for next boss
                    boss_reward_given = True
                break
    
    # Boss bullet-UFO collision and health reduction
    for bullet in boss_bullets[:]:
        # Check collision with UFO body
        ufo_distance = ((ufo_x - bullet.x)**2 + (ufo_y - bullet.y)**2 + (ufo_z - bullet.z)**2)**0.5
        wing_hit = False
        wing_offsets = [(-80, 0, 0), (80, 0, 0)]
        wing_collision_radius = 50
        for wx, wy, wz in wing_offsets:
            wing_x = ufo_x + wx
            wing_y = ufo_y + wy
            wing_z = ufo_z + wz
            wing_distance = ((wing_x - bullet.x)**2 + (wing_y - bullet.y)**2 + (wing_z - bullet.z)**2)**0.5
            if wing_distance < wing_collision_radius:
                wing_hit = True
                break
        if ufo_distance < 50 or wing_hit:
            boss_bullets.remove(bullet)
            damage_percent = get_boss_bullet_damage_percent(level)
            health = max(0, int(health - (100 * damage_percent)))
            if health <= 0:
                game_over = True
            break
    
    # Bullet-heart collision & health gain
    for bullet in bullets[:]:
        for heart in hearts[:]:
            distance = ((bullet.x - heart.x)**2 + (bullet.y - heart.y)**2 + (bullet.z - heart.z)**2)**0.5
            if distance < 30:
                bullets.remove(bullet)
                hearts.remove(heart)
                health = min(100, health + 10)  # Gain 10 health, max 100
                break

    # Bullet-gift collision (activate 4x shooting)
    for bullet in bullets[:]:
        for gift in gifts[:]:
            distance = ((bullet.x - gift.x)**2 + (bullet.y - gift.y)**2 + (bullet.z - gift.z)**2)**0.5
            if distance < 35:
                bullets.remove(bullet)
                gifts.remove(gift)
                four_x_active = True
                four_x_start_time = time.time()
                score += 10  # Bonus score for getting the power-up
                break
    
    glutPostRedisplay()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

    # overhead view stars
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
        # In 3D pilot view
        if not camera_mode_3d:
            draw_ufo()
    
    # Draw boss if active
    if boss_active:
        draw_boss()
    
    for bullet in bullets:
        draw_bullet(bullet)
    
    for boss_bullet in boss_bullets:
        draw_boss_bullet(boss_bullet)
    
    for diamond in diamonds:
        draw_diamond(diamond)
    
    for bomb in bombs:
        draw_bomb(bomb)
    
    for heart in hearts:
        draw_heart(heart)
    
    for gift in gifts:
        draw_gift(gift)
    


    # Draw UI
    camera_mode_text = "3D Pilot View" if camera_mode_3d else "Overhead View"
    draw_text(10, 770, f"Your Score: {score}")
    draw_text(10, 740, f"Health: {health}%")
    draw_text(10, 710, f"Level: {level}")
    draw_text(10, 680, f"Camera: {camera_mode_text}")
    
    # Boss status
    if boss_active:
        draw_text(10, 560, f"BOSS ACTIVE! Health: {boss_health}")
        draw_text(10, 530, "Boss is tracking you and shooting!")
    
    # 4x shooting status
    if four_x_active:
        remaining_time = max(0, int(four_x_duration - (time.time() - four_x_start_time)))
        draw_text(10, 650, f"4X SHOOTING ACTIVE! Time: {remaining_time}s")
        draw_text(10, 620, "Controls: AD/Arrow Keys to move, Space/Mouse to shoot (4X!), C to toggle camera")
    else:
        draw_text(10, 650, "Controls: AD/Arrow Keys to move, Space/Mouse to shoot, C to toggle camera")
        pass  
    
    draw_text(10, 590, "WARNING: Avoid shooting bombs! Collect golden gifts for 4X shooting!")
    
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
    global ufo_x, ufo_y, game_over, score, health, bullets, spawn_timer, difficulty_level, diamonds, bombs, camera_mode_3d, bomb_spawn_counter, diamond_spawn_counter, four_x_active, four_x_timer, hearts, gifts
    global boss_active, boss_health, boss_bullets, boss_spawned_this_level, boss_next_spawn_score
    
    if game_over:
        if key == b'r':
            ufo_x = 0
            ufo_y = GRID_LENGTH - 50  # Reset to original starting position
            score = 0
            health = 100
            game_over = False
            spawn_timer = 0
            bomb_spawn_counter = 0
            diamond_spawn_counter = 0
            difficulty_level = 1
            four_x_active = False
            four_x_timer = 0
            boss_active = False
            boss_health = 100
            boss_spawned_this_level = False
            boss_next_spawn_score = 0
            bullets.clear()
            diamonds.clear()
            bombs.clear()
            hearts.clear()
            gifts.clear()
            boss_bullets.clear()
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
        shoot_bullets()

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
        # Fire bullets using the new shooting system
        shoot_bullets()

def get_boss_damage_percent(level):
    if 2 <= level <= 5:
        return 0.25
    elif 6 <= level <= 10:
        return 0.20
    elif 11 <= level <= 15:
        return 0.15
    elif 16 <= level <= 19:
        return 0.10
    elif level == 20:
        return 0.05
    return 0.25  # Default for safety

def get_boss_bullet_damage_percent(level):
    if 2 <= level <= 5:
        return 0.05
    elif 6 <= level <= 10:
        return 0.10
    elif 11 <= level <= 15:
        return 0.15
    elif 16 <= level <= 19:
        return 0.20
    elif level == 20:
        return 0.25
    return 0.05  # Default for safety

def get_boss_defeat_reward(level):
    if 2 <= level <= 5:
        return 20
    elif 6 <= level <= 10:
        return 40
    elif 11 <= level <= 15:
        return 60
    elif 16 <= level <= 19:
        return 80
    elif level == 20:
        return 100
    return 20  # Default for safety

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(100, 10)  
    glutCreateWindow(b"THE ULTIMATE UFO - WITH BOSS")
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
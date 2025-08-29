
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# Window size
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800

# Player (UFO) state
player_x = WINDOW_WIDTH // 2
player_y = 100
player_speed = 10

# Key state
key_states = {}

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
	glColor3f(1,1,1)
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

def draw_player():
	glColor3f(0, 1, 0)
	glBegin(GL_TRIANGLES)
	glVertex2f(player_x, player_y + 30)
	glVertex2f(player_x - 20, player_y - 20)
	glVertex2f(player_x + 20, player_y - 20)
	glEnd()

def display():
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glLoadIdentity()
	draw_player()
	draw_text(10, WINDOW_HEIGHT - 30, "UFO Arcade Game")
	glutSwapBuffers()

def update(value):
	global player_x
	# Handle player movement
	if key_states.get(b'a') or key_states.get(b'A') or key_states.get(b'\x25'):
		player_x -= player_speed
	if key_states.get(b'd') or key_states.get(b'D') or key_states.get(b'\x27'):
		player_x += player_speed
	# Clamp player position
	player_x = max(20, min(WINDOW_WIDTH - 20, player_x))
	glutPostRedisplay()
	glutTimerFunc(16, update, 0)

def keyboard(key, x, y):
	key_states[key] = True

def keyboard_up(key, x, y):
	key_states[key] = False

def special_input(key, x, y):
	# Left: GLUT_KEY_LEFT (100), Right: GLUT_KEY_RIGHT (102)
	if key == GLUT_KEY_LEFT:
		key_states[b'\x25'] = True
	elif key == GLUT_KEY_RIGHT:
		key_states[b'\x27'] = True

def special_up(key, x, y):
	if key == GLUT_KEY_LEFT:
		key_states[b'\x25'] = False
	elif key == GLUT_KEY_RIGHT:
		key_states[b'\x27'] = False

def main():
	glutInit()
	glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
	glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
	glutCreateWindow(b"THE ULTIMATE UFO")
	glClearColor(0, 0, 0.1, 1)
	gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
	glutDisplayFunc(display)
	glutKeyboardFunc(keyboard)
	glutKeyboardUpFunc(keyboard_up)
	glutSpecialFunc(special_input)
	glutSpecialUpFunc(special_up)
	glutTimerFunc(16, update, 0)
	glutMainLoop()

if __name__ == "__main__":
	main()

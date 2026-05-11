

<div align="center">
  <h1>THE ULTIMATE UFO</h1>
</div>

**The Ultimate UFO** is an action-packed 3D arcade space shooter built entirely from scratch using Python and OpenGL. Players pilot an advanced spacecraft through a beautifully rendered 3D grid, dodging dangerous bombs, collecting valuable diamonds, and engaging in intense boss battles. With dynamic camera angles and a progressive leveling system, the game offers a classic, fast-paced arcade experience right on your desktop.

<div align="center">
  <img src="https://img.shields.io/badge/Key%20Features-blue?style=for-the-badge" alt="Key Features" height="34">
</div>

* **Dynamic Camera System**: Instantly toggle between a classic 2D overhead view and an immersive 3D pilot view using the 'C' key.
* **Progressive Leveling**: The game scales in difficulty. As your score increases, spawn rates rise, enemy speeds increase, and new challenges appear.
* **Epic Boss Battles**: At higher levels, encounter formidable bosses equipped with predictive tracking, scaling health, and rapid-fire laser cannons.
* **Power-ups & Collectibles**: Gather diamonds to increase your score, catch falling hearts to restore health, and hunt down rare gifts to unlock a temporary 4X shooting multiplier.
* **Rich 3D Graphics**: Custom 3D rendering featuring translucent materials, rotating energy rings, glowing engine auras, and a dynamic twinkling starfield.
* **Physics & Collision**: Built-in distance-based collision detection for precise interactions between the UFO, projectiles, enemies, and power-ups.

<div align="center">
  <img src="https://img.shields.io/badge/Tech%20Stack-blue?style=for-the-badge" alt="Tech Stack" height="34">
</div>

-   **Language**: Python 3
-   **Graphics API**: OpenGL (PyOpenGL)
-   **Window Management**: GLUT (OpenGL Utility Toolkit)
-   **Math & Logic**: Native Python `math`, `random`, and `time` modules

### Core Logic Highlights
-   **`idle()`**: The heart of the game engine. This function handles all real-time state management, including level progression, entity spawning, movement updates, and complex collision detection.
-   **`showScreen()` & `setupCamera()`**: The rendering pipeline. Responsible for clearing buffers, setting the perspective (Overhead vs. Pilot view), drawing the grid, and iterating through all active game objects to render them on screen.
-   **Entity Classes**: Clean, object-oriented structures (`Bullet`, `BossBullet`, `Diamond`, `Bomb`, `Heart`, `Gift`) to manage the state, coordinates, and active status of all on-screen elements.
-   **`draw_*()` Functions**: Modular rendering functions using direct OpenGL calls (`glPushMatrix`, `glColor3f`, `glutSolidSphere`, etc.) to construct detailed 3D models piece-by-piece, including the UFO and the Boss.

<div align="center">
  <img src="https://img.shields.io/badge/Setup%20&%20Installation-blue?style=for-the-badge" alt="Setup & Installation" height="34">
</div>

To run this game locally on your machine, follow these simple steps:

### Prerequisites
Make sure you have Python 3.x installed on your system. You will also need the PyOpenGL library.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/uzicodes/THE--ULTIMATE--UFO.git](https://github.com/uzicodes/THE--ULTIMATE--UFO.git)
    cd THE--ULTIMATE--UFO
    ```

2.  **Install required dependencies:**
    You need the Python bindings for OpenGL and GLUT. Run the following command in your terminal:
    ```bash
    pip install PyOpenGL PyOpenGL_accelerate
    ```
    *(Note for Windows users: If you encounter glut32.dll errors, you may need to download the pre-compiled PyOpenGL wheels from Christoph Gohlke's repository or ensure freeglut is installed).*

3.  **Run the game:**
    ```bash
    python the_ultimate_ufo.py
    ```

### Game Controls
-   **`A` / `D`** or **`Left` / `Right Arrow`**: Move the UFO left and right.
-   **`Spacebar`** or **`Left Mouse Click`**: Fire weapons.
-   **`C`**: Toggle between 2D Overhead Camera and 3D Pilot View.
-   **`R`**: Restart the game after a Game Over.

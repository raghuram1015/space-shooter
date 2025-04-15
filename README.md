SPACE SHOOTER

Abstract
This project is a 2D Space Shooter game developed using both web technologies (JavaScript with HTML Canvas) and Python (using the Pygame library). The game enables players to control a spaceship, shoot enemies, and progress through levels. The player can choose between different ship types, each with unique stats like speed, damage, and regeneration. This project aims to provide an engaging arcade-style experience while also exploring cross-platform game development approaches.


Introduction

The Space Shooter genre is a classic in video game history. This project modernizes the concept with colorful graphics, animations, particle effects, and interactive ship selection. It demonstrates the use of front-end web development skills along with game logic and physics in Python. It serves as an excellent platform to understand game loops, collision detection, state management, and graphical rendering.


Aim of the Project

To develop a 2D shooting game with modern UI/UX.
To implement the game in both JavaScript (Canvas) and Python (Pygame).
To provide a ship selection mechanism with varying stats.
To create a scalable structure for levels, scoring, and health regeneration.


Advantages

Cross-platform: playable in both browser and desktop.
Enhances understanding of canvas rendering and object-oriented design.
Modular structure makes it easy to add new enemies, power-ups, or weapons.
Engaging visual and sound effects with real-time feedback.


Disadvantages

No multiplayer or networking functionality.
No save/load game system or user profiles.
Limited AI behavior; enemies follow basic patterns.
Requires a good device for smooth performance at higher levels.


Future Implementation

Add more enemy types and boss battles.
Integrate sound effects and background music.
Implement local or online multiplayer features.
Add collectible power-ups or ship upgrades.
Save high scores and introduce a leaderboard system.
Deploy the game as a mobile app using frameworks like Cordova or Pygame Mobile.


System Requirements

Hardware:

Dual-core CPU
4GB RAM or higher
GPU with basic OpenGL/WebGL support
Screen resolution 1024x768 minimum

Software:

For Web Version:
Any modern web browser (Chrome, Firefox, Edge)
Code editor (VS Code, Sublime, etc.)
For Python Version:
Python 3.x installed
pygame library installed (pip install pygame)
Operating System: Windows, Linux, or macOS


Flow Chart

![image](https://github.com/user-attachments/assets/f26affb1-6c33-4d72-bc4f-eaefed4e46b2)


Algorithm

Start Game
Show ship selection screen.
Player selects a ship type (scout, fighter, tank).
Initialize game variables: health, score, bullets, enemies.

Enter game loop:
Move player with arrow/WASD keys.
Shoot bullets (spacebar).
Enemies spawn periodically.
Collision detection between:
Bullets and enemies
Player and enemies
Update scores, health, level.
If health <= 0 → Game Over.
Show final score and restart option.


Implementation

Frontend (JavaScript & HTML5 Canvas):
index.html: Contains the layout and canvas element.
style.css: Styled UI including health bars, ship selection, and game HUD.
game.js: Main logic — player movement, shooting, particle effects, enemy AI, collision detection, levels, and health regeneration.
Backend (Python with Pygame):
game.py: Python implementation with similar mechanics using Pygame library. Handles events, draws to screen, manages game objects, and includes the ship selection UI.

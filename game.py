import pygame
import random
import math
import sys

# Initialize pygame
pygame.init()

# Game constants
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (231, 76, 60)
GREEN = (46, 204, 113)
BLUE = (52, 152, 219)
YELLOW = (241, 196, 15)
ORANGE = (243, 156, 18)

# Game settings
ENEMY_POINTS = 100
LEVEL_UP_SCORE = 1000
DOUBLE_BULLETS_LEVEL = 3

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()

# Load fonts
try:
    font_small = pygame.font.SysFont('arial', 16)
    font_medium = pygame.font.SysFont('arial', 24)
    font_large = pygame.font.SysFont('arial', 48)
except:
    # Fallback if font not available
    font_small = pygame.font.Font(None, 16)
    font_medium = pygame.font.Font(None, 24)
    font_large = pygame.font.Font(None, 48)

# Global variables
score = 0
level = 1

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.random() * 2 + 0.5
        self.speed = random.random() * 0.5 + 0.1
        self.brightness = random.randint(205, 255)  # 205-255 for bright stars
        
    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)
            
    def draw(self, surface):
        pygame.draw.circle(surface, (self.brightness, self.brightness, self.brightness), 
                          (int(self.x), int(self.y)), int(self.size))

class Player:
    def __init__(self, ship_type='fighter'):
        self.width = 50
        self.height = 50
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - self.height - 30
        
        # Set ship properties based on type
        if ship_type == 'scout':
            self.speed = 7
            self.max_health = 180  # Increased from 80 to 180
            self.damage = 8
            self.regen_rate = 0.8
            self.color = GREEN
        elif ship_type == 'tank':
            self.speed = 3
            self.max_health = 250  # Increased from 150 to 250
            self.damage = 15
            self.regen_rate = 1.2
            self.color = RED
        else:  # fighter or default
            self.speed = 5
            self.max_health = 200  # Increased from 100 to 200
            self.damage = 10
            self.regen_rate = 1
            self.color = BLUE
            
        self.health = self.max_health
        self.last_regen = pygame.time.get_ticks()
        self.regen_interval = 1000  # milliseconds
        self.double_bullets = False
        self.invulnerable = False
        self.invulnerable_time = 0
        self.invulnerable_duration = 1000  # milliseconds
        self.ship_type = ship_type

    def update(self, keys, current_time):
        # Movement
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.x > 0:
            self.x -= self.speed
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.x < WIDTH - self.width:
            self.x += self.speed
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.y > 0:
            self.y -= self.speed
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.y < HEIGHT - self.height:
            self.y += self.speed

        # Health regeneration
        if current_time - self.last_regen > self.regen_interval:
            self.last_regen = current_time
            self.health = min(self.max_health, self.health + self.regen_rate)

        # Invulnerability check
        if self.invulnerable and current_time - self.invulnerable_time > self.invulnerable_duration:
            self.invulnerable = False

    def draw(self, surface):
        # Base color with invulnerability effect
        color = tuple(int(c * 0.5) for c in self.color) if self.invulnerable else self.color
        
        # Draw ship based on type
        if self.ship_type == 'scout':
            # Sleek, narrow ship
            pygame.draw.polygon(surface, color, [
                (self.x + self.width // 2, self.y),
                (self.x + self.width - 10, self.y + self.height),
                (self.x + 10, self.y + self.height)
            ])
            
            # Scout details
            pygame.draw.rect(surface, (39, 174, 96), 
                            (self.x + self.width // 2 - 3, self.y + 15, 6, 5))
            
        elif self.ship_type == 'tank':
            # Wide, bulky ship
            pygame.draw.polygon(surface, color, [
                (self.x + self.width // 2, self.y + 10),
                (self.x + self.width, self.y + self.height),
                (self.x, self.y + self.height)
            ])
            
            # Tank details
            pygame.draw.rect(surface, (192, 57, 43), 
                            (self.x + self.width // 2 - 10, self.y + 20, 20, 8))
            
        else:  # fighter or default
            # Standard balanced ship
            pygame.draw.polygon(surface, color, [
                (self.x + self.width // 2, self.y),
                (self.x + self.width, self.y + self.height),
                (self.x, self.y + self.height)
            ])
            
            # Fighter details
            pygame.draw.rect(surface, (41, 128, 185), 
                            (self.x + self.width // 2 - 5, self.y + 10, 10, 5))

        # Draw engine flames (common to all ships)
        pygame.draw.polygon(surface, ORANGE, [
            (self.x + 10, self.y + self.height),
            (self.x + 20, self.y + self.height + 15),
            (self.x + 30, self.y + self.height)
        ])

    def shoot(self, bullets):
        if self.double_bullets:
            # Double bullets
            bullets.append(Bullet(self.x + 10, self.y, self.damage))
            bullets.append(Bullet(self.x + self.width - 10, self.y, self.damage))
        else:
            # Single bullet
            bullets.append(Bullet(self.x + self.width // 2, self.y, self.damage))

    def take_damage(self, amount, particles):
        if not self.invulnerable:
            self.health -= amount
            self.invulnerable = True
            self.invulnerable_time = pygame.time.get_ticks()
            
            # Create damage particles
            for _ in range(10):
                particles.append(Particle(
                    self.x + self.width // 2,
                    self.y + self.height // 2,
                    random.random() * 2 + 1,
                    RED,
                    random.random() * 2 - 1,
                    random.random() * 2 - 1,
                    500
                ))
            
            return self.health <= 0
        return False

    def level_up(self):
        self.damage += 5
        self.regen_rate += 0.5
        
        # Enable double bullets at level 3
        global level
        if level >= DOUBLE_BULLETS_LEVEL and not self.double_bullets:
            self.double_bullets = True

class Bullet:
    def __init__(self, x, y, damage):
        self.x = x
        self.y = y
        self.width = 4
        self.height = 15
        self.speed = 10
        self.damage = damage
        self.color = YELLOW

    def update(self):
        self.y -= self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x - self.width // 2, self.y, self.width, self.height))
        
        # Create a glow effect (simplified)
        glow_surf = pygame.Surface((self.width + 6, self.height + 6), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*self.color, 100), (3, 3, self.width, self.height))
        surface.blit(glow_surf, (self.x - self.width // 2 - 3, self.y - 3))

class Enemy:
    def __init__(self, level):
        self.width = 40
        self.height = 40
        self.x = random.randint(0, WIDTH - self.width)
        self.y = -self.height
        self.speed = 2 + random.random() * level * 0.5
        self.health = 10 + level * 5
        self.max_health = self.health
        self.color = (
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255)
        )
        self.type = 'advanced' if random.random() > 0.7 else 'basic'
        self.angle = 0  # For sine wave movement

    def update(self):
        self.y += self.speed
        
        # Advanced enemies move in a sine wave pattern
        if self.type == 'advanced':
            self.angle += 0.1
            self.x += math.sin(self.angle) * 2
            
            # Keep within bounds
            if self.x < 0:
                self.x = 0
            if self.x > WIDTH - self.width:
                self.x = WIDTH - self.width

    def draw(self, surface):
        # Draw enemy ship based on type
        if self.type == 'advanced':
            # Advanced enemy design (diamond shape)
            pygame.draw.polygon(surface, self.color, [
                (self.x + self.width // 2, self.y),
                (self.x + self.width, self.y + self.height // 2),
                (self.x + self.width // 2, self.y + self.height),
                (self.x, self.y + self.height // 2)
            ])
            
            # Advanced enemy details
            pygame.draw.circle(surface, (255, 255, 255), 
                              (int(self.x + self.width // 2), int(self.y + self.height // 2)), 5)
        else:
            # Basic enemy design (triangle)
            pygame.draw.polygon(surface, self.color, [
                (self.x + self.width // 2, self.y + self.height),
                (self.x + self.width, self.y),
                (self.x, self.y)
            ])
        
        # Draw health bar
        health_percentage = self.health / self.max_health
        bar_width = self.width
        bar_height = 4
        
        pygame.draw.rect(surface, (50, 50, 50), (self.x, self.y - 10, bar_width, bar_height))
        
        bar_color = GREEN if health_percentage > 0.5 else RED
        pygame.draw.rect(surface, bar_color, (self.x, self.y - 10, int(bar_width * health_percentage), bar_height))

    def take_damage(self, amount, particles):
        self.health -= amount
        
        # Create hit particles
        for _ in range(5):
            particles.append(Particle(
                self.x + self.width // 2,
                self.y + self.height // 2,
                random.random() * 2 + 1,
                self.color,
                random.random() * 2 - 1,
                random.random() * 2 - 1,
                300
            ))
        
        return self.health <= 0

class Particle:
    def __init__(self, x, y, size, color, speed_x, speed_y, lifespan):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.lifespan = lifespan
        self.created_at = pygame.time.get_ticks()
        self.opacity = 255

    def update(self, current_time):
        self.x += self.speed_x
        self.y += self.speed_y
        
        # Calculate opacity based on remaining lifespan
        age = current_time - self.created_at
        self.opacity = 255 * (1 - (age / self.lifespan))
        
        return age < self.lifespan

    def draw(self, surface):
        if self.opacity > 0:
            # Create a surface with per-pixel alpha
            s = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
            # Draw the circle with alpha
            pygame.draw.circle(s, (*self.color, int(self.opacity)), (int(self.size), int(self.size)), int(self.size))
            # Blit the surface onto the screen
            surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))

def create_explosion(x, y, color, particles):
    # Create explosion particles
    for _ in range(30):
        angle = random.random() * math.pi * 2
        speed = random.random() * 3 + 1
        particles.append(Particle(
            x, y,
            random.random() * 3 + 1,
            color,
            math.cos(angle) * speed,
            math.sin(angle) * speed,
            1000
        ))

def draw_text(surface, text, font, color, x, y, align="left"):
    text_surface = font.render(str(text), True, color)
    text_rect = text_surface.get_rect()
    
    if align == "center":
        text_rect.centerx = x
        text_rect.y = y
    elif align == "right":
        text_rect.right = x
        text_rect.y = y
    else:  # left
        text_rect.x = x
        text_rect.y = y
        
    surface.blit(text_surface, text_rect)

def draw_health_bar(surface, x, y, width, height, value, max_value):
    # Background
    pygame.draw.rect(surface, (50, 50, 50), (x, y, width, height))
    
    # Health fill
    health_percentage = value / max_value
    fill_width = int(width * health_percentage)
    
    if health_percentage > 0.5:
        color = GREEN
    elif health_percentage > 0.25:
        color = ORANGE
    else:
        color = RED
        
    pygame.draw.rect(surface, color, (x, y, fill_width, height))
    
    # Health text
    health_text = f"{int(value)}/{max_value}"
    draw_text(surface, health_text, font_small, WHITE, x + width // 2, y + height // 2 - 8, "center")

def check_collisions(player, bullets, enemies, particles):
    global score, level
    game_over = False
    
    # Bullet-enemy collisions
    bullets_to_remove = []
    enemies_to_remove = []
    
    for bullet_idx, bullet in enumerate(bullets):
        for enemy_idx, enemy in enumerate(enemies):
            if (bullet.x + bullet.width // 2 > enemy.x and
                bullet.x - bullet.width // 2 < enemy.x + enemy.width and
                bullet.y < enemy.y + enemy.height and
                bullet.y + bullet.height > enemy.y):
                
                # Enemy hit by bullet
                if enemy.take_damage(bullet.damage, particles):
                    # Enemy destroyed
                    create_explosion(enemy.x + enemy.width // 2, enemy.y + enemy.height // 2, enemy.color, particles)
                    enemies_to_remove.append(enemy_idx)
                    
                    # Add score
                    score += ENEMY_POINTS
                    
                    # Check for level up
                    if score >= level * LEVEL_UP_SCORE:
                        level_up(player)
                
                # Mark bullet for removal
                if bullet_idx not in bullets_to_remove:
                    bullets_to_remove.append(bullet_idx)
                break
    
    # Remove bullets and enemies (in reverse order to avoid index issues)
    for idx in sorted(bullets_to_remove, reverse=True):
        if idx < len(bullets):
            bullets.pop(idx)
            
    for idx in sorted(enemies_to_remove, reverse=True):
        if idx < len(enemies):
            enemies.pop(idx)
    
    # Player-enemy collisions
    enemies_to_remove = []
    for enemy_idx, enemy in enumerate(enemies):
        if (player.x < enemy.x + enemy.width and
            player.x + player.width > enemy.x and
            player.y < enemy.y + enemy.height and
            player.y + player.height > enemy.y):
            
            # Player hit by enemy
            game_over = player.take_damage(20, particles)
            create_explosion(enemy.x + enemy.width // 2, enemy.y + enemy.height // 2, enemy.color, particles)
            enemies_to_remove.append(enemy_idx)
    
    # Remove enemies that collided with player
    for idx in sorted(enemies_to_remove, reverse=True):
        if idx < len(enemies):
            enemies.pop(idx)
            
    return game_over

def level_up(player):
    global level
    level += 1
    player.level_up()

def create_stars():
    stars = []
    for _ in range(150):
        stars.append(Star())
    return stars

def show_ship_selection(surface):
    """Show ship selection screen and return the selected ship type"""
    # Ship options
    ships = [
        {
            'type': 'fighter',
            'name': 'Fighter',
            'desc': 'Balanced',
            'color': BLUE,
            'stats': {
                'speed': 3,
                'health': 3,
                'damage': 3
            }
        },
        {
            'type': 'scout',
            'name': 'Scout',
            'desc': 'Fast & Agile',
            'color': GREEN,
            'stats': {
                'speed': 5,
                'health': 2,
                'damage': 2
            }
        },
        {
            'type': 'tank',
            'name': 'Tank',
            'desc': 'Heavy & Powerful',
            'color': RED,
            'stats': {
                'speed': 2,
                'health': 5,
                'damage': 4
            }
        }
    ]
    
    selected_index = 0
    
    # Create stars for background
    stars = create_stars()
    
    selecting = True
    while selecting:
        current_time = pygame.time.get_ticks()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected_index = (selected_index - 1) % len(ships)
                elif event.key == pygame.K_RIGHT:
                    selected_index = (selected_index + 1) % len(ships)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    selecting = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        
        # Draw background
        surface.fill(BLACK)
        
        # Draw stars
        for star in stars:
            star.update()
            star.draw(surface)
        
        # Draw title
        draw_text(surface, "SELECT YOUR SHIP", font_large, BLUE, WIDTH // 2, 50, "center")
        
        # Draw instructions
        draw_text(surface, "← → to select, SPACE to confirm", font_medium, WHITE, WIDTH // 2, HEIGHT - 50, "center")
        
        # Draw ship options
        ship_width = 180
        total_width = len(ships) * ship_width
        start_x = (WIDTH - total_width) // 2
        
        for i, ship in enumerate(ships):
            x = start_x + i * ship_width
            y = HEIGHT // 2 - 100
            
            # Draw selection box
            box_color = (100, 100, 100)
            if i == selected_index:
                box_color = (200, 200, 100)
            
            pygame.draw.rect(surface, box_color, (x, y, ship_width, 200), 0, 10)
            pygame.draw.rect(surface, ship['color'], (x, y, ship_width, 200), 3, 10)
            
            # Draw ship name
            draw_text(surface, ship['name'], font_medium, WHITE, x + ship_width // 2, y + 20, "center")
            
            # Draw ship description
            draw_text(surface, ship['desc'], font_small, (200, 200, 200), x + ship_width // 2, y + 50, "center")
            
            # Draw ship preview
            ship_preview_y = y + 80
            if ship['type'] == 'fighter':
                pygame.draw.polygon(surface, ship['color'], [
                    (x + ship_width // 2, ship_preview_y),
                    (x + ship_width // 2 + 25, ship_preview_y + 50),
                    (x + ship_width // 2 - 25, ship_preview_y + 50)
                ])
            elif ship['type'] == 'scout':
                pygame.draw.polygon(surface, ship['color'], [
                    (x + ship_width // 2, ship_preview_y),
                    (x + ship_width // 2 + 15, ship_preview_y + 60),
                    (x + ship_width // 2 - 15, ship_preview_y + 60)
                ])
            elif ship['type'] == 'tank':
                pygame.draw.polygon(surface, ship['color'], [
                    (x + ship_width // 2, ship_preview_y + 10),
                    (x + ship_width // 2 + 30, ship_preview_y + 50),
                    (x + ship_width // 2 - 30, ship_preview_y + 50)
                ])
            
            # Draw stats
            stat_y = y + 140
            for j, (stat_name, stat_value) in enumerate(ship['stats'].items()):
                draw_text(surface, f"{stat_name.capitalize()}: ", font_small, WHITE, x + 20, stat_y + j * 20, "left")
                
                # Draw stat bars
                for k in range(5):
                    bar_color = ship['color'] if k < stat_value else (50, 50, 50)
                    pygame.draw.rect(surface, bar_color, (x + 80 + k * 15, stat_y + j * 20, 10, 10))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    return ships[selected_index]['type']

def show_start_screen(surface):
    surface.fill(BLACK)
    
    # Create stars for background
    stars = create_stars()
    
    # Title
    draw_text(surface, "SPACE SHOOTER", font_large, BLUE, WIDTH // 2, HEIGHT // 3, "center")
    
    # Instructions
    draw_text(surface, "Use arrow keys or WASD to move", font_medium, WHITE, WIDTH // 2, HEIGHT // 2, "center")
    draw_text(surface, "Space to shoot (hold for auto-fire)", font_medium, WHITE, WIDTH // 2, HEIGHT // 2 + 40, "center")
    
    # Start prompt
    draw_text(surface, "Press SPACE to continue", font_medium, YELLOW, WIDTH // 2, HEIGHT * 3 // 4, "center")
    
    pygame.display.flip()
    
    # Wait for player to press space
    waiting = True
    while waiting:
        current_time = pygame.time.get_ticks()
        
        # Update and draw stars
        surface.fill(BLACK)
        for star in stars:
            star.update()
            star.draw(surface)
            
        # Redraw text
        draw_text(surface, "SPACE SHOOTER", font_large, BLUE, WIDTH // 2, HEIGHT // 3, "center")
        draw_text(surface, "Use arrow keys or WASD to move", font_medium, WHITE, WIDTH // 2, HEIGHT // 2, "center")
        draw_text(surface, "Space to shoot (hold for auto-fire)", font_medium, WHITE, WIDTH // 2, HEIGHT // 2 + 40, "center")
        draw_text(surface, "Press SPACE to continue", font_medium, YELLOW, WIDTH // 2, HEIGHT * 3 // 4, "center")
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                    
        clock.tick(FPS)

def show_game_over_screen(surface):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surface.blit(overlay, (0, 0))
    
    # Game Over text
    draw_text(surface, "GAME OVER", font_large, RED, WIDTH // 2, HEIGHT // 3, "center")
    
    # Score
    draw_text(surface, f"Final Score: {score}", font_medium, WHITE, WIDTH // 2, HEIGHT // 2, "center")
    
    # Restart prompt
    draw_text(surface, "Press SPACE to play again", font_medium, YELLOW, WIDTH // 2, HEIGHT * 3 // 4, "center")
    
    pygame.display.flip()
    
    # Wait for player to press space
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def main():
    global score, level
    
    # Show start screen
    show_start_screen(screen)
    
    # Game loop
    running = True
    
    while running:
        # Ship selection
        ship_type = show_ship_selection(screen)
        
        # Initialize game
        player = Player(ship_type)
        bullets = []
        enemies = []
        particles = []
        stars = create_stars()
        score = 0
        level = 1
        last_enemy_spawn = 0
        enemy_spawn_interval = 1500  # milliseconds
        last_shot = 0
        shoot_interval = 150  # milliseconds (decreased from 300 to 150 for faster shooting)
        auto_fire = False
        game_over = False
        
        # Game loop
        while running and not game_over:
            current_time = pygame.time.get_ticks()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        auto_fire = True
                        player.shoot(bullets)
                        last_shot = current_time
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        auto_fire = False
            
            # Get pressed keys
            keys = pygame.key.get_pressed()
            
            # Auto-fire
            if auto_fire and current_time - last_shot > shoot_interval:
                player.shoot(bullets)
                last_shot = current_time
            
            # Update player
            player.update(keys, current_time)
            
            # Update bullets
            for bullet in bullets[:]:
                bullet.update()
                if bullet.y < -bullet.height:
                    bullets.remove(bullet)
            
            # Spawn enemies
            if current_time - last_enemy_spawn > enemy_spawn_interval:
                last_enemy_spawn = current_time
                enemies.append(Enemy(level))
                
                # Adjust spawn rate based on level
                enemy_spawn_interval = max(300, 1500 - level * 100)
            
            # Update enemies
            for enemy in enemies[:]:
                enemy.update()
                if enemy.y > HEIGHT:
                    enemies.remove(enemy)
            
            # Update stars
            for star in stars:
                star.update()
            
            # Update particles
            for particle in particles[:]:
                if not particle.update(current_time):
                    particles.remove(particle)
            
            # Check collisions
            game_over = check_collisions(player, bullets, enemies, particles)
            
            # Draw everything
            screen.fill(BLACK)
            
            # Draw stars (background)
            for star in stars:
                star.draw(screen)
            
            # Draw particles (behind everything)
            for particle in particles:
                particle.draw(screen)
            
            # Draw bullets
            for bullet in bullets:
                bullet.draw(screen)
            
            # Draw enemies
            for enemy in enemies:
                enemy.draw(screen)
            
            # Draw player
            player.draw(screen)
            
            # Draw HUD
            # Health bar
            draw_health_bar(screen, 10, 10, 200, 20, player.health, player.max_health)
            
            # Score and level
            draw_text(screen, f"Score: {score}", font_small, WHITE, WIDTH // 2, 15, "center")
            draw_text(screen, f"Level: {level}", font_small, WHITE, WIDTH // 2, 35, "center")
            
            # Upgrades
            bullet_type = "Double" if player.double_bullets else "Single"
            draw_text(screen, f"Bullets: {bullet_type}", font_small, WHITE, WIDTH - 10, 15, "right")
            draw_text(screen, f"Damage: {player.damage}", font_small, WHITE, WIDTH - 10, 35, "right")
            draw_text(screen, f"Regen: {player.regen_rate:.1f} HP/s", font_small, WHITE, WIDTH - 10, 55, "right")
            
            # Update display
            pygame.display.flip()
            
            # Cap the frame rate
            clock.tick(FPS)
        
        # Show game over screen
        if game_over:
            show_game_over_screen(screen)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

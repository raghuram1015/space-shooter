// Game canvas setup
const canvas = document.getElementById("gameCanvas")
const ctx = canvas.getContext("2d")
canvas.width = 800
canvas.height = 600

// Game elements
let player
let bullets = []
let enemies = []
let particles = []
let stars = []
let gameActive = false
let score = 0
let level = 1
let lastEnemySpawn = 0
let enemySpawnInterval = 1500 // milliseconds
let lastTime = 0
let lastShot = 0
const shootInterval = 150 // milliseconds (decreased from 300 to 150 for faster shooting)
let autoFire = false
let selectedShipType = "fighter" // Default ship

// DOM elements
const gameOverScreen = document.getElementById("gameOver")
const startScreen = document.getElementById("startScreen")
const finalScoreElement = document.getElementById("finalScore")
const scoreElement = document.getElementById("score")
const levelElement = document.getElementById("level")
const bulletTypeElement = document.getElementById("bullet-type")
const damageElement = document.getElementById("damage")
const regenElement = document.getElementById("regen")
const healthFill = document.querySelector(".health-fill")
const healthText = document.querySelector(".health-text")
const shipOptions = document.querySelectorAll(".ship-option")

// Game settings
const ENEMY_POINTS = 100
const LEVEL_UP_SCORE = 1000
const DOUBLE_BULLETS_LEVEL = 3

// Ship selection
shipOptions.forEach((option) => {
  option.addEventListener("click", () => {
    // Remove selected class from all options
    shipOptions.forEach((opt) => opt.classList.remove("selected"))
    // Add selected class to clicked option
    option.classList.add("selected")
    // Set selected ship type
    selectedShipType = option.getAttribute("data-ship")
  })
})

// Star class for background
class Star {
  constructor() {
    this.x = Math.random() * canvas.width
    this.y = Math.random() * canvas.height
    this.size = Math.random() * 2 + 0.5
    this.speed = Math.random() * 0.5 + 0.1
    this.brightness = Math.random() * 50 + 205 // 205-255 for bright stars
  }

  update() {
    this.y += this.speed
    if (this.y > canvas.height) {
      this.y = 0
      this.x = Math.random() * canvas.width
    }
  }

  draw() {
    ctx.fillStyle = `rgb(${this.brightness}, ${this.brightness}, ${this.brightness})`
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
    ctx.fill()
  }
}

// Player class
class Player {
  constructor(shipType) {
    this.width = 50
    this.height = 50
    this.x = canvas.width / 2 - this.width / 2
    this.y = canvas.height - this.height - 30

    // Set ship properties based on type
    switch (shipType) {
      case "scout":
        this.speed = 7
        this.maxHealth = 180 // Increased from 80 to 180
        this.damage = 8
        this.regenRate = 0.8
        this.color = "#2ecc71" // Green
        break
      case "tank":
        this.speed = 3
        this.maxHealth = 250 // Increased from 150 to 250
        this.damage = 15
        this.regenRate = 1.2
        this.color = "#e74c3c" // Red
        break
      case "fighter":
      default:
        this.speed = 5
        this.maxHealth = 200 // Increased from 100 to 200
        this.damage = 10
        this.regenRate = 1
        this.color = "#3498db" // Blue
        break
    }

    this.health = this.maxHealth
    this.lastRegen = 0
    this.regenInterval = 1000 // milliseconds
    this.doubleBullets = false
    this.invulnerable = false
    this.invulnerableTime = 0
    this.invulnerableDuration = 1000 // milliseconds
    this.shipType = shipType
  }

  update(keys, currentTime) {
    // Movement
    if ((keys.ArrowLeft || keys.a) && this.x > 0) {
      this.x -= this.speed
    }
    if ((keys.ArrowRight || keys.d) && this.x < canvas.width - this.width) {
      this.x += this.speed
    }
    if ((keys.ArrowUp || keys.w) && this.y > 0) {
      this.y -= this.speed
    }
    if ((keys.ArrowDown || keys.s) && this.y < canvas.height - this.height) {
      this.y += this.speed
    }

    // Health regeneration
    if (currentTime - this.lastRegen > this.regenInterval) {
      this.lastRegen = currentTime
      this.health = Math.min(this.maxHealth, this.health + this.regenRate)
      updateHealthBar()
    }

    // Invulnerability check
    if (this.invulnerable && currentTime - this.invulnerableTime > this.invulnerableDuration) {
      this.invulnerable = false
    }

    // Auto-fire
    if (autoFire && currentTime - lastShot > shootInterval) {
      this.shoot()
      lastShot = currentTime
    }
  }

  draw() {
    // Base color with invulnerability effect
    const shipColor = this.invulnerable ? `rgba(${this.getRGBFromHex(this.color).join(",")}, 0.5)` : this.color

    // Draw ship based on type
    ctx.fillStyle = shipColor

    switch (this.shipType) {
      case "scout":
        // Sleek, narrow ship
        ctx.beginPath()
        ctx.moveTo(this.x + this.width / 2, this.y)
        ctx.lineTo(this.x + this.width - 10, this.y + this.height)
        ctx.lineTo(this.x + 10, this.y + this.height)
        ctx.closePath()
        ctx.fill()

        // Scout details
        ctx.fillStyle = "#27ae60"
        ctx.fillRect(this.x + this.width / 2 - 3, this.y + 15, 6, 5)
        break

      case "tank":
        // Wide, bulky ship
        ctx.beginPath()
        ctx.moveTo(this.x + this.width / 2, this.y + 10)
        ctx.lineTo(this.x + this.width, this.y + this.height)
        ctx.lineTo(this.x, this.y + this.height)
        ctx.closePath()
        ctx.fill()

        // Tank details
        ctx.fillStyle = "#c0392b"
        ctx.fillRect(this.x + this.width / 2 - 10, this.y + 20, 20, 8)
        break

      case "fighter":
      default:
        // Standard balanced ship
        ctx.beginPath()
        ctx.moveTo(this.x + this.width / 2, this.y)
        ctx.lineTo(this.x + this.width, this.y + this.height)
        ctx.lineTo(this.x, this.y + this.height)
        ctx.closePath()
        ctx.fill()

        // Fighter details
        ctx.fillStyle = "#2980b9"
        ctx.fillRect(this.x + this.width / 2 - 5, this.y + 10, 10, 5)
        break
    }

    // Draw engine flames (common to all ships)
    ctx.fillStyle = "#f39c12"
    ctx.beginPath()
    ctx.moveTo(this.x + 10, this.y + this.height)
    ctx.lineTo(this.x + 20, this.y + this.height + 15)
    ctx.lineTo(this.x + 30, this.y + this.height)
    ctx.closePath()
    ctx.fill()
  }

  // Helper function to convert hex color to RGB
  getRGBFromHex(hex) {
    // Default to blue if hex is invalid
    if (!hex || hex.length !== 7) {
      return [52, 152, 219] // Default blue
    }

    try {
      const r = Number.parseInt(hex.slice(1, 3), 16)
      const g = Number.parseInt(hex.slice(3, 5), 16)
      const b = Number.parseInt(hex.slice(5, 7), 16)
      return [r, g, b]
    } catch (e) {
      return [52, 152, 219] // Default blue on error
    }
  }

  shoot() {
    if (this.doubleBullets) {
      // Double bullets
      bullets.push(new Bullet(this.x + 10, this.y, this.damage))
      bullets.push(new Bullet(this.x + this.width - 10, this.y, this.damage))
    } else {
      // Single bullet
      bullets.push(new Bullet(this.x + this.width / 2, this.y, this.damage))
    }
  }

  takeDamage(amount) {
    if (!this.invulnerable) {
      this.health -= amount
      this.invulnerable = true
      this.invulnerableTime = performance.now()
      updateHealthBar()

      // Create damage particles
      for (let i = 0; i < 10; i++) {
        particles.push(
          new Particle(
            this.x + this.width / 2,
            this.y + this.height / 2,
            Math.random() * 2 + 1,
            "#e74c3c",
            Math.random() * 2 - 1,
            Math.random() * 2 - 1,
            500,
          ),
        )
      }

      if (this.health <= 0) {
        gameOver()
      }
    }
  }

  levelUp() {
    this.damage += 5
    this.regenRate += 0.5

    // Enable double bullets at level 3
    if (level >= DOUBLE_BULLETS_LEVEL && !this.doubleBullets) {
      this.doubleBullets = true
      bulletTypeElement.textContent = "Double"
    }

    // Update UI
    damageElement.textContent = this.damage
    regenElement.textContent = this.regenRate.toFixed(1)
  }
}

// Bullet class
class Bullet {
  constructor(x, y, damage) {
    this.x = x
    this.y = y
    this.width = 4
    this.height = 15
    this.speed = 10
    this.damage = damage
    this.color = "#f1c40f"
  }

  update() {
    this.y -= this.speed
  }

  draw() {
    ctx.fillStyle = this.color
    ctx.fillRect(this.x - this.width / 2, this.y, this.width, this.height)

    // Bullet glow
    ctx.shadowColor = this.color
    ctx.shadowBlur = 10
    ctx.fillRect(this.x - this.width / 2, this.y, this.width, this.height)
    ctx.shadowBlur = 0
  }
}

// Enemy class
class Enemy {
  constructor() {
    this.width = 40
    this.height = 40
    this.x = Math.random() * (canvas.width - this.width)
    this.y = -this.height
    this.speed = 2 + Math.random() * level * 0.5
    this.health = 10 + level * 5
    this.maxHealth = this.health
    this.color = `hsl(${Math.random() * 360}, 70%, 50%)`
    this.type = Math.random() > 0.7 ? "advanced" : "basic"
    this.angle = 0 // For sine wave movement
  }

  update() {
    this.y += this.speed

    // Advanced enemies move in a sine wave pattern
    if (this.type === "advanced") {
      this.angle += 0.1
      this.x += Math.sin(this.angle) * 2

      // Keep within bounds
      if (this.x < 0) this.x = 0
      if (this.x > canvas.width - this.width) this.x = canvas.width - this.width
    }
  }

  draw() {
    // Draw enemy ship
    ctx.fillStyle = this.color

    if (this.type === "advanced") {
      // Advanced enemy design
      ctx.beginPath()
      ctx.moveTo(this.x + this.width / 2, this.y)
      ctx.lineTo(this.x + this.width, this.y + this.height / 2)
      ctx.lineTo(this.x + this.width / 2, this.y + this.height)
      ctx.lineTo(this.x, this.y + this.height / 2)
      ctx.closePath()
      ctx.fill()

      // Advanced enemy details
      ctx.fillStyle = "rgba(255, 255, 255, 0.7)"
      ctx.beginPath()
      ctx.arc(this.x + this.width / 2, this.y + this.height / 2, 5, 0, Math.PI * 2)
      ctx.fill()
    } else {
      // Basic enemy design
      ctx.beginPath()
      ctx.moveTo(this.x + this.width / 2, this.y + this.height)
      ctx.lineTo(this.x + this.width, this.y)
      ctx.lineTo(this.x, this.y)
      ctx.closePath()
      ctx.fill()
    }

    // Draw health bar
    const healthPercentage = this.health / this.maxHealth
    const barWidth = this.width
    const barHeight = 4

    ctx.fillStyle = "rgba(0, 0, 0, 0.5)"
    ctx.fillRect(this.x, this.y - 10, barWidth, barHeight)

    ctx.fillStyle = healthPercentage > 0.5 ? "#2ecc71" : "#e74c3c"
    ctx.fillRect(this.x, this.y - 10, barWidth * healthPercentage, barHeight)
  }

  takeDamage(amount) {
    this.health -= amount

    // Create hit particles
    for (let i = 0; i < 5; i++) {
      particles.push(
        new Particle(
          this.x + this.width / 2,
          this.y + this.height / 2,
          Math.random() * 2 + 1,
          this.color,
          Math.random() * 2 - 1,
          Math.random() * 2 - 1,
          300,
        ),
      )
    }

    return this.health <= 0
  }
}

// Particle class for visual effects
class Particle {
  constructor(x, y, size, color, speedX, speedY, lifespan) {
    this.x = x
    this.y = y
    this.size = size
    this.color = color
    this.speedX = speedX
    this.speedY = speedY
    this.lifespan = lifespan
    this.createdAt = performance.now()
    this.opacity = 1
  }

  update(currentTime) {
    this.x += this.speedX
    this.y += this.speedY

    // Calculate opacity based on remaining lifespan
    const age = currentTime - this.createdAt
    this.opacity = 1 - age / this.lifespan

    return age < this.lifespan
  }

  draw() {
    ctx.fillStyle = this.color
    ctx.globalAlpha = this.opacity
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
    ctx.fill()
    ctx.globalAlpha = 1
  }
}

// Input handling
const keys = {}
window.addEventListener("keydown", (e) => {
  keys[e.key] = true

  // Shoot on space
  if (e.key === " " && gameActive) {
    if (!autoFire) {
      player.shoot()
      lastShot = performance.now()
    }
    autoFire = true
  }
})

window.addEventListener("keyup", (e) => {
  keys[e.key] = false

  // Stop auto-fire when space is released
  if (e.key === " ") {
    autoFire = false
  }
})

// Game functions
function updateHealthBar() {
  const healthPercentage = (player.health / player.maxHealth) * 100
  healthFill.style.width = `${healthPercentage}%`
  healthText.textContent = `${Math.ceil(player.health)}/${player.maxHealth}`

  // Change color based on health
  if (healthPercentage > 50) {
    healthFill.style.backgroundColor = "#2ecc71"
  } else if (healthPercentage > 25) {
    healthFill.style.backgroundColor = "#f39c12"
  } else {
    healthFill.style.backgroundColor = "#e74c3c"
  }
}

function checkCollisions() {
  // Bullet-enemy collisions
  for (let bulletIndex = bullets.length - 1; bulletIndex >= 0; bulletIndex--) {
    const bullet = bullets[bulletIndex]
    let bulletHit = false

    for (let enemyIndex = enemies.length - 1; enemyIndex >= 0; enemyIndex--) {
      const enemy = enemies[enemyIndex]

      if (
        bullet.x + bullet.width / 2 > enemy.x &&
        bullet.x - bullet.width / 2 < enemy.x + enemy.width &&
        bullet.y < enemy.y + enemy.height &&
        bullet.y + bullet.height > enemy.y
      ) {
        // Enemy hit by bullet
        if (enemy.takeDamage(bullet.damage)) {
          // Enemy destroyed
          createExplosion(enemy.x + enemy.width / 2, enemy.y + enemy.height / 2, enemy.color)
          enemies.splice(enemyIndex, 1)

          // Add score
          score += ENEMY_POINTS
          scoreElement.textContent = score

          // Check for level up
          if (score >= level * LEVEL_UP_SCORE) {
            levelUp()
          }
        }

        // Mark bullet as hit
        bulletHit = true
        break
      }
    }

    // Remove bullet if it hit something
    if (bulletHit) {
      bullets.splice(bulletIndex, 1)
    }
  }

  // Player-enemy collisions
  for (let i = enemies.length - 1; i >= 0; i--) {
    const enemy = enemies[i]

    if (
      player.x < enemy.x + enemy.width &&
      player.x + player.width > enemy.x &&
      player.y < enemy.y + enemy.height &&
      player.y + player.height > enemy.y
    ) {
      // Player hit by enemy
      player.takeDamage(20)
      createExplosion(enemy.x + enemy.width / 2, enemy.y + enemy.height / 2, enemy.color)
      enemies.splice(i, 1)
    }
  }
}

function createExplosion(x, y, color) {
  // Create explosion particles
  for (let i = 0; i < 30; i++) {
    const angle = Math.random() * Math.PI * 2
    const speed = Math.random() * 3 + 1
    particles.push(
      new Particle(x, y, Math.random() * 3 + 1, color, Math.cos(angle) * speed, Math.sin(angle) * speed, 1000),
    )
  }
}

function levelUp() {
  level++
  levelElement.textContent = level
  player.levelUp()

  // Increase difficulty
  enemySpawnInterval = Math.max(300, 1500 - level * 100)
}

function gameOver() {
  gameActive = false
  finalScoreElement.textContent = score
  gameOverScreen.classList.remove("hidden")
}

function createStars() {
  // Create a starfield
  stars = []
  for (let i = 0; i < 150; i++) {
    stars.push(new Star())
  }
}

function startGame() {
  // Reset game state
  player = new Player(selectedShipType)
  bullets = []
  enemies = []
  particles = []
  stars = []
  score = 0
  level = 1
  lastEnemySpawn = 0

  // Create stars for background
  createStars()

  // Reset UI
  scoreElement.textContent = score
  levelElement.textContent = level
  bulletTypeElement.textContent = "Single"
  damageElement.textContent = player.damage
  regenElement.textContent = player.regenRate.toFixed(1)
  updateHealthBar()

  // Hide screens
  startScreen.classList.add("hidden")
  gameOverScreen.classList.add("hidden")

  // Start game
  gameActive = true
  requestAnimationFrame(gameLoop)
}

// Game loop
function gameLoop(timestamp) {
  // Calculate delta time
  const deltaTime = timestamp - lastTime
  lastTime = timestamp

  // Clear canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height)

  if (gameActive) {
    // Update and draw stars (background)
    stars.forEach((star) => {
      star.update()
      star.draw()
    })

    // Update player
    player.update(keys, timestamp)

    // Update bullets
    bullets = bullets.filter((bullet) => {
      bullet.update()
      bullet.draw()
      return bullet.y > -bullet.height
    })

    // Spawn enemies
    if (timestamp - lastEnemySpawn > enemySpawnInterval) {
      lastEnemySpawn = timestamp
      enemies.push(new Enemy())
    }

    // Update enemies
    enemies = enemies.filter((enemy) => {
      enemy.update()
      enemy.draw()
      return enemy.y < canvas.height
    })

    // Update particles
    particles = particles.filter((particle) => {
      const alive = particle.update(timestamp)
      if (alive) particle.draw()
      return alive
    })

    // Check collisions
    checkCollisions()

    // Draw player
    player.draw()

    // Continue game loop
    requestAnimationFrame(gameLoop)
  }
}

// Event listeners for buttons
document.getElementById("startButton").addEventListener("click", startGame)
document.getElementById("restartButton").addEventListener("click", startGame)

// Initialize game
function init() {
  createStars()
  startScreen.classList.remove("hidden")
  gameOverScreen.classList.add("hidden")
}

// Start the game
init()

<div align="center">

# 🎄 The Last Christmas Run 🎄

  ![Python](https://img.shields.io/badge/Python-3.7%2B-3776AB?logo=python&logoColor=white)
  ![Pygame](https://img.shields.io/badge/Pygame-2.5%2B-4B8BBE?logo=pygame&logoColor=white)
  ![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-5C3EE8?logo=opencv&logoColor=white)
  ![NumPy](https://img.shields.io/badge/NumPy-1.24%2B-013243?logo=numpy&logoColor=white)
  ![CSV](https://img.shields.io/badge/data-CSV-orange)
  ![JSON](https://img.shields.io/badge/config-JSON-lightgrey)
  ![Random](https://img.shields.io/badge/library-Random-blue)
  ![Math](https://img.shields.io/badge/library-Math-yellow)
  ![2D Platformer](https://img.shields.io/badge/genre-2D%20Platformer-9cf)
  ![Boss Battles](https://img.shields.io/badge/feature-Boss%20Battles-red)
  ![Particle System](https://img.shields.io/badge/effect-Particle%20System-blue)
  ![Sprite Animation](https://img.shields.io/badge/feature-Sprite%20Animation-ff69b4)
  ![APU](https://img.shields.io/badge/University-Asia%20Pacific%20University-critical)
  ![Windows](https://img.shields.io/badge/Windows-0078D6?logo=windows&logoColor=white)
  ![macOS](https://img.shields.io/badge/macOS-000000?logo=apple&logoColor=white)
  ![Linux](https://img.shields.io/badge/Linux-FCC624?logo=linux&logoColor=black)

**A festive 2D platformer engineered with advanced procedural graphics, custom particle physics, and exciting boss battles.**



</div>

---

## 📖 Overview

**The Last Christmas Run** is a side-scrolling 2D platformer built entirely with **Pygame**. Take control of Santa Claus as he runs, jumps, and fights through increasingly challenging levels filled with enemies, hazards, puzzles, and powerful bosses.

Collect presents to unlock gates, activate checkpoints, survive deadly blizzards, and defeat the fearsome **Ice Golem** to save Christmas!

---

## ✨ Key Features

- **Smooth Platforming** – Responsive running, jumping, and shooting
- **Ice Physics** – Ice tiles that affect movement dynamics
- **Dynamic Hazards** – Cannons, spikes, and environmental dangers
- **Power-up System** – Health, jump boosts, and shields
- **Boss Battles** – Multi-phase Ice Golem encounters
- **Blizzard Storms** – Weather hazards that reduce visibility
- **Cinematic Sequences** – Boss intros and defeat scenes
- **Checkpoint System** – Save progress and respawn safely
- **Gift Collection** – Unlock gates by collecting presents

### 🌟 Advanced Special Effects Engineering
- **Procedural Screen Effects**: Real-time Pythagorean distance calculations render dynamic frost and damage vignettes without image assets.
- **Additive Blending (`BLEND_RGBA_ADD`)**: Core powerup glows and player auras use Linear Dodge blending to physically illuminate the screen.
- **Volumetric Parallax Fog**: The blizzard system uses Z-Depth sorting to categorize smoke into 3 parallax layers, faking volumetric 3D weather.
- **Newtonian Kinematics & Ribbons**: Projectiles utilize trajectory history buffers for motion blur and calculate gravity/drag equations per frame.

---

## 🕹️ Gameplay & Controls

### Core Mechanics
- Run and jump across challenging platforms
- Shoot snowballs to defeat enemies
- Collect presents to unlock level gates
- Activate checkpoints to save progress
- Unlock **Ice Shards** special ability after the first boss

### Controls
| Key | Action |
|-----|-------|
| `A` / `D` or `←` / `→` | Move left / right |
| `Space` / `W` / `↑` | Jump |
| `Shift` | Run |
| `F` | Shoot snowballs |
| `Q` | Special ability (Ice Shards) |
| `1` | Activate Jump Boost |
| `2` | Activate Shield |
| `R` | Restart level |
| `F1` | Toggle debug info |

---

## ⚡ Power-ups

| Power-up | Effect | Duration |
|--------|--------|----------|
| ❤️ Health | Restore 100 HP | Instant |
| ⬆️ Jump Boost | Higher jump | 8 seconds |
| 🛡️ Shield | Invincibility | 8 seconds |

---

## 📁 Project Structure

```text
The-Last-Christmas-Run/
├── main.py
├── settings.py
├── player.py
├── player_effects.py
├── level.py
├── camera.py
├── hud.py
├── menu.py
├── sound_manager.py
├── cinematic.py
├── cinematic_outro.py
├── fireworks.py
│
├── enemies/
│   ├── enemy.py
│   ├── boss.py
│   ├── boss_slam.py
│   └── stone_ring.py
│
├── hazards/
│   ├── hazard.py
│   ├── blizzard.py
│   └── smoke.py
│
├── items/
│   ├── collectible.py
│   ├── powerup.py
│   ├── gate.py
│   └── checkpoint.py
│
├── projectiles/
│   ├── projectiles.py
│   └── moving_platform.py
│
├── tiles/
│   ├── tile.py
│   ├── tile_config.py
│   ├── tile_loader.py
│   └── tile_database.json
│
├── assets/
│   ├── ui/
│   ├── weapons/
│   ├── powerup/
│   ├── editor/
│   └── story/
│
├── sprites/
│   ├── player/
│   └── enemies/
│
├── sounds/
│   ├── music/
│   ├── player/
│   ├── hazard/
│   ├── boss/
│   ├── items/
│   ├── powerup/
│   ├── fireworks/
│   └── ui/
│
└── levels/
    ├── level0_data.csv
    ├── level1_data.csv
    └── ...
```

---

## 🚀 Installation

#### Prerequisites
- Python 3.7+
- pip

#### Setup
```bash
git clone https://github.com/Maneet7805/2D-Platform_Game.git
cd 2D-Platform_Game
pip install pygame opencv-python numpy
python main.py
```

---

## 🎨 Level Editor
The game includes a built-in level editor to create custom challenges.

### Run the Editor
```bash
python editor.py
```

### Editor Features
- Category-based tile selection
- Paint and erase tiles
- Scroll through large maps
- Save and load CSV levels
- Tile previews and visual indicators

### Creating Custom Levels
1. Select a tile category
2. Choose a tile
3. Paint on the grid
4. Save as `levelX_data.csv`
5. Add the file to `LEVEL_FILES` in `settings.py`

---

## ⚙️ Game Systems

### Physics Engine
- Gravity and jumping
- Ice friction mechanics
- Pixel-perfect collision
- Smooth acceleration

### Health System
- 100 HP base health
- Damage from hazards and enemies
- Invincibility frames
- Respawn at checkpoints

### Enemy AI
- Wolves with patrol logic
- Cannons with timed firing
- Ice Golem with complex attacks

### Audio System
- Positional sound effects
- Menu, level, and boss music
- Categorized SFX system
- Adjustable volume controls

### Cinematic System
- Boss introductions
- Boss defeat sequences
- Video playback support
- Dialogue boxes with speakers

---

## 🛠️ Troubleshooting

#### Game won’t start
- Install dependencies
- Verify asset folders exist

#### Missing sounds
- Game runs gracefully without sound files! 
- Add custom sound effects to `/sounds` if needed.

#### Editor errors
- Check `tiles/` directory
- Validate `tile_database.json`

---

## 👤 Author
**Maneet Arvind Mehta**  
GitHub: [https://github.com/Maneet7805](https://github.com/Maneet7805)

### Have Fun!
Save Christmas, defeat the Ice Golem, and enjoy the adventure!

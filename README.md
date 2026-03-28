<div align="center">

# The Last Christmas Run

  ![Python](https://img.shields.io/badge/Python-3.7%2B-3776AB?logo=python&logoColor=white)
  ![Pygame](https://img.shields.io/badge/Pygame-2.5%2B-4B8BBE?logo=pygame&logoColor=white)
  ![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-5C3EE8?logo=opencv&logoColor=white)
  ![NumPy](https://img.shields.io/badge/NumPy-1.24%2B-013243?logo=numpy&logoColor=white)
  ![CSV](https://img.shields.io/badge/data-CSV-orange)
  ![JSON](https://img.shields.io/badge/config-JSON-lightgrey)
  ![2D Platformer](https://img.shields.io/badge/genre-2D%20Platformer-9cf)
  ![Boss Battles](https://img.shields.io/badge/feature-Boss%20Battles-red)
  ![Particle System](https://img.shields.io/badge/effect-Particle%20System-blue)
  ![Sprite Animation](https://img.shields.io/badge/feature-Sprite%20Animation-ff69b4)
  ![APU](https://img.shields.io/badge/University-Asia%20Pacific%20University-critical)
  ![Windows](https://img.shields.io/badge/Windows-0078D6?logo=windows&logoColor=white)
  ![macOS](https://img.shields.io/badge/macOS-000000?logo=apple&logoColor=white)
  ![Linux](https://img.shields.io/badge/Linux-FCC624?logo=linux&logoColor=black)

**A festive 2D platformer engineered with advanced procedural graphics, custom particle physics, and exciting boss battles.**
<img width="200" alt="Screenshot 2026-03-28 050249" src="https://github.com/user-attachments/assets/5dfd1195-06e7-4718-b824-a412d6d54c4c" /> <img width="200" alt="Screenshot 2026-03-28 043811" src="https://github.com/user-attachments/assets/dfe104f2-1f84-4956-a3ee-255792a6898a" /> <img width="200" alt="Screenshot 2026-03-28 051743" src="https://github.com/user-attachments/assets/997b7b7a-6eee-40c3-afac-6a051052b8d3" />

<img width="200" alt="Screenshot 2026-03-28 050551" src="https://github.com/user-attachments/assets/d546d4dd-9d81-4546-a1ff-e7b04f34d3ba" /> <img width="200" alt="Screenshot 2026-03-28 050616" src="https://github.com/user-attachments/assets/1ccad71a-0dfa-4fa8-b031-8b706349f911" /> <img width="200" alt="Screenshot 2026-03-28 052711" src="https://github.com/user-attachments/assets/421e8445-95b8-4afe-b65a-2ed8190f143c" />



</div>

---

## Overview

**The Last Christmas Run** is a side-scrolling 2D platformer built entirely with **Pygame**. Take control of Santa Claus as he runs, jumps, and fights through increasingly challenging levels filled with enemies, hazards, puzzles, and powerful bosses.

Collect presents to unlock gates, activate checkpoints, survive deadly blizzards, and defeat the fearsome **Ice Golem** to save Christmas!

---

## Key Features

- **Smooth Platforming** – Responsive running, jumping, and shooting.
- **Ice Physics** – Ice tiles that affect movement dynamics and friction.
- **Dynamic Hazards** – Cannons, spikes, and environmental dangers.
- **Power-up System** – Health restoration, jump boosts, and invincibility shields.
- **Boss Battles** – Multi-phase Ice Golem encounters with complex AI.
- **Blizzard Storms** – Dynamic weather hazards that reduce visibility.
- **Cinematic Sequences** – Scripted boss intros and defeat scenes.
- **Checkpoint System** – Save progress and respawn safely at designated points.
- **Gift Collection** – Unlock level-end gates by collecting all presents.

### Advanced Special Effects Engineering
- **Procedural Screen Effects**: Real-time Pythagorean distance calculations render dynamic frost and damage vignettes without static image assets.
- **Additive Blending (`BLEND_RGBA_ADD`)**: Core powerup glows and player auras use Linear Dodge blending to physically illuminate the screen.
- **Volumetric Parallax Fog**: The blizzard system uses Z-Depth sorting to categorize smoke into 3 parallax layers, faking volumetric 3D weather.
- **Newtonian Kinematics & Ribbons**: Projectiles utilize trajectory history buffers for motion blur and calculate gravity/drag equations per frame.

---

## Gameplay & Controls

### Core Mechanics
- Run and jump across challenging snowy platforms.
- Shoot snowballs to defeat enemies and trigger switches.
- Collect presents to unlock level gates.
- Activate checkpoints to save your progress.
- Unlock the **Ice Shards** special ability after defeating the first boss.

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

## Power-ups

| Power-up | Effect | Duration |
|--------|--------|----------|
| ❤️ Health | Restore 100 HP | Instant |
| ⬆️ Jump Boost | Significantly higher jump height | 8 seconds |
| 🛡️ Shield | Complete invincibility | 8 seconds |

---

## Project Structure

```text
The-Last-Christmas-Run/
├── main.py            
├── editor.py            
├── requirements.txt      
├── LICENSE             
├── .gitignore         
│
├── src/                
│   ├── blizzard.py      
│   ├── boss.py         
│   ├── boss_slam.py     
│   ├── button.py       
│   ├── camera.py        
│   ├── checkpoint.py   
│   ├── cinematic.py     
│   ├── cinematic_outro.py 
│   ├── collectible.py   
│   ├── enemy.py         
│   ├── fireworks.py    
│   ├── gate.py         
│   ├── hazard.py        
│   ├── hud.py          
│   ├── level.py        
│   ├── menu.py         
│   ├── moving_platform.py 
│   ├── particles.py     
│   ├── player.py        
│   ├── player_effects.py 
│   ├── powerup.py       
│   ├── powerup_effects.py 
│   ├── projectiles.py   
│   ├── settings.py       
│   ├── smoke.py         
│   ├── sound_manager.py  
│   ├── stone_ring.py     
│   ├── tile.py           
│   ├── tile_config.py    
│   └── tile_loader.py    
│
├── data/               
│   ├── level0_data.csv
│   ├── level1_data.csv
│   ├── tile_database.json
│   └── main.spec        
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
└── tiles/              
    ├── solid/
    ├── decor/
    ├── enemy/
    ├── gate/
    ├── collectible/
    ├── checkpoint/
    ├── hazard/
    ├── powerup/
    └── moving_platform/
```

---

## 🚀 Installation & Setup

### For Players
1. Go to the [Releases](https://github.com/Maneet7805/2D-Platform_Game/releases) page.
2. Download the latest `The-Last-Christmas-Run.zip`.
3. Extract and run `The Last Christmas Run.exe`.

### For Developers
1. **Clone the repository**:
   ```bash
   git clone https://github.com/Maneet7805/2D-Platform_Game.git
   cd 2D-Platform_Game
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the game**:
   ```bash
   python main.py
   ```

---

## Level Editor
Create your own festive challenges using the built-in editor.

### Usage
- **Launch**: `python editor.py`
- **Controls**:
  - `Left Click`: Place selected tile.
  - `Right Click`: Erase tile.
  - `Arrow Keys`: Scroll through the map.
  - `SAVE`: Exports current layout to `data/levelX_data.csv`.
  - `LOAD`: Imports data from `data/levelX_data.csv`.

---

## Author
**Maneet Arvind Mehta**  
GitHub: [Maneet7805](https://github.com/Maneet7805)

### Have Fun!
Save Christmas, defeat the Ice Golem, and enjoy the holiday adventure!

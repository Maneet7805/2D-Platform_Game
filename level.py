import csv
import pygame
import os
import random
from settings import *
from tile import Tile
from enemy import Enemy
from gate import Gate
from collectible import Collectible
from checkpoint import Checkpoint
from hazard import Hazard, SPIKE_TILE_ID, CANNON_TILE_ID
from powerup import PowerUp
from boss import Boss, BOSS_TILE_ID
from moving_platform import MovingPlatform
from blizzard import BlizzardStorm
from tile_config import tile_db, TileCategory
from tile_loader import TileLoader

background_img = None

ICE_TILE_IDS = [12]

class Level:
    def __init__(self, level_file='level0_data.csv', bg_img=None):
        global background_img
        if bg_img:
            background_img = bg_img
            self.background_img = bg_img
        else:
            self.background_img = None
        
        self.level_file = level_file
        
        self.tiles = pygame.sprite.Group()
        self.decorations = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.gates = pygame.sprite.Group()
        self.collectibles = pygame.sprite.Group()
        self.checkpoints = pygame.sprite.Group()
        self.hazards = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        
        self.total_gifts_in_level = 0
        self.gifts_deposited = 0
        
        self.tile_loader = TileLoader()
        self.tile_db = self.tile_loader.load_all_tiles(TILE_SIZE)
        
        self.world_data = []
        self.level_width = 0
        self.level_height = 0
        
        self.blizzard = None
        self.blizzard_triggered = False
        
        self.load_level(level_file)
    
    def load_level(self, filename):
        self.world_data = []
        
        self.tiles.empty()
        self.decorations.empty()
        self.enemies.empty()
        self.gates.empty()
        self.collectibles.empty()
        self.checkpoints.empty()
        self.hazards.empty()
        self.powerups.empty()
        self.all_sprites.empty()
        
        if not os.path.exists(filename):
            self.world_data = [[-1] * 50 for _ in range(ROWS)]
        else:
            try:
                with open(filename, newline='') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    for row in reader:
                        int_row = []
                        for cell in row:
                            try:
                                if cell.strip():
                                    int_row.append(int(cell))
                                else:
                                    int_row.append(-1)
                            except:
                                int_row.append(-1)
                        self.world_data.append(int_row)
            except Exception as e:
                self.world_data = [[-1] * 50 for _ in range(ROWS)]
        
        max_col_with_tiles = 0
        for y, row in enumerate(self.world_data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    max_col_with_tiles = max(max_col_with_tiles, x)
        
        actual_cols = max_col_with_tiles + 1
        rows = len(self.world_data)
        
        self.level_width = actual_cols * TILE_SIZE
        self.level_height = rows * TILE_SIZE
        
        counts = {
            'solid': 0,
            'decor': 0,
            'enemy': 0,
            'gate': 0,
            'collectible': 0,
            'checkpoint': 0,
            'hazard': 0,
            'powerup': 0,
            'moving_platform': 0,
            'unknown': 0,
            'ice': 0,
            'missing': 0
        }
        
        for y, row in enumerate(self.world_data):
            for x, tile_id in enumerate(row):
                if x < actual_cols and tile_id >= 0:
                    
                    if tile_id not in self.tile_db.images:
                        counts['missing'] += 1
                        continue
                    
                    tile_type = tile_db.get_tile(tile_id)
                    
                    if tile_type is None:
                        if tile_id < len(self.tile_db.images):
                            decor_sprite = Tile(
                                x * TILE_SIZE, 
                                y * TILE_SIZE, 
                                self.tile_db.images[tile_id],
                                solid=False
                            )
                            self.decorations.add(decor_sprite)
                            self.all_sprites.add(decor_sprite)
                            counts['unknown'] += 1
                        continue
                    
                    if tile_type.category == TileCategory.SOLID:
                        if tile_id in self.tile_db.images:
                            is_ice = tile_id in ICE_TILE_IDS
                            if is_ice:
                                counts['ice'] += 1
                            
                            tile_sprite = Tile(
                                x * TILE_SIZE, 
                                y * TILE_SIZE, 
                                self.tile_db.images[tile_id],
                                solid=True
                            )
                            tile_sprite.is_ice = is_ice
                            
                            self.tiles.add(tile_sprite)
                            self.all_sprites.add(tile_sprite)
                            counts['solid'] += 1
                    
                    elif tile_type.category == TileCategory.DECORATIVE:
                        if tile_id in self.tile_db.images:
                            decor_sprite = Tile(
                                x * TILE_SIZE, 
                                y * TILE_SIZE, 
                                self.tile_db.images[tile_id],
                                solid=False
                            )
                            self.decorations.add(decor_sprite)
                            self.all_sprites.add(decor_sprite)
                            counts['decor'] += 1
                    
                    elif tile_type.category == TileCategory.ENEMY:
                        enemy_type = tile_type.properties.get('enemy_type', 'melee')
                        
                        if tile_id == BOSS_TILE_ID:
                            self.boss_spawn_x = x * TILE_SIZE + TILE_SIZE // 2
                            self.boss_spawn_y = y * TILE_SIZE + TILE_SIZE // 2
                        else:
                            enemy = Enemy(x * TILE_SIZE, y * TILE_SIZE, enemy_type)
                            self.enemies.add(enemy)
                            self.all_sprites.add(enemy)
                            counts['enemy'] += 1
                    
                    elif tile_type.category == TileCategory.GATE:
                        gate_type = tile_type.properties.get('gate_type', 'level_end')
                        gate = Gate(x * TILE_SIZE, y * TILE_SIZE, gate_type, tile_id)
                        self.gates.add(gate)
                        self.all_sprites.add(gate)
                        counts['gate'] += 1
                    
                    elif tile_type.category == TileCategory.COLLECTIBLE:
                        value = tile_type.properties.get('value', 1)
                        collectible = Collectible(
                            x * TILE_SIZE,
                            y * TILE_SIZE,
                            self.tile_db.images[tile_id],
                            value
                        )
                        self.collectibles.add(collectible)
                        self.all_sprites.add(collectible)
                        counts['collectible'] += 1
                    
                    elif tile_type.category == TileCategory.CHECKPOINT:
                        checkpoint_id = tile_type.properties.get('id', 0)
                        checkpoint = Checkpoint(
                            x * TILE_SIZE,
                            y * TILE_SIZE,
                            self.tile_db.images[tile_id],
                            checkpoint_id
                        )
                        self.checkpoints.add(checkpoint)
                        self.all_sprites.add(checkpoint)
                        counts['checkpoint'] += 1
                    
                    elif tile_type.category == TileCategory.HAZARD:
                        hazard = Hazard(
                            x * TILE_SIZE,
                            y * TILE_SIZE,
                            self.tile_db.images[tile_id],
                            tile_id
                        )
                        
                        if tile_id == CANNON_TILE_ID:
                            shoot_interval = tile_type.properties.get('shoot_interval', 90)
                            direction = tile_type.properties.get('direction', -1)
                            hazard.set_cannon_properties(shoot_interval, direction)
                        
                        self.hazards.add(hazard)
                        self.all_sprites.add(hazard)
                        counts['hazard'] += 1
                    
                    elif tile_type.category == TileCategory.POWERUP:
                        powerup_type = tile_type.properties.get('type', 'health')
                        duration = tile_type.properties.get('duration', 0)
                        value = tile_type.properties.get('value', 100)
                        
                        powerup = PowerUp(
                            x * TILE_SIZE,
                            y * TILE_SIZE,
                            self.tile_db.images[tile_id],
                            powerup_type,
                            duration,
                            value
                        )
                        self.powerups.add(powerup)
                        self.all_sprites.add(powerup)
                        counts['powerup'] += 1
                    
                    elif tile_type.category == TileCategory.MOVING_PLATFORM:
                        move_type = tile_type.properties.get('type', 'horizontal')
                        distance = tile_type.properties.get('distance', TILE_SIZE * 4)
                        speed = tile_type.properties.get('speed', 2)
                        
                        platform = MovingPlatform(
                            x * TILE_SIZE,
                            y * TILE_SIZE,
                            self.tile_db.images[tile_id],
                            move_type,
                            distance,
                            speed
                        )
                        
                        self.tiles.add(platform)
                        self.all_sprites.add(platform)
                        counts['moving_platform'] += 1
        
        self.total_gifts_in_level = len(self.collectibles)
        
        for gate in self.gates:
            gate.gifts_required = self.total_gifts_in_level
        
        if 'level1' in filename:
            self.blizzard = BlizzardStorm()
            self.blizzard_triggered = False
    
    def spawn_health_powerup(self, x, y):
        health_tile_id = 49
        
        if health_tile_id in self.tile_db.images:
            health_powerup = PowerUp(
                x - TILE_SIZE // 2,
                y - TILE_SIZE,
                self.tile_db.images[health_tile_id],
                "health",
                0,
                100
            )
            self.powerups.add(health_powerup)
            self.all_sprites.add(health_powerup)
            return True
        else:
            return False
    
    def find_player_start(self):
        spawn_x = TILE_SIZE * 2
        spawn_y = SCREEN_HEIGHT - TILE_SIZE * 2
        return spawn_x, spawn_y
    
    def check_boundaries(self, player):
        boundary_triggered = False
        
        if player.hitbox.x < TILE_SIZE * 2:
            player.hitbox.x = TILE_SIZE * 2
            player.vel_x = 0
            boundary_triggered = True
        
        if player.hitbox.x > self.level_width - TILE_SIZE * 2:
            player.hitbox.x = self.level_width - TILE_SIZE * 2
            player.vel_x = 0
            boundary_triggered = True
        
        player.rect.center = player.hitbox.center
        
        if boundary_triggered:
            test_rect = player.hitbox.copy()
            test_rect.y += 3
            player.grounded = False
            
            for tile in self.tiles:
                if test_rect.colliderect(tile.rect):
                    player.grounded = True
                    player.hitbox.bottom = tile.rect.top
                    player.rect.center = player.hitbox.center
                    player.vel_y = 0
                    break
    
    def update(self, player, camera):
        
        for collectible in self.collectibles:
            collectible.update(player)
        
        for checkpoint in self.checkpoints:
            checkpoint.update(player, self.checkpoints)
        
        for hazard in self.hazards:
            hazard.update(player)
        
        for powerup in self.powerups:
            if powerup.update(player):
                powerup.kill()
        
        for enemy in self.enemies:
            enemy.update(player, self.tiles)
        
        for tile in self.tiles:
            if hasattr(tile, 'move_type'):
                tile.update(player)
        
        if self.blizzard:
            self.blizzard.update(player, self.tiles)
            
            if not self.blizzard_triggered and player.rect.x > self.level_width * 0.3:
                if random.random() < 0.001:
                    if self.blizzard.trigger():
                        self.blizzard_triggered = True
        
        player.check_snowball_collisions(self.enemies)
        
        for enemy in self.enemies:
            if player.rect.colliderect(enemy.rect):
                if hasattr(enemy, 'can_deal_damage') and enemy.can_deal_damage():
                    player.take_damage(enemy.damage)
                    if hasattr(enemy, 'reset_damage_cooldown'):
                        enemy.reset_damage_cooldown()
                    if player.rect.centerx < enemy.rect.centerx:
                        player.rect.right = enemy.rect.left
                    else:
                        player.rect.left = enemy.rect.right
        
        self.check_boundaries(player)
        
        for gate in self.gates:
            if gate.update(player):
                return "gate"
        
        if not player.alive or player.health <= 0:
            if player.ready_to_respawn:
                if player.reset_to_checkpoint():
                    return "playing"
                else:
                    return "dead"
            else:
                return "playing"
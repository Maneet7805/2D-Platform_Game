import pygame
import random
import math
from settings import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
from tile import Tile
from sound_manager import sound_manager

class BossSlam:
    def __init__(self, boss):
        self.boss = boss
        self.active = False
        self.slam_timer = 0
        self.slam_duration = 40
        self.slam_frame = 0
        
        self.slam_particles = []
        self.slam_cracks = []
        self.slam_zone = None
        
        self.screen_shake = 0
        self.screen_shake_duration = 40
        self.screen_shake_intensity = 25
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        
        self.damage_radius = TILE_SIZE * 5
        self.damage_dealt = False
        
        self.slam_trigger_frame = 6
        
        self.waves = []
        self.wave_active = False
        self.wave_timer = 0
        self.wave_interval = 15
        self.max_waves = 5
        
        self.ice_tile_id = 12
        self.ice_image = None
        self.blocks_replaced = []
        
        self.damage_dealt_this_slam = False
        self.slam_count = 0
        
        self.sound_played = False
        
    def trigger_slam(self, tiles, level=None):
        self.active = True
        self.slam_timer = self.slam_duration
        self.slam_frame = 0
        self.damage_dealt = False
        self.damage_dealt_this_slam = False
        self.blocks_replaced = []
        self.slam_count += 1
        self.sound_played = False
        
        self.slam_zone = pygame.Rect(
            self.boss.rect.centerx - self.damage_radius,
            self.boss.rect.centery - self.damage_radius,
            self.damage_radius * 2,
            self.damage_radius * 2
        )
        
        if level and hasattr(self.boss, 'level_index') and self.boss.level_index == 1:
            self.replace_tiles_with_ice(tiles, level)
        
        self.create_impact_particles()
        
        self.create_slam_cracks(tiles)
        
        self.screen_shake = self.screen_shake_duration
        self.shake_offset_x = random.randint(-self.screen_shake_intensity, self.screen_shake_intensity)
        self.shake_offset_y = random.randint(-self.screen_shake_intensity // 2, self.screen_shake_intensity // 2)
        
        self.wave_active = True
        self.waves = []
        self.wave_timer = 0
        
        return True
    
    def replace_tiles_with_ice(self, tiles, level):
        if not self.ice_image and hasattr(level, 'tile_db') and self.ice_tile_id in level.tile_db.images:
            self.ice_image = level.tile_db.images[self.ice_tile_id]
        
        if not self.ice_image:
            return
        
        for tile in tiles:
            if self.slam_zone and tile.rect.colliderect(self.slam_zone):
                if hasattr(tile, 'solid') and tile.solid:
                    current_is_ice = hasattr(tile, 'is_ice') and tile.is_ice
                    
                    if not current_is_ice:
                        original_x = tile.rect.x
                        original_y = tile.rect.y
                        
                        tile.kill()
                        
                        ice_tile = Tile(
                            original_x,
                            original_y,
                            self.ice_image,
                            solid=True
                        )
                        ice_tile.is_ice = True
                        
                        level.tiles.add(ice_tile)
                        level.all_sprites.add(ice_tile)
                        
                        self.blocks_replaced.append(ice_tile)
        
        if hasattr(level, 'decorations'):
            for tile in level.decorations:
                if self.slam_zone and tile.rect.colliderect(self.slam_zone):
                    original_x = tile.rect.x
                    original_y = tile.rect.y
                    
                    tile.kill()
                    
                    ice_tile = Tile(
                        original_x,
                        original_y,
                        self.ice_image,
                        solid=True
                    )
                    ice_tile.is_ice = True
                    
                    level.tiles.add(ice_tile)
                    level.all_sprites.add(ice_tile)
                    self.blocks_replaced.append(ice_tile)
    
    def create_impact_particles(self):
        self.slam_particles = []
        
        ground_y = self.boss.rect.bottom - 5
        
        for _ in range(60):
            angle = random.uniform(0, math.pi * 2)
            distance = random.uniform(0, self.damage_radius * 0.8)
            
            spawn_x = self.boss.rect.centerx + math.cos(angle) * distance
            spawn_y = ground_y - random.randint(0, 5)
            
            vel_angle = random.uniform(-math.pi/2, math.pi/2)
            speed = random.uniform(4, 12)
            
            base_alpha = random.randint(60, 100)
            
            particle = {
                'x': spawn_x,
                'y': spawn_y,
                'vx': math.cos(vel_angle) * speed,
                'vy': random.uniform(-10, -4),
                'size': random.randint(2, 7),
                'color': random.choice([
                    (139, 69, 19, base_alpha),
                    (160, 82, 45, base_alpha),
                    (101, 67, 33, base_alpha),
                    (120, 120, 120, base_alpha),
                    (255, 255, 255, base_alpha),
                    (240, 248, 255, base_alpha),
                ]),
                'life': random.randint(25, 40),
                'max_life': 40,
                'gravity': 0.18,
                'drag': 0.95,
                'base_alpha': base_alpha,
                'ground_spawn': True
            }
            self.slam_particles.append(particle)
        
        for _ in range(35):
            angle = random.uniform(0, math.pi * 2)
            distance = random.uniform(0, self.damage_radius * 0.9)
            
            spawn_x = self.boss.rect.centerx + math.cos(angle) * distance
            spawn_y = ground_y - 2
            
            base_alpha = random.randint(50, 80)
            
            self.slam_particles.append({
                'x': spawn_x,
                'y': spawn_y,
                'vx': math.cos(angle) * random.uniform(1, 5),
                'vy': random.uniform(-6, -1),
                'size': random.randint(5, 12),
                'color': random.choice([
                    (255, 255, 255, base_alpha),
                    (240, 255, 255, base_alpha),
                    (220, 240, 255, base_alpha),
                    (200, 200, 200, base_alpha),
                ]),
                'life': random.randint(25, 40),
                'max_life': 40,
                'gravity': 0.1,
                'drag': 0.96,
                'alpha_fade': True,
                'base_alpha': base_alpha,
                'ground_spawn': True
            })
    
    def create_slam_cracks(self, tiles):
        self.slam_cracks = []
        crack_count = 0
        
        for tile in tiles:
            if self.slam_zone and tile.rect.colliderect(self.slam_zone):
                tile_center_x = tile.rect.centerx
                tile_center_y = tile.rect.centery
                boss_center_x = self.boss.rect.centerx
                boss_center_y = self.boss.rect.centery
                
                distance = math.sqrt((tile_center_x - boss_center_x)**2 + (tile_center_y - boss_center_y)**2)
                
                intensity = random.uniform(0.5, 1.0) * (1 - distance / self.damage_radius)
                intensity = max(0.3, intensity)
                
                self.slam_cracks.append({
                    'x': tile.rect.x,
                    'y': tile.rect.y,
                    'timer': 240,
                    'intensity': intensity,
                    'pattern': random.randint(0, 3)
                })
                crack_count += 1
    
    def update(self, player, tiles):
        if self.screen_shake > 0:
            self.screen_shake -= 1
            self.shake_offset_x = random.randint(-self.screen_shake_intensity, self.screen_shake_intensity)
            self.shake_offset_y = random.randint(-self.screen_shake_intensity // 2, self.screen_shake_intensity // 2)
        else:
            self.shake_offset_x = 0
            self.shake_offset_y = 0
        
        if not self.active:
            self.wave_active = False
            self.waves = []
            return False
            
        self.slam_timer -= 1
        self.slam_frame += 1
        
        if self.wave_active:
            self.wave_timer += 1
            
            if self.wave_timer % self.wave_interval == 1 and len(self.waves) < self.max_waves:
                base_size = 30 + (len(self.waves) * 10)
                self.waves.append({
                    'radius': base_size,
                    'alpha': 255,
                    'growth_rate': 4.0,
                    'color': random.choice([
                        (255, 200, 100),
                        (255, 220, 100),
                        (255, 180, 80),
                        (255, 140, 80),
                        (255, 100, 100),
                    ]),
                    'thickness': 4,
                    'age': 0,
                    'max_age': 45
                })
            
            for wave in self.waves[:]:
                wave['radius'] += wave['growth_rate']
                wave['alpha'] -= 2
                wave['age'] += 1
                
                if wave['radius'] > 150:
                    wave['thickness'] = 3
                if wave['radius'] > 250:
                    wave['thickness'] = 2
                if wave['radius'] > 350:
                    wave['thickness'] = 1
                
                if wave['radius'] >= self.damage_radius * 1.5 or wave['alpha'] <= 20 or wave['age'] >= wave['max_age']:
                    self.waves.remove(wave)
        
        if self.slam_frame == self.slam_trigger_frame and not self.damage_dealt:
            if not self.sound_played:
                sound_manager.play_boss_smash(self.boss.rect.centerx, self.boss.rect.centery)
                self.sound_played = True
            
            self.deal_damage(player)
            self.damage_dealt = True
            self.damage_dealt_this_slam = True
            self.screen_shake = self.screen_shake_duration + 15
        
        for particle in self.slam_particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += particle['gravity']
            particle['vx'] *= particle['drag']
            particle['vy'] *= particle['drag']
            particle['life'] -= 1
            
            if particle['y'] < self.boss.rect.top - 100:
                particle['life'] = 0
                
            if particle['life'] <= 0:
                self.slam_particles.remove(particle)
        
        for crack in self.slam_cracks[:]:
            crack['timer'] -= 1
            if crack['timer'] <= 0:
                self.slam_cracks.remove(crack)
        
        if self.slam_timer <= 0 and len(self.slam_particles) == 0:
            self.active = False
            self.wave_active = False
            self.waves = []
            return True
            
        return False
    
    def deal_damage(self, player):
        if not self.slam_zone:
            return
        
        player_center_x = player.rect.centerx
        player_center_y = player.rect.centery
        boss_center_x = self.boss.rect.centerx
        boss_center_y = self.boss.rect.centery
        
        distance = math.sqrt((player_center_x - boss_center_x)**2 + (player_center_y - boss_center_y)**2)
        
        if distance <= self.damage_radius:
            player.take_damage(30)
            
            if player_center_x > boss_center_x:
                player.rect.left = boss_center_x + self.damage_radius + 10
            else:
                player.rect.right = boss_center_x - self.damage_radius - 10
    
    def draw(self, screen, camera, shake_offset_x=0, shake_offset_y=0):
        
        if not self.active:
            return
        
        center_x = self.boss.rect.centerx
        center_y = self.boss.rect.centery + TILE_SIZE // 2
        screen_center_x = center_x - camera.scroll + shake_offset_x
        screen_center_y = center_y + shake_offset_y
        
        for wave in self.waves:
            radius = wave['radius']
            alpha = wave['alpha']
            color = wave['color']
            thickness = wave.get('thickness', 4)
            
            ring_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            
            for i in range(3):
                glow_alpha = alpha // (i + 2)
                glow_thickness = thickness + i
                glow_radius = radius + i * 2
                
                pygame.draw.ellipse(
                    ring_surf,
                    (*color, glow_alpha),
                    (screen_center_x - glow_radius,
                     screen_center_y - glow_radius // 2,
                     glow_radius * 2,
                     glow_radius),
                    glow_thickness
                )
            
            if radius > 100:
                inner_radius = radius * 0.7
                pygame.draw.ellipse(
                    ring_surf,
                    (*color, alpha // 2),
                    (screen_center_x - inner_radius,
                     screen_center_y - inner_radius // 2,
                     inner_radius * 2,
                     inner_radius),
                    2
                )
            
            sparkle_count = max(3, int(radius / 30))
            for _ in range(sparkle_count):
                angle = random.uniform(0, math.pi * 2)
                sparkle_x = screen_center_x + math.cos(angle) * radius
                sparkle_y = screen_center_y + math.sin(angle) * (radius // 2)
                
                sparkle_color = random.choice([
                    (255, 255, 255),
                    (255, 255, 0),
                    (255, 200, 0),
                ])
                
                sparkle_alpha = min(200, alpha)
                pygame.draw.circle(
                    ring_surf,
                    (*sparkle_color, sparkle_alpha),
                    (int(sparkle_x), int(sparkle_y)),
                    random.randint(1, 3)
                )
            
            screen.blit(ring_surf, (0, 0))
        
        for crack in self.slam_cracks:
            screen_x = crack['x'] - camera.scroll + shake_offset_x
            screen_y = crack['y'] + shake_offset_y
            alpha = int(255 * (crack['timer'] / 240))
            intensity = crack['intensity']
            
            crack_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            line_width = max(2, int(4 * intensity))
            
            if crack['pattern'] == 0:
                pygame.draw.line(crack_surf, (150, 100, 50, alpha), 
                               (5, 5), (TILE_SIZE-5, TILE_SIZE-5), line_width)
                pygame.draw.line(crack_surf, (150, 100, 50, alpha), 
                               (TILE_SIZE-5, 5), (5, TILE_SIZE-5), line_width)
            elif crack['pattern'] == 1:
                center = TILE_SIZE // 2
                for i in range(4):
                    angle = i * math.pi / 2
                    end_x = center + int(20 * intensity * math.cos(angle))
                    end_y = center + int(20 * intensity * math.sin(angle))
                    pygame.draw.line(crack_surf, (150, 100, 50, alpha),
                                   (center, center), (end_x, end_y), line_width)
            elif crack['pattern'] == 2:
                for i in range(3):
                    offset = i * (TILE_SIZE // 3)
                    pygame.draw.line(crack_surf, (150, 100, 50, alpha),
                                   (offset, 0), (offset, TILE_SIZE), 2)
                    pygame.draw.line(crack_surf, (150, 100, 50, alpha),
                                   (0, offset), (TILE_SIZE, offset), 2)
            else:
                for _ in range(int(8 * intensity)):
                    start_x = random.randint(5, TILE_SIZE-5)
                    start_y = random.randint(5, TILE_SIZE-5)
                    end_x = start_x + random.randint(-20, 20)
                    end_y = start_y + random.randint(-20, 20)
                    if 0 < end_x < TILE_SIZE and 0 < end_y < TILE_SIZE:
                        pygame.draw.line(crack_surf, (150, 100, 50, alpha),
                                       (start_x, start_y), (end_x, end_y), max(1, line_width-1))
            
            screen.blit(crack_surf, (int(screen_x), int(screen_y)))
        
        for particle in self.slam_particles:
            screen_x = particle['x'] - camera.scroll + shake_offset_x
            screen_y = particle['y'] + shake_offset_y
            life_ratio = particle['life'] / particle['max_life']
            
            if 'base_alpha' in particle:
                base_alpha = particle['base_alpha']
            else:
                base_alpha = 80
            
            if 'alpha_fade' in particle:
                alpha = int(base_alpha * life_ratio)
            else:
                alpha = int(base_alpha * life_ratio)
            
            if len(particle['color']) == 4:
                r, g, b, _ = particle['color']
                color = (r, g, b, alpha)
            else:
                r, g, b = particle['color'][:3]
                color = (r, g, b, alpha)
            
            pygame.draw.circle(
                screen,
                color,
                (int(screen_x), int(screen_y)),
                int(particle['size'] * life_ratio * 1.2)
            )
    
    def get_shake_offset(self):
        return (self.shake_offset_x, self.shake_offset_y)
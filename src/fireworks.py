import pygame
import random
import math
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from sound_manager import sound_manager

class RisingFirework:
    def __init__(self):
        self.x = random.randint(50, SCREEN_WIDTH - 50)
        self.y = SCREEN_HEIGHT - 30
        
        self.vy = -random.uniform(2.5, 5.5)
        self.vx = random.uniform(-0.8, 0.8)
        
        self.trail = []
        self.trail_length = 30
        
        self.state = "rising"
        
        self.burst_height = random.randint(SCREEN_HEIGHT // 4, SCREEN_HEIGHT * 3 // 4)
        
        self.particles = []
        
        self.main_color = random.choice([
            (255, 50, 50),
            (255, 100, 50),
            (255, 150, 50),
            (255, 200, 50),
            (255, 255, 50),
            (50, 255, 50),
            (50, 200, 255),
            (100, 50, 255),
            (255, 50, 200),
        ])
        
        self.secondary_colors = [
            (255, 255, 255),
            (255, 255, 0),
            (255, 0, 0),
            (0, 255, 0),
            (0, 100, 255),
            (255, 0, 255),
            (0, 255, 255),
        ]
        
        self.sound_played = False
        
        self.active = True
        
        self.explosion_intensity = random.uniform(0.7, 1.3)
        
    def update(self):
        if self.state == "rising":
            self.trail.append((self.x, self.y))
            if len(self.trail) > self.trail_length:
                self.trail.pop(0)
            
            self.y += self.vy
            self.x += self.vx
            
            self.vy *= 1.001
            
            if self.y <= self.burst_height:
                self.explode()
                
            if self.y < -100:
                self.active = False
                
        elif self.state == "exploding":
            all_dead = True
            for particle in self.particles[:]:
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']
                particle['vy'] += particle['gravity']
                particle['vx'] *= particle['drag']
                particle['vy'] *= particle['drag']
                particle['life'] -= 1
                
                if particle['sparkle'] and random.random() < 0.1:
                    particle['size'] = particle['original_size'] * 1.5
                else:
                    particle['size'] = particle['original_size']
                
                if particle['life'] > 0:
                    all_dead = False
                else:
                    self.particles.remove(particle)
            
            if all_dead and len(self.particles) == 0:
                self.active = False
    
    def explode(self):
        self.state = "exploding"
        
        if not self.sound_played:
            volume_scale = random.uniform(0.8, 1.2)
            sound_manager.play_firework(volume_scale=volume_scale)
            self.sound_played = True
        
        particle_count = random.randint(120, 180)
        
        for _ in range(particle_count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(3, 12)
            
            if random.random() < 0.6:
                r = min(255, max(0, self.main_color[0] + random.randint(-40, 40)))
                g = min(255, max(0, self.main_color[1] + random.randint(-40, 40)))
                b = min(255, max(0, self.main_color[2] + random.randint(-40, 40)))
                color = (r, g, b)
            else:
                color = random.choice(self.secondary_colors)
            
            sparkle = random.random() < 0.3
            
            particle = {
                'x': self.x,
                'y': self.y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'color': color,
                'size': random.randint(3, 8),
                'original_size': 0,
                'life': random.randint(40, 80),
                'max_life': 80,
                'gravity': 0.03,
                'drag': 0.985,
                'sparkle': sparkle
            }
            particle['original_size'] = particle['size']
            self.particles.append(particle)
        
        for _ in range(30):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(4, 15)
            particle = {
                'x': self.x,
                'y': self.y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'color': (255, 255, 255),
                'size': random.randint(1, 3),
                'original_size': 1,
                'life': random.randint(20, 40),
                'max_life': 40,
                'gravity': 0.01,
                'drag': 0.99,
                'sparkle': True
            }
            self.particles.append(particle)
    
    def draw(self, surface, camera_offset=0):
        if self.state == "rising":
            for i, pos in enumerate(self.trail):
                trail_pos = i / len(self.trail) if self.trail else 0
                
                alpha = int(200 * trail_pos)
                
                size = max(1, int(4 * trail_pos))
                
                r = min(255, self.main_color[0] + int(50 * (1 - trail_pos)))
                g = min(255, self.main_color[1] + int(50 * (1 - trail_pos)))
                b = min(255, self.main_color[2] + int(50 * (1 - trail_pos)))
                
                try:
                    pygame.draw.circle(
                        surface,
                        (r, g, b, alpha),
                        (int(pos[0]), int(pos[1])),
                        size
                    )
                except:
                    pygame.draw.circle(
                        surface,
                        (r, g, b),
                        (int(pos[0]), int(pos[1])),
                        size
                    )
            
            try:
                pygame.draw.circle(
                    surface,
                    (*self.main_color, 100),
                    (int(self.x), int(self.y)),
                    8
                )
                pygame.draw.circle(
                    surface,
                    (*self.main_color, 255),
                    (int(self.x), int(self.y)),
                    5
                )
                pygame.draw.circle(
                    surface,
                    (255, 255, 255, 200),
                    (int(self.x), int(self.y)),
                    2
                )
            except:
                pygame.draw.circle(
                    surface,
                    self.main_color,
                    (int(self.x), int(self.y)),
                    6
                )
                
        elif self.state == "exploding":
            for particle in self.particles:
                life_ratio = particle['life'] / particle['max_life']
                alpha = int(255 * life_ratio)
                
                if particle['sparkle']:
                    pulse = math.sin(pygame.time.get_ticks() * 0.02 + particle['x']) * 0.3 + 0.7
                    size = int(particle['size'] * life_ratio * pulse)
                else:
                    size = int(particle['size'] * life_ratio)
                
                if size < 1:
                    size = 1
                
                try:
                    pygame.draw.circle(
                        surface,
                        (*particle['color'], alpha),
                        (int(particle['x']), int(particle['y'])),
                        size
                    )
                    
                    if particle['sparkle'] and life_ratio > 0.5:
                        pygame.draw.circle(
                            surface,
                            (255, 255, 255, alpha),
                            (int(particle['x']), int(particle['y'])),
                            size // 2
                        )
                except:
                    pygame.draw.circle(
                        surface,
                        particle['color'],
                        (int(particle['x']), int(particle['y'])),
                        size
                    )


class FireworkManager:
    def __init__(self):
        self.fireworks = []
        self.spawn_timer = 0
        self.spawn_delay = 20
        self.max_fireworks = 12
        self.active = False
        self.surface = None
        self.initialized = False
        self.mode = "victory"
        
        self.screen_flash = 0
        self.screen_flash_duration = 3
        self.screen_flash_color = (255, 255, 255)
        
        self.camera_shake = 0
        self.camera_shake_duration = 15
        self.camera_shake_intensity = 8
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        
    def start_victory(self):
        self.fireworks.clear()
        self.spawn_timer = 0
        self.active = True
        self.initialized = True
        self.mode = "victory"
        
        self.screen_flash = 0
        self.camera_shake = 0
        
        for _ in range(5):
            self.fireworks.append(RisingFirework())
        
        try:
            self.surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        except Exception as e:
            self.surface = None
    
    def stop(self):
        self.active = False
        self.fireworks.clear()
        self.surface = None
        self.initialized = False
        self.screen_flash = 0
        self.camera_shake = 0
    
    def trigger_explosion_effects(self, intensity=1.0):
        self.screen_flash = self.screen_flash_duration
        
        self.camera_shake = int(self.camera_shake_duration * intensity)
        
    def update(self):
        if not self.active or self.mode != "victory":
            return
        
        if self.screen_flash > 0:
            self.screen_flash -= 1
        
        if self.camera_shake > 0:
            self.camera_shake -= 1
            self.shake_offset_x = random.randint(-self.camera_shake_intensity, self.camera_shake_intensity)
            self.shake_offset_y = random.randint(-self.camera_shake_intensity // 2, self.camera_shake_intensity // 2)
        else:
            self.shake_offset_x = 0
            self.shake_offset_y = 0
        
        self.spawn_timer += 1
        if len(self.fireworks) < self.max_fireworks and self.spawn_timer >= self.spawn_delay:
            if random.random() < 0.3:
                new_firework = RisingFirework()
                new_firework2 = RisingFirework()
                self.fireworks.append(new_firework)
                self.fireworks.append(new_firework2)
            else:
                new_firework = RisingFirework()
                self.fireworks.append(new_firework)
            self.spawn_timer = 0
        
        for firework in self.fireworks[:]:
            was_rising = firework.state == "rising"
            firework.update()
            
            if was_rising and firework.state == "exploding":
                self.trigger_explosion_effects(firework.explosion_intensity)
            
            if not firework.active:
                self.fireworks.remove(firework)
    
    def draw(self, screen, camera_offset=0):
        if not self.active or not self.surface or self.mode != "victory":
            return
        
        self.surface.fill((0, 0, 0, 3))
        
        for firework in self.fireworks:
            firework.draw(self.surface, camera_offset)
        
        screen.blit(self.surface, (self.shake_offset_x, self.shake_offset_y))
        
        if self.screen_flash > 0:
            flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            alpha = int(60 * (self.screen_flash / self.screen_flash_duration))
            flash_surf.fill((255, 255, 255, alpha))
            screen.blit(flash_surf, (0, 0))
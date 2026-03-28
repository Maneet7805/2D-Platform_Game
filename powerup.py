import pygame
import math
import random
from settings import TILE_SIZE
from sound_manager import sound_manager

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, image, powerup_type="health", duration=0, value=0):
        super().__init__()
        
        self.image = image
        self.original_image = image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.powerup_type = powerup_type
        self.duration = duration
        self.value = value
        self.collected = False
        
        self.original_y = self.rect.y
        
        self.float_offset = 0
        self.float_speed = 0.03
        self.float_amplitude = 4
        self.rotation = 0
        self.pulse = 0
        
        self.glow_alpha = 0
        self.glow_direction = 1
        
        self.particles = []

        self.collect_particles = []
        
        if powerup_type == "health":
            self.color = (100, 255, 100)
            self.particle_color = (180, 255, 180)
        elif powerup_type == "jump_boost":
            self.color = (255, 255, 100)
            self.particle_color = (150, 255, 150)
        elif powerup_type == "shield":
            self.color = (100, 100, 255)
            self.particle_color = (150, 150, 255)
        else:
            self.color = (255, 255, 100)
            self.particle_color = (255, 255, 150)
    
    def create_particles(self):
        for _ in range(3):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.5, 1.5)
            self.particles.append({
                'x': self.rect.centerx,
                'y': self.rect.centery,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': random.randint(20, 30),
                'max_life': 30,
                'size': random.randint(1, 2)
            })

    def create_collect_burst(self):
        for _ in range(15):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 4)
            self.collect_particles.append({
                'x': self.rect.centerx,
                'y': self.rect.centery,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': random.randint(20, 35),
                'max_life': 35,
                'size': random.randint(2, 4)
            })

    def update(self, player):
        
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)

        for particle in self.collect_particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            particle['vx'] *= 0.96
            particle['vy'] *= 0.96
            if particle['life'] <= 0:
                self.collect_particles.remove(particle)
        
        if random.random() < 0.05:
            self.create_particles()
        
        self.float_offset += self.float_speed
        self.rect.y = self.original_y + (math.sin(self.float_offset * math.pi * 2) * self.float_amplitude)
        
        self.pulse += 0.05
        pulse_factor = math.sin(self.pulse) * 0.1 + 0.9
        
        new_size = int(TILE_SIZE * pulse_factor)
        self.image = pygame.transform.scale(self.original_image, (new_size, new_size))
        self.rect = self.image.get_rect(center=(self.rect.centerx, self.rect.centery))
        
        if not self.collected and self.rect.colliderect(player.rect):
            
            if self.powerup_type == "health":
                if player.health >= player.max_health:
                    return False
                else:
                    player.health = min(player.max_health, player.health + self.value)
                    player.effect_colour((100,255,100))
                    sound_manager.play_sound(sound_manager.powerup_sounds, "powerup")
                    self.collected = True
                    self.create_collect_burst()
                    return True
                
            elif self.powerup_type in ["jump_boost", "shield"]:
                self.collected = True
                player.collect_powerup(self.powerup_type, self.duration, self.value)

                if self.powerup_type == "jump_boost":
                    player.effect_colour((255, 240, 120))

                elif self.powerup_type == "shield":
                    player.effect_colour((120, 180, 255))

                sound_manager.play_sound(sound_manager.powerup_sounds, "powerup")

                return True
        
        return False
    
    def draw_glow(self, screen, camera):
        pos = camera.apply(self)
        center_x = pos[0] + self.rect.width // 2
        center_y = pos[1] + self.rect.height // 2
        
        glow_alpha = int(100 + 55 * math.sin(self.pulse * 2))
        
        for i in range(3):
            glow_size = self.rect.width // 2 + i * 4
            glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                glow_surf,
                (*self.color, glow_alpha // (i + 1)),
                (glow_size, glow_size),
                glow_size
            )
            screen.blit(glow_surf, (center_x - glow_size, center_y - glow_size))
        
        if self.powerup_type == "health":
            ring_radius = self.rect.width // 2 + 6 + int(abs(math.sin(self.pulse * 2)) * 3)
            ring_surf = pygame.Surface((ring_radius * 2 + 4, ring_radius * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(
                ring_surf,
                (*self.color, 120),
                (ring_radius + 2, ring_radius + 2),
                ring_radius,
                2
            )
            screen.blit(ring_surf, (center_x - ring_radius - 2, center_y - ring_radius - 2))

        for particle in self.particles:
            particle_x = particle['x'] - camera.scroll
            particle_y = particle['y']
            life_ratio = particle['life'] / particle['max_life']
            alpha = int(255 * life_ratio)
            pygame.draw.circle(
                screen,
                (*self.particle_color, alpha),
                (int(particle_x), int(particle_y)),
                particle['size']
            )

        for particle in self.collect_particles:
            particle_x = particle['x'] - camera.scroll
            particle_y = particle['y']
            life_ratio = particle['life'] / particle['max_life']
            alpha = int(255 * life_ratio)

            burst_surf = pygame.Surface((particle['size'] * 6, particle['size'] * 6), pygame.SRCALPHA)
            pygame.draw.circle(
                burst_surf,
                (*self.color, alpha),
                (particle['size'] * 3, particle['size'] * 3),
                particle['size']
            )
            screen.blit(
                burst_surf,
                (particle_x - particle['size'] * 3, particle_y - particle['size'] * 3)
            )
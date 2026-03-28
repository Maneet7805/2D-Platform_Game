import pygame
import random
import math
from settings import *

class SmokeParticle:
    def __init__(self, x, y):
        self.x = x + random.uniform(-3, 3)
        self.y = y

        self.radius = random.randint(6, 10)

        self.vy = random.uniform(-1.1, -0.7)

        self.vx = random.uniform(-0.1, 0.1)

        self.turbulence = random.uniform(0.005, 0.015)
        self.turb_angle = random.uniform(0, math.pi * 2)

        self.wind = 0.0

        self.base_alpha = random.randint(160, 200)
        self.alpha = self.base_alpha

        self.expand = random.uniform(0.01, 0.02)
        
        self.lifetime = random.randint(80, 120)
        self.age = 0
        
        self.start_x = x
        self.start_y = y

    def update(self, wind):
        self.age += 1
        self.wind = wind
        
        height_factor = min(1.0, self.age / 60)
        
        self.turb_angle += self.turbulence
        wobble = math.sin(self.turb_angle) * 0.2

        wind_effect = self.wind * 2

        self.x += self.vx + wobble + wind_effect
        self.y += self.vy

        self.vy *= 0.999

        self.radius += self.expand * height_factor * 0.5

        life_ratio = self.age / self.lifetime
        self.alpha = int(self.base_alpha * (1 - life_ratio * 0.5))

    def draw(self, screen, camera):
        if self.alpha <= 10:
            return

        screen_x = self.x - camera.scroll
        screen_y = self.y

        if screen_x < -100 or screen_x > 900 or screen_y < -100 or screen_y > 700:
            return

        size = int(self.radius * 2.5)
        if size < 5:
            return
            
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2

        age_factor = min(1.0, self.age / 50)
        gray_val = int(140 + 80 * age_factor)

        pygame.draw.circle(
            surf,
            (gray_val, gray_val, gray_val, self.alpha),
            (center, center),
            int(self.radius)
        )
        
        if self.radius > 4:
            pygame.draw.circle(
                surf,
                (gray_val, gray_val, gray_val, self.alpha // 3),
                (center, center),
                int(self.radius + 2)
            )

        screen.blit(surf, (int(screen_x - self.radius * 1.2), int(screen_y - self.radius * 1.2)))

    def is_dead(self):
        return self.age >= self.lifetime or self.alpha <= 10


class SmokeEffect:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.particles = []
        self.emitting = True
        self.emit_timer = 0
        self.emit_rate = 2
        
        self.wind = 0.3
        self.wind_target = 0.3
        
    def update(self):
        if random.random() < 0.01:
            self.wind_target = random.uniform(0.2, 0.8)
        self.wind += (self.wind_target - self.wind) * 0.01
        
        self.emit_timer += 1
        if self.emitting and self.emit_timer >= self.emit_rate:
            self.emit_timer = 0
            self._emit()
        
        for particle in self.particles[:]:
            particle.update(self.wind)
            if particle.is_dead():
                self.particles.remove(particle)
    
    def _emit(self):
        for _ in range(random.randint(2, 4)):
            self.particles.append(SmokeParticle(self.x, self.y))
    
    def draw(self, screen, camera):
        for particle in self.particles:
            particle.draw(screen, camera)
    
    def stop(self):
        self.emitting = False
    
    def start(self):
        self.emitting = True
    
    def burst(self, count=12):
        for _ in range(count):
            self.particles.append(SmokeParticle(self.x, self.y))
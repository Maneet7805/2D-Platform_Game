import pygame
import random
import math
import os
import pathlib
from settings import TILE_SIZE

BASE_DIR = pathlib.Path(__file__).parent

class SnowballTrailParticle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-0.3, 0.3)
        self.vy = random.uniform(-0.3, 0.3)
        self.size = random.randint(2, 4)
        self.alpha = random.randint(180, 255)
        self.life = random.randint(15, 25)
        self.max_life = self.life
        self.color = color
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.alpha = int(255 * (self.life / self.max_life))
        
    def draw(self, screen, camera):
        if self.life <= 0:
            return
        screen_x = self.x - camera.scroll
        screen_y = self.y
        color = (*self.color[:3], self.alpha)
        pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), self.size)


class IceShardTrailParticle:
    def __init__(self, x, y):
        self.x = x + random.uniform(-1.5, 1.5)
        self.y = y + random.uniform(-1.5, 1.5)
        self.vx = random.uniform(-0.25, 0.25)
        self.vy = random.uniform(-0.25, 0.25)
        self.size = random.randint(1, 3)
        self.alpha = random.randint(170, 255)
        self.life = random.randint(10, 16)
        self.max_life = self.life
        self.color = random.choice([
            (180, 235, 255),
            (140, 220, 255),
            (230, 248, 255)
        ])

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.alpha = max(0, int(255 * (self.life / self.max_life)))

    def draw(self, screen, camera):
        if self.life <= 0:
            return

        screen_x = self.x - camera.scroll
        screen_y = self.y

        glow_surface = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*self.color, self.alpha // 4), (5, 5), 4)
        screen.blit(glow_surface, (screen_x - 5, screen_y - 5))

        pygame.draw.circle(screen, (*self.color, self.alpha), (int(screen_x), int(screen_y)), self.size)


class IceShardBurstParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        angle = random.uniform(0, math.tau)
        speed = random.uniform(1.4, 3.2)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.size = random.randint(2, 5)
        self.life = random.randint(12, 20)
        self.max_life = self.life
        self.alpha = 255
        self.color = random.choice([
            (170, 230, 255),
            (120, 210, 255),
            (235, 250, 255)
        ])

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.94
        self.vy *= 0.94
        self.life -= 1
        self.alpha = max(0, int(255 * (self.life / self.max_life)))

    def draw(self, screen, camera):
        if self.life <= 0:
            return

        screen_x = self.x - camera.scroll
        screen_y = self.y
        color = (*self.color, self.alpha)

        points = [
            (screen_x, screen_y - self.size),
            (screen_x + self.size * 0.7, screen_y),
            (screen_x, screen_y + self.size),
            (screen_x - self.size * 0.7, screen_y),
        ]
        pygame.draw.polygon(screen, color, points)


class Snowball(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, damage=10):
        super().__init__()
        
        self.size = max(TILE_SIZE // 2, 20)
        
        self.image = self.load_snowball_image()
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.direction = direction
        self.speed = 8
        self.vx = self.speed * direction
        self.vy = 0
        
        self.damage = damage
        self.lifetime = 60
        self.age = 0
        self.max_distance = TILE_SIZE * 8
        self.start_x = x
        
        self.trail_particles = []
        self.trail_length = 12
        self.particle_spawn_timer = 0
        self.particle_spawn_rate = 2
        self.trail_color = (200, 230, 255)

    def load_snowball_image(self):
        try:
            paths = [
                "assets/weapons/snowball.png",
                "snowball.png"
            ]
            
            for path in paths:
                if os.path.exists(path):
                    try:
                        image = pygame.image.load(path).convert_alpha()
                        image = pygame.transform.scale(image, (self.size, self.size))
                        return image
                    except Exception as e:
                        pass
        except Exception as e:
            pass
        
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        center = self.size // 2
        pygame.draw.circle(surf, (255, 255, 255), (center, center), center)
        pygame.draw.circle(surf, (200, 230, 255), (center-1, center-1), center-2)
        return surf
        
    def update(self):
        self.age += 1
        self.particle_spawn_timer += 1
        
        if self.particle_spawn_timer >= self.particle_spawn_rate:
            self.particle_spawn_timer = 0
            particle = SnowballTrailParticle(self.rect.centerx, self.rect.centery, self.trail_color)
            self.trail_particles.append(particle)
        
        if len(self.trail_particles) > self.trail_length:
            self.trail_particles.pop(0)
        
        for particle in self.trail_particles[:]:
            particle.update()
            if particle.life <= 0:
                self.trail_particles.remove(particle)
        
        self.rect.x += self.vx
        
        if abs(self.rect.x - self.start_x) >= self.max_distance:
            return True
        if self.age >= self.lifetime:
            return True
        return False
    
    def draw_trail(self, screen, camera):
        for particle in self.trail_particles:
            particle.draw(screen, camera)
    
    def draw(self, screen, camera):
        pos = camera.apply(self)
        screen.blit(self.image, pos)


class IceShard(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, vertical_speed=0.0, damage=14):
        super().__init__()

        self.direction = direction
        self.speed = 7.5
        self.vx = self.speed * direction
        self.vy = vertical_speed
        self.damage = damage

        self.x = float(x)
        self.y = float(y)

        self.age = 0
        self.lifetime = 85
        self.max_distance = TILE_SIZE * 8
        self.start_x = x

        self.trail_particles = []
        self.burst_particles = []
        self.trail_length = 15
        self.particle_spawn_timer = 0
        self.particle_spawn_rate = 2
        self.expired = False

        self.image = self.load_ice_shard_image(direction)
        self.rect = self.image.get_rect(center=(x, y))

    def load_ice_shard_image(self, direction):
        shard_path = BASE_DIR / "assets" / "weapons" / "ice_shard.png"
        
        if shard_path.exists():
            try:
                image = pygame.image.load(str(shard_path)).convert_alpha()
                target_w = max(int(TILE_SIZE * 1.4), 34)
                target_h = max(int(TILE_SIZE * 0.75), 20)

                ratio = min(
                    target_w / max(1, image.get_width()),
                    target_h / max(1, image.get_height())
                )
                new_size = (
                    max(1, int(image.get_width() * ratio)),
                    max(1, int(image.get_height() * ratio))
                )
                image = pygame.transform.smoothscale(image, new_size)

                if direction < 0:
                    image = pygame.transform.flip(image, True, False)
                return image
            except Exception as e:
                pass

        alt_path = BASE_DIR / "sprites" / "ice_shard.png"
        
        if alt_path.exists():
            try:
                image = pygame.image.load(str(alt_path)).convert_alpha()
                target_w = max(int(TILE_SIZE * 1.4), 34)
                target_h = max(int(TILE_SIZE * 0.75), 20)

                ratio = min(
                    target_w / max(1, image.get_width()),
                    target_h / max(1, image.get_height())
                )
                new_size = (
                    max(1, int(image.get_width() * ratio)),
                    max(1, int(image.get_height() * ratio))
                )
                image = pygame.transform.smoothscale(image, new_size)

                if direction < 0:
                    image = pygame.transform.flip(image, True, False)
                return image
            except Exception as e:
                pass

        width = max(int(TILE_SIZE * 1.1), 28)
        height = max(int(TILE_SIZE * 0.45), 14)
        surface = pygame.Surface((width, height), pygame.SRCALPHA)

        outer = [
            (0, height // 2),
            (width * 0.22, 0),
            (width - 2, height // 2),
            (width * 0.22, height - 1)
        ]
        inner = [
            (width * 0.16, height // 2),
            (width * 0.3, 2),
            (width - 8, height // 2),
            (width * 0.3, height - 3)
        ]

        pygame.draw.polygon(surface, (110, 215, 255), outer)
        pygame.draw.polygon(surface, (210, 245, 255), inner)
        pygame.draw.line(
            surface,
            (255, 255, 255),
            (int(width * 0.2), height // 2),
            (width - 10, height // 2),
            2
        )

        if direction < 0:
            surface = pygame.transform.flip(surface, True, False)

        return surface

    def create_burst(self):
        if self.expired:
            return
        self.expired = True
        for _ in range(random.randint(8, 12)):
            self.burst_particles.append(IceShardBurstParticle(self.rect.centerx, self.rect.centery))

    def update(self):
        self.age += 1

        for particle in self.burst_particles[:]:
            particle.update()
            if particle.life <= 0:
                self.burst_particles.remove(particle)

        if self.expired:
            return len(self.burst_particles) == 0

        self.particle_spawn_timer += 1
        if self.particle_spawn_timer >= self.particle_spawn_rate:
            self.particle_spawn_timer = 0
            self.trail_particles.append(IceShardTrailParticle(self.rect.centerx, self.rect.centery))

        if len(self.trail_particles) > self.trail_length:
            self.trail_particles.pop(0)

        for particle in self.trail_particles[:]:
            particle.update()
            if particle.life <= 0:
                self.trail_particles.remove(particle)

        self.x += self.vx
        self.y += self.vy
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)

        if abs(self.rect.x - self.start_x) >= self.max_distance or self.age >= self.lifetime:
            self.create_burst()

        return False

    def draw_trail(self, screen, camera):
        for particle in self.trail_particles:
            particle.draw(screen, camera)

    def draw(self, screen, camera):
        if not self.expired:
            pos = camera.apply(self)

            glow = pygame.Surface((self.image.get_width() + 8, self.image.get_height() + 8), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (120, 220, 255, 45), glow.get_rect())
            screen.blit(glow, (pos[0] - 4, pos[1] - 4))

            screen.blit(self.image, pos)

        for particle in self.burst_particles:
            particle.draw(screen, camera)
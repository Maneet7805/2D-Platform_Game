import pygame
import math
import random
from settings import *
from sound_manager import sound_manager

SPIKE_TILE_ID = 45
CANNON_TILE_ID = 46

class MuzzleFlash(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        
        self.size = random.randint(TILE_SIZE // 4, TILE_SIZE // 2)
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        center = self.size // 2
        
        colors = [
            (255, 200, 50, 255),
            (255, 100, 50, 220),
            (255, 50, 0, 180),
            (255, 255, 200, 150)
        ]
        
        for i, color in enumerate(colors):
            radius = self.size - (i * 2)
            if radius > 2:
                offset_x = random.randint(-1, 1)
                offset_y = random.randint(-1, 1)
                pygame.draw.circle(
                    self.image,
                    color,
                    (center + offset_x, center + offset_y),
                    radius
                )
        
        for _ in range(4):
            spark_x = random.randint(center - 3, center + 3)
            spark_y = random.randint(center - 3, center + 3)
            spark_size = random.randint(1, 2)
            spark_color = random.choice([
                (255, 255, 255, 255),
                (255, 255, 100, 255),
                (255, 200, 50, 255)
            ])
            pygame.draw.circle(
                self.image,
                spark_color,
                (spark_x, spark_y),
                spark_size
            )
        
        if direction < 0:
            burst_points = [(center-2, center-2), (center-4, center), (center-2, center+2)]
        else:
            burst_points = [(center+2, center-2), (center+4, center), (center+2, center+2)]
        
        for point in burst_points:
            pygame.draw.circle(
                self.image,
                (255, 255, 200, 200),
                point,
                1
            )
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.lifetime = 8
        self.age = 0
        self.direction = direction
        
    def update(self):
        self.age += 1
        alpha = max(0, 255 - (self.age * 30))
        self.image.set_alpha(alpha)
        
        if self.age < 4:
            scale = 1 + (self.age * 0.15)
            new_size = int(self.size * scale)
            old_center = self.rect.center
            self.image = pygame.transform.scale(self.image, (new_size, new_size))
            self.rect = self.image.get_rect()
            self.rect.center = old_center
            
    def is_dead(self):
        return self.age >= self.lifetime


class Cannonball(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, damage=20):
        super().__init__()
        
        self.ball_size = TILE_SIZE // 2
        self.image = pygame.Surface((self.ball_size, self.ball_size), pygame.SRCALPHA)
        center = self.ball_size // 2
        
        pygame.draw.circle(
            self.image,
            (255, 100, 50, 200),
            (center, center),
            center
        )
        
        pygame.draw.circle(
            self.image,
            (255, 255, 100, 230),
            (center-1, center-1),
            center-3
        )
        
        pygame.draw.circle(
            self.image,
            (255, 255, 255, 255),
            (center-2, center-2),
            center-5
        )
        
        for _ in range(4):
            flame_x = center + random.randint(-3, 3)
            flame_y = center + random.randint(-3, 3)
            flame_size = random.randint(1, 2)
            flame_color = random.choice([
                (255, 200, 50, 200),
                (255, 150, 50, 200),
                (255, 100, 50, 180)
            ])
            pygame.draw.circle(
                self.image,
                flame_color,
                (flame_x, flame_y),
                flame_size
            )
        
        self.rect = self.image.get_rect()
        self.rect.midtop = (x, y + 5)
        
        self.direction = direction
        self.speed = 5
        self.vx = self.speed * direction
        self.vy = 0
            
        self.damage = damage
        self.lifetime = 150
        self.age = 0
        self.max_distance = TILE_SIZE * 8
        self.start_x = x
        
        self.trail = []
        self.trail_length = 15
        self.trail_colors = [
            (255, 200, 50, 180),
            (255, 150, 50, 160),
            (255, 100, 50, 140),
            (255, 50, 0, 120)
        ]
        
    def update(self):
        self.age += 1
        
        self.trail.append((self.rect.centerx, self.rect.centery))
        if len(self.trail) > self.trail_length:
            self.trail.pop(0)
        
        self.rect.x += self.vx
        
        if abs(self.rect.x - self.start_x) >= self.max_distance:
            self.kill()
            return
        
        if self.age > self.lifetime - 20:
            alpha = int(255 * ((self.lifetime - self.age) / 20))
            self.image.set_alpha(alpha)
    
    def draw_trail(self, screen, camera):
        for i, pos in enumerate(self.trail):
            trail_progress = i / len(self.trail) if len(self.trail) > 0 else 0
            
            alpha = int(200 * trail_progress)
            
            size = max(1, int(self.ball_size // 3 * trail_progress))
            
            color_index = min(len(self.trail_colors) - 1, 
                             int((1 - trail_progress) * len(self.trail_colors)))
            base_color = self.trail_colors[color_index][:3]
            
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            
            color = (*base_color, alpha)
            pygame.draw.circle(trail_surf, color, (size, size), size)
            
            if trail_progress > 0.7:
                sparkle_size = max(1, size - 1)
                pygame.draw.circle(trail_surf, (255, 255, 255, alpha//2), 
                                 (size-1, size-1), sparkle_size)
            
            screen_x = pos[0] - camera.scroll - size
            screen_y = pos[1] - size
            screen.blit(trail_surf, (screen_x, screen_y))
    
    def is_dead(self):
        return self.age >= self.lifetime

class Hazard(pygame.sprite.Sprite):
    def __init__(self, x, y, image, tile_id):
        super().__init__()
        
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.tile_id = tile_id
        
        if tile_id == SPIKE_TILE_ID:
            self.type = "spike"
            self.damage = 50
            self.damage_cooldown = 0
            
            self.hitbox = pygame.Rect(
                x + TILE_SIZE // 4,
                y + TILE_SIZE // 4,
                TILE_SIZE // 2,
                TILE_SIZE // 2
            )
            
        elif tile_id == CANNON_TILE_ID:
            self.type = "cannon"
            self.damage = 20
            self.shoot_interval = 90
            self.shoot_timer = 0
            self.direction = -1
            self.cannonballs = pygame.sprite.Group()
            self.muzzle_flashes = pygame.sprite.Group()
            
            self.sound_channel = None
            self.hitbox = self.rect.copy()
            
        else:
            self.type = "unknown"
            self.damage = 0
            self.hitbox = self.rect.copy()
    
    def set_cannon_properties(self, shoot_interval=90, direction=-1):
        if self.type == "cannon":
            self.shoot_interval = shoot_interval
            self.direction = direction
    
    def update(self, player):
        if self.type == "spike":
            if self.damage_cooldown > 0:
                self.damage_cooldown -= 1
                return False
            
            if self.hitbox.colliderect(player.rect):
                player.take_damage(self.damage)
                self.damage_cooldown = 30
                return True
                
        elif self.type == "cannon":
            self.sound_channel = sound_manager.play_continuous_sound(
                sound_manager.hazard_sounds,
                "cannon",
                self.rect.centerx,
                self.rect.centery,
                self.sound_channel
            )
            
            if self.shoot_timer > 0:
                self.shoot_timer -= 1
                
            self.muzzle_flashes.update()
            for flash in self.muzzle_flashes.copy():
                if flash.is_dead():
                    flash.kill()
                
            for cannonball in self.cannonballs.copy():
                cannonball.update()
                
                if cannonball.rect.colliderect(player.rect):
                    player.take_damage(self.damage)
                    cannonball.kill()
                    
                if cannonball.is_dead():
                    cannonball.kill()
            
            if self.shoot_timer <= 0:
                self._shoot()
                self.shoot_timer = self.shoot_interval
                
        return False
    
    def _shoot(self):
        if self.direction < 0:
            spawn_x = self.rect.left
            spawn_y = self.rect.top + 0
            flash_x = self.rect.left
            flash_y = self.rect.top + 5
        else:
            spawn_x = self.rect.right
            spawn_y = self.rect.top + 0
            flash_x = self.rect.right
            flash_y = self.rect.top + 5
        
        sound_manager.play_sound(
            sound_manager.hazard_sounds, 
            "cannon", 
            self.rect.centerx,
            self.rect.centery,
            0.7
        )
        
        for _ in range(2):
            offset_x = random.randint(-3, 3)
            offset_y = random.randint(-2, 2)
            flash = MuzzleFlash(flash_x + offset_x, flash_y + offset_y, self.direction)
            self.muzzle_flashes.add(flash)
        
        cannonball = Cannonball(
            spawn_x,
            spawn_y,
            self.direction,
            self.damage
        )
        self.cannonballs.add(cannonball)
    
    def draw(self, screen, camera):
        pos = camera.apply(self)
        screen.blit(self.image, pos)
    
    def draw_cannonballs(self, screen, camera):
        if self.type == "cannon":
            for cannonball in self.cannonballs:
                cannonball.draw_trail(screen, camera)
            
            for flash in self.muzzle_flashes:
                pos = camera.apply(flash)
                screen.blit(flash.image, pos)
            
            for cannonball in self.cannonballs:
                pos = camera.apply(cannonball)
                screen.blit(cannonball.image, pos)
    
    def draw_snowballs(self, screen, camera):
        self.draw_cannonballs(screen, camera)
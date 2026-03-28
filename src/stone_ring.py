import pygame
import math
import random
from settings import TILE_SIZE

class StoneRing:
    def __init__(self, boss):
        self.boss = boss
        self.stones = []
        self.ring_radius = TILE_SIZE * 2
        self.ring_speed = 0.02
        self.ring_angle = 0
        self.stone_count = 8
        self.create_stone_ring()
        
        self.thrown_stones = []
        self.throw_timer = 0
        self.throw_interval = 90
        
        self.chase_speed = 3
        
    def create_stone_ring(self):
        self.stones = []
        for i in range(self.stone_count):
            angle = (i / self.stone_count) * math.pi * 2
            self.stones.append({
                'angle': angle,
                'active': True
            })
    
    def create_glowing_stone(self, x, y):
        return {
            'x': x,
            'y': y,
            'radius': TILE_SIZE // 3,
            'core_color': (220, 220, 255),
            'glow_colors': [
                (50, 100, 255, 200),
                (100, 150, 255, 180),
                (150, 200, 255, 150),
                (200, 220, 255, 100),
            ],
            'active': True,
            'lifetime': 180,
            'chasing': True,
            'target_x': x,
            'target_y': y,
        }
    
    def throw_stone(self, player):
        if not self.stones:
            return None
            
        for stone in self.stones:
            if stone['active']:
                stone['active'] = False
                
                world_x = self.boss.rect.centerx + math.cos(self.ring_angle + stone['angle']) * self.ring_radius
                world_y = self.boss.rect.centery + math.sin(self.ring_angle + stone['angle']) * self.ring_radius
                
                glowing_stone = self.create_glowing_stone(world_x, world_y)
                glowing_stone['target_x'] = player.rect.centerx
                glowing_stone['target_y'] = player.rect.centery
                
                return glowing_stone
        return None
    
    def update(self, player, tiles):
        self.ring_angle += self.ring_speed
        
        self.throw_timer += 1
        if self.throw_timer >= self.throw_interval:
            self.throw_timer = 0
            thrown_stone = self.throw_stone(player)
            if thrown_stone:
                self.thrown_stones.append(thrown_stone)
        
        for stone in self.thrown_stones[:]:
            stone['target_x'] = player.rect.centerx
            stone['target_y'] = player.rect.centery
            
            dx_target = stone['target_x'] - stone['x']
            dy_target = stone['target_y'] - stone['y']
            dist_target = math.hypot(dx_target, dy_target)
            
            if dist_target > 1:
                stone['x'] += self.chase_speed * dx_target / dist_target
                stone['y'] += self.chase_speed * dy_target / dist_target
            
            stone['lifetime'] -= 1
            
            stone_rect = pygame.Rect(
                stone['x'] - stone['radius'],
                stone['y'] - stone['radius'],
                stone['radius'] * 2,
                stone['radius'] * 2
            )
            
            if stone_rect.colliderect(player.rect):
                player.take_damage(20)
                self.thrown_stones.remove(stone)
            
            elif stone['lifetime'] <= 0:
                self.thrown_stones.remove(stone)
    
    def draw_stone_with_glow(self, screen, x, y, stone):
        
        for i, glow_color in enumerate(stone['glow_colors']):
            glow_size = stone['radius'] + (i + 1) * 6
            
            glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            
            if len(glow_color) == 4:
                r, g, b, a = glow_color
                current_alpha = int(a * (0.8 + 0.2 * (stone['lifetime'] / 180)))
            else:
                r, g, b = glow_color
                current_alpha = int(200 * (0.8 + 0.2 * (stone['lifetime'] / 180)))
            
            for blur in range(3):
                blur_offset = blur * 2
                pygame.draw.circle(
                    glow_surf,
                    (r, g, b, current_alpha // (blur + 1)),
                    (glow_size + blur_offset, glow_size + blur_offset),
                    glow_size - blur
                )
            
            screen.blit(glow_surf, (int(x - glow_size - 2), int(y - glow_size - 2)))
        
        core_size = int(stone['radius'] * 0.9)
        core_surf = pygame.Surface((core_size * 2, core_size * 2), pygame.SRCALPHA)
        
        pygame.draw.circle(
            core_surf,
            (*stone['core_color'], 230),
            (core_size, core_size),
            core_size
        )
        
        screen.blit(core_surf, (int(x - core_size), int(y - core_size)))
        
        inner_glow_surf = pygame.Surface((core_size * 2, core_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            inner_glow_surf,
            (100, 150, 255, 120),
            (core_size, core_size),
            core_size
        )
        screen.blit(inner_glow_surf, (int(x - core_size), int(y - core_size)))
        
        pulse = math.sin(pygame.time.get_ticks() * 0.01) * 0.3 + 0.7
        ring_size = stone['radius'] + 8
        ring_surf = pygame.Surface((ring_size * 2, ring_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            ring_surf,
            (50, 100, 255, int(100 * pulse)),
            (ring_size, ring_size),
            ring_size,
            3
        )
        screen.blit(ring_surf, (int(x - ring_size), int(y - ring_size)))
    
    def draw(self, screen, camera, shake_x=0, shake_y=0):
        for stone in self.stones:
            if stone['active']:
                world_x = self.boss.rect.centerx + math.cos(self.ring_angle + stone['angle']) * self.ring_radius
                world_y = self.boss.rect.centery + math.sin(self.ring_angle + stone['angle']) * self.ring_radius
                
                screen_x = world_x - camera.scroll + shake_x
                screen_y = world_y + shake_y
                
                stone_size = TILE_SIZE // 3
                
                for i in range(3):
                    glow_size = stone_size + (i + 1) * 4
                    glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(
                        glow_surf,
                        (50, 100, 255, 80 - i * 20),
                        (glow_size, glow_size),
                        glow_size
                    )
                    screen.blit(glow_surf, (int(screen_x - glow_size), int(screen_y - glow_size)))
                
                pygame.draw.circle(screen, (200, 200, 255), (int(screen_x), int(screen_y)), stone_size)
                pygame.draw.circle(screen, (220, 220, 255), (int(screen_x - 2), int(screen_y - 2)), stone_size - 2)
        
        for stone in self.thrown_stones:
            screen_x = stone['x'] - camera.scroll + shake_x
            screen_y = stone['y'] + shake_y
            self.draw_stone_with_glow(screen, screen_x, screen_y, stone)
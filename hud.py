import pygame
import random
import math
from settings import *

class ChristmasHUD:
    def __init__(self, screen):
        self.screen = screen

        self.font_large = pygame.font.SysFont("arialblack", 16)
        self.font_medium = pygame.font.SysFont("arial", 14, bold=True)
        self.font_small = pygame.font.SysFont("arial", 12)
        self.font_tiny = pygame.font.SysFont("arial", 10)

        self.x = 15
        self.y = 15
        self.spacing = 48
        
        self.health_w = 220
        self.health_h = 42
        self.stats_w = 250
        self.stats_h = 48
        self.lives_w = 150
        self.lives_h = 40

        self.colors = {
            "bg_dark": (15, 20, 18, 200),
            "bg_medium": (25, 30, 28, 200),
            "bg_light": (35, 40, 38, 200),
            
            "gold": (255, 210, 100),
            "ice_blue": (180, 220, 255),
            "ice_blue_dark": (120, 180, 230),
            "snow_white": (240, 250, 255),
            "red": (240, 100, 100),
            "green": (120, 220, 140),
            "blue": (140, 200, 255),
            "jump_green": (100, 255, 100),
            "shield_blue": (100, 100, 255),
            
            "text_primary": (255, 255, 255),
            "text_secondary": (220, 220, 220),
            "text_dim": (170, 170, 170),
            
            "border": (90, 80, 70),
        }
        
        self.snow_particles = []
        for _ in range(25):
            self.snow_particles.append({
                'x': random.randint(0, self.health_w - 24),
                'y': random.randint(0, 12),
                'speed': random.uniform(0.2, 0.6),
                'size': random.randint(1, 2)
            })
        
        self.powerup_images = {}
        self.special_ability_image = None
        self.load_powerup_images()
        self.load_special_ability_image()
        
        self.animation_time = 0
        self.ready_particles = []
        self.create_ready_particles()
        
    def load_powerup_images(self):
        try:
            from tile_config import tile_db
            if 50 in tile_db.images:
                self.powerup_images["jump_boost"] = tile_db.images[50]
            else:
                surf = pygame.Surface((20, 20))
                surf.fill((100, 255, 100))
                self.powerup_images["jump_boost"] = surf
            
            if 51 in tile_db.images:
                self.powerup_images["shield"] = tile_db.images[51]
            else:
                surf = pygame.Surface((20, 20))
                surf.fill((100, 100, 255))
                self.powerup_images["shield"] = surf
        except Exception as e:
            surf = pygame.Surface((20, 20))
            surf.fill((100, 255, 100))
            self.powerup_images["jump_boost"] = surf
            
            surf = pygame.Surface((20, 20))
            surf.fill((100, 100, 255))
            self.powerup_images["shield"] = surf
    
    def load_special_ability_image(self):
        try:
            import os
            asset_paths = [
                os.path.join("assets", "weapons", "ice_shard.png"),
                os.path.join("sprites", "ice_shard.png")
            ]
            
            for path in asset_paths:
                if os.path.exists(path):
                    self.special_ability_image = pygame.image.load(path).convert_alpha()
                    self.special_ability_image = pygame.transform.scale(self.special_ability_image, (30, 30))
                    return
            
            surf = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.polygon(surf, (100, 200, 255), [(15, 0), (30, 15), (15, 30), (0, 15)])
            self.special_ability_image = surf
        except Exception as e:
            surf = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.polygon(surf, (100, 200, 255), [(15, 0), (30, 15), (15, 30), (0, 15)])
            self.special_ability_image = surf
    
    def create_ready_particles(self):
        for _ in range(8):
            angle = random.uniform(0, math.pi * 2)
            distance = random.uniform(15, 25)
            self.ready_particles.append({
                'angle': angle,
                'distance': distance,
                'speed': random.uniform(0.01, 0.03),
                'size': random.randint(1, 3),
                'alpha': random.randint(150, 255),
                'phase': random.uniform(0, math.pi * 2)
            })

    def draw_strip(self, x, y, w, h, color_key="bg_medium"):
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(
            surf, self.colors[color_key],
            (0, 0, w, h), border_radius=12
        )
        pygame.draw.rect(
            surf, self.colors["border"],
            (0, 0, w, h), 1, border_radius=12
        )
        self.screen.blit(surf, (x, y))

    def draw_health(self, player):
        w, h = self.health_w, self.health_h
        self.draw_strip(self.x, self.y, w, h, "bg_dark")
        
        health_text = self.font_medium.render("HP", True, (220, 220, 255))
        self.screen.blit(health_text, (self.x + 12, self.y + 6))
        
        value_text = self.font_medium.render(
            f"{player.health}/{player.max_health}", 
            True, self.colors["snow_white"]
        )
        self.screen.blit(value_text, (self.x + w - 70, self.y + 6))
        
        bar_x = self.x + 12
        bar_y = self.y + 26
        bar_w = w - 24
        bar_h = 12
        
        sky_surf = pygame.Surface((bar_w, bar_h))
        
        for y in range(bar_h):
            ratio = y / bar_h
            r = int(10 + 15 * ratio)
            g = int(10 + 10 * ratio)
            b = int(40 + 30 * (1 - ratio))
            pygame.draw.line(sky_surf, (r, g, b), (0, y), (bar_w, y))
        
        current_time = pygame.time.get_ticks()
        for i in range(10):
            star_x = (i * 20 + current_time // 400) % bar_w
            star_y = (i * 9) % bar_h
            pygame.draw.circle(sky_surf, (200, 200, 255), (star_x, star_y), 1)
        
        self.screen.blit(sky_surf, (bar_x, bar_y))
        
        ratio = max(0, min(1, player.health / player.max_health))
        fill_w = int(bar_w * ratio)
        
        if fill_w > 0:
            if ratio > 0.8:
                color = (120, 220, 255)
            elif ratio > 0.6:
                color = (100, 180, 255)
            elif ratio > 0.4:
                color = (180, 150, 255)
            elif ratio > 0.2:
                color = (220, 120, 200)
            else:
                color = (255, 100, 150)
            
            fill_surf = pygame.Surface((fill_w, bar_h), pygame.SRCALPHA)
            fill_surf.fill((*color, 200))
            self.screen.blit(fill_surf, (bar_x, bar_y))
            
            if fill_w > 2:
                edge_x = bar_x + fill_w - 2
                pygame.draw.line(self.screen, (255, 255, 255), 
                            (edge_x, bar_y), (edge_x, bar_y + bar_h - 1), 2)
        
        if not hasattr(self, 'snow_particles'):
            self.snow_particles = []
            for _ in range(20):
                self.snow_particles.append({
                    'x': random.randint(0, bar_w),
                    'y': random.randint(0, bar_h),
                    'speed': random.uniform(0.2, 0.6),
                    'size': random.randint(1, 2)
                })
        
        for particle in self.snow_particles:
            particle['y'] += particle['speed']
            
            if particle['y'] > bar_h:
                particle['y'] = 0
                particle['x'] = random.randint(0, bar_w)
            
            pygame.draw.circle(self.screen, (255, 255, 255), 
                            (bar_x + int(particle['x']), bar_y + int(particle['y'])), 
                            particle['size'])
        
        pygame.draw.rect(self.screen, (100, 120, 150), 
                        (bar_x-1, bar_y-1, bar_w+2, bar_h+2), 1, border_radius=4)

    def draw_stats(self, player, level, level_index):
        w, h = self.stats_w, self.stats_h
        y = self.y + self.spacing
        
        self.draw_strip(self.x, y, w, h, "bg_medium")
        
        level_color = self.colors["gold"]
        level_label = self.font_small.render("LEVEL", True, self.colors["text_dim"])
        self.screen.blit(level_label, (self.x + 15, y + 8))
        
        level_value = self.font_large.render(
            f"{level_index + 1}", True, level_color
        )
        self.screen.blit(level_value, (self.x + 75, y + 6))
        
        total_text = self.font_small.render(
            f"/{len(LEVEL_FILES)}", True, self.colors["text_dim"]
        )
        self.screen.blit(total_text, (self.x + 100, y + 12))
        
        divider_x = self.x + 135
        pygame.draw.line(self.screen, self.colors["border"],
                        (divider_x, y + 8), (divider_x, y + h - 8), 2)
        
        gift_label = self.font_small.render("GIFT", True, self.colors["text_dim"])
        self.screen.blit(gift_label, (self.x + 155, y + 8))
        
        if level.total_gifts_in_level > 0:
            carrying = player.presents_collected
            total = level.total_gifts_in_level
            
            gift_color = self.colors["gold"] if carrying > 0 else self.colors["text_dim"]
            
            gift_value = self.font_large.render(
                f"{carrying}", True, gift_color
            )
            self.screen.blit(gift_value, (self.x + 160, y + 22))
            
            total_gifts = self.font_small.render(
                f"/{total}", True, self.colors["text_dim"]
            )
            self.screen.blit(total_gifts, (self.x + 195, y + 26))
        else:
            no_gifts = self.font_small.render("0", True, self.colors["text_dim"])
            self.screen.blit(no_gifts, (self.x + 160, y + 22))
            total_gifts = self.font_small.render("/0", True, self.colors["text_dim"])
            self.screen.blit(total_gifts, (self.x + 180, y + 26))

    def draw_lives(self, player):
        w, h = self.lives_w, self.lives_h
        y = self.y + self.spacing * 2 + 5
        
        self.draw_strip(self.x, y, w, h, "bg_light")
        
        lives_label = self.font_small.render("LIVES", True, self.colors["text_dim"])
        self.screen.blit(lives_label, (self.x + 12, y + 6))
        
        lives_left = player.get_respawns_left()
        lives_color = self.colors["green"] if lives_left > 1 else self.colors["red"]
        
        lives_value = self.font_large.render(
            str(lives_left), True, lives_color
        )
        self.screen.blit(lives_value, (self.x + w - 30, y + 18))
        
        snowball_x = self.x + 55
        snowball_y = y + 22
        for i in range(3):
            if i < lives_left:
                pygame.draw.circle(self.screen, self.colors["snow_white"], 
                                 (snowball_x + i*18, snowball_y), 7)
                pygame.draw.circle(self.screen, (200, 220, 255), 
                                 (snowball_x + i*18 - 1, snowball_y - 1), 5)
                pygame.draw.circle(self.screen, (255, 255, 255), 
                                 (snowball_x + i*18 - 2, snowball_y - 2), 2)
            else:
                pygame.draw.circle(self.screen, (80, 80, 80), 
                                 (snowball_x + i*18, snowball_y), 6)
                pygame.draw.circle(self.screen, (60, 60, 60), 
                                 (snowball_x + i*18 - 1, snowball_y - 1), 4)

    def draw_powerups(self, player):
        if player.powerups["jump_boost"] == 0 and player.powerups["shield"] == 0:
            return
        
        x = SCREEN_WIDTH - 200
        y = 15
        spacing = 50
        
        if player.powerups["jump_boost"] > 0:
            img = self.powerup_images["jump_boost"]
            img_rect = img.get_rect(topleft=(x, y))
            
            if player.active_powerup == "jump_boost":
                glow_surf = pygame.Surface((img_rect.width + 8, img_rect.height + 8), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (100, 255, 100, 100), 
                                 (glow_surf.get_width()//2, glow_surf.get_height()//2), 15)
                self.screen.blit(glow_surf, (x - 4, y - 4))
                
                seconds = player.powerup_timer // 60
                timer_text = self.font_tiny.render(f"{seconds}s", True, self.colors["jump_green"])
                self.screen.blit(timer_text, (x + 25, y + 25))
            
            self.screen.blit(img, img_rect)
            
            count_text = self.font_small.render(f"x{player.powerups['jump_boost']}", True, self.colors["text_primary"])
            self.screen.blit(count_text, (x + 25, y + 5))
            
            key_text = self.font_tiny.render("1", True, self.colors["gold"])
            self.screen.blit(key_text, (x + 5, y - 8))
        
        if player.powerups["shield"] > 0:
            shield_x = x + spacing
            
            img = self.powerup_images["shield"]
            img_rect = img.get_rect(topleft=(shield_x, y))
            
            if player.active_powerup == "shield":
                glow_surf = pygame.Surface((img_rect.width + 8, img_rect.height + 8), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (100, 100, 255, 100), 
                                 (glow_surf.get_width()//2, glow_surf.get_height()//2), 15)
                self.screen.blit(glow_surf, (shield_x - 4, y - 4))
                
                seconds = player.powerup_timer // 60
                timer_text = self.font_tiny.render(f"{seconds}s", True, self.colors["shield_blue"])
                self.screen.blit(timer_text, (shield_x + 25, y + 25))
            
            self.screen.blit(img, img_rect)
            
            count_text = self.font_small.render(f"x{player.powerups['shield']}", True, self.colors["text_primary"])
            self.screen.blit(count_text, (shield_x + 25, y + 5))
            
            key_text = self.font_tiny.render("2", True, self.colors["gold"])
            self.screen.blit(key_text, (shield_x + 5, y - 8))

    def draw_special_ability(self, player):
        if not hasattr(player, 'special_ability_available') or not player.special_ability_available:
            return
        
        self.animation_time += 1
        
        x = 15
        y = 20
        icon_size = 30
        base_radius = icon_size // 2 + 5
        
        center_x = x + icon_size // 2
        center_y = y + icon_size // 2
        
        if player.special_ability_cooldown == 0:
            glow_alpha = int(60 + 30 * math.sin(self.animation_time * 0.03))
            glow_surf = pygame.Surface((icon_size + 12, icon_size + 12), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (100, 180, 255, glow_alpha), 
                             (icon_size//2 + 6, icon_size//2 + 6), icon_size//2 + 5)
            self.screen.blit(glow_surf, (x - 6, y - 6))
        
        pygame.draw.circle(self.screen, (20, 25, 35), (center_x, center_y), base_radius)
        border_color = (150, 200, 255) if player.special_ability_cooldown == 0 else (80, 100, 120)
        pygame.draw.circle(self.screen, border_color, (center_x, center_y), base_radius, 2)
        
        if self.special_ability_image:
            scaled_image = pygame.transform.scale(self.special_ability_image, (icon_size, icon_size))
            
            if player.special_ability_cooldown > 0:
                gray_overlay = pygame.Surface(scaled_image.get_size(), pygame.SRCALPHA)
                gray_overlay.fill((100, 100, 100, 160))
                scaled_image.blit(gray_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            img_rect = scaled_image.get_rect(center=(center_x, center_y))
            self.screen.blit(scaled_image, img_rect)
        
        if player.special_ability_cooldown == 0:
            shimmer_offset = (self.animation_time * 3) % 60
            for i in range(2):
                line_x = center_x - 15 + i * 15 + shimmer_offset
                if center_x - 18 <= line_x <= center_x + 18:
                    line_surf = pygame.Surface((20, 12), pygame.SRCALPHA)
                    alpha = int(80 + 40 * math.sin(self.animation_time * 0.1 + i))
                    pygame.draw.line(line_surf, (255, 255, 255, alpha), 
                                   (0, 5), (12, 0), 2)
                    self.screen.blit(line_surf, (int(line_x - 8), int(center_y - 18)))
        
        if player.special_ability_cooldown > 0:
            for _ in range(2):
                angle = (self.animation_time * 0.02 + _ * 3) % (math.pi * 2)
                dist = base_radius + 6
                px = center_x + math.cos(angle) * dist
                py = center_y + math.sin(angle) * dist
                size = random.randint(1, 2)
                alpha = random.randint(80, 150)
                
                snowflake_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(snowflake_surf, (180, 220, 255, alpha), 
                                 (size, size), size)
                self.screen.blit(snowflake_surf, (int(px - size), int(py - size)))
        
        if player.special_ability_cooldown > 0:
            progress = 1 - (player.special_ability_cooldown / player.special_ability_cooldown_max)
            
            for i in range(2):
                arc_radius = base_radius - 1 + i
                thickness = 2 - i
                alpha = 180 - i * 50
                
                step = 5
                for angle in range(0, int(360 * progress), step):
                    rad_angle = math.radians(angle)
                    px = center_x + arc_radius * math.cos(rad_angle)
                    py = center_y + arc_radius * math.sin(rad_angle)
                    
                    dot_surf = pygame.Surface((thickness*2, thickness*2), pygame.SRCALPHA)
                    pygame.draw.circle(dot_surf, (100, 200, 255, alpha), 
                                     (thickness, thickness), thickness)
                    self.screen.blit(dot_surf, (int(px - thickness), int(py - thickness)))

    def draw_progress(self, player, level):
        playable = level.level_width - TILE_SIZE * 4
        progress = max(0, player.rect.x - TILE_SIZE * 2)
        ratio = min(1, progress / playable) if playable > 0 else 0
        
        bar_h = 5
        bar_y = SCREEN_HEIGHT - bar_h - 3
        
        pygame.draw.rect(self.screen, (50, 50, 50),
                        (0, bar_y, SCREEN_WIDTH, bar_h))
        
        if ratio > 0:
            fill_w = int(SCREEN_WIDTH * ratio)
            pygame.draw.rect(self.screen, self.colors["gold"],
                           (0, bar_y, fill_w, bar_h))

    def draw_controls(self):
        y = SCREEN_HEIGHT - 18
        
        controls = [
            ("WASD", "Move"),
            ("SPACE", "Jump"),
            ("F", "Shoot"),
            ("1/2", "Powerups"),
            ("Q", "Special"),
            ("R", "Restart"),
        ]
        
        text_x = 15
        for key, action in controls:
            key_surf = self.font_tiny.render(key, True, self.colors["gold"])
            self.screen.blit(key_surf, (text_x, y - 8))
            
            action_surf = self.font_tiny.render(action, True, self.colors["text_dim"])
            self.screen.blit(action_surf, (text_x + key_surf.get_width() + 4, y - 8))
            
            text_x += key_surf.get_width() + action_surf.get_width() + 20

    def draw_debug(self, player, camera):
        debug_text = self.font_tiny.render(
            f"Cam:{int(camera.scroll)} X:{player.rect.x} Y:{player.rect.y} G:{int(player.grounded)}",
            True, (255, 255, 100)
        )
        self.screen.blit(debug_text, (SCREEN_WIDTH - 280, SCREEN_HEIGHT - 16))

    def draw(self, player, level, current_level_index, show_debug=False, camera=None):
        self.draw_health(player)
        self.draw_stats(player, level, current_level_index)
        self.draw_lives(player)
        self.draw_special_ability(player)
        self.draw_powerups(player)
        self.draw_progress(player, level)
        self.draw_controls()

        if show_debug and camera:
            self.draw_debug(player, camera)
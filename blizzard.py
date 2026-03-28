import pygame
import random
import math
import os
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE
from sound_manager import sound_manager

FREEZE_DURATION = 90
STORM_DURATION = 900
POST_STORM_DELAY = 180
FADE_DURATION = 120
SMOKE_STAY_TIME = 300
SMOKE_FADE_TIME = 120
COOLDOWN_MIN = 1200
COOLDOWN_MAX = 1800
DAMAGE_PER_TICK = 35
DAMAGE_INTERVAL = 30
SNOWFLAKE_COUNT = 100
SNOWBALL_COUNT = 20
TRAIL_LENGTH = 15
SPAWN_DELAY = 10
SPAWN_CHANCE = 0.15
SHAKE_BASE_INTENSITY = 8
FREEZE_ALPHA_SPEED = 5
MAX_OVERLAY_ALPHA = 200
GROUND_SMOKE_COUNT = 50

TRAIL_SURFACES = []
for size in range(1, 50):
    surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
    pygame.draw.circle(surf, (200, 220, 255, 180), (size, size), size)
    TRAIL_SURFACES.append(surf)

class SnowParticle:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(-100, 0)
        self.size = random.randint(1, 3)
        self.speed = random.uniform(2, 5)
        self.drift = random.uniform(-0.5, 0.5)
        self.alpha = random.randint(150, 255)
        
    def update(self):
        self.x += self.drift
        self.y += self.speed
        
        if self.y > SCREEN_HEIGHT:
            self.reset()
            
    def draw(self, screen):
        if self.y < SCREEN_HEIGHT:
            pygame.draw.circle(screen, (255, 255, 255, self.alpha), 
                             (int(self.x), int(self.y)), self.size)

class GroundSmoke:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = SCREEN_HEIGHT - random.randint(0, 60)
        self.layer = random.choice([0, 1, 2])
        
        if self.layer == 0:
            self.size = random.randint(20, 40)
            self.speed = random.uniform(-0.4, -0.1)
            self.drift = random.uniform(-0.1, 0.1)
            self.alpha = random.randint(40, 80)
            self.color = (180, 200, 230)
        elif self.layer == 1:
            self.size = random.randint(15, 30)
            self.speed = random.uniform(-0.6, -0.2)
            self.drift = random.uniform(-0.2, 0.2)
            self.alpha = random.randint(60, 120)
            self.color = (200, 220, 240)
        else:
            self.size = random.randint(10, 20)
            self.speed = random.uniform(-0.8, -0.3)
            self.drift = random.uniform(-0.3, 0.3)
            self.alpha = random.randint(80, 160)
            self.color = (220, 240, 255)
        
        self.life = random.randint(90, 150)
        self.max_life = self.life
        self.current_alpha = self.alpha
        
    def update(self):
        self.x += self.drift
        self.y += self.speed
        self.life -= 1
        
        self.drift += random.uniform(-0.02, 0.02)
        self.drift = max(-0.6, min(0.6, self.drift))
        
        life_ratio = self.life / self.max_life
        self.current_alpha = int(self.alpha * life_ratio)
        
        self.size += 0.03
        
        if self.life <= 0 or self.y < SCREEN_HEIGHT - 200:
            self.reset()
            
    def draw(self, screen, fade_factor=1.0):
        if self.life > 0:
            screen_ratio = (SCREEN_HEIGHT - self.y) / 200
            edge_fade = max(0.3, min(1.0, screen_ratio))
            
            final_alpha = int(self.current_alpha * fade_factor * edge_fade)
            
            for i in range(3):
                blur_size = int(self.size * (1 + i * 0.2))
                blur_alpha = final_alpha // (i + 2)
                blur_surf = pygame.Surface((blur_size*2, blur_size*2), pygame.SRCALPHA)
                
                center = blur_size
                for r in range(blur_size, 0, -blur_size//3):
                    step_alpha = blur_alpha * (r / blur_size)
                    pygame.draw.circle(blur_surf, (*self.color, int(step_alpha)), 
                                     (center, center), r)
                
                screen.blit(blur_surf, (int(self.x - blur_size), int(self.y - blur_size)))

class ImpactParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-5, -1)
        self.size = random.randint(2, 4)
        self.alpha = 255
        self.life = random.randint(15, 25)
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2
        self.life -= 1
        self.alpha = int(255 * (self.life / 25))
        
    def draw(self, screen, camera_offset=0):
        if self.life > 0:
            pygame.draw.circle(screen, (255, 255, 255, self.alpha), 
                             (int(self.x - camera_offset), int(self.y)), self.size)

class WindStreak:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.x = random.randint(-100, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.speed = random.uniform(8, 20)
        self.length = random.randint(15, 40)
        self.alpha = random.randint(40, 120)
        self.thickness = random.randint(1, 2)
        
    def update(self):
        self.x += self.speed
        if self.x > SCREEN_WIDTH + self.length:
            self.reset()
            self.x = random.randint(-100, -50)
            self.y = random.randint(0, SCREEN_HEIGHT)
    
    def draw(self, screen, intensity):
        alpha = int(self.alpha * intensity)
        pygame.draw.line(
            screen,
            (220, 230, 255, alpha),
            (self.x, self.y),
            (self.x + self.length, self.y + self.length // 3),
            self.thickness
        )

class BlizzardSnowball:
    def __init__(self, image):
        self.image = image
        self.original_image = image.copy()
        self.last_hit_time = 0
        self.reset()
        
    def reset(self):
        self.x = random.randint(-150, SCREEN_WIDTH + 150)
        self.y = random.randint(-400, -150)
        
        base_size = self.image.get_width() // 2
        size_variation = random.uniform(0.9, 1.1)
        self.size = int(base_size * size_variation)
        
        direction = random.choice([-1, 1])
        self.vx = random.uniform(0.5, 1.5) * direction
        self.vy = random.uniform(8, 14)
        self.base_vy = self.vy
        
        self.angle = random.uniform(0, 360)
        self.rotation_speed = random.uniform(10, 18) * random.choice([-1, 1])
        
        self.trail = []
        self.trail_length = TRAIL_LENGTH
        self.trail_positions = []
        
        self.wobble = random.uniform(-0.3, 0.3)
        self.wobble_speed = random.uniform(0.03, 0.06)
        self.wobble_angle = random.uniform(0, math.pi * 2)
        
    def update(self, intensity=1.0):
        self.trail_positions.append((self.x, self.y))
        if len(self.trail_positions) > self.trail_length:
            self.trail_positions.pop(0)
        
        self.wobble_angle += self.wobble_speed
        wobble_x = math.sin(self.wobble_angle) * self.wobble
        
        self.angle += self.rotation_speed
        if self.angle >= 360:
            self.angle -= 360
        
        current_vy = self.base_vy + (intensity * 3)
        
        self.x += self.vx + wobble_x
        self.y += current_vy
        
        if self.y > SCREEN_HEIGHT + 300 or self.x > SCREEN_WIDTH + 400 or self.x < -400:
            self.reset()
    
    def draw_trail(self, screen, camera_offset=0):
        for i, pos in enumerate(self.trail_positions):
            progress = i / len(self.trail_positions) if self.trail_positions else 0
            alpha = int(200 * progress)
            size = max(2, int(self.size * 0.4 * progress))
            
            if size < len(TRAIL_SURFACES):
                trail_surf = TRAIL_SURFACES[size].copy()
                trail_surf.set_alpha(alpha)
            else:
                trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                trail_color = (200, 220, 255, alpha)
                pygame.draw.circle(trail_surf, trail_color, (size, size), size)
            
            screen_x = pos[0] - camera_offset - size
            screen_y = pos[1] - size
            screen.blit(trail_surf, (screen_x, screen_y))
    
    def draw(self, screen, camera_offset=0):
        self.draw_trail(screen, camera_offset)
        
        rotated = pygame.transform.rotate(self.original_image, self.angle)
        rect = rotated.get_rect(center=(self.x - camera_offset, self.y))
        screen.blit(rotated, rect)


class BlizzardStorm:
    def __init__(self):
        self.active = False
        self.freeze_active = False
        self.freeze_timer = 0
        self.storm_timer = 0
        self.post_storm_timer = 0
        self.fade_timer = 0
        self.cooldown_timer = 0
        
        self.smoke_active = False
        self.smoke_timer = 0
        self.smoke_fade_timer = 0
        self.SMOKE_STAY_TIME = SMOKE_STAY_TIME
        self.SMOKE_FADE_TIME = SMOKE_FADE_TIME
        
        self.freeze_duration = FREEZE_DURATION
        self.storm_duration = STORM_DURATION
        self.post_storm_delay = POST_STORM_DELAY
        self.fade_duration = FADE_DURATION
        self.cooldown_duration = random.randint(COOLDOWN_MIN, COOLDOWN_MAX)
        
        self.damage_timer = 0
        self.damage_interval = DAMAGE_INTERVAL
        self.damage_per_tick = DAMAGE_PER_TICK
        
        self.snow_particles = [SnowParticle() for _ in range(SNOWFLAKE_COUNT)]
        
        self.ground_smoke = [GroundSmoke() for _ in range(GROUND_SMOKE_COUNT)]
        
        self.impact_particles = []
        self.impact_flash_alpha = 0
        self.impact_flash_timer = 0
        
        self.snowball_image = None
        self.load_snowball_image()
        
        self.snowballs = []
        self.snowball_count = SNOWBALL_COUNT
        self.create_snowballs()
        
        self.wind_streaks = [WindStreak() for _ in range(30)]
        
        self.frost_overlay = None
        self.create_frost_overlay()
        
        self.spawn_timer = 0
        self.spawn_delay = SPAWN_DELAY
        
        self.shake_timer = 0
        self.shake_intensity = SHAKE_BASE_INTENSITY
        self.shake_duration = 0
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        
        self.wind_music_playing = False
        self.warning_played = False
        self.current_music_volume = 0.3
        self.current_music_track = "level2.mp3"
        self.wind_volume = 0.3
        
        self.wind_sound_path = "sounds/hazard/blizzard_wind.mp3"
        
        self.transition_alpha = 0
        
    def load_snowball_image(self):
        try:
            possible_paths = [
                os.path.join("assets", "weapons", "blizzard_snowball.png"), 
            ]
            
            for path in possible_paths:
                try:
                    original = pygame.image.load(path).convert_alpha()
                    target_size = random.randint(TILE_SIZE, int(TILE_SIZE * 1.5))
                    self.snowball_image = pygame.transform.scale(
                        original, 
                        (target_size, target_size)
                    )
                    return
                except Exception as e:
                    continue
            
            size = TILE_SIZE
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 255, 255), (size//2, size//2), size//2)
            pygame.draw.circle(surf, (200, 230, 255), (size//2 - 2, size//2 - 2), size//2 - 3)
            self.snowball_image = surf
            
        except Exception as e:
            size = TILE_SIZE
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 255, 255), (size//2, size//2), size//2)
            self.snowball_image = surf

    def create_snowballs(self):
        for _ in range(self.snowball_count):
            snowball = BlizzardSnowball(self.snowball_image)
            self.snowballs.append(snowball)
    
    def create_frost_overlay(self):
        self.frost_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        max_dist = math.sqrt(center_x**2 + center_y**2)
        
        for y in range(SCREEN_HEIGHT):
            for x in range(SCREEN_WIDTH):
                dx = x - center_x
                dy = y - center_y
                dist = math.sqrt(dx*dx + dy*dy)
                
                edge_factor = min(1.0, dist / (max_dist * 0.7))
                
                if edge_factor > 0.3:
                    alpha = int(100 * (edge_factor - 0.3) / 0.7)
                    self.frost_overlay.set_at((x, y), (180, 220, 255, alpha))
    
    def start_wind_sound(self):
        try:
            if not self.wind_music_playing and os.path.exists(self.wind_sound_path):
                pygame.mixer.music.load(self.wind_sound_path)
                pygame.mixer.music.set_volume(self.wind_volume)
                pygame.mixer.music.play(-1)
                self.wind_music_playing = True
        except Exception as e:
            pass
    
    def stop_wind_sound(self):
        if self.wind_music_playing:
            pygame.mixer.music.stop()
            self.wind_music_playing = False
    
    def update_wind_volume(self, intensity):
        if self.wind_music_playing:
            target_volume = 0.2 + (intensity * 0.3)
            pygame.mixer.music.set_volume(target_volume)
    
    def trigger(self):
        if not self.active and not self.freeze_active and self.cooldown_timer <= 0:
            self.freeze_active = True
            self.freeze_timer = self.freeze_duration
            self.storm_timer = 0
            self.post_storm_timer = 0
            self.fade_timer = 0
            self.transition_alpha = 0
            self.warning_played = False
            
            if sound_manager:
                self.current_music_volume = sound_manager.volumes.get("level2", 0.3)
                self.current_music_track = sound_manager.current_music
                sound_manager.set_music_track_volume("level2", 0.0)
            
            return True
        return False
    
    def create_impact_effect(self, x, y):
        for _ in range(5):
            self.impact_particles.append(ImpactParticle(x, y))
        self.impact_flash_alpha = 40
        self.impact_flash_timer = 5
    
    def draw_ice_text(self, screen, text, y_offset=0, size=48):
        font = pygame.font.SysFont('Futura', size, bold=True)
        
        dark_blue = (10, 20, 50)
        ice_blue = (180, 220, 255)
        white = (255, 255, 255)
        
        text_surf = font.render(text, True, white)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + y_offset))
        
        for i in range(5, 0, -1):
            offset = i * 2
            gradient_factor = i / 5
            r = int(dark_blue[0] + (ice_blue[0] - dark_blue[0]) * gradient_factor)
            g = int(dark_blue[1] + (ice_blue[1] - dark_blue[1]) * gradient_factor)
            b = int(dark_blue[2] + (ice_blue[2] - dark_blue[2]) * gradient_factor)
            
            glow_surf = font.render(text, True, (r, g, b))
            glow_surf.set_alpha(80 - i * 10)
            
            for dx, dy in [(offset, 0), (-offset, 0), (0, offset), (0, -offset)]:
                glow_rect = text_rect.copy()
                glow_rect.x += dx
                glow_rect.y += dy
                screen.blit(glow_surf, glow_rect)
        
        for i in range(3):
            shimmer = font.render(text, True, ice_blue)
            shimmer.set_alpha(100 - i * 30)
            shimmer_rect = text_rect.copy()
            shimmer_rect.x += i
            shimmer_rect.y += i
            screen.blit(shimmer, shimmer_rect)
        
        screen.blit(text_surf, text_rect)
        
        for _ in range(8):
            sparkle_x = text_rect.centerx + random.randint(-text_rect.width//2 - 20, text_rect.width//2 + 20)
            sparkle_y = text_rect.centery + random.randint(-text_rect.height//2 - 10, text_rect.height//2 + 10)
            sparkle_size = random.randint(2, 4)
            sparkle_alpha = random.randint(100, 200)
            
            for i in range(2):
                pygame.draw.line(screen, (ice_blue[0], ice_blue[1], ice_blue[2], sparkle_alpha),
                               (sparkle_x - sparkle_size, sparkle_y),
                               (sparkle_x + sparkle_size, sparkle_y), 1)
                pygame.draw.line(screen, (ice_blue[0], ice_blue[1], ice_blue[2], sparkle_alpha),
                               (sparkle_x, sparkle_y - sparkle_size),
                               (sparkle_x, sparkle_y + sparkle_size), 1)
    
    def update(self, player, tiles):
        
        if not player or not tiles:
            return
        
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1
        
        if self.active or self.freeze_active:
            for particle in self.snow_particles:
                particle.update()
        
        if self.smoke_active:
            for smoke in self.ground_smoke:
                smoke.update()
            
            if not self.active:
                if self.smoke_timer > 0:
                    self.smoke_timer -= 1
                elif self.smoke_fade_timer > 0:
                    self.smoke_fade_timer -= 1
        
        if self.freeze_active:
            self.freeze_timer -= 1
            self.transition_alpha = min(MAX_OVERLAY_ALPHA, 
                                      self.transition_alpha + FREEZE_ALPHA_SPEED)
            
            if not self.warning_played and sound_manager:
                sound_manager.play_sound(sound_manager.hazard_sounds, "blizzard_warning", volume_scale=1.0)
                self.warning_played = True
            
            if self.freeze_timer <= 0:
                self.freeze_active = False
                self.active = True
                self.storm_timer = self.storm_duration
                self.shake_duration = self.storm_duration
                self.transition_alpha = 0
                self.start_wind_sound()
                
                self.smoke_active = True
                self.smoke_timer = self.SMOKE_STAY_TIME
                self.smoke_fade_timer = self.SMOKE_FADE_TIME
        
        if self.active:
            self.storm_timer -= 1
            
            intensity = 1 - (self.storm_timer / self.storm_duration)
            self.update_wind_volume(intensity)
            
            self.shake_duration -= 1
            if self.shake_duration > 0:
                shake_amount = self.shake_intensity * (intensity ** 2)
                self.shake_offset_x = random.randint(-int(shake_amount), int(shake_amount))
                self.shake_offset_y = random.randint(-int(shake_amount // 2), int(shake_amount // 2))
            else:
                self.shake_offset_x = 0
                self.shake_offset_y = 0
            
            for streak in self.wind_streaks:
                streak.update()
            
            current_time = pygame.time.get_ticks()
            for snowball in self.snowballs:
                snowball.update(intensity)
                
                self.damage_timer += 1
                if self.damage_timer >= self.damage_interval:
                    self.damage_timer = 0
                    under_cover = self.check_cover(player, tiles)
                    if not under_cover and not player.shield_active:
                        player.take_damage(self.damage_per_tick)
                        self.create_impact_effect(player.rect.centerx, player.rect.centery)
                
                snowball_rect = pygame.Rect(
                    snowball.x - snowball.size,
                    snowball.y - snowball.size,
                    snowball.size * 2,
                    snowball.size * 2
                )
                
                if snowball_rect.colliderect(player.rect):
                    if current_time - snowball.last_hit_time > 500:
                        under_cover = self.check_cover(player, tiles)
                        if not under_cover and not player.shield_active:
                            player.take_damage(self.damage_per_tick)
                            snowball.last_hit_time = current_time
                            self.create_impact_effect(snowball.x, snowball.y)
                
                if snowball.y > SCREEN_HEIGHT - 50:
                    if random.random() < 0.1:
                        self.create_impact_effect(snowball.x, SCREEN_HEIGHT - 30)
            
            for particle in self.impact_particles[:]:
                particle.update()
                if particle.life <= 0:
                    self.impact_particles.remove(particle)
            
            if self.impact_flash_timer > 0:
                self.impact_flash_timer -= 1
                self.impact_flash_alpha = max(0, self.impact_flash_alpha - 8)
            
            if self.storm_timer <= 0:
                self.active = False
                self.post_storm_timer = self.post_storm_delay
                self.fade_timer = self.fade_duration
                self.shake_offset_x = 0
                self.shake_offset_y = 0
                
                for snowball in self.snowballs:
                    snowball.reset()
                    snowball.trail_positions.clear()
                
                self.impact_particles.clear()
                self.impact_flash_alpha = 0
                self.impact_flash_timer = 0
                
                self.stop_wind_sound()
                
                if sound_manager:
                    sound_manager.set_music_track_volume("level2", self.current_music_volume)
                    sound_manager.play_music(self.current_music_track)
    
    def check_cover(self, player, tiles):
        player_top = player.rect.top
        
        for tile in tiles:
            if hasattr(tile, 'solid') and tile.solid:
                tile_rect = tile.rect
                if (tile_rect.bottom <= player_top and 
                    abs(tile_rect.centerx - player.rect.centerx) < TILE_SIZE):
                    return True
        return False
    
    def draw_warning(self, screen):
        if not self.freeze_active:
            return
        
        freeze_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        freeze_overlay.fill((40, 80, 120, self.transition_alpha))
        screen.blit(freeze_overlay, (0, 0))
        
        self.draw_ice_text(screen, "BLIZZARD APPROACHING", -50, 72)
        self.draw_ice_text(screen, "FIND COVER!", 20, 48)
        
        seconds_left = (self.freeze_timer // 60) + 1
        countdown_text = f"{seconds_left}"
        countdown_font = pygame.font.SysFont('Futura', 72, bold=True)
        
        for i in range(5, 0, -1):
            offset = i * 2
            glow = countdown_font.render(countdown_text, True, (20, 40, 80))
            glow.set_alpha(60 - i * 8)
            for dx, dy in [(offset, 0), (-offset, 0), (0, offset), (0, -offset)]:
                screen.blit(glow, (SCREEN_WIDTH//2 - glow.get_width()//2 + dx, 
                                   SCREEN_HEIGHT//2 + 100 - glow.get_height()//2 + dy))
        
        countdown_surf = countdown_font.render(countdown_text, True, (255, 255, 255))
        screen.blit(countdown_surf, (SCREEN_WIDTH//2 - countdown_surf.get_width()//2, 
                                    SCREEN_HEIGHT//2 + 100 - countdown_surf.get_height()//2))
    
    def draw(self, screen, camera_offset=0):
        
        if self.smoke_active:
            if self.active:
                fade_factor = 1.0
            elif self.smoke_timer > 0:
                fade_factor = 1.0
            else:
                fade_factor = self.smoke_fade_timer / self.SMOKE_FADE_TIME
            
            for layer in (0, 1, 2):
                for smoke in self.ground_smoke:
                    if smoke.layer == layer:
                        smoke.draw(screen, fade_factor)
            
            if self.smoke_timer <= 0 and self.smoke_fade_timer <= 0:
                self.smoke_active = False
        
        if self.active or self.freeze_active:
            for particle in self.snow_particles:
                particle.draw(screen)
        
        if self.active or self.freeze_active:
            for snowball in self.snowballs:
                snowball.draw(screen, camera_offset)
        
        if self.active:
            intensity = 1 - (self.storm_timer / self.storm_duration) if self.storm_timer > 0 else 1
            for streak in self.wind_streaks:
                streak.draw(screen, intensity)
        
        for particle in self.impact_particles:
            particle.draw(screen, camera_offset)
        
        if self.impact_flash_alpha > 0:
            flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            flash.fill((180, 220, 255, self.impact_flash_alpha))
            screen.blit(flash, (0, 0))
        
        if self.active:
            intensity = 1 - (self.storm_timer / self.storm_duration) if self.storm_timer > 0 else 1
            if self.frost_overlay:
                self.frost_overlay.set_alpha(int(180 * intensity))
                screen.blit(self.frost_overlay, (0, 0))
        
        self.draw_warning(screen)
        
        if self.active:
            grade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            intensity = 1 - (self.storm_timer / self.storm_duration) if self.storm_timer > 0 else 1
            grade.fill((40, 70, 120, int(30 * intensity)))
            screen.blit(grade, (0, 0))
    
    def get_shake_offset(self):
        return (self.shake_offset_x, self.shake_offset_y)
    
    def is_frozen(self):
        return self.freeze_active
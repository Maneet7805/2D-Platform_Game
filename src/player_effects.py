import pygame
import math
import random
import os
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE

class PlayerEffects:
    def __init__(self):
        self.ice_effect_alpha = 0
        self.ice_effect_max_alpha = 255
        self.ice_effect_fade_speed = 25
        
        self.damage_effect_alpha = 0
        
        self.damage_vignette = None
        self.ice_vignette = None
        self._create_vignette_textures()
        
    def _create_vignette_textures(self):
        
        self.damage_vignette = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        max_distance = int((SCREEN_WIDTH ** 2 + SCREEN_HEIGHT ** 2) ** 0.5 // 2)
        
        for x in range(0, SCREEN_WIDTH, 2):
            for y in range(0, SCREEN_HEIGHT, 2):
                dx = x - center_x
                dy = y - center_y
                distance = (dx ** 2 + dy ** 2) ** 0.5
                
                if distance > max_distance * 0.5:
                    edge_factor = (distance - max_distance * 0.5) / (max_distance * 0.5)
                    edge_factor = max(0, min(1, edge_factor))
                    alpha = int(220 * edge_factor)
                    
                    if alpha > 10:
                        pygame.draw.rect(self.damage_vignette, (180, 0, 0, alpha), (x, y, 2, 2))
        
        for _ in range(40):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(max_distance * 0.6, max_distance)
            x = center_x + int(math.cos(angle) * dist)
            y = center_y + int(math.sin(angle) * dist)
            
            if 0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT:
                drop_length = random.randint(8, 15)
                drop_width = random.randint(3, 6)
                alpha = random.randint(150, 220)
                
                for i in range(drop_length):
                    drop_x = x + random.randint(-2, 2)
                    drop_y = y + i
                    if 0 <= drop_x < SCREEN_WIDTH and 0 <= drop_y < SCREEN_HEIGHT:
                        fade = 1.0 - (i / drop_length)
                        drop_alpha = int(alpha * fade)
                        pygame.draw.circle(
                            self.damage_vignette,
                            (200, 0, 0, drop_alpha),
                            (drop_x, drop_y),
                            max(1, int(drop_width * fade))
                        )
        
        self.ice_vignette = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        for x in range(0, SCREEN_WIDTH, 2):
            for y in range(0, SCREEN_HEIGHT, 2):
                dx = x - center_x
                dy = y - center_y
                distance = (dx ** 2 + dy ** 2) ** 0.5
                
                if distance > max_distance * 0.4:
                    edge_factor = (distance - max_distance * 0.4) / (max_distance * 0.6)
                    edge_factor = max(0, min(1, edge_factor))
                    alpha = int(180 * edge_factor)
                    
                    if alpha > 10:
                        pygame.draw.rect(self.ice_vignette, (100, 200, 255, alpha), (x, y, 2, 2))
        
        for _ in range(60):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(max_distance * 0.3, max_distance)
            x = center_x + int(math.cos(angle) * dist)
            y = center_y + int(math.sin(angle) * dist)
            
            if 0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT:
                flake_size = random.randint(3, 7)
                alpha = random.randint(100, 200)
                
                for arm in range(6):
                    arm_angle = (arm / 6) * math.pi * 2
                    for step in range(flake_size):
                        arm_x = x + int(math.cos(arm_angle) * step * 1.5)
                        arm_y = y + int(math.sin(arm_angle) * step * 1.5)
                        if 0 <= arm_x < SCREEN_WIDTH and 0 <= arm_y < SCREEN_HEIGHT:
                            fade = 1.0 - (step / flake_size)
                            arm_alpha = int(alpha * fade)
                            pygame.draw.circle(
                                self.ice_vignette,
                                (220, 240, 255, arm_alpha),
                                (arm_x, arm_y),
                                1
                            )
                
                pygame.draw.circle(
                    self.ice_vignette,
                    (255, 255, 255, alpha),
                    (x, y),
                    2
                )
    
    def update_ice_effect(self, on_ice):
        if on_ice:
            self.ice_effect_alpha = min(self.ice_effect_max_alpha, self.ice_effect_alpha + self.ice_effect_fade_speed)
        else:
            self.ice_effect_alpha = max(0, self.ice_effect_alpha - self.ice_effect_fade_speed)
    
    def update_damage_effect(self):
        if self.damage_effect_alpha > 0:
            self.damage_effect_alpha -= 5
            if self.damage_effect_alpha < 0:
                self.damage_effect_alpha = 0
    
    def trigger_damage_effect(self):
        self.damage_effect_alpha = 220
    
    def draw_ice_effect(self, screen, camera, player_image, player_rect):
        if self.ice_effect_alpha <= 0:
            return
        
        class TempSprite:
            def __init__(self, rect):
                self.rect = rect
        
        temp_sprite = TempSprite(player_rect)
        player_pos = camera.apply(temp_sprite)
        
        player_img = player_image.copy()
        
        lower_height = player_rect.height // 2
        start_y = player_rect.height - lower_height
        
        lower_surface = pygame.Surface((player_rect.width, lower_height), pygame.SRCALPHA)
        lower_surface.blit(player_img, (0, 0), (0, start_y, player_rect.width, lower_height))
        
        tint_surface = pygame.Surface(lower_surface.get_size())
        tint_surface.fill((40, 80, 180))
        tint_surface.set_alpha(self.ice_effect_alpha)
        
        lower_surface.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        
        screen.blit(player_img, player_pos)
        screen.blit(lower_surface, (player_pos[0], player_pos[1] + start_y))
    
    def draw_damage_effect(self, screen):
        if self.damage_effect_alpha <= 0:
            return
        
        self.damage_vignette.set_alpha(self.damage_effect_alpha)
        screen.blit(self.damage_vignette, (0, 0))
    
    def draw_ice_vignette(self, screen):
        if self.ice_effect_alpha <= 0:
            return
        
        ice_alpha = int(self.ice_effect_alpha * 0.8)
        self.ice_vignette.set_alpha(ice_alpha)
        screen.blit(self.ice_vignette, (0, 0))


class AnimationLoader:
    @staticmethod
    def load_animation(path):
        frames = []
        target_size = TILE_SIZE
        
        try:
            if path.endswith('.png'):
                try:
                    sheet = pygame.image.load(path).convert_alpha()
                    if "shoot" in path:
                        frame_count = 7
                    else:
                        frame_count = 4
                    
                    frame_width = sheet.get_width() // frame_count
                    frame_height = sheet.get_height()
                    
                    for i in range(frame_count):
                        frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                        frame.blit(sheet, (0, 0), (i * frame_width, 0, frame_width, frame_height))
                        
                        frame_rect = frame.get_bounding_rect()
                        
                        if frame_rect.width > 0 and frame_rect.height > 0:
                            sprite = pygame.Surface((frame_rect.width, frame_rect.height), pygame.SRCALPHA)
                            sprite.blit(frame, (0, 0), frame_rect)
                            
                            scale = min(target_size / sprite.get_width(), target_size / sprite.get_height())
                            new_width = int(sprite.get_width() * scale)
                            new_height = int(sprite.get_height() * scale)
                            
                            if new_width > 0 and new_height > 0:
                                scaled = pygame.transform.smoothscale(sprite, (new_width, new_height))
                            else:
                                scaled = sprite
                            
                            final_surf = pygame.Surface((target_size, target_size), pygame.SRCALPHA)
                            final_surf.blit(scaled, ((target_size - new_width) // 2, (target_size - new_height) // 2))
                            frames.append(final_surf)
                        else:
                            final_surf = pygame.Surface((target_size, target_size), pygame.SRCALPHA)
                            frames.append(final_surf)
                            
                    return frames
                    
                except Exception as e:
                    surf = pygame.Surface((target_size, target_size))
                    surf.fill((255, 0, 0))
                    frames = [surf]
                    return frames
            
            else:
                file_count = 0
                while True:
                    try:
                        img_path = f"{path}/{file_count}.png"
                        if not os.path.exists(img_path):
                            break
                            
                        img = pygame.image.load(img_path).convert_alpha()
                        
                        img_rect = img.get_bounding_rect()
                        
                        if img_rect.width > 0 and img_rect.height > 0:
                            sprite = pygame.Surface((img_rect.width, img_rect.height), pygame.SRCALPHA)
                            sprite.blit(img, (0, 0), img_rect)
                            
                            scale = min(target_size / sprite.get_width(), target_size / sprite.get_height())
                            new_width = int(sprite.get_width() * scale)
                            new_height = int(sprite.get_height() * scale)
                            
                            if new_width > 0 and new_height > 0:
                                scaled = pygame.transform.smoothscale(sprite, (new_width, new_height))
                            else:
                                scaled = sprite
                            
                            final_surf = pygame.Surface((target_size, target_size), pygame.SRCALPHA)
                            final_surf.blit(scaled, ((target_size - new_width) // 2, (target_size - new_height) // 2))
                            frames.append(final_surf)
                        else:
                            final_surf = pygame.Surface((target_size, target_size), pygame.SRCALPHA)
                            frames.append(final_surf)
                        
                        file_count += 1
                        
                    except Exception as e:
                        break
                
                if len(frames) > 0:
                    pass
                else:
                    try:
                        sheet_path = f"{path}.png"
                        if os.path.exists(sheet_path):
                            sheet = pygame.image.load(sheet_path).convert_alpha()
                            
                            if "walk" in path:
                                frame_count = 10
                            elif "run" in path:
                                frame_count = 8
                            elif "jump" in path:
                                frame_count = 6
                            elif "idle" in path:
                                frame_count = 6
                            elif "death" in path:
                                frame_count = 8
                            else:
                                frame_count = 4
                            
                            frame_width = sheet.get_width() // frame_count
                            frame_height = sheet.get_height()
                            
                            for i in range(frame_count):
                                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                                frame.blit(sheet, (0, 0), (i * frame_width, 0, frame_width, frame_height))
                                
                                frame_rect = frame.get_bounding_rect()
                                
                                if frame_rect.width > 0 and frame_rect.height > 0:
                                    sprite = pygame.Surface((frame_rect.width, frame_rect.height), pygame.SRCALPHA)
                                    sprite.blit(frame, (0, 0), frame_rect)
                                    
                                    scale = min(target_size / sprite.get_width(), target_size / sprite.get_height())
                                    new_width = int(sprite.get_width() * scale)
                                    new_height = int(sprite.get_height() * scale)
                                    
                                    if new_width > 0 and new_height > 0:
                                        scaled = pygame.transform.smoothscale(sprite, (new_width, new_height))
                                    else:
                                        scaled = sprite
                                    
                                    final_surf = pygame.Surface((target_size, target_size), pygame.SRCALPHA)
                                    final_surf.blit(scaled, ((target_size - new_width) // 2, (target_size - new_height) // 2))
                                    frames.append(final_surf)
                                else:
                                    final_surf = pygame.Surface((target_size, target_size), pygame.SRCALPHA)
                                    frames.append(final_surf)
                            
                    except Exception as e:
                        pass
                
                if len(frames) == 0:
                    surf = pygame.Surface((target_size, target_size))
                    surf.fill((255, 0, 0))
                    frames = [surf]
                    
        except Exception as e:
            surf = pygame.Surface((target_size, target_size))
            surf.fill((255, 0, 0))
            frames = [surf]

        normalized_frames = []
        for i, frame in enumerate(frames):
            if frame.get_width() == target_size and frame.get_height() == target_size:
                normalized_frames.append(frame)
            else:
                new_frame = pygame.Surface((target_size, target_size), pygame.SRCALPHA)
                new_frame.fill((0, 0, 0, 0))
                
                x_offset = (target_size - frame.get_width()) // 2
                y_offset = (target_size - frame.get_height()) // 2
                
                new_frame.blit(frame, (x_offset, y_offset))
                normalized_frames.append(new_frame)
        
        return normalized_frames
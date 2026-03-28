import pygame
import math
import random
from particles import dustParticle

class PowerupEffects:
    def __init__(self, player):
        self.player = player
        
        self.heal_effect_timer = 0
        self.heal_effect_duration = 30
        self.heal_effect_color = (100, 255, 100)
        
        self.jump_boost_streak_timer = 0
        self.jump_boost_streak_duration = 16
        
        self.shield_frames = []
        self.shield_frame_index = 0
        self.shield_frame_timer = 0
        self.shield_frame_duration = 60
        self.shield_glow_pulse = 0
        self.shield_break_effect = False
        self.shield_break_timer = 0
        self.shield_break_frame_duration = 4
        self.shield_break_frame_timer = 0
        
        self.load_shield_frames("assets/powerup/shield.png", frame_count=7)
        
    def load_shield_frames(self, path, frame_count=7):
        try:
            sheet = pygame.image.load(path).convert_alpha()
            frame_width = sheet.get_width() // frame_count
            frame_height = sheet.get_height()
            
            for i in range(frame_count):
                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame.blit(sheet, (0, 0), (i * frame_width, 0, frame_width, frame_height))
                self.shield_frames.append(frame)
        except Exception as e:
            self.shield_frames = []
    
    def trigger_heal_effect(self, color=(100, 255, 100)):
        self.heal_effect_timer = self.heal_effect_duration
        self.heal_effect_color = color
    
    def trigger_jump_boost_streak(self):
        self.jump_boost_streak_timer = self.jump_boost_streak_duration
    
    def activate_shield_effect(self):
        self.shield_frame_index = 0
        self.shield_frame_timer = 0
        self.shield_break_effect = False
        self.shield_break_timer = 0
        self.shield_glow_pulse = 0
    
    def break_shield_effect(self):
        self.shield_break_effect = True
        self.shield_break_timer = len(self.shield_frames) if self.shield_frames else 0
    
    def update(self):
        if self.heal_effect_timer > 0:
            self.heal_effect_timer -= 1
        
        if self.jump_boost_streak_timer > 0:
            self.jump_boost_streak_timer -= 1
        
        if self.player.shield_active and self.shield_frames:
            self.shield_frame_timer += 1
            self.shield_glow_pulse += 0.08
            
            if self.shield_frame_timer >= self.shield_frame_duration:
                self.shield_frame_timer = 0
                if self.shield_frame_index < len(self.shield_frames) - 1:
                    self.shield_frame_index += 1
        
        if self.shield_break_effect:
            self.shield_break_frame_timer += 1
            if self.shield_break_frame_timer >= self.shield_break_frame_duration:
                self.shield_break_frame_timer = 0
                if self.shield_break_timer > 0:
                    self.shield_break_timer -= 1
                else:
                    self.shield_break_effect = False
    
    def spawn_landing_snow(self):
        foot_x = self.player.hitbox.centerx
        foot_y = self.player.hitbox.bottom
        
        for _ in range(12):
            p = dustParticle(foot_x, foot_y)
            
            p.vel_x = random.uniform(-3.5, 3.5)
            p.vel_y = random.uniform(-2.5, -0.5)
            
            if hasattr(p, "color"):
                p.color = (255, 255, 255)
            
            self.player.particles.add(p)
    
    def draw_heal_effect(self, screen, camera):
        if self.heal_effect_timer <= 0:
            return
        
        pos = camera.apply(self.player)
        center_x = pos[0] + self.player.rect.width // 2
        center_y = pos[1] + self.player.rect.height // 2
        
        progress = self.heal_effect_timer / self.heal_effect_duration
        alpha = int(120 * progress)
        
        glow_radius = max(self.player.rect.width, self.player.rect.height) // 2 + 12
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            glow_surf,
            (*self.heal_effect_color, alpha),
            (glow_radius, glow_radius),
            glow_radius
        )
        screen.blit(glow_surf, (center_x - glow_radius, center_y - glow_radius))
        
        sweep_height = int(self.player.rect.height * 1.4)
        sweep_width = self.player.rect.width + 12
        sweep_surf = pygame.Surface((sweep_width, sweep_height), pygame.SRCALPHA)
        
        sweep_y = int((1 - progress) * sweep_height)
        pygame.draw.rect(
            sweep_surf,
            (*self.heal_effect_color, alpha),
            (0, sweep_y, sweep_width, max(8, sweep_height // 4))
        )
        
        screen.blit(sweep_surf, (center_x - sweep_width // 2, center_y - sweep_height // 2))
    
    def draw_jump_boost_streak(self, screen, camera):
        if self.jump_boost_streak_timer <= 0:
            return
        
        pos = camera.apply(self.player)
        center_x = pos[0] + self.player.rect.width // 2
        top_y = pos[1]
        
        progress = self.jump_boost_streak_timer / self.jump_boost_streak_duration
        alpha = int(255 * progress)
        
        streak_surf = pygame.Surface((self.player.rect.width + 30, self.player.rect.height + 60), pygame.SRCALPHA)
        mid_x = streak_surf.get_width() // 2
        bottom_y = streak_surf.get_height() - 8
        top_line_y = 5
        
        pygame.draw.line(
            streak_surf,
            (255, 255, 255, alpha),
            (mid_x, bottom_y),
            (mid_x, top_line_y),
            5
        )
        
        pygame.draw.line(
            streak_surf,
            (255, 255, 255, int(alpha * 0.9)),
            (mid_x - 14, bottom_y - 8),
            (mid_x - 8, top_line_y + 8),
            3
        )
        
        pygame.draw.line(
            streak_surf,
            (255, 255, 255, int(alpha * 0.9)),
            (mid_x + 14, bottom_y - 8),
            (mid_x + 8, top_line_y + 8),
            3
        )
        
        screen.blit(streak_surf, (center_x - streak_surf.get_width() // 2, top_y - 25))
    
    def draw_shield_effect(self, screen, camera):
        if not self.player.shield_active and not self.shield_break_effect:
            return
        
        if not self.shield_frames:
            return
        
        pos = camera.apply(self.player)
        center_x = pos[0] + self.player.rect.width // 2
        center_y = pos[1] + self.player.rect.height // 2
        
        if self.player.shield_active:
            frame = self.shield_frames[self.shield_frame_index]
        else:
            break_index = len(self.shield_frames) - self.shield_break_timer
            break_index = max(0, min(break_index, len(self.shield_frames) - 1))
            frame = self.shield_frames[break_index]
        
        shield_size = max(self.player.rect.width, self.player.rect.height) + 30
        frame_scaled = pygame.transform.smoothscale(frame, (shield_size, shield_size))
        
        if self.player.shield_active:
            glow_alpha = int(80 + 40 * math.sin(self.shield_glow_pulse))
            glow_radius = shield_size // 2 - 4
            glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                glow_surf,
                (120, 200, 255, glow_alpha),
                (glow_radius, glow_radius),
                glow_radius
            )
            screen.blit(glow_surf, (center_x - glow_radius, center_y - glow_radius))
        
        shield_rect = frame_scaled.get_rect(center=(center_x, center_y))
        screen.blit(frame_scaled, shield_rect)
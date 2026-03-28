import pygame
import math
import random
from boss import BOSS_SIZE
from settings import *
from sound_manager import sound_manager

class CinematicOutroManager:
    def __init__(self):
        self.active = False
        self.freeze_player = False
        self.callback = None
        self.boss_spawn_x = 0
        self.boss_spawn_y = 0
        self.level_index = 0
        self.timer = 0
        self.phase = 0
        
        self.camera_start = 0
        self.camera_target = 0
        self.camera_return_start = 0
        
        self.golem_frames = []
        self.golem_frame_index = 0
        self.golem_animation_speed = 0.15
        self.show_golem = False
        
        self.transition_alpha = 0
        
        self.phase_timers = {
            'approach': 120,
            'dialogue': 720,
            'fade_out': 60,
            'fade_in': 60,
            'return': 120,
        }
        
        self.dialogue_lines = [
            "Grr… this magic… it burns…",
            "So this is the warmth I tried to erase…",
            "You may have won this clash, Santa…",
            "But the next storm… will not be so forgiving."
        ]
        self.current_line = 0
        
        self.voice_played = False
        
        self.line_start_time = 0
        self.line_durations = {
            0: 180,
            1: 180,
            2: 180,
            3: 180,
        }
        
        self.waiting_for_fade = False
        
    def load_golem_animation(self):
        frames = []
        try:
            for i in range(8):
                try:
                    frame = pygame.image.load(f"sprites/boss/idle/{i}.png").convert_alpha()
                    frame = pygame.transform.scale(frame, (TILE_SIZE * 3, TILE_SIZE * 3))
                    frames.append(frame)
                except:
                    break
            
            if len(frames) == 0:
                try:
                    sheet = pygame.image.load("sprites/boss/idle.png").convert_alpha()
                    frame_width = sheet.get_width() // 8
                    frame_height = sheet.get_height()
                    
                    for i in range(8):
                        frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                        frame.blit(sheet, (0, 0), (i * frame_width, 0, frame_width, frame_height))
                        frame = pygame.transform.scale(frame, (TILE_SIZE * 3, TILE_SIZE * 3))
                        frames.append(frame)
                except:
                    pass
            
            if len(frames) == 0:
                surf = pygame.Surface((TILE_SIZE * 3, TILE_SIZE * 3))
                surf.fill((255, 215, 0))
                frames = [surf]
            
        except Exception as e:
            surf = pygame.Surface((TILE_SIZE * 3, TILE_SIZE * 3))
            surf.fill((255, 215, 0))
            frames = [surf]
        
        return frames
    
    def start_boss_outro(self, spawn_x, spawn_y, player_x, camera_scroll, level_index=0, callback=None):
        self.active = True
        self.freeze_player = True
        self.boss_spawn_x = spawn_x
        self.boss_spawn_y = spawn_y
        self.level_index = level_index
        self.player_start_x = player_x
        self.camera_start = camera_scroll
        self.callback = callback
        self.phase = 1
        self.timer = 0
        self.current_line = 0
        self.show_golem = False
        self.golem_frame_index = 0
        self.transition_alpha = 0
        self.voice_played = False
        self.line_start_time = 0
        self.waiting_for_fade = False
        
        self.line_durations = {
            0: 180,
            1: 180,
            2: 180,
            3: 180,
        }
        
        self.golem_frames = self.load_golem_animation()
        
        self.camera_target = spawn_x - SCREEN_WIDTH // 2
    
    def update(self, player, camera):
        if not self.active:
            return
            
        self.timer += 1
        
        if self.phase == 1:
            progress = self.timer / self.phase_timers['approach']
            if progress > 1.0:
                progress = 1.0
                self.phase = 2
                self.timer = 0
                self.show_golem = True
            
            ease_progress = self.ease_in_out_cubic(progress)
            camera.scroll = self.camera_start + (self.camera_target - self.camera_start) * ease_progress
            
        elif self.phase == 2:
            if len(self.golem_frames) > 0:
                self.golem_frame_index += self.golem_animation_speed
                if self.golem_frame_index >= len(self.golem_frames):
                    self.golem_frame_index = 0
            
            if self.line_start_time == 0:
                self.line_start_time = self.timer
            
            current_duration = self.line_durations.get(self.current_line, 180)
            
            time_on_current_line = self.timer - self.line_start_time
            
            if not self.voice_played:
                self.voice_played = True
                if sound_manager:
                    sound_manager.play_boss_outro(self.boss_spawn_x, self.boss_spawn_y)
            
            if not self.waiting_for_fade:
                if time_on_current_line >= current_duration:
                    if self.current_line < len(self.dialogue_lines) - 1:
                        self.current_line += 1
                        self.line_start_time = self.timer
                    else:
                        self.waiting_for_fade = True
            
            if self.waiting_for_fade and self.current_line >= len(self.dialogue_lines) - 1:
                if time_on_current_line >= current_duration:
                    self.phase = 3
                    self.timer = 0
                    self.show_golem = False
                    self.waiting_for_fade = False
            
        elif self.phase == 3:
            self.transition_alpha += 5
            if self.transition_alpha >= 255:
                self.transition_alpha = 255
                self.phase = 4
                self.timer = 0
                self.camera_return_start = camera.scroll
                if self.callback:
                    self.callback(self.boss_spawn_x, self.boss_spawn_y)
            
        elif self.phase == 4:
            self.transition_alpha -= 5
            if self.transition_alpha <= 0:
                self.transition_alpha = 0
                self.phase = 5
                self.timer = 0
            
        elif self.phase == 5:
            progress = self.timer / self.phase_timers['return']
            if progress > 1.0:
                progress = 1.0
                self.phase = 6
                self.timer = 0
            
            target_scroll = player.rect.centerx - SCREEN_WIDTH // 2
            ease_progress = self.ease_in_out_cubic(progress)
            camera.scroll = self.camera_return_start + (target_scroll - self.camera_return_start) * ease_progress
            
        elif self.phase == 6:
            self.active = False
            self.freeze_player = False
    
    def ease_in_out_cubic(self, x):
        if x < 0.5:
            return 4 * x * x * x
        else:
            return 1 - pow(-2 * x + 2, 3) / 2
    
    def draw_dialogue_box(self, screen, text, x, y):
        
        if self.level_index == 1:
            primary_color = (0, 200, 200)
            secondary_color = (0, 150, 150)
            glow_color = (0, 255, 255, 100)
            bg_color = (0, 30, 30)
            text_color = (220, 255, 255)
            border_width = 4
            speaker = "WEAKENED GOLEM"
        else:
            primary_color = (255, 215, 0)
            secondary_color = (200, 150, 0)
            glow_color = (255, 255, 100, 100)
            bg_color = (40, 30, 0)
            text_color = (255, 255, 200)
            border_width = 3
            speaker = "WEAKENED GOLEM"
        
        font = pygame.font.SysFont('Futura', 28, bold=True)
        speaker_font = pygame.font.SysFont('Futura', 20, bold=True)
        
        speaker_surf = speaker_font.render(speaker, True, primary_color)
        text_surf = font.render(text, True, text_color)
        
        padding = 20
        speaker_width = speaker_surf.get_width() + padding * 2
        text_width = text_surf.get_width() + padding * 2
        box_width = max(speaker_width, text_width) + 40
        box_height = 100
        
        box_x = x - box_width // 2
        box_y = y - box_height - 30
        
        box_surf = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        
        for i in range(box_height):
            alpha = 220 - i * 2
            color = (bg_color[0], bg_color[1], bg_color[2], alpha)
            pygame.draw.line(box_surf, color, (0, i), (box_width, i))
        
        screen.blit(box_surf, (box_x, box_y))
        
        for i in range(3):
            glow_alpha = 100 - i * 30
            pygame.draw.rect(
                screen,
                (*primary_color, glow_alpha),
                (box_x - i, box_y - i, box_width + i * 2, box_height + i * 2),
                2,
                border_radius=15
            )
        
        pygame.draw.rect(
            screen,
            primary_color,
            (box_x, box_y, box_width, box_height),
            border_width,
            border_radius=15
        )
        
        speaker_bg_rect = pygame.Rect(
            box_x + 15,
            box_y - 10,
            speaker_surf.get_width() + 15,
            speaker_surf.get_height() + 4
        )
        pygame.draw.rect(screen, bg_color, speaker_bg_rect, border_radius=8)
        pygame.draw.rect(screen, primary_color, speaker_bg_rect, 1, border_radius=8)
        screen.blit(speaker_surf, (box_x + 20, box_y - 8))
        
        screen.blit(text_surf, (box_x + (box_width - text_width) // 2 + padding, box_y + 45))
        
        pointer_points = [
            (x - 15, box_y + box_height),
            (x + 15, box_y + box_height),
            (x, box_y + box_height + 15)
        ]
        pygame.draw.polygon(screen, bg_color, pointer_points)
        pygame.draw.polygon(screen, primary_color, pointer_points, border_width)
    
    def draw(self, screen, camera):
        if not self.active:
            return
            
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        golem_x = self.boss_spawn_x - (TILE_SIZE * 1.5)
        golem_y = self.boss_spawn_y
        
        if self.phase == 1:
            alpha = int(80 * (self.timer / self.phase_timers['approach']))
            overlay.fill((0, 0, 0, alpha))
            
        elif self.phase == 2:
            overlay.fill((0, 0, 0, 150))
            
            if self.golem_frames and len(self.golem_frames) > 0 and self.show_golem:
                frame_index = int(self.golem_frame_index)
                if frame_index < len(self.golem_frames):
                    current_frame = self.golem_frames[frame_index]
                    
                    if self.level_index == 1:
                        glow_surf = pygame.Surface((BOSS_SIZE + 20, BOSS_SIZE + 20), pygame.SRCALPHA)
                        pygame.draw.rect(glow_surf, (0, 200, 200, 50), glow_surf.get_rect(), border_radius=20)
                        screen.blit(glow_surf, (golem_x - 10 - camera.scroll, golem_y - 10))
                    else:
                        glow_surf = pygame.Surface((BOSS_SIZE + 20, BOSS_SIZE + 20), pygame.SRCALPHA)
                        pygame.draw.rect(glow_surf, (255, 215, 0, 50), glow_surf.get_rect(), border_radius=20)
                        screen.blit(glow_surf, (golem_x - 10 - camera.scroll, golem_y - 10))
                    
                    screen.blit(current_frame, (golem_x - camera.scroll, golem_y))
        
        screen.blit(overlay, (0, 0))
        
        if self.transition_alpha > 0:
            transition_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            transition_overlay.fill((0, 0, 0, self.transition_alpha))
            screen.blit(transition_overlay, (0, 0))
        
        if self.phase == 2 and self.show_golem:
            if self.current_line < len(self.dialogue_lines):
                text_x = self.boss_spawn_x - camera.scroll
                text_y = self.boss_spawn_y - TILE_SIZE * 3
                
                self.draw_dialogue_box(
                    screen,
                    self.dialogue_lines[self.current_line],
                    text_x,
                    text_y
                )
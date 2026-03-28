import pygame
import math
import random
from boss import BOSS_SIZE
from settings import *
from sound_manager import sound_manager

class CylinderParticle:
    def __init__(self, center_x, center_y, height_level):
        self.center_x = center_x
        self.center_y = center_y
        
        self.x = center_x
        self.y = center_y
        
        self.height_level = height_level
        self.radius = random.uniform(70, 90)
        
        self.angle = random.uniform(0, math.pi * 2)
        self.speed = random.uniform(0.02, 0.04)
        
        self.y_offset = random.uniform(-5, 5)
        
        self.size = random.randint(3, 6)
        self.brightness = random.randint(200, 255)
        self.alpha = random.randint(180, 230)
        
        self.life = random.randint(100, 150)
        self.max_life = self.life
        
    def update(self, center_x, center_y, time, intensity):
        self.life -= 1
        
        self.angle += self.speed * intensity
        
        self.x = center_x + math.cos(self.angle) * self.radius
        self.y = center_y - 50 + (self.height_level * 350) + self.y_offset
        
        drift = math.sin(time * 0.02 + self.height_level * 5) * 5
        self.x += drift
        
        if self.life < 30:
            self.alpha = int(255 * (self.life / 30))
            
    def draw(self, screen, camera):
        if self.alpha <= 5:
            return
            
        screen_x = self.x - camera.scroll
        screen_y = self.y
        
        if -100 < screen_x < SCREEN_WIDTH + 100 and -100 < screen_y < SCREEN_HEIGHT + 100:
            pygame.draw.circle(
                screen,
                (self.brightness, self.brightness, self.brightness, self.alpha),
                (int(screen_x), int(screen_y)),
                self.size
            )
    
    def is_dead(self):
        return self.life <= 0

class SnowCylinder:
    def __init__(self, center_x, center_y):
        self.center_x = center_x
        self.center_y = center_y - 80
        
        self.height = 400
        self.layers = 20
        self.particles = []
        self.time = 0
        self.active = False
        self.intensity = 0
        self.completed = False
        self.drift_offset = 0
        
    def start(self):
        self.active = True
        self.time = 0
        self.intensity = 0
        self.drift_offset = 0
        
        for layer in range(self.layers):
            height_level = layer / self.layers
            for _ in range(45):
                self.particles.append(
                    CylinderParticle(self.center_x, self.center_y, height_level)
                )
        
    def update(self, target_x):
        if not self.active:
            return
            
        self.time += 1
        
        if self.time < 60:
            self.intensity = self.time / 60
        elif self.time < 180:
            self.intensity = 1.0
        elif self.time < 240:
            self.intensity = 1.0
            progress = (self.time - 180) / 60
            self.drift_offset = math.sin(progress * math.pi) * 30
        else:
            fade = (self.time - 240) / 60
            self.intensity = 1.0 - fade
            if self.time >= 300:
                self.active = False
                self.completed = True
        
        current_x = target_x + self.drift_offset
        
        for particle in self.particles[:]:
            particle.update(current_x, self.center_y, self.time, self.intensity)
            if particle.is_dead():
                self.particles.remove(particle)
        
        target_count = int(900 * self.intensity)
        while len(self.particles) < target_count:
            height_level = random.uniform(0, 1)
            self.particles.append(
                CylinderParticle(current_x, self.center_y, height_level)
            )
    
    def draw(self, screen, camera):
        if not self.active:
            return
            
        for layer in range(self.layers):
            h = layer / self.layers
            y = self.center_y + h * self.height
            
            ring_alpha = int(60 * self.intensity)
            if ring_alpha > 5:
                pygame.draw.ellipse(
                    screen,
                    (255, 255, 255, ring_alpha),
                    (self.center_x - 70 - camera.scroll, y - 5, 140, 10),
                    2
                )
        
        for particle in self.particles:
            particle.draw(screen, camera)

class CinematicManager:
    def __init__(self):
        self.active = False
        self.cylinder = None
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
            'approach': 180,
            'cylinder': 300,
            'dialogue': 720,
            'fade_out': 60,
            'fade_in': 60,
            'return': 120,
            'spawn': 30
        }
        
        self.level1_dialogue = [
            "So… the bearer of Christmas magic finally arrives.",
            "I am the Ice Golem, ruler of the frozen north.",
            "This land will freeze when your magic fades.",
            "Try to stop me, Santa."
        ]
        
        self.level2_dialogue = [
            "You should have stayed out of the storm, Santa.",
            "The frozen north has answered my call.",
            "Your Christmas magic weakens with every step.",
            "This time… there will be no escape."
        ]
        
        self.dialogue_lines = self.level1_dialogue
        self.current_line = 0
        
        self.voice_played = False
        
        self.line_start_time = 0
        self.line_durations = {
            0: 180,
            1: 180,
            2: 180,
            3: 180,
        }
        
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
                surf.fill((100, 100, 255))
                frames = [surf]
            
        except Exception as e:
            surf = pygame.Surface((TILE_SIZE * 3, TILE_SIZE * 3))
            surf.fill((100, 100, 255))
            frames = [surf]
        
        return frames
    
    def set_line_durations(self, durations):
        for line_num, duration in durations.items():
            if line_num in self.line_durations:
                self.line_durations[line_num] = duration
    
    def start_boss_intro(self, spawn_x, spawn_y, player_x, camera_scroll, level_index=0, callback=None):
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
        
        sound_manager.play_music("boss_fight.mpeg")

        self.line_durations = {
            0: 195,
            1: 215,
            2: 235,
            3: 75,
        }
        
        if level_index == 1:
            self.dialogue_lines = self.level2_dialogue
        else:
            self.dialogue_lines = self.level1_dialogue
        
        self.golem_frames = self.load_golem_animation()
        self.camera_target = spawn_x - SCREEN_WIDTH // 2
    
    def draw_dialogue_box(self, screen, text, x, y):
        
        if self.level_index == 1:
            primary_color = (0, 200, 200)
            secondary_color = (0, 150, 150)
            glow_color = (0, 255, 255, 100)
            bg_color = (0, 30, 30)
            text_color = (220, 255, 255)
            border_width = 4
        else:
            primary_color = (100, 200, 255)
            secondary_color = (50, 150, 255)
            glow_color = (0, 100, 255, 80)
            bg_color = (0, 20, 40)
            text_color = (255, 255, 255)
            border_width = 3
        
        name_font = pygame.font.SysFont('Futura', 24, bold=True)
        text_font = pygame.font.SysFont('Futura', 28, bold=True)
        
        speaker = "ICE GOLEM"
        speaker_surf = name_font.render(speaker, True, primary_color)
        
        text_surf = text_font.render(text, True, text_color)
        
        padding = 25
        speaker_width = speaker_surf.get_width() + padding * 2
        text_width = text_surf.get_width() + padding * 2
        box_width = max(speaker_width, text_width) + 40
        box_height = 120
        
        box_x = x - box_width // 2
        box_y = y - box_height - 40
        
        box_surf = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        
        for i in range(box_height):
            gradient_factor = 1.0 - (i / box_height) * 0.3
            color = (
                int(bg_color[0] * gradient_factor),
                int(bg_color[1] * gradient_factor),
                int(bg_color[2] * gradient_factor),
                230
            )
            pygame.draw.line(box_surf, color, (0, i), (box_width, i))
        
        for glow_size in range(3, 0, -1):
            glow_alpha = 80 - glow_size * 20
            pygame.draw.rect(
                box_surf,
                (*primary_color[:3], glow_alpha),
                (0, 0, box_width, box_height),
                border_width + glow_size,
                border_radius=20
            )
        
        pygame.draw.rect(
            box_surf,
            (*primary_color, 255),
            (0, 0, box_width, box_height),
            border_width,
            border_radius=20
        )
        
        corner_length = 20
        corner_positions = [
            (5, 5), (box_width - 5 - corner_length, 5),
            (5, box_height - 5 - corner_length), (box_width - 5 - corner_length, box_height - 5 - corner_length)
        ]
        
        for cx, cy in corner_positions:
            pygame.draw.line(box_surf, secondary_color, (cx, cy), (cx + corner_length, cy), 2)
            pygame.draw.line(box_surf, secondary_color, (cx, cy), (cx, cy + corner_length), 2)
        
        screen.blit(box_surf, (box_x, box_y))
        
        speaker_bg_rect = pygame.Rect(
            box_x + 20,
            box_y - 12,
            speaker_surf.get_width() + 20,
            speaker_surf.get_height() + 6
        )
        
        pygame.draw.rect(screen, bg_color, speaker_bg_rect, border_radius=10)
        pygame.draw.rect(screen, primary_color, speaker_bg_rect, 2, border_radius=10)
        
        screen.blit(speaker_surf, (box_x + 30, box_y - 8))
        
        screen.blit(text_surf, (box_x + (box_width - text_width) // 2 + padding, box_y + 45))
        
        pointer_points = [
            (x - 20, box_y + box_height),
            (x + 20, box_y + box_height),
            (x, box_y + box_height + 25)
        ]
        
        shadow_points = [(px + 2, py + 2) for px, py in pointer_points]
        pygame.draw.polygon(screen, (0, 0, 0, 100), shadow_points)
        
        pygame.draw.polygon(screen, bg_color, pointer_points)
        pygame.draw.polygon(screen, primary_color, pointer_points, border_width)
    
    def update(self, player, camera):
        if not self.active:
            return
            
        self.timer += 1
        
        if self.phase == 1:
            progress = self.timer / self.phase_timers['approach']
            if progress > 1.0:
                self.phase = 2
                self.timer = 0
                self.cylinder = SnowCylinder(self.boss_spawn_x, self.boss_spawn_y)
                self.cylinder.start()
            
            ease_progress = self.ease_in_out_cubic(progress)
            camera.scroll = self.camera_start + (self.camera_target - self.camera_start) * ease_progress
            
        elif self.phase == 2:
            if self.cylinder:
                self.cylinder.update(self.boss_spawn_x)
                if self.cylinder.completed:
                    self.phase = 3
                    self.timer = 0
                    self.show_golem = True
            
        elif self.phase == 3:
            if len(self.golem_frames) > 0:
                self.golem_frame_index += self.golem_animation_speed
                if self.golem_frame_index >= len(self.golem_frames):
                    self.golem_frame_index = 0
            
            if self.line_start_time == 0:
                self.line_start_time = self.timer
            
            current_duration = self.line_durations.get(self.current_line, 180)
            
            time_on_current_line = self.timer - self.line_start_time
            
            if time_on_current_line >= current_duration:
                if self.current_line < len(self.dialogue_lines) - 1:
                    self.current_line += 1
                    self.line_start_time = self.timer
                else:
                    if time_on_current_line >= current_duration:
                        self.phase = 4
                        self.timer = 0
                        self.show_golem = False
            
            if not self.voice_played:
                self.voice_played = True
                if sound_manager:
                    if self.level_index == 1:
                        sound_manager.play_boss_intro_level2(self.boss_spawn_x, self.boss_spawn_y)
                    else:
                        sound_manager.play_boss_intro_level1(self.boss_spawn_x, self.boss_spawn_y)
            
        elif self.phase == 4:
            self.transition_alpha += 5
            if self.transition_alpha >= 255:
                self.transition_alpha = 255
                self.phase = 5
                self.timer = 0
                self.camera_return_start = camera.scroll
                if self.callback:
                    self.callback(self.boss_spawn_x, self.boss_spawn_y)
            
        elif self.phase == 5:
            self.transition_alpha -= 5
            if self.transition_alpha <= 0:
                self.transition_alpha = 0
                self.phase = 6
                self.timer = 0
            
        elif self.phase == 6:
            progress = self.timer / self.phase_timers['return']
            if progress > 1.0:
                progress = 1.0
                self.phase = 7
                self.timer = 0
            
            target_scroll = player.rect.centerx - SCREEN_WIDTH // 2
            ease_progress = self.ease_in_out_cubic(progress)
            camera.scroll = self.camera_return_start + (target_scroll - self.camera_return_start) * ease_progress
            
        elif self.phase == 7:
            self.timer += 1
            if self.timer > self.phase_timers['spawn']:
                self.active = False
                self.freeze_player = False
    
    def ease_in_out_cubic(self, x):
        if x < 0.5:
            return 4 * x * x * x
        else:
            return 1 - pow(-2 * x + 2, 3) / 2
    
    def draw(self, screen, camera):
        if not self.active:
            return
            
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        golem_x = self.boss_spawn_x - (TILE_SIZE * 1.5)
        golem_y = self.boss_spawn_y - TILE_SIZE * 2.5
        
        if self.phase == 1:
            alpha = int(80 * (self.timer / self.phase_timers['approach']))
            overlay.fill((0, 0, 0, alpha))
            
        elif self.phase == 2:
            if self.cylinder:
                self.cylinder.draw(screen, camera)
                
                intensity = self.cylinder.intensity
                for radius in range(400, 0, -40):
                    vignette_alpha = int(120 * intensity * (1 - radius/400))
                    pygame.draw.circle(
                        overlay,
                        (0, 0, 0, vignette_alpha),
                        (SCREEN_WIDTH//2, SCREEN_HEIGHT//2),
                        radius
                    )
            
        elif self.phase == 3:
            overlay.fill((0, 0, 0, 150))
            
            if self.golem_frames and len(self.golem_frames) > 0 and self.show_golem:
                frame_index = int(self.golem_frame_index)
                if frame_index < len(self.golem_frames):
                    current_frame = self.golem_frames[frame_index]
                    
                    if self.level_index == 1:
                        glow_surf = pygame.Surface((BOSS_SIZE + 20, BOSS_SIZE + 20), pygame.SRCALPHA)
                        pygame.draw.rect(glow_surf, (0, 200, 200, 50), glow_surf.get_rect(), border_radius=20)
                        screen.blit(glow_surf, (golem_x - 10 - camera.scroll, golem_y - 10))
                    
                    screen.blit(current_frame, (golem_x - camera.scroll, golem_y))
        
        screen.blit(overlay, (0, 0))
        
        if self.transition_alpha > 0:
            transition_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            transition_overlay.fill((0, 0, 0, self.transition_alpha))
            screen.blit(transition_overlay, (0, 0))
        
        if self.phase == 1:
            font = pygame.font.SysFont('Futura', 36, bold=True)
            progress = self.timer / self.phase_timers['approach']
            if progress < 0.6:
                alpha = int(255 * min(1, progress * 2))
                text = font.render("A presence awakens...", True, (255, 255, 255))
                text.set_alpha(alpha)
                text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                
                for i in range(3):
                    glow = font.render("A presence awakens...", True, (100, 200, 255))
                    glow.set_alpha(alpha // 3)
                    glow_rect = glow.get_rect(center=(SCREEN_WIDTH//2 + i, SCREEN_HEIGHT//2 + i))
                    screen.blit(glow, glow_rect)
                
                screen.blit(text, text_rect)
                
        elif self.phase == 3 and self.show_golem:
            if self.current_line < len(self.dialogue_lines):
                text_x = self.boss_spawn_x - camera.scroll
                text_y = self.boss_spawn_y - TILE_SIZE * 3
                
                self.draw_dialogue_box(
                    screen,
                    self.dialogue_lines[self.current_line],
                    text_x,
                    text_y
                )
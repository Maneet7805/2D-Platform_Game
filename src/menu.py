# menu.py
import os
import sys
import math
import time
import random
import pygame
import cv2

from settings import *

try:
    from sound_manager import sound_manager
except Exception:
    sound_manager = None


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
SOFT_BLUE = (220, 235, 255)
PANEL_BG = (10, 20, 35, 150)


def safe_load_image(path, fallback_size=None, use_colorkey=True):
    try:
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            if use_colorkey:
                img.set_colorkey((0, 0, 0))
            return img
    except Exception as e:
        pass

    if fallback_size:
        surf = pygame.Surface(fallback_size, pygame.SRCALPHA)
        surf.fill((180, 40, 40, 180))
        pygame.draw.rect(surf, WHITE, surf.get_rect(), 3, border_radius=18)
        return surf
    return None


def safe_scale_bg(image):
    if image is None:
        return None

    img_w = image.get_width()
    img_h = image.get_height()
    if img_w <= 0 or img_h <= 0:
        return image

    scale = max(SCREEN_WIDTH / img_w, SCREEN_HEIGHT / img_h)
    new_w = int(img_w * scale)
    new_h = int(img_h * scale)
    return pygame.transform.smoothscale(image, (new_w, new_h))


def draw_text_with_shadow(screen, font, text, color, center, shadow_color=(0, 0, 0), shadow_offset=(3, 3)):
    shadow = font.render(text, True, shadow_color)
    main = font.render(text, True, color)

    shadow_rect = shadow.get_rect(center=(center[0] + shadow_offset[0], center[1] + shadow_offset[1]))
    main_rect = main.get_rect(center=center)

    screen.blit(shadow, shadow_rect)
    screen.blit(main, main_rect)


def draw_round_panel(screen, rect, alpha=145, border_alpha=110, radius=24):
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel, (PANEL_BG[0], PANEL_BG[1], PANEL_BG[2], alpha), panel.get_rect(), border_radius=radius)
    pygame.draw.rect(panel, (255, 255, 255, border_alpha), panel.get_rect(), 2, border_radius=radius)
    screen.blit(panel, rect.topleft)


class Snowflake:
    def __init__(self):
        self.reset(True)

    def reset(self, initial=False):
        self.x = random.uniform(0, SCREEN_WIDTH)
        self.y = random.uniform(0, SCREEN_HEIGHT) if initial else random.uniform(-60, -10)
        self.size = random.randint(2, 5)
        self.speed = random.uniform(0.8, 2.0)
        self.drift = random.uniform(-0.35, 0.35)
        self.alpha = random.randint(120, 220)

    def update(self):
        self.y += self.speed
        self.x += self.drift

        if self.y > SCREEN_HEIGHT + 10:
            self.reset()

        if self.x < -10:
            self.x = SCREEN_WIDTH + 10
        elif self.x > SCREEN_WIDTH + 10:
            self.x = -10

    def draw(self, screen):
        surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 255, 255, self.alpha), (self.size, self.size), self.size)
        screen.blit(surf, (int(self.x), int(self.y)))


class TwinkleLight:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.phase = random.uniform(0, math.pi * 2)

    def draw(self, screen, t):
        alpha = int(120 + 80 * math.sin(t * 2 + self.phase))
        glow = pygame.Surface((22, 22), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color, max(25, alpha // 3)), (11, 11), 10)
        pygame.draw.circle(glow, (*self.color, alpha), (11, 11), 4)
        screen.blit(glow, (self.x - 11, self.y - 11))


class ImageButton:
    def __init__(self, image, center, text, font, text_color=WHITE, hover_scale=1.012, text_y_offset=-2):
        self.base_image = image
        self.image = image
        self.center = center
        self.rect = self.image.get_rect(center=center)

        self.text = text
        self.font = font
        self.text_color = text_color

        self.hover_scale = hover_scale
        self.hovered = False
        self.pressed = False
        self.scale = 1.0
        self.offset_y = 0
        self.text_y_offset = text_y_offset

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

        target_scale = self.hover_scale if self.hovered else 1.0
        self.scale += (target_scale - self.scale) * 0.18

        target_offset = -2 if self.hovered else 0
        self.offset_y += (target_offset - self.offset_y) * 0.2

        new_w = max(1, int(self.base_image.get_width() * self.scale))
        new_h = max(1, int(self.base_image.get_height() * self.scale))
        self.image = pygame.transform.smoothscale(self.base_image, (new_w, new_h))
        self.rect = self.image.get_rect(center=(self.center[0], int(self.center[1] + self.offset_y)))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_pressed = self.pressed
            self.pressed = False
            if was_pressed and self.rect.collidepoint(event.pos):
                return True

        return False

    def draw(self, screen):
        screen.blit(self.image, self.rect)

        text_center = (self.rect.centerx, self.rect.centery + self.text_y_offset)
        draw_text_with_shadow(
            screen,
            self.font,
            self.text,
            self.text_color,
            text_center,
            shadow_color=(20, 20, 20),
            shadow_offset=(2, 2)
        )


class VolumeSlider:
    def __init__(self, x, y, width, height, label, initial_value=0.5, color=GOLD):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.value = initial_value
        self.dragging = False
        self.color = color
        self.font = pygame.font.SysFont("Futura", 18, bold=True)
        self.small_font = pygame.font.SysFont("Futura", 14)
        
        self.handle_radius = 12
        self.handle_x = self.rect.x + int(self.value * self.rect.width)
        self.handle_y = self.rect.centery
        
        self.glow_alpha = 0
        self.sparkles = []
        
    def add_sparkle(self):
        self.sparkles.append({
            'x': self.handle_x + random.randint(-15, 15),
            'y': self.handle_y + random.randint(-10, 10),
            'size': random.randint(2, 4),
            'alpha': 255,
            'life': 15
        })
        
    def update(self, mouse_pos, mouse_pressed):
        handle_rect = pygame.Rect(self.handle_x - self.handle_radius, 
                                  self.handle_y - self.handle_radius,
                                  self.handle_radius * 2, self.handle_radius * 2)
        
        if handle_rect.collidepoint(mouse_pos) and mouse_pressed[0]:
            self.dragging = True
            self.glow_alpha = min(150, self.glow_alpha + 10)
            if random.random() < 0.2:
                self.add_sparkle()
        else:
            self.glow_alpha = max(0, self.glow_alpha - 5)
        
        if not mouse_pressed[0]:
            self.dragging = False
            
        if self.dragging:
            new_x = max(self.rect.x, min(self.rect.x + self.rect.width, mouse_pos[0]))
            self.value = (new_x - self.rect.x) / self.rect.width
            self.handle_x = new_x
            
            if random.random() < 0.3:
                self.add_sparkle()
        
        for sparkle in self.sparkles[:]:
            sparkle['life'] -= 1
            sparkle['alpha'] = int(255 * (sparkle['life'] / 15))
            if sparkle['life'] <= 0:
                self.sparkles.remove(sparkle)
        
    def draw(self, screen):
        label_surf = self.font.render(self.label, True, WHITE)
        screen.blit(label_surf, (self.rect.x, self.rect.y - 25))
        
        percent_surf = self.small_font.render(f"{int(self.value * 100)}%", True, GOLD)
        screen.blit(percent_surf, (self.rect.x + self.rect.width + 15, self.rect.y - 5))
        
        track_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, self.rect.height)
        pygame.draw.rect(screen, (60, 60, 70), track_rect, border_radius=5)
        
        fill_width = int(self.rect.width * self.value)
        if fill_width > 0:
            fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
            pygame.draw.rect(screen, self.color, fill_rect, border_radius=5)
        
        if self.glow_alpha > 0:
            glow_rect = track_rect.inflate(8, 8)
            pygame.draw.rect(screen, (*self.color, self.glow_alpha), glow_rect, 3, border_radius=8)
        
        handle_pos = (self.handle_x, self.handle_y)
        
        pygame.draw.circle(screen, (30, 30, 30), (handle_pos[0] + 2, handle_pos[1] + 2), self.handle_radius)
        
        pygame.draw.circle(screen, WHITE, handle_pos, self.handle_radius)
        pygame.draw.circle(screen, self.color, handle_pos, self.handle_radius - 2)
        
        pygame.draw.circle(screen, (255, 255, 255, 200), 
                          (handle_pos[0] - 2, handle_pos[1] - 2), 3)
        
        for sparkle in self.sparkles:
            pygame.draw.circle(screen, (255, 255, 255, sparkle['alpha']),
                             (sparkle['x'], sparkle['y']), sparkle['size'])


class VideoPlayer:
    def __init__(self, screen, video_filename, audio_filename=None):
        self.screen = screen
        self.video_filename = video_filename
        self.audio_filename = audio_filename

        self.cap = None
        self.playing = False
        self.finished = False
        self.frame_surface = None
        self.audio_start_time = 0
        self.frame_count = 0

        self.video_width = 0
        self.video_height = 0
        self.display_width = 0
        self.display_height = 0
        self.display_x = 0
        self.display_y = 0

        self.fps = 30
        self.frame_time = 0

    def load_video(self):
        if not os.path.exists(self.video_filename):
            return False

        try:
            self.cap = cv2.VideoCapture(self.video_filename)
            if not self.cap.isOpened():
                return False

            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            if self.fps <= 0:
                self.fps = 30

            self.frame_time = 1.0 / self.fps
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.video_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.video_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            self.calculate_display_dimensions()
            return True
        except Exception as e:
            return False

    def load_audio(self):
        if not os.path.exists(self.audio_filename):
            return False
        try:
            pygame.mixer.music.load(self.audio_filename)
            return True
        except Exception as e:
            return False

    def calculate_display_dimensions(self):
        if self.video_width <= 0 or self.video_height <= 0:
            self.display_width = SCREEN_WIDTH
            self.display_height = SCREEN_HEIGHT
            self.display_x = 0
            self.display_y = 0
            return

        video_aspect = self.video_width / self.video_height
        screen_aspect = SCREEN_WIDTH / SCREEN_HEIGHT

        if video_aspect > screen_aspect:
            self.display_width = SCREEN_WIDTH
            self.display_height = int(SCREEN_WIDTH / video_aspect)
            self.display_x = 0
            self.display_y = (SCREEN_HEIGHT - self.display_height) // 2
        else:
            self.display_height = SCREEN_HEIGHT
            self.display_width = int(SCREEN_HEIGHT * video_aspect)
            self.display_x = (SCREEN_WIDTH - self.display_width) // 2
            self.display_y = 0

    def play(self):
        if self.load_video():
            self.playing = True
            self.finished = False
            self.frame_count = 0

            if self.load_audio():
                pygame.mixer.music.play()
                self.audio_start_time = time.time()
            return True
        return False

    def update(self):
        if not self.playing or self.finished or not self.cap:
            return

        current_time = time.time()

        if self.audio_start_time > 0:
            elapsed = current_time - self.audio_start_time
            target_frame = int(elapsed / self.frame_time)

            if target_frame > self.frame_count:
                frame = None
                frames_to_skip = target_frame - self.frame_count

                for _ in range(frames_to_skip):
                    ret, frame = self.cap.read()
                    if not ret:
                        self.finished = True
                        self.playing = False
                        pygame.mixer.music.stop()
                        return
                    self.frame_count += 1

                if frame is not None:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_resized = cv2.resize(frame_rgb, (self.display_width, self.display_height))
                    self.frame_surface = pygame.surfarray.make_surface(frame_resized.swapaxes(0, 1))

        if self.frame_count >= self.total_frames - 1:
            self.finished = True
            self.playing = False
            pygame.mixer.music.stop()

    def draw(self):
        self.screen.fill(BLACK)
        if self.frame_surface:
            self.screen.blit(self.frame_surface, (self.display_x, self.display_y))

        font = pygame.font.SysFont("Futura", 24, bold=True)
        text = font.render("Press X or click to skip", True, WHITE)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        self.screen.blit(text, rect)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_x:
            self.finished = True
            self.playing = False
            if self.cap:
                self.cap.release()
            pygame.mixer.music.stop()
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.finished = True
            self.playing = False
            if self.cap:
                self.cap.release()
            pygame.mixer.music.stop()
            return True

        return False

    def cleanup(self):
        if self.cap:
            self.cap.release()
            self.cap = None
        pygame.mixer.music.stop()


class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_menu = "main"

        self.background = None
        self.load_background()
        self.bg_offset_x = 0
        self.bg_speed = 0.30

        video_path = os.path.join("assets", "story", "storyline.mov")
        audio_path = os.path.join("sounds", "story", "storyline_audio.mpeg")
        self.video_player = VideoPlayer(screen, video_path, audio_path)

        self.title_font = pygame.font.SysFont("Futura", 52, bold=True)
        self.subtitle_font = pygame.font.SysFont("Futura", 18, bold=True)
        self.button_font = pygame.font.SysFont("Arial Black", 22)
        self.panel_title_font = pygame.font.SysFont("Futura", 28, bold=True)
        self.body_font = pygame.font.SysFont("Futura", 20)
        self.small_font = pygame.font.SysFont("Futura", 17)

        self.snowflakes = [Snowflake() for _ in range(65)]
        self.twinkle_lights = []
        self.create_twinkle_lights()

        self.music_on = True
        self.sfx_on = True
        
        self.music_volume = 0.5
        self.sfx_volume = 0.5

        self.load_ui_assets()
        self.create_buttons()

        self.santa_x = -260
        self.golem_x = SCREEN_WIDTH + 260
        self.santa_target = 40
        self.golem_target = SCREEN_WIDTH - 320
        
        self.music_slider = None
        self.sfx_slider = None

    def load_ui_assets(self):
        ui_dir = os.path.join("assets", "ui")

        self.play_img = pygame.transform.smoothscale(
            safe_load_image(os.path.join(ui_dir, "play_story.png"), (330, 82)),
            (330, 82)
        )
        self.level_img = pygame.transform.smoothscale(
            safe_load_image(os.path.join(ui_dir, "level_select.png"), (330, 82)),
            (330, 82)
        )
        self.how_img = pygame.transform.smoothscale(
            safe_load_image(os.path.join(ui_dir, "how_to_play.png"), (330, 82)),
            (330, 82)
        )
        self.settings_img = pygame.transform.smoothscale(
            safe_load_image(os.path.join(ui_dir, "settings.png"), (330, 82)),
            (330, 82)
        )
        self.quit_img = pygame.transform.smoothscale(
            safe_load_image(os.path.join(ui_dir, "quit.png"), (330, 82)),
            (330, 82)
        )
        self.back_img = pygame.transform.smoothscale(
            safe_load_image(os.path.join(ui_dir, "back.png"), (135, 52)),
            (135, 52)
        )
        self.panel_img = pygame.transform.smoothscale(
            safe_load_image(os.path.join(ui_dir, "panel_frame.png"), (500, 680)),
            (500, 680)
        )

        self.santa_img = pygame.transform.smoothscale(
            safe_load_image(os.path.join(ui_dir, "santa.png"), (290, 380), use_colorkey=False),
            (290, 380)
        )
        self.golem_img = pygame.transform.smoothscale(
            safe_load_image(os.path.join(ui_dir, "golem.png"), (320, 360), use_colorkey=False),
            (320, 360)
        )

    def create_buttons(self):
        center_x = SCREEN_WIDTH // 2
        start_y = 240
        gap = 76

        self.play_button = ImageButton(self.play_img, (center_x, start_y), "PLAY STORY", self.button_font)
        self.level_select_button = ImageButton(self.level_img, (center_x, start_y + gap), "LEVEL SELECT",
                                               self.button_font)
        self.how_to_play_button = ImageButton(self.how_img, (center_x, start_y + gap * 2), "HOW TO PLAY",
                                              self.button_font)
        self.settings_button = ImageButton(self.settings_img, (center_x, start_y + gap * 3), "SETTINGS",
                                           self.button_font)
        self.quit_button = ImageButton(self.quit_img, (center_x, start_y + gap * 4 - 12), "QUIT", self.button_font)

        self.level1_button = ImageButton(self.play_img, (SCREEN_WIDTH // 2, 245), "LEVEL 1", self.button_font)
        self.level2_button = ImageButton(self.level_img, (SCREEN_WIDTH // 2, 335), "LEVEL 2", self.button_font)

        self.back_button = ImageButton(
            self.back_img,
            (88, 48),
            "BACK",
            pygame.font.SysFont("Arial Black", 16),
            text_y_offset=-1
        )

        self.music_toggle_button = ImageButton(
            self.settings_img,
            (SCREEN_WIDTH // 2, 255),
            "MUSIC: ON",
            pygame.font.SysFont("Arial Black", 20)
        )
        self.sfx_toggle_button = ImageButton(
            self.how_img,
            (SCREEN_WIDTH // 2, 345),
            "SFX: ON",
            pygame.font.SysFont("Arial Black", 20)
        )

    def load_background(self):
        editor_bg_path = os.path.join('assets', 'editor', 'menu_background.png')
        if os.path.exists(editor_bg_path):
            try:
                self.background = safe_scale_bg(pygame.image.load(editor_bg_path).convert_alpha())
                return
            except Exception as e:
                pass
        
        for filename in ["background_default.png", "background.png", "menu_bg.png"]:
            try:
                path = os.path.join('assets', 'editor', filename)
                if os.path.exists(path):
                    self.background = safe_scale_bg(pygame.image.load(path).convert_alpha())
                    return
            except Exception:
                pass
        self.background = None

    def create_twinkle_lights(self):
        colors = [
            (255, 90, 90),
            (90, 255, 140),
            (255, 220, 100),
            (110, 190, 255),
        ]
        for i in range(20):
            x = 70 + i * 48
            y = 38 + random.randint(-4, 4)
            self.twinkle_lights.append(TwinkleLight(x, y, random.choice(colors)))

    def apply_audio_settings(self):
        if sound_manager:
            try:
                if self.music_on:
                    sound_manager.set_music_track_volume("background", self.music_volume)
                    sound_manager.set_music_track_volume("level1", self.music_volume)
                    sound_manager.set_music_track_volume("level2", self.music_volume)
                else:
                    sound_manager.set_music_track_volume("background", 0.0)
                    sound_manager.set_music_track_volume("level1", 0.0)
                    sound_manager.set_music_track_volume("level2", 0.0)
                
                sound_manager.set_sfx_volume(self.sfx_volume if self.sfx_on else 0.0)
                
            except Exception as e:
                pass

    def draw_bg(self):

        if self.background:

            self.bg_offset_x += self.bg_speed

            if self.bg_offset_x > self.background.get_width():
                self.bg_offset_x = 0

            x = int(self.bg_offset_x)

            self.screen.blit(self.background, (-x, 0))
            self.screen.blit(self.background, (self.background.get_width() - x, 0))

        else:
            self.screen.fill((15, 32, 70))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 16, 35, 60))
        self.screen.blit(overlay, (0, 0))

    def draw_top_decor(self):
        t = pygame.time.get_ticks() / 1000.0
        for light in self.twinkle_lights:
            light.draw(self.screen, t)

    def draw_effects(self):
        for snowflake in self.snowflakes:
            snowflake.draw(self.screen)

    def update_effects(self):
        for snowflake in self.snowflakes:
            snowflake.update()

    def draw_title(self):
        draw_text_with_shadow(
            self.screen,
            self.title_font,
            "THE LAST CHRISTMAS RUN",
            WHITE,
            (SCREEN_WIDTH // 2, 48),
            shadow_color=(0, 100, 0),
            shadow_offset=(4, 4)
        )

        draw_text_with_shadow(
            self.screen,
            self.subtitle_font,
            "A snowy adventure with gifts, danger, and Christmas magic",
            SOFT_BLUE,
            (SCREEN_WIDTH // 2, 84),
            shadow_color=(0, 0, 0),
            shadow_offset=(2, 2)
        )

    def draw_main_frame(self):
        rect = self.panel_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 72))
        self.screen.blit(self.panel_img, rect)
        return rect

    def update_buttons(self, buttons):
        mouse_pos = pygame.mouse.get_pos()
        for btn in buttons:
            btn.update(mouse_pos)

    def draw_side_characters(self):
        if not self.santa_img or not self.golem_img:
            return

        if self.current_menu == "main":
            santa_target = -5
            golem_target = SCREEN_WIDTH - 230
        else:
            santa_target = -300
            golem_target = SCREEN_WIDTH + 100

        self.santa_x += (santa_target - self.santa_x) * 0.08
        self.golem_x += (golem_target - self.golem_x) * 0.08

        t = pygame.time.get_ticks() * 0.002
        santa_y = SCREEN_HEIGHT - self.santa_img.get_height() - 38 + math.sin(t) * 6
        golem_y = SCREEN_HEIGHT - self.golem_img.get_height() - 34 + math.sin(t + 1.3) * 6

        for x, y in [
            (self.santa_x + 140, santa_y + 150),
            (self.golem_x + 160, golem_y + 150),
        ]:
            glow = pygame.Surface((220, 220), pygame.SRCALPHA)
            pygame.draw.circle(glow, (120, 200, 255, 28), (110, 110), 110)
            self.screen.blit(glow, (x - 110, y - 110))

        self.screen.blit(self.santa_img, (self.santa_x, santa_y))
        self.screen.blit(self.golem_img, (self.golem_x, golem_y))

    def draw_main_menu(self):
        self.draw_bg()
        self.draw_top_decor()
        self.draw_title()
        self.draw_effects()
        self.draw_main_frame()

        buttons = [
            self.play_button,
            self.level_select_button,
            self.how_to_play_button,
            self.settings_button,
            self.quit_button
        ]

        self.update_buttons(buttons)

        for btn in buttons:
            btn.draw(self.screen)

        self.draw_side_characters()

    def draw_level_select(self):
        self.draw_bg()
        self.draw_top_decor()
        self.draw_effects()
        self.draw_side_characters()
        self.update_buttons([self.level1_button, self.level2_button, self.back_button])

        panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 230, 130, 460, 300)
        draw_round_panel(self.screen, panel_rect, alpha=135, border_alpha=100)

        self.back_button.draw(self.screen)
        draw_text_with_shadow(self.screen, self.panel_title_font, "SELECT LEVEL", GOLD, (SCREEN_WIDTH // 2, 160))
        self.level1_button.draw(self.screen)
        self.level2_button.draw(self.screen)

    def draw_how_to_play(self):
        self.draw_bg()
        self.draw_top_decor()
        self.draw_effects()
        self.draw_side_characters()
        self.update_buttons([self.back_button])

        panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 280, 100, 560, 440)
        draw_round_panel(self.screen, panel_rect, alpha=180, border_alpha=150, radius=30)

        self.back_button.draw(self.screen)
        draw_text_with_shadow(self.screen, self.panel_title_font, "HOW TO PLAY", GOLD, (SCREEN_WIDTH // 2, 130))

        start_y = 170
        left_col_x = SCREEN_WIDTH // 2 - 220
        right_col_x = SCREEN_WIDTH // 2 + 20
        line_height = 40

        controls_left = [
            ("MOVE", "A / D or <- / ->"),
            ("JUMP", "SPACE / W / ^"),
            ("RUN", "SHIFT"),
        ]

        controls_right = [
            ("SHOOT", "F"),
            ("SPECIAL", "Q"),
            ("RESTART", "R"),
        ]

        for i, (label, key) in enumerate(controls_left):
            y_pos = start_y + i * line_height
            label_surf = self.body_font.render(f"{label}:", True, GOLD)
            key_surf = self.body_font.render(key, True, WHITE)
            self.screen.blit(label_surf, (left_col_x, y_pos))
            self.screen.blit(key_surf, (left_col_x + 80, y_pos))

        for i, (label, key) in enumerate(controls_right):
            y_pos = start_y + i * line_height
            label_surf = self.body_font.render(f"{label}:", True, GOLD)
            key_surf = self.body_font.render(key, True, WHITE)
            self.screen.blit(label_surf, (right_col_x, y_pos))
            self.screen.blit(key_surf, (right_col_x + 90, y_pos))

        powerup_y = start_y + 3 * line_height + 20
        powerup_title = self.body_font.render("POWERUPS", True, GOLD)
        self.screen.blit(powerup_title, (left_col_x, powerup_y))

        powerups = [
            ("HEALTH", "Restores 100 HP"),
            ("JUMP BOOST", "Higher jump for 8s"),
            ("SHIELD", "Invincibility for 10s"),
        ]

        for i, (name, desc) in enumerate(powerups):
            y_pos = powerup_y + 30 + i * 30
            name_surf = self.small_font.render(name, True, (255, 255, 200))
            desc_surf = self.small_font.render(desc, True, (200, 200, 200))
            self.screen.blit(name_surf, (left_col_x + 10, y_pos))
            self.screen.blit(desc_surf, (left_col_x + 150, y_pos))

        objective_y = powerup_y
        objective_title = self.body_font.render("OBJECTIVE", True, GOLD)
        self.screen.blit(objective_title, (right_col_x, objective_y))

        objectives = [
            "Collect all gifts",
            "Reach the golden gate",
            "Defeat enemies",
            "Avoid hazards",
        ]

        for i, obj in enumerate(objectives):
            y_pos = objective_y + 30 + i * 30
            obj_surf = self.small_font.render(obj, True, WHITE)
            self.screen.blit(obj_surf, (right_col_x + 10, y_pos))

    def draw_settings(self):
        self.draw_bg()
        self.draw_top_decor()
        self.draw_effects()
        self.draw_side_characters()

        self.music_toggle_button.text = f"MUSIC: {'ON' if self.music_on else 'OFF'}"
        self.sfx_toggle_button.text = f"SFX: {'ON' if self.sfx_on else 'OFF'}"

        if not self.music_slider:
            self.music_slider = VolumeSlider(
                SCREEN_WIDTH // 2 - 150, 200, 200, 8, 
                "MUSIC VOLUME", self.music_volume, GOLD
            )
            self.sfx_slider = VolumeSlider(
                SCREEN_WIDTH // 2 - 150, 350, 200, 8,
                "SFX VOLUME", self.sfx_volume, (100, 200, 255)
            )

        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        self.music_slider.update(mouse_pos, mouse_pressed)
        self.sfx_slider.update(mouse_pos, mouse_pressed)
        
        self.music_volume = self.music_slider.value
        self.sfx_volume = self.sfx_slider.value
        
        self.apply_audio_settings()

        self.music_toggle_button.center = (SCREEN_WIDTH // 2, 275)
        self.sfx_toggle_button.center = (SCREEN_WIDTH // 2, 425)
        
        self.update_buttons([self.music_toggle_button, self.sfx_toggle_button, self.back_button])

        panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 250, 120, 500, 420)
        draw_round_panel(self.screen, panel_rect, alpha=145, border_alpha=110)

        self.back_button.draw(self.screen)
        draw_text_with_shadow(self.screen, self.panel_title_font, "SETTINGS", GOLD, (SCREEN_WIDTH // 2, 150))

        self.music_slider.draw(self.screen)
        self.sfx_slider.draw(self.screen)
        
        self.music_toggle_button.draw(self.screen)
        self.sfx_toggle_button.draw(self.screen)
    
    def run(self):
        while self.running:
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if self.current_menu == "video":
                    if self.video_player.handle_event(event):
                        self.video_player.cleanup()
                        return "level0_data.csv"

                elif self.current_menu == "main":
                    if self.play_button.handle_event(event):
                        if self.video_player.play():
                            self.current_menu = "video"
                        else:
                            return "level0_data.csv"
                    elif self.level_select_button.handle_event(event):
                        self.current_menu = "level_select"
                    elif self.how_to_play_button.handle_event(event):
                        self.current_menu = "how_to_play"
                    elif self.settings_button.handle_event(event):
                        self.current_menu = "settings"
                    elif self.quit_button.handle_event(event):
                        pygame.quit()
                        sys.exit()

                elif self.current_menu == "level_select":
                    if self.back_button.handle_event(event):
                        self.current_menu = "main"
                    elif self.level1_button.handle_event(event):
                        return "level0_data.csv"
                    elif self.level2_button.handle_event(event):
                        return "level1_data.csv"

                elif self.current_menu == "how_to_play":
                    if self.back_button.handle_event(event):
                        self.current_menu = "main"

                elif self.current_menu == "settings":
                    if self.back_button.handle_event(event):
                        self.current_menu = "main"
                    elif self.music_toggle_button.handle_event(event):
                        self.music_on = not self.music_on
                        self.apply_audio_settings()
                    elif self.sfx_toggle_button.handle_event(event):
                        self.sfx_on = not self.sfx_on
                        self.apply_audio_settings()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.current_menu in ["level_select", "how_to_play", "settings"]:
                        self.current_menu = "main"
                    elif self.current_menu == "video":
                        self.video_player.cleanup()
                        return "level0_data.csv"

            self.update_effects()
            self.screen.fill(BLACK)

            if self.current_menu == "video":
                self.video_player.update()
                self.video_player.draw()
                if self.video_player.finished:
                    self.video_player.cleanup()
                    return "level0_data.csv"

            elif self.current_menu == "main":
                self.draw_main_menu()

            elif self.current_menu == "level_select":
                self.draw_level_select()

            elif self.current_menu == "how_to_play":
                self.draw_how_to_play()

            elif self.current_menu == "settings":
                self.draw_settings()

            pygame.display.flip()

        self.video_player.cleanup()
        return None

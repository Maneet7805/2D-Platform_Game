import pygame
import random
import math
from settings import TILE_SIZE
from sound_manager import sound_manager

class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y, image, value=1):
        super().__init__()

        self.image = image.copy()
        self.original_image = self.image.copy()

        self.rect = self.image.get_rect()

        self.rect.bottom = y + TILE_SIZE - 5
        self.rect.centerx = x + TILE_SIZE // 2

        self.value = value
        self.collected = False

        self.original_y = self.rect.y
        self.float_offset = 0
        self.float_speed = 0.03
        self.float_amplitude = 2

        self.show_splash = False
        self.splash_lines = []
        self.effect_timer = 0
        self.effect_duration = 25

        self.splash_colors = [
            (255, 50, 50),
            (255, 150, 50),
            (255, 255, 50),
            (50, 255, 50),
            (50, 150, 255),
            (150, 50, 255),
            (255, 50, 150),
        ]

        self.id = id(self)

    def create_splash(self):
        lines = []
        center_x = self.rect.centerx
        center_y = self.rect.centery

        for _ in range(random.randint(15, 20)):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 4)
            
            line = {
                'x': center_x,
                'y': center_y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'length': random.randint(3, 6),
                'width': random.randint(1, 2),
                'color': random.choice(self.splash_colors),
                'life': random.randint(15, 25),
                'max_life': 25,
                'gravity': random.uniform(0.02, 0.08),
                'drag': 0.94,
            }
            lines.append(line)

        return lines

    def update(self, player):

        if not self.collected and self.rect.colliderect(player.rect):

            sound_manager.play_sound(sound_manager.item_sounds, "gift")

            self.collected = True
            self.show_splash = True
            self.splash_lines = self.create_splash()
            self.effect_timer = self.effect_duration

            player.collect_item(self.value)

            self.image.set_alpha(0)

            return True

        if self.show_splash:

            self.effect_timer -= 1

            for line in self.splash_lines[:]:
                line['x'] += line['vx']
                line['y'] += line['vy']
                
                line['vy'] += line['gravity']
                
                line['vx'] *= line['drag']
                line['vy'] *= line['drag']
                
                line['life'] -= 1
                
                if line['life'] <= 0:
                    self.splash_lines.remove(line)

            if self.effect_timer <= 0 or len(self.splash_lines) == 0:
                self.kill()
                return True

        if not self.collected:
            self.float_offset += self.float_speed
            wave = math.sin(self.float_offset * math.pi * 2)
            self.rect.y = self.original_y + (wave * self.float_amplitude)

        return False

    def draw_effect(self, screen, camera):

        if self.show_splash and len(self.splash_lines) > 0:

            for line in self.splash_lines:

                screen_x = line['x'] - camera.scroll
                screen_y = line['y']

                if screen_x < -20 or screen_x > 820 or screen_y < -20 or screen_y > 620:
                    continue

                life_ratio = line['life'] / line['max_life']
                alpha = int(200 * life_ratio)

                r, g, b = line['color']

                end_x = screen_x - line['vx'] * line['length']
                end_y = screen_y - line['vy'] * line['length']

                pygame.draw.line(
                    screen,
                    (r, g, b, alpha),
                    (int(screen_x), int(screen_y)),
                    (int(end_x), int(end_y)),
                    line['width']
                )

                if line['life'] > 15:
                    pygame.draw.circle(
                        screen,
                        (255, 255, 255, alpha),
                        (int(screen_x), int(screen_y)),
                        1
                    )
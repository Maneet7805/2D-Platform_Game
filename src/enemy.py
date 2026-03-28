import pygame
from settings import *

WOLF_SIZE = int(TILE_SIZE * 0.75)

def load_sprite_sheet(path, frame_width, frame_height):
    sheet = pygame.image.load(path).convert_alpha()
    sheet_width, sheet_height = sheet.get_size()

    frames = []
    for y in range(0, sheet_height, frame_height):
        row = []
        for x in range(0, sheet_width, frame_width):
            frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            frame.blit(sheet, (0, 0), (x, y, frame_width, frame_height))

            frame_rect = frame.get_bounding_rect()

            if frame_rect.width > 0 and frame_rect.height > 0:
                cropped = frame.subsurface(frame_rect).copy()
                cropped = pygame.transform.smoothscale(cropped, (WOLF_SIZE, WOLF_SIZE))
                row.append(cropped)

        if row:
            frames.append(row)

    return frames


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type="melee"):
        super().__init__()

        self.enemy_type = enemy_type
        self.direction = 1

        try:
            self.sprite_sheet = load_sprite_sheet(
                "sprites/enemies/wolf enemy.png", 64, 64
            )

            self.animations = {
                "idle": self.sprite_sheet[0][:6],
                "walk": self.sprite_sheet[1][:5],
                "hurt": self.sprite_sheet[2][:4],
                "death": self.sprite_sheet[3][:7]
            }

        except Exception as e:

            self.animations = {
                "idle": [pygame.Surface((WOLF_SIZE, WOLF_SIZE))],
                "walk": [pygame.Surface((WOLF_SIZE, WOLF_SIZE))],
                "hurt": [pygame.Surface((WOLF_SIZE, WOLF_SIZE))],
                "death": [pygame.Surface((WOLF_SIZE, WOLF_SIZE))]
            }

            for anim in self.animations.values():
                anim[0].fill((200, 0, 0))

        self.state = "idle"
        self.frame_index = 0

        self.animation_speeds = {
            "idle": 0.08,
            "walk": 0.12,
            "hurt": 0.1,
            "death": 0.1
        }

        self.animation_speed = self.animation_speeds[self.state]

        self.image = self.animations[self.state][0]
        self.rect = self.image.get_rect()

        self.rect.centerx = x + TILE_SIZE // 2
        self.rect.bottom = y + TILE_SIZE - 5

        self.hitbox = pygame.Rect(0, 0, WOLF_SIZE - 8, WOLF_SIZE - 8)
        self.hitbox.midbottom = self.rect.midbottom

        self.pos_x = float(self.rect.x)

        self.start_x = self.rect.x
        self.start_y = self.rect.y

        self.grounded = False
        self.vel_y = 0
        self.speed = 1

        self.health = 30
        self.max_health = 30
        self.damage = 20

        self.patrol_distance = TILE_SIZE * 3

        self.damage_cooldown = 0
        self.damage_cooldown_max = 30

        self.dead = False
        self.death_timer = 0
        self.death_duration = 45

        self.hit_flash = 0
        self.hit_flash_duration = 10

    def animate(self):
        frames = self.animations.get(self.state, self.animations["idle"])

        if not frames:
            return

        self.frame_index += self.animation_speed

        if self.frame_index >= len(frames):
            if self.state == "death":
                self.frame_index = len(frames) - 1
                if self.death_timer == 0:
                    self.death_timer = self.death_duration
            else:
                self.frame_index = 0

        frame_index = int(self.frame_index)

        if frame_index >= len(frames):
            frame_index = len(frames) - 1

        frame = frames[frame_index].copy()

        if self.direction > 0:
            frame = pygame.transform.flip(frame, True, False)

        if self.hit_flash > 0:
            red_overlay = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
            red_overlay.fill((255, 100, 100, 100))
            frame.blit(red_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            self.hit_flash -= 1

        old_midbottom = self.rect.midbottom

        self.image = frame
        self.rect = self.image.get_rect()

        self.rect.midbottom = old_midbottom
        self.hitbox.midbottom = self.rect.midbottom

    def apply_gravity(self):
        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

    def check_ground(self, tiles):
        ground_check_rect = pygame.Rect(
            self.rect.x + 5, self.rect.bottom, self.rect.width - 10, 5
        )

        for tile in tiles:
            if ground_check_rect.colliderect(tile.rect):
                return True

        return False

    def check_ground_ahead(self, tiles):
        if self.direction > 0:
            check_x = self.rect.right
        else:
            check_x = self.rect.left - TILE_SIZE

        ground_ahead_rect = pygame.Rect(
            check_x, self.rect.bottom, TILE_SIZE, 5
        )

        for tile in tiles:
            if ground_ahead_rect.colliderect(tile.rect):
                return True

        return False

    def patrol(self, tiles):
        if not self.check_ground_ahead(tiles):
            self.direction *= -1
            return

        self.pos_x += self.speed * self.direction
        self.rect.x = int(self.pos_x)

        for tile in tiles:
            if self.hitbox.colliderect(tile.rect):

                if self.direction > 0:
                    self.rect.right = tile.rect.left
                else:
                    self.rect.left = tile.rect.right

                self.pos_x = self.rect.x
                self.direction *= -1
                break

        if self.rect.x > self.start_x + self.patrol_distance:
            self.rect.x = self.start_x + self.patrol_distance
            self.pos_x = self.rect.x
            self.direction = -1

        elif self.rect.x < self.start_x - self.patrol_distance:
            self.rect.x = self.start_x - self.patrol_distance
            self.pos_x = self.rect.x
            self.direction = 1

        self.hitbox.midbottom = self.rect.midbottom

    def update_vertical(self, tiles):
        self.apply_gravity()

        self.rect.y += int(self.vel_y)

        self.hitbox.midbottom = self.rect.midbottom

        for tile in tiles:
            if self.hitbox.colliderect(tile.rect):

                if self.vel_y > 0:
                    self.rect.bottom = tile.rect.top
                    self.vel_y = 0

                elif self.vel_y < 0:
                    self.rect.top = tile.rect.bottom
                    self.vel_y = 0

                self.hitbox.midbottom = self.rect.midbottom

        self.grounded = self.check_ground(tiles)

    def take_damage(self, amount):
        if self.dead:
            return False

        self.health -= amount
        self.hit_flash = self.hit_flash_duration

        if self.health > 0:
            self.state = "hurt"
            self.frame_index = 0
            self.animation_speed = self.animation_speeds["hurt"]

        else:
            self.state = "death"
            self.frame_index = 0
            self.animation_speed = self.animation_speeds["death"]
            self.dead = True

        return self.health <= 0

    def can_deal_damage(self):
        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1
            return False

        return not self.dead and self.state not in ["death", "hurt"]

    def reset_damage_cooldown(self):
        self.damage_cooldown = self.damage_cooldown_max

    def update(self, player, tiles):

        if self.death_timer > 0:
            self.death_timer -= 1

            if self.death_timer <= 0:
                self.kill()
                return

        self.update_vertical(tiles)

        if self.grounded and not self.dead and self.state != "hurt":
            self.patrol(tiles)

        if not self.dead:

            if self.health <= 0:
                self.state = "death"
                self.frame_index = 0
                self.animation_speed = self.animation_speeds["death"]
                self.dead = True

            elif self.state == "hurt" and self.frame_index >= len(self.animations["hurt"]) - 0.5:
                self.state = "walk" if self.grounded else "idle"
                self.frame_index = 0
                self.animation_speed = self.animation_speeds[self.state]

            elif self.state not in ["hurt", "death"]:

                is_moving = abs(self.pos_x - self.start_x) > 2

                new_state = "walk" if self.grounded and is_moving else "idle"

                if new_state != self.state:
                    self.state = new_state
                    self.frame_index = 0
                    self.animation_speed = self.animation_speeds[self.state]

        self.animate()

        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1

    def draw_health_bar(self, screen, camera):
        if self.dead or self.health >= self.max_health:
            return

        pos = camera.apply(self)

        bar_width = 45
        bar_height = 6
        border_size = 2
        
        bar_x = pos[0] + self.rect.width // 2 - bar_width // 2
        bar_y = pos[1] - 15

        outer_rect = pygame.Rect(bar_x - border_size, bar_y - border_size, 
                                 bar_width + border_size * 2, bar_height + border_size * 2)
        pygame.draw.rect(screen, (30, 30, 30), outer_rect, border_radius=4)
        
        inner_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, (60, 20, 20), inner_rect, border_radius=3)

        health_percent = self.health / self.max_health
        fill_width = int(bar_width * health_percent)

        if fill_width > 0:
            if health_percent > 0.6:
                start_color = (100, 255, 100)
                end_color = (50, 200, 50)
            elif health_percent > 0.3:
                start_color = (255, 255, 100)
                end_color = (255, 200, 50)
            else:
                pulse = abs(pygame.time.get_ticks() % 500 - 250) / 250
                start_color = (255, 50, 50)
                end_color = (int(200 + 55 * pulse), 30, 30)
            
            for i in range(fill_width):
                blend = i / fill_width
                r = int(start_color[0] * (1 - blend) + end_color[0] * blend)
                g = int(start_color[1] * (1 - blend) + end_color[1] * blend)
                b = int(start_color[2] * (1 - blend) + end_color[2] * blend)
                
                pygame.draw.line(screen, (r, g, b), 
                               (bar_x + i, bar_y), 
                               (bar_x + i, bar_y + bar_height - 1))

        highlight_rect = pygame.Rect(bar_x, bar_y, fill_width, 2)
        pygame.draw.rect(screen, (255, 255, 255, 100), highlight_rect, border_radius=1)
        
        pygame.draw.rect(screen, (180, 180, 180), inner_rect, 1, border_radius=3)
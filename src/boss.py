import pygame
import random
import math
from settings import *
from boss_slam import BossSlam

BOSS_TILE_ID = 48
BOSS_SIZE = TILE_SIZE * 3

class Stone(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y):
        super().__init__()
        
        self.size = TILE_SIZE // 2
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        pygame.draw.circle(self.image, (120, 120, 120), (self.size//2, self.size//2), self.size//2)
        pygame.draw.circle(self.image, (100, 100, 100), (self.size//2 - 2, self.size//2 - 2), self.size//3)
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            self.vx = (dx / distance) * 3
            self.vy = (dy / distance) * 3
        else:
            self.vx = 0
            self.vy = 0
        
        self.damage = 15
        self.lifetime = 180
        self.age = 0
        self.max_range = TILE_SIZE * 8
        self.start_x = x
        self.start_y = y
        
    def update(self):
        self.age += 1
        self.rect.x += self.vx
        self.rect.y += self.vy
        
        if abs(self.rect.x - self.start_x) > self.max_range or abs(self.rect.y - self.start_y) > self.max_range:
            return True
            
        if self.age >= self.lifetime:
            return True
            
        return False
    
    def draw(self, screen, camera):
        pos = camera.apply(self)
        screen.blit(self.image, pos)

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, level_index=0):
        super().__init__()
        
        self.level_index = level_index
        
        self.start_x = x - TILE_SIZE
        self.start_y = y
        
        self.direction = 1
        self.health = 500 if level_index == 1 else 300
        self.max_health = self.health
        self.damage = 30
        self.dead = False
        self.death_timer = 0
        self.death_duration = 90
        
        self.weakened = False
        self.visible = True
        
        self.stone_ring = None
        if level_index == 1:
            from stone_ring import StoneRing
            self.stone_ring = StoneRing(self)
        
        self.animations = self.load_animations()
        
        self.state = "idle"
        self.frame_index = 0
        self.animation_speeds = {
            "idle": 0.08,
            "walk": 0.1,
            "attack": 0.15,
            "hurt": 0.08,
            "death": 0.08
        }
        self.animation_speed = self.animation_speeds[self.state]
        self.image = self.animations[self.state][0]
        self.rect = self.image.get_rect()
        
        self.rect.bottom = y + TILE_SIZE
        self.rect.centerx = x + TILE_SIZE // 2
        
        self.vel_y = 0
        self.grounded = True
        
        self.hitbox = pygame.Rect(0, 0, BOSS_SIZE - 20, BOSS_SIZE - 20)
        self.hitbox.midbottom = self.rect.midbottom
        
        self.pos_x = float(self.rect.x)
        self.speed = 0.5
        
        self.attacking = False
        self.attack_timer = 0
        self.attack_cooldown = 90
        self.attack_duration = 60
        self.slam_frame = 5
        
        self.slam_attack = BossSlam(self)
        
        self.cracks = []
        self.crack_duration = 180
        self.crack_damage_timer = 0
        self.crack_damage_interval = 30
        self.cracks_appeared = False
        
        self.screen_shake = 0
        self.screen_shake_duration = 10
        self.screen_shake_intensity = 3
        
        self.hit_flash = 0
        self.hit_flash_duration = 10
        
        self.damage_cooldown = 0
        self.damage_cooldown_max = 40
        
        self.weakened_threshold = 0.2
        
        self.hurt_animation_playing = False
        self.hurt_animation_timer = 0
        self.hurt_animation_duration = 20
        
        self.moving = False
        self.level = None
        
    def load_animations(self):
        animations = {
            "idle": [],
            "walk": [],
            "attack": [],
            "hurt": [],
            "death": []
        }
        
        try:
            try:
                idle_sheet = pygame.image.load("sprites/boss/idle.png").convert_alpha()
                frame_width = idle_sheet.get_width() // 8
                frame_height = idle_sheet.get_height()
                
                for i in range(8):
                    frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                    frame.blit(idle_sheet, (0, 0), (i * frame_width, 0, frame_width, frame_height))
                    frame = pygame.transform.scale(frame, (BOSS_SIZE, BOSS_SIZE))
                    animations["idle"].append(frame)
            except:
                try:
                    for i in range(8):
                        idle_img = pygame.image.load(f"sprites/boss/idle/{i}.png").convert_alpha()
                        idle_img = pygame.transform.scale(idle_img, (BOSS_SIZE, BOSS_SIZE))
                        animations["idle"].append(idle_img)
                except:
                    idle_img = pygame.image.load("sprites/boss/idle/0.png").convert_alpha()
                    idle_img = pygame.transform.scale(idle_img, (BOSS_SIZE, BOSS_SIZE))
                    animations["idle"] = [idle_img]
            
            walk_sheet = pygame.image.load("sprites/boss/walk.png").convert_alpha()
            frame_width = walk_sheet.get_width() // 10
            frame_height = walk_sheet.get_height()
            
            for i in range(10):
                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame.blit(walk_sheet, (0, 0), (i * frame_width, 0, frame_width, frame_height))
                frame = pygame.transform.scale(frame, (BOSS_SIZE, BOSS_SIZE))
                animations["walk"].append(frame)
            
            attack_sheet = pygame.image.load("sprites/boss/attack.png").convert_alpha()
            frame_width = attack_sheet.get_width() // 11
            frame_height = attack_sheet.get_height()
            
            for i in range(11):
                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame.blit(attack_sheet, (0, 0), (i * frame_width, 0, frame_width, frame_height))
                frame = pygame.transform.scale(frame, (BOSS_SIZE, BOSS_SIZE))
                animations["attack"].append(frame)
            
            hurt_sheet = pygame.image.load("sprites/boss/hurt.png").convert_alpha()
            frame_width = hurt_sheet.get_width() // 4
            frame_height = hurt_sheet.get_height()
            
            for i in range(4):
                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame.blit(hurt_sheet, (0, 0), (i * frame_width, 0, frame_width, frame_height))
                frame = pygame.transform.scale(frame, (BOSS_SIZE, BOSS_SIZE))
                animations["hurt"].append(frame)
            
            death_sheet = pygame.image.load("sprites/boss/death.png").convert_alpha()
            frame_width = death_sheet.get_width() // 12
            frame_height = death_sheet.get_height()
            
            for i in range(12):
                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame.blit(death_sheet, (0, 0), (i * frame_width, 0, frame_width, frame_height))
                frame = pygame.transform.scale(frame, (BOSS_SIZE, BOSS_SIZE))
                animations["death"].append(frame)
            
        except Exception as e:
            for anim_name in animations:
                surf = pygame.Surface((BOSS_SIZE, BOSS_SIZE))
                surf.fill((150, 0, 150))
                animations[anim_name] = [surf]
        
        return animations
    
    def start_weakened(self):
        self.weakened = True
        self.state = "idle"
    
    def chase_player(self, player, tiles):
        if not self.grounded or self.attacking or self.dead or self.weakened:
            return
        
        dx = player.rect.centerx - self.rect.centerx
        
        old_x = self.rect.x
        
        if dx > 15:
            self.direction = 1
            self.pos_x += self.speed
            self.moving = True
        elif dx < -15:
            self.direction = -1
            self.pos_x -= self.speed
            self.moving = True
        else:
            self.moving = False
        
        self.rect.x = int(self.pos_x)
        self.hitbox.midbottom = self.rect.midbottom
        
        for tile in tiles:
            if self.hitbox.colliderect(tile.rect):
                if self.direction > 0:
                    self.rect.right = tile.rect.left
                else:
                    self.rect.left = tile.rect.right
                self.pos_x = self.rect.x
                self.hitbox.midbottom = self.rect.midbottom
                break
        
        if abs(self.rect.x - old_x) < 0.5:
            self.moving = False
    
    def update(self, player, tiles):
        if not self.visible:
            return
            
        if self.screen_shake > 0:
            self.screen_shake -= 1
            self.shake_offset_x = random.randint(-self.screen_shake_intensity, self.screen_shake_intensity)
            self.shake_offset_y = random.randint(-self.screen_shake_intensity, self.screen_shake_intensity)
        else:
            self.shake_offset_x = 0
            self.shake_offset_y = 0
        
        if self.death_timer > 0:
            self.death_timer -= 1
            if self.death_timer <= 0:
                self.kill()
                return
        
        self.update_vertical(tiles)
        
        if self.level_index == 0 and not self.weakened and not self.dead:
            health_percent = self.health / self.max_health
            if health_percent <= self.weakened_threshold:
                self.start_weakened()
                return
        
        if self.stone_ring and not self.weakened and not self.dead:
            self.stone_ring.update(player, tiles)
        
        if hasattr(self, 'slam_attack'):
            self.slam_attack.update(player, tiles)
            
            if self.slam_attack.screen_shake > 0:
                shake_x, shake_y = self.slam_attack.get_shake_offset()
                self.shake_offset_x = shake_x
                self.shake_offset_y = shake_y
        
        if self.weakened:
            self.animate()
            return
        
        if self.hurt_animation_playing:
            self.hurt_animation_timer -= 1
            if self.hurt_animation_timer <= 0:
                self.hurt_animation_playing = False
        
        if not self.dead and not self.weakened:
            self.attack_timer += 1
            
            if not self.attacking and self.attack_timer >= self.attack_cooldown:
                self.attacking = True
                self.state = "attack"
                self.frame_index = 0
                self.attack_timer = 0
                self.cracks_appeared = False

        if self.attacking:
            if int(self.frame_index) == self.slam_frame and not self.cracks_appeared:
                if hasattr(self, 'slam_attack'):
                    if not self.slam_attack.active:
                        self.slam_attack.trigger_slam(tiles, self.level)
                        self.cracks_appeared = True
        
        if not self.dead:
            self.crack_damage_timer += 1
            if self.crack_damage_timer >= self.crack_damage_interval:
                self.crack_damage_timer = 0
                
                for crack in self.cracks[:]:
                    crack_rect = pygame.Rect(crack['x'], crack['y'], TILE_SIZE, TILE_SIZE)
                    if crack_rect.colliderect(player.rect):
                        player.take_damage(5)
        
        for crack in self.cracks[:]:
            crack['timer'] -= 1
            if crack['timer'] <= 0:
                self.cracks.remove(crack)
        
        if not self.attacking and not self.dead and not self.weakened:
            self.chase_player(player, tiles)
        
        self.animate()
    
    def take_damage(self, amount):
        if self.dead or self.weakened:
            return False
        
        self.health -= amount
        self.hit_flash = self.hit_flash_duration
        
        self.hurt_animation_playing = True
        self.hurt_animation_timer = self.hurt_animation_duration
        
        if self.health <= 0:
            if self.level_index == 1:
                self.state = "death"
                self.frame_index = 0
                self.dead = True
            else:
                self.start_weakened()
        
        return self.health <= 0
    
    def animate(self):
        if self.dead:
            current_state = "death"
        elif self.weakened:
            current_state = "idle"
        elif self.attacking:
            current_state = "attack"
        elif self.hurt_animation_playing:
            current_state = "hurt"
        else:
            if self.moving:
                current_state = "walk"
            else:
                current_state = "idle"
        
        frames = self.animations.get(current_state, self.animations["idle"])
        if not frames:
            return
        
        self.frame_index += self.animation_speeds.get(current_state, 0.1)
        
        if self.frame_index >= len(frames):
            if current_state == "attack":
                self.frame_index = 0
                self.attacking = False
                self.state = "idle"
            elif current_state == "hurt":
                self.frame_index = 0
                self.hurt_animation_playing = False
            elif current_state == "death":
                self.frame_index = len(frames) - 1
                if self.death_timer == 0:
                    self.death_timer = self.death_duration
            else:
                self.frame_index = 0
        
        frame_index = min(int(self.frame_index), len(frames) - 1)
        frame = frames[frame_index].copy()
        
        if self.direction < 0:
            frame = pygame.transform.flip(frame, True, False)
        
        if self.hit_flash > 0:
            tint = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
            
            flash_progress = self.hit_flash / self.hit_flash_duration
            
            if flash_progress > 0.7:
                tint_intensity = 180
            elif flash_progress > 0.4:
                tint_intensity = 120
            elif flash_progress > 0.1:
                tint_intensity = 60
            else:
                tint_intensity = 20
            
            tint.fill((100, 150, 255, tint_intensity))
            
            mask = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
            mask.blit(frame, (0, 0))
            tint.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            frame.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            
            self.hit_flash -= 1
        
        old_center = self.rect.center
        self.image = frame
        self.rect = self.image.get_rect()
        self.rect.center = old_center
        self.hitbox.midbottom = self.rect.midbottom
    
    def apply_gravity(self):
        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED
    
    def check_ground(self, tiles):
        ground_check = pygame.Rect(self.rect.x + 10, self.rect.bottom, self.rect.width - 20, 5)
        for tile in tiles:
            if ground_check.colliderect(tile.rect):
                return True
        return False
    
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
    
    def can_deal_damage(self):
        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1
            return False
        return not self.dead and not self.weakened and self.state not in ["death", "hurt"]
    
    def reset_damage_cooldown(self):
        self.damage_cooldown = self.damage_cooldown_max
    
    def draw_health_bar(self, screen, camera):
        if self.dead or self.weakened or not self.visible:
            return
        
        pos = camera.apply(self)
        shake_x = getattr(self, 'shake_offset_x', 0)
        shake_y = getattr(self, 'shake_offset_y', 0)
        
        bar_width = 300
        bar_height = 12
        bar_x = pos[0] + BOSS_SIZE//2 - bar_width//2 + shake_x
        bar_y = pos[1] - 40 + shake_y
        
        pygame.draw.rect(screen, (40, 40, 50), (bar_x, bar_y, bar_width, bar_height), border_radius=4)
        
        health_percent = self.health / self.max_health
        fill_width = int(bar_width * health_percent)
        
        if fill_width > 0:
            if health_percent > 0.6:
                color = (100, 200, 255)
            elif health_percent > 0.3:
                color = (70, 150, 255)
            else:
                color = (200, 100, 100)
            
            pygame.draw.rect(screen, color, (bar_x, bar_y, fill_width, bar_height), border_radius=4)
        
        pygame.draw.rect(screen, (200, 220, 255), (bar_x, bar_y, bar_width, bar_height), 1, border_radius=4)
        
        font = pygame.font.SysFont('Futura', 18, bold=True)
        name_text = "ICE GOLEM"
        
        level_text = f"LVL {self.level_index + 1}"
        
        name_shadow = font.render(name_text, True, (0, 0, 0))
        name_shadow_rect = name_shadow.get_rect(center=(bar_x + bar_width//2 + 1, bar_y - 12 + 1))
        screen.blit(name_shadow, name_shadow_rect)
        
        name_surf = font.render(name_text, True, (180, 220, 255))
        name_rect = name_surf.get_rect(center=(bar_x + bar_width//2, bar_y - 12))
        screen.blit(name_surf, name_rect)
        
        level_surf = font.render(level_text, True, (150, 150, 180))
        level_rect = level_surf.get_rect(bottomright=(bar_x + bar_width - 5, bar_y - 5))
        screen.blit(level_surf, level_rect)
        
        health_font = pygame.font.SysFont('Futura', 14)
        health_text = f"{self.health}/{self.max_health}"
        health_surf = health_font.render(health_text, True, (255, 255, 255))
        health_rect = health_surf.get_rect(center=(bar_x + bar_width//2, bar_y + bar_height//2))
        screen.blit(health_surf, health_rect)

    def draw_effects(self, screen, camera):
        if self.weakened or not self.visible:
            return
            
        shake_x = getattr(self, 'shake_offset_x', 0)
        shake_y = getattr(self, 'shake_offset_y', 0)
        
        if hasattr(self, 'slam_attack'):
            self.slam_attack.draw(screen, camera, shake_x, shake_y)
        
        if self.stone_ring:
            self.stone_ring.draw(screen, camera, shake_x, shake_y)
        
        for crack in self.cracks:
            screen_x = crack['x'] - camera.scroll + shake_x
            screen_y = crack['y'] + shake_y
            alpha = int(255 * (crack['timer'] / self.crack_duration))
            intensity = crack.get('intensity', 1.0)
            
            crack_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            line_width = max(2, int(4 * intensity))
            
            pygame.draw.line(crack_surf, (150, 100, 50, alpha), 
                           (5, 5), (TILE_SIZE-5, TILE_SIZE-5), line_width)
            pygame.draw.line(crack_surf, (150, 100, 50, alpha), 
                           (TILE_SIZE-5, 5), (5, TILE_SIZE-5), line_width)
            
            for _ in range(int(8 * intensity)):
                start_x = random.randint(5, TILE_SIZE-5)
                start_y = random.randint(5, TILE_SIZE-5)
                end_x = start_x + random.randint(-20, 20)
                end_y = start_y + random.randint(-20, 20)
                if 0 < end_x < TILE_SIZE and 0 < end_y < TILE_SIZE:
                    pygame.draw.line(crack_surf, (150, 100, 50, alpha//2),
                                   (start_x, start_y), (end_x, end_y), max(1, line_width-1))
            
            screen.blit(crack_surf, (int(screen_x), int(screen_y)))
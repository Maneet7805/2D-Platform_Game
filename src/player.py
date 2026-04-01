import math
import pygame
import os
from settings import *
import random
from particles import dustParticle
from sound_manager import sound_manager
from player_effects import PlayerEffects, AnimationLoader
from projectiles import Snowball, IceShard

PLAYER_SPEED = 3
ICE_SPEED = 1

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, current_level_index=0):
        super().__init__()

        self.current_level_index = current_level_index
        self.particles = pygame.sprite.Group()
        self.effects = PlayerEffects()

        self.heal_effect_timer = 0
        self.heal_effect_duration = 30
        self.heal_effect_color = (100, 255, 100)

        self.jump_boost_streak_timer = 0
        self.jump_boost_streak_duration = 16

        self.shield_frames = self.load_shield_frames(os.path.join("assets", "powerup", "shield.png"), frame_count=7)
        self.shield_frame_index = 0
        self.shield_frame_timer = 0
        self.shield_frame_duration = 85
        self.shield_glow_pulse = 0
        self.shield_break_effect = False
        self.shield_break_timer = 0

        self.shield_break_frame_duration = 4
        self.shield_break_frame_timer = 0
        
        self.animations = {
            "idle": AnimationLoader.load_animation(os.path.join("sprites", "player", "idle")),
            "walk": AnimationLoader.load_animation(os.path.join("sprites", "player", "walk")),
            "run": AnimationLoader.load_animation(os.path.join("sprites", "player", "run")),
            "jump": AnimationLoader.load_animation(os.path.join("sprites", "player", "jump")),
            "shoot": AnimationLoader.load_animation(os.path.join("sprites", "player", "shoot", "shoot.png")),
            "death": AnimationLoader.load_animation(os.path.join("sprites", "player", "death"))
        }

        self.walk_speed = PLAYER_SPEED
        self.sprint_speed = PLAYER_SPEED + 3
        self.ice_speed = ICE_SPEED

        self.state = "idle"
        self.frame_index = 0
        self.animation_speed = 0.15

        self.image = self.animations["idle"][0]
        self.rect = self.image.get_rect()
        
        self.hitbox_width = int(TILE_SIZE * 0.8)
        self.hitbox_height = int(TILE_SIZE * 0.9)
        self.hitbox = pygame.Rect(0, 0, self.hitbox_width, self.hitbox_height)
        self.hitbox.center = (x + TILE_SIZE//2, y + TILE_SIZE//2)
        
        self.start_x = x
        self.start_y = y
        
        self.vel_x = 0
        self.vel_y = 0
        self.grounded = False
        self.facing_right = True
        self.is_running = False
        
        self.jump_pressed = False
        self.jump_cooldown = 0
        
        self.on_ice = False
        self.ice_friction = 0.85
        self.ice_jump_strength = JUMP_STRENGTH * 4 // 5
        
        self.jump_boost_multiplier = 1.0
        
        self.shooting = False
        self.shoot_cooldown = 0
        self.shoot_cooldown_max = 20
        self.snowballs = pygame.sprite.Group()
        self.shoot_damage = 10
        
        self.special_ability_available = (current_level_index == 0)
        self.special_ability_cooldown = 0
        self.special_ability_cooldown_max = 300
        self.special_ability_key = pygame.K_q
        self.ice_shard_damage = 14
        
        self.special_ability_image = self.load_special_ability_image()
        
        self.presents_collected = 0
        self.total_presents_collected = 0
        self.gifts_deposited = 0
        self.collectibles_collected = 0
        self.total_collectibles = 0
        self.checkpoints_activated = []
        
        self.current_checkpoint = None
        self.respawn_count = 0
        self.max_respawns = 3
        
        self.health = 100
        self.max_health = 100
        self.alive = True
        
        self.invincible = False
        self.invincible_timer = 0
        self.invincible_duration = 60

        self.death_timer = 0
        self.death_duration = 90
        
        self.death_wait_timer = 0
        self.death_wait_duration = 60
        
        self.death_animation_speed = 0.08
        
        self.respawn_y_offset = -5
        
        self.footstep_timer = 0
        self.footstep_delay = 400
        self.last_footstep_time = 0
        self.sound_channel = None
        
        self.ready_to_respawn = False
        self.death_by_void = False
        
        self.powerups = {
            "jump_boost": 0,
            "shield": 0,
        }
        
        self.shield_active = False
        self.jump_boost_active = False
        self.powerup_timer = 0
        self.active_powerup = None

    def load_special_ability_image(self):
        asset_paths = [
            os.path.join("assets", "weapons", "ice_shard.png"),
            os.path.join("sprites", "ice_shard.png")
        ]
        
        for path in asset_paths:
            if os.path.exists(path):
                try:
                    image = pygame.image.load(path).convert_alpha()
                    return pygame.transform.scale(image, (30, 30))
                except:
                    continue
        
        surf = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.polygon(surf, (100, 200, 255), [(15, 0), (30, 15), (15, 30), (0, 15)])
        return surf

    def shoot_special_ability(self):
        if not self.special_ability_available or self.special_ability_cooldown > 0:
            return False
            
        if self.alive:
            direction = 1 if self.facing_right else -1
            offset = 20 if self.facing_right else -20
            spawn_x = self.rect.centerx + offset
            spawn_y = self.rect.centery
            
            spread_values = (-0.28, 0.0, 0.28)
            y_offsets = (-2, 0, 2)

            for vertical_speed, y_offset in zip(spread_values, y_offsets):
                shard = IceShard(
                    spawn_x,
                    spawn_y + y_offset,
                    direction,
                    vertical_speed=vertical_speed,
                    damage=self.ice_shard_damage
                )
                self.snowballs.add(shard)

            sound_manager.play_sound(
                sound_manager.powerup_sounds, 
                "ice_shard", 
                spawn_x, 
                spawn_y
            )
            
            self.special_ability_cooldown = self.special_ability_cooldown_max
            self.shooting = True
            self.state = "shoot"
            self.frame_index = 0
            return True
        return False

    def shoot(self):
        if self.shoot_cooldown <= 0 and self.alive:
            sound_manager.play_sound(sound_manager.player_sounds, "snowball")
            
            offset = 20 if self.facing_right else -20
            snowball = Snowball(
                self.rect.centerx + offset,
                self.rect.centery,
                1 if self.facing_right else -1,
                self.shoot_damage
            )
            self.snowballs.add(snowball)
            self.shoot_cooldown = self.shoot_cooldown_max
            self.shooting = True
            self.state = "shoot"
            self.frame_index = 0
            return True
        return False

    def check_snowball_collisions(self, enemies):
        for snowball in self.snowballs.copy():
            for enemy in enemies:
                if snowball.rect.colliderect(enemy.rect):
                    damage = getattr(snowball, "damage", self.shoot_damage)
                    enemy.take_damage(damage)
                    
                    if hasattr(snowball, "create_burst"):
                        snowball.create_burst()
                    
                    snowball.kill()
                    break

    def collect_item(self, value):
        self.presents_collected += value
        self.total_presents_collected += value
        self.collectibles_collected += value
        self.total_collectibles += value
    
    def deposit_gifts(self):
        self.gifts_deposited += self.presents_collected
        self.presents_collected = 0
    
    def set_checkpoint(self, x, y, checkpoint_id):
        self.current_checkpoint = (x, y, checkpoint_id)
        if checkpoint_id not in self.checkpoints_activated:
            self.checkpoints_activated.append(checkpoint_id)
    
    def reset_to_checkpoint(self):
        if self.respawn_count >= self.max_respawns:
            self.alive = False
            return False
        
        self.respawn_count += 1
        
        saved_jump = self.powerups["jump_boost"]
        saved_shield = self.powerups["shield"]
        
        if self.current_checkpoint:
            checkpoint_x, checkpoint_y, _ = self.current_checkpoint
            self.hitbox.center = (checkpoint_x + TILE_SIZE//2, checkpoint_y + TILE_SIZE//2 + self.respawn_y_offset)
        else:
            self.hitbox.center = (self.start_x + TILE_SIZE//2, self.start_y + TILE_SIZE//2 + self.respawn_y_offset)
        
        self.vel_x = 0
        self.vel_y = 0
        self.health = self.max_health
        self.alive = True
        self.grounded = False
        
        self.invincible = True
        self.invincible_timer = 120
        
        self.powerups["jump_boost"] = saved_jump
        self.powerups["shield"] = saved_shield
        
        self.shield_active = False
        self.jump_boost_active = False
        self.powerup_timer = 0
        self.active_powerup = None
        self.jump_boost_multiplier = 1.0
        
        self.death_wait_timer = 0
        self.ready_to_respawn = False
        self.death_by_void = False
        
        return True
    
    def check_ice_contact(self, tiles):
        if not self.grounded:
            self.on_ice = False
            return
        
        feet_rect = pygame.Rect(
            self.hitbox.x + 5,
            self.hitbox.bottom - 2,
            self.hitbox.width - 10,
            5
        )
        
        ice_detected = False
        for tile in tiles:
            if tile.rect.colliderect(feet_rect):
                if hasattr(tile, 'is_ice') and tile.is_ice:
                    ice_detected = True
                    break
        
        self.on_ice = ice_detected
    
    def collect_powerup(self, powerup_type, duration, value=0):
        if powerup_type == "health":
            self.health = min(self.max_health, self.health + value)
            self.effect_colour((100,255,100))
            
        elif powerup_type == "jump_boost":
            self.powerups["jump_boost"] += 1
            self.effect_colour((255, 240, 120))
            
        elif powerup_type == "shield":
            self.powerups["shield"] += 1
            self.effect_colour((120, 180, 255))

    def activate_jump_boost(self):
        if self.powerups["jump_boost"] > 0 and not self.jump_boost_active:
            self.powerups["jump_boost"] -= 1
            self.jump_boost_active = True
            self.active_powerup = "jump_boost"
            self.powerup_timer = 480
            self.jump_boost_multiplier = 1.4  
            return True
        return False

    def activate_shield(self):
        if self.powerups["shield"] > 0 and not self.shield_active:
            self.powerups["shield"] -= 1
            self.shield_active = True
            self.active_powerup = "shield"
            self.powerup_timer = 600
            self.invincible = True
            self.shield_frame_index = 0
            self.shield_frame_timer = 0
            self.shield_break_effect = False
            self.shield_break_timer = 0
            self.shield_glow_pulse = 0
            return True
        return False

    def draw_powerup_icons(self, screen):
        x = 15
        y = SCREEN_HEIGHT - 80
        
        if self.powerups["jump_boost"] > 0 or self.powerups["shield"] > 0:
            font = pygame.font.SysFont('Futura', 16)
            text_x = x
            
            if self.powerups["jump_boost"] > 0:
                color = (100, 255, 100) if self.active_powerup == "jump_boost" else (150, 150, 150)
                text = f"⬆️ 1: {self.powerups['jump_boost']}"
                if self.active_powerup == "jump_boost":
                    seconds = self.powerup_timer // 60
                    text += f" ({seconds}s)"
                text_surf = font.render(text, True, color)
                screen.blit(text_surf, (text_x, y))
                text_x += 80
            
            if self.powerups["shield"] > 0:
                color = (100, 100, 255) if self.active_powerup == "shield" else (150, 150, 150)
                text = f"🛡️ 2: {self.powerups['shield']}"
                if self.active_powerup == "shield":
                    seconds = self.powerup_timer // 60
                    text += f" ({seconds}s)"
                text_surf = font.render(text, True, color)
                screen.blit(text_surf, (text_x, y))

    def draw_special_ability_hud(self, screen):
        if not self.special_ability_available:
            return
            
        x = SCREEN_WIDTH - 70
        y = 15
        radius = 20
        
        pygame.draw.circle(screen, (30, 30, 40), (x + radius, y + radius), radius)
        pygame.draw.circle(screen, (100, 150, 200), (x + radius, y + radius), radius, 2)
        
        if self.special_ability_image:
            img_rect = self.special_ability_image.get_rect(center=(x + radius, y + radius))
            screen.blit(self.special_ability_image, img_rect)
        
        if self.special_ability_cooldown > 0:
            progress = 1 - (self.special_ability_cooldown / self.special_ability_cooldown_max)
            angle = progress * 360
            
            center_x = x + radius
            center_y = y + radius
            end_x = center_x + radius * math.cos(math.radians(angle))
            end_y = center_y + radius * math.sin(math.radians(angle))
            
            for i in range(3):
                thickness = 3 - i
                alpha = 200 - i * 50
                pygame.draw.line(screen, (255, 255, 255, alpha), 
                               (center_x, center_y), (end_x, end_y), thickness)
            
            if self.special_ability_cooldown > 0:
                seconds = (self.special_ability_cooldown // 60) + 1
                font = pygame.font.SysFont('Futura', 12)
                text = font.render(f"{seconds}s", True, (255, 255, 255))
                text_rect = text.get_rect(center=(x + radius, y + radius + 25))
                screen.blit(text, text_rect)
        else:
            font = pygame.font.SysFont('Futura', 10)
            text = font.render("READY", True, (100, 255, 100))
            text_rect = text.get_rect(center=(x + radius, y + radius + 25))
            screen.blit(text, text_rect)
        
        key_font = pygame.font.SysFont('Futura', 14, bold=True)
        key_text = key_font.render("Q", True, (255, 215, 0))
        key_rect = key_text.get_rect(center=(x + radius, y + radius - 25))
        screen.blit(key_text, key_rect)

    def handle_input(self, keys):
        
        if keys[pygame.K_1]:
            self.activate_jump_boost()
        
        if keys[pygame.K_2]:
            self.activate_shield()
        
        if keys[self.special_ability_key]:
            self.shoot_special_ability()
        
        if keys[pygame.K_f]:
            self.shoot()
        
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            
        if self.special_ability_cooldown > 0:
            self.special_ability_cooldown -= 1
        
        if self.on_ice:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.vel_x = -self.ice_speed
                self.facing_right = False
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.vel_x = self.ice_speed
                self.facing_right = True
            else:
                self.vel_x *= self.ice_friction
                if abs(self.vel_x) < 0.1:
                    self.vel_x = 0
        else:
            self.vel_x = 0
            
            self.is_running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
            
            if self.is_running:
                self.speed = self.sprint_speed
                self.animation_speed = 0.25
            else:
                self.speed = self.walk_speed
                self.animation_speed = 0.15

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.vel_x = -self.speed
                self.facing_right = False
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.vel_x = self.speed
                self.facing_right = True
        
        jump_key = keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]
        
        if jump_key and not self.jump_pressed and self.grounded and self.jump_cooldown <= 0:
            sound_manager.play_sound(sound_manager.player_sounds, "jump")
            
            if self.on_ice:
                self.vel_y = -self.ice_jump_strength
            else:
                self.vel_y = -JUMP_STRENGTH * self.jump_boost_multiplier
                if self.jump_boost_active:
                    self.jump_boost_streak_timer = self.jump_boost_streak_duration

            self.grounded = False
            self.jump_cooldown = 15
        
        self.jump_pressed = jump_key
    
    def apply_gravity(self):
        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED
    
    def update(self, tiles):
        
        if self.heal_effect_timer > 0:
            self.heal_effect_timer -= 1

        if self.jump_boost_streak_timer > 0:
            self.jump_boost_streak_timer -= 1

        if self.shield_active and self.shield_frames:
            self.shield_frame_timer += 1
            self.shield_glow_pulse += 0.08

            if self.shield_frame_timer >= self.shield_frame_duration:
                self.shield_frame_timer = 0
                if self.shield_frame_index < len(self.shield_frames) - 1:
                    self.shield_frame_index += 1

        if self.powerup_timer > 0:
            self.powerup_timer -= 1
            
            if self.powerup_timer <= 0:
                if self.active_powerup == "jump_boost":
                    self.jump_boost_active = False
                    self.jump_boost_multiplier = 1.0
                elif self.active_powerup == "shield":
                    self.shield_active = False
                    self.invincible = False
                    self.shield_break_effect = True
                    self.shield_break_timer = len(self.shield_frames) if self.shield_frames else 0
                    self.shield_frame_index = 0
                    self.shield_frame_timer = 0
                self.active_powerup = None
        
        if self.shield_break_effect:
            self.shield_break_frame_timer += 1
            if self.shield_break_frame_timer >= self.shield_break_frame_duration:
                self.shield_break_frame_timer = 0
                if self.shield_break_timer > 0:
                    self.shield_break_timer -= 1
                else:
                    self.shield_break_effect = False
                    self.shield_frame_index = 0

        if not self.alive:
            if self.death_by_void:
                self.ready_to_respawn = True
                return
            
            if self.death_timer > 0:
                self.death_timer -= 1
                self.animate()
            else:
                if self.death_wait_timer < self.death_wait_duration:
                    self.death_wait_timer += 1
                    self.animate()
                else:
                    if not self.ready_to_respawn:
                        self.ready_to_respawn = True
            return
        
        for snowball in self.snowballs.copy():
            if snowball.update():
                snowball.kill()
        
        was_grounded = self.grounded
        
        if self.vel_y == 0:
            test_rect = self.hitbox.copy()
            test_rect.y += 2
            self.grounded = False

            for tile in tiles:
                if test_rect.colliderect(tile.rect):
                    self.grounded = True
                    break
        
        self.check_ice_contact(tiles)
        
        self.effects.update_ice_effect(self.on_ice)
        self.effects.update_damage_effect()
        
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0 and not self.shield_active:
                self.invincible = False
        
        if self.jump_cooldown > 0:
            self.jump_cooldown -= 1
        
        self.apply_gravity()
        self.animate()

        if self.invincible and (self.invincible_timer // 5) % 2 == 0:
            self.image.set_alpha(128)
        else:
            self.image.set_alpha(255)
        
        self.hitbox.x += self.vel_x
        for tile in tiles:
            if self.hitbox.colliderect(tile.rect):
                if self.vel_x > 0:
                    self.hitbox.right = tile.rect.left
                elif self.vel_x < 0:
                    self.hitbox.left = tile.rect.right
                self.vel_x = 0

        current_time = pygame.time.get_ticks()
        if self.grounded and abs(self.vel_x) > 0.5 and not self.jump_pressed:
            delay = self.footstep_delay * 1.5 if self.on_ice else self.footstep_delay
            if current_time - self.last_footstep_time > delay:
                self.last_footstep_time = current_time
                
                if self.on_ice:
                    sound_manager.play_sound(sound_manager.player_sounds, "ice_walk")
                elif self.is_running:
                    sound_manager.play_sound(sound_manager.player_sounds, "run")
                else:
                    sound_manager.play_sound(sound_manager.player_sounds, "walk")
        else:
            for sound_key in ["ice_walk", "walk", "run"]:
                if sound_key in sound_manager.player_sounds and sound_manager.player_sounds[sound_key]:
                    sound_manager.player_sounds[sound_key].stop()
        
        self.hitbox.y += self.vel_y
        self.grounded = False
        for tile in tiles:
            if self.hitbox.colliderect(tile.rect):
                if self.vel_y > 0:
                    self.hitbox.bottom = tile.rect.top
                    self.vel_y = 0
                    self.grounded = True
                elif self.vel_y < 0:
                    self.hitbox.top = tile.rect.bottom
                    self.vel_y = 0
        
        if not was_grounded and self.grounded:
            if self.jump_boost_active:
                self.spawn_jump_boost_landing_snow()

        if not self.on_ice and self.is_running and self.grounded and self.vel_x != 0:
            foot_x = self.hitbox.centerx
            foot_y = self.hitbox.bottom
            if random.random() < 0.5:
                self.particles.add(dustParticle(foot_x, foot_y))

        self.rect.center = self.hitbox.center
        
        if self.rect.y > SCREEN_HEIGHT + 100:
            self.die_by_void()

        self.particles.update()

    def draw_ice_effect(self, screen, camera):
        self.effects.draw_ice_effect(screen, camera, self.image, self.rect)
    
    def take_damage(self, amount):
        if self.invincible or self.shield_active:
            return
        
        self.health -= amount
        self.effects.trigger_damage_effect()
        self.invincible = True
        self.invincible_timer = self.invincible_duration
        
        sound_manager.play_sound(sound_manager.player_sounds, "hurt")
        
        if self.health <= 0:
            self.die()

    def effect_colour(self, color=(100,255,100)):
        self.heal_effect_timer = self.heal_effect_duration
        self.heal_effect_color = color
    
    def die(self):
        if not self.alive:
            return
        
        self.alive = False
        self.health = 0
        self.death_by_void = False
        
        death_frame_count = len(self.animations["death"])
        self.death_duration = 90
        self.death_animation_speed = death_frame_count / self.death_duration
        
        self.death_timer = self.death_duration
        self.death_wait_timer = 0
        self.ready_to_respawn = False
        
        sound_manager.play_sound(sound_manager.player_sounds, "death")
    
    def die_by_void(self):
        if not self.alive:
            return
        
        self.alive = False
        self.health = 0
        self.death_by_void = True
        
        self.death_timer = 0
        self.death_wait_timer = 0
        self.ready_to_respawn = True
        
        sound_manager.play_sound(sound_manager.player_sounds, "death")
    
    def draw_damage_effect(self, screen):
        self.effects.draw_damage_effect(screen)
    
    def draw_ice_vignette(self, screen):
        self.effects.draw_ice_vignette(screen)
    
    def draw_snowballs(self, screen, camera):
        for snowball in self.snowballs:
            if hasattr(snowball, "draw_trail"):
                snowball.draw_trail(screen, camera)
            snowball.draw(screen, camera)
    
    def animate(self):
        if not self.alive:
            if self.death_by_void:
                return
                
            self.state = "death"
            frames = self.animations["death"]
            
            current_anim_speed = self.death_animation_speed
            
            if self.death_timer > 0:
                if self.frame_index < len(frames) - 1:
                    self.frame_index += current_anim_speed
            else:
                self.frame_index = len(frames) - 1
                
            frame_idx = min(int(self.frame_index), len(frames) - 1)
            self.image = frames[frame_idx]
            if not self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)
            return

        elif self.shooting:
            frames = self.animations["shoot"]
            if frames:
                self.frame_index += self.animation_speed
                if self.frame_index >= len(frames):
                    self.frame_index = 0
                    self.shooting = False
                    self.state = "idle"
                frame_idx = min(int(self.frame_index), len(frames) - 1)
                self.image = frames[frame_idx]

        elif not self.grounded:
            self.state = "jump"
            frames = self.animations["jump"]
            frame_idx = min(int(self.frame_index), len(frames) - 1)
            self.image = frames[frame_idx]

        elif self.vel_x != 0:
            if self.is_running and not self.on_ice:
                self.state = "run"
                frames = self.animations["run"]
            else:
                self.state = "walk"
                frames = self.animations["walk"]
            frame_idx = min(int(self.frame_index), len(frames) - 1)
            self.image = frames[frame_idx]

        else:
            self.state = "idle"
            frames = self.animations["idle"]
            frame_idx = min(int(self.frame_index), len(frames) - 1)
            self.image = frames[frame_idx]

        if not self.shooting:
            if self.state == "run":
                self.animation_speed = 0.25
            elif self.state == "walk":
                self.animation_speed = 0.15
            else:
                self.animation_speed = 0.1

            frames = self.animations.get(self.state, self.animations["idle"])

            if frames:
                self.frame_index += self.animation_speed
                if self.frame_index >= len(frames):
                    self.frame_index = 0
                frame_idx = min(int(self.frame_index), len(frames) - 1)
                self.image = frames[frame_idx]

        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    def get_respawns_left(self):
        return max(0, self.max_respawns - self.respawn_count)
    

    def draw_heal_effect(self, screen, camera):
        if self.heal_effect_timer <= 0:
            return

        pos = camera.apply(self)
        center_x = pos[0] + self.rect.width // 2
        center_y = pos[1] + self.rect.height // 2

        progress = self.heal_effect_timer / self.heal_effect_duration
        inverse_progress = 1.0 - progress

        if progress > 0.8:
            flash_alpha = int(255 * (progress - 0.8) * 5)
            flash_surf = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            flash_surf.fill((*self.heal_effect_color, flash_alpha // 3))
            screen.blit(flash_surf, (0, 0))

        ring_radius = int(self.rect.width * 0.5 + inverse_progress * 100)
        ring_thickness = max(1, int(10 * progress))
        ring_alpha = int(255 * progress)
        
        if ring_radius > 0 and ring_alpha > 0:
            ring_surf = pygame.Surface((ring_radius * 2 + 10, ring_radius * 2 + 10), pygame.SRCALPHA)
            pygame.draw.circle(
                ring_surf,
                (*self.heal_effect_color, ring_alpha),
                (ring_radius + 5, ring_radius + 5),
                ring_radius,
                ring_thickness
            )
            screen.blit(ring_surf, (center_x - ring_radius - 5, center_y - ring_radius - 5), special_flags=pygame.BLEND_RGBA_ADD)

        glow_pulse = math.sin(inverse_progress * 10) * 0.2 + 1.0
        glow_radius = int(max(self.rect.width, self.rect.height) * 0.8 * glow_pulse)
        glow_alpha = int(200 * progress)

        if glow_radius > 0:
            glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            for i in range(3, 0, -1):
                r = int(glow_radius * (i / 3.0))
                a = int(glow_alpha / i)
                if r > 0:
                    pygame.draw.circle(
                        glow_surf,
                        (*self.heal_effect_color, a),
                        (glow_radius, glow_radius),
                        r
                    )
            screen.blit(glow_surf, (center_x - glow_radius, center_y - glow_radius), special_flags=pygame.BLEND_RGBA_ADD)

        streak_count = 5
        base_y = center_y + self.rect.height // 2
        for i in range(streak_count):
            offset_x = math.sin(i * 13.5) * (self.rect.width * 0.8)
            speed = 30 + (i * 15 % 30)
            
            streak_y = base_y - (inverse_progress * speed * 2) - (i * 10 % 20)
            streak_length = 10 + (i * 5 % 15)
            
            streak_alpha = int(255 * progress * max(0, min(1, 0.5 + 0.5 * math.sin(progress * 20 + i))))
            if streak_alpha > 0:
                pygame.draw.line(
                    screen,
                    (*self.heal_effect_color, streak_alpha),
                    (center_x + offset_x, streak_y),
                    (center_x + offset_x, streak_y - streak_length),
                    int(2 + (i % 3))
                )

    def draw_jump_boost_streak(self, screen, camera):
        if self.jump_boost_streak_timer <= 0:
            return

        pos = camera.apply(self)
        center_x = pos[0] + self.rect.width // 2
        top_y = pos[1]

        progress = self.jump_boost_streak_timer / self.jump_boost_streak_duration
        alpha = int(255 * progress)

        streak_surf = pygame.Surface((self.rect.width + 30, self.rect.height + 60), pygame.SRCALPHA)
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

    def spawn_jump_boost_landing_snow(self):

        foot_x = self.hitbox.centerx
        foot_y = self.hitbox.bottom

        for _ in range(12):
            p = dustParticle(foot_x, foot_y)

            p.vel_x = random.uniform(-3.5, 3.5)
            p.vel_y = random.uniform(-2.5, -0.5)

            if hasattr(p, "color"):
                p.color = (255, 255, 255)

            self.particles.add(p)

    def draw_shield_effect(self, screen, camera):
        if not self.shield_active and not self.shield_break_effect:
            return

        if not self.shield_frames:
            return

        pos = camera.apply(self)
        center_x = pos[0] + self.rect.width // 2
        center_y = pos[1] + self.rect.height // 2

        if self.shield_active:
            frame = self.shield_frames[self.shield_frame_index]
        else:
            break_index = len(self.shield_frames) - self.shield_break_timer
            break_index = max(0, min(break_index, len(self.shield_frames) - 1))
            frame = self.shield_frames[break_index]

        shield_size = max(self.rect.width, self.rect.height) + 30
        frame_scaled = pygame.transform.smoothscale(frame, (shield_size, shield_size))

        if self.shield_active:
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

    def load_shield_frames(self, path, frame_count=7):
        try:
            sheet = pygame.image.load(path).convert_alpha()
        except:
            return []

        frame_width = sheet.get_width() // frame_count
        frame_height = sheet.get_height()
        frames = []

        for i in range(frame_count):
            frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            frame.blit(sheet, (0, 0), (i * frame_width, 0, frame_width, frame_height))
            frames.append(frame)

        return frames

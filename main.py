import pygame
import sys
import os

sys.path.append('src')
import io
import random
import math

if sys.stdout is not None:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

pygame.init()

from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, LEVEL_FILES
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("The Last Christmas Run")

from settings import *
from player import Player
from level import Level
from camera import Camera
from menu import Menu
from hud import ChristmasHUD
from particles import snowParticle, dustParticle
from cinematic import CinematicManager
from cinematic_outro import CinematicOutroManager
from boss import Boss, BOSS_TILE_ID
from fireworks import FireworkManager
from sound_manager import sound_manager

background_img_level1 = None
background_img_level2 = None

try:
    bg_path_level1 = os.path.join('assets', 'editor', 'background_level1.png')
    if os.path.exists(bg_path_level1):
        background_img_level1 = pygame.image.load(bg_path_level1).convert_alpha()
        background_img_level1 = scale_bg(background_img_level1)
    else:
        bg_path_default = os.path.join('assets', 'editor', 'background_default.png')
        if os.path.exists(bg_path_default):
            background_img_level1 = pygame.image.load(bg_path_default).convert_alpha()
            background_img_level1 = scale_bg(background_img_level1)
        else:
            background_img_level1 = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            background_img_level1.fill((100, 150, 200))
    
    bg_path_level2 = os.path.join('assets', 'editor', 'background_level2.png')
    if os.path.exists(bg_path_level2):
        background_img_level2 = pygame.image.load(bg_path_level2).convert_alpha()
        background_img_level2 = scale_bg(background_img_level2)
    else:
        background_img_level2 = background_img_level1
        
except Exception as e:
    background_img_level1 = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background_img_level1.fill((100, 150, 200))
    background_img_level2 = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background_img_level2.fill((150, 100, 100))

class Game:
    def __init__(self, level_file='data/level0_data.csv'):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont('Futura', 30)
        self.small_font = pygame.font.SysFont('Futura', 20)
        
        self.level_file = level_file
        
        if 'level0' in level_file:
            self.current_level_index = 0
        elif 'level1' in level_file:
            self.current_level_index = 1
        else:
            self.current_level_index = 0
        
        self.load_current_level()
        
        self.game_state = "playing"
        self.show_debug = False
        
        self.hud = ChristmasHUD(self.screen)
        self.total_presents_collected = 0
        self.houses_delivered = 0

        self.snow_particles = [snowParticle() for _ in range(150)]

        self.wind = 0
        self.wind_target = 0
        
        self.cinematic_intro = CinematicManager()
        self.cinematic_outro = CinematicOutroManager()
        self.boss_spawned = False
        self.boss_triggered = False
        self.boss_weakened_triggered = False

        self.fireworks = FireworkManager()
        
        self.victory_fireworks_started = False
        self.game_over_started = False
        
        self.debug_counter = 0

    def start_level_music(self):
        sound_manager.stop_music()
        
        if self.current_level_index == 0:
            sound_manager.play_music("level1.mp3")
        elif self.current_level_index == 1:
            sound_manager.play_music("level2.mp3")
        else:
            sound_manager.play_music("background.mp3")

    def load_current_level(self):
        if self.current_level_index == 0:
            bg_to_use = background_img_level1
        elif self.current_level_index == 1:
            bg_to_use = background_img_level2
        else:
            bg_to_use = background_img_level1
        
        self.level = Level(self.level_file, bg_to_use)
        
        player_x, player_y = self.level.find_player_start()
        
        self.player = Player(player_x, player_y, self.current_level_index)
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, self.level.level_width)
        
        sound_manager.set_player_reference(self.player)
        
        self.boss_spawned = False
        self.boss_triggered = False
        self.boss_weakened_triggered = False
        
        self.victory_fireworks_started = False
        self.game_over_started = False
        
        self.start_level_music()
        
    def spawn_boss(self, x, y):
        if not self.boss_spawned:
            level_num = 0 if 'level0' in self.level_file else 1
            boss = Boss(x, y, level_num)
            boss.level = self.level
            self.level.enemies.add(boss)
            self.level.all_sprites.add(boss)
            self.boss_spawned = True
        
    def remove_boss(self, x, y):
        if hasattr(self, 'weakened_boss') and self.weakened_boss:
            self.weakened_boss.kill()
            delattr(self, 'weakened_boss')
    
    def next_level(self):
        self.current_level_index += 1
        if self.current_level_index < len(LEVEL_FILES):
            self.level_file = LEVEL_FILES[self.current_level_index]
            self.load_current_level()
            self.game_state = "playing"
            return True
        else:
            self.game_state = "game_complete"
            sound_manager.stop_music()
            return False
    
    def restart_level(self):
        self.load_current_level()
        self.game_state = "playing"
        self.victory_fireworks_started = False
        self.game_over_started = False
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                
                if event.key == pygame.K_r:
                    self.restart_level()
                
                if event.key == pygame.K_F1:
                    self.show_debug = not self.show_debug
                
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    if event.key == pygame.K_0:
                        self.current_level_index = 0
                        self.level_file = LEVEL_FILES[0]
                        self.restart_level()
                    elif event.key == pygame.K_1 and len(LEVEL_FILES) > 1:
                        self.current_level_index = 1
                        self.level_file = LEVEL_FILES[1]
                        self.restart_level()
                    elif event.key == pygame.K_2 and len(LEVEL_FILES) > 2:
                        self.current_level_index = 2
                        self.level_file = LEVEL_FILES[2]
                        self.restart_level()
    
    def update(self):
        
        self.cinematic_intro.update(self.player, self.camera)
        self.cinematic_outro.update(self.player, self.camera)
        
        if not self.boss_triggered and hasattr(self.level, 'boss_spawn_x') and not self.boss_spawned:
            distance = abs(self.player.rect.centerx - self.level.boss_spawn_x)
            if distance < SCREEN_WIDTH * 0.3:
                self.boss_triggered = True
                self.cinematic_intro.start_boss_intro(
                    self.level.boss_spawn_x,
                    self.level.boss_spawn_y,
                    self.player.rect.centerx,
                    self.camera.scroll,
                    self.current_level_index,
                    self.spawn_boss
                )
        
        if not self.boss_weakened_triggered:
            for enemy in self.level.enemies:
                if hasattr(enemy, 'weakened') and enemy.weakened:
                    self.boss_weakened_triggered = True
                    
                    self.weakened_boss = enemy
                    enemy.visible = False
                    
                    boss_x = enemy.rect.centerx
                    boss_y = enemy.rect.y
                    
                    self.cinematic_outro.start_boss_outro(
                        boss_x,
                        boss_y,
                        self.player.rect.centerx,
                        self.camera.scroll,
                        self.remove_boss
                    )
                    break
        
        if not self.cinematic_intro.freeze_player and not self.cinematic_outro.freeze_player:
            if self.game_state == "playing":
                keys = pygame.key.get_pressed()
                self.player.handle_input(keys)
                
                self.player.update(self.level.tiles)
                
                result = self.level.update(self.player, self.camera)
                
                if result == "gate":
                    sound_manager.play_sound(sound_manager.ui_sounds, "next_level")
                    if not self.next_level():
                        pass
                elif result == "dead":
                    if self.player.death_timer <= 0 and not self.player.alive and self.player.respawn_count >= self.player.max_respawns:
                        self.game_state = "game_over"
                        sound_manager.stop_music()
                        sound_manager.play_sound(sound_manager.ui_sounds, "game_over")
                
                if not self.cinematic_intro.active and not self.cinematic_outro.active:
                    self.camera.update(self.player)

                if random.random() < 0.01:
                    self.wind_target = random.uniform(-1.5, 1.5)
                self.wind += (self.wind_target - self.wind) * 0.01

                if hasattr(self.level, 'blizzard') and self.level.blizzard is not None:
                    shake_x, shake_y = self.level.blizzard.get_shake_offset()
                    self.camera.set_shake(shake_x, shake_y)

                for snow in self.snow_particles:
                    snow.update(self.wind, SCREEN_WIDTH, SCREEN_HEIGHT)
        
        if self.game_state == "game_complete":
            self.fireworks.update()

    def draw_bg(self):
        self.screen.fill(GREEN)
        
        current_bg = self.level.background_img if hasattr(self.level, 'background_img') else None
        
        if current_bg:
            bg_width = current_bg.get_width()
            bg_scroll = self.camera.scroll * 0.5
            level_width = self.level.level_width
            tiles_needed = (level_width // bg_width) + 3
            start_x = -bg_width + (-bg_scroll % bg_width)
            
            for i in range(tiles_needed):
                x_pos = start_x + (i * bg_width)
                if x_pos < SCREEN_WIDTH + bg_width and x_pos > -bg_width:
                    self.screen.blit(current_bg, (x_pos, 0))

        for snow in self.snow_particles:
            snow.draw(self.screen)

    def draw_hud(self):
        self.hud.draw(
            player=self.player,
            level=self.level,
            current_level_index=self.current_level_index,
            show_debug=self.show_debug,
            camera=self.camera if self.show_debug else None
        )

    def draw(self):
        self.draw_bg()
        
        for sprite in self.level.all_sprites:
            if hasattr(sprite, 'visible') and not sprite.visible:
                continue
            pos = self.camera.apply(sprite)
            if -TILE_SIZE < pos[0] < SCREEN_WIDTH + TILE_SIZE:
                self.screen.blit(sprite.image, pos)

        if hasattr(self.level, 'blizzard') and self.level.blizzard is not None:
            self.level.blizzard.draw(self.screen)
        
        self.player.draw_snowballs(self.screen, self.camera)

        for checkpoint in self.level.checkpoints:
            checkpoint.draw_popup(self.screen, self.camera)
        
        for gate in self.level.gates:
            gate.draw_smoke(self.screen, self.camera)
        
        for enemy in self.level.enemies:
            if hasattr(enemy, 'visible') and not enemy.visible:
                continue
            enemy.draw_health_bar(self.screen, self.camera)

        for hazard in self.level.hazards:
            hazard.draw_snowballs(self.screen, self.camera)
        
        for collectible in self.level.collectibles:
            collectible.draw_effect(self.screen, self.camera)
        
        for enemy in self.level.enemies:
            if hasattr(enemy, 'visible') and not enemy.visible:
                continue
            if hasattr(enemy, 'draw_effects'): 
                enemy.draw_effects(self.screen, self.camera)

        self.cinematic_intro.draw(self.screen, self.camera)
        self.cinematic_outro.draw(self.screen, self.camera)
        
        if not self.cinematic_intro.freeze_player and not self.cinematic_outro.freeze_player:
            player_pos = self.camera.apply(self.player)
            self.screen.blit(self.player.image, player_pos)
            self.player.draw_ice_effect(self.screen, self.camera)
            self.player.draw_damage_effect(self.screen)
            self.player.draw_ice_vignette(self.screen)
            
            self.player.draw_heal_effect(self.screen, self.camera)
            self.player.draw_jump_boost_streak(self.screen, self.camera)
            self.player.draw_shield_effect(self.screen, self.camera)

            for particle in self.player.particles:
                particle_pos = self.camera.apply(particle)
                self.screen.blit(particle.image, particle_pos)
        
        for checkpoint in self.level.checkpoints:
            checkpoint.draw_requirements(self.screen, self.camera)
        
        if self.game_state == "game_complete":
            if not self.victory_fireworks_started:
                self.fireworks.start_victory()
                self.victory_fireworks_started = True
            
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(80)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            if self.fireworks.active and self.fireworks.mode == "victory":
                self.fireworks.draw(self.screen)
            
            self.draw_victory_message("VICTORY!", "You saved Christmas!")
        
        elif self.game_state == "game_over":
            if not self.game_over_started:
                self.game_over_started = True
            
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            self.draw_game_over_message("GAME OVER", "Press R to restart")
        
        else:
            self.draw_hud()
        
        self.debug_counter += 1
        
        pygame.display.flip()
    
    def draw_victory_message(self, title, subtitle=""):
        
        title_font = pygame.font.SysFont('Futura', 82, bold=True)
        
        for i in range(5, 0, -1):
            glow_size = i * 2
            glow_alpha = 100 - i * 15
            glow_surf = title_font.render(title, True, (255, 215, 0))
            glow_rect = glow_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50 + i))
            glow_surf.set_alpha(max(0, glow_alpha))
            self.screen.blit(glow_surf, glow_rect)
        
        title_surf = title_font.render(title, True, (255, 255, 100))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(title_surf, title_rect)
        
        if subtitle:
            sub_font = pygame.font.SysFont('Futura', 48, bold=True, italic=True)
            
            for i in range(3):
                glow_sub = sub_font.render(subtitle, True, (255, 255, 255))
                glow_sub_rect = glow_sub.get_rect(center=(SCREEN_WIDTH // 2 + i, SCREEN_HEIGHT // 2 + 20 + i))
                glow_sub.set_alpha(100 - i * 30)
                self.screen.blit(glow_sub, glow_sub_rect)
            
            sub_surf = sub_font.render(subtitle, True, WHITE)
            sub_rect = sub_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            self.screen.blit(sub_surf, sub_rect)
    
    def draw_game_over_message(self, title, subtitle=""):
        
        title_font = pygame.font.SysFont('Futura', 72, bold=True)
        
        shadow_surf = title_font.render(title, True, (100, 0, 0))
        shadow_rect = shadow_surf.get_rect(center=(SCREEN_WIDTH // 2 + 4, SCREEN_HEIGHT // 2 - 50 + 4))
        self.screen.blit(shadow_surf, shadow_rect)
        
        for i in range(3):
            glow_surf = title_font.render(title, True, (150, 0, 0))
            glow_rect = glow_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            glow_surf.set_alpha(50 - i * 15)
            self.screen.blit(glow_surf, glow_rect)
        
        title_surf = title_font.render(title, True, RED)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(title_surf, title_rect)
        
        if subtitle:
            sub_font = pygame.font.SysFont('Futura', 36)
            sub_surf = sub_font.render(subtitle, True, WHITE)
            sub_rect = sub_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            
            bg_rect = sub_rect.inflate(20, 10)
            bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            bg_surf.fill((50, 0, 0, 150))
            self.screen.blit(bg_surf, bg_rect)
            
            self.screen.blit(sub_surf, sub_rect)
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

def main():
    menu = Menu(screen)
    result = menu.run()
    
    if result == "start":
        game = Game('level0_data.csv')
        game.run()
    elif result == "level0_data.csv" or result == "level1_data.csv":
        game = Game(result)
        game.run()
    else:
        game = Game('level0_data.csv')
        game.run()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
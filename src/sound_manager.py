import pygame
import os
import math

from settings import TILE_SIZE

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        
        self.master_volume = 0.5
        self.music_volume = 0.4
        
        self.sfx_volume = 1
        
        self.volumes = {
            "jump": 0.08,
            "run": 0.03,
            "walk": 0.3,
            "ice_walk": 0.2,           
            "land": 0.1,
            "snowball": 0.1,
            "ice_shard": 0.3,
            "hurt": 0.1,
            "death": 0.1,
            
            "cannon": 0.3,
            
            "boss_smash": 0.2,
            "boss_intro_level1": 0.8,
            "boss_intro_level2": 0.8,
            "boss_outro": 0.8,
            "boss_fight": 0.25,

            "blizzard_warning": 0.8,
            "blizzard_wind": 10,
            "blizzard_howl": 0.7,
            
            "checkpoint": 2,
            "gift": 1,
            "powerup": 0.2,
            
            "game_over": 0.5,
            "next_level": 0.5,
            
            "firework": 0.5,
            
            "level1": 0.05,       
            "level2": 0.3,      
            "background": 0.05,     
        }
        
        self.default_hearing_range = TILE_SIZE * 10
        
        self.sound_ranges = {
            "cannon": TILE_SIZE * 8,
            "run": TILE_SIZE * 5,
            "walk": TILE_SIZE * 3,
            "ice_walk": TILE_SIZE * 4,
            "jump": TILE_SIZE * 8,
            "snowball": TILE_SIZE * 8,
            "ice_shard": TILE_SIZE * 8,
            "boss_smash": TILE_SIZE * 15,
            "boss_intro_level1": TILE_SIZE * 20,
            "boss_intro_level2": TILE_SIZE * 20,
            "boss_outro": TILE_SIZE * 20,
            "powerup": TILE_SIZE * 6,
            "firework": TILE_SIZE * 20,
        }
        
        self.player_sounds = {}
        self.hazard_sounds = {}
        self.boss_sounds = {}
        self.item_sounds = {}
        self.powerup_sounds = {}
        self.ui_sounds = {}
        self.firework_sounds = {}

        
        self.current_music = None
        self.music_playing = False
        
        self.player = None
        
        self.load_all_sounds()
        
        self.play_music("background.mp3")
    
    def set_player_reference(self, player):
        self.player = player
    
    def load_all_sounds(self):
        sound_folder = "sounds"
        
        if not os.path.exists(sound_folder):
            os.makedirs(sound_folder)
            return
        
        player_folder = os.path.join(sound_folder, "player")
        if os.path.exists(player_folder):
            self.player_sounds = {
                "jump": self.load_sound(os.path.join(player_folder, "jump.mp3")),
                "run": self.load_sound(os.path.join(player_folder, "run.mp3")),
                "walk": self.load_sound(os.path.join(player_folder, "walk.mp3")),
                "ice_walk": self.load_sound(os.path.join(player_folder, "ice_walk.mp3")),
                "hurt": self.load_sound(os.path.join(player_folder, "hurt.mp3")),
                "death": self.load_sound(os.path.join(player_folder, "death.mp3")),
                "snowball": self.load_sound(os.path.join(player_folder, "snowball.mp3")),
                "collision": self.load_sound(os.path.join(player_folder, "collision.mp3")),
            }
            self.player_sounds["ice_shard"] = self.load_sound(os.path.join(sound_folder, "powerup.ice_shard.mpeg"))
        
        powerup_folder = os.path.join(sound_folder, "powerup")
        if os.path.exists(powerup_folder):
            self.powerup_sounds = {
                "powerup": self.load_sound(os.path.join(powerup_folder, "powerup.mpeg")),
                "ice_shard": self.load_sound(os.path.join(powerup_folder, "ice_shard.mpeg")),
            }
        
        hazard_folder = os.path.join(sound_folder, "hazard")
        if os.path.exists(hazard_folder):
            self.hazard_sounds = {
                "cannon": self.load_sound(os.path.join(hazard_folder, "cannon.mp3")),
                
                "blizzard_warning": self.load_sound(os.path.join(hazard_folder, "blizzard_warning.mp3")),
                "blizzard_wind": self.load_sound(os.path.join(hazard_folder, "blizzard_wind.mp3")),
                "blizzard_howl": self.load_sound(os.path.join(hazard_folder, "blizzard_howl.mp3")),
            }
        
        boss_folder = os.path.join(sound_folder, "boss")
        if os.path.exists(boss_folder):
            boss_smash_path = os.path.join(boss_folder, "boss_smash.mpeg")
            if os.path.exists(boss_smash_path):
                self.boss_sounds["boss_smash"] = self.load_sound(boss_smash_path)
            
            intro_level1_path = os.path.join(boss_folder, "intro_level1.mpeg")
            if os.path.exists(intro_level1_path):
                self.boss_sounds["boss_intro_level1"] = self.load_sound(intro_level1_path)
            
            intro_level2_path = os.path.join(boss_folder, "intro_level2.mpeg")
            if os.path.exists(intro_level2_path):
                self.boss_sounds["boss_intro_level2"] = self.load_sound(intro_level2_path)
            
            outro_path = os.path.join(boss_folder, "outro.mpeg")
            if os.path.exists(outro_path):
                self.boss_sounds["boss_outro"] = self.load_sound(outro_path)
            
        else:
            os.makedirs(boss_folder, exist_ok=True)
        
        item_folder = os.path.join(sound_folder, "items")
        if os.path.exists(item_folder):
            self.item_sounds = {
                "checkpoint": self.load_sound(os.path.join(item_folder, "checkpoint.mp3")),
                "gift": self.load_sound(os.path.join(item_folder, "gift.mp3")),
            }
        
        ui_folder = os.path.join(sound_folder, "ui")
        if os.path.exists(ui_folder):
            self.ui_sounds = {
                "game_over": self.load_sound(os.path.join(ui_folder, "game_over.mp3")),
                "next_level": self.load_sound(os.path.join(ui_folder, "next_level.mp3")),
            }
        
        firework_folder = os.path.join(sound_folder, "fireworks")
        if os.path.exists(firework_folder):
            firework_path = os.path.join(firework_folder, "firework.mp3")
            if os.path.exists(firework_path):
                self.firework_sounds["firework"] = self.load_sound(firework_path)
            else:
                self.firework_sounds = {}
        else:
            os.makedirs(firework_folder, exist_ok=True)
            self.firework_sounds = {}
    
    def load_sound(self, path):
        try:
            if os.path.exists(path):
                sound = pygame.mixer.Sound(path)
                sound.set_volume(self.sfx_volume * self.master_volume)
                return sound
            else:
                return None
        except Exception as e:
            return None
    
    def calculate_distance_volume(self, world_x, world_y, sound_key):
        if not self.player:
            return 1.0
        
        hearing_range = self.sound_ranges.get(sound_key, self.default_hearing_range)
        
        dx = world_x - self.player.rect.centerx
        dy = world_y - self.player.rect.centery
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > hearing_range:
            return 0.0
        
        distance_ratio = distance / hearing_range
        volume_multiplier = 1.0 - (distance_ratio * distance_ratio)
        
        return max(0.0, min(1.0, volume_multiplier))
    
    def play_sound(self, sound_dict, key, world_x=None, world_y=None, volume_scale=1.0):
        if key in sound_dict and sound_dict[key]:
            base_volume = self.volumes.get(key, 0.5)
            
            distance_multiplier = 1.0
            if world_x is not None and world_y is not None:
                distance_multiplier = self.calculate_distance_volume(world_x, world_y, key)
                if distance_multiplier <= 0:
                    return False
            
            final_volume = (self.master_volume * 
                          self.sfx_volume * 
                          base_volume * 
                          distance_multiplier *
                          volume_scale)
            
            final_volume = min(1.0, final_volume)
            
            sound_dict[key].set_volume(final_volume)
            sound_dict[key].play()
            return True
        return False
    
    def play_boss_smash(self, world_x=None, world_y=None):
        return self.play_sound(self.boss_sounds, "boss_smash", world_x, world_y)
    
    def play_boss_intro_level1(self, world_x=None, world_y=None):
        return self.play_sound(self.boss_sounds, "boss_intro_level1", world_x, world_y)
    
    def play_boss_intro_level2(self, world_x=None, world_y=None):
        return self.play_sound(self.boss_sounds, "boss_intro_level2", world_x, world_y)
    
    def play_boss_outro(self, world_x=None, world_y=None):
        return self.play_sound(self.boss_sounds, "boss_outro", world_x, world_y)
    
    def play_powerup(self, world_x=None, world_y=None, volume_scale=1.0):
        return self.play_sound(self.powerup_sounds, "powerup", world_x, world_y, volume_scale)
    
    def play_firework(self, world_x=None, world_y=None, volume_scale=1.0):
        return self.play_sound(self.firework_sounds, "firework", world_x, world_y, volume_scale)
    
    def play_continuous_sound(self, sound_dict, key, world_x, world_y, channel=None, volume_scale=1.0):
        if key in sound_dict and sound_dict[key]:
            base_volume = self.volumes.get(key, 0.5)
            
            distance_multiplier = self.calculate_distance_volume(world_x, world_y, key)
            
            if distance_multiplier <= 0:
                if channel:
                    channel.stop()
                return None
            
            final_volume = (self.master_volume * 
                          self.sfx_volume * 
                          base_volume * 
                          distance_multiplier *
                          volume_scale)
            final_volume = min(1.0, final_volume)
            
            if channel and channel.get_busy():
                channel.set_volume(final_volume)
                return channel
            else:
                channel = sound_dict[key].play(-1)
                if channel:
                    channel.set_volume(final_volume)
                return channel
        return None
    
    def play_music(self, filename, loop=True):
        try:
            path = os.path.join("sounds", "music", filename)
            if os.path.exists(path):
                if self.music_playing:
                    pygame.mixer.music.stop()
                
                pygame.mixer.music.load(path)
                
                if "boss" in filename:
                    volume_key = "boss"
                elif "level1" in filename:
                    volume_key = "level1"
                elif "level2" in filename:
                    volume_key = "level2"
                else:
                    volume_key = "background"
                
                base_volume = self.volumes.get(volume_key, 0.3)
                
                final_volume = base_volume * self.master_volume
                pygame.mixer.music.set_volume(final_volume)
                
                pygame.mixer.music.play(-1 if loop else 0)
                self.current_music = filename
                self.music_playing = True
                return True
            else:
                return False
        except Exception as e:
            return False
    
    def stop_music(self):
        pygame.mixer.music.stop()
        self.music_playing = False
        self.current_music = None
    
    def pause_music(self):
        pygame.mixer.music.pause()
    
    def unpause_music(self):
        pygame.mixer.music.unpause()
    
    def set_music_track_volume(self, track_name, volume):
        volume = max(0.0, min(1.0, volume))
        
        if track_name == "level1":
            self.volumes["level1"] = volume
            
            if self.current_music and "level1" in self.current_music:
                final_volume = volume * self.master_volume
                pygame.mixer.music.set_volume(final_volume)
                
        elif track_name == "level2":
            self.volumes["level2"] = volume
            
            if self.current_music and "level2" in self.current_music:
                final_volume = volume * self.master_volume
                pygame.mixer.music.set_volume(final_volume)
                
        elif track_name == "background":
            self.volumes["background"] = volume
            
            if self.current_music and "background" in self.current_music:
                final_volume = volume * self.master_volume
                pygame.mixer.music.set_volume(final_volume)
    
    def set_all_music_volumes(self, volume):
        volume = max(0.0, min(1.0, volume))
        self.volumes["level1"] = volume
        self.volumes["level2"] = volume
        self.volumes["background"] = volume
        
        if self.current_music:
            if "level1" in self.current_music:
                base_volume = self.volumes["level1"]
            elif "level2" in self.current_music:
                base_volume = self.volumes["level2"]
            else:
                base_volume = self.volumes["background"]
            
            final_volume = base_volume * self.master_volume
            pygame.mixer.music.set_volume(final_volume)
    
    def get_music_volumes(self):
        return {
            "level1": self.volumes["level1"],
            "level2": self.volumes["level2"],
            "background": self.volumes["background"],
            "master": self.master_volume,
            "current_track": self.current_music
        }
    
    def set_master_volume(self, volume):
        self.master_volume = max(0.0, min(1.0, volume))
        
        if self.music_playing and self.current_music:
            if "level1" in self.current_music:
                base_volume = self.volumes["level1"]
            elif "level2" in self.current_music:
                base_volume = self.volumes["level2"]
            else:
                base_volume = self.volumes["background"]
            
            final_volume = base_volume * self.master_volume
            pygame.mixer.music.set_volume(final_volume)
    
    def set_sfx_volume(self, volume):
        self.sfx_volume = max(0.0, min(1.0, volume))
    
    def set_sound_volume(self, sound_key, volume):
        if sound_key in self.volumes:
            self.volumes[sound_key] = max(0.0, min(1.0, volume))
    
    def set_sound_range(self, sound_key, range_in_pixels):
        self.sound_ranges[sound_key] = max(1, range_in_pixels)
    
    def set_default_range(self, range_in_pixels):
        self.default_hearing_range = max(1, range_in_pixels)
    
    def print_volume_settings(self):
        pass


sound_manager = SoundManager()
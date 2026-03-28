import pygame
from settings import TILE_SIZE, SCREEN_HEIGHT
import math
from sound_manager import sound_manager

class Checkpoint(pygame.sprite.Sprite):
    def __init__(self, x, y, image, checkpoint_id=0):
        super().__init__()
        
        self.checkpoint_id = checkpoint_id
        self.activated = False
        
        self.inactive_img = image.copy()
        self.active_img = image.copy()
        
        tint_surface = pygame.Surface(self.active_img.get_size())
        tint_surface.fill((100, 200, 255))
        tint_surface.set_alpha(80)
        self.active_img.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        
        self.image = self.inactive_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.required_presents = 0
        
        self.show_popup = False
        self.popup_timer = 0
        self.popup_duration = 120
        
        self.arrow_offset = 0
        self.arrow_bounce_speed = 0.03
        self.arrow_bounce_amplitude = 6
        
    def update(self, player, all_checkpoints=None):
        if not self.activated and self.rect.colliderect(player.rect):
            self.activate(all_checkpoints)
            player.set_checkpoint(self.rect.x, self.rect.y, self.checkpoint_id)
            self.show_popup = True
            self.popup_timer = self.popup_duration
            
            sound_manager.play_sound(sound_manager.item_sounds, "checkpoint")
            
            return True
        
        if self.show_popup:
            self.popup_timer -= 1
            if self.popup_timer <= 0:
                self.show_popup = False
                
            self.arrow_offset = math.sin(
                pygame.time.get_ticks() * self.arrow_bounce_speed
            ) * self.arrow_bounce_amplitude
            
        return False
    
    def activate(self, all_checkpoints=None):
        if all_checkpoints:
            for checkpoint in all_checkpoints:
                if checkpoint != self and checkpoint.activated:
                    checkpoint.deactivate()
        
        self.activated = True
        self.image = self.active_img
    
    def deactivate(self):
        self.activated = False
        self.image = self.inactive_img
        self.show_popup = False
    
    def draw_requirements(self, screen, camera):
        if not self.activated and self.required_presents > 0:
            pos = camera.apply(self)
            
            font = pygame.font.SysFont('Futura', 20)
            text = font.render(
                f"Need: {self.required_presents} presents",
                True,
                (255,255,255)
            )
            
            text_rect = text.get_rect(
                center=(pos[0] + TILE_SIZE//2, pos[1] - 20)
            )
            
            bg_rect = text_rect.inflate(10,5)
            
            pygame.draw.rect(screen,(0,0,0,180),bg_rect)
            pygame.draw.rect(screen,(100,200,255),bg_rect,2)
            
            screen.blit(text,text_rect)
    
    def draw_popup(self, screen, camera):
        
        if not self.show_popup:
            return
        
        screen_pos = camera.apply(self)
        
        center_x = screen_pos[0] + TILE_SIZE // 2
        base_y = screen_pos[1] - 100
        
        fade_alpha = 255
        
        if self.popup_timer < 30:
            fade_alpha = int(255 * (self.popup_timer / 30))
        
        arrow_y = base_y - 20 + self.arrow_offset
        
        arrow_width = 32
        arrow_height = 40
        
        arrow_points = [
            (center_x, arrow_y + arrow_height),
            (center_x - arrow_width//2, arrow_y + 16),
            (center_x - arrow_width//4, arrow_y + 16),
            (center_x - arrow_width//4, arrow_y),
            (center_x + arrow_width//4, arrow_y),
            (center_x + arrow_width//4, arrow_y + 16),
            (center_x + arrow_width//2, arrow_y + 16)
        ]
        
        shadow_points = [(x+2,y+2) for (x,y) in arrow_points]
        pygame.draw.polygon(screen,(0,70,140),shadow_points)
        
        pygame.draw.polygon(screen,(0,200,255),arrow_points)
        
        pygame.draw.polygon(screen,(255,255,255),arrow_points,2)
        
        text_y = arrow_y + arrow_height + 20
        
        font_large = pygame.font.SysFont('Futura', 32, bold=True)
        
        shadow_text = font_large.render(
            "CHECKPOINT!", True, (30,60,120)
        )
        
        shadow_rect = shadow_text.get_rect(
            center=(center_x+2, text_y+2)
        )
        
        shadow_text.set_alpha(fade_alpha)
        screen.blit(shadow_text, shadow_rect)
        
        ice_text = font_large.render(
            "CHECKPOINT!", True, (150,220,255)
        )
        
        ice_rect = ice_text.get_rect(
            center=(center_x, text_y)
        )
        
        ice_text.set_alpha(fade_alpha)
        screen.blit(ice_text, ice_rect)
        
        highlight_text = font_large.render(
            "CHECKPOINT!", True, (255,255,255)
        )
        
        highlight_rect = highlight_text.get_rect(
            center=(center_x-1, text_y-1)
        )
        
        highlight_text.set_alpha(int(fade_alpha*0.6))
        screen.blit(highlight_text, highlight_rect)
        
        font_medium = pygame.font.SysFont('Futura', 22, bold=True, italic=True)
        
        reached_y = text_y + 30
        
        shadow_reached = font_medium.render(
            "REACHED!", True, (20,40,80)
        )
        
        shadow_reached_rect = shadow_reached.get_rect(
            center=(center_x+1, reached_y+1)
        )
        
        shadow_reached.set_alpha(fade_alpha)
        screen.blit(shadow_reached, shadow_reached_rect)
        
        reached_text = font_medium.render(
            "REACHED!", True, (100,200,255)
        )
        
        reached_rect = reached_text.get_rect(
            center=(center_x, reached_y)
        )
        
        reached_text.set_alpha(fade_alpha)
        screen.blit(reached_text, reached_rect)
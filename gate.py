import pygame
import os
from settings import *
from smoke import SmokeEffect

class Gate(pygame.sprite.Sprite):
    def __init__(self, x, y, gate_type="level_end", tile_id=41):
        super().__init__()
        
        self.gate_type = gate_type
        self.tile_id = tile_id
        
        self.image = None
        gate_path = os.path.join('tiles', 'gate', f'{tile_id}.png')
        
        if os.path.exists(gate_path):
            try:
                self.image = pygame.image.load(gate_path).convert_alpha()
                self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
            except:
                self.image = self._create_fallback()
        else:
            self.image = self._create_fallback()
        
        self.rect = self.image.get_rect()
        self.rect.bottom = y + TILE_SIZE
        self.rect.x = x
        
        if tile_id == 41:
            self.chimney_x = x + TILE_SIZE // 2 + 8
        else: 
            self.chimney_x = x + 8
        
        self.chimney_y = self.rect.y
        
        self.gifts_required = 0
        self.gifts_deposited = 0
        self.completed = False
        
        self.smoke = SmokeEffect(self.chimney_x, self.chimney_y)
        
    def _create_fallback(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill(GOLD)
        font = pygame.font.SysFont('Futura', 16)
        text = font.render(f"GATE {self.tile_id}", True, BLACK)
        text_rect = text.get_rect(center=(TILE_SIZE//2, TILE_SIZE//2))
        surf.blit(text, text_rect)
        return surf
    
    def update(self, player):
        if self.smoke:
            self.smoke.update()
        
        if self.completed:
            return False
            
        if self.rect.colliderect(player.rect):
            if player.presents_collected > 0:
                self.gifts_deposited += player.presents_collected
                player.deposit_gifts()
            
            if self.gifts_deposited >= self.gifts_required:
                self.completed = True
                if self.smoke:
                    self.smoke.burst(15)
                    self.smoke.stop()
                return True
                
        return False
    
    def draw_smoke(self, screen, camera):
        if self.smoke:
            self.smoke.draw(screen, camera)
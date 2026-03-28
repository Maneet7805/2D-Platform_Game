import pygame

class Button:
    def __init__(self, x, y, image, scale, hover_image=None):
        width = image.get_width()
        height = image.get_height()

        self.image = pygame.transform.scale(
            image,
            (int(width * scale), int(height * scale))
        )
        
        if hover_image:
            self.hover_image = pygame.transform.scale(
                hover_image,
                (int(width * scale), int(height * scale))
            )
        else:
            self.hover_image = self.image
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.clicked = False

    def draw(self, surface):
        action = False
        pos = pygame.mouse.get_pos()
        
        if self.rect.collidepoint(pos):
            surface.blit(self.hover_image, self.rect)
            
            if pygame.mouse.get_pressed()[0] and not self.clicked:
                action = True
                self.clicked = True
        else:
            surface.blit(self.image, self.rect)

        if not pygame.mouse.get_pressed()[0]:
            self.clicked = False

        return action
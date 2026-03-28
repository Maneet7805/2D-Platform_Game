import pygame
import random


pygame.init()

class snowParticle:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.randint(0, 800)
        self.y = random.randint(-600, 0)
        self.radius = random.randint(1, 4)
        self.speed = random.uniform(0.5, 2.5)
        self.wind_resistance = random.uniform(0.4, 1.0)

    def update(self, wind, SCREEN_WIDTH, SCREEN_HEIGHT):
        
        self.y += self.speed
        self.x += wind * self.wind_resistance

        if self.x < 0:
            self.x = SCREEN_WIDTH
        elif self.x > SCREEN_WIDTH:
            self.x = 0

        if self.y > SCREEN_HEIGHT:
            self.x = random.randint(0, SCREEN_WIDTH)
            self.y = random.randint(-50, 0)

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            (255, 255, 255),
            (int(self.x), int(self.y)),
            self.radius
        )

class dustParticle(pygame.sprite.Sprite):
    def __init__(self, x, y, color=(255, 255, 255)):
        super().__init__()
        self.image = pygame.Surface((4, 4), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (2, 2), 2)
        self.rect = self.image.get_rect(center=(x, y))
        self.vel_x = random.randint(-2, 2)
        self.vel_y = random.randint(-4, -1)
        self.lifetime = random.randint(20, 40)

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
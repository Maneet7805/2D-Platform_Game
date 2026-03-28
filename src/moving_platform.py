import pygame
from settings import TILE_SIZE

class MovingPlatform(pygame.sprite.Sprite):
    def __init__(self, x, y, image, move_type="horizontal", distance=200, speed=2):
        super().__init__()
        
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.move_type = move_type  
        self.start_x = x
        self.start_y = y
        self.distance = distance
        self.speed = speed
        self.direction = 1

        self.attached_player = None
        self.prev_rect = self.rect.copy()

        self.level_left_boundary = TILE_SIZE * 2
        self.level_right_boundary = float('inf')
        self.level_top_boundary = 0
        self.level_bottom_boundary = 1000
        
    def set_boundaries(self, left, right, top=0, bottom=1000):
        self.level_left_boundary = left
        self.level_right_boundary = right
        self.level_top_boundary = top
        self.level_bottom_boundary = bottom
        
    def update(self, player=None):
        self.prev_rect.x = self.rect.x
        self.prev_rect.y = self.rect.y

        new_x = self.rect.x
        new_y = self.rect.y

        if self.move_type == "horizontal":
            new_x = self.rect.x + self.speed * self.direction

            if new_x < self.level_left_boundary:
                new_x = self.level_left_boundary
                self.direction *= -1
            elif new_x + self.rect.width > self.level_right_boundary:
                new_x = self.level_right_boundary - self.rect.width
                self.direction *= -1

            if abs(new_x - self.start_x) > self.distance:
                self.direction *= -1
                new_x = self.rect.x + self.speed * self.direction

        elif self.move_type == "vertical":
            new_y = self.rect.y + self.speed * self.direction

            if new_y < self.level_top_boundary:
                new_y = self.level_top_boundary
                self.direction *= -1
            elif new_y + self.rect.height > self.level_bottom_boundary:
                new_y = self.level_bottom_boundary - self.rect.height
                self.direction *= -1

            if abs(new_y - self.start_y) > self.distance:
                self.direction *= -1
                new_y = self.rect.y + self.speed * self.direction

        self.rect.x = new_x
        self.rect.y = new_y

        if player is None:
            return

        dx = self.rect.x - self.prev_rect.x
        dy = self.rect.y - self.prev_rect.y

        LAND_TOLERANCE = max(10, abs(dy) + 4)  
        player_feet_x1 = player.rect.x + 4
        player_feet_x2 = player.rect.right - 4
        platform_x1    = self.rect.x
        platform_x2    = self.rect.right

        feet_over_platform = (player_feet_x2 > platform_x1 and
                              player_feet_x1 < platform_x2)
        feet_at_surface    = (player.rect.bottom >= self.rect.y - LAND_TOLERANCE and
                              player.rect.bottom <= self.rect.y + LAND_TOLERANCE)

        landing = feet_over_platform and feet_at_surface and player.vel_y >= 0

        if landing:
            self.attached_player = player

            player.rect.bottom = self.rect.y
            player.hitbox.y    = player.rect.y + (player.rect.height - player.hitbox.height)

            player.grounded = True
            player.vel_y    = 0

        elif self.attached_player == player:
            jumped_off   = player.vel_y < -1         
            walked_off_h = (player.rect.right <= self.rect.left or
                            player.rect.left  >= self.rect.right)
            fell_through = player.rect.top > self.rect.bottom  

            if jumped_off or walked_off_h or fell_through:
                self.attached_player = None

        if self.attached_player == player:

            if dx != 0:
                new_player_x = player.rect.x + dx
                new_player_x = max(self.level_left_boundary,
                                   min(new_player_x,
                                       self.level_right_boundary - player.rect.width))
                player.rect.x  = new_player_x
                player.hitbox.x = player.rect.x + (player.rect.width - player.hitbox.width) // 2

            if dy != 0:
                new_player_y = player.rect.y + dy
                new_player_y = max(self.level_top_boundary,
                                   min(new_player_y,
                                       self.level_bottom_boundary - player.rect.height))
                player.rect.y  = new_player_y
                player.hitbox.y = player.rect.y + (player.rect.height - player.hitbox.height)

            player.rect.bottom = self.rect.y
            player.hitbox.y    = player.rect.y + (player.rect.height - player.hitbox.height)
            player.grounded    = True
            player.vel_y       = 0
    
    def draw(self, screen, camera):
        screen_x = self.rect.x - camera.scroll
        screen_y = self.rect.y
        screen.blit(self.image, (screen_x, screen_y))
from settings import SCREEN_WIDTH

class Camera:
    def __init__(self, width, height, level_width):
        self.width = width
        self.height = height
        self.level_width = level_width
        self.scroll = 0
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        
    def set_shake(self, offset_x, offset_y):
        self.shake_offset_x = offset_x
        self.shake_offset_y = offset_y
        
    def update(self, target):
        self.scroll = target.rect.centerx - self.width // 2
        self.scroll = max(0, self.scroll)
        self.scroll = min(self.scroll, self.level_width - self.width)
    
    def apply(self, entity):
        if hasattr(entity, 'rect'):
            return (entity.rect.x - self.scroll + self.shake_offset_x, 
                    entity.rect.y + self.shake_offset_y)
        else:
            return (entity.x - self.scroll + self.shake_offset_x, 
                    entity.y + self.shake_offset_y)
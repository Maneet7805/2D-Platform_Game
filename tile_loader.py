import pygame
import os
import json
from tile_config import tile_db, TileCategory

class TileLoader:
    def __init__(self, base_path='tiles'):
        self.base_path = base_path
        
    def load_all_tiles(self, tile_size):
        
        if os.path.exists(tile_db.config_file):
            try:
                tile_db.load_database()
            except:
                pass
        
        folder_categories = {
            'solid': TileCategory.SOLID,
            'decor': TileCategory.DECORATIVE,
            'enemy': TileCategory.ENEMY,
            'gate': TileCategory.GATE,
            'collectible': TileCategory.COLLECTIBLE,
            'checkpoint': TileCategory.CHECKPOINT,
            'hazard': TileCategory.HAZARD,
            'powerup': TileCategory.POWERUP,
            'moving_platform': TileCategory.MOVING_PLATFORM,
        }
        
        tiles_by_id = {}
        
        for folder_name, category in folder_categories.items():
            folder_path = os.path.join(self.base_path, folder_name)
            
            if not os.path.exists(folder_path):
                continue
                
            try:
                png_files = [f for f in os.listdir(folder_path) if f.endswith('.png')]
            except:
                continue
            
            for filename in png_files:
                name_without_ext = os.path.splitext(filename)[0]
                
                parts = name_without_ext.split('_')
                try:
                    tile_id = int(parts[0])
                except ValueError:
                    continue
                
                properties = {}
                for part in parts[1:]:
                    if '=' in part:
                        key, val = part.split('=')
                        try:
                            val = int(val)
                        except:
                            pass
                        properties[key] = val
                
                existing_tile = tile_db.get_tile(tile_id)
                
                if existing_tile:
                    existing_props = existing_tile.properties.copy()
                    existing_props.update(properties)
                    
                    tiles_by_id[tile_id] = {
                        'name': existing_tile.name,
                        'category': existing_tile.category,
                        'folder': folder_name,
                        'filename': filename,
                        'path': os.path.join(folder_path, filename),
                        'properties': existing_props
                    }
                else:
                    tiles_by_id[tile_id] = {
                        'name': parts[0],
                        'category': category,
                        'folder': folder_name,
                        'filename': filename,
                        'path': os.path.join(folder_path, filename),
                        'properties': properties
                    }
        
        for tile_id in sorted(tiles_by_id.keys()):
            tile_data = tiles_by_id[tile_id]
            
            existing_tile = tile_db.get_tile(tile_id)
            
            if not existing_tile:
                tile_db.register_tile(
                    tile_id,
                    tile_data['name'],
                    tile_data['category'],
                    tile_data.get('properties', {})
                )
            
            try:
                img = pygame.image.load(tile_data['path']).convert_alpha()
                img = pygame.transform.scale(img, (tile_size, tile_size))
                tile_db.images[tile_id] = img
            except Exception as e:
                tile_db.images[tile_id] = self._create_fallback(tile_size, tile_data['category'], tile_id)
        
        if not tiles_by_id:
            for i in range(25):
                if 0 <= i <= 11:
                    category = TileCategory.SOLID
                elif i == 17:
                    category = TileCategory.GATE
                elif i == 18:
                    category = TileCategory.ENEMY
                else:
                    category = TileCategory.DECORATIVE
                
                if not tile_db.get_tile(i):
                    tile_db.register_tile(i, f"tile_{i}", category, {})
                tile_db.images[i] = self._create_fallback(tile_size, category, i)
        
        return tile_db
    
    def _create_fallback(self, tile_size, category, tile_id):
        surface = pygame.Surface((tile_size, tile_size))
        
        colors = {
            TileCategory.SOLID: (100, 100, 100),
            TileCategory.DECORATIVE: (0, 150, 0),
            TileCategory.ENEMY: (200, 0, 0),
            TileCategory.GATE: (255, 215, 0),
            TileCategory.COLLECTIBLE: (255, 255, 0),
            TileCategory.CHECKPOINT: (0, 0, 255),
            TileCategory.HAZARD: (255, 165, 0),
            TileCategory.POWERUP: (138, 43, 226),
            TileCategory.MOVING_PLATFORM: (0, 255, 255),
        }
        
        surface.fill(colors.get(category, (255, 255, 255)))
        
        try:
            font = pygame.font.SysFont('Arial', 16)
            text = font.render(str(tile_id), True, (255, 255, 255))
            text_rect = text.get_rect(center=(tile_size//2, tile_size//2))
            surface.blit(text, text_rect)
        except:
            pass
            
        return surface
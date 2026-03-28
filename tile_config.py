import json
import os
from enum import Enum

class TileCategory(Enum):
    SOLID = "solid"
    DECORATIVE = "decorative"
    ENEMY = "enemy"
    GATE = "gate"
    COLLECTIBLE = "collectible"
    CHECKPOINT = "checkpoint"
    HAZARD = "hazard"
    POWERUP = "powerup"
    MOVING_PLATFORM = "moving_platform"

class TileType:
    def __init__(self, tile_id, name, category, properties=None):
        self.tile_id = tile_id
        self.name = name
        self.category = category
        self.properties = properties or {}

class TileDatabase:
    def __init__(self, config_file='tile_database.json'):
        self.tiles = {}
        self.images = {}
        self.config_file = config_file
        
    def register_tile(self, tile_id, name, category, properties=None):
        tile = TileType(tile_id, name, category, properties)
        self.tiles[tile_id] = tile
        return tile
    
    def get_tile(self, tile_id):
        return self.tiles.get(tile_id)
    
    def save_database(self):
        data = {
            str(tile_id): {
                'name': tile.name,
                'category': tile.category.value,
                'properties': tile.properties
            }
            for tile_id, tile in self.tiles.items()
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_database(self):
        if not os.path.exists(self.config_file):
            return False
        
        with open(self.config_file, 'r') as f:
            data = json.load(f)
        
        for tile_id_str, tile_data in data.items():
            tile_id = int(tile_id_str)
            category = TileCategory(tile_data['category'])
            self.register_tile(
                tile_id, 
                tile_data['name'], 
                category, 
                tile_data.get('properties', {})
            )
        return True

tile_db = TileDatabase()
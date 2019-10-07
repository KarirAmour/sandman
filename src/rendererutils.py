from config import MAP_TILE_WIDTH, MAP_TILE_HEIGHT, MAP_WIDTH, \
  MAP_HEIGHT, MAP_BORDER_WIDTH
import pygame

class RendererUtils:
  @staticmethod
  def get_screen_size():
    display = pygame.display.get_surface()
    
    return display.get_size() if display != None else (0,0)

  #----------------------------------------------------------------------------

  @staticmethod  
  def get_map_render_position(): 
    screen_size = RendererUtils.get_screen_size()
    return ((screen_size[0] - MAP_BORDER_WIDTH * 2 - MAP_TILE_WIDTH * MAP_WIDTH) / 2,(screen_size[1] - MAP_BORDER_WIDTH * 2 - MAP_TILE_HEIGHT * MAP_HEIGHT - 50) / 2)  

  #----------------------------------------------------------------------------
    
  @staticmethod
  def map_position_to_pixel_position(map_position, offset = (0,0)):
    map_render_location = RendererUtils.get_map_render_position()
    return (map_render_location[0] + int(map_position[0] * MAP_TILE_WIDTH) + MAP_BORDER_WIDTH + offset[0],map_render_location[1] + int(map_position[1] * MAP_TILE_HEIGHT) + MAP_BORDER_WIDTH + offset[1])
 
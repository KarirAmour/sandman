from config import MapConfig
import pygame

class RendererUtils:

  COLOR_RGB_VALUES = [
    (210,210,210),           # white
    (10,10,10),              # black
    (255,0,0),               # red
    (0,0,255),               # blue
    (0,255,0),               # green
    (52,237,250),            # cyan
    (255,255,69),            # yellow
    (255,192,74),            # orange
    (168,127,56),            # brown
    (209,117,206)            # purple
    ]

  @staticmethod
  def get_screen_size():
    display = pygame.display.get_surface()
    
    return display.get_size() if display != None else (0,0)

  #----------------------------------------------------------------------------

  @staticmethod  
  def get_map_render_position(): 
    screen_size = RendererUtils.get_screen_size()
    return ((screen_size[0] - MapConfig.MAP_BORDER_WIDTH * 2 - MapConfig.MAP_TILE_WIDTH * MapConfig.MAP_WIDTH) / 2,(screen_size[1] - MapConfig.MAP_BORDER_WIDTH * 2 - MapConfig.MAP_TILE_HEIGHT * MapConfig.MAP_HEIGHT - 50) / 2)  

  #----------------------------------------------------------------------------
    
  @staticmethod
  def map_position_to_pixel_position(map_position, offset = (0,0)):
    map_render_location = RendererUtils.get_map_render_position()
    return (map_render_location[0] + int(map_position[0] * MapConfig.MAP_TILE_WIDTH) + MapConfig.MAP_BORDER_WIDTH + offset[0],map_render_location[1] + int(map_position[1] *MapConfig.MAP_TILE_HEIGHT) + MapConfig.MAP_BORDER_WIDTH + offset[1])
 
   ## Converts (r,g,b) tuple to html #rrggbb notation.

  #----------------------------------------------------------------------------

  @staticmethod
  def darken_color(color, by_how_may):
    r = max(color[0] - by_how_may,0)
    g = max(color[1] - by_how_may,0)
    b = max(color[2] - by_how_may,0)
    return (r,g,b)

  #----------------------------------------------------------------------------

  @staticmethod
  def lighten_color(color, by_how_may):
    r = min(color[0] + by_how_may,255)
    g = min(color[1] + by_how_may,255)
    b = min(color[2] + by_how_may,255)
    return (r,g,b)

  @staticmethod
  def rgb_to_html_notation(rgb_color):
    return "#" + hex(rgb_color[0])[2:].zfill(2) + hex(rgb_color[1])[2:].zfill(2) + hex(rgb_color[2])[2:].zfill(2)

  #----------------------------------------------------------------------------
     
  @staticmethod
  def colored_text(color_index, text, end_with_white=True):
    return "^" + RendererUtils.rgb_to_html_notation(RendererUtils.lighten_color(RendererUtils.COLOR_RGB_VALUES[color_index],75)) + text + "^#FFFFFF"

  #----------------------------------------------------------------------------

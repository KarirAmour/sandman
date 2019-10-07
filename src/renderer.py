import pygame
import os

from config import RESOURCE_PATH
from gamemap import GameMap

class Renderer(object):
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
    
  MAP_TILE_WIDTH = 50              ##< tile width in pixels
  MAP_TILE_HEIGHT = 45             ##< tile height in pixels
  MAP_TILE_HALF_WIDTH = MAP_TILE_WIDTH / 2
  MAP_TILE_HALF_HEIGHT = MAP_TILE_HEIGHT / 2

  PLAYER_SPRITE_CENTER = (30,80)   ##< player's feet (not geometrical) center of the sprite in pixels
  BOMB_SPRITE_CENTER = (22,33)
  SHADOW_SPRITE_CENTER = (25,22)

  MAP_BORDER_WIDTH = 37
  
  ANIMATION_EVENT_EXPLOSION = 0
  ANIMATION_EVENT_RIP = 1
  ANIMATION_EVENT_SKELETION = 2
  ANIMATION_EVENT_DISEASE_CLOUD = 3
  ANIMATION_EVENT_DIE = 4
  
  FONT_SMALL_SIZE = 12
  FONT_NORMAL_SIZE = 25
  MENU_LINE_SPACING = 10
  MENU_FONT_COLOR = (255,255,255)
  
  SCROLLBAR_RELATIVE_POSITION = (-200,-50)
  SCROLLBAR_HEIGHT = 300
  
  MENU_DESCRIPTION_Y_OFFSET = -80

  #----------------------------------------------------------------------------

  def __init__(self):
    self.update_screen_info()

    self.environment_images = {}
    
    self.preview_map_name = ""
    self.preview_map_image = None

    self.font_small = pygame.font.Font(os.path.join(RESOURCE_PATH,"LibertySans.ttf"),Renderer.FONT_SMALL_SIZE)
    self.font_normal = pygame.font.Font(os.path.join(RESOURCE_PATH,"LibertySans.ttf"),Renderer.FONT_NORMAL_SIZE)

    self.previous_mouse_coordinates = (-1,-1)

    pygame.mouse.set_visible(False)    # hide mouse cursor

    environment_names = ["env1","env2","env3","env4","env5","env6","env7"]

    for environment_name in environment_names:
      filename_floor = os.path.join(RESOURCE_PATH,"tile_" + environment_name + "_floor.png")
      filename_block = os.path.join(RESOURCE_PATH,"tile_" + environment_name + "_block.png")
      filename_wall = os.path.join(RESOURCE_PATH,"tile_" + environment_name + "_wall.png")

      self.environment_images[environment_name] = (pygame.image.load(filename_floor),pygame.image.load(filename_block),pygame.image.load(filename_wall))

    self.prerendered_map = None     # keeps a reference to a map for which some parts have been prerendered
    self.prerendered_map_background = pygame.Surface((GameMap.MAP_WIDTH * Renderer.MAP_TILE_WIDTH + 2 * Renderer.MAP_BORDER_WIDTH,GameMap.MAP_HEIGHT * Renderer.MAP_TILE_HEIGHT + 2 * Renderer.MAP_BORDER_WIDTH))

    self.player_images = []         ##< player images in format [color index]["sprite name"] and [color index]["sprite name"][frame]

    for i in range(10):
      self.player_images.append({})
      
      for helper_string in ["up","right","down","left"]:
        self.player_images[-1][helper_string] =  self.color_surface(pygame.image.load(os.path.join(RESOURCE_PATH,"player_" + helper_string + ".png")),i)
        
        string_index = "walk " + helper_string
      
        self.player_images[-1][string_index] = []
        self.player_images[-1][string_index].append(self.color_surface(pygame.image.load(os.path.join(RESOURCE_PATH,"player_" + helper_string + "_walk1.png")),i))
        
        if helper_string == "up" or helper_string == "down":
          self.player_images[-1][string_index].append(self.color_surface(pygame.image.load(os.path.join(RESOURCE_PATH,"player_" + helper_string + "_walk2.png")),i))
        else:
          self.player_images[-1][string_index].append(self.player_images[-1][helper_string])
        
        self.player_images[-1][string_index].append(self.color_surface(pygame.image.load(os.path.join(RESOURCE_PATH,"player_" + helper_string + "_walk3.png")),i))
        self.player_images[-1][string_index].append(self.player_images[-1][string_index][0])
        
        string_index = "box " + helper_string
        self.player_images[-1][string_index] = self.color_surface(pygame.image.load(os.path.join(RESOURCE_PATH,"player_" + helper_string + "_box.png")),i)
     
    self.bomb_images = []
    self.bomb_images.append(pygame.image.load(os.path.join(RESOURCE_PATH,"bomb1.png")))
    self.bomb_images.append(pygame.image.load(os.path.join(RESOURCE_PATH,"bomb2.png")))
    self.bomb_images.append(pygame.image.load(os.path.join(RESOURCE_PATH,"bomb3.png")))
    self.bomb_images.append(self.bomb_images[0])
     
    # load flame images
    
    self.flame_images = []
    
    for i in [1,2]:
      helper_string = "flame" + str(i)
      
      self.flame_images.append({})
      self.flame_images[-1]["all"] = pygame.image.load(os.path.join(RESOURCE_PATH,helper_string + ".png"))
      self.flame_images[-1]["horizontal"] = pygame.image.load(os.path.join(RESOURCE_PATH,helper_string + "_horizontal.png"))
      self.flame_images[-1]["vertical"] = pygame.image.load(os.path.join(RESOURCE_PATH,helper_string + "_vertical.png"))
      self.flame_images[-1]["left"] = pygame.image.load(os.path.join(RESOURCE_PATH,helper_string + "_left.png"))
      self.flame_images[-1]["right"] = pygame.image.load(os.path.join(RESOURCE_PATH,helper_string + "_right.png"))
      self.flame_images[-1]["up"] = pygame.image.load(os.path.join(RESOURCE_PATH,helper_string + "_up.png"))
      self.flame_images[-1]["down"] = pygame.image.load(os.path.join(RESOURCE_PATH,helper_string + "_down.png"))
      
    # load item images
    
    self.item_images = {}
    
    self.item_images[GameMap.ITEM_BOMB] = pygame.image.load(os.path.join(RESOURCE_PATH,"item_bomb.png"))
    self.item_images[GameMap.ITEM_FLAME] = pygame.image.load(os.path.join(RESOURCE_PATH,"item_flame.png"))
    self.item_images[GameMap.ITEM_SUPERFLAME] = pygame.image.load(os.path.join(RESOURCE_PATH,"item_superflame.png"))
    self.item_images[GameMap.ITEM_SPEEDUP] = pygame.image.load(os.path.join(RESOURCE_PATH,"item_speedup.png"))
    self.item_images[GameMap.ITEM_DISEASE] = pygame.image.load(os.path.join(RESOURCE_PATH,"item_disease.png"))
    self.item_images[GameMap.ITEM_RANDOM] = pygame.image.load(os.path.join(RESOURCE_PATH,"item_random.png"))
    self.item_images[GameMap.ITEM_SPRING] = pygame.image.load(os.path.join(RESOURCE_PATH,"item_spring.png"))
    self.item_images[GameMap.ITEM_SHOE] = pygame.image.load(os.path.join(RESOURCE_PATH,"item_shoe.png"))
    self.item_images[GameMap.ITEM_MULTIBOMB] = pygame.image.load(os.path.join(RESOURCE_PATH,"item_multibomb.png"))
    self.item_images[GameMap.ITEM_RANDOM] = pygame.image.load(os.path.join(RESOURCE_PATH,"item_random.png"))
    self.item_images[GameMap.ITEM_BOXING_GLOVE] = pygame.image.load(os.path.join(RESOURCE_PATH,"item_boxing_glove.png"))
    self.item_images[GameMap.ITEM_DETONATOR] = pygame.image.load(os.path.join(RESOURCE_PATH,"item_detonator.png"))
    self.item_images[GameMap.ITEM_THROWING_GLOVE] = pygame.image.load(os.path.join(RESOURCE_PATH,"item_throwing_glove.png"))
      
    # load/make gui images
    
    self.gui_images = {}
    self.gui_images["info board"] = pygame.image.load(os.path.join(RESOURCE_PATH,"gui_info_board.png"))   
    self.gui_images["arrow up"] = pygame.image.load(os.path.join(RESOURCE_PATH,"gui_arrow_up.png"))   
    self.gui_images["arrow down"] = pygame.image.load(os.path.join(RESOURCE_PATH,"gui_arrow_down.png"))   
    self.gui_images["seeker"] = pygame.image.load(os.path.join(RESOURCE_PATH,"gui_seeker.png"))
    self.gui_images["cursor"] = pygame.image.load(os.path.join(RESOURCE_PATH,"gui_cursor.png"))   
    self.gui_images["prompt"] = self.render_text(self.font_normal,"You sure?",(255,255,255))
    self.gui_images["version"] = self.render_text(self.font_small,"v " + Game.VERSION_STR,(0,100,0))
    
    self.player_info_board_images = [None for i in range(10)]  # up to date infoboard image for each player

    self.gui_images["out"] = pygame.image.load(os.path.join(RESOURCE_PATH,"gui_out.png"))   
     
    self.gui_images["countdown"] = {}
    
    self.gui_images["countdown"][1] = pygame.image.load(os.path.join(RESOURCE_PATH,"gui_countdown_1.png"))
    self.gui_images["countdown"][2] = pygame.image.load(os.path.join(RESOURCE_PATH,"gui_countdown_2.png"))
    self.gui_images["countdown"][3] = pygame.image.load(os.path.join(RESOURCE_PATH,"gui_countdown_3.png"))
    
    self.menu_background_image = None  ##< only loaded when in menu
    self.menu_item_images = None       ##< images of menu items, only loaded when in menu
 
    # load other images
    
    self.other_images = {}
    
    self.other_images["shadow"] = pygame.image.load(os.path.join(RESOURCE_PATH,"other_shadow.png"))
    self.other_images["spring"] = pygame.image.load(os.path.join(RESOURCE_PATH,"other_spring.png"))
    self.other_images["antena"] = pygame.image.load(os.path.join(RESOURCE_PATH,"other_antena.png"))
     
    self.other_images["disease"] = []
    self.other_images["disease"].append(pygame.image.load(os.path.join(RESOURCE_PATH,"other_disease1.png")))
    self.other_images["disease"].append(pygame.image.load(os.path.join(RESOURCE_PATH,"other_disease2.png")))    
          
    # load icon images
    
    self.icon_images = {}
    self.icon_images[GameMap.ITEM_BOMB] = pygame.image.load(os.path.join(RESOURCE_PATH,"icon_bomb.png"))
    self.icon_images[GameMap.ITEM_FLAME] = pygame.image.load(os.path.join(RESOURCE_PATH,"icon_flame.png"))
    self.icon_images[GameMap.ITEM_SPEEDUP] = pygame.image.load(os.path.join(RESOURCE_PATH,"icon_speedup.png"))
    self.icon_images[GameMap.ITEM_SHOE] = pygame.image.load(os.path.join(RESOURCE_PATH,"icon_kicking_shoe.png"))
    self.icon_images[GameMap.ITEM_BOXING_GLOVE] = pygame.image.load(os.path.join(RESOURCE_PATH,"icon_boxing_glove.png"))
    self.icon_images[GameMap.ITEM_THROWING_GLOVE] = pygame.image.load(os.path.join(RESOURCE_PATH,"icon_throwing_glove.png"))
    self.icon_images[GameMap.ITEM_SPRING] = pygame.image.load(os.path.join(RESOURCE_PATH,"icon_spring.png"))
    self.icon_images[GameMap.ITEM_MULTIBOMB] = pygame.image.load(os.path.join(RESOURCE_PATH,"icon_multibomb.png"))
    self.icon_images[GameMap.ITEM_DISEASE] = pygame.image.load(os.path.join(RESOURCE_PATH,"icon_disease.png"))
    self.icon_images[GameMap.ITEM_DETONATOR] = pygame.image.load(os.path.join(RESOURCE_PATH,"icon_detonator.png"))
    self.icon_images["etc"] = pygame.image.load(os.path.join(RESOURCE_PATH,"icon_etc.png"))
    
    # load animations
    
    self.animations = {}
    self.animations[Renderer.ANIMATION_EVENT_EXPLOSION] = Animation(os.path.join(RESOURCE_PATH,"animation_explosion"),1,10,".png",7)
    self.animations[Renderer.ANIMATION_EVENT_RIP] = Animation(os.path.join(RESOURCE_PATH,"animation_rip"),1,1,".png",0.3)
    self.animations[Renderer.ANIMATION_EVENT_SKELETION] = Animation(os.path.join(RESOURCE_PATH,"animation_skeleton"),1,10,".png",7)
    self.animations[Renderer.ANIMATION_EVENT_DISEASE_CLOUD] = Animation(os.path.join(RESOURCE_PATH,"animation_disease"),1,6,".png",5)
    self.animations[Renderer.ANIMATION_EVENT_DIE] = Animation(os.path.join(RESOURCE_PATH,"animation_die"),1,7,".png",7)

    self.party_circles = []     ##< holds info about party cheat circles, list of tuples in format (coords,radius,color,phase,speed)
    self.party_circles.append(((-180,110),40,(255,100,50),0.0,1.0))
    self.party_circles.append(((160,70),32,(100,200,150),1.4,1.5))
    self.party_circles.append(((40,-150),65,(150,100,170),2.0,0.7))
    self.party_circles.append(((-170,-92),80,(200,200,32),3.2,1.3))
    self.party_circles.append(((50,110),63,(10,180,230),0.1,1.8))
    self.party_circles.append(((205,-130),72,(180,150,190),0.5,2.0))
    
    self.party_players = []     ##< holds info about party cheat players, list of tuples in format (coords,color index,millisecond delay, rotate right)
    self.party_players.append(((-230,80),0,0,True))
    self.party_players.append(((180,10),2,220,False))
    self.party_players.append(((90,-150),4,880,True))
    self.party_players.append(((-190,-95),6,320,False))
    self.party_players.append(((-40,110),8,50,True))
    
    self.party_bombs = []       ##< holds info about party bombs, list of lists in format [x,y,increment x,increment y]
    self.party_bombs.append([10,30,1,1])
    self.party_bombs.append([700,200,1,-1])
    self.party_bombs.append([512,512,-1,1])
    self.party_bombs.append([1024,20,-1,-1])
    self.party_bombs.append([900,300,1,1])
    self.party_bombs.append([30,700,1,1])
    self.party_bombs.append([405,530,1,-1])
    self.party_bombs.append([250,130,-1,-1])

  #----------------------------------------------------------------------------

  def update_screen_info(self):
    self.screen_resolution = Renderer.get_screen_size()
    self.screen_center = (self.screen_resolution[0] / 2,self.screen_resolution[1] / 2)
    self.map_render_location = Renderer.get_map_render_position()

  #----------------------------------------------------------------------------
  
  ## Converts (r,g,b) tuple to html #rrggbb notation.

  @staticmethod
  def rgb_to_html_notation(rgb_color):
    return "#" + hex(rgb_color[0])[2:].zfill(2) + hex(rgb_color[1])[2:].zfill(2) + hex(rgb_color[2])[2:].zfill(2)

  #----------------------------------------------------------------------------
     
  @staticmethod
  def colored_text(color_index, text, end_with_white=True):
    return "^" + Renderer.rgb_to_html_notation(Renderer.lighten_color(Renderer.COLOR_RGB_VALUES[color_index],75)) + text + "^#FFFFFF"

  #----------------------------------------------------------------------------
    
  @staticmethod
  def colored_color_name(color_index, end_with_white=True):
    return Renderer.colored_text(color_index,Game.COLOR_NAMES[color_index])

  #----------------------------------------------------------------------------
  
  ## Returns colored image from another image (replaces red color with given color). This method is slow. Color is (r,g,b) tuple of 0 - 1 floats.

  def color_surface(self, surface, color_number):
    result = surface.copy()
    
    # change all red pixels to specified color
    for j in range(result.get_size()[1]):
      for i in range(result.get_size()[0]):
        pixel_color = result.get_at((i,j))
        
        if pixel_color.r == 255 and pixel_color.g == 0 and pixel_color.b == 0:
          pixel_color.r = Renderer.COLOR_RGB_VALUES[color_number][0]
          pixel_color.g = Renderer.COLOR_RGB_VALUES[color_number][1]
          pixel_color.b = Renderer.COLOR_RGB_VALUES[color_number][2]
          result.set_at((i,j),pixel_color)

    return result

  #----------------------------------------------------------------------------

  def tile_position_to_pixel_position(self, tile_position,center=(0,0)):
    return (int(float(tile_position[0]) * Renderer.MAP_TILE_WIDTH) - center[0],int(float(tile_position[1]) * Renderer.MAP_TILE_HEIGHT) - center[1])

  #----------------------------------------------------------------------------

  @staticmethod
  def get_screen_size():
    display = pygame.display.get_surface()
    
    return display.get_size() if display != None else (0,0)

  #----------------------------------------------------------------------------

  @staticmethod  
  def get_map_render_position(): 
    screen_size = Renderer.get_screen_size()
    return ((screen_size[0] - Renderer.MAP_BORDER_WIDTH * 2 - Renderer.MAP_TILE_WIDTH * GameMap.MAP_WIDTH) / 2,(screen_size[1] - Renderer.MAP_BORDER_WIDTH * 2 - Renderer.MAP_TILE_HEIGHT * GameMap.MAP_HEIGHT - 50) / 2)  

  #----------------------------------------------------------------------------
    
  @staticmethod
  def map_position_to_pixel_position(map_position, offset = (0,0)):
    map_render_location = Renderer.get_map_render_position()
    return (map_render_location[0] + int(map_position[0] * Renderer.MAP_TILE_WIDTH) + Renderer.MAP_BORDER_WIDTH + offset[0],map_render_location[1] + int(map_position[1] * Renderer.MAP_TILE_HEIGHT) + Renderer.MAP_BORDER_WIDTH + offset[1])
    
  def set_resolution(self, new_resolution):
    self.screen_resolution = new_resolution

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

  #----------------------------------------------------------------------------

  def __render_info_board_item_row(self, x, y, limit, item_type, player, board_image):   
    item_count = 20 if item_type == GameMap.ITEM_FLAME and player.get_item_count(GameMap.ITEM_SUPERFLAME) >= 1 else player.get_item_count(item_type)
   
    for i in range(item_count):
      if i > limit:
        break
        
      image_to_draw = self.icon_images[item_type]
        
      if i == limit and player.get_item_count(item_type) > limit + 1:
        image_to_draw = self.icon_images["etc"]
        
      board_image.blit(image_to_draw,(x,y))
      x += self.icon_images[item_type].get_size()[0]    

  #----------------------------------------------------------------------------

  ## Updates info board images in self.player_info_board_images. This should be called each frame, as
  #  rerendering is done only when needed.

  def update_info_boards(self, players):
    for i in range(10):      # for each player number
      update_needed = False
      
      if self.player_info_board_images[i] == None:
        self.player_info_board_images[i] = self.gui_images["info board"].copy()
        update_needed = True
      
      player = None
      
      for one_player in players:
        if one_player.get_number() == i:
          player = one_player
          break
      
      if player == None:
        continue
      
      if player.info_board_needs_update():
        update_needed = True
      
      if not update_needed or player == None:
        continue
      
      # rerendering needed here
      
      debug_log("updating info board " + str(i))
      
      board_image = self.player_info_board_images[i]
      
      board_image.blit(self.gui_images["info board"],(0,0))
      board_image.blit(self.font_small.render(str(player.get_kills()),True,(0,0,0)),(45,0))
      board_image.blit(self.font_small.render(str(player.get_wins()),True,(0,0,0)),(65,0))
      board_image.blit(self.font_small.render(Game.COLOR_NAMES[i],True,Renderer.darken_color(Renderer.COLOR_RGB_VALUES[i],100)),(4,2))
      
      if player.is_dead():
        board_image.blit(self.gui_images["out"],(15,34))
        continue
      
      # render items

      x = 5
      dy = 12

      self.__render_info_board_item_row(x,20,5,GameMap.ITEM_BOMB,player,board_image)
      self.__render_info_board_item_row(x,20 + dy,5,GameMap.ITEM_FLAME,player,board_image)
      self.__render_info_board_item_row(x,20 + 2 * dy,9,GameMap.ITEM_SPEEDUP,player,board_image)

      y = 20 + 3 * dy

      items_to_check = [
        GameMap.ITEM_SHOE,
        GameMap.ITEM_BOXING_GLOVE,
        GameMap.ITEM_THROWING_GLOVE,
        GameMap.ITEM_SPRING,
        GameMap.ITEM_MULTIBOMB,
        GameMap.ITEM_DETONATOR,
        GameMap.ITEM_DISEASE]
      
      for item in items_to_check:
        if player.get_item_count(item) or item == GameMap.ITEM_DISEASE and player.get_disease() != Player.DISEASE_NONE:
          board_image.blit(self.icon_images[item],(x,y))
          x += self.icon_images[item].get_size()[0] + 1
 
  #----------------------------------------------------------------------------

  def process_animation_events(self, animation_event_list):
    for animation_event in animation_event_list:
      self.animations[animation_event[0]].play(animation_event[1])

  #----------------------------------------------------------------------------

  ## Renders text with outline, line breaks, formatting, etc.

  def render_text(self, font, text_to_render, color, outline_color = (0,0,0), center = False):
    text_lines = text_to_render.split("\n")
    rendered_lines = []
    
    width = height = 0
    
    first_line = True
    
    for text_line in text_lines:
      line = text_line.lstrip().rstrip()
      
      if len(line) == 0:
        continue
      
      line_without_format = re.sub(r"\^.......","",line)     # remove all the markup in format ^#dddddd

      new_rendered_line = pygame.Surface(font.size(line_without_format),flags=pygame.SRCALPHA)
      
      x = 0
      first = True
      starts_with_format = line[0] == "^"
 
      for subline in line.split("^"):
        if len(subline) == 0:
          continue
        
        has_format = starts_with_format if first else True
        first = False

        text_color = color
        
        if has_format:
          text_color = pygame.Color(subline[:7])
          subline = subline[7:]
        
        new_rendered_subline = font.render(subline,True,outline_color)   # create text with outline
        new_rendered_subline.blit(new_rendered_subline,(0,2))
        new_rendered_subline.blit(new_rendered_subline,(1,0))
        new_rendered_subline.blit(new_rendered_subline,(-1,0))
        new_rendered_subline.blit(font.render(subline,True,text_color),(0,1))      
        
        new_rendered_line.blit(new_rendered_subline,(x,0))
        
        x += new_rendered_subline.get_size()[0]
        
      rendered_lines.append(new_rendered_line)

      if not first_line:
        height += Renderer.MENU_LINE_SPACING
      
      first_line = False

      height += rendered_lines[-1].get_size()[1]
      width = max(width,rendered_lines[-1].get_size()[0])
    
    result = pygame.Surface((width,height),flags=pygame.SRCALPHA)
    
    y_step = font.get_height() + Renderer.MENU_LINE_SPACING
    
    for i in range(len(rendered_lines)):
      result.blit(rendered_lines[i],(0 if not center else (width - rendered_lines[i].get_size()[0]) / 2,i * y_step))
    
    return result

  #----------------------------------------------------------------------------

  ## Updates images in self.menu_item_images (only if needed).

  def update_menu_item_images(self, menu):
    if self.menu_item_images == None:
      self.menu_item_images = {}       # format: (row, column) : (item text, image)
    
    items = menu.get_items()

    item_coordinates = []
    
    for j in range(len(items)):
      for i in range(len(items[j])):
        item_coordinates.append((j,i))
    
    if len(menu.get_text()) != 0:
      item_coordinates.append(0)       # this is the menu description text

    for menu_coordinates in item_coordinates:
      update_needed = False
        
      if not (menu_coordinates in self.menu_item_images):
        update_needed = True
    
      if menu_coordinates == 0:
        item_text = menu.get_text()
        center_text = True
      else:
        item_text = items[menu_coordinates[0]][menu_coordinates[1]]
        center_text = False
      
      if not update_needed and item_text != self.menu_item_images[menu_coordinates][0]:
        update_needed = True        
          
      if update_needed:
        debug_log("updating menu item " + str(menu_coordinates))
          
        new_image = self.render_text(self.font_normal,item_text,Renderer.MENU_FONT_COLOR,center = center_text)
          
        # text itself
        new_image.blit(new_image,(0,1))
          
        self.menu_item_images[menu_coordinates] = (item_text,new_image)

  #----------------------------------------------------------------------------
    
  def render_menu(self, menu_to_render, game):
    result = pygame.Surface(self.screen_resolution)
    
    if self.menu_background_image == None:
      self.menu_background_image = pygame.image.load(os.path.join(RESOURCE_PATH,"gui_menu_background.png"))

    background_position = (self.screen_center[0] - self.menu_background_image.get_size()[0] / 2,self.screen_center[1] - self.menu_background_image.get_size()[1] / 2)
      
    profiler.measure_start("menu rend. backg.")
    result.blit(self.menu_background_image,background_position)
    profiler.measure_stop("menu rend. backg.")

    profiler.measure_start("menu rend. party")
    if game.cheat_is_active(Game.CHEAT_PARTY):
      for circle_info in self.party_circles:           # draw circles
        circle_coords = (self.screen_center[0] + circle_info[0][0],self.screen_center[1] + circle_info[0][1])     
        radius_coefficient = (math.sin(pygame.time.get_ticks() * circle_info[4] / 100.0 + circle_info[3]) + 1) / 2.0
        circle_radius = int(circle_info[1] * radius_coefficient)
        pygame.draw.circle(result,circle_info[2],circle_coords,circle_radius)
    
      for player_info in self.party_players:           # draw players
        player_coords = (self.screen_center[0] + player_info[0][0],self.screen_center[1] + player_info[0][1])     
        
        player_direction = (int((pygame.time.get_ticks() + player_info[2]) / 150)) % 4
        
        if not player_info[3]:
          player_direction = 3 - player_direction
        
        direction_string = ("up","right","down","left")[player_direction]
        
        if int(pygame.time.get_ticks() / 500) % 2 == 0:
          direction_string = "box " + direction_string
        
        result.blit(self.player_images[player_info[1]][direction_string],player_coords)
    
      for bomb_info in self.party_bombs:
        result.blit(self.bomb_images[0],(bomb_info[0],bomb_info[1]))
        bomb_info[0] += bomb_info[2]
        bomb_info[1] += bomb_info[3]
        
        if bomb_info[0] < 0:     # border collision, change direction
          bomb_info[2] = 1
        elif bomb_info[0] > self.screen_resolution[0] - 50:
          bomb_info[2] = -1
    
        if bomb_info[1] < 0:     # border collision, change direction
          bomb_info[3] = 1
        elif bomb_info[1] > self.screen_resolution[1] - 50:
          bomb_info[3] = -1
    
    profiler.measure_stop("menu rend. party")
    
    version_position = (3,1)
    
    result.blit(self.gui_images["version"],version_position)
    
    profiler.measure_start("menu rend. item update")
    self.update_menu_item_images(menu_to_render)
    
    # render menu description text
    
    y = self.screen_center[1] + Renderer.MENU_DESCRIPTION_Y_OFFSET
    
    if len(menu_to_render.get_text()) != 0:
      result.blit(self.menu_item_images[0][1],(self.screen_center[0] - self.menu_item_images[0][1].get_size()[0] / 2,y))    # menu description text image is at index 0      
      y += self.menu_item_images[0][1].get_size()[1] + Renderer.MENU_LINE_SPACING * 2
    
    menu_items = menu_to_render.get_items()
    
    columns = len(menu_items)   # how many columns there are
    
    column_x_space = 150
    
    if columns % 2 == 0:
      xs = [self.screen_center[0] + i * column_x_space - ((columns - 1) * column_x_space / 2) for i in range(columns)] # even number of columns
    else:
      xs = [self.screen_center[0] + (i - columns / 2) * column_x_space for i in range(columns)]
    
    selected_coordinates = menu_to_render.get_selected_item()
    
    items_y = y
    
    profiler.measure_stop("menu rend. item update")
    
    # render scrollbar if needed
    
    rows = 0
    
    for column in menu_items:
      rows = max(rows,len(column))

    if rows > Menu.MENU_MAX_ITEMS_VISIBLE:
      x = xs[0] + Renderer.SCROLLBAR_RELATIVE_POSITION[0]
      
      result.blit(self.gui_images["arrow up"],(x,items_y))
      result.blit(self.gui_images["arrow down"],(x,items_y + Renderer.SCROLLBAR_HEIGHT))
      
      scrollbar_position = int(items_y + selected_coordinates[0] / float(rows) * Renderer.SCROLLBAR_HEIGHT)
      result.blit(self.gui_images["seeker"],(x,scrollbar_position))
    
    mouse_coordinates = pygame.mouse.get_pos()
    
    # render items
    
    profiler.measure_start("menu rend. items")
    
    for j in range(len(menu_items)):
      y = items_y
      
      for i in range(min(Menu.MENU_MAX_ITEMS_VISIBLE,len(menu_items[j]) - menu_to_render.get_scroll_position())):
        item_image = self.menu_item_images[(j,i + menu_to_render.get_scroll_position())][1]

        x = xs[j] - item_image.get_size()[0] / 2
                
        if (i + menu_to_render.get_scroll_position(),j) == selected_coordinates:
          # item is selected
          scale = (8 + math.sin(pygame.time.get_ticks() / 40.0)) / 7.0    # make the pulsating effect
          item_image = pygame.transform.scale(item_image,(int(scale * item_image.get_size()[0]),int(scale * item_image.get_size()[1])))
          x = xs[j] - item_image.get_size()[0] / 2
          pygame.draw.rect(result,(255,0,0),pygame.Rect(x - 4,y - 2,item_image.get_size()[0] + 8,item_image.get_size()[1] + 4))
        
        result.blit(item_image,(x,y))
        
        # did mouse go over the item?
        
        if (not game.get_settings().control_by_mouse) and (self.previous_mouse_coordinates != mouse_coordinates) and (x <= mouse_coordinates[0] <= x + item_image.get_size()[0]) and (y <= mouse_coordinates[1] <= y + item_image.get_size()[1]):
          item_coordinates = (i + menu_to_render.get_scroll_position(),j)
          menu_to_render.mouse_went_over_item(item_coordinates)
       
        y += Renderer.FONT_NORMAL_SIZE + Renderer.MENU_LINE_SPACING
    
    profiler.measure_stop("menu rend. items")
    
    mouse_events = game.get_player_key_maps().get_mouse_button_events()
    
    for i in range(len(mouse_events)):
      if mouse_events[i]:
        menu_to_render.mouse_button_pressed(i)
    
    self.previous_mouse_coordinates = mouse_coordinates
    
    # render confirm dialog if prompting
    
    if menu_to_render.get_state() == Menu.MENU_STATE_CONFIRM_PROMPT:
      width = 120
      height = 80
      x = self.screen_center[0] - width / 2
      y = self.screen_center[1] - height / 2
      
      pygame.draw.rect(result,(0,0,0),pygame.Rect(x,y,width,height))
      pygame.draw.rect(result,(255,255,255),pygame.Rect(x,y,width,height),1)
      
      text_image = pygame.transform.rotate(self.gui_images["prompt"],math.sin(pygame.time.get_ticks() / 100) * 5)
      
      x = self.screen_center[0] - text_image.get_size()[0] / 2
      y = self.screen_center[1] - text_image.get_size()[1] / 2
      
      result.blit(text_image,(x,y))
    
    # map preview
    
    profiler.measure_start("menu rend. preview")
    
    if isinstance(menu_to_render,MapSelectMenu):       # also not too nice    
      if menu_to_render.show_map_preview():
        self.update_map_preview_image(menu_to_render.get_selected_map_name())
        result.blit(self.preview_map_image,(self.screen_center[0] + 180,items_y))
    
    profiler.measure_stop("menu rend. preview")
    
    # draw cursor only if control by mouse is not allowed - wouldn't make sense
    
    if not game.get_settings().control_by_mouse:
      result.blit(self.gui_images["cursor"],pygame.mouse.get_pos())
    
    return result

  #----------------------------------------------------------------------------

  def update_map_preview_image(self, map_filename):
    if map_filename == "":
      self.preview_map_name = ""
      self.preview_map_image = None
      return
    
    if self.preview_map_name != map_filename:
      debug_log("updating map preview of " + map_filename)
      
      self.preview_map_name = map_filename
      
      tile_size = 7
      tile_half_size = tile_size / 2
    
      map_info_border_size = 5
    
      self.preview_map_image = pygame.Surface((tile_size * GameMap.MAP_WIDTH,tile_size * GameMap.MAP_HEIGHT + map_info_border_size + Renderer.MAP_TILE_HEIGHT))
    
      with open(os.path.join(Game.MAP_PATH,map_filename)) as map_file:
        map_data = map_file.read()
        temp_map = GameMap(map_data,PlaySetup(),0,0)
        
        for y in range(GameMap.MAP_HEIGHT):
          for x in range(GameMap.MAP_WIDTH):
            tile = temp_map.get_tile_at((x,y))
            tile_kind = tile.kind
            
            pos_x = x * tile_size
            pos_y = y * tile_size
            
            tile_special_object = tile.special_object
            
            if tile_special_object == None: 
              if tile_kind == MapTile.TILE_BLOCK:
                tile_color = (120,120,120)
              elif tile_kind == MapTile.TILE_WALL:
                tile_color = (60,60,60)
              else:                                            # floor
                tile_color = (230,230,230)
            else:
              if tile_special_object == MapTile.SPECIAL_OBJECT_LAVA:
                tile_color = (200,0,0)
              elif tile_special_object == MapTile.SPECIAL_OBJECT_TELEPORT_A or tile_special_object == MapTile.SPECIAL_OBJECT_TELEPORT_B:
                tile_color = (0,0,200)
              elif tile_special_object == MapTile.SPECIAL_OBJECT_TRAMPOLINE:
                tile_color = (0,200,0)
              elif tile_kind == MapTile.TILE_FLOOR:           # arrow
                tile_color = (200,200,0)
              else:
                tile_color = (230,230,230)
            
            pygame.draw.rect(self.preview_map_image,tile_color,pygame.Rect(pos_x,pos_y,tile_size,tile_size))

        starting_positions = temp_map.get_starting_positions()

        for player_index in range(len(starting_positions)):
          draw_position = (int(starting_positions[player_index][0]) * tile_size + tile_half_size,int(starting_positions[player_index][1]) * tile_size + tile_half_size)
           
          pygame.draw.rect(self.preview_map_image,tile_color,pygame.Rect(pos_x,pos_y,tile_size,tile_size))
          pygame.draw.circle(self.preview_map_image,Renderer.COLOR_RGB_VALUES[player_index],draw_position,tile_half_size)

        y = tile_size * GameMap.MAP_HEIGHT + map_info_border_size
        column = 0

        self.preview_map_image.blit(self.environment_images[temp_map.get_environment_name()][0],(0,y))

        # draw starting item icons

        starting_x = Renderer.MAP_TILE_WIDTH + 5

        x = starting_x
        
        pygame.draw.rect(self.preview_map_image,(255,255,255),pygame.Rect(x,y,Renderer.MAP_TILE_WIDTH,Renderer.MAP_TILE_HEIGHT))

        starting_items = temp_map.get_starting_items()
        
        for i in range(len(starting_items)):
          item = starting_items[i]
          
          if item in self.icon_images:
            item_image = self.icon_images[item]
            
            self.preview_map_image.blit(item_image,(x + 1,y + 1))
            
            x += item_image.get_size()[0] + 1
            column += 1
            
            if column > 2:
              column = 0
              x = starting_x
              y += 12

  #----------------------------------------------------------------------------

  def __prerender_map(self, map_to_render):
    self.animation_events = []                  # clear previous animation

    debug_log("prerendering map...")

    # following images are only needed here, so we dont store them to self
    image_trampoline = pygame.image.load(os.path.join(RESOURCE_PATH,"other_trampoline.png"))
    image_teleport = pygame.image.load(os.path.join(RESOURCE_PATH,"other_teleport.png"))
    image_arrow_up = pygame.image.load(os.path.join(RESOURCE_PATH,"other_arrow_up.png"))
    image_arrow_right = pygame.image.load(os.path.join(RESOURCE_PATH,"other_arrow_right.png"))
    image_arrow_down = pygame.image.load(os.path.join(RESOURCE_PATH,"other_arrow_down.png"))
    image_arrow_left = pygame.image.load(os.path.join(RESOURCE_PATH,"other_arrow_left.png"))
    image_lava = pygame.image.load(os.path.join(RESOURCE_PATH,"other_lava.png"))
    image_background = pygame.image.load(os.path.join(RESOURCE_PATH,"other_map_background.png"))

    self.prerendered_map_background.blit(image_background,(0,0))

    for j in range(GameMap.MAP_HEIGHT):
      for i in range(GameMap.MAP_WIDTH):
        render_position = (i * Renderer.MAP_TILE_WIDTH + Renderer.MAP_BORDER_WIDTH,j * Renderer.MAP_TILE_HEIGHT + + Renderer.MAP_BORDER_WIDTH)          
        self.prerendered_map_background.blit(self.environment_images[map_to_render.get_environment_name()][0],render_position)
       
        tile = map_to_render.get_tile_at((i,j))
          
        helper_mapping = {
            MapTile.SPECIAL_OBJECT_TELEPORT_A: image_teleport,
            MapTile.SPECIAL_OBJECT_TELEPORT_B: image_teleport,
            MapTile.SPECIAL_OBJECT_TRAMPOLINE: image_trampoline,
            MapTile.SPECIAL_OBJECT_ARROW_UP: image_arrow_up,
            MapTile.SPECIAL_OBJECT_ARROW_RIGHT: image_arrow_right,
            MapTile.SPECIAL_OBJECT_ARROW_DOWN: image_arrow_down,
            MapTile.SPECIAL_OBJECT_ARROW_LEFT: image_arrow_left,
            MapTile.SPECIAL_OBJECT_LAVA: image_lava
          }

        if tile.special_object in helper_mapping:
          self.prerendered_map_background.blit(helper_mapping[tile.special_object],render_position)
    
    game_info = map_to_render.get_game_number_info()    
      
    game_info_text = self.render_text(self.font_small,"game " + str(game_info[0]) + " of " + str(game_info[1]),(255,255,255))

    self.prerendered_map_background.blit(game_info_text,((self.prerendered_map_background.get_size()[0] - game_info_text.get_size()[0]) / 2,self.prerendered_map_background.get_size()[1] - game_info_text.get_size()[1]))

    self.prerendered_map = map_to_render

  #----------------------------------------------------------------------------

  ##< Gets an info about how given player whould be rendered in format (image to render, sprite center, relative pixel offset, draw_shadow, overlay images).

  def __get_player_render_info(self, player, game_map):
    profiler.measure_start("map rend. player")

    draw_shadow = True
    relative_offset = [0,0]
    overlay_images = []

    if player.is_dead():
      profiler.measure_stop("map rend. player")
      return (None, (0,0), (0,0), False, [])
        
    sprite_center = Renderer.PLAYER_SPRITE_CENTER
    animation_frame = (player.get_state_time() / 100) % 4
    color_index = player.get_number() if game_map.get_state() == GameMap.STATE_WAITING_TO_PLAY else player.get_team_number()

    if player.is_in_air():
      if player.get_state_time() < Player.JUMP_DURATION / 2:
        quotient = abs(player.get_state_time() / float(Player.JUMP_DURATION / 2))
      else:
        quotient = 2.0 - abs(player.get_state_time() / float(Player.JUMP_DURATION / 2))
              
      scale = (1 + 0.5 * quotient)
              
      player_image = self.player_images[color_index]["down"]
      image_to_render = pygame.transform.scale(player_image,(int(scale * player_image.get_size()[0]),int(scale * player_image.get_size()[1])))
      draw_shadow = False
              
      relative_offset[0] = -1 * (image_to_render.get_size()[0] / 2 - Renderer.PLAYER_SPRITE_CENTER[0])                   # offset caused by scale  
      relative_offset[1] = -1 * int(math.sin(quotient * math.pi / 2.0) * Renderer.MAP_TILE_HEIGHT * GameMap.MAP_HEIGHT)  # height offset

    elif player.is_teleporting():
      image_to_render = self.player_images[color_index][("up","right","down","left")[animation_frame]]

    elif player.is_boxing() or player.is_throwing():
      if not player.is_throwing() and animation_frame == 0:
        helper_string = ""
      else:
        helper_string = "box "

      helper_string += ("up","right","down","left")[player.get_direction_number()]

      image_to_render = self.player_images[color_index][helper_string]
    else:
      helper_string = ("up","right","down","left")[player.get_direction_number()]

      if player.is_walking():
        image_to_render = self.player_images[color_index]["walk " + helper_string][animation_frame]
      else:
        image_to_render = self.player_images[color_index][helper_string]

    if player.get_disease() != Player.DISEASE_NONE:
      overlay_images.append(self.other_images["disease"][animation_frame % 2]) 

    profiler.measure_stop("map rend. player") 

    return (image_to_render,sprite_center,relative_offset,draw_shadow,overlay_images)

  #----------------------------------------------------------------------------

  ##< Same as __get_player_render_info, but for bombs.

  def __get_bomb_render_info(self, bomb, game_map):
    profiler.measure_start("map rend. bomb")
    sprite_center = Renderer.BOMB_SPRITE_CENTER
    animation_frame = (bomb.time_of_existence / 100) % 4
    relative_offset = [0,0]   
    overlay_images = []      

    if bomb.has_detonator():
      overlay_images.append(self.other_images["antena"])
            
      if bomb.time_of_existence < Bomb.DETONATOR_EXPIRATION_TIME:
        animation_frame = 0                 # bomb won't pulse if within detonator expiration time

    if bomb.movement == Bomb.BOMB_FLYING:
      normalised_distance_travelled = bomb.flight_info.distance_travelled / float(bomb.flight_info.total_distance_to_travel)
            
      helper_offset = -1 * bomb.flight_info.total_distance_to_travel + bomb.flight_info.distance_travelled
            
      relative_offset = [
        int(bomb.flight_info.direction[0] * helper_offset * Renderer.MAP_TILE_WIDTH),
        int(bomb.flight_info.direction[1] * helper_offset * Renderer.MAP_TILE_HALF_HEIGHT)]

      relative_offset[1] -= int(math.sin(normalised_distance_travelled * math.pi) * bomb.flight_info.total_distance_to_travel * Renderer.MAP_TILE_HEIGHT / 2)  # height in air
          
    image_to_render = self.bomb_images[animation_frame]
          
    if bomb.has_spring:
      overlay_images.append(self.other_images["spring"])
        
    profiler.measure_stop("map rend. bomb")

    return (image_to_render,sprite_center,relative_offset,True,overlay_images)

  #----------------------------------------------------------------------------

  def render_map(self, map_to_render):
    result = pygame.Surface(self.screen_resolution)
    
    self.menu_background_image = None             # unload unneccessarry images
    self.menu_item_images = None
    self.preview_map_name = ""
    self.preview_map_image = None
    
    self.update_info_boards(map_to_render.get_players())
  
    if map_to_render != self.prerendered_map:     # first time rendering this map, prerender some stuff
      self.__prerender_map(map_to_render)

    profiler.measure_start("map rend. backg.")
    result.blit(self.prerendered_map_background,self.map_render_location)
    profiler.measure_stop("map rend. backg.")
    
    # order the players and bombs by their y position so that they are drawn correctly

    profiler.measure_start("map rend. sort")
    ordered_objects_to_render = []
    ordered_objects_to_render.extend(map_to_render.get_players())
    ordered_objects_to_render.extend(map_to_render.get_bombs())
    ordered_objects_to_render.sort(key = lambda what: 1000 if (isinstance(what,Bomb) and what.movement == Bomb.BOMB_FLYING) else what.get_position()[1])   # flying bombs are rendered above everything else
    profiler.measure_stop("map rend. sort")
    
    # render the map by lines:

    tiles = map_to_render.get_tiles()
    environment_images = self.environment_images[map_to_render.get_environment_name()]
    
    y = Renderer.MAP_BORDER_WIDTH + self.map_render_location[1]
    y_offset_block = Renderer.MAP_TILE_HEIGHT - environment_images[1].get_size()[1]
    y_offset_wall = Renderer.MAP_TILE_HEIGHT - environment_images[2].get_size()[1]
    
    line_number = 0
    object_to_render_index = 0
    
    flame_animation_frame = (pygame.time.get_ticks() / 100) % 2
    
    for line in tiles:
      x = (GameMap.MAP_WIDTH - 1) * Renderer.MAP_TILE_WIDTH + Renderer.MAP_BORDER_WIDTH + self.map_render_location[0]
      
      while True:                  # render players and bombs in the current line 
        if object_to_render_index >= len(ordered_objects_to_render):
          break
        
        object_to_render = ordered_objects_to_render[object_to_render_index]
        
        if object_to_render.get_position()[1] > line_number + 1:
          break
        
        if isinstance(object_to_render,Player):
          image_to_render, sprite_center, relative_offset, draw_shadow, overlay_images = self.__get_player_render_info(object_to_render, map_to_render)
        else:                                      # bomb
          image_to_render, sprite_center, relative_offset, draw_shadow, overlay_images = self.__get_bomb_render_info(object_to_render, map_to_render)
        
        if image_to_render == None:
          object_to_render_index += 1
          continue

        if draw_shadow:
          render_position = self.tile_position_to_pixel_position(object_to_render.get_position(),Renderer.SHADOW_SPRITE_CENTER)
          render_position = (
            (render_position[0] + Renderer.MAP_BORDER_WIDTH + relative_offset[0]) % self.prerendered_map_background.get_size()[0] + self.map_render_location[0],
            render_position[1] + Renderer.MAP_BORDER_WIDTH + self.map_render_location[1])

          result.blit(self.other_images["shadow"],render_position)
        
        render_position = self.tile_position_to_pixel_position(object_to_render.get_position(),sprite_center)
        render_position = ((render_position[0] + Renderer.MAP_BORDER_WIDTH + relative_offset[0]) % self.prerendered_map_background.get_size()[0] + self.map_render_location[0],render_position[1] + Renderer.MAP_BORDER_WIDTH + relative_offset[1] + self.map_render_location[1])
        
        result.blit(image_to_render,render_position)
        
        for additional_image in overlay_images:
          result.blit(additional_image,render_position)
      
        object_to_render_index += 1
            
      for tile in reversed(line):             # render tiles in the current line
        profiler.measure_start("map rend. tiles")
        
        if not tile.to_be_destroyed:          # don't render a tile that is being destroyed
          if tile.kind == MapTile.TILE_BLOCK:
            result.blit(environment_images[1],(x,y + y_offset_block))
          elif tile.kind == MapTile.TILE_WALL:
            result.blit(environment_images[2],(x,y + y_offset_wall))
          elif tile.item != None:
            result.blit(self.item_images[tile.item],(x,y))

        if len(tile.flames) != 0:             # if there is at least one flame, draw it
          sprite_name = tile.flames[0].direction
          result.blit(self.flame_images[flame_animation_frame][sprite_name],(x,y))

      # for debug: uncomment this to see danger values on the map
      # pygame.draw.rect(result,(int((1 - map_to_render.get_danger_value(tile.coordinates) / float(GameMap.SAFE_DANGER_VALUE)) * 255.0),0,0),pygame.Rect(x + 10,y + 10,30,30))

        x -= Renderer.MAP_TILE_WIDTH
  
        profiler.measure_stop("map rend. tiles")
  
      x = (GameMap.MAP_WIDTH - 1) * Renderer.MAP_TILE_WIDTH + Renderer.MAP_BORDER_WIDTH + self.map_render_location[0]
  
      y += Renderer.MAP_TILE_HEIGHT
      line_number += 1
      
    # update animations
    
    profiler.measure_start("map rend. anim")
    
    for animation_index in self.animations:
      self.animations[animation_index].draw(result)
    
    profiler.measure_stop("map rend. anim")
      
    # draw info boards
      
    profiler.measure_start("map rend. boards")
      
    players_by_numbers = map_to_render.get_players_by_numbers()
      
    x = self.map_render_location[0] + 12
    y = self.map_render_location[1] + self.prerendered_map_background.get_size()[1] + 20
      
    for i in players_by_numbers:
      if players_by_numbers[i] == None or self.player_info_board_images[i] == None:
        continue
        
      if players_by_numbers[i].is_dead():
        movement_offset = (0,0)
      else:
        movement_offset = (int(math.sin(pygame.time.get_ticks() / 64.0 + i) * 2),int(4 * math.sin(pygame.time.get_ticks() / 128.0 - i)))
        
      result.blit(self.player_info_board_images[i],(x + movement_offset[0],y + movement_offset[1]))
        
      x += self.gui_images["info board"].get_size()[0] - 2

    profiler.measure_stop("map rend. boards")

    profiler.measure_start("map rend. earthquake")

    if map_to_render.earthquake_is_active(): # shaking effect
      random_scale = random.uniform(0.99,1.01)
      result = pygame.transform.rotate(result,random.uniform(-4,4))
   
    profiler.measure_stop("map rend. earthquake")
   
    if map_to_render.get_state() == GameMap.STATE_WAITING_TO_PLAY:
      third = GameMap.START_GAME_AFTER / 3
      
      countdown_image_index = max(3 - map_to_render.get_map_time() / third,1)
      countdown_image = self.gui_images["countdown"][countdown_image_index]
      countdown_position = (self.screen_center[0] - countdown_image.get_size()[0] / 2,self.screen_center[1] - countdown_image.get_size()[1] / 2)
      
      result.blit(countdown_image,countdown_position)
   
    return result    


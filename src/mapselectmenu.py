import os
import random

from menu import Menu
from renderer import Renderer
from config import MAP_PATH

class MapSelectMenu(Menu):

  #----------------------------------------------------------------------------

  def __init__(self,sound_player):
    super(MapSelectMenu,self).__init__(sound_player)
    self.text = "Now select a map."
    self.map_filenames = []
    self.update_items()

  #----------------------------------------------------------------------------
    
  def update_items(self):
    self.map_filenames = sorted([filename for filename in os.listdir(MAP_PATH) if os.path.isfile(os.path.join(MAP_PATH,filename))])

    special_color = (100,100,255)

    self.items = [["^" + Renderer.rgb_to_html_notation(special_color) + "pick random","^" + Renderer.rgb_to_html_notation(special_color) + "each game random"]]

    for filename in self.map_filenames:
      self.items[0].append(filename)

  #----------------------------------------------------------------------------
    
  def random_was_selected(self):
    return self.selected_item[0] == 1

  #----------------------------------------------------------------------------
    
  def show_map_preview(self):
    return self.selected_item[0] != 0 and self.selected_item[0] != 1

  #----------------------------------------------------------------------------
    
  def get_random_map_name(self):
    return random.choice(self.map_filenames)

  #----------------------------------------------------------------------------
    
  def get_selected_map_name(self):
    if self.selected_item[0] == 0:                # pick random
      return random.choice(self.map_filenames)
    
    try:
      index = self.selected_item[0] - 2
      
      if index < 0:
        return ""
      
      return self.map_filenames[index]
    except IndexError:
      return ""

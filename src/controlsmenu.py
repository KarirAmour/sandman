import pygame

from menu import Menu
from playerkeymaps import PlayerKeyMaps
from game import Game

class ControlsMenu(Menu):

  #----------------------------------------------------------------------------

  def __init__(self, sound_player, player_key_maps, game):
    super(ControlsMenu,self).__init__(sound_player)
    self.player_key_maps = player_key_maps
    self.game = game
    self.waiting_for_key = None     # if not None, this contains a tuple (player number, action) of action that is currently being remapped
    self.wait_for_release = False   # used to wait for keys release before new key map is captured

    self.update_items()

  #----------------------------------------------------------------------------

  def color_key_string(self, key_string):
    return "^#38A8F2" + key_string if key_string != "none" else "^#E83535" + key_string

  #----------------------------------------------------------------------------
    
  def update_items(self):
    self.items = [["go back"]]
    
    prompt_string = "press some key"
    
    for i in range(Game.NUMBER_OF_CONTROLLED_PLAYERS):
      player_string = "p " + str(i + 1)
      
      player_maps = self.player_key_maps.get_players_key_mapping(i)

      for action in player_maps:
        item_string = player_string + " " + PlayerKeyMaps.ACTION_NAMES[action] + ": "
        
        if self.waiting_for_key == (i,action):
          item_string += prompt_string
        else:
          item_string += self.color_key_string(PlayerKeyMaps.key_to_string(player_maps[action]))
        
        self.items[0] += [item_string]
      
    # add menu item
    item_string = "open menu: "
    
    if self.waiting_for_key != None and self.waiting_for_key[1] == PlayerKeyMaps.ACTION_MENU:
      item_string += prompt_string
    else:
      item_string += self.color_key_string(PlayerKeyMaps.key_to_string(self.player_key_maps.get_menu_key_map()))
      
    self.items[0] += [item_string]

  #----------------------------------------------------------------------------

  ## This should be called periodically when the menu is active. It will
  #  take care of catching pressed keys if waiting for key remap.

  def update(self, player_key_maps):
    if self.waiting_for_key != None:
      keys_pressed = list(pygame.key.get_pressed()) 
      
      key_pressed = None
      
      mouse_actions = player_key_maps.get_current_mouse_control_states()     
      
      if len(mouse_actions) > 0:
        key_pressed = mouse_actions[0]
        
      for i in range(len(keys_pressed)):      # find pressed key
        if not (i in (pygame.K_NUMLOCK,pygame.K_CAPSLOCK,pygame.K_SCROLLOCK,322)) and keys_pressed[i]:
          key_pressed = i
          break
        
      if self.wait_for_release:
        if key_pressed == None:
          self.wait_for_release = False
      else:
         if key_pressed != None:
           
           debug_log("new key mapping")
           
           self.player_key_maps.set_one_key_map(key_pressed,self.waiting_for_key[0],self.waiting_for_key[1])
           self.waiting_for_key = None
           self.state = Menu.MENU_STATE_SELECTING
           self.game.save_settings()
           
           for item in self.action_keys_previous_state:
             self.action_keys_previous_state[item] = True
    
    self.update_items()

  #----------------------------------------------------------------------------

  def action_pressed(self, action):
    super(ControlsMenu,self).action_pressed(action)
    
    if self.waiting_for_key != None:
      self.waiting_for_key = None
      self.state = Menu.MENU_STATE_SELECTING
    elif action == PlayerKeyMaps.ACTION_BOMB and self.selected_item[0] > 0:
      # new key map will be captured
      helper_index = self.selected_item[0] - 1
      
      if helper_index == Game.NUMBER_OF_CONTROLLED_PLAYERS * 6:   # 6 controls for each player, then menu item follows
        self.waiting_for_key = (-1,PlayerKeyMaps.ACTION_MENU)
      else:
        action_index = helper_index % 6
        
        helper_array = (PlayerKeyMaps.ACTION_UP,PlayerKeyMaps.ACTION_RIGHT,PlayerKeyMaps.ACTION_DOWN,PlayerKeyMaps.ACTION_LEFT,PlayerKeyMaps.ACTION_BOMB,PlayerKeyMaps.ACTION_SPECIAL)
        helper_action = helper_array[action_index]
        
        self.waiting_for_key = (helper_index / 6,helper_action)
      
      self.wait_for_release = True
      
      self.state = Menu.MENU_STATE_SELECTING
      
    self.update_items()

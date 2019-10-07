#==============================================================================

## Abstract class representing a game menu. Menu item strings can contain formatting characters:
#
#  ^htmlcolorcode - sets the text color (HTML #rrggbb format,e.g. ^#2E44BF) from here to end of line or another formatting character
#==============================================================================    
class Menu(object):
  MENU_STATE_SELECTING = 0                ##< still selecting an item
  MENU_STATE_CONFIRM = 1                  ##< menu has been confirmed
  MENU_STATE_CANCEL = 2                   ##< menu has been cancelled
  MENU_STATE_CONFIRM_PROMPT = 3           ##< prompting an action
  
  MENU_MAX_ITEMS_VISIBLE = 11

  #----------------------------------------------------------------------------
  
  def __init__(self,sound_player):
    self.text = ""
    self.selected_item = (0,0)            ##< row, column
    self.items = []                       ##< list (rows) of lists (column)
    self.menu_left = False
    self.confirm_prompt_result = None     ##< True, False or None
    self.scroll_position = 0              ##< index of the first visible row
    self.sound_player = sound_player
    self.action_keys_previous_state = {
      PlayerKeyMaps.ACTION_UP : True,
      PlayerKeyMaps.ACTION_RIGHT : True,
      PlayerKeyMaps.ACTION_DOWN : True,
      PlayerKeyMaps.ACTION_LEFT : True,
      PlayerKeyMaps.ACTION_BOMB : True,
      PlayerKeyMaps.ACTION_SPECIAL : True,
      PlayerKeyMaps.ACTION_BOMB_DOUBLE: True,
      PlayerKeyMaps.ACTION_MENU : True}        ##< to detect single key presses, the values have to be True in order not to rect immediatelly upon entering the menu
    self.state = Menu.MENU_STATE_SELECTING
    pass

  #----------------------------------------------------------------------------

  def get_scroll_position(self):
    return self.scroll_position

  #----------------------------------------------------------------------------

  def get_state(self):
    return self.state

  #----------------------------------------------------------------------------
    
  def prompt_action_confirm(self):
    self.confirm_prompt_result = None
    self.state = Menu.MENU_STATE_CONFIRM_PROMPT

  #----------------------------------------------------------------------------
    
  def get_text(self):
    return self.text

  #----------------------------------------------------------------------------
  
  ## Returns menu items in format: ( (column 1 row 1 text), (column 1 row 2 text), ...), ((column 2 row 1 text), ...) ).
  
  def get_items(self):
    return self.items

  #----------------------------------------------------------------------------
  
  ## Returns a selected menu item in format (row, column).
  
  def get_selected_item(self):
    return self.selected_item

  #----------------------------------------------------------------------------
  
  def process_inputs(self, input_list):
    if self.menu_left:
      self.menu_left = False
      self.state = Menu.MENU_STATE_SELECTING
      
      for action_code in self.action_keys_previous_state:
        self.action_keys_previous_state[action_code] = True
        
      return
    
    actions_processed = []
    actions_pressed = []
    
    for action in input_list:
      action_code = action[1]
      
      if not self.action_keys_previous_state[action_code]:
        # the following condition disallows ACTION_BOMB and ACTION_BOMB_DOUBLE to be in the list at the same time => causes trouble
        if (not (action_code in actions_pressed) and not(
          (action_code == PlayerKeyMaps.ACTION_BOMB and PlayerKeyMaps.ACTION_BOMB_DOUBLE in actions_pressed) or
          (action_code == PlayerKeyMaps.ACTION_BOMB_DOUBLE and PlayerKeyMaps.ACTION_BOMB in actions_pressed) )):
          actions_pressed.append(action_code)
    
      actions_processed.append(action_code)
    
    for action_code in self.action_keys_previous_state:
      self.action_keys_previous_state[action_code] = False
      
    for action_code in actions_processed:
      self.action_keys_previous_state[action_code] = True
    
    for action in actions_pressed:
      self.action_pressed(action)
  
  #----------------------------------------------------------------------------
   
  def mouse_went_over_item(self, item_coordinates):
    self.selected_item = item_coordinates

  #----------------------------------------------------------------------------
     
  ## Handles mouse button events in the menu.
     
  def mouse_button_pressed(self, button_number):
    if button_number == 0:       # left
      self.action_pressed(PlayerKeyMaps.ACTION_BOMB)
    elif button_number == 1:     # right
      self.action_pressed(PlayerKeyMaps.ACTION_SPECIAL)
    elif button_number == 3:     # up
      self.scroll(True)
    elif button_number == 4:     # down
      self.scroll(False)

  #----------------------------------------------------------------------------
    
  def scroll(self, up):
    if up:
      if self.scroll_position > 0:
        self.scroll_position -= 1
        self.action_pressed(PlayerKeyMaps.ACTION_UP)
    else:   # down
      rows = len(self.items[self.selected_item[1]])  
      maximum_row = rows - Menu.MENU_MAX_ITEMS_VISIBLE
      
      if self.scroll_position < maximum_row:
        self.scroll_position += 1
        self.action_pressed(PlayerKeyMaps.ACTION_DOWN)

  #----------------------------------------------------------------------------
    
  ## Should be called when the menu is being left.
     
  def leaving(self):
    self.menu_left = True
    self.confirm_prompt_result = None
    self.sound_player.play_sound_event(SoundPlayer.SOUND_EVENT_CONFIRM)

  #----------------------------------------------------------------------------
     
  ## Prompts confirmation of given menu item if it has been selected.
     
  def prompt_if_needed(self, menu_item_coordinates):
    if self.state == Menu.MENU_STATE_CONFIRM and (self.confirm_prompt_result == None or self.confirm_prompt_result == False) and self.selected_item == menu_item_coordinates:
      self.prompt_action_confirm()

  #----------------------------------------------------------------------------
     
  ## Is called once for every action key press (not each frame, which is
  #  not good for menus). This can be overridden.
  
  def action_pressed(self, action):
    old_selected_item = self.selected_item
    
    if self.state == Menu.MENU_STATE_CONFIRM_PROMPT:
      if action == PlayerKeyMaps.ACTION_BOMB or action == PlayerKeyMaps.ACTION_BOMB_DOUBLE:
        self.confirm_prompt_result = True
        self.state = Menu.MENU_STATE_CONFIRM
      else:
        self.confirm_prompt_result = False
        self.state = Menu.MENU_STATE_SELECTING
    else:
      if action == PlayerKeyMaps.ACTION_UP:
        self.selected_item = (max(0,self.selected_item[0] - 1),self.selected_item[1])
      elif action == PlayerKeyMaps.ACTION_DOWN:
        self.selected_item = (min(len(self.items[self.selected_item[1]]) - 1,self.selected_item[0] + 1),self.selected_item[1])
      elif action == PlayerKeyMaps.ACTION_LEFT:
        new_column = max(0,self.selected_item[1] - 1)
        self.selected_item = (min(len(self.items[new_column]) - 1,self.selected_item[0]),new_column)
      elif action == PlayerKeyMaps.ACTION_RIGHT:
        new_column = min(len(self.items) - 1,self.selected_item[1] + 1)
        self.selected_item = (min(len(self.items[new_column]) - 1,self.selected_item[0]),new_column)
      elif action == PlayerKeyMaps.ACTION_BOMB or action == PlayerKeyMaps.ACTION_BOMB_DOUBLE:
        self.state = Menu.MENU_STATE_CONFIRM
      elif action == PlayerKeyMaps.ACTION_SPECIAL:
        self.state = Menu.MENU_STATE_CANCEL
      
    if self.selected_item[0] >= self.scroll_position + Menu.MENU_MAX_ITEMS_VISIBLE:
      self.scroll_position += 1
    elif self.selected_item[0] < self.scroll_position:
      self.scroll_position -= 1
      
    if self.selected_item != old_selected_item:
      self.sound_player.play_sound_event(SoundPlayer.SOUND_EVENT_CLICK)
    
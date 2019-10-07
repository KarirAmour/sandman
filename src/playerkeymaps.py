
import pygame

from stringserializable import StringSerializable
from config import NUMBER_OF_CONTROLLED_PLAYERS
from debug import DEBUG_PROFILING, DEBUG_FPS, DEBUG_VERBOSE, debug_log
from rendererutils import RendererUtils

## Handles conversion of keyboard events to actions of players, plus general
#  actions (such as menu, ...). Also managed some more complex input processing.

class PlayerKeyMaps(StringSerializable):
  ACTION_UP = 0
  ACTION_RIGHT = 1
  ACTION_DOWN = 2
  ACTION_LEFT = 3
  ACTION_BOMB = 4
  ACTION_SPECIAL = 5
  ACTION_MENU = 6                ##< brings up the main menu 
  ACTION_BOMB_DOUBLE = 7
  
  MOUSE_CONTROL_UP = -1
  MOUSE_CONTROL_RIGHT = -2
  MOUSE_CONTROL_DOWN = -3
  MOUSE_CONTROL_LEFT = -4
  MOUSE_CONTROL_BUTTON_L = -5
  MOUSE_CONTROL_BUTTON_M = -6
  MOUSE_CONTROL_BUTTON_R = -7
  
  MOUSE_CONTROL_BIAS = 2         ##< mouse movement bias in pixels
  
  TYPED_STRING_BUFFER_LENGTH = 15
  
  ACTION_NAMES = {
    ACTION_UP : "up",
    ACTION_RIGHT : "right",
    ACTION_DOWN : "down",
    ACTION_LEFT : "left",
    ACTION_BOMB : "bomb",
    ACTION_SPECIAL : "special",
    ACTION_MENU : "menu",
    ACTION_BOMB_DOUBLE : "bomb double" 
    }
  
  MOUSE_ACTION_NAMES = {
    MOUSE_CONTROL_UP : "m up",
    MOUSE_CONTROL_RIGHT : "m right",
    MOUSE_CONTROL_DOWN : "m down",
    MOUSE_CONTROL_LEFT : "m left",
    MOUSE_CONTROL_BUTTON_L : "m L",
    MOUSE_CONTROL_BUTTON_M : "m M",
    MOUSE_CONTROL_BUTTON_R : "m R"
    }
  
  MOUSE_CONTROL_SMOOTH_OUT_TIME = 50

  #----------------------------------------------------------------------------

  def __init__(self):
    self.key_maps = {}  ##< maps keys to tuples of a format: (player_number, action), for general actions player_number will be -1
    
    self.bomb_key_last_pressed_time = [0 for i in range(10)]  ##< for bomb double press detection
    self.bomb_key_previous_state = [False for i in range(10)] ##< for bomb double press detection

    self.allow_mouse_control = False    ##< if true, player movement by mouse is allowed, otherwise not

    mouse_control_constants = [
      PlayerKeyMaps.MOUSE_CONTROL_UP,
      PlayerKeyMaps.MOUSE_CONTROL_RIGHT,
      PlayerKeyMaps.MOUSE_CONTROL_DOWN,
      PlayerKeyMaps.MOUSE_CONTROL_LEFT,
      PlayerKeyMaps.MOUSE_CONTROL_BUTTON_L,
      PlayerKeyMaps.MOUSE_CONTROL_BUTTON_M,
      PlayerKeyMaps.MOUSE_CONTROL_BUTTON_R]

    self.mouse_control_states = {}
    self.mouse_control_keep_until = {}  ##< time in which specified control was activated,
                                        #   helps keeping them active for a certain amount of time to smooth them out 
    mouse_control_states = {
      PlayerKeyMaps.MOUSE_CONTROL_UP : False,
      PlayerKeyMaps.MOUSE_CONTROL_RIGHT : False,
      PlayerKeyMaps.MOUSE_CONTROL_DOWN : False,
      PlayerKeyMaps.MOUSE_CONTROL_LEFT : False,
      PlayerKeyMaps.MOUSE_CONTROL_BUTTON_L : False,
      PlayerKeyMaps.MOUSE_CONTROL_BUTTON_M : False,
      PlayerKeyMaps.MOUSE_CONTROL_BUTTON_R : False
      }

    for item in mouse_control_constants:
      self.mouse_control_states[item] = False
      self.mouse_control_keep_until[item] = 0
      
    self.mouse_button_states = [False,False,False,False,False] ##< (left, right, middle, wheel up, wheel down)
    self.previous_mouse_button_states = [False,False,False,False,False]  
    self.last_mouse_update_frame = -1
    
    
    self.name_code_mapping = {}     # holds a mapping of key names to pygame key codes, since pygame itself offers no such functionality   
    keys_pressed = pygame.key.get_pressed()
    
    for key_code in range(len(keys_pressed)):
      self.name_code_mapping[pygame.key.name(key_code)] = key_code
     
    self.typed_string_buffer = [" " for i in range(PlayerKeyMaps.TYPED_STRING_BUFFER_LENGTH)]
     
    self.reset()

  #----------------------------------------------------------------------------

  def pygame_name_to_key_code(self, pygame_name):
    try:
      return self.name_code_mapping[pygame_name]
    except KeyError:
      return -1

  #----------------------------------------------------------------------------

  ## Returns a state of mouse buttons including mouse wheel (unlike pygame.mouse.get_pressed) as
  #  a tuple (left, right, middle, wheel up, wheel down).

  def get_mouse_button_states(self):
    return self.mouse_button_states

  #----------------------------------------------------------------------------
    
  ## Returns a tuple corresponding to mouse buttons (same as get_mouse_button_states) where each
  #  item says if the button has been pressed since the last frame.
    
  def get_mouse_button_events(self):
    result = []
    
    for i in range(5):
      result.append(self.mouse_button_states[i] and not self.previous_mouse_button_states[i])
    
    return result

  #----------------------------------------------------------------------------
    
  ## This informs the object abour pygame events so it can keep track of some input states.
    
  def process_pygame_events(self, pygame_events, frame_number):
    if frame_number != self.last_mouse_update_frame:
      # first time calling this function this frame => reset states
    
      for i in range(5):      # for each of 5 buttons
        self.previous_mouse_button_states[i] = self.mouse_button_states[i]
    
      button_states = pygame.mouse.get_pressed()
    
      self.mouse_button_states[0] = button_states[0]
      self.mouse_button_states[1] = button_states[2]
      self.mouse_button_states[2] = button_states[1]
      self.mouse_button_states[3] = False
      self.mouse_button_states[4] = False     
      self.last_mouse_update_frame = frame_number

    for pygame_event in pygame_events:
      if pygame_event.type == pygame.MOUSEBUTTONDOWN:
        if pygame_event.button == 4:
          self.mouse_button_states[3] = True
        elif pygame_event.button == 5:
          self.mouse_button_states[4] = True
      elif pygame_event.type == pygame.KEYDOWN:
        try:
          self.typed_string_buffer = self.typed_string_buffer[1:]
          self.typed_string_buffer.append(chr(pygame_event.key))
        except Exception:
          debug_log("couldn't append typed character to the buffer")

  #----------------------------------------------------------------------------
        
  def clear_typing_buffer(self):
    self.typed_string_buffer = [" " for i in range(PlayerKeyMaps.TYPED_STRING_BUFFER_LENGTH)]

  #----------------------------------------------------------------------------
        
  def string_was_typed(self, string):
    return str.find("".join(self.typed_string_buffer),string) >= 0

  #----------------------------------------------------------------------------
        
  def reset(self):
    self.allow_control_by_mouse(False)
    self.set_player_key_map(0,pygame.K_w,pygame.K_d,pygame.K_s,pygame.K_a,pygame.K_c,pygame.K_v)
    self.set_player_key_map(1,pygame.K_UP,pygame.K_RIGHT,pygame.K_DOWN,pygame.K_LEFT,pygame.K_RETURN,pygame.K_RSHIFT)
    self.set_player_key_map(2,pygame.K_u,pygame.K_k,pygame.K_j,pygame.K_h,pygame.K_o,pygame.K_p)
    self.set_player_key_map(3,PlayerKeyMaps.MOUSE_CONTROL_UP,PlayerKeyMaps.MOUSE_CONTROL_RIGHT,PlayerKeyMaps.MOUSE_CONTROL_DOWN,PlayerKeyMaps.MOUSE_CONTROL_LEFT,PlayerKeyMaps.MOUSE_CONTROL_BUTTON_L,PlayerKeyMaps.MOUSE_CONTROL_BUTTON_R)
    self.set_special_key_map(pygame.K_ESCAPE)

  #----------------------------------------------------------------------------

  ##< Gets a direction of given action (0 - up, 1 - right, 2 - down, 3 - left).

  @staticmethod
  def get_action_direction_number(action):
    if action == PlayerKeyMaps.ACTION_UP:
      return 0
    elif action == PlayerKeyMaps.ACTION_RIGHT:
      return 1
    elif action == PlayerKeyMaps.ACTION_DOWN:
      return 2
    elif action == PlayerKeyMaps.ACTION_LEFT:
      return 3
    
    return 0

  #----------------------------------------------------------------------------

  @staticmethod
  def get_opposite_action(action):
    if action == PlayerKeyMaps.ACTION_UP:
      return PlayerKeyMaps.ACTION_DOWN
    elif action == PlayerKeyMaps.ACTION_RIGHT:
      return PlayerKeyMaps.ACTION_LEFT
    elif action == PlayerKeyMaps.ACTION_DOWN:
      return PlayerKeyMaps.ACTION_UP
    elif action == PlayerKeyMaps.ACTION_LEFT:
      return PlayerKeyMaps.ACTION_RIGHT
    
    return action

  #----------------------------------------------------------------------------

  @staticmethod
  def key_to_string(key):
    if key == None:
      return "none"
    
    if key in PlayerKeyMaps.MOUSE_ACTION_NAMES:
      result = PlayerKeyMaps.MOUSE_ACTION_NAMES[key]
    else:
      result = pygame.key.name(key)
    
      if result == "unknown key":
        result = str(key)
    
    return result   

  #----------------------------------------------------------------------------

  def set_one_key_map(self, key, player_number, action):
    if key != None:
      self.key_maps[key] = (player_number,action)
      
      to_be_deleted = []
      
      for item in self.key_maps:     # get rid of possible collissions
        if item != key and self.key_maps[item] == (player_number,action):
          to_be_deleted.append(item)
          
      for item in to_be_deleted:
        del self.key_maps[item]

  #----------------------------------------------------------------------------

  ## Sets a key mapping for a player of specified (non-negative) number.

  def set_player_key_map(self, player_number, key_up, key_right, key_down, key_left, key_bomb, key_special):
    self.set_one_key_map(key_up,player_number,PlayerKeyMaps.ACTION_UP)
    self.set_one_key_map(key_right,player_number,PlayerKeyMaps.ACTION_RIGHT)
    self.set_one_key_map(key_down,player_number,PlayerKeyMaps.ACTION_DOWN)
    self.set_one_key_map(key_left,player_number,PlayerKeyMaps.ACTION_LEFT)
    self.set_one_key_map(key_bomb,player_number,PlayerKeyMaps.ACTION_BOMB)
    self.set_one_key_map(key_special,player_number,PlayerKeyMaps.ACTION_SPECIAL)

  #----------------------------------------------------------------------------

  ## Gets a dict that says how keys are mapped for a specific player. Format: {action_code : key_code, ...}, the
  #  dict will contain all actions and possibly None values for unmapped actions.

  def get_players_key_mapping(self, player_number):
    result = {action : None for action in (
      PlayerKeyMaps.ACTION_UP,
      PlayerKeyMaps.ACTION_RIGHT,
      PlayerKeyMaps.ACTION_DOWN,
      PlayerKeyMaps.ACTION_LEFT,
      PlayerKeyMaps.ACTION_BOMB,
      PlayerKeyMaps.ACTION_SPECIAL)}
    
    for key in self.key_maps:
      if self.key_maps[key][0] == player_number:
        result[self.key_maps[key][1]] = key
    
    return result

  #----------------------------------------------------------------------------

  def allow_control_by_mouse(self, allow=True):
   self.allow_mouse_control = allow

  #----------------------------------------------------------------------------

  def set_special_key_map(self, key_menu):
    self.set_one_key_map(key_menu,-1,PlayerKeyMaps.ACTION_MENU)

  #----------------------------------------------------------------------------

  ## Makes a human-readable string that represents the current key-mapping.

  def save_to_string(self):
    result = ""

    for i in range(NUMBER_OF_CONTROLLED_PLAYERS):  # 4 players
      mapping = self.get_players_key_mapping(i)
      
      for action in mapping:
        result += str(i + 1) + " " + PlayerKeyMaps.ACTION_NAMES[action] + ": " + str(mapping[action]) + "\n"

    result += PlayerKeyMaps.ACTION_NAMES[PlayerKeyMaps.ACTION_MENU] + ": " + str(self.get_menu_key_map())
    
    return result

  #----------------------------------------------------------------------------
    
  ## Loads the mapping from string produced by save_to_string(...).
    
  def load_from_string(self, input_string):
    self.key_maps = {}
    
    lines = input_string.split("\n")
    
    for line in lines:
      line = line.lstrip().rstrip()
      
      try:
        key = int(line[line.find(":") + 1:])
      except Exception as e:
        key = None
      
      if line.find(PlayerKeyMaps.ACTION_NAMES[PlayerKeyMaps.ACTION_MENU]) == 0:
        self.set_one_key_map(key,-1,PlayerKeyMaps.ACTION_MENU)
      else:
        player_number = int(line[0]) - 1
        action_name = line[2:line.find(":")]
        
        action = None
        
        for helper_action in PlayerKeyMaps.ACTION_NAMES:
          if PlayerKeyMaps.ACTION_NAMES[helper_action] == action_name:
            action = helper_action
            break
      
        self.set_one_key_map(key,player_number,action)

  #----------------------------------------------------------------------------
    
  def get_menu_key_map(self):
    for key in self.key_maps:
      if self.key_maps[key][0] == -1:
        return key
      
    return None

  #----------------------------------------------------------------------------

  ## Returns a list of mouse control actions currently being performed (if mouse
  #  control is not allowed, the list will always be empty)

  def get_current_mouse_control_states(self):
    result = []
    
    if not self.allow_mouse_control:
      return result
    
    for mouse_action in self.mouse_control_states:
      if self.mouse_control_states[mouse_action]:
        result.append(mouse_action)
      
    return result

  #----------------------------------------------------------------------------

  ## From currently pressed keys makes a list of actions being currently performed and
  #  returns it, format: (player_number, action).

  def get_current_actions(self):
    keys_pressed = pygame.key.get_pressed()

    result = []

    reset_bomb_key_previous_state = [True for i in range(10)]

    # check mouse control:

    if self.allow_mouse_control:
      screen_center = (RendererUtils.get_screen_size()[0] / 2,RendererUtils.get_screen_size()[1] / 2)
      mouse_position = pygame.mouse.get_pos(screen_center)
      pressed = pygame.mouse.get_pressed()
      
      current_time = pygame.time.get_ticks()
      
      for item in self.mouse_control_states:    # reset
        if current_time > self.mouse_control_keep_until[item]:
          self.mouse_control_states[item] = False
      
      dx = abs(mouse_position[0] - screen_center[0])
      dy = abs(mouse_position[1] - screen_center[1])

      if dx > dy:            # choose the prevelant axis
        d_value = dx
        axis = 0
        axis_forward = PlayerKeyMaps.MOUSE_CONTROL_RIGHT
        axis_back = PlayerKeyMaps.MOUSE_CONTROL_LEFT
      else:
        axis = 1
        axis_forward = PlayerKeyMaps.MOUSE_CONTROL_DOWN
        axis_back = PlayerKeyMaps.MOUSE_CONTROL_UP
        d_value = dy

      if d_value > PlayerKeyMaps.MOUSE_CONTROL_BIAS:
        forward = mouse_position[axis] > screen_center[axis]
          
        self.mouse_control_states[axis_forward] = forward
        self.mouse_control_states[axis_back] = not forward          
        self.mouse_control_keep_until[axis_forward if forward else axis_back] = current_time + PlayerKeyMaps.MOUSE_CONTROL_SMOOTH_OUT_TIME  
        
      helper_buttons = (PlayerKeyMaps.MOUSE_CONTROL_BUTTON_L, PlayerKeyMaps.MOUSE_CONTROL_BUTTON_M, PlayerKeyMaps.MOUSE_CONTROL_BUTTON_R)

      for i in range(3):
        if pressed[i]:
          self.mouse_control_states[helper_buttons[i]] = True  
          self.mouse_control_keep_until[helper_buttons[i]] = current_time

      pygame.mouse.set_pos(screen_center)

    for key_code in self.key_maps:
      try:
        key_is_active = self.mouse_control_states[key_code] if key_code < 0 else keys_pressed[key_code]
      except IndexError as e:
        key_is_active = False
      
      if key_is_active:
        action_tuple = self.key_maps[key_code]  
        result.append(action_tuple)
        
        if action_tuple[1] == PlayerKeyMaps.ACTION_BOMB:
          player_number = action_tuple[0]
          
          if self.bomb_key_previous_state[player_number] == False and pygame.time.get_ticks() - self.bomb_key_last_pressed_time[player_number] < 200:
            result.append((player_number,PlayerKeyMaps.ACTION_BOMB_DOUBLE))
          
          self.bomb_key_last_pressed_time[player_number] = pygame.time.get_ticks()
          
          self.bomb_key_previous_state[player_number] = True
          reset_bomb_key_previous_state[player_number] = False

    for i in range(10):
      if reset_bomb_key_previous_state[i]:
        self.bomb_key_previous_state[i] = False

    return result

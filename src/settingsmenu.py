from menu import Menu


class SettingsMenu(Menu):
  COLOR_ON = "^#1DF53A"
  COLOR_OFF = "^#F51111"

  #----------------------------------------------------------------------------
  
  def __init__(self, sound_player, settings, game):
    super(SettingsMenu,self).__init__(sound_player)
    self.settings = settings
    self.game = game
    self.update_items()  

  #----------------------------------------------------------------------------
   
  def bool_to_str(self, bool_value):
    return SettingsMenu.COLOR_ON + "on" if bool_value else SettingsMenu.COLOR_OFF + "off"

  #----------------------------------------------------------------------------
    
  def update_items(self):
    self.items = [(
      "sound volume: " + (SettingsMenu.COLOR_ON if self.settings.sound_is_on() else SettingsMenu.COLOR_OFF) + str(int(self.settings.sound_volume * 10) * 10) + " %",
      "music volume: " + (SettingsMenu.COLOR_ON if self.settings.music_is_on() > 0.0 else SettingsMenu.COLOR_OFF) + str(int(self.settings.music_volume * 10) * 10) + " %",
      "screen resolution: " + str(self.settings.screen_resolution[0]) + " x " + str(self.settings.screen_resolution[1]),
      "fullscreen: " + self.bool_to_str(self.settings.fullscreen),
      "allow control by mouse: " + self.bool_to_str(self.settings.control_by_mouse),
      "configure controls",
      "complete reset",
      "back"
      )]    

  #----------------------------------------------------------------------------
    
  def action_pressed(self, action):
    super(SettingsMenu,self).action_pressed(action)

    self.prompt_if_needed((6,0))
    
    mouse_control_selected = False
    fullscreen_selected = False
    
    if self.state == Menu.MENU_STATE_SELECTING:
      if action == PlayerKeyMaps.ACTION_RIGHT:
        if self.selected_item == (0,0):
          self.settings.sound_volume = min(1.0,self.settings.sound_volume + 0.1)
          self.game.apply_sound_settings()
          self.game.save_settings()
        elif self.selected_item == (1,0):
          self.settings.music_volume = min(1.0,self.settings.music_volume + 0.1)
          self.game.apply_sound_settings()
          self.game.save_settings()
        elif self.selected_item == (2,0):
          self.settings.screen_resolution = Settings.POSSIBLE_SCREEN_RESOLUTIONS[(self.settings.current_resolution_index() + 1) % len(Settings.POSSIBLE_SCREEN_RESOLUTIONS)]      
          self.game.apply_screen_settings()
          self.game.save_settings()
      elif action == PlayerKeyMaps.ACTION_LEFT:
        if self.selected_item == (0,0):
          self.settings.sound_volume = max(0.0,self.settings.sound_volume - 0.1)
          self.game.apply_sound_settings()
          self.game.save_settings()
        elif self.selected_item == (1,0):
          self.settings.music_volume = max(0.0,self.settings.music_volume - 0.1)
          self.game.apply_sound_settings()
          self.game.save_settings()
        elif self.selected_item == (2,0):
          self.settings.screen_resolution = Settings.POSSIBLE_SCREEN_RESOLUTIONS[(self.settings.current_resolution_index() - 1) % len(Settings.POSSIBLE_SCREEN_RESOLUTIONS)]
          self.game.apply_screen_settings()
          self.game.save_settings()
    elif self.state == Menu.MENU_STATE_CONFIRM:
      if self.selected_item == (6,0):
        
        debug_log("resetting settings")
        
        self.settings.reset()
        self.game.save_settings()
        self.game.apply_sound_settings()
        self.game.apply_screen_settings()
        self.game.apply_other_settings()
        self.confirm_prompt_result = None
        self.state = Menu.MENU_STATE_SELECTING    
      elif self.selected_item == (3,0):
        fullscreen_selected = True
        self.state = Menu.MENU_STATE_SELECTING  
      elif self.selected_item == (4,0):
        mouse_control_selected = True
        self.state = Menu.MENU_STATE_SELECTING  
      elif self.selected_item != (7,0) and self.selected_item != (5,0):
        self.state = Menu.MENU_STATE_SELECTING  
      
    if mouse_control_selected:
      self.settings.control_by_mouse = not self.settings.control_by_mouse
      self.game.apply_other_settings()
      self.game.save_settings()
      self.state = Menu.MENU_STATE_SELECTING
      
    if fullscreen_selected:
      self.settings.fullscreen = not self.settings.fullscreen
      self.game.apply_screen_settings()
      self.game.save_settings()
      self.state = Menu.MENU_STATE_SELECTING

    self.update_items()

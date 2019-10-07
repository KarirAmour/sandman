    
from stringserializable import StringSerializable

class Settings(StringSerializable):
  POSSIBLE_SCREEN_RESOLUTIONS = (
    (960,720),
    (1024,768),
    (1280,720),
    (1280,1024),
    (1366,768),
    (1680,1050),
    (1920,1080)
    )
  
  SOUND_VOLUME_THRESHOLD = 0.01
  CONTROL_MAPPING_DELIMITER = "CONTROL MAPPING"
  
  #----------------------------------------------------------------------------

  def __init__(self, player_key_maps):
    self.player_key_maps = player_key_maps
    self.reset()

  #----------------------------------------------------------------------------
         
  def reset(self):
    self.sound_volume = 0.7
    self.music_volume = 0.2
    self.screen_resolution = Settings.POSSIBLE_SCREEN_RESOLUTIONS[0]
    self.fullscreen = False
    self.control_by_mouse = False
    self.player_key_maps.reset()

  #----------------------------------------------------------------------------

  def save_to_string(self):
    result = ""
    
    result += "sound volume: " + str(self.sound_volume) + "\n"
    result += "music volume: " + str(self.music_volume) + "\n"
    result += "screen resolution: " + str(self.screen_resolution[0]) + "x" + str(self.screen_resolution[1]) + "\n"
    result += "fullscreen: " + str(self.fullscreen) + "\n"
    result += "control by mouse: " + str(self.control_by_mouse) + "\n"
    result += Settings.CONTROL_MAPPING_DELIMITER + "\n"
    
    result += self.player_key_maps.save_to_string() + "\n"

    result += Settings.CONTROL_MAPPING_DELIMITER + "\n"
    
    return result

  #----------------------------------------------------------------------------
    
  def load_from_string(self, input_string):
    self.reset()
    
    helper_position = input_string.find(Settings.CONTROL_MAPPING_DELIMITER)
    
    if helper_position >= 0:
      helper_position1 = helper_position + len(Settings.CONTROL_MAPPING_DELIMITER)
      helper_position2 = input_string.find(Settings.CONTROL_MAPPING_DELIMITER,helper_position1)

      debug_log("loading control mapping")

      settings_string = input_string[helper_position1:helper_position2].lstrip().rstrip()
      self.player_key_maps.load_from_string(settings_string)

      input_string = input_string[:helper_position] + input_string[helper_position2 + len(Settings.CONTROL_MAPPING_DELIMITER):]
    
    lines = input_string.split("\n")
    
    for line in lines:
      helper_position = line.find(":")
      
      if helper_position < 0:
        continue
      
      key_string = line[:helper_position]
      value_string = line[helper_position + 1:].lstrip().rstrip()
      
      if key_string == "sound volume":
        self.sound_volume = float(value_string)
      elif key_string == "music volume":
        self.music_volume = float(value_string)
      elif key_string == "screen resolution":
        helper_tuple = value_string.split("x")
        self.screen_resolution = (int(helper_tuple[0]),int(helper_tuple[1]))
      elif key_string == "fullscreen":
        self.fullscreen = True if value_string == "True" else False     
      elif key_string == "control by mouse":
        self.control_by_mouse = True if value_string == "True" else False

  #----------------------------------------------------------------------------
    
  def sound_is_on(self):
    return self.sound_volume > Settings.SOUND_VOLUME_THRESHOLD

  #----------------------------------------------------------------------------
  
  def music_is_on(self):
    return self.music_volume > Settings.SOUND_VOLUME_THRESHOLD

  #----------------------------------------------------------------------------
   
  def current_resolution_index(self):
    return next((i for i in range(len(Settings.POSSIBLE_SCREEN_RESOLUTIONS)) if self.screen_resolution == Settings.POSSIBLE_SCREEN_RESOLUTIONS[i]),0)

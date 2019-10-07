    
import bombman

from playmenu import PlayMenu
from playerkeymaps import PlayerKeyMaps
from soundplayer import SoundPlayer
from playsetup import PlaySetup
from settingsmenu import SettingsMenu
from controlsmenu import ControlsMenu
from aboutmenu import AboutMenu
from mapselectmenu import MapSelectMenu
from playsetupmenu import PlaySetupMenu
from resultmenu import ResultMenu
from mainmenu import MainMenu
from menu import Menu
from gamemap import GameMap
from profiler import Profiler
from renderer import Renderer
# from ai import AI
# from settings import Settings

class Game(object):    
  # colors used for players and teams
  COLOR_WHITE = 0
  COLOR_BLACK = 1
  COLOR_RED = 2
  COLOR_BLUE = 3
  COLOR_GREEN = 4
  COLOR_CYAN = 5
  COLOR_YELLOW = 6
  COLOR_ORANGE = 7
  COLOR_BROWN = 8
  COLOR_PURPLE = 9

  COLOR_NAMES = [
    "white",
    "black",
    "red",
    "blue",
    "green",
    "cyan",
    "yellow",
    "orange",
    "brown",
    "purple"
    ]
    
  STATE_PLAYING = 0
  STATE_EXIT = 1
  STATE_MENU_MAIN = 2
  STATE_MENU_SETTINGS = 3
  STATE_MENU_ABOUT = 4
  STATE_MENU_PLAY_SETUP = 5
  STATE_MENU_MAP_SELECT = 6
  STATE_MENU_CONTROL_SETTINGS = 7
  STATE_MENU_PLAY = 8
  STATE_MENU_RESULTS = 9
  STATE_GAME_STARTED = 10
  
  CHEAT_PARTY = 0
  CHEAT_ALL_ITEMS = 1
  CHEAT_PLAYER_IMMORTAL = 2
  
  VERSION_STR = "0.95"
  
  NUMBER_OF_CONTROLLED_PLAYERS = 4    ##< maximum number of non-AI players on one PC
  
  RESOURCE_PATH = "resources"
  MAP_PATH = "maps"
  SETTINGS_FILE_PATH = "settings.txt"

  #----------------------------------------------------------------------------
  
  def __init__(self):
    pygame.mixer.pre_init(22050,-16,2,512)   # set smaller audio buffer size to prevent audio lag
    pygame.init()
    pygame.font.init()
    pygame.mixer.init()
    
    self.frame_number = 0
    
    self.player_key_maps = PlayerKeyMaps()
    
    self.settings = Settings(self.player_key_maps)
    
    self.game_number = 0
    
    if os.path.isfile(Game.SETTINGS_FILE_PATH):
      debug_log("loading settings from file " + Game.SETTINGS_FILE_PATH)
      
      self.settings.load_from_file(Game.SETTINGS_FILE_PATH)
 
    self.settings.save_to_file(Game.SETTINGS_FILE_PATH)  # save the reformatted settings file (or create a new one)
    
    pygame.display.set_caption("Bombman")
    
    self.renderer = Renderer()
    self.apply_screen_settings()
    
    self.sound_player = SoundPlayer()
    self.sound_player.change_music()
    self.apply_sound_settings()
    
    self.apply_other_settings()
             
    self.map_name = ""
    self.random_map_selection = False
    self.game_map = None
    
    self.play_setup = PlaySetup()
    
    self.menu_main = MainMenu(self.sound_player)
    self.menu_settings = SettingsMenu(self.sound_player,self.settings,self)
    self.menu_about = AboutMenu(self.sound_player)
    self.menu_play_setup = PlaySetupMenu(self.sound_player,self.play_setup)
    self.menu_map_select = MapSelectMenu(self.sound_player)
    self.menu_play = PlayMenu(self.sound_player)
    self.menu_controls = ControlsMenu(self.sound_player,self.player_key_maps,self)
    self.menu_results = ResultMenu(self.sound_player)
    
    self.ais = []
    
    self.state = Game.STATE_MENU_MAIN

    self.immortal_players_numbers = []
    self.active_cheats = set()

  #----------------------------------------------------------------------------

  def deactivate_all_cheats(self):
    self.active_cheats = set()

    debug_log("all cheats deactivated")

  #----------------------------------------------------------------------------
      
  def activate_cheat(self, what_cheat):
    self.active_cheats.add(what_cheat)
    
    debug_log("cheat activated")

  #----------------------------------------------------------------------------
    
  def deactivate_cheat(self, what_cheat):
    if what_cheat in self.active_cheats:
      self.active_cheats.remove(what_cheat)

  #----------------------------------------------------------------------------

  def cheat_is_active(self, what_cheat):
    return what_cheat in self.active_cheats

  #----------------------------------------------------------------------------

  def get_player_key_maps(self):
    return self.player_key_maps

  #----------------------------------------------------------------------------

  def get_settings(self):
    return self.settings

  #----------------------------------------------------------------------------

  def apply_screen_settings(self):
    display_flags = 0
    
    if self.settings.fullscreen:
      display_flags += pygame.FULLSCREEN
 
    self.screen = pygame.display.set_mode(self.settings.screen_resolution,display_flags)
    
    screen_center = (Renderer.get_screen_size()[0] / 2,Renderer.get_screen_size()[1] / 2)
    pygame.mouse.set_pos(screen_center)
    
    self.renderer.update_screen_info()

  #----------------------------------------------------------------------------
  
  def apply_sound_settings(self):
    self.sound_player.set_music_volume(self.settings.music_volume)
    self.sound_player.set_sound_volume(self.settings.sound_volume)

  #----------------------------------------------------------------------------
  
  def apply_other_settings(self):
    self.player_key_maps.allow_control_by_mouse(self.settings.control_by_mouse)

  #----------------------------------------------------------------------------
  
  def save_settings(self):
    self.settings.save_to_file(Game.SETTINGS_FILE_PATH)

  #----------------------------------------------------------------------------

  def __check_cheat(self, cheat_string, cheat = None):
    if self.player_key_maps.string_was_typed(cheat_string):
      if cheat != None:
        self.activate_cheat(cheat)
      else:
        self.deactivate_all_cheats()

      self.player_key_maps.clear_typing_buffer()

  #----------------------------------------------------------------------------

  ## Manages the menu actions and sets self.active_menu.

  def manage_menus(self):
    new_state = self.state
    prevent_input_processing = False
    
    # cheack if any cheat was typed:
    self.__check_cheat("party",game.CHEAT_PARTY)
    self.__check_cheat("herecomedatboi",game.CHEAT_ALL_ITEMS)
    self.__check_cheat("leeeroy",game.CHEAT_PLAYER_IMMORTAL)
    self.__check_cheat("revert")

    self.player_key_maps.get_current_actions()       # this has to be called in order for player_key_maps to update mouse controls properly
      
    # ================ MAIN MENU =================
    if self.state == Game.STATE_MENU_MAIN: 
      self.active_menu = self.menu_main
      
      if self.active_menu.get_state() == Menu.MENU_STATE_CONFIRM:
        new_state = [
          Game.STATE_MENU_PLAY_SETUP,
          Game.STATE_MENU_SETTINGS,
          Game.STATE_MENU_ABOUT,
          Game.STATE_EXIT
          ] [self.active_menu.get_selected_item()[0]]

    # ================ PLAY MENU =================
    elif self.state == Game.STATE_MENU_PLAY:
      self.active_menu = self.menu_play

      if self.active_menu.get_state() == Menu.MENU_STATE_CANCEL:
        new_state = Game.STATE_PLAYING

      elif self.active_menu.get_state() == Menu.MENU_STATE_CONFIRM:
        if self.active_menu.get_selected_item() == (0,0):
          new_state = Game.STATE_PLAYING
          
          for player in self.game_map.get_players():
            player.wait_for_bomb_action_release()
          
        elif self.active_menu.get_selected_item() == (1,0):
          new_state = Game.STATE_MENU_MAIN
          self.sound_player.change_music()
          self.deactivate_all_cheats()
    
    # ============== SETTINGS MENU ===============
    elif self.state == Game.STATE_MENU_SETTINGS: 
      self.active_menu = self.menu_settings
      
      if self.active_menu.get_state() == Menu.MENU_STATE_CANCEL:
        new_state = Game.STATE_MENU_MAIN
      elif self.active_menu.get_state() == Menu.MENU_STATE_CONFIRM:
        if self.active_menu.get_selected_item() == (5,0):
          new_state = Game.STATE_MENU_CONTROL_SETTINGS
        elif self.active_menu.get_selected_item() == (7,0):
          new_state = Game.STATE_MENU_MAIN

    # ========== CONTROL SETTINGS MENU ===========
    elif self.state == Game.STATE_MENU_CONTROL_SETTINGS:
      self.active_menu = self.menu_controls
      self.active_menu.update(self.player_key_maps)    # needs to be called to scan for pressed keys
      
      if self.active_menu.get_state() == Menu.MENU_STATE_CANCEL:
        new_state = Game.STATE_MENU_SETTINGS
      elif self.active_menu.get_state() == Menu.MENU_STATE_CONFIRM:
        if self.active_menu.get_selected_item() == (0,0):
          new_state = Game.STATE_MENU_SETTINGS
        
    # ================ ABOUT MENU =================
    elif self.state == Game.STATE_MENU_ABOUT: 
      self.active_menu = self.menu_about
      
      if self.active_menu.get_state() in (Menu.MENU_STATE_CONFIRM,Menu.MENU_STATE_CANCEL):
        new_state = Game.STATE_MENU_MAIN
    
    # ============== PLAY SETUP MENU ==============
    elif self.state == Game.STATE_MENU_PLAY_SETUP: 
      self.active_menu = self.menu_play_setup
      
      if self.active_menu.get_state() == Menu.MENU_STATE_CANCEL:
        new_state = Game.STATE_MENU_MAIN
      elif self.active_menu.get_state() == Menu.MENU_STATE_CONFIRM:
        if self.active_menu.get_selected_item() == (0,1):
          new_state = Game.STATE_MENU_MAP_SELECT
        elif self.active_menu.get_selected_item() == (0,0):
          new_state = Game.STATE_MENU_MAIN
    
    # ============== MAP SELECT MENU ==============
    elif self.state == Game.STATE_MENU_MAP_SELECT:
      self.active_menu = self.menu_map_select
      
      if self.active_menu.get_state() == Menu.MENU_STATE_CANCEL:
        new_state = Game.STATE_MENU_PLAY_SETUP
      elif self.active_menu.get_state() == Menu.MENU_STATE_CONFIRM:
        self.map_name = self.active_menu.get_selected_map_name()
        self.random_map_selection = self.active_menu.random_was_selected()
        self.game_number = 1     # first game
        new_state = Game.STATE_GAME_STARTED
        
        self.deactivate_cheat(Game.CHEAT_PARTY)
    
    # ================ RESULT MENU ================
    elif self.state == Game.STATE_MENU_RESULTS:
      self.active_menu = self.menu_results
    
      if self.active_menu.get_state() in (Menu.MENU_STATE_CONFIRM,Menu.MENU_STATE_CANCEL):
        new_state = Game.STATE_MENU_MAIN
      
    if new_state != self.state:  # going to new state
      self.state = new_state
      self.active_menu.leaving()
    
    self.active_menu.process_inputs(self.player_key_maps.get_current_actions())

  #----------------------------------------------------------------------------

  def acknowledge_wins(self, winner_team_number, players):
    for player in players:
      if player.get_team_number() == winner_team_number:
        player.set_wins(player.get_wins() + 1)    

  #----------------------------------------------------------------------------

  def run(self):
    time_before = pygame.time.get_ticks()

    show_fps_in = 0
    pygame_clock = pygame.time.Clock()

    while True:                                  # main loop
      profiler.measure_start("main loop")
      
      dt = min(pygame.time.get_ticks() - time_before,100)
      time_before = pygame.time.get_ticks()

      pygame_events = []

      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          self.state = Game.STATE_EXIT
        
        pygame_events.append(event)

      self.player_key_maps.process_pygame_events(pygame_events,self.frame_number)

      if self.state == Game.STATE_PLAYING:
        self.renderer.process_animation_events(self.game_map.get_and_clear_animation_events()) # play animations
        self.sound_player.process_events(self.game_map.get_and_clear_sound_events())           # play sounds
        
        profiler.measure_start("map rend.")
        self.screen.blit(self.renderer.render_map(self.game_map),(0,0)) 
        profiler.measure_stop("map rend.")
        
        profiler.measure_start("sim.")
        self.simulation_step(dt)
        profiler.measure_stop("sim.")
        
        if self.game_map.get_state() == GameMap.STATE_GAME_OVER:
          self.game_number += 1
          
          if self.game_number > self.play_setup.get_number_of_games():
            previous_winner = self.game_map.get_winner_team()
            self.acknowledge_wins(previous_winner,self.game_map.get_players())
            self.menu_results.set_results(self.game_map.get_players())
            self.game_map = None
            self.state = Game.STATE_MENU_RESULTS   # show final results
            self.deactivate_all_cheats()
          else:
            self.state = Game.STATE_GAME_STARTED   # new game
      elif self.state == Game.STATE_GAME_STARTED:
        debug_log("starting game " + str(self.game_number))
    
        previous_winner = -1
    
        if self.game_number != 1:
          previous_winner = self.game_map.get_winner_team()
        
        kill_counts = [0 for i in range(10)]
        win_counts = [0 for i in range(10)]
        
        if self.game_map != None:
          for player in self.game_map.get_players():
            kill_counts[player.get_number()] = player.get_kills()
            win_counts[player.get_number()] = player.get_wins()
        
        map_name_to_load = self.map_name if not self.random_map_selection else self.menu_map_select.get_random_map_name()
        
        with open(os.path.join(Game.MAP_PATH,map_name_to_load)) as map_file:
          map_data = map_file.read()
          self.game_map = GameMap(map_data,self.play_setup,self.game_number,self.play_setup.get_number_of_games(),self.cheat_is_active(Game.CHEAT_ALL_ITEMS))
          
        player_slots = self.play_setup.get_slots()
        
        if self.cheat_is_active(Game.CHEAT_PLAYER_IMMORTAL):
          self.immortal_players_numbers = []
          
          for i in range(len(player_slots)):
            if player_slots[i] != None and player_slots[i][0] >= 0:   # cheat: if not AI
              self.immortal_players_numbers.append(i)                 # make the player immortal
        
        self.ais = []
        
        for i in range(len(player_slots)):
          if player_slots[i] != None and player_slots[i][0] < 0:  # indicates AI
            self.ais.append(AI(self.game_map.get_players_by_numbers()[i],self.game_map))
      
        for player in self.game_map.get_players():
          player.set_kills(kill_counts[player.get_number()])
          player.set_wins(win_counts[player.get_number()])
        
        self.acknowledge_wins(previous_winner,self.game_map.get_players())    # add win counts
        
        self.sound_player.change_music()
        self.state = Game.STATE_PLAYING
      elif self.state == Game.STATE_EXIT:
        break
      else:   # in menu
        self.manage_menus()
        
        profiler.measure_start("menu rend.")
        self.screen.blit(self.renderer.render_menu(self.active_menu,self),(0,0))  
        profiler.measure_stop("menu rend.")

      pygame.display.flip()
      pygame_clock.tick()

      if show_fps_in <= 0:
        if DEBUG_FPS:
          debug_log("fps: " + str(pygame_clock.get_fps()))

        show_fps_in = 255
      else:
        show_fps_in -= 1
        
      self.frame_number += 1
      
      profiler.measure_stop("main loop")
      
      if DEBUG_PROFILING:
        debug_log(profiler.get_profile_string())
        profiler.end_of_frame()

  #----------------------------------------------------------------------------

  ## Filters a list of performed actions so that there are no actions of
  #  human players that are not participating in the game.

  def filter_out_disallowed_actions(self, actions):
    player_slots = self.play_setup.get_slots()
    result = filter(lambda a: (player_slots[a[0]] != None and player_slots[a[0]] >=0) or (a[1] == PlayerKeyMaps.ACTION_MENU), actions)    
    return result

  #----------------------------------------------------------------------------

  def simulation_step(self, dt):
    actions_being_performed = self.filter_out_disallowed_actions(self.player_key_maps.get_current_actions())
    
    for action in actions_being_performed:
      if action[0] == -1:                                # menu key pressed
        self.state = Game.STATE_MENU_PLAY
        return
    
    profiler.measure_start("sim. AIs")
    
    for i in range(len(self.ais)):
      actions_being_performed = actions_being_performed + self.ais[i].play()
      
    profiler.measure_stop("sim. AIs")
    
    players = self.game_map.get_players()

    profiler.measure_start("sim. inputs")
    
    for player in players:
      player.react_to_inputs(actions_being_performed,dt,self.game_map)
      
    profiler.measure_stop("sim. inputs")
      
    profiler.measure_start("sim. map update")
    
    self.game_map.update(dt,self.immortal_players_numbers)
    
    profiler.measure_stop("sim. map update")

  #----------------------------------------------------------------------------

  ## Sets up a test game for debugging, so that the menus can be avoided.
 
  def setup_test_game(self, setup_number = 0):
    if setup_number == 0:
      self.map_name = "classic"
      self.random_map_selection = False
      self.game_number = 1
      self.state = Game.STATE_GAME_STARTED
    elif setup_number == 1:
      self.play_setup.player_slots = [(-1,i) for i in range(10)]
      self.random_map_selection = True
      self.game_number = 1
      self.state = Game.STATE_GAME_STARTED      
    else:
      self.play_setup.player_slots = [((i,i) if i < 4 else None) for i in range(10)]
      self.map_name = "classic"
      self.game_number = 1
      self.state = Game.STATE_GAME_STARTED      

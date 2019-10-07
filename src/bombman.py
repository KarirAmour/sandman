#!/usr/bin/env python
# coding=utf-8
#
# Bombman - free and open-source Bomberman clone
#
# Copyright (C) 2016 Miloslav Číž
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ========================== A FEW COMMENTS ===========================
#
# Version numbering system:
#
# major.minor
#
# Major number increases with significant new features added (multiplayer, ...),
# minor number increases with small changes (bug fixes, AI improvements, ...) and
# it does so in this way: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 91, 92, 93, etc.
#
# ---------------------------------------------------------------------
#
# Map string format (may contain spaces and newlines, which will be ignored):
#
# <environment>;<player items>;<map items>;<tiles>
#    
# <environment>   - Name of the environment of the map (affects only visual appearance).
# <player items>  - Items that players have from the start of the game (can be an empty string),
#                   each item is represented by one letter (the same letter can appear multiple times):
#                     f - flame
#                     F - superflame
#                     b - bomb
#                     k - kicking shoe
#                     s - speedup
#                     p - spring
#                     d - disease
#                     m - multibomb
#                     r - random
#                     x - boxing glove
#                     e - detonator
#                     t - throwing glove
# <map items>     - Set of items that will be hidden in block on the map. This is a string of the
#                   same format as in <player items>. If there is more items specified than there is
#                   block tiles, then some items will be left out.
# <tiles>         - Left to right, top to bottom sequenced array of map tiles:
#                     . - floor
#                     x - block (destroyable)
#                     # - wall (undestroyable)
#                     A - teleport A
#                     B - teleport B
#                     T - trampoline
#                     V - lava
#                     u - arrow up, floor tile
#                     r - arrow right, floor tile
#                     d - arrow down, floor tile
#                     l - arrow left, floor tile
#                     U - arrow up, under block tile
#                     R - arrow right, under block tile
#                     D - arrow down, under block tile
#                     L - arrow left, under block tile
#                     <0-9> - starting position of the player specified by the number

import sys
import pygame
import os
import math
import copy
import random
import re
import time

from player import Player
from positionable import Positionable
from profiler import Profiler
from gamemap import GameMap
from bomb import Bomb

from stringserializable import StringSerializable
from playerkeymaps import PlayerKeyMaps


DEBUG_PROFILING = False
DEBUG_FPS = False
DEBUG_VERBOSE = False

#------------------------------------------------------------------------------

def debug_log(message):
  if DEBUG_VERBOSE:      
    print(message)

#==============================================================================


#==============================================================================


#==============================================================================


#==============================================================================

## Represents a flame coming off of an exploding bomb.

class Flame(object):

  #----------------------------------------------------------------------------

  def __init__(self):
    self.player = None               ##< reference to player to which the exploding bomb belonged
    self.time_to_burnout = 1000      ##< time in ms till the flame disappears
    self.direction = "all"           ##< string representation of the flame direction

#==============================================================================

class MapTile(object):
  TILE_FLOOR = 0                     ##< walkable map tile
  TILE_BLOCK = 1                     ##< non-walkable but destroyable map tile
  TILE_WALL = 2                      ##< non-walkable and non-destroyable map tile
  
  SPECIAL_OBJECT_TRAMPOLINE = 0
  SPECIAL_OBJECT_TELEPORT_A = 1
  SPECIAL_OBJECT_TELEPORT_B = 2
  SPECIAL_OBJECT_ARROW_UP = 3
  SPECIAL_OBJECT_ARROW_RIGHT = 4
  SPECIAL_OBJECT_ARROW_DOWN = 5
  SPECIAL_OBJECT_ARROW_LEFT = 6
  SPECIAL_OBJECT_LAVA = 7

  #----------------------------------------------------------------------------

  def __init__(self, coordinates):
    self.kind = MapTile.TILE_FLOOR
    self.flames = []
    self.coordinates = coordinates
    self.to_be_destroyed = False     ##< Flag that marks the tile to be destroyed after the flames go out.
    self.item = None                 ##< Item that's present on the file
    self.special_object = None       ##< special object present on the tile, like trampoline or teleport
    self.destination_teleport = None ##< in case of special_object equal to SPECIAL_OBJECT_TELEPORT_A or SPECIAL_OBJECT_TELEPORT_B holds the destionation teleport tile coordinates

  def shouldnt_walk(self):
    return self.kind in [MapTile.TILE_WALL,MapTile.TILE_BLOCK] or len(self.flames) >= 1 or self.special_object == MapTile.SPECIAL_OBJECT_LAVA

#==============================================================================

## Holds and manipulates the map data including the players, bombs etc.

#==============================================================================

## Defines how a game is set up, i.e. how many players
#  there are, what are the teams etc. Setup does not include
#  the selected map.

class PlaySetup(object):
  MAX_GAMES = 20

  #----------------------------------------------------------------------------
  
  def __init__(self):
    self.player_slots = [None for i in range(10)]    ##< player slots: (player_number, team_color),
                                                     #   negative player_number = AI, slot index ~ player color index
    self.number_of_games = 10
    
    # default setup, player 0 vs 3 AI players:
    self.player_slots[0] = (0,0)
    self.player_slots[1] = (-1,1)
    self.player_slots[2] = (-1,2)
    self.player_slots[3] = (-1,3)

  #----------------------------------------------------------------------------

  def get_slots(self):
    return self.player_slots

  #----------------------------------------------------------------------------

  def get_number_of_games(self):
    return self.number_of_games

  #----------------------------------------------------------------------------

  def set_number_of_games(self, number_of_games):
    self.number_of_games = number_of_games

  #----------------------------------------------------------------------------
  
  def increase_number_of_games(self):
    self.number_of_games = self.number_of_games % PlaySetup.MAX_GAMES + 1

  #----------------------------------------------------------------------------
  
  def decrease_number_of_games(self):
    self.number_of_games = (self.number_of_games - 2) % PlaySetup.MAX_GAMES + 1
   
#==============================================================================

    
#==============================================================================

#==============================================================================

class SoundPlayer(object):
  # sound events used by other classes to tell soundplayer what to play
  
  SOUND_EVENT_EXPLOSION = 0
  SOUND_EVENT_BOMB_PUT = 1
  SOUND_EVENT_WALK = 2
  SOUND_EVENT_KICK = 3
  SOUND_EVENT_DIARRHEA = 4
  SOUND_EVENT_SPRING = 5
  SOUND_EVENT_SLOW = 6
  SOUND_EVENT_DISEASE = 7
  SOUND_EVENT_CLICK = 8
  SOUND_EVENT_THROW = 9
  SOUND_EVENT_TRAMPOLINE = 10
  SOUND_EVENT_TELEPORT = 11
  SOUND_EVENT_DEATH = 12
  SOUND_EVENT_WIN_0 = 13
  SOUND_EVENT_WIN_1 = 14
  SOUND_EVENT_WIN_2 = 15
  SOUND_EVENT_WIN_3 = 16
  SOUND_EVENT_WIN_4 = 17
  SOUND_EVENT_WIN_5 = 18
  SOUND_EVENT_WIN_6 = 19
  SOUND_EVENT_WIN_7 = 20
  SOUND_EVENT_WIN_8 = 21
  SOUND_EVENT_WIN_9 = 22
  SOUND_EVENT_GO_AWAY = 23
  SOUND_EVENT_GO = 24
  SOUND_EVENT_EARTHQUAKE = 25
  SOUND_EVENT_CONFIRM = 26

  #----------------------------------------------------------------------------
  
  def __init__(self):
    self.sound_volume = 0.5
    self.music_volume = 0.5
   
    self.sounds = {}
    self.sounds[SoundPlayer.SOUND_EVENT_EXPLOSION] = pygame.mixer.Sound(os.path.join(Game.RESOURCE_PATH,"explosion.wav"))
    self.sounds[SoundPlayer.SOUND_EVENT_BOMB_PUT] = pygame.mixer.Sound(os.path.join(Game.RESOURCE_PATH,"bomb.wav"))
    self.sounds[SoundPlayer.SOUND_EVENT_WALK] = pygame.mixer.Sound(os.path.join(Game.RESOURCE_PATH,"footsteps.wav"))
    self.sounds[SoundPlayer.SOUND_EVENT_KICK] = pygame.mixer.Sound(os.path.join(Game.RESOURCE_PATH,"kick.wav"))
    self.sounds[SoundPlayer.SOUND_EVENT_SPRING] = pygame.mixer.Sound(os.path.join(Game.RESOURCE_PATH,"spring.wav"))
    self.sounds[SoundPlayer.SOUND_EVENT_DIARRHEA] = pygame.mixer.Sound(os.path.join(Game.RESOURCE_PATH,"fart.wav"))
    self.sounds[SoundPlayer.SOUND_EVENT_SLOW] = pygame.mixer.Sound(os.path.join(Game.RESOURCE_PATH,"slow.wav"))
    self.sounds[SoundPlayer.SOUND_EVENT_DISEASE] = pygame.mixer.Sound(os.path.join(Game.RESOURCE_PATH,"disease.wav"))
    self.sounds[SoundPlayer.SOUND_EVENT_CLICK] = pygame.mixer.Sound(os.path.join(Game.RESOURCE_PATH,"click.wav"))
    self.sounds[SoundPlayer.SOUND_EVENT_THROW] = pygame.mixer.Sound(os.path.join(Game.RESOURCE_PATH,"throw.wav"))
    self.sounds[SoundPlayer.SOUND_EVENT_TRAMPOLINE] = pygame.mixer.Sound(os.path.join(Game.RESOURCE_PATH,"trampoline.wav"))
    self.sounds[SoundPlayer.SOUND_EVENT_TELEPORT] = pygame.mixer.Sound(os.path.join(Game.RESOURCE_PATH,"teleport.wav"))
    self.sounds[SoundPlayer.SOUND_EVENT_DEATH] = pygame.mixer.Sound(os.path.join(Game.RESOURCE_PATH,"death.wav"))
    self.sounds[SoundPlayer.SOUND_EVENT_GO] = pygame.mixer.Sound(os.path.join(Game.RESOURCE_PATH,"go.wav"))
    self.sounds[SoundPlayer.SOUND_EVENT_EARTHQUAKE] = pygame.mixer.Sound(os.path.join(Game.RESOURCE_PATH,"earthquake.wav"))
    self.sounds[SoundPlayer.SOUND_EVENT_CONFIRM] = pygame.mixer.Sound(os.path.join(Game.RESOURCE_PATH,"confirm.wav"))

    self.music_filenames = [
      "music_loyalty_freak_slow_pogo.wav",
      "music_anonymous420_start_to_play.wav",
      "music_anonymous420_first_step_for_your_tech.wav",
      "music_anonymous420_echo_blues_effect.wav",
      "music_loyalty_freak_music_enby.wav"
      ]
 
    self.current_music_index = -1
    
    self.playing_walk = False
    self.kick_last_played_time = 0

  #----------------------------------------------------------------------------
     
  def play_once(self, filename):
    sound = pygame.mixer.Sound(filename)
    sound.set_volume(self.sound_volume)
    sound.play()

  #----------------------------------------------------------------------------
   
  def set_music_volume(self, new_volume):
    self.music_volume = new_volume if new_volume > Settings.SOUND_VOLUME_THRESHOLD else 0
    
    debug_log("changing music volume to " + str(self.music_volume))
    
    if new_volume > Settings.SOUND_VOLUME_THRESHOLD:
      if not pygame.mixer.music.get_busy():
        pygame.mixer.music.play()
      
      pygame.mixer.music.set_volume(new_volume)
    else:
      pygame.mixer.music.stop()

  #----------------------------------------------------------------------------
      
  def set_sound_volume(self, new_volume):
    self.sound_volume = new_volume if new_volume > Settings.SOUND_VOLUME_THRESHOLD else 0
    
    debug_log("changing sound volume to " + str(self.sound_volume))
    
    for sound in self.sounds:
      self.sounds[sound].set_volume(self.sound_volume)

  #----------------------------------------------------------------------------
   
  def change_music(self):
    while True:
      new_music_index = random.randint(0,len(self.music_filenames) - 1)
      
      if new_music_index == self.current_music_index:
        continue
      
      break
    
    self.current_music_index = new_music_index
    
    music_name = self.music_filenames[self.current_music_index]
    
    debug_log("changing music to \"" + music_name + "\"")
    
    pygame.mixer.music.stop()
    pygame.mixer.music.load(os.path.join(Game.RESOURCE_PATH,music_name))
    pygame.mixer.music.set_volume(self.music_volume)
    pygame.mixer.music.play(-1)

  #----------------------------------------------------------------------------
   
  def play_sound_event(self,sound_event):
    self.process_events([sound_event])

  #----------------------------------------------------------------------------
   
  ## Processes a list of sound events (see class constants) by playing
  #  appropriate sounds.
    
  def process_events(self, sound_event_list): 
    stop_playing_walk = True
    
    for sound_event in sound_event_list: 
      if sound_event in (                        # simple sound play
        SoundPlayer.SOUND_EVENT_EXPLOSION,
        SoundPlayer.SOUND_EVENT_CLICK,
        SoundPlayer.SOUND_EVENT_BOMB_PUT,
        SoundPlayer.SOUND_EVENT_SPRING,
        SoundPlayer.SOUND_EVENT_DIARRHEA,
        SoundPlayer.SOUND_EVENT_SLOW,
        SoundPlayer.SOUND_EVENT_DISEASE,
        SoundPlayer.SOUND_EVENT_THROW,
        SoundPlayer.SOUND_EVENT_TRAMPOLINE,
        SoundPlayer.SOUND_EVENT_TELEPORT,
        SoundPlayer.SOUND_EVENT_DEATH,
        SoundPlayer.SOUND_EVENT_GO,
        SoundPlayer.SOUND_EVENT_EARTHQUAKE,
        SoundPlayer.SOUND_EVENT_CONFIRM
        ):
        self.sounds[sound_event].play()
    
      elif sound_event == SoundPlayer.SOUND_EVENT_WALK:
        if not self.playing_walk:
          self.sounds[SoundPlayer.SOUND_EVENT_WALK].play(loops=-1)
          self.playing_walk = True
        
        stop_playing_walk = False
      elif sound_event == SoundPlayer.SOUND_EVENT_KICK:
        time_now = pygame.time.get_ticks()
        
        if time_now > self.kick_last_played_time + 200:    # wait 200 ms before playing kick sound again        
          self.sounds[SoundPlayer.SOUND_EVENT_KICK].play()
          self.kick_last_played_time = time_now
      elif SoundPlayer.SOUND_EVENT_WIN_0 <= sound_event <= SoundPlayer.SOUND_EVENT_WIN_9:
        self.play_once(os.path.join(Game.RESOURCE_PATH,"win" + str(sound_event - SoundPlayer.SOUND_EVENT_WIN_0) + ".wav"))
      
    if self.playing_walk and stop_playing_walk:
      self.sounds[SoundPlayer.SOUND_EVENT_WALK].stop()
      self.playing_walk = False
    
  #  if not self.playing_walk = False
    
#==============================================================================

class Animation(object):

  #----------------------------------------------------------------------------

  def __init__(self, filename_prefix, start_number, end_number, filename_postfix, framerate = 10):
    self.framerate = framerate
    self.frame_time = 1000 / self.framerate
    
    self.frame_images = []
    
    for i in range(start_number,end_number + 1):
      self.frame_images.append(pygame.image.load(filename_prefix + str(i) + filename_postfix))
      
    self.playing_instances = []   ##< A set of playing animations, it is a list of tuples in
                                  #  a format: (pixel_coordinates, started_playing).     

  #----------------------------------------------------------------------------

  def play(self, coordinates):
    # convert center coordinates to top left coordinates:
    
    top_left = (coordinates[0] - self.frame_images[0].get_size()[0] / 2,coordinates[1] - self.frame_images[0].get_size()[1] / 2)
    self.playing_instances.append((top_left,pygame.time.get_ticks()))

  #----------------------------------------------------------------------------
    
  def draw(self, surface):
    i = 0
    
    time_now = pygame.time.get_ticks()
    
    while True:
      if i >= len(self.playing_instances):
        break
      
      playing_instance = self.playing_instances[i]
      
      frame = int((time_now - playing_instance[1]) / self.frame_time)
      
      if frame >= len(self.frame_images):
        self.playing_instances.remove(playing_instance)
        continue
        
      surface.blit(self.frame_images[frame],playing_instance[0])
      
      i += 1

#==============================================================================

## Abstract class representing a game menu. Menu item strings can contain formatting characters:
#
#  ^htmlcolorcode - sets the text color (HTML #rrggbb format,e.g. ^#2E44BF) from here to end of line or another formatting character
    
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
    
#==============================================================================

class MainMenu(Menu):

  #----------------------------------------------------------------------------

  def __init__(self, sound_player):
    super(MainMenu,self).__init__(sound_player)
    
    self.items = [(
      "let's play!",
      "tweak some stuff",
      "what's this about",
      "run away!")]

  #----------------------------------------------------------------------------
    
  def action_pressed(self, action):
    super(MainMenu,self).action_pressed(action)
    self.prompt_if_needed((3,0))

#==============================================================================

class ResultMenu(Menu):

  #----------------------------------------------------------------------------

  def __init__(self, sound_player):
    super(ResultMenu,self).__init__(sound_player)
    
    self.items = [["I get it"]]

  #----------------------------------------------------------------------------
    
  def set_results(self, players):
    win_maximum = 0
    winner_team_numbers = []
    
    for player in players:
      if player.get_wins() > win_maximum:
        winner_team_numbers = [player.get_team_number()]
        win_maximum = player.get_wins()        
      elif player.get_wins() == win_maximum:
        winner_team_numbers.append(player.get_team_number())
    
    separator = "__________________________________________________"
    
    if len(winner_team_numbers) == 1:
      announcement_text = "Winner team is " + Renderer.colored_color_name(winner_team_numbers[0]) + "!"
    else:
      announcement_text = "Winners teams are: "
      
      first = True
      
      for winner_number in winner_team_numbers:
        if first:
          first = False
        else:
          announcement_text += ", "
          
        announcement_text += Renderer.colored_color_name(winner_team_numbers[winner_number])
    
      announcement_text += "!"
    
    self.text = announcement_text + "\n" + separator + "\n"
    
    player_number = 0
    row = 0
    column = 0
    
    # decide how many columns for different numbers of players will the table have
    columns_by_player_count = (1,2,3,2,3,3,4,4,3,5)
    table_columns = columns_by_player_count[len(players) - 1]
    
    while player_number < len(players):
      player = players[player_number]
      
      self.text += (
        Renderer.colored_color_name(player.get_number()) + " (" +
        Renderer.colored_text(player.get_team_number(),str(player.get_team_number() + 1)) + "): " +
        str(player.get_kills()) + "/" + str(player.get_wins())
        )
      
      column += 1
      
      if column >= table_columns:
        column = 0
        row += 1
        self.text += "\n"
      else:
        self.text += "     "
      
      player_number += 1
    
    self.text += "\n" + separator

#==============================================================================

#==============================================================================

#==============================================================================

#==============================================================================

#==============================================================================
    

#==============================================================================
    

#==============================================================================
from playmenu import PlayMenu
from settingsmenu import SettingsMenu
from controlsmenu import ControlsMenu
from aboutmenu import AboutMenu
from mapselectmenu import MapSelectMenu
from playsetupmenu import PlaySetupMenu
from renderer import Renderer
from ai import AI
from settings import Settings
from game import Game

if __name__ == "__main__":
  profiler = Profiler()   # profiler object is global, for simple access
  game = Game()

  if len(sys.argv) > 1: 
    if "--test" in sys.argv:       # allows to quickly init a game
      game.setup_test_game(0)
    elif "--test2" in sys.argv:
      game.setup_test_game(1)
    elif "--test3" in sys.argv:
      game.setup_test_game(2)

  game.run()

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

## Abstract class representing a game menu. Menu item strings can contain formatting characters:
#
#  ^htmlcolorcode - sets the text color (HTML #rrggbb format,e.g. ^#2E44BF) from here to end of line or another formatting character
#==============================================================================
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

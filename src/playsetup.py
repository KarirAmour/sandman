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
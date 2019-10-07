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
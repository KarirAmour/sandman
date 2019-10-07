## Info about a bomb's flight (when boxed or thrown).

class BombFlightInfo(object):

  #----------------------------------------------------------------------------

  def __init__(self):
    self.total_distance_to_travel = 0     ##< in tiles
    self.distance_travelled = 0           ##< in tiles
    self.direction = (0,0)                ##< in which direction the bomb is flying, 0, 1 or -1

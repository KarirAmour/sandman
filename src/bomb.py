from positionable import Positionable
from bombflightinfo import BombFlightInfo

class Bomb(Positionable):
  ROLLING_SPEED = 4
  FLYING_SPEED = 5
  
  BOMB_ROLLING_UP = 0
  BOMB_ROLLING_RIGHT = 1
  BOMB_ROLLING_DOWN = 2
  BOMB_ROLLING_LEFT = 3
  BOMB_FLYING = 4
  BOMB_NO_MOVEMENT = 5
  
  DETONATOR_EXPIRATION_TIME = 20000

  BOMB_EXPLODES_IN = 3000
  EXPLODES_IN_QUICK = 800     ##< for when the player has quick explosion disease

  #----------------------------------------------------------------------------
  
  def __init__(self, player):
    super(Bomb,self).__init__()
    self.time_of_existence = 0                       ##< for how long (in ms) the bomb has existed
    self.flame_length = player.get_flame_length()    ##< how far the flame will go
    self.player = player                             ##< to which player the bomb belongs
    self.explodes_in = Bomb.BOMB_EXPLODES_IN         ##< time in ms in which the bomb explodes from the time it was created (detonator_time must expire before this starts counting down)
    self.detonator_time = 0                          ##< if > 0, the bomb has a detonator on it, after expiring it becomes a regular bomb
    self.set_position(player.get_position())
    self.move_to_tile_center()
    self.has_spring = player.bombs_have_spring()
    self.movement = Bomb.BOMB_NO_MOVEMENT
    self.has_exploded = False
    self.flight_info = BombFlightInfo()

  #----------------------------------------------------------------------------
      
  ## Sends the bomb flying from its currents position to given tile (can be outside the map boundaries, will fly over the border from the other side).
    
  def send_flying(self, destination_tile_coords):
    self.movement = Bomb.BOMB_FLYING

    current_tile = self.get_tile_position()
    self.flight_info.distance_travelled = 0

    axis = 1 if current_tile[0] == destination_tile_coords[0] else 0

    self.flight_info.total_distance_to_travel = abs(current_tile[axis] - destination_tile_coords[axis])
    self.flight_info.direction = [0,0]
    self.flight_info.direction[axis] = -1 if current_tile[axis] > destination_tile_coords[axis] else 1
    self.flight_info.direction = tuple(self.flight_info.direction)

    destination_tile_coords = (destination_tile_coords[0] % GameMap.MAP_WIDTH,destination_tile_coords[1] % GameMap.MAP_HEIGHT)
    self.move_to_tile_center(destination_tile_coords)

  #----------------------------------------------------------------------------

  def has_detonator(self):
    return self.detonator_time > 0 and self.time_of_existence < Bomb.DETONATOR_EXPIRATION_TIME

  #----------------------------------------------------------------------------

  ## Returns a time until the bomb explodes by itself.

  def time_until_explosion(self):
    return self.explodes_in + self.detonator_time - self.time_of_existence

  #----------------------------------------------------------------------------

  def explodes(self):
    if not self.has_exploded:
      self.player.bomb_exploded()
      self.has_exploded = True


## Something that has a float position on the map.

class Positionable(object):

  #----------------------------------------------------------------------------

  def __init__(self):
    self.position = (0.0,0.0)

  #----------------------------------------------------------------------------

  def set_position(self,position):
    self.position = position

  #----------------------------------------------------------------------------

  def get_position(self):
    return self.position

  #----------------------------------------------------------------------------
  
  def get_neighbour_tile_coordinates(self):
    tile_coordinates = self.get_tile_position()
    
    top = (tile_coordinates[0],tile_coordinates[1] - 1)
    right = (tile_coordinates[0] + 1,tile_coordinates[1])
    down = (tile_coordinates[0],tile_coordinates[1] + 1)
    left = (tile_coordinates[0] - 1,tile_coordinates[1])  
    
    return (top,right,down,left)

  #----------------------------------------------------------------------------
  
  def get_tile_position(self):
    return Positionable.position_to_tile(self.position)

  #----------------------------------------------------------------------------
  
  ## Moves the object to center of tile (if not specified, objects current tile is used).
  
  def move_to_tile_center(self, tile_coordinates=None):
    if tile_coordinates != None:
      self.position = tile_coordinates
    
    self.position = (math.floor(self.position[0]) + 0.5,math.floor(self.position[1]) + 0.5)

  #----------------------------------------------------------------------------

  ## Converts float position to integer tile position.

  @staticmethod
  def position_to_tile(position):
    return (int(math.floor(position[0])),int(math.floor(position[1])))

  #----------------------------------------------------------------------------
  
  def is_near_tile_center(self):
    position_within_tile = (self.position[0] % 1,self.position[1] % 1)
    
    limit = 0.2
    limit2 = 1.0 - limit
    
    return (limit < position_within_tile[0] < limit2) and (limit < position_within_tile[1] < limit2)

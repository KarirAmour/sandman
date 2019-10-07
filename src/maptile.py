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
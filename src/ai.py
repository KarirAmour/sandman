    
class AI(object):
  REPEAT_ACTIONS = (100,300)    ##< In order not to compute actions with every single call to
                                #   play(), actions will be stored in self.outputs and repeated
                                #   for next random(REPEAT_ACTIONS[0],REPEAT_ACTIONS[1]) ms - saves
                                #   CPU time and prevents jerky AI movement.

  #----------------------------------------------------------------------------
  
  def __init__(self, player, game_map):
    self.player = player
    self.game_map = game_map
    
    self.outputs = []           ##< holds currently active outputs
    self.recompute_compute_actions_on = 0
    
    self.do_nothing = False     ##< this can turn AI off for debugging purposes
    self.didnt_move_since = 0 

  #----------------------------------------------------------------------------
   
  def tile_is_escapable(self, tile_coordinates):
    if not self.game_map.tile_is_walkable(tile_coordinates) or self.game_map.tile_has_flame(tile_coordinates):
      return False
    
    tile = self.game_map.get_tile_at(tile_coordinates)
    
    if tile.special_object == MapTile.SPECIAL_OBJECT_LAVA:
      return False
    
    return True

  #----------------------------------------------------------------------------
   
  ## Returns a two-number tuple of x, y coordinates, where x and y are
  #  either -1, 0 or 1, indicating a rough general direction in which to
  #  move in order to prevent AI from walking in nonsensical direction (towards
  #  outside of the map etc.).
   
  def decide_general_direction(self):
    players = self.game_map.get_players()
    
    enemy_players = filter(lambda p: p.is_enemy(self.player) and not p.is_dead(), players)
    enemy_player = enemy_players[0] if len(enemy_players) > 0 else self.player
            
    my_tile_position = self.player.get_tile_position()
    another_player_tile_position = enemy_player.get_tile_position()

    dx = another_player_tile_position[0] - my_tile_position[0]
    dy = another_player_tile_position[1] - my_tile_position[1]
    
    dx = min(max(-1,dx),1)
    dy = min(max(-1,dy),1)
    
    return (dx,dy)
   
  #----------------------------------------------------------------------------
 
  ## Rates all 4 directions from a specified tile (up, right, down, left) with a number
  #  that says how many possible safe tiles are there accesible in that direction in
  #  case a bomb is present on the specified tile. A tuple of four integers is returned
  #  with numbers for each direction - the higher number, the better it is to run to
  #  safety in that direction. 0 means there is no escape and running in that direction
  #  means death.
    
  def rate_bomb_escape_directions(self, tile_coordinates):
                    #          up       right   down   left 
    axis_directions =          ((0,-1), (1,0),  (0,1), (-1,0))
    perpendicular_directions = ((1,0),  (0,1),  (1,0), (0,1))

    result = [0,0,0,0]
    
    for direction in (0,1,2,3):
      for i in range(1,self.player.get_flame_length() + 2):
        axis_tile = (tile_coordinates[0] + i * axis_directions[direction][0],tile_coordinates[1] + i * axis_directions[direction][1])
        
        if not self.tile_is_escapable(axis_tile):
          break
        
        perpendicular_tile1 = (axis_tile[0] + perpendicular_directions[direction][0],axis_tile[1] + perpendicular_directions[direction][1])
        perpendicular_tile2 = (axis_tile[0] - perpendicular_directions[direction][0],axis_tile[1] - perpendicular_directions[direction][1])

        if i > self.player.get_flame_length() and self.game_map.get_danger_value(axis_tile) >= GameMap.SAFE_DANGER_VALUE:
          result[direction] += 1
          
        if self.tile_is_escapable(perpendicular_tile1) and self.game_map.get_danger_value(perpendicular_tile1) >= GameMap.SAFE_DANGER_VALUE:
          result[direction] += 1
          
        if self.tile_is_escapable(perpendicular_tile2) and self.game_map.get_danger_value(perpendicular_tile2) >= GameMap.SAFE_DANGER_VALUE:  
          result[direction] += 1
    
    return tuple(result)

  #----------------------------------------------------------------------------
    
  ## Returns an integer score in range 0 - 100 for given file (100 = good, 0 = bad).
    
  def rate_tile(self, tile_coordinates):
    danger = self.game_map.get_danger_value(tile_coordinates)
    
    if danger == 0:
      return 0
    
    score = 0
    
    if danger < 1000:
      score = 20
    elif danger < 2500:
      score = 40
    else:
      score = 60
    
    tile_item = self.game_map.get_tile_at(tile_coordinates).item
    
    if tile_item != None:
      if tile_item != GameMap.ITEM_DISEASE:
        score += 20
      else:
        score -= 10
        
    top = (tile_coordinates[0],tile_coordinates[1] - 1)
    right = (tile_coordinates[0] + 1,tile_coordinates[1])
    down = (tile_coordinates[0],tile_coordinates[1] + 1)
    left = (tile_coordinates[0] - 1,tile_coordinates[1])
    
    if self.game_map.tile_has_lava(top) or self.game_map.tile_has_lava(right) or self.game_map.tile_has_lava(down) or self.game_map.tile_has_lava(left):
      score -= 5    # don't go near lava
    
    if self.game_map.tile_has_bomb(tile_coordinates):
      if not self.player.can_box():
        score -= 5
    
    return score

  #----------------------------------------------------------------------------
    
  def is_trapped(self):
    neighbour_tiles = self.player.get_neighbour_tile_coordinates()
  
    trapped = True
    
    for tile_coordinates in neighbour_tiles:
      if self.game_map.tile_is_walkable(tile_coordinates):
        trapped = False
        break
    
    return trapped

  #----------------------------------------------------------------------------
    
  def number_of_blocks_next_to_tile(self, tile_coordinates):
    count = 0
    
    for tile_offset in ((0,-1),(1,0),(0,1),(-1,0)):  # for each neigbour file
      helper_tile = self.game_map.get_tile_at((tile_coordinates[0] + tile_offset[0],tile_coordinates[1] + tile_offset[1]))
      
      if helper_tile != None and helper_tile.kind == MapTile.TILE_BLOCK:
        count += 1
      
    return count

  #----------------------------------------------------------------------------
    
  ## Returns a tuple in format: (nearby_enemies, nearby allies).
    
  def players_nearby(self):
    current_position = self.player.get_tile_position()
    
    allies = 0
    enemies = 0
    
    for player in self.game_map.get_players():
      if player.is_dead() or player == self.player:
        continue
      
      player_position = player.get_tile_position()
      
      if abs(current_position[0] - player_position[0]) <= 1 and abs(current_position[1] - player_position[1]) <= 1:
        if player.is_enemy(self.player):
          enemies += 1
        else:
          allies += 1
      
    return (enemies,allies)

  #----------------------------------------------------------------------------
    
  ## Decides what moves to make and returns a list of event in the same
  #  format as PlayerKeyMaps.get_current_actions().
    
  def play(self):
    if self.do_nothing or self.player.is_dead():
      return []
    
    current_time = self.game_map.get_map_time()
    
    if current_time < self.recompute_compute_actions_on or self.player.get_state() == Player.STATE_IN_AIR or self.player.get_state() == Player.STATE_TELEPORTING:
      return self.outputs          # only repeat actions
     
    # start decisions here:
    
    # moevement decisions:
    
    self.outputs = []
    
    current_tile = self.player.get_tile_position()
    trapped = self.is_trapped()
    escape_direction_ratings = self.rate_bomb_escape_directions(current_tile)
    
    # consider possible actions and find the one with biggest score:
    
    if trapped:
      # in case the player is trapped spin randomly and press box in hope to free itself
      chosen_movement_action = random.choice((PlayerKeyMaps.ACTION_UP,PlayerKeyMaps.ACTION_RIGHT,PlayerKeyMaps.ACTION_DOWN,PlayerKeyMaps.ACTION_LEFT))
    elif self.game_map.tile_has_bomb(current_tile):
      # standing on a bomb, find a way to escape
      
      # find maximum
      best_rating = escape_direction_ratings[0]
      best_action = PlayerKeyMaps.ACTION_UP
      
      if escape_direction_ratings[1] > best_rating:
        best_rating = escape_direction_ratings[1]
        best_action = PlayerKeyMaps.ACTION_RIGHT
        
      if escape_direction_ratings[2] > best_rating:
        best_rating = escape_direction_ratings[2]
        best_action = PlayerKeyMaps.ACTION_DOWN
      
      if escape_direction_ratings[3] > best_rating:
        best_rating = escape_direction_ratings[3]
        best_action = PlayerKeyMaps.ACTION_LEFT
      
      chosen_movement_action = best_action 
    else:             # not standing on a bomb
      
      # should I not move?
      
      maximum_score = self.rate_tile(current_tile)
      best_direction_actions = [None]
    
      general_direction = self.decide_general_direction()

                       # up                     # right                     # down                     # left
      tile_increment  = ((0,-1),                  (1,0),                      (0,1),                     (-1,0))
      action =          (PlayerKeyMaps.ACTION_UP, PlayerKeyMaps.ACTION_RIGHT, PlayerKeyMaps.ACTION_DOWN, PlayerKeyMaps.ACTION_LEFT)
    
      # should I move up, right, down or left?
    
      for direction in (0,1,2,3):
        score = self.rate_tile((current_tile[0] + tile_increment[direction][0],current_tile[1] + tile_increment[direction][1]))  
      
        # count in the general direction
        extra_score = 0
        
        if tile_increment[direction][0] == general_direction[0]:
          extra_score += 2
        
        if tile_increment[direction][1] == general_direction[1]:
          extra_score += 2
          
        score += extra_score
      
        if score > maximum_score:
          maximum_score = score
          best_direction_actions = [action[direction]]
        elif score == maximum_score:
          best_direction_actions.append(action[direction])
      
      chosen_movement_action = random.choice(best_direction_actions)
      
    if chosen_movement_action != None:
      if self.player.get_disease() == Player.DISEASE_REVERSE_CONTROLS:
        chosen_movement_action = PlayerKeyMaps.get_opposite_action(chosen_movement_action)
      
      self.outputs.append((self.player.get_number(),chosen_movement_action))
      
      self.didnt_move_since = self.game_map.get_map_time()

    if self.game_map.get_map_time() - self.didnt_move_since > 10000:   # didn't move for 10 seconds or more => force move
      chosen_movement_action = random.choice((PlayerKeyMaps.ACTION_UP,PlayerKeyMaps.ACTION_RIGHT,PlayerKeyMaps.ACTION_DOWN,PlayerKeyMaps.ACTION_LEFT))
      self.outputs.append((self.player.get_number(),chosen_movement_action))
      
    # bomb decisions
    
    bomb_laid = False
    
    if self.game_map.tile_has_bomb(current_tile):
      # should I throw?
      
      if self.player.can_throw() and max(escape_direction_ratings) == 0:
        self.outputs.append((self.player.get_number(),PlayerKeyMaps.ACTION_BOMB_DOUBLE))
    elif self.player.get_bombs_left() > 0 and (self.player.can_throw() or self.game_map.get_danger_value(current_tile) > 2000 and max(escape_direction_ratings) > 0): 
      # should I lay bomb?
      
      chance_to_put_bomb = 100    # one in how many
      
      players_near = self.players_nearby()
      
      if players_near[0] > 0 and players_near[1] == 0:  # enemy nearby and no ally nearby
        chance_to_put_bomb = 5
      else:
        block_tile_ratio = self.game_map.get_number_of_block_tiles() / float(GameMap.MAP_WIDTH * GameMap.MAP_HEIGHT)

        if block_tile_ratio < 0.4:   # if there is not many tiles left, put bombs more often
          chance_to_put_bomb = 80
        elif block_tile_ratio < 0.2:
          chance_to_put_bomb = 20
      
      number_of_block_neighbours = self.number_of_blocks_next_to_tile(current_tile)
     
      if number_of_block_neighbours == 1:
        chance_to_put_bomb = 3
      elif number_of_block_neighbours == 2 or number_of_block_neighbours == 3:
        chance_to_put_bomb = 2
      
      do_lay_bomb = random.randint(0,chance_to_put_bomb) == 0
      
      if do_lay_bomb:
        bomb_laid = True
        
        if random.randint(0,2) == 0 and self.should_lay_multibomb(chosen_movement_action):  # lay a single bomb or multibomb?
          self.outputs.append((self.player.get_number(),PlayerKeyMaps.ACTION_BOMB_DOUBLE))
        else:
          self.outputs.append((self.player.get_number(),PlayerKeyMaps.ACTION_BOMB))
  
    # should I box?
    
    if self.player.can_box() and not self.player.detonator_is_active():
      if trapped or self.game_map.tile_has_bomb(self.player.get_forward_tile_position()):
        self.outputs.append((self.player.get_number(),PlayerKeyMaps.ACTION_SPECIAL))
  
    if bomb_laid:   # if bomb was laid, the outputs must be recomputed fast in order to prevent laying bombs to other tiles
      self.recompute_compute_actions_on = current_time + 10
    else:
      self.recompute_compute_actions_on = current_time + random.randint(AI.REPEAT_ACTIONS[0],AI.REPEAT_ACTIONS[1])

    # should I detonate the detonator?
    
    if self.player.detonator_is_active():
      if random.randint(0,2) == 0 and self.game_map.get_danger_value(current_tile) >= GameMap.SAFE_DANGER_VALUE:
        self.outputs.append((self.player.get_number(),PlayerKeyMaps.ACTION_SPECIAL))
  
    return self.outputs

  #----------------------------------------------------------------------------

  def should_lay_multibomb(self, movement_action):
    if self.player.can_throw():    # multibomb not possible with throwing glove
      return False
    
    multibomb_count = self.player.get_multibomb_count()
    
    if multibomb_count > 1:        # multibomb possible
      current_tile = self.player.get_tile_position()

      player_direction = movement_action if movement_action != None else self.player.get_direction_number()

      # by laying multibomb one of the escape routes will be cut off, let's check
      # if there would be any escape routes left
      
      escape_direction_ratings = list(self.rate_bomb_escape_directions(current_tile))
      escape_direction_ratings[player_direction] = 0
      
      if max(escape_direction_ratings) == 0:
        return False

      direction_vector = self.player.get_direction_vector()
      
      multibomb_safe = True
      
      for i in range(multibomb_count):
        if not self.game_map.tile_is_walkable(current_tile) or not self.game_map.tile_is_withing_map(current_tile):
          break
        
        if self.game_map.get_danger_value(current_tile) < 3000 or self.game_map.tile_has_lava(current_tile):
          multibomb_safe = False
          break
        
        current_tile = (current_tile[0] + direction_vector[0],current_tile[1] + direction_vector[1])
        
      if multibomb_safe:
        return True
      
    return False

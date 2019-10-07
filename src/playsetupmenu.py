from menu import Menu

class PlaySetupMenu(Menu):

  #----------------------------------------------------------------------------

  def __init__(self, sound_player, play_setup):
    super(PlaySetupMenu,self).__init__(sound_player)
    self.selected_item = (0,1)
    self.play_setup = play_setup
    self.update_items()

  #----------------------------------------------------------------------------
    
  def update_items(self):
    self.items = [[],[],["games: " + str(self.play_setup.get_number_of_games())]]
    
    dark_grey = (50,50,50)
      
    self.items[0].append("back")
    self.items[1].append("next")
         
    for i in range(10):
      slot_color = Renderer.COLOR_RGB_VALUES[i] if i != Game.COLOR_BLACK else dark_grey  # black with black border not visible, use dark grey
      
      self.items[0].append(Renderer.colored_text(i,str(i + 1)) + ": ")
      
      slot = self.play_setup.get_slots()[i]
      
      if slot == None:
        self.items[0][-1] += "-"
        self.items[1].append("-")
      else:
        team_color = Renderer.COLOR_RGB_VALUES[slot[1]] if slot[1] != Game.COLOR_BLACK else dark_grey
        self.items[0][-1] += ("player " + str(slot[0] + 1)) if slot[0] >= 0 else "AI"
        self.items[1].append(Renderer.colored_text(slot[1],str(slot[1] + 1)))    # team number

  #----------------------------------------------------------------------------
 
  def action_pressed(self, action):
    super(PlaySetupMenu,self).action_pressed(action)
    
    if action == PlayerKeyMaps.ACTION_UP:
      if self.selected_item == (0,2):
        self.play_setup.increase_number_of_games()  
        self.state = Menu.MENU_STATE_SELECTING
    elif action == PlayerKeyMaps.ACTION_DOWN:
      if self.selected_item == (0,2):
        self.play_setup.decrease_number_of_games()
        self.state = Menu.MENU_STATE_SELECTING
    elif self.state == Menu.MENU_STATE_CONFIRM:  
      if self.selected_item == (0,2):
        self.play_setup.increase_number_of_games()
        self.state = Menu.MENU_STATE_SELECTING
    
      if self.selected_item[0] > 0:  # override behaviour for confirm button
        slots = self.play_setup.get_slots()
        slot = slots[self.selected_item[0] - 1]
      
        if self.selected_item[1] == 0:
          # changing players
        
          if slot == None:
            new_value = -1
          else:
            new_value = slot[0] + 1
          
          slots[self.selected_item[0] - 1] = (new_value,slot[1] if slot != None else self.selected_item[0] - 1) if new_value <= 3 else None  
        else:
          # changing teams
        
          if slot != None:
            slots[self.selected_item[0] - 1] = (slot[0],(slot[1] + 1) % 10)
      
        self.state = Menu.MENU_STATE_SELECTING
      
    self.update_items()
 
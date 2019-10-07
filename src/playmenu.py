from menu import Menu
    

class PlayMenu(Menu):

  #----------------------------------------------------------------------------

  def __init__(self,sound_player):
    super(PlayMenu,self).__init__(sound_player)
    self.items = [("resume","to main menu")]

  #----------------------------------------------------------------------------
  
  def action_pressed(self, action):
    super(PlayMenu,self).action_pressed(action)
    self.prompt_if_needed((1,0))

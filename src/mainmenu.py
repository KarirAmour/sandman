from menu import Menu

class MainMenu(Menu):

  #----------------------------------------------------------------------------

  def __init__(self, sound_player):
    super(MainMenu,self).__init__(sound_player)
    
    self.items = [(
      "let's play!",
      "tweak some stuff",
      "what's this about",
      "run away!")]

  #----------------------------------------------------------------------------
    
  def action_pressed(self, action):
    super(MainMenu,self).action_pressed(action)
    self.prompt_if_needed((3,0))


        
from menu import Menu
from config import VERSION_STR

class AboutMenu(Menu):

  #----------------------------------------------------------------------------

  def __init__(self,sound_player):
    super(AboutMenu, self).__init__(sound_player) 
    self.text = ("^#2E44BFBombman^#FFFFFF - free Bomberman clone, ^#4EF259version " + VERSION_STR + "\n"
                 "Miloslav \"tastyfish\" Ciz, 2016\n\n"
                 "This game is free software, published under CC0 1.0.\n")
    self.items = [["ok, nice, back"]]

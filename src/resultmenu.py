from menu import Menu

class ResultMenu(Menu):

  #----------------------------------------------------------------------------

  def __init__(self, sound_player):
    super(ResultMenu,self).__init__(sound_player)
    
    self.items = [["I get it"]]

  #----------------------------------------------------------------------------
    
  def set_results(self, players):
    win_maximum = 0
    winner_team_numbers = []
    
    for player in players:
      if player.get_wins() > win_maximum:
        winner_team_numbers = [player.get_team_number()]
        win_maximum = player.get_wins()        
      elif player.get_wins() == win_maximum:
        winner_team_numbers.append(player.get_team_number())
    
    separator = "__________________________________________________"
    
    if len(winner_team_numbers) == 1:
      announcement_text = "Winner team is " + Renderer.colored_color_name(winner_team_numbers[0]) + "!"
    else:
      announcement_text = "Winners teams are: "
      
      first = True
      
      for winner_number in winner_team_numbers:
        if first:
          first = False
        else:
          announcement_text += ", "
          
        announcement_text += Renderer.colored_color_name(winner_team_numbers[winner_number])
    
      announcement_text += "!"
    
    self.text = announcement_text + "\n" + separator + "\n"
    
    player_number = 0
    row = 0
    column = 0
    
    # decide how many columns for different numbers of players will the table have
    columns_by_player_count = (1,2,3,2,3,3,4,4,3,5)
    table_columns = columns_by_player_count[len(players) - 1]
    
    while player_number < len(players):
      player = players[player_number]
      
      self.text += (
        Renderer.colored_color_name(player.get_number()) + " (" +
        Renderer.colored_text(player.get_team_number(),str(player.get_team_number() + 1)) + "): " +
        str(player.get_kills()) + "/" + str(player.get_wins())
        )
      
      column += 1
      
      if column >= table_columns:
        column = 0
        row += 1
        self.text += "\n"
      else:
        self.text += "     "
      
      player_number += 1
    
    self.text += "\n" + separator


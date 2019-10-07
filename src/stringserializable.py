## Something that can be saved/loaded to/from string.
  
class StringSerializable(object):

  #----------------------------------------------------------------------------

  def save_to_string(self):
    return ""

  #----------------------------------------------------------------------------
  
  def load_from_string(self, input_string):
    return

  #----------------------------------------------------------------------------
  
  def save_to_file(self, filename):
    text_file = open(filename,"w")
    text_file.write(self.save_to_string())
    text_file.close()

  #----------------------------------------------------------------------------
  
  def load_from_file(self, filename):
    with open(filename,"r") as text_file:
      self.load_from_string(text_file.read())

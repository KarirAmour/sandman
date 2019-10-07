
class Animation(object):

  #----------------------------------------------------------------------------

  def __init__(self, filename_prefix, start_number, end_number, filename_postfix, framerate = 10):
    self.framerate = framerate
    self.frame_time = 1000 / self.framerate
    
    self.frame_images = []
    
    for i in range(start_number,end_number + 1):
      self.frame_images.append(pygame.image.load(filename_prefix + str(i) + filename_postfix))
      
    self.playing_instances = []   ##< A set of playing animations, it is a list of tuples in
                                  #  a format: (pixel_coordinates, started_playing).     

  #----------------------------------------------------------------------------

  def play(self, coordinates):
    # convert center coordinates to top left coordinates:
    
    top_left = (coordinates[0] - self.frame_images[0].get_size()[0] / 2,coordinates[1] - self.frame_images[0].get_size()[1] / 2)
    self.playing_instances.append((top_left,pygame.time.get_ticks()))

  #----------------------------------------------------------------------------
    
  def draw(self, surface):
    i = 0
    
    time_now = pygame.time.get_ticks()
    
    while True:
      if i >= len(self.playing_instances):
        break
      
      playing_instance = self.playing_instances[i]
      
      frame = int((time_now - playing_instance[1]) / self.frame_time)
      
      if frame >= len(self.frame_images):
        self.playing_instances.remove(playing_instance)
        continue
        
      surface.blit(self.frame_images[frame],playing_instance[0])
      
      i += 1


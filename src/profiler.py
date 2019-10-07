from debug import DEBUG_PROFILING, DEBUG_FPS, DEBUG_VERBOSE, debug_log

class Profiler(object):
  SHOW_LAST = 10

  #----------------------------------------------------------------------------

  def __init__(self):
    self.sections = {}
    
  #----------------------------------------------------------------------------

  def measure_start(self, section_name):
    if not DEBUG_PROFILING:
      return
      
    if not (section_name in self.sections):
      self.sections[section_name] = [0.0 for i in range(Profiler.SHOW_LAST)]

    section_values = self.sections[section_name]
        
    section_values[0] -= pygame.time.get_ticks()

  #----------------------------------------------------------------------------

  def measure_stop(self, section_name):
    if not DEBUG_PROFILING:
      return
      
    if not section_name in self.sections:
      return
  
    section_values = self.sections[section_name]
    
    section_values[0] += pygame.time.get_ticks()

  #----------------------------------------------------------------------------
     
  def end_of_frame(self):
    for section_name in self.sections:
      section_values = self.sections[section_name]
      section_values.pop()
      section_values.insert(0,0)

  #----------------------------------------------------------------------------
    
  def get_profile_string(self):
    result = "PROFILING INFO:"
    
    section_names = list(self.sections.keys())
    section_names.sort()
    
    for section_name in section_names:
      result += "\n" + section_name.ljust(25) + ": "
      
      section_values = self.sections[section_name]
      
      for i in range(len(section_values)):
        result += str(section_values[i]).ljust(5)
        
      result += " AVG: " + str(sum(section_values) / float(len(section_values)))
        
    return result

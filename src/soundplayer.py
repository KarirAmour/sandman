class SoundPlayer(object):
  # sound events used by other classes to tell soundplayer what to play
  
  SOUND_EVENT_EXPLOSION = 0
  SOUND_EVENT_BOMB_PUT = 1
  SOUND_EVENT_WALK = 2
  SOUND_EVENT_KICK = 3
  SOUND_EVENT_DIARRHEA = 4
  SOUND_EVENT_SPRING = 5
  SOUND_EVENT_SLOW = 6
  SOUND_EVENT_DISEASE = 7
  SOUND_EVENT_CLICK = 8
  SOUND_EVENT_THROW = 9
  SOUND_EVENT_TRAMPOLINE = 10
  SOUND_EVENT_TELEPORT = 11
  SOUND_EVENT_DEATH = 12
  SOUND_EVENT_WIN_0 = 13
  SOUND_EVENT_WIN_1 = 14
  SOUND_EVENT_WIN_2 = 15
  SOUND_EVENT_WIN_3 = 16
  SOUND_EVENT_WIN_4 = 17
  SOUND_EVENT_WIN_5 = 18
  SOUND_EVENT_WIN_6 = 19
  SOUND_EVENT_WIN_7 = 20
  SOUND_EVENT_WIN_8 = 21
  SOUND_EVENT_WIN_9 = 22
  SOUND_EVENT_GO_AWAY = 23
  SOUND_EVENT_GO = 24
  SOUND_EVENT_EARTHQUAKE = 25
  SOUND_EVENT_CONFIRM = 26

  #----------------------------------------------------------------------------
  
  def __init__(self):
    self.sound_volume = 0.5
    self.music_volume = 0.5
   
    self.sounds = {}
    self.sounds[SoundPlayer.SOUND_EVENT_EXPLOSION] = pygame.mixer.Sound(os.path.join(Game.RESOURCE_PATH,"explosion.wav"))
    self.sounds[SoundPlayer.SOUND_EVENT_BOMB_PUT] = pygame.mixer.Sound(os.path.join(Game.RESOURCE_PATH,"bomb.wav"))
    self.sounds[SoundPlayer.SOUND_EVENT_WALK] = pygame.mixer.Sound(os.path.join(Game.RESOURCE_PATH,"footsteps.wav"))
    self.sounds[SoundPlayer.SOUND_EVENT_KICK] = pygame.mixer.Sound(os.path.join(Game.RESOURCE_PATH,"kick.wav"))
    self.sounds[SoundPlayer.SOUND_EVENT_SPRING] = pygame.mixer.Sound(os.path.join(Game.RESOURCE_PATH,"spring.wav"))
    self.sounds[SoundPlayer.SOUND_EVENT_DIARRHEA] = pygame.mixer.Sound(os.path.join(Game.RESOURCE_PATH,"fart.wav"))
    self.sounds[SoundPlayer.SOUND_EVENT_SLOW] = pygame.mixer.Sound(os.path.join(Game.RESOURCE_PATH,"slow.wav"))
    self.sounds[SoundPlayer.SOUND_EVENT_DISEASE] = pygame.mixer.Sound(os.path.join(Game.RESOURCE_PATH,"disease.wav"))
    self.sounds[SoundPlayer.SOUND_EVENT_CLICK] = pygame.mixer.Sound(os.path.join(Game.RESOURCE_PATH,"click.wav"))
    self.sounds[SoundPlayer.SOUND_EVENT_THROW] = pygame.mixer.Sound(os.path.join(Game.RESOURCE_PATH,"throw.wav"))
    self.sounds[SoundPlayer.SOUND_EVENT_TRAMPOLINE] = pygame.mixer.Sound(os.path.join(Game.RESOURCE_PATH,"trampoline.wav"))
    self.sounds[SoundPlayer.SOUND_EVENT_TELEPORT] = pygame.mixer.Sound(os.path.join(Game.RESOURCE_PATH,"teleport.wav"))
    self.sounds[SoundPlayer.SOUND_EVENT_DEATH] = pygame.mixer.Sound(os.path.join(Game.RESOURCE_PATH,"death.wav"))
    self.sounds[SoundPlayer.SOUND_EVENT_GO] = pygame.mixer.Sound(os.path.join(Game.RESOURCE_PATH,"go.wav"))
    self.sounds[SoundPlayer.SOUND_EVENT_EARTHQUAKE] = pygame.mixer.Sound(os.path.join(Game.RESOURCE_PATH,"earthquake.wav"))
    self.sounds[SoundPlayer.SOUND_EVENT_CONFIRM] = pygame.mixer.Sound(os.path.join(Game.RESOURCE_PATH,"confirm.wav"))

    self.music_filenames = [
      "music_loyalty_freak_slow_pogo.wav",
      "music_anonymous420_start_to_play.wav",
      "music_anonymous420_first_step_for_your_tech.wav",
      "music_anonymous420_echo_blues_effect.wav",
      "music_loyalty_freak_music_enby.wav"
      ]
 
    self.current_music_index = -1
    
    self.playing_walk = False
    self.kick_last_played_time = 0

  #----------------------------------------------------------------------------
     
  def play_once(self, filename):
    sound = pygame.mixer.Sound(filename)
    sound.set_volume(self.sound_volume)
    sound.play()

  #----------------------------------------------------------------------------
   
  def set_music_volume(self, new_volume):
    self.music_volume = new_volume if new_volume > Settings.SOUND_VOLUME_THRESHOLD else 0
    
    debug_log("changing music volume to " + str(self.music_volume))
    
    if new_volume > Settings.SOUND_VOLUME_THRESHOLD:
      if not pygame.mixer.music.get_busy():
        pygame.mixer.music.play()
      
      pygame.mixer.music.set_volume(new_volume)
    else:
      pygame.mixer.music.stop()

  #----------------------------------------------------------------------------
      
  def set_sound_volume(self, new_volume):
    self.sound_volume = new_volume if new_volume > Settings.SOUND_VOLUME_THRESHOLD else 0
    
    debug_log("changing sound volume to " + str(self.sound_volume))
    
    for sound in self.sounds:
      self.sounds[sound].set_volume(self.sound_volume)

  #----------------------------------------------------------------------------
   
  def change_music(self):
    while True:
      new_music_index = random.randint(0,len(self.music_filenames) - 1)
      
      if new_music_index == self.current_music_index:
        continue
      
      break
    
    self.current_music_index = new_music_index
    
    music_name = self.music_filenames[self.current_music_index]
    
    debug_log("changing music to \"" + music_name + "\"")
    
    pygame.mixer.music.stop()
    pygame.mixer.music.load(os.path.join(Game.RESOURCE_PATH,music_name))
    pygame.mixer.music.set_volume(self.music_volume)
    pygame.mixer.music.play(-1)

  #----------------------------------------------------------------------------
   
  def play_sound_event(self,sound_event):
    self.process_events([sound_event])

  #----------------------------------------------------------------------------
   
  ## Processes a list of sound events (see class constants) by playing
  #  appropriate sounds.
    
  def process_events(self, sound_event_list): 
    stop_playing_walk = True
    
    for sound_event in sound_event_list: 
      if sound_event in (                        # simple sound play
        SoundPlayer.SOUND_EVENT_EXPLOSION,
        SoundPlayer.SOUND_EVENT_CLICK,
        SoundPlayer.SOUND_EVENT_BOMB_PUT,
        SoundPlayer.SOUND_EVENT_SPRING,
        SoundPlayer.SOUND_EVENT_DIARRHEA,
        SoundPlayer.SOUND_EVENT_SLOW,
        SoundPlayer.SOUND_EVENT_DISEASE,
        SoundPlayer.SOUND_EVENT_THROW,
        SoundPlayer.SOUND_EVENT_TRAMPOLINE,
        SoundPlayer.SOUND_EVENT_TELEPORT,
        SoundPlayer.SOUND_EVENT_DEATH,
        SoundPlayer.SOUND_EVENT_GO,
        SoundPlayer.SOUND_EVENT_EARTHQUAKE,
        SoundPlayer.SOUND_EVENT_CONFIRM
        ):
        self.sounds[sound_event].play()
    
      elif sound_event == SoundPlayer.SOUND_EVENT_WALK:
        if not self.playing_walk:
          self.sounds[SoundPlayer.SOUND_EVENT_WALK].play(loops=-1)
          self.playing_walk = True
        
        stop_playing_walk = False
      elif sound_event == SoundPlayer.SOUND_EVENT_KICK:
        time_now = pygame.time.get_ticks()
        
        if time_now > self.kick_last_played_time + 200:    # wait 200 ms before playing kick sound again        
          self.sounds[SoundPlayer.SOUND_EVENT_KICK].play()
          self.kick_last_played_time = time_now
      elif SoundPlayer.SOUND_EVENT_WIN_0 <= sound_event <= SoundPlayer.SOUND_EVENT_WIN_9:
        self.play_once(os.path.join(Game.RESOURCE_PATH,"win" + str(sound_event - SoundPlayer.SOUND_EVENT_WIN_0) + ".wav"))
      
    if self.playing_walk and stop_playing_walk:
      self.sounds[SoundPlayer.SOUND_EVENT_WALK].stop()
      self.playing_walk = False
    
  #  if not self.playing_walk = False
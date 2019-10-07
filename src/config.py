
# Game Settings
VERSION_STR = "0.95"

RESOURCE_PATH = "resources"
MAP_PATH = "maps"

NUMBER_OF_CONTROLLED_PLAYERS = 4    ##< maximum number of non-AI players on one PC

COLOR_NAMES = [
    "white",
    "black",
    "red",
    "blue",
    "green",
    "cyan",
    "yellow",
    "orange",
    "brown",
    "purple"
]

CHEAT_PARTY = 0
CHEAT_ALL_ITEMS = 1
CHEAT_PLAYER_IMMORTAL = 2


# Menu Settings
MENU_STATE_SELECTING = 0                ##< still selecting an item
MENU_STATE_CONFIRM = 1                  ##< menu has been confirmed
MENU_STATE_CANCEL = 2                   ##< menu has been cancelled
MENU_STATE_CONFIRM_PROMPT = 3           ##< prompting an action
MENU_MAX_ITEMS_VISIBLE = 11 # Used in Renderer for max items before scrolling enabled


# Renderer Settings
ANIMATION_EVENT_EXPLOSION = 0
ANIMATION_EVENT_RIP = 1
ANIMATION_EVENT_SKELETION = 2
ANIMATION_EVENT_DISEASE_CLOUD = 3
ANIMATION_EVENT_DIE = 4
  
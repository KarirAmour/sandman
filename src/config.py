
from enum import Enum

# Game Settings
VERSION_STR = "0.95"

SETTINGS_FILE_PATH = "settings.txt"
RESOURCE_PATH = "resources"
MAP_PATH = "maps"

NUMBER_OF_CONTROLLED_PLAYERS = 4    ##< maximum number of non-AI players on one PC

# colors used for players and teams
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


SAFE_DANGER_VALUE = 5000     ##< time in ms, used in danger map to indicate safe tile

GIVE_AWAY_DELAY = 3000       ##< after how many ms the items of dead players will be given away

START_GAME_AFTER = 2500      ##< delay in ms before the game begins

EARTHQUAKE_DURATION = 10000


class CheatCode(Enum):
    CHEAT_PARTY = 0
    CHEAT_ALL_ITEMS = 1
    CHEAT_PLAYER_IMMORTAL = 2


class MenuConfig(Enum):

    MENU_STATE_SELECTING = 0                ##< still selecting an item
    MENU_STATE_CONFIRM = 1                  ##< menu has been confirmed
    MENU_STATE_CANCEL = 2                   ##< menu has been cancelled
    MENU_STATE_CONFIRM_PROMPT = 3           ##< prompting an action
    MENU_MAX_ITEMS_VISIBLE = 11 # Used in Renderer for max items before scrolling enabled


class RendererConfig(Enum):

    ANIMATION_EVENT_EXPLOSION = 0
    ANIMATION_EVENT_RIP = 1
    ANIMATION_EVENT_SKELETION = 2
    ANIMATION_EVENT_DISEASE_CLOUD = 3
    ANIMATION_EVENT_DIE = 4


class MapConfig(Enum):

    MAP_TILE_WIDTH = 50              ##< tile width in pixels
    MAP_TILE_HEIGHT = 45             ##< tile height in pixels
    MAP_TILE_HALF_WIDTH = MAP_TILE_WIDTH / 2
    MAP_TILE_HALF_HEIGHT = MAP_TILE_HEIGHT / 2

    MAP_BORDER_WIDTH = 37

    MAP_WIDTH = 15
    MAP_HEIGHT = 11

    WALL_MARGIN_HORIZONTAL = 0.2
    WALL_MARGIN_VERTICAL = 0.4


class Collision(Enum):
    COLLISION_BORDER_UP = 0       ##< position is inside upper border with non-walkable tile
    COLLISION_BORDER_RIGHT = 1    ##< position is inside right border with non-walkable tile
    COLLISION_BORDER_DOWN = 2     ##< position is inside bottom border with non-walkable tile
    COLLISION_BORDER_LEFT = 3     ##< position is inside left border with non-walkable tile
    COLLISION_TOTAL = 4           ##< position is inside non-walkable tile
    COLLISION_NONE = 5            ##< no collision


class GameState(Enum):

    STATE_WAITING_TO_PLAY = 0    ##< players can't do anything yet
    STATE_PLAYING = 1            ##< game is being played
    STATE_FINISHING = 2          ##< game is over but the map is still being updated for a while after
    STATE_GAME_OVER = 3          ##< the game is definitely over and should no longer be updated

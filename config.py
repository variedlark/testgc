from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
ASSETS_DIR = PROJECT_ROOT / "assets"
MUSIC_DIR = ASSETS_DIR / "music"
SFX_DIR = ASSETS_DIR / "sfx"
GENERATED_AUDIO_DIR = ASSETS_DIR / "generated"
LEVELS_DIR = PROJECT_ROOT / "levels" / "level_data"
SAVE_FILE = PROJECT_ROOT / "data" / "savegame.json"

WINDOW_TITLE = "Pulse Runner"
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
WINDOW_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

FPS_LIMIT = 120
FIXED_TIMESTEP = 1.0 / 120.0
MAX_SUBSTEPS = 8

GROUND_Y = 620
CEILING_Y = 80

PLAYER_SIZE = 42
PLAYER_START_X = 220
PLAYER_SPAWN_Y = GROUND_Y - PLAYER_SIZE

GRAVITY = 2800.0
JUMP_VELOCITY = 935.0
ORB_BOOST_VELOCITY = 1025.0
PAD_BOOST_VELOCITY = 1160.0
MAX_FALL_SPEED = 1500.0
ROTATION_SPEED = 420.0

BASE_SCROLL_SPEED = 360.0
SPEED_MULTIPLIERS = {
    "slow": 0.85,
    "normal": 1.0,
    "fast": 1.25,
    "faster": 1.45,
}

PLAYER_HITBOX_SCALE = 0.78
LEVEL_END_BUFFER = 320

DEFAULT_SETTINGS = {
    "music_volume": 0.60,
    "sfx_volume": 0.85,
    "show_fps": False,
}

LEVEL_FILE_ORDER = [
    "level_01.json",
    "level_02.json",
    "level_03.json",
    "level_04.json",
    "level_05.json",
]

COLORS = {
    "bg": (11, 15, 33),
    "bg_alt": (21, 30, 56),
    "panel": (17, 25, 48),
    "panel_alt": (27, 37, 67),
    "player": (120, 234, 255),
    "player_trail": (170, 249, 255),
    "ground": (45, 61, 95),
    "ground_glow": (90, 120, 185),
    "block": (113, 124, 255),
    "spike": (255, 96, 110),
    "orb": (255, 223, 121),
    "pad": (129, 239, 167),
    "portal_speed": (255, 170, 79),
    "portal_gravity": (171, 125, 255),
    "text": (238, 243, 255),
    "text_dim": (169, 181, 216),
    "success": (125, 255, 181),
    "danger": (255, 104, 132),
}

FONT_MAIN = "freesansbold.ttf"

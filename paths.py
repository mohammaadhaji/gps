from pathlib import Path
from os.path import join


CURRENT_FILE_DIR  = Path(__file__).parent.absolute()
TILES_DIR         = join(CURRENT_FILE_DIR, 'map/')
IMAGES_DIR        = join(CURRENT_FILE_DIR, 'ui/images')
MAIN_WINDOW_UI    = join(CURRENT_FILE_DIR, 'ui/main.ui')
MAP_SETTINGS_UI   = join(CURRENT_FILE_DIR, 'ui/mapSettings.ui')
HTML_FILE         = join(CURRENT_FILE_DIR, 'index.html')
CONFIG_FILE       = join(CURRENT_FILE_DIR, 'configs/configs')
ONLINE_TILES      = join(CURRENT_FILE_DIR, 'configs/OnlineTiles.txt')
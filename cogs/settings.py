# DNI
import os
if "SHEPBOT_ENV" not in os.environ:
    os.environ["SHEPBOT_ENV"] = "stable"

# --- Bot Settings ---
TOKEN = "XXXXXXXXXX" # Public token - removed for security 
PREFIX = ">"

# If you're not using two different bots for testing control, ignore these two lines
PROD_TOKEN = "XXXXXXXXXX" # Testing token - removed for security
PROD_PREFIX = "!"

LOW_DATA_MODE = False # You can manually set this to True, which will increase cooldown times for certain commands

# --- Wavelink Settings ---
WL_HOST = "XXXXXXXXXX" # Wavelink host - removed for security
WL_PORT = 443
WL_REST_URI = "https://" + WL_HOST  # Don't change this unless the REST URI is different
WL_PASSWORD = "XXXXXXXXXX" # Wavelink password - removed for security

# --- Starboard Settings ---
REACTION_NAME = "⭐"
MONGO_URI = "mongodb+srv://XXXXXXXXXX" # MongoDB URI - removed for security
STARBOARD_CHANNEL = 1009245232782659686

# --- Other Settings ---
PRIVATE_BOT = True
OWNER_ID = 424991711564136448 # Edit if you're selfhosting
EXTRA_ANNOYING = False # Use at your own discretion
ROLES_CHANNEL = 698656364603637790
ANNOUNCEMENTS_CHANNEL = 696814593753874464 
LOG_CHANNEL = 1018562685111128064
HALLOWEEN_CHANNEL = 766707126755917915

# --- Private Settings ---
# Ignore if PRIVATE_BOT is False
MAIN_CHANNEL = 982671777085931540
TEST_CHANNEL = 982488812208930869
EXTRA_RESPONSES = ["Bark", "Grrr", "Growl"] # Add custom responses to pings here

# --- Spotify Settings ---
# Ignore if PRIVATE_BOT is False
SPOTIFY_CLIENT_ID = "XXXXXXXXXX" # Spotify Client ID - removed for security
SPOTIFY_CLIENT_SECRET = "XXXXXXXXXX" # Spotify Client Secret - removed for security
PLAYLIST_LINK = "XXXXXXXXXX" # Spotify Playlist URL - removed for security

# --- Twitter Webhook Settings ---
WEBHOOK_URL = "XXXXXXXXXX" # Twitter webhook URL - removed for security
BEARER_TOKEN = "XXXXXXXXXX" # Twitter Bearer Token - removed for security

# --- Overrides ---
if os.environ["SHEPBOT_ENV"] == "testing":
    MAIN_CHANNEL = 982488812208930869 
    STARBOARD_CHANNEL = 1009199252586627105 # The channel ID of the starboard channel
    ROLES_CHANNEL = 1013140513886576661
    ANNOUNCEMENTS_CHANNEL = 1013140530890285168
    LOG_CHANNEL = 1018626851008151592
    HALLOWEEN_CHANNEL = 1021567923627765770
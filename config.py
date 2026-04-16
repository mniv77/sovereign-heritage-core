# config.py
# FINAL CLEAN VERSION - NO IMPORTS NEEDED

# --- DATABASE SETTINGS ---
# We are hardcoding these to guarantee the connection works.
DB_HOST = "MeirNiv.mysql.pythonanywhere-services.com"
DB_USER = "MeirNiv"
DB_NAME = "MeirNiv$default"
DB_PASSWORD = "mayyam28"  # <--- REPLACE THIS WITH YOUR REAL PASSWORD

# Broker API Keys (Add these exact names)
GEMINI_KEY = "account-rdW60WwOf2mMVwLNfUud"
GEMINI_SECRET = "2f7Kdu9WF5DtdnyBvcMH2Gn2crsF"



# --- TRADING SETTINGS ---
ALPACA_KEY = "PK2HFODS3RW3PWLCPG2K"
ALPACA_SECRET = "Vs09krhOfWs58GwWGezYzlow7O34pF8MTrcm0rb5"
PAPER_TRADING = True
LOG_FILE = "data/aimn_crypto_trading.log"


# --- SYSTEM DEFAULTS (The Mapper) ---
# This tells the scripts: "When I ask for API_KEY, give me the Gemini one."
API_KEY = GEMINI_KEY
API_SECRET = GEMINI_SECRET




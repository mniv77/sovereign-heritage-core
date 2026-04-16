# db_config.py
# Sovereign Heritage Core - Master Database Selector
# This file governs the "Talk" between the Server and your PC.

# --- MASTER DEVELOPMENT SWITCH ---
# Set to 'REMOTE' for PythonAnywhere Database (Cloud Hosting)
# Set to 'LOCAL' for Home PC Database (The Sovereign Node via Bridge)
DATABASE_TARGET = "REMOTE" 

# 1. REMOTE (CLOUD) PARAMETERS - PythonAnywhere Default
REMOTE_HOST = "MeirNiv.mysql.pythonanywhere-services.com"
REMOTE_USER = "MeirNiv"
REMOTE_PASS = "mayyam28"
REMOTE_NAME = "MeirNiv$v"

# 2. LOCAL (HOME NODE) PARAMETERS - PC/XAMPP
# Note: These are used when DATABASE_TARGET is set to "LOCAL"
LOCAL_HOST = "127.0.0.1"
LOCAL_USER = "aimn_node_service"
LOCAL_PASS = "SERVICE_SECRET_PROTOCOL_V4_8822"
LOCAL_NAME = "aimn_sovereign"

# --- DYNAMIC EXPORT LOGIC ---
# This section resolves the NameError by ensuring DATABASE_TARGET exists.
if DATABASE_TARGET == "LOCAL":
    DB_HOST = LOCAL_HOST
    DB_USER = LOCAL_USER
    DB_PASSWORD = LOCAL_PASS
    DB_NAME = LOCAL_NAME
    DB_PORT = 3306
    NODE_STATUS = "Sovereign PC Active"
else:
    DB_HOST = REMOTE_HOST
    DB_USER = REMOTE_USER
    DB_PASSWORD = REMOTE_PASS
    DB_NAME = REMOTE_NAME
    DB_PORT = 3306
    NODE_STATUS = "Cloud Mirror Active"

# The system uses these variables in app.py to establish the connection.
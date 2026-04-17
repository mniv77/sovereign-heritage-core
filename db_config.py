import os

DATABASE_TARGET = os.environ.get("DATABASE_TARGET", "REMOTE").upper()

REMOTE_HOST = os.environ.get("REMOTE_HOST", "")
REMOTE_USER = os.environ.get("REMOTE_USER", "")
REMOTE_PASS = os.environ.get("REMOTE_PASS", "")
REMOTE_NAME = os.environ.get("REMOTE_NAME", "")

LOCAL_HOST = os.environ.get("LOCAL_HOST", "127.0.0.1")
LOCAL_USER = os.environ.get("LOCAL_USER", "")
LOCAL_PASS = os.environ.get("LOCAL_PASS", "")
LOCAL_NAME = os.environ.get("LOCAL_NAME", "")

if DATABASE_TARGET == "LOCAL":
    DB_HOST = LOCAL_HOST
    DB_USER = LOCAL_USER
    DB_PASSWORD = LOCAL_PASS
    DB_NAME = LOCAL_NAME
    DB_PORT = int(os.environ.get("LOCAL_PORT", "3306"))
    NODE_STATUS = "Sovereign PC Active"
else:
    DB_HOST = REMOTE_HOST
    DB_USER = REMOTE_USER
    DB_PASSWORD = REMOTE_PASS
    DB_NAME = REMOTE_NAME
    DB_PORT = int(os.environ.get("REMOTE_PORT", "3306"))
    NODE_STATUS = "Cloud Mirror Active"

#!/usr/bin/python

SITE_PATH = "/home/james/public_wsgi/"

VERBOSE = 1

LOG_FILE = SITE_PATH + ".episema.log"
DB_FILE = SITE_PATH + ".episema.db"

ACCOUNT_DB = ".accounts.db"
PLAYER_DB = ".players.db"
WORLD_DB = ".world.db"

ACCOUNT_TABLE = "accounts"
LOCATION_TABLE = "player_location"
#LEVELS = ["seas", "islands", "regions", "locations"]
PAR_ID = "parentID"

LEVELS = ["islands", "regions", "locations"]
IDS = ["iid", "rid", "lid"]

# pid is player id.
# sid is sea id.
# iid is island id.
# A player's pid refers to their row id from the accounts table
TABLES = {"accounts": ["username", "password"],
          "player_location": ["pid", "level", "id"], # Add x and y, remove id?
          "seas": ["name"],
          "islands":  ["name", "parentID", "x", "y"],
          "regions":  ["name", "parentID", "x", "y"],
          "locations": ["name", "parentID", "x", "y"],
         }

VALUES = [("accounts", "James", "password"),
          ("player_location", 1, 1, 1),

          ("seas", "Aegean sea"),
          ("seas", "Myrtoan sea"),

          ("islands", "Nisida", 1, 1, 1),
          ("islands", "Antiparos", 1, 3, 5),
          ("islands", "Paros", 1, 3, 3),
          ("islands", "Milos", 2, 3, 4),
          ("islands", "Antimilos", 2, 1, 1),

          ("regions", "Village", 1, 3, 3),
          ("regions", "Forest", 1, 5, 5),
          ("regions", "Port", 1, 2, 3),
          ("regions", "Hydra's Den", 2, 1, 1),
          ("regions", "Some place", 3, 1, 1),
          ("regions", "Fountain", 4, 1, 1),
          ("regions", "Temple", 5, 2, 2),

          ("locations", "Uncle's House", 1, 3, 3),
          ("locations", "Library", 1, 4, 5),
          ("locations", "Border", 2, 1, 4),
          ("locations", "Dock", 3, 1, 1),
          ("locations", "Hydra", 4, 1, 1),
         ]

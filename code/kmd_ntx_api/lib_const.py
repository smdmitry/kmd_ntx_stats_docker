import os
import os
import sys
import time
import json
import logging
import requests
from dotenv import load_dotenv
from django.contrib import messages
from os.path import expanduser, dirname, realpath

import kmd_ntx_api.lib_struct as struct
from kmd_ntx_api.notary_pubkeys import get_notary_pubkeys

load_dotenv()
OTHER_SERVER = os.getenv("OTHER_SERVER") # IP / domain of the remote server
THIS_SERVER = os.getenv("THIS_SERVER")   # IP / domain of the local server
BASIC_PW = os.getenv("BASIC_PW")         # Simple pw for restricting views during testing

# LOGGING CONST
logger = logging.getLogger("mylogger")

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}


# TEMPORAL CONST
INTERVALS = (
    ('wks', 604800),    # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hrs', 3600),      # 60 * 60
    ('mins', 60),
    ('sec', 1),
)

SINCE_INTERVALS = {
    "hour": 60 * 60,
    "day": 24 * 60 * 60,
    "week": 7 * 24 * 60 * 60,
    "fortnight": 14 * 24 * 60 * 60,
    "month": 31 * 24 * 60 * 60,
    "year": 365 * 24 * 60 * 60,
}


# KMD REWARDS CONSTANTS
KOMODO_ENDOFERA = 7777777
LOCKTIME_THRESHOLD = 500000000
MIN_SATOSHIS = 1000000000
ONE_MONTH_CAP_HARDFORK = 1000000
ONE_HOUR = 60
ONE_MONTH = 31 * 24 * 60
ONE_YEAR = 365 * 24 * 60
DEVISOR = 10512000


HOME = expanduser('~')
SCRIPT_PATH = dirname(realpath(sys.argv[0]))

# COLORS
COLORS = {
    "BLACK": "#000",
    "RED": "#DC0333",
    "OTHER_COIN_COLOR": "#c58c47",
    "MAIN_COLOR": "#115621",
    "THIRD_PARTY_COLOR": "#2b53ad",
    "LT_BLUE": "#00E2FF",
    "AR_REGION": "#3C819D",
    "EU_REGION": "#B3BA41",
    "NA_REGION": "#13BF3E",
    "SH_REGION": "#B93429",
    "DEV_REGION": "#5D38CA"
}


# OPCODES CONST
OP_DUP = b'76'
OP_HASH160 = b'a9'
OP_EQUALVERIFY = b'88'
OP_CHECKSIG = b'ac'


# DPOW CONST
noMoM = ['CHIPS', 'GAME', 'HUSH3', 'EMC2', 'GIN', 'GLEEC-OLD', 'AYA', 'MCL', 'VRSC']
RETIRED_COINS = ["HUSH3", "RFOX", "PGT", "STBL", "PBC"]

EXCLUDE_DECODE_OPRET_COINS = []

SEASONS_INFO = {
    "Season_1": {
        "start_block": 1,
        "end_block": 813999,
        "start_time": 1473793441,
        "end_time": 1530921600
    },
    "Season_2": {
        "start_block": 814000,
        "end_block": 1443999,
        "start_time": 1530921600,
        "end_time": 1563148799
    },
    "Season_3": {
        "start_block": 1444000,
        "end_block": 1921999,
        "start_time": 1563148800,
        "end_time": 1592146799
    },
    "Season_4": {
        "start_block": 1922000,
        "end_block": 2436999,
        "post_season_end_block": 3436999,
        "start_time": 1592146800,
        "end_time": 1617364800,
        "post_season_end_time": 1623682799
    },
    "Season_5": {
        "start_block": 2437000,
        "end_block": 3437000,
        "start_time": 1623682800,
        "end_time": 1656077852
    },
    "Season_6": {
        "start_block": 2963330,
        "end_block": 4437000,
        "start_time": 1656077853,
        "end_time": 2147483647
    },
    "Season_7": {
        "start_block": 3484958,
        "end_block": 4484958,
        "start_time": 1688132253,
        "end_time": 1988132253
    },
    "VOTE2022_Testnet": {
        "start_block": 2903777,
        "end_block": 2923160,
        "start_time": 1651622400,
        "end_time": 1653436800,
        "notaries": [],
        "coins": ["RICK", "MORTY"],
        "servers": {
            "Main": {
                "coins": ["RICK", "MORTY"],
                "addresses": {},
                "epochs": {}
            }                        
        }    
    }
}

for _season in SEASONS_INFO:
    pubkeys = get_notary_pubkeys()
    if _season in pubkeys:
        SEASONS_INFO[_season].update({
            "regions": struct.default_regions_info()
        })
        _notaries = list(pubkeys[_season]["Main"].keys())
        _notaries.sort()
        SEASONS_INFO[_season].update({
            "notaries": _notaries
        })
        for _notary in _notaries:
            _region = _notary.split("_")[-1]
            if _region not in SEASONS_INFO[_season]["regions"].keys():
                _region = "DEV"
            SEASONS_INFO[_season]["regions"][_region]['nodes'].append(_notary)

POSTSEASON = False

for _season in SEASONS_INFO:
    if _season.find("Testnet") == -1:
        if SEASONS_INFO[_season]["start_time"] < time.time():
            if "post_season_end_time" in SEASONS_INFO[_season]:
                if SEASONS_INFO[_season]["post_season_end_time"] > time.time():
                    POSTSEASON = True
                    SEASON = _season
            elif SEASONS_INFO[_season]["end_time"] > time.time():
                    SEASON = _season


POSTSEASON = False

VOTE_YEAR = "VOTE2022"

VOTE_PERIODS = {
    "VOTE2021": {
        "max_block": 20492
    },
    "VOTE2022": {
        "max_block": 20492,
        "max_blocktime": 1653523199
    }
}

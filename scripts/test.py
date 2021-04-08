#!/usr/bin/env python3
from models import mined_row

import logging
import logging.handlers

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

sql = "SELECT block_height, block_time, block_datetime, \
              value, address, name, txid, season \
       FROM mined WHERE \
       season = 'Season_5_Testnet';"
CURSOR.execute(sql)
results = CURSOR.fetchall()
for item in results:
    row = mined_row()
    row.block_height = item["block_height"]
    row.block_time = item["block_time"]
    row.block_datetime = item["block_datetime"]
    row.value = item["value"]
    row.address = item["address"]
    row.name = item["name"]
    row.txid = item["txid"]
    row.season = item["season"]
    row.update()

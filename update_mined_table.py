#!/usr/bin/env python3
import os
import json
import binascii
import logging
import logging.handlers
from notary_pubkeys import known_addresses
from rpclib import def_credentials
from os.path import expanduser
from dotenv import load_dotenv
import psycopg2

def get_max_col_val_in_table(col, table):
    sql = "SELECT MAX("+col+") FROM "+table+";"
    cursor.execute(sql)
    last_block = cursor.fetchone()
    logger.info("Last block recorded was "+str(last_block[0]))
    return last_block[0]

def add_row_to_mined_tbl(row_data):
    try:
        sql = "INSERT INTO mined"
        sql = sql+" (block, value, address, name)"
        sql = sql+" VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, row_data)
        conn.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        return 0


def get_miners(start, end):
    count = 0
    for block in range(start, end):
        for tx in rpc["KMD"].getblock(str(block), 2)['tx']:
            if 'coinbase' in tx['vin'][0]:
                if 'addresses' in tx['vout'][0]['scriptPubKey']:
                    address = tx['vout'][0]['scriptPubKey']['addresses'][0]
                    if address in known_addresses:
                        name = known_addresses[address]
                    else:
                        name = "UNKNOWN"
                else:
                    address = "N/A"
                    name = "non-standard"

                value = tx['vout'][0]['value']
                logger.info(str(value)+" KMD mined by ["+name+"] in block "+str(block))
                row_data = (block, value, address, name)
                count += add_row_to_mined_tbl(row_data)
    logger.info(str(count)+" records added to table")

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
load_dotenv()

conn = psycopg2.connect(
  host='localhost',
  user='postgres',
  password='postgres',
  port = "7654",
  database='postgres'
)
cursor = conn.cursor()

rpc = {}
rpc["KMD"] = def_credentials("KMD")

ntx_data = {}
ntx_addr = 'RXL3YXG2ceaB6C5hfJcN4fvmLH2C34knhA'
try:
    startblock = get_max_col_val_in_table("block", "mined")-1
except:
    startblock = 1444000 # season start block
endblock = 7113400 # season end block (or tip if mid season)
tip = int(rpc["KMD"].getblockcount())
#startblock = tip - 2000
if endblock > tip:
    endblock = tip

get_miners(startblock, endblock)
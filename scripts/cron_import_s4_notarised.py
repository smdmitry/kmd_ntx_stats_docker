#!/usr/bin/env python3
import json
import time
import logging
import logging.handlers
import requests
from lib_const import NOTARY_BTC_ADDRESSES, OTHER_SERVER
from lib_notary import get_new_notary_txids, get_season_from_addresses, get_notarised_data
from models import notarised_row
from lib_const import *
from lib_api import get_btc_tx_info
from lib_table_select import get_existing_notarised_txids, get_notarised_chains

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# seasons = get_notarised_seasons()

season = "Season_4"
chains = get_notarised_chains(season)

i = 0
for chain in chains:

    i += 1
    logger.info(f">>> Importing {chain} for {season} {i}/{len(chains)}")

    existing_notarised_txids = get_existing_notarised_txids(chain, season)
    logger.info(f"existing_notarised_txids: {len(existing_notarised_txids)}")

    import_txids_url = f"{OTHER_SERVER}/api/info/chain_notarisation_txid_list?chain={chain}&season={season}"
    import_txids = requests.get(import_txids_url).json()["notarisation_txid_list"]
    logger.info(f"import_txids: {len(import_txids)}")

    logger.info(f"Processing ETA: {0.03*len(import_txids)} sec")
    time.sleep(0.02)
    
    new_txids = list(set(import_txids)-set(existing_notarised_txids))
    logger.info(f"new_txids: {len(new_txids)}")

    j = 0
    for txid in new_txids:
        j += 1
        logger.info(f">>> Importing {txid} {j}/{len(new_txids)}")
        txid_url = f"{OTHER_SERVER}/api/info/notarisation_txid?txid={txid}"
        time.sleep(0.02)
        r = requests.get(txid_url)
        try:
            txid_info = r.json()
            row = notarised_row()
            row.chain = txid_info["chain"]
            row.block_height = txid_info["block_height"]
            row.block_time = txid_info["block_time"]
            row.block_datetime = txid_info["block_datetime"]
            row.block_hash = txid_info["block_hash"]
            row.notaries = txid_info["notaries"]
            if len(txid_info["notary_addresses"]) == 0:
                if row.chain == "BTC":
                    url = f"{THIS_SERVER}/api/info/nn_btc_txid?txid={txid}"
                    local_info = requests.get(url).json()["results"][0]
                    local_addresses = []
                    for item in local_info:
                        if item["input_index"] != -1:
                            local_addresses.append(item["address"])
                    row.notary_addresses = local_addresses
                    row.season, row.server = get_season_from_addresses(row.notary_addresses, row.block_time, "BTC", "BTC", txid, row.notaries)
                    #tx_info = get_btc_tx_info(txid)
                    #row.notary_addresses = tx_info['addresses']
                    #row.season, row.server = get_season_from_addresses(row.notary_addresses, row.block_time, "BTC", "BTC", txid, row.notaries)
                elif row.chain == "LTC":
                    tx_info = get_ltc_tx_info(txid)
                    row.notary_addresses = tx_info['addresses']
                    row.season, row.server = get_season_from_addresses(row.notary_addresses, row.block_time, "LTC", "LTC", txid, row.notaries)
                else:
                    row_data = get_notarised_data(txid)
                    row.notary_addresses = row_data[6]
                    row.season = row_data[11]
                    row.server = row_data[12]                
            else:
                row.notary_addresses = txid_info["notary_addresses"]
                row.season = txid_info["season"]
                row.server = txid_info["server"]

            row.ac_ntx_blockhash = txid_info["ac_ntx_blockhash"]
            row.ac_ntx_height = txid_info["ac_ntx_height"]
            row.txid = txid_info["txid"]
            row.opret = txid_info["opret"]
            row.score_value = txid_info["score_value"]
            row.scored = txid_info["scored"]
            row.btc_validated = txid_info["btc_validated"]
            row.update()
        except Exception as e:
            logger.error(e)
            logger.error(f"Something wrong with API? {txid_url}")

CURSOR.close()
CONN.close()

'''
                runtime = int(time.time()-start)
                pct = round(i/num_unrecorded_KMD_txids*100,3)
                est_end = int(100/pct*runtime)
                if row.season == "Season_5_Testnet":
                    logger.info(f"{row.season} NTX {row.notaries}")
                logger.info(str(pct)+"% :"+str(i)+"/"+str(num_unrecorded_KMD_txids)+
                         " records added to db ["+str(runtime)+"/"+str(est_end)+" sec]")
'''
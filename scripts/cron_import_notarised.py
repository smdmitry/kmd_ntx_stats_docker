#!/usr/bin/env python3
import json
import time
import random
import requests
from lib_notary import *
from models import notarised_row, get_chain_epoch_score_at, get_chain_epoch_at, last_notarised_row
from lib_const import *
from lib_api import get_btc_tx_info
from lib_table_select import get_existing_notarised_txids, get_notarised_chains, get_notarised_seasons


def import_ntx(season, server, chain):
    existing_notarised_txids = get_existing_notarised_txids(chain, season, server)
    logger.info(f"existing_notarised_txids: {len(existing_notarised_txids)}")

    import_txids_url = f"{OTHER_SERVER}/api/info/notarisation_txid_list?season={season}&server={server}&chain={chain}"
    import_txids = requests.get(import_txids_url).json()["results"]
    logger.info(f"import_txids: {len(import_txids)}")

    new_txids = list(set(import_txids)-set(existing_notarised_txids))
    logger.info(f"new_txids: {len(new_txids)}")

    logger.info(f"Processing ETA: {0.03*len(new_txids)} sec")
    time.sleep(0.02)
    
    j = 0
    for txid in new_txids:
        j += 1
        logger.info(f">>> Importing {txid} {j}/{len(new_txids)}")
        txid_url = f"{OTHER_SERVER}/api/info/notarised_txid?txid={txid}"
        time.sleep(0.02)
        r = requests.get(txid_url)
        try:
            txid_info_resp = r.json()["results"]
            for txid_info in txid_info_resp:
                ntx_row = notarised_row()
                ntx_row.chain = txid_info["chain"]
                ntx_row.block_height = txid_info["block_height"]
                ntx_row.block_time = txid_info["block_time"]
                ntx_row.block_datetime = txid_info["block_datetime"]
                ntx_row.block_hash = txid_info["block_hash"]
                ntx_row.notaries = txid_info["notaries"]
                ntx_row.ac_ntx_blockhash = txid_info["ac_ntx_blockhash"]
                ntx_row.ac_ntx_height = txid_info["ac_ntx_height"]
                ntx_row.txid = txid_info["txid"]
                ntx_row.opret = txid_info["opret"]
                ntx_row.epoch = txid_info["epoch"]
                ntx_row.btc_validated = txid_info["btc_validated"]

                if len(txid_info["notary_addresses"]) == 0:

                    if ntx_row.chain == "BTC":
                        url = f"{THIS_SERVER}/api/info/notary_btc_txid?txid={txid}"
                        local_info = requests.get(url).json()["results"]
                        local_addresses = []
                        for item in local_info:
                            if item["input_index"] != -1:
                                local_addresses.append(item["address"])
                        ntx_row.notary_addresses = local_addresses
                        ntx_row.season, ntx_row.server = get_season_from_addresses(ntx_row.notary_addresses, ntx_row.block_time, "BTC", "BTC", txid, ntx_row.notaries)

                    elif ntx_row.chain == "LTC":
                        url = f"{THIS_SERVER}/api/info/notary_ltc_txid?txid={txid}"
                        local_info = requests.get(url).json()["results"]
                        local_addresses = []
                        for item in local_info:
                            if item["input_index"] != -1:
                                local_addresses.append(item["address"])
                        ntx_row.notary_addresses = local_addresses
                        ntx_row.season, ntx_row.server = get_season_from_addresses(ntx_row.notary_addresses, ntx_row.block_time, "LTC", "LTC", txid, ntx_row.notaries)

                    else:
                        row_data = get_notarised_data(txid)
                        ntx_row.notary_addresses = row_data[6]
                        ntx_row.season = row_data[11]
                        ntx_row.server = row_data[12]                
                        ntx_row.season, ntx_row.server = get_season_from_addresses(ntx_row.notary_addresses, ntx_row.block_time)
                        
                else:
                    ntx_row.notary_addresses = txid_info["notary_addresses"]
                    ntx_row.season = txid_info["season"]
                    ntx_row.server = txid_info["server"]

                if ntx_row.chain == "GLEEC":
                    ntx_row.server = get_gleec_ntx_server(ntx_row.txid)

                ntx_row.score_value = get_chain_epoch_score_at(ntx_row.season, ntx_row.server, ntx_row.chain, int(ntx_row.block_time))
                ntx_row.epoch = get_chain_epoch_at(ntx_row.season, ntx_row.server, ntx_row.chain, int(ntx_row.block_time))
                if ntx_row.score_value > 0:
                    ntx_row.scored = True
                else:
                    ntx_row.scored = False
                ntx_row.btc_validated = "N/A"

                ntx_row.update()
        except Exception as e:
            logger.error(e)
            logger.error(f"Something wrong with API? {txid_url}")


def import_last_ntx(season, server, notary):
    import_last_ntx_url = f"{OTHER_SERVER}/api/table/last_notarised?season={season}&server={server}&notary={notary}"
    import_last_ntx = requests.get(import_last_ntx_url).json()["results"]
    for import_item in import_last_ntx:
        chain = import_item["chain"]
        logger.info(f">>> [import_last_ntx] checking {season} {server} {notary} {chain}")
        
        local_last_ntx_url = f"{THIS_SERVER}/api/table/last_notarised?season={season}&server={server}&notary={notary}&chain={chain}"
        local_last_ntx = requests.get(local_last_ntx_url).json()["results"]

        logger.info(f">>> [import_last_ntx] {server} {server} {notary} {chain} local records: {len(local_last_ntx)}")
        if len(local_last_ntx) > 0:
            for local_item in local_last_ntx:
                local_height = local_item["block_height"]
                logger.info(f">>> [import_last_ntx] {season} {server} {notary} {chain} local block height: {local_height}")
        else:
            logger.info(f">>> [import_last_ntx] no local info for {season} {server} {notary} {chain}")
            local_height = 0


        import_height = import_item["block_height"]        
        if import_height > local_height:
            logger.info(f">>> [import_last_ntx] updating {season} {server} {chain} {notary}")
            row = last_notarised_row()
            row.notary = notary
            row.chain = import_item["chain"]
            row.txid = import_item["txid"]
            row.block_height = import_item["block_height"]
            row.block_time = import_item["block_time"]
            row.season = import_item["season"]
            row.server = import_item["server"]
            row.update()
        else:
            logger.info(f">>> [import_last_ntx] not updating {season} {server} {chain} {notary}, local block is fresher")




if __name__ == "__main__":

    seasons = get_notarised_seasons()

    for season in seasons:
        if season not in ["Season_1", "Season_2", "Season_3", "Unofficial"]: 
            season_notaries = list(NOTARY_PUBKEYS[season].keys())
            season_notaries.sort()
            servers = get_notarised_servers(season)
            for server in servers:
                for notary in season_notaries:
                    import_last_ntx(season, server, notary)

                chains = get_notarised_chains(season, server)
                i = 0
                while len(chains) > 0:
                    chain = random.choice(chains)
                    i += 1
                    logger.info(f">>> Importing {chain} for {season} {server} ({i} processed, {len(chains)} remaining )")
                    import_ntx(season, server, chain)
                    chains.remove(chain)


    CURSOR.close()
    CONN.close()
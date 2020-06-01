#!/usr/bin/env python3
import time
import requests
import table_lib
import logging
import logging.handlers
import notary_lib

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/NotaryNodes/master/season4/elected_nn_social.json")
nn_social = r.json()

conn = table_lib.connect_db()
cursor = conn.cursor()

season = "Season_4"
for notary in notary_lib.notary_pubkeys['Season_4']:
    row_list = [notary]
    notary_name = notary.split("_")[0]
    for region in nn_social[notary_name]:
        row_list = [notary+"_"+region]
        for social in ['twitter', 'youtube', 'discord', 'telegram', 'github', 'keybase', 'website', 'icon']:
            if social in nn_social[notary_name]:
                row_list.append(nn_social[notary_name][social])
            else:
                row_list.append("")
        row_list.append(season)
        row_data = tuple(row_list)

        table_lib.update_nn_social_tbl(conn, cursor, row_data)
    
season = "Season_3"
for notary in notary_lib.notary_pubkeys['Season_3.5']:
    row_list = [notary]
    notary_name = notary.split("_")[0]
    for social in ['twitter', 'youtube', 'discord', 'telegram', 'github', 'keybase', 'website', 'icon']:
        if notary_name in nn_social: 
            if social in nn_social[notary_name]:
                row_list.append(nn_social[notary_name][social])
            else:
                row_list.append("")
        else:
            row_list = [notary, '', '', '', '', '', '', '', '']
    row_list.append(season)
    row_data = tuple(row_list)

    table_lib.update_nn_social_tbl(conn, cursor, row_data)

cursor.close()

conn.close()

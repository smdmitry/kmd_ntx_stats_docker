#!/usr/bin/env python3
import logging
import logging.handlers
import requests
from lib_notary import update_ntx_tenure
from lib_table_select import get_notarised_chains, get_notarised_seasons, get_notarised_servers

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

notarised_seasons = get_notarised_seasons()

for season in notarised_seasons:

	for server in get_notarised_servers(season):

		notarised_chains = get_notarised_chains(season)
		update_ntx_tenure(notarised_chains, season, server)
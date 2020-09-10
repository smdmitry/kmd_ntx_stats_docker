#!/usr/bin/env python3
import table_lib

conn = table_lib.connect_db()
cursor = conn.cursor()

#table = 'balances'
#table = 'coin_social'
#table = 'funding_transactions'
#table = 'last_notarised'
#table = 'notarised_chain_season'
#table = 'nn_social'
#table = 'notarised_count_season'
#table = 'coins'
#table = 'notarised_btc'
#table = 'btc_address_deltas'
#table = 'notarised'
table = 'nn_btc_tx'

#cursor.execute("SELECT * FROM "+table+";")
cursor.execute("SELECT DISTINCT txid FROM "+table+" WHERE address = '1Lets1xxxx1use1xxxxxxxxxxxy2EaMkJ';")

#cursor.execute("SELECT * FROM "+table+" WHERE chain = 'BTC' AND btc_validated = 'false';")

results = cursor.fetchall()
#print(results)
print(len(results))

list = []
for item in results:
    list.append(item[0])
print(list)
cursor.close()

conn.close()



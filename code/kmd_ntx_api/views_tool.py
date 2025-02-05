#!/usr/bin/env python3
import requests
from django.shortcuts import render
from datetime import datetime as dt

# S7 refactoring
import kmd_ntx_api.buttons as buttons

# Older
from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_base58 as b58
import kmd_ntx_api.lib_info as info
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.lib_atomicdex as dex
import kmd_ntx_api.lib_dexstats as dexstats
import kmd_ntx_api.lib_tools as tools


def convert_addresses_view(request):
    context = helper.get_base_context(request)
    context.update({
        "page_title":"Address Conversion",
        "endpoint": "/api/tools/address_conversion/"
    })

    if "address" in request.GET:
        address = request.GET["address"]
        if address == "":
            messages.error(request, f"No address input!")
        else:
            address_rows = []
            addresses = b58.convert_addresses(address)["results"]

            for item in addresses:
                for coin in item:

                    # TODO: Handle segwit addresses
                    # TODO: Explorers for protocol coins
                    if coin.lower().find('segwit') == -1:
                        address_rows.append({
                            "coin":coin, "address":item[coin]
                        })

            context.update({
                "address": address,
                "address_rows": address_rows,
            })

    return render(request, 'views/tools/tool_convert_addresses.html', context)


def create_raw_transaction_view(request):
    coin = helper.get_or_none(request, "coin", "KMD")
    address = helper.get_or_none(request, "address")
    inputs = helper.get_or_none(request, "inputs")
    context = helper.get_base_context(request)

    context.update({
        "page_title":"Create Raw Transaction from Address",
        "reqget":request.GET,
        "coin":coin,
        "address": address,
        "now":int(time.time()),
        "locktime":int(time.time())-30*60,
        "30_min_ago":int(time.time()-30*60),
        "coins_list": dexstats.DEXSTATS_COINS
    })

    # Step one: get UTXOs for selection and show form for destination and amount
    if address:
        rewards_resp = tools.get_kmd_rewards(request)["results"]
        utxos = dexstats.get_dexstats_utxos(coin, address)
        has_error = False
        if isinstance(utxos, str):
            has_error = True
            messages.error(request, f"Error getting utxos: {utxos}")

        if helper.has_error(rewards_resp):
            has_error = True
            messages.error(request, f"Error getting utxos: {rewards_resp['error']}")

        if not has_error:
            for utxo in utxos:
                if utxo["txid"] in rewards_resp["utxo_list"]:
                    for rutxo in rewards_resp["utxos"]:
                        print(rutxo)
                        if rutxo["txid"] == utxo["txid"]:
                            rewards = rutxo["kmd_rewards"]
                            utxo.update({"rewards":rewards})

            context.update({
                "utxos": utxos
            })

    # Step two, construct the raw hex
    if inputs:
        output_amounts = request.GET.getlist("output_amount")
        to_addresses = request.GET.getlist("to_address")
        locktime = request.GET["locktime"]
        expiry_height = request.GET["expiry_height"]

        test_tx = b58.raw_tx()
        tx_inputs = []
        for vin in inputs.split(","):
            elements = vin.split("|")
            tx_inputs.append({
                "tx_hash":elements[0],
                "tx_pos":int(elements[1]),
                "value":float(elements[2]),
                "scriptPubKey":elements[3]
                })
        test_tx.inputs = tx_inputs

        outputs = []
        for i in range(len(to_addresses)):
            outputs.append({
                "address":to_addresses[i],
                "amount":output_amounts[i]
            })
        test_tx.outputs = outputs
        test_tx.locktime = locktime
        raw_hex = test_tx.construct()

        context.update({
            "tx_inputs": tx_inputs,
            "outputs": outputs,
            "raw_tx": raw_hex
        })

    return render(request, 'views/tools/tool_create_raw_transaction.html', context)


def daemon_cli_view(request):

    daemon_cli = info.get_daemon_cli(request)
    coin_icons = info.get_coin_icons(request)

    daemon_cli_rows = []
    for coin in daemon_cli:
        daemon_cli_rows.append({"coin":coin, "daemon_cli":daemon_cli[coin]})

    context = helper.get_base_context(request)
    context.update({
        "daemon_cli_rows": daemon_cli_rows,
        "page_title":"Daemon CLIs"
    })

    return render(request, 'views/tools/tool_daemon_cli.html', context)


def decode_op_return_view(request):
    context = helper.get_base_context(request)
    context.update({
        "page_title":"Decode OP_RETURN Tool"
    })

    op_return = helper.get_or_none(request, "OP_RETURN")

    if op_return:
        try:
            decoded = b58.decode_opret(op_return)
        except Exception as e:
            decoded = {"error": e}

        if not "error" in decoded:
            opret_rows = []
            for item in decoded:
                key_val = item.replace("_", " ").title()
                opret_rows.append({"key":key_val, "value":decoded[item]})

            context.update({
                "OP_RETURN": op_return,
                "opret_rows": opret_rows,
            })

        else:
            messages.error(request, f"Invalid OP_RETURN: {op_return}")

    return render(request, 'views/tools/tool_decode_opret.html', context)


def faucet_view(request):
    season = helper.get_page_season(request)
    notary_list = helper.get_notary_list(season)
    faucet_balances = requests.get(f"https://faucet.komodo.earth/faucet_balances").json()
    pending_tx_resp = requests.get(f"https://faucet.komodo.earth/show_pending_tx").json()
    pending_tx_list = []
    tx_rows = []
    pending_index = []
    if "Result" in pending_tx_resp:
        if "Message" in pending_tx_resp["Result"]:
            pending_tx_list = pending_tx_resp["Result"]["Message"]
    for item in pending_tx_list:
        tx_rows.append({
            "index": item[0],    
            "coin": item[1], 
            "address": item[2], 
            "time_sent": "n/a",
            "timestamp": 99999999999999,
            "amount": "n/a",  
            "txid": "n/a",
            "status": item[6]
        })
        pending_index.append(item[0])
        if len(tx_rows) >= 250:
            break
    sent_tx_resp = requests.get(f"https://faucet.komodo.earth/show_faucet_db").json()
    sent_tx_list = []
    now = time.time()
    sum_24hrs = 0
    count_24hrs = 0
    if "Result" in sent_tx_resp:
        if "Message" in sent_tx_resp["Result"]:
            sent_tx_list = sent_tx_resp["Result"]["Message"]
    for item in sent_tx_list:
        if item[0] not in pending_index:
            if item[3] > SINCE_INTERVALS['day']:
                sum_24hrs += item[4]
                count_24hrs += 1
            tx_rows.append({
                "index": item[0],
                "coin": item[1],
                "address": item[2],
                "timestamp": item[3],
                "time_sent": dt.fromtimestamp(item[3]),
                "amount": item[4],
                "txid": item[5],
                "status": item[6]
            })

    coins_list = ["RICK", "MORTY", "DOC", "MARTY", "ZOMBIE"]
    context = helper.get_base_context(request)
    context.update({
        "page_title":"Testcoin Faucet",
        "explorers":info.get_explorers(request),
        "faucet_balances":faucet_balances,
        "count_24hrs":count_24hrs,
        "sum_24hrs":sum_24hrs,
        "tx_rows": tx_rows,
        "coins_list": coins_list
    })

    if request.method == 'POST':
        if 'coin' in request.POST:
            coin = request.POST['coin'].strip()
            if coin == "TKL":
                coin = "TOKEL"
        if 'address' in request.POST:
            address = request.POST['address'].strip()
        url = f'https://faucet.komodo.earth/faucet/{coin}/{address}'
        r = requests.get(url)
        try:
            resp = r.json()
            messages.success(request, resp["Result"]["Message"])
            if resp['Status'] == "Success":
                context.update({"result": coin+"_success"})
            elif resp['Status'] == "Error":
                context.update({"result": "disqualified"})
            else:
                context.update({"result": "fail"})
        except Exception as e:
            logger.error(f"[faucet] Exception: {e}")
            messages.success(request, f"Something went wrong... {e}")
            context.update({"result":"fail"})

    return render(request, 'views/tools/tool_faucet.html', context)

def notaryfaucet_view(request):
    season = helper.get_page_season(request)
    notary_list = helper.get_notary_list(season)
    coins_list = []
    try:
        faucet_coins = requests.get("https://notaryfaucet.dragonhound.tools/faucet_coins").json()["result"]
        coins_list = faucet_coins["Main"] + faucet_coins["3P"]
    except:
        pass
    
    faucet_balances = requests.get("https://notaryfaucet.dragonhound.tools/faucet_balances").json()
    
    pending_tx_resp = requests.get("https://notaryfaucet.dragonhound.tools/show_pending_tx").json()
    pending_tx_list = []
    tx_rows = []
    pending_index = []
    if "result" in pending_tx_resp:
        if "message" in pending_tx_resp["result"]:
            pending_tx_list = pending_tx_resp["result"]["message"]
    for item in pending_tx_list:
        try:
            logger.info(item)
            
            tx_rows.append({
                "index": item[0],
                "coin": item[1],
                "pubkey": item[2],
                "notary": item[3],
                "time_sent": "n/a",
                "timestamp": 99999999999999,
                "amount": "n/a",
                "txid": "n/a",
                "status": item[7]
            })
            pending_index.append(item[0])
        except Exception as e:
            logger.info(f"Error: {e}")
        if len(tx_rows) >= 250:
            break
    sent_tx_resp = requests.get("https://notaryfaucet.dragonhound.tools/show_faucet_db").json()
    sent_tx_list = []
    now = time.time()
    sum_24hrs = 0
    count_24hrs = 0
    if "result" in sent_tx_resp:
        if "message" in sent_tx_resp["result"]:
            sent_tx_list = sent_tx_resp["result"]["message"]
    for item in sent_tx_list:
        logger.info(item)
        if item[0] not in pending_index:
            if item[4] > SINCE_INTERVALS['day']:
                sum_24hrs += item[5]
                count_24hrs += 1
            tx_rows.append({
                "index":item[0],
                "coin":item[1],
                "pubkey":item[2],
                "notary": item[3],
                "timestamp": item[4],
                "time_sent":dt.fromtimestamp(item[4]),
                "amount":item[5],
                "txid":item[6],
                "status":item[7]
            })


    context = helper.get_base_context(request)
    context.update({
        "page_title": "Notary Faucet",
        "explorers": info.get_explorers(request),
        "count_24hrs": count_24hrs,
        "sum_24hrs": sum_24hrs,
        "coins_list": coins_list,
        "tx_rows": tx_rows,
        "buttons": buttons.get_faucet_buttons(),
        "faucet_balances": faucet_balances
    })

    if request.method == 'POST':
        try:
            if 'coin' in request.POST:
                coin = request.POST['coin'].strip()
            if 'pubkey' in request.POST:
                pubkey = request.POST['pubkey'].strip()
            url = f'https://notaryfaucet.dragonhound.tools/faucet/{pubkey}/{coin}'
            r = requests.get(url)
            resp = r.json()
            messages.success(request, resp["result"]["message"])
            if resp['status'] == "success":
                context.update({"result":coin+"_success"})
            elif resp['status'] == "error":
                context.update({"result":"disqualified"})
            else:
                context.update({"result":"fail"})
        except Exception as e:
            logger.error(f"[notaryfaucet] Exception: {e}")
            messages.success(request, f"Something went wrong... {e} {url}")
            context.update({"result":"fail"})

    return render(request, 'views/tools/tool_notaryfaucet.html', context)


def kmd_rewards_view(request):
    context = helper.get_base_context(request)
    context.update({
        "page_title":"KMD Rewards Tool",
        "buttons": buttons.get_rewards_buttons(),
    })

    address = helper.get_or_none(request, "address")
    if address:
        resp = tools.get_kmd_rewards(request)
        if helper.has_error(resp):
            messages.error(request, resp["error"])

        else:

            kmd_rewards_rows = []
            for utxo in resp["results"]["utxos"]:
                kmd_rewards_rows.append(utxo)

            context.update({
                "address": address,
                "kmd_balance": resp["results"]["kmd_balance"],
                "total_rewards": round(resp["results"]["total_rewards"],6),
                "utxo_count": resp["count"],
                "eligible_utxo_count": resp["results"]["eligible_utxo_count"],
                "oldest_utxo_block": resp["results"]["oldest_utxo_block"],
                "kmd_rewards_rows": kmd_rewards_rows,
            })

    return render(request, 'views/tools/tool_kmd_rewards.html', context)


def launch_params_view(request):

    url = f"{THIS_SERVER}/api/info/launch_params"
    launch_params = requests.get(url).json()["results"]

    launch_param_rows = []
    coin_icons = info.get_coin_icons(request)
    for coin in launch_params:
        launch_param_rows.append({"coin":coin, "launch_params":launch_params[coin]})
        if coin not in coin_icons:
            coin_icons.update({coin: "/static/img/notary/icon/blank.png"})

    context = helper.get_base_context(request)
    context.update({
        "launch_param_rows": launch_param_rows,
        "page_title":"Launch Parameters"
    })

    return render(request, 'views/tools/tool_launch_params.html', context)


def pubkey_addresses_view(request):
    context = helper.get_base_context(request)
    context.update({
        "page_title": "Pubkey Addresses",
        "endpoint": "/api/tools/address_from_pubkey/"
    })
    if "pubkey" in request.GET:
        pubkey = request.GET["pubkey"]
        if pubkey == "":
            messages.error(request, f"No pubkey input!")
        elif not b58.validate_pubkey(pubkey):
            messages.error(request, f"Invalid pubkey: {pubkey}")
        else:
            base_58_coins = info.get_base_58_coin_params(request)
            address_rows = []
            
            for coin in base_58_coins:
                pubtype = base_58_coins[coin]["pubtype"]
                p2shtype = base_58_coins[coin]["p2shtype"]
                wiftype = base_58_coins[coin]["wiftype"]
                address_row = b58.calc_addr_tool(pubkey, pubtype, p2shtype, wiftype)
                address_row.update({"coin":coin})
                address_rows.append(address_row)
            context.update({
                "pubkey": pubkey,
                "address_rows": address_rows,
            })

    return render(request, 'views/tools/tool_pubkey_addresses.html', context)


def scripthashes_from_pubkey_view(request):
    context = helper.get_base_context(request)
    context.update({
        "page_title":"Get Scripthashes from Pubkey"
    })
    if "pubkey" in request.GET:
        pubkey = request.GET["pubkey"]
        url = f"{THIS_SERVER}/api/tools/scripthashes_from_pubkey/?pubkey={pubkey}"
        resp = requests.get(url).json()

        if helper.has_error(resp):
            messages.error(request, f"{resp['error']}")
        else:
            resp_rows = []
            for item in resp["results"]:
                key_val = item.replace("_", " ").title()
                resp_rows.append({"key":key_val, "value":resp["results"][item]})

            context.update({
                "pubkey":pubkey,
                "resp_rows": resp_rows
            })

    return render(request, 'views/tools/tool_scripthashes_from_pubkey.html', context)


def scripthash_from_address_view(request):
    context = helper.get_base_context(request)
    context.update({
        "page_title":"Get Scripthash from Address"
    })
    if "address" in request.GET:
        address = request.GET["address"]
        url = f"{THIS_SERVER}/api/tools/scripthash_from_address/?address={address}"
        resp = requests.get(url).json()

        if helper.has_error(resp):
            messages.error(request, f"{resp['error']}")
        else:
            resp_rows = []
            for item in resp["results"]:
                key_val = item.replace("_", " ").title()
                resp_rows.append({"key":key_val, "value":resp["results"][item]})

            context.update({
                "address":address,
                "resp_rows": resp_rows
            })

    return render(request, 'views/tools/tool_scripthash_from_address.html', context)


def send_raw_tx_view(request):
    context = helper.get_base_context(request)
    context.update({
        "page_title":"Send Raw Transaction (experimental!)",
        "coins_list": dexstats.DEXSTATS_COINS
    })

    if "coin" in request.GET or "tx_hex" in request.GET:
        resp = dex.send_raw_tx(request)

        if helper.has_error(resp):
            messages.error(request, f"{resp['error']}")
        else:
            messages.success(request, f"{resp}")

    return render(request, 'views/tools/tool_send_raw_transaction.html', context)


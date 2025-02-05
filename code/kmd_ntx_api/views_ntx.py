#!/usr/bin/env python3
import random
import numpy as np
from datetime import datetime as dt
from django.shortcuts import render

# S7 refactoring
import kmd_ntx_api.profiles as profiles
from kmd_ntx_api.seednodes import seednode_version_context

# Older
from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_info as info
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.lib_stats as stats
import kmd_ntx_api.lib_query as query
import kmd_ntx_api.lib_table as table
import kmd_ntx_api.serializers as serializers

# In order of appearance within the "Notarisation" drop down menu

def notary_profile_view(request):
    context = helper.get_base_context(request)
    # TODO: This is not currently used, but can be added for prior season stats given fully populated databases
    context.update({"notary_seasons": info.get_notary_seasons()})
    # Base context will return a random notary if one is not specified. For this view, we prefer 'None'.
    notary = notary = helper.get_or_none(request, "notary")
    season = context["season"]
    if notary in helper.get_notary_list(season):
        context.update(profiles.get_notary_profile_context(request, season, notary))
        return render(request, 'views/notarisation/notary_profile.html', context)
    context.update(profiles.get_notary_profile_index_context(request, season))
    return render(request, 'views/notarisation/notary_profile_index.html', context)


def coin_profile_view(request, coin=None): # TODO: REVIEW and ALIGN with NOTARY PROFILE
    context = helper.get_base_context(request)
    season = context["season"]
    coin = helper.get_or_none(request, "coin", coin)
    context.update({
        "server": helper.get_coin_server(season, coin),
        "page_title": "Coin Profile Index"
    })
    
    if coin:
        context.update(profiles.get_coin_profile_context(request, season, coin))
        return render(request, 'views/coin/coin_profile.html', context)    
    context.update(profiles.get_coin_profile_index_context(request, season))
    return render(request, 'views/coin/coin_profile_index.html', context)


def ntx_scoreboard_view(request, region=None):
    context = helper.get_base_context(request)
    context["region"] = helper.get_or_none(request, "region", region)
    season_stats_sorted = stats.get_season_stats_sorted(context["season"])
    context.update({
        "page_title": f"Notarisation Scoreboard",
        "anchored": True,
        "season_stats_sorted": season_stats_sorted,
        "region_score_stats": stats.get_region_score_stats(season_stats_sorted),
        "nn_social": info.get_nn_social_info(request)
    })
    return render(request, 'views/ntx/ntx_scoreboard.html', context)


def ntx_scoreboard_24hrs_view(request, region=None):
    context = helper.get_base_context(request)
    context["region"] = helper.get_or_none(request, "region", region)
    context.update({
        "page_title": f"Last 24hrs Notarisation Scoreboard",
        "anchored": True,
        "daily_stats_sorted": stats.get_daily_stats_sorted(context["season"]),
        "nn_social": info.get_nn_social_info(request)
    })
    return render(request, 'views/ntx/ntx_scoreboard_24hrs.html', context)
 
 
def seednode_version_view(request):
    context = helper.get_base_context(request)
    context.update(seednode_version_context(request))
    return render(request, 'views/atomicdex/seednode_version_stats.html', context)


def notary_coin_notarised_view(request):
    context = helper.get_base_context(request)
    season = context["season"]
    notary = context["notary"]
    server = context["server"]
    coin = context["coin"]
    context.update({
        "server": server,
        "coin": coin,
        "notary": notary, 
        "filter_params": f"&notary={{{notary}}}&coin={coin}&season={season}&server={server}"
    })

    return render(request, 'views/ntx/notary_coin_notarised.html', context)


def notary_epoch_scores_view(request):
    context = helper.get_base_context(request)
    notary = context["notary"]
    scoring_table, totals = table.get_notary_epoch_scores_table(request, notary)
    try:
        context.update({
            "table_title": context["notary_clean"],
            "scoring_table": scoring_table,
            "total_count":totals["counts"][notary],
            "total_score":totals["scores"][notary],
            "nn_social": info.get_nn_social_info(request),
            "table": "epoch_scoring"            
        })
    except Exception as e:
        messages.error(request, f"Error: {e}")
    return render(request, 'views/ntx/notary_epoch_scores_view.html', context)


def notarised_24hrs_view(request):    
    context = helper.get_base_context(request)
    context.update({
        "page_title":"dPoW Notarisations (last 24hrs)"
    })
    return render(request, 'views/ntx/notarised_24hrs.html', context)


def notary_epoch_coin_notarised_view(request):
    context = helper.get_base_context(request)
    return render(request, 'views/ntx/notary_epoch_coin_notarised.html', context)


def notarisation_view(request):
    txid = helper.get_or_none(request, "txid", "5507e4fb484e51e6d748585e7e08dcda4bb17bfb420c9ccd2c43c0481e265bf6")
    ntx_data = query.get_notarised_data(txid=txid)
    context = helper.get_base_context(request)
    serializer = serializers.notarisedSerializer(ntx_data, many=True)
    context.update({"ntx_data": dict(serializer.data[0])})
    return render(request, 'views/ntx/notarisation.html', context)


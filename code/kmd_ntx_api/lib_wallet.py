from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_query as query
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.models as models
import kmd_ntx_api.serializers as serializers


def get_source_addresses(request):
    season = helper.get_page_season(request)
    server = helper.get_page_server(request)
    coin = helper.get_or_none(request, "coin")
    notary = helper.get_or_none(request, "notary")
    return query.get_addresses_data(season, server, coin, notary)


def get_source_balances(request):
    season = helper.get_page_season(request)
    server = helper.get_page_server(request)
    coin = helper.get_or_none(request, "coin")
    notary = helper.get_or_none(request, "notary")
    return query.get_balances_data(season, server, coin, notary)

def get_distinct_rewards_txids(request):
    q = models.rewards_tx.objects.all()
    return query.get_distinct_filters(q, ["txid"])

def get_rewards_txid(request):
    if 'txid' in request.GET:
        return models.rewards_tx.objects.filter(txid=request.GET['txid'])
    return {"error": "No txid param!"}

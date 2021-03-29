#!/usr/bin/env python3

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from rest_framework import permissions, viewsets

from kmd_ntx_api.serializers import *
from kmd_ntx_api.models import *
from kmd_ntx_api.lib_query import get_notary_list 
from kmd_ntx_api.lib_api_filtered import * 


class addresses_filter(viewsets.ViewSet):
    """
    Returns Notary Node addresses, nested by Name > Season > Chain \n
    Default filter returns current NN Season \n

    """
    serializer_class = AddressesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        filters = self.serializer_class.Meta.fields
        resp = get_addresses_data(request)
        api_resp = wrap_api(resp, filters)
        return Response(api_resp)


class balances_filter(viewsets.ViewSet):
    """
    API endpoint showing notary node balances
    """
    serializer_class = BalancesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        filters = self.serializer_class.Meta.fields
        resp = get_balances_data(request)
        api_resp = wrap_api(resp, filters)
        return Response(api_resp)

class coins_filter(viewsets.ViewSet):
    """
    API endpoint showing coininfo from coins and dpow repositories
    """
    serializer_class = CoinsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        filters = self.serializer_class.Meta.fields
        resp = get_coins_data(request)
        api_resp = wrap_api(resp, filters)        
        return Response(api_resp)

class explorers_filter(viewsets.ViewSet):  # TODO: add coin type filter

    """
    Returns explorers sourced from coins repo
    """    
    serializer_class = ExplorersSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        filters = self.serializer_class.Meta.fields
        resp = get_explorers_data()
        api_resp = wrap_api(resp, filters)
        return Response(api_resp)

class mined_count_season_filter(viewsets.ViewSet):
    """
    API endpoint showing mined blocks by notary/address (minimum 10 blocks mined)
    """
    serializer_class = MinedCountSeasonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        filters = self.serializer_class.Meta.fields
        resp = get_mined_count_season_data(request)
        api_resp = wrap_api(resp, filters)
        return Response(api_resp)

class mined_count_date_filter(viewsets.ViewSet):
    """
    API endpoint showing mined blocks by notary/address (minimum 10 blocks mined) \n
    Defaults to todays date.
    """
    serializer_class = MinedCountDailySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        filters = self.serializer_class.Meta.fields
        resp = get_mined_count_daily_data(request)
        api_resp = wrap_api(resp, filters)
        return Response(api_resp)


class notarised_chain_season_filter(viewsets.ViewSet):
    """
    API endpoint showing notary node mined blocks
    """
    serializer_class = NotarisedChainSeasonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        filters = self.serializer_class.Meta.fields
        resp = get_notarised_chain_season_data(request)
        api_resp = wrap_api(resp, filters)
        return Response(api_resp)

class notarised_count_season_filter(viewsets.ViewSet):
    """
    API endpoint showing notary node mined blocks
    """
    serializer_class = NotarisedCountSeasonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        filters = self.serializer_class.Meta.fields
        resp = get_notarised_count_season_data(request)
        api_resp = wrap_api(resp, filters)
        return Response(api_resp)

class notarised_chain_date_filter(viewsets.ViewSet):
    """
    API endpoint showing notary node mined blocks. \n
    Defaults to filtering by todays date \n
    """
    serializer_class = NotarisedChainDailySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        filters = self.serializer_class.Meta.fields
        resp = get_notarised_chain_daily_data(request)
        api_resp = wrap_api(resp, filters)
        return Response(api_resp)

class notarised_count_date_filter(viewsets.ViewSet):
    """
    API endpoint showing notary node mined blocks
    """
    serializer_class = NotarisedCountDailySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        filters = self.serializer_class.Meta.fields
        resp = get_notarised_count_date_data(request)
        api_resp = wrap_api(resp, filters)
        return Response(api_resp)


#TODO: Review this - A little different to other filtered viewsets...
class notary_nodes_filter(viewsets.ViewSet):
    """
    API endpoint listing notary names for each season
    """
    serializer_class = NNSocialSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['season']
    ordering_fields = ['season', 'notary']
    ordering = ['-season', 'notary']

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        season = get_season()
        if "season" not in request.GET:
            season = request.GET["season"]
        notaries_list = get_notary_list(season)
        api_resp = wrap_api(notaries_list)
        return Response(api_resp)

class notary_rewards_filter(viewsets.ViewSet):
    """
    API endpoint showing notary rewards pending
    """
    serializer_class = RewardsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        filters = self.serializer_class.Meta.fields
        resp = get_rewards_data(request)
        api_resp = wrap_api(resp, filters)
        return Response(api_resp)

class notary_social_filter(viewsets.ViewSet):
    """
    API endpoint showing notary rewards pending
    """
    serializer_class = NNSocialSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        filters = self.serializer_class.Meta.fields
        resp = get_nn_social_data(request)
        api_resp = wrap_api(resp, filters)
        return Response(api_resp)

class last_ntx_filter(viewsets.ViewSet):
    """
    API endpoint showing notary rewards pending
    """
    serializer_class = LastNotarisedSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        last_ntx_data = last_notarised.objects.all().values()
        return Response(last_ntx_data)

class last_btc_ntx_filter(viewsets.ViewSet):
    """
    API endpoint showing notary rewards pending
    """
    serializer_class = LastBtcNotarisedSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        last_btc_ntx_data = last_btc_notarised.objects.all().values()
        return Response(last_btc_ntx_data)

class notarised_tenure_filter(viewsets.ViewSet):
    """
    Returns chain notarisation tenure, nested by Season > Chain \n
    Default filter returns current NN Season \n

    """
    serializer_class = ntxTenureSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        filters = self.serializer_class.Meta.fields
        resp = get_notarised_tenure_data(request)
        api_resp = wrap_api(resp, filters)
        return Response(api_resp)


from django.urls import path
from kmd_ntx_api import views_coin

frontend_coin_urls = [

    path('coins_last_ntx/',
          views_coin.coins_last_ntx,
          name='coins_last_ntx_view'),

    path('coin_notarised_24hrs/',
          views_coin.coin_notarised_24hrs_view,
          name='coin_notarised_24hrs'),

    path('notarised_tenure/',
          views_coin.notarised_tenure_view,
          name='notarised_tenure_view'),

    ]


api_coins_urls = [

    ]
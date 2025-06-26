from django.contrib import admin
from django.urls import path
import base.views as views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("coin_list/<str:coin_id>/", views.coin_detail, name = 'coin_detail'),
    path("",views.home, name = 'home'),
    path('coin_list/', views.coin_list, name='coin_list'),
    path("register/",views.register, name = 'registration'),
    path("login/",views.login, name = 'login'),
    path("portfolio_creation/",views.portfolio_creation, name = 'portfolio_creation'),
    path("logout/",views.logout, name = 'logout' ),
    path('portfolio/switch/', views.portfolioSelection, name='portfolioSelection'),
    path('ajax/search_coins/', views.ajax_search_coins, name='ajax_search_coins'),
    path("buy_crypto/", views.buy_crypto, name="buy_crypto"),
    path("portfolio_summary/<int:portfolio_id>/", views.my_transactions, name="my_transactions"),
    path("portfolio_summary/", views.my_transactions, name="my_transactions"),
    path("ajax/my_transactions/<int:portfolio_id>/", views.ajax_my_transactions, name="ajax_my_transactions"),
    path("ajax/my_transactions/", views.ajax_my_transactions, name="ajax_my_transactions"),
    path("coin_list/<str:coin_id>/ajax/", views.ajax_coin_detail, name='ajax_coin_detail'),
    path("ajax/sell/", views.ajax_sell, name='ajax_sell_transaction'),
    path("ajax/delete_portfolio/", views.ajax_delete_portfolio, name="ajax_delete_portfolio"),
    path("portfolio_list/", views.portfolio_list, name="portfolio_list"),




]

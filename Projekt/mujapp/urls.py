import aut.views as aut
import browse.views as viewing
from django.contrib import admin
from django.urls import path
from base.views import portfolioCreation

urlpatterns = [
    path("admin/", admin.site.urls),
    path("coin_list/<str:coin_id>/", viewing.coin_detail, name = 'coin_detail' ),
    path("", viewing.home, name = 'home'),
    path("coin_list/", viewing.coin_list, name = 'coin_list'),
    path("register/", aut.register, name = 'registration'),
    path("login/", aut.login, name = 'login'),
    path("portfolio_creation/", portfolioCreation, name = 'portfolio_creation'),
    path("logout/", aut.logout, name = 'logout' ),
    path('portfolio/switch/', viewing.portfolioSelection, name='portfolioSelection'),


]

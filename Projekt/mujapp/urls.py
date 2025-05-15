from django.contrib import admin
from django.urls import path
import base.views as views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("coin_list/<str:coin_id>/", views.coin_detail, name = 'coin_detail'),
    path("",views.home, name = 'home'),
    path("coin_list/",views.coin_list, name = 'coin_list'),
    path("register/",views.register, name = 'registration'),
    path("login/",views.login, name = 'login'),
    path("portfolio_creation/",views.portfolioCreation, name = 'portfolio_creation'),
    path("logout/",views.logout, name = 'logout' ),
    path('portfolio/switch/', views.portfolioSelection, name='portfolioSelection'),


]

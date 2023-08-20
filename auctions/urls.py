from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("categories", views.categories, name="categories"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("my_watchlist", views.access_my_watchlist, name="my_watchlist"),
    path("my_listings", views.access_my_listings, name="my_listings"),
    path("categories/<str:category_name>", views.get_listings_in_category, name="listing_category"),
    path("listing/<str:listing_name>", views.listing, name="listing"),
    path("listing/<str:listing_name>/add_watchlist", views.add_to_watchlist, name="add_watchlist"),
    path("listing/<str:listing_name>/remove_watchlist/", views.remove_from_watchlist, name="remove_watchlist"),
    path("listing/<str:listing_name>/close_bid", views.close_bid, name="close_bid"),
    path("listing/<str:listing_name>/add_comment", views.add_comment, name="add_comment"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register")
]

from django.urls import path

from . import views

app_name = "auctions"

urlpatterns = [
    # urls already created
    path("", views.index, name="index"), # ! Cambiar el diseño (no como una lista)
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # My urls
    path("add_listing/", views.add_listing, name="add_listing"), 
    path("watchlist/", views.watchlist, name="watchlist"), 
    path("add_watchlist/<int:listing_id>/", views.add_watchlist, name="add_watchlist"),
    path("remove_watchlist/<int:listing_id>/", views.remove_watchlist, name="remove_watchlist"), 
    path("categories/", views.categories, name="categories"),
    path("categories/<str:category_name>/", views.category_items, name="category_items"),
    path("listing_view/<int:listing_id>/", views.listing_view, name="listing_view"),
    path("my_listings/", views.my_listings, name="my_listings"),
    path("shopping_history/", views.shopping_history, name="shopping_history"),
    path("sell/<int:listing_id>", views.sell, name="sell"), 
    path("my_bids/", views.my_bids, name="my_bids"),
    path("place_bid/<int:listing_id>/", views.place_bid, name="place_bid"), 
    path("add_comments/<int:listing_id>/", views.add_comments, name="add_comments"),

    # Generic Views
    path("listing_view/edit/<int:pk>/", views.EditListing.as_view(), name="edit_listing"),

]

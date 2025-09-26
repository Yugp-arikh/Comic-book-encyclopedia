# encyclopedia/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("search/", views.search, name="search"),
    path("comic/<str:bl_id>/", views.comic_detail, name="comic_detail"),
    path("save/", views.save_to_search_list, name="save_to_search_list"),
    path("clear/", views.clear_search_results, name="clear_search_results"),
    path("advanced/", views.advanced_search, name="advanced_search"),
    path("reports/", views.reports, name="reports"),
    path("search-list/", views.view_search_list, name="view_search_list"),
    path("remove-from-search-list/", views.remove_from_search_list, name="remove_from_search_list"),
    path("browse/", views.browse_comics, name="browse_comics"),
]

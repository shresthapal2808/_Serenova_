from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('community/', views.community_view, name='community'),
    path('quotes/', views.quotes_view, name='quotes'),
    path("soundscape/", views.soundscape, name="soundscape"),
    path("search-sounds/", views.search_sounds, name="search_sounds"),
    path("save-mix/", views.save_mix, name="save_mix"),
    path("get-quote/", views.get_quote, name="get_quote"),
    path("community/", views.community_view, name="community"),
    path("react/<int:post_id>/", views.react_post, name="react_post"),
    path("delete-post/<int:post_id>/", views.delete_post, name="delete_post"),
     path('journal/', views.journal_view,   name='journal'),
    path('journal/<int:pk>/edit/',views.journal_edit,   name='journal_edit'),
    path('journal/<int:pk>/delete/',views.journal_delete,name='journal_delete'),
    path('api_community/', views.api_community_view, name='api_community'),
    path('about/', views.about, name="about"),
]
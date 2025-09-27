from django.urls import path
from . import views

app_name = 'voting'

urlpatterns = [
    path('', views.ElectionListView.as_view(), name='home'),
    path('election/<int:pk>/', views.ElectionDetailView.as_view(), name='election_detail'),
    path('election/<int:pk>/vote/', views.cast_vote, name='cast_vote'),
    path('election/<int:pk>/results/', views.election_results, name='election_results'),

    # App-level admin/dashboard routes (moved off of /admin/ to avoid conflict with Django admin)
    path('dashboard/elections/', views.admin_manage_elections, name='admin_manage_elections'),
    path('dashboard/elections/create/', views.admin_create_election, name='admin_create_election'),
    path('dashboard/elections/<int:pk>/add_candidate/', views.admin_add_candidate, name='admin_add_candidate'),

    # auth/registration/profile
    path('accounts/register/', views.register_view, name='register'),
    path('accounts/profile/', views.profile_view, name='profile'),

    # API for live counts
    path('api/election/<int:pk>/counts/', views.api_election_counts, name='api_election_counts'),
]

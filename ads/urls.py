from django.urls import path
from . import views

urlpatterns = [
    path('', views.ad_list, name='ad_list'),
    path('create/', views.ad_create, name='ad_create'),
    path('<int:pk>/edit/', views.ad_update, name='ad_update'),
    path('<int:pk>/delete/', views.ad_delete, name='ad_delete'),
    path('ads/<int:ad_id>/propose/', views.propose_exchange, name='propose_exchange'),
    path('proposals/incoming/', views.incoming_proposals, name='incoming_proposals'),
    path('proposals/sent/', views.sent_proposals, name='sent_proposals'),
    path('proposals/<int:proposal_id>/<str:action>/', views.respond_proposal, name='respond_proposal'),
]

from django.urls import path
from desk import views
urlpatterns=[path('',views.index),path('api/session',views.session),path('api/login',views.sign_in),path('api/logout',views.sign_out),path('api/tickets',views.tickets),path('api/tickets/<int:pk>',views.ticket_detail),path('api/conversation',views.conversation),path('api/transcribe',views.transcribe),path('api/faq',views.faq)]

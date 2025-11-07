from django.urls import path, include
from subscriptions.views import index
urlpatterns = [
    path('', index),
    path('api/', include('subscriptions.urls')),
]

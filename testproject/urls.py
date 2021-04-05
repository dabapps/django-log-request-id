from django.urls import path
from testproject import views


urlpatterns = [
    path("", views.test_view),
    path("async/", views.test_async_view),
]

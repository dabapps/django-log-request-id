from django.conf.urls import patterns, url
from testproject import views


urlpatterns = patterns(
    '',
    url(r'^$', views.test_view),
)

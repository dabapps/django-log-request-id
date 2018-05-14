import django
from testproject import views

if django.VERSION < (1, 9):
    from django.conf.urls import patterns, url
    urlpatterns = patterns(
        '',
        url(r'^$', views.test_view),
    )

else:
    from django.conf.urls import url
    urlpatterns = [
        url(r'^$', views.test_view),
    ]

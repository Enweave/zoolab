# -*- coding: utf-8 -*-

from django.conf.urls import url, patterns

urlpatterns = patterns('animals.views',
    url(r'^supplies/$', 'supplies_page', name='supplies'),
    url(r'^reports/$', 'reports_page', name='reports'),
    url(r'^get_animals/$','get_animals', name="get-animals"),
    url(r'^get_consumables/$','get_consumables', name="get-consumables"),
    url(r'^remove_supply/(?P<pk>[-\d]+)/', 'remove_supply', name="remove_supply"),
)
# -*- coding: utf-8 -*-

from django.conf.urls import url, patterns

urlpatterns = patterns('animals.views',
    url(r'^supplies/$', 'supplies_page', name='supplies'),
    url(r'^reports/$', 'reports_page', name='reports'),
    # url(r'^animal_groups/(?P<pk>[-\d]+)/', 'animal_group_detail',name='animal-group-detail'),
)
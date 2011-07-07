"""
Module: DMS UI Django URLs
Project: Adlibre DMS
Copyright: Adlibre Pty Ltd 2011
License: See LICENSE for license information
"""

from django.conf.urls.defaults import *

urlpatterns = patterns('ui.views',
    url(r'^rule-(?P<id_rule>\d+)/$','document_list', name='ui_document_list'),
    url(r'','rule_list', name='ui_rule_list'),
)
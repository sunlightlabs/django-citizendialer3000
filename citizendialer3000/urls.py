from django.conf.urls.defaults import *

urlpatterns = patterns('citizendialer3000.views',
    url(r'^$', 'callcampaign_list', name='call_list'),
    url(r'^(?P<slug>[\w\-]+)/$', 'callcampaign_detail', name='call_campaign'),
    url(r'^(?P<slug>[\w\-]+)/(?P<contact_id>\d+)/$', 'contact_detail', name='call_contact'),
    url(r'^(?P<slug>[\w\-]+)/thankyou/$', 'complete', name='call_complete'),
    url(r'^(?P<slug>[\w\-]+)/results/$', 'results', name='results'),
)

from django.conf.urls.defaults import *

urlpatterns = patterns('citizendialer3000.views',
    url(r'^call/$', 'campaign_list', name='call'),
    url(r'^call/(?P<slug>[\w\-]+)/$', 'campaign_detail', name='call_campaign'),
    url(r'^call/(?P<slug>[\w\-]+)/(?P<contact_id>\d+)/$', 'contact_detail', name='call_contact'),
    url(r'^call/(?P<slug>[\w\-]+)/thankyou/$', 'complete', name='call_complete'),
    url(r'^call/(?P<slug>[\w\-]+)/results/$', 'results', name='results'),
)

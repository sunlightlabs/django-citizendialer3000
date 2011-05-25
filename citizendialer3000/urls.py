from django.conf.urls.defaults import *

urlpatterns = patterns('citizendialer3000.views',
    url(r'^$', 'callcampaign_list', name='call_list'),
    url(r'^(?P<slug>[\w\-]+)/$', 'callcampaign_detail', name='call_campaign'),
    url(r'^(?P<slug>[\w\-]+)/thankyou/$', 'complete', name='call_complete'),
    url(r'^(?P<slug>[\w\-]+)/results/$', 'results', name='results'),
    url(r'^(?P<slug>[\w\-]+)/results/calls.csv$', 'results_calls', name='results_calls'),
    url(r'^(?P<slug>[\w\-]+)/results/summary.csv$', 'results_summary', name='results_summary'),
    url(r'^(?P<slug>[\w\-]+)/(?P<bioguide_id>\w+)/$', 'contact_detail', name='call_contact'),
)

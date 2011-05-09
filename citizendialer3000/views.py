from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from sunlightapi import sunlight
from citizendialer3000.forms import CallForm
from citizendialer3000.models import Campaign, Contact, Call
import json
import re

# get custom cache key prefix, if set
KEY_PREFIX = getattr(settings, 'CD3000_KEY_PREFIX', 'CD3000')
TIMEOUT = getattr(settings, 'CD3000_CACHE_TIMEOUT', 60 * 10) # 10 minutes

# setup API
sunlightapi.apikey = getattr(settings, 'CD3000_SUNLIGHTAPI_KEY')

# zipcode validation regex
ZIPCODE_RE = re.compile(r'^\d{5}$')

def campaign_list(request):
    data = {
        'campaigns': Campaign.objects.filter(is_public=True),
    }
    return render_to_response('citizendialer3000/campaign_list.html', data,
                              context_instance=RequestContext(request))

def campaign_detail(request, slug):
    
    campaign = get_object_or_404(Campaign, slug=slug)
    
    data = {'campaign': campaign}
    
    if 'zipcode' in request.GET:
        
        zipcode = request.GET['zipcode']
        
        if not ZIPCODE_RE.match(zipcode):
            return HttpResponseForbidden('invalid zipcode')
        
        # get bioguide_ids from cache or sunlight api
        key = "%s_ZIPCODE_%s" % (KEY_PREFIX, zipcode)
        bids = cache.get(key)
        if bids is None:
            mocs = sunlightapi.legislators.allForZip(zipcode)
            bids = [moc.bioguide_id for moc in mocs]
            cache.set(key, bids, TIMEOUT)
        
        contacts = Contact.objects.filter(campaign=campaign, bioguide_id__in=bids)
        
        if request.is_ajax():
            
            content = json.dumps({
                'zipcode': zipcode,
                'contacts': contacts,
            })
            return HttpResponse(content, mimetype='application/json')
            
        else:
            data['zipcode'] = zipcode
            data['contacts'] = contacts
        
    return render_to_response('citizendialer3000/campaign_detail.html', data,
                              context_instance=RequestContext(request))

def contact_detail(request, slug, contact_id):

    campaign = get_object_or_404(Campaign, slug=slug)
    contact = get_object_or_404(Contact, campaign=campaign, pk=contact_id)
    
    if request.method == 'POST':
        
        call = Call(contact=contact)
        form = CallForm(request.POST, instance=call)
        
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('call_complete', args=[slug]))
        else:
            #### generate error message from form errors?
            messages.error(request, 'Whoops, something went wrong.')
    
    else:
        form = CallForm()
        
    data = {
        'campaign': campaign,
        'contact': contact,
        'form': form,
    }

    return render_to_response('citizendialer3000/campaign_detail.html', data,
                              context_instance=RequestContext(request))

def complete(request, slug):
    data = {
        'campaign': get_object_or_404(Campaign, slug=slug),
    }
    return render_to_response('citizendialer3000/complete.html', data)

@login_required
def results(request, slug):
    
    if not request.user.is_staff:
        return HttpResponseForbidden('You are not allowed to view this page')
        
    data = {
        'campaign': get_object_or_404(Campaign, slug=slug),
    }
    return render_to_response('citizendialer3000/results.html', data)
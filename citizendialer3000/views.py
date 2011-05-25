from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from sunlightapi import sunlight
from citizendialer3000.forms import CallForm
from citizendialer3000.models import Campaign, Contact, Call
import json
import re
import tablib

KEY_PREFIX = getattr(settings, 'CD3000_KEY_PREFIX', 'CD3000')
TIMEOUT = getattr(settings, 'CD3000_CACHE_TIMEOUT', 60 * 10) # 10 minutes
ZIPCODE_RE = re.compile(r'^\d{5}$')

sunlight.apikey = getattr(settings, 'CD3000_SUNLIGHTAPI_KEY')

def callcampaign_list(request):
    """ Displays all publicly available campaigns.
    
        Context:
            campaigns   - query set of public campaigns
        
        Template:
            citizendialer3000/campaign_list.html
    """
    
    data = {'campaigns': Campaign.objects.filter(is_public=True)}
    return render_to_response('citizendialer3000/campaign_list.html', data,
                              context_instance=RequestContext(request))

def callcampaign_detail(request, slug):
    """ Display summary info and zipcode search box for campaign
        specified by slug.
        
        If a zipcode query string paramter is present, contacts will be pulled
        from the Sunlight Labs Congress API. The zipcode will be stored in the
        user session for use later in the process.
        
        Context:
            campaign    - the current campaign
            contacts    - list of contacts, if zipcode has been provided
            zipcode     - if provided
        
        Template:
            citizendialer3000/campaign_detail.html
    """
    
    campaign = get_object_or_404(Campaign, slug=slug)
    if not campaign.is_public:
        return HttpResponseRedirect(reverse('call_list'))
    
    data = {
        'campaign': campaign,
        'called': request.session.get("%s.called" % campaign.slug, []),
    }
    
    if campaign.is_complete:
        # campaign is complete, show the wrapup message
        # include final results if you want to show them
        contacts = campaign.contacts.all().annotate(Count("calls")).order_by('-calls__count')
        data['contacts'] = contacts
    
    elif 'zipcode' in request.GET:
        
        zipcode = request.GET['zipcode']
        request.session['cd3000_zipcode'] = zipcode
        
        if not ZIPCODE_RE.match(zipcode):
            return HttpResponseForbidden('invalid zipcode')
        
        # get bioguide_ids from cache or sunlight api
        key = "%s_ZIPCODE_%s" % (KEY_PREFIX, zipcode)
        bids = cache.get(key)
        if bids is None:
            mocs = sunlight.legislators.allForZip(zipcode)
            bids = [moc.bioguide_id for moc in mocs]
            cache.set(key, bids, TIMEOUT)
        
        contacts = Contact.objects.filter(campaign=campaign, bioguide_id__in=bids).annotate(Count("calls"))
        
        if request.is_ajax():
            # send back JSON response on ajax call
            content = json.dumps({
                'zipcode': zipcode,
                'contacts': [c.as_dict() for c in contacts],
            })
            return HttpResponse(content, mimetype='application/json')
            
        else:
            data['zipcode'] = zipcode
            data['contacts'] = contacts
        
    return render_to_response('citizendialer3000/campaign_detail.html', data,
                              context_instance=RequestContext(request))

def contact_detail(request, slug, bioguide_id):
    """ Show call script and response form for a particular contact. Response
        form values are stored in the user session so we can prepopulate
        the form on the next call.
    
        Context:
            campaign    - the campaign
            contact     - the contact
            form        - the response form
        
        Template:
            citizendialer3000/contact_detail.html
    """

    campaign = get_object_or_404(Campaign, slug=slug)
    
    if campaign.is_complete:
        return HttpResponseRedirect(reverse('callcampaign_detail', args=[slug]))
    elif not campaign.is_public:
        return HttpResponseRedirect(reverse('callcampaign_list'))
        
    contact = get_object_or_404(Contact, bioguide_id=bioguide_id)
    
    if request.method == 'POST':
        
        call = Call(contact=contact)
        form = CallForm(request.POST, instance=call)
        
        request.session.set_expiry(0)
        request.session['cd3000_firstname'] = request.POST.get('caller_first_name', None)
        request.session['cd3000_lastname'] = request.POST.get('caller_last_name', None)
        request.session['cd3000_email'] = request.POST.get('caller_email', None)
        
        if form.is_valid():
            
            form.save()
            
            # add list of called to session
            session_key = "%s.called" % campaign.slug
            called = request.session.get(session_key, [])
            called.append(contact.bioguide_id)
            request.session[session_key] = called
            
            return HttpResponseRedirect(reverse('call_complete', args=[slug]))
            
        else:
            #### generate error message from form errors?
            messages.error(request, 'Whoops, something went wrong.')
    
    else:
        form = CallForm(initial={
            'position': contact.position,
            'caller_first_name': request.session.get('cd3000_firstname', None),
            'caller_last_name': request.session.get('cd3000_lastname', None),
            'caller_email': request.session.get('cd3000_email', None),
            'caller_zipcode': request.session.get('cd3000_zipcode', None),
        })
        
    data = {
        'campaign': campaign,
        'contact': contact,
        'form': form,
    }

    return render_to_response('citizendialer3000/contact_detail.html', data,
                              context_instance=RequestContext(request))

def complete(request, slug):
    """ The "thanks" page after response form submission.
        
        Context:
            campaign    - the campaign
            zipcode     - the zipcode of the caller
            first_name  - the first name of the caller
            last_name   - the last name of the caller
            email       - email address of the caller
        
        Template:
            citizendialer3000/complete.html
    """
    
    data = {
        'campaign': get_object_or_404(Campaign, slug=slug),
        'zipcode': request.session.get('cd3000_zipcode', None),
        'first_name': request.session.get('cd3000_firstname', None),
        'last_name': request.session.get('cd3000_lastname', None),
        'email': request.session.get('cd3000_email', None),
    }
    return render_to_response('citizendialer3000/complete.html', data)

@login_required
def results(request, slug):
    """ A staff-only results page.
        
        Context:
            campaign    - the campaign
            calls       - all calls associated with the campaign
        
        Template:
            citizendialer3000/results.html
    """
    
    if not request.user.is_staff:
        return HttpResponseForbidden('You are not allowed to view this page')
        
    campaign = get_object_or_404(Campaign, slug=slug)
    data = {
        'campaign': campaign,
        'calls': Call.objects.filter(contact__campaign=campaign),
    }
    return render_to_response('citizendialer3000/results.html', data)

@login_required
def results_calls(request, slug):
    """ Return a CSV of calls.
    """
    
    if not request.user.is_staff:
        return HttpResponseForbidden('You are not allowed to view this page')
    
    campaign = get_object_or_404(Campaign, slug=slug)
    calls = Call.objects.filter(contact__campaign=campaign).select_related()
    
    data = tablib.Dataset(headers=[
        'contact','bioguide_id','position','first_name','last_name',
        'zipcode','email','notes','timestamp'])
    
    for call in calls:
        data.append((
            call.contact.full_name(),
            call.contact.bioguide_id,
            call.get_position_display(),
            call.caller_first_name,
            call.caller_last_name,
            call.caller_zipcode,
            call.caller_email,
            call.notes,
            call.timestamp,
        ))
    
    return HttpResponse(data.csv, mimetype='text/csv')

@login_required
def results_summary(request, slug):
    """ Return a CSV of calls.
    """
    
    if not request.user.is_staff:
        return HttpResponseForbidden('You are not allowed to view this page')
    
    campaign = get_object_or_404(Campaign, slug=slug)    
    contacts = campaign.contacts.all().annotate(Count("calls")).order_by('-calls__count')
    
    data = tablib.Dataset(headers=[
        'call_count','title','first','last','bioguide_id','state','party','phone'])
    
    for contact in contacts:
        data.append((
            contact.calls__count,
            contact.title,
            contact.first_name,
            contact.last_name,
            contact.bioguide_id,
            contact.state,
            contact.party,
            contact.phone,
        ))
    
    return HttpResponse(data.csv, mimetype='text/csv')
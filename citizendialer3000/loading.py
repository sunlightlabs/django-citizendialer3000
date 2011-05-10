from citizendialer3000 import *
from citizendialer3000.models import Campaign, Contact
from django.conf import settings
from sunlightapi import sunlight

sunlight.apikey = getattr(settings, 'CD3000_SUNLIGHTAPI_KEY')

TITLES = {
    HOUSE: 'Rep',
    SENATE: 'Sen',
}

PARTIES = {
    DEMOCRAT: 'D',
    REPUBLICAN: 'R',
    INDEPENDENT: 'I',
}

def load_sunlightapi(campaign, party=None, state=None, chamber=None, bioguide_ids=None):
    
    params = {'in_office': 1}
    
    if party:
        params['party'] = PARTIES[party]
    
    if state:
        params['state'] = state
    
    if chamber:
        params['title'] = TITLES[chamber]
    
    if bioguide_ids:
        params['bioguide_id'] = bioguide_ids
    
    for leg in sunlight.legislators.getList(**params):
        
        try:
            contact = Contact.objects.get(campaign=campaign, bioguide_id=leg.bioguide_id)
        except Contact.DoesNotExist:
            contact = Contact.objects.create(
                campaign=campaign,
                bioguide_id=leg.bioguide_id,
                title=leg.title,
                first_name=leg.firstname,
                last_name=leg.lastname,
                nickname=leg.nickname,
                gender=leg.gender,
                state=leg.state,
                party=leg.party,
                phone=leg.phone,
            )
    
    
from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify
from citizendialer3000 import *
from citizendialer3000.loading import load_sunlightapi
from citizendialer3000.models import Campaign, Contact
from optparse import make_option
import sys

class Command(BaseCommand):
    args = '<campaign_id>'
    help = 'Load congressional contacts from the Sunlight Labs Congress API'
    option_list = BaseCommand.option_list + (
        make_option('--campaigns', action='store_true', dest='list_campaigns', default=False,
                    help='List available campaigns and their IDs.'),
        make_option('-n', '--newcampaign', action='store', type='string', dest='campaign', metavar='TITLE',
                    help='Create a new campaign with the given title.'),
        make_option('-d', '--drop', action='store_true', dest='drop', default=False,
                    help='Delete existing contacts and calls for campaign.'),
        make_option('-b', '--bioguide', action='store', type='string', dest='bioguide', metavar='ID[,ID...]',
                    help='Filter by bioguide ID. Separate multiple values with a comma.'),
        make_option('-c', '--chamber', action='store', type='string', dest='chamber',
                    help='Filter by chamber: H, S'),
        make_option('-p', '--party', action='store', type='string', dest='party',
                    help='Filter by party: D, R, I'),
        make_option('-s', '--state', action='store', type='string', dest='state',
                    help='Filter by state: two-letter abbreviation'),
    )
    
    def handle(self, *args, **options):
        
        if options['list_campaigns']:
            
            campaigns = Campaign.objects.all()
            
            sys.stdout.write("Available campaigns:\n")
            
            for c in campaigns:
                sys.stdout.write("%s\t%s\n" % (c.pk, c.title))
            
        else:
            
            if len(args) > 0 and options['campaign']:
                raise CommandError('You may specify only one of campaign id argument or -n option')
            
            if len(args) == 0 and not options['campaign']:
                raise CommandError('You must specify a campaign id argument or -n option. Use --campaigns to see a list of available campaigns.')
                    
            if options['campaign']:
                campaign = Campaign.objects.create(
                    title=options['campaign'],
                    slug=slugify(options['campaign'])
                )
            else:
                try:
                    campaign = Campaign.objects.get(pk=args[0])
                except Campaign.DoesNotExist:
                    raise CommandError("Campaign %s not found. Use --campaigns to see a list of available campaigns." % campaign_id)
                
                
            if options['drop']:
                Contact.objects.filter(campaign=campaign).delete()
                
            kwargs = {}
            
            if options['party']:
                party = options['party'].upper()
                if not party in PARTIES:
                    raise CommandError('Party option must be one of D, R, or I. You entered %s.' % party)
                kwargs['party'] = PARTIES[party]
            
            if options['state']:
                kwargs['state'] = options['state']
            
            if options['chamber']:
                chamber = options['chamber'].upper()
                if not chamber in CHAMBERS:
                    raise CommandError('Chamber option must be one of H or S. You entered %s.' % chamber)
                kwargs['chamber'] = CHAMBERS[chamber]
                
            if options['bioguide']:
                kwargs['bioguide_ids'] = options['bioguide'].split(',')
            
            load_sunlightapi(campaign, **kwargs)
                
        
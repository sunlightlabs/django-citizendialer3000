from django.core.management.base import BaseCommand, CommandError
from citizendialer3000 import *
from citizendialer3000.models import Campaign, Contact
import csv
import sys

class Command(BaseCommand):
    args = '<campaign_id> <csv_path>'
    help = 'Load congressional contacts from a CSV'
    
    def handle(self, *args, **options):
        
        try:
            campaign = Campaign.objects.get(pk=args[0])
        except Campaign.DoesNotExist:
            raise CommandError("Campaign %s not found. Use --campaigns to see a list of available campaigns." % campaign_id)
        
        for record in csv.DictReader(sys.stdin):
            
            c = Contact(campaign=campaign)
            
            for key, value in record.iteritems():
                if hasattr(c, key):
                    setattr(c, key, value)
            
            c.save()
            
            sys.stdout.write("Saved %s %s (%s-%s)\n" % (c.first_name, c.last_name, c.party, c.state))

from django.contrib.localflavor.us.models import USStateField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime

# model definitions

POSITIONS = (
    ('?', 'unknown'),
    ('+', 'supports'),
    ('-', 'opposes'),
)

class Campaign(models.Model):
    title = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)
    content = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=datetime.datetime.utcnow)
    
    is_public = models.BooleanField(default=False, help_text="Campaign is visible to the public")
    is_complete = models.BooleanField(default=False, help_text="Campaign is open for responses")
    
    script = models.TextField(blank=True,
        help_text="Script to be read when representative's position is unknown")
    support_script = models.TextField(blank=True,
        help_text="Script to be read when representative supports campaign")
    oppose_script = models.TextField(blank=True,
        help_text="Script to be read when representative opposes campaign")
    
    yes_response = models.TextField(blank=True,
        help_text="Script to be read on positive response")
    no_response = models.TextField(blank=True,
        help_text="Script to be read on negative response")
    other_response = models.TextField(blank=True,
        help_text="Script to be read on other response")
        
    wrapup = models.TextField(blank=True,
        help_text="Text to be shown once campaign is complete")
        
    use_photos = models.BooleanField(default=True, help_text="Use bioguide photos")
    
    class Meta:
        ordering = ('title',)
    
    def __unicode__(self):
        return self.title
        
    @models.permalink
    def get_absolute_url(self):
        return ('citizendialer3000.views.callcampaign_detail', (self.slug,))

class Contact(models.Model):
    campaign = models.ForeignKey(Campaign, related_name='contacts')
    bioguide_id = models.CharField(max_length=16)
    title = models.CharField(max_length=8)
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=64)
    nickname = models.CharField(max_length=32)
    gender = models.CharField(max_length=1)
    state = USStateField()
    party = models.CharField(max_length=1)
    phone = models.CharField(max_length=16)
    
    position = models.CharField(max_length=1, choices=POSITIONS, default='?')
    call_goal = models.IntegerField(default=0)
    
    class Meta:
        ordering = ('last_name','first_name')
        unique_together = ('campaign','bioguide_id')
    
    def __unicode__(self):
        return u"%s %s" % (self.first_name, self.last_name)
        
    @models.permalink
    def get_absolute_url(self):
        return ('citizendialer3000.views.contact_detail', (self.campaign.slug, self.bioguide_id))
    
    def full_name(self):
        return u"%s %s" % (
            self.nickname or self.first_name,
            self.last_name,
        )
    
    def bio_name(self):
        return u"%s. %s %s (%s-%s)" % (
            self.title,
            self.nickname or self.first_name,
            self.last_name,
            self.party,
            self.state,
        )
    
    def as_dict(self):
        return {
            'campaign': self.campaign_id,
            'bioguide_id': self.bioguide_id,
            'title': self.title,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'nickname': self.nickname,
            'gender': self.gender,
            'state': self.state,
            'party': self.party,
            'phone': self.phone,
            'full_name': self.full_name(),
            'bio_name': self.bio_name(),
        }

class Call(models.Model):
    contact = models.ForeignKey(Contact, related_name='calls')
    position = models.CharField(max_length=1, choices=POSITIONS, default='?')
    caller_first_name = models.CharField(max_length=32, blank=True)
    caller_last_name = models.CharField(max_length=64, blank=True)
    caller_email = models.EmailField(blank=True)
    caller_zipcode = models.CharField(max_length=5, blank=True)
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=datetime.datetime.utcnow)
    
    class Meta:
        ordering = ('-timestamp',)
    
    def __unicode__(self):
        return self.position

# signal handlers

@receiver(post_save, sender=Campaign)
def campaignsave_callback(sender, **kwargs):
    from citizendialer3000.loading import load_sunlightapi
    if kwargs.get('created', False):
        load_sunlightapi(kwargs['instance'])
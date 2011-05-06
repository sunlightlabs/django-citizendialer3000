from django.contrib.localflavor.us.models import USStateField
from django.db import models
import datetime

POSITIONS = (
    ('?', 'unknown'),
    ('+', 'supports'),
    ('-', 'opposes'),
)

class Campaign(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()
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
    
    class Meta:
        ordering = ('title',)
    
    def __unicode__(self):
        return self.title

class Contact(models.Model):
    campaign = models.ForeignKey(Campaign, related_name='contacts')
    bioguide_id = models.CharField(max_length=16)
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=64)
    state = USStateField()
    
    position = models.CharField(choices=POSITIONS, default='?')
    call_goal = models.IntegerField(default=0)
    
    
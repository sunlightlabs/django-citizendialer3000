========================
django-citizendialer3000
========================

Are you an influential issue-based advocacy organization? Do you often find
yourself needing to mount a massive calling campaign to members of Congress?
Do you use Django? If you're thinking "That sounds like me!", then
citizendialer3000 is going to make your life much easier.

citizendialer3000 is a Django application that makes it simple to launch and
run call campaigns. First, create a new campaign from Django's admin interface
and enter the call script. Once public, users can find their representatives
by zipcode and are walked through the process of calling their representatives.
Finally, users are asked to record the result of their call.

http://github.com/sunlightlabs/django-citizendialer3000

------------
Requirements
------------

* django >= 1.2.0
* django.contrib.messages

-------------
Configuration
-------------

settings.py
===========

Add to *INSTALLED_APPS*::

    'citizendialer3000'

CD3000_SUNLIGHTAPI_KEY
    Your API key

CD3000_KEY_PREFIX (optional)
    Override default cache key prefix

CD3000_CACHE_TIMEOUT (optional)
    Override default cache timeout

cache
=====

Results from Sunlight API calls are cached using Django's cache API. Please
have it properly configured so it will work.

----------------
Loading Contacts
----------------

When a new campaign is created using the Django admin, citizendialer3000
automatically loads the campaign with all currently serving members of
congress. Since you may only need a subset of representatives, a handy
management command is provided to load contacts from the Sunlight Labs
Congress API::

    Usage: ./manage.py importcontacts [options] <campaign_id>

    Load congressional contacts from the Sunlight Labs Congress API

    Options:
      --campaigns           List available campaigns and their IDs.
      -n TITLE, --newcampaign=TITLE
                            Create a new campaign with the given title.
      -d, --drop            Delete existing contacts and calls for campaign.
      -b ID[,ID...], --bioguide=ID[,ID...]
                            Filter by bioguide ID. Separate multiple values with a
                            comma.
      -c CHAMBER, --chamber=CHAMBER
                            Filter by chamber: H, S
      -p PARTY, --party=PARTY
                            Filter by party: D, R, I
      -s STATE, --state=STATE
                            Filter by state: two-letter abbreviation

You must either specify a campaign_id argument or use the -n option to create
a new campaign. To see a list of campaigns and their IDs, run with the
--campaigns option.

The -d option will remove any contacts already associated with the campaign.
**It will also delete all calls associated with the campaign.**

Running without any other options will import all current members of congress.
Filter by bioguide ID, party, state, or chamber as needed.
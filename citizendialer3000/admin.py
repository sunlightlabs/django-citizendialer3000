from django.contrib import admin
from citizendialer3000.models import Campaign, Contact, Call

class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title','is_public','is_complete')
    list_filter = ('is_public','is_complete')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title',)
    
admin.site.register(Campaign, CampaignAdmin)


class CallInline(admin.TabularInline):
    fields = ('position','caller_name','notes','timestamp')
    readonly_fields = ('timestamp',)
    model = Call

class ContactAdmin(admin.ModelAdmin):
    inlines = (CallInline,)
    list_display = ('campaign','bio_name','bioguide_id','phone','position','call_goal')
    list_display_links = ('bio_name',)
    list_filter = ('campaign','position','party','state')
    search_fields = ('first_name','last_name','nickname','phone')

admin.site.register(Contact, ContactAdmin)
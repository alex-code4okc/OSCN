from django.contrib import admin
from .models import party, judge, attorney, event, issue, DocketEntry, ProtectiveOrder
# Register your models here.
admin.site.empty_value_display = '-Empty-'

@admin.register(party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ['name','children','plaintiff','defendant']
    list_filter = ['name','children','plaintiff','defendant']
    list_max_show_all = 200
    list_per_page = 200

@admin.register(judge)
class JudgeAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(attorney)
class AttorneyAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['event']

@admin.register(issue)
class IssueAdmin(admin.ModelAdmin):
   list_display = ['issue_number']

@admin.register(DocketEntry)
class DocketEntryAdmin(admin.ModelAdmin):
    list_display = ['date','code','description']    

@admin.register(ProtectiveOrder)
class ProtectiveOrderAdmin(admin.ModelAdmin):
    list_display = ['po_number','filed_date','closed_date','judge']    

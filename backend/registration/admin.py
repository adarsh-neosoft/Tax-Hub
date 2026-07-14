from django.contrib import admin

from registration.models import DscTracker
from registration.models import PoaTracker
from registration.models import OpinionManagement
from registration.models import ValuationReportManagement

admin.site.register(DscTracker)
admin.site.register(PoaTracker)
admin.site.register(OpinionManagement)
admin.site.register(ValuationReportManagement)
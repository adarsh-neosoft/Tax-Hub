from django.contrib import admin

from registration.models import DscTracker
from registration.models import PoaTracker
from registration.models import OpinionManagement
from registration.models import ValuationReportManagement
from registration.models import FormManagement
from registration.models import ComplianceManagement
from registration.models import ItrStatusManagement
from registration.models import DocumentVault

admin.site.register(DscTracker)
admin.site.register(PoaTracker)
admin.site.register(OpinionManagement)
admin.site.register(ValuationReportManagement)
admin.site.register(FormManagement)
admin.site.register(ComplianceManagement)
admin.site.register(ItrStatusManagement)
admin.site.register(DocumentVault)
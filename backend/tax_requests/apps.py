from django.apps import AppConfig


class TaxRequestsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tax_requests"

    def ready(self):
        import tax_requests.signals  # noqa: F401
        self._patch_workflow_permissions()

    def _patch_workflow_permissions(self):
        from workflow import engine
        from tax_requests.workflow_permissions import can_user_act_on_tds_opinion

        original = engine.can_user_act

        def can_user_act(instance, user):
            if getattr(instance.content_type, "model", None) == "tdsopinion":
                return can_user_act_on_tds_opinion(instance, user)
            return original(instance, user)

        engine.can_user_act = can_user_act

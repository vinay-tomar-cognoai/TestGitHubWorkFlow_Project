from EasyAssistApp.models import CobrowseAccessToken


def disable_dyte_integration():
    for access_token_obj in CobrowseAccessToken.objects.all():
        access_token_obj.enable_cognomeet = False
        access_token_obj.save(update_fields=["enable_cognomeet"])


print("Running disable_dyte_integration...\n")

disable_dyte_integration()

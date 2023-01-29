from LiveChatApp.models import LiveChatCustomer, LiveChatCobrowsingData
from EasyAssistApp.models import CobrowseIO


def update_cobrowsing_nps_data_for_livechat():
    cobrowse_objs = LiveChatCobrowsingData.objects.all()
    for cobrowse_obj in cobrowse_objs:
        try:
            req_cobrowse_obj = CobrowseIO.objects.filter(
                session_id=cobrowse_obj.cobrowse_session_id).first()
            if req_cobrowse_obj:
                cobrowse_obj.rating = req_cobrowse_obj.agent_rating
                cobrowse_obj.text_feedback = req_cobrowse_obj.client_comments

                cobrowse_obj.save(update_fields=['rating', 'text_feedback'])
                print(
                    f"Updated for LiveChatCobrowsingData cobrowse_session_id: {cobrowse_obj.cobrowse_session_id}")
        except Exception as e:
            print(
                f"Failed to update for LiveChatCobrowsingData cobrowse_session_id: {cobrowse_obj.cobrowse_session_id} with error: {str(e)}")

# Fuctions calls to be executed in the mentioned order


print("Running update_cobrowsing_nps_data_for_livechat...\n")

update_cobrowsing_nps_data_for_livechat()

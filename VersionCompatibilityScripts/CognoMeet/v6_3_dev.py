from CognoMeetApp.models import *


def create_timer_and_config_objects():
    access_token_objs = CognoMeetAccessToken.objects.all()
    for access_token_obj in access_token_objs:
        
        if not CognoMeetTimers.objects.filter(cogno_meet_access_token=access_token_obj).first():
            CognoMeetTimers.objects.create(cogno_meet_access_token=access_token_obj)
        
        if not CognoMeetConfig.objects.filter(cogno_meet_access_token=access_token_obj).first():
            CognoMeetConfig.objects.create(cogno_meet_access_token=access_token_obj)
        

print("Running create_timer_and_config_objects...\n")

create_timer_and_config_objects()

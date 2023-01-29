from EasyChatApp.models import AuditTrail, Intent, EasyChatTheme
from EasyChatApp.constants import DELETE_INTENT_ACTION
import json

audit_trail_objs = AuditTrail.objects.filter(action=DELETE_INTENT_ACTION)

for obj in audit_trail_objs:
    data = json.loads(obj.data)
    if "change_data" in data:
        continue
    intent_pk_list = data["intent_pk_list"]
    count = 0
    intent_name_list = []
    for intent_pk in intent_pk_list:
        count += 1
        intent_obj = Intent.objects.get(pk=int(intent_pk))
        intent_name_list.append({
            "number": count,
            "intent_name": intent_obj.name,
        })
        bot_obj = intent_obj.bots.all()[0]

    audit_trail_data = json.dumps({
        "intent_pk_list": intent_pk_list,
        "change_data": intent_name_list,
        "bot_pk": str(bot_obj.pk),
    })
    obj.data = audit_trail_data
    obj.save()

EasyChatTheme.objects.create(
    main_page="EasyChatApp/theme1_bot.html", chat_page="EasyChatApp/theme1.html")

APP_NAMES = (
    ("EASYASSISTAPP", "Cobrowsing"),
    ("EASYCHATAPP", "ChatBot"),
    ("EASYTMSAPP", "CognoDesk"),
    ("LIVECHATAPP", "LiveChat"),
    ("DEVELOPERCONSOLEAPP", "DeveloperConsole")
)

EASYASSIST_ACTION_TYPES = (
    ("Login", "Login"),
    ("Logout", "Logout"),
    ("Add-User", "Add-User"),
    ("Delete-User", "Delete-User"),
    ("Change-Settings", "Change-Settings"),
    ("Change-App-Config", "Change-App-Config"),
    ("Updated-User", "Updated-User"),
    ("Upload-Document", "Upload-Document"),
    ("Delete-Document", "Delete-Document"),
    ("Activate-User", "Activate-User"),
    ("Password-Resent", "Password-Resent"),
    ("EnableEmailAnalyticsSettings", "EnableEmailAnalyticsSettings"),
    ("DisableEmailAnalyticsSettings", "DisableEmailAnalyticsSettings"),
    ("CreateEmailAnalyticsProfile", "CreateEmailAnalyticsProfile"),
    ("UpdateEmailAnalyticsProfile", "UpdateEmailAnalyticsProfile"),
    ("DeleteEmailAnalyticsProfile", "DeleteEmailAnalyticsProfile"),
)

EASYTMS_ACTION_TYPES = (
    ("User-Presence-Status", "User-Presence-Status"),
)

EASYCHAT_ACTION_TYPES = (
    ("BOT_CREATED", "BOT_CREATED"),
    ("BOT_DELETED", "BOT_DELETED")
)

DEVELOPERCONSOLE_ACTION_TYPES = (
    ("Edit-White-Labeling-Config", "Edit-White-Labeling-Config"),
)

ACTION_TYPES = ()
ACTION_TYPES += EASYASSIST_ACTION_TYPES
ACTION_TYPES += EASYTMS_ACTION_TYPES
ACTION_TYPES += EASYCHAT_ACTION_TYPES
ACTION_TYPES += DEVELOPERCONSOLE_ACTION_TYPES

EXPORT_CHOICES = (
    ("AuditTrailExport", "AuditTrailExport"),
)

COMMON_DATE_FORMAT = "%Y-%m-%d"

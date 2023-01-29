from django.conf import settings

STATIC_EMAIL_TRIGGER_COUNT = 5  # Total number of static email can be triggered from UI in 1 hour

ANALYTICS_FOLDER_PATH = settings.MEDIA_ROOT + "EasyAssistApp/analytics_img/"

ANALYTICS_FOLDER_RELATIVE_PATH = "files/EasyAssistApp/analytics_img/"

EMAIL_SUBJECT = "Your requested co-browsing report"

Declined_Leads = "Declined Leads"
Follow_up_Leads = "Follow-up Leads"
Request_Attended = "Request Attended"
Request_Unattended = "Request Unattended"
Customer_Converted_through_URL = "Customers Converted through URL"
Customer_Converted_by_agent = "Customers Converted by Agent"

Captured_Leads = "Captured Leads"

LINES_MARKERS = "lines+markers"

RECORDS_ATTACHMENTS = [
    {
        "id": "attended_leads",
        "name": "Attended Leads",
        "is_enabled": True,
    },
    {
        "id": "unattended_leads",
        "name": "Unattended Leads",
        "is_enabled": True,
    },
    {
        "id": "declined_leads",
        "name": Declined_Leads,
        "is_enabled": True,
    },
    {
        "id": "followup_leads",
        "name": Follow_up_Leads,
        "is_enabled": True,
    },
    {
        "id": "agent_wise_reports",
        "name": "Agent Wise Reports",
        "is_enabled": True,
    },
]

COUNT_VARIATION_LIST = (
    ("daily", "Daily"),
    ("wtd", "Week to Date (WTD)"),
    ("mtd", "Month to Date (MTD)"),
    ("ytd", "Year to Date (YTD)"),
)

RECORDS_ANALYTICS_TABLE = [
    # Inbound
    {
        "id": "inbound",
        "name": "Inbound",
        "is_enabled": True,
        "categories": [
            {
                "id": "request_initiated",
                "name": "Request Initiated",
                "is_enabled": True,
            },
            {
                "id": "request_attended",
                "name": Request_Attended,
                "is_enabled": True,
            },
            {
                "id": "request_unattended",
                "name": Request_Unattended,
                "is_enabled": True,
            },
            {
                "id": "followup_leads",
                "name": Follow_up_Leads,
                "is_enabled": True,
            },
            {
                "id": "customer_converted",
                "name": Customer_Converted_by_agent,
                "is_enabled": True,
            },
            {
                "id": "customers_converted_by_url",
                "name": Customer_Converted_through_URL,
                "is_enabled": True,
            },
            {
                "id": "declined_leads",
                "name": Declined_Leads,
                "is_enabled": True,
            },
            {
                "id": "request_assistance_avg_wait_time",
                "name": "Avg. Waiting time for requesting Assistance",
                "is_enabled": True,
            },
            {
                "id": "avg_session_time",
                "name": "Avg. Session time",
                "is_enabled": True,
            },
            {
                "id": "unique_customers",
                "name": "Unique Customers",
                "is_enabled": True,
            },
            {
                "id": "repeated_customers",
                "name": "Repeated Customers",
                "is_enabled": True,
            }
        ],
    },
    # Outbound - Search Leads
    {
        "id": "outbound_search_leads",
        "name": "Outbound - Search Leads",
        "is_enabled": True,
        "categories": [
            {
                "id": "lead_searched",
                "name": "Lead Searched",
                "is_enabled": True,
            },
            {
                "id": "request_attended",
                "name": Request_Attended,
                "is_enabled": True,
            },
            {
                "id": "request_unattended",
                "name": Request_Unattended,
                "is_enabled": True,
            },
            {
                "id": "customers_converted_by_agent",
                "name": Customer_Converted_by_agent,
                "is_enabled": True,
            },
            {
                "id": "customers_converted_by_url",
                "name": Customer_Converted_through_URL,
                "is_enabled": True,
            },
            {
                "id": "declined_leads",
                "name": "Declined Leads",
                "is_enabled": True,
            },
            {
                "id": "captured_leads",
                "name": Captured_Leads,
                "is_enabled": True,
            },
            {
                "id": "unique_customers",
                "name": "Unique Customers",
                "is_enabled": True,
            },
            {
                "id": "repeated_customers",
                "name": "Repeated Customers",
                "is_enabled": True,
            }
        ],
    },
    # Outbound - Generate droplink
    {
        "id": "outbound_gdl",
        "name": "Outbound - GDL",
        "is_enabled": True,
        "categories": [
            {
                "id": "request_initiated",
                "name": "Request Initiated",
                "is_enabled": True,
            },
            {
                "id": "request_attended",
                "name": Request_Attended,
                "is_enabled": True,
            },
            {
                "id": "request_unattended",
                "name": Request_Unattended,
                "is_enabled": True,
            },
            {
                "id": "customer_converted",
                "name": Customer_Converted_by_agent,
                "is_enabled": True,
            },
            {
                "id": "customers_converted_by_url",
                "name": Customer_Converted_through_URL,
                "is_enabled": True,
            },
            {
                "id": "declined_leads",
                "name": Declined_Leads,
                "is_enabled": True,
            },
            {
                "id": "avg_session_time",
                "name": "Avg. Session Time",
                "is_enabled": True,
            },
        ],
    },
    # support
    {
        "id": "support",
        "name": "Support",
        "is_enabled": True,
        "categories": [
            {
                "id": "attended",
                "name": "Attended",
                "is_enabled": True,
            },
            {
                "id": "unattended",
                "name": "Unattended",
                "is_enabled": True,
            },
            {
                "id": "declined",
                "name": "Declined",
                "is_enabled": True,
            },
            {
                "id": "followup_leads",
                "name": Follow_up_Leads,
                "is_enabled": True,
            },
            {
                "id": "customers_converted_by_agent",
                "name": Customer_Converted_by_agent,
                "is_enabled": True,
            },
            {
                "id": "customers_converted_by_url",
                "name": Customer_Converted_through_URL,
                "is_enabled": True,
            },
            {
                "id": "meeting_support_history",
                "name": "Meeting Support History",
                "is_enabled": True,
            },
        ],
    },
]

RECORDS_ANALYTICS_GRAPH = [
    # General Analytics
    {
        "name": "General Analytics",
        "id": "general_analytics",
        "is_enabled": True,
        "categories": [
            # Request Details
            {
                "name": "Request Details",
                "id": "request_details",
                "is_enabled": True,
                "categories": [
                    {
                        "name": "Initiated",
                        "id": "initiated",
                        "is_enabled": True,
                    },
                    {
                        "name": "Attended",
                        "id": "attended",
                        "is_enabled": True,
                    },
                    {
                        "name": "Converted",
                        "id": "converted",
                        "is_enabled": True,
                    },
                ],
            },
            # Customer Session Details
            {
                "name": "Customer Session Details",
                "id": "customer_session_details",
                "is_enabled": True,
                "categories": [],
            },
        ],
    },
    # Inbound Analytics
    {
        "name": "Inbound Analytics",
        "id": "inbound_analytics",
        "is_enabled": True,
        "categories": [
            # Service Request Analytics
            {
                "name": "Service Request Analytics",
                "id": "service_request_analytics",
                "is_enabled": True,
                "categories": [
                    {
                        "name": "Leads Captured",
                        "id": "lead_captured",
                        "is_enabled": True,
                    },
                    {
                        "name": Request_Attended,
                        "id": "request_attended",
                        "is_enabled": True,
                    },
                    {
                        "name": "Customer Converted",
                        "id": "customer_converted",
                        "is_enabled": True,
                    },
                    {
                        "name": "Request Declined",
                        "id": "request_declined",
                        "is_enabled": True,
                    },
                ],
            }
        ],
    },
    # Outbound Analytics
    {
        "name": "Outbound Analytics",
        "id": "outbound_analytics",
        "is_enabled": True,
        "categories": [
            # Service Request Analytics
            {
                "name": "Service Request Analytics",
                "is_enabled": True,
                "id": "service_request_analytics",
                "categories": [
                    {
                        "name": "Leads Captured",
                        "id": "lead_captured",
                        "is_enabled": True,
                    },
                    {
                        "name": Request_Attended,
                        "id": "request_attended",
                        "is_enabled": True,
                    },
                    {
                        "name": "Customer Converted",
                        "id": "customer_converted",
                        "is_enabled": True,
                    },
                    {
                        "name": "Request Declined",
                        "id": "request_declined",
                        "is_enabled": True,
                    },
                ],
            }
        ],
    },
]

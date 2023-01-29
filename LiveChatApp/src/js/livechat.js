import { initialize_console, show_customers_tab, show_email_customers_tab, check_user_has_assigned_chats } from "./agent/console";
import { create_agent_socket, update_agent_websocket_token } from "./agent/livechat_agent_socket";
import {
    send_message_to_user,
    append_livechat_file_upload_modal,
    upload_file_attachment,
    activate_mic,
    reset_file_upload_modal,
} from "./agent/chatbox_input";

import {
    transfer_chat_modal_open,
    transfer_chat_to_another_agent,
    mark_chat_session_expired,
    open_customer_details,
    close_customer_details,
    close_livechat_console,
    preview_livechat_attachment_image,
    close_livechat_attachment_image,
    on_chat_history_div_scroll,
    on_chat_history_div_scroll_chat_area,
    openHistory,
    add_agent_modal_open,
    invite_guest_agent_to_chat,
    guest_agent_session_accept,
    guest_agent_session_reject,
    guest_agent_exit_chat,
    load_resolve_chat_form,
    guest_agent_filter_list,
    open_request_status_modal,
    scroll_to_bottom,
    load_raise_ticket_form,
    hide_mics_for_iOS
} from "./agent/chatbox";

import {
    open_profile_page,
    mark_user_offline,
    show_offline_reasons_modal,
    save_agent_settings,
    go_back_mobile,
    mark_user_online,
    check_and_mark_online,
    remove_selected_language_agent_settings,
} from "./agent/settings";

import {
    livechat_continous_update,
    download_chat_transcript,
    submit_filter,
    export_mis_filter,
    offline_message_report_filter,
    submit_offline_or_abandoned_or_declined_message_report_filter,
    login_logout_report_filter,
    apply_reports_filter,
    export_reports_filter,
    submit_session_report_filter,
    agent_not_ready_report_filter,
    submit_agent_not_ready_report_filter,
    agent_performance_report_filter,
    submit_agent_performance_report_filter,
    daily_interaction_report_filter,
    submit_daily_interaction_report_filter,
    hourly_interaction_report_filter,
    submit_hourly_interaction_report_filter,
    submit_livechat_analytics_filter,
    analytics_filter,
    load_livechat_analytics_all_charts,
    unset_livechat_filter_in_local_storage,
    abandoned_chats_report_filter,
    total_declined_chats_report_filter,
    submit_livechat_live_analytics_filter,
    update_daily_peak_hour_analytics_graph_and_data_table,
    update_cumulative_peak_hours_analytics_graph
} from "./admin/analytics";
import {
    switch_from_nps_graph,
    switch_from_avg_handle_time_graph,
    switch_from_avg_queue_time_graph,
    switch_from_inter_per_chat_graph,
} from "./admin/utils_analytics";
import {
    add_blacklisted_keyword,
    edit_keyword,
    delete_blacklisted_agent,
    remove_selected_blacklisted_keyword,
    on_click_blacklisted_checkbox,
    select_all_blacklisted_keyword_handler,
    download_create_blacklisted_keyword_template,
    submit_blacklisted_keywords_excel,
    reset_blacklisted_keyword_upload_modal,
} from "./admin/blacklisted_keywords";

import {
    manage_agents_continuous,
    save_admin_system_settings,
    save_admin_interaction_settings,
    load_system_setting,
    load_interaction_setting,
    open_upload_agents_modal,
    submit_agents_excel_onclick,
    download_create_agent_template_onclick,
    send_otp_code,
    check_otp,
    on_admin_otp_verification_modal_hide,
    on_otp_form_keypress,
    on_otp_form_keyup,
    livechat_agent_category_onchange,
    livechat_agent_category_edit_onchange,
    add_category_chips_edit_modal,
    edit_agent_info,
    create_agent,
    cancel_agent_modal,
    open_delete_agent_modal,
    close_delete_agent_modal,
    delete_agent,
    update_bot_list,
    toggle_agent_switch_by_admin_supervisor,
    supervisor_to_agent_switch,
    show_livechat_theme,
    auto_chat_disposal_toggle_handler,
    user_terminates_chat_toggle_handler,
    session_inactivity_toggle_handler,
    toggle_initiate_call_from_customer,
    check_select_chat_history_report_type,
    check_livechat_audit_custom_date_range,
    check_livechat_audit_date_range,
    toggle_followup_lead_sources,
    handle_whatsapp_followup_paramaters_visibility,
    get_livechat_user_category
} from "./admin/general_admin_functions";

import {
    create_only_admin,
    edit_livechat_only_admin_info,
    delete_livechat_only_admin,
    download_create_livechat_only_admin_template,
    submit_livechat_only_admin_excel,
} from "./admin/only_admin";

import {
    resetTimer,
    send_session_timeout_request,
    update_user_last_seen,
    apply_calender_filter,
    set_character_count,
    check_chat_requests_queue,
} from "./common";
import {
    go_to_one_on_one_chat,
    initialize_internal_console,
    send_message_handler,
    upload_internal_file_attachment,
    reset_file_upload_modal as reset_internal_chat_modal,
    toggle_agent_search_bar,
    search_users,
    toggle_add_member_dropdown,
    add_user_to_user_group,
} from "./common/livechat_internal_chat_console.js";
import {
    select_all_canned_handler,
    create_canned_response,
    edit_canned_response,
    delete_canned_agent,
    on_canned_checkbox,
    delete_canned_response,
    download_create_canned_response_template,
    submit_canned_response_excel,
    reset_canned_response_upload_modal,
} from "./common/canned_response";

import {
    open_change_webhook_confirm_modal,
    get_whatsapp_webhook_default_code,
    save_whatsapp_webhooks_content,
    change_webhook_code,
    reset_whatsapp_webhook_code,
    auto_save_webhook_code,
    continue_collaborative_coding,
} from "./common/whatsapp_webhook_console";

import {
    bot_changed,
    go_to_developer_editor,
    save_processor,
    run_processor_livechat,
    go_full_screen,
} from "./admin/developer_settings";

import {
    category_checkbox_click,
    edit_livechat_category,
    create_livechat_category,
    delete_livechat_category,
    select_public_category_type,
    select_private_category_type,
    select_all_category_handler,
} from "./admin/livechat_category";

import {
    add_holiday_calender,
    delete_calender_event,
    edit_calender_event,
    add_working_hours,
    set_default_calender,
    load_calendar_for_other_months,
    prev_next_month_calendar,
} from "./admin/calender";

import {
    append_file_to_agent,
    get_masked_message,
    append_customer_message,
    append_agent_message,
    archive_submit_filter,
    show_tagging_details,
    append_supervisor_file_archive,
    append_supervisor_message_archive,
} from "./common/archive_customer";

import {
    initiate_internet_speed_detection,
    initialize_page,
    is_mobile,
    toggle_side_bar,
    get_url_vars,
} from "./utils";

import {
    create_socket_ongoing_chat,
    hide_message_reply_notification_function,
} from "./agent/livechat_chat_socket";

import { 
    create_chat_group, 
    filterList, set_group_icon, 
    open_agent_dropdown_list, 
    remove_selected_member, 
    select_member, 
    update_group_chat_list, 
    delete_group,
    remove_member_from_group,
    remove_group,
    leave_group,
    get_group_events,
    cancel_remove_member_from_group,
    reset_member_count,
} from "./admin/manage_group";

import {
    enable_disable_email_notification,
    save_email_profile,
    add_new_email_profile,
    enable_disable_table_container,
    enable_disable_graph_container,
    enable_disable_attachment_container,
    hideIcon,
    show_profile_details_tab,
    delete_email_profile,
    trigger_sample_mail,
    enable_disable_graph_chat_container,
    update_multiselect_checkboxes,
} from "./admin/email_settings";

import { 
    add_section, 
    initialize_form_builder, 
    save_dispose_chat_form, 
    initialize_raise_ticket_form_builder, 
    save_raise_ticket_form, 
    handle_image_upload_input_change,
    handle_image_cross_btn,
} from "./admin/form_builder";

import { sync_preview } from "./admin/form_preview";

import { 
    initialize_chat_history_table, 
    send_supervisor_message,
    reset_file_upload_modal_chathistory,
    upload_file_attachment_chathistory, 
    activate_supervisor_mic,
} from "./admin/chat_history";

import { 
    initialize_voip_history_table, 
    export_voip_filter,
} from "./common/voip_history";

import { 
    reply_on_message_function,
    cancel_reply_on_message_function,
 } from "./admin/realtime_chat_view";

import { join_meeting } from "./agent/voip/join_meeting";
import { accept_customer_request_for_voip, connect_voip_call, reject_customer_request_for_voip, send_voip_request_to_customer } from "./agent/voip/voip";
import { end_voip_calling, toggle_audio } from "./agent/voip/join_meeting_pip";

import { send_vc_request_to_customer, generate_video_meet_link, join_guest_agent_to_call, change_color_ratingv_bar, change_color_ratingz_bar, change_color_ratingz_bar_all, save_livechat_feedback_text, set_value_to_some, save_feedback } from "./agent/vc/livechat_vc";

import { initialize_queue_requests_table, self_assign_request } from "./agent/queue_requests";
import { download_ms_integration_doc, save_configuration } from "./admin/integrations/ms_dynamics";
import { export_vc_filter, initialize_vc_history_table } from "./common/vc_history";

import { livechat_raise_ticket, livechat_search_ticket, livechat_get_previous_tickets, show_tms_enablement_toast } from "./agent/ticket";

import { check_for_transcript } from "./agent/console";

import { 
    translate_messages,
    show_original_text,
    show_translated_text,
    hide_mobile_language_translate_prompt,
    show_mobile_language_translate_prompt
    } from "./agent/language_translation";
import { check_cobrowse_agent_exists, connect_agent_to_cobrowsing, force_end_cobrowsing, is_cobrowsing_ongoing, join_cobrowsing_session, send_cobrowsing_request_to_customer } from "./agent/cobrowsing/manage_cobrowsing";
import { export_cobrowsing_filter, initialize_cb_history_table } from "./common/cobrowsing_history";

import { 
    initialize_followup_leads_table, 
    load_followup_raise_ticket_form,
    livechat_followup_raise_ticket,
    transfer_chat_to_email_conversations,
    reinitiate_whatsapp_conversation,
     } from "./common/followup_leads";

import { 
    chat_escalation_warn_user,
    chat_escalation_report_user,
    hide_chat_escalation_notification,
    chat_escalation_ignore_notification,
 } from "./common/chat_escalation";

 import {
    initialize_reported_users_table,
    show_user_block_confirmation_modal,
 } from "./admin/chat_escalation/reported_users"; 

 import {
    initialize_blocked_users_table,
 } from "./admin/chat_escalation/blocked_users"; 

 import {
    filter_function,
 } from "./agent/country_code";

 import {
    submit_agent_analytics_filter,
    load_agent_analytics_by_filter,
    unset_agent_analytics_filter_in_local_storage,
} from "./agent/analytics";

const state = {
    agent_endpoints: [
        "/livechat/",
        "/livechat/get-archived-customer-chat/",
        "/livechat/agent-profile/",
        "/livechat/canned-response/",
        "/livechat/calender/",
        "/livechat/agent-settings/",
        "/livechat/internal-chat/",
        "/livechat/voip-history/",
        "/livechat/followup-leads/",
        "/livechat/requests-in-queue/",
        "/livechat/cobrowsing-history/",
        "/livechat/vc-history/",
        "/livechat/agent-analytics/",
    ],
    is_dropdown_open: false
};

const app = () => {

    if (window.location.pathname.includes('agent-vc-meeting-end')) {
        return;
    }

    initialize_page();
    check_cobrowse_agent_exists();
    if (state.agent_endpoints.includes(window.location.pathname)) {
        initialize_console(
            window.AGENT_WEBSOCKET_TOKEN,
            window.ASSIGNED_CUSTOMER_COUNT,
            window.AGENT_FULL_NAME,
            window.AGENT_USERNAME,
            window.CURRENT_STATUS,
            window.LIVECHAT_THEME_COLOR,
            window.LIVECHAT_THEME_COLOR_LIGHT,
            window.LIVECHAT_THEME_COLOR_LIGHT_ONE,
            window.CANNED_ARR,
            window.IS_NOTIFICATION_ENABLE,
            window.BLACKLISTED_KEYWORD,
            window.SENDER_WEBSOCKET_TOKEN,
            window.CUSTOMER_BLACKLISTED_KEYWORD,
        );
    } else {

        // update_agent_websocket_token("74a65650-2902-4d43-8eb4-d68fa8eeb4dd123");
        create_agent_socket();
    }

    initialize_internal_console();

    if (window.location.pathname == "/livechat/analytics/") {
        livechat_continous_update();
        setInterval(function () {
            livechat_continous_update();
        }, 5000);
        load_livechat_analytics_all_charts();
    } else {
        unset_livechat_filter_in_local_storage();
    }

    if (window.location.pathname.includes('/livechat/agent-analytics')) {
        load_agent_analytics_by_filter();
    } else {
        unset_agent_analytics_filter_in_local_storage();
    }
    

    if(window.location.href.includes('livechat-form-builder')) {
        initialize_form_builder();
    }

    if(window.location.href.includes('raise-ticket-form-builder')) {
        initialize_raise_ticket_form_builder();
    }

    setInterval(update_user_last_seen, 5000);

    add_event_listeners();

    if (window.innerWidth <= 767) {
        // in the below listener if the nav bar is open and a click is performed anywhere on the page then the nav bar is closed
        document.addEventListener("click", function (event) {
            var parent = $(event.target).closest("#accordionSidebar, #sidebarToggleTop");
            if (parent.length === 0) {
                if (!document.getElementById("accordionSidebar").classList.contains('toggled')) {
                    document.getElementById("sidebarToggleTop").click();
                }
            }
        });
    }

    if (window.location.pathname.includes('chat-history')) {
        initialize_chat_history_table(1);
    }
    if (window.location.pathname.includes('voip-history')) {
        initialize_voip_history_table(1);
    }
    if (window.location.pathname.includes('vc-history')) {
        initialize_vc_history_table(1);
    }
    if (window.location.pathname.includes('cobrowsing-history')) {
        initialize_cb_history_table(1);
    }
    if (window.location.pathname.includes('voice-meeting')) {
        join_meeting();
    }
    if (window.location.pathname.includes('requests-in-queue')) {
        initialize_queue_requests_table(1);
    }
    if (window.location.pathname.includes('followup-leads')) {
        initialize_followup_leads_table(1);
    }
    if (window.location.pathname.includes('reported-users')) {
        initialize_reported_users_table(1);
    }
    if (window.location.pathname.includes('blocked-users')) {
        initialize_blocked_users_table(1);
    }

    update_group_chat_list({
        is_member_removed: false,
        is_member_added: false,
        user_group_id: null,
    });

    check_chat_requests_queue();
    setInterval(check_chat_requests_queue, 5000);
};

$(document).ready(() => {
    app();
});

(function ($) {
    $(function () {
        $(".dropdown-trigger").dropdown({
            constrainWidth: false,
            alignment: "left",
        });

        $(".tooltipped").tooltip({
            position: "top",
        });

        $(".readable-pro-tooltipped").tooltip({
            position: "top",
        });

        $(".tooltipped").tooltip();
        $(".tooltipped").tooltip({
            position: "top",
        });
        if (is_mobile()) {
            $("#web-switch").hide();
            $("#mobile-switch").show();
        }
    }); // end of document ready
})(jQuery); // end of jQuery name space

function add_event_listeners() {
    if (window.addEventListener) {
        window.addEventListener("load", initiate_internet_speed_detection, false);
    } else if (window.attachEvent) {
        window.attachEvent("onload", initiate_internet_speed_detection);
    }

    $(document).on("click", ".blacklisted-checkbox", function (e) {
        on_click_blacklisted_checkbox();
    });

    $(document).on("click", "#select-all-blacklisted", function (e) {
        select_all_blacklisted_keyword_handler(e.target);
    });

    if (window.location.href.match(window.location.origin + "/livechat/manage-agents/")) {
        setInterval(function () {
            manage_agents_continuous();
        }, 5000);
    }

    $("#admin-otp-verification-modal").on("hidden.bs.modal", function () {
        on_admin_otp_verification_modal_hide();
    });

    $(".otp-form").on("keypress", function (e) {
        let key_index = false;
        key_index = on_otp_form_keypress(e);
        return key_index;
    });

    $(".otp-form").on("keyup", function (e) {
        on_otp_form_keyup(e);
    });

    $("#livechat-agent-category").on("change", function (e) {
        livechat_agent_category_onchange(e);
    });

    $(".livechat-agent-category-edit").on("change", function (e) {
        livechat_agent_category_edit_onchange(e);
    });

    $("#masking-enabled").on("change", send_otp_code);

    $(document).on("click", "#submit_agents_excel", function (e) {
        submit_agents_excel_onclick();
    });

    $("#download_create_agent_template").on("click", function () {
        download_create_agent_template_onclick();
    });

    $("#export-mis-filter").click(function () {
        export_mis_filter();
    });
    $("#export-voip-history").click(function(){
       export_voip_filter();
    });

    $("#export-vc-history").click(function(){
        export_vc_filter();
     });
    
    $("#offline-message-report-filter").click(function () {
        offline_message_report_filter();
    });
    $("#abandoned-chats-report-filter").click(function () {
        abandoned_chats_report_filter();
    });
    $("#total-declined-chats-report-filter").click(function () {
        total_declined_chats_report_filter();
    });
    
    $("#daily-interaction-report-filter").click(function () {
        daily_interaction_report_filter();
    });

    $("#download-create-livechat-only-admin-template").click(function () {
        download_create_livechat_only_admin_template();
    });

    $(document).on("click", "#submit-livechat-only-admin-excel", function (e) {
        submit_livechat_only_admin_excel();
    });
    try {
        $(document).on("change", "#indeterminate-checkbox-all", function () {
            let is_checked = false;
            if (document.getElementById("indeterminate-checkbox-all").checked) {
                is_checked = true;
            }

            for (let idx = 0; idx < 7; idx++) {
                document.getElementById("indeterminate-checkbox-" + idx).checked = is_checked;
            }
        });

        for (var i = 0; i < 7; i++) {
            $(document).on("change", "#indeterminate-checkbox-" + i, function () {
                var flag = 0
                for (let idx = 0; idx < 7; idx++) {
                    if (!document.getElementById("indeterminate-checkbox-" + idx).checked) {
                        flag = 1
                        break;
                    }
                }
                if (flag == 0) {
                    document.getElementById("indeterminate-checkbox-all").checked = true
                }
                else {
                    document.getElementById("indeterminate-checkbox-all").checked = false
                }

            });
        }
    } catch (err) {
        console.log(err);
    }

    $(document).on("change", "#supervisor-to-agent-switch", function () {
        supervisor_to_agent_switch();
    });

    $(document).on("click", ".canned-checkbox", function (e) {
        on_canned_checkbox();
    });

    $(document).on("click", "#canned-delete-btn", function (e) {
        document.getElementById("delete_selected_canned_modal").style.display = "block";
    });

    $("#download_create_canned_response_template").click(function () {
        download_create_canned_response_template();
    });

    $(document).on("click", "#submit_canned_response_excel", function (e) {
        submit_canned_response_excel();
    });

    $(document).on("click", "#select-all-canned", function (e) {
        select_all_canned_handler(e.target);
    });

    $(document).on("click", "#select-all-category", function (e) {
        select_all_category_handler(e.target);
    });

    $(document).on("click", ".category-checkbox", function (e) {
        category_checkbox_click();
    });

    $(document).on("click", "#delete_selected_category", function (e) {
        $("#delete_selected_category_div").modal("open");
    });

    $(document).on("change", "#auto_chat_disposal_enabled", function (e) {
        auto_chat_disposal_toggle_handler(e.target);
    });

    $(document).on("change", "#user_terminates_chat_enabled", function (e) {
        user_terminates_chat_toggle_handler(e.target);
    });

    $(document).on("change", "#session_inactivity_enabled", function (e) {
        session_inactivity_toggle_handler(e.target);
    });

    // if agent is online and someone opens the modal of marking offline
    // and then instead of cancel agent clicks outside to close the modal.
    $("#modal-agent-current-status").on("hidden.bs.modal", function (e) {
        check_and_mark_online();
    });

    $(document).on("keyup", '.show-char-count', function (e) {
        set_character_count(e.target);
    });
    $('.livechat-agent-max-customer-allowed').on('paste', function (event) {
        if (event.originalEvent.clipboardData.getData('Text').match(/[^\d]/)) {
            event.preventDefault();
        }
    });
    $(document).on("click", '#go_full_screen', () => {
        go_full_screen();
    })
    // $(document).on("click", (e) =>{
    //     if (state.is_dropdown_open && $(e.target).closest(".wrapper-box").length === 0 && $(e.target).closest(".multiselect-options-container").length === 0) {
    //         $(".wrapper-box").trigger('click');
    //         state.is_dropdown_open = false;
    //     } else if ($(e.target).closest(".wrapper-box").length != 0){
    //         state.is_dropdown_open = !state.is_dropdown_open;
    //         return;
    //     }
    // })
    if (typeof String.prototype.trim !== "function") {
        String.prototype.trim = function () {
            return this.replace(/^\s+|\s+$/g, "");
        };
    }

    // Create Element.remove() function if not exist
    if (!("remove" in Element.prototype)) {
        Element.prototype.remove = function () {
            if (this.parentNode) {
                this.parentNode.removeChild(this);
            }
        };
    }
    $("#average_nps_card").click(function () {
        $(this).addClass("analytics-card-active");
        switch_from_nps_graph()
    });
    $("#interaction_perchat_card").click(function () {
        $(this).addClass("analytics-card-active");
        switch_from_inter_per_chat_graph()
    });
    $("#average_handletime_card").click(function () {
        $(this).addClass("analytics-card-active");
        switch_from_avg_handle_time_graph()
    });
    $("#average_customer_waittime_card").click(function () {
        $(this).addClass("analytics-card-active");
        switch_from_avg_queue_time_graph()
    });

    if (window.location.href.includes('internal-chat')) {
        setInterval(() => {
            const search_val = document.getElementById('groupchat-user-search-global').value;
            const events = get_group_events();

            let activity = false;
            for (const key in events) {
                if (events[key]) {
                    activity = true;
                    break;
                }
            }

            if (search_val == '' && !activity) {
                update_group_chat_list({is_member_added: false, is_member_removed: false, user_group_id: null});
            }
        }, 5000);
        
        $("#select-group-member-dropdown").multiselect({
            nonSelectedText: 'Select Members',
            enableFiltering: true,
            includeSelectAllOption: true,
            enableCaseInsensitiveFiltering: true,
            onChange: (event) => {
                select_member(event[0]);
            },
            onDropdownShow: (event) => {
                document.getElementById('livechat_added_members_list').style.display = 'none';

            },
            onDropdownHide: (event) => {
                document.getElementById('livechat_added_members_list').style.display = 'block';
            },
            onSelectAll: (event) => {

                if (event) reset_member_count();
                
                const selected_members = $('#select-group-member-dropdown').find("option");
                
                Array.from(selected_members).forEach(member => {
                    select_member(member);
                })
            },
        });    

        update_multiselect_checkboxes();
    
        $('.group-add-member-checkbox').on('change', function (e) {
            select_member(e.target);
        })
    
        $('#livechat-create-group-btn').on('click', function (e) {
            create_chat_group(e.target);
        })
    
        $('#member-options-search-box').on("keyup", function (e) {
            filterList(e.target.value, "members-box-options-container");
        });
    
        $('#group_image_icon').on('click', function () {
            document.getElementById('upload_group_image').click();
        })
    
        $('#upload_group_image').on('change', function (e) {
            set_group_icon(e.target);
        })

        $('#submit-response').on('click', function(e) {
            send_message_handler();
        })

        $('#delete_group__btn').on('click', function(e) {
            delete_group(e.target);
        })

        $('#remove_group_member_btn').on('click', function (e) {
            remove_member_from_group(e.target);
        })

        $('#cancel_remove_group_member_btn').on('click', function (e) {
            cancel_remove_member_from_group(e.target);
        })

        $('#remove_group_btn').on('click', function(e) {
            remove_group(e.target);
        })

        $('#leave_group_btn').on('click', function(e) {
            leave_group(e.target);
        })

        $('#livechat_agent_search_bar_toggle').on('click', function(e) {
            toggle_agent_search_bar();
        })

        $('#livechat-groupchat-agent-searchbar').on('keyup', function(e) {
            search_users(e.target.value);
        })

        $('#add-user-dropdown-wrapper').on('click', function () {
            toggle_add_member_dropdown();
        })

        $('#user-options-search-box').on("keyup", function (e) {
            filterList(e.target.value, "user-box-options-container");
        });

        $('#livechat-add-user-to-user-group-btn').on('click', function (e) {
            add_user_to_user_group();
        })
    }

    $('#livechat_add_form_section').on('click', function(e) {
        add_section();
    })

    $('#save-form-btn').on('click', function(e) {
        save_dispose_chat_form(e.target);
    })

    $('#sync_preview_btn').on('click', function(e) {
        sync_preview(e.target);
    })

    $('#livechat_call_type').on('change', function(e) {
        toggle_initiate_call_from_customer(e.target);
    })

    $('#voip_call_accept_btn').on('click', function(e) {
        accept_customer_request_for_voip();
    })

    $('#voip_call_reject_btn').on('click', function(e) {
        reject_customer_request_for_voip();
    })

    $('#voip_mute_audio').on('click', function(e) {
        toggle_audio();
    })

    $('#voip_end_call').on('click', function(e) {
        end_voip_calling();
    })

    $('#voip_call_normal_svg').on('click', function(e) {
        send_voip_request_to_customer(true);
    })

    $('#vc_call_normal_svg').on('click', function() {
        send_vc_request_to_customer(true);
    })

    $('#mobile_voip_connect_btn').on('click', function (e) {
        connect_voip_call();
    })

    $('#mobile_vc_connect_btn').on('click', function (e) {
        connect_voip_call();
    })

    $('#ms_dynamics_save_btn').on('click', () => {
        save_configuration();
    })

    $('#ms-integration-document-link').on('click', () => {
        download_ms_integration_doc();
    })

    $(".agent_language_dropdown, #agent_language_dropdown_mobile").on('change', function (e) {
        translate_messages(e.target.value);
    })

    $("#livechat_mobile_language_container_close").click(function() {
        hide_mobile_language_translate_prompt();
    });

    $("#livechat_langauge_container_show").click(function() {
        show_mobile_language_translate_prompt();
    });

    $('#guest_agent_call_connect_btn').on('click', function(e) {
        join_guest_agent_to_call();
    })

    $('#save-raise-ticket-form-btn').on('click', function(e) {
        save_raise_ticket_form(e.target);
    })

    $('#livechat_raise_ticket_btn').click( function(e) {
        load_raise_ticket_form();
    });

    $("#livechat-ticket-id").on("keypress", function (e) {
        if (event.keyCode === 13) {
            livechat_search_ticket();
        }
    });

    $("#enable-agent-raise-ticket").click(function(e) {
        show_tms_enablement_toast(e.target);
    });

    $('#transcript-submit-btn').click( function(e) {
        check_for_transcript();
    });

    $('#guest_agent_cobrowse_connect_btn').on('click', () => {
        join_cobrowsing_session();
    })

    $('#mobile_cb_normal_btn').on('click', () => {
        send_cobrowsing_request_to_customer();
    })

    $('#mobile_cobrowsing_connect_btn').on('click', () => {
        connect_agent_to_cobrowsing();
    })

    $('#export-cobrowsing-history').on('click', () => {
        export_cobrowsing_filter();
    })
    
    $('#enable_followup_lead').on('change', function(e) {
        toggle_followup_lead_sources(e.target);
    })

    $('#raise-ticket-btn').on('click', function(e) {
        load_followup_raise_ticket_form();
    })

    $('#livechat-web-resolve-btn').on('click', () => {
        if (is_cobrowsing_ongoing()) {
            $('#end-cobrowse-session').modal('show');
        } else {
            load_resolve_chat_form();
            $('#end-chat-session').modal('show');
        }
    })

    $('#livechat-mobile-resolve-btn').on('touchend', () => {
        if (is_cobrowsing_ongoing()) {
            $('#end-cobrowse-session').modal('show');
        } else {
            load_resolve_chat_form();
            $('#end-chat-session').modal('show');
        }
    })

    $('#force_end_cobrowsing_btn').on('click', () => {
        force_end_cobrowsing();
    })

    $("#blacklist-keyword-dropdown").on('change', function(e) {
        window.location.href = "?blacklist_for="+e.target.value;
    })

    $(".chat-escalation-back-btn").on('click', function(e) {
        window.location.href = "/livechat/chat-escalation/";  
    })

    $("#chat-escalation-warn-btn").on('click', function(e) {
        chat_escalation_warn_user(); 
    })

    $("#chat-escalation-report-confirm-btn").on('click', function(e) {
        chat_escalation_report_user(); 
    })

    $("#chat-escalation-warn-ignore-btn").on('click', function(e) {
        chat_escalation_ignore_notification('warn');
    })

    $("#chat-escalation-report-ignore-btn").on('click', function(e) {
        chat_escalation_ignore_notification('report');
    })

    $("#livechat-customers-tab-header").on('click', function(e) {
        show_customers_tab();
    })

    $("#livechat-email-customers-tab-header").on('click', function(e) {
        show_email_customers_tab();
    })

    $(".livechat-settings-reset-btn").on('click', function(e) {
        window.location.reload();
    })

    $("#livechat-whatsapp-followup-conversation-checkbox").on('change', function(e) {
        handle_whatsapp_followup_paramaters_visibility(e.target);
    })

    $(document).mouseup(function(e) {
        const container = $(".livechat-language-dropdown-wrapper");

        if (container.length != 0 && !container.is(e.target) && container.has(e.target).length === 0) {
            const language_div = $('.multiselect-options-container');

            if (language_div.hasClass('active')) {
                $('.wrapper-box').trigger('click');
            }
        }
    });


    $('#select_user_type').on('change', function (e) {
        const params = get_url_vars();
        
        window.location = `${window.location.origin}${window.location.pathname}?status=${params.status}&user_type=${e.target.value}`;
    })

    $("#download_create_blacklisted_keywords_template").click(function () {
        download_create_blacklisted_keyword_template();
    });

    $(document).on("click", "#submit_blacklisted_keywords_excel", function (e) {
        submit_blacklisted_keywords_excel(BLACKLIST_FOR);
    });

    $('#upload-bulk-keyword-modal').on('hidden.bs.modal', function (e) {
        reset_blacklisted_keyword_upload_modal();
    })

    $('#create-canned-response-using-excel-modal').on('hidden.bs.modal', function (e) {
        reset_canned_response_upload_modal();
    })

    $('#create-agent-using-excel-modal').on('hidden.bs.modal', function (e) {
        document.querySelector('#custom-text').innerHTML = 'No file chosen';
        document.getElementById('real-file').value = '';
    })
}

window.onload = function () {
    resetTimer();
    window.onmousemove = resetTimer;
    window.onmousedown = resetTimer;
    window.onclick = resetTimer;
    window.onkeypress = resetTimer;
    window.addEventListener("scroll", resetTimer, true);

    document.addEventListener(
        "visibilitychange",
        function () {
            if (document.hidden == false) {
                resetTimer();
            }
        },
        false
    );

    $(".date-picker").datepicker();

    setInterval(send_session_timeout_request, 3 * 60 * 1000);
    send_session_timeout_request();
    
    $(".selectpicker").attr("data-size","8");

    $('#end-chat-session').on("shown.bs.modal", function() {
        var modal_height = $("#end-chat-session .modal-body").height();
        if(modal_height < 115){
              $("#end-chat-session .modal-body").css("overflow-y","inherit");
        }
        else{
            $("#end-chat-session .modal-body").css("overflow-y","auto");
        }
      });
    
    hide_mics_for_iOS();
   
};

window.create_agent = create_agent;
window.cancel_agent_modal = cancel_agent_modal
window.open_upload_agents_modal = open_upload_agents_modal;
window.edit_agent_info = edit_agent_info;
window.save_admin_system_settings = save_admin_system_settings;
window.save_admin_interaction_settings = save_admin_interaction_settings;
window.send_otp_code = send_otp_code;
window.check_otp = check_otp;
window.add_blacklisted_keyword = add_blacklisted_keyword;
window.edit_keyword = edit_keyword;
window.delete_blacklisted_agent = delete_blacklisted_agent;
window.remove_selected_blacklisted_keyword = remove_selected_blacklisted_keyword;
window.submit_filter = submit_filter;
window.export_mis_filter = export_mis_filter;
window.offline_message_report_filter = offline_message_report_filter;
window.submit_offline_or_abandoned_or_declined_message_report_filter = submit_offline_or_abandoned_or_declined_message_report_filter;
window.login_logout_report_filter = login_logout_report_filter;
window.apply_reports_filter = apply_reports_filter;
window.export_reports_filter = export_reports_filter;
window.submit_session_report_filter = submit_session_report_filter;
window.agent_not_ready_report_filter = agent_not_ready_report_filter;
window.submit_agent_not_ready_report_filter = submit_agent_not_ready_report_filter;
window.agent_performance_report_filter = agent_performance_report_filter;
window.submit_agent_performance_report_filter = submit_agent_performance_report_filter;
window.daily_interaction_report_filter = daily_interaction_report_filter;
window.submit_daily_interaction_report_filter = submit_daily_interaction_report_filter;
window.hourly_interaction_report_filter = hourly_interaction_report_filter;
window.submit_hourly_interaction_report_filter = submit_hourly_interaction_report_filter;
window.submit_livechat_analytics_filter = submit_livechat_analytics_filter;
window.analytics_filter = analytics_filter;
window.open_delete_agent_modal = open_delete_agent_modal;
window.close_delete_agent_modal = close_delete_agent_modal;
window.delete_agent = delete_agent;
window.update_bot_list = update_bot_list;
window.toggle_agent_switch_by_admin_supervisor = toggle_agent_switch_by_admin_supervisor;
window.create_only_admin = create_only_admin;
window.edit_livechat_only_admin_info = edit_livechat_only_admin_info;
window.delete_livechat_only_admin = edit_livechat_only_admin_info;
window.download_create_livechat_only_admin_template = download_create_livechat_only_admin_template;
window.submit_livechat_only_admin_excel = submit_livechat_only_admin_excel;
window.create_canned_response = create_canned_response;
window.edit_canned_response = edit_canned_response;
window.delete_canned_agent = delete_canned_agent;
window.delete_canned_response = delete_canned_response;
window.bot_changed = bot_changed;
window.go_to_developer_editor = go_to_developer_editor;
window.save_processor = save_processor;
window.run_processor_livechat = run_processor_livechat;
window.edit_livechat_category = edit_livechat_category;
window.create_livechat_category = create_livechat_category;
window.delete_livechat_category = delete_livechat_category;
window.select_public_category_type = select_public_category_type;
window.select_private_category_type = select_private_category_type;
window.send_message_to_user = send_message_to_user;
window.append_livechat_file_upload_modal = append_livechat_file_upload_modal;
window.upload_file_attachment = upload_file_attachment;
window.activate_mic = activate_mic;
window.transfer_chat_modal_open = transfer_chat_modal_open;
window.add_agent_modal_open = add_agent_modal_open;
window.transfer_chat_to_another_agent = transfer_chat_to_another_agent;
window.invite_guest_agent_to_chat = invite_guest_agent_to_chat;
window.mark_chat_session_expired = mark_chat_session_expired;
window.open_profile_page = open_profile_page;
window.mark_user_offline = mark_user_offline;
window.show_offline_reasons_modal = show_offline_reasons_modal;
window.save_agent_settings = save_agent_settings;
window.go_back_mobile = go_back_mobile;
window.mark_user_online = mark_user_online;
window.apply_calender_filter = apply_calender_filter;
window.show_livechat_theme = show_livechat_theme;
window.download_chat_transcript = download_chat_transcript;
window.add_category_chips_edit_modal = add_category_chips_edit_modal;
window.open_customer_details = open_customer_details;
window.close_customer_details = close_customer_details;
window.close_livechat_console = close_livechat_console;
window.add_holiday_calender = add_holiday_calender;
window.delete_calender_event = delete_calender_event;
window.edit_calender_event = edit_calender_event;
window.add_working_hours = add_working_hours;
window.set_default_calender = set_default_calender;
window.load_calendar_for_other_months = load_calendar_for_other_months;
window.prev_next_month_calendar = prev_next_month_calendar;
window.append_customer_message = append_customer_message;
window.append_agent_message = append_agent_message;
window.get_masked_message = get_masked_message;
window.append_file_to_agent = append_file_to_agent;
window.archive_submit_filter = archive_submit_filter;
window.toggle_side_bar = toggle_side_bar;
window.check_user_has_assigned_chats = check_user_has_assigned_chats;
window.preview_livechat_attachment_image = preview_livechat_attachment_image;
window.close_livechat_attachment_image = close_livechat_attachment_image;
window.reset_file_upload_modal = reset_file_upload_modal;
window.create_socket_ongoing_chat = create_socket_ongoing_chat;
window.on_chat_history_div_scroll = on_chat_history_div_scroll;
window.on_chat_history_div_scroll_chat_area = on_chat_history_div_scroll_chat_area
window.openHistory = openHistory
window.guest_agent_session_accept = guest_agent_session_accept;
window.guest_agent_session_reject = guest_agent_session_reject;
window.guest_agent_exit_chat = guest_agent_exit_chat;
window.go_to_one_on_one_chat = go_to_one_on_one_chat;
window.upload_internal_file_attachment = upload_internal_file_attachment;
window.reset_internal_chat_modal = reset_internal_chat_modal;
window.enable_disable_email_notification = enable_disable_email_notification;
window.save_email_profile = save_email_profile;
window.add_new_email_profile = add_new_email_profile;
window.enable_disable_table_container = enable_disable_table_container;
window.enable_disable_graph_container = enable_disable_graph_container;
window.enable_disable_attachment_container = enable_disable_attachment_container;
window.hideIcon = hideIcon;
window.show_profile_details_tab = show_profile_details_tab;
window.delete_email_profile = delete_email_profile;
window.trigger_sample_mail = trigger_sample_mail;
window.enable_disable_graph_chat_container = enable_disable_graph_chat_container;
window.show_tagging_details = show_tagging_details;
window.guest_agent_filter_list = guest_agent_filter_list;
window.open_request_status_modal = open_request_status_modal;
window.reply_on_message_function = reply_on_message_function;
window.cancel_reply_on_message_function = cancel_reply_on_message_function;
window.send_supervisor_message = send_supervisor_message;
window.reset_file_upload_modal_chathistory = reset_file_upload_modal_chathistory;
window.upload_file_attachment_chathistory = upload_file_attachment_chathistory;
window.scroll_to_bottom = scroll_to_bottom;
window.hide_message_reply_notification_function = hide_message_reply_notification_function;
window.append_supervisor_file_archive = append_supervisor_file_archive;
window.append_supervisor_message_archive = append_supervisor_message_archive;
window.generate_video_meet_link = generate_video_meet_link;
window.activate_supervisor_mic = activate_supervisor_mic;
window.self_assign_request = self_assign_request;
window.open_change_webhook_confirm_modal = open_change_webhook_confirm_modal;
window.get_whatsapp_webhook_default_code = get_whatsapp_webhook_default_code;
window.save_whatsapp_webhooks_content = save_whatsapp_webhooks_content;
window.change_webhook_code = change_webhook_code;
window.reset_whatsapp_webhook_code = reset_whatsapp_webhook_code;
window.auto_save_webhook_code = auto_save_webhook_code;
window.continue_collaborative_coding = continue_collaborative_coding;
window.check_select_chat_history_report_type = check_select_chat_history_report_type;
window.check_livechat_audit_custom_date_range = check_livechat_audit_custom_date_range;
window.check_livechat_audit_date_range = check_livechat_audit_date_range;
window.change_color_ratingv_bar = change_color_ratingv_bar;
window.change_color_ratingz_bar = change_color_ratingz_bar;
window.change_color_ratingz_bar_all = change_color_ratingz_bar_all;
window.save_livechat_feedback_text = save_livechat_feedback_text;
window.set_value_to_some = set_value_to_some;
window.save_feedback = save_feedback;
window.remove_selected_language_agent_settings = remove_selected_language_agent_settings;
window.show_original_text = show_original_text;
window.show_translated_text = show_translated_text;
window.load_raise_ticket_form = load_raise_ticket_form;
window.handle_image_upload_input_change = handle_image_upload_input_change;
window.handle_image_cross_btn = handle_image_cross_btn;
window.livechat_raise_ticket = livechat_raise_ticket;
window.livechat_search_ticket = livechat_search_ticket;
window.livechat_get_previous_tickets = livechat_get_previous_tickets;
window.load_followup_raise_ticket_form = load_followup_raise_ticket_form;
window.livechat_followup_raise_ticket = livechat_followup_raise_ticket;
window.submit_livechat_live_analytics_filter = submit_livechat_live_analytics_filter;
window.transfer_chat_to_email_conversations = transfer_chat_to_email_conversations;
window.load_system_setting = load_system_setting;
window.load_interaction_setting = load_interaction_setting;
window.reinitiate_whatsapp_conversation = reinitiate_whatsapp_conversation;
window.get_livechat_user_category = get_livechat_user_category;
window.filter_function = filter_function;
window.submit_agent_analytics_filter = submit_agent_analytics_filter;
window.update_daily_peak_hour_analytics_graph_and_data_table = update_daily_peak_hour_analytics_graph_and_data_table;
window.update_cumulative_peak_hours_analytics_graph = update_cumulative_peak_hours_analytics_graph;
window.REPORT_WARNING_TEXT = "Note: Reports beyond 60 days will be sent over email within 24 hours";
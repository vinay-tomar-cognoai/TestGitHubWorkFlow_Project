function save_general_agent_settings(element) {

    let request_params = {
        "enable_chat_functionality": document.getElementById("enable_chat_functionality").checked,
        "enable_chat_bubble": document.getElementById("enable_chat_bubble").checked,
        "floating_button_position": document.getElementById("floating_button_position").value,
        "share_document_from_livechat": document.getElementById("share_document_from_livechat").checked,
        "allow_support_documents": document.getElementById("allow_support_documents").checked,
        "allow_only_support_documents": document.getElementById("allow_only_support_documents").checked,
        "enable_auto_offline_agent": document.getElementById("auto_offline_agent").checked,
        "display_agent_profile":document.getElementById("display_agent_profile").checked,
        "enable_preview_functionality": document.getElementById("enable-document-coview").checked,
    }

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/save-general-agent-settings/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                show_easyassist_toast("Saved successfully.");
                setTimeout(function() {
                    location.reload();
                }, 1000);
            } else {
                show_easyassist_toast("Unable to save the details");
            }
        }

        element.innerHTML = "Save";
    }
    
    xhttp.send(params);

}

function save_general_admin_settings(element) {

    var floating_button_left_right_position = document.getElementById("floating_button_left_right_position").value.trim();
    if(floating_button_left_right_position == "") {
        show_easyassist_toast("Please enter valid floating button position threshold");
        return;
    }

    var no_agent_connects_toast_threshold = document.getElementById("no_agent_connects_toast_threshold");
    if (no_agent_connects_toast_threshold && (no_agent_connects_toast_threshold.value <= 0 || no_agent_connects_toast_threshold.value > 60)) {
        show_easyassist_toast("No Agent connects session toast : Values between 1 and 60 are allowed.");
        return;
    }

    var auto_assign_unattended_lead_transfer_count = document.getElementById("auto_assign_unattended_lead_transfer_count");
    if (auto_assign_unattended_lead_transfer_count && (auto_assign_unattended_lead_transfer_count.value < 1 || auto_assign_unattended_lead_transfer_count.value > 30)) {
        show_easyassist_toast("Lead Transfer Count value should be between 1-30.");
        return;
    }

    if(document.getElementById("message_on_non_working_hours").value == "") {
        show_easyassist_toast("Non working hours message cannot be empty.");
        return;
    }

    var disable_connect_button_if_agent_unavailable = document.getElementById("disable_connect_button_if_agent_unavailable").checked;
    var message_if_agent_unavailable = document.getElementById("message_if_agent_unavailable").value;
    if (disable_connect_button_if_agent_unavailable && (!message_if_agent_unavailable || message_if_agent_unavailable.length == 0)) {
        show_easyassist_toast("Enter the required message to be shown to the customers to save the changes");
        return;
    }

    var product_category_list = document.getElementById("product_category_list").value;
    if ((document.getElementById("choose_product_category").checked || document.getElementById("enable_tag_based_assignment_for_outbound").checked) && (!product_category_list || product_category_list.length == 0)) {
        show_easyassist_toast("Enter the required fields in product category to save the changes");
        return;
    }

    let enable_greeting_bubble = document.getElementById("enable_greeting_bubble").checked;
    let greeting_bubble_text = document.getElementById("greeting_bubble_text").value.trim();
    let greeting_bubble_auto_popup_timer = document.getElementById("greeting_bubble_auto_popup_timer").value.trim();
    if(enable_greeting_bubble) {
        if(!parseInt(greeting_bubble_auto_popup_timer)){
            show_easyassist_toast("Number of times greeting bubble pops up cannot be 0 or empty");
            return;
        }

        if(!greeting_bubble_text.length) {
            show_easyassist_toast("Greeting bubble text cannot be empty");
            return;
        }

        if(!is_input_text_valid(greeting_bubble_text)) {
            show_easyassist_toast("Please enter a valid greeting bubble text (Only a-z A-z 0-9 .,@ are allowed)");
            return;
        }
    }

    var show_easyassist_connect_agent_icon = document.getElementById("show_easyassist_connect_agent_icon").checked;
    if (show_easyassist_connect_agent_icon && !window.is_icon_for_connect_with_agent) {
        show_easyassist_toast("Upload the logo to save the changes");
        return;
    }

    let field_stuck_event_handler = document.getElementById("field_stuck_event_handler")
    let enable_url_based_inactivity_popup = document.getElementById("enable_url_based_inactivity_popup")
    let allow_popup_on_browser_leave = document.getElementById("allow_popup_on_browser_leave")
    let enable_url_based_exit_intent_popup = document.getElementById("enable_url_based_exit_intent_popup")
    let show_exit_intent_url_error_message = false;
    let enable_recursive_browser_leave_popup = document.getElementById("enable_recursive_browser_leave_popup").checked;
    let exit_intent_popup_count_value = document.getElementById("exit-intent-popup-count").value.trim();
    let field_recursive_stuck_event_check = document.getElementById("field_recursive_stuck_event_check").checked;
    let inactivity_auto_popup_number = document.getElementById("inactivity_auto_popup_number").value.trim();
    let field_stuck_timer = parseInt(document.getElementById("field_stuck_timer").value.trim());

    if (allow_popup_on_browser_leave.checked) {
        if(enable_url_based_exit_intent_popup.checked) {
            let exit_intent_urls_button = document.getElementById("exit-intent-url-modal-button");
            if (exit_intent_urls_button.innerText == "Add URLs") {
                show_exit_intent_url_error_message = true;
            }
        }
        
        if(!enable_recursive_browser_leave_popup) {
            if(!exit_intent_popup_count_value.length || !parseInt(exit_intent_popup_count_value)) {
                show_easyassist_toast("Number of times Exit Intent should pop up cannot be empty or 0");
                return;
            }
        }
    }


    if (field_stuck_event_handler.checked) {
        if(enable_url_based_inactivity_popup.checked) {
            let urls_button = document.getElementById("inactivity-popup-url-modal-button")
            if (urls_button.innerText == "Add URLs") {
                if (show_exit_intent_url_error_message) {
                    show_easyassist_toast("No URLs configured for URL specific In-activity Popup and Exit Intent, please add at least one URL to continue");
                    return;
                } else {
                    show_easyassist_toast("No URLs configured for URL specific In-activity Popup, please add at least one URL to continue");
                    return;
                }
            }
        }

        if(!field_recursive_stuck_event_check) {
            if(!inactivity_auto_popup_number.length || !parseInt(inactivity_auto_popup_number)) {
                show_easyassist_toast("Number of times connect with an agent auto pop up after in-activity cannot be empty or 0");
                return;
            }

            if(!input_number_validator(parseInt(inactivity_auto_popup_number))) {
                show_easyassist_toast("Please enter number of times connect with an agent auto pop up after in-activity without special characters");
                return;
            }
        }

        if(!field_stuck_timer || field_stuck_timer <= 0 || field_stuck_timer > 3600) {
            show_easyassist_toast("Session in-activity time interval should be between 1-3600 seconds");
            return;
        }
    }

    if (show_exit_intent_url_error_message) {
        show_easyassist_toast("No URLs configured for URL specific Exit Intent, please add at least one URL to continue");
        return;
    }

    let maximum_active_leads = document.getElementById("maximum_active_leads").checked;
    let maximum_active_leads_threshold_value = document.getElementById("maximum_active_leads_threshold").value.trim();
    if(document.getElementById("enable_inbound").checked && maximum_active_leads && 
        !parseInt(maximum_active_leads_threshold_value)) {
        show_easyassist_toast("Maximum leads that can be assigned to an agent should be greater than 0");
        return;
    }
    
    // Uncomment the below line so that functionality can be enabled/disabled at the backend
    // let enable_proxy_cobrowsing = document.getElementById("enable-proxy-cobrowsing").checked;
    let enable_proxy_cobrowsing = false;
    let proxy_link_expire_time = parseInt(document.getElementById("link-expiry-time").value.trim());
    let enable_outbound_cobrowsing = document.getElementById("lead_generation").checked
    if(enable_outbound_cobrowsing && enable_proxy_cobrowsing) { 
        if(!proxy_link_expire_time || proxy_link_expire_time < 1 || proxy_link_expire_time > 1440){
            show_easyassist_toast("Link expiry time should be between 1-1440 minutes")
            return;
        }
    }

    let enable_auto_assign_to_one_agent = document.getElementById("enable_auto_assign_to_one_agent").checked;
    let auto_end_session_message = document.getElementById("auto_assign_lead_end_session_message").value.trim();

    let enable_auto_assign_unattended_lead = document.getElementById("enable_auto_assign_unattended_lead").checked;
    let auto_assign_unattended_lead_timer_input = document.getElementById("auto_assign_unattended_lead_timer_input").value.trim();
    let archive_on_unassigned_time_threshold = document.getElementById("auto-archive-lead-timer-input").value.trim();

    let unattended_lead_archive_timer_input = document.getElementById("unattended-lead-archive-timer-input").value.trim();
    if(enable_auto_assign_to_one_agent) {
        if(!auto_end_session_message.length) {
            show_easyassist_toast("Auto end session message cannot be empty");
            return;
        }

        if(!is_input_text_valid(auto_end_session_message)) {
            show_easyassist_toast("Please enter a valid auto end session message (Only a-z A-z 0-9 .,@ are allowed)");
            return;
        }

        if(!unattended_lead_archive_timer_input.length || !parseInt(unattended_lead_archive_timer_input)) {
            show_easyassist_toast("Auto end session timer cannot be empty or 0");
            return;
        }
    }

    if(enable_auto_assign_unattended_lead && !parseInt(auto_assign_unattended_lead_timer_input)) {
        show_easyassist_toast("Auto assign timer cannot be empty or 0");
        return;
    }

    if(!archive_on_unassigned_time_threshold.length || !parseInt(archive_on_unassigned_time_threshold)) {
        show_easyassist_toast("Auto archive timer cannot be empty or 0");
        return;
    }

    let request_params = {
        "enable_inbound": document.getElementById("enable_inbound").checked,
        "floating_button_bg_color": document.getElementById("floating_button_bg_color").value,
        "enable_greeting_bubble": enable_greeting_bubble,
        "greeting_bubble_auto_popup_timer": parseInt(greeting_bubble_auto_popup_timer),
        "greeting_bubble_text": remove_special_characters_from_str(stripHTML(document.getElementById("greeting_bubble_text").value)),
        "enable_lead_status": document.getElementById("enable_lead_status").checked,
        "maximum_active_leads": maximum_active_leads,
        "maximum_active_leads_threshold": parseInt(maximum_active_leads_threshold_value),
        "enable_auto_assign_unattended_lead": enable_auto_assign_unattended_lead,
        "auto_assign_unattended_lead_timer": remove_special_characters_from_str(stripHTML(auto_assign_unattended_lead_timer_input)),
        "auto_assign_unattended_lead_message": remove_special_characters_from_str(stripHTML(document.getElementById("auto_assign_unattended_lead_message").value)),
        "enable_auto_assign_to_one_agent": document.getElementById("enable_auto_assign_to_one_agent").checked,
        "auto_assigned_unattended_lead_archive_timer": remove_special_characters_from_str(stripHTML(document.getElementById("unattended-lead-archive-timer-input").value)),      
        "auto_assign_lead_end_session_message": remove_special_characters_from_str(stripHTML(document.getElementById("auto_assign_lead_end_session_message").value)),
        "show_floating_easyassist_button": document.getElementById("show_floating_easyassist_button").checked,
        "show_easyassist_connect_agent_icon": document.getElementById("show_easyassist_connect_agent_icon").checked,
        "show_only_if_agent_available": document.getElementById("show_only_if_agent_available").checked,
        "floating_button_left_right_position": floating_button_left_right_position,
        "assign_agent_under_same_supervisor": document.getElementById("assign_agent_under_same_supervisor").checked,
        "auto_assign_unattended_lead_transfer_count": remove_special_characters_from_str(stripHTML(document.getElementById("auto_assign_unattended_lead_transfer_count").value)),
        "allow_language_support": document.getElementById("allow_language_support").checked,
        "supported_language_list": document.getElementById("supported_language_list").value,
        "disable_connect_button_if_agent_unavailable": document.getElementById("disable_connect_button_if_agent_unavailable").checked,
        "enable_non_working_hours_modal_popup": document.getElementById("enable_non_working_hours_modal_popup").checked,
        "message_if_agent_unavailable": remove_special_characters_from_str(stripHTML(document.getElementById("message_if_agent_unavailable").value)),
        "message_on_non_working_hours": remove_special_characters_from_str(stripHTML(document.getElementById("message_on_non_working_hours").value)),
        "enable_followup_leads_tab": document.getElementById("enable_followup_leads_tab").checked,
        "choose_product_category": document.getElementById("choose_product_category").checked,
        "product_category_list": document.getElementById("product_category_list").value,
        "message_on_choose_product_category_modal": remove_special_characters_from_str(stripHTML(document.getElementById("message_on_choose_product_category_modal").value)),
        "connect_message": remove_special_characters_from_str(stripHTML(document.getElementById("connect_message").value)),
        "no_agent_connects_toast": document.getElementById("no_agent_connects_toast").checked,
        "no_agent_connects_toast_threshold": document.getElementById("no_agent_connects_toast_threshold").value,
        "no_agent_connects_toast_text": remove_special_characters_from_str(stripHTML(document.getElementById("no_agent_connects_toast_text").value)),
        "no_agent_connect_timer_reset_message": remove_special_characters_from_str(stripHTML(document.getElementById("no_agent_connect_timer_reset_message").value)),
        "no_agent_connect_timer_reset_count": remove_special_characters_from_str(stripHTML(document.getElementById("no_agent_connect_timer_reset_count").value)),
        "archive_on_unassigned_time_threshold": remove_special_characters_from_str(stripHTML(archive_on_unassigned_time_threshold)),
        "archive_message_on_unassigned_time_threshold": remove_special_characters_from_str(stripHTML(document.getElementById("auto-archive-popup-text").value.trim())),
        "field_stuck_event_handler": field_stuck_event_handler.checked,
        "enable_url_based_inactivity_popup": enable_url_based_inactivity_popup.checked,
        "field_recursive_stuck_event_check": field_recursive_stuck_event_check,
        "inactivity_auto_popup_number": inactivity_auto_popup_number,
        "field_stuck_timer": field_stuck_timer,
        "allow_popup_on_browser_leave": allow_popup_on_browser_leave.checked,
        "enable_recursive_browser_leave_popup": enable_recursive_browser_leave_popup,
        "enable_url_based_exit_intent_popup": enable_url_based_exit_intent_popup.checked,
        "exit_intent_popup_count": exit_intent_popup_count_value,
        "lead_generation": enable_outbound_cobrowsing,
        "enable_tag_based_assignment_for_outbound": document.getElementById("enable_tag_based_assignment_for_outbound").checked,
        "show_floating_button_after_lead_search": document.getElementById("show_floating_button_after_lead_search").checked,
        "allow_agent_to_customer_cobrowsing": document.getElementById("allow_agent_to_customer_cobrowsing").checked,
        "allow_agent_to_screen_record_customer_cobrowsing": document.getElementById("allow_agent_to_screen_record_customer_cobrowsing").checked,
        "allow_agent_to_audio_record_customer_cobrowsing": document.getElementById("allow_agent_to_audio_record_customer_cobrowsing").checked,
        "enable_request_in_queue": document.getElementById("enable_request_in_queue").checked,
        "enable_proxy_cobrowsing": enable_proxy_cobrowsing,
        "proxy_link_expire_time": proxy_link_expire_time,
        "allow_connect_with_virtual_agent_code": document.getElementById("allow-connect-with-virtual-agent-code").checked,
        "connect_with_virtual_agent_code_mandatory": document.getElementById("enable-virtual-agent-code-mandatory").checked
    }

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/save-general-admin-settings/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                if (document.getElementById("allow_agent_to_customer_cobrowsing").checked) {
                    show_easyassist_toast('Since the Reverse Cobrowsing toggle has been enabled, some of the settings will be disabled.')
                    setTimeout(function() {
                        location.reload();
                    }, 5000);
                } else {
                    show_easyassist_toast("Saved successfully");
                    setTimeout(function() {
                        location.reload();
                    }, 1000);
                }
            } else if( response.status == 302) {
                show_easyassist_toast(response.message);
            }else {
                show_easyassist_toast("Unable to save the details");
            }
        }

        element.innerHTML = "Save";
    }
    
    xhttp.send(params);

}

function save_general_customer_side_settings(element){
    var easyassit_font_family = document.getElementById("easyassit_font_family").value;
    var regex = /[+]/g;
    easyassit_font_family = easyassit_font_family.replace(regex, " ");

    let request_params = {
        "easyassit_font_family": easyassit_font_family,
    };

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/save-cobrowsing-meta-details/general/customer/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                show_easyassist_toast("Saved successfully.");
                setTimeout(function() {
                    location.reload();
                }, 1000);
            } else {
                show_easyassist_toast("Unable to save the details");
            }
        }

        element.innerHTML = "Save";
    }
    
    xhttp.send(params);
}

function save_general_console_settings(element) {

    var cobrowsing_console_theme_color_el = document.getElementById("cobrowsing-console-theme-color");
    var cobrowsing_console_theme_color = null;
    if (cobrowsing_console_theme_color_el.jscolor.toHEXString() != '#FFFFFF') {
        cobrowsing_console_theme_color = {
            "red": cobrowsing_console_theme_color_el.jscolor.rgb[0],
            "green": cobrowsing_console_theme_color_el.jscolor.rgb[1],
            "blue": cobrowsing_console_theme_color_el.jscolor.rgb[2],
            "rgb": cobrowsing_console_theme_color_el.jscolor.toRGBString(),
            "hex": cobrowsing_console_theme_color_el.jscolor.toHEXString(),
        };
    }

    var go_live_date = document.getElementById("go_live_date").value;
    if(!go_live_date) {
        show_easyassist_toast("Please enter valid Go-Live date");
        return;
    }
    go_live_date = get_iso_formatted_date(go_live_date);

    var white_listed_domains = document.getElementById("whitelisted_domain").value;
    if(white_listed_domains.length != 0) {
        let white_listed_domains_list = white_listed_domains.split(",")
        for (let link in white_listed_domains_list) {
            let is_valid = is_url_valid(white_listed_domains_list[link].trim())
            if (white_listed_domains_list[link].trim() == "*") is_valid = true;
            if (is_valid == false) {
                show_easyassist_toast("The entered URL in whitelisted domains field is not valid: " + white_listed_domains_list[link]);
                return;
            }
        }
    }

    var password_prefix_value = document.getElementById("cobrowsing_default_password_prefix").value;
    const regexPasswordPrefix = /^[0-9a-zA-Z]+$/;
    if (!password_prefix_value.match(regexPasswordPrefix)) {
        show_easyassist_toast("Password prefix can only comprise of alphabets and numbers.");
        return;
    }

    var deploy_chatbot_flag_element = document.getElementById("deploy_chatbot_flag");
    if (deploy_chatbot_flag_element.checked) {
        var deploy_chatbot_url = document.getElementById("deploy_chatbot_url").value;
        deploy_chatbot_url = stripHTML(deploy_chatbot_url);
        if(deploy_chatbot_url == ""){
            show_easyassist_toast("Chatbot CJS script cannot be empty.");
            return;
        }
        try{
            new window.URL(deploy_chatbot_url);
        } catch (error){
            console.error("ERROR: ", error);
            show_easyassist_toast("Chatbot CJS script is not valid. Please enter valid CJS script.");
            return
        }
    }

    let request_params = {
        "cobrowsing_console_theme_color": cobrowsing_console_theme_color,
        "go_live_date": go_live_date,
        "whitelisted_domain": document.getElementById("whitelisted_domain").value,
        "password_prefix": document.getElementById("cobrowsing_default_password_prefix").value,
        "deploy_chatbot_flag": document.getElementById("deploy_chatbot_flag").checked,
        "deploy_chatbot_url": stripHTML(document.getElementById("deploy_chatbot_url").value),
    };

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/save-general-console-settings/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                show_easyassist_toast("Saved successfully.");
                setTimeout(function() {
                    location.reload();
                }, 1000);
            } else {
                show_easyassist_toast("Unable to save the details");
            }
        }

        element.innerHTML = "Save";
    }
    
    xhttp.send(params);
}

function sales_cobrowse_agent_settings(element){

    if(document.getElementById("transfer_request_archive_time").value == 0) {
        show_easyassist_toast("Transfer request expiry should be greater than 0");
        return;
    }
    
    if(document.getElementById("transfer_request_archive_time").value > 600) {
        show_easyassist_toast("Transfer request expiry should not be greater than 600");
        return;
    }

    let request_params = {
        "enable_screenshot_agent": document.getElementById("enable_screenshot_agent").checked,
        "enable_invite_agent_in_cobrowsing": document.getElementById("enable_invite_agent_in_cobrowsing").checked,
        "enable_session_transfer_in_cobrowsing": document.getElementById("enable_session_transfer_in_cobrowsing").checked,
        "transfer_request_archive_time": remove_special_characters_from_str(stripHTML(document.getElementById("transfer_request_archive_time").value)),
        "enable_edit_access": document.getElementById("enable_edit_access").checked,
        "allow_video_calling_cobrowsing": document.getElementById("allow_video_calling_cobrowsing").checked,
        "customer_initiate_video_call": document.getElementById("customer_initiate_video_call").checked,
        "customer_initiate_voice_call": document.getElementById("customer_initiate_voice_call").checked,
        "customer_initiate_video_call_as_pip": document.getElementById("customer_initiate_video_call_as_pip").checked,
        "enable_voip_calling": document.getElementById("enable_voip_calling").checked,
        "voip_calling_text": remove_special_characters_from_str(stripHTML(document.getElementById("voip_calling_text").value)),
        "voip_with_video_calling_text": remove_special_characters_from_str(stripHTML(document.getElementById("voip_with_video_calling_text").value)),
        "enable_auto_voip_with_video_calling_for_first_time": document.getElementById("enable_auto_voip_with_video_calling_for_first_time").checked,
        "enable_auto_voip_calling_for_first_time": document.getElementById("enable_auto_voip_calling_for_first_time").checked,
        "enable_voip_with_video_calling": document.getElementById("enable_voip_with_video_calling").checked,
        "allow_screen_recording": document.getElementById("allow_screen_recording").checked,
        "recording_expires_in_days": (document.getElementById("recording_expires_in_days") == undefined || document.getElementById("recording_expires_in_days") == null) ? 15 : document.getElementById("recording_expires_in_days").value,
    }

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/save-cobrowse-agent-settings/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                show_easyassist_toast("Saved successfully.");
                setTimeout(function() {
                    location.reload();
                }, 1000);
            } else {
                show_easyassist_toast("Unable to save the details");
            }
        }

        element.innerHTML = "Save";
    }
    
    xhttp.send(params);
}

function sales_cobrowse_admin_settings(element){

    let archive_on_common_inactivity_threshold = document.getElementById("archive_on_common_inactivity_threshold");
    if (archive_on_common_inactivity_threshold && (archive_on_common_inactivity_threshold.value <= 0 || archive_on_common_inactivity_threshold.value > 60)) {
        show_easyassist_toast("Session in-activity value should be between 1 and 60");
        return;
    }
    
    var drop_link_expiry_time = document.getElementById("drop_link_expiry_time");
    if (drop_link_expiry_time && (drop_link_expiry_time.value <= 0 || drop_link_expiry_time.value > 60)) {
        show_easyassist_toast("Generate Drop Link Expiry: Time between 1 and 60 min are allowed.");
        return;
    }

    var urls_consider_lead_converted = document.getElementById("urls_consider_lead_converted").value;
    if(urls_consider_lead_converted.length != 0) {
        let lead_converted_urls_list = urls_consider_lead_converted.split(",")
        for (let link in lead_converted_urls_list) {
            let is_valid = is_url_valid(lead_converted_urls_list[link].trim())
            if (is_valid == false) {
                show_easyassist_toast("The entered URL is not valid: " + lead_converted_urls_list[link]);
                return;
            }
        }
    }

    var restricted_urls = document.getElementById("restricted_urls").value;
    if(restricted_urls.length != 0) {
        let restricted_urls_list = restricted_urls.split(",")
        for (let link in restricted_urls_list) {
            let is_valid = is_url_valid(restricted_urls_list[link].trim())
            if (is_valid == false) {
                show_easyassist_toast("The entered URL is not valid: " + restricted_urls_list[link]);
                return;
            }
        }
    }

    let request_params = {
        "masking_type": document.getElementById("input-masking-type").value,
        "allow_screen_sharing_cobrowse": document.getElementById("allow_screen_sharing_cobrowse").checked,
        "enable_low_bandwidth_cobrowsing": document.getElementById("enable_low_bandwidth_cobrowsing").checked,
        "enable_manual_switching": document.getElementById("enable_manual_switching").checked,
        "low_bandwidth_cobrowsing_threshold": document.getElementById("low_bandwidth_cobrowsing_threshold").value,
        "archive_on_common_inactivity_threshold": document.getElementById("archive_on_common_inactivity_threshold").value,
        "drop_link_expiry_time": document.getElementById("drop_link_expiry_time").value,
        "urls_consider_lead_converted": document.getElementById("urls_consider_lead_converted").value,
        "restricted_urls": document.getElementById("restricted_urls").value,
    }

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/save-cobrowse-admin-settings/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                show_easyassist_toast("Saved successfully.");
                setTimeout(function() {
                    location.reload();
                }, 1000);
            } else if( response.status == 302) {
                show_easyassist_toast(response.message);
            } else {
                show_easyassist_toast("Unable to save the details");
            }
        }

        element.innerHTML = "Save";
    }
    
    xhttp.send(params);
}

function save_cobrowse_customer_settings(element){
    
    if(document.getElementById("masked_field_warning_text").value.trim() == "") {
        show_easyassist_toast("Mask warning message cannot be empty.")
        return
    }

    if(document.getElementById("assistant_message").value.trim() == ""){
        show_easyassist_toast("Message to be shown on customer consent modal cannot be empty.")
        return;
    }
    
    let request_params = {
        "enable_masked_field_warning": document.getElementById("enable_masked_field_warning").checked,
        "masked_field_warning_text": remove_special_characters_from_str(stripHTML(document.getElementById("masked_field_warning_text").value)),
        "show_verification_code_modal": document.getElementById("show_verification_code_modal").checked,
        "enable_verification_code_popup": document.getElementById("enable_verification_code_popup").checked,
        "assistant_message": stripHTML(document.getElementById("assistant_message").value),
    }

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/save-cobrowsing-meta-details/cobrowsing/customer/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                show_easyassist_toast("Saved successfully.");
                setTimeout(function() {
                    location.reload();
                }, 1000);
            } else {
                show_easyassist_toast("Unable to save the details");
            }
        }

        element.innerHTML = "Save";
    }
    
    xhttp.send(params);    
}

function save_cobrowse_general_settings(element){

    var predefined_remarks_list_with_buttons = document.getElementById("predefined_remarks_with_buttons").value;
    if (document.getElementById("enable_predefined_remarks_with_buttons").checked && (!predefined_remarks_list_with_buttons || predefined_remarks_list_with_buttons.length == 0)) {
        show_easyassist_toast("Enter the required fields in predefined remarks to save the changes");
        return;
    }
    
    if(document.getElementById("enable_predefined_remarks").checked && predefined_remarks_array.length == 0){
        show_easyassist_toast("Enter the required fields in predefined remarks to save the changes");
        return;
    }
    
    if(document.getElementById("lead_conversion_checkbox_text") && document.getElementById("lead_conversion_checkbox_text").value.trim() == "") {
        show_easyassist_toast("Lead conversion message cannot be empty.")
        return
    }

    if(document.getElementById("assistant_message") && document.getElementById("assistant_message").value.trim() == ""){
        show_easyassist_toast("Message to be shown on customer consent modal cannot be empty.")
        return;
    }

    let enable_smart_agent_assignment = document.getElementById("enable_smart_agent_assignment").checked;
    let reconnecting_window_timer_element = document.getElementById("reconnecting_window_timer_input_field");
    
    if(enable_smart_agent_assignment && reconnecting_window_timer_element) {
        let reconnecting_window_timer_value = reconnecting_window_timer_element.value.trim();
        if(!reconnecting_window_timer_value.length || !parseInt(reconnecting_window_timer_value)) {
            show_easyassist_toast("Reconnecting window timer cannot be empty or 0")
            return;
        }
    }

    let request_params = {
        "lead_conversion_checkbox_text": remove_special_characters_from_str(stripHTML(document.getElementById("lead_conversion_checkbox_text").value)),
        "enable_predefined_remarks": document.getElementById("enable_predefined_remarks").checked,
        "enable_predefined_subremarks": document.getElementById("enable_predefined_subremarks").checked,
        "enable_predefined_remarks_with_buttons": document.getElementById("enable_predefined_remarks_with_buttons").checked,
        "predefined_remarks_list": predefined_remarks_array,
        "predefined_remarks_with_buttons": document.getElementById("predefined_remarks_with_buttons").value,
        "predefined_remarks_optional":  document.getElementById("input-predefined-remark-optional-checkbox").checked,
        "enable_agent_connect_message": document.getElementById("enable_agent_connect_message").checked,
        "agent_connect_message": remove_special_characters_from_str(stripHTML(document.getElementById("agent_connect_message").value)),
        "enable_smart_agent_assignment": enable_smart_agent_assignment,
        "reconnecting_window_timer_input": reconnecting_window_timer_element.value.trim(),
    }

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/save-cobrowse-general-settings/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                show_easyassist_toast("Saved successfully.");
                setTimeout(function() {
                    location.reload();
                }, 1000);
            } else if( response.status == 302) {
                show_easyassist_toast(response.message);
            } else {
                show_easyassist_toast("Unable to save the details");
            }
        }

        element.innerHTML = "Save";
    }
    
    xhttp.send(params);    
}

function save_video_agent_settings(element){
    
    let request_params = {
        "allow_capture_screenshots": document.getElementById("allow_capture_screenshots").checked,
        "enable_invite_agent_in_meeting": document.getElementById("enable_invite_agent_in_meeting").checked,
        "show_cobrowsing_meeting_lobby": document.getElementById("show_cobrowsing_meeting_lobby").checked,
        "enable_screen_sharing": document.getElementById("allow_screen_sharing").checked,
    }

    let cognomeet_request_params = {
        "cognomeet_access_token": window.COGNOMEET_ACCESS_TOKEN,
        "enable_screen_capture": document.getElementById("allow_capture_screenshots").checked,
        "enable_invite_agent": document.getElementById("enable_invite_agent_in_meeting").checked,
        "show_lobby_page": document.getElementById("show_cobrowsing_meeting_lobby").checked,
        "enable_screen_sharing": document.getElementById("allow_screen_sharing").checked,
    };

    save_config_in_cognomeet(cognomeet_request_params);

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/save-video-agent-settings/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                show_easyassist_toast("Saved successfully.");
                setTimeout(function() {
                    location.reload();
                }, 1000);
            } else {
                show_easyassist_toast("Unable to save the details");
            }
        }

        element.innerHTML = "Save";
    }
    
    xhttp.send(params);    
}

function save_video_admin_settings(element){
    
    var meeting_url = document.getElementById("meeting_url").value;
    if (!is_url_valid(meeting_url)) {
        show_easyassist_toast("The entered meeting URL is not valid.");
        return;
    }

    var no_agent_connects_meeting_toast_threshold = document.getElementById("no_agent_connects_meeting_toast_threshold");
    if (no_agent_connects_meeting_toast_threshold && no_agent_connects_meeting_toast_threshold.value <= 0) {
        show_easyassist_toast("No Agent permit meeting toast time should be greater than 0.");
        return;
    }

    var no_agent_connects_meeting_toast_text_ele = document.getElementById("no_agent_connects_meeting_toast_text");
    var no_agent_connects_meeting_toast_text = "";
    if(no_agent_connects_meeting_toast_text_ele) {
        no_agent_connects_meeting_toast_text = remove_special_characters_from_str(stripHTML(no_agent_connects_meeting_toast_text_ele.value))
        if(no_agent_connects_meeting_toast_text.length == 0 || no_agent_connects_meeting_toast_text.length >= 1024) {
            show_easyassist_toast("No agent permit meeting toast text length should be greater than 1 and less than 1024 characters.");
            return;
        }
    }

    let is_dyte_meet_enabled = false;
    let is_scheduled_meet_enabled = document.getElementById('enable_scheduled_meeting').checked;
    if(is_scheduled_meet_enabled){
        // Uncomment the below line so that functionality can be enabled/disabled at the backend
        // is_dyte_meet_enabled = document.getElementById('enable_dyte_video_calling').checked;
    }

    let max_time_duration_value = document.getElementById("meeting_end_time").value;
    if(document.getElementById("allow_meeting_end_time").checked && (max_time_duration_value <= 0 || max_time_duration_value > 1440)) {
        show_easyassist_toast("Maximum time duration for meetings should be between 1-1440 mins.");
        return;
    }

    let request_params = {
        "proxy_server": document.getElementById("proxy_pass_server").value,
        "meeting_url": document.getElementById("meeting_url").value,
        "meeting_default_password": stripHTML(document.getElementById("meeting_default_password").value),
        "meet_background_color": document.getElementById("meet_background_color").value,
        "allow_meeting_feedback": document.getElementById("allow_meeting_feedback").checked,
        "allow_meeting_end_time": document.getElementById("allow_meeting_end_time").checked,
        "meeting_end_time": max_time_duration_value,
        "allow_video_meeting_only": document.getElementById("allow_video_meeting_only").checked,
        "enable_no_agent_connects_toast_meeting": document.getElementById("no_agent_connects_toast_meeting").checked,
        "no_agent_connects_meeting_toast_threshold": document.getElementById("no_agent_connects_meeting_toast_threshold").value,
        "no_agent_connects_meeting_toast_text": no_agent_connects_meeting_toast_text,
        "allow_generate_meeting": is_scheduled_meet_enabled,
        "enable_cognomeet": is_dyte_meet_enabled,
        "enable_meeting_recording": document.getElementById('enable_meeting_recording').checked,
    };

    let cognomeet_request_params = {
        "cognomeet_access_token": window.COGNOMEET_ACCESS_TOKEN,
        "meeting_default_password": stripHTML(document.getElementById("meeting_default_password").value),
        "meeting_background_color": document.getElementById("meet_background_color").value,//
        "enable_feedback_in_meeting": document.getElementById("allow_meeting_feedback").checked,
        "enable_time_duration": document.getElementById("allow_meeting_end_time").checked,
        "max_time_duration": max_time_duration_value,//
        "no_agent_permit_meeting_toast": document.getElementById("no_agent_connects_toast_meeting").checked,
        "no_agent_permit_meeting_toast_time": document.getElementById("no_agent_connects_meeting_toast_threshold").value,//
        "no_agent_permit_meeting_toast_text": no_agent_connects_meeting_toast_text,
        "enable_auto_recording": document.getElementById('enable_meeting_recording').checked
    };

    save_config_in_cognomeet(cognomeet_request_params);

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/save-video-admin-settings/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                show_easyassist_toast("Saved successfully.");
                setTimeout(function() {
                    location.reload();
                }, 1000);
            } else {
                show_easyassist_toast("Unable to save the details");
            }
        }

        element.innerHTML = "Save";
    }

    xhttp.send(params);
}

function add_url_chip(event) {
    let keycode = (event.keyCode ? event.keyCode : event.which);
    let entered_url = $(this).val();
    let url_element_container = $(this).closest('.modal-input-field').next('.added-url-container');
    let url_added_heading = $(this).closest('.modal-input-field').next('.added-url-container').find('.added-url-heading')
    let error_message_div = $(this).next('.url-error-message')

    if (keycode == 13) {

        entered_url = stripHTML(entered_url)
        if (!is_url_valid(entered_url, true)) {
            error_message_div.css("display", "flex")
            error_message_div.css("color", "red")
            error_message_div.text("Please enter valid URL")
            return;
        }

        // check if url is already present or not
        let urls_element_list = $(this).closest('.modal-input-field').next('.added-url-container').find('.url-value')
        for (let i = 0; i < urls_element_list.length; i++) {
            if (urls_element_list[i].text == entered_url) {
                if (urls_element_list[i].parentElement.classList.contains("d-none")) {
                    urls_element_list[i].parentElement.classList.remove("d-none")
                    url_element_container.removeClass("d-none");
                    url_added_heading.removeClass("d-none");
                } else {
                    show_easyassist_toast('URL already exists.');
                }
                $(this).val('');
                return;
            }
        }

        error_message_div.css("display", "none");
        url_element_container.removeClass('d-none');
        url_added_heading.removeClass('d-none')

        $(this).val('');
        let appendingdiv = url_added_heading.next()
        appendingdiv.prepend(`
        <div class="input-url-chip">  
          <a class="url-value" target="_blank" href="${entered_url}"><u>${entered_url}</u></a>
          <div class="remove-url-chip">
                <svg width="18" height="19" viewBox="0 0 18 19" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3.23038 3.5L14.7702 15.5" stroke="#2D2D2D" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M14.7699 3.5L3.23007 15.5" stroke="#2D2D2D" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
          </div>
        </div>`);

    }

    $('.remove-url-chip').click(function () {
        let url_element_container = $(this).closest('.added-url-container');
        let url_added_heading = $(this).closest('.added-url-container').find('.added-url-heading')

        $(this).parent().addClass("d-none");
        let childrens = url_element_container.find('.input-url-chip')
        let display_none_counter = 0;

        for (let i = 0; i < childrens.length; i++) {
            if (childrens[i].className.includes("d-none")) {
                display_none_counter++;
            }
        }
        if (display_none_counter == childrens.length) {
            url_added_heading.addClass('d-none');
            url_element_container.addClass('d-none');
        }
    })
};

$('#inactivity_url_input').keypress(add_url_chip)
$('#exit_intent_url_input').keypress(add_url_chip)

function save_inactivity_popup_urls(element) {
    let modal_content = element.parentElement.parentElement
    let url_values = modal_content.querySelectorAll(".url-value")
    let error_message = modal_content.querySelector(".url-error-message")
    let urls_list = [];

    for (let i = 0; i < url_values.length; i++) {
        let url = stripHTML(url_values[i].text);

        if (url_values[i].parentElement.classList.contains("d-none")) {
            continue;
        }

        if (!is_url_valid(url, true)) {
            error_message.style.display = "flex";
            error_message.style.color = "red";
            error_message.innerHTML = "Please enter valid Email ID";
            return;
        }
        urls_list.push(url)
    }

    if (!urls_list.length) {
        show_easyassist_toast("Please add at least one URL.")
        return;
    }

    json_string = JSON.stringify({
        "urls_list": urls_list,
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/sales-ai/save-inactivity-pop-up-urls/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                if ($("#inactivity-popup-url-modal-button").text() == "Add URLs") {
                        $("#inactivity-popup-url-modal-button").text("Edit URLs");
                        document.getElementById("inactivity-popup-url-modal-button").setAttribute("onclick", "show_urls_in_urls_modal('inactivity-popup-url-Modal')")
                    }

                for (let i = 0; i < url_values.length; i++) {
                    if (url_values[i].parentElement.classList.contains("d-none")) {
                        url_values[i].parentElement.remove();
                    }
                }

                $("#inactivity-popup-url-Modal").modal("hide");
                show_easyassist_toast("URLs updated successfully");
            } else if (response["status"] == 401) {
                show_easyassist_toast("You are not authorized to perform this Operation")
            } else if (response["status"] == 300) {
                show_easyassist_toast("Please check the entered URLs")
            } else if (response["status"] == 301) {
                show_easyassist_toast("Please add at least one URL.")
            } else {
                show_easyassist_toast("Something went wrong.")
            }
        }
    }
    xhttp.send(params);
}

function save_exit_intent_popup_urls(element) {
    let modal_content = element.parentElement.parentElement
    let url_values = modal_content.querySelectorAll(".url-value")
    let error_message = modal_content.querySelector(".url-error-message")
    let urls_list = [];

    for (let i = 0; i < url_values.length; i++) {
        let url = stripHTML(url_values[i].text);
        if (url_values[i].parentElement.classList.contains("d-none")) {
            continue;
        }
        if (!is_url_valid(url, true)) {
            error_message.style.display = "flex";
            error_message.style.color = "red";
            error_message.innerHTML = "Please enter valid Email ID";
            return;
        }
        urls_list.push(url)
    }

    if (!urls_list.length) {
        show_easyassist_toast("Please add at least one URL.")
        return;
    }

    json_string = JSON.stringify({
        "urls_list": urls_list,
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/sales-ai/save-exit-intent-pop-up-urls/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                if ($("#exit-intent-url-modal-button").text() == "Add URLs") {
                    $("#exit-intent-url-modal-button").text("Edit URLs");
                    document.getElementById("exit-intent-url-modal-button").setAttribute("onclick", "show_urls_in_urls_modal('exit-intent-url-Modal')")
                }

                for (let i = 0; i < url_values.length; i++) {
                    if (url_values[i].parentElement.classList.contains("d-none")) {
                        url_values[i].parentElement.remove();
                    }
                }

                $("#exit-intent-url-Modal").modal("hide");
                show_easyassist_toast("URLs updated successfully");
            } else if (response["status"] == 401) {
                show_easyassist_toast("You are not authorized to perform this Operation");
            } else if (response["status"] == 300) {
                show_easyassist_toast("Please check the entered URLs");
            } else if (response["status"] == 301) {
                show_easyassist_toast("Please add at least one URL.")
            } else {
                show_easyassist_toast("Something went wrong.");
            }
        }
    }
    xhttp.send(params);
}

function show_urls_in_urls_modal(element_id) {
    let urls_modal = document.getElementById(element_id)
    let input_url_chips = urls_modal.querySelectorAll(".input-url-chip")
    if (input_url_chips.length) {
        let heading = urls_modal.querySelector(".added-url-heading")
        let container = urls_modal.querySelector(".added-url-container")

        heading.classList.remove("d-none");
        container.classList.remove("d-none");

        for (let i = 0; i < input_url_chips.length; i++) {
            input_url_chips[i].classList.remove("d-none");
        }
    }
}

// API to update configurations in CognoMeetApp
function save_config_in_cognomeet(cognomeet_request_params) {

    if(window.COGNOMEET_ACCESS_TOKEN == "" || window.COGNOMEET_ACCESS_TOKEN == undefined) {
        return;
    }

    let json_params = JSON.stringify(cognomeet_request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/cogno-meet/update-access-token-config/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                console.log("Config update successfully in CognoMeetApp");
            } else {
                console.log("Error in config update in CognoMeetApp");
            }
        }
    }
    
    xhttp.send(params);
}
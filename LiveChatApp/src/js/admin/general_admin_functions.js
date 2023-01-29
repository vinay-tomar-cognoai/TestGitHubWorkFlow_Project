import {
    custom_decrypt,
    EncryptVariable,
    getCsrfToken,
    showToast,
    validate_name,
    validate_phone_number,
    validate_email,
    is_valid_date,
    alphanumeric,
    encrypt_variable,
    stripHTML,
    get_url_vars,
    get_params,
} from "../utils";

import { 
    get_character_limit,
    upload_excel, 
} from '../common'
import axios from "axios";

(function ($) {
    $(function () {

        if (window.location.pathname.includes('manage-agents')) {
            apply_manage_users_delete_export_events();
            initialize_export_multiselect_dropdowns();
        }

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
        if (screen.width < 680) {
            $("#web-switch").hide();
            $("#mobile-switch").show();
        }
    }); // end of document ready
})(jQuery); // end of jQuery name space
//////////////////////////////// Manage agents continous ///////////////////////////////////

const state = {
    is_otp_verified: false,
    upload_file_limit_size: 1024000,
    token: "",
    max_customer_count_allowed: 100,
    format: {
                dateFormat: 'dd-mm-yy', 
                prevText: "Previous",
                maxDate: new Date()
            },
    checked_users: []
};

function manage_agents_continuous() {
    var csrf_token = getCsrfToken();

    var json_string = JSON.stringify({
        user_type: get_url_vars()['user_type'],
    });

    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var params = 'json_string=' + json_string;

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/livechat/manage-agents-continuous/", false);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token); 
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status"] == "200") {
                document.getElementById("total_agents").innerHTML = response["total_agents"];
                document.getElementById("logged_in_users").innerHTML = response["logged_in_users"];
                document.getElementById("not_ready_users").innerHTML = response["not_ready_users"];
                document.getElementById("ready_users").innerHTML = response["ready_users"];

                for (var user = 0; user < response["users"].length; user++) {
                    if (
                        document.getElementById(
                            "toggle-agent-switch-by-admin-supervisor-" +
                                response["users"][user]["pk"]
                        ) != null
                    ) {
                        document.getElementById(
                            "toggle-agent-switch-by-admin-supervisor-" +
                                response["users"][user]["pk"]
                        ).checked = response["users"][user]["is_online"];
                        document.getElementById(
                            "livechat-ongoing-chats-" + response["users"][user]["pk"]
                        ).innerHTML = response["users"][user]["ongoing_chats"];
                    }
                }
            }
        }
    };
    xhttp.send(params);
}

/////////////////////////// Manage agents ends ////////////////////////////////////////////

/////////////////////////// Save Admin Settings ///////////////////////////////////////////

function save_admin_system_settings() {

    var agent_unavialable_response = document.getElementById("agnet-ua-response").value.trim();
    var auto_bot_response = document.getElementById("auto_bot_response").value.trim();
    var queue_timer = document.getElementById("queue-time-id").value;
    var select_bot_obj = document.getElementById("select-bot-obj").value;
    var show_version_footer = document.getElementById("show-version-footer").checked;
    var theme_color_element = document.getElementById("livechat-theme-color");
    var r_value = parseInt(theme_color_element.jscolor.rgb[0]);
    var g_value = parseInt(theme_color_element.jscolor.rgb[1]);
    var b_value = parseInt(theme_color_element.jscolor.rgb[2]);
    var theme_color = r_value + "," + g_value + "," + b_value;
    var masking_enabled = document.getElementById("masking-enabled").checked;
    var is_supervisor_allowed_to_create_group = document.getElementById("is_supervisor_allowed_to_create_group").checked;
    var is_followup_lead_enabled = document.getElementById("enable_followup_lead").checked;
    let virtual_interpretation_enabled = document.getElementById('is_virtual_interpretation_enabled').checked;

    var followup_lead_sources = [];
    var followup_lead_sources_elements = document.querySelectorAll(".followup-lead-source");
    for(let i = 0; i < followup_lead_sources_elements.length; i++) {
        if(followup_lead_sources_elements[i].checked) {
            followup_lead_sources.push(followup_lead_sources_elements[i].value);
        }
    }

    if(is_followup_lead_enabled && followup_lead_sources.length == 0) {
        showToast('Please select atleast one source of leads', 3000);
        return;        
    }

    // auto chat disposal
    var auto_chat_disposal_enabled = document.getElementById('auto_chat_disposal_enabled').checked;
    var user_terminates_chat_enabled = document.getElementById('user_terminates_chat_enabled').checked;
    var user_terminates_chat_dispose_time = document.getElementById('user_terminates_chat_dispose_time').value;
    var session_inactivity_enabled = document.getElementById('session_inactivity_enabled').checked;
    var session_inactivity_chat_dispose_time = document.getElementById('session_inactivity_chat_dispose_time').value;

    if(!is_valid_integer(queue_timer)) {
        showToast('Please enter integer value in "Queue Time"', 3000);
        return;
    }

    if (queue_timer < 30) {
        showToast('Queue Time must be greater than or equal to 30', 3000);
        return;
    }

    if (queue_timer > 600) {
        showToast('Queue Time must be less than or equal to 600', 3000);
        return;
    }

    if (queue_timer % 5 !== 0) {
        showToast('Queue Time must be a multiple of 5', 3000);
        return;
    }

    if (auto_chat_disposal_enabled) {
        if (user_terminates_chat_enabled && !is_valid_dispose_time(user_terminates_chat_dispose_time)) {
            showToast('Please enter integer value between 1 and 59 in "Time after which chat should dispose"', 3000);
            return;
        }

        if (session_inactivity_enabled && !is_valid_dispose_time(session_inactivity_chat_dispose_time)) {
            showToast('Please enter integer value between 1 and 59 in "Time after which chat should dispose"', 3000);
            return;
        }
    }

    if (select_bot_obj == "-1") {
        showToast("Please select a bot first", 5000);
        return;
    }

    if(agent_unavialable_response == "") {
        showToast("Agent unavailable bot response cannot be empty.", 5000);
        return;
    }

    const char_limit = get_character_limit();
    if(agent_unavialable_response.length > char_limit.large) {
        showToast(`Agent not available bot response is too long.`, 2000)
        return;
    }

    if (!alphanumeric(agent_unavialable_response)) {
        showToast('Kindly enter alphanumeric text only in Agent not available bot response', 2000);
        return;
    }

    if(auto_bot_response.length > char_limit.large) {
        showToast(`Non working hour bot response is too long.`, 2000)
        return;
    }

    if (!alphanumeric(auto_bot_response)) {
        showToast('Kindly enter alphanumeric text only in non working hour bot response', 2000);
        return;
    }

    //WhatsApp Followup leads reinitiation
    let is_whatsapp_reinitiation_enabled = document.getElementById("livechat-whatsapp-followup-conversation-checkbox").checked;
    let whatsapp_reinitiating_text = document.getElementById("whatsapp-reinitiating-text").value;
    let whatsapp_reinitiating_keyword = document.getElementById("whatsapp-reinitiating-keyword").value;

    whatsapp_reinitiating_text = stripHTML(whatsapp_reinitiating_text);
    whatsapp_reinitiating_keyword = stripHTML(whatsapp_reinitiating_keyword);

    if(is_whatsapp_reinitiation_enabled && whatsapp_reinitiating_text.trim() == "") {
        showToast("Reinitiating text to be sent on whatsapp cannot be empty.", 2000);
        return;
    }

    if(is_whatsapp_reinitiation_enabled && whatsapp_reinitiating_text.length > char_limit.large) {
        showToast("Reinitiating text to be sent on whatsapp is too long.", 2000);
        return;
    }

    if(is_whatsapp_reinitiation_enabled && whatsapp_reinitiating_keyword.trim() == "") {
        showToast("Keywords to detect reinitiation cannot be empty.", 2000);
        return;
    }

    if(is_whatsapp_reinitiation_enabled && whatsapp_reinitiating_keyword.length > char_limit.medium) {
        showToast("Keywords to detect reinitiation is too long.", 2000);
        return;
    }

    var json_string = JSON.stringify({
        auto_bot_response: auto_bot_response,
        agent_unavialable_response: agent_unavialable_response,
        queue_timer: parseInt(queue_timer),
        select_bot_obj_pk: select_bot_obj,
        theme_color: theme_color,
        show_version_footer: show_version_footer,
        masking_enabled: masking_enabled,
        token: state.token,
        auto_chat_disposal_enabled: auto_chat_disposal_enabled,
        user_terminates_chat_enabled: user_terminates_chat_enabled,
        user_terminates_chat_dispose_time: parseInt(user_terminates_chat_dispose_time),
        session_inactivity_enabled: session_inactivity_enabled,
        session_inactivity_chat_dispose_time: parseInt(session_inactivity_chat_dispose_time),
        is_supervisor_allowed_to_create_group: is_supervisor_allowed_to_create_group,
        is_followup_lead_enabled: is_followup_lead_enabled,
        followup_lead_sources: followup_lead_sources,
        is_whatsapp_reinitiation_enabled: is_whatsapp_reinitiation_enabled,
        whatsapp_reinitiating_text: whatsapp_reinitiating_text,
        whatsapp_reinitiating_keyword: whatsapp_reinitiating_keyword,
        is_virtual_interpretation_enabled: virtual_interpretation_enabled,
    });
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/save-system-settings/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token); 
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);

            if (response.status_code == 200) {
                showToast("Changes Saved successfully!", 3000);
                setTimeout(function() {location.reload();}, 2000);
            } else {
                showToast(response.status_message, 3000);
            }

        }
    };
    xhttp.send(params);
}

async function save_admin_interaction_settings() {
    var max_customer_count = document.getElementById("customer-count-id").value;
    var category_enabled = document.getElementById("is-livechat-category-enabled").checked;
    var is_video_meeting_enabled = false;
    // uncomment below line once Video Meeting feature is enabled
    // var is_video_meeting_enabled = document.getElementById("is_video_meeting_enabled").checked;
    var select_bot_obj = document.getElementById("select-bot-obj").value;
    var max_guest_agent = document.getElementById("number-of-guest-agents").value;
    var guest_agent_timer = document.getElementById("pending-time-id").value;
    var is_self_assign_chat_agent_enabled = document.getElementById("enable-self-assign-chats-agent").checked;
    var is_agent_raise_ticket_functionality_enabled = document.getElementById("enable-agent-raise-ticket").checked;
    var is_customer_details_editing_enabled = document.getElementById("enable-customer-details-editing").checked;
    var is_chat_escalation_matrix_enabled = document.getElementById("is-chat-escalation-matrix-enabled").checked;
    var is_transcript_enabled = document.getElementById("enable-transcript").checked; 

    if(max_customer_count == "" || parseInt(max_customer_count) < 1 || parseInt(max_customer_count) > state.max_customer_count_allowed) {
        showToast('Please enter integer value between 1 to 100 in "Maximum number of customers with whom an agent can chat at a time"', 3000);
        return;
    }

    if(max_guest_agent != "1" && max_guest_agent != "2" && max_guest_agent != "3") {
        showToast('Maximum guest agents can be either 1, 2 or 3.', 3000);
        return;  
    }

    if(!is_valid_integer(guest_agent_timer)) {
        showToast('Please enter integer value in "Pending time for accept/reject guest agent field"', 3000);
        return;
    }

    if(guest_agent_timer > 600) {
        showToast('"Pending time for accept/reject guest agent field" must be less than or equal to 600', 3000);
        return;
    }

    if (select_bot_obj == "-1") {
        showToast("Please select a bot first", 5000);
        return;
    }

    // Voice/Video Call
    const call_type = document.getElementById('livechat_call_type').value;
    const is_call_from_customer_end_enabled = document.getElementById('enable_call_from_customer_end').checked;
    
    // Cobrowsing
    const is_cobrowsing_enabled = document.getElementById('livechat_enable_cobrowsing').checked;

    if (is_cobrowsing_enabled) {
        const is_eligible =  await enable_livechat_cobrowse_settings();

        if (!is_eligible) return;
    }

    var json_string = JSON.stringify({
        max_customer_count: parseInt(max_customer_count),
        category_enabled: category_enabled,
        select_bot_obj_pk: select_bot_obj,
        max_guest_agent: max_guest_agent,
        guest_agent_timer: parseInt(guest_agent_timer),
        call_type: call_type,
        is_call_from_customer_end_enabled: is_call_from_customer_end_enabled,
        is_self_assign_chat_agent_enabled: is_self_assign_chat_agent_enabled,
        is_agent_raise_ticket_functionality_enabled: is_agent_raise_ticket_functionality_enabled,
        is_customer_details_editing_enabled: is_customer_details_editing_enabled,
        is_cobrowsing_enabled: is_cobrowsing_enabled,
        is_chat_escalation_matrix_enabled: is_chat_escalation_matrix_enabled,
        is_transcript_enabled : is_transcript_enabled,
    });
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/save-interaction-settings/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token); 
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);

            if (response.status_code == 200) {
                showToast("Changes Saved successfully!", 3000);
                setTimeout(function() {location.reload();}, 2000);
            } else {
                showToast(response.status_message, 3000);
            }

        }
    };
    xhttp.send(params);
}

/////////////////////////////// Admin settings save end /////////////////////////////////////

//////////////////////////// Masking PII Data ///////////////////////////////////

function open_upload_agents_modal() {
    document.getElementById("create-agent-using-excel-modal").style.display = "block";
}

function close_upload_agents_modal() {
    document.getElementById("create-agent-using-excel-modal").style.display = "none";
}

function submit_agents_excel_onclick() {
    var agents_file = $("#real-file")[0].files[0];
    if (agents_file == undefined || agents_file == null) {
        showToast("Please provide excel sheet in required format.", 2000);
        return;
    }
    if (agents_file.name.split(".").pop() != "xlsx" && agents_file.name.split(".").pop() != "xls") {
        showToast("Please upload file in correct format.", 2000);
        return;
    }
    if (agents_file.size > state.upload_file_limit_size) {
        showToast("Size limit exceed(should be less than 1 MB)", 2000);
        return;
    }

    var reader = new FileReader();
    reader.readAsDataURL(agents_file);
    reader.onload = function() {

        var base64_str = reader.result.split(",")[1];

        var uploaded_file = [];
        uploaded_file.push({
            "filename": agents_file.name,
            "base64_file": base64_str,
        });

        upload_manage_agents_excel(uploaded_file);
    };

    reader.onerror = function(error) {
        console.log('Error: ', error);
    };
}

async function upload_manage_agents_excel(uploaded_file){
    var response = await upload_excel(uploaded_file);
    if (response && response.status == 200) {
        var upload_button = document.getElementById("submit_agents_excel");
        upload_button.innerHTML = "Creating..";
        upload_button.style.cursor = "not-allowed";

        var formData = new FormData();
        formData.append("src", response["src"]);
        $.ajax({
            url: "/livechat/submit-agents-excel/",
            type: "POST",
            headers: {
                "X-CSRFToken": getCsrfToken()
            },
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                response = custom_decrypt(response);
                response = JSON.parse(response);
                if (response["status_code"] == 200) {
                    showToast("Successfully created Users.", 2000);
                    window.location.reload();
                } 
                else if (response["status_code"] == 300) {
                    showToast("Duplicate entries found.", 2000);
                    window.location.reload();
                }
                else if (response["status_code"] == 101 || response["status_code"] == 403 || response["status_code"] == 500) {
                    upload_button.innerHTML = "Upload";
                    upload_button.style.cursor = "pointer";
                    showToast(response["status_message"], 2000);
                } else {
                    upload_button.innerHTML = "Upload";
                    upload_button.style.cursor = "pointer";
                    showToast("Internal Server Error", 2000);
                }
            },
            error: function (xhr, textstatus, errorthrown) {
                console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
            },
        });
    }
}

function download_create_agent_template_onclick() {
    $.ajax({
        url: "/livechat/download-create-agent-template/",
        type: "POST",
        headers: {
            "X-CSRFToken": getCsrfToken()
        },
        success: function (response) {
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if ((response["status"] = 200)) {
                if (response["export_path"] == null) {
                    alert("Sorry, unable to process your request. Kindly try again later.");
                } else {
                    if (response["export_path_exist"]) {
                        window.open(response["export_path"], "_blank");
                    } else {
                        alert("Requested data doesn't exists. Kindly try again later.");
                    }
                }
            }
        },
        error: function (xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        },
    });
}

async function send_otp_code() {
    const checked = document.getElementById("masking-enabled").checked;
    if (checked) {
        showToast("Click on Save Changes to mask the Customer data due to privacy concerns", 3000);
        return;
    }

    const bot_id = document.getElementById("select-bot-obj").value;

    $("#admin-otp-verification-modal").modal("show");
    empty_otp_fields();
    setTimeout(function () {
        document.getElementsByClassName("otp-form")[0].focus();
    }, 500);

    document.getElementById("livechat-resend-otp").style.pointerEvents = "none";
    document.getElementById("livechat-resend-otp").style.cursor = "default";

    await toggle_data_mask(bot_id);

    document.getElementById("livechat-resend-otp").style.pointerEvents = "auto";
    document.getElementById("livechat-resend-otp").style.cursor = "pointer";
}

function toggle_data_mask(bot_id) {
    return new Promise(function (resolve, reject) {
        let json_string = JSON.stringify({
            bot_id: bot_id,
        });

        json_string = EncryptVariable(json_string);
        json_string = encodeURIComponent(json_string);

        var csrf_token = getCsrfToken();
        const xhttp = new XMLHttpRequest();
        const params = "json_string=" + json_string;

        xhttp.open("POST", "/livechat/data-mask-toggle/", true);
        xhttp.setRequestHeader("X-CSRFToken", csrf_token);
        xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                var response = JSON.parse(this.responseText);
                response = custom_decrypt(response);
                response = JSON.parse(response);

                resolve();
            }
        };

        xhttp.send(params);
    });
}

function check_otp(elem) {
    const entered_otp_inputs = document.getElementsByClassName("otp-form");

    let entered_otp = "";
    for (let otp_input of entered_otp_inputs) {
        entered_otp += otp_input.value;
    }

    if (entered_otp == "" || entered_otp.length < 6) {
        showToast("Please enter otp before submitting.", 2000);
        return;
    }

    const bot_id = document.getElementById("select-bot-obj").value;

    elem.innerHTML = "Verifying..";

    match_otp_from_server(entered_otp, bot_id, elem);
}

function match_otp_from_server(entered_otp, bot_id, elem) {
    return new Promise(function (resolve, reject) {
        let json_string = JSON.stringify({
            entered_otp: entered_otp,
            bot_id: bot_id,
        });

        json_string = EncryptVariable(json_string);
        json_string = encodeURIComponent(json_string);

        var csrf_token = getCsrfToken();
        const xhttp = new XMLHttpRequest();
        const params = "json_string=" + json_string;

        xhttp.open("POST", "/livechat/check-data-toggle-otp/", true);
        xhttp.setRequestHeader("X-CSRFToken", csrf_token);
        xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                var response = JSON.parse(this.responseText);
                response = custom_decrypt(response);
                response = JSON.parse(response);

                if (response.status_code == 200) {
                    if (response.message == "Matched") {
                        state.token = response.token;
                        elem.innerHTML = "Verified";
                        state.is_otp_verified = true;

                        showToast(
                            "Click on Save Changes to save the customer data in original format without being masked",
                            3000
                        );

                        $("#admin-otp-verification-modal").modal("hide");
                    } else {
                        elem.innerHTML = "Submit";
                        showToast("Please enter correct OTP", 2000);
                    }
                    empty_otp_fields();
                } else {
                    showToast("Error in matching otp. Please try again later", 2000);
                    resolve(false);
                }
            }
        };

        xhttp.send(params);
    });
}

function empty_otp_fields() {
    let otp_elems = document.getElementsByClassName("otp-form");

    for (let otp_elem of otp_elems) {
        otp_elem.value = "";
    }
}

function on_admin_otp_verification_modal_hide() {
    if (!state.is_otp_verified) {
        const elem = document.getElementById("masking-enabled");
        elem.checked = !elem.checked;
    }
}

function on_otp_form_keypress(event) {
    let keys = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"];
    return keys.indexOf(event.key) > -1;
}

function on_otp_form_keyup(e) {
    let keys = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"];
    if (keys.indexOf(e.target.value) != -1) {
        $(e.target).next().focus();
    }
}

//////////////////////////// Masking PII Data Ends ///////////////////////////////////

/////////////////////////// ADMIN power Agent /////////////////////////////////////////

function livechat_agent_category_onchange(e) {
    let val = e.target.value.split("-");
    if (val.length > 1) {
        let id = val[0];
        val = val[1];
        let categories_added = document.getElementsByClassName("modal-chip");
        let is_present = false;
        for (let i = 0; i < categories_added.length; ++i) {
            if (categories_added[i].id == id) {
                is_present = true;
                  showToast("Category already exists.", 1000);
                break;
            }
        }

        if (!is_present) {
            let html =
                '<div class="modal-chip" id="' +
                id +
                '">\
           <p style="padding-left:20px;">' +
                val +
                '</p>\
          <img src="/static/LiveChatApp/img/modal-chip-icon.svg" \
          onclick = "remove_selected_category(this)">\
          </div>';

            $("#category-chips").append(html);
        }
    }

    $('#livechat-agent-category').val('hidden');

}

function livechat_agent_category_edit_onchange(e) {
    let val = e.target.value.split("-");
    if (val.length > 1) {
        let id = val[0];
        val = val[1];
        let categories_added = document.getElementsByClassName("modal-chip");

        let is_present = false;
        for (let i = 0; i < categories_added.length; ++i) {
            if (categories_added[i].firstChild.textContent.trim() == val) {
                is_present = true;
                break;
            }
        }

        if (!is_present) {
            let html =
                '<div class="modal-chip" id="' +
                id +
                '"><p style="padding-left:20px;">' +
                val +
                '</p>\
          <img src="/static/LiveChatApp/img/modal-chip-icon.svg" \
          onclick = "remove_selected_category(this)">\
          </div>';

            $("#category-chips-edit").append(html);
        }
    }

}

function add_category_chips_edit_modal(elem, user_id, e, val) {
    if (!val) {
        val = e.target.value.split("-");
    }

    if (val.length > 1) {
        let id = val[0];
        val = val[1];
        let categories_added = document.getElementById("category-chips-edit-" + user_id);
        
        let is_present = false;
        for (let i = 0; i < categories_added.childNodes.length; ++i) {
            if (categories_added.childNodes[i].id == user_id+"-"+id) {
                is_present = true;
                showToast("Category already exists.", 1000);
                break;
            }
        }

        if (!is_present) {
            let html =
                '<div class="modal-chip-edit modal-chip-edit-' +
                user_id +
                '" id="' +
                user_id +
                "-" +
                id +
                '">\
          <p style="padding-left:20px;">' +
                val +
                '</p>\
          <img src="/static/LiveChatApp/img/modal-chip-icon.svg" \
          onclick = "remove_selected_category(this)">\
          </div>';

            $("#category-chips-edit-" + user_id).append(html);
        }
    }

    try{
        if($('#modal-edit-agent-info-'+user_id).is(':visible'))
            $('#livechat-agent-category-'+user_id).val('hidden');
    }
    catch(err)
    {   console.log(err)
        $('#livechat-agent-category-'+user_id).val('hidden');
    }
    
}

function edit_agent_info(pk, type, current_user_status=-1) {
    try {
        let name = document.getElementById("edit-agent-name-" + pk).value;
        if (name == "" || validate_name("edit-agent-name-" + pk) == false) {
            showToast("Please enter valid name.", 2000);
            return;
        }
        let phone_number = document.getElementById("agent-phone-" + pk).value;
        if (
            phone_number == "" ||
            validate_phone_number("agent-phone-" + pk) == false ||
            phone_number.length != 10
        ) {
            showToast("Please enter valid phone number.", 2000);
            return;
        }
        // let email = document.getElementById("agent-email-" + pk).value;
        // if (email == "" || validate_email("agent-email-" + pk) == false) {
        //     showToast("Please enter valid email.", 2000);
        //     return;
        // }

        // let bot_pk = $("#livechat-user-bot-" + pk)
        //     .val()
        //     .split("-")[0];

        // let bot_pk_list = [];
        // if (bot_pk != "") bot_pk_list.push(bot_pk);

        // if (bot_pk_list.length == 0) {
        //     showToast("Please select at least one bot.", 2000);
        //     return;
        // }
        let category_pk_list = [];
        if (document.getElementById("agent-categories-" + pk).style.display == "none") {
            category_pk_list = ["-1"];
        } else {
            let category_chips = document.getElementsByClassName("modal-chip-edit-" + pk);
            if (category_chips.length == 0) {
                showToast("Please select at least one category.", 2000);
                return;
            } else {
                category_pk_list = [];
                for (let i = 0; i < category_chips.length; ++i) {
                    category_pk_list.push(category_chips[i].id.split("-")[1]);
                }
            }
        }


        let max_customers_allowed = 1;
        if (type == 3) {
            var element = document.getElementById("edit-agent-max-customers-allowed-" + pk)
            if (element)
                max_customers_allowed = element.value
            else
                max_customers_allowed = 1

        }

         if (max_customers_allowed < 1)
        {
            showToast("Please enter a valid customer allowed limit.", 2000);
            return;
        }
        if(parseInt(max_customers_allowed) && parseInt(max_customers_allowed) > state.max_customer_count_allowed){
            showToast("Maximum customers allowed should be less than 100.", 2000);
            return;
        }

        let supervisor_pk = -1;
        if (type == 3) {
            supervisor_pk = document.getElementById('select-agents-supervisor-'+pk).value;
        }
        if (current_user_status == 2){
            supervisor_pk = document.getElementById('select-agents-supervisor-'+pk).getAttribute('data-agents-supervisor-pk');
        }

        let json_string = JSON.stringify({
            current_pk: pk,
            name: name,
            phone_number: phone_number,
            // email: email,
            category_pk_list: category_pk_list,
            // bot_pk_list: bot_pk_list,
            max_customers_allowed: max_customers_allowed,
            supervisor_pk: supervisor_pk,
        });
        json_string = EncryptVariable(json_string);

        var CSRF_TOKEN = getCsrfToken();
        $.ajax({
            url: "/livechat/edit-agent-info/",
            type: "POST",
            headers: {
                "X-CSRFToken": CSRF_TOKEN
            },
            data: {
                json_string: json_string,
            },
            success: function(response) {
                response = custom_decrypt(response);
                response = JSON.parse(response);
                if (response["status_code"] == 200) {
                    showToast("Changes saved Succesfully", 2000);
                    window.location.reload();
                } else if (response["status_code"] == 300) {
                    showToast("username already exists.", 2000);
                } else if  (response.status_code == 400) {
                    showToast(response.status_message, 2000);
                } else {
                    showToast(
                        "Unable to save changes due to some internal server error. Kindly report the same",
                        2000
                    );
                }
            },
            error: function(xhr, textstatus, errorthrown) {
                console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
            },
        });
    } catch (e) {
        console.log(e)
    }
}

function cancel_agent_modal()
{ 
    $('#modal-create-agent').remove();
    var myClone = window.OriginalModal.clone();
    $('body').append(myClone);
    $("#livechat-agent-category").on("change", function (e) {
    livechat_agent_category_onchange(e);
});
} ;

function create_agent() {
    
    let name = document.getElementById("new-agent-name").value;
    if (name == "" || validate_name("new-agent-name") == false) {
        showToast("Please enter valid name.", 2000);
        return;
    }

    let phone_number = document.getElementById("new-agent-phone").value;
    if (
        phone_number == "" ||
        validate_phone_number("new-agent-phone") == false ||
        phone_number.length != 10
    ) {
        showToast("Please enter valid phone number.", 2000);
        return;
    }
    let email = document.getElementById("new-agent-email").value;
    if (email == "" || validate_email("new-agent-email") == false) {
        showToast("Please enter valid email.", 2000);
        return;
    }

    let status = document.getElementById("status-agent");

    if (status == undefined || status == "null" || status == null) {
        status = "3";
    } else {
        status = $("#status-agent").val();
    }

    let bot_pk = $("#livechat-user-bot-select").val().split("-")[0];

    let bot_pk_list = [];
    if (bot_pk != "") bot_pk_list.push(bot_pk);

    if (bot_pk_list.length == 0) {
        showToast("Please select at least one bot.", 2000);
        return;
    }
    let category_pk_list = [];
    if (document.getElementById("agent-categories").style.display == "none") {
        category_pk_list = ["-1"];
    } else {
        let category_chips = document.getElementsByClassName("modal-chip");

        if (category_chips.length == 0) {
            showToast("Please select atleast one category.", 2000);
            return;
        }
        category_pk_list = [];
        for (let i = 0; i < category_chips.length; ++i) {
            category_pk_list.push(category_chips[i].id);
        }
    }


    var supervisor_pk = "-1";
    ``;
    if (status == "3" && LIVECHAT_USER_STATUS == "1") {
        supervisor_pk = $("#selected-supervisor").val();
    }

    let max_customers_allowed = document.getElementById("new-agent-max-customers-allowed").value;
    if (max_customers_allowed == "" && status==3) {
        showToast("Please enter maximum customers allowed.", 2000);
        return;
    }
    else if(status != 3)
    {
        max_customers_allowed = 1
    }

    if(max_customers_allowed<1)
    { 
        showToast("Please enter a valid value for maximum customers allowed.", 2000);
        return;
    }
    if(parseInt(max_customers_allowed) && parseInt(max_customers_allowed) >= state.max_customer_count_allowed){
        showToast("Maximum customers allowed should be less than 100.", 2000);
        return;
    }
    
    let json_string = JSON.stringify({
        name: name,
        phone_number: phone_number,
        email: email,
        status: status,
        category_pk_list: category_pk_list,
        bot_pk_list: bot_pk_list,
        supervisor_pk: supervisor_pk,
        max_customers_allowed: max_customers_allowed
    });
    json_string = EncryptVariable(json_string);

    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
        url: "/livechat/create-new-agent/",
        type: "POST",
        headers: {
            "X-CSRFToken": CSRF_TOKEN
        },
        data: {
            json_string: json_string,
        },
        success: function (response) {
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status_code"] == 200) {
                if (status == "2") {
                    showToast("New Supervisor created Succesfully", 2000);
                } else {
                    showToast("New Agent created Succesfully", 2000);
                }
                showToast("User ID and Password are sent on the registered email", 2000);
                window.location.reload();
            } else if (response["status_code"] == 300) {
                showToast("username already exists.", 2000);
            } else if(response["status_code"] == 301 || response["status_code"] == 400 || response["status_code"] == 403){
                showToast(response["status_message"],2000)
            }else {
                showToast(
                    "Unable to create new agent due to some internal server error. Kindly report the same",
                    2000
                );
                console.log("Please report this. ", response["status_message"]);
            }
        },
        error: function (xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        },
    });
}

function open_delete_agent_modal(agent_id) {
    let elem = document.getElementById("delete-agent-btn");
    elem.dataset.agent_id = agent_id;
    elem.dataset.delete_user_type = "single";
}

function close_delete_agent_modal() {
    document.getElementById("modal-delete-agent").style.display = "none";
}

function delete_agent() {

    let delete_btn = document.getElementById("delete-agent-btn");
    let delete_user_type = delete_btn.dataset.delete_user_type;
    let selected_users = [];

    if(delete_user_type == "single") {
        selected_users = [delete_btn.dataset.agent_id]
    } else if(delete_user_type == "multiple") {
        selected_users = state.checked_users;
    } else {
        return;
    }
    
    if(!selected_users.length) {
        showToast("Please select any user", 2000);
        return;
    }

    let json_string = JSON.stringify({
        selected_users: selected_users,
    });
    json_string = EncryptVariable(json_string);
    $.ajax({
        url: "/livechat/delete-agent/",
        type: "POST",
        headers: {
            "X-CSRFToken": getCsrfToken()
        },
        data: {
            json_string: json_string,
        },
        success: function (response) {
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status_code"] == 200) {
                showToast("Deleted Succesfully", 2000);
                setTimeout(window.location.reload(), 2000);
                
            } else {
                showToast(
                    "Unable to delete the user, user may not be exist anymore.",
                    2000
                );
                setTimeout(window.location.reload(), 2000);
                
                console.log("Please report this. ", response["status_message"]);
            }
        },
        error: function (xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        },
    });
}

function update_bot_list(param) {
    if (param == "Add") {
        var s_id = document.getElementById("selected-supervisor").value;
        var bot_options = document.getElementById("livechat-user-bot-select");
    } else {
        var s_id = document.getElementById("selected-supervisor-" + param).value;
        var bot_options = document.getElementById("livechat-user-bot-" + param);
    }

    var json_string = JSON.stringify({
        selected_pk: s_id,
    });
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/get-bots-under-user/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status_code"] == "200") {
                let bot_objs = response["bot_objs"];

                let html = "";
                for (var i = 0; i < bot_objs.length; i++) {
                    html += `<option value=${bot_objs[i]["bot_pk"]}-${bot_objs[i]["bot_name"]}>${bot_objs[i]["bot_name"]}</option>`;
                }
                bot_options.innerHTML = html;
            }
        }
    };
    xhttp.send(params);
}

function add_entry_to_audit_trail_admin(
    status,
    selected_status,
    status_changed_by_admin_supervisor,
    pk
) {
    let json_string = JSON.stringify({
        pk: pk,
        status: status,
        selected_status: selected_status,
        status_changed_by_admin_supervisor: status_changed_by_admin_supervisor,
    });
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/switch-agent-status/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token); 
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status_code"] == "200") {
                showToast("Status updated successfully.", 4000);
            } else if (response["status_code"] == "300") {
                showToast(response["message"], 2000);
                setTimeout(function () {
                    window.location.reload();
                }, 2000);
            } else {
                showToast("Can't switch due to some internal error.", 4000);
            }
        }
    };
    xhttp.send(params);
}

function toggle_agent_switch_by_admin_supervisor(pk, user_status) {
    var status = document.getElementById("toggle-agent-switch-by-admin-supervisor-" + pk).checked;
    user_status = user_status == "2" ? "9" : "10";

    if (status) {
        add_entry_to_audit_trail_admin(status, "6", "0", pk);
    } else {
        add_entry_to_audit_trail_admin(status, user_status, "1", pk);
    }
}

function supervisor_to_agent_switch() {
    var status = document.getElementById("supervisor-to-agent-switch").checked;

    let json_string = JSON.stringify({
        status: status,
    });
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/switch-agent-manager/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status_code"] == "200") {
                showToast(response["message"], 5000);
                setTimeout(function () {
                    window.location.href = window.location.origin + "/livechat/";
                }, 1000);
            } else {
                showToast("Can't switch due to some internal error.", 5000);
            }
        }
    };
    xhttp.send(params);
}

function apply_livechat_theme(r_value, g_value, b_value) {
    var lighten_one = "rgb(" + r_value + "," + g_value + "," + b_value + ",1)";
    var lighten_two = "rgb(" + r_value + "," + g_value + "," + b_value + ", 0.4)";
    var lighten_three = "rgb(" + r_value + "," + g_value + "," + b_value + ",0.1)";

    try {
        collection_items = document.getElementsByClassName("collection-item active");

        for (var index = 0; index < collection_items.length; index++) {
            collection_items[index].style.setProperty("background-color", lighten_two, "important");
        }
    } catch (err) {}
}

function show_livechat_theme() {
    var theme_color_element = document.getElementById("livechat-theme-color");
    var r_value = parseInt(theme_color_element.jscolor.rgb[0]);
    var g_value = parseInt(theme_color_element.jscolor.rgb[1]);
    var b_value = parseInt(theme_color_element.jscolor.rgb[2]);
    apply_livechat_theme(r_value, g_value, b_value);
}

/* Auto Chat Disposal Starts */

function auto_chat_disposal_toggle_handler(el) {
    if (el.checked) {
        document.getElementById('auto_chat_dispose_subsections').style.display = 'table-row';
        user_terminates_chat_toggle_handler();
        session_inactivity_toggle_handler();
    } else {
        document.getElementById('auto_chat_dispose_subsections').style.display = 'none';
    }
}

function user_terminates_chat_toggle_handler(el) {
    if (!el) {
        el = document.getElementById('user_terminates_chat_enabled');
    }

    if (el.checked) {
        document.getElementById('user_terminates_chat_dispose_time_row').style.display = 'flex';
        document.getElementById('user_terminates_chat_dispose_time_divider').style.display = 'flex';

    } else {
        document.getElementById('user_terminates_chat_dispose_time_row').style.display = 'none';
        document.getElementById('user_terminates_chat_dispose_time_divider').style.display = 'none';
    }
}

function session_inactivity_toggle_handler(el) {
    if (!el) {
        el = document.getElementById('session_inactivity_enabled');
    }

    if (el.checked) {
        document.getElementById('session_inactivity_chat_dispose_time_row').style.display = 'flex';
        document.getElementById('session_inactivity_chat_dispose_time_divider').style.display = 'flex';

    } else {
        document.getElementById('session_inactivity_chat_dispose_time_row').style.display = 'none';
        document.getElementById('session_inactivity_chat_dispose_time_divider').style.display = 'none';
    }
}

function is_valid_dispose_time(time) {
    return (is_valid_integer(time) && !(time < 1) && !(time > 59));
}

function is_valid_integer(time) {
    return !isNaN(time) && Number.isInteger(parseFloat(time));
}

/* Auto Chat Disposal Ends */

export function toggle_initiate_call_from_customer(el) {
    const target_el = $("#enable_initiate_call_from_customer");

    if (el.value === "none")
        target_el.hide();
    else {

        target_el.show();

        if (el.value === "pip") {
            $("#enable_initiate_call_from_customer .livechat-setting-heading-text-div span").html(
                `Enable the option to initiate Voice Call as PIP at customer's end`
            );
        } else if (el.value === "new_tab"){
            $("#enable_initiate_call_from_customer .livechat-setting-heading-text-div span").html(
                `Enable the option to initiate Voice Call in new tab at customer's end`
            );
        } else {
            $("#enable_initiate_call_from_customer .livechat-setting-heading-text-div span").html(
                `Allow end customer to initiate video call`
            );
        }
    }
}

function check_select_chat_history_report_type(element) {

        if(element.value == "0") {

            document.getElementById("select-date-range").value = "0";
            document.getElementById("custom-range-filter-date").style.display="none";
            document.getElementById("custom-range-filter-email").style.display="none";
        } else if(element.value == "1") {

            if(document.getElementById("select-date-range").value == "4") {

                document.getElementById("info-text").style.display = "none";
                if(window.IS_REPORT_GENERATION_VIA_KAFKA_ENABLED) {
                document.getElementById("report-warning-div").style.display="block";
                document.getElementById("report-warning-text").innerHTML = window.REPORT_WARNING_TEXT
                }
                $('#export-filter-default-start-date').datepicker(state.format).val(start_date.trim());
                $('#export-filter-default-end-date').datepicker(state.format).val(end_date.trim());
            }
            if(document.getElementById("select-date-range").value == "5") {
                document.getElementById("custom-range-filter-email").style.display = "none";
            }
        } else if(element.value == "2") {

            if(document.getElementById("select-date-range").value == "4") {

                document.getElementById("info-text").style.display = "block";
                document.getElementById("report-warning-div").style.display="none";
                $('#export-filter-default-start-date').datepicker(state.format).val(custom_start_date.trim());
                $('#export-filter-default-end-date').datepicker(state.format).val(end_date.trim());
            }
            if(document.getElementById("select-date-range").value == "5") {
                document.getElementById("custom-range-filter-email").style.display = "block";
            }
        } 
}

function check_livechat_audit_custom_date_range(element) {

    if(document.getElementById("select-chat-history-report-type").value == "2") {

        let date_str = element.value;
        date_str = date_str.split("-");
        let date_value = new Date(parseInt(date_str[2]), parseInt(date_str[1]) - 1, parseInt(date_str[0]));
        date_value.setDate(date_value.getDate() + 30)

        $("#export-filter-default-end-date" ).datepicker( "option", "maxDate", date_value );

    }
}

function check_livechat_audit_date_range(element){

    if(element.value=="4") {

        document.getElementById("custom-range-filter-date").style.display="inline-flex";
        document.getElementById("custom-range-filter-email").style.display="block";
        document.getElementById("info-text").style.display = "none";
        $('#export-filter-default-start-date').datepicker(state.format).val(start_date.trim());
        $('#export-filter-default-end-date').datepicker(state.format).val(end_date.trim());

        if(document.getElementById("select-chat-history-report-type").value == "2") {
                document.getElementById("info-text").style.display = "block";
                document.getElementById("report-warning-div").style.display="none";
                        $('#export-filter-default-start-date').datepicker(state.format).val(custom_start_date.trim());
                        $('#export-filter-default-end-date').datepicker(state.format).val(end_date.trim());
        }
        if(document.getElementById("select-chat-history-report-type").value == "1" && window.IS_REPORT_GENERATION_VIA_KAFKA_ENABLED) {
            document.getElementById("report-warning-div").style.display="block";
            document.getElementById("report-warning-text").innerHTML = window.REPORT_WARNING_TEXT
        }

    } else if(element.value=="5") {

        document.getElementById("custom-range-filter-date").style.display="none";
        document.getElementById("custom-range-filter-email").style.display="none";
        if(document.getElementById("select-chat-history-report-type").value == "2" || !window.IS_REPORT_GENERATION_VIA_KAFKA_ENABLED) {
            document.getElementById("custom-range-filter-email").style.display="block";
        }
        document.getElementById("info-text").style.display = "none";
    } else {

        document.getElementById("custom-range-filter-date").style.display="none";
        document.getElementById("custom-range-filter-email").style.display="none";
        document.getElementById("info-text").style.display = "none";
    }
}

export function toggle_followup_lead_sources(element) {
    if(element.checked) {
        $('#lead-source-row').css('display','table-row');
    } else {
        $('#lead-source-row').css('display','none');
    }
}

function enable_livechat_cobrowse_settings() {
    return new Promise((resolve, reject) => {

        const json_string = JSON.stringify({
            id: USER_PK,
        });
    
        let encrypted_data = encrypt_variable(json_string);
        encrypted_data = {
            "Request": encrypted_data
        };
        // const params = JSON.stringify(encrypted_data);
        const config = {
            headers: {
              'X-CSRFToken': getCsrfToken(),
            }
        }
    
        axios
            .post(`${window.location.protocol}//${window.location.host}/easy-assist/enable-livechat-cobrowse-settings/`, encrypted_data, config)
            .then((response) => {
                response = response.data;
                response = custom_decrypt(response.Response)
                response = JSON.parse(response);

                console.log(response);
                if (response.status == 200) {
                    resolve(true);
                } else {
                    resolve(false);
                    showToast('Your admin profile does not have access to Cobrowsing. Please get its access and configure first, to enable for LiveChat.', 2000);
                }
            })
    })
}

export function load_system_setting(){
    if(document.getElementById("select-bot-obj").value != "-1"){
        window.location.href = "/livechat/system-settings/?bot_id="+document.getElementById("select-bot-obj").value;
    } else {
        window.location.href = "/livechat/system-settings/";
    }        
}

export function load_interaction_setting(){
    if(document.getElementById("select-bot-obj").value != "-1"){
        window.location.href = "/livechat/interaction-settings/?bot_id="+document.getElementById("select-bot-obj").value;
    } else {
        window.location.href = "/livechat/interaction-settings/";
    }        
}

export function handle_whatsapp_followup_paramaters_visibility(el) {
    if(el.checked){
        showToast("Please make sure that the reinitiating text is whitelisted by whatsapp vendor", 3000);
        $("#livechat-whatsapp-followup-parameters").show();
    } else {
        $("#livechat-whatsapp-followup-parameters").hide();
    }
}

export function get_livechat_user_category(e, agent_pk) {
    const supervisor_pk = e.target.value;

    const config = {
        headers: {
          'X-CSRFToken': getCsrfToken(),
        }
    }

    const json_string = JSON.stringify({
        user_pk: supervisor_pk,
        agent_pk: agent_pk,
    })

    const params = get_params(json_string);

    axios
        .post('/livechat/get-supervisor-category/', params, config)
        .then (response => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);

            console.log(response);
            if (response.status == 200) {
                let categories_chip_parent = document.getElementById('category-chips-edit-'+agent_pk);
                categories_chip_parent.innerHTML = '';   
                
                const category_list = response.category_list;
                category_list.forEach(category => {
                    add_category_chips_edit_modal(null, agent_pk, null, [category.pk, category.title]);
                })
            }
        })
}

function apply_manage_users_delete_export_events() {

    $('.livechat-user-checkbox').on("click", function (e) {
        let checked_users = document.querySelectorAll('.livechat-user-checkbox:checked');

        state.checked_users = [];
        for(let i = 0; i < checked_users.length; i++) {
            state.checked_users.push(checked_users[i].dataset.agent_id);
        }

        enable_disable_user_delete_btn();

        if(checked_users.length == window.TOTAL_USERS) {
            $("#livechat-user-global-checkbox").prop('checked', true);
        } else {
            $("#livechat-user-global-checkbox").prop('checked', false);
        }

    });

    $("#livechat-user-global-checkbox").on("click", function (e) {

        if(e.target.checked) {

            $(".livechat-user-checkbox").prop('checked', true);
            let checked_users = document.querySelectorAll('.livechat-user-checkbox:checked');

            state.checked_users = [];
            for(let i = 0; i < checked_users.length; i++) {
                state.checked_users.push(checked_users[i].dataset.agent_id);
            }

        } else {

            $(".livechat-user-checkbox").prop('checked', false);
            state.checked_users = [];
        }
        enable_disable_user_delete_btn();

    });

    $("#livechat-users-export-btn").on("click", function (e) {

        livechat_export_users();

    });

}

function enable_disable_user_delete_btn() {

    if(state.checked_users.length) {
        $("#livechat-user-delete-btn").removeClass('disable-btn');
    } else {
        $("#livechat-user-delete-btn").addClass('disable-btn');
    }
}

function initialize_export_multiselect_dropdowns() {
    
    $("#select-agent-manage-user-export").multiselect({
        nonSelectedText: 'Select agent',
        enableFiltering: true,
        includeSelectAllOption: true,
        selectAll: true,
        enableCaseInsensitiveFiltering: true
    });

    $("#select-supervisor-manage-user-export").multiselect({
        nonSelectedText: 'Select supervisor',
        enableFiltering: true,
        includeSelectAllOption: true,
        selectAll: true,
        enableCaseInsensitiveFiltering: true
    });

    $(".show-users-dropdown-checkbox").click(function(event) {
        let dropdown_id = event.target.dataset.dropdown_id;

        if ($(this).is(':checked')) {
            $(this).parent().next(".export-download-multiselect").show();

            $(`#${dropdown_id}`).multiselect('selectAll', false);
            $(`#${dropdown_id}`).multiselect('updateButtonText');

        } else {
            $(this).parent().next(".export-download-multiselect").hide();

            $(`#${dropdown_id}`).multiselect('clearSelection');

        }
    });

    $(".livechat-multiselect-dropdown.livechat-multiselect-filter-dropdown .multiselect-container>li>a>label").addClass("custom-checkbox-input");
    $(".livechat-multiselect-dropdown.livechat-multiselect-filter-dropdown .multiselect-container>li").find(".custom-checkbox-input").append("<span class='checkmark'></span>");

    if (window.LIVECHAT_USER_STATUS == "2") {
        $('#select-agent-manage-user-export').multiselect('selectAll', false);
        $('#select-agent-manage-user-export').multiselect('updateButtonText');
    }
}

function livechat_export_users() {

    let agents_list = $("#select-agent-manage-user-export").val();
    let supervisors_list = $("#select-supervisor-manage-user-export").val();

    let users_list = agents_list.concat(supervisors_list);
    
    if(!users_list.length) {
        showToast("Please select any user", 2000);
        return;
    }

    const json_string = JSON.stringify({
        users_list: users_list,
    });
    const params = get_params(json_string);

    let config = {
          headers: {
            'X-CSRFToken': getCsrfToken(),
          }
        }

    axios
        .post("/livechat/export-livechat-users/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);

            if(response.status_code == "200") {
                if (response.export_status == "export_request_completed") {
                    window.open(response["export_path"], "_blank");
                } else if (response.export_status == "export_request_saved") {
                    showToast(
                        "We have saved your request and will send data over email ID within 5 mins.",
                        3000
                    );
                    reset_export_users_modal();

                } else if (response.export_status == "export_request_failed") {
                    alert("Sorry, unable to process your request. Kindly try again later.");
                }
            }
        })     
        .catch((err) => {
            console.log(err);
        });

}

function reset_export_users_modal() {

    $('#select-agent-manage-user-export').multiselect('clearSelection');
    $('#select-supervisor-manage-user-export').multiselect('clearSelection');
    $('.show-users-dropdown-checkbox').trigger('click');
    $('#admin-manage-user-export-modal').modal('hide');

}

export {
    manage_agents_continuous,
    save_admin_system_settings,
    save_admin_interaction_settings,
    open_upload_agents_modal,
    close_upload_agents_modal,
    submit_agents_excel_onclick,
    download_create_agent_template_onclick,
    send_otp_code,
    toggle_data_mask,
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
    check_select_chat_history_report_type,
    check_livechat_audit_custom_date_range,
    check_livechat_audit_date_range
};

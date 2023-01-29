var COGNOAI_META_DATA = {};
var COGNOAI_SERVER_URL = window.localStorage.getItem('cognoai_server_url');
var COGNOAI_ACTIVE_LEAD_LIST = [];
var COGNOAI_SEARCH_LEAD_LIST = [];
var cognoai_search_for_captured_lead_interval = null;
var archive_session_id = null;

const regEmail = /^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/;

cognoai_verify_login_on_load()

function cognoai_add_local_storage_value(name, value) {
    window.localStorage.setItem(name, value);
}

function cognoai_get_local_storage_value(name) {
    return window.localStorage.getItem(name);
}

function cognoai_hide_extension_sidenav() {
    document.getElementsByClassName("cognoai-extension-sidenav")[0].style.display = "none";
}

function cognoai_generate_support_link_modal() {
    document.getElementById("cognoai-generate-support-link-modal").style.display = "block";
    if (document.getElementById("cognoai-generate-drop-link-data").value == "") {
        document.getElementById("cognoai-generate-link-button").innerHTML = "Generate Link";
        document.getElementById("cognoai-generate-drop-link-data-div").style.display = "none";
    }
}

function cognoia_search_lead_modal() {
    document.getElementById("cognoai-search-lead-modal").style.display = "block";
}

function cognoai_modal_close(ele) {
    document.getElementById(ele.parentElement.parentElement.id).style.display = "none";
}


function cognoai_add_sidenav_extension() {
    var html =
        '<div class="cognoai-extension-sidenav">\
                <div class="cognoai-extension-header">\
                    <center>\
                        <img height="40%" width="40%" src="' + COGNOAI_SERVER_URL + '/' + COGNOAI_META_DATA['source_easyassist_cobrowse_logo'] + '">\
                    </center>\
                <div id="cognoai-extenstion-minimize-icon">\
                    <a onclick="cognoai_hide_extension_sidenav()"><svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="#0085FF">\
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />\
                    </svg></a>\
                </div>\
            </div>\
            <div class="cognoai-extension-cards-header">\
                <label class="cognoai-switch">\
                    <input type="checkbox" onchange="cognoai_update_agent_cobrowsing_details()" id="cognoai-toggle-button">\
                    <div class="cognoai-slider cognoai-round">\
                        <span class="cognoai-online">Online</span>\
                        <span class="cognoai-offline">Offline</span>\
                    </div>\
                </label>\
                <button class="cognoai-extension-button" onclick="cognoai_generate_support_link_modal()">Generate support link</button>\
                <button class="cognoai-extension-button" onclick="cognoia_search_lead_modal()">Search Lead</button>\
            </div>\
            <div class="cognoai-extension-leads">\
                <center style="margin-bottom: 10px;"><span class="cognoai-span">Customers Requiring Support</span></center>\
                <div id="cognoai-active-leads-container">\
                </div>\
        </div>\
        </div>\
        <div id="cognoai-generate-support-link-modal" class="cognoai-modal">\
            <div class="cognoai-modal-content">\
                <span class="cognoai-modal-close" onclick="cognoai_modal_close(this)">&times;</span>\
                <h3>Generate a Drop Link for Cobrowsing</h3>\
                <hr>\
                <div class="cognoai-form">\
                        <span>Webiste Link</span><br>\
                        <input type="text" id="cognoai-website-url-data" class="cognoai-input"><br><br>\
                        <span>Customer Name</span><br>\
                        <input type="text" id="cognoai-customer-name-data" class="cognoai-input"><br><br>\
                        <span>Customer Mobile Number</span><br>\
                        <input type="number" id="cognoai-customer-mobile-data" class="cognoai-input"><br><br>\
                        <span>Customer Email (optional)</span><br>\
                        <input type="email" id="cognoai-customer-email-data" class="cognoai-input"><br><br>\
                        <span style="color:#858796">On clicking "Generate Link", a unique drop link will be generated which can be shared with the Customer for Cobrowsing. Drop link will be sent to the Customer via Email, if provided.</span><br>\
                        <div id="cognoai-generate-drop-link-data-div" style="display:none;">\
                            <input type="text" id="cognoai-generate-drop-link-data" class="cognoai-input">\
                        </div>\
                        <p style="color:green;" id="generate-drop-link-error"></p>\
                        <button class="cognoai-extension-button" id="cognoai-generate-link-button" onclick="cognoai_generate_support_link()">Generate Link</button>\
                </div>\
            </div>\
        </div>\
        <div id="cognoai-search-lead-modal" class="cognoai-modal">\
            <div class="cognoai-modal-content">\
                <span class="cognoai-modal-close" onclick="cognoai_modal_close(this);cognoai_capture_lead_modal_close();">&times;</span>\
                <h3>Ready to search for captured lead?</h3>\
                <hr>\
                <div class="cognoai-form">\
                    <input type="text" id="cognoai-search-lead-value" class="cognoai-input" placeholder="Search"><br><br>\
                    <div id="cognoai-search-leads-container">\
                    </div>\
                    <p id="cognoai-search-lead-error"></p>\
                    <button class="cognoai-extension-button" onclick="cognoai_capture_lead_search();">Search</button>\
                </div>\
            </div>\
        </div>\
        <div id="cognoai-archive-session-modal" class="cognoai-modal">\
            <div class="cognoai-modal-content">\
                <span class="cognoai-modal-close" onclick="cognoai_modal_close(this);">&times;</span>\
                <h3>Archive Session</h3>\
                <hr>\
                <div class="cognoai-form">\
                    <span>Please enter the remarks</span><br>\
                    <input type="text" id="cognoai-agent-remarks" class="cognoai-input"><br><br>\
                    <p style="color:red;" id="cognoai-archive-session-info"></p>\
                    <button class="cognoai-extension-button" onclick="cognoai_archive_cobrowsing_session()">Archive</button>\
                </div>\
            </div>\
        </div>';

    document.getElementsByTagName("body")[0].innerHTML += html
    document.getElementById("cognoai-extension-icon").style.display = 'block';
    document.getElementsByClassName("cognoai-extension-sidenav")[0].style.display = "block";

    cognoai_init();
}

function cognoai_init() {
    document.getElementsByClassName("cognoai-extension-cards-header")[0].style.display = "none";
    setInterval(cognoai_update_agent_cobrowsing_details, 5000);
    cognoai_update_agent_cobrowsing_details();
}

function cognoai_on_click_extension_icon() {
    document.getElementById("cognoai-extension-icon").addEventListener("click", function(e) {
        document.getElementsByClassName("cognoai-extension-sidenav")[0].style.display = "block";
    })
}


function cognoai_verify_login_on_load() {

    let cognoai_access_token = window.localStorage.getItem('cognoai_access_token');
    let cognoai_allowed_hosts = window.location.hostname;
    COGNOAI_SERVER_URL = window.localStorage.getItem('cognoai_server_url');
    let cognoai_agent_verification_token = window.localStorage.getItem('cognoai_agent_verification_token')

    let json_string = JSON.stringify({
        "cognoai_access_token": cognoai_access_token,
        "cognoai_allowed_hosts": cognoai_allowed_hosts,
        "cognoai_agent_verification_token": cognoai_agent_verification_token
    });

    let encrypted_data = cognoai_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", COGNOAI_SERVER_URL + "/easy-assist/verify-extension-token/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = cognoai_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                COGNOAI_META_DATA = response.COGNOAI_META_DATA;

                var cognoai_extension_icon = document.createElement('img');
                cognoai_extension_icon.src = COGNOAI_SERVER_URL + '/' + COGNOAI_META_DATA['source_easyassist_cobrowse_logo'];
                cognoai_extension_icon.id = "cognoai-extension-icon";
                cognoai_extension_icon.style.zIndex = "2147483647";
                cognoai_extension_icon.style.width = "100px";
                cognoai_extension_icon.style.position = "fixed";
                cognoai_extension_icon.style.right = "20px";
                cognoai_extension_icon.style.bottom = "3em";
                cognoai_extension_icon.style.display = "none";
                document.body.appendChild(cognoai_extension_icon);


                cognoai_add_sidenav_extension()

                cognoai_on_click_extension_icon()
            } else {
                window.localStorage.removeItem('cognoai_agent_verification_token')
                window.location.reload();
                return;
            }
        }
    }
    xhttp.send(params);
}

function change_agent_active_status(is_active) {
    if (is_active == true || is_active == false) {
        document.getElementById("cognoai-toggle-button").checked = is_active;
    }
}

function cognoai_create_active_lead_card(lead_data) {

    /************************************************** Customer Name ********/

    var cognoai_lead_card_html = '<div class="cognoai-active-lead-data" id="cognoai-lead-' + lead_data.session_id + '">';

    if (lead_data.is_lead == false) {
        cognoai_lead_card_html += [
            '<p class="cognoai-p">Customer Details</p>',
            '<p class="cognoai-p-data">',
            'Name: ' + lead_data.full_name,
            '<br>Mobile Number: ' + lead_data.mobile_number,
            '</p>'
        ].join('');
    } else {
        cognoai_lead_card_html += [
            '<p class="cognoai-p">Customer Details</p>',
            '<p class="cognoai-p-data">',
            lead_data.get_sync_data,
            '</p>'
        ].join('');
    }


    /************************************************** Product name and url ********/
    cognoai_lead_card_html += [
        '<p class="cognoai-p">Product</p>',
        '<p class="cognoai-p-data">',
        '<a href="',
        lead_data.product_url,
        '" target="_blank">',
        lead_data.product_name,
        '</a>',
        '</p>'
    ].join('');


    /************************************************** Status of lead ********/

    if (lead_data.is_active == false) {
        cognoai_lead_card_html += '<p class="cognoai-p-data cognoai-text-danger"> Inactive </p>';
    } else {

        // Reverse Cobrowsing Status
        if (lead_data.allow_agent_to_customer_cobrowsing == true) {
            if (lead_data.cobrowsing_start_datetime == null) {
                cognoai_lead_card_html += '<p class="cognoai-p-data cognoai-text-warning"> Waiting for Customer </p>';
            } else if (lead_data.is_active == true) {
                cognoai_lead_card_html += '<p class="cognoai-p-data cognoai-text-success"> Connected </p>';
            } else {
                cognoai_lead_card_html += '<p class="cognoai-p-data cognoai-text-danger"> Inactive </p>';
            }
        } else if (lead_data.allow_video_meeting_only) {
            // Allow Video Meeting Only
            if (lead_data.meeting_start_datetime == null) {
                if (lead_data.allow_agent_meeting == null) {
                    if (lead_data.agent_assistant_request_status) {
                        cognoai_lead_card_html += '<p class="cognoai-p-data cognoai-text-warning"> Meeting Request Sent </p>';
                    } else {
                        cognoai_lead_card_html += '<p class="cognoai-p-data cognoai-text-warning"> Request in queue </p>';
                    }
                } else if (lead_data.allow_agent_meeting == "false") {
                    cognoai_lead_card_html += '<p class="cognoai-p-data cognoai-text-danger"> Request denied by customer </p>';
                } else {
                    cognoai_lead_card_html += '<p class="cognoai-p-data cognoai-text-danger"> Waiting for Agent </p>';
                }
            } else if (lead_data.is_active) {
                cognoai_lead_card_html += '<p class="cognoai-p-data cognoai-text-success"> Connected with an Agent </p>';
            } else {
                cognoai_lead_card_html += '<p class="cognoai-p-data cognoai-text-danger"> Inactive </p>';
            }
        } else {
            // Cobrowsing
            if (lead_data.cobrowsing_start_datetime == null) {
                if (lead_data.allow_agent_cobrowse == null) {
                    if (lead_data.agent_assistant_request_status) {
                        cognoai_lead_card_html += '<p class="cognoai-p-data cognoai-text-warning"> Cobrowsing Request Sent </p>';
                    } else {
                        cognoai_lead_card_html += '<p class="cognoai-p-data cognoai-text-warning"> Request in queue </p>';
                    }
                } else if (lead_data.allow_agent_cobrowse == "false") {
                    cognoai_lead_card_html += '<p class="cognoai-p-data cognoai-text-danger"> Request denied by customer </p>';
                } else {
                    cognoai_lead_card_html += '<p class="cognoai-p-data cognoai-text-warning"> Waiting for Agent </p>';
                }
            } else if (lead_data.is_active) {
                cognoai_lead_card_html += '<p class="cognoai-p-data cognoai-text-success"> Connected with an Agent </p>';
            } else {
                cognoai_lead_card_html += '<p class="cognoai-p-data cognoai-text-danger"> Inactive </p>';
            }
        }
    }

    /************************************************** OTP ********/

    if (lead_data.enable_verification_code_popup) {
        cognoai_lead_card_html += [
            '<p class="cognoai-p">OTP</p>',
            '<p class="cognoai-p-data">',
            lead_data.otp,
            '</p>'
        ].join('');
    }

    /************************************************** Total time spent ********/

    cognoai_lead_card_html += [
        '<p class="cognoai-p">Time Duration</p>',
        '<p class="cognoai-p-data">',
        lead_data.total_time_spent,
        '</p>'
    ].join('');

    /************************************************** Request message & Request button ********/

    var lead_request_button_text = "";
    var lead_request_info_text = "";
    var lead_request_button_click_fun = "";

    if (lead_data.is_active == true) {

        if (lead_data.allow_agent_cobrowse == "true") {
            lead_request_button_text = 'Connect';
            lead_request_info_text = 'Request for assistance has been accepted by the Customer.';
            lead_request_button_click_fun = 'cognoai_assign_lead_to_agent(\'' + lead_data.session_id + '\')';
        } else if (lead_data.allow_agent_cobrowse == "false") {
            // requested for assistance but client doesn't allowed
            lead_request_button_text = 'Request Co-browsing';
            lead_request_info_text = 'Request for assistance has been denied by the customer. Kindly make sure, you are connected with client on call.';
            lead_request_button_click_fun = 'cognoai_request_for_cobrowsing(\'' + lead_data.session_id + '\')';
        } else {
            if (lead_data.agent_assistant_request_status == true) {
                // requested for assistance but state has not been changed
                lead_request_button_text = 'Resend Request';
                lead_request_info_text = 'Request for assistance has been sent to the customer.';
                lead_request_button_click_fun = 'cognoai_request_for_cobrowsing(\'' + lead_data.session_id + '\')';
            } else {
                lead_request_button_text = 'Request Co-browsing';
                lead_request_button_click_fun = 'cognoai_request_for_cobrowsing(\'' + lead_data.session_id + '\')';
            }
        }

    } else {
        lead_request_button_text = 'Archive';
        lead_request_button_click_fun = 'cognoai_archive_session_modal_open(\'' + lead_data.session_id + '\')';
    }

    cognoai_lead_card_html += [
        '<p class="cognoai-p" style="color: green;">',
        lead_request_info_text,
        '</p>',
    ].join('');

    cognoai_lead_card_html += [
        '<p class="cognoai-p">Connect/Achive</p>',
        '<p class="cognoai-p-data">',
        '<button class="cognoai-extension-lead-button"',
        'onclick="' + lead_request_button_click_fun + '"',
        '>',
        lead_request_button_text,
        '</button>',
        '</p>',
    ].join('');

    cognoai_lead_card_html += '</div>';

    return cognoai_lead_card_html;

}

function cognoai_update_active_lead_cards(COGNOAI_NEW_LEAD_LIST) {
    var cognoai_all_lead_card_html = "";
    for (var index = 0; index < COGNOAI_NEW_LEAD_LIST.length; index++) {
        var lead_data = COGNOAI_NEW_LEAD_LIST[index];
        cognoai_all_lead_card_html += cognoai_create_active_lead_card(lead_data)
    }
    var cognoai_extension_leads_container = document.getElementById("cognoai-active-leads-container");
    cognoai_extension_leads_container.innerHTML = cognoai_all_lead_card_html;
    COGNOAI_ACTIVE_LEAD_LIST = COGNOAI_NEW_LEAD_LIST;

    document.getElementsByClassName("cognoai-extension-cards-header")[0].style.display = "block";
}

function cognoai_update_agent_cobrowsing_details() {

    cognoai_access_token = window.localStorage.getItem('cognoai_access_token');
    cognoai_allowed_hosts = window.location.hostname;
    COGNOAI_SERVER_URL = window.localStorage.getItem('cognoai_server_url');
    cognoai_agent_verification_token = window.localStorage.getItem('cognoai_agent_verification_token');

    var cognoai_initial_call = false;
    if (cognoai_update_agent_cobrowsing_details.caller) {
        if (cognoai_update_agent_cobrowsing_details.caller.name == "cognoai_init") {
            cognoai_initial_call = true;
        }
    }
    var is_active = null;

    if (cognoai_initial_call == false)
        is_active = document.getElementById("cognoai-toggle-button").checked;

    json_string = JSON.stringify({
        "cognoai_access_token": cognoai_access_token,
        "cognoai_allowed_hosts": cognoai_allowed_hosts,
        "cognoai_agent_verification_token": cognoai_agent_verification_token,
        "is_active": is_active,
    });
    encrypted_data = cognoai_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", COGNOAI_SERVER_URL + "/easy-assist/ext/update-agent-cobrowsing-details/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = cognoai_custom_decrypt(response.Response);
            response = JSON.parse(response);
            is_active = response.is_active;
            change_agent_active_status(response.is_active);
            cognoai_update_active_lead_cards(response.cobrowse_io_details);
        }
    }
    xhttp.send(params);
}

function cognoai_generate_support_link() {
    var cognoai_generate_link_button = document.getElementById("cognoai-generate-link-button");
    var client_page_link = document.getElementById("cognoai-website-url-data").value;
    var customer_name = document.getElementById("cognoai-customer-name-data").value.trim();
    var customer_mobile_number = document.getElementById("cognoai-customer-mobile-data").value.trim();
    var customer_email_id = document.getElementById("cognoai-customer-email-data").value.trim();

    var error_message_element = document.getElementById("generate-drop-link-error");

    client_page_link = client_page_link.trim();
    customer_name = customer_name.trim();
    const regex = /^[^\s]+$/;
    const regName = /^[^\s][a-zA-Z ]+$/;
    const regMob = /^[6-9]{1}[0-9]{9}$/;

    if (!regex.test(client_page_link)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a client page link (without whitespaces)";
        return;
    }

    if (!regName.test(customer_name)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter full name (only A-Z, a-z and space is allowed)";
        return;
    }

    if (!regMob.test(customer_mobile_number)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter valid 10-digit mobile number";
        return;
    }

    if (customer_email_id != null && customer_email_id != "" && !regEmail.test(customer_email_id)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter valid email id.";
        return;
    }

    json_string = JSON.stringify({
        "cognoai_access_token": cognoai_access_token,
        "cognoai_allowed_hosts": cognoai_allowed_hosts,
        "cognoai_agent_verification_token": cognoai_agent_verification_token,
        "client_page_link": client_page_link,
        "customer_name": customer_name,
        "customer_mobile_number": customer_mobile_number,
        "customer_email_id": customer_email_id,
    });
    encrypted_data = cognoai_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    cognoai_generate_link_button.innerHTML = "Generating...";

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", COGNOAI_SERVER_URL + "/easy-assist/ext/generate-drop-link/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = cognoai_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                if (response.generated_link == 'Error') {
                    error_message_element.style.color = "red";
                    error_message_element.innerHTML = "Please use a valid url";
                    cognoai_generate_link_button.innerHTML = "Generate Link";
                } else {
                    error_message_element.style.color = "green";
                    error_message_element.innerHTML = "Link has been generated successfully.";
                    document.getElementById("cognoai-generate-drop-link-data-div").style.display = "block";
                    document.getElementById("cognoai-generate-drop-link-data").value = response.generated_link;
                    cognoai_generate_link_button.innerHTML = "Generate Link";
                }
            } else {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = "Could not generate a drop link";
                cognoai_generate_link_button.innerHTML = "Generate Link";
            }
        }
    }
    xhttp.send(params);

}

/////////////////////////// update_captured_lead //////////////////////

function cognoai_create_search_lead_card(lead_data) {

    var last_update_datetime_html = "";
    var active_inactive = '<i class="fas fa-fw fa-check-square text-success"></i>';
    var opt_div_html = "";
    var lead_request_info_html = "";
    var lead_request_button_html = "";

    last_update_datetime_html = [
        '<p class="cognoai-p">Last Update DateTime</p>',
        '<p class="cognoai-p-data">',
        lead_data.last_update_datetime,
        '</p>',
    ].join('');

    if (lead_data.is_active == false) {
        active_inactive = '<i class="fas fa-fw fa-times-circle text-danger"></i>';
    }

    if (lead_data.enable_verification_code_popup) {
        opt_div_html = [
            '<p class="cognoai-p">OTP</p>',
            '<p class="cognoai-p-data">',
            lead_data.otp,
            '</p>'
        ].join('');
    }

    var lead_request_button_text = "";
    var lead_request_info_text = "";
    var lead_request_button_click_fun = "";

    if (lead_data.is_active == true) {
        if (lead_data.allow_agent_cobrowse == "true") {
            lead_request_button_text = 'Connect';
            lead_request_info_text = 'Request for assistance has been accepted by the Customer.';
            lead_request_button_click_fun = 'cognoai_assign_lead_to_agent(\'' + lead_data.session_id + '\')';
        } else if (lead_data.allow_agent_cobrowse == "false") {
            // requested for assistance but client doesn't allowed
            lead_request_button_text = 'Request Co-browsing';
            lead_request_info_text = 'Request for assistance has been denied by the customer. Kindly make sure, you are connected with client on call.';
            lead_request_button_click_fun = 'cognoai_request_for_cobrowsing(\'' + lead_data.session_id + '\')';
        } else {
            if (lead_data.agent_assistant_request_status == true) {
                // requested for assistance but state has not been changed
                lead_request_button_text = 'Resend Request';
                lead_request_info_text = 'Request for assistance has been sent to the customer.';
                lead_request_button_click_fun = 'cognoai_request_for_cobrowsing(\'' + lead_data.session_id + '\')';
            } else {
                lead_request_button_text = 'Request Co-browsing';
                lead_request_button_click_fun = 'cognoai_request_for_cobrowsing(\'' + lead_data.session_id + '\')';
            }
        }

    } else {
        lead_request_button_text = 'Archive';
        lead_request_button_click_fun = 'cognoai_archive_session_modal_open(\'' + lead_data.session_id + '\')';
    }

    lead_request_info_html = [
        '<p class="cognoai-p">',
        lead_request_info_text,
        '</p>',
    ].join('');

    lead_request_button_html = [
        '<p class="cognoai-p-data">',
        '<button class="cognoai-extension-lead-button"',
        'onclick="' + lead_request_button_click_fun + '"',
        '>',
        lead_request_button_text,
        '</button>',
        '</p>',
    ].join('');

    var cognoai_lead_card_html = ['<div class="cognoai-search-lead-data" id="cognoai-lead-0">',
        last_update_datetime_html,
        active_inactive,
        opt_div_html,
        lead_request_info_html,
        lead_request_button_html,
        '</div>'
    ].join('');
    return cognoai_lead_card_html;
}

function cognoai_update_search_lead_cards(COGNOAI_NEW_LEAD_LIST) {
    var cognoai_all_lead_card_html = "";
    for (var index = 0; index < COGNOAI_NEW_LEAD_LIST.length; index++) {
        var lead_data = COGNOAI_NEW_LEAD_LIST[index];
        cognoai_all_lead_card_html += cognoai_create_search_lead_card(lead_data)
    }
    var cognoai_extension_leads_container = document.getElementById("cognoai-search-leads-container");
    cognoai_extension_leads_container.innerHTML = cognoai_all_lead_card_html;
    COGNOAI_SEARCH_LEAD_LIST = COGNOAI_NEW_LEAD_LIST;
}

function cognoai_capture_lead_modal_close() {
    clearInterval(cognoai_search_for_captured_lead_interval);
    cognoai_search_for_captured_lead_interval = null;
}

function cognoai_capture_lead_search() {
    if (cognoai_search_for_captured_lead_interval == null) {
        cognoai_search_for_captured_lead();
        cognoai_search_for_captured_lead_interval = setInterval(cognoai_search_for_captured_lead, 5000);
    }
}

function cognoai_search_for_captured_lead() {
    var cognoai_search_leads_container = document.getElementById("cognoai-search-leads-container");
    cognoai_search_leads_container.innerHTML = "";

    var cognoai_search_lead_error = document.getElementById("cognoai-search-lead-error");
    cognoai_search_lead_error.innerHTML = "";

    var cognoai_search_lead_value = document.getElementById("cognoai-search-lead-value").value;
    if (cognoai_search_lead_value == "") {
        cognoai_search_lead_error.style.color = "red";
        cognoai_search_lead_error.innerHTML = "Please enter valid search value";
        return;
    }

    json_string = JSON.stringify({
        "cognoai_access_token": cognoai_access_token,
        "cognoai_allowed_hosts": cognoai_allowed_hosts,
        "cognoai_agent_verification_token": cognoai_agent_verification_token,
        "search_value": cognoai_search_lead_value,
    });
    encrypted_data = cognoai_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", COGNOAI_SERVER_URL + "/easy-assist/ext/search-lead/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = cognoai_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                let cobrowse_io_details = response.cobrowse_io_details;

                if (cobrowse_io_details.length == 0) {
                    var cognoai_extension_leads_container = document.getElementById("cognoai-search-leads-container");
                    cognoai_extension_leads_container.innerHTML = "No active customer with that details found. Please wait for some time, or ask the customer to refresh the page and then try again.";
                } else {
                    cognoai_update_search_lead_cards(response.cobrowse_io_details);
                }
            }
        }
    }
    xhttp.send(params);
}

function cognoai_assign_lead_to_agent(session_id) {

    json_string = JSON.stringify({
        "cognoai_access_token": cognoai_access_token,
        "cognoai_allowed_hosts": cognoai_allowed_hosts,
        "cognoai_agent_verification_token": cognoai_agent_verification_token,
        "session_id": session_id,
    });
    encrypted_data = cognoai_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", COGNOAI_SERVER_URL + "/easy-assist/ext/assign-lead/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = cognoai_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {

                window.open(COGNOAI_SERVER_URL + "/easy-assist/crm/cobrowsing/" + response["login_token"], target="_blank");
            }
        }
    }
    xhttp.send(params);
}

function cognoai_request_for_cobrowsing(session_id) {

    json_string = JSON.stringify({
        "cognoai_access_token": cognoai_access_token,
        "cognoai_allowed_hosts": cognoai_allowed_hosts,
        "cognoai_agent_verification_token": cognoai_agent_verification_token,
        "session_id": session_id,
    });
    encrypted_data = cognoai_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", COGNOAI_SERVER_URL + "/easy-assist/ext/request-assist/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = cognoai_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                cognoai_update_agent_cobrowsing_details();
            }
        }
    }
    xhttp.send(params);
}


function cognoai_archive_session_modal_open(session_id) {
    archive_session_id = session_id;
    document.getElementById("cognoai-archive-session-modal").style.display = "block";
}

function cognoai_archive_cobrowsing_session() {
    let comment_desc = ""
    let comments = document.getElementById("cognoai-agent-remarks").value;

    json_string = JSON.stringify({
        "cognoai_access_token": cognoai_access_token,
        "cognoai_allowed_hosts": cognoai_allowed_hosts,
        "cognoai_agent_verification_token": cognoai_agent_verification_token,
        "id": archive_session_id,
        "comments": comments,
        "comment_desc": comment_desc,
    });
    encrypted_data = cognoai_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", COGNOAI_SERVER_URL + "/easy-assist/ext/close-session/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = cognoai_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                cognoai_update_agent_cobrowsing_details();
                document.getElementById("cognoai-archive-session-modal").style.display = "none";
            } else {
                document.getElementById("cognoai-archive-session-info").innerHTML = "Unable to end Session. Please try again later";
            }
        }
    }
    xhttp.send(params);
}
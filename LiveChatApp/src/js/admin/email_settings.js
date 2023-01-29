import axios from "axios";

import {
    EncryptVariable,
    custom_decrypt,
    encrypt_variable,
    showToast,
    get_params,
    stripHTML,
    getCsrfToken,
    validate_email,
} from "../utils";

const state = {
    current_selected_profile: '',
    is_render_required: true,
};

(function ($) {
    $(function () {

        if(String(window.location.href).includes('email-settings')){
            apply_email_settings_event_listeners();
        }

        if(String(window.location.href).includes('email-settings') || String(window.location.href).includes('settings')){
            apply_email_configuration_event_listeners();
        }

    }); // end of document ready
})(jQuery); // end of jQuery name space

function enable_disable_email_notification(){
	var is_email_enabled = document.getElementById('livechat-email-setting-profile-cb').checked;
    var json_string = JSON.stringify({
        is_email_enabled: is_email_enabled
    });
    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;    
    xhttp.open("POST", "/livechat/enable-disable-email-notification/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
            	if(response["is_email_enabled"]){
                    showToast("Email Notification Enabled", 4000);
                    $("#livechat-email-analytics-configure-btn").css("display", "inline-flex");
                    window.IS_EMAIL_ENABLED = "True";
                }
                else{
                    showToast("Email Notification Disabled", 4000);
                    $("#livechat-email-analytics-configure-btn").css("display", "none");
                    window.IS_EMAIL_ENABLED = "False";
                }
            }
        }
    };
    xhttp.send(params);

}

function save_email_profile(){
    let pk = state.current_selected_profile;
    if(!pk) return;

    var profile_name = document.getElementById('profile-name-'+pk).value;
    if (profile_name == "") {
        showToast("Profile Name cannot be empty", 2000);
        return;
    }
    if (profile_name.trim() == "") {
        showToast("Profile Name cannot be empty", 2000);
        return;
    }
    if (profile_name.length > 25) {
        showToast("Profile Name max characters allowed - 25", 2000);
        return;
    }

    var format = /[`@#$%^*()_+\-=\[\]{};':"\\|,.<>\/~]/;
    if (format.test(profile_name.trim())) {
        showToast("Invalid Profile Name", 2000);
        return;
    }

    var email_freq = $("#select-email-frequency-dropdown-"+pk).val();

    var email_address = [];
    var email_address_list_container = document.getElementById("email-id-list-"+pk)["children"];
    for(let i = 0;i<email_address_list_container.length;i++){
        email_address.push((email_address_list_container[i]).attributes.value.value);
    }

    var email_subject = document.getElementById("email-subject-input-"+pk).value;
    if (email_subject.length > 100) {
        showToast("Email Subject max characters allowed - 100", 2000);
        return;
    }

    var agent_connection_rate = document.getElementById("email-agent-connection-"+pk).value;
    if(parseInt(agent_connection_rate) > 100 || parseInt(agent_connection_rate) < 0){
        showToast("Agent Connection rate should be between 1 - 100", 2000);
        return;   
    }

    var is_table_parameters_enabled = document.getElementById("livechat-email-table-parameter-cb-"+pk).checked;

    var count_variations = []
    for(let i = 1; i<=5; i++){
        if(document.getElementById('count-' + i + '-' + pk).checked){
            count_variations.push(document.getElementById('count-' + i + '-' + pk).value);
        }  
    }

    var channel_list = [];
    for(let i = 0; i < CHANNEL_NAME_LIST.length; i++){

        if(document.getElementById('table-channel-' + CHANNEL_NAME_LIST[i]["name"] + '-' + pk).checked){
            channel_list.push(document.getElementById('table-channel-' + CHANNEL_NAME_LIST[i]["name"] + '-' + pk).value);
        }
    }
    var table_records = [];
    for(let i = 1; i<=10; i++){
        if(document.getElementById('table-records-' + i + '-' + pk).checked){
            table_records.push(document.getElementById('table-records-' + i + '-' + pk).value);
        }  
    }

    var is_graph_enabled = document.getElementById("livechat-email-graphic-parameter-cb-"+pk).checked;
    var is_graph_chart_reports_enabled = document.getElementById("graph-chart-reports-"+pk).checked;
    var graph_chart_reports = [];
    for(let i = 1; i<=5; i++){
        if(document.getElementById('graph-chart-reports-' + i + '-' + pk).checked){
            graph_chart_reports.push(document.getElementById('graph-chart-reports-' + i + '-' + pk).value);
        }  
    }

    var is_interactions_enabled = document.getElementById("graph-interaction-"+pk).checked;
    var is_avg_handle_time_enabled = document.getElementById("graph-handle-time-"+pk).checked;
    var is_attachment_enabled = document.getElementById("livechat-email-attachment-parameter-cb-"+pk).checked;

    var attachment_parameters = [];
    for(let i = 1; i<=3; i++){
        if(document.getElementById('attachment-' + i + '-' + pk).checked){
            attachment_parameters.push(document.getElementById('attachment-' + i + '-' + pk).value);
        }
    }

    var json_string = JSON.stringify({
        profile_id: pk,
        profile_name : profile_name,
        email_freq : email_freq,
        email_addr_list : email_address,
        email_subject : email_subject,
        agent_connection_rate : agent_connection_rate,
        is_table_parameters_enabled : is_table_parameters_enabled,
        count_variations : count_variations,
        channel_list : channel_list,
        table_records_list : table_records,
        is_graph_parameters_enabled : is_graph_enabled,
        is_chat_reports_enabled : is_graph_chart_reports_enabled,
        graph_chat_reports_list : graph_chart_reports,
        is_interactions_enabled : is_interactions_enabled,
        is_avg_handle_time_enabled : is_avg_handle_time_enabled,
        is_attachment_parameters_enabled : is_attachment_enabled,
        attachment_parameters_list : attachment_parameters,
    });
    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;    
    xhttp.open("POST", "/livechat/save-email-profile/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                showToast(response["message"], 2000);
                setTimeout(() => {
                    location.reload();
                }, 2000);
            } else if (response["status"] == 400){
                showToast(response["message"], 2000);
            }
        }
    };
    xhttp.send(params);

}

function check_and_display_profile_data(){
    var email_profile_pks = JSON.parse(window.EMAIL_PROFILE_PKS);
    if(window.IS_EMAIL_ENABLED == "True"){
        document.getElementById("livechat-email-setting-profile-container").style.display = "block";
        if(parseInt(window.EMAIL_PROFILE_LENGTH) == 0){
            document.getElementById("profile-details-tab-new").style.display = "block";
            document.getElementById("profile-tab-new").style.display = "block";
            var email_id_input = document.getElementById("email-id-input-new");

            var email_tag_container = document.getElementById("email-id-list-new");
            new LivechatTagElement(email_id_input, email_tag_container, 'new');

            check_and_render_email_freq_new_profile();
            state.current_selected_profile = 'new';
        }
        else{
            for(let i=0;i<email_profile_pks.length;i++){
                document.getElementById("profile-details-tab-"+email_profile_pks[i]).style.display = "none";
            }
            document.getElementById("profile-details-tab-"+window.LATEST_EMAIL_PK).style.display = "block";
            $("#profile-heading-tab-"+window.LATEST_EMAIL_PK).addClass('active'); 
            state.current_selected_profile = window.LATEST_EMAIL_PK;
        }
    }
    else{
        if(parseInt(window.EMAIL_PROFILE_LENGTH) == 0){
            document.getElementById("profile-details-tab-new").style.display = "block";
            document.getElementById("profile-tab-new").style.display = "block";
            var email_id_input = document.getElementById("email-id-input-new");

            var email_tag_container = document.getElementById("email-id-list-new");
            new LivechatTagElement(email_id_input, email_tag_container, 'new');

            check_and_render_email_freq_new_profile();
            state.current_selected_profile = 'new';
        }
        document.getElementById("livechat-email-setting-profile-container").style.display = "none";
        $("#profile-heading-tab-new").addClass('active'); 
    }
}

function add_new_email_profile(){
    if(document.getElementById("profile-details-tab-new").style.display == "block"){
        showToast("Please save the last Email Profile", 4000);
        return;
    }
    var email_profile_pks = JSON.parse(window.EMAIL_PROFILE_PKS);

    for(let i=0;i<email_profile_pks.length;i++){
        document.getElementById("profile-details-tab-"+email_profile_pks[i]).style.display = "none";
        $("#profile-heading-tab-"+email_profile_pks[i]).removeClass('active'); 
    }
    document.getElementById("profile-details-tab-new").style.display = "block";
    document.getElementById("profile-tab-new").style.display = "block";
    $("#profile-heading-tab-new").addClass('active');
    var email_id_input = document.getElementById("email-id-input-new");

    var email_tag_container = document.getElementById("email-id-list-new");
    new LivechatTagElement(email_id_input, email_tag_container, 'new');

    check_and_render_email_freq_new_profile();
    state.current_selected_profile = 'new';

}

function enable_disable_table_container(pk){
    if(document.getElementById("livechat-email-table-parameter-cb-"+pk).checked){
        $("#livechat-table-parameter-container-"+pk).fadeIn(500);
    }
    else{
        $("#livechat-table-parameter-container-"+pk).fadeOut(500);
    }
}

function enable_disable_graph_container(pk){
    if(document.getElementById("livechat-email-graphic-parameter-cb-"+pk).checked){
        $("#livechat-graphic-parameter-container-"+pk).fadeIn(500);
    }
    else{
        $("#livechat-graphic-parameter-container-"+pk).fadeOut(500);
    }
}

function enable_disable_graph_chat_container(pk){
    if(document.getElementById("graph-chart-reports-"+pk).checked){
        $("#livechat-email-chat-report-chip-container-"+pk).fadeIn(500);
    }
    else{
        $("#livechat-email-chat-report-chip-container-"+pk).fadeOut(500);
    }
}

function enable_disable_attachment_container(pk){
    if(document.getElementById("livechat-email-attachment-parameter-cb-"+pk).checked){
        $("#livechat-attachment-parameter-container-"+pk).fadeIn(500);
    }
    else{
        $("#livechat-attachment-parameter-container-"+pk).fadeOut(500);
    }         
}

function check_and_render_email_address(){
    var email_profile_pks = JSON.parse(window.EMAIL_PROFILE_PKS);
    for(let i=0; i<email_profile_pks.length;i++){
        var email_id_input = document.getElementById("email-id-input-"+email_profile_pks[i]);

        var email_tag_container = document.getElementById("email-id-list-"+email_profile_pks[i]);
        new LivechatTagElement(email_id_input, email_tag_container, email_profile_pks[i]);
    }
}


function check_and_render_email_freq(){
    var email_profile_pks = JSON.parse(window.EMAIL_PROFILE_PKS);
    for(let i=0; i<email_profile_pks.length;i++){
          $("#select-email-frequency-dropdown-"+email_profile_pks[i]).multiselect({
            nonSelectedText: 'Select Frequency',
            enableFiltering: true,
            includeSelectAllOption: true
          });      
    }
    update_multiselect_checkboxes();
}

function check_and_render_email_freq_new_profile(){
  $("#select-email-frequency-dropdown-new").multiselect({
    nonSelectedText: 'Select Frequency',
    enableFiltering: true,
    includeSelectAllOption: true
  });
  
  update_multiselect_checkboxes();
}

export function update_multiselect_checkboxes() {
    $(".livechat-multiselect-dropdown.livechat-multiselect-filter-dropdown .multiselect-container>li>a>label").addClass("custom-checkbox-input");
    $(".livechat-multiselect-dropdown.livechat-multiselect-filter-dropdown .multiselect-container>li").find(".custom-checkbox-input").append("<span class='checkmark'></span>");
}

class LivechatTagElement {
    constructor(element, tag_container, pk) {
        this.element = element;
        this.tag_container = tag_container;
        this.pk = pk;
        var email_address = [];
        var email_address_list_container = document.getElementById("email-id-list-"+pk)["children"];
        for(let i = 0;i<email_address_list_container.length;i++){
            email_address.push((email_address_list_container[i]).attributes.value.value);
        }
        this.email_id_list = email_address;
        this.initialize();
    }

    initialize() {
        var _this = this;
        _this.add_event_listeners_in_tag_element();
        if(_this.email_id_list.length > 0){
            for(let i = 0; i<_this.email_id_list.length; i++){
            var tag_remove_btns = _this.tag_container.querySelectorAll("[class='tag-remove-btn']");
            tag_remove_btns.forEach(function(tag_remove_btn, index) {
                $(tag_remove_btn).on("click", function() {
                    _this.remove_email_id_tags(index);
                });
            });   
            }
        }
    }

    add_event_listeners_in_tag_element() {
        var _this = this;

        $(_this.element).on("keypress", function(event) {
            var target = event.target;
            var value = target.value;


            if (event.key === 'Enter' || event.keyCode == 13) {
                let val = value.trim().replace(/(<([^>]+)>)/ig, '');
                if (!check_valid_email(value)) {
                    showToast("Please enter valid email", 2000);

                } else {
                    var email_id_exist = _this.email_id_list.some(value => value === val);
                    if (email_id_exist) {
                        showToast("Email ID already exist", 2000);

                    } else {
                        _this.email_id_list.push(value);
                        _this.render_email_id_tags();
                    }

                    target.value = "";
                }
            }
        });
    }

    render_email_id_tags() {
        var _this = this;

        function add_event_listener_in_remove_btn() {

            var tag_remove_btns = _this.tag_container.querySelectorAll("[class='tag-remove-btn']");
            tag_remove_btns.forEach(function(tag_remove_btn, index) {
                $(tag_remove_btn).on("click", function() {
                    _this.remove_email_id_tags(index);
                });
            });
        }

        var html = "";
        _this.email_id_list.forEach(function(value, index) {
            html += `
        <li class="bg-primary cognoai-tag" value="${value}">
            <span style="font-weight: 500; line-height:1.2; word-break:break-word;">${value}</span>
            <span class="tag-remove-btn">x</span>
        </li>`;
        });

        _this.tag_container.innerHTML = html;

        add_event_listener_in_remove_btn();
    }

    remove_email_id_tags(removed_index) {
        var _this = this;
        var updated_email_id_list = [];
        for (var idx = 0; idx < _this.email_id_list.length; idx++) {
            if (idx == removed_index) {
                continue;
            }
            updated_email_id_list.push(_this.email_id_list[idx]);
        }

        _this.email_id_list = updated_email_id_list;
        _this.render_email_id_tags();
    }

    get_value() {
        var _this = this;
        return _this.email_id_list;
    }

    update_value(email_id_list) {
        var _this = this;
        _this.email_id_list = email_id_list;
        _this.render_email_id_tags();
    }
}

function check_valid_email(email_id) {
    if (!email_id) {
        return false;
    }

    var regex_email = /^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/;
    if (!regex_email.test(email_id)) {
        return false;
    }
    return true;
}

function hideIcon(self) {
    self.style.backgroundImage = 'none';
}

function show_profile_details_tab(pk){
    var email_profile_pks = JSON.parse(window.EMAIL_PROFILE_PKS);

    for(let i=0;i<email_profile_pks.length;i++){
        document.getElementById("profile-details-tab-"+email_profile_pks[i]).style.display = "none";
        $("#profile-heading-tab-"+email_profile_pks[i]).removeClass('active'); 
    }
    document.getElementById("profile-details-tab-new").style.display = "none";
    $("#profile-heading-tab-new").removeClass('active'); 

    document.getElementById("profile-details-tab-"+pk).style.display = "block";
    $("#profile-heading-tab-"+pk).addClass('active');
    state.current_selected_profile = pk; 

}

function delete_email_profile(pk){
    if(pk=='new'){
        showToast("Email Profile Deleted", 2000);
        location.reload();
    }
    var json_string = JSON.stringify({
        email_profile_pk: pk
    });
    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;    
    xhttp.open("POST", "/livechat/delete-email-profile/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                showToast("Email Profile Deleted", 2000);
                location.reload();
            }
        }
    };
    xhttp.send(params);
}

function trigger_sample_mail(){
    let pk = state.current_selected_profile;
    if(!pk) return;

    if(pk=='new'){
        showToast("Save the Email Profile", 4000);
        return;
    }

    document.getElementById("analytics-sample-mail-btn").innerHTML = "Sending...";
    var json_string = JSON.stringify({
        email_profile_pk: pk
    });
    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;    
    xhttp.open("POST", "/livechat/send-sample-mail/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                showToast("Mail Sent Successfully", 2000);
            } else {
                showToast(response["message"], 2000);
            }
            document.getElementById("analytics-sample-mail-btn").innerHTML = 'Trigger Sample Email'
        }
    };
    xhttp.send(params);
}

function apply_email_configuration_event_listeners() {
    $("#livechat-email-conversation-cb").on('change', function(e) {
        enable_disable_livechat_for_email();
    })

    $(".livechat-email-protocol-btn").click(function() {
        $('.livechat-email-protocol-btn-wrapper').hide();
        $('.close-modal-back-btn').hide();
        $('.livechat-email-back-btn-modal').show();
        $('.livechat-email-protocol-details-wrapper').show();
        $('#livechat-email-authentication-modal .modal-footer').show();
    });

    $(".livechat-email-back-btn-modal").click(function() {
        $('.livechat-email-protocol-btn-wrapper').show();
        $(this).hide();
        $('.close-modal-back-btn').show();
        $('.livechat-email-protocol-details-wrapper').hide();
        $('#livechat-email-authentication-modal .modal-footer').hide();
        document.getElementById('livechat-email-conversation-cb').checked = false;
    });

    $("#email-config-authenticate-btn").click(function() {
        email_config_authentication();
    });

    $(".remove-authentication-toast").click(function() {
        $(this).parent().hide();
    });

    $(".livechat-conversation-email-item svg").click(function() {
        $(this).parent().hide();
        handle_email_config_status(false, false);
        document.getElementById('livechat-email-conversation-cb').checked = false;
    });

    $('#livechat-email-authentication-modal').on('hidden.bs.modal', function () {
      document.getElementById('livechat-email-conversation-cb').checked = false;
    })
}

function apply_email_settings_event_listeners() {
    $("#livechat-email-analytics-configure-btn").on("click", function(event) {
        $("#livechat-email-notification-modal").modal("show");
        if(state.is_render_required) {
            check_and_display_profile_data();
            check_and_render_email_address();
            check_and_render_email_freq();
            state.is_render_required = false;
        }
    });

    $(".email-collapse-heading-div").click(function() {
        $(this).parent().toggleClass("email-collapse-trigger");
    });

    $("#livechat-email-auto-disposal-cb").on("change", function(event) {
        if (this.checked) {
            $(".email-auto-disposal-option-wrapper").show();

        } else {
            $(".email-auto-disposal-option-wrapper").hide();

        }
    });

    $("#livechat-email-session-inactivity-cb").on("change", function(event) {
        if (this.checked) {
            $(".chat-dispose-time-wrapper").show();

        } else {
            $(".chat-dispose-time-wrapper").hide();

        }
    });

    $("#email-configuration-save-btn").on("click", function(event) {
        save_livechat_email_configuration();
    });
}

function enable_disable_livechat_for_email() {
    let is_livechat_enabled_for_email = document.getElementById('livechat-email-conversation-cb').checked;
    if(is_livechat_enabled_for_email) {
        if(window.IS_SUCCESSFUL_AUTHENTICATION_COMPLETE) {
            handle_email_config_status(true, true);
            $(".livechat-conversation-email-item").css("display", "inline-flex");

        } else {
            $("#livechat-email-authentication-modal").modal("show");
        }
    } else {
        handle_email_config_status(false, true);
        $(".livechat-conversation-email-item").hide();
    }
}

async function email_config_authentication() {
    let email_config_id = $("#email-config-id").val();
    let email_config_password = $("#email-config-password").val();
    let email_config_server = $("#email-config-server").val();
    let email_config_security = $("#email-config-security").val();

    if (email_config_id == "" || validate_email("email-config-id") == false) {
        showToast("Please enter valid email.", 2000);
        return;
    }

    if (email_config_password == "") {
        showToast("Please enter password.", 2000);
        return;
    }

    if (email_config_server == "") {
        showToast("Please enter imap server.", 2000);
        return;
    }

    if (email_config_security == "") {
        showToast("Please choose valid security.", 2000);
        return;
    }

    email_config_server = stripHTML(email_config_server);
    email_config_security = stripHTML(email_config_security);

    document.getElementById("email-config-authenticate-btn").innerText = "Authenticating...";
    $("#email-config-authenticate-btn").css("pointer-events", "none");
    $("#livechat-email-conversation-cb").attr("disabled", true);
    const response = await get_email_config_authentication_status(email_config_id, email_config_password, email_config_server, email_config_security);

    if(response.authentication_status == "success") {
        $(".email-authentication-success-toast").css("display", "flex");

    } else if (response.authentication_status == "fail") {
        document.getElementById('livechat-email-conversation-cb').checked = false;
        $(".email-authentication-failed-toast").css("display", "flex");

    }
    setTimeout(() => {location.reload();}, 2000);
}

function get_email_config_authentication_status(email_config_id, email_config_password, email_config_server, email_config_security) {
    return new Promise((resolve, reject) => {

        let json_string = {
            email_config_id: email_config_id,
            email_config_password: email_config_password,
            email_config_server: email_config_server, 
            email_config_security: email_config_security,
        };

        json_string = JSON.stringify(json_string);
        const params = get_params(json_string);

        let config = {
              headers: {
                'X-CSRFToken': getCsrfToken(),
              }
            }

        axios
            .post("/livechat/email-config-authentication/", params, config)
            .then((response) => {
                response = custom_decrypt(response.data);
                response = JSON.parse(response);
                
                if (response.status == 200) {
                    $("#livechat-email-authentication-modal").modal("hide");
                    resolve(response);
                } 
            })       
            .catch((err) => {
                console.log(err);
            });

    });
}

function handle_email_config_status(is_livechat_enabled_for_email, is_successful_authentication_complete) {

    let json_string = {
        is_livechat_enabled_for_email: is_livechat_enabled_for_email,
        is_successful_authentication_complete: is_successful_authentication_complete,
    };

    json_string = JSON.stringify(json_string);
    const params = get_params(json_string);

    let config = {
          headers: {
            'X-CSRFToken': getCsrfToken(),
          }
        }

    axios
        .post("/livechat/handle-email-config-status/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);
            
            if (response.status == 200) {

                if(!is_livechat_enabled_for_email) {
                    if(is_successful_authentication_complete) {
                        showToast("Disabled LiveChat Conversations through Email Channel.", 2000);
                    } else {
                        showToast("Email server setup removed.", 2000);
                        setTimeout(() => {location.reload();}, 2000);
                    }
                }
            } 
        })       
        .catch((err) => {
            console.log(err);
        });
}

function save_livechat_email_configuration() {
    let is_auto_disposal_enabled = document.getElementById("livechat-email-auto-disposal-cb").checked;
    let is_session_inactivity_enabled = document.getElementById("livechat-email-session-inactivity-cb").checked;
    let chat_disposal_duration = document.getElementById("livechat-email-session-inactivity-duration").value;
    let is_followup_leads_over_mail_enabled = document.getElementById("livechat-email-followup-leads-cb").checked;

    if(is_session_inactivity_enabled && (chat_disposal_duration == "" || parseInt(chat_disposal_duration) < 1 || parseInt(chat_disposal_duration) > 50)) {
        showToast('Please enter integer value between 1 to 50 in "Time After Which Chat Should Dispose field"', 3000);
        return;        
    }

    let json_string = {
        is_auto_disposal_enabled: is_auto_disposal_enabled,
        is_session_inactivity_enabled: is_session_inactivity_enabled,
        chat_disposal_duration: chat_disposal_duration,
        is_followup_leads_over_mail_enabled: is_followup_leads_over_mail_enabled,
    };

    json_string = JSON.stringify(json_string);
    const params = get_params(json_string);

    let config = {
          headers: {
            'X-CSRFToken': getCsrfToken(),
          }
        }

    axios
        .post("/livechat/save-livechat-email-configuration/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);
            
            if (response.status == 200) {
                showToast("Email configuration saved successfully!", 3000);
                setTimeout(() => {location.reload();}, 2000);
            } else {
                showToast(response.message, 2000);
            }
        })       
        .catch((err) => {
            console.log(err);
        });
}

export {
    save_email_profile,
	enable_disable_email_notification,
    add_new_email_profile,
    enable_disable_table_container,
    enable_disable_graph_container,
    enable_disable_attachment_container,
    hideIcon,
    show_profile_details_tab,
    delete_email_profile,
    trigger_sample_mail,
    enable_disable_graph_chat_container,
};
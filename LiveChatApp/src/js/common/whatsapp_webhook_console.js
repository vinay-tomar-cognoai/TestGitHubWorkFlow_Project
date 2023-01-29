import {
    EncryptVariable,
    showToast,
    custom_decrypt,
    getCsrfToken,
} from "../utils";

import {
    check_for_system_commands,
    show_processor_errors,
} from "../admin/developer_settings"


export function open_change_webhook_confirm_modal() {

    change_wsp_code = document.getElementById("eastchat_whatsapp_config_dropdown").value;
    document.getElementById("eastchat_whatsapp_config_dropdown").value = selected_whatsapp_service_provider;
    $('#livechat_whatsapp_config_assign_modal').modal("show");
}

export function get_whatsapp_webhook_default_code(wsp_code) {

    if (selected_whatsapp_service_provider != null && is_change_webhook_code_confirmed == false && wsp_code != selected_whatsapp_service_provider) {
        open_change_webhook_confirm_modal();
        return;
    }

    if (wsp_code == "none") {
        document.getElementById("whatsapp_webhook_function_div").style.display = "none";
        var editor = ace.edit("editor-code");
        editor.setValue("");
        document.getElementById("save_wa_webhook_btn").setAttribute("disabled", "");
        document.getElementById("reset_wa_webhook_btn").setAttribute("disabled", "");
        return;
    } else {
        document.getElementById("whatsapp_webhook_function_div").style.display = "flex";
        document.getElementById("save_wa_webhook_btn").removeAttribute("disabled");
        document.getElementById("reset_wa_webhook_btn").removeAttribute("disabled");
    }

    var json_string = JSON.stringify({
        wsp_code: wsp_code
    })

    json_string = EncryptVariable(json_string);
    var CSRF_TOKEN = getCsrfToken();

    var response = $.ajax({
        url: '/livechat/get-livechat-webhook-default-code/',
        type: "POST",
        async: false,
        headers: {
            "X-CSRFToken": CSRF_TOKEN
        },
        data: {
            json_string: json_string,
        },
        success: function(response) {
            response = custom_decrypt(response);
            response = JSON.parse(response);

            var editor = ace.edit("editor-code");

            if (response["status"] == 200){
                editor.setValue(response["default_code"]);
            } else {
                showToast(response["message"], 2000);
                editor.setValue("");
            }

            var code_title = document.getElementsByClassName("livechat-whatsapp-config-bot-name-div")[0].innerText.split(" ")[0];
            code_title += " - " + response["wsp_name"];
            document.getElementsByClassName("livechat-whatsapp-config-bot-name-div")[0].innerText = code_title;
        },
        error: function(error) {
            console.log("Error in get-livechat-webhook-default-code");
        }
    });
}

export function save_whatsapp_webhooks_content(bot_id, is_auto_save=false) {

    editor = ace.edit("editor-code");
    var code = editor.getValue();
    var wsp_code = document.getElementById("eastchat_whatsapp_config_dropdown").value;

    if (check_for_system_commands(code)) {
        showToast("Code contains system-commands. Please remove them and save again.", 2000);
        document.getElementById("livechat-processor-status").value = "\n\nError(s):";
        show_processor_errors();
        return;
    };

    if (wsp_code == "none") {
        showToast("Please select valid WhatsApp BSP.", 2000);
        return;
    }
    
    var json_string = JSON.stringify({
        code: code,
        bot_id: bot_id,
        wsp_code: wsp_code
    })
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = 'json_string=' + json_string
    xhttp.open("POST", "/livechat/save-livechat-webhook-content/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                if (is_auto_save == false) {
                    showToast("Changes saved successfully.", 2000);
                    setTimeout(function(e) {
                        window.location.reload();
                    }, 2000);
                } else {
                    document.getElementById("livechat-auto-save-tag").style.display = "block";
                    setTimeout(function(e) {
                        document.getElementById("livechat-auto-save-tag").style.display = "none";
                    }, 2000);
                }
            } else if (response["status"] == 300) {

                showToast(response["message"], 2000);
            } else if (response["status"] == 400) {

                showToast(response["message"], 2000);
            } else {
                
                showToast("An Error occured cannot save the function.", 2000);
            }
        }
    }
    xhttp.send(params);
}

export function change_webhook_code() {

    is_change_webhook_code_confirmed = true;
    document.getElementById("eastchat_whatsapp_config_dropdown").value = change_wsp_code;
    get_whatsapp_webhook_default_code(change_wsp_code);
    $('#livechat_whatsapp_config_assign_modal').modal("hide");
}

export function reset_whatsapp_webhook_code() {

    if (selected_whatsapp_service_provider == null || selected_whatsapp_service_provider == "") {
        return;
    }

    document.getElementById("eastchat_whatsapp_config_dropdown").value = selected_whatsapp_service_provider;
    get_whatsapp_webhook_default_code(selected_whatsapp_service_provider);
    $("#modal-whatsapp-reset-config").modal("hide");
}

function get_url_vars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m, key, value) {
        vars[key] = value;
    });
    return vars;
}

export function auto_save_webhook_code() {

    if (document.getElementById("eastchat_whatsapp_config_dropdown").value == "none") {
        return;
    }
    var bot_id = get_url_vars()["bot_pk"];
    save_whatsapp_webhooks_content(bot_id, true);
}

export function continue_collaborative_coding() {

    document.getElementById("whatsapp_webhook_function_div").style.display = "flex";
    auto_save_interval = setInterval(auto_save_webhook_code, auto_save_time_interval);
    document.getElementById("eastchat_whatsapp_config_dropdown").disabled = false;
    document.getElementById("save_wa_webhook_btn").removeAttribute("disabled");
    document.getElementById("reset_wa_webhook_btn").removeAttribute("disabled");
    $("#modal-whatsapp-already-working-config").modal("hide");
}

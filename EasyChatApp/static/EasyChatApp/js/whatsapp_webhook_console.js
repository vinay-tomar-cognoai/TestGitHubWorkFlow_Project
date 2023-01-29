var is_change_webhook_code_confirmed = false;
var auto_save_interval = null;
var auto_save_time_interval = 30000;
var change_wsp_code = "";

$(document).ready(function() {
    window.setTimeout(function (){
        $('#eastchat_whatsapp_config_dropdown').select2({
            dropdownParent: $('#eastchat_whatsapp_config_dropdown_container')
        });
    }, 500);
})

function open_change_webhook_confirm_modal() {
    change_wsp_code = document.getElementById("eastchat_whatsapp_config_dropdown").value;
    document.getElementById("eastchat_whatsapp_config_dropdown").value = selected_whatsapp_service_provider;
    $('#eastchat_whatsapp_config_dropdown').select2({
        dropdownParent: $('#eastchat_whatsapp_config_dropdown_container')
    });
    $('#easychat_whatsapp_config_assign_modal').modal("open");
}

function get_whatsapp_webhook_default_code(wsp_code) {

    if (selected_whatsapp_service_provider != null && is_change_webhook_code_confirmed == false && wsp_code != selected_whatsapp_service_provider) {
        open_change_webhook_confirm_modal();
        return;
    }

    if (wsp_code == "none") {
        document.getElementById("whatsapp_webhook_function_div").style.display = "none";
        var editor = ace.edit("editor-code-whatsapp");
        editor.setValue("");
        document.getElementById("save_wa_webhook_btn").setAttribute("disabled", "");
        document.getElementById("reset_wa_webhook_btn").setAttribute("disabled", "");
        return;
    } else {
        document.getElementById("whatsapp_webhook_function_div").style.display = "block";
        document.getElementById("save_wa_webhook_btn").removeAttribute("disabled");
        document.getElementById("reset_wa_webhook_btn").removeAttribute("disabled");
    }

    var json_string = JSON.stringify({
        wsp_code: wsp_code
    })

    json_string = EncryptVariable(json_string);

    var response = $.ajax({
        url: '/chat/get-wa-webhook-default-code/',
        type: "POST",
        async: false,
        data: {
            json_string: json_string,
        },
        success: function(response) {
            response = custom_decrypt(response);
            response = JSON.parse(response);

            var editor = ace.edit("editor-code-whatsapp");

            if (response["status"] == 200){
                editor.setValue(response["default_code"]);
            } else {
                showToast(response["message"]);
                editor.setValue("");
            }

            var code_title = document.getElementsByClassName("easychat-whatsapp-config-bot-name-div")[0].innerText.split(" ")[0];
            code_title += " - " + response["wsp_name"];
            document.getElementsByClassName("easychat-whatsapp-config-bot-name-div")[0].innerText = code_title;
        },
        error: function(error) {
            console.log("Error in get-wa-webhook-default-code");
        }
    });
}

function save_whatsapp_webhooks_content(bot_id, is_auto_save=false) {

    var editor = ace.edit("editor-code-whatsapp");
    var code = editor.getValue();
    var wsp_code = document.getElementById("eastchat_whatsapp_config_dropdown").value;

    if (check_for_system_commands(code)) {
        M.toast({
            "html": "Code contains system-commands. Please remove them and save again."
        }, 2000);
        document.getElementById("easychat-processor-status").value = "\n\nError(s):";
        show_processor_errors();
        return;
    };

    if (wsp_code == "none") {
        M.toast({
            "html": "Please select valid WhatsApp BSP."
        }, 2000);
        return;
    }
    
    csrf_token = get_csrf_token();
    var json_string = JSON.stringify({
        code: code,
        bot_id: bot_id,
        wsp_code: wsp_code
    })
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);
    var xhttp = new XMLHttpRequest();
    var params = 'json_string=' + json_string
    xhttp.open("POST", "/chat/save-whatsapp-webhook-content/", true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                if (is_auto_save == false) {
                    M.toast({
                        "html": "Changes saved successfully."
                    }, 2000);
                    setTimeout(function(e) {
                        window.location.reload();
                    }, 2000);
                } else {
                    document.getElementById("easychat-auto-save-tag").style.display = "block";
                    setTimeout(function(e) {
                        document.getElementById("easychat-auto-save-tag").style.display = "none";
                    }, 2000);
                }
            } else if (response["status"] == 300) {
                M.toast({
                    "html": response["message"]
                })
            } else if (response["status"] == 400) {

                M.toast({
                    "html": response["message"]
                })
            } else {
                M.toast({
                    "html": "An Error occured cannot save the function."
                })
            }
        }
    }
    xhttp.send(params);
}

function reset_whatsapp_webhook_code() {

    if (selected_whatsapp_service_provider == null || selected_whatsapp_service_provider == "") {
        return;
    }

    document.getElementById("eastchat_whatsapp_config_dropdown").value = selected_whatsapp_service_provider;
    $('#eastchat_whatsapp_config_dropdown').select2({
        dropdownParent: $('#eastchat_whatsapp_config_dropdown_container')
    });

    get_whatsapp_webhook_default_code(selected_whatsapp_service_provider);
}

function change_webhook_code() {

    is_change_webhook_code_confirmed = true;
    document.getElementById("eastchat_whatsapp_config_dropdown").value = change_wsp_code;
    $('#eastchat_whatsapp_config_dropdown').select2({
        dropdownParent: $('#eastchat_whatsapp_config_dropdown_container')
    });
    get_whatsapp_webhook_default_code(change_wsp_code);
}

function close_change_webhook_confirm_modal() {

    $('#easychat_whatsapp_config_assign_modal').modal("close");
}

function auto_save_webhook_code() {

    if (document.getElementById("eastchat_whatsapp_config_dropdown").value == "none") {
        return;
    }
    var bot_id = get_url_vars()["bot_pk"];
    save_whatsapp_webhooks_content(bot_id, true);
}

function continue_collaborative_coding() {

    document.getElementById("whatsapp_webhook_function_div").style.display = "block";
    auto_save_interval = setInterval(auto_save_webhook_code, auto_save_time_interval);
    document.getElementById("eastchat_whatsapp_config_dropdown").disabled = false;
    document.getElementById("save_wa_webhook_btn").removeAttribute("disabled");
    document.getElementById("reset_wa_webhook_btn").removeAttribute("disabled");
}

$(document).ready(function () {

    if (is_any_other_user_active) {
        setTimeout(function() {
            $("#easychat_whatsapp_config_already_working_modal").modal("open");
        }, 500);
        document.getElementById("eastchat_whatsapp_config_dropdown").disabled = true;
        document.getElementById("save_wa_webhook_btn").setAttribute("disabled", "");
        document.getElementById("reset_wa_webhook_btn").setAttribute("disabled", "");
    }

    if (selected_whatsapp_service_provider != null && !is_any_other_user_active) {
        auto_save_interval = setInterval(auto_save_webhook_code, auto_save_time_interval);
    }
})

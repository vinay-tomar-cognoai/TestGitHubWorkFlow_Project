$(document).ready(function() {
    var select_el = document.getElementById("campaign-list-select");
    var select_element_obj = new EasyassistCustomSelect(select_el, null, null);
})

function get_selected_bot_wsp_code(wsp_code, is_reset=false) {
    var bot_pk = get_url_vars()['bot_pk'];
    
    if (wsp_code == 'none') {
        document.getElementById("campaign-api-code-editor").style.display = "none";
        document.getElementById("save-wa-code-btn").disabled = true;
        document.getElementById("reset-wa-code-btn").disabled = true;
        return;
    }

    var request_params = {
        bot_pk: bot_pk,
        wsp_code: wsp_code,
        is_reset: is_reset,
    };

    var json_params = JSON.stringify(request_params);
    var encrypted_data = campaign_custom_encrypt(json_params);
    encrypted_data = {
        Request: encrypted_data,
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/campaign/get-selected-bot-wsp-code/", true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.setRequestHeader("X-CSRFToken", get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if (response.status == 200) {
                var editor = ace.edit("editor-code");
                editor.setValue(response.api_code);

                var code_title = document.getElementsByClassName("campaign-whatsapp-config-bot-name-div")[0].innerText.trim().split(" ")[0];
                code_title += " - " + response.wsp_name;
                document.getElementsByClassName("campaign-whatsapp-config-bot-name-div")[0].innerText = code_title;

                document.getElementById("campaign-api-code-editor").style.display = "block";
                if (response.wsp_code == "1"){ // 1 is default for Ameyo
                    document.getElementById("namespace-input-text").style.display = "flex";
                    document.getElementById("campaign-namespace").style.display = "block";
                    document.getElementById("campaign-namespace").value = response.namespace;
                    $('.campaign-tooltip-namespace').tooltip();
                }
                else {
                    document.getElementById("campaign-namespace").style.display = "none";
                    document.getElementById("namespace-input-text").style.display = "none";
                }
            } else {
                show_campaign_toast(response.status_message);
                var editor = ace.edit("editor-code");
                editor.setValue('');
            }

            document.getElementById("save-wa-code-btn").disabled = false;
            document.getElementById("reset-wa-code-btn").disabled = false;
        }
    };

    xhttp.send(params);
}


function save_api_code() {

    var wsp_code = document.getElementById("campaign-list-select").value;
    var bot_pk = get_url_vars()["bot_pk"];

    if (wsp_code == 'none') {
        show_campaign_toast('Please select a WhatsApp service provider.');
        return;
    }

    let namespace = ""
    let reg = /[\s~`!@#$%\^&*+=\-\[\]\\';,/{}|\\":<>\?()\.]/g
    let letter_reg = /[a-zA-Z]/
    if (wsp_code == "1") {  // 1 is for Ameyo by default
        namespace = document.getElementById("campaign-namespace").value;
        document.getElementById("warning-msg-namespace").style.display = "none";
        document.getElementById("sp-char-warning-msg-namespace").style.display = "none";
        document.getElementById("warning-msg-namespace-length").style.display = "none";
        document.getElementById("success-msg-namespace").style.display = "none";
        if (namespace == "") {
            document.getElementById("warning-msg-namespace").style.display = "flex";
            $('#warning-msg-namespace').delay(4000).fadeOut(2000);
            return;
        } else if (reg.test(namespace) || !letter_reg.test(namespace)) {
            document.getElementById("sp-char-warning-msg-namespace").style.display = "flex";
            $('#sp-char-warning-msg-namespace').delay(5000).fadeOut(3000);
            return;
        } else if (namespace.length < 8 || namespace.length > 45 ) {
            document.getElementById("warning-msg-namespace-length").style.display = "flex";
            $('#warning-msg-namespace-length').delay(5000).fadeOut(3000);
            return;
        }
    }

    var editor = ace.edit("editor-code");
    var code = editor.getValue();

    if (check_for_system_commands(code)) {
        show_campaign_toast("Code contains system commands. Please remove them and try again.");
        document.getElementById("campaign-processor-status").value = "\n\nError(s):";
        show_processor_errors();
        return;
    }

    var request_params = {
        wsp_code: wsp_code,
        code: code,
        bot_pk: bot_pk,
        namespace: namespace,
    };

    var json_params = JSON.stringify(request_params);
    var encrypted_data = campaign_custom_encrypt(json_params);
    encrypted_data = {
        Request: encrypted_data,
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/campaign/save-api-code/", true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.setRequestHeader("X-CSRFToken", get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if (response.status == 200) {
                document.getElementById("success-msg-namespace").style.display = "flex";
                $('#success-msg-namespace').delay(4000).fadeOut(2000);;
            } else {
                show_campaign_toast(response.status_message);

                if(check_for_system_commands(code)) show_processor_errors();
            }
        }
    };

    xhttp.send(params);

}

function reset_bot_wsp_code() {

    var wsp_code = document.getElementById("campaign-list-select").value;

    if (wsp_code == "none") {
        show_campaign_toast('Please select a WhatsApp service provider.');
        $("#whatsapp_config_reset_modal").modal("hide");
        return;
    }

    get_selected_bot_wsp_code(wsp_code, true);
    $("#whatsapp_config_reset_modal").modal("hide");
}

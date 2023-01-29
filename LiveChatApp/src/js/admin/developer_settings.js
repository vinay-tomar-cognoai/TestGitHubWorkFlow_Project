import { custom_decrypt, EncryptVariable, getCsrfToken, showToast, get_url_vars } from "../utils";

(function ($) {
    $(function () {
        if(String(window.location.href).includes('developer-settings') && document.getElementById("developer-bot")){
            let bot_pk = document.getElementById("developer-bot").value;
            enable_disable_ticket_raise_functionality(bot_pk);
        }

    }); // end of document ready
})(jQuery); // end of jQuery name space

const state = {
    highlighted_lines: {},
    processor_errors: {},
    system_commands: window.SYSTEM_COMMANDS,
}

function bot_changed() {
    document.getElementById("choose-function").style.display = "block";
    document.getElementById("go-button").style.display = "block";
    let bot_pk = document.getElementById("developer-bot").value;
    enable_disable_ticket_raise_functionality(bot_pk);
    
    document.getElementById('type_of_editor').value = '0';
    $('#type_of_editor').selectpicker('refresh');
}

function enable_disable_ticket_raise_functionality(bot_pk) {

    if (bot_pk in window.TICKET_RAISE_FUNCTIONALITY && window.TICKET_RAISE_FUNCTIONALITY[bot_pk] == "True") {
        document.getElementById("customize-raise-ticket-form-option").style.display = "block";
        document.getElementById("raise-ticket-option").style.display = "block";
        document.getElementById("search-ticket-option").style.display = "block";
        document.getElementById("get-previous-tickets-option").style.display = "block";
    } else {
        document.getElementById("customize-raise-ticket-form-option").style.display = "none";
        document.getElementById("raise-ticket-option").style.display = "none";
        document.getElementById("search-ticket-option").style.display = "none";
        document.getElementById("get-previous-tickets-option").style.display = "none";        
    }
}

function go_to_developer_editor() {
    const bot_pk = document.getElementById('developer-bot').value;
    const selected_option = document.getElementById('type_of_editor').value;

    if (bot_pk == "0") {
        showToast("Please select a Bot to proceed", 5000);
        return;
    }

    if (selected_option == "0") {
        showToast("Please select a Function to proceed", 5000);
        return;
    }

    if (selected_option == '4') {
        window.location.href = `/livechat/livechat-form-builder/?bot_pk=${bot_pk}`;
    } else if (selected_option == '6') {
        window.location.href = `/livechat/whatsapp-webhook-console/?bot_pk=${bot_pk}`;
    } else if (selected_option == '7') {
        window.location.href = `/livechat/api-docs/?bot_pk=${bot_pk}`;
    } else if (selected_option == '8') {
        window.location.href = `/livechat/raise-ticket-form-builder/?bot_pk=${bot_pk}`;
    } else {
        window.location.href = `/livechat/developer-editors/?bot_pk=${bot_pk}&editor_id=${selected_option}`;
    }
}

function save_processor(bot_pk, type_of_processor) {
    var editor = ace.edit("editor-code");
    var code = editor.getValue();
    var name_of_processor = document.getElementById("name_of_processor").value;
    if (name_of_processor == "") {
        showToast("Please give a name before saving", 2000);
        return;
    }

    if (check_for_system_commands(code)) {
        showToast("Code contains system commands. Please remove them and then save.", 2000);
        show_processor_errors ();
        return;
    }
    
    let json_string = JSON.stringify({
        name: name_of_processor,
        code: code,
        bot_pk: bot_pk,
        type_of_processor: type_of_processor,
    });
    json_string = EncryptVariable(json_string);

    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
        url: "/livechat/save-livechat-processor/",
        type: "POST",
        headers: {
            "X-CSRFToken": CSRF_TOKEN
        },
        data: {
            json_string: json_string,
        },
        success: function (response) {
            var response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status_code"] == 200) {
                showToast("Processor Saved successfully", 2000);
                window.location.reload();
            } else if (response.status_code == 400) {
                showToast(response.message, 2000);
                if (check_for_system_commands(code)) show_processor_errors ();
            } 
            else {
                showToast("Report this error.", 2000);
            }
        },
        error: function (xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        },
    });
}
function scroll_to_bottom() {
    var objDiv = document.getElementById("livechat-processor-status");
    objDiv.scrollTop = objDiv.scrollHeight;
}

function run_processor_livechat() {
    var dynamic_variable = document.getElementById("livechat_dynamic_variable").value;
    if (dynamic_variable == "") {
        showToast("Please enter a parameter value", 2000);
        return;
    }
    document.getElementById("livechat-processor-status").style.display = "block";
    document.getElementById("livechat-processor-status").value = "Running ...";
    var editor = ace.edit("editor-code");
    var code = editor.getValue();

    if (check_for_system_commands(code)) {
        showToast("Code contains system commands. Please remove them and try again.", 2000);
        show_processor_errors ();
        return;
    }

    let csrf_token = getCsrfToken();
    var json_string = JSON.stringify({
        code: code,
        bot_pk: get_url_vars()['bot_pk'],
        parameter: dynamic_variable,
    });
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/livechat-processor-run/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            let processor_output_text_area = "";

            if (response["status"] == 200) {
                document.getElementById("livechat-processor-status").style.display = "block";
                processor_output_text_area = document.getElementById("livechat-processor-status");
                processor_output_text_area.value = "  Output:\n\n";
                processor_output_text_area.value +=
                    "Excecution time: " + response["elapsed_time"] + "\n\n";
                try {
                    processor_output_text_area.value += JSON.stringify(
                        JSON.parse(response["message"]),
                        null,
                        4
                    );
                } catch (err) {
                    console.log(err);
                    processor_output_text_area.value += JSON.stringify(
                        response["message"],
                        null,
                        4
                    );
                }
                // console.log(response["message"]);
            } else if (response["status"] == 300) {
                document.getElementById("livechat-processor-status").style.display = "block";
                processor_output_text_area = document.getElementById("livechat-processor-status");
                processor_output_text_area.value = "Output:\n\n";
                processor_output_text_area.value +=
                    "Excecution time: " + response["elapsed_time"] + "\n\n";
                processor_output_text_area.value += "Error message!\n\n";
                processor_output_text_area.value += response["message"];
            } else if (response.status == 400) {
                showToast(response.message, 2000);
                if (check_for_system_commands(code)) show_processor_errors ();
                else {
                    processor_output_text_area = document.getElementById("livechat-processor-status");
                    processor_output_text_area.value = '\n\nEnter valid client id or easychat user id.';
                }
            }
        }
    };
    xhttp.send(params);
}

function go_full_screen() {
    if (editor.container.mozRequestFullScreen) {
        editor.container.mozRequestFullScreen();
    } else {
        editor.container.webkitRequestFullscreen();
    }
}

export function check_for_system_commands(code) {
    var Range = ace.require('ace/range').Range;
    var code_lines = code.split('\n')
    var contains_system_commands = false;

    if (!state.system_commands) state.system_commands = window.SYSTEM_COMMANDS;

    for(var i=0; i<code_lines.length; ++i) {
        var line = code_lines[i];
        for(let cmd of state.system_commands) {
            var err_index = line.indexOf(cmd);
            if(err_index != -1) {
                contains_system_commands = true;

                if (!state.highlighted_lines[i]) {
                    var id =editor.session.addMarker(new Range(i, 0, i, 1), "my-marker", "fullLine");
                    state.highlighted_lines[i] = id;
                    state.processor_errors[i] = "Line " + (i+1) + " : " + err_index + " Contains " + cmd + " command which is a system command.";   
                }

                // document.getElementById('system-command-error').style.display = 'block';
                break;
            } else {
                editor.session.removeMarker(state.highlighted_lines[i]);
                state.highlighted_lines[i] = undefined;
                state.processor_errors[i] = "";
            }
        }
    }

    return contains_system_commands;
}

export function show_processor_errors() {
    const processor_output_text_area = document.getElementById("livechat-processor-status");

    processor_output_text_area.value = `\nError(s):`
    for(const key in state.processor_errors) {
        if (state.processor_errors[key] != "") {
            processor_output_text_area.value += '\n\n' + state.processor_errors[key];
        }
    }

    processor_output_text_area.style.display = 'block';
}

export { bot_changed, go_to_developer_editor, save_processor, run_processor_livechat, go_full_screen };

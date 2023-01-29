$(document).ready(function() {
    document.getElementById('campaign-navbar-submenu-1').click();
    if (window.location.href.includes('api-editor') || window.location.href.includes('api-integration')) {
        setTimeout(function() {
            document.getElementById('api_integration_link').classList.add('active');
        }, 100)
    }

    $("#campaign-user-otp").on("keypress", function (event) {
        let keys = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"];

        return keys.indexOf(event.key) > -1;
    });

    $("#campaign-user-otp").on("keyup", function (event) {
        if (event.target.value.length == 6) {
            document.getElementById('verify_otp_btn').disabled = false;
            document.getElementById('verify_otp_btn').classList.remove('easyassist-disabled-input');
        } else {
            document.getElementById('verify_otp_btn').disabled = true;
            document.getElementById('verify_otp_btn').classList.add('easyassist-disabled-input');
        }
    });

    if (window.location.pathname.includes('api-integration')) {
        document.querySelector('#campaign-user-email').addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                document.getElementById('send_otp_btn').click();
            }
        });
    
        document.querySelector('#campaign-user-otp').addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                document.getElementById('verify_otp_btn').click();
            }
        });
    }
})

/* GLOBAL VARIABLES */

var system_commands = window.SYSTEM_COMMANDS ? window.SYSTEM_COMMANDS : ['os.system', 'subprocess', 'import threading', 'threading.Thread', 'ssh'];
var highlighted_lines = {};
var processor_errors = {};

/* GLOBAL VARIABLES ENDS */


function validate_email(email) {
    const regEmail = /^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/;

    return regEmail.test(email);
}

function empty_otp_fields() {
    let otp_elems = document.getElementsByClassName("otp-form");

    for (let otp_elem of otp_elems) {
        otp_elem.value = "";
    }
}

async function send_otp(el) {
    var email = document.getElementById("campaign-user-email").value.trim();

    if (email == "") {
        document.getElementById('send-otp-errors').innerHTML = 'Please enter your Email ID';
        return;
    } else {
        document.getElementById('send-otp-errors').innerHTML = '';
    }

    if (!validate_email(email)) {
        document.getElementById('send-otp-errors').innerHTML = 'Please enter a valid Email ID';
        return;
    } else {
        document.getElementById('send-otp-errors').innerHTML = '';
    }

    var email_ends_with = email.split('@')[1];
    
    if (email_ends_with != 'getcogno.ai') {
        document.getElementById('send-otp-errors').innerHTML = 'Email ID ending with getcogno.ai only is valid for API Integration';
        return;
    } else {
        document.getElementById('send-otp-errors').innerHTML = '';
    }

    show_campaign_toast('Please wait while we are verifying your email id.')
    el.disabled = true;
    el.classList.add('easyassist-disabled-input');

    var response = await send_otp_code(email);

    if (response.status == 200) {
        el.style.display = 'none';
        document.getElementById('campaign-otp-div').style.display = 'block';
        document.getElementById("campaign-user-email").disabled = true;
        document.getElementById("campaign-user-email").classList.add('easyassist-disabled-input');
    }
}

function send_otp_code(email) {
    return new Promise(function (resolve, reject) {
        var request_params = {
            email: email,
        };

        var json_params = JSON.stringify(request_params);
        var encrypted_data = campaign_custom_encrypt(json_params);
        encrypted_data = {
            Request: encrypted_data,
        };
        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/campaign/send-otp/", true);
        xhttp.setRequestHeader("Content-Type", "application/json");
        xhttp.setRequestHeader("X-CSRFToken", get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                var response = JSON.parse(this.responseText);
                response = campaign_custom_decrypt(response.Response);
                response = JSON.parse(response);

                if (response.status == 200 || response.status == 202) {
                    resolve(response);
                } else {
                    document.getElementById('send-otp-errors').innerHTML = response.status_message;
                    document.getElementById("send_otp_btn").innerHTML = 'Send OTP';
                    document.getElementById("send_otp_btn").disabled = false;
                    document.getElementById("send_otp_btn").classList.remove('easyassist-disabled-input')
                }
            }
        };
        xhttp.send(params);
    });
}

async function check_otp() {
    var entered_otp = document.getElementById("campaign-user-otp").value;

    if (entered_otp == "") {
        document.getElementById('sent-otp-info').innerHTML = "Please enter otp before submitting.";
        document.getElementById('sent-otp-info').style.color = 'red';
        return;
    } else if (entered_otp.length < 6 || entered_otp.length > 6) {
        document.getElementById('sent-otp-info').innerHTML = "Please enter valid 6 digit otp code";
        document.getElementById('sent-otp-info').style.color = 'red';
        return;

    } else {
        document.getElementById('sent-otp-info').innerHTML = "You will receive an OTP on your entered email id. Use that OTP to verify yourself.";
        document.getElementById('sent-otp-info').style .color = '#858796';
    }

    var access_token = await match_otp_from_server(entered_otp);

    go_to_code_editor(access_token);
}

function match_otp_from_server(entered_otp) {
    return new Promise(function (resolve, reject) {
        var email = document.getElementById("campaign-user-email").value.trim();

        var request_params = {
            otp: entered_otp,
            email: email,
        };

        var json_params = JSON.stringify(request_params);
        var encrypted_data = campaign_custom_encrypt(json_params);
        encrypted_data = {
            Request: encrypted_data,
        };
        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/campaign/verify-user/", true);
        xhttp.setRequestHeader("Content-Type", "application/json");
        xhttp.setRequestHeader("X-CSRFToken", get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                var response = JSON.parse(this.responseText);
                response = campaign_custom_decrypt(response.Response);
                response = JSON.parse(response);

                if (response.status == 200) {
                    var access_token = response.access_token;
                    resolve(access_token);
                } else {
                    document.getElementById('sent-otp-info').innerHTML = response.status_message;
                    document.getElementById('sent-otp-info').style.color = 'red';
                }
            }
        };

        xhttp.send(params);
    });
}

function go_to_code_editor(access_token) {
    window.location.href = window.location.origin + '/campaign/api-editor/?bot_pk=' + BOT_ID + '&access_token=' + access_token
}


function get_url_vars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m, key, value) {
        vars[key] = value;
    });
    return vars;
}

/* API Editor Functions */

function set_api_completed_status(is_api_completed) {
    var el = document.getElementById('api_completion_status');
    
    if (is_api_completed) {
        el.innerHTML = 'Completed';
        el.disabled = true;
    } else {
        el.innerHTML = 'Pending';
        el.disabled = false;
    }

    el.style.display = 'block';
}

function enable_editing() {
    document.getElementById('save_api_btn').disabled = false;
    document.getElementById('save_api_btn').classList.remove('easyassist-disabled-input');
    document.getElementById('run_api_btn').style.display = 'block';
    document.getElementById('api_completion_status').style.display = 'block';
}

function disable_editing() {
    document.getElementById('save_api_btn').disabled = true;
    document.getElementById('save_api_btn').classList.add('easyassist-disabled-input');
    document.getElementById('run_api_btn').style.display = 'none';
    document.getElementById('api_completion_status').style.display = 'none';
}

function mark_api_integration_completed(el) {
    var access_token = get_url_vars()['access_token'];
    var bot_pk = get_url_vars()['bot_pk'];
    var campaign_id = document.getElementById('campaign-list-select').value;

    if (campaign_id == 'none') {
        show_campaign_toast('Please select a campaign.');
        return;
    }

    var request_params = {
        campaign_id: campaign_id,
        access_token: access_token,
        bot_pk: bot_pk,
    };

    var json_params = JSON.stringify(request_params);
    var encrypted_data = campaign_custom_encrypt(json_params);
    encrypted_data = {
        Request: encrypted_data,
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/campaign/mark-api-integration-completed/", true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.setRequestHeader("X-CSRFToken", get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if (response.status == 200) {
                show_campaign_toast(response.status_message);
                set_api_completed_status(true);
            } else {
                show_campaign_toast(response.status_message);
            }

            $('#api_completed_confirmation_modal').modal('hide');
        }
    };

    xhttp.send(params);

}

function go_full_screen_mode() {
    if (editor.container.mozRequestFullScreen) {
        editor.container.mozRequestFullScreen();
    } else {
        editor.container.webkitRequestFullscreen();
    }
}

function show_api_status_toast() {
    show_campaign_toast('Click if API Integration is completed.')
}

function run_api_code() {
    var campaign_id = document.getElementById('campaign-list-select').value;
    var bot_pk = get_url_vars()['bot_pk'];

    if (campaign_id == 'none') {
        show_campaign_toast('Please select a campaign.');
        return;
    }

    var editor = ace.edit("editor-code");
    var code = editor.getValue();

    document.getElementById("campaign-processor-status").value = 'Running...';
    
    if (check_for_system_commands(code)) {
        show_campaign_toast("Code contains system commands. Please remove them and try again.");
        document.getElementById("campaign-processor-status").value = "\n\nError(s):";
        show_processor_errors();
        return;
    }

    var request_params = {
        'code': code,
        'bot_pk': bot_pk,
    };

    var json_params = JSON.stringify(request_params);
    var encrypted_data = campaign_custom_encrypt(json_params);
    encrypted_data = {
        Request: encrypted_data,
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/campaign/run-api/", true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.setRequestHeader("X-CSRFToken", get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if (response["status"] == 200) {
                document.getElementById("campaign-processor-status").style.display = "block";
                processor_output_text_area = document.getElementById("campaign-processor-status")
                processor_output_text_area.value = "  Output:\n\n"
                processor_output_text_area.value += "Excecution time: " + response["elapsed_time"] + "\n\n"
                for (item in response["message"]) {
                    if (typeof response["message"][item] == 'object') {
                        processor_output_text_area.value += "  " + item + ": {\n"
                        for (items in response["message"][item]) {
                            processor_output_text_area.value += "    " + items + ": " + response["message"][item][items] + "\n";
                        }
                        processor_output_text_area.value += "     }\n\n"
                    } else {
                        processor_output_text_area.value += "  " + item + ": " + response["message"][item] + "\n\n";
                    }
                }
            } else if (response["status"] == 300) {
                document.getElementById("campaign-processor-status").style.display = "block";
                processor_output_text_area = document.getElementById("campaign-processor-status");
                processor_output_text_area.value = "Output:\n\n";
                processor_output_text_area.value += "Excecution time: " + response["elapsed_time"] + "\n\n";
                processor_output_text_area.value += "Error(s):\n\n";
                processor_output_text_area.value += response["message"];

            } else if (response["status"] == 400) {
                if (check_for_system_commands(code)) {
                    show_processor_errors();
                }
            }
        }
    }
    xhttp.send(params);
}

function show_api_status_confirmation_modal() {
    $('#api_completed_confirmation_modal').modal('show');
}

function set_session_expire_timeout() {
    var curr_data = new Date()
    var total_seconds = curr_data.getTime() / 1000;

    var time_left = (EXPIRE_TIME_SECONDS - total_seconds) * 1000;

    // to show alert modal before 10 minutes
    time_left = time_left - (10*60*1000);

    setTimeout(show_session_expire_alert_modal, time_left);
}

function show_session_expire_alert_modal() {
    $('#session_expire_alert_modal').modal('show');
}

function extend_session() {
    var access_token = get_url_vars()['access_token'];

    var request_params = {
        access_token: access_token,
    };

    var json_params = JSON.stringify(request_params);
    var encrypted_data = campaign_custom_encrypt(json_params);
    encrypted_data = {
        Request: encrypted_data,
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/campaign/extend-session/", true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.setRequestHeader("X-CSRFToken", get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if (response.status == 200) {
                show_campaign_toast(response.status_message);
                
                EXPIRE_TIME_SECONDS = response.expire_time_seconds;
                set_session_expire_timeout();
            } else {
                show_campaign_toast(response.status_message);
            }

            $('#session_expire_alert_modal').modal('hide');
        }
    };

    xhttp.send(params);

}

function check_for_system_commands(code) {
    var Range = ace.require('ace/range').Range;
    var code_lines = code.split('\n')
    var contains_system_commands = false;

    for(var i=0; i<code_lines.length; ++i) {
        var line = code_lines[i];
        for(cmd of system_commands) {
            var err_index = line.indexOf(cmd);
            if(err_index != -1) {
                contains_system_commands = true;

                if (!highlighted_lines[i]) {
                    var id =editor.session.addMarker(new Range(i, 0, i, 1), "my-marker", "fullLine");
                    highlighted_lines[i] = id;
                    processor_errors[i] = "Line " + (i+1) + " : " + err_index + " Contains " + cmd + " command which is a system command.";   
                }

                // document.getElementById('system-command-error').style.display = 'block';
                break;
            } else {
                editor.session.removeMarker(highlighted_lines[i]);
                highlighted_lines[i] = undefined;
                processor_errors[i] = "";
            }
        }
    }

    return contains_system_commands;
}

function show_processor_errors() {
    processor_output_text_area = document.getElementById("campaign-processor-status");

    for(key in processor_errors) {
        if (processor_errors[key] != "") {
            processor_output_text_area.value += '\n\n' + processor_errors[key];
        }
    }

    processor_output_text_area.style.display = 'block';
}

/* API Editor Functions Ends */

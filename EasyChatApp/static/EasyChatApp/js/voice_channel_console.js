var selected_tts_provider = voice_modulation_details.selected_tts_provider

$(document).ready(function () {
    $('#voice_provider').val(selected_tts_provider).change()
    update_voice_channel_settings(selected_tts_provider, voice_modulation_details)

    $( "#voicebot_caller_id_input_div" ).focus(function() {
        if($('#voicebot_event_caller_id_container').css('display') == 'none') {
            $("#voicebot_event_caller_id_container").show();
            $( "#voicebot_caller_id_dropdown_icon" ).addClass("voicebot-caller-id-dropdown-active")

        } else if ($('#voicebot_event_caller_id_container').css('display') == 'block') {
            $("#voicebot_event_caller_id_container").show();
            $( "#voicebot_caller_id_dropdown_icon" ).addClass("voicebot-caller-id-dropdown-active")
        }
    });

    $("#voicebot_caller_id_dropdown_icon").click(function() {
        if($('#voicebot_event_caller_id_container').css('display') == 'none'){
            $("#voicebot_event_caller_id_container").show();
            $("#voicebot_caller_id_dropdown_icon").addClass("voicebot-caller-id-dropdown-active");
        } else if ($('#voicebot_event_caller_id_container').css('display') == 'block'){
            $("#voicebot_event_caller_id_container").hide();
            $( "#voicebot_caller_id_dropdown_icon" ).removeClass("voicebot-caller-id-dropdown-active")
        }
    });

    $(document).mouseup(function(e) {
        const container = $(".easychat-caller-id-dropdown-wrapper");
        if (container.length != 0 && !container.is(e.target) && container.has(e.target).length === 0 ) {
            if ($('#voicebot_event_caller_id_container').css('display') == 'block') {
                $('#voicebot_caller_id_dropdown_icon').trigger('click');
            }
        }
    });

    $(".toggle-password").click(function() {
        $(this).toggleClass("fa-eye fa-eye-slash");
        var input = $($(this).attr("toggle"));
        if (input.attr("type") == "password") {
            input.attr("type", "text");
        } else {
            input.attr("type", "password");
        }
    });

    $(".toggle-password-key").click(function() {
        $(this).toggleClass("fa-eye fa-eye-slash");
        var input = $($(this).attr("toggle"));
        if (input.attr("type") == "password") {
            input.attr("type", "text");
        } else {
            input.attr("type", "password");
        }
    });
});

$(document).on("click", "#save-voice-channel", function (e) {
    let bot_id = url_parameters = get_url_vars()["id"];
    let welcome_message = $("#welcome-message").trumbowyg('html')
    let failure_message = $("#failure-message").trumbowyg('html')
    let authentication_message = $("#authentication-message").trumbowyg('html')

    let voice_provider = $('#voice_provider').val()
    let voice_language = $('#voice_channel_language').val()
    let voice_type = $('#voice_type').val()
    let voice_name = $('#voice_name').val()
    let speaking_speed = $('#speaking_speed_slider').data("ionRangeSlider").result.from
    let speaking_pitch = $('#pitch_value_slider').data("ionRangeSlider").result.from
    let asr_provider = $('#voice_asr_provider').val()

    var api_key = document.getElementById("api-key-field").value.trim();
    var api_token = document.getElementById("api-token-field").value.trim();
    var api_subdomain = document.getElementById("voice_bot_subdomain_select").value.trim();
    var api_sid = document.getElementById("account_sid").value.trim();

    var silence_threshold_count = document.getElementById("silence_threshold_count").value;

    var silence_response = document.getElementById("silence_response").value.trim();
    if (silence_response == ""){
        M.toast({
            "html": "Silence Follow Up response cannot be empty."
        }, 2000);
        return;
    }

    var silence_termination_response = document.getElementById("silence_termination_response").value.trim();
    if (silence_termination_response == ""){
        M.toast({
            "html": "Silence termination response cannot be empty."
        }, 2000);
        return;
    }

    var loop_threshold_count = document.getElementById("loop_threshold_count").value;

    var is_agent_handover = document.getElementById("enable_agent_handover").checked;

    var loop_termination_response = document.getElementById("loop_termination_response").value.trim();
    if (loop_termination_response == ""){
        M.toast({
            "html": "Loop termination response cannot be empty."
        }, 2000);
        return;
    }

    var loop_handover_response = document.getElementById("loop_handover_response").value.trim();
    if (loop_handover_response == ""){
        M.toast({
            "html": "Loop handover response cannot be empty."
        }, 2000);
        return;
    }

    var validation_message = check_channel_messages_validation(welcome_message, failure_message, authentication_message);
    if (validation_message != "No Error") {
        M.toast({
            "html": validation_message
        }, 2000);
        return;
    }

    if (
        speaking_speed > $('#speaking_speed_slider').data("ionRangeSlider").result.max ||
        speaking_speed < $('#speaking_speed_slider').data("ionRangeSlider").result.min
    ) {
        M.toast({
            "html": "Please enter a valid Speaking Speed Value!"
        }, 2000);
        return;
    }
    if (
        speaking_pitch > $('#pitch_value_slider').data("ionRangeSlider").result.max ||
        speaking_pitch < $('#pitch_value_slider').data("ionRangeSlider").result.min
    ) {
        M.toast({
            "html": "Please enter a valid Pitch Value!"
        }, 2000);
        return;
    }

    var languages_supported = "";
    var language_checkboxes = document.querySelectorAll("#language-box-options-container .option .item-checkbox");
    for (var i=0; i<language_checkboxes.length; i++) {
        if (language_checkboxes[i].checked) {
            languages_supported += language_checkboxes[i].value + ",";
        }
    }

    if (languages_supported == ""){
        M.toast({
            "html": "Please select atleast one language."
        }, 2000);
        return;
    }

    var fallback_response = document.getElementById("fallback_response").value.trim();
    if (fallback_response == ""){
        M.toast({
            "html": "Fallback response cannot be empty."
        }, 2000);
        return;
    }

    json_string = JSON.stringify({
        bot_id: bot_id,
        welcome_message: welcome_message,
        failure_message: failure_message,
        authentication_message: authentication_message,
        api_key: api_key,
        api_token: api_token,
        api_subdomain: api_subdomain,
        api_sid: api_sid,
        selected_tts_provider: voice_provider,
        tts_language: voice_language,
        tts_speaking_style: voice_type,
        tts_voice: voice_name,
        tts_speaking_speed: speaking_speed,
        tts_pitch: speaking_pitch,
        asr_provider: asr_provider,
        silence_threshold_count: silence_threshold_count,
        silence_response: silence_response,
        silence_termination_response: silence_termination_response,
        loop_threshold_count: loop_threshold_count,
        is_agent_handover: is_agent_handover,
        loop_termination_response: loop_termination_response,
        loop_handover_response: loop_handover_response,
        languages_supported: languages_supported,
        fallback_response: fallback_response
    });
    json_string = EncryptVariable(json_string)
    $.ajax({
        url: "/chat/channels/voice/save/",
        type: "POST",
        data: {
            json_string: json_string
        },
        headers: {
            "X-CSRFToken": get_csrf_token()
        },
        success: function (response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                M.toast({
                    "html": "Channel details saved successfully."
                })
                window.location = window.location.href;
            } else if (response["status"] == 402) {
                M.toast({
                    "html": response["message"]
                }, 2000)
                setTimeout(function() {
                    window.location.href = "/chat/home"
                }, 2000)
            } else {
                M.toast({
                    "html": response["message"]
                }, 2000)
            }
        },
        error: function (error) {
            console.log("Report this error: ", error);
        }
    });
});

$("#pitch_value_slider").ionRangeSlider({
    min: 0,
    max: 3,
    step: 0.01,
    from: 0.2
});

$("#speaking_speed_slider").ionRangeSlider({
    min: 0,
    max: 2,
    step: 0.01,
    from: 0.2
});

let voice_name_mapping = {
    'Microsoft': ['NeerjaNeural', 'PrabhatNeural'],
    'Google': [['Standard-A', 'Standard-B', 'Standard-C', 'Standard-D'], ['Wavenet-A', 'Wavenet-B', 'Wavenet-C', 'Wavenet-D']],
    'AwsPolly': ['Aditi', 'Raveena'],
};

let voice_type_mapping = {
    'Microsoft': ['general'],
    'Google': ['basic', 'wavenet'],
    'AwsPolly': ['standard'],
};

let slider_values_mapping = {
    'Microsoft': { 'speaking_speed': [0, 3], 'pitch': [0, 2] },
    'Google': { 'speaking_speed': [0, 4], 'pitch': [-20, 20] },
    'AwsPolly': { 'speaking_speed': [20, 200], 'pitch': [-20, 20] },
};

// When an option is changed, search the above for matching choices
$('#voice_provider').on('change', function () {
    // Set selected option as variable
    let selectValue = $(this).val();

    // Empty the target field
    $('#voice_name').empty();
    $('#voice_type').empty();

    for (i = 0; i < voice_type_mapping[selectValue].length; i++) {
        // Output choice in the target field
        $('#voice_type').append("<option value='" + voice_type_mapping[selectValue][i] + "'>" + voice_type_mapping[selectValue][i] + "</option>");
    }

    // For each chocie in the selected option
    let temp_name_mapping = voice_name_mapping[selectValue]
    if (selectValue == 'Google') {
        if ($('#voice_type').val() == 'basic') {
            temp_name_mapping = temp_name_mapping[0]
        } else if ($('#voice_type').val() == 'wavenet') {
            temp_name_mapping = temp_name_mapping[1]
        }
    }
    let display_name;
    for (i = 0; i < temp_name_mapping.length; i++) {
        display_name = temp_name_mapping[i]
        // Output choice in the target field
        if(selectValue == 'Microsoft') {
            if(temp_name_mapping[i] == 'PrabhatNeural') display_name = 'Prabhat (Neural)' 
            else if(temp_name_mapping[i] == 'NeerjaNeural') display_name = 'Neerja (Neural)' 
        }
        $('#voice_name').append("<option value='" + temp_name_mapping[i] + "'>" + display_name + "</option>");
    }

    update_voice_channel_settings(selectValue, voice_modulation_details)
});

$('#voice_type').change(function () {
    let selectValue = $('#voice_provider').val();
    let temp_name_mapping = voice_name_mapping[selectValue]
    if (selectValue == 'Google') {
        if ($('#voice_type').val() == 'basic') {
            temp_name_mapping = temp_name_mapping[0]
        } else if ($('#voice_type').val() == 'wavenet') {
            temp_name_mapping = temp_name_mapping[1]
        }
        $('#voice_name').empty();
        for (i = 0; i < temp_name_mapping.length; i++) {
            // Output choice in the target field
            $('#voice_name').append("<option value='" + temp_name_mapping[i] + "'>" + temp_name_mapping[i] + "</option>");
        }
    }
})

$('#speaking_speed_slider').change(function () {
    $('#speaking_speed_value').val($('#speaking_speed_slider').data("ionRangeSlider").result.from)
})

$('#pitch_value_slider').change(function () {
    $('#pitch_value').val($('#pitch_value_slider').data("ionRangeSlider").result.from)
})

$('#speaking_speed_value').blur(function () {
    update_slider_values(this, 'speaking_speed_slider')
})

$('#pitch_value').blur(function () {
    update_slider_values(this, 'pitch_value_slider')
})

$('#speaking_speed_value, #pitch_value').keydown(function (e) {
    let key = e.keyCode || e.charCode;
    if (key == 13) {
        $(this).blur();  // Loses focus from field when enter is pressed
    }
})

function update_slider_values(el, slider_name) {
    let current_value = $(el).val()
    let updated_value = (current_value.indexOf(".") >= 0) ? (current_value.substr(0, current_value.indexOf(".")) + current_value.substr(current_value.indexOf("."), 3)) : current_value;
    let slider_max_val = $('#' + slider_name).data("ionRangeSlider").result.max
    let slider_min_val = $('#' + slider_name).data("ionRangeSlider").result.min
    if (updated_value > slider_max_val) updated_value = slider_max_val
    if (updated_value < slider_min_val) updated_value = slider_min_val
    $(el).val(updated_value)
    $('#' + slider_name).data("ionRangeSlider").update({ from: $(el).val() });
}

function update_voice_channel_settings(provider, voice_modulation_details) {
    $('#speaking_speed_slider').data("ionRangeSlider").update({ from: voice_modulation_details[provider].tts_speaking_speed, min: slider_values_mapping[provider]['speaking_speed'][0], max: slider_values_mapping[provider]['speaking_speed'][1] });
    $('#pitch_value_slider').data("ionRangeSlider").update({ from: voice_modulation_details[provider].tts_pitch, min: slider_values_mapping[provider]['pitch'][0], max: slider_values_mapping[provider]['pitch'][1] });
    $('#voice_channel_language').val(voice_modulation_details[provider].tts_language).change()
    $('#voice_type').val(voice_modulation_details[provider].tts_speaking_style).change()
    $('#voice_name').val(voice_modulation_details[provider].tts_voice).change()
    $('#voice_asr_provider').val(voice_modulation_details[provider].asr_provider).change()
    $('#speaking_speed_slider, #pitch_value_slider').change()
    setTimeout(function () {
        $('.select2-selection__rendered').removeAttr('title')
    }, 500)
}

$('#reset_voice_modulation').click(function() {
    update_voice_channel_settings($('#voice_provider').val(), default_voice_modulation)
})

function change_loop_response_wrapper() {
    if (document.getElementById("disable_agent_handover").checked) {
        document.getElementById("loop_termination_wrapper").style.display = "table-row";
        document.getElementById("loop_handover_wrapper").style.display = "none";
    } else {
        document.getElementById("loop_handover_wrapper").style.display = "table-row";
        document.getElementById("loop_termination_wrapper").style.display = "none";
    }
}


$( "#voicebot_variation_input_div" ).focus(function() {
    
    if ($('#voicebot_event_variation_container').css('display') == 'none') {
       $("#voicebot_event_variation_container").show();
       $( "#voicebot_variation_dropdown_icon" ).addClass("voicebot-variation-dropdown-active")
  
    } else if ($('#voicebot_event_variation_container').css('display') == 'block') {
      $("#voicebot_event_variation_container").show();
      $( "#voicebot_variation_dropdown_icon" ).addClass("voicebot-variation-dropdown-active")  
    }
});
  
$( "#voicebot_variation_dropdown_icon" ).click(function() {

    if ($('#voicebot_event_variation_container').css('display') == 'none') {
       $("#voicebot_event_variation_container").show();
       $( "#voicebot_variation_dropdown_icon" ).addClass("voicebot-variation-dropdown-active")

    } else if ($('#voicebot_event_variation_container').css('display') == 'block') {
      $("#voicebot_event_variation_container").hide();
      $( "#voicebot_variation_dropdown_icon" ).removeClass("voicebot-variation-dropdown-active")
    }
});

$(document).mouseup(function(e) {
    const container = $(".easychat-add-variation-dropdown-wrapper");

    if (container.length != 0 && !container.is(e.target) && container.has(e.target).length === 0 ) {
    
        if ($('#voicebot_event_variation_container').css('display') == 'block') {
            $('#voicebot_variation_dropdown_icon').trigger('click');
        }
    }
});


function update_repeat_variations(e) {
    if (e.keyCode == 13) {
        var input_variation = document.getElementById("voicebot_variation_input_div").value.trim();
        if (input_variation) {
            if (!repeat_variations_list.includes(input_variation.toLowerCase())) {
                add_repeat_variation(input_variation);
            } else {
                M.toast({
                    "html": "Variation already exists."
                }, 2000);
                document.getElementById("voicebot_variation_input_div").value = "";
                return;
            }
        } else {
            M.toast({
                "html": "Please enter valid variation."
            }, 2000);
            document.getElementById("voicebot_variation_input_div").value = "";
            return;
        }
    }
}

document.getElementById("voicebot_variation_input_div").onkeyup = update_repeat_variations;


function add_repeat_variation(repeat_variation) {
    var bot_id = get_url_vars()["id"];

    json_string = JSON.stringify({
        bot_id: bot_id,
        repeat_variation: repeat_variation
    })

    json_string = EncryptVariable(json_string);

    $.ajax({
        url: "/chat/channels/voice/add-repeat-variation/",
        type: "POST",
        data: {
            json_string: json_string
        },
        headers: {
            "X-CSRFToken": get_csrf_token()
        },
        success: function (response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {

                var variations_list = document.getElementById("voicebot_event_variation_container");
                var html = '<li class="voicebot-variation-item" id="repeat_variation_' + repeat_variations_count + '">\
                    <div class="voicebot-variation-item-text">' + repeat_variation + '</div>\
                    <a class="modal-trigger" onclick="open_delete_variations_model(' + repeat_variations_count + ')">\
                    <svg width="19" height="19" viewBox="0 0 19 19" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path d="M11.0166 8.38202L10.7916 13.632M8.2416 13.632L8.0166 8.38202M5.0166 5.38202L5.64214 14.7651C5.71218 15.8157 6.58478 16.632 7.63771 16.632H11.3955C12.4484 16.632 13.321 15.8157 13.3911 14.7651L14.0166 5.38202M5.0166 5.38202H7.2666M5.0166 5.38202H3.5166M14.0166 5.38202H15.5166M14.0166 5.38202H11.7666M11.7666 5.38202V5.13202C11.7666 4.02745 10.8712 3.13202 9.7666 3.13202H9.2666C8.16203 3.13202 7.2666 4.02745 7.2666 5.13202V5.38202M11.7666 5.38202H7.2666" stroke="#FF281A" stroke-width="1.38624" stroke-linecap="round" stroke-linejoin="round"/>\
                    </svg>\
                    </a>\
                </li>';

                variations_list.insertAdjacentHTML("afterbegin", html);
                document.getElementById("voicebot_variation_input_div").value = "";
                repeat_variations_list.push(repeat_variation.toLowerCase());
                variations_list.scrollTo(0, 0);

                repeat_variations_count += 1;

                M.toast({
                    "html": response["message"]
                }, 2000)
                
            } else {
                M.toast({
                    "html": response["message"]
                }, 2000)
            }
        },
        error: function (error) {
            console.log("Report this error: ", error);
        }
    });
}


function delete_repeat_variation(variation_number) {

    var repeat_variation = document.getElementById("repeat_variation_" + variation_number).getElementsByClassName("voicebot-variation-item-text")[0].innerText.trim();

    var bot_id = get_url_vars()["id"];

    json_string = JSON.stringify({
        bot_id: bot_id,
        repeat_variation: repeat_variation
    })

    json_string = EncryptVariable(json_string);

    $.ajax({
        url: "/chat/channels/voice/delete-repeat-variation/",
        type: "POST",
        data: {
            json_string: json_string
        },
        headers: {
            "X-CSRFToken": get_csrf_token()
        },
        success: function (response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                document.getElementById("repeat_variation_" + variation_number).remove();
                $('#easychat_voicebot_variation_delete_modal').modal('close');

                const index = repeat_variations_list.indexOf(repeat_variation.toLowerCase());
                if (index > -1) {
                    repeat_variations_list.splice(index, 1);
                }

                M.toast({
                    "html": response["message"]
                }, 2000)
            } else {
                M.toast({
                    "html": response["message"]
                }, 2000)
            }
        },
        error: function (error) {
            console.log("Report this error: ", error);
        }
    });
}

function open_delete_variations_model(variation_number) {
    document.getElementById("delete-variation").setAttribute("onclick", "delete_repeat_variation('" + variation_number +"')");
    $('#easychat_voicebot_variation_delete_modal').modal('open');
}


$("#language-box-options-container .option label").click(function (e){
    e.target.parentElement.querySelector('[type="checkbox"]').checked = !e.target.parentElement.querySelector('[type="checkbox"]').checked;
})


function save_voice_caller(){
    remove_add_caller_modal_errors();
    var bot_id = get_url_vars()["id"];
    var caller_id = document.getElementById("add_call_id").value.trim();

    if (caller_id == "" || caller_id.length != 10 || isNaN(caller_id)){
        document.getElementById("add_call_id").classList.add("error_msg");
        document.getElementById("caller-id-err").innerText = "Please enter valid 10 digit caller id.";
        document.getElementById("caller-id-err").style.display = "block";
        return;
    }

    var app_id = document.getElementById("add_app_id").value.trim();

    if (app_id == "" || app_id.length != 4 || isNaN(app_id)){
        document.getElementById("add_app_id").classList.add("error_msg");
        document.getElementById("app-id-err").innerText = "Please enter valid 4 digit app id.";
        document.getElementById("app-id-err").style.display = "block";
        return;
    }

    json_string = JSON.stringify({
        bot_id: bot_id,
        caller_id: caller_id,
        app_id: app_id
    })

    json_string = EncryptVariable(json_string);

    $.ajax({
        url: "/chat/channels/voice/add-caller/",
        type: "POST",
        data: {
            json_string: json_string
        },
        headers: {
            "X-CSRFToken": get_csrf_token()
        },
        success: function (response) {
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                var caller_ids_container = document.getElementById("voicebot_event_caller_id_container");
                var html = `<li class="voicebot-caller-id-item" search-value="` + response["caller_id"] + "|" + response["app_id"] + `" id="voice_bot_caller_id_` + response["voice_bot_caller_id"] + `">
                    <div class="voicebot-caller-id-item-text call_id_num">` + response["caller_id"] + `</div>
                    <div class="voicebot-caller-id-item-text app_id">App ID: ` + response["app_id"] + `</div>
                    <a class="modal-trigger voicebot-caller-id-cross-icon" onclick="open_delete_caller_modal('` + response["voice_bot_caller_id"] + `')">
                        <svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M3.40088 3.05899L12.2881 12.3006" stroke="#FF281A" stroke-width="1.54026" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M12.2881 3.05899L3.4009 12.3006" stroke="#FF281A" stroke-width="1.54026" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>   
                    </a>
                </li>`
                caller_ids_container.insertAdjacentHTML("beforeend", html);
                M.toast({
                    "html": "Added caller successfully"
                }, 2000)
                document.getElementById("add_call_id").value = "";
                document.getElementById("add_app_id").value = "";
                document.getElementById("save_call_id").setAttribute("disabled", "");
                $('#add_caller_id').modal("close");

            } else if (response["status"] == 501) {
                document.getElementById("add_call_id").classList.add("error_msg");
                document.getElementById("add_app_id").classList.add("error_msg");
                document.getElementById("caller-app-err").innerText = "The Caller ID and App ID already exist in the list, please enter new values.";
                document.getElementById("caller-app-err").style.display = "block";

            } else if (response["status"] == 502) {
                document.getElementById("add_call_id").classList.add("error_msg");
                document.getElementById("caller-id-err").innerText = "The Caller ID already exist in the list, please enter new values.";
                document.getElementById("caller-id-err").style.display = "block";

            } else if (response["status"] == 503) {
                document.getElementById("add_app_id").classList.add("error_msg");
                document.getElementById("app-id-err").innerText = "The App ID already exist in the list, please enter new values.";
                document.getElementById("app-id-err").style.display = "block";

            } else {
                M.toast({
                    "html": response["message"]
                }, 2000)
            }
        },
        error: function (error) {
            console.log("Report this error: ", error);
        }
    });
}


function close_add_voice_caller_modal() {
    document.getElementById("add_call_id").value = "";
    document.getElementById("add_app_id").value = "";
    document.getElementById("save_call_id").setAttribute("disabled", "");
    remove_add_caller_modal_errors();
}


function delete_voice_caller(voice_bot_caller_id){
    var bot_id = get_url_vars()["id"];

    json_string = JSON.stringify({
        bot_id: bot_id,
        voice_bot_caller_id: voice_bot_caller_id
    })

    json_string = EncryptVariable(json_string);

    $.ajax({
        url: "/chat/channels/voice/delete-caller/",
        type: "POST",
        data: {
            json_string: json_string
        },
        headers: {
            "X-CSRFToken": get_csrf_token()
        },
        success: function (response) {
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                document.getElementById("voice_bot_caller_id_" + voice_bot_caller_id).remove();
                M.toast({
                    "html": "Deleted caller successfully"
                }, 2000)
                $('#easychat_voicebot_call_id_delete_modal').modal("close");
            } else {
                M.toast({
                    "html": response["message"]
                }, 2000)
            }
        },
        error: function (error) {
            console.log("Report this error: ", error);
        }
    });
}


function close_delete_caller_modal() {
    $('#easychat_voicebot_call_id_delete_modal').modal("close");
}


function open_delete_caller_modal(voice_bot_caller_id){
    document.getElementById("delete-caller-button").setAttribute("onclick", "delete_voice_caller('" + voice_bot_caller_id + "')");
    $('#easychat_voicebot_call_id_delete_modal').modal("open");
}


function search_for_callers(event){
    var search_value = document.getElementById("voicebot_caller_id_input_div").value.trim();
    search_value = search_value.replace(/\D/g,'');
    document.getElementById(event.target.id).value = search_value;
    var caller_items = document.getElementsByClassName("voicebot-caller-id-item");
    for (var i=0; i<caller_items.length; i++){
        if (caller_items[i].getAttribute("search-value").includes(search_value)){
            caller_items[i].style.display = "flex";
        } else {
            caller_items[i].style.display = "none";
        }
    }
}

function only_numeric_for_caller_id(event){

    var element = event.target;
    var value = element.value;
    var count = value.length;
    var copy_paste = [65, 67,86, 88];
    
    if((event.ctrlKey && copy_paste.includes(event.keyCode)) || (event.metaKey  && copy_paste.includes(event.keyCode))){
        return;
    }
    if (event.keyCode == 69){
        event.preventDefault();
    }
    if ((event.keyCode >= 48 && event.keyCode <= 57) || (event.keyCode >= 96 && event.keyCode <= 105)) { 
        if(count >= 10){
            event.preventDefault();
        }
    }else if(![8, 37, 39, 107, 109].includes(event.keyCode)){
        event.preventDefault();
    }
    
    
}

function only_numeric_for_app_id(event){

    var element = event.target;
    var value = element.value;
    var count = value.length;
    var copy_paste = [65, 67,86, 88];
    
    if((event.ctrlKey && copy_paste.includes(event.keyCode)) || (event.metaKey  && copy_paste.includes(event.keyCode))){
        return;
    }
    if (event.keyCode == 69){
        event.preventDefault();
    }
    
    if ((event.keyCode >= 48 && event.keyCode <= 57) || (event.keyCode >= 96 && event.keyCode <= 105)) { 
        if(count >= 4){
            event.preventDefault();
        }
    }else if(![8, 37, 39, 107, 109].includes(event.keyCode)){
        event.preventDefault();
    }
    
}

function remove_add_caller_modal_errors() {
    document.getElementById("caller-id-err").style.display = "none";
    document.getElementById("app-id-err").style.display = "none";
    document.getElementById("caller-app-err").style.display = "none";
    document.getElementById("add_call_id").classList.remove("error_msg");
    document.getElementById("add_app_id").classList.remove("error_msg");
}

function is_add_call_details_empty(event) {
    let add_call_id=document.getElementById("add_call_id").value;
    let add_app_id=document.getElementById("add_app_id").value;
    add_app_id = add_app_id.replace(/\D/g,'');
    add_call_id = add_call_id.replace(/\D/g,'');
    document.getElementById("add_call_id").value = add_call_id;
    document.getElementById("add_app_id").value = add_app_id;

    if (add_call_id !=""&& add_app_id !="") {
        document.getElementById("save_call_id").removeAttribute("disabled");
    } else {
        document.getElementById("save_call_id").setAttribute("disabled", "");
    }
}

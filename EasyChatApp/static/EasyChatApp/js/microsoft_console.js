add_channel_language_selction_event("microsoft-teams")
add_language_dropdown_search_event()
language_dropdown_close_onclicking_outside_event()
language_search_dropdown_event()
open_close_language_dropdown_event()
$(document).ready(function () {
    create_language_custom_dropdowns();
});
$(document).on("click", "#ignore-changes-in-non-primary-language", function (e) {
    let bot_id = (get_url_vars()["id"])
    let channel_name = "Microsoft"
    ignore_changes_in_non_primary_languages(bot_id, channel_name)
});
$(document).on("click", "#auto-fix-changes-in-non-primary-language", function (e) {
    let bot_id = (get_url_vars()["id"])
    let channel_name = "Microsoft"
    auto_fix_changes_in_non_primary_languages(bot_id, channel_name)
});

$(document).on("click", "#save-ms-teams-channel", function(e) {
    var location_href = window.location.href;
    var location_href = location_href.replace("#", "");
    var location_href = location_href.replace("!", "");
    var bot_id = get_url_vars()['id'];
    // var welcome_message = $('#welcome-message').val();
    // var failure_message = $('#failure-message').val();
    // var authentication_message = $("#authentication-message").val();
    var welcome_message = $("#welcome-message").trumbowyg('html')
    var failure_message = $("#failure-message").trumbowyg('html')
    var authentication_message = $("#authentication-message").trumbowyg('html')

    var is_language_auto_detection_enabled = document.getElementById("is_language_auto_detection_enabled").checked
    var is_enable_choose_language_flow_enabled_for_welcome_response = document.getElementById("is_enable_choose_language_flow_enabled_for_welcome_response").checked

    selected_supported_languages = get_selected_languages_list()

    if ("en" in selected_supported_languages == false) {
        selected_supported_languages.push("en");
    }

    var validation_message = check_channel_messages_validation(welcome_message, failure_message, authentication_message);
    if (validation_message != "No Error") {
        M.toast({
            "html": validation_message
        }, 2000);
        return;
    }

    ms_team_app_code = document.getElementById("ms_team_app_code").value;
    if (ms_team_app_code == '') {
        M.toast({
            "html": "App Code cannot be empty!"
        }, 2000);
        return;
    }

    ms_team_app_password = document.getElementById("ms_team_app_password").value;
    if (ms_team_app_password == '') {
        M.toast({
            "html": "App Password cannot be empty!"
        }, 2000);
        return;
    }

    json_string = JSON.stringify({
        bot_id: bot_id,
        welcome_message: welcome_message,
        failure_message: failure_message,
        authentication_message: authentication_message,
        ms_team_app_password: ms_team_app_password,
        ms_team_app_code: ms_team_app_code,
        selected_supported_languages: selected_supported_languages,
        is_enable_choose_language_flow_enabled_for_welcome_response: is_enable_choose_language_flow_enabled_for_welcome_response,
        is_language_auto_detection_enabled: is_language_auto_detection_enabled,
    });
    json_string = EncryptVariable(json_string)
    document.getElementById("easychat_ms_teams_channel_preloader").style.display = "block";
    $.ajax({
        url: "/chat/channels/microsoft-teams/save/",
        type: "POST",
        data: {
            json_string: json_string
        },
        headers: {
            "X-CSRFToken": get_csrf_token()
        },
        success: function(response) {
            document.getElementById("easychat_ms_teams_channel_preloader").style.display = "none";
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                M.toast({
                    "html": "Channel details updated successfully."
                })
                window.location = window.location.href;
            } else if (response["status"] == 400) {
                M.toast({
                    "html": response["message"]
                }, 2000)
            } else if (response["status"] == 402) {
                M.toast({
                    "html": response["message"]
                }, 2000)
                setTimeout(function() {
                    window.location.href = "/chat/home"
                }, 2000)
            } else {
                M.toast({
                    "html": "Unable to process your request. Please try again after some time"
                })
            }
        },
        error: function(error) {
            document.getElementById("easychat_ms_teams_channel_preloader").style.display = "none";
            console.log("Report this error: ", error);
        }
    });
});

$("#language-box-options-container .option .item-checkbox").change(function () {

    enable_disable_auto_language_detection_toogle();
    enable_disable_welcome_message_language_change_toogle()

});

$(document).on("click", "#save-ms-teams-channel-for-non-primary-language", function (e) {
    let bot_id = (get_url_vars()["id"])
    let selected_language = get_url_vars()['selected_lang']

    var welcome_message = $("#welcome-message").trumbowyg('html');
    var failure_message = $("#failure-message").trumbowyg('html')
    var authentication_message = $("#authentication-message").trumbowyg('html')

    var validation_message = check_channel_messages_validation(welcome_message, failure_message, authentication_message);

    if (validation_message != "No Error") {
        M.toast({
            "html": validation_message
        }, 2000);
        return;
    }
    channel_name = "Microsoft"

    json_string = {
        bot_id: bot_id,
        welcome_message: welcome_message,
        failure_message: failure_message,
        channel_name: channel_name,
        selected_language: selected_language,
        authentication_message: authentication_message,
        save_auto_pop_up_text: false,
    }
    json_string = JSON.stringify(json_string);
    json_string = EncryptVariable(json_string);
    document.getElementById("easychat_ms_teams_channel_preloader").style.display = "block";
    $.ajax({
        url: "/chat/save-channel-language-tuned-objects/",
        type: "POST",
        data: {
            json_string: json_string
        },
        success: function (response) {
            document.getElementById("easychat_ms_teams_channel_preloader").style.display = "none";
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                M.toast({
                    "html": "Channel details updated successfully."
                })
                window.location = window.location.href;
            } else if (response["status"] == 400) {
                M.toast({
                    "html": response["message"]
                }, 2000)
            } else {
                M.toast({
                    "html": "Internal Server Error. Please report this error"
                })
            }
        },
        error: function (error) {
            document.getElementById("easychat_web_channel_preloader").style.display = "none";
            console.log("Report this error: ", error);
        },
    });
});

function ms_teams_download_config_file(){
    var location_href = window.location.href;
    var location_href = location_href.replace("#", "");
    var location_href = location_href.replace("!", "");
    var bot_id = location_href.split("?")[1].split("=")[1];

    let json_string = JSON.stringify({
        bot_id: bot_id,
    });

    json_string = EncryptVariable(json_string)
    $.ajax({
        url: "/chat/channels/ms-teams/download-config/",
        type: "POST",
        data: {
            json_string: json_string
        },
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                console.log(response);
                config_file_path = response["config_file_path"];

                const url = window.location.origin + config_file_path;
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;

                a.download = 'config.json';
                document.body.appendChild(a);
                a.click();
            } else {
                M.toast({
                    "html": "Unable to process your request. Please try again after some time"
                })
            }
        },
        error: function(error) {
            console.log("Report this error: ", error);
        }
    });
}

function html_tags_remover(text) {

    return text.replace(/<\/?[^>]+(>|$)/g, "").trim();
}
add_channel_language_selction_event("twitter")
add_language_dropdown_search_event()
language_dropdown_close_onclicking_outside_event()
language_search_dropdown_event()
open_close_language_dropdown_event()
$(document).ready(function () {
    create_language_custom_dropdowns();
});
$(document).on("click", "#ignore-changes-in-non-primary-language", function (e) {
    let bot_id = (get_url_vars()["id"])
    let channel_name = "Telegram"
    ignore_changes_in_non_primary_languages(bot_id, channel_name)
});
$(document).on("click", "#auto-fix-changes-in-non-primary-language", function (e) {
    let bot_id = (get_url_vars()["id"])
    let channel_name = "Telegram"
    auto_fix_changes_in_non_primary_languages(bot_id, channel_name)
});
$(document).on("click", "#save-twitter-channel", function(e) {
    var location_href = window.location.href;
    var location_href = location_href.replace("#", "");
    var location_href = location_href.replace("!", "");
    var bot_id = get_url_vars()['id'];

    var welcome_message = $("#welcome-message").trumbowyg('html');
    var failure_message = $("#failure-message").trumbowyg('html');
    var authentication_message = $("#authentication-message").trumbowyg('html');

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

    failure_recommendation_list = $("#multiple-select-twitter-failure-message-list").val();

    let image_id = document.getElementById("uploaded-bot-welcome-image");
    let image_url = image_id.getAttribute("src");
    let video_url = document.getElementById("upload-bot-welcome-video-url").value.trim();

    var selected_supported_languages = get_selected_languages_list()
    if (!selected_supported_languages.includes("en")) {
        selected_supported_languages.push("en");
    }

    if (isValidURL(video_url) == false && video_url != "") {
        M.toast({
            "html": "Please enter valid video url"
        }, 2000);
        return;
    }

    let twitter_app_id = document.getElementById("twitter_app_id").value.trim();
    let twitter_api_key = document.getElementById("twitter_api_key").value.trim();
    let twitter_key_api_secret = document.getElementById("twitter_key_api_secret").value.trim();
    let twitter_access_token = document.getElementById("twitter_access_token").value.trim();
    let twitter_access_token_secret = document.getElementById("twitter_access_token_secret").value.trim();
    let twitter_bearer_token = document.getElementById("twitter_bearer_token").value.trim();
    let twitter_dev_env_label = document.getElementById("twitter_dev_env_label").value.trim();

    if(twitter_app_id == "") {
        M.toast({
            "html": "Please enter valid App ID"
        }, 2000);
        return;
    }

    if(twitter_api_key == "") {
        M.toast({
            "html": "Please enter valid API key"
        }, 2000);
        return;
    }

    if(twitter_key_api_secret == "") {
        M.toast({
            "html": "Please enter valid API key secret"
        }, 2000);
        return;
    }

    if(twitter_access_token == "") {
       M.toast({
            "html": "Please enter valid access token"
        }, 2000);
        return; 
    }

    if(twitter_access_token_secret == "") {
        M.toast({
            "html": "Please enter valid access token secret"
        }, 2000);
        return;
    }

    if(twitter_bearer_token == "") {
        M.toast({
            "html": "Please enter valid bearer token"
        }, 2000);
        return;
    }

    if(twitter_dev_env_label == "") {
       M.toast({
            "html": "Please enter valid dev environment label"
        }, 2000);
        return; 
    }

    let json_string = JSON.stringify({
        bot_id: bot_id,
        welcome_message: welcome_message,
        failure_message: failure_message,
        authentication_message: authentication_message,
        image_url: image_url,
        video_url: video_url,
        failure_recommendation_list: failure_recommendation_list,
        selected_supported_languages: selected_supported_languages,
        twitter_app_id: twitter_app_id,
        twitter_api_key: twitter_api_key,
        twitter_key_api_secret: twitter_key_api_secret,
        twitter_access_token: twitter_access_token,
        twitter_access_token_secret: twitter_access_token_secret,
        twitter_bearer_token: twitter_bearer_token,
        twitter_dev_env_label: twitter_dev_env_label,
        selected_supported_languages: selected_supported_languages,
        is_enable_choose_language_flow_enabled_for_welcome_response: is_enable_choose_language_flow_enabled_for_welcome_response,
        is_language_auto_detection_enabled: is_language_auto_detection_enabled,
    });
    json_string = EncryptVariable(json_string)
    $.ajax({
        url: "/chat/channels/twitter/save/",
        type: "POST",
        data: {
            json_string: json_string
        },
        headers: {
            "X-CSRFToken": get_csrf_token()
        },
        success: function(response) {
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
            console.log("Report this error: ", error);
        }
    });
});

$("#language-box-options-container .option .item-checkbox").change(function () {

    enable_disable_auto_language_detection_toogle();
    enable_disable_welcome_message_language_change_toogle()

});

$(document).on("click", "#save-twitter-channel-for-non-primary-language", function (e) {
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
    channel_name = "Twitter"

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
    $.ajax({
        url: "/chat/save-channel-language-tuned-objects/",
        type: "POST",
        data: {
            json_string: json_string
        },
        success: function (response) {
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
            console.log("Report this error: ", error);
        },
    });
});

function twitter_subscribe_webhook(){
    var location_href = window.location.href;
    var location_href = location_href.replace("#", "");
    var location_href = location_href.replace("!", "");
    var bot_id = location_href.split("?")[1].split("=")[1];

    let json_string = JSON.stringify({
        bot_id: bot_id,
    });

    json_string = EncryptVariable(json_string)
    $.ajax({
        url: "/chat/channels/twitter/subscribe-webhook/",
        type: "POST",
        data: {
            json_string: json_string
        },
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                setTimeout(function(){
                    window.location = window.location.href;
                }, 6000);
                M.toast({
                    "html": response["message"]
                }, 2000);
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

function twitter_delete_webhook(){
    var location_href = window.location.href;
    var location_href = location_href.replace("#", "");
    var location_href = location_href.replace("!", "");
    var bot_id = location_href.split("?")[1].split("=")[1];

    let json_string = JSON.stringify({
        bot_id: bot_id,
    });

    json_string = EncryptVariable(json_string)
    $.ajax({
        url: "/chat/channels/twitter/delete-webhook/",
        type: "POST",
        data: {
            json_string: json_string
        },
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                M.toast({
                    "html": response["message"]
                }, 2000);
                window.location = window.location.href;
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

function twitter_reset_config(){
    var location_href = window.location.href;
    var location_href = location_href.replace("#", "");
    var location_href = location_href.replace("!", "");
    var bot_id = location_href.split("?")[1].split("=")[1];

    let json_string = JSON.stringify({
        bot_id: bot_id,
    });

    json_string = EncryptVariable(json_string)
    $.ajax({
        url: "/chat/channels/twitter/reset-config/",
        type: "POST",
        data: {
            json_string: json_string
        },
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                setTimeout(function(){
                    window.location = window.location.href;
                }, 4000);
                M.toast({
                    "html": "Twitter configuration has been reset successfully",
                }, 2000);
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
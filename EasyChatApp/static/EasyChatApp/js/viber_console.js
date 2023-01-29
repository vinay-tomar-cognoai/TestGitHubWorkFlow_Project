if (window.location.pathname.indexOf("/chat/channels/viber") != -1) {
    add_channel_language_selction_event("viber")
    add_language_dropdown_search_event()
    language_dropdown_close_onclicking_outside_event()
    language_search_dropdown_event()
    open_close_language_dropdown_event()
    var upload_file_limit_size = 5120000
    var viber_uploaded_welcome_image_src = ""
    $(document).on("click", "#upload-viber-sender-logo", function(e) {
        e.preventDefault();
        var input_upload_image = ($("#input_upload_viber_sender_logo"))[0].files[0]

        if (input_upload_image == null || input_upload_image == undefined) {
            M.toast({
                "html": "Please select a file."
            }, 2000);

            setTimeout(function() {
                $('#modal-sender-logo').modal('open');
            }, 200);
            return false;
        }
        if (input_upload_image.name.match(/.+\.(jpg|jpeg|png|gif)$/i) == null) {
            M.toast({
                "html": "File format is not supported"
            }, 2000);
            setTimeout(function() {
                $('#modal-sender-logo').modal('open');
            }, 200);
            return false;
        }
        if (input_upload_image.size > upload_file_limit_size) {
            M.toast({
                "html": "Size limit exceed(should be less than 5 MB)."
            }, 2000);

            setTimeout(function() {
                $('#modal-sender-logo').modal('open');
            }, 200);
            return;
        }

        if (check_malicious_file(input_upload_image.name) == true) {
            setTimeout(function() {
                $('#modal-sender-logo').modal('open');
            }, 200);
            return false;
        }

        document.getElementById("uploaded-bot-viber-bot-logo-image").style.display = "none";
        
        $("#remove-viber-sender-logo").hide()

        var reader = new FileReader();
        reader.readAsDataURL(input_upload_image);
        reader.onload = function() {

            base64_str = reader.result.split(",")[1];

            uploaded_file = [];
            uploaded_file.push({
                "filename": input_upload_image.name,
                "base64_file": base64_str,
            });

            upload_welcome_image_for_viber();
        };
        reader.onerror = function(error) {
            console.log('Error: ', error);
        };
    });

    async function upload_welcome_image_for_viber() {
        var response = await upload_image();
        if (response && response.status == 200) {
            src = response.src;
            viber_uploaded_welcome_image_src = src
            compressed_src = response["compressed_image_path"]
            document.getElementById("uploaded-bot-viber-bot-logo-image").src = src;
            document.getElementById("uploaded-bot-viber-bot-logo-image").dataset.compressed_src = compressed_src;
            document.getElementById("uploaded-bot-viber-bot-logo-image").style.display = "inline-block";
            document.getElementById('input_upload_viber_sender_logo2').value = "";
            document.getElementById('modal-sender-logo').style.display = "none";
            $("#remove-viber-sender-logo").show();
        }
    }

    $(document).on("click", "#remove-viber-sender-logo", function(e) {
        document.getElementById("uploaded-bot-viber-bot-logo-image").src = "";
        viber_uploaded_welcome_image_src = ""
        document.getElementById("uploaded-bot-viber-bot-logo-image").style.display = "none";
        document.getElementById('modal-sender-logo').style.display = "";
        $("#remove-viber-sender-logo").hide();
        
    });
    window.onload = function(){
        $('#ms-list-1 input').change(()=>{
            $('#initial_questions_container').html('')
            if ($('#ms-list-1 input:checked').length < 1){
                document.getElementById("initial_questions_container").style.display = "none";
            }else{
                document.getElementById("initial_questions_container").style.display = "block";
            }
            $('#ms-list-1 input:checked').each((idx,element) => {
                $('#initial_questions_container').append('<span>'+element.title+'</span>')
            });
        });
        $('#ms-list-2 input').change(()=>{
            $('#failure_recommendation_container').html('')
            if ($('#ms-list-2 input:checked').length < 1){
                document.getElementById("failure_recommendation_container").style.display = "none";
            }else{
                document.getElementById("failure_recommendation_container").style.display = "block";
            }
            $('#ms-list-2 input:checked').each((idx,element) => {
                $('#failure_recommendation_container').append('<span>'+element.title+'</span>')
            });
        });
        $('#ms-list-3 input').change(()=>{
            $('#language_container').html('')
            if ($('#ms-list-3 input:checked').length < 1){
                document.getElementById("language_container").style.display = "none";
            }else{
                document.getElementById("language_container").style.display = "block";
            }
            
            $('#ms-list-3 input:checked').each((idx,element) => {
                $('#language_container').append('<span>'+element.title+'</span>')
            });
        });
            
        $('#ms-list-1 input, #ms-list-2 input, #ms-list-3 input').change()
        
    }

    $(document).ready(function () {
        create_language_custom_dropdowns();
        
    });
    $(document).on("click", "#ignore-changes-in-non-primary-language", function (e) {
        let bot_id = (get_url_vars()["id"])
        let channel_name = "Viber"
        ignore_changes_in_non_primary_languages(bot_id, channel_name)
    });
    $(document).on("click", "#auto-fix-changes-in-non-primary-language", function (e) {
        let bot_id = (get_url_vars()["id"])
        let channel_name = "Viber"
        auto_fix_changes_in_non_primary_languages(bot_id, channel_name)
    });
    $(document).on("click", "#save-viber-channel", function (e) {

        var location_href = window.location.href;
        location_href = location_href.replace("#", "");
        location_href = location_href.replace("!", "");
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

        failure_recommendation_list = $("#multiple-select-viber-failure-message-list").val();
        initial_message_list = $("#multiple-select-viber-initial-message-list").val();

        viber_url = document.getElementById("viber-url").value;
        if (viber_url == '') {
            M.toast({
                "html": "URL cannot be empty!"
            }, 2000);
            return;
        }

        viber_auth_token = document.getElementById("viber-auth-token").value;
        if (viber_auth_token == '') {
            M.toast({
                "html": "Auth Token cannot be empty!"
            }, 2000);
            return;
        }

        let image_id = document.getElementById("uploaded-bot-welcome-image");
        let image_url = image_id.getAttribute("src");
        let video_url = document.getElementById("upload-bot-welcome-video-url").value.trim();
        let viber_sender_logo = document.getElementById("uploaded-bot-viber-bot-logo-image");
        let viber_sender_logo_url = viber_sender_logo.getAttribute("src");

        var selected_supported_languages = $("#multiple-select-viber-language-message-list").val()

        if (!selected_supported_languages.includes("en")) {
            selected_supported_languages.push("en");
        }

        if (isValidURL(video_url) == false && video_url != "") {
            M.toast({
                "html": "Please enter valid video url"
            }, 2000);
            return;
        }
        json_string = JSON.stringify({
            bot_id: bot_id,
            welcome_message: welcome_message,
            failure_message: failure_message,
            authentication_message: authentication_message,
            image_url: image_url,
            video_url: video_url,
            initial_message_list:initial_message_list,
            failure_recommendation_list: failure_recommendation_list,
            selected_supported_languages: selected_supported_languages,
            viber_url: viber_url,
            viber_auth_token: viber_auth_token,
            viber_sender_logo_url: viber_sender_logo_url,
            is_enable_choose_language_flow_enabled_for_welcome_response: is_enable_choose_language_flow_enabled_for_welcome_response,
            is_language_auto_detection_enabled: is_language_auto_detection_enabled,
        });
        json_string = EncryptVariable(json_string)
        $.ajax({
            url: "/chat/channels/viber/save/",
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
                        "html": "Channel details updated successfully."
                    })
                    window.location = window.location.href;
                } else if (response["status"] == 400) {
                    M.toast({
                        "html": response["message"]
                    }, 2000)
                } else if (response["status"] == 401) {
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
                        "html": "Channel details couldn't be saved. Please try again."
                    })
                }
            },
            error: function (error) {
                console.log("Report this error: ", error);
            }
        });
    });

    $("#multiple-select-viber-language-message-list").change(function () {
        
        checked_list = $('#ms-list-3 input:checked');
        if (checked_list.length <= 1) {
            document.getElementById("is_language_auto_detection_enabled").checked = false;
            document.getElementById("is_language_auto_detection_enabled").disabled = true;
            document.getElementById("bot_language_auto_detection_div").style.display = "none"
        } else {
            document.getElementById("is_language_auto_detection_enabled").disabled = false;
            document.getElementById("bot_language_auto_detection_div").style.display = "grid"
        }

        if (checked_list.length <= 1) {
            document.getElementById("is_enable_choose_language_flow_enabled_for_welcome_response").checked = false;
            document.getElementById("is_enable_choose_language_flow_enabled_for_welcome_response").disabled = true;
            document.getElementById("enable_choose_language_welcome_response_toogle_div").style.display = "none"
        } else {
            document.getElementById("is_enable_choose_language_flow_enabled_for_welcome_response").disabled = false;
            document.getElementById("enable_choose_language_welcome_response_toogle_div").style.display = "grid"
        }

    });

    $(document).on("click", "#save-viber-channel-for-non-primary-language", function (e) {
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
        channel_name = "Viber"

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
        document.getElementById("easychat_viber_channel_preloader").style.display = "block";
        $.ajax({
            url: "/chat/save-channel-language-tuned-objects/",
            type: "POST",
            data: {
                json_string: json_string
            },
            success: function (response) {
                document.getElementById("easychat_viber_channel_preloader").style.display = "none";
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
                document.getElementById("easychat_viber_channel_preloader").style.display = "none";
                console.log("Report this error: ", error);
            },
        });
    });
}

function set_viber_webhook(element) {

    element.innerHTML = "Adding...";
    var location_href = window.location.href;
    location_href = location_href.replace("#", "");
    location_href = location_href.replace("!", "");
    var bot_id = location_href.split("?")[1].split("=")[1];
    var viber_auth_token = document.getElementById("viber-auth-token").value;
    var viber_url = document.getElementById("viber-url").value;

    json_string = JSON.stringify({
        bot_id: bot_id,
        viber_auth_token: viber_auth_token,
        viber_url: viber_url
    });
    json_string = EncryptVariable(json_string)
    $.ajax({
        url: "/chat/viber/set-webhook/",
        type: "POST",
        headers: {
            'X-CSRFToken': get_csrf_token()
        },
        data: {
            json_string: json_string
        },
        success: function (response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                element.classList.remove("green");
                element.classList.add("grey");
                element.removeAttribute("onclick");
                document.getElementById("viber-url").value = response["viber_url"];
                document.getElementById("viber-url").setAttribute("readonly", true);
                document.getElementById("viber-auth-token").value = response["viber_auth_token"];
                document.getElementById("viber-auth-token").setAttribute("readonly", true);
                M.toast({
                    "html": "API token added successfully."
                }, 2000)
                element.innerHTML = "Connected";
            } else {
                M.toast({
                    "html": "Unable to set Webhook. Please re-verify your credentials or report this issue"
                }, 2000)
                element.innerHTML = "Re-Connect Webhook";
            }
        },
        error: function (error) {
            M.toast({
                "html": "Please report this error " + error
            }, 2000)
        }
    });
}

function html_tags_remover(text) {

    return text.replace(/<\/?[^>]+(>|$)/g, "").trim();
}
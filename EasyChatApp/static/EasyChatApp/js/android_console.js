if (window.location.pathname.indexOf("/chat/channels/android") != -1) {

    function save_android_theme_settings(element) {
        update_bot_color_font()
        check_theme_change = true
        $("#save-android-channel").click();
    }

    function update_bot_color_font() {
        theme_selected = [];
        theme_elemnts = $("input:radio[name=easychat-theme]:checked")
        for (var i = 0; i < theme_elemnts.length; i++) {
            theme_selected.push(theme_elemnts[i].value)

        }
        if (theme_selected.length == 0) {
            alert("Please select theme")
            return
        }
        theme_selected = theme_selected[0]

        if (theme_selected == "theme_7") {
            bot_theme_color = "2D4CB8"
            save_bot_font('Roboto', '14px')
            check_font_change = true
        } else {
            bot_theme_color = $("#bot_theme_color").val()
        }
    }

    function get_url_vars() {
        var vars = {};
        var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m, key, value) {
            vars[key] = value;
        });
        return vars;
    }

    function font_family_list(font, font_size) {
        $.ajax({
            url: "https://www.googleapis.com/webfonts/v1/webfonts?key=AIzaSyAxUTWdP9EaAtUAdWscKgu8KXLwzW4tXOI",
            type: "GET",
            success: function(response) {
                var html_string = '';
                font_item_list = [];
                font_item_list = response['items']
                for (var i = 0; i < font_item_list.length; i++) {
                    if (font_item_list[i]['family'] == font) {
                        html_string += '<option value=' + font_item_list[i]['family'].replace(' ', '+') + ' selected>' + font_item_list[i]['family'] + '</option>';
                    } else {
                        html_string += '<option value=' + font_item_list[i]['family'].replace(' ', '+') + '>' + font_item_list[i]['family'] + '</option>';
                    }
                }
                size_list = '<option value="" selected>Choose One</option>'
                for (var i = 1; i <= 40; i++) {
                    if (font_size == i) {
                        size_list += "<option value='" + i + "px' selected>" + i + "px </option>";
                    } else {
                        size_list += "<option value='" + i + "px'>" + i + "px </option>";
                    }
                }
                $('#modal-set-bot-font').modal("open");
                $("#bot-font-list").select2({
                    dropdownParent: $("#modal-set-bot-font"),
                    width: "100%",
                });
                $("#bot-font-size-list").select2({
                    dropdownParent: $("#modal-set-bot-font"),
                    width: "100%",
                });
                $("#bot-custom-font-size").select2({
                    dropdownParent: $("#modal-set-bot-font"),
                    width: "100%",
                });
                document.getElementById("bot-font-list").innerHTML = html_string;
                document.getElementById("bot-custom-font-size").innerHTML = size_list;

            },
            error: function() {

            },
        });
    }

    function set_test_font(font, font_size) {
        font_css_list = document.getElementsByClassName("bot-name");
        for (var i = 0; i < font_css_list.length; i++) {
            font_css_list[i].remove();
        }

        font_family = document.getElementById("bot-font-list").value;
        font_size_custom = document.getElementById("bot-font-size-list").value;
        if (font_size_custom == "custom") {
            document.getElementById("bot-custom-font-size-div").style.display = "block";
        } else {
            document.getElementById("bot-custom-font-size-div").style.display = "none";
            document.getElementById("bot-custom-font-size").value = "";
        }
        if (font_size_custom == "custom") {
            font_size_custom = document.getElementById("bot-custom-font-size").value;
        }
        if (font_size_custom == "") {
            font_size_custom = font_size;
        }
        if (font_family == '') {
            font_family = font;
        }
        document.getElementById("bot-font-test").style.fontFamily = font_family.replace('+', ' ');
        document.getElementById("bot-font-data").style.fontFamily = font_family.replace('+', ' ');
        document.getElementById("bot-font-test").style.fontSize = "14px";
        document.getElementById("bot-font-test").value = document.getElementById("bot-font-test").value;
        var x = document.createElement("LINK");
        x.setAttribute("rel", "stylesheet");
        x.setAttribute("href", "https://fonts.googleapis.com/css?family=" + font_family);
        x.setAttribute("class", "bot-font");
        document.head.appendChild(x);
    }

    function save_bot_font(font, font_size) {
        var location_href = window.location.href;
        var location_href = location_href.replace("#", "");
        var location_href = location_href.replace("!", "");
        var bot_id = get_url_vars()['id']
        font_family = document.getElementById("bot-font-list").value;
        font_size_custom = document.getElementById("bot-font-size-list").value;
        if (font_size_custom == "custom") {
            font_size_custom = document.getElementById("bot-custom-font-size").value;
        }
        if (font_size_custom == "") {
            font_size_custom = font_size;
        }
        if (font_family == '' || check_font_change) {
            font_family = font.replace('+', ' ');
        }
        font_family = font_family.replace('+', ' ');
        var json_string = JSON.stringify({
            bot_id: bot_id,
            font: font_family,
            font_size: "14px",
        })
        json_string = EncryptVariable(json_string)
        $.ajax({
            url: "/chat/bot/save-font/",
            type: "POST",
            data: {
                json_string: json_string
            },
            success: function(response) {
                response = custom_decrypt(response)
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    document.getElementById("bot-font-data").value = font_family;
                } else {
                    M.toast({
                        "html": "Internal Server Error"
                    }, 2000);
                }
            },
            error: function(error) {
                document.getElementById("easychat_android_channel_preloader").style.display = "none";
                console.log("Report this error: ", error)
            }
        });
        document.getElementById("bot-font-list").value;
        document.getElementById("bot-font-size-list").value;
        document.getElementById("bot-custom-font-size").value;
    }

    var location_href = window.location.href;
    var location_href = location_href.replace("#", "");
    var location_href = location_href.replace("!", "");
    var bot_id = get_url_vars()['id']
    var selected_language = get_url_vars()['selected_lang']
    var json_string = JSON.stringify({
        bot_id: bot_id,
        selected_language: selected_language,
    })
    json_string = EncryptVariable(json_string)
    document.getElementById("easychat_android_channel_preloader").style.display = "block";
    $.ajax({
        url: "/chat/channels/android/edit/",
        type: "POST",
        data: {
            json_string: json_string
        },
        success: function(response) {
            document.getElementById("easychat_android_channel_preloader").style.display = "none";
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                failure_recommendation_list = response["failure_recommendations"]["items"]
                initial_message_list = response["initial_message"]["items"];
                images = response["initial_message"]["images"];
                compressed_images = response["initial_message"]["compressed_images"];
                videos = response["initial_message"]["videos"];

                carousel_img_url_list = response["carousel_img_url_list"]["items"];
                compressed_img_url_list = response["carousel_img_url_list"]["compressed_items"];
                redirect_url_list = response["redirect_url_list"]["items"];
                welcome_banner_count = response["welcome_banner_count"];
                try {
                    selected_language = get_url_vars()['selected_lang']
                    if (selected_language == "en" || selected_language == null || selected_language == undefined) {
                        if (welcome_banner_count < 1) {
                            preview_banner_button = document.getElementById("preview-banner")
                            preview_banner_button.style.opacity = "0.5";
                            preview_banner_button.disabled = true;
                            preview_banner_button.style.cursor = "not-allowed";
                        }
                    }

                } catch (err) {
                    console.log(err)
                }

                for (var i = 0; i < carousel_img_url_list.length; i++) {
                    if (compressed_img_url_list) {
                        AddBannerRedirectionUrl(carousel_img_url_list[i], redirect_url_list[i], compressed_img_url_list[i]);
                    } else {
                        AddBannerRedirectionUrl(carousel_img_url_list[i], redirect_url_list[i]);
                    }
                }

                if (images != null && images != undefined && images.length > 0) {
                    document.getElementById("uploaded-bot-welcome-image").src = images[0];
                    if (compressed_images && compressed_images.length > 0) {
                        document.getElementById("uploaded-bot-welcome-image").dataset.compressed_src = compressed_images[0];
                    }

                    document.getElementById("uploaded-bot-welcome-image").style.display = "inline-block";
                    $("#remove-bot-welcome-image").show();
                }

                if (videos != null && videos != undefined && videos.length > 0) {
                    document.getElementById("upload-bot-welcome-video-url").value = videos[0];
                }
            } else {
                console.log("Internal server error.");
            }
        },
        error: function(error) {
            document.getElementById("easychat_android_channel_preloader").style.display = "none";
            console.log("Report this error: ", error)
        }
    });


    $(document).on("click", "#save-android-channel", function(e) {

        var location_href = window.location.href;
        var location_href = location_href.replace("#", "");
        var location_href = location_href.replace("!", "");
        var bot_id = (get_url_vars()["id"])
        var selected_language = get_url_vars()['selected_lang']
        var welcome_message = $("#welcome-message").trumbowyg('html');
        var failure_message = $("#failure-message").trumbowyg('html');
        var authentication_message = $("#authentication-message").trumbowyg('html');

        var is_language_auto_detection_enabled = document.getElementById("is_language_auto_detection_enabled").checked
        var is_textfield_input_enabled = document.getElementById("is-input-textfield").checked

        var validation_message = check_channel_messages_validation(welcome_message, failure_message, authentication_message);
        if (validation_message != "No Error") {
            M.toast({
                "html": validation_message
            }, 2000);
            return;
        }


        initial_message_list = $("#multiple-select-initial-message-list").val();

        failure_recommendation_list = $("#multiple-select-failure-message-list").val();

        selected_supported_languages = get_selected_languages_list()
        if (!selected_supported_languages.includes("en")) {
            selected_supported_languages.push("en");
        }
        sticky_intent_list = $("#multiple-select-sticky-intent-list").val();

        is_automatic_carousel_enabled = document.getElementById('carousel_switch').checked;
        carousel_time = document.getElementById('carousel_time').value;

        if (check_theme_change == false)
            bot_theme_color = $("#bot_theme_color").val();

        if (is_automatic_carousel_enabled && carousel_time <= 0) {
            M.toast({
                "html": "Enter valid scrolling time interval"
            }, 2000);
            return;
        }

        if (is_automatic_carousel_enabled && carousel_time > 30) {
            M.toast({
                "html": "Scrolling time limit is 30 seconds"
            }, 2000);
            return;
        }

        var inputs = document.getElementsByTagName("input");
        carousel_img_url_list = []
        redirect_url_list = []
        compressed_img_url_list = []
        for (var i = 0; i < inputs.length; i++) {
            if (inputs[i].id.indexOf("imageurl_str_image_url_") == 0) {
                data_id = inputs[i].id
                token_id = data_id.split("_")[4];
                image_url = store_this_data_locally($("#imageurl_str_image_url_" + token_id).val())
                carousel_img_url_list.push(image_url)
            }
        }

        for (var i = 0; i < inputs.length; i++) {
            if (inputs[i].id.indexOf("redurl_str_rd_url_") == 0) {
                data_id = inputs[i].id
                token_id = data_id.split("_")[4];
                redirect_url_list.push($("#redurl_str_rd_url_" + token_id).val())
            }
        }

        for (var i = 0; i < inputs.length; i++) {
            if (inputs[i].id.indexOf("imageurl_compressed_str_image_url_") == 0) {
                image_url = inputs[i].value
                compressed_img_url_list.push(image_url)
            }
        }

        image_id = document.getElementById("uploaded-bot-welcome-image");
        image_url = image_id.getAttribute("src");

        compressed_image_url = image_id.dataset.compressed_src;
        if (!compressed_image_url) compressed_image_url = '';

        video_url = document.getElementById("upload-bot-welcome-video-url").value.trim();

        if (isValidURL(video_url) == false && video_url != "") {
            M.toast({
                "html": "Please enter valid video url"
            }, 2000);
            return;
        }

        video_url = getEmbedVideoURL(video_url);

        theme_selected = [];
        theme_elemnts = $("input:radio[name=easychat-theme]:checked")
        for (var i = 0; i < theme_elemnts.length; i++) {
            theme_selected.push(theme_elemnts[i].value)

        }
        if (theme_selected.length == 0) {
            alert("Please select theme")
            return
        }

        theme_selected = theme_selected[0]

        if(theme_selected == "theme_3"){

            if(!check_is_welcome_banner_present()){
                showToast("Welcome banner can not be empty for this theme");
                return;
            }   
        }

        let sticky_button_format = "Button";
        var sticky_button_menu_format_selected = document.getElementById('menu-format').checked

        var sticky_intent_list_menu = []
        if (sticky_button_menu_format_selected) {
            sticky_button_format = "Menu";
            var elements = document.querySelectorAll('.sticky-intent-menu-item-div > input');

            for (element of elements) {
                let intent = element.value;
                intent = intent.split('_');
                sticky_intent_list_menu.push(intent);
            }
        }

        var hamburger_list_menu = []
        var quick_list_menu = []

        var is_bot_notification_sound_enabled = false;
        var elem = document.getElementById("is_bot_notification_sound_enabled");
        if (elem != null) {
            if (elem.checked) {
                is_bot_notification_sound_enabled = true;
            }

            // json_string.is_bot_notification_sound_enabled = is_bot_notification_sound_enabled
        }
        is_web_bot_phonetic_typing_enabled = false
        if (selected_supported_languages.includes("hi")) {
            is_web_bot_phonetic_typing_enabled = document.getElementById("is_web_bot_phonetic_typing_enabled").checked
        }
        disclaimer_message = ""
        if (is_web_bot_phonetic_typing_enabled) {
            var disclaimer_message = $("#language-disclaimer-text").trumbowyg('html');
            disclaimer_message = disclaimer_message.trim();
            if (disclaimer_message == "") {
                M.toast({
                    "html": "Disclaimer message cannot be empty."
                }, 2000);
                return;
            }

            if (disclaimer_message.trim().length > 256) {
                M.toast({
                    "html": "Disclaimer message to long."
                }, 2000);
                return;
            }
        }

        var wb_table_body = document.getElementById("easychat-welcome-banner-draggable-item");
        var welcome_banner_list = [];
        for (var ix=0; ix<wb_table_body.children.length; ix++){
            welcome_banner_list.push(wb_table_body.children[ix].id.split("wb-card-")[1].trim());
        }

        var is_enabled_intent_icon = document.getElementById("enable-intent-icon").checked;

        var intent_icon_channel_choices = [];
        if (is_enabled_intent_icon) {
            var checked_inputs = document.getElementById("intent-icon-choices-wrapper").querySelectorAll("input[type='checkbox']:checked");
            for (var i=0; i<checked_inputs.length; i++) {
                intent_icon_channel_choices.push(checked_inputs[i].value);
            }

            if (!intent_icon_channel_choices.length) {
                M.toast({
                    "html": "Please select atleast one intent icon choices from dropdown"
                }, 2000);
                return ;
            }
        }

        json_string = {
            bot_id: bot_id,
            welcome_message: welcome_message,
            failure_message: failure_message,
            authentication_message: authentication_message,
            initial_message_list: initial_message_list,
            image_url: image_url,
            compressed_image_url: compressed_image_url,
            video_url: video_url,
            theme_selected: theme_selected,
            failure_recommendation_list: failure_recommendation_list,
            carousel_img_url_list: carousel_img_url_list,
            redirect_url_list: redirect_url_list,
            compressed_img_url_list: compressed_img_url_list,
            bot_theme_color: bot_theme_color,
            sticky_intent_list: sticky_intent_list,
            is_automatic_carousel_enabled: is_automatic_carousel_enabled,
            carousel_time: carousel_time,
            sticky_intent_list_menu: sticky_intent_list_menu,
            sticky_button_format: sticky_button_format,
            hamburger_items: hamburger_list_menu,
            quick_items: quick_list_menu,
            selected_supported_languages: selected_supported_languages,
            selected_language: selected_language,
            is_bot_notification_sound_enabled: is_bot_notification_sound_enabled,
            is_web_bot_phonetic_typing_enabled: is_web_bot_phonetic_typing_enabled,
            disclaimer_message: disclaimer_message,
            welcome_banner_list: welcome_banner_list,
            is_language_auto_detection_enabled: is_language_auto_detection_enabled,
            is_enabled_intent_icon: is_enabled_intent_icon,
            is_textfield_input_enabled: is_textfield_input_enabled,
            intent_icon_channel_choices: intent_icon_channel_choices,
        }

        var is_bot_notification_sound_enabled = false;
        var elem = document.getElementById("is_bot_notification_sound_enabled");
        if (elem != null) {
            if (elem.checked) {
                is_bot_notification_sound_enabled = true;
            }

            json_string.is_bot_notification_sound_enabled = is_bot_notification_sound_enabled
        }

        json_string = JSON.stringify(json_string);
        json_string = EncryptVariable(json_string);
        document.getElementById("easychat_android_channel_preloader").style.display = "block";
        $.ajax({
            url: "/chat/channels/android/save/",
            type: "POST",
            data: {
                json_string: json_string
            },
            headers: {
            "X-CSRFToken": get_csrf_token()
            },
            success: function(response) {
                document.getElementById("easychat_android_channel_preloader").style.display = "none";
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
                        "html": "Internal Server Error. Please report this error"
                    })
                }
            },
            error: function(error) {
                document.getElementById("easychat_android_channel_preloader").style.display = "none";
                console.log("Report this error: ", error);
            },
        });
    });

    $(document).on("click", "#ignore-changes-in-non-primary-language", function(e) {
        let bot_id = (get_url_vars()["id"])
        let channel_name = "Android"
        ignore_changes_in_non_primary_languages(bot_id, channel_name)
    });
    $(document).on("click", "#auto-fix-changes-in-non-primary-language", function(e) {
        let bot_id = (get_url_vars()["id"])
        let channel_name = "Android"
        auto_fix_changes_in_non_primary_languages(bot_id, channel_name)
    });
    $(document).ready(function() {
        create_language_custom_dropdowns();
        disable_auto_pop_up_fileds();
        // will be using this in future
        // disable_web_landing_options();
    });
    add_channel_language_selction_event("android")
    add_language_dropdown_search_event()
    language_dropdown_close_onclicking_outside_event()
    language_search_dropdown_event()
    open_close_language_dropdown_event()

    $(document).on("click", "#save-android-channel-for-non-primary-language", function(e) {
        let bot_id = (get_url_vars()["id"])
        let selected_language = get_url_vars()['selected_lang']
        let welcome_message = $("#welcome-message").trumbowyg('html');
        let failure_message = $("#failure-message").trumbowyg('html');
        let authentication_message = $("#authentication-message").trumbowyg('html');

        var validation_message = check_channel_messages_validation(welcome_message, failure_message, authentication_message);
        if (validation_message != "No Error") {
            M.toast({
                "html": validation_message
            }, 2000);
            return;
        }

        channel_name = "Android"

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
        document.getElementById("easychat_android_channel_preloader").style.display = "block";
        $.ajax({
            url: "/chat/save-channel-language-tuned-objects/",
            type: "POST",
            data: {
                json_string: json_string
            },
            success: function(response) {
                document.getElementById("easychat_android_channel_preloader").style.display = "none";
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
            error: function(error) {
                document.getElementById("easychat_android_channel_preloader").style.display = "none";
                console.log("Report this error: ", error);
            },
        });
    });

}

var upload_image_file_limit_size = 2048000;
var image_compressed_path = "";

async function upload_welcome_banner(input_upload_image) {
    var response = await upload_image();

    if (response && response.status == 200) {
        var uploaded_image_src = response["src"];
    } else {
        M.toast({
            "html": "Image upload failed."
        }, 2000);
        return;
    }

    var img_name = uploaded_image_src.split("/")[uploaded_image_src.split("/").length - 1];
    img_name = img_name.replace(/.*[\/\\]/, '');
    if(img_name) {
        $('#upload-image-section .drag-drop-container').hide();
        $('#upload-image-section #image-url-input-field').hide();
        $('#upload-image-section #error-message').hide();
        $('#upload-image-section #max-size-limit').hide();
        $('#upload-image-section #image-selected-container').html(`
        <div class="selected-image-wrapper">
            <div class="image-container-div">
                <img id="welcome-banner-uploaded-image" img-src="`+ uploaded_image_src +`" src="`+ uploaded_image_src +`">
                <svg onclick="handle_image_cross_btn()" class="dismiss-circle" width="20" height="21" viewBox="0 0 20 21" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M10 2.5C14.4183 2.5 18 6.08172 18 10.5C18 14.9183 14.4183 18.5 10 18.5C5.58172 18.5 2 14.9183 2 10.5C2 6.08172 5.58172 2.5 10 2.5ZM7.80943 7.61372C7.61456 7.47872 7.34514 7.49801 7.17157 7.67157L7.11372 7.74082C6.97872 7.93569 6.99801 8.20511 7.17157 8.37868L9.29289 10.5L7.17157 12.6213L7.11372 12.6906C6.97872 12.8854 6.99801 13.1549 7.17157 13.3284L7.24082 13.3863C7.43569 13.5213 7.70511 13.502 7.87868 13.3284L10 11.2071L12.1213 13.3284L12.1906 13.3863C12.3854 13.5213 12.6549 13.502 12.8284 13.3284L12.8863 13.2592C13.0213 13.0643 13.002 12.7949 12.8284 12.6213L10.7071 10.5L12.8284 8.37868L12.8863 8.30943C13.0213 8.11456 13.002 7.84514 12.8284 7.67157L12.7592 7.61372C12.5643 7.47872 12.2949 7.49801 12.1213 7.67157L10 9.79289L7.87868 7.67157L7.80943 7.61372Z" fill="#4D4D4D"/>
                </svg>                                                    
            </div>
            <div class="image-name-copy-div">
                <div class="image-name" style="font-weight: normal;font-size: 14px;color:#000000;line-height: 17px;margin-bottom: 10px;">
                    ${img_name}
                </div>
                <div onclick="copy_image_url()" class="image-url-copy-div">
                    <svg style="margin-right: 3px;" width="24" height="25" viewBox="0 0 24 25" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M16 16.5C18.2091 16.5 20 14.7091 20 12.5C20 10.3578 18.316 8.60892 16.1996 8.5049L16 8.5H14C13.5858 8.5 13.25 8.83579 13.25 9.25C13.25 9.6297 13.5322 9.94349 13.8982 9.99315L14 10H16C17.3807 10 18.5 11.1193 18.5 12.5C18.5 13.8255 17.4685 14.91 16.1644 14.9947L16 15H14C13.5858 15 13.25 15.3358 13.25 15.75C13.25 16.1297 13.5322 16.4435 13.8982 16.4932L14 16.5H16ZM10 16.5C10.4142 16.5 10.75 16.1642 10.75 15.75C10.75 15.3703 10.4678 15.0565 10.1018 15.0068L10 15H8C6.61929 15 5.5 13.8807 5.5 12.5C5.5 11.1745 6.53154 10.09 7.83562 10.0053L8 10H10C10.4142 10 10.75 9.66421 10.75 9.25C10.75 8.8703 10.4678 8.55651 10.1018 8.50685L10 8.5H8C5.79086 8.5 4 10.2909 4 12.5C4 14.6422 5.68397 16.3911 7.80036 16.4951L8 16.5H10ZM8.25 13.25H15.75C16.1642 13.25 16.5 12.9142 16.5 12.5C16.5 12.1203 16.2178 11.8065 15.8518 11.7568L15.75 11.75H8.25C7.83579 11.75 7.5 12.0858 7.5 12.5C7.5 12.8797 7.78215 13.1935 8.14823 13.2432L8.25 13.25H15.75H8.25Z" fill="#0254D7"/>
                    </svg>
                    <span>
                        Copy Image URL
                    </span>                                                        
                </div>
            </div>
        </div>`);
    }
}

function handle_image_upload_input_change(ele) {

    var input_upload_image = ele.files[0];

    if (input_upload_image == null || input_upload_image == undefined) {
        M.toast({
            "html": "Please select a valid file."
        }, 2000);
        document.getElementById("error-message").innerText = "Please select a valid file.";
        document.getElementById("error-message").style.display = "block";
        return false;
    }

    if (input_upload_image.name.match(/.+\.(jpg|jpeg|png|gif)$/i) == null) {
        M.toast({
            "html": "Please select the correct file type(.jpg, .png)"
        }, 2000);
        document.getElementById("error-message").innerText = "Please select the correct file type(.jpg, .png)";
        document.getElementById("error-message").style.display = "block";
        return false;
    }

    if (input_upload_image.size > upload_image_file_limit_size) {
        M.toast({
            "html": "File size should be less than 2 MB."
        }, 2000);
        document.getElementById("error-message").innerText = "File size should be less than 2 MB.";
        document.getElementById("error-message").style.display = "block";
        return false;
    }

    if (check_malicious_file(input_upload_image.name) == true) {
        M.toast({
            "html": "Please select the correct file type(.jpg, .png)"
        }, 2000);
        document.getElementById("error-message").innerText = "Please select the correct file type(.jpg, .png)";
        document.getElementById("error-message").style.display = "block";
        return false;
    }

    var reader = new FileReader();
    reader.readAsDataURL(input_upload_image);
    reader.onload = function() {

        base64_str = reader.result.split(",")[1];

        uploaded_file = [];
        uploaded_file.push({
            "filename": input_upload_image.name,
            "base64_file": base64_str,
        });

        upload_welcome_banner(input_upload_image);

    };

    reader.onerror = function(error) {
        console.log('Error: ', error);
        return false;
    };
}

function handle_image_cross_btn(){
  $("#upload-image-section .drag-drop-container").show();
  $('#upload-image-section #image-url-input-field').show();
  $('#upload-image-section #error-message').show();
  $('#upload-image-section #max-size-limit').show();
  $("#upload-image-section #image-selected-container").html("");
  $("#upload-image-section #drag-drop-input-box").val(""); 
}

function create_dropdowns() {
  $('#action-type').select2({
      dropdownParent: $('#action-type-container')
  });
  $('#intent-type').select2({
      dropdownParent: $('#intent-type-container')
  });
  $('#edit-intent-type').select2({
      dropdownParent: $('#edit-intent-type-container')
  });
}

$(document).ready(function(){
    setTimeout(create_dropdowns, 500);
});

$('#intent-type').select2().on('select2:open', function(e){
  $('.select2-search__field').attr('placeholder', 'Search Intent');
})
$('#edit-intent-type').select2().on('select2:open', function(e){
  $('.select2-search__field').attr('placeholder', 'Search Intent');
})
  
function handle_action_type_change(element){
    if(element.value==="1"){
        $('#select-intent').hide();
        $('#redirection-url').show();
    }
    else if(element.value==="2"){
        $('#select-intent').show();
        $('#redirection-url').hide();
    }
    else if(element.value==="3"){
        $('#select-intent').show();
        $('#redirection-url').show();
    }
}

$(function() {
        $('#easychat-welcome-banner-draggable-item').sortable({
            containment: "parent",
        });
    });
$(document).ready(function(){

    $('#add-banner-modal').removeAttr('tabIndex');

    $(function() {
        $('#intent-icon-choices-multiple-select').multiselect({
            columns: 1,
            placeholder: 'Select Intent',
            search: true,
            searchOptions: {
                'default': 'Search Intent'
            },
            selectAll: false,
        });
    });
})

function create_welcome_banner_card(response) {
    var table_body = document.getElementById("easychat-welcome-banner-draggable-item");

    var redirect_html = "-";
    if (response["redirection_url"] != "-") {
        redirect_html = `<a target="_blank" href="` + response["redirection_url"] + `">` + response["redirection_url"] + `</a>`;
    }

    var html = `<tr class="ui-sortable-handle" id="wb-card-` + response["welcome_banner_pk"] + `" style="">
        <td>
            <div class="easychat-welcome-banner-list-image-name-wrapper">
                <div class="image-div">
                    <img src="` + response["image_url"] + `">
                </div>
                <div class="image-name-div">
                    ` + response["image_name"] + `
                </div>
            </div>
        </td>
        <td>` + redirect_html + `</td>
        <td>` + response["intent_name"] + `</td>
        <td class="icons-div">
            <button class="banner-eye-icon tooltip" onclick="image_modal_open('` + response["image_url"] + `','/')"><img src="/static/EasyChatApp/img/wc-eye-icon.svg">
                <span class="tooltiptext">View Banner</span>
            </button>
            <button type="button" class="banner-edit-icon tooltip" data-target="edit-welcome-banner-redirecturl-modal" id="wb-edit-btn-` + response["welcome_banner_pk"] + `" onclick="edit_welcome_banner_modal('` + response["action_type"] + `', '` + response["redirection_url"] + `', '` + response["intent_pk"] + `', '` + response["welcome_banner_pk"] + `')"><img src="/static/EasyChatApp/img/wc-edit-icon.svg">
            <span class="tooltiptext">Edit URL</span>
            </button>
            <button class="banner-cross-icon delete-button-image-redirection-url tooltip" data-target="delete-welcome-banner-redirecturl-modal" onclick="delete_welcome_banner_modal('` + response["welcome_banner_pk"] + `')"><img src="/static/EasyChatApp/img/wc-cross-icon.svg">
                <span class="tooltiptext remove-banner-tooltip">Remove Banner</span>
            </button>
        </td>
    </tr>`;

    table_body.insertAdjacentHTML("beforeend", html);
}

function save_welcome_banner() {

    var action_type = document.getElementById("action-type").value;

    var image_url = "";
    if (document.getElementById("welcome-banner-uploaded-image")) {
        image_url = document.getElementById("welcome-banner-uploaded-image").src;
    } else {
        image_url = document.getElementById("wb-image-url").value.trim();
        if (!isValidURL(image_url)) {
            M.toast({
                "html": "Please enter valid image url."
            }, 2000);
            return;
        }

        if (image_url.trim() == "") {
            M.toast({
                "html": "Please enter valid image url."
            }, 2000);
            return;
        }
    }

    var redirection_url = "";
    var intent_pk = "";

    if (action_type != "2") {
        redirection_url = document.getElementById("wb-redirection-url").value.trim();
        if (!isValidURL(redirection_url)) {
            M.toast({
                "html": "Please enter valid redirection url."
            }, 2000);
            return;
        }

        if (redirection_url.trim() == "") {
            M.toast({
                "html": "Please enter valid redirection url."
            }, 2000);
            return;
        }
    }

    if (action_type != "1") {
        intent_pk = document.getElementById("intent-type").value;
        if (intent_pk.trim() == "none") {
            M.toast({
                "html": "Please select valid intent."
            }, 2000);
            return;
        }
    }

    json_string = JSON.stringify({
        "bot_id": bot_id,
        "channel_name": "Android",
        "action_type": action_type,
        "image_url": image_url,
        "redirection_url": redirection_url,
        "intent_pk": intent_pk
    })
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: '/chat/save-welcome-banner/',
        type: "POST",
        data: {
            json_string: json_string
        },
        dataType: "json",
        async: false,
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response['status'] == 200) {
                M.toast({
                    "html": "Welcome banner created successfully."
                }, 2000);
                create_welcome_banner_card(response);

                var preview_banner_button = document.getElementById("preview-banner")
                preview_banner_button.style.opacity = "1";
                preview_banner_button.disabled = false;
                preview_banner_button.style.cursor = "pointer";
                $('#add-banner-modal').modal('close');
            } else {
                M.toast({
                    "html": response["message"]
                }, 2000);
                return
            }
        },
        error: function(xhr, textstatus, errorthrown) {
            M.toast({
                "html": "There are some issues while creating welcome banner."
            }, 2000);
        }
    });
}

function image_modal_open(img_url, rd_url) {
    document.getElementById("welcome-banner-list-image-rdurl").href = rd_url;
    document.getElementById("welcome-banner-image-view").src = img_url;
    $('#welcome-banner-image-view-modal').modal('open');
}

function edit_welcome_banner_modal(action_type, redirection_url, intent_pk, welcome_banner_pk) {

    var select_input = document.getElementById("select2-edit-action-type-container");

    if (action_type == "1") {
        select_input.innerText = "Redirection URL";
    } else if (action_type == "2") {
        select_input.innerText = "Trigger Intent";
    } else {
        select_input.innerText = "Redirection URL with Trigger Intent";
    }

    if (action_type == "2") {
        document.getElementById("wb-edit-redirection-url").value = "";
        document.getElementById("edit-redirection-url").style.display = "none";
    } else {
        document.getElementById("wb-edit-redirection-url").value = redirection_url;
        document.getElementById("edit-redirection-url").style.display = "block";
    }

    if (action_type == "1") {
        document.getElementById("edit-select-intent").style.display = "none";
        document.getElementById("edit-intent-type").value = "none";
        $('#edit-intent-type').select2({
            dropdownParent: $('#edit-intent-type-container')
        });
    } else {
        document.getElementById("edit-select-intent").style.display = "block";
        document.getElementById("edit-intent-type").value = String(intent_pk).toLowerCase();
        $('#edit-intent-type').select2({
            dropdownParent: $('#edit-intent-type-container')
        });
    }

    document.getElementById("edit-welcome-banner-redirecturl-modal").getElementsByClassName("filter-modal-footer-btn")[0].setAttribute("wb_id", welcome_banner_pk)
    document.getElementById("edit-welcome-banner-redirecturl-modal").getElementsByClassName("filter-modal-footer-btn")[0].setAttribute("action_type", action_type)

    $("#edit-welcome-banner-redirecturl-modal").modal("open");

}

function edit_banner_details(el) {
    var action_type = el.getAttribute("action_type");
    var wb_id = el.getAttribute("wb_id");
    var edited_rd_url = "";
    var intent_id = "";

    if (action_type != "2") {
        var edited_rd_url = document.getElementById("wb-edit-redirection-url").value.trim()
        if (!isValidURL(edited_rd_url)) {
            M.toast({
                "html": "Please enter valid redirect url."
            }, 2000);
            return;
        }

        if (edited_rd_url.trim() == "") {
            M.toast({
                "html": "Please enter valid redirect url."
            }, 2000);
            return;
        }
    }

    if (action_type != "1") {
        intent_id = document.getElementById("edit-intent-type").value;
        if (intent_id.trim() == "") {
            M.toast({
                "html": "Please select valid intent."
            }, 2000);
            return;
        }
    }

    json_string = JSON.stringify({
        "wb_id": wb_id,
        "redirected_url": edited_rd_url,
        "intent_id": intent_id
    })
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: '/chat/edit-welcome-banner/',
        type: "POST",
        data: {
            json_string: json_string
        },
        dataType: "json",
        async: false,
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response['status'] == 200) {
                M.toast({
                    "html": "Welcome banner edited successfully."
                }, 2000);

                var edit_btn = document.getElementById("wb-edit-btn-" + response["wb_id"]);
                edit_btn.setAttribute("onclick", `edit_welcome_banner_modal("` + response["action_type"] + `", "` + response["redirection_url"] + `", "` + response["intent_id"] + `", "` + response["wb_id"] + `")`);

                var td_elements = document.getElementById("wb-card-" + response["wb_id"]).getElementsByTagName("td");
                if (response["redirection_url"] == "-") {
                    td_elements[1].innerHTML = response["redirection_url"];
                } else {
                    td_elements[1].innerHTML = `<a href="` + response["redirection_url"] + `">` + response["redirection_url"] + `</a>`;
                }
                td_elements[2].innerHTML = response["intent_name"];

                $('#edit-welcome-banner-redirecturl-modal').modal('close');
            } else {
                M.toast({
                    "html": response["message"]
                }, 2000);
                return
            }
        },
        error: function(xhr, textstatus, errorthrown) {
            M.toast({
                "html": "There are some issues while editing welcome banner."
            }, 2000);
        }
    });

}
function delete_welcome_banner_modal(welcome_banner_pk) {
    document.getElementById("delete-welcome-banner-redirecturl-modal").getElementsByClassName("termination-yes-btn")[0].setAttribute("wb_id", welcome_banner_pk)
    $("#delete-welcome-banner-redirecturl-modal").modal("open");
}
function delete_banner_details(el) {
    var wb_id = el.getAttribute("wb_id");
    json_string = JSON.stringify({
        "wb_id": wb_id
    })
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: '/chat/delete-welcome-banner/',
        type: "POST",
        data: {
            json_string: json_string
        },
        dataType: "json",
        async: false,
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response['status'] == 200) {
                $("#delete-welcome-banner-redirecturl-modal").modal("close");

                document.getElementById("wb-card-" + response["wb_id"]).remove();

                if (document.getElementById("easychat-welcome-banner-draggable-item").children.length == 0) {
                    var preview_banner_button = document.getElementById("preview-banner")
                    preview_banner_button.style.opacity = "0.5";
                    preview_banner_button.disabled = true;
                    preview_banner_button.style.cursor = "not-allowed";
                }

                M.toast({
                    "html": "Welcome banner deleted successfully."
                }, 2000);
            }
        },
        error: function(xhr, textstatus, errorthrown) {
            M.toast({
                "html": "There are some issues while deleting welcome banner."
            }, 2000);
        }
    });

}

function preview_banner() {

    var is_automatic_carousel_enabled = document.getElementById("carousel_switch").checked
    if(is_automatic_carousel_enabled) {

        var time = document.getElementById("carousel_time").value
        let isnum = /^\d+$/.test(time.trim());
        if (!isnum) {
            M.toast({
                "html": "Enter valid scrolling time input."
            }, 2000);
            return;
        }

           
           if (time <= 0) {
            M.toast({
                "html": "Enter valid scrolling time interval"
            }, 2000);
            return;
        }

        if (time > 30) {
            M.toast({
                "html": "Scrolling time limit is 30 seconds"
            }, 2000);
            return;
        }
    }

    parent = document.getElementById("preview-banner-image-list")
    while (parent.firstChild) {
        parent.removeChild(parent.firstChild);
    }

    var wb_cards = document.getElementById("easychat-welcome-banner-draggable-item").getElementsByClassName("ui-sortable-handle");
    var html = "";

    for (var i=0; i<wb_cards.length; i++){
        if (wb_cards[i].getElementsByTagName("td")[1].children[0] != null && wb_cards[i].getElementsByTagName("td")[1].children[0] != undefined) {
            html += '<li><a href="' + wb_cards[i].getElementsByTagName("td")[1].children[0].href + '" target="_blanck"><img src="' + wb_cards[i].getElementsByClassName("image-div")[0].children[0].src + '"></a></li>';
        } else {
            html += '<li><img src="' + wb_cards[i].getElementsByClassName("image-div")[0].children[0].src + '"></a></li>';
        }
    }

    $(html).appendTo($("#preview-banner-image-list"));
    $('#welcome-preview-banner-modal').modal('open');

    $("#preview-banner-image-list").slick({
        slidesToScroll: 1,
        dots: false,
        adaptiveHeight: true,
        slidesToShow: 1,
        prevArrow: '<button class="slide-arrow prev-arrow"></button>',
        nextArrow: '<button class="slide-arrow next-arrow"></button>'
    })

    setTimeout(function () {
        $(".modal-overlay").click(function () {
            if ($('#welcome-preview-banner-modal')[0].style.display !== "none") {
                $('#preview-banner-image-list').slick('unslick');
            }
        })
    }, 100)

}

$('#slider-modal-close').click(function(){
    $('#preview-banner-image-list').slick('unslick');
})

function open_add_banner_modal() {
    handle_image_cross_btn();
    document.getElementById("wb-image-url").value = "";
    document.getElementById("wb-redirection-url").value = "";
    document.getElementById("action-type").value = "1";
    $('#action-type').select2({
        dropdownParent: $('#action-type-container')
    });
    document.getElementById("intent-type").value = "none";
    $('#intent-type').select2({
        dropdownParent: $('#intent-type-container')
    });
    handle_action_type_change(document.getElementById("action-type"));
    document.getElementById("error-message").style.display = "none";
    $('#add-banner-modal').modal('open');
}

function copy_image_url() {

    const el = document.createElement('textarea');
    el.value = document.getElementById("welcome-banner-uploaded-image").src;
    document.body.appendChild(el);

    var mac = navigator.userAgent.match(/Mac|ipad|ipod|iphone/i)
    if (!navigator.clipboard) {
        if (mac && mac.toString().trim() == "Mac") {
            var editable = el.contentEditable;
            var readOnly = el.readOnly;

            el.contentEditable = true;
            el.readOnly = true;

            var range = document.createRange();
            range.selectNodeContents(el);

            var selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
            el.setSelectionRange(0, 999999);

            el.contentEditable = editable;
            el.readOnly = readOnly;
        } else {
            el.select();
        }
        document.execCommand("copy");
    } else {
        navigator.clipboard.writeText(el.value)
    }

    document.body.removeChild(el);

    M.toast({
        "html": "URL copied to clipboard"
    }, 2000)
}

$("#language-box-options-container .option .item-checkbox").change(function(){
   
    enable_disable_auto_language_detection_toogle();
    
});

function handle_theme_selection(elem) {
    if (prev_theme_selected == "") {
        prev_theme_selected = THEME_SELECTED
    }
    if (elem.id == "theme_3") {
        $('#show_welcome_banner_checkbox').hide()
        $('#show_initial_questions_checkbox').hide()
        if (!check_is_welcome_banner_present()) {
            showToast("Welcome banner can not be empty for this theme");
            document.getElementById(prev_theme_selected).checked = true
            elem.checked = false
            return;
        }
    } else {
        $('#show_welcome_banner_checkbox').css('display', 'table-row');
        $('#show_initial_questions_checkbox').css('display', 'table-row');
    }
    prev_theme_selected = elem.id;
}

var BOT_ID = ""
var is_faq_extraction_in_progress = false
var extraction_timer = null
var extraction_toast_timer = null
var faq_questions = []
var faq_answers = []
var default_welcome_message = "Hi, I am Iris, a Virtual Assistant. I am here to help you with your most common queries. You name it and I do it. How can I help you today?"
var website_faq_added = "Not Added"

$(document).ready(function() {

    $("#new_bot_message_welcome").val(default_welcome_message)
    set_character_count($("#new_bot_message_welcome")[0])
})

$('.easychat-create-bot-icon-item').click(function (e) {

    $('.easychat-create-bot-icon-item').each(function () {
        $(this).removeClass('easychat-create-bot-icon-item-active')
    })
    $(this).addClass('easychat-create-bot-icon-item-active');
    $("#create_newbot_icon_next").removeClass('create-bot-btn-disable');

});

function EncryptVariable(data) {

    utf_data = EasyChatCryptoJS.enc.Utf8.parse(data);
    encoded_data = utf_data;
    random_key = generateRandomString(16);
    encrypted_data = CustomEncrypt(encoded_data, random_key);

    return encrypted_data;
}

function createPreview() {
    const bot_icon = $(".easychat-create-bot-icon-item-active img")[0].src
    const bot_name = $("#new_bot_name").val()
    const welcome_message = $("#new_bot_message_welcome").val() === default_welcome_message ? "Default" : "Edited"
    const chipped_languages_elms = $(".language-items:checked")
    let languages_string = ""
    for (const chip of chipped_languages_elms) {
        languages_string += chip.name + ", "
    }
    languages_string = languages_string.replace(/, $/, "")
    const csat = $("#enable_csat")[0].checked ? "Enabled" : "Disabled"
    const addOnFeaturesElms = $(".add-on-features:checked")
    let addOnFeaturesHTML = ""
    if (addOnFeaturesElms.length === 0) {
        addOnFeaturesHTML += `
        <div class="create-bot-preview-item-text">
            <span>None</span>
        </div>
        `
    }
    for (const elm of addOnFeaturesElms) {
        addOnFeaturesHTML += `
        <div class="create-bot-preview-item-text">
            <span>${elm.name} Functionality</span>
        </div>
        `
    }
    const selectedChannelElms = $("input[name='create-bot-channel-btn']:checked +label")
    let containerPreviewChannelsHTML = ""
    for (const channel of selectedChannelElms) {
        const channelHTML = `
            <div class="create-bot-channels-preview-item">
                ${channel.innerHTML}
            </div>
        `
        containerPreviewChannelsHTML += channelHTML
    }
    $("#preview_icon")[0].src = bot_icon
    $(".create-bot-preview-name-text").html(bot_name)
    $("#welcome_preview").html(welcome_message)
    $("#language_preview").html(languages_string)
    $("#csat_preview").html(csat)
    $("#preview_add_on_features_div").html(addOnFeaturesHTML)
    $(".create-bot-channels-preview-content-div").html(containerPreviewChannelsHTML)
    $("#website_faq").html(website_faq_added)
}

function upload_details_over_server(element, uploaded_file) {

    return new Promise(function() {
        var csrf_token = $('input[name="csrfmiddlewaretoken"]').val();
        var json_string = JSON.stringify(uploaded_file)
        json_string = EncryptVariable(json_string)

        encrypted_data = {
            "Request": json_string
        }

        var params = JSON.stringify(encrypted_data);

        $.ajax({
            url: "/chat/upload-image/",
            type: "POST",
            contentType: "application/json",
            headers: {
                'X-CSRFToken': csrf_token
            },
            data: params,
            processData: false,
            success: function(response) {
                response = custom_decrypt(response)
                response = JSON.parse(response);
                if (response.status == 200) {
                    $('#upload-icon-section .easychat-bot-icon-upload-div').hide();
                    $('#upload-icon-section #image-selected-container').css("display", "inline-flex");

                    $('#upload-icon-section #image-selected-container').html(`
                        <div class="image-container-div">
                            <img width="40px" height="40px" src=${response.src} alt="bot_image_custom">
                            <div onclick="handle_image_cross_btn(this)" class="dismiss-circle">
                            <svg width="10" height="10" viewBox="0 0 10 10" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M0.897052 1.05379L0.96967 0.96967C1.23594 0.703403 1.6526 0.679197 1.94621 0.897052L2.03033 0.96967L5 3.939L7.96967 0.96967C8.26256 0.676777 8.73744 0.676777 9.03033 0.96967C9.32322 1.26256 9.32322 1.73744 9.03033 2.03033L6.061 5L9.03033 7.96967C9.2966 8.23594 9.3208 8.6526 9.10295 8.94621L9.03033 9.03033C8.76406 9.2966 8.3474 9.3208 8.05379 9.10295L7.96967 9.03033L5 6.061L2.03033 9.03033C1.73744 9.32322 1.26256 9.32322 0.96967 9.03033C0.676777 8.73744 0.676777 8.26256 0.96967 7.96967L3.939 5L0.96967 2.03033C0.703403 1.76406 0.679197 1.3474 0.897052 1.05379L0.96967 0.96967L0.897052 1.05379Z" fill="#FF0000"/>
                            </svg>

                            </div>                                                   
                        </div>
                    `)
                    $("#image-selected-container").click();
                }else{
                	showToast("Please upload a valid bot icon image", 5000)
                }
            },
            error: function(xhr, textstatus, errorthrown) {
                alert("Unable to load image. Please try after sometime");
                console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
            }
        });
    })
}

function check_welcome_message_validation(welcome_message) {
    var message = "No Error";
    if (welcome_message.trim() == "") {
        message = "Welcome message cannot be empty."
    }

    if (welcome_message.trim().length > character_limit_large_text) {
        message = "Welcome Message is too long."
    }

    return message
}

function check_language_validation() {
    const checked_languages = $(".item-checkbox:checked")

    if (checked_languages.length > 5) {
        return false
    }

    return true
}

function show_bot_url_error(message) {
    $(".create-bot-url-error-message-div")[0].style.display = "block"
    $(".create-bot-url-error-message-div").html(message)
}

function is_faq_url_valid() {
    let url_html = $("#new_bot_faqs_url").val();
    url_html = url_html.trim();

    if (website_faq_added === "Added") {
        return false
    }
    if (url_html == "") {
        show_bot_url_error("Please enter a valid URL")
        return false;
    }
    if (isValidURL(url_html) == false) {
        show_bot_url_error("Please enter a valid URL")
        return false;
    }

    if (!isExternal(url_html)) {
        show_bot_url_error("Internal urls are not allowed.")
        return false;
    }

    $(".create-bot-url-error-message-div")[0].style.display = "none"
    $(".create-bot-url-error-message-div").html("")
    $("#extract_faq").removeClass("create-bot-btn-disable")
    return true
}

$(document).on("keyup", "#new_bot_faqs_url", is_faq_url_valid)

function faq_success_operations(message, addToBot=false, searchAnimation=false, successAnimation=false, loadAnimation=false) {
    $(".create-bot-url-extarct-adding-faqs-message-wrapper")[0].style.display = "block"
    $(".create-bot-url-extarct-adding-faqs-message-wrapper").html(`<span>${message}</span>`)
    $("#extract_faq").addClass("create-bot-btn-disable")
    if (addToBot) {
        $("#add_faq_to_intent").removeClass("create-bot-btn-disable")
    }
    if (loadAnimation) {
        $("#create_newbot_faqs_skip").removeClass("create-bot-btn-disable")
        $("#loading_files_gif")[0].style.display = "none"
    }
    if (searchAnimation) {
        $("#create_newbot_faqs_skip").addClass("create-bot-btn-disable")
        $("#search_error_gif")[0].style.display = "none"
        $("#loading_files_gif")[0].style.display = "inline"
    }
    if (successAnimation) {
        $("#loading_files_gif")[0].style.display = "none"
        $("#upload_files_gif")[0].style.display = "inline"
    }
}

function faq_failure_operations(extractFaq=true, addToBot=false) {
    $(".create-bot-url-extarct-adding-faqs-message-wrapper")[0].style.display = "none"
    $(".create-bot-url-extarct-adding-faqs-message-wrapper").html(null)

    $("#create_newbot_faqs_skip").removeClass("create-bot-btn-disable")
    $("#loading_files_gif")[0].style.display = "none"
    $("#search_error_gif")[0].style.display = "inline"
    
    if (extractFaq) {
        $("#extract_faq").removeClass("create-bot-btn-disable")
    } 
    if (addToBot) {
        $("#add_faq_to_intent").removeClass("create-bot-btn-disable")
    }
}

function reset() {
    $('#new-bot').modal('close');
    $('.modal').on('shown.bs.modal', function (e) {
        $('#modal-general-feedback').find('input:text, input:file, input:password, select, textarea').val('');
        $(this).removeData();
    });
    $('.easychat-custom-create-new-bot-modal').find('input:text, input:file, input:password, select, textarea').val('');
    $(".easychat-custom-create-new-bot-modal").find('input:checkbox').prop('checked', false);
    $("#English-en").prop("checked", true)
    $("#language-box-options-container").removeClass("active")

    update_language_chips()
    for (const elm of $(".easychat-custom-create-new-bot-modal .modal-content")) {
        elm.style.display = "none"
    }
    BOT_ID = ""
    is_faq_extraction_in_progress = false
    if (extraction_timer) {
        clearTimeout(extraction_timer)
    }
    if (extraction_toast_timer) {
        clearTimeout(extraction_toast_timer)
    }
    extraction_timer = null
    extraction_toast_timer = null
    faq_questions = []
    faq_answers = []
    website_faq_added = "Not Added"
    $("#bot-name-error").html("")
    $("#language-dropdown-arrow")[0].style.transform = "translateY(-50%)"
    $("#first-step-bot-cross").addClass("modal-close")
    $("#first-step-bot-cross").removeClass("modal-trigger")
    $("#first-step-bot-cross").removeAttr("data-target")
    $("#upload_files_gif")[0].style.display = "none"
    $("#search_error_gif")[0].style.display = "none"
    $("#loading_files_gif")[0].style.display = "none"
    $("#new_bot_faqs_url").prop("disabled", false)
    $("#channel-one").prop("checked", true)
    $('.step-one-tablinks').removeClass("tab-active");
    $('.step-two-tablinks').removeClass("tab-active");
    $('.step-three-tablinks').removeClass("tab-active");
    $('#bot-name-tab').addClass("tab-active");
    $("#bot-primary-settings-tab").addClass("tab-active")
    $("#primarySettings")[0].style.display = "block"
    $("#addonFeatures")[0].style.display = "none"
    $("#channels")[0].style.display = "block"
    $("#voiceChannel")[0].style.display = "none"
    $("#bot-regular-channel-tab").addClass("tab-active")
    $(".easychat-create-bot-url-btn").addClass("create-bot-btn-disable")
    $("#new_bot_name-char-count")[0].innerHTML = "0"
    $(".create-bot-url-extarct-adding-faqs-message-wrapper")[0].style.display = "none"
    $(".create-bot-url-error-message-div")[0].style.display = "none"
    $("#bot-icon-tab")[0].style["pointer-events"] = "none"
    $('.step-one-tabcontent').show();
    $('#botIcon').hide();
    $("#create_bot_step_one")[0].style.display = "block"
    $("#create_newbot_faqs_skip")[0].style.display = "inline"
    $("#create_newbot_faqs_skip").removeClass("create-bot-btn-disable")
    $("#create_newbot_faqs_next")[0].style.display = "none"
    $("#create_newbot_features_skip")[0].style.display = "inline"
    $("#create_newbot_features_next")[0].style.display = "none"
    $(".easychat-create-bot-icon-item").removeClass("easychat-create-bot-icon-item-active")
    $("#create_newbot_name_next").addClass("create-bot-btn-disable")
    handle_image_cross_btn()
    $("#new_bot_message_welcome").val(default_welcome_message)
    set_character_count($("#new_bot_message_welcome")[0])
    $(".item-checkbox").prop("disabled",false)
    $("#English-en").prop("disabled",true)

}

$(document).on("click", "#create_bot_delete_modal_btn", function (e) {
    var json_string = JSON.stringify({
        bot_id: BOT_ID
    })
    json_string = EncryptVariable(json_string);
    $.ajax({
        url: "/chat/bot/delete/",
        type: "POST",
        headers: {
            "X-CSRFToken": get_csrf_token()
        },
        data: {
            json_string: json_string
        },
        success: function (response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                M.toast({
                    "html": "Bot deleted successfully."
                })
                $('#new-bot').modal('close');
                $('.modal').on('shown.bs.modal', function (e) {
                    $('#modal-general-feedback').find('input:text, input:file, input:password, select, textarea').val('');
                    $(this).removeData();
                });
                reset()
            } else {
                M.toast({
                    "html": "Internal Server Error. Please report this error"
                })
            }
        },
        error: function (error) {
            console.log("Report this error: ", error);
            M.toast({
                "html": "Internal Server Error. Please report this error"
            })
            if (error.status == 403) {
                window.location.href = "/chat/login"
            }
        }
    });
});

$("#add_faq_to_intent").click(function() {

    $("#add_faq_to_intent").addClass("create-bot-btn-disable")
    faq_success_operations("Adding FAQs to your bot...", false, true)

    $.ajax({
        url: "/chat/create-intent-from-faqs/",
        type: "POST",
        data: {
            questions: EncryptVariable(JSON.stringify(faq_questions)),
            answers: EncryptVariable(JSON.stringify(faq_answers)),
            bot_pk: EncryptVariable(JSON.stringify(BOT_ID))
        },

        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                faq_success_operations("Added FAQs to your bot", false, false, true)
                website_faq_added = "Added"
                $("#new_bot_faqs_url").attr("disabled", true)
                $("#create_newbot_faqs_skip")[0].style.display = "none"
                $("#create_newbot_faqs_next")[0].style.display = "inline"
            } else if (response["status"] == 300) {
                M.toast({
                    "html": response.message
                })
                faq_failure_operations(false, true)
            } else {
                M.toast({
                    "html": "Internal Server Error. Please report this error"
                })
                faq_failure_operations(false, true)
            }
        },
        error: function(jqXHR, exception) {
            console.log("Request failed to create intent!", response);
            faq_failure_operations(false, true)
            M.toast({
                html: "Internal Server Error. Please report this error"
            });
        },
    });
}
)

function track_two_minute_bot_extract_faq_progress() {

    var json_string = JSON.stringify({
        bot_id: BOT_ID,
        event_type: 'faq_extraction',
    })

    json_string = EncryptVariable(json_string)
    $.ajax({
        url: "/chat/bot/track-event-progress/",
        type: "POST",
        headers: {
            'X-CSRFToken': get_csrf_token()
        },
        data: {
            data: json_string,
        },
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);

            if (response.status == 200) {
                let is_completed = response.is_completed;
                let is_toast_displayed = response.is_toast_displayed;
                let is_failed = response.is_failed;
                let event_info = response.event_info;
                let failed_message = response.failed_message;
                if (is_failed && !is_toast_displayed) {
                    is_faq_extraction_in_progress = false;
                    if (failed_message == '') failed_message = 'FAQ Extraction Failed'
                    faq_failure_operations()
                    showToast("FAQ Extraction Failed", 2000);
                } else if (is_completed && !is_toast_displayed) {
                    is_faq_extraction_in_progress = false;
                    let faqs = event_info;
                    if (faqs.length > 2) {
                        for (var i = 0; i < faqs.length; i++) {
                            if (faqs[i]["question"].trim() != "") {
                                faqs[i]["question"] = faqs[i]["question"].replace(/<\/?[^>]+(>|$)/g, "");
                                faqs[i]["answer"] = faqs[i]["answer"].replace(/<\/?[^>]+(>|$)/g, "");
                                faq_questions.push(faqs[i]["question"])
                                faq_answers.push(faqs[i]["answer"])
                            }
                        }
                    } else {
                        faq_failure_operations()
                        showToast("Provided URL does not have enough data.", 2000);
                        return
                    }
                    faq_success_operations("FAQs extracted successfully, Click below to add the FAQs to your bot", true, false, false, true)
                    if (extraction_toast_timer) {
                        clearInterval(extraction_toast_timer);
                    }
                    if (extraction_timer) { 
                        clearInterval(extraction_timer);
                    }
                } else if (is_completed && is_toast_displayed){
                    is_faq_extraction_in_progress = false;
                    faq_success_operations("FAQs extracted successfully, Click below to add the FAQs to your bot", true, false, false, true)
                    if (extraction_toast_timer) {
                        clearInterval(extraction_toast_timer);
                    }
                    if (extraction_timer) { 
                        clearInterval(extraction_timer);
                    }
                }
            } else {
                is_faq_extraction_in_progress = false;
                faq_failure_operations()
                if (extraction_toast_timer) {
                    clearInterval(extraction_toast_timer);
                }
                if (extraction_timer) { 
                    clearInterval(extraction_timer);
                }
                showToast("FAQ Extraction Failed", 2000);
            }
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
            faq_failure_operations()
            is_faq_extraction_in_progress = false;
            showToast("FAQ Extraction Failed", 2000);
        }
    });
}

$("#extract_faq").click(function() {
    if (is_faq_extraction_in_progress) {
        showToast("FAQ Extraction is already in process!", 2000);
        return;
    }
    let url_html = $("#new_bot_faqs_url").val();
    url_html = url_html.trim();
    
    if (!is_faq_url_valid()) {
        return
    }

    let json_string = JSON.stringify({
        url_html: url_html,
        bot_pk: BOT_ID,
    })
    json_string = EncryptVariable(json_string);

    faq_success_operations("Extracting FAQs...", false, true)

    $.ajax({
        url: "/chat/fetch-faqs/",
        type: "POST",
        headers: {
            'X-CSRFToken': get_csrf_token(),
        },
        data: {
            json_string: json_string
        },
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if(response["status"] == 200) {
                is_faq_extraction_in_progress = true;
                extraction_timer = setInterval(track_two_minute_bot_extract_faq_progress, 5000);
                extraction_toast_timer = setInterval(function () {
                    showToast("FAQ Extraction is taking longer than expected. Please wait.")
                }, 30000)

            }  else {
                is_faq_extraction_in_progress = false;
                faq_failure_operations()
                showToast("Unable to extract FAQ. Please try after some time.", 2000);
            }
        },
        error: function(jqXHR, exception) {
            is_faq_extraction_in_progress = false;
            faq_failure_operations()
            showToast("Unable to connect to server. Please try again later.", 2000);
        },
    });
});

function update_channel_urls() {
    all_channel_atags = $(".create-bot-channel-advance-setting-btn")
    for (const channel of all_channel_atags) {
        const href = `/chat/channels/${channel.id}/?id=${BOT_ID}`
        channel.href = href
        channel.target = "_blank"
    }
}

function update_bot_config() {
    const welcome_message = $("#new_bot_message_welcome").val()
    const is_nps_required = $("#enable_csat")[0].checked
    const checked_languages_elms = $(".item-checkbox:checked")
    let is_enable_live_chat = $("#enable_live_chat")[0]
    is_enable_live_chat = is_enable_live_chat ? is_enable_live_chat.checked : false
    let is_enable_co_browse = $("#enable_co_browse")[0]
    is_enable_co_browse = is_enable_co_browse ? is_enable_co_browse.checked : false
    let is_enable_ticket_management = $("#enable_ticket_management")[0]
    is_enable_ticket_management = is_enable_ticket_management ? is_enable_ticket_management.checked : false
    const is_enable_pdf_searcher = $("#enable_pdf_searcher")[0].checked
    let is_enable_easy_search = $("#enable_easy_search")[0]
    is_enable_easy_search = is_enable_easy_search ? is_enable_easy_search.checked : false
    const is_enable_lead_generation = $("#enable_lead_generation")[0].checked

    const selected_languages = []
    for (const language of checked_languages_elms) {
        selected_languages.push(language.value)
    }

    let json_string = JSON.stringify({
        bot_id: BOT_ID,
        welcome_message,
        selected_languages,
        is_nps_required,
        is_enable_live_chat,
        is_enable_co_browse,
        is_enable_ticket_management,
        is_enable_pdf_searcher,
        is_enable_easy_search,
        is_enable_lead_generation
    })

    json_string = EncryptVariable(json_string);

    $("#create_bot_loader_header_animation").html("Adding configurations for your bot...")
    $(".create-bot-loader-div")[0].style.display = "flex"

    $.ajax({
        url: "/chat/two-minute-bot/update-config",
        type: "POST",
        headers: {
            'X-CSRFToken': get_csrf_token(),
        },
        data: {
            data: json_string
        },
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            $(".create-bot-loader-div")[0].style.display = "none"

            if (response.status === 200) {
                $('#create_bot_step_two').hide();
                $('#create_bot_step_three').show();
            }
            else if (response.status === 400 || response.status === 102 || response.status === 402) {
                M.toast({
                    html: response.msg
                })
            } else {
                M.toast({
                    html: "Please check if inputs are valid."
                })
            }
        },
        error: function(error) {
            $(".create-bot-loader-div")[0].style.display = "none"
            M.toast({
                html: "Internal Server Error. Please report this error."
            })
            console.log("Report this error: ", error)
        }
    })
}

$(document).on("change", "#language-box-options-container", function(event) {
    const checked_languages = $(".item-checkbox:checked")
    const unchecked_languages = $(".item-checkbox:not(:checked)")
    if (checked_languages.length === 5) {
        for (const language of unchecked_languages) {
            language.disabled = true
        }
    } else {
        for (const language of unchecked_languages) {
            language.disabled = false
        }
    }
})

$(document).on("keyup", "#new_bot_message_welcome", function(event) {
    set_character_count(event.target)
})

$(document).on("click", "#create_newbot_icon_next", function (e) {
    const bot_img_elm = $(".easychat-create-bot-icon-item-active img")[0]
    let bot_name = $("#new_bot_name").val();
    let bot_img_url = bot_img_elm.src

    if (bot_img_elm.alt === "bot-image-default-1") {
        bot_img_url = "/static/EasyChatApp/img/popup-4.gif"
    }

    if (bot_img_url.trim() == "") {
        M.toast({
            "html": "Bot Image URL is invalid!"
        }, 2000);
        return;
    }

    if (bot_name.trim() == "") {
        M.toast({
            "html": "Bot Name cannot be empty"
        }, 2000);
        return;
    }

    if (bot_name.length > 18) {
        M.toast({
            "html": "Max characters allowed - 18"
        }, 2000);
        return;
    }

    var format = /[`@#$%^*()_+\-=\[\]{};':"\\|,.<>\/~]/;
    if (format.test(bot_name.trim())) {
        M.toast({
            "html": "Invalid Bot Name(Only alphabets, 0-9, ?, !, & are allowed)"
        }, 2000);
        return;
    }

    let check_special_character_string = bot_name.trim().replace(/[&\/\\#,+()$~%.'":*?<>{}!@ ]/g, '');

    let check_emoji_only_string = check_special_character_string.replace(/^(?:[\u2700-\u27bf]|(?:\ud83c[\udde6-\uddff]){2}|[\ud800-\udbff][\udc00-\udfff]|[\u0023-\u0039]\ufe0f?\u20e3|\u3299|\u3297|\u303d|\u3030|\u24c2|\ud83c[\udd70-\udd71]|\ud83c[\udd7e-\udd7f]|\ud83c\udd8e|\ud83c[\udd91-\udd9a]|\ud83c[\udde6-\uddff]|[\ud83c[\ude01-\ude02]|\ud83c\ude1a|\ud83c\ude2f|[\ud83c[\ude32-\ude3a]|[\ud83c[\ude50-\ude51]|\u203c|\u2049|[\u25aa-\u25ab]|\u25b6|\u25c0|[\u25fb-\u25fe]|\u00a9|\u00ae|\u2122|\u2139|\ud83c\udc04|[\u2600-\u26FF]|\u2b05|\u2b06|\u2b07|\u2b1b|\u2b1c|\u2b50|\u2b55|\u231a|\u231b|\u2328|\u23cf|[\u23e9-\u23f3]|[\u23f8-\u23fa]|\ud83c\udccf|\u2934|\u2935|[\u2190-\u21ff])+$/, '');
    if (check_emoji_only_string == '') {
        M.toast({
            "html": "Bot name should have atleast one alphanumeric character."
        }, 2000);
        return;
    }
    var json_string = JSON.stringify({
        bot_id: BOT_ID,
        bot_name: bot_name.trim(),
        bot_image: bot_img_url
    })

    json_string = EncryptVariable(json_string);

    $("#create_bot_loader_header_animation").html("Creating bot for you...")
    $(".create-bot-loader-div")[0].style.display = "flex"

    $.ajax({
        url: "/chat/two-minute-bot/create/",
        type: "POST",
        headers: {
            'X-CSRFToken': get_csrf_token(),
        },
        data: {
            json_string: json_string
        },
        success: function (response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            BOT_ID = response.bot_id ? response.bot_id : ""
            update_channel_urls()
            if (response["status"] == 200) {
                $('#create_bot_step_one').hide();
                $('#create_bot_step_two').show();
                $("#first-step-bot-cross").removeClass("modal-close")
                $("#first-step-bot-cross").addClass("modal-trigger")
                $("#first-step-bot-cross").attr("data-target", "easychat_bot_create_delete_modal")
            } else if (response["status"] == 300) {
                M.toast({
                    "html": "You have reached the limit for number of bots that you can create."
                }, 2000);
            } else if (response["status"] == 302) {
                M.toast({
                    "html": "Please enter a valid bot name."
                }, 2000);
            } else if (response["status"] == 303) {
                M.toast({
                    "html": "Please provide a valid bot image."
                }, 2000);
            }else if (response['status'] == 400) {
                M.toast({
                    "html": "Bot with same name already exists. Please choose different name"
                }, 3000);
            } else if (response["status"] == 401) {
                M.toast({
                    "html": "You have permission to create only one bot."
                }, 2000);
            } else {
                M.toast({
                    "html": "Internal Server Error. Please report this error"
                });
            }
            $(".create-bot-loader-div")[0].style.display = "none"
        },
        error: function (error) {
            $(".create-bot-loader-div")[0].style.display = "none"
            console.log("Report this error: ", error);
            M.toast({
                "html": "Internal Server Error. Please report this error"
            }, 2000);
        }
    });

});

document.getElementById('drag-drop-input-box').addEventListener('change', function(element) {

    const file = element.target.files[0];
    const reader = new FileReader();

    reader.readAsDataURL(file);

    reader.onload = function() {

        base64_str = reader.result.split(",")[1];

        const uploaded_file = [];
        uploaded_file.push({
            "filename": file.name,
            "base64_file": base64_str
        });

        upload_details_over_server(element, uploaded_file);
    };

    reader.onerror = function(error) {
        console.log('Error: ', error);
    };

})

function handle_image_cross_btn(e) {

    $("#upload-icon-section .easychat-bot-icon-upload-div").show();
    $('#upload-icon-section #image-selected-container').hide();


    $("#upload-icon-section #image-selected-container").html("");
    $("#upload-icon-section #drag-drop-input-box").val("");

    setTimeout(function () {

        $("#create_newbot_icon_next").addClass('create-bot-btn-disable');


    }, 100);



}
$('#create_newbot_name_next').click(validate_bot_name)
$('#bot-icon-tab').click(validate_bot_name)

function validate_bot_name (e) {
    let bot_name = $("#new_bot_name").val();

    if (bot_name.trim() == "") {
        $("#bot-name-error").html("Bot Name cannot be empty")
        return
    }

    if (bot_name.length > 18) {
        $("#bot-name-error").html("Maximum characters allowed - 18")
        return;
    }

    var format = /[`@#$%^*()_+\-=\[\]{};':"\\|,.<>\/~]/;
    if (format.test(bot_name.trim())) {
        $("#bot-name-error").html("Invalid Bot Name(Only alphabets, 0-9, ?, !, & are allowed)")
        return;
    }

    let check_emoji_only_string = remove_special_and_emoji_chars(bot_name)
    
    if (check_emoji_only_string == '') {
        $("#bot-name-error").html("Bot name should have atleast one alphanumeric character.")
        return;
    }
    var json_string = JSON.stringify({
        bot_name: bot_name.trim(),
        bot_id: BOT_ID
    })

    json_string = EncryptVariable(json_string);

    $.ajax({
        url: "/chat/two-minute-bot/bot-name-validate/",
        type: "POST",
        headers: {
            'X-CSRFToken': get_csrf_token(),
        },
        data: {
            json_string: json_string
        },
        success: function (response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                $('.step-one-tablinks').removeClass("tab-active");
                $('#bot-icon-tab').addClass("tab-active");

                $('.step-one-tabcontent').hide();
                $('#botIcon').show();
            } else if (response["status"] == 302) {
                $("#bot-name-error").html("Please enter a valid bot name.")
            }else if (response['status'] == 400) {
                $("#bot-name-error").html("Bot with same name already exists. Please choose different name.")
            } else {
                M.toast({
                    "html": "Internal Server Error. Please report this error."
                });
            }
            $(".create-bot-loader-div")[0].style.display = "none"
        },
        error: function (error) {
            console.log("Report this error: ", error);
            M.toast({
                "html": "Internal Server Error. Please report this error"
            }, 2000);
            $(".create-bot-loader-div")[0].style.display = "none"
        }
    });

};

$('#create_bot_step_two_back_arrow').click(function (e) {

    $("#language-box-options-container").removeClass("active")
    $("#language-dropdown-arrow")[0].style.transform = "translateY(-50%)"
    update_language_chips()

    $('#create_bot_step_one').show();
    $('#create_bot_step_two').hide();

});

$('#create_bot_step_three_back_arrow').click(function (e) {

    $('#create_bot_step_two').show();
    $('#create_bot_step_three').hide();

});

$('#create_bot_step_four_back_arrow').click(function (e) {

    $('#create_bot_step_three').show();
    $('#create_bot_step_four').hide();

});

$('#create_bot_step_five_back_arrow').click(function (e) {

    $('#create_bot_step_four').show();
    $('#create_bot_step_five').hide();

});

$('#create_newbot_settings_next').click(function (e) {

    const welcome_msg = $("#new_bot_message_welcome").val()
    const checked_languages_elms = $(".item-checkbox:checked")

    const message = check_welcome_message_validation(welcome_msg)
    if (message !== "No Error") {
        M.toast({
            html: message
        })
        return
    }

    const language_validate = check_language_validation()
    if (!language_validate) {
        M.toast({
            html: "Maximum 5 languages can be selected from the list"
        })
        return
    }

    $('.step-two-tablinks').removeClass("tab-active");
    $('#bot-addon-features-tab').addClass("tab-active");

    $('.step-two-tabcontent').hide();
    $('#addonFeatures').show();

});

$('#create_newbot_channels_next').click(function (e) {

    $('.step-three-tablinks').removeClass("tab-active");
    $('#bot-voice-channel-tab').addClass("tab-active");

    $('.step-three-tabcontent').hide();
    $('#voiceChannel').show();

});

$("#addonFeatures input").on("change", function (event) {
    if ($('#addonFeatures input[type="checkbox"]:checked').length > 0) {
        $("#create_newbot_features_skip").hide();
        $('#create_newbot_features_next').show();


    } else {
        $('#create_newbot_features_skip').show();
        $("#create_newbot_features_next").hide();


    }
});
$(document).click(function() {
    const optionsContainer = document.querySelector("#language-box-options-container");
    const searchBox = document.querySelector(".search-box input");
    const dropArrow = document.querySelector("#language-dropdown-arrow");
    optionsContainer.classList.remove("active");

    dropArrow.style.transform = "translateY(-50%) rotate(0deg)";
    update_language_chips()
    document.getElementById("language-options-search-box").style.display = "none";

    searchBox.value = "";
    filterList("");
  }); 
$('.select-box').click(function (event) {event.stopPropagation();});


$('#create_newbot_voice_channel_next').click(function (e) {

    $("#create_bot_loader_header_animation").html("Adding configurations for your bot...")
    $(".create-bot-loader-div")[0].style.display = "flex"
    
    const checked_languages_elms = $(".item-checkbox:checked")
    const selected_languages = []
    for (const language of checked_languages_elms) {
        selected_languages.push(language.value)
    }
    
    const selectedChannelElms = $('input[name=create-bot-channel-btn]:checked~label')
    var channels_added = []
    for (const channel of selectedChannelElms) {
        channels_added.push(channel.id);
    }

    var json_string = JSON.stringify({
        bot_id: BOT_ID,
        channels_added: channels_added,
        selected_languages, selected_languages
    })
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: "/chat/two-minute-bot/update-language/",
        type: "POST",
        headers: {
            'X-CSRFToken': get_csrf_token(),
        },
        data: {
            json_string: json_string
        },
        success: function (response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);

            if (response["status"] == 200) {
                $('#create_bot_step_three').hide();
                $('#create_bot_step_four').show();
            } else if (response["status"] == 401) {
                M.toast({
                    "html": response["message"]
                }, 2000)
            } else {
                M.toast({
                    "html": "Internal Server Error. Please report this error."
                });
            }
        $(".create-bot-loader-div")[0].style.display = "none"
        },
        error: function (error) {
            console.log("Report this error: ", error);
            M.toast({
                "html": "Internal Server Error. Please report this error"
            }, 2000);
            $(".create-bot-loader-div")[0].style.display = "none"
        }
    });
    
});

$('.create-bot-step-four-action-btns').click(function (e) {

    // $("#create_bot_loader_header_animation").html("We are almost there...")
    // $(".create-bot-loader-div")[0].style.display = "flex"

    createPreview()
    $('#create_bot_step_four').hide();
    $('#create_bot_step_five').show();

});

$('#create_newbot_preview_build_btn').click(function (e) {

    // $("#create_bot_loader_header_animation").html("Creating bot for you....")
    // $(".create-bot-loader-div")[0].style.display = "flex"

    $("#view_bot")[0].href = `/chat/bot/?id=${BOT_ID}`
    $("#add_skills")[0].href = `/chat/intent?bot_pk=${BOT_ID}&selected_language=en`
    $('#create_bot_step_five').hide();
    $('#create_bot_final_step').show();

});

function modal_close() {
    setTimeout(function () {
        $(".modal-overlay").click(function () {
            if ($('#create_bot_final_step')[0].style.display !== "none") {
                $('#new-bot').modal('close');
                window.location.reload()
            }
        })
    }, 100)
}

// language js
function update_language_chips() {

    const selected = document.querySelector(".selected");
    let is_any_language_checked = false
    let count = 0;
    selected.innerHTML = ""
    var checked_list = $(".item-checkbox:checked")
    for (let i = 0; i < checked_list.length; i++) {
        is_any_language_checked = true
        count++;
        if (count > 5 && to_add_diffrentiator)
            break;
        make_slected_language_span_chips(checked_list[i].id, checked_list[i].name)
    }
    if (count > 5 && to_add_diffrentiator) {
        var btn = document.createElement("BUTTON");
        btn.innerText = "+" + String(checked_list.length - 5);
        btn.id = "languages-extend-button"
        selected.appendChild(btn);
        add_language_extend_button_event_listner();
    }
    if (!is_any_language_checked)
        selected.innerHTML = "Select Language";
}
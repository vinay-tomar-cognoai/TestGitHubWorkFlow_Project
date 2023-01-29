//////////////////////////////////  language configuration event listners /////////////////////////
var selected_language = ""
var action_performed = ""
var is_edit_language_called = false
var INPUT_LARGE_TEXT_LIMIT = 2000
var INPUT_SMALL_TEXT_LIMIT = 50

// $(".easychat-language-config-edit-btn").click(function() {

//     $(this).parent().toggleClass("edit-language-config-active");

// });

$('#language_config_select_new_lang_dropdown').select2().on('select2:open', function (e) {
    $('.select2-search__field').attr('placeholder', 'Search Language');
})

$(".easychat-lang-config-otp-input").on("keypress", function (e) {
    let key_index = false;
    key_index = on_otp_form_keypress(e);
    return key_index;
});

$(".easychat-lang-config-otp-input").on("keyup", function (e) {
    on_otp_form_keyup(e);
    var key = event.keyCode || event.charCode;
    if (key == 8 || key == 46) {
        $(e.target).prev().focus();
    }
});

$(document).ready(function () {

    setTimeout(function () {
        $('#language_config_select_new_lang_dropdown').select2({
            dropdownParent: $('#language_config_select_new_lang_dropdown_container')
        });

        $('#easychat_language_config_email_verify_modal').modal({
            dismissible: false
        });
        $('#easychat_language_config_otp_verify_modal').modal({
            dismissible: false
        });
        $('#easychat_language_config_delete_lang_modal').modal({
            dismissible: false
        });
        $('#easychat_language_config_add_new_modal').modal({
            dismissible: false
        });

        $('.modal').removeAttr("tabindex")

    }, 2000)


})


function handle_action_type_change(element) {


    if (element.value == "none") {
        return
    }
    document.getElementById("language_config_select_new_lang_dropdown").disabled = true;
    document.getElementById("configure-constant-keywords-save-button").style.pointerEvents = "none";
    $('#easychat_language_configure_constant_keywords_container').hide();
    $("#language-template-object-loader").show();
    selected_language = element.value
    show_language_constant_keywords(element.value);

}

function on_otp_form_keypress(event) {
    let keys = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"];
    return keys.indexOf(event.key) > -1;
}

function on_otp_form_keyup(e) {
    let keys = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"];
    if (keys.indexOf(e.target.value) != -1) {
        $(e.target).next().focus();
    }
}

function handle_toast_close() {

    $('#easychat_language_config_success_toast_container').hide();

}

function handle_edit_language_change(language_id) {

    let curr_language = language_id.split("-")[1]

    document.getElementById(language_id).selected = true;

    $('#language_config_select_new_lang_dropdown').trigger('change');

    document.getElementById("language_config_select_new_lang_dropdown").disabled = true;

    $("#easychat_language_config_add_new_modal").modal('open');

    action_performed = "edit_language_keywords"

    is_edit_language_called = true
}

function keyPressFilter(event) {
    
    var regex = new RegExp("^[a-zA-Z0-9!?& ]+$"); // your regex

    var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);

    if (!regex.test(key)) {

       event.preventDefault();

       return false;

    }

};

function pasteFilter(event) {
    var format = /[`@#$%^*()_+\-=\[\]{};':"\\|,.<>\/~]/;
    clipboardData = event.clipboardData || window.clipboardData;
    pastedData = clipboardData.getData('Text');

    if(format.test(pastedData.trim()))
    {
      event.preventDefault();

       return false;

    }

};

function create_constant_keywords_table(constant_keywords_dict) {

    table_body = document.getElementById("easychat_language_configure_constant_keywords_table_body")

    const keys = Object.keys(constant_keywords_dict);
    var tooltip_text = '<sup><i class="material-icons inline-icon tooltipped constant-keyword-tooltip" data-position="top" data-tooltip="Separate different options by placing $$$ signs between them.">help</i></sup>'

    html = ""
    keys.forEach((key, index) => {

        heading = key.replaceAll("_", " ")
        value = constant_keywords_dict[key]
        items = value.split("$$$")
        if (key === "bot_name") {
            html += "<tr><td><div class='language-configure-constant-keywords-subheading-text'>" + heading + " (Max: 18 Chars)" + "</div></td>\
            <td><input onkeypress='keyPressFilter(event)' onpaste='pasteFilter(event)' maxlength='"+ "18" + "' id='" + key + "' type='text' class='language-configure-constant-keywords-input' value='" + value + "' placeholder='Type here'>" +
            "</td></tr>"
        }
        else if (items.length > 1) {
            html += "<tr><td><div class='language-configure-constant-keywords-subheading-text'>" + heading + tooltip_text + "</div></td>\
                    <td><textarea style=' overflow: hidden; resize: none' wrap='off' maxlength='"+ INPUT_LARGE_TEXT_LIMIT + "'  id='" + key + "' type='text' class='language-configure-constant-keywords-input' placeholder='Type here'>" + value + "</textarea></td>\
                 </tr>"
        } else {
            tooltip_text = ""
            var text_limit = INPUT_LARGE_TEXT_LIMIT
            if (key == "powered_by_text") {
                tooltip_text = '<sup><i class="material-icons inline-icon tooltipped constant-keyword-tooltip" data-position="top" data-tooltip="Only first 50 characters will be shown as powered by text.">help</i></sup>'
                text_limit = INPUT_SMALL_TEXT_LIMIT
            }

            html += "<tr><td><div class='language-configure-constant-keywords-subheading-text'>" + heading + tooltip_text + "</div></td>\
                    <td><input maxlength='"+ text_limit + "' id='" + key + "' type='text' class='language-configure-constant-keywords-input' value='" + value + "' placeholder='Type here'></td>\
                 </tr>"
        }

    });

    table_body.innerHTML = html;

    $(".constant-keyword-tooltip").tooltip();



}

function show_language_constant_keywords(selected_language) {

    let bot_id = window.location.pathname.split("/")[4];
    json_string = {
        bot_id: bot_id,
        selected_language: selected_language
    }
    json_string = JSON.stringify(json_string);
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: "/chat/get-language-constant-keywords/",
        type: "POST",
        data: {
            json_string: json_string
        },
        success: function (response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {

                constant_keywords_dict = response["constant_keywords_dict"]

                create_constant_keywords_table(constant_keywords_dict)

                $("#language-template-object-loader").hide()
                $('#easychat_language_configure_constant_keywords_container').show();
                document.getElementById("configure-constant-keywords-save-button").style.pointerEvents = "auto";
                if (!is_edit_language_called) {
                    document.getElementById("language_config_select_new_lang_dropdown").disabled = false;
                }

            } else if (response["status"] == 400 || response["status"] == 102) {

                M.toast({
                    "html": response["message"]
                }, 2000)
            } else {
                M.toast({
                    "html": "Something went wrong, Please refresh and try again"
                })
            }
        },
        error: function (error) {
            console.log("Report this error: ", error);
        },
    });


}

function reset_add_langauge_modal() {

    document.getElementById("language_config_select_new_lang_dropdown").disabled = false;
    document.getElementById("configure-constant-keywords-save-button").style.pointerEvents = "auto";
    $('#easychat_language_configure_constant_keywords_container').hide();
    $('#language_config_select_new_lang_dropdown').val('none').trigger('change');
    $("#language-template-object-loader").hide();

}

function handle_add_new_language() {

    document.getElementById("language_config_select_new_lang_dropdown").disabled = false;
    document.getElementById("configure-constant-keywords-save-button").style.pointerEvents = "auto";
    is_edit_language_called = false

    $("#easychat_language_config_add_new_modal").modal('open');

    $('#language_config_select_new_lang_dropdown').val('none').trigger('change');

    $('#easychat_language_configure_constant_keywords_container').hide();

    action_performed = "add_language"

}

function get_dict_of_constant_keywords() {
    let constant_keywords_inputs = document.querySelectorAll(".language-configure-constant-keywords-input");

    if (constant_keywords_inputs == null) {
        return
    }
    keywords_dict = {}

    for (let i = 0; i < constant_keywords_inputs.length; i++) {
        key = constant_keywords_inputs[i].id
        value = constant_keywords_inputs[i].value
        keywords_dict[key] = value

    }

    return keywords_dict;
}

function handle_delete_language(language) {

    selected_language = language

    if (selected_language == "en") {
        M.toast({
            "html": "Can not Delete Default language"
        })
        return
    }
    $("#easychat_language_config_delete_lang_modal").modal('open');

}

function hide_edit_and_show_delete_validate_button() {
    document.getElementById("delete-selected-language-validate-button").style.display = "block";
    document.getElementById("edit-selected-language-validate-button").style.display = "none";
}

function hide_delete_and_show_edit_validate_button() {
    document.getElementById("delete-selected-language-validate-button").style.display = "none";
    document.getElementById("edit-selected-language-validate-button").style.display = "block";
}

function handle_delete_confirmation() {

    // hide_edit_and_show_delete_validate_button();

    // $("#easychat_language_config_email_verify_modal").modal('open');
    // $("#easychat_language_config_modal").modal('close')

    delete_selected_language_from_configuration()

    action_performed = "delete_language"
}

function save_language_configuration_constant_keywords() {
    selected_language = $('#language_config_select_new_lang_dropdown').val();

    if (selected_language == null || selected_language == "none") {
        showToast('Please Select A Language to Add', 2000);
        return
    }
    document.getElementById("configure-constant-keywords-save-button").innerText = "Saving..."

    update_language_constant_keywords(selected_language)

    // $("#easychat_language_config_add_new_modal").modal('close');

    // $("#easychat_language_config_email_verify_modal").modal('open');

}

function delete_selected_language_from_configuration() {

    // update_validate_button_inner_text("Verifying")
    let bot_id = window.location.pathname.split("/")[4];

    // let email_id = $("#easychat-language-configuration-email-id").val()
    // let entered_otp = get_entered_otp();

    // if (entered_otp == "" || entered_otp.length < 6) {
    //     showToast('Please enter otp before submitting.', 2000);
    //     return ;
    // }

    json_string = {
        bot_id: bot_id,
        selected_language: selected_language,
        // email_id:email_id,
        // entered_otp:entered_otp,
    }
    json_string = JSON.stringify(json_string);
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: "/chat/delete-language-from-supported-languages/",
        type: "POST",
        data: {
            json_string: json_string
        },
        success: function (response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {


                // $('#easychat_language_config_success_toast_container').show();
                showToast("Language Deleted Succesfully")
                // $("#easychat_language_config_otp_verify_modal").modal('close');
                $('#easychat_language_config_delete_lang_modal').modal('close')
                $('#easychat_language_config_modal').modal('close')
                setTimeout(function () {
                    window.location.reload();
                }, 3000);

            } else if (response["status"] == 400) {

                $("#easychat-otp-failed-message-box").show()
                $("#easychat-otp-success-message-box").hide()

            } else {
                M.toast({
                    "html": "Unable To Delete This Language. Please Refresh And Try Again Later"
                })
            }
        },
        error: function (error) {
            console.log("Report this error: ", error);
        },
    });
    // update_validate_button_inner_text("Validate")
}

function get_entered_otp() {

    var entered_otp_inputs = document.getElementsByClassName('easychat-lang-config-otp-input');

    var entered_otp = "";
    for (otp_input of entered_otp_inputs) {
        entered_otp += otp_input.value;
    }

    return entered_otp
}


function update_language_constant_keywords(selected_language) {

    // update_validate_button_inner_text("Verifying")
    let bot_id = window.location.pathname.split("/")[4];
    let constant_keywords_dict = get_dict_of_constant_keywords();
    // let email_id = $("#easychat-language-configuration-email-id").val()
    // let entered_otp = get_entered_otp();

    // if (entered_otp == "" || entered_otp.length < 6) {
    //     showToast('Please enter otp before submitting.', 2000);
    //     return ;
    // }

    json_string = {
        bot_id: bot_id,
        selected_language: selected_language,
        constant_keywords_dict: constant_keywords_dict,
        // email_id:email_id,
        // entered_otp:entered_otp,
    }
    json_string = JSON.stringify(json_string);
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: "/chat/update-language-constant-keywords/",
        type: "POST",
        data: {
            json_string: json_string
        },
        success: function (response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {

                document.getElementById("configure-constant-keywords-save-button").innerText = "Save"
                $('#easychat_language_config_success_toast_container').show();
                // $("#easychat_language_config_otp_verify_modal").modal('close');
                $('#easychat_language_config_add_new_modal').modal('close')
                setTimeout(function () {
                    window.location.reload();
                }, 6000);
            } else if (response["status"] == 400) {
                $("#easychat-otp-failed-message-box").show()
                $("#easychat-otp-success-message-box").hide()

            } else {
                M.toast({
                    "html": "Something went wrong, Please refresh and try again"
                })
            }
        },
        error: function (error) {
            console.log("Report this error: ", error);
        },
    });

    // update_validate_button_inner_text("Validate")
}

function show_send_otp_modal() {

    let email_id = $("#easychat-language-configuration-email-id").val()

    if (!check_is_email_valid_of_staff(email_id)) {
        $(".easychat-email-otp-failed-message-box").show()
        return;
    } else {
        $(".easychat-email-otp-failed-message-box").hide()
    }

    send_otp_for_lanague_configuration();

    $("#easychat_language_config_email_verify_modal").modal("close");

    $("#easychat-otp-success-message-box").hide()
    $("#easychat-otp-failed-message-box").hide()

    $("#easychat_language_config_otp_verify_modal").modal("open");

    empty_user_otp_input();


}

function empty_user_otp_input() {
    $(".easychat-lang-config-otp-input").val("");
    $(".easychat-lang-config-otp-input:first").focus()
}

function check_is_email_valid_of_staff(email_id) {

    if (!validateEmailAddr(email_id)) {
        return false
    }

    return email_id.endsWith("@getcogno.ai")

}

function update_validate_button_inner_text(text) {

    edit_button = document.getElementById("edit-selected-language-validate-button")
    delete_button = document.getElementById("delete-selected-language-validate-button")

    if (edit_button.style.display == "block") {
        edit_button.innerHTML = text
    } else {
        delete_button.innerHTML = text
    }
}

function send_otp_for_lanague_configuration() {

    let bot_id = window.location.pathname.split("/")[4];
    let email_id = $("#easychat-language-configuration-email-id").val()

    $("#language-configuration-email-confirmation-display").html(email_id)

    json_string = {
        bot_id: bot_id,
        selected_language: selected_language,
        email_id: email_id,
        action_performed: action_performed,
    }
    json_string = JSON.stringify(json_string);
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: "/chat/send-otp-for-language-configuration/",
        type: "POST",
        data: {
            json_string: json_string
        },
        success: function (response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {

                $("#easychat-otp-success-message-box").show()

            } else if (response["status"] == 400) {

                showToast(response["message"])
            } else {

                showToast("Something went wrong, Please refresh and try again")
            }
        },
        error: function (error) {
            console.log("Report this error: ", error);
        },
    });

}

/* NLP Configurations */
$(document).ready(function () {
    $("#easychat-bot-intent-threshold").ionRangeSlider({
        min: 0,
        max: 1,
        step: 0.01
    });
    $("#checkbox_bot_level_advance_nlp_cb").on("change", function (event) {
        if (this.checked) {
            $("#easychat_threshold_value_range_container").show();

        } else {
            $('#easychat_threshold_value_range_container').hide();


        }
    });

    initialise_profanity_response_modal();

    $("#enable-do-not-translate").on("change", function(event) {
        if (this.checked) {
            $("#dont_translate_keyword_enable_wrapper").show();
        } else {
            $('#dont_translate_keyword_enable_wrapper').hide();
        }
    });

    $("#enable-do-not-translate").change();
    update_do_not_translate_containers();

    var add_keyword_inputs = document.getElementsByClassName("add-keyword-input-div");
    var keyword_value = "";
    var words_container = null;
    var html = "";

    for (var i=0; i<add_keyword_inputs.length; i++) {
        add_keyword_inputs[i].onkeyup = function (evt) {
            if (evt.keyCode == 13) {
                keyword_value = evt.target.value.trim();
                if (!keyword_value) {
                    if (evt.target.id == "add-no-translate-keyword") {
                        showToast("Please enter valid keyword and then press enter.");
                    } else {
                        showToast("Please enter valid regex and then press enter.");
                    }
                    return;
                }

                if (evt.target.id == "add-no-translate-keyword") {
                    words_container = document.getElementById("keywords-container");
                    for (var i=0; i<words_container.children.length; i++) {
                        if (words_container.children[i].getAttribute("value").toLowerCase().includes(keyword_value.toLowerCase())) {
                            showToast("Keyword already exists. Please enter valid keyword and then press enter.");
                            evt.target.value = "";
                            return;
                        } 
                    }
                } else {
                    words_container = document.getElementById("regex-container");
                    for (var i=0; i<words_container.children.length; i++) {
                        if (words_container.children[i].getAttribute("value").includes(keyword_value)) {
                            showToast("Regex already exists. Please enter valid keyword and then press enter.");
                            evt.target.value = "";
                            return;
                        } 
                    }
                }

                html = `<div class="translate-keyword-chip-item" value="` + keyword_value + `">
                    <span>` + keyword_value + `</span>
                    <a onclick="remove_keywords_chip(this)">
                        <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M2.3938 2.25L9.60619 9.75" stroke="white" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"></path>
                        <path d="M9.6062 2.25L2.39381 9.75" stroke="white" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"></path>
                        </svg>
                    </a>
                </div>`

                words_container.insertAdjacentHTML("beforeend", html);
                evt.target.value = "";

                update_do_not_translate_containers();
            }
        }
    }

});

function initialise_profanity_response_modal() {

    let profanity_response_text = $("#profanity-word-bot-response").val()

    $("#profanity-word-bot-response").trumbowyg({
        tagsToKeep: [],
        defaultLinkTarget: '_blank',
        allowTagsFromPaste: {
            allowedTags: ['h4', 'p', 'br']
        },
        minimalLinks: true,
        btns: [
            // ['viewHTML'],
            ['strong', 'em'],
            ['link'],
            ['unorderedList', 'orderedList'],
            ['underline'],
            ['emoji'],
        ],
    }).on('tbwinit', function () {
        $('#profanity-word-bot-response').trumbowyg('html', profanity_response_text);
    });
}

/* NLP Configurations ends */

$(document).on("click", "#livechat-profanity-words-enable", function (e) {
    if (document.getElementById("livechat-profanity-words-enable").checked) {
        document.getElementById("configure-profanity-setting").style.display = ""
    } else {
        document.getElementById("configure-profanity-setting").style.display = "none"
    }
});


function show_developer_form() {
    if (document.getElementById("easychat-checkbox-livechat-enable").checked == true) {
        document.getElementById("livechat-developers-options-form").style.display = "table-row"
        document.getElementById("livechat-developers-options-processor-customer").style.display = "table-row"
        document.getElementById("livechat-developers-options-processor-end-chat").style.display = "table-row"
        $(".emoji-checkbox-container").css("display", "");
        $("#trigger_livechat_profanity_words_wrapper").css("display", "table-row");


    } else {
        document.getElementById("livechat-developers-options-form").style.display = "none"
        document.getElementById("livechat-developers-options-processor-customer").style.display = "none"
        document.getElementById("livechat-developers-options-processor-end-chat").style.display = "none"
        $(".emoji-checkbox-container").css("display", "none");
        $("#trigger_livechat_profanity_words_wrapper").css("display", "none");

    }

}


function check_profanity_model_settings() {

    profanity_word_bot_response = $("#profanity-word-bot-response").trumbowyg('html');

    profanity_word_bot_response = validate_ck_editor_response(profanity_word_bot_response)


    if (profanity_word_bot_response.length == 0) {

        M.toast({
            "html": "Profanity Text Response cannot be empty."
        }, 2000);
        return
        false;
    }
    $('#modal-configure-profanity-setting').modal('close');
    return true

}

// bot break config

$(document).on("change", "#checkbox-is-email-bot-break-enable", function () {

    var status = document.getElementById("checkbox-is-email-bot-break-enable").checked
    if (status) {

        $("#edit-bot-break-email-config").show()
        if (BOT_BREAK_EMAIL_CONFIGURED.toLowerCase() == "true") {

            $("#test-bot-break-fail-email-config").show()
        }
    } else {

        $("#edit-bot-break-email-config").hide()
        if (BOT_BREAK_EMAIL_CONFIGURED.toLowerCase() == "true") {

            $("#test-bot-break-fail-email-config").hide()
        }
    }
});



function get_bot_break_api_config() {
    mail_sender_time_interval = $("#bot_break_mail_sender_time_interval_input").val()
    if (mail_sender_time_interval == undefined || mail_sender_time_interval == "" || mail_sender_time_interval < 0) {

        M.toast({
            "html": "Kindly enter a valid time interval."
        }, 2000);
        return {
            is_invalid_bot_break_params: true,
            bot_break_mail_sender_time_interval: -1,
            bot_break_email_addr_list: []
        };
    }

    email_addr_list = []
    var email_addr_chip_elmts = M.Chips.getInstance($('#bot-break-email-config-email-address')).chipsData;
    for (var i = 0; i < email_addr_chip_elmts.length; i++) {

        email_addr_list.push(email_addr_chip_elmts[i]["tag"]);
    }
    if (!email_addr_list.length) {

        M.toast({
            "html": "Kindly enter an Email ID to proceed."
        }, 2000);
        return {
            is_invalid_bot_break_params: true,
            bot_break_mail_sender_time_interval: -1,
            bot_break_email_addr_list: []
        };
    }
    for (var i = 0; i < email_addr_list.length; i++) {
        if (!validateEmailAddr(email_addr_list[i])) {
            M.toast({
                "html": "Kindly enter a valid email id."
            }, 2000);
            return {
                is_invalid_bot_break_params: true,
                bot_break_mail_sender_time_interval: -1,
                bot_break_email_addr_list: []
            };
        }
    }
    return {
        is_invalid_bot_break_params: false,
        bot_break_mail_sender_time_interval: mail_sender_time_interval,
        bot_break_email_addr_list: email_addr_list
    };
}

//////////////////  Bot Break Email Configuration /////////////////////

function save_bot_fail_email_configuration(e, bot_pk) {
    mail_sender_time_interval = 1
    email_addr_list = []
    bot_break_api_config = get_bot_break_api_config()
    if (bot_break_api_config.is_invalid_bot_break_params) {
        return;
    }
    mail_sender_time_interval = bot_break_api_config.bot_break_mail_sender_time_interval
    email_addr_list = bot_break_api_config.bot_break_email_addr_list
    csrf_token = get_csrf_token()

    json_string = JSON.stringify({
        "bot_id": bot_pk,
        "mail_sender_time_interval": mail_sender_time_interval,
        "mail_sent_to_list": email_addr_list,
    });
    e.innerHTML = "Saving..."
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: "/chat/save-bot-fail-email-config/",
        type: "POST",
        headers: {
            "X-CSRFToken": csrf_token
        },
        data: {
            data: json_string
        },
        success: function (response) {
            e.innerHTML = "Save"
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                M.toast({
                    "html": "Email Configuration saved."
                })
                if (response["email_configured"]) {
                    $("#test-bot-break-fail-email-config").show();
                } else {
                    $("#test-bot-break-fail-email-config").hide();
                }
            } else if (response["status"] == 300) {
                M.toast({
                    "html": response["msg"]
                })
            } else {
                M.toast({
                    "html": "Unable to process you request. Please try again later."
                })
            }
        },
        error: function (error) {
            e.innerHTML = "Save"
            M.toast({
                "html": "Unable to process you request. Please try again later."
            })
            console.log("Report this error: ", error);
        }
    });

}


function send_bot_break_fail_test_email(bot_pk) {

    csrf_token = get_csrf_token()

    json_string = JSON.stringify({
        "bot_id": bot_pk,
    });

    json_string = EncryptVariable(json_string);
    $("#test-bot-break-fail-email-config").val("Sending test mail...")
    $.ajax({
        url: "/chat/send-bot-break-test-email/",
        type: "POST",
        headers: {
            "X-CSRFToken": csrf_token
        },
        data: {
            data: json_string
        },
        success: function (response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            $("#test-bot-break-fail-email-config").val("Test Bot Break Mail")
            $("#modal-api-fail-email-config").modal('close');
            if (response["status"] == 200) {
                M.toast({
                    "html": "Test mail sent!"
                })
            } else {
                M.toast({
                    "html": "Unable to process you request. Please try again later."
                })
            }
        },
        error: function (error) {
            $("#test-bot-break-fail-email-config").val("Test Bot Break Mail")
            console.log("Report this error: ", error);
        }
    });
}
// bot break config ends

// Livechat Provider configuration start

$("#easychat-checkbox-livechat-enable").on("click", function (event) {
    if (this.checked) {
        $("#choose-livechat-provider-row").show();

    } else {
        $('#choose-livechat-provider-row').hide();
    }
});

$('#livechat-provider-select').on('change', function(){
    if ( this.value == 'ameyo_fusion'){
        $("#livechat-provider-configure-btn").show();
        $(".fusion-select-notification-div").show();
    }
    else{
        $("#livechat-provider-configure-btn").hide();
        $(".fusion-select-notification-div").hide();
    }
});

$(".fusion-select-notification-div .fusion-select-notification .close-svg svg").click(function(){
    $(".fusion-select-notification-div").hide(200);
});

// Livechat Provider configuration end

function remove_keywords_chip(ele) {
    ele.parentElement.remove();
    update_do_not_translate_containers();
}

function update_do_not_translate_containers() {
    if (document.getElementById("keywords-container").children.length){
        document.getElementById("keywords-container").style.display = "block";
    } else {
        document.getElementById("keywords-container").style.display = "none";
    }

    if (document.getElementById("regex-container").children.length){
        document.getElementById("regex-container").style.display = "block";
    } else {
        document.getElementById("regex-container").style.display = "none";
    }
}

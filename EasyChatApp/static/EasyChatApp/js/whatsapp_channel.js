
// This maintains all the data of catalogue sections
const catalogue_state = {
    active_section: null // ID of Catalogue Section being edited is stored in active_section
};

const BOT_ID = get_url_vars()["id"];

var ACTIVE_CATALOGUE_TYPE;

const RETAILER_ID_NAME_MAPPING = {} // Used for WhatsApp Catalogue ID-Name Mapping

$(document).ready(function () {
    track_sync_products_and_details_progress();
    sync_products_details_timer = setInterval(track_sync_products_and_details_progress, 5000);
    $("#catalog_single_product_bodytext").trumbowyg({
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
    });
    $("#catalog_multiple_product_bodytext, #wa_api_body_text, #wa_api_merge_cart_response, #wa_commerce_merge_cart_response").trumbowyg({
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
    });

    $("#whatsapp_catalog_productid_dragable").sortable({
        containment: "parent"
    });
    $("#whatsapp_catalog_productid_dragable_edit").sortable({
        containment: "parent"
    });

    $("#add_section_main_div_wrapper, #catalogue_sections_container").sortable({
        containment: "parent",
        handle: '.multi-product-drag-icon'
    });

    $(function () {
        $("#enable_block_spam_user").click(function () {
            if ($(this).is(":checked")) {
                if (!$("#enable_block_user_number")[0].checked && !$("#enable_block_user_keyword")[0].checked) {
                    $("#enable_block_user_number")[0].checked = true
                }
                if ($("#enable_block_user_number")[0].checked) {
                    $("#Block_users_based_on_number_wrapper").show();
                }
                if ($("#enable_block_user_keyword")[0].checked) {
                    $("#Block_users_based_on_keyword_wrapper").show();
                }
                $("#block_user_based_on_keyword").show();
                $("#enable_block_user_number_div").show();
            } else {
                $("#block_user_based_on_keyword").hide();
                $("#enable_block_user_number_div").hide();
                $("#Block_users_based_on_number_wrapper").hide();
                $("#Block_users_based_on_keyword_wrapper").hide();
            }
        });
    });

    $(function () {
        $("#enable_block_user_number").click(function () {
            if ($(this).is(":checked")) {
                $("#Block_users_based_on_number_wrapper").show();
            } else if ($("#enable_block_user_keyword")[0].checked) {
                $("#Block_users_based_on_number_wrapper").hide();
            } else {
                $("#enable_block_user_number")[0].checked = true
                M.toast({
                    "html": "At least one of the block spam type should be selected"
                }, 2000);
            }
        });
    });

    $(function () {
        $("#enable_block_user_keyword").click(function () {
            if ($(this).is(":checked")) {
                $("#Block_users_based_on_keyword_wrapper").show();
            } else if ($("#enable_block_user_number")[0].checked) {
                $("#Block_users_based_on_keyword_wrapper").hide();
            } else {
                $("#enable_block_user_keyword")[0].checked = true
                M.toast({
                    "html": "At least one of the block spam type should be selected"
                }, 2000);
            }
        });
    });

    // js for multiselect dropdown
    $(function() {
        $('#multiple-select-whatsapp-initial-message-list').multiselect({
            columns: 1,
            placeholder: 'Select Intent',
            search: true,
            searchOptions: {
                'default': 'Search Intent'
            },
            selectAll: false,
        });
        $('#multiple-select-whatsapp-failure-message-list').multiselect({
            columns: 1,
            placeholder: 'Select Intent',
            search: true,
            searchOptions: {
                'default': 'Search Intent'
            },
            selectAll: false,
        });
        
        $('#language-box-options-container').multiselect({
            columns: 1,
            placeholder: 'Select Language',
            search: true,
            searchOptions: {
                'default': 'Search Language'
            },
            selectAll: false,
        });
    });
    // js for multiselect dropdown end

    // js for showing/hiding disable auto-popup checkbox
    $("#is-minimization-enabled").on("change", function(event) {
        if (this.checked) {
            $("#disable_auto_popup_minimized_wrapper").show();
        } else {
            $('#disable_auto_popup_minimized_wrapper').hide();
            $('#disable_auto_popup_minimized_cb').prop('checked', false);
        }
    });
    // js for showing/hiding disable auto-popup checkbox end

    (function () {
        let url_vars = get_url_vars();
        let selected_language = url_vars.selected_lang ? url_vars.selected_lang : "en"
        let json_string = JSON.stringify({
            bot_id: url_vars.id,
            selected_language: selected_language
        });
        $.ajax({
            url: "/chat/channels/whatsapp/get-catalogue-details/",
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
                    if("catalogue_items_map" in response && response.catalogue_items_map.length) {
                        create_catalogue_items_dropdown(response.catalogue_items_map)
                    }
                    if ("catalogue_metadata" in response) {
                        populate_whatsapp_catalogue_details(
                            response, response.catalogue_type, JSON.parse(response.catalogue_metadata)
                        )
                    }
                    if ("is_catalogue_enabled" in response && response.is_catalogue_enabled) {
                        $("#enable_whatsapp_catalog_cb").prop("checked", true).change()
                    }
                    if ("catalogue_type" in response) {
                        if(response.catalogue_type == "commerce_manager_catalogue") {
                            $("#enable_whatsapp_catalog_commerce_cb").prop("checked", true).change()
                        } else if (response.catalogue_type == "api_catalogue") {
                            $("#enable_whatsapp_catalog_api_cb").prop("checked", true).change()
                        }
                    }
                }
            },
            error: function (error) {
                console.log("Report this error: ", error);
            }
        });
        setTimeout(() => {
            if (selected_language != "en") {
                disable_catalogue_options_for_language_tuning()
            }
        }, 500)
    })();

    $("#sync_products_fb_btn").click(() => {
        let access_token = $("#wa_access_token").val().trim();
        let catalogue_id = $("#wa_api_catalogue_id").val().trim();
        if (access_token == "") {
            M.toast({
                "html": "Access Token cannot be empty!."
            }, 2000);
            return;
        }
        if (catalogue_id == "") {
            M.toast({
                "html": "Catalogue ID cannot be empty!."
            }, 2000);
            return;
        }
        $("#sync_products_fb_svg").css("animation", "rotate 2s infinite");
        $("#sync_products_fb_btn").css("pointer-events", "none");
        let json_string = JSON.stringify({
            bot_id: BOT_ID,
            catalogue_id: catalogue_id,
            access_token: access_token
        });
        $.ajax({
            url: "/chat/channels/whatsapp/add-catalogue-details/",
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
                    sync_products_details_timer = setInterval(track_sync_products_and_details_progress, 5000);
                } else {
                    $("#sync_products_fb_svg").css("animation", "none");
                    $("#sync_products_fb_btn").css("pointer-events", "auto");
                    if ("message" in response) {
                        M.toast({
                            "html": response.message
                        }, 3000);
                    } else {
                        M.toast({
                            "html": "Error in adding Catalogue Details and Syncing Products, please try again later!"
                        }, 3000);
                    }
                }
            },
            error: function (error) {
                $("#sync_products_fb_svg").css("animation", "none");
                $("#sync_products_fb_btn").css("pointer-events", "auto");
                M.toast({
                    "html": "Error in adding Catalogue Details and Syncing Products, please try again later!"
                }, 3000);
            }
        });
    })

    function track_sync_products_and_details_progress() {

        let json_string = JSON.stringify({
            bot_id: BOT_ID,
            event_type: 'sync_products',
        })
        $("#sync_products_fb_svg").css("animation", "rotate 2s infinite");
        $("#sync_products_fb_btn").css("pointer-events", "none");
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

                    if (is_failed && !is_toast_displayed) {
                        if ("message" in event_info) {
                            M.toast({
                                "html": event_info["message"]
                            }, 5000);
                        } else {
                            M.toast({
                                "html": "Error in Syncing products with Commerce Manager, please try again later."
                            }, 2000);
                        }
                        $("#sync_products_fb_svg").css("animation", "none");
                        $("#sync_products_fb_btn").css("pointer-events", "auto");
                        if (sync_products_details_timer) {
                            clearInterval(sync_products_details_timer);
                        }
                    } else if (is_completed && !is_toast_displayed) {
                        if ("status" in event_info && event_info.status != 200 && "message" in event_info) {
                            M.toast({
                                "html": event_info["message"]
                            }, 5000);
                        } else {
                            $("#wa_access_token, #wa_api_catalogue_id").prop("disabled", "disabled")
                            $("#wa_access_token, #wa_api_catalogue_id").css("cursor", 'url("/static/EasyChatApp/img/red-not-allowed.svg"), auto')
                            
                            M.toast({
                                "html": "Details added and products synced successfully!"
                            }, 3000);

                            if("catalogue_items_map" in event_info && event_info.catalogue_items_map.length) {
                                create_catalogue_items_dropdown(event_info.catalogue_items_map)
                            }
                        }
                        $("#sync_products_fb_svg").css("animation", "none");
                        $("#sync_products_fb_btn").css("pointer-events", "auto");
                        if (sync_products_details_timer) {
                            clearInterval(sync_products_details_timer);
                        }
                    } else if (is_completed && is_toast_displayed){
                        if (sync_products_details_timer) {
                            clearInterval(sync_products_details_timer);
                        }
                        $("#sync_products_fb_svg").css("animation", "none");
                        $("#sync_products_fb_btn").css("pointer-events", "auto");
                    }
                } else {
                    if (sync_products_details_timer) {
                        clearInterval(sync_products_details_timer);
                    }
                    $("#sync_products_fb_svg").css("animation", "none");
                    $("#sync_products_fb_btn").css("pointer-events", "auto");
                }
            },
            error: function(xhr, textstatus, errorthrown) {
                console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
                $("#sync_products_fb_svg").css("animation", "none");
                $("#sync_products_fb_btn").css("pointer-events", "auto");
            }
        });
    }

    function create_catalogue_items_dropdown(catalogue_items_map) {
        $("li.product-id-item.product-id-item-select").remove();
        for (let index = 0; index < catalogue_items_map.length; index++) {
            let active_item = catalogue_items_map[index]
            let dropdown_html = `<li class="product-id-item product-id-item-select">
                            <label>
                                <input type="checkbox" item-retailer-id="${active_item.retailer_id}" id="${active_item.retailer_id}"
                                    style="position:relative;opacity:1;width: unset !important;margin-top: 0 !important;height: 1.4rem !important;pointer-events: auto;cursor: pointer;">
                                <div class="product-id-item-text">${sanitize_html(active_item.item_name)} (${sanitize_html(active_item.retailer_id)})</div>
                            </label>
                        </li>`
            $("#add_product_id_container").append(dropdown_html)
            RETAILER_ID_NAME_MAPPING[active_item.retailer_id] = active_item.item_name
        }
        $("#item_selection_dropdown_wrapper").css("display", "flex");
        $("#catalog_modal_product_id_input").hide();
        $("#whatsapp_catalog_productid_dragable").css({
            "width": "100%",
            "min-height": "45px",
            "margin": "0px"
        });

        $("#add_product_id_container input").on("change", function (event) {
            if (this.checked) {
                $("#whatsapp_catalog_productid_dragable").append(get_product_id_chip_html(this.id));
            } else {
                $("span[item-retailer-id='" + this.id + "']").remove();
            }
            check_section_save_btn_state();
        });
    }

    function add_catalogue_char_count_listeners() {
        $("#wa_api_header_text").keyup((el) => $("#wa_api_header_count").text(el.target.value.length))
        $("#wa_api_body_text_wrapper .trumbowyg-editor").keyup((el) => $("#wa_api_body_count").text($("#wa_api_body_text").trumbowyg('html').length))
        $("#wa_api_footer_text").keyup((el) => $("#wa_api_footer_count").text(el.target.value.length))
        $("#header_text_multiple_product").keyup((el) => $("#wa_commerce_header_count").text(el.target.value.length))
        $("#wa_multiple_body_text_wrapper .trumbowyg-editor").keyup((el) => $("#wa_multiple_body_text").text($("#catalog_multiple_product_bodytext").trumbowyg('html').length))
        $("#footer_text_multiple_product").keyup((el) => $("#wa_multiple_footer_text").text(el.target.value.length))
        $("#single_product_body_text_wrapper .trumbowyg-editor").keyup((el) => $("#wa_single_body_text").text($("#catalog_single_product_bodytext").trumbowyg('html').length))
        $("#footer_text_single_product").keyup((el) => $("#wa_single_footer_text").text(el.target.value.length))
    }
    add_catalogue_char_count_listeners();
    $("#single_product_body_text_wrapper .trumbowyg-editor, #wa_api_body_text_wrapper .trumbowyg-editor, #wa_multiple_body_text_wrapper .trumbowyg-editor").keyup();
});

$(document).on("click", ".ms-has-selections button", function() {
    $("input[value=en]").attr("disabled", true)
})

function handle_submit_spam_keywords(e) {
    let keywords = e.target.elements.spam_keyword.value
    keywords = keywords.replace(/(<([^>]+)>)/ig, '')
    const multiple_keywords = keywords.split(" ")

    for (let keyword of multiple_keywords) {
        if (keyword.trim() !== "" && !block_spam_keywords[keyword.toLowerCase()]) {
        block_spam_keywords[keyword.toLowerCase()] = true
        $(".keyword-preview-container-div").append(`
            <span>
                ${keyword}
                <svg width="13" style="cursor: pointer;" height="13" viewBox="0 0 13 13" fill="none" xmlns="http://www.w3.org/2000/svg" onclick="handle_remove_keyword(event)">
                <path d="M2.94727 2.8103L10.1597 10.3103" stroke="white" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"></path>
                <path d="M10.1602 2.8103L2.94776 10.3103" stroke="white" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"></path>
                </svg>
            </span>
        `)
        }
    }

    if (Object.keys(block_spam_keywords).length > 0) {
        $(".keyword-preview-container").show()
    }

    handle_search_keyword()

    $("#spam_keyword").val("")
    return false
}

function handle_remove_keyword(e) {
    delete block_spam_keywords[e.currentTarget.parentElement.innerText]
    $(e.currentTarget.parentElement).remove()
    if (Object.keys(block_spam_keywords).length <= 0) {
        $(".keyword-preview-container").hide()
    }
    handle_search_keyword()
}

function handle_search_keyword() {
    const all_keywords = $(".keyword-preview-container-div span")
    const regex = new RegExp($("#block_keyword_search_bar").val().trim(), "gi")
    let any_match = false;

    for (const keyword of all_keywords) {
        if (keyword.innerText.trim().match(regex)) {
            $(keyword).show()
            any_match = true
        } else {
            $(keyword).hide()
        }
    }

    if (!any_match) {
        $("#no-keyword-div").show()
    } else {
        $("#no-keyword-div").hide()
    }
}

function handle_block_thresold_value(e) {
    e.target.value = Math.floor(e.target.value)
    if (Number(e.target.value) > 264) {
        e.target.value = 264
    }
    if (e.target.id === "query_block_msg_count") {
        const query_warning_thresold = $("#query_warning_msg_count").val()
        if (e.target.value <= query_warning_thresold) {
            e.target.value = String(Number(query_warning_thresold) + 1)
        }
    } else if (e.target.id === "keywords_block_msg_count") {
        const keywords_warning_thresold = $("#keywords_warning_msg_count").val()
        if (e.target.value <= keywords_warning_thresold) {
            e.target.value = String(Number(keywords_warning_thresold) + 1)
        }
    }
}

function handle_non_natural_numbers(e) {
    if (e.target.value <= 0) {
        e.target.value = 1
    }

    e.target.value = Math.floor(e.target.value)

    if (e.target.id.match("warning_msg_count") && Number(e.target.value) > 263) {
        e.target.value = 263
    }

    if (e.target.id === "keywords_warning_msg_count" && Number(e.target.value) >= Number($("#keywords_block_msg_count").val())) {
        $("#keywords_block_msg_count").val(String(Number(e.target.value) + 1))
    }

    if (e.target.id === "query_warning_msg_count" && Number(e.target.value) >= Number($("#query_block_msg_count").val())) {
        $("#query_block_msg_count").val(String(Number(e.target.value) + 1))
    }

    if (e.target.id === "query_block_duration" || e.target.id === "keywords_block_duration") {
        if (Number(e.target.value) > 24) {
            e.target.value = 24
        }
    }
}

$(document).on("click", "#select-intent-processor~span", function() {
    $("body > span:last-of-type input")[0].style = "border-radius: 20px !important;" +
    "padding: 0rem 0.8rem !important;margin-top: 6px !important;width: 90% !important;" + 
    "box-shadow: none;height: 2.5rem !important;" + 
    "border-bottom: 1px solid #e6e6e6 !important;font-size: 15px !important;letter-spacing: -0.06em;"
})

$("#whatsapp_single_product_catalog-cb").on("change", function (event) {
    if (this.checked) {
        $(".whatsapp-single-product-catalog-div").show();
        $('#whatsapp-multiple-product-catalog-div').hide();
    } else {
        $('.whatsapp-single-product-catalog-div').hide();
    }
});

$("#whatsapp_multiple_product_catalog-cb").on("change", function (event) {
    if (this.checked) {
        $(".whatsapp-single-product-catalog-div").hide();
        $('#whatsapp-multiple-product-catalog-div').show();
    } else {
        $('#whatsapp-multiple-product-catalog-div').hide();
    }
});

$("#enable_whatsapp_catalog_cb").on("change", function (event) {

    if (this.checked) {
        $("#catalogue_manager_options_div").show();
    } else {
        $("#catalogue_manager_options_div").hide();
        $("#enable_whatsapp_catalog_commerce_cb, #enable_whatsapp_catalog_api_cb").prop("checked", false).change();
    }
})

$("#enable_whatsapp_catalog_commerce_cb").on("change", function (event) {
    if (this.checked) {
        $(".whatsapp-catalog-data-wrapper-div").show();
        $("#enable_whatsapp_catalog_api_cb").prop("checked", false).change();
    } else {
        $('.whatsapp-catalog-data-wrapper-div').hide();
    }
});

$("#enable_whatsapp_catalog_api_cb").on("change", function (event) {
    if (this.checked) {
        $("#catalogue_via_api_wrapper, #api_add_section_wrapper").show();
        $("#enable_whatsapp_catalog_commerce_cb").prop("checked", false).change();
    } else {
        $('#catalogue_via_api_wrapper, #api_add_section_wrapper').hide();
    }
});

$("#wa_api_merge_cart_toggle").on("change", function (event) {
    if (this.checked) {
        $("#api_merge_cart_response_wrapper").show();
    } else {
        $("#api_merge_cart_response_wrapper").hide();
    }
});

$("#wa_commerce_merge_cart_toggle").on("change", function (event) {
    if (this.checked) {
        $("#commerce_merge_cart_response_wrapper").show();
    } else {
        $("#commerce_merge_cart_response_wrapper").hide();
    }
});

$('.enable-block-spam-user-div-wrapper input[type=number]').on('keypress', function (event) {

    var regex = new RegExp("^[0-9]"); // your regex

    var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);

    if (!regex.test(key)) {

    event.preventDefault();

    return false;

    }

});

$('.enable-block-spam-user-div-wrapper input[type=number]').on('paste', function (event) {

    var regex = new RegExp("^[0-9]*$"); // your regex
    var pastedData = event.originalEvent.clipboardData.getData('text');

    if (!regex.test(pastedData)) {

    event.preventDefault();

    return false;

    }

});

function check_whatsapp_credentials_validation(username, password, host_url){
    is_cred_valid = true
    if(username.trim() == ""){
        M.toast({
            "html": "Whatsapp Credentials Username can not be Empty."
        }, 2000);
        is_cred_valid = false
        return is_cred_valid
    }
    if(password.trim() == ""){
        M.toast({
            "html": "Whatsapp Credentials Password can not be Empty."
        }, 2000);
        is_cred_valid = false
        return is_cred_valid
    }

    if(!isValidURL(host_url)  || host_url.trim() == ""){
        M.toast({
            "html": "Please enter valid Url in Whatsapp Credentials"
        }, 2000);
        is_cred_valid = false
        return is_cred_valid
    }

    if(host_url.substr(-1) == '/'){
        M.toast({
            "html": "Please do not enter a '/' at the end of the Url in Whatsapp Credentials"
        }, 2000);
        is_cred_valid = false
        return is_cred_valid
    }

    return is_cred_valid
}

$(document).on("click", "#save-whatsapp-channel", function (e) {
    let location_href = window.location.href;
    location_href = location_href.replace("#", "");
    location_href = location_href.replace("!", "");
    let bot_id = get_url_vars()['id']
    let is_email_notifiication_enabled = document.getElementById("checkbox-is-whatsapp-email-notifiication-enabled").checked;
    // var welcome_message = $('#welcome-message').val();
    // var failure_message = $('#failure-message').val();

    let welcome_message = $("#welcome-message").trumbowyg('html');
    let failure_message = $("#failure-message").trumbowyg('html')
    let authentication_message = $("#authentication-message").trumbowyg('html')

    let is_language_auto_detection_enabled = document.getElementById("is_language_auto_detection_enabled").checked
    let is_enable_choose_language_flow_enabled_for_welcome_response = document.getElementById("is_enable_choose_language_flow_enabled_for_welcome_response").checked

    let selected_supported_languages = [];
    $(".language-box-options-container").each((indx, ele) => {
        selected_supported_languages.push(ele.id.split('_')[1])
    })

    if ("en" in selected_supported_languages == false) {
        selected_supported_languages.push("en");
    }

    // whatsapp credentials validation
    let username = document.getElementById("easychat_whatsapp_vendor_username").value;
    let host_url = document.getElementById("easychat_whatsapp_vendor_url").value.trim();
    let password = document.getElementById("easychat_whatsapp_vendor_password").value;

    let are_creds_valid = check_whatsapp_credentials_validation(username, password, host_url)
    if(!are_creds_valid){
        return;
    }
    var validation_message = check_channel_messages_validation(welcome_message, failure_message, authentication_message);
    if (validation_message != "No Error") {
        M.toast({
            "html": validation_message
        }, 2000);
        return;
    }
    
    let initial_message_list = [];
    $(".initial_questions_selected_intent").each((indx, ele) => {
        initial_message_list.push(ele.id.split('_')[1])
         })
        
        
        //  $("select#multiple-select-whatsapp-failure-message-list").val();
    let failure_recommendation_list = [];
    $(".failure_questions_selected_intent").each((indx, ele) => {
        failure_recommendation_list.push(ele.id.split('_')[1])
    })
     
    let image_id = document.getElementById("uploaded-bot-welcome-image");
    let image_url = image_id.getAttribute("src");
    let video_url = document.getElementById("upload-bot-welcome-video-url").value.trim();

    // Get Block Sapam User Config
    let is_enabled_block_spam_user = $("#enable_block_spam_user")[0].checked
    let is_enabled_block_spam_query = $("#enable_block_user_number")[0].checked
    let is_enabled_block_spam_keywords = $("#enable_block_user_keyword")[0].checked
    let query_warning_message_thresold = $("#query_warning_msg_count").val()
    let query_warning_message_text = $("#query_warning_msg").trumbowyg('html')
    let query_block_message_thresold = $("#query_block_msg_count").val()
    let query_block_message_text = $("#query_block_msg").trumbowyg('html')
    let query_block_duration = $("#query_block_duration").val()
    let spam_keywords = Object.keys(block_spam_keywords)
    let keywords_warning_message_thresold = $("#keywords_warning_msg_count").val()
    let keywords_warning_message_text = $("#keywords_warning_msg").trumbowyg('html')
    let keywords_block_message_thresold = $("#keywords_block_msg_count").val()
    let keywords_block_message_text = $("#keywords_block_msg").trumbowyg('html')
    let keywords_block_duration = $("#keywords_block_duration").val()
    if (is_enabled_block_spam_user) {
        validation_message = check_channel_block_warning_message_validation(query_warning_message_text, query_block_message_text, 
            keywords_warning_message_text, keywords_block_message_text)
    }

    if (is_enabled_block_spam_user && validation_message != "No Error") {
        M.toast({
            "html": validation_message
        }, 2000);
        return;
    }

    if (isValidURL(video_url) == false && video_url != "") {
        M.toast({
            "html": "Please enter valid video url"
        }, 2000);
        return;
    }

    const mobile_regex = /^[6-9]{1}[0-9]{9}$/;
    var integrated_whatsapp_mobile = document.getElementById("easychat-whatsapp-mobile").value;
    if (integrated_whatsapp_mobile.trim() != "" && !mobile_regex.test(integrated_whatsapp_mobile)) {

        M.toast({
            "html": "Please enter valid mobile number."
        }, 2000);
        return;
    }

    var whatsapp_number_masking = document.getElementById('checkbox-whatsapp-number-masking-enabled').checked;

    let is_catalogue_enabled = document.getElementById('enable_whatsapp_catalog_cb').checked;

    let catalogue_metadata = {}
    let catalogue_via;
    if (is_catalogue_enabled) {
        catalogue_metadata = get_whatsapp_catalogue_data();
        if($("#enable_whatsapp_catalog_commerce_cb").prop("checked")) {
            catalogue_via = "commerce_manager_catalogue";
        } else {
            catalogue_via = "api_catalogue";
        }
    }
    if ("error_message" in catalogue_metadata) {
        M.toast({
            "html": catalogue_metadata.error_message
        }, 2000);
        return;
    }

    json_string = JSON.stringify({
        bot_id: bot_id,
        welcome_message: welcome_message,
        failure_message: failure_message,
        authentication_message: authentication_message,
        initial_message_list: initial_message_list,
        image_url: image_url,
        video_url: video_url,
        failure_recommendation_list: failure_recommendation_list,
        is_email_notifiication_enabled: is_email_notifiication_enabled,
        integrated_whatsapp_mobile: integrated_whatsapp_mobile,
        whatsapp_number_masking: whatsapp_number_masking,
        selected_supported_languages: selected_supported_languages,
        is_enable_choose_language_flow_enabled_for_welcome_response: is_enable_choose_language_flow_enabled_for_welcome_response,
        is_language_auto_detection_enabled: is_language_auto_detection_enabled,
        is_enabled_block_spam_user,
        is_enabled_block_spam_query,
        is_enabled_block_spam_keywords,
        query_warning_message_thresold,
        query_warning_message_text,
        query_block_message_thresold,
        query_block_message_text,
        query_block_duration,
        spam_keywords,
        keywords_warning_message_thresold,
        keywords_warning_message_text,
        keywords_block_message_thresold,
        keywords_block_message_text,
        keywords_block_duration,
        is_catalogue_enabled,
        catalogue_metadata,
        catalogue_via,
        username,
        password,
        host_url,
    });

    json_string = EncryptVariable(json_string)
    document.getElementById("easychat_whatsapp_channel_preloader").style.display = "block";
    $.ajax({
        url: "/chat/channels/whatsapp/save/",
        type: "POST",
        data: {
            json_string: json_string
        },
        headers: {
            "X-CSRFToken": get_csrf_token()
        },
        success: function (response) {
            document.getElementById("easychat_whatsapp_channel_preloader").style.display = "none";
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
        error: function (error) {
            document.getElementById("easychat_whatsapp_channel_preloader").style.display = "none";
            console.log("Report this error: ", error);
        }
    });
});

$("#catalogue_section_title").keyup(() => {
    let section_title_length = $("#catalogue_section_title").val().length;
    $('#section_text_count').text(section_title_length);
    check_section_save_btn_state();
})

$("#catalog_modal_product_id_input").keypress((event) => {
    let keycode = (event.keyCode ? event.keyCode : event.which);
    if (keycode != '13') return
    let product_id = $("#catalog_modal_product_id_input").val().trim()
    if (product_id == "") {
        M.toast({
            "html": "Please enter a valid Product ID"
        }, 2000)
        return;
    }
    $("#whatsapp_catalog_productid_dragable").append(get_product_id_chip_html(product_id));
    $("#catalog_modal_product_id_input").val("");
    check_section_save_btn_state();
})

function revised_language_change_sideeffect(show_change_language_on_welcome_message=false) {
    const selected_language_list = $('select#language-box-options-container').val()

    if (selected_language_list.length === 0) {
        document.getElementById("is_language_auto_detection_enabled").checked = false;
        document.getElementById("is_language_auto_detection_enabled").disabled = true;
        document.getElementById("bot_language_auto_detection_div").style.visibility = "hidden"

        document.getElementById("is_enable_choose_language_flow_enabled_for_welcome_response").checked = false;
        document.getElementById("is_enable_choose_language_flow_enabled_for_welcome_response").disabled = true;
        document.getElementById("enable_choose_language_welcome_response_toogle_div").style.display = "none"
    } else {
        document.getElementById("is_language_auto_detection_enabled").disabled = false;
        document.getElementById("bot_language_auto_detection_div").style.visibility = "visible"

        document.getElementById("is_enable_choose_language_flow_enabled_for_welcome_response").disabled = false;
        document.getElementById("enable_choose_language_welcome_response_toogle_div").style.display = "grid"
    }

    if (!show_change_language_on_welcome_message) {
        document.getElementById("enable_choose_language_welcome_response_toogle_div").style.display = "none"
    }
}

function check_channel_block_warning_message_validation(query_warning_message_text, query_block_message_text, 
    keywords_warning_message_text, keywords_block_message_text) {
        let message = "No Error";
        if (query_warning_message_text.trim() == "") {
            message = "Warning message for user queries cannot be empty."
            return message;
        }

        if (query_warning_message_text.trim().length > character_limit_large_text) {
            message = "Warning message for user queries is too long."
            return message;
        }

        if (query_block_message_text.trim() == "") {
            message = "Blocking message for user queries cannot be empty."
            return message;
        }

        if (query_block_message_text.trim().length > character_limit_large_text) {
            message = "Blocking message for user queries is too long."
            return message;
        }

        if (keywords_warning_message_text.trim() == "") {
            message = "Warning message for spam keywords cannot be empty."
            return message;
        }

        if (keywords_warning_message_text.trim().length > character_limit_large_text) {
            message = "Warning message for spam keywords is too long."
            return message;
        }

        if (keywords_block_message_text.trim() == "") {
            message = "Blocking message for spam keywords cannot be empty."
            return message;
        }

        if (keywords_block_message_text.trim().length > character_limit_large_text) {
            message = "Blocking message for spam keywords is too long."
            return message;
        }
        return message;
    }

/**
 * Adds a Catalogue Section for Multiple Product Catalogue.
 */
function add_catalogue_section() {
    let section_title = $("#catalogue_section_title").val().trim();
    if (section_title == "" || section_title.length > 24) {
        M.toast({
            "html": "Please enter a valid Section Title (Max 24 characters)"
        }, 2000)
        return;
    }

    let product_ids = []
    $("#whatsapp_catalog_productid_dragable span").each((indx, element) => {
        product_ids.push($(element).attr("item-retailer-id").trim());
    })
    if (!product_ids.length) {
        M.toast({
            "html": "Please enter atleast one product"
        }, 2000)
        return;
    }
    let is_section_update = false;
    let active_section_id = catalogue_state.active_section;
    if (active_section_id && active_section_id in catalogue_state) {
        is_section_update = true
    } else {
        catalogue_state.active_section = generate_random_string(4);
    }
    catalogue_state[catalogue_state.active_section] = {};
    catalogue_state[catalogue_state.active_section].product_ids = product_ids;
    catalogue_state[catalogue_state.active_section].section_title = section_title;
    catalogue_state[catalogue_state.active_section].catalogue_type = (ACTIVE_CATALOGUE_TYPE == "commerce_manager_catalogue") ? "commerce_manager_catalogue" : "api_catalogue";
    if (!is_section_update) {
        if(ACTIVE_CATALOGUE_TYPE == "commerce_manager_catalogue") {
            $("#catalogue_sections_container").append(
                get_catalogue_section_html(catalogue_state[catalogue_state.active_section])
            );
        } else {
            $("#add_section_main_div_wrapper").append(
                get_catalogue_section_html(catalogue_state[catalogue_state.active_section])
            );
        }
    } else {
        update_catalogue_section_html(catalogue_state.active_section)
    }
    $("#easychat_whatsapp_add_section_modal").modal("close");
    catalogue_state.active_section = null;
}

/**
 * Returns a JSON of all the data related to WhatsApp Catalogue.
 */
function get_whatsapp_catalogue_data() {
    let catalogue_metadata = {};
    let catalogue_via;
    if($("#enable_whatsapp_catalog_commerce_cb").prop("checked")) {
        let catalogue_type = $("input:radio[name=catalogue_product_type]:checked").val();
        catalogue_via = "commerce_manager_catalogue";
        catalogue_metadata.catalogue_type = catalogue_type
        catalogue_metadata.body_text = $("#catalog_" + catalogue_type + "_bodytext").trumbowyg('html');
        if (catalogue_metadata.body_text.trim() == "") {
            catalogue_metadata.error_message = "Body Text cannot be empty.";
            return catalogue_metadata;
        }
        if (catalogue_metadata.body_text.length > 1024) {
            catalogue_metadata.error_message = "Body Text cannot be greater than 1024 characters.";
            return catalogue_metadata;
        }
        catalogue_metadata.footer_text = $('#footer_text_' + catalogue_type).val();
        if (catalogue_metadata.footer_text.length > 60) {
            catalogue_metadata.error_message = "Footer Text cannot be greater than 60 characters.";
            return catalogue_metadata;
        }
        catalogue_metadata.catalogue_id = $('#catalogue_id_' + catalogue_type).val();
        if (catalogue_metadata.catalogue_id.trim() == "") {
            catalogue_metadata.error_message = "Catalogue ID cannot be empty.";
            return catalogue_metadata;
        }

        let merge_cart_enabled = $('#wa_commerce_merge_cart_toggle').prop('checked');
        catalogue_metadata.merge_cart_enabled = merge_cart_enabled ? "true" : "false"
        catalogue_metadata.merge_cart_text = $("#wa_commerce_merge_cart_response").trumbowyg('html');
        if (merge_cart_enabled && catalogue_metadata.merge_cart_text.trim() == "") {
            catalogue_metadata.error_message = "Merge Cart Response cannot be empty.";
            return catalogue_metadata;
        }

        if (catalogue_type == 'single_product') {
            catalogue_metadata.product_id = $('#product_id_single_product').val();
            if (catalogue_metadata.product_id.trim() == "") {
                catalogue_metadata.error_message = "Product ID cannot be empty.";
            }
            return catalogue_metadata;
        }
        catalogue_metadata.header_text = $('#header_text_multiple_product').val();
        if (catalogue_metadata.header_text.trim() == "") {
            catalogue_metadata.error_message = "Header Text cannot be empty.";
            return catalogue_metadata;
        }
        if (catalogue_metadata.header_text.length > 60) {
            catalogue_metadata.error_message = "Header Text cannot be greater than 60 characters.";
            return catalogue_metadata;
        }
        // if (("active_section" in catalogue_state && Object.keys(catalogue_state).length == 1) || Object.keys(catalogue_state).length == 0) {
        //     catalogue_metadata.error_message = "Atleast one section is required for Multiple Product Catalogue.";
        //     return catalogue_metadata;
        // }

        catalogue_metadata.section_ordering = []
        $("#catalogue_sections_container .easychat-whatsapp-menu-item-wrapper").each((indx, ele) => {
            let section_id = ele.id.split("_");
            section_id = section_id[section_id.length - 1]
            catalogue_metadata.section_ordering.push(section_id)
        })
        // delete catalogue_state.active_section
        catalogue_metadata.sections = catalogue_state
        return catalogue_metadata;
    } else if ($("#enable_whatsapp_catalog_api_cb").prop("checked")) {
        catalogue_via = "api_catalogue"
        catalogue_metadata.business_id = $("#wa_business_id").val().trim();
        if(catalogue_metadata.business_id == "") {
            catalogue_metadata.error_message = "WhatsApp Business ID cannot be empty!";
            return catalogue_metadata;
        }
        catalogue_metadata.access_token = $("#wa_access_token").val().trim();
        if(catalogue_metadata.access_token == "") {
            catalogue_metadata.error_message = "WhatsApp Access Token cannot be empty!";
            return catalogue_metadata;
        }
        // catalogue_metadata.catalogue_type = "multiple_product";
        catalogue_metadata.catalogue_id = $("#wa_api_catalogue_id").val().trim();
        if (catalogue_metadata.catalogue_id == "") {
            catalogue_metadata.error_message = "Catalogue ID cannot be empty.";
            return catalogue_metadata;
        }
        catalogue_metadata.header_text = $('#wa_api_header_text').val().trim();
        if (catalogue_metadata.header_text == "") {
            catalogue_metadata.error_message = "Header Text cannot be empty.";
            return catalogue_metadata;
        }
        if (catalogue_metadata.header_text.length > 60) {
            catalogue_metadata.error_message = "Header Text cannot be greater than 60 characters.";
            return catalogue_metadata;
        }
        catalogue_metadata.body_text = $("#wa_api_body_text").trumbowyg('html').trim();
        if (catalogue_metadata.body_text == "") {
            catalogue_metadata.error_message = "Body Text cannot be empty.";
            return catalogue_metadata;
        }
        if (catalogue_metadata.body_text.length > 1024) {
            catalogue_metadata.error_message = "Body Text cannot be greater than 1024 characters.";
            return catalogue_metadata;
        }
        catalogue_metadata.footer_text = $("#wa_api_footer_text").val().trim();
        if (catalogue_metadata.footer_text.length > 60) {
            catalogue_metadata.error_message = "Footer Text cannot be greater than 60 characters.";
            return catalogue_metadata;
        }
        catalogue_metadata.sections = catalogue_state;
        catalogue_metadata.catalogue_type = "multiple_product";
        let merge_cart_enabled = $('#wa_api_merge_cart_toggle').prop('checked');
        catalogue_metadata.merge_cart_enabled = merge_cart_enabled ? "true" : "false"
        catalogue_metadata.merge_cart_text = $("#wa_api_merge_cart_response").trumbowyg('html');
        if (merge_cart_enabled && catalogue_metadata.merge_cart_text.trim() == "") {
            catalogue_metadata.error_message = "Merge Cart Response cannot be empty.";
            return catalogue_metadata;
        }
        
        catalogue_metadata.section_ordering = []
        $("#add_section_main_div_wrapper .easychat-whatsapp-menu-item-wrapper").each((indx, ele) => {
            let section_id = ele.id.split("_");
            section_id = section_id[section_id.length - 1]
            catalogue_metadata.section_ordering.push(section_id)
        })
    } else {
        catalogue_metadata.error_message = "Please select atleast one catalogue type!"
    }
    return catalogue_metadata;
}

function get_product_name_if_available(product_id) {
    if (product_id in RETAILER_ID_NAME_MAPPING) {
        return sanitize_html(RETAILER_ID_NAME_MAPPING[product_id]) + " (" + product_id + ")";
    } else {
        return sanitize_html(product_id)
    }
}

/**
 * Returns HTML of sortable chip for Catalogue Product ID.
 * @param product_id is the ID of Product to be added.
 */
function get_product_id_chip_html(product_id) {
    let chip_id = generate_random_string(3);
    return '<span item-retailer-id="' + product_id + '" id="chip_' + chip_id + '" class="ui-sortable-handle">' +
        '<b>' +
        '<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M8 8.5C8.55228 8.5 9 8.94772 9 9.5C9 10.0523 8.55228 10.5 8 10.5C7.44772 10.5 7 10.0523 7 9.5C7 8.94772 7.44772 8.5 8 8.5ZM4 8.5C4.55228 8.5 5 8.94772 5 9.5C5 10.0523 4.55228 10.5 4 10.5C3.44772 10.5 3 10.0523 3 9.5C3 8.94772 3.44772 8.5 4 8.5ZM8 5C8.55228 5 9 5.44772 9 6C9 6.55228 8.55228 7 8 7C7.44772 7 7 6.55228 7 6C7 5.44772 7.44772 5 8 5ZM4 5C4.55228 5 5 5.44772 5 6C5 6.55228 4.55228 7 4 7C3.44772 7 3 6.55228 3 6C3 5.44772 3.44772 5 4 5ZM8 1.5C8.55228 1.5 9 1.94772 9 2.5C9 3.05228 8.55228 3.5 8 3.5C7.44772 3.5 7 3.05228 7 2.5C7 1.94772 7.44772 1.5 8 1.5ZM4 1.5C4.55228 1.5 5 1.94772 5 2.5C5 3.05228 4.55228 3.5 4 3.5C3.44772 3.5 3 3.05228 3 2.5C3 1.94772 3.44772 1.5 4 1.5Z" fill="white"></path></svg>' +
        '</b>' + get_product_name_if_available(product_id) +
        '<a class="remove-chip-btn" onclick="remove_product_chip(`' + chip_id + '`, `' + product_id +'`)"> <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2.3938 2.25L9.60619 9.75" stroke="white" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"></path><path d="M9.6062 2.25L2.39381 9.75" stroke="white" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"></path></svg></a>' +
        '</span>'
}

/**
 * Removes Product ID Chip from WhatsApp Catalogue Section.
 * @param chip_id is the ID of Product Chip to be removed
 */
function remove_product_chip(chip_id, product_id) {
    $('#chip_' + chip_id).remove();
    check_section_save_btn_state();
    $("#add_product_id_container input[item-retailer-id='" + product_id + "']").prop("checked", false).change();
}

/**
 * Resets the WhatsApp Catalogue Add Section Modal.
 */
function reset_section_modal(is_api_modal=false) {
    $('#catalogue_section_title').val('').keyup();
    $('#catalog_modal_product_id_input').val('');
    $('#whatsapp_catalog_productid_dragable').html('');
    catalogue_state.active_section = null;
    $('#catalogue_section_heading').text('Add Section');
    check_section_save_btn_state();
    if (is_api_modal) {
        ACTIVE_CATALOGUE_TYPE = "api_catalogue"
    } else {
        ACTIVE_CATALOGUE_TYPE = "commerce_manager_catalogue"
    }
    $("#add_product_id_container input").prop("checked", false)
    $("#product-id-search-bar1").val("").keyup();
}

/**
 * Returns HTML for the div containing all the added section information.
 * @param section_details is a JSON having all the data of the section to be added.
 */
function get_catalogue_section_html(section_details) {
    let section_html = `<div class="easychat-whatsapp-menu-item-wrapper" id="section_${catalogue_state.active_section}">
    <div class="add-section-heading-tags">
    <span class="multi-product-drag-icon"style="cursor: grabbing;">
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M10.6667 11.3333C11.403 11.3333 12 11.9303 12 12.6667C12 13.403 11.403 14 10.6667 14C9.93029 14 9.33333 13.403 9.33333 12.6667C9.33333 11.9303 9.93029 11.3333 10.6667 11.3333ZM5.33333 11.3333C6.06971 11.3333 6.66667 11.9303 6.66667 12.6667C6.66667 13.403 6.06971 14 5.33333 14C4.59695 14 4 13.403 4 12.6667C4 11.9303 4.59695 11.3333 5.33333 11.3333ZM10.6667 6.66667C11.403 6.66667 12 7.26362 12 8C12 8.73638 11.403 9.33333 10.6667 9.33333C9.93029 9.33333 9.33333 8.73638 9.33333 8C9.33333 7.26362 9.93029 6.66667 10.6667 6.66667ZM5.33333 6.66667C6.06971 6.66667 6.66667 7.26362 6.66667 8C6.66667 8.73638 6.06971 9.33333 5.33333 9.33333C4.59695 9.33333 4 8.73638 4 8C4 7.26362 4.59695 6.66667 5.33333 6.66667ZM10.6667 2C11.403 2 12 2.59695 12 3.33333C12 4.06971 11.403 4.66667 10.6667 4.66667C9.93029 4.66667 9.33333 4.06971 9.33333 3.33333C9.33333 2.59695 9.93029 2 10.6667 2ZM5.33333 2C6.06971 2 6.66667 2.59695 6.66667 3.33333C6.66667 4.06971 6.06971 4.66667 5.33333 4.66667C4.59695 4.66667 4 4.06971 4 3.33333C4 2.59695 4.59695 2 5.33333 2Z" fill="#4D4D4D"/>
        </svg>
    </span>
    <div class="add-section-end-btn">
            <a onclick="edit_catalogue_section('${catalogue_state.active_section}')" style="cursor: pointer;" class="modal-trigger">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M13.3736 2.62638C14.2088 3.46154 14.2088 4.81562 13.3736 5.65079L6.22097 12.8034C6.0555 12.9689 5.84972 13.0883 5.62395 13.1499L2.56665 13.9837C2.23206 14.075 1.92503 13.7679 2.01629 13.4333L2.8501 10.376C2.91167 10.1503 3.03109 9.9445 3.19656 9.77903L10.3492 2.62638C11.1844 1.79121 12.5385 1.79121 13.3736 2.62638ZM9.76981 4.4736L3.83045 10.4129C3.77529 10.4681 3.73548 10.5367 3.71496 10.6119L3.08754 12.9125L5.38808 12.285C5.46334 12.2645 5.53193 12.2247 5.58709 12.1696L11.5262 6.23004L9.76981 4.4736ZM10.9831 3.26026L10.4033 3.83951L12.1597 5.59655L12.7397 5.0169C13.2248 4.53182 13.2248 3.74534 12.7397 3.26026C12.2547 2.77518 11.4682 2.77518 10.9831 3.26026Z" fill="#0254D7"></path>
        </svg>
        </a>
        <a class="delete-section-btn" onclick="setup_delete_section_modal('${catalogue_state.active_section}')" class="modal-trigger">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path fill-rule="evenodd" clip-rule="evenodd" d="M5.78997 3.33333L5.93819 2.66635C5.97076 2.60661 6.02879 2.52176 6.10562 2.45091C6.19775 2.36595 6.27992 2.33333 6.35185 2.33333H9.31481C9.31449 2.33333 9.31456 2.33334 9.31502 2.33337C9.31797 2.33359 9.33695 2.335 9.36833 2.34383C9.40259 2.35346 9.44447 2.36997 9.48859 2.39625C9.56583 2.44225 9.65609 2.52152 9.72769 2.66283L9.87669 3.33333H5.78997ZM5.15683 4.33333C5.16372 4.33348 5.17059 4.33348 5.17744 4.33333H10.4892C10.4961 4.33348 10.5029 4.33348 10.5098 4.33333H13.1667C13.4428 4.33333 13.6667 4.10948 13.6667 3.83333C13.6667 3.55719 13.4428 3.33333 13.1667 3.33333H10.9011L10.6918 2.39154L10.6809 2.34267L10.6606 2.29693C10.3311 1.55548 9.67791 1.33333 9.31481 1.33333H6.35185C5.9497 1.33333 5.63682 1.52294 5.42771 1.71576C5.22096 1.90642 5.0796 2.13146 5.00606 2.29693L4.98573 2.34267L4.97487 2.39154L4.76558 3.33333H2.5C2.22386 3.33333 2 3.55719 2 3.83333C2 4.10948 2.22386 4.33333 2.5 4.33333H5.15683ZM3.09959 5.00452C3.37324 4.96747 3.6251 5.15928 3.66215 5.43292L4.65773 12.787C4.7031 12.9453 4.80538 13.1798 4.96108 13.369C5.12181 13.5643 5.29845 13.6667 5.5 13.6667H10.5C10.5571 13.6667 10.6813 13.6397 10.7862 13.543C10.8763 13.4599 11 13.2815 11 12.8867V12.853L11.0045 12.8196L12.0045 5.43292C12.0416 5.15928 12.2934 4.96747 12.5671 5.00452C12.8407 5.04157 13.0325 5.29343 12.9955 5.56708L11.9998 12.922C11.9921 13.5331 11.7842 13.9831 11.4638 14.2783C11.1521 14.5657 10.7763 14.6667 10.5 14.6667H5.5C4.90155 14.6667 4.46708 14.3424 4.18892 14.0044C3.9146 13.671 3.75283 13.2816 3.6828 13.0127L3.67522 12.9836L3.67119 12.9537L2.67119 5.56708C2.63414 5.29343 2.82594 5.04157 3.09959 5.00452Z" fill="#E10E00"></path>
        </svg>
        </a>
    </div>
  </div>
    <div class="easychat-whatsapp-menu-data-item">
        <div class="easychat-whatsapp-menu-item-header">
            Section Title
        </div>
        <div class="whatsapp-menu-item-title-wrapper">
            <input type="text" id="section_title_${catalogue_state.active_section}" class="section-title-disabled-input" value="${section_details.section_title}" disabled="">
        </div>
    </div>
    <div class="easychat-whatsapp-menu-data-item">
        <div class="easychat-whatsapp-menu-item-header">
            Product ID/Name
        </div>
        <div class="whatsapp-menu-item-selected-intent-wrapper section-max-height">
            <div class="whatsapp-menu-selected-intent-div">

                <div id="product_ids_${catalogue_state.active_section}" class="whatsapp-menu-selected-intent-items">`
    section_details.product_ids.forEach(product_id => {
        section_html += `<div class="whatsapp-menu-selected-intent-chip">
                            ${get_product_name_if_available(product_id)}
                        </div>`
    })
    section_html += `</div>
                </div>
            </div>
        </div>
    </div>`
    return section_html;
}

/**
 * Adds delete catalogue section function for the section to be deleted in Delete Section Modal.
 * @param section_id is the Section ID to be deleted.
 */
function setup_delete_section_modal(section_id) {
    $("#easychat_whatsapp_menu_delete_modal").modal("open");
    $("#delete_catalogue_section").attr("onclick", "delete_catalogue_section('" + section_id + "')");
}

/**
 * Deletes catlaogue section and removes its information from catalogue state.
 * @param section_id is the Section ID to be deleted.
 */
function delete_catalogue_section(section_id) {
    $("#section_" + section_id).remove();
    delete catalogue_state[section_id];
    $('#easychat_whatsapp_menu_delete_modal').modal('close');
}

/**
 * Opens the modal to edit an existing Catalogue Section.
 * @param section_id is the Section ID to be edited.
 */
function edit_catalogue_section(section_id) {
    reset_section_modal();
    ACTIVE_CATALOGUE_TYPE = catalogue_state[section_id].catalogue_type;
    $('#catalogue_section_heading').text('Edit Section');
    catalogue_state.active_section = section_id;
    $("#easychat_whatsapp_add_section_modal").modal("open");
    $("#catalogue_section_title").val(catalogue_state[section_id].section_title).keyup();
    $("#add_product_id_container input").prop("checked", false)
    catalogue_state[section_id].product_ids.forEach((product_id) => {
        $("#whatsapp_catalog_productid_dragable").append(get_product_id_chip_html(product_id))
        $("#add_product_id_container input[item-retailer-id='" + product_id + "']").prop("checked", true)
    })
    check_section_save_btn_state();
}

/**
 * Updates the catalogue section HTML after editing an existing section.
 * @param section_id is the Section ID of the HTML Div to be updated.
 */
function update_catalogue_section_html(section_id) {
    let section_html = '';
    catalogue_state[section_id].product_ids.forEach(product_id => {
        section_html += `<div class="whatsapp-menu-selected-intent-chip">
                            ${get_product_name_if_available(product_id)}
                        </div>`
    })
    $("#product_ids_" + section_id).html(section_html);
    $("#section_title_" + section_id).val(catalogue_state[section_id].section_title);
}

/**
 * Populates all the data related to WhatsApp Catalogue on page load.
 * @param catalogue_metadata is the metadata of the WhatsApp Catalogue of the selected Bot.
 */
function populate_whatsapp_catalogue_details(api_response, catalogue_via, catalogue_metadata) {
    if ("catalogue_id" in api_response && api_response.catalogue_id.length) {
        $("#catalogue_id_single_product, #catalogue_id_multiple_product, #wa_api_catalogue_id").val(api_response.catalogue_id)
        $("#catalogue_id_single_product, #catalogue_id_multiple_product, #wa_api_catalogue_id").prop("disabled", "disabled")
        $("#catalogue_id_single_product, #catalogue_id_multiple_product, #wa_api_catalogue_id").css("cursor", 'url("/static/EasyChatApp/img/red-not-allowed.svg"), auto')
    }
    if ("catalogue_access_token" in api_response && api_response.catalogue_access_token != "") {
        $("#wa_access_token").val(api_response.catalogue_access_token);
        $("#wa_access_token").prop("disabled", "disabled")
        $("#wa_access_token").css("cursor", 'url("/static/EasyChatApp/img/red-not-allowed.svg"), auto')
    }
    if("catalogue_business_id" in api_response && api_response.catalogue_business_id != "") {
        $("#wa_business_id").val(api_response.catalogue_business_id);
    }
    if ("section_ordering" in catalogue_metadata) {
        for (let index = 0; index < catalogue_metadata.section_ordering.length; index++) {
            let section_id = catalogue_metadata.section_ordering[index]
            catalogue_state.active_section = section_id;
            catalogue_state[section_id] = catalogue_metadata.sections[section_id];
            if(catalogue_via == "commerce_manager_catalogue") {
                $("#catalogue_sections_container").append(
                    get_catalogue_section_html(catalogue_state[catalogue_state.active_section])
                );
            } else {
                $("#add_section_main_div_wrapper").append(
                    get_catalogue_section_html(catalogue_state[catalogue_state.active_section])
                );
            }
        }
    }
    catalogue_state.active_section = null;
    if(catalogue_via == "commerce_manager_catalogue") {
        let catalogue_type = catalogue_metadata.catalogue_type;
        $("input[name='catalogue_product_type'][value=" + catalogue_type + "]").prop('checked', true).change();
        $("#catalog_" + catalogue_type + "_bodytext").trumbowyg('html', catalogue_metadata.body_text);
        $('#footer_text_' + catalogue_type).val(catalogue_metadata.footer_text).keyup();
        $('#catalogue_id_' + catalogue_type).val(catalogue_metadata.catalogue_id);
        if ("merge_cart_enabled" in catalogue_metadata && catalogue_metadata.merge_cart_enabled == "true") {
            $("#wa_commerce_merge_cart_toggle").prop('checked', true).change();
        }
        if("merge_cart_text" in catalogue_metadata) {
            $("#wa_commerce_merge_cart_response").trumbowyg('html', catalogue_metadata.merge_cart_text)
        }
        if (catalogue_type == 'single_product') {
            $('#product_id_single_product').val(catalogue_metadata.product_id)
            return;
        }
        $('#header_text_multiple_product').val(catalogue_metadata.header_text).keyup();

    } else if (catalogue_via == "api_catalogue") {
        if ("merge_cart_enabled" in catalogue_metadata && catalogue_metadata.merge_cart_enabled == "true") {
            $("#wa_api_merge_cart_toggle").prop('checked', true).change();
        }
        if("merge_cart_text" in catalogue_metadata) {
            $("#wa_api_merge_cart_response").trumbowyg('html', catalogue_metadata.merge_cart_text)
        }
        $("#wa_business_id").val(api_response.catalogue_business_id);
        $("#wa_access_token").val(api_response.catalogue_access_token);
        $("#wa_api_catalogue_id").val(catalogue_metadata.catalogue_id);
        $("#wa_api_header_text").val(catalogue_metadata.header_text).keyup();
        $("#wa_api_body_text").trumbowyg("html", catalogue_metadata.body_text);
        $("#wa_api_footer_text").val(catalogue_metadata.footer_text).keyup();
        if(api_response.catalogue_access_token.length) {
            $("#wa_access_token").prop("disabled", "disabled")
            $("#wa_access_token").css("cursor", 'url("/static/EasyChatApp/img/red-not-allowed.svg"), auto')
        }
        if(catalogue_metadata.catalogue_id.length) {
            $("#wa_api_catalogue_id").prop("disabled", "disabled")
            $("#wa_api_catalogue_id").css("cursor", 'url("/static/EasyChatApp/img/red-not-allowed.svg"), auto')
        }
    }
    $("#single_product_body_text_wrapper .trumbowyg-editor, #wa_api_body_text_wrapper .trumbowyg-editor, #wa_multiple_body_text_wrapper .trumbowyg-editor").keyup();
}

function check_section_save_btn_state() {
    let section_title_length = $("#catalogue_section_title").val().length
    let product_ids_length = $("#whatsapp_catalog_productid_dragable span").length
    $(".section-save-btn").css({
        "pointer-events": (section_title_length && product_ids_length) ? "auto" : "none",
        "opacity": (section_title_length && product_ids_length) ? "1" : "0.5"
    })
}

function disable_catalogue_options_for_language_tuning() {
    $(".delete-section-btn, .whatsapp-menu-format-btn, .catalogue-selection-checkbox").css({
        "pointer-events": "none",
        "opacity": "0.5"
    })
    $("#catalog_modal_product_id_input, #add_product_id_input_div").prop('disabled', 'disabled')
    $("#catalog_modal_product_id_input, .preview-input-container-div, #add_product_id_input_div").css("cursor", 'url("/static/EasyChatApp/img/red-not-allowed.svg"), auto')
    $("#whatsapp_catalog_productid_dragable").css("pointer-events", "none")
}

function html_tags_remover(text) {
    return text.replace(/<\/?[^>]+(>|$)/g, "").trim();
}

if (window.location.pathname.indexOf("/chat/channels/whatsapp") != -1) {

    var location_href = window.location.href;
    var location_href = location_href.replace("#", "");
    var location_href = location_href.replace("!", "");
    var bot_id = get_url_vars()['id']
    var json_string = JSON.stringify({
        bot_id: bot_id
    })
    json_string = EncryptVariable(json_string);
    document.getElementById("easychat_whatsapp_channel_preloader").style.display = "block";
    $.ajax({
        url: "/chat/channels/whatsapp/edit/",
        type: "POST",
        data: {
            json_string: json_string
        },
        success: function (response) {
            document.getElementById("easychat_whatsapp_channel_preloader").style.display = "none";
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {

                failure_recommendation_list = response["failure_recommendations"]["items"]
                initial_message_list = response["initial_message"]["items"];
                images = response["initial_message"]["images"];
                videos = response["initial_message"]["videos"];

                if (images != undefined && images != null && images.length > 0) {
                    document.getElementById("uploaded-bot-welcome-image").src = images[0];
                    document.getElementById("uploaded-bot-welcome-image").style.display = "inline-block";
                    $("#remove-bot-welcome-image").show();
                }

                if (videos != undefined && videos != null && videos.length > 0) {
                    document.getElementById("upload-bot-welcome-video-url").value = videos[0];
                }

            } else {
                console.log("Internal server error.");
            }
        },
        error: function (error) {
            document.getElementById("easychat_whatsapp_channel_preloader").style.display = "none";
            console.log("Report this error: ", error)
        }
    });
    add_channel_language_selction_event("whatsapp")
    add_language_dropdown_search_event()
    language_dropdown_close_onclicking_outside_event()
    language_search_dropdown_event()
    open_close_language_dropdown_event()
    $(document).ready(function () {
        create_language_custom_dropdowns();
    });
    $(document).on("click", "#ignore-changes-in-non-primary-language", function (e) {
        let bot_id = (get_url_vars()["id"])
        let channel_name = "WhatsApp"
        ignore_changes_in_non_primary_languages(bot_id, channel_name)
    });
    $(document).on("click", "#auto-fix-changes-in-non-primary-language", function (e) {
        let bot_id = (get_url_vars()["id"])
        let channel_name = "WhatsApp"
        auto_fix_changes_in_non_primary_languages(bot_id, channel_name)
    });

    $("#language-box-options-container .option .item-checkbox").change(function () {

        enable_disable_auto_language_detection_toogle();
        enable_disable_welcome_message_language_change_toogle(true)

    });

    $(document).on("click", "#save-whatsapp-channel-for-non-primary-language", function (e) {
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
        channel_name = "WhatsApp"

        let is_catalogue_enabled = document.getElementById('enable_whatsapp_catalog_cb').checked;

        let catalogue_metadata = {}
        let catalogue_via;
        if (is_catalogue_enabled) {
            catalogue_metadata = get_whatsapp_catalogue_data()
            if($("#enable_whatsapp_catalog_commerce_cb").prop("checked")) {
                catalogue_via = "commerce_manager_catalogue";
            } else {
                catalogue_via = "api_catalogue";
            }
        }
        if ("error_message" in catalogue_metadata) {
            M.toast({
                "html": catalogue_metadata.error_message
            }, 2000);
            return;
        }

        let is_enabled_block_spam_user = $("#enable_block_spam_user")[0].checked
        let query_warning_message_text = $("#query_warning_msg").trumbowyg('html')
        let query_block_message_text = $("#query_block_msg").trumbowyg('html')
        let keywords_warning_message_text = $("#keywords_warning_msg").trumbowyg('html')
        let keywords_block_message_text = $("#keywords_block_msg").trumbowyg('html')

        if (is_enabled_block_spam_user && validation_message != "No Error") {
            M.toast({
                "html": validation_message
            }, 2000);
            return;
        }

        json_string = {
            bot_id: bot_id,
            welcome_message: welcome_message,
            failure_message: failure_message,
            channel_name: channel_name,
            selected_language: selected_language,
            authentication_message: authentication_message,
            save_auto_pop_up_text: false,
            is_catalogue_enabled: is_catalogue_enabled,
            catalogue_metadata: catalogue_metadata,
            catalogue_via: catalogue_via,
            is_enabled_block_spam_user,
            query_warning_message_text,
            query_block_message_text,
            keywords_warning_message_text,
            keywords_block_message_text,
        }
        json_string = JSON.stringify(json_string);
        json_string = EncryptVariable(json_string);
        document.getElementById("easychat_whatsapp_channel_preloader").style.display = "block";
        $.ajax({
            url: "/chat/save-channel-language-tuned-objects/",
            type: "POST",
            data: {
                json_string: json_string
            },
            success: function (response) {
                document.getElementById("easychat_whatsapp_channel_preloader").style.display = "none";
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
}

function toggle_whatsapp_credentials_password_visibilty(){

    let password_ele = document.getElementById("easychat_whatsapp_vendor_password");
    if (password_ele.type === "password") {
        password_ele.type = "text";
        $(".show-password-icon").show()
        $(".hide-password-icon").hide()
    } else {
        password_ele.type = "password";
        $(".show-password-icon").hide()
        $(".hide-password-icon").show()
    }

}

$("#add_product_id_input_div").click(function (event) {
    if(event.target.id != "add_product_id_input_div") return;
    $("#product-id-search-bar1").keyup();
    if ($('#add_product_id_container').css('display') == 'none') {
        $("#add_product_id_container").show();
        $("#add-product-id_dropdown_icon").addClass("product-id-dropdown-active")
    }
    else if ($('#add_product_id_container').css('display') == 'block') {
        $("#add_product_id_container").scrollTop(0);
        $("#add_product_id_container").hide();
        $("#add-product-id_dropdown_icon").removeClass("product-id-dropdown-active")
    }
});

$(document).on('click', function(event) {
    if ($(event.target).closest('#add_product_id_input_div, #add_product_id_container').length === 0) {
        $("#add_product_id_container").scrollTop(0);
        $("#add_product_id_container").hide();
        $("#add-product-id_dropdown_icon").removeClass("product-id-dropdown-active");
    }
    event.stopPropagation();
});

function add_section_product_search() {
    let input, filter, search_value, i, text_value;
    input = document.getElementById("product-id-search-bar1");
    filter = input.value.toUpperCase();
    search_value = document.querySelectorAll('.product-id-item-select .product-id-item-text');
    let count = 0
    for (i = 0; i < search_value.length; i++) {

        text_value = search_value[i].textContent || search_value[i].innerText;
        if (text_value.toUpperCase().indexOf(filter) > -1) {
            search_value[i].parentElement.parentElement.style.display = "";

            count++;

        } else {
            search_value[i].parentElement.parentElement.style.display = "none";
        }
    }
    if (count == 0) {
        document.getElementById('product_item_no_data_found').style.display = "flex";
    } else {
        document.getElementById('product_item_no_data_found').style.display = "none";
    }
}

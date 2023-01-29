var NEW_NODE_DUMMY_DATA = {
    "lazyLoaded": true,
    "name": "",
    "tree_pk": null,
    "intent_response": {
        "response_list": [
            {
                "text_response": "",
                "speech_response": "",
                "text_reprompt_response": "",
                "speech_reprompt_response": "",
                "ssml_response": ""
            }
        ],
        "image_list": [],
        "video_list": [],
        "choice_list": [],
        "recommendation_list": [],
        "card_list": {},
        "modes": {
            "is_typable": "true",
            "is_button": "true",
            "is_slidable": "false",
            "is_date": "false",
            "is_dropdown": "false"
        },
        "modes_param": {
            "is_slidable": [
                {
                    "max": "",
                    "min": "",
                    "step": "",
                    "placeholder": ""
                }
            ],
            "range_slider_list": [
                {}
            ],
            "radio_button_choices": {},
            "check_box_choices": {},
            "drop_down_choices": {}
        },
        "table_list_of_list": "{\"items\": \"\"}",
    },
    "other_settings": {
        "validators": [],
        "child_choices_list": [],
        "intent_children_list": [],
        "is_part_of_suggestion_list": true,
        "is_bot_feedback_required": true,
        "is_child_tree_visible": true,
        "whatsapp_list_message_header": "Options",
        "selected_validator_obj": {},
        "selected_user_authentication": {},
    },
    "necessary_keywords": "",
    "restricted_keywords": "",
    "intent_threshold": "1.0",
    "campaign_link": "None",
    "enable_intent_level_nlp": false,
    "explanation": "",
    "is_custom_order_selected": false,
    "intent_name_list": [],
    "recommeded_intents_dict_list": [],
    "intent_name": "",
    "answer_pk": null,
    "training_data": [],
    "supported_channel_list": [],
    "is_feedback_required": false,
    "order_of_response": [],
    "default_order_of_response": [],
    "whatsapp_menu_section_objs": {},
}

var change_language_triggered = false
var offsetx_max = 0
var node_vertical_position = {}
var auto_fix_selected_tree_pk = null;

$(document).ready(function() {
    $("#easychat-intent-threshold").ionRangeSlider({
        min: 0,
        max: 1,
        step: 0.01
    });

    let intent_id = get_url_vars()["intent_pk"];

    if (intent_id != undefined && intent_id != null && intent_id != '') {
        encrypted_intent_id = EncryptVariable(intent_id);

        let external_function_str = 'function trigger_intent_' + intent_id + '() {\n\n    trigger_chatbot_query("' + encrypted_intent_id + '");\n    return;\n}';
        let editor = ace.edit("easychat_extent_trigger_function_editor-_div");
        editor.setTheme("ace/theme/monokai");
        editor.setReadOnly(true);
        editor.getSession().setMode("ace/mode/javascript");
        editor.setOptions({
            useWrapMode: true,
            highlightActiveLine: true,
            showPrintMargin: false,
            value: external_function_str
        });
    }
    if(document.getElementById("multiple-select-intent-channel-list") != null){
        document.getElementById("multiple-select-intent-channel-list").onchange = function(e){
            check_for_short_name()
            check_for_whatsapp_channel();
        }
    }
    let short_name_input_field = document.getElementById("enter_intent_short_name")
    short_name_input_field.addEventListener('input', () => {
        document.getElementById("short_name_field-char-count").innerHTML = short_name_input_field.value.length
    });
})

function copy_to_clipboard() {

    let ace_lines = document.getElementsByClassName("ace_line");
    let text = "";
    for (let i=0; i<ace_lines.length; i++){
        text += ace_lines[i].innerText;
        if (ace_lines.length-1 != i){
            text += "\n";
        }
    }

    const el = document.createElement('textarea');
    el.value = text;
    document.body.appendChild(el);

    let mac = navigator.userAgent.match(/Mac|ipad|ipod|iphone/i)
    if (!navigator.clipboard) {
        if (mac && mac.toString().trim() == "Mac") {
            let editable = el.contentEditable;
            let readOnly = el.readOnly;

            el.contentEditable = true;
            el.readOnly = true;

            let range = document.createRange();
            range.selectNodeContents(el);

            let selection = window.getSelection();
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
        "html": "Function copied to clipboard"
    }, 2000)

    $('#extent_trigger_copy_function_btn').css("background", "#10B981");
    $('#extent_trigger_copy_function_btn span').text("Copied to Clipboard");
}

$(document).ready(function () {
    $('.easychat-intent-icon-item').click(function(e) {
        $('.easychat-intent-icon-item').each(function() {
            $(this).removeClass('easychat-active-intent-icon');
        })
        $(this).addClass('easychat-active-intent-icon');

        document.getElementById("intent-icon-upload-error-message").innerText = "";
        document.getElementById("intent-icon-upload-error-message").style.display = "none";
    });

    if (is_enable_intent_icon) {

        document.getElementById('drag-drop-input-box').addEventListener('change', (e) => {

            if (window.location.href.indexOf("intent_pk=") == -1) {
                e.target.value = "";
                M.toast({
                    "html": "You can add intent icon after creating intent."
                }, 2000);
                return;
            }

            const input_upload_image = e.target.files[0];
            const reader = new FileReader();

            let file_size = 30000;
            if (input_upload_image.size > file_size) {
                e.target.value = "";
                document.getElementById("intent-icon-upload-error-message").innerText = "Uploaded icon size is more than 30KB";
                document.getElementById("intent-icon-upload-error-message").style.display = "block";
                return;
            }

            let file_path = input_upload_image.name.split(".")[input_upload_image.name.split(".").length - 1].trim().toLowerCase();

            if (file_path != "png" && file_path != "svg") {
                e.target.value = "";
                document.getElementById("intent-icon-upload-error-message").innerText = "File format not supported";
                document.getElementById("intent-icon-upload-error-message").style.display = "block";
                return;
            }
            
            reader.readAsDataURL(input_upload_image);
            reader.onload = function() {
                base64_str = reader.result.split(",")[1];
                uploaded_file = [];
                uploaded_file.push({
                    "filename": input_upload_image.name,
                    "base64_file": base64_str,
                });

                upload_intent_icon_image();

            }
        })
    }
})

async function upload_intent_icon_image() {
    let response = await upload_image();

    if (response && response.status == 200) {
        add_intent_icon(response["src"]);

        $('#upload-icon-section .easychat-intent-icon-upload-div').hide();
        $('#upload-icon-section #image-selected-container').css("display", "inline-flex");
        $('#upload-icon-section #image-selected-container').html(`
        <div class="image-container-div">
            <img width="40px" height="40px" src="${response["src"]}">
            <div onclick="handle_image_cross_btn(this)" class="dismiss-circle">
            <svg width="10" height="10" viewBox="0 0 10 10" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M0.897052 1.05379L0.96967 0.96967C1.23594 0.703403 1.6526 0.679197 1.94621 0.897052L2.03033 0.96967L5 3.939L7.96967 0.96967C8.26256 0.676777 8.73744 0.676777 9.03033 0.96967C9.32322 1.26256 9.32322 1.73744 9.03033 2.03033L6.061 5L9.03033 7.96967C9.2966 8.23594 9.3208 8.6526 9.10295 8.94621L9.03033 9.03033C8.76406 9.2966 8.3474 9.3208 8.05379 9.10295L7.96967 9.03033L5 6.061L2.03033 9.03033C1.73744 9.32322 1.26256 9.32322 0.96967 9.03033C0.676777 8.73744 0.676777 8.26256 0.96967 7.96967L3.939 5L0.96967 2.03033C0.703403 1.76406 0.679197 1.3474 0.897052 1.05379L0.96967 0.96967L0.897052 1.05379Z" fill="#FF0000"/>
            </svg>
            </div>
        </div>`);
    }
}

function handle_image_cross_btn(e) {
    remove_intent_icon();
    $("#upload-icon-section .easychat-intent-icon-upload-div").show();
    $('#upload-icon-section #image-selected-container').hide();
    $("#upload-icon-section #image-selected-container").html("");
    $("#upload-icon-section #drag-drop-input-box").val("");
    setTimeout(()=>{
        $("#upload-icon-section #image-selected-container").removeClass("easychat-active-intent-icon")
    }, 100)
}

function add_intent_icon(icon_src) {
    let json_string = JSON.stringify({
        intent_pk: intent_pk,
        icon_src: icon_src
    })
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    let xhttp = new XMLHttpRequest();
    let params = 'json_string=' + json_string
    xhttp.open("POST", "/chat/add-intent-icon/", false);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                M.toast({
                    "html": "Successfully added intent icon."
                }, 2000);
                document.getElementById("intent-icon-upload-error-message").innerText = "";
                document.getElementById("intent-icon-upload-error-message").style.display = "none";
            } else {
                M.toast({
                    "html": response["message"]
                }, 2000);
                document.getElementById("intent-icon-upload-error-message").innerText = response["message"];
                document.getElementById("intent-icon-upload-error-message").style.display = "block";
            }
        }
    }
    xhttp.send(params);
}

function remove_intent_icon() {
    let json_string = JSON.stringify({
        intent_pk: intent_pk
    })
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    let xhttp = new XMLHttpRequest();
    let params = 'json_string=' + json_string
    xhttp.open("POST", "/chat/remove-intent-icon/", false);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                M.toast({
                    "html": "Successfully removed intent icon."
                }, 2000);
            } else {
                M.toast({
                    "html": response["message"]
                }, 2000);
            }
        }
    }
    xhttp.send(params);
}

function check_for_whatsapp_channel() {
    let selected_channels_list = $("#multiple-select-intent-channel-list").val();
    if(selected_channels_list.includes("WhatsApp")){
        document.getElementById('whatsapp_short_name_field').style.display = 'block';
        document.getElementById('whatsapp_description_field').style.display = 'block';
        document.getElementById('whatsapp_menu_collapsible').style.display = 'block';
    } else {
        document.getElementById('whatsapp_short_name_field').style.display = 'none';
        document.getElementById('whatsapp_description_field').style.display = 'none';
        document.getElementById('whatsapp_menu_collapsible').style.display = 'none';
    }
}

function open_intent_menu_data(evt, menuName) {
    let i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(menuName).style.display = "block";
    evt.currentTarget.className += " active";

    if (menuName === "bot_response") {
        $("#bot_response .tabs").tabs('select', 'intent-bot-response-tab')
    }

    if (menuName === "intent_settings") {
        $("#intent_settings .tabs").tabs('select', 'edit_intent_settings_content')
    }

    document.getElementById("edit_intent_details_data_wrapper").classList.add("easychat-show-intent-details");
    document.getElementById("edit_intent_bot_preview_wrapper").classList.add("shift-preview-right-nav-active");
    // bot_preview_section_show();
    document.getElementById("edit_intent_bot_preview_wrapper").classList.remove("show-preview-expand-right-nav");
    document.getElementById("edit_intent_bot_preview_wrapper").classList.remove("show-preview-collapse-right-nav");

}

function show_details_wrapper() {
    $(".easychat-edit-intent-rightnav-menu-wrapper").show()
    $(".easychat-edit-intent-preview-wrapper").show()
    $("#show_edit_intent_details_wrapper").hide()
    
    document.getElementById("edit_intent_details_data_wrapper").classList.add("easychat-show-intent-details");
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById("create_intent").style.display = "block";

    document.getElementById("create_intent_menu_icon").classList.add("active");
    document.getElementById("edit_intent_bot_preview_wrapper").classList.add("shift-preview-right-nav-active");
    document.getElementById("edit_intent_bot_preview_wrapper").classList.remove("show-preview-expand-right-nav");
    document.getElementById("edit_intent_bot_preview_wrapper").classList.remove("show-preview-collapse-right-nav");
    
}

function hide_details_wrapper() {
    $("#show_edit_intent_details_wrapper").show()
    document.getElementById("edit_intent_details_data_wrapper").classList.remove("easychat-show-intent-details");
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    editor.node_selected = null;
    document.getElementById("edit_intent_bot_preview_wrapper").classList.remove("shift-preview-right-nav-active");
    document.getElementById("edit_intent_bot_preview_wrapper").classList.remove("show-preview-expand-right-nav");
    document.getElementById("edit_intent_bot_preview_wrapper").classList.remove("show-preview-collapse-right-nav");
}

$(document).on("change", "#checkbox-intent-authentication", function(e) {
    if (document.getElementById("checkbox-intent-authentication").checked) {
        $("#div-select-user-authentication").show();
    } else {
        $("#div-select-user-authentication").hide();
    }
});

$("#checkbox-intent-authentication").change();

$(document).on("click", "#checkbox-small-talk-enabled", function(e) {
    if (document.getElementById("checkbox-small-talk-enabled").checked) {
        document.getElementById("checkbox-intent-part-of-suggestionList").checked = false;

        $("#checkbox-intent-part-of-suggestionList").prop("disabled", "disabled");
        document.getElementById("checkbox-intent-feedback").checked = false;
        $("#checkbox-intent-feedback").prop("disabled", "disabled");
    } else {
        // document.getElementById("checkbox-intent-part-of-suggestionList").checked = true;
        $("#checkbox-intent-part-of-suggestionList").removeAttr("disabled", "disabled");
        $("#checkbox-intent-feedback").removeAttr("disabled", "disabled");
    }
});

$(document).on("click", "#checkbox-intent-part-of-suggestionList", function(e) {
    if (document.getElementById("checkbox-intent-part-of-suggestionList").checked) {
        document.getElementById("checkbox-small-talk-enabled").checked = false;
        $("#checkbox-small-talk-enabled").prop("disabled", "disabled");
    } else {
        // document.getElementById("checkbox-small-talk-enabled").checked = true;
        $("#checkbox-small-talk-enabled").removeAttr("disabled", "disabled");
    }
});

$(document).on('click', '#suggest-variations-btn', function () {
    let selected_bot_pk = BOT_ID
    let intent_name = $("#intent_name_input_div").val()
    let json_string = JSON.stringify({
        intent_name: intent_name,
        bot_id: selected_bot_pk,
        page_no: 1
    });
    $("#suggest-variations-btn span")[0].innerHTML = "Generating...."
    setTimeout(function () {
        json_string = EncryptVariable(json_string);
        $.ajax({
            url: '/chat/get-variations/',
            type: "POST",
            data: {
                json_string: json_string
            },
            dataType: "json",
            async: false,
            success: function (response) {
                response = custom_decrypt(response)
                response = JSON.parse(response);
                $("#suggest-variations-btn span")[0].innerHTML = 'Suggest Variations<sup><b> BETA</b></sup>'
                if (response['status'] == 200) {
                    variations = response["variation_list"]
                    more_var = response["more_var"]
                    $("#show-more-variations").hide()
                    if (more_var) {
                        temp_string = "add_more_variation('" + bot_id + "','" + intent_name + "',1)"
                        document.getElementById("show-more-variations").setAttribute("onclick", temp_string)
                        $("#show-more-variations").show()
                    }
                    let stripped_data = node_intent_data[selected_node].training_data.map(function(train) {
                        return train.trim()
                    })
                    variations = variations.reduce((result, sentence)=>{
                        if ( !stripped_data.includes(sentence)) {
                            result.push(sentence)
                        }
                        return result
                    }, [])
                    if (variations.length > 0) {
                        fill_training_data_rhs(variations, false);
                        M.toast({
                            'html': "Variations added successfully!",
                            'displayLength': 3000
                        }, 2000);
                    } else {
                        M.toast({
                            'html': "No Variations generated!",
                            'displayLength': 3000
                        }, 2000);
                    }
                } else {
                    M.toast({
                        'html': "Error while generating Variations!",
                        'displayLength': 3000
                    }, 2000);
                }
            }
        });
    }, 1000)
});

$(document).on("keypress", "#edit_intent_treaning_question_input", function (e) {
    let keycode = (e.keyCode ? e.keyCode : e.which);
    if (keycode == '13') {
        value = $("#edit_intent_treaning_question_input").val();
        fill_training_data_rhs([value], false);
        $("#edit_intent_treaning_question_input").val("");
    }
});

$(document).on("change", ".input.training-sentence", function (e) {
    if (!sanitize_special_characters_from_text(e.currentTarget.value.trim(), 'Training questions cannot contain special characters')) {
        e.currentTarget.parentElement.remove()
    }

    let stripped_data = node_intent_data[selected_node].training_data.map(function(train) {
        return train.trim()
    })

    if (stripped_data.includes(e.currentTarget.value.trim())) {
        e.currentTarget.parentElement.remove()
        M.toast({
            'html': `"${e.currentTarget.value}" is already present in training questions.`,
            'displayLength': 3000
        }, 2000);
    }

    const new_data = []

    for (const elm of $(".input.training-sentence")) {
        new_data.push(elm.value)
    }

    node_intent_data[selected_node].training_data = new_data
});

$(document).on("keypress", "#add_enter_intent_image_url_data", function (e) {
    let keycode = (e.keyCode ? e.keyCode : e.which);
    if (keycode == '13') {
        value = $("#add_enter_intent_image_url_data").val().trim();
        if (isValidURL(value) == false) {
            $("#image_upload_failed span").text("URL/Links added must consist of HTTP/HTTPS, Eg. https://www.google.com")
            $("#image_upload_failed").show()
            setTimeout(function() {
                $("#image_upload_failed").hide()
            }, 3000)
            show_image_upload_div()
            return;
        }
        if (!isExternal(value)) {
            $("#image_upload_failed span").text("URL/Links added must consist of HTTP/HTTPS, Eg. https://www.google.com")
            $("#image_upload_failed").show()
            setTimeout(function() {
                $("#image_upload_failed").hide()
            }, 3000)
            show_image_upload_div()
            return;
        }
        add_images_response_rhs([value], true);
        $("#add_enter_intent_image_url_data").val("");
        node_intent_data[selected_node].intent_response.image_list.push(value)

        $("#image_upload_successfull").show()
        $("#image_upload_failed").hide()
        setTimeout(function() {
            $("#image_upload_successfull").hide()
        }, 2000)
    }
});

$(document).on("keypress", "#add_enter_intent_video_url_data", function (e) {
    let keycode = (e.keyCode ? e.keyCode : e.which);
    if (keycode == '13') {
        let value = $("#add_enter_intent_video_url_data").val().trim();
        if (!isValidURL(value)) {
            M.toast({
                "html": "URL/Links added must consist of HTTP/HTTPS, Eg. https://www.google.com"
            }, 2000);
            return;
        }
        if (!isExternal(value)) {
            showToast("Only external urls allowed.", 2000);
            return;
        }
        add_videos_response_rhs([value], true);
        $("#add_enter_intent_video_url_data").val("");
        node_intent_data[selected_node].intent_response.video_list.push(value)
    }
});

$(document).on("keyup", "#table-generation-space td", function() {
    node_intent_data[selected_node].intent_response.table_list_of_list = `{"items": ${JSON.stringify(check_table_filled())}}`
})

$(document).on("countrychange", "#phone", function() {
    node_intent_data[selected_node].intent_response.modes_param.country_code = $("#phone").intlTelInput("getSelectedCountryData").iso2
})

$(document).on("change", "#channel-GoogleBusinessMessages", function() {
    if ($("#channel-GoogleBusinessMessages")[0].checked) {
        $("#short_name_field").show()
    } else {
        $("#short_name_field").hide()
    }
}) 

$(document).on("change", "#channel-WhatsApp", function() {
    if (!$("#channel-WhatsApp")[0].checked) {
        $("#whatsapp_menu_format_cb").prop("checked", false).trigger("change")
    }
}) 

$(document).on("change", "#channel-WhatsApp", function() {
    if ($("#channel-WhatsApp")[0].checked) {
        $("#whatsapp-specific-text-field").show()
    } else {
        $("#whatsapp-specific-text-field").hide()
    }
}) 

$(document).on("change", "#intent_select_all_chanells_cb", function() {
    if ($("#intent_select_all_chanells_cb")[0].checked) {
        $("#whatsapp-specific-text-field").show()
        $("#short_name_field").show()
    } else {
        $("#whatsapp-specific-text-field").hide()
        $("#short_name_field").hide()
    }
}) 

function generate_table_rhs(table_list_of_list) {
    table_matrix = JSON.parse(table_list_of_list).items;
    tableSpace = document.getElementById('table-generation-space');
    tableSpace.innerHTML = "";
    if (table_matrix != "None" && table_matrix != "") {
        rows = table_matrix.length;
        columns = table_matrix[0].length;
        if (columns <= 4) {
            let theader = '<table style="table-layout: fixed;">\n';
            let tbody = '';

            for (let i = 0; i < rows; i++) {
                // create each row
                tbody += '<tr>';

                for (let j = 0; j < columns; j++) {
                    // create cell
                    tbody += '<td contenteditable="true"id=' + '"cell-id-' + i.toString() + j.toString() + '"' + '>';
                    tbody += un_entity(table_matrix[i][j]);
                    tbody += '</td>'
                }

                // closing row table
                tbody += '</tr>\n';

            }
            let tfooter = '</table>';

            tableSpace.innerHTML = (theader + tbody + tfooter);
            $("#number-of-rows-table").val(rows)
            $("#number-of-columns-table").val(columns)
        }
    }
};

function initialize_carousel(identity) {
    $(identity).carousel({
        fullWidth: true,
        indicators: false,
        noWrap: true,
        dist: 0,
        numVisible: 1,
        onCycleTo: function(slide) {
            try {
                if ($(slide).next().is('.carousel-item')) {
                    $(identity + ' .moveNextCarousel').removeClass("disabled")
                    $(identity + ' .moveNextCarousel').parent().show()
                } else {
                    $(identity + ' .moveNextCarousel').parent().hide()
                }

                if ($(slide).prev().is('.carousel-item')) {
                    $(identity + ' .movePrevCarousel').removeClass("disabled")
                    $(identity + ' .movePrevCarousel').parent().show()
                } else {
                    $(identity + ' .movePrevCarousel').parent().hide()
                }
            } catch {}
        }
    });
}

function add_card_response_rhs(cards, initial) {
    let html = "";
    let tab_html = "";

    if (!initial) {
        let all_cards = node_intent_data[selected_node].intent_response.card_list
        let card_keys = Object.keys(all_cards)
        if (all_cards[card_keys.at(-1)]) {
            let is_valid = validate_card_content([all_cards[card_keys.at(-1)]])
            if (is_valid) {
                all_cards[card_keys.at(-1)] = is_valid
            } else {
                return
            }
        }
    } else if (Object.keys(cards).length === 0) {
        $(".card-response-tabs .tab:not(#dummy_card_tab)").remove()
        $("#response_card_result").html("")
        return
    }
    
    let counter = Object.keys(node_intent_data[selected_node].intent_response.card_list).length
    if (Object.keys(cards).length > 0) {
        let card_counter = 1;
        for (let card of Object.values(cards)) {
            let title = card.title
            title = title ? title : ""
            let content = card.content
            content = content ? content : ""
            let link = card.link
            link = link ? link : ""
            let img_url = card.img_url
            img_url = img_url ? img_url : ""
    
            if (link && link.startsWith("/files/")) {
                link = window.location.protocol + "//" + window.location.host + link;
            }
        
            if (img_url && img_url.startsWith("/files/")) {
                img_url = window.location.protocol + "//" + window.location.host + img_url;
            }
    
            html += `
                <div id="added_card_${card_counter}" class="intent-upload-image-overflow-div response-added-cards">
                    <div class="card-input-div-wrapper">
                        <div class="edit-intent-input-heading-div">
                            <span>
                                Title
                            </span>
                        </div>
                        <div class="edit-intent-input-div">
                            <input type="text" value="${title}" onchange="handle_general_input_change(event,'card_title', ${card_counter})" class="form-control input" id="" placeholder="Card Title">
                        </div>
                    </div>
                    <div class="card-input-div-wrapper">
                        <div class="edit-intent-input-heading-div">
                            <span>
                                Content
                            </span>
                        </div>
                        <div class="edit-intent-input-div">
                            <textarea name="" id="" onchange="handle_general_input_change(event, 'card_content', ${card_counter})" placeholder="Type here">${content}</textarea>
                        </div>
                    </div>
                    <div class="card-input-div-wrapper">
                        <div class="edit-intent-input-heading-div">
                            <span style="height: 20px;" class="tooltipped" data-position="top" data-tooltip="URL/Links added must consist of HTTP/HTTPS, Eg. https://www.google.com">
                                <svg width="18" height="19" viewBox="0 0 18 19" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M9 2.75C12.7279 2.75 15.75 5.77208 15.75 9.5C15.75 13.2279 12.7279 16.25 9 16.25C5.27208 16.25 2.25 13.2279 2.25 9.5C2.25 5.77208 5.27208 2.75 9 2.75ZM8.99743 8.31828C8.65132 8.31851 8.36623 8.57923 8.32747 8.91491L8.32298 8.99362L8.32541 12.7066L8.33 12.7853C8.3692 13.1209 8.65463 13.3813 9.00074 13.3811C9.34685 13.3808 9.63194 13.1201 9.67071 12.7844L9.6752 12.7057L9.67277 8.99273L9.66818 8.91403C9.62897 8.5784 9.34354 8.31805 8.99743 8.31828ZM9.0003 5.78773C8.53382 5.78773 8.15566 6.16589 8.15566 6.63237C8.15566 7.09886 8.53382 7.47702 9.0003 7.47702C9.46679 7.47702 9.84495 7.09886 9.84495 6.63237C9.84495 6.16589 9.46679 5.78773 9.0003 5.78773Z" fill="#4D4D4D"></path>
                                </svg>
                            </span>
                            <span>
                                Link/Pdf
                            </span>
                        </div>
                        <div class="intent-upload-image-wrapper-div">
                            <div class="intent-drag-and-upload-div">
                                <input type="file" style="display: none" onchange="handle_card_link_change(event, ${card_counter})">
                                <div class="intent-drag-drop-file-div" onclick="trigger_card_file_upload(event)" style="">
                                    <svg width="65" height="50" viewBox="0 0 65 50" fill="none"
                                        xmlns="http://www.w3.org/2000/svg">
                                        <path
                                            d="M2.64508 6.65137L2.14508 44.1514C2.14508 48.1514 6.14508 48.6514 7.64508 45.1514L15.6451 20.1514C16.8451 16.9514 19.1451 16.1514 20.1451 16.1514H51.1451V13.6514C51.1451 12.0514 48.8117 11.6514 47.6451 11.6514H29.6451C28.0451 11.6514 26.3117 10.6514 25.6451 10.1514L21.1451 5.65137C19.9451 4.05137 17.9784 3.65137 17.1451 3.65137H6.14508C3.34508 3.65137 2.64508 5.65137 2.64508 6.65137Z"
                                            stroke="#1B65DB" stroke-width="3" />
                                        <path
                                            d="M51.3899 48.9297L4.58014 49.4531C6.55108 48.6158 7.70079 46.6618 8.02928 45.7894L15.913 20.6671C17.0956 16.8987 20.0192 16.3056 21.3331 16.48H59.7664C64.1025 16.48 63.8725 19.6203 63.2156 21.1905L55.8245 45.7894C55.0362 48.3017 52.5396 48.9297 51.3899 48.9297Z"
                                            fill="#1B65DB" />
                                    </svg>
                                    <p>
                                        Drop Your PDF here or 
                                        <a class="color-blue" onclick="trigger_card_file_upload(event)">Browse</a>
                                    </p>
                                    <p>
                                        Supports PDF
                                    </p>
                                    <p class="color-blue">
                                        Maximum - 5 MB
                                    </p>

                                </div>
                            </div>
                            <span class="or-span">or</span>
                            <div class="edit-intent-input-div">
                                <input type="text" class="form-control input" onchange="handle_general_input_change(event, 'card_link', ${card_counter})" value="${link}" id="card_link_${card_counter}" placeholder="URL Link">
                            </div>
                        </div>
                    </div>
                    <div class="card-input-div-wrapper">
                        <div class="edit-intent-input-heading-div">
                            <span style="height: 20px;" class="tooltipped" data-position="top" data-tooltip="URL/Links added must consist of HTTP/HTTPS, Eg. https://www.google.com">
                                <svg width="18" height="19" viewBox="0 0 18 19" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M9 2.75C12.7279 2.75 15.75 5.77208 15.75 9.5C15.75 13.2279 12.7279 16.25 9 16.25C5.27208 16.25 2.25 13.2279 2.25 9.5C2.25 5.77208 5.27208 2.75 9 2.75ZM8.99743 8.31828C8.65132 8.31851 8.36623 8.57923 8.32747 8.91491L8.32298 8.99362L8.32541 12.7066L8.33 12.7853C8.3692 13.1209 8.65463 13.3813 9.00074 13.3811C9.34685 13.3808 9.63194 13.1201 9.67071 12.7844L9.6752 12.7057L9.67277 8.99273L9.66818 8.91403C9.62897 8.5784 9.34354 8.31805 8.99743 8.31828ZM9.0003 5.78773C8.53382 5.78773 8.15566 6.16589 8.15566 6.63237C8.15566 7.09886 8.53382 7.47702 9.0003 7.47702C9.46679 7.47702 9.84495 7.09886 9.84495 6.63237C9.84495 6.16589 9.46679 5.78773 9.0003 5.78773Z" fill="#4D4D4D"></path>
                                </svg>
                            </span>
                            <span>
                                Image
                            </span>
                        </div>
                        `
            if (img_url) {
                html += `
                <div class="intent-upload-image-wrapper-div" id="card_image_result_div_${card_counter}">
                    <div class="intent-file-uploaded-div">
                        <div class="uploaded-img-div">
                            <img src="${img_url}" alt="picture">

                            <div class="uploaded-img-delete" onclick="delete_card_image(event, ${card_counter})">
                                <span>
                                    <svg width="25" height="25" viewBox="0 0 25 25" fill="none"
                                        xmlns="http://www.w3.org/2000/svg">
                                        <path fill-rule="evenodd" clip-rule="evenodd"
                                            d="M8.74675 5.40137L9.02452 4.15137C9.17267 3.81803 9.64674 3.15137 10.3579 3.15137H14.8023C15.0986 3.15137 15.7801 3.35137 16.1356 4.15137L16.4134 5.40137H20.5801C20.9943 5.40137 21.3301 5.73715 21.3301 6.15137C21.3301 6.56558 20.9943 6.90137 20.5801 6.90137H4.58008C4.16586 6.90137 3.83008 6.56558 3.83008 6.15137C3.83008 5.73715 4.16586 5.40137 4.58008 5.40137H8.74675ZM7.08008 19.2314L5.58008 8.15137H19.5801L18.0801 19.2314C18.0801 20.7674 17.0801 21.1514 16.5801 21.1514H9.08008C7.88008 21.1514 7.24674 19.8714 7.08008 19.2314Z"
                                            fill="#FF281A" />
                                    </svg>
                                </span>
                            </div>
                        </div>
                    </div>
                    <span class="or-span">or</span>
                    <div class="edit-intent-input-div">
                        <input type="text" class="form-control input" onchange="handle_general_input_change(event, 'card_image', ${card_counter})" value="${img_url}" id="" placeholder="Image Link">
                    </div>
                </div>
                <div style="display: none;" class="intent-upload-image-wrapper-div" id="card_image_upload_div_${card_counter}">
                `
            } else {
                html += `<div class="intent-upload-image-wrapper-div" id="card_image_upload_div_${card_counter}">`
            }
            html += `
                    <div class="intent-drag-and-upload-div">
                        <input type="file" style="display: none" onchange="handle_card_image_change(event, ${card_counter})">
                        <div class="intent-drag-drop-file-div" onclick="trigger_card_file_upload(event)" style="">
                            <svg width="65" height="50" viewBox="0 0 65 50" fill="none"
                                xmlns="http://www.w3.org/2000/svg">
                                <path
                                    d="M2.64508 6.65137L2.14508 44.1514C2.14508 48.1514 6.14508 48.6514 7.64508 45.1514L15.6451 20.1514C16.8451 16.9514 19.1451 16.1514 20.1451 16.1514H51.1451V13.6514C51.1451 12.0514 48.8117 11.6514 47.6451 11.6514H29.6451C28.0451 11.6514 26.3117 10.6514 25.6451 10.1514L21.1451 5.65137C19.9451 4.05137 17.9784 3.65137 17.1451 3.65137H6.14508C3.34508 3.65137 2.64508 5.65137 2.64508 6.65137Z"
                                    stroke="#1B65DB" stroke-width="3" />
                                <path
                                    d="M51.3899 48.9297L4.58014 49.4531C6.55108 48.6158 7.70079 46.6618 8.02928 45.7894L15.913 20.6671C17.0956 16.8987 20.0192 16.3056 21.3331 16.48H59.7664C64.1025 16.48 63.8725 19.6203 63.2156 21.1905L55.8245 45.7894C55.0362 48.3017 52.5396 48.9297 51.3899 48.9297Z"
                                    fill="#1B65DB" />
                            </svg>
                            <p>
                                Drop Your Image here or 
                                <a class="color-blue">Browse</a>
                            </p>
                            <p>
                                Supports JPG
                            </p>
                            <p class="color-blue">
                                Dimensions 320*225
                            </p>
                            <p class="color-blue">
                                Maximum - 5 MB
                            </p>

                        </div>
                    </div>
                    <span class="or-span">or</span>
                    <div class="edit-intent-input-div">
                        <input type="text" class="form-control input" onchange="handle_general_input_change(event, 'card_image', ${card_counter})" id="" placeholder="Image Link">
                    </div>
                </div>
                    </div>
                </div>
            `
            if (title.length > 20) {
                title = title.substring(0, 20) + "..."
            }
            if (card_counter === 1) {
                tab_html += `
                    <li class="tab">
                        <a class="active" href="#added_card_${card_counter}">
                        <span>${title ? title : "Card Title"}</span>
                           <svg style="margin-left:6px;" onclick="delete_card(event, ${counter})" width="13" height="13" viewBox="0 0 13 13" fill="none" xmlns="http://www.w3.org/2000/svg">
                           <path d="M2.47388 2.59863L9.68627 10.0986" stroke="white" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"/>
                           <path d="M9.68628 2.59863L2.47389 10.0986" stroke="white" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                        </a>
                    </li>
                `
            } else {
                tab_html += `
                    <li class="tab">
                        <a href="#added_card_${card_counter}">
                        <span>${title ? title : "Card Title"}</span>
                        <svg style="margin-left:6px;" onclick="delete_card(event, ${counter})" width="13" height="13" viewBox="0 0 13 13" fill="none" xmlns="http://www.w3.org/2000/svg">
                           <path d="M2.47388 2.59863L9.68627 10.0986" stroke="white" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"/>
                           <path d="M9.68628 2.59863L2.47389 10.0986" stroke="white" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                        </a>
                    </li>
                `
            }
            card_counter += 1
        }
    } else {
        counter += 1
        if (initial) {
            node_intent_data[selected_node].intent_response.card_list = {[counter]: {}}
        } else {
            let card_list_dict = node_intent_data[selected_node].intent_response.card_list
            node_intent_data[selected_node].intent_response.card_list = {...card_list_dict, [counter]: {}}

        }  

        html += `
        <div id="added_card_${counter}" class="intent-upload-card-overflow-div response-added-cards">
            <div class="card-input-div-wrapper">
                <div class="edit-intent-input-heading-div">
                    <span>
                        Title
                    </span>
                </div>
                <div class="edit-intent-input-div">
                    <input type="text" class="form-control input" onchange="handle_general_input_change(event, 'card_title', ${counter})" id="" placeholder="Card Title">
                </div>
            </div>
            <div class="card-input-div-wrapper">
                <div class="edit-intent-input-heading-div">
                    <span>
                        Content
                    </span>
                </div>
                <div class="edit-intent-input-div">
                    <textarea name="" id="" onchange="handle_general_input_change(event, 'card_content', ${counter})" placeholder="Type here"></textarea>
                </div>
            </div>
            <div class="card-input-div-wrapper">
                <div class="edit-intent-input-heading-div">
                    <span style="height: 20px;" class="tooltipped" data-position="top" data-tooltip="URL/Links added must consist of HTTP/HTTPS, Eg. https://www.google.com">
                        <svg width="18" height="19" viewBox="0 0 18 19" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M9 2.75C12.7279 2.75 15.75 5.77208 15.75 9.5C15.75 13.2279 12.7279 16.25 9 16.25C5.27208 16.25 2.25 13.2279 2.25 9.5C2.25 5.77208 5.27208 2.75 9 2.75ZM8.99743 8.31828C8.65132 8.31851 8.36623 8.57923 8.32747 8.91491L8.32298 8.99362L8.32541 12.7066L8.33 12.7853C8.3692 13.1209 8.65463 13.3813 9.00074 13.3811C9.34685 13.3808 9.63194 13.1201 9.67071 12.7844L9.6752 12.7057L9.67277 8.99273L9.66818 8.91403C9.62897 8.5784 9.34354 8.31805 8.99743 8.31828ZM9.0003 5.78773C8.53382 5.78773 8.15566 6.16589 8.15566 6.63237C8.15566 7.09886 8.53382 7.47702 9.0003 7.47702C9.46679 7.47702 9.84495 7.09886 9.84495 6.63237C9.84495 6.16589 9.46679 5.78773 9.0003 5.78773Z" fill="#4D4D4D"></path>
                        </svg>
                    </span>
                    <span>
                        Link/Pdf
                    </span>
                </div>
                <div class="intent-upload-image-wrapper-div">
                    <div class="intent-drag-and-upload-div">
                        <input type="file" style="display: none" onchange="handle_card_link_change(event, ${counter})">
                        <div class="intent-drag-drop-file-div" onclick="trigger_card_file_upload(event)" style="">
                            <svg width="65" height="50" viewBox="0 0 65 50" fill="none"
                                xmlns="http://www.w3.org/2000/svg">
                                <path
                                    d="M2.64508 6.65137L2.14508 44.1514C2.14508 48.1514 6.14508 48.6514 7.64508 45.1514L15.6451 20.1514C16.8451 16.9514 19.1451 16.1514 20.1451 16.1514H51.1451V13.6514C51.1451 12.0514 48.8117 11.6514 47.6451 11.6514H29.6451C28.0451 11.6514 26.3117 10.6514 25.6451 10.1514L21.1451 5.65137C19.9451 4.05137 17.9784 3.65137 17.1451 3.65137H6.14508C3.34508 3.65137 2.64508 5.65137 2.64508 6.65137Z"
                                    stroke="#1B65DB" stroke-width="3" />
                                <path
                                    d="M51.3899 48.9297L4.58014 49.4531C6.55108 48.6158 7.70079 46.6618 8.02928 45.7894L15.913 20.6671C17.0956 16.8987 20.0192 16.3056 21.3331 16.48H59.7664C64.1025 16.48 63.8725 19.6203 63.2156 21.1905L55.8245 45.7894C55.0362 48.3017 52.5396 48.9297 51.3899 48.9297Z"
                                    fill="#1B65DB" />
                            </svg>
                            <p>
                                Drop Your PDF here or 
                                <a class="color-blue">Browse</a>
                            </p>
                            <p>
                                Supports PDF
                            </p>
                            <p class="color-blue">
                                Maximum - 5 MB
                            </p>

                        </div>
                    </div>
                    <span class="or-span">or</span>
                    <div class="edit-intent-input-div">
                        <input type="text" class="form-control input" onchange="handle_general_input_change(event, 'card_link', ${counter})" id="card_link_${counter}" placeholder="URL Link">
                    </div>
                </div>
            </div>
            <div class="card-input-div-wrapper">
                <div class="edit-intent-input-heading-div">
                    <span style="height: 20px;" class="tooltipped" data-position="top" data-tooltip="URL/Links added must consist of HTTP/HTTPS, Eg. https://www.google.com">
                        <svg width="18" height="19" viewBox="0 0 18 19" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M9 2.75C12.7279 2.75 15.75 5.77208 15.75 9.5C15.75 13.2279 12.7279 16.25 9 16.25C5.27208 16.25 2.25 13.2279 2.25 9.5C2.25 5.77208 5.27208 2.75 9 2.75ZM8.99743 8.31828C8.65132 8.31851 8.36623 8.57923 8.32747 8.91491L8.32298 8.99362L8.32541 12.7066L8.33 12.7853C8.3692 13.1209 8.65463 13.3813 9.00074 13.3811C9.34685 13.3808 9.63194 13.1201 9.67071 12.7844L9.6752 12.7057L9.67277 8.99273L9.66818 8.91403C9.62897 8.5784 9.34354 8.31805 8.99743 8.31828ZM9.0003 5.78773C8.53382 5.78773 8.15566 6.16589 8.15566 6.63237C8.15566 7.09886 8.53382 7.47702 9.0003 7.47702C9.46679 7.47702 9.84495 7.09886 9.84495 6.63237C9.84495 6.16589 9.46679 5.78773 9.0003 5.78773Z" fill="#4D4D4D"></path>
                        </svg>
                    </span>
                    <span>
                        Image
                    </span>
                </div>
                <div class="intent-upload-image-wrapper-div" id="card_image_upload_div_${counter}">
                    <div class="intent-drag-and-upload-div">
                        <input type="file" style="display: none" onchange="handle_card_image_change(event, ${counter})">
                        <div class="intent-drag-drop-file-div" onclick="trigger_card_file_upload(event)" style="">
                            <svg width="65" height="50" viewBox="0 0 65 50" fill="none"
                                xmlns="http://www.w3.org/2000/svg">
                                <path
                                    d="M2.64508 6.65137L2.14508 44.1514C2.14508 48.1514 6.14508 48.6514 7.64508 45.1514L15.6451 20.1514C16.8451 16.9514 19.1451 16.1514 20.1451 16.1514H51.1451V13.6514C51.1451 12.0514 48.8117 11.6514 47.6451 11.6514H29.6451C28.0451 11.6514 26.3117 10.6514 25.6451 10.1514L21.1451 5.65137C19.9451 4.05137 17.9784 3.65137 17.1451 3.65137H6.14508C3.34508 3.65137 2.64508 5.65137 2.64508 6.65137Z"
                                    stroke="#1B65DB" stroke-width="3" />
                                <path
                                    d="M51.3899 48.9297L4.58014 49.4531C6.55108 48.6158 7.70079 46.6618 8.02928 45.7894L15.913 20.6671C17.0956 16.8987 20.0192 16.3056 21.3331 16.48H59.7664C64.1025 16.48 63.8725 19.6203 63.2156 21.1905L55.8245 45.7894C55.0362 48.3017 52.5396 48.9297 51.3899 48.9297Z"
                                    fill="#1B65DB" />
                            </svg>
                            <p>
                                Drop Your Image here or 
                                <a class="color-blue">Browse</a>
                            </p>
                            <p>
                                Supports JPG, PNG
                            </p>
                            <p class="color-blue">
                                Dimensions 320*225
                            </p>
                            <p class="color-blue">
                                Maximum - 5 MB
                            </p>

                        </div>
                    </div>
                    <span class="or-span">or</span>
                    <div class="edit-intent-input-div">
                        <input type="text" class="form-control input" onchange="handle_general_input_change(event, 'card_image', ${counter})" id="" placeholder="Image Link">
                    </div>
                </div>
            </div>
        </div>
        `
        tab_html += `<li class="tab">
                <a class="active" href="#added_card_${counter}">
                <span>Card Title</span>
                <svg style="margin-left:6px;" onclick="delete_card(event, ${counter})" width="13" height="13" viewBox="0 0 13 13" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M2.47388 2.59863L9.68627 10.0986" stroke="white" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M9.68628 2.59863L2.47389 10.0986" stroke="white" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"/>
                 </svg>
                </a></li>` 
    }
    
    if (initial) {
        $(".response-added-cards").remove()
        $(".card-response-tabs .tab:not(#dummy_card_tab)").remove()
        $("#response_card_result").html(html)
    } else {
        $("#response_card_result").append(html)
    }

    $(".tooltipped").tooltip()
    
    $(".card-response-tabs").append(tab_html)
    try {
        $('.tabs:not(#response_widget_tab_wrapper)').tabs()
    } catch {}

    if (initial) {
        $(".card-response-tabs").tabs("select", "added_card_1")
    } else {
        $(".card-response-tabs").tabs("select", "added_card_" + counter)
    }
    
}

function delete_card(e, id) {
    $("#added_card_"+ id).remove()
    $(e.currentTarget).parent().parent().remove()

    node_intent_data[selected_node].intent_response.card_list[id] = null
}

function get_cards() {
    return Object.values(node_intent_data[selected_node].intent_response.card_list).filter(function(card) {
        return Boolean(card)
    })
}

function validate_cards() {
    const all_cards = get_cards()
    const last_card = all_cards.at(-1)

    if (all_cards.length > 0) {
        if (!last_card.title || !last_card.content || !last_card.link || !last_card.img_url) {
            return false
        }
    }

    return true
}

function validate_card_content(all_cards) {
    for (const card of all_cards) {
        let tree_card_title = card.title
        let tree_card_content = card.content;
        let tree_card_link = card.link;
        let tree_card_img_url = card.img_url;

        tree_card_title = tree_card_title ? tree_card_title : ""
        tree_card_content = tree_card_content ? tree_card_content : ""
        tree_card_link = tree_card_link ? tree_card_link : ""
        tree_card_img_url = tree_card_img_url ? tree_card_img_url : ""
        tree_card_img_url = tree_card_img_url.trim()
        tree_card_link = tree_card_link.trim()

        let format = /[`#%^*()_+\-=\[\]{};':"\\|,.<>\/~]/;

        if (format.test(tree_card_title.trim())) {

            M.toast({
                "html": "Please provide valid intent card title"
            });
            return;
        }

        tree_card_title = stripHTML(tree_card_title.trim())
        tree_card_title = strip_unwanted_characters(tree_card_title)

        tree_card_content = stripHTML(tree_card_content.trim())
        tree_card_content = strip_unwanted_security_characters(tree_card_content)

        if (tree_card_title == "") {
            M.toast({
                "html": "Please provide valid tree card title."
            });
            return;
        }

        if (tree_card_content.trim() == "") {
            M.toast({
                "html": "Please provide valid tree card content."
            });
            return;
        }

        if (tree_card_link.trim() == "") {
            M.toast({
                "html": "Card link cannot be empty."
            });
            return;
        }

        if (tree_card_img_url.trim() == "") {
            M.toast({
                "html": "Card image cannot be empty."
            });
            return;
        }

        if (isValidURL(tree_card_link) == false) {
            M.toast({
                "html": "URL/Links added must consist of HTTP/HTTPS, Eg. https://www.google.com"
            });
            return;
        }

        if (isValidURL(tree_card_img_url) == false) {
            M.toast({
                "html": "Please provide valid image card url"
            });
            return;
        }

        if (all_cards.length === 1) {
            return {title: tree_card_title, content: tree_card_content, link: tree_card_link, img_url: tree_card_img_url}
        }

    }
    return true

}

function add_images_response_rhs(images, show_image_carousel, initial=false) {
    try {
        $("#only_image_carousel").carousel("destroy")
    } catch {}
    if (initial) {
        $("#only_image_carousel .carousel-item:not(#response_image_upload)").remove()
    }
    if (images && images.length > 0) {
        $("#add_response_video").removeClass("disable-video-recoder-save-value")
        for (let image of images) {
            if (image.startsWith("/files/")) {
                image = window.location.protocol + "//" + window.location.host + url;
            }

            let html = `
            <div class="carousel-item intent-file-uploaded-div" style="transform: translateX(0px) translateX(0px) translateX(0px) translateZ(0px); z-index: 0; opacity: 1; visibility: visible;">
                <div class="uploaded-img-div">
                <img src="${image}" original_src="${image}" alt="${image.split("/").at(-1)}" onerror="this.onerror=null;this.src='/static/EasyChatApp/img/blocked_image.png';"/>

                    <div class="uploaded-img-delete" onclick="delete_uploaded_image(event)">
                        <span>
                            <svg width="25" height="25" viewBox="0 0 25 25" fill="none"
                                xmlns="http://www.w3.org/2000/svg">
                                <path fill-rule="evenodd" clip-rule="evenodd"
                                    d="M8.74675 5.40137L9.02452 4.15137C9.17267 3.81803 9.64674 3.15137 10.3579 3.15137H14.8023C15.0986 3.15137 15.7801 3.35137 16.1356 4.15137L16.4134 5.40137H20.5801C20.9943 5.40137 21.3301 5.73715 21.3301 6.15137C21.3301 6.56558 20.9943 6.90137 20.5801 6.90137H4.58008C4.16586 6.90137 3.83008 6.56558 3.83008 6.15137C3.83008 5.73715 4.16586 5.40137 4.58008 5.40137H8.74675ZM7.08008 19.2314L5.58008 8.15137H19.5801L18.0801 19.2314C18.0801 20.7674 17.0801 21.1514 16.5801 21.1514H9.08008C7.88008 21.1514 7.24674 19.8714 7.08008 19.2314Z"
                                    fill="#FF281A" />
                            </svg>
                        </span>
                    </div>
                </div>
            </div>
            `
            $("#response_image_upload").before(html)
        }

    } else {
        $("#add_response_video").addClass("disable-video-recoder-save-value")
    }

    initialize_carousel("#only_image_carousel")
    $('#only_image_carousel').carousel("next", node_intent_data[selected_node].intent_response.image_list.length - 1)

    if (initial) {
        setTimeout(function() {$("#only_image_carousel").carousel("set", 0)}, 200)
    } else {
        setTimeout(function() {$("#only_image_carousel").carousel("set", node_intent_data[selected_node].intent_response.image_list.length - 1)}, 200)
    }
    

    if (show_image_carousel === true) {
        $(".image-carousel-slider carousel-slider-arrow").show()
    } else if (show_image_carousel === false) {
        $(".image-carousel-slider carousel-slider-arrow").hide()
    }
}

function add_videos_response_rhs(videos, show_video_carousel, initial=false) {
    try {
        $(".carousel.video-carousel-slider").carousel("destroy")
    } catch {}
    let video_count = 0
    if (initial) {
        $(".video-carousel-slider .carousel-item").remove()
    } else {
        video_count = node_intent_data[selected_node].intent_response.video_list.length
    }
    if (videos && videos.length > 0) {
        $(".upload-video-wrapper-div").show()

        for (const video of videos) {
            let html="";
            video_count += 1
            if (isValidURL(video) == false) {
                M.toast({
                    "html": "URL/Links added must consist of HTTP/HTTPS, Eg. https://www.google.com"
                }, 2000);
                return;
            }
        
            let embed_url = getEmbedVideoURL(video);

            html += `
            <div class="carousel-item intent-file-uploaded-div">
                <div class="uploaded-img-div">
            `

            if (embed_url.indexOf("embed") == -1) {
                html += `
                <video width="100%" height="100%" controls>
                  <source src="` + embed_url + `" type="video/mp4">
                </video>
                </div>
                `;
            } else {
                html += `
                <iframe width="100%" height="100%"
                    src="${embed_url}" frameborder="1"
                    allowfullscreen>
                </iframe>
                </div>
                `
            }

            html += `
            <div class="secondary-content" style="margin: auto;
                ">
                <a href="javascript:void(0)" onclick="delete_response_video(event, '${video_count}')">
                <svg width="239" height="33" viewBox="0 0 239 33" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect x="0.0800781" width="238" height="33" rx="4" fill="#FFF9F9"/>
                    <path d="M13.2158 20V12.2979H15.6597C16.4618 12.2979 17.1582 12.4626 17.749 12.792C18.3434 13.1214 18.7928 13.5744 19.0972 14.1509C19.4015 14.7238 19.5537 15.3862 19.5537 16.1382C19.5537 17.3377 19.21 18.2812 18.5225 18.9688C17.835 19.6562 16.8807 20 15.6597 20H13.2158ZM14.4028 18.9634H15.6382C16.4546 18.9634 17.1099 18.7199 17.604 18.2329C18.0981 17.7459 18.3452 17.0477 18.3452 16.1382C18.3452 15.2573 18.0981 14.5716 17.604 14.0811C17.1134 13.5905 16.4582 13.3452 15.6382 13.3452H14.4028V18.9634ZM20.5635 17.1426C20.5635 16.5446 20.6888 16.0146 20.9395 15.5527C21.1901 15.0872 21.5321 14.7292 21.9653 14.4785C22.4022 14.2279 22.8927 14.1025 23.437 14.1025C23.8739 14.1025 24.2713 14.1795 24.6294 14.3335C24.9875 14.4875 25.2829 14.6987 25.5156 14.9673C25.752 15.2358 25.9328 15.5492 26.0581 15.9072C26.187 16.2653 26.2515 16.6502 26.2515 17.062V17.4917H21.7183C21.7397 17.9966 21.9098 18.403 22.2285 18.7109C22.5472 19.0189 22.9679 19.1729 23.4907 19.1729C23.856 19.1729 24.1818 19.0905 24.4683 18.9258C24.7583 18.7611 24.9606 18.5391 25.0752 18.2598H26.1978C26.0474 18.8255 25.7269 19.2821 25.2363 19.6294C24.7493 19.9731 24.1567 20.145 23.4585 20.145C22.6027 20.145 21.9062 19.8639 21.3691 19.3018C20.832 18.736 20.5635 18.0163 20.5635 17.1426ZM21.7397 16.6001H25.1074C25.0716 16.1274 24.8979 15.755 24.5864 15.4829C24.2749 15.2072 23.8918 15.0693 23.437 15.0693C22.993 15.0693 22.6099 15.2126 22.2876 15.499C21.9653 15.7855 21.7827 16.1525 21.7397 16.6001ZM27.3955 18.5713V11.75H28.5503V18.5015C28.5503 18.6554 28.5879 18.7736 28.6631 18.856C28.7383 18.9383 28.8475 18.9795 28.9907 18.9795H29.2324V20H28.7598C28.3265 20 27.9899 19.8747 27.75 19.624C27.5137 19.3734 27.3955 19.0225 27.3955 18.5713ZM30.1025 17.1426C30.1025 16.5446 30.2279 16.0146 30.4785 15.5527C30.7292 15.0872 31.0711 14.7292 31.5044 14.4785C31.9412 14.2279 32.4318 14.1025 32.9761 14.1025C33.4129 14.1025 33.8104 14.1795 34.1685 14.3335C34.5265 14.4875 34.8219 14.6987 35.0547 14.9673C35.291 15.2358 35.4718 15.5492 35.5972 15.9072C35.7261 16.2653 35.7905 16.6502 35.7905 17.062V17.4917H31.2573C31.2788 17.9966 31.4489 18.403 31.7676 18.7109C32.0863 19.0189 32.507 19.1729 33.0298 19.1729C33.395 19.1729 33.7209 19.0905 34.0073 18.9258C34.2974 18.7611 34.4997 18.5391 34.6143 18.2598H35.7368C35.5864 18.8255 35.266 19.2821 34.7754 19.6294C34.2884 19.9731 33.6958 20.145 32.9976 20.145C32.1418 20.145 31.4453 19.8639 30.9082 19.3018C30.3711 18.736 30.1025 18.0163 30.1025 17.1426ZM31.2788 16.6001H34.6465C34.6107 16.1274 34.437 15.755 34.1255 15.4829C33.814 15.2072 33.4308 15.0693 32.9761 15.0693C32.5321 15.0693 32.1489 15.2126 31.8267 15.499C31.5044 15.7855 31.3218 16.1525 31.2788 16.6001ZM36.7197 15.1929V14.2583H37.4771C37.5773 14.2583 37.6597 14.2243 37.7241 14.1562C37.7886 14.0882 37.8208 13.9969 37.8208 13.8823V12.6201H38.9058V14.2476H40.5815V15.1929H38.9058V18.1416C38.9058 18.7288 39.1851 19.0225 39.7437 19.0225H40.5225V20H39.5664C38.9935 20 38.5477 19.8442 38.229 19.5327C37.9103 19.2176 37.751 18.7646 37.751 18.1738V15.1929H36.7197ZM41.543 17.1426C41.543 16.5446 41.6683 16.0146 41.9189 15.5527C42.1696 15.0872 42.5116 14.7292 42.9448 14.4785C43.3817 14.2279 43.8722 14.1025 44.4165 14.1025C44.8534 14.1025 45.2508 14.1795 45.6089 14.3335C45.967 14.4875 46.2624 14.6987 46.4951 14.9673C46.7314 15.2358 46.9123 15.5492 47.0376 15.9072C47.1665 16.2653 47.231 16.6502 47.231 17.062V17.4917H42.6978C42.7192 17.9966 42.8893 18.403 43.208 18.7109C43.5267 19.0189 43.9474 19.1729 44.4702 19.1729C44.8354 19.1729 45.1613 19.0905 45.4478 18.9258C45.7378 18.7611 45.9401 18.5391 46.0547 18.2598H47.1772C47.0269 18.8255 46.7064 19.2821 46.2158 19.6294C45.7288 19.9731 45.1362 20.145 44.438 20.145C43.5822 20.145 42.8857 19.8639 42.3486 19.3018C41.8115 18.736 41.543 18.0163 41.543 17.1426ZM42.7192 16.6001H46.0869C46.0511 16.1274 45.8774 15.755 45.5659 15.4829C45.2544 15.2072 44.8713 15.0693 44.4165 15.0693C43.9725 15.0693 43.5894 15.2126 43.2671 15.499C42.9448 15.7855 42.7622 16.1525 42.7192 16.6001ZM51.1572 15.1929V14.2583H51.9146C52.0148 14.2583 52.0972 14.2243 52.1616 14.1562C52.2261 14.0882 52.2583 13.9969 52.2583 13.8823V12.6201H53.3433V14.2476H55.019V15.1929H53.3433V18.1416C53.3433 18.7288 53.6226 19.0225 54.1812 19.0225H54.96V20H54.0039C53.431 20 52.9852 19.8442 52.6665 19.5327C52.3478 19.2176 52.1885 18.7646 52.1885 18.1738V15.1929H51.1572ZM56.3887 20V11.75H57.5327V15.0156H57.6079C57.7404 14.7578 57.9552 14.5412 58.2524 14.3657C58.5496 14.1903 58.9006 14.1025 59.3052 14.1025C59.9461 14.1025 60.46 14.312 60.8467 14.731C61.2334 15.1463 61.4268 15.6709 61.4268 16.3047V20H60.272V16.5249C60.272 16.131 60.1449 15.8088 59.8906 15.5581C59.64 15.3075 59.3302 15.1821 58.9614 15.1821C58.5675 15.1821 58.2327 15.3164 57.957 15.585C57.6813 15.8499 57.5435 16.1847 57.5435 16.5894V20H56.3887ZM62.9146 12.6094C62.9146 12.3981 62.9862 12.2244 63.1294 12.0884C63.2726 11.9523 63.4535 11.8843 63.6719 11.8843C63.8975 11.8843 64.0819 11.9523 64.2251 12.0884C64.3719 12.2244 64.4453 12.3981 64.4453 12.6094C64.4453 12.8278 64.3719 13.005 64.2251 13.1411C64.0819 13.2772 63.8975 13.3452 63.6719 13.3452C63.4499 13.3452 63.2673 13.2772 63.124 13.1411C62.9844 13.005 62.9146 12.8278 62.9146 12.6094ZM63.0918 20V14.2476H64.2466V20H63.0918ZM65.5732 18.2974H66.6636C66.7388 18.8953 67.1577 19.1943 67.9204 19.1943C68.2928 19.1943 68.5811 19.1191 68.7852 18.9688C68.9928 18.8148 69.0967 18.6089 69.0967 18.3511C69.0967 18.1613 69.034 18.0091 68.9087 17.8945C68.7869 17.7764 68.6258 17.6904 68.4253 17.6367C68.2284 17.5794 68.0099 17.5311 67.77 17.4917C67.5301 17.4523 67.2902 17.4004 67.0503 17.3359C66.814 17.2715 66.5955 17.1855 66.395 17.0781C66.1981 16.9707 66.0369 16.8096 65.9116 16.5947C65.7899 16.3763 65.729 16.1077 65.729 15.7891C65.729 15.2985 65.9295 14.8957 66.3306 14.5806C66.7316 14.2619 67.258 14.1025 67.9097 14.1025C68.5005 14.1025 68.9946 14.2565 69.3921 14.5645C69.7896 14.8724 70.0098 15.2949 70.0527 15.832H68.9946C68.9624 15.5814 68.8496 15.3844 68.6562 15.2412C68.4629 15.098 68.1979 15.0264 67.8613 15.0264C67.5426 15.0264 67.2866 15.0962 67.0933 15.2358C66.9035 15.3719 66.8086 15.5492 66.8086 15.7676C66.8086 15.918 66.8569 16.0433 66.9536 16.1436C67.0539 16.2438 67.1828 16.3154 67.3403 16.3584C67.5015 16.4014 67.6841 16.4443 67.8882 16.4873C68.0923 16.5267 68.3 16.5625 68.5112 16.5947C68.7261 16.627 68.9355 16.6825 69.1396 16.7612C69.3438 16.84 69.5246 16.9367 69.6821 17.0513C69.8433 17.1623 69.9722 17.3252 70.0688 17.54C70.1691 17.7549 70.2192 18.0073 70.2192 18.2974C70.2192 18.8488 70.008 19.2946 69.5854 19.6348C69.1665 19.9749 68.6007 20.145 67.8882 20.145C67.1756 20.145 66.6206 19.9803 66.2231 19.6509C65.8293 19.3179 65.6126 18.8667 65.5732 18.2974ZM74.0327 12.2979H75.3164L77.4863 18.5498H77.5508L79.7529 12.2979H81.0742L78.1792 20H76.8687L74.0327 12.2979ZM81.9819 12.6094C81.9819 12.3981 82.0535 12.2244 82.1968 12.0884C82.34 11.9523 82.5208 11.8843 82.7393 11.8843C82.9648 11.8843 83.1493 11.9523 83.2925 12.0884C83.4393 12.2244 83.5127 12.3981 83.5127 12.6094C83.5127 12.8278 83.4393 13.005 83.2925 13.1411C83.1493 13.2772 82.9648 13.3452 82.7393 13.3452C82.5173 13.3452 82.3346 13.2772 82.1914 13.1411C82.0518 13.005 81.9819 12.8278 81.9819 12.6094ZM82.1592 20V14.2476H83.314V20H82.1592ZM85.3389 19.3125C84.8232 18.7575 84.5654 18.0342 84.5654 17.1426C84.5654 16.251 84.8215 15.5223 85.3335 14.9565C85.8455 14.3872 86.5026 14.1025 87.3047 14.1025C87.5625 14.1025 87.8042 14.1383 88.0298 14.21C88.2554 14.2816 88.4434 14.3747 88.5938 14.4893C88.7477 14.6038 88.8695 14.7095 88.959 14.8062C89.0485 14.8993 89.1237 14.9924 89.1846 15.0854H89.2651V11.75H90.4199V20H89.2866V19.1836H89.2168C88.762 19.8245 88.1426 20.145 87.3584 20.145C86.5312 20.145 85.8581 19.8675 85.3389 19.3125ZM85.7417 17.1265C85.7417 17.7209 85.9046 18.1989 86.2305 18.5605C86.5599 18.9186 86.9914 19.0977 87.5249 19.0977C88.062 19.0977 88.4917 18.9097 88.814 18.5337C89.1362 18.1577 89.2974 17.6886 89.2974 17.1265C89.2974 16.5213 89.1291 16.0433 88.7925 15.6924C88.4595 15.3379 88.0334 15.1606 87.5142 15.1606C86.9914 15.1606 86.5653 15.3451 86.2358 15.7139C85.9064 16.0791 85.7417 16.55 85.7417 17.1265ZM91.6768 17.1426C91.6768 16.5446 91.8021 16.0146 92.0527 15.5527C92.3034 15.0872 92.6453 14.7292 93.0786 14.4785C93.5155 14.2279 94.006 14.1025 94.5503 14.1025C94.9871 14.1025 95.3846 14.1795 95.7427 14.3335C96.1007 14.4875 96.3962 14.6987 96.6289 14.9673C96.8652 15.2358 97.0461 15.5492 97.1714 15.9072C97.3003 16.2653 97.3647 16.6502 97.3647 17.062V17.4917H92.8315C92.853 17.9966 93.0231 18.403 93.3418 18.7109C93.6605 19.0189 94.0812 19.1729 94.604 19.1729C94.9692 19.1729 95.2951 19.0905 95.5815 18.9258C95.8716 18.7611 96.0739 18.5391 96.1885 18.2598H97.311C97.1606 18.8255 96.8402 19.2821 96.3496 19.6294C95.8626 19.9731 95.27 20.145 94.5718 20.145C93.716 20.145 93.0195 19.8639 92.4824 19.3018C91.9453 18.736 91.6768 18.0163 91.6768 17.1426ZM92.853 16.6001H96.2207C96.1849 16.1274 96.0112 15.755 95.6997 15.4829C95.3882 15.2072 95.005 15.0693 94.5503 15.0693C94.1063 15.0693 93.7231 15.2126 93.4009 15.499C93.0786 15.7855 92.896 16.1525 92.853 16.6001ZM98.3584 17.1265C98.3584 16.5571 98.4873 16.0415 98.7451 15.5796C99.0065 15.1177 99.37 14.756 99.8354 14.4946C100.301 14.2332 100.824 14.1025 101.404 14.1025C101.984 14.1025 102.505 14.235 102.967 14.5C103.432 14.765 103.792 15.1284 104.046 15.5903C104.304 16.0487 104.433 16.5607 104.433 17.1265C104.433 17.6922 104.302 18.2061 104.041 18.668C103.783 19.1263 103.422 19.488 102.956 19.7529C102.491 20.0143 101.97 20.145 101.393 20.145C100.512 20.145 99.7853 19.8604 99.2124 19.291C98.6431 18.7181 98.3584 17.9966 98.3584 17.1265ZM99.5347 17.1265C99.5347 17.6994 99.7083 18.172 100.056 18.5444C100.407 18.9132 100.852 19.0977 101.393 19.0977C101.937 19.0977 102.383 18.9115 102.73 18.5391C103.081 18.1667 103.257 17.6958 103.257 17.1265C103.257 16.5535 103.081 16.0827 102.73 15.7139C102.383 15.3451 101.937 15.1606 101.393 15.1606C100.849 15.1606 100.403 15.3468 100.056 15.7192C99.7083 16.0881 99.5347 16.5571 99.5347 17.1265Z" fill="#2D2D2D"/>
                    <path d="M210.175 11.9551H211.689H223.808" stroke="#E10E00" stroke-width="1.51481" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M213.962 11.9554V10.4406C213.962 10.0388 214.121 9.65354 214.405 9.36946C214.689 9.08538 215.075 8.92578 215.476 8.92578H218.506C218.908 8.92578 219.293 9.08538 219.577 9.36946C219.861 9.65354 220.021 10.0388 220.021 10.4406V11.9554M222.293 11.9554V22.5591C222.293 22.9608 222.134 23.3461 221.849 23.6302C221.565 23.9143 221.18 24.0739 220.778 24.0739H213.204C212.803 24.0739 212.417 23.9143 212.133 23.6302C211.849 23.3461 211.689 22.9608 211.689 22.5591V11.9554H222.293Z" stroke="#E10E00" stroke-width="1.51481" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                </a>
            </div>
            </div>
            `
            $(".video-carousel-slider").prepend(html)
        }

        initialize_carousel(".carousel.video-carousel-slider")
    }

    if (show_video_carousel === true) {
        $(".upload-video-wrapper-div").show()
    } else if (show_video_carousel === false) {
        $(".upload-video-wrapper-div").hide()
    }
}

function delete_response_video(e, video) {
    e.currentTarget.parentElement.parentElement.remove()
    node_intent_data[selected_node].intent_response.video_list = node_intent_data[selected_node].intent_response.video_list.filter(function(vid, idx) {
        return idx != video - 1
    })

    if (node_intent_data[selected_node].intent_response.video_list.length === 0) {
        $(".upload-video-wrapper-div").hide()
    }

    initialize_carousel(".carousel.video-carousel-slider")
}

function add_calendar_widget_rhs(modes) {
    if (modes.is_single_datepicker === "true") {

        document.getElementById("enabledatepicker_switch1").checked = true

        document.querySelector(".single-date").disabled = false;
        document.querySelector(".custom-date").disabled = false;
        document.getElementById('single-date-picker-radio').checked = true
        document.getElementById('custom-date-picker-radio').checked = false
    }

    if (modes.is_multi_datepicker  === "true") {
        document.getElementById("enabledatepicker_switch1").checked = true

        document.querySelector(".single-date").disabled = false;
        document.querySelector(".custom-date").disabled = false;
        document.getElementById('single-date-picker-radio').checked = false
        document.getElementById('custom-date-picker-radio').checked = true
    }

    if (modes.is_single_timepicker  === "true") {
        document.getElementById("enabletimepicker_switch2").checked = true

        document.querySelector(".single-time").disabled = false;
        document.querySelector(".custom-time").disabled = false;
        document.getElementById('single-time-picker-radio').checked = true
        document.getElementById('custom-time-picker-radio').checked = false
    }

    if (modes.is_multi_timepicker  === "true") {
        document.getElementById("enabletimepicker_switch2").checked = true

        document.querySelector(".single-time").disabled = false;
        document.querySelector(".custom-time").disabled = false;
        document.getElementById('single-time-picker-radio').checked = false
        document.getElementById('custom-time-picker-radio').checked = true
    }
}

function edit_radio(e) {
    if ($(e.currentTarget).parent().attr("value") === e.currentTarget.value.trim()) {
        e.currentTarget.value = e.currentTarget.value.trim()
        return
    }
    $(e.currentTarget).parent().attr("value", e.currentTarget.value.trim())

    if (node_intent_data[selected_node].intent_response.modes_param.radio_button_choices.includes(e.currentTarget.value.trim())) {
        $(e.currentTarget).parent().remove()
        showToast("Choice already exists(All choices must be different)")
    }

    node_intent_data[selected_node].intent_response.modes_param.radio_button_choices = $("#sortable-radio-widget-edit-div").sortable("toArray", {attribute: "value"})
}

function delete_radio(e) {
    $(e.currentTarget).parent().remove()
    node_intent_data[selected_node].intent_response.modes_param.radio_button_choices = node_intent_data[selected_node].intent_response.modes_param.radio_button_choices.filter(function(radio) {
        return radio !== $(e.currentTarget).prev().val()
    })
}

function add_radio_widget_rhs(radio_data, initial) {
    if (radio_data.length > 0) {
        let html="";

        for (let radio of radio_data) {
            radio = radio.trim()
            html += `
            <div class="response-widget-dragable-output-item" value="${radio}">
                <div class="dragable-item-icon tooltip-custom">
                    <svg width="24" height="25" viewBox="0 0 24 25" fill="none"
                        xmlns="http://www.w3.org/2000/svg">
                        <path fill-rule="evenodd" clip-rule="evenodd"
                            d="M16.9998 6.5C16.9998 7.6 16.0998 8.5 14.9998 8.5C13.8998 8.5 12.9998 7.6 12.9998 6.5C12.9998 5.4 13.8998 4.5 14.9998 4.5C16.0998 4.5 16.9998 5.4 16.9998 6.5ZM8.9998 4.5C7.8998 4.5 6.9998 5.4 6.9998 6.5C6.9998 7.6 7.8998 8.5 8.9998 8.5C10.0998 8.5 10.9998 7.6 10.9998 6.5C10.9998 5.4 10.0998 4.5 8.9998 4.5ZM6.99976 12.5C6.99976 11.4 7.89976 10.5 8.99976 10.5C10.0998 10.5 10.9998 11.4 10.9998 12.5C10.9998 13.6 10.0998 14.5 8.99976 14.5C7.89976 14.5 6.99976 13.6 6.99976 12.5ZM8.99976 20.5C10.0998 20.5 10.9998 19.6 10.9998 18.5C10.9998 17.4 10.0998 16.5 8.99976 16.5C7.89976 16.5 6.99976 17.4 6.99976 18.5C6.99976 19.6 7.89976 20.5 8.99976 20.5ZM14.9998 10.5C13.8998 10.5 12.9998 11.4 12.9998 12.5C12.9998 13.6 13.8998 14.5 14.9998 14.5C16.0998 14.5 16.9998 13.6 16.9998 12.5C16.9998 11.4 16.0998 10.5 14.9998 10.5ZM12.9998 18.5C12.9998 17.4 13.8998 16.5 14.9998 16.5C16.0998 16.5 16.9998 17.4 16.9998 18.5C16.9998 19.6 16.0998 20.5 14.9998 20.5C13.8998 20.5 12.9998 19.6 12.9998 18.5Z"
                            fill="#DADADA"></path>
                    </svg>
                    <div class="tooltiptext-custom tooltip-bottom-custom">Drag to move</div>
                </div>
                <div class="widget-indigator-icon">
                    <svg width="24" height="25" viewBox="0 0 24 25" fill="none"
                        xmlns="http://www.w3.org/2000/svg">
                        <path fill-rule="evenodd" clip-rule="evenodd"
                            d="M5 12C5 8.136 8.136 5 12 5C15.864 5 19 8.136 19 12C19 15.864 15.864 19 12 19C8.136 19 5 15.864 5 12ZM6.39959 12C6.39959 15.094 8.90559 17.6 11.9996 17.6C15.0936 17.6 17.5996 15.094 17.5996 12C17.5996 8.90597 15.0936 6.39997 11.9996 6.39997C8.90559 6.39997 6.39959 8.90597 6.39959 12Z"
                            fill="#C4C4C4"></path>
                    </svg>
                </div>
                <input class="edit_radio_button_choices"
                    type="text" maxlength="100" onchange="edit_radio(event)"
                    value="${radio}">
                <div class="widget-delete-icon" onclick="delete_radio(event)">
                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none"
                        xmlns="http://www.w3.org/2000/svg">
                        <path d="M1.67261 1.5L10.3275 10.5" stroke="#4D4D4D"
                            stroke-width="1.125" stroke-linecap="round"
                            stroke-linejoin="round" />
                        <path d="M10.3274 1.5L1.67252 10.5" stroke="#4D4D4D"
                            stroke-width="1.125" stroke-linecap="round"
                            stroke-linejoin="round" />
                    </svg>
                </div>
            </div>
            `
            if (!initial) {
                node_intent_data[selected_node].intent_response.modes_param.radio_button_choices.push(radio)
                $("#sortable-radio-widget-edit-div").append(html)
            } else {
                $("#sortable-radio-widget-edit-div").html(html)
            }
        }

        $("#sortable-radio-widget-edit-div").sortable({
            containment: "parent",
            update: function() {
                node_intent_data[selected_node].intent_response.modes_param.radio_button_choices = $("#sortable-radio-widget-edit-div").sortable("toArray", {attribute: "value"})
            }
        });
    }
}

function edit_checkbox(e, id) {
    if ($(e.currentTarget).parent().attr("value") === e.currentTarget.value.trim()) {
        e.currentTarget.value = e.currentTarget.value.trim()
        return
    }
    $(e.currentTarget).parent().attr("value", e.currentTarget.value.trim())

    if (node_intent_data[selected_node].intent_response.modes_param.check_box_choices.includes(e.currentTarget.value.trim())) {
        $(e.currentTarget).parent().remove()
        showToast("Choice already exists(All choices must be different)")
    }

    node_intent_data[selected_node].intent_response.modes_param.check_box_choices = $("#sortable-checkbox-widget-edit-div").sortable("toArray", {attribute: "value"})
}

function delete_checkbox(e) {
    $(e.currentTarget).parent().remove()
    node_intent_data[selected_node].intent_response.modes_param.check_box_choices = node_intent_data[selected_node].intent_response.modes_param.check_box_choices.filter(function(check) {
        return check !== $(e.currentTarget).prev().val()
    })
}

function add_checkbox_widget_rhs(checkbox_data, initial) {
    if (checkbox_data.length > 0) {
        let html="";

        for (let checkbox of checkbox_data) {
            checkbox = checkbox.trim()
            html += `
            <div class="response-widget-dragable-output-item" value="${checkbox}">
                <div class="dragable-item-icon tooltip-custom">
                    <svg width="24" height="25" viewBox="0 0 24 25" fill="none"
                        xmlns="http://www.w3.org/2000/svg">
                        <path fill-rule="evenodd" clip-rule="evenodd"
                            d="M16.9998 6.5C16.9998 7.6 16.0998 8.5 14.9998 8.5C13.8998 8.5 12.9998 7.6 12.9998 6.5C12.9998 5.4 13.8998 4.5 14.9998 4.5C16.0998 4.5 16.9998 5.4 16.9998 6.5ZM8.9998 4.5C7.8998 4.5 6.9998 5.4 6.9998 6.5C6.9998 7.6 7.8998 8.5 8.9998 8.5C10.0998 8.5 10.9998 7.6 10.9998 6.5C10.9998 5.4 10.0998 4.5 8.9998 4.5ZM6.99976 12.5C6.99976 11.4 7.89976 10.5 8.99976 10.5C10.0998 10.5 10.9998 11.4 10.9998 12.5C10.9998 13.6 10.0998 14.5 8.99976 14.5C7.89976 14.5 6.99976 13.6 6.99976 12.5ZM8.99976 20.5C10.0998 20.5 10.9998 19.6 10.9998 18.5C10.9998 17.4 10.0998 16.5 8.99976 16.5C7.89976 16.5 6.99976 17.4 6.99976 18.5C6.99976 19.6 7.89976 20.5 8.99976 20.5ZM14.9998 10.5C13.8998 10.5 12.9998 11.4 12.9998 12.5C12.9998 13.6 13.8998 14.5 14.9998 14.5C16.0998 14.5 16.9998 13.6 16.9998 12.5C16.9998 11.4 16.0998 10.5 14.9998 10.5ZM12.9998 18.5C12.9998 17.4 13.8998 16.5 14.9998 16.5C16.0998 16.5 16.9998 17.4 16.9998 18.5C16.9998 19.6 16.0998 20.5 14.9998 20.5C13.8998 20.5 12.9998 19.6 12.9998 18.5Z"
                            fill="#DADADA"></path>
                    </svg>
                    <div class="tooltiptext-custom tooltip-bottom-custom">Drag to move</div>
                </div>
                <div class="widget-indigator-icon" style="height: 20px;">
                    <svg width="19" height="19" viewBox="0 0 19 19" fill="none"
                        xmlns="http://www.w3.org/2000/svg">
                        <path fill-rule="evenodd" clip-rule="evenodd"
                            d="M4.25 2.75H14.75C15.575 2.75 16.25 3.425 16.25 4.25V14.75C16.25 15.575 15.575 16.25 14.75 16.25H4.25C3.425 16.25 2.75 15.575 2.75 14.75V4.25C2.75 3.425 3.425 2.75 4.25 2.75ZM5 14.75H14C14.4125 14.75 14.75 14.4125 14.75 14V5C14.75 4.5875 14.4125 4.25 14 4.25H5C4.5875 4.25 4.25 4.5875 4.25 5V14C4.25 14.4125 4.5875 14.75 5 14.75Z"
                            fill="#C4C4C4"></path>
                    </svg>
                </div>
                <input type="text" maxlength="100" class="edit_radio_button_choices"
                    onchange="edit_checkbox(event)"
                    value="${checkbox}">
                <div class="widget-delete-icon" onclick="delete_checkbox(event)">
                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none"
                        xmlns="http://www.w3.org/2000/svg">
                        <path d="M1.67261 1.5L10.3275 10.5" stroke="#4D4D4D"
                            stroke-width="1.125" stroke-linecap="round"
                            stroke-linejoin="round" />
                        <path d="M10.3274 1.5L1.67252 10.5" stroke="#4D4D4D"
                            stroke-width="1.125" stroke-linecap="round"
                            stroke-linejoin="round" />
                    </svg>
                </div>
            </div>
            `
            if (!initial) {
                node_intent_data[selected_node].intent_response.modes_param.check_box_choices.push(checkbox)
            }
        }

        $("#sortable-checkbox-widget-edit-div").append(html)
        $("#sortable-checkbox-widget-edit-div").sortable({
            containment: "parent",
            update: function() {
                node_intent_data[selected_node].intent_response.modes_param.check_box_choices = $("#sortable-checkbox-widget-edit-div").sortable("toArray", {attribute: "value"})
            }
        });
    }
}

function edit_dropdown(e) {
    if ($(e.currentTarget).parent().attr("value") === e.currentTarget.value.trim()) {
        e.currentTarget.value = e.currentTarget.value.trim()
        return
    }
    $(e.currentTarget).parent().attr("value", e.currentTarget.value.trim())

    if (node_intent_data[selected_node].intent_response.modes_param.drop_down_choices.includes(e.currentTarget.value.trim())) {
        $(e.currentTarget).parent().remove()
        showToast("Choice already exists(All choices must be different)")
    }

    node_intent_data[selected_node].intent_response.modes_param.drop_down_choices = $("#sortable-dropdown-widget-edit-div").sortable("toArray", {attribute: "value"})
}

function delete_dropdown(e) {
    $(e.currentTarget).parent().remove()
    node_intent_data[selected_node].intent_response.modes_param.drop_down_choices = node_intent_data[selected_node].intent_response.modes_param.drop_down_choices.filter(function(drop) {
        return drop !== $(e.currentTarget).prev().val()
    })
}

function add_dropdown_widget_rhs(dropdown_data, initial) {
    if (dropdown_data.length > 0) {
        let html="";

        for (let dropdown of dropdown_data) {
            dropdown = dropdown.trim()
            html += `
            <div class="response-widget-dragable-output-item" value="${dropdown}">
                <div class="dragable-item-icon tooltip-custom">
                    <svg width="24" height="25" viewBox="0 0 24 25" fill="none"
                        xmlns="http://www.w3.org/2000/svg">
                        <path fill-rule="evenodd" clip-rule="evenodd"
                            d="M16.9998 6.5C16.9998 7.6 16.0998 8.5 14.9998 8.5C13.8998 8.5 12.9998 7.6 12.9998 6.5C12.9998 5.4 13.8998 4.5 14.9998 4.5C16.0998 4.5 16.9998 5.4 16.9998 6.5ZM8.9998 4.5C7.8998 4.5 6.9998 5.4 6.9998 6.5C6.9998 7.6 7.8998 8.5 8.9998 8.5C10.0998 8.5 10.9998 7.6 10.9998 6.5C10.9998 5.4 10.0998 4.5 8.9998 4.5ZM6.99976 12.5C6.99976 11.4 7.89976 10.5 8.99976 10.5C10.0998 10.5 10.9998 11.4 10.9998 12.5C10.9998 13.6 10.0998 14.5 8.99976 14.5C7.89976 14.5 6.99976 13.6 6.99976 12.5ZM8.99976 20.5C10.0998 20.5 10.9998 19.6 10.9998 18.5C10.9998 17.4 10.0998 16.5 8.99976 16.5C7.89976 16.5 6.99976 17.4 6.99976 18.5C6.99976 19.6 7.89976 20.5 8.99976 20.5ZM14.9998 10.5C13.8998 10.5 12.9998 11.4 12.9998 12.5C12.9998 13.6 13.8998 14.5 14.9998 14.5C16.0998 14.5 16.9998 13.6 16.9998 12.5C16.9998 11.4 16.0998 10.5 14.9998 10.5ZM12.9998 18.5C12.9998 17.4 13.8998 16.5 14.9998 16.5C16.0998 16.5 16.9998 17.4 16.9998 18.5C16.9998 19.6 16.0998 20.5 14.9998 20.5C13.8998 20.5 12.9998 19.6 12.9998 18.5Z"
                            fill="#DADADA"></path>
                    </svg>
                    <div class="tooltiptext-custom tooltip-bottom-custom">Drag to move</div>
                </div>
                <input type="text" maxlength="100" class="edit_radio_button_choices"
                    onchange="edit_dropdown(event)"
                    value="${dropdown}">
                <div class="widget-delete-icon" onclick="delete_dropdown(event)">
                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none"
                        xmlns="http://www.w3.org/2000/svg">
                        <path d="M1.67261 1.5L10.3275 10.5" stroke="#4D4D4D"
                            stroke-width="1.125" stroke-linecap="round"
                            stroke-linejoin="round" />
                        <path d="M10.3274 1.5L1.67252 10.5" stroke="#4D4D4D"
                            stroke-width="1.125" stroke-linecap="round"
                            stroke-linejoin="round" />
                    </svg>
                </div>
            </div>
            `
            if (!initial) {
                node_intent_data[selected_node].intent_response.modes_param.drop_down_choices.push(dropdown)
            }
        }

        $("#sortable-dropdown-widget-edit-div").append(html)
        $("#sortable-dropdown-widget-edit-div").sortable({
            containment: "parent",
            update: function() {
                node_intent_data[selected_node].intent_response.modes_param.drop_down_choices = $("#sortable-dropdown-widget-edit-div").sortable("toArray", {attribute: "value"})
            }
        });
    }
}

function add_rhs_other_settings_for_root(other_data, widget_required_data) {
    $("#select-user-validator").val("")
    $("#select-user-authentication").val("")
    $('#multiple-select-child-choices').val("")
    $('#select-intent-processor').val("")
    $("#select_section_options_container input").prop("checked", false)
    $("#select-sections-container").empty();
    
    if (node_intent_data[selected_node].isRoot) {
        $("#intent_settings_faq_div").show()
        $("#intent_settings_suggestion_div").show()
        $("#intent_settings_small_talk_div").show()
        $("#feedback_div").show()
        $(".div-select-user-authentication").show()
        $("#confirm_reset_div").hide()

        $("#checkbox_faq_intent").prop("disabled", false)
        $("#checkbox-intent-part-of-suggestionList").prop("disabled", false)
        if (other_data.intent_children_list.length > 0 || other_data.is_quick_recommendation_present) {
            $("#checkbox_faq_intent").prop("disabled", true)
        } 
        if (other_data.is_faq_intent) {
            $("#checkbox_faq_intent").prop("checked", true)
        } else {
            $("#checkbox_faq_intent").prop("checked", false)
        }

        if (other_data.is_small_talk) {
            $("#checkbox-intent-part-of-suggestionList").prop("disabled", true)
        } 
        if (other_data.is_part_of_suggestion_list) {
            $("#checkbox-small-talk-enabled").prop("disabled", true)
            $("#checkbox-intent-part-of-suggestionList").prop("checked", true)
        } else {
            $("#checkbox-small-talk-enabled").prop("disabled", false)
            $("#checkbox-intent-part-of-suggestionList").prop("checked", false)
        }

        if (other_data.is_small_talk) {
            $("#checkbox-small-talk-enabled").prop("checked", true)
        } else {
            $("#checkbox-small-talk-enabled").prop("checked", false)
        }

        if (node_intent_data[selected_node].is_bot_feedback_required) {
            $("#checkbox-intent-feedback").prop("disabled", false)
            $("#feedback_div").show()
            if (other_data.is_small_talk) {
                $("#checkbox-intent-feedback").prop("disabled", true)
            } 
            if (other_data.is_feedback_required) {
                $("#checkbox-intent-feedback").prop("checked", true)
            } else {
                $("#checkbox-intent-feedback").prop("checked", false)
            }
        } else {
            $("#feedback_div").hide()
        }

        if (other_data.authentication_objs.length > 0) {
            let auth_html = ""
            for (const auth of other_data.authentication_objs) {
                if (other_data.selected_user_authentication && auth.id == other_data.selected_user_authentication.id) {
                    auth_html += `<option value="${auth.id }" selected>${auth.name}</option>`
                } else {
                    auth_html += `<option value="${auth.id }">${auth.name}</option>`
                }
            }
            if (!other_data.selected_user_authentication) {
                other_data.selected_user_authentication = other_data.authentication_objs[0]
            }
            $('#select-user-authentication').html(auth_html)
            $('#select-user-authentication').select2().on('select2:open', function(e) {
                $('.select2-search__field').attr('placeholder', 'Search Here');
            });
            $(".div-select-user-authentication-dropdown").show()
            $(".div-select-user-authentication").show()

            if (other_data.is_authentication_required) {
                $("#checkbox-intent-authentication").prop("checked", true)
            } else {
                $("#checkbox-intent-authentication").prop("checked", false)
                $(".div-select-user-authentication-dropdown").hide()
            }
        } else {
            other_data.is_authentication_required = false
            $(".div-select-user-authentication-dropdown").hide()
            $(".div-select-user-authentication").hide()
        }

        // Adding available catalogue sections into sections dropdown
        if($("#select_section_options_container").attr("sections_appended") == "false") {
            let catalogue_sections = JSON.parse(node_intent_data[selected_node].catalogue_sections)
            for (const section_id in catalogue_sections){
                let dropdown_option_html = `<li class="select-section-item available-section-option select-section-item-select" style="">
                                                <label>
                                                    <input type="checkbox" section-id="${section_id}" value="${catalogue_sections[section_id]}" id="section_${section_id}"
                                                        style="position:relative;opacity:1;width: unset !important;margin-top: 0 !important;height: 1.4rem !important;pointer-events: auto;cursor: pointer;">
                                                    <div class="select-section-item-text">${catalogue_sections[section_id]}</div>
                                                </label>
                                            </li>`
                $("#select_section_options_container").append(dropdown_option_html)
            }
            $("#select_section_options_container").attr("sections_appended", "true")
            $("#select_section_options_container input").on("change", function (event) {
                let selected_catalogue_sections = []
                if (this.checked) {
                    $("#select-sections-container").append(get_selected_section_chip_html(this.id, this.value));
                    add_event_listeners_for_sections_chips();
                } else {
                    let section_id = this.id.split("_")
                    section_id = section_id[section_id.length - 1]
                    $("#chip_" + section_id).remove();
                }
                $("#select_section_options_container input:checked").each((indx, ele) => {
                    selected_catalogue_sections.push($(ele).attr("section-id"))
                })
                node_intent_data[selected_node].intent_response.modes_param.temp_selected_catalogue_sections = selected_catalogue_sections
            });
        }

    } else {
        $("#intent_settings_faq_div").hide()
        $("#intent_settings_suggestion_div").hide()
        $("#intent_settings_small_talk_div").hide()
        $("#feedback_div").hide()
        $(".div-select-user-authentication").hide()
        $("#confirm_reset_div").show()

        if (other_data.is_confirmation_and_reset_enabled) {
            $("#checkbox-confirmation-and-reset-enabled").prop("checked", true)
        } else {
            $("#checkbox-confirmation-and-reset-enabled").prop("checked", false)
        }
    }

    let validator_html = ""

    for (const validator of other_data.validators) {
        if (other_data.selected_validator_obj && validator.processor__pk == other_data.selected_validator_obj.processor__pk) {
            validator_html += `<option value="${validator.processor__pk}" selected>${validator.name}</option>`
        } else {
            validator_html += `<option value="${validator.processor__pk}">${validator.name}</option>`
        }
    }

    if (!other_data.selected_validator_obj) {
        other_data.selected_validator_obj = {processor__pk: ""}
    }

    $("#select-user-validator").append(validator_html)
    $('#select-user-validator').select2().on('select2:open', function(e) {
        $('.select2-search__field').attr('placeholder', 'Search Here');
    });

    if (other_data.is_child_tree_visible) {
        $("#checkbox-intent-child-tree-options-visible").prop("checked", true)
    } else {
        $("#checkbox-intent-child-tree-options-visible").prop("checked", false)
    }

    if (other_data.show_go_back_checkbox) {
        $("#go_back_div").show()
        if (other_data.is_go_back_enabled) {
            $("#checkbox-tree-go-back-enabled").prop("checked", true)
        } else {
            $("#checkbox-tree-go-back-enabled").prop("checked", false)
        }
    } else {
        $("#go_back_div").hide()
    }

    let child_html = ""
    if (other_data.choices_order_changed) {
        if (other_data.child_choices_list.length !== other_data.intent_children_list.length) {
            let new_child_list = []
            for (const child of other_data.child_choices_list) {
                if (other_data.intent_children_list.includes(child)) {
                    new_child_list.push(child)
                }
            }
            for (const child of other_data.intent_children_list) {
                if (!other_data.child_choices_list.includes(child)) {
                    new_child_list.push(child)
                }
            }
            other_data.child_choices_list = new_child_list
        }
        for (const child of other_data.child_choices_list) {
            child_html += `<option value="${child}" selected>${child}</option>`
        }
    } else {
        for (const child of other_data.intent_children_list) {
            child_html += `<option value="${child}">${child}</option>`
        }
    }
    
    $('#multiple-select-child-choices').html(child_html)
    $('#multiple-select-child-choices').select2({
        placeholder: "Search"
    }).on('select2:open', function(e) {
        $('#child-choices-dropdown .select2-search__field').attr('placeholder', 'Search');
    });

    if (other_data.is_last_tree) {
        $("#checkbox-last-tree").prop("checked", true)
    } else {
        $("#checkbox-last-tree").prop("checked", false)
    }

    $("#disposition_code").val(other_data.disposition_code)

    if (other_data.is_exit_tree) {
        $("#checkbox-exit-tree").prop("checked", true)
    } else {
        $("#checkbox-exit-tree").prop("checked", false)
    }

    if (other_data.is_transfer_tree) {
        $("#checkbox-transfer-tree").prop("checked", true)
    } else {
        $("#checkbox-transfer-tree").prop("checked", false)
    }

    if (other_data.allow_barge) {
        $("#checkbox-allow-barge").prop("checked", true)
    } else {
        $("#checkbox-allow-barge").prop("checked", false)
    }

    if (other_data.is_item_purchased) {
        $("#checkbox_is_item_purchased").prop("checked", true)
    } else {
        $("#checkbox_is_item_purchased").prop("checked", false)
    }

    $("#whatsapp-list-message-header").val(other_data.whatsapp_list_message_header)

    if (widget_required_data.is_catalogue_added === "true") {
        $("#add_catalogue_checkbox").prop("checked", true)
        $("#catalogue_section_dropdown_div").show();
    } else {
        $("#add_catalogue_checkbox").prop("checked", false)
        $("#catalogue_section_dropdown_div").hide();
    }

    if ("selected_catalogue_sections" in node_intent_data[selected_node].intent_response.modes_param) {
        for (section_id of node_intent_data[selected_node].intent_response.modes_param.selected_catalogue_sections) {
            $("#select_section_options_container input[section-id=" + section_id + "]").prop("checked", true).change();
        }
    }

    if (is_new_intent == "False") {
        $("option[value=external-trigger-intent]").prop("disabled", false)
    } else {
        $("option[value=external-trigger-intent]").prop("disabled", true)
    }
    
}

function fill_training_data_rhs(training_data, initial) {
    let node_id = selected_node
    if (initial) {
        $(".edit-intent-treaning-question-item-div").remove()
    }
    for (let sentence of training_data) {
        sentence = sentence.trim()
        if (sentence.trim() == "") {
            continue;
        }
        if (!sanitize_special_characters_from_text(sentence, 'Training questions cannot contain special characters')) {
            continue
        }

        let stripped_data = node_intent_data[selected_node].training_data.map(function(train) {
            return train.trim()
        })

        if (!initial && stripped_data.includes(sentence)) {
            M.toast({
                "html": "This training sentence already exists"
            }, 2000);
            continue
        } else if (!initial) {
            node_intent_data[node_id].training_data.push(sentence)
        }

        $("#training_show_more").before(`
        <div class="edit-intent-treaning-question-item-div">
            <input type="text" class="input training-sentence" value="${sentence}">
            <a href="#" class="training-question-delete-btn" onclick="remove_training_questions(event, ${node_id}, '${sentence}')">
                <svg width="13" height="13" viewBox="0 0 13 13" fill="none"
                    xmlns="http://www.w3.org/2000/svg">
                    <path d="M1.71069 2.11353L10.1484 10.8877" stroke="#2D2D2D" stroke-width="1.09678"
                        stroke-linecap="round" stroke-linejoin="round" />
                    <path d="M10.1484 2.11353L1.71069 10.8877" stroke="#2D2D2D" stroke-width="1.09678"
                        stroke-linecap="round" stroke-linejoin="round" />
                </svg>
            </a>
        </div>
        `)
    }
}

function handle_language_direction() {
    let rtl_css = {}
    if (LANGUAGE_DIRECTION == "rtl") {
        rtl_css = {
            "direction": "rtl",
            "text-align": "right"
        }
    } else {
        rtl_css = {
            "direction": "unset",
            "text-align": "unset"
        }
    }

    $(".node-wrapper-div span").css({...rtl_css, "text-align": "unset"})
    $(".trumbowyg-editor").css(rtl_css)
    $("#table-generation-space td").css(rtl_css)
    $(".intent_name_input_div").css(rtl_css)
    $("#response_card_result textarea").css(rtl_css)
    $("#response_card_result input[type=text]").first().css(rtl_css)
    
}

function fill_rhs_with_data_for_root(data) {
    $('.easychat-dropdown-select-custom').removeClass('open')
    language_tablinks_change()
    if (node_intent_data[selected_node].isRoot) {
        $("#create_intent_menu_icon span").html(`
            <p>Intent Name &</p><p style="margin-top: 2px !important">Training Questions</p>
        `)
        $( "#create_intent_menu_icon span" ).addClass( "two-line-tooltiptext" )
    } else {
        $("#create_intent_menu_icon span").html(`
            <p>Child Intent Name</p>
        `)
        $( "#create_intent_menu_icon span" ).removeClass( "two-line-tooltiptext" )
    }

    // Intent name
    $("#intent_name_input_div").val(data.name)
    $(".intent_name_input_div:not(#intent_name_input_div)").val(data.name)
    if ($(".intent_name_tooltip").length) {
        $(".intent_name_tooltip").attr("data-tooltip", data.name)
    } else {
        $(".intent_name_input_div:not(#intent_name_input_div)").wrap(`
        <span class="tooltipped intent_name_tooltip" style="flex-grow: 2;" data-position="bottom" data-tooltip="${data.name}"></span>
        `)
        $(".tooltipped").tooltip()
    }

    //Bot Response
    let sentence_list = []
    let image_list = []
    let video_list = []
    let card_list = []
    let table_list_of_list = {}
    let show_image_carousel = false
    let show_video_carousel = false

    let bot_response_data = data.intent_response;
    sentence_list = bot_response_data["response_list"]
    image_list = bot_response_data["image_list"]
    video_list = bot_response_data["video_list"]
    card_list = bot_response_data["card_list"]
    table_list_of_list = bot_response_data["table_list_of_list"]

    // Bot Response - Text
    if (sentence_list.length > 0) {

        let text_response = ""
        let speech_response = ""
        let reprompt_response = ""
        let ssml_response = ""

        text_response = sentence_list[0]["text_response"]
        speech_response = sentence_list[0]["speech_response"]
        if ("text_reprompt_response" in sentence_list[0]) {
            reprompt_response = sentence_list[0]["text_reprompt_response"]
        }
        if("ssml_response" in sentence_list[0]) {
            ssml_response = sentence_list[0]["ssml_response"]
        }

        $("#intent_bot_response_text_text").trumbowyg('html', text_response)
        $("#intent_bot_response_text_speech").trumbowyg('html', speech_response)
        $("#intent_bot_response_reprompt").trumbowyg('html', reprompt_response)
        $("#intent_bot_response_ssml").trumbowyg('html', ssml_response)

    }

    // Bot Response - Table
    $("#number-of-rows-table").val("")
    $("#number-of-columns-table").val("")
    generate_table_rhs(table_list_of_list)

    //Bot Response - Cards
    if (Array.isArray(card_list)) {
        let card_obj = {}
        let card_counter = 1;
        for (const card of card_list) {
            card_obj[card_counter] = card
            card_counter += 1
        }
        node_intent_data[selected_node].intent_response.card_list = card_obj
    }
    card_list = node_intent_data[selected_node].intent_response.card_list
    add_card_response_rhs(card_list, true)

    handle_language_direction()

    if (SELECTED_LANGUAGE !== "en") {
        $("#preview_show_hide_div").hide()
        $("#response_image_tab").hide()
        $("#response_video_tab").hide()
        $("#ssml_response_div").hide()
        $("#add_bot_response_card_btn").hide();
        open_intent_menu_data({currentTarget: $("#edit_bot_response_icon")[0]}, 'bot_response')
        $("#secondary_intent_name_input_div").prop("readonly", false)
        if (Object.keys(card_list).length == 0) {
            $("#response_cards_tab").hide();
            $("#response_tables_tab").css({"margin-right" : "290px"})
        } else {
            $("#response_cards_tab").show();
            $("#response_tables_tab").css({"margin-right" : ""})
        }
        return
    } else {
        $("#preview_show_hide_div").show()
        $("#ssml_response_div").show()
        $("#response_image_tab, #response_cards_tab").show()
        $("#response_video_tab").show()
        $("#add_bot_response_card_btn").show();
        $("#secondary_intent_name_input_div").prop("readonly", true)
        $("#response_tables_tab").css({"margin-right" : ""})
    }

    //Bot Response - Image
    $("#add_enter_intent_image_url_data").val("")
    if (image_list && image_list.length > 0) show_image_carousel = true;
    add_images_response_rhs(image_list, show_image_carousel, true)

    //Bot Response - Video
    $("#add_enter_intent_video_url_data").val("")
    if (video_list && video_list.length > 0) show_video_carousel = true;
    add_videos_response_rhs(video_list, show_video_carousel, true)

    // Fill training 
    if (data.isRoot) {
        $("#parent_training").show()
        $("#child_training").hide()
        data.training_data && fill_training_data_rhs(data.training_data, true)
    } else {
        $("#parent_training").hide()
        $("#child_training").show()

        $("#enter_tree_short_name").val(data.short_name_value)
        $("#tree_short_name_field-char-count").text(data.short_name_value?.length)
        if (data.short_name_enabled) {
            $("#enter_tree_short_name").parent().show()
        } else {
            $("#enter_tree_short_name").parent().hide()
        }

        $("#tree-whatsapp-short-name-input").val(data.whatsapp_short_name)
        $("#tree_whatsapp_short_name_field-char-count").text(data.whatsapp_short_name?.length)

        $("#tree-whatsapp-description-input").val(data.whatsapp_description)
        $("#tree_whatsapp_description_field-char-count").text(data.whatsapp_description?.length)

        $("#tree_accept_keywords").val(data.accept_keywords)

    }

    // Widget Response
    cancel_all_widget(false)
    let widget_required_data = bot_response_data.modes
    let widget_field_data = bot_response_data.modes_param
    if (!widget_field_data.range_slider_list) {
        widget_field_data.range_slider_list = [{}]
    }
    if (!widget_field_data.radio_button_choices) {
        widget_field_data.radio_button_choices = []
    }
    if (!widget_field_data.check_box_choices) {
        widget_field_data.check_box_choices = []
    }
    if (!widget_field_data.drop_down_choices) {
        widget_field_data.drop_down_choices = []
    }
    
    if (widget_required_data.is_calender === "true") {
        $(".intent-response-widget-tabs-wrapper .tabs").tabs('select', 'calendar_picker_widget_content');
        add_calendar_widget_rhs(widget_required_data)
    } else if (widget_required_data.is_radio_button  === "true") {
        $(".intent-response-widget-tabs-wrapper .tabs").tabs('select', 'radio_widget_content');
        add_radio_widget_rhs(widget_field_data.radio_button_choices, true)
    } else if (widget_required_data.is_check_box  === "true") {
        $(".intent-response-widget-tabs-wrapper .tabs").tabs('select', 'checkbox_widget_content');
        add_checkbox_widget_rhs(widget_field_data.check_box_choices, true)
    } else if (widget_required_data.is_drop_down  === "true") {
        $(".intent-response-widget-tabs-wrapper .tabs").tabs('select', 'dropdown_widget_content');
        add_dropdown_widget_rhs(widget_field_data.drop_down_choices, true)
    } else if (widget_required_data.is_video_recorder_allowed  === "true") {
        $(".intent-response-widget-tabs-wrapper .tabs").tabs('select', 'video_widget_content');
        $("#checkbox-intent-video-recorder").trigger( "click" )
        if (widget_required_data.is_save_video_attachment  === "true") {
            $("#checkbox-intent-save-video-attachment").prop("checked", true)
        }
    } else if (widget_required_data.is_range_slider  === "true") {
        $(".intent-response-widget-tabs-wrapper .tabs").tabs('select', 'range_slider_widget_content');
        if (widget_field_data.range_slider_list[0].range_type === "single-range-slider") {
            $("#single-range-slider").trigger( "click" )
        } else {
            $("#multi-range-slider").trigger( "click" )
        }
        $("#range-slider-min-range").val(widget_field_data.range_slider_list[0]?.min)
        $("#range-slider-max-range").val(widget_field_data.range_slider_list[0]?.max)
    } else if (widget_required_data.is_attachment_required  === "true") {
        $(".intent-response-widget-tabs-wrapper .tabs").tabs('select', 'file_attach_widget_content');
        $("#checkbox-intent-attachment").trigger( "click" )
        $("#choosen_file_type").val(widget_field_data.choosen_file_type).trigger( "change" )

        if (widget_required_data.is_save_attachment_required  === "true") {
            $("#checkbox-intent-save-attachment").prop("checked", true)
        }
    } else if (widget_required_data.is_phone_widget_enabled  === "true") {
        $(".intent-response-widget-tabs-wrapper .tabs").tabs('select', 'phone_number_widget_content');
        $("#checkbox-intent-country-code-cb").trigger( "click" )
        if (widget_field_data.country_code) {
            $("#phone").intlTelInput("setCountry", widget_field_data.country_code);
        } else {
            $("#phone").intlTelInput("setCountry", "in");
        }   
    } else if (widget_required_data.is_create_form_allowed  === "true") {
        $(".intent-response-widget-tabs-wrapper .tabs").tabs('select', 'create_form_widget_content');
        $("#form_name").val(widget_field_data.form_name)
        if (!Array.isArray(widget_field_data.form_fields_list)) {
            widget_field_data.form_fields_list =  JSON.parse(widget_field_data.form_fields_list)
        }
        add_initial_form_sections(widget_field_data.form_fields_list)
    }

    if (widget_required_data.is_attachment_required !== "true") {
        $('#choosen_file_type').val("").trigger("change");
        widget_required_data.is_save_attachment_required = "false";
    }

    if (widget_required_data.is_radio_button != "true") {
        widget_field_data.radio_button_choices = []
    }

    if (widget_required_data.is_check_box != "true") {
        widget_field_data.check_box_choices = []
    }

    if (widget_required_data.is_drop_down != "true") {
        widget_field_data.drop_down_choices = []
    }

    if (widget_required_data.is_create_form_allowed != "true") {
        widget_field_data.form_fields_list = []
    }

    if (!$(".intent-widget-overflow-div-content div.active").attr("id")) {
        $("#response_widget .edit-intent-details-action-btns-wrapper button").addClass("disable-video-recoder-save-value")
    } else {
        $("#response_widget .edit-intent-details-action-btns-wrapper button").removeClass("disable-video-recoder-save-value")
    }

    // Channel Settings
    if ($(".edit-intent-channel-btn:not(:checked)").length === 0) {
        $("#intent_select_all_chanells_cb").prop("checked", true)
    }

    // Other Settings
    cancel_bot_settings(true, false)
    add_rhs_other_settings_for_root(data.other_settings, widget_required_data)

    // Advanced Settings
    if (data.other_settings.is_automatic_recursion_enabled) {
        $("#checkbox-automate-recursion").prop("checked", true)
    } else {
        $("#checkbox-automate-recursion").prop("checked", false)
    }

    let intent_processor_options_html = `
        <option value="" selected>Choose One</option>
        <option value="post">Post Processor ${data.other_settings.post_processor_tree_name}</option>
        <option value="pipe">Pipe Processor ${data.other_settings.pipe_processor_tree_name}</option>
        <option value="api">API Tree ${data.other_settings.api_tree_name}</option>
        <option value="data">Data Model</option>
        <option value="api-integration-v2">Automate API Integration - v2 <pre>beta</pre></option>
    `

    if (data.isRoot) {
        intent_processor_options_html += `
        <option value="common-utils">Common Utils File</option>
        <option value="export">Export as JSON</option>
        <option value="log">Logs</option>
        <option value="whatsapp-history">WhatsApp History</option>
        `
    }

    if (data.other_settings.is_package_installer_on) {
        intent_processor_options_html += `<option value="package-manager">Package Installer</option>`
    }
    if (data.other_settings.is_whatsapp_simulator_on) {
        intent_processor_options_html += `<option value="whatsapp-simulator">WhatsApp Simulator</option>`
    }
    if (data.other_settings.is_custom_js_required) {
        intent_processor_options_html += `<option value="chatbot-custom-js">Chatbot JS</option>`
    }
    if (data.other_settings.is_custom_css_required) {
        intent_processor_options_html += `<option value="chatbot-custom-css">Chatbot CSS</option>`
    }
    if (is_new_intent == "False") {
        intent_processor_options_html += `<option value="external-trigger-intent">External Trigger Intent Function</option>`
    }

    $("#select-intent-processor").html(intent_processor_options_html)
    $('#select-intent-processor').select2().on('select2:open', function(e) {
        $('.select2-search__field').attr('placeholder', 'Search Here');
    });

    $("#post_processor_variable").val(data.other_settings.post_processor_variable)

    if (data.other_settings.required_analytics_variable) {
        $("#checkbox-flow-analytics").prop("checked", true)
        $("#flow_analytics_variable").show()
        $("#flow_analytics_variable").val(data.other_settings.flow_analytics_variable)
    } else {
        $("#checkbox-flow-analytics").prop("checked", false)
        $("#flow_analytics_variable").hide()
        $("#flow_analytics_variable").val("")
    }

    $("#category_intent_variable").val("category_name").prop("disabled", true)
    if (data.other_settings.is_category_response_allowed) {
        $("#checkbox-cateogry-intent").prop("checked", true)
        $("#category_intent_variable").show()
    } else {
        $("#checkbox-cateogry-intent").prop("checked", false)
        $("#category_intent_variable").hide()
    }

    // Quick Recommendations
    cancel_bot_recommendation(true, false)
    let quick_recom_html = ""
    for (const intent_pk of data.recommeded_intents_dict_list) {
        $(`#multiple-select-intent-choice-list option[value=${intent_pk}]`).prop("selected", true)
    }
    $("#multiple-select-intent-choice-list").trigger("change")

    $('#multiple-select-intent-choice-list').select2({
        placeholder: 'Search'
    }).on('select2:open', function(e) {
        $('#child-intent-selection .select2-search__field').prop('placeholder', 'Search');
    });

    if (widget_required_data.is_recommendation_menu == "true") {
        $("#checkbox-intent-recommendation-menu").prop("checked", true)
    } else {
        $("#checkbox-intent-recommendation-menu").prop("checked", false)
    }

    // Order of Response
    if (data.is_custom_order_selected) {
        $("#custom-order").prop("checked", true)
    } else {
        $("#default-order").prop("checked", true)
    }
    load_order_of_responses(data, bot_response_data, widget_required_data)

    // Conversion Flow Description
    $("#explanation").val(data.explanation)

    if (data.isRoot) {
        // Advanced NLP
        if (data.enable_intent_level_nlp) {
            $("#advanced_nlp_tab").show()
            $("#easychat_necessary_keywords").text(data.necessary_keywords)
            $("#easychat_restricted_keywords").text(data.restricted_keywords)
            if (data.intent_threshold) {
                $("#easychat-intent-threshold").data("ionRangeSlider").update({from: data.intent_threshold})
            } else {
                $("#easychat-intent-threshold").data("ionRangeSlider").update({from: "1.0"})
            }
        } else {
            $("#advanced_nlp_tab").hide()
        }

        // Campaign Links
        if (data.campaign_link !== "None") {
            $("#campaign_link").show()
            $("#campaign_link_text").text(data.campaign_link)
            $("#campaign_link_new_tab")[0].href = data.campaign_link
            $("#campaign_link_copy").prop("onclick", `copy_text_to_clipboard('${data.campaign_link}')`)
        } else {
            $("#campaign_link").hide()
        }
    }

    // Whatsapp menu format
    $("#whatsapp_menu_data").html("")
    $("#whatsapp_menu_edit_section").removeClass("active")
    $("#whatsapp_menu_edit_section").hide()
    if (!data.is_new_tree) {
        if (Array.isArray(data.whatsapp_menu_section_objs)) {
            let obj = {}
            data.whatsapp_menu_section_objs.map(function(section, idx) {
                obj[idx+1] = section
            })
            data.whatsapp_menu_section_objs = obj
        }
    
        if (data.enable_whatsapp_menu_format && $("#channel-WhatsApp")[0].checked) {
            $("#whatsapp_menu_format_cb").prop("checked", true).trigger("change")
        } else {
            $("#whatsapp_menu_format_cb").prop("checked", false).trigger("change")
        }
    
        $("#optgroup-child-tree").remove()
        $("#optgroup-main-tree").remove()
        add_main_and_child_options(data.unselected_child_trees, data.unselected_main_intents, true)
        enable_or_disable_dropdown_check_boxes()
        $('#easychat_whatsapp_menu_intent_list').multiselect("reload");
        fill_rhs_with_whatsapp_menu_format_data(data.whatsapp_menu_section_objs, true)
        enable_or_disable_add_section_btn()
    }

    // Tab links
    if (data.isRoot) {
        $("#tab_intent_icon").show()
        $("#tab_channels").show()
        $("#tab_campaign_links").show()
    } else {
        $("#tab_intent_icon").hide()
        $("#tab_channels").hide()
        $("#tab_campaign_links").hide()
        $("#advanced_nlp_tab").hide()
    }

    bot_response_preview()
}

function remove_training_questions(e, node_id, sentence) {
    node_intent_data[node_id].training_data = node_intent_data[node_id].training_data.filter(function (elm) {
        return elm !== sentence
    })
    e.currentTarget.parentElement.remove()
}

function build_initial_flow(tree_structure, is_root, parent_node_id, offsetx) {
    let tree_name = tree_structure.tree_name
    let parent
    let data = {
        name: tree_name
    }
    let offsety = window.outerHeight / 8

    let childs = []

    if (is_new_intent === "True") {
        data.name = ""
        let html = `<div class="node-wrapper-div"><span>Click to edit intent</span>` + root_html
        parent = editor.addNode("name", 0, 1, offsetx, offsety, "new-intent-node-identifier-div facebook", data, html);
        node_vertical_position[parent] = offsety
        node_intent_data[parent] = JSON.parse(JSON.stringify(NEW_NODE_DUMMY_DATA))
        node_intent_data[parent].isRoot = true
        $("#node-"+ parent + " a").hide()
        $("#node-"+ parent + " .node-create-child-icon").css("visibility", "hidden")
        return
    }

    if (tree_structure.child_choices_list.length > 0) {
        childs = tree_structure.child_choices_list
    } else {
        childs = Object.keys(tree_structure.subtree)
    }

    if (is_root) {
        offsetx_max = 0
        let html = `<div class="node-wrapper-div"><span>${tree_name}</span>` + root_html
        parent = editor.addNode("name", 0, 1, offsetx, offsety, "facebook", data, html);
        node_vertical_position[parent] = offsety
        node_intent_data[parent] = {lazyLoaded: false, name: tree_name, tree_pk: tree_structure.tree_pk}
    } else {
        $("#save_intent_category").hide()
        $("#save_intent_flow").show()
        offsety = editor.getNodeFromId(parent_node_id).pos_y + 100
        if ($("#node-"+parent_node_id).outerHeight() > 50) {
            offsety += ($("#node-"+parent_node_id).outerHeight() - 50)
        }
        if (childs.length == 0) {
            let sibling = editor.getNodeFromId(parent_node_id).outputs.output_1.connections.at(-1)
            if (sibling) {
                sibling = sibling.node
                offsetx = editor.getNodeFromId(sibling).pos_x + 250
            }
        } else if (offsetx < offsetx_max) {
            offsetx = offsetx_max
        }
        let child = editor.addNode("name", 1, 1, offsetx, offsety, "facebook", data, html.replace("<span></span>", `<span>${tree_name}</span>`));
        node_vertical_position[child] = offsety
        editor.addConnection(parent_node_id, child, "output_1", "input_1")
        node_intent_data[child] = {lazyLoaded: false, name: tree_name, tree_pk: tree_structure.tree_pk}
        parent = child
    }

    if (SELECTED_LANGUAGE != "en") {
        $(`#node-${parent} a`).hide()
        $(`#node-${parent} .node-create-child-icon`).css("visibility", "hidden")
    }

    if (childs.length > 1) {
        offsetx = offsetx - 100
    }

    let counter = 0

    for (const sub_tree_index of childs) {
        counter += 1
        offsetx = build_initial_flow(tree_structure.subtree[sub_tree_index], false, parent, offsetx)
    }

    childs = editor.getNodeFromId(parent).outputs.output_1.connections.map(function(node_data) {
        return node_data.node
    })

    if (counter > 0 && counter == childs.length) {
        offsetx_max = Math.max(offsetx_max, editor.getNodeFromId(childs.at(-1)).pos_x + 350)
        return editor.getNodeFromId(childs.at(-1)).pos_x + 350
    }

    if (childs.length) {
        offsetx_max = Math.max(offsetx_max, editor.getNodeFromId(childs.at(-1)).pos_x + 250)
        return editor.getNodeFromId(childs.at(-1)).pos_x + 250
    }

    offsetx_max = Math.max(offsetx_max, editor.getNodeFromId(parent).pos_x + 250)
    return editor.getNodeFromId(parent).pos_x + 250
    
}

class Deque {
    constructor() {
        this.front = this.back = undefined;
    }
    addFront(value) {
        if (!this.front) this.front = this.back = { value };
        else this.front = this.front.next = { value, prev: this.front };
    }
    removeFront() {
        let value = this.peekFront();
        if (this.front === this.back) this.front = this.back = undefined;
        else (this.front = this.front.prev).next = undefined;
        return value;
    }
    peekFront() { 
        return this.front && this.front.value;
    }
    addBack(value) {
        if (!this.front) this.front = this.back = { value };
        else this.back = this.back.prev = { value, next: this.back };
    }
    removeBack() {
        let value = this.peekBack();
        if (this.front === this.back) this.front = this.back = undefined;
        else (this.back = this.back.next).back = undefined;
        return value;
    }
    peekBack() { 
        return this.back && this.back.value;
    }
}

function update_node_position(id, offsetx) {
    editor.drawflow.drawflow.Home.data[id].pos_x = offsetx;
    document.getElementById("node-"+id).style.left = offsetx + "px";
    editor.updateConnectionNodes("node-"+id);
}

function update_node_vertical_positions(id) {
    let offsety;
    if (id == 1) {
        offsety = window.outerHeight / 8
    } else {
        parent = editor.getNodeFromId(id).inputs.input_1.connections[0].node
        offsety = editor.getNodeFromId(parent).pos_y + 100
        if ($("#node-"+parent).outerHeight() > 50) {
            offsety += ($("#node-"+parent).outerHeight() - 50)
        }
    }
    editor.drawflow.drawflow.Home.data[id].pos_y = offsety;
    document.getElementById("node-"+id).style.top = offsety + "px";
    editor.updateConnectionNodes("node-"+id);

    childs = editor.getNodeFromId(id).outputs.output_1.connections.map(function(node_data) {
        return node_data.node
    })

    for (const child of childs) {
        update_node_vertical_positions(child)
    }
}

function update_flow() {
    node_positions = {}
    left_most_value = Number.MAX_SAFE_INTEGER
    righ_most_value = -Number.MAX_SAFE_INTEGER
    let deque = new Deque()
    let level_order_nodes = [] 

    deque.addBack(1)
    deque.addBack(null)
    let max_number_node = 0
    let number_of_node_in_level = 0
    let max_node = -Number.MAX_SAFE_INTEGER
    let count = 1

    while (deque.peekBack() || deque.peekFront()) {
        let elm = deque.removeFront()
        level_order_nodes.push(elm)

        if (elm) {
            let childs = editor.getNodeFromId(elm).outputs.output_1.connections.map(function(node_data) {
                return node_data.node
            })

            childs.reverse().forEach(function(child) {
                deque.addBack(child)
            })
        } else {
            max_node = Math.max(max_node, count)
            deque.addBack(null)
        }
    }

    level_order_nodes.reverse()
    let section = 5;

    for (const node of level_order_nodes) {
        if (node) {
            section += 1
        } else {
            break
        }   
    }

    let left_most_position = window.outerWidth / section
    let new_level = true
    let offsetx = left_most_position;
    for (const node of level_order_nodes) {
        if (node) {
            let childs = editor.getNodeFromId(node).outputs.output_1.connections.map(function(node_data) {
                return node_positions[node_data.node]
            })
            let old_offset = offsetx

            if (childs.length == 1) {
                offsetx = childs[0]
            } else if (childs.length == 0) {
                if (new_level) {
                    offsetx = left_most_position
                }
            } else {
                let offset_avg = (childs[0] + childs.at(-1)) / 2
                offsetx = offset_avg
            }

            if (new_level) {
                left_most_position = offsetx - 250
                new_level = false
            } else {
                if (old_offset > offsetx) {
                    offsetx = old_offset
                    right_shift_tree(node, offsetx)
                }
            }

            node_positions[node] = offsetx
            update_node_position(node, offsetx)
            if (offsetx > righ_most_value) {
                righ_most_value = offsetx
            }
            if (offsetx < left_most_value) {
                left_most_value = offsetx
            }
            number_of_node_in_level += 1
            offsetx += 250
        } else {
            max_number_node = Math.max(max_number_node,number_of_node_in_level)
            number_of_node_in_level = 0
            new_level = true
        }
    }

    let span = righ_most_value - left_most_value
    let factor = window.outerWidth/1.2 * 0.1 * 2

    let zoom_level = Math.ceil((span - window.outerWidth/1.2)/factor) * 0.1
    zoom_level = zoom_level ? zoom_level : 0.5
    zoom_level = zoom_level == 1 ? zoom_level - 0.5 : zoom_level
    let right_extra_offset = 0
    if (max_node < 5) {
        right_extra_offset = -200
    }

    let translatex = 0
    if (max_number_node > 5) {
        translatex = window.outerWidth/1.5 - (righ_most_value + left_most_value + 192)/2
    }
    else {
        translatex = window.outerWidth/1.8 - (righ_most_value + left_most_value + 192)/2 + right_extra_offset
    }
    if (span > window.outerWidth/1.2) {
        editor.zoom = 1.0
        if (zoom_level > 0.5) {
            zoom_level = 0.5
        }
        editor.zoom_value = zoom_level
        editor.zoom_out()
        editor.zoom_value = 0.1
        if (zoom_level < editor.zoom_min) {
            editor.zoom_min = 0.2
        }
    } else {
        editor.zoom = 1.1
        editor.zoom_out()
    }

    $(".drawflow").css("transform", `translate(${translatex}px, 0px) scale(${editor.zoom})`)

    return node_positions

}

function right_shift_tree(id, offsetx) {
    let childs = editor.getNodeFromId(id).outputs.output_1.connections.map(function(node_data) {
        return {node: node_data.node, pos: node_positions[node_data.node]}
    })

    let offset_avg = childs.reduce(function(a, b) {
        return {pos: a.pos + b.pos}
    }).pos / childs.length

    let difference = (offsetx - offset_avg) / childs.length

    for (const child of childs) {
        let id = child.node
        let offsetx = editor.getNodeFromId(id).pos_x + difference
        update_node_position(id, offsetx)
    }
}

function find_right_sibling(id, parent) {
    let siblings = editor.getNodeFromId(parent).outputs.output_1.connections.map(function(node_data) {
        return node_data.node
    })
    let previous_node = null
    let current_node = null
    for (const sibling of siblings) {
        previous_node = current_node
        current_node = sibling
        if (previous_node == id) break
    }

    return current_node

}

function add_more_variation(bot_pk, intent_name, page_no) {
    // let selected_bot_pk = $("#multiple-select-bot-choice-pk-list").val()
    // let intent_name = $("#intent_name").val()
    let json_string = JSON.stringify({
        intent_name: intent_name,
        bot_id: bot_pk,
        page_no: page_no
    });
    document.getElementById("show-more-variations").innerHTML = "Showing..."
    setTimeout(function () {
        json_string = EncryptVariable(json_string);
        $.ajax({
            url: '/chat/get-variations/',
            type: "POST",
            data: {
                json_string: json_string
            },
            dataType: "json",
            async: false,
            success: function (response) {
                response = custom_decrypt(response)
                response = JSON.parse(response);
                $("#suggest-variations-btn span")[0].innerHTML = 'Suggest Variations<sup><b> BETA</b></sup>'
                if (response['status'] == 200) {
                    variations = response["variation_list"]
                    more_var = response["more_var"]
                    document.getElementById("show-more-variations").innerHTML = "Show More"
                    $("#show-more-variations").hide()
                    if (more_var) {
                        temp_string = "add_more_variation('" + bot_pk + "','" + intent_name + "'," + (page_no + 1) + ")"
                        document.getElementById("show-more-variations").setAttribute("onclick", temp_string)
                        $("#show-more-variations").show()
                    }
                    let stripped_data = node_intent_data[selected_node].training_data.map(function(train) {
                        return train.trim()
                    })
                    variations = variations.reduce((result, sentence)=>{
                        if ( !stripped_data.includes(sentence)) {
                            result.push(sentence)
                        }
                        return result
                    }, [])
                    if (variations.length > 0) {
                        fill_training_data_rhs(variations, false);
                        M.toast({
                            'html': "Variations added successfully!",
                            'displayLength': 3000
                        }, 2000);
                    } else {
                        M.toast({
                            'html': "No Variations generated!",
                            'displayLength': 3000
                        }, 2000);
                    }
                } else {
                    document.getElementById("show-more-variations").innerHTML = "Show More"
                    M.toast({
                        'html': "Error while generating Variations!",
                        'displayLength': 3000
                    }, 2000);
                }
            }
        });
    }, 1000)
};

function render_uploaded_image() {
    let input_upload_image = ($("#imgupload"))[0].files[0]
    $("#imgupload").val("")

    if (input_upload_image == null || input_upload_image == undefined) {
        $("#image_upload_failed span").text("Please choose a file.")
        $("#image_upload_failed").show()
        setTimeout(function() {
            $("#image_upload_failed").hide()
        }, 3000)
        return;
    }
    if (input_upload_image.name.toLowerCase().match(/\.(jpeg|jpg|gif|png)$/) == null) {
        $("#image_upload_failed span").text("File format is not supported.")
        $("#image_upload_failed").show()
        setTimeout(function() {
            $("#image_upload_failed").hide()
        }, 3000)
        return false;
    }

    if (input_upload_image.size > upload_file_limit_size) {
        $("#image_upload_failed span").text("Size limit exceed(should be less than 5 MB).")
        $("#image_upload_failed").show()
        setTimeout(function() {
            $("#image_upload_failed").hide()
        }, 3000)
        return;
    }

    if (check_malicious_file(input_upload_image.name) == true) {
        return false;
    }

    let reader = new FileReader();
    reader.readAsDataURL(input_upload_image);
    reader.onload = function () {

        base64_str = reader.result.split(",")[1];

        uploaded_file = [];
        uploaded_file.push({
            "filename": input_upload_image.name,
            "base64_file": base64_str,
        });

        upload_intent_image(uploaded_file);
    };

    reader.onerror = function (error) {
        console.log('Error: ', error);
    };
}

async function upload_intent_image(uploaded_file) {
    let response = await upload_image(uploaded_file);

    if (response && response.status == 200) {
        src = window.location.origin + response["src"]
        add_images_response_rhs([src], true);
        node_intent_data[selected_node].intent_response.image_list.push(src)
        
    }
    $("#image_upload_successfull").show()
    $("#image_upload_failed").hide()
    setTimeout(function() {
        $("#image_upload_successfull").hide()
    }, 2000)
}

function delete_uploaded_image(event) {
    event.currentTarget.parentElement.parentElement.remove()
    node_intent_data[selected_node].intent_response.image_list = node_intent_data[selected_node].intent_response.image_list.filter(function(image) {
        return image !== $(event.currentTarget).prev().attr("original_src")
    })

    setTimeout(function() {
        initialize_carousel("#only_image_carousel")
    }, 100)

    if ($("#only_image_carousel .carousel-item").length <= 1) {
        $("#add_response_video").addClass("disable-video-recoder-save-value")
    }
}

function load_order_of_responses(intent_data, bot_response_data, widget_required_data, manual_check=false) {
    let response_pk = intent_data['answer_pk']
    let new_order_response = []

    sentence_list = bot_response_data["response_list"]
    image_list = bot_response_data["image_list"]
    video_list = bot_response_data["video_list"]
    card_list = Object.values(bot_response_data["card_list"]).filter(function(card) {
        return card && Object.keys(card).length > 0
    })
    table_list_of_list =  bot_response_data["table_list_of_list"]

    let order_div = document.getElementById('easychat_order_of_responses');
    let response_item;
    let drag_img;
    let order_of_response = intent_data.order_of_response
    let default_order_of_response = intent_data.default_order_of_response

    let is_custom_order_selected = document.getElementById('custom-order').checked;
    if (order_of_response.length == 0 || !is_custom_order_selected) {
        order_of_response = default_order_of_response

        if (order_of_response.length == 0) {
            order_of_response = ['text', 'image', 'table', 'video', 'link_cards', 'intent_level_feedback', 'quick_recommendations', 'drop_down', 'date_picker', 'checkbox', 'radio_button', 'range_slider', 'form', 'time_picker', 'calendar_picker', 'file_attach', 'video_record', 'phone_number'];
        }
    }
    if (manual_check) {
        for (const resp of default_order_of_response) {
            if (!order_of_response.includes(resp)) {
                order_of_response.push(resp)
            }
        }
    }

    order_div.innerHTML = '';

    for (element of order_of_response) {
        drag_img = `<span class="easychat-drag-response">${capitalize_words(element)}</span>
        <svg width="25" height="24" viewBox="0 0 25 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M15.5824 17C16.4108 17 17.0824 17.6716 17.0824 18.5C17.0824 19.3284 16.4108 20 15.5824 20C14.7539 20 14.0824 19.3284 14.0824 18.5C14.0824 17.6716 14.7539 17 15.5824 17ZM8.58237 17C9.41079 17 10.0824 17.6716 10.0824 18.5C10.0824 19.3284 9.41079 20 8.58237 20C7.75394 20 7.08237 19.3284 7.08237 18.5C7.08237 17.6716 7.75394 17 8.58237 17ZM15.5824 10C16.4108 10 17.0824 10.6716 17.0824 11.5C17.0824 12.3284 16.4108 13 15.5824 13C14.7539 13 14.0824 12.3284 14.0824 11.5C14.0824 10.6716 14.7539 10 15.5824 10ZM8.58237 10C9.41079 10 10.0824 10.6716 10.0824 11.5C10.0824 12.3284 9.41079 13 8.58237 13C7.75394 13 7.08237 12.3284 7.08237 11.5C7.08237 10.6716 7.75394 10 8.58237 10ZM15.5824 3C16.4108 3 17.0824 3.67157 17.0824 4.5C17.0824 5.32843 16.4108 6 15.5824 6C14.7539 6 14.0824 5.32843 14.0824 4.5C14.0824 3.67157 14.7539 3 15.5824 3ZM8.58237 3C9.41079 3 10.0824 3.67157 10.0824 4.5C10.0824 5.32843 9.41079 6 8.58237 6C7.75394 6 7.08237 5.32843 7.08237 4.5C7.08237 3.67157 7.75394 3 8.58237 3Z" fill="#212121"></path>
        </svg>
        `;
        response_item = '<div class="easychat-intent-response-item" value="' + element + '" item-name="' + element + '">' + drag_img + '</div>';

        if (element == "image" && image_list.length == 0) {
            response_item = ''
        } else if (element == "link_cards" && card_list.length == 0) {
            response_item = ''
        } else if (element == "table") {
            try {
                if (table_res == "") {
                    if (table_list_of_list)
                        table_matrix = table_list_of_list;
                    else
                        table_matrix = '{"items": ""}';
                    table_matrix = JSON.parse(table_matrix)["items"];
                    table_res = table_matrix
                }
            } catch (err) {
                table_res = null
            }
            if (table_res == undefined || table_res == null || table_res == '') {
                response_item = ''
            }
        } else if (element == "video" && video_list.length == 0) {
            response_item = ''
        } else if (element == "quick_recommendations") {
            let recommended_intent_list = document.getElementById('multiple-select-intent-choice-list').value;
            if (recommended_intent_list.length == 0) {
                response_item = ''
            }
        } else if (element == "checkbox") {
            let is_check_box_allowed = widget_required_data.is_check_box
            if (is_check_box_allowed !== 'true') {
                response_item = ''
            }
        } else if (element == "radio_button") {
            let is_radio_button_allowed = widget_required_data.is_radio_button
            radio_choices_list = []
            if (is_radio_button_allowed !== "true") {
                response_item = ''
            }
        } else if (element == "drop_down") {
            let is_drop_down_allowed = widget_required_data.is_drop_down
            if (is_drop_down_allowed !== "true") {
                response_item = ''
            }
        } else if (element == "video_record") {
            let is_video_recorder_allowed = widget_required_data.is_video_recorder_allowed;
            if (is_video_recorder_allowed !== "true") {
                response_item = ''
            }
        } else if (element == "date_picker") {
            response_item = ''
        } else if (element == "time_picker") {
            response_item = ''
        } else if (element == "range_slider") {
            let is_range_slider_required = widget_required_data.is_range_slider;
            if (is_range_slider_required !== "true") {
                response_item = ''
            }
        } else if (element == "form") {
            let is_create_form = widget_required_data.is_create_form_allowed
            if (is_create_form !== "true") {
                response_item = '';
            }
        } else if (element == "file_attach") {
            let is_attachment_required = widget_required_data.is_attachment_required;
            if (is_attachment_required !== "true") {
                response_item = ''
            }
        } else if (element == "calendar_picker") {
            let is_calender_picker_allowed = widget_required_data.is_calender;
            if (is_calender_picker_allowed !== "true") {
                response_item = ''
            }
        } else if (element == "phone_number") {
            let is_phone_widget_enabled = widget_required_data.is_phone_widget_enabled;
            if (is_phone_widget_enabled !== "true") {
                response_item = ''
            }
        } else if (element == "intent_level_feedback") {
            let is_intent_level_feedback_required = intent_data.is_feedback_required && intent_data.is_bot_feedback_required;
            if (!is_intent_level_feedback_required) {
                response_item = ''
            }
        }

        if (response_item != '') {
            $(order_div).append(response_item);
            new_order_response.push(element)
        }
    }
    node_intent_data[selected_node].order_of_response = new_order_response
    let elem = document.getElementById('easychat_order_of_responses');
    if (is_custom_order_selected) {
        elem.classList.remove('response-order-disabled');

        $('#easychat_order_of_responses').sortable({
            containment: "parent",
            update: function() {
                node_intent_data[selected_node].order_of_response = $("#easychat_order_of_responses").sortable("toArray", {attribute: "value"})
            }
        });
    } else {
        elem.classList.add('response-order-disabled');
    }
}

function trigger_card_file_upload(e) {
    $(e.currentTarget).prev().trigger('click')
}

function handle_card_link_change(e, card_id) {
    let input_upload_image = e.currentTarget.files[0]
    e.currentTarget.value = ""

    if (input_upload_image == null || input_upload_image == undefined) {
        M.toast({
            "html": "Please choose a file."
        }, 2000);
        return;
    }
    if (input_upload_image.name.toLowerCase().match(/\.(pdf)$/) == null) {
        M.toast({
            "html": "File format is not supported"
        }, 2000);
        return false;
    }

    if (input_upload_image.size > upload_file_limit_size) {
        M.toast({
            "html": "Size limit exceed(should be less than 5 MB)."
        }, 2000);
        return;
    }

    if (check_malicious_file(input_upload_image.name) == true) {
        return false;
    }

    let reader = new FileReader();
    reader.readAsDataURL(input_upload_image);
    reader.onload = function () {

        base64_str = reader.result.split(",")[1];

        uploaded_file = [];
        uploaded_file.push({
            "filename": input_upload_image.name,
            "base64_file": base64_str,
        });

        upload_card_link(uploaded_file, card_id);
    };

    reader.onerror = function (error) {
        console.log('Error: ', error);
    };
}

function upload_file_card_new(uploaded_file) {
    return new Promise(function (resolve, reject) {
        let csrf_token = $('input[name="csrfmiddlewaretoken"]').val();
        let json_string = JSON.stringify(uploaded_file)
        json_string = EncryptVariable(json_string)

        encrypted_data = {
            "Request": json_string
        }

        let params = JSON.stringify(encrypted_data);

        $.ajax({
            url: "/chat/upload-file-card/",
            type: "POST",
            contentType: "application/json",
            headers: {
                'X-CSRFToken': csrf_token
            },
            data: params,
            processData: false,
            success: function (response) {
                response = custom_decrypt(response)
                response = JSON.parse(response);
                if (response.status == 200) {
                    resolve(response);
                } else if (response.status == 300) {
                    M.toast({
                        "html": "File format is Invalid"
                    }, 2000)
                } else {
                    M.toast({
                        "html": "Unable to upload your file. Please try again later."
                    }, 2000)
                }
            },
            error: function (xhr, textstatus, errorthrown) {
                console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
            }
        });
    })
}

async function upload_card_link(uploaded_file, card_id) {
    let response = await upload_file_card_new(uploaded_file);

    if (response && response.status == 200) {
        src = window.location.origin + response["src"]
        document.getElementById(`card_link_${card_id}`).value = src;
        node_intent_data[selected_node].intent_response.card_list[card_id].link = src
    }
}

function handle_card_image_change(e, card_id) {
    let input_upload_image = e.currentTarget.files[0]
    e.currentTarget.value = ""

    if (input_upload_image == null || input_upload_image == undefined) {
        M.toast({
            "html": "Please choose a file."
        }, 2000);
        return;
    }
    if (input_upload_image.name.toLowerCase().match(/\.(jpeg|jpg|gif|png)$/) == null) {
        M.toast({
            "html": "File format is not supported"
        }, 2000);
        return false;
    }

    if (input_upload_image.size > upload_file_limit_size) {
        M.toast({
            "html": "Size limit exceed(should be less than 5 MB)."
        }, 2000);
        return;
    }

    if (check_malicious_file(input_upload_image.name) == true) {
        return false;
    }

    let reader = new FileReader();
    reader.readAsDataURL(input_upload_image);
    reader.onload = function () {

        base64_str = reader.result.split(",")[1];

        uploaded_file = [];
        uploaded_file.push({
            "filename": input_upload_image.name,
            "base64_file": base64_str,
        });

        upload_card_image(uploaded_file, card_id);
    };

    reader.onerror = function (error) {
        console.log('Error: ', error);
    };
}

function delete_card_image(e, card_id) {
    $(`#card_image_result_div_${card_id}`).remove()
    $(`#card_image_upload_div_${card_id}`).show()
    delete node_intent_data[selected_node].intent_response.card_list[card_id].img_url
}   

async function upload_card_image(uploaded_file, card_id, upload=true) {
    let response = {};

    if (upload) {
        response = await upload_image(uploaded_file);
    } else {
        response.status = 200
        response.src = uploaded_file
    }

    if (response && response.status == 200) {
        if (upload) {
            src = window.location.origin + response["src"]
        } else {
            src = response["src"]
        }
        node_intent_data[selected_node].intent_response.card_list[card_id].img_url = src
        $(`#card_image_upload_div_${card_id}`).hide()
        $(`#card_image_upload_div_${card_id}`).after(`
        <div class="intent-upload-image-wrapper-div" id="card_image_result_div_${card_id}">
            <div class="intent-file-uploaded-div">
                <div class="uploaded-img-div">
                    <img src="${src}" alt="picture">
                    <div class="uploaded-img-delete" onclick="delete_card_image(event, ${card_id})">
                        <span>
                            <svg width="25" height="25" viewBox="0 0 25 25" fill="none"
                                xmlns="http://www.w3.org/2000/svg">
                                <path fill-rule="evenodd" clip-rule="evenodd"
                                    d="M8.74675 5.40137L9.02452 4.15137C9.17267 3.81803 9.64674 3.15137 10.3579 3.15137H14.8023C15.0986 3.15137 15.7801 3.35137 16.1356 4.15137L16.4134 5.40137H20.5801C20.9943 5.40137 21.3301 5.73715 21.3301 6.15137C21.3301 6.56558 20.9943 6.90137 20.5801 6.90137H4.58008C4.16586 6.90137 3.83008 6.56558 3.83008 6.15137C3.83008 5.73715 4.16586 5.40137 4.58008 5.40137H8.74675ZM7.08008 19.2314L5.58008 8.15137H19.5801L18.0801 19.2314C18.0801 20.7674 17.0801 21.1514 16.5801 21.1514H9.08008C7.88008 21.1514 7.24674 19.8714 7.08008 19.2314Z"
                                    fill="#FF281A" />
                            </svg>
                        </span>
                    </div>
                </div>
            </div>
            <span class="or-span">or</span>
            <div class="edit-intent-input-div">
                <input type="text" class="form-control input" onchange="handle_general_input_change(event, 'card_image', ${card_id})" value="${src}" id="" placeholder="Link Image">
            </div>
        </div>
        `)
    }
}

function handle_general_input_change(e, event_type, id) {
    if (event_type === "card_title") {
        if (e.currentTarget.value.length > 20) {
            $(`a[href='#added_card_${id}'] span`).html(e.currentTarget.value.substring(0, 20) + "...")
        } else {
            $(`a[href='#added_card_${id}'] span`).html(e.currentTarget.value)
        }
        node_intent_data[selected_node].intent_response.card_list[id].title = e.currentTarget.value 
    } else if (event_type === "node_name") {
        node_intent_data[selected_node].name = e.currentTarget.value
    } else if (event_type === "card_content") {
        node_intent_data[selected_node].intent_response.card_list[id].content = e.currentTarget.value 
    } else if (event_type === "card_link") {
        node_intent_data[selected_node].intent_response.card_list[id].link = e.currentTarget.value 
    } else if (event_type === "card_image") {
        if ($(`#card_image_result_div_${id}`)) {
            delete_card_image({}, id)
        }
        upload_card_image(e.currentTarget.value, id, false);
    } else if (event_type === "widget_datepicker") {
        if (!e.currentTarget.checked) {
            node_intent_data[selected_node].intent_response.modes.is_single_datepicker = "false"
            node_intent_data[selected_node].intent_response.modes.is_multi_datepicker = "false"
        }
    } else if (event_type === "widget_singledate") {
        node_intent_data[selected_node].intent_response.modes.is_single_datepicker = "true"
        node_intent_data[selected_node].intent_response.modes.is_multi_datepicker = "false"
    } else if (event_type === "widget_customdate") {
        node_intent_data[selected_node].intent_response.modes.is_single_datepicker = "false"
        node_intent_data[selected_node].intent_response.modes.is_multi_datepicker = "true"
    } else if (event_type === "widget_timepicker") {
        if (!e.currentTarget.checked) {
            node_intent_data[selected_node].intent_response.modes.is_single_timepicker = "false"
            node_intent_data[selected_node].intent_response.modes.is_multi_timepicker = "false"
        }
    } else if (event_type === "widget_singletime") {
        node_intent_data[selected_node].intent_response.modes.is_single_timepicker = "true"
        node_intent_data[selected_node].intent_response.modes.is_multi_timepicker = "false"
    } else if (event_type === "widget_customtime") {
        node_intent_data[selected_node].intent_response.modes.is_single_timepicker = "false"
        node_intent_data[selected_node].intent_response.modes.is_multi_timepicker = "true"
    } else if (event_type === "widget_video") {
        if (e.currentTarget.checked) {
            node_intent_data[selected_node].intent_response.modes.is_video_recorder_allowed = 'true'
        } else {
            node_intent_data[selected_node].intent_response.modes.is_video_recorder_allowed = "false"
        }
    } else if (event_type === "widget_save_video") {
        if (e.currentTarget.checked) {
            node_intent_data[selected_node].intent_response.modes.is_save_video_attachment = "true"
        } else {
            node_intent_data[selected_node].intent_response.modes.is_save_video_attachment = "false"
        }
    } else if (event_type === "widget_single_range") {
        node_intent_data[selected_node].intent_response.modes_param.range_slider_list[0].range_type = "single-range-slider"
    } else if (event_type === "widget_multi_range") {
        node_intent_data[selected_node].intent_response.modes_param.range_slider_list[0].range_type = "multi-range-slider"
    } else if (event_type === "widget_min_range") {
        node_intent_data[selected_node].intent_response.modes_param.range_slider_list[0].min = e.currentTarget.value
    } else if (event_type === "widget_max_range") {
        node_intent_data[selected_node].intent_response.modes_param.range_slider_list[0].max = e.currentTarget.value
    } else if (event_type === "widget_file_attatch") {
        if (e.currentTarget.checked) {
            node_intent_data[selected_node].intent_response.modes.is_attachment_required = "true"
        } else {
            node_intent_data[selected_node].intent_response.modes.is_attachment_required = "false"
        }
    } else if (event_type === "widget_file_type") {
        node_intent_data[selected_node].intent_response.modes_param.choosen_file_type = e.currentTarget.value
    } else if (event_type === "widget_save_attachment") {
        if (e.currentTarget.checked) {
            node_intent_data[selected_node].intent_response.modes.is_save_attachment_required = "true"
        } else {
            node_intent_data[selected_node].intent_response.modes.is_save_attachment_required = "false"
        }
    } else if (event_type === "widget_country_code") {
        if (e.currentTarget.checked) {
            node_intent_data[selected_node].intent_response.modes.is_phone_widget_enabled = "true"
        } else {
            node_intent_data[selected_node].intent_response.modes.is_phone_widget_enabled = "false"
        }
    } else if (event_type === "widget_form_name") {
        node_intent_data[selected_node].intent_response.modes_param.form_name = e.currentTarget.value
    } else if (event_type === "quick_recom_list") {
        node_intent_data[selected_node].recommeded_intents_dict_list = $("#multiple-select-intent-choice-list").val()
    } else if (event_type === "quick_recom_menu") {
        if (e.currentTarget.checked) {
            node_intent_data[selected_node].intent_response.modes.is_recommendation_menu = "true"
        } else {
            node_intent_data[selected_node].intent_response.modes.is_recommendation_menu = "false"
        }
    } else if (event_type === "explanation") {
        node_intent_data[selected_node].explanation = e.currentTarget.value
    } else if (event_type === "nlp_necessary") {
        node_intent_data[selected_node].necessary_keywords = e.currentTarget.value
    } else if (event_type === "nlp_restricted") {
        node_intent_data[selected_node].restricted_keywords = e.currentTarget.value
    } else if (event_type === "nlp_thresold") {
        node_intent_data[selected_node].intent_threshold = $("#easychat-intent-threshold").val()
    } else if (event_type === "other_faq_intent") {
        if (e.currentTarget.checked) {
            node_intent_data[selected_node].other_settings.is_faq_intent = true
        } else {
            node_intent_data[selected_node].other_settings.is_faq_intent = false
        }
    } else if (event_type === "other_intent_suggestion") {
        if (e.currentTarget.checked) {
            node_intent_data[selected_node].other_settings.is_part_of_suggestion_list = true
        } else {
            node_intent_data[selected_node].other_settings.is_part_of_suggestion_list = false
        }
    } else if (event_type === "other_auth") {
        if (e.currentTarget.checked) {
            node_intent_data[selected_node].other_settings.is_authentication_required = true
            $(".div-select-user-authentication-dropdown").show()
        } else {
            node_intent_data[selected_node].other_settings.is_authentication_required = false
            $(".div-select-user-authentication-dropdown").hide()
        }
    } else if (event_type === "other_intent_small_talk") {
        if (e.currentTarget.checked) {
            node_intent_data[selected_node].other_settings.is_small_talk = true
            $("#checkbox-intent-part-of-suggestionList").prop("disabled", true)
            $("#checkbox-intent-feedback").prop("disabled", true)
        } else {
            $("#checkbox-intent-feedback").prop("disabled", false)
            $("#checkbox-intent-part-of-suggestionList").prop("disabled", false)
            node_intent_data[selected_node].other_settings.is_small_talk = false
        }
    } else if (event_type === "other_validator") {
        node_intent_data[selected_node].other_settings.selected_validator_obj.processor__pk = e.currentTarget.value
    } else if (event_type === "other_feedback") {
        if (e.currentTarget.checked) {
            node_intent_data[selected_node].other_settings.is_feedback_required = true
        } else {
            node_intent_data[selected_node].other_settings.is_feedback_required = false
        }
    } else if (event_type === "other_auth") {
        node_intent_data[selected_node].other_settings.selected_user_authentication.pk = e.currentTarget.value
    } else if (event_type === "other_child_visible") {
        if (e.currentTarget.checked) {
            node_intent_data[selected_node].other_settings.is_child_tree_visible = true
        } else {
            node_intent_data[selected_node].other_settings.is_child_tree_visible = false
        }
    } else if (event_type === "other_go_back") {
        if (e.currentTarget.checked) {
            node_intent_data[selected_node].other_settings.is_go_back_enabled = true
        } else {
            node_intent_data[selected_node].other_settings.is_go_back_enabled = false
        }
    } else if (event_type === "other_child_order") {
        node_intent_data[selected_node].other_settings.choices_order_changed = true
        node_intent_data[selected_node].other_settings.child_choices_list = $(e.currentTarget).val()
    } else if (event_type === "other_final_child") {
        if (e.currentTarget.checked) {
            node_intent_data[selected_node].other_settings.is_last_tree = true
        } else {
            node_intent_data[selected_node].other_settings.is_last_tree = false
        }
    } else if (event_type === "other_disposition") {
        node_intent_data[selected_node].other_settings.disposition_code = e.currentTarget.value
    } else if (event_type === "other_exit_tree") {
        if (e.currentTarget.checked) {
            node_intent_data[selected_node].other_settings.is_exit_tree = true
        } else {
            node_intent_data[selected_node].other_settings.is_exit_tree = false
        }
    } else if (event_type === "other_transfer_tree") {
        if (e.currentTarget.checked) {
            node_intent_data[selected_node].other_settings.is_transfer_tree = true
        } else {
            node_intent_data[selected_node].other_settings.is_transfer_tree = false
        }
    } else if (event_type === "other_allow_barge") {
        if (e.currentTarget.checked) {
            node_intent_data[selected_node].other_settings.allow_barge = true
        } else {
            node_intent_data[selected_node].other_settings.allow_barge = false
        }
    } else if (event_type === "is_item_purchased") {
        if (e.currentTarget.checked) {
            node_intent_data[selected_node].other_settings.is_item_purchased = true
        } else {
            node_intent_data[selected_node].other_settings.is_item_purchased = false
        }
    } else if (event_type === "other_whatsapp_header") {
        node_intent_data[selected_node].other_settings.whatsapp_list_message_header = e.currentTarget.value
    } else if (event_type === "other_catalogue") {
        if (e.currentTarget.checked) {
            node_intent_data[selected_node].intent_response.modes.is_catalogue_added = "true"
            $(".enable-add-catalogue").show();
        } else {
            node_intent_data[selected_node].intent_response.modes.is_catalogue_added = "false"
            $('.enable-add-catalogue').hide();
        }
    } else if (event_type === "advance_recursion") {
        if (e.currentTarget.checked) {
            node_intent_data[selected_node].other_settings.is_automatic_recursion_enabled = true
        } else {
            node_intent_data[selected_node].other_settings.is_automatic_recursion_enabled = false
        }
    } else if (event_type === "advance_processor_variable") {
        node_intent_data[selected_node].other_settings.post_processor_variable = e.currentTarget.value
    } else if (event_type === "advance_flow_analytics") {
        if (e.currentTarget.checked) {
            node_intent_data[selected_node].other_settings.required_analytics_variable = true
        } else {
            $("#flow_analytics_variable").val("")
            node_intent_data[selected_node].other_settings.flow_analytics_variable = ""
            node_intent_data[selected_node].other_settings.required_analytics_variable = false
        }
    } else if (event_type === "advance_flow_variable") {
        node_intent_data[selected_node].other_settings.flow_analytics_variable = e.currentTarget.value
    } else if (event_type === "advance_category_response") {
        if (e.currentTarget.checked) {
            node_intent_data[selected_node].other_settings.is_category_response_allowed = true
        } else {
            node_intent_data[selected_node].other_settings.is_category_response_allowed = false
        }
    } else if (event_type === "other_confirm_reset") {
        if (e.currentTarget.checked) {
            node_intent_data[selected_node].other_settings.is_confirmation_and_reset_enabled = true
        } else {
            node_intent_data[selected_node].other_settings.is_confirmation_and_reset_enabled = false
        }
    } else if (event_type === "tree_whatsapp_short") {
        node_intent_data[selected_node].whatsapp_short_name = e.currentTarget.value
    } else if (event_type === "tree_whatsapp_description") {
        node_intent_data[selected_node].whatsapp_description = e.currentTarget.value
    } else if (event_type === "tree_short_name") {
        node_intent_data[selected_node].short_name_value = e.currentTarget.value
    }
}

function check_table_filled() {
    rows = 0;
    columns = 0;
    if (document.getElementById('number-of-rows-table').value != "") {
        rows = document.getElementById('number-of-rows-table').value
    }
    if (document.getElementById('number-of-columns-table').value != "") {
        columns = document.getElementById('number-of-columns-table').value
    }
    table_input_list_of_list = []
    for (i = 0; i < rows; i++) {
        row_list = []
        for (j = 0; j < columns; j++) {
            cell_value = document.getElementById('cell-id-' + i.toString() + j.toString()).innerHTML;
            if (cell_value != "") {
                if (un_entity(cell_value).trim() == "<br>" || un_entity(cell_value).trim() == "")
                    return false
                else
                    row_list.push(un_entity(cell_value));
            } else {
                return false
            };

        };
        table_input_list_of_list.push(row_list)
    };
    return table_input_list_of_list
};

function save_training_intent_and_bot_response() {
    intent_pk = null

    if (window.location.href.indexOf("intent_pk=") != -1) {

        let url_parameters = get_url_vars();
        intent_pk = url_parameters["intent_pk"];
    }

    intent_name = node_intent_data[selected_node].name.trim();

    if (intent_name == "") {
        M.toast({
            "html": "Intent name cannot be empty."
        }, 2000);
        return;
    }

    const category_obj_pk = $("#select-intent-category").val()

    // To check only emoji is present or not 
    let emoji_regex = /^(?:[\u2700-\u27bf]|(?:\ud83c[\udde6-\uddff]){2}|[\ud800-\udbff][\udc00-\udfff]|[\u0023-\u0039]\ufe0f?\u20e3|\u3299|\u3297|\u303d|\u3030|\u24c2|\ud83c[\udd70-\udd71]|\ud83c[\udd7e-\udd7f]|\ud83c\udd8e|\ud83c[\udd91-\udd9a]|\ud83c[\udde6-\uddff]|[\ud83c[\ude01-\ude02]|\ud83c\ude1a|\ud83c\ude2f|[\ud83c[\ude32-\ude3a]|[\ud83c[\ude50-\ude51]|\u203c|\u2049|[\u25aa-\u25ab]|\u25b6|\u25c0|[\u25fb-\u25fe]|\u00a9|\u00ae|\u2122|\u2139|\ud83c\udc04|[\u2600-\u26FF]|\u2b05|\u2b06|\u2b07|\u2b1b|\u2b1c|\u2b50|\u2b55|\u231a|\u231b|\u2328|\u23cf|[\u23e9-\u23f3]|[\u23f8-\u23fa]|\ud83c\udccf|\u2934|\u2935|[\u2190-\u21ff])+$/;
    raw_intent = intent_name.split(" ").join("")
    const emoji_test_reg = emoji_regex.test(raw_intent);

    if (emoji_test_reg) {
        M.toast({
            "html": "Intent name cannot have only Emoji."
        }, 2000);
        return;
    }

    multilingual_intent_elm = document.getElementById("multilingual_intent_name")
    multilingual_intent_name = ""
    if (multilingual_intent_elm != null && multilingual_intent_elm != undefined) {
        multilingual_intent_name = multilingual_intent_elm.value
    }
    selected_bot_pk_list = [BOT_ID];

    if (selected_bot_pk_list.length == 0) {
        M.toast({
            "html": "Select atleast one bot in which intent will be supported"
        }, 2000);
        return;
    }

    training_data_list = node_intent_data[selected_node].training_data

    if (SELECTED_LANGUAGE === "en") {
        if (training_data_list.length == 0) {
            M.toast({
                "html": "At least one training sentence is required."
            }, 2000);
            return;
        }
    }

    let response_present = ['text'];

    intent_bot_response_text_text = $("#intent_bot_response_text_text").trumbowyg('html');
    intent_bot_response_text_speech = $("#intent_bot_response_text_speech").trumbowyg('html');
    intent_bot_response_reprompt = $("#intent_bot_response_reprompt").trumbowyg('html');
    intent_bot_response_ssml = $("#intent_bot_response_ssml").val();

    intent_bot_response_text_text = intent_bot_response_text_text.replace(new RegExp('\r?<br />', 'g'), '<br>');

    if (validate_ck_editor_response(intent_bot_response_text_text) != "" && validate_ck_editor_response(intent_bot_response_text_speech) == "") {
        intent_bot_response_text_speech = intent_bot_response_text_text
    }

    if (validate_ck_editor_response(intent_bot_response_text_text) == "") {
        M.toast({
            "html": "At least one text response required."
        }, 2000);
        return;
    }

    let intent_response_list = [{
        "text_response": intent_bot_response_text_text,
        "speech_response": intent_bot_response_text_speech,
        "hinglish_response": "",
        "reprompt_response": intent_bot_response_reprompt,
        "ssml_response": intent_bot_response_ssml,
    }];

    if (intent_response_list.length == 0) {
        M.toast({
            'html': 'Text response cannot be empty.'
        }, 2000);
        return;
    }

    image_list = node_intent_data[selected_node].intent_response.image_list

    if (image_list && image_list.length > 0) {
        response_present.push('image');
    }

    video_list = node_intent_data[selected_node].intent_response.video_list

    if (video_list && video_list.length > 0) {
        response_present.push('video');
    }

    let card_list = Object.values(node_intent_data[selected_node].intent_response.card_list)
    card_list = card_list.filter(function(card) {
        return Boolean(card)
    })

    let is_valid = validate_card_content(card_list)

    if (is_valid) {
        if (card_list.length === 1) {
            card_list = [is_valid]
        }
    } else {
        return
    }

    if (card_list.length > 0) {
        response_present.push('link_cards');
    }

    if (category_obj_pk == "" || category_obj_pk == null) {
        alert("Please select suitable category for Intent");
        return;
    }

    table_input_list_of_list = JSON.parse(node_intent_data[selected_node].intent_response.table_list_of_list).items

    if (table_input_list_of_list) {
        response_present.push('table');
    }

    let json_string = JSON.stringify({
        intent_pk,
        intent_name,
        multilingual_name: multilingual_intent_name,
        training_data: training_data_list,
        response_sentence_list: intent_response_list,
        selected_bot_pk_list,
        image_list,
        video_list,
        card_list,
        table_input_list_of_list,
        selected_language,
        category_obj_pk,
    })
    json_string = EncryptVariable(json_string);
    let url = "/chat/save-intent-bot-response/"
    if (SELECTED_LANGUAGE !== "en") {
        url = "/chat/save-multilingual-intent/"
    } 

    $.ajax({
        url: url,
        type: "POST",
        headers: {
            'X-CSRFToken': get_csrf_token(),
        },
        data: {
            json_string: json_string
        },
        dataType: "json",
        async: false,
        success: function (response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response['status'] == 200) {
                if (is_new_intent === "True") {
                    create_language_custom_dropdowns_for_intent()
                    open_close_language_dropdown_event()
                    language_dropdown_close_onclicking_outside_event()
                    add_language_selction_event_for_edit_intent()
                    let new_url = window.location.pathname.replace("#", "").replace("create-intent", "edit-intent") + "?intent_pk=" + response["intent_pk"] + "&selected_language=en"
                    history.pushState({}, null, new_url)
                    $("#flow_excel_trigger").show()
                    $("#node-"+ selected_node + " a").show()
                    $("#node-"+ selected_node + " .node-create-child-icon").css("visibility", "visible")
                    $("#node-" + selected_node).removeClass("new-intent-node-identifier-div")
                    node_intent_data[selected_node].tree_pk = response["tree_pk"]
                    node_intent_data[selected_node].answer_pk = response["answer_pk"]
                    node_intent_data[selected_node].lazyLoaded = false
                    SELECTED_TREE_PK = response["tree_pk"]
                    intent_pk = response["intent_pk"]
                    $(".custom-tooltip-intent:not(#create_intent_menu_icon,#edit_bot_response_icon)").removeClass("disable-video-recoder-save-value")
                    $(".edit-intent-details-cancel-btn").removeClass("disable-video-recoder-save-value")
                    node_intent_data[selected_node].keep_resp_page = true
                    editor.events.nodeSelected.listeners[0](selected_node)
                }
                if (response["need_to_build"]) {
                    document.getElementById('easychat-build-bot-toast-div').style.display = 'flex';
                    document.getElementById("easychat-content-wrapper").style.maxHeight = '85vh';

                    var side_nav = document.getElementById('main-console-sidenav');
                    if (side_nav) {
                        side_nav.style.marginTop = '6.5%';
                    }
                }
                if (SELECTED_LANGUAGE === "en") {
                    load_order_of_responses(
                        node_intent_data[selected_node],
                        node_intent_data[selected_node].intent_response,
                        node_intent_data[selected_node].intent_response.modes,
                        true
                    )
                    if (is_new_intent == "False") {
                        bot_response_preview()
                        bot_preview_section_show()
                    } else {
                        is_new_intent = "False"
                    }

                    if (response["need_to_show_auto_fix_popup"]) {
                        auto_fix_selected_tree_pk = node_intent_data[selected_node].tree_pk;
                        $("#autofix_div").show()
                    }
                    
                }
                if ($(".intent_name_tooltip").length) {
                    $(".intent_name_tooltip").attr("data-tooltip", intent_name)
                } else {
                    $(".intent_name_input_div:not(#intent_name_input_div)").wrap(`
                    <span class="tooltipped intent_name_tooltip" style="flex-grow: 2;" data-position="bottom" data-tooltip="${intent_name}"></span>
                    `)
                    $(".tooltipped").tooltip()
                }
                M.toast({
                    'html': "Intent saved successfully!"
                }, 1000);
            } else {
                if (response['status'] == 301) {

                    M.toast({
                        'html': "Intent Name Already Exists"
                    }, 2000);
                } else if (response['status'] == 302) {
                    M.toast({
                        'html': response["status_message"]
                    }, 2000);
                } else if (response['status'] == 303) {
                    M.toast({
                        'html': response["status_message"]
                    }, 2000);
                } else {
                    M.toast({
                        'html': "Unable to save the Intent!"
                    }, 2000);
                }
                // enable_save_intent_buttons();
            }
        }
    });
}

function save_intent_icon() {
    let intent_icon_unique_id = ""
    let intent_pk = null

    if (window.location.href.indexOf("intent_pk=") != -1) {

        let url_parameters = get_url_vars();
        intent_pk = url_parameters["intent_pk"];
    }

    selected_bot_pk_list = [BOT_ID];

    const category_obj_pk = $("#select-intent-category").val()

    if (selected_bot_pk_list.length == 0) {
        M.toast({
            "html": "Select atleast one bot in which intent will be supported"
        }, 2000);
        return;
    }
    if (is_enable_intent_icon) {
        let intent_icon_active_elements = document.getElementsByClassName("easychat-active-intent-icon");

        if (intent_icon_active_elements.length < 1) {
            M.toast({
                'html': 'Please select atleast one intent icon.'
            }, 2000);
            return;
        } else if (intent_icon_active_elements > 1) {
            M.toast({
                'html': 'Please select only one intent icon.'
            }, 2000);
            return;
        } else {
            intent_icon_unique_id = intent_icon_active_elements[0].getAttribute("icon_unique_id");
        }
    } else {
        intent_icon_unique_id = "";
    }

    let json_string = JSON.stringify({
        intent_pk,
        selected_bot_pk_list,
        intent_icon_unique_id,
        category_obj_pk,
    })
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: '/chat/save-intent-icon-response/',
        type: "POST",
        headers: {
            'X-CSRFToken': get_csrf_token(),
        },
        data: {
            json_string: json_string
        },
        dataType: "json",
        async: false,
        success: function (response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response['status'] == 200) {
                M.toast({
                    'html': "intent icon saved successfully!"
                }, 1000);
            }
        }
    });

}

function save_intent_channel() {
    let intent_icon_unique_id = ""
    let intent_pk = null

    if (window.location.href.indexOf("intent_pk=") != -1) {

        let url_parameters = get_url_vars();
        intent_pk = url_parameters["intent_pk"];
    }

    selected_bot_pk_list = [BOT_ID];

    const category_obj_pk = $("#select-intent-category").val()

    if (selected_bot_pk_list.length == 0) {
        M.toast({
            "html": "Select atleast one bot in which intent will be supported"
        }, 2000);
        return;
    }
    
    let selected_channels_list = $(".edit-intent-channel-btn:checked").toArray();
    selected_channels_list = selected_channels_list.map((elm) => elm.value)

    if (selected_channels_list.length === 0) {
        M.toast({
            "html": "Please select at least one channel."
        }, 2000);
        return
    }

    let intent_short_name = $('#enter_intent_short_name').val().trim();
    if(selected_channels_list.includes("GoogleBusinessMessages")){
        if(intent_short_name.length > 25){
            M.toast({
                "html": "Intent short name cannot more than 25 characters."
            }, 2000);
            return
        }
    }

    let whatsapp_short_name = "";
    if (document.getElementById("whatsapp-short-name-input")) {
        whatsapp_short_name = document.getElementById("whatsapp-short-name-input").value;
        if (whatsapp_short_name.length == 0) {
            M.toast({
                "html": "Whatsapp button title cannot be empty."
            }, 2000);
            return;
        }
    }

    let whatsapp_description = "";
    if (document.getElementById("whatsapp-description-input")) {
        whatsapp_description = document.getElementById("whatsapp-description-input").value;
        if (whatsapp_description.length == 0) {
            M.toast({
                "html": "Whatsapp description cannot be empty."
            }, 2000);
            return;
        }
    }

    let json_string = JSON.stringify({
        intent_pk,
        selected_bot_pk_list,
        intent_icon_unique_id,
        whatsapp_short_name,
        whatsapp_description,
        intent_short_name,
        channel_list: selected_channels_list,
        category_obj_pk,
    })
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: '/chat/save-intent-channel/',
        type: "POST",
        headers: {
            'X-CSRFToken': get_csrf_token(),
        },
        data: {
            json_string: json_string
        },
        dataType: "json",
        async: false,
        success: function (response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response['status'] == 200) {
                M.toast({
                    'html': "intent channels saved successfully!"
                }, 1000);
            } else {
                M.toast({
                    'html': "Unable to save the Intent channels!"
                }, 2000);
            }
        }
    });

}

function save_intent_widget_response() {
    let intent_pk = null
    let response_present = []

    if (window.location.href.indexOf("intent_pk=") != -1) {

        let url_parameters = get_url_vars();
        intent_pk = url_parameters["intent_pk"];
    }

    let selected_bot_pk_list = [BOT_ID];

    const category_obj_pk = $("#select-intent-category").val()

    if (selected_bot_pk_list.length == 0) {
        M.toast({
            "html": "Select atleast one bot in which intent will be supported"
        }, 2000);
        return;
    }

    let widget_data_req = node_intent_data[selected_node].intent_response.modes
    let widget_data_field = node_intent_data[selected_node].intent_response.modes_param

    let selected_widget = $(".intent-widget-overflow-div-content div.active").attr("id")

    // File Attatchment
    let is_attachment_required = false
    let is_save_attachment_required = false
    let choosen_file_type= ""
    if (selected_widget == "file_attach_widget_content") {
        is_attachment_required = $("#checkbox-intent-attachment").prop("checked")

        if (!is_attachment_required) {
            M.toast({
                "html": "Please Select File Attach Required"
            }, 2000);
            return;
        }

        if (widget_data_req.is_save_attachment_required) {
            is_save_attachment_required = widget_data_req.is_save_attachment_required
        }
        choosen_file_type = widget_data_field.choosen_file_type;
    }
    else
        widget_data_req.is_attachment_required = "false"

    if (is_attachment_required && (!choosen_file_type || choosen_file_type == "none")) {

        M.toast({
            "html": "Please select file type."
        }, 2000);
        return;
    }

    if (is_attachment_required) {
        response_present.push('file_attach');
    }

    // Range Slider
    let is_range_slider_required = false;
    let minimum_range = ""
    let maximum_range = ""
    let range_slider_type = ""

    if (selected_widget == "range_slider_widget_content") {
        is_range_slider_required = true;
        range_slider_type = widget_data_field.range_slider_list[0].range_type;
        minimum_range = widget_data_field.range_slider_list[0].min;
        maximum_range = widget_data_field.range_slider_list[0].max;
        minimum_range = parseInt(minimum_range)
        maximum_range = parseInt(maximum_range)
        if (range_slider_type == "" || range_slider_type == null || range_slider_type == undefined) {
            M.toast({
                'html': 'Please select a range slider option.'
            }, 2000);
            return;
        }

        if (/^\d+$/.test(minimum_range) == false || /^\d+$/.test(maximum_range) == false) {
            M.toast({
                'html': 'Please enter a valid range.'
            }, 2000);
            return;
        }
        if (minimum_range >= maximum_range) {
            M.toast({
                'html': 'Minimum range should be less than maximum.'
            }, 2000);
            return;
        }

        if (minimum_range >= 9999999999 || maximum_range >= 9999999999) {
            M.toast({
                'html': 'Range values should be less than 10 digits'
            }, 2000);
            return;
        }

        response_present.push('range_slider');
    } else {
        widget_data_req.is_range_slider = "false"
    }

    //Radio Button
    let is_radio_button_allowed = false
    let radio_choices_list = []
    if (selected_widget == "radio_widget_content") {
        is_radio_button_allowed = true
        radio_choices_list = Object.values(widget_data_field.radio_button_choices).filter(function(elm) {
            return Boolean(elm)
        })
        if (radio_choices_list.length == 0) {
            M.toast({
                "html": "At least one choice is required."
            }, 2000);
            return;
        }
        response_present.push('radio_button');
    } else {
        widget_data_req.is_radio_button = "false"
    }

    //Checkbox
    let is_check_box_allowed = false
    let checkbox_choices_list = []
    if (selected_widget == "checkbox_widget_content") {
        is_check_box_allowed = true
        checkbox_choices_list = Object.values(widget_data_field.check_box_choices).filter(function(elm) {
            return Boolean(elm)
        })

        if (checkbox_choices_list.length == 0) {
            M.toast({
                "html": "At least one choice is required."
            }, 2000);
            return;
        }
        response_present.push('checkbox');
    } else {
        widget_data_req.is_check_box = "false"
    }

    //Phone Widget
    let is_phone_widget_enabled = false
    let country_code = "in"
    if (selected_widget == "phone_number_widget_content") {
        is_phone_widget_enabled = $("#checkbox-intent-country-code-cb").prop("checked")
        
        if (!is_phone_widget_enabled) {
            M.toast({
                'html': 'Please Select Enable Country Code Option.'
            }, 2000);
            return;
        }

        if (widget_data_field.country_code) {
            country_code = widget_data_field.country_code
        }

        response_present.push('phone_number');
    } else {
        widget_data_req.is_phone_widget_enabled = "false"
    }

    // Form
    let is_create_form_allowed = false
    if (selected_widget == 'create_form_widget_content')
        is_create_form_allowed = true
    let form_name = ""
    form_fields_list = [];
    if (is_create_form_allowed) {
        response_present.push('form');
        form_name = document.getElementById('form_name').value;
        form_name = strip_unwanted_characters(stripHTML(form_name));
        form_name = form_name.trim();
        if (form_name == '') {
            M.toast({
                "html": "Please enter a valid form name"
            }, 2000);
            return;
        }

        let fields_present = []

        let ordered_fileds = $("#create-form-fields").sortable("toArray").filter(function(elm) {
            return elm.match(/saved_data_div/)
        })

        if (ordered_fileds.length == 0) {
            ordered_fileds = $("#create-form-fields").sortable("toArray")

            fields_present = ordered_fileds.map(function(elm) {
                return document.getElementById(elm)
            });
        } else {
            fields_present = ordered_fileds.map(function(elm) {
                return document.getElementById("field-" + elm.split("saved_data_div_")[1])
            });
        }

        if (fields_present.length == 0) {
            M.toast({
                "html": "Please add atleast one form section"
            }, 2000);
            return;
        }
        for (let i = 0; i < fields_present.length; ++i) {
            let field_id = fields_present[i].id;
            let field_div = document.getElementById(field_id);
            let field_id_num = field_id.split('-')[1]

            let label_name, input_type, placeholder_or_options_elem1, placeholder_or_options_elem2, validator, attachment_type, optional, range_type, calendar_type, dependent;
            placeholder_or_options_elem2 = ""

            label_name = document.getElementById('input_name_' + field_id_num + '_1').value;
            label_name = strip_unwanted_characters(stripHTML(label_name));

            input_type = document.getElementById('input_type_' + field_id_num).value
            // input_type = input_name_mapping(input_type)

            placeholder_or_options_elem1 = document.getElementById('input_selected_type_' + field_id_num + '_3').value;
            validator = document.getElementById('validator_' + field_id_num).value;

            // validator = validator_mapping(validator);

            attachment_type = document.getElementById('file_attach_type_' + field_id_num).value;

            range_type = document.getElementById('range_selector_' + field_id_num).value;

            calendar_type = document.getElementById('calendar_selector_type_' + field_id_num).value;

            optional = document.getElementById('optional-toggle-field-' + field_id_num).checked;

            dependent = document.getElementById('dependent-field-' + field_id_num);

            country_code = $("#phone_number_selector_type_" + field_id_num).intlTelInput("getSelectedCountryData").iso2

            if (dependent) {
                dependent = dependent.checked;
            } else {
                dependent = false;
            }
            let dependent_on = ''
            let dependent_on_label_name = ''
            if (dependent) {
                dependent_on = document.getElementById('dependent_field_dropdown_' + field_id_num).value;
                dependent_on_label_name = document.getElementById('input_name_' + dependent_on + '_1')?.value
            }

            if (dependent_on == 'Select Dependency') {
                M.toast({
                    "html": "Please select a valid dependency"
                }, 2000);
                return;
            }

            let dependent_fields = document.querySelectorAll('.dependent-dropdown');
            let dependent_ids = []
            for (let j = 0; j < dependent_fields.length; j++) {
                if (dependent_fields[j].value == field_id_num) {
                    dependent_ids.push(dependent_fields[j].id.split('_')[3])
                }
            }
            
            dependent_ids = dependent_ids.join('$$$')

            label_name = label_name.trim();
            if (label_name == "") {
                M.toast({
                    "html": "Please enter a valid label name"
                }, 2000);
                return;
            }

            if (input_type == "") {
                M.toast({
                    "html": "Please enter an input type"
                }, 2000);
                return;
            }

            let placeholder_or_options = placeholder_or_options_elem1;

            if (input_type == 'file_attach') {
                placeholder_or_options = attachment_type
            } else {
                if (input_type == "radio") {

                    placeholder_or_options = form_get_radio_button_list(field_id.split("-")[1])
                    placeholder_or_options = placeholder_or_options.join('$$$')

                } else if (input_type == "checkbox") {
                    placeholder_or_options = form_get_check_box_list(field_id.split("-")[1])
                    placeholder_or_options = placeholder_or_options.join('$$$')

                } else if (input_type == "dropdown_list") {
                    placeholder_or_options = form_get_dropdown_list(field_id.split("-")[1])
                    placeholder_or_options = placeholder_or_options.join('$$$')
                } else if (input_type == "range") {
                    var form_range_slider_min_value = document.getElementById("form-range-slider-min-range-" + field_id.split("-")[1]).value;
                    var form_range_slider_max_value = document.getElementById("form-range-slider-max-range-" + field_id.split("-")[1]).value;
                    placeholder_or_options = form_range_slider_min_value + "-" + form_range_slider_max_value;
                }
            }

            if (input_type == "text_field" || input_type == "phone_number") {
                if (placeholder_or_options == "") {
                    M.toast({
                        "html": "Please enter placeholder value"
                    }, 2000);
                    return;
                }
            } else if (!api_integrated_fields.includes(field_id_num) && input_type == "dropdown_list" && placeholder_or_options == "") {
                M.toast({
                    "html": "Please enter at least one and valid dropdown option"
                }, 2000);
                return;
            } else if (!api_integrated_fields.includes(field_id_num) && input_type == "checkbox" && placeholder_or_options == "") {
                M.toast({
                    "html": "Please enter at least one and valid checkbox option"
                }, 2000);
                return;
            } else if (!api_integrated_fields.includes(field_id_num) && input_type == "radio" && placeholder_or_options == "") {
                M.toast({
                    "html": "Please enter at least one and valid radio button option"
                }, 2000);
                return;
            } else if (input_type == "range") {
                if (placeholder_or_options.split('-')[0] == "" || placeholder_or_options.split('-')[1] == "") {
                    M.toast({
                        "html": "Please enter a range"
                    }, 2000);
                    return;
                } else if (placeholder_or_options.split('-').length != 2 || (isNaN(placeholder_or_options.split('-')[0]) || isNaN(placeholder_or_options.split('-')[1]))) {
                    M.toast({
                        "html": "Please enter a valid range"
                    }, 2000);
                    return;
                } else if (parseInt(placeholder_or_options.split('-')[0]) >= parseInt(placeholder_or_options.split('-')[1])) {
                    M.toast({
                        'html': 'Minimum range should be less than maximum.'
                    }, 2000);
                    return;
                }
            } else if (input_type == "file_attach" && (placeholder_or_options == undefined || placeholder_or_options == "")) {
                M.toast({
                    "html": "Please select file type"
                }, 2000);
                return;
            }

            form_fields_list.push({
                label_name: label_name,
                input_type: input_type,
                validator: validator,
                placeholder_or_options: placeholder_or_options,
                optional: optional.toString(),
                range_type: range_type,
                calendar_type: calendar_type,
                field_id_num: field_id_num,
                is_dependent: dependent.toString(),
                dependent_on: dependent_on.toString(),
                dependent_on_label_name: dependent_on_label_name,
                dependent_field_ids: dependent_ids,
                country_code: country_code,
            })
        }

        response_present.push('form');

    } else {
        widget_data_req.is_create_form_allowed = false
    }
    widget_data_field.form_fields_list = form_fields_list

    //Calendar
    let is_calender_picker_allowed = false
    let is_single_calender_date_picker_allowed = false
    let is_multi_calender_date_picker_allowed = false
    let is_single_calender_time_picker_allowed = false
    let is_multi_calender_time_picker_allowed = false
    let is_calender_date_picker_enabled = document.getElementById('enabledatepicker_switch1').checked
    let is_calender_time_picker_enabled = document.getElementById('enabletimepicker_switch2').checked
    if (selected_widget == "calendar_picker_widget_content") {
        if (!is_calender_date_picker_enabled && !is_calender_time_picker_enabled) {
            M.toast({
                'html': 'Please select atleast one option in calendar picker.'
            }, 2000);
            return;
        }
        is_calender_picker_allowed = true
        if (is_calender_date_picker_enabled) {
            is_single_calender_date_picker_allowed = widget_data_req.is_single_datepicker == "true";
            is_multi_calender_date_picker_allowed = widget_data_req.is_multi_datepicker == "true";
        }
        if (is_calender_time_picker_enabled) {
            is_single_calender_time_picker_allowed = widget_data_req.is_single_timepicker == "true";
            is_multi_calender_time_picker_allowed = widget_data_req.is_multi_timepicker == "true";
        }
    }
        
    else 
        widget_data_req.is_calender = "false"

    if (is_calender_picker_allowed) {

        if (is_calender_date_picker_enabled) {
            if ((!is_single_calender_date_picker_allowed && !is_multi_calender_date_picker_allowed)) {
                M.toast({
                    'html': 'Please select atleast one option in date picker.'
                }, 2000);
                return;
            }
        }

        if (is_calender_time_picker_enabled) {
            if ((!is_single_calender_time_picker_allowed && !is_multi_calender_time_picker_allowed)) {
                M.toast({
                    'html': 'Please select atleast one option in time picker.'
                }, 2000);
                return;
            }
        }

        response_present.push('calendar_picker');
    }

    //Dropdown
    let is_drop_down_allowed = false
    let dropdown_choices_list = []
    if (selected_widget == "dropdown_widget_content") {
        is_drop_down_allowed = true
        dropdown_choices_list = Object.values(widget_data_field.drop_down_choices).filter(function(elm) {
            return Boolean(elm)
        })
        
        if (dropdown_choices_list.length == 0) {
            M.toast({
                "html": "At least one choice is required."
            }, 2000);
            return;
        }
        response_present.push('drop_down');
    } else {
        widget_data_req.is_drop_down = "false"
    }

    // Video Recorder
    let is_video_recorder_allowed = false
    let is_save_video_attachment_required = false
    if (selected_widget == "video_widget_content") {
        is_video_recorder_allowed = $("#checkbox-intent-video-recorder").prop("checked")
        if (!is_video_recorder_allowed) {
            M.toast({
                "html": "Please Select Video Recorder Allowed"
            }, 2000);
            return;
        }
        is_save_video_attachment_required = widget_data_req.is_save_video_attachment;
        is_save_video_attachment_required = is_save_video_attachment_required ? is_save_video_attachment_required : false
    }
    if (is_video_recorder_allowed) {
        response_present.push('video_record')
    } else {
        widget_data_req.is_video_recorder_allowed = "false"
    }
    
    let json_string = JSON.stringify({
        intent_pk,
        selected_bot_pk_list,
        is_attachment_required,
        is_save_attachment_required,
        choosen_file_type,
        is_range_slider_required,
        minimum_range,
        maximum_range,
        range_slider_type,
        is_radio_button_allowed,
        radio_button_choices: radio_choices_list,
        is_check_box_allowed,
        checkbox_choices_list,
        is_phone_widget_enabled,
        country_code,
        is_create_form_allowed,
        form_name,
        form_fields_list,
        is_calender_picker_allowed,
        is_single_calender_date_picker_allowed,
        is_multi_calender_date_picker_allowed,
        is_single_calender_time_picker_allowed,
        is_multi_calender_time_picker_allowed,
        is_date_picker_allowed: false,
        is_time_picker_allowed: false,
        is_single_date_picker_allowed: false,
        is_multi_date_picker_allowed: false,
        is_single_time_picker_allowed: false,
        is_multi_time_picker_allowed: false,
        is_drop_down_allowed,
        dropdown_choices_list,
        is_video_recorder_allowed,
        is_save_video_attachment_required,
        category_obj_pk,
    });

    json_string = EncryptVariable(json_string);

    $.ajax({
        url: '/chat/save-intent-widget-response/',
        type: "POST",
        headers: {
            'X-CSRFToken': get_csrf_token(),
        },
        data: {
            json_string: json_string
        },
        dataType: "json",
        async: false,
        success: function (response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response['status'] == 200) {
                if (!selected_widget) {
                    $("#response_widget .edit-intent-details-action-btns-wrapper .edit-intent-details-next-btn").addClass("disable-video-recoder-save-value")
                }
                if (SELECTED_LANGUAGE === "en") {
                    load_order_of_responses(
                        node_intent_data[selected_node],
                        node_intent_data[selected_node].intent_response,
                        node_intent_data[selected_node].intent_response.modes,
                        true
                    )
                    bot_response_preview()
                    bot_preview_section_show()
                }
                M.toast({
                    'html': "intent widget saved successfully!"
                }, 1000);
            } else {
                M.toast({
                    'html': "Unable to save intent widget!"
                }, 2000);
            }
        }
    });
}

function save_intent_recomm() {
    let intent_pk = null

    if (window.location.href.indexOf("intent_pk=") != -1) {

        let url_parameters = get_url_vars();
        intent_pk = url_parameters["intent_pk"];
    }

    selected_bot_pk_list = [BOT_ID];

    const category_obj_pk = $("#select-intent-category").val()

    if (selected_bot_pk_list.length == 0) {
        M.toast({
            "html": "Select atleast one bot in which intent will be supported"
        }, 2000);
        return;
    }

    let recommended_intent_list = []
    
    recommended_intent_list = node_intent_data[selected_node].recommeded_intents_dict_list
    let is_recommendation_menu = node_intent_data[selected_node].intent_response.modes.is_recommendation_menu === "true"
    is_recommendation_menu = is_recommendation_menu ? true : false

    let json_string = JSON.stringify({
        intent_pk,
        selected_bot_pk_list,
        recommended_intent_list,
        is_recommendation_menu,
        category_obj_pk,
    })
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: '/chat/save-intent-quick-recom/',
        type: "POST",
        headers: {
            'X-CSRFToken': get_csrf_token(),
        },
        data: {
            json_string: json_string
        },
        dataType: "json",
        async: false,
        success: function (response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            load_order_of_responses(
                node_intent_data[selected_node],
                node_intent_data[selected_node].intent_response,
                node_intent_data[selected_node].intent_response.modes,
                true
            )
            bot_response_preview()
            bot_preview_section_show()
            if (response['status'] == 200) {
                M.toast({
                    'html': "intent quick recommmendations saved successfully!"
                }, 1000);
            } else {
                M.toast({
                    'html': "Unable to save the Intent quick recommmendations!"
                }, 2000);
            }
        }
    });

}

function save_intent_order_response() {
    let intent_pk = null

    if (window.location.href.indexOf("intent_pk=") != -1) {

        let url_parameters = get_url_vars();
        intent_pk = url_parameters["intent_pk"];
    }

    selected_bot_pk_list = [BOT_ID];

    const category_obj_pk = $("#select-intent-category").val()

    if (selected_bot_pk_list.length == 0) {
        M.toast({
            "html": "Select atleast one bot in which intent will be supported"
        }, 2000);
        return;
    }

    let is_custom_order_selected = node_intent_data[selected_node].is_custom_order_selected
    let order_of_response = node_intent_data[selected_node].order_of_response

    let json_string = JSON.stringify({
        intent_pk,
        selected_bot_pk_list,
        is_custom_order_selected,
        order_of_response,
        category_obj_pk,
    })
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: '/chat/save-intent-order-response/',
        type: "POST",
        headers: {
            'X-CSRFToken': get_csrf_token(),
        },
        data: {
            json_string: json_string
        },
        dataType: "json",
        async: false,
        success: function (response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response['status'] == 200) {
                M.toast({
                    'html': "Intent order of response saved successfully!"
                }, 1000);
                if (SELECTED_LANGUAGE === "en") {
                    // load_order_of_responses(
                    //     node_intent_data[selected_node],
                    //     node_intent_data[selected_node].intent_response,
                    //     node_intent_data[selected_node].intent_response.modes,
                    //     true
                    // )
                    bot_response_preview()
                    bot_preview_section_show()
                }
            } else {
                M.toast({
                    'html': "Unable to save the Intent order of response!"
                }, 2000);
            }
        }
    });

}

function save_intent_explanation_flow() {
    let intent_pk = null

    if (window.location.href.indexOf("intent_pk=") != -1) {

        let url_parameters = get_url_vars();
        intent_pk = url_parameters["intent_pk"];
    }

    selected_bot_pk_list = [BOT_ID];

    const category_obj_pk = $("#select-intent-category").val()

    if (selected_bot_pk_list.length == 0) {
        M.toast({
            "html": "Select atleast one bot in which intent will be supported"
        }, 2000);
        return;
    }

    let explanation = node_intent_data[selected_node].explanation

    let json_string = JSON.stringify({
        intent_pk,
        selected_bot_pk_list,
        explanation,
        category_obj_pk,
    })
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: '/chat/save-intent-conversion-flow-description/',
        type: "POST",
        headers: {
            'X-CSRFToken': get_csrf_token(),
        },
        data: {
            json_string: json_string
        },
        dataType: "json",
        async: false,
        success: function (response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response['status'] == 200) {
                M.toast({
                    'html': "Intent conversion flow description saved successfully!"
                }, 1000);
            } else {
                M.toast({
                    'html': "Unable to save the Intent conversion flow description!"
                }, 2000);
            }
        }
    });

}

function save_intent_advanced_nlp_config() {
    let intent_pk = null

    if (window.location.href.indexOf("intent_pk=") != -1) {

        let url_parameters = get_url_vars();
        intent_pk = url_parameters["intent_pk"];
    }

    selected_bot_pk_list = [BOT_ID];

    const category_obj_pk = $("#select-intent-category").val()

    if (selected_bot_pk_list.length == 0) {
        M.toast({
            "html": "Select atleast one bot in which intent will be supported"
        }, 2000);
        return;
    }

    let necessary_keywords = node_intent_data[selected_node].necessary_keywords
    let restricted_keywords = node_intent_data[selected_node].restricted_keywords
    let intent_threshold = node_intent_data[selected_node].intent_threshold

    let json_string = JSON.stringify({
        intent_pk,
        selected_bot_pk_list,
        necessary_keywords,
        restricted_keywords,
        intent_threshold,
        category_obj_pk,
    })
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: '/chat/save-intent-advance-nlp-config/',
        type: "POST",
        headers: {
            'X-CSRFToken': get_csrf_token(),
        },
        data: {
            json_string: json_string
        },
        dataType: "json",
        async: false,
        success: function (response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response['status'] == 200) {
                M.toast({
                    'html': "Intent advanced nlp config successfully!"
                }, 1000);
            } else {
                M.toast({
                    'html': "Unable to save the Intent advanced nlp config!"
                }, 2000);
            }
        }
    });

}

function save_intent_settings() {
    let intent_pk = null

    if (window.location.href.indexOf("intent_pk=") != -1) {

        let url_parameters = get_url_vars();
        intent_pk = url_parameters["intent_pk"];
    }

    selected_bot_pk_list = [BOT_ID];

    const category_obj_pk = $("#select-intent-category").val()

    if (selected_bot_pk_list.length == 0) {
        M.toast({
            "html": "Select atleast one bot in which intent will be supported"
        }, 2000);
        return;
    }

    let settings = node_intent_data[selected_node].other_settings

    let is_faq_intent = settings.is_faq_intent
    let is_small_talk = settings.is_small_talk
    let is_part_of_suggestion_list = settings.is_part_of_suggestion_list
    let validator_id = settings.selected_validator_obj?.processor__pk
    validator_id = validator_id ? validator_id : ""
    let is_feedback_required = settings.is_feedback_required
    let authentication_id = settings.selected_user_authentication?.id
    authentication_id = authentication_id ? authentication_id : ""
    let is_authentication_required = settings.is_authentication_required
    let is_child_intent_visible = settings.is_child_tree_visible
    let is_go_back_enabled = settings.is_go_back_enabled
    let child_choices = settings.child_choices_list
    let is_last_tree = settings.is_last_tree
    let disposition_code = settings.disposition_code
    let is_exit_tree = settings.is_exit_tree
    let is_transfer_tree = settings.is_transfer_tree
    let allow_barge = settings.allow_barge
    let is_catalogue_purchased = settings.is_item_purchased
    let is_catalogue_added = node_intent_data[selected_node].intent_response.modes.is_catalogue_added
    is_catalogue_added = is_catalogue_added === "true" ? true : false
    let selected_catalogue_sections = node_intent_data[selected_node].intent_response.modes_param.temp_selected_catalogue_sections;
    node_intent_data[selected_node].intent_response.modes_param.selected_catalogue_sections = selected_catalogue_sections;
    if (!selected_catalogue_sections || !selected_catalogue_sections.length) {
        selected_catalogue_sections = []
    }
    
    if (is_catalogue_added && (!selected_catalogue_sections || !selected_catalogue_sections.length)) {
        M.toast({
            "html": "Please select atleast one section for WhatsApp Catalogue"
        }, 2000);
        return;
    }

    let is_automate_recursion_enabled = settings.is_automatic_recursion_enabled
    let post_processor_variable = settings.post_processor_variable
    let flow_analytics_variable = settings.flow_analytics_variable
    let is_category_intent_allowed = settings.is_category_response_allowed


    let json_string = JSON.stringify({
        intent_pk,
        selected_bot_pk_list,
        is_faq_intent,
        is_small_talk,
        is_part_of_suggestion_list,
        validator_id,
        is_feedback_required,
        authentication_id,
        is_authentication_required,
        is_child_intent_visible,
        is_go_back_enabled,
        child_choices,
        is_last_tree,
        disposition_code,
        is_exit_tree,
        is_transfer_tree,
        allow_barge,
        is_catalogue_added,
        is_automate_recursion_enabled,
        post_processor_variable,
        flow_analytics_variable,
        is_category_intent_allowed,
        category_obj_pk,
        selected_catalogue_sections,
        is_catalogue_purchased
    })
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: '/chat/save-intent-settings/',
        type: "POST",
        headers: {
            'X-CSRFToken': get_csrf_token(),
        },
        data: {
            json_string: json_string
        },
        dataType: "json",
        async: false,
        success: function (response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response['status'] == 200) {
                M.toast({
                    'html': "Intent settings saved successfully!"
                }, 1000);
                if (response["trigger_flow_change"]) {
                    const tree_structure = fetchIntentTreeStructureByIntentID(intent_pk, SELECTED_LANGUAGE)
                    editor.clear()
                    editor.nodeId = 1
                    node_intent_data = {}
                    build_initial_flow(tree_structure[1], true, null, window.outerWidth / 6)
                    update_flow()
                    update_node_vertical_positions(1)
                    $(`#node-${selected_node}`).addClass("selected")
                }
            } else if (response['status'] == 401) {
                M.toast({
                    'html': "Kindly select all the children in child order"
                }, 4000);
            } else {
                M.toast({
                    'html': "Unable to save the Intent settings!"
                }, 2000);
            }
        }
    });

}

function save_tree_bot_response() {
    let tree_pk = node_intent_data[selected_node].tree_pk
    let is_new_tree;
    let is_in_between_tree;
    let parent;
    if (node_intent_data[selected_node].is_new_tree) {
        parent = editor.getNodeFromId(selected_node).inputs.input_1.connections[0].node
        tree_pk = node_intent_data[parent].tree_pk
        is_new_tree = true
        if (node_intent_data[selected_node].is_in_between_tree) {
            is_in_between_tree = true
        } else {
            is_in_between_tree = false
        }
    } else {
        is_new_tree = false
    }

    let tree_name = $('#intent_name_input_div').val().trim();
    tree_name = stripHTML(tree_name);
    let accept_keywords = $("#tree_accept_keywords").val();
    let tree_short_name = document.getElementById("enter_tree_short_name").value
    tree_short_name = tree_short_name.trim()

    if(SELECTED_LANGUAGE === "en" && tree_short_name.length > 25){
        M.toast({
            "html": "Tree short name cannot be more than 25 characters."
        }, 2000);
        return;
    }

    let whatsapp_short_name = null;
    if (SELECTED_LANGUAGE === "en" && document.getElementById("tree-whatsapp-short-name-input")) {
        whatsapp_short_name = node_intent_data[selected_node].whatsapp_short_name;

        if (!whatsapp_short_name) {
            M.toast({
                "html": "Whatsapp button title connot be empty."
            }, 2000);
            return;
        }
    }

    let whatsapp_description = null;
    if (SELECTED_LANGUAGE === "en" && document.getElementById("tree-whatsapp-description-input")) {
        whatsapp_description = node_intent_data[selected_node].whatsapp_description;

        if (!whatsapp_description) {
            M.toast({
                "html": "Whatsapp description connot be empty."
            }, 2000);
            return;
        }
    }

    if (tree_name == "") {
        M.toast({
            "html": "Child Intent Name cannot be empty."
        }, 2000);
        return;
    }

    let response_present = ['text'];

    intent_bot_response_text_text = $("#intent_bot_response_text_text").trumbowyg('html');
    intent_bot_response_text_speech = $("#intent_bot_response_text_speech").trumbowyg('html');
    intent_bot_response_reprompt = $("#intent_bot_response_reprompt").trumbowyg('html');
    intent_bot_response_ssml = $("#intent_bot_response_ssml").val();

    intent_bot_response_text_text = intent_bot_response_text_text.replace(new RegExp('\r?<br />', 'g'), '<br>');

    if (validate_ck_editor_response(intent_bot_response_text_text) != "" && validate_ck_editor_response(intent_bot_response_text_speech) == "") {
        intent_bot_response_text_speech = intent_bot_response_text_text
    }

    if (validate_ck_editor_response(intent_bot_response_text_text) == "") {
        M.toast({
            "html": "At least one text response required."
        }, 2000);
        return;
    }

    let intent_response_list = [{
        "text_response": intent_bot_response_text_text,
        "speech_response": intent_bot_response_text_speech,
        "hinglish_response": "",
        "reprompt_response": intent_bot_response_reprompt,
        "ssml_response": intent_bot_response_ssml,
    }];

    if (intent_response_list.length == 0) {
        M.toast({
            'html': 'Text response cannot be empty.'
        }, 2000);
        return;
    }

    image_list = node_intent_data[selected_node].intent_response.image_list

    if (image_list && image_list.length > 0) {
        response_present.push('image');
    }

    video_list = node_intent_data[selected_node].intent_response.video_list

    if (video_list && video_list.length > 0) {
        response_present.push('video');
    }

    let card_list = Object.values(node_intent_data[selected_node].intent_response.card_list)
    card_list = card_list.filter(function(card) {
        return Boolean(card)
    })

    let is_valid = validate_card_content(card_list)

    if (is_valid) {
        if (card_list.length === 1) {
            card_list = [is_valid]
        }
    } else {
        return
    }

    if (card_list.length > 0) {
        response_present.push('link_cards');
    }

    category_obj_pk = document.getElementById("select-intent-category").value

    if (category_obj_pk == "" || category_obj_pk == null) {
        alert("Please select suitable category for Intent");
        return;
    }

    table_input_list_of_list = JSON.parse(node_intent_data[selected_node].intent_response.table_list_of_list).items

    if (table_input_list_of_list) {
        response_present.push('table');
    }
    if (SELECTED_LANGUAGE !== "en") {
        tree_name = $('#secondary_intent_name_input_div').val()
    }
    let json_string = JSON.stringify({
        tree_pk,
        tree_name,
        tree_short_name,
        whatsapp_short_name,
        whatsapp_description,
        accept_keywords,
        response_sentence_list: intent_response_list,
        image_list,
        video_list,
        card_list,
        table_input_list_of_list,
        is_new_tree,
        is_in_between_tree,
        selected_language,
    })
    json_string = EncryptVariable(json_string);
    let url = "/chat/save-tree-response/"
    if (SELECTED_LANGUAGE !== "en") {
        url = "/chat/save-multilingual-tree/"
    } 

    $.ajax({
        url: url,
        type: "POST",
        headers: {
            'X-CSRFToken': get_csrf_token(),
        },
        data: {
            json_string: json_string
        },
        dataType: "json",
        async: false,
        success: function (response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response['status'] == 200) {
                if (node_intent_data[selected_node].is_new_tree) {
                    $("#node-" + selected_node).removeClass("new-intent-node-identifier-div")
                    $("#node-"+ selected_node + " a").show()
                    $("#node-"+ selected_node + " .node-create-child-icon").css("visibility", "visible")
                    $("#node-"+ selected_node + " .node-remove-child-icon").css("visibility", "hidden")
                    node_intent_data[selected_node].tree_pk = response["new_tree_pk"]
                    node_intent_data[parent].lazyLoaded = false
                    node_intent_data[selected_node].lazyLoaded = false
                    $(".custom-tooltip-intent:not(#create_intent_menu_icon,#edit_bot_response_icon)").removeClass("disable-video-recoder-save-value")
                    $(".edit-intent-details-cancel-btn").removeClass("disable-video-recoder-save-value")
                    $("#save_intent_category").hide()
                    $("#save_intent_flow").show()
                }
                if (SELECTED_LANGUAGE === "en") {
                    load_order_of_responses(
                        node_intent_data[selected_node],
                        node_intent_data[selected_node].intent_response,
                        node_intent_data[selected_node].intent_response.modes,
                        true
                    )
                    if (!node_intent_data[selected_node].is_new_tree) {
                        bot_response_preview()
                        bot_preview_section_show()
                    } else {
                        node_intent_data[selected_node].is_new_tree = false
                        node_intent_data[selected_node].keep_resp_page = true
                        editor.events.nodeSelected.listeners[0](selected_node)
                    }

                    if (response["need_to_show_auto_fix_popup"]) {
                        auto_fix_selected_tree_pk = node_intent_data[selected_node].tree_pk;
                        $("#autofix_div").show()
                    }
                }
                if ($(".intent_name_tooltip").length) {
                    $(".intent_name_tooltip").attr("data-tooltip", tree_name)
                } else {
                    $(".intent_name_input_div:not(#intent_name_input_div)").wrap(`
                    <span class="tooltipped intent_name_tooltip" style="flex-grow: 2;" data-position="bottom" data-tooltip="${tree_name}"></span>
                    `)
                    $(".tooltipped").tooltip()
                }
                M.toast({
                    'html': "Tree saved successfully!"
                }, 1000);
            } else {
                if (response['status'] == 301) {

                    M.toast({
                        'html': response["status_message"]
                    }, 2000);
                } else if (response['status'] == 302) {
                    M.toast({
                        'html': response["status_message"]
                    }, 2000);
                } else if (response['status'] == 303) {
                    M.toast({
                        'html': response["status_message"]
                    }, 2000);
                } else {
                    M.toast({
                        'html': response["status_message"]
                    }, 2000);
                }
                // enable_save_intent_buttons();
            }
        }
    });
}

function decide_save_bot_response() {
    last_selected_elm.querySelector(".node-wrapper-div span").innerText = node_intent_data[selected_node].name.trim();
    if (selected_node == 1) {
        save_training_intent_and_bot_response()
    } else {
        save_tree_bot_response()
    }
}

function save_tree_widget_response() {
    let tree_pk = node_intent_data[selected_node].tree_pk
    let response_present = []

    let widget_data_req = node_intent_data[selected_node].intent_response.modes
    let widget_data_field = node_intent_data[selected_node].intent_response.modes_param

    let selected_widget = $(".intent-widget-overflow-div-content div.active").attr("id")

    // File Attatchment
    let is_attachment_required = false
    let is_save_attachment_required = false
    let choosen_file_type= ""
    if (selected_widget == "file_attach_widget_content") {
        is_attachment_required = $("#checkbox-intent-attachment").prop("checked")

        if (!is_attachment_required) {
            M.toast({
                "html": "Please Select File Attach Required"
            }, 2000);
            return;
        }

        is_save_attachment_required = widget_data_req.is_save_attachment_required
        choosen_file_type = widget_data_field.choosen_file_type;
    }
    else
        widget_data_req.is_attachment_required = "false"

    if (is_attachment_required && choosen_file_type == "") {

        M.toast({
            "html": "Please select file type."
        }, 2000);
        return;
    }

    if (is_attachment_required) {
        response_present.push('file_attach');
    }

    // Range Slider
    let is_range_slider_required = false;
    let minimum_range = ""
    let maximum_range = ""
    let range_slider_type = ""

    if (selected_widget == "range_slider_widget_content") {
        is_range_slider_required = true;
        range_slider_type = widget_data_field.range_slider_list[0].range_type;
        minimum_range = widget_data_field.range_slider_list[0].min;
        maximum_range = widget_data_field.range_slider_list[0].max;
        minimum_range = parseInt(minimum_range)
        maximum_range = parseInt(maximum_range)
        if (range_slider_type == "" || range_slider_type == null || range_slider_type == undefined) {
            M.toast({
                'html': 'Please select a range slider option.'
            }, 2000);
            return;
        }

        if (/^\d+$/.test(minimum_range) == false || /^\d+$/.test(maximum_range) == false) {
            M.toast({
                'html': 'Please enter a valid range.'
            }, 2000);
            return;
        }
        if (minimum_range >= maximum_range) {
            M.toast({
                'html': 'Minimum range should be less than maximum.'
            }, 2000);
            return;
        }

        if (minimum_range >= 9999999999 || maximum_range >= 9999999999) {
            M.toast({
                'html': 'Range values should be less than 10 digits'
            }, 2000);
            return;
        }

        response_present.push('range_slider');
    } else {
        widget_data_req.is_range_slider = "false"
    }

    //Radio Button
    let is_radio_button_allowed = false
    let radio_choices_list = []
    if (selected_widget == "radio_widget_content") {
        is_radio_button_allowed = true
        radio_choices_list = Object.values(widget_data_field.radio_button_choices)
        if (radio_choices_list.length == 0) {
            M.toast({
                "html": "At least one choice is required."
            }, 2000);
            return;
        }
        response_present.push('radio_button');
    } else {
        widget_data_req.is_radio_button = "false"
    }

    //Checkbox
    let is_check_box_allowed = false
    let checkbox_choices_list = []
    if (selected_widget == "checkbox_widget_content") {
        is_check_box_allowed = true
        checkbox_choices_list = Object.values(widget_data_field.check_box_choices)

        if (checkbox_choices_list.length == 0) {
            M.toast({
                "html": "At least one choice is required."
            }, 2000);
            return;
        }
        response_present.push('checkbox');
    } else {
        widget_data_req.is_check_box = "false"
    }

    //Phone Widget
    let is_phone_widget_enabled = false
    let country_code = "in"
    if (selected_widget == "phone_number_widget_content") {
        is_phone_widget_enabled = $("#checkbox-intent-country-code-cb").prop("checked")
        
        if (!is_phone_widget_enabled) {
            M.toast({
                'html': 'Please Select Enable Country Code Option.'
            }, 2000);
            return;
        }

        if (widget_data_field.country_code) {
            country_code = widget_data_field.country_code
        }

        response_present.push('phone_number');
    } else {
        widget_data_req.is_phone_widget_enabled = "false"
    }

    // Form
    let is_create_form_allowed = false
    if (selected_widget == 'create_form_widget_content')
        is_create_form_allowed = true
    let form_name = ""
    form_fields_list = [];
    if (is_create_form_allowed) {
        form_name = document.getElementById('form_name').value;
        form_name = strip_unwanted_characters(stripHTML(form_name));
        form_name = form_name.trim();
        if (form_name == '') {
            M.toast({
                "html": "Please enter a valid form name"
            }, 2000);
            return;
        }

        let fields_present = []

        let ordered_fileds = $("#create-form-fields").sortable("toArray").filter(function(elm) {
            return elm.match(/saved_data_div/)
        })

        if (ordered_fileds.length == 0) {
            ordered_fileds = $("#create-form-fields").sortable("toArray")

            fields_present = ordered_fileds.map(function(elm) {
                return document.getElementById(elm)
            });
        } else {
            fields_present = ordered_fileds.map(function(elm) {
                return document.getElementById("field-" + elm.split("saved_data_div_")[1])
            });
        }

        if (fields_present.length == 0) {
            M.toast({
                "html": "Please add atleast one form section"
            }, 2000);
            return;
        }
        for (let i = 0; i < fields_present.length; ++i) {
            let field_id = fields_present[i].id;
            let field_div = document.getElementById(field_id);
            let field_id_num = field_id.split('-')[1]

            let label_name, input_type, placeholder_or_options_elem1, placeholder_or_options_elem2, validator, attachment_type, optional, range_type, calendar_type, dependent;
            placeholder_or_options_elem2 = ""

            label_name = document.getElementById('input_name_' + field_id_num + '_1').value;
            label_name = strip_unwanted_characters(stripHTML(label_name));

            input_type = document.getElementById('input_type_' + field_id_num).value
            // input_type = input_name_mapping(input_type)

            placeholder_or_options_elem1 = document.getElementById('input_selected_type_' + field_id_num + '_3').value;
            validator = document.getElementById('validator_' + field_id_num).value;

            // validator = validator_mapping(validator);

            attachment_type = document.getElementById('file_attach_type_' + field_id_num).value;

            range_type = document.getElementById('range_selector_' + field_id_num).value;

            calendar_type = document.getElementById('calendar_selector_type_' + field_id_num).value;

            optional = document.getElementById('optional-toggle-field-' + field_id_num).checked;

            dependent = document.getElementById('dependent-field-' + field_id_num);

            country_code = $("#phone_number_selector_type_" + field_id_num).intlTelInput("getSelectedCountryData").iso2

            if (dependent) {
                dependent = dependent.checked;
            } else {
                dependent = false;
            }
            let dependent_on = ''
            let dependent_on_label_name = ''
            if (dependent) {
                dependent_on = document.getElementById('dependent_field_dropdown_' + field_id_num).value;
                dependent_on_label_name = document.getElementById('input_name_' + dependent_on + '_1')?.value
            }

            if (dependent_on == 'Select Dependency') {
                M.toast({
                    "html": "Please select a valid dependency"
                }, 2000);
                return;
            }

            let dependent_fields = document.querySelectorAll('.dependent-dropdown');
            let dependent_ids = []
            for (let j = 0; j < dependent_fields.length; j++) {
                if (dependent_fields[j].value == field_id_num) {
                    dependent_ids.push(dependent_fields[j].id.split('_')[3])
                }
            }
            
            dependent_ids = dependent_ids.join('$$$')

            label_name = label_name.trim();
            if (label_name == "") {
                M.toast({
                    "html": "Please enter a valid label name"
                }, 2000);
                return;
            }

            if (input_type == "") {
                M.toast({
                    "html": "Please enter an input type"
                }, 2000);
                return;
            }

            let placeholder_or_options = placeholder_or_options_elem1;

            if (input_type == 'file_attach') {
                placeholder_or_options = attachment_type
            } else {
                if (input_type == "radio") {

                    placeholder_or_options = form_get_radio_button_list(field_id.split("-")[1])
                    placeholder_or_options = placeholder_or_options.join('$$$')

                } else if (input_type == "checkbox") {
                    placeholder_or_options = form_get_check_box_list(field_id.split("-")[1])
                    placeholder_or_options = placeholder_or_options.join('$$$')

                } else if (input_type == "dropdown_list") {
                    placeholder_or_options = form_get_dropdown_list(field_id.split("-")[1])
                    placeholder_or_options = placeholder_or_options.join('$$$')
                } else if (input_type == "range") {
                    var form_range_slider_min_value = document.getElementById("form-range-slider-min-range-" + field_id.split("-")[1]).value;
                    var form_range_slider_max_value = document.getElementById("form-range-slider-max-range-" + field_id.split("-")[1]).value;
                    placeholder_or_options = form_range_slider_min_value + "-" + form_range_slider_max_value;
                }
            }

            if (input_type == "text_field" || input_type == "phone_number") {
                if (placeholder_or_options == "") {
                    M.toast({
                        "html": "Please enter placeholder value"
                    }, 2000);
                    return;
                }
            } else if (!api_integrated_fields.includes(field_id_num) && input_type == "dropdown_list" && placeholder_or_options == "") {
                M.toast({
                    "html": "Please enter at least one and valid dropdown option"
                }, 2000);
                return;
            } else if (!api_integrated_fields.includes(field_id_num) && input_type == "checkbox" && placeholder_or_options == "") {
                M.toast({
                    "html": "Please enter at least one and valid checkbox option"
                }, 2000);
                return;
            } else if (!api_integrated_fields.includes(field_id_num) && input_type == "radio" && placeholder_or_options == "") {
                M.toast({
                    "html": "Please enter at least one and valid radio button option"
                }, 2000);
                return;
            } else if (input_type == "range") {
                if (placeholder_or_options.split('-')[0] == "" || placeholder_or_options.split('-')[1] == "") {
                    M.toast({
                        "html": "Please enter a range"
                    }, 2000);
                    return;
                } else if (placeholder_or_options.split('-').length != 2 || (isNaN(placeholder_or_options.split('-')[0]) || isNaN(placeholder_or_options.split('-')[1]))) {
                    M.toast({
                        "html": "Please enter a valid range"
                    }, 2000);
                    return;
                } else if (parseInt(placeholder_or_options.split('-')[0]) >= parseInt(placeholder_or_options.split('-')[1])) {
                    M.toast({
                        'html': 'Minimum range should be less than maximum.'
                    }, 2000);
                    return;
                }
            } else if (input_type == "file_attach" && (placeholder_or_options == undefined || placeholder_or_options == "")) {
                M.toast({
                    "html": "Please select file type"
                }, 2000);
                return;
            }

            form_fields_list.push({
                label_name: label_name,
                input_type: input_type,
                validator: validator,
                placeholder_or_options: placeholder_or_options,
                optional: optional.toString(),
                range_type: range_type,
                calendar_type: calendar_type,
                field_id_num: field_id_num,
                is_dependent: dependent.toString(),
                dependent_on: dependent_on.toString(),
                dependent_on_label_name: dependent_on_label_name,
                dependent_field_ids: dependent_ids,
                country_code: country_code,
            })
        }

        response_present.push('form');

    } else {
        widget_data_req.is_create_form_allowed = false
    }
    widget_data_field.form_fields_list = form_fields_list    

    //Calendar
    let is_calender_picker_allowed = false
    let is_single_calender_date_picker_allowed = false
    let is_multi_calender_date_picker_allowed = false
    let is_single_calender_time_picker_allowed = false
    let is_multi_calender_time_picker_allowed = false
    let is_calender_date_picker_enabled = document.getElementById('enabledatepicker_switch1').checked
    let is_calender_time_picker_enabled = document.getElementById('enabletimepicker_switch2').checked
    if (selected_widget == "calendar_picker_widget_content") {
        if (!is_calender_date_picker_enabled && !is_calender_time_picker_enabled) {
            M.toast({
                'html': 'Please select atleast one option in calendar picker.'
            }, 2000);
            return;
        }
        is_calender_picker_allowed = true
        if (is_calender_date_picker_enabled) {
            is_single_calender_date_picker_allowed = widget_data_req.is_single_datepicker == "true";
            is_multi_calender_date_picker_allowed = widget_data_req.is_multi_datepicker == "true";
        }
        if (is_calender_time_picker_enabled) {
            is_single_calender_time_picker_allowed = widget_data_req.is_single_timepicker == "true";
            is_multi_calender_time_picker_allowed = widget_data_req.is_multi_timepicker == "true";
        }
    }
        
    else 
        widget_data_req.is_calender = "false"

    if (is_calender_picker_allowed) {

        if (is_calender_date_picker_enabled) {
            if ((!is_single_calender_date_picker_allowed && !is_multi_calender_date_picker_allowed)) {
                M.toast({
                    'html': 'Please select atleast one option in date picker.'
                }, 2000);
                return;
            }
        }

        if (is_calender_time_picker_enabled) {
            if ((!is_single_calender_time_picker_allowed && !is_multi_calender_time_picker_allowed)) {
                M.toast({
                    'html': 'Please select atleast one option in time picker.'
                }, 2000);
                return;
            }
        }

        response_present.push('calendar_picker');
    }

    //Dropdown
    let is_drop_down_allowed = false
    let dropdown_choices_list = []
    if (selected_widget == "dropdown_widget_content") {
        is_drop_down_allowed = true
        dropdown_choices_list = Object.values(widget_data_field.drop_down_choices)
        
        if (dropdown_choices_list.length == 0) {
            M.toast({
                "html": "At least one choice is required."
            }, 2000);
            return;
        }
        response_present.push('drop_down');
    } else {
        widget_data_req.is_drop_down = "false"
    }

    // Video Recorder
    let is_video_recorder_allowed = false
    let is_save_video_attachment_required = false
    if (selected_widget == "video_widget_content") {
        is_video_recorder_allowed = $("#checkbox-intent-video-recorder").prop("checked")
        if (!is_video_recorder_allowed) {
            M.toast({
                "html": "Please Select Video Recorder Allowed"
            }, 2000);
            return;
        }
        is_save_video_attachment_required = widget_data_req.is_save_video_attachment;
        is_save_video_attachment_required = is_save_video_attachment_required ? is_save_video_attachment_required : false
    }
    if (is_video_recorder_allowed) {
        response_present.push('video_record')
    } else {
        widget_data_req.is_video_recorder_allowed = "false"
    }
    
    let json_string = JSON.stringify({
        tree_pk,
        is_attachment_required,
        is_save_attachment_required,
        choosen_file_type,
        is_range_slider_required,
        minimum_range,
        maximum_range,
        range_slider_type,
        is_radio_button_allowed,
        radio_button_choices: radio_choices_list,
        is_check_box_allowed,
        checkbox_choices_list,
        is_phone_widget_enabled,
        country_code,
        is_create_form_allowed,
        form_name,
        form_fields_list,
        is_calender_picker_allowed,
        is_single_calender_date_picker_allowed,
        is_multi_calender_date_picker_allowed,
        is_single_calender_time_picker_allowed,
        is_multi_calender_time_picker_allowed,
        is_date_picker_allowed: false,
        is_time_picker_allowed: false,
        is_single_date_picker_allowed: false,
        is_multi_date_picker_allowed: false,
        is_single_time_picker_allowed: false,
        is_multi_time_picker_allowed: false,
        is_drop_down_allowed,
        dropdown_choices_list,
        is_video_recorder_allowed,
        is_save_video_attachment_required
    });

    json_string = EncryptVariable(json_string);

    $.ajax({
        url: '/chat/save-tree-widget/',
        type: "POST",
        headers: {
            'X-CSRFToken': get_csrf_token(),
        },
        data: {
            json_string: json_string
        },
        dataType: "json",
        async: false,
        success: function (response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response['status'] == 200) {
                if (!selected_widget) {
                    $("#response_widget .edit-intent-details-action-btns-wrapper .edit-intent-details-next-btn").addClass("disable-video-recoder-save-value")
                }
                if (SELECTED_LANGUAGE === "en") {
                    load_order_of_responses(
                        node_intent_data[selected_node],
                        node_intent_data[selected_node].intent_response,
                        node_intent_data[selected_node].intent_response.modes,
                        true
                    )
                    bot_response_preview()
                    bot_preview_section_show()
                }
                M.toast({
                    'html': "tree widget saved successfully!"
                }, 1000);
            } else {
                M.toast({
                    'html': "Unable to save tree widget!"
                }, 2000);
            }
        }
    });
}

function decide_save_widget_response() {
    if (selected_node == 1) {
        save_intent_widget_response()
    } else {
        save_tree_widget_response()
    }
}

function save_tree_settings() {
    let intent_pk = null

    if (window.location.href.indexOf("intent_pk=") != -1) {

        let url_parameters = get_url_vars();
        intent_pk = url_parameters["intent_pk"];
    }

    tree_pk =  node_intent_data[selected_node].tree_pk

    let settings = node_intent_data[selected_node].other_settings

    let validator_id = settings.selected_validator_obj?.processor__pk
    validator_id = validator_id ? validator_id : ""
    let is_child_tree_visible = settings.is_child_tree_visible
    let is_go_back_enabled = settings.is_go_back_enabled
    let child_choices = settings.child_choices_list
    let is_last_tree = settings.is_last_tree
    let disposition_code = settings.disposition_code
    let is_exit_tree = settings.is_exit_tree
    let is_transfer_tree = settings.is_transfer_tree
    let allow_barge = settings.allow_barge
    let is_catalogue_purchased = settings.is_item_purchased
    let is_catalogue_added = node_intent_data[selected_node].intent_response.modes.is_catalogue_added
    is_catalogue_added = is_catalogue_added === "true" ? true : false
    let selected_catalogue_sections = node_intent_data[selected_node].intent_response.modes_param.temp_selected_catalogue_sections;
    node_intent_data[selected_node].intent_response.modes_param.selected_catalogue_sections = selected_catalogue_sections;
    if (!selected_catalogue_sections || !selected_catalogue_sections.length) {
        selected_catalogue_sections = []
    }

    if (is_catalogue_added && (!selected_catalogue_sections || !selected_catalogue_sections.length)) {
        M.toast({
            "html": "Please select atleast one section for WhatsApp Catalogue"
        }, 2000);
        return;
    }
    let is_confirmation_and_reset_enabled = settings.is_confirmation_and_reset_enabled
    let required_analytics_variable = settings.required_analytics_variable

    let is_automate_recursion_enabled = settings.is_automatic_recursion_enabled
    let post_processor_variable = settings.post_processor_variable
    let flow_analytics_variable = settings.flow_analytics_variable
    let category_response_allowed = settings.is_category_response_allowed


    let json_string = JSON.stringify({
        intent_pk,
        tree_pk,
        validator_id,
        is_child_tree_visible,
        is_go_back_enabled,
        child_choices,
        is_last_tree,
        disposition_code,
        is_exit_tree,
        is_transfer_tree,
        allow_barge,
        is_catalogue_added,
        is_automate_recursion_enabled,
        post_processor_variable,
        flow_analytics_variable,
        category_response_allowed,
        is_confirmation_and_reset_enabled,
        required_analytics_variable,
        selected_catalogue_sections,
        is_catalogue_purchased
    })
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: '/chat/save-tree-settings/',
        type: "POST",
        headers: {
            'X-CSRFToken': get_csrf_token(),
        },
        data: {
            json_string: json_string
        },
        dataType: "json",
        async: false,
        success: function (response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response['status'] == 200) {
                M.toast({
                    'html': "Tree settings saved successfully!"
                }, 1000);
                if (response["trigger_flow_change"]) {
                    const tree_structure = fetchIntentTreeStructureByIntentID(intent_pk, SELECTED_LANGUAGE)
                    editor.clear()
                    editor.nodeId = 1
                    node_intent_data = {}
                    build_initial_flow(tree_structure[1], true, null, window.outerWidth / 6)
                    update_flow()
                    update_node_vertical_positions(1)
                }
            } else if (response['status'] == 401) {
                M.toast({
                    'html': "Kindly select all the children in child order"
                }, 4000);
            } else {
                M.toast({
                    'html': "Unable to save the Tree settings!"
                }, 2000);
            }
        }
    });

}

function decide_save_settings() {
    if (selected_node == 1) {
        save_intent_settings()
    } else {
        save_tree_settings()
    }
}

function save_tree_recomm() {
    let tree_pk = node_intent_data[selected_node].tree_pk

    let recommended_intent_list = []
    
    recommended_intent_list = node_intent_data[selected_node].recommeded_intents_dict_list

    let is_recommendation_menu = node_intent_data[selected_node].intent_response.modes.is_recommendation_menu === "true"
    is_recommendation_menu = is_recommendation_menu ? true : false

    let json_string = JSON.stringify({
        tree_pk,
        recommended_intent_list,
        is_recommendation_menu,
    })
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: '/chat/save-tree-recommendation/',
        type: "POST",
        headers: {
            'X-CSRFToken': get_csrf_token(),
        },
        data: {
            json_string: json_string
        },
        dataType: "json",
        async: false,
        success: function (response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response['status'] == 200) {
                M.toast({
                    'html': "Tree quick recommmendations saved successfully!"
                }, 1000);
                load_order_of_responses(
                    node_intent_data[selected_node],
                    node_intent_data[selected_node].intent_response,
                    node_intent_data[selected_node].intent_response.modes,
                    true
                )
                bot_response_preview()
                bot_preview_section_show()
            } else {
                M.toast({
                    'html': "Unable to save the Tree quick recommmendations!"
                }, 2000);
            }
        }
    });

}

function decide_save_recomm() {
    if (selected_node == 1) {
        save_intent_recomm()
    } else {
        save_tree_recomm()
    }
}

function save_tree_order_response() {
    let tree_pk = node_intent_data[selected_node].tree_pk

    let is_custom_order_selected = node_intent_data[selected_node].is_custom_order_selected
    let order_of_response = node_intent_data[selected_node].order_of_response

    let json_string = JSON.stringify({
        tree_pk,
        is_custom_order_selected,
        order_of_response,
    })
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: '/chat/save-tree-order-response/',
        type: "POST",
        headers: {
            'X-CSRFToken': get_csrf_token(),
        },
        data: {
            json_string: json_string
        },
        dataType: "json",
        async: false,
        success: function (response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response['status'] == 200) {
                if (SELECTED_LANGUAGE === "en") {
                    bot_response_preview()
                    bot_preview_section_show()
                }
                M.toast({
                    'html': "Tree order of response saved successfully!"
                }, 1000);
            } else {
                M.toast({
                    'html': "Unable to save the Tree order of response!"
                }, 2000);
            }
        }
    });

}

function decide_save_order_response() {
    if (selected_node == 1) {
        save_intent_order_response()
    } else {
        save_tree_order_response()
    }
}

function save_tree_explanation_flow() {
    let tree_pk = node_intent_data[selected_node].tree_pk

    let explanation = node_intent_data[selected_node].explanation

    let json_string = JSON.stringify({
        tree_pk,
        explanation
    })
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: '/chat/save-tree-conversion-flow-description/',
        type: "POST",
        headers: {
            'X-CSRFToken': get_csrf_token(),
        },
        data: {
            json_string: json_string
        },
        dataType: "json",
        async: false,
        success: function (response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response['status'] == 200) {
                M.toast({
                    'html': "Tree conversion flow description saved successfully!"
                }, 1000);
            } else {
                M.toast({
                    'html': "Unable to save the Tree conversion flow description!"
                }, 2000);
            }
        }
    });

}

function decide_save_tree_explanation_flow() {
    if (selected_node == 1) {
        save_intent_explanation_flow()
    } else {
        save_tree_explanation_flow()
    }
}

function widget_decider(selected_widget) {
    const widget_data_req = node_intent_data[selected_node].intent_response.modes
    const widget_map = {
        "file_attach_widget_content": "is_attachment_required",
        "range_slider_widget_content": "is_range_slider",
        "radio_widget_content": "is_radio_button",
        "checkbox_widget_content": "is_check_box",
        "phone_number_widget_content": "is_phone_widget_enabled",
        "create_form_widget_content": "is_create_form_allowed",
        "calendar_picker_widget_content": "is_calender",
        "dropdown_widget_content": "is_drop_down",
        "video_widget_content": "is_video_recorder_allowed",
    }

    for (const field of Object.values(widget_map)) {
        if (widget_map[selected_widget] === field) {
            widget_data_req[field] = "true" 
            if (field === "is_calender") {
                if ($("#enabledatepicker_switch1")[0].checked) {
                    widget_data_req.is_datepicker = "true"
                }
                if ($("#enabletimepicker_switch2")[0].checked) {
                    widget_data_req.is_timepicker = "true"
                }
                if ($("#custom-date-picker-radio")[0].checked) {
                    widget_data_req.is_multi_datepicker = "true"
                }
                if ($("#custom-time-picker-radio")[0].checked) {
                    widget_data_req.is_multi_timepicker = "true"
                }
                if ($("#single-date-picker-radio")[0].checked) {
                    widget_data_req.is_single_datepicker = "true"
                }
                if ($("#single-time-picker-radio")[0].checked) {
                    widget_data_req.is_single_timepicker = "true"
                }
            }
        } else {
            widget_data_req[field] = "false" 
            if (field === "is_calender") {
                widget_data_req.is_datepicker = "false"
                widget_data_req.is_timepicker = "false"
                widget_data_req.is_multi_datepicker = "false"
                widget_data_req.is_multi_timepicker = "false"
                widget_data_req.is_single_datepicker = "false"
                widget_data_req.is_single_timepicker = "false"
            }
        }
    }
}

function build_preview_text_response(text) {
    let html = ""
    let splitted_text = text.replace(/<p>/g, "").replace(/<\/p>/g, "").split("$$$")

    for (const text of splitted_text) {
        html += `
        <div class="preview-bot-message-wrapper">
            <div class="preview-bot-message-div" style="word-break: break-word; flex-direction: column;">
                <p>
                ${text.replace(/ style=".*?"/g, "").replace(/ style='.*?'/g, "")}
                </p>
            </div>
        </div>
        `
    }
    
    return html
}

function build_preview_table_response(table_matrix) {
    let html = `
    <div class="preview-bot-message-wrapper">
        <table class="table-response-bot-preview-wrapper">
    `
    const rows = table_matrix.length;
    const columns = table_matrix[0].length;
    
    if (columns <= 4 && rows > 0) {
        for (let i = 0; i < rows; i++) {
            // create each row
            html += '<tr>';

            for (let j = 0; j < columns; j++) {
                // create cell
                html += '<td>';
                html += un_entity(table_matrix[i][j]);
                html += '</td>'
            }

            // closing row table
            html += '</tr>\n';

        }
        html += `
        </table>
        </div>
        `
        return html
    }
    return ""
}

function build_preview_image_response(images) {
    let html = `
    <div class="preview-bot-message-wrapper">
        <div class="image-response-bot-preview-wrapper">
            <div class="carousel carousel-slider preview-image-carousel-slider intent-uploaded-div"
                data-indicators="true">
    `
    for (const image of images) {
        html += `
            <div class="carousel-item intent-file-uploaded-div">
                <div class="uploaded-img-div">
                    <img src="${image}" alt="${image.split("/").at(-1)}" onerror="this.onerror=null;this.src='/static/EasyChatApp/img/blocked_image.png';">
                </div>
            </div>
            `
    }

    html += `
    <div class="carousel-slider-arrow">
        <div class="arrow left">
            <a
                class="movePrevCarousel middle-indicator-text waves-effect waves-light content-indicator">
                <i class="material-icons left  middle-indicator-text">chevron_left</i>
            </a>
        </div>

        <div class="arrow right">
            <a
                class=" moveNextCarousel middle-indicator-text waves-effect waves-light content-indicator">
                <i class="material-icons right middle-indicator-text">chevron_right</i>
            </a>
        </div>
    </div>
    </div>
    </div>
    </div>
    `

    if (images.length > 0) {
        return html
    }
    return ""
}

function build_preview_video_response(videos) {
    let html = `
    <div class="preview-bot-message-wrapper">
        <div class="video-response-bot-preview-wrapper">
            <div class="carousel carousel-slider preview-video-carousel-slider intent-uploaded-div"
                data-indicators="true">
    `

    for (const video of videos) {
        let embed_url = getEmbedVideoURL(video);

        html += `
        <div class="carousel-item intent-file-uploaded-div">
            <div class="uploaded-img-div">
        `

        if (embed_url.indexOf("embed") == -1) {
            html += `
            <video width="100%" height="100%" controls>
                <source src="` + embed_url + `" type="video/mp4">
            </video>
            </div>
            </div>
            `;
        } else {
            html += `
            <iframe width="100%" height="100%"
                src="${embed_url}" frameborder="1"
                allowfullscreen>
            </iframe>
            </div>
            </div>
            `
        }
    }

    html += `
    <div class="carousel-slider-arrow">
        <div class="arrow left">
            <a
                class="movePrevCarousel middle-indicator-text waves-effect waves-light content-indicator">
                <i class="material-icons left  middle-indicator-text">chevron_left</i>
            </a>
        </div>

        <div class="arrow right">
            <a
                class=" moveNextCarousel middle-indicator-text waves-effect waves-light content-indicator">
                <i class="material-icons right middle-indicator-text">chevron_right</i>
            </a>
        </div>
    </div>
    </div>
    </div>
    </div>
    `

    if (videos.length > 0) {
        return html
    }
    return ""
}

function build_preview_card_response(cards) {
    let html = `
    <div class="preview-bot-message-wrapper">
        <div class="card-response-bot-preview-wrapper">
            <div class="carousel carousel-slider preview-card-carousel-slider intent-uploaded-div"
            data-indicators="true">
    `

    for (const card of cards) {
        html += `
        <div class="carousel-item intent-file-uploaded-div">
                <img src="${card.img_url}" alt="">
                <div style="display: flex; flex-direction:column; padding:4px 8px;">
                    <div class="card-response-bot-header" title="${card.title}">
                        ${card.title}
                    </div>
                    <div class="card-response-bot-description">
                        ${sanitize_html(card.content)}
                    </div>
                    <div class="content-ellipsis" style="position: relative; top: -10px; color: #CBCACA;"></div>
                </div>
                <a href="${card.link}" target="_blank">
                    <svg width="215" height="45" viewBox="0 0 215 45" fill="none"
                        xmlns="http://www.w3.org/2000/svg">
                        <path
                            d="M0 0H215V37C215 41.4183 211.418 45 207 45H7.99999C3.58172 45 0 41.4183 0 37V0Z"
                            fill="#F8FAFC" />
                        <path
                            d="M63.9219 28V16.7969H65.6484V21.9688H65.75L70.0391 16.7969H72.1641L68.2109 21.4219L72.3203 28H70.2578L67.0625 22.7812L65.6484 24.4297V28H63.9219ZM73.9531 28V19.6328H75.5859V20.75H75.6953C75.8776 20.375 76.1849 20.0599 76.6172 19.8047C77.0495 19.5495 77.5599 19.4219 78.1484 19.4219C79.0807 19.4219 79.8255 19.724 80.3828 20.3281C80.9401 20.9323 81.2188 21.6979 81.2188 22.625V28H79.5391V22.9453C79.5391 22.3672 79.3594 21.8984 79 21.5391C78.6458 21.1745 78.2005 20.9922 77.6641 20.9922C77.0807 20.9922 76.5964 21.1953 76.2109 21.6016C75.8255 22.0026 75.6328 22.5078 75.6328 23.1172V28H73.9531ZM83.0469 23.8203C83.0469 22.9922 83.2344 22.2422 83.6094 21.5703C83.9896 20.8984 84.5182 20.3724 85.1953 19.9922C85.8724 19.612 86.6328 19.4219 87.4766 19.4219C88.3203 19.4219 89.0781 19.6146 89.75 20C90.4271 20.3854 90.9505 20.9141 91.3203 21.5859C91.6953 22.2526 91.8828 22.9974 91.8828 23.8203C91.8828 24.6432 91.6927 25.3906 91.3125 26.0625C90.9375 26.7292 90.4115 27.2552 89.7344 27.6406C89.0573 28.0208 88.2995 28.2109 87.4609 28.2109C86.1797 28.2109 85.1224 27.7969 84.2891 26.9688C83.4609 26.1354 83.0469 25.0859 83.0469 23.8203ZM84.7578 23.8203C84.7578 24.6536 85.0104 25.3411 85.5156 25.8828C86.026 26.4193 86.6745 26.6875 87.4609 26.6875C88.2526 26.6875 88.901 26.4167 89.4062 25.875C89.9167 25.3333 90.1719 24.6484 90.1719 23.8203C90.1719 22.987 89.9167 22.3021 89.4062 21.7656C88.901 21.2292 88.2526 20.9609 87.4609 20.9609C86.6693 20.9609 86.0208 21.2318 85.5156 21.7734C85.0104 22.3099 84.7578 22.9922 84.7578 23.8203ZM92.7266 19.6328H94.5078L96.2188 26.0156H96.3281L98.3281 19.6328H100.102L102.086 26.0156H102.203L103.914 19.6328H105.703L103.227 28H101.211L99.2578 21.7891H99.1641L97.1953 28H95.1953L92.7266 19.6328ZM111.828 28V19.6328H113.461V20.7344H113.57C113.768 20.349 114.068 20.0339 114.469 19.7891C114.87 19.5443 115.354 19.4219 115.922 19.4219C116.51 19.4219 117.023 19.5469 117.461 19.7969C117.898 20.0469 118.24 20.3906 118.484 20.8281H118.594C119.125 19.8906 119.984 19.4219 121.172 19.4219C122.089 19.4219 122.826 19.7109 123.383 20.2891C123.945 20.862 124.227 21.6042 124.227 22.5156V28H122.547V23.0859C122.547 22.4141 122.393 21.8984 122.086 21.5391C121.779 21.1745 121.346 20.9922 120.789 20.9922C120.242 20.9922 119.786 21.1849 119.422 21.5703C119.062 21.9505 118.883 22.4661 118.883 23.1172V28H117.203V22.8984C117.203 22.3203 117.036 21.8594 116.703 21.5156C116.37 21.1667 115.935 20.9922 115.398 20.9922C114.862 20.9922 114.411 21.1875 114.047 21.5781C113.688 21.9635 113.508 22.4609 113.508 23.0703V28H111.828ZM126.047 23.8203C126.047 22.9922 126.234 22.2422 126.609 21.5703C126.99 20.8984 127.518 20.3724 128.195 19.9922C128.872 19.612 129.633 19.4219 130.477 19.4219C131.32 19.4219 132.078 19.6146 132.75 20C133.427 20.3854 133.951 20.9141 134.32 21.5859C134.695 22.2526 134.883 22.9974 134.883 23.8203C134.883 24.6432 134.693 25.3906 134.312 26.0625C133.938 26.7292 133.411 27.2552 132.734 27.6406C132.057 28.0208 131.299 28.2109 130.461 28.2109C129.18 28.2109 128.122 27.7969 127.289 26.9688C126.461 26.1354 126.047 25.0859 126.047 23.8203ZM127.758 23.8203C127.758 24.6536 128.01 25.3411 128.516 25.8828C129.026 26.4193 129.674 26.6875 130.461 26.6875C131.253 26.6875 131.901 26.4167 132.406 25.875C132.917 25.3333 133.172 24.6484 133.172 23.8203C133.172 22.987 132.917 22.3021 132.406 21.7656C131.901 21.2292 131.253 20.9609 130.461 20.9609C129.669 20.9609 129.021 21.2318 128.516 21.7734C128.01 22.3099 127.758 22.9922 127.758 23.8203ZM136.906 28V19.6328H138.523V21.0859H138.633C138.779 20.7005 139.052 20.3594 139.453 20.0625C139.854 19.7656 140.328 19.6172 140.875 19.6172H141.609V21.25H140.828C140.13 21.25 139.581 21.4896 139.18 21.9688C138.784 22.4479 138.586 23.0833 138.586 23.875V28H136.906ZM142.641 23.8438C142.641 22.974 142.823 22.2031 143.188 21.5312C143.552 20.8542 144.049 20.3333 144.68 19.9688C145.315 19.6042 146.029 19.4219 146.82 19.4219C147.456 19.4219 148.034 19.5339 148.555 19.7578C149.076 19.9818 149.505 20.2891 149.844 20.6797C150.188 21.0703 150.451 21.526 150.633 22.0469C150.82 22.5677 150.914 23.1276 150.914 23.7266V24.3516H144.32C144.352 25.0859 144.599 25.6771 145.062 26.125C145.526 26.5729 146.138 26.7969 146.898 26.7969C147.43 26.7969 147.904 26.6771 148.32 26.4375C148.742 26.1979 149.036 25.875 149.203 25.4688H150.836C150.617 26.2917 150.151 26.9557 149.438 27.4609C148.729 27.9609 147.867 28.2109 146.852 28.2109C145.607 28.2109 144.594 27.8021 143.812 26.9844C143.031 26.1615 142.641 25.1146 142.641 23.8438ZM144.352 23.0547H149.25C149.198 22.3672 148.945 21.8255 148.492 21.4297C148.039 21.0286 147.482 20.8281 146.82 20.8281C146.174 20.8281 145.617 21.0365 145.148 21.4531C144.68 21.8698 144.414 22.4036 144.352 23.0547Z"
                            fill="#3884FD" />
                    </svg>
                </a>
        </div>
        `
    }

    html += `
    <div class="carousel-slider-arrow">
        <div class="arrow left">
            <a
                class="movePrevCarousel middle-indicator-text waves-effect waves-light content-indicator">
                <i class="material-icons left  middle-indicator-text">chevron_left</i>
            </a>
        </div>

        <div class="arrow right">
            <a
                class=" moveNextCarousel middle-indicator-text waves-effect waves-light content-indicator">
                <i class="material-icons right middle-indicator-text">chevron_right</i>
            </a>
        </div>
    </div>
    </div>
    </div>
    </div>
    `

    if (cards.length > 0) {
        return html
    }

    return ""
}

function build_preview_calendar_widget_response(widget_data_req) {
    let html = `<div class="preview-user-message-wrapper">`

    if (widget_data_req.is_multi_datepicker === "true" && widget_data_req.is_multi_timepicker === "true") {
        html += `
        <div class="custom-date-time-response-bot-preview-wrapper">
        <svg width="182" height="149" viewBox="0 0 182 149" fill="none" xmlns="http://www.w3.org/2000/svg">
        <g filter="url(#filter0_dd_1693_222562)">
        <rect x="4.97266" y="3.3418" width="171.935" height="137.659" rx="2.37152" fill="white"/>
        <rect x="19.2021" y="15.1992" width="143.477" height="23.4861" rx="3.55728" fill="white"/>
        <path d="M20.4021 30.9424V22.5424H25.1901V23.4304H21.3741V26.3104H24.9381V27.1864H21.3741V30.9424H20.4021ZM26.9392 30.9424V24.7024H27.8752V25.8664H27.9472C28.0512 25.5624 28.2552 25.2944 28.5592 25.0624C28.8632 24.8224 29.2272 24.7024 29.6512 24.7024H30.1792V25.6504H29.6632C29.1112 25.6504 28.6752 25.8464 28.3552 26.2384C28.0432 26.6224 27.8872 27.1184 27.8872 27.7264V30.9424H26.9392ZM36.6807 30.1624C36.0647 30.7864 35.2887 31.0984 34.3527 31.0984C33.4167 31.0984 32.6407 30.7904 32.0247 30.1744C31.4087 29.5504 31.1007 28.7664 31.1007 27.8224C31.1007 26.8784 31.4127 26.0984 32.0367 25.4824C32.6607 24.8584 33.4367 24.5464 34.3647 24.5464C35.3007 24.5464 36.0767 24.8584 36.6927 25.4824C37.3087 26.1064 37.6167 26.8864 37.6167 27.8224C37.6167 28.7584 37.3047 29.5384 36.6807 30.1624ZM34.3527 30.2344C35.0247 30.2344 35.5727 30.0064 35.9967 29.5504C36.4287 29.0944 36.6447 28.5184 36.6447 27.8224C36.6447 27.1264 36.4287 26.5504 35.9967 26.0944C35.5727 25.6384 35.0247 25.4104 34.3527 25.4104C33.6887 25.4104 33.1407 25.6424 32.7087 26.1064C32.2847 26.5624 32.0727 27.1344 32.0727 27.8224C32.0727 28.5264 32.2847 29.1064 32.7087 29.5624C33.1407 30.0104 33.6887 30.2344 34.3527 30.2344ZM39.3628 30.9424V24.7024H40.3108V25.6024H40.3828C40.7508 24.8984 41.3588 24.5464 42.2068 24.5464C42.6628 24.5464 43.0588 24.6504 43.3948 24.8584C43.7388 25.0584 43.9988 25.3344 44.1748 25.6864H44.2588C44.6588 24.9264 45.3188 24.5464 46.2388 24.5464C46.9268 24.5464 47.4788 24.7664 47.8948 25.2064C48.3188 25.6464 48.5308 26.2104 48.5308 26.8984V30.9424H47.5828V27.2104C47.5828 26.6344 47.4468 26.1944 47.1748 25.8904C46.9108 25.5864 46.5428 25.4344 46.0708 25.4344C45.6068 25.4344 45.2148 25.5944 44.8948 25.9144C44.5828 26.2264 44.4268 26.6624 44.4268 27.2224V30.9424H43.4788V27.0304C43.4788 26.5424 43.3308 26.1544 43.0348 25.8664C42.7468 25.5784 42.3788 25.4344 41.9308 25.4344C41.4828 25.4344 41.0988 25.5984 40.7788 25.9264C40.4668 26.2544 40.3108 26.6744 40.3108 27.1864V30.9424H39.3628Z" fill="black"/>
        <rect x="13.2691" y="38.982" width="74.1138" height="23.4071" rx="3.26084" fill="white"/>
        <path d="M20.0262 54.1855V45.7855H24.8142V46.6735H20.9982V49.5535H24.5622V50.4295H20.9982V54.1855H20.0262ZM26.5633 54.1855V47.9455H27.4993V49.1095H27.5713C27.6753 48.8055 27.8793 48.5375 28.1833 48.3055C28.4873 48.0655 28.8513 47.9455 29.2753 47.9455H29.8033V48.8935H29.2873C28.7353 48.8935 28.2993 49.0895 27.9793 49.4815C27.6673 49.8655 27.5113 50.3615 27.5113 50.9695V54.1855H26.5633ZM36.3047 53.4055C35.6887 54.0295 34.9127 54.3415 33.9767 54.3415C33.0407 54.3415 32.2647 54.0335 31.6487 53.4175C31.0327 52.7935 30.7247 52.0095 30.7247 51.0655C30.7247 50.1215 31.0367 49.3415 31.6607 48.7255C32.2847 48.1015 33.0607 47.7895 33.9887 47.7895C34.9247 47.7895 35.7007 48.1015 36.3167 48.7255C36.9327 49.3495 37.2407 50.1295 37.2407 51.0655C37.2407 52.0015 36.9287 52.7815 36.3047 53.4055ZM33.9767 53.4775C34.6487 53.4775 35.1967 53.2495 35.6207 52.7935C36.0527 52.3375 36.2687 51.7615 36.2687 51.0655C36.2687 50.3695 36.0527 49.7935 35.6207 49.3375C35.1967 48.8815 34.6487 48.6535 33.9767 48.6535C33.3127 48.6535 32.7647 48.8855 32.3327 49.3495C31.9087 49.8055 31.6967 50.3775 31.6967 51.0655C31.6967 51.7695 31.9087 52.3495 32.3327 52.8055C32.7647 53.2535 33.3127 53.4775 33.9767 53.4775ZM38.9868 54.1855V47.9455H39.9348V48.8455H40.0068C40.3748 48.1415 40.9828 47.7895 41.8308 47.7895C42.2868 47.7895 42.6828 47.8935 43.0188 48.1015C43.3628 48.3015 43.6228 48.5775 43.7988 48.9295H43.8828C44.2828 48.1695 44.9428 47.7895 45.8628 47.7895C46.5508 47.7895 47.1028 48.0095 47.5188 48.4495C47.9428 48.8895 48.1548 49.4535 48.1548 50.1415V54.1855H47.2068V50.4535C47.2068 49.8775 47.0708 49.4375 46.7988 49.1335C46.5348 48.8295 46.1668 48.6775 45.6948 48.6775C45.2308 48.6775 44.8388 48.8375 44.5188 49.1575C44.2068 49.4695 44.0508 49.9055 44.0508 50.4655V54.1855H43.1028V50.2735C43.1028 49.7855 42.9548 49.3975 42.6588 49.1095C42.3708 48.8215 42.0028 48.6775 41.5548 48.6775C41.1068 48.6775 40.7228 48.8415 40.4028 49.1695C40.0908 49.4975 39.9348 49.9175 39.9348 50.4295V54.1855H38.9868ZM53.8155 54.1855V45.7855H56.3115C57.6155 45.7855 58.6435 46.1735 59.3955 46.9495C60.1475 47.7255 60.5235 48.7375 60.5235 49.9855C60.5235 51.2975 60.1515 52.3255 59.4075 53.0695C58.6715 53.8135 57.6395 54.1855 56.3115 54.1855H53.8155ZM54.7875 53.3215H56.3115C57.3115 53.3215 58.0955 53.0295 58.6635 52.4455C59.2395 51.8535 59.5275 51.0335 59.5275 49.9855C59.5275 48.9615 59.2395 48.1535 58.6635 47.5615C58.0955 46.9615 57.3115 46.6615 56.3115 46.6615H54.7875V53.3215ZM64.9025 54.3415C63.9905 54.3415 63.2425 54.0375 62.6585 53.4295C62.0825 52.8215 61.7945 52.0375 61.7945 51.0775C61.7945 50.1175 62.0785 49.3295 62.6465 48.7135C63.2225 48.0975 63.9505 47.7895 64.8305 47.7895C65.3985 47.7895 65.8665 47.9175 66.2345 48.1735C66.6105 48.4295 66.8745 48.6895 67.0265 48.9535H67.0985V47.9455H68.0465V54.1855H67.1345V53.2015H67.0625C66.5425 53.9615 65.8225 54.3415 64.9025 54.3415ZM63.3665 52.8295C63.7745 53.2695 64.3065 53.4895 64.9625 53.4895C65.6185 53.4895 66.1425 53.2575 66.5345 52.7935C66.9345 52.3295 67.1345 51.7575 67.1345 51.0775C67.1345 50.3255 66.9265 49.7335 66.5105 49.3015C66.1025 48.8695 65.5785 48.6535 64.9385 48.6535C64.2985 48.6535 63.7745 48.8815 63.3665 49.3375C62.9665 49.7855 62.7665 50.3655 62.7665 51.0775C62.7665 51.8055 62.9665 52.3895 63.3665 52.8295ZM72.598 54.1855C72.014 54.1855 71.558 54.0255 71.23 53.7055C70.902 53.3855 70.738 52.9175 70.738 52.3015V48.7495H69.562V47.9455H70.498C70.698 47.9455 70.798 47.8415 70.798 47.6335V46.1335H71.686V47.9455H73.606V48.7495H71.686V52.2895C71.686 53.0015 72.01 53.3575 72.658 53.3575H73.522V54.1855H72.598ZM77.9942 54.3415C77.0582 54.3415 76.3022 54.0335 75.7262 53.4175C75.1582 52.8015 74.8742 52.0175 74.8742 51.0655C74.8742 50.0895 75.1662 49.3015 75.7502 48.7015C76.3342 48.0935 77.0622 47.7895 77.9342 47.7895C78.8622 47.7895 79.5982 48.0895 80.1422 48.6895C80.6862 49.2895 80.9582 50.0535 80.9582 50.9815V51.4015H75.8702C75.8942 52.0335 76.0942 52.5375 76.4702 52.9135C76.8542 53.2895 77.3662 53.4775 78.0062 53.4775C78.4382 53.4775 78.8302 53.3775 79.1822 53.1775C79.5342 52.9775 79.7782 52.7015 79.9142 52.3495H80.8982C80.7222 52.9415 80.3742 53.4215 79.8542 53.7895C79.3342 54.1575 78.7142 54.3415 77.9942 54.3415ZM75.8942 50.5615H79.9502C79.9102 49.9615 79.7022 49.4935 79.3262 49.1575C78.9502 48.8215 78.4862 48.6535 77.9342 48.6535C77.3982 48.6535 76.9342 48.8295 76.5422 49.1815C76.1582 49.5335 75.9422 49.9935 75.8942 50.5615Z" fill="#2755CB"/>
        <rect x="13.2691" y="38.982" width="74.1138" height="23.4071" rx="3.26084" stroke="#2755CB" stroke-width="0.592879"/>
        <rect x="94.4976" y="38.982" width="74.1138" height="23.4071" rx="3.26084" fill="white"/>
        <path d="M101.255 54.1855V45.7855H106.043V46.6735H102.227V49.5535H105.791V50.4295H102.227V54.1855H101.255ZM107.792 54.1855V47.9455H108.728V49.1095H108.8C108.904 48.8055 109.108 48.5375 109.412 48.3055C109.716 48.0655 110.08 47.9455 110.504 47.9455H111.032V48.8935H110.516C109.964 48.8935 109.528 49.0895 109.208 49.4815C108.896 49.8655 108.74 50.3615 108.74 50.9695V54.1855H107.792ZM117.533 53.4055C116.917 54.0295 116.141 54.3415 115.205 54.3415C114.269 54.3415 113.493 54.0335 112.877 53.4175C112.261 52.7935 111.953 52.0095 111.953 51.0655C111.953 50.1215 112.265 49.3415 112.889 48.7255C113.513 48.1015 114.289 47.7895 115.217 47.7895C116.153 47.7895 116.929 48.1015 117.545 48.7255C118.161 49.3495 118.469 50.1295 118.469 51.0655C118.469 52.0015 118.157 52.7815 117.533 53.4055ZM115.205 53.4775C115.877 53.4775 116.425 53.2495 116.849 52.7935C117.281 52.3375 117.497 51.7615 117.497 51.0655C117.497 50.3695 117.281 49.7935 116.849 49.3375C116.425 48.8815 115.877 48.6535 115.205 48.6535C114.541 48.6535 113.993 48.8855 113.561 49.3495C113.137 49.8055 112.925 50.3775 112.925 51.0655C112.925 51.7695 113.137 52.3495 113.561 52.8055C113.993 53.2535 114.541 53.4775 115.205 53.4775ZM120.215 54.1855V47.9455H121.163V48.8455H121.235C121.603 48.1415 122.211 47.7895 123.059 47.7895C123.515 47.7895 123.911 47.8935 124.247 48.1015C124.591 48.3015 124.851 48.5775 125.027 48.9295H125.111C125.511 48.1695 126.171 47.7895 127.091 47.7895C127.779 47.7895 128.331 48.0095 128.747 48.4495C129.171 48.8895 129.383 49.4535 129.383 50.1415V54.1855H128.435V50.4535C128.435 49.8775 128.299 49.4375 128.027 49.1335C127.763 48.8295 127.395 48.6775 126.923 48.6775C126.459 48.6775 126.067 48.8375 125.747 49.1575C125.435 49.4695 125.279 49.9055 125.279 50.4655V54.1855H124.331V50.2735C124.331 49.7855 124.183 49.3975 123.887 49.1095C123.599 48.8215 123.231 48.6775 122.783 48.6775C122.335 48.6775 121.951 48.8415 121.631 49.1695C121.319 49.4975 121.163 49.9175 121.163 50.4295V54.1855H120.215ZM136.772 54.1855V46.6735H134.204V45.7855H140.312V46.6735H137.744V54.1855H136.772ZM142.811 46.6255C142.683 46.7535 142.519 46.8175 142.319 46.8175C142.119 46.8175 141.955 46.7535 141.827 46.6255C141.699 46.4895 141.635 46.3215 141.635 46.1215C141.635 45.9295 141.699 45.7695 141.827 45.6415C141.955 45.5055 142.119 45.4375 142.319 45.4375C142.519 45.4375 142.683 45.5055 142.811 45.6415C142.947 45.7695 143.015 45.9295 143.015 46.1215C143.015 46.3215 142.947 46.4895 142.811 46.6255ZM141.827 54.1855V47.9455H142.775V54.1855H141.827ZM144.887 54.1855V47.9455H145.835V48.8455H145.907C146.275 48.1415 146.883 47.7895 147.731 47.7895C148.187 47.7895 148.583 47.8935 148.919 48.1015C149.263 48.3015 149.523 48.5775 149.699 48.9295H149.783C150.183 48.1695 150.843 47.7895 151.763 47.7895C152.451 47.7895 153.003 48.0095 153.419 48.4495C153.843 48.8895 154.055 49.4535 154.055 50.1415V54.1855H153.107V50.4535C153.107 49.8775 152.971 49.4375 152.699 49.1335C152.435 48.8295 152.067 48.6775 151.595 48.6775C151.131 48.6775 150.739 48.8375 150.419 49.1575C150.107 49.4695 149.951 49.9055 149.951 50.4655V54.1855H149.003V50.2735C149.003 49.7855 148.855 49.3975 148.559 49.1095C148.271 48.8215 147.903 48.6775 147.455 48.6775C147.007 48.6775 146.623 48.8415 146.303 49.1695C145.991 49.4975 145.835 49.9175 145.835 50.4295V54.1855H144.887ZM158.801 54.3415C157.865 54.3415 157.109 54.0335 156.533 53.4175C155.965 52.8015 155.681 52.0175 155.681 51.0655C155.681 50.0895 155.973 49.3015 156.557 48.7015C157.141 48.0935 157.869 47.7895 158.741 47.7895C159.669 47.7895 160.405 48.0895 160.949 48.6895C161.493 49.2895 161.765 50.0535 161.765 50.9815V51.4015H156.677C156.701 52.0335 156.901 52.5375 157.277 52.9135C157.661 53.2895 158.173 53.4775 158.813 53.4775C159.245 53.4775 159.637 53.3775 159.989 53.1775C160.341 52.9775 160.585 52.7015 160.721 52.3495H161.705C161.529 52.9415 161.181 53.4215 160.661 53.7895C160.141 54.1575 159.521 54.3415 158.801 54.3415ZM156.701 50.5615H160.757C160.717 49.9615 160.509 49.4935 160.133 49.1575C159.757 48.8215 159.293 48.6535 158.741 48.6535C158.205 48.6535 157.741 48.8295 157.349 49.1815C156.965 49.5335 156.749 49.9935 156.701 50.5615Z" fill="#2755CB"/>
        <rect x="94.4976" y="38.982" width="74.1138" height="23.4071" rx="3.26084" stroke="#2755CB" stroke-width="0.592879"/>
        <line x1="4.97266" y1="74.2465" x2="176.973" y2="74.2465" stroke="#DADADA" stroke-width="0.592879"/>
        <rect x="19.2021" y="86.4004" width="143.477" height="18.743" rx="3.55728" fill="white"/>
        <path d="M22.1301 97.7715V90.2595H19.5621V89.3715H25.6701V90.2595H23.1021V97.7715H22.1301ZM31.2072 96.9915C30.5912 97.6155 29.8152 97.9275 28.8792 97.9275C27.9432 97.9275 27.1672 97.6195 26.5512 97.0035C25.9352 96.3795 25.6272 95.5955 25.6272 94.6515C25.6272 93.7075 25.9392 92.9275 26.5632 92.3115C27.1872 91.6875 27.9632 91.3755 28.8912 91.3755C29.8272 91.3755 30.6032 91.6875 31.2192 92.3115C31.8352 92.9355 32.1432 93.7155 32.1432 94.6515C32.1432 95.5875 31.8312 96.3675 31.2072 96.9915ZM28.8792 97.0635C29.5512 97.0635 30.0992 96.8355 30.5232 96.3795C30.9552 95.9235 31.1712 95.3475 31.1712 94.6515C31.1712 93.9555 30.9552 93.3795 30.5232 92.9235C30.0992 92.4675 29.5512 92.2395 28.8792 92.2395C28.2152 92.2395 27.6672 92.4715 27.2352 92.9355C26.8112 93.3915 26.5992 93.9635 26.5992 94.6515C26.5992 95.3555 26.8112 95.9355 27.2352 96.3915C27.6672 96.8395 28.2152 97.0635 28.8792 97.0635Z" fill="black"/>
        <rect x="13.2691" y="105.439" width="74.1138" height="23.4071" rx="3.26084" fill="white"/>
        <path d="M29.7542 120.643V113.131H27.1862V112.243H33.2942V113.131H30.7262V120.643H29.7542ZM38.8312 119.863C38.2152 120.487 37.4392 120.799 36.5032 120.799C35.5672 120.799 34.7912 120.491 34.1752 119.875C33.5592 119.251 33.2512 118.467 33.2512 117.523C33.2512 116.579 33.5632 115.799 34.1872 115.183C34.8112 114.559 35.5872 114.247 36.5152 114.247C37.4512 114.247 38.2272 114.559 38.8432 115.183C39.4592 115.807 39.7672 116.587 39.7672 117.523C39.7672 118.459 39.4552 119.239 38.8312 119.863ZM36.5032 119.935C37.1752 119.935 37.7232 119.707 38.1472 119.251C38.5792 118.795 38.7952 118.219 38.7952 117.523C38.7952 116.827 38.5792 116.251 38.1472 115.795C37.7232 115.339 37.1752 115.111 36.5032 115.111C35.8392 115.111 35.2912 115.343 34.8592 115.807C34.4352 116.263 34.2232 116.835 34.2232 117.523C34.2232 118.227 34.4352 118.807 34.8592 119.263C35.2912 119.711 35.8392 119.935 36.5032 119.935ZM45.0677 120.643V112.243H47.5637C48.8677 112.243 49.8957 112.631 50.6477 113.407C51.3997 114.183 51.7757 115.195 51.7757 116.443C51.7757 117.755 51.4037 118.783 50.6597 119.527C49.9237 120.271 48.8917 120.643 47.5637 120.643H45.0677ZM46.0397 119.779H47.5637C48.5637 119.779 49.3477 119.487 49.9157 118.903C50.4917 118.311 50.7797 117.491 50.7797 116.443C50.7797 115.419 50.4917 114.611 49.9157 114.019C49.3477 113.419 48.5637 113.119 47.5637 113.119H46.0397V119.779ZM56.1547 120.799C55.2427 120.799 54.4947 120.495 53.9107 119.887C53.3347 119.279 53.0467 118.495 53.0467 117.535C53.0467 116.575 53.3307 115.787 53.8987 115.171C54.4747 114.555 55.2027 114.247 56.0827 114.247C56.6507 114.247 57.1187 114.375 57.4867 114.631C57.8627 114.887 58.1267 115.147 58.2787 115.411H58.3507V114.403H59.2987V120.643H58.3867V119.659H58.3147C57.7947 120.419 57.0747 120.799 56.1547 120.799ZM54.6187 119.287C55.0267 119.727 55.5587 119.947 56.2147 119.947C56.8707 119.947 57.3947 119.715 57.7867 119.251C58.1867 118.787 58.3867 118.215 58.3867 117.535C58.3867 116.783 58.1787 116.191 57.7627 115.759C57.3547 115.327 56.8307 115.111 56.1907 115.111C55.5507 115.111 55.0267 115.339 54.6187 115.795C54.2187 116.243 54.0187 116.823 54.0187 117.535C54.0187 118.263 54.2187 118.847 54.6187 119.287ZM63.8502 120.643C63.2662 120.643 62.8102 120.483 62.4822 120.163C62.1542 119.843 61.9902 119.375 61.9902 118.759V115.207H60.8142V114.403H61.7502C61.9502 114.403 62.0502 114.299 62.0502 114.091V112.591H62.9382V114.403H64.8582V115.207H62.9382V118.747C62.9382 119.459 63.2622 119.815 63.9102 119.815H64.7742V120.643H63.8502ZM69.2465 120.799C68.3105 120.799 67.5545 120.491 66.9785 119.875C66.4105 119.259 66.1265 118.475 66.1265 117.523C66.1265 116.547 66.4185 115.759 67.0025 115.159C67.5865 114.551 68.3145 114.247 69.1865 114.247C70.1145 114.247 70.8505 114.547 71.3945 115.147C71.9385 115.747 72.2105 116.511 72.2105 117.439V117.859H67.1225C67.1465 118.491 67.3465 118.995 67.7225 119.371C68.1065 119.747 68.6185 119.935 69.2585 119.935C69.6905 119.935 70.0825 119.835 70.4345 119.635C70.7865 119.435 71.0305 119.159 71.1665 118.807H72.1505C71.9745 119.399 71.6265 119.879 71.1065 120.247C70.5865 120.615 69.9665 120.799 69.2465 120.799ZM67.1465 117.019H71.2025C71.1625 116.419 70.9545 115.951 70.5785 115.615C70.2025 115.279 69.7385 115.111 69.1865 115.111C68.6505 115.111 68.1865 115.287 67.7945 115.639C67.4105 115.991 67.1945 116.451 67.1465 117.019Z" fill="#2755CB"/>
        <rect x="13.2691" y="105.439" width="74.1138" height="23.4071" rx="3.26084" stroke="#2755CB" stroke-width="0.592879"/>
        <rect x="94.4976" y="105.439" width="74.1138" height="23.4071" rx="3.26084" fill="white"/>
        <path d="M111.483 120.643V113.131H108.915V112.243H115.023V113.131H112.455V120.643H111.483ZM120.56 119.863C119.944 120.487 119.168 120.799 118.232 120.799C117.296 120.799 116.52 120.491 115.904 119.875C115.288 119.251 114.98 118.467 114.98 117.523C114.98 116.579 115.292 115.799 115.916 115.183C116.54 114.559 117.316 114.247 118.244 114.247C119.18 114.247 119.956 114.559 120.572 115.183C121.188 115.807 121.496 116.587 121.496 117.523C121.496 118.459 121.184 119.239 120.56 119.863ZM118.232 119.935C118.904 119.935 119.452 119.707 119.876 119.251C120.308 118.795 120.524 118.219 120.524 117.523C120.524 116.827 120.308 116.251 119.876 115.795C119.452 115.339 118.904 115.111 118.232 115.111C117.568 115.111 117.02 115.343 116.588 115.807C116.164 116.263 115.952 116.835 115.952 117.523C115.952 118.227 116.164 118.807 116.588 119.263C117.02 119.711 117.568 119.935 118.232 119.935ZM128.524 120.643V113.131H125.956V112.243H132.064V113.131H129.496V120.643H128.524ZM134.563 113.083C134.435 113.211 134.271 113.275 134.071 113.275C133.871 113.275 133.707 113.211 133.579 113.083C133.451 112.947 133.387 112.779 133.387 112.579C133.387 112.387 133.451 112.227 133.579 112.099C133.707 111.963 133.871 111.895 134.071 111.895C134.271 111.895 134.435 111.963 134.563 112.099C134.699 112.227 134.767 112.387 134.767 112.579C134.767 112.779 134.699 112.947 134.563 113.083ZM133.579 120.643V114.403H134.527V120.643H133.579ZM136.639 120.643V114.403H137.587V115.303H137.659C138.027 114.599 138.635 114.247 139.483 114.247C139.939 114.247 140.335 114.351 140.671 114.559C141.015 114.759 141.275 115.035 141.451 115.387H141.535C141.935 114.627 142.595 114.247 143.515 114.247C144.203 114.247 144.755 114.467 145.171 114.907C145.595 115.347 145.807 115.911 145.807 116.599V120.643H144.859V116.911C144.859 116.335 144.723 115.895 144.451 115.591C144.187 115.287 143.819 115.135 143.347 115.135C142.883 115.135 142.491 115.295 142.171 115.615C141.859 115.927 141.703 116.363 141.703 116.923V120.643H140.755V116.731C140.755 116.243 140.607 115.855 140.311 115.567C140.023 115.279 139.655 115.135 139.207 115.135C138.759 115.135 138.375 115.299 138.055 115.627C137.743 115.955 137.587 116.375 137.587 116.887V120.643H136.639ZM150.553 120.799C149.617 120.799 148.861 120.491 148.285 119.875C147.717 119.259 147.433 118.475 147.433 117.523C147.433 116.547 147.725 115.759 148.309 115.159C148.893 114.551 149.621 114.247 150.493 114.247C151.421 114.247 152.157 114.547 152.701 115.147C153.245 115.747 153.517 116.511 153.517 117.439V117.859H148.429C148.453 118.491 148.653 118.995 149.029 119.371C149.413 119.747 149.925 119.935 150.565 119.935C150.997 119.935 151.389 119.835 151.741 119.635C152.093 119.435 152.337 119.159 152.473 118.807H153.457C153.281 119.399 152.933 119.879 152.413 120.247C151.893 120.615 151.273 120.799 150.553 120.799ZM148.453 117.019H152.509C152.469 116.419 152.261 115.951 151.885 115.615C151.509 115.279 151.045 115.111 150.493 115.111C149.957 115.111 149.493 115.287 149.101 115.639C148.717 115.991 148.501 116.451 148.453 117.019Z" fill="#2755CB"/>
        <rect x="94.4976" y="105.439" width="74.1138" height="23.4071" rx="3.26084" stroke="#2755CB" stroke-width="0.592879"/>
        <rect x="5.2691" y="3.63824" width="171.342" height="137.067" rx="2.07508" stroke="#FAFAFA" stroke-width="0.592879"/>
        </g>
        <defs>
        <filter id="filter0_dd_1693_222562" x="0.229622" y="0.97028" width="181.486" height="147.146" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
        <feFlood flood-opacity="0" result="BackgroundImageFix"/>
        <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
        <feOffset dy="2.37152"/>
        <feGaussianBlur stdDeviation="2.37152"/>
        <feColorMatrix type="matrix" values="0 0 0 0 0.196487 0 0 0 0 0.196487 0 0 0 0 0.279476 0 0 0 0.06 0"/>
        <feBlend mode="multiply" in2="BackgroundImageFix" result="effect1_dropShadow_1693_222562"/>
        <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
        <feOffset dy="2.37152"/>
        <feGaussianBlur stdDeviation="1.18576"/>
        <feColorMatrix type="matrix" values="0 0 0 0 0.196487 0 0 0 0 0.196487 0 0 0 0 0.279476 0 0 0 0.08 0"/>
        <feBlend mode="multiply" in2="effect1_dropShadow_1693_222562" result="effect2_dropShadow_1693_222562"/>
        <feBlend mode="normal" in="SourceGraphic" in2="effect2_dropShadow_1693_222562" result="shape"/>
        </filter>
        </defs>
        </svg>
        </div>
        </div>
        `
    } else if (widget_data_req.is_multi_datepicker === "true" && widget_data_req.is_single_timepicker === "true") {
        html += `
        <div class="custom-date-single-time-response-bot-preview-wrapper">
        <svg width="182" height="91" viewBox="0 0 182 91" fill="none" xmlns="http://www.w3.org/2000/svg">
        <g filter="url(#filter0_dd_1693_222539)">
        <rect x="4.97266" y="2.68164" width="171.935" height="81.2012" rx="2.37152" fill="white"/>
        <rect x="13.2691" y="14.8355" width="74.1138" height="23.4071" rx="3.26084" fill="white"/>
        <path d="M20.0262 30.0391V21.6391H24.8142V22.5271H20.9982V25.4071H24.5622V26.2831H20.9982V30.0391H20.0262ZM26.4921 30.0391V23.7991H27.4281V24.9631H27.5001C27.6041 24.6591 27.8081 24.3911 28.1121 24.1591C28.4161 23.9191 28.7801 23.7991 29.2041 23.7991H29.7321V24.7471H29.2161C28.6641 24.7471 28.2281 24.9431 27.9081 25.3351C27.5961 25.7191 27.4401 26.2151 27.4401 26.8231V30.0391H26.4921ZM36.1624 29.2591C35.5464 29.8831 34.7704 30.1951 33.8344 30.1951C32.8984 30.1951 32.1224 29.8871 31.5064 29.2711C30.8904 28.6471 30.5824 27.8631 30.5824 26.9191C30.5824 25.9751 30.8944 25.1951 31.5184 24.5791C32.1424 23.9551 32.9184 23.6431 33.8464 23.6431C34.7824 23.6431 35.5584 23.9551 36.1744 24.5791C36.7904 25.2031 37.0984 25.9831 37.0984 26.9191C37.0984 27.8551 36.7864 28.6351 36.1624 29.2591ZM33.8344 29.3311C34.5064 29.3311 35.0544 29.1031 35.4784 28.6471C35.9104 28.1911 36.1264 27.6151 36.1264 26.9191C36.1264 26.2231 35.9104 25.6471 35.4784 25.1911C35.0544 24.7351 34.5064 24.5071 33.8344 24.5071C33.1704 24.5071 32.6224 24.7391 32.1904 25.2031C31.7664 25.6591 31.5544 26.2311 31.5544 26.9191C31.5544 27.6231 31.7664 28.2031 32.1904 28.6591C32.6224 29.1071 33.1704 29.3311 33.8344 29.3311ZM38.7734 30.0391V23.7991H39.7214V24.6991H39.7934C40.1614 23.9951 40.7694 23.6431 41.6174 23.6431C42.0734 23.6431 42.4694 23.7471 42.8054 23.9551C43.1494 24.1551 43.4094 24.4311 43.5854 24.7831H43.6694C44.0694 24.0231 44.7294 23.6431 45.6494 23.6431C46.3374 23.6431 46.8894 23.8631 47.3054 24.3031C47.7294 24.7431 47.9414 25.3071 47.9414 25.9951V30.0391H46.9934V26.3071C46.9934 25.7311 46.8574 25.2911 46.5854 24.9871C46.3214 24.6831 45.9534 24.5311 45.4814 24.5311C45.0174 24.5311 44.6254 24.6911 44.3054 25.0111C43.9934 25.3231 43.8374 25.7591 43.8374 26.3191V30.0391H42.8894V26.1271C42.8894 25.6391 42.7414 25.2511 42.4454 24.9631C42.1574 24.6751 41.7894 24.5311 41.3414 24.5311C40.8934 24.5311 40.5094 24.6951 40.1894 25.0231C39.8774 25.3511 39.7214 25.7711 39.7214 26.2831V30.0391H38.7734ZM53.4598 30.0391V21.6391H55.9558C57.2598 21.6391 58.2878 22.0271 59.0398 22.8031C59.7918 23.5791 60.1678 24.5911 60.1678 25.8391C60.1678 27.1511 59.7958 28.1791 59.0518 28.9231C58.3158 29.6671 57.2838 30.0391 55.9558 30.0391H53.4598ZM54.4318 29.1751H55.9558C56.9558 29.1751 57.7398 28.8831 58.3078 28.2991C58.8838 27.7071 59.1718 26.8871 59.1718 25.8391C59.1718 24.8151 58.8838 24.0071 58.3078 23.4151C57.7398 22.8151 56.9558 22.5151 55.9558 22.5151H54.4318V29.1751ZM64.4756 30.1951C63.5636 30.1951 62.8156 29.8911 62.2316 29.2831C61.6556 28.6751 61.3676 27.8911 61.3676 26.9311C61.3676 25.9711 61.6516 25.1831 62.2196 24.5671C62.7956 23.9511 63.5236 23.6431 64.4036 23.6431C64.9716 23.6431 65.4396 23.7711 65.8076 24.0271C66.1836 24.2831 66.4476 24.5431 66.5996 24.8071H66.6716V23.7991H67.6196V30.0391H66.7076V29.0551H66.6356C66.1156 29.8151 65.3956 30.1951 64.4756 30.1951ZM62.9396 28.6831C63.3476 29.1231 63.8796 29.3431 64.5356 29.3431C65.1916 29.3431 65.7156 29.1111 66.1076 28.6471C66.5076 28.1831 66.7076 27.6111 66.7076 26.9311C66.7076 26.1791 66.4996 25.5871 66.0836 25.1551C65.6756 24.7231 65.1516 24.5071 64.5116 24.5071C63.8716 24.5071 63.3476 24.7351 62.9396 25.1911C62.5396 25.6391 62.3396 26.2191 62.3396 26.9311C62.3396 27.6591 62.5396 28.2431 62.9396 28.6831ZM72.1 30.0391C71.516 30.0391 71.06 29.8791 70.732 29.5591C70.404 29.2391 70.24 28.7711 70.24 28.1551V24.6031H69.064V23.7991H70C70.2 23.7991 70.3 23.6951 70.3 23.4871V21.9871H71.188V23.7991H73.108V24.6031H71.188V28.1431C71.188 28.8551 71.512 29.2111 72.16 29.2111H73.024V30.0391H72.1ZM77.4251 30.1951C76.4891 30.1951 75.7331 29.8871 75.1571 29.2711C74.5891 28.6551 74.3051 27.8711 74.3051 26.9191C74.3051 25.9431 74.5971 25.1551 75.1811 24.5551C75.7651 23.9471 76.4931 23.6431 77.3651 23.6431C78.2931 23.6431 79.0291 23.9431 79.5731 24.5431C80.1171 25.1431 80.3891 25.9071 80.3891 26.8351V27.2551H75.3011C75.3251 27.8871 75.5251 28.3911 75.9011 28.7671C76.2851 29.1431 76.7971 29.3311 77.4371 29.3311C77.8691 29.3311 78.2611 29.2311 78.6131 29.0311C78.9651 28.8311 79.2091 28.5551 79.3451 28.2031H80.3291C80.1531 28.7951 79.8051 29.2751 79.2851 29.6431C78.7651 30.0111 78.1451 30.1951 77.4251 30.1951ZM75.3251 26.4151H79.3811C79.3411 25.8151 79.1331 25.3471 78.7571 25.0111C78.3811 24.6751 77.9171 24.5071 77.3651 24.5071C76.8291 24.5071 76.3651 24.6831 75.9731 25.0351C75.5891 25.3871 75.3731 25.8471 75.3251 26.4151Z" fill="#2755CB"/>
        <rect x="13.2691" y="14.8355" width="74.1138" height="23.4071" rx="3.26084" stroke="#2755CB" stroke-width="0.592879"/>
        <rect x="94.4976" y="14.8355" width="74.1138" height="23.4071" rx="3.26084" fill="white"/>
        <path d="M111.483 30.0391V22.5271H108.915V21.6391H115.023V22.5271H112.455V30.0391H111.483ZM120.489 29.2591C119.873 29.8831 119.097 30.1951 118.161 30.1951C117.225 30.1951 116.449 29.8871 115.833 29.2711C115.217 28.6471 114.909 27.8631 114.909 26.9191C114.909 25.9751 115.221 25.1951 115.845 24.5791C116.469 23.9551 117.245 23.6431 118.173 23.6431C119.109 23.6431 119.885 23.9551 120.501 24.5791C121.117 25.2031 121.425 25.9831 121.425 26.9191C121.425 27.8551 121.113 28.6351 120.489 29.2591ZM118.161 29.3311C118.833 29.3311 119.381 29.1031 119.805 28.6471C120.237 28.1911 120.453 27.6151 120.453 26.9191C120.453 26.2231 120.237 25.6471 119.805 25.1911C119.381 24.7351 118.833 24.5071 118.161 24.5071C117.497 24.5071 116.949 24.7391 116.517 25.2031C116.093 25.6591 115.881 26.2311 115.881 26.9191C115.881 27.6231 116.093 28.2031 116.517 28.6591C116.949 29.1071 117.497 29.3311 118.161 29.3311ZM126.583 30.0391V21.6391H129.079C130.383 21.6391 131.411 22.0271 132.163 22.8031C132.915 23.5791 133.291 24.5911 133.291 25.8391C133.291 27.1511 132.919 28.1791 132.175 28.9231C131.439 29.6671 130.407 30.0391 129.079 30.0391H126.583ZM127.555 29.1751H129.079C130.079 29.1751 130.863 28.8831 131.431 28.2991C132.007 27.7071 132.295 26.8871 132.295 25.8391C132.295 24.8151 132.007 24.0071 131.431 23.4151C130.863 22.8151 130.079 22.5151 129.079 22.5151H127.555V29.1751ZM137.599 30.1951C136.687 30.1951 135.939 29.8911 135.355 29.2831C134.779 28.6751 134.491 27.8911 134.491 26.9311C134.491 25.9711 134.775 25.1831 135.343 24.5671C135.919 23.9511 136.647 23.6431 137.527 23.6431C138.095 23.6431 138.563 23.7711 138.931 24.0271C139.307 24.2831 139.571 24.5431 139.723 24.8071H139.795V23.7991H140.743V30.0391H139.831V29.0551H139.759C139.239 29.8151 138.519 30.1951 137.599 30.1951ZM136.063 28.6831C136.471 29.1231 137.003 29.3431 137.659 29.3431C138.315 29.3431 138.839 29.1111 139.231 28.6471C139.631 28.1831 139.831 27.6111 139.831 26.9311C139.831 26.1791 139.623 25.5871 139.207 25.1551C138.799 24.7231 138.275 24.5071 137.635 24.5071C136.995 24.5071 136.471 24.7351 136.063 25.1911C135.663 25.6391 135.463 26.2191 135.463 26.9311C135.463 27.6591 135.663 28.2431 136.063 28.6831ZM145.223 30.0391C144.639 30.0391 144.183 29.8791 143.855 29.5591C143.527 29.2391 143.363 28.7711 143.363 28.1551V24.6031H142.187V23.7991H143.123C143.323 23.7991 143.423 23.6951 143.423 23.4871V21.9871H144.311V23.7991H146.231V24.6031H144.311V28.1431C144.311 28.8551 144.635 29.2111 145.283 29.2111H146.147V30.0391H145.223ZM150.548 30.1951C149.612 30.1951 148.856 29.8871 148.28 29.2711C147.712 28.6551 147.428 27.8711 147.428 26.9191C147.428 25.9431 147.72 25.1551 148.304 24.5551C148.888 23.9471 149.616 23.6431 150.488 23.6431C151.416 23.6431 152.152 23.9431 152.696 24.5431C153.24 25.1431 153.512 25.9071 153.512 26.8351V27.2551H148.424C148.448 27.8871 148.648 28.3911 149.024 28.7671C149.408 29.1431 149.92 29.3311 150.56 29.3311C150.992 29.3311 151.384 29.2311 151.736 29.0311C152.088 28.8311 152.332 28.5551 152.468 28.2031H153.452C153.276 28.7951 152.928 29.2751 152.408 29.6431C151.888 30.0111 151.268 30.1951 150.548 30.1951ZM148.448 26.4151H152.504C152.464 25.8151 152.256 25.3471 151.88 25.0111C151.504 24.6751 151.04 24.5071 150.488 24.5071C149.952 24.5071 149.488 24.6831 149.096 25.0351C148.712 25.3871 148.496 25.8471 148.448 26.4151Z" fill="#2755CB"/>
        <rect x="94.4976" y="14.8355" width="74.1138" height="23.4071" rx="3.26084" stroke="#2755CB" stroke-width="0.592879"/>
        <rect x="13.2691" y="48.3218" width="155.342" height="23.4071" rx="3.26084" fill="white"/>
        <path d="M63.1804 63.5254L66.4204 55.1254H67.5604L70.7884 63.5254H69.7684L69.0124 61.5334H64.9564L64.2004 63.5254H63.1804ZM65.2924 60.6454H68.6764L67.0204 56.2534H66.9484L65.2924 60.6454ZM74.6172 63.6814C73.7052 63.6814 72.9572 63.3774 72.3732 62.7694C71.7972 62.1614 71.5092 61.3774 71.5092 60.4174C71.5092 59.4574 71.7932 58.6694 72.3612 58.0534C72.9372 57.4374 73.6652 57.1294 74.5452 57.1294C75.1132 57.1294 75.5812 57.2574 75.9492 57.5134C76.3252 57.7694 76.5892 58.0294 76.7412 58.2934H76.8132V54.5254H77.7612V63.5254H76.8492V62.5414H76.7772C76.2572 63.3014 75.5372 63.6814 74.6172 63.6814ZM73.0812 62.1694C73.4892 62.6094 74.0212 62.8294 74.6772 62.8294C75.3332 62.8294 75.8572 62.5974 76.2492 62.1334C76.6492 61.6694 76.8492 61.0974 76.8492 60.4174C76.8492 59.6654 76.6412 59.0734 76.2252 58.6414C75.8172 58.2094 75.2932 57.9934 74.6532 57.9934C74.0132 57.9934 73.4892 58.2214 73.0812 58.6774C72.6812 59.1254 72.4812 59.7054 72.4812 60.4174C72.4812 61.1454 72.6812 61.7294 73.0812 62.1694ZM82.4336 63.6814C81.5216 63.6814 80.7736 63.3774 80.1896 62.7694C79.6136 62.1614 79.3256 61.3774 79.3256 60.4174C79.3256 59.4574 79.6096 58.6694 80.1776 58.0534C80.7536 57.4374 81.4816 57.1294 82.3616 57.1294C82.9296 57.1294 83.3976 57.2574 83.7656 57.5134C84.1416 57.7694 84.4056 58.0294 84.5576 58.2934H84.6296V54.5254H85.5776V63.5254H84.6656V62.5414H84.5936C84.0736 63.3014 83.3536 63.6814 82.4336 63.6814ZM80.8976 62.1694C81.3056 62.6094 81.8376 62.8294 82.4936 62.8294C83.1496 62.8294 83.6736 62.5974 84.0656 62.1334C84.4656 61.6694 84.6656 61.0974 84.6656 60.4174C84.6656 59.6654 84.4576 59.0734 84.0416 58.6414C83.6336 58.2094 83.1096 57.9934 82.4696 57.9934C81.8296 57.9934 81.3056 58.2214 80.8976 58.6774C80.4976 59.1254 80.2976 59.7054 80.2976 60.4174C80.2976 61.1454 80.4976 61.7294 80.8976 62.1694ZM92.8333 63.5254V56.0134H90.2653V55.1254H96.3733V56.0134H93.8053V63.5254H92.8333ZM98.8013 55.9654C98.6733 56.0934 98.5093 56.1574 98.3093 56.1574C98.1093 56.1574 97.9453 56.0934 97.8173 55.9654C97.6893 55.8294 97.6253 55.6614 97.6253 55.4614C97.6253 55.2694 97.6893 55.1094 97.8173 54.9814C97.9453 54.8454 98.1093 54.7774 98.3093 54.7774C98.5093 54.7774 98.6733 54.8454 98.8013 54.9814C98.9373 55.1094 99.0053 55.2694 99.0053 55.4614C99.0053 55.6614 98.9373 55.8294 98.8013 55.9654ZM97.8173 63.5254V57.2854H98.7653V63.5254H97.8173ZM100.806 63.5254V57.2854H101.754V58.1854H101.826C102.194 57.4814 102.802 57.1294 103.65 57.1294C104.106 57.1294 104.502 57.2334 104.838 57.4414C105.182 57.6414 105.442 57.9174 105.618 58.2694H105.702C106.102 57.5094 106.762 57.1294 107.682 57.1294C108.37 57.1294 108.922 57.3494 109.338 57.7894C109.762 58.2294 109.974 58.7934 109.974 59.4814V63.5254H109.026V59.7934C109.026 59.2174 108.89 58.7774 108.618 58.4734C108.354 58.1694 107.986 58.0174 107.514 58.0174C107.05 58.0174 106.658 58.1774 106.338 58.4974C106.026 58.8094 105.87 59.2454 105.87 59.8054V63.5254H104.922V59.6134C104.922 59.1254 104.774 58.7374 104.478 58.4494C104.19 58.1614 103.822 58.0174 103.374 58.0174C102.926 58.0174 102.542 58.1814 102.222 58.5094C101.91 58.8374 101.754 59.2574 101.754 59.7694V63.5254H100.806ZM114.649 63.6814C113.713 63.6814 112.957 63.3734 112.381 62.7574C111.813 62.1414 111.529 61.3574 111.529 60.4054C111.529 59.4294 111.821 58.6414 112.405 58.0414C112.989 57.4334 113.717 57.1294 114.589 57.1294C115.517 57.1294 116.253 57.4294 116.797 58.0294C117.341 58.6294 117.613 59.3934 117.613 60.3214V60.7414H112.525C112.549 61.3734 112.749 61.8774 113.125 62.2534C113.509 62.6294 114.021 62.8174 114.661 62.8174C115.093 62.8174 115.485 62.7174 115.837 62.5174C116.189 62.3174 116.433 62.0414 116.569 61.6894H117.553C117.377 62.2814 117.029 62.7614 116.509 63.1294C115.989 63.4974 115.369 63.6814 114.649 63.6814ZM112.549 59.9014H116.605C116.565 59.3014 116.357 58.8334 115.981 58.4974C115.605 58.1614 115.141 57.9934 114.589 57.9934C114.053 57.9934 113.589 58.1694 113.197 58.5214C112.813 58.8734 112.597 59.3334 112.549 59.9014Z" fill="#2755CB"/>
        <rect x="13.2691" y="48.3218" width="155.342" height="23.4071" rx="3.26084" stroke="#2755CB" stroke-width="0.592879"/>
        <rect x="5.2691" y="2.97808" width="171.342" height="80.6084" rx="2.07508" stroke="#FAFAFA" stroke-width="0.592879"/>
        </g>
        <defs>
        <filter id="filter0_dd_1693_222539" x="0.229622" y="0.310124" width="181.421" height="90.6872" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
        <feFlood flood-opacity="0" result="BackgroundImageFix"/>
        <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
        <feOffset dy="2.37152"/>
        <feGaussianBlur stdDeviation="2.37152"/>
        <feColorMatrix type="matrix" values="0 0 0 0 0.196487 0 0 0 0 0.196487 0 0 0 0 0.279476 0 0 0 0.06 0"/>
        <feBlend mode="multiply" in2="BackgroundImageFix" result="effect1_dropShadow_1693_222539"/>
        <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
        <feOffset dy="2.37152"/>
        <feGaussianBlur stdDeviation="1.18576"/>
        <feColorMatrix type="matrix" values="0 0 0 0 0.196487 0 0 0 0 0.196487 0 0 0 0 0.279476 0 0 0 0.08 0"/>
        <feBlend mode="multiply" in2="effect1_dropShadow_1693_222539" result="effect2_dropShadow_1693_222539"/>
        <feBlend mode="normal" in="SourceGraphic" in2="effect2_dropShadow_1693_222539" result="shape"/>
        </filter>
        </defs>
        </svg>
        </div>
        </div>
        `
    } else if (widget_data_req.is_single_datepicker === "true" && widget_data_req.is_multi_timepicker === "true") {
        html += `
        <div class="single-date-custom-time-response-bot-preview-wrapper">
        <svg width="182" height="92" viewBox="0 0 182 92" fill="none" xmlns="http://www.w3.org/2000/svg">
        <g filter="url(#filter0_dd_1693_222516)">
        <rect x="4.97266" y="3.02246" width="171.935" height="81.2012" rx="2.37152" fill="white"/>
        <rect x="13.2691" y="14.9332" width="155.342" height="23.8932" rx="3.26084" fill="white"/>
        <path d="M62.6804 30.3799L65.9204 21.9799H67.0604L70.2884 30.3799H69.2684L68.5124 28.3879H64.4564L63.7004 30.3799H62.6804ZM64.7924 27.4999H68.1764L66.5204 23.1079H66.4484L64.7924 27.4999ZM74.1883 30.5359C73.2763 30.5359 72.5283 30.2319 71.9443 29.6239C71.3683 29.0159 71.0803 28.2319 71.0803 27.2719C71.0803 26.3119 71.3643 25.5239 71.9323 24.9079C72.5083 24.2919 73.2363 23.9839 74.1163 23.9839C74.6843 23.9839 75.1523 24.1119 75.5203 24.3679C75.8963 24.6239 76.1603 24.8839 76.3123 25.1479H76.3843V21.3799H77.3323V30.3799H76.4203V29.3959H76.3483C75.8283 30.1559 75.1083 30.5359 74.1883 30.5359ZM72.6523 29.0239C73.0603 29.4639 73.5923 29.6839 74.2483 29.6839C74.9043 29.6839 75.4283 29.4519 75.8203 28.9879C76.2203 28.5239 76.4203 27.9519 76.4203 27.2719C76.4203 26.5199 76.2123 25.9279 75.7963 25.4959C75.3883 25.0639 74.8643 24.8479 74.2243 24.8479C73.5843 24.8479 73.0603 25.0759 72.6523 25.5319C72.2523 25.9799 72.0523 26.5599 72.0523 27.2719C72.0523 27.9999 72.2523 28.5839 72.6523 29.0239ZM82.0759 30.5359C81.1639 30.5359 80.4159 30.2319 79.8319 29.6239C79.2559 29.0159 78.9679 28.2319 78.9679 27.2719C78.9679 26.3119 79.2519 25.5239 79.8199 24.9079C80.3959 24.2919 81.1239 23.9839 82.0039 23.9839C82.5719 23.9839 83.0399 24.1119 83.4079 24.3679C83.7839 24.6239 84.0479 24.8839 84.1999 25.1479H84.2719V21.3799H85.2199V30.3799H84.3079V29.3959H84.2359C83.7159 30.1559 82.9959 30.5359 82.0759 30.5359ZM80.5399 29.0239C80.9479 29.4639 81.4799 29.6839 82.1359 29.6839C82.7919 29.6839 83.3159 29.4519 83.7079 28.9879C84.1079 28.5239 84.3079 27.9519 84.3079 27.2719C84.3079 26.5199 84.0999 25.9279 83.6839 25.4959C83.2759 25.0639 82.7519 24.8479 82.1119 24.8479C81.4719 24.8479 80.9479 25.0759 80.5399 25.5319C80.1399 25.9799 79.9399 26.5599 79.9399 27.2719C79.9399 27.9999 80.1399 28.5839 80.5399 29.0239ZM90.8899 30.3799V21.9799H93.3859C94.6899 21.9799 95.7179 22.3679 96.4699 23.1439C97.2219 23.9199 97.5979 24.9319 97.5979 26.1799C97.5979 27.4919 97.2259 28.5199 96.4819 29.2639C95.7459 30.0079 94.7139 30.3799 93.3859 30.3799H90.8899ZM91.8619 29.5159H93.3859C94.3859 29.5159 95.1699 29.2239 95.7379 28.6399C96.3139 28.0479 96.6019 27.2279 96.6019 26.1799C96.6019 25.1559 96.3139 24.3479 95.7379 23.7559C95.1699 23.1559 94.3859 22.8559 93.3859 22.8559H91.8619V29.5159ZM101.977 30.5359C101.065 30.5359 100.317 30.2319 99.7328 29.6239C99.1568 29.0159 98.8688 28.2319 98.8688 27.2719C98.8688 26.3119 99.1528 25.5239 99.7208 24.9079C100.297 24.2919 101.025 23.9839 101.905 23.9839C102.473 23.9839 102.941 24.1119 103.309 24.3679C103.685 24.6239 103.949 24.8839 104.101 25.1479H104.173V24.1399H105.121V30.3799H104.209V29.3959H104.137C103.617 30.1559 102.897 30.5359 101.977 30.5359ZM100.441 29.0239C100.849 29.4639 101.381 29.6839 102.037 29.6839C102.693 29.6839 103.217 29.4519 103.609 28.9879C104.009 28.5239 104.209 27.9519 104.209 27.2719C104.209 26.5199 104.001 25.9279 103.585 25.4959C103.177 25.0639 102.653 24.8479 102.013 24.8479C101.373 24.8479 100.849 25.0759 100.441 25.5319C100.041 25.9799 99.8408 26.5599 99.8408 27.2719C99.8408 27.9999 100.041 28.5839 100.441 29.0239ZM109.672 30.3799C109.088 30.3799 108.632 30.2199 108.304 29.8999C107.976 29.5799 107.812 29.1119 107.812 28.4959V24.9439H106.636V24.1399H107.572C107.772 24.1399 107.872 24.0359 107.872 23.8279V22.3279H108.76V24.1399H110.68V24.9439H108.76V28.4839C108.76 29.1959 109.084 29.5519 109.732 29.5519H110.596V30.3799H109.672ZM115.069 30.5359C114.133 30.5359 113.377 30.2279 112.801 29.6119C112.233 28.9959 111.949 28.2119 111.949 27.2599C111.949 26.2839 112.241 25.4959 112.825 24.8959C113.409 24.2879 114.137 23.9839 115.009 23.9839C115.937 23.9839 116.673 24.2839 117.217 24.8839C117.761 25.4839 118.033 26.2479 118.033 27.1759V27.5959H112.945C112.969 28.2279 113.169 28.7319 113.545 29.1079C113.929 29.4839 114.441 29.6719 115.081 29.6719C115.513 29.6719 115.905 29.5719 116.257 29.3719C116.609 29.1719 116.853 28.8959 116.989 28.5439H117.973C117.797 29.1359 117.449 29.6159 116.929 29.9839C116.409 30.3519 115.789 30.5359 115.069 30.5359ZM112.969 26.7559H117.025C116.985 26.1559 116.777 25.6879 116.401 25.3519C116.025 25.0159 115.561 24.8479 115.009 24.8479C114.473 24.8479 114.009 25.0239 113.617 25.3759C113.233 25.7279 113.017 26.1879 112.969 26.7559Z" fill="#2755CB"/>
        <rect x="13.2691" y="14.9332" width="155.342" height="23.8932" rx="3.26084" stroke="#2755CB" stroke-width="0.592879"/>
        <rect x="13.2691" y="48.6627" width="74.1138" height="23.4071" rx="3.26084" fill="white"/>
        <path d="M20.0262 63.8662V55.4662H24.8142V56.3542H20.9982V59.2342H24.5622V60.1102H20.9982V63.8662H20.0262ZM26.5633 63.8662V57.6262H27.4993V58.7902H27.5713C27.6753 58.4862 27.8793 58.2182 28.1833 57.9862C28.4873 57.7462 28.8513 57.6262 29.2753 57.6262H29.8033V58.5742H29.2873C28.7353 58.5742 28.2993 58.7702 27.9793 59.1622C27.6673 59.5462 27.5113 60.0422 27.5113 60.6502V63.8662H26.5633ZM36.3047 63.0862C35.6887 63.7102 34.9127 64.0222 33.9767 64.0222C33.0407 64.0222 32.2647 63.7142 31.6487 63.0982C31.0327 62.4742 30.7247 61.6902 30.7247 60.7462C30.7247 59.8022 31.0367 59.0222 31.6607 58.4062C32.2847 57.7822 33.0607 57.4702 33.9887 57.4702C34.9247 57.4702 35.7007 57.7822 36.3167 58.4062C36.9327 59.0302 37.2407 59.8102 37.2407 60.7462C37.2407 61.6822 36.9287 62.4622 36.3047 63.0862ZM33.9767 63.1582C34.6487 63.1582 35.1967 62.9302 35.6207 62.4742C36.0527 62.0182 36.2687 61.4422 36.2687 60.7462C36.2687 60.0502 36.0527 59.4742 35.6207 59.0182C35.1967 58.5622 34.6487 58.3342 33.9767 58.3342C33.3127 58.3342 32.7647 58.5662 32.3327 59.0302C31.9087 59.4862 31.6967 60.0582 31.6967 60.7462C31.6967 61.4502 31.9087 62.0302 32.3327 62.4862C32.7647 62.9342 33.3127 63.1582 33.9767 63.1582ZM38.9868 63.8662V57.6262H39.9348V58.5262H40.0068C40.3748 57.8222 40.9828 57.4702 41.8308 57.4702C42.2868 57.4702 42.6828 57.5742 43.0188 57.7822C43.3628 57.9822 43.6228 58.2582 43.7988 58.6102H43.8828C44.2828 57.8502 44.9428 57.4702 45.8628 57.4702C46.5508 57.4702 47.1028 57.6902 47.5188 58.1302C47.9428 58.5702 48.1548 59.1342 48.1548 59.8222V63.8662H47.2068V60.1342C47.2068 59.5582 47.0708 59.1182 46.7988 58.8142C46.5348 58.5102 46.1668 58.3582 45.6948 58.3582C45.2308 58.3582 44.8388 58.5182 44.5188 58.8382C44.2068 59.1502 44.0508 59.5862 44.0508 60.1462V63.8662H43.1028V59.9542C43.1028 59.4662 42.9548 59.0782 42.6588 58.7902C42.3708 58.5022 42.0028 58.3582 41.5548 58.3582C41.1068 58.3582 40.7228 58.5222 40.4028 58.8502C40.0908 59.1782 39.9348 59.5982 39.9348 60.1102V63.8662H38.9868ZM55.5435 63.8662V56.3542H52.9755V55.4662H59.0835V56.3542H56.5155V63.8662H55.5435ZM61.5827 56.3062C61.4547 56.4342 61.2907 56.4982 61.0907 56.4982C60.8907 56.4982 60.7267 56.4342 60.5987 56.3062C60.4707 56.1702 60.4067 56.0022 60.4067 55.8022C60.4067 55.6102 60.4707 55.4502 60.5987 55.3222C60.7267 55.1862 60.8907 55.1182 61.0907 55.1182C61.2907 55.1182 61.4547 55.1862 61.5827 55.3222C61.7187 55.4502 61.7867 55.6102 61.7867 55.8022C61.7867 56.0022 61.7187 56.1702 61.5827 56.3062ZM60.5987 63.8662V57.6262H61.5467V63.8662H60.5987ZM63.6581 63.8662V57.6262H64.6061V58.5262H64.6781C65.0461 57.8222 65.6541 57.4702 66.5021 57.4702C66.9581 57.4702 67.3541 57.5742 67.6901 57.7822C68.0341 57.9822 68.2941 58.2582 68.4701 58.6102H68.5541C68.9541 57.8502 69.6141 57.4702 70.5341 57.4702C71.2221 57.4702 71.7741 57.6902 72.1901 58.1302C72.6141 58.5702 72.8261 59.1342 72.8261 59.8222V63.8662H71.8781V60.1342C71.8781 59.5582 71.7421 59.1182 71.4701 58.8142C71.2061 58.5102 70.8381 58.3582 70.3661 58.3582C69.9021 58.3582 69.5101 58.5182 69.1901 58.8382C68.8781 59.1502 68.7221 59.5862 68.7221 60.1462V63.8662H67.7741V59.9542C67.7741 59.4662 67.6261 59.0782 67.3301 58.7902C67.0421 58.5022 66.6741 58.3582 66.2261 58.3582C65.7781 58.3582 65.3941 58.5222 65.0741 58.8502C64.7621 59.1782 64.6061 59.5982 64.6061 60.1102V63.8662H63.6581ZM77.5724 64.0222C76.6364 64.0222 75.8804 63.7142 75.3044 63.0982C74.7364 62.4822 74.4524 61.6982 74.4524 60.7462C74.4524 59.7702 74.7444 58.9822 75.3284 58.3822C75.9124 57.7742 76.6404 57.4702 77.5124 57.4702C78.4404 57.4702 79.1764 57.7702 79.7204 58.3702C80.2644 58.9702 80.5364 59.7342 80.5364 60.6622V61.0822H75.4484C75.4724 61.7142 75.6724 62.2182 76.0484 62.5942C76.4324 62.9702 76.9444 63.1582 77.5844 63.1582C78.0164 63.1582 78.4084 63.0582 78.7604 62.8582C79.1124 62.6582 79.3564 62.3822 79.4924 62.0302H80.4764C80.3004 62.6222 79.9524 63.1022 79.4324 63.4702C78.9124 63.8382 78.2924 64.0222 77.5724 64.0222ZM75.4724 60.2422H79.5284C79.4884 59.6422 79.2804 59.1742 78.9044 58.8382C78.5284 58.5022 78.0644 58.3342 77.5124 58.3342C76.9764 58.3342 76.5124 58.5102 76.1204 58.8622C75.7364 59.2142 75.5204 59.6742 75.4724 60.2422Z" fill="#2755CB"/>
        <rect x="13.2691" y="48.6627" width="74.1138" height="23.4071" rx="3.26084" stroke="#2755CB" stroke-width="0.592879"/>
        <rect x="94.4976" y="48.6627" width="74.1138" height="23.4071" rx="3.26084" fill="white"/>
        <path d="M111.483 63.8662V56.3542H108.915V55.4662H115.023V56.3542H112.455V63.8662H111.483ZM120.56 63.0862C119.944 63.7102 119.168 64.0222 118.232 64.0222C117.296 64.0222 116.52 63.7142 115.904 63.0982C115.288 62.4742 114.98 61.6902 114.98 60.7462C114.98 59.8022 115.292 59.0222 115.916 58.4062C116.54 57.7822 117.316 57.4702 118.244 57.4702C119.18 57.4702 119.956 57.7822 120.572 58.4062C121.188 59.0302 121.496 59.8102 121.496 60.7462C121.496 61.6822 121.184 62.4622 120.56 63.0862ZM118.232 63.1582C118.904 63.1582 119.452 62.9302 119.876 62.4742C120.308 62.0182 120.524 61.4422 120.524 60.7462C120.524 60.0502 120.308 59.4742 119.876 59.0182C119.452 58.5622 118.904 58.3342 118.232 58.3342C117.568 58.3342 117.02 58.5662 116.588 59.0302C116.164 59.4862 115.952 60.0582 115.952 60.7462C115.952 61.4502 116.164 62.0302 116.588 62.4862C117.02 62.9342 117.568 63.1582 118.232 63.1582ZM128.524 63.8662V56.3542H125.956V55.4662H132.064V56.3542H129.496V63.8662H128.524ZM134.563 56.3062C134.435 56.4342 134.271 56.4982 134.071 56.4982C133.871 56.4982 133.707 56.4342 133.579 56.3062C133.451 56.1702 133.387 56.0022 133.387 55.8022C133.387 55.6102 133.451 55.4502 133.579 55.3222C133.707 55.1862 133.871 55.1182 134.071 55.1182C134.271 55.1182 134.435 55.1862 134.563 55.3222C134.699 55.4502 134.767 55.6102 134.767 55.8022C134.767 56.0022 134.699 56.1702 134.563 56.3062ZM133.579 63.8662V57.6262H134.527V63.8662H133.579ZM136.639 63.8662V57.6262H137.587V58.5262H137.659C138.027 57.8222 138.635 57.4702 139.483 57.4702C139.939 57.4702 140.335 57.5742 140.671 57.7822C141.015 57.9822 141.275 58.2582 141.451 58.6102H141.535C141.935 57.8502 142.595 57.4702 143.515 57.4702C144.203 57.4702 144.755 57.6902 145.171 58.1302C145.595 58.5702 145.807 59.1342 145.807 59.8222V63.8662H144.859V60.1342C144.859 59.5582 144.723 59.1182 144.451 58.8142C144.187 58.5102 143.819 58.3582 143.347 58.3582C142.883 58.3582 142.491 58.5182 142.171 58.8382C141.859 59.1502 141.703 59.5862 141.703 60.1462V63.8662H140.755V59.9542C140.755 59.4662 140.607 59.0782 140.311 58.7902C140.023 58.5022 139.655 58.3582 139.207 58.3582C138.759 58.3582 138.375 58.5222 138.055 58.8502C137.743 59.1782 137.587 59.5982 137.587 60.1102V63.8662H136.639ZM150.553 64.0222C149.617 64.0222 148.861 63.7142 148.285 63.0982C147.717 62.4822 147.433 61.6982 147.433 60.7462C147.433 59.7702 147.725 58.9822 148.309 58.3822C148.893 57.7742 149.621 57.4702 150.493 57.4702C151.421 57.4702 152.157 57.7702 152.701 58.3702C153.245 58.9702 153.517 59.7342 153.517 60.6622V61.0822H148.429C148.453 61.7142 148.653 62.2182 149.029 62.5942C149.413 62.9702 149.925 63.1582 150.565 63.1582C150.997 63.1582 151.389 63.0582 151.741 62.8582C152.093 62.6582 152.337 62.3822 152.473 62.0302H153.457C153.281 62.6222 152.933 63.1022 152.413 63.4702C151.893 63.8382 151.273 64.0222 150.553 64.0222ZM148.453 60.2422H152.509C152.469 59.6422 152.261 59.1742 151.885 58.8382C151.509 58.5022 151.045 58.3342 150.493 58.3342C149.957 58.3342 149.493 58.5102 149.101 58.8622C148.717 59.2142 148.501 59.6742 148.453 60.2422Z" fill="#2755CB"/>
        <rect x="94.4976" y="48.6627" width="74.1138" height="23.4071" rx="3.26084" stroke="#2755CB" stroke-width="0.592879"/>
        <rect x="5.2691" y="3.3189" width="171.342" height="80.6084" rx="2.07508" stroke="#FAFAFA" stroke-width="0.592879"/>
        </g>
        <defs>
        <filter id="filter0_dd_1693_222516" x="0.229622" y="0.650944" width="181.421" height="90.6872" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
        <feFlood flood-opacity="0" result="BackgroundImageFix"/>
        <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
        <feOffset dy="2.37152"/>
        <feGaussianBlur stdDeviation="2.37152"/>
        <feColorMatrix type="matrix" values="0 0 0 0 0.196487 0 0 0 0 0.196487 0 0 0 0 0.279476 0 0 0 0.06 0"/>
        <feBlend mode="multiply" in2="BackgroundImageFix" result="effect1_dropShadow_1693_222516"/>
        <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
        <feOffset dy="2.37152"/>
        <feGaussianBlur stdDeviation="1.18576"/>
        <feColorMatrix type="matrix" values="0 0 0 0 0.196487 0 0 0 0 0.196487 0 0 0 0 0.279476 0 0 0 0.08 0"/>
        <feBlend mode="multiply" in2="effect1_dropShadow_1693_222516" result="effect2_dropShadow_1693_222516"/>
        <feBlend mode="normal" in="SourceGraphic" in2="effect2_dropShadow_1693_222516" result="shape"/>
        </filter>
        </defs>
        </svg>
        </div>
        </div>        
        `
    } else if (widget_data_req.is_single_datepicker === "true" && widget_data_req.is_single_timepicker === "true") {
        html += `
        <div class="single-date-time-response-bot-preview-wrapper">
        <svg width="182" height="58" viewBox="0 0 182 58" fill="none" xmlns="http://www.w3.org/2000/svg">
        <g filter="url(#filter0_dd_1693_222500)">
        <rect x="4.97266" y="2.84961" width="171.935" height="47.7152" rx="2.37152" fill="white"/>
        <rect x="9.2691" y="15.0035" width="78.1138" height="23.4071" rx="3.26084" fill="white"/>
        <path d="M20.0662 30.207L23.3062 21.807H24.4462L27.6742 30.207H26.6542L25.8982 28.215H21.8422L21.0862 30.207H20.0662ZM22.1782 27.327H25.5622L23.9062 22.935H23.8342L22.1782 27.327ZM31.5741 30.363C30.6621 30.363 29.9141 30.059 29.3301 29.451C28.7541 28.843 28.4661 28.059 28.4661 27.099C28.4661 26.139 28.7501 25.351 29.3181 24.735C29.8941 24.119 30.6221 23.811 31.5021 23.811C32.0701 23.811 32.5381 23.939 32.9061 24.195C33.2821 24.451 33.5461 24.711 33.6981 24.975H33.7701V21.207H34.7181V30.207H33.8061V29.223H33.7341C33.2141 29.983 32.4941 30.363 31.5741 30.363ZM30.0381 28.851C30.4461 29.291 30.9781 29.511 31.6341 29.511C32.2901 29.511 32.8141 29.279 33.2061 28.815C33.6061 28.351 33.8061 27.779 33.8061 27.099C33.8061 26.347 33.5981 25.755 33.1821 25.323C32.7741 24.891 32.2501 24.675 31.6101 24.675C30.9701 24.675 30.4461 24.903 30.0381 25.359C29.6381 25.807 29.4381 26.387 29.4381 27.099C29.4381 27.827 29.6381 28.411 30.0381 28.851ZM39.4616 30.363C38.5496 30.363 37.8016 30.059 37.2176 29.451C36.6416 28.843 36.3536 28.059 36.3536 27.099C36.3536 26.139 36.6376 25.351 37.2056 24.735C37.7816 24.119 38.5096 23.811 39.3896 23.811C39.9576 23.811 40.4256 23.939 40.7936 24.195C41.1696 24.451 41.4336 24.711 41.5856 24.975H41.6576V21.207H42.6056V30.207H41.6936V29.223H41.6216C41.1016 29.983 40.3816 30.363 39.4616 30.363ZM37.9256 28.851C38.3336 29.291 38.8656 29.511 39.5216 29.511C40.1776 29.511 40.7016 29.279 41.0936 28.815C41.4936 28.351 41.6936 27.779 41.6936 27.099C41.6936 26.347 41.4856 25.755 41.0696 25.323C40.6616 24.891 40.1376 24.675 39.4976 24.675C38.8576 24.675 38.3336 24.903 37.9256 25.359C37.5256 25.807 37.3256 26.387 37.3256 27.099C37.3256 27.827 37.5256 28.411 37.9256 28.851ZM48.2756 30.207V21.807H50.7716C52.0756 21.807 53.1036 22.195 53.8556 22.971C54.6076 23.747 54.9836 24.759 54.9836 26.007C54.9836 27.319 54.6116 28.347 53.8676 29.091C53.1316 29.835 52.0996 30.207 50.7716 30.207H48.2756ZM49.2476 29.343H50.7716C51.7716 29.343 52.5556 29.051 53.1236 28.467C53.6996 27.875 53.9876 27.055 53.9876 26.007C53.9876 24.983 53.6996 24.175 53.1236 23.583C52.5556 22.983 51.7716 22.683 50.7716 22.683H49.2476V29.343ZM59.3626 30.363C58.4506 30.363 57.7026 30.059 57.1186 29.451C56.5426 28.843 56.2546 28.059 56.2546 27.099C56.2546 26.139 56.5386 25.351 57.1066 24.735C57.6826 24.119 58.4106 23.811 59.2906 23.811C59.8586 23.811 60.3266 23.939 60.6946 24.195C61.0706 24.451 61.3346 24.711 61.4866 24.975H61.5586V23.967H62.5066V30.207H61.5946V29.223H61.5226C61.0026 29.983 60.2826 30.363 59.3626 30.363ZM57.8266 28.851C58.2346 29.291 58.7666 29.511 59.4226 29.511C60.0786 29.511 60.6026 29.279 60.9946 28.815C61.3946 28.351 61.5946 27.779 61.5946 27.099C61.5946 26.347 61.3866 25.755 60.9706 25.323C60.5626 24.891 60.0386 24.675 59.3986 24.675C58.7586 24.675 58.2346 24.903 57.8266 25.359C57.4266 25.807 57.2266 26.387 57.2266 27.099C57.2266 27.827 57.4266 28.411 57.8266 28.851ZM67.0581 30.207C66.4741 30.207 66.0181 30.047 65.6901 29.727C65.3621 29.407 65.1981 28.939 65.1981 28.323V24.771H64.0221V23.967H64.9581C65.1581 23.967 65.2581 23.863 65.2581 23.655V22.155H66.1461V23.967H68.0661V24.771H66.1461V28.311C66.1461 29.023 66.4701 29.379 67.1181 29.379H67.9821V30.207H67.0581ZM72.4543 30.363C71.5183 30.363 70.7623 30.055 70.1863 29.439C69.6183 28.823 69.3343 28.039 69.3343 27.087C69.3343 26.111 69.6263 25.323 70.2103 24.723C70.7943 24.115 71.5223 23.811 72.3943 23.811C73.3223 23.811 74.0583 24.111 74.6023 24.711C75.1463 25.311 75.4183 26.075 75.4183 27.003V27.423H70.3303C70.3543 28.055 70.5543 28.559 70.9303 28.935C71.3143 29.311 71.8263 29.499 72.4663 29.499C72.8983 29.499 73.2903 29.399 73.6423 29.199C73.9943 28.999 74.2383 28.723 74.3743 28.371H75.3583C75.1823 28.963 74.8343 29.443 74.3143 29.811C73.7943 30.179 73.1743 30.363 72.4543 30.363ZM70.3543 26.583H74.4103C74.3703 25.983 74.1623 25.515 73.7863 25.179C73.4103 24.843 72.9463 24.675 72.3943 24.675C71.8583 24.675 71.3943 24.851 71.0023 25.203C70.6183 25.555 70.4023 26.015 70.3543 26.583Z" fill="#2755CB"/>
        <rect x="9.2691" y="15.0035" width="78.1138" height="23.4071" rx="3.26084" stroke="#2755CB" stroke-width="0.592879"/>
        <rect x="94.4976" y="15.0035" width="78.1138" height="23.4071" rx="3.26084" fill="white"/>
        <path d="M105.795 30.207L109.035 21.807H110.175L113.403 30.207H112.383L111.627 28.215H107.571L106.815 30.207H105.795ZM107.907 27.327H111.291L109.635 22.935H109.563L107.907 27.327ZM117.303 30.363C116.391 30.363 115.643 30.059 115.059 29.451C114.483 28.843 114.195 28.059 114.195 27.099C114.195 26.139 114.479 25.351 115.047 24.735C115.623 24.119 116.351 23.811 117.231 23.811C117.799 23.811 118.267 23.939 118.635 24.195C119.011 24.451 119.275 24.711 119.427 24.975H119.499V21.207H120.447V30.207H119.535V29.223H119.463C118.943 29.983 118.223 30.363 117.303 30.363ZM115.767 28.851C116.175 29.291 116.707 29.511 117.363 29.511C118.019 29.511 118.543 29.279 118.935 28.815C119.335 28.351 119.535 27.779 119.535 27.099C119.535 26.347 119.327 25.755 118.911 25.323C118.503 24.891 117.979 24.675 117.339 24.675C116.699 24.675 116.175 24.903 115.767 25.359C115.367 25.807 115.167 26.387 115.167 27.099C115.167 27.827 115.367 28.411 115.767 28.851ZM125.19 30.363C124.278 30.363 123.53 30.059 122.946 29.451C122.37 28.843 122.082 28.059 122.082 27.099C122.082 26.139 122.366 25.351 122.934 24.735C123.51 24.119 124.238 23.811 125.118 23.811C125.686 23.811 126.154 23.939 126.522 24.195C126.898 24.451 127.162 24.711 127.314 24.975H127.386V21.207H128.334V30.207H127.422V29.223H127.35C126.83 29.983 126.11 30.363 125.19 30.363ZM123.654 28.851C124.062 29.291 124.594 29.511 125.25 29.511C125.906 29.511 126.43 29.279 126.822 28.815C127.222 28.351 127.422 27.779 127.422 27.099C127.422 26.347 127.214 25.755 126.798 25.323C126.39 24.891 125.866 24.675 125.226 24.675C124.586 24.675 124.062 24.903 123.654 25.359C123.254 25.807 123.054 26.387 123.054 27.099C123.054 27.827 123.254 28.411 123.654 28.851ZM135.732 30.207V22.695H133.164V21.807H139.272V22.695H136.704V30.207H135.732ZM141.771 22.647C141.643 22.775 141.479 22.839 141.279 22.839C141.079 22.839 140.915 22.775 140.787 22.647C140.659 22.511 140.595 22.343 140.595 22.143C140.595 21.951 140.659 21.791 140.787 21.663C140.915 21.527 141.079 21.459 141.279 21.459C141.479 21.459 141.643 21.527 141.771 21.663C141.907 21.791 141.975 21.951 141.975 22.143C141.975 22.343 141.907 22.511 141.771 22.647ZM140.787 30.207V23.967H141.735V30.207H140.787ZM143.847 30.207V23.967H144.795V24.867H144.867C145.235 24.163 145.843 23.811 146.691 23.811C147.147 23.811 147.543 23.915 147.879 24.123C148.223 24.323 148.483 24.599 148.659 24.951H148.743C149.143 24.191 149.803 23.811 150.723 23.811C151.411 23.811 151.963 24.031 152.379 24.471C152.803 24.911 153.015 25.475 153.015 26.163V30.207H152.067V26.475C152.067 25.899 151.931 25.459 151.659 25.155C151.395 24.851 151.027 24.699 150.555 24.699C150.091 24.699 149.699 24.859 149.379 25.179C149.067 25.491 148.911 25.927 148.911 26.487V30.207H147.963V26.295C147.963 25.807 147.815 25.419 147.519 25.131C147.231 24.843 146.863 24.699 146.415 24.699C145.967 24.699 145.583 24.863 145.263 25.191C144.951 25.519 144.795 25.939 144.795 26.451V30.207H143.847ZM157.761 30.363C156.825 30.363 156.069 30.055 155.493 29.439C154.925 28.823 154.641 28.039 154.641 27.087C154.641 26.111 154.933 25.323 155.517 24.723C156.101 24.115 156.829 23.811 157.701 23.811C158.629 23.811 159.365 24.111 159.909 24.711C160.453 25.311 160.725 26.075 160.725 27.003V27.423H155.637C155.661 28.055 155.861 28.559 156.237 28.935C156.621 29.311 157.133 29.499 157.773 29.499C158.205 29.499 158.597 29.399 158.949 29.199C159.301 28.999 159.545 28.723 159.681 28.371H160.665C160.489 28.963 160.141 29.443 159.621 29.811C159.101 30.179 158.481 30.363 157.761 30.363ZM155.661 26.583H159.717C159.677 25.983 159.469 25.515 159.093 25.179C158.717 24.843 158.253 24.675 157.701 24.675C157.165 24.675 156.701 24.851 156.309 25.203C155.925 25.555 155.709 26.015 155.661 26.583Z" fill="#2755CB"/>
        <rect x="94.4976" y="15.0035" width="78.1138" height="23.4071" rx="3.26084" stroke="#2755CB" stroke-width="0.592879"/>
        <rect x="5.2691" y="3.14605" width="171.342" height="47.1223" rx="2.07508" stroke="#FAFAFA" stroke-width="0.592879"/>
        </g>
        <defs>
        <filter id="filter0_dd_1693_222500" x="0.229622" y="0.478092" width="181.421" height="57.2009" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
        <feFlood flood-opacity="0" result="BackgroundImageFix"/>
        <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
        <feOffset dy="2.37152"/>
        <feGaussianBlur stdDeviation="2.37152"/>
        <feColorMatrix type="matrix" values="0 0 0 0 0.196487 0 0 0 0 0.196487 0 0 0 0 0.279476 0 0 0 0.06 0"/>
        <feBlend mode="multiply" in2="BackgroundImageFix" result="effect1_dropShadow_1693_222500"/>
        <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
        <feOffset dy="2.37152"/>
        <feGaussianBlur stdDeviation="1.18576"/>
        <feColorMatrix type="matrix" values="0 0 0 0 0.196487 0 0 0 0 0.196487 0 0 0 0 0.279476 0 0 0 0.08 0"/>
        <feBlend mode="multiply" in2="effect1_dropShadow_1693_222500" result="effect2_dropShadow_1693_222500"/>
        <feBlend mode="normal" in="SourceGraphic" in2="effect2_dropShadow_1693_222500" result="shape"/>
        </filter>
        </defs>
        </svg>        
        </div>
        </div> 
        `
    } else if (widget_data_req.is_multi_datepicker === "true") {
        html += `
        <div class="custom-date-response-bot-preview-wrapper">
        <svg width="173" height="25" viewBox="0 0 173 25" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="9.2691" y="0.835502" width="74.1138" height="23.4071" rx="3.26084" fill="white"/>
        <path d="M16.0262 16.0391V7.63906H20.8142V8.52706H16.9982V11.4071H20.5622V12.2831H16.9982V16.0391H16.0262ZM22.4921 16.0391V9.79906H23.4281V10.9631H23.5001C23.6041 10.6591 23.8081 10.3911 24.1121 10.1591C24.4161 9.91906 24.7801 9.79906 25.2041 9.79906H25.7321V10.7471H25.2161C24.6641 10.7471 24.2281 10.9431 23.9081 11.3351C23.5961 11.7191 23.4401 12.2151 23.4401 12.8231V16.0391H22.4921ZM32.1624 15.2591C31.5464 15.8831 30.7704 16.1951 29.8344 16.1951C28.8984 16.1951 28.1224 15.8871 27.5064 15.2711C26.8904 14.6471 26.5824 13.8631 26.5824 12.9191C26.5824 11.9751 26.8944 11.1951 27.5184 10.5791C28.1424 9.95506 28.9184 9.64306 29.8464 9.64306C30.7824 9.64306 31.5584 9.95506 32.1744 10.5791C32.7904 11.2031 33.0984 11.9831 33.0984 12.9191C33.0984 13.8551 32.7864 14.6351 32.1624 15.2591ZM29.8344 15.3311C30.5064 15.3311 31.0544 15.1031 31.4784 14.6471C31.9104 14.1911 32.1264 13.6151 32.1264 12.9191C32.1264 12.2231 31.9104 11.6471 31.4784 11.1911C31.0544 10.7351 30.5064 10.5071 29.8344 10.5071C29.1704 10.5071 28.6224 10.7391 28.1904 11.2031C27.7664 11.6591 27.5544 12.2311 27.5544 12.9191C27.5544 13.6231 27.7664 14.2031 28.1904 14.6591C28.6224 15.1071 29.1704 15.3311 29.8344 15.3311ZM34.7734 16.0391V9.79906H35.7214V10.6991H35.7934C36.1614 9.99506 36.7694 9.64306 37.6174 9.64306C38.0734 9.64306 38.4694 9.74706 38.8054 9.95506C39.1494 10.1551 39.4094 10.4311 39.5854 10.7831H39.6694C40.0694 10.0231 40.7294 9.64306 41.6494 9.64306C42.3374 9.64306 42.8894 9.86306 43.3054 10.3031C43.7294 10.7431 43.9414 11.3071 43.9414 11.9951V16.0391H42.9934V12.3071C42.9934 11.7311 42.8574 11.2911 42.5854 10.9871C42.3214 10.6831 41.9534 10.5311 41.4814 10.5311C41.0174 10.5311 40.6254 10.6911 40.3054 11.0111C39.9934 11.3231 39.8374 11.7591 39.8374 12.3191V16.0391H38.8894V12.1271C38.8894 11.6391 38.7414 11.2511 38.4454 10.9631C38.1574 10.6751 37.7894 10.5311 37.3414 10.5311C36.8934 10.5311 36.5094 10.6951 36.1894 11.0231C35.8774 11.3511 35.7214 11.7711 35.7214 12.2831V16.0391H34.7734ZM49.4598 16.0391V7.63906H51.9558C53.2598 7.63906 54.2878 8.02706 55.0398 8.80306C55.7918 9.57906 56.1678 10.5911 56.1678 11.8391C56.1678 13.1511 55.7958 14.1791 55.0518 14.9231C54.3158 15.6671 53.2838 16.0391 51.9558 16.0391H49.4598ZM50.4318 15.1751H51.9558C52.9558 15.1751 53.7398 14.8831 54.3078 14.2991C54.8838 13.7071 55.1718 12.8871 55.1718 11.8391C55.1718 10.8151 54.8838 10.0071 54.3078 9.41506C53.7398 8.81506 52.9558 8.51506 51.9558 8.51506H50.4318V15.1751ZM60.4756 16.1951C59.5636 16.1951 58.8156 15.8911 58.2316 15.2831C57.6556 14.6751 57.3676 13.8911 57.3676 12.9311C57.3676 11.9711 57.6516 11.1831 58.2196 10.5671C58.7956 9.95106 59.5236 9.64306 60.4036 9.64306C60.9716 9.64306 61.4396 9.77106 61.8076 10.0271C62.1836 10.2831 62.4476 10.5431 62.5996 10.8071H62.6716V9.79906H63.6196V16.0391H62.7076V15.0551H62.6356C62.1156 15.8151 61.3956 16.1951 60.4756 16.1951ZM58.9396 14.6831C59.3476 15.1231 59.8796 15.3431 60.5356 15.3431C61.1916 15.3431 61.7156 15.1111 62.1076 14.6471C62.5076 14.1831 62.7076 13.6111 62.7076 12.9311C62.7076 12.1791 62.4996 11.5871 62.0836 11.1551C61.6756 10.7231 61.1516 10.5071 60.5116 10.5071C59.8716 10.5071 59.3476 10.7351 58.9396 11.1911C58.5396 11.6391 58.3396 12.2191 58.3396 12.9311C58.3396 13.6591 58.5396 14.2431 58.9396 14.6831ZM68.1 16.0391C67.516 16.0391 67.06 15.8791 66.732 15.5591C66.404 15.2391 66.24 14.7711 66.24 14.1551V10.6031H65.064V9.79906H66C66.2 9.79906 66.3 9.69506 66.3 9.48706V7.98706H67.188V9.79906H69.108V10.6031H67.188V14.1431C67.188 14.8551 67.512 15.2111 68.16 15.2111H69.024V16.0391H68.1ZM73.4251 16.1951C72.4891 16.1951 71.7331 15.8871 71.1571 15.2711C70.5891 14.6551 70.3051 13.8711 70.3051 12.9191C70.3051 11.9431 70.5971 11.1551 71.1811 10.5551C71.7651 9.94706 72.4931 9.64306 73.3651 9.64306C74.2931 9.64306 75.0291 9.94306 75.5731 10.5431C76.1171 11.1431 76.3891 11.9071 76.3891 12.8351V13.2551H71.3011C71.3251 13.8871 71.5251 14.3911 71.9011 14.7671C72.2851 15.1431 72.7971 15.3311 73.4371 15.3311C73.8691 15.3311 74.2611 15.2311 74.6131 15.0311C74.9651 14.8311 75.2091 14.5551 75.3451 14.2031H76.3291C76.1531 14.7951 75.8051 15.2751 75.2851 15.6431C74.7651 16.0111 74.1451 16.1951 73.4251 16.1951ZM71.3251 12.4151H75.3811C75.3411 11.8151 75.1331 11.3471 74.7571 11.0111C74.3811 10.6751 73.9171 10.5071 73.3651 10.5071C72.8291 10.5071 72.3651 10.6831 71.9731 11.0351C71.5891 11.3871 71.3731 11.8471 71.3251 12.4151Z" fill="#2755CB"/>
        <rect x="9.2691" y="0.835502" width="74.1138" height="23.4071" rx="3.26084" stroke="#2755CB" stroke-width="0.592879"/>
        <rect x="90.4976" y="0.835502" width="74.1138" height="23.4071" rx="3.26084" fill="white"/>
        <path d="M107.483 16.0391V8.52706H104.915V7.63906H111.023V8.52706H108.455V16.0391H107.483ZM116.489 15.2591C115.873 15.8831 115.097 16.1951 114.161 16.1951C113.225 16.1951 112.449 15.8871 111.833 15.2711C111.217 14.6471 110.909 13.8631 110.909 12.9191C110.909 11.9751 111.221 11.1951 111.845 10.5791C112.469 9.95506 113.245 9.64306 114.173 9.64306C115.109 9.64306 115.885 9.95506 116.501 10.5791C117.117 11.2031 117.425 11.9831 117.425 12.9191C117.425 13.8551 117.113 14.6351 116.489 15.2591ZM114.161 15.3311C114.833 15.3311 115.381 15.1031 115.805 14.6471C116.237 14.1911 116.453 13.6151 116.453 12.9191C116.453 12.2231 116.237 11.6471 115.805 11.1911C115.381 10.7351 114.833 10.5071 114.161 10.5071C113.497 10.5071 112.949 10.7391 112.517 11.2031C112.093 11.6591 111.881 12.2311 111.881 12.9191C111.881 13.6231 112.093 14.2031 112.517 14.6591C112.949 15.1071 113.497 15.3311 114.161 15.3311ZM122.583 16.0391V7.63906H125.079C126.383 7.63906 127.411 8.02706 128.163 8.80306C128.915 9.57906 129.291 10.5911 129.291 11.8391C129.291 13.1511 128.919 14.1791 128.175 14.9231C127.439 15.6671 126.407 16.0391 125.079 16.0391H122.583ZM123.555 15.1751H125.079C126.079 15.1751 126.863 14.8831 127.431 14.2991C128.007 13.7071 128.295 12.8871 128.295 11.8391C128.295 10.8151 128.007 10.0071 127.431 9.41506C126.863 8.81506 126.079 8.51506 125.079 8.51506H123.555V15.1751ZM133.599 16.1951C132.687 16.1951 131.939 15.8911 131.355 15.2831C130.779 14.6751 130.491 13.8911 130.491 12.9311C130.491 11.9711 130.775 11.1831 131.343 10.5671C131.919 9.95106 132.647 9.64306 133.527 9.64306C134.095 9.64306 134.563 9.77106 134.931 10.0271C135.307 10.2831 135.571 10.5431 135.723 10.8071H135.795V9.79906H136.743V16.0391H135.831V15.0551H135.759C135.239 15.8151 134.519 16.1951 133.599 16.1951ZM132.063 14.6831C132.471 15.1231 133.003 15.3431 133.659 15.3431C134.315 15.3431 134.839 15.1111 135.231 14.6471C135.631 14.1831 135.831 13.6111 135.831 12.9311C135.831 12.1791 135.623 11.5871 135.207 11.1551C134.799 10.7231 134.275 10.5071 133.635 10.5071C132.995 10.5071 132.471 10.7351 132.063 11.1911C131.663 11.6391 131.463 12.2191 131.463 12.9311C131.463 13.6591 131.663 14.2431 132.063 14.6831ZM141.223 16.0391C140.639 16.0391 140.183 15.8791 139.855 15.5591C139.527 15.2391 139.363 14.7711 139.363 14.1551V10.6031H138.187V9.79906H139.123C139.323 9.79906 139.423 9.69506 139.423 9.48706V7.98706H140.311V9.79906H142.231V10.6031H140.311V14.1431C140.311 14.8551 140.635 15.2111 141.283 15.2111H142.147V16.0391H141.223ZM146.548 16.1951C145.612 16.1951 144.856 15.8871 144.28 15.2711C143.712 14.6551 143.428 13.8711 143.428 12.9191C143.428 11.9431 143.72 11.1551 144.304 10.5551C144.888 9.94706 145.616 9.64306 146.488 9.64306C147.416 9.64306 148.152 9.94306 148.696 10.5431C149.24 11.1431 149.512 11.9071 149.512 12.8351V13.2551H144.424C144.448 13.8871 144.648 14.3911 145.024 14.7671C145.408 15.1431 145.92 15.3311 146.56 15.3311C146.992 15.3311 147.384 15.2311 147.736 15.0311C148.088 14.8311 148.332 14.5551 148.468 14.2031H149.452C149.276 14.7951 148.928 15.2751 148.408 15.6431C147.888 16.0111 147.268 16.1951 146.548 16.1951ZM144.448 12.4151H148.504C148.464 11.8151 148.256 11.3471 147.88 11.0111C147.504 10.6751 147.04 10.5071 146.488 10.5071C145.952 10.5071 145.488 10.6831 145.096 11.0351C144.712 11.3871 144.496 11.8471 144.448 12.4151Z" fill="#2755CB"/>
        <rect x="90.4976" y="0.835502" width="74.1138" height="23.4071" rx="3.26084" stroke="#2755CB" stroke-width="0.592879"/>
        </svg>        
        </div>
        </div>
        `
    } else if (widget_data_req.is_single_datepicker === "true") {
        html += `
        <div class="single-date-response-bot-preview-wrapper">
        <svg width="182" height="58" viewBox="0 0 182 58" fill="none" xmlns="http://www.w3.org/2000/svg">
        <g filter="url(#filter0_dd_1693_222478)">
        <rect x="4.97266" y="2.50195" width="171.935" height="47.7152" rx="2.37152" fill="white"/>
        <rect x="19.4986" y="14.4127" width="142.884" height="23.8932" rx="3.26084" fill="white"/>
        <path d="M62.6804 29.8594L65.9204 21.4594H67.0604L70.2884 29.8594H69.2684L68.5124 27.8674H64.4564L63.7004 29.8594H62.6804ZM64.7924 26.9794H68.1764L66.5204 22.5874H66.4484L64.7924 26.9794ZM74.1883 30.0154C73.2763 30.0154 72.5283 29.7114 71.9443 29.1034C71.3683 28.4954 71.0803 27.7114 71.0803 26.7514C71.0803 25.7914 71.3643 25.0034 71.9323 24.3874C72.5083 23.7714 73.2363 23.4634 74.1163 23.4634C74.6843 23.4634 75.1523 23.5914 75.5203 23.8474C75.8963 24.1034 76.1603 24.3634 76.3123 24.6274H76.3843V20.8594H77.3323V29.8594H76.4203V28.8754H76.3483C75.8283 29.6354 75.1083 30.0154 74.1883 30.0154ZM72.6523 28.5034C73.0603 28.9434 73.5923 29.1634 74.2483 29.1634C74.9043 29.1634 75.4283 28.9314 75.8203 28.4674C76.2203 28.0034 76.4203 27.4314 76.4203 26.7514C76.4203 25.9994 76.2123 25.4074 75.7963 24.9754C75.3883 24.5434 74.8643 24.3274 74.2243 24.3274C73.5843 24.3274 73.0603 24.5554 72.6523 25.0114C72.2523 25.4594 72.0523 26.0394 72.0523 26.7514C72.0523 27.4794 72.2523 28.0634 72.6523 28.5034ZM82.0759 30.0154C81.1639 30.0154 80.4159 29.7114 79.8319 29.1034C79.2559 28.4954 78.9679 27.7114 78.9679 26.7514C78.9679 25.7914 79.2519 25.0034 79.8199 24.3874C80.3959 23.7714 81.1239 23.4634 82.0039 23.4634C82.5719 23.4634 83.0399 23.5914 83.4079 23.8474C83.7839 24.1034 84.0479 24.3634 84.1999 24.6274H84.2719V20.8594H85.2199V29.8594H84.3079V28.8754H84.2359C83.7159 29.6354 82.9959 30.0154 82.0759 30.0154ZM80.5399 28.5034C80.9479 28.9434 81.4799 29.1634 82.1359 29.1634C82.7919 29.1634 83.3159 28.9314 83.7079 28.4674C84.1079 28.0034 84.3079 27.4314 84.3079 26.7514C84.3079 25.9994 84.0999 25.4074 83.6839 24.9754C83.2759 24.5434 82.7519 24.3274 82.1119 24.3274C81.4719 24.3274 80.9479 24.5554 80.5399 25.0114C80.1399 25.4594 79.9399 26.0394 79.9399 26.7514C79.9399 27.4794 80.1399 28.0634 80.5399 28.5034ZM90.8899 29.8594V21.4594H93.3859C94.6899 21.4594 95.7179 21.8474 96.4699 22.6234C97.2219 23.3994 97.5979 24.4114 97.5979 25.6594C97.5979 26.9714 97.2259 27.9994 96.4819 28.7434C95.7459 29.4874 94.7139 29.8594 93.3859 29.8594H90.8899ZM91.8619 28.9954H93.3859C94.3859 28.9954 95.1699 28.7034 95.7379 28.1194C96.3139 27.5274 96.6019 26.7074 96.6019 25.6594C96.6019 24.6354 96.3139 23.8274 95.7379 23.2354C95.1699 22.6354 94.3859 22.3354 93.3859 22.3354H91.8619V28.9954ZM101.977 30.0154C101.065 30.0154 100.317 29.7114 99.7328 29.1034C99.1568 28.4954 98.8688 27.7114 98.8688 26.7514C98.8688 25.7914 99.1528 25.0034 99.7208 24.3874C100.297 23.7714 101.025 23.4634 101.905 23.4634C102.473 23.4634 102.941 23.5914 103.309 23.8474C103.685 24.1034 103.949 24.3634 104.101 24.6274H104.173V23.6194H105.121V29.8594H104.209V28.8754H104.137C103.617 29.6354 102.897 30.0154 101.977 30.0154ZM100.441 28.5034C100.849 28.9434 101.381 29.1634 102.037 29.1634C102.693 29.1634 103.217 28.9314 103.609 28.4674C104.009 28.0034 104.209 27.4314 104.209 26.7514C104.209 25.9994 104.001 25.4074 103.585 24.9754C103.177 24.5434 102.653 24.3274 102.013 24.3274C101.373 24.3274 100.849 24.5554 100.441 25.0114C100.041 25.4594 99.8408 26.0394 99.8408 26.7514C99.8408 27.4794 100.041 28.0634 100.441 28.5034ZM109.672 29.8594C109.088 29.8594 108.632 29.6994 108.304 29.3794C107.976 29.0594 107.812 28.5914 107.812 27.9754V24.4234H106.636V23.6194H107.572C107.772 23.6194 107.872 23.5154 107.872 23.3074V21.8074H108.76V23.6194H110.68V24.4234H108.76V27.9634C108.76 28.6754 109.084 29.0314 109.732 29.0314H110.596V29.8594H109.672ZM115.069 30.0154C114.133 30.0154 113.377 29.7074 112.801 29.0914C112.233 28.4754 111.949 27.6914 111.949 26.7394C111.949 25.7634 112.241 24.9754 112.825 24.3754C113.409 23.7674 114.137 23.4634 115.009 23.4634C115.937 23.4634 116.673 23.7634 117.217 24.3634C117.761 24.9634 118.033 25.7274 118.033 26.6554V27.0754H112.945C112.969 27.7074 113.169 28.2114 113.545 28.5874C113.929 28.9634 114.441 29.1514 115.081 29.1514C115.513 29.1514 115.905 29.0514 116.257 28.8514C116.609 28.6514 116.853 28.3754 116.989 28.0234H117.973C117.797 28.6154 117.449 29.0954 116.929 29.4634C116.409 29.8314 115.789 30.0154 115.069 30.0154ZM112.969 26.2354H117.025C116.985 25.6354 116.777 25.1674 116.401 24.8314C116.025 24.4954 115.561 24.3274 115.009 24.3274C114.473 24.3274 114.009 24.5034 113.617 24.8554C113.233 25.2074 113.017 25.6674 112.969 26.2354Z" fill="#2755CB"/>
        <rect x="19.4986" y="14.4127" width="142.884" height="23.8932" rx="3.26084" stroke="#2755CB" stroke-width="0.592879"/>
        <rect x="5.2691" y="2.79839" width="171.342" height="47.1223" rx="2.07508" stroke="#FAFAFA" stroke-width="0.592879"/>
        </g>
        <defs>
        <filter id="filter0_dd_1693_222478" x="0.229622" y="0.130436" width="181.421" height="57.2009" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
        <feFlood flood-opacity="0" result="BackgroundImageFix"/>
        <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
        <feOffset dy="2.37152"/>
        <feGaussianBlur stdDeviation="2.37152"/>
        <feColorMatrix type="matrix" values="0 0 0 0 0.196487 0 0 0 0 0.196487 0 0 0 0 0.279476 0 0 0 0.06 0"/>
        <feBlend mode="multiply" in2="BackgroundImageFix" result="effect1_dropShadow_1693_222478"/>
        <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
        <feOffset dy="2.37152"/>
        <feGaussianBlur stdDeviation="1.18576"/>
        <feColorMatrix type="matrix" values="0 0 0 0 0.196487 0 0 0 0 0.196487 0 0 0 0 0.279476 0 0 0 0.08 0"/>
        <feBlend mode="multiply" in2="effect1_dropShadow_1693_222478" result="effect2_dropShadow_1693_222478"/>
        <feBlend mode="normal" in="SourceGraphic" in2="effect2_dropShadow_1693_222478" result="shape"/>
        </filter>
        </defs>
        </svg>        
        </div>
        </div> 
        `
    } else if (widget_data_req.is_multi_timepicker === "true") {
        html += `
        <div class="single-date-response-bot-preview-wrapper">
        <svg width="173" height="25" viewBox="0 0 173 25" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="9.2691" y="0.662651" width="74.1138" height="23.4071" rx="3.26084" fill="white"/>
        <path d="M16.0262 15.8662V7.46621H20.8142V8.35421H16.9982V11.2342H20.5622V12.1102H16.9982V15.8662H16.0262ZM22.5633 15.8662V9.62621H23.4993V10.7902H23.5713C23.6753 10.4862 23.8793 10.2182 24.1833 9.98621C24.4873 9.74621 24.8513 9.62621 25.2753 9.62621H25.8033V10.5742H25.2873C24.7353 10.5742 24.2993 10.7702 23.9793 11.1622C23.6673 11.5462 23.5113 12.0422 23.5113 12.6502V15.8662H22.5633ZM32.3047 15.0862C31.6887 15.7102 30.9127 16.0222 29.9767 16.0222C29.0407 16.0222 28.2647 15.7142 27.6487 15.0982C27.0327 14.4742 26.7247 13.6902 26.7247 12.7462C26.7247 11.8022 27.0367 11.0222 27.6607 10.4062C28.2847 9.78221 29.0607 9.47021 29.9887 9.47021C30.9247 9.47021 31.7007 9.78221 32.3167 10.4062C32.9327 11.0302 33.2407 11.8102 33.2407 12.7462C33.2407 13.6822 32.9287 14.4622 32.3047 15.0862ZM29.9767 15.1582C30.6487 15.1582 31.1967 14.9302 31.6207 14.4742C32.0527 14.0182 32.2687 13.4422 32.2687 12.7462C32.2687 12.0502 32.0527 11.4742 31.6207 11.0182C31.1967 10.5622 30.6487 10.3342 29.9767 10.3342C29.3127 10.3342 28.7647 10.5662 28.3327 11.0302C27.9087 11.4862 27.6967 12.0582 27.6967 12.7462C27.6967 13.4502 27.9087 14.0302 28.3327 14.4862C28.7647 14.9342 29.3127 15.1582 29.9767 15.1582ZM34.9868 15.8662V9.62621H35.9348V10.5262H36.0068C36.3748 9.82221 36.9828 9.47021 37.8308 9.47021C38.2868 9.47021 38.6828 9.57421 39.0188 9.78221C39.3628 9.98221 39.6228 10.2582 39.7988 10.6102H39.8828C40.2828 9.85021 40.9428 9.47021 41.8628 9.47021C42.5508 9.47021 43.1028 9.69021 43.5188 10.1302C43.9428 10.5702 44.1548 11.1342 44.1548 11.8222V15.8662H43.2068V12.1342C43.2068 11.5582 43.0708 11.1182 42.7988 10.8142C42.5348 10.5102 42.1668 10.3582 41.6948 10.3582C41.2308 10.3582 40.8388 10.5182 40.5188 10.8382C40.2068 11.1502 40.0508 11.5862 40.0508 12.1462V15.8662H39.1028V11.9542C39.1028 11.4662 38.9548 11.0782 38.6588 10.7902C38.3708 10.5022 38.0028 10.3582 37.5548 10.3582C37.1068 10.3582 36.7228 10.5222 36.4028 10.8502C36.0908 11.1782 35.9348 11.5982 35.9348 12.1102V15.8662H34.9868ZM51.5435 15.8662V8.35421H48.9755V7.46621H55.0835V8.35421H52.5155V15.8662H51.5435ZM57.5827 8.30621C57.4547 8.43421 57.2907 8.49821 57.0907 8.49821C56.8907 8.49821 56.7267 8.43421 56.5987 8.30621C56.4707 8.17021 56.4067 8.00221 56.4067 7.80221C56.4067 7.61021 56.4707 7.45021 56.5987 7.32221C56.7267 7.18621 56.8907 7.11821 57.0907 7.11821C57.2907 7.11821 57.4547 7.18621 57.5827 7.32221C57.7187 7.45021 57.7867 7.61021 57.7867 7.80221C57.7867 8.00221 57.7187 8.17021 57.5827 8.30621ZM56.5987 15.8662V9.62621H57.5467V15.8662H56.5987ZM59.6581 15.8662V9.62621H60.6061V10.5262H60.6781C61.0461 9.82221 61.6541 9.47021 62.5021 9.47021C62.9581 9.47021 63.3541 9.57421 63.6901 9.78221C64.0341 9.98221 64.2941 10.2582 64.4701 10.6102H64.5541C64.9541 9.85021 65.6141 9.47021 66.5341 9.47021C67.2221 9.47021 67.7741 9.69021 68.1901 10.1302C68.6141 10.5702 68.8261 11.1342 68.8261 11.8222V15.8662H67.8781V12.1342C67.8781 11.5582 67.7421 11.1182 67.4701 10.8142C67.2061 10.5102 66.8381 10.3582 66.3661 10.3582C65.9021 10.3582 65.5101 10.5182 65.1901 10.8382C64.8781 11.1502 64.7221 11.5862 64.7221 12.1462V15.8662H63.7741V11.9542C63.7741 11.4662 63.6261 11.0782 63.3301 10.7902C63.0421 10.5022 62.6741 10.3582 62.2261 10.3582C61.7781 10.3582 61.3941 10.5222 61.0741 10.8502C60.7621 11.1782 60.6061 11.5982 60.6061 12.1102V15.8662H59.6581ZM73.5724 16.0222C72.6364 16.0222 71.8804 15.7142 71.3044 15.0982C70.7364 14.4822 70.4524 13.6982 70.4524 12.7462C70.4524 11.7702 70.7444 10.9822 71.3284 10.3822C71.9124 9.77421 72.6404 9.47021 73.5124 9.47021C74.4404 9.47021 75.1764 9.77021 75.7204 10.3702C76.2644 10.9702 76.5364 11.7342 76.5364 12.6622V13.0822H71.4484C71.4724 13.7142 71.6724 14.2182 72.0484 14.5942C72.4324 14.9702 72.9444 15.1582 73.5844 15.1582C74.0164 15.1582 74.4084 15.0582 74.7604 14.8582C75.1124 14.6582 75.3564 14.3822 75.4924 14.0302H76.4764C76.3004 14.6222 75.9524 15.1022 75.4324 15.4702C74.9124 15.8382 74.2924 16.0222 73.5724 16.0222ZM71.4724 12.2422H75.5284C75.4884 11.6422 75.2804 11.1742 74.9044 10.8382C74.5284 10.5022 74.0644 10.3342 73.5124 10.3342C72.9764 10.3342 72.5124 10.5102 72.1204 10.8622C71.7364 11.2142 71.5204 11.6742 71.4724 12.2422Z" fill="#2755CB"/>
        <rect x="9.2691" y="0.662651" width="74.1138" height="23.4071" rx="3.26084" stroke="#2755CB" stroke-width="0.592879"/>
        <rect x="90.4976" y="0.662651" width="74.1138" height="23.4071" rx="3.26084" fill="white"/>
        <path d="M107.483 15.8662V8.35421H104.915V7.46621H111.023V8.35421H108.455V15.8662H107.483ZM116.56 15.0862C115.944 15.7102 115.168 16.0222 114.232 16.0222C113.296 16.0222 112.52 15.7142 111.904 15.0982C111.288 14.4742 110.98 13.6902 110.98 12.7462C110.98 11.8022 111.292 11.0222 111.916 10.4062C112.54 9.78221 113.316 9.47021 114.244 9.47021C115.18 9.47021 115.956 9.78221 116.572 10.4062C117.188 11.0302 117.496 11.8102 117.496 12.7462C117.496 13.6822 117.184 14.4622 116.56 15.0862ZM114.232 15.1582C114.904 15.1582 115.452 14.9302 115.876 14.4742C116.308 14.0182 116.524 13.4422 116.524 12.7462C116.524 12.0502 116.308 11.4742 115.876 11.0182C115.452 10.5622 114.904 10.3342 114.232 10.3342C113.568 10.3342 113.02 10.5662 112.588 11.0302C112.164 11.4862 111.952 12.0582 111.952 12.7462C111.952 13.4502 112.164 14.0302 112.588 14.4862C113.02 14.9342 113.568 15.1582 114.232 15.1582ZM124.524 15.8662V8.35421H121.956V7.46621H128.064V8.35421H125.496V15.8662H124.524ZM130.563 8.30621C130.435 8.43421 130.271 8.49821 130.071 8.49821C129.871 8.49821 129.707 8.43421 129.579 8.30621C129.451 8.17021 129.387 8.00221 129.387 7.80221C129.387 7.61021 129.451 7.45021 129.579 7.32221C129.707 7.18621 129.871 7.11821 130.071 7.11821C130.271 7.11821 130.435 7.18621 130.563 7.32221C130.699 7.45021 130.767 7.61021 130.767 7.80221C130.767 8.00221 130.699 8.17021 130.563 8.30621ZM129.579 15.8662V9.62621H130.527V15.8662H129.579ZM132.639 15.8662V9.62621H133.587V10.5262H133.659C134.027 9.82221 134.635 9.47021 135.483 9.47021C135.939 9.47021 136.335 9.57421 136.671 9.78221C137.015 9.98221 137.275 10.2582 137.451 10.6102H137.535C137.935 9.85021 138.595 9.47021 139.515 9.47021C140.203 9.47021 140.755 9.69021 141.171 10.1302C141.595 10.5702 141.807 11.1342 141.807 11.8222V15.8662H140.859V12.1342C140.859 11.5582 140.723 11.1182 140.451 10.8142C140.187 10.5102 139.819 10.3582 139.347 10.3582C138.883 10.3582 138.491 10.5182 138.171 10.8382C137.859 11.1502 137.703 11.5862 137.703 12.1462V15.8662H136.755V11.9542C136.755 11.4662 136.607 11.0782 136.311 10.7902C136.023 10.5022 135.655 10.3582 135.207 10.3582C134.759 10.3582 134.375 10.5222 134.055 10.8502C133.743 11.1782 133.587 11.5982 133.587 12.1102V15.8662H132.639ZM146.553 16.0222C145.617 16.0222 144.861 15.7142 144.285 15.0982C143.717 14.4822 143.433 13.6982 143.433 12.7462C143.433 11.7702 143.725 10.9822 144.309 10.3822C144.893 9.77421 145.621 9.47021 146.493 9.47021C147.421 9.47021 148.157 9.77021 148.701 10.3702C149.245 10.9702 149.517 11.7342 149.517 12.6622V13.0822H144.429C144.453 13.7142 144.653 14.2182 145.029 14.5942C145.413 14.9702 145.925 15.1582 146.565 15.1582C146.997 15.1582 147.389 15.0582 147.741 14.8582C148.093 14.6582 148.337 14.3822 148.473 14.0302H149.457C149.281 14.6222 148.933 15.1022 148.413 15.4702C147.893 15.8382 147.273 16.0222 146.553 16.0222ZM144.453 12.2422H148.509C148.469 11.6422 148.261 11.1742 147.885 10.8382C147.509 10.5022 147.045 10.3342 146.493 10.3342C145.957 10.3342 145.493 10.5102 145.101 10.8622C144.717 11.2142 144.501 11.6742 144.453 12.2422Z" fill="#2755CB"/>
        <rect x="90.4976" y="0.662651" width="74.1138" height="23.4071" rx="3.26084" stroke="#2755CB" stroke-width="0.592879"/>
        </svg>        
        </div>
        </div>
        `
    } else if (widget_data_req.is_single_timepicker === "true") {
        html += `
        <div class="single-date-response-bot-preview-wrapper">
        <svg width="182" height="58" viewBox="0 0 182 58" fill="none" xmlns="http://www.w3.org/2000/svg">
        <g filter="url(#filter0_dd_1693_222489)">
        <rect x="4.97266" y="2.67578" width="171.935" height="47.7152" rx="2.37152" fill="white"/>
        <rect x="19.4986" y="14.5865" width="142.884" height="23.8932" rx="3.26084" fill="white"/>
        <path d="M63.1804 30.0332L66.4204 21.6332H67.5604L70.7884 30.0332H69.7684L69.0124 28.0412H64.9564L64.2004 30.0332H63.1804ZM65.2924 27.1532H68.6764L67.0204 22.7612H66.9484L65.2924 27.1532ZM74.6883 30.1892C73.7763 30.1892 73.0283 29.8852 72.4443 29.2772C71.8683 28.6692 71.5803 27.8852 71.5803 26.9252C71.5803 25.9652 71.8643 25.1772 72.4323 24.5612C73.0083 23.9452 73.7363 23.6372 74.6163 23.6372C75.1843 23.6372 75.6523 23.7652 76.0203 24.0212C76.3963 24.2772 76.6603 24.5372 76.8123 24.8012H76.8843V21.0332H77.8323V30.0332H76.9203V29.0492H76.8483C76.3283 29.8092 75.6083 30.1892 74.6883 30.1892ZM73.1523 28.6772C73.5603 29.1172 74.0923 29.3372 74.7483 29.3372C75.4043 29.3372 75.9283 29.1052 76.3203 28.6412C76.7203 28.1772 76.9203 27.6052 76.9203 26.9252C76.9203 26.1732 76.7123 25.5812 76.2963 25.1492C75.8883 24.7172 75.3643 24.5012 74.7243 24.5012C74.0843 24.5012 73.5603 24.7292 73.1523 25.1852C72.7523 25.6332 72.5523 26.2132 72.5523 26.9252C72.5523 27.6532 72.7523 28.2372 73.1523 28.6772ZM82.5759 30.1892C81.6639 30.1892 80.9159 29.8852 80.3319 29.2772C79.7559 28.6692 79.4679 27.8852 79.4679 26.9252C79.4679 25.9652 79.7519 25.1772 80.3199 24.5612C80.8959 23.9452 81.6239 23.6372 82.5039 23.6372C83.0719 23.6372 83.5399 23.7652 83.9079 24.0212C84.2839 24.2772 84.5479 24.5372 84.6999 24.8012H84.7719V21.0332H85.7199V30.0332H84.8079V29.0492H84.7359C84.2159 29.8092 83.4959 30.1892 82.5759 30.1892ZM81.0399 28.6772C81.4479 29.1172 81.9799 29.3372 82.6359 29.3372C83.2919 29.3372 83.8159 29.1052 84.2079 28.6412C84.6079 28.1772 84.8079 27.6052 84.8079 26.9252C84.8079 26.1732 84.5999 25.5812 84.1839 25.1492C83.7759 24.7172 83.2519 24.5012 82.6119 24.5012C81.9719 24.5012 81.4479 24.7292 81.0399 25.1852C80.6399 25.6332 80.4399 26.2132 80.4399 26.9252C80.4399 27.6532 80.6399 28.2372 81.0399 28.6772ZM93.1179 30.0332V22.5212H90.5499V21.6332H96.6579V22.5212H94.0899V30.0332H93.1179ZM99.157 22.4732C99.029 22.6012 98.865 22.6652 98.665 22.6652C98.465 22.6652 98.301 22.6012 98.173 22.4732C98.045 22.3372 97.981 22.1692 97.981 21.9692C97.981 21.7772 98.045 21.6172 98.173 21.4892C98.301 21.3532 98.465 21.2852 98.665 21.2852C98.865 21.2852 99.029 21.3532 99.157 21.4892C99.293 21.6172 99.361 21.7772 99.361 21.9692C99.361 22.1692 99.293 22.3372 99.157 22.4732ZM98.173 30.0332V23.7932H99.121V30.0332H98.173ZM101.232 30.0332V23.7932H102.18V24.6932H102.252C102.62 23.9892 103.228 23.6372 104.076 23.6372C104.532 23.6372 104.928 23.7412 105.264 23.9492C105.608 24.1492 105.868 24.4252 106.044 24.7772H106.128C106.528 24.0172 107.188 23.6372 108.108 23.6372C108.796 23.6372 109.348 23.8572 109.764 24.2972C110.188 24.7372 110.4 25.3012 110.4 25.9892V30.0332H109.452V26.3012C109.452 25.7252 109.316 25.2852 109.044 24.9812C108.78 24.6772 108.412 24.5252 107.94 24.5252C107.476 24.5252 107.084 24.6852 106.764 25.0052C106.452 25.3172 106.296 25.7532 106.296 26.3132V30.0332H105.348V26.1212C105.348 25.6332 105.2 25.2452 104.904 24.9572C104.616 24.6692 104.248 24.5252 103.8 24.5252C103.352 24.5252 102.968 24.6892 102.648 25.0172C102.336 25.3452 102.18 25.7652 102.18 26.2772V30.0332H101.232ZM115.147 30.1892C114.211 30.1892 113.455 29.8812 112.879 29.2652C112.311 28.6492 112.027 27.8652 112.027 26.9132C112.027 25.9372 112.319 25.1492 112.903 24.5492C113.487 23.9412 114.215 23.6372 115.087 23.6372C116.015 23.6372 116.751 23.9372 117.295 24.5372C117.839 25.1372 118.111 25.9012 118.111 26.8292V27.2492H113.023C113.047 27.8812 113.247 28.3852 113.623 28.7612C114.007 29.1372 114.519 29.3252 115.159 29.3252C115.591 29.3252 115.983 29.2252 116.335 29.0252C116.687 28.8252 116.931 28.5492 117.067 28.1972H118.051C117.875 28.7892 117.527 29.2692 117.007 29.6372C116.487 30.0052 115.867 30.1892 115.147 30.1892ZM113.047 26.4092H117.103C117.063 25.8092 116.855 25.3412 116.479 25.0052C116.103 24.6692 115.639 24.5012 115.087 24.5012C114.551 24.5012 114.087 24.6772 113.695 25.0292C113.311 25.3812 113.095 25.8412 113.047 26.4092Z" fill="#2755CB"/>
        <rect x="19.4986" y="14.5865" width="142.884" height="23.8932" rx="3.26084" stroke="#2755CB" stroke-width="0.592879"/>
        <rect x="5.2691" y="2.97222" width="171.342" height="47.1223" rx="2.07508" stroke="#FAFAFA" stroke-width="0.592879"/>
        </g>
        <defs>
        <filter id="filter0_dd_1693_222489" x="0.229622" y="0.304264" width="181.421" height="57.2009" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
        <feFlood flood-opacity="0" result="BackgroundImageFix"/>
        <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
        <feOffset dy="2.37152"/>
        <feGaussianBlur stdDeviation="2.37152"/>
        <feColorMatrix type="matrix" values="0 0 0 0 0.196487 0 0 0 0 0.196487 0 0 0 0 0.279476 0 0 0 0.06 0"/>
        <feBlend mode="multiply" in2="BackgroundImageFix" result="effect1_dropShadow_1693_222489"/>
        <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
        <feOffset dy="2.37152"/>
        <feGaussianBlur stdDeviation="1.18576"/>
        <feColorMatrix type="matrix" values="0 0 0 0 0.196487 0 0 0 0 0.196487 0 0 0 0 0.279476 0 0 0 0.08 0"/>
        <feBlend mode="multiply" in2="effect1_dropShadow_1693_222489" result="effect2_dropShadow_1693_222489"/>
        <feBlend mode="normal" in="SourceGraphic" in2="effect2_dropShadow_1693_222489" result="shape"/>
        </filter>
        </defs>
        </svg>        
        </div>
        </div> 
        `
    }

    return html
}

function build_preview_radio_widget_response(radio_choices) {
    if (radio_choices.length === 0) {
        return ""
    }
    let html = `
    <div class="preview-user-message-wrapper">
        <div class="radio-checkbox-widget-response-bot-preview-wrapper">
    `

    for (const radio of radio_choices) {
        html += `
        <div class="radio-checkbox-widget-wrapper-item">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none"
                xmlns="http://www.w3.org/2000/svg">
                <path
                    d="M3.75 9C3.75 11.8942 6.105 14.25 9 14.25C11.8942 14.25 14.25 11.8942 14.25 9C14.25 6.10575 11.8942 3.75 9 3.75C6.105 3.75 3.75 6.10575 3.75 9ZM12.75 9C12.75 11.0677 11.0677 12.75 9 12.75C6.93225 12.75 5.25 11.0677 5.25 9C5.25 6.93225 6.93225 5.25 9 5.25C11.0677 5.25 12.75 6.93225 12.75 9Z"
                    fill="#C4C4C4" />
            </svg>
            <div style="word-break: break-word">${radio}</div>
        </div>
        `
    }

    html += `</div></div>`
    return html
}

function build_preview_checkbox_widget_response(choices) {
    if (choices.length === 0) {
        return ""
    }
    let html = `
    <div class="preview-user-message-wrapper">
        <div class="radio-checkbox-widget-response-bot-preview-wrapper">
    `

    for (const check of choices) {
        html += `
        <div class="radio-checkbox-widget-wrapper-item">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none"
                xmlns="http://www.w3.org/2000/svg">
                <path fill-rule="evenodd" clip-rule="evenodd"
                    d="M3.16055 1.77734H12.8396C13.6001 1.77734 14.2223 2.39957 14.2223 3.16006V12.8391C14.2223 13.5996 13.6001 14.2218 12.8396 14.2218H3.16055C2.40005 14.2218 1.77783 13.5996 1.77783 12.8391V3.16006C1.77783 2.39957 2.40005 1.77734 3.16055 1.77734ZM3.85207 12.839H12.1484C12.5286 12.839 12.8397 12.5279 12.8397 12.1476V3.85135C12.8397 3.4711 12.5286 3.15999 12.1484 3.15999H3.85207C3.47182 3.15999 3.16071 3.4711 3.16071 3.85135V12.1476C3.16071 12.5279 3.47182 12.839 3.85207 12.839Z"
                    fill="#CBCACA" />
            </svg>

            <div style="word-break: break-word">${check}</div>
        </div>
        `
    }

    html += `</div></div>`
    return html
}

function build_preview_dropdown_widget_response(choices) {
    if (choices.length === 0) {
        return ""
    }
    let html = `
    <div class="preview-user-message-wrapper">
        <div class="dropdown-widget-response-bot-preview-wrapper">
            <svg width="215" height="35" viewBox="0 0 215 35" fill="none"
                xmlns="http://www.w3.org/2000/svg">
                <rect x="0.596591" y="0.596591" width="213.807" height="33.0795" rx="3.63068"
                    fill="white" />
                <path
                    d="M20.6767 21.2927C19.8287 21.2927 19.1167 21.0447 18.5407 20.5487C17.9647 20.0447 17.6767 19.4087 17.6767 18.6407H18.6487C18.6487 19.1367 18.8367 19.5527 19.2127 19.8887C19.5887 20.2247 20.0887 20.3927 20.7127 20.3927C21.2727 20.3927 21.7287 20.2647 22.0807 20.0087C22.4327 19.7527 22.6087 19.4087 22.6087 18.9767C22.6087 18.4967 22.4487 18.1287 22.1287 17.8727C21.8087 17.6167 21.4207 17.4367 20.9647 17.3327C20.5087 17.2287 20.0527 17.1167 19.5967 16.9967C19.1487 16.8687 18.7647 16.6287 18.4447 16.2767C18.1247 15.9247 17.9647 15.4407 17.9647 14.8247C17.9647 14.2007 18.2087 13.6727 18.6967 13.2407C19.1847 12.8007 19.8367 12.5807 20.6527 12.5807C21.3807 12.5807 22.0207 12.7887 22.5727 13.2047C23.1327 13.6127 23.4127 14.2167 23.4127 15.0167H22.4167C22.4167 14.5287 22.2607 14.1487 21.9487 13.8767C21.6447 13.6047 21.2087 13.4687 20.6407 13.4687C20.0807 13.4687 19.6567 13.6007 19.3687 13.8647C19.0807 14.1287 18.9367 14.4487 18.9367 14.8247C18.9367 15.1287 19.0207 15.3847 19.1887 15.5927C19.3647 15.7927 19.5887 15.9447 19.8607 16.0487C20.1327 16.1527 20.4327 16.2447 20.7607 16.3247C21.0967 16.4047 21.4287 16.5007 21.7567 16.6127C22.0927 16.7167 22.3967 16.8527 22.6687 17.0207C22.9407 17.1807 23.1607 17.4247 23.3287 17.7527C23.5047 18.0727 23.5927 18.4607 23.5927 18.9167C23.5927 19.5967 23.3287 20.1647 22.8007 20.6207C22.2807 21.0687 21.5727 21.2927 20.6767 21.2927ZM27.9114 21.2927C26.9754 21.2927 26.2194 20.9847 25.6434 20.3687C25.0754 19.7527 24.7914 18.9687 24.7914 18.0167C24.7914 17.0407 25.0834 16.2527 25.6674 15.6527C26.2514 15.0447 26.9794 14.7407 27.8514 14.7407C28.7794 14.7407 29.5154 15.0407 30.0594 15.6407C30.6034 16.2407 30.8754 17.0047 30.8754 17.9327V18.3527H25.7874C25.8114 18.9847 26.0114 19.4887 26.3874 19.8647C26.7714 20.2407 27.2834 20.4287 27.9234 20.4287C28.3554 20.4287 28.7474 20.3287 29.0994 20.1287C29.4514 19.9287 29.6954 19.6527 29.8314 19.3007H30.8154C30.6394 19.8927 30.2914 20.3727 29.7714 20.7407C29.2514 21.1087 28.6314 21.2927 27.9114 21.2927ZM25.8114 17.5127H29.8674C29.8274 16.9127 29.6194 16.4447 29.2434 16.1087C28.8674 15.7727 28.4034 15.6047 27.8514 15.6047C27.3154 15.6047 26.8514 15.7807 26.4594 16.1327C26.0754 16.4847 25.8594 16.9447 25.8114 17.5127ZM33.4332 21.1367C33.0412 21.1367 32.7372 21.0207 32.5212 20.7887C32.3052 20.5567 32.1972 20.2287 32.1972 19.8047V12.1367H33.1452V19.8047C33.1452 20.1327 33.2972 20.2967 33.6012 20.2967H33.8892V21.1367H33.4332ZM38.095 21.2927C37.159 21.2927 36.403 20.9847 35.827 20.3687C35.259 19.7527 34.975 18.9687 34.975 18.0167C34.975 17.0407 35.267 16.2527 35.851 15.6527C36.435 15.0447 37.163 14.7407 38.035 14.7407C38.963 14.7407 39.699 15.0407 40.243 15.6407C40.787 16.2407 41.059 17.0047 41.059 17.9327V18.3527H35.971C35.995 18.9847 36.195 19.4887 36.571 19.8647C36.955 20.2407 37.467 20.4287 38.107 20.4287C38.539 20.4287 38.931 20.3287 39.283 20.1287C39.635 19.9287 39.879 19.6527 40.015 19.3007H40.999C40.823 19.8927 40.475 20.3727 39.955 20.7407C39.435 21.1087 38.815 21.2927 38.095 21.2927ZM35.995 17.5127H40.051C40.011 16.9127 39.803 16.4447 39.427 16.1087C39.051 15.7727 38.587 15.6047 38.035 15.6047C37.499 15.6047 37.035 15.7807 36.643 16.1327C36.259 16.4847 36.043 16.9447 35.995 17.5127ZM45.4681 21.2927C44.5321 21.2927 43.7641 20.9807 43.1641 20.3567C42.5641 19.7327 42.2641 18.9527 42.2641 18.0167C42.2641 17.0887 42.5681 16.3127 43.1761 15.6887C43.7841 15.0567 44.5441 14.7407 45.4561 14.7407C46.1521 14.7407 46.7761 14.9407 47.3281 15.3407C47.8881 15.7327 48.2481 16.2687 48.4081 16.9487H47.4241C47.2961 16.5407 47.0521 16.2167 46.6921 15.9767C46.3401 15.7287 45.9361 15.6047 45.4801 15.6047C44.8241 15.6047 44.2881 15.8367 43.8721 16.3007C43.4561 16.7567 43.2481 17.3287 43.2481 18.0167C43.2481 18.7207 43.4601 19.3007 43.8841 19.7567C44.3081 20.2047 44.8481 20.4287 45.5041 20.4287C45.9601 20.4287 46.3681 20.3047 46.7281 20.0567C47.0881 19.8087 47.3281 19.4847 47.4481 19.0847H48.4201C48.2601 19.7647 47.9041 20.3047 47.3521 20.7047C46.8001 21.0967 46.1721 21.2927 45.4681 21.2927ZM52.5394 21.1367C51.9554 21.1367 51.4994 20.9767 51.1714 20.6567C50.8434 20.3367 50.6794 19.8687 50.6794 19.2527V15.7007H49.5034V14.8967H50.4394C50.6394 14.8967 50.7394 14.7927 50.7394 14.5847V13.0847H51.6274V14.8967H53.5474V15.7007H51.6274V19.2407C51.6274 19.9527 51.9514 20.3087 52.5994 20.3087H53.4634V21.1367H52.5394ZM63.6878 20.3567C63.0718 20.9807 62.2958 21.2927 61.3598 21.2927C60.4238 21.2927 59.6478 20.9847 59.0318 20.3687C58.4158 19.7447 58.1078 18.9607 58.1078 18.0167C58.1078 17.0727 58.4198 16.2927 59.0438 15.6767C59.6678 15.0527 60.4438 14.7407 61.3718 14.7407C62.3078 14.7407 63.0838 15.0527 63.6998 15.6767C64.3158 16.3007 64.6238 17.0807 64.6238 18.0167C64.6238 18.9527 64.3118 19.7327 63.6878 20.3567ZM61.3598 20.4287C62.0318 20.4287 62.5798 20.2007 63.0038 19.7447C63.4358 19.2887 63.6518 18.7127 63.6518 18.0167C63.6518 17.3207 63.4358 16.7447 63.0038 16.2887C62.5798 15.8327 62.0318 15.6047 61.3598 15.6047C60.6958 15.6047 60.1478 15.8367 59.7158 16.3007C59.2918 16.7567 59.0798 17.3287 59.0798 18.0167C59.0798 18.7207 59.2918 19.3007 59.7158 19.7567C60.1478 20.2047 60.6958 20.4287 61.3598 20.4287ZM66.2988 21.1367V14.8967H67.2468V15.8087H67.3188C67.4628 15.5047 67.6988 15.2527 68.0268 15.0527C68.3628 14.8447 68.7628 14.7407 69.2268 14.7407C69.9388 14.7407 70.5028 14.9767 70.9188 15.4487C71.3428 15.9127 71.5547 16.5007 71.5547 17.2127V21.1367H70.6068V17.2727C70.6068 16.7847 70.4508 16.3887 70.1388 16.0847C69.8268 15.7807 69.4468 15.6287 68.9988 15.6287C68.5028 15.6287 68.0868 15.8007 67.7508 16.1447C67.4148 16.4807 67.2468 16.9047 67.2468 17.4167V21.1367H66.2988ZM76.2395 21.2927C75.3035 21.2927 74.5475 20.9847 73.9715 20.3687C73.4035 19.7527 73.1195 18.9687 73.1195 18.0167C73.1195 17.0407 73.4115 16.2527 73.9955 15.6527C74.5795 15.0447 75.3075 14.7407 76.1795 14.7407C77.1075 14.7407 77.8435 15.0407 78.3875 15.6407C78.9315 16.2407 79.2035 17.0047 79.2035 17.9327V18.3527H74.1155C74.1395 18.9847 74.3395 19.4887 74.7155 19.8647C75.0995 20.2407 75.6115 20.4287 76.2515 20.4287C76.6835 20.4287 77.0755 20.3287 77.4275 20.1287C77.7795 19.9287 78.0235 19.6527 78.1595 19.3007H79.1435C78.9675 19.8927 78.6195 20.3727 78.0995 20.7407C77.5795 21.1087 76.9595 21.2927 76.2395 21.2927ZM74.1395 17.5127H78.1955C78.1555 16.9127 77.9475 16.4447 77.5715 16.1087C77.1955 15.7727 76.7315 15.6047 76.1795 15.6047C75.6435 15.6047 75.1795 15.7807 74.7875 16.1327C74.4035 16.4847 74.1875 16.9447 74.1395 17.5127ZM89.3519 20.3567C88.7359 20.9807 87.9599 21.2927 87.0239 21.2927C86.0879 21.2927 85.3119 20.9847 84.6959 20.3687C84.0799 19.7447 83.7719 18.9607 83.7719 18.0167C83.7719 17.0727 84.0839 16.2927 84.7079 15.6767C85.3319 15.0527 86.1079 14.7407 87.0359 14.7407C87.9719 14.7407 88.7479 15.0527 89.3639 15.6767C89.9799 16.3007 90.2879 17.0807 90.2879 18.0167C90.2879 18.9527 89.9759 19.7327 89.3519 20.3567ZM87.0239 20.4287C87.6959 20.4287 88.2439 20.2007 88.6679 19.7447C89.0999 19.2887 89.3159 18.7127 89.3159 18.0167C89.3159 17.3207 89.0999 16.7447 88.6679 16.2887C88.2439 15.8327 87.6959 15.6047 87.0239 15.6047C86.3599 15.6047 85.8119 15.8367 85.3799 16.3007C84.9559 16.7567 84.7439 17.3287 84.7439 18.0167C84.7439 18.7207 84.9559 19.3007 85.3799 19.7567C85.8119 20.2047 86.3599 20.4287 87.0239 20.4287ZM92.4188 21.1367V15.7007H91.2428V14.8967H92.4188V14.1527C92.4188 13.5287 92.6148 13.0367 93.0068 12.6767C93.3988 12.3167 93.9148 12.1367 94.5548 12.1367H95.1428V12.9647H94.5428C94.1428 12.9647 93.8468 13.0767 93.6548 13.3007C93.4628 13.5167 93.3668 13.8047 93.3668 14.1647V14.8967H95.1908V15.7007H93.3668V21.1367H92.4188ZM102.614 21.1367C102.03 21.1367 101.574 20.9767 101.246 20.6567C100.918 20.3367 100.754 19.8687 100.754 19.2527V15.7007H99.5777V14.8967H100.514C100.714 14.8967 100.814 14.7927 100.814 14.5847V13.0847H101.702V14.8967H103.622V15.7007H101.702V19.2407C101.702 19.9527 102.026 20.3087 102.674 20.3087H103.538V21.1367H102.614ZM105.299 21.1367V12.1367H106.247V15.8087H106.319C106.463 15.5047 106.703 15.2527 107.039 15.0527C107.383 14.8447 107.787 14.7407 108.251 14.7407C108.963 14.7407 109.531 14.9767 109.955 15.4487C110.387 15.9207 110.603 16.5087 110.603 17.2127V21.1367H109.655V17.2727C109.655 16.7847 109.495 16.3887 109.175 16.0847C108.855 15.7807 108.471 15.6287 108.023 15.6287C107.535 15.6287 107.115 15.7927 106.763 16.1207C106.419 16.4407 106.247 16.8487 106.247 17.3447V21.1367H105.299ZM115.286 21.2927C114.35 21.2927 113.594 20.9847 113.018 20.3687C112.45 19.7527 112.166 18.9687 112.166 18.0167C112.166 17.0407 112.458 16.2527 113.042 15.6527C113.626 15.0447 114.354 14.7407 115.226 14.7407C116.154 14.7407 116.89 15.0407 117.434 15.6407C117.978 16.2407 118.25 17.0047 118.25 17.9327V18.3527H113.162C113.186 18.9847 113.386 19.4887 113.762 19.8647C114.146 20.2407 114.658 20.4287 115.298 20.4287C115.73 20.4287 116.122 20.3287 116.474 20.1287C116.826 19.9287 117.07 19.6527 117.206 19.3007H118.19C118.014 19.8927 117.666 20.3727 117.146 20.7407C116.626 21.1087 116.006 21.2927 115.286 21.2927ZM113.186 17.5127H117.242C117.202 16.9127 116.994 16.4447 116.618 16.1087C116.242 15.7727 115.778 15.6047 115.226 15.6047C114.69 15.6047 114.226 15.7807 113.834 16.1327C113.45 16.4847 113.234 16.9447 113.186 17.5127ZM123.755 21.1367V15.7007H122.579V14.8967H123.755V14.1527C123.755 13.5287 123.951 13.0367 124.343 12.6767C124.735 12.3167 125.251 12.1367 125.891 12.1367H126.479V12.9647H125.879C125.479 12.9647 125.183 13.0767 124.991 13.3007C124.799 13.5167 124.703 13.8047 124.703 14.1647V14.8967H126.527V15.7007H124.703V21.1367H123.755ZM132.887 20.3567C132.271 20.9807 131.495 21.2927 130.559 21.2927C129.623 21.2927 128.847 20.9847 128.231 20.3687C127.615 19.7447 127.307 18.9607 127.307 18.0167C127.307 17.0727 127.619 16.2927 128.243 15.6767C128.867 15.0527 129.643 14.7407 130.571 14.7407C131.507 14.7407 132.283 15.0527 132.899 15.6767C133.515 16.3007 133.823 17.0807 133.823 18.0167C133.823 18.9527 133.511 19.7327 132.887 20.3567ZM130.559 20.4287C131.231 20.4287 131.779 20.2007 132.203 19.7447C132.635 19.2887 132.851 18.7127 132.851 18.0167C132.851 17.3207 132.635 16.7447 132.203 16.2887C131.779 15.8327 131.231 15.6047 130.559 15.6047C129.895 15.6047 129.347 15.8367 128.915 16.3007C128.491 16.7567 128.279 17.3287 128.279 18.0167C128.279 18.7207 128.491 19.3007 128.915 19.7567C129.347 20.2047 129.895 20.4287 130.559 20.4287ZM136.371 21.1367C135.979 21.1367 135.675 21.0207 135.459 20.7887C135.243 20.5567 135.135 20.2287 135.135 19.8047V12.1367H136.083V19.8047C136.083 20.1327 136.235 20.2967 136.539 20.2967H136.827V21.1367H136.371ZM139.687 21.1367C139.295 21.1367 138.991 21.0207 138.775 20.7887C138.559 20.5567 138.451 20.2287 138.451 19.8047V12.1367H139.399V19.8047C139.399 20.1327 139.551 20.2967 139.855 20.2967H140.143V21.1367H139.687ZM146.809 20.3567C146.193 20.9807 145.417 21.2927 144.481 21.2927C143.545 21.2927 142.769 20.9847 142.153 20.3687C141.537 19.7447 141.229 18.9607 141.229 18.0167C141.229 17.0727 141.541 16.2927 142.165 15.6767C142.789 15.0527 143.565 14.7407 144.493 14.7407C145.429 14.7407 146.205 15.0527 146.821 15.6767C147.437 16.3007 147.745 17.0807 147.745 18.0167C147.745 18.9527 147.433 19.7327 146.809 20.3567ZM144.481 20.4287C145.153 20.4287 145.701 20.2007 146.125 19.7447C146.557 19.2887 146.773 18.7127 146.773 18.0167C146.773 17.3207 146.557 16.7447 146.125 16.2887C145.701 15.8327 145.153 15.6047 144.481 15.6047C143.817 15.6047 143.269 15.8367 142.837 16.3007C142.413 16.7567 142.201 17.3287 142.201 18.0167C142.201 18.7207 142.413 19.3007 142.837 19.7567C143.269 20.2047 143.817 20.4287 144.481 20.4287ZM150.468 21.1367L148.524 14.8967H149.556L151.068 20.0567H151.14L152.796 14.8967H153.876L155.52 20.0567H155.592L157.116 14.8967H158.148L156.192 21.1367H154.968L153.372 16.0727H153.3L151.692 21.1367H150.468ZM160.576 13.5767C160.448 13.7047 160.284 13.7687 160.084 13.7687C159.884 13.7687 159.72 13.7047 159.592 13.5767C159.464 13.4407 159.4 13.2727 159.4 13.0727C159.4 12.8807 159.464 12.7207 159.592 12.5927C159.72 12.4567 159.884 12.3887 160.084 12.3887C160.284 12.3887 160.448 12.4567 160.576 12.5927C160.712 12.7207 160.78 12.8807 160.78 13.0727C160.78 13.2727 160.712 13.4407 160.576 13.5767ZM159.592 21.1367V14.8967H160.54V21.1367H159.592ZM162.58 21.1367V14.8967H163.528V15.8087H163.6C163.744 15.5047 163.98 15.2527 164.308 15.0527C164.644 14.8447 165.044 14.7407 165.508 14.7407C166.22 14.7407 166.784 14.9767 167.2 15.4487C167.624 15.9127 167.836 16.5007 167.836 17.2127V21.1367H166.888V17.2727C166.888 16.7847 166.732 16.3887 166.42 16.0847C166.108 15.7807 165.728 15.6287 165.28 15.6287C164.784 15.6287 164.368 15.8007 164.032 16.1447C163.696 16.4807 163.528 16.9047 163.528 17.4167V21.1367H162.58ZM172.617 24.0527C171.873 24.0527 171.261 23.8727 170.781 23.5127C170.301 23.1527 170.009 22.6847 169.905 22.1087H170.805C170.885 22.4687 171.089 22.7447 171.417 22.9367C171.745 23.1287 172.145 23.2247 172.617 23.2247C173.329 23.2247 173.861 23.0407 174.213 22.6727C174.565 22.3047 174.741 21.7927 174.741 21.1367V20.1527H174.669C174.149 20.9127 173.429 21.2927 172.509 21.2927C171.597 21.2927 170.849 20.9887 170.265 20.3807C169.689 19.7727 169.401 18.9887 169.401 18.0287C169.401 17.0687 169.685 16.2807 170.253 15.6647C170.829 15.0487 171.557 14.7407 172.437 14.7407C173.005 14.7407 173.473 14.8687 173.841 15.1247C174.217 15.3807 174.481 15.6407 174.633 15.9047H174.705V14.8967H175.653V21.1367C175.653 22.0487 175.381 22.7607 174.837 23.2727C174.301 23.7927 173.561 24.0527 172.617 24.0527ZM170.973 19.7807C171.381 20.2207 171.913 20.4407 172.569 20.4407C173.225 20.4407 173.749 20.2087 174.141 19.7447C174.541 19.2807 174.741 18.7087 174.741 18.0287C174.741 17.2767 174.533 16.6847 174.117 16.2527C173.709 15.8207 173.185 15.6047 172.545 15.6047C171.905 15.6047 171.381 15.8327 170.973 16.2887C170.573 16.7367 170.373 17.3167 170.373 18.0287C170.373 18.7567 170.573 19.3407 170.973 19.7807Z"
                    fill="#4D4D4D" />
                <path
                    d="M187.537 15.3125C187.764 15.0676 188.147 15.0534 188.392 15.2808L191.409 18.1258L194.426 15.2808C194.671 15.0534 195.054 15.0676 195.281 15.3125C195.509 15.5574 195.495 15.9403 195.25 16.1677L191.821 19.395C191.589 19.6105 191.23 19.6105 190.997 19.395L187.568 16.1677C187.323 15.9403 187.309 15.5574 187.537 15.3125Z"
                    fill="#7B7A7B" />
                <rect x="0.596591" y="0.596591" width="213.807" height="33.0795" rx="3.63068"
                    stroke="#EBEBEB" stroke-width="0.806818" />
            </svg>
            <div class="dropdown-widget-response-bot-options">
                <svg width="205" height="26" viewBox="0 0 205 26" fill="none"
                    xmlns="http://www.w3.org/2000/svg">
                    <rect width="203.318" height="25.2955" rx="3.22727"
                        transform="matrix(1 0 0 -1 0.84082 25.6357)" fill="#F8F8F8" />
                    <path
                        d="M22.303 17.0335L19.7788 14.5093C20.3854 13.7811 20.6879 12.8471 20.6233 11.9016C20.5588 10.956 20.1322 10.0718 19.4323 9.43276C18.7324 8.79374 17.8131 8.44915 16.8656 8.47068C15.9181 8.49221 15.0154 8.87819 14.3452 9.54834C13.6751 10.2185 13.2891 11.1212 13.2676 12.0687C13.246 13.0162 13.5906 13.9355 14.2296 14.6354C14.8687 15.3353 15.7529 15.7619 16.6984 15.8264C17.644 15.891 18.578 15.5885 19.3062 14.9819L21.8304 17.5061L22.303 17.0335ZM13.947 12.1583C13.947 11.5633 14.1235 10.9817 14.454 10.4871C14.7845 9.99237 15.2543 9.60681 15.804 9.37913C16.3537 9.15146 16.9585 9.09188 17.542 9.20795C18.1255 9.32402 18.6615 9.61052 19.0822 10.0312C19.5029 10.4519 19.7894 10.9879 19.9055 11.5714C20.0216 12.155 19.962 12.7598 19.7343 13.3095C19.5066 13.8591 19.1211 14.3289 18.6264 14.6595C18.1317 14.99 17.5501 15.1664 16.9552 15.1664C16.1576 15.1655 15.393 14.8483 14.8291 14.2844C14.2651 13.7204 13.9479 12.9558 13.947 12.1583Z"
                        fill="#4D4D4D" />
                    <path
                        d="M33.4267 17.1443C32.5787 17.1443 31.8667 16.8963 31.2907 16.4003C30.7147 15.8963 30.4267 15.2603 30.4267 14.4923H31.3987C31.3987 14.9883 31.5867 15.4043 31.9627 15.7403C32.3387 16.0763 32.8387 16.2443 33.4627 16.2443C34.0227 16.2443 34.4787 16.1163 34.8307 15.8603C35.1827 15.6043 35.3587 15.2603 35.3587 14.8283C35.3587 14.3483 35.1987 13.9803 34.8787 13.7243C34.5587 13.4683 34.1707 13.2883 33.7147 13.1843C33.2587 13.0803 32.8027 12.9683 32.3467 12.8483C31.8987 12.7203 31.5147 12.4803 31.1947 12.1283C30.8747 11.7763 30.7147 11.2923 30.7147 10.6763C30.7147 10.0523 30.9587 9.52428 31.4467 9.09228C31.9347 8.65228 32.5867 8.43228 33.4027 8.43228C34.1307 8.43228 34.7707 8.64028 35.3227 9.05628C35.8827 9.46428 36.1627 10.0683 36.1627 10.8683H35.1667C35.1667 10.3803 35.0107 10.0003 34.6987 9.72828C34.3947 9.45628 33.9587 9.32028 33.3907 9.32028C32.8307 9.32028 32.4067 9.45228 32.1187 9.71628C31.8307 9.98028 31.6867 10.3003 31.6867 10.6763C31.6867 10.9803 31.7707 11.2363 31.9387 11.4443C32.1147 11.6443 32.3387 11.7963 32.6107 11.9003C32.8827 12.0043 33.1827 12.0963 33.5107 12.1763C33.8467 12.2563 34.1787 12.3523 34.5067 12.4643C34.8427 12.5683 35.1467 12.7043 35.4187 12.8723C35.6907 13.0323 35.9107 13.2763 36.0787 13.6043C36.2547 13.9243 36.3427 14.3123 36.3427 14.7683C36.3427 15.4483 36.0787 16.0163 35.5507 16.4723C35.0307 16.9203 34.3227 17.1443 33.4267 17.1443ZM40.6614 17.1443C39.7254 17.1443 38.9694 16.8363 38.3934 16.2203C37.8254 15.6043 37.5414 14.8203 37.5414 13.8683C37.5414 12.8923 37.8334 12.1043 38.4174 11.5043C39.0014 10.8963 39.7294 10.5923 40.6014 10.5923C41.5294 10.5923 42.2654 10.8923 42.8094 11.4923C43.3534 12.0923 43.6254 12.8563 43.6254 13.7843V14.2043H38.5374C38.5614 14.8363 38.7614 15.3403 39.1374 15.7163C39.5214 16.0923 40.0334 16.2803 40.6734 16.2803C41.1054 16.2803 41.4974 16.1803 41.8494 15.9803C42.2014 15.7803 42.4454 15.5043 42.5814 15.1523H43.5654C43.3894 15.7443 43.0414 16.2243 42.5214 16.5923C42.0014 16.9603 41.3814 17.1443 40.6614 17.1443ZM38.5614 13.3643H42.6174C42.5774 12.7643 42.3694 12.2963 41.9934 11.9603C41.6174 11.6243 41.1534 11.4563 40.6014 11.4563C40.0654 11.4563 39.6014 11.6323 39.2094 11.9843C38.8254 12.3363 38.6094 12.7963 38.5614 13.3643ZM47.9385 17.1443C47.0265 17.1443 46.2785 16.8403 45.6945 16.2323C45.1185 15.6243 44.8305 14.8403 44.8305 13.8803C44.8305 12.9203 45.1145 12.1323 45.6825 11.5163C46.2585 10.9003 46.9865 10.5923 47.8665 10.5923C48.4345 10.5923 48.9025 10.7203 49.2705 10.9763C49.6465 11.2323 49.9105 11.4923 50.0625 11.7563H50.1345V10.7483H51.0825V16.9883H50.1705V16.0043H50.0985C49.5785 16.7643 48.8585 17.1443 47.9385 17.1443ZM46.4025 15.6323C46.8105 16.0723 47.3425 16.2923 47.9985 16.2923C48.6545 16.2923 49.1785 16.0603 49.5705 15.5963C49.9705 15.1323 50.1705 14.5603 50.1705 13.8803C50.1705 13.1283 49.9625 12.5363 49.5465 12.1043C49.1385 11.6723 48.6145 11.4563 47.9745 11.4563C47.3345 11.4563 46.8105 11.6843 46.4025 12.1403C46.0025 12.5883 45.8025 13.1683 45.8025 13.8803C45.8025 14.6083 46.0025 15.1923 46.4025 15.6323ZM53.1269 16.9883V10.7483H54.0629V11.9123H54.1349C54.2389 11.6083 54.4429 11.3403 54.7469 11.1083C55.0509 10.8683 55.4149 10.7483 55.8389 10.7483H56.3669V11.6963H55.8509C55.2989 11.6963 54.8629 11.8923 54.5429 12.2843C54.2309 12.6683 54.0749 13.1643 54.0749 13.7723V16.9883H53.1269ZM60.4212 17.1443C59.4852 17.1443 58.7172 16.8323 58.1172 16.2083C57.5172 15.5843 57.2172 14.8043 57.2172 13.8683C57.2172 12.9403 57.5212 12.1643 58.1292 11.5403C58.7372 10.9083 59.4972 10.5923 60.4092 10.5923C61.1052 10.5923 61.7292 10.7923 62.2812 11.1923C62.8412 11.5843 63.2012 12.1203 63.3612 12.8003H62.3772C62.2492 12.3923 62.0052 12.0683 61.6452 11.8283C61.2932 11.5803 60.8892 11.4563 60.4332 11.4563C59.7772 11.4563 59.2412 11.6883 58.8252 12.1523C58.4092 12.6083 58.2012 13.1803 58.2012 13.8683C58.2012 14.5723 58.4132 15.1523 58.8372 15.6083C59.2612 16.0563 59.8012 16.2803 60.4572 16.2803C60.9132 16.2803 61.3212 16.1563 61.6812 15.9083C62.0412 15.6603 62.2812 15.3363 62.4012 14.9363H63.3732C63.2132 15.6163 62.8572 16.1563 62.3052 16.5563C61.7532 16.9483 61.1252 17.1443 60.4212 17.1443ZM65.0566 16.9883V7.98828H66.0046V11.6603H66.0766C66.2206 11.3563 66.4606 11.1043 66.7966 10.9043C67.1406 10.6963 67.5446 10.5923 68.0086 10.5923C68.7206 10.5923 69.2886 10.8283 69.7126 11.3003C70.1446 11.7723 70.3606 12.3603 70.3606 13.0643V16.9883H69.4126V13.1243C69.4126 12.6363 69.2526 12.2403 68.9326 11.9363C68.6126 11.6323 68.2286 11.4803 67.7806 11.4803C67.2926 11.4803 66.8726 11.6443 66.5206 11.9723C66.1766 12.2923 66.0046 12.7003 66.0046 13.1963V16.9883H65.0566ZM78.2035 16.9883C77.6195 16.9883 77.1635 16.8283 76.8355 16.5083C76.5075 16.1883 76.3435 15.7203 76.3435 15.1043V11.5523H75.1675V10.7483H76.1035C76.3035 10.7483 76.4035 10.6443 76.4035 10.4363V8.93628H77.2915V10.7483H79.2115V11.5523H77.2915V15.0923C77.2915 15.8043 77.6155 16.1603 78.2635 16.1603H79.1275V16.9883H78.2035ZM80.7806 19.7483V18.8843H81.2486C81.8246 18.8843 82.2126 18.6163 82.4126 18.0803L82.7006 17.3243L80.1686 10.7483H81.2246L83.1566 16.0283H83.2286L85.1726 10.7483H86.2406L83.2646 18.4163C83.0966 18.8643 82.8686 19.1963 82.5806 19.4123C82.3006 19.6363 81.9166 19.7483 81.4286 19.7483H80.7806ZM87.6855 19.7483V10.7483H88.5975V11.7323H88.6695C89.1895 10.9723 89.9095 10.5923 90.8295 10.5923C91.7415 10.5923 92.4855 10.8963 93.0615 11.5043C93.6455 12.1123 93.9375 12.8963 93.9375 13.8563C93.9375 14.8163 93.6495 15.6043 93.0735 16.2203C92.5055 16.8363 91.7815 17.1443 90.9015 17.1443C90.3335 17.1443 89.8615 17.0163 89.4855 16.7603C89.1175 16.5043 88.8575 16.2443 88.7055 15.9803H88.6335V19.7483H87.6855ZM89.2095 15.6323C89.6255 16.0643 90.1535 16.2803 90.7935 16.2803C91.4335 16.2803 91.9535 16.0563 92.3535 15.6083C92.7615 15.1523 92.9655 14.5683 92.9655 13.8563C92.9655 13.1283 92.7615 12.5443 92.3535 12.1043C91.9535 11.6643 91.4255 11.4443 90.7695 11.4443C90.1135 11.4443 89.5855 11.6763 89.1855 12.1403C88.7935 12.6043 88.5975 13.1763 88.5975 13.8563C88.5975 14.6083 88.8015 15.2003 89.2095 15.6323ZM98.2591 17.1443C97.3231 17.1443 96.5671 16.8363 95.9911 16.2203C95.4231 15.6043 95.1391 14.8203 95.1391 13.8683C95.1391 12.8923 95.4311 12.1043 96.0151 11.5043C96.5991 10.8963 97.3271 10.5923 98.1991 10.5923C99.1271 10.5923 99.8631 10.8923 100.407 11.4923C100.951 12.0923 101.223 12.8563 101.223 13.7843V14.2043H96.1351C96.1591 14.8363 96.3591 15.3403 96.7351 15.7163C97.1191 16.0923 97.6311 16.2803 98.2711 16.2803C98.7031 16.2803 99.0951 16.1803 99.4471 15.9803C99.7991 15.7803 100.043 15.5043 100.179 15.1523H101.163C100.987 15.7443 100.639 16.2243 100.119 16.5923C99.5991 16.9603 98.9791 17.1443 98.2591 17.1443ZM96.1591 13.3643H100.215C100.175 12.7643 99.9671 12.2963 99.5911 11.9603C99.2151 11.6243 98.7511 11.4563 98.1991 11.4563C97.6631 11.4563 97.1991 11.6323 96.8071 11.9843C96.4231 12.3363 96.2071 12.7963 96.1591 13.3643Z"
                        fill="#4D4D4D" />
                </svg>

                <ul>
    `

    for (const drop of choices) {
        html += `
            <li style="word-break: break-word">${drop}</li>
        `
    }

    html += `</div></ul></div></div>`
    return html
}

function build_preview_video_widget_response() {
    if (!$("#checkbox-intent-video-recorder").prop("checked")) {
        return ""
    }
    let html = `
    <div class="preview-user-message-wrapper">
        <div class="video-widget-response-bot-preview-wrapper">
            <svg width="212" height="159" viewBox="0 0 212 159" fill="none"
                xmlns="http://www.w3.org/2000/svg">
                <rect width="212" height="129.962" rx="1.28485" fill="#2D2D2D" />
                <rect x="9.74683" y="112.903" width="191.693" height="2.43678" rx="1.21839"
                    fill="#C4C4C4" />
                <path fill-rule="evenodd" clip-rule="evenodd"
                    d="M134.23 94.1183L131.095 96.9655L129.589 96.9655C129.011 96.9655 128.784 97.5078 128.744 97.779L128.805 100.219C128.854 100.87 129.307 101.033 129.527 101.033H131.095L134.622 104.287C135.562 104.938 136.059 104.016 136.189 103.473V94.525C135.876 93.2234 134.752 93.7115 134.23 94.1183ZM137.254 96.6476C137.485 96.4881 137.801 96.5457 137.961 96.7763C138.256 97.2033 138.598 97.9263 138.698 98.7578C138.801 99.6019 138.655 100.582 137.934 101.451C137.755 101.666 137.435 101.696 137.219 101.517C137.003 101.338 136.973 101.018 137.153 100.802C137.657 100.194 137.767 99.5126 137.69 98.8798C137.612 98.2345 137.341 97.6653 137.126 97.3539C136.966 97.1233 137.024 96.8071 137.254 96.6476ZM139.288 94.7102C139.108 94.4944 138.788 94.4647 138.573 94.6438C138.357 94.8229 138.327 95.1429 138.506 95.3587C139.428 96.4693 140.765 99.5641 138.479 102.868C138.32 103.099 138.378 103.415 138.608 103.575C138.839 103.734 139.155 103.676 139.314 103.446C141.932 99.6611 140.409 96.0609 139.288 94.7102Z"
                    fill="#7B7A7B" />
                <path
                    d="M162.808 94.2236C161.714 94.2236 160.828 95.1101 160.828 96.2035V98.0311C160.828 98.2834 161.032 98.488 161.285 98.488C161.537 98.488 161.741 98.2834 161.741 98.0311V96.2035C161.741 95.6147 162.219 95.1374 162.808 95.1374H164.635C164.887 95.1374 165.092 94.9329 165.092 94.6805C165.092 94.4282 164.887 94.2236 164.635 94.2236H162.808Z"
                    fill="#7B7A7B" />
                <path
                    d="M166.767 94.2236C166.515 94.2236 166.31 94.4282 166.31 94.6805C166.31 94.9329 166.515 95.1374 166.767 95.1374H168.595C169.184 95.1374 169.661 95.6147 169.661 96.2035V98.0311C169.661 98.2834 169.866 98.488 170.118 98.488C170.37 98.488 170.575 98.2834 170.575 98.0311V96.2035C170.575 95.1101 169.688 94.2236 168.595 94.2236H166.767Z"
                    fill="#7B7A7B" />
                <path
                    d="M161.285 99.7064C161.537 99.7064 161.741 99.911 161.741 100.163V101.991C161.741 102.58 162.219 103.057 162.808 103.057H164.635C164.887 103.057 165.092 103.262 165.092 103.514C165.092 103.766 164.887 103.971 164.635 103.971H162.808C161.714 103.971 160.828 103.084 160.828 101.991V100.163C160.828 99.911 161.032 99.7064 161.285 99.7064Z"
                    fill="#7B7A7B" />
                <path
                    d="M170.575 100.163C170.575 99.911 170.37 99.7064 170.118 99.7064C169.866 99.7064 169.661 99.911 169.661 100.163V101.991C169.661 102.58 169.184 103.057 168.595 103.057H166.767C166.515 103.057 166.31 103.262 166.31 103.514C166.31 103.766 166.515 103.971 166.767 103.971H168.595C169.688 103.971 170.575 103.084 170.575 101.991V100.163Z"
                    fill="#7B7A7B" />
                <circle cx="194.943" cy="99.0965" r="1.08301"
                    transform="rotate(89.9055 194.943 99.0965)" fill="#7B7A7B" />
                <circle cx="194.937" cy="95.3065" r="1.08301"
                    transform="rotate(89.9055 194.937 95.3065)" fill="#7B7A7B" />
                <circle cx="194.949" cy="102.888" r="1.08301"
                    transform="rotate(89.9055 194.949 102.888)" fill="#7B7A7B" />
                <path
                    d="M30.1175 100.74V97.6252C30.1175 97.1033 30.2452 96.6443 30.5007 96.2482C30.7598 95.8484 31.0855 95.5504 31.4779 95.3542C31.874 95.1543 32.2997 95.0544 32.755 95.0544C33.214 95.0544 33.6416 95.1543 34.0376 95.3542C34.4337 95.5504 34.7595 95.8484 35.0149 96.2482C35.274 96.6443 35.4036 97.1033 35.4036 97.6252V100.74C35.4036 101.262 35.274 101.723 35.0149 102.123C34.7595 102.519 34.4337 102.817 34.0376 103.017C33.6416 103.213 33.214 103.311 32.755 103.311C32.2997 103.311 31.874 103.213 31.4779 103.017C31.0855 102.817 30.7598 102.519 30.5007 102.123C30.2452 101.723 30.1175 101.262 30.1175 100.74ZM31.3224 100.668C31.3224 101.101 31.4557 101.456 31.7222 101.734C31.9925 102.012 32.3367 102.151 32.755 102.151C33.177 102.151 33.5231 102.012 33.7933 101.734C34.0636 101.456 34.1987 101.101 34.1987 100.668V97.6919C34.1987 97.2662 34.0617 96.9145 33.7878 96.6369C33.5176 96.3555 33.1733 96.2149 32.755 96.2149C32.3441 96.2149 32.0017 96.3555 31.7278 96.6369C31.4576 96.9145 31.3224 97.2662 31.3224 97.6919V100.668ZM37.2914 103.1C37.1397 102.956 37.0638 102.78 37.0638 102.573C37.0638 102.365 37.1397 102.188 37.2914 102.04C37.4432 101.891 37.6228 101.817 37.83 101.817C38.0447 101.817 38.2224 101.891 38.3631 102.04C38.5075 102.184 38.5796 102.362 38.5796 102.573C38.5796 102.784 38.5075 102.959 38.3631 103.1C38.2224 103.241 38.0447 103.311 37.83 103.311C37.6228 103.311 37.4432 103.241 37.2914 103.1ZM37.2914 98.8746C37.1397 98.7265 37.0638 98.5488 37.0638 98.3415C37.0638 98.1342 37.1397 97.9602 37.2914 97.8196C37.4432 97.6752 37.6228 97.603 37.83 97.603C38.0447 97.603 38.2224 97.6734 38.3631 97.814C38.5075 97.9547 38.5796 98.1305 38.5796 98.3415C38.5796 98.5525 38.5075 98.7302 38.3631 98.8746C38.2224 99.0189 38.0447 99.0911 37.83 99.0911C37.6228 99.0911 37.4432 99.0189 37.2914 98.8746ZM40.2565 100.74V97.6252C40.2565 97.1033 40.3842 96.6443 40.6396 96.2482C40.8988 95.8484 41.2245 95.5504 41.6169 95.3542C42.013 95.1543 42.4387 95.0544 42.894 95.0544C43.353 95.0544 43.7805 95.1543 44.1766 95.3542C44.5727 95.5504 44.8985 95.8484 45.1539 96.2482C45.413 96.6443 45.5426 97.1033 45.5426 97.6252V100.74C45.5426 101.262 45.413 101.723 45.1539 102.123C44.8985 102.519 44.5727 102.817 44.1766 103.017C43.7805 103.213 43.353 103.311 42.894 103.311C42.4387 103.311 42.013 103.213 41.6169 103.017C41.2245 102.817 40.8988 102.519 40.6396 102.123C40.3842 101.723 40.2565 101.262 40.2565 100.74ZM41.4614 100.668C41.4614 101.101 41.5947 101.456 41.8612 101.734C42.1314 102.012 42.4757 102.151 42.894 102.151C43.316 102.151 43.6621 102.012 43.9323 101.734C44.2025 101.456 44.3377 101.101 44.3377 100.668V97.6919C44.3377 97.2662 44.2007 96.9145 43.9268 96.6369C43.6565 96.3555 43.3123 96.2149 42.894 96.2149C42.4831 96.2149 42.1407 96.3555 41.8668 96.6369C41.5965 96.9145 41.4614 97.2662 41.4614 97.6919V100.668ZM47.2861 100.74V97.6252C47.2861 97.1033 47.4138 96.6443 47.6692 96.2482C47.9283 95.8484 48.2541 95.5504 48.6464 95.3542C49.0425 95.1543 49.4682 95.0544 49.9235 95.0544C50.3825 95.0544 50.8101 95.1543 51.2062 95.3542C51.6023 95.5504 51.928 95.8484 52.1834 96.2482C52.4425 96.6443 52.5721 97.1033 52.5721 97.6252V100.74C52.5721 101.262 52.4425 101.723 52.1834 102.123C51.928 102.519 51.6023 102.817 51.2062 103.017C50.8101 103.213 50.3825 103.311 49.9235 103.311C49.4682 103.311 49.0425 103.213 48.6464 103.017C48.2541 102.817 47.9283 102.519 47.6692 102.123C47.4138 101.723 47.2861 101.262 47.2861 100.74ZM48.491 100.668C48.491 101.101 48.6242 101.456 48.8908 101.734C49.161 102.012 49.5052 102.151 49.9235 102.151C50.3455 102.151 50.6916 102.012 50.9619 101.734C51.2321 101.456 51.3672 101.101 51.3672 100.668V97.6919C51.3672 97.2662 51.2302 96.9145 50.9563 96.6369C50.6861 96.3555 50.3418 96.2149 49.9235 96.2149C49.5126 96.2149 49.1702 96.3555 48.8963 96.6369C48.6261 96.9145 48.491 97.2662 48.491 97.6919V100.668Z"
                    fill="white" />
                <g clip-path="url(#clip0_1512_243563)">
                    <path
                        d="M13.6934 96.3623L14.3703 106.173L16.7761 103L20.7523 103.209L13.6934 96.3623Z"
                        stroke="#CBCACA" stroke-width="1.04347" stroke-linecap="round"
                        stroke-linejoin="round" />
                    <path d="M16.9114 103.291L18.8421 107.448" stroke="#CBCACA"
                        stroke-width="1.04347" stroke-linecap="round" stroke-linejoin="round" />
                </g>
                <path
                    d="M0 140.532C0 139.112 1.15049 137.962 2.5697 137.962H46.897C48.3162 137.962 49.4667 139.112 49.4667 140.532V155.95C49.4667 157.369 48.3162 158.519 46.897 158.519H2.5697C1.15049 158.519 0 157.369 0 155.95V140.532Z"
                    fill="#3884FD" />
                <path
                    d="M16.9493 151.348C16.4876 151.348 16.0829 151.267 15.7351 151.105C15.3874 150.943 15.1146 150.713 14.9167 150.413C14.7248 150.113 14.6259 149.756 14.6199 149.343H15.6272C15.6332 149.678 15.7501 149.963 15.978 150.197C16.2058 150.431 16.5266 150.548 16.9403 150.548C17.3061 150.548 17.5909 150.461 17.7947 150.287C18.0046 150.107 18.1095 149.879 18.1095 149.603C18.1095 149.381 18.0586 149.202 17.9566 149.064C17.8607 148.926 17.7258 148.812 17.5519 148.722C17.384 148.632 17.1892 148.551 16.9673 148.479C16.7455 148.407 16.5116 148.329 16.2658 148.245C15.7801 148.083 15.4144 147.874 15.1685 147.616C14.9287 147.358 14.8088 147.019 14.8088 146.599C14.8028 146.246 14.8837 145.937 15.0516 145.673C15.2255 145.409 15.4653 145.205 15.7711 145.061C16.0829 144.911 16.4457 144.837 16.8594 144.837C17.2671 144.837 17.6239 144.911 17.9297 145.061C18.2414 145.211 18.4843 145.421 18.6582 145.691C18.8321 145.955 18.922 146.264 18.928 146.617H17.9207C17.9207 146.455 17.8787 146.303 17.7947 146.159C17.7108 146.009 17.5879 145.886 17.426 145.79C17.2641 145.694 17.0662 145.646 16.8324 145.646C16.5326 145.64 16.2838 145.715 16.0859 145.871C15.894 146.027 15.7981 146.243 15.7981 146.518C15.7981 146.764 15.87 146.953 16.0139 147.085C16.1579 147.217 16.3557 147.328 16.6075 147.418C16.8594 147.502 17.1472 147.601 17.471 147.715C17.7828 147.817 18.0616 147.939 18.3074 148.083C18.5532 148.227 18.7481 148.416 18.892 148.65C19.0419 148.884 19.1169 149.181 19.1169 149.54C19.1169 149.858 19.0359 150.155 18.874 150.431C18.7121 150.701 18.4693 150.922 18.1455 151.096C17.8217 151.264 17.423 151.348 16.9493 151.348ZM21.9939 151.24C21.5562 151.24 21.2085 151.135 20.9506 150.925C20.6928 150.71 20.5639 150.329 20.5639 149.783V147.58H19.7994V146.779H20.5639L20.6808 145.646H21.5173V146.779H22.7764V147.58H21.5173V149.783C21.5173 150.029 21.5682 150.2 21.6702 150.296C21.7781 150.386 21.961 150.431 22.2188 150.431H22.7314V151.24H21.9939ZM25.2704 151.348C24.8927 151.348 24.5809 151.285 24.335 151.159C24.0892 151.033 23.9063 150.868 23.7864 150.665C23.6665 150.455 23.6065 150.227 23.6065 149.981C23.6065 149.549 23.7744 149.208 24.1102 148.956C24.446 148.704 24.9256 148.578 25.5492 148.578H26.7184V148.497C26.7184 148.149 26.6225 147.888 26.4306 147.715C26.2447 147.541 26.0019 147.454 25.7021 147.454C25.4383 147.454 25.2074 147.52 25.0096 147.652C24.8177 147.778 24.7008 147.966 24.6588 148.218H23.7055C23.7354 147.894 23.8434 147.619 24.0292 147.391C24.2211 147.157 24.4609 146.98 24.7488 146.86C25.0426 146.734 25.3633 146.671 25.7111 146.671C26.3347 146.671 26.8174 146.836 27.1591 147.166C27.5009 147.49 27.6718 147.933 27.6718 148.497V151.24H26.8443L26.7634 150.476C26.6375 150.722 26.4546 150.928 26.2148 151.096C25.9749 151.264 25.6601 151.348 25.2704 151.348ZM25.4593 150.575C25.7171 150.575 25.933 150.515 26.1068 150.395C26.2867 150.269 26.4246 150.104 26.5206 149.9C26.6225 149.696 26.6854 149.471 26.7094 149.226H25.6481C25.2704 149.226 25.0006 149.292 24.8387 149.423C24.6828 149.555 24.6048 149.72 24.6048 149.918C24.6048 150.122 24.6798 150.284 24.8297 150.404C24.9856 150.518 25.1955 150.575 25.4593 150.575ZM28.7834 151.24V146.779H29.6378L29.7187 147.625C29.8746 147.331 30.0905 147.1 30.3663 146.932C30.6481 146.758 30.9869 146.671 31.3826 146.671V147.67H31.1218C30.858 147.67 30.6211 147.715 30.4113 147.805C30.2074 147.888 30.0425 148.035 29.9166 148.245C29.7967 148.449 29.7367 148.734 29.7367 149.1V151.24H28.7834ZM34.0708 151.24C33.6331 151.24 33.2853 151.135 33.0275 150.925C32.7696 150.71 32.6407 150.329 32.6407 149.783V147.58H31.8762V146.779H32.6407L32.7576 145.646H33.5941V146.779H34.8532V147.58H33.5941V149.783C33.5941 150.029 33.645 150.2 33.747 150.296C33.8549 150.386 34.0378 150.431 34.2956 150.431H34.8083V151.24H34.0708Z"
                    fill="white" />
                <path
                    d="M57.1758 140.532C57.1758 139.112 58.3263 137.962 59.7455 137.962H104.073C105.492 137.962 106.642 139.112 106.642 140.532V155.95C106.642 157.369 105.492 158.519 104.073 158.519H59.7455C58.3263 158.519 57.1758 157.369 57.1758 155.95V140.532Z"
                    fill="#F6F6F6" />
                <path
                    d="M74.6521 151.348C74.1904 151.348 73.7857 151.267 73.4379 151.105C73.0901 150.943 72.8173 150.713 72.6195 150.413C72.4276 150.113 72.3287 149.756 72.3227 149.343H73.33C73.336 149.678 73.4529 149.963 73.6807 150.197C73.9086 150.431 74.2294 150.548 74.6431 150.548C75.0088 150.548 75.2937 150.461 75.4975 150.287C75.7074 150.107 75.8123 149.879 75.8123 149.603C75.8123 149.381 75.7613 149.202 75.6594 149.064C75.5635 148.926 75.4286 148.812 75.2547 148.722C75.0868 148.632 74.8919 148.551 74.6701 148.479C74.4482 148.407 74.2144 148.329 73.9686 148.245C73.4829 148.083 73.1171 147.874 72.8713 147.616C72.6315 147.358 72.5115 147.019 72.5115 146.599C72.5055 146.246 72.5865 145.937 72.7544 145.673C72.9283 145.409 73.1681 145.205 73.4739 145.061C73.7857 144.911 74.1484 144.837 74.5622 144.837C74.9699 144.837 75.3266 144.911 75.6324 145.061C75.9442 145.211 76.1871 145.421 76.3609 145.691C76.5348 145.955 76.6248 146.264 76.6308 146.617H75.6234C75.6234 146.455 75.5815 146.303 75.4975 146.159C75.4136 146.009 75.2907 145.886 75.1288 145.79C74.9669 145.694 74.769 145.646 74.5352 145.646C74.2354 145.64 73.9865 145.715 73.7887 145.871C73.5968 146.027 73.5009 146.243 73.5009 146.518C73.5009 146.764 73.5728 146.953 73.7167 147.085C73.8606 147.217 74.0585 147.328 74.3103 147.418C74.5622 147.502 74.85 147.601 75.1737 147.715C75.4855 147.817 75.7643 147.939 76.0102 148.083C76.256 148.227 76.4509 148.416 76.5948 148.65C76.7447 148.884 76.8196 149.181 76.8196 149.54C76.8196 149.858 76.7387 150.155 76.5768 150.431C76.4149 150.701 76.1721 150.922 75.8483 151.096C75.5245 151.264 75.1258 151.348 74.6521 151.348ZM79.6967 151.24C79.259 151.24 78.9112 151.135 78.6534 150.925C78.3956 150.71 78.2667 150.329 78.2667 149.783V147.58H77.5022V146.779H78.2667L78.3836 145.646H79.22V146.779H80.4792V147.58H79.22V149.783C79.22 150.029 79.271 150.2 79.3729 150.296C79.4809 150.386 79.6637 150.431 79.9216 150.431H80.4342V151.24H79.6967ZM83.4346 151.348C83.0089 151.348 82.6251 151.252 82.2834 151.06C81.9476 150.862 81.6808 150.59 81.4829 150.242C81.285 149.888 81.1861 149.477 81.1861 149.01C81.1861 148.542 81.285 148.134 81.4829 147.787C81.6868 147.433 81.9596 147.16 82.3014 146.968C82.6431 146.77 83.0239 146.671 83.4436 146.671C83.8693 146.671 84.2501 146.77 84.5858 146.968C84.9276 147.16 85.1974 147.433 85.3953 147.787C85.5991 148.134 85.7011 148.542 85.7011 149.01C85.7011 149.477 85.5991 149.888 85.3953 150.242C85.1974 150.59 84.9276 150.862 84.5858 151.06C84.2441 151.252 83.8603 151.348 83.4346 151.348ZM83.4346 150.53C83.6624 150.53 83.8723 150.473 84.0642 150.359C84.262 150.245 84.4209 150.077 84.5409 149.855C84.6608 149.627 84.7207 149.346 84.7207 149.01C84.7207 148.674 84.6608 148.395 84.5409 148.173C84.4269 147.945 84.271 147.775 84.0732 147.661C83.8813 147.547 83.6714 147.49 83.4436 147.49C83.2157 147.49 83.0029 147.547 82.805 147.661C82.6132 147.775 82.4573 147.945 82.3373 148.173C82.2174 148.395 82.1575 148.674 82.1575 149.01C82.1575 149.346 82.2174 149.627 82.3373 149.855C82.4573 150.077 82.6132 150.245 82.805 150.359C82.9969 150.473 83.2068 150.53 83.4346 150.53ZM86.7321 153.219V146.779H87.5865L87.6854 147.472C87.8293 147.262 88.0272 147.076 88.279 146.914C88.5309 146.752 88.8546 146.671 89.2504 146.671C89.6821 146.671 90.0628 146.773 90.3926 146.977C90.7224 147.181 90.9802 147.46 91.1661 147.814C91.358 148.167 91.4539 148.569 91.4539 149.019C91.4539 149.468 91.358 149.87 91.1661 150.224C90.9802 150.572 90.7224 150.847 90.3926 151.051C90.0628 151.249 89.6791 151.348 89.2414 151.348C88.8936 151.348 88.5848 151.279 88.315 151.141C88.0512 151.003 87.8413 150.809 87.6854 150.557V153.219H86.7321ZM89.0795 150.521C89.4872 150.521 89.823 150.383 90.0868 150.107C90.3506 149.825 90.4825 149.459 90.4825 149.01C90.4825 148.716 90.4226 148.455 90.3027 148.227C90.1827 147.999 90.0179 147.823 89.808 147.697C89.5981 147.565 89.3553 147.499 89.0795 147.499C88.6718 147.499 88.336 147.64 88.0722 147.921C87.8143 148.203 87.6854 148.566 87.6854 149.01C87.6854 149.459 87.8143 149.825 88.0722 150.107C88.336 150.383 88.6718 150.521 89.0795 150.521Z"
                    fill="#2D2D2D" />
                <path
                    d="M160.442 140.532C160.442 139.112 161.593 137.962 163.012 137.962H209.43C210.849 137.962 212 139.112 212 140.532V155.95C212 157.369 210.849 158.519 209.43 158.519H163.012C161.593 158.519 160.442 157.369 160.442 155.95V140.532Z"
                    fill="#F6F6F6" />
                <path
                    d="M173.69 151.348C173.228 151.348 172.823 151.267 172.476 151.105C172.128 150.943 171.855 150.713 171.657 150.413C171.465 150.113 171.366 149.756 171.36 149.343H172.368C172.374 149.678 172.491 149.963 172.718 150.197C172.946 150.431 173.267 150.548 173.681 150.548C174.047 150.548 174.331 150.461 174.535 150.287C174.745 150.107 174.85 149.879 174.85 149.603C174.85 149.381 174.799 149.202 174.697 149.064C174.601 148.926 174.466 148.812 174.292 148.722C174.125 148.632 173.93 148.551 173.708 148.479C173.486 148.407 173.252 148.329 173.006 148.245C172.521 148.083 172.155 147.874 171.909 147.616C171.669 147.358 171.549 147.019 171.549 146.599C171.543 146.246 171.624 145.937 171.792 145.673C171.966 145.409 172.206 145.205 172.512 145.061C172.823 144.911 173.186 144.837 173.6 144.837C174.008 144.837 174.364 144.911 174.67 145.061C174.982 145.211 175.225 145.421 175.399 145.691C175.573 145.955 175.662 146.264 175.668 146.617H174.661C174.661 146.455 174.619 146.303 174.535 146.159C174.451 146.009 174.328 145.886 174.167 145.79C174.005 145.694 173.807 145.646 173.573 145.646C173.273 145.64 173.024 145.715 172.826 145.871C172.635 146.027 172.539 146.243 172.539 146.518C172.539 146.764 172.611 146.953 172.754 147.085C172.898 147.217 173.096 147.328 173.348 147.418C173.6 147.502 173.888 147.601 174.211 147.715C174.523 147.817 174.802 147.939 175.048 148.083C175.294 148.227 175.489 148.416 175.633 148.65C175.782 148.884 175.857 149.181 175.857 149.54C175.857 149.858 175.776 150.155 175.615 150.431C175.453 150.701 175.21 150.922 174.886 151.096C174.562 151.264 174.164 151.348 173.69 151.348ZM178.51 151.348C177.97 151.348 177.544 151.18 177.232 150.845C176.927 150.509 176.774 150.008 176.774 149.343V146.779H177.727V149.244C177.727 150.107 178.081 150.539 178.788 150.539C179.142 150.539 179.433 150.413 179.661 150.161C179.889 149.909 180.003 149.549 180.003 149.082V146.779H180.956V151.24H180.111L180.039 150.458C179.901 150.734 179.697 150.952 179.427 151.114C179.163 151.27 178.857 151.348 178.51 151.348ZM184.678 151.348C184.33 151.348 184.021 151.279 183.752 151.141C183.488 151.003 183.278 150.809 183.122 150.557L183.023 151.24H182.169V144.765H183.122V147.472C183.266 147.262 183.464 147.076 183.716 146.914C183.968 146.752 184.291 146.671 184.687 146.671C185.119 146.671 185.499 146.773 185.829 146.977C186.159 147.181 186.417 147.46 186.603 147.814C186.795 148.167 186.891 148.569 186.891 149.019C186.891 149.468 186.795 149.87 186.603 150.224C186.417 150.572 186.159 150.847 185.829 151.051C185.499 151.249 185.116 151.348 184.678 151.348ZM184.516 150.521C184.924 150.521 185.26 150.383 185.523 150.107C185.787 149.825 185.919 149.459 185.919 149.01C185.919 148.716 185.859 148.455 185.739 148.227C185.619 147.999 185.455 147.823 185.245 147.697C185.035 147.565 184.792 147.499 184.516 147.499C184.108 147.499 183.773 147.64 183.509 147.921C183.251 148.203 183.122 148.566 183.122 149.01C183.122 149.459 183.251 149.825 183.509 150.107C183.773 150.383 184.108 150.521 184.516 150.521ZM187.922 151.24V146.779H188.767L188.848 147.409C188.992 147.181 189.181 147.001 189.415 146.869C189.655 146.737 189.93 146.671 190.242 146.671C190.95 146.671 191.441 146.95 191.717 147.508C191.879 147.25 192.095 147.046 192.365 146.896C192.64 146.746 192.937 146.671 193.255 146.671C193.813 146.671 194.25 146.839 194.568 147.175C194.886 147.511 195.045 148.011 195.045 148.677V151.24H194.092V148.776C194.092 147.912 193.762 147.481 193.102 147.481C192.766 147.481 192.491 147.607 192.275 147.859C192.065 148.11 191.96 148.47 191.96 148.938V151.24H191.007V148.776C191.007 147.912 190.674 147.481 190.008 147.481C189.678 147.481 189.406 147.607 189.19 147.859C188.98 148.11 188.875 148.47 188.875 148.938V151.24H187.922ZM196.7 145.934C196.52 145.934 196.37 145.88 196.25 145.772C196.136 145.658 196.079 145.517 196.079 145.349C196.079 145.181 196.136 145.043 196.25 144.935C196.37 144.822 196.52 144.765 196.7 144.765C196.88 144.765 197.027 144.822 197.141 144.935C197.261 145.043 197.32 145.181 197.32 145.349C197.32 145.517 197.261 145.658 197.141 145.772C197.027 145.88 196.88 145.934 196.7 145.934ZM196.223 151.24V146.779H197.177V151.24H196.223ZM200.306 151.24C199.868 151.24 199.52 151.135 199.263 150.925C199.005 150.71 198.876 150.329 198.876 149.783V147.58H198.111V146.779H198.876L198.993 145.646H199.829V146.779H201.088V147.58H199.829V149.783C199.829 150.029 199.88 150.2 199.982 150.296C200.09 150.386 200.273 150.431 200.531 150.431H201.043V151.24H200.306Z"
                    fill="#2D2D2D" />
                <defs>
                    <clipPath id="clip0_1512_243563">
                        <rect width="12.5216" height="12.5216" fill="white"
                            transform="matrix(0.926175 0.377095 -0.309402 0.950931 12.728 94.2832)" />
                    </clipPath>
                </defs>
            </svg>
        </div>
    </div>
    `
    return html
}

function build_preview_slider_widget_response(range_data) {
    if (!$("input[name=range-slider-type]:checked")) {
        return ""
    }
    let html = `
    <div class="preview-user-message-wrapper">
    <div class="slider-widget-response-bot-preview-wrapper">
        <div class="slider-widget-response-bot-preview-content">
    `
    if (range_data.range_type === "single-range-slider") {
        html += `
        <svg width="60" height="7" viewBox="0 0 60 7" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M0.0655651 4.65111H0.971386C0.977003 4.97131 1.10199 5.23673 1.34635 5.44739C1.59071 5.65805 1.91653 5.76337 2.3238 5.76337C2.68612 5.76337 2.97683 5.68613 3.19591 5.53165C3.41499 5.37436 3.52454 5.1609 3.52454 4.89126C3.52454 4.71712 3.48662 4.56825 3.41078 4.44467C3.33775 4.32108 3.23804 4.22418 3.11165 4.15396C2.98526 4.08094 2.84061 4.01914 2.6777 3.96859C2.51479 3.91803 2.34205 3.87168 2.15948 3.82955C1.97973 3.78742 1.79856 3.74248 1.61599 3.69473C1.43623 3.64418 1.2649 3.57817 1.10199 3.49672C0.939085 3.41245 0.794435 3.31134 0.668041 3.19337C0.541647 3.0726 0.440533 2.9139 0.364697 2.71729C0.291669 2.52068 0.255155 2.29317 0.255155 2.03476C0.255155 1.56009 0.43632 1.16124 0.798648 0.838238C1.16378 0.515233 1.65532 0.35373 2.27324 0.35373C2.53726 0.35373 2.78864 0.390244 3.02739 0.463271C3.26894 0.536298 3.48802 0.644435 3.68463 0.787681C3.88405 0.928118 4.04275 1.11771 4.16072 1.35645C4.28149 1.59239 4.34328 1.86203 4.34609 2.16537H3.40235C3.40235 1.86484 3.30264 1.6275 3.10322 1.45335C2.90661 1.2764 2.62714 1.18793 2.26481 1.18793C1.91372 1.18793 1.64408 1.26798 1.45589 1.42808C1.27052 1.58817 1.17783 1.78479 1.17783 2.01791C1.17783 2.17239 1.21575 2.30581 1.29158 2.41816C1.36742 2.5277 1.46853 2.61477 1.59493 2.67937C1.72132 2.74397 1.86738 2.80015 2.03309 2.8479C2.19881 2.89564 2.37295 2.94199 2.55552 2.98693C2.73809 3.02906 2.92066 3.07681 3.10322 3.13017C3.28579 3.18073 3.45993 3.24955 3.62565 3.33662C3.79137 3.42369 3.93742 3.52902 4.06381 3.6526C4.19021 3.77338 4.29132 3.93348 4.36716 4.1329C4.443 4.33232 4.48091 4.56264 4.48091 4.82385C4.48091 5.34628 4.2843 5.77601 3.89108 6.11306C3.50066 6.45011 2.967 6.61864 2.29009 6.61864C1.64127 6.61864 1.10761 6.43607 0.689107 6.07093C0.273412 5.70299 0.0655651 5.22971 0.0655651 4.65111ZM5.2477 4.2635C5.2477 3.79444 5.34601 3.37875 5.54262 3.01642C5.73923 2.65128 6.00747 2.37041 6.34732 2.1738C6.68999 1.97718 7.07479 1.87888 7.50172 1.87888C7.84439 1.87888 8.15616 1.93927 8.43703 2.06004C8.71791 2.18082 8.94963 2.34653 9.1322 2.55719C9.31757 2.76785 9.45942 3.01361 9.55772 3.29449C9.65884 3.57536 9.70939 3.8773 9.70939 4.20031V4.53736H6.15352C6.17037 4.93339 6.30379 5.25218 6.55377 5.49373C6.80375 5.73529 7.13377 5.85606 7.54385 5.85606C7.83034 5.85606 8.08594 5.79146 8.31064 5.66226C8.53815 5.53306 8.69684 5.35891 8.78672 5.13983H9.66726C9.54929 5.58361 9.29791 5.94173 8.91311 6.21418C8.53112 6.48382 8.06628 6.61864 7.51857 6.61864C6.84728 6.61864 6.30098 6.39815 5.87967 5.95718C5.45836 5.5134 5.2477 4.94884 5.2477 4.2635ZM6.17037 3.83798H8.812C8.78391 3.46722 8.64769 3.17511 8.40333 2.96165C8.15897 2.74538 7.85843 2.63724 7.50172 2.63724C7.15343 2.63724 6.8529 2.74959 6.60011 2.97429C6.34732 3.19899 6.20408 3.48689 6.17037 3.83798ZM10.6068 5.38419V0.0335329H11.5126V5.32942C11.5126 5.4502 11.5421 5.54289 11.6011 5.60749C11.6601 5.67209 11.7457 5.70439 11.8581 5.70439H12.0477V6.50488H11.6769C11.3371 6.50488 11.073 6.40658 10.8849 6.20996C10.6995 6.01335 10.6068 5.7381 10.6068 5.38419ZM12.7302 4.2635C12.7302 3.79444 12.8285 3.37875 13.0251 3.01642C13.2217 2.65128 13.49 2.37041 13.8298 2.1738C14.1725 1.97718 14.5573 1.87888 14.9842 1.87888C15.3269 1.87888 15.6387 1.93927 15.9195 2.06004C16.2004 2.18082 16.4321 2.34653 16.6147 2.55719C16.8001 2.76785 16.9419 3.01361 17.0402 3.29449C17.1413 3.57536 17.1919 3.8773 17.1919 4.20031V4.53736H13.636C13.6529 4.93339 13.7863 5.25218 14.0363 5.49373C14.2862 5.73529 14.6163 5.85606 15.0263 5.85606C15.3128 5.85606 15.5684 5.79146 15.7931 5.66226C16.0206 5.53306 16.1793 5.35891 16.2692 5.13983H17.1498C17.0318 5.58361 16.7804 5.94173 16.3956 6.21418C16.0136 6.48382 15.5488 6.61864 15.0011 6.61864C14.3298 6.61864 13.7835 6.39815 13.3622 5.95718C12.9409 5.5134 12.7302 4.94884 12.7302 4.2635ZM13.6529 3.83798H16.2945C16.2664 3.46722 16.1302 3.17511 15.8858 2.96165C15.6415 2.74538 15.3409 2.63724 14.9842 2.63724C14.6359 2.63724 14.3354 2.74959 14.0826 2.97429C13.8298 3.19899 13.6866 3.48689 13.6529 3.83798ZM17.9713 4.25086C17.9713 3.80989 18.0696 3.40965 18.2662 3.05013C18.4628 2.6878 18.7395 2.40271 19.0962 2.19486C19.4557 1.98421 19.8602 1.87888 20.3096 1.87888C20.8517 1.87888 21.325 2.03336 21.7294 2.34232C22.1367 2.65128 22.3909 3.06136 22.492 3.57255H21.5609C21.4823 3.31415 21.3292 3.1063 21.1017 2.94901C20.877 2.78891 20.6158 2.70886 20.318 2.70886C19.8967 2.70886 19.5555 2.85492 19.2942 3.14703C19.033 3.43914 18.9024 3.80708 18.9024 4.25086C18.9024 4.69745 19.0358 5.06681 19.3027 5.35891C19.5695 5.65102 19.9136 5.79708 20.3349 5.79708C20.6242 5.79708 20.8826 5.71843 21.1101 5.56114C21.3376 5.40385 21.4907 5.19741 21.5693 4.94182H22.492C22.3937 5.4502 22.1423 5.85747 21.7378 6.16362C21.3334 6.46696 20.8601 6.61864 20.318 6.61864C19.9754 6.61864 19.6566 6.55825 19.3616 6.43747C19.0695 6.31389 18.8224 6.14677 18.6201 5.93611C18.4179 5.72265 18.2592 5.47126 18.1441 5.18196C18.0289 4.88985 17.9713 4.57949 17.9713 4.25086ZM23.2293 2.73414V2.00106H23.8233C23.902 2.00106 23.9666 1.97438 24.0171 1.92101C24.0677 1.86764 24.093 1.79602 24.093 1.70614V0.716058H24.944V1.99263H26.2585V2.73414H24.944V5.04714C24.944 5.50778 25.1631 5.7381 25.6013 5.7381H26.2122V6.50488H25.4622C25.0128 6.50488 24.6632 6.3827 24.4132 6.13834C24.1632 5.89117 24.0382 5.53587 24.0382 5.07242V2.73414H23.2293ZM29.9703 5.9656C29.5658 5.53025 29.3636 4.96288 29.3636 4.2635C29.3636 3.56413 29.5644 2.99255 29.9661 2.54876C30.3677 2.10217 30.8831 1.87888 31.5123 1.87888C31.7145 1.87888 31.9041 1.90697 32.0811 1.96314C32.258 2.01932 32.4055 2.09234 32.5234 2.18222C32.6442 2.2721 32.7397 2.35496 32.8099 2.4308C32.8801 2.50382 32.9391 2.57685 32.9869 2.64988H33.0501V1.99263H33.9559V6.50488H33.0669V5.86449H33.0122C32.6554 6.36725 32.1695 6.61864 31.5544 6.61864C30.9056 6.61864 30.3775 6.40096 29.9703 5.9656ZM30.2863 4.25086C30.2863 4.71712 30.4141 5.09208 30.6697 5.37577C30.9281 5.65664 31.2665 5.79708 31.685 5.79708C32.1063 5.79708 32.4434 5.64962 32.6962 5.3547C32.949 5.05978 33.0753 4.69184 33.0753 4.25086C33.0753 3.77619 32.9433 3.40122 32.6793 3.12596C32.4181 2.8479 32.0839 2.70886 31.6766 2.70886C31.2665 2.70886 30.9323 2.85351 30.6739 3.14281C30.4155 3.42931 30.2863 3.79866 30.2863 4.25086ZM37.1199 1.99263H38.0805L39.2939 5.40947H39.3571L40.5621 1.99263H41.5395L39.8206 6.50488H38.8389L37.1199 1.99263ZM42.5507 5.9656C42.1462 5.53025 41.944 4.96288 41.944 4.2635C41.944 3.56413 42.1448 2.99255 42.5464 2.54876C42.9481 2.10217 43.4635 1.87888 44.0927 1.87888C44.2949 1.87888 44.4845 1.90697 44.6614 1.96314C44.8384 2.01932 44.9858 2.09234 45.1038 2.18222C45.2246 2.2721 45.3201 2.35496 45.3903 2.4308C45.4605 2.50382 45.5195 2.57685 45.5672 2.64988H45.6304V1.99263H46.5363V6.50488H45.6473V5.86449H45.5925C45.2358 6.36725 44.7499 6.61864 44.1348 6.61864C43.486 6.61864 42.9579 6.40096 42.5507 5.9656ZM42.8666 4.25086C42.8666 4.71712 42.9944 5.09208 43.25 5.37577C43.5084 5.65664 43.8469 5.79708 44.2654 5.79708C44.6867 5.79708 45.0238 5.64962 45.2765 5.3547C45.5293 5.05978 45.6557 4.69184 45.6557 4.25086C45.6557 3.77619 45.5237 3.40122 45.2597 3.12596C44.9985 2.8479 44.6642 2.70886 44.257 2.70886C43.8469 2.70886 43.5126 2.85351 43.2542 3.14281C42.9958 3.42931 42.8666 3.79866 42.8666 4.25086ZM47.8423 5.38419V0.0335329H48.7481V5.32942C48.7481 5.4502 48.7776 5.54289 48.8366 5.60749C48.8956 5.67209 48.9813 5.70439 49.0936 5.70439H49.2832V6.50488H48.9125C48.5726 6.50488 48.3086 6.40658 48.1204 6.20996C47.935 6.01335 47.8423 5.7381 47.8423 5.38419ZM50.3786 4.89126V1.99263H51.2844V4.72695C51.2844 5.04153 51.3799 5.29572 51.5709 5.48952C51.7619 5.68332 52.0021 5.78023 52.2914 5.78023C52.6088 5.78023 52.87 5.67349 53.075 5.46003C53.2829 5.24376 53.3868 4.97131 53.3868 4.64268V1.99263H54.2926V6.50488H53.4121V5.90241H53.3531C53.2548 6.10464 53.0891 6.27457 52.8559 6.41219C52.6256 6.54982 52.3518 6.61864 52.0344 6.61864C51.5316 6.61864 51.13 6.45573 50.8294 6.12992C50.5289 5.8041 50.3786 5.39122 50.3786 4.89126ZM55.2995 4.2635C55.2995 3.79444 55.3979 3.37875 55.5945 3.01642C55.7911 2.65128 56.0593 2.37041 56.3992 2.1738C56.7418 1.97718 57.1266 1.87888 57.5536 1.87888C57.8962 1.87888 58.208 1.93927 58.4889 2.06004C58.7698 2.18082 59.0015 2.34653 59.184 2.55719C59.3694 2.76785 59.5113 3.01361 59.6096 3.29449C59.7107 3.57536 59.7612 3.8773 59.7612 4.20031V4.53736H56.2054C56.2222 4.93339 56.3556 5.25218 56.6056 5.49373C56.8556 5.73529 57.1856 5.85606 57.5957 5.85606C57.8822 5.85606 58.1378 5.79146 58.3625 5.66226C58.59 5.53306 58.7487 5.35891 58.8386 5.13983H59.7191C59.6011 5.58361 59.3498 5.94173 58.965 6.21418C58.583 6.48382 58.1181 6.61864 57.5704 6.61864C56.8991 6.61864 56.3528 6.39815 55.9315 5.95718C55.5102 5.5134 55.2995 4.94884 55.2995 4.2635ZM56.2222 3.83798H58.8638C58.8358 3.46722 58.6995 3.17511 58.4552 2.96165C58.2108 2.74538 57.9103 2.63724 57.5536 2.63724C57.2053 2.63724 56.9047 2.74959 56.652 2.97429C56.3992 3.19899 56.2559 3.48689 56.2222 3.83798Z" fill="#2D2D2D"/>
        </svg>
        <div>
            <div style="height:14px;">
                <svg width="190" height="11" viewBox="0 0 190 11" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect y="4.09082" width="190" height="2" rx="1" fill="#6A6DCD" fill-opacity="0.3"/>
            <rect x="0.000244141" y="4.09082" width="184.987" height="2.16782" rx="1.08391" fill="#2755CB"/>
            <ellipse cx="184.463" cy="4.7231" rx="4.57208" ry="4.2231" fill="#2755CB"/>
            </svg>
            </div>
            <div class="easychat-bot-slider-output-input-single" style="padding-top:0px;">
                <div>${range_data.max}</div>
            </div>
        </div>
        <div style="display: flex; width:100%; align-items:center;">
            <div class="range-slider-value-div" style="width: 100%;">
                ${range_data.max}
            </div>
        </div>
        <div style="display: flex; width:100%; justify-content:center; padding: 0px 8px;">
            <svg width="59" height="7" viewBox="0 0 59 7" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M0.960938 4.72754H1.80078C1.80599 5.02441 1.92188 5.27051 2.14844 5.46582C2.375 5.66113 2.67708 5.75879 3.05469 5.75879C3.39062 5.75879 3.66016 5.68717 3.86328 5.54395C4.06641 5.39811 4.16797 5.2002 4.16797 4.9502C4.16797 4.78874 4.13281 4.65072 4.0625 4.53613C3.99479 4.42155 3.90234 4.33171 3.78516 4.2666C3.66797 4.19889 3.53385 4.1416 3.38281 4.09473C3.23177 4.04785 3.07161 4.00488 2.90234 3.96582C2.73568 3.92676 2.56771 3.88509 2.39844 3.84082C2.23177 3.79395 2.07292 3.73275 1.92188 3.65723C1.77083 3.5791 1.63672 3.48535 1.51953 3.37598C1.40234 3.264 1.30859 3.11686 1.23828 2.93457C1.17057 2.75228 1.13672 2.54134 1.13672 2.30176C1.13672 1.86165 1.30469 1.49186 1.64062 1.19238C1.97917 0.892904 2.4349 0.743164 3.00781 0.743164C3.2526 0.743164 3.48568 0.777018 3.70703 0.844727C3.93099 0.912435 4.13411 1.0127 4.31641 1.14551C4.5013 1.27572 4.64844 1.4515 4.75781 1.67285C4.86979 1.8916 4.92708 2.1416 4.92969 2.42285H4.05469C4.05469 2.14421 3.96224 1.92415 3.77734 1.7627C3.59505 1.59863 3.33594 1.5166 3 1.5166C2.67448 1.5166 2.42448 1.59082 2.25 1.73926C2.07812 1.8877 1.99219 2.06999 1.99219 2.28613C1.99219 2.42936 2.02734 2.55306 2.09766 2.65723C2.16797 2.75879 2.26172 2.83952 2.37891 2.89941C2.49609 2.95931 2.63151 3.01139 2.78516 3.05566C2.9388 3.09993 3.10026 3.1429 3.26953 3.18457C3.4388 3.22363 3.60807 3.2679 3.77734 3.31738C3.94661 3.36426 4.10807 3.42806 4.26172 3.50879C4.41536 3.58952 4.55078 3.68717 4.66797 3.80176C4.78516 3.91374 4.87891 4.06217 4.94922 4.24707C5.01953 4.43197 5.05469 4.64551 5.05469 4.8877C5.05469 5.37207 4.8724 5.77051 4.50781 6.08301C4.14583 6.39551 3.65104 6.55176 3.02344 6.55176C2.42188 6.55176 1.92708 6.38249 1.53906 6.04395C1.15365 5.7028 0.960938 5.264 0.960938 4.72754ZM5.76562 4.36816C5.76562 3.93327 5.85677 3.54785 6.03906 3.21191C6.22135 2.87337 6.47005 2.61296 6.78516 2.43066C7.10286 2.24837 7.45964 2.15723 7.85547 2.15723C8.17318 2.15723 8.46224 2.21322 8.72266 2.3252C8.98307 2.43717 9.19792 2.59082 9.36719 2.78613C9.53906 2.98145 9.67057 3.20931 9.76172 3.46973C9.85547 3.73014 9.90234 4.01009 9.90234 4.30957V4.62207H6.60547C6.62109 4.98926 6.74479 5.28483 6.97656 5.50879C7.20833 5.73275 7.51432 5.84473 7.89453 5.84473C8.16016 5.84473 8.39714 5.78483 8.60547 5.66504C8.81641 5.54525 8.96354 5.38379 9.04688 5.18066H9.86328C9.75391 5.59212 9.52083 5.92415 9.16406 6.17676C8.8099 6.42676 8.37891 6.55176 7.87109 6.55176C7.2487 6.55176 6.74219 6.34733 6.35156 5.93848C5.96094 5.52702 5.76562 5.00358 5.76562 4.36816ZM6.62109 3.97363H9.07031C9.04427 3.62988 8.91797 3.35905 8.69141 3.16113C8.46484 2.96061 8.1862 2.86035 7.85547 2.86035C7.53255 2.86035 7.25391 2.96452 7.01953 3.17285C6.78516 3.38118 6.65234 3.64811 6.62109 3.97363ZM10.7344 5.40723V0.446289H11.5742V5.35645C11.5742 5.46842 11.6016 5.55436 11.6562 5.61426C11.7109 5.67415 11.7904 5.7041 11.8945 5.7041H12.0703V6.44629H11.7266C11.4115 6.44629 11.1667 6.35514 10.9922 6.17285C10.8203 5.99056 10.7344 5.73535 10.7344 5.40723ZM12.7031 4.36816C12.7031 3.93327 12.7943 3.54785 12.9766 3.21191C13.1589 2.87337 13.4076 2.61296 13.7227 2.43066C14.0404 2.24837 14.3971 2.15723 14.793 2.15723C15.1107 2.15723 15.3997 2.21322 15.6602 2.3252C15.9206 2.43717 16.1354 2.59082 16.3047 2.78613C16.4766 2.98145 16.6081 3.20931 16.6992 3.46973C16.793 3.73014 16.8398 4.01009 16.8398 4.30957V4.62207H13.543C13.5586 4.98926 13.6823 5.28483 13.9141 5.50879C14.1458 5.73275 14.4518 5.84473 14.832 5.84473C15.0977 5.84473 15.3346 5.78483 15.543 5.66504C15.7539 5.54525 15.901 5.38379 15.9844 5.18066H16.8008C16.6914 5.59212 16.4583 5.92415 16.1016 6.17676C15.7474 6.42676 15.3164 6.55176 14.8086 6.55176C14.1862 6.55176 13.6797 6.34733 13.2891 5.93848C12.8984 5.52702 12.7031 5.00358 12.7031 4.36816ZM13.5586 3.97363H16.0078C15.9818 3.62988 15.8555 3.35905 15.6289 3.16113C15.4023 2.96061 15.1237 2.86035 14.793 2.86035C14.4701 2.86035 14.1914 2.96452 13.957 3.17285C13.7227 3.38118 13.5898 3.64811 13.5586 3.97363ZM17.5625 4.35645C17.5625 3.94759 17.6536 3.5765 17.8359 3.24316C18.0182 2.90723 18.2747 2.6429 18.6055 2.4502C18.9388 2.25488 19.3138 2.15723 19.7305 2.15723C20.2331 2.15723 20.6719 2.30046 21.0469 2.58691C21.4245 2.87337 21.6602 3.25358 21.7539 3.72754H20.8906C20.8177 3.48796 20.6758 3.29525 20.4648 3.14941C20.2565 3.00098 20.0143 2.92676 19.7383 2.92676C19.3477 2.92676 19.0312 3.06217 18.7891 3.33301C18.5469 3.60384 18.4258 3.94499 18.4258 4.35645C18.4258 4.77051 18.5495 5.11296 18.7969 5.38379C19.0443 5.65462 19.3633 5.79004 19.7539 5.79004C20.0221 5.79004 20.2617 5.71712 20.4727 5.57129C20.6836 5.42546 20.8255 5.23405 20.8984 4.99707H21.7539C21.6628 5.46842 21.4297 5.84603 21.0547 6.12988C20.6797 6.41113 20.2409 6.55176 19.7383 6.55176C19.4206 6.55176 19.125 6.49577 18.8516 6.38379C18.5807 6.26921 18.3516 6.11426 18.1641 5.91895C17.9766 5.72103 17.8294 5.48796 17.7227 5.21973C17.6159 4.94889 17.5625 4.66113 17.5625 4.35645ZM22.4375 2.9502V2.27051H22.9883C23.0612 2.27051 23.1211 2.24577 23.168 2.19629C23.2148 2.14681 23.2383 2.0804 23.2383 1.99707V1.0791H24.0273V2.2627H25.2461V2.9502H24.0273V5.09473C24.0273 5.52181 24.2305 5.73535 24.6367 5.73535H25.2031V6.44629H24.5078C24.0911 6.44629 23.7669 6.33301 23.5352 6.10645C23.3034 5.87728 23.1875 5.54785 23.1875 5.11816V2.9502H22.4375ZM25.9453 4.36816C25.9453 3.93327 26.0365 3.54785 26.2188 3.21191C26.401 2.87337 26.6497 2.61296 26.9648 2.43066C27.2826 2.24837 27.6393 2.15723 28.0352 2.15723C28.3529 2.15723 28.6419 2.21322 28.9023 2.3252C29.1628 2.43717 29.3776 2.59082 29.5469 2.78613C29.7188 2.98145 29.8503 3.20931 29.9414 3.46973C30.0352 3.73014 30.082 4.01009 30.082 4.30957V4.62207H26.7852C26.8008 4.98926 26.9245 5.28483 27.1562 5.50879C27.388 5.73275 27.694 5.84473 28.0742 5.84473C28.3398 5.84473 28.5768 5.78483 28.7852 5.66504C28.9961 5.54525 29.1432 5.38379 29.2266 5.18066H30.043C29.9336 5.59212 29.7005 5.92415 29.3438 6.17676C28.9896 6.42676 28.5586 6.55176 28.0508 6.55176C27.4284 6.55176 26.9219 6.34733 26.5312 5.93848C26.1406 5.52702 25.9453 5.00358 25.9453 4.36816ZM26.8008 3.97363H29.25C29.224 3.62988 29.0977 3.35905 28.8711 3.16113C28.6445 2.96061 28.3659 2.86035 28.0352 2.86035C27.7122 2.86035 27.4336 2.96452 27.1992 3.17285C26.9648 3.38118 26.832 3.64811 26.8008 3.97363ZM31.3672 5.94629C30.9922 5.54264 30.8047 5.0166 30.8047 4.36816C30.8047 3.71973 30.9909 3.18978 31.3633 2.77832C31.7357 2.36426 32.2135 2.15723 32.7969 2.15723C32.9844 2.15723 33.1602 2.18327 33.3242 2.23535C33.4883 2.28743 33.625 2.35514 33.7344 2.43848C33.8464 2.52181 33.9349 2.59863 34 2.66895C34.0651 2.73665 34.1198 2.80436 34.1641 2.87207H34.2227V0.446289H35.0625V6.44629H34.2383V5.85254H34.1875C33.8568 6.31868 33.4062 6.55176 32.8359 6.55176C32.2344 6.55176 31.7448 6.34993 31.3672 5.94629ZM31.6602 4.35645C31.6602 4.78874 31.7786 5.13639 32.0156 5.39941C32.2552 5.65983 32.569 5.79004 32.957 5.79004C33.3477 5.79004 33.6602 5.65332 33.8945 5.37988C34.1289 5.10645 34.2461 4.7653 34.2461 4.35645C34.2461 3.91634 34.1237 3.56868 33.8789 3.31348C33.6367 3.05566 33.3268 2.92676 32.9492 2.92676C32.569 2.92676 32.2591 3.06087 32.0195 3.3291C31.7799 3.59473 31.6602 3.93717 31.6602 4.35645ZM37.9961 2.2627H38.8867L40.0117 5.43066H40.0703L41.1875 2.2627H42.0938L40.5 6.44629H39.5898L37.9961 2.2627ZM43.0312 5.94629C42.6562 5.54264 42.4688 5.0166 42.4688 4.36816C42.4688 3.71973 42.6549 3.18978 43.0273 2.77832C43.3997 2.36426 43.8776 2.15723 44.4609 2.15723C44.6484 2.15723 44.8242 2.18327 44.9883 2.23535C45.1523 2.28743 45.2891 2.35514 45.3984 2.43848C45.5104 2.52181 45.599 2.59863 45.6641 2.66895C45.7292 2.73665 45.7839 2.80436 45.8281 2.87207H45.8867V2.2627H46.7266V6.44629H45.9023V5.85254H45.8516C45.5208 6.31868 45.0703 6.55176 44.5 6.55176C43.8984 6.55176 43.4089 6.34993 43.0312 5.94629ZM43.3242 4.35645C43.3242 4.78874 43.4427 5.13639 43.6797 5.39941C43.9193 5.65983 44.2331 5.79004 44.6211 5.79004C45.0117 5.79004 45.3242 5.65332 45.5586 5.37988C45.793 5.10645 45.9102 4.7653 45.9102 4.35645C45.9102 3.91634 45.7878 3.56868 45.543 3.31348C45.3008 3.05566 44.9909 2.92676 44.6133 2.92676C44.2331 2.92676 43.9232 3.06087 43.6836 3.3291C43.444 3.59473 43.3242 3.93717 43.3242 4.35645ZM47.9375 5.40723V0.446289H48.7773V5.35645C48.7773 5.46842 48.8047 5.55436 48.8594 5.61426C48.9141 5.67415 48.9935 5.7041 49.0977 5.7041H49.2734V6.44629H48.9297C48.6146 6.44629 48.3698 6.35514 48.1953 6.17285C48.0234 5.99056 47.9375 5.73535 47.9375 5.40723ZM50.2891 4.9502V2.2627H51.1289V4.79785C51.1289 5.08952 51.2174 5.3252 51.3945 5.50488C51.5716 5.68457 51.7943 5.77441 52.0625 5.77441C52.3568 5.77441 52.599 5.67546 52.7891 5.47754C52.9818 5.27702 53.0781 5.02441 53.0781 4.71973V2.2627H53.918V6.44629H53.1016V5.8877H53.0469C52.9557 6.0752 52.8021 6.23275 52.5859 6.36035C52.3724 6.48796 52.1185 6.55176 51.8242 6.55176C51.3581 6.55176 50.9857 6.40072 50.707 6.09863C50.4284 5.79655 50.2891 5.41374 50.2891 4.9502ZM54.8516 4.36816C54.8516 3.93327 54.9427 3.54785 55.125 3.21191C55.3073 2.87337 55.556 2.61296 55.8711 2.43066C56.1888 2.24837 56.5456 2.15723 56.9414 2.15723C57.2591 2.15723 57.5482 2.21322 57.8086 2.3252C58.069 2.43717 58.2839 2.59082 58.4531 2.78613C58.625 2.98145 58.7565 3.20931 58.8477 3.46973C58.9414 3.73014 58.9883 4.01009 58.9883 4.30957V4.62207H55.6914C55.707 4.98926 55.8307 5.28483 56.0625 5.50879C56.2943 5.73275 56.6003 5.84473 56.9805 5.84473C57.2461 5.84473 57.4831 5.78483 57.6914 5.66504C57.9023 5.54525 58.0495 5.38379 58.1328 5.18066H58.9492C58.8398 5.59212 58.6068 5.92415 58.25 6.17676C57.8958 6.42676 57.4648 6.55176 56.957 6.55176C56.3346 6.55176 55.8281 6.34733 55.4375 5.93848C55.0469 5.52702 54.8516 5.00358 54.8516 4.36816ZM55.707 3.97363H58.1562C58.1302 3.62988 58.0039 3.35905 57.7773 3.16113C57.5508 2.96061 57.2721 2.86035 56.9414 2.86035C56.6185 2.86035 56.3398 2.96452 56.1055 3.17285C55.8711 3.38118 55.7383 3.64811 55.707 3.97363Z" fill="#7B7A7B"/>
                </svg>
        </div>
        `
    } else {
        html += `
        <svg width="60" height="7" viewBox="0 0 60 7" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M0.0655651 4.65111H0.971386C0.977003 4.97131 1.10199 5.23673 1.34635 5.44739C1.59071 5.65805 1.91653 5.76337 2.3238 5.76337C2.68612 5.76337 2.97683 5.68613 3.19591 5.53165C3.41499 5.37436 3.52454 5.1609 3.52454 4.89126C3.52454 4.71712 3.48662 4.56825 3.41078 4.44467C3.33775 4.32108 3.23804 4.22418 3.11165 4.15396C2.98526 4.08094 2.84061 4.01914 2.6777 3.96859C2.51479 3.91803 2.34205 3.87168 2.15948 3.82955C1.97973 3.78742 1.79856 3.74248 1.61599 3.69473C1.43623 3.64418 1.2649 3.57817 1.10199 3.49672C0.939085 3.41245 0.794435 3.31134 0.668041 3.19337C0.541647 3.0726 0.440533 2.9139 0.364697 2.71729C0.291669 2.52068 0.255155 2.29317 0.255155 2.03476C0.255155 1.56009 0.43632 1.16124 0.798648 0.838238C1.16378 0.515233 1.65532 0.35373 2.27324 0.35373C2.53726 0.35373 2.78864 0.390244 3.02739 0.463271C3.26894 0.536298 3.48802 0.644435 3.68463 0.787681C3.88405 0.928118 4.04275 1.11771 4.16072 1.35645C4.28149 1.59239 4.34328 1.86203 4.34609 2.16537H3.40235C3.40235 1.86484 3.30264 1.6275 3.10322 1.45335C2.90661 1.2764 2.62714 1.18793 2.26481 1.18793C1.91372 1.18793 1.64408 1.26798 1.45589 1.42808C1.27052 1.58817 1.17783 1.78479 1.17783 2.01791C1.17783 2.17239 1.21575 2.30581 1.29158 2.41816C1.36742 2.5277 1.46853 2.61477 1.59493 2.67937C1.72132 2.74397 1.86738 2.80015 2.03309 2.8479C2.19881 2.89564 2.37295 2.94199 2.55552 2.98693C2.73809 3.02906 2.92066 3.07681 3.10322 3.13017C3.28579 3.18073 3.45993 3.24955 3.62565 3.33662C3.79137 3.42369 3.93742 3.52902 4.06381 3.6526C4.19021 3.77338 4.29132 3.93348 4.36716 4.1329C4.443 4.33232 4.48091 4.56264 4.48091 4.82385C4.48091 5.34628 4.2843 5.77601 3.89108 6.11306C3.50066 6.45011 2.967 6.61864 2.29009 6.61864C1.64127 6.61864 1.10761 6.43607 0.689107 6.07093C0.273412 5.70299 0.0655651 5.22971 0.0655651 4.65111ZM5.2477 4.2635C5.2477 3.79444 5.34601 3.37875 5.54262 3.01642C5.73923 2.65128 6.00747 2.37041 6.34732 2.1738C6.68999 1.97718 7.07479 1.87888 7.50172 1.87888C7.84439 1.87888 8.15616 1.93927 8.43703 2.06004C8.71791 2.18082 8.94963 2.34653 9.1322 2.55719C9.31757 2.76785 9.45942 3.01361 9.55772 3.29449C9.65884 3.57536 9.70939 3.8773 9.70939 4.20031V4.53736H6.15352C6.17037 4.93339 6.30379 5.25218 6.55377 5.49373C6.80375 5.73529 7.13377 5.85606 7.54385 5.85606C7.83034 5.85606 8.08594 5.79146 8.31064 5.66226C8.53815 5.53306 8.69684 5.35891 8.78672 5.13983H9.66726C9.54929 5.58361 9.29791 5.94173 8.91311 6.21418C8.53112 6.48382 8.06628 6.61864 7.51857 6.61864C6.84728 6.61864 6.30098 6.39815 5.87967 5.95718C5.45836 5.5134 5.2477 4.94884 5.2477 4.2635ZM6.17037 3.83798H8.812C8.78391 3.46722 8.64769 3.17511 8.40333 2.96165C8.15897 2.74538 7.85843 2.63724 7.50172 2.63724C7.15343 2.63724 6.8529 2.74959 6.60011 2.97429C6.34732 3.19899 6.20408 3.48689 6.17037 3.83798ZM10.6068 5.38419V0.0335329H11.5126V5.32942C11.5126 5.4502 11.5421 5.54289 11.6011 5.60749C11.6601 5.67209 11.7457 5.70439 11.8581 5.70439H12.0477V6.50488H11.6769C11.3371 6.50488 11.073 6.40658 10.8849 6.20996C10.6995 6.01335 10.6068 5.7381 10.6068 5.38419ZM12.7302 4.2635C12.7302 3.79444 12.8285 3.37875 13.0251 3.01642C13.2217 2.65128 13.49 2.37041 13.8298 2.1738C14.1725 1.97718 14.5573 1.87888 14.9842 1.87888C15.3269 1.87888 15.6387 1.93927 15.9195 2.06004C16.2004 2.18082 16.4321 2.34653 16.6147 2.55719C16.8001 2.76785 16.9419 3.01361 17.0402 3.29449C17.1413 3.57536 17.1919 3.8773 17.1919 4.20031V4.53736H13.636C13.6529 4.93339 13.7863 5.25218 14.0363 5.49373C14.2862 5.73529 14.6163 5.85606 15.0263 5.85606C15.3128 5.85606 15.5684 5.79146 15.7931 5.66226C16.0206 5.53306 16.1793 5.35891 16.2692 5.13983H17.1498C17.0318 5.58361 16.7804 5.94173 16.3956 6.21418C16.0136 6.48382 15.5488 6.61864 15.0011 6.61864C14.3298 6.61864 13.7835 6.39815 13.3622 5.95718C12.9409 5.5134 12.7302 4.94884 12.7302 4.2635ZM13.6529 3.83798H16.2945C16.2664 3.46722 16.1302 3.17511 15.8858 2.96165C15.6415 2.74538 15.3409 2.63724 14.9842 2.63724C14.6359 2.63724 14.3354 2.74959 14.0826 2.97429C13.8298 3.19899 13.6866 3.48689 13.6529 3.83798ZM17.9713 4.25086C17.9713 3.80989 18.0696 3.40965 18.2662 3.05013C18.4628 2.6878 18.7395 2.40271 19.0962 2.19486C19.4557 1.98421 19.8602 1.87888 20.3096 1.87888C20.8517 1.87888 21.325 2.03336 21.7294 2.34232C22.1367 2.65128 22.3909 3.06136 22.492 3.57255H21.5609C21.4823 3.31415 21.3292 3.1063 21.1017 2.94901C20.877 2.78891 20.6158 2.70886 20.318 2.70886C19.8967 2.70886 19.5555 2.85492 19.2942 3.14703C19.033 3.43914 18.9024 3.80708 18.9024 4.25086C18.9024 4.69745 19.0358 5.06681 19.3027 5.35891C19.5695 5.65102 19.9136 5.79708 20.3349 5.79708C20.6242 5.79708 20.8826 5.71843 21.1101 5.56114C21.3376 5.40385 21.4907 5.19741 21.5693 4.94182H22.492C22.3937 5.4502 22.1423 5.85747 21.7378 6.16362C21.3334 6.46696 20.8601 6.61864 20.318 6.61864C19.9754 6.61864 19.6566 6.55825 19.3616 6.43747C19.0695 6.31389 18.8224 6.14677 18.6201 5.93611C18.4179 5.72265 18.2592 5.47126 18.1441 5.18196C18.0289 4.88985 17.9713 4.57949 17.9713 4.25086ZM23.2293 2.73414V2.00106H23.8233C23.902 2.00106 23.9666 1.97438 24.0171 1.92101C24.0677 1.86764 24.093 1.79602 24.093 1.70614V0.716058H24.944V1.99263H26.2585V2.73414H24.944V5.04714C24.944 5.50778 25.1631 5.7381 25.6013 5.7381H26.2122V6.50488H25.4622C25.0128 6.50488 24.6632 6.3827 24.4132 6.13834C24.1632 5.89117 24.0382 5.53587 24.0382 5.07242V2.73414H23.2293ZM29.9703 5.9656C29.5658 5.53025 29.3636 4.96288 29.3636 4.2635C29.3636 3.56413 29.5644 2.99255 29.9661 2.54876C30.3677 2.10217 30.8831 1.87888 31.5123 1.87888C31.7145 1.87888 31.9041 1.90697 32.0811 1.96314C32.258 2.01932 32.4055 2.09234 32.5234 2.18222C32.6442 2.2721 32.7397 2.35496 32.8099 2.4308C32.8801 2.50382 32.9391 2.57685 32.9869 2.64988H33.0501V1.99263H33.9559V6.50488H33.0669V5.86449H33.0122C32.6554 6.36725 32.1695 6.61864 31.5544 6.61864C30.9056 6.61864 30.3775 6.40096 29.9703 5.9656ZM30.2863 4.25086C30.2863 4.71712 30.4141 5.09208 30.6697 5.37577C30.9281 5.65664 31.2665 5.79708 31.685 5.79708C32.1063 5.79708 32.4434 5.64962 32.6962 5.3547C32.949 5.05978 33.0753 4.69184 33.0753 4.25086C33.0753 3.77619 32.9433 3.40122 32.6793 3.12596C32.4181 2.8479 32.0839 2.70886 31.6766 2.70886C31.2665 2.70886 30.9323 2.85351 30.6739 3.14281C30.4155 3.42931 30.2863 3.79866 30.2863 4.25086ZM37.1199 1.99263H38.0805L39.2939 5.40947H39.3571L40.5621 1.99263H41.5395L39.8206 6.50488H38.8389L37.1199 1.99263ZM42.5507 5.9656C42.1462 5.53025 41.944 4.96288 41.944 4.2635C41.944 3.56413 42.1448 2.99255 42.5464 2.54876C42.9481 2.10217 43.4635 1.87888 44.0927 1.87888C44.2949 1.87888 44.4845 1.90697 44.6614 1.96314C44.8384 2.01932 44.9858 2.09234 45.1038 2.18222C45.2246 2.2721 45.3201 2.35496 45.3903 2.4308C45.4605 2.50382 45.5195 2.57685 45.5672 2.64988H45.6304V1.99263H46.5363V6.50488H45.6473V5.86449H45.5925C45.2358 6.36725 44.7499 6.61864 44.1348 6.61864C43.486 6.61864 42.9579 6.40096 42.5507 5.9656ZM42.8666 4.25086C42.8666 4.71712 42.9944 5.09208 43.25 5.37577C43.5084 5.65664 43.8469 5.79708 44.2654 5.79708C44.6867 5.79708 45.0238 5.64962 45.2765 5.3547C45.5293 5.05978 45.6557 4.69184 45.6557 4.25086C45.6557 3.77619 45.5237 3.40122 45.2597 3.12596C44.9985 2.8479 44.6642 2.70886 44.257 2.70886C43.8469 2.70886 43.5126 2.85351 43.2542 3.14281C42.9958 3.42931 42.8666 3.79866 42.8666 4.25086ZM47.8423 5.38419V0.0335329H48.7481V5.32942C48.7481 5.4502 48.7776 5.54289 48.8366 5.60749C48.8956 5.67209 48.9813 5.70439 49.0936 5.70439H49.2832V6.50488H48.9125C48.5726 6.50488 48.3086 6.40658 48.1204 6.20996C47.935 6.01335 47.8423 5.7381 47.8423 5.38419ZM50.3786 4.89126V1.99263H51.2844V4.72695C51.2844 5.04153 51.3799 5.29572 51.5709 5.48952C51.7619 5.68332 52.0021 5.78023 52.2914 5.78023C52.6088 5.78023 52.87 5.67349 53.075 5.46003C53.2829 5.24376 53.3868 4.97131 53.3868 4.64268V1.99263H54.2926V6.50488H53.4121V5.90241H53.3531C53.2548 6.10464 53.0891 6.27457 52.8559 6.41219C52.6256 6.54982 52.3518 6.61864 52.0344 6.61864C51.5316 6.61864 51.13 6.45573 50.8294 6.12992C50.5289 5.8041 50.3786 5.39122 50.3786 4.89126ZM55.2995 4.2635C55.2995 3.79444 55.3979 3.37875 55.5945 3.01642C55.7911 2.65128 56.0593 2.37041 56.3992 2.1738C56.7418 1.97718 57.1266 1.87888 57.5536 1.87888C57.8962 1.87888 58.208 1.93927 58.4889 2.06004C58.7698 2.18082 59.0015 2.34653 59.184 2.55719C59.3694 2.76785 59.5113 3.01361 59.6096 3.29449C59.7107 3.57536 59.7612 3.8773 59.7612 4.20031V4.53736H56.2054C56.2222 4.93339 56.3556 5.25218 56.6056 5.49373C56.8556 5.73529 57.1856 5.85606 57.5957 5.85606C57.8822 5.85606 58.1378 5.79146 58.3625 5.66226C58.59 5.53306 58.7487 5.35891 58.8386 5.13983H59.7191C59.6011 5.58361 59.3498 5.94173 58.965 6.21418C58.583 6.48382 58.1181 6.61864 57.5704 6.61864C56.8991 6.61864 56.3528 6.39815 55.9315 5.95718C55.5102 5.5134 55.2995 4.94884 55.2995 4.2635ZM56.2222 3.83798H58.8638C58.8358 3.46722 58.6995 3.17511 58.4552 2.96165C58.2108 2.74538 57.9103 2.63724 57.5536 2.63724C57.2053 2.63724 56.9047 2.74959 56.652 2.97429C56.3992 3.19899 56.2559 3.48689 56.2222 3.83798Z" fill="#2D2D2D"/>
        </svg>
        <div>
            <div style="height:14px;">
                <svg width="190" height="11" viewBox="0 0 190 11" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect x="4.46387" y="4.08984" width="183.541" height="1.9631" rx="0.981548" fill="#6A6DCD" fill-opacity="0.3"/>
                    <rect x="4.46411" y="4.08984" width="184.987" height="2.16782" rx="1.08391" fill="#2755CB"/>
                    <ellipse cx="184.593" cy="4.7106" rx="4.46466" ry="4.14517" fill="#2755CB"/>
                    <ellipse cx="4.46466" cy="4.7106" rx="4.46466" ry="4.14517" fill="#2755CB"/>
                    </svg>
            </div>
            <div class="easychat-bot-slider-output-input" style="width: 100%; font-weight: normal; font-size: 12px; color: #2D2D2D; display: flex; justify-content: space-between;">
                <div>${range_data.min}</div>
                <div>${range_data.max}</div>
            </div>
        </div>
        <div style="display: flex; width:100%; justify-content:space-between; align-items:center;">
            <div class="range-slider-value-div">
            ${range_data.min}
            </div>
            <svg width="11" height="2" viewBox="0 0 11 2" fill="none" xmlns="http://www.w3.org/2000/svg">
            <line x1="0.046875" y1="0.953957" x2="10.1134" y2="0.953957" stroke="#CBCACA" stroke-width="0.719039"/>
            </svg>
            <div class="range-slider-value-div">
            ${range_data.max}
            </div>
        </div>
        <div style="display: flex; width:100%; justify-content:space-between; padding: 0px 8px;">
            <svg width="54" height="7" viewBox="0 0 54 7" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M0.510083 6.35156V1.31689H1.4159L3.16435 5.37201H3.20648L4.80395 1.31689H5.70275V6.35156H4.95492V2.90734H4.91279L3.54704 6.35156H2.79921L1.30355 2.87223H1.25791V6.35156H0.510083ZM6.81923 1.52052C6.81923 1.38242 6.86604 1.2689 6.95967 1.17996C7.05329 1.09102 7.17149 1.04654 7.31427 1.04654C7.46173 1.04654 7.58227 1.09102 7.6759 1.17996C7.77186 1.2689 7.81984 1.38242 7.81984 1.52052C7.81984 1.6633 7.77186 1.77916 7.6759 1.8681C7.58227 1.95705 7.46173 2.00152 7.31427 2.00152C7.16915 2.00152 7.04978 1.95705 6.95615 1.8681C6.86487 1.77916 6.81923 1.6633 6.81923 1.52052ZM6.93509 6.35156V2.59135H7.68994V6.35156H6.93509ZM8.77482 6.35156V2.59135H9.5086V3.09342H9.55775C9.63968 2.92489 9.77777 2.78329 9.97204 2.6686C10.1663 2.5539 10.3957 2.49656 10.6602 2.49656C11.0792 2.49656 11.4139 2.63232 11.6643 2.90383C11.9148 3.17534 12.04 3.51941 12.04 3.93604V6.35156H11.2851V4.07999C11.2851 3.82018 11.2044 3.60952 11.0429 3.44802C10.8837 3.28418 10.6836 3.20226 10.4425 3.20226C10.1804 3.20226 9.96268 3.29354 9.78948 3.47611C9.61627 3.65634 9.52967 3.88338 9.52967 4.15723V6.35156H8.77482ZM13.0125 1.52052C13.0125 1.38242 13.0593 1.2689 13.1529 1.17996C13.2466 1.09102 13.3648 1.04654 13.5076 1.04654C13.655 1.04654 13.7756 1.09102 13.8692 1.17996C13.9651 1.2689 14.0131 1.38242 14.0131 1.52052C14.0131 1.6633 13.9651 1.77916 13.8692 1.8681C13.7756 1.95705 13.655 2.00152 13.5076 2.00152C13.3624 2.00152 13.2431 1.95705 13.1494 1.8681C13.0582 1.77916 13.0125 1.6633 13.0125 1.52052ZM13.1284 6.35156V2.59135H13.8832V6.35156H13.1284ZM14.9681 6.35156V2.59135H15.7019V3.0864H15.751C15.84 2.91319 15.9746 2.77158 16.1548 2.66157C16.335 2.55156 16.5527 2.49656 16.8078 2.49656C17.0723 2.49656 17.3029 2.55273 17.4995 2.66508C17.6961 2.77743 17.8494 2.93191 17.9594 3.12853H18.0086C18.2473 2.70722 18.6335 2.49656 19.1672 2.49656C19.5791 2.49656 19.9103 2.62646 20.1608 2.88627C20.4136 3.14374 20.5399 3.47728 20.5399 3.88689V6.35156H19.7851V4.14319C19.7851 3.84125 19.7161 3.60952 19.578 3.44802C19.4399 3.28418 19.2456 3.20226 18.9951 3.20226C18.7494 3.20226 18.5446 3.28886 18.3807 3.46207C18.2192 3.63293 18.1385 3.86465 18.1385 4.15723V6.35156H17.3836V4.05892C17.3836 3.79912 17.3087 3.59197 17.1589 3.43749C17.0091 3.28067 16.8137 3.20226 16.5726 3.20226C16.3315 3.20226 16.129 3.29003 15.9652 3.46558C15.8037 3.63878 15.723 3.86231 15.723 4.13616V6.35156H14.9681ZM21.5687 5.00688V2.59135H22.3235V4.86995C22.3235 5.1321 22.4031 5.34393 22.5622 5.50543C22.7214 5.66693 22.9215 5.74768 23.1626 5.74768C23.4271 5.74768 23.6448 5.65874 23.8156 5.48085C23.9889 5.30062 24.0755 5.07358 24.0755 4.79973V2.59135H24.8303V6.35156H24.0965V5.8495H24.0474C23.9654 6.01802 23.8274 6.15963 23.6331 6.27432C23.4411 6.38901 23.2129 6.44636 22.9484 6.44636C22.5295 6.44636 22.1948 6.3106 21.9443 6.03909C21.6939 5.76758 21.5687 5.42351 21.5687 5.00688ZM25.9363 6.35156V2.59135H26.67V3.0864H26.7192C26.8081 2.91319 26.9427 2.77158 27.1229 2.66157C27.3032 2.55156 27.5209 2.49656 27.776 2.49656C28.0405 2.49656 28.271 2.55273 28.4676 2.66508C28.6642 2.77743 28.8176 2.93191 28.9276 3.12853H28.9767C29.2155 2.70722 29.6017 2.49656 30.1353 2.49656C30.5473 2.49656 30.8785 2.62646 31.1289 2.88627C31.3817 3.14374 31.5081 3.47728 31.5081 3.88689V6.35156H30.7532V4.14319C30.7532 3.84125 30.6842 3.60952 30.5461 3.44802C30.408 3.28418 30.2137 3.20226 29.9633 3.20226C29.7175 3.20226 29.5127 3.28886 29.3489 3.46207C29.1874 3.63293 29.1066 3.86465 29.1066 4.15723V6.35156H28.3518V4.05892C28.3518 3.79912 28.2769 3.59197 28.1271 3.43749C27.9773 3.28067 27.7818 3.20226 27.5407 3.20226C27.2997 3.20226 27.0972 3.29003 26.9334 3.46558C26.7719 3.63878 26.6911 3.86231 26.6911 4.13616V6.35156H25.9363ZM34.1413 2.59135H34.9418L35.9529 5.43872H36.0056L37.0097 2.59135H37.8243L36.3918 6.35156H35.5738L34.1413 2.59135ZM38.6669 5.90216C38.3298 5.53937 38.1613 5.06656 38.1613 4.48375C38.1613 3.90093 38.3287 3.42462 38.6634 3.0548C38.9981 2.68264 39.4276 2.49656 39.9519 2.49656C40.1204 2.49656 40.2784 2.51997 40.4259 2.56678C40.5733 2.61359 40.6962 2.67445 40.7945 2.74935C40.8952 2.82425 40.9747 2.89329 41.0333 2.95649C41.0918 3.01735 41.1409 3.0782 41.1807 3.13906H41.2334V2.59135H41.9882V6.35156H41.2474V5.8179H41.2018C40.9045 6.23687 40.4996 6.44636 39.987 6.44636C39.4463 6.44636 39.0063 6.26496 38.6669 5.90216ZM38.9302 4.47321C38.9302 4.86176 39.0367 5.17423 39.2497 5.41063C39.465 5.64469 39.7471 5.76173 40.0958 5.76173C40.4469 5.76173 40.7278 5.63884 40.9385 5.39308C41.1491 5.14731 41.2544 4.84069 41.2544 4.47321C41.2544 4.07765 41.1444 3.76518 40.9244 3.5358C40.7067 3.30407 40.4282 3.18821 40.0888 3.18821C39.7471 3.18821 39.4686 3.30875 39.2532 3.54984C39.0379 3.78858 38.9302 4.09637 38.9302 4.47321ZM43.0766 5.41765V0.958771H43.8315V5.37201C43.8315 5.47266 43.856 5.5499 43.9052 5.60373C43.9544 5.65757 44.0257 5.68449 44.1194 5.68449H44.2774V6.35156H43.9684C43.6852 6.35156 43.4652 6.26964 43.3083 6.1058C43.1539 5.94195 43.0766 5.71257 43.0766 5.41765ZM45.1902 5.00688V2.59135H45.9451V4.86995C45.9451 5.1321 46.0246 5.34393 46.1838 5.50543C46.343 5.66693 46.5431 5.74768 46.7842 5.74768C47.0487 5.74768 47.2663 5.65874 47.4372 5.48085C47.6104 5.30062 47.697 5.07358 47.697 4.79973V2.59135H48.4519V6.35156H47.7181V5.8495H47.6689C47.587 6.01802 47.4489 6.15963 47.2546 6.27432C47.0627 6.38901 46.8345 6.44636 46.57 6.44636C46.151 6.44636 45.8163 6.3106 45.5659 6.03909C45.3154 5.76758 45.1902 5.42351 45.1902 5.00688ZM49.291 4.48375C49.291 4.09286 49.3729 3.74645 49.5367 3.44451C49.7006 3.14023 49.9241 2.90617 50.2073 2.74232C50.4929 2.57848 50.8135 2.49656 51.1693 2.49656C51.4549 2.49656 51.7147 2.54688 51.9487 2.64753C52.1828 2.74818 52.3759 2.88627 52.528 3.06182C52.6825 3.23737 52.8007 3.44217 52.8827 3.67623C52.9669 3.91029 53.009 4.16191 53.009 4.43108V4.71196H50.0458C50.0599 5.04198 50.171 5.30765 50.3794 5.50894C50.5877 5.71023 50.8627 5.81088 51.2044 5.81088C51.4432 5.81088 51.6562 5.75704 51.8434 5.64938C52.033 5.54171 52.1653 5.39659 52.2402 5.21402H52.9739C52.8756 5.58384 52.6661 5.88227 52.3455 6.10931C52.0272 6.33401 51.6398 6.44636 51.1834 6.44636C50.624 6.44636 50.1687 6.26262 49.8176 5.89514C49.4665 5.52532 49.291 5.05486 49.291 4.48375ZM50.0599 4.12914H52.2612C52.2378 3.82018 52.1243 3.57676 51.9207 3.39887C51.717 3.21864 51.4666 3.12853 51.1693 3.12853C50.8791 3.12853 50.6286 3.22215 50.418 3.4094C50.2073 3.59665 50.088 3.83657 50.0599 4.12914Z" fill="#7B7A7B"/>
            </svg>
            <svg width="56" height="7" viewBox="0 0 56 7" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M0.928052 6.35156V1.31689H1.83387L3.58232 5.37201H3.62445L5.22192 1.31689H6.12072V6.35156H5.37289V2.90734H5.33076L3.96501 6.35156H3.21718L1.72152 2.87223H1.67588V6.35156H0.928052ZM7.5918 5.90216C7.25475 5.53937 7.08623 5.06656 7.08623 4.48375C7.08623 3.90093 7.25358 3.42462 7.58829 3.0548C7.923 2.68264 8.3525 2.49656 8.8768 2.49656C9.04533 2.49656 9.20332 2.51997 9.35078 2.56678C9.49824 2.61359 9.62112 2.67445 9.71943 2.74935C9.82007 2.82425 9.89965 2.89329 9.95817 2.95649C10.0167 3.01735 10.0658 3.0782 10.1056 3.13906H10.1583V2.59135H10.9131V6.35156H10.1723V5.8179H10.1267C9.82943 6.23687 9.42451 6.44636 8.91191 6.44636C8.37123 6.44636 7.93119 6.26496 7.5918 5.90216ZM7.85512 4.47321C7.85512 4.86176 7.96162 5.17423 8.17462 5.41063C8.38995 5.64469 8.672 5.76173 9.02075 5.76173C9.37184 5.76173 9.65272 5.63884 9.86337 5.39308C10.074 5.14731 10.1794 4.84069 10.1794 4.47321C10.1794 4.07765 10.0693 3.76518 9.84933 3.5358C9.63165 3.30407 9.35312 3.18821 9.01373 3.18821C8.672 3.18821 8.39346 3.30875 8.17813 3.54984C7.96279 3.78858 7.85512 4.09637 7.85512 4.47321ZM11.5627 6.35156L12.8933 4.39597L11.6645 2.59135H12.5176L13.3603 3.89391H13.4024L14.238 2.59135H15.0947L13.8623 4.41704L15.193 6.35156H14.3398L13.4024 4.95772H13.3392L12.4193 6.35156H11.5627ZM15.8179 1.52052C15.8179 1.38242 15.8647 1.2689 15.9584 1.17996C16.052 1.09102 16.1702 1.04654 16.313 1.04654C16.4604 1.04654 16.581 1.09102 16.6746 1.17996C16.7705 1.2689 16.8185 1.38242 16.8185 1.52052C16.8185 1.6633 16.7705 1.77916 16.6746 1.8681C16.581 1.95705 16.4604 2.00152 16.313 2.00152C16.1678 2.00152 16.0485 1.95705 15.9548 1.8681C15.8636 1.77916 15.8179 1.6633 15.8179 1.52052ZM15.9338 6.35156V2.59135H16.6886V6.35156H15.9338ZM17.7735 6.35156V2.59135H18.5073V3.0864H18.5564C18.6454 2.91319 18.78 2.77158 18.9602 2.66157C19.1404 2.55156 19.3581 2.49656 19.6132 2.49656C19.8777 2.49656 20.1083 2.55273 20.3049 2.66508C20.5015 2.77743 20.6548 2.93191 20.7648 3.12853H20.814C21.0527 2.70722 21.4389 2.49656 21.9726 2.49656C22.3845 2.49656 22.7157 2.62646 22.9662 2.88627C23.219 3.14374 23.3454 3.47728 23.3454 3.88689V6.35156H22.5905V4.14319C22.5905 3.84125 22.5215 3.60952 22.3834 3.44802C22.2453 3.28418 22.051 3.20226 21.8005 3.20226C21.5548 3.20226 21.35 3.28886 21.1861 3.46207C21.0246 3.63293 20.9439 3.86465 20.9439 4.15723V6.35156H20.189V4.05892C20.189 3.79912 20.1141 3.59197 19.9643 3.43749C19.8145 3.28067 19.6191 3.20226 19.378 3.20226C19.1369 3.20226 18.9345 3.29003 18.7706 3.46558C18.6091 3.63878 18.5284 3.86231 18.5284 4.13616V6.35156H17.7735ZM24.3741 5.00688V2.59135H25.1289V4.86995C25.1289 5.1321 25.2085 5.34393 25.3676 5.50543C25.5268 5.66693 25.7269 5.74768 25.968 5.74768C26.2325 5.74768 26.4502 5.65874 26.6211 5.48085C26.7943 5.30062 26.8809 5.07358 26.8809 4.79973V2.59135H27.6357V6.35156H26.9019V5.8495H26.8528C26.7709 6.01802 26.6328 6.15963 26.4385 6.27432C26.2466 6.38901 26.0183 6.44636 25.7539 6.44636C25.3349 6.44636 25.0002 6.3106 24.7497 6.03909C24.4993 5.76758 24.3741 5.42351 24.3741 5.00688ZM28.7417 6.35156V2.59135H29.4754V3.0864H29.5246C29.6135 2.91319 29.7481 2.77158 29.9283 2.66157C30.1086 2.55156 30.3263 2.49656 30.5814 2.49656C30.8459 2.49656 31.0764 2.55273 31.273 2.66508C31.4696 2.77743 31.623 2.93191 31.733 3.12853H31.7821C32.0209 2.70722 32.4071 2.49656 32.9407 2.49656C33.3527 2.49656 33.6839 2.62646 33.9343 2.88627C34.1871 3.14374 34.3135 3.47728 34.3135 3.88689V6.35156H33.5587V4.14319C33.5587 3.84125 33.4896 3.60952 33.3515 3.44802C33.2134 3.28418 33.0191 3.20226 32.7687 3.20226C32.5229 3.20226 32.3181 3.28886 32.1543 3.46207C31.9928 3.63293 31.912 3.86465 31.912 4.15723V6.35156H31.1572V4.05892C31.1572 3.79912 31.0823 3.59197 30.9325 3.43749C30.7827 3.28067 30.5872 3.20226 30.3461 3.20226C30.1051 3.20226 29.9026 3.29003 29.7388 3.46558C29.5773 3.63878 29.4965 3.86231 29.4965 4.13616V6.35156H28.7417ZM36.9467 2.59135H37.7472L38.7583 5.43872H38.811L39.8151 2.59135H40.6297L39.1972 6.35156H38.3792L36.9467 2.59135ZM41.4723 5.90216C41.1352 5.53937 40.9667 5.06656 40.9667 4.48375C40.9667 3.90093 41.1341 3.42462 41.4688 3.0548C41.8035 2.68264 42.233 2.49656 42.7573 2.49656C42.9258 2.49656 43.0838 2.51997 43.2313 2.56678C43.3787 2.61359 43.5016 2.67445 43.5999 2.74935C43.7006 2.82425 43.7801 2.89329 43.8387 2.95649C43.8972 3.01735 43.9463 3.0782 43.9861 3.13906H44.0388V2.59135H44.7936V6.35156H44.0528V5.8179H44.0072C43.7099 6.23687 43.305 6.44636 42.7924 6.44636C42.2517 6.44636 41.8117 6.26496 41.4723 5.90216ZM41.7356 4.47321C41.7356 4.86176 41.8421 5.17423 42.0551 5.41063C42.2704 5.64469 42.5525 5.76173 42.9012 5.76173C43.2523 5.76173 43.5332 5.63884 43.7439 5.39308C43.9545 5.14731 44.0598 4.84069 44.0598 4.47321C44.0598 4.07765 43.9498 3.76518 43.7298 3.5358C43.5121 3.30407 43.2336 3.18821 42.8942 3.18821C42.5525 3.18821 42.274 3.30875 42.0586 3.54984C41.8433 3.78858 41.7356 4.09637 41.7356 4.47321ZM45.882 5.41765V0.958771H46.6369V5.37201C46.6369 5.47266 46.6615 5.5499 46.7106 5.60373C46.7598 5.65757 46.8311 5.68449 46.9248 5.68449H47.0828V6.35156H46.7738C46.4906 6.35156 46.2706 6.26964 46.1137 6.1058C45.9593 5.94195 45.882 5.71257 45.882 5.41765ZM47.9956 5.00688V2.59135H48.7505V4.86995C48.7505 5.1321 48.83 5.34393 48.9892 5.50543C49.1484 5.66693 49.3485 5.74768 49.5896 5.74768C49.8541 5.74768 50.0717 5.65874 50.2426 5.48085C50.4158 5.30062 50.5024 5.07358 50.5024 4.79973V2.59135H51.2573V6.35156H50.5235V5.8495H50.4743C50.3924 6.01802 50.2543 6.15963 50.06 6.27432C49.8681 6.38901 49.6399 6.44636 49.3754 6.44636C48.9564 6.44636 48.6217 6.3106 48.3713 6.03909C48.1208 5.76758 47.9956 5.42351 47.9956 5.00688ZM52.0964 4.48375C52.0964 4.09286 52.1783 3.74645 52.3421 3.44451C52.506 3.14023 52.7295 2.90617 53.0127 2.74232C53.2983 2.57848 53.6189 2.49656 53.9747 2.49656C54.2603 2.49656 54.5201 2.54688 54.7541 2.64753C54.9882 2.74818 55.1813 2.88627 55.3334 3.06182C55.4879 3.23737 55.6061 3.44217 55.6881 3.67623C55.7723 3.91029 55.8144 4.16191 55.8144 4.43108V4.71196H52.8512C52.8653 5.04198 52.9764 5.30765 53.1848 5.50894C53.3931 5.71023 53.6681 5.81088 54.0098 5.81088C54.2486 5.81088 54.4616 5.75704 54.6488 5.64938C54.8384 5.54171 54.9707 5.39659 55.0456 5.21402H55.7793C55.681 5.58384 55.4715 5.88227 55.1509 6.10931C54.8326 6.33401 54.4452 6.44636 53.9888 6.44636C53.4294 6.44636 52.9741 6.26262 52.623 5.89514C52.2719 5.52532 52.0964 5.05486 52.0964 4.48375ZM52.8653 4.12914H55.0666C55.0432 3.82018 54.9297 3.57676 54.7261 3.39887C54.5224 3.21864 54.272 3.12853 53.9747 3.12853C53.6845 3.12853 53.434 3.22215 53.2234 3.4094C53.0127 3.59665 52.8934 3.83657 52.8653 4.12914Z" fill="#7B7A7B"/>
                </svg>
        </div>
        `
    }
    html += `
    <svg width="212" height="24" viewBox="0 0 212 24" fill="none"
        xmlns="http://www.w3.org/2000/svg">
        <path
            d="M12.8868 14.8604V8.81874H15.0439C15.6562 8.81874 16.1478 8.99148 16.5185 9.33695C16.8893 9.67962 17.0746 10.1262 17.0746 10.6767C17.0746 11.0924 16.9609 11.4562 16.7334 11.7679C16.5087 12.0797 16.2222 12.2988 15.8739 12.4252L17.2474 14.8604H16.1941L14.9597 12.5642H13.8179V14.8604H12.8868ZM13.8179 11.7553H15.0018C15.3332 11.7553 15.6015 11.6626 15.8065 11.4772C16.0115 11.2918 16.1141 11.025 16.1141 10.6767C16.1141 10.3706 16.0129 10.1192 15.8107 9.92258C15.6113 9.72316 15.3304 9.62345 14.9681 9.62345H13.8179V11.7553ZM17.9341 12.619C17.9341 12.1499 18.0324 11.7342 18.229 11.3719C18.4256 11.0068 18.6939 10.7259 19.0337 10.5293C19.3764 10.3327 19.7612 10.2343 20.1881 10.2343C20.5308 10.2343 20.8426 10.2947 21.1234 10.4155C21.4043 10.5363 21.636 10.702 21.8186 10.9127C22.004 11.1233 22.1458 11.3691 22.2441 11.65C22.3453 11.9308 22.3958 12.2328 22.3958 12.5558V12.8928H18.8399C18.8568 13.2889 18.9902 13.6077 19.2402 13.8492C19.4902 14.0908 19.8202 14.2115 20.2303 14.2115C20.5168 14.2115 20.7724 14.1469 20.9971 14.0177C21.2246 13.8885 21.3833 13.7144 21.4731 13.4953H22.3537C22.2357 13.9391 21.9843 14.2972 21.5995 14.5696C21.2175 14.8393 20.7527 14.9741 20.205 14.9741C19.5337 14.9741 18.9874 14.7536 18.5661 14.3126C18.1448 13.8689 17.9341 13.3043 17.9341 12.619ZM18.8568 12.1934H21.4984C21.4703 11.8227 21.3341 11.5306 21.0897 11.3171C20.8454 11.1008 20.5448 10.9927 20.1881 10.9927C19.8399 10.9927 19.5393 11.1051 19.2865 11.3298C19.0337 11.5545 18.8905 11.8424 18.8568 12.1934ZM23.2342 13.5248H24.0895C24.1485 13.9939 24.4771 14.2284 25.0754 14.2284C25.3675 14.2284 25.5936 14.1694 25.7537 14.0514C25.9166 13.9307 25.998 13.7692 25.998 13.5669C25.998 13.4181 25.9489 13.2987 25.8506 13.2088C25.7551 13.1161 25.6287 13.0487 25.4714 13.0066C25.3169 12.9616 25.1456 12.9237 24.9574 12.8928C24.7692 12.8619 24.581 12.8212 24.3928 12.7706C24.2074 12.7201 24.0361 12.6527 23.8788 12.5684C23.7243 12.4842 23.598 12.3578 23.4996 12.1892C23.4041 12.0179 23.3564 11.8072 23.3564 11.5573C23.3564 11.1725 23.5137 10.8565 23.8283 10.6093C24.1428 10.3593 24.5557 10.2343 25.0669 10.2343C25.5304 10.2343 25.918 10.3551 26.2297 10.5967C26.5415 10.8382 26.7143 11.1697 26.748 11.591H25.918C25.8927 11.3944 25.8042 11.2399 25.6525 11.1275C25.5009 11.0152 25.293 10.959 25.029 10.959C24.779 10.959 24.5782 11.0138 24.4265 11.1233C24.2777 11.23 24.2032 11.3691 24.2032 11.5404C24.2032 11.6584 24.2412 11.7567 24.317 11.8353C24.3956 11.914 24.4968 11.9702 24.6203 12.0039C24.7467 12.0376 24.89 12.0713 25.0501 12.105C25.2102 12.1359 25.3731 12.164 25.5388 12.1892C25.7073 12.2145 25.8716 12.258 26.0317 12.3198C26.1918 12.3816 26.3337 12.4575 26.4573 12.5473C26.5836 12.6344 26.6848 12.7622 26.7606 12.9307C26.8392 13.0993 26.8786 13.2973 26.8786 13.5248C26.8786 13.9573 26.7129 14.307 26.3814 14.5739C26.0528 14.8407 25.609 14.9741 25.0501 14.9741C24.4911 14.9741 24.0558 14.8449 23.744 14.5865C23.435 14.3253 23.2651 13.9714 23.2342 13.5248ZM27.7507 12.619C27.7507 12.1499 27.849 11.7342 28.0456 11.3719C28.2422 11.0068 28.5104 10.7259 28.8503 10.5293C29.193 10.3327 29.5778 10.2343 30.0047 10.2343C30.3474 10.2343 30.6591 10.2947 30.94 10.4155C31.2209 10.5363 31.4526 10.702 31.6352 10.9127C31.8206 11.1233 31.9624 11.3691 32.0607 11.65C32.1618 11.9308 32.2124 12.2328 32.2124 12.5558V12.8928H28.6565C28.6734 13.2889 28.8068 13.6077 29.0567 13.8492C29.3067 14.0908 29.6368 14.2115 30.0468 14.2115C30.3333 14.2115 30.5889 14.1469 30.8136 14.0177C31.0411 13.8885 31.1998 13.7144 31.2897 13.4953H32.1702C32.0523 13.9391 31.8009 14.2972 31.4161 14.5696C31.0341 14.8393 30.5693 14.9741 30.0216 14.9741C29.3503 14.9741 28.804 14.7536 28.3826 14.3126C27.9613 13.8689 27.7507 13.3043 27.7507 12.619ZM28.6734 12.1934H31.315C31.2869 11.8227 31.1507 11.5306 30.9063 11.3171C30.6619 11.1008 30.3614 10.9927 30.0047 10.9927C29.6564 10.9927 29.3559 11.1051 29.1031 11.3298C28.8503 11.5545 28.7071 11.8424 28.6734 12.1934ZM32.9412 11.0896V10.3565H33.5353C33.6139 10.3565 33.6785 10.3298 33.7291 10.2765C33.7797 10.2231 33.8049 10.1515 33.8049 10.0616V9.07153H34.656V10.3481H35.9705V11.0896H34.656V13.4026C34.656 13.8632 34.8751 14.0936 35.3132 14.0936H35.9241V14.8604H35.1742C34.7248 14.8604 34.3751 14.7382 34.1251 14.4938C33.8752 14.2466 33.7502 13.8913 33.7502 13.4279V11.0896H32.9412Z"
            fill="#FF281A" />
        <path
            d="M108.073 11.8395C108.073 11.4014 108.152 10.9899 108.309 10.6051C108.466 10.2175 108.682 9.88466 108.958 9.60659C109.233 9.32853 109.564 9.10945 109.952 8.94935C110.342 8.78925 110.761 8.7092 111.208 8.7092C111.929 8.7092 112.547 8.90581 113.061 9.29904C113.578 9.69226 113.926 10.2119 114.106 10.8579H113.103C112.971 10.4619 112.734 10.1515 112.391 9.92679C112.049 9.70209 111.654 9.58974 111.208 9.58974C110.803 9.58974 110.435 9.68805 110.104 9.88466C109.772 10.0785 109.512 10.3481 109.324 10.6936C109.136 11.0362 109.042 11.4182 109.042 11.8395C109.042 12.4884 109.248 13.0262 109.661 13.4532C110.074 13.8801 110.59 14.0936 111.208 14.0936C111.654 14.0936 112.047 13.9826 112.387 13.7607C112.727 13.5388 112.966 13.2299 113.103 12.8338H114.123C113.952 13.4799 113.603 13.9981 113.078 14.3885C112.556 14.7789 111.932 14.9741 111.208 14.9741C110.761 14.9741 110.342 14.8955 109.952 14.7382C109.562 14.5781 109.229 14.3604 108.954 14.0851C108.681 13.8071 108.466 13.4742 108.309 13.0866C108.152 12.699 108.073 12.2833 108.073 11.8395ZM115.522 14.3211C115.117 13.8857 114.915 13.3184 114.915 12.619C114.915 11.9196 115.116 11.348 115.518 10.9042C115.919 10.4576 116.435 10.2343 117.064 10.2343C117.266 10.2343 117.456 10.2624 117.633 10.3186C117.81 10.3748 117.957 10.4478 118.075 10.5377C118.196 10.6276 118.291 10.7104 118.361 10.7863C118.432 10.8593 118.491 10.9323 118.538 11.0053H118.602V10.3481H119.507V14.8604H118.618V14.22H118.564C118.207 14.7227 117.721 14.9741 117.106 14.9741C116.457 14.9741 115.929 14.7564 115.522 14.3211ZM115.838 12.6063C115.838 13.0726 115.966 13.4476 116.221 13.7312C116.48 14.0121 116.818 14.1525 117.237 14.1525C117.658 14.1525 117.995 14.0051 118.248 13.7102C118.5 13.4153 118.627 13.0473 118.627 12.6063C118.627 12.1317 118.495 11.7567 118.231 11.4814C117.97 11.2034 117.635 11.0643 117.228 11.0643C116.818 11.0643 116.484 11.209 116.225 11.4983C115.967 11.7848 115.838 12.1541 115.838 12.6063ZM120.813 14.8604V10.3481H121.694V10.9506H121.753C121.851 10.7483 122.017 10.5784 122.25 10.4408C122.483 10.3032 122.759 10.2343 123.076 10.2343C123.579 10.2343 123.98 10.3973 124.281 10.7231C124.581 11.0489 124.732 11.4618 124.732 11.9617V14.8604H123.826V12.1345C123.826 11.8227 123.729 11.5699 123.535 11.3761C123.344 11.1795 123.104 11.0812 122.815 11.0812C122.5 11.0812 122.239 11.1907 122.031 11.4098C121.823 11.6261 121.719 11.8985 121.719 12.2272V14.8604H120.813ZM125.718 12.6063C125.718 12.1654 125.816 11.7651 126.012 11.4056C126.209 11.0433 126.486 10.7582 126.842 10.5503C127.202 10.3397 127.606 10.2343 128.056 10.2343C128.598 10.2343 129.071 10.3888 129.476 10.6978C129.883 11.0068 130.137 11.4168 130.238 11.928H129.307C129.228 11.6696 129.075 11.4618 128.848 11.3045C128.623 11.1444 128.362 11.0643 128.064 11.0643C127.643 11.0643 127.302 11.2104 127.04 11.5025C126.779 11.7946 126.649 12.1626 126.649 12.6063C126.649 13.0529 126.782 13.4223 127.049 13.7144C127.316 14.0065 127.66 14.1525 128.081 14.1525C128.37 14.1525 128.629 14.0739 128.856 13.9166C129.084 13.7593 129.237 13.5529 129.316 13.2973H130.238C130.14 13.8057 129.889 14.2129 129.484 14.5191C129.08 14.8224 128.606 14.9741 128.064 14.9741C127.722 14.9741 127.403 14.9137 127.108 14.7929C126.816 14.6694 126.569 14.5022 126.366 14.2916C126.164 14.0781 126.005 13.8267 125.89 13.5374C125.775 13.2453 125.718 12.935 125.718 12.6063ZM131.026 12.619C131.026 12.1499 131.124 11.7342 131.321 11.3719C131.518 11.0068 131.786 10.7259 132.126 10.5293C132.468 10.3327 132.853 10.2343 133.28 10.2343C133.623 10.2343 133.935 10.2947 134.215 10.4155C134.496 10.5363 134.728 10.702 134.911 10.9127C135.096 11.1233 135.238 11.3691 135.336 11.65C135.437 11.9308 135.488 12.2328 135.488 12.5558V12.8928H131.932C131.949 13.2889 132.082 13.6077 132.332 13.8492C132.582 14.0908 132.912 14.2115 133.322 14.2115C133.609 14.2115 133.864 14.1469 134.089 14.0177C134.317 13.8885 134.475 13.7144 134.565 13.4953H135.446C135.328 13.9391 135.076 14.2972 134.691 14.5696C134.309 14.8393 133.845 14.9741 133.297 14.9741C132.626 14.9741 132.079 14.7536 131.658 14.3126C131.237 13.8689 131.026 13.3043 131.026 12.619ZM131.949 12.1934H134.59C134.562 11.8227 134.426 11.5306 134.182 11.3171C133.937 11.1008 133.637 10.9927 133.28 10.9927C132.932 10.9927 132.631 11.1051 132.378 11.3298C132.126 11.5545 131.982 11.8424 131.949 12.1934ZM136.385 13.7397V8.389H137.291V13.6849C137.291 13.8057 137.32 13.8984 137.379 13.963C137.438 14.0276 137.524 14.0599 137.636 14.0599H137.826V14.8604H137.455C137.115 14.8604 136.851 14.762 136.663 14.5654C136.478 14.3688 136.385 14.0936 136.385 13.7397Z"
            fill="#3884FD" />
        <path
            d="M158.612 4.85547C158.612 2.64633 160.403 0.855469 162.612 0.855469H207.622C209.831 0.855469 211.622 2.64633 211.622 4.85547V19.8647C211.622 22.0738 209.831 23.8647 207.622 23.8647H162.612C160.403 23.8647 158.612 22.0739 158.612 19.8647V4.85547Z"
            fill="#3884FD" />
        <path
            d="M170.497 13.0066H171.403C171.409 13.3268 171.534 13.5922 171.778 13.8029C172.022 14.0135 172.348 14.1188 172.755 14.1188C173.118 14.1188 173.408 14.0416 173.628 13.8871C173.847 13.7298 173.956 13.5164 173.956 13.2467C173.956 13.0726 173.918 12.9237 173.842 12.8001C173.769 12.6766 173.67 12.5797 173.543 12.5094C173.417 12.4364 173.272 12.3746 173.109 12.3241C172.946 12.2735 172.774 12.2272 172.591 12.185C172.411 12.1429 172.23 12.098 172.048 12.0502C171.868 11.9996 171.697 11.9336 171.534 11.8522C171.371 11.7679 171.226 11.6668 171.1 11.5488C170.973 11.4281 170.872 11.2694 170.796 11.0728C170.723 10.8761 170.687 10.6486 170.687 10.3902C170.687 9.91556 170.868 9.51671 171.23 9.19371C171.595 8.8707 172.087 8.7092 172.705 8.7092C172.969 8.7092 173.22 8.74571 173.459 8.81874C173.701 8.89177 173.92 8.9999 174.116 9.14315C174.316 9.28359 174.474 9.47318 174.592 9.71192C174.713 9.94786 174.775 10.2175 174.778 10.5208H173.834C173.834 10.2203 173.734 9.98297 173.535 9.80882C173.338 9.63187 173.059 9.5434 172.696 9.5434C172.345 9.5434 172.076 9.62345 171.888 9.78354C171.702 9.94364 171.609 10.1403 171.609 10.3734C171.609 10.5279 171.647 10.6613 171.723 10.7736C171.799 10.8832 171.9 10.9702 172.027 11.0348C172.153 11.0994 172.299 11.1556 172.465 11.2034C172.63 11.2511 172.805 11.2975 172.987 11.3424C173.17 11.3845 173.352 11.4323 173.535 11.4856C173.717 11.5362 173.892 11.605 174.057 11.6921C174.223 11.7792 174.369 11.8845 174.495 12.0081C174.622 12.1288 174.723 12.2889 174.799 12.4884C174.875 12.6878 174.913 12.9181 174.913 13.1793C174.913 13.7017 174.716 14.1315 174.323 14.4685C173.932 14.8056 173.399 14.9741 172.722 14.9741C172.073 14.9741 171.539 14.7915 171.121 14.4264C170.705 14.0585 170.497 13.5852 170.497 13.0066ZM175.932 13.2467V10.3481H176.838V13.0824C176.838 13.397 176.933 13.6512 177.124 13.845C177.315 14.0388 177.556 14.1357 177.845 14.1357C178.162 14.1357 178.423 14.029 178.628 13.8155C178.836 13.5992 178.94 13.3268 178.94 12.9982V10.3481H179.846V14.8604H178.966V14.2579H178.907C178.808 14.4601 178.643 14.63 178.409 14.7677C178.179 14.9053 177.905 14.9741 177.588 14.9741C177.085 14.9741 176.683 14.8112 176.383 14.4854C176.082 14.1596 175.932 13.7467 175.932 13.2467ZM181.173 14.8604V8.389H182.079V11.0053H182.13C182.175 10.9323 182.234 10.8579 182.307 10.7821C182.382 10.7062 182.479 10.6248 182.597 10.5377C182.718 10.4478 182.867 10.3748 183.044 10.3186C183.224 10.2624 183.415 10.2343 183.617 10.2343C184.243 10.2343 184.756 10.4576 185.155 10.9042C185.553 11.348 185.753 11.9196 185.753 12.619C185.753 13.3184 185.551 13.8857 185.146 14.3211C184.742 14.7564 184.214 14.9741 183.562 14.9741C182.953 14.9741 182.469 14.7227 182.113 14.22H182.054V14.8604H181.173ZM182.054 12.6063C182.054 13.0473 182.179 13.4153 182.429 13.7102C182.679 14.0051 183.014 14.1525 183.436 14.1525C183.857 14.1525 184.194 14.0121 184.447 13.7312C184.702 13.4504 184.83 13.0754 184.83 12.6063C184.83 12.1513 184.702 11.7806 184.447 11.4941C184.194 11.2076 183.863 11.0643 183.453 11.0643C183.045 11.0643 182.71 11.2034 182.446 11.4814C182.184 11.7567 182.054 12.1317 182.054 12.6063ZM186.853 14.8604V10.3481H187.733V10.9422H187.792C187.899 10.7343 188.06 10.5644 188.277 10.4324C188.493 10.3004 188.754 10.2343 189.06 10.2343C189.378 10.2343 189.654 10.3018 189.89 10.4366C190.126 10.5714 190.31 10.7568 190.442 10.9927H190.501C190.788 10.4871 191.251 10.2343 191.891 10.2343C192.386 10.2343 192.783 10.3902 193.084 10.702C193.387 11.011 193.539 11.4112 193.539 11.9027V14.8604H192.633V12.2103C192.633 11.848 192.55 11.5699 192.384 11.3761C192.219 11.1795 191.985 11.0812 191.685 11.0812C191.39 11.0812 191.144 11.1851 190.948 11.393C190.754 11.598 190.657 11.8761 190.657 12.2272V14.8604H189.751V12.1092C189.751 11.7974 189.661 11.5488 189.481 11.3635C189.302 11.1753 189.067 11.0812 188.778 11.0812C188.489 11.0812 188.246 11.1865 188.049 11.3972C187.855 11.605 187.758 11.8733 187.758 12.2019V14.8604H186.853ZM194.702 9.0631C194.702 8.89739 194.758 8.76116 194.87 8.65443C194.982 8.5477 195.124 8.49433 195.296 8.49433C195.473 8.49433 195.617 8.5477 195.73 8.65443C195.845 8.76116 195.902 8.89739 195.902 9.0631C195.902 9.23443 195.845 9.37347 195.73 9.4802C195.617 9.58693 195.473 9.6403 195.296 9.6403C195.121 9.6403 194.978 9.58693 194.866 9.4802C194.756 9.37347 194.702 9.23443 194.702 9.0631ZM194.841 14.8604V10.3481H195.746V14.8604H194.841ZM196.677 11.0896V10.3565H197.272C197.35 10.3565 197.415 10.3298 197.465 10.2765C197.516 10.2231 197.541 10.1515 197.541 10.0616V9.07153H198.392V10.3481H199.707V11.0896H198.392V13.4026C198.392 13.8632 198.611 14.0936 199.049 14.0936H199.66V14.8604H198.91C198.461 14.8604 198.111 14.7382 197.861 14.4938C197.611 14.2466 197.486 13.8913 197.486 13.4279V11.0896H196.677Z"
            fill="white" />
    </svg>
    </div> 
    </div> 
    </div> 
    `
    return html
}

function build_file_attach_preview(file_type, full_width=false) {
    let file_name = ""
    if (file_type == "image(ex. .jpeg, .png, .jpg)") {
        file_name = ".jpeg, .png, .gif, .jpg"
    } else if (file_type == "word processor(i.e. .doc,.pdf)") {
        file_name = ".doc, .docx, .odt, .pdf, .rtf, .tex, .wks, .wkp"
    } else if (file_type == "compressed file(ex. .zip)") {
        file_name = ".zip, .rar, .rpm, .z, .tar.gz, .pkg"
    } else if (file_type == "video file(ex. .mp4)") {
        file_name = ".mp4"
    }
    let style = ""
    if (full_width) {
        style = "style='width: 100%'"
    }

    let html = `
        <div class="attachment-widget-response-bot-preview-wrapper preview-attachment-widget-container" ${style}>
            <svg width="42" height="41" viewBox="0 0 42 41" fill="none" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
            <rect x="0.959473" y="0.509766" width="40.161" height="40.161" fill="url(#pattern0)"/>
            <defs>
            <pattern id="pattern0" patternContentUnits="objectBoundingBox" width="1" height="1">
            <use xlink:href="#image0_1512_243677" transform="scale(0.00195312)"/>
            </pattern>
            <image id="image0_1512_243677" width="512" height="512" xlink:href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAgAAAAIACAYAAAD0eNT6AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAACAASURBVHic7d1rkFxnfefx39Onu6fnKll32VZsXWxJlrls4uDFgC3J9tpJ1oQFQgi7IUC2sikW2M0LMMtShMAmRZZsKLLspWIo2HJIsWQrgMOaYCyNjcFeiEmBQdaMJFsGgdHV1mVGM9N9+jz74misizWjnpnT5znPeb6fqi4blzX9p7vdz3fO1QiltP+wXWVN+xVJYjcaYzZK9lpJKyX1n3ksdjshyiqxkqyUSLJWShIpPvNoJ1IrkVrt9O8vpmJsksjERpqSNUcT2UkjHZP0nGSOGdljidWhSsUcUDv5sWztmW1bzMEc/y8CpWBcD4Bs7N1rezTYvrNS0e2ydpuMrnM9EzCbdiJNxWcfzViy8/9xk5KekbTLGP3QJuZHkY2fOLS55+k3GdPOaGSgVAgAz+0/2PynSVR5qxL7mzJa4noeYL4SK0220sfp1sxbCObotJG+Z6XHJPNoqxo9dscGcziTnwx4jgDwkLXW7D/avsvKfkBWN7qeB8iclSZiabwpnZ5a0JaBFzNmnxINS/q6aUQ7tq01x7P88YAvCADPPH0kfq219j9JeonrWYA8JFY63ZTGptJdBRmLJX1H0tcTJV+5bVPPE5k/A1BQBIAnRo/aK6pJ/AlJv+F6FsCVqVg6MSlNNLv1DPYZydxnjP5m67XVbxtjMt34ABQJAVBw1lrz9JHWeyTzJ5L6XM8DFMFULJ2YkCZaXXwSY/ZJ9t4oqn72lg3mQBefCXCCACiwp56zixTH94jf+oGLaral50+nBw52USLpG1bmM1NRdN+vXmOmuvpsQE4IgILaf7j58sToy7LmKtezAEU31pSOn87szIHZHJXRX1bb1U/dfJ35edefDegiAqCA9h5pba1YfVnSItezAL5IrHR8QhqbzPisgYtrGukrSuyfb7uu/v+6/3RA9giAgtl3KP4Xxti/ltRwPQvgo6lYOjqWXnkwD0YatlZ/tH1z7eF8nhHIBgFQIE8diX9N1n5ZUtX1LIDPrJWOjqenD+bo2zL6w+0baztyfVZgngiAgth/sHljUjE7lF6nH0AGTk1Jz4/nskvgXDsTqw/etrn2WL5PC8wNAVAATx+Z3GiT6FEu5Qtkr9WWDp/Kb5fAGdZa+79la++/9Trz41yfGegQAeDY/v22kfTHj0l6uetZgLJqJ9LhsfSGQzlrSvqf7Vr1Q7evNydyf3ZgFhXXA4Su3d/+r2LxB7oqqkgrB6VGLfenrkt6T9SKR4ZH4zfn/uzALNgC4NDTh+M3Wtm/cT0HEApHBwe+wEhfk43fuW1z7zNuJgDOIgAcGTliB2s23i3pCtezACGxSg8MPOXuen7jMvrQ0Wurn3yTMW1nUyB47AJwpGbjj4jFH8idkbSkXxqoOxuhX1b/Zdlo/OjDT05e42wKBI8tAA7s/fnUlkpU+b443x9wx6YHBnb1hkKXdtrIfmDbpvonnU6BIBEADjx1qPl5GfMW13MAobNWOnjKydkB5zFWX1Kl+nvbNpqjbidBSAiAnO05NLkuMtGo+O0fKIS2lQ6elGL3e+N/ahL7G9xbAHnhGICcVVW9Wyz+QGFERloxIFXc/zp0pa2YR4ZHWne7HgRhcP+RD8jBg7Z/vBIflDTgehYA5xubko6Nu55imv3r1lTt9+54mSnMRCgftgDkaMy03yAWf6CQBnqkfndnBlzAvKXWE3/74X12jetJUF4EQI5Mxf626xkAzGxJv1SLXE/xgpe14/g7wyPNG1wPgnIiAHJy4IRdIqttrucAMLOKkZYNqEg7R1dbmeEdu+O7XA+C8iEActKcbG+VVJzfLQBcVD2ShnpcT3GeAWPsl4ZHm//W9SAoFwIgJ9bw2z/gi0W9UrViXY9xrsha86kdI62PuR4E5UEA5MQYSwAAnqgY6bK+4uwHmGaku3eOtP7UWlu84eAdAiAHu6yty2qj6zkAdK6vLvXmf/vgTrzvodH2f/+wtXx/Y0H4AOWg/lxzg7j4D+CdJX0q0gGBL7Cyv3/zaPseIgALwYcnB5U42uR6BgBzV42k/mJuBZBk3/GaPe3PEAGYLz44OTCy61zPAGB+FvUWciOAJMlY+zYiAPPFhyYHidFi1zMAmJ9alB4PUFREAOaLD0wODJf/Bbw21Ot6gtkRAZgPPiy5MIOuJwAwf/WosGcEvMBY+7abR9ufJgLQKT4oebBJwX9/AHApgw3XE3TCvp0tAegUHxIA6EBvNb1AUNGxOwCd4gMCAJ0wRbpd8OyIAHSCDwcAdKjfi90AKSIAl8IHAwA61BOlpwX6ggjAbPhQAMAcFPmaABfD2QGYCR8IAJiDhpd39eDsALwYHwYAmIOeWnEvDTwbdgfgQnwQAGAOjNII8BERgHPxIQCAOfJzN0CKCMA0H7dk5W541C6zNt5orNlgK0m/sWbQGi2ytrOAWj2ku3qquq7bcwLIx1QsHTzpeoqFscZ87pFro9/9sDGJ61ngBgFwgfv32p4eG9+otrYbo62Srpe0dCE/c1m/1N+TyXgACsBa6cDx9K8+IwLCRgBIevxxWzvR375Txr7VSL8mKdNr9xMAQPk8e0JqtV1PsXBEQLiCDoAHRuzlNcV/YKXfkbS8W89DAADlc3RcGp9yPUVWzGe/uTH610RAWIIMgIdHJta2Vbtbsm+T1PWlmQAAyuf4hHRiwvUU2WFLQHiCCoBHD9jeibH4bmP0fuWw8E8jAIDyGZ9KtwKUCREQlmBOAxneHf/zyfHWk8boD5Xj4g+gnCKP7gnQKS4bHJbSv8n377U9O0dan7TG3ieZqx2PA6AkqqXdfsplg0NR6jd4eNfkhkY7flTSexTY7g4A3VUp8TcKFwsKQ2nf3AdHm79so+gxSb/oehYA5VOpqNS/VhAB5VfKN3Z4T+u2ijU7JC1zPQuA8irlF+g5iIByK92bunN3/Hqb6H5Jg65nAQDfEQHlVao3dHh3a6uM/bwkT+/VBcAnpsS7AM5FBJRTad7MB0emXmqNviSp4XoWAGEIZP2XxCmCZVSKN/Lvd9klFZn7JC12PQsAlBenCJaJ92+itdbUo/izkrnK9SwAUHbsDigP79/A4dH4vZJe63oOAAgFEVAOXr95Dz85eY2kj7ieAwBCQwT4z+s3rl2J/kJc1x8AnCAC/ObtmzY8Gr9Z0p2u5wCAkBEB/vLyDfuitZGVPup6DgAApwj6yss3a/lo+7dk7QbXcwAAptm3EwF+8e6NstYaK3u36zkAABciAnzi3Zv00Gh8h6TrXc8BALgYIsAX3r1B1ti3up4BADAbIsAHXr059++1Q7Lm113PAQC4FCKg6Lx6Y3rj1usl9bmeAwDQCSKgyLx6UxLpDtczAADmgggoKm/eEGutMcZsdT0HAGCuiIAi8ubNGH6yeZ2kVa7nAADMBxFQNN68EaZqXul6BgDAQhABReLNm5DIbHI9AwBgoYiAovDpDdjoegAAQBaIgCLw5sU3Vte6ngEAkBUiwDWfXngOAASAUiECXPLiRbfWGkn9rucAAGSNCHDFixf8gSfUJylyPQcAoBuIABe8eLGjigZczwAA6CYiIG9evNBJjd/+AaD8iIA88SIDAAqECMgLLzAAoGCIgDzw4gIACogI6DZeWABAQREB3cSLCgAoMCKgW3hBAQAFRwR0Ay8mAMADREDWeCEBAJ4gArLEiwgA8AgRkBVeQACAZ4iALPDiAQA8ZN9+82j7HiJg/njhAGCejHE9QejsO9gSMH+8aAAwT3yBFgG7A+aLFwwA5oktAEVBBMwHLxYAzFOFb9AC4ZiAueKFAoB5qvINWjAcEzAXvEgAME/1yPUEeLF0S4C1lh00l0AAAMA8VQmAgrLvGB5tf8r1FEVHAADAPNUiSfyeWVD2nTtHWn/qeooiIwAAYJ4qRurhW7TI3rdjpPVB10MUFR9dAFiARt31BJiNkT66Y3fz3a7nKCICAAAWoFFzPQEuxRjziZ0j8Wtdz1E0BAAALEAjkiK+SYsukuwXdu5p3uh6kCLhYwsAC2GkPnYD+KBXifnSjiftVa4HKQoCAAAWaIAA8MVqVeK/G95lB1wPUgQEAAAsUL2aPlB8RnpJUmnd43qOIiAAACADixquJ0CnjDFv3jHS/Peu53CNAACADPTVz1wYCF4wMh/fsad1s+s5XCIAACAji3tdT4A5qJpEX3jwh3al60FcIQAAICN9da4L4JnVlVr8v0K9cRABAAAZWtLH7QE8c8fO0dbvux7CBQIAADJUi6QhdgV4xcj82c6RyY2u58gbAQAAGVvckHo4LdAnfVL0V48/boPagUMAAEDWjLR8IL1bILxxw8n++L2uh8gTAQAAXRBVpGUD4oAAnxh9cHjX5AbXY+SFAACALumtScs4KNAnvTaK7gnlrAACAAC6qL9HWtznegrMwdaHRtpvdT1EHggAAOiyoYZ0GRHgDWvsnz3yhL3M9RzdRgAAQA6GGtJSjgnwxbK4Hn/I9RDdRgAAQE4G6tKKAanCN2/hWemdD+6evNb1HN3ExxAActRbk1YPcp0AD9QrJvq46yG6iQAAgJxVI2nl4JlbCLNLoMheu2Oktd31EN1CAACAA8akZwesHmJrQJEZ6T+X9bRAAgAAHKpH0qohaWm/VOUbuYh+aXhP+1dcD9ENfNwAoAAGeqTLF6dXD6xFrqfBeaz9SBm3AhAAAFAQRlJ/XVq9SFo5lF5EyJRu2fHSLw3vbf+q6yGyRgAAQMEYSY2qtKxfuvLMVoGBBlsGnEps6a4LQAAAQIFVTLpVYGmfdPmiNAiWD6RXFhzoSUOhHqXHD1Qq4qyC7nnFjj2tm10PkSWOPQUAj0QVqa/ueor5sZKsldqJlJz5a9yW4iR9NNvpPyusRH8g6Zuux8gKAQAAyIVRekxDZZZdGYmVpuJzHq00HIrASK/dsXdy/a3XNJ5yPUsW2AUAACiMikmvlri4N71Y0pol6V8HG+nWD+fjJdV/53qIrLh/OQEAmIGR1KhJS/qkKxZLKwbTeypUXB3rYO3bvzViBx09e6YIAACAF4zSrQNLB86eHdHIf0f2QMu0fjP3Z+0CAgAA4B1z5uyIlUPplRR78zww0pp35PhsXUMAAAC81lNNb7O8elG6e6Dbewes9MoH905d1+Wn6ToCAABQCvUo3T2welF63EA3maTi/VYAAgAAUCq1M7dbXtbfvTMHjNW//KK1Xl+bkQAAAJRSf0969cShhrqxX2DV8pH4NZn/1BwRAACA0qqY9LLJqwelasa/r1uZN2b7E/NFAAAASq9elS4/c4fFzBj7Bp93AxAAAIAgGJMeF7BsILMLCa1aujd+VSY/yQECAAAQlOnrB1QzWAFNW69b+E9xgwAAAASnHqUXEKov/EqCd2QwjhMEAAAgSFFFWjWYXl543oyu+8Yu+wuZDZUjAgAAECxjpOUDUt8CLiVcjVq3ZzdRfggAAEDQjEkPDBxozO/PJzJ3ZjtRPvK/jxJQIhMt6ecnpWNj0qkpabIlWddDoZCqlfQ69Yv70gPQlvalCw+KwSi95bBNpPHmnP/sNmutMcZ49Z8/AQDMkbXSgePS6CHp0Kn0fwOdOCxJx9K/76tL65dJm1Z2/7r16IxReppgYtO4n4OlD+1pbpQ00pXBuoQAAObg0Cnpu89IxydcTwLfnW5KP3xWevKgtGW1dP3lUsQWAffOHBNw8JTUjDv/Y9aam+RZAHAMANABa6V//In0wG4Wf2SrnUhP/Ez6vz+STvDZKgRjpBVzvHSwVeWV3ZuoOwgA4BLiRNq5R9p10PUkKLMTE9L9T0rPnnA9CaR0a8yKOVwx0Fh7U3cnyh4BAMwiSaSH9/KljHzEbWl4b3pgKdyrRemNhDpitPn+vXaoqwNljAAAZvHYfhZ/5CtJpG/uk8amXE8CSRroSc/e6ICpx/GWLo+TKQIAmMHTx9IHkLdmLD3yFGeYFMWS/nRrwKVUZF/S/WmyQwAAFzEVS4//2PUUCNnRMWnPEddTQDp7oSBd6niASuX6PObJCgEAXMTug2kEAC498bP0IFS4V4+kRT2z/zvGWgIA8FnbSqOHXU8BpFeW3H/U9RSYtqg3vYHQTKzEMQCAz376/NwuAAJ001MEQGEYc8mzAlZ8a8QO5jTOghEAwAV+etz1BMBZR8fZHVUk/fXZbx/cbDe9uTUwAQBc4PAp1xMAZ1nLZ7JoLuub5XjAWnR1jqMsCAEAnKM9jzuBAd12ctL1BDhXLZL6Zjgg0Njk6lyHWQACADjHRItzr1E8RGnxLGrMsBXAmqvznWT+CADgHJxyhSJqtV1PgAvVIqn3IlcItNauyH+a+SEAAKDguEtwMS3qvdg/NUvznmO+CADgHFX+i0ABzeW2tMhPPZIaF54RUBEBAPior56e6wsUycAlrkAHdwYveG+sJQAAL1UMX7YonqGG6wkwk95a+r0xzYgAALy10pvreCEExkgrBlxPgZkY86JTAr15twgA4AJXLnY9AXDWikGpXnU9BWYzcP7ZAHVrrRc7EgkA4AJXLJJ6+MJFQazzZoNyuHqq5x9A/LV9usgJgsVDAAAXqFSkzStdTwGk+5fXLnM9BTrRd/6S78WRRAQAcBGbVs1+ww8gDy+/Uoq82JiMc08HXGa0yN0knSMAgIuoRdIvX+V6CoRs5aC0nt/+vdFTPXsKca3hx5kABAAwg6uWSNd4c1FPlElPVXr1eq5J4ZOKkXrOXLDJGD8u3kgAALO48SrpCs4KQI6qFWn7tS/apwwP9Hi225AAAGZhjLT1mnRrANBt9ap060ZpmTdnkuNcDc/OHvJsXCB/FSO9Zr20uFd64lluF4zuWNov3byBK1H6rKfm142bCACgA8ZIL70ivUjQd5+Rjoy7nghlUYukl14ubV7FPn/fGfl14yYCAJiDJf3SnVukZ09Iew5LPz3OFgHMz1AjPcr/2hVc6a9MagQAUG6XL0ofzVg6dEo6Oi6dnJCm2lKr7Xo6FE3FpLeOHeiRFvdJqwZnupc8fEcAAIGoV6U1l6UPAIg8OrTeo1EBACg2n7YAEAAAAGTEp0s3EwAAAGSkQgAAABCeyEg1Ky/ODSIAAADIipGm2mq6HqMTBAAAABnqqRAAAAAEpxERAAAABKdWU+x6hk4QAAAABIgAAAAgQAQAAAABIgAAAAgQAQAAQIAIAAAAAkQAAAAQIAIAAIAAEQAAAASIAAAAIEAEAAAAASIAAAAIEAEAAECACAAAAAJEAAAAEKCq6wEA+C9JpGOnpaNj0qlJaTKWmrEUVaR6JA00pMW90opBqbfmeloAEgEAYAEOnpT2HZUOPC/F7c7+zNIBae0SacNyqRZ1dz4AMyMAAMzZwZPS9w5Iz43P/c8eG0sfP/iZtGmVdP1qqcrOSCB3BACAjrXa0neekfYfy+Zn/fBn0tNHpZvWSquGFv4zAXSO7gbQkeMT0ld/lM3if67xKenB0TQGAOSHLQAALunImLRzT3pgXzdYK33/Z9J4S7rxKsmY7jwPgLPYAgBgVkfG0t/Qu7X4n2vvYelbT6dBAKC7CAAAM5pe/Ds9wj8LzxwjAoA8EAAALsrF4j+NCAC6jwAA8CIuF/9pRADQXQQAgPMUYfGfRgQA3UMAAHhBkRb/aUQA0B0EAABJxVz8pxEBQPYIAACFXvynEQFAtggAIHA+LP7TiAAgOwQAEDCfFv9pRACQDQIACJSPi/80IgBYOAIACJDPi/80IgBYGAIACEwZFv9pRAAwfwQAEJAyLf7TiABgfggAIBBlXPynEQHA3BEAQADKvPhPIwKAuSEAgJILYfGfRgQAnSMAgBILafGfRgQAnSEAgJIKcfGfRgQAl0YAACUU8uI/jQgAZkcAACXD4n8WEQDMjAAASoTF/8WIAODiCACgJFj8Z0YEAC9GAAAlwOJ/aUQAcD4CAPAci3/niADgLAIA8BiL/9wRAUCKAAA8xeI/f0QAQAAAXmLxXzgiAKEjAADPsPhnhwhAyAgAwCMs/tkjAhAqAgDwBIt/9xABCBEBAHiAxb/7iACEhgAACo7FPz9EAEJCAAAFxuKfPyIAoSAAgIJi8XeHCEAICACggFj83SMCUHYEAFAwLP7FQQSgzAgAoEBY/IuHCEBZEQBAQbD4FxcRgDIiAIACYPEvPiIAZUMAAI6x+PuDCECZEACAQyz+/iECUBYEAOAIi7+/iACUAQEAOMDi7z8iAL4jAICcsfiXBxEAnxEAQI5Y/MuHCICvCAAgJyz+5UUEwEcEAJADFv/yIwLgGwIA6DIW/3AQAfAJAQB0EYt/eIgA+IIAALqExT9cRAB8QAAAXcDiDyIARUcAABlj8cc0IgBFRgAAGWLxx4WIABQVAQBk5PiEtIPFHxfxzDHp8Z+4ngI4HwEAZKBtpYf2Si0Wf8xg5JD0k+ddTwGcRQAAGdhzSDo16XoKFN33fsKuABQHAQBkYO8R1xPAB2NT0sFTrqcAUgQAsEBTsXRiwvUU8MWhk64nAFIEALBA41OuJ4BP+LygKAgAAMiTcT0AkCIAgAUa6HE9AXzSz+cFBUEAAAtUr0qLel1PAV+sGHA9AZAiAIAMrF/megL4oK9HWj3kegogRQAAGdi4Quqru54CRfdPrpAMxwCgIAgAIAPVSHr1OqnCf1GYwdVLpXVsKUKB8HUFZGTlkHTLhjQGgHNdvVR61VrXUwDnIwCADF25WLrreukXLmNTL9IzRF61Xnr1erYOoXiqrgcAymagR7rlGul0M73s66lJqZ109zmfPy09e6K7z1EGPVVpw/LuP09fTVo6IC3rJwRRXAQA0CV9dWnd0nyea98RAqATjZr0i2tcTwEUAxulAAAIEAEAAECACAAAAAJEAAAAECACAACAABEAAAAEiAAAACBABAAAAAEiAAAACBABAABAgAgAAAACRAAAABAgAgAAgAARAAAABIgAAAAgQAQAAAABIgAAAAgQAQAAQIAIAAAAAkQAAAAQIAIAAIAAEQAAAASIAAAAIEAEAAAAASIAAAAIEAEAAECACAAAAAJEAAAAECACAACAABEAAAAEiAAAACBABAAAAAEiAAAACBABAABAgAgAAAACRAAAABAgAgAAgAARAAAABIgAAAAgQAQAAAABIgAAAAgQAQAAQIAIAAAAAkQAAAAQIAIAAIAAEQAAAASIAAAAIEAEAAAAASIAAAAIEAEAAECACAAAAAJEAAAAECACAACAABEAAAAEiAAAACBABAAAAAEiAAAACBABAABAgAgAAAACRAAAABAgAgAAgAARAAAABIgAAAAgQAQAAAABIgAAAAgQAQAAQIAIAAAAAkQAAAAQIAIAAIAAEQAAAASIAAAAIEAEAAAAASIAAAAIEAEAAECACAAAAAJEAAAAECACAACAABEAAAAEiAAAACBABAAAAAEiAAAACBABAABAgAgAAAACRAAAABAgAgAAgAARAAAABIgAAAAgQAQAAAABIgAAAAgQAQAAQIAIAAAAAkQAAAAQIAIAAIAAEQAAAASIAAAAIEAEAAAAASIAAAAIEAEAAECACAAAAAJEAAAAECACAACAABEAAAAEiAAAACBABAAAAAEiAAAACBABAABAgAgAAAACRAAAJVAxrifwA68TcBYBAJRAo+Z6Aj80qq4nAIqDAABKYKjhegI/DPW6ngAoDgIAKIGBHmkxi9slrbnM9QRAcRAAQElsWe16gmJb0ietGnQ9BVAcBABQEmuXSiuHXE9RTBUj3bhWMhwECLyAAABKwhhp6wZ2BVzIGOmmtdKyfteTAMVCAAAlUq9Kv3JdujUA0kDd6vaN0tplricBioeTYoCSqUbSq9dLm1dK+45Kz56QxpuSta4ny0dPNd3ff9USaf1yw7n/wAwIAKCklg6kD0myklqx03FyEUVSxIIPdIQAAAJglO4eAIBpHAMAAECACAAAAAJEAAAAECACAACAABEAAAAEiAAAACBABAAAAAEiAAAACBABAABAgAgAAAACRAAAABAgAgAAgAARAAAABIgAAAAgQAQAAAABIgAAAAgQAQAAQIAIAAAAAkQAAAAQIAIAAIAAEQAAAASIAAAAIEAEAAAAASIA8mBcDwAAyEucqO16hk4QADlIrOsJAAB5qTV10vUMnSAAckAAAEAw4jVrzITrITpBAOTAEgAAEIox1wN0igDIQZsAAIBQHHQ9QKcIgBy0vDgcBACwYEYjrkfoFAGQg5gAAIAwWI26HqFTBEAO2gkHAgJAGCwBgPNNxa4nAAB0mzHJo65n6BQBkJPJlusJAADdZKVn1y1vsAUA55tkCwAAlJuxO1yPMBcEQE5acXosAACgnIwqX3c9w1wQADmxksabrqcAAHTJ+KSNvuJ6iLkgAHJEAABAOVlj/3bLCuPNVQAlAiBXzZiLAgFAGVUSc6/rGeaKAMjZyUnXEwAAMmW0a+2KqlcHAEoEQO7GmlLMwYAAUBrWmo8aY7z7ZicA8malU2wFAICSMPvWL4/+j+sp5oMAcODUJPcHAIAysFbvNcZ4+Y1OADhgJT132vUUAICFsNLXN6ysftn1HPNFADgy0eK0QADw2JQx7fe4HmIhCACHnj/N1QEBwEvGvn/98sYe12MsBAHgUDuRjo6nuwQAAN746rpltU+6HmKhCADHJlvSyQnXUwAAOmMPNJvVtxljvP/djQAogBMTHA8AAB44Yazu2nylOeZ6kCwQAAVgJR0bTw8MBAAU0qSR7lq3sv4D14NkhQAoCGulo2PSVOx6EgDAeaya1prfWrei9ojrUbJEABRIYqXDp9LjAgAAhTBujXmdz+f7z4QAKJjESofHpNMcEwAAThnpWGJ1+4YV1a+5nqUbCIACslY6MnbmaoHeH2cKAF56PLbtV1yzsvaY60G6hQAosFOT0qFTXCwIAHJkjfQXk8urr7p2ZeNp18N0U9X1AJjdZCw9e0Ja0if197ieBgBKba+xete6lbUHXA+SB7YAeCCx6RUDD56Uml7ecwoABUSl6AAABSJJREFUCm1CVn9UGa++NJTFX2ILgFemYunnJ6WBmjTUK9Ui1xMBgNcmjMynkyj6+Ial5oDrYfJGAPjGSmPN9MqBvXVpqCH18C4CwFwckvQ5Y6ufWLfSHHI9jCssHZ6ySk8VPN2UqpX0+ID+OlsFAGAGY7L2PpnK53+yPHpgmzHBX3aNACiBOEnvJ3BiQqpG6RaB3ppUj6RaRZJxPSEA5O6IjJ6w0sNKtPPAiup3WPTPRwCUTNxOH+NTZ/6BSSOgFkmVSnrUpzFShSgAUFDVSE/21fR3nfy7Vmob6aSsPWFUGTM22Vftre1Zs8g81+05fUcAlJ2VWu30AQBeMPYH2zfW3+96jLLjNEAAAAJEAAAAECACAACAABEAAAAEiAAAACBABAAAAAEiAAAACBABAABAgLwIgEYi63oGAADKxIsAaPdqwvUMAICc2Mpp1yOEwIsA0DMacz0CACAfRvaU6xlC4EUAbNtmYkmTrucAAHSftTrpeoYQeBEAZxx3PQAAIAcVnXA9Qgh8CoCnXA8AAMiBNftcjxACjwLAjLqeAACQh5jv+xx4FACWDwQAlF88NNbztOshQuBPAFj9wPUIAICue/KGG0zL9RAh8CYAxserj0hqup4DANA9RtrpeoZQeBMAd91gTkv6rus5AADdk1hDAOTEmwCQJFnKEABKLE7q0TddDxEKvwIgSb7oegQAQHcY6Ru3rzdcAyAnXgXA9i09uyR93/UcAIDsJdbc63qGkHgVAJIkIz4gAFA+Y3Ezus/1ECHxLgCqleq9krhTFACUirn3jpeZcddThMS7ALj5GnNE0qddzwEAyEwrUuvjrocIjXcBIEkmqn5cXBMAAErC/NUtm3r3u54iNF4GwLZrzE8l8xnXcwAAFqyZ2PhjrocIkZcBIEnNdvRBSUdczwEAmD9j9ee3bW7scT1HiLwNgDu3mOeMsR9wPQcAYL7sASXVP3Y9Rai8DQBJ2npt7TNGesT1HACA+ai8a9sWM+Z6ilB5HQDGGKuo+hZJR13PAgDonDHmU9s3VTnv3yGvA0A6c0CgMb8jybqeBQDQkSd6+qL3uR4idN4HgCRt31i930p/4noOAMAlHbFR+/U3rTETrgcJnXE9QFastWZ4tH2PZH/X9SwAgIs6nVjddtvm2mOuB0FJtgBI6fEARzdG/0ZGf+t6FgDAi7SM9AYW/+IoTQBI0puMaTf6qv9KEgeWAEBxTEjmjds21f7e9SA4q1QBIEk3rTETRzdWXy9j/tL1LAAAHU+M7uCI/+IpzTEAF7LWmof2xB+yVh9SCUMHAArPmH2K26/bvqVnl+tR8GKlDYBpD460tlWkz0ta7XoWAAiFsfqSGtV3bFtrjrueBRdX+gCQpG8+aVfHlfhzkv6Z61kAoOTGrOz7bt1U/x+uB8HsggiAaTt2x3cZk/w3yaxxPQsAlI01+qra1Xfdep35setZcGlBBYAk3b/XDjXa8X+U9E5JA67nAYAS+Edr9R9u3Vx7wPUg6FxwATDtwd12qVH8bmP0bklLXM8DAB561Frzse2boq8aY7gcu2eCDYBp3xqxgy3beoM15rclbRVnDADAbI7ImC8kSu69bWP9H1wPg/kLPgDO9fA+uyZutX69IrPdGt0itgwAgLXSjyTtlDFfX3QqevCGG0zL9VBYOAJgBh+2trJtX+tl7aTyEslulNVGSVdL5jLJDio9fqDX7ZQAkInnJY1LGpN0SNbsMbKjNjIjrUr0D3dsMIcdz4cu+P/SjihghBhptgAAAABJRU5ErkJggg=="/>
            </defs>
            </svg>
            <div class="preview-attachment-text-one">Drag and browse your files</div>  
            <div class="preview-attachment-text-two">${file_name}</div> 
            <div class="preview-attachment-text-three">Maximum allowed file size: ${attachment_max_file_size}MB</div>        
        </div>
    `

    return html
}

function build_preview_file_widget_response(file_type) {
    if (!$("#checkbox-intent-attachment").prop("checked")) {
        return ""
    }
    let html = `
    <div class="preview-user-message-wrapper">
        ${build_file_attach_preview(file_type)}
    </div>
    `
    return html
}

function build_preview_phone_widget_response() {
    if (!$("#checkbox-intent-country-code-cb").prop("checked")) {
        return ""
    }
    let html = `
    <div class="preview-user-message-wrapper">
    <div class="attachment-widget-response-bot-preview-wrapper" style="width: 90%">
        <div class="easychat-country-dropdown-preview-wrapper" id="telephone-preview-wrapper-only-phone">
            <input style="border: none !important; pointer-events: none !important;" readonly type="tel" placeholder="Enter Mobile Number" id="telephone-preview-only-phone" class="phone-number-input">
        </div>
    </div>
    </div>`
    return html
}

function get_intent_info(pk) {
    for (const intent of intent_name_list) {
        if (intent.intent_pk == pk) {
            return [intent.intent_name, intent.icon]
        }
    }
}

function build_preview_quick_recommendation(recom_list, is_menu) {
    let html = ""
    if (is_menu) {
        html += `
        <div class="preview-bot-message-wrapper quick-recom-menu-preview">
        `
        for (const recom of recom_list) {
            let [name, icon] = get_intent_info(recom)

            html += `
                <div class="intent-menu-bot-preview" title="${name}">
                    ${name}
                </div>
            `
        }
    } else {
        html += `
        <div class="preview-bot-message-wrapper quick-recom-preview">
        `
        for (const recom of recom_list) {
            let [name, icon] = get_intent_info(recom)
            icon = icon ? icon : `<svg width="30" height="29" viewBox="0 0 30 29" fill="none"
            xmlns="http://www.w3.org/2000/svg">
            <path fill-rule="evenodd" clip-rule="evenodd"
                d="M14.5671 0.725625C14.1429 0.810801 13.7951 1.04558 12.7918 1.92362L11.8016 2.79044L7.33447 2.80579L2.86732 2.82119L2.73062 2.98246L2.59393 3.14373V6.94835V10.753L1.76911 11.4621C1.31546 11.8522 0.920331 12.2353 0.891043 12.3134C0.858753 12.3997 0.837793 15.6081 0.837793 20.4752C0.837793 29.2355 0.820741 28.7808 1.15475 28.9352C1.25938 28.9836 4.88919 29.0007 15.0638 29.0007H28.8313L28.9969 28.8327L29.1625 28.6647V20.4702V12.2757L28.9471 12.0602C28.8286 11.9416 28.4468 11.5989 28.0986 11.2986L27.4656 10.7526L27.4643 7.00513C27.4634 4.22453 27.4456 3.21879 27.3953 3.10695C27.2499 2.78314 27.3912 2.79245 22.6308 2.79245H18.2462L17.2888 1.9539C16.2173 1.01541 16.0239 0.882817 15.5406 0.755109C15.1764 0.658897 14.9357 0.651598 14.5671 0.725625ZM15.4847 1.96005C15.6388 2.03966 15.9306 2.25863 16.1331 2.44669L16.5014 2.7886L15.0426 2.79056C14.2404 2.79159 13.5839 2.7809 13.5839 2.76676C13.5839 2.75256 13.792 2.55824 14.0464 2.3349C14.6772 1.78096 14.9833 1.70119 15.4847 1.96005ZM26.3295 8.8416L26.329 13.7413L23.1804 16.4713C21.4487 17.9728 19.8416 19.363 19.6092 19.5605L19.1867 19.9197H15.0053H10.8238L7.24926 16.8305L3.6748 13.7413L3.67253 8.8416L3.67027 3.94193H15.0002H26.33L26.3295 8.8416ZM14.3487 6.62368C13.4235 6.82438 12.5811 7.3194 11.8512 8.09128C10.8428 9.15771 10.3734 10.2806 10.315 11.7665C10.2762 12.7536 10.3671 13.224 10.7538 14.0373C10.9788 14.5105 11.1186 14.7145 11.4936 15.1164C11.9939 15.6526 12.6934 16.1633 13.225 16.3805C13.9361 16.6711 15.2643 16.7525 16.1552 16.5599C17.6802 16.2304 18.2815 15.7083 17.7533 15.1724C17.5212 14.9368 17.3886 14.9283 16.9585 15.1213C16.1418 15.4878 15.0732 15.635 14.231 15.4972C13.0092 15.2973 12.0262 14.4219 11.6187 13.171C11.4831 12.755 11.4673 12.6202 11.4661 11.8734C11.465 11.1112 11.4782 11.0012 11.6204 10.586C12.1045 9.17334 13.1934 8.09139 14.4597 7.76483C14.8941 7.65281 15.8276 7.65379 16.3001 7.76678C17.4127 8.03283 18.1904 8.81292 18.4786 9.95189C18.6995 10.8248 18.6382 11.7192 18.3092 12.4248C17.953 13.1887 17.229 13.5728 17.0502 13.0928C16.9282 12.7651 16.9345 12.5972 17.1255 11.0644C17.2335 10.1975 17.3221 9.41508 17.3223 9.32571C17.3226 9.22237 17.2625 9.10208 17.1572 8.99523C16.8827 8.71671 16.4588 8.78511 16.2633 9.13949C16.2245 9.20978 16.157 9.19346 15.8525 9.04035C14.9718 8.59745 13.9063 8.86971 13.1218 9.73797C12.5399 10.382 12.1898 11.5193 12.3324 12.3019C12.53 13.3866 13.3893 14.2086 14.394 14.274C14.8985 14.3068 15.426 14.1821 15.8162 13.9377L16.0941 13.7636L16.3261 13.994C16.6278 14.2937 16.9279 14.4167 17.3511 14.4142C18.0296 14.4102 18.6006 14.0535 19.0713 13.3395C19.7003 12.3854 19.8896 10.9648 19.5615 9.66061C19.3147 8.67953 18.6231 7.70436 17.811 7.19238C16.8794 6.60511 15.4879 6.37654 14.3487 6.62368ZM15.3832 10.0414C15.5215 10.1094 15.7265 10.285 15.8448 10.4369L16.0576 10.71L15.9508 11.5072C15.8344 12.3764 15.7431 12.5958 15.3847 12.8674C14.9444 13.2011 14.3057 13.2272 13.9374 12.9265C13.4824 12.5551 13.3466 12.1449 13.4691 11.5128C13.6203 10.7334 14.0423 10.2033 14.6701 10.0045C15.0098 9.89694 15.0983 9.90154 15.3832 10.0414ZM2.59393 12.5056C2.59393 12.7667 2.57818 12.7765 2.39412 12.6295L2.26139 12.5236L2.38359 12.3997C2.5562 12.2246 2.59393 12.2436 2.59393 12.5056ZM27.7445 12.4978C27.7435 12.5179 27.6798 12.5808 27.6029 12.6376L27.463 12.7408V12.507V12.273L27.6047 12.3672C27.6826 12.419 27.7455 12.4778 27.7445 12.4978ZM5.90792 17.1579C7.96429 18.935 9.65386 20.4084 9.66259 20.4322C9.67414 20.4641 3.9521 25.4809 2.15489 27.0146L1.97078 27.1717V20.462C1.97078 14.0767 1.9756 13.7564 2.06992 13.8396C2.12442 13.8877 3.85154 15.3809 5.90792 17.1579ZM28.0862 20.4657C28.0862 24.1484 28.0671 27.161 28.0437 27.1603C27.9844 27.1587 20.41 20.5365 20.3866 20.4657C20.3686 20.4116 27.9529 13.784 28.0437 13.7744C28.0671 13.772 28.0862 16.7831 28.0862 20.4657ZM23.1479 24.4171L27.0528 27.8224L21.0265 27.8371C17.712 27.8451 12.289 27.8451 8.97526 27.8371L2.95036 27.8224L6.86144 24.4171L10.7725 21.0117H15.0078H19.243L23.1479 24.4171Z"
                fill="#2741FA" />
            </svg>`
    
            html += `
            <div class="intent-icon-bot-preview-wrapper">
                ${icon}
                <div class="intent-icon-bot-preview-text" title="${name}">
                    ${name}
                </div>
            </div>
            `
        }
    }

    html += "</div>"
    return html
}

function bot_response_preview() {
    const node_data = node_intent_data[selected_node]
    const bot_response = node_data.intent_response
    const widget_data_req = bot_response.modes
    const widget_data_field = bot_response.modes_param
    const dynamic_preview = $("#dynamic_preview")
    let form_functions; 
    let form_html = ""
    let html = ""

    // Node Name
    $("#preview_node_name").text(node_data.name)
    if (!node_data.name) {
        $("#preview_node_name").hide()
    } else {
        $("#preview_node_name").show()
    }

    for (const response of node_data.order_of_response) {
        if (response === "text") {
            let text = bot_response.response_list[0].text_response
            if (text.trim()) {
                html += build_preview_text_response(text)
            }
        } else if (response === "table") {
            let table_matrix = JSON.parse(bot_response.table_list_of_list).items
            if (table_matrix.length > 0) {
                html += build_preview_table_response(table_matrix)
            }
        } else if (response === "image") {
            let images = bot_response.image_list
            if (images.length > 0) {
                html += build_preview_image_response(images)
            }
        } else if (response === "video") {
            let videos = bot_response.video_list
            if (videos.length > 0) {
                html += build_preview_video_response(videos)
            }
        } else if (response === "link_cards") {
            let cards = get_cards().filter(function(card) {
                return Object.keys(card).length > 0
            })
            if (cards.length > 0) {
                html += build_preview_card_response(cards)
            }
        } else if (response === "calendar_picker") {
            html += build_preview_calendar_widget_response(widget_data_req)
        } else if (response === "radio_button") {
            html += build_preview_radio_widget_response(Object.values(widget_data_field.radio_button_choices))
        } else if (response === "checkbox") {
            html += build_preview_checkbox_widget_response(Object.values(widget_data_field.check_box_choices))
        } else if (response === "drop_down") {
            html += build_preview_dropdown_widget_response(Object.values(widget_data_field.drop_down_choices))
        } else if (response === "video_record") {
            html += build_preview_video_widget_response()
        } else if (response === "range_slider") {
            html += build_preview_slider_widget_response(widget_data_field.range_slider_list[0])
        } else if (response === "file_attach") {
            html += build_preview_file_widget_response(widget_data_field.choosen_file_type)
        } else if (response === "phone_number") {
            html += build_preview_phone_widget_response()
        } else if (response === "quick_recommendations") {
            html += build_preview_quick_recommendation(node_data.recommeded_intents_dict_list, widget_data_req.is_recommendation_menu === "true")
        } else if (response === "form") {
            [form_html, form_functions] = build_form_widget_preview()
            html += form_html
        }
    }

    if (node_data.enable_whatsapp_menu_format) {
        html += build_preview_whatsapp_menu_format(
            Object.values(node_data.whatsapp_menu_section_objs).filter(function(section) {
                return Boolean(section)
            }),
            node_data.other_settings.whatsapp_list_message_header
        )
    }

    dynamic_preview.html(html)

    for (const response of node_data.order_of_response) {
        if (response === "image") {
            initialize_carousel(".carousel.preview-image-carousel-slider")
            $(".carousel.preview-image-carousel-slider").carousel("next", bot_response.image_list.length - 1)
            setTimeout(function() {$(".carousel.preview-image-carousel-slider").carousel("set", 0)}, 200)
        }
        else if (response === "video") {
            initialize_carousel(".carousel.preview-video-carousel-slider")
            $(".carousel.preview-video-carousel-slider").carousel("next")
            setTimeout(function() {$(".carousel.preview-video-carousel-slider").carousel("set", 0)}, 200)
        }
        else if (response === "link_cards") {
            initialize_carousel(".carousel.preview-card-carousel-slider")
            $(".carousel.preview-card-carousel-slider").carousel("next")
            setTimeout(function() {$(".carousel.preview-card-carousel-slider").carousel("set", 0)}, 200)
            let cards = get_cards().filter(function(card) {
                return Object.keys(card).length > 0
            })

            for (let i=0; i < cards.length; i++) {
                if ($(".card-response-bot-description")[i].scrollHeight / 6 > 40) {
                    $(".content-ellipsis")[i].innerHTML = "..."
                }
            }
        } 
        else if (response === "form") {
            if (form_functions) {
                form_functions.forEach(function(fn) {
                    fn()
                })
            }
            $('.easychat-form-widget-dropdown-wrapper').select2().on('select2:open', function (e) {
                $('.select2-search__field').attr('placeholder', 'Search here');
            });
        }
        else if (response === "phone_number") {
            initialize_phone_number_selector_console("telephone-preview-" + "only-phone", widget_data_field.country_code, "only-phone")
        } else if(response === "quick_recommendations") {
            $(".quick-recom-preview svg").css("min-height", "25px")
        }
    }
}

function recurse_flow_create(node_id) {
    const tree_pk = node_intent_data[node_id].tree_pk
    const node = editor.getNodeFromId(node_id)

    const output_conn = node.outputs.output_1.connections

    const flow = {[tree_pk]: {}}
    for (const con of output_conn) {
        const child_flow = recurse_flow_create(con.node)
        flow[tree_pk] = {...flow[tree_pk], ...child_flow}
    }
    return flow
}

function validate_flow() {
    for (const node_id of Object.keys(node_intent_data)) {
        if (node_id != 1) {
            const node = editor.getNodeFromId(node_id)
            const input_conn = node.inputs?.input_1?.connections 

            if (!input_conn || input_conn.length === 0) {
                return false
            }
        }
    }
    return true
}

function update_node_lazyloaded_status() {
    for (const node_intent_id in node_intent_data){
        node_intent_data[node_intent_id].lazyLoaded = false;
    }
}

function save_flow() {
    if (!validate_flow()) {
        M.toast({
            "html": "Flow is invalid"
        }, 2000)
        return
    }

    let intent_pk = null

    if (window.location.href.indexOf("intent_pk=") != -1) {

        let url_parameters = get_url_vars();
        intent_pk = url_parameters["intent_pk"];
    }

    const flow = recurse_flow_create(1)
    const category_obj_pk = $("#select-intent-category").val()

    let json_string = JSON.stringify({
        flow,
        category_obj_pk,
        intent_pk,
    })
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: '/chat/save-flow/',
        type: "POST",
        headers: {
            'X-CSRFToken': get_csrf_token(),
        },
        data: {
            json_string: json_string
        },
        dataType: "json",
        async: false,
        success: function (response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response['status'] == 200) {
                update_node_lazyloaded_status();
                M.toast({
                    'html': "Flow Saved Successfully!"
                }, 1000);
            } else if (response['status'] == 300) {
                M.toast({
                    'html': response["message"]
                }, 1000);
            } else {
                M.toast({
                    'html': "Unable to save flow"
                }, 2000);
            }
        }
    });
}

function save_intent_category() {

    let intent_pk = null

    if (window.location.href.indexOf("intent_pk=") != -1) {

        let url_parameters = get_url_vars();
        intent_pk = url_parameters["intent_pk"];
    }

    const category_obj_pk = $("#select-intent-category").val()
    const flow = null
    let json_string = JSON.stringify({
        flow,
        category_obj_pk,
        intent_pk,
    })
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: '/chat/save-flow/',
        type: "POST",
        headers: {
            'X-CSRFToken': get_csrf_token(),
        },
        data: {
            json_string: json_string
        },
        dataType: "json",
        async: false,
        success: function (response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response['status'] == 200) {
                M.toast({
                    'html': "Category Saved Successfully!"
                }, 1000);
            } else if (response['status'] == 300) {
                M.toast({
                    'html': response["message"]
                }, 1000);
            } else {
                M.toast({
                    'html': "Unable to save category"
                }, 2000);
            }
        }
    });
}

function language_tablinks_change() {
    if (SELECTED_LANGUAGE === "en") {
        $(".custom-tooltip-intent").show()
    } else {
        $(".custom-tooltip-intent").hide()
        $("#edit_bot_response_icon").show()
    }

    if (is_new_intent === "True" || node_intent_data[selected_node].is_new_tree) {
        $(".bot_response_delete_button").hide()
        $(".custom-tooltip-intent:not(#create_intent_menu_icon,#edit_bot_response_icon)").addClass("disable-video-recoder-save-value")
        $(".edit-intent-details-cancel-btn").addClass("disable-video-recoder-save-value")
    } else {
        $(".bot_response_delete_button").show()
        $(".custom-tooltip-intent:not(#create_intent_menu_icon,#edit_bot_response_icon)").removeClass("disable-video-recoder-save-value")
        $(".edit-intent-details-cancel-btn").removeClass("disable-video-recoder-save-value")
    }
}

function change_intent_language() {
    change_language_triggered = true
    const intent_pk = get_url_vars()["intent_pk"];
    const tree_structure = fetchIntentTreeStructureByIntentID(intent_pk, SELECTED_LANGUAGE)
    if (tree_structure["need_to_show_auto_fix_popup"]) {
        auto_fix_selected_tree_pk = node_intent_data['1'].tree_pk;
        $("#autofix_div").show()
    } else {
        $("#autofix_div").hide()
    }
    editor.clear()
    editor.nodeId = 1
    node_intent_data = {}
    build_initial_flow(tree_structure[1], true, null, window.outerWidth / 6)
    update_flow()
    update_node_vertical_positions(1)
    change_language_triggered = false
    setTimeout(function() {
        $('.easychat-dropdown-select-custom').removeClass('open')
    }, 100)
}

function cancel_bot_response(confirm) {

    if (!confirm) {
        $("#easychat_form_widget_resetall_modal").modal("open")
        $("#easychat_form_widget_resetall_modal .termination-yes-btn").attr("onclick", "cancel_bot_response(true)")
        return
    }

    let current_response_tab = $("#node_response_div > div.active").attr("id")
    const bot_response = node_intent_data[selected_node].intent_response

    // Bot Response - Text
    if (current_response_tab == "intent-bot-response-tab") {
        $("#intent_bot_response_text_text").trumbowyg('html', "")
        $("#intent_bot_response_text_speech").trumbowyg('html', "")
        $("#intent_bot_response_reprompt").trumbowyg('html', "")
        $("#intent_bot_response_ssml").trumbowyg('html', "")

        bot_response.response_list.text_response = ""
        bot_response.response_list.speech_response = ""
        bot_response.response_list.ssml_response = ""
        bot_response.response_list.text_reprompt_response = ""
    }

    // Bot Response - Table
    if (current_response_tab == "intent-tables-tab") {
        $("#delete-table-from-given").click()
        $(".edit-intent-table-input-div input").val("")

        bot_response.table_list_of_list = "{\"items\": []}"
    }

    // Bot Response - Cards
    if (current_response_tab == "intent-cards-tab") {
        $(".card-response-tabs .tab:not(#dummy_card_tab)").remove()
        $(".response-added-cards").remove()

        bot_response.card_list = {}
    }

    // Bot Response - Images
    if (current_response_tab == "intent-images-tab") {
        $("#only_image_carousel .carousel-item:not(#response_image_upload)").remove()
        $("#add_enter_intent_image_url_data").val("")
        initialize_carousel("#only_image_carousel")

        bot_response.image_list = []
    }

    // Bot Response -Videos
    if (current_response_tab == "intent-videos-tab") {
        $("#add_enter_intent_video_url_data").val("")
        $(".video-carousel-slider .carousel-item").remove()
        $(".upload-video-wrapper-div").hide()
        initialize_carousel(".carousel.video-carousel-slider")

        bot_response.video_list = []
    }

}

function cancel_bot_icon(confirm) {
    if (!confirm) {
        $("#easychat_form_widget_resetall_modal").modal("open")
        $("#easychat_form_widget_resetall_modal .termination-yes-btn").attr("onclick", "cancel_bot_icon(true)")
        return
    }

    $(".easychat-active-intent-icon").removeClass("easychat-active-intent-icon")
    $("div[icon_unique_id=1]").first().addClass("easychat-active-intent-icon")
}

function cancel_bot_channel(confirm) {
    if (!confirm) {
        $("#easychat_form_widget_resetall_modal").modal("open")
        $("#easychat_form_widget_resetall_modal .termination-yes-btn").attr("onclick", "cancel_bot_channel(true)")
        return
    }

    $("#enter_intent_short_name").val("")
    $("#whatsapp-short-name-input").val(node_intent_data[selected_node].name)
    $("#whatsapp-description-input").val(node_intent_data[selected_node].name)

    $("#short_name_field-char-count").text(0)
    $("#whatsapp_short_name_field-char-count").text(node_intent_data[selected_node].name.length)
    $("#whatsapp_description_field-char-count").text(node_intent_data[selected_node].name.length)

    $("#intent_select_all_chanells_cb").prop("checked", false).click()
    let intent_channels = document.getElementsByClassName("edit-intent-channel-btn");
    for (i = 0; i < intent_channels.length; i++) {
        intent_channels[i].checked = true;
    }
}

function cancel_bot_settings(confirm, remove=true) {
    if (!confirm) {
        $("#easychat_form_widget_resetall_modal").modal("open")
        $("#easychat_form_widget_resetall_modal .termination-yes-btn").attr("onclick", "cancel_bot_settings(true)")
        return
    }

    let current_active_tab = $(".intent-settings-overflow-div-content div.active").attr("id")

    if (current_active_tab == "edit_intent_settings_content") {
        document.querySelectorAll("#edit_intent_settings_content input[type=checkbox]").forEach(function(elm) {
            elm.checked = false
            elm.disabled = false
        })
    
        $("#checkbox_faq_intent").prop("disabled", true)
        $("#checkbox-small-talk-enabled").prop("disabled", true)
        $("#checkbox-intent-part-of-suggestionList").prop("checked", true)
        $("#checkbox-intent-feedback").prop("checked", true)
        $("#checkbox-intent-child-tree-options-visible").prop("checked", true)
        $("#catalogue_section_dropdown_div").hide()
        $("#select_section_options_container input").prop("checked", false).change()
        $("#disposition_code").val("")
    
        if (remove) {
            $("#select-user-validator").val("").trigger("change")
            $("#select-user-authentication").val("").trigger("change")
            $('#multiple-select-child-choices').val([]).trigger("change")
        } else {
            $("#select-user-validator option[value!='']").remove()
            $("#select-user-authentication option[value!='']").remove()
            $("#multiple-select-child-choices option[value!='']").remove()
        }

        // Data removal
        if (!remove) {
            return
        }
        
        for (const key of Object.keys(node_intent_data[selected_node].other_settings)) {
            if (node_intent_data[selected_node].other_settings[key] === true) {
                node_intent_data[selected_node].other_settings[key] = false
            }
        }

        node_intent_data[selected_node].other_settings["is_part_of_suggestion_list"] = true
        node_intent_data[selected_node].other_settings["is_feedback_required"] = true
        node_intent_data[selected_node].other_settings["is_child_tree_visible"] = true
        if (node_intent_data[selected_node].other_settings.authentication_objs.length > 0) {
            node_intent_data[selected_node].other_settings["selected_user_authentication"] = node_intent_data[selected_node].other_settings.authentication_objs[0]
        }
        node_intent_data[selected_node].other_settings["selected_validator_obj"] = {processor__pk: ""}
        node_intent_data[selected_node].other_settings["child_choices_list"] = []
        node_intent_data[selected_node].other_settings["disposition_code"] = ""
        node_intent_data[selected_node].intent_response.modes.is_catalogue_added = "false"

    } else {
        document.querySelectorAll("#edit_intent_advance_settings_content input[type=checkbox]").forEach(function(elm) {
            elm.checked = false
        })

        $('#select-intent-processor').val("").trigger("change")
        $("#post_processor_variable").val("")
        $("#flow_analytics_variable").val("")
        $("#category_analytics_variable_div").hide()
        $("#flow_analytics_variable_div").hide()

        // Data removal
        if (!remove) {
            return
        }

        node_intent_data[selected_node].other_settings["flow_analytics_variable"] = ""
        node_intent_data[selected_node].other_settings["post_processor_variable"] = ""
        node_intent_data[selected_node].other_settings.is_category_response_allowed = false
    }
    
}

function cancel_bot_recommendation(confirm, remove=true) {
    if (!confirm) {
        $("#easychat_form_widget_resetall_modal").modal("open")
        $("#easychat_form_widget_resetall_modal .termination-yes-btn").attr("onclick", "cancel_bot_recommendation(true)")
        return
    }

    if (remove) {
        $('#multiple-select-intent-choice-list').val("").trigger("change")
    } else {
        $("#multiple-select-intent-choice-list").val("")
        $('#multiple-select-intent-choice-list').select2().on('select2:open', function(e) {
            $('#child-intent-selection .select2-search__field').attr('placeholder', 'Search');
        });
    }
    
    $('#checkbox-intent-recommendation-menu').prop("checked", false)

    // Data delete
    if (!remove) {
        return
    }
    node_intent_data[selected_node].recommeded_intents_dict_list = []
    node_intent_data[selected_node].intent_response.modes.is_recommendation_menu = "false"
}

function cancel_bot_order_response(confirm) {
    if (!confirm) {
        $("#easychat_form_widget_resetall_modal").modal("open")
        $("#easychat_form_widget_resetall_modal .termination-yes-btn").attr("onclick", "cancel_bot_order_response(true)")
        return
    }

    $('#default-order').prop("checked", true).trigger("change")

    // Data delete
    node_intent_data[selected_node].is_custom_order_selected = false
}

function cancel_bot_coversion_flow(confirm) {
    if (!confirm) {
        $("#easychat_form_widget_resetall_modal").modal("open")
        $("#easychat_form_widget_resetall_modal .termination-yes-btn").attr("onclick", "cancel_bot_coversion_flow(true)")
        return
    }

    $('#explanation').val("")

    // Data delete
    node_intent_data[selected_node].explanation = ""
}

function cancel_bot_advanced_nlp(confirm) {
    if (!confirm) {
        $("#easychat_form_widget_resetall_modal").modal("open")
        $("#easychat_form_widget_resetall_modal .termination-yes-btn").attr("onclick", "cancel_bot_advanced_nlp(true)")
        return
    }

    $('#easychat_necessary_keywords').text("")
    $('#easychat_restricted_keywords').text("")
    $("#easychat-intent-threshold").data("ionRangeSlider").update({from: "1.0"})

    // Data delete
    node_intent_data[selected_node].necessary_keywords = ""
    node_intent_data[selected_node].restricted_keywords = ""
    node_intent_data[selected_node].intent_threshold = "1.0"
}

function cancel_all_widget(api_integration=true) {
    $("#response_widget_tab_wrapper a").removeClass("active")
    $(".intent-widget-overflow-div-content > div:not(:first-child)").removeClass("active")
    $(".intent-widget-overflow-div-content > div:not(:first-child)").css("display", "none")
    document.getElementById("enabledatepicker_switch1").checked = false
    document.getElementById("enabletimepicker_switch2").checked = false

    document.getElementById('single-date-picker-radio').checked = false
    document.getElementById('single-date-picker-radio').disabled = true
    document.getElementById('custom-date-picker-radio').checked = false
    document.getElementById('custom-date-picker-radio').disabled = true

    document.getElementById('single-time-picker-radio').checked = false
    document.getElementById('single-time-picker-radio').disabled = true
    document.getElementById('custom-time-picker-radio').checked = false
    document.getElementById('custom-time-picker-radio').disabled = true

    document.getElementById("sortable-radio-widget-edit-div").innerHTML = ""
    document.getElementById("sortable-checkbox-widget-edit-div").innerHTML = ""
    document.getElementById("sortable-dropdown-widget-edit-div").innerHTML = ""

    document.getElementById("checkbox-intent-video-recorder").checked = false;
    document.getElementById("checkbox-intent-save-video-attachment").checked = false;
    $("#easychat-save-video-attachment-server").addClass("disable-video-recoder-save-value")

    $("input[name=range-slider-type]").prop("checked", false)
    $("#range-slider-min-max-value-input-div").hide()
    $("#range-slider-min-range").val("")
    $("#range-slider-max-range").val("")

    document.getElementById("checkbox-intent-attachment").checked = false;
    document.getElementById("checkbox-intent-save-attachment").checked = false;
    $("#easychat-save-file-attachment-server").hide()
    $('#choosen_file_type').val("")

    document.getElementById("checkbox-intent-country-code-cb").checked = false;
    $("#modal-country-code-wrapper").addClass("disable-video-recoder-save-value")
    $("#phone").intlTelInput("setCountry", country_code);

    $('#create-form-fields').html('')
    $('#create-form-fields').hide()
    $("#form_name").val('')
    $('#form_name').val('')
    api_integration && reset_api_integration('', true)
}

function cancel_bot_widget_updated(confirm) {
    if (!confirm) {
        $("#easychat_form_widget_resetall_modal").modal("open")
        $("#easychat_form_widget_resetall_modal .termination-yes-btn").attr("onclick", "cancel_bot_widget_updated(true)")
        return
    }

    let widget_data_req = node_intent_data[selected_node].intent_response.modes
    let widget_data_field = node_intent_data[selected_node].intent_response.modes_param

    let id = $(".intent-widget-overflow-div-content div.active").attr("id")

    $("#response_widget_tab_wrapper a").removeClass("active")
    $(".intent-widget-overflow-div-content > div:not(:first-child)").removeClass("active")
    $(".intent-widget-overflow-div-content > div:not(:first-child)").css("display", "none")
    $("#response_widget .edit-intent-details-action-btns-wrapper .edit-intent-details-cancel-btn").addClass("disable-video-recoder-save-value")

    if (id == 'calendar_picker_widget_content') {

        document.getElementById("enabledatepicker_switch1").checked = false
        document.getElementById("enabletimepicker_switch2").checked = false

        document.getElementById('single-date-picker-radio').checked = false
        document.getElementById('single-date-picker-radio').disabled = true
        document.getElementById('custom-date-picker-radio').checked = false
        document.getElementById('custom-date-picker-radio').disabled = true

        document.getElementById('single-time-picker-radio').checked = false
        document.getElementById('single-time-picker-radio').disabled = true
        document.getElementById('custom-time-picker-radio').checked = false
        document.getElementById('custom-time-picker-radio').disabled = true

        widget_data_req.is_datepicker = "false"
        widget_data_req.is_timepicker = "false"
        widget_data_req.is_single_datepicker = "false"
        widget_data_req.is_multi_datepicker = "false"
        widget_data_req.is_single_timepicker = "false"
        widget_data_req.is_multi_timepicker = "false"

    } else if (id == 'radio_widget_content') {
        document.getElementById("sortable-radio-widget-edit-div").innerHTML = ""
        widget_data_field.radio_button_choices = {}
    } else if (id == 'checkbox_widget_content') {
        document.getElementById("sortable-checkbox-widget-edit-div").innerHTML = ""
        widget_data_field.check_box_choices = {}
    } else if (id == 'dropdown_widget_content') {
        document.getElementById("sortable-dropdown-widget-edit-div").innerHTML = ""
        widget_data_field.drop_down_choices = {}
    } else if (id == 'video_widget_content') {
        document.getElementById("checkbox-intent-video-recorder").checked = false;
        document.getElementById("checkbox-intent-save-video-attachment").checked = false;
        $("#easychat-save-video-attachment-server").addClass("disable-video-recoder-save-value")
        widget_data_req.is_video_recorder_allowed = "false"
        widget_data_req.is_save_video_attachment = "false"
    } else if (id == 'range_slider_widget_content') {
        $("input[name=range-slider-type]").prop("checked", false)
        $("#range-slider-min-max-value-input-div").hide()
        $("#range-slider-min-range").val("")
        $("#range-slider-max-range").val("")

        widget_data_req.is_range_slider = "false"
        widget_data_field.range_slider_list[0].range_type = undefined
        widget_data_field.range_slider_list[0].min = ""
        widget_data_field.range_slider_list[0].max = ""
    } else if (id == 'file_attach_widget_content') {
        document.getElementById("checkbox-intent-attachment").checked = false;
        document.getElementById("checkbox-intent-save-attachment").checked = false;
        $("#easychat-save-file-attachment-server").hide()
        $('#choosen_file_type').val("").trigger("change")

        widget_data_req.is_attachment_required = "false"
        widget_data_req.is_save_attachment_required = "false"
        widget_data_field.choosen_file_type = ""

    } else if (id == 'phone_number_widget_content') {
        document.getElementById("checkbox-intent-country-code-cb").checked = false;
        $("#modal-country-code-wrapper").addClass("disable-video-recoder-save-value")
        $("#phone").intlTelInput("setCountry", country_code);

        widget_data_req.is_phone_widget_enabled = "false"
        widget_data_field.country_code = country_code
    }  
    else if (id == 'create_form_widget_content') {
        $('#create-form-fields').html('')
        $('#create-form-fields').hide()
        $("#form_name").val('')
        $('#form_name').val('')
        reset_api_integration('', true)
    }

}

function build_form_widget_preview() {

    let form_name = $('#form_name').val();
    let form_html = ""

    if (form_name == "") {
        return ["", []];
    }


    const data = get_built_form_info(true);

    if (!data) return ["", []];

    form_html += `
    <div class="preview-user-message-wrapper">
        <div class="form-widget-response-bot-preview-wrapper">
        <div style="width:100%; padding: 0px 12px;">
    `

    const form = data.form;
    const form_function_arr = []

    state.form = { ...form };

    const field_ids = form.field_order;

    let form_name_div = `<div class="preview-form-name-div">${form_name}</div>`;
    form_html += form_name_div

    field_ids.forEach(field_id => {
        const field = form[field_id];
        let current_id = field_id.split('-')[1]
        const html = get_field_html_based_input_type(field, current_id);

        form_html += html

        form_function_arr.push(initialize_phone_number_selector_console.bind({}, "telephone-preview-" + current_id, field.country_code, current_id))
        
    })

    form_html += "</div></div></div></div></div></div>"

    return [form_html, form_function_arr]
}

function show_whatsapp_preview() {
    bot_response_preview()
    bot_preview_section_show()
}

function delete_intent() {
    let intent_pk = get_url_vars()["intent_pk"]
    let bot_pk = SELECTED_BOT_PK
    json_string = JSON.stringify({
        intent_pk_list: [intent_pk],
        bot_pk: bot_pk,
    });
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: '/chat/delete-intent/',
        type: "POST",
        headers: {
            'X-CSRFToken': get_csrf_token(),
        },
        data: {
            json_string: json_string
        },
        success: function (data) {
            data = custom_decrypt(data)
            data = JSON.parse(data);
            if (data['status'] == 200) {
                if (intents_deleted_count > 1) {
                    M.toast({
                        'html': "Intents deleted successfully!"
                    }, 2000);
                } else {
                    M.toast({
                        'html': "Intent deleted successfully!"
                    }, 2000);
                }

                if (bot_pk != undefined) {
                    setTimeout(function () {
                        let location = '/chat/intent/?bot_pk=' + bot_pk + "&selected_language=en";
                        window.location = location;
                    }, 2000);
                } else {
                    setTimeout(function () {
                        window.location = window.location.href;
                    }, 2000);
                }
            } else {
                M.toast({
                    'html': "Unable to delete the Intent!"
                }, 2000);
            }
        }
    });
}

// Add Catalogue section JS

$(document).ready(function() {

    $("#select-sections-container").sortable({
        containment: "parent",
        appendTo: 'body',
        containment: 'window',
        scroll: false,
        helper: 'clone'
    });
    
    $("#select_section_input_div").click(function (event) {
        if(event.target.id != "select_section_input_div") return;
        $("#select_section_search_bar").keyup();
        if ($('#select_section_options_container').css('display') == 'none') {
            $("#select_section_options_container").show();
            $("#select_section_dropdown_icon").addClass("select-dropdown-active")
        }
        else if ($('#select_section_options_container').css('display') == 'block') {
            $("#select_section_options_container").scrollTop(0);
            $("#select_section_options_container").hide();
            $("#select_section_dropdown_icon").removeClass("select-dropdown-active")
        }
    });
    
    $(document).on('click', function(event) {
        if ($(event.target).closest('#select_section_input_div, #select_section_options_container').length === 0) {
            $("#select_section_options_container").scrollTop(0);
            $("#select_section_options_container").hide();
            $("#select_section_dropdown_icon").removeClass("select-dropdown-active");
        }
        event.stopPropagation();
    });
})

function add_section_product_search() {
    let input, filter, search_value, i, text_value;
    input = document.getElementById("select_section_search_bar");
    filter = input.value.toUpperCase();
    search_value = document.querySelectorAll('.select-section-item-select .select-section-item-text');
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
        document.getElementById('select_section_no_data_found').style.display = "flex";
    } else {
        document.getElementById('select_section_no_data_found').style.display = "none";
    }
};

function get_selected_section_chip_html(section_id, section_title) {
    section_id = section_id.split("_")
    section_id = section_id[section_id.length - 1]
    let chip_html = `<span id="chip_${section_id}" class="ui-sortable-handle"><b><svg style="margin-top: 3px;"
                        width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path
                            d="M8 8.5C8.55228 8.5 9 8.94772 9 9.5C9 10.0523 8.55228 10.5 8 10.5C7.44772 10.5 7 10.0523 7 9.5C7 8.94772 7.44772 8.5 8 8.5ZM4 8.5C4.55228 8.5 5 8.94772 5 9.5C5 10.0523 4.55228 10.5 4 10.5C3.44772 10.5 3 10.0523 3 9.5C3 8.94772 3.44772 8.5 4 8.5ZM8 5C8.55228 5 9 5.44772 9 6C9 6.55228 8.55228 7 8 7C7.44772 7 7 6.55228 7 6C7 5.44772 7.44772 5 8 5ZM4 5C4.55228 5 5 5.44772 5 6C5 6.55228 4.55228 7 4 7C3.44772 7 3 6.55228 3 6C3 5.44772 3.44772 5 4 5ZM8 1.5C8.55228 1.5 9 1.94772 9 2.5C9 3.05228 8.55228 3.5 8 3.5C7.44772 3.5 7 3.05228 7 2.5C7 1.94772 7.44772 1.5 8 1.5ZM4 1.5C4.55228 1.5 5 1.94772 5 2.5C5 3.05228 4.55228 3.5 4 3.5C3.44772 3.5 3 3.05228 3 2.5C3 1.94772 3.44772 1.5 4 1.5Z"
                            fill="white"></path>
                    </svg></b>${section_title}<a class="remove-chip-btn" onclick="remove_section_chip('${section_id}')"> <svg
                        width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M2.3938 2.25L9.60619 9.75" stroke="white" stroke-width="1.30211" stroke-linecap="round"
                            stroke-linejoin="round"></path>
                        <path d="M9.6062 2.25L2.39381 9.75" stroke="white" stroke-width="1.30211" stroke-linecap="round"
                            stroke-linejoin="round"></path>
                    </svg></a>
                    </span>`
    return chip_html
}

function add_event_listeners_for_sections_chips() {
    $('#select-sections-container span').hover(function () {
        $(this).css({
            "background-color": "#0254d7",
            "color": "#fff",
            "padding": "4px 12px",
            "width": "max-content",
            "font-size": "12px!important",
            "border-radius": "4px"
        })
    });
    
    $('#select-sections-container span').mouseleave(function () {
        $(this).css({
            "background-color": "#0254d7",
            "color": "#fff",
            "padding": "4px 12px",
            "width": "max-content",
            "font-size": "12px!important",
            "border-radius": "4px"
        })
    });
}

function remove_section_chip(section_id) {
    $("#select_section_options_container input[section-id='" + section_id + "']").prop("checked", false).change();
}

function handle_toast_close() {

    $('#easychat_language_config_success_toast_container_category').hide();

}

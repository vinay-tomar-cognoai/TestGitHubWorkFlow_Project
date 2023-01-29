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
            placeholder: "ui-state-highlight"
        });
    });
$(document).ready(function(){

    $('#add-banner-modal').removeAttr('tabIndex');
    handle_hindi_phoentic_typing_display_message();

})

function handle_hindi_phoentic_typing_display_message(){
    for(let i=0; i<LIST_OF_PHONETIC_TYPING_SUPPORTED_LANGUAGES.length;i++){

        lang = LIST_OF_PHONETIC_TYPING_SUPPORTED_LANGUAGES[i]
        if(!document.getElementById(lang)){
            if(document.getElementById("language-disclaimer-text-row")){
                document.getElementById("language-disclaimer-text-row").style.display = "none";
            }
        }else{
            if(!document.getElementById(lang).checked){
                document.getElementById("language-disclaimer-text-row").style.display = "none";
            }
            if(document.getElementById(lang).checked){
                if (document.getElementById("is_web_bot_phonetic_typing_enabled").checked)
                {
                    document.getElementById("language-disclaimer-text-row").style.display = "grid";
                }
                break
            }
        }
    }
}

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
        "channel_name": "Web",
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
                return;
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

function create_initial_questions_new_tag_list(initial_message_list) {

    var new_tag_list = []
    for(var idx in initial_message_list) {

        if(!document.getElementById("new-tag-"+initial_message_list[idx]).disabled &&   
                $( "#new-tag-"+initial_message_list[idx] ).hasClass( "active-button" )) {
            
            new_tag_list.push(true)
        } else {
            new_tag_list.push(false)
        }
    }

    return new_tag_list
}

function change_initial_questions_preview_color() {
    $('.preview-container > span').css('background', '#'+$("#bot_theme_color").val())
}

$(document).on("click", "#save-web-channel", function(e) {

    var location_href = window.location.href;
    var location_href = location_href.replace("#", "");
    var location_href = location_href.replace("!", "");
    var bot_id = (get_url_vars()["id"])
    var selected_language = get_url_vars()['selected_lang']
    var welcome_message = $("#welcome-message").trumbowyg('html')
    var failure_message = $("#failure-message").trumbowyg('html')
    var authentication_message = $("#authentication-message").trumbowyg('html')

    var is_language_auto_detection_enabled = document.getElementById("is_language_auto_detection_enabled").checked
    var is_textfield_input_enabled = document.getElementById("is-input-textfield").checked
    
    var validation_message = check_channel_messages_validation(welcome_message, failure_message, authentication_message);
    if (validation_message != "No Error") {
        M.toast({
            "html": validation_message
        }, 2000);
        return;
    }

    var is_auto_popup_enabled_desktop = document.getElementById("is-bot-auto-popup-allowed-desktop").checked;
    var is_auto_popup_enabled_mobile = document.getElementById("is-bot-auto-popup-allowed-mobile").checked;
    var auto_popup_timer = document.getElementById("bot_auto_popup_timer").value;
    var auto_popup_type = document.getElementById("bot-popup-options-values").value;
    var auto_popup_text = document.getElementById("bot_auto_popup_text").value;
    var auto_popup_initial_message_list = $("#bot-popup-multiple-select-message-list").val();
    var is_auto_popup_inactivity_enabled = document.getElementById("bot-popup-inactivity-cb").checked;
    var enable_custom_intent_bubbles = false;

    var custom_intents_for = "";
    if(document.getElementById("auto_popup_enable_custom_intents").checked && document.getElementById("enable_form_assist").checked==false){
        enable_custom_intent_bubbles = true;
        custom_intents_for = "auto_popup";
    }
    else if (document.getElementById("form_assist_enable_custom_intents").checked){
        enable_custom_intent_bubbles = true;
        custom_intents_for = "form_assist";
    }

    if (is_auto_popup_enabled_desktop == true || is_auto_popup_enabled_mobile == true) {
        if (auto_popup_timer.trim() == "") {
            M.toast({
                "html": "Auto popup timer cannot be empty."
            }, 2000);
            return;
        }
        if (auto_popup_type.trim() == "0") {
            M.toast({
                "html": "Auto popup type cannot be empty."
            }, 2000);
            return;
        }

        if (auto_popup_type == 2) {

            if (auto_popup_text.trim() == "") {
                M.toast({
                    "html": "Auto popup text cannot be empty."
                }, 2000);
                return;
            } 

        } else if (auto_popup_type == 3) {
            if (auto_popup_initial_message_list.length == 0) {
                M.toast({
                    "html": "Auto popup initial messages cannot be empty."
                }, 2000);
                return;
            }

            if (auto_popup_text.trim() == "") {
                M.toast({
                    "html": "Auto popup text cannot be empty."
                }, 2000);
                return;
            }
        }

    }

    if (auto_popup_timer == '' || auto_popup_timer == null)
        auto_popup_timer = 5;

    //Form Assist popup details
    var is_form_assist_enabled = document.getElementById("enable_form_assist").checked;

    var is_voice_based_form_assist_enabled = document.getElementById("enable_voice_form_assist").checked;

    var enable_response_form_assist = document.getElementById('enable_response_form_assist').checked;

    var form_assist_auto_popup_type = "1"
    if(document.getElementById("form_assist_intent_bubble_cb").checked) {
        form_assist_auto_popup_type = "2"
    }

    var form_assist_autopop_up_timer = document.getElementById("form_assist_autopop_up_timer").value;

    var form_assist_autopop_up_inactivity_timer = document.getElementById("form_assist_autopop_up_inactivity_timer").value;

    var form_assist_intent_bubble_timer = document.getElementById("form_assist_intent_bubble_timer").value;

    var form_assist_intent_bubble_inactivity_timer = document.getElementById("form_assist_intent_bubble_inactivity_timer").value;

    var form_assist_intent_bubble_type = document.getElementById("form-assist-bot-popup-options-values").value;

    var form_assist_auto_pop_text = document.getElementById("form_assist_auto_pop_text").value;

    var form_assist_intents = $("#form-assist-bot-popup-multiple-select-message-list").val();

    if(parseInt(form_assist_autopop_up_timer) < 0 || parseInt(form_assist_autopop_up_timer) > 300) {
        form_assist_autopop_up_timer = 10;
    }

    if(parseInt(form_assist_autopop_up_inactivity_timer) < 0 || parseInt(form_assist_autopop_up_inactivity_timer) > 300) {
        form_assist_autopop_up_inactivity_timer = 5;
    }

    if(parseInt(form_assist_intent_bubble_timer) < 0 || parseInt(form_assist_intent_bubble_timer) > 300) {
        form_assist_intent_bubble_timer = 10;
    }

    if(parseInt(form_assist_intent_bubble_inactivity_timer) < 0 || parseInt(form_assist_intent_bubble_inactivity_timer) > 300) {
        form_assist_intent_bubble_inactivity_timer = 5;
    }

    if(is_form_assist_enabled == true) {

        if(form_assist_auto_pop_text.trim() == "" && form_assist_auto_popup_type == "2") {
            M.toast({
                "html": "Auto popup text cannot be empty."
            }, 2000);
            return;            
        }

        if(form_assist_intent_bubble_type == "2" && form_assist_intents.length == 0 && form_assist_auto_popup_type == "2") {
            M.toast({
                "html": "Please select intent for form assist intent bubble"
            }, 2000);
            return;            
        }

    }

    var bot_position = document.getElementById("select-bot-position").value;

    initial_message_list = []
    var selected_initial_questions = document.getElementsByClassName("initial-questions-selected-intents");

    Array.prototype.forEach.call(selected_initial_questions, function(el) {
            initial_message_list.push(el.innerHTML)

    });
    initial_questions_new_tag_list = create_initial_questions_new_tag_list(initial_message_list)

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

    var is_enable_gradient = document.getElementById("enable-gradient").checked;

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

    var is_minimization_enabled = false;
    if (document.getElementById("is-minimization-enabled").checked) {
        is_minimization_enabled = true;
    }
    let disable_auto_popup_minimized = false;
    if(document.getElementById('disable_auto_popup_minimized_cb').checked){
        disable_auto_popup_minimized = true;
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
    var elements = document.querySelectorAll('.hamburger-menu-item > input');
    var counter = 0;
    for (element of elements) {
        counter++;
        let intent = element.value;
        intent = intent.split('_');
        intent[0] = "" + counter
        if (intent[2] != "Icon" && intent[3] != "Menu Title" && intent[intent.length - 1] != "deleted")
            hamburger_list_menu.push(intent);

    }


    var quick_list_menu = []
    var elements = document.querySelectorAll('.quick-menu-item > input');
    var counter = 0;
    for (element of elements) {
        counter++;
        let intent = element.value;
        intent = intent.split(',');
        intent[0] = "" + counter

        if (intent[2] != "Icon" && intent[3] != "Menu Title" && intent[intent.length - 1] != "deleted")
            quick_list_menu.push(intent);
    }

    var is_bot_notification_sound_enabled = false;
    var elem = document.getElementById("is_bot_notification_sound_enabled");
    if (elem != null) {
        if (elem.checked) {
            is_bot_notification_sound_enabled = true;
        }

        // json_string.is_bot_notification_sound_enabled = is_bot_notification_sound_enabled
    }
    is_web_bot_phonetic_typing_enabled = false
    for(let i =0 ; i< LIST_OF_PHONETIC_TYPING_SUPPORTED_LANGUAGES.length;i++){
        language_code = LIST_OF_PHONETIC_TYPING_SUPPORTED_LANGUAGES[i].split("-")[1]
        if(selected_supported_languages.includes(language_code)){
            is_web_bot_phonetic_typing_enabled = document.getElementById("is_web_bot_phonetic_typing_enabled").checked
            break
        }

    }
    disclaimer_message = ""
    if(is_web_bot_phonetic_typing_enabled){
        var disclaimer_message = $("#language-disclaimer-text").trumbowyg('html')
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
            return ;
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
        initial_questions_new_tag_list: initial_questions_new_tag_list,
        image_url: image_url,
        compressed_image_url: compressed_image_url,
        video_url: video_url,
        theme_selected: theme_selected,
        failure_recommendation_list: failure_recommendation_list,
        carousel_img_url_list: carousel_img_url_list,
        redirect_url_list: redirect_url_list,
        compressed_img_url_list: compressed_img_url_list,
        bot_position: bot_position,
        bot_theme_color: bot_theme_color,
        is_enable_gradient: is_enable_gradient,
        is_minimization_enabled: is_minimization_enabled,
        sticky_intent_list: sticky_intent_list,
        is_automatic_carousel_enabled: is_automatic_carousel_enabled,
        carousel_time: carousel_time,
        sticky_intent_list_menu: sticky_intent_list_menu,
        sticky_button_format: sticky_button_format,
        hamburger_items: hamburger_list_menu,
        quick_items: quick_list_menu,
        is_auto_popup_enabled_desktop: is_auto_popup_enabled_desktop,
        is_auto_popup_enabled_mobile: is_auto_popup_enabled_mobile,
        auto_popup_timer: auto_popup_timer,
        auto_popup_type: auto_popup_type,
        auto_popup_text: auto_popup_text,
        auto_popup_initial_message_list: auto_popup_initial_message_list,
        is_auto_popup_inactivity_enabled: is_auto_popup_inactivity_enabled,
        selected_supported_languages: selected_supported_languages,
        selected_language: selected_language,
        is_bot_notification_sound_enabled: is_bot_notification_sound_enabled,
        is_web_bot_phonetic_typing_enabled: is_web_bot_phonetic_typing_enabled,
        disclaimer_message: disclaimer_message,
        is_form_assist_enabled: is_form_assist_enabled,
        is_voice_based_form_assist_enabled: is_voice_based_form_assist_enabled,
        enable_response_form_assist: enable_response_form_assist,
        form_assist_auto_popup_type: form_assist_auto_popup_type,
        form_assist_autopop_up_timer: form_assist_autopop_up_timer,
        form_assist_autopop_up_inactivity_timer: form_assist_autopop_up_inactivity_timer,
        form_assist_intent_bubble_timer: form_assist_intent_bubble_timer,
        form_assist_intent_bubble_inactivity_timer: form_assist_intent_bubble_inactivity_timer,
        form_assist_intent_bubble_type: form_assist_intent_bubble_type,
        form_assist_auto_pop_text: form_assist_auto_pop_text,
        form_assist_intents: form_assist_intents,
        welcome_banner_list: welcome_banner_list,
        is_language_auto_detection_enabled: is_language_auto_detection_enabled,
        is_enabled_intent_icon: is_enabled_intent_icon,
        disable_auto_popup_minimized: disable_auto_popup_minimized,
        enable_custom_intent_bubbles: enable_custom_intent_bubbles,
        custom_intents_for:custom_intents_for,
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
    document.getElementById("easychat_web_channel_preloader").style.display = "block";
    $.ajax({
        url: "/chat/channels/web/save/",
        type: "POST",
        data: {
            json_string: json_string
        },
        headers: {
            "X-CSRFToken": get_csrf_token()
        },
        success: function(response) {
            document.getElementById("easychat_web_channel_preloader").style.display = "none";
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
            document.getElementById("easychat_web_channel_preloader").style.display = "none";
            console.log("Report this error: ", error);
        },
    });
});


function delete_bot_image(bot_id) {

    if (bot_id == undefined) {
        M.toast({
            "html": "Please enter valid bot id"
        }, 2000)
    }

    json_string = JSON.stringify({
        "bot_id": bot_id
    })
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: "/chat/bot/delete-bot-image/",
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
                M.toast({
                    "html": response["message"]
                }, 2000)
                redirection_url = "/chat/channels/web/?id=" + bot_id
                window.location = redirection_url;
            }},
        async: false,
        error: function (xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        }
    });

}


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

// auto popup custom intents

function save_delete_custom_intents_validation(){

    let is_auto_popup_enabled_desktop = document.getElementById("is-bot-auto-popup-allowed-desktop").checked;
    let is_auto_popup_enabled_mobile = document.getElementById("is-bot-auto-popup-allowed-mobile").checked;
    let auto_popup_type = document.getElementById("bot-popup-options-values").value;
    let auto_popup_text = document.getElementById("bot_auto_popup_text").value;
    let auto_popup_initial_message_list = $("#bot-popup-multiple-select-message-list").val();

    if (is_auto_popup_enabled_desktop == true || is_auto_popup_enabled_mobile == true) {
       if (auto_popup_type == 3) {
            if (auto_popup_initial_message_list.length == 0) {
                M.toast({
                    "html": "Auto popup initial messages cannot be empty."
                }, 2000);
                return false;
            }

            if (auto_popup_text.trim() == "") {
                M.toast({
                    "html": "Auto popup text cannot be empty."
                }, 2000);
                return false;
            }
        }

    }

    let is_form_assist_enabled = document.getElementById("enable_form_assist").checked;
    let form_assist_auto_popup_type = "1"
    if(document.getElementById("form_assist_intent_bubble_cb").checked) {
        form_assist_auto_popup_type = "2"
    }
    let form_assist_intent_bubble_type = document.getElementById("form-assist-bot-popup-options-values").value;
    let form_assist_auto_pop_text = document.getElementById("form_assist_auto_pop_text").value;
    let form_assist_intents = $("#form-assist-bot-popup-multiple-select-message-list").val();

    if(is_form_assist_enabled == true) {

        if(form_assist_auto_pop_text.trim() == "" && form_assist_auto_popup_type == "2") {
            M.toast({
                "html": "Auto popup text cannot be empty."
            }, 2000);
            return false;            
        }

        if(form_assist_intent_bubble_type == "2" && form_assist_intents.length == 0 && form_assist_auto_popup_type == "2") {
            M.toast({
                "html": "Please select intent for form assist intent bubble"
            }, 2000);
            return false;            
        }

    }
    return true;

}

function add_custom_intents(custom_intent_is_for){

    var bot_id = get_url_vars()['id']
    let selected_language = get_url_vars()['selected_lang']
    if (selected_language == undefined || selected_language == null) {
        selected_language = "en"
    }

    custom_intent_url = document.getElementById("add_custom_url_"+custom_intent_is_for.toString()).value.trim();
    if (isValidURL(custom_intent_url) == false) {
        M.toast({
            "html": "Please enter valid url"
        }, 2000);
        return;
    }

    var custom_intent_list = $("#"+custom_intent_is_for.toString()+"_webpage_add_intents_dropdown").val();
    if (custom_intent_url != "" && custom_intent_list == "") {
        M.toast({
            "html": "Please select an intent."
        }, 2000);
        return;
    }

    if(save_delete_custom_intents_validation() == false){
        return
    }

    document.getElementById("add_custom_url_"+custom_intent_is_for.toString()).value = "";

    json_string = JSON.stringify({
        bot_id: bot_id,
        custom_intent_url: custom_intent_url,
        custom_intent_list: custom_intent_list,
        selected_language: selected_language,
        custom_intents_for: custom_intent_is_for.toString(),
    });
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: "/chat/channels/save-custom-intents/",
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
                M.toast({
                    "html": "Custom Intent added. Please update js file again."
                })
                document.getElementById("save-web-channel").click();
            } else if (response["status"] == 301) {
                M.toast({
                    "html": "This url already exists"
                })
            } else if (response["status"] == 401) {
                M.toast({
                    "html": response['status_message']
                })
            } else if (response["status"] == 208) {
                M.toast({
                    "html": response['status_message']
                })
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

}


function edit_custom_intents(custom_intent_is_for,custom_intents_pk){

    var bot_id = get_url_vars()['id']
    let selected_language = get_url_vars()['selected_lang']
    if (selected_language == undefined || selected_language == null) {
        selected_language = "en"
    }

    if (custom_intent_list == "") {
        M.toast({
            "html": "Please select an intent."
        }, 2000);
        return;
    }

    var custom_intent_list = $("#"+custom_intent_is_for.toString()+"_webpage_edit_intents_dropdown-"+custom_intents_pk.toString()).val();

    json_string = JSON.stringify({
        bot_id: bot_id,
        custom_intent_list: custom_intent_list,
        selected_language: selected_language,
        custom_intents_pk: custom_intents_pk,
    });
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: "/chat/channels/edit-custom-intents/",
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
                M.toast({
                    "html": "Changes edited. Please update js file again."
                })
                var edit_btn = document.getElementById("edit-custom-intent-"+response["custom_intents_pk"].toString());
                var intent_list = response["custom_intent_list"];
                intent_list = intent_list.split(",")
                edit_btn.setAttribute("href", "#edit-intents-modal-" + response["custom_intents_pk"].toString());
                var td_elements = document.getElementById("custom-intents-data-" + response["custom_intents_pk"]).getElementsByTagName("td");
                td_elements[1].innerHTML = ""
                for(let i=0; i < intent_list.length;i++){
                    td_elements[1].innerHTML += "<span>" + intent_list[i] + "</span>" ;
                }

                $('#edit-intents-modal-'+response["custom_intents_pk"]).modal('close');

            } else if (response["status"] == 301) {
                M.toast({
                    "html": "This Custom intent does not exist"
                })
            } else if (response["status"] == 401) {
                M.toast({
                    "html": response['status_message']
                })
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

}

function delete_custom_intents(custom_intents_pk){

    var bot_id = get_url_vars()['id']
    if(save_delete_custom_intents_validation() == false){
        return
    }

    json_string = JSON.stringify({
        bot_id: bot_id,
        custom_intents_pk: custom_intents_pk,
    });
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: "/chat/channels/delete-custom-intents/",
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
                M.toast({
                    "html": "Custom Intent Deleted. Please update js file again."
                })
                document.getElementById("save-web-channel").click();
            } else if (response["status"] == 301) {
                M.toast({
                    "html": "This Custom intent does not exist"
                })
            } else if (response["status"] == 401) {
                M.toast({
                    "html": response['status_message']
                })
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

}

$("#language-box-options-container .option .item-checkbox").change(function(){
   
    enable_disable_auto_language_detection_toogle();
    
});

$("#is-input-textfield").change(function() {
    if(!this.checked) {
        $("#enable_response_form_assist").prop("checked", false);
        $("#enable_response_form_assist").prop("disabled", true);

    } else {
        $("#enable_response_form_assist").prop("disabled", false);        
    }
});


//  will uncomment and complete this in next pr

// function is_form_assist_or_auto_pop_up_enabled(){

//     let form_assist_enabled = document.getElementById("enable_form_assist").checked

//     var is_auto_popup_enabled_desktop = document.getElementById("is-bot-auto-popup-allowed-desktop").checked;
//     var is_auto_popup_enabled_mobile = document.getElementById("is-bot-auto-popup-allowed-mobile").checked;

//     return form_assist_enabled || is_auto_popup_enabled_desktop || is_auto_popup_enabled_mobile;


// }

// function disable_web_landing_prompt_message(){

// }

// function enable_web_landing_prompt_message(){

// }

// function handle_web_landing_prompt(){

//     if(is_form_assist_or_auto_pop_up_enabled()){
//         disable_web_landing_prompt_message()
//     }else{
//         enable_web_landing_prompt_message()
//     }
// }

// $(document).ready(function() {
//     handle_web_landing_prompt();
//     console.log("hey")
// });

// $('#enable_form_assist, #is-bot-auto-popup-allowed-desktop, #is-bot-auto-popup-allowed-mobile').change(function() {
//     console.log("hey")
//     handle_web_landing_prompt();
    
// });

function html_tags_remover(text) {

    return text.replace(/<\/?[^>]+(>|$)/g, "").trim();
}
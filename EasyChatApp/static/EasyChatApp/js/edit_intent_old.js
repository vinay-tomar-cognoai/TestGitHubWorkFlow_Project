$(document).ready(function() {
    $("#easychat-intent-threshold").ionRangeSlider({
        min: 0,
        max: 1,
        step: 0.01
    });

    var intent_id = get_url_vars()["intent_pk"];

    if (intent_id != undefined && intent_id != null && intent_id != '') {
        encrypted_intent_id = EncryptVariable(intent_id);

        var external_function_str = 'function trigger_intent_' + intent_id + '() {\n\n    trigger_chatbot_query("' + encrypted_intent_id + '");\n    return;\n}';
        var editor = ace.edit("easychat_extent_trigger_function_editor-_div");
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
    var short_name_input_field = document.getElementById("enter_intent_short_name")
    short_name_input_field.addEventListener('input', () => {
        document.getElementById("short_name_field-char-count").innerHTML = short_name_input_field.value.length
    });
})

function copy_to_clipboard() {

    var ace_lines = document.getElementsByClassName("ace_line");
    var text = "";
    for (var i=0; i<ace_lines.length; i++){
        text += ace_lines[i].innerText;
        if (ace_lines.length-1 != i){
            text += "\n";
        }
    }

    const el = document.createElement('textarea');
    el.value = text;
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
        "html": "Function copied to clipboard"
    }, 2000)

    console.log("click copy")
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

            var file_size = 30000;
            if (input_upload_image.size > file_size) {
                e.target.value = "";
                M.toast({
                    "html": "Uploaded icon size is more than 30KB"
                }, 2000);
                document.getElementById("intent-icon-upload-error-message").innerText = "Uploaded icon size is more than 30KB";
                document.getElementById("intent-icon-upload-error-message").style.display = "block";
                return;
            }

            var file_path = input_upload_image.name.split(".")[input_upload_image.name.split(".").length - 1].trim().toLowerCase();

            if (file_path != "png" && file_path != "svg") {
                e.target.value = "";
                M.toast({
                    "html": "File format not supported"
                }, 2000);
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
    var response = await upload_image();

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
}

function add_intent_icon(icon_src) {
    var json_string = JSON.stringify({
        intent_pk: intent_pk,
        icon_src: icon_src
    })
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var xhttp = new XMLHttpRequest();
    var params = 'json_string=' + json_string
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
    var json_string = JSON.stringify({
        intent_pk: intent_pk
    })
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var xhttp = new XMLHttpRequest();
    var params = 'json_string=' + json_string
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
                setTimeout(function () {window.location.reload()}, 2000);
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

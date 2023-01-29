var uploaded_file = [];

/////////////////////////////// Encryption And Decription //////////////////////////

function CustomEncrypt(msgString, key) {
    // msgString is expected to be Utf8 encoded
    var iv = EasyChatCryptoJS.lib.WordArray.random(16);
    var encrypted = EasyChatCryptoJS.AES.encrypt(msgString, EasyChatCryptoJS.enc.Utf8.parse(key), {
        iv: iv
    });
    var return_value = key;
    return_value += "." + encrypted.toString();
    return_value += "." + EasyChatCryptoJS.enc.Base64.stringify(iv);
    return return_value;
}

function generateRandomString(length) {
    var result = '';
    var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    var charactersLength = characters.length;
    for (var i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
}


function EncryptVariable(data) {

    utf_data = EasyChatCryptoJS.enc.Utf8.parse(data);
    encoded_data = utf_data;
    // encoded_data = EasyChatCryptoJS.enc.Base64.stringify(utf_data);
    random_key = generateRandomString(16);
    // console.log(random_key)
    encrypted_data = CustomEncrypt(encoded_data, random_key);

    return encrypted_data;
}


function custom_decrypt(msg_string) {

    var payload = msg_string.split(".");
    var key = payload[0];
    var decrypted_data = payload[1];
    var decrypted = EasyChatCryptoJS.AES.decrypt(decrypted_data, EasyChatCryptoJS.enc.Utf8.parse(key), {
        iv: EasyChatCryptoJS.enc.Base64.parse(payload[2])
    });
    return decrypted.toString(EasyChatCryptoJS.enc.Utf8);
}

////////////////////////////////////////////////////////////////////////////////////

function upload_details_over_server(element) {

    return new Promise(function(resolve, reject) {
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
                    document.getElementById(element.id + "-name").innerText = response.src.split("/")[response.src.split("/").length - 1];
	                document.getElementById(element.id + "-img").src = response.src;
                }else{
                	alert("Unable to load image. Please try after sometime");
                }
            },
            error: function(xhr, textstatus, errorthrown) {
                console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
            }
        });
    })
}

function handle_logo_upload_input_change(element) {
	selected_file = element.files[0];

    var reader = new FileReader();
    reader.readAsDataURL(selected_file);
    reader.onload = function() {

        base64_str = reader.result.split(",")[1];

        uploaded_file = [];
        uploaded_file.push({
            "filename": selected_file.name,
            "base64_file": base64_str
        });

        upload_details_over_server(element);
    };

    reader.onerror = function(error) {
        console.log('Error: ', error);
    };

}

function save_general_whitelabel_settings(reset, reset_type) {

    if (!reset) {
        general_logo = document.getElementById("general-logo-upload-input-img").getAttribute("src");
        general_page_logo = document.getElementById("general-page-logo-upload-input-img").getAttribute("src");
        general_primary_color = document.getElementById("general-primary-color").value.trim();
        general_secondary_color = document.getElementById("general-secondary-color").value.trim();
        hide_login_with_gsuite_button = document.getElementById("hide-login-with-gsuite").checked;
        disabled_multifactor_authentication_button = document.getElementById("disabled-multifactor-authentication").checked;
        general_favicon = document.getElementById("general-favicon-input-img").getAttribute("src");
        smtp_email_id = document.getElementById("general-smtp-email-id").value.trim();
        smtp_email_password = document.getElementById("general-smtp-email-password").value.trim();
        replace_name_over_entire_console = document.getElementById("replace-easychat-over-console").value.trim();
        general_email_signature = document.getElementById("general-email-signature").value;
        enable_footer_over_entire_console = document.getElementById("enable-footer-over-entire-console").checked;
        legal_name = document.getElementById("general-legal-name").value.trim();
        general_title = document.getElementById("general-title-text").value.trim();

        if (general_primary_color == "") {
            M.toast({
                "html": "Please provide the primary color code."
            }, 2000);
            return;
        }

        if (general_secondary_color == "") {
            M.toast({
                "html": "Please provide the secondary color code."
            }, 2000);
            return;
        }

        if (general_title == "") {
            M.toast({
                "html": "Please provide the title text"
            }, 2000);
            return;
        }

        if (smtp_email_id == "") {
            M.toast({
                "html": "Please provide email id"
            }, 2000);
            return;
        }

        if (smtp_email_password == "") {
            M.toast({
                "html": "Please provide Password"
            }, 2000);
            return;
        }

        if (replace_name_over_entire_console == "") {
            M.toast({
                "html": "Please provide a word to replace"
            }, 2000);
            return;
        }

        if (general_email_signature == "") {
            M.toast({
                "html": "Please provide a signature."
            }, 2000);
            return;
        }

        if (legal_name == "") {
            M.toast({
                "html": "Please provide a legal name"
            }, 2000);
            return;
        }

        json_string = JSON.stringify({
            "reset": "false",
            "reset_type": "",
            "general_logo": general_logo,
            "general_page_logo": general_page_logo,
            "general_primary_color": general_primary_color,
            "general_secondary_color": general_secondary_color,
            "hide_login_with_gsuite_button": hide_login_with_gsuite_button,
            "disabled_multifactor_authentication_button":disabled_multifactor_authentication_button,
            "general_favicon": general_favicon,
            "smtp_email_id": smtp_email_id,
            "smtp_email_password": smtp_email_password,
            "replace_name_over_entire_console": replace_name_over_entire_console,
            "general_email_signature": general_email_signature,
            "enable_footer_over_entire_console": enable_footer_over_entire_console,
            "legal_name": legal_name,
            "general_title": general_title
        });
    } else {
        json_string = JSON.stringify({
            "reset": "true",
            "reset_type": reset_type
        })
    }

    var csrf_token = $('input[name="csrfmiddlewaretoken"]').val();
    json_string = EncryptVariable(json_string);

    encrypted_data = {
        "Request": json_string
    }

    var params = JSON.stringify(encrypted_data);

    $.ajax({
        url: "/developer-console/whitelabel/save-general-whitelabel-settings/",
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
            if(response.status == 200){
            	M.toast({
                    "html": "Details saved successfully"
                }, 2000);
                setTimeout(function(){ window.location.reload(); }, 2000);
            }else{
                M.toast({
                    "html": "Unable to save details. Please try again later."
                }, 2000);
            }
        },
        error: function(xhr, textstatus, errorthrown) {
            M.toast({
                "html": "Please report this error: " + xhr.status
            }, 2000);
        }
    });

}

function show_password() {
    document.getElementById("general-smtp-email-password").type = "text";
    document.getElementById("whitelabel_password_show_icon").style.display = "none";
    document.getElementById("whitelabel_password_hide_icon").style.display = "inline-block";
}

function hide_password() {
    document.getElementById("general-smtp-email-password").type = "password";
    document.getElementById("whitelabel_password_show_icon").style.display = "inline-block";
    document.getElementById("whitelabel_password_hide_icon").style.display = "none";
}

function show_whitelabel_theme(ele) {

    var setcolor = $(ele).val();
    ele.style.setProperty("background-color", "#" + setcolor, "important");

}

$(document).ready(function() {
    $('.tooltipped').tooltip();
    $('.dropdown-trigger').dropdown();
});

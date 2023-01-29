$(document).on("change", "#cognomeet-console-logo-input, #cognomeet-console-favicon-input", function (e) {
    var element = e.target;
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

        upload_cognomeet_console_img(element);
    };

    reader.onerror = function(error) {
        console.log('Error: ', error);
    };
});

function upload_cognomeet_console_img(element) {

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
                    var filename = (response.src).split("/")
                    filename = filename[filename.length - 1]
                    if(element.id == "cognomeet-console-logo-input") {
                        document.getElementById("cognomeet-logo-file-name").innerHTML = filename;
                        document.getElementById("cognomeet-console-logo").src = response.src;
                    } else if (element.id == "cognomeet-console-favicon-input") {
                        document.getElementById("cognomeet-favicon-file-name").innerHTML = filename;
                        document.getElementById("cognomeet-console-favicon").src = response.src;
                    }
                } else {
                    M.toast({
                        "html": "Unable to load image. Please try after sometime"
                    }, 2000);
                }
            },
            error: function(xhr, textstatus, errorthrown) {
                console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
            }
        });
    })
}

function save_cognomeet_whitelabel_settings() {
    var cognomeet_console_logo = document.getElementById("cognomeet-console-logo").getAttribute("src");
    var cognomeet_console_favicon = document.getElementById("cognomeet-console-favicon").getAttribute("src");
    var cognomeet_console_title = document.getElementById("cognomeet-console-title").value.trim();

    if(!cognomeet_console_logo) {
        M.toast({
            "html": "Please select a logo."
        }, 2000);
        return;
    } 

    if(!cognomeet_console_favicon) {
        M.toast({
            "html": "Please select a favicon."
        }, 2000);
        return;
    }

    if(!cognomeet_console_title) {
        M.toast({
            "html": "Please provide the title text."
        }, 2000);
        return;
    } 
    
    if(cognomeet_console_title.length > 30) {
        M.toast({
            "html": "Title text cannot be more than 30 characters."
        }, 2000);
        return;
    } 

    json_string = JSON.stringify({
        "cognomeet_console_logo": cognomeet_console_logo,
        "cognomeet_console_favicon": cognomeet_console_favicon,
        "cognomeet_console_title": cognomeet_console_title
    });

    var csrf_token = $('input[name="csrfmiddlewaretoken"]').val();
    json_string = EncryptVariable(json_string);

    encrypted_data = {
        "Request": json_string
    }

    var params = JSON.stringify(encrypted_data);

    $.ajax({
        url: "/developer-console/whitelabel/save-cognomeet-whitelabel-settings/",
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

function reset_cognomeet_settings(setting_type) {

    json_string = JSON.stringify({
        "setting_type": setting_type
    });

    var csrf_token = $('input[name="csrfmiddlewaretoken"]').val();
    json_string = EncryptVariable(json_string);

    encrypted_data = {
        "Request": json_string
    }

    var params = JSON.stringify(encrypted_data);

    $.ajax({
        url: "/developer-console/whitelabel/reset-cognomeet-whitelabel-settings/",
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
            if(response.status == 200) {
                if(setting_type == "logo") {
                    document.getElementById("cognomeet-logo-file-name").innerHTML = response.filename;
                    document.getElementById("cognomeet-console-logo").src = response.src;
                } else if (setting_type == "favicon") {
                    document.getElementById("cognomeet-favicon-file-name").innerHTML = response.filename;
                    document.getElementById("cognomeet-console-favicon").src = response.src;
                }
            } else {
                M.toast({
                    "html": "Unable to reset. Please try again later."
                }, 2000);
            }
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        }
    });

}
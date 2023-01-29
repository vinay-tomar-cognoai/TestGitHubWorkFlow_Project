var upload_file_limit_size = 5120000
var alexa_uploaded_welcome_image_src = ""
$(document).on("click", "#upload-alexa-welcome-image", function(e) {
    e.preventDefault();
    var input_upload_image = ($("#input_upload_image_bot_alexa_welcome_message"))[0].files[0]

    if (input_upload_image == null || input_upload_image == undefined) {
        M.toast({
            "html": "Please select a file."
        }, 2000);

        setTimeout(function() {
            $('#modal-upload-image').modal('open');
        }, 200);
        return false;
    }
    if (input_upload_image.name.match(/\.(jpeg|jpg|gif|png)$/) == null) {
        M.toast({
            "html": "File format is not supported"
        }, 2000);
        setTimeout(function() {
            $('#modal-upload-image').modal('open');
        }, 200);
        return false;
    }
    if (input_upload_image.size > upload_file_limit_size) {
        M.toast({
            "html": "Size limit exceed(should be less than 5 MB)."
        }, 2000);

        setTimeout(function() {
            $('#modal-upload-image').modal('open');
        }, 200);
        return;
    }

    if (check_malicious_file(input_upload_image.name) == true) {
        setTimeout(function() {
            $('#modal-upload-image').modal('open');
        }, 200);
        return false;
    }

    document.getElementById("uploaded-alexa-bot-welcome-image").style.display = "none";
    try {
        $("#remove-bot-alexa-welcome-image").hide()
    } catch {
        $("#remove-bot-alexa-welcome-image").attr("disabled", true);
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

        upload_welcome_image_for_alexa();
    };
    reader.onerror = function(error) {
        console.log('Error: ', error);
    };
});

async function upload_welcome_image_for_alexa() {
    var response = await upload_image();
    if (response && response.status == 200) {
        src = response.src;
        alexa_uploaded_welcome_image_src = src
        compressed_src = response["compressed_image_path"]
        document.getElementById("uploaded-alexa-bot-welcome-image").src = src;
        document.getElementById("uploaded-alexa-bot-welcome-image").dataset.compressed_src = compressed_src;
        document.getElementById("uploaded-alexa-bot-welcome-image").style.display = "inline-block";
        document.getElementById('input_upload_image_bot_alexa_welcome_message2').value = "";
        document.getElementById('add-alexa-welcome-image').style.display = "none"
        try {
            $("#remove-bot-alexa-welcome-image").show()
        } catch {
            $("#remove-bot-alexa-welcome-image").attr("disabled", false);
        }
    }
}

$(document).on("click", "#remove-bot-alexa-welcome-image", function(e) {
    document.getElementById("uploaded-alexa-bot-welcome-image").src = "";
    alexa_uploaded_welcome_image_src = ""
    document.getElementById("uploaded-alexa-bot-welcome-image").style.display = "none";
    document.getElementById('add-alexa-welcome-image').style.display = ""
    try {
        $("#remove-bot-alexa-welcome-image").hide()
    } catch {
        $("#remove-bot-alexa-welcome-image").attr("disabled", true);
    }
});
$(document).on("keypress keydown paste", "#alexa-project-id", function(e) {
    setTimeout(function() {
        var project_id = $("#alexa-project-id").val();
        project_id = project_id.trim();
        if(project_id == ""){
            document.getElementById("add-alexa-project-details").classList.add("disabled");
            disable_alexa_project_details();
        }else{
            document.getElementById("add-alexa-project-details").classList.remove("disabled");
            enable_alexa_project_details();
        }
    }, 100);
});


function add_alexa_project_id(channel_name, to_show_modal=true){
    let project_id = $("#alexa-project-id").val();
    project_id = project_id.trim();
    if(project_id == ""){
        showToast("Project Id Can not be Empty", 2000);
        return false;
    }
    detail_obj_pk = undefined
    let bot_id = get_url_vars()["id"];
    img_el = document.getElementById("uploaded-alexa-bot-welcome-image")
    attached_file_src = img_el.getAttribute("src");
    var json_string = JSON.stringify({
       project_id:project_id,
       bot_id:bot_id,
       attached_file_src:attached_file_src,
       channel_name: channel_name
    })
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: "/chat/add-google-alexa-project-details/",
        type: "POST",
        data: {
            json_string: json_string
        },
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            
            if(response["status"] == 200){

                project_id = response["project_id"]
                client_id = response["client_id"]
                client_secret = response["client_secret"] 
                project_name = response["name"]
                redirect_uris = response["redirect_uris"]
                client_type = response["client_type"] 
                detail_obj_pk = response["details_obj_id"]
                authorization_grant_type = response["authorization_grant_type"]
                document.getElementById("alexa-project-name").innerHTML = project_name
                document.getElementById("alexa-project-project_id").innerHTML = project_id
                document.getElementById("alexa-project-client_id").innerHTML = client_id 
                document.getElementById("alexa-project-client_secret").innerHTML = client_secret
                document.getElementById("alexa-project-redirect_uris").innerHTML = redirect_uris
                document.getElementById("alexa-project-client_type").innerHTML = client_type
                document.getElementById("alexa-project-authorization_grant_type").innerHTML = authorization_grant_type
                if(to_show_modal){
                    $("#modal-alexa-project-details").modal('open')
                }
                enable_alexa_project_details(detail_obj_pk);

            }else{
                showToast("Something Went wrong", 2000);
            }

        },
        error: function(jqXHR, exception) {
            $("#processing").hide();
            Materialize.toast("Error!", 2000);
        },
    });
return true
}

function save_auth_page_content(detail_obj_id, channel) {

    var editor = ace.edit("editor-code");
    var code = editor.getValue();

    var csrf_token = get_csrf_token();
    var json_string = JSON.stringify({
        code: code,
        channel: channel,
        detail_obj_id: detail_obj_id,
    })
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var xhttp = new XMLHttpRequest();
    var params = 'json_string=' + json_string
    xhttp.open("POST", "/chat/save-auth-page-content/", true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {

                M.toast({
                    "html": "Changes saved successfully."
                }, 2000);
                setTimeout(function(e) {
                    window.location.reload();
                }, 2000);

            } else {
                M.toast({
                    "html": "Unable to save data. Please try after some time."
                }, 2000);
            }
        }
    }
    xhttp.send(params);
}


function save_sign_in_processor_content(processor_type, detail_obj_id, name, is_autosave = false) {

    if(document.getElementById("processor-name").value.toString().trim() == "")
    {
        M.toast({
                    "html": "Processor name can't be empty."
                }, 2000);
        return;
    }
     var editor = ace.edit("editor-code");
    var code = editor.getValue();

    if (check_for_system_commands(code)) {
        document.getElementById("easychat-processor-status").value = "\n\nError(s):";
        show_processor_errors();
        return;
    };

    document.getElementById("easychat-processor-status").style.display = 'none';
    document.getElementById('system-command-error').style.display = 'none';

    var is_new = false;

    if (name == "asdhs524fdbghdagfht52eg2fc") {
        is_new = true
    }
    name = document.getElementById("processor-name").value

    csrf_token = get_csrf_token();
    var json_string = JSON.stringify({
        code: code,
        processor_type: processor_type,
        detail_obj_id: detail_obj_id,
        name: name,
        is_new: is_new,
    })
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var xhttp = new XMLHttpRequest();
    var params = 'json_string=' + json_string
    xhttp.open("POST", "/chat/save-signin-processor-content/", true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                if (is_autosave == false) {

                    M.toast({
                        "html": "Changes saved successfully."
                    }, 2000);
                    setTimeout(function(e) {
                        window.location.reload();
                    }, 2000);
                } else {
                    clearTimeout(autosave_session_timer)
                    document.getElementById("easychat-autosave-span").style.display = "inline-block";
                    setTimeout(function(e) {
                        document.getElementById("easychat-autosave-span").style.display = "none";
                    }, 2000)
                }
            } else if (response["status"] == 300) {

                M.toast({
                    "html": response["message"]
                })
            } else if (response['status'] == 400) {
                if (check_for_system_commands(code)) {
                    document.getElementById("easychat-processor-status").value = "\n\nError(s):";
                    show_processor_errors();
                }
            }
        }
    }
    xhttp.send(params);


}

function disable_alexa_project_details(){
    document.getElementById("alexa-project-oauth-status-get-otp").classList.add("disabled");
    document.getElementById("alexa-project-oauth-status-verify-otp").classList.add("disabled");
    document.getElementById("add-alexa-welcome-image").classList.add("disabled");
}

function enable_alexa_project_details(detail_obj_pk){
    if(detail_obj_pk != undefined && detail_obj_pk != null){
        document.getElementById("alexa-project-oauth-status-get-otp").classList.remove("disabled");
        document.getElementById("alexa-project-oauth-status-get-otp").href="/chat/edit-signin-processor-console/?id=" + detail_obj_pk + "&type=get_otp"
        document.getElementById("alexa-project-oauth-status-verify-otp").classList.remove("disabled");
        document.getElementById("alexa-project-oauth-status-verify-otp").href="/chat/edit-signin-processor-console/?id=" + detail_obj_pk + "&type=verify_otp"
        document.getElementById("alexa-project-auth-page").href="/chat/edit-console-page/?id=" + detail_obj_pk + "&channel=alexa"
    }
    document.getElementById("add-alexa-welcome-image").classList.remove("disabled");
    document.getElementById("alexa-project-auth-page").classList.remove("disabled");
}
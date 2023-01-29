$(document).ready(function() {

    var email_id_input = document.getElementsByClassName("email-id-input")[0];

    var email_tag_container = document.getElementsByClassName("email_id_tag_container")[0];
    new LivechatTagElement(email_id_input, email_tag_container);
});

class LivechatTagElement {
    constructor(element, tag_container) {
        this.element = element;
        this.tag_container = tag_container;
        var email_address = [];
        var email_address_list_container = document.getElementsByClassName("livechat-console-email-ids");
        for(let i = 0; i < email_address_list_container.length; i++) {
            email_address.push((email_address_list_container[i]).attributes.value.value);
        }
        this.email_id_list = email_address;
        this.initialize();
    }

    initialize() {
        var _this = this;
        _this.add_event_listeners_in_tag_element();
        if(_this.email_id_list.length > 0){
            for(let i = 0; i<_this.email_id_list.length; i++){
            var tag_remove_btns = _this.tag_container.querySelectorAll("[class='tag-remove-btn']");
            tag_remove_btns.forEach(function(tag_remove_btn, index) {
                $(tag_remove_btn).on("click", function() {
                    _this.remove_email_id_tags(index);
                });
            });   
            }
        }
    }

    add_event_listeners_in_tag_element() {
        var _this = this;

        $(_this.element).on("keypress", function(event) {
            var target = event.target;
            var value = target.value;


            if (event.key === 'Enter' || event.keyCode == 13) {
                let val = value.trim().replace(/(<([^>]+)>)/ig, '');
                if (!check_valid_email(value)) {
                    M.toast({
                        "html": "Please enter valid email"
                    }, 2000);

                } else {
                    var email_id_exist = _this.email_id_list.some(value => value === val);
                    if (email_id_exist) {
                        M.toast({
                            "html": "Email ID already exist"
                        }, 2000);

                    } else {
                        _this.email_id_list.push(value);
                        _this.render_email_id_tags();
                    }

                    target.value = "";
                }
            }
        });
    }

    render_email_id_tags() {
        var _this = this;

        function add_event_listener_in_remove_btn() {

            var tag_remove_btns = _this.tag_container.querySelectorAll("[class='tag-remove-btn']");
            tag_remove_btns.forEach(function(tag_remove_btn, index) {
                $(tag_remove_btn).on("click", function() {
                    _this.remove_email_id_tags(index);
                });
            });
        }

        var html = "";
        _this.email_id_list.forEach(function(value, index) {
            html += `
        <li class="bg-primary cognoai-tag livechat-console-email-ids" value="${value}" >
            <span style="font-weight: 500;">${value}</span>
            <span class="tag-remove-btn">x</span>
        </li>`;
        });

        _this.tag_container.innerHTML = html;

        add_event_listener_in_remove_btn();
    }

    remove_email_id_tags(removed_index) {
        var _this = this;

        var updated_email_id_list = [];
        for (var idx = 0; idx < _this.email_id_list.length; idx++) {
            if (idx == removed_index) {
                continue;
            }
            updated_email_id_list.push(_this.email_id_list[idx]);
        }

        _this.email_id_list = updated_email_id_list;
        _this.render_email_id_tags();
    }

    get_value() {
        var _this = this;
        return _this.email_id_list;
    }

    update_value(email_id_list) {
        var _this = this;
        _this.email_id_list = email_id_list;
        _this.render_email_id_tags();
    }
}

function check_valid_email(email_id) {
    if (!email_id) {
        return false;
    }

    var regex_email = /^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/;
    if (!regex_email.test(email_id)) {
        return false;
    }
    return true;
}

$(document).on("change", "#livechat-console-logo, #livechat-console-favicon", function (e) {
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

        upload_livechat_console_img(element);
    };

    reader.onerror = function(error) {
        console.log('Error: ', error);
    };
});

function upload_livechat_console_img(element) {

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
                    document.getElementById(element.id + "-name").innerHTML = filename;
                    document.getElementById(element.id + "-img").src = response.src;                    
                }else{
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

function save_livechat_console_settings() {

    var livechat_console_logo = document.getElementById("livechat-console-logo-img").getAttribute("src");
    var livechat_console_favicon = document.getElementById("livechat-console-favicon-img").getAttribute("src");
    var livechat_console_title = document.getElementById("livechat-console-title").value;
    var email_address = [];
    var email_address_list_container = document.getElementsByClassName("livechat-console-email-ids");
    for(let i = 0; i < email_address_list_container.length; i++){
        email_address.push((email_address_list_container[i]).attributes.value.value);
    }

    if(!livechat_console_logo) {
        M.toast({
            "html": "Please select a logo."
        }, 2000);
        return;
    } 

    if(!livechat_console_favicon) {
        M.toast({
            "html": "Please select a favicon."
        }, 2000);
        return;
    }

    if(!livechat_console_title) {
        M.toast({
            "html": "Please provide the title text."
        }, 2000);
        return;
    }  

    if(email_address.length == 0) {
        M.toast({
            "html": "Please enter at least one email ID."
        }, 2000);
        return;        
    }

    json_string = JSON.stringify({
        "livechat_console_logo": livechat_console_logo,
        "livechat_console_favicon": livechat_console_favicon,
        "livechat_console_title": livechat_console_title,
        "email_address": email_address
    });

    var csrf_token = $('input[name="csrfmiddlewaretoken"]').val();
    json_string = EncryptVariable(json_string);

    encrypted_data = {
        "Request": json_string
    }

    var params = JSON.stringify(encrypted_data);

    $.ajax({
        url: "/developer-console/whitelabel/save-livechat-whitelabel-settings/",
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

function set_default_livechat_settings(setting_type) {

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
        url: "/developer-console/whitelabel/reset-livechat-whitelabel-settings/",
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

                if(setting_type == "logo") {
                    document.getElementById("livechat-console-logo-name").innerHTML = response.filename;
                    document.getElementById("livechat-console-logo-img").src = response.src;
                } else if (setting_type == "favicon") {
                    document.getElementById("livechat-console-favicon-name").innerHTML = response.filename;
                    document.getElementById("livechat-console-favicon-img").src = response.src;
                }


            }else{
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
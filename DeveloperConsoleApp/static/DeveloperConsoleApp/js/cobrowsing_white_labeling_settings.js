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

class CobrowseTagElement {
    constructor(element, tag_container) {
        this.element = element;
        this.tag_container = tag_container;
        
        var email_id_list_elements = document.getElementsByClassName("masking-pii-email");
        var email_id_list = [];
        for (var i=0; i<email_id_list_elements.length; i++) {
            email_id_list.push(email_id_list_elements[i].innerText);
        }

        this.email_id_list = email_id_list;
        this.initialize();
    }

    initialize() {
        var _this = this;
        _this.add_event_listeners_in_tag_element();
        _this.render_email_id_tags();
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
        <li class="bg-primary cognoai-tag">
            <span class="masking-pii-email" style="font-weight: 500;">${value}</span>
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

$(document).ready(function() {
    var email_id_input = document.getElementsByClassName("email-id-input")[0];
    var email_tag_container = document.getElementsByClassName("email_id_tag_container")[0];
    new CobrowseTagElement(email_id_input, email_tag_container);
});

$(document).on("change", "#cobrowse-console-logo-input, #cobrowse-console-favicon-input", function (e) {
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

        upload_cobrowse_console_img(element);
    };

    reader.onerror = function(error) {
        console.log('Error: ', error);
    };
});

function upload_cobrowse_console_img(element) {

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
                    if(element.id == "cobrowse-console-logo-input") {
                        document.getElementById("cobrowse-logo-file-name").innerHTML = filename;
                        document.getElementById("cobrowse-console-logo").src = response.src;
                    } else if (element.id == "cobrowse-console-favicon-input") {
                        document.getElementById("cobrowse-favicon-file-name").innerHTML = filename;
                        document.getElementById("cobrowse-console-favicon").src = response.src;
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

function save_cobrowsing_whitelabel_settings() {
    var cobrowse_console_logo = document.getElementById("cobrowse-console-logo").getAttribute("src");
    var cobrowse_console_favicon = document.getElementById("cobrowse-console-favicon").getAttribute("src");
    var cobrowse_console_title = document.getElementById("cobrowse-console-title").value.trim();
    
    var masking_pii_email_ids = [];
    var masking_pii_email_elements = document.getElementsByClassName("masking-pii-email");
    for (var i = 0; i < masking_pii_email_elements.length; i++) {
        masking_pii_email_ids.push(masking_pii_email_elements[i].innerText.trim());
    }

    if(!cobrowse_console_logo) {
        M.toast({
            "html": "Please select a logo."
        }, 2000);
        return;
    } 

    if(!cobrowse_console_favicon) {
        M.toast({
            "html": "Please select a favicon."
        }, 2000);
        return;
    }

    if(!cobrowse_console_title) {
        M.toast({
            "html": "Please provide the title text."
        }, 2000);
        return;
    }

    if(cobrowse_console_title.length > 30) {
        M.toast({
            "html": "Title text cannot be more than 30 characters."
        }, 2000);
        return;
    }

    if(masking_pii_email_ids.length == 0) {
        M.toast({
            "html": "Please enter at least one email ID."
        }, 2000);
        return;        
    }

    json_string = JSON.stringify({
        "cobrowse_console_logo": cobrowse_console_logo,
        "cobrowse_console_favicon": cobrowse_console_favicon,
        "cobrowse_console_title": cobrowse_console_title,
        "masking_pii_email_ids": masking_pii_email_ids
    });

    var csrf_token = $('input[name="csrfmiddlewaretoken"]').val();
    json_string = EncryptVariable(json_string);

    encrypted_data = {
        "Request": json_string
    }

    var params = JSON.stringify(encrypted_data);

    $.ajax({
        url: "/developer-console/whitelabel/save-cobrowsing-whitelabel-settings/",
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

function reset_cobrowse_settings(setting_type) {

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
        url: "/developer-console/whitelabel/reset-cobrowse-whitelabel-settings/",
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
                    document.getElementById("cobrowse-logo-file-name").innerHTML = response.filename;
                    document.getElementById("cobrowse-console-logo").src = response.src;
                } else if (setting_type == "favicon") {
                    document.getElementById("cobrowse-favicon-file-name").innerHTML = response.filename;
                    document.getElementById("cobrowse-console-favicon").src = response.src;
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
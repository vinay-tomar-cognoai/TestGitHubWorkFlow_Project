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


class LivechatTagElement {
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
    new LivechatTagElement(email_id_input, email_tag_container);
});


function save_easychatapp_whitelabel_settings(reset, reset_type) {

    if (!reset) {
        chatbot_logo = document.getElementById("easychatapp-logo-img").getAttribute("src");
        tab_logo = document.getElementById("easychatapp-favicon-img").getAttribute("src");
        title_text = document.getElementById("easychatapp-title-text").value.trim();
        disable_show_brand_name = document.getElementById("easychatapp-disable-brand-name").checked;

        if (title_text == "") {
            M.toast({
                "html": "Please provide the title text"
            }, 2000);
            return;
        }

        masking_pii_email_ids = [];
        masking_pii_email_elements = document.getElementsByClassName("masking-pii-email");
        for (var i=0; i<masking_pii_email_elements.length; i++) {
            masking_pii_email_ids.push(masking_pii_email_elements[i].innerText.trim());
        }

        if (masking_pii_email_ids.length == 0) {
            M.toast({
                "html": "Please enter at least one email ID."
            }, 2000);
            return;
        }

        json_string = JSON.stringify({
            "reset": "false",
            "reset_type": "",
            "chatbot_logo": chatbot_logo,
            "tab_logo": tab_logo,
            "title_text": title_text,
            "disable_show_brand_name": disable_show_brand_name,
            "masking_pii_email_ids": masking_pii_email_ids
        })

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
        url: "/developer-console/whitelabel/save-easychatapp-whitelabel-settings/",
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
                    "html": response["message"]
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


function save_cognodeskapp_whitelabel_settings(reset, reset_type) {

    if (!reset) {
        chatbot_logo = document.getElementById("cognodeskapp-logo-img").getAttribute("src");
        tab_logo = document.getElementById("cognodeskapp-favicon-img").getAttribute("src");
        title_text = document.getElementById("cognodeskapp-title-text").value.trim();

        if (title_text == "") {
            M.toast({
                "html": "Please provide the title text"
            }, 2000);
            return;
        }

        json_string = JSON.stringify({
            "reset": "false",
            "reset_type": "",
            "chatbot_logo": chatbot_logo,
            "tab_logo": tab_logo,
            "title_text": title_text
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
        url: "/developer-console/whitelabel/save-cognodeskapp-whitelabel-settings/",
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

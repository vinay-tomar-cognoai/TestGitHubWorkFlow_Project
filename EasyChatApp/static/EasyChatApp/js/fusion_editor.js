$(document).ready(function(){
    $("#ameyo-config-btn").click(function(){
        save_fusion_config();
    });

    $(".fusion-select-notification-div .fusion-select-notification .close-svg svg").click(function(){
        $(".fusion-select-notification-div").hide(200);
    });

    $("#ameyo-config-api-select").select2({ 
        dropdownCssClass : "ameyo-config-api-options" 
    });

    $("#ameyo-config-api-select").change(function(){
      let editor_type = $("#ameyo-config-api-select").val();
      let bot_pk = window.SELECTED_BOT_PK;
      window.location = "/chat/fusion-editor/?bot_pk=" + bot_pk + "&editor_id=" + editor_type;
    });

    $("#save-ameyo-processor-btn").click(function(){
        save_fusion_processor(false);
    });

    $("#reset-ameyo-processor-btn").click(function(){
        save_fusion_processor(true);
    });

});

function save_fusion_config() {

    let bot_pk = window.SELECTED_BOT_PK;

    let app_id = $("#ameyo-app-id").val();
    let host_name = $("#ameyo-host-name").val();

    app_id = stripHTML(app_id);
    app_id = strip_unwanted_characters(app_id);

    host_name = stripHTML(host_name);

    if(app_id.trim() == "") {
        showToast("APP ID cannot be empty.", 2000);
        return;
    }

    if(host_name.trim() == "") {
        showToast("Host Name cannot be empty.", 2000);
        return;
    }

    var json_string = JSON.stringify({
        bot_pk: bot_pk,
        app_id: app_id,
        host_name: host_name
    })
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = 'json_string=' + json_string
    xhttp.open("POST", "/chat/save-fusion-config/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token); 
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                $("#ameyo-config-variable-apply-success").show(200);
                setTimeout(() => {
                  location.reload();
                }, "2000")
            } else if (response["status"] == 400) {
                showToast(response["message"], 2000);
            } else {
                $("#ameyo-config-variable-apply-failure").show(200);
            }
        }
    }
    xhttp.send(params);
}

function save_fusion_processor(is_reset) {

    let bot_pk = window.SELECTED_BOT_PK;
    let type_of_processor = window.TYPE_OF_PROCESSOR;

    var editor = ace.edit("editor-code");
    var code = editor.getValue();

    var json_string = JSON.stringify({
        bot_pk: bot_pk,
        type_of_processor: type_of_processor,
        code: code,
        is_reset: is_reset
    })
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = 'json_string=' + json_string
    xhttp.open("POST", "/chat/save-fusion-processor/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token); 
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {

                if(is_reset) {
                    showToast("Successfully Reset!", 2000);
                } else {
                    showToast("Successfully Saved!", 2000);
                }
                
                setTimeout(() => {
                  location.reload();
                }, "2000")
            } else {
                showToast(response["message"], 2000);
            }
        }
    }
    xhttp.send(params);
}
import { 
    get_character_limit,
    upload_excel,
 } from "../common";
import {
    custom_decrypt,
    EncryptVariable,
    showToast,
    validate_canned_response,
    validate_keyword,
    getCsrfToken,
} from "../utils";

const state = {
    upload_file_limit_size: 1024000,
};

function create_canned_response() {

    document.getElementById("special-character-error").value = "";
    document.getElementById("error-div").style.display = "none";
    let title = "None";
    let keyword = document.getElementById("canned-keyword").value.trim();
    if (keyword == "" || keyword.length == 0) {
        document.getElementById("special-character-error").innerHTML = "Please enter a valid keyword of length greater than 0.";
        document.getElementById("error-div").style.display = "block";
        showToast("Please enter a valid keyword.", 2000);
        return;
    }
    if(!validate_keyword("canned-keyword")){
        document.getElementById("special-character-error").innerHTML = "Please enter valid keyword (Only a-z, A-Z characters are allowed).";
        document.getElementById("error-div").style.display = "block";
        showToast("Please enter a valid keyword.", 2000);
        return;
    }
    let canned_response = document.getElementById("canned-response").value.trim();

    if (canned_response == "" || canned_response.length == 0) {
        document.getElementById("special-character-error").innerHTML = "Please enter a valid canned response of length greater than 0.";
        document.getElementById("error-div").style.display = "block";
        showToast("Please enter a valid canned response.", 2000);
        return;
    } 
    let response_recieved = validate_canned_response("canned-response");
    let is_valid_canned_resonse = response_recieved[response_recieved.length -1];
    response_recieved.pop();
    if(!is_valid_canned_resonse){
        let distinct_invalid_chars = new Set() , disallowed_char_text = "";
        for(let i = 0 ; i < response_recieved.length ; i++){
            distinct_invalid_chars.add(response_recieved[i]);
        }
        for(let key of distinct_invalid_chars){
            disallowed_char_text += key + " ";
        }
        document.getElementById("special-character-error").innerHTML = "Please enter a valid sentence " + disallowed_char_text + "are not allowed in canned response.";
        document.getElementById("error-div").style.display = "block";
        showToast("Please enter a valid canned response.", 2000);
        return;
    }

    const char_limit = get_character_limit();
    if (canned_response.length > char_limit.large) {
        document.getElementById("special-character-error").innerHTML = "Please enter a valid canned response within allowed length.";
        document.getElementById("error-div").style.display = "block";
        showToast(`Exceeding character limit of ${char_limit.large} characters in canned response`, 2000);
        return;
    }

    if (keyword.length > char_limit.small) {
        document.getElementById("special-character-error").innerHTML = "Please enter a valid keyword within allowed length.";
        document.getElementById("error-div").style.display = "block";
        showToast(`Exceeding character limit of ${char_limit.small} characters in keyword`, 2000);
        return;
    }

    let status = document.getElementById("canned-status").value;

    var json_string = JSON.stringify({
        title: title,
        keyword: keyword,
        response: canned_response,
        status: status,
    });
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/create-new-canned-response/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status_code"] == "200") {
                showToast("Canned response saved successfully!", 3000);
                setTimeout(()=>{location.reload();}, 2000);
            } else if (response["status_code"] == "300") {
                showToast("Canned response with duplicate keyword can't be created!", 5000);
            } else if (response["status_code"] == "301") {
                showToast("Canned response should not contain blacklisted words", 5000);
            } else if (response["status_code"] == "302") {
                document.getElementById("special-character-error").innerHTML =
                    response["status_message"];
                document.getElementById("error-div").style.display = "block";
                showToast("Can not add canned response", 5000);
            } else {
                showToast(response.status_message, 5000);
            }
        }
    };
    xhttp.send(params);
}

function edit_canned_response(canned_response_pk) {
    document.getElementById("special-character-error-edit-" + canned_response_pk).value = "";
    document.getElementById("error-div-edit-" + canned_response_pk).style.display = "none";

    let title = "None";
    let keyword = document.getElementById("canned-keyword-" + canned_response_pk).value;
    if (keyword == "" || keyword.trim().length == 0) {
        document.getElementById("special-character-error-edit-" + canned_response_pk).innerHTML = "Please enter a valid keyword of length greater than 0.";
        document.getElementById("error-div-edit-" + canned_response_pk).style.display = "block";
        showToast("Please enter a valid keyword.", 2000);
        return;
    }
    if(!validate_keyword("canned-keyword-" + canned_response_pk)){
        document.getElementById("special-character-error-edit-" + canned_response_pk).innerHTML = "Please enter valid keyword (Only a-z, A-Z characters are allowed).";
        document.getElementById("error-div-edit-" + canned_response_pk).style.display = "block";
        showToast("Please enter a valid keyword.", 2000);
        return;
    }
    let canned_response = document.getElementById("canned-response-" + canned_response_pk).value;
    if (canned_response == "" || canned_response.trim().length == 0) {
        document.getElementById("special-character-error-edit-" + canned_response_pk).innerHTML = "Please enter a valid canned response of length greater than 0.";
        document.getElementById("error-div-edit-" + canned_response_pk).style.display = "block";
        showToast("Please enter a valid canned response.", 2000);
        return;
    }
    let response_recieved = validate_canned_response("canned-response-" + canned_response_pk);
    let is_valid_canned_resonse = response_recieved[response_recieved.length -1];
    response_recieved.pop();
    if(!is_valid_canned_resonse){
        let distinct_invalid_chars = new Set() , disallowed_char_text = "";
        for(let i = 0 ; i < response_recieved.length ; i++){
            distinct_invalid_chars.add(response_recieved[i]);
        }
        for(let key of distinct_invalid_chars){
            disallowed_char_text += key + " ";
        }
        document.getElementById("special-character-error-edit-" + canned_response_pk).innerHTML = "Please enter a valid sentence " + disallowed_char_text + "are not allowed.";
        document.getElementById("error-div-edit-" + canned_response_pk).style.display = "block";
        showToast("Please enter a valid canned response.", 2000);
        return;
    }

    const char_limit = get_character_limit();
    if (canned_response.length > char_limit.large) {
        document.getElementById("special-character-error-edit-" + canned_response_pk).innerHTML = "Please enter a valid canned response within allowed length.";
        document.getElementById("error-div-edit-" + canned_response_pk).style.display = "block";
        showToast(`Exceeding character limit of ${char_limit.large} characters in canned response`, 2000);
        return;
    }

    if (keyword.length > char_limit.small) {
        document.getElementById("special-character-error-edit-" + canned_response_pk).innerHTML = "Please enter a valid keyword within allowed length.";
        document.getElementById("error-div-edit-" + canned_response_pk).style.display = "block";
        showToast(`Exceeding character limit of ${char_limit.small} characters in keyword`, 2000);
        return;
    }

    let status = document.getElementById("canned-status-" + canned_response_pk).value;
    var json_string = JSON.stringify({
        title: title,
        keyword: keyword,
        response: canned_response,
        status: status,
        canned_response_pk: canned_response_pk,
    });
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/edit-canned-response/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status_code"] == "200") {
                showToast("Canned response saved successfully!", 3000);
                setTimeout(()=>{location.reload();}, 2000);
            } else if (response["status_code"] == "300") {
                showToast("Canned response with duplicate keyword can't be created!", 5000);
                // setTimeout(location.reload(),2000);
            } else if (response["status_code"] == "301") {
                showToast("Canned response should not contain blacklisted words", 5000);
            } else if (response["status_code"] == "302") {
                document.getElementById(
                    "special-character-error-edit-" + canned_response_pk
                ).innerHTML = response["status_message"];
                document.getElementById("error-div-edit-" + canned_response_pk).style.display =
                    "block";
                showToast("Can not add canned response", 5000);
            } else {
                showToast(response.status_message, 5000);
            }
        }
    };
    xhttp.send(params);
}

function delete_canned_agent(canned_response_pk) {
    //canned_response_pk = elem.dataset.canned_response_pk;
    let canned_response_pk_list = [];
    canned_response_pk_list.push(canned_response_pk);
    let json_string = JSON.stringify({
        canned_response_pk_list: canned_response_pk_list,
    });
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/delete-canned-response/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            showToast("Deleted successfully!", 3000);
            setTimeout(()=>{location.reload();}, 2000);
        }
    };
    xhttp.send(params);
}

function on_canned_checkbox() {
    var canned_list = document.getElementsByClassName("canned-checkbox");
    var flag = 0;
    var selected_intent = 0;
    for (var i = 0; i < canned_list.length; i++) {
        if (document.getElementById(canned_list[i].id).checked) {
            selected_intent = selected_intent + 1;
        }
        else {
            flag = 1;
        }
    }

    if(flag == 0)
        document.getElementById("select-all-canned").checked = true
    else
        document.getElementById("select-all-canned").checked = false

    show_hide_canned_delete_btn(selected_intent != 0);
}

function show_hide_canned_delete_btn(show) {
    if (show) {
        document.getElementById("canned-delete-btn").style.display = "inline-block";
        document.getElementById("canned-mobile-delete-btn").style.display = "inline-block";
        document.getElementById("canned-add-btn").style.display = "none";
        document.getElementById("canned-mobile-add-btn").style.display = "none";
    } else {
        document.getElementById("canned-delete-btn").style.display = "none";
        document.getElementById("canned-mobile-delete-btn").style.display = "none";
        document.getElementById("canned-add-btn").style.display = "inline-block";
        document.getElementById("canned-mobile-add-btn").style.display = "inline-block";
    }
}

function delete_canned_response() {
    var canned_list = document.getElementsByClassName("canned-checkbox");
    var canned_response_pk_list = [];

    for (var i = 0; i < canned_list.length; i++) {
        if (document.getElementById(canned_list[i].id).checked) {
            canned_response_pk_list.push(canned_list[i].id.split("-")[2]);
        }
    }
    if (canned_response_pk_list.length == 0) {
        showToast("Please select at least one Canned response", 3000);
        return;
    }
    let json_string = JSON.stringify({
        canned_response_pk_list: canned_response_pk_list,
    });
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/delete-canned-response/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token); 
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            showToast("Deleted Successfully", 3000);
            setTimeout(()=>{location.reload();}, 2000);
        }
    };
    xhttp.send(params);
}

function submit_canned_response_excel() {
    document.getElementById("special-character-error-excel").value = "";
    document.getElementById("error-div-excel").style.display = "none";
    var canned_response_file = $("#real-file")[0].files[0];
    if (canned_response_file == undefined || canned_response_file == null) {
        showToast("Please provide excel sheet in required format.", 2000);
        return;
    }
    if (
        canned_response_file.name.split(".").pop() != "xlsx" &&
        canned_response_file.name.split(".").pop() != "xls"
    ) {
        showToast("Please upload file in correct format.", 2000);
        return;
    }
    if (canned_response_file.size > state.upload_file_limit_size) {
        showToast("Size limit exceed(should be less than 1 MB)", 2000);
        return;
    }

    var reader = new FileReader();
    reader.readAsDataURL(canned_response_file);
    reader.onload = function() {

        var base64_str = reader.result.split(",")[1];

        var uploaded_file = [];
        uploaded_file.push({
            "filename": canned_response_file.name,
            "base64_file": base64_str,
        });

        upload_canned_response_excel(uploaded_file);
    };

    reader.onerror = function(error) {
        console.log('Error: ', error);
    };
}

async function upload_canned_response_excel(uploaded_file){
    var response = await upload_excel(uploaded_file);
    if (response && response.status == 200) {
        var upload_button = document.getElementById("submit_canned_response_excel");
        upload_button.innerHTML = "Creating..";
        upload_button.style.cursor = "not-allowed";
        let status = document.getElementById("canned-status").value;
        var formData = new FormData();
        var src = window.location.origin + response["src"]
        formData.append("src", response["src"]);
        formData.append("canned-status", status);
        $.ajax({
            url: "/livechat/create-new-canned-response-excel/",
            type: "POST",
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                response = custom_decrypt(response);
                response = JSON.parse(response);
                if (response["status_code"] == 200) {
                    showToast("Successfully created canned response.", 2000);
                    setTimeout(()=>{window.location.reload();}, 2000)
                } else if (response["status_code"] == "201") {
                    showToast("Successfully created canned response, ignoring some duplicates.", 2000);
                    setTimeout(()=>{window.location.reload();}, 2000)
                } else if (response["status_code"] == 101) {
                    upload_button.innerHTML = "Upload";
                    upload_button.style.cursor = "pointer";
                    showToast(response["status_message"], 2000);
                } else if (response["status_code"] == "300") {
                    upload_button.innerHTML = "Upload";
                    upload_button.style.cursor = "pointer";
                    showToast("Canned response with duplicate keyword can't be created!", 2000);
                } else if (response["status_code"] == "301") {
                    upload_button.innerHTML = "Upload";
                    upload_button.style.cursor = "pointer";
                    showToast("Canned response should not contain blacklisted words", 2000);
                } else if (response["status_code"] == "302") {
                    upload_button.innerHTML = "Upload";
                    upload_button.style.cursor = "pointer";
                    document.getElementById("special-character-error-excel").innerHTML =
                        response["status_message"];
                    document.getElementById("error-div-excel").style.display = "block";
                    showToast("Can not add canned response", 5000);
                } else {
                    upload_button.innerHTML = "Upload";
                    upload_button.style.cursor = "pointer";
                    showToast(response.status_message, 2000);
                    setTimeout(()=>{window.location.reload();}, 2000)
                }
            },
            error: function (xhr, textstatus, errorthrown) {
                console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
            },
        });
    }
}

function download_create_canned_response_template() {
    let export_path =
        "/files/templates/livechat-canned-response-create-excel-template" +
        "/Template_createCannedResponse.xlsx";

    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", export_path, false);
    xhttp.send();
    if (xhttp.status == 200) {
        window.open(export_path, "_blank");
    } else {
        alert("Requested data doesn't exists. Kindly try again later.");
    }
}

function select_all_canned_handler(el) {
    const checked = el.checked;
    const all_checkboxes = document.getElementsByClassName("canned-checkbox");

    Array.from(all_checkboxes).forEach((checkbox) => {
        checkbox.checked = checked;
    });

    show_hide_canned_delete_btn(checked);
}

export function reset_canned_response_upload_modal() {
    document.querySelector('#custom-text').innerHTML = 'No file chosen';
    document.getElementById('real-file').value = '';
}

export{
    create_canned_response,
    edit_canned_response,
    delete_canned_agent,
    on_canned_checkbox,
    delete_canned_response,
    submit_canned_response_excel,
    download_create_canned_response_template,
    select_all_canned_handler,
}
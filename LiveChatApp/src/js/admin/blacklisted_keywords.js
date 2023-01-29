// #################################

// Blacklisted keyword

// #################################
import axios from "axios";
import { get_character_limit, upload_excel } from "../common";
import { custom_decrypt, EncryptVariable, getCsrfToken, showToast, validate_keyword } from "../utils";

const state = {
    all_blacklisted_keyword_checked: false,
    response: "",
    added_words: new Set(),
    added_words_lower: new Set(),
    upload_file_limit_size: 1024000,
};

function on_click_blacklisted_checkbox() {
    var blacklisted_list = document.getElementsByClassName("blacklisted-checkbox");
    var flag = 0;
    var selected_intent = 0;
    for (var i = 0; i < blacklisted_list.length; i++) {
        if (document.getElementById(blacklisted_list[i].id).checked) {
            selected_intent = selected_intent + 1;
        }
        else
        {
            flag = 1;
        }
    }
    if(flag == 0)
        document.getElementById("select-all-blacklisted").checked = true
    else
        document.getElementById("select-all-blacklisted").checked = false

    show_hide_delete_btn(selected_intent != 0);
}

function show_hide_delete_btn (show) {
    if (show) {
        document.getElementById("blacklisted-delete-btn").style.display = 'inline-block';
        document.getElementById("blacklisted-add-btn").style.display = 'none';
    } else {
        document.getElementById("blacklisted-delete-btn").style.display = 'none';
        document.getElementById("blacklisted-add-btn").style.display = 'inline-block';
    }
}

function select_all_blacklisted_keyword_handler (el) {
    const checked = el.checked;
    const all_checkboxes = document.getElementsByClassName ('blacklisted-checkbox');
    
    Array.from(all_checkboxes).forEach(checkbox => {
        checkbox.checked = checked;
    })

    show_hide_delete_btn(checked);
}

function add_blacklisted_keyword(blacklist_for) {
    if (state.added_words.size == 0) {
        showToast('Keyword list cannot be empty', 2000);
        return;
    }

    var json_string = JSON.stringify({
        added_words: Array.from(state.added_words),
        blacklist_for: blacklist_for,
    });
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/add-blacklisted-keyword/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token); 
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            
            if (response.status == "200") {
                if (response.all_words_added) {
                    showToast("Keywords added successfully.", 3000);
                } else {
                    showToast("Some Keywords were not added successfully.", 3000);
                }

               setTimeout(()=>{location.reload();}, 2000);
            } else if (response.status == "300") {
                showToast("Keyword already exists.", 3000);
            } else {
                showToast(response.message, 3000);
            }
        }
    };
    xhttp.send(params);
}

function edit_keyword(pk, blacklist_for) {
    let word = document.getElementById("blacklisted-keyword-" + pk).value;
    if (
        word == "" ||
        word.trim().length == 0 ||
        validate_keyword("blacklisted-keyword-" + pk) == false
    ) {
        showToast("Please enter a valid keyword.", 3000);
        return;
    }

    const char_limit = get_character_limit();
    if (word.trim().length > char_limit.small) {
        showToast(`Exceeding character limit of ${char_limit.small} characters`, 2000);
        return;
    }
    
    var json_string = JSON.stringify({
        pk: pk,
        word: word,
        blacklist_for: blacklist_for,
    });
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/edit-blacklisted-keyword/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token); 
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status_code"] == "200") {
                showToast("Changes saved successfully.", 3000);
                setTimeout(()=>{location.reload();}, 2000);
            } else if (response["status_code"] == "300") {
                showToast("Keyword already exists.", 3000);
            } else {
                showToast(response.message, 3000);
            }
        }
    };
    xhttp.send(params);
}

function delete_blacklisted_agent(pk) {
    let blacklisted_keyword_pk_list = [];
    blacklisted_keyword_pk_list.push(pk);
    let json_string = JSON.stringify({
        blacklisted_keyword_pk_list: blacklisted_keyword_pk_list,
    });
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/delete-blacklisted-keyword/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token); 
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            showToast("Removed successfully.", 3000);
            setTimeout(()=>{location.reload();}, 2000);
        }
    };
    xhttp.send(params);
}

function on_modify_blacklisted_select_all_checkbox() {
    var blacklisted_keyword = document.getElementsByClassName("blacklisted-checkbox");

    if (state.all_blacklisted_keyword_checked == true) {
        for (var i = 0; i < blacklisted_keyword.length; i++) {
            document.getElementById(blacklisted_keyword[i].id).checked = false;
        }
        state.all_blacklisted_keyword_checked = false;
    } else {
        for (var i = 0; i < blacklisted_keyword.length; i++) {
            if (document.getElementById(blacklisted_keyword[i].id).disabled) {
            } else {
                document.getElementById(blacklisted_keyword[i].id).checked = true;
            }
        }
        state.all_blacklisted_keyword_checked = true;
    }
    if (state.all_blacklisted_keyword_checked) {
        $("#blacklisted_keyword_delete_div").show();
    } else {
        $("#blacklisted_keyword_delete_div").hide();
    }
}

function remove_selected_blacklisted_keyword() {
    var blacklisted_keyword = document.getElementsByClassName("blacklisted-checkbox");
    var blacklisted_keyword_pk_list = [];

    for (var i = 0; i < blacklisted_keyword.length; i++) {
        if (document.getElementById(blacklisted_keyword[i].id).checked) {
            blacklisted_keyword_pk_list.push(blacklisted_keyword[i].id.split("-")[2]);
        }
    }
    if (blacklisted_keyword_pk_list.length == 0) {
        showToast("Please select at leat one keyword.", 3000);
        return;
    }
    let json_string = JSON.stringify({
        blacklisted_keyword_pk_list: blacklisted_keyword_pk_list,
    });
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/delete-blacklisted-keyword/", true);
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

$(document).on("keyup", "#blacklisted-keyword", (e) => {
    const key = e.which;

    if (key == 13) {
        let word = e.target.value;
        word = word.trim();

        if (word === '' || !validate_keyword('blacklisted-keyword')) {
            showToast('Please enter a valid keyword', 2000);
            return;
        }

        if (state.added_words_lower.has(word.toLowerCase()) || WORDS_PRESENT.join('-').toLowerCase().split('-').includes(word.toLowerCase())) {
            showToast('Keyword already present', 2000);
            return;
        }

        state.added_words.add(word);
        state.added_words_lower.add(word.toLowerCase());

        const word_html = `
                            <div class="keyword-tag" id="${word}">
								<p>${word}</p>
								<span class="delete-keyword-tag click-remove-keyword-tag" id="delete-${word}">
								    <svg width="12" height="13" viewBox="0 0 12 13" fill="none" xmlns="http://www.w3.org/2000/svg">
									    <path d="M2.3938 2.27954L9.60619 9.77954" stroke="#CBCACA" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"/>
									    <path d="M9.6062 2.27954L2.39381 9.77954" stroke="#CBCACA" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"/>
								    </svg>
							    </span>
							</div>
        `;

        $('#added_blacklisted_keyword_tags').append(word_html);
        e.target.value = '';

        setTimeout(() => {
            $(`#delete-${word}`).on('click', (e) => {
                console.log(e.currentTarget);
                const id = e.currentTarget.id.split('-')[1];

                document.getElementById(id).remove();
                state.added_words.delete(id);
                state.added_words_lower.delete(id.toLowerCase());
            })
        }, 300);
    }
});

export function download_create_blacklisted_keyword_template() {
    let export_path =
        "/files/templates/livechat-blacklisted-keywords-template" +
        "/Blacklisted_Keywords_Template.xlsx";

    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", export_path, false);
    xhttp.send();
    if (xhttp.status == 200) {
        window.open(export_path, "_blank");
    } else {
        alert("Requested data doesn't exists. Kindly try again later.");
    }
}

export function submit_blacklisted_keywords_excel(blacklist_for) {
    const blacklisted_keywords_file = $("#real-file")[0].files[0];
    
    if (blacklisted_keywords_file == undefined || blacklisted_keywords_file == null) {
        showToast("Please provide excel sheet in required format.", 2000);
        return;
    }
    if (
        blacklisted_keywords_file.name.split(".").pop() != "xlsx" &&
        blacklisted_keywords_file.name.split(".").pop() != "xls"
    ) {
        showToast("Please upload file in correct format.", 2000);
        return;
    }
    if (blacklisted_keywords_file.size > state.upload_file_limit_size) {
        showToast("Size limit exceed(should be less than 1 MB)", 2000);
        return;
    }

    var reader = new FileReader();
    reader.readAsDataURL(blacklisted_keywords_file);
    reader.onload = function() {

        var base64_str = reader.result.split(",")[1];

        var uploaded_file = [];
        uploaded_file.push({
            "filename": blacklisted_keywords_file.name,
            "base64_file": base64_str,
        });

        upload_blacklisted_keywords_excel(uploaded_file, blacklist_for);
    };

    reader.onerror = function(error) {
        console.log('Error: ', error);
    };
}

async function upload_blacklisted_keywords_excel(uploaded_file, blacklist_for){
    const response = await upload_excel(uploaded_file);
    
    if (response && response.status == 200) {
        const upload_button = document.getElementById("submit_blacklisted_keywords_excel");
        upload_button.innerHTML = "Creating..";
        upload_button.style.cursor = "not-allowed";
        upload_button.style.pointerEvents = 'none';

        var formData = new FormData();
        var src = window.location.origin + response["src"]
        formData.append("src", response["src"]);
        formData.append("blacklist_for", blacklist_for);
        
        const config = {
            headers: {
              'X-CSRFToken': getCsrfToken(),
            }
        }

        axios
            .post("/livechat/create-blacklisted-keyword-excel/", formData, config)
            .then (response => {
                response = custom_decrypt(response.data)
                response = JSON.parse(response)

                if (response.status == 200) {
                    if (response.all_words_created) {
                        showToast('Keywords created successfully', 2000);
                    } else {
                        showToast('Some keywords were not created successfully', 2000);
                    }

                    setTimeout(() => {
                        window.location.reload();
                    }, 2000);
                } else {
                    showToast(response.message, 2000);
                }

                upload_button.innerHTML = "Upload";
                upload_button.style.cursor = "cursor";
                upload_button.style.pointerEvents = 'auto';
            })
    }
}

export function reset_blacklisted_keyword_upload_modal() {
    document.querySelector('#custom-text').innerHTML = 'No file chosen';
    document.getElementById('real-file').value = '';
}

$(document).ready(function(){
    $('#modal-add-blacklisted-keyword .modal-footer .btn-close').on('click', function () {
        $('#blacklisted-keyword').val("");
        $('#blacklisted-keyword-char-count').html('0')
      });
});

export {
    add_blacklisted_keyword,
    edit_keyword,
    delete_blacklisted_agent,
    remove_selected_blacklisted_keyword,
    on_click_blacklisted_checkbox,
    select_all_blacklisted_keyword_handler,
};

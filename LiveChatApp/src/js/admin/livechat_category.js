// *****************************************  LiveChat Category  ****************************************************
import { get_character_limit } from "../common";
import { custom_decrypt, EncryptVariable, showToast, validate_category_title, getCsrfToken } from "../utils";

const state = {
    all_category_checked: false,
};

function modify_category_select_all_checkbox() {
    var category_list = document.getElementsByClassName("category-checkbox");

    if (state.all_category_checked == true) {
        for (var i = 0; i < category_list.length; i++) {
            document.getElementById(category_list[i].id).checked = false;
        }
        state.all_category_checked = false;
    } else {
        for (var i = 0; i < category_list.length; i++) {
            if (document.getElementById(category_list[i].id).disabled) {
            } else {
                document.getElementById(category_list[i].id).checked = true;
            }
        }
        state.all_category_checked = true;
    }
    if (state.all_category_checked) {
        $("#category_deletion_div").show();
    } else {
        $("#category_deletion_div").hide();
    }
}

function category_checkbox_click() {
    var category_list = document.getElementsByClassName("category-checkbox");
    var selected_intent = 0;
    var flag = 0;
    for (var i = 0; i < category_list.length; i++) {
        if (document.getElementById(category_list[i].id).checked) {
            selected_intent = selected_intent + 1;
        }
        else
            {flag = 1;}
    }
    if(flag == 0)
        document.getElementById("select-all-category").checked = true
    else
        document.getElementById("select-all-category").checked = false


    show_hide_delete_btn(selected_intent != 0);
}

function show_hide_delete_btn (show) {
    if (show) {
        document.getElementById("category-delete-btn").style.display = 'inline-block';
        document.getElementById("category-add-btn").style.display = 'none';
    } else {
        document.getElementById("category-delete-btn").style.display = 'none';
        document.getElementById("category-add-btn").style.display = 'inline-block';
    }
}

function select_all_category_handler (el) {
    const checked = el.checked;
    const all_checkboxes = document.getElementsByClassName ('category-checkbox');
    
    Array.from(all_checkboxes).forEach(checkbox => {
        checkbox.checked = checked;
    })

    show_hide_delete_btn(checked);
}

function edit_livechat_category(category_pk) {
    let title = document.getElementById("category-title-" + category_pk).value;
    let priority = document.getElementById("category-priority-" + category_pk).value;
    if (
        title == "" ||
        title.trim().length == 0 ||
        validate_category_title("category-title-" + category_pk) == false
    ) {
        showToast("Please enter a valid category name.", 2000);
        return;
    }

    const char_limit = get_character_limit();
    if (title.length > char_limit.small) {
        showToast(`Exceeding character limit of ${char_limit.small} characters`, 2000)
        return;
    }

    let bot_pk = document.getElementById("category-bot-" + category_pk).value;
    let is_public = document.getElementById("category-type-public-" + category_pk).checked;
    var json_string = JSON.stringify({
        title: title,
        priority: priority,
        category_pk: category_pk,
        bot_id: bot_pk,
        is_public: is_public,
    });
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/edit-livechat-category/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status_code"] == "200") {
                showToast("Category saved successfully!", 3000);
                setTimeout(function() {location.reload();}, 2000);
            } else if (response["status_code"] == "300") {
                showToast("Category name exists, can't be created!", 5000);
            } else {
                showToast("Category can't be created, due to some internal error!", 5000);
            }
        }
    };
    xhttp.send(params);
}

function create_livechat_category() {
    let title = document.getElementById("category-title").value;
    let priority = document.getElementById("category-priority").value;
    let bot = document.getElementById("category-bot").value;

    const char_limit = get_character_limit();
    if (
        title == "" ||
        title.trim().length == 0 ||
        validate_category_title("category-title") == false
    ) {
        showToast("Please enter a valid category name.", 5000);
        return;
    }

    if (title.length > char_limit.small) {
        showToast(`Exceeding character limit of ${char_limit.small} characters`, 2000)
        return;
    }

    let is_public = document.getElementById("category-type-public").checked;

    var json_string = JSON.stringify({
        title: title,
        priority: priority,
        bot_id: bot,
        is_public: is_public,
    });

    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/create-new-category/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status_code"] == "200") {
                showToast("New category created successfully!", 3000);
                setTimeout(function() {location.reload();}, 2000);
            } else if (response["status_code"] == "300") {
                showToast("Category name exists, can't be created!", 5000);
            } else {
                showToast(response.status_message, 5000);
            }
        }
    };
    xhttp.send(params);
}

function delete_livechat_category(category_pk) {
    var category_pk_list = [];
    if (category_pk == "None") {
        var category_list = document.getElementsByClassName("category-checkbox");

        for (var i = 0; i < category_list.length; i++) {
            if (document.getElementById(category_list[i].id).checked) {
                category_pk_list.push(category_list[i].id.split("-")[2]);
            }
        }
    } else {
        category_pk_list.push(category_pk);
    }

    if (category_pk_list.length == 0) {
        showToast("Please select at leat one Category.", 3000);
        return;
    }
    let json_string = JSON.stringify({
        category_pk_list: category_pk_list,
    });
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/delete-livechat-category/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status_code"] == "200") {
                showToast("Deleted successfully!", 5000);
                setTimeout(function() {location.reload();}, 2000);
            } else {
                showToast("Can't delete due to some internal error.", 5000);
            }
        }
    };
    xhttp.send(params);
}

function select_public_category_type(category_pk) {
    let private_radio_button = "";
    let priority_div = "";
    if (category_pk == null) {
        private_radio_button = document.getElementById("category-type-private");
        priority_div = document.getElementById("add-new-category-priority-div");
    } else {
        private_radio_button = document.getElementById("category-type-private-" + category_pk);
        priority_div = document.getElementById("add-new-category-priority-div-edit-" + category_pk);
    }

    private_radio_button.checked = false;

    priority_div.style.display = "block";
}

function select_private_category_type(category_pk) {
    let public_radio_button = "";
    let priority_div = "";
    if (category_pk == null) {
        public_radio_button = document.getElementById("category-type-public");
        priority_div = document.getElementById("add-new-category-priority-div");
    } else {
        public_radio_button = document.getElementById("category-type-public-" + category_pk);
        priority_div = document.getElementById("add-new-category-priority-div-edit-" + category_pk);
    }

    public_radio_button.checked = false;
    priority_div.style.display = "none";
}

export {
    modify_category_select_all_checkbox,
    category_checkbox_click,
    edit_livechat_category,
    create_livechat_category,
    delete_livechat_category,
    select_public_category_type,
    select_private_category_type,
    select_all_category_handler,
};

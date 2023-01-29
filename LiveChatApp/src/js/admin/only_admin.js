import {
    custom_decrypt,
    EncryptVariable,
    getCsrfToken,
    showToast,
    validate_name,
    validate_phone_number,
    validate_email,
} from "../utils";

(function ($) {
    $(function () {
        $(".dropdown-trigger").dropdown({
            constrainWidth: false,
            alignment: "left",
        });

        $(".tooltipped").tooltip({
            position: "top",
        });

        $(".readable-pro-tooltipped").tooltip({
            position: "top",
        });

        $(".tooltipped").tooltip();
        $(".tooltipped").tooltip({
            position: "top",
        });
        if (screen.width < 680) {
            $("#web-switch").hide();
            $("#mobile-switch").show();
        }
    }); // end of document ready
})(jQuery); // end of jQuery name space
/////////////////////////////////   LiveChat Only Admin management ////////////////////////////////////

const state = {
    upload_file_limit_size: 1024000,
};

function create_only_admin() {
    let name = document.getElementById("edit-only-admin-full-name").value;
    if (name == "" || validate_name("edit-only-admin-full-name") == false) {
        showToast("Please enter valid name.", 2000);
        return;
    }

    let phone_number = document.getElementById("edit-only-admin-phone").value;
    if (
        phone_number == "" ||
        validate_phone_number("edit-only-admin-phone") == false ||
        phone_number.length != 10
    ) {
        showToast("Please enter valid phone number.", 2000);
        return;
    }
    let email = document.getElementById("edit-only-admin-email").value;
    if (email == "" || validate_email("edit-only-admin-email") == false) {
        showToast("Please enter valid email.", 2000);
        return;
    }

    let json_string = JSON.stringify({
        name: name,
        phone_number: phone_number,
        email: email,
    });
    json_string = EncryptVariable(json_string);

    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
        url: "/livechat/create-livechat-only-admin/",
        type: "POST",
        headers: {
            "X-CSRFToken": CSRF_TOKEN
        },
        data: {
            json_string: json_string,
        },
        success: function (response) {
            var response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status_code"] == "200") {
                showToast("New only LiveChat admin created succesfully", 2000);
                window.location.reload();
            } else if (response["status_code"] == "300") {
                showToast("Username already exists.", 2000);
            } else {
                showToast(
                    "Unable to create new livechat only admin due to some technical issue. Kindly report the same",
                    2000
                );
            }
        },
        error: function (xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        },
    });
}

function edit_livechat_only_admin_info(current_livechat_only_admin_pk) {
    let name = document.getElementById(
        "edit-only-admin-full-name-" + current_livechat_only_admin_pk
    ).value;
    if (
        name == "" ||
        validate_name("edit-only-admin-full-name-" + current_livechat_only_admin_pk) == false
    ) {
        showToast("Please enter valid name.", 2000);
        return;
    }

    let phone_number = document.getElementById(
        "edit-only-admin-phone-" + current_livechat_only_admin_pk
    ).value;
    if (
        phone_number == "" ||
        validate_phone_number("edit-only-admin-phone-" + current_livechat_only_admin_pk) == false ||
        phone_number.length != 10
    ) {
        showToast("Please enter valid phone number.", 2000);
        return;
    }
    let email = document.getElementById(
        "edit-only-admin-email-" + current_livechat_only_admin_pk
    ).value;
    if (
        email == "" ||
        validate_email("edit-only-admin-email-" + current_livechat_only_admin_pk) == false
    ) {
        showToast("Please enter valid email.", 2000);
        return;
    }

    let json_string = JSON.stringify({
        name: name,
        phone_number: phone_number,
        email: email,
        current_livechat_only_admin_pk: current_livechat_only_admin_pk,
    });
    json_string = EncryptVariable(json_string);

    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
        url: "/livechat/edit-livechat-only-admin/",
        type: "POST",
        headers: {
            "X-CSRFToken": CSRF_TOKEN
        },
        data: {
            json_string: json_string,
        },
        success: function (response) {
            var response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status_code"] == "200") {
                showToast("Changes saved Succesfully", 2000);
                window.location.reload();
            } else if (response["status_code"] == "300") {
                showToast("Username already exists.", 2000);
            } else {
                showToast(
                    "Unable to save changes due to some technical issue. Kindly report the same",
                    2000
                );
            }
        },
        error: function (xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        },
    });
}
function delete_livechat_only_admin(current_livechat_only_admin_pk) {
    let json_string = JSON.stringify({
        current_livechat_only_admin_pk: current_livechat_only_admin_pk,
    });
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: "/livechat/delete-livechat-only-admin/",
        type: "POST",
        data: {
            json_string: json_string,
        },
        success: function (response) {
            var response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status_code"] == "200") {
                showToast("Deleted Succesfully", 2000);
                window.location.reload();
            } else if (response["status_code"] == "300") {
                showToast(response["status_message"], 2000);
                window.location.reload();
            } else {
                showToast(
                    "Unable to delete due to some technical issue. Kindly report the same",
                    2000
                );
            }
        },
        error: function (xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        },
    });
}

function download_create_livechat_only_admin_template() {
    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
        url: "/livechat/download-create-livechat-only-admin-template/",
        type: "POST",
        headers: {
            "X-CSRFToken": CSRF_TOKEN
        },
        success: function (response) {
            var response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status"] == "200") {
                if (response["export_path"] == null) {
                    alert("Sorry, unable to process your request. Kindly try again later.");
                } else {
                    if (response["export_path_exist"]) {
                        window.open(response["export_path"], "_blank");
                    } else {
                        alert("Requested data doesn't exists. Kindly try again later.");
                    }
                }
            }
        },
        error: function (xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        },
    });
}

function submit_livechat_only_admin_excel() {
    var upload_button = document.getElementById("submit-livechat-only-admin-excel");
    var livechat_only_admin_file = $("#real-file")[0].files[0];
    if (livechat_only_admin_file == undefined || livechat_only_admin_file == null) {
        showToast("Please provide excel sheet in required format.", 2000);
        return;
    }
    if (
        livechat_only_admin_file.name.split(".").pop() != "xlsx" &&
        livechat_only_admin_file.name.split(".").pop() != "xls"
    ) {
        showToast("Please upload file in correct format.", 2000);
        return;
    }
    if (livechat_only_admin_file.size > state.upload_file_limit_size) {
        showToast("Size limit exceed(should be less than 1 MB)", 2000);
        return;
    }
    upload_button.innerHTML = "Creating..";
    upload_button.style.cursor = "not-allowed";

    var CSRF_TOKEN = getCsrfToken();
    var formData = new FormData();
    formData.append("livechat_only_admin_file", livechat_only_admin_file);
    $.ajax({
        url: "/livechat/submit-livechat-only-admin-excel/",
        type: "POST",
        headers: {
            "X-CSRFToken": CSRF_TOKEN
        },
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
            var response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status_code"] == "200") {
                showToast("Successfully created livechat only admin(s).", 2000);
                window.location.reload();
            } else if (response["status_code"] == "101") {
                upload_button.innerHTML = "Upload";
                upload_button.style.cursor = "pointer";
                showToast(response["status_message"], 2000);
            } else {
                upload_button.innerHTML = "Upload";
                upload_button.style.cursor = "pointer";
                showToast(
                    "Unable to create LiveChat only admin due to some technical issue.",
                    2000
                );
            }
        },
        error: function (xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        },
    });
}

export {
    create_only_admin,
    edit_livechat_only_admin_info,
    delete_livechat_only_admin,
    download_create_livechat_only_admin_template,
    submit_livechat_only_admin_excel,
};

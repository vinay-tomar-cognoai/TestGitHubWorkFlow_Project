const UPLOAD_FILE_SIZE_LIMIT = 1024000;
let is_admin_filter_applied = false;
let is_supervisor_filter_applied = false;
const canned_response_regex = /^[a-zA-Z @.?!,0-9]+$/;
const canned_keyword_regex = /^[a-z0-9]+$/;


function create_canned_response() {
    let error_element = document.getElementById("error-message")
    error_element.innerHTML = "";
    error_element.classList.remove('d-none')
    let keyword = document.getElementById("add-canned-keyword").value.trim();
    let canned_response = document.getElementById("add-canned-response").value.trim();

    if (document.getElementById("add-canned-keyword").value.indexOf(' ') >= 0) {
        error_element.innerHTML = "Keyword shouldn’t contain space between words";
        return;
    }

    if (!canned_response.length && !keyword.length) {
        error_element.innerHTML = "Please add input values to continue";
        return;
    }

    if (!keyword.length) {
        error_element.innerHTML = "Please add a keyword to continue";
        return;
    }

    if (!validate_canned_keyword(keyword)) {
        error_element.innerHTML = "Please enter valid keyword (Only a-z 0-9 characters are allowed)";
        return;
    }

    if (!canned_response.length) {
        error_element.innerHTML = "Please add a response to continue";
        return;
    }

    if (!validate_canned_response(canned_response)) {
        error_element.innerHTML = "Please enter a valid response (Only a-z A-Z @ . ? ! , 0-9 characters are allowed)";
        return;
    }

    if (canned_response.length > 500) {
        error_element.innerHTML = "Response shouldn’t be more than 500 characters long";
        return;
    }

    if (keyword.length > 25) {
        error_element.innerHTML = "Keyword shouldn’t be more than 25 characters long";
        return;
    }

    let json_string = JSON.stringify({
        "keyword": remove_special_characters_from_str(stripHTML(keyword)),
        "response": remove_special_characters_from_str(stripHTML(canned_response)),
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/create-new-canned-response/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status_code"] == 200) {
                $("#modal-add-canned-response").modal("hide");
                easyassist_show_long_toast("Canned response added successfully", 2000);
                setTimeout(function () {
                    window.location.reload(true);
                }, 2000);
            } else if (response["status_code"] == 300) {
                error_element.innerHTML = "Keyword already exists, please try a different one";
            } else if (response["status_code"] == 301) {
                error_element.innerHTML = "Canned response should not contain blacklisted words";
            } else if (response["status_code"] == 302 || response["status_code"] == 400) {
                error_element.innerHTML = response["status_message"];
            } else {
                error_element.innerHTML = "Internal server error while creating canned response";
            }
        }
    };
    xhttp.send(params);
}

function edit_canned_response(canned_response_pk) {

    let error_element = document.getElementById("error-message-edit");
    error_element.innerHTML = "";
    error_element.classList.remove('d-none')

    let keyword = document.getElementById("edit-canned-keyword").value;
    let canned_response = document.getElementById("edit-canned-response").value.trim();

    if (document.getElementById("edit-canned-keyword").value.indexOf(' ') >= 0) {
        error_element.innerHTML = "Keyword shouldn’t contain space between words";
        return;
    }

    if (!canned_response.length && !keyword.length) {
        error_element.innerHTML = "Please add input values to continue";
        return;
    }

    if (!keyword.length) {
        error_element.innerHTML = "Please add a keyword to continue";
        return;
    }

    if (!validate_canned_keyword(keyword)) {
        error_element.innerHTML = "Please enter valid keyword (Only a-z 0-9 characters are allowed)";
        return;
    }

    if (!canned_response.length) {
        error_element.innerHTML = "Please add a response to continue";
        return;
    }

    if (!validate_canned_response(canned_response)) {
        error_element.innerHTML = "Please enter a valid response (Only a-z A-Z @ . ? ! , 0-9 characters are allowed)";
        return;
    }

    if (canned_response.length > 500) {
        error_element.innerHTML = "Response shouldn’t be more than 500 characters long";
        return;
    }

    if (keyword.length > 25) {
        error_element.innerHTML = "Keyword shouldn’t be more than 25 characters long";
        return;
    }

    let json_string = JSON.stringify({
        "keyword": remove_special_characters_from_str(stripHTML(keyword)),
        "response": remove_special_characters_from_str(stripHTML(canned_response)),
        "canned_response_pk": stripHTML(canned_response_pk),
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/edit-canned-response/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status_code"] == 200) {
                $("#modal-edit-canned-response").modal("hide");
                easyassist_show_long_toast("Canned response updated successfully", 2000);
                setTimeout(function () {
                    window.location.reload(true);
                }, 2000);
            } else if (response["status_code"] == 300) {
                error_element.innerHTML = response["status_message"];
            } else if (response["status_code"] == 302) {
                error_element.innerHTML = response["status_message"];
            } else {
                error_element.innerHTML = response["status_message"];
            }
        }
    };
    xhttp.send(params);
}

function delete_canned_response(canned_response_pk) {

    let error_element = document.getElementById("error-message-delete");
    error_element.innerHTML = "";

    window.localStorage.setItem("canned_response_page", '1');

    let canned_response_pk_list = [];
    canned_response_pk_list.push(canned_response_pk);

    let json_string = JSON.stringify({
        canned_response_pk_list: canned_response_pk_list,
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/delete-canned-response/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status_code"] == 200) {
                $("#modal-delete-canned-response").modal("hide");
                easyassist_show_long_toast("Canned response deleted successfully", 2000);
                setTimeout(function () {
                    window.location.reload(true);
                }, 2000);
            } else {
                error_element.innerHTML = "Server error";
                error_element.classList.remove('d-none')
            }
        }
    };
    xhttp.send(params);
}

function submit_canned_response_excel() {

    let canned_response_file = $("#canned-response-batch-file-upload")[0].files[0];
    if (canned_response_file == undefined || canned_response_file == null) {
        easyassist_show_long_toast("Please provide excel sheet in required format", 2000);
        file_upload.value = null;
        return;
    }
    if (canned_response_file.name.split(".").pop() != "xlsx" && canned_response_file.name.split(".").pop() != "xls") {
        easyassist_show_long_toast("Please upload file in correct format", 2000);
        file_upload.value = null;
        return;
    }
    if (canned_response_file.size > UPLOAD_FILE_SIZE_LIMIT) {
        easyassist_show_long_toast("Size limit exceed(should be less than 1 MB)", 2000);
        return;
    }

    let malicious_file_report = check_malicious_file(canned_response_file.name)
    if (malicious_file_report.status) {
        easyassist_show_long_toast(malicious_file_report.message, 2000);
        file_upload.value = null;
        return false
    }

    let reader = new FileReader();
    reader.readAsDataURL(canned_response_file);
    reader.onload = function () {

        let base64_str = reader.result.split(",")[1];

        let uploaded_file = {
            "filename": canned_response_file.name,
            "base64_file": base64_str,
        };

        upload_canned_response_excel(uploaded_file);
    };

    reader.onerror = function (error) {
        console.log('Error: ', error);
        file_upload.value = null;
    };
}

async function upload_excel(uploaded_file) {
    return new Promise(function (resolve, reject) {
        let json_string = JSON.stringify(uploaded_file)
        let encrypted_data = easyassist_custom_encrypt(json_string);

        let error_element = document.getElementById("uploaded_file_errors")
        error_element.innerHTML = ""

        encrypted_data = {
            "Request": encrypted_data
        };

        const params = JSON.stringify(encrypted_data);

        let xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/easy-assist/upload-excel/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function () {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response)
            response = JSON.parse(response);
            if (this.readyState == 4) {
                if (response.status == 200) {
                    resolve(response);
                } else if (response.status == 300) {
                    error_element.innerHTML = "Invalid file format";
                    file_upload.value = null;
                } else {
                    error_element.innerHTML = "Internal Server Error. Please try again later.";
                }
            }
        }

        xhttp.send(params);
    })
}

async function upload_canned_response_excel(uploaded_file) {
    let response = await upload_excel(uploaded_file);
    if (response && response.status == 200) {
        let upload_button = document.getElementById("submit_canned_response_excel");
        let error_element = document.getElementById("uploaded_file_errors")
        error_element.innerHTML = "";
        let feedback_element = document.getElementById("feedback-sheet-download-button-div");
        feedback_element.innerHTML = "";
        let json_string = JSON.stringify({
            "src": response["src"],
        });

        let encrypted_data = easyassist_custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        upload_button.innerHTML = "Creating..";
        const params = JSON.stringify(encrypted_data);
        let xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/easy-assist/create-new-canned-response-excel/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function () {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response)
            response = JSON.parse(response);
            if (this.readyState == 4) {
                if (response["status_code"] == 200) {
                    $("#modal-add-canned-response-excel").modal("hide");
                    easyassist_show_long_toast("Canned response added successfully", 2000);
                    setTimeout(function () {
                        window.location.reload(true);
                    }, 2000);
                } else if (response["status_code"] == 401) {
                    error_element.innerHTML = response.status_message;
                    file_upload.value = null;
                } else if (response["status_code"] == 407 ) {
                    error_element.innerHTML = response.status_message;
                    file_upload.value = null;
                } else if (response["status_code"] == 400) {
                    error_element.innerHTML = response.status_message;
                    file_upload.value = null;
                    let html_error_file = [
                        '<button class="btn" id="feedback-sheet-download-button">',
                        '<svg width="14" height="18" viewBox="0 0 14 18" fill="none" xmlns="http://www.w3.org/2000/svg">',
                        '<path d="M1 16H13C13.5523 16 14 16.4477 14 17C14 17.5063 13.6238 17.9247 13.1357 17.9909L13 18H1C0.447715 18 0 17.5523 0 17C0 16.4937 0.376205 16.0753 0.864306 16.0091L1 16H13H1ZM6.86431 0.00912889L7 0C7.50626 0 7.92465 0.376205 7.99087 0.864306L8 1V11.2507L11.0069 8.24551C11.362 7.89049 11.9175 7.85822 12.309 8.14869L12.4212 8.24551C12.7762 8.60054 12.8084 9.15609 12.518 9.54757L12.4212 9.65973L7.70711 14.3738C7.35208 14.7288 6.79653 14.7611 6.40505 14.4706L6.29289 14.3738L1.57885 9.65973C1.18832 9.2692 1.18832 8.63604 1.57885 8.24551C1.93387 7.89049 2.48942 7.85822 2.8809 8.14869L2.99306 8.24551L6 11.2533V1C6 0.493739 6.37621 0.0753454 6.86431 0.00912889L7 0L6.86431 0.00912889Z" fill="white"/>',
                        '</svg>',
                        '<a href="/' + response["file_path"] + '" style="text-decoration:none; color:#FFFFFF !important; "> Download feedback sheet </a>',
                        '</button>',
                    ].join('');
                    feedback_element.innerHTML = html_error_file;
                } else {
                    error_element.innerHTML = "Internal error while creating canned response";
                }
            }
        }
        upload_button.innerHTML = "Upload";
        xhttp.send(params);
    }
}

function download_create_canned_response_template() {
    let export_path = window.TEMPLATE_PATH;

    let xhttp = new XMLHttpRequest();
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

function reset_canned_response_upload_modal() {
    document.querySelector('#custom-text').innerHTML = 'No file chosen';
    document.getElementById('real-file').value = '';
}

function validate_canned_response(value) {
    if (canned_response_regex.test(value)) {
        return true;
    } else {
        return false;
    }
}

function validate_canned_keyword(value) {
    if (canned_keyword_regex.test(value)) {
        return true;
    } else {
        return false;
    }
}

function delete_canned_responses() {

    let error_element = document.getElementById("error-message");
    error_element.innerHTML = "";
    error_element.classList.remove('d-none')

    let canned_list = document.getElementsByClassName("canned-checkbox");
    let canned_response_pk_list = [];

    window.localStorage.setItem("canned_response_page", '1');

    for (let i = 0; i < canned_list.length; i++) {
        if (document.getElementById(canned_list[i].id).checked) {
            canned_response_pk_list.push(canned_list[i].id.split("-")[3]);
        }
    }
    if (canned_response_pk_list.length == 0) {
        easyassist_show_long_toast("Please select at least one canned response", 3000);
        return;
    }

    let json_string = JSON.stringify({
        "canned_response_pk_list": canned_response_pk_list,
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/delete-canned-response/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status_code"] == 200) {
                $("#multi-delete-canned-response").modal("hide");
                easyassist_show_long_toast("Canned responses deleted successfully", 2000);
                setTimeout(function () {
                    window.location.reload(true);
                }, 2000);
            } else if (response["status_code"] == 407) {
                easyassist_show_long_toast(response["status_message"], 2000);
                $("#multi-delete-canned-response").modal("hide");
            } else {
                error_element.innerHTML = "Server error";
            }
        }
    };
    xhttp.send(params);
}

function export_canned_responses(el) {

    let export_div_element = document.getElementById("export-canned-response");
    export_div_element.innerHTML = "Exporting...";

    const params = ""
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/sales-ai/export-canned-responses/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {

        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);

            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if (response.status == 200 && response["export_path"] != null) {
                let export_path = response["export_path"];
                window.location = window.location.protocol + "//" + window.location.host + "/" + export_path;
            } else if (response.status == 300) {
                easyassist_show_long_toast("Your request has been recorded. You will get the Email in next 24 hrs.", 3000);

            } else {
                show_easyassist_toast("Unable to download canned responses");
            }
            export_div_element.innerHTML = "Export";
            el.disabled = false;
        }
    }
    xhttp.send(params);
}

function apply_canned_response_filter(element) {
    let values = [];
    if (window.AGENT_ROLE == "admin") {
        if (document.getElementById("supervisor-input").checked) {
            const selected = document.querySelectorAll('#select-agent-username-dropdown option:checked');
            is_supervisor_filter_applied = true;
            values = Array.from(selected).map(el => el.value);
        } else if (document.getElementById("admin-input").checked) {
            is_admin_filter_applied = true;
            values = [document.getElementById("admin-input").value];
        }
    } else if (window.AGENT_ROLE == "agent") {
        if (document.getElementById("supervisor-input").checked) {
            const selected = document.querySelectorAll('#select-agent-username-dropdown option:checked');
            is_supervisor_filter_applied = true;
            values = Array.from(selected).map(el => el.value);
        } else if (document.getElementById("admin-input").checked) {
            is_admin_filter_applied = true;
            values = [document.getElementById("admin-input").value];
        }
    } else {
        if (document.getElementById("supervisor-input").checked) {
            is_supervisor_filter_applied = true;
            values = [document.getElementById("supervisor-input").value];
        } else if (document.getElementById("admin-input").checked) {
            values = [document.getElementById("admin-input").value];
            is_admin_filter_applied = true;
        }
    }

    window.localStorage.setItem("is_admin_filter_applied", is_admin_filter_applied);
    window.localStorage.setItem("is_supervisor_filter_applied", is_supervisor_filter_applied);

    if (!values.length) {
        easyassist_show_long_toast("Please select any filter and then apply", 2000);
        return;
    } else {
        $("#modal-filter-canned-response").modal("hide");
    }

    document.getElementById("filter-button-text").innerHTML = "Edit Filters";
    window.localStorage.setItem("selected_supervisors", JSON.stringify(values));

    get_all_canned_response()
}

function clear_canned_response_filter() {
    let selected_supervisors = window.localStorage.getItem("selected_supervisors");

    if (selected_supervisors || is_admin_filter_applied || is_supervisor_filter_applied) {
        easyassist_show_long_toast("Filters have been reset", 2000);
        is_admin_filter_applied = false;
        is_supervisor_filter_applied = false;
        window.localStorage.removeItem("is_admin_filter_applied");
        window.localStorage.removeItem("is_supervisor_filter_applied");
        $("#modal-filter-canned-response").modal("hide");
        window.localStorage.removeItem("selected_supervisors");
        get_all_canned_response();
        $(".admin-user").click();
        $("#select-agent-username-dropdown").val('');
        $("#select-agent-username-dropdown").multiselect("refresh");
        document.getElementById("supervisor-input").checked = false;
        document.getElementById("admin-input").checked = false;
        document.getElementById("filter-button-text").innerHTML = "Filter";
    } else {
        easyassist_show_long_toast("Please apply atleast one filter to reset", 2000);
    }
}

function set_keyword_character_count(el) {
    const count = el.value.length;
    const have_space = el.value.indexOf(' ');
    document.getElementById("count").innerHTML = count;
    let error_element = document.getElementById('error-message-edit');
    error_element.textContent = '';
    if (have_space >= 0) {
        error_element.classList.remove('d-none');
        error_element.textContent = `Keyword shouldn’t contain space between words`;
    } else {
        if (!error_element.classList.contains("d-none"))
            error_element.classList.add('d-none');
    }
}

function set_response_character_count(el) {
    const count = el.value.length;
    document.getElementById("response-count").innerHTML = count;
}

function get_all_canned_response() {
    let request_params = {};

    let page_number = parseInt(window.localStorage.getItem("canned_response_page"));
    if (!page_number) {
        page_number = 1;
    }

    let selected_supervisors = window.localStorage.getItem("selected_supervisors");
    selected_supervisors = JSON.parse(selected_supervisors);
    let searched_keyword = window.localStorage.getItem("searched_keyword");

    if (selected_supervisors && searched_keyword) {
        request_params["selected_supervisors"] = selected_supervisors;
        request_params["searched_keyword"] = stripHTML(searched_keyword);
    } else if (selected_supervisors) {
        request_params["selected_supervisors"] = selected_supervisors;
    } else if (searched_keyword) {
        request_params["searched_keyword"] = stripHTML(searched_keyword);
    }

    request_params["page_number"] = page_number;

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);

    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/get-all-canned-responses/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status_code"] == 200) {
                let canned_response_list = response.canned_response_list
                let canned_response_list_html = ""

                $('#canned-responses-table').dataTable().fnClearTable();
                $('#canned-responses-table').DataTable().destroy();

                if (canned_response_list) {

                    for (let idx = 0; idx < canned_response_list.length; idx++) {
                        let canned_response_data = canned_response_list[idx];
                        canned_response_list_html += create_canned_response_card(canned_response_data);
                    }


                }

                if (document.getElementById("canned-responses-table")) {
                    document.getElementById("canned-responses-table-body").innerHTML = canned_response_list_html;
                    if (canned_response_list.length) {
                        document.getElementById("canned-table-pagination-div").innerHTML = "";
                        add_pagination(response.pagination_data, response.start, response.end, response.total_canned_responses);
                    } else {
                        document.getElementById("canned-table-pagination-div").innerHTML = "";
                    }
                }

                let canned_table = $('#canned-responses-table').DataTable({
                    "bLengthChange": true,
                    paging: false,
                    "bFilter": true,
                    "bAutoWidth": true,
                    "ordering": false,
                    info: false,
                    "bSort": false,
                    "oLanguage": {
                        "sEmptyTable": "    "
                    }
                });

                $("#custom-table-search").keyup(function () {
                    if ($(this).val() != false) {
                        $('.search-bar-button').addClass('active-search')
                    } else {
                        $('.search-bar-button').removeClass('active-search')
                    }
                });

                if (!canned_table.data().any()) {
                    $('#canned_responses_table_info').hide();
                    $('#canned_responses_table_paginate').hide();
                    $("#checkbox-label").hide();
                    $('#export-canned-responses').addClass('disable_export');
                } else {
                    $('#export-canned-responses').removeClass('disable_export');
                    $("#checkbox-label").show();
                }

                $('#select-all-canned').click(function (e) {
                    select_all_canned_handler(e.target)
                })

                $('.canned-checkbox').click(function (e) {
                    select_canned_handler(e.target)
                })

                if (document.getElementById("select-all-canned")) {
                    document.getElementById("select-all-canned").checked = false;
                    show_hide_canned_delete_btn(false);
                }
            } else {
                easyassist_show_long_toast("Some error occured while getting canned responses", 3000);
            }

        }
    }
    xhttp.send(params);
}

function create_canned_response_card(canned_response_data) {
    let canned_response_data_html = "";
    THEME_COLOR = THEME_COLOR.toLowerCase();
    let visibility_html = "";

    try {
        canned_response_data_html += '<tr>';

        if (AGENT_ROLE != "agent") {
            canned_response_data_html += `<td>
                                            <label class="canned-response-checkbox p-0 mb-0">
                                                <input
                                                type="checkbox"
                                                class="canned-checkbox"
                                                id="canned-response-checkbox-${canned_response_data['pk']}"
                                                />
                                                <span class="checkmark"></span>
                                            </label>
                                        </td>`;
        }

        canned_response_data_html += `<td>${canned_response_data.keyword}</td>
                                      <td>${canned_response_data.response}</td>
                                      <td><span class="email-text">${canned_response_data.added_by}</span></td>
                                      <td>
                                      <div class="d-flex align-items-center">`;

        if (canned_response_data.visibility == "Team Only") {
            visibility_html += `<svg class="mr-1" width="12" height="13" viewBox="0 0 12 13" fill="none" xmlns="http://www.w3.org/2000/svg">
                                                <path fill-rule="evenodd" clip-rule="evenodd" d="M4.25016 1.08008C2.99686 1.08008 1.98828 2.09352 1.98828 3.34195C1.98828 4.55932 2.94129 5.54748 4.14374 5.59749C4.21202 5.59244 4.28454 5.59223 4.35168 5.59745C5.55323 5.54698 6.50659 4.55931 6.51203 3.34129C6.51167 2.09364 5.49788 1.08008 4.25016 1.08008ZM1.33203 3.34195C1.33203 1.73205 2.63346 0.423828 4.25016 0.423828C5.86054 0.423828 7.16828 1.73157 7.16828 3.34195L7.16828 3.34332C7.16171 4.91849 5.92037 6.20143 4.35451 6.25406C4.33994 6.25455 4.32535 6.25407 4.31084 6.25262C4.27516 6.24905 4.22613 6.24877 4.1807 6.2529C4.16716 6.25413 4.15355 6.25452 4.13997 6.25406C2.57435 6.20143 1.33203 4.91843 1.33203 3.34195Z" fill="#4D4D4D"/>
                                                <path fill-rule="evenodd" clip-rule="evenodd" d="M8.24481 1.91858C8.24481 1.73736 8.39171 1.59045 8.57293 1.59045C9.88643 1.59045 10.9427 2.65381 10.9427 3.96025C10.9427 5.24013 9.92725 6.28241 8.66104 6.32981C8.64335 6.33047 8.62563 6.3297 8.60807 6.3275C8.58984 6.32523 8.56334 6.3247 8.53333 6.32803C8.35322 6.34804 8.19099 6.21826 8.17098 6.03815C8.15097 5.85804 8.28075 5.69581 8.46086 5.67579C8.52568 5.66859 8.59312 5.66722 8.65872 5.67304C9.56381 5.62751 10.2865 4.87786 10.2865 3.96025C10.2865 3.01502 9.52277 2.2467 8.57293 2.2467C8.39171 2.2467 8.24481 2.0998 8.24481 1.91858Z" fill="#4D4D4D"/>
                                                <path fill-rule="evenodd" clip-rule="evenodd" d="M4.35087 6.94983C5.45915 6.94983 6.58372 7.22826 7.44832 7.80572C8.22235 8.32085 8.65296 9.03334 8.65296 9.78847C8.65296 10.5436 8.22241 11.2574 7.44861 11.7754L7.44855 11.7755C6.58118 12.3558 5.45516 12.6359 4.3465 12.6359C3.23798 12.6359 2.1121 12.3559 1.24478 11.7757C0.470684 11.2605 0.0400391 10.548 0.0400391 9.79285C0.0400391 9.03777 0.470587 8.32391 1.24438 7.80591L1.24559 7.8051L1.24559 7.80511C2.11553 7.2283 3.24249 6.94983 4.35087 6.94983ZM1.60883 8.35166C0.971399 8.77859 0.696289 9.30704 0.696289 9.79285C0.696289 10.2786 0.971333 10.8055 1.60866 11.2296L1.60938 11.23C2.34618 11.723 3.33766 11.9796 4.3465 11.9796C5.35534 11.9796 6.34681 11.723 7.08361 11.23C7.72144 10.803 7.99671 10.2744 7.99671 9.78847C7.99671 9.30273 7.72166 8.77578 7.08433 8.35177L7.08384 8.35144C6.35011 7.8614 5.3601 7.60608 4.35087 7.60608C3.34202 7.60608 2.34883 7.86122 1.60883 8.35166Z" fill="#4D4D4D"/>
                                                <path fill-rule="evenodd" clip-rule="evenodd" d="M9.39571 7.67977C9.43555 7.50298 9.61116 7.39197 9.78794 7.4318C10.2369 7.53297 10.6735 7.71264 11.0397 7.99193C11.5651 8.38649 11.8523 8.93052 11.8523 9.49899C11.8523 10.0673 11.5652 10.6112 11.04 11.0058C10.669 11.2903 10.2256 11.4772 9.76523 11.5731C9.58782 11.6101 9.41404 11.4962 9.37708 11.3188C9.34012 11.1414 9.45398 10.9676 9.63139 10.9307C10.0104 10.8517 10.3598 10.7007 10.6418 10.4841L10.6448 10.4819L10.6448 10.4819C11.0286 10.194 11.196 9.83427 11.196 9.49899C11.196 9.1637 11.0286 8.80394 10.6448 8.51607L10.6425 8.51436L10.6425 8.51435C10.3672 8.30413 10.0226 8.1574 9.64367 8.072C9.46689 8.03216 9.35587 7.85655 9.39571 7.67977Z" fill="#4D4D4D"/>
                                            </svg>
                                        Team Only`;
        } else {
            visibility_html += `<svg class="mr-1" width="14" height="15" viewBox="0 0 14 15" fill="none" xmlns="http://www.w3.org/2000/svg">
                                            <g clip-path="url(#clip0_77_6595)">
                                                <path fill-rule="evenodd" clip-rule="evenodd"
                                                    d="M7.25218 1.38718C3.93132 1.38718 1.23923 4.07926 1.23923 7.40013C1.23923 10.721 3.93132 13.4131 7.25218 13.4131C10.573 13.4131 13.2651 10.721 13.2651 7.40013C13.2651 4.07926 10.573 1.38718 7.25218 1.38718ZM0.4375 7.40013C0.4375 3.63648 3.48853 0.585449 7.25218 0.585449C11.0158 0.585449 14.0669 3.63648 14.0669 7.40013C14.0669 11.1638 11.0158 14.2148 7.25218 14.2148C3.48853 14.2148 0.4375 11.1638 0.4375 7.40013Z"
                                                    fill="#4D4D4D" />
                                                <path fill-rule="evenodd" clip-rule="evenodd"
                                                    d="M7.70162 7.3238L9.22615 7.53018C9.35792 7.54564 9.4845 7.59063 9.59647 7.6618L13.2214 9.89149C13.41 10.0075 13.4688 10.2544 13.3528 10.4429C13.2368 10.6315 12.9899 10.6904 12.8013 10.5744L9.17353 8.3429C9.17125 8.3415 9.16899 8.34008 9.16674 8.33863C9.15633 8.33194 9.14452 8.32775 9.13223 8.32638C9.12903 8.32603 9.12584 8.32564 9.12266 8.32521L7.5927 8.11809L7.5895 8.11765C7.56315 8.11386 7.5363 8.11893 7.51314 8.13204C7.48999 8.14515 7.47183 8.16557 7.46153 8.19011C7.46039 8.19283 7.45922 8.19553 7.45801 8.19822L6.54271 10.2493L6.54206 10.2508C6.5313 10.2746 6.52778 10.3011 6.53194 10.3269C6.53607 10.3526 6.54758 10.3764 6.56505 10.3956C6.56518 10.3958 6.56531 10.3959 6.56544 10.3961L7.82033 11.7511L7.82271 11.7537C7.92104 11.8617 7.99308 11.991 8.03321 12.1315C8.07335 12.272 8.0805 12.4198 8.0541 12.5635C8.05393 12.5645 8.05376 12.5654 8.05358 12.5664C8.05343 12.5671 8.05329 12.5679 8.05314 12.5686L7.79258 13.8914C7.7498 14.1087 7.53902 14.2501 7.32181 14.2073C7.10459 14.1645 6.96318 13.9537 7.00597 13.7365L7.26588 12.417C7.2696 12.3953 7.26839 12.373 7.26233 12.3518C7.25622 12.3304 7.24535 12.3107 7.23053 12.2941L5.97607 10.9396L5.97491 10.9383C5.85104 10.8034 5.76949 10.6351 5.7404 10.4543C5.71135 10.2738 5.73584 10.0887 5.81085 9.92197C5.81098 9.92169 5.8111 9.92141 5.81123 9.92113L6.72433 7.87497C6.80368 7.68893 6.94202 7.5341 7.11809 7.4344C7.2951 7.33417 7.50026 7.29529 7.70162 7.3238Z"
                                                    fill="#4D4D4D" />
                                                <path fill-rule="evenodd" clip-rule="evenodd"
                                                    d="M3.19989 2.19409C3.40368 2.2806 3.49875 2.51594 3.41224 2.71972L2.81165 4.13443C2.7989 4.16566 2.79841 4.20056 2.81033 4.23214L2.81051 4.23262L3.57883 6.27702C3.5798 6.27961 3.58075 6.28221 3.58167 6.28482C3.58889 6.30531 3.60125 6.32361 3.61757 6.33796C3.63389 6.35231 3.65362 6.36223 3.67487 6.36677L3.67534 6.36687L5.10305 6.67376C5.24242 6.70239 5.37329 6.76289 5.4854 6.85054C5.59796 6.93854 5.68852 7.05149 5.74995 7.18048C5.75011 7.18081 5.75026 7.18114 5.75042 7.18147L6.00117 7.70275C6.01327 7.72564 6.03122 7.74495 6.05321 7.75869C6.0754 7.77256 6.10088 7.78025 6.12702 7.78098H7.02515C7.24654 7.78098 7.42602 7.96045 7.42602 8.18184C7.42602 8.40323 7.24654 8.58271 7.02515 8.58271H6.12321C6.1221 8.58271 6.12099 8.5827 6.11988 8.58269C6.11907 8.58268 6.11825 8.58268 6.11743 8.58266C5.94429 8.58017 5.77513 8.53033 5.6283 8.43856C5.48146 8.34678 5.36253 8.21657 5.28442 8.06203C5.28323 8.05968 5.28207 8.05733 5.28093 8.05496L5.02705 7.52716L5.02617 7.52531C5.01816 7.50843 5.00632 7.49365 4.9916 7.48215C4.97688 7.47064 4.95969 7.46272 4.94137 7.45901C4.93978 7.45869 4.93819 7.45836 4.9366 7.45802L3.50732 7.15079C3.50724 7.15077 3.50717 7.15076 3.50709 7.15074C3.35172 7.1175 3.20748 7.04495 3.08816 6.94003C2.96997 6.8361 2.88015 6.70386 2.8271 6.55573L2.06021 4.51515C2.06018 4.51504 2.06014 4.51494 2.0601 4.51484C1.97607 4.29189 1.98029 4.04528 2.07191 3.82533L2.07296 3.82281L2.67426 2.40643C2.76077 2.20264 2.99611 2.10757 3.19989 2.19409Z"
                                                    fill="#4D4D4D" />
                                                <path fill-rule="evenodd" clip-rule="evenodd"
                                                    d="M8.69588 0.842705C8.88957 0.735482 9.13351 0.80558 9.24074 0.999273L9.86207 2.12169L9.86355 2.12437C9.96341 2.30806 9.99932 2.51975 9.96563 2.7261C9.93194 2.93245 9.83056 3.12172 9.67747 3.26411C9.67605 3.26543 9.67462 3.26674 9.67318 3.26804L7.87947 4.88838C7.82559 4.93909 7.76553 4.98282 7.70072 5.01854C7.7006 5.01861 7.70048 5.01867 7.70036 5.01874L6.87923 5.4727C6.87721 5.47381 6.87519 5.47491 6.87316 5.47598C6.74017 5.54655 6.59265 5.58537 6.44215 5.58941C6.43857 5.5895 6.43498 5.58955 6.4314 5.58955H5.00301C4.97594 5.58982 4.94952 5.59791 4.92694 5.61286C4.90445 5.62776 4.88673 5.64881 4.87591 5.67351L4.32214 6.98787C4.23618 7.19189 4.00111 7.2876 3.79708 7.20164C3.59306 7.11568 3.49735 6.88061 3.58331 6.67659L4.13784 5.36042L4.139 5.3577C4.21143 5.18927 4.33144 5.04563 4.48431 4.9444C4.63718 4.84317 4.81627 4.78876 4.99961 4.78783L5.00165 4.78782H6.42445C6.44911 4.78662 6.47324 4.78017 6.49522 4.7689L7.31373 4.31639C7.31981 4.31305 7.32542 4.30893 7.33044 4.30415C7.33311 4.3016 7.33581 4.29908 7.33855 4.29661L9.13289 2.6757C9.1549 2.65465 9.16947 2.627 9.17438 2.59692C9.17934 2.56652 9.17417 2.53535 9.15967 2.50821L8.53931 1.38756C8.43209 1.19387 8.50219 0.949928 8.69588 0.842705Z"
                                                    fill="#4D4D4D" />
                                            </g>
                                            <defs>
                                                <clipPath id="clip0_77_6595">
                                                    <rect width="14" height="14" fill="white" transform="translate(0 0.585449)" />
                                                </clipPath>
                                            </defs>
                                        </svg>
                                        Everyone`;
        }

        canned_response_data_html += visibility_html;

        canned_response_data_html += `  </div>
                                      </td>`;

        if (AGENT_ROLE != "agent") {
            canned_response_data_html += '<td>';

            if (AGENT_ROLE == "admin" || canned_response_data.agent_role == "supervisor") {
                canned_response_data_html += `<div class="d-flex edit-delete-container justify-content-around">
                                                    <span class="edit-canned-response" onclick="populate_canned_response_edit_data('${canned_response_data.pk}', '${canned_response_data.keyword}', '${canned_response_data.response}', '${canned_response_data.visibility}')">
                                                `;

                if (THEME_COLOR) {
                    canned_response_data_html += `<svg width="24" height="25" viewBox="0 0 24 25" fill="${THEME_COLOR}" xmlns="http://www.w3.org/2000/svg">
                                                    <path d="M21.0302 3.55506C22.4276 4.95252 22.4276 7.21825 21.0302 8.61572L9.06186 20.584C8.78498 20.8609 8.44064 21.0607 8.06288 21.1638L2.94719 22.559C2.38732 22.7117 1.87359 22.1979 2.02628 21.638L3.42147 16.5224C3.52449 16.1446 3.72432 15.8003 4.0012 15.5234L15.9695 3.55506C17.367 2.15759 19.6327 2.15759 21.0302 3.55506ZM15 6.64596L5.06186 16.584C4.96956 16.6763 4.90296 16.7911 4.86861 16.917L3.81877 20.7665L7.6682 19.7166C7.79412 19.6823 7.9089 19.6157 8.0012 19.5234L17.939 9.58496L15 6.64596ZM17.0302 4.61572L16.06 5.58496L18.999 8.52496L19.9695 7.55506C20.7812 6.74338 20.7812 5.42739 19.9695 4.61572C19.1578 3.80404 17.8419 3.80404 17.0302 4.61572Z" fill=${THEME_COLOR}"/>`;
                } else {
                    canned_response_data_html += `<svg width="24" height="25" viewBox="0 0 24 25" fill="None" xmlns="http://www.w3.org/2000/svg">
                                                    <path d="M21.0302 3.55506C22.4276 4.95252 22.4276 7.21825 21.0302 8.61572L9.06186 20.584C8.78498 20.8609 8.44064 21.0607 8.06288 21.1638L2.94719 22.559C2.38732 22.7117 1.87359 22.1979 2.02628 21.638L3.42147 16.5224C3.52449 16.1446 3.72432 15.8003 4.0012 15.5234L15.9695 3.55506C17.367 2.15759 19.6327 2.15759 21.0302 3.55506ZM15 6.64596L5.06186 16.584C4.96956 16.6763 4.90296 16.7911 4.86861 16.917L3.81877 20.7665L7.6682 19.7166C7.79412 19.6823 7.9089 19.6157 8.0012 19.5234L17.939 9.58496L15 6.64596ZM17.0302 4.61572L16.06 5.58496L18.999 8.52496L19.9695 7.55506C20.7812 6.74338 20.7812 5.42739 19.9695 4.61572C19.1578 3.80404 17.8419 3.80404 17.0302 4.61572Z" fill="#0254D7"/>`;
                }

                canned_response_data_html += `  </svg>                                          
                                                        </span>
                                                        <span class="delete-canned-response" onclick="populate_canned_response_delete_data('${canned_response_data.pk}')">
                                                            <svg width="24" height="25" viewBox="0 0 24 25" fill="none" xmlns="http://www.w3.org/2000/svg">
                                                                <path d="M14 10.5854L13.7 17.5854M10.3 17.5854L10 10.5854M6 6.58545L6.87554 19.7185C6.94558 20.7691 7.81818 21.5854 8.87111 21.5854H15.1289C16.1818 21.5854 17.0544 20.7691 17.1245 19.7185L18 6.58545M6 6.58545H9M6 6.58545H4M18 6.58545H20M18 6.58545H15M15 6.58545V5.58545C15 4.48088 14.1046 3.58545 13 3.58545H11C9.89543 3.58545 9 4.48088 9 5.58545V6.58545M15 6.58545H9" stroke="#FF0000" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                                                            </svg>                                          
                                                        </span>
                                                    </div>`;
            }

            canned_response_data_html += `  </td>
                                        </tr>`;
        }

    } catch (err) {
        console.log("ERROR: create_canned_response_card ", err);
        canned_response_data_html = "";
    }
    return canned_response_data_html;
}

function add_pagination(pagination, start, end, total_objs) {
    let html = `<div class="row mt-3">`

    html += `<div class="col-md-6 col-sm-12 show-pagination-entry-container" filter_default_text="Showing 1 to 20 of 22 entries" start_point="1" end_point="20">
                Showing ${start} to ${end} entries out of ${total_objs}
                </div>
                <div class="col-md-6 col-sm-12">
                <div class="d-flex justify-content-end">
                <nav aria-label="Page navigation example">
                    <ul class="pagination">
                    <li id="previous-button" class="disabled page-item">
                        <span>
                            <a class="previous-button page-link" href="javascript:void(0)" aria-label="Previous">
                                <span aria-hidden="true">Previous</span>
                                <span class="sr-only">Previous</span>
                            </a>
                        </span>
                    </li>`;

    for (let page = 1; page < pagination.page_range; ++page) {
        if (pagination.number == page) {
            if (page == 1) {
                html += `<li class="purple darken-3 active page-item" id="page-${page}" ><a data-page="${page}" class="canned-response-pagination purple darken-3 page-item page-link" href="javascript:void(0)">${page}</a></li>`;
            } else if (pagination.num_pages == page) {
                html += `<li class="purple darken-3 page-item active" id="page-${page}" style="border-radius: 0 6px 6px 0;"><a data-page="${page}" class="canned-response-pagination purple darken-3 page-item page-link" href="javascript:void(0)">${page}</a></li>`;
            } else {
                html += `<li class="active purple darken-3 page-item" style="border-radius: 0px;" id="page-${page}"><a data-page="${page}" class="canned-response-pagination purple darken-3 page-item page-link" href="javascript:void(0)">${page}</a></li>`;
            }
        } else if (page > pagination.number - 5 && page < pagination.number + 5) {
            html += `<li class="purple darken-3 page-item" id="page-${page}"><a class="canned-response-pagination purple darken-3 page-item page-link" href="javascript:void(0)" data-page="${page}">${page}</a></li>`;
        }
    }
    html += `<li id="next-button" class="page-item">
                <a class="next-button page-link" href="javascript:void(0)" aria-label="Next">
                    <span aria-hidden="true">Next</span>
                    <span class="sr-only">Next</span>
                </a>
            </li>
            </ul>
            </nav>
            </div>
            </div>`;
    document.getElementById("canned-table-pagination-div").innerHTML = html;

    apply_pagination_events(pagination.page_range);
}

function apply_pagination_events(page_range) {
    let previous_button_ele = document.getElementById("previous-button");
    let next_button_ele = document.getElementById("next-button");
    $(".canned-response-pagination").on("click", (event) => {
        let current_page = event.target.dataset.page;
        if (document.getElementById('page-' + current_page.toString())) {
            $('#page-' + current_page.toString()).css({ "background": "black" });
        }
        if (current_page > 1) {
            if (document.getElementById('page-' + (current_page - 1).toString())) {
                document.getElementById('page-' + (current_page - 1).toString()).classList.remove("active");
            }
        }
        window.localStorage.setItem("canned_response_page", current_page);
        if (parseInt(window.localStorage.getItem("canned_response_page")) > 1) {
            if (previous_button_ele && previous_button_ele.classList.contains("disabled")) {
                previous_button_ele.classList.remove("disabled");
            }
        } else {
            if (previous_button_ele && !previous_button_ele.classList.contains("disabled")) {
                document.getElementById("previous-button").classList.add("disabled");
            }
        }

        if (parseInt(window.localStorage.getItem("canned_response_page")) < page_range - 1) {
            if (next_button_ele && next_button_ele.classList.contains("disabled")) {
                document.getElementById("next-button").classList.remove("disabled");
            }
        } else {
            if (!next_button_ele && next_button_ele.classList.contains("disabled")) {
                document.getElementById("next-button").classList.add("disabled");
            }
        }
        get_all_canned_response();
    });

    if (parseInt(window.localStorage.getItem("canned_response_page")) > 1) {
        if (previous_button_ele && previous_button_ele.classList.contains("disabled")) {
            previous_button_ele.classList.remove("disabled");
        }
        $(".previous-button").on("click", (event) => {
            let page_number = parseInt(window.localStorage.getItem("canned_response_page")) - 1;
            window.localStorage.setItem("canned_response_page", page_number);
            get_all_canned_response();
        });
    } else {
        if (previous_button_ele && !previous_button_ele.classList.contains("disabled")) {
            document.getElementById("previous-button").classList.add("disabled");
        }
    }

    if (parseInt(window.localStorage.getItem("canned_response_page")) < page_range - 1) {
        if (next_button_ele && next_button_ele.classList.contains("disabled")) {
            document.getElementById("next-button").classList.remove("disabled");
        }
        $(".next-button").on("click", (event) => {
            let page_number = parseInt(window.localStorage.getItem("canned_response_page")) + 1;
            window.localStorage.setItem("canned_response_page", page_number);
            get_all_canned_response()
        });
    } else {
        if (next_button_ele && !next_button_ele.classList.contains("disabled")) {
            document.getElementById("next-button").classList.add("disabled");
        }
    }
}

function set_canned_response_local_storage_obj() {
    let searched_keyword = window.localStorage.getItem("searched_keyword");
    let updated_searched_keyword = document.getElementById("custom-table-search").value;
    window.localStorage.setItem("canned_response_page", '1');

    if (updated_searched_keyword) {
        searched_keyword = updated_searched_keyword;
        window.localStorage.setItem("searched_keyword", searched_keyword);
    } else {
        window.localStorage.removeItem("searched_keyword");
    }
}

function select_canned_handler(el) {
    let all_checkboxes = document.getElementsByClassName("canned-checkbox");
    let checked_count = 0;
    Array.from(all_checkboxes).forEach((checkbox) => {
        if (checkbox.checked) {
            checked_count++;
        }
    });

    if (all_checkboxes.length == checked_count) {
        document.getElementById("select-all-canned").checked = true;
        show_hide_canned_delete_btn(true);
    } else if (checked_count > 1) {
        document.getElementById("select-all-canned").checked = false;
        show_hide_canned_delete_btn(true);
    } else {
        document.getElementById("select-all-canned").checked = false;
        show_hide_canned_delete_btn(false);
    }
}

function show_hide_canned_delete_btn(show) {
    if (show) {
        document.getElementById("delete-all-btn-div").classList.remove('d-none')
    } else {
        document.getElementById("delete-all-btn-div").classList.add('d-none')
    }
}

function get_shorter_canned_response_file_name(filename, file_name_required_length) {
    let dot_index = filename.lastIndexOf(".");
    if (dot_index > 0 && dot_index > file_name_required_length) {
        var fileExtension = filename.substring(dot_index, filename.length);
        filename = filename.substring(0, file_name_required_length) + "..." + fileExtension;
    }
    return filename;
}

function populate_canned_response_edit_data(canned_response_pk, keyword, response, visibility) {

    let error_element = document.getElementById("error-message-edit");
    error_element.innerHTML = "";
    
    if(!error_element.classList.contains("d-none")) {
        error_element.classList.add("d-none");
    }

    let visibility_html = "";
    if (visibility == "Team Only") {
        visibility_html += `<svg class="mr-1" width="12" height="13" viewBox="0 0 12 13" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path fill-rule="evenodd" clip-rule="evenodd" d="M4.25016 1.08008C2.99686 1.08008 1.98828 2.09352 1.98828 3.34195C1.98828 4.55932 2.94129 5.54748 4.14374 5.59749C4.21202 5.59244 4.28454 5.59223 4.35168 5.59745C5.55323 5.54698 6.50659 4.55931 6.51203 3.34129C6.51167 2.09364 5.49788 1.08008 4.25016 1.08008ZM1.33203 3.34195C1.33203 1.73205 2.63346 0.423828 4.25016 0.423828C5.86054 0.423828 7.16828 1.73157 7.16828 3.34195L7.16828 3.34332C7.16171 4.91849 5.92037 6.20143 4.35451 6.25406C4.33994 6.25455 4.32535 6.25407 4.31084 6.25262C4.27516 6.24905 4.22613 6.24877 4.1807 6.2529C4.16716 6.25413 4.15355 6.25452 4.13997 6.25406C2.57435 6.20143 1.33203 4.91843 1.33203 3.34195Z" fill="#4D4D4D"/>
                                <path fill-rule="evenodd" clip-rule="evenodd" d="M8.24481 1.91858C8.24481 1.73736 8.39171 1.59045 8.57293 1.59045C9.88643 1.59045 10.9427 2.65381 10.9427 3.96025C10.9427 5.24013 9.92725 6.28241 8.66104 6.32981C8.64335 6.33047 8.62563 6.3297 8.60807 6.3275C8.58984 6.32523 8.56334 6.3247 8.53333 6.32803C8.35322 6.34804 8.19099 6.21826 8.17098 6.03815C8.15097 5.85804 8.28075 5.69581 8.46086 5.67579C8.52568 5.66859 8.59312 5.66722 8.65872 5.67304C9.56381 5.62751 10.2865 4.87786 10.2865 3.96025C10.2865 3.01502 9.52277 2.2467 8.57293 2.2467C8.39171 2.2467 8.24481 2.0998 8.24481 1.91858Z" fill="#4D4D4D"/>
                                <path fill-rule="evenodd" clip-rule="evenodd" d="M4.35087 6.94983C5.45915 6.94983 6.58372 7.22826 7.44832 7.80572C8.22235 8.32085 8.65296 9.03334 8.65296 9.78847C8.65296 10.5436 8.22241 11.2574 7.44861 11.7754L7.44855 11.7755C6.58118 12.3558 5.45516 12.6359 4.3465 12.6359C3.23798 12.6359 2.1121 12.3559 1.24478 11.7757C0.470684 11.2605 0.0400391 10.548 0.0400391 9.79285C0.0400391 9.03777 0.470587 8.32391 1.24438 7.80591L1.24559 7.8051L1.24559 7.80511C2.11553 7.2283 3.24249 6.94983 4.35087 6.94983ZM1.60883 8.35166C0.971399 8.77859 0.696289 9.30704 0.696289 9.79285C0.696289 10.2786 0.971333 10.8055 1.60866 11.2296L1.60938 11.23C2.34618 11.723 3.33766 11.9796 4.3465 11.9796C5.35534 11.9796 6.34681 11.723 7.08361 11.23C7.72144 10.803 7.99671 10.2744 7.99671 9.78847C7.99671 9.30273 7.72166 8.77578 7.08433 8.35177L7.08384 8.35144C6.35011 7.8614 5.3601 7.60608 4.35087 7.60608C3.34202 7.60608 2.34883 7.86122 1.60883 8.35166Z" fill="#4D4D4D"/>
                                <path fill-rule="evenodd" clip-rule="evenodd" d="M9.39571 7.67977C9.43555 7.50298 9.61116 7.39197 9.78794 7.4318C10.2369 7.53297 10.6735 7.71264 11.0397 7.99193C11.5651 8.38649 11.8523 8.93052 11.8523 9.49899C11.8523 10.0673 11.5652 10.6112 11.04 11.0058C10.669 11.2903 10.2256 11.4772 9.76523 11.5731C9.58782 11.6101 9.41404 11.4962 9.37708 11.3188C9.34012 11.1414 9.45398 10.9676 9.63139 10.9307C10.0104 10.8517 10.3598 10.7007 10.6418 10.4841L10.6448 10.4819L10.6448 10.4819C11.0286 10.194 11.196 9.83427 11.196 9.49899C11.196 9.1637 11.0286 8.80394 10.6448 8.51607L10.6425 8.51436L10.6425 8.51435C10.3672 8.30413 10.0226 8.1574 9.64367 8.072C9.46689 8.03216 9.35587 7.85655 9.39571 7.67977Z" fill="#4D4D4D"/>
                            </svg>
                            Team Only`;
    } else {
        visibility_html += `<svg class="mr-1" width="14" height="15" viewBox="0 0 14 15" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <g clip-path="url(#clip0_77_6595)">
                                    <path fill-rule="evenodd" clip-rule="evenodd"
                                        d="M7.25218 1.38718C3.93132 1.38718 1.23923 4.07926 1.23923 7.40013C1.23923 10.721 3.93132 13.4131 7.25218 13.4131C10.573 13.4131 13.2651 10.721 13.2651 7.40013C13.2651 4.07926 10.573 1.38718 7.25218 1.38718ZM0.4375 7.40013C0.4375 3.63648 3.48853 0.585449 7.25218 0.585449C11.0158 0.585449 14.0669 3.63648 14.0669 7.40013C14.0669 11.1638 11.0158 14.2148 7.25218 14.2148C3.48853 14.2148 0.4375 11.1638 0.4375 7.40013Z"
                                        fill="#4D4D4D" />
                                    <path fill-rule="evenodd" clip-rule="evenodd"
                                        d="M7.70162 7.3238L9.22615 7.53018C9.35792 7.54564 9.4845 7.59063 9.59647 7.6618L13.2214 9.89149C13.41 10.0075 13.4688 10.2544 13.3528 10.4429C13.2368 10.6315 12.9899 10.6904 12.8013 10.5744L9.17353 8.3429C9.17125 8.3415 9.16899 8.34008 9.16674 8.33863C9.15633 8.33194 9.14452 8.32775 9.13223 8.32638C9.12903 8.32603 9.12584 8.32564 9.12266 8.32521L7.5927 8.11809L7.5895 8.11765C7.56315 8.11386 7.5363 8.11893 7.51314 8.13204C7.48999 8.14515 7.47183 8.16557 7.46153 8.19011C7.46039 8.19283 7.45922 8.19553 7.45801 8.19822L6.54271 10.2493L6.54206 10.2508C6.5313 10.2746 6.52778 10.3011 6.53194 10.3269C6.53607 10.3526 6.54758 10.3764 6.56505 10.3956C6.56518 10.3958 6.56531 10.3959 6.56544 10.3961L7.82033 11.7511L7.82271 11.7537C7.92104 11.8617 7.99308 11.991 8.03321 12.1315C8.07335 12.272 8.0805 12.4198 8.0541 12.5635C8.05393 12.5645 8.05376 12.5654 8.05358 12.5664C8.05343 12.5671 8.05329 12.5679 8.05314 12.5686L7.79258 13.8914C7.7498 14.1087 7.53902 14.2501 7.32181 14.2073C7.10459 14.1645 6.96318 13.9537 7.00597 13.7365L7.26588 12.417C7.2696 12.3953 7.26839 12.373 7.26233 12.3518C7.25622 12.3304 7.24535 12.3107 7.23053 12.2941L5.97607 10.9396L5.97491 10.9383C5.85104 10.8034 5.76949 10.6351 5.7404 10.4543C5.71135 10.2738 5.73584 10.0887 5.81085 9.92197C5.81098 9.92169 5.8111 9.92141 5.81123 9.92113L6.72433 7.87497C6.80368 7.68893 6.94202 7.5341 7.11809 7.4344C7.2951 7.33417 7.50026 7.29529 7.70162 7.3238Z"
                                        fill="#4D4D4D" />
                                    <path fill-rule="evenodd" clip-rule="evenodd"
                                        d="M3.19989 2.19409C3.40368 2.2806 3.49875 2.51594 3.41224 2.71972L2.81165 4.13443C2.7989 4.16566 2.79841 4.20056 2.81033 4.23214L2.81051 4.23262L3.57883 6.27702C3.5798 6.27961 3.58075 6.28221 3.58167 6.28482C3.58889 6.30531 3.60125 6.32361 3.61757 6.33796C3.63389 6.35231 3.65362 6.36223 3.67487 6.36677L3.67534 6.36687L5.10305 6.67376C5.24242 6.70239 5.37329 6.76289 5.4854 6.85054C5.59796 6.93854 5.68852 7.05149 5.74995 7.18048C5.75011 7.18081 5.75026 7.18114 5.75042 7.18147L6.00117 7.70275C6.01327 7.72564 6.03122 7.74495 6.05321 7.75869C6.0754 7.77256 6.10088 7.78025 6.12702 7.78098H7.02515C7.24654 7.78098 7.42602 7.96045 7.42602 8.18184C7.42602 8.40323 7.24654 8.58271 7.02515 8.58271H6.12321C6.1221 8.58271 6.12099 8.5827 6.11988 8.58269C6.11907 8.58268 6.11825 8.58268 6.11743 8.58266C5.94429 8.58017 5.77513 8.53033 5.6283 8.43856C5.48146 8.34678 5.36253 8.21657 5.28442 8.06203C5.28323 8.05968 5.28207 8.05733 5.28093 8.05496L5.02705 7.52716L5.02617 7.52531C5.01816 7.50843 5.00632 7.49365 4.9916 7.48215C4.97688 7.47064 4.95969 7.46272 4.94137 7.45901C4.93978 7.45869 4.93819 7.45836 4.9366 7.45802L3.50732 7.15079C3.50724 7.15077 3.50717 7.15076 3.50709 7.15074C3.35172 7.1175 3.20748 7.04495 3.08816 6.94003C2.96997 6.8361 2.88015 6.70386 2.8271 6.55573L2.06021 4.51515C2.06018 4.51504 2.06014 4.51494 2.0601 4.51484C1.97607 4.29189 1.98029 4.04528 2.07191 3.82533L2.07296 3.82281L2.67426 2.40643C2.76077 2.20264 2.99611 2.10757 3.19989 2.19409Z"
                                        fill="#4D4D4D" />
                                    <path fill-rule="evenodd" clip-rule="evenodd"
                                        d="M8.69588 0.842705C8.88957 0.735482 9.13351 0.80558 9.24074 0.999273L9.86207 2.12169L9.86355 2.12437C9.96341 2.30806 9.99932 2.51975 9.96563 2.7261C9.93194 2.93245 9.83056 3.12172 9.67747 3.26411C9.67605 3.26543 9.67462 3.26674 9.67318 3.26804L7.87947 4.88838C7.82559 4.93909 7.76553 4.98282 7.70072 5.01854C7.7006 5.01861 7.70048 5.01867 7.70036 5.01874L6.87923 5.4727C6.87721 5.47381 6.87519 5.47491 6.87316 5.47598C6.74017 5.54655 6.59265 5.58537 6.44215 5.58941C6.43857 5.5895 6.43498 5.58955 6.4314 5.58955H5.00301C4.97594 5.58982 4.94952 5.59791 4.92694 5.61286C4.90445 5.62776 4.88673 5.64881 4.87591 5.67351L4.32214 6.98787C4.23618 7.19189 4.00111 7.2876 3.79708 7.20164C3.59306 7.11568 3.49735 6.88061 3.58331 6.67659L4.13784 5.36042L4.139 5.3577C4.21143 5.18927 4.33144 5.04563 4.48431 4.9444C4.63718 4.84317 4.81627 4.78876 4.99961 4.78783L5.00165 4.78782H6.42445C6.44911 4.78662 6.47324 4.78017 6.49522 4.7689L7.31373 4.31639C7.31981 4.31305 7.32542 4.30893 7.33044 4.30415C7.33311 4.3016 7.33581 4.29908 7.33855 4.29661L9.13289 2.6757C9.1549 2.65465 9.16947 2.627 9.17438 2.59692C9.17934 2.56652 9.17417 2.53535 9.15967 2.50821L8.53931 1.38756C8.43209 1.19387 8.50219 0.949928 8.69588 0.842705Z"
                                        fill="#4D4D4D" />
                                </g>
                                <defs>
                                    <clipPath id="clip0_77_6595">
                                        <rect width="14" height="14" fill="white" transform="translate(0 0.585449)" />
                                    </clipPath>
                                </defs>
                            </svg>
                            Everyone`;
    }

    document.getElementById("edit-canned-keyword").value = keyword;
    document.getElementById("edit-canned-response").value = response;
    document.getElementById("canned-visibility").innerHTML = visibility_html;
    document.getElementById("count").innerHTML = keyword.length;
    document.getElementById("response-count").innerHTML = response.length;
    document.getElementById("canned-response-edit-save-button").setAttribute("onclick", `edit_canned_response('${canned_response_pk}')`);
    $("#modal-edit-canned-response").modal("show");
}

function populate_canned_response_delete_data(canned_response_pk) {
    let error_element = document.getElementById("error-message-delete");
    error_element.innerHTML = "";
    
    if(!error_element.classList.contains("d-none")) {
        error_element.classList.add("d-none");
    }

    document.getElementById("delete-canned-response-button").setAttribute("onclick", `delete_canned_response('${canned_response_pk}')`);
    $("#modal-delete-canned-response").modal("show");
}

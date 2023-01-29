$(document).ready(function() {
    initialize_active_sandbox_user_table();
});

$(document).on('click', '.cobrowse-show-password-icon-wrapper', function() {
    var input = $(".cobrowse-password-input-field");
    input.attr('type') === 'password' ? input.attr('type', 'text') : input.attr('type', 'password')
    if (input.attr('type') === 'password') {
        $(".cobrowse-password-hide-icon").css("display", "inline-block")
        $(".cobrowse-password-show-icon").css("display", "none")

    } else {
        $(".cobrowse-password-hide-icon").css("display", "none")
        $(".cobrowse-password-show-icon").css("display", "inline-block")
    }
});

$(".add-cobrowsing-access-cb").on("change", function(event) {
    if (this.checked) {
        $(".cobrowsing-options-wrapper").fadeIn(500);

    } else {
        $('.cobrowsing-options-wrapper').fadeOut(500);
    }
    document.getElementById("video-meeting-access").checked = false
});

$(".edit-cobrowsing-access-cb").on("change", function(event) {
    if (this.checked) {
        $(".cobrowsing-options-wrapper").fadeIn(500);

    } else {
        $('.cobrowsing-options-wrapper').fadeOut(500);
    }
    document.getElementById("edit-video-meeting-enabled").checked = false
});

// add user
$(".add-reverse-cobrowsing-cb").on("change", function(event) {
    if (this.checked) {

        // $(".add-outbound-cobrowsing-cb").attr("disabled", true);
        // $(".add-outbound-cobrowsing-cb").parent().css("opacity", "0.5");
        // $(".add-inbound-cobrowsing-cb").attr("disabled", true);
        // $(".add-inbound-cobrowsing-cb").parent().css("opacity", "0.5");
        document.getElementById("inbound-cobrowsing-access").checked = false;
        document.getElementById("outbound-cobrowsing-access").checked = false; 

    } else {
        // $(".add-outbound-cobrowsing-cb").attr("disabled", false);
        // $(".add-inbound-cobrowsing-cb").attr("disabled", false);
        $(".add-outbound-cobrowsing-cb").parent().css("opacity", "1");
        $(".add-inbound-cobrowsing-cb").parent().css("opacity", "1");
    }
});

$(".add-inbound-cobrowsing-cb").on("change", function(event) {
    if (this.checked) {

        // $(".add-reverse-cobrowsing-cb").attr("disabled", true);
        // $(".add-reverse-cobrowsing-cb").parent().css("opacity", "0.5");
        document.getElementById("reverse-cobrowsing-access").checked = false; 

    } else if ($(".add-outbound-cobrowsing-cb").prop('checked') == true) {
        // $(".add-reverse-cobrowsing-cb").attr("disabled", true);
        // $(".add-reverse-cobrowsing-cb").parent().css("opacity", "0.5");
        document.getElementById("reverse-cobrowsing-access").checked = false; 


    } else if ($(".add-inbound-cobrowsing-cb").prop('checked') == false) {
        // $(".add-reverse-cobrowsing-cb").attr("disabled", false);
        // $(".add-reverse-cobrowsing-cb").parent().css("opacity", "1");
        document.getElementById("reverse-cobrowsing-access").checked = false; 

    }
});

$(".add-outbound-cobrowsing-cb").on("change", function(event) {
    if (this.checked) {

        // $(".add-reverse-cobrowsing-cb").attr("disabled", true);
        // $(".add-reverse-cobrowsing-cb").parent().css("opacity", "0.5");
        document.getElementById("reverse-cobrowsing-access").checked = false; 

    } else if ($(".add-inbound-cobrowsing-cb").prop('checked') == true) {

        // $(".add-reverse-cobrowsing-cb").attr("disabled", true);
        // $(".add-reverse-cobrowsing-cb").parent().css("opacity", "0.5");
        document.getElementById("reverse-cobrowsing-access").checked = false; 

    } else if ($(".add-outbound-cobrowsing-cb").prop('checked') == false) {

        // $(".add-reverse-cobrowsing-cb").attr("disabled", false);
        // $(".add-reverse-cobrowsing-cb").parent().css("opacity", "1");
        document.getElementById("reverse-cobrowsing-access").checked = false; 

    }
});

// edit user
$(".edit-reverse-cobrowsing-cb").on("change", function(event) {
    if (this.checked) {

        // $(".edit-outbound-cobrowsing-cb").attr("disabled", true);
        // $(".edit-outbound-cobrowsing-cb").parent().css("opacity", "0.5");
        // $(".edit-inbound-cobrowsing-cb").attr("disabled", true);
        // $(".edit-inbound-cobrowsing-cb").parent().css("opacity", "0.5");
        document.getElementById("inbound-cobrowsing-access").checked = false;
        document.getElementById("outbound-cobrowsing-access").checked = false;
        document.getElementById("edit-inbound-enabled").checked = false;
        document.getElementById("edit-outbound-enabled").checked = false; 

    } else {
        // $(".edit-outbound-cobrowsing-cb").attr("disabled", false);
        // $(".edit-inbound-cobrowsing-cb").attr("disabled", false);
        // $(".edit-outbound-cobrowsing-cb").parent().css("opacity", "1");
        // $(".edit-inbound-cobrowsing-cb").parent().css("opacity", "1");
        document.getElementById("inbound-cobrowsing-access").checked = false;
        document.getElementById("outbound-cobrowsing-access").checked = false;
        document.getElementById("edit-inbound-enabled").checked = false;
        document.getElementById("edit-outbound-enabled").checked = false;  
    }

});
$(".edit-inbound-cobrowsing-cb").on("change", function(event) {
    if (this.checked) {

        // $(".edit-reverse-cobrowsing-cb").attr("disabled", true);
        // $(".edit-reverse-cobrowsing-cb").parent().css("opacity", "0.5");
        document.getElementById("reverse-cobrowsing-access").checked = false;
        document.getElementById("edit-reverse-cobrowsing-enabled").checked = false; 

    } else if ($(".edit-outbound-cobrowsing-cb").prop('checked') == true) {
        // $(".edit-reverse-cobrowsing-cb").attr("disabled", true);
        // $(".edit-reverse-cobrowsing-cb").parent().css("opacity", "0.5");
        document.getElementById("reverse-cobrowsing-access").checked = false; 
        document.getElementById("edit-reverse-cobrowsing-enabled").checked = false;

    } else if ($(".edit-inbound-cobrowsing-cb").prop('checked') == false) {
        // $(".edit-reverse-cobrowsing-cb").attr("disabled", false);
        // $(".edit-reverse-cobrowsing-cb").parent().css("opacity", "1");
        document.getElementById("reverse-cobrowsing-access").checked = false; 
        document.getElementById("edit-reverse-cobrowsing-enabled").checked = false;
    }
});

$(".edit-outbound-cobrowsing-cb").on("change", function(event) {
    if (this.checked) {

        // $(".edit-reverse-cobrowsing-cb").attr("disabled", true);
        // $(".edit-reverse-cobrowsing-cb").parent().css("opacity", "0.5");
        document.getElementById("reverse-cobrowsing-access").checked = false; 
        document.getElementById("edit-reverse-cobrowsing-enabled").checked = false;

    } else if ($(".edit-inbound-cobrowsing-cb").prop('checked') == true) {
        // $(".edit-reverse-cobrowsing-cb").attr("disabled", true);
        // $(".edit-reverse-cobrowsing-cb").parent().css("opacity", "0.5");
        document.getElementById("reverse-cobrowsing-access").checked = false; 
        document.getElementById("edit-reverse-cobrowsing-enabled").checked = false;

    } else if ($(".edit-outbound-cobrowsing-cb").prop('checked') == false) {
        // $(".edit-reverse-cobrowsing-cb").attr("disabled", false);
        // $(".edit-reverse-cobrowsing-cb").parent().css("opacity", "1");
        document.getElementById("reverse-cobrowsing-access").checked = false; 
        document.getElementById("edit-reverse-cobrowsing-enabled").checked = false;
    }
});

$("#video-meeting-access").on("change", function(event) {
    document.getElementById("inbound-cobrowsing-access").checked = false;
    document.getElementById("outbound-cobrowsing-access").checked = false;
    document.getElementById("reverse-cobrowsing-access").checked = false; 
    document.getElementById("edit-reverse-cobrowsing-enabled").checked = false;
    document.getElementById("edit-inbound-enabled").checked = false;
    document.getElementById("edit-outbound-enabled").checked = false;
    document.getElementById("cobrowsing-access").checked = false;
    $('.cobrowsing-options-wrapper').fadeOut(500);
});

$("#edit-video-meeting-enabled").on("change", function(event) {
    document.getElementById("inbound-cobrowsing-access").checked = false;
    document.getElementById("outbound-cobrowsing-access").checked = false;
    document.getElementById("reverse-cobrowsing-access").checked = false; 
    document.getElementById("edit-reverse-cobrowsing-enabled").checked = false;
    document.getElementById("edit-inbound-enabled").checked = false;
    document.getElementById("edit-outbound-enabled").checked = false;
    document.getElementById("edit-cobrowsing-enabled").checked = false;
    document.getElementById("cobrowsing-access").checked = false;
    $('.cobrowsing-options-wrapper').fadeOut(500);
});

function hide_add_sandbox_user_modal() {
    document.getElementById("sandbox-user-email-id").value = "";
    document.getElementById("sandbox-user-password").value = "";
    document.getElementById("error-element").innerHTML = "";

    document.getElementById("cobrowsing-access").click();
    document.getElementById("inbound-cobrowsing-access").checked = false;
    document.getElementById("outbound-cobrowsing-access").checked = false; 
    document.getElementById("reverse-cobrowsing-access").checked = false; 
    document.getElementById("video-meeting-access").checked = false; 

    $("#modal-sandbox-add-user").modal("hide");
}

function add_new_sandbox_user(element) {
	var error_message_element = document.getElementById("error-element");
	error_message_element.innerHTML = "";

	let email_id = document.getElementById("sandbox-user-email-id").value;
	let password = document.getElementById("sandbox-user-password").value;

	email_id = stripHTML(email_id)
	password = stripHTML(password)

	let is_cobrowsing_enabled = document.getElementById("cobrowsing-access").checked;
	let inbound_enabled = document.getElementById("inbound-cobrowsing-access").checked;
	let outbound_enabled = document.getElementById("outbound-cobrowsing-access").checked;
	let reverse_cobrowsing_enabled = document.getElementById("reverse-cobrowsing-access").checked;

	let video_meeting_enabled = document.getElementById("video-meeting-access").checked;

    if(!is_cobrowsing_enabled && !video_meeting_enabled) {
        error_message_element.innerHTML = "Please select at least one of the option";
        error_message_element.style.color = "red";
        return;
    }

    if(is_cobrowsing_enabled) {
        if(!inbound_enabled && !outbound_enabled && !reverse_cobrowsing_enabled) {
            error_message_element.innerHTML = "Please select at least one of the cobrowsing options";
            error_message_element.style.color = "red";
            return;
        }
    }

	if(inbound_enabled || outbound_enabled) {
		reverse_cobrowsing_enabled = false;
	}

	const regEmail = /^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/;
	if (!regEmail.test(email_id)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter valid email id";
        return;
    }

    const regexPassword = /^(?=.*[A-Z])(?=.*[!@#$&*])(?=.*\d)(?=.*[a-z]).{8,}/;
    if (!regexPassword.test(password)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please Enter valid Password";
        return;
    }

    let request_params = {
        "email_id": email_id,
        "password": password,
        "is_cobrowsing_enabled": is_cobrowsing_enabled,
        "inbound_enabled": inbound_enabled,
        "outbound_enabled": outbound_enabled,
        "reverse_cobrowsing_enabled": reverse_cobrowsing_enabled,
        "video_meeting_enabled": video_meeting_enabled,
    };

    let json_params = JSON.stringify(request_params);

    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/sandbox-user/create/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                error_message_element.style.color = "green";
                error_message_element.innerHTML = "Sandbox User created successfully.";

                hide_add_sandbox_user_modal();
                window.ACTIVE_SANDBOX_USER_TABLE.fetch_active_sandbox_users();
                window.location.reload();

            } else if (response.status == 301) {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = "User with same email id already exist.";
            } else {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = "Something went wrong. Please try again.";
            }
        }
        element.innerHTML = "Save";
    }
    xhttp.send(params);
}

class SandboxUserTableBase {
    update_table_attribute(table_elements) {
        for (var idx = 0; idx < table_elements.length; idx++) {
            var table_el = table_elements[idx];
            var thead_el = table_elements[idx].getElementsByTagName('thead');
            if (thead_el.length == 0) {
                continue;
            }
            thead_el = thead_el[0];
            var tbody_el = table_elements[idx].getElementsByTagName('tbody');
            if (tbody_el.length == 0) {
                continue;
            }

            tbody_el = tbody_el[0];
            for (var row_index = 0; row_index < tbody_el.rows.length; row_index++) {
                if (tbody_el.rows[row_index].children.length != thead_el.rows[0].children.length) {
                    continue;
                }
                for (var col_index = 0; col_index < tbody_el.rows[row_index].children.length; col_index++) {
                    var column_element = tbody_el.rows[row_index].children[col_index];
                    var th_text = thead_el.rows[0].children[col_index].innerText;
                    column_element.setAttribute("data-content", th_text);
                }
            }
        }
    }

    apply_pagination(pagination_container, pagination_metadata, onclick_handler, target_obj) {
        var metadata = pagination_metadata;
        var html = "";

        var filter_default_text = "Showing " + metadata.start_point + " to " + metadata.end_point + " of " + metadata.total_count + " entries";

        if (metadata.has_previous) {
            html += [
                '<li class="page-item">',
                '<a class="page-link previous_button" data-page="' + metadata.previous_page_number + '" href="javascript:void(0)" aria-label="Previous">',
                '<span aria-hidden="true">Previous</span>',
                '<span class="sr-only">Previous</span>',
                '</a>',
                '</li>'
            ].join('');
        } else {
            html += [
                '<li class="page-item disabled">',
                '<a class="page-link previous_button" href="javascript:void(0)" aria-label="Previous">',
                '<span aria-hidden="true">Previous</span>',
                '<span class="sr-only">Previous</span>',
                '</a>',
                '</li>'
            ].join('');
        }

        if ((metadata.number - 4) > 1) {
            html += '<li class="page-item"><a class="page-link" data-page="' + (metadata.number - 5) + '" href="javascript:void(0)">&hellip;</a></li>';
        }

        for (var index = metadata.page_range[0]; index < metadata.page_range[1]; index++) {
            if (metadata.number == index) {
                html += [
                    '<li class="active purple darken-3 page-item">',
                    '<a data-page="' + index + '" href="javascript:void(0)" class="page-link">' + index + '</a>',
                    '</li>',
                ].join('');
            } else if (index > (metadata.number - 5) && index < (metadata.number + 5)) {
                html += [
                    '<li class="page-item">',
                    '<a href="javascript:void(0)" data-page="' + index + '" class="page-link">' + index + '</a>',
                    '</li>',
                ].join('');
            }
        }

        if (metadata.num_pages > (metadata.number + 4)) {
            html += [
                '<li class="page-item">',
                '<a href="javascript:void(0)" data-page="' + (metadata.number + 5) + '" class="page-link">&hellip;</a>',
                '</li>',
            ].join('');
        }

        if (metadata.has_next) {
            html += [
                '<li class="page-item">',
                '<a class="page-link next_button" data-page="' + metadata.next_page_number + '" href="javascript:void(0)" aria-label="Previous">',
                '<span aria-hidden="true">Next</span>',
                '<span class="sr-only">Next</span>',
                '</a>',
                '</li>'
            ].join('');
        } else {
            html += [
                '<li class="page-item disabled">',
                '<a class="page-link next_button" href="javascript:void(0)" aria-label="Previous">',
                '<span aria-hidden="true">Next</span>',
                '<span class="sr-only">Next</span>',
                '</a>',
                '</li>'
            ].join('');
        }

        html = [
            '<div class="col-md-6 col-sm-12 show-pagination-entry-container" filter_default_text=\'' + filter_default_text + '\'>',
            filter_default_text,
            '</div>',
            '<div class="col-md-6 col-sm-12">',
            '<div class="d-flex justify-content-end">',
            '<nav aria-label="Page navigation example">',
            '<ul class="pagination">',
            html,
            '</ul>',
            '</nav>',
            '</div>',
            '</div>',
        ].join('');

        pagination_container.innerHTML = html;

        var pagination_links = pagination_container.querySelectorAll('a.page-link');

        pagination_links.forEach((pagination_link_element) => {
            var page_number = pagination_link_element.getAttribute('data-page');
            if (page_number != null && page_number != undefined) {
                pagination_link_element.addEventListener('click', function (event) {
                    onclick_handler('page', page_number, target_obj);
                })
            }
        });
    }
};

class ActiveSandboxUserTable extends SandboxUserTableBase {
    constructor(table_container, pagination_container) {
        super();
        this.table_container = table_container;
        this.table = null;
        this.options = {};

        this.active_user_metadata = {};
        this.pagination_container = pagination_container;

        this.data_checklist = {
            'sandbox_user_data': false,
        };

        this.data_table_obj = null;

        this.init();
    }

    init() {
        var _this = this;
        _this.initialize_table_header_metadata();
        _this.fetch_active_sandbox_users();
    }

    initialize_table_header_metadata() {
        var _this = this;
        _this.active_user_metadata.lead_data_cols = _this.get_table_meta_data();
    }

    initialize_table() {
        var _this = this;

        _this.table_container.innerHTML = '<table class="table table-bordered" id="sandbox_user_table" width="100%" cellspacing="0"></table>';
        _this.table = _this.table_container.querySelector("table");

        if (!_this.table) return;
        if (_this.active_user_metadata.lead_data_cols.length == 0) return;

        _this.initialize_head();
        _this.initialize_body();
        _this.add_event_listeners();
        _this.add_event_listeners_in_rows();
        _this.update_table_attribute([_this.table]);
    }

    initialize_head() {
        var _this = this;

        var th_html = "";
        _this.active_user_metadata.lead_data_cols.forEach((column_info_obj) => {
            if (column_info_obj.selected == false) return;
            var name = column_info_obj.name;
            var display_name = column_info_obj.display_name;
            th_html += '<th name="' + name + '">' + display_name + '</th>'
        });

        var thead_html = [
            '<thead>',
            '<tr>',
            th_html,
            '</tr>',
            '</thead>',
        ].join('');

        _this.table.innerHTML = thead_html;
    }

    initialize_body() {
        var _this = this;

        var sandbox_user_data_list = this.get_rows();

        _this.data_table_obj = $(_this.table).DataTable({
            "data": sandbox_user_data_list,
            "ordering": false,
            "bPaginate": false,
            "bInfo": false,
            "bLengthChange": false,
            "searching": false,
            'columnDefs': [{
                "targets": 0,
                "className": "text-left",
                "width": "20%"
            },
            ],

            initComplete: function (settings) {
                _this.apply_table_pagination();
            },
            createdRow: function (row, data, dataIndex) {
                row.setAttribute("sandbox_user_id", _this.sandbox_user_data[dataIndex].sandbox_user_id);
            },
        });

        const today_date = new Date()
        const tomorrow_date = new Date(today_date)
        tomorrow_date.setDate(tomorrow_date.getDate() + 1)
        $('.cobrowse-sandbox-extend-date').datepicker({
            startDate: tomorrow_date,
            dateFormat: "dd/mm/yy",
            changeMonth: true,
            changeYear: true,
            autoclose: true,
            dayNamesMin: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
        });
    }

    apply_table_pagination() {
        var _this = this;
        if(_this.sandbox_user_data.length == 0) {
            _this.pagination_container.innerHTML = "";
            return;
        }

        var container = _this.pagination_container;
        var metadata = _this.pagination_metadata;
        var onclick_handler = _this.add_filter_and_fetch_data;
        _this.apply_pagination(container, metadata, onclick_handler, _this);
    }

    update_url_with_filters(filters) {
        var key_value = "";
        for (var filter_key in filters) {
            var filter_data = filters[filter_key];
            for (var index = 0; index < filter_data.length; index++) {
                key_value += filter_key + "=" + filter_data[index] + "&";
            }
        }

        var newurl = window.location.protocol + "//" + window.location.host + window.location.pathname + '?' + key_value;
        window.history.pushState({ path: newurl }, '', newurl);
    }

    add_filter_and_fetch_data(key, value, target_obj = null) {
        var _this = this;
        if (target_obj) {
            _this = target_obj;
        }

        var filters = get_url_multiple_vars();
        if (key == "page") {
            filters.page = [value];
        }

        _this.update_url_with_filters(filters);
        _this.fetch_active_sandbox_users();
    }

    fetch_active_sandbox_users(selected_date_filter, checked_status, start_date, end_date) {
        var _this = this;

        var scroll_pos = document.getElementById('content-wrapper').scrollTop;
        var filters = get_url_multiple_vars();

        var request_params = {
            'page': ((filters["page"] && filters["page"][0]) || 1),
        };

        var json_params = JSON.stringify(request_params);
        var encrypted_data = easyassist_custom_encrypt(json_params);
        encrypted_data = {
            "Request": encrypted_data
        };
        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/easy-assist/sandbox-user/get-all-users/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                var response = JSON.parse(this.responseText);
                response = easyassist_custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    _this.pagination_metadata = response.pagination_metadata;
                    _this.set_sandbox_user_data(response.active_sandbox_users);
                    document.getElementById('content-wrapper').scrollTop = scroll_pos;
                }
            }
        }
        xhttp.send(params);
    }

    set_sandbox_user_data(sandbox_user_data) {
        var _this = this;
        if (sandbox_user_data) {
            _this.sandbox_user_data = sandbox_user_data;
            _this.data_checklist.sandbox_user_data = true;
        }

        _this.check_and_initialize_table();
    }

    check_and_initialize_table() {
        var _this = this;

        if (_this.data_checklist.sandbox_user_data == false) return false;

        _this.initialize_table();
    }

    get_row_html(name, sandbox_user_obj) {
        var _this = this;

        var data = sandbox_user_obj[name];
        if(data == null || data == undefined) {
            data = "-";
        }
        var sandbox_user_id = sandbox_user_obj.sandbox_user_id;

        var html = "";
        switch (name) {
            case "username":
                var data = sandbox_user_obj.email_id;
                if(data == null || data == undefined) {
                    data = "-";
                }
                html = data;
                break;

            case "expire_date":
                if(sandbox_user_obj.is_expiry_time_passed) {
                    html = `<div class="cobrowse-sandbox-expired-text">${data}</div>`;
                } else {
                    html = `<div class="cobrowse-sandbox-not-expired-text">${data}</div>`;
                }
                break;

            case "create_datetime":
                html = data;
                break;

            case "action":
                html = `
                <div class="text-md-center edit-delete-btn-class">
                    <a title="" style="cursor: pointer; margin-right: 1em;" class="sandbox-user-edit-btn">
                        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M13.2692 0.730772C14.2436 1.70513 14.2436 3.28489 13.2692 4.25925L4.92447 12.604C4.73142 12.7971 4.49134 12.9364 4.22794 13.0082L0.661097 13.981C0.270732 14.0875 -0.0874597 13.7293 0.0190035 13.3389L0.99178 9.77206C1.06361 9.50867 1.20294 9.26858 1.39599 9.07553L9.74075 0.730772C10.7151 -0.243591 12.2949 -0.243591 13.2692 0.730772ZM9.06478 2.88586L2.13552 9.81506C2.07117 9.87941 2.02473 9.95944 2.00078 10.0472L1.26879 12.7312L3.95276 11.9992C4.04056 11.9753 4.12059 11.9288 4.18494 11.8645L11.114 4.93504L9.06478 2.88586ZM10.4803 1.4703L9.80385 2.1461L11.853 4.19597L12.5297 3.51972C13.0956 2.95379 13.0956 2.03623 12.5297 1.4703C11.9638 0.904373 11.0462 0.904373 10.4803 1.4703Z"></path>
                        </svg>
                    </a>
                    <a style="cursor: pointer; margin-right: 1em;">
                        <svg width="14" height="16" viewBox="0 0 14 16" fill="none" xmlns="http://www.w3.org/2000/svg" class="sandbox-user-delete-btn">
                            <path d="M7 0C8.40298 0 9.54889 1.05927 9.62136 2.39215L9.625 2.52632H13.475C13.7649 2.52632 14 2.75253 14 3.03158C14 3.28737 13.8025 3.49877 13.5462 3.53223L13.475 3.53684H12.7337L11.8798 13.6779C11.7693 14.9896 10.6309 16 9.26338 16H4.73662C3.36913 16 2.23072 14.9896 2.12021 13.6779L1.2656 3.53684H0.525C0.259213 3.53684 0.0395562 3.34676 0.0047925 3.10014L0 3.03158C0 2.77578 0.197508 2.56438 0.453761 2.53093L0.525 2.52632H4.375C4.375 1.13107 5.55025 0 7 0ZM11.6807 3.53684H2.31929L3.16677 13.5962C3.23308 14.3832 3.91613 14.9895 4.73662 14.9895H9.26338C10.0839 14.9895 10.7669 14.3832 10.8332 13.5962L11.6807 3.53684ZM5.425 6.06316C5.69079 6.06316 5.91044 6.25324 5.94521 6.49986L5.95 6.56842V11.9579C5.95 12.2369 5.71495 12.4632 5.425 12.4632C5.15921 12.4632 4.93956 12.2731 4.90479 12.0265L4.9 11.9579V6.56842C4.9 6.28937 5.13505 6.06316 5.425 6.06316ZM8.575 6.06316C8.84079 6.06316 9.06044 6.25324 9.09521 6.49986L9.1 6.56842V11.9579C9.1 12.2369 8.86495 12.4632 8.575 12.4632C8.30921 12.4632 8.08956 12.2731 8.05479 12.0265L8.05 11.9579V6.56842C8.05 6.28937 8.28505 6.06316 8.575 6.06316ZM7 1.01053C6.1664 1.01053 5.48405 1.63379 5.42863 2.42254L5.425 2.52632H8.575L8.57137 2.42254C8.51595 1.63379 7.8336 1.01053 7 1.01053Z" fill="#EE2525"></path>
                        </svg>
                    </a>
                </div>`;
                break;

            case "extend":
                let expire_date_obj = new Date(sandbox_user_obj.expire_date);
                let formatted_date = null;
                try {
                    formatted_date = expire_date_obj.toLocaleString().split(",")[0];
                } catch(err) {}

                html = `
                <div class="text-md-center cobrowse-sandbox-extend-btn-wrapper">
                    <input type="text" style="display:none" id="${sandbox_user_id}" class="datepicker cobrowse-sandbox-extend-date" value="${formatted_date}">
                    <button type="button" class="cobrowse-sandbox-extend-btn">Extend</button>
                </div>`;

                break;

            default:
                html = "-";
                console.log("Error: unknown column")
                break;
        }
        return html;
    }

    get_row(sandbox_user_obj) {
        var _this = this;

        var sandbox_user_data_list = [];

        _this.active_user_metadata.lead_data_cols.forEach((column_info_obj) => {
            try {
                if (column_info_obj.selected == false) return;
                var name = column_info_obj.name;
                sandbox_user_data_list.push(_this.get_row_html(name, sandbox_user_obj));
            } catch (err) {
                console.log("ERROR get_row on adding row data of column : ", column_info_obj);
            }
        });

        return sandbox_user_data_list;
    }

    get_rows() {
        var _this = this;
        var sandbox_user_data_list = [];
        _this.sandbox_user_data.forEach((sandbox_user_obj) => {
            sandbox_user_data_list.push(_this.get_row(sandbox_user_obj));
        })
        return sandbox_user_data_list;
    }

    add_event_listeners_in_rows(container = null) {
        var _this = this;
        if (container == null) container = _this.table;
    }

    add_event_listeners() {
        var _this = this;

        var sandbox_user_delete_btns = _this.table_container.querySelectorAll(".sandbox-user-delete-btn");
        sandbox_user_delete_btns.forEach(function(sandbox_user_delete_btn) {
            let table_row = sandbox_user_delete_btn.closest("tr");
            let sandbox_user_id = table_row.getAttribute("sandbox_user_id");

            sandbox_user_delete_btn.onclick = function() {
                show_delete_sandbox_user_modal(sandbox_user_id);
            }
        });

        var sandbox_user_edit_btns = _this.table_container.querySelectorAll(".sandbox-user-edit-btn");
        sandbox_user_edit_btns.forEach(function(sandbox_user_edit_btn) {
            let table_row = sandbox_user_edit_btn.closest("tr");
            let sandbox_user_id = table_row.getAttribute("sandbox_user_id");

            sandbox_user_edit_btn.onclick = function() {
                show_edit_sandbox_user_modal(sandbox_user_id);
            }
        });

        var sandbox_user_extend_btns = _this.table_container.querySelectorAll(".cobrowse-sandbox-extend-btn");
        sandbox_user_extend_btns.forEach(function(sandbox_user_extend_btns) {
            let table_row = sandbox_user_extend_btns.closest("tr");
            let sandbox_user_id = table_row.getAttribute("sandbox_user_id");

            sandbox_user_extend_btns.onclick = function() {
                $("#"+sandbox_user_id).show().focus().hide();
            }
        });

        var expiretime_extend_date_elements = document.querySelectorAll(".cobrowse-sandbox-extend-date");
        expiretime_extend_date_elements.forEach(function(expiretime_extend_date_element) {
            expiretime_extend_date_element.onchange = function() {
                let table_row = expiretime_extend_date_element.closest("tr");
                let sandbox_user_id = table_row.getAttribute("sandbox_user_id");
                let changed_date = expiretime_extend_date_element.value;
                update_sandbox_user_expire_date(sandbox_user_id, changed_date);
            }
        });
    }

    get_table_meta_data() {
        var _this = this;
        var lead_data_cols = _this.get_default_meta_data();
        return lead_data_cols;
    }

    get_default_meta_data() {
        var lead_data_cols = [
            ['username', 'Username', true],
            ['create_datetime', 'Created On', true],
            ['expire_date', 'Will Expire On', true],
            ['extend', '', true],
            ['action', '', true],
        ]

        var default_lead_data_cols = [];
        lead_data_cols.forEach((lead_data_col, index) => {
            default_lead_data_cols.push({
                name: lead_data_col[0],
                display_name: lead_data_col[1],
                index: index,
                selected: lead_data_col[2],
            });
        });
        return default_lead_data_cols;
    }
}

function initialize_active_sandbox_user_table() {
    if (window.location.pathname.indexOf("/easy-assist/sandbox-user/creds") != 0) {
        return;
    }

    var sandbox_user_table_container = document.querySelector("#sandbox_user_table_container");
    var pagination_container = document.getElementById("sandbox_user_table_pagination_div");

    window.ACTIVE_SANDBOX_USER_TABLE = new ActiveSandboxUserTable(
        sandbox_user_table_container, pagination_container);
}

function show_delete_sandbox_user_modal(sandbox_user_id) {
    document.getElementById("delete-sandbox-user-error-element").innerHTML = "";
    document.getElementById("delete-sandbox-user-id").value = sandbox_user_id;
    $("#modal-sandbox-delete-user").modal("show");
}

function hide_delete_sandbox_user_modal() {
    document.getElementById("delete-sandbox-user-id").value = "";
    $("#modal-sandbox-delete-user").modal("hide");
}

function delete_sandbox_user(element) {
    let error_message_element = document.getElementById("delete-sandbox-user-error-element");
    error_message_element.innerHTML = "";

    let sandbox_user_id = document.getElementById("delete-sandbox-user-id").value;

    if(sandbox_user_id == "" || sandbox_user_id == null) {
        error_message_element.innerHTML = "Please select a valid sandbox user";
        error_message_element.style.color = "red";
        return;
    }

    let request_params = {
        "sandbox_user_id": sandbox_user_id,
    };

    let json_params = JSON.stringify(request_params);

    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Deleting...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/sandbox-user/delete/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                error_message_element.style.color = "green";
                error_message_element.innerHTML = "Sandbox User deleted successfully.";

                hide_delete_sandbox_user_modal();
                window.ACTIVE_SANDBOX_USER_TABLE.fetch_active_sandbox_users();

            } else if (response.status == 301) {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = "Sandbox user does not exist.";
            } else {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = "Something went wrong. Please try again.";
            }
        }
        element.innerHTML = "Delete";
    }
    xhttp.send(params);
}

function show_edit_sandbox_user_modal(sandbox_user_id) {

    if(sandbox_user_id == "" || sandbox_user_id == null) {
        show_easyassist_toast("Please select a valid sandbox user");
        return;
    }

    let request_params = {
        "sandbox_user_id": sandbox_user_id,
    };

    let json_params = JSON.stringify(request_params);

    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/sandbox-user/get-data/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                let data = response.sandbox_user_data;

                update_edit_user_modal_field(data);
                $("#modal-sandbox-edit-user").modal("show");

            } else if(response.status == 301) {
                show_easyassist_toast("Sandbox user does not exist");
                window.ACTIVE_SANDBOX_USER_TABLE.fetch_active_sandbox_users();
            } else {
                show_easyassist_toast("Something went wrong. Please try again");
            }
        }
    }
    xhttp.send(params);
}

function update_edit_user_modal_field(data) {
    document.getElementById("edit-sandbox-user-email-id").value = data.email_id;
    document.getElementById("edit-sandbox-user-password").value = data.sandbox_user_password;
    if(data.enable_cobrowsing) {
        if(!document.getElementById("edit-cobrowsing-enabled").checked) {
            document.getElementById("edit-cobrowsing-enabled").click();    
        }
    }

    document.getElementById("edit-inbound-enabled").checked = data.enable_inbound;
    document.getElementById("edit-outbound-enabled").checked = data.enable_outbound;
    document.getElementById("edit-reverse-cobrowsing-enabled").checked = data.enable_reverse_cobrowsing;
    document.getElementById("edit-video-meeting-enabled").checked = data.enable_video_meeting;
    document.getElementById("edit-error-element").innerHTML = "";
}

function hide_edit_sandbox_user_modal() {
    $("#modal-sandbox-edit-user").modal("hide");
}


function save_edited_sandbox_user_credentials(element) {
    let error_message_element = document.getElementById("edit-error-element");
    error_message_element.innerHTML = "";

    let email_id = document.getElementById("edit-sandbox-user-email-id").value;
    let password = document.getElementById("edit-sandbox-user-password").value;
    let cobrowsing_enabled = document.getElementById("edit-cobrowsing-enabled").checked;
    let inbound_enabled = document.getElementById("edit-inbound-enabled").checked;
    let outbound_enabled = document.getElementById("edit-outbound-enabled").checked;
    let reverse_cobrowsing_enabled = document.getElementById("edit-reverse-cobrowsing-enabled").checked;
    let video_meeting_enabled = document.getElementById("edit-video-meeting-enabled").checked;

    if(inbound_enabled || outbound_enabled) {
        reverse_cobrowsing_enabled = false;
    }

    if(reverse_cobrowsing_enabled) {
        inbound_enabled = false;
        outbound_enabled = false;
    }

    if(!cobrowsing_enabled && !video_meeting_enabled) {
        error_message_element.innerHTML = "Please select at least one of the option";
        error_message_element.style.color = "red";
        return;
    }

    if(cobrowsing_enabled) {
        if(!inbound_enabled && !outbound_enabled && !reverse_cobrowsing_enabled) {
            error_message_element.innerHTML = "Please select at least one of the cobrowsing options";
            error_message_element.style.color = "red";
            return;
        }
    }

    const regEmail = /^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/;
    if (!regEmail.test(email_id)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter valid email id";
        return;
    }

    const regexPassword = /^(?=.*[A-Z])(?=.*[!@#$&*])(?=.*\d)(?=.*[a-z]).{8,}/;
    if (!regexPassword.test(password)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please Enter valid Password";
        return;
    }

    let request_params = {
        "email_id": email_id,
        "password": password,
        "cobrowsing_enabled": cobrowsing_enabled,
        "inbound_enabled": inbound_enabled,
        "outbound_enabled": outbound_enabled,
        "reverse_cobrowsing_enabled": reverse_cobrowsing_enabled,
        "video_meeting_enabled": video_meeting_enabled,
    };

    let json_params = JSON.stringify(request_params);

    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/sandbox-user/save/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                error_message_element.style.color = "green";
                error_message_element.innerHTML = "Saved successfully.";

                hide_edit_sandbox_user_modal();
                window.ACTIVE_SANDBOX_USER_TABLE.fetch_active_sandbox_users();

            } else if (response.status == 301) {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = "Sandbox user does not exist.";
            } else {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = "Something went wrong. Please try again.";
            }
        }
        element.innerHTML = "Save";
    }
    xhttp.send(params);
}

function update_sandbox_user_expire_date(sandbox_user_id, expire_date) {
    let request_params = {
        "sandbox_user_id": sandbox_user_id,
        "expire_date": expire_date,
    };

    let json_params = JSON.stringify(request_params);

    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/sandbox-user/update-expire-date/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                show_easyassist_toast("Expire Date updated successfully");
                window.ACTIVE_SANDBOX_USER_TABLE.fetch_active_sandbox_users();

            } else if(response.status == 301) {
                show_easyassist_toast("Sandbox user does not exist");
            } else {
                show_easyassist_toast("Something went wrong. Please try again");
            }
        }
    }
    xhttp.send(params);
}

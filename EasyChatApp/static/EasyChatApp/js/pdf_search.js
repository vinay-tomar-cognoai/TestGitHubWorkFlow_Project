$(document).ready(document_ready);
window.addEventListener('popstate', window_pop_state_listener)

function document_ready() {
    disable_future_date()
    $('.datepicker').datepicker({
        endDate: '+0d',
    });

    
    // $('.pdf-search-tooltip').tooltip();

    // $(".positive_numeric").on("keypress input", function (event) {
    //     var keyCode = event.which;

    //     if ((keyCode != 8 || keyCode == 32) && (keyCode < 48 || keyCode > 57)) {
    //         return false;
    //     }

    //     var self = $(this);
    //     self.val(self.val().replace(/\D/g, ""));
    // });   
    
    // Initialize PDF Dashboard table
    initialize_active_pdf_table();

    refresh_data_dynamically();
    
}

function change_date_format_original(date)
{
    var dateParts = date.split("-");
    date = dateParts[2]+"-"+dateParts[1]+"-"+dateParts[0];  
    return date.trim();
}

function is_valid_date(date) {
    var date2 = change_date_format_original(date)
    date = new Date(date);
    date2 = new Date(date2);
    var check_date = date instanceof Date && !isNaN(date)
    var check_date2 =date2 instanceof Date && !isNaN(date2)
    return check_date || check_date2;
}

function get_csrfmiddlewaretoken() {
    let token = $('input[name="csrfmiddlewaretoken"]').val();
    return token;
}

function window_pop_state_listener() {
    if (window.ACTIVE_PDF_TABLE) {
        window.ACTIVE_PDF_TABLE.fetch_active_pdf();
    }
}
function disable_future_date(){
    var dtToday = new Date();

    var month = dtToday.getMonth() + 1;
    var day = dtToday.getDate();
    var year = dtToday.getFullYear();
    if(month < 10)
        month = '0' + month.toString();
    if(day < 10)
        day = '0' + day.toString();

    var maxDate = year + '-' + month + '-' + day;
    $("[type='date']").attr("max", maxDate)
}
function get_url_vars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m, key, value) {
        vars[key] = value;
    });
    return vars;
}

function show_pdf_search_toast(message) {
    M.toast({
        "html": message
    });
}

/* Campaign Filter Functions */

var applied_filter = []

function show_custom_date() {
    if (document.getElementById('pdf_search_overview_custom_date_btn').checked) {
        document.getElementById("analytics-custom-date-select-area").style.display = "block";
    } else {
        document.getElementById("analytics-custom-date-select-area").style.display = "none";
    }
}

function apply_pdf_search_filter() {
    let filters = get_url_multiple_vars();
    var selected_date_filter = $("input[type='radio'][name='date-range-filter-btn']:checked").val();
    var status_elems = document.getElementsByName('filter_pdf_search_status');

    if (!selected_date_filter) {
        show_pdf_search_toast('Please select date range');
        return;
    }

    var start_date, end_date;
    if (selected_date_filter == '4') {
        start_date = document.getElementById('filter_custom_start_date').value;

        if (!start_date) {
            show_pdf_search_toast('Please select start date');
            return;
        }

        end_date = document.getElementById('filter_custom_end_date').value;

        if (!end_date) {
            show_pdf_search_toast('Please select end date');
            return;
        }

        if(Date.parse(start_date) > Date.parse(end_date)){
            show_pdf_search_toast('Start date cannot be less than end date.')
            return;
        }
        filters["start_date"] = [start_date];
        filters["end_date"] = [end_date];
    } else {
        filters["start_date"] = [];
        filters["end_date"] = [];
    }

    var pdf_search_status = []
    for (elem of status_elems) {
        if (elem.checked) pdf_search_status.push(elem.value);
    }

    filters["selected_date_filter"] = [selected_date_filter]
    filters["pdf_search_status"] = pdf_search_status;

    window.ACTIVE_PDF_TABLE.update_url_with_filters(filters);
    window.ACTIVE_PDF_TABLE.fetch_active_pdf();
}

function clear_filter() {
    document.getElementById('pdf_search_overview_week').checked = true;
    document.getElementById('filter_custom_start_date').value = DEFAULT_START_DATE;
    document.getElementById('filter_custom_end_date').value = DEFAULT_END_DATE;
    document.getElementById('analytics-custom-date-select-area').style.display = 'none';

    var status_elems = document.getElementsByName('filter_pdf_search_status');
    for (elem of status_elems) {
        elem.checked = false;
    }

    let filters = get_url_multiple_vars();
    let updated_filters = {
        'bot_pk': filters['bot_pk'],
    };
    window.ACTIVE_PDF_TABLE.update_url_with_filters(updated_filters);
    window.ACTIVE_PDF_TABLE.fetch_active_pdf();
}

function check_select_date_range(el, export_type) {
    var selected_range = el.value;

    if(selected_range == '4') {
        document.getElementById('from-date-div-'+export_type).style.display = 'block';
        document.getElementById('to-date-div-'+export_type).style.display = 'block';
    } else {
        document.getElementById('from-date-div-'+export_type).style.display = 'none';
        document.getElementById('to-date-div-'+export_type).style.display = 'none';
    }

    if (selected_range != 0) {
        document.getElementById('email-id-div-'+export_type).style.display = 'block';
    } else {
        document.getElementById('email-id-div-'+export_type).style.display = 'none';
    }
}

function update_applied_filter() {

    function update_status(){
        $("[name='filter_pdf_search_status']").prop("checked", false);
        if(filters.pdf_search_status && filters.pdf_search_status.length > 0) {
            let status_elems = document.getElementsByName('filter_pdf_search_status');
            for (let elem of status_elems) {
                if(filters.pdf_search_status.indexOf(elem.value) >= 0){
                    elem.checked = true;
                }
            }
        }
    }

    function update_date_range(){
        if("start_date" in filters){
            document.getElementById('filter_custom_start_date').value = filters["start_date"][0];
        }

        if("end_date" in filters){
            document.getElementById('filter_custom_end_date').value = filters["end_date"][0];
        }

        if("selected_date_filter" in filters){
            let selected_date_filter = filters["selected_date_filter"][0];

            document.getElementById('pdf_search_overview_week').checked = false;
            document.getElementById('pdf_search_overview_month').checked = false;
            document.getElementById('pdf_search_overview_three_month').checked = false;
            document.getElementById('pdf_search_overview_custom_date_btn').checked = false;
            document.getElementById('pdf_search_overview_beg').checked = false;

            if(selected_date_filter === "4"){
                document.getElementById('pdf_search_overview_custom_date_btn').checked = true;
                document.getElementById('analytics-custom-date-select-area').style.display = 'block';
            } else {
                if(selected_date_filter === "1") document.getElementById('pdf_search_overview_week').checked = true;
                if(selected_date_filter === "2") document.getElementById('pdf_search_overview_month').checked = true;
                if(selected_date_filter === "3") document.getElementById('pdf_search_overview_three_month').checked = true;
                if(selected_date_filter === "5") document.getElementById('pdf_search_overview_beg').checked = true;
                document.getElementById('analytics-custom-date-select-area').style.display = 'none';
            }
        }
    }

    let filters = get_url_multiple_vars();
    update_date_range();
    update_status();

    add_applied_filters_chips();
}

function revome_selected_filter_chip(el) {
    var selected_filter_parameters = $(el).closest('.filter-parameter-column')[0];
    var removed_value = $(el).closest('.filter-chip').find('span').html();
    var filter_key = selected_filter_parameters.getAttribute('filter-key');
    var filter_data = selected_filter_parameters.getAttribute('filter-data');
    filter_data = JSON.parse(filter_data);

    var new_filter_data = [];
    for (var idx = 0; idx < filter_data.length; idx++) {
        if (filter_data[idx] == removed_value) {
            continue;
        }
        new_filter_data.push(filter_data[idx]);
    }

    applied_filter_key_value_map[filter_key] = new_filter_data;

    if (filter_key == "title") {
        custom_title_filter_dropdown.update_value(new_filter_data);
    } else if (filter_key == "agent") {
        $("#selected-agent-filter").multiselect('deselect', removed_value);
    } else if (filter_key == "action") {
        custom_action_filter_dropdown.update_value(new_filter_data);
    }

    selected_filter_parameters.setAttribute('filter-data', JSON.stringify(new_filter_data));
    if (new_filter_data.length == 0) {
        $(selected_filter_parameters).find('.remove-filter-row-btn').click();
    } else {
        el.parentElement.remove();
    }
    var filter_chip_html = generate_filter_chips(filter_key, new_filter_data, true);
    selected_filter_parameters.getElementsByClassName('filter-chip-column')[0].innerHTML = filter_chip_html;
}

function add_applied_filters_chips() {

    function get_filter_key_display_name(filter_key){
        let display_name = filter_key;
        if(filter_key == "start_date") {
            display_name = "Start Date";
        } else if (filter_key == "end_date") {
            display_name = "End Date";
        } else if (filter_key == "pdf_search_status") {
            display_name = "Status";
        } else if (filter_key == "selected_date_filter") {
            display_name = "Date Range";
        }
        return display_name;
    }

    function get_valid_value_display_name(filter_value) {
        let display_name = filter_value;
        if(filter_value == "active") {
            display_name = "Active";
        } else if(filter_value == "inactive") {
            display_name = "Inactive";
        } else if(filter_value == "indexing") {
            display_name = "Indexing";
        } else if(filter_value == "not_indexed") {
            display_name = "Not Indexed";
        } else if(filter_value == "indexed") {
            display_name = "Indexed";
        }
        return display_name;
    }

    var url_params = get_url_multiple_vars();
    var params_keys = Object.keys(url_params);
    is_filter_applied = false;
    var filter_html = "";

    for (var idx = 0; idx < params_keys.length; idx++) {
        var filter_key = params_keys[idx];

        if (["page", "bot_pk"].indexOf(filter_key) >= 0) {
            continue;
        }

        var display_name = get_filter_key_display_name(filter_key);

        is_filter_applied = true;

        var filter_values = url_params[filter_key];

        var html_filter_chip = "";

        for (var index = 0; index < filter_values.length; index++) {
            var value_display_name = decodeURI(filter_values[index]);

            value_display_name = get_valid_value_display_name(value_display_name);

            var input_element = document.querySelector("#pdf-search-filter-modal [filter_key='" + filter_key + "'][value='" + decodeURI(filter_values[index]) + "']")

            if(input_element){
                value_display_name = input_element.getAttribute("display_name");
            }

            html_filter_chip += `
                <div class="filter-chip">
                    <span>${value_display_name}</span>
                    <button class="filter-chip-remove-icon" onclick="remove_applied_filter_by_value('${decodeURI(filter_values[index])}', '${filter_key}');">
                        <svg width="9" height="9" viewBox="0 0 9 9" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M5.38146 4.50006L8.06896 1.8188C8.18665 1.70112 8.25276 1.54149 8.25276 1.37505C8.25276 1.20862 8.18665 1.04899 8.06896 0.931305C7.95127 0.813615 7.79165 0.747498 7.62521 0.747498C7.45877 0.747498 7.29915 0.813615 7.18146 0.931305L4.50021 3.61881L1.81896 0.931305C1.70127 0.813615 1.54164 0.747498 1.37521 0.747498C1.20877 0.747498 1.04915 0.813615 0.931456 0.931305C0.813766 1.04899 0.747649 1.20862 0.747649 1.37505C0.747649 1.54149 0.813766 1.70112 0.931456 1.8188L3.61896 4.50006L0.931456 7.18131C0.872876 7.23941 0.826379 7.30853 0.794649 7.38469C0.762919 7.46086 0.746582 7.54255 0.746582 7.62506C0.746582 7.70756 0.762919 7.78925 0.794649 7.86542C0.826379 7.94158 0.872876 8.0107 0.931456 8.0688C0.989558 8.12739 1.05868 8.17388 1.13485 8.20561C1.21101 8.23734 1.2927 8.25368 1.37521 8.25368C1.45771 8.25368 1.5394 8.23734 1.61557 8.20561C1.69173 8.17388 1.76085 8.12739 1.81896 8.0688L4.50021 5.38131L7.18146 8.0688C7.23956 8.12739 7.30868 8.17388 7.38485 8.20561C7.46101 8.23734 7.5427 8.25368 7.62521 8.25368C7.70771 8.25368 7.78941 8.23734 7.86557 8.20561C7.94173 8.17388 8.01085 8.12739 8.06896 8.0688C8.12754 8.0107 8.17403 7.94158 8.20576 7.86542C8.23749 7.78925 8.25383 7.70756 8.25383 7.62506C8.25383 7.54255 8.23749 7.46086 8.20576 7.38469C8.17403 7.30853 8.12754 7.23941 8.06896 7.18131L5.38146 4.50006Z" fill="#0254D7"/>
                        </svg>
                    </button>
                </div>`;
        }

        filter_html += `
            <div class="col-md-12 col-sm-12 filter-result-item">
                <div class="filter-name-text">
                    <span>${display_name}</span>
                    <button class="filter-remove-icon filter-show-on-mobile" onclick="remove_applied_filter('${filter_key}');">
                        <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M1.5 1.5L10.5 10.5M1.5 10.5L10.5 1.5L1.5 10.5Z" stroke="#DC0000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path>
                        </svg>
                    </button>
                </div>
                <div class="chip-area">
                    ${html_filter_chip}
                </div>
                <button class="filter-remove-icon filter-hide-on-mobile" style="background: transparent !important;" onclick="remove_applied_filter('${filter_key}');">
                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M1.5 1.5L10.5 10.5M1.5 10.5L10.5 1.5L1.5 10.5Z" stroke="#DC0000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path>
                    </svg>
                </button>
            </div>`;
    }

    filter_html += `
        <div class="col-md-12 col-sm-12 mb-2 filter-padding-0" style="text-align: right;">
            <button class="clear-all-filter-btn" type="button" onclick="clear_filter()">Clear All</button>
        </div>`;

    if (is_filter_applied) {
        document.getElementById("applied-filter-result-container").innerHTML = filter_html;
        document.getElementById("applied-filter-div").style.display = '';
    } else {
        document.getElementById("applied-filter-div").style.display = 'none';
    }
}

function remove_applied_filter(filter_key) {
    var url_params = get_url_multiple_vars();
    var params_keys = Object.keys(url_params);

    var key_value = "";
    for (var idx = 0; idx < params_keys.length; idx++) {
        if (params_keys[idx] == filter_key) {
            url_params[params_keys[idx]] = [];
            continue;
        }
    }

    window.ACTIVE_PDF_TABLE.update_url_with_filters(url_params);
    window.ACTIVE_PDF_TABLE.fetch_active_pdf();
}

function remove_applied_filter_by_value(target_filter_value, filter_key) {
    var url_params = get_url_multiple_vars();
    var params_keys = Object.keys(url_params);
    console.log(filter_key);
    console.log(url_params);

    for (var idx = 0; idx < params_keys.length; idx++) {
        if (params_keys[idx] == filter_key) {
            var filter_values = url_params[params_keys[idx]];
            var new_filter_values = [];
            for (var index = 0; index < filter_values.length; index++) {
                var filter_value = decodeURI(filter_values[index]);
                if (filter_value == target_filter_value) {
                    continue;
                }
                new_filter_values.push(filter_value);
            }
            console.log(new_filter_values);
            url_params[params_keys[idx]] = new_filter_values;
        }
    }

    window.ACTIVE_PDF_TABLE.update_url_with_filters(url_params);
    window.ACTIVE_PDF_TABLE.fetch_active_pdf();
}

function export_pdf_search_request(el) {
    var bot_id = get_url_multiple_vars()['bot_pk'][0];
    var error_message = document.getElementById('general-error-message');
    error_message.innerText = "";

    var start_date, end_date;
    request_date_type = document.getElementById('export-select-date-range').value;

    if (request_date_type == '0' || request_date_type == "") {
        error_message.innerHTML = 'Please select date range';
        return;
    } else {
        error_message.innerHTML = '';
    }

    if (request_date_type == '4') {
        start_date = document.getElementById('export_custom_start_date').value;

        if (!start_date) {
            error_message.innerHTML = 'Please select a start date';
            return;
        } else {
            error_message.innerHTML = '';
        }

        if (!is_valid_date(start_date)) {
            error_message.innerHTML = 'Please select valid start date';
            return;
        } else {
            error_message.innerHTML = '';
        }

        end_date = document.getElementById('export_custom_end_date').value;

        if (!end_date) {
            error_message.innerHTML = 'Please select a end date';
            return;
        } else {
            error_message.innerHTML = '';
        }

        if (!is_valid_date(end_date)) {
            error_message.innerHTML = 'Please select valid end date';
            return;
        } else {
            error_message.innerHTML = '';
        }

        if(Date.parse(start_date) > Date.parse(end_date)){
            error_message.innerHTML = 'Start date must be less than end date.';
            return;
        } else {
            error_message.innerHTML = '';
        }

        start_date = change_date_format_original(start_date);
        end_date = change_date_format_original(end_date);
    }

    var email_id = document.getElementById('export-email-id').value;

    if (email_id == '') {
        document.getElementById('general-error-message').innerHTML = 'Please enter your Email ID';
        return;
    } else {
        document.getElementById('general-error-message').innerHTML = '';
    }

    if (!validate_email(email_id)) {
        document.getElementById('general-error-message').innerHTML = 'Please enter valid Email ID';
        return;
    } else {
        document.getElementById('general-error-message').innerHTML = '';
    }

    send_export_request_to_server(bot_id, email_id, request_date_type, start_date, end_date);
}

function send_export_request_to_server(bot_id, email_id, request_date_type, start_date, end_date) {
    var request_params = {
        'bot_id': bot_id,
        'email_id': email_id,
        'start_date': start_date,
        'end_date': end_date,
        'request_date_type': request_date_type,
    };

    var json_params = JSON.stringify(request_params);
    var encrypted_data = EncryptVariable(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/chat/bot/export-pdf-search-report/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                show_pdf_search_toast('You will receive the pdf search report data dump on the above email ID within 24 hours.');

                $('#export-pdf-search-modal').modal('close');

            } else {
                show_pdf_search_toast(response.message);
            }
        }
    }
    xhttp.send(params);
}

function refresh_data_dynamically() {
    setInterval(function () {
        if(document.getElementById('pdf-search-bar').value.trim() == "")
        {
            window.ACTIVE_PDF_TABLE.fetch_active_pdf();
        }
    }, 10000);
}

class PDFSearcher {
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
            html += `
                <li class="page-item">
                    <a class="page-link previous_button" data-page="${metadata.previous_page_number}" href="javascript:void(0)" aria-label="Previous">
                    <span class="sr-only">Previous</span>
                    </a>
                </li>`;
        } else {
            html += `
                <li class="page-item disabled">
                    <a class="page-link previous_button" href="javascript:void(0)" aria-label="Previous">
                    <span class="sr-only">Previous</span>
                    </a>
                </li>`;
        }

        if ((metadata.number - 4) > 1) {
            html += `
                <li class="page-item">
                    <a class="page-link" data-page="${(metadata.number - 5)}" href="javascript:void(0)">&hellip;</a>
                </li>`;
        }

        for (var index = metadata.page_range[0]; index < metadata.page_range[1]; index++) {
            if (metadata.number == index) {
                html += `
                    <li class="active purple darken-3 page-item">
                        <a data-page="${index}" href="javascript:void(0)" class="page-link">${index}</a>
                    </li>`;
            } else if (index > (metadata.number - 5) && index < (metadata.number + 5)) {
                html += `
                    <li class="page-item">
                        <a href="javascript:void(0)" data-page="${index}" class="page-link">${index}</a>
                    </li>`;
            }
        }

        if (metadata.num_pages > (metadata.number + 4)) {
            html += `
                <li class="page-item">
                    <a href="javascript:void(0)" data-page="${(metadata.number + 5)}" class="page-link">&hellip;</a>
                </li>`;
        }

        if (metadata.has_next) {
            html += `
                <li class="page-item">
                    <a class="page-link next_button" data-page="${metadata.next_page_number}" href="javascript:void(0)" aria-label="Previous">
                        <span class="sr-only">Next</span>
                    </a>
                </li>`;
        } else {
            html += `
                <li class="page-item disabled">
                    <a class="page-link next_button" href="javascript:void(0)" aria-label="Previous">
                        <span class="sr-only">Next</span>
                    </a>
                </li>`;
        }

        html = `
            <div class="col-md-6 col-sm-12 show-pagination-entry-container" filter_default_text='${filter_default_text}'>
                ${filter_default_text}
            </div>
            <div class="col-md-6 col-sm-12">
                <div class="d-flex justify-content-end">
                    <nav aria-label="Page navigation example">
                        <ul class="pagination">
                            ${html}
                        </ul>
                    </nav>
                </div>
            </div>`;

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

class ActivePDFTable extends PDFSearcher {
    constructor(table_container, searchbar_element, pagination_container) {
        super();
        this.table_container = table_container;
        this.table = null;
        this.options = {
            enable_select_rows: false,
        }

        this.active_user_metadata = {};
        this.pagination_container = pagination_container;
        this.searchbar_element = searchbar_element;

        this.data_checklist = {
            'pdf_data': false,
        };

        this.data_table_obj = null;
        this.init();
    }

    init() {
        var _this = this;
        _this.initialize_table_header_metadata();
        _this.initialize_lead_data_metadata_update_modal();
        _this.fetch_active_pdf();
    }

    initialize_table_header_metadata() {
        var _this = this;
        _this.active_user_metadata.lead_data_cols = _this.get_table_meta_data();
    }

    initialize_table() {
        var _this = this;

        _this.table_container.innerHTML = '<table class="dataTable highlight" id="pdf_search_table" width="100%" cellspacing="0" role="grid" style="width: 100%;"></table>';
        _this.table = _this.table_container.querySelector("table");

        if (!_this.table) return;
        if (_this.active_user_metadata.lead_data_cols.length == 0) return;
        if(_this.pdf_data.length == 0) {
            _this.options.enable_select_rows = false;
        }

        _this.initialize_head();
        _this.initialize_body();
        _this.add_event_listeners();
        _this.add_event_listeners_in_rows();
        _this.update_table_attribute([_this.table]);

        /*
            ------- saved for future reference -------
            $(_this.table).DataTable().clear().draw();
            $(_this.table).DataTable().destroy(true);
        */
    }

    initialize_head() {
        var _this = this;
        const { enable_select_rows } = _this.options;

        var th_html = "";
        _this.active_user_metadata.lead_data_cols.forEach((column_info_obj) => {
            if (column_info_obj.selected == false) return;
            var name = column_info_obj.name;
            var display_name = column_info_obj.display_name;
            th_html += '<th name="' + name + '">' + display_name + '</th>'
        });

        var select_rows_html = "";
        if (enable_select_rows) {
            select_rows_html = `
                <th>
                    <input type="checkbox" class="pdf_select_all_rows_cb" />
                </th>`;
        }

        var thead_html = `
            <thead>
                <tr>
                    ${select_rows_html}
                    ${th_html}
                </tr>
            </thead>`;

        _this.table.innerHTML = thead_html;
    }

    initialize_body() {
        var _this = this;
        var not_indexed_count =0;

        var pdf_data_list = this.get_rows();

        _this.data_table_obj = $(_this.table).DataTable({
            "data": pdf_data_list,
            "ordering": false,
            "bPaginate": false,
            "bInfo": false,
            "bLengthChange": false,
            "searching": true,
            'columnDefs': [{
                "targets": 0,
                "className": "text-left text-md-center",
                "width": "4%"
            },
            ],

            initComplete: function (settings) {
                $(_this.table).colResizable({
                    disable: true
                });
                $(_this.table).colResizable({
                    liveDrag: true,
                    minWidth: 100,
                    postbackSafe: true,
                });
                _this.apply_table_pagination();
                _this.show_filter_div();
                _this.add_filter_event_listener();
            },
            createdRow: function (row, data, dataIndex) {
                row.setAttribute("pdf_id", _this.pdf_data[dataIndex].pdf_id);
                row.setAttribute("status", _this.pdf_data[dataIndex].status);
                if(_this.pdf_data[dataIndex].status=="not_indexed"){
                    not_indexed_count++;
                }
                row.setAttribute("pdf_name",_this.pdf_data[dataIndex].name);
                row.setAttribute("important_pages",_this.pdf_data[dataIndex].important_pages);
                row.setAttribute("skipped_pages",_this.pdf_data[dataIndex].skipped_pages);
                row.setAttribute("file_path",_this.pdf_data[dataIndex].file_path);
            },
        });
        if(not_indexed_count > 0){
            show_start_indexing_btn();
        }
    }

    add_filter_event_listener(){
        var _this = this;

        // Event listener in searchbar element
        _this.searchbar_element.addEventListener("input", function(event){
            var value = event.target.value;

            if (!_this.data_table_obj) {
                return;
            }

            _this.data_table_obj.search(value).draw();

            var pagination_entry_container = _this.pagination_container.querySelector(".show-pagination-entry-container");

            if(pagination_entry_container){
                var showing_entry_count = _this.table.querySelectorAll("tbody tr[role='row']").length;
                var total_entry = _this.pagination_metadata.end_point - _this.pagination_metadata.start_point + 1;

                if(value.length != 0){
                    var text = "Showing " + showing_entry_count + " entries (filtered from " + total_entry + " total entries)";
                    pagination_entry_container.innerHTML = text;
                } else {
                    pagination_entry_container.innerHTML = pagination_entry_container.getAttribute("filter_default_text");
                }  
            }
        });
    }

    show_filter_div(){
        var _this = this;
        update_applied_filter();
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
        _this.fetch_active_pdf();
    }

    apply_table_pagination() {
        var _this = this;
        if(_this.pdf_data.length == 0) {
            _this.pagination_container.innerHTML = "";
            return;
        }

        var container = _this.pagination_container;
        var metadata = _this.pagination_metadata;
        var onclick_handler = _this.add_filter_and_fetch_data;
        _this.apply_pagination(container, metadata, onclick_handler, _this);
    }

    fetch_active_pdf() {
        var _this = this;

        // var scroll_pos = document.getElementById('content-wrapper').scrollTop;
        var filters = get_url_multiple_vars();

        var request_params = {
            'page': ((filters["page"] && filters["page"][0]) || 1),
            'bot_pk': filters["bot_pk"][0],
            'pdf_search_status': (filters['pdf_search_status'] || []),
            'selected_date_filter': ( (filters["selected_date_filter"] && filters["selected_date_filter"][0]) || ''),
            'start_date': ((filters["start_date"] && filters["start_date"][0]) || DEFAULT_START_DATE),
            'end_date': ((filters["end_date"] && filters["end_date"][0]) || DEFAULT_END_DATE),
        };

        var json_params = JSON.stringify(request_params);
        var encrypted_data = EncryptVariable(json_params);
        encrypted_data = {
            "Request": encrypted_data
        };
        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/chat/bot/get-active-pdf/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', $('input[name="csrfmiddlewaretoken"]').val());
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                var response = JSON.parse(this.responseText);
                response = custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    window.IS_INDEXING_IN_PROGRESS = response.is_indexing_in_progress;

                    _this.pagination_metadata = response.pagination_metadata;
                    _this.set_pdf_data(response.active_pdfs);

                    if(response.is_indexing_in_progress) {
                        disable_start_indexing_btn();
                        show_start_indexing_btn();
                        disable_upload_pdf_btn();
                        hide_disclaimer_message();

                    } else if(response.is_indexing_required) {
                        enable_start_indexing_btn();
                        show_start_indexing_btn();
                        enable_upload_pdf_btn();
                        show_disclaimer_message();

                    } else {
                        hide_start_indexing_btn();
                        enable_upload_pdf_btn();
                        hide_disclaimer_message();

                    }
                   // document.getElementById('content-wrapper').scrollTop = scroll_pos;
                }
            }
        }
        xhttp.send(params);
    }

    set_pdf_data(pdf_data) {
        var _this = this;
        if (pdf_data) {
            _this.pdf_data = pdf_data;
            _this.data_checklist.pdf_data = true;
        }

        _this.check_and_initialize_table();
    }

    check_and_initialize_table() {
        var _this = this;

        if (_this.data_checklist.pdf_data == false) return false;

        _this.initialize_table();
    }

    get_row_html(name, pdf_data_obj) {
        var _this = this;
        var data = pdf_data_obj[name];
        if(data == null || data == undefined) {
            data = "-";
        }
        var pdf_id = pdf_data_obj.pdf_id;
        var bot_pk = get_url_multiple_vars()['bot_pk'][0];
        var pdf_status = pdf_data_obj.status;

        var html = "";
        switch (name) {
            case "name":
                html = data;
                break;

            case "status":
                var status = data.toLowerCase();
                if(status == "active") {
                    html = `<span style="color:#047857">Active</span>`;
                } else if(status == "inactive") {
                    html = `<span style="color:#FF0000">Inactive</span>`;
                } else if(status == "indexing") {
                    html = `<span style="color:#2F80ED;">Indexing</span>`
                } else if(status == "not_indexed") {
                    html = `<span style="color:#F9600A">Not Indexed</span>`
                } else if(status == "indexed") {
                    html = `<span style="color:#047857">Indexed</span>`
                } else {
                    html = `<span>${data}</span>`
                }
                break;

            case "click_count":
                html = data;
                break;

            case "search_count":
                html = data;
                break;

            case "open_rate":
                html = data;
                break;

            case "create_datetime":
                html = data;
                break;

            case "action":
                var pdf_status = pdf_data_obj.status;
                var html = "";

                if(window.IS_INDEXING_IN_PROGRESS) {
                    html = `
                    <div class="action-icons">
                        <svg class="pdf-delete-icon disabled" width="20" height="21" viewBox="0 0 20 21" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M11.5 4.5C11.5 3.67157 10.8284 3 10 3C9.17157 3 8.5 3.67157 8.5 4.5H7.5C7.5 3.11929 8.61929 2 10 2C11.3807 2 12.5 3.11929 12.5 4.5H17C17.2761 4.5 17.5 4.72386 17.5 5C17.5 5.27614 17.2761 5.5 17 5.5H16.446L15.1499 16.7292C15.0335 17.7384 14.179 18.5 13.1631 18.5H6.83688C5.821 18.5 4.9665 17.7384 4.85006 16.7292L3.553 5.5H3C2.75454 5.5 2.55039 5.32312 2.50806 5.08988L2.5 5C2.5 4.72386 2.72386 4.5 3 4.5H11.5ZM15.438 5.5H4.561L5.84347 16.6146C5.90169 17.1192 6.32894 17.5 6.83688 17.5H13.1631C13.6711 17.5 14.0983 17.1192 14.1565 16.6146L15.438 5.5ZM8.5 8C8.74546 8 8.94961 8.15477 8.99194 8.35886L9 8.4375V14.5625C9 14.8041 8.77614 15 8.5 15C8.25454 15 8.05039 14.8452 8.00806 14.6411L8 14.5625V8.4375C8 8.19588 8.22386 8 8.5 8ZM11.5 8C11.7455 8 11.9496 8.15477 11.9919 8.35886L12 8.4375V14.5625C12 14.8041 11.7761 15 11.5 15C11.2545 15 11.0504 14.8452 11.0081 14.6411L11 14.5625V8.4375C11 8.19588 11.2239 8 11.5 8Z" fill="#FF0000"></path>
                        </svg>
                        <svg class="pdf-update-icon disabled" width="24" height="25" viewBox="0 0 24 25" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M13.4864 8.42997L16.6596 11.6032L10.4284 17.8344C10.2548 18.008 10.0389 18.1333 9.80204 18.1979L6.5945 19.0727C6.24346 19.1684 5.92135 18.8463 6.01709 18.4952L6.89187 15.2877C6.95647 15.0509 7.08176 14.835 7.25536 14.6614L13.4864 8.42997ZM17.9325 7.15722C18.8087 8.03343 18.8087 9.45404 17.9325 10.3302L17.3242 10.938L14.151 7.76535L14.7595 7.15722C15.6357 6.28101 17.0563 6.28101 17.9325 7.15722Z" fill="#475569"></path>
                        </svg>
                        <svg class="pdf-download-icon" width="20" height="21" viewBox="0 0 20 21" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path fill-rule="evenodd" clip-rule="evenodd" d="M8.88586 4.72358C8.88586 4.1089 9.38416 3.6106 9.99884 3.6106C10.6135 3.6106 11.1118 4.1089 11.1118 4.72358V9.92748C11.1118 10.0067 11.1761 10.071 11.2553 10.071H12.7816C12.9996 10.0711 13.1976 10.1984 13.288 10.3968C13.3784 10.5952 13.3447 10.8282 13.2018 10.9928L10.419 14.1935C10.3134 14.3152 10.1601 14.3852 9.99884 14.3852C9.83762 14.3852 9.68432 14.3152 9.57868 14.1935L6.79592 10.9928C6.65295 10.8282 6.61924 10.5952 6.70968 10.3968C6.80011 10.1984 6.99804 10.0711 7.21609 10.071H8.74236C8.82161 10.071 8.88586 10.0067 8.88586 9.92748V4.72358ZM15.4259 14.0287C15.4259 13.6445 15.7374 13.333 16.1216 13.333C16.3066 13.3322 16.4843 13.4052 16.6154 13.5357C16.7465 13.6663 16.8202 13.8437 16.8202 14.0287V15.0935C16.8202 16.3615 15.7922 17.3895 14.5242 17.3895H5.47331C4.20638 17.3879 3.18018 16.3604 3.18018 15.0935V14.0287C3.18018 13.6445 3.49165 13.333 3.87586 13.333C4.26008 13.333 4.57155 13.6445 4.57155 14.0287V15.0935C4.57219 15.5911 4.97564 15.9943 5.47331 15.9946H14.5242C15.0218 15.9943 15.4253 15.5911 15.4259 15.0935V14.0287Z" fill="#0F248C"></path>
                        </svg>
                    </div>`    
                } else {
                    html = `
                    <div class="action-icons">
                        <svg class="pdf-delete-icon" width="20" height="21" viewBox="0 0 20 21" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M11.5 4.5C11.5 3.67157 10.8284 3 10 3C9.17157 3 8.5 3.67157 8.5 4.5H7.5C7.5 3.11929 8.61929 2 10 2C11.3807 2 12.5 3.11929 12.5 4.5H17C17.2761 4.5 17.5 4.72386 17.5 5C17.5 5.27614 17.2761 5.5 17 5.5H16.446L15.1499 16.7292C15.0335 17.7384 14.179 18.5 13.1631 18.5H6.83688C5.821 18.5 4.9665 17.7384 4.85006 16.7292L3.553 5.5H3C2.75454 5.5 2.55039 5.32312 2.50806 5.08988L2.5 5C2.5 4.72386 2.72386 4.5 3 4.5H11.5ZM15.438 5.5H4.561L5.84347 16.6146C5.90169 17.1192 6.32894 17.5 6.83688 17.5H13.1631C13.6711 17.5 14.0983 17.1192 14.1565 16.6146L15.438 5.5ZM8.5 8C8.74546 8 8.94961 8.15477 8.99194 8.35886L9 8.4375V14.5625C9 14.8041 8.77614 15 8.5 15C8.25454 15 8.05039 14.8452 8.00806 14.6411L8 14.5625V8.4375C8 8.19588 8.22386 8 8.5 8ZM11.5 8C11.7455 8 11.9496 8.15477 11.9919 8.35886L12 8.4375V14.5625C12 14.8041 11.7761 15 11.5 15C11.2545 15 11.0504 14.8452 11.0081 14.6411L11 14.5625V8.4375C11 8.19588 11.2239 8 11.5 8Z" fill="#FF0000"></path>
                        </svg>
                        <svg class="pdf-update-icon" width="24" height="25" viewBox="0 0 24 25" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M13.4864 8.42997L16.6596 11.6032L10.4284 17.8344C10.2548 18.008 10.0389 18.1333 9.80204 18.1979L6.5945 19.0727C6.24346 19.1684 5.92135 18.8463 6.01709 18.4952L6.89187 15.2877C6.95647 15.0509 7.08176 14.835 7.25536 14.6614L13.4864 8.42997ZM17.9325 7.15722C18.8087 8.03343 18.8087 9.45404 17.9325 10.3302L17.3242 10.938L14.151 7.76535L14.7595 7.15722C15.6357 6.28101 17.0563 6.28101 17.9325 7.15722Z" fill="#475569"></path>
                        </svg>
                        <svg class="pdf-download-icon" width="20" height="21" viewBox="0 0 20 21" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path fill-rule="evenodd" clip-rule="evenodd" d="M8.88586 4.72358C8.88586 4.1089 9.38416 3.6106 9.99884 3.6106C10.6135 3.6106 11.1118 4.1089 11.1118 4.72358V9.92748C11.1118 10.0067 11.1761 10.071 11.2553 10.071H12.7816C12.9996 10.0711 13.1976 10.1984 13.288 10.3968C13.3784 10.5952 13.3447 10.8282 13.2018 10.9928L10.419 14.1935C10.3134 14.3152 10.1601 14.3852 9.99884 14.3852C9.83762 14.3852 9.68432 14.3152 9.57868 14.1935L6.79592 10.9928C6.65295 10.8282 6.61924 10.5952 6.70968 10.3968C6.80011 10.1984 6.99804 10.0711 7.21609 10.071H8.74236C8.82161 10.071 8.88586 10.0067 8.88586 9.92748V4.72358ZM15.4259 14.0287C15.4259 13.6445 15.7374 13.333 16.1216 13.333C16.3066 13.3322 16.4843 13.4052 16.6154 13.5357C16.7465 13.6663 16.8202 13.8437 16.8202 14.0287V15.0935C16.8202 16.3615 15.7922 17.3895 14.5242 17.3895H5.47331C4.20638 17.3879 3.18018 16.3604 3.18018 15.0935V14.0287C3.18018 13.6445 3.49165 13.333 3.87586 13.333C4.26008 13.333 4.57155 13.6445 4.57155 14.0287V15.0935C4.57219 15.5911 4.97564 15.9943 5.47331 15.9946H14.5242C15.0218 15.9943 15.4253 15.5911 15.4259 15.0935V14.0287Z" fill="#0F248C"></path>
                        </svg>
                    </div>`
                }

                break;

            default:
                html = "-";
                console.log("Error: unknown column")
                break;
        }
        return html;
    }

    get_select_row_html(pdf_data_obj) {
        var _this = this;
        const { enable_select_rows } = _this.options;

        if (!enable_select_rows) {
            return "";
        }

        var select_row_html = '<input class="pdf_select_row_cb" type="checkbox" pdf_id="' + pdf_data_obj.pdf_id + '" />';
        return select_row_html;
    }

    get_row(pdf_data_obj) {
        var _this = this;
        const { enable_select_rows } = _this.options;

        var pdf_data_list = [];

        var select_row_html = _this.get_select_row_html(pdf_data_obj);
        if (enable_select_rows) {
            pdf_data_list.push(select_row_html);
        }

        _this.active_user_metadata.lead_data_cols.forEach((column_info_obj) => {
            try {
                if (column_info_obj.selected == false) return;
                var name = column_info_obj.name;
                pdf_data_list.push(_this.get_row_html(name, pdf_data_obj));
            } catch (err) {
                console.log("ERROR get_row on adding row data of column : ", column_info_obj);
            }
        });

        return pdf_data_list;
    }

    get_rows() {
        var _this = this;
        var pdf_data_list = [];
        _this.pdf_data.forEach((pdf_data_obj) => {
            pdf_data_list.push(_this.get_row(pdf_data_obj));
        });
        return pdf_data_list;
    }

    select_row_checkbox_change_listener(event) {
        var _this = this;
        var select_all_rows_cb = _this.table.querySelector(".pdf_select_all_rows_cb");
        var select_row_cbs = _this.table.querySelectorAll(".pdf_select_row_cb");

        var total_rows_checked = 0;
        select_row_cbs.forEach((select_row_cb) => {
            if (select_row_cb.checked) {
                total_rows_checked += 1;
            }
        });

        if (total_rows_checked == select_row_cbs.length) {
            select_all_rows_cb.checked = true;
        } else {
            select_all_rows_cb.checked = false;
        }

        if(total_rows_checked > 0) {
            document.getElementById("delete_pdf_btn").disabled = false;
        } else {
            document.getElementById("delete_pdf_btn").disabled = true;
        }
    }

    show_filtered_results(event) {
        var _this = this;
        var value = event.target.value;

        if (!_this.data_table_obj) {
            return;
        }

        _this.data_table_obj.search(value).draw();

        var pagination_entry_container = _this.pagination_container.querySelector(".show-pagination-entry-container");

        if (pagination_entry_container) {
            var showing_entry_count = _this.table.querySelectorAll("tbody tr[role='row']").length;
            var total_entry = _this.pagination_metadata.end_point - _this.pagination_metadata.start_point + 1;

            if (value.length != 0) {
                var text = "Showing " + showing_entry_count + " entries (filtered from " + total_entry + " total entries)";
                pagination_entry_container.innerHTML = text;
            } else {
                pagination_entry_container.innerHTML = pagination_entry_container.getAttribute("filter_default_text");
            }
        }
    }

    add_event_listeners_in_rows(container = null) {
        var _this = this;
        if (container == null) container = _this.table;

        // select row checkbox event listener
        var select_row_cbs = container.querySelectorAll(".pdf_select_row_cb");
        select_row_cbs.forEach((select_row_cb) => {
            select_row_cb.addEventListener("change", (event) => {
                _this.select_row_checkbox_change_listener(event);
            });
        });

        // Event listener in searchbar element
        _this.searchbar_element.onkeyup = function (event) {
            _this.show_filtered_results(event);
        }
    }

    add_event_listeners() {
        var _this = this;

        // Select all row checkbox event listener
        var select_all_rows_cb = _this.table.querySelector(".pdf_select_all_rows_cb");
        if (select_all_rows_cb) {
            select_all_rows_cb.addEventListener("change", function () {
                var select_row_cbs = _this.table.querySelectorAll(".pdf_select_row_cb");
                var all_rows_selected = this.checked;

                select_row_cbs.forEach((select_row_cb) => {
                    if (all_rows_selected) {
                        select_row_cb.checked = true;
                    } else {
                        select_row_cb.checked = false;
                    }
                })

                if(all_rows_selected) {
                    document.getElementById("delete_pdf_btn").disabled = false;
                } else {
                    document.getElementById("delete_pdf_btn").disabled = true;
                }
            });
        }

        var pdf_delete_btns = _this.table_container.querySelectorAll(".pdf-delete-icon");
        pdf_delete_btns.forEach(function(pdf_delete_btn) {
            var tr_element = pdf_delete_btn.closest("tr");
            var pdf_key = tr_element.getAttribute("pdf_id");

            pdf_delete_btn.addEventListener("click", function(event) {
                if(pdf_delete_btn.classList.contains("disabled")) {
                    show_pdf_search_toast("PDF cannot be deleted while indexing is in progress");
                } else {
                    show_delete_pdf_modal(pdf_key);
                }
            });
        });
        
        var pdf_update_btns = _this.table_container.querySelectorAll(".pdf-update-icon");
        pdf_update_btns.forEach(function(pdf_update_btn) {
            var tr_element = pdf_update_btn.closest("tr");
            var pdf_key = tr_element.getAttribute("pdf_id");
            var status = tr_element.getAttribute("status");
            var pdf_name = tr_element.getAttribute("pdf_name");
            var important_pages = tr_element.getAttribute("important_pages");
            var skipped_pages = tr_element.getAttribute("skipped_pages");

            pdf_update_btn.addEventListener("click", function(event) {
                if(pdf_update_btn.classList.contains("disabled")) {
                    show_pdf_search_toast("PDF cannot be updated while indexing is in progress");
                } else {
                    show_update_pdf_modal(pdf_key,status,pdf_name,important_pages,skipped_pages);
                }
            });
        });

        var pdf_download_btns = _this.table_container.querySelectorAll(".pdf-download-icon");
        pdf_download_btns.forEach(function(pdf_download_btn) {
            var tr_element = pdf_download_btn.closest("tr");
            var pdf_name = tr_element.getAttribute("pdf_name");
            var file_path = tr_element.getAttribute("file_path");
            pdf_download_btn.addEventListener("click", function(event) {
                download_pdf(pdf_name,file_path);    
            });
        });

        
    }

    initialize_lead_data_metadata_update_modal() {
        var _this = this;
        var lead_data_cols = _this.active_user_metadata.lead_data_cols;
        var container = document.querySelector("#lead_dala_table_meta_div");
        var selected_values = [];
        var unselected_values = [];
        lead_data_cols.forEach((obj) => {
            if (obj.selected == true) {
                selected_values.push({
                    'key': obj.name,
                    'value': obj.display_name
                });
            } else {
                unselected_values.push({
                    'key': obj.name,
                    'value': obj.display_name
                });
            }
        });

        initialize_custom_tag_input(selected_values, unselected_values, container)
    }

    update_table_meta_deta(lead_data_cols) {
        var _this = this;
        _this.active_user_metadata.lead_data_cols = lead_data_cols;

        _this.save_table_meta_data();
        _this.initialize_table();
    }

    save_table_meta_data() {
        var _this = this;
        var lead_data_cols = _this.active_user_metadata.lead_data_cols
        window.localStorage.setItem("pdf_table_meta_data", JSON.stringify(lead_data_cols));
    }

    get_table_meta_data() {
        var _this = this;
        var lead_data_cols = window.localStorage.getItem("pdf_table_meta_data");

        if (lead_data_cols == null) {
            lead_data_cols = _this.get_default_meta_data();
        } else {
            lead_data_cols = JSON.parse(lead_data_cols);
        }
        return lead_data_cols;
    }

    get_default_meta_data() {
        var lead_data_cols = [
            ['name', 'Name', true],
            ['create_datetime', 'Data and Time', true],
            ['status', 'Status', true],
            ['click_count', 'Click Count', true],
            ['search_count', 'Search Count', true],
            ['open_rate', 'Open Rate', true],
            ['action', 'Action', true]
        ];

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
};

function download_pdf(pdf_name, file_path){

    window.open(window.location.origin + file_path);
}

function initialize_active_pdf_table() {

    var pdf_table_container = document.querySelector("#pdf_dashboard_table");
    var pdf_searchbar = document.querySelector("#pdf-search-bar");
    var pagination_container = document.getElementById("pdf_table_pagination_div");

    window.ACTIVE_PDF_TABLE = new ActivePDFTable(pdf_table_container, pdf_searchbar, pagination_container);
}

function save_lead_data_table_metadata() {

    var lead_data_cols = window.ACTIVE_PDF_TABLE.active_user_metadata.lead_data_cols;

    var selected_values = [];
    var unselected_values = [];
    window.LEAD_DATA_METADATA_INPUT.selected_values.filter((obj) => {
        selected_values.push(obj.key);
    });
    window.LEAD_DATA_METADATA_INPUT.unselected_values.filter((obj) => {
        unselected_values.push(obj.key);
    });

    if (selected_values.length < 2) {
        show_pdf_toast("Atleast two columns needs to be selected.");
        return;
    }

    lead_data_cols.forEach((item, index) => {
        if (selected_values.indexOf(item.name) >= 0) {
            item.selected = true;
            item.index = selected_values.indexOf(item.name);
        } else {
            item.selected = false;
            item.index = window.LEAD_DATA_METADATA_INPUT.selected_values.length;
        }
    })

    lead_data_cols.sort((obj1, obj2) => {
        return obj1.index - obj2.index;
    });

    window.ACTIVE_PDF_TABLE.update_table_meta_deta(lead_data_cols)
}

function initialize_custom_tag_input(selected_values, unselected_values, container) {
    window.LEAD_DATA_METADATA_INPUT = new CognoAICustomTagInput(container, selected_values, unselected_values);
}

class CognoAICustomTagInput {
    constructor(container, selected_values, unselected_values) {
        this.container = container;
        this.selected_values = selected_values;
        this.unselected_values = unselected_values;
        this.button_display_div = null;
        this.drag_obj = null;
        this.init();
    }

    init() {
        var _this = this;
        _this.initialize();
    }

    add_event_listeners() {
        var _this = this;
        var delete_buttons = _this.button_display_div.querySelectorAll(".tag_delete_button");
        delete_buttons.forEach((delete_button) => {
            delete_button.addEventListener('click', function (event) {
                _this.tag_delete_button_click_listner(event)
            });
        });

        var select_element = _this.select_element;
        select_element.addEventListener("change", function (event) {
            _this.tag_select_listnet(event);
        })
    }

    tag_delete_button_click_listner(event) {
        var _this = this;
        var target = event.target;
        var key = target.previousElementSibling.getAttribute("key");
        var index = _this.find_index_of_element(key, _this.selected_values);
        if (index != -1) {
            var target_obj = _this.selected_values[index];
            _this.selected_values.splice(index, 1);
            _this.unselected_values.push(target_obj);
            _this.initialize();
        }
    }

    tag_select_listnet(event) {
        var _this = this;
        var target = event.target;
        var key = target.value;
        var index = _this.find_index_of_element(key, _this.unselected_values);
        if (index != -1) {
            var target_obj = _this.unselected_values[index];
            _this.selected_values.push(target_obj);
            _this.unselected_values.splice(index, 1);
            _this.initialize();
        }
    }

    find_index_of_element(key, list) {
        for (var index = 0; index < list.length; index++) {
            if (list[index].key == key) return index;
        }
        return -1;
    }

    find_unselected_element_by_key(key) {
        var _this = this;
        var target_obj = null;
        _this.unselected_values.forEach((obj) => {
            if (obj.key == key && target_obj == null) {
                target_obj = obj;
            }
        });
        return target_obj;
    }

    find_selected_element_by_key(key) {
        var _this = this;
        var target_obj = null;
        _this.selected_values.forEach((obj) => {
            if (obj.key == key && target_obj == null) {
                target_obj = obj;
            }
        });
        return target_obj;
    }

    onmouseover_tag = function (element) {
        var handler = element.querySelector("svg");
        handler.style.display = "";
    }

    onmouseout_tag = function (element) {
        var handler = element.querySelector("svg");
        handler.style.display = "none";
    }

    get_tag_input_html() {
        var _this = this;
        var tag_input_html = '<ul class="cognoai-custom-tag-input mt-3">';

        _this.selected_values.forEach((obj, index) => {
            tag_input_html += `
                <li class="bg-primary" onmouseover="window.LEAD_DATA_METADATA_INPUT.onmouseover_tag(this)" onmouseout="window.LEAD_DATA_METADATA_INPUT.onmouseout_tag(this)">
                    <svg class="drag-handle" width="14" height="16" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-bottom: 2px; display: none;">
                        <path fill-rule="evenodd" clip-rule="evenodd" d="M9.91658 3.5C9.91658 4.14167 9.39158 4.66667 8.74992 4.66667C8.10825 4.66667 7.58325 4.14167 7.58325 3.5C7.58325 2.85834 8.10825 2.33334 8.74992 2.33334C9.39158 2.33334 9.91658 2.85834 9.91658 3.5ZM5.24996 2.33334C4.60829 2.33334 4.08329 2.85834 4.08329 3.50001C4.08329 4.14167 4.60829 4.66667 5.24996 4.66667C5.89163 4.66667 6.41663 4.14167 6.41663 3.50001C6.41663 2.85834 5.89163 2.33334 5.24996 2.33334ZM4.08325 7C4.08325 6.35834 4.60825 5.83334 5.24992 5.83334C5.89159 5.83334 6.41659 6.35834 6.41659 7C6.41659 7.64167 5.89159 8.16667 5.24992 8.16667C4.60825 8.16667 4.08325 7.64167 4.08325 7ZM5.24992 11.6667C5.89159 11.6667 6.41659 11.1417 6.41659 10.5C6.41659 9.85834 5.89159 9.33334 5.24992 9.33334C4.60825 9.33334 4.08325 9.85834 4.08325 10.5C4.08325 11.1417 4.60825 11.6667 5.24992 11.6667ZM8.74992 5.83334C8.10825 5.83334 7.58325 6.35834 7.58325 7C7.58325 7.64167 8.10825 8.16667 8.74992 8.16667C9.39158 8.16667 9.91658 7.64167 9.91658 7C9.91658 6.35834 9.39158 5.83334 8.74992 5.83334ZM7.58325 10.5C7.58325 9.85834 8.10825 9.33334 8.74992 9.33334C9.39158 9.33334 9.91658 9.85834 9.91658 10.5C9.91658 11.1417 9.39158 11.6667 8.74992 11.6667C8.10825 11.6667 7.58325 11.1417 7.58325 10.5Z" fill="white"/>
                    </svg>
                    <span key='${obj.key}' class="value_display_span">
                        ${obj.value}
                    </span>
                    <span class="tag_delete_button" index='${index}'>x</span>
                </li>`
        });

        tag_input_html += '</ul>';
        return tag_input_html;
    }

    get_tag_select_html() {
        var _this = this;
        var tag_select_html = '<select class="form-control" data-select="false">';
        tag_select_html += '<option disabled selected> Choose column name </option>';

        _this.unselected_values.forEach((obj, index) => {
            tag_select_html += '<option value="' + obj.key + '"> ' + obj.value + '</option>';
        });

        tag_select_html += '</select>';
        return tag_select_html;
    }

    initialize() {
        var _this = this;
        var html = "";
        html += _this.get_tag_input_html();
        html += _this.get_tag_select_html();
        _this.container.innerHTML = html;

        _this.button_display_div = _this.container.querySelector("ul");
        _this.select_element = _this.container.querySelector("select");
        _this.add_event_listeners();
        _this.select_element_obj = new EasyassistCustomSelect(_this.select_element, null, window.CONSOLE_THEME_COLOR);

        _this.drag_obj = new CognoAiDragableTagInput(_this.button_display_div, function (event) {
            _this.drag_finish_callback(event)
        });
    }

    drag_finish_callback = function (event) {
        var _this = this;

        var elements = _this.button_display_div.children;
        var new_list = [];
        for (var idx = 0; idx < elements.length; idx++) {
            var element = elements[idx];
            var value_display_span = element.querySelector(".value_display_span");
            var key = value_display_span.getAttribute("key");
            var index = _this.find_index_of_element(key, _this.selected_values);
            new_list.push(_this.selected_values[index]);
        }

        _this.selected_values = new_list;
    }
}

class CognoAiDragableTagInput {
    constructor(container, drag_finish_callback) {
        this.container = container
        this.element = null;
        this.currX = 0;
        this.currY = 0;
        this.clientX = 0;
        this.clientY = 0;
        this.pageX = 0;
        this.offset = 12;
        this.is_dragging = false;
        this.drag_container = null;
        this.prevX = 0;
        this.prevY = 0;
        this.drag_finish_callback = drag_finish_callback;

        var _this = this;

        document.addEventListener("mouseleave", function (e) {
            _this.drag_element('out', e);
            e.preventDefault();
        });

        _this.drag_container = document;

        _this.drag_container.addEventListener("mousemove", function (e) {
            _this.drag_element('move', e);
        });

        _this.drag_container.addEventListener("mouseup", function (e) {
            _this.drag_element('up', e);
        });

        _this.initialize();
    }

    initialize() {
        var _this = this;
        var elements = _this.container.querySelectorAll(".drag-handle");
        if (elements.length == 0) {
            elements = _this.container.children;
        }
        for (var index = 0; index < elements.length; index++) {
            var element = elements[index];
            var target_element = _this.get_target_element(element);

            element.addEventListener("mousedown", function (e) {
                _this.drag_element('down', e);
            });

            element.addEventListener("mouseup", function (e) {
                _this.drag_element('up', e);
            });

            target_element.addEventListener("touchstart", function (e) {
                _this.prevX = e.touches[0].clientX;
                _this.prevY = e.touches[0].clientY;
                _this.drag_element('down', e);
            });

            target_element.addEventListener("touchmove", function (e) {
                var data = {
                    movementX: e.touches[0].clientX - _this.prevX,
                    movementY: e.touches[0].clientY - _this.prevY,
                    clientX: e.touches[0].clientX,
                    clientY: e.touches[0].clientY,
                }
                _this.prevX = e.touches[0].clientX;
                _this.prevY = e.touches[0].clientY;
                _this.drag_element('move', data);
            });

            target_element.addEventListener("touchend", function (e) {
                _this.prevX = 0;
                _this.prevY = 0;
                _this.drag_element('out', e);
            });

            element.style.cursor = "move";
        }
    }

    get_target_element(element) {
        var _this = this;
        var handle = element;
        while (handle.parentElement != _this.container)
            handle = handle.parentElement;
        return handle;
    }

    drag_element(direction, e) {
        var _this = this;
        if (direction == 'down') {
            _this.is_dragging = true;
            _this.element = _this.get_target_element(e.target);
            if (!_this.dummy_element) {
                _this.dummy_element = document.createElement("span");
                _this.dummy_element.className = "cognoai-drag-dummy-element";
            }
        }

        if (direction == 'up' || direction == "out") {
            if (_this.is_dragging == false) {
                return;
            }

            _this.dummy_element.insertAdjacentElement("beforebegin", _this.element);
            _this.element.classList.remove("cognoai-drag-helper");
            _this.element.style.top = "";
            _this.element.style.left = "";
            _this.currX = 0;
            _this.currY = 0;
            _this.offset = 12;
            _this.is_dragging = false;
            _this.drag_container = null;
            _this.prevX = 0;
            _this.prevY = 0;
            _this.is_dragging = false;

            _this.element = null;
            if (_this.dummy_element.parentElement) {
                _this.dummy_element.parentElement.removeChild(_this.dummy_element);
            }
            _this.dummy_element = null;

            if (_this.drag_finish_callback) {
                try {
                    _this.drag_finish_callback()
                } catch (err) { }
            }
        }

        if (direction == 'move') {
            if (_this.is_dragging) {

                var left = _this.element.offsetLeft;
                var top = _this.element.offsetTop;

                _this.element.classList.add("cognoai-drag-helper");
                _this.currX = e.movementX + left;
                _this.currY = e.movementY + top;

                _this.clientX = e.clientX;
                _this.clientY = e.clientY;

                _this.pageX = e.pageX;

                _this.drag();
                _this.compute();
            }
        }
    }

    drag() {
        var _this = this;
        // _this.currX = Math.max(_this.currX, 0);

        _this.element.style.left = _this.currX + "px";
        _this.element.style.top = _this.currY + "px";
    }

    compute() {
        var _this = this;

        _this.element.hidden = true;
        let elemBelow = document.elementFromPoint(_this.clientX, _this.clientY);
        _this.element.hidden = false;

        try {
            var target_element = _this.get_target_element(elemBelow);
            if (target_element) {

                var pWidth = $(target_element).innerWidth(); //use .outerWidth() if you want borders
                var pOffset = $(target_element).offset();
                var x = _this.pageX - pOffset.left;
                if (pWidth / 2 > x) {
                    target_element.insertAdjacentElement("beforebegin", _this.dummy_element);
                } else {
                    target_element.insertAdjacentElement("afterend", _this.dummy_element);
                }
            }
        } catch (err) { }
    }
}

function get_url_multiple_vars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function (m, key, value) {
        if (!(key in vars)) {
            vars[key] = [];
        }
        vars[key].push(strip_unwanted_characters(value));
    });
    return vars;
}


function expand_pages_in_list_format(pages){
    var a = pages.split(',');
    var new_a = new Array();
    for(var i=0;i<a.length;i++){
        var sub_split = a[i].split("-");
        var arr1 = new Array();
        if(sub_split.length == 2){
            for(var j=parseInt(sub_split[0]);j<=parseInt(sub_split[1]);j++){
                arr1.push(j);
            }
            new_a.push(arr1);
        }
        else{
            new_a.push(parseInt(sub_split[0]));
        }
    }
    var mergerd_a = new Array();
    for(var i=0;i<new_a.length;i++){
        
        mergerd_a = mergerd_a.concat(new_a[i]);
    } 
    let unique_mergerd_a = [...new Set(mergerd_a)];
    return unique_mergerd_a.sort(function(a,b){
        return a-b;
    });
}

function get_pages_in_list_format(pages){
    pages=pages.trim();
    if(pages.length == 0){
        return "";
    }
    if(pages[0] == ',' && pages.slice(-1) == ','){
        return pages.slice(1,-1);
    }
    if(pages[0] == ','){
        return pages.slice(1);
    }
    if(pages.slice(-1) == ','){
        return pages.slice(0,-1);
    }
    var patt1 = /[^0-9,\s-]/g;
    var result = pages.match(patt1);
    if(result != null){
        return "";
    }
    var a = pages.split(',');
    var new_a = new Array();
    for(var i=0;i<a.length;i++){
        var sub_split = a[i].split("-");
        var arr1 = new Array();
        if(sub_split.length == 2){
            for(var j=parseInt(sub_split[0]);j<=parseInt(sub_split[1]);j++){
                arr1.push(j);
            }
            new_a.push(arr1);
        }
        else{
            new_a.push(parseInt(sub_split[0]));
        }
    }
    var mergerd_a = new Array();
    for(var i=0;i<new_a.length;i++){
        
        mergerd_a = mergerd_a.concat(new_a[i]);
    } 
    let unique_mergerd_a = [...new Set(mergerd_a)];
    unique_mergerd_a.sort(function(a,b){
        return a-b;
    });

    return contract_expanded_pages(unique_mergerd_a);
}
    
function contract_expanded_pages(unique_mergerd_a){

    var result = new Array();
    var s=0;
    var e;
    var str;
    for(var i=0;i<unique_mergerd_a.length-1;i++){
        if(Math.abs((unique_mergerd_a[i] - unique_mergerd_a[i+1])) != 1){
            
            e=i;
            if(s==e){
                str=unique_mergerd_a[s];
            }
            else{
            str=unique_mergerd_a[s]+"-"+unique_mergerd_a[e];
            }
            result.push(str);
            s=i+1;
        }
        else{

            continue;
        }
    }
    if(unique_mergerd_a[i]-unique_mergerd_a[i-1] != 1){
        str=unique_mergerd_a[i];
        result.push(str);
    }
    else{
        str=unique_mergerd_a[s]+"-"+unique_mergerd_a[i];
        result.push(str);
    }
    return result;
}

function check_pdf_file(file_name) {
    file_name = file_name.toLowerCase();
    file_name = file_name.split(".");
    file_extension = String(file_name.slice(-1));
    var pdf_files = ["pdf"];

    if(pdf_files.includes(file_extension)) {
        return true;
    }
    return false;
}

function upload_pdf(element) {
    pdf_input_file = ($("#pdf-upload-modal #drag-drop-input-box"))[0].files[0];
    var file = pdf_input_file;

    var uploaded_pdf_name = document.getElementById("pdf_name").value;
    uploaded_pdf_name = uploaded_pdf_name.trim();
    uploaded_pdf_name = stripHTML(uploaded_pdf_name);
    if(uploaded_pdf_name.length==0){
        show_pdf_search_toast("PDF name cannot be empty");
        return;
    }

    if (file == undefined || file == null) {
        show_pdf_search_toast("Please choose a file.");
        return;
    }

    var malicious_file_report = check_malicious_file(file.name)
    if (malicious_file_report.status == true) {
        show_pdf_search_toast(malicious_file_report.message)
        return false;
    }

    if (check_pdf_file(file.name) == false) {
        return false;
    }

    if (file.size / 1000000 > 5) {
        show_pdf_search_toast("File size cannot exceed 5 MB");
        $("#drag-drop-input-box")[0].value = "";
        return;
    }

    if(uploaded_pdf_name.length > 25){
        show_pdf_search_toast("PDF Name should not be more than 25 characters");
        return;
    }
    var uploaded_pdf_important_pages = document.getElementById("imp_pages").value;
    uploaded_pdf_important_pages = stripHTML(uploaded_pdf_important_pages);
    var uploaded_pdf_skipped_pages = document.getElementById("skipped_pages").value;
    uploaded_pdf_skipped_pages = stripHTML(uploaded_pdf_skipped_pages);
    if(uploaded_pdf_important_pages.trim().length != 0 && uploaded_pdf_skipped_pages.trim().length !=0){    
        important_pages1 = expand_pages_in_list_format(uploaded_pdf_important_pages);
        skipped_pages1 = expand_pages_in_list_format(uploaded_pdf_skipped_pages);

        var check = 0;

        if(important_pages1.length > skipped_pages1.length){
            for(var i=0; i<skipped_pages1.length;i++){
                if(important_pages1.includes(skipped_pages1[i])){
                    check = 1;
                    break;
                }   
            }
        }
        else{
            for(var i=0; i<important_pages1.length;i++){
                if(skipped_pages1.includes(important_pages1[i])){
                    check = 1;
                    break;
                }   
            }
        }
        if(check==1){
            show_pdf_search_toast("The page numbers can not be same for important and skipped pages.");
            return;
        }
    }
    else if(uploaded_pdf_important_pages.trim().length == 0 && uploaded_pdf_skipped_pages.trim().length !=0){
        important_pages1 = [];
        skipped_pages1 = expand_pages_in_list_format(uploaded_pdf_skipped_pages);
    }
    else if(uploaded_pdf_skipped_pages.trim().length == 0 && uploaded_pdf_important_pages.trim().length != 0){
        skipped_pages1 = [];
        important_pages1 = expand_pages_in_list_format(uploaded_pdf_important_pages);
    }
    else{
        skipped_pages1 = [];
        important_pages1 = [];
    }

    var reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = function() {
        var filters = get_url_multiple_vars();
        base64_str = reader.result.split(",")[1];

        var json_string = {
            "base64_file": base64_str,
            "name": uploaded_pdf_name,
            "file_name": file.name,
            "important_pages": important_pages1.join(","),
            "skipped_pages": skipped_pages1.join(","),
            "bot_pk": filters["bot_pk"][0],
        };

        json_string = JSON.stringify(json_string);

        encrypted_data = EncryptVariable(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        var params = JSON.stringify(encrypted_data);

        element.innerText = "Uploading...";

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/chat/bot/upload-pdf/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', $('input[name="csrfmiddlewaretoken"]').val());
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = custom_decrypt(response.Response);
                response = JSON.parse(response);
                if(response.status == 200) {
                    window.ACTIVE_PDF_TABLE.fetch_active_pdf();
                    reset_upload_pdf_modal();
                    $("#pdf-upload-modal").modal("close");

                    show_disclaimer_message();

                    show_start_indexing_btn();
                } else if(response.status == 400) {

                    show_pdf_search_toast(response.message);

                } else if(response.status == 300) {

                    show_pdf_search_toast("Upload file is malicious. Please upload valid file.");

                } else {
                    show_pdf_search_toast("Something went wrong. Please try again");
                }

                element.innerText = "Upload";
            }
        }
        xhttp.send(params);
    };

    reader.onerror = function(error) {
        console.log('Error: ', error);
    };
}

function show_delete_pdf_modal(pdf_key) {
    var delete_modal_element = document.getElementById("delete-confirmation-modal");
    var delete_pdf_input_elment = delete_modal_element.querySelector("input[type='hidden']");
    delete_pdf_input_elment.value = pdf_key;

    $("#delete-confirmation-modal").modal("open");
}

function show_update_pdf_modal(pdf_key,status,pdf_name,important_pages,skipped_pages) {
    reset_update_pdf_modal();
    var update_modal_element = document.getElementById("pdf-update-modal");
    var update_pdf_input_elment = update_modal_element.querySelector("input[type='hidden']");
    update_pdf_input_elment.value = pdf_key;
    var update_pdf_name_input_elment = update_modal_element.querySelector("#update_pdf_name");
    update_pdf_name_input_elment.value = pdf_name;
    var update_pdf_important_pages_input_elment = update_modal_element.querySelector("#update_imp_pages");
    update_pdf_important_pages_input_elment.value = contract_expanded_pages(important_pages.split(','));
    var update_pdf_skipped_pages_input_elment = update_modal_element.querySelector("#update_skipped_pages");
    update_pdf_skipped_pages_input_elment.value = contract_expanded_pages(skipped_pages.split(','));;
    var update_pdf_status_input_elment = update_modal_element.querySelector("#active");
    update_pdf_status_input_elment.checked = true;
    var update_pdf_status_input_elment = update_modal_element.querySelector("#inactive");
    update_pdf_status_input_elment.checked = false;
    if(status=="active"){
        var update_pdf_status_input_elment = update_modal_element.querySelector("#active");
        update_pdf_status_input_elment.checked = true;
    }
    else if(status=="inactive"){
        var update_pdf_status_input_elment = update_modal_element.querySelector("#inactive");
        update_pdf_status_input_elment.checked = true;
    }

    $("#pdf-update-modal").modal("open");
}

function delete_pdf(element) {

    var delete_modal_element = document.getElementById("delete-confirmation-modal");
    var delete_pdf_input_elment = delete_modal_element.querySelector("input[type='hidden']");
    var pdf_key = delete_pdf_input_elment.value;

    var filters = get_url_multiple_vars();
    var bot_pk = filters["bot_pk"][0];

    if(!pdf_key) {
        return;
    }

    var json_string = {
        "pdf_key": pdf_key,
        "bot_pk": bot_pk
    };

    json_string = JSON.stringify(json_string);

    encrypted_data = EncryptVariable(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);

    element.innerText = "Deleting...";

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/chat/bot/delete-pdf/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', $('input[name="csrfmiddlewaretoken"]').val());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);

            window.ACTIVE_PDF_TABLE.fetch_active_pdf();
            element.innerText = "Delete";
            $(delete_modal_element).modal("close");

            show_disclaimer_message();

            show_start_indexing_btn();
        }
    }
    xhttp.send(params);
}

function update_pdf(element) {
    pdf_update_input_file = ($("#pdf-update-modal #drag-drop-input-box"))[0].files[0];
    var file = pdf_update_input_file;
    var update_modal_element = document.getElementById("pdf-update-modal");
    var update_pdf_input_elment = update_modal_element.querySelector("input[type='hidden']");
    var pdf_key = update_pdf_input_elment.value;
    var update_pdf_status_input_elment = update_modal_element.querySelector("#active");
    var pdf_status;

    if(update_pdf_status_input_elment.checked == true){
        pdf_status = "active";
    } else {
        pdf_status = "inactive";
    }

    if(!pdf_key) {
        return;
    }

    var updated_pdf_name = document.getElementById("update_pdf_name").value; 
    updated_pdf_name = stripHTML(updated_pdf_name);
    updated_pdf_name = updated_pdf_name.trim();

    if(updated_pdf_name.length == 0) {
        show_pdf_search_toast("PDF name cannot be empty");
        return;

    }

    if(updated_pdf_name.length > 25){
        show_pdf_search_toast("PDF Name should not be more than 25 characters");
        return;
    }

    if(file) {
        var malicious_file_report = check_malicious_file(file.name)
        if (malicious_file_report.status == true) {
            show_pdf_search_toast(malicious_file_report.message)
            return false;
        }

        if (check_pdf_file(file.name) == false) {
            return false;
        }

        if (file.size / 1000000 > 5) {
            show_pdf_search_toast("File size cannot exceed 5 MB");
            $("#drag-drop-input-box")[0].value = "";
            return;
        }
    }

    var updated_pdf_important_pages = document.getElementById("update_imp_pages").value;
    updated_pdf_important_pages = stripHTML(updated_pdf_important_pages);
    var updated_pdf_skipped_pages = document.getElementById("update_skipped_pages").value;
    updated_pdf_skipped_pages = stripHTML(updated_pdf_skipped_pages);
    if(updated_pdf_important_pages.trim().length != 0 && updated_pdf_skipped_pages.trim().length !=0){
        update_important_pages1 = expand_pages_in_list_format(updated_pdf_important_pages);
        update_skipped_pages1 = expand_pages_in_list_format(updated_pdf_skipped_pages);

        var check = 0;
        if(update_important_pages1.length > update_skipped_pages1.length){
            for(var i=0; i<update_skipped_pages1.length;i++){
                if(update_important_pages1.includes(update_skipped_pages1[i])){
                    check = 1;
                    break;
                }   
            }
        }
        else{
            for(var i=0; i<update_important_pages1.length;i++){
                if(update_skipped_pages1.includes(update_important_pages1[i])){
                    check = 1;
                    break;
                }   
            }
        }
        if(check==1){
            show_pdf_search_toast("The page numbers can not be same for important and skipped pages.");
            return;
        }
    }
    else if(updated_pdf_important_pages.trim().length == 0 && updated_pdf_skipped_pages.trim().length !=0){
        update_important_pages1 = [];
        update_skipped_pages1 = expand_pages_in_list_format(updated_pdf_skipped_pages);
    }
    else if(updated_pdf_skipped_pages.trim().length == 0 && updated_pdf_important_pages.trim().length != 0){
        update_skipped_pages1 = [];
        update_important_pages1 = expand_pages_in_list_format(updated_pdf_important_pages);
    }
    else{
        update_skipped_pages1 = [];
        update_important_pages1 = [];
    }

    update_important_pages1 = update_important_pages1.join(',');
    update_skipped_pages1 = update_skipped_pages1.join(',');

    if(file) {
        var reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = function() {
            base64_str = reader.result.split(",")[1];

            var file_obj = {
                "file_name": file.name,
                "base64_str": base64_str,
            };

            update_pdf_details(
                element,
                updated_pdf_name,
                update_important_pages1,
                update_skipped_pages1,
                pdf_key,
                pdf_status,
                file_obj
            )

        };

        reader.onerror = function(error) {
            console.log('Error: ', error);
        };
    } else {
         update_pdf_details(
            element,
            updated_pdf_name,
            update_important_pages1,
            update_skipped_pages1,
            pdf_key,
            pdf_status
        )
    }
}


function update_pdf_details(element, pdf_name, important_pages, skipped_pages, pdf_key, pdf_status, file_obj=null) {
    var filters = get_url_multiple_vars();

    if(file_obj) {
        var json_string = {
            "is_file_attached": true,
            "base64_file": file_obj.base64_str,
            "file_name": file_obj.file_name,
            "name": pdf_name,
            "important_pages": important_pages,
            "skipped_pages": skipped_pages,
            "bot_pk": filters["bot_pk"][0],
            "pdf_key": pdf_key,
            "status": pdf_status
        };
    } else {
        var json_string = {
            "is_file_attached": false,
            "name": pdf_name,
            "important_pages": important_pages,
            "skipped_pages": skipped_pages,
            "bot_pk": filters["bot_pk"][0],
            "pdf_key": pdf_key,
            "status": pdf_status
        };
    }

    element.innerText = "Updating...";

    json_string = JSON.stringify(json_string);

    encrypted_data = EncryptVariable(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/chat/bot/update-pdf/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);

            if(response.status == 200) {

                initialize_active_pdf_table();
                // reset_update_pdf_modal();
                $("#pdf-update-modal").modal("close");

                if(response.is_indexing_required) {
                    show_disclaimer_message();
                    show_start_indexing_btn();
                }

            } else if(response.status == 400){

                show_pdf_search_toast(response.message);
                reset_update_pdf_modal();

            } else if(response.status == 301) {

                show_pdf_search_toast("PDF status cannot be changed");

            } else if(response.status == 300) {

                show_pdf_search_toast("Upload file is malicious. Please upload valid file.");

            }  else {
                show_pdf_search_toast("Something went wrong. Please try again");
            }

            element.innerText = "Update";
        }
    }
    xhttp.send(params);
}

function start_indexing(element) {

    var start_indexing_element_div = document.getElementById("start_indexing_btn_div");
    var start_indexing_element_btn = start_indexing_element_div.querySelector(".start_indexing_btn");
    start_indexing_element_btn.classList.add("indexing-active");
    var filters = get_url_multiple_vars();
    var bot_pk = filters["bot_pk"][0];

    var json_string = {
        "bot_pk": bot_pk
    };

    json_string = JSON.stringify(json_string);

    encrypted_data = EncryptVariable(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);

    element.innerText = "Starting ...";

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/chat/bot/pdf/start-indexing/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', $('input[name="csrfmiddlewaretoken"]').val());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);

            if(response["status"] == 200) {
                show_pdf_search_toast("PDF Indexing process has been started successfully.");
                $("#pdf-start-indexing-modal").modal("close");
                disable_start_indexing_btn();
                window.ACTIVE_PDF_TABLE.fetch_active_pdf();

            }  else if(response["status"] == 300) {

                show_pdf_search_toast("Elasticsearch Server is not running. Please contact the administrator");
                enable_start_indexing_btn();

            } else if(response["status"] == 301) {

                show_pdf_search_toast("PDF indexing is already in progress. Please wait for a while to start the process again.");
                $("#pdf-start-indexing-modal").modal("close");
                disable_start_indexing_btn();

            } else {
                console.log("Something went wrong. Please try again.");
            }

            element.innerText = "Start";
        }
    }
    xhttp.send(params);
}

function reset_upload_pdf_modal(){
    document.getElementById("pdf_name").value = "";
    document.getElementById("imp_pages").value = "";
    document.getElementById("skipped_pages").value = "";
    handle_file_upload_cross_btn();
    
}

function reset_update_pdf_modal(){
    handle_file_update_cross_btn();
}


function stripHTML(htmlString) {
    return htmlString.replace(/(<([^>]+)[><])/ig, ' ');
}
$(document).ready(function() {
    let filters = get_url_multiple_vars();
    SEARCHED_TEMPLATE = (filters['search_template']) ? filters['search_template'][0] : '';
    update_campaign_progress_bar(CAMPAIGN_CHANNEL);
    update_campaign_sidebar('template');
    initialize_campaign_template_table();
    $('#campaign_template_input_error').hide();
    $('#template_upload_btn').prop("disabled", true );

    $('#message-template-div-outer').scroll(function(){
        $('.table-action-dropdown-menu-list').removeClass('show');
    })
});

function show_create_template_modal() {
    $("#upload_template_modal").modal("hide");
    $('#create_campaign_template_modal').modal('show');
}
function open_upload_template_modal(){
    $('#no-data-found-modal').modal("hide");
    $("#upload_template_modal").modal("show");
    $('#file_upload_bar').hide();
    $('#template_upload_btn').prop("disabled", true );
    $('#upload_template_modal .No-File-Selected-Yet').show();
}
var template_variables_global = {}
let header_variable_global = {}
let dynamic_cta_url_variable_global = {}
FILENAME = ""
SEARCHED_TEMPLATE = ""
SELECTD_VARIABLES = VARIABLES
SELECTD_HEADER_VARIABLE = HEADER_VARIABLE
SELECTD_CTA_VARIABLES = CTA_VARIABLES

class CampaignTemplateTable extends CampaignBase {
    constructor(table_container, searchbar_element, pagination_container) {
        super();
        this.table_container = table_container;
        this.table = null;
        this.options = {
            enable_select_rows: true,
        }

        this.active_user_metadata = {};
        this.pagination_container = pagination_container;
        this.searchbar_element = searchbar_element;

        this.data_checklist = {
            'campaign_data': false,
        };

        this.data_table_obj = null;

        this.init();
    }

    init() {
        var _this = this;
        _this.initialize_table_header_metadata();
        _this.initialize_lead_data_metadata_update_modal();
        _this.fetch_campaign_templates();
    }

    initialize_table_header_metadata() {
        var _this = this;
        _this.active_user_metadata.lead_data_cols = _this.get_table_meta_data();
    }

    initialize_table() {
        var _this = this;

        _this.table_container.innerHTML = '<table class="table table-bordered" id="campaign_template_table" width="100%" cellspacing="0"></table>';
        _this.table = _this.table_container.querySelector("table");

        if (!_this.table) return;
        if (_this.active_user_metadata.lead_data_cols.length == 0) return;
        if(_this.campaign_data.length == 0) {
            _this.options.enable_select_rows = false;
        } else {
            _this.options.enable_select_rows = true;
        }

        _this.initialize_head();
        _this.initialize_body();
        _this.add_event_listeners();
        _this.add_event_listeners_in_rows();
        _this.update_table_attribute([_this.table]);
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
            select_rows_html = [
                '<th>',
                '</th>',
            ].join('');
        }

        var thead_html = [
            '<thead>',
            '<tr>',
            select_rows_html,
            th_html,
            '</tr>',
            '</thead>',
        ].join('');

        _this.table.innerHTML = thead_html;
    }

    initialize_body() {
        var _this = this;

        var campaign_data_list = this.get_rows();

        _this.data_table_obj = $(_this.table).DataTable({
            "data": campaign_data_list,
            "ordering": false,
            "bPaginate": false,
            "bInfo": false,
            "bLengthChange": false,
            "searching": false,
            'columnDefs': [{
                "targets": 0,
                "className": "text-left text-md-center",
                "width": "4%"
            },
            ],
            "drawCallback": function (settings) {
                if($(this).find('.dataTables_empty').length == 1) {
                    $(this).parents('#campaign_template_table_pagination_wrapper_div').hide();
                    $('#table_no_data_found').css("display","flex");
                }
                else{
                    $('#table_no_data_found').hide();
                    $(this).parents('#campaign_template_table_pagination_wrapper_div').show();
                }
            },

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
            },
            createdRow: function (row, data, dataIndex) {
                row.setAttribute("batch_id", _this.campaign_data[dataIndex].batch_id);
            },
        });
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
        _this.fetch_campaign_templates();
    }

    apply_table_pagination() {
        var _this = this;
        if(_this.campaign_data.length == 0) {
            _this.pagination_container.innerHTML = "";
            return;
        }

        var container = _this.pagination_container;
        var metadata = _this.pagination_metadata;
        var onclick_handler = _this.add_filter_and_fetch_data;
        _this.apply_pagination(container, metadata, onclick_handler, _this);
    }

    fetch_campaign_templates() {
        var _this = this;
        active_template_data_loader();

        var filters = get_url_multiple_vars();
        let selected_template_pk = $("input[type='radio'][name='campaign_template']:checked").val();
        if (!selected_template_pk){
            selected_template_pk = parseInt(filters['selected_template_id']);
        }
        var request_params = {
            'page': ((filters["page"] && filters["page"][0]) || 1),
            'bot_pk': filters['bot_pk'][0],
            'campaign_id': filters['campaign_id'][0],
            'searched_template': SEARCHED_TEMPLATE,
            'selected_template_pk': selected_template_pk,
        };

        var json_params = JSON.stringify(request_params);
        var encrypted_data = campaign_custom_encrypt(json_params);
        encrypted_data = {
            "Request": encrypted_data
        };
        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/campaign/get-campaign-templates/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                var response = JSON.parse(this.responseText);
                response = campaign_custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    _this.pagination_metadata = response.pagination_metadata;
                    _this.set_campaign_data(response.campaign_templates);

                    if(!selected_template_pk){
                        selected_template_pk = response.selected_template_pk
                    }
                    update_campaign_template_page_url(selected_template_pk);
                    var radio_elem = document.getElementById('campaign-template-radio-' + selected_template_pk);
                    if (radio_elem) {
                        radio_elem.checked = true;
                        $(radio_elem).parent().parent().css("background-color", "#F1F6FD");
                    }

                    for (var template of response.campaign_templates) {
                        template_variables_global[template['template_pk']] = Array.from(new Set(template['template_variables']));
                        dynamic_cta_url_variable_global[template['template_pk']] = Array.from(new Set(template['dynamic_cta_url_variable']));
                        header_variable_global[template['template_pk']] = Array.from(new Set(template['header_variable']));
                    }
                }
            } else if(this.readyState == 4 && this.status == 403){
                trigger_session_time_out_modal();
            }
            deactive_template_data_loader();
        }
        xhttp.send(params);
    }

    set_campaign_data(campaign_data) {
        var _this = this;
        if (campaign_data) {
            _this.campaign_data = campaign_data;
            _this.data_checklist.campaign_data = true;
        }

        _this.check_and_initialize_table();
    }

    check_and_initialize_table() {
        var _this = this;

        if (_this.data_checklist.campaign_data == false) return false;

        _this.initialize_table();
    }

    get_row_html(name, campaign_data_obj) {
        var _this = this;

        var data = campaign_data_obj[name];
        if(data == null || data == undefined) {
            data = "-";
        }

        var template_pk = campaign_data_obj.template_pk;

        var html = "";
        switch (name) {
            case "template_name":
                html = `<span class="text-capitalize">${data}</span>`;
                break;

            case "created_datetime":
                html = data;
                break;

            case "status":
                html = `<span class="text-capitalize">${data}</span>`;
                break;

            case "type":
                html = `<span class="text-capitalize">${data}</span>`;
                break;
    
            case "category":
                html = `<span class="text-capitalize">${data}</span>`;
                break;
            
            case "language":
                html = `<span class="text-capitalize">${data}</span>`;
                break;

            case "message_type":
                html = `<span class="text-capitalize">${data}</span>`;
                break;

            case "suggested_reply_type":
                html = `<span class="text-capitalize">${data}</span>`;
                break;               

            case "action":
                html = `
                <div class="action-flex-div">
                    <div class="action-dropdown-div-wrapper">
                        <div class="action-btn-data-wrapper btn-group" data-toggle="dropdown">
                            <a class="btn btn-lg dots-btn action-btn">
                                <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <g filter="url(#filter0_d_77_8519)"><rect x="2" y="2" width="24" height="24" rx="4" fill="#FAFAFA" shape-rendering="crispEdges"/><circle cx="14" cy="14" r="1.33333" fill="#2D2D2D"/><circle cx="9.33333" cy="14" r="1.33333" fill="#2D2D2D"/><circle cx="18.6666" cy="14" r="1.33333" fill="#2D2D2D"/></g><defs><filter id="filter0_d_77_8519" x="0" y="0" width="28" height="28" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB"><feFlood flood-opacity="0" result="BackgroundImageFix"/><feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/><feOffset/><feGaussianBlur stdDeviation="1"/><feComposite in2="hardAlpha" operator="out"/><feColorMatrix type="matrix" values="0 0 0 0 0.0416667 0 0 0 0 0.0416667 0 0 0 0 0.0416667 0 0 0 0.15 0"/><feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_77_8519"/><feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_77_8519" result="shape"/></filter></defs>
                                </svg>
                            </a>
                        </div>
                        <div class="dropdown-menu overview-menu-list table-action-dropdown-menu-list dropdown-menu-right">
                            <ul class="list-group custom-popover"> 
                                <li class="list-group-item group-data" onclick="download_campaign_template_modal('${template_pk}')">
                                    <span>Download</span>
                                    <span class="group-data-logo download"> </span>
                                </li>
                                <li class="list-group-item group-data" onclick="show_edit_campaign_template_modal('${template_pk}')">
                                    <span>View</span>
                                    <span class="group-data-logo view"> </span>
                                </li>
                                <li class="list-group-item group-data" onclick="open_delete_template_modal('${template_pk}')">
                                    <span>Delete</span>
                                    <span class="group-data-logo delete"> </span>
                                </li>
                            </ul>
                        </div>  
                    </div>
                </div>
                `;
                break;

            default:
                html = "-";
                console.log("Error: unknown column")
                break;
        }
        return html;
    }

    get_select_row_html(campaign_data_obj) {
        var _this = this;
        const { enable_select_rows } = _this.options;

        if (!enable_select_rows) {
            return "";
        }

        var select_row_html = '<input class="campaign_select_row_cb" type="radio" name="campaign_template" value="' + campaign_data_obj.template_pk + '" id="campaign-template-radio-' + campaign_data_obj.template_pk +'" />';

        return select_row_html;
    }

    get_row(campaign_data_obj) {
        var _this = this;
        const { enable_select_rows } = _this.options;

        var campaign_data_list = [];

        var select_row_html = _this.get_select_row_html(campaign_data_obj);
        if (enable_select_rows) {
            campaign_data_list.push(select_row_html);
        }

        _this.active_user_metadata.lead_data_cols.forEach((column_info_obj) => {
            try {
                if (column_info_obj.selected == false) return;
                var name = column_info_obj.name;
                campaign_data_list.push(_this.get_row_html(name, campaign_data_obj));
            } catch (err) {
                console.log("ERROR get_row on adding row data of column : ", column_info_obj);
            }
        });

        return campaign_data_list;
    }

    get_rows() {
        var _this = this;
        var campaign_data_list = [];
        _this.campaign_data.forEach((campaign_data_obj) => {
            campaign_data_list.push(_this.get_row(campaign_data_obj));
        })
        return campaign_data_list;
    }

    add_event_listeners_in_rows(container = null) {
        var _this = this;
        if (container == null) container = _this.table;

    }

    add_event_listeners() {
        var _this = this;
    }

    initialize_lead_data_metadata_update_modal() {
        var _this = this;
        var lead_data_cols = _this.active_user_metadata.lead_data_cols;
        var container = document.querySelector("#lead_data_table_meta_div");
        var selected_values = [];
        var unselected_values = [];
        lead_data_cols.forEach((obj) => {
            if (obj.selected == true && obj.name != "status") {  // Extra condition added to remove "status" column from message template view
                selected_values.push({
                    'key': obj.name,
                    'value': obj.display_name
                });
            } else if (obj.name != "status") {
                unselected_values.push({
                    'key': obj.name,
                    'value': obj.display_name
                });
            }
        });

        initialize_template_custom_tag_input(selected_values, unselected_values, container)
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
        window.localStorage.setItem("campaign_template_table_meta_data_" + CAMPAIGN_CHANNEL.replace(" ", "_"), JSON.stringify(lead_data_cols));
    }

    get_table_meta_data() {
        var _this = this;
        var lead_data_cols = window.localStorage.getItem("campaign_template_table_meta_data_" + CAMPAIGN_CHANNEL.replace(" ", "_"));
        if (!lead_data_cols) {
            lead_data_cols = _this.get_default_meta_data();
        } else {
            lead_data_cols = JSON.parse(lead_data_cols);
        }
        return lead_data_cols;
    }

    get_default_meta_data() {
        if(CAMPAIGN_CHANNEL == 'RCS') {
            var lead_data_cols = [
                ['template_name', 'Template Name', true],
                ['message_type', 'Message Type', true],
                ['suggested_reply_type', 'Suggested Reply Type', true],
                ['created_datetime', 'Created On', true],
                ['action', 'Actions', true]
            ]
        } else {
            var lead_data_cols = [
                ['template_name', 'Template Name', true],
                ['status', 'Status', false],
                // ['category', 'Categories', true],
                ['type', 'Type', true],
                ['language', 'Language', true],
                ['created_datetime', 'Date & Time', true],
                ['action', 'Actions', true]
            ]
        }

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

function initialize_campaign_template_table() {
    if (window.location.pathname.indexOf("/campaign/create-template") != 0) {
        return;
    }

    var campaign_table_container = document.querySelector("#campaign_template_table_container");
    var campaign_searchbar = document.querySelector("#campaign-template-search-bar");
    var pagination_container = document.getElementById("campaign_template_pagination_div");

    window.CAMPAIGN_TEMPLATE_TABLE = new CampaignTemplateTable(
        campaign_table_container, campaign_searchbar, pagination_container);
}

function save_campaign_template_table_metadata() {

    var lead_data_cols = window.CAMPAIGN_TEMPLATE_TABLE.active_user_metadata.lead_data_cols;

    var selected_values = [];
    var unselected_values = [];
    window.LEAD_DATA_METADATA_INPUT.selected_values.filter((obj) => {
        selected_values.push(obj.key);
    });
    window.LEAD_DATA_METADATA_INPUT.unselected_values.filter((obj) => {
        unselected_values.push(obj.key);
    });


    if (selected_values.length < 2) {
        show_campaign_toast("Atleast two columns needs to be selected.");
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

    window.CAMPAIGN_TEMPLATE_TABLE.update_table_meta_deta(lead_data_cols)
}

function initialize_template_custom_tag_input(selected_values, unselected_values, container) {
    window.LEAD_DATA_METADATA_INPUT = new CognoAICustomTagInput(container, selected_values, unselected_values);
}

function open_delete_template_modal(template_pk) {
    document.getElementById('delete_template_btn').dataset.id = template_pk;

    $('#delete_campaign_template_modal').modal('show');
    document.getElementById("delete-template-error-msg").style.display = 'none';
}


function delete_campaign_template(el) {
    var error_element = document.getElementById("delete-template-error-msg");

    var template_pk = el.dataset.id;

    var json_string = {
        'template_pk': template_pk,
        'bot_pk': get_url_multiple_vars()['bot_pk'][0],
        'campaign_channel': CAMPAIGN_CHANNEL,
    };

    json_string = JSON.stringify(json_string);

    var encrypted_data = campaign_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);

    el.innerText = "Deleting...";

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", '/campaign/delete-campaign-template/', true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if(response["status"] == 200) {

                var error_message = "Template deleted successfully.";
                show_campaign_error_message(error_element, error_message, false);

                initialize_campaign_template_table();
                setTimeout(function() {
                    $('#delete_campaign_template_modal').modal('hide');
                }, 1000);
            } else {
                show_campaign_error_message(error_element, response.message);
            }
            el.innerText = "Delete";
        } else if(this.readyState == 4 && this.status == 403){
            trigger_session_time_out_modal();
        }
    }
    xhttp.send(params);      
}

function add_template_to_campaign(element, variables, is_next_clicked=false) {

    var selected_template_pk = $("input[type='radio'][name='campaign_template']:checked").val();

    if (!selected_template_pk) {
        var error_message = 'Please select a template.';
        show_campaign_toast(error_message);
        return;
    }

    if (is_next_clicked) {
        element.innerText = "Saving...";
    } else {
        element.innerText = "Saving as Draft";
    }

    var request_params = {
        'bot_pk': BOT_ID,
        'campaign_id': get_url_multiple_vars()['campaign_id'][0],
        'selected_template_pk': selected_template_pk,
        'campaign_channel': CAMPAIGN_CHANNEL,
    };

    if (is_next_clicked) {
        let header_variable = variables['header_variable']
        let body_variables = variables['body_variables']
        let cta_variables = variables['cta_variables']
        if (header_variable && header_variable.length > 0){
            request_params['header_variable'] = header_variable
        }
        if (body_variables && body_variables.length > 0){
            request_params['variables'] = body_variables
        }
        if (cta_variables && cta_variables.length > 0){
            request_params['dynamic_cta_url_variable'] = cta_variables
        }
    }
    var json_params = JSON.stringify(request_params);
    var encrypted_data = campaign_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/campaign/add-template-to-campaign/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                var campaign_id = response["campaign_id"]
                if (is_next_clicked) {
                    setTimeout(function() {
                        var template_url = window.location.origin + '/campaign/review/?bot_pk=' + BOT_ID + '&campaign_id=' + campaign_id;
                        SELECTD_VARIABLES = variables['body_variables']
                        SELECTD_HEADER_VARIABLE = variables['header_variable']
                        SELECTD_CTA_VARIABLES = variables['cta_variables']
                        window.location.href = template_url;
                    }, 1000);
                }
                else {
                    window.location.href = window.location.origin + '/campaign/dashboard/?bot_pk=' + BOT_ID;
                }
                var error_message = "Campaign has been saved successfully";
                show_campaign_toast(error_message);
            } else {
                var error_message = response.message;
                show_campaign_toast(error_message);
            }
            if(!is_next_clicked) {
                element.innerText = "Save as Draft";
            }
        } else if(this.readyState == 4 && this.status == 403){
            trigger_session_time_out_modal();
        }
    }
    xhttp.send(params);
}


var template_file_global = undefined;

if (document.getElementById("campaign-template-file-upload")) {
    document.getElementById("campaign-template-file-upload").addEventListener('change', function(event) {
        var file = document.getElementById("campaign-template-file-upload").files[0];
        
        if(file) {
            template_file_global = ($("#campaign-template-file-upload"))[0].files[0];
            
            FILENAME = file.name;
            var is_file_valid = true;
            var files_validation_error = '';
            if (check_file_extension(FILENAME) == false) {
                is_file_valid = false;
                files_validation_error = "file_extension";
            } else if(check_malicious_file(FILENAME).status) {
                is_file_valid = false;
                files_validation_error = "malicious_file";
            }
    
            var upload_error = document.getElementById('campaign_template_input_error');
    
            if(is_file_valid == false) {
                $('#file_upload_bar').hide();
                let html = `<p class="mb-0" ><span  style="font-weight: 700;">Error:</span>`
                if(files_validation_error == "file_size") {
                    html += `File size cannot exceed 5 MB.`;
                } else if(files_validation_error == "malicious_file") {
                    document.getElementById('uploaded_template_file_errors').style.display = 'none';
                    html += ` Please do not use (dot) except for extension.`;
                } else {
                    html += `The file could not be uploaded. Only files with the following extensions are allowed: XLS and XLSX.`;
                }
                html += `</p>`
                upload_error.innerHTML = html
                upload_error.style.color = "red";
                $('#campaign_template_input_error').show();
                return;
            } else {
                upload_error.style.display = 'none'
                $('#template_upload_btn').prop( "disabled", false );
            }
    
            if(FILENAME.length > 30) FILENAME = FILENAME.substr(0, 30) + "...";
            let wrapper_element = document.getElementById('file-wrapper-div-error-id');
            wrapper_element.classList.remove("file-wrapper-div-error");
            document.getElementById('uploaded_template_file_errors').style.display = 'none';
            $('#upload_template_modal .No-File-Selected-Yet').hide();
            $('#upload_template_modal .file-name-div').html(FILENAME);
            $('#sub-heding-section-text').html("File Added")
            $('#upload_template_modal .modal-upload-file').show();
            $('#upload_template_modal .progress').show();
    
            var progress_div = $('#upload_template_modal .progress')[0].children[0];
            progress_div.classList.remove('determinate');
            progress_div.classList.add('indeterminate');
            setTimeout(function() {
                progress_div.classList.remove('indeterminate');
                progress_div.classList.add('determinate');
            }, 300);
        } else {
            if(template_file_global == undefined){
                $('#upload_template_modal .file-name-div').html("No file selected");
                $('#upload_template_modal .progress').hide();
            }
        }
    });    
}

function remove_uploaded_template_file() {
    let wrapper_element = document.getElementById('file-wrapper-div-error-id');
    wrapper_element.classList.remove("file-wrapper-div-error");
    $('#upload_template_modal .No-File-Selected-Yet').show();
    $('#sub-heding-section-text').html("")
    $('#upload_template_modal .file-name-div').html("");
    $('#upload_template_modal .modal-upload-file').hide();
    $('#template_upload_btn').prop( "disabled", true );
    document.getElementById("campaign-template-file-upload").value = "";
    template_file_global = undefined;

    document.getElementById('uploaded_template_file_errors').style.display = 'none';
    document.getElementById('uploaded_template_file_errors').innerHTML = '<p style="font-weight: 500;">Uploaded File contains following error(s):</p>';
}

function download_sample_campaign_template() {
    var json_string = {};

    json_string = JSON.stringify(json_string);

    var encrypted_data = campaign_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/campaign/download-sample-campaign-template/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if(response["status"] = 200) {
                if(response["export_path"] == null) {
                    alert("Sorry, unable to process your request. Kindly try again later.");
                } else {
                    if(response["export_path_exist"]) {
                        window.open(response["export_path"], "_self");
                    } else {
                        alert("Requested data doesn't exists. Kindly try again later.");
                    }
                }
            }
        } else if(this.readyState == 4 && this.status == 403){
            trigger_session_time_out_modal();
        }
    }

    xhttp.send(params);
}


function upload_campaign_template_file(el) {
    document.getElementById("uploaded_template_file_errors").innerHTML = "";

    var file = template_file_global;

    if (file == undefined || file == null) {
        show_campaign_toast("Please choose a file.");
        return;
    }

    var malicious_file_report = check_malicious_file(file.name)
    if (malicious_file_report.status == true) {
        show_campaign_toast(malicious_file_report.message)
        return false
    }

    if (check_file_extension(file.name) == false) {
        return false;
    }

    el.innerText = "Uploading..."
    // show_campaign_toast('Your file is being uploaded. Please wait, it may take some time..')
    var reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = function() {

        var base64_str = reader.result.split(",")[1];

        var json_string = {
            "filename": file.name,
            "base64_file": base64_str,
            "bot_pk": get_url_multiple_vars()['bot_pk'][0],
        };

        json_string = JSON.stringify(json_string);

        var encrypted_data = campaign_custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", '/campaign/upload-template/', true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                var response = JSON.parse(this.responseText);
                response = campaign_custom_decrypt(response.Response);
                response = JSON.parse(response);

                if(response["status"] == 200) {

                    $('#upload_campaign_batch_modal').modal('hide');
                    $('#save-template-error-message').hide();
                    remove_uploaded_template_file();
                    $("#upload_template_modal").modal("hide");
                    $('#save_template_btn').prop('disabled', false);
                    if (response.template_exist_rows.length > 0){
                        $('#save_template_btn').prop('disabled', true)
                        $('#save-template-error-message').show();
                        let error_container = document.getElementById("save-template-error-message");
                        let error_html = '<p class="mb-0" style="font-weight: 450;"><span  style="font-weight: 700;">Error: </span>';
                        error_html += 'The highlighted template name with same language already exists on the dashboard. Please delete the existing template and re-upload this file.'
                        error_html += '</p>'
                        error_container.innerHTML = error_html;
                    }
                    set_template_preview_modal(response.sample_data, response.original_file_name, response.file_path, response.template_exist_rows);
                    

                } else if(response.status == 403){
                    $("#upload_template_modal").modal("hide");
                    $('#no-data-found-modal').modal('show');
                    $('#no-data-found-file').html(FILENAME)
                    
                } else if (response.status == 400) {

                    var row_errors = response['row_errors'];
                    var error_no = 1;
                    let wrapper_element = document.getElementById('file-wrapper-div-error-id');
                    $('#template_upload_btn').prop("disabled", true );
                    wrapper_element.classList.add("file-wrapper-div-error");
                    $('#sub-heding-section-text').html(`Error(s) in the uploaded file!`)
                    if (row_errors.length > 0) {
                        $('#uploaded_template_file_errors').append(`<p style="font-weight: 500;">Uploaded File contains following error(s):</p>`)
                        for (error of row_errors) {
                            $('#uploaded_template_file_errors').append(`<p class="upload-batch-error-text"'>${error_no}. ${error}</p>`);
                            ++error_no;
                        }
                    }

                    document.getElementById('uploaded_template_file_errors').style.display = 'block';
                } else {
                    document.getElementById('campaign_template_input_error').innerHTML = '<p class="mb-0" ><span  style="font-weight: 700;">Error:</span>Please upload valid file</p>';
                    document.getElementById('campaign_template_input_error').style.color = 'red';
                    document.getElementById('campaign_template_input_error').style.display = 'block';
                }

                el.innerText = "Upload";
            } else if(this.readyState == 4 && this.status == 403){
                trigger_session_time_out_modal();
            }
        }
        xhttp.send(params);
    };

    reader.onerror = function(error) {
        console.log('Error: ', error);
    };
}
DATA_TABLE_INITIALIZED = false
function set_template_preview_modal(sample_data, file_name, file_path, template_exist_rows) {
    // sample_data_global = sample_data
    document.getElementById('new-template-file-name').innerHTML = file_name;
    document.getElementById('new_template_file_path').value = file_path;

    update_template_preview_table(sample_data, template_exist_rows);
    $('#new_template_uploaded_modal').modal('show');
    if (!DATA_TABLE_INITIALIZED){
        DATA_TABLE_INITIALIZED = true
        $('#new_template_table_div').DataTable({
            "ordering": false,
            "bPaginate": false,
            "bInfo": false,
            "bLengthChange": false,
            "searching": false,
        
            "drawCallback": function (settings) {
                $('[data-toggle="tooltip"]').tooltip({
                    container: 'body',
                    boundary: 'window',
                });        
            }
        });
    }
    $('#new_template_uploaded_modal').on('shown.bs.modal', function (e){
        $('#new_template_uploaded_modal .new-batch-table-preview-div').scrollLeft(0);
        $('#new_template_uploaded_modal .new-batch-table-preview-div').scrollTop(0);
        });
}

function update_template_preview_table(template_data_list, template_exist_rows) {
    var table_container = document.getElementById("new_template_table_div");
    var tbody_element = table_container.querySelector("tbody");
    var html = "";
    if (template_exist_rows.length > 0){
        let alert_svg = `<svg width="15" height="14" viewBox="0 0 15 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M6.65227 2.4756C7.19771 2.18518 7.87862 2.35393 8.21321 2.84888L8.25665 2.91838L12.3268 9.9823C12.4238 10.1505 12.4746 10.3397 12.4746 10.532C12.4746 11.1326 11.9893 11.6241 11.3751 11.664L11.2943 11.6666H3.15512C2.9551 11.6666 2.75835 11.6178 2.58336 11.5246C2.03789 11.2343 1.82541 10.5899 2.08432 10.0547L2.12256 9.98242L6.19159 2.9185C6.29888 2.73224 6.45852 2.57876 6.65227 2.4756ZM11.6385 10.3488L7.56832 3.28488C7.46304 3.10216 7.2236 3.03608 7.03352 3.13728C6.98509 3.16307 6.94305 3.1983 6.90996 3.24049L6.87996 3.28492L2.81093 10.3488C2.70568 10.5316 2.77445 10.7617 2.96453 10.8629C3.00828 10.8862 3.05611 10.9012 3.10542 10.9072L3.15512 10.9102H11.2943C11.5116 10.9102 11.6877 10.7409 11.6877 10.532C11.6877 10.484 11.6782 10.4365 11.6598 10.3921L11.6385 10.3488L7.56832 3.28488L11.6385 10.3488ZM7.22461 9.14183C7.51394 9.14183 7.74848 9.3673 7.74848 9.64543C7.74848 9.92355 7.51394 10.149 7.22461 10.149C6.93528 10.149 6.70074 9.92355 6.70074 9.64543C6.70074 9.3673 6.93528 9.14183 7.22461 9.14183ZM7.22241 5.35869C7.42159 5.35854 7.58631 5.5007 7.61252 5.68528L7.61615 5.73659L7.61804 8.0066C7.61822 8.21548 7.44221 8.38494 7.22492 8.38511C7.02575 8.38526 6.86102 8.24311 6.83481 8.05853L6.83118 8.00721L6.82929 5.7372C6.82912 5.52832 7.00512 5.35886 7.22241 5.35869Z" fill="#E10E00"/>
                        </svg>`
        $('.add_alert_svg_in_template_header_lang').html(alert_svg + '&nbsp&nbsp&nbsp Language')
        $('.add_alert_svg_in_template_header_temp_name').html(alert_svg + '&nbsp&nbsp&nbsp Template Name')
    }else{
        $('.add_alert_svg_in_template_header_lang').html('Language')
        $('.add_alert_svg_in_template_header_temp_name').html('Template Name')
    }

    for(var idx = 0; idx < template_data_list.length; idx ++) {
        var template_data = template_data_list[idx];

        var template_type = (template_data.type || "-");
        var template_category = (template_data.category || "-");
        var template_language = (template_data.language || "-");
        var template_body = (template_data.template_body || "-");
        var template_header = (template_data.template_header || "-");
        var template_footer = (template_data.template_footer || "-");
        var template_name = (template_data.template_name || "-");
        var template_attachment = (template_data.template_attachment || "-");
        var template_cta_text = (template_data.template_cta_text || "-");
        var template_cta_link = (template_data.template_cta_link || "-");
        var template_button_type = (template_data.template_button_type || "-");
        var template_callus_text = (template_data.template_callus_text || "-");
        var template_callus_number = (template_data.template_callus_number || "-");
        var template_qr_1 = (template_data.template_qr_1 || "-");
        var template_qr_2 = (template_data.template_qr_2 || "-");
        var template_qr_3 = (template_data.template_qr_3 || "-");
        var document_file_name = (template_data.document_file_name || "-");
        
        html += "<tr>";
        html += "<td class='message-body-template-div'><span class='text-capitalize'>" + template_type + "</span></td>";
        if(template_exist_rows, template_exist_rows.includes(idx+1)){
            html += "<td class='note-text-div--red message-body-template-div'><span class='note-text-div--red text-capitalize' style='padding: 14px 6px!important;'>" + template_language + "</span></td>";
            html += "<td class='note-text-div--red message-body-template-div'><span class=' note-text-div--red text-capitalize' style='padding: 14px 6px!important;'>" + template_name + "</span></td>";
        }else{
            html += "<td class='message-body-template-div'><span class='text-capitalize' style='padding: 14px 6px!important;'>" + template_language + "</span></td>";
            html += "<td class='message-body-template-div'><span class='text-capitalize' style='padding: 14px 6px!important;'>" + template_name + "</span></td>";
        }
        html += "<td class='message-body-template-div'><span class='text-capitalize'>" + template_category + "</span></td>";
        template_body = sanitize_html(template_body)
        html += `<td class="message-body-template-div "><span class="message-body-template-div">  ${template_body} </span></td>`;
        template_header = sanitize_html(template_header)
        html += `<td class="message-body-template-div"><span class="message-body-template-div">  ${template_header} </span></td>`;
        template_footer = sanitize_html(template_footer)
        html += `<td class="message-body-template-div"><span class="message-body-template-div">  ${template_footer} </span></td>`;
        html += "<td class='message-body-template-div'>" + template_button_type + "</td>";
        html += "<td class='message-body-template-div'>" + template_cta_text + "</td>";
        if(template_cta_link.length > 97){
           html += "<td><span class='table-tooltipped-wrapper-1' data-toggle='tooltip' title='"+ template_cta_link +"'>" + template_cta_link + "</span></td>";
        } else {
                html += "<td><span class='table-tooltipped-wrapper-1'>" + template_cta_link + "</span></td>";
            }
        html += "<td class='message-body-template-div'>" + template_callus_text + "</td>";
        html += "<td class='message-body-template-div'>" + template_callus_number + "</td>";
        html += "<td class='message-body-template-div'>" + template_qr_1 + "</td>";
        html += "<td class='message-body-template-div'>" + template_qr_2 + "</td>";
        html += "<td class='message-body-template-div'>" + template_qr_3 + "</td>";
        if(template_attachment.length > 97){
           html += "<td><span class='table-tooltipped-wrapper-1' data-toggle='tooltip' title='"+template_attachment+"'>" + template_attachment + "</span></td>";
        } else {
                html += "<td><span class='table-tooltipped-wrapper-1'>" +template_attachment+ "</span></td>";
            }
        html += "<td class='message-body-template-div'>" +  document_file_name + "</td>";
        html += "</tr>";
    }

    tbody_element.innerHTML = html;
}


function delete_template_file () {

    var file_path = document.getElementById('new_template_file_path').value;

    var json_string = {
        'file_path': file_path,
        'bot_pk': get_url_multiple_vars()['bot_pk'][0],
    };

    json_string = JSON.stringify(json_string);

    var encrypted_data = campaign_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", '/campaign/delete-template-file/', true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if(response["status"] == 200) {
                show_campaign_toast('File deleted successfully.');
                $('#new_template_uploaded_modal').modal('hide');
                $('#upload_template_modal').modal('show');

            } else {
                show_campaign_toast(response.message)
            }
        } else if(this.readyState == 4 && this.status == 403){
            trigger_session_time_out_modal();
        }
    }
    xhttp.send(params);   
}

function save_campaign_template(el) {
    var error_container = document.getElementById("save-template-error-message");

    var file_path = document.getElementById('new_template_file_path').value;
    var file_name = document.getElementById('new-template-file-name').innerHTML;

    var json_string = {
        'file_path': file_path,
        'file_name': file_name,
        'bot_pk': get_url_multiple_vars()['bot_pk'][0],
    };

    json_string = JSON.stringify(json_string);

    var encrypted_data = campaign_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);

    el.innerText = "Saving...";

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", '/campaign/save-template/', true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if(response["status"] == 200) {

                let error_data = response["error_data"];
                let is_error_occured = false;
                if (error_data.error || error_data.template_name_exist.length){
                    let error_html = '<p class="mb-0" style="font-weight: 450;"><span  style="font-weight: 700;">Error: </span>';

                    if(error_data.error) {
                        is_error_occured = true;
                        error_html += error_data["error"];
                    }

                    if(error_data.template_name_exist.length > 0) {
                        is_error_occured = true;
                        error_html += "Not able to upload this template/s because of an already existing Template Name<br>";
                        for(var idx = 0; idx < error_data.template_name_exist.length; idx ++) {
                            var template_name = error_data.template_name_exist[idx];
                            error_html += template_name + " for the " + error_data.template_language_exist_list[idx] + " Language" + "<br>";
                        }
                    }
                    error_html += '</p>'
                    error_container.innerHTML = error_html;
                }
                initialize_campaign_template_table();

                if(is_error_occured == false) {
                    $('#new_template_uploaded_modal').modal('hide');
                    $('#upload_template_modal').modal('hide');
                    show_campaign_toast('Template uploaded successfully.');
                }else{
                    $('#save_template_btn').prop('disabled', true)
                }

            } else {
                show_campaign_toast("Not able to save template. Please try agian");
            }
            el.innerText = "Save Template";
        } else if(this.readyState == 4 && this.status == 403){
            trigger_session_time_out_modal();
        }
    }
    xhttp.send(params);
}

function download_campaign_template_modal(template_pk) {

    var json_string = {
        'template_pk': template_pk,
        'bot_pk': get_url_multiple_vars()['bot_pk'][0],
    };

    json_string = JSON.stringify(json_string);

    var encrypted_data = campaign_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", '/campaign/download-campaign-template/', true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if(response["status"] == 200) {
                if(response["download_file_path"]){
                    window.location.href = window.location.origin + response["download_file_path"]
                    show_campaign_toast("Campaign template file downloaded successfully");
                }else{
                    show_campaign_toast("This template file is not available for download");
                }
            } else {
                show_campaign_toast("Unable to download campaign template file")
            }

        } else if(this.readyState == 4 && this.status == 403){
            trigger_session_time_out_modal();
        }
    }
    xhttp.send(params);      
}

function show_edit_campaign_template_modal(template_pk) {
    var json_string = {
        'template_pk': template_pk,
        'bot_pk': get_url_multiple_vars()['bot_pk'][0],
        'campaign_channel': CAMPAIGN_CHANNEL
    };
    json_string = JSON.stringify(json_string);

    var encrypted_data = campaign_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", '/campaign/get-campaign-template-details/', true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if(response["status"] == 200) {
                if (CAMPAIGN_CHANNEL == 'RCS') {
                    set_edit_rcs_campaign_template_modal(response.template_data)
                } else {
                    set_edit_campaign_template_modal(response.template_data);
                }
            } else {
                show_campaign_toast(response.message);
            }
        } else if(this.readyState == 4 && this.status == 403){
            trigger_session_time_out_modal();
        }
    }
    xhttp.send(params);
}

function set_edit_campaign_template_modal(template_data) {
    var base_obj = new CampaignBase();

    var table_container = document.getElementById("edit_template_table_div");
    var edit_template_table = table_container.querySelector("table");
    var tbody_element = table_container.querySelector("tbody");

    var template_type = (template_data.type || "-");
    var template_category = (template_data.category || "-");
    var template_language = (template_data.language || "-");
    var template_body = (template_data.template_body || "-");
    var template_header = (template_data.template_header || "-");
    var template_footer = (template_data.template_footer || "-");
    var template_name = (template_data.template_name || "-");
    var template_cta_text = (template_data.cta_text || "-");;
    var template_cta_link = (template_data.cta_link || "-");;
    var template_button_type = (template_data.template_button_type || "-");
    var template_callus_text = (template_data.template_callus_text || "-");
    var template_callus_number = (template_data.template_callus_number || "-");
    var template_qr_1 = (template_data.template_qr_1 || "-");
    var template_qr_2 = (template_data.template_qr_2 || "-");
    var template_qr_3 = (template_data.template_qr_3 || "-");
    var template_attachment = (template_data.attachment_src || "-");
    var document_file_name = (template_data.document_file_name || "-");
    
    html = "<tr>";
    html += "<td class='message-body-template-div'><span class='text-capitalize'>" + template_type + "</span></td>";
    html += "<td class='message-body-template-div'><span class='text-capitalize'>" + template_language + "</span></td>";
    html += "<td class='message-body-template-div'><span class='text-capitalize'>" + template_name + "</span></td>";
    html += "<td class='message-body-template-div'><span class='text-capitalize'>" + template_category + "</span></td>";
    html += '<td class="message-body-template-div">' + template_body + '</td>';
    html += '<td class="message-body-template-div">' + template_header + '</td>';
    html += '<td class="message-body-template-div">'+ template_footer + '</td>';
    html += "<td class='message-body-template-div'>" + template_button_type + "</td>";
    html += "<td class='message-body-template-div'>" + template_cta_text + "</td>";
    if(template_cta_link.length > 97){
         html += "<td><span class='table-tooltipped-wrapper-1' data-toggle='tooltip' title='"+template_cta_link+"'>" + template_cta_link + "</span></td>";
    } else {
          html += "<td><span class='table-tooltipped-wrapper-1'>" +template_cta_link+ "</span></td>";
    }
    html += "<td class='message-body-template-div'>" + template_callus_text + "</td>";
    html += "<td class='message-body-template-div'>" + template_callus_number + "</td>";
    html += "<td class='message-body-template-div'>" + template_qr_1 + "</td>";
    html += "<td class='message-body-template-div'>" + template_qr_2 + "</td>";
    html += "<td class='message-body-template-div'>" + template_qr_3 + "</td>";
    if(template_attachment.length > 97){
        html += "<td><span class='table-tooltipped-wrapper-1' data-toggle='tooltip' title='"+template_attachment+"'>" + template_attachment + "</span></td>";
    } else {
        html += "<td><span class='table-tooltipped-wrapper-1'>" +template_attachment+ "</span></td>";
    }
    html += "<td class='message-body-template-div'>" + document_file_name + "</td>";
    html += "</tr>";

    tbody_element.innerHTML = html;

    base_obj.update_table_attribute([edit_template_table]);

    document.getElementById("edit-template-name").innerHTML = template_name;
    $("#edit_campaign_template_modal").modal("show");
    $('[data-toggle="tooltip"]').tooltip({
        container: 'body',
        boundary: 'window'
        });
    $('#edit_campaign_template_modal').on('shown.bs.modal', function (e){
      $('#edit_template_table_div').scrollLeft(0);
      $('#edit_template_table_div').scrollTop(0);
    });
    document.getElementById("edit-template-delete-svg-btn").dataset.template_id = template_data.template_pk;
}

function get_clean_template_variable(value) {
    let clean_value = value.replace("&amp;","&").replace("&lt;","<").replace("&gt;",">").replace("&#039;","'");
    clean_value = remove_special_characters_from_str(clean_value).replace(/[\s_]/g,"").toLowerCase();
    clean_value = clean_value.replace(/[+@“]/g,"");
    return clean_value
}

function set_template_variables() {
    var selected_template_pk = $("input[type='radio'][name='campaign_template']:checked").val();

    if (!selected_template_pk) {
        var error_message = 'Please select a template.';
        show_campaign_toast(error_message);
        return;
    }
 
    var variables = template_variables_global[selected_template_pk]
    let dynamic_cta_url_variable_variable = dynamic_cta_url_variable_global[selected_template_pk]
    let header_variable = header_variable_global[selected_template_pk]
    if ((!variables || variables.length == 0) && (!dynamic_cta_url_variable_variable || dynamic_cta_url_variable_variable.length == 0) && (!header_variable || header_variable.length == 0)) {
        add_template_to_campaign(document.getElementById('save_template_next_btn'), {}, true);
    } else {
        var option_html = ''
        for (header of HEADER_FIELDS) {
            option_html += `<option value='${header}'>${header.replace('*', '')}</option>`
        }

        var map_variable_html = ''
        let map_dynamic_cta_url_variable_variable_html = ''
        let header_variable_html = ''

        if (selected_template_pk != SELECTED_TEMPLATE_PK) {
            VARIABLES = []
            CTA_VARIABLES = []
            HEADER_VARIABLE = []
            let header_fields_list = []
            for (header of HEADER_FIELDS) {
                header = sanitize_html(header).replace('&quot;','"');
                header_fields_list.push(get_clean_template_variable(header));
            }

            for (selected_val of variables) {
                cleaned_variable = get_clean_template_variable(selected_val)
                let index = header_fields_list.indexOf(cleaned_variable)
                if (index > -1) {
                    VARIABLES.push(HEADER_FIELDS[index])
                } else {
                    VARIABLES.push("")
                }
            }
    
            for (selected_val of dynamic_cta_url_variable_variable) {
                cleaned_variable = get_clean_template_variable(selected_val)
                let index = header_fields_list.indexOf(cleaned_variable)
                if (index > -1) {
                    CTA_VARIABLES.push(HEADER_FIELDS[index])
                } else {
                    CTA_VARIABLES.push("")
                }
            }
    
            for (selected_val of header_variable) {
                cleaned_variable = get_clean_template_variable(selected_val)
                let index = header_fields_list.indexOf(cleaned_variable)
                if (index > -1) {
                    HEADER_VARIABLE.push(HEADER_FIELDS[index])
                } else {
                    HEADER_VARIABLE.push("")
                }
            }
        } else {
            VARIABLES = SELECTD_VARIABLES
            CTA_VARIABLES = SELECTD_CTA_VARIABLES
            HEADER_VARIABLE = SELECTD_HEADER_VARIABLE
        }


        if(header_variable.length < 1){
            document.getElementById("template_map_header_variable_table").style.setProperty('display', 'none', 'important');
        }else{
            for (variable of header_variable) {
                header_variable_html += get_map_header_variable_body(variable, option_html);
            }
            document.getElementById("template_map_header_variable_table").style.setProperty('display', 'flex', 'important');
        }
        
        if (variables.length < 1){
            document.getElementById("template_map_variable_body_table").style.setProperty('display', 'none', 'important');
        }else{
            for (variable of variables) {
                map_variable_html += get_map_variable_body(variable, option_html);
            }
            document.getElementById("template_map_variable_body_table").style.setProperty('display', 'flex', 'important');
        }
        
        if (dynamic_cta_url_variable_variable.length < 1){
            document.getElementById("template_map_dynamic_cta_url_variable_variable_body_table").style.setProperty('display', 'none', 'important');
        }else{
            for (variable of dynamic_cta_url_variable_variable){
                map_dynamic_cta_url_variable_variable_html += get_map_cta_variable_body(variable, option_html);
            }
            document.getElementById("template_map_dynamic_cta_url_variable_variable_body_table").style.setProperty('display', 'flex', 'important');
        }
        
        $('#template_map_dynamic_cta_url_variable_variable_body').html(map_dynamic_cta_url_variable_variable_html);
        $('#template_map_variable_body').html(map_variable_html);
        $('#template_map_header_variable_body').html(header_variable_html);
        $('#map_template_variable_modal').modal('show');
        $('[data-toggle="tooltip"]').tooltip({
            container: 'body',
            boundary: 'window'
            });
        if (variables.length > 0) {
            var elems = document.querySelectorAll('.form-control.template_variable_values');
            var itr = 0;
            for (elem of elems) {
                new EasyassistCustomSelect2(elem, "Choose Value", null);

                elem.value = VARIABLES[itr]
                var change_event = new Event('change');
                elem.dispatchEvent(change_event);

                ++itr;
            }
        }

        if (dynamic_cta_url_variable_variable.length > 0) {
            let elems = document.querySelectorAll('.form-control.template_cta_variable_values');
            let itr = 0;
            for (elem of elems) {
                new EasyassistCustomSelect2(elem, "Choose Value", null);

                elem.value = CTA_VARIABLES[itr]
                let change_event = new Event('change');
                elem.dispatchEvent(change_event);

                ++itr;
            }
        }

        if (header_variable.length > 0) {
            let elems = document.querySelectorAll('.form-control.template_header_variable_values');
            let itr = 0;
            for (elem of elems) {
                new EasyassistCustomSelect2(elem, "Choose Value", null);

                elem.value = HEADER_VARIABLE[itr]
                let change_event = new Event('change');
                elem.dispatchEvent(change_event);

                ++itr;
            }
        }
    }
}

function get_map_variable_body(variable, option_html) {
    var html = `<tr>
                <td class="align-left  variable-name"><span class="variable-name-tooltip" data-toggle="tooltip" title="${variable}">${variable}</span></td>
                <td class="align-middle variable-data">
                    <select class="form-control template_variable_values">
                        ${option_html}
                    </select>
                </td>
            </tr>`

    return html;
}

function get_map_cta_variable_body(variable, option_html) {
    var html = `<tr>
                <td class="align-left variable-name"><span class="variable-name-tooltip" data-toggle="tooltip" title="${variable}">${variable}</span></td>
                <td class="align-middle variable-data">
                    <select class="form-control template_cta_variable_values">
                        ${option_html}
                    </select>
                </td>
            </tr>`

    return html;
}

function get_map_header_variable_body(variable, option_html) {
    var html = `<tr>
                <td class="align-left  variable-name"><span class="variable-name-tooltip" data-toggle="tooltip" title="${variable}">${variable}</span></td>
                <td class="align-middle variable-data">
                    <select class="form-control template_header_variable_values">
                        ${option_html}
                    </select>
                </td>
            </tr>`

    return html;
}

function map_template_variables() {

    var body_elems = document.querySelectorAll('.form-control.template_variable_values');
    let cta_elems = document.querySelectorAll('.form-control.template_cta_variable_values');
    let header_elems = document.querySelectorAll('.form-control.template_header_variable_values');

    let variables_values = {'header_variable': [], 'body_variables': [], 'cta_variables': []}

    for (i=0; i<header_elems.length; ++i) {
        let value = header_elems[i].value;

        if (!value || value == 'none') {
            show_campaign_toast('The Header Variable values cannot be empty, please select the valid column below.');
            return;
        }
        variables_values['header_variable'].push(value);
    }

    for (i=0; i<body_elems.length; ++i) {
        var value = body_elems[i].value;

        if (!value || value == 'none') {
            show_campaign_toast('The Body Variable values cannot be empty, please select the valid column below.');
            return;
        }
        variables_values['body_variables'].push(value);
    }
    for (i=0; i<cta_elems.length; ++i) {
        let value = cta_elems[i].value;

        if (!value || value == 'none') {
            show_campaign_toast('The CTA Variable values cannot be empty, please select the valid column below.');
            return;
        }
        variables_values['cta_variables'].push(value);
    }
    
    add_template_to_campaign(document.getElementById('save_template_next_btn'), variables_values, true);
}

function apply_template_search() {
    let searched_template = document.getElementById("campaign-template-search-bar").value.trim();
    document.getElementById("campaign-template-search-bar").value = searched_template;

    // Changed template pagination on search input change.
    let filters = get_url_multiple_vars();
    filters.page = ['1'];
    window.CAMPAIGN_TEMPLATE_TABLE.update_url_with_filters(filters);

    if (searched_template != "") {
        SEARCHED_TEMPLATE = searched_template
    } else {
        SEARCHED_TEMPLATE = "";
    }
    initialize_campaign_template_table();
}

const search_campaign_template = debounce(function() {
    apply_template_search();
})

document.getElementById("campaign-template-search-bar").addEventListener("search", function(event) {
    apply_template_search()
});

function active_template_data_loader(){
    $('#no-data-loader').show();
    $('#campaign_template_table').hide();
    $('#campaign_template_pagination_div').hide();
    $('#message-template-div-outer').hide();
    $('#table_no_data_found').hide();
    $('#save_template_next_btn').prop('disabled', true);
    $('#new_rcs_template_btn').prop('disabled', true);
    $('.custom_metadata_btn').prop('disabled', true);
}

function deactive_template_data_loader(){
    $('#no-data-loader').hide();
    $('#campaign_template_table').show();
    $('#campaign_template_pagination_div').show();
    $('#message-template-div-outer').show();
    $('#save_template_next_btn').prop('disabled', false);
    $('#new_rcs_template_btn').prop('disabled', false);
    $('.custom_metadata_btn').prop('disabled', false);
}

$(document).on('change', '#campaign_template_table td input', function() {
    if(this.checked) {
        let selected_template_pk = $("input[type='radio'][name='campaign_template']:checked").val();
        update_campaign_template_page_url(selected_template_pk);
        $("#campaign_template_table tbody tr").css("background-color", "#fff");
        $(this).parent().parent().css("background-color", "#F1F6FD");
    }
})

function update_campaign_template_page_url(selected_template_pk){
    let filters = get_url_multiple_vars();
    let filters_page = filters['page'];
    if (!filters_page){
        filters_page = 1;
    }
    let newurl = `${window.location.protocol}//${window.location.host}${window.location.pathname}?bot_pk=${filters['bot_pk']}&campaign_id=${filters['campaign_id']}&selected_template_id=${selected_template_pk}&page=${filters_page}`;
    if (SEARCHED_TEMPLATE){
        $("#campaign-template-search-bar").val(SEARCHED_TEMPLATE)
        newurl += `&search_template=${SEARCHED_TEMPLATE}`;
    }
    window.history.pushState({ path: newurl }, '', newurl);
}
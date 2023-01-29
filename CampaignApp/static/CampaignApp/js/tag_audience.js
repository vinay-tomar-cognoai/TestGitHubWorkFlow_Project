let ERROR_FILE_PATH = ""
let ERROR_FILE_NAME = ""
let AUTO_DELETE_CONFIRM = false
let ERROR_ROWS = []
let UPLOADING_PROCESS_RUNNING = null
let SEARCHED_BATCH = ""
let SELECTED_CAMPAIGN_ID = ""

$(document).ready(function() {
    if(window.location.href.includes('tag-audience')) {
        let filters = get_url_multiple_vars()
        SEARCHED_BATCH = (filters['search_batch']) ? filters['search_batch'][0] : '';
        SELECTED_CAMPAIGN_ID = (filters['selected_campaign']) ? filters['selected_campaign'][0] : '';
        update_campaign_progress_bar(CAMPAIGN_CHANNEL);
        update_campaign_sidebar('audience')
        initialize_tag_audience_table();

        $('.delete-file-svg').tooltip();
    }

    $('#tag-audience-div-outer').scroll(function(){
        $('.table-action-dropdown-menu-list').removeClass('show');
    })
})

var campaign_batches_global = {}

/*
    ActiveCampaignsTable 

    Description :
        - This class is used to do manage active campaign table in dashboard

    Required Parameters : 

        lead_data_cols : column confogurations 
            - received in console meta data - get_active_agent_console_settings
            - window.ACTIVE_AGENT_METADATA.lead_data_cols
        campaign_data : list of campaign information object
            - received in fetch_active_campaign response
        table : active lead table
            - tms_active_lead_table

    initialization : 
        - This is initialized in fetch_active_campaign api response
        - window.ACTIVE_CAMPAIGN_TABLE
*/

class TagAudienceTable extends CampaignBase {
    constructor(table_container, searchbar_element, pagination_container, campaign_id) {
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

        this.init(campaign_id);
    }

    init(campaign_id) {
        var _this = this;
        _this.initialize_table_header_metadata();
        _this.initialize_lead_data_metadata_update_modal();
        _this.fetch_active_campaigns(campaign_id);
    }

    initialize_table_header_metadata() {
        var _this = this;
        _this.active_user_metadata.lead_data_cols = _this.get_table_meta_data();
    }

    initialize_table() {
        var _this = this;

        _this.table_container.innerHTML = '<table class="table table-bordered" id="campaign_batch_table" width="100%" cellspacing="0"></table>';
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

        // document.getElementById("assign-campaign-btn").style.display = "none";
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
                $('[data-toggle="tooltip"]').tooltip({
                    container: 'body',
                    boundary: 'window'
                });

                if($(this).find('.dataTables_empty').length == 1) {
                    $(this).parents('#tag_audience_table_pagination_wrapper_div').hide();
                    $('#table_no_data_found').css("display","flex");
                }
                else{
                    $('#table_no_data_found').hide();
                    $(this).parents('#tag_audience_table_pagination_wrapper_div').show();
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
                if (! _this.campaign_data[dataIndex].sample_data.length){
                    $(row).children().css('opacity','0.45');
                    $(row).children().find('#action_dropdown_menu_btn').css('pointer-events','none');
                    $(row).children().find('#action_btn_tooltip_div').addClass('cursor-not-allowed');
                    $(row).children().find('#action_btn_tooltip_div').attr({
                        'data-toggle':'tooltip',
                        'title':'This option cannot be selected for the batch file if it is created via API'
                    });
                    $(row).children().find('#past_campaign_modal_click').parent().addClass('no-select-batch-click-border').css('opacity','revert');
                }
            },
        });
        
        if($('#campaign_batch_table tbody tr').length == 1){
            $('#campaign_batch_table tbody tr td').css('height','60px');
        }
        else{
            $('#campaign_batch_table tbody tr td').css('height','auto');
        }
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
        _this.fetch_active_campaigns();
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

    update_select_campaign_drop_down(campaign_objs){
        let html = '<select id="select-campaign" class="form-control" >'

        if (SELECTED_CAMPAIGN_ID){
            html  += '<option value="0">Choose Campaign</option>'
        } else{
            html  += '<option value="0" selected="selected">Choose Campaign</option>'
        }
        
        for (let campaign_obj=0;  campaign_obj<campaign_objs.length; campaign_obj++){
            let campaign_var = campaign_objs[campaign_obj];
            if (campaign_var[0] == SELECTED_CAMPAIGN_ID){
                html += '<option value="' + campaign_var[0] + '" selected="selected">'+campaign_var[1] +'</option>';
            }else{
                html += '<option value="' + campaign_var[0] + '">'+campaign_var[1] +'</option>';
            }
        }
        html += '</select>'
        $('#select-campaign-div').html(html);
        $(document).ready(function() {
            var select_el = document.getElementById("select-campaign");
            window.custom_select_dropdown = new EasyassistCustomSelect(select_el, null, null);
        })
    }

    fetch_active_campaigns(campaign_id) {
        var _this = this;
        active_batch_data_loader();
        var filters = get_url_multiple_vars();

        let selected_batch_id = $("input[type='radio'][name='campaign_batch']:checked").val();

        if (!selected_batch_id){
            selected_batch_id = parseInt(filters['selected_batch_id']);
        }

        var request_params = {
            'page': ((filters["page"] && filters["page"][0]) || 1),
            'bot_pk': filters['bot_pk'][0],
            'campaign_id': filters['campaign_id'][0],
            'campaign_channel': CAMPAIGN_CHANNEL,
            'searched_batch': SEARCHED_BATCH,
            'selected_batch_id': selected_batch_id,
            'selected_campaign_id': SELECTED_CAMPAIGN_ID,
        };

        if (campaign_id != "") {
            request_params['selected_campaign_id'] = campaign_id
        }

        var json_params = JSON.stringify(request_params);
        var encrypted_data = campaign_custom_encrypt(json_params);
        encrypted_data = {
            "Request": encrypted_data
        };
        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/campaign/get-campaign-batches/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                var response = JSON.parse(this.responseText);
                response = campaign_custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    _this.pagination_metadata = response.pagination_metadata;
                    _this.set_campaign_data(response.campaign_batches);
                    _this.update_select_campaign_drop_down(response.campaign_objs);
                    if (!selected_batch_id){
                        selected_batch_id = response.selected_batch_id;
                    }

                    update_tag_audience_page_url(selected_batch_id);
                    var radio_elem = document.getElementById('campaign-batch-radio-'+selected_batch_id);

                    if (radio_elem) {
                        radio_elem.checked = true;
                        $(radio_elem).parent().parent().css("background-color", "#F1F6FD");
                    }
                }
            } else if(this.readyState == 4 && this.status == 403){
                trigger_session_time_out_modal();
            }
            deactive_batch_data_loader();
        }
        xhttp.send(params);
    }

    set_campaign_data(campaign_data) {
        var _this = this;
        if (campaign_data) {
            _this.campaign_data = campaign_data;
            _this.data_checklist.campaign_data = true;
        }

        for (var data of campaign_data) {
            campaign_batches_global[data.batch_id] = data;
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
        var batch_id = campaign_data_obj.batch_id;

        var html = "";
        switch (name) {
            case "batch_name":
                data = data.replace(/.{35}/g, "$&" + "<br>");
                html = data
                break;

            case "created_on":
                html = `<div style="width:auto!important;"> ${data} </div>`;
                break;

            case "active_campaigns":
                if(data.length){
                    html = `<span id="past_campaign_modal_click" class="past-campaign-modal-click" data-toggle="modal" onclick="open_past_campaign_modal(${batch_id})">
                            Click Here
                        </span>`
                }else{
                  html = `<span class="no-past-campaign">
                                Not Available
                            </span>`
                }
                break;

            case "total_contacts":
                html = data;
                break;

            case "opted_in":
                html = data;
                break;

            case "rcs_enabled":
                html = data;
                break;

            case "action":
                html = `
                <div class="action-flex-div">
                    <div class="action-dropdown-div-wrapper" id="action_btn_tooltip_div">
                        <div class="action-btn-data-wrapper btn-group" data-toggle="dropdown" id="action_dropdown_menu_btn">
                            <a class="btn btn-lg dots-btn action-btn">
                                <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <g filter="url(#filter0_d_77_8519)"><rect x="2" y="2" width="24" height="24" rx="4" fill="#FAFAFA" shape-rendering="crispEdges"/><circle cx="14" cy="14" r="1.33333" fill="#2D2D2D"/><circle cx="9.33333" cy="14" r="1.33333" fill="#2D2D2D"/><circle cx="18.6666" cy="14" r="1.33333" fill="#2D2D2D"/></g><defs><filter id="filter0_d_77_8519" x="0" y="0" width="28" height="28" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB"><feFlood flood-opacity="0" result="BackgroundImageFix"/><feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/><feOffset/><feGaussianBlur stdDeviation="1"/><feComposite in2="hardAlpha" operator="out"/><feColorMatrix type="matrix" values="0 0 0 0 0.0416667 0 0 0 0 0.0416667 0 0 0 0 0.0416667 0 0 0 0.15 0"/><feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_77_8519"/><feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_77_8519" result="shape"/></filter></defs>
                                </svg>
                            </a>
                        </div>
                        <div class="dropdown-menu overview-menu-list table-action-dropdown-menu-list dropdown-menu-right">
                            <ul class="list-group custom-popover"> 
                                <li class="list-group-item group-data" onclick="download_campaign_batch_file(${batch_id})">
                                    <span>Download</span>
                                    <span class="group-data-logo download"> </span>
                                </li>
                                <li class="list-group-item group-data" onclick="set_edit_campaign_batch_modal(${batch_id})">
                                    <span>View</span>
                                    <span class="group-data-logo view"> </span>
                                </li>
                                <li class="list-group-item group-data" onclick="open_delete_batch_modal(${batch_id})">
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

        var select_row_html
        if (campaign_data_obj.sample_data.length){
            select_row_html = '<input class="campaign_select_row_cb" type="radio" name="campaign_batch"  value="' + campaign_data_obj.batch_id + '" id="campaign-batch-radio-'+campaign_data_obj.batch_id+'" />';
        }else{
            select_row_html = '<div  class="audience-disabled-input-div" id="nobatchdata" data-toggle="tooltip" data-original-title="This batch file cannot be selected if created via API."></div>'
        }
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

    select_row_checkbox_change_listener(event) {
        var _this = this;
        // var select_all_rows_cb = _this.table.querySelector(".campaign_select_all_rows_cb");
        // var select_row_cbs = _this.table.querySelectorAll(".campaign_select_row_cb");

        // var total_rows_checked = 0;
        // select_row_cbs.forEach((select_row_cb) => {
        //     if (select_row_cb.checked) {
        //         total_rows_checked += 1;
        //     }
        // });

        // if (total_rows_checked == select_row_cbs.length) {
        //     select_all_rows_cb.checked = true;
        // } else {
        //     select_all_rows_cb.checked = false;
        // }

        // if(total_rows_checked > 0) {
        //     document.getElementById("delete_campaign_btn").disabled = false;
        // } else {
        //     document.getElementById("delete_campaign_btn").disabled = true;
        // }
    }

    add_event_listeners_in_rows(container = null) {
        var _this = this;
        if (container == null) container = _this.table;
    }

    add_event_listeners() {
        var _this = this;

        // Select all row checkbox event listener
        var select_all_rows_cb = _this.table.querySelector(".campaign_select_all_rows_cb");
        if (select_all_rows_cb) {
            select_all_rows_cb.addEventListener("change", function () {
                var select_row_cbs = _this.table.querySelectorAll(".campaign_select_row_cb");
                var all_rows_selected = this.checked;

                select_row_cbs.forEach((select_row_cb) => {
                    if (all_rows_selected) {
                        select_row_cb.checked = true;
                    } else {
                        select_row_cb.checked = false;
                    }
                })

                if(all_rows_selected) {
                    document.getElementById("delete_campaign_btn").disabled = false;
                } else {
                    document.getElementById("delete_campaign_btn").disabled = true;
                }
            });
        }
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
        window.localStorage.setItem("tag_audience_table_meta_data_" + CAMPAIGN_CHANNEL.replace(" ", "_"), JSON.stringify(lead_data_cols));
    }

    get_table_meta_data() {
        var _this = this;
        var lead_data_cols = window.localStorage.getItem("tag_audience_table_meta_data_" + CAMPAIGN_CHANNEL.replace(" ", "_"));

        if (lead_data_cols == null) {
            lead_data_cols = _this.get_default_meta_data();
        } else {
            lead_data_cols = JSON.parse(lead_data_cols);
        }
        return lead_data_cols;
    }

    get_default_meta_data() {
        if(CAMPAIGN_CHANNEL == 'RCS') {
            var lead_data_cols = [
                ['batch_name', 'Batch Name', true],
                ['created_on', 'Created On', true],
                ['active_campaigns', 'Campaigns Assigned', true],
                ['total_contacts', 'Total Contacts', true],
                ['rcs_enabled', 'RCS Enabled', true],
                ['action', 'Action', true]
            ]
        } else {
            var lead_data_cols = [
                ['batch_name', 'Batch Name', true],
                ['created_on', 'Created On', true],
                ['active_campaigns', 'Campaigns Assigned', true],
                ['total_contacts', 'Total Contacts', true],
                // ['opted_in', 'Opted In', true],
                ['action', 'Action', true]
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

function initialize_tag_audience_table() {
    var campaign_table_container = document.querySelector("#tag_audience_table");
    var campaign_searchbar = document.querySelector("#tag-audience-search-bar");
    var pagination_container = document.getElementById("tag_audience_table_pagination_div");
    let campaign_id = SELECTED_CAMPAIGN_ID;

    window.ACTIVE_CAMPAIGN_TABLE = new TagAudienceTable(
        campaign_table_container, campaign_searchbar, pagination_container, campaign_id);
}

function save_lead_data_table_metadata() {

    var lead_data_cols = window.ACTIVE_CAMPAIGN_TABLE.active_user_metadata.lead_data_cols;

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

    window.ACTIVE_CAMPAIGN_TABLE.update_table_meta_deta(lead_data_cols)
}

function initialize_custom_tag_input(selected_values, unselected_values, container) {
    window.LEAD_DATA_METADATA_INPUT = new CognoAICustomTagInput(container, selected_values, unselected_values);
}


/* Upload Contacts Functionality */

var batch_file_global = undefined;

if (document.getElementById("campaign-batch-file-upload")) {
    document.getElementById("campaign-batch-file-upload").addEventListener('change', function(event) {
        var file = document.getElementById("campaign-batch-file-upload").files[0];
        ERROR_ROWS = []
        if(file) {
            batch_file_global = ($("#campaign-batch-file-upload"))[0].files[0];
            
            let filename = file.name;
            let is_file_valid = true;
            let files_validation_error = '';
            let fileExtension = filename.substring(filename.lastIndexOf(".") + 1, filename.length).toLowerCase();;

            if (check_file_extension(filename) == false) {
                is_file_valid = false;
                files_validation_error = "file_extension";
            } else if(check_malicious_file(filename).status) {
                is_file_valid = false;
                files_validation_error = "malicious_file";
                // file.size/1000000 > 150
            } else if(fileExtension == 'psv' && file.size/1000000 > 300) {
                is_file_valid = false;
                files_validation_error = "file_size";
                // file.size/1000000 > 5
            } else if(fileExtension != 'csv' && file.size/1000000 > 300) {
                is_file_valid = false;
                files_validation_error = "file_size";
                // file.size/1000000 > 150
            } else if(fileExtension == 'csv' && file.size/1000000 > 300) {
                is_file_valid = false;
                files_validation_error = "file_size";
            }
    
            if(is_file_valid == false) {
                remove_error_elements();
                document.getElementById('campaign_batch_input_error').style.display = 'flex';
                let upload_error = document.getElementById('error-note-text');
                if(files_validation_error == "file_size") {
                    // upload_error.innerHTML = "The file size exceeds the maximum limit of 5 MB for Excel and 15 MB for CSV and PSV and the maximum contacts should not be more than 100K users in a single file.";
                    upload_error.innerHTML = "The file size exceeds the maximum limit of 300 MB for Excel and 300 MB for CSV and PSV and the maximum contacts should not be more than 100K users in a single file.";
                } else if(files_validation_error == "malicious_file") {
                    upload_error.innerHTML = "We do not allow . (dot) in the file name except for the extension. Please remove the dot and Re-upload the file.";
                } else {
                    upload_error.innerHTML = "The file could not be uploaded. Only files with the following extensions are allowed: XLS, XLSX, and CSV.";
                }
                $('#upload-campaign-batch-modal .No-File-Selected-Yet').hide();
                $('#upload-campaign-batch-modal .file-name-div').html(filename);
                $('#upload-campaign-batch-modal .modal-upload-file').show();
                return;
            }
    
            if(filename.length > 50) filename = filename.substr(0, 50) + "...";
            $('#upload-campaign-batch-modal .No-File-Selected-Yet').hide();
            $('#upload-campaign-batch-modal .file-name-div').html(filename);
            $('#upload-campaign-batch-modal .modal-upload-file').show();
            $('#upload-batch-element').prop("disabled",false);
            remove_error_elements()
            
        } else {
            if(batch_file_global == undefined){
                $('#upload-campaign-batch-modal .No-File-Selected-Yet').show();
            }
        }
    });    
}

function remove_uploaded_file() {
    $('#upload-campaign-batch-modal .file-name-div').html("");
    $('#upload-campaign-batch-modal .modal-upload-file').hide();
    document.getElementById("campaign-batch-file-upload").value = "";
    $('#upload-batch-element').prop("disabled",true);
    batch_file_global = undefined;
    $('#upload-campaign-batch-modal .No-File-Selected-Yet').show();
    ERROR_ROWS = []
    remove_error_elements()
}

function remove_error_elements() {
    let wrapper_element = document.getElementById('file-wrapper-div-error-id');
    wrapper_element.classList.remove("file-wrapper-div-error");
    document.getElementById('sub-heding-section-text').innerHTML = 'File Added'
    document.getElementById('download-error-file-btn-id').style.display = "none";
    document.getElementById('campaign-auto-delete-number-div').style.display = "none";
    $('#auto-delete-number-checkbox').prop('checked', false);
    document.getElementById('uploaded_batch_file_errors').scrollTop = 0;
    document.getElementById('uploaded_batch_file_errors').innerHTML = '<p>Uploaded File contains following error(s):</p>';
    document.getElementById('campaign_batch_input_error').style.display = 'none';
    document.getElementById('uploaded_batch_file_errors').style.display = 'none';
}

function download_batch_template() {
    var json_string = {
        'campaign_channel': CAMPAIGN_CHANNEL,
    };

    json_string = JSON.stringify(json_string);

    var encrypted_data = campaign_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/campaign/download-batch-template/", true);
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

$("#campaign-delete-modal-save-btn").click(function(){
    AUTO_DELETE_CONFIRM = true;
    upload_batch_file('');
  });

$("#campaign-delete-modal-cancel-btn").click(function(){
    AUTO_DELETE_CONFIRM = false;
    $('#upload-campaign-batch-modal').modal('show');
});

var batch_header_meta_global = [];
var sample_data_global = [];
var total_audience_global = 0;
var total_opted_in_global = 0;
var is_edit_modal_open = false;

function upload_batch_file(el) {
    let file = batch_file_global;

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

    let auto_delete_checked = document.getElementById('auto-delete-number-checkbox').checked
    $('#upload-campaign-batch-modal').modal('hide');
    if (auto_delete_checked) {
        if (AUTO_DELETE_CONFIRM) {
            UPLOADING_PROCESS_RUNNING = 2
            $('#invalid-numbers-delete-modal').modal('hide');
            $('#uploading-updated-batch-modal').modal('show');
            reset_progress_bar()
        } else {
            $('#invalid-numbers-delete-modal').modal('show');
            return
        }
    } else {
        UPLOADING_PROCESS_RUNNING = 1
        $('#upload-campaign-batch-loader-modal').modal('show');
        reset_progress_bar()
    }
    show_campaign_toast('Please wait while we are uploading the contacts from your batch file');
    var formData = new FormData();
    formData.append("file", file);
    var json_string = {
        "filename": file.name,
        "campaign_channel": CAMPAIGN_CHANNEL,
        "auto_delete_checked": auto_delete_checked,
        "error_rows": ERROR_ROWS,
        "bot_id": BOT_ID
    };

    json_string = JSON.stringify(json_string);

    var encrypted_data = campaign_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    formData.append("params", params);

    xhttp.open("POST", '/campaign/upload-batch/', true);
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if ([400, 401].includes(response["status"])) {
                setTimeout(function() { show_campaign_toast(response["message"], 10000) }, 1500);
                hide_upload_batch_loader()
                return;
            }
            else if (response["status"] == 200) {
                event_progress_id = response["event_progress_id"]
                extraction_timer = setInterval(track_upload_batch_progress, 1000, event_progress_id);
                $('#upload-batch-modal-title').text('Uploading Batch')
                $('#upload-batch-element').prop("disabled",true);
                $('#upload-batch-element').text('Uploading...')
            } else {
                show_campaign_toast('There seems to be an internal server error or connection timeout, please try uploading your file again.');
                hide_upload_batch_loader()
            }
        } else if(this.readyState == 4 && this.status == 403){
            trigger_session_time_out_modal();
        }
    }
    xhttp.send(formData);
};
   

function track_upload_batch_progress(event_progress_id) {

    var json_string = JSON.stringify({
        event_progress_id: event_progress_id
    })

    json_string = campaign_custom_encrypt(json_string)
    $.ajax({
        url: "/campaign/track-event-progress/",
        type: "POST",
        headers: {
            'X-CSRFToken': get_csrfmiddlewaretoken()
        },
        data: {
            data: json_string,
        },
        success: function(response) {
            response = campaign_custom_decrypt(response)
            response = JSON.parse(response);

            if (response.status == 200) {
                let is_completed = response.is_completed;
                let is_toast_displayed = response.is_toast_displayed;
                let is_failed = response.is_failed;
                let event_info = response.event_info;
                let failed_message = response.failed_message;
                let event_progress = response.event_progress
                
                $('.layout .Rectangle .chart .bar').css('width', event_progress + '%')
                $('.layout .Rectangle .num').text(event_progress + '%')
                $('.layout .Rectangle .num').css('margin-left', parseInt(event_progress) - 8 + '%', 'important')
                
                response = event_info
                if (is_completed) {
                    AUTO_DELETE_CONFIRM = false
                    if(response["status"] == 200) {
                        $('#upload-campaign-batch-modal').modal('hide');
                        document.getElementById('campaign_batch_input_error').style.display = 'none';

                        total_opted_in_global = response.total_opted_in

                        if(is_edit_modal_open) {
                            set_batch_preview_edit_modal(response.header_metadata, response.sample_data, response.original_file_name, response.total_batch_count, response.file_path);
                        } else {
                            if (document.getElementById('auto-delete-number-checkbox').checked) {
                                $('#row-deleted-count-div').show();
                                document.getElementById('deleted-row-count').innerHTML = response['deleted_rows']
                            } else {
                                $('#row-deleted-count-div').hide();
                            }
                            
                            set_batch_preview_modal(response.header_metadata, response.sample_data, response.original_file_name, response.total_batch_count, response.file_path);
                        }
                
                    } else if (response.status == 400) {
                        let row_errors = response['row_errors'];
                        ERROR_ROWS = response["error_rows"]
                        document.getElementById('download-error-file-btn-id').style.display = "flex";
                        document.getElementById('campaign-auto-delete-number-div').style.display = "flex";
                        document.getElementById('campaign_batch_input_error').style.display = 'none';
                        $('#upload-batch-element').prop("disabled",true);
                        ERROR_FILE_PATH = response["file_path"]
                        ERROR_FILE_NAME = response["original_file_name"]

                        let wrapper_element = document.getElementById('file-wrapper-div-error-id');
                        wrapper_element.classList.add("file-wrapper-div-error");
                        
                        document.getElementById('sub-heding-section-text').innerHTML = 'Error(s) in the uploaded file!'
                        document.getElementById('uploaded_batch_file_errors').innerHTML = '<p>Uploaded File contains following error(s):</p>';
                        let error_no = 1;
                        for (error of row_errors) {
                            $('#uploaded_batch_file_errors').append(`<p class="upload-batch-error-text"'>${error_no}. ${error}</p>`);
                            ++error_no;
                        }
                        document.getElementById('uploaded_batch_file_errors').style.display = 'block';
                        $('#upload-campaign-batch-modal').modal('show');
                    } else if (response.status == 401 || response.status == 402) {
                        $('#upload-campaign-batch-modal').modal('show');
                        document.getElementById('uploaded_batch_file_errors').style.display = 'none';
                        document.getElementById('campaign_batch_input_error').style.display = 'flex';
                        document.getElementById('error-note-text').innerHTML = response.status_message;
                        $('#upload-batch-element').prop("disabled",true);
                    } else if (response.status == 403) {
                        $('#no-data-found-modal').modal('show');
                        document.getElementById('no-data-found-file').innerHTML = batch_file_global.name
                    } else {
                        document.getElementById('campaign_batch_input_error').style.display = 'flex';
                        document.getElementById('uploaded_batch_file_errors').style.display = 'none';
                        document.getElementById('error-note-text').innerHTML = 'Unable to upload the file. Please try again later!';
                        $('#upload-batch-element').prop("disabled",true);
                    }
                    if (extraction_timer) {
                        clearInterval(extraction_timer)
                    }
                    hide_upload_batch_loader();
                }
            } else {
                if (extraction_timer) {
                    clearInterval(extraction_timer)
                }
                hide_upload_batch_loader();
            }
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
            hide_upload_batch_loader();
        }
    });
}

function set_batch_preview_modal(header, sample_data, file_name, total_batch_count, file_path) {
    batch_header_meta_global = header;
    total_audience_global = total_batch_count;
    sample_data_global = sample_data
    document.getElementById('new-batch-file-name').innerHTML = file_name;
    document.getElementById('new-batch-name').value = file_name.split('.')[0];
    document.getElementById('new-batch-total-count').innerHTML = total_batch_count;
    document.getElementById('new_batch_file_path').value = file_path;

    let table = get_batch_preview_table_html(header, sample_data);
    document.getElementById('new_batch_table_div').innerHTML = table;
    $('#new-batch-uploaded-modal').modal('show');
    add_tooltip_preview_modal();
    $('#new-batch-uploaded-modal').on('shown.bs.modal', function (e){
        $('#new_batch_table_div').scrollLeft(0);
        $('.custom_modal .modal-body').scrollTop(0);
        });
}

function add_tooltip_preview_modal() {
    $('#audience-file-preview-table').DataTable({
        "ordering": false,
        "bPaginate": false,
        "bInfo": false,
        "bLengthChange": false,
        "searching": false,
    
        "drawCallback": function (settings) {
            $('[data-toggle="tooltip"]').tooltip({
                container: 'body',
                boundary: 'window'
                    });
    
                }
            });
}

function get_batch_preview_table_html(header, sample_data) {
    var html = `<table class='table dataTable no-footer' id='audience-file-preview-table' role='grid'><thead>`

    html += get_header_html(header);

    html += `</thead><tbody>`

    html += get_body_html(sample_data);

    html += `</tbody></table>`

    return html;
}

function get_header_html(header) {
    var html = `<tr role='row'>`
    let head_count = 1
    for (var obj of header) {
        let col_name = obj.col_name.replace('*', '').trim()
        let greater_than_limit = false;
        if (col_name.length >= 21){
            greater_than_limit = true;
        }
        if(head_count==1 && col_name.length < 33){
            greater_than_limit = false;
        }
        if (head_count == 1 ) {
            if (greater_than_limit){
                html += `<th scope="col" style="background-color: white !important;width: 288px;" class="sorting_disabled" rowspan="1" colspan="1"><p class="header-tooltip-wrapper" data-toggle="tooltip" title="${obj.col_name.replace('*', '')}">${col_name}</p></th>`;
            } else{
                html += `<th scope="col" style="background-color: white !important;width: 288px;" class="sorting_disabled" rowspan="1" colspan="1"><p class="header-tooltip-wrapper">${col_name}</p></th>`;
            }
            
        } else if (head_count == 2 || head_count == 3 || head_count == 6) {
            if (greater_than_limit){
                html += `<th scope="col" style="background-color: white !important;width: 185px;" class="sorting_disabled" rowspan="1" colspan="1"><p class="header-tooltip-wrapper" data-toggle="tooltip" title="${obj.col_name.replace('*', '')}">${col_name}</p></th>`;
            } else{
                html += `<th scope="col" style="background-color: white !important;width: 185px;" class="sorting_disabled" rowspan="1" colspan="1"><p class="header-tooltip-wrapper">${col_name}</p></th>`;
            }
        } else {
            if (greater_than_limit){
                html += `<th scope="col" style="background-color: white !important;width: 185px;" class="sorting_disabled" rowspan="1" colspan="1"><p class="table-tooltipped-wrapper" data-toggle="tooltip" title="${obj.col_name.replace('*', '')}">${col_name}</p></th>`;
            } else{
                html += `<th scope="col" style="background-color: white !important;width: 185px;" class="sorting_disabled" rowspan="1" colspan="1"><p class="table-tooltipped-wrapper">${col_name}</p></th>`;
            }
        }
        head_count += 1;
    }

    html += `</tr>`;

    return html;
}

function get_body_html(sample_data) {
    let html = ''
    for (let row of sample_data) {
        html += `<tr>`;
        let col_index = 1;
        for (var data of row) {
            let greater_than_limit = false;
            if (data.length >= 21){
                greater_than_limit = true;
            }
            if (greater_than_limit){
                html += `<td><span class="table-tooltipped-wrapper" data-toggle="tooltip" title="${data}">${data}</span></td>`;
            } else {
                html += `<td><span class="table-tooltipped-wrapper">${data}</span></td>`;
            }
            col_index += 1;
        }

        html += `</tr>`
    }

    return html;
}

function save_campaign_batch(el) {
    var id = el.dataset.id

    if (id) {
        var batch_name = document.getElementById('edit-batch-name').value.trim();
        var file_path = document.getElementById('edit_batch_file_path').value;
        var file_name = document.getElementById('edit-batch-file-name').innerHTML;
    } else {
        var batch_name = document.getElementById('new-batch-name').value.trim();
        var file_path = document.getElementById('new_batch_file_path').value;
        var file_name = document.getElementById('new-batch-file-name').innerHTML;
    }

    if (batch_name == '') {
        show_campaign_toast('The batch file name cannot be empty.');
        return;
    }

    batch_name = stripHTML(batch_name);

    if (test_special_characters_in_batch_name(batch_name)) {
        show_campaign_toast('We only support special characters like _, -, @, (, ), [, ] with at least 1 alphabet or number present in the file name.');
        return;
    }
    batch_name = remove_special_characters_from_batch_name(batch_name);
    var json_string = {
        'batch_name': batch_name,
        'batch_header_meta': batch_header_meta_global,
        'sample_data': sample_data_global,
        'total_audience': total_audience_global,
        'total_opted_in': total_opted_in_global,
        'file_path': file_path,
        'file_name': file_name,
        'bot_pk': get_url_multiple_vars()['bot_pk'][0],
        'campaign_channel': CAMPAIGN_CHANNEL,
    };
    if (id) {
        json_string['batch_id'] = id;
    }

    json_string = JSON.stringify(json_string);

    var encrypted_data = campaign_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", '/campaign/save-batch/', true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if(response["status"] == 200) {
                show_campaign_toast('The batch file is uploaded successfully.');
                initialize_tag_audience_table();

                if (id) {
                    $('#edit_campaign_batch_modal').modal('hide');
                } else {
                    $('#new-batch-uploaded-modal').modal('hide');
                }
                remove_uploaded_file();
            } else {
                show_campaign_toast(response.message)
            }
            
        } else if(this.readyState == 4 && this.status == 403){
            trigger_session_time_out_modal();
        }
    }
    xhttp.send(params);
}

function delete_batch_file () {
    if (is_edit_modal_open) {
        $('#edit_campaign_batch_modal').modal('hide');
        $('#upload-campaign-batch-modal').modal('show');
        return;
    }

    var file_path = document.getElementById('new_batch_file_path').value;

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
    xhttp.open("POST", '/campaign/delete-batch-file/', true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if(response["status"] == 200) {
                show_campaign_toast('The batch file is deleted successfully.');
                $('#new-batch-uploaded-modal').modal('hide');
                $('#upload-campaign-batch-modal').modal('show');
                remove_uploaded_file()
            } else {
                show_campaign_toast(response.message)
            }
        } else if(this.readyState == 4 && this.status == 403){
            trigger_session_time_out_modal();
        }
    }
    xhttp.send(params);   
}

function open_upload_campaign_batch_modal() {
    if (UPLOADING_PROCESS_RUNNING == null) {
        $('#upload-campaign-batch-modal').modal('show');
        is_edit_modal_open = false;
        $('#auto-delete-number-checkbox').prop('checked', false);
        let file_uploader = document.getElementById("file_upload_bar");
        let upload_error = document.getElementById("uploaded_batch_file_errors")
        let column_header_error = document.getElementById("campaign_batch_input_error")
        
        if (window.getComputedStyle(file_uploader).display === "none" || window.getComputedStyle(upload_error).display !== "none" || window.getComputedStyle(column_header_error).display !== "none") {
            $('#upload-batch-element').prop("disabled", true);
        } else {
            $('#upload-batch-element').prop("disabled", false);
        }
    } else if (UPLOADING_PROCESS_RUNNING == 1) {
        $('#upload-campaign-batch-loader-modal').modal('show');
    } else {
        $('#uploading-updated-batch-modal').modal('show');
    }
    
}
/* Upload Contacts Functionality Ends */

function go_to_upload_campaign_batch_modal(param) {
    is_edit_modal_open = false;
    if(param == 'EmptyFile') {
        remove_uploaded_file()
    }
    $('#new-batch-uploaded-modal').modal('hide');
    $('#no-data-found-modal').modal('hide');
    $('#upload-campaign-batch-modal').modal('show');
    $('#upload-batch-element').prop("disabled",false);
}

// Downlaod error file
$("#download-batch-error-file").click(function(){
    window.open(window.location.origin + ERROR_FILE_PATH + ERROR_FILE_NAME);
});

// Download campaign batch 
function download_campaign_batch_file(id) {

    var json_string = {
        'batch_id': id,
        'bot_pk': get_url_multiple_vars()['bot_pk'][0],
    };

    json_string = JSON.stringify(json_string);

    var encrypted_data = campaign_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", '/campaign/download-batch-file/', true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if(response["status"] == 200) {
                if(response["download_file_path"].trim()){
                    window.location.href = window.location.origin + response["download_file_path"] + 'file'
                    show_campaign_toast("Batch file downloaded successfully");
                }else{
                    show_campaign_toast("This batch file is not available for download")
                }
            } else {
                show_campaign_toast("Unable to download batch file")
            }

        } else if(this.readyState == 4 && this.status == 403){
            trigger_session_time_out_modal();
        }
    }
    xhttp.send(params);      
} 

/* Edit Batch Functionality Starts */

function set_edit_campaign_batch_modal(id) {
    is_edit_modal_open = true;
    $('#edit_campaign_batch_modal').modal('show');

    var {batch_header_meta, batch_name, total_contacts, sample_data, file_path, file_name} = campaign_batches_global[id];

    batch_header_meta_global = batch_header_meta;
    total_audience_global = total_contacts;
    sample_data_global = sample_data

    document.getElementById('edit-batch-file-name').innerHTML = file_name;
    document.getElementById('edit-batch-name').value = batch_name;
    document.getElementById('edit-batch-total-count').innerHTML = total_contacts;
    document.getElementById('edit_batch_file_path').value = file_path;

    var table = get_batch_preview_table_html(batch_header_meta, sample_data);

    document.getElementById('edit_batch_table_div').innerHTML = table;

    document.getElementById('edit_batch_btn').dataset.id = id;

    document.getElementById('edit_batch_modal_loader').style.display = 'none';
    document.getElementById('edit_batch_modal').style.display = 'block';
    $('[data-toggle="tooltip"]').tooltip({
        container: 'body',
        boundary: 'window'
        });
    $('#edit_campaign_batch_modal').on('shown.bs.modal', function (e){
        $('#edit_batch_table_div').scrollLeft(0);
        $('.custom_modal .modal-body').scrollTop(0);
    });
}
function set_batch_preview_edit_modal(header, sample_data, file_name, total_batch_count, file_path) {
    batch_header_meta_global = header;
    total_audience_global = total_batch_count;
    sample_data_global = sample_data

    document.getElementById('edit-batch-file-name').innerHTML = file_name;
    document.getElementById('edit-batch-total-count').innerHTML = total_batch_count;
    document.getElementById('edit_batch_file_path').value = file_path;


    var table = get_batch_preview_table_html(header, sample_data);

    document.getElementById('edit_batch_table_div').innerHTML = table;

    $('#edit_campaign_batch_modal').modal('show');
}

function open_delete_batch_modal(batch_id) {
    document.getElementById('delete_batch_btn').dataset.id = batch_id;

    $('#delete_campaign_batch_modal').modal('show');
}

function delete_batch(el) {
    var error_element = document.getElementById("delete-batch-error-msg");
    var batch_id = el.dataset.id;

    var json_string = {
        'batch_id': batch_id,
        'bot_pk': get_url_multiple_vars()['bot_pk'][0],
    };

    json_string = JSON.stringify(json_string);

    var encrypted_data = campaign_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);

    el.innerText = "Deleting...";

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", '/campaign/delete-batch/', true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if(response["status"] == 200) {
                error_element.innerText = "Template deleted successfully.";
                error_element.style.color = "green";
                initialize_tag_audience_table();
                $('#delete_campaign_batch_modal').modal('hide');
                error_element.innerText = "";

            } else {
                error_element.innerText = response.message;
                error_element.style.color = "red";
            }

            el.innerText = "Delete";
        } else if(this.readyState == 4 && this.status == 403){
            trigger_session_time_out_modal();
        }
    }
    xhttp.send(params);      
}

function reset_delete_modal() {
    document.getElementById('delete_batch_btn').innerHTML = 'Delete';
    document.getElementById("delete-batch-error-msg").innerHTML = '';
}

function add_batch_to_campaign(element, is_next_clicked=false) {
    var error_message_element = document.getElementById("save-campaign-error-message");
    error_message_element.innerText = "";

    var selected_batch_id = $("input[type='radio'][name='campaign_batch']:checked").val();

    if (!selected_batch_id) {
        var error_message = 'Please select a batch.';
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
        'selected_batch_id': selected_batch_id
    };

    var json_params = JSON.stringify(request_params);
    var encrypted_data = campaign_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/campaign/add-batch-to-campaign/", true);
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
                        var template_url;
                        if (CAMPAIGN_CHANNEL == 'Voice Bot') {
                            template_url = window.location.origin + '/campaign/voice-bot/settings/?bot_pk=' + BOT_ID + '&campaign_id=' + campaign_id;
                        } else {
                            template_url = window.location.origin + '/campaign/create-template/?bot_pk=' + BOT_ID + '&campaign_id=' + campaign_id;
                        }

                        window.location.href = template_url;
                    }, 1000);
                }
                else{
                    window.location.href = window.location.origin + '/campaign/dashboard/?bot_pk=' + BOT_ID;
                }
                var error_message = "Campaign has been saved successfully";
                show_campaign_toast(error_message);
            } else {
                var error_message = "Not able to save campaign. Please try again";
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
/* Edit Batch Functionality Ends */

function apply_campaign_filter() {
    var selected_campaign_id = document.getElementById('select-campaign').value;

    if (selected_campaign_id == '0') {
        SELECTED_CAMPAIGN_ID = "";
        initialize_tag_audience_table();
    } else {
        SELECTED_CAMPAIGN_ID = selected_campaign_id
        initialize_tag_audience_table();
    }
}

function apply_batch_search() {
    let searched_batch = document.getElementById("tag-audience-search-bar").value.trim();
    document.getElementById("tag-audience-search-bar").value = searched_batch;
    searched_batch = stripHTML(searched_batch);
    searched_batch = remove_special_characters_from_str(searched_batch);

    // Changed audience batch pagination on search input change.
    let filters = get_url_multiple_vars();
    filters.page = ['1'];
    window.ACTIVE_CAMPAIGN_TABLE.update_url_with_filters(filters);

    if (searched_batch != "") {
        SEARCHED_BATCH = searched_batch
    } else {
        SEARCHED_BATCH = "";
    }
    initialize_tag_audience_table()
}

const search_campaign_batch = debounce(function() {
    apply_batch_search()
})

document.getElementById("tag-audience-search-bar")?.addEventListener("search", function(event) {
    apply_batch_search()
});

function active_batch_data_loader(){
    $('#no-data-loader').show();
    $('#campaign_batch_table_wrapper').hide();
    $('#tag_audience_table_pagination_div').hide();
    $('#table_no_data_found').hide();
    $('#upload-batch-button').prop('disabled', true);
    $('#save-batch-next-btn').prop('disabled', true);
    $('.custom_filter_btn').prop('disabled', true);
    $('.custom_metadata_btn').prop('disabled', true);
}

function deactive_batch_data_loader(){
    $('#no-data-loader').hide();
    $('#campaign_batch_table_wrapper').show();
    $('#tag_audience_table_pagination_div').show();
    $('#upload-batch-button').prop('disabled', false);
    $('#save-batch-next-btn').prop('disabled', false);
    $('.custom_filter_btn').prop('disabled', false);
    $('.custom_metadata_btn').prop('disabled', false);
}

function clear_campaign_filter() {
    var elem = document.getElementById('select-campaign');
    SELECTED_CAMPAIGN_ID = "";
    elem.value = '0';
    var change_event = new Event('change');
    custom_select_dropdown.update_value("0")
    elem.dispatchEvent(change_event);
    
    initialize_tag_audience_table();
}

function toggle_radio_btn(el) {
    if (el.classList.contains('selected-batch')) {
        el.checked = false;
        el.classList.remove('selected-batch');
    } else {
        el.classList.add('selected-batch');

        var name = el.name;
        var all_elems = document.getElementsByName(name);
        for(elem of all_elems) {
            if (elem != el) elem.classList.remove('selected-batch');
        }
    }
}

function hide_upload_batch_loader() {
    UPLOADING_PROCESS_RUNNING = null;
    $('#uploading-updated-batch-modal').modal('hide');
    $('#upload-campaign-batch-loader-modal').modal('hide');
    $('#upload-campaign-batch-modal').modal('hide');
    $('#upload-batch-element').prop("disabled",true);
    $('#upload-batch-element').text('Upload')
}

function reset_progress_bar() {
    $('.layout .Rectangle .chart .bar').css('width', '0%');
    $('.layout .Rectangle .num').css('left', '1%', 'important');
    $('.layout .Rectangle .num').css('margin-left', '')
    $('.layout .Rectangle .num').text('0%');
}

function auto_delete_checked() {
    let auto_delete_checked = document.getElementById('auto-delete-number-checkbox').checked
    if (auto_delete_checked) {
        $('#upload-batch-element').prop("disabled",false);
    } else {
        $('#upload-batch-element').prop("disabled",true);
    }
}

$(document).on('change', '#campaign_batch_table td input', function() {
    if(this.checked) {
        let selected_batch_id = $("input[type='radio'][name='campaign_batch']:checked").val();
        update_tag_audience_page_url(selected_batch_id);
        $("#campaign_batch_table tbody tr").css("background-color", "#fff");
        $(this).parent().parent().css("background-color", "#F1F6FD");
    }
})

function update_tag_audience_page_url(selected_batch_id){
    let filters = get_url_multiple_vars();
    let filters_page = filters['page'];
    if (!filters_page){
        filters_page = 1;
    }
    let newurl = `${window.location.protocol}//${window.location.host}${window.location.pathname}?bot_pk=${filters['bot_pk']}&campaign_id=${filters['campaign_id']}&selected_batch_id=${selected_batch_id}&page=${filters_page}`
    if (SELECTED_CAMPAIGN_ID){
        newurl += `&selected_campaign=${SELECTED_CAMPAIGN_ID}`
    }
    if (SEARCHED_BATCH){
        $("#tag-audience-search-bar").val(SEARCHED_BATCH);
        newurl += `&search_batch=${SEARCHED_BATCH}`
    }
    window.history.pushState({ path: newurl }, '', newurl);
}

function open_past_campaign_modal(batch_id) {
    let campaign_batch = campaign_batches_global[batch_id]
    let batch_name = campaign_batch["batch_name"]
    let active_campaigns = campaign_batch["active_campaigns"]
    let active_campaign_html = ""
    for(let active_campaign=0; active_campaign<active_campaigns.length; active_campaign++){
        active_campaign_html += `<div class="past-campaign-list-item">
                                    ${active_campaigns[active_campaign]}
                                </div>`
    }
    let html = `<div class="past-campaign-batch-name">
                Batch Name: <span class="bold"><b style="word-break: break-all;">${batch_name}</b></span> 
            </div>
            <div class="past-campaign-list">
                ${active_campaign_html}
            </div>`
    $('#past_campaign_batch_name').html(html);
    $('#audience_past_campaign_modal').modal('show');
}
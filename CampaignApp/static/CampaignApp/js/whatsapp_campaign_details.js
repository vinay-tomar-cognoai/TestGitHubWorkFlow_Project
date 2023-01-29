// FILTER_DATE_TYPE = "4";
// START_DATE = DEFAULT_START_DATE;
// END_DATE = DEFAULT_END_DATE;
SEARCHED_VALUE = ""
SEARCHED_TYPE = ""
STATUS_FILTER = [];
QUICK_REPLY_FILTER = [];
TEMPLATE_FILTER = [];
TOTAL_ENTRY = 0
IS_TEMPLATE_SELECT = false;
DEFAULT_TEMPLATES = [];
DEFAULT_QUICK_REPLY = [];
CAMPAIGN_IDS = DEFAULT_CAMPAIGN;
SHOW_QR_DROP_DOWN = true;
IS_FIRST_RENDER = true;
ALL_CAMPAIGN_LIST = [];
TEST_MESSAGE_FILTER = [];

$(document).ready(function() {
    try {
        // document.getElementById("whatsapp_report_beg").checked = true;
        let status_checkboxes = document.querySelectorAll('[id="campaign-filter-status"]');
        for (let i=0; i<status_checkboxes.length; i++) {
            status_checkboxes[i].checked = true;
        }

        let test_message_status = document.querySelectorAll('[id="test-message-status"]');
        for (let i=0; i<test_message_status.length; i++) {
            test_message_status[i].checked = true;
        }
            
        $(".template-name-chips-div .chips .cross-icon").click(function(){
            $(this).parent().remove();
        })

        let modal_height = $("#campaign_meta_data_table .modal-body").height();
        if(modal_height > 300){
            $("#campaign_meta_data_table .modal-body").css("overflow-y","auto");
        }
        initialize_whatsapp_campaign_template_table();

        if (window.location.href.includes("/campaign/whatsapp-campaign-details/")) {
            setInterval(update_whatsapp_campaign_data, 180000, false);
        }

        $(".template-name-chips-div").hide();
        
    } catch (error) {
    
    }

});

function remove_selected_chips(el) {
    let intent_checkbox_id = el.id;
    $('input[value="'+ intent_checkbox_id +'"]').click().change()
}

function update_whatsapp_campaign_data(show_loader=true) {
    let search_input = document.getElementById("whatsapp-history-search-bar").value.trim();
    if (search_input != "") {
        return;
    }
    SEARCHED_VALUE = ""
    SEARCHED_TYPE = ""
    $(".tooltip").hide();

    window.WHATSAPP_CAMPAIGN_DETAILS_TABLE.get_whatsapp_campaign_data(show_loader);
}

class WhatsappDetailsTable extends CampaignBase {
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
            'campaign_data': false,
        };
        this.number_of_records = 10;
        this.data_table_obj = null;

        this.init();
    }

    init() {
        let _this = this;
        _this.initialize_table_header_metadata();
        _this.initialize_lead_data_metadata_update_modal();
        _this.get_whatsapp_campaign_data();
        
    }

    initialize_table_header_metadata() {
        let _this = this;
        _this.active_user_metadata.lead_data_cols = _this.get_table_meta_data();
    }

    initialize_table() {
        let _this = this;

        _this.table_container.innerHTML = '<table class="table table-bordered" id="whatsapp_campaign_details_table" width="100%" cellspacing="0"></table>';
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
        _this.update_table_attribute([_this.table]);
    }

    initialize_head() {
        let _this = this;
        const { enable_select_rows } = false;
        let th_html = "";
        _this.active_user_metadata.lead_data_cols.forEach((column_info_obj) => {
            if (column_info_obj.selected == false) return;
            let name = column_info_obj.name;
            let display_name = column_info_obj.display_name;
            th_html += '<th name="' + name + '" id="' + name + '">' + display_name + '</th>'
        });

        let select_rows_html = "";
        if (enable_select_rows) {
            select_rows_html = [
                '<th>',
                '</th>',
            ].join('');
        }

        let thead_html = [
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
        let _this = this;
        let campaign_data_list = this.get_rows();
        _this.data_table_obj = $(_this.table).DataTable({
            "data": campaign_data_list,
            "ordering": false,
            "bPaginate": false,
            "bInfo": false,
            "bLengthChange": false,
            "searching": true,
            "drawCallback": function (settings) {
                $('[data-toggle="tooltip"]').tooltip({
                    container: 'body',
                    boundary: 'window',
                    delay: { "show": 1000 }
                });

                if($(this).find('.dataTables_empty').length == 1) {
                    $(this).parent().hide();
                    $('#table_no_data_found').css("display","flex");
                }
                else{
                    $('#table_no_data_found').hide();
                }
            },

            initComplete: function() {
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
        });
    }

    apply_table_pagination() {
        let _this = this;
        if(_this.campaign_data.length == 0) {
            _this.pagination_container.innerHTML = "";
            return;
        }

        let container = _this.pagination_container;
        let metadata = _this.pagination_metadata;
        let onclick_handler = _this.add_filter_and_fetch_data;
        _this.apply_pagination(container, metadata, onclick_handler, _this);
    }

    update_url_with_filters(filters) {
        let key_value = "";
        for (let filter_key in filters) {
            let filter_data = filters[filter_key];
            for (let index = 0; index < filter_data.length; index++) {
                key_value += filter_key + "=" + filter_data[index] + "&";
            }
        }

        let newurl = window.location.protocol + "//" + window.location.host + window.location.pathname + '?' + key_value;
        newurl = newurl.slice(0,-1);
        window.history.pushState({ path: newurl }, '', newurl);
    }

    add_filter_and_fetch_data(key, value, target_obj = null) {
        let _this = this;
        if (target_obj) {
            _this = target_obj;
        }

        let filters = get_url_multiple_vars();
        if (key == "page") {
            filters.page = [value];
        }

        _this.update_url_with_filters(filters);
        _this.get_whatsapp_campaign_data(true, true);
    }

    lead_data_table_meta_div() {
        let _this = this;
        if(_this.campaign_data.length == 0) {
            _this.pagination_container.innerHTML = "";
            return;
        }

        let container = _this.pagination_container;
        let metadata = _this.pagination_metadata;
        let onclick_handler = _this.add_filter_and_fetch_data;
        _this.apply_pagination(container, metadata, onclick_handler, _this);
    }

    get_whatsapp_campaign_data(show_loader=true, is_pagination=false){
        if (show_loader){
            active_user_stats_data_loader();
        }
        let _this = this;        
        let number_of_pages = document.getElementById('number_of_pages');
        let selected_page = [...number_of_pages.selectedOptions]
                        .map(option => option.value);
        this.number_of_records = selected_page[0]
        let filters = get_url_multiple_vars();

        let request_params = {
            "bot_pk": filters["bot_pk"][0],
            "campaign_ids": CAMPAIGN_IDS,
            // "filter_date_type": FILTER_DATE_TYPE,
            // "start_date": START_DATE,
            // "end_date": END_DATE,
            "status_filter": STATUS_FILTER,
            'quick_reply': QUICK_REPLY_FILTER,
            'templates': TEMPLATE_FILTER,
            'number_of_records': this.number_of_records,
            'page': ((filters["page"] && filters["page"][0]) || 1),
            'searched_value': SEARCHED_VALUE,
            'searched_type': SEARCHED_TYPE,
            'is_template_select': false,
            'is_first_render': IS_FIRST_RENDER,
            'is_pagination': is_pagination,
            'test_message_filter': TEST_MESSAGE_FILTER,
        }
        let json_params = JSON.stringify(request_params);
        let encrypted_data = campaign_custom_encrypt(json_params);
        encrypted_data = {
            "Request": encrypted_data
        };
        let params = JSON.stringify(encrypted_data);
    
        let xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/campaign/get-whatsapp-audience-campaign-details/", true);
        xhttp.timeout = API_TIMEOUT;
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                let response = JSON.parse(this.responseText);
                response = campaign_custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    _this.pagination_metadata = response.pagination_metadata;
                    TOTAL_ENTRY = response.pagination_metadata.total_count
                    // START_DATE = response["date_range_list"][0]
                    // END_DATE = response["date_range_list"][1]
                    // $("#whatsapp-campaign-date-range").html(`<span>Date:&nbsp; </span> ${convert_date_format(START_DATE)} - ${convert_date_format(END_DATE)}`)
                    _this.set_campaign_data(response["data"])
                    $('#select-template-name').multiselect("destroy");
                    $('#select-quick-reply').multiselect("destroy");
                    let selected_template_names = TEMPLATE_FILTER
                    if (selected_template_names.length == 0){
                        selected_template_names = response['selected_template_names']
                    }
                    let all_campaigns_selected = false;
                    if (!IS_FIRST_RENDER){
                        all_campaigns_selected = $("#select-whatsapp-campaign-reports option:not(:selected)").length == 0;
                    }
                    _this.updating_filter_data(response["quick_reply_data"],  response["template_names"], selected_template_names, all_campaigns_selected)
                    if (IS_FIRST_RENDER) {
                        ALL_CAMPAIGN_LIST = response['all_campaign_list']
                    }
                    if (IS_FIRST_RENDER || IS_TEMPLATE_SELECT) {
                        // $('#select-whatsapp-campaign-reports').multiselect("destroy");
                        _this.update_campaign_dropdown(response['selected_campaigns'])
                        IS_FIRST_RENDER = false;
                    }
                    if (!is_pagination){
                        set_user_stats(response["user_stats_list"][0]);
                    }
                    deactive_user_stats_data_loader();

                } else if (response["status"] == 401) {
                    go_back();
                    
                } else {
                    show_campaign_toast(response["message"])
                }
                setTimeout(()=>{
                    $(".whatsapp_campaign-reload-svg").removeClass('active');
                    $("#whatsapp_campaign-reload-btn").css("pointer-events", "auto");
                },3000)
            } else if(this.readyState == 4 && this.status == 403){
                trigger_session_time_out_modal();
            }
        }
        xhttp.ontimeout = (e) => {
            show_campaign_toast("The connection has timed out, please try again later");
            $(".whatsapp_campaign-reload-svg").removeClass('active');
            $("#whatsapp_campaign-reload-btn").css("pointer-events", "auto");
            $('.search-btn').removeClass('active');
            $('.search-btn').prop('disabled', true);
        };
        xhttp.send(params);
    }

    update_campaign_dropdown(selected_campaigns){
        $("#select-whatsapp-campaign-reports").empty();
        let all_campaigns = ALL_CAMPAIGN_LIST
        let unselected_campaigns = []
        if (selected_campaigns == undefined) {
            selected_campaigns = CAMPAIGN_IDS
        }

        for(let cmp=0; cmp<all_campaigns.length; cmp++){
            if (selected_campaigns.includes(all_campaigns[cmp][0].toString()) || selected_campaigns.includes(all_campaigns[cmp][0])){
                $('#select-whatsapp-campaign-reports').append($("<option></option>").attr({value:all_campaigns[cmp][0],selected:'selected'}).text(all_campaigns[cmp][1])); 
            }else{
                unselected_campaigns.push(all_campaigns[cmp]);
            }
        }
        for(let cmp=0; cmp<unselected_campaigns.length; cmp++){
            $('#select-whatsapp-campaign-reports').append($("<option></option>").attr({value:unselected_campaigns[cmp][0]}).text(unselected_campaigns[cmp][1])); 
        }

        $('#select-whatsapp-campaign-reports').selectpicker({
            liveSearchPlaceholder: 'Search',
            noneResultsText: "No results matched",
            liveSearch: true,
            size: 5,
        });
        $('#select-whatsapp-campaign-reports').selectpicker('refresh');
        // $('#select-whatsapp-campaign-reports').multiselect("refresh");
    }

    updating_filter_data(quick_replies, template_names, selected_template_names, all_campaigns_selected){
        if (DEFAULT_TEMPLATES.length < 1){
            DEFAULT_TEMPLATES = selected_template_names
        }
        
        // Dropdown for Quick Reply
        let show_qr_chips = false;
        $("#quick_reply_multiselect_div").next('.template-name-chips-div').empty()
        $("#quick_reply_multiselect_div").next('.template-name-chips-div').hide();
        $("#select-quick-reply").empty(); 
        if (quick_replies.length > 0){
            $('#quick_reply_container').show();
            for(let qr=0; qr<quick_replies.length; qr++){
                if (QUICK_REPLY_FILTER.includes(quick_replies[qr])){
                    show_qr_chips = true;
                    $('#select-quick-reply').append($("<option></option>").attr({value:quick_replies[qr],selected:'selected'}).text(quick_replies[qr])); 
                    $("#quick_reply_multiselect_div").next('.template-name-chips-div').append('<div class="chips" id="' + quick_replies[qr] + '">'+ quick_replies[qr] + '<span id="' + quick_replies[qr] + '" class="cross-icon" style="display: inline-flex;" onclick="remove_selected_chips(this)"><svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2.3938 2.25L9.60619 9.75" stroke="white" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"></path><path d="M9.6062 2.25L2.39381 9.75" stroke="white" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"></path></svg></span></div>')
                }else{
                    $('#select-quick-reply').append($("<option></option>").attr({value:quick_replies[qr]}).text(quick_replies[qr])); 
                }
                
            }
            if (show_qr_chips){
                $("#quick_reply_multiselect_div").next('.template-name-chips-div').show();
            }
        }else{
            $('#quick_reply_container').hide();
        }
        $('#select-quick-reply').multiselect({
            nonSelectedText: 'Choose Quick Reply',
            enableFiltering: true,
            enableCaseInsensitiveFiltering: true,
            selectAll: true,
            includeSelectAllOption: true,
        });
        $('#select-quick-reply').multiselect("refresh");
        $('#quick_reply_multiselect_div ul li input').change(() => {
            $("#quick_reply_multiselect_div").next('.template-name-chips-div').empty()
            $('#quick_reply_multiselect_div ul li input:checked').each((indx, element) => {
                $("#quick_reply_multiselect_div").next('.template-name-chips-div').append('<div class="chips" id="' + element.value + '">'+ element.value + '<span id="' + element.value + '" class="cross-icon" style="display: inline-flex;" onclick="remove_selected_chips(this)"><svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2.3938 2.25L9.60619 9.75" stroke="white" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"></path><path d="M9.6062 2.25L2.39381 9.75" stroke="white" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"></path></svg></span></div>')
            })
            $(".template-name-chips-div #multiselect-all").remove();
            if ($("#quick_reply_multiselect_div").next('.template-name-chips-div').is(':empty')) {
                $("#quick_reply_multiselect_div").next('.template-name-chips-div').hide();
            }
            else {
                $("#quick_reply_multiselect_div").next('.template-name-chips-div').show();
            }
    
        })
        if (!SHOW_QR_DROP_DOWN || quick_replies.length < 1){
            $('#quick_reply_container').hide();
        }else{
            $('#quick_reply_container').show();
        }
        $("#quick_reply_multiselect_div button.multiselect").click(function() {
            $("#campaign_custom_filter_modal .modal-body").animate({ scrollTop: 210 }, 1000);
        });

        // Dropdown for template
        $("#template_name_multiselect_div").next('.template-name-chips-div').empty();
        $("#template_name_multiselect_div").next('.template-name-chips-div').hide();
        $("#select-template-name").empty();
        if (template_names.length > 0 && selected_template_names.length > 0){
            $("#template_name_container").show();
            for(let temp=0; temp<template_names.length; temp++){
                if (selected_template_names.includes(template_names[temp])){
                    if (all_campaigns_selected){
                        $('#select-template-name').append($("<option></option>").attr({value:template_names[temp],selected:'selected'}).text(template_names[temp]));
                        $("#template_name_multiselect_div").next('.template-name-chips-div').append('<div class="chips" id="' + template_names[temp] + '">'+ template_names[temp] + '<span id="' + template_names[temp] + '" class="cross-icon" style="display: inline-flex;" onclick="remove_selected_chips(this)"><svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2.3938 2.25L9.60619 9.75" stroke="white" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"></path><path d="M9.6062 2.25L2.39381 9.75" stroke="white" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"></path></svg></span></div>')
                    }
                    else{
                        $("#template_name_multiselect_div").next('.template-name-chips-div').append('<div class="chips" id="' + template_names[temp] + '">'+ template_names[temp] + '</div>')
                    }
                }else if(all_campaigns_selected){
                    $('#select-template-name').append($("<option></option>").attr({value:template_names[temp]}).text(template_names[temp]));
                }
            }
            if(selected_template_names.length > 0){
                $("#template_name_multiselect_div").next('.template-name-chips-div').show();
            }
        }else{
            $("#template_name_container").hide();
        }
        if (all_campaigns_selected){
            $('#select-template-name').show()
            $('#select-template-name').multiselect({
                nonSelectedText: 'Choose Template Name',
                enableFiltering: true,
                enableCaseInsensitiveFiltering: true,
                selectAll: true,
                includeSelectAllOption: true,
            
            });
            $('#select-template-name').multiselect("refresh");
        } else{
            $('#select-template-name').hide()
        }
            
        $('#template_name_multiselect_div ul li input').change(() => {
            $("#template_name_multiselect_div").next('.template-name-chips-div').empty()
            $('#template_name_multiselect_div ul li input:checked').each((indx, element) => {
                $("#template_name_multiselect_div").next('.template-name-chips-div').append('<div class="chips" id="' + element.value + '">'+ element.value + '<span id="' + element.value + '" class="cross-icon" style="display: inline-flex;" onclick="remove_selected_chips(this)"><svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2.3938 2.25L9.60619 9.75" stroke="white" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"></path><path d="M9.6062 2.25L2.39381 9.75" stroke="white" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"></path></svg></span></div>')
            })
            $(".template-name-chips-div #multiselect-all").remove();
            if ($("#template_name_multiselect_div").next('.template-name-chips-div').is(':empty')) {
                $("#template_name_multiselect_div").next('.template-name-chips-div').hide();
            }
            else {
                $("#template_name_multiselect_div").next('.template-name-chips-div').show();
            }
        })
        $("#template_name_multiselect_div button.multiselect").click(function() {
            $("#campaign_custom_filter_modal .modal-body").animate({ scrollTop: 210 }, 1000);
        });
    }

    set_campaign_data(campaign_data) {
        let _this = this;
        if (campaign_data) {
            _this.campaign_data = campaign_data;
            _this.data_checklist.campaign_data = true;
        }

        _this.check_and_initialize_table();
    }

    check_and_initialize_table() {
        let _this = this;

        if (_this.data_checklist.campaign_data == false) return false;

        _this.initialize_table();
    }

    get_row_html(name, campaign_data_obj) {
        let _this = this;
        let data = campaign_data_obj[name];
        if(data == null || data == undefined) {
            data = "-";
        }
        let html = "";
        let greater_than_limit = false;
                if (data.length > 21){
                    greater_than_limit = true;
                }
        switch (name) {
            case "phone_number":
                html = `<span class="text-capitalize">${data}</span>`;
                break;

            case "recipient_id":
                if (greater_than_limit){
                html = `<span class="whatsapp-history-table-tooltipped" data-toggle="tooltip" title="${data}">${data}</span>`;
                }
                else{
                html = `<span class="whatsapp-history-table-tooltipped">${data}</span>`;
                }
                break;
            
            case "status":
                html = `<span class="text-capitalize">${data}</span>`;
                break;

            case "campaign":
                if (greater_than_limit){
                html = `<div class="d-flex "><span class="whatsapp-history-table-tooltipped" data-toggle="tooltip" title="${data}" data-original-title="${data}">${data}</span>${campaign_data_obj['is_test'] ? '<span class="campaign-message-type-indegator">Test</span>' : ""}</div>`;
                }
                else{
                    html = `<div class="d-flex "><span class="whatsapp-history-table-tooltipped" data-toggle="tooltip">${data}</span>${campaign_data_obj['is_test'] ? '<span class="campaign-message-type-indegator">Test</span>' : ""}</div>`;
                }
                break;

            case "template":
                if (greater_than_limit){
                html = `<span class="whatsapp-history-table-tooltipped" data-toggle="tooltip" title="${data}">${data}</span>`;
                }
                else{
                html = `<span class="whatsapp-history-table-tooltipped">${data}</span>`;
                }
                break;

            case "failure_reason":
                if (greater_than_limit){
                html = `<span class="text-capitalize whatsapp-history-table-tooltipped" data-toggle="tooltip" title="${data}">${data}</span>`;
                }
                else{
                html = `<span class="text-capitalize whatsapp-history-table-tooltipped">${data}</span>`;
                }
                break;

            case "quick_reply":
                if (greater_than_limit){
                html = `<span class="whatsapp-history-table-tooltipped" data-toggle="tooltip" title="${data}">${data}</span>`;
                }
                else{
                html = `<span class="whatsapp-history-table-tooltipped">${data}</span>`;
                }
                break;
            
            case "sent_time":
                html = `<span class="text-capitalize">${data}</span>`;
                break;

            case "delivered_time":
                html = `<span class="text-capitalize">${data}</span>`;
                break;  

            case "read_time":
                html = `<span class="text-capitalize">${data}</span>`;
                break;      

            case "chat_history":
                if (campaign_data_obj["status"].toLowerCase() == "failed"){
                    html = `<span class="text-capitalize">-</span>`;
                }else{
                    html = `<span class="text-capitalize"><a class="campaign-report-table-clickhere-btn" style="color: #2741FA !important;" href="/chat/user-filtered/?bot_id=` + get_url_multiple_vars()["bot_pk"][0] + `&user_id=` + campaign_data_obj['phone_number'] + `" target="_blank" >${data}</a></span>`;
                }
                break;

            default:
                html = "-";
                console.log("Error: unknown column")
                break;
        }
        return html;
    }

    get_row(campaign_data_obj) {
        let _this = this;
        const { enable_select_rows } = false;

        let campaign_data_list = [];

        let select_row_html = ""
        if (enable_select_rows) {
            campaign_data_list.push(select_row_html);
        }

        _this.active_user_metadata.lead_data_cols.forEach((column_info_obj) => {
            try {
                if (column_info_obj.selected == false) return;
                let name = column_info_obj.name;
                campaign_data_list.push(_this.get_row_html(name, campaign_data_obj));
            } catch (err) {
                console.log("ERROR get_row on adding row data of column : ", column_info_obj);
            }
        });

        return campaign_data_list;
    }

    get_rows() {
        let _this = this;
        let campaign_data_list = [];
        _this.campaign_data.forEach((campaign_data_obj) => {
            campaign_data_list.push(_this.get_row(campaign_data_obj));
        })
        return campaign_data_list;
    }

    initialize_lead_data_metadata_update_modal() {
        let _this = this;
        let lead_data_cols = _this.active_user_metadata.lead_data_cols;
        let container = document.querySelector("#lead_data_table_meta_div");
        let selected_values = [];
        let unselected_values = [];
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

        initialize_template_custom_tag_input(selected_values, unselected_values, container)
    }

    update_table_meta_deta(lead_data_cols) {
        let _this = this;
        _this.active_user_metadata.lead_data_cols = lead_data_cols;

        _this.save_table_meta_data();
        _this.initialize_table();
    }

    save_table_meta_data() {
        let _this = this;
        let lead_data_cols = _this.active_user_metadata.lead_data_cols
        window.localStorage.setItem("whatsapp_campaign_details_table_meta_data", JSON.stringify(lead_data_cols));
    }

    get_table_meta_data() {
        let _this = this;
        let lead_data_cols = window.localStorage.getItem("whatsapp_campaign_details_table_meta_data");
        if (!lead_data_cols) {
            lead_data_cols = _this.get_default_meta_data();
        } else {
            lead_data_cols = JSON.parse(lead_data_cols);
        }
        return lead_data_cols;
    }

    get_default_meta_data() {

    let lead_data_cols = [
        ['phone_number', 'Phone Number', true],
        ['recipient_id', 'Recipient ID', true],
        ['status', 'Status', true],
        ['campaign', 'Campaign', true],
        ['template', 'Template Name', true],
        ['failure_reason', 'Failure Reason', true],
        ['quick_reply', 'Quick Reply', true],
        ['sent_time', 'Sent Time', true],
        ['delivered_time', 'Delivered Time', true],
        ['read_time', 'Read Time', true],
        ['chat_history', 'Chat History', true]
    ]
        

    let default_lead_data_cols = [];
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

function initialize_whatsapp_campaign_template_table() {
    if (window.location.pathname.indexOf("/campaign/whatsapp-campaign-details/") != 0) {
        return;
    }
    let campaign_table_container = document.querySelector("#whatsapp_history_table_container");
    let campaign_searchbar = document.querySelector("#whatsapp-history-search-bar");
    let pagination_container = document.getElementById("whatsapp_history_table_pagination_div");

    window.WHATSAPP_CAMPAIGN_DETAILS_TABLE = new WhatsappDetailsTable(
        campaign_table_container, campaign_searchbar, pagination_container);
}

function clear_whatsapp_audience_filter() {
    // document.getElementById("whatsapp_report_beg").checked = true;
    // document.getElementById('campaign-custom-date-select-area-flow').style.display = 'none';
    // $('#whatsapp_history_filter_custom_start_date').val(END_DATE)
    // $('#whatsapp_history_filter_custom_end_date').val(END_DATE)
    let status_checkboxes = document.querySelectorAll('[id="campaign-filter-status"]');
    for (let i=0; i<status_checkboxes.length; i++) {
        status_checkboxes[i].checked = true;
    }

    let test_message_status = document.querySelectorAll('[id="test-message-status"]');
    for (let i=0; i<test_message_status.length; i++) {
        test_message_status[i].checked = true;
    }

    let quick_replies = document.getElementById('select-quick-reply').selectedOptions;
    for (let i=0; i<quick_replies.length; i++) {
        quick_replies[i].selected = false;
    }

    let selected_templates = document.getElementById('select-template-name')
    for (let i=0; i<selected_templates.length; i++) {
        selected_templates[i].checked = false;
    }

    // FILTER_DATE_TYPE = "4";
    // START_DATE = DEFAULT_START_DATE;
    // END_DATE = DEFAULT_END_DATE;
    STATUS_FILTER = [];
    TEST_MESSAGE_FILTER = [];
    QUICK_REPLY_FILTER = [];
    TEMPLATE_FILTER = [];
    IS_TEMPLATE_SELECT = false;
    CAMPAIGN_IDS = DEFAULT_CAMPAIGN;
    SHOW_QR_DROP_DOWN = true;
    IS_FIRST_RENDER = true;
    window.WHATSAPP_CAMPAIGN_DETAILS_TABLE.get_whatsapp_campaign_data();
}

function apply_whatsapp_audience_filter(){
    // let filter_date_type = $("input[type='radio'][name='whatsapp-history-date-filter']:checked").val();

    // let start_date = "";
    // let end_date = "";

    // if (filter_date_type == "5") {
    //     start_date = document.getElementById("whatsapp_history_filter_custom_start_date").value;
    //     if (!start_date) {
    //         show_campaign_toast("The start date cannot be empty.");
    //         return;
    //     }

    //      end_date = document.getElementById("whatsapp_history_filter_custom_end_date").value;
    //     if (!end_date) {
    //         show_campaign_toast("The end date cannot be empty.");
    //         return;
    //     }

    //     let today = new Date();
    //     today = today.getFullYear() + "-" + String(today.getMonth() + 1).padStart(2, '0') + "-" + String(today.getDate()).padStart(2, '0');

    //     if (start_date > today) {
    //         show_campaign_toast("The start date cannot be greater than the current date.");
    //         return;
    //     }

    //     if (end_date > today) {
    //         show_campaign_toast("The end date cannot be greater than the current date.");
    //         return;
    //     }

    //     if (start_date > end_date) {
    //         show_campaign_toast('The start date cannot be greater than the end date.');
    //         return;
    //     }
    // }
    // FILTER_DATE_TYPE = filter_date_type;
    // START_DATE = start_date;
    // END_DATE = end_date;
    IS_TEMPLATE_SELECT = false;
    let status_checkboxes = document.querySelectorAll('[id="campaign-filter-status"]');
    let status_filter = [];

    for (let i=0; i<status_checkboxes.length; i++) {
        if (status_checkboxes[i].checked) {
            status_filter.push(status_checkboxes[i].value);
        }
    }

    let test_message_status = document.querySelectorAll('[id="test-message-status"]');
    let test_message_filter = []
    for (let i=0; i<test_message_status.length; i++) {
        if (test_message_status[i].checked) {
            test_message_filter.push(test_message_status[i].value);
        }
    }
    TEST_MESSAGE_FILTER = test_message_filter
    STATUS_FILTER = status_filter
    let quick_replies = document.getElementById('select-quick-reply');
    let selected_quick_replies = [...quick_replies.selectedOptions]
                    .map(option => option.value);
    QUICK_REPLY_FILTER = selected_quick_replies
    let templates = document.getElementById('select-template-name');
    let selected_templates = [...templates.selectedOptions]
                    .map(option => option.value);
    TEMPLATE_FILTER = selected_templates
    let filters = get_url_multiple_vars();
    filters["page"] = "1"
    window.WHATSAPP_CAMPAIGN_DETAILS_TABLE.update_url_with_filters(filters);
    window.WHATSAPP_CAMPAIGN_DETAILS_TABLE.get_whatsapp_campaign_data();
    $("#campaign_custom_filter_modal").modal("hide");
}


function go_back() {
    window.location.href = "/campaign/dashboard/?bot_pk=" + get_url_multiple_vars()["bot_pk"][0];
}

function initialize_template_custom_tag_input(selected_values, unselected_values, container) {
    window.LEAD_DATA_METADATA_INPUT = new CognoAICustomTagInput(container, selected_values, unselected_values);
}

function save_whatsapp_campaign_details_table_metadata() {

    let lead_data_cols = window.WHATSAPP_CAMPAIGN_DETAILS_TABLE.active_user_metadata.lead_data_cols;

    let selected_values = [];
    let unselected_values = [];
    window.LEAD_DATA_METADATA_INPUT.selected_values.filter((obj) => {
        selected_values.push(obj.key);
    });
    window.LEAD_DATA_METADATA_INPUT.unselected_values.filter((obj) => {
        unselected_values.push(obj.key);
    });

    if (selected_values.length < 2) {
        show_campaign_toast("Minimum 2 columns should be selected for the table.");
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

    window.WHATSAPP_CAMPAIGN_DETAILS_TABLE.update_table_meta_deta(lead_data_cols)
}

// function show_custom_date_user_filter(el) {
//     if (el.id === 'whatsapp_report_custom_date_btn') {
//         document.getElementById('campaign-custom-date-select-area-flow').style.display = 'flex';
//     } else {
//         document.getElementById('campaign-custom-date-select-area-flow').style.display = 'none';
//     }
// }

function export_whatsapp_campaign_reports_request(el) {

    let email_id = document.getElementById('filter-data-email-2').value.trim();

    if (email_id == '') {
        document.getElementById('general-error-message-2').innerHTML = 'Please enter your valid Email ID';
        document.getElementById("filter-data-email-2").style.borderColor = "#FF281A";
        return;
    } else {
        document.getElementById('general-error-message-2').innerHTML = '';
    }

    if (!validate_email(email_id)) {
        document.getElementById('general-error-message-2').innerHTML = 'Please enter a valid Email ID';
        document.getElementById("filter-data-email-2").style.borderColor = "#FF281A";
        return;
    } else {
        document.getElementById('general-error-message-2').innerHTML = '';
        document.getElementById("filter-data-email-2").style.borderColor = "#EBEBEB";
    }
    save_whatsapp_campaign_history_request_data(email_id);
}


function save_whatsapp_campaign_history_request_data(email_id=null) {

    let filters = get_url_multiple_vars();

    let request_params = {
        "bot_pk": filters["bot_pk"][0],
        "campaign_ids": CAMPAIGN_IDS,
        // "filter_date_type": FILTER_DATE_TYPE,
        // "start_date": START_DATE,
        // "end_date": END_DATE,
        "status_filter": STATUS_FILTER,
        'quick_reply': QUICK_REPLY_FILTER,
        'templates': TEMPLATE_FILTER,
        'searched_value': SEARCHED_VALUE,
        'searched_type': SEARCHED_TYPE,
        'is_template_select': false,
        'email_id': email_id,
        'is_first_render': IS_FIRST_RENDER,
        'test_message_filter': TEST_MESSAGE_FILTER,
        'total_entry': TOTAL_ENTRY,
        }

    let json_params = JSON.stringify(request_params);
    let encrypted_data = campaign_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    let params = JSON.stringify(encrypted_data);

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/campaign/save-export-whatsapp-campaign-history-request/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                if(TOTAL_ENTRY <= 500 || TOTAL_ENTRY > 5000){
                    show_campaign_toast(response["message"])
                }
                if(response["file_path"] && response["file_path"].trim()){
                    window.location.href = window.location.origin + '/' + response["file_path"]
                    $('.custom_export_btn').prop('disabled', false);
                }
                document.getElementById('filter-data-email-2').value = "";
                $("#campaign_multi_export_modal").modal("hide");
            } else {
                show_campaign_toast(response["message"])
            }
        } else if(this.readyState == 4 && this.status == 403){
            trigger_session_time_out_modal();
        }
    }
    xhttp.send(params);
}

$(".campaign-filter-status-success, .campaign-filter-status-failed").change(function(){

    let status_checkboxes = document.querySelectorAll('[id="campaign-filter-status"]');
    if (status_checkboxes[0].checked == false && status_checkboxes[1].checked == true){
        $('#quick_reply_container').hide();
        SHOW_QR_DROP_DOWN = false;
    }else{
        $('#quick_reply_container').show();
        SHOW_QR_DROP_DOWN = true;
    }
});

$("#number_of_pages").change(function(){
    window.WHATSAPP_CAMPAIGN_DETAILS_TABLE.get_whatsapp_campaign_data();
});

$('#select-whatsapp-campaign-reports').change(function(){
    IS_TEMPLATE_SELECT = false;
    QUICK_REPLY_FILTER = [];
    TEMPLATE_FILTER = [];
    let options = document.getElementById("select-whatsapp-campaign-reports").options;
    let campaign_ids = [];

    for (let i=0; i<options.length; i++) {
        if (options[i].selected) {
            campaign_ids.push(options[i].value);
        }
    }
    CAMPAIGN_IDS = campaign_ids
    window.WHATSAPP_CAMPAIGN_DETAILS_TABLE.get_whatsapp_campaign_data();
});

function apply_search_on_whatsapp_history(){
    let searched_val = document.getElementById("whatsapp-history-search-bar").value.trim();
    document.getElementById("whatsapp-history-search-bar").value = searched_val;
    if(searched_val == "") return;

    SEARCHED_VALUE = searched_val.trim();
    let isnum = /^\d+$/.test(searched_val);
    if(isnum == true){
        SEARCHED_TYPE = "phone_number"
    } else{
        SEARCHED_TYPE = "recipient_id"
    }
    window.WHATSAPP_CAMPAIGN_DETAILS_TABLE.get_whatsapp_campaign_data();
}

$("#whatsapp-history-search-bar").keyup(function(event) {
    if (event.keyCode === 13) {
        $("#whatsapp-details-search-button").click();
    }
});

function set_user_stats(user_stats_list){
    if(user_stats_list == undefined){
        document.getElementById("total_sent_value").innerHTML = 0
        document.getElementById("total_delivered_value").innerHTML = 0
        document.getElementById("total_read_value").innerHTML = 0
        document.getElementById("total_failed_value").innerHTML = 0
        document.getElementById("total_replied_value").innerHTML = 0
        document.getElementById("total_processed_value").innerHTML = 0
        document.getElementById("total_test_sent_value").innerHTML = 0
    document.getElementById("total_test_failed_value").innerHTML = 0
        return;
    }
    document.getElementById("total_sent_value").innerHTML = user_stats_list['total_sent'];
    document.getElementById("total_delivered_value").innerHTML = user_stats_list['total_delivered'];
    document.getElementById("total_read_value").innerHTML = user_stats_list['total_read'];
    document.getElementById("total_failed_value").innerHTML = user_stats_list['total_failed'];
    document.getElementById("total_replied_value").innerHTML = user_stats_list['total_replied'];
    document.getElementById("total_processed_value").innerHTML = user_stats_list['total_processed'];
    document.getElementById("total_test_sent_value").innerHTML = user_stats_list['total_test_sent'];
    document.getElementById("total_test_failed_value").innerHTML = user_stats_list['total_test_failed'];
}

function open_whatsapp_export_modal() {
    if(TOTAL_ENTRY == 0){
        show_campaign_toast("There is no data available to export for the selected campaign/s and the filters selected.");
        return;
    }else if(TOTAL_ENTRY > 5000) {
        $('#campaign_multi_export_modal').modal('show');
        return;
    } else if(TOTAL_ENTRY > 500){
        show_campaign_toast('The file download will begin shortly, please wait for some time.', 7000);
    }
    $('.custom_export_btn').prop('disabled', true);
    save_whatsapp_campaign_history_request_data();
}

function convert_date_format(date) {
    let splitted_date = date.split("-")
    return splitted_date.reverse().join("/")
}

function reload_whatsapp_audience_page(){
    $(".whatsapp_campaign-reload-svg").addClass('active');
    $("#whatsapp_campaign-reload-btn").css("pointer-events", "none");
    document.getElementById("whatsapp-history-search-bar").value = '' ;
    IS_FIRST_RENDER = true;
    update_whatsapp_campaign_data();
    show_campaign_toast("Please wait while we are updating the data");
    $('.search-btn').removeClass('active');
    $('.search-btn').prop('disabled', true);
}

$('#whatsapp-history-search-bar').on('input',function(event) {
    if ($(this).val() != '') {
        $('.search-btn').addClass('active');
        $('.search-btn').prop('disabled', false);
    } else {
        $('.search-btn').removeClass('active');
        $('.search-btn').prop('disabled', true);
        update_whatsapp_campaign_data();
    }
});

function active_user_stats_data_loader(){
    if (IS_FIRST_RENDER){
        $('.camapign-status-card-reload-btn-div').hide();
    }
    $('#no-data-loader').show();
    $('#whatsapp_campaign_table_wrapper').hide();
    $('#whatsapp_history_table_pagination_div').hide();
    $('.custom_filter_btn').prop('disabled', true);
    $('.custom_export_btn').prop('disabled', true);
    $('.custom_metadata_btn').prop('disabled', true);
    $('.whatsapp_history_search_bar').prop('disabled', true);   
}

function deactive_user_stats_data_loader(){
    $('#no-data-loader').hide();
    $('#whatsapp_campaign_table_wrapper').show();
    $('#whatsapp_history_table_pagination_div').show();
    $('.custom_filter_btn').prop('disabled', false);
    $('.custom_export_btn').prop('disabled', false);
    $('.custom_metadata_btn').prop('disabled', false);
    $('.whatsapp_history_search_bar').prop('disabled', false);
    $('.camapign-status-card-reload-btn-div').show();
}
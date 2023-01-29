import axios from "axios";

import {
    custom_decrypt,
    get_params,
    showToast,
    stripHTML,
    strip_unwanted_characters,
    EncryptVariable,
    encrypt_variable,
    getCsrfToken,
    is_mobile,
    change_date_format_original,
    is_valid_date,
    validate_email,
    generate_random_string,
} from "../utils";

import { get_messages_html } from "./archive_customer";

import { 
    set_form_state, 
    generate_option_map, 
    get_field_html_based_input_type,
    update_dependent_inputs 
} from "../admin/form_preview";

import {
    get_text_data,
    get_radio_data,
    get_checkbox_data,
    get_datepicker_data,
    get_dropdown_data,
    get_attachment_data,
    save_system_message,
    append_system_text_response,
} from "../agent/chatbox";

const state = {
    filter: {
        is_applied: false,
        agent_usernames: null,
        lead_source: null,
        lead_category: null,
        start_date: null,
        end_date: null,
    },
    page: 1,
    initial_refresh: true,
    refresh_interval: 0,
    raise_ticket_form: {},
    customer: {
        name: '',
        email: '',
        phone: ''
    },
    session_id: '',
    checked_leads: [],
    is_global_lead_checkbox_enabled: false,
    total_leads: 0,
    current_selected_bot: '',
};

$(window).ready(function () {

    if (!window.location.pathname.includes('followup-leads')) {
        unset_followup_lead_filter();
        return;
    }

    apply_event_listeners();

    load_followup_lead_filters();

    state.refresh_interval = parseInt(REFRESH_INTERVAL);

    initilialize_multiselect_filter_options();

    setInterval(() => {
        initialize_followup_leads_table(state.page);
    }, state.refresh_interval * 1000);

    setTimeout(() => {
        apply_filter_datepicker();
    }, 500);

    state.initial_refresh = false;

});

function load_followup_lead_filters() {

    let filter = state.filter;

    if(localStorage.getItem(`followup_lead_is_applied`)) {

        filter.is_applied = (localStorage.getItem(`followup_lead_is_applied`) === "true" );
        if(!window.IS_USER_AGENT) {
            filter.agent_usernames = JSON.parse(localStorage.getItem(`followup_lead_agent_usernames`));
        }
        filter.lead_source = JSON.parse(localStorage.getItem(`followup_lead_source`));
        filter.lead_category = JSON.parse(localStorage.getItem(`followup_lead_category`));
        filter.start_date = localStorage.getItem(`followup_lead_start_date`);
        filter.end_date = localStorage.getItem(`followup_lead_end_date`);

        if(!window.IS_USER_AGENT && filter.agent_usernames.length){
            filter.agent_usernames.forEach(element => {
                $('#select-agent-username-dropdown option[value="'+element+'"]').prop('selected', true)
            });
        }

        if(filter.lead_source.length){
            filter.lead_source.forEach(element => {
                $('#select-source-dropdown option[value="'+element+'"]').prop('selected', true)
            });
        }

        if(filter.lead_category.length){
            filter.lead_category.forEach(element => {
                $('#select-categories-dropdown option[value="'+element+'"]').prop('selected', true)
            });
        }

    }
}

function apply_filter_datepicker() {

    let filter = state.filter;

    if(filter.start_date) {
        let start_date = change_date_format_original(filter.start_date);
        $('#followup-filter-start-date').datepicker({ dateFormat: 'dd-mm-yy', prevText: "Previous" }).val(start_date.trim()) 
    }

    if(filter.end_date) {
        let end_date = change_date_format_original(filter.end_date);
        $('#followup-filter-end-date').datepicker({ dateFormat: 'dd-mm-yy', prevText: "Previous" }).val(end_date.trim()) 
    }
}

function apply_event_listeners() {
    $("#apply_filter_followup_lead_btn").on("click", function (e) {
        apply_followup_lead_filter();
    });

    $("#followup_lead_transfer_btn").on("click", function (e) {
        load_lead_transfer_modal();
    });

    $("#followup_lead_mark_complete_btn").on("click", function (e) {
        followup_lead_complete();
    });

    $("#transfer-lead-btn").on("click", function (e) {
        followup_lead_transfer();
    });

    $("#lead-transfer-toast-cancel").on("click", function (e) {
        $('#lead-toast-container').css('display', 'none');
    });
}

function initilialize_multiselect_filter_options() {

    $('#tranfer-lead-select-agent-dropdown').multiselect({
        nonSelectedText: 'Select Agent',
        enableFiltering: true,
        enableCaseInsensitiveFiltering: true,
        selectAll: false,
        includeSelectAllOption: false,
    });

    $('#select-agent-username-dropdown').multiselect({
        nonSelectedText: 'Select Agent',
        enableFiltering: true,
        enableCaseInsensitiveFiltering: true,
        selectAll: true,
        includeSelectAllOption: true,
    });

    $('#select-source-dropdown').multiselect({
        nonSelectedText: 'Select Source',
        enableFiltering: true,
        enableCaseInsensitiveFiltering: true,
        selectAll: true,
        includeSelectAllOption: true,
    });
    
    $('#select-categories-dropdown').multiselect({
        nonSelectedText: 'Select Category',
        enableFiltering: true,
        enableCaseInsensitiveFiltering: true,
        selectAll: true,
        includeSelectAllOption: true,
    });

    $(".livechat-multiselect-dropdown.livechat-multiselect-filter-dropdown .multiselect-container>li>a>label").addClass("custom-checkbox-input");
    $(".livechat-multiselect-dropdown.livechat-multiselect-filter-dropdown .multiselect-container>li").find(".custom-checkbox-input").append("<span class='checkmark'></span>");

}

export async function initialize_followup_leads_table(page) {
    if (state.initial_refresh) {
        toggle_loader("show");
    }

    state.page = page;

    const response = await get_followup_leads(page); 
    toggle_loader("hide");
    state.total_leads = response.followup_leads.length;

    if (response.followup_leads.length > 0) {
        const table_html = get_table_html(response);

        document.getElementById("livechat_followup_lead_no_data").style.display = "none";

        $("#livechat_followup_lead_table_div").html(table_html);
        $("#livechat_followup_lead_table_div").css("display", "block");

        initialize_datatable(response.start_point, response.total_leads);
        apply_pagination(response.pagination_data);

        apply_event_listeners_on_leads();
        
    } else {
        document.getElementById(
            "livechat_followup_lead_table_div"
        ).style.display = "none";
        document.getElementById("livechat_followup_lead_no_data").style.display =
            "block";
    }
    enable_disable_transfer_complete_btns();

}

function apply_event_listeners_on_leads() {

    $(".view_transcript_btn").on("click", function (e) {
        load_followup_lead_transcripts(e.target);
    });

    $('.followup-lead-checkbox').on("click", function (e) {
        let checked_leads = document.querySelectorAll('.followup-lead-checkbox:checked');

        if(checked_leads.length) {
            $("#followup_lead_transfer_btn, #followup_lead_mark_complete_btn").removeClass('disable-btn');
            $("#followup_lead_transfer_btn, #followup_lead_mark_complete_btn").prop('disabled', false);
        } else {
            $("#followup_lead_transfer_btn, #followup_lead_mark_complete_btn").addClass('disable-btn');
            $("#followup_lead_transfer_btn, #followup_lead_mark_complete_btn").prop('disabled', true);
        }

        state.checked_leads = [];
        for(let i = 0; i < checked_leads.length; i++) {
            state.checked_leads.push(checked_leads[i].id);
        }

        if(checked_leads.length == state.total_leads) {
            $("#followup-lead-checkbox-header").prop('checked', true);
            state.is_global_lead_checkbox_enabled = true;
        } else {
            $("#followup-lead-checkbox-header").prop('checked', false);
            state.is_global_lead_checkbox_enabled = false;
        }

    });

    $("#followup-lead-checkbox-header").on("click", function (e) {

        if(e.target.checked) {

            $(".followup-lead-checkbox").prop('checked', true);
            let checked_leads = document.querySelectorAll('.followup-lead-checkbox:checked');
            state.is_global_lead_checkbox_enabled = true;

            state.checked_leads = [];
            for(let i = 0; i < checked_leads.length; i++) {
                state.checked_leads.push(checked_leads[i].id);
            }

        } else {
            $(".followup-lead-checkbox").prop('checked', false);
            state.is_global_lead_checkbox_enabled = false;
            state.checked_leads = [];
        }
        enable_disable_transfer_complete_btns();

    });
}

function enable_disable_transfer_complete_btns() {
    if(state.checked_leads.length) {
        $("#followup_lead_transfer_btn, #followup_lead_mark_complete_btn").removeClass('disable-btn');
        $("#followup_lead_transfer_btn, #followup_lead_mark_complete_btn").prop('disabled', false);
    } else {
        $("#followup_lead_transfer_btn, #followup_lead_mark_complete_btn").addClass('disable-btn');
        $("#followup_lead_transfer_btn, #followup_lead_mark_complete_btn").prop('disabled', true);
    }
}

function apply_event_listeners_on_agents() {

    $("#tranfer-lead-select-agent-dropdown").on("change", function (e) {
        let selected_agent = $("#tranfer-lead-select-agent-dropdown").val();

        if(selected_agent) {
            $("#transfer-lead-btn").removeClass('disable-btn');
            $("#transfer-lead-btn").prop('disabled', false); 
        } else {
            $("#transfer-lead-btn").addClass('disable-btn');
            $("#transfer-lead-btn").prop('disabled', true);             
        }
    });

}

function toggle_loader(value) {
    value = value == "show" ? "block" : "none";

    document.getElementById("livechat_followup_leads_loader").style.display = value;
}

export function get_followup_leads(page) {
    return new Promise((resolve, reject) => {
        let json_string = {
            page: page,
        };

        if (state.filter.is_applied) {
            const filter = state.filter;

            json_string = {
                ...json_string,
                lead_source: filter.lead_source,
                lead_category: filter.lead_category,
                start_date: filter.start_date,
                end_date: filter.end_date,
            };

            if(!window.IS_USER_AGENT) {
                json_string = {
                    ...json_string,
                    agent_usernames: filter.agent_usernames,
                };    
            }
        }
        json_string = JSON.stringify(json_string);
        const params = get_params(json_string);

        let config = {
              headers: {
                'X-CSRFToken': getCsrfToken(),
              }
            }

        axios
            .post("/livechat/get-livechat-followup-leads/", params, config)
            .then((response) => {
                response = custom_decrypt(response.data);
                response = JSON.parse(response);
                
                if(response.status == 200) {
                    resolve(response);
                }
            })       
            .catch((err) => {
                console.log(err);
            });
    });

}

function get_table_html(response) {
    let table_html = `<table role="grid" id="follow-leads-table" class="display dataTable no-footer" aria-describedby="table-agent-details_info">`;

    table_html += get_table_header(response.is_user_agent);
    table_html += get_table_body(response.followup_leads, response.is_user_agent);
    table_html += `</table>`;
    return table_html;
}

function get_table_header(is_user_agent) {

    let agent_name_header = '';
    if(!is_user_agent) {
        agent_name_header = '<th role="columnheader" class="sorting_disabled" rowspan="1" colspan="1">Agent Name</th>';
    }

    let lead_checkbox_header = '<input type="checkbox" class="table-input-checkbox" id="followup-lead-checkbox-header">';
    if(state.is_global_lead_checkbox_enabled) {
        lead_checkbox_header = '<input type="checkbox" class="table-input-checkbox" id="followup-lead-checkbox-header" checked>';
    }

    return `
        <thead role="rowgroup">
            <tr role="row">
                <th role="columnheader" class="sorting_disabled" rowspan="1" colspan="1" >
                    <label class="custom-checkbox-input">
                        ${lead_checkbox_header}
                        <span class="checkmark"></span>                            
                    </label>
                </th>
                <th role="columnheader" class="sorting_disabled" rowspan="1" colspan="1">Customer Details</th>
                ${agent_name_header}
                <th role="columnheader" class="sorting_disabled" rowspan="1" colspan="1">Source</th>
                <th role="columnheader" class="sorting_disabled" rowspan="1" colspan="1">Channel</th>
                <th role="columnheader" class="sorting_disabled" rowspan="1" colspan="1">Categories</th>
                <th role="columnheader" class="sorting_disabled" rowspan="1" colspan="1">Timestamp</th>
                <th role="columnheader" class="sorting_disabled" rowspan="1" colspan="1">Chat History</th>

            </tr>
        </thead>`;
}

function get_table_body(followup_leads, is_user_agent) {
    let body_html = ``;
    followup_leads.forEach((followup_lead) => {
        body_html += `<tr role="row">`;

        if(state.checked_leads.includes(followup_lead.pk)) {
            body_html += get_col(`<label class="custom-checkbox-input"><input id="${followup_lead.pk}" type="checkbox" class="table-input-checkbox followup-lead-checkbox" style="cursor: pointer;" checked><span class="checkmark"></span></label>`);
        } else {
            body_html += get_col(`<label class="custom-checkbox-input"><input id="${followup_lead.pk}" type="checkbox" class="table-input-checkbox followup-lead-checkbox" style="cursor: pointer;"><span class="checkmark"></span></label>`);
        }
        body_html += get_col(` Name: ${followup_lead.username} <br> Mobile No. ${followup_lead.phone} <br> Email address: ${followup_lead.email}`);
        if(!is_user_agent) {
            body_html += get_col(followup_lead.agent);
        }
        body_html += get_col(followup_lead.source);
        body_html += get_col(followup_lead.channel);
        body_html += get_col(followup_lead.category);
        body_html += get_col(followup_lead.assigned_date);
        body_html += get_col(`<button class="view_transcript_btn follow-up-lead-chat-hist-btn" data-bot-id="${followup_lead.bot_pk}" id="followup-lead-transcript-btn_${followup_lead.pk}">Chat History</button>`);

        body_html += "</tr>";
    });

    return body_html;
}

function get_col(value) {
    return `
            <td role="cell">${value}</td>`;
}

function initialize_datatable(start_point, total_leads) {
    $("#follow-leads-table").DataTable({
        language: {
            info: `Showing _START_ to _END_ entries out of ${total_leads}`,
            infoEmpty: "No records available",
            infoFiltered: "(filtered from _MAX_ total records)",
        },
        bPaginate: false,
        ordering: false,
        infoCallback: function (settings, start, end, max, total, pre) {
            if (settings.oPreviousSearch["sSearch"] != "") {
                return pre;
            }
            end = start_point - 1 + end;
            start = start_point - 1 + start;
            return `Showing ${start} to ${end} entries out of ${total_leads}`;
        },
        drawCallback: function( settings ) {
            if(settings.aiDisplay.length == 0){
                $("#follow-leads-table thead th .custom-checkbox-input").hide();
            }
            else{
                $("#follow-leads-table thead th .custom-checkbox-input").show();
            }
        },
    });

    const table = $("#follow-leads-table").DataTable();

    const value = document.getElementById("followup-lead-history-table-search").value;
    
    if (value != "") {
        table.search(value).draw();
    }

    $("#followup-lead-history-table-search").keyup(function () {
        let value = this.value;
        table.search(value).draw();
    });

}

function apply_pagination(pagination) {
    let html = `<div class="container-fluid">`;

    if (pagination.has_other_pages) {
        html += `<div class="pagination-div">
                    <ul class="pagination-content">`;

        for (let page = 1; page < pagination.page_range; ++page) {
            if (pagination.number == page) {
                if (page == 1) {
                    html += `<li class="active-page"><a data-page="${page}" class="followup-leads-pagination" style="color: #0254d7;" href="javascript:void(0)">${page}</a></li>`;
                } else if (pagination.num_pages == page) {
                    html += `<li class="active-page" style="border-radius: 0 6px 6px 0;"><a data-page="${page}" class="followup-leads-pagination" style="color: #0254d7;" href="javascript:void(0)">${page}</a></li>`;
                } else {
                    html += `<li class="active-page" style="border-radius: 0px;"><a data-page="${page}" class="followup-leads-pagination" style="color: #0254d7;" href="javascript:void(0)">${page}</a></li>`;
                }
            } else if (
                page > pagination.number - 5 &&
                page < pagination.number + 5
            ) {
                html += `<li><a class="followup-leads-pagination" href="javascript:void(0)" data-page="${page}">${page}</a></li>`;
            }
        }
    }

    $("#follow-leads-table_wrapper").append(html);

    add_pagination_events();
}

function add_pagination_events() {
    $(".followup-leads-pagination").on("click", (event) => {
        initialize_followup_leads_table(event.target.dataset.page);
    });
}

export function apply_followup_lead_filter() {
    const agent_usernames = $("#select-agent-username-dropdown").val();
    const lead_source = $("#select-source-dropdown").val();
    const lead_category = $("#select-categories-dropdown").val();

    let start_date = document
        .getElementById("followup-filter-start-date")
        .value.trim();

    let end_date = document
        .getElementById("followup-filter-end-date")
        .value.trim();

    start_date = change_date_format_original(start_date);
    end_date = change_date_format_original(end_date);

    if (
        start_date == "" ||
        end_date == "" ||
        !is_valid_date(start_date) ||
        !is_valid_date(end_date)
    ) {
        showToast("Please enter valid dates", 4000);
        return;
    }

    const start_datetime = new Date(start_date);
    const end_datetime = new Date(end_date);
    if (start_datetime > end_datetime) {
        showToast("Start Date should be less than End Date", 4000);
        return;
    }

    state.filter.is_applied = true;
    state.filter.agent_usernames = agent_usernames;
    state.filter.lead_source = lead_source;
    state.filter.lead_category = lead_category;
    state.filter.start_date = start_date;
    state.filter.end_date = end_date;

    set_followup_lead_filter();

    $("#apply-filter-followup-lead").modal("hide");
    state.checked_leads = [];
    state.is_global_lead_checkbox_enabled = false;
    initialize_followup_leads_table(1);
}

function set_followup_lead_filter() {
    localStorage.setItem(`followup_lead_is_applied`, state.filter.is_applied);
    localStorage.setItem(`followup_lead_agent_usernames`, JSON.stringify(state.filter.agent_usernames));
    localStorage.setItem(`followup_lead_source`, JSON.stringify(state.filter.lead_source));
    localStorage.setItem(`followup_lead_category`, JSON.stringify(state.filter.lead_category))
    localStorage.setItem(`followup_lead_start_date`, state.filter.start_date)
    localStorage.setItem(`followup_lead_end_date`, state.filter.end_date)
}

function unset_followup_lead_filter() {
    localStorage.removeItem(`followup_lead_is_applied`);
    localStorage.removeItem(`followup_lead_agent_usernames`);
    localStorage.removeItem(`followup_lead_source`);
    localStorage.removeItem(`followup_lead_category`);
    localStorage.removeItem(`followup_lead_start_date`);
    localStorage.removeItem(`followup_lead_end_date`);
}

async function load_followup_lead_transcripts(element) {

    let id = element.id.split("_")[1];
    state.current_selected_bot = element.getAttribute('data-bot-id');

    $("#chat-transcript-modal").modal("show");

    const response = await get_message_history(id);
    var html = get_chat_html(response, id);

    $("#livechat-chat-messages").html('')
    $("#livechat-chat-messages").append(html);

    state.raise_ticket_form = JSON.parse(response.raise_ticket_form);
    state.session_id = id;
    set_customer_details(response);
}

function set_customer_details(response) {
    state.customer.name = response.customer_name;
    state.customer.email = response.customer_email;
    state.customer.phone = response.customer_phone;
}

function get_message_history(id) {
    return new Promise((resolve, reject) => {
        const json_string = JSON.stringify({
            session_id: id,
        });
        const params = get_params(json_string);
        let config = {
            headers: {
              'X-CSRFToken': getCsrfToken(),
            }
          }
     
        axios
            .post("/livechat/get-livechat-followup-lead-messages/", params, config)
            .then((response) => {
                response = custom_decrypt(response.data);
                response = JSON.parse(response);

                if(response.status == 200) {
                    resolve(response);
                }
            })     
            .catch((err) => {
                console.log(err);
            });
    });
}

function get_chat_html(response, pk) {
    let html = ``;

    html += `<div class="col-12 mb-2 livechat-archive-chat-history-chats-parent-div" id="livechat-history-message-box-container-div" style="margin-bottom: 0px !important;height: calc(100vh - 15rem) !important;"><div class="live-chat-area-admin" id="live-chat-area-admin-section">`;

    html += get_chat_loader(pk);
    html += `<div class="live-chat-day-date-indicator" id="live-chat-indicator-${pk}">Today</div>`;

    html += `<div class="live-chat-message-wrapper-archived" id="style-2_${pk}" data-id="${pk}" style="height: inherit !important;">`;

    html += get_messages_html(response);

    let footer_html = ``;
    let disable_btn_class = '';
    if(response.is_whatsapp_conversation_reinitiated) {
        disable_btn_class = 'disable-reinitiate-conv-btn';
    }

    if(response.is_whatsapp_reinitiation_enabled) {
        footer_html += `<button id="whatsapp-reinitiation-btn-${pk}" class="btn-primary reinitiate-conv-btn click-reinitiate-btn ${disable_btn_class}" onclick="reinitiate_whatsapp_conversation('${pk}')">Reinitiate Conversation </button>`;
    }

    if(response.is_livechat_email_enabled) {
        footer_html += `<button class="btn-primary" onclick="transfer_chat_to_email_conversations('${pk}')" style="opacity: 1; pointer-events: auto; display: inline-block; width: 125px;">Chat over email </button>`;   
    }

    if(response.is_agent_raise_ticket_functionality_enabled) {
        footer_html += `<button id="raise-ticket-btn" class="btn-primary" onclick="load_followup_raise_ticket_form()" data-id="41d494a7-8d65-4549-b39f-ac52f150bdf4" style="opacity: 1; pointer-events: auto; display: inline-block;">Raise a ticket </button>`;
    }

     $("#raise-ticket-btn-container").html(footer_html);

    return html;
}

function get_chat_loader(pk) {
    return `
            <div class="loader-custom" id="chat_loader-${pk}" style="position: absolute; left: 50%; transform: translateX(-50%);">
                <div id="loader-inside-div">
                    <div>
                    </div>
                    <div>
                    </div>
                    <div>
                    </div>
                    <div>
                    </div>
                </div>
            </div>
    `;
}

export function load_followup_raise_ticket_form() {

    $('#raise-ticket-error-message').css('display','none');
    $("#livechat-raise-ticket-form").html("");

    let form = state.raise_ticket_form;

    if(Object.keys(form).length == 0) {
        form = get_default_raise_ticket_form();
        state.raise_ticket_form = form;
    }

    set_form_state(form);

    generate_option_map();

    const field_ids = form.field_order;

    field_ids.forEach((field_id) => {
        const field = form[field_id];

        const html = get_field_html_based_input_type(
            field,
            field_id.split("_")[1]
        );

        $("#livechat-raise-ticket-form").append(html);

        if (field.type == "4") {
            $(
                `#livechat-form-datepicker_${field_id.split("_")[1]}`
            ).datepicker();

            $(`#livechat-form-datepicker_${field_id.split("_")[1]}`).on(
                "change",
                (e) => {
                    change_date(e.target);
                }
            );
        } else if (field.type == "2") {
            $(`.livechat-form-radio-btn_${field_id.split("_")[1]}`).on(
                "change",
                (e) => {
                    update_dependent_inputs(field_id.split("_")[1]);
                }
            );
        } else if (field.type == "6") {
            $(`#input-element_${field_id.split("_")[1]}`).on("change", (e) => {
                update_dependent_inputs(field_id.split("_")[1]);
            });
        } else if (field.type == "3") {
            $(`.livechat-form-checkbox_${field_id.split("_")[1]}`).on(
                "change",
                (e) => {
                    update_dependent_inputs(field_id.split("_")[1]);
                }
            );
        }
    });

    pre_fill_customer_details(form, field_ids);

    $('#livechat-raise-ticket-modal').modal('show');
}

function get_default_raise_ticket_form() {

    let sample_form_data = [{"label_name": "Name", "type": "1", "optional": false, "placeholder": "Enter full name", "dependent": false}, 
    {"label_name": "Email", "type": "1", "optional": false, "placeholder": "Enter email id", "dependent": false}, 
    {"label_name": "Phone No", "type": "1", "optional": false, "placeholder": "Enter phone no", "dependent": false}, 
    {"label_name": "Categories", "type": "6", "optional": false, "dependent": false, "values": window.CATEGORY_DICT[state.current_selected_bot]}, 
    {"label_name": "Query", "type": "5", "optional": false, "placeholder": "Enter query", "dependent": false}, 
    {"label_name": 'Attachment', "type": '7', "optional": true, "dependent": false}];

    let fields = [];
    let form_data = {};
    sample_form_data.forEach(data => {
        let id = generate_random_string(5);
        id = "field_" + id;
        fields.push(id);
        form_data[id] = data;
    });
    form_data["field_order"] = fields;

    return form_data;    
}

function pre_fill_customer_details(form, field_ids) {

    try {
        field_ids.forEach((field_id) => { 

            const field = form[field_id];
            if(field.label_name == "Name") {
                document.getElementById("input-element_"+field_id.split("_")[1]).value = state.customer.name;
            }

            if(field.label_name == "Email") {
                document.getElementById("input-element_"+field_id.split("_")[1]).value = state.customer.email;
            }

            if(field.label_name == "Phone No") {
                document.getElementById("input-element_"+field_id.split("_")[1]).value = state.customer.phone;
            }

        });
    } catch (err) { console.log(err); }
}

export async function livechat_followup_raise_ticket() {

    let form_filled = [];
    form_filled = await get_form_filled_data();
    if (form_filled.length == 0) return;

    let json_string = {
        form_filled: form_filled,
        session_id: state.session_id,
    };

    json_string = JSON.stringify(json_string);
    const params = get_params(json_string);

    let config = {
          headers: {
            'X-CSRFToken': getCsrfToken(),
          }
        }

    axios
        .post("/livechat/livechat-raise-ticket/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);

            if(response.status == 200) {

                $('#raise-ticket-error-message').css('display','none');
                $('#livechat-raise-ticket-modal').modal('hide');
                $('#ticket-id-span').text(response.ticket_id);
                $('#ticket-submit-modal').modal('show');

            } else if (response.status == 500) {

                $('#raise-ticket-error-message').css('display','block');

            }
        })        
        .catch((err) => {
            console.log(err);
        });
}

async function get_form_filled_data() {
    let form_filled = [];
    let form = state.raise_ticket_form;

    const fields = form.field_order;
    let is_form_filled = true;
    for (let field_id of fields) {
        const field = form[field_id];

        let res = {};
        if (field.type == "1" || field.type == "5") {
            res = get_text_data(field, field_id);
        } else if (field.type == "2") {
            res = get_radio_data(field, field_id);
        } else if (field.type == "3") {
            res = get_checkbox_data(field, field_id);
        } else if (field.type == "4") {
            res = get_datepicker_data(field, field_id);
        } else if (field.type == "6") {
            res = get_dropdown_data(field, field_id);
        }  else if (field.type == "7") {
            res = await get_attachment_data(field, field_id);
        }

        if ("is_valid" in res && res.is_valid == false) {
            showToast(res.error, 2000);
            is_form_filled = false;
            return;
        }

        form_filled.push(res);
    }

    if (!is_form_filled) return [];

    return form_filled;
}

function load_lead_transfer_modal() {
    
    let checked_leads = state.checked_leads;

    if(checked_leads.length == 0) return;

    let json_string = {
        checked_leads: checked_leads,
    };

    json_string = JSON.stringify(json_string);
    const params = get_params(json_string);

    let config = {
          headers: {
            'X-CSRFToken': getCsrfToken(),
          }
        }

    axios
        .post("/livechat/get-livechat-followup-lead-agents/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);

            if(response.status == 200) {

                if(response.agent_list.length) {

                    $("#transfer-lead-dropdown-container").css('display', 'block');
                    $("#filter-no-agent-toast").attr("style", "display: none !important");
                    let agent_list_html = get_agent_list_html(response.agent_list);

                    $("#tranfer-lead-select-agent-dropdown").html("");
                    $("#tranfer-lead-select-agent-dropdown").html(agent_list_html);
                    setTimeout(() => {$('#tranfer-lead-select-agent-dropdown').multiselect( 'rebuild' )}, 500);

                    apply_event_listeners_on_agents();

                } else {

                    $("#transfer-lead-dropdown-container").css('display', 'none');
                    $("#filter-no-agent-toast").attr("style", "display: flex !important");  

                }
                $("#transfer-lead-modal").modal("show");
            }
        })        
        .catch((err) => {
            console.log(err);
        });
}

function get_agent_list_html(agent_list) {
    let html = `<option value="">Select Agent</option>`;

    for(let i = 0; i < agent_list.length; i++) {
        html += `<option value="${agent_list[i]}">${agent_list[i]}</option>`;
    }

    return html;
}

function followup_lead_transfer() {
    let selected_agent = $("#tranfer-lead-select-agent-dropdown").val();

    if(!selected_agent) {
        showToast("Please select an agent", 2000);
        return;
    }

   let json_string = {
        checked_leads: state.checked_leads,
        selected_agent: selected_agent
    };

    json_string = JSON.stringify(json_string);
    const params = get_params(json_string);

    let config = {
          headers: {
            'X-CSRFToken': getCsrfToken(),
          }
        }

    axios
        .post("/livechat/transfer-livechat-followup-lead/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);

            if(response.status == 200) {
                $("#transfer-lead-modal").modal("hide");

                $("#lead-transfer-complete-message").text("Lead has been successfully transferred");
                $('#lead-toast-container').css('display', 'flex');
                setTimeout(function() {
                    $('#lead-toast-container').css('display', 'none');
                }, 2000);

                state.checked_leads = [];
                state.is_global_lead_checkbox_enabled = false;
                initialize_followup_leads_table(state.page);
            } else {
                showToast(response.status_message, 2000);
            }
        })        
        .catch((err) => {
            console.log(err);
        });
}

function followup_lead_complete() {

    let checked_leads = state.checked_leads;

    if(checked_leads.length == 0) return;

   let json_string = {
        checked_leads: state.checked_leads,
    };

    json_string = JSON.stringify(json_string);
    const params = get_params(json_string);

    let config = {
          headers: {
            'X-CSRFToken': getCsrfToken(),
          }
        }

    axios
        .post("/livechat/complete-livechat-followup-lead/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);

            if(response.status == 200) {

                $("#lead-transfer-complete-message").text("Lead has been successfully marked as complete");
                $('#lead-toast-container').css('display', 'flex');
                setTimeout(function() {
                    $('#lead-toast-container').css('display', 'none');
                }, 2000);

                state.checked_leads = [];
                state.is_global_lead_checkbox_enabled = false;
                initialize_followup_leads_table(state.page);
            } else {
                showToast(response.status_message, 2000);
            }
        })        
        .catch((err) => {
            console.log(err);
        });
}

export function transfer_chat_to_email_conversations(session_id) {

   let json_string = {
        session_id: session_id,
    };

    json_string = JSON.stringify(json_string);
    const params = get_params(json_string);

    let config = {
          headers: {
            'X-CSRFToken': getCsrfToken(),
          }
        }

    axios
        .post("/livechat/transfer-followup-lead-to-email-conversations/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);

            if(response.status == 200) {
                $("#chat-transcript-modal").modal("hide");
                state.checked_leads = [];
                state.is_global_lead_checkbox_enabled = false;
                initialize_followup_leads_table(state.page);
                showToast("Lead transferred to email conversation!", 2000);
            } else {
                showToast(response.status_message, 2000);
            }
        })        
        .catch((err) => {
            console.log(err);
        });
}

export function reinitiate_whatsapp_conversation(session_id) {

   let json_string = {
        session_id: session_id,
    };

    json_string = JSON.stringify(json_string);
    const params = get_params(json_string);

    let config = {
          headers: {
            'X-CSRFToken': getCsrfToken(),
          }
        }

    axios
        .post("/livechat/reinitiate-whatsapp-conversation/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);

            if(response.status == 200) {
                $(`#whatsapp-reinitiation-btn-${session_id}`).addClass("disable-reinitiate-conv-btn");
                let text = 'Reinitiating Request Sent';
                let message_id = save_system_message(text, 'WHATSAPP_REINITIATING_REQUEST', session_id);
                let message_html = `<div class="live-chat-customer-details-update-message-div">${text}</div>`;
                append_system_text_response(text, '', session_id, message_id);
                scroll_to_bottom(session_id);
            } else {
                showToast(response.status_message, 2000);
            }
        })        
        .catch((err) => {
            console.log(err);
        });
}

function scroll_to_bottom(session_id) {
    const elem = document.getElementById(`style-2_${session_id}`);
    if (elem) {
        $(elem).scrollTop($(elem)[0].scrollHeight);
    }
}
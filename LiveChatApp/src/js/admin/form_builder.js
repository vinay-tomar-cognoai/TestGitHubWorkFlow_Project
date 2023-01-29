import { 
    custom_decrypt, 
    generate_random_string, 
    get_params, 
    get_url_vars, 
    is_mobile, 
    showToast, 
    stripHTML, 
    strip_unwanted_characters,
    is_file_supported,
    check_malicious_file,
    check_file_size,
    getCsrfToken,
    stripHTMLtags 
} from "../utils";

import axios from 'axios';
import { sync_preview } from "./form_preview";
import { get_character_limit } from "../common";
import { get_theme_color, set_theme_color } from "../agent/console";

const state = {
    form: {},
    form_changes: {},
    dependent_types: ['2', '3', '6'],
    option_map: {},
    options_global: [],
    attachment: {
        data: "",
        form_data: "",
        file_src: '',
        file_name: '',
        channel_file_url: '',
    },
}

export function initialize_form_builder() {
    state.form = window.FORM;
    set_theme_color(window.LIVECHAT_THEME_COLOR, window.LIVECHAT_THEME_COLOR_LIGHT, window.LIVECHAT_THEME_COLOR_LIGHT_ONE);
    set_form();
    
    const is_form_enabled = document.getElementById('livechat-chat-dispose-page-toggle-cb').checked;
    if (is_form_enabled) {
        setTimeout(() => {
            sync_preview();
        }, 400)
    }
}

export function initialize_raise_ticket_form_builder() {

    if(Object.keys(window.FORM).length == 0) {
        state.form = get_default_raise_ticket_form();  
    } else {
        state.form = window.FORM;
    }

    set_theme_color(window.LIVECHAT_THEME_COLOR, window.LIVECHAT_THEME_COLOR_LIGHT, window.LIVECHAT_THEME_COLOR_LIGHT_ONE);
    set_form();
    
    setTimeout(() => {
        sync_preview();
    }, 400)
}

export function get_default_raise_ticket_form() {

    let sample_form_data = [{"label_name": "Name", "type": "1", "optional": false, "placeholder": "Enter full name", "dependent": false}, 
    {"label_name": "Email", "type": "9", "optional": false, "placeholder": "Enter email id", "dependent": false}, 
    {"label_name": "Phone No", "type": "8", "optional": false, "placeholder": "Enter phone no", "dependent": false}, 
    {"label_name": "Categories", "type": "6", "optional": false, "dependent": false, "values": window.CATEGORY_LIST}, 
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

function set_form() {
    let html = '', id;
    if (Object.keys(state.form).length == 0) {
        id = generate_random_string(5);
        html = get_default_field(id);

        $('#livechat-form-fields').html(html);

        setTimeout(() => {
            add_remove_form_field_event(id);
            add_input_type_change_event(id);
            add_independent_field_change_event(id);
        }, 300)

    } else {
        const field_ids = state.form.field_order;

        field_ids.forEach(field_id => {
            const field = state.form[field_id];

            add_section(field_id.split('_')[1]);

            const label_el = document.querySelector(`#${field_id} .form-field-label-name`);
            label_el.value = field.label_name;

            setTimeout(() => {
                const input_type_el = document.getElementById(`input-type-dropdown_${field_id.split('_')[1]}`);
                input_type_el.value = field.type;

                state.form_changes[field_id] = {}
                if (field.type == '1' || field.type == '5' || field.type == '8' || field.type == '9') {
                    state.form_changes[field_id][field.type] = field.placeholder;
                } else if (field.type == '4') {
                    state.form_changes[field_id][field.type] = field.date_format;
                }
                else if (state.dependent_types.includes(field.type)) {
                    state.form_changes[field_id][field.type] = {}
                    state.form_changes[field_id][field.type].all_options = []

                    if (field.dependent == false) {
                        state.form_changes[field_id][field.type]['0'] = field.values;
                        state.form_changes[field_id][field.type].all_options.push(...field.values)
                        state.options_global = [...state.options_global, ...field.values];
                    } else {                        
                        let last_key = '';
                        for (const key in field) {
                            if (key == '0') continue;
                            
                            if (Array.isArray(field[key]) && key != 'dependent_ids' && key != 'dependent_on_ids' && key != 'all_options') {
                                last_key = key;

                                state.form_changes[field_id][field.type][key] = field[key];
                                state.form_changes[field_id][field.type].all_options.push(...field[key])
                                state.options_global = [...state.options_global, ...field[key]];
                            }
                        }

                        setTimeout(() => {
                            const elem = document.getElementById(`livechat-dependent-value-dropdown_${field_id.split('_')[1]}`);

                            $(elem).val(last_key);
                            $(elem).selectpicker('refresh');
                            $(elem).trigger('change')
                        }, 100)
                    }
                }

                const optional_el = document.querySelector(`#${field_id} .livechat-form-field-optional-checkbox`);
                optional_el.checked = field.optional;
                
                $(input_type_el).trigger('change');

            }, 400)
        })
    }
}

function get_default_field(id) {
    const char_limit = get_character_limit();
    let attachment_option_html = "";

    if(window.location.href.includes('raise-ticket-form-builder')) {
        attachment_option_html = '<option value="7">Attachment</option>';
    }

    let html = `
    <div class="livechat-create-form-field" id="field_${id}">
        <div class="livechat-create-form-div-remove">
            <svg class="remove-form-field" id="remove-field_${id}" width="11" height="10" viewBox="0 0 11 10" fill="none" xmlns="http://www.w3.org/2000/svg">   
                <path d="M11 1.23576L9.64067 0L5.5 3.76424L1.35933 0L0 1.23576L4.14067 5L0 8.76424L1.35933 10L5.5 6.23576L9.64067 10L11 8.76424L6.85933 5L11 1.23576Z" fill="#757575"></path> </svg></div>
        <div class="mb-3">
            <label>Label Name <b>*</b></label>
            <input maxlength="${char_limit.medium}" class="form-control form-field-label-name" type="text" placeholder="Eg: Account details">
        </div>
        <div class="mb-3">
            <label>Input type <b>*</b></label>
            <select class="form-control select-dropdown-icon" id="input-type-dropdown_${id}">
                    <option value="1" selected>Text Field</option>
                    <option value="2">Radio Button</option>
                    <option value="3">Checkbox</option>
                    <option value="4">Single date</option>
                    <option value="5">Comment Section</option>
                    <option value="6">Dropdown</option>
                    ${attachment_option_html}
                    <option value="8">Phone Number</option>
                    <option value="9">Email Address</option>
            </select>
        </div>
        <div class="input-type-section">
            <div class="mb-3">
                <input maxlength="${char_limit.medium}" id="text-field-placeholder_${id}" class="form-control text-field-placeholder-text" type="text" placeholder="Placeholder Text">
            </div>
        </div>
        <div class="livechat-dispose-form-field-footer">
            <div class="livechat-dispose-form-optional-btn" style="font-weight: 300; font-size: 14px"><span>Optional</span>
                <label class="livechat-option-switch">
                    <input type="checkbox" class="livechat-form-field-optional-checkbox">
                    <span class="livechat-option-switch-slider round"></span>
                </label>
            </div>

        </div>
    </div>
    `

    return html;
}

export function add_section(id) {
    if (!id) {
        id = generate_random_string(5);
    }

    const html = get_default_field(id);

    $('#livechat-form-fields').append(html);

    scroll_form_to_bottom();

    setTimeout(() => {
        add_remove_form_field_event(id);
        add_input_type_change_event(id);
        add_independent_field_change_event(id);
    }, 300)
}

function scroll_form_to_bottom() {
    var objDiv = document.getElementById("livechat-form-fields");
    objDiv.scrollTop = objDiv.scrollHeight;
}

function add_input_type_change_event(id) {
    const elem = document.getElementById(`input-type-dropdown_${id}`);

    $(elem).on("change", (e) => {
        add_input_type_section(id, e.target.value);

        if (state.dependent_types.includes(e.target.value)) {
            update_options(document.getElementById(`livechat-dependent-value-dropdown_${id}`), e.target.value);
        } else {
            update_independent_fields(id, e.target.value);
        }
    });
}

function add_remove_form_field_event(id) {
    const elem = document.getElementById(`remove-field_${id}`);

    if (is_mobile()) {
        $(elem).on("touchend", () => {
            remove_form_field(id);
        });
    } else {
        $(elem).on("click", () => {
            remove_form_field(id);
        });
    }
}

function add_independent_field_change_event(id) {
    let elem = document.getElementById(`text-field-placeholder_${id}`);
    $(elem).on("keyup", (e) => {
        if (!state.form_changes[`field_${id}`]) {
            state.form_changes[`field_${id}`] = {};
        }

        state.form_changes[`field_${id}`]['1'] = e.target.value;
    });

    elem = document.getElementById(`comment-field-placeholder_${id}`);
    $(elem).on("keyup", (e) => {
        if (!state.form_changes[`field_${id}`]) {
            state.form_changes[`field_${id}`] = {};
        }

        state.form_changes[`field_${id}`]['5'] = e.target.value;
    });

    elem = document.getElementById(`date-field-select_${id}`);
    $(elem).on("change", (e) => {
        if (!state.form_changes[`field_${id}`]) {
            state.form_changes[`field_${id}`] = {};
        }

        state.form_changes[`field_${id}`]['4'] = e.target.value;
    });

    elem = document.getElementById(`mobile-field-placeholder_${id}`);
    $(elem).on("keyup", (e) => {
        if (!state.form_changes[`field_${id}`]) {
            state.form_changes[`field_${id}`] = {};
        }

        state.form_changes[`field_${id}`]['8'] = e.target.value;
    });

    elem = document.getElementById(`email-field-placeholder_${id}`);
    $(elem).on("keyup", (e) => {
        if (!state.form_changes[`field_${id}`]) {
            state.form_changes[`field_${id}`] = {};
        }

        state.form_changes[`field_${id}`]['9'] = e.target.value;
    });
}

function remove_form_field(id) {
    const elem = document.getElementById(`field_${id}`);

    const data = get_built_form_info(false);
    const form = data.form;
    const field = form[`field_${id}`];

    if (field.dependent_ids && field.dependent_ids.length > 0) {
        showToast('Cannot remove this field because some fields depend on it.', 2000);
        return;
    }

    if (elem) {
        if (field.type && state.dependent_types.includes(field.type)) {
            let all_options;
            if (field.dependent == false) {
                all_options = field.values;
            } else {
                all_options = field.all_options;
            }
            
            if (all_options) {
                for (const option of all_options) {
                    let index = state.options_global.indexOf(option);
    
                    if (index > -1) {
                        state.options_global.splice(index, 1);
                        if (state.option_map[option]) {
                            state.option_map[option] = undefined;
                        }
                    }
    
                    state.form_changes[`field_${id}`] = undefined;
                }
            }
        }

        elem.remove();
    }
}

function add_input_type_section(id, value) {
    const section = document.querySelector(`#field_${id} .input-type-section`);
    const char_limit = get_character_limit();

    let html = ''
    if (value == '1') {
        html = get_text_field_section(id, char_limit);
    }
    else if (value == '2') {
        html = get_radio_button_section(id, char_limit);
    }
    else if (value == '3') {
        html = get_checkbox_section(id, char_limit);
    }
    else if (value == '4') {
        html = get_single_date_section(id, char_limit);
    }
    else if (value == '5') {
        html = get_comment_section(id, char_limit);
    }
    else if (value == '6') {
        html = get_dropdown_section(id, char_limit);
    }
    else if (value == '7') {
        html = get_attachment_section(id, char_limit);
    }
    else if (value == '8') {
        html = get_mobile_field_section(id, char_limit);
    }
    else if (value == '9') {
        html = get_email_field_section(id, char_limit);
    }

    section.innerHTML = html;

    const elem = document.getElementById(`livechat-dependent-value-dropdown_${id}`);
    if (elem) {
        $(elem).selectpicker()
        $(elem).on('change', function (e) {
            update_options(e.target, value);
        })
    }

    add_dropdown_keypress_event(id);
    add_checkbox_keypress_event(id);
    add_radio_keypress_event(id);
    add_independent_field_change_event(id);

    update_dependent_dropdowns();

    $('.livechat-dispose-form-sortable-div').sortable({
        containment: "parent",
        update: function(event, ui) {
            change_choice_order(event)
        },
    });
}

function change_choice_order(event) {
    const elem_id = event.target.id;
    const elems = document.querySelectorAll(`#${elem_id} input`);
    let options = [];
    elems.forEach(elem => {
        options.push(elem.value);
    })

    const id = elem_id.split('_')[1];
    const input_type = document.getElementById(`input-type-dropdown_${id}`).value;
    const dependent_on = document.getElementById(`livechat-dependent-value-dropdown_${id}`).value;

    state.form_changes[`field_${id}`][input_type][dependent_on] = options;
}

function get_text_field_section(id, char_limit) {
    const html = `
    <div class="mb-3">
        <input maxlength="${char_limit.medium}" id="text-field-placeholder_${id}" class="form-control text-field-placeholder-text" type="text" placeholder="Placeholder Text">
    </div>
    `

    return html;
}

function get_mobile_field_section(id, char_limit) {
    const html = `
    <div class="mb-3">
        <input maxlength="${char_limit.medium}" id="mobile-field-placeholder_${id}" class="form-control text-field-placeholder-text" type="text" placeholder="Placeholder Text">
    </div>
    `

    return html;
}

function get_email_field_section(id, char_limit) {
    const html = `
    <div class="mb-3">
        <input maxlength="${char_limit.medium}" id="email-field-placeholder_${id}" class="form-control text-field-placeholder-text" type="text" placeholder="Placeholder Text">
    </div>
    `

    return html;
}

function get_radio_button_section(id, char_limit) {
    const html = `
    <div class="mb-3">
        <label>Dependent on value <b>*</b></label>
        <select data-size='4' id="livechat-dependent-value-dropdown_${id}" class="form-control select-dropdown-icon selectpicker livechat-depend-on-value-dropdown" data-live-search="true"> 
                <option value="0">None</option>       
        </select>
    </div>
    <div class="livechat-dispose-radio-chip-area livechat-dispose-form-sortable-div" id="input-chip-section_${id}">

    </div>
    <div class="mb-3">
        <input maxlength="${char_limit.medium}" id="radio-input-field_${id}" class="form-control " type="text" placeholder='Enter any value or text and hit " Enter " '>
    </div>
    `

    return html;
}

function get_checkbox_section(id, char_limit) {
    const html = `
    <div class="mb-3">
        <label>Dependent on value <b>*</b></label>
        <select data-size='4' id="livechat-dependent-value-dropdown_${id}" class="form-control select-dropdown-icon selectpicker livechat-depend-on-value-dropdown" data-live-search="true">
                <option value="0">None</option>
        </select>
    </div>
    <div class="livechat-dispose-checkbox-chip-area livechat-dispose-form-sortable-div" id="input-chip-section_${id}">
        
    </div>
    <div class="mb-3">
        <input maxlength="${char_limit.medium}" class="form-control" id="checkbox-input-field_${id}" type="text" placeholder='Enter any value or text and hit " Enter " '>
    </div>
    `

    return html;
}

function get_single_date_section(id) {
    const html = `
    <div class="mb-3">
        <label>Date Format <b>*</b><a data-toggle="tooltip" data-placement="top" title='The selected date format will be saved after the agent hits "Submit" button in the chat dispose form'>
            <svg width="20" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path fill-rule="evenodd" clip-rule="evenodd" d="M21.6001 12.0001C21.6001 14.5462 20.5887 16.988 18.7884 18.7883C16.988 20.5887 14.5462 21.6001 12.0001 21.6001C9.45407 21.6001 7.01227 20.5887 5.21192 18.7883C3.41157 16.988 2.40015 14.5462 2.40015 12.0001C2.40015 9.45401 3.41157 7.01221 5.21192 5.21186C7.01227 3.41151 9.45407 2.40009 12.0001 2.40009C14.5462 2.40009 16.988 3.41151 18.7884 5.21186C20.5887 7.01221 21.6001 9.45401 21.6001 12.0001ZM12.0001 8.40008C11.7893 8.39988 11.5821 8.45523 11.3995 8.56056C11.2168 8.66589 11.0652 8.81749 10.9597 9.00008C10.8836 9.14154 10.7799 9.26627 10.6547 9.36688C10.5294 9.46749 10.3853 9.54194 10.2308 9.58581C10.0762 9.62968 9.91448 9.64208 9.75507 9.62227C9.59567 9.60246 9.44186 9.55085 9.30277 9.4705C9.16368 9.39015 9.04213 9.28268 8.94534 9.15449C8.84856 9.02629 8.77849 8.87996 8.7393 8.72418C8.70011 8.56841 8.6926 8.40634 8.7172 8.24761C8.74181 8.08887 8.79804 7.93669 8.88255 7.80009C9.27881 7.11382 9.89044 6.57748 10.6226 6.27424C11.3547 5.971 12.1665 5.91781 12.9319 6.12291C13.6974 6.32802 14.3737 6.77996 14.8562 7.40864C15.3386 8.03733 15.6001 8.80763 15.6001 9.60009C15.6004 10.3448 15.3697 11.0713 14.9399 11.6795C14.51 12.2877 13.9022 12.7477 13.2001 12.9961V13.2001C13.2001 13.5183 13.0737 13.8236 12.8487 14.0486C12.6236 14.2737 12.3184 14.4001 12.0001 14.4001C11.6819 14.4001 11.3767 14.2737 11.1516 14.0486C10.9266 13.8236 10.8001 13.5183 10.8001 13.2001V12.0001C10.8001 11.6818 10.9266 11.3766 11.1516 11.1516C11.3767 10.9265 11.6819 10.8001 12.0001 10.8001C12.3184 10.8001 12.6236 10.6737 12.8487 10.4486C13.0737 10.2236 13.2001 9.91834 13.2001 9.60009C13.2001 9.28183 13.0737 8.9766 12.8487 8.75156C12.6236 8.52651 12.3184 8.40008 12.0001 8.40008ZM12.0001 18.0001C12.3184 18.0001 12.6236 17.8737 12.8487 17.6486C13.0737 17.4236 13.2001 17.1183 13.2001 16.8001C13.2001 16.4818 13.0737 16.1766 12.8487 15.9516C12.6236 15.7265 12.3184 15.6001 12.0001 15.6001C11.6819 15.6001 11.3767 15.7265 11.1516 15.9516C10.9266 16.1766 10.8001 16.4818 10.8001 16.8001C10.8001 17.1183 10.9266 17.4236 11.1516 17.6486C11.3767 17.8737 11.6819 18.0001 12.0001 18.0001Z" fill="#3C4852"/>
                </svg>
                
        </a></label>
        <select class="form-control select-dropdown-icon" id="date-field-select_${id}">
            
                <option>Choose One</option>
                <option value="%d-%m-%y">DD-MM-YY</option>
            
                <option value="%m-%d-%y">MM-DD-YY</option>
                

                <option value="%y-%d-%m">YY-DD-MM</option>

                <option value="%y-%m-%d">YY-MM-DD</option>
        </select>
    </div>
    `

    return html;
}

function get_comment_section(id, char_limit) {
    const html = `
    <div class="mb-3">
        <input maxlength="${char_limit.medium}" id="comment-field-placeholder_${id}" class="form-control " type="text" placeholder="Placeholder Text">
    </div>
    `

    return html;
}

function get_dropdown_section(id, char_limit) {
    const html = `
    <div class="mb-3 ">
        <label>Dependent on value <b>*</b></label>
        <select data-size='4' class="form-control  selectpicker livechat-depend-on-value-dropdown" id="livechat-dependent-value-dropdown_${id}" data-live-search="true">
                <option value="0">None</option>
        </select>
    </div>
    <div class="livechat-dispose-dropdown-chip-area livechat-dispose-form-sortable-div" id="input-chip-section_${id}">

    </div>
    <div class="mb-3">
        <input maxlength="${char_limit.medium}" class="form-control" type="text" id="dropdown-input-field_${id}" placeholder='Enter any value or text and hit " Enter " '>
    </div>
    `

    return html;
}

function get_attachment_section(id, char_limit) {
    const html = `<div id="upload-file-section_${id}">
                    <div id="file-selected-container_${id}">
                  </div>
                  <div class="drag-drop-container" style="text-align: center;background: #eff6ff;border: 0.7px dashed #93C5FD;border-radius: 3px;padding: 20px;height: 70px;position: relative;">
                    <span class="drag-drop-message" style="color: rgb(15, 82, 161); flex-direction: column; display: flex;align-items: center;justify-content: center; margin-top: 5px;">    
                        <p style="width:90%;margin-bottom: 0;color: #A8A8A8;font-size: 12px;font-weight: 500;">
                            Drag and drop or 
                            <a style="color: #2754F3;">browse</a>
                        </p>
                    </span>
                    <div class="drag-drop-input-field-wrapper">
                        <input onchange="handle_image_upload_input_change('${id}')" id="drag-drop-input-box_${id}" style="border-bottom: none !important;border: 1px solid black;height: 100% !important;opacity: 0;cursor: pointer; width: 100%;" type="file" accept=".jpg,.png,.svg,.pdf">
                    </div>
                    </div>
                  </div>`;

    return html;
}

function add_dropdown_keypress_event(id) {
    const elem = document.getElementById(`dropdown-input-field_${id}`);

    if (elem) {
        $(elem).on('keypress', (e) => {
            if (e.key == 'Enter') {
                add_dropdown_chip(id, e.target.value, true);
            }
        })
    }
}

function add_checkbox_keypress_event(id) {
    const elem = document.getElementById(`checkbox-input-field_${id}`);

    if (elem) {
        $(elem).on('keypress', (e) => {
            if (e.key == 'Enter') {
                add_checkbox_chip(id, e.target.value, true);
            }
        })
    }
}

function add_radio_keypress_event(id) {
    const elem = document.getElementById(`radio-input-field_${id}`);

    if (elem) {
        $(elem).on('keypress', (e) => {
            if (e.key == 'Enter') {
                add_radio_chip(id, e.target.value, true);
            }
        })
    }
}

function validate_option_value(id, value, input_type, old_value) {

    if (value == "") {
        showToast('Choice Cannot be empty', 2000);
        return false;
    }

    const field_id = `field_${id}`;

    if (!state.form_changes[field_id]) {
        state.form_changes[field_id] = {}
    }

    if (!state.form_changes[field_id][input_type]) {
        state.form_changes[field_id][input_type] = {}
    }

    const dependent_on = document.getElementById(`livechat-dependent-value-dropdown_${id}`).value;

    if (!state.form_changes[field_id][input_type][dependent_on]) {
        state.form_changes[field_id][input_type][dependent_on] = [];
    }

    if (state.form_changes[field_id][input_type][dependent_on].join('|').toLowerCase().split('|').includes(value.toLowerCase())) {
        showToast('Choices must be different.', 2000);
        return false;
    }

    if (state.options_global.join('|').toLowerCase().split('|').includes(value.toLowerCase())) {
        showToast('Similar choice exists in one of the form fields.', 2000);
        return false;
    }

    state.form_changes[field_id][input_type][dependent_on].push(value);

    if (!state.form_changes[field_id][input_type].all_options) {
        state.form_changes[field_id][input_type].all_options = []
    }

    state.form_changes[field_id][input_type].all_options.push(value);
    state.options_global.push(value);

    if (old_value) {
        const index1 = state.form_changes[field_id][input_type].all_options.indexOf(old_value);
        if (index1 > -1) state.form_changes[field_id][input_type].all_options.splice(index1, 1);
        
        const index2 = state.options_global.indexOf(old_value);
        if (index2 > -1) state.options_global.splice(index2, 1);

        const index3 = state.form_changes[field_id][input_type][dependent_on].indexOf(old_value);
        if (index3 > -1) state.form_changes[field_id][input_type][dependent_on].splice(index3, 1);
    }

    return true;
}

function add_dropdown_chip(id, value, is_validation_required) {
    value = value.trim();
    value = stripHTML(value);
    value = strip_unwanted_characters(value);

    if (!is_validation_required || validate_option_value(id, value, '6')) {
        const dependent_on = document.getElementById(`livechat-dependent-value-dropdown_${id}`).value;

        const elem = document.querySelector(`#field_${id} .livechat-dispose-dropdown-chip-area`);

        const chip_id = generate_random_string(5);

        const html = get_dropdown_chip_html(value, id + chip_id);
        $(elem).append(html);

        $(`#dropdown-chip-delete_${id}${chip_id}`).on('click', () => {
            remove_dropdown_chip(id + chip_id, dependent_on);
        })

        $(`#option-value_${id}${chip_id}`).on('focusout', () => {
            change_option(id + chip_id, '6');
        })

        add_chip_input_event(`option-value_${id}${chip_id}`)
        add_chip_focus_event($(`#option-value_${id}${chip_id}`))
        add_chip_focusout_event($(`#option-value_${id}${chip_id}`))

        document.getElementById(`dropdown-input-field_${id}`).value = '';
        update_dependent_dropdowns();
    }
}

function add_chip_input_event(id) {
    $.fn.text_width = function(text, font) {

        if (!$.fn.text_width.fakeEl) $.fn.text_width.fakeEl = $('<span>').hide().appendTo(document.body);

        $.fn.text_width.fakeEl.text(text || this.val() || this.text() || this.attr('placeholder')).css('font', font || this.css('font'));

        return $.fn.text_width.fakeEl.width();
    };

    $(`#${id}`).on('input', function() {
        const input_width = $(this).text_width();
        
        $(this).attr('style', `width: ${input_width * 1.2}px !important`);

    }).trigger('input');


    function input_width(elem, minW, maxW) {
        elem = $(this);

    }

    var target_elem = $(`#${id}`);

    input_width(target_elem);
}

function add_chip_focus_event(elem) {
    $(elem).on('focus', () => {
        const theme_color = get_theme_color();

        $(elem).parent().css("background", "#ffffff");
        $(elem).parent().css('border', `1px solid ${theme_color.one}`);
        $(elem).css('color', '#000');
        $(elem).parent().children('.widget-delete-icon').css("display", "none");
    })
}

function add_chip_focusout_event(elem) {
    $(elem).on('focusout', () => {
        const theme_color = get_theme_color();

        $(elem).parent().css("background", `${theme_color.one}`);
        $(elem).parent().css('border', `none`);
        $(elem).css('color', '#fff');
        $(elem).parent().children('.widget-delete-icon').css("display", "block");
    })
}


function get_dropdown_chip_html(value, id) {
    const char_limit = get_character_limit();

    const html = `
    <div id="dropdown-chip_${id}" class="form-widget-dropdown-chip-item " style="border: none;">
        <div class="dragable-item-icon tooltip-custom">
            <svg width="14" height="15" viewBox="0 0 14 15" fill="#d9d9d9" xmlns="http://www.w3.org/2000/svg">
                <path fill-rule="evenodd" clip-rule="evenodd" d="M9.91683 4.00016C9.91683 4.64183 9.39183 5.16683 8.75016 5.16683C8.1085 5.16683 7.5835 4.64183 7.5835 4.00016C7.5835 3.3585 8.1085 2.8335 8.75016 2.8335C9.39183 2.8335 9.91683 3.3585 9.91683 4.00016ZM5.2502 2.8335C4.60854 2.8335 4.08354 3.3585 4.08354 4.00017C4.08354 4.64183 4.60854 5.16683 5.2502 5.16683C5.89187 5.16683 6.41687 4.64183 6.41687 4.00017C6.41687 3.3585 5.89187 2.8335 5.2502 2.8335ZM4.0835 7.50016C4.0835 6.8585 4.6085 6.3335 5.25016 6.3335C5.89183 6.3335 6.41683 6.8585 6.41683 7.50016C6.41683 8.14183 5.89183 8.66683 5.25016 8.66683C4.6085 8.66683 4.0835 8.14183 4.0835 7.50016ZM5.25016 12.1668C5.89183 12.1668 6.41683 11.6418 6.41683 11.0002C6.41683 10.3585 5.89183 9.8335 5.25016 9.8335C4.6085 9.8335 4.0835 10.3585 4.0835 11.0002C4.0835 11.6418 4.6085 12.1668 5.25016 12.1668ZM8.75016 6.3335C8.1085 6.3335 7.5835 6.8585 7.5835 7.50016C7.5835 8.14183 8.1085 8.66683 8.75016 8.66683C9.39183 8.66683 9.91683 8.14183 9.91683 7.50016C9.91683 6.8585 9.39183 6.3335 8.75016 6.3335ZM7.5835 11.0002C7.5835 10.3585 8.1085 9.8335 8.75016 9.8335C9.39183 9.8335 9.91683 10.3585 9.91683 11.0002C9.91683 11.6418 9.39183 12.1668 8.75016 12.1668C8.1085 12.1668 7.5835 11.6418 7.5835 11.0002Z"></path>
            </svg>
            <div class="tooltiptext-custom tooltip-bottom-custom tooltip-dropdown">Drag to move</div>
        </div>
        <input maxlength="${char_limit.medium}" type="text" class="edit-form-widget-dropdown-choices" id="option-value_${id}" value="${value}" data-value="${value}">
        <div class="widget-delete-icon" style="display: block;">
            <svg id="dropdown-chip-delete_${id}" width="12" height="13" viewBox="0 0 12 13" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9.15035 3.35486C9.05694 3.26123 8.93011 3.20861 8.79785 3.20861C8.66559 3.20861 8.53877 3.26123 8.44535 3.35486L6.00035 5.79486L3.55535 3.34986C3.46194 3.25623 3.33511 3.20361 3.20285 3.20361C3.07059 3.20361 2.94377 3.25623 2.85035 3.34986C2.65535 3.54486 2.65535 3.85986 2.85035 4.05486L5.29535 6.49986L2.85035 8.94486C2.65535 9.13986 2.65535 9.45486 2.85035 9.64986C3.04535 9.84486 3.36035 9.84486 3.55535 9.64986L6.00035 7.20486L8.44535 9.64986C8.64035 9.84486 8.95535 9.84486 9.15035 9.64986C9.34535 9.45486 9.34535 9.13986 9.15035 8.94486L6.70535 6.49986L9.15035 4.05486C9.34035 3.86486 9.34035 3.54486 9.15035 3.35486Z" fill="white"></path>
            </svg>
        </div>
    </div>
    `

    return html;
}

function remove_dropdown_chip(id, dependent_on) {
    const elem = document.getElementById(`dropdown-chip_${id}`);

    if (elem) {
        const value = document.getElementById(`option-value_${id}`).value;
        const index = state.form_changes[`field_${id.substring(0, 5)}`]['6'][dependent_on].indexOf(value);

        if (index != -1) {
            state.form_changes[`field_${id.substring(0, 5)}`]['6'][dependent_on].splice(index, 1);

            const index2 = state.options_global.indexOf(value);
            if (index2 != -1) {
                state.options_global.splice(index2, 1)
            }

            const index3 = state.form_changes[`field_${id.substring(0, 5)}`]['6'].all_options.indexOf(value);
            if (index3 != -1) {
                state.form_changes[`field_${id.substring(0, 5)}`]['6'].all_options.splice(index3, 1)
            }

            if (state.option_map[value]) {
                state.option_map[value] = undefined;
            }
        }

        elem.remove();
        update_dependent_dropdowns();
    }
}

function add_checkbox_chip(id, value, is_validation_required) {
    value = value.trim();
    value = stripHTML(value);
    value = strip_unwanted_characters(value);

    if (!is_validation_required || validate_option_value(id, value, '3')) {
        const dependent_on = document.getElementById(`livechat-dependent-value-dropdown_${id}`).value;

        const elem = document.querySelector(`#field_${id} .livechat-dispose-checkbox-chip-area`);

        const chip_id = generate_random_string(5);

        const html = get_checkbox_option_html(value, id + chip_id);
        $(elem).append(html);

        $(`#remove-checkbox-option_${id}${chip_id}`).on('click', () => {
            remove_checkbox_option(id + chip_id, dependent_on);
        })

        $(`#option-value_${id}${chip_id}`).on('focusout', () => {
            change_option(id + chip_id, '3');
        })

        add_option_focus_event($(`#option-value_${id}${chip_id}`));
        add_option_focusout_event($(`#option-value_${id}${chip_id}`));

        document.getElementById(`checkbox-input-field_${id}`).value = '';
        update_dependent_dropdowns();
    }
}

function get_checkbox_option_html(value, id) {
    const char_limit = get_character_limit();

    const html = `
    <div id="checkbox-option_${id}" class="response-widget-dragable-output-item ">
        <div class="dragable-item-icon tooltip-custom">
            <svg width="24" height="25" viewBox="0 0 24 25" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path fill-rule="evenodd" clip-rule="evenodd" d="M16.9998 6.5C16.9998 7.6 16.0998 8.5 14.9998 8.5C13.8998 8.5 12.9998 7.6 12.9998 6.5C12.9998 5.4 13.8998 4.5 14.9998 4.5C16.0998 4.5 16.9998 5.4 16.9998 6.5ZM8.9998 4.5C7.8998 4.5 6.9998 5.4 6.9998 6.5C6.9998 7.6 7.8998 8.5 8.9998 8.5C10.0998 8.5 10.9998 7.6 10.9998 6.5C10.9998 5.4 10.0998 4.5 8.9998 4.5ZM6.99976 12.5C6.99976 11.4 7.89976 10.5 8.99976 10.5C10.0998 10.5 10.9998 11.4 10.9998 12.5C10.9998 13.6 10.0998 14.5 8.99976 14.5C7.89976 14.5 6.99976 13.6 6.99976 12.5ZM8.99976 20.5C10.0998 20.5 10.9998 19.6 10.9998 18.5C10.9998 17.4 10.0998 16.5 8.99976 16.5C7.89976 16.5 6.99976 17.4 6.99976 18.5C6.99976 19.6 7.89976 20.5 8.99976 20.5ZM14.9998 10.5C13.8998 10.5 12.9998 11.4 12.9998 12.5C12.9998 13.6 13.8998 14.5 14.9998 14.5C16.0998 14.5 16.9998 13.6 16.9998 12.5C16.9998 11.4 16.0998 10.5 14.9998 10.5ZM12.9998 18.5C12.9998 17.4 13.8998 16.5 14.9998 16.5C16.0998 16.5 16.9998 17.4 16.9998 18.5C16.9998 19.6 16.0998 20.5 14.9998 20.5C13.8998 20.5 12.9998 19.6 12.9998 18.5Z" fill="#DADADA"></path>
            </svg>
            <div class="tooltiptext-custom tooltip-bottom-custom tooltip-radio">Drag to move</div>
        </div>
        <div class="widget-indigator-icon">
            <svg width="19" height="19" viewBox="0 0 19 19" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path fill-rule="evenodd" clip-rule="evenodd" d="M4.25 2.75H14.75C15.575 2.75 16.25 3.425 16.25 4.25V14.75C16.25 15.575 15.575 16.25 14.75 16.25H4.25C3.425 16.25 2.75 15.575 2.75 14.75V4.25C2.75 3.425 3.425 2.75 4.25 2.75ZM5 14.75H14C14.4125 14.75 14.75 14.4125 14.75 14V5C14.75 4.5875 14.4125 4.25 14 4.25H5C4.5875 4.25 4.25 4.5875 4.25 5V14C4.25 14.4125 4.5875 14.75 5 14.75Z" fill="#C4C4C4"></path>
            </svg>
        </div>
        <input maxlength="${char_limit.medium}" type="text" id="option-value_${id}" class="edit_radio_button_choices" value="${value}" data-value="${value}">
        <div class="widget-delete-icon">
            <svg id="remove-checkbox-option_${id}" width="12" height="13" viewBox="0 0 12 13" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9.15011 3.35534C9.05669 3.26172 8.92987 3.2091 8.79761 3.2091C8.66535 3.2091 8.53852 3.26172 8.44511 3.35534L6.00011 5.79534L3.55511 3.35034C3.46169 3.25672 3.33487 3.2041 3.20261 3.2041C3.07035 3.2041 2.94352 3.25672 2.85011 3.35034C2.65511 3.54534 2.65511 3.86034 2.85011 4.05534L5.29511 6.50034L2.85011 8.94534C2.65511 9.14034 2.65511 9.45534 2.85011 9.65034C3.04511 9.84534 3.36011 9.84534 3.55511 9.65034L6.00011 7.20534L8.44511 9.65034C8.64011 9.84534 8.95511 9.84534 9.15011 9.65034C9.34511 9.45534 9.34511 9.14034 9.15011 8.94534L6.70511 6.50034L9.15011 4.05534C9.34011 3.86534 9.34011 3.54534 9.15011 3.35534Z" fill="#2D2D2D"></path>
            </svg>
        </div>
    </div>
    `

    return html;
}

function remove_checkbox_option(id, dependent_on) {
    const elem = document.getElementById(`checkbox-option_${id}`);

    if (elem) {
        const value = document.getElementById(`option-value_${id}`).value;
        const index = state.form_changes[`field_${id.substring(0, 5)}`]['3'][dependent_on].indexOf(value);

        if (index != -1) {
            state.form_changes[`field_${id.substring(0, 5)}`]['3'][dependent_on].splice(index, 1);

            const index2 = state.options_global.indexOf(value);
            if (index2 != -1) {
                state.options_global.splice(index2, 1)
            }

            const index3 = state.form_changes[`field_${id.substring(0, 5)}`]['3'].all_options.indexOf(value);
            if (index3 != -1) {
                state.form_changes[`field_${id.substring(0, 5)}`]['3'].all_options.splice(index3, 1)
            }

            if (state.option_map[value]) {
                state.option_map[value] = undefined;
            }
        }

        elem.remove();
        update_dependent_dropdowns();
    }
}

function add_radio_chip(id, value, is_validation_required) {
    value = value.trim();
    value = stripHTML(value);
    value = strip_unwanted_characters(value);

    if (!is_validation_required || validate_option_value(id, value, '2')) {
        const dependent_on = document.getElementById(`livechat-dependent-value-dropdown_${id}`).value;

        const elem = document.querySelector(`#field_${id} .livechat-dispose-radio-chip-area`);

        const chip_id = generate_random_string(5);

        const html = get_radio_option_html(value, id + chip_id);
        $(elem).append(html);

        $(`#remove-radio-option_${id}${chip_id}`).on('click', () => {
            remove_radio_option(id + chip_id, dependent_on);
        })

        $(`#option-value_${id}${chip_id}`).on('focusout', () => {
            change_option(id + chip_id, '2');
        })

        add_option_focus_event($(`#option-value_${id}${chip_id}`));
        add_option_focusout_event($(`#option-value_${id}${chip_id}`));

        document.getElementById(`radio-input-field_${id}`).value = '';
        update_dependent_dropdowns();
    }
}

function get_radio_option_html(value, id) {
    const char_limit = get_character_limit();

    const html = `
    <div id="radio-option_${id}" class="response-widget-dragable-output-item ">
        <div class="dragable-item-icon tooltip-custom">
            <svg width="24" height="25" viewBox="0 0 24 25" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path fill-rule="evenodd" clip-rule="evenodd" d="M16.9998 6.5C16.9998 7.6 16.0998 8.5 14.9998 8.5C13.8998 8.5 12.9998 7.6 12.9998 6.5C12.9998 5.4 13.8998 4.5 14.9998 4.5C16.0998 4.5 16.9998 5.4 16.9998 6.5ZM8.9998 4.5C7.8998 4.5 6.9998 5.4 6.9998 6.5C6.9998 7.6 7.8998 8.5 8.9998 8.5C10.0998 8.5 10.9998 7.6 10.9998 6.5C10.9998 5.4 10.0998 4.5 8.9998 4.5ZM6.99976 12.5C6.99976 11.4 7.89976 10.5 8.99976 10.5C10.0998 10.5 10.9998 11.4 10.9998 12.5C10.9998 13.6 10.0998 14.5 8.99976 14.5C7.89976 14.5 6.99976 13.6 6.99976 12.5ZM8.99976 20.5C10.0998 20.5 10.9998 19.6 10.9998 18.5C10.9998 17.4 10.0998 16.5 8.99976 16.5C7.89976 16.5 6.99976 17.4 6.99976 18.5C6.99976 19.6 7.89976 20.5 8.99976 20.5ZM14.9998 10.5C13.8998 10.5 12.9998 11.4 12.9998 12.5C12.9998 13.6 13.8998 14.5 14.9998 14.5C16.0998 14.5 16.9998 13.6 16.9998 12.5C16.9998 11.4 16.0998 10.5 14.9998 10.5ZM12.9998 18.5C12.9998 17.4 13.8998 16.5 14.9998 16.5C16.0998 16.5 16.9998 17.4 16.9998 18.5C16.9998 19.6 16.0998 20.5 14.9998 20.5C13.8998 20.5 12.9998 19.6 12.9998 18.5Z" fill="#DADADA"></path>
            </svg>
            <div class="tooltiptext-custom tooltip-bottom-custom tooltip-radio">Drag to move</div>
        </div>
        <div class="widget-indigator-icon">
            <svg width="24" height="25" viewBox="0 0 24 25" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path fill-rule="evenodd" clip-rule="evenodd" d="M5 12C5 8.136 8.136 5 12 5C15.864 5 19 8.136 19 12C19 15.864 15.864 19 12 19C8.136 19 5 15.864 5 12ZM6.39959 12C6.39959 15.094 8.90559 17.6 11.9996 17.6C15.0936 17.6 17.5996 15.094 17.5996 12C17.5996 8.90597 15.0936 6.39997 11.9996 6.39997C8.90559 6.39997 6.39959 8.90597 6.39959 12Z" fill="#C4C4C4"></path>
            </svg>
        </div>
        <input maxlength="${char_limit.medium}" type="text" id="option-value_${id}" class="edit_radio_button_choices" value="${value}" data-value="${value}">
        <div class="widget-delete-icon">
            <svg id="remove-radio-option_${id}" width="12" height="13" viewBox="0 0 12 13" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9.15011 3.35534C9.05669 3.26172 8.92987 3.2091 8.79761 3.2091C8.66535 3.2091 8.53852 3.26172 8.44511 3.35534L6.00011 5.79534L3.55511 3.35034C3.46169 3.25672 3.33487 3.2041 3.20261 3.2041C3.07035 3.2041 2.94352 3.25672 2.85011 3.35034C2.65511 3.54534 2.65511 3.86034 2.85011 4.05534L5.29511 6.50034L2.85011 8.94534C2.65511 9.14034 2.65511 9.45534 2.85011 9.65034C3.04511 9.84534 3.36011 9.84534 3.55511 9.65034L6.00011 7.20534L8.44511 9.65034C8.64011 9.84534 8.95511 9.84534 9.15011 9.65034C9.34511 9.45534 9.34511 9.14034 9.15011 8.94534L6.70511 6.50034L9.15011 4.05534C9.34011 3.86534 9.34011 3.54534 9.15011 3.35534Z" fill="#2D2D2D"></path>
            </svg>
        </div>
    </div>
    `

    return html;
}

function remove_radio_option(id, dependent_on) {
    const elem = document.getElementById(`radio-option_${id}`);

    if (elem) {
        const value = document.getElementById(`option-value_${id}`).value;
        const index = state.form_changes[`field_${id.substring(0, 5)}`]['2'][dependent_on].indexOf(value);

        if (index != -1) {
            state.form_changes[`field_${id.substring(0, 5)}`]['2'][dependent_on].splice(index, 1);

            const index2 = state.options_global.indexOf(value);
            if (index2 != -1) {
                state.options_global.splice(index2, 1)
            }

            const index3 = state.form_changes[`field_${id.substring(0, 5)}`]['2'].all_options.indexOf(value);
            if (index3 != -1) {
                state.form_changes[`field_${id.substring(0, 5)}`]['2'].all_options.splice(index3, 1);
            }

            if (state.option_map[value]) {
                state.option_map[value] = undefined;
            }
        }

        elem.remove();
        update_dependent_dropdowns();
    }
}

function add_option_focus_event(elem) {
    $(elem).on('focus', () => {
        const theme_color = get_theme_color();

        $(elem).parent().css("background", "#ffffff");
        $(elem).parent().css('border', `1px solid #F7F7F7`);
        $(elem).parent().children('.widget-delete-icon').css("display", "none");
    })
}

function add_option_focusout_event(elem) {
    $(elem).on('focusout', () => {
        const theme_color = get_theme_color();

        $(elem).parent().css("background", `#F7F7F7`);
        $(elem).parent().css('border', `none`);
        $(elem).parent().children('.widget-delete-icon').css("display", "block");
    })
}

function change_option(id, input_type) {
    const elem = document.getElementById(`option-value_${id}`);

    let value = elem.value;
    value = stripHTML(value);
    value = strip_unwanted_characters(value);

    if (value == elem.dataset.value) {
        elem.value = value;
        return;
    };

    if (validate_option_value(id.substring(0, 5), value, input_type, elem.dataset.value)) {
        update_dependent_dropdowns();
        elem.dataset.value = value;
    } else {
        elem.value = elem.dataset.value;
    }
}

function update_options(el, input_type) {
    const id = el.id.split('_')[1];
    const value = el.value;

    if (input_type == '6') {
        document.querySelector(`#field_${id} .livechat-dispose-dropdown-chip-area`).innerHTML = '';

        const field_changes = state.form_changes[`field_${id}`];

        if (field_changes) {
            const options = field_changes[input_type];

            if (options && options[value]) {
                for (const option of options[value]) {
                    add_dropdown_chip(id, option, false);
                }
            }
        }
    }
    else if (input_type == '3') {
        document.querySelector(`#field_${id} .livechat-dispose-checkbox-chip-area`).innerHTML = '';

        const field_changes = state.form_changes[`field_${id}`];

        if (field_changes) {
            const options = field_changes[input_type];

            if (options && options[value]) {
                for (const option of options[value]) {
                    add_checkbox_chip(id, option, false);
                }
            }
        }
    }
    else if (input_type == '2') {
        document.querySelector(`#field_${id} .livechat-dispose-radio-chip-area`).innerHTML = '';

        const field_changes = state.form_changes[`field_${id}`];

        if (field_changes) {
            const options = field_changes[input_type];

            if (options && options[value]) {
                for (const option of options[value]) {
                    add_radio_chip(id, option, false);
                }
            }
        }
    }
}

function update_independent_fields(id, input_type) {
    if (input_type == '1') {
        const elem = document.getElementById(`text-field-placeholder_${id}`);

        if (elem) {
            if (state.form_changes[`field_${id}`] && state.form_changes[`field_${id}`]['1']) {
                elem.value = state.form_changes[`field_${id}`]['1'];
            }
        }
    } else if (input_type == '5') {
        const elem = document.getElementById(`comment-field-placeholder_${id}`);

        if (elem) {
            if (state.form_changes[`field_${id}`] && state.form_changes[`field_${id}`]['5']) {
                elem.value = state.form_changes[`field_${id}`]['5'];
            }
        }
    } else if (input_type == '4') {
        const elem = document.getElementById(`date-field-select_${id}`);

        if (elem) {
            if (state.form_changes[`field_${id}`] && state.form_changes[`field_${id}`]['4']) {
                elem.value = state.form_changes[`field_${id}`]['4'];
            }
        }
    } else if (input_type == '8') {
        const elem = document.getElementById(`mobile-field-placeholder_${id}`);

        if (elem) {
            if (state.form_changes[`field_${id}`] && state.form_changes[`field_${id}`]['8']) {
                elem.value = state.form_changes[`field_${id}`]['8'];
            }
        }
    } else if (input_type == '9') {
        const elem = document.getElementById(`email-field-placeholder_${id}`);

        if (elem) {
            if (state.form_changes[`field_${id}`] && state.form_changes[`field_${id}`]['9']) {
                elem.value = state.form_changes[`field_${id}`]['9'];
            }
        }
    }
}

/* Update Dependent Dropdowns Functionality */

function update_dependent_dropdowns() {
    const fields = document.getElementsByClassName('livechat-create-form-field');
    const dependent_values = [];

    Array.from(fields).forEach(field => {
        const id = field.id.split('_')[1];

        const input_type = document.getElementById(`input-type-dropdown_${id}`).value;

        if (state.dependent_types.includes(input_type)) {
            add_options_in_dependent_dropdown(id, dependent_values);

            const field_changes = state.form_changes[`field_${id}`];

            if (field_changes) {
                const options = field_changes[input_type];

                if (options) {
                    for (const key in options) {
                        if (key == 'all_options') continue;

                        for (const option of options[key]) {
                            dependent_values.push(option);
                            state.option_map[option] = field.id;
                        }
                    }
                }
            }
        }
    })
}

function add_options_in_dependent_dropdown(id, values) {
    const elem = document.getElementById(`livechat-dependent-value-dropdown_${id}`);
    let selected_val = elem.value;
    let is_selected_val_present = selected_val == '0';

    if (elem) {
        elem.innerHTML = `<option value="0" selected>None</option>`;

        values.forEach(value => {
            if (selected_val == value) {
                is_selected_val_present = true;
            }

            const option_id = generate_random_string(5);
            elem.innerHTML += `<option value="${value}">${value}</option>`
        })
    }

    if (is_selected_val_present) {
        $(elem).val(selected_val);
    } else {
        $(elem).val('0');
        update_options(elem, document.getElementById(`input-type-dropdown_${id}`).value);
    }

    $(elem).selectpicker('refresh');
}

/* Update Dependent Dropdowns Functionality Ends */

/* Save Form Functionality */

export function save_dispose_chat_form() {
    const is_form_enabled = document.getElementById('livechat-chat-dispose-page-toggle-cb').checked;

    let form = {}

    let need_to_save = true;
    if (is_form_enabled) {
        let data = get_built_form_info(true);

        if (data) {
            form = data.form;
            need_to_save = data.need_to_save;
        } else {
            need_to_save = false;
        }
    }

    if(need_to_save) {
        save_form_to_server(is_form_enabled, form);
    }

}

function save_form_to_server(is_form_enabled, form) {
    const json_string = JSON.stringify({
        bot_pk: get_url_vars()['bot_pk'],
        is_form_enabled: is_form_enabled,
        form: form,
    }) 

    const params = get_params(json_string);

    let config = {
          headers: {
            'X-CSRFToken': getCsrfToken(),
          }
        }

    axios.post('/livechat/save-dispose-chat-form/', params, config)
        .then(response => {
            response = custom_decrypt(response.data)
            response = JSON.parse(response)
            
            if (response.status == '200') {
                showToast('Changes Saved Successfully.', 2000);
            } else {
                showToast('Failed to save form. Please try again later', 2000);
            }
        })
        .catch((err) => {
            console.log(err);
            showToast('Failed to save form. Please try again later', 2000);
        });
}

export function get_built_form_info(is_toast_required) {
    let form = {};
    
    form.field_order = [];
    const fields = document.getElementsByClassName('livechat-create-form-field');

    if (is_toast_required && fields.length == 0) {
        showToast('Form Cannot be empty', 2000);
        return;
    }

    let need_to_save = Array.from(fields).length != 0;
    Array.from(fields).forEach(field => {
        form[field.id] = {};

        let label_name = document.querySelector(`#${field.id} .form-field-label-name`).value.trim();
        label_name = stripHTMLtags(label_name);
        label_name = strip_unwanted_characters(label_name);

        if (is_toast_required && label_name == '') {
            showToast('Label name cannot be empty', 2000);
            need_to_save = false;
            return;
        }

        form[field.id].label_name = label_name;

        let input_type = document.getElementById(`input-type-dropdown_${field.id.split('_')[1]}`).value;
        form[field.id].type = input_type;

        form[field.id].optional = document.querySelector(`#${field.id} .livechat-form-field-optional-checkbox`).checked;

        const field_info = get_field_info_based_input_type(input_type, field.id, form);

        if (is_toast_required && 'is_valid' in field_info && field_info.is_valid == false) {
            showToast(field_info.error, 2000);
            need_to_save = false;
            return;
        }

        form[field.id] = { ...form[field.id], ...field_info };
        form.field_order.push(field.id);
    })

    return {
        form: form,
        need_to_save: need_to_save,
    };
}

function get_field_info_based_input_type(input_type, id, form) {
    if (input_type == '1' || input_type == '8' || input_type == '9') {
        return get_text_field_info(id, input_type);
    }
    else if (input_type == '2') {
        return get_radio_field_info(id, form);
    }
    else if (input_type == '3') {
        return get_checkbox_field_info(id, form);
    }
    else if (input_type == '4') {
        return get_single_date_field_info(id);
    }
    else if (input_type == '5') {
        return get_comment_field_info(id);
    }
    else if (input_type == '6') {
        return get_dropdown_field_info(id, form);
    }
    else if (input_type == '7') {
        return { dependent: false };
    } 
}

function get_text_field_info(id, input_type) {
    if (!state.form_changes[id]) {
        return {
            is_valid: false,
            error: 'Placeholder text cannot be empty.'
        }
    }

    let placeholder_text = state.form_changes[id][input_type];
    placeholder_text = placeholder_text.trim();
    placeholder_text = stripHTMLtags(placeholder_text);
    placeholder_text = strip_unwanted_characters(placeholder_text);

    if (!placeholder_text || placeholder_text == '') {
        return {
            is_valid: false,
            error: 'Placeholder text cannot be empty.'
        }
    } else {
        return {
            placeholder: placeholder_text,
            dependent: false,
        }
    }
}

function get_radio_field_info(id, form) {
    if (state.form_changes[id]) {
        const options = state.form_changes[id]['2'];
        if (options && Object.keys(options).length > 0) {
            if (options['0'] && options['0'].length > 0) {
                return {
                    dependent: false,
                    values: options['0'],
                }
            } else {
                let value_map = { dependent: true };
                let is_options_empty = true;
                for (const key in options) {
                    if (key == '0' || key == 'all_options' || key == 'dependent_ids' || key == 'dependent_on_ids') continue;

                    if (options[key].length > 0) {
                        is_options_empty = false;

                        value_map[key] = options[key];
                    
                        const key_field_id = state.option_map[key];
                        if (!form[key_field_id]) continue;
    
                        if (!form[key_field_id]['dependent_ids']) {
                            form[key_field_id]['dependent_ids'] = [];
                        }
    
                        if (!form[key_field_id]['dependent_ids'].includes(id)) {
                            form[key_field_id]['dependent_ids'].push(id)
                        }
    
    
                        if (!form[id]['dependent_on_ids']) {
                            form[id]['dependent_on_ids'] = [];
                        }
    
                        if (!form[id]['dependent_on_ids'].includes(key_field_id)) {
                            form[id]['dependent_on_ids'].push(key_field_id)
                        }
                    }
                }

                if (Array.isArray(options.all_options))
                    value_map.all_options = [...options.all_options];

                if (!is_options_empty) return value_map;
            }
        }
    }

    return {
        is_valid: false,
        error: 'Radio button field cannot be empty.'
    }
}

function get_checkbox_field_info(id, form) {
    if (state.form_changes[id]) {
        const options = state.form_changes[id]['3'];

        if (options && Object.keys(options).length > 0) {
            if (options['0'] && options['0'].length > 0) {
                return {
                    dependent: false,
                    values: options['0'],
                }
            } else {
                let value_map = { dependent: true };
                let is_options_empty = true;
                for (const key in options) {
                    if (key == '0' || key == 'all_options' || key == 'dependent_ids' || key == 'dependent_on_ids') continue;

                    if (options[key].length > 0) {
                        is_options_empty = false;

                        value_map[key] = options[key];

                        const key_field_id = state.option_map[key];
    
                        if (!form[key_field_id]) continue;
    
                        if (!form[key_field_id]['dependent_ids']) {
                            form[key_field_id]['dependent_ids'] = [];
                        }
    
                        if (!form[key_field_id]['dependent_ids'].includes(id)) {
                            form[key_field_id]['dependent_ids'].push(id)
                        }
    
    
                        if (!form[id]['dependent_on_ids']) {
                            form[id]['dependent_on_ids'] = [];
                        }
    
                        if (!form[id]['dependent_on_ids'].includes(key_field_id)) {
                            form[id]['dependent_on_ids'].push(key_field_id)
                        }
                    }
                }

                if (Array.isArray(options.all_options))
                    value_map.all_options = [...options.all_options];

                if (!is_options_empty) return value_map;
            }
        }
    }

    return {
        is_valid: false,
        error: 'Checkbox field cannot be empty.'
    }
}

function get_single_date_field_info(id) {
    if (!state.form_changes[id]) {
        return {
            is_valid: false,
            error: 'Please select date format.'
        }
    }

    let date_format = state.form_changes[id]['4'];

    if (!date_format || date_format == '') {
        return {
            is_valid: false,
            error: 'Please select date format.'
        }
    } else {
        return {
            date_format: date_format,
            dependent: false,
        }
    }
}

function get_comment_field_info(id) {
    if (!state.form_changes[id]) {
        return {
            is_valid: false,
            error: 'Placeholder text for comment cannot be empty.'
        }
    }

    let placeholder_text = state.form_changes[id]['5'];
    placeholder_text = placeholder_text.trim();
    placeholder_text = stripHTML(placeholder_text);
    placeholder_text = strip_unwanted_characters(placeholder_text);

    if (!placeholder_text || placeholder_text == '') {
        return {
            is_valid: false,
            error: 'Placeholder text for comment cannot be empty.'
        }
    } else {
        return {
            placeholder: placeholder_text,
            dependent: false,
        }
    }
}

function get_dropdown_field_info(id, form) {
    if (state.form_changes[id]) {
        const options = state.form_changes[id]['6'];

        if (options && Object.keys(options).length > 0) {
            if (options['0'] && options['0'].length > 0) {
                return {
                    dependent: false,
                    values: options['0'],
                }
            } else {
                let value_map = { dependent: true };
                let is_options_empty = true;
                for (const key in options) {
                    if (key == '0' || key == 'all_options' || key == 'dependent_ids' || key == 'dependent_on_ids') continue;

                    if (options[key].length > 0) {
                        is_options_empty = false;

                        value_map[key] = options[key];
                    
                        const key_field_id = state.option_map[key];
                        if (!form[key_field_id]) continue;

                        if (!form[key_field_id]['dependent_ids']) {
                            form[key_field_id]['dependent_ids'] = [];
                        }

                        if (!form[key_field_id]['dependent_ids'].includes(id)) {
                            form[key_field_id]['dependent_ids'].push(id)
                        }

                        if (!form[id]['dependent_on_ids']) {
                            form[id]['dependent_on_ids'] = [];
                        }

                        if (!form[id]['dependent_on_ids'].includes(key_field_id)) {
                            form[id]['dependent_on_ids'].push(key_field_id)
                        }
                    }
                }

                if (Array.isArray(options.all_options))
                    value_map.all_options = [...options.all_options];

                if (!is_options_empty) return value_map;
            }
        }
    }

    return {
        is_valid: false,
        error: 'Dropdown choices cannot be empty.'
    }
}

export function save_raise_ticket_form() {
    const is_form_enabled = document.getElementById('livechat-raise-ticket-page-toggle-cb').checked;

    let form = {}

    let need_to_save = true;
    if (is_form_enabled) {
        let data = get_built_form_info(true);

        if (data) {
            form = data.form;
            need_to_save = data.need_to_save;
        } else {
            need_to_save = false;
        }
    }

    if(need_to_save) {
        save_raise_ticket_form_to_server(is_form_enabled, form);
    }

}

function save_raise_ticket_form_to_server(is_form_enabled, form) {
    const json_string = JSON.stringify({
        bot_pk: get_url_vars()['bot_pk'],
        is_form_enabled: is_form_enabled,
        form: form,
    }) 

    const params = get_params(json_string);
    let config = {
        headers: {
            'X-CSRFToken': getCsrfToken(),
        }
    }
    axios.post('/livechat/save-raise-ticket-form/', params, config)
        .then(response => {
            response = custom_decrypt(response.data)
            response = JSON.parse(response)
            
            if (response.status == '200') {
                showToast('Changes Saved Successfully.', 2000);
            } else {
                showToast('Failed to save form. Please try again later', 2000);
            }
        })
        .catch((err) => {
            console.log(err);
            showToast('Failed to save form. Please try again later', 2000);
        });
}


/* Save Form Functionality Ends */

/* Save Form Builder Attachment Starts */

export function handle_image_upload_input_change(id, type='') {

    state.attachment.form_data = new FormData();
    state.attachment.data = document.querySelector(
        "#drag-drop-input-box"+type+"_"+id
    ).files[0];
    if (
        !is_file_supported(state.attachment.data.name) ||
        !check_malicious_file(state.attachment.data.name)
    ) {
        showToast("Invalid File Format!", 3000);
        return;
    }

    if (!check_file_size(state.attachment.data.size)) {
        showToast("Please Enter a file of size less than 5MB!", 3000);
        return;
    }

    append_file_to_attachment_div(state.attachment.data.name, id, type);
}

function append_file_to_attachment_div(file_name, id, type) {

    if (file_name) {
        $('#upload-file-section'+type+'_'+id+' .drag-drop-container').hide();

        $('#upload-file-section'+type+'_'+id+' #file-selected-container'+type+'_'+id).html(`
        <div class="selected-image-wrapper">
            <div class="image-container-div">
            <svg width="24" height="25" viewBox="0 0 24 25" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path fill-rule="evenodd" clip-rule="evenodd" d="M14.8638 4.69045L18.4754 8.30204C18.6005 8.42711 18.6708 8.59676 18.6708 8.77367V19.1708C18.6708 19.9077 18.0735 20.505 17.3367 20.505H6.66333C5.92649 20.505 5.32916 19.9077 5.32916 19.1708V5.82916C5.32916 5.09232 5.92649 4.495 6.66333 4.495H14.3922C14.5691 4.49503 14.7387 4.56534 14.8638 4.69045ZM17.0031 19.1708C17.1873 19.1708 17.3367 19.0215 17.3367 18.8373V9.18793C17.3366 9.09964 17.3016 9.01496 17.2393 8.95245L14.2134 5.92656C14.1509 5.8642 14.0662 5.82918 13.9779 5.82916H6.99687C6.81266 5.82916 6.66333 5.97849 6.66333 6.1627V18.8373C6.66333 19.0215 6.81266 19.1708 6.99687 19.1708H17.0031ZM9.86466 11.1658C10.6015 11.1658 11.1988 10.5685 11.1988 9.83166C11.1988 9.09482 10.6015 8.4975 9.86466 8.4975C9.12782 8.4975 8.5305 9.09482 8.5305 9.83166C8.5305 10.5685 9.12782 11.1658 9.86466 11.1658ZM13.2001 11.4613C13.3151 11.4613 13.422 11.5206 13.4829 11.6181L16.3774 16.247C16.4097 16.2984 16.4115 16.3634 16.3821 16.4165C16.3527 16.4696 16.2967 16.5026 16.236 16.5025H8.16427C8.10353 16.5026 8.04756 16.4696 8.01815 16.4165C7.98874 16.3634 7.99053 16.2984 8.02285 16.247L9.874 13.2858C9.93495 13.1883 10.0418 13.1291 10.1568 13.1291C10.2718 13.1291 10.3787 13.1883 10.4397 13.2858L11.016 14.2077C11.0468 14.2562 11.1001 14.2855 11.1575 14.2855C11.2148 14.2855 11.2682 14.2562 11.2989 14.2077L12.9172 11.6181C12.9782 11.5206 13.0851 11.4613 13.2001 11.4613Z" fill="black"/>
            <mask id="mask0_131_1347" style="mask-type:alpha" maskUnits="userSpaceOnUse" x="5" y="4" width="14" height="17">
            <path fill-rule="evenodd" clip-rule="evenodd" d="M14.8638 4.69045L18.4754 8.30204C18.6005 8.42711 18.6708 8.59676 18.6708 8.77367V19.1708C18.6708 19.9077 18.0735 20.505 17.3367 20.505H6.66333C5.92649 20.505 5.32916 19.9077 5.32916 19.1708V5.82916C5.32916 5.09232 5.92649 4.495 6.66333 4.495H14.3922C14.5691 4.49503 14.7387 4.56534 14.8638 4.69045ZM17.0031 19.1708C17.1873 19.1708 17.3367 19.0215 17.3367 18.8373V9.18793C17.3366 9.09964 17.3016 9.01496 17.2393 8.95245L14.2134 5.92656C14.1509 5.8642 14.0662 5.82918 13.9779 5.82916H6.99687C6.81266 5.82916 6.66333 5.97849 6.66333 6.1627V18.8373C6.66333 19.0215 6.81266 19.1708 6.99687 19.1708H17.0031ZM9.86466 11.1658C10.6015 11.1658 11.1988 10.5685 11.1988 9.83166C11.1988 9.09482 10.6015 8.4975 9.86466 8.4975C9.12782 8.4975 8.5305 9.09482 8.5305 9.83166C8.5305 10.5685 9.12782 11.1658 9.86466 11.1658ZM13.2001 11.4613C13.3151 11.4613 13.422 11.5206 13.4829 11.6181L16.3774 16.247C16.4097 16.2984 16.4115 16.3634 16.3821 16.4165C16.3527 16.4696 16.2967 16.5026 16.236 16.5025H8.16427C8.10353 16.5026 8.04756 16.4696 8.01815 16.4165C7.98874 16.3634 7.99053 16.2984 8.02285 16.247L9.874 13.2858C9.93495 13.1883 10.0418 13.1291 10.1568 13.1291C10.2718 13.1291 10.3787 13.1883 10.4397 13.2858L11.016 14.2077C11.0468 14.2562 11.1001 14.2855 11.1575 14.2855C11.2148 14.2855 11.2682 14.2562 11.2989 14.2077L12.9172 11.6181C12.9782 11.5206 13.0851 11.4613 13.2001 11.4613Z" fill="white"/>
            </mask>
            <g mask="url(#mask0_131_1347)">
            </g>
            </svg>
            
                                                                 
            </div>
            <div class="image-name-copy-div">
                <div class="image-name" style="font-weight: normal;font-size: 14px;color:#000000;line-height: 17px;">
                    ${file_name}
                </div>
                <svg onclick="handle_image_cross_btn('${id}', '${type}')" class="dismiss-circle" width="20" height="21" viewBox="0 0 20 21" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M10 2.5C14.4183 2.5 18 6.08172 18 10.5C18 14.9183 14.4183 18.5 10 18.5C5.58172 18.5 2 14.9183 2 10.5C2 6.08172 5.58172 2.5 10 2.5ZM7.80943 7.61372C7.61456 7.47872 7.34514 7.49801 7.17157 7.67157L7.11372 7.74082C6.97872 7.93569 6.99801 8.20511 7.17157 8.37868L9.29289 10.5L7.17157 12.6213L7.11372 12.6906C6.97872 12.8854 6.99801 13.1549 7.17157 13.3284L7.24082 13.3863C7.43569 13.5213 7.70511 13.502 7.87868 13.3284L10 11.2071L12.1213 13.3284L12.1906 13.3863C12.3854 13.5213 12.6549 13.502 12.8284 13.3284L12.8863 13.2592C13.0213 13.0643 13.002 12.7949 12.8284 12.6213L10.7071 10.5L12.8284 8.37868L12.8863 8.30943C13.0213 8.11456 13.002 7.84514 12.8284 7.67157L12.7592 7.61372C12.5643 7.47872 12.2949 7.49801 12.1213 7.67157L10 9.79289L7.87868 7.67157L7.80943 7.61372Z" fill="#4D4D4D"/>
            </svg> 
              
            </div>
        </div>`)
    }
}

export function handle_image_cross_btn(id, type) {
    $("#upload-file-section"+type+"_"+id+" .drag-drop-container").show();

    $('#upload-file-section'+type+'_'+id+' #file-selected-container'+type+'_'+id).html("");
    $("#upload-file-section"+type+"_"+id+" #drag-drop-input-box"+type+"_"+id).val("");
    state.attachment.file_src = "";
}

/* Save Form Builder Attachment Ends */

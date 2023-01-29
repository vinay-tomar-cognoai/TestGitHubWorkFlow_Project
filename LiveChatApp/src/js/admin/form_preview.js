import { initialize_country_code_selector } from "../agent/country_code";
import { validate_email, validate_number_input_value, validate_phone_number } from "../utils";
import { get_built_form_info } from "./form_builder";

const state = {
    form: {},
    option_map: {},
    days: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
    months: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
}

export function sync_preview() {
    $('#livechat_form_preview_div').html('');

    const data = get_built_form_info(true);

    if (!data) return;
    
    const sync_required = data.need_to_save;


    if (!sync_required) return;

    const form = data.form;

    state.form = { ...form };

    generate_option_map();

    const field_ids = form.field_order;

    field_ids.forEach(field_id => {
        const field = form[field_id];

        const html = get_field_html_based_input_type(field, field_id.split('_')[1]);

        $('#livechat_form_preview_div').append(html);

        if (field.type == '4') {
            $(`#livechat-form-datepicker_${field_id.split('_')[1]}`).datepicker();

            $(`#livechat-form-datepicker_${field_id.split('_')[1]}`).on('change', (e) => {
                change_date(e.target);
            })
        } else if (field.type == '2') {
            $(`.livechat-form-radio-btn_${field_id.split('_')[1]}`).on('change', (e) => {
                update_dependent_inputs(field_id.split('_')[1]);
            })
        } else if( field.type == '6') {
            $(`#input-element_${field_id.split('_')[1]}`).on('change', (e) => {
                update_dependent_inputs(field_id.split('_')[1]);
            })
        } else if (field.type == '3') {
            $(`.livechat-form-checkbox_${field_id.split('_')[1]}`).on('change', (e) => {
                update_dependent_inputs(field_id.split('_')[1]);
            })
        } else if (field.type == '8') {
            initialize_country_code_selector(null, `input-element_${field_id.split('_')[1]}`);

            $(`#input-element_${field_id.split('_')[1]}`).on('focusout', (e) => {
                
                let is_valid = $(`#input-element_${field_id.split('_')[1]}`).intlTelInput("isValidNumber");
                
                if (!is_valid) {
                    $(`#error-message_${field_id.split('_')[1]}`).show();
                } else {
                    if($(`#input-element_${field_id.split('_')[1]}`).intlTelInput("getSelectedCountryData").dialCode == "91") {

                        if (!validate_phone_number(`input-element_${field_id.split('_')[1]}`)) {
                            $(`#error-message_${field_id.split('_')[1]}`).show();
                        } else {
                            $(`#error-message_${field_id.split('_')[1]}`).hide();
                        }
                    } else {
                        if (!validate_number_input_value(e.target.value)) {
                            $(`#error-message_${field_id.split('_')[1]}`).show();
                        } else {
                            $(`#error-message_${field_id.split('_')[1]}`).hide();
                        }
                    }
                }
            })
        } else if (field.type == '9') {
            $(`#input-element_${field_id.split('_')[1]}`).on('focusout', (e) => {
                console.log('here');
                if (!validate_email(`input-element_${field_id.split('_')[1]}`)) {
                    $(`#error-message_${field_id.split('_')[1]}`).show();
                } else {
                    $(`#error-message_${field_id.split('_')[1]}`).hide();
                }
            })   
        }
    })
}

export function generate_option_map() {
    const field_ids = state.form.field_order;

    field_ids.forEach(field_id => {
        const field = state.form[field_id];

        if (['2', '3', '6'].includes(field.type)) {
            if (field.dependent) {
                for (const key in field) {
                    if (key == '0') continue;
                    
                    if (Array.isArray(field[key]) && key != 'dependent_ids' && key != 'dependent_on_ids' && key != 'all_options') {
                        const key_id = field.dependent_on_ids.filter((_val, index, arr) => {
                            const _field = state.form[_val];
                            if (_field.dependent) {
                                if (_field.all_options.includes(key)) {
                                    return _val;
                                }
                            } else {
                                if (_field.values.includes(key)) {
                                    return _val;
                                }
                            }
                        })

                        for (const option of field[key]) {
                            state.option_map[option] = key_id[0];
                        }
                    }
                }
            }
        }
    })
}

export function get_field_html_based_input_type(field, id) {
    if (field.type == '1') {
        return get_text_field_html(field, id);
    }
    else if (field.type == '2') {
        return get_radio_button_html(field, id);
    }
    else if (field.type == '3') {
        return get_checkbox_html(field, id);
    }
    else if (field.type == '4') {
        return get_date_field_html(field, id);
    }
    else if (field.type == '5') {
        return get_comment_field_html(field, id);
    }
    else if (field.type == '6') {
        return get_dropdown_html(field, id);
    }
    else if (field.type == '7') {
        return get_attachment_html(field, id);
    }
    else if (field.type == '8') {
        return get_mobile_field_html(field, id);
    }
    else if (field.type == '9') {
        return get_email_field_html(field, id);
    }

}

function get_text_field_html(field, id) {
    let html = `
    <div class="mb-3">
        <label>${field.label_name}
    `

    if (!field.optional) {
        html += `
        <b>*</b>
        `
    }
    
    html += `
    </label>
    <input class="form-control raise-ticket-text-field" id="input-element_${id}" type="text" placeholder="${field.placeholder}">
    </div>
    `

    return html;
}

function get_mobile_field_html(field, id) {
    let html = `<div class="mb-3 phone-number-input-div-preview preview-input-div">
                    <label>${field.label_name}`;
            
    if (!field.optional) {
        html += `<b>*</b>`;
    }

    html +=     `</label>
                <input type="tel" id="input-element_${id}" placeholder="${field.placeholder}" class="customer-phone-number">
                <div class="errorMsg" id="error-message_${id}">Please enter valid number</div>
            </div>`;
    
    return html;
}

function get_email_field_html (field, id) {
    let html = `<div class="mb-3 email-address-input-div-preview preview-input-div">
                    <label>${field.label_name}`;

    if (!field.optional) {
        html += `<b>*</b>`;
    }
                
    html += `</label><input maxlength="100" id="input-element_${id}" class="text-field-placeholder-text" type="text" placeholder="${field.placeholder}">
            <div class="errorMsg" id="error-message_${id}">Please enter valid Email ID</div>
            </div>`
    
    return html;
}

function get_comment_field_html(field, id) {
    let html = `
    <div class="mb-3 form-preview-comment-container">
        <label>${field.label_name}
    `

    if (!field.optional) {
        html += `
        <b>*</b>
        `
    }

    html += `
    </label>
    <textarea id="input-element_${id}" class="form-preview-comment-section-textarea" placeholder="${field.placeholder}"></textarea>
    </div>
    `

    return html
}

function get_date_field_html(field, id) {
    let html = `
    <div class="mb-3 form-preview-date-div-container">
        <label>${field.label_name}
    `

    if (!field.optional) {
        html += `
        <b>*</b>
        `
    }

    html += `
        </label>
        <div class="livechat-dispose-date-preview-wrapper" id="livechat-date-display-wrapper_${id}">
            <div class="livechat-dispose-date-div date">02</div>
            <div class="livechat-dispose-month-day-wrapper">
                <div class="livechat-dispose-month-div month-year">
                    May 2021
                </div>
                <div class="livechat-dispose-day-div day">Thursday</div>
            </div>
            <input type="text" id="livechat-form-datepicker_${id}" class="resolve-chat-datepicker-input" placeholder="Add Date">
        </div>
    </div>
    `

    return html;
}

export function change_date(el) {
    if (el.value !== "Add Date") {
        const id = el.id.split('_')[1];
        const date = new Date(el.value);
        
        document.querySelector(`#livechat-date-display-wrapper_${id} .date`).innerHTML = date.getDate();
        document.querySelector(`#livechat-date-display-wrapper_${id} .month-year`).innerHTML = state.months[date.getMonth()] + " " + date.getFullYear();
        document.querySelector(`#livechat-date-display-wrapper_${id} .day`).innerHTML = state.days[date.getDay()];

        el.style.opacity = "0";
    }
}

function get_radio_button_html(field, id) {
    let display_prop = 'block';

    if (field.dependent) {
        display_prop = 'none';
    }

    let html = `
    <div class="mb-3 form-preview-radio-checkbox-div" id="input-element_${id}" style="display: ${display_prop}">
        <label>${field.label_name}
    `

    if (!field.optional) {
        html += `
        <b>*</b>
        `
    }

    html += `
        </label>
    `

    if (!field.dependent) {
        for (const option of field.values) {
            html += `
            <div class="radio-btn-container-item" data-value="${option}">
                <input type="radio" name="radio_${id}" value="${option}" id="${option}" class="livechat-custom-agent-radio-btn livechat-form-radio-btn_${id}">
                <label for="${option}">${option}</label>
            </div>
            `
        }
    } else {
        for (const key in field) {
            if (Array.isArray(field[key]) && key != '0' && key != 'all_options' && key != 'dependent_on_ids' && key != 'dependent_ids') {
                for (const option of field[key]) {
                    html += `
                    <div class="radio-btn-container-item" data-value="${option}" style="display: none;">
                        <input type="radio" name="radio_${id}" value="${option}" id="${option}" class="livechat-custom-agent-radio-btn livechat-form-radio-btn_${id}">
                        <label for="${option}">${option}</label>
                    </div>
                    `
                }
            }
        }
    }

    html += `
    </div>
    `

    return html;
}

function get_checkbox_html (field, id) {
    let display_prop = 'block';

    if (field.dependent) {
        display_prop = 'none';
    }

    let html = `
    <div id="input-element_${id}" class="mb-3 form-preview-radio-checkbox-div agent-chat-dispose-checkbox-option" style="display: ${display_prop}">
        <label>${field.label_name}
    `

    if (!field.optional) {
        html += `
        <b>*</b>
        `
    }

    html += `
    </label>
    `

    if (!field.dependent) {
        for (const option of field.values) {
            html += `
            <div class="checkbox-btn-container-item" data-value="${option}">
                <input type="checkbox" class="livechat-form-checkbox_${id}" id="${option}" name="" value="${option}">
                <label for="${option}">${option}</label>
            </div>
            `
        }
    
    } else {
        for (const key in field) {
            if (Array.isArray(field[key]) && key != '0' && key != 'all_options' && key != 'dependent_on_ids' && key != 'dependent_ids') {
                for (const option of field[key]) {
                    html += `
                    <div class="checkbox-btn-container-item" data-value="${option}" style="display: none;">
                        <input type="checkbox" class="livechat-form-checkbox_${id}" id="${option}" name="" value="${option}">
                        <label for="${option}">${option}</label>
                    </div>
                    `
                }
            }
        }
    }

    html += `
    </div>
    `

    return html;
}

function get_dropdown_html (field, id) {
    let html = `
    <div class="mb-3">
        <label>${field.label_name}
    `

    if (!field.optional) {
        html += `
        <b>*</b>
        `
    }

    html += `
        </label>
    `

    if (field.dependent) {
        html += `
        <select name="dropdown_${id}" class="form-control select-dropdown-icon" disabled id="input-element_${id}">
        `
        html += `<option value="0" selected disabled>Choose one of the following</option>`

        for (const key in field) {
            if (Array.isArray(field[key]) && key != '0' && key != 'all_options' && key != 'dependent_on_ids' && key != 'dependent_ids') {
                for (const option of field[key]) {
                    html += `
                    <option value="${option}" style="display: none;">${option}</option>
                    `
                }
            }
        }

        html += `</select>
        `
    } else {
        html += `<select name="dropdown_${id}" class="form-control select-dropdown-icon" id="input-element_${id}">`

        html += `<option value="0" selected disabled>Choose one of the following</option>`

        for (const option of field.values) {
            html += `
            <option value="${option}">${option}</option>
            `
        }

        html += `</select>`
    }

    html += `
    </div>
    `

    return html;
}

function get_attachment_html(field, id) {

    let html = `<div class="mb-3">
                    <label>${field.label_name}
                `;

    if (!field.optional) {
        html += `
        <b>*</b>
        `;
    }
        
    html += `
        </label>
        <div id="upload-file-sectionpreview_${id}">
            <div id="file-selected-containerpreview_${id}">
            </div>
            <div class="drag-drop-container" style="text-align: center;background: #eff6ff;border: 0.7px dashed #93C5FD;border-radius: 3px;padding: 20px;height: 70px;position: relative;">
                <span class="drag-drop-message" style="color: rgb(15, 82, 161); flex-direction: column; display: flex;align-items: center;justify-content: center; margin-top: 5px;">   
                    <p style="width:90%;margin-bottom: 0;color: #A8A8A8;font-size: 12px;font-weight: 500;">
                        Drag and drop or 
                        <a style="color: #2754F3;">browse</a>
                    </p>
                </span>
                <div class="drag-drop-input-field-wrapper">
                    <input onchange="handle_image_upload_input_change('${id}', 'preview')" id="drag-drop-input-boxpreview_${id}" style="border-bottom: none !important;border: 1px solid black;height: 100% !important;opacity: 0;cursor: pointer; width: 100%;" type="file" accept=".jpg,.png,.svg,.pdf">
                </div>
            </div>
            </div>
        </div>`;

    return html;
}

export function update_dependent_inputs(id) {
    const field = state.form[`field_${id}`];
    const dependent_ids = field.dependent_ids;

    if (!dependent_ids) return;

    dependent_ids.forEach(dependent_id => {
        dependent_id = dependent_id.split('_')[1];

        if (field.type == '2') {
            update_dependent_inputs_on_radio(id, dependent_id);
        }
        else if (field.type == '3') {
            update_dependent_inputs_on_checkbox(id, dependent_id);
        }
        else if (field.type == '6') {
            update_dependent_inputs_on_dropdown(id, dependent_id);
        }

        update_dependent_inputs(dependent_id);
    })
}

function update_dependent_inputs_on_radio(parent_id, dependent_id) {
    const d_field = state.form[`field_${dependent_id}`];
    const selected_el = document.querySelector(`input[name="radio_${parent_id}"]:checked`);

    if (!selected_el) {
        const radio_btns = document.querySelectorAll(`.livechat-form-radio-btn_${parent_id}`);
        radio_btns.forEach(btn => {
            const key = btn.value;
            update_choices(`field_${parent_id}`, d_field, key, dependent_id, false);
        })
    } else {
        update_choices(`field_${parent_id}`, d_field, selected_el.value, dependent_id, true);
    }
}

function update_dependent_inputs_on_checkbox(parent_id, dependent_id) {
    const checkbox_btns = document.querySelectorAll(`.livechat-form-checkbox_${parent_id}`);
    const d_field = state.form[`field_${dependent_id}`];

    const checked_btns = Array.from(checkbox_btns).filter((value, index, arr) => {
        return value.checked;
    })

    let custom_field = {
        checked_boxes: [],
        ...d_field
    }

    let checked = false;
    if (checked_btns.length > 0) {
        checked_btns.forEach(btn => {
            const key = btn.value;
            if(Array.isArray(d_field[key])) {
                custom_field.checked_boxes.push(...d_field[key])
            }
        })

        checked = true;
    }
        
    const key = 'checked_boxes';
    update_choices(`field_${parent_id}`, custom_field, key, dependent_id, checked);
}

function update_dependent_inputs_on_dropdown(parent_id, dependent_id) {
    const elem = document.querySelector(`#input-element_${parent_id}`);
    const options = elem.options;
    const d_field = state.form[`field_${dependent_id}`];

    if (elem.value == '0') {
        Array.from(options).forEach(option => {
            const key = option.value;
            update_choices(`field_${parent_id}`, d_field, key, dependent_id, false);
        })
    } else {
        update_choices(`field_${parent_id}`, d_field, elem.value, dependent_id, true);
    }
}

function update_choices(parent_id, d_field, key, dependent_id, checked) {
    let all_keys;
    if(state.form[parent_id].dependent) {
        all_keys = state.form[parent_id].all_options;
    } else {
        all_keys = state.form[parent_id].values;
    }

    if (d_field.type == '2') {
        update_radio_choices(all_keys, parent_id, d_field, key, dependent_id, checked);
    }
    else if (d_field.type == '3') {
        update_checkbox_choices(all_keys, parent_id, d_field, key, dependent_id, checked);
    }
    else if (d_field.type == '6') {
        update_dropdown_choices(all_keys, parent_id, d_field, key, dependent_id, checked);
    }
}

function update_checkbox_choices(all_keys, parent_id, field, key, id, is_selected) {
    if (!Array.isArray(field[key])) {
        field[key] = [];
    }

    const elems = document.querySelectorAll(`#input-element_${id} .checkbox-btn-container-item`);

    let options_hidden = 0;
    elems.forEach(elem => {
        const value = elem.dataset.value;

        const is_connected = get_relation_between_two_fields(field, value, key, parent_id);

        if (!is_connected) {
            if (elem.style.display == 'none') {
                ++options_hidden;
            }
            return;
        }

        if (is_selected && field[key].includes(value)) {
            elem.style.display = 'flex';
        } else {
            let is_option_hidden = true;
            if (!is_selected) {
                is_option_hidden = update_choice_based_parent(value, field, elem);
            }

            if (is_option_hidden) {
                ++options_hidden;
                document.getElementById(value).checked = false;
                elem.style.display = 'none';
            }
        }
    })

    if (options_hidden == elems.length) {
        document.getElementById(`input-element_${id}`).style.display = 'none';
    } else {
        document.getElementById(`input-element_${id}`).style.display = 'block';
    }
}

function update_radio_choices(all_keys, parent_id, field, key, id, is_selected) {
    if (!Array.isArray(field[key])) {
        field[key] = [];
    }

    const elems = document.querySelectorAll(`#input-element_${id} .radio-btn-container-item`);
    
    let options_hidden = 0;
    elems.forEach(elem => {
        const value = elem.dataset.value;

        const is_connected = get_relation_between_two_fields(field, value, key, parent_id);

        if (!is_connected) {
            if (elem.style.display == 'none') {
                ++options_hidden;
            }
            return;
        }

        if (is_selected && field[key].includes(value)) {
            elem.style.display = 'flex';
        } else {
            let is_option_hidden = true;
            if (!is_selected) {
                is_option_hidden = update_choice_based_parent(value, field, elem);
            }

            if (is_option_hidden) {
                ++options_hidden;
                document.getElementById(value).checked = false;
                elem.style.display = 'none';
            }
        }
    })

    if (options_hidden == elems.length) {
        document.getElementById(`input-element_${id}`).style.display = 'none';
    } else {
        document.getElementById(`input-element_${id}`).style.display = 'block';
    }
}

function update_dropdown_choices(all_keys, parent_id,  field, key, id, is_selected) {
    if (!Array.isArray(field[key])) {
        field[key] = [];
    }

    const elem = document.querySelector(`#input-element_${id}`);
    const options = elem.options;

    let all_options_hidden = true;
    Array.from(options).forEach(option => {
        const value = option.value;
        
        const is_connected = get_relation_between_two_fields(field, value, key, parent_id);

        if (!is_connected) {
            return;
        }

        if (is_selected && field[key].includes(value)) {
            option.style.display = 'block';
        } else {
            let is_option_hidden = true;
            if (!is_selected) {
                is_option_hidden = update_choice_based_parent(value, field, option);
            }

            if (is_option_hidden) {
                if (elem.value == option.value) {
                    elem.value = '0';
                }

                if (option.value != '0')
                    option.style.display = 'none';
            }
        }

        if (option.value != '0' && option.style.display != 'none') {
            all_options_hidden = false;
        }
    })

    document.getElementById(`input-element_${id}`).disabled = all_options_hidden ;
}

function get_relation_between_two_fields(field, value, key, parent_id) {
    let field1 = state.option_map[value];
    let field2 = state.option_map[key];

    let is_connected = (field1 == parent_id) || (field1 == field2);

    if (is_connected) return true;

    let connected_fields = []

    let is_traversed = {};
    state.form.field_order.forEach(field_id => {
        is_traversed[field_id] = false;
    })

    get_connected_fields(connected_fields, field1, is_traversed);

    if (key == 'checked_boxes') {
        for (const _key in field) {
            if (_key == '0' || _key == 'dependent_ids' || _key == 'dependent_on_ids' || _key == 'all_options')
                continue
            
            if (Array.isArray(field[_key])) {
                field2 = state.option_map[_key];
                is_connected =  (field1 == field2) || connected_fields.includes(field2);
                
                if (is_connected) return true;
            }
        }

        return false;
    }

    return connected_fields.includes(field2);
}

function get_connected_fields(connected_fields, field_id, is_traversed) {
    if (is_traversed[field_id]) return;

    const field = state.form[field_id];

    if (field && field.dependent_on_ids) {
        for (const id of field.dependent_on_ids) {
            if (!is_traversed[id])
                connected_fields.push(id);
        }
    }

    if (field && field_id.dependent_ids) {
        for (const id of field.dependent_ids) {
            if (!is_traversed[id])
                connected_fields.push(id);
        }
    }

    is_traversed[field_id] = true;

    for (const id of connected_fields) {
        get_connected_fields(connected_fields, id, is_traversed);
    }
}

function update_choice_based_parent(value, field, elem) {
    let field_id = state.option_map[value];
    let is_option_hidden = true;
    if (field_id) {
        let field_key = get_selected_value_based_input_type(field_id);

        if (field_key && field_key != '') {
            if (Array.isArray(field_key)) {
                for (const _key of field_key) {
                    if (field[_key] && field[_key].includes(value)) {
                        elem.style.display = 'flex';
                        is_option_hidden = false;
                        break;
                    }
                }
            } else {
                if (field[field_key] && field[field_key].includes(value)) {
                    elem.style.display = 'flex';
                    is_option_hidden = false;
                }
            }
        }
    }

    return is_option_hidden;
}

function get_selected_value_based_input_type (id) {
    const field = state.form[id];

    if (field) {
        if (field.type == '2') {
            const elem = document.querySelector(`input[name="radio_${id.split('_')[1]}"]:checked`);

            if (elem) {
                return elem.value;
            }

            return "";
        }
        else if (field.type == '3') {
            const checkbox_btns = document.querySelectorAll(`.livechat-form-checkbox_${id.split('_')[1]}`);
        
            let selected_values = [];
            for (const btn of checkbox_btns) {
                if (btn.checked) selected_values.push(btn.value);
            }

            return selected_values;
        }
        else {
            return document.getElementById(`input-element_${id.split('_')[1]}`).value;
        }
    }
}

export function set_form_state(form) {
    state.form = form;
}
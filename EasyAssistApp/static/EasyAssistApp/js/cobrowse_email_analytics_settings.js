$(document).ready(function() {
    $("#enable_email_settings").on("change", function(event) {
        update_profile_tab_container_status();
        save_enable_email_settings_changes();
    });

    $('#add-new-tab-btn').on('click', function (e) {
        add_new_profile_tab();
    });

    document.getElementById("nav-settings-menu").classList.add("active");

    fetch_all_existing_profile(update_profile_tab_container_status);
});

function update_profile_tab_container_status() {
    var enable_email_settings = document.getElementById("enable_email_settings");

    if(enable_email_settings.checked) {
        show_profile_tab_container();
    } else {
        hide_profile_tab_container();
    }
}

function show_profile_tab_container() {
    $("#analytics-profile-container").fadeIn(500);
}

function hide_profile_tab_container() {
    $("#analytics-profile-container").fadeOut(500)
}

class EasyAssistTagElement {
    constructor(element, tag_container) {
        this.element = element;
        this.tag_container = tag_container;
        this.email_id_list = [];

        this.initialize();
    }

    initialize() {
        var _this = this;
        _this.add_event_listeners_in_tag_element();
    }

    add_event_listeners_in_tag_element() {
        var _this = this;

        $(_this.element).on("keypress", function(event) {
            var target = event.target;
            var value = target.value;

            if (event.key === 'Enter' || event.keyCode == 13) {
                let val = value.trim().replace( /(<([^>]+)>)/ig, '');
                if(!check_valid_email(value)) {
                    show_easyassist_toast("Please enter valid email");
                } else {
                    var email_id_exist = _this.email_id_list.some(value => value === val);
                    if(email_id_exist) {
                        show_easyassist_toast('Email ID already exist');
                    } else {
                        _this.email_id_list.push(value);
                        _this.render_email_id_tags();
                    }

                    target.value = "";
                }
            }
        });
    }

    render_email_id_tags() {
        var _this = this;

        function add_event_listener_in_remove_btn() {

            var tag_remove_btns = _this.tag_container.querySelectorAll("[class='tag-remove-btn']");
            tag_remove_btns.forEach(function(tag_remove_btn, index) {
                $(tag_remove_btn).on("click", function() {
                    _this.remove_email_id_tags(index);
                });
            });
        }

        var html = "";
        _this.email_id_list.forEach(function(value, index) {
            html += `
                <li class="bg-primary cognoai-tag">
                    <span style="font-weight: 500;">${value}</span>
                    <span class="tag-remove-btn">x</span>
                </li>`;
        });

        _this.tag_container.innerHTML = html;

        add_event_listener_in_remove_btn();
    }

    remove_email_id_tags(removed_index) {
        var _this = this;

        var updated_email_id_list = [];
        for(var idx = 0; idx < _this.email_id_list.length; idx ++) {
            if(idx == removed_index) {
                continue;
            }
            updated_email_id_list.push(_this.email_id_list[idx]);
        }

        _this.email_id_list = updated_email_id_list;
        _this.render_email_id_tags();
    }

    get_value() {
        var _this = this;
        return _this.email_id_list;
    }

    update_value(email_id_list) {
        var _this = this;
        _this.email_id_list = email_id_list;
        _this.render_email_id_tags();
    }
}

class EasyAssistAdvancedCustomMultiSelect {
/**
   * Advanced multiselect using Bootstrap-muliselect
   * @param  {Object}   select_element  DOM select element
   * @param  {Object}   tag_container   Tag container
   * @Doc    {Document} https://davidstutz.github.io/bootstrap-multiselect/
   */

    constructor(select_element, tag_container) {
        this.element = select_element;
        this.tag_container = tag_container;
        this.initialize();
    }

    initialize() {
        var _this = this;
        $(_this.element).multiselect({
            nonSelectedText: 'Select Records',
            enableFiltering: true,
            enableCaseInsensitiveFiltering: true,
            includeSelectAllOption: true
        });

        _this.add_event_listeners();
    }

    value_change_event_listener() {
        var _this = this;

        function add_event_listener_in_remove_btn() {

            var tag_remove_btns = _this.tag_container.querySelectorAll("[class='selected-item-remove-btn']");
            tag_remove_btns.forEach(function(tag_remove_btn, index) {
                $(tag_remove_btn).on("click", function() {
                    let option_value = tag_remove_btn.getAttribute("data-value");
                    _this.remove_selected_option(option_value);
                });
            });
        }

        var html = "";
        var dropdown_options = $(_this.element).find("option:selected");

        for(var idx = 0; idx < dropdown_options.length; idx ++) {
            var option_text = $(dropdown_options[idx]).text();
            var option_value = $(dropdown_options[idx]).val();
            html += `
            <div class="selected-item">
                <span>${option_text}</span>
                <span class="selected-item-remove-btn" data-value="${option_value}">
                    <svg width="8" height="8" viewBox="0 0 8 8" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M7.15035 0.854978C7.05694 0.761352 6.93011 0.708735 6.79785 0.708735C6.66559 0.708735 6.53877 0.761352 6.44535 0.854978L4.00035 3.29498L1.55535 0.849978C1.46194 0.756352 1.33511 0.703735 1.20285 0.703735C1.07059 0.703735 0.943767 0.756352 0.850352 0.849978C0.655352 1.04498 0.655352 1.35998 0.850352 1.55498L3.29535 3.99998L0.850352 6.44498C0.655352 6.63998 0.655352 6.95498 0.850352 7.14998C1.04535 7.34498 1.36035 7.34498 1.55535 7.14998L4.00035 4.70498L6.44535 7.14998C6.64035 7.34498 6.95535 7.34498 7.15035 7.14998C7.34535 6.95498 7.34535 6.63998 7.15035 6.44498L4.70535 3.99998L7.15035 1.55498C7.34035 1.36498 7.34035 1.04498 7.15035 0.854978Z" fill="black" fill-opacity="0.54"/>
                    </svg>
                </span>
            </div>`;
        }

        _this.tag_container.innerHTML = html;
        add_event_listener_in_remove_btn();
    }

    remove_selected_option(option_value) {
        var _this = this;
        $(_this.element).multiselect('deselect', option_value);
        $(_this.element).trigger("change");
    }

    add_event_listeners() {
        var _this = this;
        $(_this.element).on("change", function() {
            _this.value_change_event_listener(); 
        });

        $(_this.element).trigger("change");
    }

    get_value() {
        var _this = this;
        var data = $(_this.element).val();
        return data;
    }

    update_value(value_list) {
        var _this = this;
        $(_this.element).multiselect("deselectAll", false);
        $(_this.element).multiselect("select", value_list);
        $(_this.element).trigger("change");
    }
}

class EmailAnalyticsProfile {
    constructor(container, profile_tab_element, profile_data) {
        this.profile_container = container;
        this.profile_tab_element = profile_tab_element;

        this.profile_data = profile_data;

        // Profile ID
        // This will be set only in case of existing profile.
        // For all new profiles its value will be null
        this.profile_id = null;

        // EasyAssistTagElement Instance 
        this.email_tag_obj = null;

        // Dropdown Elements
        this.count_variation_dropdown = null;
        this.email_frequency_dropdown = null;
        this.attachment_record_dropdown = null;

        // Table Parameter
        this.table_parameter_keys = [];
        this.graph_parameter_keys = [];

        this.set_profile_id("1234");
        this.initialize();
    }

    initialize() {
        var _this = this;
        _this.create_profile();
    }

    create_profile() {
        var _this = this;
        _this.profile_container.innerHTML = "";
        _this.create_general_parameters();
        _this.create_graphic_parameters();
        _this.create_table_parameters();
        _this.create_attachment_parameters();
        _this.create_save_profile_btn();

        _this.initialize_easyassist_dropdown();
        _this.initialize_tooltip();

        _this.add_event_listeners();
        _this.update_analytics_profile();
    }

    // General Paramters
    create_general_parameters() {
        var _this = this;
        var email_subject = EMAIL_ANALATYICS_DEFAULT_DATA.email_subject;
        var profile_name = _this.profile_tab_element.innerText;
        profile_name = profile_name.trim();

        let html = `
        <div class="row align-items-center">
            <div class="col-md-6 col-sm-12">
                <span class="sub-heading-text-primary">Trigger Settings</span>
            </div>
            <div class="col-md-6 col-sm-12 mt-2 mt-sm-0">
                <button type="button" class="btn btn-primary btn-trigger-email" name="trigger_email_btn" disabled>
                    Trigger Sample Email
                </button>
            </div>
        </div>

        <div class="row align-items-center mt-4">
            <div class="col-md-6 col-sm-12">
                <span class="text">Profile Name</span>
            </div>
            <div class="col-md-6 col-sm-12 mt-2 mt-sm-0">
                <input class="profile-name-input" type="text" name="profile-name" placeholder="Profile Name" value="${profile_name}" autocomplete="off"/>
            </div>
        </div>

        <div class="row align-items-center mt-4">
            <div class="col-md-6 col-sm-12">
                <span class="text">Email Frequency</span>
            </div>
            <div class="col-md-6 col-sm-12 mt-2 mt-sm-0 email-frequency-dropdowm-div">
                <select name="email-frequency-dropdown">
                    <option value="1">Daily</option>
                    <option value="7">7 days</option>
                    <option value="30">30 days</option>
                    <option value="60">60 days</option>
                    <option value="90">90 days</option>
                </select>
            </div>
        </div>

        <div class="row align-items-center mt-4">
            <div class="col-md-6 col-sm-12">
                <span class="text">Email Address</span>
            </div>
            <div class="col-md-6 col-sm-12 mt-2 mt-sm-0">
                <ul name="email-id-list" class="email_id_tag_container"></ul>
                <input class="email-id-input" type="text" name="email-id-input" placeholder="Enter email address and hit enter" autocomplete="off"/>
            </div>
        </div>

        <div class="row align-items-center mt-4">
            <div class="col-md-6 col-sm-12">
                <span class="text">Email Subject</span>
            </div>
            <div class="col-md-6 col-sm-12 mt-2 mt-sm-0">
                <input class="email-subject-input" type="text" name="email-subject" placeholder="Email Subject" value="${email_subject}"/>
            </div>
        </div>

        <div class="row mt-2">
            <div class="col-md-12 col-sm-12">
                <hr />
            </div>
        </div>`;

        _this.profile_container.innerHTML += html;
    }

    // Graphic Container 
    create_graphic_parameters() {
        var _this = this;

        function get_graphhic_option_html(categories) {
            let html = "";
            categories.forEach(function(data, index) {
                var sub_categories = data.categories;
                var category_name = data.name;
                var category_id = data.id;
                var is_enabled = data.is_enabled;

                var sub_categories_html = _this.get_option_html(sub_categories);
                html += `
                    <optgroup data-label="${category_name}" data-value="${category_id}" data-selected="${is_enabled}">
                        ${sub_categories_html}
                    </optgroup>
                `;
            });

            return html;
        }

        function get_graphic_record_html() {
            let html = "";
            var records_analytics_graph = EMAIL_ANALATYICS_DEFAULT_DATA.records_analytics_graph;
            records_analytics_graph.forEach(function(record_data, index) {
                var record_name = record_data.name;
                var record_id = record_data.id;
                var is_enabled = record_data.is_enabled;
                var categories = record_data.categories;
                var cb_status = "";

                if(is_enabled) {
                    cb_status = "checked";
                }

                var subcategory_option_html = get_graphhic_option_html(categories);

                html += `
                    <div class="row align-items-center mt-4 px-3">
                        <div class="col-md-6 col-sm-12">
                            <label class="graphic-parameter-label easyassist-switch-checkbox-label">
                                <input type="checkbox" name="${record_id}-graph-paramter-cb" ${cb_status}/>
                                <span class="easyassist-switch-checkbox"></span>
                                <span class="text">${record_name}</span>
                            </label>
                        </div>
                        <div class="col-md-6 col-sm-12 mt-2 mt-sm-0">
                            <div class="easyassist-group-select" name="${record_id}-dropdown-container">
                                <select name="${record_id}-graph-subcategory-dropdown" multiple data-hide-disabled="false">
                                    ${subcategory_option_html}
                                </select>
                            </div>
                        </div>
                    </div>`;

                _this.graph_parameter_keys.push({
                    "record_id": record_id,
                    "record_value_obj": null,
                });
            });

            return html;
        }

        var graphic_record_html = get_graphic_record_html();

        var html = `
        <div class="row align-items-center mt-1">
            <div class="col-8 col-md-6">
                <span class="text-primary heading-text-primary">Graphic Parameter</span>
                <span data-toggle="tooltip" data-placement="bottom" title="Only last 7 days data will be displayed on graphs.">
                    <i class="fas fa-info-circle"></i>
                </span>
            </div>
            <div class="col-4 col-md-6">
                <label class="easyassist-option-switch">
                    <input type="checkbox" name="enable-graphic-parameter" checked>
                    <span class="easyassist-option-switch-slider round"></span>
                </label>
            </div>

            <div class="col-md-12 col-sm-12" name="graphic-parameter-container">
                ${graphic_record_html}
            </div>
        </div>
        <div class="row mt-2">
            <div class="col-md-12 col-sm-12">
                <hr />
            </div>
        </div>`;

        _this.profile_container.innerHTML += html;
    }

    // Table Parameter
    create_table_parameters() {
        var _this = this;

        function get_table_record_html() {
            let html = "";
            var records_analytics_table = EMAIL_ANALATYICS_DEFAULT_DATA.records_analytics_table;
            records_analytics_table.forEach(function(record_data, index) {
                var record_id = record_data.id;
                var record_name = record_data.name;
                var is_enabled = record_data.is_enabled;
                var categories = record_data.categories;
                var option_html = _this.get_option_html(categories);
                var cb_status = "";

                if(is_enabled) {
                    cb_status = "checked";
                }

                html += `
                    <div class="row align-items-center mt-4 px-3">
                        <div class="col-md-4 col-sm-12">
                            <label class="table-parameter-label easyassist-switch-checkbox-label">
                                <input type="checkbox" name="${record_id}-table-paramter-cb" ${cb_status}/>
                                <span class="easyassist-switch-checkbox"></span>
                                <span class="text">${record_name}</span>
                            </label>
                        </div>
                        <div class="col-md-4 col-sm-12 mt-2 mt-sm-0">
                            <div class="easyassist-multiselect-dropdown-container" name="${record_id}-dropdown-container">
                                <select name="${record_id}-table-dropdown" multiple>
                                    ${option_html};
                                </select>
                            </div>
                        </div>
                        <div class="col-md-4 col-sm-12 mt-4 mt-md-0">
                            <div class="selected-item-container" name="${record_id}-selected-item-container">

                            </div>
                        </div>
                    </div>`;

                _this.table_parameter_keys.push({
                    "record_id": record_id,
                    "record_value_obj": null,
                });
            });
            return html;
        }

        function get_count_variation_option_html() {
            var count_variation_list = EMAIL_ANALATYICS_DEFAULT_DATA.count_variation_list;
            var option_html = "";
            for(var idx = 0; idx < count_variation_list.length; idx ++) {
                option_html += `<option value="${count_variation_list[idx][0]}">${count_variation_list[idx][1]}</option>`;
            }
            return option_html;
        }

        var table_record_html = get_table_record_html();
        var count_variation_option_html = get_count_variation_option_html();

        var html = `
        <div class="row align-items-center mt-1">
            <div class="col-8 col-md-6">
                <span class="text-primary heading-text-primary">Table Parameter</span>
            </div>
            <div class="col-4 col-md-6">
                <label class="easyassist-option-switch">
                    <input type="checkbox" name="enable-table-parameter" checked>
                    <span class="easyassist-option-switch-slider round"></span>
                </label>
            </div>
            <div class="col-md-12 col-sm-12" name="table-parameter-container">
                <div class="row align-items-center mt-4">
                    <div class="col-md-6 col-sm-12">
                        <span class="text">Count Variations</span>
                    </div>
                    <div class="col-md-6 col-sm-12 mt-2 mt-sm-0 count-variations-dropdown-div">
                        <select name="count-variation-dropdown">
                            ${count_variation_option_html}
                        </select>
                    </div>
                </div>

                <div class="row align-items-center mt-4">
                    <div class="col-md-12 col-sm-12">
                        <span class="text">Record Parameters</span>
                    </div>
                    <div class="col-md-12 col-sm-12 mt-2">
                        ${table_record_html}
                    </div>
                </div>
            </div>
        </div>
        <div class="row mt-2">
            <div class="col-md-12 col-sm-12">
                <hr />
            </div>
        </div>`;

        _this.profile_container.innerHTML += html;
    }

    // Attachment Parameters
    create_attachment_parameters() {
        var _this = this;
        var record_attachments = EMAIL_ANALATYICS_DEFAULT_DATA.record_attachments;
        var record_option_html = _this.get_option_html(record_attachments)
        var html = `
        <div class="row align-items-center mt-1">
            <div class="col-8 col-md-6">
                <span class="text-primary heading-text-primary">Attachment Parameter</span>
            </div>
            <div class="col-4 col-md-6">
                <label class="easyassist-option-switch">
                    <input type="checkbox" name="enable-attachment-parameter" checked>
                    <span class="easyassist-option-switch-slider round"></span>
                </label>
            </div>
            <div class="col-md-12 col-sm-12" name="attachment-parameter-container">
                <div class="row align-items-center mt-2">
                    <div class="col-md-4 col-sm-12">
                        <span class="text">Records</span>
                    </div>
                    <div class="col-md-4 col-sm-12 mt-2 mt-sm-0">
                        <div class="easyassist-multiselect-dropdown-container">
                            <select name="select-record-dropdown" multiple>
                            ${record_option_html}
                            </select>
                        </div>

                        <div class="mt-2">
                            <label class="single-excel-file-label easyassist-switch-checkbox-label">
                                <input type="checkbox" name="single-excel-file-label">
                                <span class="easyassist-switch-checkbox"></span>
                                <span>Send as Single Excel</span>
                            </label>
                        </div>
                    </div>
                    <div class="col-md-4 col-sm-12 mt-4 mt-sm-0">
                        <div class="selected-item-container" name="attachment-selected-item-container">

                        </div>
                    </div>
                </div>
            </div>
        </div>`;

        _this.profile_container.innerHTML += html;
    }

    // Save button
    create_save_profile_btn() {
        var _this = this;
        var html = `
        <div class="row mt-4">
            <div class="col-12 text-right">
                <button type="button" style="background: #10B981!important;" id="save-button" class="btn btn-save-profile btn-width-100">Save</button>
            </div>
        </div>`;

        _this.profile_container.innerHTML += html;
    }

    save_profile_details(element) {
        var _this = this;

        var profile_id = _this.profile_id;

        var profile_name = _this.profile_container.querySelector("[name='profile-name']").value.trim();
        
        if(!profile_name.length) {
            show_easyassist_toast("Please enter profile name to conitue");
            return;
        }

        const profile_name_regex =  /^[^\s][a-zA-Z0-9 _-]+$/

        if(!profile_name_regex.test(profile_name)) {
            show_easyassist_toast("Please enter a valid profile name. Only A-Z, a-z, 0-9, -, _ and space are allowed");
            return;
        }

        let email_frequency = _this.email_frequency_dropdown.get_value();

        if(!email_frequency.length) {
            show_easyassist_toast("Please select email frequency to continue");
            return;
        }

        let email_address_list = _this.email_tag_obj.get_value();
        if(email_address_list.length == 0) {
            show_easyassist_toast("Please enter atleast one email id")
            return;
        }

        var email_subject_element = _this.profile_container.querySelector("[name='email-subject']");
        var email_subject = email_subject_element.value.trim();
        email_subject = stripHTML(email_subject);
        email_subject = remove_special_characters_from_str(email_subject);

        if(!email_subject) {
            show_easyassist_toast("Please enter email subject");
            return;
        }

        var enable_graphic_parameter = _this.profile_container.querySelector("[name='enable-graphic-parameter']").checked;
        var graph_parameter_records = {};
        var invalid_parameter_list = [];

        if(enable_graphic_parameter) {
            _this.graph_parameter_keys.forEach(function(record_obj) {
                var record_id = record_obj.record_id;
                var record_value_obj = record_obj.record_value_obj;
                var is_enabled = _this.profile_container.querySelector(`[name='${record_id}-graph-paramter-cb']`).checked;
                var selected_values = record_value_obj.get_value();
                var total_selected_values = Object.keys(selected_values).length;

                if(is_enabled) {
                    graph_parameter_records[record_id] = selected_values;
                    if(total_selected_values == 0) {
                        invalid_parameter_list.push(record_id);
                    }    
                }
            });
        }

        if(invalid_parameter_list.length > 0) {
            let first_invalid_parameter = invalid_parameter_list[0].split("_").join(' ');
            show_easyassist_toast("Please select valid parameter for " + first_invalid_parameter);
            return;
        }

        var enable_table_parameter = _this.profile_container.querySelector("[name='enable-table-parameter']").checked;
        var count_variation = _this.count_variation_dropdown.get_value();
        var table_parameter_records = {};
        invalid_parameter_list = [];

        if(table_parameter_records) {
            _this.table_parameter_keys.forEach(function(record_obj) {
                var record_id = record_obj.record_id;
                var record_value_obj = record_obj.record_value_obj;
                var is_enabled = _this.profile_container.querySelector(`[name='${record_id}-table-paramter-cb']`).checked;
                var selected_values = record_value_obj.get_value();

                if(is_enabled) {
                    table_parameter_records[record_id] = selected_values;

                    if(selected_values.length == 0) {
                        invalid_parameter_list.push(record_id);
                    }
                }
            });
        }

        if(invalid_parameter_list.length > 0) {
            let first_invalid_parameter = invalid_parameter_list[0].split("_").join(' ');
            show_easyassist_toast("Please select valid parameter for " + first_invalid_parameter);
            return;
        }

        var enable_attacment_parameter = _this.profile_container.querySelector("[name='enable-attachment-parameter']").checked;
        var use_single_file = _this.profile_container.querySelector("[name='single-excel-file-label']").checked;
        var attachment_parameter_records = [];
        if(enable_attacment_parameter) {
            attachment_parameter_records = _this.attachment_record_dropdown.get_value();

            if(attachment_parameter_records.length == 0) {
                show_easyassist_toast("Please select valid attachment records");
                return;
            }
        }

        var request_params = {
            "profile_id": profile_id,
            "profile_name": profile_name,
            "email_frequency": email_frequency,
            "email_address_list": email_address_list,
            "email_subject": email_subject,
            "graphic_parameters": {
                "is_enabled": enable_graphic_parameter,
                "graph_parameter_records": graph_parameter_records,
            },
            "table_parameter": {
                "is_enabled": enable_table_parameter,
                "table_parameter_records": table_parameter_records,
                "count_variation": count_variation,
            },
            "attachment_parameter": {
                "is_enabled": enable_attacment_parameter,
                "use_single_file": use_single_file,
                "attachment_parameter_records": attachment_parameter_records,
            }
        };

        var json_params = JSON.stringify(request_params);
        var encrypted_data = easyassist_custom_encrypt(json_params);
        encrypted_data = {
            "Request": encrypted_data
        };
        var params = JSON.stringify(encrypted_data);
        element.innerHTML = "Saving...";

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/easy-assist/agent/save-email-analytics-profile/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                var response = JSON.parse(this.responseText);
                response = easyassist_custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response.status == 200) {
                    show_easyassist_toast("Profile has been saved successfully");
                    setTimeout(function() {
                        window.location.reload();
                    }, 1000);
                } else if(response.status == 301 ) {
                    show_easyassist_toast("Please enter valid email");
                } else if(response.status == 302 ) {
                    show_easyassist_toast(response.message);
                } else {
                    show_easyassist_toast("Internal Server Error"); 
                }
            }
            element.innerHTML = "Save";
        }
        xhttp.send(params);
    }

    trigger_email() {
        var _this = this;
        if(_this.profile_id == null) {
            show_easyassist_toast("Please save the profile.");
            return;
        }

        var trigger_email_btn = _this.profile_container.querySelector("[name='trigger_email_btn']");
        var profile_id = _this.profile_id;

        var request_params = {
            "profile_id": profile_id,
        };

        var json_params = JSON.stringify(request_params);
        var encrypted_data = easyassist_custom_encrypt(json_params);
        encrypted_data = {
            "Request": encrypted_data
        };
        var params = JSON.stringify(encrypted_data);

        trigger_email_btn.innerText = "Sending...";

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/easy-assist/agent/trigger-email-analytics/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                var response = JSON.parse(this.responseText);
                response = easyassist_custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response.status == 200) {
                    show_easyassist_toast("Analytics email has been sent to you.");
                } else if(response.status == 301) {
                    show_easyassist_toast("Not able to trigger email. Maximum limit exceeded. You can retry after 1 hour.");
                } else if(response.status == 401) {
                    show_easyassist_toast("You are not authorize to perform this operation.");
                } else {
                    show_easyassist_toast("Something went wrong. Please try again");
                }
            }
            trigger_email_btn.innerText = "Trigger Sample Email";
        }
        xhttp.send(params);
    }

    add_event_listeners() {
        var _this = this;
        _this.add_general_parameters_event_listeners();    
        _this.add_graphic_parameters_event_listeners();
        _this.add_table_parameters_event_listeners();
        _this.add_attachment_parameters_event_listeners();
        _this.add_save_btn_event_listener();
    }

    add_general_parameters_event_listeners() {
        var _this = this;
        var trigger_email_btn = _this.profile_container.querySelector("[name='trigger_email_btn']");
        $(trigger_email_btn).on("click", function() {
            _this.trigger_email();
        });

        var email_id_input = _this.profile_container.querySelector("[name='email-id-input']");
        var email_tag_container = _this.profile_container.querySelector("[name='email-id-list']");
        _this.email_tag_obj = new EasyAssistTagElement(email_id_input, email_tag_container);

        var profile_name_input = _this.profile_container.querySelector("[name='profile-name']");
        $(profile_name_input).on("keypress", function(event) {
            var value = event.target.value;
            value = value.trim();

            if(value.length >= 20) {
                show_easyassist_toast("Profile name should not be more than 20 characters long");
                event.preventDefault();
            }
        });

        $(email_id_input).on("keypress", function(event) {
            var value = event.target.value;
            value = value.trim();

            if(value.length >= 100) {
                show_easyassist_toast("Email ID should not be more than 100 characters long");
                event.preventDefault();
            }
        });

        var email_subject = _this.profile_container.querySelector("[name='email-subject']");
        $(email_subject).on("keypress", function(event) {
            var value = event.target.value;
            value = value.trim();

            if(value.length >= 50) {
                show_easyassist_toast("Email subject should not be more than 50 characters long");
                event.preventDefault();
            }
        });
    }

    add_graphic_parameters_event_listeners() {
        var _this = this;
        var enable_graphic_parameter_cb = _this.profile_container.querySelector("[name='enable-graphic-parameter']");
        var graphic_parameter_container = _this.profile_container.querySelector("[name='graphic-parameter-container']");

        $(enable_graphic_parameter_cb).on("change", function(event) {
            if(enable_graphic_parameter_cb.checked) {
                $(graphic_parameter_container).fadeIn(500);
            } else {
                $(graphic_parameter_container).fadeOut(500);
            }
        });

        _this.graph_parameter_keys.forEach(function(record_obj) {
            var record_id = record_obj.record_id;
            var enable_graph_analytics_cb = _this.profile_container.querySelector(`[name='${record_id}-graph-paramter-cb']`);
            $(enable_graph_analytics_cb).on("change", function() {
                var dropdown_container = _this.profile_container.querySelector(`[name='${record_id}-dropdown-container']`);
                if(enable_graph_analytics_cb.checked) {
                    dropdown_container.classList.remove("disabled")
                } else {
                    dropdown_container.classList.add("disabled")
                }
            });
        });
    }


    add_table_parameters_event_listeners() {
        var _this = this;
        var enable_table_parameter_cb = _this.profile_container.querySelector("[name='enable-table-parameter']");
        var table_parameter_container = _this.profile_container.querySelector("[name='table-parameter-container']");

        $(enable_table_parameter_cb).on("change", function(event) {
            if(enable_table_parameter_cb.checked) {
                $(table_parameter_container).fadeIn(500);
            } else {
                $(table_parameter_container).fadeOut(500);
            }
        });

        _this.table_parameter_keys.forEach(function(record_obj) {
            var record_id = record_obj.record_id;
            var enable_table_analytics_cb = _this.profile_container.querySelector(`[name='${record_id}-table-paramter-cb']`);
            $(enable_table_analytics_cb).on("change", function() {
                var dropdown_container = _this.profile_container.querySelector(`[name='${record_id}-dropdown-container']`);
                var selected_item_container = _this.profile_container.querySelector(`[name='${record_id}-selected-item-container']`);

                if(enable_table_analytics_cb.checked) {
                    dropdown_container.classList.remove("disabled");
                    selected_item_container.classList.remove("disabled");
                } else {
                    dropdown_container.classList.add("disabled");
                    selected_item_container.classList.add("disabled");
                }
            });
        });
    }

    add_attachment_parameters_event_listeners() {
        var _this = this;
        var enable_attachment_parameter_cb = _this.profile_container.querySelector("[name='enable-attachment-parameter']");
        var attachment_parameter_container = _this.profile_container.querySelector("[name='attachment-parameter-container']");

        $(enable_attachment_parameter_cb).on("change", function(event) {
            if(enable_attachment_parameter_cb.checked) {
                $(attachment_parameter_container).fadeIn(500);
            } else {
                $(attachment_parameter_container).fadeOut(500);
            }
        });
    }

    add_save_btn_event_listener() {
        var _this = this;

        var save_btn = _this.profile_container.querySelector(".btn-save-profile");
        $(save_btn).on("click", function() {
            _this.save_profile_details(save_btn);
        });
    }

    update_analytics_profile() {
        var _this = this;
        if(!_this.profile_data) {
            return;
        }

        var profile_data = _this.profile_data;
        _this.update_general_settings();
        _this.update_graphic_parameters();
        _this.update_table_parameters();
        _this.update_attachment_parameters();
    }

    update_general_settings() {
        var _this = this;
        var profile_data = _this.profile_data;
        var profile_id = profile_data.pk;
        var profile_name = profile_data.profile_name;
        var email_subject = profile_data.email_subject;
        var email_id_list = profile_data.email_id_list;
        var email_frequency = profile_data.email_frequency;

        _this.profile_id = profile_id;
        _this.profile_container.querySelector("[name='trigger_email_btn']").disabled = false;
        _this.profile_container.querySelector("[name='profile-name']").value = profile_name;
        _this.profile_container.querySelector("[name='email-subject']").value = email_subject;

        _this.email_frequency_dropdown.update_value(email_frequency);
        _this.email_tag_obj.update_value(email_id_list);
    }

    update_graphic_parameters() {
        var _this = this;
        var profile_data = _this.profile_data;
        var graphic_parameters = profile_data.graphic_parameters;

        var enable_graph_parameter_cb = _this.profile_container.querySelector("[name='enable-graphic-parameter']");

        if(graphic_parameters.is_enabled != enable_graph_parameter_cb.checked) {
            enable_graph_parameter_cb.click();
        }

        _this.count_variation_dropdown.update_value(graphic_parameters.count_variation);

        _this.graph_parameter_keys.forEach(function(record_obj) {
            var record_id = record_obj.record_id;
            var dropdown_obj = record_obj.record_value_obj;

            var enable_record_cb = _this.profile_container.querySelector(`[name='${record_id}-graph-paramter-cb']`);

            var is_record_enabled = false;
            if(record_id in graphic_parameters.records) {
                dropdown_obj.update_value(graphic_parameters.records[record_id]);
                is_record_enabled = true;
            }

            if(is_record_enabled != enable_record_cb.checked) {
                enable_record_cb.click();
            }
        });
    }

    update_table_parameters() {
        var _this = this;
        var profile_data = _this.profile_data;
        var table_parameters = profile_data.table_parameters;

        var enable_table_parameter_cb = _this.profile_container.querySelector("[name='enable-table-parameter']");

        if(table_parameters.is_enabled != enable_table_parameter_cb.checked) {
            enable_table_parameter_cb.click();
        }

        _this.count_variation_dropdown.update_value(table_parameters.count_variation);

        _this.table_parameter_keys.forEach(function(record_obj) {
            var record_id = record_obj.record_id;
            var dropdown_obj = record_obj.record_value_obj;

            var enable_record_cb = _this.profile_container.querySelector(`[name='${record_id}-table-paramter-cb']`);

            var is_record_enabled = false;
            if(record_id in table_parameters.records) {
                dropdown_obj.update_value(table_parameters.records[record_id]);
                is_record_enabled = true;
            }

            if(is_record_enabled != enable_record_cb.checked) {
                enable_record_cb.click();
            }
        });
    }

    update_attachment_parameters() {
        var _this = this;
        var profile_data = _this.profile_data;
        var attachment_parameters = profile_data.attachment_parameter;

        var enable_attachment_parameter_cb = _this.profile_container.querySelector("[name='enable-attachment-parameter']");

        if(attachment_parameters.is_enabled != enable_attachment_parameter_cb.checked) {
            enable_attachment_parameter_cb.click();
        }

        _this.profile_container.querySelector("[name='single-excel-file-label']").checked = attachment_parameters.use_single_file;
        _this.attachment_record_dropdown.update_value(attachment_parameters.records)
    }

    set_profile_id(profile_id) {
        var _this = this;

        if(profile_id == null) {
            _this.profile_id = _this.generate_random_profile_id();
        } else {
            _this.profile_id = profile_id;
        }
    }

    generate_random_profile_id() {
        var total_profiles = 1 + 1;
        var profile_id = "new-profile-" + total_profiles;
        return profile_id;
    }

    initialize_easyassist_dropdown() {
        var _this = this;
        var email_frequency_dropdown_selector = '[name="email-frequency-dropdown"]';
        var email_frequency_dropdown = _this.profile_container.querySelector(email_frequency_dropdown_selector);
        _this.email_frequency_dropdown = new EasyassistCustomSelectMultiple(email_frequency_dropdown, null, null);
        
        var count_variation_dropdown_selector = '[name="count-variation-dropdown"]';
        var count_variation_dropdown = _this.profile_container.querySelector(count_variation_dropdown_selector);
        _this.count_variation_dropdown = new EasyassistCustomSelectMultiple(count_variation_dropdown, null, null);

        var select_record_dropdown_selector = '[name="select-record-dropdown"]';
        var select_record_dropdown = _this.profile_container.querySelector(select_record_dropdown_selector);
        var select_record_dropdown_container = _this.profile_container.querySelector('[name="attachment-selected-item-container"]');
        _this.attachment_record_dropdown = new EasyAssistAdvancedCustomMultiSelect(select_record_dropdown, select_record_dropdown_container);

        _this.table_parameter_keys.forEach(function(record_obj) {
            var record_id = record_obj.record_id;
            var table_parameter_dropdown_selector = `[name="${record_id}-table-dropdown"]`;
            var table_parameter_dropdown = _this.profile_container.querySelector(table_parameter_dropdown_selector);
            var table_record_container = _this.profile_container.querySelector(`[name="${record_id}-selected-item-container"]`);
            record_obj.record_value_obj = new EasyAssistAdvancedCustomMultiSelect(table_parameter_dropdown, table_record_container);
        });

        _this.graph_parameter_keys.forEach(function(record_obj) {
            var record_id = record_obj.record_id;
            var table_parameter_dropdown_selector = `[name="${record_id}-graph-subcategory-dropdown"]`;
            var table_parameter_dropdown = _this.profile_container.querySelector(table_parameter_dropdown_selector);
            record_obj.record_value_obj = new EasyassistCustomGroupSelectMultiple(table_parameter_dropdown, "Select Analytics", null);
        });

        $(".dropdown-menu>li .dropdown-item-checkbox").addClass("filter-modal-custom-checkbox");
        $(".dropdown-menu>li").find(".filter-modal-custom-checkbox").append("<span class='filter-custom-checkmark'></span>");

        $(".multiselect-container>li>a>label").addClass("filter-modal-custom-checkbox");
        $(".multiselect-container>li").find(".filter-modal-custom-checkbox").append("<span class='filter-custom-checkmark'></span>");

        $(".easyassist-group-select .dropdown-menu>li>label").addClass("filter-modal-custom-checkbox");
        $(".easyassist-group-select .dropdown-menu>li").find(".filter-modal-custom-checkbox").append("<span class='filter-custom-checkmark'></span>");
    }

    initialize_tooltip() {
        var _this = this;
        var tooltip_elements = _this.profile_container.querySelectorAll("[data-toggle='tooltip']");
        $(tooltip_elements).tooltip();
    }

    get_option_html(data) {
        var option_html = "";
        for(var idx = 0; idx < data.length; idx ++) {
            var selected = "";

            if(data[idx].is_enabled) {
                selected = "selected";
            }

            option_html += `<option value="${data[idx].id}" ${selected}>${data[idx].name}</option>`;
        }

        return option_html;
    }
}

function add_new_profile_tab(profile_data=null) {
    var profile_tab_class = "";

    var next_tab = $('#tabs li').length;
    var profile_name = "Profile " + next_tab;
    var profile_id = null;
    var is_existing_profile = false;

    if(profile_data) {
        profile_name = profile_data.profile_name;
        profile_id = profile_data.pk;
        is_existing_profile = true;
    }

    if(is_existing_profile == false) {
        profile_tab_class = "tab-new-profile";
        var total_new_profiles = document.getElementsByClassName(profile_tab_class).length;
        if(total_new_profiles > 0) {
            show_easyassist_toast("Please save last profile.");
            return;
        }
    } else {
        profile_tab_class = "tab-edit-profile";
    }

    var new_tab_btn_parent = document.getElementById("add-new-tab-btn").parentElement;
    var tab_content_container = document.getElementById("tab-content-container");

    var tab_html =`
        <li class="btn-profile-tab ${profile_tab_class}">
            <a href="#tab${next_tab}" data-toggle="tab">
                <span>${profile_name}</span>
                <button type="button" class="btn-delete-profile" onclick="show_delete_profile_modal(this, '${profile_id}');">
                    <svg width="10" height="11" viewBox="0 0 10 11" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M9.72504 0.61163C9.58492 0.47119 9.39468 0.392266 9.19629 0.392266C8.9979 0.392266 8.80766 0.47119 8.66754 0.61163L5.00004 4.27163L1.33254 0.60413C1.19242 0.46369 1.00218 0.384766 0.803789 0.384766C0.605401 0.384766 0.415163 0.46369 0.275039 0.60413C-0.0174609 0.89663 -0.0174609 1.36913 0.275039 1.66163L3.94254 5.32913L0.275039 8.99663C-0.0174609 9.28913 -0.0174609 9.76163 0.275039 10.0541C0.567539 10.3466 1.04004 10.3466 1.33254 10.0541L5.00004 6.38663L8.66754 10.0541C8.96004 10.3466 9.43254 10.3466 9.72504 10.0541C10.0175 9.76163 10.0175 9.28913 9.72504 8.99663L6.05754 5.32913L9.72504 1.66163C10.01 1.37663 10.01 0.89663 9.72504 0.61163Z" fill="#0254D7"/>
                    </svg>
                </button>
            </a>
        </li>`;

    new_tab_btn_parent.insertAdjacentHTML("beforebegin", tab_html);

    var new_tab = document.createElement("div");
    new_tab.classList.add("tab-pane");
    new_tab.setAttribute("id", 'tab'+next_tab);

    tab_content_container.appendChild(new_tab);
    $('#tabs a[href="#tab' + next_tab + '"]').tab('show');

    var profile_tab_btn = $(`#tabs a[href="#tab${next_tab}"]`).parent()[0];

    var new_profile = new EmailAnalyticsProfile(new_tab, profile_tab_btn, profile_data);
}

function check_and_add_new_profile() {
    var total_profiles = $('#tabs li').length - 1;
    if(total_profiles == 0) {
        add_new_profile_tab();
    }
}

function fetch_all_existing_profile(callback=null) {
    var request_params = {};
    var json_params = JSON.stringify(request_params);
    var encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/get-all-email-analytics-profiles/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if (response.status == 200) {
                 var analytics_profiles = response["analytics_profiles"];
                 render_existing_profiles(analytics_profiles);
            } else {
                show_easyassist_toast("Internal Server Error"); 
            }

            if(callback != null) {
                callback();
            }
        }
    }
    xhttp.send(params);
}

function render_existing_profiles(analytics_profiles) {
    if(analytics_profiles.length == 0) {
        check_and_add_new_profile();
        return;
    }

    analytics_profiles.forEach(function(profile) {
        add_new_profile_tab(profile);
    });

    $("#tabs li").children('a').first().click();
}

function show_delete_profile_modal(element, profile_id) {
    window.DELETED_PROFILE_TAB = element;

    $("#delete-email-analytics-profile-modal").modal("show");
    document.getElementById("delete-profile-modal-btn").setAttribute("data-profile-id", profile_id);
}

function remove_profile_tab() {
    var li_element = DELETED_PROFILE_TAB.closest("li");
    var anchor_element = li_element.querySelector("a");
    $($(anchor_element).attr('href')).remove();
    $(li_element).remove();

    $("#tabs li").children('a').first().click();
}

function delete_mailer_analytics_profile() {
    var profile_id = document.getElementById("delete-profile-modal-btn").getAttribute("data-profile-id");
    if(profile_id == null || profile_id == "null") {
        remove_profile_tab();
    } else {
        delete_existing_profile(profile_id);
    }

    $("#delete-email-analytics-profile-modal").modal("hide");
}

function delete_existing_profile(profile_id) {
    var request_params = {
        "profile_id": profile_id,
    };
    var json_params = JSON.stringify(request_params);
    var encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/delete-email-analytics-profile/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if (response.status == 200) {
                show_easyassist_toast("Mailer analytics profile deleted successfully.");
                remove_profile_tab();
            } else {
                show_easyassist_toast("Something went wrong. Please try again"); 
            }
        }
    }
    xhttp.send(params);
}

function save_enable_email_settings_changes() {
    var enable_email_settings = document.getElementById("enable_email_settings").checked;
    var request_params = {
        "enable_email_settings": enable_email_settings,
    };

    var json_params = JSON.stringify(request_params);
    var encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/save-enable-email-settings/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if (response.status == 200) {
                if(enable_email_settings == true) {
                    show_easyassist_toast("Mailer Analytics has been enabled");
                } else {
                    show_easyassist_toast("Mailer Analytics has been disabled");
                }
            } else if(response.status == 401) {
                show_easyassist_toast("You are not authorized to perform this operation.");
            } else {
                show_easyassist_toast("Something went wrong. Please try again"); 
            }
        }
    }
    xhttp.send(params);
}
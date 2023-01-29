function add_new_form_category() {
    var form_category_el = document.getElementById('form-category');
    var new_category_id = Date.now()

    var html = [
        '<li class="dropdown-list" id="form-category-list-' + new_category_id + '">',
            '<div style="display: inline-block;">',
                '<input type="text" value="New Section" id="form-category-name-' + new_category_id + '" class="form-category-input" onmouseup="select_category_value(this)" onkeyup="update_category_name(this.value, \'' + new_category_id + '\')"/>',
            '</div>',
            '<div class="form-category-action-btn">',
                '<button class="btn" type="button" role="group" data-toggle="collapse" data-target="#edit-category-' + new_category_id + '">',
                    '<svg width="17" height="17" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">',
                        '<path d="M9.84202 0.713396C10.7932 -0.237799 12.3354 -0.237799 13.2866 0.713396C14.1982 1.62496 14.2361 3.07929 13.4005 4.03608L13.2866 4.15798L4.8794 12.5652C4.6999 12.7447 4.48395 12.8826 4.24688 12.9699L4.10223 13.0162L0.553236 13.9841C0.249894 14.0668 -0.0302313 13.8143 0.00263139 13.5162L0.0159031 13.4468L0.98381 9.89777C1.0506 9.65287 1.16969 9.42602 1.33219 9.23255L1.43482 9.1206L9.84202 0.713396ZM9.08915 2.70443L2.0537 9.73947C1.97292 9.82025 1.909 9.91578 1.86519 10.0205L1.82819 10.1281L1.06094 12.9381L3.87194 12.1718C3.94541 12.1518 4.01564 12.1223 4.08095 12.0844L4.17504 12.0213L4.26053 11.9463L11.2956 4.91086L9.08915 2.70443ZM12.6677 1.33227C12.0922 0.756725 11.1789 0.72475 10.5658 1.23635L10.4609 1.33227L9.70793 2.08565L11.9144 4.29208L12.6677 3.5391C13.2433 2.96356 13.2753 2.05028 12.7637 1.43721L12.6677 1.33227Z" fill="#212121"/>',
                    '</svg>',
                '</button>',
                '<button class="btn" type="button" data-toggle="modal" data-target="#delete-category-modal-' + new_category_id + '">',
                    '<svg width="17" height="19" viewBox="0 0 12 14" fill="none" xmlns="http://www.w3.org/2000/svg">',
                        '<path d="M6 0C7.20256 0 8.18476 0.926865 8.24688 2.09313L8.25 2.21053H11.55C11.7985 2.21053 12 2.40846 12 2.65263C12 2.87645 11.8307 3.06143 11.6111 3.0907L11.55 3.09474H10.9146L10.1827 11.9681C10.088 13.1159 9.11217 14 7.94004 14H4.05996C2.88783 14 1.91205 13.1159 1.81732 11.9681L1.0848 3.09474H0.45C0.222183 3.09474 0.0339053 2.92841 0.00410786 2.71262L0 2.65263C0 2.42881 0.169292 2.24384 0.388938 2.21456L0.45 2.21053H3.75C3.75 0.989686 4.75736 0 6 0ZM10.012 3.09474H1.98796L2.71438 11.8967C2.77121 12.5853 3.35668 13.1158 4.05996 13.1158H7.94004C8.64332 13.1158 9.22879 12.5853 9.28562 11.8967L10.012 3.09474ZM4.65 5.30526C4.87782 5.30526 5.06609 5.47159 5.09589 5.68738L5.1 5.74737V10.4632C5.1 10.7073 4.89853 10.9053 4.65 10.9053C4.42218 10.9053 4.23391 10.7389 4.20411 10.5231L4.2 10.4632V5.74737C4.2 5.5032 4.40147 5.30526 4.65 5.30526ZM7.35 5.30526C7.57782 5.30526 7.76609 5.47159 7.79589 5.68738L7.8 5.74737V10.4632C7.8 10.7073 7.59853 10.9053 7.35 10.9053C7.12218 10.9053 6.93391 10.7389 6.90411 10.5231L6.9 10.4632V5.74737C6.9 5.5032 7.10147 5.30526 7.35 5.30526ZM6 0.88421C5.28548 0.88421 4.70061 1.42957 4.65311 2.11972L4.65 2.21053H7.35L7.34689 2.11972C7.29939 1.42957 6.71452 0.88421 6 0.88421Z" fill="#212121"/>',
                    '</svg>',
                '</button>',
            '</div>',
            '<input type="hidden" value="' + new_category_id + '" name="form-category-id">',
        '</li>',
        '<div class="modal fade" id="delete-category-modal-' + new_category_id + '" tabindex="-1" role="dialog" aria-labelledby="apply_filter_modal_modal_label" aria-hidden="true">',
            '<div class="modal-dialog" role="document">',
                '<div class="modal-content">',
                    '<div class="modal-header">',
                        '<h5 class="modal-title" id="apply_filter_modal_modal_label">Delete Section</h5>',
                    '</div>',
                    '<div class="modal-body">',
                        'Do you really want to delete this section?',
                    '</div>',
                    '<div class="modal-footer">',
                        '<button class="btn btn-secondary" type="button" data-dismiss="modal">Cancel</button>',
                        '<button class="btn btn-danger" onclick="delete_form_category(\'' + new_category_id + '\')">Delete</button>',
                    '</div>',
                '</div>',
            '</div>',
        '</div>',
        '<div id="edit-category-' + new_category_id + '" class="collapse edit-form-category-container">',
            '<div class="row">',
                '<div class="col-12" style="padding: 0">',
                    '<div class="card edit-category-container">',
                        '<div class="card-body">',
                            '<div class="row">',
                                '<div class="col-md-9 col-sm-12">',
                                    '<div style="vertical-align: middle">',
                                        'Please add your question in <span class="category_name">New Section</span>',
                                    '</div>',
                                '</div>',
                                '<div class="col-md-3 col-sm-12 text-right mt-sm" style="padding: 0">',
                                    '<button class="btn add-new-question-btn" onclick="add_new_question(\'' + new_category_id + '\')">',
                                        '+ Add new question',
                                    '</button>',
                                '</div>',
                            '</div>',
                        '</div>',
                    '</div>',
                '</div>',
            '</div>',
            '<div class="row" id="question-container-' + new_category_id + '">',
            '</div>',
        '</div>',
    ].join('');

    $(form_category_el).append(html);
    if($("#form-category-dropdown").hasClass('collapsed') == true) {
        document.getElementById("form-category-dropdown").click();
    }
}

function add_new_question(category_id) {
    var new_question_id = Date.now();
    html = [
        '<div class="col-12 mb-3" style="padding: 0;" id="form-question-' + new_question_id + '">',
            '<div class="card add-question-container">',
                '<div class="card-body">',
                    '<div class="row">',
                        '<div class="col-md-7 col-sm-12" style="padding: 0" id="form-category-question-field-' + new_question_id + '">',
                        '<div class="question-text">Add question</div>',
                            '<div class="mt-3">',
                                '<input class="cobrowse-form-input" placeholder="Label" type="text" id="question-label-' + new_question_id + '"/>',
                            '</div>',
                            '<div id="question-option-container-' + new_question_id + '">',
                            '</div>',
                            '<div class="mt-4">',
                                '<input type="checkbox" class="mandatory-checkbox" id="mandatory-checkbox-' + new_question_id + '"/>',
                                '<label for="mandatory-checkbox-' + new_question_id + '">Mandatory Field</label>',
                            '</div>',
                        '</div>',
                        '<div class="col-md-5 col-sm-12 mt-sm" style="padding: 0">',
                            '<div class="question-text">Choose Input Type</div>',
                            '<div class="mt-3">',
                                '<select class="selectpicker" id="question-type-' + new_question_id + '" onchange="update_form_category_question_field(this.value,\'' + new_question_id + '\')">',
                                    '<option value="text">Text</option>',
                                    '<option value="number">Number</option>',
                                    '<option value="radio">Radio</option>',
                                    '<option value="checkbox">Checkbox</option>',
                                    '<option value="dropdown">Dropdown</option>',
                                '</select>',
                            '</div>', 
                        '</div>',
                    '</div>',
                '</div>',
                '<div class="remove-question-container">',
                    '<button class="btn" type="button" onclick="remove_form_category_question(\'' + new_question_id + '\')">',
                        '<svg width="11" height="10" viewBox="0 0 11 10" fill="none" xmlns="http://www.w3.org/2000/svg">',
                            '<path d="M11 1.23576L9.64067 0L5.5 3.76424L1.35933 0L0 1.23576L4.14067 5L0 8.76424L1.35933 10L5.5 6.23576L9.64067 10L11 8.76424L6.85933 5L11 1.23576Z" fill="#757575"/>',
                        '</svg>',
                    '</button>',
                '</div>',
                '<input type="hidden" name="form-question-id" value="' + new_question_id + '" />',
            '</div>',
        '</div>',
    ].join('');

    $("#question-container-" + category_id).append(html);
    $('#question-type-' + new_question_id).trigger('change');
    $('#form-question-' + new_question_id).find('#question-type-' + new_question_id).selectpicker();
}

function update_category_name(value, category_id) {
    var edit_category_container = document.getElementById('edit-category-' + category_id);
    $(edit_category_container).find('.category_name').html(value);
}

function update_form_category_question_field(value, question_id) {

    var html = "";
    if(value == 'text' || value == 'number') {
        $("#question-option-container-" + question_id).html(html);
    } else if(value == 'radio' || value == 'checkbox' || value == 'dropdown') {
        if($("#question-option-container-" + question_id).find('.question_options_list').length == 0) {
            html = [
                 '<div class="mt-3">',
                    '<ul class="question_options_list" style="padding: 0;" id="question-options-' + question_id + '"></ul>',
                    '<input class="question-options-input cobrowse-form-input" placeholder="Options" type="text" />',
                '</div>',
            ].join('');
            $("#question-option-container-" + question_id).html(html);
            $('#question-option-container-' + question_id + ' .question-options-input').on('keypress', function(e) {
                if (e.key === 'Enter' || e.keyCode==13) {
                    let val = e.target.value.trim().replace( /(<([^>]+)>)/ig, '');
                    if (val !== '') {
                        let option_already_exist = false;
                        $(e.target).parent().find('ul').find('.question-option-text').each(function(_, option_text_el) {
                            if($(option_text_el).html().trim() == val) {
                                option_already_exist = true;
                                return;
                            }
                        });
                        if(option_already_exist) {
                            alert("Option already exist.");
                        } else {
                            render_question_options(e.target);
                        }
                        e.target.value = '';
                        e.target.focus();
                    } else {
                        alert('Options cannot be empty');
                    }
                }
            });
        }
    }
}

function remove_form_category_question(question_id) {
    document.getElementById("form-question-" + question_id).remove();
}

function remove_existing_form_category_question(question_id) {

    var request_params = {
        'question_id': question_id,
    };

    json_params = JSON.stringify(request_params);
    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/sales-ai/delete-cobrowse-form-category-question/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                show_toast("Form Question deleted successfully");
                $("#delete-question-modal-" + question_id).modal('hide');
                remove_form_category_question(question_id);
            } else if(response.status == 300) {
                $("#delete-question-modal-" + question_id).modal('hide');
                show_toast("Form Question does not exist");
            } else {
                $("#delete-question-modal-" + question_id).modal('hide');
                show_toast("Internal server error. Please try again");
            }
        }
    }
    xhttp.send(params);
}

function render_question_options(el) {
    html = [
        '<li class="question-option-li">',
            '<span style="font-weight: bold;" class="question-option-text">',
                el.value,
            '</span>',
            '<span style="color:white;cursor: pointer;font-weight: bold;float: right;margin-left:0.5em;"onclick=" remove_question_option(this)">',
            'x',
            '</span>',
        '</li>'
    ].join('');
    $(el).parent().find('ul').append(html);
}

function remove_question_option(el) {
    $(el).closest('li').remove();
}

function delete_form_category(category_id) {

    document.getElementById("form-category-list-" + category_id).remove();
    document.getElementById("edit-category-" + category_id).remove();
    $("#delete-category-modal-" + category_id).modal('hide');

    setTimeout(function() {
        document.getElementById("delete-category-modal-" + category_id).remove();
    }, 1000);
}

function delete_existing_form_category(category_id) {

    var request_params = {
        'category_id': category_id,
    };

    json_params = JSON.stringify(request_params);
    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/sales-ai/delete-cobrowse-form-category/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                show_toast("Form Category deleted successfully");
                delete_form_category(category_id);
            } else if(response.status == 300) {
                show_toast("Form Category does not exist");
                $("#delete-category-modal-" + category_id).modal('hide');
            } else {
                show_toast("Internal server error. Please try again");
                $("#delete-category-modal-" + category_id).modal('hide');
            }
        }
    }
    xhttp.send(params);
}

function create_form(el) {

    var form_name = document.getElementById("form-name").value.trim();
    form_name = stripHTML(form_name);
    form_name = remove_special_characters_from_str(form_name);

    if(form_name == "") {
        show_toast("Please enter valid form name");
        return;
    }

    var selected_product_categories = "None";
    if($('#product-category').length) {
        selected_product_categories = $('#product-category').val();
    }

    if(selected_product_categories != "None" && selected_product_categories.length == 0) {
        show_toast("Please choose a product categories")
        return;
    }

    var all_fields_valid = true;
    var form_data = [];

    var form_category_container = document.getElementById("form-category");
    $(form_category_container).find('.dropdown-list').each(function(idx, category_list) {
        var category_id = $(category_list).find('input[name="form-category-id"]').val();
        var category_name = document.getElementById("form-category-name-" + category_id).value.trim();
        category_name = stripHTML(category_name);
        category_name = remove_special_characters_from_str(category_name);

        if(category_name == '') {
            all_fields_valid = false;
            show_toast("Please enter valid category name");
            return;
        }

        var category_data = {
            'category_name': category_name,
            'questions': [],
        };

        var question_container = document.getElementById("question-container-" + category_id);
        $(question_container).find('.add-question-container').each(function(_, question_list) {
            var question_id = $(question_list).find('input[name="form-question-id"]').val();
            var question_type = $('#question-type-' + question_id).val();
            var question_label = stripHTML($('#question-label-' + question_id).val().trim());
            question_label = remove_special_characters_from_str(question_label);
            var is_mandatory = $("#mandatory-checkbox-" + question_id).prop('checked');
            var question_choices = [];

            if(question_label == '') {
                all_fields_valid = false;
                show_toast("Please enter valid question label");
                return;
            }

            if(question_type == 'checkbox' || question_type == 'radio' || question_type == 'dropdown') {
                $('#question-options-' + question_id).find('.question-option-text').each(function(_, option_el) {
                    var question_choice = $(option_el).html().trim();
                    question_choice = stripHTML(question_choice);
                    question_choice = remove_special_characters_from_str(question_choice);
                    question_choices.push(question_choice);
                });

                if(question_choices.length == 0) {
                    all_fields_valid = false;
                    show_toast("Please enter valid question options");
                    return;
                } 
            }

            var question_data = {
                'question_type': question_type,
                'question_label': question_label,
                'question_choices': question_choices,
                'is_mandatory': is_mandatory,
            };

            category_data['questions'].push(question_data);
        });

        form_data.push(category_data);
    });

    if(all_fields_valid == false) {
        return;
    }

    var request_params = {
        'form_name': form_name,
        'product_categories': selected_product_categories,
        'form_data': form_data,
    };

    json_params = JSON.stringify(request_params);
    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/sales-ai/create-cobrowse-form/?salesforce_token="+SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                show_toast("Form created successfully");
                setTimeout(function() {
                    window.location.reload();
                }, 1000);
            } else {
                show_toast("Internal server error. Please try again");
            }
        }
    }
    xhttp.send(params);

}

function save_form(el) {

    var form_id = document.getElementById("form-id").value;
    var form_name = document.getElementById("form-name").value.trim();
    form_name = stripHTML(form_name);
    form_name = remove_special_characters_from_str(form_name);

    if(form_name == "") {
        show_toast("Please enter valid form name");
        return;
    }

    var all_fields_valid = true;
    var form_data = [];

    var form_category_container = document.getElementById("form-category");
    $(form_category_container).find('.dropdown-list').each(function(idx, category_list) {
        var category_id = $(category_list).find('input[name="form-category-id"]').val();
        var category_name = document.getElementById("form-category-name-" + category_id).value.trim();
        category_name = stripHTML(category_name);
        category_name = remove_special_characters_from_str(category_name);

        if(category_name == '') {
            all_fields_valid = false;
            show_toast("Please enter valid category name");
            return;
        }

        var category_data = {
            'category_id': category_id,
            'category_name': category_name,
            'questions': [],
        };

        var question_container = document.getElementById("question-container-" + category_id);
        $(question_container).find('.add-question-container').each(function(_, question_list) {
            var question_id = $(question_list).find('input[name="form-question-id"]').val();
            var question_type = $('#question-type-' + question_id).val();
            var question_label = stripHTML($('#question-label-' + question_id).val().trim());
            question_label = remove_special_characters_from_str(question_label);
            var is_mandatory = $("#mandatory-checkbox-" + question_id).prop('checked');
            var question_choices = [];

            if(question_label == '') {
                all_fields_valid = false;
                show_toast("Please enter valid question label");
                return;
            }

            if(question_type == 'checkbox' || question_type == 'radio' || question_type == 'dropdown') {
                $('#question-options-' + question_id).find('.question-option-text').each(function(_, option_el) {
                    var question_choice = $(option_el).html().trim();
                    question_choice = stripHTML(question_choice);
                    question_choice = remove_special_characters_from_str(question_choice);
                    question_choices.push(question_choice);
                });

                if(question_choices.length == 0) {
                    all_fields_valid = false;
                    show_toast("Please enter valid question options");
                    return;
                } 
            }

            var question_data = {
                'question_id': question_id,
                'question_type': question_type,
                'question_label': question_label,
                'question_choices': question_choices,
                'is_mandatory': is_mandatory,
            };

            category_data['questions'].push(question_data);
        });

        form_data.push(category_data);
    });

    if(all_fields_valid == false) {
        return;
    }

    var request_params = {
        'form_id': form_id,
        'form_name': form_name,
        'form_data': form_data,
    };

    json_params = JSON.stringify(request_params);
    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/sales-ai/save-cobrowse-form/?salesforce_token="+SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                show_toast("Form saved successfully");
                setTimeout(function() {
                    window.location.reload();
                }, 1000);
            } else {
                show_toast("Internal server error. Please try again");
            }
        }
    }
    xhttp.send(params);

}

function show_toast(message) {
    document.getElementById("toast_message").innerHTML = message
    $('.toast').toast('show');
}

function stripHTML(text){
   var regex = /(<([^>]+)>)/ig;
   return text.replace(regex, "");
}

function remove_special_characters_from_str(text) {
    var symobols_to_remove = [
        '/', '\\', ':', ';', "'", '"', '=', "-", "$", "*", "%", "!", "@", "~",
        "'", "^", "(", ")", "{", "}", "[", "]", "#", "<", ">"];
    for(var idx = 0; idx < symobols_to_remove.length; idx ++) {
        text = text.replaceAll(symobols_to_remove[idx], "")
    }
    return text;
}

function select_category_value(el) {

    $(el).select();
}
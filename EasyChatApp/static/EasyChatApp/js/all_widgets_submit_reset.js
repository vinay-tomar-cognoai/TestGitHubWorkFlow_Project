function remove_submit_reset_btn_div() {
    $(".bot-widget-submit-reset-btn-wrapper").remove()
}

function reset_radio_btn() {
    $('input[name=radio_button]:checked').prop('checked', false)
    if ($(".radio-div .radio-item").hasClass("radio-item-active")) {
        $(".radio-div .radio-item").removeClass("radio-item-active")
    }

    $("#user_input").val("")
    $("#user_input").text("")
}

function reset_checkbox_btn(element) {
    var parent_element = element.closest(".easychat-check-box-container");
    $('#' + parent_element.id + ' input[class=checkbox-input]:checked').prop('checked', false)
    if ($(".checkbox-div .checkbox-item").hasClass("checkbox-item-active")) {
        $(".checkbox-div .checkbox-item").removeClass("checkbox-item-active")
    }
    toggle_checkbox_submit_button(parent_element);
    toggle_checkbox_reset_btn(parent_element);
}


function reset_dropdown_btn() {

    $(".selected-dropdown").html(DROPDOWN_TEXT)
    $("#selected-blue-radio-dropdown").removeAttr("id")
    $(".radio-dropdown").prop("checked", false)
    $("#user_input").val("")
    $("#user_input").text("")
}


function reset_single_range_slider_btn(single_range_slider_id) {
    document.getElementById("single-slider-error-div-" + single_range_slider_id).style.display = "none";
    var single_slider = $('#easychat-single-range-input-' + single_range_slider_id)
    single_slider.val(single_slider.prop('max'))
    change_single_range_slider_values(single_range_slider_id)
}

function form_reset_single_range_slider_btn(single_range_slider_id) {
    document.getElementById("single-slider-error-div-" + single_range_slider_id).style.display = "none";
    var single_slider = $('#easychat-single-range-input-' + single_range_slider_id)
    single_slider.val(single_slider.prop('max'))
    form_change_single_range_slider_values(single_range_slider_id)
}

function reset_multi_range_slider_btn(multi_range_slider_id) {
    document.getElementById("multi-slider-error-div-" + multi_range_slider_id).style.display = "none";
    var multi_range_slider = $("#easychat-bot-multi-range-slider-" + multi_range_slider_id + " .js-range-slider")
    var min_value = parseInt(document.getElementById("multi-range-slider-min-max-static-value-" + multi_range_slider_id).children[0].innerText);
    var max_value = parseInt(document.getElementById("multi-range-slider-min-max-static-value-" + multi_range_slider_id).children[1].innerText);
    
    document.querySelector("#easychat-bot-range-min-selected-value-" + multi_range_slider_id).value = min_value;
    document.querySelector("#easychat-bot-range-max-selected-value-" + multi_range_slider_id).value = max_value;

    multi_range_slider.data("ionRangeSlider").update({
        from: min_value,
        to: max_value
    })
}

function form_reset_multi_range_slider_btn(multi_range_slider_id) {
    document.getElementById("multi-slider-error-div-" + multi_range_slider_id).style.display = "none";
    var multi_range_slider = $("#easychat-bot-multi-range-slider-" + multi_range_slider_id + " .js-range-slider")
    var min_value = parseInt(document.getElementById("multi-range-slider-min-max-static-value-" + multi_range_slider_id).children[0].innerText);
    var max_value = parseInt(document.getElementById("multi-range-slider-min-max-static-value-" + multi_range_slider_id).children[1].innerText);
    
    document.querySelector("#easychat-bot-range-min-selected-value-" + multi_range_slider_id).value = min_value;
    document.querySelector("#easychat-bot-range-max-selected-value-" + multi_range_slider_id).value = max_value;

    multi_range_slider.data("ionRangeSlider").update({
        from: min_value,
        to: max_value
    })
}

function reset_file_attachment_btn(choosen_file_type, is_flow_ended, input_id) {
    var file_extension = document.getElementById("easychat-uploadfile__XPS-" + input_id).value.split(".")[document.getElementById("easychat-uploadfile__XPS-" + input_id).value.split(".").length - 1].toLowerCase();

    if (file_extension.indexOf("png") != -1 || file_extension.indexOf("mp4") != -1 || file_extension.indexOf("jpeg") != -1 || file_extension.indexOf("jpg") != -1 || file_extension.indexOf("gif") != -1) {
        previewImg.style.display = "none";
    }

    if (file_extension.indexOf("mp4") != -1) {
        document.querySelector("#preview-img-" + input_id).style.display = "none";
    }

    document.getElementById("easychat-uploadfile__XPS-" + input_id).value = "";
    document.querySelector("#easychat-upload-file-container-" + input_id).style.display = "none";
    document.querySelector("#easychat-dragdropContainer__XPS-" + input_id + " .easychat-attachment-dragdrop-wrapper").style.display = "flex";
    document.querySelector("#submit-cancel-btns-wrapper-" + input_id + " .easychat-bot-widget-submit-btn").classList.add("easychat-widget-disabled");
    document.querySelector("#submit-cancel-btns-wrapper-" + input_id + " .easychat-bot-widget-reset-btn").classList.add("easychat-widget-disabled");
}

function cancel_dropdown_btn(ele) {
    ele.parentElement.parentElement.parentElement.classList.add("easychat-widget-disabled");
    update_input_placeholder_based_on_theme(get_placeholder_text_based_on_theme());
    enable_user_input();
    empty_user_input_based_on_theme();
}

function send_dropdown_user_input(ele) {

    if (!ele.parentElement.parentElement.querySelector(".selected-dropdown")) {
        return;
    }

    var dropdown_value = ele.parentElement.parentElement.querySelector(".selected-dropdown").innerText.trim();
    if (!dropdown_value.length) {
        return;
    }
    ele.parentElement.parentElement.parentElement.remove();
    update_input_placeholder_based_on_theme(get_placeholder_text_based_on_theme());
    empty_user_input_based_on_theme();
    send_user_input(dropdown_value);
}

function send_radio_button_user_input(ele) {
    if (!ele.parentElement.parentElement.querySelector("input:checked")) {
        return;
    }

    var radio_button_value = ele.parentElement.parentElement.querySelector("input:checked").value.trim();

    if (!radio_button_value.length) {
        return;
    }
    ele.parentElement.parentElement.remove();
    update_input_placeholder_based_on_theme(get_placeholder_text_based_on_theme());
    send_user_input(radio_button_value);
}

function cancel_radio_btn(ele) {
    var radio_widget_id = ele.closest(".easychat-radio-button-container").id;

    $("#" + radio_widget_id + " .radio-item").removeClass("radio-item-active");
    if (document.querySelector("#" + radio_widget_id + " .radio-input:checked")) {
        document.querySelector("#" + radio_widget_id + " .radio-input:checked").checked = false;
    }
    ele.parentElement.parentElement.classList.add("easychat-widget-disabled");
    empty_user_input_based_on_theme(); 
    update_input_placeholder_based_on_theme(get_placeholder_text_based_on_theme());
    enable_user_input();
}

function get_placeholder_text_based_on_theme() {
    if (EASYCHAT_BOT_THEME == "theme_1") {
        return EASYCHAT_INPUT_QUERY_THEME_1_PLACEHOLDER
    } else if (EASYCHAT_BOT_THEME == "theme_2") {
        return EASYCHAT_INPUT_QUERY_THEME_2_PLACEHOLDER
    } else {
        return EASYCHAT_INPUT_QUERY_THEME_3_PLACEHOLDER
    }
}

function update_input_placeholder_based_on_theme(placeholder) {
    if (EASYCHAT_BOT_THEME == "theme_1" || EASYCHAT_BOT_THEME == "theme_2") {
        document.getElementById("user_input").placeholder = placeholder;
    } else {
        document.getElementById('user_input_placeholder_text').innerText = placeholder;
    }
}

function toggle_checkbox_submit_button(element) {
    var parent_element = element.closest(".easychat-check-box-container");
    if (parent_element.querySelectorAll("input:checked").length) {
        parent_element.querySelector(".easychat-bot-widget-submit-btn").classList.remove("easychat-widget-disabled");
    } else {
        parent_element.querySelector(".easychat-bot-widget-submit-btn").classList.add("easychat-widget-disabled");
    }
}

function send_checkbox_user_input(element) {
    var checked_inputs = element.closest(".easychat-check-box-container").querySelectorAll("input:checked");
    if (!checked_inputs.length) {
        return;
    }

    var checked_input_list = [];
    for (var i=0; i<checked_inputs.length; i++) {
        checked_input_list.push(checked_inputs[i].value);
    }

    element.closest(".easychat-check-box-container").remove();
    send_user_input(checked_input_list.join(","));
    update_input_placeholder_based_on_theme(get_placeholder_text_based_on_theme());
}

function cancel_checkbox_btn(element) {
    var parent_element = element.closest(".easychat-check-box-container");
    reset_checkbox_btn(parent_element);
    parent_element.classList.add("easychat-widget-disabled");
    update_input_placeholder_based_on_theme(get_placeholder_text_based_on_theme());
    enable_user_input();
    empty_user_input_based_on_theme();
}

function toggle_checkbox_reset_btn(element) {
    var checkbox_widget = element.closest(".easychat-check-box-container");
    if (checkbox_widget.querySelectorAll("input:checked").length) {
        checkbox_widget.querySelector(".easychat-bot-widget-reset-btn").classList.remove("easychat-widget-disabled");
    } else {
        checkbox_widget.querySelector(".easychat-bot-widget-reset-btn").classList.add("easychat-widget-disabled");
    }
}

function reset_phone_widget_input(phone_widget_id) {
    document.getElementById("country_phone_number_" + phone_widget_id).value = "";
    reset_phone_widget("country_phone_number_" + phone_widget_id, document.getElementById("country-code-error-message-div-" + phone_widget_id));
    document.querySelector("#easychat-country-code-submit-btn-wrapper-" + phone_widget_id + " .easychat-bot-widget-submit-btn").classList.add("easychat-widget-disabled");
}

function cancel_phone_widget(phone_widget_id) {
    reset_phone_widget_input(phone_widget_id);
    document.getElementById("easychat-country-code-submit-btn-wrapper-" + phone_widget_id).classList.add("easychat-widget-disabled");
    update_input_placeholder_based_on_theme(get_placeholder_text_based_on_theme());
    enable_user_input();
    empty_user_input_based_on_theme();
}

function update_multi_range_slider(multi_range_slider_id) {
    var min_value = parseInt(document.getElementById("multi-range-slider-min-max-static-value-" + multi_range_slider_id).children[0].innerText);
    var max_value = parseInt(document.getElementById("multi-range-slider-min-max-static-value-" + multi_range_slider_id).children[1].innerText);
    var from_value = parseInt(document.getElementById("easychat-bot-range-min-selected-value-" + multi_range_slider_id).value);
    var to_value = parseInt(document.getElementById("easychat-bot-range-max-selected-value-" + multi_range_slider_id).value);

    var error_div = document.getElementById("multi-slider-error-div-" + multi_range_slider_id);
    error_div.style.display = "none";

    var submit_btn = document.querySelector("#easychat-bot-multi-range-slider-" + multi_range_slider_id + " .easychat-bot-widget-submit-btn");

    var error = "";
    
    if (!from_value) {
        if (error != "") {
            error += "<br>";
        }
        error += RANGE_SLIDER_ERROR_MESSAGES.split("$$$")[3];
    }

    if (!to_value) {
        if (error != "") {
            error += "<br>";
        }
        error += RANGE_SLIDER_ERROR_MESSAGES.split("$$$")[4];
    }

    if (from_value < min_value) {
        if (error != "") {
            error += "<br>";
        }
        error += RANGE_SLIDER_ERROR_MESSAGES.split("$$$")[5];
    }

    if (from_value > max_value) {
        if (error != "") {
            error += "<br>";
        }
        error += RANGE_SLIDER_ERROR_MESSAGES.split("$$$")[6];
    }

    if (to_value > max_value) {
        if (error != "") {
            error += "<br>";
        }
        error += RANGE_SLIDER_ERROR_MESSAGES.split("$$$")[7];
    }

    if (to_value < min_value) {
        if (error != "") {
            error += "<br>";
        }
        error += RANGE_SLIDER_ERROR_MESSAGES.split("$$$")[8];
    }

    if (from_value > to_value) {
        if (error != "") {
            error += "<br>";
        }
        error += RANGE_SLIDER_ERROR_MESSAGES.split("$$$")[9];
    }

    if (error) {
        error_div.innerHTML = error;
        error_div.style.display = "block";
        submit_btn.classList.add("easychat-widget-disabled");
    } else {

        if (document.getElementsByTagName("body")[0].classList.contains("language-right-to-left-wrapper")) {
            var temp_to_value = to_value
            to_value = max_value - (from_value - min_value);
            from_value = max_value - (temp_to_value - min_value);
        }

        $("#easychat-bot-multi-range-slider-" + multi_range_slider_id + " .js-range-slider").data("ionRangeSlider").update({
            from: from_value,
            to: to_value
        });
        submit_btn.classList.remove("easychat-widget-disabled");
    }
}

function form_update_multi_range_slider(multi_range_slider_id) {
    var min_value = parseInt(document.getElementById("multi-range-slider-min-max-static-value-" + multi_range_slider_id).children[0].innerText);
    var max_value = parseInt(document.getElementById("multi-range-slider-min-max-static-value-" + multi_range_slider_id).children[1].innerText);
    var from_value = parseInt(document.getElementById("easychat-bot-range-min-selected-value-" + multi_range_slider_id).value);
    var to_value = parseInt(document.getElementById("easychat-bot-range-max-selected-value-" + multi_range_slider_id).value);

    var error_div = document.getElementById("multi-slider-error-div-" + multi_range_slider_id);
    error_div.style.display = "none";

    var error = "";
    
    if (!from_value) {
        if (error != "") {
            error += "<br>";
        }
        error += RANGE_SLIDER_ERROR_MESSAGES.split("$$$")[3];
    }

    if (!to_value) {
        if (error != "") {
            error += "<br>";
        }
        error += RANGE_SLIDER_ERROR_MESSAGES.split("$$$")[4];
    }

    if (from_value < min_value) {
        if (error != "") {
            error += "<br>";
        }
        error += RANGE_SLIDER_ERROR_MESSAGES.split("$$$")[5];
    }

    if (from_value > max_value) {
        if (error != "") {
            error += "<br>";
        }
        error += RANGE_SLIDER_ERROR_MESSAGES.split("$$$")[6];
    }

    if (to_value > max_value) {
        if (error != "") {
            error += "<br>";
        }
        error += RANGE_SLIDER_ERROR_MESSAGES.split("$$$")[7];
    }

    if (to_value < min_value) {
        if (error != "") {
            error += "<br>";
        }
        error += RANGE_SLIDER_ERROR_MESSAGES.split("$$$")[8];
    }

    if (from_value > to_value) {
        if (error != "") {
            error += "<br>";
        }
        error += RANGE_SLIDER_ERROR_MESSAGES.split("$$$")[9];
    }

    if (error) {
        error_div.innerHTML = error;
        error_div.style.display = "block";
    } else {

        if (document.getElementsByTagName("body")[0].classList.contains("language-right-to-left-wrapper")) {
            var temp_to_value = to_value
            to_value = max_value - (from_value - min_value);
            from_value = max_value - (temp_to_value - min_value);
        }

        $("#easychat-bot-multi-range-slider-" + multi_range_slider_id + " .js-range-slider").data("ionRangeSlider").update({
            from: from_value,
            to: to_value
        });
    }
}

function update_single_range_slider(single_range_slider_id) {
    var single_range_slider_ele = document.getElementById("easychat-single-range-input-" + single_range_slider_id)
    var min_value = parseInt(single_range_slider_ele.min);
    var max_value = parseInt(single_range_slider_ele.max);
    var value = parseInt(document.getElementById("easychat-bot-range-selected-value-" + single_range_slider_id).value);

    var error = ""
    var error_div = document.getElementById("single-slider-error-div-" + single_range_slider_id);
    error_div.style.display = "none";

    var submit_btn = document.querySelector("#easychat-bot-single-range-slider-" + single_range_slider_id + " .easychat-bot-widget-submit-btn");

    if (value < min_value) {
        if (error != "") {
            error += "<br>"
        }
        error += RANGE_SLIDER_ERROR_MESSAGES.split("$$$")[0];
    }

    if (value > max_value) {
        if (error != "") {
            error += "<br>"
        }
        error += RANGE_SLIDER_ERROR_MESSAGES.split("$$$")[1];
    }

    if (!value) {
        if (error != "") {
            error += "<br>"
        }
        error += RANGE_SLIDER_ERROR_MESSAGES.split("$$$")[2];
    }

    if (error) {
        error_div.innerHTML = error;
        error_div.style.display = "block";
        submit_btn.classList.add("easychat-widget-disabled");
    } else {
        single_range_slider_ele.value = value;
        change_single_range_slider_values(single_range_slider_id);
        submit_btn.classList.remove("easychat-widget-disabled");
    }
}

function form_update_single_range_slider(single_range_slider_id) {
    var single_range_slider_ele = document.getElementById("easychat-single-range-input-" + single_range_slider_id)
    var min_value = parseInt(single_range_slider_ele.min);
    var max_value = parseInt(single_range_slider_ele.max);
    var value = parseInt(document.getElementById("easychat-bot-range-selected-value-" + single_range_slider_id).value);

    var error = ""
    var error_div = document.getElementById("single-slider-error-div-" + single_range_slider_id);
    error_div.style.display = "none";

    if (value < min_value) {
        if (error != "") {
            error += "<br>"
        }
        error += RANGE_SLIDER_ERROR_MESSAGES.split("$$$")[0];
    }

    if (value > max_value) {
        if (error != "") {
            error += "<br>"
        }
        error += RANGE_SLIDER_ERROR_MESSAGES.split("$$$")[1];
    }

    if (!value) {
        if (error != "") {
            error += "<br>"
        }
        error += RANGE_SLIDER_ERROR_MESSAGES.split("$$$")[2];
    }

    if (error) {
        error_div.innerHTML = error;
        error_div.style.display = "block";
    } else {
        single_range_slider_ele.value = value;
        form_change_single_range_slider_values(single_range_slider_id);
    }
}

function cancel_and_reset_form_submission(form_id) {
    reset_all_form_elements(form_id);
    document.getElementById("easychat-form-container-" + form_id).classList.add("easychat-widget-disabled");
    update_input_placeholder_based_on_theme(get_placeholder_text_based_on_theme());
    enable_user_input();
    empty_user_input_based_on_theme();
    answers_filled = {};
}

function form_reset_file_attach(parent_id) {
    var file_attach_parent_div = document.getElementById(parent_id)
    file_attach_parent_div.querySelector("input").value = "";
    answers_filled[parent_id].value = "";
    if (file_attach_parent_div.querySelector(".easychat-form-widget-file-alert")) {
        file_attach_parent_div.querySelector(".easychat-form-widget-file-alert").innerHTML = "";
        file_attach_parent_div.querySelector(".easychat-form-widget-file-alert").style.display = "none";
    }
    file_attach_parent_div.querySelector(".easychat-dragdropafterSelect__XPS").style.display = "none";
    file_attach_parent_div.querySelector(".easychat-dragdropMsg__XPS").style.display = "flex";
    file_attach_parent_div.querySelector(".easychat-attachment-dragdrop-wrapper").style.display = "block";
    file_attach_parent_div.querySelector(".form-uploaded-file").style.display = "none";
    file_attach_parent_div.querySelector(".easychat-dragdropafterSelect__XPS div").style.display = "none";
}

function form_reset_date_picker(parent_id) {
    var date_inputs = document.querySelectorAll("#" + parent_id + " input");
    var label = LABEL_ADD;

    for (var i=0; i<date_inputs.length; i++) {
        if (date_inputs.length > 1 && i==0) {
            label = LABEL_FROM;
        } else if (date_inputs.length > 1 && i==1) {
            label = LABEL_TO;
        }

        date_inputs[i].value = label + " " + LABEL_DATE;
        date_inputs[i].style.opacity = "100";
        date_inputs[i].nextElementSibling.style.visibility = "hidden";
    }
}

function form_reset_time_picker(parent_id) {
    var time_inputs = document.querySelectorAll("#" + parent_id + " input");
    var label = LABEL_ADD;

    for (var i=0; i<time_inputs.length; i++) {
        if (time_inputs.length > 1 && i==0) {
            label = LABEL_FROM;
        } else if (time_inputs.length > 1 && i==1) {
            label = LABEL_TO;
        }

        time_inputs[i].value = label + " " + LABEL_TIME;
    }
}

function form_reset_phone_number(parent_id) {
    document.getElementById("country_phone_number_input-" + parent_id.split("-")[parent_id.split("-").length - 1]).value = "";
}

function reset_all_form_elements(form_id) {
    var inp_id = "";
    var parent_id = ""
    for (var i=0; i<form_fields.length; i++) {
        var inp_id = form_id + "_" + form_fields[i].field_id_num;
        var parent_id = "parent-input-" + inp_id
        if (form_fields[i].input_type == "text_field") {
            document.getElementById("input-" + inp_id).value = "";
        } else if (form_fields[i].input_type == "dropdown_list") {
            document.getElementById("input-" + inp_id).selectedIndex = 0;
            $('#input-' + inp_id).select2({
                width: "100%",
                placeholder: DROPDOWN_TEXT,
                allowClear: true,
            });
        } else if (form_fields[i].input_type == "checkbox") {
            var checked_checkboxes = document.getElementById(parent_id).querySelectorAll("input:checked");
            for (var j=0; j<checked_checkboxes.length; j++) {
                checked_checkboxes[j].checked = false;
                checked_checkboxes[j].parentElement.classList.remove("checkbox-item-active");
            }
        } else if (form_fields[i].input_type == "radio") {
            var radio_checkboxes = document.getElementById(parent_id).querySelectorAll("input:checked");
            for (var j=0; j<radio_checkboxes.length; j++) {
                radio_checkboxes[j].checked = false;
                radio_checkboxes[j].parentElement.classList.remove("radio-item-active");
            }
        } else if (form_fields[i].input_type == "range") {
            if (form_fields[i].range_type == "Single Range Selector") {
                form_reset_single_range_slider_btn("input-" + inp_id);
            } else {
                form_reset_multi_range_slider_btn("input-" + inp_id)
            }
        } else if (form_fields[i].input_type == "file_attach") {
            form_reset_file_attach(parent_id);
        } else if (form_fields[i].input_type == "date_picker") {
            form_reset_date_picker(parent_id);
        } else if (form_fields[i].input_type == "time_picker") {
            form_reset_time_picker(parent_id);
        } else if (form_fields[i].input_type == "phone_number") {
            form_reset_phone_number(parent_id);
        }

        answers_filled[parent_id].value = "";
    }
}

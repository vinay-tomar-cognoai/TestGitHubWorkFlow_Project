/* GLOBAL VARIABLES */

var is_email_frequency_dropdown_open = false;
var added_emails = [];
var is_profile_edited = false;
var profile_id = '';
var is_mailer_profile_modal_opened = false;
var selected = document.querySelector(".selected");
var dropdown = document.querySelector(".wrapper-box");
var optionsContainer = document.querySelector(".email-frequency-options-container");

var optionsList = document.querySelectorAll(".option");
var checkList = document.querySelectorAll(".item-checkbox");
let count = 0;
var checkedItems = new Set();
let open = false;

/* GLOBAL VARIABLES ENDS */

$('#channel_selection_div .table_parameter_channels_checkbox').change(() => {
    let selected_channels = get_selected_items(document.querySelectorAll('.table_parameter_channels_checkbox'))
    if (selected_channels.has("WhatsApp")) {
        $('#customer_initiated_div, #business_initiated_div').css('display', 'inline-flex')
    } else {
        $('#customer_initiated_div, #business_initiated_div').hide()
        $('#customer_initiated_div input, #business_initiated_div input').prop('checked', false)
    }
})

function applyCross() {
    document.querySelectorAll(".cross-btn").forEach((eachCrossBtn) => {
        eachCrossBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            if (document.querySelector(`._${e.target.name}`))
                document.querySelector(`._${e.target.name}`).remove();
            checkedItems.delete(`${e.target.name}`);
            document.getElementById(`myCheck${e.target.name}`).checked = false;
            if (checkedItems.size === 0)
                selected.innerHTML = "Select Frequency";
                selected.style.padding = '10px';
        });
    });
}

function makeCheckArray() {
    checkList.forEach((c) => {
        if (c.checked == true) checkedItems.add(c.getAttribute("name"));
        else checkedItems.delete(c.getAttribute("name"));
    });
}

function makeSpans(text) {
    var span = document.createElement("SPAN");
    span.innerHTML = `<span>${text}</span><img class='cross-btn' name='${text}' src='img/cross.svg' alt='cross' />`;
    span.classList.add("tag", `_${text}`);
    selected.appendChild(span);
    applyCross();
}

function hideIcon(self) {
    self.style.backgroundImage = "none";
}

$("#enable_table_parameter_cb").on("change", function(event) {
    if (this.checked) {
        $(".email-analytics-toggleable-table-parameter-div").fadeIn(500);

    } else {
        $('.email-analytics-toggleable-table-parameter-div').fadeOut(500);


    }
});
$("#enable_graphic_parameter_cb").on("change", function(event) {
    if (this.checked) {
        $(".email-analytics-toggleable-graphic-parameter-div").fadeIn(500);

    } else {
        $('.email-analytics-toggleable-graphic-parameter-div').fadeOut(500);


    }
});
$("#enable_attachment_parameter_cb").on("change", function(event) {
    if (this.checked) {
        $(".email-analytics-toggleable-attachment-parameter-div").fadeIn(500);

    } else {
        $('.email-analytics-toggleable-attachment-parameter-div').fadeOut(500);


    }
});


function create_custom_traffic_analytics_dropdown() {
    $("#email-traffic-analytics-dropdown .easychat-console-select-drop").each(function(i, select) {
        if (!$(this).next().hasClass('easychat-dropdown-select-custom')) {
            $(this).after('<div class="easychat-dropdown-select-custom wide ' + ($(this).attr('class') || '') + '" tabindex="0"><span id="traffic-analytics-current-select" class="current"></span><div class="list"><ul></ul></div></div>');
            var dropdown = $(this).next();

            var options = $(select).find('span');

            var selected = $(this).find('easychat-console-language-option:selected');

            dropdown.find('#traffic-analytics-current-select.current').html(selected.data('display-text') || selected.text());
            options.each(function(j, o) {

                var display = $(o).data('display-text') || '';
                dropdown.find('ul').append('<li class="easychat-console-language-option ' + ($(o).is(':selected') ? 'selected' : '') + '" data-value="' + $(o).data("value") + '" data-display-text="' + display + '">' + $(o).text() + '</li>');
            });
        }

        // $("#email-flow-completion-rate-dropdown ul li:eq(" + 0 + ")").addClass('easychat-lang-selected');

        $('#traffic-analytics-current-select').html("Select Traffic Analytics");

    });

    $('#email-traffic-analytics-dropdown .easychat-dropdown-select-custom ul').before('<div class="dd-search"> <svg class="drop-language-search-icon" width="15" height="14" viewBox="0 0 15 14" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M13.1875 12.0689L9.88352 8.76489C10.6775 7.81172 11.0734 6.58914 10.9889 5.35148C10.9045 4.11382 10.3461 2.95638 9.42994 2.11993C8.51381 1.28349 7.31047 0.83244 6.07025 0.86062C4.83003 0.8888 3.64842 1.39404 2.77123 2.27123C1.89404 3.14842 1.3888 4.33003 1.36062 5.57025C1.33244 6.81047 1.78349 8.01381 2.61993 8.92994C3.45638 9.84607 4.61382 10.4045 5.85148 10.4889C7.08914 10.5734 8.31172 10.1775 9.26489 9.38352L12.5689 12.6875L13.1875 12.0689ZM2.25002 5.68752C2.25002 4.90876 2.48095 4.14748 2.91361 3.49996C3.34627 2.85244 3.96122 2.34776 4.6807 2.04974C5.40019 1.75172 6.19189 1.67375 6.95569 1.82568C7.71949 1.97761 8.42108 2.35262 8.97175 2.90329C9.52242 3.45396 9.89743 4.15555 10.0494 4.91935C10.2013 5.68315 10.1233 6.47485 9.8253 7.19433C9.52728 7.91382 9.0226 8.52877 8.37508 8.96143C7.72756 9.39409 6.96628 9.62502 6.18752 9.62502C5.14358 9.62386 4.14274 9.20865 3.40457 8.47047C2.66639 7.7323 2.25118 6.73145 2.25002 5.68752Z" fill="#909090"/></svg><input id="txtSearchValuetraffic" autocomplete="off" placeholder="Search Categories" onkeyup="filter_traffic_analytics()" class="dd-searchbox" type="text"></div>');


    $('.easychat-dropdown-select-custom ul li:last').after('<div class="custom-drop-nodata-found-div">No result found</div> ');




}

$(document).on('click', '#email-traffic-analytics-dropdown .easychat-dropdown-select-custom .easychat-console-language-option', function(event) {

    $(this).closest('.list').find('.easychat-lang-selected').removeClass('easychat-lang-selected');
    $(this).addClass('easychat-lang-selected');

    var text = $(this).data('display-text') || $(this).text();
    $(this).closest('.easychat-dropdown-select-custom').find('#traffic-analytics-current-select').text(text);
    $(this).closest('.easychat-dropdown-select-custom').prev('select').val($(this).data('value')).trigger('change');


});
//}

function filter_traffic_analytics() {
    var valThis = $('#txtSearchValuetraffic').val();
    $('#email-traffic-analytics-dropdown .easychat-dropdown-select-custom ul > li').each(function() {
        var text = $(this).text();
        (text.toLowerCase().indexOf(valThis.toLowerCase()) > -1) ? $(this).show(): $(this).hide();

        if ($('#email-traffic-analytics-dropdown .easychat-dropdown-select-custom ul').children(':visible').not('#email-traffic-analytics-dropdown .custom-drop-nodata-found-div').length === 0) {
            $('#email-traffic-analytics-dropdown .custom-drop-nodata-found-div').show();
        } else {
            $('#email-traffic-analytics-dropdown .custom-drop-nodata-found-div').hide();
        }

    });
};

// traffic analytics dropdown

// intent analytics dropdown
function create_custom_intent_analytics_dropdown() {
    $("#email-intent-analytics-dropdown .easychat-console-select-drop").each(function(i, select) {
        if (!$(this).next().hasClass('easychat-dropdown-select-custom')) {
            $(this).after('<div class="easychat-dropdown-select-custom wide ' + ($(this).attr('class') || '') + '" tabindex="0"><span id="intent-analytics-current-select" class="current"></span><div class="list"><ul></ul></div></div>');
            var dropdown = $(this).next();

            var options = $(select).find('span');

            var selected = $(this).find('easychat-console-language-option:selected');

            dropdown.find('#intent-analytics-current-select.current').html(selected.data('display-text') || selected.text());
            options.each(function(j, o) {

                var display = $(o).data('display-text') || '';
                dropdown.find('ul').append('<li class="easychat-console-language-option ' + ($(o).is(':selected') ? 'selected' : '') + '" data-value="' + $(o).data("value") + '" data-display-text="' + display + '">' + $(o).text() + '</li>');
            });
        }

        // $("#email-flow-completion-rate-dropdown ul li:eq(" + 0 + ")").addClass('easychat-lang-selected');

        $('#intent-analytics-current-select').html("Select Intent Analytics");

    });

    $('#email-intent-analytics-dropdown .easychat-dropdown-select-custom ul').before('<div class="dd-search"> <svg class="drop-language-search-icon" width="15" height="14" viewBox="0 0 15 14" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M13.1875 12.0689L9.88352 8.76489C10.6775 7.81172 11.0734 6.58914 10.9889 5.35148C10.9045 4.11382 10.3461 2.95638 9.42994 2.11993C8.51381 1.28349 7.31047 0.83244 6.07025 0.86062C4.83003 0.8888 3.64842 1.39404 2.77123 2.27123C1.89404 3.14842 1.3888 4.33003 1.36062 5.57025C1.33244 6.81047 1.78349 8.01381 2.61993 8.92994C3.45638 9.84607 4.61382 10.4045 5.85148 10.4889C7.08914 10.5734 8.31172 10.1775 9.26489 9.38352L12.5689 12.6875L13.1875 12.0689ZM2.25002 5.68752C2.25002 4.90876 2.48095 4.14748 2.91361 3.49996C3.34627 2.85244 3.96122 2.34776 4.6807 2.04974C5.40019 1.75172 6.19189 1.67375 6.95569 1.82568C7.71949 1.97761 8.42108 2.35262 8.97175 2.90329C9.52242 3.45396 9.89743 4.15555 10.0494 4.91935C10.2013 5.68315 10.1233 6.47485 9.8253 7.19433C9.52728 7.91382 9.0226 8.52877 8.37508 8.96143C7.72756 9.39409 6.96628 9.62502 6.18752 9.62502C5.14358 9.62386 4.14274 9.20865 3.40457 8.47047C2.66639 7.7323 2.25118 6.73145 2.25002 5.68752Z" fill="#909090"/></svg><input id="txtSearchValueintent" autocomplete="off" placeholder="Search Categories" onkeyup="filter_intent_analytics()" class="dd-searchbox" type="text"></div>');


    $('.easychat-dropdown-select-custom ul li:last').after('<div class="custom-drop-nodata-found-div">No result found</div> ');




}

$(document).on('click', '#email-intent-analytics-dropdown .easychat-dropdown-select-custom .easychat-console-language-option', function(event) {

    $(this).closest('.list').find('.easychat-lang-selected').removeClass('easychat-lang-selected');
    $(this).addClass('easychat-lang-selected');

    var text = $(this).data('display-text') || $(this).text();
    $(this).closest('.easychat-dropdown-select-custom').find('#intent-analytics-current-select').text(text);
    $(this).closest('.easychat-dropdown-select-custom').prev('select').val($(this).data('value')).trigger('change');

    //update_form_widget(event, this)
});
//}

function filter_intent_analytics() {
    var valThis = $('#txtSearchValueintent').val();
    $('#email-intent-analytics-dropdown .easychat-dropdown-select-custom ul > li').each(function() {
        var text = $(this).text();
        (text.toLowerCase().indexOf(valThis.toLowerCase()) > -1) ? $(this).show(): $(this).hide();

        if ($('#email-intent-analytics-dropdown .easychat-dropdown-select-custom ul').children(':visible').not('#email-intent-analytics-dropdown .custom-drop-nodata-found-div').length === 0) {
            $('#email-intent-analytics-dropdown .custom-drop-nodata-found-div').show();
        } else {
            $('#email-intent-analytics-dropdown .custom-drop-nodata-found-div').hide();
        }

    });
};

// intent analytics dropdown



// flow completion dropdown
function create_custom_flow_completion_dropdown() {
    $("#email-flow-completion-rate-dropdown .easychat-console-select-drop").each(function(i, select) {
        if (!$(this).next().hasClass('easychat-dropdown-select-custom')) {
            $(this).after('<div class="easychat-dropdown-select-custom wide ' + ($(this).attr('class') || '') + '" tabindex="0"><span id="flow-completion-current-select" class="current"></span><div class="list"><ul></ul></div></div>');
            var dropdown = $(this).next();

            var options = $(select).find('span');

            var selected = $(this).find('easychat-console-language-option:selected');

            dropdown.find('#flow-completion-current-select.current').html(selected.data('display-text') || selected.text());
            options.each(function(j, o) {

                var display = $(o).data('display-text') || '';
                dropdown.find('ul').append('<li class="easychat-console-language-option ' + ($(o).is(':selected') ? 'selected' : '') + '" data-value="' + $(o).data("value") + '" data-display-text="' + display + '">' + $(o).text() + '</li>');
            });
        }

        // $("#email-flow-completion-rate-dropdown ul li:eq(" + 0 + ")").addClass('easychat-lang-selected');

        $('#flow-completion-current-select').html("Select Flow Completion rate");

    });

    $('#email-flow-completion-rate-dropdown .easychat-dropdown-select-custom ul').before('<div class="dd-search"> <svg class="drop-language-search-icon" width="15" height="14" viewBox="0 0 15 14" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M13.1875 12.0689L9.88352 8.76489C10.6775 7.81172 11.0734 6.58914 10.9889 5.35148C10.9045 4.11382 10.3461 2.95638 9.42994 2.11993C8.51381 1.28349 7.31047 0.83244 6.07025 0.86062C4.83003 0.8888 3.64842 1.39404 2.77123 2.27123C1.89404 3.14842 1.3888 4.33003 1.36062 5.57025C1.33244 6.81047 1.78349 8.01381 2.61993 8.92994C3.45638 9.84607 4.61382 10.4045 5.85148 10.4889C7.08914 10.5734 8.31172 10.1775 9.26489 9.38352L12.5689 12.6875L13.1875 12.0689ZM2.25002 5.68752C2.25002 4.90876 2.48095 4.14748 2.91361 3.49996C3.34627 2.85244 3.96122 2.34776 4.6807 2.04974C5.40019 1.75172 6.19189 1.67375 6.95569 1.82568C7.71949 1.97761 8.42108 2.35262 8.97175 2.90329C9.52242 3.45396 9.89743 4.15555 10.0494 4.91935C10.2013 5.68315 10.1233 6.47485 9.8253 7.19433C9.52728 7.91382 9.0226 8.52877 8.37508 8.96143C7.72756 9.39409 6.96628 9.62502 6.18752 9.62502C5.14358 9.62386 4.14274 9.20865 3.40457 8.47047C2.66639 7.7323 2.25118 6.73145 2.25002 5.68752Z" fill="#909090"/></svg><input id="txtSearchValueflow" autocomplete="off" placeholder="Search Categories" onkeyup="filter_flow_completion()" class="dd-searchbox" type="text"></div>');


    $('.easychat-dropdown-select-custom ul li:last').after('<div class="custom-drop-nodata-found-div">No result found</div> ');




}

$(document).on('click', '#email-flow-completion-rate-dropdown .easychat-dropdown-select-custom .easychat-console-language-option', function(event) {

    $(this).closest('.list').find('.easychat-lang-selected').removeClass('easychat-lang-selected');
    $(this).addClass('easychat-lang-selected');

    var text = $(this).data('display-text') || $(this).text();
    $(this).closest('.easychat-dropdown-select-custom').find('#flow-completion-current-select').text(text);
    $(this).closest('.easychat-dropdown-select-custom').prev('select').val($(this).data('value')).trigger('change');

    //update_form_widget(event, this)
});
//}

function filter_flow_completion() {
    var valThis = $('#txtSearchValueflow').val();
    $('#email-flow-completion-rate-dropdown .easychat-dropdown-select-custom ul > li').each(function() {
        var text = $(this).text();
        (text.toLowerCase().indexOf(valThis.toLowerCase()) > -1) ? $(this).show(): $(this).hide();

        if ($('#email-flow-completion-rate-dropdown .easychat-dropdown-select-custom ul').children(':visible').not('#email-flow-completion-rate-dropdown .custom-drop-nodata-found-div').length === 0) {
            $('#email-flow-completion-rate-dropdown .custom-drop-nodata-found-div').show();
        } else {
            $('#email-flow-completion-rate-dropdown .custom-drop-nodata-found-div').hide();
        }

    });
};

// flow completion dropdown

$(document).on('click', '.easychat-dropdown-select-custom', function(event) {
    if ($(event.target).hasClass('dd-searchbox')) {
        return;
    }
    $('.easychat-dropdown-select-custom').not($(this)).removeClass('open');
    $(this).toggleClass('open');
    $('.dd-searchbox').val("");
    $(".easychat-dropdown-select-custom ul li").show();
    $('.custom-drop-nodata-found-div').hide();
    if ($(this).hasClass('open')) {
        $(this).find('.easychat-console-language-option').attr('tabindex', 0);
        $(this).find('.easychat-lang-selected').focus();
    } else {
        $(this).find('.easychat-console-language-option').removeAttr('tabindex');
        $(this).focus();
    }
});

// Close when clicking outside
$(document).on('click', function(event) {
    if ($(event.target).closest('.easychat-dropdown-select-custom').length === 0) {
        $('.easychat-dropdown-select-custom').removeClass('open');
        $('.easychat-dropdown-select-custom .option').removeAttr('tabindex');
    }
    event.stopPropagation();
});



$(document).on('keydown', '.easychat-dropdown-select-custom', function(event) {
    var focused_option = $($(this).find('.list .easychat-console-language-option:focus')[0] || $(this).find('.list .easychat-console-language-option.easychat-lang-selected')[0]);
    // Space or Enter
    //if (event.keyCode == 32 || event.keyCode == 13) {
    if (event.keyCode == 13) {
        if ($(this).hasClass('open')) {
            focused_option.trigger('click');
        } else {
            $(this).trigger('click');
        }
        return false;
        // Down
    } else if (event.keyCode == 40) {
        if (!$(this).hasClass('open')) {
            $(this).trigger('click');
        } else {
            focused_option.next().focus();
        }
        return false;
        // Up
    } else if (event.keyCode == 38) {
        if (!$(this).hasClass('open')) {
            $(this).trigger('click');
        } else {
            var focused_option = $($(this).find('.list .easychat-console-language-option:focus')[0] || $(this).find('.list .easychat-console-language-option.easychat-lang-selected')[0]);
            focused_option.prev().focus();
        }
        return false;
        // Esc
    } else if (event.keyCode == 27) {
        if ($(this).hasClass('open')) {
            $(this).trigger('click');
        }
        return false;
    }
});



$(document).ready(function() {
    $("#mailer-analytics-email-address input").attr("placeholder", "Type here and hit enter");

    create_custom_flow_completion_dropdown();
    create_custom_intent_analytics_dropdown();
    create_custom_traffic_analytics_dropdown();

    $('#email_frequency_dropdown_wrapper').on('click', function() {
        toggle_email_frequency_dropdown();
    })

    $("#mailer_bot_accuracy").on("keypress", function (event) {
        let keys = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"];

        let value = event.target.value;

        return keys.indexOf(event.key) > -1 && (value == '' || parseInt(value)*10 <= 100);
    });  
});

function toggle_email_frequency_dropdown() {
    is_email_frequency_dropdown_open = !is_email_frequency_dropdown_open;
    
    var options = document.querySelector(".email-frequency-options-container");
    options.classList.toggle("active");

    if (is_email_frequency_dropdown_open) {
        selected.style.border = "none";
    } else {
        show_items_in_dropdown();
    }
}

function show_items_in_dropdown() {
    var items = document.querySelectorAll(".email-frequency-options-container .item-checkbox");
    var selected_items = get_selected_items(items);
    var selected_el = document.querySelector(".email-frequency-selected-items");

    selected_el.innerHTML = "";
    let flag = true;
    for (let item of selected_items) {
        flag = false;
        append_frequency_name_chip(item, selected_el);
    }

    if (flag) {
        selected_el.innerHTML = "Select Frequency";
        selected_el.style.padding = '10px';
    } else {
        selected_el.style.padding = '5px 10px 10px 5px'
    }
}

function get_selected_items(items) {
    var checked_items = new Set()

    items.forEach((item) => {
        if (item.checked) {
            checked_items.add(item.getAttribute("name"));
        } else {
            checked_items.delete(item.getAttribute("name"));
        } 
    });

    return checked_items;
}

function append_frequency_name_chip(text, selected_el) {
    var span = document.createElement("SPAN");
    span.innerHTML = `<span>${text}</span><img class='cross-btn email-frequency-selected-delete-icon' name='${text}' src='/static/EasyChatApp/img/Cross.png' alt='cross' />`;
    span.classList.add("tag", `_${text}`);
    selected_el.appendChild(span);
    add_delete_email_frequency_event();
}

function add_delete_email_frequency_event() {
    document.querySelectorAll(".email-frequency-selected-delete-icon").forEach((btn) => {
        
        btn.addEventListener("click", (e) => {
            e.stopPropagation();
            document.getElementById(`${e.target.name}`).checked = false;
            show_items_in_dropdown();
        });
    });
}

function add_email_address (e, data) {
    var added_email = data.childNodes[0].textContent;
    var need_to_delete = false;
    
    if (!validateEmailAddr(added_email)) {
        need_to_delete = true;
        M.toast({
            "html": "Please enter valid email address."
        }, 2000);
    }

    if (need_to_delete) {
        var added_el = e[0].M_Chips.chipsData
        var elem = $('#mailer-analytics-email-address');
        var instance = M.Chips.getInstance(elem);
        instance.deleteChip(added_el.length - 1);
    }

    if (!need_to_delete) {
        added_emails.push(added_email);
    }
}

function delete_email_address (e, data) {
    var deleted_word = data.childNodes[0].textContent;

    var index = added_emails.indexOf(deleted_word);

    if (index > -1) {
        added_emails.splice(index, 1);
    }
}

/* Save Profile Functionality */

function get_trigger_settings() {
    var profile_name = document.getElementById('mailer-profile-name').value.trim();
    profile_name = stripHTML(profile_name);
    profile_name = strip_unwanted_characters(profile_name);

    if (profile_name == "") {
        M.toast({
            "html": "Profile name cannot be empty."
        }, 2000);

        return {is_valid: false};
    }

    var email_frequency = get_selected_items(document.querySelectorAll(".email-frequency-options-container .item-checkbox"));

    var email_subject = document.getElementById('mailer_email_subject').value.trim();
    email_subject = stripHTML(email_subject)
    email_subject = strip_unwanted_characters(email_subject);

    var bot_accuracy = document.getElementById('mailer_bot_accuracy').value.trim();

    if (bot_accuracy == "") bot_accuracy = 0;

    return {
        is_valid: true,
        profile_name: profile_name,
        email_frequency: Array.from(email_frequency),
        email_subject: email_subject,
        emails: added_emails,
        bot_accuracy: bot_accuracy,
    }
}

function get_table_parameters() {
    var is_table_enabled = document.getElementById('enable_table_parameter_cb').checked;

    var count_variations, selected_channels, 
        message_analytics, session_analytics,  
        user_analytics, livechat_analytics,
        flow_analytics, intent_analytics, traffic_analytics;

    if (is_table_enabled) {
        count_variations = get_selected_items(document.querySelectorAll('.table_parameter_count_variation_checkbox'));
        selected_channels = get_selected_items(document.querySelectorAll('.table_parameter_channels_checkbox'));
        message_analytics = get_selected_items(document.querySelectorAll('.table_parameter_message_analytics_checkbox'));
        session_analytics = get_selected_items(document.querySelectorAll('.table_parameter_session_analytics_checkbox'));
        user_analytics = get_selected_items(document.querySelectorAll('.table_parameter_user_analytics_checkbox'));
        livechat_analytics = get_selected_items(document.querySelectorAll('.table_parameter_livechat_analytics_checkbox'));
        language_query_analytics = get_selected_items(document.querySelectorAll('.table_parameter_language_analytics_checkbox'));

        flow_analytics = $('#mailer-flow-completion-multi-dropdown').val();
        flow_analytics_options = document.getElementById('mailer-flow-completion-multi-dropdown').options;
        flow_analytics = flow_analytics.length == flow_analytics_options.length ? ['all_selected'] : flow_analytics;
        
        intent_analytics = $('#mailer-intent-analytics-multi-dropdown').val();
        intent_analytics_options = document.getElementById('mailer-intent-analytics-multi-dropdown').options;
        intent_analytics = intent_analytics.length == intent_analytics_options.length ? ['all_selected'] : intent_analytics;

        traffic_analytics = $('#mailer-traffic-analytics-multi-dropdown').val();
        traffic_analytics_options = document.getElementById('mailer-traffic-analytics-multi-dropdown').options;
        traffic_analytics = traffic_analytics.length == traffic_analytics_options.length ? ['all_selected'] : traffic_analytics;

        language_analytics = $('#language-based-multi-dropdown').val();
        language_analytics_options = document.getElementById('language-based-multi-dropdown').options;
        language_analytics = language_analytics.length == language_analytics_options.length ? ['all'] : language_analytics;
        
    } else {
        count_variations = [];
        selected_channels = [];
        message_analytics = [];
        session_analytics = [];
        user_analytics = [];
        livechat_analytics = [];
        language_query_analytics = [];
        flow_analytics = [];
        intent_analytics = [];
        traffic_analytics = [];
        language_analytics = [];
    }

    return {
        is_table_enabled: is_table_enabled,
        count_variation: Array.from(count_variations),
        channels: Array.from(selected_channels),
        message_analytics: Array.from(message_analytics),
        session_analytics: Array.from(session_analytics),
        user_analytics: Array.from(user_analytics),
        livechat_analytics: Array.from(livechat_analytics),
        language_query_analytics: Array.from(language_query_analytics),
        flow_analytics: flow_analytics,
        intent_analytics: intent_analytics,
        traffic_analytics: traffic_analytics,
        language_analytics: language_analytics
    }
}

function get_graph_parameters() {
    var is_graph_enabled = document.getElementById('enable_graphic_parameter_cb').checked;

    var graph_parameters, message_analytics_graph;

    if (is_graph_enabled) {
        graph_parameters = get_selected_items(document.querySelectorAll('.graph_parameters_checkbox'));
        message_analytics_graph = get_selected_items(document.querySelectorAll('.message_analytics_graph_checkbox'));
    } else {
        graph_parameters = [];
        message_analytics_graph = [];
    }

    return {
        is_graph_enabled: is_graph_enabled,
        graph_parameters: Array.from(graph_parameters),
        message_analytics_graph: Array.from(message_analytics_graph),
    }   
}

function get_attachment_parameters() {
    var is_attachment_enabled = document.getElementById('enable_attachment_parameter_cb').checked;

    var attachments;

    if (is_attachment_enabled) {
        attachments = get_selected_items(document.querySelectorAll('.attachment_parameters_checkbox'));
    } else {
        attachments = [];
    }

    return {
        is_attachment_enabled: is_attachment_enabled,
        attachments: Array.from(attachments),
    }   
}

function save_profile_to_server () {
    var trigger_settings = get_trigger_settings();

    if (!trigger_settings.is_valid) return;

    var table_params = get_table_parameters();
    var graph_params = get_graph_parameters();
    var attachment_params = get_attachment_parameters();
    
    let bot_id = window.location.pathname.split("/")[4];

    json_string = {
        bot_id: bot_id,
        profile_name: trigger_settings.profile_name,
        email_frequency: trigger_settings.email_frequency,
        email_subject: trigger_settings.email_subject,
        emails: trigger_settings.emails,
        bot_accuracy: trigger_settings.bot_accuracy,
        table_params: JSON.stringify(table_params),
        graph_params: JSON.stringify(graph_params),
        attachment_params: JSON.stringify(attachment_params),
    };

    if (is_profile_edited) {
        json_string.profile_id = profile_id;
    }

    if (trigger_settings.emails.length == 0) {
        M.toast({
            "html": "Please enter at least one email address."
        }, 2000);
        return;
    }

    json_string = JSON.stringify(json_string)
    json_string = EncryptVariable(json_string)

    $.ajax({
        url: "/chat/save-mailer-profile/",
        type: "POST",
        data: {
            json_string: json_string
        },
        success: function(response) {
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response.status == 200) {
                M.toast({
                    "html": "Profile saved successfully."
                }, 2000);

                setTimeout(function() {
                    window.location.reload();
                }, 3000);
            } else {
                M.toast({
                    "html": response.message
                }, 2000);
            }
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log(xhr);
            console.log(textstatus);
            console.log(errorthrown);
        }
    });
}

/* Save Profile Functionality Ends */

/* Render Profile Functionality */

function set_profile_modal() {

    if (!is_mailer_profile_modal_opened) {
        var profiles = PROFILE_DICT;

        Object.keys(profiles).forEach(function(key) {
            add_profile_to_modal(profiles[key]);
        })
        
        $(".email-analytics-profile-div-cb").on("change", function(event) {
            if (this.checked) {
                profile_id = event.target.id.replace('profile_', '');
                $(".mailer-modal-btn-wrapper").css("display", "flex");
        
            } else {
                $(".mailer-modal-btn-wrapper").css("display", "none");
            }
        });  

        is_mailer_profile_modal_opened = true;
    }

    $('#modal-mailer_analytics').modal('open');
}

function add_profile_to_modal(profile) {
    var html = `<div class="col s4">
                    <label>
                        <input type="radio" name="email_analytics_profile_div" class="email-analytics-profile-div-cb" id="profile_${profile.id}">
                
                        <div class="email-analytics-person-profile-container">
                            <div class="email-analytics-person-profile-heading-text">
                                ${profile.name}
                            </div>

                            <a class="email-analytics-person-profile-delete-btn modal-trigger" id="delete_${profile.name}" onclick="open_delete_profile_modal(this)">
                                <svg width="16" height="16" viewBox="0 0 16 16" fill="#909090" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M12.2 3.80664C12.0754 3.6818 11.9063 3.61165 11.73 3.61165C11.5536 3.61165 11.3845 3.6818 11.26 3.80664L7.99998 7.05997L4.73998 3.79997C4.61543 3.67514 4.44633 3.60498 4.26998 3.60498C4.09364 3.60498 3.92453 3.67514 3.79998 3.79997C3.53998 4.05997 3.53998 4.47997 3.79998 4.73997L7.05998 7.99997L3.79998 11.26C3.53998 11.52 3.53998 11.94 3.79998 12.2C4.05998 12.46 4.47998 12.46 4.73998 12.2L7.99998 8.93997L11.26 12.2C11.52 12.46 11.94 12.46 12.2 12.2C12.46 11.94 12.46 11.52 12.2 11.26L8.93998 7.99997L12.2 4.73997C12.4533 4.48664 12.4533 4.05997 12.2 3.80664Z" />
                                </svg>
                            </a>

                            <a href="javascript:void(0)" id="edit_${profile.name}" class="email-analytics-person-profile-edit-btn" onclick="edit_mailer_profile(this);">
                                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M11.2388 6.60825L13.8831 9.25263L8.69045 14.4453C8.54578 14.5899 8.36587 14.6943 8.16849 14.7482L5.49554 15.4772C5.203 15.5569 4.93458 15.2885 5.01436 14.996L5.74335 12.323C5.79718 12.1257 5.90159 11.9457 6.04626 11.8011L11.2388 6.60825ZM14.9439 5.54763C15.6741 6.2778 15.6741 7.46165 14.9439 8.19182L14.437 8.69825L11.7926 6.0544L12.2997 5.54763C13.0299 4.81746 14.2137 4.81746 14.9439 5.54763Z" fill="white"/>
                                </svg>
                            </a>
                            <div class="email-analytics-person-profile-subheading-list">
                                <div>Trigger Settings </div>`;
    
    if (profile.is_graph_enabled) {
        html += `<div>Graphic Settings</div>`;
    }

    if (profile.is_table_enabled) {
        html += `<div>Table Parameters</div>`;
    }

    if (profile.is_attachment_enabled) {
        html += `<div>Attachment Parameters</div>`;
    }

    html += `</div>
            </div>
        </label>
        </div>`

    $('#mailer_analytics_all_profiles').prepend(html);
}

function edit_mailer_profile(el) {
    var id = el.id.replace('edit_', '');
    
    var profile = PROFILE_DICT[id];
    profile_id = profile.id;
    is_profile_edited = true;

    document.getElementById('profile_details_div').scrollTop = 0;
    document.getElementById('mailer-profile-name').value = profile.name;
    document.getElementById('modal_profile_name_head').innerHTML = profile.name;
    document.getElementById('mailer_bot_accuracy').value = profile.bot_accuracy;

    check_items(profile.email_frequency, document.querySelectorAll(".email-frequency-options-container .item-checkbox"));
    show_items_in_dropdown();
    add_email_addresses(profile.email_address);

    document.getElementById('mailer_email_subject').value = profile.email_subject;

    $('.show-char-count').trigger('keyup');

    set_table_parameters(profile.table_params, profile.is_table_enabled);
    set_graph_parameters(profile.graph_params, profile.is_graph_enabled);
    set_attachment_parameters(profile.attachment_params, profile.is_attachment_enabled);
    show_profile();
}

function add_email_addresses(email_address) {
    var data = []
    added_emails = []
    for(var email of email_address) {
        added_emails.push(email);
        data.push({
            "tag": email,
        });
    }

    $('#mailer-analytics-email-address').chips({
        data: data,
        onChipDelete: function(e, data) {
            delete_email_address(e, data)
        },
        onChipAdd: function(e, data) {
            add_email_address(e, data)
        }
    })
}

function uncheck_items(items) {
    items.forEach((item) => {
        item.checked = false;
    });
}

function check_items(item_names, items) {
    items.forEach((item) => {
        if(item_names.includes(item.getAttribute("name"))) {
            item.checked = true;
        } else {
            item.checked = false;
        }
        $(item).change()
    });
}

function load_flow_analytics_data(flow_analytics) {
    var flow_analytics_el = document.getElementById('mailer-flow-completion-multi-dropdown');
    flow_analytics_el.classList.remove('jqmsLoaded');
    
    var classes = flow_analytics_el.classList;
    var element_id;
    Array.from(classes).forEach(function(class_name) {
        if (class_name.indexOf('ms-list') > -1) {
            element_id = class_name;
        }
    })

    if (element_id) {
        flow_analytics_el.classList.remove(element_id);
        document.getElementById(element_id).remove();    
    }

    all_selected = false;
    if (flow_analytics.includes('all_selected')) {
        all_selected = true;
    }

    for (var option of flow_analytics_el.options) {
        if (all_selected || flow_analytics.includes(option.value.trim())) {
            option.selected = true;
        } else {
            option.selected = false;
        }
    }

    $('#mailer-flow-completion-multi-dropdown').multiselect({
        columns: 1,
        placeholder: 'Select Flow Completion rate',
        search: true,
        searchOptions: {
            'default': 'Search Here'
        },
        selectAll: true
    });
}

function load_intent_analytics_data(intent_analytics) {
    var intent_analytics_el = document.getElementById('mailer-intent-analytics-multi-dropdown');
    intent_analytics_el.classList.remove('jqmsLoaded');

    var classes = intent_analytics_el.classList;
    var element_id;
    Array.from(classes).forEach(function(class_name) {
        if (class_name.indexOf('ms-list') > -1) {
            element_id = class_name;
        }
    })

    if (element_id) {
        intent_analytics_el.classList.remove(element_id);
        document.getElementById(element_id).remove();    
    }
    
    all_selected = false;
    if (intent_analytics.includes('all_selected')) {
        all_selected = true;
    }

    for (var option of intent_analytics_el.options) {
        if (all_selected || intent_analytics.includes(option.value.trim())) {
            option.selected = true;
        } else {
            option.selected = false;
        }
    }

    $('#mailer-intent-analytics-multi-dropdown').multiselect({
        columns: 1,
        placeholder: 'Select Intent Analytics',
        search: true,
        searchOptions: {
            'default': 'Search Here'
        },
        selectAll: true
    });
}

function load_traffic_analytics_data(traffic_analytics) {
    var traffic_analytics_el = document.getElementById('mailer-traffic-analytics-multi-dropdown');
    traffic_analytics_el.classList.remove('jqmsLoaded');
    
    var classes = traffic_analytics_el.classList;
    var element_id;
    Array.from(classes).forEach(function(class_name) {
        if (class_name.indexOf('ms-list') > -1) {
            element_id = class_name;
        }
    })

    if (element_id) {
        traffic_analytics_el.classList.remove(element_id);
        document.getElementById(element_id).remove();    
    }

    all_selected = false;
    if (traffic_analytics.includes('all_selected')) {
        all_selected = true;
    }
    
    for (var option of traffic_analytics_el.options) {
        if (all_selected || traffic_analytics.includes(option.value.trim())) {
            option.selected = true;
        } else {
            option.selected = false;
        }
    }

    $('#mailer-traffic-analytics-multi-dropdown').multiselect({
        columns: 1,
        placeholder: 'Select Traffic Analytics',
        search: true,
        searchOptions: {
            'default': 'Search Here'
        },
        selectAll: true
    });
}

document.getElementById('language-based-multi-dropdown').onchange = ()=>{
    if(document.getElementById('language-based-multi-dropdown').options.selectedIndex != -1){
        document.getElementById('language_query_analytics').style.display = "block"
    }else{
        document.getElementById('language_query_analytics').style.display = "none"
    }
}

function load_language_analytics_data(language_analytics){
    var language_analytics_el = document.getElementById('language-based-multi-dropdown');
    language_analytics_el.classList.remove('jqmsLoaded');
    
    var classes = language_analytics_el.classList;
    var element_id;
    Array.from(classes).forEach(function(class_name) {
        if (class_name.indexOf('ms-list') > -1) {
            element_id = class_name;
        }
    })

    if (element_id) {
        language_analytics_el.classList.remove(element_id);
        document.getElementById(element_id).remove();    
    }

    all_selected = false;
    if (language_analytics.includes('all')) {
        all_selected = true;
    }
    
    for (var option of language_analytics_el.options) {
        if (all_selected || language_analytics.includes(option.value.trim())) {
            option.selected = true;
        } else {
            option.selected = false;
        }
    }

    if(language_analytics_el.options.selectedIndex != -1){
        document.getElementById('language_query_analytics').style.display = "block"
    }else{
        document.getElementById('language_query_analytics').style.display = "none"
    }

    $('#language-based-multi-dropdown').multiselect({
        columns: 1,
        placeholder: 'Select Languages',
        search: true,
        searchOptions: {
            'default': 'Search'
        },
        selectAll: true
    });
}

function set_table_parameters(table_params, is_table_enabled) {
    document.getElementById('enable_table_parameter_cb').checked = is_table_enabled;
    $('#enable_table_parameter_cb').trigger('change');

    check_items(table_params.count_variation, document.querySelectorAll('.table_parameter_count_variation_checkbox'));
    check_items(table_params.channels, document.querySelectorAll('.table_parameter_channels_checkbox'));
    check_items(table_params.message_analytics, document.querySelectorAll('.table_parameter_message_analytics_checkbox'));
    check_items(table_params.session_analytics, document.querySelectorAll('.table_parameter_session_analytics_checkbox'));
    check_items(table_params.user_analytics, document.querySelectorAll('.table_parameter_user_analytics_checkbox'));
    check_items(table_params.livechat_analytics, document.querySelectorAll('.table_parameter_livechat_analytics_checkbox'));
    check_items(table_params.language_query_analytics, document.querySelectorAll('.table_parameter_language_analytics_checkbox'));

    load_flow_analytics_data(table_params.flow_analytics);
    load_intent_analytics_data(table_params.intent_analytics);
    load_traffic_analytics_data(table_params.traffic_analytics);
    load_language_analytics_data(table_params.language_analytics);
}

function set_graph_parameters(graph_params, is_graph_enabled) {
    document.getElementById('enable_graphic_parameter_cb').checked = is_graph_enabled;
    $('#enable_graphic_parameter_cb').trigger('change');

    check_items(graph_params.graph_parameters, document.querySelectorAll('.graph_parameters_checkbox'));
    check_items(graph_params.message_analytics_graph, document.querySelectorAll('.message_analytics_graph_checkbox'));
}

function set_attachment_parameters(attachment_params, is_attachment_enabled) {
    document.getElementById('enable_attachment_parameter_cb').checked = is_attachment_enabled;
    $('#enable_attachment_parameter_cb').trigger('change');

    check_items(attachment_params.attachments, document.querySelectorAll('.attachment_parameters_checkbox'));
}

function create_new_profile() {
    profile_id = '';
    is_profile_edited = false;
    added_emails = [];

    var total_profiles = Object.keys(PROFILE_DICT).length;
    var counter = total_profiles + 1;

    var new_profile_name = `Profile ${counter}`;

    while(new_profile_name in PROFILE_DICT) {
        counter += 1;
        new_profile_name = `Profile ${counter}`
    }

    document.getElementById('mailer-profile-name').value = new_profile_name;
    document.getElementById('modal_profile_name_head').innerHTML = new_profile_name;
    uncheck_items(document.querySelectorAll(".email-frequency-options-container .item-checkbox"));
    show_items_in_dropdown();

    $('#mailer-analytics-email-address').chips({
        data: [],
        onChipDelete: function(e, data) {
            delete_email_address(e, data)
        },
        onChipAdd: function(e, data) {
            add_email_address(e, data)
        }
    })

    document.getElementById('mailer_email_subject').value = DEFAULT_MAIL_SUBJECT;
    document.getElementById('mailer_bot_accuracy').value = 0;

    $('.show-char-count').trigger('keyup');

    set_table_parameters({
        count_variation: ['Daily'],
        channels: [],
        message_analytics: [],
        session_analytics: [],
        user_analytics: [],
        livechat_analytics: [],
        flow_analytics: [],
        intent_analytics: [],
        traffic_analytics: [],
        language_analytics: [],
        language_query_analytics: [],
    }, true)

    set_graph_parameters({
        graph_parameters: [],
        message_analytics_graph: [],
    }, false)

    set_attachment_parameters({
        attachments: [],
    }, false)

    show_profile();
}

function show_profile() {
    $(".eamil-analytics-profile-edit-modal-content").css("display", "block");
    $(".eamil-analytics-profile-add-modal-content").css("display", "none");
    $(".email-analytics-edit-modal-save-btn").css("display", "flex");
    $(".mailer-modal-btn-wrapper").css("display", "none");

    document.getElementById('profile_details_div').scrollTop = 0;
}

function open_delete_profile_modal(el) {
    var id = el.id.replace('delete_', '');

    document.getElementById('delete_mailer_profile_btn').dataset.id = id;

    $('#email-analytics-delete-profile-modal').modal('open');
}

function delete_mailer_profile(el) {
    var profile_name = el.dataset.id;
    var profile_id = PROFILE_DICT[profile_name].id;

    json_string = {
        profile_id: profile_id,
    };

    json_string = JSON.stringify(json_string)
    json_string = EncryptVariable(json_string)

    $.ajax({
        url: "/chat/delete-mailer-profile/",
        type: "POST",
        data: {
            json_string: json_string
        },
        success: function(response) {
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response.status == 200) {
                M.toast({
                    "html": "Profile deleted successfully."
                }, 2000);

                setTimeout(function() {
                    window.location.reload();
                }, 3000);
            } else {
                M.toast({
                    "html": response.message
                }, 2000);
            }
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log(xhr);
            console.log(textstatus);
            console.log(errorthrown);
        }
    });
}

function collapseRotateIcon(ele) {
    ele.childNodes[0].classList.toggle(
        "email-analytics-collapsible-icon-rotate"
    );
}

function go_to_all_profiles() {
    $(".eamil-analytics-profile-edit-modal-content").css("display", "none");
    $(".eamil-analytics-profile-add-modal-content").css("display", "block");
    $(".email-analytics-edit-modal-save-btn").css("display", "none");

    var selected_profile = $("input[type='radio'][name='email_analytics_profile_div']:checked").val();

    if (selected_profile) {
        $(".mailer-modal-btn-wrapper").css("display", "flex");
    }

    var settings = document.getElementsByClassName('email-analytics-collapsible-icon-rotate');
    
    Array.from(settings).forEach(function(setting) {
        setting.classList.toggle('email-analytics-collapsible-icon-rotate');
    })

    var elems = document.getElementsByClassName('email-analytics-collapsible-options');

    Array.from(elems).forEach(function(elem) {
        var instance = M.Collapsible.getInstance(elem);
        instance.close();
    })

    document.getElementById('trigger_settings_icon').classList.add('email-analytics-collapsible-icon-rotate');
    var instance = M.Collapsible.getInstance(document.getElementById('trigger_settings_collapsible'));
    instance.open();
}

/* Render Profile Functionality Ends */

function send_sample_mail(el) {

    if(profile_id == '') {
        M.toast({
            "html": "Please select a profile to send sample mail."
        }, 2000);

        return;
    }

    el.innerHTML = 'Sending'

    json_string = {
        profile_id: profile_id,
    };

    json_string = JSON.stringify(json_string)
    json_string = EncryptVariable(json_string)

    $.ajax({
        url: "/chat/send-test-mail/",
        type: "POST",
        data: {
            json_string: json_string
        },
        success: function(response) {
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response.status == 200) {
                M.toast({
                    "html": "Mail sent successfully."
                }, 2000);
            } else {
                M.toast({
                    "html": response.message
                }, 2000);
            }

            el.innerHTML = 'Send Sample Mail'
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log(xhr);
            console.log(textstatus);
            console.log(errorthrown);

            el.innerHTML = 'Send Sample Mail'
        }
    });
}

$(document).mouseup(function(e) {
    const container = $(".easychat-profile-dropdown-wrapper");

    if (container.length != 0 && !container.is(e.target) && container.has(e.target).length === 0) {
        const profile_div = $('.email-frequency-options-container');

        if (profile_div.hasClass('active')) {
            $('.wrapper-box').trigger('click');
        }
    }
});

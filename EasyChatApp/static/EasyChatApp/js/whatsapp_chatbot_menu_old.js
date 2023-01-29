var edit_main_intents_selected = 0;

$(document).on('contextmenu', '.add-api-variable', function(e) {
    e.preventDefault();
    var d = document.getElementById('api-menu-div');
    d.style.position = "absolute";
    d.style.left = e.pageX + 'px';
    d.style.top = e.pageY + 'px';
    var api_variable_name = this.id.split("-")[1];
    $(".btn-share-api").attr("id", "btn-share-bot-" + api_variable_name);
    $("#api-menu-div").show();
    return false;
});

function update_section_title_chars() {
    document.getElementById("whatsapp-add-section-title-chars").innerText = document.getElementById("whatsapp-menu-section-title").value.length;
    enable_or_disable_add_section_save_btn();
}

function reset_add_section_modal() {
    document.getElementById("whatsapp-menu-section-title").value = "";

    var checked_inputs = document.querySelectorAll("#easychat_whatsapp_menu_intent_list option");
    for (var i=0; i<checked_inputs.length; i++) {
        checked_inputs[i].selected = false;
    }

    document.getElementById("child_intent_group").innerHTML = " - ";
    document.getElementById("main_intent_group").innerHTML = " - ";
}

function enable_or_disable_add_section_save_btn() {
    var save_section_btn = document.getElementById("save-whatsapp-menu");
    if (document.getElementById("whatsapp-menu-section-title").value.length && (document.getElementById("child_intent_group").children.length || document.getElementById("main_intent_group").children.length)) {
        save_section_btn.classList.remove("whatsapp-menu-disabled");
        save_section_btn.setAttribute("onclick", "save_whatsapp_menu_section('" + document.getElementById("easychat_whatsapp_add_section_modal").getAttribute("whatsapp-section-id") + "');");
    } else {
        save_section_btn.classList.add("whatsapp-menu-disabled");
        save_section_btn.setAttribute("onclick", "return false;")
    }
}

function enable_or_disable_dropdown_check_boxes() {
    let quick_recommendations_selected, input_checkboxes;
    if ($('#easychat_whatsapp_menu_intent_list_div ul li.optgroup:last span').text() === "Main Intent") {
        quick_recommendations_selected = document.getElementsByClassName("main-intent").length + $('#easychat_whatsapp_menu_intent_list_div ul li.optgroup:last input:checked').length - edit_main_intents_selected;
        input_checkboxes = $('#easychat_whatsapp_menu_intent_list_div ul li.optgroup:last input')
    } else {
        quick_recommendations_selected = document.getElementsByClassName("main-intent").length - edit_main_intents_selected;
        input_checkboxes = []
    }
    
    if (quick_recommendations_selected >= whatsapp_quick_recommendation_allowed) {
        for (var i=0; i<input_checkboxes.length; i++) {
            if (!input_checkboxes[i].checked) {
                input_checkboxes[i].disabled = true;
                input_checkboxes[i].parentElement.classList.add("whatsapp-menu-disabled");
            }
        }
    } else {
        for (var i=0; i<input_checkboxes.length; i++) {
            input_checkboxes[i].disabled = false;
            input_checkboxes[i].parentElement.classList.remove("whatsapp-menu-disabled");
        }
    }
}

function enable_or_disable_add_section_btn() {
    var total_options_selected = document.querySelectorAll(".child-tree").length + document.querySelectorAll(".main-intent").length;
    var add_section_btn = document.getElementById("whatsapp-menu-add-section-btn");
    if (total_options_selected >= 10) {
        add_section_btn.classList.add("whatsapp-menu-disabled");
        add_section_btn.setAttribute("onclick", "return false;");
    } else {
        add_section_btn.classList.remove("whatsapp-menu-disabled");
        add_section_btn.setAttribute("onclick", "open_add_whatsapp_new_section_modal()");
    }

    var preview_section_btn = document.getElementById("whatsapp-menu-preview-section-btn");
    if (document.querySelectorAll(".easychat-whatsapp-menu-item-wrapper").length) {
        preview_section_btn.classList.remove("whatsapp-menu-disabled");
        preview_section_btn.setAttribute("onclick", "preview_whatsapp_menu()");
    } else {
        preview_section_btn.classList.add("whatsapp-menu-disabled");
        preview_section_btn.setAttribute("onclick", "return false;");
        document.getElementsByClassName("easychat-whatsapp-sync-preview-data-wrapper")[0].style.display = "none";
    }
}

function add_onchange_function() {
    if ($('#easychat_whatsapp_menu_intent_list_div ul li.optgroup:first span').text() === "Child Intent") {
        $('#easychat_whatsapp_menu_intent_list_div ul li.optgroup:first input').change(() => {
            $('#child_intent_group').empty()
            $('#easychat_whatsapp_menu_intent_list_div ul li.optgroup:first input:checked').each((indx, element) => {
                $('#child_intent_group').append('<div id="div_' + element.id + '" value="' + element.value + '"><span><b><svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M8 8.5C8.55228 8.5 9 8.94772 9 9.5C9 10.0523 8.55228 10.5 8 10.5C7.44772 10.5 7 10.0523 7 9.5C7 8.94772 7.44772 8.5 8 8.5ZM4 8.5C4.55228 8.5 5 8.94772 5 9.5C5 10.0523 4.55228 10.5 4 10.5C3.44772 10.5 3 10.0523 3 9.5C3 8.94772 3.44772 8.5 4 8.5ZM8 5C8.55228 5 9 5.44772 9 6C9 6.55228 8.55228 7 8 7C7.44772 7 7 6.55228 7 6C7 5.44772 7.44772 5 8 5ZM4 5C4.55228 5 5 5.44772 5 6C5 6.55228 4.55228 7 4 7C3.44772 7 3 6.55228 3 6C3 5.44772 3.44772 5 4 5ZM8 1.5C8.55228 1.5 9 1.94772 9 2.5C9 3.05228 8.55228 3.5 8 3.5C7.44772 3.5 7 3.05228 7 2.5C7 1.94772 7.44772 1.5 8 1.5ZM4 1.5C4.55228 1.5 5 1.94772 5 2.5C5 3.05228 4.55228 3.5 4 3.5C3.44772 3.5 3 3.05228 3 2.5C3 1.94772 3.44772 1.5 4 1.5Z" fill="white"/></svg></b>' + element.title + ' <a id="cross_' + element.id + '" onclick="remove_selected_intent(this)"> <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2.3938 2.25L9.60619 9.75" stroke="white" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"/><path d="M9.6062 2.25L2.39381 9.75" stroke="white" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"/></svg></a></span></div>')
            })
            if ($('#child_intent_group').is(':empty')) {
                $('#child_intent_group').append("-");
            }
            enable_or_disable_add_section_save_btn();
        });
    }

    if ($('#easychat_whatsapp_menu_intent_list_div ul li.optgroup:last span').text() === "Main Intent") {
        $('#easychat_whatsapp_menu_intent_list_div ul li.optgroup:last input').change(() => {
            $('#main_intent_group').empty()
            $('#easychat_whatsapp_menu_intent_list_div ul li.optgroup:last input:checked').each((indx, element) => {
                $('#main_intent_group').append('<div id="div_' + element.id + '" value="' + element.value + '"><span><b><svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M8 8.5C8.55228 8.5 9 8.94772 9 9.5C9 10.0523 8.55228 10.5 8 10.5C7.44772 10.5 7 10.0523 7 9.5C7 8.94772 7.44772 8.5 8 8.5ZM4 8.5C4.55228 8.5 5 8.94772 5 9.5C5 10.0523 4.55228 10.5 4 10.5C3.44772 10.5 3 10.0523 3 9.5C3 8.94772 3.44772 8.5 4 8.5ZM8 5C8.55228 5 9 5.44772 9 6C9 6.55228 8.55228 7 8 7C7.44772 7 7 6.55228 7 6C7 5.44772 7.44772 5 8 5ZM4 5C4.55228 5 5 5.44772 5 6C5 6.55228 4.55228 7 4 7C3.44772 7 3 6.55228 3 6C3 5.44772 3.44772 5 4 5ZM8 1.5C8.55228 1.5 9 1.94772 9 2.5C9 3.05228 8.55228 3.5 8 3.5C7.44772 3.5 7 3.05228 7 2.5C7 1.94772 7.44772 1.5 8 1.5ZM4 1.5C4.55228 1.5 5 1.94772 5 2.5C5 3.05228 4.55228 3.5 4 3.5C3.44772 3.5 3 3.05228 3 2.5C3 1.94772 3.44772 1.5 4 1.5Z" fill="white"/></svg></b>' + element.title + ' <a id="cross_' + element.id + '" onclick="remove_selected_intent(this)"><svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2.3938 2.25L9.60619 9.75" stroke="white" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"/><path d="M9.6062 2.25L2.39381 9.75" stroke="white" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"/></svg></a></span></div>')
            })
            if ($('#main_intent_group').is(':empty')) {
                $('#main_intent_group').append("-");
            }
            enable_or_disable_dropdown_check_boxes();
            enable_or_disable_add_section_save_btn();
        });
    }
}

$(function() {
    $('#easychat_whatsapp_menu_intent_list').multiselect({
        columns: 1,
        placeholder: 'Select Intent',
        search: true,
        searchOptions: {
            'default': 'Search Intent'
        },
        selectAll: false
    });

    $("#main_intent_group").sortable({
        containment: "parent"
    });
    $("#child_intent_group").sortable({
        containment: "parent"
    });

    add_onchange_function();
    enable_or_disable_dropdown_check_boxes();
});

function remove_selected_intent(el) {
    let intent_checkbox_id = el.id.split('_')[1]
    $('#' + intent_checkbox_id).click().change()
    enable_or_disable_add_section_save_btn();
}

$("#home-button").click(function() {
    if ($("#panel").is(":visible") == true) {
        $("#panel").hide(100);
    } else {
        $("#panel").show(100);
    }
});

$(document).on('contextmenu', '.collapsible_custom', function(e) {
    e.preventDefault();
    var d = document.getElementById('menu-div');
    d.style.position = "absolute";
    d.style.left = e.pageX - 200 + 'px';edit_main_intents_selected
    d.style.top = e.pageY + 'px';
    pk_list = this.id.split("_");
    global_select_tree_name = $(this).text().trim()
    global_select_intent_id = pk_list[0];
    global_select_parent_id = pk_list[1];
    global_select_tree_id = pk_list[2];
    var tree_name = document.getElementById(this.id + "_tree_name_container").getAttribute("value");
    document.getElementById("modal_tree_name").value = tree_name;
    $("#menu-div").show();
    return false;
});

$(document).ready(function() {
    $('.modal').modal();
    $('.modal').on('shown.bs.modal', function(e) {
        $('#modal-general-feedback').find('input:text, input:file, input:password, select, textarea').val('');
        $(this).removeData();
    });

    $("#whatsapp_preview_close_btn").click(function() {
        $(this).parent().hide();
    });
    
    $("#enable_whatsapp_menu_format").on("change", function(event) {
        if (this.checked) {
            $(".easychat-whatsapp-menu-format-data-wrapper").show();
    
        } else {
            $('.easychat-whatsapp-menu-format-data-wrapper').hide();
        }
    });

    var whatsapp_short_name_input_field = document.getElementById("whatsapp-short-name-input")
    whatsapp_short_name_input_field.addEventListener('input', () => {
        document.getElementById("whatsapp_short_name_field-char-count").innerHTML = whatsapp_short_name_input_field.value.length
    });

    var whatsapp_description_input_field = document.getElementById("whatsapp-description-input")
    whatsapp_description_input_field.addEventListener('input', () => {
        document.getElementById("whatsapp_description_field-char-count").innerHTML = whatsapp_description_input_field.value.length
    });

    enable_or_disable_add_section_btn();

    document.getElementById("whatsapp-menu-section-title").onkeyup = update_section_title_chars;
});

function add_whatsapp_menu_section_html(data) {

    var child_trees_html = '';
    for (var i=0; i<data["child_trees_data"].length; i++) {
        child_trees_html += `<div class="whatsapp-menu-selected-intent-chip child-tree" onclick="open_tree_page('` + data["child_trees_data"][i].intent_pk + `', '` + data["child_trees_data"][i].parent_tree_pk + `', '` + data["child_trees_data"][i].tree_pk + `')" name="` + data["child_trees_data"][i].name + `" description="` + data["child_trees_data"][i].description + `" short_name="` + data["child_trees_data"][i].short_name + `" value="` + data["child_trees_data"][i].tree_pk + `">` + data["child_trees_data"][i].name + `</div>`
    }

    var main_intents_html = '';
    for (var i=0; i<data["main_intents_data"].length; i++) {
        main_intents_html += `<div class="whatsapp-menu-selected-intent-chip main-intent" onclick="open_intent_page('` + data["main_intents_data"][i].intent_pk + `')" name="` + data["main_intents_data"][i].name + `" description="` + data["main_intents_data"][i].description + `" short_name="` + data["main_intents_data"][i].short_name + `" value="` + data["main_intents_data"][i].intent_pk + `">` + data["main_intents_data"][i].name + `</div>`
    }

    var html = `<div class="easychat-whatsapp-menu-item-wrapper" id="easychat-whatsapp-menu-item-` + data["whatsapp_menu_section_id"] + `">
        <div class="easychat-whatsapp-menu-data-item">
            <div class="easychat-whatsapp-menu-item-header">Section title</div>
            <div class="whatsapp-menu-item-title-wrapper">
                <input type="text" style="width: calc(100% - 100px) !important; margin: 0px !important; height: 32px !important; letter-spacing: 0.24px !important; color: #000000 !important; padding-left: 4px !important;" value="` + data["section_title"] + `" disabled="">
                <div class="whatsapp-menu-item-action-btns-wrapper">
                    <a onclick="open_and_update_whatsapp_section_modal('` + data["whatsapp_menu_section_id"] + `')">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M13.3736 2.62638C14.2088 3.46154 14.2088 4.81562 13.3736 5.65079L6.22097 12.8034C6.0555 12.9689 5.84972 13.0883 5.62395 13.1499L2.56665 13.9837C2.23206 14.075 1.92503 13.7679 2.01629 13.4333L2.8501 10.376C2.91167 10.1503 3.03109 9.9445 3.19656 9.77903L10.3492 2.62638C11.1844 1.79121 12.5385 1.79121 13.3736 2.62638ZM9.76981 4.4736L3.83045 10.4129C3.77529 10.4681 3.73548 10.5367 3.71496 10.6119L3.08754 12.9125L5.38808 12.285C5.46334 12.2645 5.53193 12.2247 5.58709 12.1696L11.5262 6.23004L9.76981 4.4736ZM10.9831 3.26026L10.4033 3.83951L12.1597 5.59655L12.7397 5.0169C13.2248 4.53182 13.2248 3.74534 12.7397 3.26026C12.2547 2.77518 11.4682 2.77518 10.9831 3.26026Z" fill="#0254D7"></path>
                            </svg>
                    </a>
                    <a onclick="open_whatsapp_menu_section_delete_modal('` + data["whatsapp_menu_section_id"] + `')" class="modal-trigger">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path fill-rule="evenodd" clip-rule="evenodd" d="M5.78997 3.33333L5.93819 2.66635C5.97076 2.60661 6.02879 2.52176 6.10562 2.45091C6.19775 2.36595 6.27992 2.33333 6.35185 2.33333H9.31481C9.31449 2.33333 9.31456 2.33334 9.31502 2.33337C9.31797 2.33359 9.33695 2.335 9.36833 2.34383C9.40259 2.35346 9.44447 2.36997 9.48859 2.39625C9.56583 2.44225 9.65609 2.52152 9.72769 2.66283L9.87669 3.33333H5.78997ZM5.15683 4.33333C5.16372 4.33348 5.17059 4.33348 5.17744 4.33333H10.4892C10.4961 4.33348 10.5029 4.33348 10.5098 4.33333H13.1667C13.4428 4.33333 13.6667 4.10948 13.6667 3.83333C13.6667 3.55719 13.4428 3.33333 13.1667 3.33333H10.9011L10.6918 2.39154L10.6809 2.34267L10.6606 2.29693C10.3311 1.55548 9.67791 1.33333 9.31481 1.33333H6.35185C5.9497 1.33333 5.63682 1.52294 5.42771 1.71576C5.22096 1.90642 5.0796 2.13146 5.00606 2.29693L4.98573 2.34267L4.97487 2.39154L4.76558 3.33333H2.5C2.22386 3.33333 2 3.55719 2 3.83333C2 4.10948 2.22386 4.33333 2.5 4.33333H5.15683ZM3.09959 5.00452C3.37324 4.96747 3.6251 5.15928 3.66215 5.43292L4.65773 12.787C4.7031 12.9453 4.80538 13.1798 4.96108 13.369C5.12181 13.5643 5.29845 13.6667 5.5 13.6667H10.5C10.5571 13.6667 10.6813 13.6397 10.7862 13.543C10.8763 13.4599 11 13.2815 11 12.8867V12.853L11.0045 12.8196L12.0045 5.43292C12.0416 5.15928 12.2934 4.96747 12.5671 5.00452C12.8407 5.04157 13.0325 5.29343 12.9955 5.56708L11.9998 12.922C11.9921 13.5331 11.7842 13.9831 11.4638 14.2783C11.1521 14.5657 10.7763 14.6667 10.5 14.6667H5.5C4.90155 14.6667 4.46708 14.3424 4.18892 14.0044C3.9146 13.671 3.75283 13.2816 3.6828 13.0127L3.67522 12.9836L3.67119 12.9537L2.67119 5.56708C2.63414 5.29343 2.82594 5.04157 3.09959 5.00452Z" fill="#E10E00"></path>
                        </svg>
                    </a>
                </div>
            </div>
        </div>
        <div class="easychat-whatsapp-menu-data-item">
            <div class="easychat-whatsapp-menu-item-header">
                Intents
            </div>
            <div class="whatsapp-menu-item-selected-intent-wrapper">
                <div class="whatsapp-menu-selected-intent-div">
                    <div class="whatsapp-menu-selected-intent-header">
                        Child Intent
                    </div>
                    <div class="whatsapp-menu-selected-intent-items">` + child_trees_html + `</div>

                </div>
                <div class="whatsapp-menu-selected-intent-div">
                    <div class="whatsapp-menu-selected-intent-header">
                        Main Intent
                    </div>
                    <div class="whatsapp-menu-selected-intent-items">` + main_intents_html + `</div>
                </div>
            </div>
        </div>
    </div>`;

    document.getElementsByClassName("easychat-whatsapp-menu-format-data-wrapper")[0].insertAdjacentHTML("beforeend", html);
}

function update_whatsapp_menu_section_html(data) {
    var child_trees_html = '';
    for (var i=0; i<data["child_trees_data"].length; i++) {
        child_trees_html += `<div class="whatsapp-menu-selected-intent-chip child-tree" onclick="open_tree_page('` + data["child_trees_data"][i].intent_pk + `', '` + data["child_trees_data"][i].parent_tree_pk + `', '` + data["child_trees_data"][i].tree_pk + `')" name="` + data["child_trees_data"][i].name + `" description="`+ data["child_trees_data"][i].description +`" short_name="` + data["child_trees_data"][i].short_name + `" value="` + data["child_trees_data"][i].tree_pk + `">` + data["child_trees_data"][i].name + `</div>`
    }

    var main_intents_html = '';
    for (var i=0; i<data["main_intents_data"].length; i++) {
        main_intents_html += `<div class="whatsapp-menu-selected-intent-chip main-intent" onclick="open_intent_page('` + data["main_intents_data"][i].intent_pk + `')" name="` + data["main_intents_data"][i].name + `" description="` + data["main_intents_data"][i].description + `" short_name="` + data["main_intents_data"][i].short_name + `" value="` + data["main_intents_data"][i].intent_pk + `">` + data["main_intents_data"][i].name + `</div>`
    }

    var whatsapp_menu_section_card = document.querySelector('#easychat-whatsapp-menu-item-' + data["whatsapp_menu_section_id"]);
    whatsapp_menu_section_card.querySelector(".whatsapp-menu-item-title-wrapper input").value = data["section_title"];

    var selected_options_divs = whatsapp_menu_section_card.querySelectorAll(".whatsapp-menu-selected-intent-div");
    selected_options_divs[0].querySelector(".whatsapp-menu-selected-intent-items").innerHTML = child_trees_html;
    selected_options_divs[1].querySelector(".whatsapp-menu-selected-intent-items").innerHTML = main_intents_html;
}

function reload_dropdown(dropdown_id) {
    $('#' + dropdown_id).multiselect({
        columns: 1,
        placeholder: 'Select Intent',
        search: true,
        searchOptions: {
            'default': 'Search Intent'
        },
        selectAll: false,
        action: "reload"
    });
}

function add_default_new_section(child_tree_pk_list) {
    save_whatsapp_menu_section("", "Section title", child_tree_pk_list);
}

function update_select_intent_dropdown(child_tree_pk_list, main_intent_pk_list) {
    var child_tree_optgroup = document.getElementById("optgroup-child-tree");
    for (var i=0; i<child_tree_pk_list.length; i++){
        if (child_tree_optgroup && child_tree_optgroup.querySelector('[value="' + child_tree_pk_list[i] + '"]')) {
            child_tree_optgroup.querySelector('[value="' + child_tree_pk_list[i] + '"]').remove();
        }
    }

    var main_intent_optgroup = document.getElementById("optgroup-main-intent");
    for (var i=0; i<main_intent_pk_list.length; i++) {
        if (main_intent_optgroup && main_intent_optgroup.querySelector('[value="' + main_intent_pk_list[i] + '"]')) {
            main_intent_optgroup.querySelector('[value="' + main_intent_pk_list[i] + '"]').remove();
        }
    }

    var already_selected_options = document.querySelectorAll(".already-selected");
    for (var i=0; i<already_selected_options.length; i++) {
        already_selected_options[i].classList.remove("already-selected");
    }

    if (child_tree_optgroup && !child_tree_optgroup.children.length) {
        child_tree_optgroup.remove();
    }

    if (main_intent_optgroup && !main_intent_optgroup.children.length) {
        main_intent_optgroup.remove();
    }

    // reload_dropdown('easychat_whatsapp_menu_intent_list');
    add_onchange_function();
}

function save_whatsapp_menu_section(whatsapp_menu_section_id="", section_title="", child_tree_pk_list=[]) {
    if (!section_title){
        section_title = document.getElementById("whatsapp-menu-section-title").value;
    }

    if (!section_title) {
        showToast("Please add valid section title");
        return;
    }

    var main_intent_pk_list = [];

    if (!child_tree_pk_list.length){
        var child_trees = document.getElementById("child_intent_group").children;
        for (var i=0; i<child_trees.length; i++) {
            child_tree_pk_list.push(child_trees[i].getAttribute("value"));
        }

        var main_intents = document.getElementById("main_intent_group").children;
        for (var i=0; i<main_intents.length; i++) {
            main_intent_pk_list.push(main_intents[i].getAttribute("value"));
        }
    }

    if (!child_tree_pk_list.length && !main_intent_pk_list.length) {
        showToast("Please select atleast one child tree or main intent from dropdown");
        return;
    }

    var json_string = JSON.stringify({
        bot_id: SELECTED_BOT_OBJ_ID,
        tree_pk: TREE_PK,
        whatsapp_menu_section_id: whatsapp_menu_section_id,
        section_title: section_title,
        child_tree_pk_list: child_tree_pk_list,
        main_intent_pk_list: main_intent_pk_list
    })
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var xhttp = new XMLHttpRequest();
    var params = 'json_string=' + json_string
    xhttp.open("POST", "/chat/save-whatsapp-menu-section/", false);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.setRequestHeader('X-CSRFToken', get_csrf_token());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);

            if (response["status"] == 200) {
                if (whatsapp_menu_section_id == response["data"]["whatsapp_menu_section_id"]) {
                    update_whatsapp_menu_section_html(response["data"]);
                    showToast("Section details edited successfully")
                } else {
                    add_whatsapp_menu_section_html(response["data"]);
                    showToast("Section created successfully");
                }
                update_select_intent_dropdown(child_tree_pk_list, main_intent_pk_list);
                enable_or_disable_add_section_btn();
                edit_main_intents_selected = 0;
            } else {
                showToast(response["message"]);
            }
            $('#easychat_whatsapp_add_section_modal').modal("close");
        }
    }
    xhttp.send(params);
}

function remove_already_selected_intent() {
    var already_selected_options = document.querySelectorAll(".already-selected");
    already_selected_options.forEach(option => {
        option.remove();
    })

    if (document.getElementById("optgroup-child-tree") && !document.getElementById("optgroup-child-tree").children.length) {
        document.getElementById("optgroup-child-tree").remove();
    }

    if (document.getElementById("optgroup-main-intent") && !document.getElementById("optgroup-main-intent").children.length) {
        document.getElementById("optgroup-main-intent").remove();
    }
}

function open_and_update_whatsapp_section_modal(whatsapp_section_id) {
    reset_add_section_modal();
    remove_already_selected_intent();
    var whatsapp_menu_section_card = document.getElementById("easychat-whatsapp-menu-item-" + whatsapp_section_id);

    var child_trees_selected = whatsapp_menu_section_card.querySelectorAll(".child-tree");
    var main_intents_selected = whatsapp_menu_section_card.querySelectorAll(".main-intent");

    edit_main_intents_selected = main_intents_selected.length;

    var section_title = whatsapp_menu_section_card.querySelector(".whatsapp-menu-item-title-wrapper input").value;

    var html = '';

    if (child_trees_selected.length) {
        if (!document.getElementById("optgroup-child-tree")) {
            document.getElementById("easychat_whatsapp_menu_intent_list").insertAdjacentHTML("afterbegin", `<optgroup id="optgroup-child-tree" label="Child Intent"></optgroup>`);
        }
        var child_tree_optgroup = document.getElementById("optgroup-child-tree");
        html = '';
        for (var i=0; i<child_trees_selected.length; i++) {
            html += `<option class="already-selected" value="` + child_trees_selected[i].getAttribute("value") + `" selected>` + child_trees_selected[i].getAttribute("name") + `</option>`;
        }
        child_tree_optgroup.insertAdjacentHTML("afterbegin", html);
    }
    
    if (main_intents_selected.length) {
        if (!document.getElementById("optgroup-main-intent")) {
            document.getElementById("easychat_whatsapp_menu_intent_list").insertAdjacentHTML("beforeend", `<optgroup id="optgroup-main-intent" label="Main Intent"></optgroup>`);
        }
        var main_intent_optgroup = document.getElementById("optgroup-main-intent");

        html = '';
        for (var i=0; i<main_intents_selected.length; i++) {
            html += `<option class="already-selected" value="` + main_intents_selected[i].getAttribute("value") + `" selected>` + main_intents_selected[i].getAttribute("name") + `</option>`;
        }
        main_intent_optgroup.insertAdjacentHTML("afterbegin", html);
    }

    $('#easychat_whatsapp_menu_intent_list').multiselect("reload");
    add_onchange_function();
    document.getElementById("whatsapp-menu-section-title").value = section_title;

    let checked_child_trees_elements = []
    if ($('#easychat_whatsapp_menu_intent_list_div ul li.optgroup:first span').text() === "Child Intent") {
        checked_child_trees_elements = $("#easychat_whatsapp_menu_intent_list_div ul li.optgroup:first input:checked");
    }
    
    $('#child_intent_group').empty();
    for (var i=0; i<checked_child_trees_elements.length; i++) {
        $('#child_intent_group').append('<div id="div_' + checked_child_trees_elements[i].id + '" value="' + checked_child_trees_elements[i].value + '"><span><b><svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M8 8.5C8.55228 8.5 9 8.94772 9 9.5C9 10.0523 8.55228 10.5 8 10.5C7.44772 10.5 7 10.0523 7 9.5C7 8.94772 7.44772 8.5 8 8.5ZM4 8.5C4.55228 8.5 5 8.94772 5 9.5C5 10.0523 4.55228 10.5 4 10.5C3.44772 10.5 3 10.0523 3 9.5C3 8.94772 3.44772 8.5 4 8.5ZM8 5C8.55228 5 9 5.44772 9 6C9 6.55228 8.55228 7 8 7C7.44772 7 7 6.55228 7 6C7 5.44772 7.44772 5 8 5ZM4 5C4.55228 5 5 5.44772 5 6C5 6.55228 4.55228 7 4 7C3.44772 7 3 6.55228 3 6C3 5.44772 3.44772 5 4 5ZM8 1.5C8.55228 1.5 9 1.94772 9 2.5C9 3.05228 8.55228 3.5 8 3.5C7.44772 3.5 7 3.05228 7 2.5C7 1.94772 7.44772 1.5 8 1.5ZM4 1.5C4.55228 1.5 5 1.94772 5 2.5C5 3.05228 4.55228 3.5 4 3.5C3.44772 3.5 3 3.05228 3 2.5C3 1.94772 3.44772 1.5 4 1.5Z" fill="white"/></svg></b>' + checked_child_trees_elements[i].title + ' <a id="cross_' + checked_child_trees_elements[i].id + '" onclick="remove_selected_intent(this)"> <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2.3938 2.25L9.60619 9.75" stroke="white" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"/><path d="M9.6062 2.25L2.39381 9.75" stroke="white" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"/></svg></a></span></div>');
    }
    if ($('#child_intent_group').is(':empty')) {
        $('#child_intent_group').append("-");
    }

    let checked_main_intent_elements = []
    if ($('#easychat_whatsapp_menu_intent_list_div ul li.optgroup:last span').text() === "Main Intent") {
        checked_main_intent_elements = $('#easychat_whatsapp_menu_intent_list_div ul li.optgroup:last input:checked');
    }

    $('#main_intent_group').empty();
    for (var i=0; i<checked_main_intent_elements.length; i++) {
        $('#main_intent_group').append('<div id="div_' + checked_main_intent_elements[i].id + '" value="' + checked_main_intent_elements[i].value + '"><span><b><svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M8 8.5C8.55228 8.5 9 8.94772 9 9.5C9 10.0523 8.55228 10.5 8 10.5C7.44772 10.5 7 10.0523 7 9.5C7 8.94772 7.44772 8.5 8 8.5ZM4 8.5C4.55228 8.5 5 8.94772 5 9.5C5 10.0523 4.55228 10.5 4 10.5C3.44772 10.5 3 10.0523 3 9.5C3 8.94772 3.44772 8.5 4 8.5ZM8 5C8.55228 5 9 5.44772 9 6C9 6.55228 8.55228 7 8 7C7.44772 7 7 6.55228 7 6C7 5.44772 7.44772 5 8 5ZM4 5C4.55228 5 5 5.44772 5 6C5 6.55228 4.55228 7 4 7C3.44772 7 3 6.55228 3 6C3 5.44772 3.44772 5 4 5ZM8 1.5C8.55228 1.5 9 1.94772 9 2.5C9 3.05228 8.55228 3.5 8 3.5C7.44772 3.5 7 3.05228 7 2.5C7 1.94772 7.44772 1.5 8 1.5ZM4 1.5C4.55228 1.5 5 1.94772 5 2.5C5 3.05228 4.55228 3.5 4 3.5C3.44772 3.5 3 3.05228 3 2.5C3 1.94772 3.44772 1.5 4 1.5Z" fill="white"/></svg></b>' + checked_main_intent_elements[i].title + ' <a id="cross_' + checked_main_intent_elements[i].id + '" onclick="remove_selected_intent(this)"><svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2.3938 2.25L9.60619 9.75" stroke="white" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"/><path d="M9.6062 2.25L2.39381 9.75" stroke="white" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"/></svg></a></span></div>');
    }
    if ($('#main_intent_group').is(':empty')) {
        $('#main_intent_group').append("-");
    }

    document.getElementById("easychat_whatsapp_add_section_modal").setAttribute("whatsapp-section-id", whatsapp_section_id);
    document.querySelector("#easychat_whatsapp_add_section_modal .modal-heading-text-div").innerText = "Edit Section";
    update_section_title_chars();
    $('#easychat_whatsapp_add_section_modal').modal("open");
    enable_or_disable_add_section_save_btn();
}

function open_add_whatsapp_new_section_modal() {
    edit_main_intents_selected = 0;
    reset_add_section_modal();
    remove_already_selected_intent();
    $('#easychat_whatsapp_menu_intent_list').multiselect("reload");
    add_onchange_function();
    enable_or_disable_dropdown_check_boxes();
    document.getElementById("easychat_whatsapp_add_section_modal").setAttribute("whatsapp-section-id", "");
    document.querySelector("#easychat_whatsapp_add_section_modal .modal-heading-text-div").innerText = "Add Section";
    $('#easychat_whatsapp_add_section_modal').modal("open");
    enable_or_disable_add_section_save_btn();
}

function add_options_after_deleting_whatsapp_menu_section(whatsapp_section_id) {
    var whatsapp_menu_section_card = document.getElementById("easychat-whatsapp-menu-item-" + whatsapp_section_id);

    var child_trees_selected = whatsapp_menu_section_card.querySelectorAll(".child-tree");
    var main_intents_selected = whatsapp_menu_section_card.querySelectorAll(".main-intent");

    var child_trees_optgroup = document.getElementById("optgroup-child-tree");

    if (!child_trees_optgroup && child_trees_selected.length) {
        document.getElementById("easychat_whatsapp_menu_intent_list").insertAdjacentHTML("afterbegin", `<optgroup id="optgroup-child-tree" label="Child Intent"></optgroup>`);
        child_trees_optgroup = document.getElementById("optgroup-child-tree");
    }

    var html = '';

    for (var i=0; i<child_trees_selected.length; i++) {
        html += `<option value="` + child_trees_selected[i].getAttribute("value") + `">` + child_trees_selected[i].getAttribute("name") + `</option>`
    }

    if (html) {
        child_trees_optgroup.insertAdjacentHTML('afterbegin', html);
    }

    var main_intent_optgroup = document.getElementById("optgroup-main-intent");

    if (!main_intent_optgroup && main_intents_selected.length) {
        document.getElementById("easychat_whatsapp_menu_intent_list").insertAdjacentHTML("beforeend", `<optgroup id="optgroup-main-intent" label="Main Intent"></optgroup>`);
        main_intent_optgroup = document.getElementById("optgroup-main-intent");
    }

    html = '';

    for (var i=0; i<main_intents_selected.length; i++) {
        html += `<option value="` + main_intents_selected[i].getAttribute("value") + `">` + main_intents_selected[i].getAttribute("name") + `</option>`
    }

    if (html) {
        main_intent_optgroup.insertAdjacentHTML('afterbegin', html);
    }
}


function delete_whatsapp_menu_section(whatsapp_menu_section_id) {
    var json_string = JSON.stringify({
        bot_id: SELECTED_BOT_OBJ_ID,
        whatsapp_menu_section_id: whatsapp_menu_section_id
    })
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var xhttp = new XMLHttpRequest();
    var params = 'json_string=' + json_string
    xhttp.open("POST", "/chat/delete-whatsapp-menu-section/", false);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.setRequestHeader('X-CSRFToken', get_csrf_token());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);

            if (response["status"] == 200){
                add_options_after_deleting_whatsapp_menu_section(whatsapp_menu_section_id);
                document.getElementById("easychat-whatsapp-menu-item-" + whatsapp_menu_section_id).remove();
                enable_or_disable_add_section_btn();
                $('#easychat_whatsapp_menu_delete_modal').modal('close');
                showToast("Section deleted successfully");
            } else {
                showToast(response["message"])
            }
        }
    }
    xhttp.send(params);
}

function open_whatsapp_menu_section_delete_modal(whatsapp_menu_section_id) {
    document.querySelector("#easychat_whatsapp_menu_delete_modal .termination-buttons .termination-yes-btn").setAttribute("onclick", "delete_whatsapp_menu_section('" + whatsapp_menu_section_id + "')")
    $('#easychat_whatsapp_menu_delete_modal').modal("open");
}


function preview_whatsapp_menu() {

    $('.easychat-whatsapp-sync-preview-data-wrapper').hide();

    var whatsapp_menu_sections = document.getElementsByClassName("easychat-whatsapp-menu-item-wrapper");
    if (!whatsapp_menu_sections.length) {
        showToast("Please add atleast one section to see the preview.");
        return;
    }

    var html = `<div class="easychat-whatsapp-sync-preview-header">` + document.getElementById("whatsapp-list-message-header").value + `</div>`;

    var child_trees = null;
    var main_intents = null;

    var is_checked_pointer_shown = false;

    for (var i=0; i<whatsapp_menu_sections.length; i++) {
        html += `<div class="easychat-whatsapp-sync-preview-green-header">` + whatsapp_menu_sections[i].querySelector(".whatsapp-menu-item-title-wrapper input").value + `</div>`;

        child_trees = whatsapp_menu_sections[i].querySelectorAll(".child-tree");
        main_intents = whatsapp_menu_sections[i].querySelectorAll(".main-intent");

        for (var j=0; j<child_trees.length; j++) {
            html += `<div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <div class="preview-text-div">
                    <div class="easychat-whatsapp-sync-preview-subheader">` + child_trees[j].getAttribute("short_name") + `</div>
                    <div class="easychat-whatsapp-sync-preview-item-value">` + child_trees[j].getAttribute("description") + `</div>
                </div>`;
            if (!is_checked_pointer_shown) {
                html += `<span style="display: flex; align-items: center;">
                        <svg width="12" height="13" viewBox="0 0 12 13" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M5.9172 2.16048C8.39748 2.16048 10.4081 4.17114 10.4081 6.65141C10.4081 9.13168 8.39748 11.1423 5.9172 11.1423C3.43693 11.1423 1.42627 9.13168 1.42627 6.65141C1.42627 4.17114 3.43693 2.16048 5.9172 2.16048ZM5.9172 2.83401C3.80891 2.83401 2.09981 4.54312 2.09981 6.65141C2.09981 8.7597 3.80891 10.4688 5.9172 10.4688C8.02549 10.4688 9.7346 8.7597 9.7346 6.65141C9.7346 4.54312 8.02549 2.83401 5.9172 2.83401ZM5.91566 3.95657C7.40313 3.95657 8.60895 5.1624 8.60895 6.64987C8.60895 8.13733 7.40313 9.34316 5.91566 9.34316C4.42819 9.34316 3.22236 8.13733 3.22236 6.64987C3.22236 5.1624 4.42819 3.95657 5.91566 3.95657Z" fill="#0254D7"/>
                        </svg>
                    </span>
                </div>`;
                is_checked_pointer_shown = true;
            } else {
                html += `<span style="display: flex; align-items: center;">
                        <svg width="12" height="13" viewBox="0 0 12 13" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path fill-rule="evenodd" clip-rule="evenodd" d="M1.42627 6.2749C1.42627 3.7959 3.43821 1.78397 5.9172 1.78397C8.3962 1.78397 10.4081 3.7959 10.4081 6.2749C10.4081 8.75389 8.3962 10.7658 5.9172 10.7658C3.43821 10.7658 1.42627 8.75389 1.42627 6.2749ZM2.32443 6.27487C2.32443 8.25987 3.93219 9.86762 5.91718 9.86762C7.90217 9.86762 9.50992 8.25987 9.50992 6.27487C9.50992 4.28988 7.90217 2.68213 5.91718 2.68213C3.93219 2.68213 2.32443 4.28988 2.32443 6.27487Z" fill="#CBCACA"/>
                        </svg>      
                    </span>
                </div>`;
            }
        }

        for (var j=0; j<main_intents.length; j++) {
            html += `<div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <div class="preview-text-div">
                    <div class="easychat-whatsapp-sync-preview-subheader">` + main_intents[j].getAttribute("short_name") + `</div>
                    <div class="easychat-whatsapp-sync-preview-item-value">` + main_intents[j].getAttribute("description") + `</div>
                </div>`;
            if (!is_checked_pointer_shown) {
                html += `<span style="display: flex; align-items: center;">
                        <svg width="12" height="13" viewBox="0 0 12 13" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M5.9172 2.16048C8.39748 2.16048 10.4081 4.17114 10.4081 6.65141C10.4081 9.13168 8.39748 11.1423 5.9172 11.1423C3.43693 11.1423 1.42627 9.13168 1.42627 6.65141C1.42627 4.17114 3.43693 2.16048 5.9172 2.16048ZM5.9172 2.83401C3.80891 2.83401 2.09981 4.54312 2.09981 6.65141C2.09981 8.7597 3.80891 10.4688 5.9172 10.4688C8.02549 10.4688 9.7346 8.7597 9.7346 6.65141C9.7346 4.54312 8.02549 2.83401 5.9172 2.83401ZM5.91566 3.95657C7.40313 3.95657 8.60895 5.1624 8.60895 6.64987C8.60895 8.13733 7.40313 9.34316 5.91566 9.34316C4.42819 9.34316 3.22236 8.13733 3.22236 6.64987C3.22236 5.1624 4.42819 3.95657 5.91566 3.95657Z" fill="#0254D7"/>
                        </svg>
                    </span>
                </div>`;
                is_checked_pointer_shown = true;
            } else {
                html += `<span style="display: flex; align-items: center;">
                        <svg width="12" height="13" viewBox="0 0 12 13" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path fill-rule="evenodd" clip-rule="evenodd" d="M1.42627 6.2749C1.42627 3.7959 3.43821 1.78397 5.9172 1.78397C8.3962 1.78397 10.4081 3.7959 10.4081 6.2749C10.4081 8.75389 8.3962 10.7658 5.9172 10.7658C3.43821 10.7658 1.42627 8.75389 1.42627 6.2749ZM2.32443 6.27487C2.32443 8.25987 3.93219 9.86762 5.91718 9.86762C7.90217 9.86762 9.50992 8.25987 9.50992 6.27487C9.50992 4.28988 7.90217 2.68213 5.91718 2.68213C3.93219 2.68213 2.32443 4.28988 2.32443 6.27487Z" fill="#CBCACA"/>
                        </svg>      
                    </span>
                </div>`;
            }
        }

        document.querySelector(".easychat-whatsapp-sync-preview-data-div").innerHTML = html;
        $('.easychat-whatsapp-sync-preview-data-wrapper').show();
    }
}

function open_tree_page(intent_pk, parent_pk, tree_pk) {
    window.open('/chat/edit-tree/?intent_pk=' + intent_pk + '&parent_pk=' + parent_pk + '&tree_pk=' + tree_pk + '&selected_language=en', '_blank');
}

function open_intent_page(intent_pk) {
    window.open('/chat/edit-intent/?intent_pk=' + intent_pk + '&selected_language=en', '_blank');
}

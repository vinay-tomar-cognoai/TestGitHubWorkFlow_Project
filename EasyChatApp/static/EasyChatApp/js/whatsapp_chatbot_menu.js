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
        save_section_btn.classList.remove("disable-video-recoder-save-value");
        save_section_btn.setAttribute("onclick", "save_whatsapp_menu_section('" + document.getElementById("easychat_whatsapp_add_section_modal").getAttribute("whatsapp-section-id") + "');");
    } else {
        save_section_btn.classList.add("disable-video-recoder-save-value");
        save_section_btn.setAttribute("onclick", "return false;")
    }
}

function enable_or_disable_dropdown_check_boxes() {
    var quick_recommendations_selected = document.getElementsByClassName("main-intent").length + $('#easychat_whatsapp_menu_intent_list_div ul li.optgroup-main-intent-class.optgroup input:checked').length - edit_main_intents_selected;
    var input_checkboxes = $('#easychat_whatsapp_menu_intent_list_div ul li.optgroup-main-intent-class.optgroup input')
    if (quick_recommendations_selected >= node_intent_data[selected_node].whatsapp_quick_recommendations_allowed) {
        for (var i=0; i<input_checkboxes.length; i++) {
            if (!input_checkboxes[i].checked) {
                input_checkboxes[i].disabled = true;
                input_checkboxes[i].parentElement.classList.add("disable-video-recoder-save-value");
            }
        }
    } else {
        for (var i=0; i<input_checkboxes.length; i++) {
            input_checkboxes[i].disabled = false;
            input_checkboxes[i].parentElement.classList.remove("disable-video-recoder-save-value");
        }
    }
}

function enable_or_disable_add_section_btn() {
    var total_options_selected = document.querySelectorAll(".child-tree").length + document.querySelectorAll(".main-intent").length;
    var add_section_btn = document.getElementById("whatsapp-menu-add-section-btn");
    if (total_options_selected >= 10) {
        add_section_btn.classList.add("disable-video-recoder-save-value");
        // add_section_btn.setAttribute("onclick", "return false;");
    } else {
        add_section_btn.classList.remove("disable-video-recoder-save-value");
        // add_section_btn.setAttribute("onclick", "open_add_whatsapp_new_section_modal()");
    }

    // var preview_section_btn = document.getElementById("whatsapp-menu-preview-section-btn");
    // if (document.querySelectorAll(".easychat-whatsapp-menu-item-wrapper").length) {
    //     preview_section_btn.classList.remove("disable-video-recoder-save-value");
    //     preview_section_btn.setAttribute("onclick", "preview_whatsapp_menu()");
    // } else {
    //     preview_section_btn.classList.add("disable-video-recoder-save-value");
    //     preview_section_btn.setAttribute("onclick", "return false;");
    //     document.getElementsByClassName("easychat-whatsapp-sync-preview-data-wrapper")[0].style.display = "none";
    // }
}

function add_onchange_function() {
    $('#easychat_whatsapp_menu_intent_list_div ul li.optgroup-child-tree-class.optgroup input').change(() => {
        $('#child_intent_group').empty()
        $('#easychat_whatsapp_menu_intent_list_div ul li.optgroup-child-tree-class.optgroup input:checked').each((indx, element) => {
            $('#child_intent_group').append('<div id="div_' + element.id + '" value="' + element.value + '"><span><b><svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M8 8.5C8.55228 8.5 9 8.94772 9 9.5C9 10.0523 8.55228 10.5 8 10.5C7.44772 10.5 7 10.0523 7 9.5C7 8.94772 7.44772 8.5 8 8.5ZM4 8.5C4.55228 8.5 5 8.94772 5 9.5C5 10.0523 4.55228 10.5 4 10.5C3.44772 10.5 3 10.0523 3 9.5C3 8.94772 3.44772 8.5 4 8.5ZM8 5C8.55228 5 9 5.44772 9 6C9 6.55228 8.55228 7 8 7C7.44772 7 7 6.55228 7 6C7 5.44772 7.44772 5 8 5ZM4 5C4.55228 5 5 5.44772 5 6C5 6.55228 4.55228 7 4 7C3.44772 7 3 6.55228 3 6C3 5.44772 3.44772 5 4 5ZM8 1.5C8.55228 1.5 9 1.94772 9 2.5C9 3.05228 8.55228 3.5 8 3.5C7.44772 3.5 7 3.05228 7 2.5C7 1.94772 7.44772 1.5 8 1.5ZM4 1.5C4.55228 1.5 5 1.94772 5 2.5C5 3.05228 4.55228 3.5 4 3.5C3.44772 3.5 3 3.05228 3 2.5C3 1.94772 3.44772 1.5 4 1.5Z" fill="white"/></svg></b>' + element.title + ' <a id="cross_' + element.id + '" onclick="remove_selected_intent(this)"> <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2.3938 2.25L9.60619 9.75" stroke="white" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"/><path d="M9.6062 2.25L2.39381 9.75" stroke="white" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"/></svg></a></span></div>')
        })
        if ($('#child_intent_group').is(':empty')) {
            $('#child_intent_group').append("-");
        }
        enable_or_disable_add_section_save_btn();
    });

    $('#easychat_whatsapp_menu_intent_list_div ul li.optgroup-main-intent-class.optgroup input').change(() => {
        $('#main_intent_group').empty()
        $('#easychat_whatsapp_menu_intent_list_div ul li.optgroup-main-intent-class.optgroup input:checked').each((indx, element) => {
            $('#main_intent_group').append('<div id="div_' + element.id + '" value="' + element.value + '"><span><b><svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M8 8.5C8.55228 8.5 9 8.94772 9 9.5C9 10.0523 8.55228 10.5 8 10.5C7.44772 10.5 7 10.0523 7 9.5C7 8.94772 7.44772 8.5 8 8.5ZM4 8.5C4.55228 8.5 5 8.94772 5 9.5C5 10.0523 4.55228 10.5 4 10.5C3.44772 10.5 3 10.0523 3 9.5C3 8.94772 3.44772 8.5 4 8.5ZM8 5C8.55228 5 9 5.44772 9 6C9 6.55228 8.55228 7 8 7C7.44772 7 7 6.55228 7 6C7 5.44772 7.44772 5 8 5ZM4 5C4.55228 5 5 5.44772 5 6C5 6.55228 4.55228 7 4 7C3.44772 7 3 6.55228 3 6C3 5.44772 3.44772 5 4 5ZM8 1.5C8.55228 1.5 9 1.94772 9 2.5C9 3.05228 8.55228 3.5 8 3.5C7.44772 3.5 7 3.05228 7 2.5C7 1.94772 7.44772 1.5 8 1.5ZM4 1.5C4.55228 1.5 5 1.94772 5 2.5C5 3.05228 4.55228 3.5 4 3.5C3.44772 3.5 3 3.05228 3 2.5C3 1.94772 3.44772 1.5 4 1.5Z" fill="white"/></svg></b>' + element.title + ' <a id="cross_' + element.id + '" onclick="remove_selected_intent(this)"><svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2.3938 2.25L9.60619 9.75" stroke="white" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"/><path d="M9.6062 2.25L2.39381 9.75" stroke="white" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"/></svg></a></span></div>')
        })
        if ($('#main_intent_group').is(':empty')) {
            $('#main_intent_group').append("-");
        }
        enable_or_disable_dropdown_check_boxes();
        enable_or_disable_add_section_save_btn();
    });
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
    // enable_or_disable_dropdown_check_boxes();
});

function remove_selected_intent(typ, value) {
    $(`#easychat_whatsapp_menu_intent_list_div ul li.optgroup:${typ} input[value=${value}]`).click()
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

// $(document).ready(function() {
//     $('.modal').modal();
//     $('.modal').on('shown.bs.modal', function(e) {
//         $('#modal-general-feedback').find('input:text, input:file, input:password, select, textarea').val('');
//         $(this).removeData();
//     });

//     $("#whatsapp_preview_close_btn").click(function() {
//         $(this).parent().hide();
//     });
    
//     $("#enable_whatsapp_menu_format").on("change", function(event) {
//         if (this.checked) {
//             $(".easychat-whatsapp-menu-format-data-wrapper").show();
    
//         } else {
//             $('.easychat-whatsapp-menu-format-data-wrapper').hide();
//         }
//     });

//     var whatsapp_short_name_input_field = document.getElementById("whatsapp-short-name-input")
//     whatsapp_short_name_input_field.addEventListener('input', () => {
//         document.getElementById("whatsapp_short_name_field-char-count").innerHTML = whatsapp_short_name_input_field.value.length
//     });

//     var whatsapp_description_input_field = document.getElementById("whatsapp-description-input")
//     whatsapp_description_input_field.addEventListener('input', () => {
//         document.getElementById("whatsapp_description_field-char-count").innerHTML = whatsapp_description_input_field.value.length
//     });

//     // enable_or_disable_add_section_btn();

//     document.getElementById("whatsapp-menu-section-title").onkeyup = update_section_title_chars;
// });

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

function update_select_intent_dropdown(whatsapp_section_id) {
    let whatsapp_data = node_intent_data[selected_node].whatsapp_menu_section_objs[whatsapp_section_id]

    if (!whatsapp_data) {
        return
    }

    let child_tree_pk_list = whatsapp_data.child_tree_details
    let main_intent_pk_list = whatsapp_data.main_intent_details

    var child_tree_optgroup = document.getElementById("optgroup-child-tree");
    for (var i=0; i<child_tree_pk_list.length; i++){
        if (child_tree_optgroup && child_tree_optgroup.querySelector('[value="' + child_tree_pk_list[i].tree_pk + '"]')) {
            child_tree_optgroup.querySelector('[value="' + child_tree_pk_list[i].tree_pk + '"]').remove();
        }
    }

    var main_intent_optgroup = document.getElementById("optgroup-main-intent");
    for (var i=0; i<main_intent_pk_list.length; i++) {
        if (main_intent_optgroup && main_intent_optgroup.querySelector('[value="' + main_intent_pk_list[i].intent_pk + '"]')) {
            main_intent_optgroup.querySelector('[value="' + main_intent_pk_list[i].intent_pk + '"]').remove();
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

    section_title = strip_unwanted_characters(section_title);

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

    reload_dropdown('easychat_whatsapp_menu_intent_list');
    add_onchange_function();
    document.getElementById("whatsapp-menu-section-title").value = section_title;

    var checked_child_trees_elements = document.querySelectorAll("#easychat_whatsapp_menu_intent_list_div ul li.optgroup-child-tree-class.optgroup input:checked");
    $('#child_intent_group').empty();
    for (var i=0; i<checked_child_trees_elements.length; i++) {
        $('#child_intent_group').append('<div id="div_' + checked_child_trees_elements[i].id + '" value="' + checked_child_trees_elements[i].value + '"><span><b><svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M8 8.5C8.55228 8.5 9 8.94772 9 9.5C9 10.0523 8.55228 10.5 8 10.5C7.44772 10.5 7 10.0523 7 9.5C7 8.94772 7.44772 8.5 8 8.5ZM4 8.5C4.55228 8.5 5 8.94772 5 9.5C5 10.0523 4.55228 10.5 4 10.5C3.44772 10.5 3 10.0523 3 9.5C3 8.94772 3.44772 8.5 4 8.5ZM8 5C8.55228 5 9 5.44772 9 6C9 6.55228 8.55228 7 8 7C7.44772 7 7 6.55228 7 6C7 5.44772 7.44772 5 8 5ZM4 5C4.55228 5 5 5.44772 5 6C5 6.55228 4.55228 7 4 7C3.44772 7 3 6.55228 3 6C3 5.44772 3.44772 5 4 5ZM8 1.5C8.55228 1.5 9 1.94772 9 2.5C9 3.05228 8.55228 3.5 8 3.5C7.44772 3.5 7 3.05228 7 2.5C7 1.94772 7.44772 1.5 8 1.5ZM4 1.5C4.55228 1.5 5 1.94772 5 2.5C5 3.05228 4.55228 3.5 4 3.5C3.44772 3.5 3 3.05228 3 2.5C3 1.94772 3.44772 1.5 4 1.5Z" fill="white"/></svg></b>' + checked_child_trees_elements[i].title + ' <a id="cross_' + checked_child_trees_elements[i].id + '" onclick="remove_selected_intent(this)"> <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2.3938 2.25L9.60619 9.75" stroke="white" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"/><path d="M9.6062 2.25L2.39381 9.75" stroke="white" stroke-width="1.30211" stroke-linecap="round" stroke-linejoin="round"/></svg></a></span></div>');
    }
    if ($('#child_intent_group').is(':empty')) {
        $('#child_intent_group').append("-");
    }

    var checked_main_intent_elements = document.querySelectorAll('#easychat_whatsapp_menu_intent_list_div ul li.optgroup-main-intent-class.optgroup input:checked');
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
    reload_dropdown('easychat_whatsapp_menu_intent_list');
    add_onchange_function();
    enable_or_disable_dropdown_check_boxes();
    document.getElementById("easychat_whatsapp_add_section_modal").setAttribute("whatsapp-section-id", "");
    document.querySelector("#easychat_whatsapp_add_section_modal .modal-heading-text-div").innerText = "Add Section";
    $('#easychat_whatsapp_add_section_modal').modal("open");
    enable_or_disable_add_section_save_btn();
}

function add_main_and_child_options(child_trees_selected, main_intents_selected, initial=false) {
    let child_attr = "tree_pk"
    let main_attr = "intent_pk"

    if (initial) {
        child_attr = "pk"
        main_attr = "pk"
    }

    let child_trees_optgroup = document.getElementById("optgroup-child-tree");

    if (!child_trees_optgroup && child_trees_selected.length) {
        document.getElementById("easychat_whatsapp_menu_intent_list").insertAdjacentHTML("afterbegin", `<optgroup id="optgroup-child-tree" label="Child Intent"></optgroup>`);
        child_trees_optgroup = document.getElementById("optgroup-child-tree");
    }

    var html = '';

    for (var i=0; i<child_trees_selected.length; i++) {
        html += `<option value="` + child_trees_selected[i][child_attr] + `">` + child_trees_selected[i].name + `</option>`
    }

    if (html) {
        if (initial) {
            $(child_trees_optgroup).html(html);
        } else {
            $(child_trees_optgroup).prepend(html);
        }
    }

    var main_intent_optgroup = document.getElementById("optgroup-main-intent");

    if (!main_intent_optgroup && main_intents_selected.length) {
        document.getElementById("easychat_whatsapp_menu_intent_list").insertAdjacentHTML("beforeend", `<optgroup id="optgroup-main-intent" label="Main Intent"></optgroup>`);
        main_intent_optgroup = document.getElementById("optgroup-main-intent");
    }

    html = '';

    for (var i=0; i<main_intents_selected.length; i++) {
        html += `<option value="` + main_intents_selected[i][main_attr] + `">` + main_intents_selected[i].name + `</option>`
    }

    if (html) {
        if (initial) {
            $(main_intent_optgroup).html(html);
        } else {
            $(main_intent_optgroup).prepend(html);
        }
    }
}

function add_options_after_deleting_whatsapp_menu_section(whatsapp_section_id) {
    let whatsapp_data = node_intent_data[selected_node].whatsapp_menu_section_objs[whatsapp_section_id]

    let child_trees_selected = whatsapp_data.child_tree_details
    let main_intents_selected = whatsapp_data.main_intent_details

    add_main_and_child_options(child_trees_selected, main_intents_selected)
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
    window.open('/chat/edit-intent/?intent_pk=' + intent_pk + '&tree_pk=' + tree_pk + '&selected_language=en', '_blank');
}

function open_intent_page(intent_pk) {
    window.open('/chat/edit-intent/?intent_pk=' + intent_pk + '&selected_language=en', '_blank');
}

function fill_rhs_with_whatsapp_menu_format_data(data, initial) {
    let whatsapp_menu_title_html = ""
    let whatsapp_menu_section_html = ""
    let section_class = ""
    let section_display = "block"
    if (initial) {
        $("#whatsapp_menu_data").html("")
        $("#whatsapp_menu_title .tab:not(.indicator)").remove()
        if (Object.keys(data).length === 0) {
            $("#whatsapp-menu-preview-section-btn").addClass("disable-video-recoder-save-value")
            $("#whatsapp_menuformat .edit-intent-details-action-btns-wrapper").addClass("disable-video-recoder-save-value")
            return
        } else {
            $("#whatsapp-menu-preview-section-btn").removeClass("disable-video-recoder-save-value")
            $("#whatsapp_menuformat .edit-intent-details-action-btns-wrapper").removeClass("disable-video-recoder-save-value")
        }
    } else {
        let validate = validate_whatsapp_menu_section()

        if (!validate) {
            M.toast({
                "html": "Please complete all sections first!"
            }, 2000);
            return;
        }
    }
    
    let counter = Object.keys(node_intent_data[selected_node].whatsapp_menu_section_objs).length

    if (Object.keys(data).length > 0) {
        let section_counter = 0;
        for (let section of Object.values(data)) {
            section_counter += 1
            if (section_counter === 1) {
                section_class = " active"
                section_display = "block"
            } else {
                section_class = ""
                section_display = 'none'
            }
            let pk = section.pk
            let title =  section.title
            let child_tree_details = section.child_tree_details
            let main_intent_details = section.main_intent_details

            let child_intent_chips_html = `
                <div class="whatsapp-menu-selected-intent-items">
            `

            for (const child of child_tree_details) {
                child_intent_chips_html += `
                <div class="whatsapp-menu-selected-intent-chip child-tree"
                onclick="open_tree_page('${child.intent_pk}', '${child.parent_tree_pk}', '${child.tree_pk}')">${child.name}</div>
                `
            }

            child_intent_chips_html += "</div>"

            let main_intent_chips_html = `
            <div class="whatsapp-menu-selected-intent-items">
            `

            for (const main of main_intent_details) {
                main_intent_chips_html += `
                <div class="whatsapp-menu-selected-intent-chip main-intent"
                onclick="open_intent_page('${main.intent_pk}')">${main.name}</div>
                `
            }

            main_intent_chips_html += "</div>"

            whatsapp_menu_section_html += `
            <div id="whatsapp_menu_item_${section_counter}" style="display: ${section_display}" class="easychat-whatsapp-menu-item-wrapper${section_class}">
                <div class="easychat-whatsapp-menu-data-item">
                    <div class="whatsapp-menu-item-action-btns-wrapper">
                        <a onclick="edit_whatsapp_section(${section_counter})">
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="none"
                                xmlns="http://www.w3.org/2000/svg">
                                <path
                                    d="M13.3736 2.62638C14.2088 3.46154 14.2088 4.81562 13.3736 5.65079L6.22097 12.8034C6.0555 12.9689 5.84972 13.0883 5.62395 13.1499L2.56665 13.9837C2.23206 14.075 1.92503 13.7679 2.01629 13.4333L2.8501 10.376C2.91167 10.1503 3.03109 9.9445 3.19656 9.77903L10.3492 2.62638C11.1844 1.79121 12.5385 1.79121 13.3736 2.62638ZM9.76981 4.4736L3.83045 10.4129C3.77529 10.4681 3.73548 10.5367 3.71496 10.6119L3.08754 12.9125L5.38808 12.285C5.46334 12.2645 5.53193 12.2247 5.58709 12.1696L11.5262 6.23004L9.76981 4.4736ZM10.9831 3.26026L10.4033 3.83951L12.1597 5.59655L12.7397 5.0169C13.2248 4.53182 13.2248 3.74534 12.7397 3.26026C12.2547 2.77518 11.4682 2.77518 10.9831 3.26026Z"
                                    fill="#0254D7"></path>
                            </svg>
                        </a>
                        <a onclick="delete_whatsapp_section(${section_counter}, false)" class="modal-trigger">
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="none"
                                xmlns="http://www.w3.org/2000/svg">
                                <path fill-rule="evenodd" clip-rule="evenodd"
                                    d="M5.78997 3.33333L5.93819 2.66635C5.97076 2.60661 6.02879 2.52176 6.10562 2.45091C6.19775 2.36595 6.27992 2.33333 6.35185 2.33333H9.31481C9.31449 2.33333 9.31456 2.33334 9.31502 2.33337C9.31797 2.33359 9.33695 2.335 9.36833 2.34383C9.40259 2.35346 9.44447 2.36997 9.48859 2.39625C9.56583 2.44225 9.65609 2.52152 9.72769 2.66283L9.87669 3.33333H5.78997ZM5.15683 4.33333C5.16372 4.33348 5.17059 4.33348 5.17744 4.33333H10.4892C10.4961 4.33348 10.5029 4.33348 10.5098 4.33333H13.1667C13.4428 4.33333 13.6667 4.10948 13.6667 3.83333C13.6667 3.55719 13.4428 3.33333 13.1667 3.33333H10.9011L10.6918 2.39154L10.6809 2.34267L10.6606 2.29693C10.3311 1.55548 9.67791 1.33333 9.31481 1.33333H6.35185C5.9497 1.33333 5.63682 1.52294 5.42771 1.71576C5.22096 1.90642 5.0796 2.13146 5.00606 2.29693L4.98573 2.34267L4.97487 2.39154L4.76558 3.33333H2.5C2.22386 3.33333 2 3.55719 2 3.83333C2 4.10948 2.22386 4.33333 2.5 4.33333H5.15683ZM3.09959 5.00452C3.37324 4.96747 3.6251 5.15928 3.66215 5.43292L4.65773 12.787C4.7031 12.9453 4.80538 13.1798 4.96108 13.369C5.12181 13.5643 5.29845 13.6667 5.5 13.6667H10.5C10.5571 13.6667 10.6813 13.6397 10.7862 13.543C10.8763 13.4599 11 13.2815 11 12.8867V12.853L11.0045 12.8196L12.0045 5.43292C12.0416 5.15928 12.2934 4.96747 12.5671 5.00452C12.8407 5.04157 13.0325 5.29343 12.9955 5.56708L11.9998 12.922C11.9921 13.5331 11.7842 13.9831 11.4638 14.2783C11.1521 14.5657 10.7763 14.6667 10.5 14.6667H5.5C4.90155 14.6667 4.46708 14.3424 4.18892 14.0044C3.9146 13.671 3.75283 13.2816 3.6828 13.0127L3.67522 12.9836L3.67119 12.9537L2.67119 5.56708C2.63414 5.29343 2.82594 5.04157 3.09959 5.00452Z"
                                    fill="#E10E00"></path>
                            </svg>
                        </a>
                    </div>
                    <div class="easychat-whatsapp-menu-item-header">Section Name</div>
                    <div class="whatsapp-menu-item-title-wrapper edit-intent-input-with-header-div"
                        style="margin-top: 12px;">
                        <input type="text" class="edit-intent-common-primary-input" readonly
                            style="width: 100% !important; margin: 0px !important; border: 1px solid #CBCACA !important; height: 40px !important; letter-spacing: 0.24px !important; color: #000000 !important; background-color: #ffffff !important;font-size:14px !important"
                            value="${title}" disabled="">

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
                            <div class="child_tree_chip">
                                ${child_intent_chips_html}
                            </div>
                            
                        </div>
                        <div class="whatsapp-menu-selected-intent-div">
                            <div class="whatsapp-menu-selected-intent-header">
                                Main Intent
                            </div>
                            <div class="main_intent_chip">
                                ${main_intent_chips_html}
                            </div>
                            
                        </div>
                    </div>
                </div>
            </div>
            `

            whatsapp_menu_title_html += `
            <li class="tab">
                <a href="#whatsapp_menu_item_${section_counter}" class="${section_class}">
                    <span>${title}</span>
                </a>
            </li>
            `
        }
    } else {
        whatsapp_menu_section_html += `
        <div id="whatsapp_menu_item_${counter+1}" class="easychat-whatsapp-menu-item-wrapper" style="display: none">
            <div class="easychat-whatsapp-menu-data-item">
                <div class="whatsapp-menu-item-action-btns-wrapper">
                    <a onclick="edit_whatsapp_section(${counter+1})">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none"
                            xmlns="http://www.w3.org/2000/svg">
                            <path
                                d="M13.3736 2.62638C14.2088 3.46154 14.2088 4.81562 13.3736 5.65079L6.22097 12.8034C6.0555 12.9689 5.84972 13.0883 5.62395 13.1499L2.56665 13.9837C2.23206 14.075 1.92503 13.7679 2.01629 13.4333L2.8501 10.376C2.91167 10.1503 3.03109 9.9445 3.19656 9.77903L10.3492 2.62638C11.1844 1.79121 12.5385 1.79121 13.3736 2.62638ZM9.76981 4.4736L3.83045 10.4129C3.77529 10.4681 3.73548 10.5367 3.71496 10.6119L3.08754 12.9125L5.38808 12.285C5.46334 12.2645 5.53193 12.2247 5.58709 12.1696L11.5262 6.23004L9.76981 4.4736ZM10.9831 3.26026L10.4033 3.83951L12.1597 5.59655L12.7397 5.0169C13.2248 4.53182 13.2248 3.74534 12.7397 3.26026C12.2547 2.77518 11.4682 2.77518 10.9831 3.26026Z"
                                fill="#0254D7"></path>
                        </svg>
                    </a>
                    <a onclick="delete_whatsapp_section(${counter+1}, false)" class="modal-trigger">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none"
                            xmlns="http://www.w3.org/2000/svg">
                            <path fill-rule="evenodd" clip-rule="evenodd"
                                d="M5.78997 3.33333L5.93819 2.66635C5.97076 2.60661 6.02879 2.52176 6.10562 2.45091C6.19775 2.36595 6.27992 2.33333 6.35185 2.33333H9.31481C9.31449 2.33333 9.31456 2.33334 9.31502 2.33337C9.31797 2.33359 9.33695 2.335 9.36833 2.34383C9.40259 2.35346 9.44447 2.36997 9.48859 2.39625C9.56583 2.44225 9.65609 2.52152 9.72769 2.66283L9.87669 3.33333H5.78997ZM5.15683 4.33333C5.16372 4.33348 5.17059 4.33348 5.17744 4.33333H10.4892C10.4961 4.33348 10.5029 4.33348 10.5098 4.33333H13.1667C13.4428 4.33333 13.6667 4.10948 13.6667 3.83333C13.6667 3.55719 13.4428 3.33333 13.1667 3.33333H10.9011L10.6918 2.39154L10.6809 2.34267L10.6606 2.29693C10.3311 1.55548 9.67791 1.33333 9.31481 1.33333H6.35185C5.9497 1.33333 5.63682 1.52294 5.42771 1.71576C5.22096 1.90642 5.0796 2.13146 5.00606 2.29693L4.98573 2.34267L4.97487 2.39154L4.76558 3.33333H2.5C2.22386 3.33333 2 3.55719 2 3.83333C2 4.10948 2.22386 4.33333 2.5 4.33333H5.15683ZM3.09959 5.00452C3.37324 4.96747 3.6251 5.15928 3.66215 5.43292L4.65773 12.787C4.7031 12.9453 4.80538 13.1798 4.96108 13.369C5.12181 13.5643 5.29845 13.6667 5.5 13.6667H10.5C10.5571 13.6667 10.6813 13.6397 10.7862 13.543C10.8763 13.4599 11 13.2815 11 12.8867V12.853L11.0045 12.8196L12.0045 5.43292C12.0416 5.15928 12.2934 4.96747 12.5671 5.00452C12.8407 5.04157 13.0325 5.29343 12.9955 5.56708L11.9998 12.922C11.9921 13.5331 11.7842 13.9831 11.4638 14.2783C11.1521 14.5657 10.7763 14.6667 10.5 14.6667H5.5C4.90155 14.6667 4.46708 14.3424 4.18892 14.0044C3.9146 13.671 3.75283 13.2816 3.6828 13.0127L3.67522 12.9836L3.67119 12.9537L2.67119 5.56708C2.63414 5.29343 2.82594 5.04157 3.09959 5.00452Z"
                                fill="#E10E00"></path>
                        </svg>
                    </a>
                </div>
                <div class="easychat-whatsapp-menu-item-header">Section Name</div>
                <div class="whatsapp-menu-item-title-wrapper edit-intent-input-with-header-div"
                    style="margin-top: 12px;">
                    <input type="text" class="edit-intent-common-primary-input" readonly
                        style="width: 100% !important; margin: 0px !important; border: 1px solid #CBCACA !important; height: 40px !important; letter-spacing: 0.24px !important; color: #000000 !important; background-color: #ffffff !important;"
                        value="New Section" disabled="">

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
                        <div class="child_tree_chip">
                        -
                        </div>
                    </div>
                    <div class="whatsapp-menu-selected-intent-div">
                        <div class="whatsapp-menu-selected-intent-header">
                            Main Intent
                        </div>
                        <div class="main_intent_chip">
                        -
                        </div>
                    </div>
                </div>
            </div>
        </div>
        `
        whatsapp_menu_title_html += `
        <li class="tab">
            <a href="#whatsapp_menu_item_${counter+1}" class="active">
                <span>New Section</span>
            </a>
        </li>
        `
        $("#whatsapp_menu_title a").removeClass("active")
        $("#whatsapp_menu_data .easychat-whatsapp-menu-item-wrapper").removeClass("active")
        $("#whatsapp_menu_data .easychat-whatsapp-menu-item-wrapper").hide()
    }

    $("#whatsapp_menu_data").append(whatsapp_menu_section_html)
    $("#whatsapp_menu_title").append(whatsapp_menu_title_html)

    try {
        $('.tabs:not(#response_widget_tab_wrapper)').tabs()
    } catch {}

    if (Object.keys(data).length === 0) {
        node_intent_data[selected_node].whatsapp_menu_section_objs[counter+1] = {
            title: "New Section",
            pk: "",
            child_tree_details: [],
            main_intent_details: []
        }
        edit_whatsapp_section(counter+1)
    }
}

function add_optgroups() {
    let child_trees_optgroup = document.getElementById("optgroup-child-tree");

    if (!child_trees_optgroup) {
        document.getElementById("easychat_whatsapp_menu_intent_list").insertAdjacentHTML("afterbegin", `<optgroup id="optgroup-child-tree" label="Child Intent"></optgroup>`);
    }

    let main_intent_optgroup = document.getElementById("optgroup-main-intent");

    if (!main_intent_optgroup) {
        document.getElementById("easychat_whatsapp_menu_intent_list").insertAdjacentHTML("beforeend", `<optgroup id="optgroup-main-intent" label="Main Intent"></optgroup>`);
    }
}

function edit_whatsapp_section(id) {
    $("#whatsapp-menu-preview-section-btn").addClass("disable-video-recoder-save-value")
    $("#whatsapp_menu_title a").removeClass("active")
    $("#whatsapp_menu_data .easychat-whatsapp-menu-item-wrapper").removeClass("active")
    $("#whatsapp_menu_data .easychat-whatsapp-menu-item-wrapper").hide()
    $("#whatsapp_menu_edit_section").addClass("active")
    $("#whatsapp_menu_edit_section").show()
    $("#whatsapp_menu_title a").addClass("disable-video-recoder-save-value")
    $('#child_intent_group').empty()
    $('#main_intent_group').empty()
    $('#whatsapp_menu_format_note').show()

    let whatsapp_data = node_intent_data[selected_node].whatsapp_menu_section_objs[id]

    $("#edit_section_save").attr("onclick", `save_whatsapp_section(${id})`)
    $("#edit_section_cancel").attr("onclick", `cancel_whatsapp_section(${id})`)
    $("#edit_section_title").val(whatsapp_data.title)
    $("#whatsapp-add-section-title-chars").text(whatsapp_data.title.length)

    add_optgroups()
    add_options_after_deleting_whatsapp_menu_section(id)
    $('#easychat_whatsapp_menu_intent_list').multiselect("reload");

    for (const child of whatsapp_data.child_tree_details) {
        $(`#easychat_whatsapp_menu_intent_list_div ul li.optgroup:first input[value=${child.tree_pk}]`).click()
    }

    for (const main of whatsapp_data.main_intent_details) {
        $(`#easychat_whatsapp_menu_intent_list_div ul li.optgroup:last input[value=${main.intent_pk}]`).click()
    }

}

function cancel_whatsapp_section(id) {
    $("#whatsapp_menu_title a").removeClass("disable-video-recoder-save-value")
    $(`#easychat_whatsapp_menu_intent_list_div ul li.optgroup input:checked`).click()
    $("#edit_section_title").val("New Section")

    $("#whatsapp_menu_edit_section").removeClass("active")
    $("#whatsapp_menu_edit_section").hide()
    $(`#whatsapp_menu_title a[href='#whatsapp_menu_item_${id}']`).addClass("active")
    $(`#whatsapp_menu_item_${id}`).show()
    $(`#whatsapp_menu_item_${id}`).addClass("active")
    $('#whatsapp_menu_format_note').hide()

    update_select_intent_dropdown(id)
    $('#easychat_whatsapp_menu_intent_list').multiselect("reload");
    $('.tabs:not(#response_widget_tab_wrapper)').tabs()
}

function update_whatsapp_section(id, title, pk, child_tree_details, main_intent_details) {
    const section_id = "#whatsapp_menu_item_" + id

    $(`${section_id} .edit-intent-common-primary-input`).val(title)
    $(`#whatsapp_menu_title a[href='#whatsapp_menu_item_${id}'] span`).text(title)

    if (child_tree_details.length > 0) {
        let child_intent_chips_html = `
                <div class="whatsapp-menu-selected-intent-items">
            `
        for (const child of child_tree_details) {
            child_intent_chips_html += `
            <div class="whatsapp-menu-selected-intent-chip child-tree"
            onclick="open_tree_page('${child.intent_pk}', '${child.parent_tree_pk}', '${child.tree_pk}')">${child.name}</div>
            `
        }
        child_intent_chips_html += "</div>"
        $(`${section_id} .child_tree_chip`).html(child_intent_chips_html)
    } else {
        $(`${section_id} .child_tree_chip`).html("")
    }

    if (main_intent_details.length > 0) {
        let main_intent_chips_html = `
        <div class="whatsapp-menu-selected-intent-items">
        `

        for (const main of main_intent_details) {
            main_intent_chips_html += `
            <div class="whatsapp-menu-selected-intent-chip main-intent"
            onclick="open_intent_page('${main.intent_pk}')">${main.name}</div>
            `
        }

        main_intent_chips_html += "</div>"
        $(`${section_id} .main_intent_chip`).html(main_intent_chips_html)
    } else {
        $(`${section_id} .main_intent_chip`).html("")
    }

    const whatsapp_section_data = node_intent_data[selected_node].whatsapp_menu_section_objs[id]
    whatsapp_section_data.title = title
    whatsapp_section_data.pk = pk
    whatsapp_section_data.child_tree_details = child_tree_details
    whatsapp_section_data.main_intent_details = main_intent_details

    $("#whatsapp_menu_edit_section").removeClass("active")
    $("#whatsapp_menu_edit_section").hide()
    $(`#whatsapp_menu_title a[href='#whatsapp_menu_item_${id}']`).addClass("active")
    $(`#whatsapp_menu_item_${id}`).show()
    $(`#whatsapp_menu_item_${id}`).addClass("active")
}

function save_whatsapp_section(id) {
    const whatsapp_section_data = node_intent_data[selected_node].whatsapp_menu_section_objs[id]
    let whatsapp_menu_section_id = whatsapp_section_data.pk
    let section_title = $("#edit_section_title").val()
    let child_tree_pk_list = []
    let main_intent_pk_list = []

    child_tree_pk_list = $("#child_intent_group").sortable("toArray", {attribute: "value"})
    main_intent_pk_list = $("#main_intent_group").sortable("toArray", {attribute: "value"})

    if (section_title == null){
        section_title = document.getElementById("whatsapp-menu-section-title").value;
    }

    section_title = strip_unwanted_characters(section_title);
    section_title = section_title.trim();

    if (!section_title) {
        showToast("Please add valid section title");
        return;
    }

    if (!child_tree_pk_list.length && !main_intent_pk_list.length) {
        showToast("Please select atleast one child tree or main intent from dropdown");
        return;
    }

    var json_string = JSON.stringify({
        bot_id: SELECTED_BOT_OBJ_ID,
        tree_pk: node_intent_data[selected_node].tree_pk,
        whatsapp_menu_section_id: whatsapp_menu_section_id,
        section_title: section_title,
        child_tree_pk_list: child_tree_pk_list,
        main_intent_pk_list: main_intent_pk_list,
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
                    showToast("Section details edited successfully")
                } else {
                    showToast("Section created successfully");
                }

                whatsapp_menu_section_id = response["data"]["whatsapp_menu_section_id"]
                section_title = response["data"]["section_title"]
                child_tree_pk_list = response["data"]["child_trees_data"]
                main_intent_pk_list = response["data"]["main_intents_data"]

                update_whatsapp_section(id, section_title, whatsapp_menu_section_id, child_tree_pk_list, main_intent_pk_list)
                update_select_intent_dropdown(id);
                $('#easychat_whatsapp_menu_intent_list').multiselect("reload");
                enable_or_disable_add_section_btn()
                cancel_whatsapp_section()
                $("#whatsapp-menu-preview-section-btn").removeClass("disable-video-recoder-save-value")
                $("#whatsapp_menuformat .edit-intent-details-action-btns-wrapper").removeClass("disable-video-recoder-save-value")
            } else {
                showToast(response["message"]);
            }
        }
    }
    xhttp.send(params);
}

function delete_whatsapp_section(id, confirm) {
    if (!confirm) {
        $("#easychat_whatsapp_menu_delete_modal").modal("open")
        $("#easychat_whatsapp_menu_delete_modal .termination-yes-btn").attr("onclick", `delete_whatsapp_section(${id}, true)`)
        return
    }
    $("#easychat_whatsapp_menu_delete_modal").modal("close")

    const whatsapp_section_data = node_intent_data[selected_node].whatsapp_menu_section_objs[id]
    const whatsapp_menu_section_id = whatsapp_section_data.pk

    if (!whatsapp_menu_section_id) {
        $(`#whatsapp_menu_item_${id}`).remove()
        $(`#whatsapp_menu_title a[href='#whatsapp_menu_item_${id}']`).parent().remove()
        if ($("#whatsapp_menu_title .tab:not(.indicator)").length === 0) {
            $("#whatsapp_menu_title").prepend(
                `<li class="tab" style="display: none;">
                <a href="#dummy">
                    <span>Dummy</span>
                </a>
            </li>`
            )
        }
        let last_section_id = Object.keys(node_intent_data[selected_node].whatsapp_menu_section_objs).at(-2)
        cancel_whatsapp_section(last_section_id)
        delete node_intent_data[selected_node].whatsapp_menu_section_objs[id]
        $('.tabs:not(#response_widget_tab_wrapper)')
        showToast("Section deleted successfully");
        if ($(".easychat-whatsapp-menu-item-wrapper").length === 1) {
            $("#whatsapp-menu-preview-section-btn").addClass("disable-video-recoder-save-value")
            $("#whatsapp_menuformat .edit-intent-details-action-btns-wrapper").addClass("disable-video-recoder-save-value")
        } else {
            $("#whatsapp-menu-preview-section-btn").removeClass("disable-video-recoder-save-value")
            $("#whatsapp_menuformat .edit-intent-details-action-btns-wrapper").removeClass("disable-video-recoder-save-value")
        }
        return
    }

    let json_string = JSON.stringify({
        bot_id: SELECTED_BOT_OBJ_ID,
        whatsapp_menu_section_id: whatsapp_menu_section_id
    })
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    const xhttp = new XMLHttpRequest();
    const params = 'json_string=' + json_string
    xhttp.open("POST", "/chat/delete-whatsapp-menu-section/", false);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.setRequestHeader('X-CSRFToken', get_csrf_token());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);

            if (response["status"] == 200){
                add_optgroups()
                add_options_after_deleting_whatsapp_menu_section(id);
                $('#easychat_whatsapp_menu_intent_list').multiselect("reload");
                $(`#whatsapp_menu_item_${id}`).remove()
                $(`#whatsapp_menu_title a[href='#whatsapp_menu_item_${id}']`).parent().remove()
                if ($("#whatsapp_menu_title .tab:not(.indicator)").length === 0) {
                    $("#whatsapp_menu_title").prepend(
                        `<li class="tab" style="display: none;">
                        <a href="#dummy">
                            <span>Dummy</span>
                        </a>
                    </li>`
                    )
                }
                let last_section_id = Object.keys(node_intent_data[selected_node].whatsapp_menu_section_objs).at(-2)
                cancel_whatsapp_section(last_section_id)
                delete node_intent_data[selected_node].whatsapp_menu_section_objs[id]
                $('.tabs:not(#response_widget_tab_wrapper)')
                showToast("Section deleted successfully");
                enable_or_disable_add_section_btn()
            } else {
                showToast(response["message"])
            }
        }
    }
    xhttp.send(params);
}

function validate_whatsapp_menu_section() {
    let whatsapp_menu_section_cards = Object.values(node_intent_data[selected_node].whatsapp_menu_section_objs).filter(function(section) {
        return Boolean(section)
    });

    if (whatsapp_menu_section_cards.length > 0 && !whatsapp_menu_section_cards.at(-1).pk) {
        return false
    }

    return true
}

function save_intent_whatsapp_menu_format() {
    let intent_pk = null

    if (window.location.href.indexOf("intent_pk=") != -1) {

        let url_parameters = get_url_vars();
        intent_pk = url_parameters["intent_pk"];
    }

    selected_bot_pk_list = [BOT_ID];

    const category_obj_pk = $("#select-intent-category").val()

    if (selected_bot_pk_list.length == 0) {
        M.toast({
            "html": "Select atleast one bot in which intent will be supported"
        }, 2000);
        return;
    }

    let enable_whatsapp_menu_format = node_intent_data[selected_node].enable_whatsapp_menu_format;
    let whatsapp_list_message_header = ""

    if (enable_whatsapp_menu_format) {

        whatsapp_list_message_header = node_intent_data[selected_node].other_settings.whatsapp_list_message_header
        if (whatsapp_list_message_header == "") {
            M.toast({
                'html': 'Please enter WhatsApp list message header.'
            }, 2000);
            return;
        } else if (whatsapp_list_message_header.length > 20) {
            M.toast({
                'html': 'WhatsApp list message header cannot be greater than 20 characters.'
            }, 2000);
            return;
        }

        let validate = validate_whatsapp_menu_section()

        if (!validate) {
            M.toast({
                "html": "Please complete all sections first!"
            }, 2000);
            return;
        }

        let whatsapp_menu_section_cards = Object.values(node_intent_data[selected_node].whatsapp_menu_section_objs).filter(function(section) {
            return Boolean(section.pk)
        });
        if (!whatsapp_menu_section_cards.length) {
            M.toast({
                "html": "Please add at least one section in menu format"
            }, 2000);
            return;
        }

        var total_options_selected = document.querySelectorAll(".child-tree").length + document.querySelectorAll(".main-intent").length;
        if (total_options_selected < 4) {
            M.toast({
                "html": "Total quick recommendations and child intents selected in whatsapp chatbot menu should be greater than 3."
            }, 2000);
            return;
        } else if (total_options_selected > 10) {
            M.toast({
                "html": "Total quick recommendations and child intents selected in whatsapp chatbot menu should be less than 11."
            }, 2000);
            return;
        }
    }

    let json_string = JSON.stringify({
        intent_pk,
        selected_bot_pk_list,
        enable_whatsapp_menu_format,
        category_obj_pk,
        whatsapp_list_message_header
    })
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: '/chat/save-intent-whatsapp-menu-format/',
        type: "POST",
        headers: {
            'X-CSRFToken': get_csrf_token(),
        },
        data: {
            json_string: json_string
        },
        dataType: "json",
        async: false,
        success: function (response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            bot_response_preview()
            $("#preview_show_hide_div").click()
            if (response['status'] == 200) {
                if (!enable_whatsapp_menu_format) {
                    $("#whatsapp_menuformat .edit-intent-details-action-btns-wrapper").addClass("disable-video-recoder-save-value")
                }
                M.toast({
                    'html': "intent whatsapp menu format saved successfully!"
                }, 1000);
            } else {
                M.toast({
                    'html': "Unable to save the Intent whatsapp menu format!"
                }, 2000);
            }
        }
    });

}

function save_tree_whatsapp_menu_format() {
    let tree_pk = node_intent_data[selected_node].tree_pk

    let enable_whatsapp_menu_format = node_intent_data[selected_node].enable_whatsapp_menu_format;
    let whatsapp_list_message_header = ""

    if (enable_whatsapp_menu_format) {

        whatsapp_list_message_header = node_intent_data[selected_node].other_settings.whatsapp_list_message_header
        if (whatsapp_list_message_header == "") {
            M.toast({
                'html': 'Please enter whatsapp list message header.'
            }, 2000);
            return;
        } else if (whatsapp_list_message_header.length > 20) {
            M.toast({
                'html': 'Whatsapp list message header cannot be greater than 20 characters.'
            }, 2000);
            return;
        }

        let validate = validate_whatsapp_menu_section()

        if (!validate) {
            M.toast({
                "html": "Please complete all sections first!"
            }, 2000);
            return;
        }

        let whatsapp_menu_section_cards = Object.values(node_intent_data[selected_node].whatsapp_menu_section_objs).filter(function(section) {
            return Boolean(section.pk)
        });
        if (!whatsapp_menu_section_cards.length) {
            M.toast({
                "html": "Please add at least one section in menu format"
            }, 2000);
            return;
        }

        var total_options_selected = document.querySelectorAll(".child-tree").length + document.querySelectorAll(".main-intent").length;
        if (total_options_selected < 4) {
            M.toast({
                "html": "Total quick recommendations and child intents selected in whatsapp chatbot menu should be greater than 3."
            }, 2000);
            return;
        } else if (total_options_selected > 10) {
            M.toast({
                "html": "Total quick recommendations and child intents selected in whatsapp chatbot menu should be less than 11."
            }, 2000);
            return;
        }
    }

    let json_string = JSON.stringify({
        tree_pk,
        enable_whatsapp_menu_format,
        whatsapp_list_message_header
    })
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: '/chat/save-tree-whatsapp-menu-format/',
        type: "POST",
        headers: {
            'X-CSRFToken': get_csrf_token(),
        },
        data: {
            json_string: json_string
        },
        dataType: "json",
        async: false,
        success: function (response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            bot_response_preview()
            $("#preview_show_hide_div").click()
            if (response['status'] == 200) {
                if (!enable_whatsapp_menu_format) {
                    $("#whatsapp_menuformat .edit-intent-details-action-btns-wrapper").addClass("disable-video-recoder-save-value")
                }
                M.toast({
                    'html': "Tree whatsapp menu format saved successfully!"
                }, 1000);
            } else {
                M.toast({
                    'html': "Unable to save Tree whatsapp menu format!"
                }, 2000);
            }
        }
    });

}

function decide_save_whatsapp_menu_format() {
    if (selected_node == 1) {
        save_intent_whatsapp_menu_format()
    } else {
        save_tree_whatsapp_menu_format()
    }

    if ($(".easychat-whatsapp-menu-item-wrapper").length === 1 || !$("#whatsapp_menu_format_cb").prop("checked")) {
        $("#whatsapp-menu-preview-section-btn").addClass("disable-video-recoder-save-value")
        $("#whatsapp_menuformat .edit-intent-details-action-btns-wrapper").addClass("disable-video-recoder-save-value")
    } else {
        $("#whatsapp-menu-preview-section-btn").removeClass("disable-video-recoder-save-value")
        $("#whatsapp_menuformat .edit-intent-details-action-btns-wrapper").removeClass("disable-video-recoder-save-value")
    }
}

function build_preview_whatsapp_menu_format(sections, header) {
    let html = `
    <div class="preview-bot-message-wrapper">
    <div class="whatsapp-menu-format-bot-preview-wrapper" style="width:100%;">
        <div class="easychat-whatsapp-sync-preview-data-div">
            <div class="easychat-whatsapp-sync-preview-header">${header}</div>
    `

    for (const section of sections) {
        html += `
        <div class="easychat-whatsapp-sync-preview-green-header">${section.title}</div>
        `

        let childs = section.child_tree_details.concat(section.main_intent_details)

        for (const child of childs) {
            html += `
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <div class="preview-text-div">
                    <div class="easychat-whatsapp-sync-preview-subheader">${child.name}
                    </div>
                </div><span style="display: flex; align-items: center;">
                    <svg width="21" height="21" viewBox="0 0 21 21" fill="none"
                        xmlns="http://www.w3.org/2000/svg">
                        <path
                            d="M10.8896 2.94727C15.3128 2.94727 18.8984 6.53291 18.8984 10.956C18.8984 15.3792 15.3128 18.9648 10.8896 18.9648C6.46651 18.9648 2.88086 15.3792 2.88086 10.956C2.88086 6.53291 6.46651 2.94727 10.8896 2.94727ZM10.8896 4.14839C7.12987 4.14839 4.08199 7.19628 4.08199 10.956C4.08199 14.7158 7.12987 17.7637 10.8896 17.7637C14.6494 17.7637 17.6973 14.7158 17.6973 10.956C17.6973 7.19628 14.6494 4.14839 10.8896 4.14839ZM10.8869 6.15028C13.5395 6.15028 15.6899 8.30066 15.6899 10.9533C15.6899 13.6059 13.5395 15.7563 10.8869 15.7563C8.23425 15.7563 6.08387 13.6059 6.08387 10.9533C6.08387 8.30066 8.23425 6.15028 10.8869 6.15028Z"
                            fill="#0254D7" />
                    </svg>
                </span>
            </div>
            `
        }
    }
    html += `</div></div></div>`

    return html
}

function cancel_bot_whatsapp_menu_format(confirm) {

    if (!confirm) {
        $("#easychat_form_widget_resetall_modal").modal("open")
        $("#easychat_form_widget_resetall_modal .termination-yes-btn").attr("onclick", "cancel_bot_whatsapp_menu_format(true)")
        return
    }

    const whatsapp_section_data = node_intent_data[selected_node].whatsapp_menu_section_objs

    $("#whatsapp_menu_format_cb").prop("checked", false).trigger("change")
    $("#whatsapp-menu-add-section-btn").removeClass("disable-video-recoder-save-value")

    for (const id of Object.keys(whatsapp_section_data)) {
        if (whatsapp_section_data[id]) {
            delete_whatsapp_section(id, true)
        }
    }

}

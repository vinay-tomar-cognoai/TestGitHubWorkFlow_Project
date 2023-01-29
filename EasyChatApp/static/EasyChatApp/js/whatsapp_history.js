
function delete_whatsapp_bot_filter() {
    div = document.getElementById("whatsapp-bot-div");
    div.parentNode.removeChild(div);
    document.getElementById("select-whatsapp-bot-filter").value = ""
}

function delete_whatsapp_number_filter() {
    div = document.getElementById("whatsapp-number-div");
    div.parentNode.removeChild(div);
    document.getElementById("filter-whatsapp-number").value = ""
}

function delete_whatsapp_date_filter() {
    div = document.getElementById("whatsapp-date-div");
    div.parentNode.removeChild(div);
    document.getElementById("add-whatsapp-date-key").value = ""
}

function check_whatsapp_filter() {
    var value = document.getElementById("check-whatsapp-filter-select").value;
    if (value == "1") {
        document.getElementById("div-whatsapp-bot").style.display = "block";
        document.getElementById("div-whatsapp-number").style.display = "none";
        document.getElementById("div-whatsapp-received-date").style.display = "none";
    } else if (value == "2") {
        document.getElementById("div-whatsapp-bot").style.display = "none";
        document.getElementById("div-whatsapp-number").style.display = "block";
        document.getElementById("div-whatsapp-received-date").style.display = "none";
    } else if (value == "3") {
        document.getElementById("div-whatsapp-bot").style.display = "none";
        document.getElementById("div-whatsapp-number").style.display = "none";
        document.getElementById("div-whatsapp-received-date").style.display = "block";
    } else {
        document.getElementById("div-whatsapp-bot").style.display = "none";
        document.getElementById("div-whatsapp-number").style.display = "none";
        document.getElementById("div-whatsapp-received-date").style.display = "none";
    }
}

function add_whatsapp_filter_option() {
    var value = document.getElementById("check-whatsapp-filter-select").value;
    if (value == "") {
        showToast("Kindly select a valid filter", 2000);
        return;
    }
    if (value == "1") {
        select_bot = document.getElementById("select-whatsapp-bot-filter");
        bot_value = select_bot.value;
        bot_name = select_bot.options[select_bot.selectedIndex].text;
        var flag = false;
        try {
            val = document.getElementById("add-whatsapp-bot-key").value
            flag = false
        } catch {
            flag = true
        }
        if (flag == true) {
            if (value != "" && bot_value != "") {
                html = '<br><div class="row" id="whatsapp-bot-div"><div class="col s4">'
                html += '<input id="add-whatsapp-bot-key" value="Filter by bot" disabled>'
                html += '</div>'
                html += '<div class="col s4">'
                html += '<input id="add-whatsapp-bot-key" value="' + bot_name + '" disabled>'
                html += '</div><a class="red-text text-darken-3" onclick="delete_whatsapp_bot_filter()"><i class="material-icons">delete</i></a></div>'
                div_html = document.getElementById("add-whatsapp-filter-buttons")
                div_html.insertAdjacentHTML('beforeend', html);
            } else {
                showToast("Kindly select a valid filter", 2000);
                return;
            }
        } else {
            showToast("This filter is already present.", 2000);
            return;
        }
    } else if (value == "2") {
        whatsapp_number = document.getElementById("filter-whatsapp-number").value;
        if (whatsapp_number == "") {
            showToast("Kindly select a valid filter", 2000);
            return;
        }

        var flag = false;
        try {
            val = document.getElementById("add-whatsapp-number").value
            flag = false
        } catch {
            flag = true
        }
        if (flag == true) {
            if (value != "" && whatsapp_number != "") {
                html = '<br><div class="row" id="whatsapp-number-div"><div class="col s4">'
                html += '<input id="add-whatsapp-number" value="Filter by WhatsApp Number" disabled>'
                html += '</div>'
                html += '<div class="col s4">'
                html += '<input id="add-whatsapp-number-value" value= " ' + whatsapp_number + ' " disabled>'
                html += '</div><a class="red-text text-darken-3" onclick="delete_whatsapp_number_filter()"><i class="material-icons">delete</i></a></div>'
                div_html = document.getElementById("add-whatsapp-filter-buttons")
                div_html.insertAdjacentHTML('beforeend', html);
            } else {
                showToast("Kindly select a valid filter.", 2000);
                return;
            }
        } else {
            showToast("This filter is already present.", 2000);
            return;
        }
    } else if (value == "3") {
        whatsapp_date = document.getElementById("whatsapp-filter-date").value;
        if (whatsapp_date == "") {
            showToast("Kindly select a valid filter", 2000);
            return;
        }
        var flag = false;
        try {
            val = document.getElementById("add-whatsapp-date-key").value
            flag = false
        } catch {
            flag = true
        }
        if (flag == true) {
            if (value != "" && whatsapp_date != "") {
                html = '<br><div class="row" id="whatsapp-date-div"><div class="col s4">'
                html += '<input id="add-channels-key" value="Filter by Received Date" disabled>'
                html += '</div>'
                html += '<div class="col s4">'
                html += '<input id="add-whatsapp-date-key" value= " ' + whatsapp_date + ' " disabled>'
                html += '</div><a class="red-text text-darken-3" onclick="delete_whatsapp_date_filter()"><i class="material-icons">delete</i></a></div>'
                div_html = document.getElementById("add-whatsapp-filter-buttons")
                div_html.insertAdjacentHTML('beforeend', html);
            } else {
                showToast("Kindly select a valid filter.", 2000);
                return;
            }
        } else {
            showToast("This filter is already present.", 2000);
            return;
        }
    }
}

function select_whatsapp_filter() {
    let is_filter_applied = false
    bot = document.getElementById("select-whatsapp-bot-filter").value;
    var bot_id = ""
    if (bot != "") {
        bot_id = "?bot_id=" + bot;
        is_filter_applied = true
    }
    whatsapp_number = document.getElementById("filter-whatsapp-number").value;
    var whatsapp_mobile = ""
    if (whatsapp_number != "") {
        if (bot == "") {
            whatsapp_mobile = "?mobile=" + whatsapp_number
        } else {
            whatsapp_mobile = "&mobile=" + whatsapp_number
        }
        is_filter_applied = true
    }
    whatsapp_date_value = document.getElementById("whatsapp-filter-date").value;
    var whatsapp_date = ""
    if (whatsapp_date_value != "") {

        if (! (new Date().setHours(0, 0, 0, 0) >= new Date(whatsapp_date_value).setHours(0, 0, 0, 0))) {
            M.toast({
                "html": "Received Date should not be Future Date"
            });
            return;
        }
        if (bot == "") {
            if (whatsapp_number == "") {
                whatsapp_date = "?received_date=" + whatsapp_date_value;
            } else {
                whatsapp_date = "&received_date=" + whatsapp_date_value;
            }
        } else {
            whatsapp_date = "&received_date=" + whatsapp_date_value;
        }
        is_filter_applied = true
    }
    
    if(!is_filter_applied){
        return;
    }
    
    value = bot_id + whatsapp_mobile + whatsapp_date
    window.location = window.location.origin + window.location.pathname + value;
}

function search_from_whatsapp_history_table() {
    // Declare variables
    var input = document.getElementById("whatsapp-history-search-bar");
    var filter = input.value.toUpperCase();
    var table = document.getElementById("whatsapp-history-table");
    var trs = table.tBodies[0].getElementsByTagName("tr");

    var tds
    let tr_counter = trs.length;
    for (var i = 0; i < trs.length; i++) {
    tds = trs[i].getElementsByTagName("td");
        trs[i].style.display = "none";
        for (var i2 = 0; i2 < tds.length; i2++) {
            if (tds[i2].innerHTML.toUpperCase().indexOf(filter) > -1) {
                trs[i].style.display = "";
                tr_counter--;
                continue;
            }
        }
    }

    if(tr_counter == trs.length) {
        document.getElementById("whatsapp_history_no_data_found").style.display = "block";
        document.getElementById("whatsapp-history-table").style.display = "none";
        document.getElementById("datatable-info-pagination-div").style.display = "none";
       
    }
    else {
        document.getElementById("whatsapp_history_no_data_found").style.display = "none";
        document.getElementById("whatsapp-history-table").style.display = "block";
        document.getElementById("datatable-info-pagination-div").style.display = "flex";
    }
}

$(document).ready(function() {

    $("#easychat-data-table-length-select").select2({ 
        dropdownCssClass : "easychat-datatable-option-container" 
    });

    $("#select-whatsapp-bot-filter").select2({
        dropdownCssClass : "select-user-id-field-dropdown",
        placeholder: 'Filter by bot ',
    })
    .on("select2:open", function () {
        $("#modal-whatsapp-history-filter").removeAttr("tabindex");
        $('input.select2-search__field').attr('placeholder', 'Search Bot');
    })
});



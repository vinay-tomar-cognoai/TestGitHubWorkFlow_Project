var flow_analytics_counter = 0;
var flow_completion_data = null;
var intent_analytics_page = 0;
var whatsapp_block_analytics_page = 0;
var whatsapp_catalogue_analytics_page = 0;
var whatsapp_block_analytics_scrolled = false;
var whatsapp_catalogue_analytics_scrolled = false;
var catalogue_table_body_removed = false;
var show_block_spam_data = true;
var show_catalogue_data = true;
var is_last_page_whatsapp = false;
var is_last_page_catalogue = false;
var show_intent_data = true;
var intent_analytics_scrolled = false;
var intent_analytics_counter = 1;
var whatsapp_analytics_counter = 1;
var catalogue_analytics_counter
var is_last_page = false;
var date_rules = { year: 'numeric', month: 'short', day: 'numeric' };
var livechat_filter = false;
var myChart = null;
var livechat_global_clear_filter = false;
var default_start_date;
var default_end_date;
var traffic_analytics_page = 0;
var traffic_analytics_scrolled = false;
var is_last_page_traffic = false;
var traffic_analytics_counter = 1;
var show_traffic_data = true;
var traffic_table_sort = null; 

// Welcome banner analytics initializations
var welcome_analytics_page = 0;
var welcome_analytics_scrolled = false;
var is_last_page_welcome = false;
var welcome_analytics_counter = 1;
var show_welcome_data = true;
var welcome_table_sort = null
var conversion_node_analytics_pk = 0;

$(document).ready(function() {
    disable_future_date()
    $("#conversion_analytics_loader").show();
    load_conversion_analytics();
    setTimeout(function(){
        $("#conversion_analytics_loader").hide();
    },300);
    
});

function reset_start_end_date(start_val, end_val) {
    let start_date = $("#" + start_val).attr("current_applied_date");
    let end_date = $("#" + end_val).attr("current_applied_date");
    start_date = start_date ? start_date : default_start_date;
    end_date = end_date ? end_date : default_end_date;
    document.getElementById(start_val).value = start_date;
    document.getElementById(end_val).value = end_date;
}

function load_conversion_analytics(){
    intent_analytics_page = 0;
    traffic_analytics_page = 0;
    welcome_analytics_page = 0
    load_flow_conversion_analytics();
    load_intent_conversion_analytics();
    load_livechat_conersion_analytics();
    load_flow_dropoff_analytics();
    load_traffic_conversion_analytics();
    load_welcome_banner_analytics();
    load_whatsapp_block_analytics();
    load_whatsapp_catalogue_analytics();
}

function set_page_and_load_intent_analytics(){
    intent_analytics_page = 0;
    load_intent_conversion_analytics();
}

function set_page_and_load_whatsapp_block_analytics() {
    whatsapp_block_analytics_page = 0;
    load_whatsapp_block_analytics();
}

function set_page_and_load_whatsapp_catalogue_analytics() {
    whatsapp_catalogue_analytics_page = 0;
    load_whatsapp_catalogue_analytics();
}

function set_page_and_load_traffic_analytics(){
    traffic_analytics_page = 0;
    load_traffic_conversion_analytics();
}

function set_page_and_load_welcome_analytics(){
    welcome_analytics_page = 0;
    load_welcome_banner_analytics();
}
function disable_future_date(){
    var dtToday = new Date();

    var month = dtToday.getMonth() + 1;
    var day = dtToday.getDate();
    var year = dtToday.getFullYear();
    if(month < 10)
        month = '0' + month.toString();
    if(day < 10)
        day = '0' + day.toString();

    var maxDate = year + '-' + month + '-' + day;
    $("[type='date']").attr("max", maxDate)
}
function deselect_all_channels() {
    
    var channel_element_list = document.querySelectorAll(".flow-completion-rate-channels")
    channel_element_list.forEach(function(element){

        element.checked = false;
    });

    channel_element_list = document.querySelectorAll(".intent-analytics-channels")
    channel_element_list.forEach(function(element){

        element.checked = false;
    });

    channel_element_list = document.querySelectorAll(".livechat-analytics-channels")
    channel_element_list.forEach(function(element){

        element.checked = false;
    });

    channel_element_list = document.querySelectorAll(".dropoff-analytics-channels")
    channel_element_list.forEach(function(element){

        element.checked = false;
    });
}


function selected_channels_based_on_global_selected_channel() {

    var channel_element_list = document.querySelectorAll(".conversion-analytics-channels")
    channel_element_list.forEach(function(element){

        if (element.checked) {

            var all_channel_list = document.querySelectorAll("." + element.value)
            all_channel_list.forEach(function(element_one){

                element_one.checked = true;
            })
        }
    });
}
function apply_global_filter(){
        channel_list = [];
        var start_date = "";
        var end_date = "";
        document.getElementById("analytics-custom-date-select-area-flow").style.display = "none";
        document.getElementById("analytics-custom-date-select-area-intent").style.display = "none";
        document.getElementById("analytics-custom-date-select-area-livechat").style.display = "none";
        document.getElementById("analytics-custom-date-select-area-traffic").style.display = "none"; 
        document.getElementById("analytics-custom-date-select-area-welcome").style.display = "none"; 
        document.getElementById("analytics-custom-date-select-area-dropoff").style.display = "none";

        if(document.getElementById('conversion_global_week').checked){
            document.getElementById('conversion_flow_week').checked = true;
            document.getElementById('conversion_intent_week').checked = true;
            document.getElementById('conversion_livechat_week').checked = true;
            document.getElementById('conversion_traffic_week').checked = true;
            document.getElementById('conversion_welcome_week').checked = true;
            document.getElementById('conversion_dropoff_intent_week').checked = true;
            document.getElementById("whatsapp_block_week").checked = true;
            document.getElementById("catalogue_week").checked = true;
        } else if (document.getElementById('conversion_global_month').checked){
            document.getElementById('conversion_flow_month').checked = true;
            document.getElementById('conversion_intent_month').checked = true;
            document.getElementById('conversion_livechat_month').checked = true;
            document.getElementById('conversion_traffic_month').checked = true;
            document.getElementById('conversion_welcome_month').checked = true;
            document.getElementById('conversion_dropoff_intent_month').checked = true;
            document.getElementById("whatsapp_block_month").checked = true;
            document.getElementById("catalogue_month").checked = true;

        } else if (document.getElementById('conversion_global_three_month').checked){
            document.getElementById('conversion_flow_three_month').checked = true;
            document.getElementById('conversion_intent_three_month').checked = true;
            document.getElementById('conversion_livechat_three_month').checked = true;
            document.getElementById('conversion_traffic_three_month').checked = true;
            document.getElementById('conversion_welcome_three_month').checked = true;
            document.getElementById('conversion_dropoff_intent_three_month').checked = true;
            document.getElementById("whatsapp_block_three_month").checked = true;
            document.getElementById("catalogue_three_month").checked = true;

        } else if (document.getElementById('conversion_global_beg').checked){
            document.getElementById('conversion_flow_beg').checked = true;
            document.getElementById('conversion_intent_beg').checked = true;
            document.getElementById('conversion_livechat_beg').checked = true;
            document.getElementById('conversion_traffic_beg').checked = true;   
            document.getElementById('conversion_welcome_beg').checked = true;
            document.getElementById('conversion_dropoff_intent_beg').checked = true;
            document.getElementById('whatsapp_block_beg').checked = true;
            document.getElementById("catalogue_beginning").checked = true;

        } else if (document.getElementById('conversion_global_custom_date_btn').checked){
            start_date = document.getElementById("conversion_global_custom_start_date").value;
            end_date = document.getElementById("conversion_global_custom_end_date").value;
            var today = new Date();
            var today = today.getFullYear() + "-" + String(today.getMonth() + 1).padStart(2, '0') + "-" + String(today.getDate()).padStart(2, '0');

            if (Date.parse(start_date) > Date.parse(end_date)){
               
                M.toast({
                    "html": "Start Date should be smaller than End Date"
                }, 2000);

                reset_start_end_date("conversion_global_custom_start_date","conversion_global_custom_end_date");

                return;
            }

            if(Date.parse(today) < Date.parse(end_date)){
                M.toast({
                    "html": "End date cannot be greater than today's date."
                }, 2000);

                reset_start_end_date("conversion_global_custom_start_date","conversion_global_custom_end_date");
                
                return;
            }

            if (Date.parse(start_date) > Date.parse(today)){
                M.toast({
                    "html": "Start date cannot be greater than today's date."
                }, 2000);
                
                reset_start_end_date("conversion_global_custom_start_date","conversion_global_custom_end_date");

                return;
            }

            $("#conversion_global_custom_start_date").attr("current_applied_date", start_date)
            $("#conversion_global_custom_end_date").attr("current_applied_date", end_date)

            document.getElementById('conversion_flow_custom_date_btn').checked = true;
            document.getElementById('conversion_intent_custom_date_btn').checked = true;
            document.getElementById('conversion_livechat_custom_date_btn').checked = true;
            document.getElementById('conversion_traffic_custom_date_btn').checked = true;   
            document.getElementById('conversion_welcome_custom_date_btn').checked = true;
            document.getElementById('conversion_dropoff_intent_custom_date_btn').checked = true;
            document.getElementById('whatsapp_block_custom_date_btn').checked = true;
            document.getElementById("catalogue_custom_date_btn").checked = true;

            document.getElementById("conversion_flow_custom_start_date").value = start_date;
            document.getElementById("conversion_flow_custom_end_date").value = end_date;
            document.getElementById("conversion_intent_custom_start_date").value = start_date;
            document.getElementById("conversion_intent_custom_end_date").value = end_date;
            document.getElementById("conversion_livechat_custom_start_date").value = start_date;
            document.getElementById("conversion_livechat_custom_end_date").value = end_date;
            document.getElementById("conversion_traffic_custom_start_date").value = start_date;
            document.getElementById("conversion_traffic_custom_end_date").value = end_date;
            document.getElementById("conversion_welcome_custom_start_date").value = start_date;
            document.getElementById("conversion_welcome_custom_end_date").value = end_date;
            document.getElementById("conversion_dropoff_custom_start_date").value = start_date;
            document.getElementById("conversion_dropoff_custom_end_date").value = end_date;
            document.getElementById("conversion_whatsapp_custom_start_date").value = start_date;
            document.getElementById("conversion_whatsapp_custom_end_date").value = end_date;
            document.getElementById("conversion_catalogue_custom_start_date").value = start_date;
            document.getElementById("conversion_catalogue_custom_end_date").value = end_date;

            document.getElementById("analytics-custom-date-select-area-flow").style.display = "block";
            document.getElementById("analytics-custom-date-select-area-intent").style.display = "block";
            document.getElementById("analytics-custom-date-select-area-livechat").style.display = "block";     
            document.getElementById("analytics-custom-date-select-area-traffic").style.display = "block";   
            document.getElementById("analytics-custom-date-select-area-welcome").style.display = "block";
            document.getElementById("analytics-custom-date-select-area-dropoff").style.display = "block";  
            document.getElementById("analytics-custom-date-select-area-whatsapp").style.display = "block"; 
            document.getElementById("analytics-custom-date-select-area-catalogue").style.display = "block";    
        }

        deselect_all_channels();
        selected_channels_based_on_global_selected_channel();
        
        load_flow_conversion_analytics();
        set_page_and_load_intent_analytics();    
        if(livechat_global_clear_filter == false){
            set_filter_flag_and_load_livechat_analytics();  
        }
        else{
            livechat_filter = false;
            livechat_global_clear_filter = false;
            load_livechat_conersion_analytics();
        }
        set_page_and_load_traffic_analytics();
        set_page_and_load_welcome_analytics();
        load_flow_dropoff_analytics();

        set_page_and_load_whatsapp_block_analytics();

        // For WhatsApp Catalogue
        whatsapp_catalogue_analytics_scrolled = false;
        set_page_and_load_whatsapp_catalogue_analytics();
}

function clear_filter(modal_type){
    default_start_date = window.default_start_date;
    default_end_date = window.default_end_date;

    document.getElementById("analytics-custom-date-select-area-" + modal_type).style.display = "none";
    document.getElementById("conversion_" + modal_type + "_custom_start_date").value = default_start_date;
    document.getElementById("conversion_" + modal_type + "_custom_end_date").value = default_end_date;        
    
    if(modal_type == "flow"){
        document.getElementById('conversion_flow_week').checked = true;
        var channel_element_list = document.querySelectorAll(".flow-completion-rate-channels")
        channel_element_list.forEach(function(element){
            element.checked = false;
        });
        load_flow_conversion_analytics(); 
    } else if (modal_type == "intent"){
        document.getElementById('conversion_intent_week').checked = true;
        var channel_element_list = document.querySelectorAll(".intent-analytics-channels")
        channel_element_list.forEach(function(element){
            element.checked = false;
        });
        set_page_and_load_intent_analytics();
         
    } else if (modal_type == "livechat"){
        document.getElementById('conversion_livechat_week').checked = true;
        var channel_element_list = document.querySelectorAll(".livechat-analytics-channels")
        channel_element_list.forEach(function(element){
            element.checked = false;
        });
        livechat_filter = false;
        load_livechat_conersion_analytics();
    } else if (modal_type == "global"){
        document.getElementById("conversion_flow_custom_start_date").value = default_start_date;
        document.getElementById("conversion_flow_custom_end_date").value = default_end_date;
        document.getElementById("conversion_intent_custom_start_date").value = default_start_date;
        document.getElementById("conversion_intent_custom_end_date").value = default_end_date;
        document.getElementById("conversion_livechat_custom_start_date").value = default_start_date;
        document.getElementById("conversion_livechat_custom_end_date").value = default_end_date;
        document.getElementById("conversion_traffic_custom_start_date").value = default_start_date;
        document.getElementById("conversion_traffic_custom_end_date").value = default_end_date;
        //welcome banner
        document.getElementById("conversion_welcome_custom_start_date").value = default_start_date;
        document.getElementById("conversion_welcome_custom_end_date").value = default_end_date;

        document.getElementById("conversion_dropoff_custom_start_date").value = default_start_date;
        document.getElementById("conversion_dropoff_custom_end_date").value = default_end_date;

        document.getElementById("conversion_catalogue_custom_start_date").value = default_start_date;
        document.getElementById("conversion_catalogue_custom_end_date").value = default_end_date;

        document.getElementById('conversion_global_week').checked = true;

        var channel_element_list = document.querySelectorAll(".conversion-analytics-channels")
        channel_element_list.forEach(function(element){
            element.checked = false;
        });

        for(let j=1; j <= source_length ; j++ ){
                document.getElementById("traffic_source_checkbox"+j).checked = false;
        }
        livechat_global_clear_filter = true;
        apply_global_filter();
    } else if (modal_type == "traffic"){
        document.getElementById('conversion_traffic_week').checked = true;
        for(let j=1; j <= source_length ; j++ ){
                document.getElementById("traffic_source_checkbox"+j).checked = false;
        }
        set_page_and_load_traffic_analytics();
    } else if (modal_type == "welcome"){
        document.getElementById('conversion_welcome_week').checked = true;
        if(document.getElementById("total_clicks"))
        document.getElementById("total_clicks").innerHTML = "..."
        set_page_and_load_welcome_analytics();
        
    } else if (modal_type == "dropoff"){
        document.getElementById("conversion_dropoff_intent_week").checked = true;
        document.getElementById("conversion_dropoff_custom_start_date").value = default_start_date;
        document.getElementById("conversion_dropoff_custom_end_date").value = default_end_date;

        var channel_element_list = document.querySelectorAll(".dropoff-analytics-channels")
        channel_element_list.forEach(function(element){
            element.checked = false;
        });

        load_flow_dropoff_analytics();
    } else if (modal_type == "whatsapp") {
        $("input[name=whatsapp_block_analytics_type_filter]").prop("checked", false)
        document.getElementById("whatsapp_block_week").checked = true;
        document.getElementById("conversion_whatsapp_custom_start_date").value = default_start_date;
        document.getElementById("conversion_whatsapp_custom_end_date").value = default_end_date;

        load_whatsapp_block_analytics();
    } else if (modal_type == "catalogue") {
        $("input[name=whatsapp_catalogue_purchased_filter]").prop("checked", false)
        document.getElementById("catalogue_week").checked = true;
        document.getElementById("conversion_catalogue_custom_start_date").value = default_start_date;
        document.getElementById("conversion_catalogue_custom_end_date").value = default_end_date;
        load_whatsapp_catalogue_analytics();
    }

}


function load_flow_dropoff_analytics_data(data){
    var dropoff_analytics_tbody = document.getElementById("dropoff_conversion_analytics_table_body");
    var selected_language = get_url_vars()["selected_language"];
    var tbody_html = "";

    for (var i = 0; i < data.length; i++) {
        var child_intent_name = data[i].child_intent_name;
        var main_intent_name = data[i].main_intent_name;
        if(customer_dropoff_api_status_code == 200){
            child_intent_name = data[i].child_intent_multilingual_name;
            main_intent_name = data[i].main_intent_multilingual_name;
        }
        tbody_html += `<tr role="row" class="odd">
            <td>` + (i + 1) + `</td>`
        if (customer_dropoff_language_script_type == "rtl") {
            tbody_html += "<td style='direction: rtl; text-align: right;'>" + child_intent_name + "</td>";
            var dropoff_search_bar_id = $("#drop_off_search_bar");
            if (dropoff_search_bar_id.length) {
                mirror_search_bar(dropoff_search_bar_id);
            }
        } else {
            tbody_html += "<td>" + child_intent_name + "</td>";
        }
        tbody_html += `<td>` + data[i].dropoffs + `</td>`
        if (customer_dropoff_language_script_type == "rtl"){
            tbody_html += `<td style='direction: rtl; text-align: right;'><a style="text-decoration: underline;" target="_blank" class="tooltipped" data-position="top" data-tooltip="` + main_intent_name + `" href="/chat/edit-intent/?intent_pk=` + data[i].id + `&selected_language=`+selected_language+ `">` + main_intent_name + `</a></td>`
        } else {
            tbody_html += `<td><a style="text-decoration: underline;" target="_blank" class="tooltipped" data-position="top" data-tooltip="` + main_intent_name + `" href="/chat/edit-intent/?intent_pk=` + data[i].id + `&selected_language=`+selected_language+ `">` + main_intent_name + `</a></td>`
        }

        tbody_html += `<td>
                <div>
                <div class="analytics-table-progressbar">
                    <div class="analytics-table-progressbar-inside" style="width:` + data[i].dropoff_percentage + `%"></div>
                </div>
                <div class="anamytics-table-progress-percent-text">` + data[i].dropoff_percentage + `%</div>
                </div>
            </td>
        </tr>`
    }

    dropoff_analytics_tbody.innerHTML = tbody_html;
    if (customer_dropoff_api_status_code == 300){
        document.getElementById("translation_api_toast_container").style.display = "flex";
        setTimeout(api_fail_message_none, 4000);
    }
}


function load_flow_dropoff_analytics(){

    var bot_pk = get_url_vars()["bot_id"];
    var selected_language = get_url_vars()['selected_language'];
    if (typeof selected_language == 'undefined'){
        selected_language = "en"
    } 
    var dropoff_analytics_filter_result = check_dropoff_conversion_analytics_filter();

    var start_date = dropoff_analytics_filter_result.start_date;
    var end_date = dropoff_analytics_filter_result.end_date;
    var channel_list = dropoff_analytics_filter_result.channel_list;

    var today = new Date();
    var today = today.getFullYear() + "-" + String(today.getMonth() + 1).padStart(2, '0') + "-" + String(today.getDate()).padStart(2, '0');

            if (Date.parse(start_date) > Date.parse(end_date)){

                M.toast({
                    "html": "Start Date should be smaller than End Date"
                }, 2000);

                reset_start_end_date("conversion_dropoff_custom_start_date","conversion_dropoff_custom_end_date");

                return;
            }

            if(Date.parse(today) < Date.parse(end_date)){
                M.toast({
                    "html": "End date cannot be greater than today's date."
                }, 2000);

                reset_start_end_date("conversion_dropoff_custom_start_date","conversion_dropoff_custom_end_date");

                return;
            }

            if (Date.parse(start_date) > Date.parse(today)){
                M.toast({
                    "html": "Start date cannot be greater than today's date."
                }, 2000);

                reset_start_end_date("conversion_dropoff_custom_start_date","conversion_dropoff_custom_end_date");

                return;
            }

    $("#conversion_dropoff_custom_start_date").attr("current_applied_date", start_date)
    $("#conversion_dropoff_custom_end_date").attr("current_applied_date", end_date)
    document.getElementById("dropoff_conversion_analytics_table_body").innerHTML = "";
    document.getElementById("dropoff_conversion_analytics_no_data_found").style.display = "none";
    document.getElementById("dropoff_conversion_analytics_table_scroll").style.display = "block";
    document.getElementById("conversion_dropoff_analytics_loader").style.display = "block";

    var xhttp = new XMLHttpRequest();
    var params = '';
    xhttp.open("GET", "/chat/get-conversion-dropoff-analytics/?bot_pk=" + bot_pk + "&start_date=" + start_date + "&end_date=" + end_date + "&channel_list=" + channel_list + "&selected_language=" + selected_language, true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && (this.status == 200 || response["status"] == 300)) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);
            customer_dropoff_language_script_type = "ltr";
            customer_dropoff_api_status_code = response['status']
            if (response["status"] == 200 || response["status"] == 300) {
                customer_dropoff_language_script_type = response["language_script_type"];
                if (response["flow_dropoff_analytics_data"].length > 0){
                    load_flow_dropoff_analytics_data(response["flow_dropoff_analytics_data"]);
                    document.getElementById("conversion_dropoff_analytics_loader").style.display = "none";

                } else {

                    document.getElementById("conversion_dropoff_analytics_loader").style.display = "none";
                    document.getElementById("dropoff_conversion_analytics_no_data_found").style.display = "flex";
                    document.getElementById("dropoff_conversion_analytics_table_scroll").style.display = "none";
                }

                if (Date.parse(start_date) != Date.parse(end_date)) {
                    show_start_date = convert_to_date_format(start_date);
                    show_end_date = convert_to_date_format(end_date);
                    document.getElementById("dropoff_conversion_analytics_date").innerHTML = "Range : " + show_start_date + " to " + show_end_date;
                } else {
                    show_date = convert_to_date_format(start_date);
                    document.getElementById("dropoff_conversion_analytics_date").innerHTML = "" + show_date;
                }

            } else {
                document.getElementById("conversion_dropoff_analytics_loader").style.display = "none";
                document.getElementById("dropoff_conversion_analytics_no_data_found").style.display = "flex";
                document.getElementById("dropoff_conversion_analytics_table_scroll").style.display = "none";
                document.getElementById("dropoff_conversion_analytics_date").innerHTML = "";
            }
        }
    }
    xhttp.send(params);
}


function load_flow_conversion_analytics(){
        bot_pk = get_url_vars()["bot_id"];
        selected_language = get_url_vars()['selected_language']
        if (typeof selected_language == 'undefined'){
            selected_language = "en"
        }
        flow_conversion_filter_result = check_flow_conversion_analytics_filter();
        var start_date = flow_conversion_filter_result.start_date;
        var end_date = flow_conversion_filter_result.end_date;
        channel_list = flow_conversion_filter_result.channel_list;
        var today = new Date();
        var today = today.getFullYear() + "-" + String(today.getMonth() + 1).padStart(2, '0') + "-" + String(today.getDate()).padStart(2, '0');

        var today = new Date();
        var today = today.getFullYear() + "-" + String(today.getMonth() + 1).padStart(2, '0') + "-" + String(today.getDate()).padStart(2, '0');

            if (Date.parse(start_date) > Date.parse(end_date)){

                M.toast({
                    "html": "Start Date should be smaller than End Date"
                }, 2000);

                reset_start_end_date("conversion_flow_custom_start_date","conversion_flow_custom_end_date");

                return;
            }

            if(Date.parse(today) < Date.parse(end_date)){
                M.toast({
                    "html": "End date cannot be greater than today's date."
                }, 2000);

                reset_start_end_date("conversion_flow_custom_start_date","conversion_flow_custom_end_date");

                return;
            }

            if (Date.parse(start_date) > Date.parse(today)){
                M.toast({
                    "html": "Start date cannot be greater than today's date."
                }, 2000);

                reset_start_end_date("conversion_flow_custom_start_date","conversion_flow_custom_end_date");

                return;
            }

        if(document.getElementById("flow_conversion_analytics_table_body")){
            var table_body = document.getElementById("flow_conversion_analytics_table_body");
            table_body.remove();
        }
        $("#conversion_flow_custom_start_date").attr("current_applied_date", start_date)
        $("#conversion_flow_custom_end_date").attr("current_applied_date", end_date)
        document.getElementById("flow_conversion_analytics_no_data_found").style.display = "none";
        document.getElementById("flow_conversion_analytics_table_scroll").style.display = "block";
        document.getElementById('conversion_flow_analytics_loader').style.display = "block";
        var xhttp = new XMLHttpRequest();
        var params = '';
        xhttp.open("GET", "/chat/get-conversion-flow-analytics/?bot_pk=" + bot_pk +"&start_date=" + start_date + "&end_date=" + end_date + "&channel_list=" + channel_list + "&selected_language=" + selected_language, true);
        xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhttp.onreadystatechange = async function () {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = custom_decrypt(response)
                response = JSON.parse(response);
                if (response["status"] == 200 || response['status'] == 300) {
                    flow_analytics_counter = 0;
                    var table = document.getElementById("flow_conversion_analytics_table");
                    table_body = table.appendChild(document.createElement('tbody'))
                    table_body.setAttribute("id", "flow_conversion_analytics_table_body");
                    flow_completion_data = response["flow_completion_data"];
                    flow_conversion_api_status_code = response['status'];
                    flow_conversion_language_script_type = response["language_script_type"];

                    if (flow_completion_data.length == 0) {
                        document.getElementById("flow_conversion_analytics_no_data_found").style.display = "flex";
                        document.getElementById("flow_conversion_analytics_table_scroll").style.display = "none";
                        flow_completion_data = null;
                    } else {
                        render_flow_conversion_analytics_data(flow_analytics_counter, table_body);
                    }

                    document.getElementById('conversion_flow_analytics_loader').style.display = "none";
                    if (Date.parse(start_date) != Date.parse(end_date)) {
                        show_start_date = convert_to_date_format(start_date);
                        show_end_date = convert_to_date_format(end_date);
                        document.getElementById("flow_conversion_analytics_date").innerHTML = "Range : " + show_start_date + " to " + show_end_date;
                    } else {
                        show_date = convert_to_date_format(start_date);
                        document.getElementById("flow_conversion_analytics_date").innerHTML = "" + show_date;
                    }

                } else {
                    document.getElementById('conversion_flow_analytics_loader').style.display = "none";
                }
            }
        }
        xhttp.send(params);
}

function convert_to_date_format(date_string){
    if(date_string == null)
        return "";
    var parts = date_string.split('-');
    var std_date = new Date(parts[0], parts[1] - 1, parts[2]);
    if((std_date.toDateString()) == null)
        return "";
    var date_format = (std_date.toDateString()).split(' ');
    var res_date = date_format[2] + ' ' + date_format[1] + ' ' + date_format[3]
    return res_date;
}

function check_dropoff_conversion_analytics_filter(){
    var channel_list = [];
    var start_date = "";
    var end_date = "";

    if(document.getElementById('conversion_dropoff_intent_week').checked){
        start_date = document.getElementById("conversion_dropoff_intent_week").getAttribute('start_date_value');
        end_date = document.getElementById("conversion_dropoff_intent_week").getAttribute('end_date_value');
    }
    else if(document.getElementById('conversion_dropoff_intent_month').checked){
        start_date = document.getElementById("conversion_dropoff_intent_month").getAttribute('start_date_value');
        end_date = document.getElementById("conversion_dropoff_intent_month").getAttribute('end_date_value');
    }
    else if(document.getElementById('conversion_dropoff_intent_three_month').checked){
        start_date = document.getElementById("conversion_dropoff_intent_three_month").getAttribute('start_date_value');
        end_date = document.getElementById("conversion_dropoff_intent_three_month").getAttribute('end_date_value');
    }
    else if(document.getElementById('conversion_dropoff_intent_beg').checked){
        start_date = document.getElementById("conversion_dropoff_intent_beg").getAttribute('start_date_value');
        end_date = document.getElementById("conversion_dropoff_intent_beg").getAttribute('end_date_value');
    }
    else if(document.getElementById('conversion_dropoff_intent_custom_date_btn').checked){
        start_date = document.getElementById("conversion_dropoff_custom_start_date").value;
        end_date = document.getElementById("conversion_dropoff_custom_end_date").value;
    }

    var channel_element_list = document.querySelectorAll(".dropoff-analytics-channels");
    channel_element_list.forEach(function(element){

        if(element.checked) {

            channel_list.push(element.value);
        }
    });

    return {
        start_date,
        end_date,
        channel_list
    };

}

function check_flow_conversion_analytics_filter(){
        channel_list = [];
        var start_date = "";
        var end_date = "";

        if(document.getElementById('conversion_flow_week').checked){
            start_date = document.getElementById("conversion_flow_week").getAttribute('start_date_value');
            end_date = document.getElementById("conversion_flow_week").getAttribute('end_date_value');
        }
        else if(document.getElementById('conversion_flow_month').checked){
            start_date = document.getElementById("conversion_flow_month").getAttribute('start_date_value');
            end_date = document.getElementById("conversion_flow_month").getAttribute('end_date_value');
        }
        else if(document.getElementById('conversion_flow_three_month').checked){
            start_date = document.getElementById("conversion_flow_three_month").getAttribute('start_date_value');
            end_date = document.getElementById("conversion_flow_three_month").getAttribute('end_date_value');
        }
        else if(document.getElementById('conversion_flow_beg').checked){
            start_date = document.getElementById("conversion_flow_beg").getAttribute('start_date_value');
            end_date = document.getElementById("conversion_flow_beg").getAttribute('end_date_value');
        }
        else if(document.getElementById('conversion_flow_custom_date_btn').checked){
            start_date = document.getElementById("conversion_flow_custom_start_date").value;
            end_date = document.getElementById("conversion_flow_custom_end_date").value;
        }

        var channel_element_list = document.querySelectorAll(".flow-completion-rate-channels")
        channel_element_list.forEach(function(element){

            if(element.checked) {

                channel_list.push(element.value);
            }
        });

        return {
            start_date,
            end_date,
            channel_list
        };
}

function render_flow_conversion_analytics_data(flow_analytics_counter, table_body){
    let flow_analytics_counter_max = flow_analytics_counter+20;
    if(flow_analytics_counter_max >= flow_completion_data.length)
        flow_analytics_counter_max = flow_completion_data.length;
    if(flow_analytics_counter < flow_completion_data.length){

    for (let i = flow_analytics_counter; i < flow_analytics_counter_max; i++){
        var row = table_body.insertRow();
        addCell(row, i+1);
        var intent_name = flow_completion_data[i]['multilingual_name']

        if (flow_conversion_api_status_code == 300){
            intent_name = flow_completion_data[i]['name'];
        }
        html = '<a class="modal-trigger" href="#conversion-node-analytics-modal" onclick="render_flow_analytics_in_modal('+flow_completion_data[i]["id"]+')" >' + intent_name + '</a>'
        var td = row.insertCell();
        td.innerHTML = html;

        if (flow_conversion_language_script_type == "rtl") {
            td.style.direction = "rtl";
            td.style.textAlign ="right";
            var flow_completion_search_bar_id = $("#flow_completion_search_bar")
            if (flow_completion_search_bar_id.length) {
                mirror_search_bar(flow_completion_search_bar_id);
            }
        }

        addCell(row, flow_completion_data[i]['hit_count']);
        addCell(row, flow_completion_data[i]['complete_count']);
        addCell(row, flow_completion_data[i]['abort_count']);
        html = '<div>\
                    <div class="analytics-table-progressbar">\
                    <div class="analytics-table-progressbar-inside" style="width: ' + flow_completion_data[i]['flow_percent'] +'%"></div>\
                    </div>\
                    <div class="anamytics-table-progress-percent-text">' + flow_completion_data[i]['flow_percent'] + '%</div>\
                </div>'
        var td = row.insertCell();
        td.innerHTML = html;
       
    }
    if (flow_conversion_api_status_code == 300){
        document.getElementById("translation_api_toast_container").style.display = "flex";
        setTimeout(api_fail_message_none, 4000);
    }
    }
    search_from_table('flow_conversion_analytics_table', 'flow_analytics_search')

}

function addCell(tr, text, is_tooltip_required=false) {
    var td = tr.insertCell();
    td.textContent = text;
    if (is_tooltip_required) {
        td.setAttribute("data-tippy-content", text)
    }
    return td;
}

function render_flow_analytics_in_modal(intent_pk){
    svg.selectAll('*').remove();
    bot_pk = get_url_vars()["bot_id"];
    selected_language = get_url_vars()["selected_language"]

    flow_conversion_filter_result = check_flow_conversion_analytics_filter();
    var start_date = flow_conversion_filter_result.start_date;
    var end_date = flow_conversion_filter_result.end_date;
    channel_list = flow_conversion_filter_result.channel_list;
    var json_string = JSON.stringify({
        bot_pk: bot_pk,
        intent_pk: intent_pk,
        start_date: start_date,
        end_date: end_date,
        channel_list: channel_list,
        selected_language: selected_language
    })

    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var xhttp = new XMLHttpRequest();
    var params = 'json_string=' + json_string
    xhttp.open("POST", "/chat/get-conversion-node-analytics/", true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200 || response["status"] == 300) {
                get_conversion_node_analytics_status_code = response["status"]
                conversion_node_analytics_pk = intent_pk;
                var json = JSON.parse(response["flow_tree_data"]);
                var max_level = response["max_level"];
                render_flow_analytics_data(json, max_level);
            } else {
                M.toast({
                    "html": "Please try again later."
                }, 2000);
            }
        }
    }
    xhttp.send(params);
}

function download_conversion_node_analytics(){
    flow_conversion_filter_result = check_flow_conversion_analytics_filter();
    var start_date = flow_conversion_filter_result.start_date;
    var end_date = flow_conversion_filter_result.end_date;
    channel_list = flow_conversion_filter_result.channel_list;
    selected_language = get_url_vars()["selected_language"]
    if(typeof selected_language == 'undefined'){
        selected_language = get_url_vars()["dropdown_language"]
    }

    if(Date.parse(start_date) > Date.parse(end_date)){
        M.toast({
            "html": "Start Date should be smaller than End Date"
        }, 2000);
        return;
    }
    window.location = "/chat/download-flow-analytics/?intent_pk="+conversion_node_analytics_pk+"&startdate="+start_date+"&enddate="+end_date+"&channel="+channel_list + "&selected_language=" + selected_language
}

function download_user_specific_dropoff_intent_specific(){
    flow_conversion_filter_result = check_flow_conversion_analytics_filter();
    var start_date = flow_conversion_filter_result.start_date;
    var end_date = flow_conversion_filter_result.end_date;
    channel_list = flow_conversion_filter_result.channel_list;
    selected_language = get_url_vars()["selected_language"]

    if(Date.parse(start_date) > Date.parse(end_date)){
        M.toast({
            "html": "Start Date should be smaller than End Date"
        }, 2000);
        return;
    }
    window.location = "/chat/download-user-specific-dropoff-analytics/?intent_pk="+conversion_node_analytics_pk+"&startdate="+start_date+"&enddate="+end_date+"&channel="+channel_list+"&selected_language="+selected_language
}

function load_intent_conversion_analytics(){
        bot_pk = get_url_vars()["bot_id"];
        selected_language = get_url_vars()['selected_language']
        if (typeof selected_language == 'undefined'){
            selected_language = "en"
        } 
        flow_conversion_filter_result = check_intent_conversion_analytics_filter();
        var start_date = flow_conversion_filter_result.start_date;
        var end_date = flow_conversion_filter_result.end_date;
        channel_list = flow_conversion_filter_result.channel_list;

        var today = new Date();
        var today = today.getFullYear() + "-" + String(today.getMonth() + 1).padStart(2, '0') + "-" + String(today.getDate()).padStart(2, '0');

            if (Date.parse(start_date) > Date.parse(end_date)){

                M.toast({
                    "html": "Start Date should be smaller than End Date"
                }, 2000);

                reset_start_end_date("conversion_intent_custom_start_date","conversion_intent_custom_end_date");

                return;
            }

            if(Date.parse(today) < Date.parse(end_date)){
                M.toast({
                    "html": "End date cannot be greater than today's date."
                }, 2000);

                reset_start_end_date("conversion_intent_custom_start_date","conversion_intent_custom_end_date");

                return;
            }

            if (Date.parse(start_date) > Date.parse(today)){
                M.toast({
                    "html": "Start date cannot be greater than today's date."
                }, 2000);

                reset_start_end_date("conversion_intent_custom_start_date","conversion_intent_custom_end_date");

                return;
            }

        if(intent_analytics_page<=0)
            intent_analytics_page = 1



        if(document.getElementById("intent_conversion_analytics_table_body") && intent_analytics_scrolled == false){
            var table_body = document.getElementById("intent_conversion_analytics_table_body");
            table_body.remove();
        }
        $("#conversion_intent_custom_start_date").attr("current_applied_date", start_date)
        $("#conversion_intent_custom_end_date").attr("current_applied_date", end_date)
        document.getElementById("intent_conversion_analytics_no_data_found").style.display = "none";
        document.getElementById("intent_conversion_analytics_table_scroll").style.display = "block";
        document.getElementById('conversion_intent_analytics_loader').style.display = "block";

        if(document.getElementById('analytics-table-data-total-area')){
            var intent_table_total_row = document.getElementById('analytics-table-data-total-area');
            intent_table_total_row.parentNode.removeChild(intent_table_total_row);
        }

        var xhttp = new XMLHttpRequest();
        var params = '';
        xhttp.open("GET", "/chat/get-conversion-intent-analytics/?bot_pk=" + bot_pk +"&start_date=" + start_date + "&end_date=" + end_date + "&channel_list=" + channel_list + "&page=" + intent_analytics_page + "&selected_language=" + selected_language, true);
        xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhttp.onreadystatechange = async function () {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = custom_decrypt(response)
                response = JSON.parse(response);
                intent_analytics_language_script_type = "ltr";
                if (response["status"] == 200 || response["status"] == 300) {
                    intent_analytics_language_script_type = response["language_script_type"]
                    if (intent_analytics_scrolled == false) {
                        var table = document.getElementById("intent_conversion_analytics_table");
                        table_body = table.appendChild(document.createElement('tbody'))
                        table_body.setAttribute("id", "intent_conversion_analytics_table_body");
                        intent_analytics_counter = 1;
                    } else {
                        table_body = document.getElementById("intent_conversion_analytics_table_body");
                    }
                    var intent_completion_data = response["intent_completion_data"];
                    var total_intent_count = response["total_intent_count"];
                    is_last_page = response["is_last_page"];
                    intent_analytics_api_status_code = response['status']


                    if (intent_completion_data.length == 0) {
                        document.getElementById("intent_conversion_analytics_no_data_found").style.display = "flex";
                        document.getElementById("intent_conversion_analytics_table_scroll").style.display = "none";
                    } else {
                        render_intent_conversion_analytics_data(intent_completion_data, total_intent_count, table_body);
                        if (intent_analytics_api_status_code == 300) {
                        document.getElementById("translation_api_toast_container").style.display = "flex";
                        setTimeout(function(){
                        document.getElementById("translation_api_toast_container").style.display = "none";
                        },4000)

                    }
                    }

                    document.getElementById('conversion_intent_analytics_loader').style.display = "none";

                    if (Date.parse(start_date) != Date.parse(end_date)) {
                        show_start_date = convert_to_date_format(start_date);
                        show_end_date = convert_to_date_format(end_date);
                        document.getElementById("intent_conversion_analytics_date").innerHTML = "Range : " + show_start_date + " to " + show_end_date;
                    } else {
                        show_date = convert_to_date_format(start_date);
                        document.getElementById("intent_conversion_analytics_date").innerHTML = "" + show_date;
                    }

                    show_intent_data = true;
                    intent_analytics_scrolled = false;
                } else {
                    document.getElementById('conversion_intent_analytics_loader').style.display = "none";
                }
                search_from_table('intent_conversion_analytics_table', 'intent_analytics_search')
            }
        }
        xhttp.send(params);
}

function check_intent_conversion_analytics_filter(){
        channel_list = [];
        var start_date = "";
        var end_date = "";

        if(document.getElementById('conversion_intent_week').checked){
            start_date = document.getElementById("conversion_intent_week").getAttribute('start_date_value');
            end_date = document.getElementById("conversion_intent_week").getAttribute('end_date_value');
        }
        else if(document.getElementById('conversion_intent_month').checked){
            start_date = document.getElementById("conversion_intent_month").getAttribute('start_date_value');
            end_date = document.getElementById("conversion_intent_month").getAttribute('end_date_value');
        }
        else if(document.getElementById('conversion_intent_three_month').checked){
            start_date = document.getElementById("conversion_intent_three_month").getAttribute('start_date_value');
            end_date = document.getElementById("conversion_intent_three_month").getAttribute('end_date_value');
        }
        else if(document.getElementById('conversion_intent_beg').checked){
            start_date = document.getElementById("conversion_intent_beg").getAttribute('start_date_value');
            end_date = document.getElementById("conversion_intent_beg").getAttribute('end_date_value');
        }
        else if(document.getElementById('conversion_intent_custom_date_btn').checked){
            start_date = document.getElementById("conversion_intent_custom_start_date").value;
            end_date = document.getElementById("conversion_intent_custom_end_date").value;
        }

        var channel_element_list = document.querySelectorAll(".intent-analytics-channels")
        channel_element_list.forEach(function(element){

            if(element.checked) {

                channel_list.push(element.value);
            }
        });

        return {
            start_date,
            end_date,
            channel_list
        };
}

function render_intent_conversion_analytics_data(intent_completion_data, total_intent_count, table_body){

    for (let i = 0; i < intent_completion_data.length; i++){
        var row = table_body.insertRow();
        addCell(row, intent_analytics_counter);
        if (intent_analytics_api_status_code == 200){
            var tcell = addCell(row, intent_completion_data[i]['multilingual_name']);
            if (intent_analytics_language_script_type == "rtl") {
                tcell.style.direction = "rtl";
                tcell.style.textAlign = "right";
                var intent_analytics_search_bar_id = $("#intent_analytics_search_bar")
                if (intent_analytics_search_bar_id.length) {
                    mirror_search_bar(intent_analytics_search_bar_id);
                }
            }
        }
        else{
            addCell(row, intent_completion_data[i]['intent_name']);
        }

        addCell(row, intent_completion_data[i]['count']);
        var intent_progress = Math.round((intent_completion_data[i]['count']/total_intent_count)*100);
        html = '<div>\
                    <div class="analytics-table-progressbar">\
                        <div class="analytics-table-progressbar-inside" style="width: ' + intent_progress +'%"></div>\
                    </div>\
                    <div class="anamytics-table-progress-percent-text">' + intent_progress + '%</div>\
                </div>'
        var td = row.insertCell();
        td.innerHTML = html;
        intent_analytics_counter += 1;
    }
    var tr = table_body.insertRow();
    tr.setAttribute("id", "analytics-table-data-total-area");
    tr.innerHTML = '<td></td>\
                    <td style="text-align: left;">Total </td>\
                    <td>' + total_intent_count + '</td>\
                    <td></td>'

}

function load_whatsapp_block_analytics(){

    if (channel_list.length != 0 && !channel_list.includes("WhatsApp")) {
        $("#whatsapp_block_analytics_no_data_found").css("display", "flex");
        $("#whatsapp_block_analytics_table_scroll").hide();
        return;
    }

    let bot_pk = get_url_vars()["bot_id"];
    let whatsapp_block_filter_result = check_whatsapp_block_analytics_filter();
    let { start_date, end_date, spam_type }  = whatsapp_block_filter_result;

    let today = new Date();
    today = today.getFullYear() + "-" + String(today.getMonth() + 1).padStart(2, '0') + "-" + String(today.getDate()).padStart(2, '0');

        if (Date.parse(start_date) > Date.parse(end_date)){

            M.toast({
                "html": "Start Date should be smaller than End Date"
            }, 2000);

            reset_start_end_date("conversion_whatsapp_custom_start_date","conversion_whatsapp_custom_end_date");

            return;
        }

        if(Date.parse(today) < Date.parse(end_date)){
            M.toast({
                "html": "End date cannot be greater than today's date."
            }, 2000);

            reset_start_end_date("conversion_whatsapp_custom_start_date","conversion_whatsapp_custom_end_date");

            return;
        }

        if (Date.parse(start_date) > Date.parse(today)){
            M.toast({
                "html": "Start date cannot be greater than today's date."
            }, 2000);

            reset_start_end_date("conversion_whatsapp_custom_start_date","conversion_whatsapp_custom_end_date");

            return;
        }

    $("#conversion_whatsapp_custom_start_date").attr("current_applied_date", start_date)
    $("#conversion_whatsapp_custom_end_date").attr("current_applied_date", end_date)
    if (whatsapp_block_analytics_page<=0) whatsapp_block_analytics_page = 1

    if(document.getElementById("whatsapp_block_analytics_table_body") && whatsapp_block_analytics_scrolled == false){
        let table_body = document.getElementById("whatsapp_block_analytics_table_body");
        table_body.remove();
    }

    document.getElementById("whatsapp_block_analytics_no_data_found").style.display = "none";
    document.getElementById("whatsapp_block_analytics_table_scroll").style.display = "block";
    document.getElementById('whatsapp_block_analytics_loader').style.display = "block";

    let xhttp = new XMLHttpRequest();
    let params = '';
    xhttp.open("GET", "/chat/get-whatsapp-block-analytics/?bot_pk=" + bot_pk + "&start_date=" + start_date + "&end_date=" + end_date + "&block_type=" + spam_type + "&page=" + whatsapp_block_analytics_page, true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = async function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                if (whatsapp_block_analytics_scrolled == false) {
                    let table = document.getElementById("whatsapp_block_analytics_table");
                    table_body = table.appendChild(document.createElement('tbody'))
                    table_body.setAttribute("id", "whatsapp_block_analytics_table_body");
                    whatsapp_analytics_counter = 1;
                } else {
                    table_body = document.getElementById("whatsapp_block_analytics_table_body");
                }
                let block_session_data = response["block_session_data"];
                is_last_page_whatsapp = response["is_last_page"];
                whatsapp_analytics_api_status_code = response['status']


                if (block_session_data.length == 0) {
                    document.getElementById("whatsapp_block_analytics_no_data_found").style.display = "flex";
                    document.getElementById("whatsapp_block_analytics_table_scroll").style.display = "none";
                } else {
                    render_whatsapp_block_analytics_data(block_session_data, table_body);
                }
                }

                document.getElementById('whatsapp_block_analytics_loader').style.display = "none";

                if (Date.parse(start_date) != Date.parse(end_date)) {
                    let show_start_date = convert_to_date_format(start_date);
                    let show_end_date = convert_to_date_format(end_date);
                    document.getElementById("whatsapp_block_analytics_date").innerHTML = "Range : " + show_start_date + " to " + show_end_date;
                } else {
                    show_date = convert_to_date_format(start_date);
                    document.getElementById("whatsapp_block_analytics_date").innerHTML = "" + show_date;
                }

                show_block_spam_data = true;
                whatsapp_block_analytics_scrolled = false;
            } else {
                document.getElementById('whatsapp_block_analytics_loader').style.display = "none";
            }
        }
    
    xhttp.send(params);
}

function check_whatsapp_block_analytics_filter(){
    let start_date = default_start_date;
    let end_date = default_end_date;
    let spam_type = "All";

    if(document.getElementById('whatsapp_block_week').checked){
        start_date = document.getElementById("whatsapp_block_week").getAttribute('start_date_value');
        end_date = document.getElementById("whatsapp_block_week").getAttribute('end_date_value');
    }
    else if(document.getElementById('whatsapp_block_month').checked){
        start_date = document.getElementById("whatsapp_block_month").getAttribute('start_date_value');
        end_date = document.getElementById("whatsapp_block_month").getAttribute('end_date_value');
    }
    else if(document.getElementById('whatsapp_block_three_month').checked){
        start_date = document.getElementById("whatsapp_block_three_month").getAttribute('start_date_value');
        end_date = document.getElementById("whatsapp_block_three_month").getAttribute('end_date_value');
    }
    else if(document.getElementById('whatsapp_block_beg').checked){
        start_date = document.getElementById("whatsapp_block_beg").getAttribute('start_date_value');
        end_date = document.getElementById("whatsapp_block_beg").getAttribute('end_date_value');
    }
    else if(document.getElementById('whatsapp_block_custom_date_btn').checked){
        start_date = document.getElementById("conversion_whatsapp_custom_start_date").value;
        end_date = document.getElementById("conversion_whatsapp_custom_end_date").value;
    }

    if ($("#whatsapp_block_query")[0].checked) {
        spam_type = "spam_message"
    } else if ($("#whatsapp_block_keyword")[0].checked) {
        spam_type = "keyword"
    }

    return {
        start_date,
        end_date,
        spam_type
    };
}

function format_whatsapp_datetime(datetime) {
    let datetime_obj = new Date(datetime)
    const options = {
        dateStyle: "full",
        timeStyle: "short"
    }  
    datetime_obj = datetime_obj.toLocaleString("en-IN", options)
    datetime_obj = datetime_obj.split(", ").slice(1).join().replace(" at ", ",")

    return datetime_obj
}

function render_whatsapp_block_analytics_data(block_session_data, table_body) {
    for (let i = 0; i < block_session_data.length; i++){
        let row = table_body.insertRow();
        addCell(row, whatsapp_analytics_counter);
        addCell(row, block_session_data[i]['whatsapp_number'])
        if (block_session_data[i]['block_type'] === "spam_message") {
            addCell(row, "Spam Message");
            addCell(row, "-");
        } else {
            addCell(row, "Keyword");
            addCell(row, block_session_data[i]['blocked_spam_keywords']);
        }
        addCell(row, format_whatsapp_datetime(block_session_data[i]['block_time']));
        addCell(row, format_whatsapp_datetime(block_session_data[i]['unblock_time']));
        whatsapp_analytics_counter += 1;
    }
}

function render_whatsapp_catalogue_analytics_data(catalogue_cart_data, table_body) {
    for (let i = 0; i < catalogue_cart_data.length; i++){
        let row = table_body.insertRow();
        addCell(row, catalogue_analytics_counter);
        addCell(row, format_whatsapp_datetime(catalogue_cart_data[i]['cart_update_time']));
        addCell(row, catalogue_cart_data[i]['user__user_id'])
        addCell(row, catalogue_cart_data[i]['current_cart_packet'], true)
        let is_purchased = catalogue_cart_data[i]['is_purchased'] ? "Yes" : "No";
        addCell(row, is_purchased)
        addCell(row, catalogue_cart_data[i]['cart_total'])
        catalogue_analytics_counter += 1;
    }
}

function get_selected_bot_id(){
    bot_pk = $("#selected-bot-for-analytics").val();
    return bot_pk;
}

function set_filter_flag_and_load_livechat_analytics(){
    livechat_filter = true;
    load_livechat_conersion_analytics();
}

function load_traffic_conversion_analytics(){

        bot_pk = get_url_vars()["bot_id"];

        traffic_conversion_filter_result = check_traffic_conversion_analytics_filter();
        var start_date = traffic_conversion_filter_result.start_date;
        var end_date = traffic_conversion_filter_result.end_date;
        source_list = traffic_conversion_filter_result.source_list;

        if(traffic_analytics_page<=0)
            traffic_analytics_page = 1

        var today = new Date();
        var today = today.getFullYear() + "-" + String(today.getMonth() + 1).padStart(2, '0') + "-" + String(today.getDate()).padStart(2, '0');

            if (Date.parse(start_date) > Date.parse(end_date)){

                M.toast({
                    "html": "Start Date should be smaller than End Date"
                }, 2000);

                reset_start_end_date("conversion_traffic_custom_start_date","conversion_traffic_custom_end_date");

                return;
            }

            if(Date.parse(today) < Date.parse(end_date)){
                M.toast({
                    "html": "End date cannot be greater than today's date."
                }, 2000);

                reset_start_end_date("conversion_traffic_custom_start_date","conversion_traffic_custom_end_date");

                return;
            }

            if (Date.parse(start_date) > Date.parse(today)){
                M.toast({
                    "html": "Start date cannot be greater than today's date."
                }, 2000);

                reset_start_end_date("conversion_traffic_custom_start_date","conversion_traffic_custom_end_date");

                return;
            }

        if(document.getElementById("traffic_conversion_analytics_table_body") && traffic_analytics_scrolled == false){
            var table_body = document.getElementById("traffic_conversion_analytics_table_body");
            table_body.remove();
        }
        $("#conversion_traffic_custom_start_date").attr("current_applied_date", start_date)
        $("#conversion_traffic_custom_end_date").attr("current_applied_date", end_date)
        document.getElementById("traffic_conversion_analytics_no_data_found").style.display = "none";
        document.getElementById("traffic_conversion_analytics_table_scroll").style.display = "block";
        document.getElementById('conversion_traffic_analytics_loader').style.display = "block";

        var xhttp = new XMLHttpRequest();
        var params = '';
        xhttp.open("GET", "/chat/get-conversion-bot-hits-analytics/?bot_pk=" + bot_pk +"&start_date=" + start_date + "&end_date=" + end_date + "&source_list=" + source_list + "&page=" + traffic_analytics_page, true);
        xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = custom_decrypt(response)
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    if(traffic_table_sort != null)
                        traffic_table_sort.destroy();

                    if(traffic_analytics_scrolled == false){
                        var table = document.getElementById("traffic_conversion_analytics_table");
                        table_body = table.appendChild(document.createElement('tbody'))
                        table_body.setAttribute("id", "traffic_conversion_analytics_table_body");
                        traffic_analytics_counter = 1;
                    }
                    else{
                        table_body = document.getElementById("traffic_conversion_analytics_table_body");
                    }
                    var bot_hit_data_count = response["bot_hit_data_count"];
                    is_last_page_traffic = response["is_last_page"];

                    render_traffic_conversion_analytics_data(bot_hit_data_count, table_body);
                    traffic_analytics_table_sort();

                    document.getElementById('conversion_traffic_analytics_loader').style.display = "none";

                    if(Date.parse(start_date) != Date.parse(end_date)){
                        show_start_date = convert_to_date_format(start_date);
                        show_end_date = convert_to_date_format(end_date);
                        document.getElementById("traffic_conversion_analytics_date").innerHTML = "Range : " + show_start_date + " to " + show_end_date;
                    }
                    else{
                        show_date = convert_to_date_format(start_date);
                        document.getElementById("traffic_conversion_analytics_date").innerHTML = "" + show_date;
                    }

                    show_traffic_data = true;
                    traffic_analytics_scrolled = false;
                }
                else{
                    document.getElementById('conversion_traffic_analytics_loader').style.display = "none";
                }
                if (bot_hit_data_count.length>0) {
                search_from_table('traffic_conversion_analytics_table', 'traffic_analytics_search')
                }
            }
        }
        xhttp.send(params);
}

function check_traffic_conversion_analytics_filter(){

        source_list = [];
        var start_date = "";
        var end_date = "";

        if(document.getElementById('conversion_traffic_week').checked){
            start_date = document.getElementById("conversion_traffic_week").getAttribute('start_date_value');
            end_date = document.getElementById("conversion_traffic_week").getAttribute('end_date_value');
        }
        else if(document.getElementById('conversion_traffic_month').checked){
            start_date = document.getElementById("conversion_traffic_month").getAttribute('start_date_value');
            end_date = document.getElementById("conversion_traffic_month").getAttribute('end_date_value');
        }
        else if(document.getElementById('conversion_traffic_three_month').checked){
            start_date = document.getElementById("conversion_traffic_three_month").getAttribute('start_date_value');
            end_date = document.getElementById("conversion_traffic_three_month").getAttribute('end_date_value');
        }
        else if(document.getElementById('conversion_traffic_beg').checked){
            start_date = document.getElementById("conversion_traffic_beg").getAttribute('start_date_value');
            end_date = document.getElementById("conversion_traffic_beg").getAttribute('end_date_value');
        }
        else if(document.getElementById('conversion_traffic_custom_date_btn').checked){
            start_date = document.getElementById("conversion_traffic_custom_start_date").value;
            end_date = document.getElementById("conversion_traffic_custom_end_date").value;
        }

        for(let j=1; j <= source_length ; j++ ){
            if(document.getElementById("traffic_source_checkbox"+j).checked)
                source_list.push(document.getElementById("traffic_source_checkbox"+j).value);
        }

        return {
            start_date,
            end_date,
            source_list
        };
}

function traffic_analytics_table_sort(){
    traffic_table_sort = $('#traffic_conversion_analytics_table').DataTable({
        paging: false,
        searching: false,

        info: false,

        'order': [],
        'columnDefs': [{
            "targets": 0,
            "orderable": false
        }]

    });

    traffic_table_sort.on('order.dt search.dt', function() {
        traffic_table_sort.column(0, {
            search: 'applied',
            order: 'applied'
        }).nodes().each(function(cell, i) {
            cell.innerHTML = i + 1;
        });
    }).draw();
    if($("#traffic_conversion_analytics_table_body .dataTables_empty").length !== 0) {
        $("#traffic_conversion_analytics_table_body tr").remove();
    }

}


function render_traffic_conversion_analytics_data(bot_hit_data_count,table_body){

    if (bot_hit_data_count.length>0) {
        for (let i = 0; i < bot_hit_data_count.length; i++){
            var row = table_body.insertRow();
            addCell(row, traffic_analytics_counter);
            html = '<a target="_blank" class="tooltipped" data-position="top" data-tooltip="' + bot_hit_data_count[i]['web_page'] + '" href="' + bot_hit_data_count[i]['web_page'] + '">' + bot_hit_data_count[i]['web_page'].substring(0,20) + '...</a>'
            var td = row.insertCell();
            td.innerHTML = html;
            setTimeout(function(){ $('.tooltipped').tooltip(); }, 300);
            addCell(row, bot_hit_data_count[i]['web_page_source']);
            addCell(row, bot_hit_data_count[i]['page_views']);
            addCell(row, bot_hit_data_count[i]['bot_views']);

            addCell(row, get_time_format(bot_hit_data_count[i]['average_time_spent']));
            traffic_analytics_counter += 1;
        }
    }
    else {
        document.getElementById("traffic_conversion_analytics_no_data_found").style.display = "flex";
        document.getElementById("traffic_conversion_analytics_table_scroll").style.display = "none";
    }
}


//load welcome analytics

function load_welcome_banner_analytics(){

        if (channel_list.length != 0 && !(channel_list.includes("Web")  || channel_list.includes("Android")  || channel_list.includes("iOS")  ) ){
            $("#welcome_conversion_analytics_no_data_found").css("display", "flex");
            $("#welcome_conversion_analytics_table_scroll").hide();
            return;
        }
        bot_pk = get_url_vars()["bot_id"];
        selected_language = get_url_vars()["selected_language"]
        if (typeof selected_language == 'undefined'){
            selected_language = "en"
        }
        welcome_conversion_filter_result = check_welcome_banner_analytics_filter();
        var start_date = welcome_conversion_filter_result.start_date;
        var end_date = welcome_conversion_filter_result.end_date;

        if(welcome_analytics_page<=0)
            welcome_analytics_page = 1

        var today = new Date();
            var today = today.getFullYear() + "-" + String(today.getMonth() + 1).padStart(2, '0') + "-" + String(today.getDate()).padStart(2, '0');

            if (Date.parse(start_date) > Date.parse(end_date)){

                M.toast({
                    "html": "Start Date should be smaller than End Date"
                }, 2000);

                reset_start_end_date("conversion_welcome_custom_start_date","conversion_welcome_custom_end_date");

                return;
            }

            if(Date.parse(today) < Date.parse(end_date)){
                M.toast({
                    "html": "End date cannot be greater than today's date."
                }, 2000);

                reset_start_end_date("conversion_welcome_custom_start_date","conversion_welcome_custom_end_date");

                return;
            }

            if (Date.parse(start_date) > Date.parse(today)){
                M.toast({
                    "html": "Start date cannot be greater than today's date."
                }, 2000);

                reset_start_end_date("conversion_welcome_custom_start_date","conversion_welcome_custom_end_date");

                return;
            } else {
                if(document.getElementById("total_clicks"))
                {
                    document.getElementById("total_clicks").innerHTML = "..."
                }
        }

        if(document.getElementById("welcome_conversion_analytics_table_body") && welcome_analytics_scrolled == false){
            var table_body = document.getElementById("welcome_conversion_analytics_table_body");
            table_body.remove();
        }
        $("#conversion_welcome_custom_start_date").attr("current_applied_date", start_date)
        $("#conversion_welcome_custom_end_date").attr("current_applied_date", end_date)
        document.getElementById("welcome_conversion_analytics_no_data_found").style.display = "none";
        document.getElementById("welcome_conversion_analytics_table_scroll").style.display = "block";
        document.getElementById('conversion_welcome_analytics_loader').style.display = "block";

        var xhttp = new XMLHttpRequest();
        var params = '';
        xhttp.open("GET", "/chat/get-conversion-welcome-analytics/?bot_pk=" + bot_pk +"&start_date=" + start_date + "&end_date=" + end_date + "&page=" + welcome_analytics_page +"&selected_language=" + selected_language, true);
        xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = custom_decrypt(response)
                response = JSON.parse(response);
                welcome_analytics_api_status_code = response['status']
                welcome_analytics_language_script_type = "ltr";
                if (response["status"] == 200 || response["status"] == 300) {
                    welcome_analytics_language_script_type = response["language_script_type"]
                    if(welcome_table_sort != null)
                        welcome_table_sort.destroy();

                    var total_clicks = response["total_clicks"]

                    if(welcome_analytics_scrolled == false){
                        var table = document.getElementById("welcome_banner_analytics_table");
                        table_body = table.appendChild(document.createElement('tbody'))
                        table_body.setAttribute("id", "welcome_conversion_analytics_table_body");
                        welcome_analytics_counter = 1;
                    }
                    else{
                        table_body = document.getElementById("welcome_conversion_analytics_table_body");
                    }
                    var welcome_banner_clicked_data_count = response["welcome_banner_clicked_data_count"];
                    is_last_page_welcome = response["is_last_page"];

                    render_welcome_banner_analytics_data(welcome_banner_clicked_data_count, table_body, total_clicks);
                    welcome_analytics_table_sort();
                    if (welcome_analytics_api_status_code == 300){
                        document.getElementById("translation_api_toast_container").style.display = "flex";
                        setTimeout(api_fail_message_none, 4000);
                    }

                    document.getElementById('conversion_welcome_analytics_loader').style.display = "none";

                    if(Date.parse(start_date) != Date.parse(end_date)){
                        show_start_date = convert_to_date_format(start_date);
                        show_end_date = convert_to_date_format(end_date);
                        document.getElementById("welcome_conversion_analytics_date").innerHTML = "Range : " + show_start_date + " to " + show_end_date;
                    }
                    else{
                        show_date = convert_to_date_format(start_date);
                        document.getElementById("welcome_conversion_analytics_date").innerHTML = "" + show_date;
                    }

                    show_welcome_data = true;
                    welcome_analytics_scrolled = false;
                }
                else{
                    document.getElementById('conversion_welcome_analytics_loader').style.display = "none";
                }
                if (welcome_banner_clicked_data_count.length>0) {
                search_from_table('welcome_banner_analytics_table', 'welcome_analytics_search')
                }
            }
        }
        xhttp.send(params);
}

function welcome_analytics_table_sort(){
    try{
    welcome_table_sort  = $('#welcome_banner_analytics_table').DataTable({
                paging: false,
                searching: false,

                info: false,

                'order': [],
                'columnDefs': [{
                    "targets": 0,
                    "orderable": false
                }]

            });

            welcome_table_sort.on('order.dt search.dt', function() {
                welcome_table_sort.column(0, {
                    search: 'applied',
                    order: 'applied'
                }).nodes().each(function(cell, i) {
                    cell.innerHTML = i + 1;
                });
            }).draw();
        } catch(err)
        {}
        if($("#welcome_conversion_analytics_table_body .dataTables_empty").length !== 0) {
            $("#welcome_conversion_analytics_table_body tr").remove();
        }
}

function render_welcome_banner_analytics_data(welcome_banner_clicked_data_count,table_body,total_clicks){


    for (let i = 0; i < welcome_banner_clicked_data_count.length; i++){
        var image = welcome_banner_clicked_data_count[i]["preview_source"].split("/")
        image = image[image.length - 1]
        var image_name = image.split(".")[0]
        var image_ext = image.split(".")[1]
        if(image_name.length > 15)
            image_name = image_name.slice(0, 15) + "... ." + image_ext
        else
            image_name = image

        var link = welcome_banner_clicked_data_count[i]["web_page_visited"]
        if(link.length > 40)
        {
            link = link.slice(0, 40) + "... ."
        }
        var user_id_list_length = welcome_banner_clicked_data_count[i]["frequency"]
        var percent_total = user_id_list_length/total_clicks*100
        percent_total =  Math.round(percent_total);
        var row = table_body.insertRow();
        addCell(row, welcome_analytics_counter);
        html = '<a style="text-decoration: underline;cursor:pointer;" onclick="open_preview_modal(\''+welcome_banner_clicked_data_count[i]["preview_source"]+'\',\''+image_name+'\')" class="tooltipped" data-position="top" data-tooltip="' + welcome_banner_clicked_data_count[i]['preview_source'] + '">' + image_name + '</a>'
        var td = row.insertCell();
        td.innerHTML = html;

        html = '<a style="text-decoration: underline;" target="_blank" class="tooltipped" data-position="top" data-tooltip="' + welcome_banner_clicked_data_count[i]['web_page_visited'] + '" href="' + welcome_banner_clicked_data_count[i]['web_page_visited'] + '">' + link + '</a>'
        if (welcome_banner_clicked_data_count[i]["web_page_visited"] == "-") {
            html = "-";
        } else {
            html = '<a style="text-decoration: underline;" target="_blank" class="tooltipped" data-position="top" data-tooltip="' + welcome_banner_clicked_data_count[i]['web_page_visited'] + '" href="' + welcome_banner_clicked_data_count[i]['web_page_visited'] + '">' + link + '</a>'
        }
        td = row.insertCell();
        td.innerHTML = html;

        td = row.insertCell();
        var welcome_banner_analytics_search_bar_id = $("#welcome_banner_analytics_search_bar")
        if (welcome_banner_clicked_data_count[i]["intent__name"] == null || welcome_banner_clicked_data_count[i]["intent__name"] == undefined) {
            td.innerHTML = "-";
            if (welcome_analytics_language_script_type == "rtl") {
                td.style.direction = "rtl";
                td.style.textAlign = "right";
                if (welcome_banner_analytics_search_bar_id.length) {
                    mirror_search_bar(welcome_banner_analytics_search_bar_id);
                }
            }
        } else {
            if (welcome_analytics_api_status_code == 300) {
                td.innerHTML = welcome_banner_clicked_data_count[i]["intent__name"];
            }
            else {
                td.innerHTML = welcome_banner_clicked_data_count[i]["multilingual_name"];
                if (welcome_analytics_language_script_type == "rtl") {
                    td.style.direction = "rtl";
                    td.style.textAlign = "right";
                    if (welcome_banner_analytics_search_bar_id.length) {
                        mirror_search_bar(welcome_banner_analytics_search_bar_id);
                    }
                }
            }
        }

        addCell(row, user_id_list_length);
        td = row.insertCell()
        html = '<div>\
                    <div class="analytics-table-progressbar">\
                    <div class="analytics-table-progressbar-inside" style="width:'+percent_total+'%"></div>\
                    </div>\
                    <div class="anamytics-table-progress-percent-text">'+percent_total+'%</div>\
                </div>'
        td.innerHTML = html;

        setTimeout(function(){ $('.tooltipped').tooltip(); }, 300);
        welcome_analytics_counter += 1;
    }

    if(document.getElementById('welcome-banner-table-data-total-area'))
    {

        document.getElementById("total_clicks").innerText = total_clicks

    } else {

    var footer_html = '<tfoot>\
                        <tr id="welcome-banner-table-data-total-area"><td rowspan="1" colspan="1"></td><td rowspan="1" colspan="1">Total</td><td rowspan="1" colspan="1"></td><td rowspan="1" colspan="1"></td><td id="total_clicks" rowspan="1" colspan="1"> ' + total_clicks  + '</td><td rowspan="1" colspan="1"></td></tr>\
                    </tfoot>'
    document.getElementById("welcome_banner_analytics_table").insertAdjacentHTML('beforeend', footer_html)

    }

     if(welcome_banner_clicked_data_count.length > 0)
    {
        document.getElementById("welcome-banner-table-data-total-area").style.display = ""
    } else{
        document.getElementById("welcome-banner-table-data-total-area").style.display = "none"
        document.getElementById("welcome_conversion_analytics_table_scroll").style.display = "none"
        document.getElementById("welcome_conversion_analytics_no_data_found").style.display = "flex"
    }

}


function open_preview_modal(link, image_name)
{
    document.getElementById('preview_modal_heading').innerText = image_name
    document.getElementById("preview_modal_img").src = link
    $('#easychat-livechat-welcome-banner-preview-image-filter-modal').modal('open');

}

function check_welcome_banner_analytics_filter(){
        var start_date = "";
        var end_date = "";

        if(document.getElementById('conversion_welcome_week').checked){
            start_date = document.getElementById("conversion_welcome_week").getAttribute('start_date_value');
            end_date = document.getElementById("conversion_welcome_week").getAttribute('end_date_value');
        }
        else if(document.getElementById('conversion_welcome_month').checked){
            start_date = document.getElementById("conversion_welcome_month").getAttribute('start_date_value');
            end_date = document.getElementById("conversion_welcome_month").getAttribute('end_date_value');
        }
        else if(document.getElementById('conversion_welcome_three_month').checked){
            start_date = document.getElementById("conversion_welcome_three_month").getAttribute('start_date_value');
            end_date = document.getElementById("conversion_welcome_three_month").getAttribute('end_date_value');
        }
        else if(document.getElementById('conversion_welcome_beg').checked){
            start_date = document.getElementById("conversion_welcome_beg").getAttribute('start_date_value');
            end_date = document.getElementById("conversion_welcome_beg").getAttribute('end_date_value');
        }
        else if(document.getElementById('conversion_welcome_custom_date_btn').checked){
            start_date = document.getElementById("conversion_welcome_custom_start_date").value;
            end_date = document.getElementById("conversion_welcome_custom_end_date").value;
        }



        return {
            start_date,
            end_date
        };
}


//-------End load welcome analytics------


function get_time_format(secs){
var hours = String(Math.floor(secs / 60 / 60));
var minutes = String(Math.floor(secs / 60) - (hours * 60));
var seconds = String(secs % 60);
if(hours.length == 1)
    hours = '0' + hours;
if(minutes.length == 1)
    minutes = '0' + minutes;
if(seconds.length == 1)
    seconds = '0' + seconds;
return hours + ':' + minutes + ':' + seconds;
}

function load_livechat_conersion_analytics(){

        if (!is_livechat_enabled){
            return;
        }

        bot_pk = get_url_vars()["bot_id"];

        livechat_conversion_filter_result = check_livechat_conversion_analytics_filter();
        start_date = livechat_conversion_filter_result.start_date;
        end_date = livechat_conversion_filter_result.end_date;
        channel_list = livechat_conversion_filter_result.channel_list;

    if (Date.parse(start_date) > Date.parse(end_date)) {
        M.toast({
            "html": "Start Date should be smaller than End Date"
        }, 2000);
        reset_start_end_date("conversion_livechat_custom_start_date", "conversion_livechat_custom_end_date");
        return;
    }
        $("#conversion_livechat_custom_start_date").attr("current_applied_date", start_date)
        $("#conversion_livechat_custom_end_date").attr("current_applied_date", end_date)
        document.getElementById('live_chat_analytics_graph').style.display = "block";

        var xhttp = new XMLHttpRequest();
        var params = '';
        xhttp.open("GET", "/chat/get-conversion-livechat-analytics/?bot_pk=" + bot_pk +"&start_date=" + start_date + "&end_date=" + end_date + "&channel_list=" + channel_list + "&livechat_filter=" + livechat_filter, true);
        xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = custom_decrypt(response)
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    if(myChart != null)
                        myChart.destroy();

                    livechat_completion_data = response['livechat_completion_data'];
                    intent_raised_total = response["intent_raised_total"]
                    request_raised_total = response["request_raised_total"]
                    agent_connect_total = response["agent_connect_total"]
                    intent_raised_previous_day = response["intent_raised_previous_day"]
                    request_raised_previous_day = response["request_raised_previous_day"]
                    agent_connect_previous_day = response["agent_connect_previous_day"]

                    render_livechat_conversion_analytics_data(livechat_completion_data);
                    render_livechat_card_analytics_data(intent_raised_total, request_raised_total, agent_connect_total, intent_raised_previous_day, request_raised_previous_day, agent_connect_previous_day);

                    if(Date.parse(start_date) != Date.parse(end_date)){
                        show_start_date = convert_to_date_format(start_date);
                        show_end_date = convert_to_date_format(end_date);
                        document.getElementById("livechat_conversion_analytics_date").innerHTML = "Range : " + show_start_date + " to " + show_end_date;
                    }
                    else{
                        show_date = convert_to_date_format(start_date);
                        document.getElementById("livechat_conversion_analytics_date").innerHTML = "" + show_date;
                    }
                }
                else{
                    document.getElementById('live_chat_analytics_graph').style.display = "none";
                }
            }
        }
        xhttp.send(params);
}

function check_livechat_conversion_analytics_filter(){
        channel_list = [];
        start_date = "";
        end_date = "";

        if(document.getElementById('conversion_livechat_week').checked){
            start_date = document.getElementById("conversion_livechat_week").getAttribute('start_date_value');
            end_date = document.getElementById("conversion_livechat_week").getAttribute('end_date_value');
        }
        else if(document.getElementById('conversion_livechat_month').checked){
            start_date = document.getElementById("conversion_livechat_month").getAttribute('start_date_value');
            end_date = document.getElementById("conversion_livechat_month").getAttribute('end_date_value');
        }
        else if(document.getElementById('conversion_livechat_three_month').checked){
            start_date = document.getElementById("conversion_livechat_three_month").getAttribute('start_date_value');
            end_date = document.getElementById("conversion_livechat_three_month").getAttribute('end_date_value');
        }
        else if(document.getElementById('conversion_livechat_beg').checked){
            start_date = document.getElementById("conversion_livechat_beg").getAttribute('start_date_value');
            end_date = document.getElementById("conversion_livechat_beg").getAttribute('end_date_value');
        }
        else if(document.getElementById('conversion_livechat_custom_date_btn').checked){
            start_date = document.getElementById("conversion_livechat_custom_start_date").value;
            end_date = document.getElementById("conversion_livechat_custom_end_date").value;
        }

        var channel_element_list = document.querySelectorAll(".livechat-analytics-channels")
        channel_element_list.forEach(function(element){

            if(element.checked) {

                channel_list.push(element.value);
            }
        });

        return {
            start_date,
            end_date,
            channel_list
        };
}

function convert_to_date_graph(date_string, raw_date){
    var parts = date_string.split('-');
    var std_date = new Date(parts[0], parts[1] - 1, parts[2]);
    if (raw_date) {
        return std_date;
    }
    var date_format = (std_date.toDateString()).split(' ');
    var res_date = date_format[2] + ' ' + date_format[1];
    return res_date;
}

function render_livechat_conversion_analytics_data(livechat_completion_data){
    var date_labels = [];
    var chat_labels = [];
    var request_labels = [];
    var agent_connected_labels = [];
    var point_radius = 0;

    for(let i = 0; i < livechat_completion_data.length; i++){
        const dateSplit = livechat_completion_data[i]['date'].split("-");
        let objDate;
        if (livechat_completion_data.length <= 3) {
            objDate = convert_to_date_graph(livechat_completion_data[i]['date'], false) + " '" + dateSplit[0].slice(2);
        } else {
            objDate = convert_to_date_graph(livechat_completion_data[i]['date'], true).getTime();
        }
        date_labels.push(objDate);
        chat_labels.push(livechat_completion_data[i]['intent_raised_count']);
        request_labels.push(livechat_completion_data[i]['request_raised_count']);
        agent_connected_labels.push(livechat_completion_data[i]['agent_connect_count']);
    }

    myChart && myChart.destroy()

    var options = {
        series: [{
                name: "Chat with an expert",
                data: chat_labels,
            },
            {
                name: "Request Raised",
                data: request_labels,
            },
            {
                name: "Agent Connected",
                data: agent_connected_labels,
            }
    
        ],
        colors: ['#3751FF', '#10B981', '#E53E3E'],
        chart: {
            height: 350,
            type: 'line',
            zoom: {
                enabled: false
            },
            toolbar: {
                show: false,
            }
        },
        dataLabels: {
            enabled: false
        },
        stroke: {
            width: 2,
            curve: "smooth",
        },
        grid: {
            show: true,
            borderColor: '#f1f1f1',
            strokeDashArray: 0,
            position: 'back',
            xaxis: {
                lines: {
                    show: true
                },
            },
            yaxis: {
                lines: {
                    show: true
                }
            },
            row: {
                colors: '#C4C4C4',
                opacity: 0
            },
            column: {
                colors: '#C4C4C4',
                opacity: 0
            },
            padding: {
                top: 0,
                right: 0,
                bottom: 0,
                left: 10
            },
        },
        xaxis: {
            categories: date_labels,
            type: date_labels.length > 3 ? 'datetime' : "category",
            labels: {
                datetimeUTC: false,
                datetimeFormatter: {
                    day: "dd MMM 'yy",
                },
            },

            //   categories: [
            //      sevenWeeksBack,date
            //   ],

        },
        yaxis: [
            {
                labels: {
                formatter: function(val) {
                    return val.toFixed(0);
                }
                }
            }
        ]
    };
    
    myChart = new ApexCharts(document.querySelector("#live_chat_analytics_graph"), options);
    myChart.render();
   
}

function render_livechat_card_analytics_data(intent_raised_total, request_raised_total, agent_connect_total, intent_raised_previous_day, request_raised_previous_day, agent_connect_previous_day){
    document.getElementById("intent-raised-div").style.display = "none";
    document.getElementById("request-raised-div").style.display = "none";
    document.getElementById("agent-count-div").style.display = "none";
    document.getElementById("livechat-percent-div").style.display = "none";
    document.getElementById("chat-with-expert-livechat-analytics").innerHTML = intent_raised_total;
    document.getElementById("request-raised-livechat-analytics").innerHTML = request_raised_total;
    document.getElementById("agent-connect-livechat-analytics").innerHTML = agent_connect_total;
    if(intent_raised_total == 0)
        livechat_conversion_percent = 0;
    else
        livechat_conversion_percent = Math.round((agent_connect_total / intent_raised_total) * 100);
    document.getElementById("percent-livechat-analytics").innerHTML = String(livechat_conversion_percent) + "%";

    if(livechat_filter == false){
        document.getElementById("intent-raised-div").style.display = "flex";
        document.getElementById("request-raised-div").style.display = "flex";
        document.getElementById("agent-count-div").style.display = "flex";
        document.getElementById("livechat-percent-div").style.display = "flex";
        if(intent_raised_total < intent_raised_previous_day){
            if(intent_raised_previous_day == 0){
                document.getElementById("intent-raised-text").innerHTML = "No data from yesterday";
            }
            else{
                document.getElementById("intent-raised-neg").style.display = "flex";
                intent_raised_data = Math.round(((intent_raised_previous_day-intent_raised_total)/intent_raised_previous_day)*100);
                document.getElementById("intent-raised-data").innerHTML = "-" + String(intent_raised_data) + "%";
                document.getElementById("intent-raised-data").style.color = "#C9291F";
            }
        }
        else{
            if(intent_raised_total == 0){
                document.getElementById("intent-raised-text").innerHTML = "No data for today";
            }
            else{
                document.getElementById("intent-raised-pos").style.display = "flex";
                intent_raised_data = Math.round(((intent_raised_total-intent_raised_previous_day)/intent_raised_total)*100);
                document.getElementById("intent-raised-data").innerHTML = String(intent_raised_data) + "%";
                document.getElementById("intent-raised-data").style.color = "#00B051";
            }
        }
        if(request_raised_total < request_raised_previous_day){
            if(request_raised_previous_day == 0){
                document.getElementById("request-raised-text").innerHTML = "No data from yesterday";
            }
            else{
                document.getElementById("request-raised-neg").style.display = "flex";
                request_raised_data = Math.round(((request_raised_previous_day-request_raised_total)/request_raised_previous_day)*100);
                document.getElementById("request-raised-data").innerHTML = "-" + String(request_raised_data) + "%";
                document.getElementById("request-raised-data").style.color = "#C9291F";
            }
        }
        else{
            if(request_raised_total == 0){
                document.getElementById("request-raised-text").innerHTML = "No data for today";
            }
            else{
                document.getElementById("request-raised-pos").style.display = "flex";
                request_raised_data = Math.round(((request_raised_total-request_raised_previous_day)/request_raised_total)*100);
                document.getElementById("request-raised-data").innerHTML = String(request_raised_data) + "%";
                document.getElementById("request-raised-data").style.color = "#00B051";
            }
        }
        if(agent_connect_total < agent_connect_previous_day){
            if(agent_connect_previous_day == 0){
                document.getElementById("agent-count-text").innerHTML = "No data from yesterday";
            }
            else{
                document.getElementById("agent-count-neg").style.display = "flex";
                agent_connect_data = Math.round(((agent_connect_previous_day-agent_connect_total)/agent_connect_previous_day)*100);
                document.getElementById("agent-count-data").innerHTML = "-" + String(agent_connect_data) + "%";
                document.getElementById("agent-count-data").style.color = "#C9291F";
            }
        }
        else{
            if(agent_connect_total == 0){
                document.getElementById("agent-count-text").innerHTML = "No data for today";
            }
            else{
                document.getElementById("agent-count-pos").style.display = "flex";
                agent_connect_data = Math.round(((agent_connect_total-agent_connect_previous_day)/agent_connect_total)*100);
                document.getElementById("agent-count-data").innerHTML = String(agent_connect_data) + "%";
                document.getElementById("agent-count-data").style.color = "#00B051";
            }
        }
        if(intent_raised_previous_day == 0)
            livechat_percent_previous_day = 0;
        else
            livechat_percent_previous_day = Math.round((agent_connect_previous_day / intent_raised_previous_day) * 100);

        if(livechat_conversion_percent < livechat_percent_previous_day){
            if(livechat_percent_previous_day == 0){
                document.getElementById("livechat-percent-text").innerHTML = "No data from yesterday";
            }
            else{
                document.getElementById("livechat-percent-neg").style.display = "flex";
                livechat_percent_data = Math.round(((livechat_percent_previous_day-livechat_conversion_percent)/livechat_percent_previous_day)*100);
                document.getElementById("livechat-percent-data").innerHTML = "-" + String(livechat_percent_data) + "%";
                document.getElementById("livechat-percent-data").style.color = "#C9291F";
            }
        }
        else{
            if(livechat_conversion_percent == 0){
                document.getElementById("livechat-percent-text").innerHTML = "No data for today";
            }
            else{
                document.getElementById("livechat-percent-pos").style.display = "flex";
                livechat_percent_data = Math.round(((livechat_conversion_percent-livechat_percent_previous_day)/livechat_conversion_percent)*100);
                document.getElementById("livechat-percent-data").innerHTML = String(livechat_percent_data) + "%";
                document.getElementById("livechat-percent-data").style.color = "#00B051";
            }
        }
    }

}

document.getElementById("flow_conversion_analytics_table_scroll").addEventListener("scroll", function(event)
{
    var el = document.getElementById("flow_conversion_analytics_table_scroll");
    if (($(el).scrollTop() + $(el).innerHeight() >= $(el)[0].scrollHeight)) {
        document.getElementById('conversion_flow_analytics_loader').style.display = "block";
        flow_analytics_counter += 20;
        table_body = document.getElementById("flow_conversion_analytics_table_body");
        render_flow_conversion_analytics_data(flow_analytics_counter, table_body);
        document.getElementById('conversion_flow_analytics_loader').style.display = "none";
    }
});

document.getElementById("intent_conversion_analytics_table_scroll").addEventListener("scroll", function(event)
{
    var el = document.getElementById("intent_conversion_analytics_table_scroll");
    if (($(el).scrollTop() + $(el).innerHeight() >= $(el)[0].scrollHeight) && show_intent_data == true && is_last_page == false) {
        show_intent_data = false;
        intent_analytics_scrolled = true;
        intent_analytics_page += 1;
        load_intent_conversion_analytics();
    }
});

document.getElementById("whatsapp_block_analytics_table_scroll").addEventListener("scroll", function(event)
{
    let el = document.getElementById("whatsapp_block_analytics_table_scroll");
    if (($(el).scrollTop() + $(el).innerHeight() >= $(el)[0].scrollHeight) && show_block_spam_data == true && is_last_page_whatsapp == false) {
        show_block_spam_data = false;
        whatsapp_block_analytics_scrolled = true;
        whatsapp_block_analytics_page += 1;
        load_whatsapp_block_analytics();
    }
});

document.getElementById("whatsapp_catalogue_table_scroll").addEventListener("scroll", function (event) {
    let el = document.getElementById("whatsapp_catalogue_table_scroll");
    if (($(el).scrollTop() + $(el).innerHeight() >= $(el)[0].scrollHeight) && show_catalogue_data == true && is_last_page_catalogue == false) {
        show_catalogue_data = false;
        whatsapp_catalogue_analytics_scrolled = true;
        whatsapp_catalogue_analytics_page += 1;
        load_whatsapp_catalogue_analytics();
    }
});

document.getElementById("traffic_conversion_analytics_table_scroll").addEventListener("scroll", function(event)
{
    var el = document.getElementById("traffic_conversion_analytics_table_scroll");
    if (($(el).scrollTop() + $(el).innerHeight() >= $(el)[0].scrollHeight) && show_traffic_data == true && is_last_page_traffic == false) {
        show_traffic_data = false;
        traffic_analytics_scrolled = true;
        traffic_analytics_page += 1;
        load_traffic_conversion_analytics();
    }
});

document.getElementById("welcome_conversion_analytics_table_scroll").addEventListener("scroll", function(event)
{
    var el = document.getElementById("welcome_conversion_analytics_table_scroll");
    if (($(el).scrollTop() + $(el).innerHeight() >= $(el)[0].scrollHeight) && show_welcome_data == true && is_last_page_welcome== false) {
        show_welcome_data = false;
        welcome_analytics_scrolled = true;
        welcome_analytics_page += 1;
        load_welcome_banner_analytics();
    }
});

function validate_email_addresses(email_id, input_field_id) {
    let invalid_email_addresses = [];
    let find_duplicates = arr => arr.filter((item, index) => arr.indexOf(item) != index)
    let duplicate_email_addresses = [...new Set(find_duplicates(email_id.split(",")))];

    for (let id of email_id.split(",")) {
        if (!validate_email(id)) {
            invalid_email_addresses.push(id);
        }
    }
    let validation_error_message = "";
    let duplicate_error_message = "";

    if (!invalid_email_addresses.length && !duplicate_email_addresses.length) return true;
    if (invalid_email_addresses.length == 1) {
        validation_error_message = `<span style="color: red;">Error:</span> The email address <span style="color: red;">${invalid_email_addresses.join(", ")}</span> provided is invalid. Please enter a valid email address to proceed.`
    } else if (invalid_email_addresses.length > 1) {
        validation_error_message = `<span style="color: red;">Error:</span> The email addresses <span style="color: red;">${invalid_email_addresses.join(", ")}</span> provided are invalid. Please enter valid email addresses to proceed.`
    }
    if (duplicate_email_addresses.length == 1) {
        duplicate_error_message = `<span style="color: red;">Error:</span> Duplicate email address <span style="color: red;">${duplicate_email_addresses.join(", ")}</span> added. Kindly remove the duplicate email address to proceed.`
    } else if (duplicate_email_addresses.length > 1) {
        duplicate_error_message = `<span style="color: red;">Error:</span> Duplicate email addresses <span style="color: red;">${duplicate_email_addresses.join(", ")}</span> added. Kindly remove the duplicate email addresses to proceed.`
    }
    if (invalid_email_addresses.length) {
        $("#" + input_field_id).siblings("p.email-validation-error").html(validation_error_message)
        $("#" + input_field_id).siblings("p.email-validation-error").show();
    } else {
        $("#" + input_field_id).siblings("p.email-validation-error").html('')
        $("#" + input_field_id).siblings("p.email-validation-error").hide();
    }

    if (duplicate_email_addresses.length) {
        $("#" + input_field_id).siblings("p.duplicate-email-error").html(duplicate_error_message)
        $("#" + input_field_id).siblings("p.duplicate-email-error").show();
    } else {
        $("#" + input_field_id).siblings("p.duplicate-email-error").html('')
        $("#" + input_field_id).siblings("p.duplicate-email-error").hide();
    }
    return false
}

function export_analytics_excel(type, open_modal){
    if (type == "catalogue_conversion_analytics") {
        if (channel_list.length != 0 && !channel_list.includes("WhatsApp")) {
            M.toast({"html": 'There is no data available to export for the selected channel'}, 3000, "rounded");
            return
        }
    }
    bot_pk = get_url_vars()["bot_id"];
    selected_language = get_url_vars()["selected_language"]
    email_id = window.user_email;
    channel_list = [];
    source_list = [];
    let spam_type = "All"
    let is_catalogue_purchased = "all";
    if(type=="flow_conversion_analytics"){
        flow_conversion_filter_result = check_flow_conversion_analytics_filter();
        start_date = flow_conversion_filter_result.start_date;
        end_date = flow_conversion_filter_result.end_date;
        channel_list = flow_conversion_filter_result.channel_list;

        if(Date.parse(start_date) > Date.parse(end_date)){
            M.toast({
                "html": "Start Date should be smaller than End Date"
            }, 2000);
            return;
        }

        const st_date = new Date(start_date)
        const ed_date = new Date(end_date)

        email_id = document.getElementById("export-data-email-flow-conversion-analytics").value.replace(/\s/g, '')

        if(!open_modal){
            $('#modal-email-for-export-flow-conversion-analytics').modal('open');
            return
        }
        if (!validate_email_addresses(email_id, "export-data-email-flow-conversion-analytics")) {
            return;
        }
    }

    else if(type=="intent_conversion_analytics"){
        intent_conversion_filter_result = check_intent_conversion_analytics_filter();
        start_date = intent_conversion_filter_result.start_date;
        end_date = intent_conversion_filter_result.end_date;
        channel_list = intent_conversion_filter_result.channel_list;

        if(Date.parse(start_date) > Date.parse(end_date)){
            M.toast({
                "html": "Start Date should be smaller than End Date"
            }, 2000);
            return;
        }

        const st_date = new Date(start_date)
        const ed_date = new Date(end_date)

        email_id = document.getElementById("export-data-email-intent-conversion-analytics").value.replace(/\s/g, '')

        if(!open_modal){
            $('#modal-email-for-export-intent-conversion-analytics').modal('open');
            return
        }
        if (!validate_email_addresses(email_id, "export-data-email-intent-conversion-analytics")) {
            return;
        }

    }

    else if(type=="livechat_conversion_analytics"){
        livechat_conversion_filter_result = check_livechat_conversion_analytics_filter();
        start_date = livechat_conversion_filter_result.start_date;
        end_date = livechat_conversion_filter_result.end_date;
        channel_list = livechat_conversion_filter_result.channel_list;

        if(Date.parse(start_date) > Date.parse(end_date)){
            M.toast({
                "html": "Start date cannot be less than end date."
            }, 2000);
            return;
        }

        const st_date = new Date(start_date)
        const ed_date = new Date(end_date)

        email_id = document.getElementById("export-data-email-livechat-conversion-analytics").value.replace(/\s/g, '')

        if(!open_modal){
            $('#modal-email-for-export-livechat-conversion-analytics').modal('open');
            return
        }
        if (!validate_email_addresses(email_id, "export-data-email-livechat-conversion-analytics")) {
            return;
        }

    }
    else if(type=="traffic_conversion_analytics"){
        traffic_conversion_filter_result = check_traffic_conversion_analytics_filter();
        start_date = traffic_conversion_filter_result.start_date;
        end_date = traffic_conversion_filter_result.end_date;
        source_list = traffic_conversion_filter_result.source_list;

        if(Date.parse(start_date) > Date.parse(end_date)){
            M.toast({
                "html": "Start Date should be smaller than End Date"
            }, 2000);
            return;
        }
        email_id = document.getElementById("export-data-email-traffic-conversion-analytics").value.replace(/\s/g, '')
        
        if(!open_modal){
            $('#modal-email-for-export-traffic-conversion-analytics').modal('open');      
            return
        }
        if (!validate_email_addresses(email_id, "export-data-email-traffic-conversion-analytics")) {
            return;
        }
    }
    else if(type=="welcome_conversion_analytics"){
        welcome_conversion_filter_result = check_welcome_banner_analytics_filter();
        start_date = welcome_conversion_filter_result.start_date;
        end_date = welcome_conversion_filter_result.end_date;

        if(Date.parse(start_date) > Date.parse(end_date)){
            M.toast({
                "html": "Start Date should be smaller than End Date"
            }, 2000);
            return;
        }
        email_id = document.getElementById("export-data-email-welcome-banner-click").value.replace(/\s/g, '')
        
        if(!open_modal){
            $('#modal-email-for-export-welcome-banner-clicks').modal('open');      
            return
        }
        if (!validate_email_addresses(email_id, "export-data-email-welcome-banner-click")) {
            return;
        }
    } else if (type == "dropoff_conversion_analytics"){
        dropoff_conversion_filter_result = check_dropoff_conversion_analytics_filter();
        start_date = dropoff_conversion_filter_result.start_date;
        end_date = dropoff_conversion_filter_result.end_date;
        channel_list = dropoff_conversion_filter_result.channel_list;

        if(Date.parse(start_date) > Date.parse(end_date)){
            M.toast({
                "html": "Start Date should be smaller than End Date"
            }, 2000);
            return;
        }
        const st_date = new Date(start_date)
        const ed_date = new Date(end_date)

        email_id = document.getElementById("export-data-email-Customer-Dropoff-analytics").value.replace(/\s/g, '')
        
        if(!open_modal){
            $('#modal-email-for-export-Customer-Dropoff-analytics').modal('open');      
            return
        }
        if (!validate_email_addresses(email_id, "export-data-email-Customer-Dropoff-analytics")) {
            return;
        }

    } else if (type === "whatsapp_block_analytics") {
        whatsapp_block_filter_result = check_whatsapp_block_analytics_filter();
        start_date = whatsapp_block_filter_result.start_date
        end_date = whatsapp_block_filter_result.end_date
        spam_type = whatsapp_block_filter_result.spam_type

        if(Date.parse(start_date) > Date.parse(end_date)){
            M.toast({
                "html": "Start Date should be smaller than End Date"
            }, 2000);
            return;
        }
        const st_date = new Date(start_date)
        const ed_date = new Date(end_date)

        email_id = document.getElementById("export-data-email-whatsapp_block").value.replace(/\s/g, '')
        
        if(!open_modal){
            $('#modal-email-for-export-blocked-users-WhatsApp').modal('open');      
            return
        }
        if (!validate_email_addresses(email_id, "export-data-email-whatsapp_block")) {
            return;
        }

    } else if (type === "catalogue_conversion_analytics") {
        catalogue_filter_data = get_whatsapp_catalogue_filter_data();
        start_date = catalogue_filter_data.start_date
        end_date = catalogue_filter_data.end_date
        is_catalogue_purchased = catalogue_filter_data.is_catalogue_purchased

        if(Date.parse(start_date) > Date.parse(end_date)){
            M.toast({
                "html": "Start Date should be smaller than End Date"
            }, 2000);
            return;
        }
        const st_date = new Date(start_date)
        const ed_date = new Date(end_date)

        email_id = document.getElementById("export-data-email-catalogue-conversion").value.replace(/\s/g, '')
        
        if(!open_modal){
            $('#modal-email-for-export-whatsapp-catalogue-carts').modal('open');      
            return
        }
        if (!validate_email_addresses(email_id, "export-data-email-catalogue-conversion")) {
            return;
        }

    }

    $("p.email-validation-error, p.duplicate-email-error").html('')
    $("p.email-validation-error, p.duplicate-email-error").hide();
    $('.modal').modal('close');

    var json_string = JSON.stringify({
        bot_pk: bot_pk,
        start_date :start_date,
        end_date:end_date,
        type:type,
        channel_list:channel_list,
        email_id:email_id,
        source_list: source_list,
        selected_language: selected_language,
        spam_type,
        is_catalogue_purchased,
    });

    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);
    var xhttp = new XMLHttpRequest();
    var params = 'json_string='+json_string
    xhttp.open("POST", "/chat/export-conversion-analytics-excel/", true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);

            if(response["status"]==200){

                if ("export_file_path" in response){
                    var file_url = response["export_file_path"]
                    window.open(file_url)
                }else if ("email_id" in response) {
                    var email_id = response["email_id"];
                    setTimeout(function (e) {
                        M.toast({
                            "html": "You will receive the dump over email in less than an hour on the email address(es) provided"
                        });
                    }, 1000)
                }

            } else if (response["status"] == 201) {
                let email_id = response["email_id"];
                M.toast({
                    "html": "You will receive the dump over email in 24 hours on the email address(es) provided"
                });
            }

            else{
                M.toast({
                    "html": "Internal server error please report error."
                });
            }
        }
    }
    xhttp.send(params);

}

function search_from_table(table_id, input_id) {
    // Declare variables
    var input = document.getElementById(input_id);
    var filter = input.value.toUpperCase();
    var table = document.getElementById(table_id);
    var trs = table.tBodies[0].getElementsByTagName("tr");

    var tds
    let tr_counter = trs.length;
    for (var i = 0; i < trs.length; i++) {
    tds = trs[i].getElementsByTagName("td");
        trs[i].style.display = "none";
        for (var i2 = 0; i2 < tds.length; i2++) {
            if (tds[i2].innerText.toUpperCase().indexOf(filter) > -1) {
                trs[i].style.display = "";
                tr_counter--;
                continue;
            }
        }
    }

    if (table_id == "flow_conversion_analytics_table"){
        if(tr_counter == trs.length){
            document.getElementById("flow_conversion_analytics_no_data_found").style.display = "flex";
            document.getElementById("flow_conversion_analytics_table_scroll").style.display = "none";
        }
        else{
            document.getElementById("flow_conversion_analytics_no_data_found").style.display = "none";
            document.getElementById("flow_conversion_analytics_table_scroll").style.display = "block";
        }
    } else if (table_id == "intent_conversion_analytics_table"){
        if(tr_counter == trs.length){
            document.getElementById("intent_conversion_analytics_no_data_found").style.display = "flex";
            document.getElementById("intent_conversion_analytics_table_scroll").style.display = "none";
        }
        else{
            document.getElementById("intent_conversion_analytics_no_data_found").style.display = "none";
            document.getElementById("intent_conversion_analytics_table_scroll").style.display = "block";
        }
    } else if (table_id == "traffic_conversion_analytics_table"){
        if(tr_counter == trs.length){
            document.getElementById("traffic_conversion_analytics_no_data_found").style.display = "flex";
            document.getElementById("traffic_conversion_analytics_table_scroll").style.display = "none";
        }
        else{
            document.getElementById("traffic_conversion_analytics_no_data_found").style.display = "none";
            document.getElementById("traffic_conversion_analytics_table_scroll").style.display = "block";
        }

    } else if (table_id == "welcome_banner_analytics_table"){

        if (tr_counter == trs.length){
                document.getElementById("welcome_conversion_analytics_no_data_found").style.display = "flex";
                document.getElementById("welcome-banner-table-data-total-area").style.display = "none";
                document.getElementById("welcome_conversion_analytics_table_scroll").style.display = "none";
        } else {
                document.getElementById("welcome_conversion_analytics_no_data_found").style.display = "none";
                document.getElementById("welcome_conversion_analytics_table_scroll").style.display = "block";

            if(filter.trim() == ""){
                if(document.getElementById("total_clicks")){
                    if(document.getElementById("total_clicks").innerHTML.toString().trim() != "null" && document.getElementById("total_clicks").innerHTML.toString().trim() != "" ){
                        document.getElementById("welcome-banner-table-data-total-area").style.display = ""
                    }
                }
            } else if(tds.length > 1){
               document.getElementById("welcome-banner-table-data-total-area").style.display = "none"
            }
        }

    } else if (table_id == "dropoff_banner_analytics_table"){
        if(tr_counter == trs.length){
            document.getElementById("dropoff_conversion_analytics_no_data_found").style.display = "flex";
            document.getElementById("dropoff_conversion_analytics_table_scroll").style.display = "none";
        } else {
            document.getElementById("dropoff_conversion_analytics_no_data_found").style.display = "none";
            document.getElementById("dropoff_conversion_analytics_table_scroll").style.display = "block";
        }
    } else if (table_id == "whatsapp_block_analytics_table") {
        if(tr_counter == trs.length){
            document.getElementById("whatsapp_block_analytics_no_data_found").style.display = "flex";
            document.getElementById("whatsapp_block_analytics_table_scroll").style.display = "none";
        } else {
            document.getElementById("whatsapp_block_analytics_no_data_found").style.display = "none";
            document.getElementById("whatsapp_block_analytics_table_scroll").style.display = "block";
        }
    } else if (table_id == "whatsapp_catalogue_table") {
        if(tr_counter == trs.length){
            $("#whatsapp_catalogue_no_data_found").css("display", "flex");
            $("#whatsapp_catalogue_table_scroll").hide();
        } else {
            $("#whatsapp_catalogue_no_data_found").hide();
            $("#whatsapp_catalogue_table_scroll").show();
        }
    }

}

function get_url_vars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m, key, value) {
        vars[key] = value;
    });
    return vars;
}

function validate_email(email) {

    var regex = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
    var ctrl = email;

    if (ctrl != "" && regex.test(ctrl)) {
        return true;
    } else {
        return false;
    }
}

function create_custom_dropdowns() {
    $(".easychat-console-select-drop").each(function(i, select) {
        if (!$(this).next().hasClass('easychat-dropdown-select-custom')) {
            $(this).after('<div class="easychat-dropdown-select-custom wide ' + ($(this).attr('class') || '') + '" tabindex="0"><span class="current"></span><div class="list"><ul></ul></div></div>');
            var dropdown = $(this).next();

            var options = $(select).find('span');

            var selected = $(this).find('easychat-console-language-option:selected');

            dropdown.find('.current').html(selected.data('display-text') || selected.text());
            options.each(function(j, o) {

                var display = $(o).data('display-text') || '';
                dropdown.find('ul').append('<li class="easychat-console-language-option ' + ($(o).is(':selected') ? 'selected' : '') + '" data-value="' + $(o).data("value") + '" data-display-text="' + display + '">' + $(o).text() + '</li>');
            });
        }
    });

    $('.easychat-dropdown-select-custom ul').before('<div class="dd-search"> <svg class="drop-language-search-icon" width="15" height="14" viewBox="0 0 15 14" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M13.1875 12.0689L9.88352 8.76489C10.6775 7.81172 11.0734 6.58914 10.9889 5.35148C10.9045 4.11382 10.3461 2.95638 9.42994 2.11993C8.51381 1.28349 7.31047 0.83244 6.07025 0.86062C4.83003 0.8888 3.64842 1.39404 2.77123 2.27123C1.89404 3.14842 1.3888 4.33003 1.36062 5.57025C1.33244 6.81047 1.78349 8.01381 2.61993 8.92994C3.45638 9.84607 4.61382 10.4045 5.85148 10.4889C7.08914 10.5734 8.31172 10.1775 9.26489 9.38352L12.5689 12.6875L13.1875 12.0689ZM2.25002 5.68752C2.25002 4.90876 2.48095 4.14748 2.91361 3.49996C3.34627 2.85244 3.96122 2.34776 4.6807 2.04974C5.40019 1.75172 6.19189 1.67375 6.95569 1.82568C7.71949 1.97761 8.42108 2.35262 8.97175 2.90329C9.52242 3.45396 9.89743 4.15555 10.0494 4.91935C10.2013 5.68315 10.1233 6.47485 9.8253 7.19433C9.52728 7.91382 9.0226 8.52877 8.37508 8.96143C7.72756 9.39409 6.96628 9.62502 6.18752 9.62502C5.14358 9.62386 4.14274 9.20865 3.40457 8.47047C2.66639 7.7323 2.25118 6.73145 2.25002 5.68752Z" fill="#909090"/></svg><input id="txtSearchValue" autocomplete="off" placeholder="Search Language" onkeyup="filter()" class="dd-searchbox" type="text"></div>');
    $('.easychat-dropdown-select-custom span').before(' <svg class="drop-language-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"> <rect width="24" height="24" fill="white"/><path fill-rule="evenodd" clip-rule="evenodd" d="M8.62477 3C8.92313 3 9.20927 3.11832 9.42024 3.32894C9.63121 3.53955 9.74973 3.82521 9.74973 4.12306V5.24612H13.1246C13.4229 5.24612 13.7091 5.36444 13.9201 5.57506C14.131 5.78567 14.2495 6.07133 14.2495 6.36918C14.2495 6.66703 14.131 6.95269 13.9201 7.1633C13.7091 7.37392 13.4229 7.49224 13.1246 7.49224H11.5249C11.1238 9.36076 10.4714 11.1665 9.58549 12.8605C9.91172 13.258 10.256 13.6421 10.6137 14.0127C10.7163 14.1189 10.7969 14.2442 10.851 14.3815C10.9051 14.5188 10.9316 14.6654 10.9289 14.8129C10.9262 14.9605 10.8945 15.106 10.8355 15.2413C10.7765 15.3765 10.6914 15.4989 10.585 15.6013C10.4786 15.7037 10.3531 15.7842 10.2156 15.8382C10.078 15.8922 9.9312 15.9186 9.78344 15.916C9.63568 15.9133 9.48989 15.8816 9.3544 15.8227C9.2189 15.7638 9.09636 15.6788 8.99376 15.5727C8.78227 15.3525 8.57415 15.1279 8.37053 14.8988C7.37625 16.3736 6.20217 17.7192 4.8753 18.9048C4.65254 19.1002 4.36149 19.1999 4.06547 19.1822C3.76945 19.1645 3.49241 19.0308 3.2946 18.8103C3.09679 18.5897 2.99423 18.3001 3.00921 18.0044C3.02419 17.7087 3.15551 17.4309 3.37461 17.2314C4.74286 16.009 5.92861 14.5972 6.89572 13.039C6.26734 12.1494 5.7081 11.213 5.22291 10.2381C5.15171 10.1056 5.10791 9.96011 5.09409 9.81035C5.08028 9.66059 5.09674 9.50958 5.14249 9.36629C5.18824 9.223 5.26236 9.09034 5.36044 8.97618C5.45852 8.86203 5.57857 8.76871 5.71347 8.70175C5.84836 8.63479 5.99535 8.59556 6.14572 8.58639C6.29609 8.57722 6.44678 8.5983 6.58883 8.64837C6.73089 8.69844 6.86142 8.77648 6.97269 8.87787C7.08396 8.97926 7.1737 9.10193 7.23658 9.2386C7.49982 9.76644 7.78668 10.2808 8.09605 10.7794C8.56515 9.7305 8.94201 8.63102 9.21762 7.49224H4.12495C3.8266 7.49224 3.54046 7.37392 3.32949 7.1633C3.11852 6.95269 3 6.66703 3 6.36918C3 6.07133 3.11852 5.78567 3.32949 5.57506C3.54046 5.36444 3.8266 5.24612 4.12495 5.24612H7.49982V4.12306C7.49982 3.82521 7.61834 3.53955 7.82931 3.32894C8.04028 3.11832 8.32642 3 8.62477 3ZM15.3745 9.73836C15.5834 9.73847 15.7881 9.79663 15.9657 9.90632C16.1433 10.016 16.2869 10.1729 16.3802 10.3594L19.745 17.0776C19.7528 17.0912 19.7603 17.1051 19.7675 17.1191L20.8812 19.3428C21.0147 19.6093 21.0366 19.918 20.9422 20.2007C20.8478 20.4835 20.6448 20.7172 20.3777 20.8505C20.1107 20.9838 19.8016 21.0057 19.5184 20.9114C19.2351 20.8172 19.001 20.6145 18.8675 20.3479L18.0553 18.7228H12.696L11.8815 20.3479C11.8183 20.4844 11.7283 20.6069 11.6168 20.7081C11.5053 20.8092 11.3746 20.887 11.2325 20.9368C11.0903 20.9865 10.9395 21.0073 10.7892 20.9978C10.6388 20.9883 10.4919 20.9487 10.3572 20.8814C10.2224 20.8142 10.1026 20.7206 10.0047 20.6062C9.90691 20.4918 9.83309 20.359 9.78767 20.2156C9.74224 20.0722 9.72613 19.9211 9.74029 19.7714C9.75445 19.6216 9.79859 19.4763 9.8701 19.3439L10.9838 17.1202L11.0052 17.0776L14.3688 10.3594C14.4622 10.1729 14.6057 10.016 14.7833 9.90632C14.9609 9.79663 15.1656 9.73847 15.3745 9.73836ZM13.8198 16.4767H16.9292L15.2807 12.4524L13.8198 16.4767Z" fill="#4B4B4B"/></svg>');

    var url_string = window.location.href
    var url = new URL(url_string);
    var selected_language = url.searchParams.get("selected_language");
    if(selected_language == null){
        selected_language = "en";
    }
    $(".easychat-dropdown-select-custom ul li[data-value='" + selected_language + "']").addClass('easychat-lang-selected');
    var default_select_lang_drop = $('.easychat-dropdown-select-custom ul li[data-value="' + selected_language + '"]').text();
    $('.current').html(default_select_lang_drop);
    $('.easychat-dropdown-select-custom ul li:last').after('<div class="custom-drop-nodata-found-div">No result found</div>');



}


// Event listeners

// Open/close
$(document).on('click', '.easychat-dropdown-select-custom', function(event) {
    if ($(event.target).hasClass('dd-searchbox')) {
        return;
    }
    $('.easychat-dropdown-select-custom').not($(this)).removeClass('open');
    $('.custom-drop-nodata-found-div').hide();
    $(this).toggleClass('open');
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

function filter() {
    var valThis = $('#txtSearchValue').val();
    $('.easychat-dropdown-select-custom ul > li').each(function() {
        var text = $(this).text();
        (text.toLowerCase().indexOf(valThis.toLowerCase()) > -1) ? $(this).show(): $(this).hide();
    });

    if ($('.easychat-dropdown-select-custom ul').children(':visible').not('.custom-drop-nodata-found-div').length === 0) {
        $('.custom-drop-nodata-found-div').show();
    } else {
        $('.custom-drop-nodata-found-div').hide();
    }
};
// Search

// Option click
$(document).on('click', '.easychat-dropdown-select-custom .easychat-console-language-option', function(event) {
    $(this).closest('.list').find('.easychat-lang-selected').removeClass('easychat-lang-selected');
    $(this).addClass('easychat-lang-selected');

    var text = $(this).data('display-text') || $(this).text();

    $(this).closest('.easychat-dropdown-select-custom').find('.current').text(text);
    $(this).closest('.easychat-dropdown-select-custom').prev('select').val($(this).data('value')).trigger('change');
    var url_string = window.location.href
    var url = new URL(url_string);
    bot_id = url.searchParams.get("bot_id");
    $('#modal-language-change-loader').modal("open");
    changed_language = $(this).attr('data-value');
    setTimeout(function (){
        window.location = "/chat/conversion-analytics/?bot_id=" + bot_id + "&selected_language=" + changed_language;
    },2000)
});

// Keyboard events
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
    create_custom_dropdowns();
});


function api_fail_message_none(){
    document.getElementById("translation_api_toast_container").style.display = "none";
}

function mirror_search_bar(search_bar_id){
    search_bar_id.addClass("language-right-to-left-wrapper");
}


// WhatsApp Catalogue Conversion Analytics

function load_whatsapp_catalogue_analytics() {

    if (channel_list.length != 0 && !channel_list.includes("WhatsApp")) {
        $("#whatsapp_catalogue_no_data_found").css("display", "flex");
        $("#whatsapp_catalogue_table_scroll").hide();
        return;
    }

    let bot_pk = get_url_vars()["bot_id"];
    let catalogue_filter_data = get_whatsapp_catalogue_filter_data();
    let { start_date, end_date, is_catalogue_purchased } = catalogue_filter_data;

    let today = new Date();
    today = today.getFullYear() + "-" + String(today.getMonth() + 1).padStart(2, '0') + "-" + String(today.getDate()).padStart(2, '0');

    if (Date.parse(start_date) > Date.parse(end_date)) {

        M.toast({
            "html": "Start Date should be smaller than End Date"
        }, 2000);

        reset_start_end_date("conversion_catalogue_custom_start_date", "conversion_catalogue_custom_end_date");

        return;
    }

    if (Date.parse(today) < Date.parse(end_date)) {
        M.toast({
            "html": "End date cannot be greater than today's date."
        }, 2000);

        reset_start_end_date("conversion_catalogue_custom_start_date", "conversion_catalogue_custom_end_date");

        return;
    }

    if (Date.parse(start_date) > Date.parse(today)) {
        M.toast({
            "html": "Start date cannot be greater than today's date."
        }, 2000);

        reset_start_end_date("conversion_catalogue_custom_start_date", "conversion_catalogue_custom_end_date");

        return;
    }

    $("#conversion_catalogue_custom_start_date").attr("current_applied_date", start_date)
    $("#conversion_catalogue_custom_end_date").attr("current_applied_date", end_date)

    if (whatsapp_catalogue_analytics_page <= 0) whatsapp_catalogue_analytics_page = 1

    if (document.getElementById("whatsapp_catalogue_analytics_table_body") && whatsapp_catalogue_analytics_scrolled == false) {
        let table_body = document.getElementById("whatsapp_catalogue_analytics_table_body");
        table_body.remove();
        catalogue_table_body_removed = true
    }

    $("#conversion_catalogue_custom_start_date").attr("current_applied_date", start_date)
    $("#conversion_catalogue_custom_end_date").attr("current_applied_date", end_date)

    $("#whatsapp_catalogue_no_data_found").hide();
    $("#whatsapp_catalogue_table_scroll, #whatsapp_catalogue_analytics_loader").show();

    let xhttp = new XMLHttpRequest();
    let params = '';
    xhttp.open("GET", "/chat/get-whatsapp-catalogue-analytics/?bot_pk=" + bot_pk + "&start_date=" + start_date + "&end_date=" + end_date + "&is_catalogue_purchased=" + is_catalogue_purchased + "&page=" + whatsapp_catalogue_analytics_page, true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = async function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                if (catalogue_table_body_removed) {
                    let table = document.getElementById("whatsapp_catalogue_table");
                    table_body = table.appendChild(document.createElement('tbody'))
                    table_body.setAttribute("id", "whatsapp_catalogue_analytics_table_body");
                    catalogue_analytics_counter = 1;
                    catalogue_table_body_removed = false;
                } else {
                    table_body = document.getElementById("whatsapp_catalogue_analytics_table_body");
                }
                let catalogue_cart_data = response["catalogue_cart_data"];
                is_last_page_catalogue = response["is_last_page"];
                whatsapp_analytics_api_status_code = response['status']

                if (catalogue_cart_data.length == 0) {
                    $("#whatsapp_catalogue_no_data_found").css("display", "flex");
                    $("#whatsapp_catalogue_table_scroll").hide();
                } else {
                    render_whatsapp_catalogue_analytics_data(catalogue_cart_data, table_body);
                }
            }
            $("#whatsapp_catalogue_analytics_loader").hide()

            if (Date.parse(start_date) != Date.parse(end_date)) {
                let show_start_date = convert_to_date_format(start_date);
                let show_end_date = convert_to_date_format(end_date);
                document.getElementById("whatsapp_catalogue_date_range").innerHTML = "Range : " + show_start_date + " to " + show_end_date;
            } else {
                show_date = convert_to_date_format(start_date);
                document.getElementById("whatsapp_catalogue_date_range").innerHTML = "" + show_date;
            }

            show_catalogue_data = true;
            whatsapp_catalogue_analytics_scrolled = false;
            add_catalogue_tooltip_listeners();
        } else {
            $("#whatsapp_catalogue_analytics_loader").hide()
        }
    }
    xhttp.send(params);
}

function get_whatsapp_catalogue_filter_data(){
    let start_date = default_start_date;
    let end_date = default_end_date;
    let is_catalogue_purchased = "all";

    if(document.getElementById("catalogue_week").checked){
        start_date = document.getElementById("catalogue_week").getAttribute("start_date_value");
        end_date = document.getElementById("catalogue_week").getAttribute("end_date_value");
    }
    else if(document.getElementById("catalogue_month").checked){
        start_date = document.getElementById("catalogue_month").getAttribute("start_date_value");
        end_date = document.getElementById("catalogue_month").getAttribute("end_date_value");
    }
    else if(document.getElementById("catalogue_three_month").checked){
        start_date = document.getElementById("catalogue_three_month").getAttribute("start_date_value");
        end_date = document.getElementById("catalogue_three_month").getAttribute("end_date_value");
    }
    else if(document.getElementById("catalogue_beginning").checked){
        start_date = document.getElementById("catalogue_beginning").getAttribute("start_date_value");
        end_date = document.getElementById("catalogue_beginning").getAttribute("end_date_value");
    }
    else if(document.getElementById("catalogue_custom_date_btn").checked){
        start_date = document.getElementById("conversion_catalogue_custom_start_date").value;
        end_date = document.getElementById("conversion_catalogue_custom_end_date").value;
    }

    if($("input[name='whatsapp_catalogue_purchased_filter']:checked").length) {
        is_catalogue_purchased = $("input[name='whatsapp_catalogue_purchased_filter']:checked").val();
    }

    return {
        start_date,
        end_date,
        is_catalogue_purchased
    };
}

function add_catalogue_tooltip_listeners() {
    const table_scroll_container = document.querySelector('#whatsapp_catalogue_table_scroll');
    const parent_scroll_container = document.querySelector('#easychat-content-wrapper');
    const instances =  tippy('[data-tippy-content]',{
        boundary: 'window',
        flipOnUpdate: true,
        placement: 'left',
        trigger: 'click',
        arrow: true,
        theme: 'light',
    });
    table_scroll_container.addEventListener('scroll', () => {
        instances.forEach(instance => {
            instance.hide()
        })
    })
    parent_scroll_container.addEventListener('scroll', () => {
        instances.forEach(instance => {
            instance.hide()
        })
    })
}

function resize_Textarea(id) {
    var textarea = document.getElementById(id);
    textarea.style.height = "";
    textarea.style.height = Math.min(textarea.scrollHeight, 100) + "px";
  }
$(document).ready(function () {

    $('#datepicker-1-0').datepicker({

        changeMonth: true,
        changeYear: true,
        dayNamesMin: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
        beforeShow: function (textbox, instance) {
            $('.easychat-calendar-div-wrapper').append($('#ui-datepicker-div'));
            $("#timepicker-container-1-1 .custom-timepicker").hide();
            $("#timepicker-container-1-0 .custom-timepicker").hide();
        }
    });

   initialize_range_filter()

   var url_params = get_url_vars()
   var no_of_records_per_page = 10
   if (url_params["no_of_records_per_page"] != null)
   {
        no_of_records_per_page = url_params["no_of_records_per_page"]
        $("#easychat_message_history_table_row_dropdown").val(no_of_records_per_page+"");
    }
    
    var entries_info_element = document.getElementById("table_page_info")
    if (entries_info_element) {
        var first_entry = (current_page_number-1)*no_of_records_per_page + 1
        var last_entry = (current_page_number-1)*no_of_records_per_page + current_page_entries_length
        entries_info_element.innerHTML = "Showing " + first_entry + " to " + last_entry + " of " + total_entries + " entries"
    } 

    add_intents_to_filter(url_params["bot_id"], url_params["intent_pk"])

    initialize_lead_data_metadata_update_modal()  

    meta_data_chip_sortable()


});


$(document).ready(function () {

    $('#datepicker-1-1').datepicker({

        changeMonth: true,
        changeYear: true,
        dayNamesMin: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
        beforeShow: function (textbox, instance) {
            $('.easychat-calendar-div-wrapper').append($('#ui-datepicker-div'));
            $("#timepicker-container-1-1 .custom-timepicker").hide();
            $("#timepicker-container-1-0 .custom-timepicker").hide();
        }
    });
});

function meta_data_chip_sortable() {

    $('#edit-table-modal .meta-data-chips li').hover(function() {
            $(this).find(" .drag-handle").show();
        }, function() {
            $(this).find(" .drag-handle").hide();
        })
  
        
        $('#sortable-chips').sortable({
            helper: 'clone',
                placeholder: 'drop-placeholder',
                connectWith: 'li'
        });
    

}

var high_percent = ""
var low_percent = ""


function initialize_range_filter() {

        var $range = $(".js-range-slider"),
                $from = $(".from"),
                $to = $(".to"),
                range,
                min = $range.data('min'),
                max = $range.data('max'),
                from,
                to;

        var updateValues = function() {
            low_percent = from
            high_percent = to
            $from.prop("value", from);
            $to.prop("value", to);
        };

        $range.ionRangeSlider({
            onChange: function(data) {
                from = data.from;
                to = data.to;
                updateValues();
            }
        });

        range = $range.data("ionRangeSlider");
        var updateRange = function() {
            range.update({
                from: from,
                to: to
            });
        };

        $from.on("input", function() {
            from = +$(this).prop("value");
            if (from < min) {
                from = min;
            }
            if (from > to) {
                from = to;
            }
            updateValues();
            updateRange();
        });

        $to.on("input", function() {
            to = +$(this).prop("value");
            if (to > max) {
                to = max;
            }
            if (to < from) {
                to = from;
            }
            updateValues();
            updateRange();
        });
}

function show_custom_date() {
    if (document.getElementById('date-range-custom-date').checked) {
        document.getElementById("analytics-custom-date-select-area").style.display = "block";
    } else {
        document.getElementById("analytics-custom-date-select-area").style.display = "none";

    }
}


function initialize_lead_data_metadata_update_modal(){
    
    var metadata_list = bot_metadata["lead_data_cols"]
    for( var i in bot_metadata["lead_data_cols"])
    {   
         if(metadata_list[i]["selected"] == "false")
        { 
            if(is_percentage_match_enabled == "True")
            {
            
                $('#easychat_message_history_select_column_dropdown_metadata').append('<option value='+ metadata_list[i]["name"] + '>'+ metadata_list[i]["display_name"] + '</option>')
            
            } else {
                if (metadata_list[i]["name"] != "variation_responsible" && metadata_list[i]["name"] != "percentage_match")
                {
                    $('#easychat_message_history_select_column_dropdown_metadata').append('<option value='+ metadata_list[i]["name"] + '>'+ metadata_list[i]["display_name"] + '</option>')

                }
            }
        } else {

            if(is_percentage_match_enabled == "True")
            {
            
                $('#sortable-chips').append('<li >\
                                            <svg class="drag-handle" width="14" height="16" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin: 0px 4px 2px 0px; cursor: move;display:none;">\
                                                        <path fill-rule="evenodd" clip-rule="evenodd" d="M9.91658 3.5C9.91658 4.14167 9.39158 4.66667 8.74992 4.66667C8.10825 4.66667 7.58325 4.14167 7.58325 3.5C7.58325 2.85834 8.10825 2.33334 8.74992 2.33334C9.39158 2.33334 9.91658 2.85834 9.91658 3.5ZM5.24996 2.33334C4.60829 2.33334 4.08329 2.85834 4.08329 3.50001C4.08329 4.14167 4.60829 4.66667 5.24996 4.66667C5.89163 4.66667 6.41663 4.14167\
                                                        6.41663 3.50001C6.41663 2.85834 5.89163 2.33334 5.24996 2.33334ZM4.08325 7C4.08325 6.35834 4.60825 5.83334 5.24992 5.83334C5.89159 5.83334 6.41659 6.35834 6.41659 7C6.41659 7.64167 5.89159 8.16667 5.24992 8.16667C4.60825 8.16667 4.08325 7.64167 4.08325 7ZM5.24992 11.6667C5.89159 11.6667 6.41659 11.1417 6.41659 10.5C6.41659 9.85834 5.89159 9.33334 5.24992 9.33334C4.60825 9.33334 4.08325 9.85834 4.08325 10.5C4.08325 11.1417 4.60825 11.6667 5.24992 11.6667ZM8.74992 5.83334C8.10825 5.83334 7.58325 6.35834 7.58325 7C7.58325 7.64167 8.10825 8.16667 8.74992 8.16667C9.39158 8.16667 9.91658 7.64167 9.91658 7C9.91658 6.35834 9.39158 5.83334 8.74992 5.83334ZM7.58325 10.5C7.58325 9.85834 8.10825 9.33334 8.74992 9.33334C9.39158 9.33334 9.91658 9.85834 9.91658 10.5C9.91658 11.1417 9.39158 11.6667 8.74992 11.6667C8.10825 11.6667 7.58325 11.1417 7.58325 10.5Z" fill="black">\
                                                        </path>\
                                                    </svg>\
                                            <span key="'+ metadata_list[i]["name"] +'" class="value_display_span">'+metadata_list[i]["display_name"]+
                                            '</span>\
                                            <svg class="dismiss-chip" onclick="delete_chip(this,\''+metadata_list[i]["name"]+'\', \''+metadata_list[i]["display_name"]+'\')" width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                                <path d="M4.89705 12.9462L4.96967 13.0303C5.23594 13.2966 5.6526 13.3208 5.94621 13.1029L6.03033 13.0303L9 10.061L11.9697 13.0303C12.2626 13.3232 12.7374 13.3232 13.0303 13.0303C13.3232 12.7374 13.3232 12.2626 13.0303 11.9697L10.061 9L13.0303 6.03033C13.2966 5.76406 13.3208 5.3474 13.1029 5.05379L13.0303 4.96967C12.7641 4.7034 12.3474 4.6792 12.0538 4.89705L11.9697 4.96967L9 7.939L6.03033 4.96967C5.73744 4.67678 5.26256 4.67678 4.96967 4.96967C4.67678 5.26256 4.67678 5.73744 4.96967 6.03033L7.939 9L4.96967 11.9697C4.7034 12.2359 4.6792 12.6526 4.89705 12.9462L4.96967 13.0303L4.89705 12.9462Z" fill="#7B7A7B"/>\
                                                </svg>\
                                            </li>  ')
            
            } else {
                if (metadata_list[i]["name"] != "variation_responsible" && metadata_list[i]["name"] != "percentage_match")
                {
                    $('#sortable-chips').append('<li>\
                        <svg class="drag-handle" width="14" height="16" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin: 0px 4px 2px 0px; cursor: move;display:none;">\
                                                        <path fill-rule="evenodd" clip-rule="evenodd" d="M9.91658 3.5C9.91658 4.14167 9.39158 4.66667 8.74992 4.66667C8.10825 4.66667 7.58325 4.14167 7.58325 3.5C7.58325 2.85834 8.10825 2.33334 8.74992 2.33334C9.39158 2.33334 9.91658 2.85834 9.91658 3.5ZM5.24996 2.33334C4.60829 2.33334 4.08329 2.85834 4.08329 3.50001C4.08329 4.14167 4.60829 4.66667 5.24996 4.66667C5.89163 4.66667 6.41663 4.14167\
                                                        6.41663 3.50001C6.41663 2.85834 5.89163 2.33334 5.24996 2.33334ZM4.08325 7C4.08325 6.35834 4.60825 5.83334 5.24992 5.83334C5.89159 5.83334 6.41659 6.35834 6.41659 7C6.41659 7.64167 5.89159 8.16667 5.24992 8.16667C4.60825 8.16667 4.08325 7.64167 4.08325 7ZM5.24992 11.6667C5.89159 11.6667 6.41659 11.1417 6.41659 10.5C6.41659 9.85834 5.89159 9.33334 5.24992 9.33334C4.60825 9.33334 4.08325 9.85834 4.08325 10.5C4.08325 11.1417 4.60825 11.6667 5.24992 11.6667ZM8.74992 5.83334C8.10825 5.83334 7.58325 6.35834 7.58325 7C7.58325 7.64167 8.10825 8.16667 8.74992 8.16667C9.39158 8.16667 9.91658 7.64167 9.91658 7C9.91658 6.35834 9.39158 5.83334 8.74992 5.83334ZM7.58325 10.5C7.58325 9.85834 8.10825 9.33334 8.74992 9.33334C9.39158 9.33334 9.91658 9.85834 9.91658 10.5C9.91658 11.1417 9.39158 11.6667 8.74992 11.6667C8.10825 11.6667 7.58325 11.1417 7.58325 10.5Z" fill="black">\
                                                        </path>\
                                                    </svg>\
                    <span key="'+ metadata_list[i]["name"] +'" class="value_display_span">'+metadata_list[i]["display_name"]+
                    '</span>\
                    <svg class="dismiss-chip" onclick="delete_chip(this,\''+metadata_list[i]["name"]+'\', \''+metadata_list[i]["display_name"]+'\')" width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path d="M4.89705 12.9462L4.96967 13.0303C5.23594 13.2966 5.6526 13.3208 5.94621 13.1029L6.03033 13.0303L9 10.061L11.9697 13.0303C12.2626 13.3232 12.7374 13.3232 13.0303 13.0303C13.3232 12.7374 13.3232 12.2626 13.0303 11.9697L10.061 9L13.0303 6.03033C13.2966 5.76406 13.3208 5.3474 13.1029 5.05379L13.0303 4.96967C12.7641 4.7034 12.3474 4.6792 12.0538 4.89705L11.9697 4.96967L9 7.939L6.03033 4.96967C5.73744 4.67678 5.26256 4.67678 4.96967 4.96967C4.67678 5.26256 4.67678 5.73744 4.96967 6.03033L7.939 9L4.96967 11.9697C4.7034 12.2359 4.6792 12.6526 4.89705 12.9462L4.96967 13.0303L4.89705 12.9462Z" fill="#7B7A7B"/>\
                        </svg>\
                    </li>  ')
                }
            }


            if(metadata_list[i]["name"] == "user_query")
            {
                $('#message_history_row').append('<th name="' +  metadata_list[i]["name"] + '" tabindex="0" rowspan="1" colspan="1" class="sorting"\
                                                        aria-controls="search_table" style="min-width: 100px">'
                                                       + metadata_list[i]["display_name"] +
                                                        '</th>')
            }  else if(metadata_list[i]["name"] == "location") 
            {
                $('#message_history_row').append('<th id="location-dropdown-header" name="'+metadata_list[i]["name"]+'" tabindex="0" rowspan="1" colspan="1" data-orderable="false" class="sorting_disabled" aria-controls="search_table" style="width: 110xp;">\
                                                        <select id="location-dropdown" onchange="location_details_change()">\
                                                        <option value="none" selected disabled hidden>'
                                                            + metadata_list[i]["display_name"] +
                                                        '</option>\
                                                        <option value="city">City</option>\
                                                        <option value="state">State</option>\
                                                        <option value="pincode">Pincode</option>\
                                                        </select>\
                                                        <div id="location-dropdown-container"></div>\
                                                    </th>')

            }
            else if( metadata_list[i]["name"] != "percentage_match" && metadata_list[i]["name"] != "variation_responsible")
            {   
                $('#message_history_row').append('<th name="' +  metadata_list[i]["name"] + '" data-orderable="false" tabindex="0" rowspan="1" colspan="1" class="sorting_disabled"\
                                                        aria-controls="search_table">'
                                                       + metadata_list[i]["display_name"] +
                                                  '</th>')

            } else {

                 if(is_percentage_match_enabled == "True")
                {

                    if(metadata_list[i]["name"] == "percentage_match")
                    {
                        $('#message_history_row').append('<th name="' +  metadata_list[i]["name"] + '" tabindex="0" rowspan="1" colspan="1" class="sorting" style="min-width: 80px"\
                                                            aria-controls="search_table">\
                                                            % Match\
                                                            </th>')
                        
                    } else if (metadata_list[i]["name"] == "variation_responsible") {
                        $('#message_history_row').append('<th name="' +  metadata_list[i]["name"] + '" tabindex="0" rowspan="1" colspan="1" data-orderable="false"  class="sorting_disabled"\
                                                            aria-controls="search_table" >'
                                                            + metadata_list[i]["display_name"] +
                                                            '</th>')
                    }

                }
            }

        }
    }
                                                 
}

function delete_chip(elem, name, display_name) {
    $('#easychat_message_history_select_column_dropdown_metadata').append('<option value='+ name + '>'+ display_name + '</option>')
    elem.parentElement.remove()
}

function add_to_chip() {
    var selectBox = document.getElementById("easychat_message_history_select_column_dropdown_metadata");
    var name = selectBox.options[selectBox.selectedIndex].value;
    var display_name = selectBox.options[selectBox.selectedIndex].innerHTML
    $("#easychat_message_history_select_column_dropdown_metadata option[value='"+name+"']").each(function() {
    $(this).remove();
});
    $("#easychat_message_history_select_column_dropdown_metadata").val("none");
    $('#sortable-chips').append('<li>\
                                <svg class="drag-handle" width="14" height="16" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin: 0px 4px 2px 0px; cursor: move;display:none;">\
                                                        <path fill-rule="evenodd" clip-rule="evenodd" d="M9.91658 3.5C9.91658 4.14167 9.39158 4.66667 8.74992 4.66667C8.10825 4.66667 7.58325 4.14167 7.58325 3.5C7.58325 2.85834 8.10825 2.33334 8.74992 2.33334C9.39158 2.33334 9.91658 2.85834 9.91658 3.5ZM5.24996 2.33334C4.60829 2.33334 4.08329 2.85834 4.08329 3.50001C4.08329 4.14167 4.60829 4.66667 5.24996 4.66667C5.89163 4.66667 6.41663 4.14167\
                                                        6.41663 3.50001C6.41663 2.85834 5.89163 2.33334 5.24996 2.33334ZM4.08325 7C4.08325 6.35834 4.60825 5.83334 5.24992 5.83334C5.89159 5.83334 6.41659 6.35834 6.41659 7C6.41659 7.64167 5.89159 8.16667 5.24992 8.16667C4.60825 8.16667 4.08325 7.64167 4.08325 7ZM5.24992 11.6667C5.89159 11.6667 6.41659 11.1417 6.41659 10.5C6.41659 9.85834 5.89159 9.33334 5.24992 9.33334C4.60825 9.33334 4.08325 9.85834 4.08325 10.5C4.08325 11.1417 4.60825 11.6667 5.24992 11.6667ZM8.74992 5.83334C8.10825 5.83334 7.58325 6.35834 7.58325 7C7.58325 7.64167 8.10825 8.16667 8.74992 8.16667C9.39158 8.16667 9.91658 7.64167 9.91658 7C9.91658 6.35834 9.39158 5.83334 8.74992 5.83334ZM7.58325 10.5C7.58325 9.85834 8.10825 9.33334 8.74992 9.33334C9.39158 9.33334 9.91658 9.85834 9.91658 10.5C9.91658 11.1417 9.39158 11.6667 8.74992 11.6667C8.10825 11.6667 7.58325 11.1417 7.58325 10.5Z" fill="black">\
                                                        </path>\
                                </svg>\
                                <span key="'+ name +'"  class="value_display_span">'+display_name+
                                '</span>\
                                <svg class="dismiss-chip" onclick="delete_chip(this,\''+name+'\', \''+display_name+'\')" width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                    <path d="M4.89705 12.9462L4.96967 13.0303C5.23594 13.2966 5.6526 13.3208 5.94621 13.1029L6.03033 13.0303L9 10.061L11.9697 13.0303C12.2626 13.3232 12.7374 13.3232 13.0303 13.0303C13.3232 12.7374 13.3232 12.2626 13.0303 11.9697L10.061 9L13.0303 6.03033C13.2966 5.76406 13.3208 5.3474 13.1029 5.05379L13.0303 4.96967C12.7641 4.7034 12.3474 4.6792 12.0538 4.89705L11.9697 4.96967L9 7.939L6.03033 4.96967C5.73744 4.67678 5.26256 4.67678 4.96967 4.96967C4.67678 5.26256 4.67678 5.73744 4.96967 6.03033L7.939 9L4.96967 11.9697C4.7034 12.2359 4.6792 12.6526 4.89705 12.9462L4.96967 13.0303L4.89705 12.9462Z" fill="#7B7A7B"/>\
                                    </svg>\
                                </li>  ')
    meta_data_chip_sortable()
}


function save_lead_data_table_metadata(){
    
    var url_params = get_url_vars();
    var bot_id = ""
    if (url_params["bot_id"])
    {
        bot_id = url_params["bot_id"] 
    }
    var list_span =$('#sortable-chips li').find('span').map(function(){
        return $(this)
    }).get();
  
    var selected_values = []
    var json_obj = {}
    var is_percentage_match_found = false
    var is_variation_responsible_found = false

    for(var index in list_span)
    {   
        if(list_span[index].attr('key') == "variation_responsible")
            is_variation_responsible_found = true

        if(list_span[index].attr('key') == "percentage_match")
            is_percentage_match_found = true
        
        json_obj = {"display_name": list_span[index].html(),
                    "name": list_span[index].attr('key'),
                    "selected": "true"}
       
        selected_values.push(json_obj)
        
    }

    if(selected_values.length <= 2){
        M.toast({
                    "html": "Please select more than 2 values."
                }, 2000);
        return;
    }

    var unselected_values = []

    $("#easychat_message_history_select_column_dropdown_metadata option").each(function()
    {
        if($(this).val() != "none")
        {
            if($(this).val() == "variation_responsible")
            is_variation_responsible_found = true

            if($(this).val() == "percentage_match")
                is_percentage_match_found = true

            json_obj = {"display_name": $(this).html(),
                        "name": $(this).val(),
                        "selected": "false"}
            unselected_values.push(json_obj)
        }
    });

    if (!is_variation_responsible_found) {
        json_obj = {"display_name": "Variation Responsible",
                    "name": "variation_responsible",
                    "selected": "false"
                    }
        unselected_values.push(json_obj)
    }

    if (!is_percentage_match_found) {
        json_obj = {"display_name": "Percentage Match",
                    "name": "percentage_match",
                    "selected": "false"
                    }
        unselected_values.push(json_obj)
    }


    var lead_data_cols = selected_values.concat(unselected_values); 

    var request_params = {
        "lead_data_cols": lead_data_cols,
        "bot_pk": bot_id
    };

    var json_params = JSON.stringify(request_params);
  
    json_string = EncryptVariable(json_params);
    json_string = encodeURIComponent(json_string);
    encrypted_data = {
        "json_string": encrypted_data
    };
    var params = 'json_string=' + json_string

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/chat/save-bot-lead-table-metadata/", true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                console.log("data updated successfully")
                window.location.reload()
            }
        }
    }
    xhttp.send(params);
}


function searchInfoMessageHistory(table_id, number_of_columns) {
    
    var input, filter, table, tr, td, i;
    input = document.getElementById("message-history-search-bar");
    filter = input.value.toUpperCase();
    table = document.getElementById(table_id);
    tr = table.getElementsByTagName("tr");
    no_data_shown = true
    for (var i = 1; i < tr.length; i++) {
        var display_status = false;
        for (var j = 0; j < number_of_columns; j++) {
            th = tr[i].getElementsByTagName("td")[j];
            if (th) {
                if (th.innerHTML.toUpperCase().indexOf(filter) > -1) {
                    display_status = true;
                    break;
                }
            }
        }

        if (display_status) {
            tr[i].style.display = "";
            no_data_shown = false
        } else {
            tr[i].style.display = "none";
        }
    }
    if (document.getElementById("message_history_table_pagination_div") != null) {
        if (no_data_shown == true) {
            if(document.getElementById("no_elem_found_table") != null) {
                document.getElementById("no_elem_found_table").remove()
                document.getElementById("global-selected-message-history-wrapper-div").style.visibility = "visible";
            }
            
            document.getElementById("message_history_table_pagination_div").style.display = "none";
            var no_element_found_html = '<p class="green lighten-1 black-text center" style="padding:1em; margin: 1em;" id="no_elem_found_table">No results found.</p>'
            $('#search_table_wrapper').append(no_element_found_html)
            document.getElementById("global-selected-message-history-wrapper-div").style.visibility = "hidden";
        } else {
            if(document.getElementById("no_elem_found_table") != null) {
                document.getElementById("no_elem_found_table").remove()
                document.getElementById("global-selected-message-history-wrapper-div").style.visibility = "visible";
            }
            document.getElementById("message_history_table_pagination_div").style.display = "";
        }
    }
}


var ans_hr = "", ans_min = "", ans_ampm = "";
function handle_click_time(id) {

    let all_hrs = document.querySelectorAll("#timepicker-container-" + id + " .hr-clock ul li");
    let all_mins = document.querySelectorAll("#timepicker-container-" + id + " .min-clock ul li");
    let all_ampm = document.querySelectorAll("#timepicker-container-" + id + " .ampm-clock ul li");
    all_hrs.forEach(each_hr => {
        if (each_hr.childNodes[1].checked === true) {
            each_hr.childNodes[0].classList.add("datetimepicker-selected-time");
            ans_hr = each_hr.childNodes[0].innerText;
        }
        else
            each_hr.childNodes[0].classList.remove("datetimepicker-selected-time");
    })
    all_mins.forEach(each_min => {
        if (each_min.childNodes[1].checked === true) {
            each_min.childNodes[0].classList.add("datetimepicker-selected-time");
            ans_min = each_min.childNodes[0].innerText;
        }
        else
            each_min.childNodes[0].classList.remove("datetimepicker-selected-time");
    })
    all_ampm.forEach(each_ampm => {
        if (each_ampm.childNodes[1].checked === true) {
            each_ampm.childNodes[0].classList.add("datetimepicker-selected-time");
            ans_ampm = each_ampm.childNodes[0].innerText;
        }
        else
            each_ampm.childNodes[0].classList.remove("datetimepicker-selected-time");
    })
}
function handle_time_picker_click(id) {

    if (id === "1-0")
        document.querySelector("#timepicker-container-1-1 .custom-timepicker").style.display = "none";

    if (id === "1-1")
        document.querySelector("#timepicker-container-1-0 .custom-timepicker").style.display = "none";

    document.querySelector("#timepicker-container-" + id + " .custom-timepicker").style.display = "block";

}
function close_time_modal(id) {
    document.querySelector("#timepicker-container-" + id + " .custom-timepicker").style.display = "none";
}
function handle_save_time(id) {
    document.querySelector("#timepicker-container-" + id + " .custom-timepicker").style.display = "none";
    if (ans_hr && ans_ampm && ans_min)
        document.querySelector("#time-picker-btn-" + id).value = ans_hr + " : " + ans_min + " " + ans_ampm;
}

function changed_date(id, type, event) {
    var day_arr = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
    var month_arr = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    var date = new Date(document.querySelector("#datepicker-" + id).value);
    var datenum = date.getDate();
    var month = date.getMonth();
    var year = date.getFullYear();
    var day = date.getDay();
    document.querySelector("#date-displayer-" + id + " .date").innerHTML = datenum;
    document.querySelector("#date-displayer-" + id + " .month-year").innerHTML = month_arr[month] + " " + year;
    if (day - 1 != -1) {
        document.querySelector("#date-displayer-" + id + " .day").innerHTML = day_arr[day - 1];
    } else {
        document.querySelector("#date-displayer-" + id + " .day").innerHTML = day_arr[6];
    }
    document.querySelector("#datepicker-" + id).style.opacity = "0";
    document.querySelector("#date-displayer-" + id + " .row").style.display = "flex";
}

function handle_close() {
    document.querySelector(".btns-sections").style.display = "none";
}


//Main Dropdown Section
const dropdownarrow = document.querySelector("#location-dropdown-div .dropdown svg");
const dropdown = document.querySelector("#location-dropdown-div .dropdown-wrapper-main .dropdown");
const dropdown_menu = document.querySelector("#location-dropdown-div .dropdown-menu");
const search_box = document.querySelector("#location-dropdown-div .search-box-main");
const options_list = document.querySelectorAll("#location-dropdown-div .dropdown-menu-main .option");
const all_check_boxes = document.querySelectorAll("#location-dropdown-div .item-checkbox");
const selected = new Set();

all_check_boxes.forEach((each_check_box) => {
    if (each_check_box.checked)
        selected.add(each_check_box);
})
if (selected.size !== 0)
    document.querySelector(".dropdown .title").innerText = "Select Location";


search_box.addEventListener("keyup", function (e) {
    filter_list(e.target.value);
});

function filter_list(search_term) {
    search_term = search_term.toLowerCase();
    let flag = 0;
    document.querySelector(".dropdown-menu-main .no-elem").style.display = "none";
    options_list.forEach(option => {
        let label = option.firstElementChild.firstElementChild.nextElementSibling.innerText.toLowerCase();
        if (label.indexOf(search_term) != -1) {
            flag = 1;
            option.style.display = "block";
            option.nextElementSibling.style.display = "block";
        }
        else {
            option.style.display = "none";
            option.nextElementSibling.style.display = "none";
        }
    })
    if (flag === 0) {
        document.querySelector(".dropdown-menu-main .no-elem").style.display = "block";
    }

}

var open = false;
dropdown_menu.addEventListener("click", (e) => {
    e.stopPropagation();
})
dropdown.addEventListener("click", (e) => {
    e.stopPropagation();
    open = !open;
    if (open) {
        dropdownarrow.style.transform = "rotate(180deg)";
        dropdown_menu.style.display = "flex";
        document.querySelector(".dropdown .title").innerText = "Select Location";
        document.querySelector(".dropdown-menu-main").scrollIntoView();
    }
    else {
        dropdownarrow.style.transform = "rotate(0deg)";
        dropdown_menu.style.display = "none";
        make_array_of_checked();
        if (selected.size > 0) {
            document.querySelector(".dropdown .title").innerText = "";
            selected.forEach((each_selected) => {
                make_spans(each_selected.getAttribute("name"));
            })
        }


    }

})

function open_side_location() {
    if (document.getElementById("myCheckState").checked) {
        document.querySelector(".state-wrapper").style.display = "block";
    }
    if (document.getElementById("myCheckCity").checked) {
        document.querySelector(".city-wrapper").style.display = "block";
    }
    if (document.getElementById("myCheckPincode").checked) {
        document.querySelector(".pincode-wrapper").style.display = "block";
    }
    if (!document.getElementById("myCheckState").checked) {
        document.querySelector(".state-wrapper").style.display = "none";
    }
    if (!document.getElementById("myCheckCity").checked) {
        document.querySelector(".city-wrapper").style.display = "none";
    }
    if (!document.getElementById("myCheckPincode").checked) {
        document.querySelector(".pincode-wrapper").style.display = "none";
    }
}
function close_current_drop_down() {
    if (open) {
        open = !open;
        dropdownarrow.style.transform = "rotate(0deg)";
        dropdown_menu.style.display = "none";
        make_array_of_checked();
        if (selected.size > 0) {
            document.querySelector(".dropdown .title").innerText = "";
            selected.forEach((each_selected) => {
                make_spans(each_selected.getAttribute("name"));
            })
        }
    }
    open_side_location();
}
document.addEventListener("click", () => {
    if (open) {
        open = !open;
        dropdownarrow.style.transform = "rotate(0deg)";
        dropdown_menu.style.display = "none";
        make_array_of_checked();
        if (selected.size > 0) {
            document.querySelector(".dropdown .title").innerText = "";
            selected.forEach((each_selected) => {
                make_spans(each_selected.getAttribute("name"));
            })
        }
    }
})
document.querySelector(".state").addEventListener("click", () => {
    document.querySelector(".state").style.backgroundColor = "#0254D7";
    document.querySelector(".city").style.backgroundColor = "white";
    document.querySelector(".pincode").style.backgroundColor = "white";
    document.querySelector("#myCheckState").previousElementSibling.style.color = "#fff";
    document.querySelector("#myCheckCity").previousElementSibling.style.color = "black";
    document.querySelector("#myCheckPincode").previousElementSibling.style.color = "black";
    document.querySelector("#myCheckCity").checked = false;
    document.querySelector("#myCheckPincode").checked = false;
    document.querySelector("#location-dropdown-div .dropdown-wrapper-main .dropdown .title").innerHTML = "State";
    if (document.getElementById("myCheckState").checked) {
        close_current_drop_down();
    }

})
document.querySelector(".city").addEventListener("click", () => {
    document.querySelector(".city").style.backgroundColor = "#0254D7";
    document.querySelector(".state").style.backgroundColor = "white";
    document.querySelector(".pincode").style.backgroundColor = "white";
    document.querySelector("#myCheckState").previousElementSibling.style.color = "black";
    document.querySelector("#myCheckCity").previousElementSibling.style.color = "#fff";
    document.querySelector("#myCheckPincode").previousElementSibling.style.color = "black";
    document.querySelector("#myCheckState").checked = false;
    document.querySelector("#myCheckPincode").checked = false;
    document.querySelector("#location-dropdown-div .dropdown-wrapper-main .dropdown .title").innerHTML = "City";
    if (document.getElementById("myCheckCity").checked) {
        close_current_drop_down();
    }
})
document.querySelector(".pincode").addEventListener("click", () => {
    document.querySelector(".pincode").style.backgroundColor = "#0254D7";
    document.querySelector(".city").style.backgroundColor = "white";
    document.querySelector(".state").style.backgroundColor = "white";
    document.querySelector("#myCheckState").previousElementSibling.style.color = "black";
    document.querySelector("#myCheckCity").previousElementSibling.style.color = "black";
    document.querySelector("#myCheckPincode").previousElementSibling.style.color = "#fff";
    document.querySelector("#myCheckCity").checked = false;
    document.querySelector("#myCheckState").checked = false;
    document.querySelector("#location-dropdown-div .dropdown-wrapper-main .dropdown .title").innerHTML = "Pincode";
    if (document.getElementById("myCheckPincode").checked) {
        close_current_drop_down();
    }
})

function make_array_of_checked() {
    all_check_boxes.forEach((each_check_box) => {
        if (each_check_box.checked)
            selected.add(each_check_box);
        else
            selected.delete(each_check_box);
    })
}

function make_spans(text) {
    var span = document.createElement("SPAN");
    span.innerHTML = `<span>${document.getElementById('myCheck' + text).previousElementSibling.innerHTML}</span>`;
    span.classList.add("category-tag", `${text}`);
    document.querySelector(".dropdown .title").appendChild(span);
}


///Select location by state


const options_list_state = document.querySelectorAll(".dropdown-menu-state .option");
document.querySelector(".search-box-state").addEventListener("keyup", function (e) {
    filter_list_state(e.target.value);
});

function filter_list_state(search_term) {
    search_term = search_term.toLowerCase();
    let flag = 0;
    document.querySelector(".dropdown-menu-state .no-elem").style.display = "none";
    options_list_state.forEach(option => {
        let label = option.firstElementChild.firstElementChild.nextElementSibling.innerText.toLowerCase();
        if (label.indexOf(search_term) != -1) {
            flag = 1;
            option.style.display = "block";
            option.nextElementSibling.style.display = "block";
        }
        else {
            option.style.display = "none";
            option.nextElementSibling.style.display = "none";
        }
    })
    if (flag === 0)
        document.querySelector(".dropdown-menu-state .no-elem").style.display = "block";
}

const dropdownarrow_state = document.querySelector(".state-wrapper .dropdown svg");
const dropdown_state = document.querySelector(".state-wrapper .dropdown");
const dropdown_menu_state = document.querySelector(".state-wrapper .dropdown-menu");
const all_check_boxes_state = document.querySelectorAll(".item-checkbox-state");
const selected_state = new Set();
var open_state = false;
dropdown_menu_state.addEventListener("click", (e) => {
    e.stopPropagation();
})
dropdown_state.addEventListener("click", (e) => {

    e.stopPropagation();
    open_state = !open_state;
    if (open_state) {
        dropdownarrow_state.style.transform = "rotate(180deg)";
        dropdown_menu_state.style.display = "flex";
        document.querySelector(".state-wrapper .dropdown .title").innerText = "Select State";
        document.querySelector(".dropdown-menu-state").scrollIntoView();
    }
    else {
        dropdownarrow_state.style.transform = "rotate(0deg)";
        dropdown_menu_state.style.display = "none";
        make_array_of_checked_state();
        if (selected_state.size > 0) {
            document.querySelector(".state-wrapper .dropdown .title").innerText = "";
            selected_state.forEach((each_selected) => {
                make_spans_state(each_selected.getAttribute("name"));
            })
        }


    }

})

document.addEventListener("click", () => {
    if (open_state) {
        open_state = !open_state;
        dropdownarrow_state.style.transform = "rotate(0deg)";
        dropdown_menu_state.style.display = "none";
        make_array_of_checked_state();
        if (selected_state.size > 0) {
            document.querySelector(".state-wrapper .dropdown .title").innerText = "";
            selected_state.forEach((each_selected) => {
                make_spans_state(each_selected.getAttribute("name"));
            })
        }
    }
})
function apply_cross_state() {
    document.querySelectorAll(".cross-btn-state").forEach((each_cross_btn) => {
        each_cross_btn.addEventListener("click", (e) => {
            e.stopPropagation();
            if (document.querySelector(`.${e.target.name}`))
                document.querySelector(`.${e.target.name}`).remove();
            selected_state.delete(document.getElementById(`myCheck${e.target.name}`));
            document.getElementById(`myCheck${e.target.name}`).checked = false;
            if (selected_state.size === 0)
                document.querySelector(".state-wrapper .dropdown .title").innerHTML = "Select State";

        })
    });
}

function make_array_of_checked_state() {
    all_check_boxes_state.forEach((each_check_box) => {
        if (each_check_box.checked)
            selected_state.add(each_check_box);
        else
            selected_state.delete(each_check_box);
    })
}

function make_spans_state(text) {
    var span = document.createElement("SPAN");
    span.innerHTML = `<span>${document.getElementById('myCheck' + text).previousElementSibling.innerHTML}</span><img class='cross-btn cross-btn-state' name='${text}' src='/static/EasyChatApp/img/cross-mh.svg' alt='cross' />`;
    span.classList.add("category-tag-each", `${text.split(" ").join("_")}`);
    document.querySelector(".state-wrapper .dropdown .title").appendChild(span);
    apply_cross_state();
}



//Filter by city


const options_list_city = document.querySelectorAll(".dropdown-menu-city .option");
document.querySelector(".search-box-city").addEventListener("keyup", function (e) {
    filter_list_city(e.target.value);
});

function filter_list_city(search_term) {
    search_term = search_term.toLowerCase();
    let flag = 0;
    document.querySelector(".dropdown-menu-city .no-elem").style.display = "none";
    options_list_city.forEach(option => {
        let label = option.firstElementChild.firstElementChild.nextElementSibling.innerText.toLowerCase();
        if (label.indexOf(search_term) != -1) {
            flag = 1;
            option.style.display = "block";
            option.nextElementSibling.style.display = "block";
        }
        else {
            option.style.display = "none";
            option.nextElementSibling.style.display = "none";
        }
    })
    if (flag === 0)
        document.querySelector(".dropdown-menu-city .no-elem").style.display = "block";
}

const dropdownarrow_city = document.querySelector(".city-wrapper .dropdown svg");
const dropdown_city = document.querySelector(".city-wrapper .dropdown");
const dropdown_menu_city = document.querySelector(".city-wrapper .dropdown-menu");
const all_check_boxes_city = document.querySelectorAll(".item-checkbox-city");
const selected_city = new Set();
var open_city = false;
dropdown_menu_city.addEventListener("click", (e) => {
    e.stopPropagation();
})
dropdown_city.addEventListener("click", (e) => {

    e.stopPropagation();
    open_city = !open_city;
    if (open_city) {
        dropdownarrow_city.style.transform = "rotate(180deg)";
        dropdown_menu_city.style.display = "flex";
        document.querySelector(".city-wrapper .dropdown .title").innerText = "Select City";
        document.querySelector(".dropdown-menu-city").scrollIntoView();
    }
    else {
        dropdownarrow_city.style.transform = "rotate(0deg)";
        dropdown_menu_city.style.display = "none";
        make_array_of_checked_city();
        if (selected_city.size > 0) {
            document.querySelector(".city-wrapper .dropdown .title").innerText = "";
            selected_city.forEach((each_selected) => {
                make_spans_city(each_selected.getAttribute("name"));
            })
        }


    }

})

document.addEventListener("click", () => {
    if (open_city) {
        open_city = !open_city;
        dropdownarrow_city.style.transform = "rotate(0deg)";
        dropdown_menu_city.style.display = "none";
        make_array_of_checked_city();
        if (selected_city.size > 0) {
            document.querySelector(".city-wrapper .dropdown .title").innerText = "";
            selected_city.forEach((each_selected) => {
                make_spans_city(each_selected.getAttribute("name"));
            })
        }
    }
})
function apply_cross_city() {
    document.querySelectorAll(".cross-btn-city").forEach((each_cross_btn) => {
        each_cross_btn.addEventListener("click", (e) => {
            e.stopPropagation();
            if (document.querySelector(`.${e.target.name}`))
                document.querySelector(`.${e.target.name}`).remove();
            selected_city.delete(document.getElementById(`myCheck${e.target.name}`));
            document.getElementById(`myCheck${e.target.name}`).checked = false;
            if (selected_city.size === 0)
                document.querySelector(".city-wrapper .dropdown .title").innerHTML = "Select City";

        })
    });
}

function make_array_of_checked_city() {
    all_check_boxes_city.forEach((each_check_box) => {
        if (each_check_box.checked)
            selected_city.add(each_check_box);
        else
            selected_city.delete(each_check_box);
    })
}

function make_spans_city(text) {
    var span = document.createElement("SPAN");
    span.innerHTML = `<span>${document.getElementById('myCheck' + text).previousElementSibling.innerHTML}</span><img class='cross-btn cross-btn-city' name='${text}' src='/static/EasyChatApp/img/cross-mh.svg' alt='cross' />`;
    span.classList.add("category-tag-each", `${text.split(" ").join("_")}`);
    document.querySelector(".city-wrapper .dropdown .title").appendChild(span);
    apply_cross_city();
}



///Filter by pincode

const options_list_pincode = document.querySelectorAll(".dropdown-menu-pincode .option");
document.querySelector(".search-box-pincode").addEventListener("keyup", function (e) {
    filter_list_pincode(e.target.value);
});

function filter_list_pincode(search_term) {
    search_term = search_term.toLowerCase();
    let flag = 0;
    document.querySelector(".dropdown-menu-pincode .no-elem").style.display = "none";
    options_list_pincode.forEach(option => {
        let label = option.firstElementChild.firstElementChild.nextElementSibling.innerText.toLowerCase();
        if (label.indexOf(search_term) != -1) {
            flag = 1;
            option.style.display = "block";
            option.nextElementSibling.style.display = "block";
        }
        else {
            option.style.display = "none";
            option.nextElementSibling.style.display = "none";
        }
    })
    if (flag === 0)
        document.querySelector(".dropdown-menu-pincode .no-elem").style.display = "block";
}

const dropdownarrow_pincode = document.querySelector(".pincode-wrapper .dropdown svg");
const dropdown_pincode = document.querySelector(".pincode-wrapper .dropdown");
const dropdown_menu_pincode = document.querySelector(".pincode-wrapper .dropdown-menu");
const all_check_boxes_pincode = document.querySelectorAll(".item-checkbox-pincode");
const selected_pincode = new Set();
var open_pincode = false;
dropdown_menu_pincode.addEventListener("click", (e) => {
    e.stopPropagation();
})
dropdown_pincode.addEventListener("click", (e) => {

    e.stopPropagation();
    open_pincode = !open_pincode;
    if (open_pincode) {
        dropdownarrow_pincode.style.transform = "rotate(180deg)";
        dropdown_menu_pincode.style.display = "flex";
        document.querySelector(".pincode-wrapper .dropdown .title").innerText = "Select Pincode";
        document.querySelector(".dropdown-menu-pincode").scrollIntoView();
    }
    else {
        dropdownarrow_pincode.style.transform = "rotate(0deg)";
        dropdown_menu_pincode.style.display = "none";
        make_array_of_checked_pincode();
        if (selected_pincode.size > 0) {
            document.querySelector(".pincode-wrapper .dropdown .title").innerText = "";
            selected_pincode.forEach((each_selected) => {
                make_spans_pincode(each_selected.getAttribute("name"));
            })
        }


    }

})

document.addEventListener("click", () => {
    if (open_pincode) {
        open_pincode = !open_pincode;
        dropdownarrow_pincode.style.transform = "rotate(0deg)";
        dropdown_menu_pincode.style.display = "none";
        make_array_of_checked_pincode();
        if (selected_pincode.size > 0) {
            document.querySelector(".pincode-wrapper .dropdown .title").innerText = "";
            selected_pincode.forEach((each_selected) => {
                make_spans_pincode(each_selected.getAttribute("name"));
            })
        }
    }
})
function apply_cross_pincode() {
    document.querySelectorAll(".cross-btn-pincode").forEach((each_cross_btn) => {
        each_cross_btn.addEventListener("click", (e) => {
            e.stopPropagation();
            if (document.querySelector(`.pin${e.target.name}`))
                document.querySelector(`.pin${e.target.name}`).remove();
            selected_pincode.delete(document.getElementById(`myCheck${e.target.name}`));
            document.getElementById(`myCheck${e.target.name}`).checked = false;
            if (selected_pincode.size === 0)
                document.querySelector(".pincode-wrapper .dropdown .title").innerHTML = "Select Pincode";

        })
    });
}

function make_array_of_checked_pincode() {
    all_check_boxes_pincode.forEach((each_check_box) => {
        if (each_check_box.checked)
            selected_pincode.add(each_check_box);
        else
            selected_pincode.delete(each_check_box);
    })
}

function make_spans_pincode(text) {
    var span = document.createElement("SPAN");
    span.innerHTML = `<span>${document.getElementById('myCheck' + text).previousElementSibling.innerHTML}</span><img class='cross-btn cross-btn-pincode' name='${text}' src='/static/EasyChatApp/img/cross-mh.svg' alt='cross' />`;
    span.classList.add("category-tag-each", `pin${text}`);
    document.querySelector(".pincode-wrapper .dropdown .title").appendChild(span);
    apply_cross_pincode();
}

function compare_message_history_dates(start_date, end_date) {
    // function will return true if start_date <= end_date
    // MM/DD/YYYY format
    var start_date_day = start_date.split("/")[1];
    var start_date_month = start_date.split("/")[0];
    var start_date_year = start_date.split("/")[2];
    var end_date_day = end_date.split("/")[1];
    var end_date_month = end_date.split("/")[0];
    var end_date_year = end_date.split("/")[2];

    if (end_date_year < start_date_year) {
        return false;
    } else if (end_date_year == start_date_year) {
        if (end_date_month < start_date_month) {
            return false;
        } else if (end_date_month == start_date_month) {
            if (end_date_day < start_date_day) {
                return false;
            }
        }
    }
    return true;
}

function compare_message_history_datetime(start_date, end_date, start_time, end_time) {
    // function will return true if start_date_time <= end_date_time
    var start_date_day = start_date.split("/")[1];
    var start_date_month = start_date.split("/")[0];
    var start_date_year = start_date.split("/")[2];
    var end_date_day = end_date.split("/")[1];
    var end_date_month = end_date.split("/")[0];
    var end_date_year = end_date.split("/")[2];

    var start_time_ap = start_time.split(" ")[3];
    var end_time_ap = end_time.split(" ")[3];
    var start_time_hr = start_time.split(" ")[0];
    var end_time_hr = end_time.split(" ")[0];
    var start_time_min = start_time.split(" ")[2];
    var end_time_min = end_time.split(" ")[2];

    if (end_date_year < start_date_year) {
        return false;
    } else if (end_date_year == start_date_year) {
        if (end_date_month < start_date_month) {
            return false;
        } else if (end_date_month == start_date_month) {
            if (end_date_day < start_date_day) {
                return false;
            } else if (end_date_day == start_date_day) {
                if (end_time_ap == "AM" && start_time_ap == "PM") {
                    return false;
                } else if (end_time_ap == start_time_ap) {
                    if (end_time_hr < start_time_hr) {
                        return false;
                    } else if (end_time_hr == start_time_hr) {
                        if (end_time_min < start_time_min) {
                            return false;
                        }
                    }
                }
            }
        }
    }
    return true;
}

$('#easychat_message_history_table_row_dropdown').on('change', function() {
    //Check for no_of_records_per_page
    var url_params = get_url_vars();
    delete url_params["no_of_records_per_page"];

    var no_of_records_per_page = this.value
    if (no_of_records_per_page != "") {
        url_params["no_of_records_per_page"] = no_of_records_per_page;
    }

    redirect_to_url_based_params(url_params);
});

function apply_message_history_filter() {
    var url_params = get_url_vars();
    
    //Check query type
    delete url_params["query_type"];

    var selected_query_type_elem = $('input[name="analytics-card-filter-btn"]:checked');

    if (selected_query_type_elem && selected_query_type_elem.length > 0) {
        url_params["query_type"] = selected_query_type_elem.val();
    }
    
    //Check feedback type
    delete url_params["feedback_type"];
    
    var selected_feedback_elem = $('input[name="analytics-card-feedback-filter-btn"]:checked');
    if (selected_feedback_elem && selected_feedback_elem.length > 0) {
        url_params["feedback_type"] = selected_feedback_elem.val();
    }
    
    //Check for channels selected
    delete url_params["channels"];

    var selected_channels = get_selected_channels('message-history');
    if (selected_channels != "") {
        url_params["channels"] = selected_channels;
    }

    //Check for no_of_records_per_page
    delete url_params["no_of_records_per_page"];

    var no_of_records_per_page = $('#easychat_message_history_table_row_dropdown').find(":selected").text();
    if (no_of_records_per_page != "") {
        url_params["no_of_records_per_page"] = no_of_records_per_page;
    }

    //Check for intent_id
    delete url_params["intent_pk"];

    var intent_id = $('#easychat_message_history_select_intent_dropdown').find(":selected").val();
    if (intent_id != "" && intent_id != "none") {
        url_params["intent_pk"] = intent_id;
    }

    //Check for percentage
    delete url_params["low_percent"];
    delete url_params["high_percent"];

    if (is_percentage_match_enabled == "True")
    {
        var low_percent_value = low_percent
        var high_percent_value = high_percent

        if (intent_id != "" && (low_percent != "" || high_percent != "")) {
            url_params["low_percent"] = low_percent_value;
            url_params["high_percent"] = high_percent_value;

        }
    }

    //Check sentiment
    delete url_params["sentiment"];

    var selected_sentiment_elem = $('input[name="analytics-card-sentiment-filter-btn"]:checked');
    if (selected_sentiment_elem && selected_sentiment_elem.length > 0) {
        url_params["sentiment"] = selected_sentiment_elem.val();
    }

    //Check timestamp type
    delete url_params["filter_type"];
    delete url_params["start_date"];
    delete url_params["end_date"];

    var selected_date_filter_elem = $('input[name="analytics-card-timestamp-filter-btn"]:checked');
    if (selected_date_filter_elem && selected_date_filter_elem.length > 0) {
        url_params["filter_type"] = selected_date_filter_elem.val();
    }

    if (url_params["filter_type"] && url_params["filter_type"] == '5') {
        //Date and time validation
        var today = new Date();
        var today = String(today.getMonth() + 1).padStart(2, '0') + '/' + String(today.getDate()).padStart(2, '0') + '/' + today.getFullYear();
        
        var from_date = document.getElementById("datepicker-1-0").value;
        var end_date = document.getElementById("datepicker-1-1").value;
        
        var from_time = document.getElementById("time-picker-btn-1-0").value;
        var end_time = document.getElementById("time-picker-btn-1-1").value;
        
        if (Date.parse(from_date) > Date.parse(today)) {
            showToast("From date cannot be greater than today's date.");
            return;
        }

        if (Date.parse(end_date) > Date.parse(today)) {
            showToast("To date cannot be greater than today's date");
            return;
        }

        if (!compare_message_history_datetime(from_date, end_date, from_time, end_time)) {
            showToast("From timestamp cannot be greater than to timestamp.");
            return;
        }

        url_params["start_date"] = from_date + "_" + from_time.split(" ").join("");
        url_params["end_date"] = end_date + "_" + end_time.split(" ").join("");
    }

    //Check filter by location
    delete url_params["location_state"];
    delete url_params["location_city"];
    delete url_params["location_pincode"];
    var state_list = "";
    var city_list = "";
    var pincode_list = "";
    if (document.getElementById("myCheckState").checked) {
        var states = document.getElementsByClassName("item-checkbox-state");
        for (var i = 0; i < states.length; i++) {
            if (states[i].checked) {
                if (state_list != "") {
                    state_list += "+";
                }
                state_list += states[i].getAttribute("name").split(" ").join("_");
            }
        }
        if (state_list != "") {
            url_params["location_state"] = state_list
        }
    } else if (document.getElementById("myCheckCity").checked) {
        var cities = document.getElementsByClassName("item-checkbox-city");
        for (var i = 0; i < cities.length; i++) {
            if (cities[i].checked) {
                if (city_list != "") {
                    city_list += "+";
                }
                city_list += cities[i].getAttribute("name").split(" ").join("_");
            }
        }
        if (city_list != "") {
            url_params["location_city"] = city_list;
        }
    } else if (document.getElementById("myCheckPincode").checked) {
        var pincodes = document.getElementsByClassName("item-checkbox-pincode");
        for (var i = 0; i < pincodes.length; i++) {
            if (pincodes[i].checked) {
                if (pincode_list != "") {
                    pincode_list += "+";
                }
                pincode_list += pincodes[i].getAttribute("name");
            }
        }
        if (pincode_list != "") {
            url_params["location_pincode"] = pincode_list;
        }
    }

    redirect_to_url_based_params(url_params);
}

function redirect_to_url_based_params(url_params) {
    var redirect_url = "?";
    for (var param in url_params) {
        if (redirect_url != "?") {
            redirect_url += "&"
        }
        redirect_url += param + "=" + url_params[param];
    }

    window.location = redirect_url;   
}


$(document).ready(function () {
    var url_params = get_url_vars();
    if (url_params["location_state"] != null && url_params["location_state"] != undefined) {
        var selected_states = url_params["location_state"].split("+");
        var state_checkboxes_dropdown = document.getElementsByClassName("dropdown-menu-state")[0];
        for (var i = 0; i < selected_states.length; i++) {
            state_checkboxes_dropdown.querySelector('[name="' + selected_states[i].split("_").join(" ") + '"]').checked = true;
        }
        dropdown_state.click();
        document.getElementById("myCheckState").checked = true;
        document.getElementById("state").click();
    } else if (url_params["location_city"] != null && url_params["location_city"] != undefined) {
        var selected_cities = url_params["location_city"].split("+");
        var city_checkboxes_dropdown = document.getElementsByClassName("dropdown-menu-city")[0];
        for (var i = 0; i < selected_cities.length; i++) {
            city_checkboxes_dropdown.querySelector('[name="' + selected_cities[i].split("_").join(" ") + '"]').checked = true;
        }
        dropdown_city.click();
        document.getElementById("myCheckCity").checked = true;
        document.getElementById("city").click();
    } else if (url_params["location_pincode"] != null && url_params["location_pincode"] != undefined) {
        var selected_pincodes = url_params["location_pincode"].split("+");
        var pincode_checkboxes_dropdown = document.getElementsByClassName("dropdown-menu-pincode")[0];
        for (var i = 0; i < selected_pincodes.length; i++) {
            pincode_checkboxes_dropdown.querySelector('[name="' + selected_pincodes[i] + '"]').checked = true;
        }
        dropdown_pincode.click();
        document.getElementById("myCheckPincode").checked = true;
        document.getElementById("pincode").click();
    }
    changed_date('1-0', 'Double datetime', null);
    changed_date('1-1', 'Double datetime', null);
    show_custom_date();

});

function refresh_timestamp() {
    var today = new Date();
    var today = String(today.getMonth() + 1).padStart(2, '0') + '/' + String(today.getDate()).padStart(2, '0') + '/' + today.getFullYear();
    document.getElementById("datepicker-1-0").value = today;
    document.getElementById("datepicker-1-1").value = today;
    changed_date('1-0', 'Double datetime', null);
    changed_date('1-1', 'Double datetime', null);
    document.getElementById("time-picker-btn-1-0").value = "12 : 00 AM";
    document.getElementById("time-picker-btn-1-1").value = "11 : 59 PM";
    document.getElementById("ui-datepicker-div").style.display = "none";
    close_time_modal('1-0');
    close_time_modal('1-1');
}


function add_intents_to_filter(bot_id, intent_pk) {

    chosen_bot_id = bot_id;
  
    $.ajax({
        url: '/fetch-intents-of-bot-selected/',
        type: "POST",
        headers: {
            "X-CSRFToken": get_csrf_token()
        },
        data: {
            'bot_pk': chosen_bot_id,
        },
        success: function(response) {
            if (response["status"] == 200) {
                intents = response["intents"];
                intent_list = '';
                intent_list += "<option value= none selected> Select Intent </option>";
                for (var i = 0; i < intents.length; i++) {
                    intent_list += "<option value=" + intents[i]['pk'] + ">" + intents[i]["name"] + "</option>";
                }
                document.getElementById("easychat_message_history_select_intent_dropdown").innerHTML = intent_list;
                if(intent_pk)
                $("#easychat_message_history_select_intent_dropdown").val(intent_pk);
            }
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        }
    });

}

$(document).on("change", ".selected-misdashboard", function(e) {

    selected_misdashboard_list = document.getElementsByClassName("selected-misdashboard");

    show_add_next_round_button = false;
    for (var i = 0; i < selected_misdashboard_list.length; i++) {
        id = selected_misdashboard_list[i];
        if (id.checked == true) {
            show_add_next_round_button = true;
            break;
        }
    }

    if (show_add_next_round_button == true) {
        $(".ms-false-positive-btn-wrapper").show();
    } else {
        $(".ms-false-positive-btn-wrapper").hide();
    }
});


function mark_flagged_queries(flagged_queries_type) {

    var bot_id = get_url_vars()["bot_id"];
    var message_history_pk_list = [];

    var message_history_checkboxes = document.getElementsByClassName("selected-misdashboard");

    for (var i=0; i<message_history_checkboxes.length; i++) {
        if (message_history_checkboxes[i].checked) {
            message_history_pk_list.push(message_history_checkboxes[i].id.split("input-checkbox-selected-misdashboard-")[1].trim());
        }
    }

    if (message_history_pk_list.length == 0) {
        M.toast({
            "html": "Please select valid the message history set."
        }, 2000);
        return;
    }

    var json_string = {
        "bot_id": bot_id,
        "flagged_queries_type": flagged_queries_type,
        "message_history_pk_list": message_history_pk_list
    }

    var json_string = JSON.stringify(json_string);
  
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);
    encrypted_data = {
        "json_string": encrypted_data
    };
    var params = 'json_string=' + json_string

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/chat/mark-flagged-queries/", true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status"] == 200) {

                var success_toast = "Successfully marked the flagged queries as ";
                if (flagged_queries_type == "1") {
                    success_toast += "False Positives."
                } else {
                    success_toast += "Not False Positives."
                }

                M.toast({
                    "html": success_toast
                }, 2000);
                setTimeout(function(){
                    window.location.reload();
                }, 2000);
            } else if (response["status"] == 300) {
                M.toast({
                    "html": response["message"]
                }, 2000);
                setTimeout(function(){
                    window.location.reload();
                }, 2000);
            } else {
                M.toast({
                    "html": response["message"]
                }, 2000);
            }
        }
    }
    xhttp.send(params);
}

function pagination_handler(page_number) {
    let filters = get_url_multiple_params();
    filters.page = [page_number];
    let key_value = "";
    for (var filter_key in filters) {
        let filter_data = filters[filter_key];
        for (var index = 0; index < filter_data.length; index++) {
            key_value += filter_key + "=" + filter_data[index] + "&";
        }
    }
    let new_url = window.location.protocol + "//" + window.location.host + window.location.pathname + '?' + key_value;
    window.location.href = new_url;
}

function get_url_multiple_params() {
    let url_vars = {};
    let parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function (m, key, value) {
        if (!(key in url_vars)) {
            url_vars[key] = [];
        }
        url_vars[key].push(value);
    });
    return url_vars;
}

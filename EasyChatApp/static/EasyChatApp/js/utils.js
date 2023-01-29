function create_custom_category_dropdown() {
    $("#easychat-filter-intent-category-select-div .easychat-console-select-drop").each(function(i, select) {
        if (!$(this).next().hasClass('easychat-dropdown-select-custom')) {
            $(this).after('<div class="easychat-dropdown-select-custom wide ' + ($(this).attr('class') || '') + '" tabindex="0"><span id="category-current-select" class="current"></span><div class="list"><ul></ul></div></div>');
            var dropdown = $(this).next();

            var options = $(select).find('span');

            var selected = $(this).find('easychat-console-language-option:selected');

            dropdown.find('#category-current-select.current').html(selected.data('display-text') || selected.text());
            options.each(function(j, o) {

                var display = $(o).data('display-text') || '';
                dropdown.find('ul').append('<li class="easychat-console-language-option ' + ($(o).is(':selected') ? 'selected' : '') + '" data-value="' + $(o).data("value") + '" data-display-text="' + display + '">' + $(o).text() + '</li>');
            });
        }
        
        $("#easychat-filter-intent-category-select-div ul li:eq(" + window.selected_category_index + ")").addClass('easychat-lang-selected');

    });

    $('#easychat-filter-intent-category-select-div .easychat-dropdown-select-custom ul').before('<div class="dd-search"> <svg class="drop-language-search-icon" width="15" height="14" viewBox="0 0 15 14" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M13.1875 12.0689L9.88352 8.76489C10.6775 7.81172 11.0734 6.58914 10.9889 5.35148C10.9045 4.11382 10.3461 2.95638 9.42994 2.11993C8.51381 1.28349 7.31047 0.83244 6.07025 0.86062C4.83003 0.8888 3.64842 1.39404 2.77123 2.27123C1.89404 3.14842 1.3888 4.33003 1.36062 5.57025C1.33244 6.81047 1.78349 8.01381 2.61993 8.92994C3.45638 9.84607 4.61382 10.4045 5.85148 10.4889C7.08914 10.5734 8.31172 10.1775 9.26489 9.38352L12.5689 12.6875L13.1875 12.0689ZM2.25002 5.68752C2.25002 4.90876 2.48095 4.14748 2.91361 3.49996C3.34627 2.85244 3.96122 2.34776 4.6807 2.04974C5.40019 1.75172 6.19189 1.67375 6.95569 1.82568C7.71949 1.97761 8.42108 2.35262 8.97175 2.90329C9.52242 3.45396 9.89743 4.15555 10.0494 4.91935C10.2013 5.68315 10.1233 6.47485 9.8253 7.19433C9.52728 7.91382 9.0226 8.52877 8.37508 8.96143C7.72756 9.39409 6.96628 9.62502 6.18752 9.62502C5.14358 9.62386 4.14274 9.20865 3.40457 8.47047C2.66639 7.7323 2.25118 6.73145 2.25002 5.68752Z" fill="#909090"/></svg><input id="txtSearchValueCategory" autocomplete="off" placeholder="Search Categories" onkeyup="filter_category()" class="dd-searchbox" type="text"></div>');


    $('#easychat-filter-intent-category-select-div .easychat-dropdown-select-custom ul li:last').after('<div class="custom-drop-nodata-found-div">No result found</div> ');

    var selected_category_name = $("#easychat-filter-intent-category-select-div ul .easychat-lang-selected").html();
    
    $('#category-current-select').html(selected_category_name);

}

//function select_option_for_category() {
 $(document).on('click', '#easychat-filter-intent-category-select-div .easychat-dropdown-select-custom .easychat-console-language-option', function(event) {

     $(this).closest('.list').find('.easychat-lang-selected').removeClass('easychat-lang-selected');
     $(this).addClass('easychat-lang-selected');

     var text = $(this).data('display-text') || $(this).text();
     $(this).closest('.easychat-dropdown-select-custom').find('#category-current-select').text(text);
     $(this).closest('.easychat-dropdown-select-custom').prev('select').val($(this).data('value')).trigger('change');

     //update_form_widget(event, this)
 });
//}

function filter_category() {
    var valThis = $('#txtSearchValueCategory').val();
    $('#easychat-filter-intent-category-select-div .easychat-dropdown-select-custom ul > li').each(function() {
        var text = $(this).text();
        (text.toLowerCase().indexOf(valThis.toLowerCase()) > -1) ? $(this).show(): $(this).hide();

        if ($('#easychat-filter-intent-category-select-div .easychat-dropdown-select-custom ul').children(':visible').not('#easychat-filter-intent-category-select-div .custom-drop-nodata-found-div').length === 0) {
            $('#easychat-filter-intent-category-select-div .custom-drop-nodata-found-div').show();
        } else {
            $('#easychat-filter-intent-category-select-div .custom-drop-nodata-found-div').hide();
        }

    });
};
$(document).ready(function() {
    create_custom_category_dropdown();
});

// /////////////////// auto fix and ignore start//////////////////////////////////////
function auto_fix_changes_in_non_primary_languages(bot_id, channel_name){
    json_string = {
        bot_id: bot_id,
        channel_name:channel_name,
    }
    json_string = JSON.stringify(json_string);
    json_string = EncryptVariable(json_string);
    $("#channel-language-auto-fix-pop-up-div").hide()
    document.getElementById("language-loader-inner-text").innerText= "Auto Fixing Languages"
    $("#modal-language-change-loader").modal('open')

    $.ajax({
        url: "/chat/auto-fix-changes-in-non-primary-languages/",
        type: "POST",
        data: {
            json_string: json_string
        },
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                console.log("languages auto fixed succesfully")
                $("#modal-language-change-loader").modal('close')
                M.toast({
                    "html": "Languages auto fixed Succesfully!"
                }, 2000)

                document.getElementById("language-loader-inner-text").innerText= "Loading Languages"
            } else if (response["status"] == 400) {
                $("#modal-language-change-loader").modal('close')
                M.toast({
                    "html": response["message"]
                }, 2000)
                document.getElementById("language-loader-inner-text").innerText= "Loading Languages"
            } else {
                $("#modal-language-change-loader").modal('close')
                M.toast({
                    "html": "Something went wrong, Please refresh and try again"
                })
                document.getElementById("language-loader-inner-text").innerText= "Loading Languages"
            }
        },
        error: function(error) {
            console.log("Report this error: ", error);
        },
    });
}
function ignore_changes_in_non_primary_languages(bot_id ,channel_name){
    json_string = {
        bot_id: bot_id,
        channel_name:channel_name,
    }
    json_string = JSON.stringify(json_string);
    json_string = EncryptVariable(json_string);
    $("#channel-language-auto-fix-pop-up-div").hide()
    $("#easychat_channel_language_update_preloader").show()
   
    $.ajax({
        url: "/chat/ignore-changes-in-non-primary-languages/",
        type: "POST",
        data: {
            json_string: json_string
        },
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                $("#easychat_channel_language_update_preloader").hide()
            } else if (response["status"] == 400) {
                M.toast({
                    "html": response["message"]
                }, 2000)
                $("#easychat_channel_language_update_preloader").hide()
            } else {
                M.toast({
                    "html": "Something went wrong, Please refresh and try again"
                })
                $("#easychat_channel_language_update_preloader").hide()
            }
        },
        error: function(error) {
            document.getElementById("easychat_web_channel_preloader").style.display = "none";
            console.log("Report this error: ", error);
        },
    });
}
///////////////////////////////////////////////////// auto fix and ignore end for channels//////////////////////////////
///////////////////////////////////////////////////// auto fix and ignore start for Intents//////////////////////////////

function auto_fix_bot_response_changes_in_non_primary_languages(){
    json_string = {
        tree_pk: auto_fix_selected_tree_pk
    }
    json_string = JSON.stringify(json_string);
    json_string = EncryptVariable(json_string);
    $("#autofix_div").hide()
    document.getElementById("language-loader-inner-text").innerText= "Auto Fixing Languages"
    $("#modal-language-change-loader").modal('open')

    $.ajax({
        url: "/chat/auto-fix-bot-response-changes-in-non-primary-languages/",
        type: "POST",
        data: {
            json_string: json_string
        },
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                
                $("#modal-language-change-loader").modal('close')
                if (document.getElementById("intent-language-auto-fix-pop-up-div-old")) {
                    document.getElementById("intent-language-auto-fix-pop-up-div-old").style.display = "none";
                }
                M.toast({
                    "html": "Languages auto fixed Succesfully!"
                }, 2000)

                document.getElementById("language-loader-inner-text").innerText= "Loading Intent"
            } else if (response["status"] == 400) {
                $("#modal-language-change-loader").modal('close')
                M.toast({
                    "html": response["message"]
                }, 2000)
                document.getElementById("language-loader-inner-text").innerText= "Loading Intent"
            } else {
                $("#modal-language-change-loader").modal('close')
                M.toast({
                    "html": "Something went wrong, Please refresh and try again"
                })
                document.getElementById("language-loader-inner-text").innerText= "Loading Intent"
            }
        },
        error: function(error) {
            console.log("Report this error: ", error);
        },
    });
}
function ignore_bot_response_changes_in_non_primary_languages(){
    json_string = {
        tree_pk: auto_fix_selected_tree_pk
    }
    json_string = JSON.stringify(json_string);
    json_string = EncryptVariable(json_string);
    $("#autofix_div").hide()
    
   
    $.ajax({
        url: "/chat/ignore-bot-response-changes-in-non-primary-languages/",
        type: "POST",
        data: {
            json_string: json_string
        },
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                console.log("Language fine tuning changes ignored succesfully")
                if (document.getElementById("intent-language-auto-fix-pop-up-div-old")) {
                    document.getElementById("intent-language-auto-fix-pop-up-div-old").style.display = "none";
                }
            } else if (response["status"] == 400) {
                M.toast({
                    "html": response["message"]
                }, 2000)
            } else {
                M.toast({
                    "html": "Something went wrong, Please refresh and try again"
                })
            }
        },
        error: function(error) {
            document.getElementById("easychat_web_channel_preloader").style.display = "none";
            console.log("Report this error: ", error);
        },
    });
}



///////////////////////////////////////////////////// auto fix and ignore end for intents//////////////////////////////
///////////////////////////////////////////////////// auto fix and ignore start for bot configuration //////////////////////////////
function auto_fix_bot_configuration_changes_in_non_primary_languages(bot_id){
    json_string = {
        bot_id: bot_id,
    }
    json_string = JSON.stringify(json_string);
    json_string = EncryptVariable(json_string);

    $("#modal-language-change-loader .modal-content #language-loader-inner-text").html("Auto Fixing Languages") 
    $("#modal-language-change-loader").modal('open')

    $.ajax({
        url: "/chat/auto-fix-bot-configuration-changes-in-non-primary-languages/",
        type: "POST",
        data: {
            json_string: json_string
        },
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                
                $("#modal-language-change-loader").modal('close')
                M.toast({
                    "html": "Languages auto fixed Succesfully!"
                }, 2000)

                document.getElementById("language-loader-inner-text").innerText= "Loading Languages"
            } else if (response["status"] == 400) {
                $("#modal-language-change-loader").modal('close')
                M.toast({
                    "html": response["message"]
                }, 2000)
                document.getElementById("language-loader-inner-text").innerText= "Loading Languages"
            } else {
                $("#modal-language-change-loader").modal('close')
                M.toast({
                    "html": "Something went wrong, Please refresh and try again"
                })
                document.getElementById("language-loader-inner-text").innerText= "Loading Languages"
            }
        },
        error: function(error) {
            console.log("Report this error: ", error);
        },
    });
}
function ignore_bot_configuration_changes_in_non_primary_languages(bot_id){
    json_string = {
        bot_id: bot_id
    }
    json_string = JSON.stringify(json_string);
    json_string = EncryptVariable(json_string);
    
    $.ajax({
        url: "/chat/ignore-bot-configuration-changes-in-non-primary-languages/",
        type: "POST",
        data: {
            json_string: json_string
        },
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                // for debugging
                console.log("Language fine tuning changes ignored succesfully")
            } else if (response["status"] == 400) {
                M.toast({
                    "html": response["message"]
                }, 2000)
            } else {
                M.toast({
                    "html": "Something went wrong, Please refresh and try again"
                })
            }
        },
        error: function(error) {
            console.log("Report this error: ", error);
        },
    });
}
// ////////////////////////////////// auto -fix ignore ends for bot configuration //////////////////////////////////////

function update_url_with_filters(filters) {
    let key_value = "";
    for (var filter_key in filters) {
        let filter_data = filters[filter_key];
        for (var index = 0; index < filter_data.length; index++) {
            key_value += filter_key + "=" + filter_data[index] + "&";
        }
    }
    let new_url = window.location.protocol + "//" + window.location.host + window.location.pathname + '?' + key_value;
    return new_url
}

function get_url_multiple_vars() {
    let url_vars = {};
    window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function (m, key, value) {
        if (!(key in url_vars)) {
            url_vars[key] = [];
        }
        url_vars[key].push(strip_unwanted_characters(value));
    });
    return url_vars;
}

function get_url_link_for_a_partcular_page_no(page_no){

    let url_vars = get_url_multiple_vars();
    url_vars.page = [page_no];
    new_url = update_url_with_filters(url_vars)
    return new_url
}

function get_url_with_a_parameter_and_its_value(parameter_value, parameter_string){

    let url_vars = get_url_multiple_vars();
    url_vars[parameter_string] = [parameter_value];
    new_url = update_url_with_filters(url_vars)
    return new_url
}

function get_particular_page_html(page_no,display){
    return `<li><a href="` + get_url_link_for_a_partcular_page_no(page_no) + `"> ` + display + `</a></li>`
}

function apply_pagination_data(pagination_data, pagnition_container){

    let data_entries_html = '<div class="dataTables_info" id="data-model-table_info">Showing ' + pagination_data.start_point + ' to ' + pagination_data.end_point + ' of ' + pagination_data.total_count + ' entries</div>'

    let paginator_html = `<ul class="pagination">`

    if(pagination_data.has_other_pages){
        let current_page_no = pagination_data.number
        let prev_page_no = current_page_no - 1
        let next_page_no = current_page_no + 1
        let total_number_of_pages = pagination_data.num_pages
        if(pagination_data.has_previous){
            let last_page_url = get_url_link_for_a_partcular_page_no(prev_page_no)
            paginator_html += `<li class="next-btn">
                <a href="` + last_page_url + `">
                    Previous
                </a>
            </li>`

        }else{
            // disable krna hai yha pe previous button
            paginator_html += `<li class="disabled previous-btn">Previous</li>`
        }
        let html_for_prev_pages = ""
        let html_for_curent_page = `<li class="active purple darken-3"><a href="`+ get_url_link_for_a_partcular_page_no(current_page_no) +`">` + current_page_no + `</a></li>`
        let html_for_pages_after_curr_page = ""
        
        let start_page_no = 1
        if(current_page_no > 5){
            html_for_prev_pages += get_particular_page_html(current_page_no-5 ,"...")
            start_page_no = current_page_no-4
        }

        for(let i=start_page_no; i<current_page_no;i++){
            html_for_prev_pages += get_particular_page_html(i ,i)
        }
                    
        let end_page_no = total_number_of_pages
        let html_for_end_page = ""
        if(total_number_of_pages - current_page_no > 5){
            end_page_no = current_page_no + 4
            html_for_end_page = get_particular_page_html(current_page_no+5 ,"...")
        }

        for(let i=current_page_no+1; i<=end_page_no;i++){
            html_for_pages_after_curr_page += get_particular_page_html(i ,i)
        }

        html_for_pages_after_curr_page += html_for_end_page

        paginator_html += html_for_prev_pages + html_for_curent_page + html_for_pages_after_curr_page

        if(pagination_data.has_next){

            let next_page_url = get_url_link_for_a_partcular_page_no(next_page_no)
            paginator_html += `<li class="next-btn">
                <a href="` + next_page_url + `">
                    Next
                </a>
            </li>`
        }else{
            paginator_html += `<li class="disabled next-btn">Next</li>`
        }
    }
    
    paginator_html += '</ul>'
    pagnition_container.innerHTML = data_entries_html + paginator_html
}

function search_from_data_model_table() {
    
    var input = document.getElementById("data-model-search-bar");
    var filter = input.value.toUpperCase();
    var table = document.getElementById("data-model-table");
    var trs = table.tBodies[0].getElementsByTagName("tr");

    let tr_counter = trs.length;

    $("#data-model-table tbody tr").each((indx, ele) => {
        let key_text = $(ele).children().eq(1).text().toUpperCase()
        // We skip searching in value of attached_file_src because it is very big and causes page to become unresponsive
        if (key_text.indexOf("ATTACHED_FILE_SRC") > -1) {
            if (("ATTACHED_FILE_SRC").indexOf(filter) > -1) {
                $(ele).show();
                tr_counter--;
            } else {
                $(ele).hide();
            }
            return true;
        }
        let element_text = $(ele).text().toUpperCase();
        if (element_text.indexOf(filter) > -1) {
            $(ele).show();
            tr_counter--;
        } else {
            $(ele).hide();
        }
    })

    if(tr_counter == trs.length) {
        document.getElementById("data_model_no_data_found").style.display = "block";
        document.getElementById("data-model-table").style.display = "none";
        document.getElementById("datatable-info-pagination-div").style.display = "none";
        
    }
    else {
        document.getElementById("data_model_no_data_found").style.display = "none";
        document.getElementById("data-model-table").style.display = "table";
        document.getElementById("datatable-info-pagination-div").style.display = "flex";
    }
}

function handle_no_of_records_to_show(){
    let no_of_records = document.getElementById("easychat-data-table-length-select").value
    window.location.href = get_url_with_a_parameter_and_its_value(no_of_records, "no_of_records_per_page")
}

if (window.location.href.indexOf("/chat/data-model-entries/") != -1) {
	
	$(document).ready(function() {
		setTimeout(function(){
            $("#easychat-data-table-length-select").select2({ 
		    dropdownCssClass : "easychat-datatable-option-container" 
	    	});

			$("#data-model-userid-filter").select2({
				dropdownCssClass : "select-user-id-field-dropdown",
				placeholder: 'Filter by User ID ',
			})
			.on("select2:open", function () {
			$("#page-filter-modal").removeAttr("tabindex");
			$('input.select2-search__field').attr('placeholder', 'Search User ID');
			})
        
			$("#data-model-variable-filter").select2({
				dropdownCssClass : "select-user-id-field-dropdown",
				placeholder: 'Filter by Variable ',
			})
			.on("select2:open", function () {
			$("#page-filter-modal").removeAttr("tabindex");
			$('input.select2-search__field').attr('placeholder', 'Search Variable');
			})

        }, 0)

		const pagination_data = JSON.parse(window.pagination_metadata)
		let paginator_container = document.getElementById("datatable-info-pagination-div")

		apply_pagination_data(pagination_data, paginator_container)
        let url_vars = get_url_multiple_vars();

        if("no_of_records_per_page" in url_vars){
            let no_of_records_per_page = url_vars["no_of_records_per_page"][0]
            $("#easychat-data-table-length-select").val(no_of_records_per_page)
        }
	});
}

function check_and_update_whatsapp_history_filter_data(){
    let url_vars = get_url_multiple_vars();
    if("no_of_records_per_page" in url_vars){
        let no_of_records_per_page = url_vars["no_of_records_per_page"][0]
        $("#easychat-data-table-length-select").val(no_of_records_per_page)
    }
    if("bot_id" in url_vars){
        let bot_id_value = url_vars["bot_id"][0]
        $('#select-whatsapp-bot-filter').val(bot_id_value)
    }   
    if("mobile" in url_vars){
        let mobile_value = url_vars["mobile"][0]
        $("#filter-whatsapp-number").val(mobile_value)
    }
    if("received_date" in url_vars){
        let received_date_value = url_vars["received_date"][0]
        $("#whatsapp-filter-date").val(received_date_value)
    }
    
}


if (window.location.href.indexOf("/chat/whatsapp-history/") != -1) {

    $(document).ready(function() {
        const pagination_metadata = JSON.parse(window.pagination_metadata)
        let paginator_container = document.getElementById("datatable-info-pagination-div")
        apply_pagination_data(pagination_metadata, paginator_container)
        check_and_update_whatsapp_history_filter_data()
    });
}


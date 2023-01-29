

var automated_testing_result_filter_user_choice = "0";
var is_last_update_test_progress_call_completed = true;

var RESET_ICON_SVG = '<svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">\
<path d="M2.39999 4.19998C2.06862 4.19998 1.79999 3.93135 1.79999 3.59998V1.19998C1.79999 0.868605 2.06862 0.599976 2.39999 0.599976C2.73136 0.599976 2.99999 0.868605 2.99999 \
1.19998L2.99999 2.26275C4.07933 1.3506 5.47578 0.799976 6.99999 0.799976C10.4242 0.799976 13.2 3.57581 13.2 6.99998C13.2 10.4241 10.4242 13.2 6.99999 13.2C3.57582 13.2 0.799988 10.4241 0.799988 6.99998C0.799988 6.69984 0.821358 6.40435 0.862744 6.11502C0.884117 5.9656 0.910823 5.81785 0.942668 5.672C1.01335 5.34825 1.33309 5.1431 \
1.65684 5.21378C1.98058 5.28447 2.18573 5.60421 2.11505 5.92796C2.08941 6.04542 2.06789 6.16446 2.05065 6.28493C2.01729 6.51816 1.99999 6.75687 1.99999 6.99998C1.99999 9.7614 4.23856 12 6.99999 12C9.76141 12 12 9.7614 12 6.99998C12 4.23855 9.76141 1.99998 6.99999 1.99998C5.87391 1.99998 4.83537 2.37172 3.9994 2.99998H4.79999C5.13136 2.99998 5.39999 3.2686 5.39999 3.59998C5.39999 3.93135 5.13136 4.19998 4.79999 4.19998H2.39999Z" fill="#334155"/>\
</svg>'

// 0 -> both passed and failed
// 1 -> passed
// 2 -> failed
// Following couple functions render the result of automated testing by backend calling it every so often
if (window.location.pathname.indexOf("/chat/test-chatbot/") != -1) {

    renderAutomatedTestingResult();

    var selected_bot_id = get_url_vars()["bot_pk"];

    automated_testing_started = localStorage.getItem('automated_testing_started-' + selected_bot_id) == undefined ? 'false' : localStorage.getItem('automated_testing_started-' + selected_bot_id);

    TOTAL_SENTENCES = localStorage.getItem('automated_testing_total_sentences_for_id_' + selected_bot_id) == undefined ? TOTAL_SENTENCES : localStorage.getItem('automated_testing_total_sentences_for_id_' + selected_bot_id);

    automated_test_progress = setInterval(function() {
        if(is_last_update_test_progress_call_completed){
        
        update_automated_test_progress(selected_bot_id);
        }
    }, 2000)

    update_start_and_stop_testing_buttons();
}

function update_start_and_stop_testing_buttons(){

    if(automated_testing_started == "true"){

        $("#stop-automated-testing-modal-open-btn").show();
        $("#start-automated-testing-modal-open-btn").hide();
        disable_automated_testing_export_and_filter_buttons();
        $(".automated_testing_status_reset_svg_container").css("pointer-events","none")
    }else{

        $("#start-automated-testing-modal-open-btn").show();
        $("#stop-automated-testing-modal-open-btn").hide();
        enable_automated_testing_export_and_filter_buttons();
        $(".automated_testing_status_reset_svg_container").css("pointer-events","unset")
    }
}

function get_automated_testing_filter_value(){

    if(document.getElementById("automated-testing-status-all").checked){
        return "0";
    }
    else if(document.getElementById("automated-testing-status-pass").checked){
        return "1";
    }

    return "2";
}

function clear_automated_testing_filters(){
    document.getElementById("automated-testing-status-all").checked = true
    renderAutomatedTestingResult("0")
}

function apply_filter_automated_testing() {

    automated_testing_result_filter_user_choice = get_automated_testing_filter_value();

    renderAutomatedTestingResult(automated_testing_result_filter_user_choice);
}

function renderAutomatedTestingResult(filter_type="0") {

    $("#automated_testing_results_loader").show()
    $("#automated_testing_results_table_body").html("")

    var selected_bot_id = get_url_vars()["bot_pk"];

    var json_string = JSON.stringify({
        selected_bot_id: selected_bot_id,
        filter_type: filter_type,
    });

    $.ajax({
        url: "/chat/get-automated-testing-result/",
        type: "GET",
        data: {
            json_string: json_string
        },
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            var html_table = `<div class="center-align" style="padding:1em;">No test results available. Please click on Start Bot Testing first.</div>`

            $("#automated_testing_results_loader").hide()
            $("#automated_testing_live_count").html("")
            if (response["status"] == 200) {

                test_results_details = response["test_results_details"]
                host = window.location.host;
                correct_sentences_length = response['correct_sentences']
                total_sentences_length = response['total_sentences']
            
                update_accuracy_of_automation_testing(correct_sentences_length, total_sentences_length)

                if (test_results_details.length == 0) {

                    $("#automated_testing_results_no_data_found").show()

                } else {
                    
                    $("#automated_testing_result_date").html("Last Tested On : " + response['result_timestamp'])

                    if(automated_testing_started != "true"){

                        TOTAL_SENTENCES = total_sentences_length
                    }

                    let html_table = get_table_body_html(test_results_details)

                    $("#automated_testing_results_no_data_found").hide()
                    $("#automated_testing_results_table_body").html("")
                    $("#automated_testing_results_table_body").html(html_table);
                    
                }
            }else{

                $("#automated_testing_results_no_data_found").show()
                $("#automated_testing_results_loader").hide()
            }

        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
            $("#automated_testing_results_loader").hide()
        }
    });

}

function get_edit_intent_page_link_html(intent_pk, intent_name){

    let html = "<a target='_blank' href='/chat/edit-intent/?intent_pk=" + intent_pk + "&selected_language=en'>" + intent_name + "</a>"

    return html
}

function get_edit_intent_page_link_html_for_list_of_intents(intent_pk_list, intent_name_list){
    
    html = ""

    for(let i = 0; i < intent_pk_list.length; i++){

        intent_name = intent_name_list[i]
        intent_pk = intent_pk_list[i]
        html += get_edit_intent_page_link_html(intent_pk, intent_name)

        if(i != intent_pk_list.length -1){
            html += "<br>"
        }
    }

    if(html == ""){
        html = "None"
    }

    return html
}

function get_table_body_html(test_result_details){
    
    let html_table = ""

    for (var i = 0; i < test_result_details.length; i++) {

        orignal_intent_pk = test_result_details[i]['original_intent_pk']
        orignal_intent_name = test_result_details[i]['original_intent_name']
        test_result_obj_pk = test_result_details[i]['test_result_obj_pk']
        orignal_intent = get_edit_intent_page_link_html(orignal_intent_pk, orignal_intent_name)

        identified_intent_name_list = test_result_details[i]["identified_intent_name_list"]
        identified_intent_pk_list = test_result_details[i]["identified_intent_pk_list"]

        identified_intents = get_edit_intent_page_link_html_for_list_of_intents(identified_intent_pk_list, identified_intent_name_list)
        
        html_table += `<tr>
            <td>` + test_result_details[i]["query_sentence"] + `</td>
            <td>` + orignal_intent + `</td>
            <td id='automated_test_identified_intent_` + test_result_obj_pk+ `' >` + identified_intents + `</td>
            <td id='automated_test_status_` + test_result_obj_pk+ `' >` + get_test_result_status_html(test_result_details[i]["status"], test_result_obj_pk)+ `</td>
            <td id='automated_test_cause_` + test_result_obj_pk+ `' >` + test_result_details[i]["cause"] + `</td>
            </tr>`;

    }

    return html_table
}

function get_test_result_status_html(status, test_result_obj_pk){
    html = "<div class='automated_testing_status_wrapper'><div class='automated_testing_status_" + status + "_text'>" + status + " </div><div data-toggle='tooltip' title='Re-run' class='automated_testing_status_reset_svg_container' onclick='re_run_test_case_for_particular_sentence(`"+ test_result_obj_pk +"`)'>" + RESET_ICON_SVG + "</div>"
    return html
}

$(document).on("click", "#start-automated-testing-btn", function(e) {

    selected_bot_id = get_url_vars()["bot_pk"];

    if (selected_bot_id != undefined && selected_bot_id != null) {

        startAutomatedTesting(selected_bot_id);

        $("#automated_testing_results_table_body").html("")

        $("#automated_testing_results_loader").show()
        $("#automated_testing_results_no_data_found").hide()
        reset_accuracy_text()
        document.getElementById("automated-testing-status-all").checked = true;
    }

});

function reset_accuracy_text(){

    $('#test-percent').html("0")
    $('#test-final-result').html("0/0")
    $("#result-paragraph").show()
}

$(document).on("click", "#stop-automated-testing-btn", function(e) {

    selected_bot_id = get_url_vars()["bot_pk"];

    if (selected_bot_id != undefined && selected_bot_id != null) {

        stop_automated_testing(selected_bot_id);
        
    }

});

function stop_automated_testing(selected_bot_id){

    
    var json_string = JSON.stringify({
        selected_bot_id: selected_bot_id,
    })
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: "/chat/stop-automated-testing/",
        type: "POST",
        data: {
            json_string: json_string
        },
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            
            if (response["status"] == 200) {

                M.toast({
                    "html": "Automation Testing Stopped In Between"
                }, 1000);

                update_details_for_end_of_automation_testing(selected_bot_id);
                setTimeout(function(){
                    renderAutomatedTestingResult();
                }, 1000)
                
            }
            if(response["status"] == 300){
                console.log("Testing was stopped already")
                update_details_for_end_of_automation_testing(selected_bot_id);
                setTimeout(function(){
                    renderAutomatedTestingResult();
                }, 1000)
            }

            $("#preloader_automation_testing_div").hide();
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        }
    });

}

function update_details_for_end_of_automation_testing(selected_bot_id){

    automated_testing_started = 'false';

    localStorage.setItem('automated_testing_started-' + selected_bot_id, false);

    localStorage.setItem('automated_testing_total_sentences_for_id_' + selected_bot_id, TOTAL_SENTENCES);

    update_start_and_stop_testing_buttons();
    clearInterval(automated_test_progress);

}

function export_automated_testing_excel(){

    selected_bot_id = get_url_vars()["bot_pk"];

    email_id = document.getElementById("export-data-email-automated-testing-report").value 
   
    if(!validate_email(email_id)){

        M.toast({"html": 'Please enter valid Email address'}, 4000, "rounded");
        return
    }
    var json_string = JSON.stringify({
        selected_bot_id: selected_bot_id,
        email_id: email_id
    })
    json_string = EncryptVariable(json_string);
    $.ajax({

        url: "/chat/export-automated-testing-excel/",
        type: "POST",
        data: {
            json_string: json_string
        },
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);

            if (response["status"] == 200) {
                M.toast({
                    "html": "Your request for Automated Testing Report has been processed and will be sent on the Email ID provided"
                }, 1000);
            } 
            if(response["status"] == 400 ){
                M.toast({
                    "html": response["status_message"]
                }, 1000);
            }
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
            M.toast({
                "html": "Unable to export automated testing. Kindly try again later."
            }, 1000);
        }
    });

}



function update_automated_test_progress(selected_bot_id) {

    is_last_update_test_progress_call_completed = false

    var json_string = JSON.stringify({
        selected_bot_id: selected_bot_id,
    })
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: "/chat/get-automated-test-progress/",
        type: "POST",
        data: {
            json_string: json_string
        },
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {

                is_last_update_test_progress_call_completed = true

                var test_results_details = response["test_results_details"]

                var test_cases_processed = response["test_cases_processed"];
                var test_cases_passed = response["test_cases_passed"]
                var is_automated_testing_completed = response["is_automated_testing_completed"];
                var is_excel_created = response["is_excel_created"];

                if (is_automated_testing_completed && automated_testing_started == 'false') {

                    clearInterval(automated_test_progress);
                    
                } else {
                   
                    html_body = get_table_body_html(test_results_details)


                    document.getElementById("automated_testing_live_count").innerHTML = "(" + test_cases_processed + " out of " + TOTAL_SENTENCES + ")"

                    document.getElementById("automated_testing_results_table_body").innerHTML += html_body

                    $(".automated_testing_status_reset_svg_container").css("pointer-events","none")

                    test_cases_passed = parseInt(test_cases_passed);

                    if (test_cases_passed == NaN || test_cases_passed == undefined) {

                        test_cases_passed = 0;
                    }

                    update_accuracy_of_automation_testing(test_cases_passed, test_cases_processed)

                    if (is_automated_testing_completed) {

                        $(".automated_testing_status_reset_svg_container").css("pointer-events","unset")

                            update_details_for_end_of_automation_testing(selected_bot_id)

                            setTimeout(function() {

                                renderAutomatedTestingResult();

                            }, 2000);

                    }
                }

            } else {

                M.toast({
                    "html": "Unable to start automated testing. Kindly try again later."
                }, 1000);

                is_last_update_test_progress_call_completed = true
            }
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
            M.toast({
                "html": "Unable to start automated testing. Kindly try again later."
            }, 1000);
            is_last_update_test_progress_call_completed = true
        }
    });
}

function update_re_runed_test_result_details_in_html(test_result_details, test_result_obj_pk){

    let test_status = test_result_details[0]["status"]
    let test_cause = test_result_details[0]["cause"]
    let status_html = get_test_result_status_html(test_status, test_result_obj_pk) 

    identified_intent_name_list = test_result_details[0]["identified_intent_name_list"]
    identified_intent_pk_list = test_result_details[0]["identified_intent_pk_list"]

    identified_intents = get_edit_intent_page_link_html_for_list_of_intents(identified_intent_pk_list, identified_intent_name_list)
        
    $("#automated_test_status_"+ test_result_obj_pk).html(status_html)
    $("#automated_test_cause_"+ test_result_obj_pk).html(test_cause)
    $("#automated_test_identified_intent_"+ test_result_obj_pk).html(identified_intents)

}

function update_accuracy_of_automation_testing(test_cases_passed, test_cases_processed){

    $("#result-paragraph").css("display", "block");

    $('#test-final-result').html(test_cases_passed + '/' + test_cases_processed);

    var pass_percent = ((test_cases_passed * 100) / parseInt(test_cases_processed)).toFixed(2);

    if(pass_percent == 'NaN'){
        pass_percent = 0;
    }

    $('#test-percent').html(pass_percent);

}

function re_run_test_case_for_particular_sentence(test_result_obj_pk){
    
    disable_automated_testing_export_and_filter_buttons();

    $("#automated_test_status_"+ test_result_obj_pk).html("Running ...")

    var selected_bot_id = get_url_vars()["bot_pk"];

    var json_string = JSON.stringify({
        selected_bot_id: selected_bot_id,
        test_result_obj_pk: test_result_obj_pk,
    })

    json_string = EncryptVariable(json_string);

    $.ajax({
        url: "/chat/re-run-automation-testing-for-single-sentence/",
        type: "POST",
        data: {
            json_string: json_string
        },
        success: function(response) {

            response = custom_decrypt(response)
            response = JSON.parse(response);

            if (response["status"] == 200) {

               test_result_details = response["test_result_details"]
               test_cases_passed = response["test_cases_passed"]
               update_re_runed_test_result_details_in_html(test_result_details, test_result_obj_pk)

               update_accuracy_of_automation_testing(test_cases_passed, TOTAL_SENTENCES)

            } else {

              M.toast({
                "html": "Unable to start automated testing. Kindly try again later."
                }, 1000);
                let status_html = get_test_result_status_html("Retry", test_result_obj_pk) 

                $("#automated_test_status_"+ test_result_obj_pk).html(status_html)
            }
            enable_automated_testing_export_and_filter_buttons();
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
            M.toast({
                "html": "Unable to start automated testing. Kindly try again later."
            }, 1000);
            enable_automated_testing_export_and_filter_buttons();
        }
    });
}

function startAutomatedTesting(selected_bot_id) {

    automated_testing_started = 'true';

    localStorage.setItem('automated_testing_started-' + selected_bot_id, true);

    update_start_and_stop_testing_buttons()

    percentage_of_intents = $('input[name="automated_testing_batch_size"]:checked').val()

    var json_string = JSON.stringify({
        selected_bot_id: selected_bot_id,
        percentage_of_intents: percentage_of_intents,
    })

    json_string = EncryptVariable(json_string);

    response = $.ajax({
        url: "/chat/automated-testing/",
        type: "POST",
        data: {
            json_string: json_string
        },
        success: function(response) {

            response = custom_decrypt(response)
            response = JSON.parse(response);

            $("#preloader_automation_testing_div").hide();

            if (response["status"] == 200) {

                document.getElementById('automated-test-percent').innerHTML = 'starting...';

                TOTAL_SENTENCES = response["total_sentences"]
                localStorage.setItem('automated_testing_total_sentences_for_id_' + selected_bot_id, TOTAL_SENTENCES);

                automated_test_progress = setInterval(function() {
                    if(is_last_update_test_progress_call_completed){
                        update_automated_test_progress(selected_bot_id);
                    }
                }, 2000)

                M.toast({
                    "html": "Automated testing started."
                }, 1000);

            } else {

                M.toast({
                    "html": "Unable to start automated testing. Kindly try again later."
                }, 1000);

                $("#automated-test-progress-bar").hide();
            }
        },
        error: function(xhr, textstatus, errorthrown) {
            $("#automated-test-progress-bar").hide();
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
            M.toast({
                "html": "Unable to start automated testing. Kindly try again later."
            }, 1000);
        }
    }).responseJSON;
}


function disable_automated_testing_export_and_filter_buttons(){
    document.getElementById("export_automated_testing_excel").style.pointerEvents = "none";
    document.getElementById("trigger_automated_testing_filter_modal").style.pointerEvents = "none";
}

function enable_automated_testing_export_and_filter_buttons(){
    document.getElementById("export_automated_testing_excel").style.pointerEvents = "unset";
    document.getElementById("trigger_automated_testing_filter_modal").style.pointerEvents = "unset";
}
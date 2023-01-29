/////////// Extract FAQs

var is_faq_extraction_in_progress = false;

$(document).ready(function() {
    is_faq_extraction_in_progress = true;
    disable_user_inputs();
    track_extract_faq_progress();
    extraction_timer = setInterval(track_extract_faq_progress, 5000);
    extraction_toast_timer = setInterval(function () {
        showToast("FAQ Extraction is taking longer than expected. Please wait.")
    }, 30000)
})

function disable_user_inputs() { 
    document.getElementById("extract_faq_btn").classList.add("disabled");
    document.getElementById("export_table_faqs_btn").classList.add("disabled");
    document.getElementById("button-intent-creat-with-extract-faqs-bot").classList.add("disabled");
    document.getElementById("url_html_id").disabled = true;
}

function enable_user_inputs() {
    document.getElementById("extract_faq_btn").classList.remove("disabled");
    document.getElementById("export_table_faqs_btn").classList.remove("disabled");
    document.getElementById("button-intent-creat-with-extract-faqs-bot").classList.remove("disabled");
    document.getElementById("url_html_id").disabled = false;
}

function enable_extract_faqs() {
    // adding this in set time out of 100 miliseconds because on paste the url_html input field was receving empty value
    setTimeout(function() {
        var url_html = $("#url_html_id").val();
        url_html = url_html.trim();

        if (isValidURL(url_html) == false || is_faq_extraction_in_progress) {

            document.getElementById("extract_faq_btn").classList.add("disabled");
        } else {

            document.getElementById("extract_faq_btn").classList.remove("disabled");
        }
    }, 100);
}

function start_extract_faqs(event) {

    if (!event.shiftKey) {
        if (event.keyCode == 13 || event.which == 13) {
            $("#extract_faq_btn").click();
        }
    }
}

function isExternal(url) {
   var domain = (new URL(url));
   domain = domain.hostname;
   
   if (domain === 'localhost' || domain === '[::1]' || domain.match(/^127(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$/))
   {
        return false;
   }
   else {
    return true;
   }
}

$("#extract_faq_btn").click(function() {
    if (is_faq_extraction_in_progress) {
        showToast("FAQ Extraction is already in process!", 2000);
        return;
    }
    var url_html = $("#url_html_id").val();
    url_html = url_html.trim();
    if (url_html == "") {
        showToast("Kindly enter a URL to start extracting FAQs", 2000);
        return;
    }
    if (isValidURL(url_html) == false) {
        showToast("URL/Links added must consist of HTTP/HTTPS, Eg. https://www.google.com.", 2000);
        return;
    }

    if (!isExternal(url_html)) {
        showToast("Internal urls are not allowed.", 2000);
        return;
    }

    $("#processing").show();
    var json_string = JSON.stringify({
        url_html: url_html,
        bot_pk: get_url_vars()["bot_pk"],
    })
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: "/chat/fetch-faqs/",
        type: "POST",
        headers: {
            'X-CSRFToken': get_csrf_token(),
        },
        data: {
            json_string: json_string
        },
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if(response["status"] == 200) {
                is_faq_extraction_in_progress = true;
                disable_user_inputs();
                extraction_timer = setInterval(track_extract_faq_progress, 5000);
                extraction_toast_timer = setInterval(function () {
                    showToast("FAQ Extraction is taking longer than expected. Please wait.")
                }, 30000)

            }  else {
                is_faq_extraction_in_progress = false;
                enable_user_inputs();
                $("#processing").hide();
                showToast("Unable to extract FAQ. Please try after some time.", 2000);
            }
        },
        error: function(jqXHR, exception) {
            $("#processing").hide();
            is_faq_extraction_in_progress = false;
            enable_user_inputs();
            showToast("Unable to connect to server. Please try again later.", 2000);
            console.log(jqXHR, exception); //For debugging purpose
        },
    });
});


function export_faqs(questions, answers) {
    $.ajax({
        url: "/chat/export-faqs/",
        type: "POST",
        data: {
            questions: EncryptVariable(JSON.stringify(questions)),
            answers: EncryptVariable(JSON.stringify(answers))
        },
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            console.log("Successfully exported FAQs!", response);
            var file_url = response["file_url"];
            window.open(file_url);
        },
        error: function(jqXHR, exception) {},
    });
}

$("#export_table_faqs_btn").click(function() {


    var table = document.getElementById("faq_table");
    var questions = [];
    var answers = [];
    for (var i = 1, row; row = table.rows[i]; i++) {
        var question = table.rows[i].cells[0].textContent;
        // question = question.substr(0, question.length - "delete".length);
        var answer = table.rows[i].cells[1].textContent;
        questions.push(question);
        answers.push(answer);
        // i += 2;
    }

    export_faqs(questions, answers);

});

// make intent from extracted faqs


function send_faqs_to_server_to_make_intent(questions, answers, bot_pk) {

    $("#button-intent-creat-with-extract-faqs-bot").addClass("disabled");

    $.ajax({
        url: "/chat/create-intent-from-faqs/",
        type: "POST",
        data: {
            questions: EncryptVariable(JSON.stringify(questions)),
            answers: EncryptVariable(JSON.stringify(answers)),
            bot_pk: EncryptVariable(JSON.stringify(bot_pk))
        },

        success: function(response) {
            $("#processing").hide();
            response = custom_decrypt(response)
            response = JSON.parse(response);
            console.log("Request sent to create intent!", response);
            M.toast({
                html: response['message']
            });
            $("#button-intent-creat-with-extract-faqs-bot").removeClass("disabled");
        },
        error: function(jqXHR, exception) {
            $("#processing").hide();
            console.log("Request failed to create intent!", response);
            M.toast({
                html: response['message']
            });
            $("#button-intent-creat-with-extract-faqs-bot").removeClass("disabled");
        },
    });
}

$("#button-intent-creat-with-extract-faqs-bot").click(function() {
    var url_parameters = get_url_vars()
    if (url_parameters["bot_pk"] == undefined || url_parameters["bot_pk"] == null) {
        M.toast({
            html: "Something went wrong. Please retry again."
        });
        return;
        
    }
    var bot_pk = url_parameters["bot_pk"]

    if (bot_pk == "0") {
        M.toast({
            html: "Please select at least one bot."
        });
        return;
    }

    var table = document.getElementById("faq_table");

    if (table.rows.length <= 1) {
        M.toast({
            html: "Please add at least one faq."
        });
        return;
    }

    $("#processing").show();
    var questions = [];
    var answers = [];
    for (var i = 1; i < table.rows.length; i++) {
        var question = table.rows[i].cells[0].innerText;
        var answer = table.rows[i].cells[1].innerHTML;
        questions.push(question);
        answers.push(answer);
    }

    send_faqs_to_server_to_make_intent(questions, answers, bot_pk);

});


$(document).on('click', '.delete_question', function() {
    // $(this).parent().parent().next().next().remove();
    // $(this).parent().parent().next().remove();
    $(this).parent().parent().remove();
});

function track_extract_faq_progress() {

    var json_string = JSON.stringify({
        bot_id: get_url_vars()["bot_pk"],
        event_type: 'faq_extraction',
    })

    json_string = EncryptVariable(json_string)
    $.ajax({
        url: "/chat/bot/track-event-progress/",
        type: "POST",
        headers: {
            'X-CSRFToken': get_csrf_token()
        },
        data: {
            data: json_string,
        },
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);

            if (response.status == 200) {
                let is_completed = response.is_completed;
                let is_toast_displayed = response.is_toast_displayed;
                let is_failed = response.is_failed;
                let event_info = response.event_info;
                let failed_message = response.failed_message;
                $("#processing").show();
                if (is_failed && !is_toast_displayed) {
                    $("#processing").hide();
                    is_faq_extraction_in_progress = false;
                    if (failed_message == '') failed_message = 'FAQ Extraction Failed'
                    showToast("FAQ Extraction Failed", 2000);
                    enable_user_inputs();
                } else if (is_completed && !is_toast_displayed) {
                    is_faq_extraction_in_progress = false;
                    $("#processing").hide();
                    let url_html = $("#url_html_id").val();
                    url_html = url_html.trim();
                    if (url_html.length > 500) {
                        $('#url_html_id').val('');
                    }
                    $('#url_html_id').innerHeight(10)
                    let faqs = event_info;
                    let html_string = "<table id='faq_table'>";
                    if (faqs.length > 2) {
                        html_string += "<th style='width:40%'>Question</th><th style='width:50%'>Answer</th><th style='width:10%'>Options</th>"
                        for (var i = 0; i < faqs.length; i++) {
                            if (faqs[i]["question"].trim() != "") {
                                faqs[i]["answer"] = faqs[i]["answer"].replace(new RegExp('\r?<p>--&gt;', 'g'), "");
                                html_string += "<tr><td contenteditable='true' style='width:40%'>" + faqs[i]["question"] + "</td>"
                                html_string += "<td contenteditable='true' style='width:50%'>" + faqs[i]["answer"] + "</td>"
                                html_string += "<td style='width:10%'><a class='delete_question' ><i class='material-icons red-text text-darken-3'>delete</i></a></td></tr>"
                            }
                        }
                    } else {
    
                        showToast("Provided URL does not have enough data.", 2000);
                        $('#url_html_id').val('');
                    }
                    html_string += "</table>"
                    $("#table_div").html(html_string);
                    $("#export_table_faqs_btn").removeClass("disabled");
                    $("#button-intent-creat-with-extract-faqs-bot").removeClass("disabled");
                    if (extraction_toast_timer) {
                        clearInterval(extraction_toast_timer);
                    }
                    if (extraction_timer) { 
                        clearInterval(extraction_timer);
                    }
                    enable_user_inputs();
                } else if (is_completed && is_toast_displayed){
                    $("#processing").hide();
                    is_faq_extraction_in_progress = false;
                    if (extraction_toast_timer) {
                        clearInterval(extraction_toast_timer);
                    }
                    if (extraction_timer) { 
                        clearInterval(extraction_timer);
                    }
                    enable_user_inputs();
                }
            } else {
                $("#processing").hide();
                is_faq_extraction_in_progress = false;
                if (extraction_toast_timer) {
                    clearInterval(extraction_toast_timer);
                }
                if (extraction_timer) { 
                    clearInterval(extraction_timer);
                }
                enable_user_inputs();
            }
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
            $("#processing").hide();
            is_faq_extraction_in_progress = false;
            enable_user_inputs();
        }
    });
}

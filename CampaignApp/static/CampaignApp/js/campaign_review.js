function reverse_sanitize_html(safe) {
    return safe.replaceAll('&amp;', '&').replaceAll('&lt;', '<').replaceAll('&gt;', '>').replaceAll('&quot;', '"').replaceAll("&#39;", "'");
}

$(document).ready(function() {
    if (TEMPLATE_TYPE != 'text'){
        IS_STATIC = (IS_STATIC === 'True')
        if(!IS_STATIC){
            document.getElementById('media_details_radio_2').checked = true;
            document.getElementById('upload_another_media').style.display = 'none';
            document.getElementById('personalised_media').style.display = 'block';
        } else{
            document.getElementById('media_details_radio_1').checked = true;
            document.getElementById('upload_another_media').style.display = 'block';
            document.getElementById('personalised_media').style.display = 'none';
        }
        set_image_preview(true);
        if (TEMPLATE_TYPE == 'document'){
            fall_back_doc_name_icon_set();
        }
    }
    update_campaign_progress_bar('Whatsapp Business');
    update_campaign_sidebar('review');
    if(document.getElementById("campaign-list-select")) {
        var select_el = document.getElementById("campaign-list-select");
        var select_element_obj = new EasyassistCustomSelect(select_el, null, null);
    }
    if(document.getElementById("custom_url_options_selected")) {
        var select_el = document.getElementById("custom_url_options_selected");
        var select_element_obj = new EasyassistCustomSelect(select_el, null, null);
    }
    if(document.getElementById("doc_name_options_selected")) {
        var select_el = document.getElementById("doc_name_options_selected");
        var select_element_obj = new EasyassistCustomSelect(select_el, null, null);
    }
    $("#template_body").text(function (index, currentcontent) {
        $(this).text(reverse_sanitize_html($(this).text()))
    })
    $("#template_header").text(function (index, currentcontent) {
        $(this).text(reverse_sanitize_html($(this).text()))
    })
    $("#template_footer").text(function (index, currentcontent) {
        $(this).text(reverse_sanitize_html($(this).text()))
    })
});

function is_custom_url_options_edited(){
    let custom_url_options_selected = $("#custom_url_options_selected").val().trim();
    if (custom_url_options_selected == 'none' || custom_url_options_selected == DYNAMIC_URL_DD){
        return true;
    }
    return false;

}

$('#custom_url_options_selected').change(function(){
    save_details_attachment();
    if (is_custom_url_options_edited()){
        document.getElementById("save_and_confirm_btn").disabled = true;
        SAVE_ATTACHMENT = true;
        EDITED = false;
    }else{
        document.getElementById("save_and_confirm_btn").disabled = false;
    }
})

function set_document_name(is_url_changed=true){
    let static_doc_name = $('#static_doc_name').val().trim();
        let document_file_name = DOCUMENT_NAME
        let doc_name_options_selected = ''
        if (IS_STATIC){
            if (!is_url_changed && static_doc_name==DOCUMENT_NAME){
                document.getElementById("save_and_confirm_btn").disabled = true;
                SAVE_ATTACHMENT = true;
                EDITED = false;
            }else{
                document.getElementById("save_and_confirm_btn").disabled = false;
                SAVE_ATTACHMENT = false;
                EDITED = true;
            }
            if (static_doc_name && static_doc_name.length > 0){
                document_file_name = static_doc_name
            }
        }else{
            let fall_back_doc_name = $('#fall_back_doc_name').val().trim();
            if (fall_back_doc_name || fall_back_doc_name.length > 1){
                document_file_name = fall_back_doc_name;
            }
            doc_name_options_selected = $("#doc_name_options_selected").val().trim();
            if (doc_name_options_selected) document_file_name = doc_name_options_selected;
            
            if (is_custom_url_options_edited()){
                SAVE_ATTACHMENT = [DYNAMIC_DOC_DD, "none"].includes(doc_name_options_selected)
                document.getElementById("save_and_confirm_btn").disabled = SAVE_ATTACHMENT;   
            }
        }
        let original_file_name = document_file_name;
        if(document_file_name && document_file_name.length > 10) document_file_name = document_file_name.substring(0,10) + "... ";
        if (document_file_name && document_file_name!='none'){
            if (!IS_STATIC) document_file_name = '{{' + document_file_name + '}}';
            $("#text-pdf-wrapper-span").text(document_file_name + '.pdf')
            $('#text-pdf-wrapper-span').attr('data-original-title', original_file_name);
        }else{
            $("#text-pdf-wrapper-span").text("document.pdf")
            $('#text-pdf-wrapper-span').attr('data-original-title',"document");
        }
}

function attachment_urls_button_check(){
    let attachment_text_field = $('#attachment_text_field').val().trim();
    let is_url_changed = false;

    if (IS_STATIC && (attachment_text_field.length < 1 || attachment_text_field==ATTACHMENT_URL)){
        document.getElementById("save_and_confirm_btn").disabled = true;
        SAVE_ATTACHMENT = true;
        EDITED = false;
    }else{
        is_url_changed = true;
        document.getElementById("save_and_confirm_btn").disabled = false;
        SAVE_ATTACHMENT = false;
        EDITED = true;
    }
    return is_url_changed;
}

function set_image_preview(is_first_render=false){
    if (IS_STATIC){
        let image_url = is_first_render ? ATTACHMENT_URL : $('#attachment_text_field').val().trim();
        if (image_url.length < 1){
            image_url = ATTACHMENT_URL;
        }
        let html=`<a href="${image_url}" target="_blank">
                <img src="${image_url}" onerror="this.onerror=null; this.src = '${DEFAULT_IMAGE}'" alt="">
            </a>`
        $("#image_wrapper_div").html(html);
        }else{
            let html=`<a href="${DEFAULT_IMAGE}" target="_blank">
                <img src="${DEFAULT_IMAGE}" alt="">
            </a>`
        $("#image_wrapper_div").html(html);
        }
}

function set_video_preview(){
    if (IS_STATIC){
        let video_url = $('#attachment_text_field').val().trim();
        let html=`<div class="video-container">
                <video src="${video_url}" controls muted width="200px" poster="${DEFAULT_IMAGE}"></video>
            </div>`
        $("#video_wrapper_div").html(html);
    }else{
        let video_url = ''
        let html=`<div class="video-container">
                <video src="${video_url}" controls muted width="200px" poster="${DEFAULT_IMAGE}"></video>
            </div>`
        $("#video_wrapper_div").html(html);
    }
}

function save_details_attachment(){
    let is_url_changed = attachment_urls_button_check();
    
    if (TEMPLATE_TYPE == 'document'){
        set_document_name(is_url_changed);
    }else if(TEMPLATE_TYPE == 'image'){
        set_image_preview();
    }else if(TEMPLATE_TYPE == 'video'){
        set_video_preview();
    }
}

$('#attachment_text_field').keyup(function(){
    let attachment_text_field = $('#attachment_text_field').val().trim();

    if (attachment_text_field.length < 1){
        document.getElementById("save_and_confirm_btn").disabled = true;
        $('.campaign-media-icons').addClass('icon-disabled');       
    }else{
        $('#media_url_text_field').css("border","")
        $('.campaign-media-icons').removeClass('icon-disabled');
        save_details_attachment();
    }
})
$('#doc_name_options_selected').change(function(){
    save_details_attachment();
})

let Buttons = document.querySelectorAll(".cutomize-media-options .options");
for (let button of Buttons) {
    button.addEventListener('click', (e) => {
        const et = e.target;
        const active = document.querySelector(".options_media .active");
        if (active) {
            active.classList.remove("active");
        }
        et.classList.add("active");
        let allContent = document.querySelectorAll('.options-div-wrapper');
        for (let content of allContent) {
            if (content.getAttribute('data-number') === button.getAttribute('data-number')) {
                content.style.display = "block";
            }else {
                content.style.display = "none";
            }
            EDITED = false;
            if (button.getAttribute('data-number') == 1){
                let is_url_changed = attachment_urls_button_check();
                IS_STATIC = true;
                if (TEMPLATE_TYPE == 'document'){
                    set_document_name(is_url_changed);
                }
                let attachment_text_field = $('#attachment_text_field').val().trim();
                if (attachment_text_field.length < 1){
                    $('#attachment_text_field').val(ATTACHMENT_URL);
                    $('#media_url_text_field').css("border","")
                    $('.campaign-media-icons').removeClass('icon-disabled');
                }
                
            }else{
                let is_media_drop_down_changed = false;
                let custom_url_options_selected = $("#custom_url_options_selected").val().trim();
                if (custom_url_options_selected == DYNAMIC_URL_DD){
                    document.getElementById("save_and_confirm_btn").disabled = true;
                }else{
                    document.getElementById("save_and_confirm_btn").disabled = false;
                    SAVE_ATTACHMENT = false;
                    EDITED = true;
                    is_media_drop_down_changed = true;
                }
                IS_STATIC = false;
                if (TEMPLATE_TYPE == 'document'){
                    set_document_name();
                    let doc_name_options_selected = $("#doc_name_options_selected").val().trim();
                    if (doc_name_options_selected == DYNAMIC_DOC_DD && !is_media_drop_down_changed){
                        document.getElementById("save_and_confirm_btn").disabled = true;
                    }else{
                        document.getElementById("save_and_confirm_btn").disabled = false;
                        SAVE_ATTACHMENT = false;
                        EDITED = true;
                    }
                }
            }
            if (TEMPLATE_TYPE == 'image'){
                set_image_preview();
            } else if(TEMPLATE_TYPE == 'video'){
                set_video_preview();
            }
        }
    });
}

function clear_attachment_text(){
    document.getElementById("save_and_confirm_btn").disabled = true;
    SAVE_ATTACHMENT = false;
    $('#attachment_text_field').val("");
    $('.campaign-media-icons').addClass('icon-disabled');
}

function open_in_new_tab(){
    let attachment_text_field = $('#attachment_text_field').val().trim();
    if (attachment_text_field.length > 0){
        window.open($('#attachment_text_field').val(), '_blank');
    }
}

function clear_fallback_text(){
    document.getElementById("save_and_confirm_btn").disabled = false;
    SAVE_ATTACHMENT = false;
    $('#fall_back_doc_name').val("");
    $('.campaign-media-icons-doc').addClass('icon-disabled');
}

function fall_back_doc_name_icon_set(){
    let fall_back_doc_name = $('#fall_back_doc_name').val().trim();

    if (fall_back_doc_name.length < 1){
        $('.campaign-media-icons-doc').addClass('icon-disabled');       
    }else{
        $('.campaign-media-icons-doc').removeClass('icon-disabled');
    }
}

$('#fall_back_doc_name').keyup(function(){
    let fall_back_doc_name = $('#fall_back_doc_name').val().trim();

    is_fall_back_name_saved = (fall_back_doc_name == FALL_BACK_DOC_NAME)
    document.getElementById("save_and_confirm_btn").disabled = is_fall_back_name_saved;

    if (!is_fall_back_name_saved){
        SAVE_ATTACHMENT = false;
        EDITED = true;
    }else{
        SAVE_ATTACHMENT = false;
        EDITED = false;
    }
    fall_back_doc_name_icon_set();
})

$('#static_doc_name').keyup(function(){
    let fall_back_doc_name = $('#static_doc_name').val().trim();
    if (fall_back_doc_name.length < 1){
        $('.campaign-media-icons-doc-static').addClass('icon-disabled'); 
    }else{
        $('.campaign-media-icons-doc-static').removeClass('icon-disabled');
        $('#document_text_field').css("border","")
        save_details_attachment();
    }
})

function clear_static_doc_text(){
    document.getElementById("save_and_confirm_btn").disabled = true;
    SAVE_ATTACHMENT = false;
    $('#static_doc_name').val("");
    $('.campaign-media-icons-doc-static').addClass('icon-disabled');
}

function save_attachment_details(show_toaster=true){

    $('#is_single_vendor_toaster').css({"display":"none"});
    document.getElementById("save_and_confirm_btn").disabled = true;

    let dynamic_attactment_column = $('#custom_url_options_selected').val();
    let doc_name_options = $('#doc_name_options_selected').val();
    let custom_attachment_url = $('#attachment_text_field').val();
    let fall_back_doc_name = $('#fall_back_doc_name').val();
    let static_doc_name = $('#static_doc_name').val();
    let old_custom_attachment_url = custom_attachment_url;
    if (!IS_STATIC){
        if (dynamic_attactment_column == 'none'){
            $('#unsuccessful_save').text("Please provide the required media details before sending the campaign.");
            $('#unsuccessfully_credentials').css({"display":"block"});
            document.getElementById("save_and_confirm_btn").disabled = false;
            return;
        }
        custom_attachment_url = '';
    }
    SAVE_ATTACHMENT = true;
    var request_params = {
        'campaign_id': get_url_multiple_vars()['campaign_id'][0],
        'doc_name_options': doc_name_options,
        'dynamic_attactment_column': dynamic_attactment_column,
        'custom_attachment_url': custom_attachment_url,
        'fall_back_doc_name': fall_back_doc_name,
        'static_doc_name': static_doc_name,
        'is_static': IS_STATIC
    };

    var json_params = JSON.stringify(request_params);
    var encrypted_data = campaign_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);   

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/campaign/save-attachment-details/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                if(IS_STATIC){
                    ATTACHMENT_URL = old_custom_attachment_url;
                    DOCUMENT_NAME = static_doc_name;
                } else{
                    DYNAMIC_URL_DD = dynamic_attactment_column;
                    DYNAMIC_DOC_DD = doc_name_options;
                    FALL_BACK_DOC_NAME = fall_back_doc_name;
                }
                successful_save_close();
                $('#unsuccessfully_credentials').css({"display":"none"});
                $('#successfully_credentials').css({"display":"none"});
                if (show_toaster){
                    $('#successful_save').text("The changes have been saved successfully, you can now proceed to send the campaign.")
                    $('#successfully_credentials').css({"display":"block"});
                }
            } else {
                SAVE_ATTACHMENT = false;
                show_campaign_toast("Internal Server Error");
                document.getElementById("save_and_confirm_btn").disabled = false;
            }
        } else if(this.readyState == 4 && this.status == 403){
            trigger_session_time_out_modal();
        } 
    }
    xhttp.send(params);  
}

function successful_save_close(){
    $('#successfully_credentials').css({"display":"none"});
    $('#unsuccessfully_credentials').css({"display":"none"});
}

$(".schedule-campaign-btn").click(function() {
    if (!validation_to_save_attachment()){
        return;
    }
    setTimeout(function() {
        if (channel_value == "whatsapp") {
            bot_wsp_id = document.getElementById("campaign-list-select").value;
            if (bot_wsp_id == "none") {
                show_campaign_toast('Please select WhatsApp BSP.');
                return;
            }
            var template_url = window.location.origin + '/campaign/schedule/?bot_pk=' + BOT_ID + '&campaign_id=' + campaign_id + 
            '&channel=WhatsApp' + '&bot_wsp_id=' + bot_wsp_id;
            window.location.href = template_url;
        } else {
            var template_url = window.location.origin + '/campaign/schedule/?bot_pk=' + BOT_ID + '&campaign_id=' + campaign_id + '&channel=RCS'
            window.location.href = template_url;
        }
    }, 1000);

});

function check_limit_of_audience(){
    let max_row = $('#get_number_for_test_audience').val().trim();
    max_row = parseInt(max_row)
    if (!max_row || max_row < 1){
        $('#get_number_for_test_audience').css("border","1px solid #ff0000");
        return true;
    }
    if (max_row > CAMPAIGN_BATCH || max_row > 50){
        document.getElementById('text_audience_modal').style.display = 'none';
        document.getElementById('error_audience_modal').style.display = 'block';
        $('.next_audience_btn').addClass('d-none');
        $('.try_again_btn').removeClass('d-none');
        return true;
    }
    $('#get_number_for_test_audience').css("border","");
    return false;
}

function get_test_audience_data(el) {

    if (check_limit_of_audience()){
        return
    }

    document.getElementById('number_of_test_recipients').style.display = 'none';  
    document.getElementById("getting_audience_loader").style.display = "block";

    let max_row = $('#get_number_for_test_audience').val().trim();
    max_row = parseInt(max_row)
    var request_params = {
        'bot_pk': get_url_multiple_vars()['bot_pk'][0],
        'campaign_id': get_url_multiple_vars()['campaign_id'][0],
        'max_row': max_row,
    };

    var json_params = JSON.stringify(request_params);
    var encrypted_data = campaign_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/campaign/test-audience-data/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                var table = get_batch_preview_table_html(response.header_name, response.sample_data);
                
                document.getElementById('edit_batch_table_div').innerHTML = table;
                setTimeout(()=>{
                    document.getElementById("getting_audience_loader").style.display = "none";
                    document.getElementById('verify_edit_batch_modal').style.display = 'block';
                    document.getElementById('verify_edit_batch').style.display = 'block';
                },2000)

                $('#number_of_audience_fetched').html('Number of test recipients : '+String(max_row))
                $('[data-toggle="tooltip"]').tooltip({
                    container: 'body',
                    boundary: 'window'
                    });
            } else if(response["status"] == 203){
                show_campaign_toast("More than audience batch");
            } else {
                show_campaign_toast(response.message);
            }
        } else if(this.readyState == 4 && this.status == 403){
            trigger_session_time_out_modal();
        } 
    }
    xhttp.send(params);   
}

function send_test_campaign() {
    let text_html = `<p>Bon voyage, test campaign! Your test campaign messages are on the way to the test recipients.</p>`
    $('#send_modal_message').html(text_html);
    let img_html = `<img src="${IN_PROGRESS_GIF}"></img>`;
    $('#sending_image_gif').html(img_html);
    document.getElementById("send_modal_sub_message").style.display = "none";
    document.getElementById('verify_edit_batch_modal').style.display = 'none';
    document.getElementById("send_campaign_modal").style.display = 'block';
    var bot_id = get_url_multiple_vars()['bot_pk'][0];
    var bot_wsp_id = null;

    bot_wsp_id = document.getElementById("campaign-list-select").value;
    let max_row = $('#get_number_for_test_audience').val().trim();
    max_row = parseInt(max_row)
    var request_params = {
        'bot_pk': bot_id,
        'campaign_id': get_url_multiple_vars()['campaign_id'][0],
        'bot_wsp_id': bot_wsp_id,
        'max_row': max_row,
    };

    var json_params = JSON.stringify(request_params);
    var encrypted_data = campaign_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);
    document.getElementById("send-campaign-button").disabled = true;
    document.getElementById("schedule-campaign-btn").disabled = true;
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/campaign/send-test-campaign/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                setTimeout(function () {
                    $('#send_modal_message').html(`<p>Test Campaign Sent Successfully!</p>`);
                    let img_html = `<img src="${SUCCESS_GIF}"></img>`;
                    let overview_link_html = `<a href='/campaign/whatsapp-campaign-details/?bot_pk=${get_url_multiple_vars()["bot_pk"][0]}&campaign_id=${get_url_multiple_vars()["campaign_id"][0]}' target="_blank" ><u>here</u></a>`
                    let text_html = `<p>You can check the detailed test campaign reports on the Overview Page by clicking ${overview_link_html}.</p>`
                    $('#send_modal_sub_message').html(text_html);
                    document.getElementById("send_modal_sub_message").style.display = "block";
                    $('#sending_image_gif').html(img_html);
                    document.getElementById("send-campaign-button").disabled = false;
                    document.getElementById("schedule-campaign-btn").disabled = false;
                }, 3000);
            }else{
                show_campaign_toast(response.message);
            }
        } else if(this.readyState == 4 && this.status == 403){
            trigger_session_time_out_modal();
        } 
    }
    xhttp.send(params);   
}

function close_all_modals(){
    document.getElementById('number_of_test_recipients').style.display = 'none';
    document.getElementById('send_campaign_modal').style.display = 'none';
    document.getElementById('verify_edit_batch_modal').style.display = 'none';
}

$('#send_another_campaign').click(function(){
    close_all_modals();
    $('#get_number_for_test_audience').val('');
    document.getElementById('number_of_test_recipients').style.display = 'block';  
})

$('#send_test_campaign_btn').click(function(){
    if (!validation_to_save_attachment()){
        return;
    }
    
    let bot_wsp_id = null;

    if (!document.getElementById("campaign-list-select")) {
        show_campaign_toast('No BSP’s are currently configured, please configure a BSP inside “API integration".');
        return;
    } else {
        bot_wsp_id = document.getElementById("campaign-list-select").value;
        if (bot_wsp_id == "none") {
            show_campaign_toast('Please select WhatsApp BSP.');
            return;
        }
    }
    $('#get_number_for_test_audience').css("border","");
    $('#get_number_for_test_audience').val('');
    document.getElementById('number_of_test_recipients').style.display = 'block';  
})

$('#back_to_enter_test_number_modal').click(function(){
    $('#get_number_for_test_audience').css("border","");
    $('#get_number_for_test_audience').val('');
    document.getElementById('verify_edit_batch_modal').style.display = 'none';
    document.getElementById('number_of_test_recipients').style.display = 'block';  
})

$('.close_number_of_test_recipients').click(function(){
    close_all_modals();
})

$('.try_again_btn').click(function(){
    $('#get_number_for_test_audience').css("border","");
    $('#get_number_for_test_audience').val('');
    document.getElementById('text_audience_modal').style.display = 'block';
    document.getElementById('error_audience_modal').style.display = 'none';
    $('.next_audience_btn').removeClass('d-none');
    $('.try_again_btn').addClass('d-none');
})

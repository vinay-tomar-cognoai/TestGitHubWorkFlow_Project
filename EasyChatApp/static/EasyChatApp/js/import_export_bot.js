var selected_export = {
    0: 'export',
    1: 'export-as-zip',
    2: 'export-faq',
    3: 'export-alexa-json',
    4: 'export-multilingual-intents-as-excel',
}

var bot_id = ""

var import_timer = null

$(document).ready(function() {
        track_file_import_progress();
        import_timer = setInterval(track_file_import_progress, 5000);

    $('#export_import_tab').on('click', function() {
        if (!import_timer) {
            track_file_import_progress();
            import_timer = setInterval(track_file_import_progress, 5000);
        }
    })
})

function export_data(bot_pk) {
    bot_id = bot_pk;
    var selected_type = $("#select-export-type").val()
    if (selected_type == "None") {

        M.toast({
            "html": "Please select a valid option."
        }, 2000)
        return;
    }

    if (INTENT_COUNT > 100) {
        $('#easychat_export_bot_email_modal').modal('open');
    } else {
        window.location = '/chat/bot/' + selected_export[selected_type] + '/' + bot_pk
    }
}

function export_data_on_mail() {
    var email_id = document.getElementById('easychat-export-bot-email-id').value.trim();

    if (!validateEmailAddr(email_id)) {
        M.toast({
            'html': 'Please enter valid Email ID.'
        }, 2000);

        return;
    }

    var selected_type = $("#select-export-type").val()

    var json_string = JSON.stringify({
        bot_id: bot_id,
        email_id: email_id,
        export_type: selected_type
    })

    $.ajax({
        url: '/chat/bot/export-large-bot/',
        type: "POST",
        async: false,
        data: {
            json_string: json_string,
        },
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                
                M.toast({
                    'html': "We haved saved your request and will send data over provided email ID within 24 hours."
                }, 2000);
                $('#easychat_export_bot_email_modal').modal('close');
            } else {

                M.toast({
                    'html': "Failed to export bot. Please try again later."
                }, 2000);
            }
        }
    })
}

function handle_zip_upload(ele) {

    var input_file = ele.files[0];

    if (input_file == null || input_file == undefined) {
        M.toast({
            "html": "Please select a valid file."
        }, 2000);
        document.getElementById("error-message-zip").innerText = "Please select a valid file.";
        document.getElementById("error-message-zip").style.display = "block";
        return false;
    }

    if (input_file.name.match(/\.(zip)$/) == null) {
        M.toast({
            "html": "Please select the correct file type(.zip)"
        }, 2000);
        document.getElementById("error-message-zip").innerText = "Please select the correct file type(.zip)";
        document.getElementById("error-message-zip").style.display = "block";
        return false;
    }

    if (check_malicious_file(input_file.name) == true) {
        M.toast({
            "html": "Please select the correct file type(.zip)"
        }, 2000);
        document.getElementById("error-message-zip").innerText = "Please select the correct file type(.zip)";
        document.getElementById("error-message-zip").style.display = "block";
        return false;
    }

    $('#modal-import-bot-zip .drag-drop-container .drag-drop-message').hide();
    $('#modal-import-bot-zip #error-message-zip').hide();
    $('#modal-import-bot-zip #zip-selected-container').html(`
    <div class="selected-image-wrapper">
        <div class="image-container-div">
            <svg version="1.1" id="Capa_2" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px"
	            width="77.749px" height="77.749px" viewBox="0 0 77.749 77.749" style="enable-background:new 0 0 77.749 77.749;"
	            xml:space="preserve">
                <g>
                    <path d="M54.04,0H14.908c-2.627,0-4.767,2.141-4.767,4.768V72.98c0,2.631,2.14,4.769,4.767,4.769H62.84
                    c2.63,0,4.768-2.138,4.768-4.769V14.743L54.04,0z M55.165,7.135l5.947,6.463h-5.947V7.135z M63.604,72.98
                    c0,0.42-0.344,0.765-0.766,0.765h-47.93c-0.421,0-0.763-0.345-0.763-0.765V4.768c0-0.421,0.342-0.762,0.763-0.762h24.413v1.717
                    h-5.18v2.892h5.18v5.676h-5.18v2.891h5.18v5.442h-5.18v2.891h5.18v0.217v0.166v4.281h-5.18v2.892h5.18v5.676h-5.18v2.892h5.18
                    v5.441h-5.18v2.891h2.77c-1.059,0.053-1.902,0.92-1.902,1.99v1.141h0.016v8.649c0,2.246,1.828,4.074,4.074,4.074
                    s4.073-1.828,4.073-4.074v-8.649h0.002v-1.141c0-1.104-0.896-2-2-2h-0.057v-4.438h4.756v-2.892h-4.756v-5.441h4.756v-2.892h-4.756
                    v-5.677h4.756v-2.891h-4.756v-4.664h4.756v-2.891h-4.756v-5.442h4.756V9.842h-4.756V4.165h4.756v-0.16h5.285V15.6
                    c0,1.104,0.899,1.999,2.004,1.999h10.441V72.98z M41.7,56.65v4.832c0,1.451-1.177,2.625-2.625,2.625
                    c-1.449,0-2.625-1.174-2.625-2.625V56.65H41.7z"/>
                </g>
            </svg>
            <svg onclick="file_remove_handler('zip')" class="dismiss-circle" width="20" height="21" viewBox="0 0 20 21" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M10 2.5C14.4183 2.5 18 6.08172 18 10.5C18 14.9183 14.4183 18.5 10 18.5C5.58172 18.5 2 14.9183 2 10.5C2 6.08172 5.58172 2.5 10 2.5ZM7.80943 7.61372C7.61456 7.47872 7.34514 7.49801 7.17157 7.67157L7.11372 7.74082C6.97872 7.93569 6.99801 8.20511 7.17157 8.37868L9.29289 10.5L7.17157 12.6213L7.11372 12.6906C6.97872 12.8854 6.99801 13.1549 7.17157 13.3284L7.24082 13.3863C7.43569 13.5213 7.70511 13.502 7.87868 13.3284L10 11.2071L12.1213 13.3284L12.1906 13.3863C12.3854 13.5213 12.6549 13.502 12.8284 13.3284L12.8863 13.2592C13.0213 13.0643 13.002 12.7949 12.8284 12.6213L10.7071 10.5L12.8284 8.37868L12.8863 8.30943C13.0213 8.11456 13.002 7.84514 12.8284 7.67157L12.7592 7.61372C12.5643 7.47872 12.2949 7.49801 12.1213 7.67157L10 9.79289L7.87868 7.67157L7.80943 7.61372Z" fill="#4D4D4D"/>
            </svg>                                                    
        </div>
        <div class="image-name-copy-div" style="width: 100%">
            <div class="image-name" style="font-weight: normal;font-size: 14px;color:#000000;line-height: 17px;margin-bottom: 10px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; width: 100%;">
                ${sanitize_html(input_file.name)}
            </div>
        </div>
    </div>`);
}

function handle_json_upload(ele) {

    var input_file = ele.files[0];

    if (input_file == null || input_file == undefined) {
        M.toast({
            "html": "Please select a valid file."
        }, 2000);
        document.getElementById("error-message-json").innerText = "Please select a valid file.";
        document.getElementById("error-message-json").style.display = "block";
        return false;
    }

    if (input_file.name.match(/\.(json)$/) == null) {
        M.toast({
            "html": "Please select the correct file type(.json)"
        }, 2000);
        document.getElementById("error-message-json").innerText = "Please select the correct file type(.json)";
        document.getElementById("error-message-json").style.display = "block";
        return false;
    }

    if (check_malicious_file(input_file.name) == true) {
        M.toast({
            "html": "Please select the correct file type(.json)"
        }, 2000);
        document.getElementById("error-message-json").innerText = "Please select the correct file type(.json)";
        document.getElementById("error-message-json").style.display = "block";
        return false;
    }

    $('#modal-import-bot-json .drag-drop-container .drag-drop-message').hide();
    $('#modal-import-bot-json #error-message-json').hide();
    $('#modal-import-bot-json #json-selected-container').html(`
    <div class="selected-image-wrapper">
        <div class="image-container-div">
        <svg version="1.1" id="Capa_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px"
        viewBox="0 0 58 58" width='78' height='78' style="enable-background:new 0 0 58 58;" xml:space="preserve">
   <g>
       <path d="M50.949,12.187l-1.361-1.361l-9.504-9.505c-0.001-0.001-0.001-0.001-0.002-0.001l-0.77-0.771
           C38.957,0.195,38.486,0,37.985,0H8.963C7.776,0,6.5,0.916,6.5,2.926V39v16.537V56c0,0.837,0.841,1.652,1.836,1.909
           c0.051,0.014,0.1,0.033,0.152,0.043C8.644,57.983,8.803,58,8.963,58h40.074c0.16,0,0.319-0.017,0.475-0.048
           c0.052-0.01,0.101-0.029,0.152-0.043C50.659,57.652,51.5,56.837,51.5,56v-0.463V39V13.978C51.5,13.211,51.407,12.644,50.949,12.187
           z M39.5,3.565L47.935,12H39.5V3.565z M8.963,56c-0.071,0-0.135-0.025-0.198-0.049C8.61,55.877,8.5,55.721,8.5,55.537V41h41v14.537
           c0,0.184-0.11,0.34-0.265,0.414C49.172,55.975,49.108,56,49.037,56H8.963z M8.5,39V2.926C8.5,2.709,8.533,2,8.963,2h28.595
           C37.525,2.126,37.5,2.256,37.5,2.391V13.78c-0.532-0.48-1.229-0.78-2-0.78c-0.553,0-1,0.448-1,1s0.447,1,1,1c0.552,0,1,0.449,1,1v4
           c0,1.2,0.542,2.266,1.382,3c-0.84,0.734-1.382,1.8-1.382,3v4c0,0.551-0.448,1-1,1c-0.553,0-1,0.448-1,1s0.447,1,1,1
           c1.654,0,3-1.346,3-3v-4c0-1.103,0.897-2,2-2c0.553,0,1-0.448,1-1s-0.447-1-1-1c-1.103,0-2-0.897-2-2v-4
           c0-0.771-0.301-1.468-0.78-2h11.389c0.135,0,0.265-0.025,0.391-0.058c0,0.015,0.001,0.021,0.001,0.036V39H8.5z"/>
       <path d="M16.354,51.43c-0.019,0.446-0.171,0.764-0.458,0.95s-0.672,0.28-1.155,0.28c-0.191,0-0.396-0.022-0.615-0.068
           s-0.429-0.098-0.629-0.157s-0.385-0.123-0.554-0.191s-0.299-0.135-0.39-0.198l-0.697,1.107c0.183,0.137,0.405,0.26,0.67,0.369
           s0.54,0.207,0.827,0.294s0.565,0.15,0.834,0.191s0.504,0.062,0.704,0.062c0.401,0,0.791-0.039,1.169-0.116
           c0.378-0.077,0.713-0.214,1.005-0.41s0.524-0.456,0.697-0.779s0.26-0.723,0.26-1.196v-7.848h-1.668V51.43z"/>
       <path d="M25.083,49.064c-0.314-0.228-0.654-0.422-1.019-0.581s-0.702-0.323-1.012-0.492s-0.569-0.364-0.779-0.588
           s-0.314-0.518-0.314-0.882c0-0.146,0.036-0.299,0.109-0.458s0.173-0.303,0.301-0.431s0.273-0.234,0.438-0.321
           s0.337-0.139,0.52-0.157c0.328-0.027,0.597-0.032,0.807-0.014s0.378,0.05,0.506,0.096s0.226,0.091,0.294,0.137
           s0.13,0.082,0.185,0.109c0.009-0.009,0.036-0.055,0.082-0.137s0.101-0.185,0.164-0.308s0.132-0.255,0.205-0.396
           s0.137-0.271,0.191-0.39c-0.265-0.173-0.61-0.299-1.039-0.376s-0.853-0.116-1.271-0.116c-0.41,0-0.8,0.063-1.169,0.191
           s-0.692,0.313-0.971,0.554s-0.499,0.535-0.663,0.882S20.4,46.13,20.4,46.576c0,0.492,0.104,0.902,0.314,1.23
           s0.474,0.613,0.793,0.854s0.661,0.451,1.025,0.629s0.704,0.355,1.019,0.533s0.576,0.376,0.786,0.595s0.314,0.483,0.314,0.793
           c0,0.511-0.148,0.896-0.444,1.155s-0.723,0.39-1.278,0.39c-0.183,0-0.378-0.019-0.588-0.055s-0.419-0.084-0.629-0.144
           s-0.412-0.123-0.608-0.191s-0.357-0.139-0.485-0.212l-0.287,1.176c0.155,0.137,0.34,0.253,0.554,0.349s0.439,0.171,0.677,0.226
           c0.237,0.055,0.472,0.094,0.704,0.116s0.458,0.034,0.677,0.034c0.511,0,0.966-0.077,1.367-0.232s0.738-0.362,1.012-0.622
           s0.485-0.561,0.636-0.902s0.226-0.695,0.226-1.06c0-0.538-0.104-0.978-0.314-1.319S25.397,49.292,25.083,49.064z"/>
       <path d="M34.872,45.072c-0.378-0.429-0.82-0.754-1.326-0.978s-1.06-0.335-1.661-0.335s-1.155,0.111-1.661,0.335
           s-0.948,0.549-1.326,0.978s-0.675,0.964-0.889,1.606s-0.321,1.388-0.321,2.235s0.107,1.595,0.321,2.242s0.511,1.185,0.889,1.613
           s0.82,0.752,1.326,0.971s1.06,0.328,1.661,0.328s1.155-0.109,1.661-0.328s0.948-0.542,1.326-0.971s0.675-0.966,0.889-1.613
           s0.321-1.395,0.321-2.242s-0.107-1.593-0.321-2.235S35.25,45.501,34.872,45.072z M34.195,50.698
           c-0.137,0.487-0.326,0.882-0.567,1.183s-0.515,0.518-0.82,0.649s-0.627,0.198-0.964,0.198c-0.328,0-0.641-0.07-0.937-0.212
           s-0.561-0.364-0.793-0.67s-0.415-0.699-0.547-1.183s-0.203-1.066-0.212-1.75c0.009-0.702,0.082-1.294,0.219-1.777
           c0.137-0.483,0.326-0.877,0.567-1.183s0.515-0.521,0.82-0.649s0.627-0.191,0.964-0.191c0.328,0,0.641,0.068,0.937,0.205
           s0.561,0.36,0.793,0.67s0.415,0.704,0.547,1.183s0.203,1.06,0.212,1.743C34.405,49.616,34.332,50.211,34.195,50.698z"/>
       <polygon points="44.012,50.869 40.061,43.924 38.393,43.924 38.393,54 40.061,54 40.061,47.055 44.012,54 45.68,54 45.68,43.924 
           44.012,43.924 	"/>
       <path d="M20.5,20v-4c0-0.551,0.448-1,1-1c0.553,0,1-0.448,1-1s-0.447-1-1-1c-1.654,0-3,1.346-3,3v4c0,1.103-0.897,2-2,2
           c-0.553,0-1,0.448-1,1s0.447,1,1,1c1.103,0,2,0.897,2,2v4c0,1.654,1.346,3,3,3c0.553,0,1-0.448,1-1s-0.447-1-1-1
           c-0.552,0-1-0.449-1-1v-4c0-1.2-0.542-2.266-1.382-3C19.958,22.266,20.5,21.2,20.5,20z"/>
       <circle cx="28.5" cy="19.5" r="1.5"/>
       <path d="M28.5,25c-0.553,0-1,0.448-1,1v3c0,0.552,0.447,1,1,1s1-0.448,1-1v-3C29.5,25.448,29.053,25,28.5,25z"/>
   </g>
   </svg>
            <svg onclick="file_remove_handler('json')" class="dismiss-circle" width="20" height="21" viewBox="0 0 20 21" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M10 2.5C14.4183 2.5 18 6.08172 18 10.5C18 14.9183 14.4183 18.5 10 18.5C5.58172 18.5 2 14.9183 2 10.5C2 6.08172 5.58172 2.5 10 2.5ZM7.80943 7.61372C7.61456 7.47872 7.34514 7.49801 7.17157 7.67157L7.11372 7.74082C6.97872 7.93569 6.99801 8.20511 7.17157 8.37868L9.29289 10.5L7.17157 12.6213L7.11372 12.6906C6.97872 12.8854 6.99801 13.1549 7.17157 13.3284L7.24082 13.3863C7.43569 13.5213 7.70511 13.502 7.87868 13.3284L10 11.2071L12.1213 13.3284L12.1906 13.3863C12.3854 13.5213 12.6549 13.502 12.8284 13.3284L12.8863 13.2592C13.0213 13.0643 13.002 12.7949 12.8284 12.6213L10.7071 10.5L12.8284 8.37868L12.8863 8.30943C13.0213 8.11456 13.002 7.84514 12.8284 7.67157L12.7592 7.61372C12.5643 7.47872 12.2949 7.49801 12.1213 7.67157L10 9.79289L7.87868 7.67157L7.80943 7.61372Z" fill="#4D4D4D"/>
            </svg>                                                    
        </div>
        <div class="image-name-copy-div" style="width: 100%;">
            <div class="image-name" style="font-weight: normal;font-size: 14px;color:#000000;line-height: 17px;margin-bottom: 10px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; width: 100%;">
                ${sanitize_html(input_file.name)}
            </div>
        </div>
    </div>`);
}

function handle_excel_upload(ele) {

    var input_file = ele.files[0];

    if (input_file == null || input_file == undefined) {
        M.toast({
            "html": "Please select a valid file."
        }, 2000);
        document.getElementById("error-message-excel").innerText = "Please select a valid file.";
        document.getElementById("error-message-excel").style.display = "block";
        return false;
    }

    if (input_file.name.match(/\.(xls|xlsx)$/) == null) {
        M.toast({
            "html": "Please select the correct file type(.xls,.xlsx)"
        }, 2000);
        document.getElementById("error-message-excel").innerText = "Please select the correct file type(.xls, .xlsx)";
        document.getElementById("error-message-excel").style.display = "block";
        return false;
    }

    if (check_malicious_file(input_file.name) == true) {
        M.toast({
            "html": "Please select the correct file type(.xls, .xlsx)"
        }, 2000);
        document.getElementById("error-message-excel").innerText = "Please select the correct file type(.xls, .xlsx)";
        document.getElementById("error-message-excel").style.display = "block";
        return false;
    }

    $('#modal-import-mulitlingual-intents-excel .drag-drop-container .drag-drop-message').hide();
    $('#modal-import-mulitlingual-intents-excel #error-message-excel').hide();
    $('#modal-import-mulitlingual-intents-excel #excel-selected-container').html(`
    <div class="selected-image-wrapper">
        <div class="image-container-div">
        <svg version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px"
            viewBox="0 0 512 512" style="enable-background:new 0 0 512 512;" xml:space="preserve" width='78' height='78'>
        <g>
            <g>
                <g>
                    <path d="M447.168,134.56c-0.535-1.288-1.318-2.459-2.304-3.445l-128-128c-2.003-1.988-4.709-3.107-7.531-3.115H74.667
                        C68.776,0,64,4.776,64,10.667v490.667C64,507.224,68.776,512,74.667,512h362.667c5.891,0,10.667-4.776,10.667-10.667V138.667
                        C447.997,137.256,447.714,135.86,447.168,134.56z M320,36.416L411.584,128H320V36.416z M426.667,490.667H85.333V21.333h213.333
                        v117.333c0,5.891,4.776,10.667,10.667,10.667h117.333V490.667z"/>
                    <path d="M128,181.333v256c0,5.891,4.776,10.667,10.667,10.667h234.667c5.891,0,10.667-4.776,10.667-10.667v-256
                        c0-5.891-4.776-10.667-10.667-10.667H138.667C132.776,170.667,128,175.442,128,181.333z M320,192h42.667v42.667H320V192z
                        M320,256h42.667v42.667H320V256z M320,320h42.667v42.667H320V320z M320,384h42.667v42.667H320V384z M213.333,192h85.333v42.667
                        h-85.333V192z M213.333,256h85.333v42.667h-85.333V256z M213.333,320h85.333v42.667h-85.333V320z M213.333,384h85.333v42.667
                        h-85.333V384z M149.333,192H192v42.667h-42.667V192z M149.333,256H192v42.667h-42.667V256z M149.333,320H192v42.667h-42.667V320z
                        M149.333,384H192v42.667h-42.667V384z"/>
                </g>
            </g>
        </g>
        </svg>

            <svg onclick="file_remove_handler('excel')" class="dismiss-circle" width="20" height="21" viewBox="0 0 20 21" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M10 2.5C14.4183 2.5 18 6.08172 18 10.5C18 14.9183 14.4183 18.5 10 18.5C5.58172 18.5 2 14.9183 2 10.5C2 6.08172 5.58172 2.5 10 2.5ZM7.80943 7.61372C7.61456 7.47872 7.34514 7.49801 7.17157 7.67157L7.11372 7.74082C6.97872 7.93569 6.99801 8.20511 7.17157 8.37868L9.29289 10.5L7.17157 12.6213L7.11372 12.6906C6.97872 12.8854 6.99801 13.1549 7.17157 13.3284L7.24082 13.3863C7.43569 13.5213 7.70511 13.502 7.87868 13.3284L10 11.2071L12.1213 13.3284L12.1906 13.3863C12.3854 13.5213 12.6549 13.502 12.8284 13.3284L12.8863 13.2592C13.0213 13.0643 13.002 12.7949 12.8284 12.6213L10.7071 10.5L12.8284 8.37868L12.8863 8.30943C13.0213 8.11456 13.002 7.84514 12.8284 7.67157L12.7592 7.61372C12.5643 7.47872 12.2949 7.49801 12.1213 7.67157L10 9.79289L7.87868 7.67157L7.80943 7.61372Z" fill="#4D4D4D"/>
            </svg>                                                    
        </div>
        <div class="image-name-copy-div" style="width: 100%">
            <div class="image-name" style="font-weight: normal;font-size: 14px;color:#000000;line-height: 17px;margin-bottom: 10px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; width: 100%;">
                ${sanitize_html(input_file.name)}
            </div>
        </div>
    </div>`);
}

function handle_intent_json_upload(ele) {

    var input_file = ele.files[0];

    if (input_file == null || input_file == undefined) {
        M.toast({
            "html": "Please select a valid file."
        }, 2000);
        document.getElementById("error-message-intent-json").innerText = "Please select a valid file.";
        document.getElementById("error-message-intent-json").style.display = "block";
        return false;
    }

    if (input_file.name.match(/\.(json)$/) == null) {
        M.toast({
            "html": "Please select the correct file type(.json)"
        }, 2000);
        document.getElementById("error-message-intent-json").innerText = "Please select the correct file type(.json)";
        document.getElementById("error-message-intent-json").style.display = "block";
        return false;
    }

    if (check_malicious_file(input_file.name) == true) {
        M.toast({
            "html": "Please select the correct file type(.json)"
        }, 2000);
        document.getElementById("error-message-intent-json").innerText = "Please select the correct file type(.json)";
        document.getElementById("error-message-intent-json").style.display = "block";
        return false;
    }

    $('#modal-import-intent-json .drag-drop-container .drag-drop-message').hide();
    $('#modal-import-intent-json #error-message-intent-json').hide();
    $('#modal-import-intent-json #intent-json-selected-container').html(`
    <div class="selected-image-wrapper">
        <div class="image-container-div">
        <svg version="1.1" id="Capa_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px"
        viewBox="0 0 58 58" width='78' height='78' style="enable-background:new 0 0 58 58;" xml:space="preserve">
   <g>
       <path d="M50.949,12.187l-1.361-1.361l-9.504-9.505c-0.001-0.001-0.001-0.001-0.002-0.001l-0.77-0.771
           C38.957,0.195,38.486,0,37.985,0H8.963C7.776,0,6.5,0.916,6.5,2.926V39v16.537V56c0,0.837,0.841,1.652,1.836,1.909
           c0.051,0.014,0.1,0.033,0.152,0.043C8.644,57.983,8.803,58,8.963,58h40.074c0.16,0,0.319-0.017,0.475-0.048
           c0.052-0.01,0.101-0.029,0.152-0.043C50.659,57.652,51.5,56.837,51.5,56v-0.463V39V13.978C51.5,13.211,51.407,12.644,50.949,12.187
           z M39.5,3.565L47.935,12H39.5V3.565z M8.963,56c-0.071,0-0.135-0.025-0.198-0.049C8.61,55.877,8.5,55.721,8.5,55.537V41h41v14.537
           c0,0.184-0.11,0.34-0.265,0.414C49.172,55.975,49.108,56,49.037,56H8.963z M8.5,39V2.926C8.5,2.709,8.533,2,8.963,2h28.595
           C37.525,2.126,37.5,2.256,37.5,2.391V13.78c-0.532-0.48-1.229-0.78-2-0.78c-0.553,0-1,0.448-1,1s0.447,1,1,1c0.552,0,1,0.449,1,1v4
           c0,1.2,0.542,2.266,1.382,3c-0.84,0.734-1.382,1.8-1.382,3v4c0,0.551-0.448,1-1,1c-0.553,0-1,0.448-1,1s0.447,1,1,1
           c1.654,0,3-1.346,3-3v-4c0-1.103,0.897-2,2-2c0.553,0,1-0.448,1-1s-0.447-1-1-1c-1.103,0-2-0.897-2-2v-4
           c0-0.771-0.301-1.468-0.78-2h11.389c0.135,0,0.265-0.025,0.391-0.058c0,0.015,0.001,0.021,0.001,0.036V39H8.5z"/>
       <path d="M16.354,51.43c-0.019,0.446-0.171,0.764-0.458,0.95s-0.672,0.28-1.155,0.28c-0.191,0-0.396-0.022-0.615-0.068
           s-0.429-0.098-0.629-0.157s-0.385-0.123-0.554-0.191s-0.299-0.135-0.39-0.198l-0.697,1.107c0.183,0.137,0.405,0.26,0.67,0.369
           s0.54,0.207,0.827,0.294s0.565,0.15,0.834,0.191s0.504,0.062,0.704,0.062c0.401,0,0.791-0.039,1.169-0.116
           c0.378-0.077,0.713-0.214,1.005-0.41s0.524-0.456,0.697-0.779s0.26-0.723,0.26-1.196v-7.848h-1.668V51.43z"/>
       <path d="M25.083,49.064c-0.314-0.228-0.654-0.422-1.019-0.581s-0.702-0.323-1.012-0.492s-0.569-0.364-0.779-0.588
           s-0.314-0.518-0.314-0.882c0-0.146,0.036-0.299,0.109-0.458s0.173-0.303,0.301-0.431s0.273-0.234,0.438-0.321
           s0.337-0.139,0.52-0.157c0.328-0.027,0.597-0.032,0.807-0.014s0.378,0.05,0.506,0.096s0.226,0.091,0.294,0.137
           s0.13,0.082,0.185,0.109c0.009-0.009,0.036-0.055,0.082-0.137s0.101-0.185,0.164-0.308s0.132-0.255,0.205-0.396
           s0.137-0.271,0.191-0.39c-0.265-0.173-0.61-0.299-1.039-0.376s-0.853-0.116-1.271-0.116c-0.41,0-0.8,0.063-1.169,0.191
           s-0.692,0.313-0.971,0.554s-0.499,0.535-0.663,0.882S20.4,46.13,20.4,46.576c0,0.492,0.104,0.902,0.314,1.23
           s0.474,0.613,0.793,0.854s0.661,0.451,1.025,0.629s0.704,0.355,1.019,0.533s0.576,0.376,0.786,0.595s0.314,0.483,0.314,0.793
           c0,0.511-0.148,0.896-0.444,1.155s-0.723,0.39-1.278,0.39c-0.183,0-0.378-0.019-0.588-0.055s-0.419-0.084-0.629-0.144
           s-0.412-0.123-0.608-0.191s-0.357-0.139-0.485-0.212l-0.287,1.176c0.155,0.137,0.34,0.253,0.554,0.349s0.439,0.171,0.677,0.226
           c0.237,0.055,0.472,0.094,0.704,0.116s0.458,0.034,0.677,0.034c0.511,0,0.966-0.077,1.367-0.232s0.738-0.362,1.012-0.622
           s0.485-0.561,0.636-0.902s0.226-0.695,0.226-1.06c0-0.538-0.104-0.978-0.314-1.319S25.397,49.292,25.083,49.064z"/>
       <path d="M34.872,45.072c-0.378-0.429-0.82-0.754-1.326-0.978s-1.06-0.335-1.661-0.335s-1.155,0.111-1.661,0.335
           s-0.948,0.549-1.326,0.978s-0.675,0.964-0.889,1.606s-0.321,1.388-0.321,2.235s0.107,1.595,0.321,2.242s0.511,1.185,0.889,1.613
           s0.82,0.752,1.326,0.971s1.06,0.328,1.661,0.328s1.155-0.109,1.661-0.328s0.948-0.542,1.326-0.971s0.675-0.966,0.889-1.613
           s0.321-1.395,0.321-2.242s-0.107-1.593-0.321-2.235S35.25,45.501,34.872,45.072z M34.195,50.698
           c-0.137,0.487-0.326,0.882-0.567,1.183s-0.515,0.518-0.82,0.649s-0.627,0.198-0.964,0.198c-0.328,0-0.641-0.07-0.937-0.212
           s-0.561-0.364-0.793-0.67s-0.415-0.699-0.547-1.183s-0.203-1.066-0.212-1.75c0.009-0.702,0.082-1.294,0.219-1.777
           c0.137-0.483,0.326-0.877,0.567-1.183s0.515-0.521,0.82-0.649s0.627-0.191,0.964-0.191c0.328,0,0.641,0.068,0.937,0.205
           s0.561,0.36,0.793,0.67s0.415,0.704,0.547,1.183s0.203,1.06,0.212,1.743C34.405,49.616,34.332,50.211,34.195,50.698z"/>
       <polygon points="44.012,50.869 40.061,43.924 38.393,43.924 38.393,54 40.061,54 40.061,47.055 44.012,54 45.68,54 45.68,43.924 
           44.012,43.924 	"/>
       <path d="M20.5,20v-4c0-0.551,0.448-1,1-1c0.553,0,1-0.448,1-1s-0.447-1-1-1c-1.654,0-3,1.346-3,3v4c0,1.103-0.897,2-2,2
           c-0.553,0-1,0.448-1,1s0.447,1,1,1c1.103,0,2,0.897,2,2v4c0,1.654,1.346,3,3,3c0.553,0,1-0.448,1-1s-0.447-1-1-1
           c-0.552,0-1-0.449-1-1v-4c0-1.2-0.542-2.266-1.382-3C19.958,22.266,20.5,21.2,20.5,20z"/>
       <circle cx="28.5" cy="19.5" r="1.5"/>
       <path d="M28.5,25c-0.553,0-1,0.448-1,1v3c0,0.552,0.447,1,1,1s1-0.448,1-1v-3C29.5,25.448,29.053,25,28.5,25z"/>
   </g>
   </svg>
            <svg onclick="file_remove_handler('intent-json')" class="dismiss-circle" width="20" height="21" viewBox="0 0 20 21" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M10 2.5C14.4183 2.5 18 6.08172 18 10.5C18 14.9183 14.4183 18.5 10 18.5C5.58172 18.5 2 14.9183 2 10.5C2 6.08172 5.58172 2.5 10 2.5ZM7.80943 7.61372C7.61456 7.47872 7.34514 7.49801 7.17157 7.67157L7.11372 7.74082C6.97872 7.93569 6.99801 8.20511 7.17157 8.37868L9.29289 10.5L7.17157 12.6213L7.11372 12.6906C6.97872 12.8854 6.99801 13.1549 7.17157 13.3284L7.24082 13.3863C7.43569 13.5213 7.70511 13.502 7.87868 13.3284L10 11.2071L12.1213 13.3284L12.1906 13.3863C12.3854 13.5213 12.6549 13.502 12.8284 13.3284L12.8863 13.2592C13.0213 13.0643 13.002 12.7949 12.8284 12.6213L10.7071 10.5L12.8284 8.37868L12.8863 8.30943C13.0213 8.11456 13.002 7.84514 12.8284 7.67157L12.7592 7.61372C12.5643 7.47872 12.2949 7.49801 12.1213 7.67157L10 9.79289L7.87868 7.67157L7.80943 7.61372Z" fill="#4D4D4D"/>
            </svg>                                                    
        </div>
        <div class="image-name-copy-div" style="width: 100%;">
            <div class="image-name" style="font-weight: normal;font-size: 14px;color:#000000;line-height: 17px;margin-bottom: 10px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; width: 100%;">
                ${sanitize_html(input_file.name)}
            </div>
        </div>
    </div>`);
}

function file_remove_handler(type){
    let id;
    if (type == 'zip') {
        id = 'modal-import-bot-zip';
    } else if (type == 'json') {
        id = 'modal-import-bot-json';
    } else if (type == 'excel') {
        id = 'modal-import-mulitlingual-intents-excel'
    } else if (type == 'intent-json') {
        id = 'modal-import-intent-json';
    }

    $('#' + id + " .drag-drop-container .drag-drop-message").show();
    $('#' + id + " .file-selected-container").html("");
    $('#' + id + " .easychat-import-input-box").val(""); 
  }
  

function import_data() {

    var selected_type = $("#select-import-type").val()

    if (selected_type == "None") {

        M.toast({
            "html": "Please select a valid option."
        }, 2000)
        return;
    }
    if (selected_type == "0") {

        $("#modal-import-bot-json").modal('open')
    } else if (selected_type == "1") {

        $("#modal-import-bot-zip").modal('open')
    } 
    else if (selected_type == "2"){
        $("#modal-import-mulitlingual-intents-excel").modal('open')
    }else {
        $("#modal-import-intent-instruction").modal('open')
    }
}

$(document).on("click", "#import-bot-json", function(e) {

    bot_id = window.location.pathname.split('/')[3]

    e.preventDefault();
    var input_json_file = ($("#drag-drop-input-box-json"))[0].files[0]

    if (input_json_file == null || input_json_file == undefined) {
        M.toast({
            "html": "Please select a file."
        }, 2000);
        return false;
    }

    if (check_malicious_file(input_json_file.name) == true) {
        return false;
    }

    var formData = new FormData();
    var csrf_token = $('input[name="csrfmiddlewaretoken"]').val();
    formData.append("input_json_file", input_json_file);
    formData.append("data", JSON.stringify({
        "bot_id": bot_id
    }));

    e.target.innerHTML = 'Uploading...';
    e.target.disabled = true;

    $.ajax({
        url: "/chat/bot/import/",
        type: "POST",
        headers: {
            'X-CSRFToken': csrf_token
        },
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response["status"] == 200) {
                M.toast({
                    "html": "Import started"
                }, 2000);

                show_import_progress(input_json_file.name);

                import_timer = setInterval(track_file_import_progress, 5000);

            } else if (response["status"] == 401) {
                M.toast({
                    "html": "Some problem occured during importing json file."
                }, 2000);
            } else if (response["status"] == 300) {
                M.toast({
                    "html": "Not supported file format"
                }, 2000);
            } else {
                M.toast({
                    "html": "Unable to import agent into existing bot. Please upload valid json file."
                }, 2000);
            }

            e.target.innerHTML = 'Upload';
            e.target.disabled = false;

            $("#modal-import-bot-json").modal("close");
            file_remove_handler('json');
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);

            e.target.innerHTML = 'Upload';
            e.target.disabled = false;
            $("#modal-import-bot-json").modal("close");
            file_remove_handler('json');
            M.toast({
                "html": "Import failed"
            }, 2000);

        }
    });
});

$(document).on("click", "#import-bot-zip", function(e) {

    bot_id = window.location.pathname.split('/')[3]

    e.preventDefault();
    var input_zip_file = ($("#drag-drop-input-box-zip"))[0].files[0]

    if (input_zip_file == null || input_zip_file == undefined) {
        M.toast({
            "html": "Please select a zip file."
        }, 2000);
        return false;
    }

    if (check_malicious_file(input_zip_file.name) == true) {
        return false;
    }

    var file_ext = input_zip_file.name.split('.').pop()

    if (file_ext != 'zip') {

        M.toast({
            "html": "Please upload valid zip file."
        }, 2000);
        $("#modal-import-bot-zip").modal("close");
        return;
    }

    var formData = new FormData();
    var csrf_token = $('input[name="csrfmiddlewaretoken"]').val();
    formData.append("input_zip_file", input_zip_file);
    formData.append("data", JSON.stringify({
        "bot_id": bot_id
    }));

    e.target.innerHTML = 'Uploading';
    e.target.disabled = true;

    $.ajax({
        url: "/chat/bot/import-bot-zip/",
        type: "POST",
        headers: {
            'X-CSRFToken': csrf_token
        },
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response["status"] == 200) {
                M.toast({
                    "html": "Import Started"
                }, 2000);

                show_import_progress(input_zip_file.name);
                import_timer = setInterval(track_file_import_progress, 5000);
            } else if (response["status"] == 401) {
                M.toast({
                    "html": "Some problem occured during importing zip file."
                }, 2000);
            } else if (response["status"] == 300) {
                M.toast({
                    "html": "Please upload valid zip file. Do not use .(dot) in filename except for extension."
                }, 2000);
            } else {
                M.toast({
                    "html": "Unable to import zip into existing bot. Please upload valid zip file."
                }, 2000);
            }
            
            e.target.innerHTML = 'Upload';
            e.target.disabled = false;
            $("#modal-import-bot-zip").modal("close");
            file_remove_handler('zip');
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);

            e.target.innerHTML = 'Upload';
            e.target.disabled = false;
            $("#modal-import-bot-zip").modal("close");
            file_remove_handler('zip');
            M.toast({
                "html": "Import failed"
            }, 2000);
        }
    });
});

$(document).on("click", "#import-mulitlingual-intents-excel", function(e) {

    bot_id = window.location.pathname.split('/')[3]

    e.preventDefault();
    var input_file = ($("#drag-drop-input-box-excel"))[0].files[0]

    if (input_file == null || input_file == undefined) {
        M.toast({
            "html": "Please select a file."
        }, 2000);
        return false;
    }

    if (check_malicious_file(input_file.name) == true) {
        return false;
    }

    var formData = new FormData();
    var csrf_token = $('input[name="csrfmiddlewaretoken"]').val();
    formData.append("input_file", input_file);
    formData.append("data", JSON.stringify({
        "bot_id": bot_id
    }));

    e.target.innerHTML = 'Uploading';
    e.target.disabled = true;
    $.ajax({
        url: "/chat/bot/import-mulitlingual-intents-from-excel/",
        type: "POST",
        headers: {
            'X-CSRFToken': csrf_token
        },
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response["status"] == 200) {
                M.toast({
                    "html": "Import Started"
                }, 2000);

                show_import_progress(input_file.name);
                import_timer = setInterval(track_file_import_progress, 5000);
            }
             else if (response["status"] == 101) {
                M.toast({
                    "html": response["message"]
                }, 2000);
            }  else if (response["status"] == 400) {
                M.toast({
                    "html": response["message"]
                }, 2000);
            } 
            else {
                M.toast({
                    "html": "Language fine-tuning import failed."
                }, 2000);
            }
            e.target.innerHTML = 'Upload';
            e.target.disabled = false;
            $("#modal-import-mulitlingual-intents-excel").modal("close");
            file_remove_handler('excel');

        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);

            e.target.innerHTML = 'Upload';
            e.target.disabled = false;
            $("#modal-import-mulitlingual-intents-excel").modal("close");
            file_remove_handler('excel');
            M.toast({
                "html": "Import failed"
            }, 2000);
        }
    });
});

$(document).on("click", "#import-intent-json", function(e) {

    bot_id = window.location.pathname.split('/')[3]

    e.preventDefault();
    var input_json_file = ($("#drag-drop-input-box-intent-json"))[0].files[0]

    if (input_json_file == null || input_json_file == undefined) {
        M.toast({
            "html": "Please select a file."
        }, 2000);
        return false;
    }

    if (check_malicious_file(input_json_file.name) == true) {
        return false;
    }

    var formData = new FormData();
    var csrf_token = $('input[name="csrfmiddlewaretoken"]').val();
    formData.append("input_json_file", input_json_file);
    formData.append("data", JSON.stringify({
        "bot_id": bot_id
    }));

    e.target.innerHTML = 'Uploading';
    e.target.disabled = true;
    $.ajax({
        url: "/chat/bot/import-intent/",
        type: "POST",
        headers: {
            'X-CSRFToken': csrf_token
        },
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response["status"] == 200) {
                M.toast({
                    "html": "Import started"
                }, 2000);

                show_import_progress(input_json_file.name);
                import_timer = setInterval(track_file_import_progress, 5000);
            } else if (response["status"] == 401) {
                M.toast({
                    "html": "Some problem occured during importing json file."
                }, 2000);
            } else if (response["status"] == 300) {
                M.toast({
                    "html": "Not supported file format"
                }, 2000);
            } else if (response["status"] == 301) {
                M.toast({
                    "html": "Intent already exists"
                }, 2000);
            } else {
                M.toast({
                    "html": "Unable to import intent into existing bot. Please upload valid json file."
                }, 2000);
            }

            e.target.innerHTML = 'Upload';
            e.target.disabled = false;
            $("#modal-import-intent-json").modal("close");
            file_remove_handler('intent-json');
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);

            e.target.innerHTML = 'Upload';
            e.target.disabled = false;
            $("#modal-import-intent-json").modal("close");
            file_remove_handler('intent-json');
            M.toast({
                "html": "Import failed"
            }, 2000);
        }
    });
});

function show_import_progress(filename) {
    $('#easychat_import_choices_div').hide();
    $('#easychat_import_btn_div').hide();
    $('#easychat_import_progress_file_name').html('Importing ' + filename);
    $('#easychat-import-file-progress-container').show();
}

function hide_import_progress() {
    $('#easychat_import_choices_div').show();
    $('#easychat_import_btn_div').show();
    $('#easychat-import-file-progress-container').hide();
    document.getElementById("myBar_export").innerText = "0%";
}

function show_progress_percent(filename, event_progress) {
    show_import_progress(filename);

    var elem = document.getElementById("myBar_export");
    elem.style.width = event_progress + '%';
    elem.innerHTML = event_progress + '%';
}

function track_file_import_progress() {
    var csrf_token = $('input[name="csrfmiddlewaretoken"]').val();
    bot_id = window.location.pathname.split('/')[3]

    var json_string = JSON.stringify({
        bot_id: bot_id,
        event_type: 'import_bot'
    })

    json_string = EncryptVariable(json_string)
    $.ajax({
        url: "/chat/bot/track-event-progress/",
        type: "POST",
        headers: {
            'X-CSRFToken': csrf_token
        },
        data: {
            data: json_string,
        },
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            // log to check the status of import progress
            console.log(response);
            if (response.status == 200) {
                var event_progress = response.event_progress;
                var is_completed = response.is_completed;
                var is_toast_displayed = response.is_toast_displayed;
                var is_failed = response.is_failed;
                var event_info = response.event_info;
                var failed_message = response.failed_message;

                if (is_failed && !is_toast_displayed) {
                    if (failed_message == '') failed_message = 'Import Failed'

                    show_import_toast(failed_message);
                    hide_import_progress();
                } else if (is_completed && !is_toast_displayed) {

                    show_import_toast('Imported Successfully');
                    show_progress_percent(event_info.file_uploaded, 100);

                    setTimeout(hide_import_progress, 1000)
                } else {

                    if (!is_completed && !is_failed) {
                        show_progress_percent(event_info.file_uploaded, event_progress);
                    }
                }
            } else {
                if (import_timer) {
                    clearInterval(import_timer);
                }
            }
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        }
    });
}

function show_import_toast(message) {
    M.toast({
        'html': message,
    }, 2000);
}
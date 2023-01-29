function disable_auto_pop_up_fileds(){
    let selected_language =  get_url_vars()['selected_lang']
    if(selected_language == undefined || selected_language == null){
        selected_language = "en"
    }
    if( selected_language == "en") return;
    try{
        try{
            document.getElementById("bot-popup-multiple-select-message-list").disabled = true;
        }catch(err){
          //pass
        }
        document.getElementById("is-bot-auto-popup-allowed-desktop").disabled = true;
        document.getElementById("is-bot-auto-popup-allowed-mobile").disabled = true;
        document.getElementById("bot_auto_popup_timer").disabled = true;
        document.getElementById("bot-popup-options-values").disabled = true;   
        
    }catch(err){
        //pass
    }
}


function disable_web_landing_options(){
    let selected_language =  get_url_vars()['selected_lang']
    if(selected_language == undefined || selected_language == null){
        selected_language = "en"
    }
    if( selected_language == "en") return;
    try{
        document.getElementById("add_landing_url_data").disabled = true;
        document.getElementById("select-web-landing-list").disabled = true;
        document.getElementById("show_prompt_details").disabled = true;
        var edit_web_urls = document.querySelectorAll('[id^="edit_web_url_"]');

        for (var i = 0; i < edit_web_urls.length; i++) {
            edit_web_urls[i].disabled = true;
        }
        var edit_select_list = document.querySelectorAll('[id^="edit_select_list_"]');

        for (var i = 0; i < edit_web_urls.length; i++) {
            edit_select_list[i].disabled = true;
        }
        var prompt_message_timer = document.querySelectorAll('[id^="prompt_message_timer_"]');

        for (var i = 0; i < prompt_message_timer.length; i++) {
            prompt_message_timer[i].disabled = true;
        }
        var enable_prompt_message_check_box = document.querySelectorAll('[id^="prompt_message_timer_"]');

        for (var i = 0; i < enable_prompt_message_check_box.length; i++) {
            enable_prompt_message_check_box[i].disabled = true;
        }

        document.getElementById("edit-inital-bot-messages").style.pointerEvents = "none";
        document.getElementById("add-web-landing-save-button").style.pointerEvents = "none";
        $('.delete-web-landing-svg-icon').css('pointer-events','none');
    }catch(err){
        console.log(err)
    }
}


function language_search_dropdown_event(){
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
}

function language_dropdown_close_onclicking_outside_event(){
    // Close when clicking outside
    $(document).on('click', function(event) {
        if ($(event.target).closest('.easychat-dropdown-select-custom').length === 0) {
            $('.easychat-dropdown-select-custom').removeClass('open');
            $('.easychat-dropdown-select-custom .option').removeAttr('tabindex');
        }
        event.stopPropagation();
    });
}

function open_close_language_dropdown_event(){
    $(document).on('click', '.easychat-dropdown-select-custom', function(event) {
        if ($(event.target).hasClass('dd-searchbox')) {
            return;
        }
        $('.easychat-dropdown-select-custom').not($(this)).removeClass('open');
        $(this).toggleClass('open');
        $('#txtSearchValue').val("");
        $('#modal-create-form .dd-searchbox').val("")
        $('.self-learning-create-add-intent-modal .dd-searchbox').val("")
        $(".easychat-dropdown-select-custom ul li").show();

        $('.custom-drop-nodata-found-div').hide();


        if ($(this).hasClass('open')) {
            $(this).find('.easychat-console-language-option').attr('tabindex', 0);
            $(this).find('.easychat-lang-selected').focus();
        } else {
            $(this).find('.easychat-console-language-option').removeAttr('tabindex');
            $(this).focus();
        }
    });
}

function add_channel_language_selction_event(channel_name){
    $(document).on('click', '.easychat-dropdown-select-custom .easychat-console-language-option', function(event) {
        $(this).closest('.list').find('.easychat-lang-selected').removeClass('easychat-lang-selected');
        $(this).addClass('easychat-lang-selected');

        var text = $(this).data('display-text') || $(this).text();
        $(this).closest('.easychat-dropdown-select-custom').find('.current').text(text);
        $(this).closest('.easychat-dropdown-select-custom').prev('select').val($(this).data('value')).trigger('change');
        $("#modal-language-change-loader .modal-content #language-loader-inner-text").html("Loading Channel languages")
        $('#modal-language-change-loader').modal('open');
        selected_language = $(this).data('value').trim()
        bot_id = get_url_vars()['id']
        window.location = window.location.origin+'/chat/channels/'+ channel_name +'/?id='+bot_id+"&selected_lang="+selected_language;
    });
}
function add_language_selction_event_for_edit_intent(){
    $(document).on('click', '#edit-intent-custom-drp-down .easychat-dropdown-select-custom .easychat-console-language-option', function(event) {
        $(this).closest('.list').find('.easychat-lang-selected').removeClass('easychat-lang-selected');
        $(this).addClass('easychat-lang-selected');

        var text = $(this).data('display-text') || $(this).text();
        $(this).closest('.easychat-dropdown-select-custom').find('.current-language').text(text);
        $(this).closest('.easychat-dropdown-select-custom').prev('select').val($(this).data('value')).trigger('change');
        selected_language = $(this).data('value').trim()
        check_and_update_language_intent(selected_language, INTENT_PK_FOR_INTENT_TUNING);

    });
}
function add_language_selction_event_for_intent(is_form = false){
    $(document).on('click', '#edit-intent-custom-drp-down .easychat-dropdown-select-custom .easychat-console-language-option', function(event) {
        $(this).closest('.list').find('.easychat-lang-selected').removeClass('easychat-lang-selected');
        $(this).addClass('easychat-lang-selected');

        var text = $(this).data('display-text') || $(this).text();
        $(this).closest('.easychat-dropdown-select-custom').find('.current-language').text(text);
        $(this).closest('.easychat-dropdown-select-custom').prev('select').val($(this).data('value')).trigger('change');
        selected_language = $(this).data('value').trim()
        $("#modal-language-change-loader .modal-content #language-loader-inner-text").html("Loading Intents")
        check_and_update_language(selected_language, selected_bot_obj_pk);
    });
}
function add_language_dropdown_search_event(){
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
}

function create_language_custom_dropdowns() {
    $(".easychat-console-select-drop").each(function(i, select) {
        if (!$(this).next().hasClass('easychat-dropdown-select-custom')) {
            $(this).after('<div class="easychat-dropdown-select-custom wide ' + ($(this).attr('class') || '') + '" tabindex="0"><span class="current-language"></span><div class="list"><ul></ul></div></div>');
            let dropdown = $(this).next();  
            let options = $(select).find('span');
            let selected = $(this).find('easychat-console-language-option:selected');
            dropdown.find('.current-language').html(selected.data('display-text') || selected.text());
            options.each(function(j, o) {
                let display = $(o).data('display-text') || '';
                dropdown.find('ul').append('<li class="easychat-console-language-option ' + ($(o).is(':selected') ? 'selected' : '') + '" data-value="' + $(o).data("value") + '" data-display-text="' + display + '">' + $(o).text() + '</li>');
            });
        }

    });
    $('.easychat-dropdown-select-custom ul li:last').after('<div class="custom-drop-nodata-found-div">No result found</div> ');
    $('.easychat-dropdown-select-custom ul').before('<div class="dd-search"> <svg class="drop-language-search-icon" width="15" height="14" viewBox="0 0 15 14" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M13.1875 12.0689L9.88352 8.76489C10.6775 7.81172 11.0734 6.58914 10.9889 5.35148C10.9045 4.11382 10.3461 2.95638 9.42994 2.11993C8.51381 1.28349 7.31047 0.83244 6.07025 0.86062C4.83003 0.8888 3.64842 1.39404 2.77123 2.27123C1.89404 3.14842 1.3888 4.33003 1.36062 5.57025C1.33244 6.81047 1.78349 8.01381 2.61993 8.92994C3.45638 9.84607 4.61382 10.4045 5.85148 10.4889C7.08914 10.5734 8.31172 10.1775 9.26489 9.38352L12.5689 12.6875L13.1875 12.0689ZM2.25002 5.68752C2.25002 4.90876 2.48095 4.14748 2.91361 3.49996C3.34627 2.85244 3.96122 2.34776 4.6807 2.04974C5.40019 1.75172 6.19189 1.67375 6.95569 1.82568C7.71949 1.97761 8.42108 2.35262 8.97175 2.90329C9.52242 3.45396 9.89743 4.15555 10.0494 4.91935C10.2013 5.68315 10.1233 6.47485 9.8253 7.19433C9.52728 7.91382 9.0226 8.52877 8.37508 8.96143C7.72756 9.39409 6.96628 9.62502 6.18752 9.62502C5.14358 9.62386 4.14274 9.20865 3.40457 8.47047C2.66639 7.7323 2.25118 6.73145 2.25002 5.68752Z" fill="#909090"/></svg><input id="txtSearchValue" autocomplete="off" placeholder="Search Language" onkeyup="filter_languages_in_channel_dropdown()" class="dd-searchbox" type="text"></div>');
    $('.easychat-dropdown-select-custom span').before(' <svg class="drop-language-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"> <rect width="24" height="24" fill="white"/><path fill-rule="evenodd" clip-rule="evenodd" d="M8.62477 3C8.92313 3 9.20927 3.11832 9.42024 3.32894C9.63121 3.53955 9.74973 3.82521 9.74973 4.12306V5.24612H13.1246C13.4229 5.24612 13.7091 5.36444 13.9201 5.57506C14.131 5.78567 14.2495 6.07133 14.2495 6.36918C14.2495 6.66703 14.131 6.95269 13.9201 7.1633C13.7091 7.37392 13.4229 7.49224 13.1246 7.49224H11.5249C11.1238 9.36076 10.4714 11.1665 9.58549 12.8605C9.91172 13.258 10.256 13.6421 10.6137 14.0127C10.7163 14.1189 10.7969 14.2442 10.851 14.3815C10.9051 14.5188 10.9316 14.6654 10.9289 14.8129C10.9262 14.9605 10.8945 15.106 10.8355 15.2413C10.7765 15.3765 10.6914 15.4989 10.585 15.6013C10.4786 15.7037 10.3531 15.7842 10.2156 15.8382C10.078 15.8922 9.9312 15.9186 9.78344 15.916C9.63568 15.9133 9.48989 15.8816 9.3544 15.8227C9.2189 15.7638 9.09636 15.6788 8.99376 15.5727C8.78227 15.3525 8.57415 15.1279 8.37053 14.8988C7.37625 16.3736 6.20217 17.7192 4.8753 18.9048C4.65254 19.1002 4.36149 19.1999 4.06547 19.1822C3.76945 19.1645 3.49241 19.0308 3.2946 18.8103C3.09679 18.5897 2.99423 18.3001 3.00921 18.0044C3.02419 17.7087 3.15551 17.4309 3.37461 17.2314C4.74286 16.009 5.92861 14.5972 6.89572 13.039C6.26734 12.1494 5.7081 11.213 5.22291 10.2381C5.15171 10.1056 5.10791 9.96011 5.09409 9.81035C5.08028 9.66059 5.09674 9.50958 5.14249 9.36629C5.18824 9.223 5.26236 9.09034 5.36044 8.97618C5.45852 8.86203 5.57857 8.76871 5.71347 8.70175C5.84836 8.63479 5.99535 8.59556 6.14572 8.58639C6.29609 8.57722 6.44678 8.5983 6.58883 8.64837C6.73089 8.69844 6.86142 8.77648 6.97269 8.87787C7.08396 8.97926 7.1737 9.10193 7.23658 9.2386C7.49982 9.76644 7.78668 10.2808 8.09605 10.7794C8.56515 9.7305 8.94201 8.63102 9.21762 7.49224H4.12495C3.8266 7.49224 3.54046 7.37392 3.32949 7.1633C3.11852 6.95269 3 6.66703 3 6.36918C3 6.07133 3.11852 5.78567 3.32949 5.57506C3.54046 5.36444 3.8266 5.24612 4.12495 5.24612H7.49982V4.12306C7.49982 3.82521 7.61834 3.53955 7.82931 3.32894C8.04028 3.11832 8.32642 3 8.62477 3ZM15.3745 9.73836C15.5834 9.73847 15.7881 9.79663 15.9657 9.90632C16.1433 10.016 16.2869 10.1729 16.3802 10.3594L19.745 17.0776C19.7528 17.0912 19.7603 17.1051 19.7675 17.1191L20.8812 19.3428C21.0147 19.6093 21.0366 19.918 20.9422 20.2007C20.8478 20.4835 20.6448 20.7172 20.3777 20.8505C20.1107 20.9838 19.8016 21.0057 19.5184 20.9114C19.2351 20.8172 19.001 20.6145 18.8675 20.3479L18.0553 18.7228H12.696L11.8815 20.3479C11.8183 20.4844 11.7283 20.6069 11.6168 20.7081C11.5053 20.8092 11.3746 20.887 11.2325 20.9368C11.0903 20.9865 10.9395 21.0073 10.7892 20.9978C10.6388 20.9883 10.4919 20.9487 10.3572 20.8814C10.2224 20.8142 10.1026 20.7206 10.0047 20.6062C9.90691 20.4918 9.83309 20.359 9.78767 20.2156C9.74224 20.0722 9.72613 19.9211 9.74029 19.7714C9.75445 19.6216 9.79859 19.4763 9.8701 19.3439L10.9838 17.1202L11.0052 17.0776L14.3688 10.3594C14.4622 10.1729 14.6057 10.016 14.7833 9.90632C14.9609 9.79663 15.1656 9.73847 15.3745 9.73836ZM13.8198 16.4767H16.9292L15.2807 12.4524L13.8198 16.4767Z" fill="#4B4B4B"/></svg>');

    let selected_language =  get_url_vars()['selected_lang']
    if(selected_language == undefined || selected_language == null){
        selected_language = "en"
    }
    let el = $(".easychat-dropdown-select-custom ul ").find(`[data-value='${selected_language}']`)
    el.addClass('easychat-lang-selected')
    let default_select_lang_drop = el.text()
    $('.current-language').html(default_select_lang_drop);

}
function filter_languages_in_channel_dropdown(){
    var valThis = $('#txtSearchValue').val();
    $('.easychat-dropdown-select-custom ul > li').each(function() {
        var text = $(this).text();
        (text.toLowerCase().indexOf(valThis.toLowerCase()) > -1) ? $(this).show(): $(this).hide();
        if ($('.easychat-dropdown-select-custom ul').children(':visible').not('.custom-drop-nodata-found-div').length === 0) {
            $('.custom-drop-nodata-found-div').show();
        } else {
            $('.custom-drop-nodata-found-div').hide();
        }
    });
}

function get_url_vars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m, key, value) {
        vars[key] = value;
    });
    return vars;
}

function create_language_custom_dropdowns_for_intent() {
    $("#edit-intent-custom-drp-down .easychat-console-select-drop").each(function(i, select) {
        if (!$(this).next().hasClass('easychat-dropdown-select-custom')) {
            $(this).after('<div class="easychat-dropdown-select-custom wide ' + ($(this).attr('class') || '') + '" tabindex="0"><span class="current-language"></span><div class="list"><ul></ul></div></div>');
            let dropdown = $(this).next();  
            let options = $(select).find('span');
            let selected = $(this).find('easychat-console-language-option:selected');
            dropdown.find('.current-language').html(selected.data('display-text') || selected.text());
            options.each(function(j, o) {
                let display = $(o).data('display-text') || '';
                dropdown.find('ul').append('<li class="easychat-console-language-option ' + ($(o).is(':selected') ? 'selected' : '') + '" data-value="' + $(o).data("value") + '" data-display-text="' + display + '">' + $(o).text() + '</li>');
            });
        }

    });
    $('#edit-intent-custom-drp-down .easychat-dropdown-select-custom ul li:last').after('<div class="custom-drop-nodata-found-div">No result found</div> ');
    $('#edit-intent-custom-drp-down .easychat-dropdown-select-custom ul').before('<div class="dd-search"> <svg class="drop-language-search-icon" width="15" height="14" viewBox="0 0 15 14" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M13.1875 12.0689L9.88352 8.76489C10.6775 7.81172 11.0734 6.58914 10.9889 5.35148C10.9045 4.11382 10.3461 2.95638 9.42994 2.11993C8.51381 1.28349 7.31047 0.83244 6.07025 0.86062C4.83003 0.8888 3.64842 1.39404 2.77123 2.27123C1.89404 3.14842 1.3888 4.33003 1.36062 5.57025C1.33244 6.81047 1.78349 8.01381 2.61993 8.92994C3.45638 9.84607 4.61382 10.4045 5.85148 10.4889C7.08914 10.5734 8.31172 10.1775 9.26489 9.38352L12.5689 12.6875L13.1875 12.0689ZM2.25002 5.68752C2.25002 4.90876 2.48095 4.14748 2.91361 3.49996C3.34627 2.85244 3.96122 2.34776 4.6807 2.04974C5.40019 1.75172 6.19189 1.67375 6.95569 1.82568C7.71949 1.97761 8.42108 2.35262 8.97175 2.90329C9.52242 3.45396 9.89743 4.15555 10.0494 4.91935C10.2013 5.68315 10.1233 6.47485 9.8253 7.19433C9.52728 7.91382 9.0226 8.52877 8.37508 8.96143C7.72756 9.39409 6.96628 9.62502 6.18752 9.62502C5.14358 9.62386 4.14274 9.20865 3.40457 8.47047C2.66639 7.7323 2.25118 6.73145 2.25002 5.68752Z" fill="#909090"/></svg><input id="txtSearchValue" autocomplete="off" placeholder="Search Language" onkeyup="filter_languages_in_channel_dropdown()" class="dd-searchbox" type="text"></div>');
    $('#edit-intent-custom-drp-down .easychat-dropdown-select-custom span').before(' <svg class="drop-language-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"> <rect width="24" height="24" fill="white"/><path fill-rule="evenodd" clip-rule="evenodd" d="M8.62477 3C8.92313 3 9.20927 3.11832 9.42024 3.32894C9.63121 3.53955 9.74973 3.82521 9.74973 4.12306V5.24612H13.1246C13.4229 5.24612 13.7091 5.36444 13.9201 5.57506C14.131 5.78567 14.2495 6.07133 14.2495 6.36918C14.2495 6.66703 14.131 6.95269 13.9201 7.1633C13.7091 7.37392 13.4229 7.49224 13.1246 7.49224H11.5249C11.1238 9.36076 10.4714 11.1665 9.58549 12.8605C9.91172 13.258 10.256 13.6421 10.6137 14.0127C10.7163 14.1189 10.7969 14.2442 10.851 14.3815C10.9051 14.5188 10.9316 14.6654 10.9289 14.8129C10.9262 14.9605 10.8945 15.106 10.8355 15.2413C10.7765 15.3765 10.6914 15.4989 10.585 15.6013C10.4786 15.7037 10.3531 15.7842 10.2156 15.8382C10.078 15.8922 9.9312 15.9186 9.78344 15.916C9.63568 15.9133 9.48989 15.8816 9.3544 15.8227C9.2189 15.7638 9.09636 15.6788 8.99376 15.5727C8.78227 15.3525 8.57415 15.1279 8.37053 14.8988C7.37625 16.3736 6.20217 17.7192 4.8753 18.9048C4.65254 19.1002 4.36149 19.1999 4.06547 19.1822C3.76945 19.1645 3.49241 19.0308 3.2946 18.8103C3.09679 18.5897 2.99423 18.3001 3.00921 18.0044C3.02419 17.7087 3.15551 17.4309 3.37461 17.2314C4.74286 16.009 5.92861 14.5972 6.89572 13.039C6.26734 12.1494 5.7081 11.213 5.22291 10.2381C5.15171 10.1056 5.10791 9.96011 5.09409 9.81035C5.08028 9.66059 5.09674 9.50958 5.14249 9.36629C5.18824 9.223 5.26236 9.09034 5.36044 8.97618C5.45852 8.86203 5.57857 8.76871 5.71347 8.70175C5.84836 8.63479 5.99535 8.59556 6.14572 8.58639C6.29609 8.57722 6.44678 8.5983 6.58883 8.64837C6.73089 8.69844 6.86142 8.77648 6.97269 8.87787C7.08396 8.97926 7.1737 9.10193 7.23658 9.2386C7.49982 9.76644 7.78668 10.2808 8.09605 10.7794C8.56515 9.7305 8.94201 8.63102 9.21762 7.49224H4.12495C3.8266 7.49224 3.54046 7.37392 3.32949 7.1633C3.11852 6.95269 3 6.66703 3 6.36918C3 6.07133 3.11852 5.78567 3.32949 5.57506C3.54046 5.36444 3.8266 5.24612 4.12495 5.24612H7.49982V4.12306C7.49982 3.82521 7.61834 3.53955 7.82931 3.32894C8.04028 3.11832 8.32642 3 8.62477 3ZM15.3745 9.73836C15.5834 9.73847 15.7881 9.79663 15.9657 9.90632C16.1433 10.016 16.2869 10.1729 16.3802 10.3594L19.745 17.0776C19.7528 17.0912 19.7603 17.1051 19.7675 17.1191L20.8812 19.3428C21.0147 19.6093 21.0366 19.918 20.9422 20.2007C20.8478 20.4835 20.6448 20.7172 20.3777 20.8505C20.1107 20.9838 19.8016 21.0057 19.5184 20.9114C19.2351 20.8172 19.001 20.6145 18.8675 20.3479L18.0553 18.7228H12.696L11.8815 20.3479C11.8183 20.4844 11.7283 20.6069 11.6168 20.7081C11.5053 20.8092 11.3746 20.887 11.2325 20.9368C11.0903 20.9865 10.9395 21.0073 10.7892 20.9978C10.6388 20.9883 10.4919 20.9487 10.3572 20.8814C10.2224 20.8142 10.1026 20.7206 10.0047 20.6062C9.90691 20.4918 9.83309 20.359 9.78767 20.2156C9.74224 20.0722 9.72613 19.9211 9.74029 19.7714C9.75445 19.6216 9.79859 19.4763 9.8701 19.3439L10.9838 17.1202L11.0052 17.0776L14.3688 10.3594C14.4622 10.1729 14.6057 10.016 14.7833 9.90632C14.9609 9.79663 15.1656 9.73847 15.3745 9.73836ZM13.8198 16.4767H16.9292L15.2807 12.4524L13.8198 16.4767Z" fill="#4B4B4B"/></svg>');

    let selected_language = SELECTED_LANGUAGE
    let el = $("#edit-intent-custom-drp-down .easychat-dropdown-select-custom ul ").find(`[data-value='${selected_language}']`)
    el.addClass('easychat-lang-selected')
    let default_select_lang_drop = el.text()
    $('.current-language').html(default_select_lang_drop);

}


function check_selected_language_is_supported(selected_language, bot_pk){

    let final_selected_language = selected_language
    try{
        var json_string = JSON.stringify({
            selected_language: selected_language,
            bot_pk: bot_pk
        })
        json_string = EncryptVariable(json_string);
        json_string = encodeURIComponent(json_string);

        var xhttp = new XMLHttpRequest();
        var params = 'json_string=' + json_string
        xhttp.open("POST", "/chat/check-selected-language-is-supported/", false);
        xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = custom_decrypt(response)
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    final_selected_language =selected_language
                }else if (response["status"] == 301) {
                    final_selected_language = response["default_language"]
                    M.toast({
                        "html": "Selected Language is not Supported. Please refresh the Page"
                    }, 1000);
                    $("#modal-language-change-loader").modal('close')
                }else {
                    final_selected_language = response["default_language"]
                    M.toast({
                        "html": "Unable to get requested Data. Please refresh the Page"
                    }, 1000);
                    $("#modal-language-change-loader").modal('close')
                }
            }
        }
        xhttp.send(params);
    }catch(err){
        final_selected_language = "en"
    }
    return final_selected_language
}
function check_and_update_language(selected_language, bot_pk) {

    $("#modal-language-change-loader").modal('open')
    selected_language = check_selected_language_is_supported(selected_language,bot_pk)
    window.location = set_url_parameter("selected_language", selected_language)
   
}


function check_and_update_language_intent(selected_language, intent_pk) {

    
    
    $("#modal-language-change-loader").modal('open')
    $("#language-loader-inner-text").html("Loading Intent")
    selected_language = check_selected_language_is_supported(selected_language,SELECTED_BOT_PK)
    var json_string = JSON.stringify({
        selected_language: selected_language,
        intent_pk: intent_pk
    })
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var xhttp = new XMLHttpRequest();
    var params = 'json_string=' + json_string
    xhttp.open("POST", "/chat/update-selected-language-intent/", false);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {

                window.location = window.location.origin + "/chat/edit-intent-multilingual/?intent_pk=" + intent_pk + "&selected_language=" + selected_language;
            } else {

                M.toast({
                    "html": "Unable to get requested data. Please try after sometime."
                }, 1000);
                $("#modal-language-change-loader").modal('close')
            }
        }
    }
    xhttp.send(params);
}

////// form edit-intent

 var input_types = ["Text Field", "Dropdown list", "Checkbox", "Radio Button", "Range Slider", "File Attach", "Date Picker","Time Picker"]
 var validator_types = ["Choose Validator", "6 Digit OTP Validator", "4 Digit OTP Validator", "Email Validator", "PAN Validator", "Name Validator"]
 var range_types = ["Single Range Selector","Dual Range Selector"]
 var attachment_types = ["image(ex. .jpeg, .png, .jpg)", "video file(ex. .mp4)","word processor(i.e. .doc,.pdf)","compressed file(ex. .zip)"]
 var calendar_types = ["Single Type","Custom Type"]
 function create_custom_dropdowns_form_widgets(className, field_id, input_type="", validator="", placeholder_or_options,range="",calendar_type="") {
     var selected_input_type = 0
     var selected_validator_type = 0 
     var selected_range_type = 0 
     var selected_file_attach = 0 
     var selected_calendar_type = 0
     if (input_type != "") {
         selected_input_type = input_types.indexOf(input_type)
     }

     if(validator != "")
     {
        selected_validator_type = validator_types.indexOf(validator)
     }

     if(range != "")
     {
        selected_range_type = range_types.indexOf(range)
     }

     if(input_type == "File Attach")
     {
        selected_file_attach = attachment_types.indexOf(placeholder_or_options)
     }

     if(calendar_type != "")
     {
        selected_calendar_type = calendar_types.indexOf(calendar_type)
     }
     $("#" + className + " .easychat-console-select-drop").each(function(i, select) {
         if (!$(this).next().hasClass('easychat-dropdown-select-custom')) {
             $(this).after('<div style="margin-bottom: 5px;" id="easychat-dropdown-select-custom-' + i + '-' + field_id + '" class="easychat-dropdown-select-custom wide ' + ($(this).attr('class') || '') + '" tabindex="' + field_id + '"><span class="current" id="current-' + i + '-' + field_id + '"></span><div class="list"><ul></ul></div></div>');
             var dropdown = $(this).next();

             var options = $(select).find('span');

             var selected = $(this).find('easychat-console-language-option:selected');

             dropdown.find('#current-' + i + '-' + field_id).html(selected.data('display-text') || selected.text());
             options.each(function(j, o) {


                 var display = $(o).data('display-text') || '';
                 dropdown.find('ul').append('<li class="easychat-console-language-option ' + ($(o).is(':selected') ? 'selected' : '') + '" id="easychat-console-language-option-' + i + '-' + field_id + '" data-value="' + $(o).data("value") + '" data-display-text="' + display + '">' + $(o).text() + '</li>');
             });
         }

        $('#modal-create-form '+' #easychat-dropdown-select-custom-' + i + '-' + field_id + '  ul li:last').after('<div class="custom-drop-nodata-found-div">No result found</div> ');
         $("#" + className + ' #easychat-dropdown-select-custom-' + i + '-' + field_id + ' ul').before(`<div class="dd-search"> <svg class="drop-language-search-icon" width="15" height="14" viewBox="0 0 15 14" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M13.1875 12.0689L9.88352 8.76489C10.6775 7.81172 11.0734 6.58914 10.9889 5.35148C10.9045 4.11382 10.3461 2.95638 9.42994 2.11993C8.51381 1.28349 7.31047 0.83244 6.07025 0.86062C4.83003 0.8888 3.64842 1.39404 2.77123 2.27123C1.89404 3.14842 1.3888 4.33003 1.36062 5.57025C1.33244 6.81047 1.78349 8.01381 2.61993 8.92994C3.45638 9.84607 4.61382 10.4045 5.85148 10.4889C7.08914 10.5734 8.31172 10.1775 9.26489 9.38352L12.5689 12.6875L13.1875 12.0689ZM2.25002 5.68752C2.25002 4.90876 2.48095 4.14748 2.91361 3.49996C3.34627 2.85244 3.96122 2.34776 4.6807 2.04974C5.40019 1.75172 6.19189 1.67375 6.95569 1.82568C7.71949 1.97761 8.42108 2.35262 8.97175 2.90329C9.52242 3.45396 9.89743 4.15555 10.0494 4.91935C10.2013 5.68315 10.1233 6.47485 9.8253 7.19433C9.52728 7.91382 9.0226 8.52877 8.37508 8.96143C7.72756 9.39409 6.96628 9.62502 6.18752 9.62502C5.14358 9.62386 4.14274 9.20865 3.40457 8.47047C2.66639 7.7323 2.25118 6.73145 2.25002 5.68752Z" fill="#909090"/></svg><input id="txtSearchValue-` + i + `-` + field_id + `" autocomplete="off" placeholder="Search" onkeyup="form_widget_filter(` + i + `,` + field_id + `)" class="dd-searchbox" type="text"></div>`);

         if(i==0)
            $("#" + className + " #easychat-dropdown-select-custom-" + i + "-" + field_id + " ul li:eq(" + selected_input_type + ")").addClass('easychat-lang-selected');
        else if(i == 1)
        {
            $("#" + className + " #easychat-dropdown-select-custom-" + i + "-" + field_id + " ul li:eq(" + selected_validator_type + ")").addClass('easychat-lang-selected');

        } else if(i == 2)
        {
           $("#" + className + " #easychat-dropdown-select-custom-" + i + "-" + field_id + " ul li:eq(" + selected_file_attach + ")").addClass('easychat-lang-selected');

        } 
        else if(i == 3)
        {
            $("#" + className + " #easychat-dropdown-select-custom-" + i + "-" + field_id + " ul li:eq(" + selected_range_type + ")").addClass('easychat-lang-selected');

        } else if(i == 4)
        {
            $("#" + className + " #easychat-dropdown-select-custom-" + i + "-" + field_id + " ul li:eq(" + selected_calendar_type + ")").addClass('easychat-lang-selected');
        }
         var default_select_lang_drop = $("#" + className + ' #easychat-dropdown-select-custom-' + i + '-' + field_id + ' ul li:first').text();
         if (input_type != "" && i == 0) {
             default_select_lang_drop = input_type

                if (input_type == "Checkbox") {
                 document.getElementById("sortable-checkbox-widget-edit-div-" + field_id).style.display = "block"
                 document.getElementById('input_selected_type_' + field_id + '_3').placeholder = "Enter any value or text and hit \"Enter\""
                 document.getElementById('input_selected_type_' + field_id + '_3').style.display = "inline-block"
             }

             if (input_type == "Radio Button") {
                 document.getElementById("sortable-radio-widget-edit-div-" + field_id).style.display = "block"
                 document.getElementById('input_selected_type_' + field_id + '_3').placeholder = "Enter any value or text and hit \"Enter\""
                 document.getElementById('input_selected_type_' + field_id + '_3').style.display = "inline-block"
             }


             if (input_type == "Dropdown list") {
                 document.getElementById("sortable-dropdown-widget-edit-div-" + field_id).style.display = "flex"
                 document.getElementById('input_selected_type_' + field_id + '_3').placeholder = "Enter any value or text and hit \"Enter\""
                 document.getElementById('input_selected_type_' + field_id + '_3').style.display = "block"
             }

             if (input_type == "File Attach") {
             document.getElementById('file_attach_' + field_id).style.display = "inline-block"
             document.getElementById('input_selected_type_' + field_id + '_3').style.display = "block"
             document.getElementById('input_selected_type_' + field_id + "_3").style.visibility = "hidden"

             }

             if (input_type == "Range Slider") {
                 document.getElementById("range_type_"+field_id).style.display = "block"
                 document.getElementById("form-widget-range-slider-min-max-container" + field_id).style.display = "block";
                 document.getElementById('input_selected_type_' + field_id + '_3').style.display = "none"

             }
            
             if(input_type == "Date Picker" || input_type == "Time Picker")
             {
                document.getElementById('calendar_type_'+field_id).style.display = "inline-block"
               document.getElementById('input_selected_type_' + field_id + '_3').style.display = "block";
                document.getElementById('input_selected_type_' + field_id+'_3').style.visibility = "hidden";
                                
             }
         }
         if (validator != "" && i == 1) {
             if (input_type == "Text Field") {
                 document.getElementById("validator_dropdown_" + field_id).style.display = "block"
                 default_select_lang_drop = validator
             } 
         }

         if (placeholder_or_options != "" && i == 2) {
             if (input_type == "File Attach") {
                 document.getElementById("file_attach_" + field_id).style.display = "block"
                 document.getElementById('input_selected_type_' + field_id + '_3').style.display = "block"
                 document.getElementById('input_selected_type_' + field_id + '_3').style.visibility = "hidden"
                 default_select_lang_drop = placeholder_or_options
             } 
         }

         if (range != "" && i == 3) {
             if (input_type == "Range Slider") {
                 document.getElementById("range_type_" + field_id).style.display = "block"
                 document.getElementById('input_selected_type_' + field_id + '_3').style.display = "none"
                 default_select_lang_drop = range
             } 
         }

         if(calendar_type != "" && i == 4)
         {if (input_type == "Date Picker" || input_type == "Time Picker") {
                 document.getElementById("calendar_type_" + field_id).style.display = "block"
                 document.getElementById('input_selected_type_' + field_id + '_3').style.display = "block"
                 document.getElementById('input_selected_type_' + field_id + '_3').style.visibility = "hidden"
                 default_select_lang_drop = calendar_type
             } 

         }


         $("#" + className + ' #current-' + i + '-' + field_id).html(default_select_lang_drop);
     });



 }

 function form_widget_filter(i, field_id) {

     var id = '#txtSearchValue-' + i + '-' + field_id
     var valThis = $(id).val();
     $('#easychat-dropdown-select-custom-' + i + '-' + field_id + ' ul > li').each(function() {
         var text = $(this).text();
         (text.toLowerCase().indexOf(valThis.toLowerCase()) > -1) ? $(this).show(): $(this).hide();
        if ($('#modal-create-form'+ ' #easychat-dropdown-select-custom-' + i + '-' + field_id + ' ul').children(':visible').not('#modal-create-form .custom-drop-nodata-found-div').length === 0) {
            $('#modal-create-form .custom-drop-nodata-found-div').show();
        } else {
            $('#modal-create-form .custom-drop-nodata-found-div').hide();
        }

        if ($('.self-learning-create-add-intent-modal'+ ' #easychat-dropdown-select-custom-' + i + '-' + field_id + ' ul').children(':visible').not('.self-learning-create-add-intent-modal .custom-drop-nodata-found-div').length === 0) {
            $('.self-learning-create-add-intent-modal .custom-drop-nodata-found-div').show();
        } else {
            $('.self-learning-create-add-intent-modal .custom-drop-nodata-found-div').hide();
        }
     });
 };
 // Search

 // Option click
 function select_option_for_form_widgets() {
     $(document).on('click', '#modal-create-form .easychat-dropdown-select-custom .easychat-console-language-option', function(event) {

         $(this).closest('.list').find('.easychat-lang-selected').removeClass('easychat-lang-selected');
         $(this).addClass('easychat-lang-selected');

         var text = $(this).data('display-text') || $(this).text();
         $(this).closest('.easychat-dropdown-select-custom').find('.current').text(text);
         $(this).closest('.easychat-dropdown-select-custom').prev('select').val($(this).data('value')).trigger('change');

         update_form_widget(event, this)
     });
 }

 function update_form_widget(event, elem) {

     var is_input_type_change = elem.id.split("-")[4]
     var field_id = elem.id.split("-")[5]

     if (is_input_type_change == 0) {
         //text input
         if ($(elem).data('value') == 'text_field') {
             document.getElementById("validator_dropdown_" + field_id).style.display = "block"
             document.getElementById('input_selected_type_' + field_id + '_3').placeholder = "placeholder text"
              document.getElementById('input_selected_type_' + field_id + "_3").style.display = "inline-block"

             // remove_radio
             document.getElementById("sortable-radio-widget-edit-div-" + field_id).style.display = "none"
             document.getElementById("sortable-radio-widget-edit-div-" + field_id).innerHTML = ""
             document.getElementById("new_bot_error_div_widgets_" + field_id).innerHTML = ""

             //remove checkbox
             document.getElementById("sortable-checkbox-widget-edit-div-" + field_id).style.display = "none"
             document.getElementById("sortable-checkbox-widget-edit-div-" + field_id).innerHTML = ""

             //remove dropdown
             document.getElementById("sortable-dropdown-widget-edit-div-" + field_id).style.display = "none"
             document.getElementById("sortable-dropdown-widget-edit-div-" + field_id).innerHTML = ""

             //remove file attach
             document.getElementById('file_attach_' + field_id).style.display = "none"
             document.getElementById('input_selected_type_' + field_id + "_3").style.visibility = "visible"

             //remove range slider
             document.getElementById("form-widget-range-slider-min-max-container" + field_id).style.display = "none";

             //remove date or time picker
             document.getElementById("calendar_type_" + field_id).style.display = "none"

         } else if ($(elem).data('value') == "radio") {

             document.getElementById('input_selected_type_' + field_id + '_3').style.display = "inline-block"
             document.getElementById("sortable-radio-widget-edit-div-" + field_id).style.display = "block"
             document.getElementById('input_selected_type_' + field_id + '_3').value = ""
             document.getElementById('input_selected_type_' + field_id + '_3').placeholder = "Enter any value or text and hit \"Enter\""

             // remove input
             document.getElementById("validator_dropdown_" + field_id).style.display = "none"
             //remove checkbox
             document.getElementById("sortable-checkbox-widget-edit-div-" + field_id).style.display = "none"
             document.getElementById("sortable-checkbox-widget-edit-div-" + field_id).innerHTML = ""
             document.getElementById("new_bot_error_div_widgets_" + field_id).innerHTML = ""

             //remove dropdown
             document.getElementById("sortable-dropdown-widget-edit-div-" + field_id).style.display = "none"
             document.getElementById("sortable-dropdown-widget-edit-div-" + field_id).innerHTML = ""
             //remove file attach
             document.getElementById('file_attach_' + field_id).style.display = "none"
             document.getElementById('input_selected_type_' + field_id + "_3").style.visibility = "visible"

             //remove range slider
             document.getElementById("form-widget-range-slider-min-max-container" + field_id).style.display = "none";
             document.getElementById("range_type_" + field_id).style.display = "none"

             //remove date or time picker
             document.getElementById("calendar_type_" + field_id).style.display = "none"

         } else if ($(elem).data('value') == "checkbox") {
             document.getElementById("sortable-checkbox-widget-edit-div-" + field_id).style.display = "block"
             document.getElementById('input_selected_type_' + field_id + '_3').value = "";
             document.getElementById('input_selected_type_' + field_id + '_3').placeholder = "Enter any value or text and hit \"Enter\""
              document.getElementById('input_selected_type_' + field_id + '_3').style.display = "inline-block"

             //remove input
             document.getElementById("validator_dropdown_" + field_id).style.display = "none"
             // remove_radio
             document.getElementById("sortable-radio-widget-edit-div-" + field_id).style.display = "none"
             document.getElementById("sortable-radio-widget-edit-div-" + field_id).innerHTML = ""
             document.getElementById("new_bot_error_div_widgets_" + field_id).innerHTML = ""

             //remove dropdown
             document.getElementById("sortable-dropdown-widget-edit-div-" + field_id).style.display = "none"
             document.getElementById("sortable-dropdown-widget-edit-div-" + field_id).innerHTML = ""
             //remove file attach
             document.getElementById('file_attach_' + field_id).style.display = "none"
             document.getElementById('input_selected_type_' + field_id + "_3").style.visibility = "visible"

             //remove range slider
             document.getElementById("form-widget-range-slider-min-max-container" + field_id).style.display = "none";
             document.getElementById("range_type_" + field_id).style.display = "none"

             //remove date or time picker
             document.getElementById("calendar_type_" + field_id).style.display = "none"


         } else if ($(elem).data('value') == "dropdown_list") {
             document.getElementById("sortable-dropdown-widget-edit-div-" + field_id).style.display = "flex"
             document.getElementById('input_selected_type_' + field_id + '_3').value = "";
             document.getElementById('input_selected_type_' + field_id + '_3').placeholder = "Enter any value or text and hit \"Enter\""
              document.getElementById('input_selected_type_' + field_id + '_3').style.display = "block"

             //remove input
             document.getElementById("validator_dropdown_" + field_id).style.display = "none"
             // remove_radio
             document.getElementById("sortable-radio-widget-edit-div-" + field_id).style.display = "none"
             document.getElementById("sortable-radio-widget-edit-div-" + field_id).innerHTML = ""
             document.getElementById("new_bot_error_div_widgets_" + field_id).innerHTML = ""

             //remove checkbox
             document.getElementById("sortable-checkbox-widget-edit-div-" + field_id).style.display = "none"
             document.getElementById("sortable-checkbox-widget-edit-div-" + field_id).innerHTML = ""

             //remove file attach
             document.getElementById('file_attach_' + field_id).style.display = "none"
             document.getElementById('input_selected_type_' + field_id + "_3").style.visibility = "visible"

             //remove range slider
             document.getElementById("form-widget-range-slider-min-max-container" + field_id).style.display = "none";
             document.getElementById("range_type_" + field_id).style.display = "none"


             document.getElementById('input_selected_type_' + field_id + "_3").style.display = "block"

             //remove date or time picker
             document.getElementById("calendar_type_" + field_id).style.display = "none"

         } else if ($(elem).data('value') == "file_attach") {

             document.getElementById('file_attach_' + field_id).style.display = "inline-block"
             document.getElementById('input_selected_type_' + field_id + '_3').style.display = "block"
             document.getElementById('input_selected_type_' + field_id + "_3").style.visibility = "hidden"

             //remove input
             document.getElementById("validator_dropdown_" + field_id).style.display = "none"
             // remove_radio
             document.getElementById("sortable-radio-widget-edit-div-" + field_id).style.display = "none"
             document.getElementById("sortable-radio-widget-edit-div-" + field_id).innerHTML = ""
             document.getElementById("new_bot_error_div_widgets_" + field_id).innerHTML = ""

             //remove checkbox
             document.getElementById("sortable-checkbox-widget-edit-div-" + field_id).style.display = "none"
             document.getElementById("sortable-checkbox-widget-edit-div-" + field_id).innerHTML = ""

             //remove dropdown
             document.getElementById("sortable-dropdown-widget-edit-div-" + field_id).style.display = "none"
             document.getElementById("sortable-dropdown-widget-edit-div-" + field_id).innerHTML = ""

             //remove range slider
             document.getElementById("form-widget-range-slider-min-max-container" + field_id).style.display = "none";
             document.getElementById("range_type_" + field_id).style.display = "none"

             //remove date or time picker
             document.getElementById("calendar_type_" + field_id).style.display = "none"


         } else if ($(elem).data('value') == "range") {
              document.getElementById('range_type_' + field_id).style.display = "block"
             document.getElementById("form-widget-range-slider-min-max-container" + field_id).style.display = "block";

             //remove input
             document.getElementById("validator_dropdown_" + field_id).style.display = "none"
             document.getElementById('input_selected_type_' + field_id + '_3').style.display = "none"

             // remove_radio
             document.getElementById("sortable-radio-widget-edit-div-" + field_id).style.display = "none"
             document.getElementById("sortable-radio-widget-edit-div-" + field_id).innerHTML = ""
             document.getElementById("new_bot_error_div_widgets_" + field_id).innerHTML = ""

             //remove checkbox
             document.getElementById("sortable-checkbox-widget-edit-div-" + field_id).style.display = "none"
             document.getElementById("sortable-checkbox-widget-edit-div-" + field_id).innerHTML = ""

             //remove dropdown
             document.getElementById("sortable-dropdown-widget-edit-div-" + field_id).style.display = "none"
             document.getElementById("sortable-dropdown-widget-edit-div-" + field_id).innerHTML = ""

             //remove file attach
             document.getElementById('file_attach_' + field_id).style.display = "none"
             document.getElementById('input_selected_type_' + field_id + "_3").style.visibility = "visible"

             //remove date or time picker
             document.getElementById("calendar_type_" + field_id).style.display = "none"
            
         } else if(($(elem).data('value') == "date_picker") || ($(elem).data('value') == "time_picker"))
         {
            document.getElementById("calendar_type_" + field_id).style.display = "block"
                 document.getElementById('input_selected_type_' + field_id + '_3').style.display = "block"
                 document.getElementById('input_selected_type_' + field_id + '_3').style.visibility = "hidden"

              //remove input
             document.getElementById("validator_dropdown_" + field_id).style.display = "none"
             // remove_radio
             document.getElementById("sortable-radio-widget-edit-div-" + field_id).style.display = "none"
             document.getElementById("sortable-radio-widget-edit-div-" + field_id).innerHTML = ""
             document.getElementById("new_bot_error_div_widgets_" + field_id).innerHTML = ""

             //remove checkbox
             document.getElementById("sortable-checkbox-widget-edit-div-" + field_id).style.display = "none"
             document.getElementById("sortable-checkbox-widget-edit-div-" + field_id).innerHTML = ""

             //remove dropdown
             document.getElementById("sortable-dropdown-widget-edit-div-" + field_id).style.display = "none"
             document.getElementById("sortable-dropdown-widget-edit-div-" + field_id).innerHTML = ""

             //remove range slider
             document.getElementById("form-widget-range-slider-min-max-container" + field_id).style.display = "none";
             document.getElementById("range_type_" + field_id).style.display = "none"

             //remove file attach
             document.getElementById('file_attach_' + field_id).style.display = "none"
         }

     }
 }


 // custom dropdown for self learning


function create_custom_dropdown_for_selflearning(key) {
  
     $("#modal_add_to_intent"+key+" .easychat-console-select-drop").each(function(i, select) {
         if (!$(this).next().hasClass('easychat-dropdown-select-custom')) {
             $(this).after('<div style="margin-bottom: 5px;" id="easychat-dropdown-select-custom-' + i + '-' + key + '" class="easychat-dropdown-select-custom wide ' + ($(this).attr('class') || '') + '" tabindex="' + key + '"><span class="current" id="current-' + i + '-' + key + '"></span><div class="list"><ul></ul></div></div>');
             var dropdown = $(this).next();

             var options = $(select).find('span');

             var selected = $(this).find('easychat-console-language-option:selected');

             dropdown.find('#current-' + i + '-' + key).html(selected.data('display-text') || selected.text());
             options.each(function(j, o) {
                 var display = $(o).data('display-text') || '';
                 dropdown.find('ul').append('<li class="easychat-console-language-option ' + ($(o).is(':selected') ? 'selected' : '') + '" id="easychat-console-language-option-' + i + '-' + key + '" data-value="' + $(o).data("value") + '" data-display-text="' + display + '">' + $(o).text() + '</li>');
             });

            $("#modal_add_to_intent"+key+" #easychat-dropdown-select-custom-" + i + "-" + key + " ul li:eq(" + 0 + ")").addClass('easychat-lang-selected');
            $("#modal_add_to_intent" + key + ' #current-' + i + '-' + key).html("choose from dropdown");

         }

        $('#modal_add_to_intent'+key+' #easychat-dropdown-select-custom-' + i + '-' + key + '  ul li:last').after('<div class="custom-drop-nodata-found-div">No result found</div> ');
         $('#modal_add_to_intent'+key+' #easychat-dropdown-select-custom-' + i + '-' + key + ' ul').before(`<div class="dd-search"> <svg class="drop-language-search-icon" width="15" height="14" viewBox="0 0 15 14" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M13.1875 12.0689L9.88352 8.76489C10.6775 7.81172 11.0734 6.58914 10.9889 5.35148C10.9045 4.11382 10.3461 2.95638 9.42994 2.11993C8.51381 1.28349 7.31047 0.83244 6.07025 0.86062C4.83003 0.8888 3.64842 1.39404 2.77123 2.27123C1.89404 3.14842 1.3888 4.33003 1.36062 5.57025C1.33244 6.81047 1.78349 8.01381 2.61993 8.92994C3.45638 9.84607 4.61382 10.4045 5.85148 10.4889C7.08914 10.5734 8.31172 10.1775 9.26489 9.38352L12.5689 12.6875L13.1875 12.0689ZM2.25002 5.68752C2.25002 4.90876 2.48095 4.14748 2.91361 3.49996C3.34627 2.85244 3.96122 2.34776 4.6807 2.04974C5.40019 1.75172 6.19189 1.67375 6.95569 1.82568C7.71949 1.97761 8.42108 2.35262 8.97175 2.90329C9.52242 3.45396 9.89743 4.15555 10.0494 4.91935C10.2013 5.68315 10.1233 6.47485 9.8253 7.19433C9.52728 7.91382 9.0226 8.52877 8.37508 8.96143C7.72756 9.39409 6.96628 9.62502 6.18752 9.62502C5.14358 9.62386 4.14274 9.20865 3.40457 8.47047C2.66639 7.7323 2.25118 6.73145 2.25002 5.68752Z" fill="#909090"/></svg><input id="txtSearchValue-` + i + `-` + key + `" autocomplete="off" placeholder="Search" onkeyup="form_widget_filter(` + i + `,` + key + `)" class="dd-searchbox" type="text"></div>`);        

     });



 }


  // Option click
 function select_option_for_selflearning(key) {
     $(document).on('click', '#modal_add_to_intent'+key+' .easychat-dropdown-select-custom .easychat-console-language-option', function(event) {

         $(this).closest('.list').find('.easychat-lang-selected').removeClass('easychat-lang-selected');
         $(this).addClass('easychat-lang-selected');

         var text = $(this).data('display-text') || $(this).text();
         $(this).closest('.easychat-dropdown-select-custom').find('.current').text(text);
         $(this).closest('.easychat-dropdown-select-custom').prev('select').val($(this).data('value')).trigger('change');
     });
 }


 /////////////////////////////////////////////////////////////////////     bot configuration dropdown functions start //////////////////////////////////////////////////


function create_language_custom_dropdowns_for_bot_configuration() {
    $("#edit-bot-custom-drp-down .easychat-console-select-drop").each(function(i, select) {
        if (!$(this).next().hasClass('easychat-dropdown-select-custom')) {
            $(this).after('<div class="easychat-dropdown-select-custom wide ' + ($(this).attr('class') || '') + '" tabindex="0"><span class="current-language"></span><div class="list"><ul></ul></div></div>');
            let dropdown = $(this).next();  
            let options = $(select).find('span');
            let selected = $(this).find('easychat-console-language-option:selected');
            dropdown.find('.current-language').html(selected.data('display-text') || selected.text());
            options.each(function(j, o) {
                let display = $(o).data('display-text') || '';
                dropdown.find('ul').append('<li class="easychat-console-language-option ' + ($(o).is(':selected') ? 'selected' : '') + '" data-value="' + $(o).data("value") + '" data-display-text="' + display + '">' + $(o).text() + '</li>');
            });
        }

    });
    $('#edit-bot-custom-drp-down .easychat-dropdown-select-custom ul li:last').after('<div class="custom-drop-nodata-found-div">No result found</div> ');
    $('#edit-bot-custom-drp-down .easychat-dropdown-select-custom ul').before('<div class="dd-search"> <svg class="drop-language-search-icon" width="15" height="14" viewBox="0 0 15 14" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M13.1875 12.0689L9.88352 8.76489C10.6775 7.81172 11.0734 6.58914 10.9889 5.35148C10.9045 4.11382 10.3461 2.95638 9.42994 2.11993C8.51381 1.28349 7.31047 0.83244 6.07025 0.86062C4.83003 0.8888 3.64842 1.39404 2.77123 2.27123C1.89404 3.14842 1.3888 4.33003 1.36062 5.57025C1.33244 6.81047 1.78349 8.01381 2.61993 8.92994C3.45638 9.84607 4.61382 10.4045 5.85148 10.4889C7.08914 10.5734 8.31172 10.1775 9.26489 9.38352L12.5689 12.6875L13.1875 12.0689ZM2.25002 5.68752C2.25002 4.90876 2.48095 4.14748 2.91361 3.49996C3.34627 2.85244 3.96122 2.34776 4.6807 2.04974C5.40019 1.75172 6.19189 1.67375 6.95569 1.82568C7.71949 1.97761 8.42108 2.35262 8.97175 2.90329C9.52242 3.45396 9.89743 4.15555 10.0494 4.91935C10.2013 5.68315 10.1233 6.47485 9.8253 7.19433C9.52728 7.91382 9.0226 8.52877 8.37508 8.96143C7.72756 9.39409 6.96628 9.62502 6.18752 9.62502C5.14358 9.62386 4.14274 9.20865 3.40457 8.47047C2.66639 7.7323 2.25118 6.73145 2.25002 5.68752Z" fill="#909090"/></svg><input id="txtSearchValue" autocomplete="off" placeholder="Search Language" onkeyup="filter_languages_in_channel_dropdown()" class="dd-searchbox" type="text"></div>');
    $('#edit-bot-custom-drp-down .easychat-dropdown-select-custom span').before(' <svg class="drop-language-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"> <rect width="24" height="24" fill="white"/><path fill-rule="evenodd" clip-rule="evenodd" d="M8.62477 3C8.92313 3 9.20927 3.11832 9.42024 3.32894C9.63121 3.53955 9.74973 3.82521 9.74973 4.12306V5.24612H13.1246C13.4229 5.24612 13.7091 5.36444 13.9201 5.57506C14.131 5.78567 14.2495 6.07133 14.2495 6.36918C14.2495 6.66703 14.131 6.95269 13.9201 7.1633C13.7091 7.37392 13.4229 7.49224 13.1246 7.49224H11.5249C11.1238 9.36076 10.4714 11.1665 9.58549 12.8605C9.91172 13.258 10.256 13.6421 10.6137 14.0127C10.7163 14.1189 10.7969 14.2442 10.851 14.3815C10.9051 14.5188 10.9316 14.6654 10.9289 14.8129C10.9262 14.9605 10.8945 15.106 10.8355 15.2413C10.7765 15.3765 10.6914 15.4989 10.585 15.6013C10.4786 15.7037 10.3531 15.7842 10.2156 15.8382C10.078 15.8922 9.9312 15.9186 9.78344 15.916C9.63568 15.9133 9.48989 15.8816 9.3544 15.8227C9.2189 15.7638 9.09636 15.6788 8.99376 15.5727C8.78227 15.3525 8.57415 15.1279 8.37053 14.8988C7.37625 16.3736 6.20217 17.7192 4.8753 18.9048C4.65254 19.1002 4.36149 19.1999 4.06547 19.1822C3.76945 19.1645 3.49241 19.0308 3.2946 18.8103C3.09679 18.5897 2.99423 18.3001 3.00921 18.0044C3.02419 17.7087 3.15551 17.4309 3.37461 17.2314C4.74286 16.009 5.92861 14.5972 6.89572 13.039C6.26734 12.1494 5.7081 11.213 5.22291 10.2381C5.15171 10.1056 5.10791 9.96011 5.09409 9.81035C5.08028 9.66059 5.09674 9.50958 5.14249 9.36629C5.18824 9.223 5.26236 9.09034 5.36044 8.97618C5.45852 8.86203 5.57857 8.76871 5.71347 8.70175C5.84836 8.63479 5.99535 8.59556 6.14572 8.58639C6.29609 8.57722 6.44678 8.5983 6.58883 8.64837C6.73089 8.69844 6.86142 8.77648 6.97269 8.87787C7.08396 8.97926 7.1737 9.10193 7.23658 9.2386C7.49982 9.76644 7.78668 10.2808 8.09605 10.7794C8.56515 9.7305 8.94201 8.63102 9.21762 7.49224H4.12495C3.8266 7.49224 3.54046 7.37392 3.32949 7.1633C3.11852 6.95269 3 6.66703 3 6.36918C3 6.07133 3.11852 5.78567 3.32949 5.57506C3.54046 5.36444 3.8266 5.24612 4.12495 5.24612H7.49982V4.12306C7.49982 3.82521 7.61834 3.53955 7.82931 3.32894C8.04028 3.11832 8.32642 3 8.62477 3ZM15.3745 9.73836C15.5834 9.73847 15.7881 9.79663 15.9657 9.90632C16.1433 10.016 16.2869 10.1729 16.3802 10.3594L19.745 17.0776C19.7528 17.0912 19.7603 17.1051 19.7675 17.1191L20.8812 19.3428C21.0147 19.6093 21.0366 19.918 20.9422 20.2007C20.8478 20.4835 20.6448 20.7172 20.3777 20.8505C20.1107 20.9838 19.8016 21.0057 19.5184 20.9114C19.2351 20.8172 19.001 20.6145 18.8675 20.3479L18.0553 18.7228H12.696L11.8815 20.3479C11.8183 20.4844 11.7283 20.6069 11.6168 20.7081C11.5053 20.8092 11.3746 20.887 11.2325 20.9368C11.0903 20.9865 10.9395 21.0073 10.7892 20.9978C10.6388 20.9883 10.4919 20.9487 10.3572 20.8814C10.2224 20.8142 10.1026 20.7206 10.0047 20.6062C9.90691 20.4918 9.83309 20.359 9.78767 20.2156C9.74224 20.0722 9.72613 19.9211 9.74029 19.7714C9.75445 19.6216 9.79859 19.4763 9.8701 19.3439L10.9838 17.1202L11.0052 17.0776L14.3688 10.3594C14.4622 10.1729 14.6057 10.016 14.7833 9.90632C14.9609 9.79663 15.1656 9.73847 15.3745 9.73836ZM13.8198 16.4767H16.9292L15.2807 12.4524L13.8198 16.4767Z" fill="#4B4B4B"/></svg>');

    let selected_language = SELECTED_LANGUAGE
    let el = $("#edit-bot-custom-drp-down .easychat-dropdown-select-custom ul ").find(`[data-value='${selected_language}']`)
    el.addClass('easychat-lang-selected')
    let default_select_lang_drop = el.text()
    $('.current-language').html(default_select_lang_drop);

}
function add_language_selction_event_for_bot_configuration(){
    $(document).on('click', '#edit-bot-custom-drp-down .easychat-dropdown-select-custom .easychat-console-language-option', function(event) {
        $(this).closest('.list').find('.easychat-lang-selected').removeClass('easychat-lang-selected');
        $(this).addClass('easychat-lang-selected');

        var text = $(this).data('display-text') || $(this).text();
        $(this).closest('.easychat-dropdown-select-custom').find('.current-language').text(text);
        $(this).closest('.easychat-dropdown-select-custom').prev('select').val($(this).data('value')).trigger('change');
        selected_language = $(this).data('value').trim()
        $("#modal-language-change-loader .modal-content #language-loader-inner-text").html("Configuring Response Languages")
        check_and_update_language(selected_language, BOT_ID);
    });
}

function open_close_language_dropdown_event_configurations(){
    $(document).on('click', '.easychat-dropdown-select-custom', function(event) {
        if ($(event.target).hasClass('dd-searchbox')) {
            return;
        }
        $('.easychat-dropdown-select-custom').not($(this)).removeClass('open');
        $('#txtSearchValue').val("");
        $(".easychat-dropdown-select-custom ul li").show();

        $('.custom-drop-nodata-found-div').hide();


        if ($(this).hasClass('open')) {
            $(this).find('.easychat-console-language-option').attr('tabindex', 0);
            $(this).find('.easychat-lang-selected').focus();
        } else {
            $(this).find('.easychat-console-language-option').removeAttr('tabindex');
            $(this).focus();
        }
    });
}

/////////////////////////////////////////////////////////////////////     bot configuration dropdown functions end //////////////////////////////////////////////////

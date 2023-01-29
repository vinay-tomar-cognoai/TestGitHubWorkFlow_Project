
$("#bot_action_opner_btn").click(function() {
    
    $("#bot_action_btn_items").slideToggle();
    $(this).toggleClass("rotate-bot-action-opner-btn");
    if ($('#bot_action_opner_btn').css('display') != "none" ) {
            setTimeout(function() {
                resize_chabot_window()
            }, 400)
        }
});
$("#sticky_menu_opner_btn").click(function() {
    if (EASYCHAT_BOT_THEME == "theme_4") {
        $("#bot_menu_option_items_wrapper_div").slideDown();
    } else {
        $("#bot_menu_option_items_wrapper").slideDown();
    }
    
    $(".bot-button-only-footer-menu-wrapper").hide();
});
$(".bot-sticky-menu-close-btn-wrapper").click(function() {
    $("#bot_menu_option_items_wrapper").slideUp();
    $("#bot_menu_option_items_wrapper_div").slideUp();

    setTimeout(function() {

        $(".bot-button-only-footer-menu-wrapper").show();


    }, 400);
});
$(".easychat-sticky-menu-item").click(function() {
    $("#bot_menu_option_items_wrapper").slideUp();
    $("#bot_menu_option_items_wrapper_div").slideUp();
    setTimeout(function() {

        $(".bot-button-only-footer-menu-wrapper").show();


    }, 400);
});


// theme3 language btn 
$("#sticky_lang_dropdown_opner_btn").click(function() {
    const language_div = $('#button_only_language_wrapper');

    if (language_div.css('display') != "block") {
        $("#button_only_language_wrapper").slideToggle();
    }

});
$('.language-dropdown-content-wrapper-items').on('click', function(event) {
    event.stopPropagation();
    $(this).find('.active-language').removeClass('active-language');
    $(event.target).addClass('active-language');
    $("#button_only_language_wrapper").slideUp();

    $('.bot-language-selected-text-div').text($(event.target).text());

})

// Sticky intents for other themes than theme3 with no input field

function append_sticky_intents_menu_no_input_field(sticky_intents_list_menu) {
    $("#easychat_sticky_menu_items_no_input").empty();
    var html = ''
    for (let i = 0; i < sticky_intents_list_menu.length; ++i) {
        let sticky_intent = sticky_intents_list_menu[i];
        let clean_intent_name = sticky_intent[0].replaceAll("'", "\\"+"'");

        html += '<div class="easychat-sticky-menu-item" onclick="send_sticky_message_no_input(\'' + clean_intent_name + '\', \'' + sticky_intent[2] + '\'); $(\'.bot-sticky-menu-close-btn-wrapper\').click();">\
                            <div>\
                            <i class = "fa ' + sticky_intent[1] + ' sticky-menu-item-icon" style="color:' + BOT_THEME_COLOR + '"></i>\
                            </div>\
                            <div class="easychat-sticky-menu-item-text">' + sticky_intent[0] + '</div>\
                        </div>'
    }

    $("#easychat_sticky_menu_items_no_input").append(html);

}

function send_sticky_message_no_input(user_input, intent_id) {
    if (sticky_button_display_format == "Menu") {
        let sticky_menu = document.getElementById('easychat_sticky_menu_items_no_input');
        sticky_menu.className = 'easychat-sticky-menu-items-no-input';
    }

    entered_suggestion = true;
    is_sticky_message = true;
    send_user_input(user_input, intent_id);

    setTimeout(function() {
        resize_chabot_window()
    }, 500)
    
}

function hide_input_field_footer() {
    if (!IS_TEXTFIELD_INPUT_ENABLED) {
        document.getElementById("hide-if-no-input").style.display = "none"
        $(".dont-hide-if-no-input").css('display', '')
        if(EASYCHAT_BOT_THEME == "theme_4") {
            $(".easychat-bot-footer-input-wrapper").hide()
            $("#bot_menu_option_items_wrapper").css('display', 'flex')
        }
    if (EASYCHAT_BOT_THEME != "theme_1") {

        if (!$("#easychat-footer").hasClass("footer-with-button-only")) {
            $("#easychat-footer").addClass("footer-with-button-only")
        }
    }
    
        if (!$("#user_actions_div").hasClass("footer-with-button-only")) {
            $("#user_actions_div").addClass("footer-with-button-only")
        }
        if(EASYCHAT_BOT_THEME == "theme_1") {
            document.getElementById("easychat-footer").style.boxShadow = "none";
        }

    }

}

function show_input_field_footer() {
    if (!IS_TEXTFIELD_INPUT_ENABLED) {
        document.getElementById("hide-if-no-input").style.display = ""
        remove_button_only_class()
        $(".dont-hide-if-no-input").css('display', 'none')
        if(EASYCHAT_BOT_THEME == "theme_4") {
            $(".easychat-bot-footer-input-wrapper").css('display', 'flex')
            $("#bot_menu_option_items_wrapper").prop("style", "display: none !important")
        }
        if(EASYCHAT_BOT_THEME == "theme_1") {
            document.getElementById("user_actions_div").style.border = "1px solid #f2f2f2";
            document.getElementById("easychat-footer").style.boxShadow = "rgb(0 0 0 / 10%) 0px 0px 15px";
        }
    }

}

function remove_button_only_class() {
    if ($("#easychat-footer").hasClass("footer-with-button-only")) {
        $("#easychat-footer").removeClass("footer-with-button-only")
    }


    if ($("#user_actions_div").hasClass("footer-with-button-only")) {
        $("#user_actions_div").removeClass("footer-with-button-only")
    }

    $("#dont-hide-if-no-input").css('display', 'none')
    
}

function append_sticky_intents_no_input_field(sticky_intents_list) {
    $("#sticky-div-no-input").empty();
    var html = ''
    html += '<button class="arrow-button-left" onclick="sticky_scroll_backward()" style="border: none !important;"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M0 0H18C21.3137 0 24 2.68629 24 6V18C24 21.3137 21.3137 24 18 24H0V0Z" fill=""></path><path fill-rule="evenodd" clip-rule="evenodd" d="M15.7071 4.29289C16.0976 4.68342 16.0976 5.31658 15.7071 5.70711L9.41421 12L15.7071 18.2929C16.0976 18.6834 16.0976 19.3166 15.7071 19.7071C15.3166 20.0976 14.6834 20.0976 14.2929 19.7071L7.29289 12.7071C6.90237 12.3166 6.90237 11.6834 7.29289 11.2929L14.2929 4.29289C14.6834 3.90237 15.3166 3.90237 15.7071 4.29289Z" fill="' + BOT_THEME_COLOR + '"></path></svg></button>'
    for (let i = 0; i < sticky_intents_list.length; ++i) {
        let sticky_intent = sticky_intents_list[i];
        let clean_intent_name = sticky_intent.name.replaceAll("'", "\\"+"'");

        html += '<button class="button_sticky" onclick="send_sticky_message(\'' + clean_intent_name + '\', \'' + sticky_intent.id + '\')" style="color:' + BOT_THEME_COLOR + ';font-size:15px;outline:auto;border-radius:10px;border:0;height:30px;">' + sticky_intent.name + '</button>&nbsp;&nbsp;&nbsp;&nbsp;'
    }

    html += '<button class="arrow-button-right" onclick="sticky_scroll_forward()" style="border: none !important;"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M24 0H6C2.68629 0 0 2.68629 0 6V18C0 21.3137 2.68629 24 6 24H24V0Z" fill=""></path><path fill-rule="evenodd" clip-rule="evenodd" d="M8.2929 4.29289C7.9024 4.68342 7.9024 5.31658 8.2929 5.70711L14.5858 12L8.2929 18.2929C7.9024 18.6834 7.9024 19.3166 8.2929 19.7071C8.6834 20.0976 9.3166 20.0976 9.7071 19.7071L16.7071 12.7071C17.0976 12.3166 17.0976 11.6834 16.7071 11.2929L9.7071 4.29289C9.3166 3.90237 8.6834 3.90237 8.2929 4.29289Z" fill="' + BOT_THEME_COLOR + '"></path></svg></button>'

    $("#sticky-div-no-input").append(html);

    append_side_arrows_if_needed()

}

function append_sticky_intents_no_input_field_theme_3_4(sticky_intents_list) {
    var element = $("#easychat-bot-sticky-intent-items-div")
    if (EASYCHAT_BOT_THEME == "theme_4") {
        element = $("#easychat-bot-sticky-intent-items-div-no-input")   
    }

    element.empty()


    var html = ''

    for (let i = 0; i < sticky_intents_list.length; ++i) {
        let sticky_intent = sticky_intents_list[i];
        let clean_intent_name = sticky_intent.name.replaceAll("'", "\\"+"'");

        html += '<button class="button-sticky-item" onclick="send_sticky_message(\'' + clean_intent_name + '\', \'' + sticky_intent.id + '\')">' + sticky_intent.name + '</button>'
    }

    element.append(html)

    setTimeout(function() {
        $("#easychat-sticky-btn-theme3-4").css('display', 'flex')
        append_side_arrows_if_needed()
    }, 400)
    
    
}

function append_side_arrows_if_needed() {
    total_length_of_buttons = 0
    var button_sticky = "button_sticky"
    var sticky_div = "sticky-div"
    var easychat_sticky_intents = "easychat-sticky-intents"
    var arrow_button_left = "arrow-button-left"
    var arrow_button_right = "arrow-button-right"
    if (EASYCHAT_BOT_THEME == "theme_3" || EASYCHAT_BOT_THEME == "theme_4") {
        button_sticky = "button-sticky-item"
        easychat_sticky_intents = "easychat-bot-sticky-intent-items-div"
        arrow_button_left = "sticky-intent-arrow-button-left"
        arrow_button_right = "sticky-intent-arrow-button-right"
        if (EASYCHAT_BOT_THEME == "theme_4") {
            easychat_sticky_intents = "easychat-bot-sticky-intent-items-div-no-input"
        }
    }

    for (var button_iterator = 0; button_iterator < document.getElementsByClassName(button_sticky).length; button_iterator++) {
        total_length_of_buttons += document.getElementsByClassName(button_sticky)[button_iterator].offsetWidth
    }
    if (detectIEEdge()) {
        document.getElementById(sticky_div).style.width = 1.15 * (total_length_of_buttons) + "px";
        //document.getElementsByClassName("arrow-button-left")[0].style.display = "none";
        //document.getElementsByClassName("arrow-button-right")[0].style.display = "none";
    }

    if (total_length_of_buttons < 0.9 * document.getElementById(easychat_sticky_intents).offsetWidth) {
        document.getElementsByClassName(arrow_button_left)[0].style.display = "none";
        document.getElementsByClassName(arrow_button_right)[0].style.display = "none";

        if (EASYCHAT_BOT_THEME == "theme_2") {
            $("#" + easychat_sticky_intents).css('margin-left', "0px")
            $(".language-right-to-left-wrapper #" + easychat_sticky_intents).css('margin-left', "20px")
        } else if (EASYCHAT_BOT_THEME == "theme_3" || EASYCHAT_BOT_THEME == "theme_4") {
            $("#" + easychat_sticky_intents).css("width", "100%");
        }
    }

}

$(document).mouseup(function(e) {
    var container = $(".easychat-bot-language-div-button-only");
    if (container.length != 0 && !container.is(e.target) && container.has(e.target).length === 0) {

        const language_div = $('#button_only_language_wrapper');

        if (language_div.css('display') == "block") {
            $("#button_only_language_wrapper").slideToggle();

        }
    }

    hide_no_input_sticky_menu_event(e)
});

function hide_no_input_sticky_menu_event(e) {
    var wrapper_sticky_menu = ".easychat-button-only-sticky-menu-option-wrapper"

    var container2 = $(wrapper_sticky_menu);
    if (container2.length != 0 && !container2.is(e.target) && container2.has(e.target).length === 0) {
        hide_no_input_sticky_menu()
    }
}

function hide_no_input_sticky_menu() {
    var menu_div = $('#bot_menu_option_items_wrapper');
    if (EASYCHAT_BOT_THEME == "theme_4") {
        menu_div = $('#bot_menu_option_items_wrapper_div');
    }

    if (menu_div.css('display') == "block") {
        menu_div.slideUp();
        setTimeout(function() {
    
            $(".bot-button-only-footer-menu-wrapper").show();
    
    
        }, 400);

    }
}

$(".bot-language-selected-wrapper-div").click(function() {
    const language_div = $('#button_only_language_wrapper');
    if (language_div.css('display') == "block") {
        $("#button_only_language_wrapper").slideToggle();
        
    }
})
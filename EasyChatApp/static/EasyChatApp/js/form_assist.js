// Global Variables

var timer;
var auto_form_pop_timer;
var is_trigger_bot_allowed = 0;
var prev_element_id = ""
var element_id = ""
var form_assist_id = ""
var form_assist_intent_name = ""
var flag_trigger_timer = true
var is_clicked_blank_space = false
var is_hover = false
var stop_form_assist = false
var starting_element = false
var speech_synthesis_utterance_instance = null;
var speech_synthesis_instance = window.speechSynthesis;
var voices = null;
var speech_pause_resume_interval = null;
var is_form_assist_greeting_bubble_popped = false;


//If form assist is active it will return "true", else "false"
function is_form_assist_active(){
    return stop_form_assist;
}

//It will return the intent name. 
function get_form_assist_id(){
    return form_assist_id
}

// It will enable form assist
function enable_form_assist() {
    stop_form_assist = false
    check_user_activity_status()
}

// When window loads "check_user_activity_status()" will initialize and check user activity.
function check_user_activity_status() {
    window.onload = resetTimer;
    window.onclick = resetTimer;
    window.onkeypress = resetTimer;
    window.addEventListener('scroll', resetTimer, true);
    if(window.is_form_assist_auto_pop_allowed == true){
        is_trigger_bot_allowed = 0
        element_id = ""
        form_assist_id = ""
        form_assist_intent_name = ""
        stop_form_assist = false
        startTimer();
    }
}

// When bot popups timer will stop.
function stop_user_activity_status() {
    clearTimeout(timer);
    is_trigger_bot_allowed = 1;
    cancel_text_to_speech();
}

//It will stop all the activity
function stop_all_activity(){
    clearTimeout(timer);
    is_trigger_bot_allowed = 1;
    stop_form_assist = true
}

// Get "element_id" and openChatBot() 
function openChatBot() {
    if(window.disable_auto_popup_minimized && get_cookie('is_bot_minimized') == 'true') return;

    if(window.disable_auto_popup_minimized && get_cookie('is_bot_minimized') != 'true'){
        is_clicked_blank_space = false
    }

    if(document.getElementById("allincall-chat-box").style.display == 'block') return

    if (element_id != "" && (window.form_assist_auto_popup_type == "1" || window.form_assist_intent_bubble_type == '2')) {
        openFormAssist();
    } else if (element_id != "" && window.form_assist_auto_popup_type == "2" && window.form_assist_intent_bubble_type == '1') {
        document.getElementById("allincall-notification-count").style.display="flex";
        document.getElementById("notification-message-div").style.display="block";
        if(BOT_POSITION.indexOf("top") != -1 && document.getElementById("notification-message-div").parentNode.className.indexOf("greeting") != -1) {
            document.getElementById("notification-message-div").style.display="flex"
        }
    } else if(window.is_form_assist_auto_pop_allowed == true){
        starting_element = true
        if(window.form_assist_auto_popup_type == "1") {
            auto_form_pop_timer = window.setTimeout(function(e){
                document.getElementById("allincall-popup").click();
            },form_assist_autopop_up_timer*1000) 
        } else if (window.form_assist_auto_popup_type == "2") {
            auto_form_pop_timer = setTimeout(function(e) {
                show_greeting_bubble_and_intents(); 
            }, form_assist_intent_bubble_timer * 1000)  
        }
    }
    clearTimeout(timer);
}

// startTimer()  and popup bot after "trigger_bot_time"
function startTimer() {
    if (!is_trigger_bot_allowed) {
        is_trigger_bot_allowed = 0
        openChatBot()
    }
}

// resetTimer()
function resetTimer(e, reset_blank_space_click) {
    window.clearTimeout(timer);
    window.clearTimeout(auto_form_pop_timer)
    if(reset_blank_space_click == true){
        is_clicked_blank_space = false
        timer = setTimeout(function() {
            is_clicked_blank_space = false
            openChatBot()
        }, 200);
    }
    if (stop_form_assist == false && is_clicked_blank_space == false && is_hover == false && window.form_assist_auto_popup_type == "1") {
        if(element_id != "" && element_id in window.form_assist_tag_timer) {
            timer = setTimeout(openChatBot, window.form_assist_tag_timer[element_id]*1000);
        } else {
            timer = setTimeout(openChatBot, window.form_assist_inactivity_timer*1000);
        }
    } else if (stop_form_assist == false && is_clicked_blank_space == false && is_hover == false && window.form_assist_auto_popup_type == "2") {
        if(element_id != "" && element_id in window.form_assist_tag_timer) {
            timer = setTimeout(openChatBot, window.form_assist_tag_mapping[element_id][1]*1000);
        } else {
            if(element_id){
                timer = setTimeout(openChatBot, window.form_assist_intent_bubble_inactivity_timer*1000);
            } else {
                timer = setTimeout(openChatBot, 500);
            }
        }
    }
}

// resetHoverTimer()
function resetHoverTimer() {
    window.clearTimeout(timer);
    if (stop_form_assist == false && is_clicked_blank_space == false && is_hover == true && window.form_assist_auto_popup_type == "1") {
        timer = setTimeout(openChatBot, window.form_assist_inactivity_timer*1000);
    } else if (stop_form_assist == false && is_clicked_blank_space == false && is_hover == true && window.form_assist_auto_popup_type == "2") {
        timer = setTimeout(openChatBot, window.form_assist_intent_bubble_inactivity_timer*1000);
    }
    is_hover = false
}

// MD5 hashing for element.
function get_md5_string(element) {

    var string = "";
    if (element.getAttribute("id") != null) {
        string = element.getAttribute("id");
    } else if (element.getAttribute("data-id") != null) {
        string = element.getAttribute("data-id");
    } else {
        string = element.outerHTML;
        string = string.replace(/style="[^"]*"/, ""); // remove style tag from html string
        string = string.replace(/value="[^"]*"/, ""); // remove value tag from html string
        string = string.replace(/class="[^"]*"/, ""); // remove class tag from html string
        string = string.replace(/aria-required="[^"]*"/, ""); // remove aria-required
        string = string.replace(/aria-invalid="[^"]*"/, ""); // remove aria-invalid
        string = string.replace(/[a-z0-9-_]*=""/g, ""); // remove all attributes whose value is empty
        string = string.replace(/ /g, ""); // remove whitespace from html string
    }
    return EasyChatCryptoJS.MD5(string).toString();
}

// When window loads
function callFormAssist() {

    // Check user activity
    check_user_activity_status();
    cancel_text_to_speech();

    // Click event
    document.addEventListener('click', function(event) {
        if(starting_element == true){
            clearTimeout(auto_form_pop_timer);
            starting_element = false
        }
        // If user click on "input"/"button"/"select"
        if (event.target.matches('input') || event.target.matches('button') || event.target.matches('select')) {

            // If user didn't hover first at "input"/"button"/"select"
            if (is_hover == false) {
                is_clicked_blank_space = false
                // Get activeElement
                element = document.activeElement;
                //Get MD5 hash of element
                element_id = get_md5_string(element);
                // Hide bot when user click on any field
                is_display = document.getElementById("allincall-chat-box").style.display;
                if(is_display == "block"){
                    close_chatbot_animation()
                    setTimeout(function(){
                        if(!document.getElementById('allincall-min-popup') || document.getElementById('allincall-min-popup').style.display != 'block'){
                            document.getElementById("allincall-popup").style.display="block";
                        }
                        document.getElementById("allincall-chat-box").style.display="none";
                        if(document.getElementById("easychat-bot-minimize-button"))
                            document.getElementById("easychat-bot-minimize-button").style.display="none";

                        if(document.getElementById("easychat-bot-close-button")) 
                            document.getElementById("easychat-bot-close-button").style.display="none";
                        check_for_bot_minimized_state()
                    }, 900);                    
                }

                //If user multiple time click on same element.
                if (prev_element_id != element_id) {
                    console.log("Currently focused at " + element_id);
                    clearTimeout(timer);
                    is_trigger_bot_allowed = 1
                    resetTimer();
                    prev_element_id = element_id;
                }
            }
        } else if (event.target.matches('textarea') || event.target.matches('focus')) {
            is_hover = false
            is_clicked_blank_space = false
            element = document.activeElement;
            element_id = get_md5_string(element);
            close_chatbot_animation()
            setTimeout(function(){
                if(!document.getElementById('allincall-min-popup') || document.getElementById('allincall-min-popup').style.display != 'block'){
                    document.getElementById("allincall-popup").style.display="block";
                }
                document.getElementById("allincall-chat-box").style.display="none";
                if(document.getElementById("easychat-bot-minimize-button"))
                    document.getElementById("easychat-bot-minimize-button").style.display="none";
                if(document.getElementById("easychat-bot-close-button")) 
                    document.getElementById("easychat-bot-close-button").style.display="none";
                check_for_bot_minimized_state()
            }, 900);
            if (prev_element_id != element_id) {
                console.log("Currently focused at " + element_id);
                clearTimeout(timer);
                is_trigger_bot_allowed = 1
                resetTimer();
                prev_element_id = element_id;
            }
        } else {
            if(event.path[0].id == 'allincall-maximize-popup' || event.path[1].id == 'allincall-maximize-popup'){
                is_clicked_blank_space = false
            } else {
                is_clicked_blank_space = true
                prev_element_id = ""
            }
        }
    }, false);

    // Hover event
    document.addEventListener('mouseover', function() {
        if(starting_element == true){
            clearTimeout(auto_form_pop_timer);
            starting_element = false
        }
        //If event is "button"/"select"/"input"

        if (event.target.matches('button') || event.target.matches('select') || event.target.matches('input')) {
            //If hover element is button.
            if (event.target.matches('button'))
            {
                is_clicked_blank_space = false
                is_hover = true
                element = event.target
                element = document.activeElement;
                element_id = get_md5_string(element);
                close_chatbot_animation()
                setTimeout(function(){
                    if(!document.getElementById('allincall-min-popup') || document.getElementById('allincall-min-popup').style.display != 'block'){
                        document.getElementById("allincall-popup").style.display="block";
                    }
                    document.getElementById("allincall-chat-box").style.display="none";
                    if(document.getElementById("easychat-bot-minimize-button"))
                        document.getElementById("easychat-bot-minimize-button").style.display="none";
                    if(document.getElementById("easychat-bot-close-button")) 
                        document.getElementById("easychat-bot-close-button").style.display="none";
                    check_for_bot_minimized_state()
                }, 900);

                if (prev_element_id != element_id) {
                    console.log("Currently hovered at " + element_id);
                    clearTimeout(timer);
                    is_trigger_bot_allowed = 1
                    resetHoverTimer();
                    prev_element_id = element_id;
                }
            } else if (event.target.matches('input')) {
                is_clicked_blank_space = false
                is_hover = true
                element = event.target
                if (element.getAttribute("type") == 'radio' || element.getAttribute("type") == 'button' || element.getAttribute("type") == 'checkbox') {
                    element_id = get_md5_string(element);
                    close_chatbot_animation()
                    setTimeout(function(){
                        if(!document.getElementById('allincall-min-popup') || document.getElementById('allincall-min-popup').style.display != 'block'){
                            document.getElementById("allincall-popup").style.display="block";
                        }
                        document.getElementById("allincall-chat-box").style.display="none";
                        if(document.getElementById("easychat-bot-minimize-button"))
                            document.getElementById("easychat-bot-minimize-button").style.display="none";
                        if(document.getElementById("easychat-bot-close-button")) 
                            document.getElementById("easychat-bot-close-button").style.display="none";
                        check_for_bot_minimized_state()
                    }, 900);
                    if (prev_element_id != element_id) {
                        console.log("Currently hovered at " + element_id);
                        clearTimeout(timer);
                        is_trigger_bot_allowed = 1
                        resetHoverTimer();
                        prev_element_id = element_id;
                    }
                } else {
                    is_hover = false
                    prev_element_id = ""
                }
            }
        }
    });
}

// openformAssist()
function openFormAssist() {
    if(window.disable_auto_popup_minimized && get_cookie('is_bot_minimized') == 'true'){
        return;
    }
    if(element_id in window.form_assist_tags){
        form_assist_id = window.form_assist_tags[element_id];
        if (form_assist_id != "" && window.form_assist_auto_popup_type == "1") 
        {
            document.getElementById("allincall-popup").click();
            stop_user_activity_status();
        } else if(form_assist_id != "" && window.form_assist_intent_bubble_type == "2") {

            document.getElementById("notification-message-div").style.display="block";
            var intent_bubble_elems = document.getElementsByClassName('form-assist-intent-bubble');

            for(let i = 0; i < intent_bubble_elems.length; i++) {
                intent_bubble_elems[i].style.display = "none";
            }
            document.getElementById("intent-bubble-greeting-message").style.display = "none";
            document.getElementById(window.form_assist_tag_mapping[element_id][0]).style.display = "block";
            if(window.voice_based_form_assist_enabled) {
                text_to_speech(window.form_assist_intent_responses_dict[form_assist_id]);
            }
        }

    } else if (element_id != "" && window.form_assist_intent_bubble_type == "2") {
        show_greeting_bubble_and_intents();
        if(is_form_assist_greeting_bubble_popped){
            if(document.getElementById('intent-bubble-greeting-message') && document.getElementById('intent-bubble-greeting-message').style.display != 'block') {
                document.getElementById("notification-message-div").style.display = "none";
            }
        }
    } else {
        element_id = ""
        form_assist_id = ""
        form_assist_intent_name = ""
        stop_form_assist = false
        check_user_activity_status()
    }
}

function open_form_assist_greeting_intent(thiselem) {
    easychat_intent_name = thiselem.innerText;
    is_initial_trigger_intent = true;
    document.getElementById("allincall-popup").click();
    stop_user_activity_status();
}

function text_to_speech(message_to_be_spoken) {

    message_to_be_spoken = message_to_be_spoken.replace(/<[^>]*>?/gm, '');
    speech_synthesis_utterance_instance = new SpeechSynthesisUtterance(message_to_be_spoken);
    speech_synthesis_utterance_instance.lang = selected_language;
    speech_synthesis_utterance_instance.rate = 0.95;
    speech_synthesis_utterance_instance.pitch = 1;
    speech_synthesis_utterance_instance.volume = 1;
    speech_synthesis_utterance_instance.onend = function(event){
        try{
            clearInterval(speech_pause_resume_interval);
        }catch(err){}
    }
    voices = speech_synthesis_instance.getVoices();
    speech_synthesis_instance.speak(speech_synthesis_utterance_instance);
    speech_pause_resume_interval = setInterval(function() {
      speech_synthesis_instance.pause();
      speech_synthesis_instance.resume();
    }, 10000);

}

function cancel_text_to_speech() {
    if (speech_synthesis_instance != null) {
        speech_synthesis_instance.cancel();
    }
}

function check_for_bot_minimized_state() {
    if (is_minimization_enabled) {
        document.getElementById("allincall-minimize-popup").style.display = "";
        if (window.disable_auto_popup_minimized && get_cookie('is_bot_minimized') == 'true'){
            document.getElementById("allincall-popup").style.display = "none";
            document.getElementById("allincall-min-popup").style.display = "block";
            document.getElementById("allincall-maximize-popup").style.display = "flex";
            document.getElementById("allincall-minimize-popup").style.display = "none";
            document.getElementById("allincall-maximize-popup-tooltip").style.visibility = "hidden";
            document.getElementById("allincall-minimize-popup-tooltip").style.visibility = "hidden";
            change_css_on_bot_minimization(BOT_POSITION)
        }
    }
}

function show_greeting_bubble_and_intents(){
    if(is_form_assist_greeting_bubble_popped) return;
    if(document.getElementById("allincall-chat-box").style.display == 'block') return
    
    if(window.form_assist_intent_bubble_type == "1")
        document.getElementById("allincall-notification-count").style.display="flex";

    document.getElementById("notification-message-div").style.display="block";
    if(document.getElementById('intent-bubble-greeting-message')){
        document.getElementById('intent-bubble-greeting-message').style.display="block";
        var intent_bubble_elems = document.getElementsByClassName('form-assist-intent-bubble');
        if(intent_bubble_elems){
            for(let i = 0; i < intent_bubble_elems.length; i++) {
                if(intent_bubble_elems[i].id in window.form_assist_intent_bubble){
                    intent_bubble_elems[i].style.display = "block";
                } else {
                    intent_bubble_elems[i].style.display = "none";
                }
            }
        }
    }
    if(BOT_POSITION.indexOf("top") != -1 && document.getElementById("notification-message-div").parentNode.className.indexOf("greeting") != -1) {
        document.getElementById("notification-message-div").style.display="flex"
    }
    is_form_assist_greeting_bubble_popped = true
}

/*

Old form Assist Logic

function openFormAssist() {
    var xhttp = new XMLHttpRequest();
    var params = 'tag_id=' + element_id + '&bot_id=' + BOT_ID;
    xhttp.open("POST", SERVER_URL + "/chat/form-assist-response/", true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            if (response["status"] == 200) {
                form_assist_id = response["form_assist_id"];
                form_assist_intent_name = response["form_assist_intent_name"]
                if (form_assist_id != "") 
                {
                    document.getElementById("allincall-popup").click();
                    // stop_form_assist = false
                    stop_user_activity_status();
                }
            } else {
                element_id = ""
                form_assist_id = ""
                form_assist_intent_name = ""
                stop_form_assist = false
                check_user_activity_status()
            }
        }
    }
    xhttp.send(params);
}
*/

// this is working fine - this is working fine

$('.processing').hide();
$('.test_processing').hide();
$('.upload_testdata').hide();
$('.typing-loader').hide();
$(".modal").modal();

// console.log("init.js")
PARENT_DOMAIN_URL = "*";
API_SERVER_URL = "/chat/query/";
STATIC_IMG_PATH = "/static/EasyChatApp/img";
STATIC_MP3_PATH = "/static/EasyChatApp/mp3";

var livechat = false;
var BOT_DISPLAY_NAME = 'hello world';
var CLEAR_API_URL = "/chat/clear-user-data/";
var MESSAGE_IMG = "/static/EasyChatApp/img/favicon.png";
var BOT_THEME_COLOR = '1a237e';
var is_file_attached = false;
var attachment_url = "";
var last_action = "";

file_type_ext = {
  "image(ex. .jpeg, .png)":".jpeg, .png, .gif",
  "word processor(i.e. .doc,.pdf)":".doc, .odt, .pdf, .rtf, .tex, .txt, .wks, .wkp",
  "compressed file(ex. .zip)":".zip, .rar, .rpm, .z, .tar.gz, .pkg",
}

function transpose(a) {
    return Object.keys(a[0]).map(function(c) {
        return a.map(function(r) { return r[c]; });
    });
}

var user_id = '';
var session_id = '';
var bot_id = '';
var bot_name = '';
var timer_var = '';
var window_location = '';
var isMapJsLoaded = 0;
var mapId = 1;
var voice_to_text=null;
var is_form_assist="false";
var script_tag_id = "";
var welcome_form_assist;
var flag_timer = false;
var is_hindi_user = false;
var trigger = true;

get_config_params();


/////////////////////////////// Encryption And Decription //////////////////////////

function CustomEncrypt(msgString, key) {
    // msgString is expected to be Utf8 encoded
    var iv = EasyChatCryptoJS.lib.WordArray.random(16);
    var encrypted = EasyChatCryptoJS.AES.encrypt(msgString, EasyChatCryptoJS.enc.Utf8.parse(key), {
        iv: iv
    });
    var return_value = key;
    return_value += "."+encrypted.toString(); 
    return_value += "."+EasyChatCryptoJS.enc.Base64.stringify(iv);
    return return_value;
}

function generateRandomString(length) {
   var result           = '';
   var characters       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
   var charactersLength = characters.length;
   for ( var i = 0; i < length; i++ ) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
   }
   return result;
}


function EncryptVariable(data){

  utf_data = EasyChatCryptoJS.enc.Utf8.parse(data);
  encoded_data = utf_data;
  // encoded_data = EasyChatCryptoJS.enc.Base64.stringify(utf_data);
  random_key = generateRandomString(16);
  // console.log(random_key)
  encrypted_data = CustomEncrypt(encoded_data, random_key);

  return encrypted_data;
}

////////////////////////////////////////////////////////////////////////////////////


// function tooIdle() {

//         //console.log("inside tooIdle");
//         // window.onload = resetTimer;
//         //window.onmousemove = resetTimer;
//         //window.onmousedown = resetTimer;       
//         //window.ontouchstart = resetTimer;  
//         window.onclick = resetTimer;      
//         window.onkeypress = resetTimer;   
//         //window.addEventListener('scroll', resetTimer, true); 

//     }
// function resetTimer() {
//         clearTimeout(timer_var);
//         //console.log("inside resetTimer");
//         if(flag_timer==false)
//           timer_var = setTimeout(giveSuggestions,5000);
        
// }

// function giveSuggestions() {
//   flag_timer = true;
//   clearTimeout(timer_var);
//   if(!is_hindi_user){
//     appendResponseServer("Do you want any further assistance?", false, "", "","");
//     var temp = ["Yes", "No","हिंदी में देखें।"];
//     appendRecommendationsList(temp);
//     scroll_to_bottom();  
//   }
//   else{
//     appendResponseServer("Do you want any further assistance?", false, "", "","");
//     var temp = ["Yes", "No"];
//     appendRecommendationsList(temp);
//     scroll_to_bottom(); 
//   }
// }

window.onload = function(){

    bot_id = getBotID();

    if(bot_id==null){
       console.log("please enter valid bot id.");
       return;
    }

    bot_name = getBotName();

    if(bot_name==null){
       console.log("please enter valid bot name.");
    }
    session_id = getCookie("easychat_session_id");
    window_location = window.location.pathname;

    url_params = get_url_vars();
    var form_assist_intent_name = url_params["form_assist_intent_name"];
    page_category = url_params["page_category"];
    is_form_assist = url_params["is_form_assist"]
    if(is_form_assist =="true" && form_assist_intent_name!="" && form_assist_intent_name!=undefined && form_assist_intent_name!=null){
        formAssistIntent();
    }else if(page_category!="" && page_category!=undefined && page_category!=null){
        triggerIntent();
    }else{
        getWelcomeMessage(bot_id,bot_name);
        suggestion_list = get_suggestion_list(bot_id,bot_name);
        autocomplete(document.getElementById("query"), suggestion_list);              
    }
}

function get_url_vars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
        vars[key] = value;
    });
    return vars;
}

function getCsrfToken() {
    var CSRF_TOKEN = $('input[name="csrfmiddlewaretoken"]').val();
    return CSRF_TOKEN;
}

function showToast(message, duration) {
    M.toast({
        "html": message
    }, duration);
}


function getBotID(){
    bot_id = get_url_vars()["id"];
    if(bot_id==undefined || bot_id==null || bot_id=="" || bot_id=="undefined" || bot_id=="null"){
      return null;
    }
    return bot_id;
}

function getBotName(){
    bot_name = get_url_vars()["name"];
    if(bot_name==undefined || bot_name==null || bot_name=="" || bot_name=="undefined" || bot_name=="null"){
       return null;
    }
    return bot_name;
}

function show_submit_query_button(){
  $("#start_button").css("display", "none");
  $("#submit-img").css("display", "block");  
}

function show_voice_button(){
  if(voice_to_text==true){
    $("#start_button").css("display", "block");
    $("#submit-img").css("display", "none");      
  }else{
     show_submit_query_button();
  }
}

$(document).on("click","#scrollBot-img", function(e){
    $("#style-2").stop().animate({ scrollTop: $("#style-2")[0].scrollHeight}, 500);
});

$("#style-2").scroll(function() {
   if($("#style-2")[0].scrollHeight-($('#style-2').scrollTop()+$('#style-2').height()) > 100){
       $("#scrollBot-img").show(); //reached the desired point -- show div
   }else{
       $("#scrollBot-img").hide(); //reached the desired point -- show div    
   }
});

function is_mobile(){
    if( /Android|webOS|iPhone|iPad|iPod|BlackBerry/i.test(navigator.userAgent) ) {
        return true;
    } else {
        return false;
    }
}

//testing
function get_config_params()
{
    $.ajax({
        url: "/chat/get-config-params/",
        type: "POST",
        data: {
        },
        success: function(response) {
            site_title = response['site_title'];
            $('.site-title').html(site_title);
        },
        error: function(xhr, textstatus, errorthrown) {
            // console.log("Please report this error: "+errorthrown+xhr.status+xhr.responseText);
        }
    });

    bot_id = getBotID();
    if(bot_id==null){
        return;
    }

    bot_name = getBotName();
    if(bot_name==null){
       return;
    }

    $("#global-preloader").show();
    $("#chatbot-main-div").hide();

    chatbot_user_id = getCookie("ChatbotUserId");
    if(chatbot_user_id!="" && chatbot_user_id!=undefined && chatbot_user_id!=null){
        user_id = chatbot_user_id;
    }

    var json_string = JSON.stringify({
      bot_id: bot_id,
    });
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);


    $.ajax({
       url: "/chat/get-bot-message-image/",
       type: "POST",
       data: {
           json_string: json_string,
       },
       success: function(response) {
           if(response["status"]==200)
           {
              if(response['bot_message_image_url']!=null && response['bot_message_image_url']!=""){
                 MESSAGE_IMG = response['bot_message_image_url'];
              }

              BOT_THEME_COLOR = response['bot_theme_color'];

              if(response['bot_display_name']!=''){
                BOT_DISPLAY_NAME = response['bot_display_name'];
              }

              bot_terms_and_conditions = response["bot_terms_and_conditions"];
              if(bot_terms_and_conditions!=null && bot_terms_and_conditions!=""){
                  document.getElementById("bot-terms-and-condition-text").innerHTML=bot_terms_and_conditions;
                  $("#terms-condition-easychat").modal({
                      onCloseEnd: function() {
                          if(getCookie("accepted_terms_conditions")!="1"){
                            close_chatbot();
                          }
                      }
                  });
                  if(getCookie("accepted_terms_conditions")!="1"){
                    $("#terms-condition-easychat").modal("open");
                  }    
              }

              $("#chatbot_name_id").html(BOT_DISPLAY_NAME);
              $("#restart-button").css('background','#'+BOT_THEME_COLOR);
              $("#header").css("background-color",'#'+response['bot_theme_color']);
              $("#submit-img").css("color",'#'+response['bot_theme_color']+' !important');
              $("#submit").css("color",'#'+response['bot_theme_color']);
              $("#voice_btn").css('color','#'+BOT_THEME_COLOR);
              $("#start_button").css('background-color','#'+BOT_THEME_COLOR);
           }else{
               $("#header").css("background-color",'#'+BOT_THEME_COLOR+'!important');
               $("#restart-button").css('background','#'+BOT_THEME_COLOR);
               $("#submit-img").css('color','#'+BOT_THEME_COLOR);
           }

           $("#global-preloader").hide();
           $("#chatbot-main-div").show();
       },
       error: function(xhr, textstatus, errorthrown) {

       }
   });
}

var scroll_to_bottom = function() {
  $('#style-2').scrollTop($('#style-2')[0].scrollHeight);
};


function return_time() {
    var d = new Date();
    var hours = d.getHours().toString();
    var minutes = d.getMinutes().toString();
    var flagg = "AM";
    if(parseInt(hours) > 12){
        hours = hours - 12;
        flagg = "PM";
    }
    if(hours.length==1){
        hours = "0"+hours;
    }
    if(minutes.length==1){
        minutes = "0"+minutes;
    }

    var time = hours+":"+minutes+" "+flagg;
    return time;
}


function appendResponseServer(sentence, flag, url1, url2, tooltip_response){
    sentence = sentence.replace("<p>","");sentence = sentence.replace("</p>","");
    sentence = sentence.replace("<strong>","<b>");sentence = sentence.replace("</strong>","</b>");
    sentence = sentence.replace("<em>","<i>");sentence = sentence.replace("</em>","</i>");
    sentence = sentence.replace('background-color:#ffffff; color:#000000','');
    sentence = sentence.replace("background-color:#ffffff;","");

    $(".errormessage").remove();
    $(".input-field").remove();
    sentence_list = sentence.split("$$$")
    for(var i=0;i<sentence_list.length;i++){
    sentence = sentence_list[i]
    var html = ""

    if(tooltip_response==""||tooltip_response=="undefined"){
        html =
        `<div class="row chatmessage">\
            <div class="col s1 l1" >\
               <img src="`+MESSAGE_IMG+`" width=34 class="chatbot_left_image">\
            </div>\
            <div class="col s10 m10">\
               <div class="chip chip2 chip_left" >\
                  <span>`+sentence+`</span>\
               </div>\
            </div>\
            <div class="timestampl" >`+return_time()+`</div>\
        </div>`;
    }else{
      html =
      `<script>
       $(document).ready(function(){
        $('.tooltipped').tooltip();
      });
      </script>
      <div class="row chatmessage">\
          <div class="col s1 l1" >\
             <img src="`+MESSAGE_IMG+`" width=34 class="chatbot_left_image">\
          </div>\
          <div class="col s10 m10">\
             <div class="chip chip2 chip_left" >\
                <span>`+sentence+`</span>\
                <p align="right" style="margin: 0em;padding: 0em;"><i class="material-icons prefix blue-text tooltipped" data-position="bottom" data-tooltip="`+tooltip_response+`">info</i></p>\
             </div>\
          </div>\
          <div class="timestampl" >`+return_time()+`</div>\
      </div>`;
    }

    $("#style-2").append(html);
   }
}

function appendResponseError(sentence, flag, url1, url2, tooltip_response){
    sentence = sentence.replace("<p>","");sentence = sentence.replace("</p>","");
    sentence = sentence.replace("<strong>","<b>");sentence = sentence.replace("</strong>","</b>");
    sentence = sentence.replace("<em>","<i>");sentence = sentence.replace("</em>","</i>");
    sentence = sentence.replace('background-color:#ffffff; color:#000000','');
    sentence = sentence.replace("background-color:#ffffff;","");
    var html = ""

    if(tooltip_response==""||tooltip_response=="undefined"){
        html =
        `<div class="row errormessage">\
            <div class="col s1 l1" >\
               <img src="`+MESSAGE_IMG+`" width=34 class="chatbot_left_image">\
            </div>\
            <div class="col s10 m10">\
               <div class="chip chip2 chip_left" >\
                  <span>`+sentence+`</span>\
               </div>\
            </div>\
            <div class="timestampl" >`+return_time()+`</div>\
        </div>`;
    }else{
      html =
      `<script>
       $(document).ready(function(){
        $('.tooltipped').tooltip();
      });
      </script>
      <div class="row errormessage">\
          <div class="col s1 l1" >\
             <img src="`+MESSAGE_IMG+`" width=34 class="chatbot_left_image">\
          </div>\
          <div class="col s10 m10">\
             <div class="chip chip2 chip_left" >\
                <span>`+sentence+`</span>\
                <p align="right" style="margin: 0em;padding: 0em;"><i class="material-icons prefix blue-text tooltipped" data-position="bottom" data-tooltip="`+tooltip_response+`">info</i></p>\
             </div>\
          </div>\
          <div class="timestampl" >`+return_time()+`</div>\
      </div>`;
    }

    $("#style-2").append(html);
}

function append_attachment(choosen_file_type){
    // console.log("choosen_file_type inside append_attachment", choosen_file_type);

    var html =
        `<div class="row chatmessage">\
                <div class="file-field input-field col s12 m12 l6">\
                    <div class="btn blue darken-4 s6 m6" style="margin-left:15%">\
                      <span>Select File</span>\
                      <input id="upload_attachment" type="file" accept="`+ choosen_file_type +`">\
                    </div>\
                    <div class="file-path-wrapper s4 m6">\
                      <input id="upload_attachment1" class="file-path validate" type="text">\
                    </div>\
                    <div class="modal-footer col" style="margin-left:12.5%">\
                      <a class="modal-close waves-effect waves-green btn-flat grey" id="upload_button">Upload</a>\
                    </div>\
                </div>
                
        </div>`;

    
    $("#style-2").append(html);
}

function appendButtons(display_list, value_list){
    var string = '';
    for(var i=0;i<value_list.length;i++){
        string+=`
            <style>
                 .button3:hover {
                     color: white!important;
                     background-color:#`+BOT_THEME_COLOR+`;
                 }

                 .button2{
                    border: 1px solid #`+BOT_THEME_COLOR+`;
                 }
            </style>`;

        string += '<button class="button2 button3 chipbutton" style="color: #'+BOT_THEME_COLOR+'" value="'+value_list[i]+'">';
        string += display_list[i];
        string += '</button>';
    }
    var html = '\
    <div class="row chatmessage">\
        <div class="col s2 l2">\
        </div>\
        <div class="col s10 l10">\
           <div>'+
              string
           +'</div>\
        </div>\
    </div>\
    ';
    $("#style-2").append(html);
}


function appendVideo(video_url_list){

    if(video_url_list.length==0){
        return;
    }
    // console.log("inside appendVideo");

    var video_html = "";

    if(video_url_list[0].indexOf("embed")!=-1){
        var video_html = `
        <div class="video-container">
            <iframe height="250em" src="`+video_url_list[0]+`" frameborder="1" allowfullscreen></iframe>
        </div>`;
    }else{
        var video_html = `
        <video width="320" height="240" controls>
          <source src="`+video_url_list[0]+`" type="video/mp4">
        </video>`;
    }

    var html = `
    <div class="row chatmessage" style="margin-left: 4em;">
        <div class="col s11">`+video_html+`</div>
        <div class="col s1"></div>
    </div><br>`;

    $("#style-2").append(html);
}

function appendImage(image_url_list){

    if(image_url_list.length==0)
    {
        return;
    }

    var html = `<div class="col s11">  <!-- <div class="slider">
            <ul class="slides"> -->`

    for(var i=0;i<image_url_list.length;i++)
    {
        if(i==1){
          break;
        }

        html += `
             <!-- <li> -->
                <img class="materialboxed responsive-img" src="`+image_url_list[i]+`" onclick="openImageInTab(this.src)">
              <!-- </li> -->`
    }

    html +=`<!--</ul>
        </div>--> </div>`

    var image_html = `
    <div class="row chatmessage" style="margin-left: 2em;">
        `+html+`
    </div><br>`

    $("#style-2").append(image_html);

    $(document).ready(function(){
        $('.slider').slider({
            indicators:true,
            height:200,
            interval:3000,
            full_width: true
        });
    });

    $(document).ready(function(){
        $('.materialboxed').materialbox();
    });
}

function openImageInTab(src){
   window.open(src);
}

function slider_size() {
    $('#chat_slider').css("width", "199.149px");
}

function updateSlider(slideAmount) {
    // console.log("Here it is ");
    $("thumb").css("style", "left: 162.24px; height: 0px; width: 0px; top: 10px; margin-left: 7px;");
    var sliderDiv = document.getElementById("sliderAmount");
    $('#query').val(slideAmount);
    $("#start_button").css("display", "none");
    $("#submit-img").attr('src',STATIC_IMG_PATH+'/send2.png');
    $("#submit-img").css("display", "block");
    //$("#start_button").css("display", "none");}
}


function appendSlider(min_val, max_val, step_val, placeholder, element_id){

   var html = `
    <div class="row chatmessage chat_slider_chatmessage">
      <div class="col s1"></div>
      <div class="col s11"><p><b>`+placeholder+`</b></p></div>
      <div class="col s1"></div>
      <div class="col s2">
          <br>`+min_val+`
      </div>
      <div class="col s7">
      <form action="#">
        <p class="range-field">
          <input type="range" class="chat_slider" id="`+element_id+`" min="`+min_val+`" max="`+max_val+`" step="`+step_val+`" onclick="slider_size()" onchange="updateSlider(this.value)" style="width:100%;"/>
        </p>
      </form>
      </div>
      <div class="col s2">
      <br>`+max_val+`
      </div>
    </div>
    `
    $("#style-2").append(html);
    slider_size();
    putSliderValueIntoQuery();
}

function putSliderValueIntoQuery(){
   chat_slider_element = document.getElementsByClassName("chat_slider");
   var message = "";
   for(var i=0;i<chat_slider_element.length;i++){
      message += $("#"+chat_slider_element[i].id).val();
      if(i!=chat_slider_element.length-1){
         message+=", "
      }
   }
   $("#query").val(message);
   show_submit_query_button();
}


function updateDate(date) {
    $('#query').val(date);
    $("#submit-img").attr('src',STATIC_IMG_PATH+'/send2.png');
    show_submit_query_button();
}

function appendDate() {
   var html = `<div class="row chatmessage" style="margin-left: 4em;">
    <div class="col s8">
      <input type="date" onchange="updateDate(this.value)">
    </div>`;

    $("#style-2").append(html);
}


function updateDropdown(value) {
    $('#query').val(value);
    show_submit_query_button();
    $("#submit-img").click();
}

function appendDropdown(display_list, value_list){
    var html = `
    <div class="row chatmessage" style="margin-left: 4em;">
    <div class="input-field col s8">
        <select class="select_class" onchange="updateDropdown(this.value)">
          <option value="" disabled selected>Choose your option</option>`;

    for(var i=0;i<value_list.length;i++){
        html += `<option value="`+value_list[i]+`">`+display_list[i]+`</option>`
    }

    html += `</select></div>`;
    $("#style-2").append(html);
    $('select').formSelect();
}

/******************************* 

    EasySearch Google Themes

*******************************/

// function appendEasySearchCard(card_details){
//   remove_card_slider_if_exist();
//   google_search_results = card_details
//   if(google_search_results.length > 0){
//         var html =
//         `<div class="row chatmessage">\
//                 <div class="google_search_cards">
//                `;

//         for(var i=0;i<google_search_results.length;i++){
//             html += `<div value="`+google_search_results[i]["url"]+`" 
//             class="google_search_card chipgoogleresult">
//             <p class="google_search_title">`+google_search_results[i]["title"]+`<p><p class="google_search_link" style="margin-bottom:1em">
//             `+google_search_results[i]["url"]+`<p><hr><p class="google_search_description">`+google_search_results[i]["description"]+`</p></div>`;
//         }

//         html += '</div></div>';
//         $("#style-2").append(html);
//     }
//     var elements = document.getElementsByClassName("google_search_description");
//     for(var i=0; i<elements.length; i++) {
//       limitLinesOfGoogleSearchResult(elements[i], 2);
//     }
//     var elements = document.getElementsByClassName("google_search_title");
//     for(var i=0; i<elements.length; i++) {
//       limitLinesOfGoogleSearchResult(elements[i], 2);
//     }
//     var elements = document.getElementsByClassName("google_search_link");
//     for(var i=0; i<elements.length; i++) {
//       limitLinesOfGoogleSearchResult(elements[i], 1);
//     }
//     if(is_mobile()){
//      var elements = document.getElementsByClassName("google_search_cards");
//     }
// }

/*
  EasySearch Card Theme
*/

function appendEasySearchCard(card_details){

  remove_card_slider_if_exist();
  card_title_list = []
  card_display_url = []
  card_url_list = []
  card_content_list = []

  for(i=0;i<card_details.length;i++){
      title = card_details[i]["title"]
      //img_url = card_details[i]["img_url"]
      url = card_details[i]["url"]
      display_url = card_details[i]["display_url"]
      content = card_details[i]["description"]

      card_title_list.push(title);
      //card_img_url_list.push(img_url);
      card_url_list.push(url);
      card_display_url.push(display_url)
      card_content_list.push(content);
  }
  var card_html = `<div style="width:100%; margin-top:0.2em; display:inline-block;" id="easychat-slideshow-container-main-div-card">
      <div class="easychat-slideshow-container">`;


  var total_cards = card_details.length;
  var current_card_no = 0;
  for(i = 0; i < card_details.length; i++){
    current_card_no = i + 1;
    card_html += `<div class="easychat-slideshow-slides-cards fade">
                    <div class="easychat-slideshow-numbertext">`+current_card_no+` / `+total_cards+`</div>
                    <a href="`+card_url_list[i]+`" target="_blank">
                      <div class="row chatmessage" style="margin-left: 4em;">
                        <div class="col s10">
                          <div class="card">`;
                          card_html += `<div class="card-content" style="border: black;">
                      <span class="card-title activator black-text text-darken-4 center" style="font-size:15px;"><u>`+card_title_list[i]+`</u></span>
                      </br>
                      <p style="font-size:15px;color:#`+BOT_THEME_COLOR+`;">`+card_content_list[i]+`</p>
                  </div>
                  </div>
                </div>
              </div></a></div>`;
  }
  if(card_details.length >1){
  card_html += `<a class="easychat-slideshow-prev" onclick="plusSlidesCards(-1)" style="background-color:#`+BOT_THEME_COLOR+`;">&#10094;</a>
          <a class="easychat-slideshow-next" onclick="plusSlidesCards(1)" style="background-color:#`+BOT_THEME_COLOR+`;">&#10095;</a>
        </div><br><div style="text-align:center">`;
    
    for(var i=0;i<card_details.length;i++){
        current_card_no=i+1;
        card_html += `<span class="easychat-slideshow-dot-cards" onclick="currentSlideCards(`+current_card_no+`)"></span>`;
    }
  }
        
  card_html += `</div></div><br>`;

  $("#style-2").append(card_html);

  if(card_details.length >1){
    slideIndexCard = 1;
    showSlidesCards(slideIndexCard);
  }
  scroll_to_bottom();
}


function appendCard(card_details){

  remove_card_slider_if_exist();
  card_title_list = []
  card_img_url_list = []
  card_url_list = []
  card_content_list = []

  for(i=0;i<card_details.length;i++){
      title = card_details[i]["title"]
      img_url = card_details[i]["img_url"]
      url = card_details[i]["link"]
      content = card_details[i]["content"]

      card_title_list.push(title);
      card_img_url_list.push(img_url);
      card_url_list.push(url);
      card_content_list.push(content);
  }

  var card_html = `<div style="width:100%; margin-top:0.2em; display:inline-block;" id="easychat-slideshow-container-main-div-card">
      <div class="easychat-slideshow-container">`;


  var total_cards = card_details.length;
  var current_card_no = 0;

  for(i = 0; i < card_details.length; i++){
    current_card_no = i + 1;
    card_html += `<div class="easychat-slideshow-slides-cards fade">
                    <div class="easychat-slideshow-numbertext">`+current_card_no+` / `+total_cards+`</div>
                      <div class="row chatmessage" style="margin-left: 4em;">
                        <div class="col s11">
                          <div class="card">`;

                          if(card_img_url_list[i].trim()!=""){
                            card_html += `<div class="card-image waves-effect waves-block waves-light">
                            <img class="activator responsive-image" src="`+card_img_url_list[i]+`" style="height:5em;width:6em;">
                            </div>`              
                          }  
                
                    card_html += `<div class="card-content" style="border: black;">
                      <span class="card-title activator grey-text text-darken-4" style="font-size:15px;">`+card_title_list[i]+`<i class="material-icons right">more_vert</i></span>
                      <p>
                        <a href="`+card_url_list[i]+`" target="_blank">Please click here</a>
                      </p>
                    </div>
                    <div class="card-reveal">
                      <span class="card-title grey-text text-darken-4" style="font-size:15px;">`+card_title_list[i]+`<i class="material-icons right">close</i></span>
                      <p style="font-size:15px;">`+card_content_list[i]+`</p>
                    </div>
                  </div>
                </div>
              </div></div>`;
  }
  card_html += `<a class="easychat-slideshow-prev" onclick="plusSlidesCards(-1)" style="background-color:#`+BOT_THEME_COLOR+`;">&#10094;</a>
          <a class="easychat-slideshow-next" onclick="plusSlidesCards(1)" style="background-color:#`+BOT_THEME_COLOR+`;">&#10095;</a>
        </div><br><div style="text-align:center">`;

  for(var i=0;i<card_details.length;i++){
      current_card_no=i+1;
      card_html += `<span class="easychat-slideshow-dot-cards" onclick="currentSlideCards(`+current_card_no+`)"></span>`;
  }
        
    card_html += `</div></div><br>`;

  $("#style-2").append(card_html);

  slideIndexCard = 1;
  showSlidesCards(slideIndexCard);
  scroll_to_bottom();
}

function appendResponseUser(sentence){
    sentence = sentence.replace("<p>","");sentence = sentence.replace("</p>","");
    sentence = sentence.replace("<","#");sentence = sentence.replace(">","#");

    var html =
    `<script>
     $(document).ready(function(){
      $('.tooltipped').tooltip();
    });
    </script>

    <div class="row chatmessage">\
        <div class="col s3">\
        </div>\
        <div class="col s9">\
            <div class="chip chip2 right chip_right" style="background-color: #`+BOT_THEME_COLOR+`">\
                <span>`+sentence+`</span>\
            </div>\
        </div>\
        <div class="timestampr" >`+return_time()+`</div>\
    </div>`;
    $("#style-2").append(html);
    scroll_to_bottom();
    clearTimeout(timer_var)
}

function appendRecommendationsList(list){
    if(list.length > 0){
        var html =
        '<div class="row chatmessage">\
            <div class="col s2">\
            </div>\
            <div class="col s9 l9">\
               <div class="button-group button-group2" style="margin-top:4px;">\
               ';

        for(var i=0;i<list.length;i++){
            html += '<div class="button recommendation_style chiprecommendation" style="color: #'+BOT_THEME_COLOR+'">'+list[i]+'</div>';
        }

        html += '</div></div></div>';
        $("#style-2").append(html);
    }
}

function appendGoogleSearchResultsList(google_search_results){
    //console.log(discrptnlist)
    if(google_search_results.length > 0){
        var html =
        `<div class="row chatmessage">\
                <div class="google_search_cards">
               `;

        for(var i=0;i<google_search_results.length;i++){
            html += `<div value="`+google_search_results[i]["google_search_link"]+`" 
            class="google_search_card chipgoogleresult">
            <p class="google_search_title">`+google_search_results[i]["google_search_title"]+`<p><p class="google_search_link" style="margin-bottom:1em">
            `+google_search_results[i]["google_search_link"]+`<p><hr><p class="google_search_description">`+google_search_results[i]["google_search_descrptn"]+`</p></div>`;
        }

        html += '</div></div>';
        $("#style-2").append(html);
    }
  var elements = document.getElementsByClassName("google_search_description");
  for(var i=0; i<elements.length; i++) {
      limitLinesOfGoogleSearchResult(elements[i], 2);
  }
  var elements = document.getElementsByClassName("google_search_title");
  for(var i=0; i<elements.length; i++) {
      limitLinesOfGoogleSearchResult(elements[i], 2);
  }
  var elements = document.getElementsByClassName("google_search_link");
  for(var i=0; i<elements.length; i++) {
      limitLinesOfGoogleSearchResult(elements[i], 1);
  }
  if(is_mobile()){
    var elements = document.getElementsByClassName("google_search_cards");
    elements[elements.length-1].classList.add("hide_scrollbar");
    }
}

function limitLinesOfGoogleSearchResult(el, nLines) {
  j=0;
  while(j<2){
  var nHeight,
    el2 = el.cloneNode(true);
  el2.style.position = 'absolute';
  el2.style.top = '0';
  el2.style.width = '10%';
  el2.style.overflow = 'hidden';
  el2.style.visibility = 'hidden';
  el2.style.whiteSpace = 'nowrap';
  el.parentNode.appendChild(el2);
  nHeight = (el2.clientHeight+2)*nLines; 
  el.parentNode.removeChild(el2);
  el2 = null;
  if (el.clientHeight > nHeight) {
    var i = 0,
      imax = nLines * 35;
    while (el.clientHeight > nHeight) {
      el.innerHTML = el.textContent.slice(0, -2) + '&hellip;';
      ++i;
      if (i === imax) break;
    }
  }
  j=j+1
}
}


$(document).ready(function() {
    document.cookie = Math.random();
    if(is_mobile()){
    }else{
        $("#query").focus();
    }
    $("#navig").css("background-color","#FFF");
    $("#submit-img").attr('src',STATIC_IMG_PATH+'/send1.png');
});

function enableInput(query){
    $("#query").removeAttr('disabled');
    $("#query").attr("placeholder","Please type your query here.");
}

function disableInput(){
    $('#query').val("");
    $('#query').attr('placeholder','Please select an option from the above choices');
    $("#query").attr('disabled','disabled');
}

$(document).on("keyup","#query",function (e) {
    var key = e.which;
    if(key == 13)
    {
        $('#submit-img').click();
        return false;
    }
});

function appendGoogleMap() {
  current_latitude = ""
  current_longitude = ""
  if (("geolocation" in navigator)) {
    // check if geolocation is supported/enabled on current browser
    navigator.geolocation.getCurrentPosition(
     function success(position) {
       // for when getting location is a success
       console.log('latitude', position.coords.latitude,
                   'longitude', position.coords.longitude);
        current_latitude = position.coords.latitude
        current_longitude = position.coords.longitude
     },
    function error(error_message) {
      // for when getting location results in an error
      console.error('An error has occured while retrieving' +
                    'location before', error_message)
      // alert("error has occured before")
      // alert(error_message)
      ajaxCallToIndex("Share Pincode", API_SERVER_URL)
      return;
    });
  } else {
    // alert("geolocation is not supported before")
    // geolocation is not supported
    // get your location some other way
    console.log('geolocation is not enabled on this browser')
    ajaxCallToIndex("Share Pincode", API_SERVER_URL)
    return;
  }

  $("#map").empty();

  html = `
      <style>
        #map`+mapId+` {
          height: 100%;
        }
        html, body {
          height: 100%;
          margin: 0;
          padding: 0;
        }
      </style>
      <div id="map`+mapId+`"></div>

      <script>

      var lat_coord = ""
      var lng_coord = ""
      var map;
      var setMarker = false; ////Has the user plotted their location marker?
      var marker = ""

      var myLatlng = ""
      if (("geolocation" in navigator)) {
        // check if geolocation is supported/enabled on current browser
        navigator.geolocation.getCurrentPosition(
         function success(position) {
           // for when getting location is a success
           console.log('latitude', position.coords.latitude,
                       'longitude', position.coords.longitude);
           // getAddress(position.coords.latitude,
           //            position.coords.longitude)
         lat_coord = position.coords.latitude
         lng_coord = position.coords.longitude
         var pos = {
              lat: position.coords.latitude,
              lng: position.coords.longitude
            };

            if(setMarker==true){
              console.log("set marker is true")
              console.log("postition is ",pos)
               map.setCenter(pos);
               marker.setPosition(map.getCenter());

            }else{
            }


         // alert(lat_coord)
         // alert(lng_coord)
         },
        function error(error_message) {
          // for when getting location results in an error
          console.error('An error has occured while retrieving' +
                        'location', error_message)
          // alert("error has occured")
          // alert(error_message)
        });
      } else {
        console.log('geolocation is not enabled on this browser')
      }

        function initMap() {
          // var myLatlng = new google.maps.LatLng(19.108290,72.878370);
          var myLatlng = new google.maps.LatLng(lat_coord,lng_coord);
          map = new google.maps.Map(document.getElementById('map`+mapId+`'), {
            center: myLatlng,
            zoom: 15
          });
          console.log("position coordinate ",myLatlng)
          var centerControlDiv = document.createElement('div');
          var centerControl = new CenterControl(centerControlDiv, map);

          centerControlDiv.index = 1;
          map.controls[google.maps.ControlPosition.BOTTOM_CENTER].push(centerControlDiv);


          if(setMarker==false){
            marker = new google.maps.Marker({
              position: myLatlng,
              map: map,
              draggable:true,
              title:"Drag me!"
          });
            setMarker=true;
            map.addListener('drag', function(e) {
              // placeMarkerAndPanTo(e.latLng, map);
              placeMarkerAndPanTo(map.getCenter(), map);
            });
            console.log("set marker is false")
          }else{
           marker.setPosition(map.getCenter());
          console.log("set marker is true")
          }
      }

      function placeMarkerAndPanTo(latLng, map) {
           marker.setPosition(map.getCenter());
           console.log('set position', latLng)
      }

      function CenterControl(controlDiv, map) {

          // Set CSS for the control border.
          var controlUI = document.createElement('div');
          controlUI.style.backgroundColor = '#fff';
          controlUI.style.border = '2px solid #fff';
          controlUI.style.borderRadius = '3px';
          controlUI.style.boxShadow = '0 2px 6px rgba(0,0,0,.3)';
          controlUI.style.cursor = 'pointer';
          controlUI.style.marginBottom = '22px';
          controlUI.style.textAlign = 'center';
          controlUI.title = 'Click to Submit the location';
          controlDiv.appendChild(controlUI);

          // Set CSS for the control interior.
          var controlText = document.createElement('div');
          controlText.style.color = 'rgb(25,25,25)';
          controlText.style.fontFamily = 'Roboto,Arial,sans-serif';
          controlText.style.fontSize = '16px';
          controlText.style.lineHeight = '38px';
          controlText.style.paddingLeft = '5px';
          controlText.style.paddingRight = '5px';
          controlText.innerHTML = 'Submit your location';
          controlUI.appendChild(controlText);

          // Setup the click event listeners: simply set the map to Chicago.
          controlUI.addEventListener('click', function() {
            var lat = marker.getPosition().lat();
            var lng = marker.getPosition().lng();
            console.log("lat lng  is ",lat+"__"+lng)
            console.log("button clicked")
            $("#map`+mapId+`").hide()
            ajaxCallToIndex(lat+"__"+lng,API_SERVER_URL)
          });

        }
      </script>`;

      if(isMapJsLoaded==0){
        html+=`<script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBAHTtk1lkVvIl1X_i7_1aIK9RCrhqGEpQ&callback=initMap" defer></script>`;
      }
      mapId+=1;
      $("#style-2").append(html);
}

var speech_synthesis_utterance_instance = null;
var speech_synthesis_instance = window.speechSynthesis;
var voices = null;

function cancelTextToSpeech(){
  if(speech_synthesis_instance!=null){
      speech_synthesis_instance.cancel();
  }  
}

function textToSpeech(message_to_be_spoken){
    cancelTextToSpeech();
    speech_synthesis_utterance_instance = new SpeechSynthesisUtterance(message_to_be_spoken);
    speech_synthesis_utterance_instance.lang="en-US";
    speech_synthesis_utterance_instance.rate = 0.95;
    speech_synthesis_utterance_instance.pitch = 1;
    speech_synthesis_utterance_instance.volume = 1;
    voices = speech_synthesis_instance.getVoices();
    speech_synthesis_instance.speak(speech_synthesis_utterance_instance);
}

var is_flow_ended=true;

function appendServerChat(data) {

    remove_image_slider_if_exist();

    if(data['response']["text_response"]["modes"]['check_ticket_status']=="true") 
    {
        $('#modal-check-ticket-status').modal({
            onCloseEnd: function() {
               enableInput();
            }            
        });
        $('#modal-check-ticket-status').modal('open');
        return;
    }
    if(data['response']["text_response"]["modes"]['check_meeting_status']=="true") 
    {
        $('#modal-check-meeting-status').modal({
            onCloseEnd: function() {
               enableInput();
            }            
        });
        $('#modal-check-meeting-status').modal('open');
        return;
    }
    if(data['response']["text_response"]["modes"]['schedule_meeting']=="true") 
    {
        $('#modal-schedule-meeting').modal({
            onCloseEnd: function() {
               enableInput();
            }            
        });
        $('#modal-schedule-meeting').modal('open');
        return;
    }
    if(data['response']["text_response"]["modes"]['raise_service_request']=="true") 
    {
        $('#modal-create-issue').modal({
            onCloseEnd: function() {
               enableInput();
            }            
        });
        $('#modal-create-issue').modal('open');
        return;
    }
    var sentence = "";
    var tooltip_response = "";
    if(data['status_code']=="200"){
      sentence = data['response']['text_response']['text'];
      text_speech = data['response']['speech_response']['text'];

      if(data["response"]["is_text_to_speech_required"]==true){
        textToSpeech(text_speech);
      }

      if(data['response']['tooltip_response']){
        tooltip_response = data['response']['tooltip_response']
      }else{
        tooltip_response = "";
      }
    }else{
      sentence = data['status_message'];
      tooltip_response = "";
    }
   // appendResponseServer(sentence, false, "", "", tooltip_response);

    if(data["bot_id"] == 234){

      var sentence_list = sentence.split("@@@");
      appendResponseServer(sentence_list[0], false, "", "", tooltip_response);
    }else{

      appendResponseServer(sentence, false, "", "", tooltip_response);
    }

    if("auto_trigger_last_intent" in data['response']["text_response"]["modes"] && data['response']["text_response"]["modes"]["auto_trigger_last_intent"]=="true"){
        if(data["response"]["last_identified_intent_name"]!=null && data["response"]["last_identified_intent_name"]!="None"){
            ajaxCallToIndex(data["response"]["last_identified_intent_name"], API_SERVER_URL);
            return;
        }
    }

    if(data["is_attachment_required"]==true){

      var choosen_file_type = data["choosen_file_type"];
      
      choosen_file_type = choosen_file_type.replace(/"/g,'');
      choosen_file_ext = file_type_ext[choosen_file_type];
      append_attachment(choosen_file_ext);
    }

    choices = [];
    if("choices" in data["response"]){
      choices = data['response']['choices'];      
    }

    cards = [];
    if("cards" in data["response"]){
      cards = data["response"]["cards"];      
    }

    images = [];
    if("images" in data["response"]){
      images = data["response"]["images"];      
    }

    videos = [];
    if("videos" in data["response"]){
      videos = data["response"]["videos"];      
    }

    display_list = []
    value_list = []
    for(i=0;i<choices.length;i++){
        display_list.push(choices[i]["display"]);
        value_list.push(choices[i]["value"]);
    }

    if(data["response"]["text_response"]["modes"]["is_button"]=="true"){
        appendButtons(display_list, value_list);
    }   

    is_flow_ended = data["response"]["is_flow_ended"];

    if(data['response']["text_response"]["modes"]['is_slidable']=="true") {

        list_of_sliders = data['response']['text_response']["modes_param"]["is_slidable"];

        for(var i=0;i<list_of_sliders.length;i++){
           var slider_min = data['response']['text_response']["modes_param"]["is_slidable"][i]["min"];
           var slider_max = data['response']['text_response']["modes_param"]["is_slidable"][i]["max"];
           var slider_step = data['response']['text_response']["modes_param"]["is_slidable"][i]["step"];
           var placeholder = data['response']['text_response']["modes_param"]["is_slidable"][i]["placeholder"];
           appendSlider(slider_min, slider_max, slider_step, placeholder, "chat_min_max_slider_"+i);
        }
    }
    if(data['response']["text_response"]["modes"]['is_date']=="true") {
        appendDate();
    }

    if(data['response']["text_response"]["modes"]['is_dropdown']=="true") {
        appendDropdown(display_list, value_list);
    }
    if(data['response']["easy_search_results"].length!=0){
        appendEasySearchCard(data["response"]["easy_search_results"]);
    }


    if(data['response']["recommendations"].length!=0){
        appendRecommendationsList(data["response"]["recommendations"]);
    }

    if(data['response']["google_search_results"].length!=0){
        appendGoogleSearchResultsList(data["response"]["google_search_results"]);
    }
    
    is_typable = data['response']['text_response']['modes']['is_typable'];

    is_location_required = data['response']['text_response']['modes']['is_location_required'];

    if(cards.length!=0){
        appendCard(cards);
    }

    if(is_typable=="false")
        disableInput();
    else
        enableInput();

    if(images.length!=0){
      append_bot_slider_images(images);
    }

    if(videos.length!=0){
       appendVideo(videos);
    }

    if(is_location_required){
        appendGoogleMap();
    }

    if(data['response']["text_response"]["modes"]['is_livechat']=="true") {
       append_livechat_response();
       is_livechat = true;
    }

    if(sentence_list != undefined){
      if(data["bot_id"] == 1 && sentence_list.length > 1){

        appendResponseServer(sentence_list[1], false, "", "", tooltip_response);
      }
    }
}

function playSound(filename){
    var mp3Source = '<source src="' + filename + '" type="audio/mpeg">';
    document.getElementById("sound").innerHTML='<audio autoplay="autoplay">' + mp3Source + '</audio>';
}

function ajaxCallToIndex(sentence, url){

    $("#style-2").append(`<div class="typing-loader"></div>`);
    $(".typing-loader").show();
    scroll_to_bottom();

    var channel_params = "";
    channel_params = JSON.stringify({
        "is_form_assist":is_form_assist,
        "session_id":session_id,
        "window_location":window_location
    });

    if(is_file_attached){
      channel_params = JSON.stringify({
          "attachment_url": attachment_url,
          "is_form_assist":is_form_assist,
          "is_file_attached": true
      });
      is_file_attached = false;
    }
    console.log(bot_id)
    var json_string = JSON.stringify({
      message: sentence,
      user_id: user_id,
      channel: "Web",
      channel_params: channel_params,
      bot_id: bot_id,
      bot_name: bot_name,
      bot_display_name: bot_name,
      is_attachment_required: false,
      choosen_file_type: "none"
    });
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    $.ajax({
        url: url,
        type: "POST",
        data: {
            json_string: json_string
        },
        success: function(data){

          console.log(data["response"]["cards"]);
            if(isSafari){
                show_submit_query_button();
            }else{
                show_voice_button();
            }

            user_id = data['user_id'];
            bot_id = data['bot_id'];
            setCookie("ChatbotUserId", user_id);
            is_form_assist = "false";

            // if(sentence=="हिंदी में देखें।"){

            // }

            if(data['timer_value']){
              timer_var = setTimeout(function(){
                ajaxCallToIndex(data['auto_response'], API_SERVER_URL);
              }, data['timer_value']);
            }

            setTimeout(function(){
                $(".typing-loader").remove();
                appendServerChat(data);
                playSound(STATIC_MP3_PATH+"/popup.mp3");
                document.getElementById('query').value='';
                if(!is_mobile()){
                    $("#query").focus();
                }
                scroll_to_bottom();
            }, 500);
        },
        error: function (jqXHR, exception) {
           appendResponseServer(BOT_DISPLAY_NAME+" bot is under maintenance, Please try again after some time. Sorry for your inconvenience.", false, "", "","", "");
           scroll_to_bottom();
        },
    });
}


function GetWelcomeResponse(channel, bot_id, bot_name){
    url_parameters = get_url_vars();
    var json_string = JSON.stringify({
      channel_name: channel,
      bot_id: bot_id,
      bot_name: bot_name,
      user_id: user_id,
      session_id: session_id,
      bot_web_page: decodeURIComponent(url_parameters["easychat_window_location"]),
      web_page_source: decodeURIComponent(url_parameters["web_page_source"])      
    })

    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);
    var response = $.ajax({
        url: "/chat/get-channel-details/",
        type: "POST",
        async: false,
        data: {
            json_string: json_string
        },
        success: function(data){
            
            return data;
        },
        error: function (jqXHR, exception) {
             appendResponseServer(BOT_DISPLAY_NAME+" bot is under maintenance, Please try again after some time. Sorry for your inconvenience.", false, "", "","");
             scroll_to_bottom();
             return null;
        },
    }).responseJSON;

    return response;
}

// function getPrevSessionHistory(prev_session_id){
//   var response = $.ajax({
//         url: "/chat/get-prev-session-history/",
//         type: "POST",
//         async: false,
//         data: {
//             prev_session_id:prev_session_id,
//         },
//         success: function(response){
//           console.log(response)
//           if (response['status']==200){
//             for (i = response["prev_msg_histry"].length-1; i>=0; i--) {
//               appendResponseUser(response["prev_msg_histry"][i]["user_msg"])
//               appendResponseServer(response["prev_msg_histry"][i]["bot_response"], false, "", "","");
//               scroll_to_bottom();
//             }
//           }
//         },
//         error: function (jqXHR, exception) {
//         },
//     }).responseJSON;
// }

function getWelcomeMessage(bot_id,bot_name)
{
    channel_details = GetWelcomeResponse("Web", bot_id,bot_name);
  
    if(channel_details==null){
       return;
    }

    user_id = channel_details["user_id"];
    message = channel_details["welcome_message"];
    speech_message = channel_details["speech_message"];

    featues_list = channel_details["initial_messages"]["items"];
    is_text_to_speech_required = channel_details["is_text_to_speech_required"];
    bot_start_conversation_intent = channel_details["bot_start_conversation_intent"];

    images = []
    if("images" in channel_details["initial_messages"]){
      images = channel_details["initial_messages"]["images"];
    }
    videos = []
    if("videos" in channel_details["initial_messages"]){
      videos = channel_details["initial_messages"]["videos"];
    }

    setTimeout(function(){
        appendResponseServer(message,"","","","");
        if(images.length>0){
          appendImage(images);
        }
        if(videos.length>0){
          appendVideo(videos);
        }
        appendRecommendationsList(featues_list);
        playSound(STATIC_MP3_PATH+"/popup.mp3");
        is_restart_allow=true;

        if(is_text_to_speech_required==true && speech_message!=""){
           textToSpeech(speech_message);
        }

        // prev_session_id = getCookie("easychat_prev_session_id");
        // console.log(prev_session_id)
        // if (prev_session_id!="")
        // {
        //   getPrevSessionHistory(prev_session_id)
        //   setCookie("easychat_prev_session_id","")
        //   prev_session_id = getCookie("easychat_prev_session_id");
        //   console.log(prev_session_id)
        // }
        
        if(bot_start_conversation_intent!=null && bot_start_conversation_intent!=""){
            ajaxCallToIndex(bot_start_conversation_intent, API_SERVER_URL);   
        }
    }, 500);
}

$(document).on("click","#submit-img", function(e){

    if(($.trim($('#query').val()) != '') && ($("#query").val()).length<300){
        var sentence = $("#query").val();
        sentence = $($.parseHTML(sentence)).text();
        if (sentence.length == 0) {      // error!
          $("#query").val("");
          return;
        }
        $("#query").val("");
        appendResponseUser(sentence);
        
        if(is_livechat==true){
             save_customer_chat(sentence, room_name);
             var sentence = JSON.stringify({
                 'message': sentence,
                 'sender': 'user'
             });
             chat_socket1.send(sentence);
             return;
        }
        else{
          disableInput();
          ajaxCallToIndex(sentence, API_SERVER_URL);
        }
        $("#submit-img").attr('src',STATIC_IMG_PATH+'/send1.png');
    }
    else{

    }

    if(document.getElementsByClassName("chat_slider").length>0){
       $(".chat_slider_chatmessage").remove();
    }
});


$(document).on("click", "#upload_button",function(e){  

  $("#style-2").append(`<div class="typing-loader"></div>`);
  $(".typing-loader").show();
  scroll_to_bottom();                                                                                                                                                                                                                                                                                                                                                                                                           
  e.preventDefault();
  var choosen_file_type = "none";
  var upload_attachment = ($("#upload_attachment"))[0].files[0]

  if(upload_attachment == "" || upload_attachment == null || upload_attachment == undefined){

    choosen_file_type = document.getElementById("upload_attachment").accept;
    $(".input-field").remove();
    sentence = "Opps...<br>You haven't selected any file.<br>Please select you file.";
    $(".typing-loader").remove();
    appendResponseError(sentence, "", "", "", "");
    append_attachment(choosen_file_type);
    scroll_to_bottom();
    return;
  }

  if(upload_attachment.size >= 5 * 1024 * 1024){

    choosen_file_type = document.getElementById("upload_attachment").accept;
    $(".input-field").remove();
    sentence = "Opps...<br>File size id too large. <br>Please select a file of size less than 5MB.";
    $(".typing-loader").remove();
    appendResponseError(sentence, "", "", "", "");
    append_attachment(choosen_file_type);
    scroll_to_bottom();
    return;
  }
  
  var formData = new FormData();
  var CSRF_TOKEN = $('input[name="csrfmiddlewaretoken"]').val();
  formData.append("upload_attachment", upload_attachment);                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          

  sentence = "Thank you! <br>your file has been uploaded.<br>";

  $.ajax({
      url: "/chat/upload-attachment/",
      type: "POST",
      headers: {
          'X-CSRFToken': CSRF_TOKEN
      },
      data: formData,
      processData: false,
      contentType: false,
      success: function(data){

        sentence += "You can find your file here:<br>" + window.location.origin + data["src"];
        $(".typing-loader").remove();
        appendResponseServer(sentence, "", "", "", "");
        is_file_attached = true;
        attachment_url = data["src"];

        if(is_flow_ended==false){
          ajaxCallToIndex("attachment", API_SERVER_URL);
        }
        scroll_to_bottom();
      },
      error: function (jqXHR, exception) {
         appendResponseServer(BOT_DISPLAY_NAME+" bot is under maintenance, Please try again after some time. Sorry for your inconvenience.", false, "", "","", "");
         scroll_to_bottom();
      },
  }); 
});


var is_restart_allow = true;

$('body').on('click','#restart-button', function(){
    restart_chatbot();
});


function restart_chatbot(call_type="restart") {
  if(livechat_queue_timer){
    clearInterval(livechat_queue_timer);
  }
  remove_queue_timer();
  $(".chatmessage").remove();
  $(".easychat-slideshow-prev").remove()
  remove_card_slider_if_exist();
  remove_image_slider_if_exist();
  clearTimeout(timer_var);
  enableInput("");
  // console.log("restart_chatbot");
  save_time_spent();

  if(!is_restart_allow){
     return;
  }

  if(livechat==true){
      $.ajax({
        url: "/chat/delete-livechat-session/",
        type: "POST",
        data: {
          user_id:user_id,
        },
        success: function(response) {

        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: "+errorthrown+xhr.status+xhr.responseText);
        }
      });
      chatSocket.close()
      livechat=false
  }

  is_restart_allow=false;
  var json_string = JSON.stringify({
    user_id: user_id,
  });
  json_string = EncryptVariable(json_string);
  json_string = encodeURIComponent(json_string);
  $.ajax({
      url: CLEAR_API_URL,
      type: "POST",
      data: {
          json_string: json_string,
      },
      success: function(data){
          $("#query").val("");
          $("#submit-img").attr('src',STATIC_IMG_PATH+'/send1.png');
          if(call_type == "restart")
            getWelcomeMessage(bot_id,bot_name);
      }
  });
}

$('body').on('click','#minimize-chatbot', function(){
    parent.postMessage('minimize-chatbot','*');
});

$('body').on('click','#close-chatbot', function(){
  
  if(livechat==true)
  {
    $.ajax({
      url: "/chat/delete-livechat-session/",
      type: "POST",
      data: {
        user_id:user_id,
      },
      success: function(response) {
        
      },
      error: function(xhr, textstatus, errorthrown) {
          console.log("Please report this error: "+errorthrown+xhr.status+xhr.responseText);
      }
    });
    chatSocket.close()
    livechat=false
  }

  if (user_id=="" || getCookie("isFeedbackDone")=="1") {
    close_chatbot()
  }
  else{
  document.getElementById("style-2").style.opacity="0.3"
  document.getElementById("style-2").style.pointerEvents="none"
  document.getElementById("feedback_box_container").style.display="block"
  document.getElementById("feedback_box_container").style.backgroundColor='#'+BOT_THEME_COLOR
  document.getElementById("submit-feedback").style.backgroundColor='#'+BOT_THEME_COLOR
  }

   // $('#allincall-chat-box', window.parent.document).hide("slow");
   // $('#allincall-popup', window.parent.document).show("slow");
   //parent.postMessage('close-bot','*')
});

$('body').on('click','#submit-feedback', function(){
  setCookie("isFeedbackDone","1");
  rating=document.querySelector('input[name="emoji"]:checked').value;
  comments=document.getElementById("comment-box").value;
  save_feedback(user_id,bot_id,rating,comments);
  close_chatbot();
});

$('body').on('click','#close-feedback-form', function(){
  close_feedback_form();
});

$('body').on('click','#no-feedback-given', function(){
  setCookie("isFeedbackDone","1");
  close_chatbot();
});

function setCookie(cookiename,cookievalue) {
  document.cookie = cookiename + "="+cookievalue;
}

function getCookie(cookiename) {
  var cookie_name = cookiename + "=";
  var decodedCookie = decodeURIComponent(document.cookie);
  var cookie_array = decodedCookie.split(';');
  for(var i = 0; i < cookie_array.length; i++) {
    var c = cookie_array[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(cookie_name) == 0) {
      return c.substring(cookie_name.length, c.length);
    }
  }
  return "";
}

function open_cobrowsing(argument) {
  parent.postMessage('share-screen','*')
}

function stop_form_assist(argument) {
  parent.postMessage('stop-form-assist','*')
}

function close_chatbot(argument) {
  
  last_action = "close_bot";
  parent.postMessage('close-bot','*')
  close_feedback_form();
  restart_chatbot("close");
}

function save_time_spent(){

  $.ajax({
    url: "/chat/save-time-spent/",
    type: "POST",
    data: {
      user_id:user_id,
      session_id:session_id
    },
    success: function(response) {
    },
    error: function(xhr, textstatus, errorthrown) {
        // console.log("Please report this error: "+errorthrown+xhr.status+xhr.responseText);
    }
  });
}

function save_feedback(user_id,bot_id,rating,comments) {
  var json_string = JSON.stringify({
    session_id: session_id,
    user_id: user_id,
    bot_id: bot_id,
    rating: rating,
    comments: comments
  });
  json_string = EncryptVariable(json_string);
  json_string = encodeURIComponent(json_string);

  $.ajax({
      url: "/chat/save-feedback/",
      type: "POST",
      data: {
        json_string: json_string
      },
      success: function(response) {
      },
      error: function(xhr, textstatus, errorthrown) {
          // console.log("Please report this error: "+errorthrown+xhr.status+xhr.responseText);
      }
  });
}

function close_feedback_form() {
  document.getElementById("style-2").style.opacity="1"
  document.getElementById("feedback_box_container").style.display="none"
  document.getElementsByClassName("feedback_comment-box-div")[0].style.display="none"
  document.getElementById("style-2").style.pointerEvents="all"
  var ele = document.getElementsByName("emoji");
   for(var i=0;i<ele.length;i++){
      ele[i].checked = false;
   }
  document.getElementById("comment-box").value="";
}

$('body').on('click','#logo-container', function(){
    if(!is_mobile()){
        $("#query").focus();
    }
});

$(document).on("input", "#query", function(e){
    var value = $("#query").val();
    if($.trim($('#query').val()) == ''){
        $("#submit-img").attr('src',STATIC_IMG_PATH+'/send1.png');
    }else{
        $("#submit-img").show();
        $("#submit-img").attr('src',STATIC_IMG_PATH+'/send2.png');
    }
});

$(document).on('click','.button2', function(){
    $(this).css('background-color', '#'+BOT_THEME_COLOR);
    $(this).css('color', 'white');
    $('.button2').attr('disabled', "");
    $('.button2').attr('class', 'button2 chipbutton');
    var sentence = $(this).html();
    if(sentence.indexOf("thumbs-up-filled")!=-1){
        sentence = "Helpful";
    }else if(sentence.indexOf("thumbs-down-filled")!=-1){
        sentence = "Unhelpful";
    }
    value = $(this).val();
    appendResponseUser(sentence);
    ajaxCallToIndex(value, API_SERVER_URL);
    $("#submit-img").attr('src',STATIC_IMG_PATH+'/send1.png');
});

$(document).on('click','.chiprecommendation', function(){
    $(this).css('background-color', '#'+BOT_THEME_COLOR);
    $(this).css('color', 'white');
    var sentence = $(this).html();
    appendResponseUser(sentence);
    // if(sentence=="हिंदी में देखें।" && is_form_assist==true){
    //   var hindi_message = welcome_form_assist["hinglish_response"];
    //   appendResponseServer(hindi_message, false, "", "","");
    //   scroll_to_bottom();
    //   is_hindi_user = true;
    //   setTimeout(giveSuggestions,1000);
    // }
    // else if(sentence=="Yes" && is_form_assist==true){
    //   appendResponseServer("Please select the mode of assistance:", false, "", "", "");
    //   var assist_options = ["Chat with an expert", "Call with an expert", "Meeting with an expert"];
    //   appendRecommendationsList(assist_options);
    //   scroll_to_bottom();
    //   stop_form_assist();
    // }
    // else if(sentence=="No" && is_form_assist==true){
    //   close_chatbot();
    // }
    // else if(sentence=="Call with an expert" && is_form_assist==true){
      
    //   scroll_to_bottom();
    //   flag_timer = true;
    //   clearTimeout(timer_var);
    //   open_cobrowsing();
      
    // }
    // else{
      // clearTimeout(timer_var);
      // flag_timer = true;
       ajaxCallToIndex(sentence, API_SERVER_URL);
    //}
    $("#submit-img").attr('src',STATIC_IMG_PATH+'/send1.png');
});

$(document).on('click','.chipgoogleresult', function(){
    // /$(this).css('background-color', '#'+BOT_THEME_COLOR);
    //$(this).css('color', 'white');
    var url_link = $(this).attr("value");
    var win = window.open(url_link, '_blank');
    win.focus();
    //console.log(url_link);
});

var is_livechat = false;

function autocomplete(inp, arr) {
  /*the autocomplete function takes two arguments,
  the text field element and an array of possible autocompleted values:*/
  var currentFocus;
  /*execute a function when someone writes in the text field:*/
  inp.addEventListener("input", function(e) {
      var a, b, i, val = this.value;
      /*close any already open lists of autocompleted values*/
      closeAllLists();
      if (!val) { return false;}
      currentFocus = -1;
      /*create a DIV element that will contain the items (values):*/
      a = document.createElement("DIV");
      a.setAttribute("id", this.id + "autocomplete-list");
      a.setAttribute("class", "autocomplete-items");
      /*append the DIV element as a child of the autocomplete container:*/
      this.parentNode.appendChild(a);
      /*for each item in the array...*/

      var max_element_to_show = 0;
      arr_value_list = [];
      for (i = 0; i < arr.length; i++) {

        arr_key = arr[i]["key"];
        arr_value = arr[i]["value"];

        if(max_element_to_show>max_suggestions){
            break;
        }

        if(is_flow_ended && is_livechat==false){
          /*check if the item starts with the same letters as the text field value:*/
          if (arr_key.toUpperCase().indexOf(val.toUpperCase())!=-1 && arr_value_list.indexOf(arr_value)<0){
            /*create a DIV element for each matching element:*/
            b = document.createElement("DIV");
            arr_value_list.push(arr_value);
            /*make the matching letters bold:*/
            b.innerHTML = "<strong>" + arr_value + "</strong>";
            // b.innerHTML += arr[i].substr(val.length);
            /*insert a input field that will hold the current array item's value:*/
            b.innerHTML += "<input type='hidden' value='" + arr_value + "'>";
            /*execute a function when someone clicks on the item value (DIV element):*/
                b.addEventListener("click", function(e) {
                /*insert the value for the autocomplete text field:*/
                inp.value = this.getElementsByTagName("input")[0].value;
                /*close the list of autocompleted values,
                (or any other open lists of autocompleted values:*/
                closeAllLists();
                $('#submit-img').click();
            });
            a.appendChild(b);
            max_element_to_show+=1;
          }
        }
      }

      /*Empty suggestion list check*/
      if(max_element_to_show==0){
        query_token_list = val.split(" ");
        if(query_token_list.length==0){
            return;
        }

        val = query_token_list[query_token_list.length-1];
        arr_value_list = [];

        for (i = 0; i < arr.length; i++){
          arr_key = arr[i]["key"];
          arr_value = arr[i]["value"];
          if(max_element_to_show>max_suggestions){
              break;
          }
          if(is_flow_ended && is_livechat==false){
            /*check if the item starts with the same letters as the text field value:*/
            if(arr_key.toUpperCase().indexOf(val.toUpperCase())!=-1 && arr_value_list.indexOf(arr_value)<0){
              /*create a DIV element for each matching element:*/
              b = document.createElement("DIV");
              arr_value_list.push(arr_value);
              /*make the matching letters bold:*/
              b.innerHTML = "<strong>" + arr_value + "</strong>";
              // b.innerHTML += arr_value.substr(val.length);
              /*insert a input field that will hold the current array item's value:*/
              b.innerHTML += "<input type='hidden' value='" + arr_value + "'>";
              /*execute a function when someone clicks on the item value (DIV element):*/
              b.addEventListener("click", function(e){
                /*insert the value for the autocomplete text field:*/
                inp.value = this.getElementsByTagName("input")[0].value;
                /*close the list of autocompleted values,
                (or any other open lists of autocompleted values:*/
                closeAllLists();
                $('#submit-img').click();
              });
              a.appendChild(b);
              max_element_to_show+=1;
            }
          }
        }
      }

  });
  /*execute a function presses a key on the keyboard:*/
  inp.addEventListener("keydown", function(e) {
      var x = document.getElementById(this.id + "autocomplete-list");
      if (x) x = x.getElementsByTagName("div");
      if (e.keyCode == 40) {
        /*If the arrow DOWN key is pressed,
        increase the currentFocus variable:*/
        currentFocus++;
        /*and and make the current item more visible:*/
        addActive(x);
      } else if (e.keyCode == 38) { //up
        /*If the arrow UP key is pressed,
        decrease the currentFocus variable:*/
        currentFocus--;
        /*and and make the current item more visible:*/
        addActive(x);
      } else if (e.keyCode == 13) {
        /*If the ENTER key is pressed, prevent the form from being submitted,*/
        e.preventDefault();
        if (currentFocus > -1) {
          /*and simulate a click on the "active" item:*/
          if (x) x[currentFocus].click();
        }
      }
  });

  function addActive(x) {
    /*a function to classify an item as "active":*/
    if (!x) return false;
    /*start by removing the "active" class on all items:*/
    removeActive(x);
    if (currentFocus >= x.length) currentFocus = 0;
    if (currentFocus < 0) currentFocus = (x.length - 1);
    /*add class "autocomplete-active":*/
    x[currentFocus].classList.add("autocomplete-active");
  }

  function removeActive(x) {
    /*a function to remove the "active" class from all autocomplete items:*/
    for (var i = 0; i < x.length; i++) {
      x[i].classList.remove("autocomplete-active");
    }
  }

  function closeAllLists(elmnt) {
      /*close all autocomplete lists in the document,
      except the one passed as an argument:*/
      var x = document.getElementsByClassName("autocomplete-items");
      for (var i = 0; i < x.length; i++) {
        if (elmnt != x[i] && elmnt != inp) {
        x[i].parentNode.removeChild(x[i]);
      }
    }
  }

  /*execute a function when someone clicks in the document:*/
  document.addEventListener("click", function (e) {
      closeAllLists(e.target);
  });
}


var suggestion_list = []
var max_suggestions = 6;

function get_suggestion_list(bot_id, bot_name)
{
    var json_string = JSON.stringify({
      bot_id: bot_id,
      bot_name: bot_name,
    });
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);
    response = $.ajax({
        url:'/chat/get-data/',
        type:'POST',
        async: false,
        data:{
            json_string: json_string
        },
        success: function(response){
            return response;
        },
        error: function(error){
            console.log("Report this error", error);
            return {"status":500};
        }
    }).responseJSON;

    if(response["status"]==200){
        max_suggestions = response["max_suggestions"];
        return response["sentence_list"];
    }
    else{
        return [];
    }
}

var final_transcript = '';
var recognizing = false;
var ignore_onend;

var isSafari = (!!navigator.userAgent.match(/Version\/[\d\.]+.*Safari/));

// window.onbeforeunload = function(e) {
//     // if(livechat==true)
//     // {
//     //   $.ajax({
//     //     url: "/chat/delete-livechat-session/",
//     //     type: "POST",
//     //     data: {
//     //       user_id:user_id,
//     //     },
//     //     success: function(response) {
//     //       //console.log("Success");
//     //     },
//     //     error: function(xhr, textstatus, errorthrown) {
//     //       console.log("Please report this error: "+errorthrown+xhr.status+xhr.responseText);
//     //     }


//     //   });
//     //   chatSocket.close();
//     //   livechat=false;
//     // }
//     if(user_id != "" || user_id != undefined){
//       if(last_action != "close_bot"){
//         // console.log("inside onbeforeunload");
//         save_time_spent()
//       }
//     }
// };

if(!isSafari){
    if (!('webkitSpeechRecognition' in window)) {
        console.log("webkitSpeechRecognition is not supported in current browser.");
        voice_to_text=false;
    } else {
        voice_to_text=true;
        start_button.style.display = 'inline-block';
        var SpeechRecognition = SpeechRecognition || webkitSpeechRecognition
        // window.SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
        var recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;

        recognition.onstart = function() {
            recognizing = true;
            $("#start_button").addClass("pulse");
        };

        recognition.onerror = function(event) {
            $("#start_button").removeClass("pulse");
            if (event.error == 'no-speech') {
                ignore_onend = true;
            }
            if (event.error == 'audio-capture') {
                ignore_onend = true;
            }
            if (event.error == 'not-allowed') {
                ignore_onend = true;
            }
        };

        recognition.onend = function() {
            $("#start_button").removeClass("pulse");
            recognizing = false;
            if (ignore_onend) {
                return;
            }
            if (!final_transcript) {
                return;
            }

        };

        recognition.onresult = function(event) {

        document.getElementById('query').value=event.results[0][0].transcript;
        if (event.results[0].isFinal){
            if(($.trim($('#query').val()) != '') && ($("#query").val()).length<300){
                var sentence = $("#query").val();
                sentence = $($.parseHTML(sentence)).text();
                if (sentence.length == 0) {      // error!
                  $("#query").val("");
                  return;
                }
                $("#query").val("");
                disableInput();
                appendResponseUser(sentence);
                ajaxCallToIndex(sentence, API_SERVER_URL);
            }
            $("#start_button").removeClass("pulse");
            recognition.stop();
          }
        };
    }

}else{
    voice_to_text=false;
    show_submit_query_button();
}

$(document).on("click","#start_img", function(e){
  if(recognizing){
    recognition.stop();
    return;
  }

  final_transcript = '';
  recognition.start();
});


$(document).on("keypress","#query", function(e){
    show_submit_query_button();
});

$(document).on("change","#query", function(e){
  if($("#query").val().length==0){
    if(isSafari){
        show_submit_query_button();
    }
    else{
        show_voice_button();
    }
  }else{
      show_submit_query_button();
  }
});

$(document).on("mouseleave","#query", function(e){
  if($( "#query" ).val().length==0){
    if(isSafari){
        show_submit_query_button();
    }
    else{
        show_voice_button();
    }
    $("#start_button").removeClass("pulse");
  }
});
var slideIndexCard = 0;

function plusSlides(n) {
  showSlides(slideIndex += n);
}

function plusSlidesCards(n) {
  showSlidesCards(slideIndexCard += n);
}


function currentSlide(n) {
  showSlides(slideIndex = n);
}

function currentSlideCards(n) {
  showSlidesCards(slideIndexCard = n);
}

$(document).ready(function(){
    $('.sidenav').sidenav();
  });


function showSlides(n) {
  var i;
  var slides = document.getElementsByClassName("easychat-slideshow-slides");
  var dots = document.getElementsByClassName("easychat-slideshow-dot");

  if (n > slides.length) {slideIndex = 1}    

  if (n < 1) {slideIndex = slides.length}

  for (i = 0; i < slides.length; i++) {
      slides[i].style.display = "none";  
  }

  for (i = 0; i < dots.length; i++) {
      dots[i].className = dots[i].className.replace(" active", "");
  }

  slides[slideIndex-1].style.display = "block";  
  dots[slideIndex-1].className += " active";
  scroll_to_bottom();
}

function showSlidesCards(n) {
  var i;
  var slides = document.getElementsByClassName("easychat-slideshow-slides-cards");
  var dots = document.getElementsByClassName("easychat-slideshow-dot-cards");

  if (n > slides.length) {slideIndexCard = 1}    

  if (n < 1) {slideIndexCard = slides.length}

  for (i = 0; i < slides.length; i++) {
      slides[i].style.display = "none";
  }

  for (i = 0; i < dots.length; i++) {
      dots[i].className = dots[i].className.replace(" active", "");
  }

  slides[slideIndexCard-1].style.display = "block";  
  dots[slideIndexCard-1].className += " active";
  //scroll_to_bottom();
}

var slideIndex = 1;

function remove_image_slider_if_exist(){
    slider_main_container = document.getElementById("easychat-slideshow-container-main-div");
    if(slider_main_container!=undefined && slider_main_container!=null){
      slider_main_container.remove();
    } 
}

function remove_card_slider_if_exist(){
    slider_main_container = document.getElementById("easychat-slideshow-container-main-div-card");
    if(slider_main_container!=undefined && slider_main_container!=null){
      slider_main_container.remove();
    } 
}

function append_bot_slider_images(image_url_list){

  remove_image_slider_if_exist();

  image_slidershow_html = '<div style="width:100%; margin-top:0.2em; display:inline-block;" id="easychat-slideshow-container-main-div">\
      <div class="easychat-slideshow-container">';

  total_images = image_url_list.length;

  for(var i=0;i<image_url_list.length;i++){
    current_image_no = i+1;
    image_slidershow_html += '<div class="easychat-slideshow-slides fade">\
            <div class="easychat-slideshow-numbertext">'+current_image_no+' / '+total_images+'</div>\
            <img src="'+image_url_list[i]+'" class="easychat-slideshow-images" onclick="show_image_slider_into_parent_window()">\
          </div>';      
  }

          image_slidershow_html += '<a class="easychat-slideshow-prev" onclick="plusSlides(-1)" style="background-color:#'+BOT_THEME_COLOR+';">&#10094;</a>\
          <a class="easychat-slideshow-next" onclick="plusSlides(1)" style="background-color:#'+BOT_THEME_COLOR+';">&#10095;</a>\
        </div><br><div style="text-align:center">';

    for(var i=0;i<image_url_list.length;i++){
      current_image_no=i+1;
      image_slidershow_html += '<span class="easychat-slideshow-dot" onclick="currentSlide('+current_image_no+')"></span>';
    }
        
    image_slidershow_html += '</div></div>';

  document.getElementById("style-2").innerHTML+=image_slidershow_html;

  slideIndex = 1;
  showSlides(slideIndex);
  scroll_to_bottom();
  autocomplete(document.getElementById("query"), suggestion_list);
}


function show_image_slider_into_parent_window(){

  easychat_slider_images = document.getElementsByClassName("easychat-slideshow-images");
  image_url_list = [];
  for(var i=0;i<easychat_slider_images.length;i++){
      image_url_list.push(easychat_slider_images[i].src);
  }

  parent.postMessage({
      event_id: 'show-image-slider-into-parent',
      data: {
         image_url_list:image_url_list
      }
  }, PARENT_DOMAIN_URL);
}


function accepted_terms_conditions(element){
  setCookie("accepted_terms_conditions","1");
}

////////// Live Chat ///////////////

// var liveChatSocket=null;

// function append_livechat_response(){

//     livechat = true;
    
//     var roomName = user_id;

//     chatSocket = new WebSocket(
//         'ws://' + window.location.host +
//         '/ws/chat/room/' + roomName + '/');

//     chatSocket.onmessage = function(e) {

//         var data = JSON.parse(e.data);
        
//         var sender = data['sender'];
//         var message = data['message'];

//         $.ajax({

//           url:'/chat/update-livechat-message-history/',
//           type:'POST',
//           data:{
//               "user_id" : user_id,
//               "sender":sender,
//               "message":message,
//           },
//           success: function(response){
              
//           },
//           error: function(error){
//               console.log("append_livechat_response", error);
//               return {"status":500};
//           }

//         });
//         if(sender=="agent")
//           appendResponseServer(message,"","","","");
        
//         scroll_to_bottom();
//     };

//     chatSocket.onclose = function(e) {
//         $.ajax({
//           url: "/chat/delete-livechat-session/",
//           type: "POST",
//           data: {
//             user_id:user_id,
//           },
//           success: function(response) {
//             //console.log("Success");
//           },
//           error: function(xhr, textstatus, errorthrown) {
//               console.log("Please report this error: "+errorthrown+xhr.status+xhr.responseText);
//           }
//         });
//         chatSocket.close();
//         livechat=false;
//         console.error('Chat socket closed unexpectedly');
//     };
    
//     $.ajax({
//         url: '/assign-customer-care-agent/',
//         type: "POST",
//         data: {
//             user_id : user_id
//         },
//         success: function(response){
//           if(response['status']==200){
//             appendResponseServer("Dear User,<br> Mr. "+ response['customer_care_agent'] +" from our Customer Service Team has been assigned to you.\nHe will help you out with all your queries.", false, "", "","");
//             scroll_to_bottom();
//           }
//           else
//           {
//             appendResponseServer(BOT_DISPLAY_NAME+" bot is under maintenance, Please try again after some time. Sorry for your inconvenience.", false, "", "","");
//            scroll_to_bottom();
//           }
//         },
//         error: function (jqXHR, exception) {
//            appendResponseServer(BOT_DISPLAY_NAME+" bot is under maintenance, Please try again after some time. Sorry for your inconvenience.", false, "", "","");
//            scroll_to_bottom();
//         }, 
//     });
// }

function formAssistIntent() {

    url_params = get_url_vars();
    form_assist_intent_name = url_params["form_assist_intent_name"];
    ajaxCallToIndex(form_assist_intent_name, API_SERVER_URL);
    form_assist_intent_name = "";
}

function triggerIntent() {
    page_category = decodeURI(page_category);
    ajaxCallToIndex(page_category, API_SERVER_URL);
    page_category = "";
}

document.addEventListener("visibilitychange", function(){
  if(document.hidden){
     cancelTextToSpeech();
     // restart_chatbot();
  }
}, false);

// window.onbeforeunload = function(){
//     cancelTextToSpeech();
//     restart_chatbot();
// }


function get_url_vars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m, key, value) {
        vars[key] = value;
    });
    return vars;
}

function create_issue(element){
  name = document.getElementById("new-issue-name").value;
    if(name == ""){
      showToast("Please enter your name.");
      return;
    }
    if(!/^[a-zA-Z ]*$/.test(name)){
      showToast("Please enter a valid name.");
      return;
    }
    phone_no = document.getElementById("new-issue-phone").value;
    if(phone_no == "" || phone_no.length!=10){
      showToast("Please enter your 10 digits mobile number.");
      return;
    }
    if(phone_no.length != 10 || !/^\d{10}$/.test(phone_no)){
      showToast("Please enter a valid phone no.");
      return;
    }
    issue = document.getElementById("new-issue-issue").value;
    if(issue == ""){
      showToast("Please describe your issue.");
      return;
    }
    priority = document.getElementById("ticket-priority").value;
    if(priority == ""){
      showToast("Please select the priority.");
      return;
    }
    category = document.getElementById("ticket-category").value;
    if(category == ""){
      showToast("Please select the category.");
      return;
    }

    bot_id = get_url_vars()["id"]
    json_string = JSON.stringify({
        name:name,
        phone_no:phone_no,
        email:"",
        issue:issue,
        priority:priority,
        category:category,
        bot_id:bot_id
    });
    json_string = EncryptVariable(json_string);
    
    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
       url: '/tms/create-issue/',
       type: 'POST',
       headers: {
           'X-CSRFToken': CSRF_TOKEN
       },
       data: {
           data: json_string
       },
       success: function(response) {
           if (response["status_code"] == 200 && response["ticket_id"] != "") {
               $('#modal-create-issue').modal('close');
               message_response = "Thank you for submitting your issue. Your Ticket ID is " +response["ticket_id"]+" .Our agent will contact you soon."
               appendResponseServer(message_response,false, "", "", "");
           }
           else{
               showToast("Unable to submit your issue due to some internal server error. Kindly report the same", 2000);
               console.log("Please report this. ", response["status_message"]);            
           }
       },
       error: function(xhr, textstatus, errorthrown){
           console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
       }
   });
}

function schedule_meeting(element){
  console.log("Entering details...")
  name = document.getElementById("new-meeting-name").value;
    if(name == ""){
      showToast("Please enter your name.");
      return;
    }
    if(!/^[a-zA-Z ]*$/.test(name)){
      showToast("Please enter a valid name.");
      return;
    }

    phone_no = document.getElementById("new-meeting-phone").value;
    if(phone_no == "" || phone_no.length!=10){
      showToast("Please enter your 10 digits mobile number.");
      return;
    }
    if(phone_no.length != 10 || !/^\d{10}$/.test(phone_no)){
      showToast("Please enter a valid phone no.");
      return;
    }
    meet_date = document.getElementById("new-meeting-date").value;
    if(meet_date == ""){
      showToast("Please enter meeting date.")
      return;
    }
    meet_date_year = meet_date.split("-")[0]
    meet_date_month = meet_date.split("-")[1]
    meet_date_date = meet_date.split("-")[2]
    if(meet_date_year < new Date().getFullYear()){
      showToast("Please enter a valid year.")
      return;
    }
    else if(meet_date_year == new Date().getFullYear() && meet_date_month < (new Date().getMonth() + 1)){
      showToast("Please enter a valid month.")
      return;
    }
    else if(meet_date_year == new Date().getFullYear() && meet_date_month == (new Date().getMonth() + 1) && meet_date_date < new Date().getDate()){
      showToast("Please enter a valid date.")
      return;
    }

    meet_time = document.getElementById("new-meeting-time").value;
    if(meet_time == ""){
      showToast("Please enter meeting time.")
      return;
    }
    if(meet_date_year == new Date().getFullYear() && meet_date_month == (new Date().getMonth() + 1) && meet_date_date == new Date().getDate()){
      meet_time_hour = meet_time.split(":")[0]
      meet_time_hour = parseInt(meet_time_hour)

      meet_time_minute = meet_time.split(":")[1]
      meet_time_minute = parseInt(meet_time_minute)

      current_hour = new Date().getHours()
      current_minute = new Date().getMinutes()
        if(meet_time_hour < current_hour){
          showToast("Please enter valid time.")
          return;
        }
        else if(meet_time_hour == current_hour && meet_time_minute < current_minute){
            showToast("Please enter valid time.");
            return;
        }
    }

    meet_agent_date_time = meet_date + "T" + meet_time

    user_pincode = document.getElementById("new-meeting-pincode").value;

    issue = document.getElementById("new-meeting-issue").value;
    if(issue == ""){
      showToast("Please describe your issue.");
      return;
    }
    json_string = JSON.stringify({
        name:name,
        phone_no:phone_no,
        email:"",
        issue:issue,
        meet_agent_date_time:meet_agent_date_time,
        user_pincode:user_pincode
    });
    json_string = EncryptVariable(json_string);

    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
       url: '/tms/schedule-meeting/',
       type: 'POST',
       headers: {
           'X-CSRFToken': CSRF_TOKEN
       },
       data: {
           data: json_string
       },
       success: function(response) {
           if (response["status_code"] == 200) {
               $('#modal-schedule-meeting').modal('close');
               message_response = "Thank you for scheduling the meeting. Your Meeting ID is " +response["meeting_id"]+" .Our agent will contact you soon."
               appendResponseServer(message_response,false, "", "", "");
           }
           else{
               showToast("Unable to schedule meeting due to some internal server error. Kindly report the same", 2000);
               console.log("Please report this. ", response["status_message"]);            
           }
       },
       error: function(xhr, textstatus, errorthrown){
           console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
       }
   });
}

function close_issue(element){
  appendResponseServer("You have not scheduled the meeting. Tell me, How may I assist you?",false, "", "", "");
}


$(document).ready(function(){
    $(':input').on('focus',function(){
        $(this).attr('autocomplete', 'off');
    });
});


function check_ticket_status(element){
  ticket_id = document.getElementById("check-ticket-id").value;
    if(ticket_id == ""){
      showToast("Please enter your ticket id.");
      return;
    }
    json_string = JSON.stringify({
        ticket_id:ticket_id,
    });
    json_string = EncryptVariable(json_string);

    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
       url: '/tms/check-ticket-status/',
       type: 'POST',
       headers: {
           'X-CSRFToken': CSRF_TOKEN
       },
       data: {
           data: json_string
       },
       success: function(response) {
           if (response["status_code"] == 200 && response["ticket_exist"] == true) {
               $('#modal-check-ticket-status').modal('close');
               ticket_status_message = ""
               ticket_status_message = response["ticket_status_message_response"]
               appendResponseServer(ticket_status_message,false, "", "", "");
           }
           else if(response["ticket_exist"] == false){
            $('#modal-check-ticket-status').modal('close');
            appendResponseServer("Sorry, no such ticket found. Please check your Ticket ID and try again.",false, "", "", "");
           }
           else{
               showToast("Unable to submit your issue due to some internal server error. Kindly report the same", 2000);
               console.log("Please report this. ", response["status_message"]);            
           }
       },
       error: function(xhr, textstatus, errorthrown){
           console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
       }
   });
}

function check_meeting_status(element){
  meeting_id = document.getElementById("check-meeting-id").value;
    if(meeting_id == ""){
      showToast("Please enter your meeting id.");
      return;
    }
    json_string = JSON.stringify({
        meeting_id:meeting_id,
    });
    json_string = EncryptVariable(json_string);

    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
       url: '/tms/check-meeting-status/',
       type: 'POST',
       headers: {
           'X-CSRFToken': CSRF_TOKEN
       },
       data: {
           data: json_string
       },
       success: function(response) {
           if (response["status_code"] == 200 && response["meeting_exist"] == true) {
               $('#modal-check-meeting-status').modal('close');
               meeting_status_message = ""
               meeting_status_message = response["meeting_status_message_response"]
               appendResponseServer(meeting_status_message,false, "", "", "");
           }
           else if(response["meeting_exist"] == false){
            $('#modal-check-meeting-status').modal('close');
            appendResponseServer("Sorry, no such meeting found. Please check your Meeting ID and try again.",false, "", "", "");
           }
           else{
            $('#modal-check-meeting-status').modal('close');
               showToast("Unable to submit your issue due to some internal server error. Kindly report the same", 2000);
               console.log("Please report this. ", response["status_message"]);            
           }
       },
       error: function(xhr, textstatus, errorthrown){
           console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
       }
   });
}



var liveChatSocket = null;
var agent_assigned = false;
var need_to_add_wel_msg = true;
var room_name = null;
var chat_socket1 = null;
var check_agent_assign_timer = null;

function append_livechat_response(){
    livechat = true;
    room_name = user_id;

    create_socket1(room_name);

    var CSRF = $('input[name="csrfmiddlewaretoken"]').val();
    var json_string = JSON.stringify({
      room_name: room_name,
      bot_id: "1",
      session_id: user_id,
      user_id: user_id,
      username: room_name,
      phone: "9012345678",
      email: "test@123456.com",
    });
    json_string = EncryptVariable(json_string);

    $.ajax({
       url: '/livechat/create-customer/',
       type: 'POST',
       headers:{
          'X-CSRFToken':CSRF
        },
       data: {
        json_string: json_string
       },
       success: function(response) {
           if (response["status_code"] == 200){
               // window.location.reload();
               // window.location.pathname = '/livechat/' + response["room_name"] + '/';
               check_agent_assign_timer = setInterval(assign_agent, 5000);
           }
           else{
                M.toast({
                    "html": "Unable to delete due to some internal server error. Kindly report the same"
                }, 2000);
               console.log("Please report this. ", response["status_message"]);            
           }
       },
       error: function(xhr, textstatus, errorthrown){
           console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
       }
     });

     //check_agent_assign_timer = setInterval(assign_agent, 5000);
}


function assign_agent(){
      var json_string = JSON.stringify({
        room_name: room_name,
      });
      json_string = EncryptVariable(json_string);
      json_string = encodeURIComponent(json_string);
      var xhttp = new XMLHttpRequest();
      var params = 'json_string='+json_string;
      xhttp.open("POST", '/livechat/assign-agent/', true);
        xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhttp.onreadystatechange = function() {
          if (this.readyState == 4 && this.status == 200) {
              console.log("Agent Assigned!!!");
              agent_assigned = true;
              // console.log(typeof(this.response))
              response = this.response
              response = JSON.parse(response)
              assigned_agent = response["assigned_agent"]
              if(assigned_agent == "None"){
                agent_assigned = false;
                need_to_add_wel_msg = true;
              }else if(assigned_agent == "not_available"){
                var message = "Agent is unable to reach you.<br>Please wait, we are working on it."
                // appendResponseServer(message);
                appendResponseServer(message, false, "", "", "");

                // append_bot_text_response(message, false);
               // save_customer_chat("Agent is unable to reach you. Please wait, we are working on it.", room_name, 'agent');
                need_to_add_wel_msg = true;
                scroll_to_bottom();
              }else if (assigned_agent == "session_end"){
                 is_livechat = false;
                 chat_socket1.close();
                 clearTimeout(check_agent_assign_timer);
                 need_to_add_wel_msg = true;
                 scroll_to_bottom();
              }else{
                if(need_to_add_wel_msg){
                  var message = "Congratulations!!!\n<br><b>"+assigned_agent+"</b> has joind your room. You can ask your queries.<br>"
                  // appendResponseServer(message);
                  appendResponseServer(message, false, "", "", "");
                  message = "Congratulations!!! "+assigned_agent+" has joind your room. You can ask your queries."
                 // save_customer_chat(message,room_name,'agent');
                  need_to_add_wel_msg = false;
                  scroll_to_bottom();
                }
              }

              //scroll_to_bottom();
          }
        }
        xhttp.send(params);
    }

function create_socket1(room_name){

      chat_socket1 = new WebSocket(
          'ws://' + window.location.host +
          '/ws/' + room_name + '/customer/');

      chat_socket1.onmessage = function(e) {
          var data = JSON.parse(e.data);
          var message = data['message'];
          var sender = data['sender'];
          // console.log(e.data);
          if(sender=="agent_end_session"){

          append_feedback_form();
          scroll_to_bottom();
        }else if(sender=="agent"){
              appendResponseServer(message, false, "", "", "");
              scroll_to_bottom();
          }
      }

      chat_socket1.onclose = function(e) {
          console.log('Chat socket closed unexpectedly');
      };

      chat_socket1.onopen = function(e){
          console.log("Connection established.")
      }
}

function append_feedback_form(){

  // append_bot_text_response("Agent has left the session. LiveChat session ended.", false);
  appendResponseServer("Agent has left the session. LiveChat session ended.", false, "", "", "");
  disableInput()

  user_input = "It was great helping you. Your feedback help us to improvise our service quality.\nPlease rate your agent.";
  var time = return_time();
  
  var html = `<div class="rating-bar-container__wrapper" style="width: 92%;margin: auto;margin-top: 1em;">
            <div id="rating-bar-container__XqPZ" class="rating-bar-container" zQPK="false" onmouseout="change_color_ratingz_bar_all(this)">
              <button id="rating-bar-button__01" onmouseover="changeColorRatingvBar(this)" onmouseout="change_color_ratingz_bar(this)" onclick="set_value_to_some(this)" value="1">1</button><button id="rating-bar-button__02" onclick="set_value_to_some(this)" onmouseover="changeColorRatingvBar(this)" onmouseout="change_color_ratingz_bar(this)" value="2">2</button><button id="rating-bar-button__03" onmouseover="changeColorRatingvBar(this)" onclick="set_value_to_some(this)" onmouseout="change_color_ratingz_bar(this)" value="3">3</button><button id="rating-bar-button__04" onclick="set_value_to_some(this)" onmouseover="changeColorRatingvBar(this)" onmouseout="change_color_ratingz_bar(this)" value="4">4</button><button id="rating-bar-button__05" onmouseover="changeColorRatingvBar(this)" onclick="set_value_to_some(this)" onmouseout="change_color_ratingz_bar(this)" value="5">5</button><button id="rating-bar-button__06" onclick="set_value_to_some(this)" onmouseover="changeColorRatingvBar(this)" onmouseout="change_color_ratingz_bar(this)" value="6">6</button><button id="rating-bar-button__07" onmouseover="changeColorRatingvBar(this)" onclick="set_value_to_some(this)" onmouseout="change_color_ratingz_bar(this)" value="7">7</button><button id="rating-bar-button__08" onclick="set_value_to_some(this)" onmouseover="changeColorRatingvBar(this)" onmouseout="change_color_ratingz_bar(this)" value="8">8</button><button id="rating-bar-button__09" onmouseover="changeColorRatingvBar(this)" onclick="set_value_to_some(this)" onmouseout="change_color_ratingz_bar(this)" value="9">9</button><button id="rating-bar-button__10" onclick="set_value_to_some(this)" onmouseover="changeColorRatingvBar(this)" onmouseout="change_color_ratingz_bar(this)" value="10">10</button>
            </div><br><div style="width:30%;margin:auto;"><span id="rating-bar-container-timer__XqPZ"></span></div></div>`
    document.getElementById("style-2").innerHTML += '<div id="livechat_feedback" style="display:inline-block;"><div style="box-shadow: 1px 1px 6px rgba(0, 0, 0, 0.2);color: black;width: 80%;margin: auto;margin-top: 1.5em;border-radius: 1em;padding: 1em;background-color:white;">'+user_input+html+'</div></div>';
  scroll_to_bottom();
  feedBack_timer_fun();
  
  // document.getElementById("easychat-chat-container").innerHTML += html;

}


function feedBack_timer_fun(){
    var timer_value = 60
    ratingTimer = setInterval(function(){
      if(timer_value < 10){
          document.getElementById("rating-bar-container-timer__XqPZ").textContent = "00:0"+timer_value;
        }else{
          document.getElementById("rating-bar-container-timer__XqPZ").textContent = "00:"+timer_value;
        }
        if(timer_value <= 10){
            // document.getElementById("rating-bar-container-timer__XqPZ").style.border = "solid red";
            document.getElementById("rating-bar-container-timer__XqPZ").style.color = "red";
        }
        if(timer_value > 10 && timer_value <= 30){
            // document.getElementById("rating-bar-container-timer__XqPZ").style.border = "solid orange";
            document.getElementById("rating-bar-container-timer__XqPZ").style.color = "orange";
        }
        if(timer_value > 30){
            // document.getElementById("rating-bar-container-timer__XqPZ").style.border = "solid green";
            document.getElementById("rating-bar-container-timer__XqPZ").style.color = "green";
           }
        timer_value = timer_value - 1;
        if(timer_value == -1){
               document.getElementById("livechat_feedback").remove()
               // append_bot_text_response("Hi, I am your personal virtual assistant. How may I assist you further?", false);
               appendResponseServer("Hi, I am your personal virtual assistant. How may I assist you further?", false, "", "", "");
               clearInterval(ratingTimer);
               scroll_to_bottom();
               enableInput();
           }
        },1000);
    
}

function set_value_to_some(el){
    el.parentElement.setAttribute("zQPK","true")
    var rate_value = el.getAttribute("value")
    clearInterval(ratingTimer);
    save_livechat_feedback(rate_value, room_name);
    // el.parentElement.parentElement.remove()
    document.getElementById("livechat_feedback").remove()
    appendResponseServer("Thank you for connecting us. Hoping to help you in future.", false,"","","");
    appendResponseServer("Hi, I am your personal virtual assistant. How may I assist you further?", false,"","","");
    scroll_to_bottom();
    enableInput()
}
function change_color_ratingz_bar_all(el){
    current_hover_value = parseInt(el.childElementCount);
    if(el.getAttribute("zQPK") == "false"){
        for(var i=0; i<=current_hover_value ;i++){
            if (el.children[i] != undefined) {
                el.children[i].style.color ="black"
                el.children[i].style.backgroundColor ="white"    
                }
        }   
    }
}

function change_color_ratingz_bar(el){
    current_hover_value = parseInt(el.getAttribute("value"));
    for(var i=current_hover_value; i<=current_hover_value ;i++){
        if (el.parentElement.children[i] != undefined) {
            el.parentElement.children[i].style.color ="black"
            el.parentElement.children[i].style.backgroundColor ="white"
        }
    }
}

function changeColorRatingvBar(el){
    current_hover_value = parseInt(el.getAttribute("value"));
        for(var i=0; i<current_hover_value ;i++){
            if (current_hover_value <= 6){
                el.parentElement.children[i].style.color ="white"
                el.parentElement.children[i].style.backgroundColor ="red"
            }
            if (6 < current_hover_value && current_hover_value <= 8){
                el.parentElement.children[i].style.color ="white"
                el.parentElement.children[i].style.backgroundColor ="orange"
            }
            if (8 < current_hover_value){
                el.parentElement.children[i].style.color ="white"
                el.parentElement.children[i].style.backgroundColor ="green"
                }
            }
        for(var j=current_hover_value; j<=el.parentElement.childElementCount ;j++){
            if (el.parentElement.children[j] != undefined) {
                el.parentElement.children[j].style.color ="black"
                el.parentElement.children[j].style.backgroundColor ="white"
            }
        }
}


function save_livechat_feedback(rate_value, room_name){
  var json_string = JSON.stringify({
    room_name: room_name,
    rate_value: rate_value
  });
  
  json_string = EncryptVariable(json_string);
  json_string = encodeURIComponent(json_string);

  var xhttp = new XMLHttpRequest();
  var params = 'json_string='+json_string
  xhttp.open("POST", '/livechat/save-livechat-feedback/', true);
  xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
  xhttp.onreadystatechange = function() {
    if(this.readyState == 4 && this.status == 200){
      console.log("Rating updated successfully!!!")
    }
  }
  xhttp.send(params);
}

/*
function send_message_to_server(){
      console.log("IMNOTIN")
      if(($.trim($('#query').val()) != '') && ($("#query").val()).length<3000){
        var sentence = $("#query").val();
        sentence = $($.parseHTML(sentence)).text();
        if (sentence.length == 0) {      // error!
          $("#query").val("");
          return;
        }
        $("#query").val("");
        appendResponseUser(sentence, "", "", "", "");
        save_customer_chat(sentence, room_name);
        var sentence = JSON.stringify({
             'message':sentence,
            'sender':'user'
         });
        chat_socket1.send(sentence);
      } 
}
*/


function save_customer_chat(sentence, room_name, sender="customer"){
  var json_string = JSON.stringify({
    message: sentence,
    room_name: room_name,
    sender: sender
  });
  json_string = EncryptVariable(json_string);
  var CSRF = $('input[name="csrfmiddlewaretoken"]').val();
  $.ajax({
      url: '/livechat/save-customer-chat/',
      type: "POST",
      headers:{
        'X-CSRFToken':CSRF
      },
      async: false,
      data:{
          json_string: json_string
      },
      success: function(response){
          if(response["status"]==200){
          }else{
            console.log("chat send by agent saved");
          }
      }
  });
}

// var mark_offline_var = false;
window.onbeforeunload = function(e) {
  cancelTextToSpeech();
  restart_chatbot();
  if(user_id != "" || user_id != undefined){
      if(last_action != "close_bot"){
        save_time_spent()
      }
    }
  try{
      chat_socket1.close();
    }
    catch{
      
    }
}
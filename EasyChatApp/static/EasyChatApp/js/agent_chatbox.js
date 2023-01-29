var BOT_THEME_COLOR = '6a1b9a';
var MESSAGE_IMG = "/static/EasyChatApp/img/favicon.png";
STATIC_IMG_PATH = "/static/EasyChatApp/img";
STATIC_MP3_PATH = "/static/EasyChatApp/mp3";
var timer_var = '';

$(document).on("click","#scrollBot-img", function(e){
    $("#style-2").stop().animate({ scrollTop: $("#style-2")[0].scrollHeight}, 500);
});


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

var scroll_to_bottom = function() {
  $('#style-2').scrollTop($('#style-2')[0].scrollHeight);
  
};

function append_response_user(sentence){

    sentence = sentence.replace("<p>","");sentence = sentence.replace("</p>","");
    sentence = sentence.replace("<","#");sentence = sentence.replace(">","#");

    var html =
    '<script>\
     $(document).ready(function(){\
      $('.tooltipped').tooltip();\
    });\
    </script>\
    <div class="row chatmessage">\
        <div class="col s3">\
        </div>\
        <div class="col s9">\
            <div class="chip chip2 right chip-right" style="background-color: #'+BOT_THEME_COLOR+'">\
                <span style="color:white;">'+sentence+'</span>\
            </div>\
        </div>\
        <div class="timestampr" >'+return_time()+'</div>\
    </div>';
    $("#style-2").append(html);
    
    scroll_to_bottom();
    clearTimeout(timer_var)
}

function append_response_server(sentence, flag, url1, url2, tooltip_response){
    sentence = sentence.replace("<p>","");sentence = sentence.replace("</p>","");
    sentence = sentence.replace("<strong>","<b>");sentence = sentence.replace("</strong>","</b>");
    sentence = sentence.replace("<em>","<i>");sentence = sentence.replace("</em>","</i>");
    sentence = sentence.replace('background-color:#ffffff; color:#000000','');
    sentence = sentence.replace("background-color:#ffffff;","");
    var html = ""
    if(tooltip_response=="" || tooltip_response=="undefined"){
        html =
        '<div class="row chatmessage">\
            <div class="col s1 l1" >\
               <img src="'+MESSAGE_IMG+'" width=34 class="chatbot-left-image">\
            </div>\
            <div class="col s10 m10">\
               <div class="chip chip2 chip-left" >\
                  <span>'+sentence+'</span>\
               </div>\
            </div>\
            <div class="timestampl" >'+return_time()+'</div>\
        </div>';
    }else{
      html =
      '<script>\
       $(document).ready(function(){\
        $(".tooltipped").tooltip();\
      });\
      </script>\
      <div class="row chatmessage">\
          <div class="col s1 l1" >\
             <img src="'+MESSAGE_IMG+'" width=34 class="chatbot-left-image">\
          </div>\
          <div class="col s10 m10">\
             <div class="chip chip2 chip-left" >\
                <span>'+sentence+'</span>\
                <p align="right" style="margin: 0em;padding: 0em;"><i class="material-icons prefix blue-text tooltipped" data-position="bottom" data-tooltip="'+tooltip_response+'">info</i></p>\
             </div>\
          </div>\
          <div class="timestampl" >'+return_time()+'</div>\
      </div>';
    }

    $("#style-2").append(html);
}


function send_message_to_user(user_id){

  if(($.trim($('#query').val()) != '') && ($("#query").val()).length<300){
      
      var sentence = $("#query").val();
      sentence = $($.parseHTML(sentence)).text();

      if (sentence.length == 0) {     
        $("#query").val("");
        return;
      }
      $("#query").val("");
      append_response_user(sentence);
      
     var sentence = JSON.stringify({
           'message': JSON.stringify({"text_message": sentence, "type": "text", "channel": "Web", "path": ""}),
          'sender':"agent",
       });
       
     chat_socket.send(sentence);

     }  
}
var SERVER_URL = "";
var minimized_chatbot = false;

function addCSS(filename){
     var head = document.getElementsByTagName('head')[0];
     var style = document.createElement('link');
     style.href = filename;
     style.type = 'text/css';
     style.rel = 'stylesheet';
     head.append(style);
}

// Include script file
function addScript(filename){
    var head = document.getElementsByTagName('head')[0];
    var script = document.createElement('script');
    script.src = filename;
    script.type = 'text/javascript';
    head.append(script);
}

addCSS(SERVER_URL+"/static/EasyChatApp/css/embed.css");
addCSS(SERVER_URL+"/static/EasyChatApp/css/materialize.min.css");
addCSS(SERVER_URL+"/static/EasyChatApp/css/material_icons.css");
addScript(SERVER_URL+"/static/EasyChatApp/js/jquery.min.js");
addScript(SERVER_URL+"/static/EasyChatApp/js/materialize.min.js");

var slideIndex=1;

function get_url_vars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
        vars[key] = value;
    });
    return vars;
}

function plusSlides(n) {
  showSlides(slideIndex += n);
}

function currentSlide(n) {
  showSlides(slideIndex = n);
}

function remove_image_slider_if_exist(){
    slider_main_container = document.getElementById("modal-image-slider-container");
    if(slider_main_container!=undefined && slider_main_container!=null){
       slider_main_container.remove();
    } 
}

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
            <img src="'+image_url_list[i]+'" class="easychat-slideshow-images">\
          </div>';      
  }

    image_slidershow_html += '<a class="easychat-slideshow-prev" onclick="plusSlides(-1)">&#10094;</a>\
      <a class="easychat-slideshow-next" onclick="plusSlides(1)">&#10095;</a>\
    </div><br><div style="text-align:center">';

    for(var i=0;i<image_url_list.length;i++){
        current_image_no=i+1;
        image_slidershow_html += '<span class="easychat-slideshow-dot" onclick="currentSlide('+current_image_no+')"></span>';
    }
        
    image_slidershow_html += '</div></div>';

    main_slider_modal = '<div id="modal-image-slider-container" class="modal" style="hei">\
              <div class="modal-content">\
                <div class="row">'+image_slidershow_html+'</div></div></div>';

  $('body').append(main_slider_modal);

  $("#modal-image-slider-container").modal({
      full_width: true,
      height:600
  });

  $("#modal-image-slider-container").modal("open");

  slideIndex = 1;

  showSlides(slideIndex);
}

window.onload = function() {

    // $('body').append('<iframe id="allincall-chat-box" frameborder="0" style="display:none;" allow="microphone;"></iframe>');
    var iframe = document.createElement('iframe');
    iframe.style.display = "none";
    iframe.id = "allincall-chat-box";
    iframe.frameborder = "0";
    iframe.style.zIndex = "2147483647";
    document.body.appendChild(iframe);

    url_parameters = get_url_vars();
    bot_id = url_parameters["id"];
    bot_name = url_parameters["name"];
    bot_theme = url_parameters["theme"];
    var start_time = ""

    if(bot_id==undefined || bot_id==null){
        return null;
    }

    if(bot_name==undefined || bot_name==null){
        return null;
    }

    var xhttp = new XMLHttpRequest();
    var params = 'bot_id='+bot_id;
    xhttp.open("POST", "/chat/get-bot-image/", true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            var popup_image = document.createElement("img");
            popup_image.id = "allincall-popup";
            popup_image.style.position = "fixed";
            popup_image.style.cursor = "pointer";
            popup_image.style.right="20px";
            popup_image.style.bottom="0";
            popup_image.style.width="7em";
            popup_image.style.zIndex="2147483647";

            if(response.status==200 && response.bot_image_url!=""){
                popup_image.src=response.bot_image_url;
            }else{
                popup_image.src="/static/EasyChatApp/img/popup-3.svg";
            }

            document.body.appendChild(popup_image);

            var auto_pop_timer_handle=null;

            $(document).on("click", "#allincall-popup", function(e){

                if(auto_pop_timer_handle!=null){
                    clearTimeout(auto_pop_timer_handle);
                }

                $('#query').focus();
                var current_src = $("#allincall-chat-box").attr("src");
                if((typeof current_src === 'undefined') || (current_src == null)){
                }
                else{
                  $("#allincall-chat-box").slideDown("slow");
                }
                $('#allincall-popup').hide("slow");
                $("#allincall-chat-box").slideDown("slow");
                $('#query').focus();
                if(minimized_chatbot){
                  $("#allincall-chat-box").slideDown("slow");
                }else{
                  $("#allincall-chat-box").attr("src","/chat/index/?id="+bot_id+'&name='+bot_name+'&theme='+bot_theme);
                }
            });

            if(response.status==200 && response.is_auto_pop_allowed){
               auto_pop_timer_handle = setTimeout(function(e){
                    $("#allincall-popup").click();
               }, response.auto_pop_timer*1000);
            }

            $(document).ready(function(){
                $('.collapsible').collapsible();
            });

        }
    }
    xhttp.send(params);

    window.addEventListener('message', function(event) {

        if(event.data.event_id === 'show-image-slider-into-parent'){
            append_bot_slider_images(event.data.data.image_url_list);
        }

        if(event.data=="minimize-chatbot"){
            $('#allincall-chat-box', window.document).hide("slow");
            $('#allincall-popup', window.document).show("slow");
            minimized_chatbot = true;
        }
        if(event.data=="close-bot"){
            $('#allincall-chat-box', window.document).hide("slow");
            $('#allincall-popup', window.document).show("slow");
        }
    });
}

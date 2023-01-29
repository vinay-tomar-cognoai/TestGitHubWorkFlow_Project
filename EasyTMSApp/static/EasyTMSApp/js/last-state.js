var framesContainer = document.querySelector('#frames-container');
var currentFrameIdx = 0;
var playbackIntervalId = null;
var cobrowseSocket = null;
var is_page_reloaded = false;
var sync_client_web_screen_timer = null;

function sync_client_web_screen(){

    json_string = JSON.stringify({
         "id": COBROWSE_SESSION_ID
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/sync/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_easyassist_cookie("csrftoken"));
    xhttp.onreadystatechange = function(){
        if(this.readyState==4 && this.status==200){
          response = JSON.parse(this.responseText);
          response = easyassist_custom_decrypt(response.Response);
          response = JSON.parse(response);

          var blob = new Blob([response.html], {type: 'text/html'});
          var iframe = document.createElement('iframe');
          iframe.src = window.URL.createObjectURL(blob);
          iframe.hidden = true;
          iframe.onload = renderFrame; 
          iframe.setAttribute("class", "client-data-frame");
          framesContainer.appendChild(iframe);
          document.getElementById("preloader").style.display="none";
          is_page_reloaded = false;
        }
    }
    xhttp.send(params);
}

function highlightElement(event, frame_window){

    json_string = JSON.stringify({
        "id": COBROWSE_SESSION_ID,
        "position": {
            "clientX": event.clientX,
            "clientY": event.clientY,
            "agent_window_width": frame_window.outerWidth,
            "agent_window_height": frame_window.outerHeight,
            "screen_width": screen.width,
            "screen_height": screen.height,
            "agent_window_x_offset": frame_window.pageXOffset,
            "agent_window_y_offset": frame_window.pageYOffset,
            "pageX": event.pageX,
            "pageY": event.pageY
         }
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    json_string = encodeURIComponent(json_string);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/highlight/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_easyassist_cookie("csrftoken"));
    xhttp.onreadystatechange = function(){
        if(this.readyState==4 && this.status==200){
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
        }
    }
    xhttp.send(params);
}

function renderFrame(event) {
    setTimeout(function(){
        event.preventDefault();
        if (framesContainer.children.length) {

            var frame = framesContainer.children[currentFrameIdx];
            if(!frame) {return;}
            if (currentFrameIdx > 0) {
                var prevFrame = frame.previousElementSibling;
                prevFrame.hidden = true;
                window.URL.revokeObjectURL(prevFrame.src);
                prevFrame.parentNode.removeChild(prevFrame);
                currentFrameIdx = currentFrameIdx - 1;
            }

            frame.hidden = false;
            scrollX = parseInt(frame.contentDocument.documentElement.dataset.scrollX);
            scrollY = parseInt(frame.contentDocument.documentElement.dataset.scrollY);
            frame.contentDocument.addEventListener('contextmenu', event => event.preventDefault());

            // frame.contentWindow.scrollTo({top:scrollY, left:scrollX, behavior: 'smooth'});
            frame.contentWindow.scrollTo(scrollX, scrollY);
            frame.contentWindow.document.onclick = function(event){
                highlightElement(event, frame.contentWindow);
            }


            var active_element_list = [];
            active_element_list = frame.contentWindow.document.querySelectorAll("input[easyassist-active=\"true\"]");
            for(var index=0; index<active_element_list.length; index++){
                if(active_element_list[index].getAttribute("type")=="checkbox"){
                    active_element_list[index].parentElement.style.outline="solid 2px #E83835 !important";
                }else if(active_element_list[index].getAttribute("type")=="radio"){
                    active_element_list[index].parentElement.style.outline="solid 2px #E83835 !important";
                }else{
                    active_element_list[index].parentElement.style.outline="solid 2px red";
                }
            }

            active_element_list = frame.contentWindow.document.querySelectorAll("select[easyassist-active=\"true\"]");
            for(var index=0; index<active_element_list.length; index++){ 
                active_element_list[index].parentElement.style.outline="solid 2px #E83835 !important";
            }

            active_element_list = frame.contentWindow.document.querySelectorAll("textarea[easyassist-active=\"true\"]");
            for(var index=0; index<active_element_list.length; index++){ 
                active_element_list[index].style.outline="solid 2px #E83835 !important";
            }

            div_element_list = frame.contentWindow.document.querySelectorAll("div");
            for(var index=0; index<div_element_list.length; index++){
                div_ele = div_element_list[index];
                scroll_left = div_ele.getAttribute("easyassist-data-scroll-x");
                scroll_top = div_ele.getAttribute("easyassist-data-scroll-y");
                div_ele.scrollLeft = scroll_left;
                div_ele.scrollTop = scroll_top;
            }

            currentFrameIdx++;
        }
        document.getElementById("preloader").style.display="none";

    }, 1000);
}

function playback(interval) {
  clearInterval(playbackIntervalId);

  if (!framesContainer.children.length) {
    return;
  }

  var i = 0;
  playbackIntervalId = setInterval(function() {
    var iframe = framesContainer.children[i];
    if (i > 0) {
      framesContainer.children[i - 1].hidden = true;
    } else if (i == 0) {
      framesContainer.children[framesContainer.children.length - 1].hidden = true;
    }
    iframe.hidden = false;

    i++;
    i %= framesContainer.children.length;
  }, interval);
}

window.onload = function(){
   sync_client_web_screen();
};
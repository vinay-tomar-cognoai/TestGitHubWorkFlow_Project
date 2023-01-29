var framesContainer = document.querySelector('#frames-container');
var currentFrameIdx = 0;
var playbackIntervalId = null;
var cobrowseSocket = null;
var is_page_reloaded = false;
var sync_client_web_screen_timer = null;
var cobrowsing_meta_data_page = 1;
var load_more_meta = false;

function create_and_iframe(html){
    var blob = new Blob([html], {
        type: 'text/html'
    });
    var iframe = document.createElement('iframe');
    iframe.src = window.URL.createObjectURL(blob);
    iframe.hidden = true;
    iframe.onload = renderFrame;
    iframe.setAttribute("class", "client-data-frame");
    framesContainer.appendChild(iframe);
    document.getElementById("easyassist-loader").style.display = "none";
    is_page_reloaded = false;    
}

function sync_client_web_screen() {

    let json_string = JSON.stringify({
        "id": COBROWSE_SESSION_ID
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/sync/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200 && response.is_active == false) {
                clearTimeout(sync_client_web_screen_timer);
                alert("Customer has left the session.");
                window.location = "/easy-assist/sales-ai/dashboard/";
            } else if (response.status == 200 && response.html != null && (response.is_updated == true || is_page_reloaded == true)) {
                var blob = new Blob([response.html], {
                    type: 'text/html'
                });
                var iframe = document.createElement('iframe');
                iframe.src = window.URL.createObjectURL(blob);
                iframe.hidden = true;
                iframe.onload = renderFrame;
                iframe.setAttribute("class", "client-data-frame");
                framesContainer.appendChild(iframe);
                document.getElementById("easyassist-loader").style.display = "none";
                is_page_reloaded = false;
            }
        }
    }
    xhttp.send(params);
}

function highlightElement(event, frame_window) {

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
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
        }
    }
    xhttp.send(params);
}

function renderFrame(event) {
    setTimeout(function () {
        event.preventDefault();
        if (framesContainer.children.length) {

            var frame = framesContainer.children[currentFrameIdx];
            if (!frame) {
                return;
            }

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
            frame.contentDocument.onkeydown = function (e) {
                e = e || window.event; //Get event
                e.preventDefault();
                e.stopPropagation();
            };

            // frame.contentWindow.scrollTo({top:scrollY, left:scrollX, behavior: 'smooth'});
            frame.contentWindow.scrollTo(scrollX, scrollY);
            //console.log("scrolled");
            //frame.hidden = false;
            //console.log("hidden-false");
            frame.contentWindow.document.onclick = function (event) {
                highlightElement(event, frame.contentWindow);
            }

            var active_element_list = [];
            active_element_list = frame.contentWindow.document.querySelectorAll("input[easyassist-active=\"true\"]");
            for(let index = 0; index < active_element_list.length; index++) {
                if (active_element_list[index].getAttribute("type") == "checkbox") {
                    active_element_list[index].parentElement.style.outline = "solid 2px #E83835 !important";
                } else if (active_element_list[index].getAttribute("type") == "radio") {
                    active_element_list[index].parentElement.style.outline = "solid 2px #E83835 !important";
                } else {
                    active_element_list[index].parentElement.style.outline = "solid 2px red";
                }
            }

            active_element_list = frame.contentWindow.document.querySelectorAll("select[easyassist-active=\"true\"]");
            for(let index = 0; index < active_element_list.length; index++) {
                active_element_list[index].parentElement.style.outline = "solid 2px #E83835 !important";
            }

            active_element_list = frame.contentWindow.document.querySelectorAll("textarea[easyassist-active=\"true\"]");
            for(let index = 0; index < active_element_list.length; index++) {
                active_element_list[index].parentElement.style.outline = "solid 2px #E83835 !important";
            }

            let div_element_list = frame.contentWindow.document.querySelectorAll("div");
            for(let index = 0; index < div_element_list.length; index++) {
                let div_ele = div_element_list[index];
                let scroll_left = div_ele.getAttribute("easyassist-data-scroll-x");
                let scroll_top = div_ele.getAttribute("easyassist-data-scroll-y");
                div_ele.scrollLeft = scroll_left;
                div_ele.scrollTop = scroll_top;
            }
            currentFrameIdx++;

            //frame.hidden = false;
        }
        document.getElementById("easyassist-loader").style.display = "none";

    }, 1000);
}

function playback(interval) {
    clearInterval(playbackIntervalId);

    if (!framesContainer.children.length) {
        return;
    }

    var i = 0;
    playbackIntervalId = setInterval(function () {
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

window.onload = function () {
    is_page_reloaded = true;
    sync_client_web_screen_timer = setInterval(function () {
        sync_client_web_screen();
    }, 2000);
};


function take_client_screenshot(type) {
    json_string = JSON.stringify({
        "id": COBROWSE_SESSION_ID,
        "screenshot_type": type
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/take-client-screenshot/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            console.log(response);
        }
    }
    xhttp.send(params);
}

function close_agent_confirm_session(element) {
    let comments = document.getElementById("close-session-remarks").value;

    if (comments.replace(/[^a-z0-9]/gi, '') == "") {
        alert("Comments can not be empty.");
        return;
    }

    json_string = JSON.stringify({
        "id": COBROWSE_SESSION_ID,
        "comments": comments
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "closing...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/close-session/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                window.location = "/easy-assist/sales-ai/dashboard/";
            } else {
                element.innerHTML = "Close";
            }
        }
    }
    xhttp.send(params);
}

function capture_client_screenshot_confirm() {
    take_client_screenshot("screenshot");
}

function capture_client_pageshot_confirm() {
    take_client_screenshot("pageshot");
}


function fetch_cobrowsing_meta_information() {

    if (load_more_meta == false) {
        cobrowsing_meta_data_page = 1;
        document.getElementById("meta_information_body").innerHTML = "Loading...";
    }

    json_string = JSON.stringify({
        "id": COBROWSE_SESSION_ID,
        "page": cobrowsing_meta_data_page
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/get-meta-information/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                var tbody_html = '';
                let meta_information_list = response.meta_information_list;
                for(let index = 0; index < meta_information_list.length; index++) {
                    //if (meta_information_list[index]["type"] == "screenshot") {
                        tbody_html += '<tr><td><a target="_blank" href="' + meta_information_list[index]["content"] + '">' + meta_information_list[index]["type"] + '</a></td><td>' + meta_information_list[index]["datetime"] + '</td></tr>';
                    //} else {
                    //    tbody_html += '<tr><td>' + meta_information_list[index]["type"] + '</td><td>' + meta_information_list[index]["datetime"] + '</td></tr>';
                    //}
                }
                if (response.is_last_page == false) {
                    tbody_html += '<tr onclick="load_more_meta_information(this)"><td colspan="2"><button class="btn btn-primary float-right">Load More</button></td></tr>';
                }

                if (cobrowsing_meta_data_page == 1) {
                    document.getElementById("meta_information_body").innerHTML = tbody_html;
                } else {
                    document.getElementById("meta_information_body").innerHTML += tbody_html;
                }
            } else {
                console.error("Unable to load the details. Kindly try again.");
            }
            load_more_meta = false;
        }
    }
    xhttp.send(params);
}

function load_more_meta_information(element) {
    element.parentElement.removeChild(element);
    cobrowsing_meta_data_page += 1;
    load_more_meta = true;
    fetch_cobrowsing_meta_information();
}


function share_cobrowsing_session(element){

    document.getElementById("share-session-error").innerHTML="";

    let support_agents = $("#multiple-support-agent").val();

    if (support_agents.length==0) {
        document.getElementById("share-session-error").innerHTML="Please select atleast one support agent with whom you want to share the session.";
        return;
    }

    json_string = JSON.stringify({
        "id": COBROWSE_SESSION_ID,
        "support_agents": support_agents
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "sharing..";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/share-session/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if(response.status==200){
                $("#askfor_support_modal").modal('hide');
            }
            element.innerHTML = "Share";
        }
    }
    xhttp.send(params);
}

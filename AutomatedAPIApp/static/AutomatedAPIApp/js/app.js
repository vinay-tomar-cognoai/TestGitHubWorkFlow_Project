/****************************** ACTIONS ON DOCUMENT & WINDOW EVENT ******************************/
$(document).ready(document_ready);
window.addEventListener("resize", window_resize);

window.SELECTED_METADATA = {
    'authorization_type': 'None',
}
window.last_api_response = {};
window.last_master_table_parser_list = [];
window.active_function_variables = {};
window.active_api_pk = -1;

body_history_dict = {
    'application/json': "",
    "text/plain": "",
    "application/javascript": "",
    "application/xml": "",
    "text/xml": "",
    "text/html": "",
}



function document_ready() {

    $('.datepicker').datepicker({
        endDate: '+0d',
    });

    $('.tms-tooltip').tooltip();

    $(".positive_numeric").on("keypress input", function(event) {
        var keyCode = event.which;
     
        if ( (keyCode != 8 || keyCode ==32 ) && (keyCode < 48 || keyCode > 57)) { 
            return false;
        }

        var self = $(this);
        self.val(self.val().replace(/\D/g, ""));
    });

    $(".mobile_number").on("keypress", tms_mobile_number_validation);

    // var auth_type_select = document.querySelector(".auto-api-authorization-type-select");
    // new AutomatedApiCustomSelect(auth_type_select, null, "#254a9c");
    
    var temp_response = {"message": "API Response will be shown here."}
    var editor =new JsonEditor('#request-response-container', temp_response);
    editor.load(temp_response);

    var auto_api_header_name = document.querySelectorAll(".auto-api-header-name");
    for(var index=0; index<auto_api_header_name.length; index++){
        auto_api_header_name[index].addEventListener("click", function(event){
            var target = event.target;
            var container = target.closest(".auto-api-subsection-container");
            var body = container.querySelector(".auto-api-subsection-body");
            if(container.className.indexOf("cognoai-collapsed") == -1){
                container.classList.add("cognoai-collapsed");
                $(body).toggle(700);
                // $(body).fadeOut( "slow", function() {});
            } else {
                $(body).toggle(700);
                container.classList.remove("cognoai-collapsed");
                // $(body).fadeIn( "fast", function() {});
                // body.style.display = "";
            }
        })
    }

    fetch_parent_tree_variable_names();
}

function tms_mobile_number_validation(event){
    var element = event.target;
    var value = element.value;
    var count = value.length;

    if ((event.keyCode >= 48 && event.keyCode <= 57) || (event.keyCode >= 96 && event.keyCode <= 105)) { 
        if(count >= 10){
            event.preventDefault();
        }
    }
}

function window_resize() {
    tooltip_utility_change();
}

document.querySelector("#content-wrapper").addEventListener(
    "scroll", 
    function(){
        var datepicket_dropdown = document.querySelector(".datepicker-dropdown");
        if(datepicket_dropdown){
            document.body.removeChild(datepicket_dropdown);
        }
    }
)

/****************************** TMS CONSOLE TOOLTIP ******************************/

function tooltip_utility_change() {
    if (window.innerWidth <= 767) {
        $('.tooltip-navbar').tooltip('dispose');
        $('.tooltip-navbar').css('width', '');
    } else {
        if (get_cookie("sales-ai-accordion-sidebar") == "toggled") {
            document.getElementById("accordionSidebar").classList.add("toggled");
            $(".tooltip-navbar").tooltip({
                boundary: 'window',
                placement: "right",
                container: 'body',
                trigger: 'hover'
            });
            $('.tooltip-navbar').tooltip('enable');
            $('.tooltip-navbar').css('width', '100%');
        }
    }
}

/****************************** TMS CONSOLE TOAST ******************************/

function show_automated_api_toast(message) {
    var element = document.getElementById("automated-api-snackbar");
    element.innerHTML = message;
    element.className = "show";
    setTimeout(function() {
        element.className = element.className.replace("show", "");
    }, 5000);
}

/****************************** TMS CONSOLE COOKIE ******************************/

function get_cookie(cookiename) {
    var cookie_name = cookiename + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var cookie_array = decodedCookie.split(';');
    for (var i = 0; i < cookie_array.length; i++) {
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

function set_cookie(cookiename, cookievalue, path = "") {
    var domain = window.location.hostname.substring(window.location.host.indexOf(".") + 1);

    if (window.location.hostname.split(".").length == 2 || window.location.hostname == "127.0.0.1") {
        domain = window.location.hostname;
    }

    if (path == "") {
        document.cookie = cookiename + "=" + cookievalue + ";domain=" + domain;
    } else {
        document.cookie = cookiename + "=" + cookievalue + ";path=" + path + ";domain=" + domain;
    }
}

/****************************** STRING PROCESS ******************************/

function stripHTML(text) {
    try {
        text = text.trim();
    } catch (err) {}

    var regex = /(<([^>]+)>)/ig;
    return text.replace(regex, "");
}

function remove_special_characters_from_str(text) {
    var regex = /:|;|'|"|=|-|\$|\*|%|!|`|~|&|\^|\(|\)|\[|\]|\{|\}|\[|\]|#|<|>|\/|\\/g;
    text = text.replace(regex, "");
    return text;
}

function get_updated_url_with_filters(filters){
    var key_value = "";
    for(var filter_key in filters){
        var filter_data = filters[filter_key];
        for(var index = 0; index < filter_data.length; index ++) {
            key_value += filter_key + "=" + filter_data[index] + "&";
        }
    }

    var newurl = window.location.protocol + "//" + window.location.host + window.location.pathname + '?' + key_value;
    return newurl;
}

function get_url_multiple_vars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m, key, value) {
        if (!(key in vars)) {
            vars[key] = [];
        }
        vars[key].push(value);
    });
    return vars;
}

function get_prev_active_content_type_language(auto_api_api_type_ul){
    try{
        var type_lis = auto_api_api_type_ul.querySelectorAll(".api-type-li.active");
        let el = type_lis[0]
        return el.getAttribute("api_type")
    }catch(err){
        console.log(err)
    }
}

function update_tbody_headers(value, add_empty_row=true) {
    var table_tbody = document.getElementById("header-table-tbody");

    var auto_api_api_type_ul = document.querySelector(".auto-api-api-type-ul");
    
    var type_lis = auto_api_api_type_ul.querySelectorAll(".api-type-li");

    let prev_selected_item = get_prev_active_content_type_language(auto_api_api_type_ul);

    for(var index=0; index<type_lis.length; index++){
        type_lis[index].classList.remove("active");
        if(type_lis[index].getAttribute("api_type") == value){
            type_lis[index].classList.add("active");
        }
    }

    table_tbody.innerHTML = '<tr>\
        <td><input class="form-control" type="text" value="' + 'Content-Type' + '" disabled/></td>\
        <td><input class="form-control" type="text" value="' + value + '" disabled/></td>\
        <td></td>\
    </tr>';

    if(add_empty_row){
        add_table_empty_row("", "");
    }
    let language = value.split("/")
    language = language[1]
    if(language == "plain"){
        language = "text";
    }
    
    if(language == "x-www-form-urlencoded"){
        $("#auto-api-subsection-api-body").hide()
    }else{
        $("#auto-api-subsection-api-body").show()
        let content = body_history_dict[value]
        change_api_body_input_language(language, content, prev_selected_item)

    }
}

function update_tbody_headers_based_on_authorization(value){

    var auto_api_api_type_ul = document.querySelector(".auto-api-authorization-ul");
    var type_lis = auto_api_api_type_ul.querySelectorAll(".api-auth-li");
    for(var index=0; index<type_lis.length; index++){
        type_lis[index].classList.remove("active");
        if(type_lis[index].getAttribute("auth_type") == value){
            type_lis[index].classList.add("active");
        }
    }

    var bearer_token_container = document.getElementById("bearer-token-input-container");
    var basic_auth_container = document.getElementById("basic-auth-input-container");
    var digest_auth_container = document.getElementById("digest-auth-input-container");
    var oauth_1_container = document.getElementById("oauth-1-input-container");

    bearer_token_container.style.display = "none";
    basic_auth_container.style.display = "none";
    digest_auth_container.style.display = "none";
    oauth_1_container.style.display = "none";

    if(value == "bearer-token") {
        bearer_token_container.style.display = "block";
    }else if (value == "basic-auth") {
        basic_auth_container.style.display = "block";
    }else if (value == "digest-auth") {
        digest_auth_container.style.display = "block";
    }else if (value == "oauth-1.0-auth") {
        oauth_1_container.style.display = "block";
    }

    window.SELECTED_METADATA["authorization_type"] = value;
}

function beautify_body_content(element) {
    // var textarea = document.getElementById(element.getAttribute("for"));
    try{
        let editor = ace.edit("api-body")
        let api_body = editor.getValue()
        var json_data = JSON.parse(api_body);         
        editor.setValue(JSON.stringify(json_data, null, 4))
        // var json_data = JSON.parse(textarea.value);  
        // textarea.value = JSON.stringify(json_data, null, 4);
    }catch(err){
        alert("Invalid data");
    }
}

var getFromBetween = {
    results:[],
    string:"",
    getFromBetween:function (sub1,sub2) {
        if(this.string.indexOf(sub1) < 0 || this.string.indexOf(sub2) < 0) return false;
        var SP = this.string.indexOf(sub1)+sub1.length;
        var string1 = this.string.substr(0,SP);
        var string2 = this.string.substr(SP);
        var TP = string1.length + string2.indexOf(sub2);
        return this.string.substring(SP,TP);
    },
    removeFromBetween:function (sub1,sub2) {
        if(this.string.indexOf(sub1) < 0 || this.string.indexOf(sub2) < 0) return false;
        var removal = sub1+this.getFromBetween(sub1,sub2)+sub2;
        this.string = this.string.replace(removal,"");
    },
    getAllResults:function (sub1,sub2) {
        // first check to see if we do have both substrings
        if(this.string.indexOf(sub1) < 0 || this.string.indexOf(sub2) < 0) return;

        // find one result
        var result = this.getFromBetween(sub1,sub2);
        // push it to the results array
        this.results.push(result);
        // remove the most recently found one from the string
        this.removeFromBetween(sub1,sub2);

        // if there's more substrings
        if(this.string.indexOf(sub1) > -1 && this.string.indexOf(sub2) > -1) {
            this.getAllResults(sub1,sub2);
        }
        else return;
    },
    get:function (string,sub1,sub2) {
        this.results = [];
        this.string = string;
        this.getAllResults(sub1,sub2);
        return this.results;
    }
};

function execute_api(){

    let request_type = document.getElementById("request-type").value;
    let request_url = document.getElementById("request-url").value;
    let editor = ace.edit("api-body")
    let api_body = editor.getValue()
    // let api_body = document.getElementById("api-body").value;

    if (request_url.trim() == "") {
        alert("Please enter valid API request url.");
        return;
    }

    let check_for_dynamic_variables = getFromBetween.get(api_body, "{/", "/}");

    check_for_dynamic_variables = check_for_dynamic_variables.concat(getFromBetween.get(request_url, "{/", "/}"));

    let table_inner_html = '';
    if (check_for_dynamic_variables.length != 0) {
        table_inner_html = '<p>Dynamic request parameter found. Please enter test input parameter for the data.</p><table class="table table-striped" style="table-layout: auto; width:100%;">\
            <thead>\
                <tr>\
                    <th>key</th>\
                    <th>value</th>\
                </tr>\
            </thead><tbody id="api-execution-request-packet-tbody">';

        for(var index=0; index < check_for_dynamic_variables.length; index++) {
            table_inner_html += '<tr><td>'+check_for_dynamic_variables[index]+'</td><td><input type="text" class="form-control"/></td></tr>';
        }
        
        table_inner_html += '</tbody></table>';

        document.getElementById("api-execution-request-packet").innerHTML = table_inner_html;
        $('#dynamic-request-parameter-confirmation-modal').modal('show');
    } else {
        execute_dynamic_api();
        // table_inner_html = '<p>No dynamic request parameters found. Are you want to execute API?</p>'
    }

}

function execute_dynamic_api() {

    let request_type = document.getElementById("request-type").value;
    let request_url = document.getElementById("request-url").value;
    // let api_body = document.getElementById("api-body").value;
    let editor = ace.edit("api-body")
    let api_body = editor.getValue()

    let api_test_body = api_body;

    let dynamic_request_table = document.getElementById("api-execution-request-packet-tbody");

    if (dynamic_request_table != null && dynamic_request_table != undefined) {
        let tr_children = dynamic_request_table.children;
        for(var index=0; index < tr_children.length; index++) {
            var variable_key = tr_children[index].children[0].innerHTML;
            var variable_test_value = tr_children[index].children[1].children[0].value;

            if(variable_test_value.trim() == "") {
                alert("Please enter valid test value for " + variable_key + " variable.");
                return;
            }
            api_test_body = api_test_body.replace("{/" + variable_key + "/}", variable_test_value);
            request_url = request_url.replace("{/" + variable_key + "/}", variable_test_value);
        }
        $('#dynamic-request-parameter-confirmation-modal').modal('hide');
    }
    let tbody = document.getElementById("header-table-tbody").children;
    let headers = {}
    for(var tr_index = 0; tr_index < tbody.length-1; tr_index++) {
        let key = tbody[tr_index].children[0].children[0].value;
        let value = tbody[tr_index].children[1].children[0].value;
        headers[key] = value;
    }

    let authorization_type = window.SELECTED_METADATA["authorization_type"];
    let authorization_params = {};
    authorization_params["type"] = authorization_type;

    if (authorization_type == "bearer-token") {
        let token = document.getElementById("bearer-token-input").value;

        if (token.trim() == "") {
            alert("Please enter valid bearer token for authorization.");
            return;
        }

        authorization_params["params"] = {
            "token": token
        }
    } else if (authorization_type == "basic-auth") {

        let basic_auth_username = document.getElementById("basic-auth-username").value;
        let basic_auth_password = document.getElementById("basic-auth-password").value;

        if (basic_auth_username.trim() == "") {
            alert("Please enter valid username for basic authorization.");
            return;
        }

        if (basic_auth_password.trim() == "") {
            alert("Please enter valid password for basic authorization.");
            return;
        }

        authorization_params["params"] = {
            "username": basic_auth_username,
            "password": basic_auth_password
        }

    } else if (authorization_type == "digest-auth") {
 
        let digest_auth_username = document.getElementById("digest-auth-username").value;
        let digest_auth_password = document.getElementById("digest-auth-password").value;

        if (digest_auth_username.trim() == "") {
            alert("Please enter valid username for digest authorization.");
            return;
        }

        if (digest_auth_password.trim() == "") {
            alert("Please enter valid password for digest authorization.");
            return;
        }

        authorization_params["params"] = {
            "username": digest_auth_username,
            "password": digest_auth_password
        }

    } else if (authorization_type == "oauth-1.0-auth") {
 
        let oauth1_consumer_key = document.getElementById("oauth-1-auth-consumer-key").value;
        let oauth1_consuer_secret = document.getElementById("oauth-1-auth-consumer-secret").value;
        let oauth1_access_token = document.getElementById("oauth-1-auth-access-token").value;
        let oauth1_token_secret = document.getElementById("oauth-1-auth-token-secret").value;

        if (oauth1_consumer_key.trim() == "") {
            alert("Please enter valid consumer key for OAuth 1.0 authorization.");
            return;
        }

        if (oauth1_consuer_secret.trim() == "") {
            alert("Please enter valid consumer key for OAuth 1.0 authorization.");
            return;
        }

        if (oauth1_access_token.trim() == "") {
            alert("Please enter valid consumer key for OAuth 1.0 authorization.");
            return;
        }

        if (oauth1_token_secret.trim() == "") {
            alert("Please enter valid consumer key for OAuth 1.0 authorization.");
            return;
        }

        authorization_params["params"] = {
            "consumer-key": oauth1_consumer_key,
            "consumer-secret": oauth1_consuer_secret,
            "access-token": oauth1_access_token,
            "token-secret": oauth1_token_secret
        }

    }

    authorization_params = JSON.stringify(authorization_params);
    headers = JSON.stringify(headers);

    let dynamic_response_variables = getFromBetween.get(api_body, "{{", "}}");
    dynamic_response_variables = dynamic_response_variables.concat(getFromBetween.get(request_url, "{{", "}}"));
    dynamic_response_variables = dynamic_response_variables.concat(getFromBetween.get(authorization_params, "{{", "}}"));
    dynamic_response_variables = dynamic_response_variables.concat(getFromBetween.get(headers, "{{", "}}"));

    for(let index=0; index<dynamic_response_variables.length; index++){
        let dynamic_response_variable = dynamic_response_variables[index];
        if(sessionStorage.getItem(dynamic_response_variable) ){
            api_test_body = api_test_body.replace("{{" + dynamic_response_variable + "}}", "\"" + sessionStorage.getItem(dynamic_response_variable) + "\"");
            request_url = request_url.replace("{{" + dynamic_response_variable + "}}", sessionStorage.getItem(dynamic_response_variable));
            authorization_params = authorization_params.replace("{{" + dynamic_response_variable + "}}", sessionStorage.getItem(dynamic_response_variable));
            headers = headers.replace("{{" + dynamic_response_variable + "}}", sessionStorage.getItem(dynamic_response_variable));
        }
    }

    let json_params = JSON.stringify({
        "type": request_type,
        "url": request_url,
        "body": api_test_body,
        "authorization": authorization_params,
        "headers": headers
    })

    let encrypted_data = auto_api_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    show_automated_api_toast("Sending your request. You will see the response below.");

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/automated-api/test/execute-api/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = auto_api_custom_decrypt(response.Response);
            response = JSON.parse(response);
            last_api_response = {};
            if(response["status"] == 200) {
                let content_type = response["api_response"]["headers"]["Content-Type"];
                if(content_type.indexOf("application/json")!=-1){
                    response["api_response"]["body"] = JSON.parse(response["api_response"]["body"]);
                    last_api_response = response["api_response"]["body"];
                    let editor =new JsonEditor('#request-response-container', response);
                    editor.load(response);
                    document.querySelector("#parse-response-button").style.display = "";
                }else{                    
                    document.getElementById("request-response-container").innerHTML = JSON.stringify(response, 4);
                }
                document.getElementById("api-response-container").style.display = "block";
                parse_json_data_and_load_into_table()
                document.querySelector(".api-response-card").scrollIntoView();
            }else{
                show_automated_api_toast("Internal server error");
            }
            draw_active_functions_usable_variable();
        } else if(this.readyState == 4){
            show_automated_api_toast("Something went wrong");
        }
    }
    xhttp.send(params);
}

function update_headers_based_on_content_type(content_type, body){

    if(content_type != "application/x-www-form-urlencoded"){
        return
    }

    for(var key in body){
        add_table_row(key, body[key]);
    }
}


function fetch_parent_tree_variable_names() {

    let api_pk = -1;

    try{
        if("api_pk" in get_url_multiple_vars()){
            api_pk = get_url_multiple_vars()["api_pk"][0];
        }
    }catch(err){}

    let json_params = JSON.stringify({
        "tree_id": get_url_multiple_vars()["tree_id"][0],
        "api_pk": api_pk,
    });

    let encrypted_data = auto_api_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/automated-api/test/fetch-parent-tree-variables/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = auto_api_custom_decrypt(response.Response);
            response = JSON.parse(response);
            console.log("response = ", response);
            let variable_name_list = "";
            let post_processor_variable_html = "";
            if(response.status == 200) {
                let tbody_html = "";
                for(var index=0; index < response["parent_variable_names"].length; index++){
                    let parent_variable_name = response["parent_variable_names"][index];
                    post_processor_variable_html += [
                        "<tr>",
                            "<td>" + parent_variable_name + "</td>",
                            "<td> <input class='form-control' type='text' value={/" + parent_variable_name + "/} disabled/> </td>",
                        "</tr>"
                    ].join("");
                    // variable_name_list += "<a href='javascript:void(0)' onclick='set_variable_into_api(this)' variable=""+parent_variable_name+"">@"+parent_variable_name+"</a>";
                }

                if (response["integrated_api"] != null) {
                    window.active_api_pk = response["integrated_api"]["api_pk"]
                    if(response["integrated_api"]["type"] == "GET"){
                        document.querySelector("#request-type [value=GET]").setAttribute("selected", "");
                        document.querySelector("#request-type [value=POST]").removeAttribute("selected");
                    } else {
                        document.querySelector("#request-type [value=GET]").removeAttribute("selected");
                        document.querySelector("#request-type [value=POST]").setAttribute("selected", "");
                    }
                    // document.getElementById("request-type").value = response["integrated_api"]["type"];
                    document.getElementById("request-url").value = response["integrated_api"]["url"];
                    // document.getElementById("api-body").value = response["integrated_api"]["body"];   
                    
                    setTimeout(function (){
                        let editor = ace.edit("api-body")
                        editor.setValue(response["integrated_api"]["body"])  
                    },1000)     
                    let headers = JSON.parse(response["integrated_api"]["headers"]);
                    let authorization = JSON.parse(response["integrated_api"]["authorization"]);
                    let variables = JSON.parse(response["integrated_api"]["variables"]);
                    let body;
                    try{
                        body = JSON.parse(response["integrated_api"]["body"]);
                    } catch (err) {
                        body = "";
                    }

                    let have_extra_headers = false;
                    content_type = ""
                    for(var header_key in headers){
                        if(header_key=="Content-Type"){
                            update_tbody_headers(headers[header_key], false);
                            content_type = headers[header_key]
                            // document.getElementById("request-header-type").value = headers[header_key];
                            // update_tbody_headers(document.getElementById("request-header-type"));
                        } else {
                            have_extra_headers = true;
                            add_table_row(header_key, headers[header_key]);
                        }
                    }
                    update_headers_based_on_content_type(content_type, body)
                    add_table_empty_row();

                    let authorization_type = "None";
                    if ("type" in authorization) {                    
                        authorization_type = authorization["type"];
                    }
                    // document.getElementById("request-authorization-type").value = authorization_type;
                    // $("#request-authorization-type").change();

                    if (authorization_type == "bearer-token") {
                        document.getElementById("bearer-token-input").value = authorization["params"]["token"];   
                    } else if (authorization_type == "basic-auth") {                        
                        document.getElementById("basic-auth-username").value = authorization["params"]["username"];   
                        document.getElementById("basic-auth-password").value = authorization["params"]["password"];   
                    } else if (authorization_type == "digest-auth") {                        
                        document.getElementById("digest-auth-username").value = authorization["params"]["username"];   
                        document.getElementById("digest-auth-password").value = authorization["params"]["password"];   
                    } else if (authorization_type == "oauth-1.0-auth") {
                        document.getElementById("oauth-1-auth-consumer-key").value = authorization["params"]["consumer-key"];
                        document.getElementById("oauth-1-auth-consumer-secret").value = authorization["params"]["consumer-secret"];
                        document.getElementById("oauth-1-auth-access-token").value = authorization["params"]["access-token"];
                        document.getElementById("oauth-1-auth-token-secret").value = authorization["params"]["token-secret"];                        
                    }
                    update_tbody_headers_based_on_authorization(authorization_type);

                    if(variables){
                        window.active_function_variables = variables;
                    }
                } else {
                    update_tbody_headers("application/json", true);
                }

                window.all_api_variable_list = response["all_api_variable_list"];
                draw_active_functions_usable_variable();

                var method_select = document.querySelector(".auto-api-metadata-1-method-select");
                new AutomatedApiCustomSelect(method_select, null, "#254a9c");
            }

            let post_processor_variables_table = document.querySelector("#post-processor-variables-table");
            let post_processor_variables_info = document.querySelector("#post-processor-variables-info");
            if(post_processor_variable_html == ""){
                post_processor_variables_table.style.display = "none";
                post_processor_variables_info.innerHTML = "No post processor variable available";
            } else {
                post_processor_variables_table.querySelector("tbody").innerHTML = post_processor_variable_html;
                post_processor_variables_table.style.display = "";
                post_processor_variables_info.innerHTML = "NOTE: You can use this variables as given in 'how to use' column";
            }

            // document.getElementById("variable-custom-sidenav-container").innerHTML+=variable_name_list;
        } else if(this.readyState == 4){
            show_automated_api_toast("Something went wrong");
        }
    }
    xhttp.send(params);    
}

function save_active_api_metadata() {

    let request_type = document.getElementById("request-type").value;
    let request_url = document.getElementById("request-url").value;
    let editor = ace.edit("api-body")
    let api_body = editor.getValue()
    // let api_body = document.getElementById("api-body").value;

    let tbody = document.getElementById("header-table-tbody").children;
    let headers = {}
    for(var tr_index = 0; tr_index < tbody.length-1; tr_index++) {
        let key = tbody[tr_index].children[0].children[0].value;
        let value = tbody[tr_index].children[1].children[0].value;
        headers[key] = value;
    }

    let variables = window.active_function_variables;

    let authorization_type = window.SELECTED_METADATA["authorization_type"];
    let authorization_params = {};
    authorization_params["type"] = authorization_type;

    if (authorization_type == "bearer-token") {
        let token = document.getElementById("bearer-token-input").value;

        if (token.trim() == "") {
            alert("Please enter valid bearer token for authorization.");
            return;
        }

        authorization_params["params"] = {
            "token": token
        }
    } else if (authorization_type == "basic-auth") {

        let basic_auth_username = document.getElementById("basic-auth-username").value;
        let basic_auth_password = document.getElementById("basic-auth-password").value;

        if (basic_auth_username.trim() == "") {
            alert("Please enter valid username for basic authorization.");
            return;
        }

        if (basic_auth_password.trim() == "") {
            alert("Please enter valid password for basic authorization.");
            return;
        }

        authorization_params["params"] = {
            "username": basic_auth_username,
            "password": basic_auth_password
        }

    } else if (authorization_type == "digest-auth") {
 
        let digest_auth_username = document.getElementById("digest-auth-username").value;
        let digest_auth_password = document.getElementById("digest-auth-password").value;

        if (digest_auth_username.trim() == "") {
            alert("Please enter valid username for digest authorization.");
            return;
        }

        if (digest_auth_password.trim() == "") {
            alert("Please enter valid password for digest authorization.");
            return;
        }

        authorization_params["params"] = {
            "username": digest_auth_username,
            "password": digest_auth_password
        }

    }  else if (authorization_type == "oauth-1.0-auth") {
 
        let oauth1_consumer_key = document.getElementById("oauth-1-auth-consumer-key").value;
        let oauth1_consuer_secret = document.getElementById("oauth-1-auth-consumer-secret").value;
        let oauth1_access_token = document.getElementById("oauth-1-auth-access-token").value;
        let oauth1_token_secret = document.getElementById("oauth-1-auth-token-secret").value;

        if (oauth1_consumer_key.trim() == "") {
            alert("Please enter valid consumer key for OAuth 1.0 authorization.");
            return;
        }

        if (oauth1_consuer_secret.trim() == "") {
            alert("Please enter valid consumer key for OAuth 1.0 authorization.");
            return;
        }

        if (oauth1_access_token.trim() == "") {
            alert("Please enter valid consumer key for OAuth 1.0 authorization.");
            return;
        }

        if (oauth1_token_secret.trim() == "") {
            alert("Please enter valid consumer key for OAuth 1.0 authorization.");
            return;
        }

        authorization_params["params"] = {
            "consumer-key": oauth1_consumer_key,
            "consumer-secret": oauth1_consuer_secret,
            "access-token": oauth1_access_token,
            "token-secret": oauth1_token_secret
        }

    }

    show_automated_api_toast("Saving API details.");

    let json_params = JSON.stringify({
        "type": request_type,
        "url": request_url,
        "body": api_body,
        "tree_id": get_url_multiple_vars()["tree_id"][0],
        "api_pk": window.active_api_pk,
        "authorization": JSON.stringify(authorization_params),
        "headers": JSON.stringify(headers),
        "variables": JSON.stringify(variables),
    })

    let encrypted_data = auto_api_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    let params = JSON.stringify(encrypted_data);

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/automated-api/tag-api-tree/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = auto_api_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if(response["status"] == 200){
                let dictionary = get_url_multiple_vars();
                dictionary["api_pk"] = [response["api_pk"]];
                setTimeout(function(){
                    window.location.href = get_updated_url_with_filters(dictionary);
                }, 1000);
            }
        }
    }
    xhttp.send(params);    
}


function open_custom_sidenav() {
  document.getElementById("variable-custom-sidenav-container").style.width = "250px";
}

/* Set the width of the side navigation to 0 */
function close_custom_sidenav() {
  document.getElementById("variable-custom-sidenav-container").style.width = "0";
}

function set_variable_into_api(element) {
    variable_name = element.getAttribute("variable");
    variable_name = "{/" + variable_name + "/}";

    /////////// Based on current active element, dynamic variable will be added to that element
    active_element = document.getElementById(current_active_element);
    var cursorPosition = active_element.selectionStart
    var new_request_body = active_element.value.substr(0, cursorPosition-1) + variable_name + active_element.value.substr(cursorPosition, ) ;
    active_element.value = new_request_body;
    // close_custom_sidenav();
}

function check_for_variable_input_textarea(element){
    body_value = element.value.trim();
    current_active_element = element.id
    cursorPosition = element.selectionStart;
    if(body_value != "" && body_value[cursorPosition-1]=="@") {
        // open_custom_sidenav();
    }
}

function delete_header_table_row(element){
    element.parentElement.parentElement.removeChild(element.parentElement);
}

function add_table_row(key, value) {
    table_tbody = document.getElementById("header-table-tbody");
    table_tbody.innerHTML += '<tr>\
        <td><input class="form-control" type="text" value="' + key + '"/></td>\
        <td><input class="form-control" type="text" value="' + value + '"/></td>\
        <td onclick="delete_header_table_row(this)" style="cursor:pointer;"><i class="fa fa-trash" style="color:red;"></i></td>\
    </tr>';
}

function add_table_empty_row() {
    let table_tbody = document.getElementById("header-table-tbody");
    let html = '<tr class="header-empty-input-tr">\
        <td><input class="form-control header-empty-input" type="text"/></td>\
        <td><input class="form-control header-empty-input" type="text"/></td>\
        <td class="delete_button"></td>\
    </tr>';

    table_tbody.insertAdjacentHTML("beforeend", html);

    let header_empty_inputs = document.querySelectorAll(".header-empty-input");
    for(let index=0; index<header_empty_inputs.length; index++){
        header_empty_inputs[index].addEventListener("input", header_empty_input_event_listener);
    }
}

function header_empty_input_event_listener(event){
    let value = event.target.value;
    value = value.trim();
    if(value == "") return;

    let header_empty_input_tr = document.querySelector(".header-empty-input-tr");
    header_empty_input_tr.classList.remove("header-empty-input-tr");

    let delete_button = header_empty_input_tr.querySelector(".delete_button");
    $(delete_button).attr("onclick", "delete_header_table_row(this)")
    delete_button.style.cursor = "pointer";
    delete_button.innerHTML = '<i class="fa fa-trash" style="color:red;"></i>';

    let header_empty_inputs = document.querySelectorAll(".header-empty-input");
    for(var index=0; index<header_empty_inputs.length; index++){
        header_empty_inputs[index].removeEventListener("input", header_empty_input_event_listener);
        header_empty_inputs[index].classList.remove("header-empty-input");
    }

    add_table_empty_row();
}

function check_variable_already_exists(key){
    for(let variable in window.active_function_variables){
        if(window.active_function_variables[variable] == key){
            return true;
        }
    }
    return false;
}

function get_variable_name_from_response_key(key){
    for(let variable in window.active_function_variables){
        if(window.active_function_variables[variable] == key){
            return variable;
        }
    }
    return null;
}

function recursive_json_parser(dict, prefix) {
    for(dict_key in dict){
        let new_key = prefix + "['" + dict_key + "']";

        if ( check_variable_already_exists(new_key) ){
            sessionStorage.setItem(get_variable_name_from_response_key(new_key), dict[dict_key]);
            continue;
        }

        if (dict[dict_key] == null) {
            last_master_table_parser_list.push({
                "key": new_key,
                "value": dict[dict_key],
                "type": "None"
            })
        }else if(typeof(dict[dict_key]) == "string") {
            last_master_table_parser_list.push({
                "key": new_key,
                "value": dict[dict_key],
                "type": "string"
            })
        }else if(typeof(dict[dict_key]) == "number") {
            last_master_table_parser_list.push({
                "key": new_key,
                "value": dict[dict_key],
                "type": "number"
            })
        }else if(Array.isArray(dict[dict_key])){

            if (dict[dict_key].length!=0 && typeof(dict[dict_key][0]) == "string") {
                last_master_table_parser_list.push({
                    "key": new_key,
                    "value": dict[dict_key],
                    "type": "list-string"
                })
            } else if (dict[dict_key].length!=0 && typeof(dict[dict_key][0]) == "number") {
                last_master_table_parser_list.push({
                    "key": new_key,
                    "value": dict[dict_key],
                    "type": "list-number"
                })
            } else if (dict[dict_key].length!=0 && Array.isArray(dict[dict_key][0])) {
                last_master_table_parser_list.push({
                    "key": new_key,
                    "value": dict[dict_key],
                    "type": "list-list"
                })
            } else if (dict[dict_key].length!=0) {
                list_dict_key_list = [];
                for(list_dict_key in dict[dict_key][0]) {
                    list_dict_key_list.push(list_dict_key);
                }
                last_master_table_parser_list.push({
                    "key": new_key,
                    "value": list_dict_key_list,
                    "type": "list-dict"
                })
            }
        }else{
            prefix += "[" + dict_key + "]"
            recursive_json_parser(dict[dict_key], prefix);
        }
    }
}

function parse_json_data_and_load_into_table() {

    try{
        for(let variable in window.active_function_variables){
            sessionStorage.removeItem(variable);
        }
    } catch(err){
        console.log("ERROR : ", err);
    }

    last_master_table_parser_list = [];
    recursive_json_parser(last_api_response, "api_response_data");
    total_html = "";
    for(var index =0; index < last_master_table_parser_list.length; index++) {
        total_html += '<tr class="response-parse-tr">\
            <td style="max-width: 250px;" class="data-from-response">'+last_master_table_parser_list[index]["key"]+'</td>\
            <td>'+last_master_table_parser_list[index]["value"]+'</td>\
            <td>'+last_master_table_parser_list[index]["type"].toString()+'</td>\
            <td><input response_index="'+index+'" class="response-parse-alias-input form-control" placeholder="Enter variable name" type="text" value=""/></td>\
            <td><input response_index="'+index+'" type="checkbox" class="response-parse-checkbox"/></td>\
        </tr>';
    }

    document.getElementById("parse_json_data_and_load_into_table_container").innerHTML = total_html;
    // document.getElementById("parse_json_data_and_load_into_table_container").scrollIntoView();
    // $("#parsed-json-data-show-modal").modal("show");
}

function save_api_response_variables(){
    let checked_eles = document.querySelectorAll(".response-parse-checkbox");

    let variables = window.active_function_variables;

    for(let index=0; index<checked_eles.length; index++){
        if(checked_eles[index].checked == false) continue;

        let response_parse_tr = checked_eles[index].closest(".response-parse-tr");
        let response_parse_alias_input = response_parse_tr.querySelector(".response-parse-alias-input");
        let key = response_parse_alias_input.value;
        key = key.trim();
        if(key == ""){
            show_automated_api_toast("please provide valid variable name");
            return;
        }
        let data = response_parse_tr.querySelector(".data-from-response").innerHTML;
        variables[key] = data
    }

    $("#parsed-json-data-show-modal").modal("hide");
    save_active_api_metadata();
}

function draw_active_functions_usable_variable(){
    let active_fun_var_table = document.querySelector("#active-functions-usabled-variable-table");
    let active_fun_var_tbody = active_fun_var_table.querySelector("tbody");
    let tbody_html = "";
    for (let index=0; index<window.all_api_variable_list.length; index++) {
        let variables = JSON.parse(window.all_api_variable_list[index]);
        for(let variable in variables){
            tbody_html += [
                "<tr>",
                    "<td>" + (index+1) + "</td>",
                    "<td>" + variable + "</td>",
                    "<td> " + variables[variable] + " </td>",
                    "<td> " + sessionStorage.getItem(variable) + " </td>",
                    "<td> <input type='text' class='form-control' value={{" + variable + "}} disabled/> </td>"
            ].join("");

            if(variable in window.active_function_variables){
                tbody_html += "<td> <i class='fa fa-trash' style='color:red;cursor: pointer;' onclick='delete_active_function_variable(this, \"" + variable + "\")'></i></td>";
            } else {
                tbody_html += "<td> <i class='fa fa-trash' style='color:red;cursor: pointer;' onclick='can_not_delete_not_active_api()'></i></td>";
            }

            tbody_html += [
                "</tr>"
            ].join("");
        }
    }

    if(tbody_html == ""){
        active_fun_var_table.style.display = "none";
        document.querySelector("#active-functions-usabled-variable-info").innerHTML = "No response variable used";
    } else {
        active_fun_var_tbody.innerHTML = tbody_html;
        active_fun_var_table.style.display = "";
        document.querySelector("#active-functions-usabled-variable-info").innerHTML = "NOTE: You can use this variables as given in 'how to use' column";
    }
}

function delete_active_function_variable(element, variable_name){
    let tr_tag = element.closest("tr");
    tr_tag.parentElement.removeChild(tr_tag);
    delete window.active_function_variables[variable_name];
    show_automated_api_toast("Press save button to delete");
}

function can_not_delete_not_active_api(){
    show_automated_api_toast("To delete this go to relevant function");
}

function generate_automated_api() {

    if(window.active_api_pk == -1){
        show_automated_api_toast("Please save api to generate code");
        return;
    }

    let json_params = JSON.stringify({
        "tree_id": get_url_multiple_vars()["tree_id"][0]
    });

    let encrypted_data = auto_api_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    show_automated_api_toast("Generating API code. You will see the response below.");

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/automated-api/generate-automated-code/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = auto_api_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if(response.status == 200){

                let generated_code = response["generated_code"];

                window.api_generated_code = ace.edit("api-generated-code");
                api_generated_code.setTheme("ace/theme/monokai");
                document.getElementById('api-generated-code').style.fontSize='14px';
                api_generated_code.getSession().setMode("ace/mode/python");
                api_generated_code.setOptions({
                    enableBasicAutocompletion: true,
                    enableSnippets: true
                });

                api_generated_code.setValue(generated_code);

                document.querySelector(".api-generated-code-card").style.display = "";
                document.querySelector(".api-generated-code-card").scrollIntoView();
                // window.location = decodeURIComponent(get_url_multiple_vars()["previous_location"]);
            }else{
                alert("Unable to generate the automated api code.")
            }
        }
    }
    xhttp.send(params);
}

function go_full_screen_mode() {
    window.api_generated_code.container.webkitRequestFullscreen()
}

function save_code_into_api_tree_api_call(){
    var api_code = window.api_generated_code.getValue();
    let json_params = JSON.stringify({
        "tree_id": get_url_multiple_vars()["tree_id"][0],
        "api_code": api_code,
    });

    let encrypted_data = auto_api_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/automated-api/save-code-into-api-tree/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = auto_api_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if(response.status == 200){
                window.location = decodeURIComponent(get_url_multiple_vars()["previous_location"][0]);
            }else{
                alert("Unable to generate the automated api code.")
            }
        }
    }
    xhttp.send(params);
}


function save_code_into_api_tree(is_api_tree_already_present){

    if(is_api_tree_already_present != 'False'){
        $("#genrate_api_tree_confirmation_modal").modal("show")
        return
    }
    save_code_into_api_tree_api_call();
}

function save_previous_history(prev_selected_item){

    editor = ace.edit("api-body");
    prev_value = editor.getValue();
    body_history_dict[prev_selected_item] = prev_value

}

function change_api_body_input_language(lang, content, prev_selected_item){

    save_previous_history(prev_selected_item)
    var elementExists = document.getElementById("api-body");
    container_elem = document.getElementById("auto-api-subsection-api-body")
    if( elementExists ) {
        container_elem.removeChild(elementExists);
    }
    var div = document.createElement("div");
    div.innerHTML = "";
    div.id = "api-body";
    document.body.appendChild(div);
    $("#auto-api-subsection-api-body").append(div)
    editor = ace.edit("api-body");
    editor.setValue(content)
    editor.setTheme("ace/theme/monokai");
    editor.session.setMode("ace/mode/" + lang);
}

/****************************** GET ACTIVE AGENT SPECIFIC SETTINGS ******************************/

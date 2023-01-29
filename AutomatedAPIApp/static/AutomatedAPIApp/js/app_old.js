var last_api_response = null;
var last_master_table_parser_list = [];

///////////// ID of current active element
var current_active_element = "";

function get_url_vars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m, key, value) {
        vars[key] = value;
    });
    return vars;
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

function execute_api(element){

	request_type = document.getElementById("request-type").value;
	request_url = document.getElementById("request-url").value;
	api_body = document.getElementById("api-body").value;

    if (request_url.trim() == "") {
        alert("Please enter valid API request url.");
        return;
    }

    check_for_dynamic_variables = getFromBetween.get(api_body, "{/", "/}");

    check_for_dynamic_variables = check_for_dynamic_variables.concat(getFromBetween.get(request_url, "{/", "/}"));

    table_inner_html = '';
    if (check_for_dynamic_variables.length != 0) {
        table_inner_html = '<p>Dynamic request parameter found. Please enter test input parameter for the data.</p><table class="table table-striped" style="table-layout: auto; width:100%;">\
            <thead>\
                <tr>\
                    <th>key</th>\
                    <th>value</th>\
                </tr>\
            </thead><tbody id="api-execution-request-packet-tbody">';

        for(var index=0; index < check_for_dynamic_variables.length; index++) {
            table_inner_html += '<tr><td>'+check_for_dynamic_variables[index]+'</td><td contenteditable="true"></td></tr>';
        }
        
        table_inner_html += '</tbody></table>';
    } else {
        table_inner_html = '<p>No dynamic request parameters found. Are you want to execute API?</p>'
    }

    document.getElementById("api-execution-request-packet").innerHTML = table_inner_html;

    $('#dynamic-request-parameter-confirmation-modal').modal('show');
}


function execute_dynamic_api(element) {

    request_type = document.getElementById("request-type").value;
    request_url = document.getElementById("request-url").value;
    api_body = document.getElementById("api-body").value;
    api_test_body = api_body;

    dynamic_request_table = document.getElementById("api-execution-request-packet-tbody");

    if (dynamic_request_table != null && dynamic_request_table != undefined) {
        tr_children = dynamic_request_table.children;
        for(var index=0; index < tr_children.length; index++) {
            var variable_key = tr_children[index].children[0].innerHTML;
            var variable_test_value = tr_children[index].children[1].innerHTML;

            if(variable_test_value.trim() == "") {
                alert("Please enter valid test value for "+variable_key+" variable.");
                return;
            }
            api_test_body = api_test_body.replace("{/" + variable_key + "/}", variable_test_value);
            request_url = request_url.replace("{/" + variable_key + "/}", variable_test_value);
        }
    }
    tbody = document.getElementById("header-table-tbody").children;
    headers = {}
    for(var tr_index = 0; tr_index < tbody.length; tr_index++) {
        key = tbody[tr_index].children[0].innerHTML;
        value = tbody[tr_index].children[1].innerHTML;      
        headers[key] = value;
    }

    authorization_type = document.getElementById("request-authorization-type").value;
    authorization_params = {};
    authorization_params["type"] = authorization_type;

    if (authorization_type == "bearer-token") {
        token = document.getElementById("bearer-token-input").value;

        if (token.trim() == "") {
            alert("Please enter valid bearer token for authorization.");
            return;
        }

        authorization_params["params"] = {
            "token": token
        }
    } else if (authorization_type == "basic-auth") {

        basic_auth_username = document.getElementById("basic-auth-username").value;
        basic_auth_password = document.getElementById("basic-auth-password").value;

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
 
        digest_auth_username = document.getElementById("digest-auth-username").value;
        digest_auth_password = document.getElementById("digest-auth-password").value;

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
 
        oauth1_consumer_key = document.getElementById("oauth-1-auth-consumer-key").value;
        oauth1_consuer_secret = document.getElementById("oauth-1-auth-consumer-secret").value;
        oauth1_access_token = document.getElementById("oauth-1-auth-access-token").value;
        oauth1_token_secret = document.getElementById("oauth-1-auth-token-secret").value;

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

    json_params = JSON.stringify({
        "type": request_type,
        "url": request_url,
        "body": api_test_body,
        "authorization": JSON.stringify(authorization_params),
        "headers": JSON.stringify(headers)
    })

    encrypted_data = auto_api_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/automated-api/test/execute-api/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = auto_api_custom_decrypt(response.Response);
            response = JSON.parse(response);
            last_api_response = {};
            if(response["status"] == 200) {
                content_type = response["api_response"]["headers"]["Content-Type"];
                if(content_type.indexOf("application/json")!=-1){
                    response["api_response"]["body"] = JSON.parse(response["api_response"]["body"]);
                    last_api_response = response["api_response"]["body"];
                    var editor =new JsonEditor('#request-response-container', response);
                    editor.load(response);
                }else{                    
                    document.getElementById("request-response-container").innerHTML = JSON.stringify(response, 4);
                }
                document.getElementById("api-response-container").style.display = "block";
            }else{

            }
        }
    }
    xhttp.send(params);
}

function tag_integrated_api_with_selected_tree(element) {

    request_type = document.getElementById("request-type").value;
    request_url = document.getElementById("request-url").value;
    api_body = document.getElementById("api-body").value;
    // api_test_body = api_body;

    // dynamic_request_table = document.getElementById("api-execution-request-packet-tbody");

    // if (dynamic_request_table != null && dynamic_request_table != undefined) {
    //     tr_children = dynamic_request_table.children;
    //     for(var index=0; index < tr_children.length; index++) {
    //         var variable_key = tr_children[index].children[0].innerHTML;
    //         var variable_test_value = tr_children[index].children[1].innerHTML;

    //         if(variable_test_value.trim() == "") {
    //             alert("Please enter valid test value for "+variable_key+" variable.");
    //             return;
    //         }
    //         api_test_body = api_test_body.replace("{/" + variable_key + "/}", variable_test_value);
    //     }
    // }

    tbody = document.getElementById("header-table-tbody").children;
    headers = {}
    for(var tr_index = 0; tr_index < tbody.length; tr_index++) {
        key = tbody[tr_index].children[0].innerHTML;
        value = tbody[tr_index].children[1].innerHTML;      
        headers[key] = value;
    }

    authorization_type = document.getElementById("request-authorization-type").value;
    authorization_params = {};
    authorization_params["type"] = authorization_type;

    if (authorization_type == "bearer-token") {
        token = document.getElementById("bearer-token-input").value;

        if (token.trim() == "") {
            alert("Please enter valid bearer token for authorization.");
            return;
        }

        authorization_params["params"] = {
            "token": token
        }
    } else if (authorization_type == "basic-auth") {

        basic_auth_username = document.getElementById("basic-auth-username").value;
        basic_auth_password = document.getElementById("basic-auth-password").value;

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
 
        digest_auth_username = document.getElementById("digest-auth-username").value;
        digest_auth_password = document.getElementById("digest-auth-password").value;

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
 
        oauth1_consumer_key = document.getElementById("oauth-1-auth-consumer-key").value;
        oauth1_consuer_secret = document.getElementById("oauth-1-auth-consumer-secret").value;
        oauth1_access_token = document.getElementById("oauth-1-auth-access-token").value;
        oauth1_token_secret = document.getElementById("oauth-1-auth-token-secret").value;

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

    json_params = JSON.stringify({
        "type": request_type,
        "url": request_url,
        "body": api_body,
        "tree_id": get_url_vars()["tree_id"],
        "authorization": JSON.stringify(authorization_params),
        "headers": JSON.stringify(headers)
    })

    encrypted_data = auto_api_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/automated-api/tag-api-tree/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = auto_api_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if(response["status"] == 200){
                window.location.reload();
            }
        }
    }
    xhttp.send(params);    
}


function recursive_json_parser(dict, prefix) {
    for(dict_key in dict){
        if (dict[dict_key] == null) {
            last_master_table_parser_list.push({
                "key": prefix + dict_key,
                "value": dict[dict_key],
                "type": "None"
            })
        }else if(typeof(dict[dict_key]) == "string") {
            last_master_table_parser_list.push({
                "key": prefix + dict_key,
                "value": dict[dict_key],
                "type": "string"
            })
        }else if(typeof(dict[dict_key]) == "number") {
            last_master_table_parser_list.push({
                "key": prefix + dict_key,
                "value": dict[dict_key],
                "type": "number"
            })
        }else if(Array.isArray(dict[dict_key])){

            if (dict[dict_key].length!=0 && typeof(dict[dict_key][0]) == "string") {
                last_master_table_parser_list.push({
                    "key": prefix + dict_key,
                    "value": dict[dict_key],
                    "type": "list-string"
                })
            } else if (dict[dict_key].length!=0 && typeof(dict[dict_key][0]) == "number") {
                last_master_table_parser_list.push({
                    "key": prefix + dict_key,
                    "value": dict[dict_key],
                    "type": "list-number"
                })
            } else if (dict[dict_key].length!=0 && Array.isArray(dict[dict_key][0])) {
                last_master_table_parser_list.push({
                    "key": prefix + dict_key,
                    "value": dict[dict_key],
                    "type": "list-list"
                })
            } else if (dict[dict_key].length!=0) {
                list_dict_key_list = [];
                for(list_dict_key in dict[dict_key][0]) {
                    list_dict_key_list.push(list_dict_key);
                }
                last_master_table_parser_list.push({
                    "key": prefix + dict_key,
                    "value": list_dict_key_list,
                    "type": "list-dict"
                })
            }
        }else{
            prefix += dict_key + "."
            recursive_json_parser(dict[dict_key], prefix);
        }
    }
}

function parse_json_data_and_load_into_table(element) {
    last_master_table_parser_list = [];
    recursive_json_parser(last_api_response, "");
    total_html = "";
    for(var index =0; index < last_master_table_parser_list.length; index++) {
        total_html += '<tr>\
            <td>'+last_master_table_parser_list[index]["key"]+'</td>\
            <td>'+last_master_table_parser_list[index]["value"]+'</td>\
            <td>'+last_master_table_parser_list[index]["type"].toString()+'</td>\
            <td contenteditable="true" id="response_index_'+index+'">'+ last_master_table_parser_list[index]["key"] +'</td>\
        </tr>';
    }
    document.getElementById("parse_json_data_and_load_into_table_container").innerHTML = total_html;
    document.getElementById("parse_json_data_and_load_into_table_container").scrollIntoView();
}

function save_response_alias_for_api_response(element) {
    index = element.getAttribute("index");
    alias = document.getElementById("response_index_"+index);
    if(alias.innerHTML.strip() == ""){
        alert("Please enter valid alias name which can be used in bot response");
        return;
    }   

    alert("Alias saved"); 
}

function fetch_parent_tree_variable_names() {

    json_params = JSON.stringify({
        "tree_id": get_url_vars()["tree_id"]
    });

    encrypted_data = auto_api_custom_encrypt(json_params);
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
            response = JSON.parse(this.responseText);
            response = auto_api_custom_decrypt(response.Response);
            response = JSON.parse(response);
            variable_name_list = "";
            if(response.status == 200) {
                for(var index=0; index < response["parent_variable_names"].length; index++){
                    parent_variable_name = response["parent_variable_names"][index];
                    variable_name_list += '<a href="javascript:void(0)" onclick="set_variable_into_api(this)" variable="'+parent_variable_name+'">@'+parent_variable_name+'</a>';
                }

                if (response["integrated_api"] != null) {
                    document.getElementById("request-type").value = response["integrated_api"]["type"];
                    document.getElementById("request-url").value = response["integrated_api"]["url"];
                    document.getElementById("api-body").value = response["integrated_api"]["body"];                    
                    headers = JSON.parse(response["integrated_api"]["headers"]);
                    authorization = JSON.parse(response["integrated_api"]["authorization"]);
                    for(var header_key in headers){
                        if(header_key=="Content-Type"){
                            document.getElementById("request-header-type").value = headers[header_key];
                            update_tbody_headers(document.getElementById("request-header-type"));
                        }
                    } 

                    authorization_type = "None";
                    if ("type" in authorization) {                    
                        authorization_type = authorization["type"];
                    }
                    document.getElementById("request-authorization-type").value = authorization_type;
                    $("#request-authorization-type").change();

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
                }
            }
            document.getElementById("variable-custom-sidenav-container").innerHTML+=variable_name_list;
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
    var request_body_element = document.getElementById("api-body");
    var new_request_body = active_element.value.substr(0, cursorPosition-1) + variable_name + active_element.value.substr(cursorPosition, ) ;
    active_element.value = new_request_body;
    close_custom_sidenav();
}

function check_for_variable_input_textarea(element){
    body_value = element.value.trim();
    current_active_element = element.id
    cursorPosition = element.selectionStart;
    if(body_value != "" && body_value[cursorPosition-1]=="@") {
        open_custom_sidenav();
    }
}

function load_dummy_message_response_packet() {
    response = {"message": "API Response will be shown here."};
    var editor =new JsonEditor('#request-response-container', response);
    editor.load(response);                        
    document.getElementById("api-response-container").style.display = "block";
}

function generate_automated_api() {
    json_params = JSON.stringify({
        "tree_id": get_url_vars()["tree_id"]
    });

    encrypted_data = auto_api_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/automated-api/generate-automated-code/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = auto_api_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if(response.status == 200){
                window.location = decodeURIComponent(get_url_vars()["previous_location"]);
            }else{
                alert("Unable to generate the automated api code.")
            }
        }
    }
    xhttp.send(params);        
}

window.onload = function(e){
    fetch_parent_tree_variable_names();
    load_dummy_message_response_packet();
}
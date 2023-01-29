(function(exports) {

	function get_csrfmiddlewaretoken(){
	    return document.querySelector("input[name=\"csrfmiddlewaretoken\"]").value;
	}

	function generate_random_string(length) {
	   var result           = '';
	   var characters       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
	   var charactersLength = characters.length;
	   for ( var i = 0; i < length; i++ ) {
	      result += characters.charAt(Math.floor(Math.random() * charactersLength));
	   }
	   return result;
	}

	function custom_encrypt(msg_string) {
	    // msgString is expected to be Utf8 encoded
	    var key = generate_random_string(16);
	    var iv = CryptoJS.lib.WordArray.random(16);
	    var encrypted = CryptoJS.AES.encrypt(msg_string, CryptoJS.enc.Utf8.parse(key), {
	        iv: iv
	    });
	    var return_value = key;
	    return_value += "."+encrypted.toString();
	    return_value += "."+CryptoJS.enc.Base64.stringify(iv);
	    return return_value;
	}

	function custom_decrypt(msg_string){
	    var payload = msg_string.split(".");
	    var key = payload[0];
	    var decrypted_data = payload[1];
	    var decrypted = CryptoJS.AES.decrypt(decrypted_data, CryptoJS.enc.Utf8.parse(key), {
	        iv: CryptoJS.enc.Base64.parse(payload[2])
	    });
	    return decrypted.toString(CryptoJS.enc.Utf8);
	}

	exports.generate_random_string = generate_random_string
	exports.custom_encrypt = custom_encrypt;
	exports.custom_decrypt = custom_decrypt;
	exports.get_csrfmiddlewaretoken = get_csrfmiddlewaretoken;

})(window);

var selected_testcase_excel_base64 = null;
var base64_str = ""

function get_base64_of_selected_document(file) {
    var reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = function() {
        base64_str = reader.result.split(",")[1];
        selected_testcase_excel_base64 = base64_str;
    };
    reader.onerror = function(error) {
    	alert("Unable to parse uploaded excel sheet");
    };
}

function check_client_selected_document(element) {
    var file = element.files[0];
    get_base64_of_selected_document(file);
}

function start_testcase_excel(element) {

    json_string = JSON.stringify({
    	"filename": "hello.csv",
    	"test_bot_id": selected_test_bot_id,
        "base64_file": base64_str
    });

    encrypted_data = custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    processing_started(document.getElementById("uploading-task"));

    var params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/automation/upload-qa-testcase-excel/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if(response.status == 302) {
                alert("Malicious content found in the file. Please try again.")
                return
            }
            if (response.status == 200) {
            	processing_ended(document.getElementById("uploading-task"));
            	start_validating_excel(response.testcase_id);
            } else {

            	alert("Unable to upload the excel sheet. Please try again");
            }
        }
    }
    xhttp.send(params);
}

function start_validating_excel(testcase_id) {

    json_string = JSON.stringify({
        "testcase_id": testcase_id
    });

    encrypted_data = custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    processing_started(document.getElementById("validating-excel-task"));

    var params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/automation/validate-qa-testcase-excel/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                processing_ended(document.getElementById("validating-excel-task"));
                setTimeout(function(e){
                    window.location.reload();
                }, 1000);
            } else {
                alert("Uploaded test case excel sheet is not in proper format. Please check");
            }
        }
    }
    xhttp.send(params); 
}


function load_json_data(qa_testcase_flow_id) {

    json_string = JSON.stringify({
        "qa_testcase_flow_id": qa_testcase_flow_id
    });

    encrypted_data = custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    document.getElementById("flow-output-tbody-content").innerHTML = "Loading...";                
    var params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/automation/get-testcase-flow-output/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            console.log(response);
            tbody_content_element = document.getElementById("flow-output-tbody-content");
            if(response["status"] == 200){
                flow_output = response["flow_output"];
                tbody_html_content = "";
                for(var index=0; index < flow_output.length; index++){

                    recommendations_html = "";
                    recommendations = flow_output[index]["output"]["recommendations"];

                    for(var c_index = 0; c_index < flow_output[index]["output"]["choices"].length; c_index++) {
                        recommendations.push(flow_output[index]["output"]["choices"][c_index]["display"]);
                    }

                    for(var r_index=0; r_index < recommendations.length; r_index++){
                        recommendations_html += '<span class="badge badge-secondary">'+recommendations[r_index]+'</span>';
                    }

                    tbody_html_content += '<tr>\
                        <td scope="row">'+ flow_output[index]["query"] +'</td>\
                        <td scope="row">'+ flow_output[index]["output"]["text_response"] + '</td>\
                        <td scope="row">'+ recommendations_html +'</td>\
                    </tr>';
                }
                tbody_content_element.innerHTML = tbody_html_content;
            }else{
                document.getElementById("flow-output-tbody-content").innerHTML = "Unable to load the flow results";                
            }
        }
    }
    xhttp.send(params);     
}

function test_automation_bot(test_bot_id) {   

    json_string = JSON.stringify({
        "bot_id": test_bot_id
    });

    encrypted_data = custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/automation/test/automation-api/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["query_response"]){
                alert("Automation API is working fine");
            }else{
                alert("Automation API is not working as required");
            }
        }
    }
    xhttp.send(params);     
}
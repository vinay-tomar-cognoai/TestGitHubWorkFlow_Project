(function($) {
    $(function() {
        $('.sidenav').sidenav();
        $('.dropdown-trigger').dropdown({
            constrainWidth: false,
            alignment: 'left'
        });
        $('.collapsible').collapsible();
        $('.modal').modal();
        $('.tabs').tabs();
        $('select').select2({
            width: "100%"
        });
       // $('select').formSelect();
        $('.slider').slider();
        $('.tooltipped').tooltip({
            position: 'top'
        });
        // $('.tooltipped').tooltip();
        $('.datepicker').datepicker({
            format: "dd/mm/yyyy"
        });
        $('.fixed-action-btn').floatingActionButton();
        $('[data-toggle="tooltip"]').tooltip()
        $(".readable-pro-tooltipped").tooltip({
            position: "top"
        });
    }); // end of document ready
})(jQuery); // end of jQuery name space

function getCsrfToken() {
    var CSRF_TOKEN = $('input[name="csrfmiddlewaretoken"]').val();
    return CSRF_TOKEN;
}

function showToast(message, duration) {
    M.toast({
        "html": message
    }, duration);
}

/////////////////////////////// Encryption And Decription //////////////////////////

function CustomEncrypt(msgString, key) {
    // msgString is expected to be Utf8 encoded
    var iv = CryptoJS.lib.WordArray.random(16);
    var encrypted = CryptoJS.AES.encrypt(msgString, CryptoJS.enc.Utf8.parse(key), {
        iv: iv
    });
    var return_value = key;
    return_value += "."+encrypted.toString(); 
    return_value += "."+CryptoJS.enc.Base64.stringify(iv);
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

  utf_data = CryptoJS.enc.Utf8.parse(data);
  encoded_data = utf_data;
  // encoded_data = CryptoJS.enc.Base64.stringify(utf_data);
  random_key = generateRandomString(16);
  // console.log(random_key)
  encrypted_data = CustomEncrypt(encoded_data, random_key);

  return encrypted_data;
}


function custom_decrypt(msg_string){

  var payload = msg_string.split(".");
  var key = payload[0];
  var decrypted_data = payload[1];
  var decrypted = CryptoJS.AES.decrypt(decrypted_data, CryptoJS.enc.Utf8.parse(key), { iv: CryptoJS.enc.Base64.parse(payload[2]) });
  return decrypted.toString(CryptoJS.enc.Utf8);
}


////////////////////////////////////////////////////////////////////////////////////

var SESSION_TIME = 600000; // 10 minutes
var session_timer = "";
var user_last_activity_time_obj = new Date()

// Custom user session

/*
    get_delayed_date_object
    delay current date by delay_period
    var date_obj = new Date();                                      -> current date
    date_obj.setMinutes( date_obj.getMinutes() + delay_period );    -> delay by delay_period
*/

function get_delayed_date_object(delay_period){
    var date_obj = new Date();
    date_obj.setMinutes( date_obj.getMinutes() + delay_period );
    return date_obj
}

/*
    send_session_timeout_request
    is_online_from_this_time                -> delayed by 3 minuits date object
    user_last_activity_time_obj -> user's last activity time
    if(user_last_activity_time_obj > is_online_from_this_time) -> is user active from last 3 minutes
*/

function set_cookie(cookiename, cookievalue, path = "") {
    if (path == "") {
        document.cookie = cookiename + "=" + cookievalue;
    } else {
        document.cookie = cookiename + "=" + cookievalue + ";path=" + path;
    }
}

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

function send_session_timeout_request() {

    if(get_cookie("is_online") == "0"){
        return;
    }

    var is_online_from_this_time = get_delayed_date_object(-3);

    if (user_last_activity_time_obj > is_online_from_this_time) {
        var CSRF_TOKEN = $('input[name="csrfmiddlewaretoken"]').val();
        $.ajax({
            url: "/chat/set-session-time-limit/",
            type: "POST",
            headers: {
                'X-CSRFToken': CSRF_TOKEN
            },
            data: {},
            success: function(response) {
                set_cookie("is_online", "1", "/");
            },
            error: function(xhr, textstatus, errorthrown) {
                set_cookie("is_online", "0", "/");
            }
        });
    }
}

function resetTimer(e) {
    var delay_by_nine_minutes = get_delayed_date_object(-18);
    if(user_last_activity_time_obj < delay_by_nine_minutes){ // if user is active in last minute ( after inactive for 9 minuits )
        user_last_activity_time_obj = new Date()
        send_session_timeout_request();
    }
    user_last_activity_time_obj = new Date();
}

window.onload = function() {
    resetTimer();
    window.onmousemove = resetTimer;
    window.onmousedown = resetTimer;
    window.onclick = resetTimer;
    window.onkeypress = resetTimer;
    window.addEventListener('scroll', resetTimer, true);

    document.addEventListener("visibilitychange", function() {
        if (document.hidden == false) {
            resetTimer();
        }
    }, false);

    setInterval(send_session_timeout_request, 3*60*1000);
    send_session_timeout_request();
}


// $(document).on("click", "#btn-filter-queries", function(e) {
//     var filter = $("#select-tickets").val();
//     search_url = "/tms/?";
//     search = "";
//     if(filter == "1"){
//       search_url += "pending"
//     }
//     else if(filter == "2"){
//       search_url += "reopen"
//     }
//     else if(filter == "3"){
//         search_url += "resolved"
//     }
//     else if(filter == "4"){
//       search_url +="tickets"
//     }
//     else if(filter == "5"){
//       search_url +="unassigned" 
//     }
//     else if(filter == "6"){
//       search_url += "assigned-tickets"
//     }
//     search += window.location.origin + search_url
//     window.location = search;
// });

function select_bot(){
  bot_id = document.getElementById("select-bot-for-category").value;
  search_url = "/tms/ticket-categories/?";
  search = ""
  if(bot_id != ""){
    search_url += "bot_id="+bot_id
  }
  else{
   search_url ="/tms/ticket-categories/"
   search= ""
  }
  search += window.location.origin + search_url
    window.location = search;
}


function select_tickets_option(){
  var filter = $("#select-tickets").val();
  var bot = $("#select-bot-filter").val();
    search_url = "/tms/?";
    search = "";
    if(bot != ""){
      search_url += "bot_id="+bot
      search_url += "&"
    }
    search = "";
    if(filter == "1"){
      search_url += "pending"
    }
    else if(filter == "2"){
      search_url += "reopen"
    }
    else if(filter == "3"){
        search_url += "resolved"
    }
    else if(filter == "4"){
      search_url +="tickets"
    }
    else if(filter == "5"){
      search_url +="unassigned" 
    }
    else if(filter == "6"){
      search_url += "assigned-tickets"
    }
    search += window.location.origin + search_url
    window.location = search;
}


$(document).on("change", ".selected-customer", function(e){
    selected_customer_list = document.getElementsByClassName("selected-customer");
    show_assign_agent_button = false;
    for (var i = 0; i < selected_customer_list.length; i++) {
        id = selected_customer_list[i].id;
        if (document.getElementById(id).checked == true) {
            show_assign_agent_button = true;
            break;
        }
    }
    if (show_assign_agent_button == true) {
        $("#btn-assign-agent").removeAttr('disabled');
        $("#btn-delete-query").removeAttr('disabled');
        $("#btn-assign-agent").removeClass('assign-agent-btn');

    } else {
        $("#btn-assign-agent").attr('disabled','disabled');
        $("#btn-delete-query").attr('disabled','disabled');
        $("#btn-assign-agent").addClass('assign-agent-btn');
    }
});

function get_list_of_selected_customer(){
    selected_customer_list = document.getElementsByClassName("selected-customer");
    customer_id_list = [];
    for (var i = 0; i < selected_customer_list.length; i++) {
        id = selected_customer_list[i].id;
        if(document.getElementById(id).checked){
            id_item_list = id.split("-");
            customer_id_list.push(id_item_list[id_item_list.length-1]);            
        }
    }        
    return customer_id_list;
}
function assign_agent(element){

    agent_id = document.getElementById("assign-agent-customer").value

    if(agent_id == ""){
      showToast("Kindly assign an agent to the ticket.", 2000);
      return;
    }
    selected_customer_list = get_list_of_selected_customer()

    // console.log(agent_id)
    json_string = JSON.stringify({
        agent_id:agent_id,
        selected_customer_list:selected_customer_list
    });

    json_string = EncryptVariable(json_string);

    var CSRF_TOKEN = getCsrfToken();
    element.innerHTML = "Assigning...";

    $.ajax({
       url: '/tms/assign-agent/',
       type: 'POST',
       headers: {
           'X-CSRFToken': CSRF_TOKEN
       },
       data: {
           data: json_string
       },
       success: function(response) {
            response = custom_decrypt(response["response"])
            response = JSON.parse(response);
            if (response["status_code"] == 200) {
               showToast("Assigned Succesfully", 2000);
               window.location.reload();
            }
            else{
               showToast("Unable to save due to some internal server error. Kindly report the same.", 2000);
               console.log("Please report this. ", response["status_message"]);            
            }
            element.innerHTML = "Assign Agent";
       },
       error: function(xhr, textstatus, errorthrown){
           console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
            element.innerHTML = "Assign Agent";
       }
   });
}

function assign_agent_particular(customer_id)
{
  agent_id = document.getElementById("assign-agent-customer-"+customer_id).value
  if(agent_id == ""){
    showToast("Kindly assign an agent to the ticket.", 2000);
    return;
  }
    // console.log(agent_id)
    json_string = JSON.stringify({
        agent_id:agent_id,
        selected_customer_list:customer_id
    });

    json_string = EncryptVariable(json_string);

    var CSRF_TOKEN = getCsrfToken();

    $.ajax({
       url: '/tms/assign-agent/',
       type: 'POST',
       headers: {
           'X-CSRFToken': CSRF_TOKEN
       },
       data: {
           data: json_string
       },
       success: function(response) {
            response = custom_decrypt(response["response"])
            response = JSON.parse(response);
            if (response["status_code"] == 200) {
               showToast("Assigned Succesfully", 2000);
               window.location.reload();
            }
            else{
               showToast("Unable to save due to some internal server error. Kindly report the same.", 2000);
               console.log("Please report this. ", response["status_message"]);            
            }
       },
       error: function(xhr, textstatus, errorthrown){
           console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
       }
   });
}

function assign_self_agent(agent_id){
    selected_customer_list = get_list_of_selected_customer()
    json_string = JSON.stringify({
        agent_id:agent_id,
        selected_customer_list:selected_customer_list
    });

    json_string = EncryptVariable(json_string);

    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
       url: '/tms/assign-agent/',
       type: 'POST',
       headers: {
           'X-CSRFToken': CSRF_TOKEN
       },
       data: {
           data: json_string
       },
       success: function(response) {
          response = custom_decrypt(response["response"])
          response = JSON.parse(response);
          if (response["status_code"] == 200) {
             showToast("Assigned Succesfully", 2000);
             window.location.reload();
          }
          else{
             showToast("Unable to assign due to some internal server error. Kindly report the same", 2000);
             console.log("Please report this. ", response["status_message"]);            
          }
          element.innerHTML = "Assign Agent";
       },
       error: function(xhr, textstatus, errorthrown){
           console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
            element.innerHTML = "Assign Agent";
       }
   });
}

function assign_self_agent_particular(agent_id, customer_id){
    json_string = JSON.stringify({
        agent_id:agent_id,
        selected_customer_list:customer_id
    });

    json_string = EncryptVariable(json_string);

    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
       url: '/tms/assign-agent/',
       type: 'POST',
       headers: {
           'X-CSRFToken': CSRF_TOKEN
       },
       data: {
           data: json_string
       },
       success: function(response) {
          response = custom_decrypt(response["response"])
          response = JSON.parse(response);
          if (response["status_code"] == 200) {
             showToast("Assigned Succesfully", 2000);
             window.location.reload();
          }
          else{
             showToast("Unable to assign due to some internal server error. Kindly report the same", 2000);
             console.log("Please report this. ", response["status_message"]);            
          }
          element.innerHTML = "Assign Agent";
       },
       error: function(xhr, textstatus, errorthrown){
           console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
            element.innerHTML = "Assign Agent";
       }
   });
}

function resolve_issue(customer_id){
    // console.log(customer_id);
    agent_comment = document.getElementById("agent-comments-issue-" + customer_id).value;
    if(agent_comment == ""){
      showToast("Please enter your comment.");
      return;
    }

    json_string = JSON.stringify({
        agent_comment:agent_comment,
        customer_id:customer_id
    });

    json_string = EncryptVariable(json_string);

    var CSRF_TOKEN = getCsrfToken();

    $.ajax({
       url: '/tms/issue-resolved/',
       type: 'POST',
       headers: {
           'X-CSRFToken': CSRF_TOKEN
       },
       data: {
           data: json_string
       },
       success: function(response) {
          response = custom_decrypt(response["response"])
          response = JSON.parse(response);
          if (response["status_code"] == 200 && response["another_agent"] == false) {
             showToast("Resolved Succesfully", 2000);
             window.location.reload();
          }
          else if(response["another_agent"] == true){
          showToast("You are not allowed to resolve this issue.", 2000);
          }
          else{
             showToast("Unable to resolved due to some internal server error. Kindly report the same", 2000);
             console.log("Please report this. ", response["status_message"]);            
          }
       },
       error: function(xhr, textstatus, errorthrown){
           console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
       }
   });
}

function add_agent_comment(customer_id){
    agent_comment = document.getElementById("agent-comments-" + customer_id).value;
    if(agent_comment == ""){
      showToast("Please enter your comment.");
      return;
    }

    json_string = JSON.stringify({
        agent_comment:agent_comment,
        customer_id:customer_id
    });
    json_string = EncryptVariable(json_string);

    var CSRF_TOKEN = getCsrfToken();

    $.ajax({
       url: '/tms/add-agent-comment/',
       type: 'POST',
       headers: {
           'X-CSRFToken': CSRF_TOKEN
       },
       data: {
           data: json_string
       },
       success: function(response) {
        response = custom_decrypt(response["response"])
          response = JSON.parse(response);
           if (response["status_code"] == 200 && response["another_agent"] == false) {
               showToast("Comment Added Succesfully", 2000);
               window.location.reload();
           }
           else if(response["another_agent"] == true){
              showToast("You are not allowed to add comment in this issue.")
           }
           else{
               showToast("Unable to add comment due to some internal server error. Kindly report the same", 2000);
               console.log("Please report this. ", response["status_message"]);            
           }
       },
       error: function(xhr, textstatus, errorthrown){
           console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
       }
   });
}

function add_agent_comment_reopen(customer_id){
    agent_comment = document.getElementById("reopen-description-" + customer_id).value;
    if(agent_comment == ""){
      showToast("Please enter your comment.");
      return;
    }

    json_string = JSON.stringify({
        agent_comment:agent_comment,
        customer_id:customer_id
    });
    json_string = EncryptVariable(json_string);

    var CSRF_TOKEN = getCsrfToken();

    $.ajax({
       url: '/tms/add-agent-comment/',
       type: 'POST',
       headers: {
           'X-CSRFToken': CSRF_TOKEN
       },
       data: {
           data: json_string
       },
       success: function(response) {
          response = custom_decrypt(response["response"])
          response = JSON.parse(response);
           if (response["status_code"] == 200 && response["another_agent"] == false) {
               showToast("Comment Added Succesfully", 2000);
               window.location.reload();
           }
           else if(response["another_agent"] == true){
              showToast("You are not allowed to add comment in this issue.")
           }
           else{
               showToast("Unable to add comment due to some internal server error. Kindly report the same", 2000);
               console.log("Please report this. ", response["status_message"]);            
           }
       },
       error: function(xhr, textstatus, errorthrown){
           console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
       }
   });
}


// function create_issue(element){
//     name = document.getElementById("new-issue-name").value;
//     if(name == ""){
//       showToast("Please enter customer's name.");
//       return;
//     }
//     if(!/^[a-zA-Z]/.test(name)){
//       showToast("Please enter a valid name.");
//       return;
//     }
//     phone_no = document.getElementById("new-issue-phone").value;
//     if(phone_no == ""){
//       showToast("Please enter customer's phone no.");
//       return;
//     }
//     if(phone_no.length != 10 || !/^\d{10}$/.test(phone_no)){
//       showToast("Please enter a valid phone no.");
//       return;
//     }
//     email = document.getElementById("new-issue-email").value;
//     if(email == ""){
//       showToast("Please enter customer's email.");
//       return;
//     }
//     if(!/^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/.test(email)){
//      showToast("Please enter a valid email.");
//       return; 
//     }
//     issue = document.getElementById("new-issue-issue").value;
//     if(issue == ""){
//       showToast("Please describe the issue.");
//       return;
//     }
//     json_string = JSON.stringify({
//         name:name,
//         phone_no:phone_no,
//         email:email,
//         issue:issue
//     });

//     var CSRF_TOKEN = getCsrfToken();
//     $.ajax({
//        url: '/tms/create-issue/',
//        type: 'POST',
//        headers: {
//            'X-CSRFToken': CSRF_TOKEN
//        },
//        data: {
//            data: json_string
//        },
//        success: function(response) {
//            if (response["status_code"] == 200) {
//                showToast("Created Succesfully", 2000);
//                window.location.reload();
//            }
//            else{
//                showToast("Unable to create new issue due to some internal server error. Kindly report the same", 2000);
//                console.log("Please report this. ", response["status_message"]);            
//            }
//        },
//        error: function(xhr, textstatus, errorthrown){
//            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
//        }
//    });
// }

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
    if(!name.replace(/\s/g, '').length){
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
    email = document.getElementById("new-issue-email").value;
    if(email == ""){
      showToast("Please enter customer's email.");
      return;
    }
    if(!/^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/.test(email)){
     showToast("Please enter a valid email.");
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
    // bot_id = document.getElementById("ticket-bot").value;
    // if(bot_id == ""){
    //   showToast("Please select a bot.")
    //   return ;
    // }
    category = document.getElementById("ticket-category").value;
    if(category == ""){
      showToast("Please select the category.");
      return;
    }
    json_string = JSON.stringify({
        name:name,
        phone_no:phone_no,
        email:email,
        issue:issue,
        priority:priority,
        category:category,
        "channel":"Web"
        // bot_id: ""
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
          response = custom_decrypt(response["response"])
          response = JSON.parse(response);
           if (response["status_code"] == 200) {
               showToast("Created Succesfully", 2000);
               window.location.reload();
           }else if(response["status_code"] == 305){
              showToast("Ticket is created successfully but today office is holiday so no agent will able to resolve it.", 2000);
               window.location.reload();
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

function create_agent(element){
    // first_name = document.getElementById("new-agent-first-name").value;
    // if(first_name == ""){
    //   showToast("Please enter first name.");
    //   return;
    // }
    // if(!/^[a-zA-Z ]*$/.test(first_name)){
    //   showToast("Please enter a valid first name.");
    //   return;
    // }
    // if(!first_name.replace(/\s/g, '').length){
    //   showToast("Please enter a valid name.");
    //   return;
    // }
    // last_name = document.getElementById("new-agent-last-name").value;
    // if(last_name == ""){
    //   showToast("Please enter last name.");
    //   return;
    // }
    // if(!/^[a-zA-Z ]*$/.test(last_name)){
    //   showToast("Please enter a valid last name.");
    //   return;
    // }
    // if(!last_name.replace(/\s/g, '').length){
    //   showToast("Please enter a valid name.");
    //   return;
    // }
    // phone_number = document.getElementById("new-agent-phone").value;
    // if(phone_number == ""){
    //   showToast("Please enter phone number.");
    //   return;
    // }
    // if(phone_number.length != 10 || !/^\d{10}$/.test(phone_number)){
    //   showToast("Please enter a valid phone no.");
    //   return;
    // }
    
    email = document.getElementById("new-agent-email").value;
    if(email == ""){
      showToast("Please enter email.");
      return;
    }
    if(!/^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/.test(email)){
     showToast("Please enter a valid email.");
      return; 
    }
    username = document.getElementById("new-agent-username").value;
    if(username == ""){
      showToast("Please enter username.");
      return;
    }
    status = document.getElementById("staus-agent").value;
    if(status == ""){
      showToast("Please Select Type of User");
      return;
    }
    password = document.getElementById("user-password").value;
    if(password == ""){

    }
    if (password.trim() == "") {
        M.toast({
            "html": "Please enter a password"
        }, 2000);
        return;
    }
    password_regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,32}$/

    if (password_regex.test(password) == false) {
        // document.getElementById("password_check_sandbox_user").style.display = "block"

        one_upercase_and_lowercase_regex = /(?=.*[a-z])(?=.*[A-Z])/
        if (one_upercase_and_lowercase_regex.test(password) == false) {
            M.toast({
                "html": "Password must contain one upper case letter and one lower case letter"
            }, 2000);
            document.getElementById("tms-password-cap-small-check").style.display = "list-item";
        } else {

            document.getElementById("tms-password-cap-small-check").style.display = "none";
        }

        atleast_one_no_regex = /(?=.*\d)/
        if (atleast_one_no_regex.test(password) == false) {
            M.toast({
                "html": "Password must contain one number"
            }, 2000);
            document.getElementById("tms-password-number-check").style.display = "list-item";
        } else {

            document.getElementById("tms-password-number-check").style.display = "none";
        }

        special_char_regex = /(?=.*[@$!%*?&])/
        if (special_char_regex.test(password) == false) {
            M.toast({
                "html": "Password must contain one special character"
            }, 2000);
            document.getElementById("tms-password-special-char-check").style.display = "list-item";
        } else {

            document.getElementById("tms-password-special-char-check").style.display = "none";
        }

        if (password.length < 8 || password.length > 32) {
            M.toast({
                "html": "Password length must be between 8-32 characters"
            }, 2000);
            document.getElementById("tms-password-length-check").style.display = "list-item";
        } else {

            document.getElementById("tms-password-length-check").style.display = "none";
        }

        return;
    }

    if (password.includes(username)) {
        M.toast({
            "html": "Password must not contain user name"
        }, 2000);

        return;
    }

    category_pk = parseInt(document.getElementById("tms-ticket-category").value)
    if(isNaN(category_pk)){
        M.toast({
            "html": "Please Select a Valid Category "
        }, 2000);

        return;
    }
    json_string = JSON.stringify({
        // first_name:first_name,
        // last_name:last_name,
        // phone_number:phone_number,
        username:username,
        email:email,
        status:status,
        password:password,
        category_pk:category_pk,
        "channel":"Web"
    });
    json_string = EncryptVariable(json_string);

    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
       url: '/tms/create-new-agent/',
       type: 'POST',
       headers: {
           'X-CSRFToken': CSRF_TOKEN
       },
       data: {
           data: json_string
       },
       success: function(response) {
          response = custom_decrypt(response["response"])
          response = JSON.parse(response);
           if (response["status_code"] == 200) {
              // console.log(response)
              if(response["is_user_exists"] == true){
                showToast("Username already taken.", 2000);
                return;
              }
              else if(response["is_user_archived"] == true){
                showToast("User with this username is in archived list. Please, try different username.", 3000);
                return;
              }
              else{
               showToast("New Agent created Succesfully", 2000);
               window.location.reload();
              }
           }
           else{
               showToast("Unable to create new agent due to some internal server error. Kindly report the same", 2000);
               console.log("Please report this. ", response["status_message"]);            
           }
       },
       error: function(xhr, textstatus, errorthrown){
           console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
       }
   });
}

if(window.location.pathname=="/tms/customer-ticket-history/"){
  $(document).ready(function(){
      var table = $('#table-customer-ticket-history').DataTable({"ordering": false});
      setTimeout(function(){
          window.location.reload();
      }, 300000);
  });
}

if(window.location.pathname=="/tms/customer-meeting-history/"){
  $(document).ready(function(){
      var table = $('#table-customer-meeting-history').DataTable({"ordering": false});
      setTimeout(function(){
          window.location.reload();
      }, 300000);
  });
}
if(window.location.pathname=="/tms/ticket-categories/"){
  $(document).ready(function(){
      var table = $('#table-category-details').DataTable({"ordering": false});
      setTimeout(function(){
          window.location.reload();
      }, 300000);
  });
}
if(window.location.pathname=="/tms/manage-agents/"){
  $(document).ready(function(){
      var table = $('#table-agent-details').DataTable(
          {"ordering": false,
          initComplete: function() {
            $(this.api().table().container()).find('input').parent().wrap('<form>').parent().attr('autocomplete', 'off');
        }
      });
      
  });
}
if(window.location.pathname=="/tms/history/"){
  $(document).ready(function(){
      var table = $('#table-customer-history').DataTable({"ordering": false});
  });
}
if(window.location.pathname=="/tms/meetings/"){
  $(document).ready(function(){
      var table = $('#table-user-meetings').DataTable({"ordering": false});
  });
}
if(window.location.pathname=="/tms/calendar/"){
  $(document).ready(function(){
      var table = $('#table-working-details').DataTable({"ordering": false,iDisplayLength: -1});
  });
  $(document).ready(function(){
      var table = $('#table-leave-details').DataTable({"ordering": false,iDisplayLength: -1});
  });

}

function reopen_ticket(customer_id){
    reopen_description = document.getElementById("reopen-description-resolved-" + customer_id).value;
    if(reopen_description == ""){
      showToast("Please enter the description.");
      return;
    }
    json_string = JSON.stringify({
        reopen_description:reopen_description,
        customer_id:customer_id,
    });
    json_string = EncryptVariable(json_string);

    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
       url: '/tms/reopen-ticket/',
       type: 'POST',
       headers: {
           'X-CSRFToken': CSRF_TOKEN
       },
       data: {
           data: json_string
       },
       success: function(response) {
          response = custom_decrypt(response["response"])
          response = JSON.parse(response);
           if (response["status_code"] == 200 && response["another_agent"] == false) {
               showToast("Reopened Succesfully", 2000);
               window.location.reload();
           }
           else if( response["another_agent"] == true){
              showToast("You are not allowed to reopen this issue.", 2000);
           }
           else{
               showToast("Unable to reopen due to some internal server error. Kindly report the same", 2000);
               console.log("Please report this. ", response["status_message"]);            
           }
       },
       error: function(xhr, textstatus, errorthrown){
           console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
       }
   });
}
$(document).on("change", "#global-selected-customer", function(e){
    is_checked = document.getElementById("global-selected-customer").checked;
    selection_check = false
    selected_customers_list = document.getElementsByClassName("selected-customer");
    for (var i = 0; i < selected_customers_list.length; i++) {
        id = selected_customers_list[i].id;
        document.getElementById(id).checked = is_checked;
        selection_check = true
    }
    $(".global-selected-customer").change();
    if(selection_check == true && is_checked == true){
    $("#btn-assign-agent").removeAttr('disabled');
    $("#btn-delete-query").removeAttr('disabled');
  }
  else {
        $("#btn-assign-agent").attr('disabled','disabled');
        $("#btn-delete-query").attr('disabled','disabled');
    }

});
function delete_customer_query(){
    selected_customer_list = get_list_of_selected_customer();
    json_string = JSON.stringify({
        selected_customer_list:selected_customer_list,
    });
    json_string = EncryptVariable(json_string);

    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
       url: '/tms/delete-customer-query/',
       type: 'POST',
       headers: {
           'X-CSRFToken': CSRF_TOKEN
       },
       data: {
           data: json_string
       },
       success: function(response) {
          response = custom_decrypt(response["response"])
          response = JSON.parse(response);
           if (response["status_code"] == 200) {
               showToast("Deleted Succesfully", 2000);
               window.location.reload();
           }
           else{
               showToast("Unable to delete due to some internal server error. Kindly report the same", 2000);
               console.log("Please report this. ", response["status_message"]);            
           }
       },
       error: function(xhr, textstatus, errorthrown){
           console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
       }
   });
}

function change_password(agent_id){
  // old_password = document.getElementById("old-password-"+agent_id).value
  new_password = document.getElementById("new-password-"+agent_id).value
  renew_password = document.getElementById("re-new-password-"+agent_id).value
  if(new_password == "" || new_password == undefined || new_password == null){
    showToast("Please enter your new password.")
    return;
  }
  if(renew_password == "" || renew_password == undefined || renew_password == null){
    showToast("Please re-enter your new password.")
    return;
  }
  if(new_password != renew_password){
    showToast("New passwords should be same in both the field.",2000);
    return;
  }

    json_string = JSON.stringify({
        new_password:new_password,
        agent_id:agent_id
    });

    json_string = EncryptVariable(json_string);

    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
       url: '/tms/change-password/',
       type: 'POST',
       headers: {
           'X-CSRFToken': CSRF_TOKEN
       },
       data: {
           data: json_string
       },
       success: function(response) {
          response = custom_decrypt(response["response"])
          response = JSON.parse(response);
           if (response["status_code"] == 200) {
               showToast("Password Changed Succesfully", 2000);
               window.location = window.location.origin;
           }
           else{
               showToast("Unable to change password due to some internal server error. Kindly report the same", 2000);
               console.log("Please report this. ", response["status_message"]);            
           }
       },
       error: function(xhr, textstatus, errorthrown){
           console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
       }
   });
}

function delete_agent(agent_id){
    json_string = JSON.stringify({
        agent_id:agent_id,
    });
    json_string = EncryptVariable(json_string);

    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
       url: '/tms/delete-agent/',
       type: 'POST',
       headers: {
           'X-CSRFToken': CSRF_TOKEN
       },
       data: {
           data: json_string
       },
       success: function(response) {
          response = custom_decrypt(response["response"])
          response = JSON.parse(response);
           if (response["status_code"] == 200) {
               showToast("Deleted Succesfully", 2000);
               window.location.reload();
           }
           else{
               showToast("Unable to delete due to some internal server error. Kindly report the same", 2000);
               console.log("Please report this. ", response["status_message"]);            
           }
       },
       error: function(xhr, textstatus, errorthrown){
           console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
       }
   });
}

function save_prefrences(agent_id){
  var selected_bot = $('#multiple-bot-select-'+agent_id).val();
  // var selected_category = $('#multiple-category-select-'+agent_id).val();
  json_string = JSON.stringify({
        agent_id:agent_id,
        selected_bot:selected_bot,
        // selected_category:selected_category,
    });
  json_string = EncryptVariable(json_string);

    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
       url: '/tms/save-agent-prefrences/',
       type: 'POST',
       headers: {
           'X-CSRFToken': CSRF_TOKEN
       },
       data: {
           data: json_string
       },
       success: function(response) {
          response = custom_decrypt(response["response"])
          response = JSON.parse(response);
           if (response["status_code"] == 200) {
               showToast("Saved Succesfully", 2000);
               window.location.reload();
           }
           else{
               showToast("Unable to save due to some internal server error. Kindly report the same", 2000);
               console.log("Please report this. ", response["status_message"]);            
           }
       },
       error: function(xhr, textstatus, errorthrown){
           console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
       }
   });
}

function meeting_scheduled(customer_id){
    // console.log(customer_id);
    agent_comment = document.getElementById("agent-comments-" + customer_id).value;
    if(agent_comment == ""){
      showToast("Please enter your comment.");
      return;
    }

    json_string = JSON.stringify({
        agent_comment:agent_comment,
        customer_id:customer_id
    });
    json_string = EncryptVariable(json_string);

    var CSRF_TOKEN = getCsrfToken();

    $.ajax({
       url: '/tms/meeting-scheduled/',
       type: 'POST',
       headers: {
           'X-CSRFToken': CSRF_TOKEN
       },
       data: {
           data: json_string
       },
       success: function(response) {
          response = custom_decrypt(response["response"])
          response = JSON.parse(response);
           if (response["status_code"] == 200) {
               showToast("Scheduled Succesfully", 2000);
               window.location.reload();
           }
           else{
               showToast("Unable to submit due to some internal server error. Kindly report the same", 2000);
               console.log("Please report this. ", response["status_message"]);            
           }
       },
       error: function(xhr, textstatus, errorthrown){
           console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
       }
   });
}
function delete_customer_meeting(customer_id){
    json_string = JSON.stringify({
        customer_id:customer_id,
    });
    json_string = EncryptVariable(json_string);

    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
       url: '/tms/delete-customer-meeting/',
       type: 'POST',
       headers: {
           'X-CSRFToken': CSRF_TOKEN
       },
       data: {
           data: json_string
       },
       success: function(response) {
          response = custom_decrypt(response["response"])
          response = JSON.parse(response);
           if (response["status_code"] == 200) {
               showToast("Deleted Succesfully", 2000);
               window.location.reload();
           }
           else{
               showToast("Unable to delete due to some internal server error. Kindly report the same", 2000);
               console.log("Please report this. ", response["status_message"]);            
           }
       },
       error: function(xhr, textstatus, errorthrown){
           console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
       }
   });
}

function assign_agent_meeting(element){

    agent_id = document.getElementById("assign-agent-user").value
    selected_customer_list = get_list_of_selected_customer()

    // console.log(selected_customer_list)
    json_string = JSON.stringify({
        agent_id:agent_id,
        selected_customer_list:selected_customer_list
    });
    json_string = EncryptVariable(json_string);

    var CSRF_TOKEN = getCsrfToken();
    element.innerHTML = "Assigning...";
    $.ajax({
       url: '/tms/assign-agent-meeting/',
       type: 'POST',
       headers: {
           'X-CSRFToken': CSRF_TOKEN
       },
       data: {
           data: json_string
       },
       success: function(response) {
          response = custom_decrypt(response["response"])
          response = JSON.parse(response);
           if (response["status_code"] == 200) {
               showToast("Assigned Succesfully", 2000);
               window.location.reload();
           }
           else{
               showToast("Unable to assign due to some internal server error. Kindly report the same", 2000);
               console.log("Please report this. ", response["status_message"]);            
           }
            element.innerHTML = "Assign Agent";
       },
       error: function(xhr, textstatus, errorthrown){
           console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
            element.innerHTML = "Assign Agent";
       }
   });
}

function assign_agent_meeting_particular(customer_id){

    agent_id = document.getElementById("assign-agent-user-"+customer_id).value
    json_string = JSON.stringify({
        agent_id:agent_id,
        selected_customer_list:customer_id
    });
    json_string = EncryptVariable(json_string);

    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
       url: '/tms/assign-agent-meeting/',
       type: 'POST',
       headers: {
           'X-CSRFToken': CSRF_TOKEN
       },
       data: {
           data: json_string
       },
       success: function(response) {
          response = custom_decrypt(response["response"])
          response = JSON.parse(response);
           if (response["status_code"] == 200) {
               showToast("Assigned Succesfully", 2000);
               window.location.reload();
           }
           else{
               showToast("Unable to assign due to some internal server error. Kindly report the same", 2000);
               console.log("Please report this. ", response["status_message"]);            
           }
       },
       error: function(xhr, textstatus, errorthrown){
           console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
       }
   });
}

// function assign_meeting_self_agent(agent_id){
//     selected_customer_list = get_list_of_selected_customer()
//     json_string = JSON.stringify({
//         agent_id:agent_id,
//         selected_customer_list:selected_customer_list
//     });
//     json_string = EncryptVariable(json_string);

//     var CSRF_TOKEN = getCsrfToken();
//     $.ajax({
//        url: '/tms/assign-meeting-by-agent/',
//        type: 'POST',
//        headers: {
//            'X-CSRFToken': CSRF_TOKEN
//        },
//        data: {
//            data: json_string
//        },
//        success: function(response) {
//           response = custom_decrypt(response["response"])
//           response = JSON.parse(response);
//            if (response["status_code"] == 200) {
//                showToast("Assigned Succesfully", 2000);
//                window.location.reload();
//            }
//            else{
//                showToast("Unable to assign due to some internal server error. Kindly report the same", 2000);
//                console.log("Please report this. ", response["status_message"]);            
//            }
//             element.innerHTML = "Assign Agent";
//        },
//        error: function(xhr, textstatus, errorthrown){
//            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
//             element.innerHTML = "Assign Agent";
//        }
//    });
// }

function assign_meeting_self_agent_particular(agent_id, customer_id){
    json_string = JSON.stringify({
        agent_id:agent_id,
        selected_customer_list:customer_id
    });
    json_string = EncryptVariable(json_string);

    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
       url: '/tms/assign-meeting-by-agent/',
       type: 'POST',
       headers: {
           'X-CSRFToken': CSRF_TOKEN
       },
       data: {
           data: json_string
       },
       success: function(response) {
          response = custom_decrypt(response["response"])
          response = JSON.parse(response);
           if (response["status_code"] == 200) {
               showToast("Assigned Succesfully", 2000);
               window.location.reload();
           }
           else{
               showToast("Unable to assign due to some internal server error. Kindly report the same", 2000);
               console.log("Please report this. ", response["status_message"]);            
           }
            element.innerHTML = "Assign Agent";
       },
       error: function(xhr, textstatus, errorthrown){
           console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
            element.innerHTML = "Assign Agent";
       }
   });
}

// $(document).on("click", "#btn-filter-history", function(e) {
//     var filter = $("#select-history").val();
//     search_url = "/tms/history?";
//     search = "";
//     if(filter == "2"){
//       search_url += "meetings"
//     }
//     else if(filter == "3"){
//       search_url += "tickets"
//     }
//     search += window.location.origin + search_url
//     window.location = search;
// });

function select_history_option(){
    var filter = $("#select-history").val();
    search_url = "/tms/history?";
    search = "";
    if(filter == "2"){
      search_url += "meetings"
    }
    else if(filter == "3"){
      search_url += "tickets"
    }
    search += window.location.origin + search_url
    window.location = search;
}

// $(document).on("click", "#btn-filter-meetings", function(e) {
//     var filter = $("#select-meetings").val();
//     search_url = "/tms/meetings?";
//     search = "";
//     if(filter == "1"){
//       search_url += "pending-meetings"
//     }
//     else if(filter == "2"){
//       search_url += "completed-meetings"
//     }
//     else if(filter == "3"){
//       search_url += "unassigned-meetings"
//     }
//     search += window.location.origin + search_url
//     window.location = search;
// });

function select_meetings_option(){
    var filter = $("#select-meetings").val();
    search_url = "/tms/meetings?";
    search = "";
    if(filter == "1"){
      search_url += "pending-meetings"
    }
    else if(filter == "2"){
      search_url += "completed-meetings"
    }
    else if(filter == "3"){
      search_url += "unassigned-meetings"
    }
    else if(filter == "5"){
      search_url +="meetings"
    }
    else if(filter == "4"){
      search_url += "assigned-meetings"
    }

    search += window.location.origin + search_url
    window.location = search;
}

function change_priority(customer_id){
    priority = document.getElementById("change-priority-"+customer_id).value;
    if(priority == ""){
      showToast("Select a priority.", 2000);
      return;
    }
    json_string = JSON.stringify({
        customer_id:customer_id,
        priority:priority
    });
    json_string = EncryptVariable(json_string);

    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
       url: '/tms/change-ticket-priority/',
       type: 'POST',
       headers: {
           'X-CSRFToken': CSRF_TOKEN
       },
       data: {
           data: json_string
       },
       success: function(response) {
          response = custom_decrypt(response["response"])
          response = JSON.parse(response);
           if (response["status_code"] == 200) {
               showToast("Priority Changed Succesfully", 2000);
               window.location.reload();
           }
           else{
               showToast("Unable to change priority due to some internal server error. Kindly report the same", 2000);
               console.log("Please report this. ", response["status_message"]);            
           }
       },
       error: function(xhr, textstatus, errorthrown){
           console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
       }
   });
}

function change_category(customer_id){
    category = document.getElementById("change-category-ticket-"+customer_id).value;
    if(category == ""){
      showToast("Select a category.", 2000);
    }
    json_string = JSON.stringify({
        customer_id:customer_id,
        category:category
    });
    json_string = EncryptVariable(json_string);

    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
       url: '/tms/change-ticket-category/',
       type: 'POST',
       headers: {
           'X-CSRFToken': CSRF_TOKEN
       },
       data: {
           data: json_string
       },
       success: function(response) {
          response = custom_decrypt(response["response"])
          response = JSON.parse(response);
           if (response["status_code"] == 200) {
               showToast("Category Changed Succesfully", 2000);
               window.location.reload();
           }
           else{
               showToast("Unable to change category due to some internal server error. Kindly report the same", 2000);
               console.log("Please report this. ", response["status_message"]);            
           }
       },
       error: function(xhr, textstatus, errorthrown){
           console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
       }
   });
}


// var input = document.getElementById("add-ticket-category-days");
// input.addEventListener("keyup", function(event) {
//   if (event.keyCode === 13) {
//     event.preventDefault();
//     document.getElementById("add-this-ticket-category").click();
//   }
// });

// var input = document.getElementById("add-ticket-category");
// input.addEventListener("keyup", function(event) {
//   if (event.keyCode === 13) {
//     event.preventDefault();
//     document.getElementById("add-this-ticket-category").click();
//   }
// });

function add_category(bot_id){
    // bot_id = document.getElementById("select-bot-for-category").value;
    if(bot_id == ""){
        showToast("Please select a bot.", 2000);
        return;
      }

    category = document.getElementById("add-ticket-category").value.toUpperCase();
    if(category == ""){
      showToast("Please enter a category.", 2000);
      return;
    }
    ticket_period = document.getElementById("add-ticket-category-days").value;
    if(ticket_period == ""){
      showToast("Please enter number of days.", 2000);
      return;
    }
    if(!/^[0-9]*$/.test(ticket_period)){
      showToast("Please enter valid number of days.", 2000);
      return;
    }
    json_string = JSON.stringify({
        category:category,
        ticket_period:ticket_period,
        bot_id:bot_id,
    });
    json_string = EncryptVariable(json_string);

    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
       url: '/tms/add-ticket-category/',
       type: 'POST',
       headers: {
           'X-CSRFToken': CSRF_TOKEN
       },
       data: {
           data: json_string
       },
       success: function(response) {
          response = custom_decrypt(response["response"])
          response = JSON.parse(response);
           if (response["status_code"] == 200 && response["is_category_exists"] == false) {
               showToast("Ticket Category Added Succesfully", 2000);
               window.location.reload();
           }
           else if(response["is_category_exists"] == true){
              showToast("Category already exists.", 2000);
           }
           else{
               showToast("Unable to add ticket category due to some internal server error. Kindly report the same", 2000);
               console.log("Please report this. ", response["status_message"]);            
           }
       },
       error: function(xhr, textstatus, errorthrown){
           console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
       }
   });
}

function save_category(category_id, bot_id){
    var new_category = ""
    new_category = document.getElementById("edit-ticket-category-name-"+category_id).value.toUpperCase();
    if(new_category == ""){
      showToast("Please enter a category.", 2000);
      return;
    }
    var new_ticket_period = ""
    new_ticket_period = document.getElementById("edit-ticket-category-days-"+category_id).value;
    if(new_ticket_period == ""){
      showToast("Please enter number of days.", 2000);
      return;
    }
    if(!/^[0-9]*$/.test(new_ticket_period)){
      showToast("Please enter valid number of days.", 2000);
      return;
    }
    json_string = JSON.stringify({
        category_id:category_id,
        bot_id:bot_id,
        new_category:new_category,
        new_ticket_period:new_ticket_period,
    });
    json_string = EncryptVariable(json_string);

    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
       url: '/tms/edit-ticket-category/',
       type: 'POST',
       headers: {
           'X-CSRFToken': CSRF_TOKEN
       },
       data: {
           data: json_string
       },
       success: function(response) {
          response = custom_decrypt(response["response"])
          response = JSON.parse(response);
           if (response["status_code"] == 200 && response["is_category_exists"] == false) {
               showToast("Ticket Category Edited Succesfully", 2000);
               window.location.reload();
           }
           else if(response["is_category_exists"] == true){
              showToast("Category already exists.", 2000);
           }
           else{
               showToast("Unable to edit ticket category due to some internal server error. Kindly report the same", 2000);
               console.log("Please report this. ", response["status_message"]);            
           }
       },
       error: function(xhr, textstatus, errorthrown){
           console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
       }
   });
}

function delete_ticket_category(category_id)
{
  json_string = JSON.stringify({
        category_id:category_id,
    });
  json_string = EncryptVariable(json_string);
    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
       url: '/tms/delete-ticket-category/',
       type: 'POST',
       headers: {
           'X-CSRFToken': CSRF_TOKEN
       },
       data: {
           data: json_string
       },
       success: function(response) {
          response = custom_decrypt(response["response"])
          response = JSON.parse(response);
           if (response["status_code"] == 200) {
               showToast("Ticket Category Deleted Succesfully", 2000);
               window.location.reload();
           }
           else{
               showToast("Unable to delete ticket category due to some internal server error. Kindly report the same", 2000);
               console.log("Please report this. ", response["status_message"]);            
           }
       },
       error: function(xhr, textstatus, errorthrown){
           console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
       }
   });
  
}

function schedule_meeting(element){
  // console.log("Entering details...")
  name = document.getElementById("new-meeting-name").value;
    if(name == ""){
      showToast("Please enter customer's name.");
      return;
    }
    if(!/^[a-zA-Z ]*$/.test(name)){
      showToast("Please enter a valid name.");
      return;
    }

    phone_no = document.getElementById("new-meeting-phone").value;
    if(phone_no == "" || phone_no.length!=10){
      showToast("Please enter customer's 10 digits mobile number.");
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
        user_pincode:user_pincode,
        "channel":"Web"
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
          response = custom_decrypt(response["response"])
          response = JSON.parse(response);
           if (response["status_code"] == 200) {
              showToast("Meeting Scheduled Succesfully.");
              window.location.reload();
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

function save_working_hours(){
  mode = document.getElementById("select-work-mode").value;
  if(mode == ""){
    showToast("Please select the method.", 2000);
    return;
  }
  var month = ""
  if(mode == "1"){
    month = document.getElementById("select-working-month").value;
  }
  year = document.getElementById("select-working-year").value;
  start_time = document.getElementById("start-working-time").value;
  end_time = document.getElementById("end-working-time").value;
  update_existing_working_days = document.getElementById("update-existing-working-days").checked;

  if(start_time == "" || end_time == ""){
    showToast("Please enter working hours.", 2000);
    return;
  }

  if(start_time >= end_time){
    showToast("Please enter valid working hours.", 2000);
    return;
  }

  var days_list = []
  var count = 0;
  var week_days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
  for(var i=0;i<7;i++){
    value = document.getElementById("indeterminate-checkbox-"+i).checked;
    if(value == false){
        count = count + 1
        days_list.push(week_days[i])
    }
  }

  if(count == 7){
    showToast("Please select working days.", 2000);
    return;
  }
  json_string = JSON.stringify({
        "month":month,
        "year":year,
        "start_time":start_time,
        "end_time":end_time,
        "days_list":days_list,
        "update_existing_working_days": update_existing_working_days,
        "mode":mode
    });
  json_string = EncryptVariable(json_string);
    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
       url: '/tms/create-working-hours/',
       type: 'POST',
       headers: {
           'X-CSRFToken': CSRF_TOKEN
       },
       data: {
           data: json_string
       },
       success: function(response) {
          response = custom_decrypt(response["response"])
          response = JSON.parse(response);
           if (response["status_code"] == 200) {
               showToast("Working hours created for particular month", 2000);
               window.location.reload();
           }else if (response["status_code"] == 305) {
               showToast("Working hours exists. Please select update existing working days to update changes.", 2000);
               // window.location.reload();
           }
           else{
               showToast("Unable to create working hours due to some internal server error. Kindly report the same", 2000);
               console.log("Please report this. ", response["status_message"]);            
           }
       },
       error: function(xhr, textstatus, errorthrown){
           console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
       }
   });
}

function change_filter(){
  value = document.getElementById("select-working-leave").value;
  search_url = "/tms/calendar/?"
  if(value == "1"){
      search_url += "is_holiday";
  }
  else if(value == "2"){
    search_url +="is_working";
  }
  month = document.getElementById("select-leave-month").value;
  search_url +="&month="+month;
  year = document.getElementById("select-leave-year").value;
  search_url +="&year="+year;  
  window.location = search_url;
}

function save_leave_calender(){
  value =document.getElementById("add-leave-select").value;
  if(value == "1"){
    date = document.getElementById("modal-leave-date").value;
    reason = document.getElementById("modal-leave-reason").value;
    if(date == ""){
      showToast("Please enter the date",2000)
      return;
    }
    if(reason == ""){
      showToast("Please enter the reason",2000)
      return;
    }
    if(!/^[a-zA-Z ]*$/.test(reason)){
      showToast("Please enter the reason",2000)
      return;
    }
    if(!reason.replace(/\s/g, '').length){
      showToast("Please enter the reason",2000)
      return;
    }
    json_string = JSON.stringify({
          "value":value,
          "date":date,
          "reason":reason,
      });
  }
  else if(value == "2"){
    start_date = document.getElementById("modal-leave-start-date").value;
    end_date = document.getElementById("modal-leave-end-date").value;
    reason = document.getElementById("modal-leave-reason").value;
    if(start_date == "" || end_date == ""){
      showToast("Please enter the date",2000)
      return;
    }
    if(reason == ""){
      showToast("Please enter the reason",2000)
      return;
    }
    if(!/^[a-zA-Z ]*$/.test(reason)){
      showToast("Please enter the reason",2000)
      return;
    }
    if(!reason.replace(/\s/g, '').length){
      showToast("Please enter the reason",2000)
      return;
    }
    json_string = JSON.stringify({
          "value":value,
          "start_date":start_date,
          "end_date":end_date,
          "reason":reason,
      });
  }
  else{
    showToast("Please select an option", 2000);
    return;
  }
  json_string = EncryptVariable(json_string);
    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
       url: '/tms/create-leave/',
       type: 'POST',
       headers: {
           'X-CSRFToken': CSRF_TOKEN
       },
       data: {
           data: json_string
       },
       success: function(response) {
          response = custom_decrypt(response["response"])
          response = JSON.parse(response);
           if (response["status_code"] == 200) {
               showToast("Leave created", 2000);
               window.location.reload();
           }else if (response["status_code"] == 305) {
               showToast("Holiday already exists for selected day", 2000);
               // window.location.reload();
           }else if (response["status_code"] == 405) {
               showToast("Please check the dates and than try again.", 2000);
               // window.location.reload();
           }
           else{
               showToast("Unable to create leave due to some internal server error. Kindly report the same", 2000);
               console.log("Please report this. ", response["status_message"]);            
           }
       },
       error: function(xhr, textstatus, errorthrown){
           console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
       }
   });
}


function edit_working_calendar(working_id){
  start_time = document.getElementById("edit-start-working-time-"+working_id).value;
  end_time = document.getElementById("edit-end-working-time-"+working_id).value;
  if(start_time == "" || end_time == ""){
    showToast("Please enter working hours.",2000);
    return;
  }
  if(start_time >= end_time){
    showToast("Please enter valid working hours.",2000);
    return;
  }

  json_string = JSON.stringify({
        "start_time":start_time,
        "end_time":end_time,
        "working_id":working_id
    });
  json_string = EncryptVariable(json_string);
    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
       url: '/tms/edit-working-hours/',
       type: 'POST',
       headers: {
           'X-CSRFToken': CSRF_TOKEN
       },
       data: {
           data: json_string
       },
       success: function(response) {
          response = custom_decrypt(response["response"])
          response = JSON.parse(response);
           if (response["status_code"] == 200) {
               showToast("Working hours edited for particular month", 2000);
               window.location.reload();
           }else if (response["status_code"] == 305) {
               showToast("Working hours exists", 2000);
               // window.location.reload();
           }
           else{
               showToast("Unable to edit working hours due to some internal server error. Kindly report the same", 2000);
               console.log("Please report this. ", response["status_message"]);            
           }
       },
       error: function(xhr, textstatus, errorthrown){
           console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
       }
   });
}

function delete_leave_calendar(calendar_id){
  start_time = document.getElementById("add-start-working-time-"+calendar_id).value;
  end_time = document.getElementById("add-end-working-time-"+calendar_id).value;

  if(start_time == "" || end_time == ""){
    showToast("Please select working hours.",2000)
    return;
  }
  if(start_time >= end_time){
    showToast("Please enter valid working hours.",2000)
    return;
  }

  json_string = JSON.stringify({
        "start_time":start_time,
        "end_time":end_time,
        "calendar_id":calendar_id
    });
  json_string = EncryptVariable(json_string);
    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
       url: '/tms/delete-leaves/',
       type: 'POST',
       headers: {
           'X-CSRFToken': CSRF_TOKEN
       },
       data: {
           data: json_string
       },
       success: function(response) {
          response = custom_decrypt(response["response"])
          response = JSON.parse(response);
           if (response["status_code"] == 200) {
               showToast("Leave deleted successfully", 2000);
               window.location.reload();
           }
           else{
               showToast("Unable to delete leave due to some internal server error. Kindly report the same", 2000);
               console.log("Please report this. ", response["status_message"]);            
           }
       },
       error: function(xhr, textstatus, errorthrown){
           console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
       }
   }); 
}

function get_leave_option(){
  value =document.getElementById("add-leave-select").value;
  html = ""
  if(value == "1"){
    document.getElementById("add-leave-option").innerHTML = ""
    html = "<div class=\"col s3\">\
                <p>Date</p>\
               <input type=\"date\" id=\"modal-leave-date\">\
            </div>\
            <div class=\"col s9\">\
               <p>Reason</p>\
               <input type=\"text\" id=\"modal-leave-reason\">\
            </div>"
    document.getElementById("add-leave-option").innerHTML = html;
  }
  else if(value == "2"){
    document.getElementById("add-leave-option").innerHTML = ""
    html = "<div class=\"col s6\">\
        <p>Start Date</p>\
          <input type=\"date\" id=\"modal-leave-start-date\">\
      </div>\
      <div class=\"col s6\">\
        <p>End Date</p>\
          <input type=\"date\" id=\"modal-leave-end-date\">\
      </div>\
      <div class=\"col s12\">\
        <p>Reason</p>\
        <input type=\"text\" id=\"modal-leave-reason\">\
      </div>"
      document.getElementById("add-leave-option").innerHTML = html;
  }
}

function capture_general_feedBack() {
    document.getElementById("feedback-description-error").style.display="none";
    document.getElementById("feedback-category-error").style.display="none";
    document.getElementById("feedback-priority-error").style.display="none";
    document.getElementById("upload-feedback-screenshot-error").style.display="none";
    flag_error = false;

    description = document.getElementById('feedback_description').value;
    description = stripHTML(description).trim()
    if(description == "")
    {
        document.getElementById("feedback-description-error").style.display="block";
        document.getElementById("feedback-description-error").textContent = "*Description cannot be empty";
        flag_error = true;
    }

    // is_feedback_screenshot_attached = document.getElementById("is_feedback_screenshot_attached").checked;

    is_feedback_screenshot_attached = true;

    feedback_category = document.getElementById("feedback_category").value;
    if(feedback_category == "")
    {
        document.getElementById("feedback-category-error").style.display="block";
        flag_error = true;
    }

    feedback_priority = document.getElementById("feedback_priority").value;

    if(feedback_priority == "")
    {
        document.getElementById("feedback-priority-error").style.display="block";
        flag_error = true;
    }
    
    if(!($("#input_upload_feedback_screenshot"))[0].files[0])
    {
        // document.getElementById("upload-feedback-screenshot-error").style.display="block";
        is_feedback_screenshot_attached = false;
    }
    if(flag_error == false)
    {
        document.getElementById("feedback_preloader").style.display = "block";
        if(is_feedback_screenshot_attached)
        {
                var input_upload_image = ($("#input_upload_feedback_screenshot"))[0].files[0]
                var formData = new FormData();
                var CSRF_TOKEN = $('input[name="csrfmiddlewaretoken"]').val();
                formData.append("input_upload_image", input_upload_image);

            $.ajax({
                url: "/chat/upload-image/",
                type: "POST",
                headers: {
                    'X-CSRFToken': CSRF_TOKEN
                },
                data: formData,
                processData: false,
                contentType: false,
                success: function(response) {
                    if (response["status"] == 200) {
                        // src = window.location.origin + response["src"]
                        // addIntentResponseImageIntoCollection(src);
                        json_string = JSON.stringify({
                            description: description,
                            category: feedback_category,
                            priority: feedback_priority,
                            app: "EasyTMS",
                            src: response['src'],                        
                        });
                        json_string = EncryptVariable(json_string);
                        $.ajax({
                            url: "/chat/capture-general-feedback/",
                            type: "POST",
                            data: {
                                data: json_string,
                            },
                            success: function(response) {
                                if (response['status'] == 200) {
                                    M.toast({
                                        "html": "Feedback Sent."
                                    }, 2000)
                                    window.location.reload();
                                } else {
                                    M.toast({
                                        "html": "Internal Server Error."
                                    }, 2000)
                                }
                            },
                            error: function(xhr, textstatus, errorthrown) {}
                        });

                    } else if (response["status"] == 300) {
                        document.getElementById("feedback_preloader").style.display = "none";
                        M.toast({
                            "html": "File format is Invalid"
                        }, 2000)
                    } else {
                        document.getElementById("feedback_preloader").style.display = "none";
                        M.toast({
                            "html": "Internal Server Error. Please try again later."
                        }, 2000)
                    }
                },
                error: function(xhr, textstatus, errorthrown) {
                    document.getElementById("feedback_preloader").style.display = "none";
                    console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
                }
            });
        }
    else
    {
        json_string = JSON.stringify({
            description: description,
            category: feedback_category,
            priority: feedback_priority,
            app: "EasyTMS",
            src: "",                        
        });
        json_string = EncryptVariable(json_string);
        $.ajax({
            url: "/chat/capture-general-feedback/",
            type: "POST",
            data: {
                data: json_string,
            },
            success: function(response) {
                if (response['status'] == 200) {
                    M.toast({
                        "html": "Feedback Sent."
                    }, 2000)
                    window.location.reload();
                } else {
                    document.getElementById("feedback_preloader").style.display = "none";
                    M.toast({
                        "html": "Internal Server Error."
                    }, 2000)
                }
            },
            error: function(xhr, textstatus, errorthrown) {
                document.getElementById("feedback_preloader").style.display = "none";
            }
        });
    }
    }
}

function getCSRFToken() {
    return $('input[name="csrfmiddlewaretoken"]').val();
}

function stripHTML(htmlString) {
    return htmlString.replace(/<[^>]+>/g, '');
}

function open_general_feedback_modal()
{
    $("#modal-general-feedback").modal("open");
    var elem = document.getElementById('modal-general-feedback');
    $('#modal-general-feedback').find('input:text, input:file, input:password, select, select2-feedback_category-container, textarea').val('');
}

function submit_agent_performance_report_filter(){
  start_date = document.getElementById("agent-performance-report-start-date").value;
  if(start_date == ""){
    M.toast({
      "html":"Please select a start date"
    },2000)
    return;
  }
  end_date = document.getElementById("agent-performance-report-end-date").value;
  if(end_date == ""){
    M.toast({
      "html":"Please select a end date"
    },2000)
    return;
  }
  if(start_date > end_date){
    M.toast({
      "html":"Please select a valid date range"
    },2000)
    return;
  }
  window.location.href = window.location.origin + window.location.pathname + "?start_date="+start_date + "&end_date="+end_date
}

function validate_email(id){

  var regex = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
  var ctrl =  document.getElementById(id);

  if (regex.test(ctrl.value)) {
      return true;
  }
  else {
      return false;
  }
}

function agent_performance_export(){

    startdate = $('#startdate').val();
    enddate = $('#enddate').val();
    email_field = document.getElementById('filter-data-email');

    if(validate_email("filter-data-email")==false){
        M.toast({"html": 'Please enter valid email ID'}, 4000, "rounded");
        return;
    }

    if(startdate=="" || enddate=="")
    {
        M.toast({"html": 'Please enter valid dates'}, 4000, "rounded");
        return ;
    }
    var start_datetime = new Date(startdate);
    var end_datetime = new Date(enddate);
    if (start_datetime > end_datetime) {

        M.toast({"html": 'Start Date should be less than End Date'}, 4000, "rounded");
        return ;
    }
    var json_string = JSON.stringify({
        "startdate": startdate,
        "enddate": enddate,
        "email": email_field.value,
    })
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: "/tms/agent-performance-report-exportdata/",
        type: "POST",
        data: {
            json_string: json_string
        },
        success: function(response) {
          response = custom_decrypt(response)
          response = JSON.parse(response);
          if(response["status"]=200){
              alert("We haved saved your request and will send data over provided email ID within 24 hours.")
              window.location.reload()
          }
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: "+errorthrown+xhr.status+xhr.responseText);
        }
    });
}


function agent_active(agent_id){

  agent_status = document.getElementById("agent-status").checked;
    var json_string = JSON.stringify({
        "agent_status": agent_status,
        "agent_id":agent_id
    })
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: "/tms/agent-active-or-not/",
        type: "POST",
        data: {
            json_string: json_string
        },
        success: function(response) {
          response = custom_decrypt(response)
          response = JSON.parse(response);
          if(response["status"]=200){
             // window.location.reload()
          }
          else{
            M.toast({
              "html":"Unable to mark you as absent. Please try again."
            },2000)
          }
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: "+errorthrown+xhr.status+xhr.responseText);
        }
    });
}


function submit_flag(customer_id){

  flag_not_relevent = document.getElementById("checkbox-flag-ticket-not-relevent").checked;
  flag_bot = document.getElementById("checkbox-flag-ticket-bot").checked;

  if(flag_not_relevent == false && flag_bot == false){
      M.toast({
        "html":"Please select atleast one option."
      },2000)
      return;
  }

  var json_string = JSON.stringify({
      "flag_not_relevent": flag_not_relevent,
      "flag_bot":flag_bot,
      "customer_id":customer_id
  })
  json_string = EncryptVariable(json_string);
  var CSRF_TOKEN = getCsrfToken();
  $.ajax({
      url: "/tms/agent-flag-ticket/",
      type: "POST",
      data: {
          json_string: json_string
      },
      success: function(response) {
        response = custom_decrypt(response)
        response = JSON.parse(response);
        if(response["status"]=200){
           window.location.reload()
        }
        else{
          M.toast({
            "html":"Unable to mark you as absent. Please try again."
          },2000)
        }
      },
      error: function(xhr, textstatus, errorthrown) {
          console.log("Please report this error: "+errorthrown+xhr.status+xhr.responseText);
      }
  });
}

if(window.location.pathname=="/tms/"){
  $(document).ready(function(){
      var table = $('#table-customer-details').DataTable({
        "language": {
              "info": "Showing _START_ to _END_ entries out of "+total_customer_objs,
              "infoEmpty": "No records available",
              "infoFiltered": "(filtered from _MAX_ total records)",
            },
           "bPaginate": false,
           "pagingType": "simple",
           "ordering": false,
          "infoCallback": function( settings, start, end, max, total, pre ) {
                end = (start_point - 1) + end;
                start = (start_point - 1) + start;
                return "Showing " + start + " to " + end + " entries out of " +total_customer_objs;
              }
      });
      setTimeout(function(){
          window.location.reload();
      }, 300000);
  });
}
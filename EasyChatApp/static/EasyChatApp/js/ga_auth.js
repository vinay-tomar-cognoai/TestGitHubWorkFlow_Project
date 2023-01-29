function validate_phone_number(phone) {
        
    phone = phone.trim();
    var is_number = /^\d+$/.test(phone);
    var regex = /[6-9][0-9]{9}/;
    if (phone != "" && regex.test(phone) && phone.length == 10 && is_number) {
        return true;
    }

    return false;
}
    
function validate_email(email) {
   var email = email.trim();
    var regex = /^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/;
    if (email != "" && regex.test(email)) {
        return true;
    }

    return false;
}


function get_csrf_token() {
    var CSRF_TOKEN = $('input[name="csrfmiddlewaretoken"]').val();
    return CSRF_TOKEN;
}

function get_otp(el) {

    $("#internal_error").hide();
    var CSRFToken=get_csrf_token();
    var mobile_number = $("#mobile-number").val();


    if(mobile_number == "" || !validate_phone_number(mobile_number)) {
        
        $("#internal_error").html("Please enter valid Mobile Number");
        $("#internal_error").show();
        return ;
    }

    var email_id = $("#email-id").val();

    if(email_id == "" || !validate_email(email_id)) {
        
        $("#internal_error").html("Please enter valid Email ID");
        $("#internal_error").show();
        return ;
    }
    var pan_number = $("#pan-number").val();

    if(IS_PAN_REQ == 'True' || IS_PAN_REQ == 'true') {

        if(pan_number == "") {
        
            $("#internal_error").html("Please enter valid PAN Number");
            $("#internal_error").show();
            return ;
        }
    }

    $(el).html('Sending');    

    $.ajax({
        url:"/chat/get-google-assistant-auth-otp/",
            type:"POST",
            data:{
                mobile_number: mobile_number,
                email_id: email_id,
                pan_number: pan_number,
                project_details_id: PROJECT_DETAILS_PK,
            },
            success: function(response){ 
                if(response["status"]==200){
                    document.querySelector(".easychat-alexa-login-credential-div").style.display = "none";
                    document.querySelector(".easychat-alexa-otp-verification-div").style.display = "block";
                    document.getElementsByClassName('otp-form')[0].focus();
                }else{
                    $("#internal_error").show();                     
                }

                $(el).html('Get OTP');    
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
            $(el).html('Get OTP');
        }
    });        
}

var CSRFToken=get_csrf_token();
$(document).on("click","#verify-btn", function(e){
    $("#otp_internal_error").hide();

    var mobile_number = $("#mobile-number").val();
    var email_id = $("#email-id").val();
    var pan_number = $("#pan-number").val();
    var entered_otp_inputs = document.getElementsByClassName('otp-form');

    var entered_otp = "";
    for (otp_input of entered_otp_inputs) {
        entered_otp += otp_input.value;
    }

    if (entered_otp == "" || entered_otp.length < 6) {
        $('#otp_internal_info').html('Please enter otp before submitting.');
        return;
    } else {
        $('#otp_internal_info').html('');
    }

    $(e.target).html('Verifying');

    $.ajax({
        url:"/chat/verify-google-assistant-otp/",
        type:"POST",
        data:{
            mobile_number: mobile_number,
            email_id: email_id,
            pan_number: pan_number,
            otp: entered_otp,
            project_details_id: PROJECT_DETAILS_PK,
        },
        success: function(response){

             if(response["status"]==200){

                var cur_url = new URL(window.location.href);
                window.location.href = window.location.origin + "/o/authorize/" + cur_url.search;
             }else{

                $("#otp_internal_error").show();
                $(e.target).html('Verify');
             }
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
            $(e.target).html('Verify');
        }
    });
});

$('.otp-form').on('keypress', function(e) {
    keys = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    return keys.indexOf(event.key) > -1
});

$('.otp-form').on('keyup', function(e) {
    keys = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    if (keys.indexOf(this.value) != -1) {
        $(this).next().focus();
    }
});

function empty_otp_fields() {
    var otp_elems = document.getElementsByClassName('otp-form');

    for (otp_elem of otp_elems) {
        otp_elem.value = '';
    }
}

function resend_otp_code(el) {
    $("#otp_internal_error").hide();                     
    $(el).html('Sending');
    el.style.pointerEvents = 'none';

    var mobile_number = $("#mobile-number").val();
    var email_id = $("#email-id").val();
    var pan_number = $("#pan-number").val();

    empty_otp_fields();

    $.ajax({
        url:"/chat/get-google-assistant-auth-otp/",
            type:"POST",
            data:{
                mobile_number: mobile_number,
                email_id: email_id,
                pan_number: pan_number,
            },
            success: function(response){ 
                if(response["status"]==200){
                    document.getElementById('otp_internal_info').innerHTML  = 'OTP has been sent successfully.';
                    document.getElementsByClassName('otp-form')[0].focus();
                    
                    setTimeout(function() {
                        document.getElementById('otp_internal_info').innerHTML  = '';
                        el.style.pointerEvents = 'auto';
                    }, 2000)
                }else{
                    $("#otp_internal_error").show();                     
                }

                $(el).html('Resend Code');    
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        }
    });
}
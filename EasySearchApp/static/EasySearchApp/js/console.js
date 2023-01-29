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
        $('.slider').slider();
        $('.tooltipped').tooltip({
            position: 'top'
        });
        $('.datepicker').datepicker({
            format: "dd/mm/yyyy"
        });
        $('.fixed-action-btn').floatingActionButton();
        $(".readable-pro-tooltipped").tooltip({
            position: "top"
        });
    });
})(jQuery);

/***********************************************************************************/

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

function showToast(message, duration) {
    M.toast({
        "html": message, classes: 'rounded'
    }, duration);
}

function getCsrfToken() {
    var CSRF_TOKEN = $('input[name="csrfmiddlewaretoken"]').val();
    return CSRF_TOKEN;
}

$(document).on("click", "#btn-save-details", function(e) {

    var files = ($("#input-upload-logo"))[0].files
    if (files.length == 0) {
        showToast("Kindly select an png/jpg file to upload.", 2000);
        return;
    }
    file = files[0];

    var formData = new FormData();
    fname = file['name'].split('.');
    fname = fname[fname.length - 1].toLowerCase();
    if (fname == "jpg" || fname == "png") {
        formData.append("file", file);
    } else {
        showToast("Kindly select an jpg/png file to upload.", 2000);
        return;
    }
    var next_indexing = document.getElementById("next-indexing").value;
    if (next_indexing == ""){
        showToast("Kindly enter the auto indexing days", 2000);
        return;
    }
    formData.append("next_indexing",next_indexing)
    $.ajax({
        url: "/console/save-details/",
        type: "POST",
        headers: {
            "X-CSRFToken": getCsrfToken()
        },
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                console.log("response")
                showToast("Saved successfully.", 2000);
                window.location.reload()
            } else {
                console.log(response);
            }
        },
         error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        }
    });
});


$(document).on("click", "#btn-start-crawling", function(e) {

    var url = document.getElementById("crawl-url").value
    if(url == "")
    {
        showToast("Kindly enter a URL to start crawling", 2000);
        return;
    }
    var hyper_text = document.getElementById("hyper-text").value

    if(hyper_text == "1"){
        hyper_text = "HTTPS"
    }
    else if( hyper_text == "2"){
        hyper_text = "HTTP"
    }
    else{

        showToast("Kindly select the hyper text", 2000);
        return;
    }
    var json_string = JSON.stringify({
      url: url,
      hyper_text: hyper_text
    })
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: "/console/start-crawling/",
        type: "POST",
        headers: {
            "X-CSRFToken": getCsrfToken()
        },
        data: {
            json_string: json_string
        },
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                console.log("response")
                 showToast("Saved successfully.", 2000);
            } else {
                console.log(response);
            }
        },
         error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        }
    });
});




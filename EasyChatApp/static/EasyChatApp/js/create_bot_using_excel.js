var excel_processing_interval = null
var excel_processing_id = ""

$("#home-button").click(function() {
    if ($("#panel").is(":visible") == true) {
      $("#panel").hide(100);  
    } else {
      $("#panel").show(100);
    }
  });

$(document).on('contextmenu', '.collapsible_custom', function(e){
    e.preventDefault();
    var d = document.getElementById('menu-div');
    d.style.position = "absolute";
    d.style.left = e.pageX - 200 + 'px';
    d.style.top = e.pageY + 'px';
    pk_list = this.id.split("_");
    global_select_tree_name = $(this).text().trim()
    global_select_intent_id = pk_list[0];
    global_select_parent_id = pk_list[1];
    global_select_tree_id = pk_list[2];
    var tree_name = document.getElementById(this.id+"_tree_name_container").getAttribute("value");
    document.getElementById("modal_tree_name").value = tree_name;
    $("#menu-div").show();
    return false;
});

$(document).ready(function() {
      $('.modal').modal();
      $('.modal').on('shown.bs.modal', function(e)
  { 
    $('#modal-general-feedback').find('input:text, input:file, input:password, select, textarea').val('');
      $(this).removeData();
  }) ;
});

$(document).ready(function(){
  $('.collapsible').collapsible();
});
$(document).ready(function(){
  $('.datepicker').datepicker({
    format: 'yyyy-mm-dd',
  });
});


elements = document.getElementById("buildchatbot-sidenav");

elements = document.getElementById("buildchatbot-sidenav");
for(var index=0; index<elements.childNodes.length; index++){
   if(elements.childNodes[index].href!=undefined){
      elements.childNodes[index].classList.remove("active");
   }
}

for(var index=0; index<elements.childNodes.length; index++){
   if(elements.childNodes[index].href!=undefined && elements.childNodes[index].href.indexOf(window.location.pathname)!=-1){
      elements.childNodes[index].classList.add("active");
      break;
   }
}

$(document).on("click", "#submit_faqs", function(e) {
    e.preventDefault();
    document.getElementsByClassName("error-message")[0].style.display = "none";
    document.getElementsByClassName("loading-message")[0].style.display = "none";
    var selected_bot_pk = get_url_vars()["bot_pk"];

    if (selected_bot_pk == "None") {
        M.toast({
            "html": "Please select atleast one bot to create quick excel bot."
        }, 2000);
        return;
    }

    var selected_bot_pk_list = [selected_bot_pk];
    var selected_type_of_excel = document.getElementById("excel").value;

    var my_file = ($("#drag-drop-input-box"))[0].files[0];

    if (my_file == undefined || my_file == null) {
        M.toast({
            "html": "Please provide excel sheet in required format."
        }, 2000);
        return;
    }

    if (check_malicious_file(my_file.name) == true) {
        return false;
    }

    var allowed_files_list = ["xlsx", "xls"]
    var file_name = my_file.name;
    var file_extension = file_name.substring(file_name.lastIndexOf(".") + 1, file_name.length);
    file_extension = file_extension.toLowerCase();

    if (allowed_files_list.includes(file_extension) == false) {
        M.toast({
            "html": "." + file_extension + " files are not allowed"
        }, 2000);
        return true;
    }

    var formData = new FormData();
    formData.append("my_file", my_file);
    formData.append("bot_id_list", selected_bot_pk_list);
    formData.append("type_of_excel_file", selected_type_of_excel);

    document.getElementsByClassName("loading-message")[0].style.display = "flex";
    document.getElementById("submit_faqs").disabled = true;
    document.getElementById('excel').disabled = true;
    $.ajax({
        url: "/chat/submit-excel/",
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response['status'] == 200) {

                excel_processing_id = response["excel_processing_id"];

                excel_processing_interval = setInterval(function() {
                    update_excel_processing_progress(excel_processing_id);
                }, 5000)

                if (selected_type_of_excel == "1") {
                    M.toast({
                        'html': "Creating your FAQ bot. It may take some time."
                    }, 2000);
                } else {
                    M.toast({
                        'html': "Creating your UserFlow based bot. It may take some time."
                    }, 2000);
                }
            } else if (response['status'] == 101) {
                document.getElementsByClassName("loading-message")[0].style.display = "none";
                document.getElementsByClassName("error-message")[0].getElementsByTagName("span")[0].innerHTML = response["message"]
                document.getElementsByClassName("error-message")[0].style.display = "flex";
                document.getElementById("submit_faqs").disabled = false;
                document.getElementById('excel').disabled = false;
                M.toast({
                    'html': response["message"]
                }, 2000);
            } else if (response['status'] == 300) {
                document.getElementsByClassName("loading-message")[0].style.display = "none";
                document.getElementsByClassName("error-message")[0].getElementsByTagName("span")[0].innerHTML = response["message"]
                document.getElementsByClassName("error-message")[0].style.display = "flex";
                document.getElementById("submit_faqs").disabled = false;
                document.getElementById('excel').disabled = false;
                error_messages_array = response["message"].split("::")
                html_string = "<h6>We found following errors:"
                for (var i = 0; i < error_messages_array.length; i++) {
                    html_string += "<p>" + error_messages_array[i] + "</p>"
                }
                html_string += "</h6>"
                var errorDisplaySpace = document.getElementById("error_messages");
                errorDisplaySpace.innerHTML = html_string;
                errorDisplaySpace.scrollIntoView();
            } else if (response['status'] == 400 || response['status'] == 401) {
                document.getElementsByClassName("loading-message")[0].style.display = "none";
                document.getElementsByClassName("error-message")[0].getElementsByTagName("span")[0].innerHTML = response["message"]
                document.getElementsByClassName("error-message")[0].style.display = "flex";
                document.getElementById("submit_faqs").disabled = false;
                document.getElementById('excel').disabled = false;
                M.toast({
                    'html': response["message"]
                }, 2000);
            } else {
                document.getElementsByClassName("loading-message")[0].style.display = "none";
                try{
                    document.getElementsByClassName("error-message")[0].getElementsByTagName("span")[0].innerHTML = response["status_message"]
                }catch(err){
                    document.getElementsByClassName("error-message")[0].getElementsByTagName("span")[0].innerHTML = "Please check excel file format";
                }
                document.getElementsByClassName("error-message")[0].style.display = "flex";
                document.getElementById("submit_faqs").disabled = false;
                document.getElementById('excel').disabled = false;
                try {
                    M.toast({
                        'html': response["status_message"]
                    }, 2000);
                } catch (e) {
                    M.toast({
                        'html': "Please check excel file format"
                    }, 2000);
                }
            }
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        }
    });

});

function update_excel_processing_progress(excel_processing_id) {
    var json_string = JSON.stringify({
        excel_processing_id: excel_processing_id,
    })
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: "/chat/get-excel-processing-progress/",
        type: "POST",
        data: {
            json_string: json_string
        },
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                clearInterval(excel_processing_interval);
                document.getElementsByClassName("loading-message")[0].style.display = "none";
                document.getElementsByClassName("error-message")[0].style.display = "none";
                document.getElementById("submit_faqs").disabled = false;
                document.getElementById('excel').disabled = false;
                document.querySelector(".drag-drop-message").style.display="flex";
                document.querySelector("#bot-excel-selected-filename").innerHTML="";
                document.querySelector("#drag-drop-input-box").value="";
                $("#success-modal").modal("open");
            }else if (response["status"] == 102) {
                clearInterval(excel_processing_interval);
                document.getElementsByClassName("loading-message")[0].style.display = "none";
                document.getElementsByClassName("error-message")[0].getElementsByTagName("span")[0].innerHTML = response["status_message"]
                document.getElementsByClassName("error-message")[0].style.display = "flex";
                document.getElementById("submit_faqs").disabled = false;
                document.getElementById('excel').disabled = false;
                document.querySelector(".drag-drop-message").style.display="flex";
                document.querySelector("#bot-excel-selected-filename").innerHTML="";
                document.querySelector("#drag-drop-input-box").value="";
                M.toast({
                    "html": response["status_message"]
                }, 1000);
            }else if (response["status"] == 500){
                clearInterval(excel_processing_interval);
                document.getElementById("submit_faqs").disabled = false;
                document.getElementById('excel').disabled = false;
                document.querySelector(".drag-drop-message").style.display="flex";
                document.querySelector("#bot-excel-selected-filename").innerHTML="";
                document.querySelector("#drag-drop-input-box").value="";
            }
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
            M.toast({
                "html": "Unable to start excel processing. Kindly try again later."
            }, 1000);
        }
    });
}

function handleFileInputChange(){
    var fileName=document.querySelector("#drag-drop-input-box").value;
    fileName = fileName.replace(/.*[\/\\]/, '');
    if(fileName)
    {  
        if (fileName.length > 25){
            fileName = fileName.slice(0, 25) + "...";
        }
    document.querySelector(".drag-drop-message").style.display="none";
    document.querySelector("#bot-excel-selected-filename").innerHTML=` 
            <div class="bot-excel-selected-dismiss-btn" style="display: flex;justify-content: flex-end;">
              <svg width="16" onclick="handleFileCrossBtn()" style="z-index: 1000;cursor: pointer;" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M2.39705 2.55379L2.46967 2.46967C2.73594 2.2034 3.1526 2.1792 3.44621 2.39705L3.53033 2.46967L8 6.939L12.4697 2.46967C12.7626 2.17678 13.2374 2.17678 13.5303 2.46967C13.8232 2.76256 13.8232 3.23744 13.5303 3.53033L9.061 8L13.5303 12.4697C13.7966 12.7359 13.8208 13.1526 13.6029 13.4462L13.5303 13.5303C13.2641 13.7966 12.8474 13.8208 12.5538 13.6029L12.4697 13.5303L8 9.061L3.53033 13.5303C3.23744 13.8232 2.76256 13.8232 2.46967 13.5303C2.17678 13.2374 2.17678 12.7626 2.46967 12.4697L6.939 8L2.46967 3.53033C2.2034 3.26406 2.1792 2.8474 2.39705 2.55379L2.46967 2.46967L2.39705 2.55379Z" fill="#A8A8A8"/>
              </svg>                
            </div>
            <div class="">
              <svg width="67" height="80" viewBox="0 0 67 80" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M17.5 62V22.6398L38.9465 18.0205L44.8023 23.5511L46.1256 24.8744L48.1256 26.8744L48.6602 27.409L43.3964 62H17.5Z" stroke="#BED8FB" stroke-width="35" stroke-linejoin="round"/>
                <path d="M44.3446 35.3108C46.417 36.3471 48.688 36.9199 51 36.9922V56.5H24V16H30.5705C30.6222 16.5494 30.7024 17.0961 30.8107 17.6379L31.3107 20.1379C31.7206 22.1872 32.5279 24.1363 33.6872 25.8752L34.6872 27.3752C35.2716 28.2519 35.9413 29.0687 36.6863 29.8137L38.1863 31.3137C39.4023 32.5297 40.8064 33.5418 42.3446 34.3108L44.3446 35.3108Z" stroke="#DDEAFB" stroke-width="32" stroke-linejoin="round"/>
              </svg>
            </div>                         
            <p>
            ${sanitize_html(fileName)}
            </p>`;
    }
}

function handleFileCrossBtn(){
    if (document.getElementsByClassName("loading-message")[0].style.display == "flex"){
        return;
    }
    document.querySelector(".drag-drop-message").style.display="flex";
    document.querySelector("#bot-excel-selected-filename").innerHTML="";
    document.querySelector("#drag-drop-input-box").value="";
}

function handleSelected(e){
    document.querySelector(".open-container-excel").style.display="block";
    document.getElementById("select2-excel-container").style.color="#444";
    document.getElementsByClassName("loading-message")[0].style.display = "none";
    document.getElementsByClassName("error-message")[0].style.display = "none";
    document.querySelector(".drag-drop-message").style.display="flex";
    document.querySelector("#bot-excel-selected-filename").innerHTML="";
    document.querySelector("#drag-drop-input-box").value="";
    if (e.value == "1"){
      document.getElementById("sample-excel").href = "/files/faq/EasyChatFAQSheetFormat.xlsx";
    }else{
      document.getElementById("sample-excel").href = "/files/faq/EasyChatFlowSheetFormat.xlsx";
    }

}

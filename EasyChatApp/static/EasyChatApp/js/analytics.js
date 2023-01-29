$('.dropdown-trigger').dropdown();
$('.modal').modal();
$('.processing').hide();
$('.test_processing').hide();
$('.upload_testdata').hide();


$(document).ready(function(){
    disable_future_date()
    $('.modal').modal();
});

var flow_analytics_filter_value = [];
var flow_analytics_date_filter_value = null;
var set_initial_filter = true;

/////////////////////////////// Encryption And Decription //////////////////////////

function CustomEncrypt(msgString, key) {
    // msgString is expected to be Utf8 encoded
    var iv = EasyChatCryptoJS.lib.WordArray.random(16);
    var encrypted = EasyChatCryptoJS.AES.encrypt(msgString, EasyChatCryptoJS.enc.Utf8.parse(key), {
        iv: iv
    });
    var return_value = key;
    return_value += "."+encrypted.toString(); 
    return_value += "."+EasyChatCryptoJS.enc.Base64.stringify(iv);
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

  utf_data = EasyChatCryptoJS.enc.Utf8.parse(data);
  encoded_data = utf_data;
  // encoded_data = EasyChatCryptoJS.enc.Base64.stringify(utf_data);
  random_key = generateRandomString(16);
  // console.log(random_key)
  encrypted_data = CustomEncrypt(encoded_data, random_key);

  return encrypted_data;
}

function custom_decrypt(msg_string){

  var payload = msg_string.split(".");
  var key = payload[0];
  var decrypted_data = payload[1];
  var decrypted = EasyChatCryptoJS.AES.decrypt(decrypted_data, EasyChatCryptoJS.enc.Utf8.parse(key), { iv: EasyChatCryptoJS.enc.Base64.parse(payload[2]) });
  return decrypted.toString(EasyChatCryptoJS.enc.Utf8);
}


////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    flow_analytics_filter_value = [];
    set_flow_analytics_filter();
})

function transpose(a) {
    return Object.keys(a[0]).map(function(c) {
        return a.map(function(r) { return r[c]; });
    });
}

function showAnalyticsPreloader(){
   $("#div-analytics-preloader").show();
   $("#div-analytics").hide();
   $("#select-bot-for-analytics").hide();
}

function hideAnalyticsPreloader(){
   $("#div-analytics-preloader").hide();
   $("#select-bot-for-analytics").show();
   $("#div-analytics").show();  
}

if(window.location.pathname=="/chat/analytics/"){
    setTimeout(function(){
        showDailyAnalytics([]);
    }, 500);
}

function validateEmail(emailField) {
    var reg = /^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/;
    if (reg.test(emailField.value) == false) {
        return false;
    }
    return true;
}

if(window.location.pathname=="/chat/mis-dashboard/"){
    $("#show-global-search").show();
    $("#global_search").attr("placeholder","Search in IT Dashboard");
    $("#global_search").attr("onkeyup","searchInfo('mis-dashboard-info-table',8)");
    $(".modal").modal();
}

$("#export-mis-filter").click(function(){

    selected_filter_value = $("input[name='select-date-range']:checked").val()
    bot_pk = document.getElementById('selected-bot-message-history').value;

    if(!selected_filter_value || selected_filter_value.trim() == ""){
        showToast("Please select valid date range filter", 2000);
        return;
    }

    is_keyword = "No"
    keyword_str = ""
    startdate = $('#startdate').val();
    enddate = $('#enddate').val();
    filter = $('#filter').val();
    email_field = document.getElementById('filter-data-email');    

    if(selected_filter_value=="4" && validateEmail(email_field)==false){
        M.toast({"html": 'Please enter valid email ID'}, 4000, "rounded");
        return;
    }

    bot_name = "All";
    if (bot_pk!="None"){
        bot_name = document.getElementById('selected-bot-message-history').selectedOptions[0].label;
    }
    
    var startdate_obj = new Date(startdate)
    var enddate_obj = new Date(enddate)
    if((selected_filter_value=="4" && (startdate=="" || enddate=="")) || (selected_filter_value=="4" && startdate_obj.getTime()>enddate_obj.getTime()))
    {
        M.toast({"html": 'Please enter valid dates'}, 4000, "rounded");
    }
    else
    {
        var json_string = JSON.stringify({
            "selected_filter_value": selected_filter_value,
            "is_keyword" : is_keyword,
            "keyword_str": keyword_str,
            "startdate": startdate,
            "enddate": enddate,
            "filter": filter,
            "email": email_field.value,
            "bot_pk": bot_pk,
            "bot_name": bot_name
        })
        json_string = EncryptVariable(json_string);

        $.ajax({
            url: "/chat/exportdata/",
            type: "POST",
            data: {
                json_string: json_string
            },
            success: function(response) {
              response = custom_decrypt(response)
              response = JSON.parse(response);
              if(response["status"]==200){
                  if(response["export_path"]==null){
                    showToast("Sorry, unable to process your request. Kindly try again later.", 2000);
                  }else if(response["export_path"]=="request_saved"){
                        setTimeout(function(){ showToast("We have saved your request and will send data over provided email ID within 24 hours.", 4000); }, 500);      
                  }else{
                      if(response["export_path_exist"]){
                        window.location = response["export_path"]
                      }else{
                        showToast("Requested data doesn't exists. Kindly try again later.", 2000);
                      }
                  }
              }else if(response["status"]==400) {
                M.toast({"html": response["message"]}, 4000, "rounded");
              }else {
                showToast("Sorry, unable to process your request. Kindly try again later.", 2000);
              }
            },
            error: function(xhr, textstatus, errorthrown) {
                console.log("Please report this error: "+errorthrown+xhr.status+xhr.responseText);
            }
        });
    }
});

$("#export-nps-data").click(function(){
    selected_filter_value = $("input[name=analytics-export-filter]:checked").val();

    if(selected_filter_value=="0"){
        alert("Please select valid date range filter");
        return;
    }
    startdate = $('#export-startdate').val();
    enddate = $('#export-enddate').val();
    email_field = document.getElementById('filter-data-email');   
    bot_pk = $('#selected_bot_pk').data("selected_bot_pk");

    if(selected_filter_value=="4" && validateEmail(email_field)==false){
        M.toast({"html": 'Please enter valid email ID'}, 4000, "rounded");
        return;
    }

    var startdate_obj = new Date(startdate)
    var enddate_obj = new Date(enddate)
    if((selected_filter_value=="4" && (startdate=="" || enddate=="")) || (selected_filter_value=="4" && startdate_obj.getTime()>enddate_obj.getTime()))
    {
        M.toast({"html": 'Please enter valid dates'}, 4000, "rounded");
    }
    else
    {
        var json_string = JSON.stringify({
            "selected_filter_value": selected_filter_value,
            "startdate": startdate,
            "enddate": enddate,
            "email": email_field.value,
            "bot_pk": bot_pk,
        })
        json_string = EncryptVariable(json_string);

        $.ajax({
            url: "/chat/export-nps-data/",
            type: "POST",
            data: {
                json_string: json_string
            },
            success: function(response) {
              response = custom_decrypt(response)
              response = JSON.parse(response);
              if(response["status"]=200){
                  if(response["export_path"]==null){
                      alert("Sorry, unable to process your request. Kindly try again later.");
                  }else if(response["export_path"]=="request_saved"){
                      setTimeout(function(){ alert("We have saved your request and will send data over provided email ID within 24 hours."); }, 500); 
                  }else{
                      if(response["export_path_exist"]){
                        window.open(response["export_path"], "_blank");
                      }else{
                        alert("Requested data doesn't exists. Kindly try again later.");
                      }
                  }
              }
            },
            error: function(xhr, textstatus, errorthrown) {
                console.log("Please report this error: "+errorthrown+xhr.status+xhr.responseText);
            }
        });
    }
});

$('#export-mis-keyword').click(function(){

    is_keyword = "Yes"
    keyword_str = $('#keyword_str').val();
    startdate = ""
    enddate = ""
    filter = ""
    bot_pk = document.getElementById('selected-bot-message-history').value;
    bot_name = "All"

    if (bot_pk!="None"){
      bot_name = document.getElementById('selected-bot-message-history').selectedOptions[0].label
    }

    email_field = document.getElementById('filter-data-keyword-email');    

    if(validateEmail(email_field)==false){
      M.toast({"html": 'Please enter valid email ID'}, 4000, "rounded");
      return;
    }

    if(keyword_str==""){
        Materialize.toast('Please enter keywords', 4000, "rounded")
    }else{
        var json_string = JSON.stringify({
            "is_keyword" : is_keyword,
            "keyword_str": keyword_str,
            "startdate": startdate,
            "enddate": enddate,
            "filter": filter,
            "email": email_field.value,
            "bot_name": bot_name
        })
        json_string = EncryptVariable(json_string);
        $.ajax({
            url: "/chat/exportdata/",
            type: "POST",
            data: {
                json_string: json_string
            },
            success: function(response) {
              response = custom_decrypt(response);
              response = JSON.parse(response);
              if(response["status"]=200){
                  $("#modal-mis-keyword").modal("close");
                  alert(response['message']);
              }
              else if(response["status"]=404){
                  $("#modal-mis-keyword").modal("close");
                  alert(response['message'])
              }
            },
            error: function(xhr, textstatus, errorthrown) {
                console.log("Please report this error: "+errorthrown+xhr.status+xhr.responseText);
            }
        });
    }
});

function showMonthlyAnalytics(bots_pk,bot_type){
    var json_string = JSON.stringify({
        bots_pk : JSON.stringify(bots_pk),
        bot_type : bot_type,
    })
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: "/chat/get-monthly-analytics/",
        type: "POST",
        data: {
          json_string: json_string
        },
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response)
            month_list = response["sorted_month_list"];
            user_frequency_list = [];
            message_frequency_list = [];

            user_frequency_max = 0;
            message_frequency_max = 0;

            for (var i = 0; i < month_list.length; i++) {
                month = month_list[i];

                user_frequency_max = Math.max(user_frequency_max, response["user_frequency"][month]);
                message_frequency_max = Math.max(message_frequency_max, response["message_frequency"][month]);

                user_frequency_list.push(response["user_frequency"][month]);
                message_frequency_list.push(response["message_frequency"][month]);
            }

            user_step_size = Math.ceil(user_frequency_max/5.0);
            message_step_size = Math.ceil(message_frequency_max/5.0);

            // drawChart("monthly-user-bar-chart", "Month", "No of Unique Users", "", month_list, user_frequency_list, user_step_size)
            // drawChart("monthly-message-bar-chart", "Month", "No of Messages", "", month_list, message_frequency_list, message_step_size)

            new Chart(document.getElementById("monthly-user-message-analytics"), {
                type: 'line',
                data:{
                  labels: month_list,
                  datasets: [{
                      label: "Monthly Unique Number of Users",
                      fill: true,
                      lineTension: 0.1,
                      // backgroundColor: "#FFFDE7",
                      borderColor: "#4527a0",
                      borderCapStyle: 'butt',
                      borderDash: [],
                      borderDashOffset: 0.0,
                      borderJoinStyle: 'miter',
                      pointBorderColor: "white",
                      pointBackgroundColor: "black",
                      pointBorderWidth: 1,
                      pointHoverRadius: 8,
                      pointHoverBackgroundColor: "brown",
                      pointHoverBorderColor: "yellow",
                      pointHoverBorderWidth: 2,
                      pointRadius: 4,
                      pointHitRadius: 10,
                      // notice the gap in the data and the spanGaps: false
                      data: user_frequency_list,
                      spanGaps: false,
                    },{
                      label: "Number of Messages received monthly",
                      fill: true,
                      lineTension: 0.1,
                      // backgroundColor: "#FFFDE7",
                      borderColor: "#2e7d32",
                      borderCapStyle: 'butt',
                      borderDash: [],
                      borderDashOffset: 0.0,
                      borderJoinStyle: 'miter',
                      pointBorderColor: "white",
                      pointBackgroundColor: "black",
                      pointBorderWidth: 1,
                      pointHoverRadius: 8,
                      pointHoverBackgroundColor: "brown",
                      pointHoverBorderColor: "yellow",
                      pointHoverBorderWidth: 2,
                      pointRadius: 4,
                      pointHitRadius: 10,
                      // notice the gap in the data and the spanGaps: false
                      data: message_frequency_list,
                      spanGaps: false,
                    }]
                },
                options: {
                    responsive: true,
                    legend: { display: true },
                    title: {
                        display: true,
                        text: "Monthly Analytics"
                    },
                    scales: {
                        yAxes: [{
                            ticks: {
                                display: true,
                                labelString: "No of users",
                                beginAtZero:true,
                                stepSize: Math.max(user_step_size, message_step_size),
                            }
                        }]
                    }
                }
            });

            getUserFeedback(bots_pk, bot_type);
            get_user_time_spent();
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: "+errorthrown+xhr.status+xhr.responseText);
        }
    });
}

 var dynamicColors = function() {
    var r = Math.floor(Math.random() * 255);
    var g = Math.floor(Math.random() * 255);
    var b = Math.floor(Math.random() * 255);
    return "rgb(" + r + "," + g + "," + b + ")";
 };

function renderIntentInformation(intent_frequency)
{
    if(intent_frequency.length!=0)
    {
        intent_name_list = []
        intent_frequency_list = []
        random_color_list = []

        iter_len = Math.min(5, intent_frequency.length)

        for(var i=0;i<iter_len;i++)
        {
            var intent_name = intent_frequency[i]["intent_name"];
            if(intent_name==null){
                intent_name = "Not identified"
            }

            intent_name_list.push(intent_name);
            intent_frequency_list.push(intent_frequency[i]["frequency"]);
            random_color_list.push(dynamicColors());
        }

        intent_pie_data = {
            datasets: [{
                fill: true,
                backgroundColor: random_color_list,
                data: intent_frequency_list
            }],

            // These labels appear in the legend and in the tooltips when hovering different arcs
            labels: intent_name_list
        };

        var options = {
            title: {
                      display: true,
                      text: 'Intent Analytics',
                      position: 'top'
                  }
            }

        var canvas = document.getElementById("intent-analytics");

        var piechart = new Chart(canvas.getContext('2d'),{
            type: 'doughnut',
            data: intent_pie_data,
            options: options
        });

        $("#div-intent-analytics").show();
    }
}

function isDictEmpty(dict){
    for(var key in dict){
        return false;
    }
    return true;
}

function renderChannelInformation(message_by_channel){

    if(!isDictEmpty(message_by_channel))
    {
        channel_list = []
        frequency_list = []
        random_color_list = []

        for(var channel in message_by_channel)
        {
            channel_list.push(channel);
            frequency_list.push(message_by_channel[channel]);
            random_color_list.push(dynamicColors());
        }

        channel_pie_data = {
            datasets: [{
                fill: true,
                backgroundColor: random_color_list,
                data: frequency_list
            }],

            // These labels appear in the legend and in the tooltips when hovering different arcs
            labels: channel_list
        };

        var options = {
            title: {
                      display: true,
                      text: 'Channel Analytics',
                      position: 'top'
                  }
            }

        var canvas = document.getElementById("channel-analytics");

        var piechart = new Chart(canvas.getContext('2d'),{
            type: 'doughnut',
            data: channel_pie_data,
            options: options
        });

        $("#div-channel-analytics").show();
    }    
}

$('#show-analytics-btn').click(function(){
    selected_bot_pk_list = $("#multiple-select-bot-choice-pk-list").val();
    setTimeout(function(){
        showDailyAnalytics(selected_bot_pk_list);
    }, 500);
});

function showDailyAnalytics(bots_pk){
    showAnalyticsPreloader();
    Chart.helpers.each(Chart.instances, function(instance){
       instance.destroy()
    })
    // bots_type = $('#bots_type').val()
    list = document.getElementsByName("bot-type-group")
    var bot_type=null;
    
    for(bot_type=0;bot_type<list.length;bot_type++)
    {
        if(list[bot_type].checked){
            bot_type = list[bot_type].id
            break
        }
    }
    var json_string = JSON.stringify({
        bots_pk : JSON.stringify(bots_pk),
        bot_type : bot_type,
    })
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: "/chat/get-daily-analytics/",
        type: "POST",
        data: {
          json_string: json_string
        },
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response)
            bot_names = response['bot_names']
            bot_names_string = "<h6>Showing analytics for Bots -> <b>"
            
            for(var i=0;i<bot_names.length;i++){
              bot_names_string+=bot_names[i]+", "
            }

            bot_names_string = bot_names_string.substring(0, bot_names_string.length - 2);
            bot_names_string+=".</h6></b>"

            $("#show-analytics-bots-name").html(bot_names_string)
            day_list = response["sorted_day_list"];
            message_by_channel = response["message_by_channel"][day_list[day_list.length-1]];
            intent_frequency = response["intent_frequency"][day_list[day_list.length-1]];

            renderIntentInformation(intent_frequency);
            renderChannelInformation(message_by_channel);

            user_frequency_list = [];
            message_frequency_list = [];
            count_unanswered_list = [];
            count_answered_list = [];
            total_message_list = [];

            user_frequency_max = 0;
            message_frequency_max = 0;
            count_answered_max = 0;
            count_unanswered_max = 0;
            total_message_max = 0;
            var total_answered_messages = 0;
            var total_unanswered_messages = 0;

            for (var i = 0; i < day_list.length; i++) {
                str_day = day_list[i];
                var total_message = response["answered"][str_day] + response["unanswered_message"][str_day];

                user_frequency_max = Math.max(user_frequency_max, response["user_frequency"][str_day]);
                message_frequency_max = Math.max(message_frequency_max, response["message_frequency"][str_day]);
                count_answered_max = Math.max(count_answered_max, response["answered"][str_day]);
                count_unanswered_max = Math.max(count_unanswered_max, response["unanswered_message"][str_day]);
                total_message_max = Math.max(total_message_max, total_message);

                user_frequency_list.push(response["user_frequency"][str_day]);
                message_frequency_list.push(response["message_frequency"][str_day]);
                count_answered_list.push(response["answered"][str_day]);
                count_unanswered_list.push(response["unanswered_message"][str_day]);
                total_message_list.push(total_message);

                total_answered_messages += response["answered"][str_day];
                total_unanswered_messages += response["unanswered_message"][str_day];
            }

            user_frequency_step = Math.ceil(user_frequency_max/5.0);
            message_frequency_step = Math.ceil(message_frequency_max/5.0);
            answered_step = Math.ceil(count_answered_max/5.0);
            unanswered_step = Math.ceil(count_unanswered_max/5.0);
            total_message_step = Math.ceil(total_message_max/5.0);

            document.getElementById("number-of-messages-today").innerHTML = message_frequency_list[day_list.length-1];
            document.getElementById("number-of-users-today").innerHTML = user_frequency_list[day_list.length-1];

            $("#number-of-messages-today").each(function () {
                $(this).prop('Counter',0).animate({
                    Counter: $(this).text()
                }, {
                    duration: 500,
                    easing: 'swing',
                    step: function (now) {
                        $(this).text(Math.ceil(now));
                    }
                });
            });

            $("#number-of-users-today").each(function () {
                $(this).prop('Counter',0).animate({
                    Counter: $(this).text()
                }, {
                    duration: 500,
                    easing: 'swing',
                    step: function (now) {
                        $(this).text(Math.ceil(now));
                    }
                });
            });


            // drawChart("daily-user-bar-chart", "Days", "No of Unique Users", "", day_list, user_frequency_list, user_frequency_step);
            // drawChart("daily-message-bar-chart", "Days", "No of Messages", "", day_list, message_frequency_list, message_frequency_step);
            // drawChart("daily-unanswered-bar-chart", "Days", "No of Unanswered Messages", "", day_list, count_unanswered_list, unanswered_step);
            // drawChart("daily-answered-bar-chart", "Days", "No of Answered Messages", "", day_list, count_answered_list, answered_step);

            new Chart(document.getElementById("daily-user-analytics"), {
                type: 'line',
                data:{
                  labels: day_list,
                  datasets: [{
                      label: "Daily Unique Number of Users",
                      fill: true,
                      lineTension: 0.1,
                      // backgroundColor: "#FFFDE7",
                      borderColor: "#2e7d32",
                      borderCapStyle: 'butt',
                      borderDash: [],
                      borderDashOffset: 0.0,
                      borderJoinStyle: 'miter',
                      pointBorderColor: "white",
                      pointBackgroundColor: "black",
                      pointBorderWidth: 1,
                      pointHoverRadius: 8,
                      pointHoverBackgroundColor: "brown",
                      pointHoverBorderColor: "yellow",
                      pointHoverBorderWidth: 2,
                      pointRadius: 4,
                      pointHitRadius: 10,
                      // notice the gap in the data and the spanGaps: false
                      data: user_frequency_list,
                      spanGaps: false,
                    }]
                },
                options: {
                    responsive: true,
                    legend: { display: true },
                    title: {
                        display: true,
                        text: "Daily User analytics"
                    },
                    scales: {
                        yAxes: [{
                            ticks: {
                                display: true,
                                labelString: "No of users",
                                beginAtZero:true,
                                stepSize: Math.max(answered_step, unanswered_step),
                            }
                        }]
                    }
                }
            });

            pie_data = {
                datasets: [{
                    fill: true,
                    backgroundColor: [
                            '#388e3c',
                            '#d32f2f'],
                    data: [total_answered_messages, total_unanswered_messages]
                }],

                // These labels appear in the legend and in the tooltips when hovering different arcs
                labels: [
                    'No of answered messages',
                    'No of unanswered messages'
                ]
            };

            var options = {
                title: {
                          display: true,
                          text: 'Messages Analytics for last 6 months',
                          position: 'top'
                      }
                }

            var canvas = document.getElementById("daily-message-piechart-analytics");

            var piechart = new Chart(canvas.getContext('2d'),{
                type: 'doughnut',
                data: pie_data,
                options: options
            });

            new Chart(document.getElementById("daily-message-analytics"), {
                type: 'line',
                data:{
                  labels: day_list,
                  datasets: [{
                      label: "Total Number of Messages",
                      fill: true,
                      lineTension: 0.1,
                      // backgroundColor: "#FFFDE7",
                      borderColor: "#2e7d32",
                      borderCapStyle: 'butt',
                      borderDash: [],
                      borderDashOffset: 0.0,
                      borderJoinStyle: 'miter',
                      pointBorderColor: "white",
                      pointBackgroundColor: "black",
                      pointBorderWidth: 1,
                      pointHoverRadius: 8,
                      pointHoverBackgroundColor: "brown",
                      pointHoverBorderColor: "yellow",
                      pointHoverBorderWidth: 2,
                      pointRadius: 4,
                      pointHitRadius: 10,
                      // notice the gap in the data and the spanGaps: false
                      data: total_message_list,
                      spanGaps: false,
                    },{
                      label: "No of Answered Messages",
                      fill: false,
                      lineTension: 0.1,
                      // backgroundColor: "#EDE7F6",
                      borderColor: "#4527a0",
                      borderCapStyle: 'butt',
                      borderDash: [],
                      borderDashOffset: 0.0,
                      borderJoinStyle: 'miter',
                      pointBorderColor: "white",
                      pointBackgroundColor: "black",
                      pointBorderWidth: 1,
                      pointHoverRadius: 8,
                      pointHoverBackgroundColor: "brown",
                      pointHoverBorderColor: "yellow",
                      pointHoverBorderWidth: 2,
                      pointRadius: 4,
                      pointHitRadius: 10,
                      // notice the gap in the data and the spanGaps: false
                      data: count_answered_list,
                      spanGaps: false,
                    },{
                      label: "No of Unanswered Messages",
                      fill: false,
                      lineTension: 0.1,
                      // backgroundColor: "#FFFDE7",
                      borderColor: "#ef6c00",
                      borderCapStyle: 'butt',
                      borderDash: [],
                      borderDashOffset: 0.0,
                      borderJoinStyle: 'miter',
                      pointBorderColor: "white",
                      pointBackgroundColor: "black",
                      pointBorderWidth: 1,
                      pointHoverRadius: 8,
                      pointHoverBackgroundColor: "brown",
                      pointHoverBorderColor: "yellow",
                      pointHoverBorderWidth: 2,
                      pointRadius: 4,
                      pointHitRadius: 10,
                      // notice the gap in the data and the spanGaps: false
                      data: count_unanswered_list,
                      spanGaps: false,
                    }]
                },
                options: {
                    responsive: true,
                    legend: { display: true },
                    title: {
                        display: true,
                        text: "Messages Analytics"
                    },
                    scales: {
                        yAxes: [{
                            ticks: {
                                display: true,
                                labelString: "No of messages",
                                beginAtZero:true,
                                stepSize: Math.max(answered_step, unanswered_step),
                            }
                        }]
                    }
                }
            });

            showMonthlyAnalytics(bots_pk, bot_type);
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: "+errorthrown+xhr.status+xhr.responseText);
        }
    });
}

function show_top_intents(){
    $.ajax({
        url: "/chat/get-top-intents/",
        type: "POST",
        data: {

        },
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response)
            intent_list = response["intent_list"]
            intent_frequency_list = response["intent_frequency_list"]
            intent_step_size = response["intent_frequency_step_size"]
            drawChart("top-intent-bar-chart", "Frequency", "Intent Name", "", intent_list, intent_frequency_list, intent_step_size)
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: "+errorthrown+xhr.status+xhr.responseText);
        }
    });
}

function getUserFeedback(bots_pk, bot_type){  
    var json_string = JSON.stringify({
        bots_pk : JSON.stringify(bots_pk),
        bot_type : bot_type,
    })
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: "/chat/get-feedback/",
        type: "POST",
        data: {
          json_string: json_string
        },
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response)
            // console.log(response)
            positive_feedback = response["promoter_feedback"];
            negative_feedback = response["demoter_feedback"];
            total_sentences = response["total_feedback"];
            
            if(total_sentences!=0){
              positive_feedback = Math.round(((positive_feedback-negative_feedback)*100)/total_sentences);              
            }
            
            document.getElementById("positive-feedback").innerHTML = positive_feedback;

            $("#positive-feedback").each(function () {
                $(this).prop('Counter',0).animate({
                    Counter: $(this).text()
                }, {
                    duration: 500,
                    easing: 'swing',
                    step: function (now) {
                        $(this).text(Math.ceil(now));
                    }
                });
            });

            hideAnalyticsPreloader();
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: "+errorthrown+xhr.status+xhr.responseText);
        }
    });
}

function get_user_time_spent(){
    $.ajax({
        url: "/chat/get-user-time-spent/",
        type: "POST",
        data: {
        },
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response)
            total_time = response["total_time"];
            user_count = response["user_count"];

            var average_time_spent = 0;
            var time_minutes = 0;
            var time_second = 0;
            if(total_time!=0){
                
                average_time_spent = Math.round(total_time/user_count);
                time_minutes = Math.floor(average_time_spent/60);
                time_second = average_time_spent - (time_minutes*60);             
            }
            
            document.getElementById("average-time-spent-min").innerHTML = time_minutes;
            document.getElementById("average-time-spent-sec").innerHTML = time_second;

            $("#average-time-spent-min").each(function () {
                $(this).prop('Counter',0).animate({
                    Counter: $(this).text()
                }, {
                    duration: 500,
                    easing: 'swing',
                    step: function (now) {
                        $(this).text(Math.ceil(now));
                    }
                });
            });

            $("#average-time-spent-sec").each(function () {
                $(this).prop('Counter',0).animate({
                    Counter: $(this).text()
                }, {
                    duration: 500,
                    easing: 'swing',
                    step: function (now) {
                        $(this).text(Math.ceil(now));
                    }
                });
            });

            hideAnalyticsPreloader();
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: "+errorthrown+xhr.status+xhr.responseText);
        }
    });
}



function drawChart(element_id, x_label, y_label, text, x_list, y_list, steps){

    var bg_color = new Array(x_list.length)
    for (var i=0;i<bg_color.length;i++){
        bg_color[i]="#3e95cd"
    }
    // Bar chart
    new Chart(document.getElementById(element_id), {
        type: 'line',
        data:{
          labels: x_list,
          datasets: [{
              label: y_label,
              fill: true,
              lineTension: 0.1,
              backgroundColor: "#EDE7F6",
              borderColor: "#512DA8",
              borderCapStyle: 'butt',
              borderDash: [],
              borderDashOffset: 0.0,
              borderJoinStyle: 'miter',
              pointBorderColor: "white",
              pointBackgroundColor: "black",
              pointBorderWidth: 1,
              pointHoverRadius: 8,
              pointHoverBackgroundColor: "brown",
              pointHoverBorderColor: "yellow",
              pointHoverBorderWidth: 2,
              pointRadius: 4,
              pointHitRadius: 10,
              // notice the gap in the data and the spanGaps: false
              data: y_list,
              spanGaps: false,
            }]
        },
        options: {
            responsive: true,
            legend: { display: false },
            title: {
                display: true,
                text: text
            },
            scales: {
                yAxes: [{
                    ticks: {
                        display: true,
                        labelString: y_label,
                        beginAtZero:true,
                        stepSize: steps,
                    }
                }]
            }
        }
    });
}


function download_flow_analytics(intent_pk){
    flow_analytics_filter_result = check_flow_analytics_filter_values();
    start_date = flow_analytics_filter_result.start_date;
    end_date = flow_analytics_filter_result.end_date;
    channel_list = flow_analytics_filter_result.channel_list;
    selected_language = get_url_vars()["selected_language"]
    if(typeof selected_language == 'undefined'){
        selected_language = get_url_vars()["dropdown_language"]
    }

    if(Date.parse(start_date) > Date.parse(end_date)){
        M.toast({
            "html": "Start date cannot be less than end date."
        }, 2000);
        return;
    }
    window.location = "/chat/download-flow-analytics/?intent_pk="+intent_pk+"&startdate="+start_date+"&enddate="+end_date+"&channel="+channel_list + "&selected_language=" + selected_language
}


function download_user_specific_dropoff_analytics(intent_pk){
    flow_analytics_filter_result = check_flow_analytics_filter_values();
    start_date = flow_analytics_filter_result.start_date;
    end_date = flow_analytics_filter_result.end_date;
    channel_list = flow_analytics_filter_result.channel_list;
    dropdown_language = get_url_vars()["dropdown_language"]

    if(Date.parse(start_date) > Date.parse(end_date)){
        M.toast({
            "html": "Start date cannot be less than end date."
        }, 2000);
        return;
    }
    window.location = "/chat/download-user-specific-dropoff-analytics/?intent_pk="+intent_pk+"&startdate="+start_date+"&enddate="+end_date+"&channel="+channel_list+"&dropdown_language="+dropdown_language
}


function apply_date_filter(intent_id,first_object_created_date,last_object_created_date) {
    date_start = $("#date_start").val();
    date_end = $("#date_end").val();
    if (date_start != "" && date_end!=""){
        date_start = Date.parse(date_start)
        date_end = Date.parse(date_end)
        first_object_created_date_parsed = Date.parse(first_object_created_date)
        last_object_created_date_parsed = Date.parse(last_object_created_date)
        bot_pk = $('#flow_analytics_bot_id').val()

        if (date_start<=date_end && date_end>=first_object_created_date_parsed ){
            date_start = $("#date_start").val();
            date_end = $("#date_end").val();
            window.location = "/chat/flow-analytics/?intent_pk="+intent_id+"&start_date="+date_start+"&date_end="+date_end+"&bot_pk="+bot_pk
        }
        else{
            alert("Please select valid dates between "+first_object_created_date +" and "+ last_object_created_date)
        }
    }
    else{
        alert("Please select all dates")
    }
    
};

function check_flow_analytics_filter_values(){
    channel_list = [];
    start_date = "";
    end_date = "";
    flow_analytics_date_filter_value = "";
    flow_analytics_channel_filter_value = [];
    dropdown_language = get_url_vars()["dropdown_language"]
    if(document.getElementById('date_range_1').checked){
        start_date = document.getElementById("date_range_1").getAttribute('start_date_value');
        end_date = document.getElementById("date_range_1").getAttribute('end_date_value');
        flow_analytics_date_filter_value = "date_range_1";
    }
    else if(document.getElementById('date_range_2').checked){
        start_date = document.getElementById("date_range_2").getAttribute('start_date_value');
        end_date = document.getElementById("date_range_2").getAttribute('end_date_value');
        flow_analytics_date_filter_value = "date_range_2";
    }
    else if(document.getElementById('date_range_3').checked){
        start_date = document.getElementById("date_range_3").getAttribute('start_date_value');
        end_date = document.getElementById("date_range_3").getAttribute('end_date_value');
        flow_analytics_date_filter_value = "date_range_3";           
    }
    else if(document.getElementById('date_range_4').checked){
        start_date = document.getElementById("date_range_4").getAttribute('start_date_value');
        end_date = document.getElementById("date_range_4").getAttribute('end_date_value');
        flow_analytics_date_filter_value = "date_range_4";              
    }
    else if(document.getElementById('date_range_5').checked){
        start_date = document.getElementById("custom_start_date").value;
        end_date = document.getElementById("custom_end_date").value;
        flow_analytics_date_filter_value = "date_range_5";                
    }

    var channels_elems = document.querySelectorAll('.flow-analytics-channel-checkbox');

    channels_elems.forEach(function(channel) {
        if (channel.checked) {
            channel_list.push(channel.id)
        }
    })

    return {
        start_date,
        end_date,
        channel_list,
        dropdown_language
    };
}

function redirect_to_intent_page(intent_pk, tree_pk, parent_pk, level){
    if(tree_pk == parent_pk)
        window.open("/chat/edit-intent/?intent_pk="+intent_pk, "_blank")
    else if (document.cookie.match(/edit_intent_ui=old/)) {
        window.open("/chat/edit-tree/?intent_pk="+intent_pk+"&parent_pk="+parent_pk+"&tree_pk="+tree_pk, "_blank") 
    } else
        window.open("/chat/edit-intent/?intent_pk="+intent_pk+"&tree_pk="+tree_pk, "_blank")
}

function load_flow_analytics(intent_id, bot_pk){

    flow_analytics_filter_result = check_flow_analytics_filter_values();
    start_date = flow_analytics_filter_result.start_date;
    end_date = flow_analytics_filter_result.end_date;
    channel_list = flow_analytics_filter_result.channel_list;
    dropdown_language = flow_analytics_filter_result.dropdown_language;

    if(Date.parse(start_date) > Date.parse(end_date)){
        M.toast({
            "html": "Start date cannot be less than end date."
        }, 2000);
        return;
    }

    window.location = "/chat/flow-analytics/?intent_pk="+intent_id+"&bot_pk="+bot_pk+"&start_date="+start_date+"&date_end="+end_date+"&channel="+channel_list+"&date_filter="+flow_analytics_date_filter_value+"&channel_filter="+channel_list+"&dropdown_language="+dropdown_language
}

function set_flow_analytics_filter(){
    date_filter = window.date_filter;
    channel_filter = window.channel_filter;

    if(date_filter != null && date_filter != undefined && date_filter != ""){
        date_filter = date_filter.trim()
        document.getElementById(date_filter).checked = true;
        if(date_filter == "date_range_5"){
            document.getElementById("analytics-custom-date-select-area").style.display = "block";
            var url = new URL(window.location.href);
            var start_date = url.searchParams.get("start_date");
            var end_date = url.searchParams.get("date_end");
            document.getElementById("custom_start_date").value = start_date;
            document.getElementById("custom_end_date").value = end_date;
        } 
    }
    if(channel_filter != null && channel_filter != undefined && channel_filter != "") {

        for(let i =0;i<channel_filter.length;i++) {

            if(channel_filter[i] != null && channel_filter[i] != undefined && channel_filter[i] != "") {
                
                document.getElementById(channel_filter[i]).checked = true;
            }
        }
    }
}

function reset_flow_analytics_filter(intent_id, default_start_date, default_end_date, bot_pk) {
    window.location = "/chat/flow-analytics/?intent_pk="+intent_id+"&bot_pk="+bot_pk+"&start_date="+default_start_date+"&date_end="+default_end_date+"&date_filter=date_range_1"+"&dropdown_language="+get_url_vars()["dropdown_language"]
}

function check_flow_analytics_filter(){
    var value = document.getElementById("check-flow-analytics-filter-select").value;
    if(value == "1"){
        document.getElementById("div-flow-analytics-channels").style.display = "block"
        document.getElementById("div-flow-analytics-date").style.display = "none"
        document.getElementById("modal-message-default-settings-custom-flow").style.display = "none"

    }else if(value == "2"){
        document.getElementById("div-flow-analytics-channels").style.display = "none"
        document.getElementById("div-flow-analytics-date").style.display = "block"

    }
}
function disable_future_date(){
    var dtToday = new Date();

    var month = dtToday.getMonth() + 1;
    var day = dtToday.getDate();
    var year = dtToday.getFullYear();
    if(month < 10)
        month = '0' + month.toString();
    if(day < 10)
        day = '0' + day.toString();

    var maxDate = year + '-' + month + '-' + day;
    $("[type='date']").attr("max", maxDate)
}
function add_flow_analytics_filter_option(value){
    if(!set_initial_filter){
        var value = document.getElementById("check-flow-analytics-filter-select").value;
    }
    if(value == ""){
        showToast("Kindly select a valid filter", 2000);
        return;
    }
    if(value == "1"){
        channel_value = document.getElementById("select-flow-analytics-channels-filter").value;
        if(channel_value == ""){
            showToast("Kindly select a valid filter", 2000);
            return;
        }
        
        var flag = false;
        try{
            val = document.getElementById("add-flow-analytics-channels-key").value
            flag = false
        }catch{
            flag = true
        }
        if(flag == true){
            if(value != "" && channel_value != ""){
                html = '<div class="row" id="flow-analytics-filter-channels-div"><br><div class="col s4">'
                html += '<input id="add-flow-analytics-channels-key" value="Filter by Channel" disabled>'
                html += '</div>'
                html += '<div class="col s4">'
                html += '<input id="add-flow-analytics-channels-value" value= " '+ channel_value +' " disabled>'
                html += '</div><a class="red-text text-darken-3" onclick="delete_flow_analytics_channels_filter_option()"><i class="material-icons">delete</i></a></div>'
                div_html = document.getElementById("add-flow-analytics-filter-buttons")
                div_html.insertAdjacentHTML('beforeend', html);
                flow_analytics_filter_value.push(value);
            }
            else{
                showToast("Kindly select a valid filter.", 2000);
                return;
            }
        }
        else{
              showToast("This filter is already present.", 2000);
              return;
        }
      }
    else if(value == "2"){
        date_filter_value = document.getElementById("modal-message-default-settings-type-flow").value;
        flow_analytics_date_filter_value = date_filter_value
        if(date_filter_value == ""){
            showToast("Kindly select a valid filter", 2000);
            return;
        }
        date_filter_text = $("#modal-message-default-settings-type-flow option:selected").text()
        var start_date_elm = document.getElementsByClassName("message-default-start-date-flow")[0]
        var start_date = start_date_elm.value;
          if(start_date == ""){
              showToast("Kindly enter a start date.", 2000);
              return;
          }
        var end_date_elm = document.getElementsByClassName("message-default-end-date-flow")[0]
        var end_date = end_date_elm.value;
        if(end_date == ""){
              showToast("Kindly enter a end date.", 2000);
          return;
        }
        var flag = false;
        try{
            val = document.getElementById("add-flow-analytics-date-key").value
            flag = false
        }catch{
            flag = true
        }
        value_last_month = start_date_elm.getAttribute('value_last_month')
        value_last3 = start_date_elm.getAttribute('value_last3')
        value_golive = start_date_elm.getAttribute('value_golive')
        if(flag == true){
            if(value != "" && date_filter_value != ""){
                html = '<div class="row" id="flow-analytics-filter-date-div"><br><div class="col s4">'
                html += '<input id="add-flow-analytics-date-key" value="Filter by Date" disabled>'
                html += '</div>'
                html += '<div class="col s4"><input id="add-flow-analytics-date-value" value= " '+ date_filter_text +' " disabled></div> '
                if (date_filter_value =='custom_date'){                    
                    html += '<div class="col s8">'
                    html +='<div class="col s6">Start Date <input type="date" disabled class="message-default-start-date-flow" value="'+start_date+'" value_last_month="'+value_last_month+'" value_last3="'+value_last3+'" value_golive="'+value_golive+'"></div>'
                    html +='<div class="col s6">End Date<input type="date" disabled class="message-default-end-date-flow" value="'+end_date+'" value_last_month="'+end_date+'" value_last3="'+end_date+'" value_golive="'+end_date+'"></div>'
                    html += '</div>'
                }
                html += '<a class="red-text text-darken-3" onclick="delete_flow_analytics_date_filter_option()"><i class="material-icons">delete</i></a></div>'
                div_html = document.getElementById("add-flow-analytics-filter-buttons")
                div_html.insertAdjacentHTML('beforeend', html);
                flow_analytics_filter_value.push(value);
            }
            else{
                showToast("Kindly select a valid filter.", 2000);
                return;
            }
        }
        else{
                showToast("This filter is already present.", 2000);
                return;
            }
    }
}

function delete_flow_analytics_date_filter_option(){
    div = document.getElementById("flow-analytics-filter-date-div");
    div.parentNode.removeChild(div); 
    document.getElementsByClassName("message-default-start-date-flow")[0] = ""
    document.getElementsByClassName("message-default-end-date-flow")[0] = ""
    document.getElementById("modal-message-default-settings-type-flow").value = ""
    $('#modal-message-default-settings-type-flow').trigger('change');
    let index = flow_analytics_filter_value.indexOf('2');
    if (index > -1) {
      flow_analytics_filter_value.splice(index, 1);
    }
}

function delete_flow_analytics_channels_filter_option(){
    div = document.getElementById("flow-analytics-filter-channels-div");
    div.parentNode.removeChild(div);
    let index = flow_analytics_filter_value.indexOf('1');
    if (index > -1) {
      flow_analytics_filter_value.splice(index, 1);
    }
}

$(document).on("change", "#modal-message-default-settings-type-flow", function(e){
    var filter_type = document.getElementById("modal-message-default-settings-type-flow").value
    document.getElementById("modal-message-default-settings-custom-flow").style.display = "none"
    elems = document.getElementsByClassName("message-default-start-date-flow")
    if (filter_type == "last_month"){
    document.getElementsByClassName("message-default-start-date-flow")[elems.length-1].value = document.getElementsByClassName("message-default-start-date-flow")[elems.length-1].getAttribute("value_last_month")

    }
    else if (filter_type == "last_3_months"){
    document.getElementsByClassName("message-default-start-date-flow")[elems.length-1].value = document.getElementsByClassName("message-default-start-date-flow")[elems.length-1].getAttribute("value_last3")

    }
    else if (filter_type == "since_go_live"){
    document.getElementsByClassName("message-default-start-date-flow")[elems.length-1].value = document.getElementsByClassName("message-default-start-date-flow")[elems.length-1].getAttribute("value_golive")

    }
    else if (filter_type == "custom_date"){
    document.getElementById("modal-message-default-settings-custom-flow").style.display = "block"
    document.getElementsByClassName("message-default-start-date-flow")[elems.length-1].value = document.getElementsByClassName("message-default-start-date-flow")[elems.length-1].getAttribute("value")

    }
    

});
// /////////////////////////////////////////////////////// Message-History JS Start
// ////////////////////////////////////////////////////// Message-History JS Start

// function get_message_history_table(response)
// {
//   // console.log("Response is ", response);
//   user_query = response['user_query'];
//   bot_response = response['bot_response'];
//   time_sent = response['time_sent'];
//   intent_name = response['intent_name'];
//   intent_pk = response["intent_pk"];
//   user_id = response['user_id'];
//   channel = response['channel'];


//   var html_table = `

//     <table id="message-history-info-table" class="striped highlight responsive-table white" style="margin-top:2%;">
//         <thead>
//             <tr>
//                 <th>User Query</th>
//                 <th>Bot Response</th>
//                 <th>Time</th>
//                 <th>Intent Recognized</th>
//                 <th>User ID</th>
//                 <th>Channel</th>
//             </tr>
//         </thead>
//         <tbody>`;

//         for(var i=0;i<user_query.length;i++){

//             id = user_id[i].slice(-10);

//             html_table += `<tr>
//                 <td>`+user_query[i]+`</td>
//                 <td>`+bot_response[i]+`</td>
//                 <td>`+time_sent[i]+`</td>`

//                 if(intent_pk[i]!=-1)
//                 {
//                     html_table += `<td><a href="/chat/edit-intent/?intent_pk=`+intent_pk[i]+`">`+intent_name[i]+`</a></td>`;
//                 }
//                 else
//                 {
//                     html_table += `<td>`+intent_name[i]+`</td>`;
//                 }

//                 html_table += `<td><a href="/chat/user-details/`+user_id[i]+`" target="_blank">`+id+`</a></td>
//                 <td>`+channel[i]+`</td>
//             </tr>`;
//         }    
        
//         html_table += `</tbody>
//     </table>`;

//     return html_table;
// }

// function load_message_history()
// {
//   $.ajax({
//       url: '/chat/fetch-message-history/',
//       type: "POST",
//       data: {
//       },
//       success: function(data){
//         console.log(data);
//         html_table = get_message_history_table(data);
//         $("#main-console-container").html(html_table);
//       }
//   });
// }

/////////////////////////////////////////////////////// Message-History JS End

// if(window.location.pathname.indexOf("/chat/user-details/")!=-1)
// {
//     user_id = window.location.pathname.split("/chat/user-details/")[1];

//     $.ajax({
//         url: "/chat/get-user-details/",
//         type: "POST",
//         data: {
//             user_id:user_id
//         },
//         success: function(response) {

//             date_list = response["date_list"]
//             user_id_list = response["user_id_list"]
//             message_received_list = response["message_received_list"]
//             bot_response_list = response["bot_response_list"]
//             intent_name_list = response["intent_name_list"]
//             channel_name_list = response["channel_name_list"]
//             api_request_packet_list = response["api_request_packet_list"]
//             api_response_packet_list = response["api_response_packet_list"]

//             html_table = `<p class="white" style="padding:1em;">No data available</p>`;

//             if(date_list.length!=0)
//             {
//                 user_id_str = user_id_list[0].slice(-10);

//                 html_table = `
//                     <div class="col s12 z-depth-1" style="margin-top:1em;">
//                         <div class="col s6 center-align" style="padding:1em;">Messages from `+user_id_str+`</div>
//                         <div class="col s6 center-align" style="padding:1em;">Channel: `+channel_name_list[0]+`</div>
//                     </div>

//                     <div class="col s12 z-depth-1" style="margin-top:1em;">
//                     <table class="striped highlight responsive-table" style="table-layout: fixed; width: 100%">
//                     <thead>
//                         <tr>
//                             <th>Date</th>
//                             <th>User Query</th>
//                             <th>Bot Response</th>
//                             <th>Intent Recognized</th>
//                             <!-- <th>Channel</th>
//                             <th>User ID</th>-->
//                         </tr>
//                     </thead>
//                     <tbody>`;

//                     for(var i=0;i<date_list.length;i++)
//                     {
//                         str_date = date_list[i];
//                         // str_date = str_date.slice(0, -8);
//                         user_id = user_id_list[i];
//                         user_id = user_id.slice(-10);

//                         html_table += `
//                             <tr>
//                                 <td>`+str_date+`</td>
//                                 <td>`+message_received_list[i]+`</td>
//                                 <td style="word-wrap: break-word">`+bot_response_list[i]+`</td>
//                                 <td>`+intent_name_list[i]+`</td>
//                                 <!-- <td>`+channel_name_list[i]+`</td>
//                                 <td><a href="/chat/user-details/`+user_id_list[i]+`">`+user_id+`</a></td> -->
//                             </tr>`;
//                     }
//                     html_table += `</tbody></table></div>`;
//             }

//             $("#user-details-content").html(html_table);
//         },
//         error: function(xhr, textstatus, errorthrown) {
//             console.log("Please report this error: "+errorthrown+xhr.status+xhr.responseText);
//         }
//     });

// }

// /////////////////////////////////////////////////////////////////////// MIS Dashboard

// function load_mis_dashboard_container(){
//     html = `
//         <div class="row" style="margin-top:2%">
//             <a class="waves-effect waves-light btn purple darken-2 modal-trigger" href="#modal-mis-filter">Export With Dates</a>
//             <a class="waves-effect waves-light btn purple darken-2 modal-trigger" href="#modal-mis-keyword">Export with Keywords</a>
//         </div> 

//         <div class="row">        
//             <div class="col s12">
//                 <table id="show_mis_dashboard" class="striped highlight responsive-table">
//                 </table>           
//             </div>
//         </div>`

//     $("#main-console-container").html(html);
// }

// function show_mis_dashboard(){
    
//     $.ajax({
//         url: "/chat/get-mis-dashboard/",
//         type: "POST",
//         data: {
//         },
//         success: function(response) {
//             date_list = response["date_list"]
//             user_id_list = response["user_id_list"]
//             message_received_list = response["message_received_list"]
//             bot_response_list = response["bot_response_list"]
//             intent_name_list = response["intent_name_list"]
//             intent_pk_list = response["intent_pk_list"]
//             channel_name_list = response["channel_name_list"]
//             api_request_packet_list = response["api_request_packet_list"]
//             api_response_packet_list = response["api_response_packet_list"]

//             // dataSet = [date_list, user_id_list, message_received_list, bot_response_list, intent_name_list, channel_name_list, api_request_packet_list, api_response_packet_list];

//             // dataSet = transpose(dataSet);

//             // $('#show_mis_dashboard').DataTable({
//             //     data: dataSet,
//             //     columns: [
//             //         { title: "Date" },
//             //         { title: "User Id" },
//             //         { title: "Message Received" },
//             //         { title: "Bot response" },
//             //         { title: "Intent" },
//             //         { title: "Channel" },
//             //         { title: "API Request Packet" },
//             //         { title: "API response Packet" },
//             //     ]
//             // });
//             // 
            
//             html_table = `
//                 <thead>
//                     <tr>
//                         <th>Date</th>
//                         <th>User Query</th>
//                         <th>Bot Response</th>
//                         <th>Intent Recognized</th>
//                         <th>Channel</th>
//                         <th>User ID</th>
//                         <th>API Request Packet</th>
//                         <th>API Response Packet</th>
//                     </tr>
//                 </thead>
//                 <tbody>`;

//                 for(var i=0;i<date_list.length;i++)
//                 {
//                     html_table += `
//                         <tr>
//                             <td>`+date_list[i]+`</td>
//                             <td>`+message_received_list[i]+`</td>
//                             <td>`+bot_response_list[i]+`</td>`

//                             if(intent_pk_list[i]!=-1)
//                             {
//                                 html_table+=`<td><a href="/chat/edit-intent/?intent_pk=`+intent_pk_list[i]+`">`+intent_name_list[i]+`</a></td>`;
//                             }
//                             else
//                             {
//                                 html_table+=`<td>`+intent_name_list[i]+`</td>`;
//                             }

                            
//                             html_table+=`<td>`+channel_name_list[i]+`</td>
//                             <td><a href="/chat/user-details/`+user_id_list[i]+`" target="_blank">`+user_id_list[i].slice(-10)+`</a></td>
//                             <td>`+api_request_packet_list[i]+`</td>
//                             <td>`+api_response_packet_list[i]+`</td>
//                         </tr>`;
//                 }

//                 html_table += `</tbody></table>`;

//                 $("#mis-dashboard-info-table").html(html_table);

//         },
//         error: function(xhr, textstatus, errorthrown) {
//             console.log("Please report this error: "+errorthrown+xhr.status+xhr.responseText);
//         }
//     });
// }

// // $(document).on("click","#mis-dashboard-button", function(e){

// //////////////////////////////////////////////////////////////////////////////////

// $('#start_test').click(function(){
//     $('.upload_testdata').show();
//     $('.start_testing').hide();
// });

// $('#submit_testfaqs').click( function() {

//     var my_file = ($("#test_file"))[0].files[0]
//     var formData = new FormData();
//     formData.append("test_file", my_file);
//     // $('.indeterminate').show();
//     $('.test_processing').show();
//     $('.upload_testdata').hide();

//     $.ajax({
//         url: "/chat/get-test-analysis/",
//         type: "POST",
//         data: formData,
//         /*{
//             item_name: item_name,
//             item_amt: item_amt
//         },*/
//         processData: false,
//         contentType: false,
//         success: function(response) {
//             // $('.indeterminate').hide();
//             $('.test_processing').hide();
//             $('.start_testing').show();

//             if(response["status"]==200)
//             {
//                 console.log("Success!", response);
//                 actual_question_list = response["actual_question_list"]
//                 actual_answer_list = response["actual_answer_list"]
//                 variation_question_list = response["variation_question_list"]
//                 variation_answer_list = response["variation_answer_list"]
//                 actual_intent_list = response["actual_intent_list"]
//                 variation_intent_list = response["variation_intent_list"]
//                 score_list = response["score_list"]

//                 dataSet = [actual_question_list, variation_question_list, actual_answer_list, variation_answer_list, actual_intent_list, variation_intent_list, score_list];

//                 dataSet = transpose(dataSet);

//                 $('#show_test_results').DataTable({
//                     data: dataSet,
//                     columns: [
//                         { title: "Actual Question" },
//                         { title: "Variational Question" },
//                         { title: "Actual Answer" },
//                         { title: "Bot Answer" },
//                         { title: "Actual Intent" },
//                         { title: "Variational Intent" },
//                         { title: "Score" },
//                     ]
//                 });
//             }

//             console.log("Success fetching data!");
//         },
//         error: function(xhr, textstatus, errorthrown) {
//             console.log("Please report this error: "+errorthrown+xhr.status+xhr.responseText);
//         }
//     });
// });

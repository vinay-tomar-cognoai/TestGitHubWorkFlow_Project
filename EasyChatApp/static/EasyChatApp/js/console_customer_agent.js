(function($){
  $(function(){
    $('.sidenav').sidenav();
    $('.dropdown-trigger').dropdown();
    $('.tooltipped').tooltip();
    $('.collapsible').collapsible();
    $('.modal').modal();
    $('.tooltipped').tooltip({
        position:"top"
    });
    $('.tabs').tabs();
    $('select').select2({width: "100%"});
  }); // end of document ready
})(jQuery); // end of jQuery name space


document.body.addEventListener('keypress',function (e) {
  if(e.keyCode==13) {
    $("#login-customer-agent-btn").click();
  }
});


function getCSRFToken(){
  return $('input[name="csrfmiddlewaretoken"]').val();
}

/////////////////////////////////////////////////Customer Agent Authentication JS Start
$(document).on("click","#login-customer-agent-btn", function(e){

  username = $("#username").val();
  password = $("#password").val();
  
  CSRF_TOKEN = getCSRFToken();

  var response = $.ajax({
      url: '/chat/authentication-customer-agent/',
      type: "POST",
      headers:{
        'X-CSRFToken':CSRF_TOKEN
      },
      async: false,
      data:{
          username: username,
          password: password
      },
      success: function(response){
          
          if(response["status"]==200){
              setTimeout(function(){
                  window.location = '/chat/customer-care/';
              }, 2000);

              M.toast({"html":"Welcome, "+username}, 2000);
          }else{
              M.toast({"html":"Please check your username or password"}, 2000);
          }
      }
  }).responseJSON;

  return response;
});
/////////////////////////////////////////////Customer Agent Authentication JS End



   
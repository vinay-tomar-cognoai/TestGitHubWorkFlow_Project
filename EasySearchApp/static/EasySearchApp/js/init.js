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

function showToast(message, duration) {
    M.toast({
        "html": message, classes: 'rounded'
    }, duration);
}

function getCsrfToken() {
    var CSRF_TOKEN = $('input[name="csrfmiddlewaretoken"]').val();
    return CSRF_TOKEN;
}

/***********************************************************************************/

/* FUNCTIONS */

var query = document.getElementById("form-search");
query.addEventListener("keydown", function (e) {
    if (e.keyCode === 13) {
        validate();
    }
});

function get_url_vars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m, key, value) {
        vars[key] = value;
    });
    return vars;
}

function validate() {
    var search_query = document.getElementById("form-search").value;
    if(search_query == "" || search_query == undefined){
        var toastHTML = '<span>Please enter some query.</span>';
        showToast(toastHTML);
        return;
    }
    source = get_url_vars()["source"];
    bot_id = get_url_vars()["bot_id"];
    window.location = "/search/?source="+source+"&bot_id="+bot_id+"&query="+search_query
}
function goToDocuments(){
    var search_query = document.getElementById("form-search").value;
    if(search_query == "" || search_query == undefined){
        var toastHTML = '<span>Please enter some query.</span>';
        showToast(toastHTML);
        return;
    }
    source = get_url_vars()["source"];
    bot_id = get_url_vars()["bot_id"];
    window.location = "/search/?source="+source+'&bot_id='+bot_id+"&query="+search_query
}

function goToHome(){

    var search_query = document.getElementById("form-search").value;
    if(search_query == "" || search_query == undefined){
        var toastHTML = '<span>Please enter some query.</span>';
        showToast(toastHTML);
        return;
    }
    source = get_url_vars()["source"];
    bot_id = get_url_vars()["bot_id"];
    window.location = "/search/?source="+source+'&bot_id='+bot_id+"&query="+search_query
}


























$(document).ready(function() {

    if ($("#searchinput_country_modal").length == 0){ 
        $("#modal-country-code-wrapper .country-list").prepend("<input autocomplete='off' id='searchinput_country_modal' style='width: 100% !important; border-bottom: none !important; box-shadow: none !important;' placeholder='Search..' class='search_phone_number_widget_class'  type='text' onkeydown='filterFunctionModal(event, \"modal-country-code-wrapper\")' data-search autofocus/>");
        $("#modal-country-code-wrapper .country-list").append("<div class='country-no-result-found' id='country_no_result_found_modal'>No Results Found</div>");
        
        $("#searchinput_country_modal").focus();
        $("#searchinput_country_modal").click(function(event) {
            event.stopPropagation();
            $("#modal-country-code-wrapper .country-list").addClass("show");
        });
    }
    
});

function filterFunctionModal(event, wrapper_id) {
    var input, filter, ul, a, i;
    input = document.getElementById("searchinput_country_modal");

    a = document.querySelectorAll("#modal-country-code-wrapper .country");
    event.stopPropagation();

    setTimeout(function() {
        filter = input.value.toUpperCase().trim();
        var no_results_found = true
        for (i = 0; i < a.length; i++) {
            var txtValue = a[i].textContent || a[i].innerText;
            if (txtValue.toUpperCase().startsWith(filter)) {
                a[i].style.display = "";
                no_results_found = false
            } else {
                a[i].style.display = "none";
            }
        }
        if (filter != "") {
            $("li.country.preferred, li.divider").hide();
        } else {
            $("li.country.preferred, li.divider").show();
        }
        if (no_results_found) {
            document.querySelector("#" + wrapper_id + " .country-no-result-found").style.display = "block";
        } else {
            document.querySelector("#" + wrapper_id + " .country-no-result-found").style.display = "none";
        }
    }, 100)
    

}


var telInput = $("#phone"),
    errorMsg = $("#error-msg"),
    validMsg = $("#valid-msg");

// initialise plugin
telInput.intlTelInput({
    initialCountry: "in",

    allowExtensions: true,
    formatOnDisplay: true,
    autoFormat: true,
    autoHideDialCode: true,
    autoPlaceholder: true,
    // defaultCountry: "auto",
    ipinfoToken: "yolo",
    nationalMode: false,
    numberType: "MOBILE",
    //onlyCountries: ['us', 'gb', 'ch', 'ca', 'do'],
    preferredCountries: ['in', 'ae', 'qa', 'om', 'bh', 'kw', 'ma'],
    preventInvalidNumbers: true,
    separateDialCode: true,
});



var reset = function() {
    telInput.removeClass("error");
    errorMsg.addClass("hide");
    validMsg.addClass("hide");
};

// on keyup / change flag: reset
telInput.on("keyup change", reset);

//enable-country-code toggle
$(".enable-country-code-cb").on("change", function(event) {
    if (this.checked) {
        $(".modal-country-code-wrapper").show();

    } else {
        $('.modal-country-code-wrapper').hide();

    }
});
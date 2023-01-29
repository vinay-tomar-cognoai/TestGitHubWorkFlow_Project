$(document).ready(function(){


	if(window.api_fail_email_configured_editor + "" == "True"){

		mail_sent_to_list_editor = window.mail_sent_to_list
		$("#mail_sender_time_interval_input_editor").val(window.mail_sender_time_interval_editor)
		add_api_mailer_email_chips_data(mail_sent_to_list_editor)
		
		var html=`In case of an API Failure, an email will be sent out to `

		for(var c =0 ; c < mail_sent_to_list_editor.length; c++)
		{
			if(mail_sent_to_list_editor.length <= 3)
			{
				if(c == mail_sent_to_list_editor.length -1)
				{
					html = html + mail_sent_to_list_editor[c] + ". "
				}
				else {
					html = html + mail_sent_to_list_editor[c] +", "
				}
			} else
			{

				if(c == 2)
				{
					var count = mail_sent_to_list_editor.length - 3;
					html = html + mail_sent_to_list_editor[c] + ", +" + count + ". "
					break;

				}
				else {
					html = html + mail_sent_to_list_editor[c] +", "
				}
			} 
		}
		document.getElementById("email-config-message").innerHTML = html + `<a class="modal-trigger" href="#modal-api-fail-email-config">Configure Now</a>`;

		document.getElementById("api-mailer-btn").setAttribute('style', 'opacity:0.9;border: 1px solid #10B981;background: #ECFDF5 !important;pointer-events:none;');
		document.getElementById("api-mailer-btn").innerHTML=`<svg width="16" height="17" viewBox="0 0 16 17" fill="none" xmlns="http://www.w3.org/2000/svg">
		<path d="M8 0.5C12.4183 0.5 16 4.08172 16 8.5C16 12.9183 12.4183 16.5 8 16.5C3.58172 16.5 0 12.9183 0 8.5C0 4.08172 3.58172 0.5 8 0.5ZM8 1.5C4.13401 1.5 1 4.63401 1 8.5C1 12.366 4.13401 15.5 8 15.5C11.866 15.5 15 12.366 15 8.5C15 4.63401 11.866 1.5 8 1.5ZM11.3584 6.14645C11.532 6.32001 11.5513 6.58944 11.4163 6.78431L11.3584 6.85355L7.35355 10.8584C7.17999
		 11.032 6.91056 11.0513 6.71569 10.9163L6.64645 10.8584L4.64645 8.85842C4.45118 8.66316 4.45118 8.34658 4.64645 8.15131C4.82001 7.97775 5.08944 7.95846 5.28431 8.09346L5.35355 8.15131L7 9.798L10.6513 6.14645C10.8466 5.95118 11.1632 5.95118 11.3584 6.14645Z" fill="#059669"/>
		</svg>      
		<p>API Mailer</p>`;
		document.getElementById("api-mailer-btn").setAttribute("disabled","");
		enable_save_script()

	}else{

		disable_save_script();

		document.getElementById("email-config-message").innerHTML=`
		No email Configured for API Failure. 
		<a class="modal-trigger" href="#modal-api-fail-email-config">Configure Now</a>`;
		document.getElementById("email-config-message").style.color="#013498";
	}

	$("#add-api-mailer-input").keypress(function(e) {
		var keycode = (e.keyCode ? e.keyCode : e.which);
		if (keycode == '13') {
			value = $("#add-api-mailer-input").val();
			let api_mailer_list=[value]
			add_api_mailer_email_chips_data(api_mailer_list);
			$("#add-api-mailer-input").val("");
		}
	});

    input_filename_element = document.getElementById("processor-name");

    input_filename_element.onkeyup = function(e){
        value = input_filename_element.value;
        if(value==""){
            disable_save_script();
        }else{
            enable_save_script();
        }
    };

})

function enable_save_script(){
	let is_api_mail_configured=true
	
	if(window.api_fail_email_configured_editor + "" != "True"){
		is_api_mail_configured = false
	}
	if(is_api_mail_configured){
		$("#save-processor-btn").css("opacity", 1)
		$("#save-processor-btn").css("cursor", "pointer")
	}
}

function disable_save_script(){ 

	$("#save-processor-btn").css("opacity", 0.5)
	$("#save-processor-btn").css("cursor", "default")
	
}

function add_api_mailer_email_chips_data(list_of_added_email_ids){

	let email_chip_container_el = document.getElementById("added-email-address-div-container")
	let html = ""
	for(let i=0; i<list_of_added_email_ids.length; i++ ){
		html += `<div " class="email-address-tag-div">
					<span class="api-mailer-configure-email-id-data">` + list_of_added_email_ids[i] +`</span> 
					<span class="remove-email-icon">
					<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
						<path d="M18 6L6 18" stroke="#0254D7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
						<path d="M6 6L18 18" stroke="#0254D7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
					</svg>
					</span>
				</div>`
	}
	email_chip_container_el.innerHTML += html

	$(".email-address-tag-div .remove-email-icon").click(function() {
		$(this).parent(".email-address-tag-div").remove();
	});
}

$(document).on("click", ".delete-button-api-url", function(e) {
    e.preventDefault();
    element = "#" + this.id;
    $(element).remove();
    $(element).remove();

});

function add_api_list_url(sentence) {
    if (sentence.trim() == "") {
        return;
    }
    var str_id = sentence.toString().replace(/[^A-Z0-9]/ig, "");

    var html = `<li class="collection-item" id="` + str_id + `">
      <div class="api-added-collection-list-div">
        <input id="` + str_id + `" type="text" value="` + sentence + `" style="width: 80%">
        <div class="secondary-content">
        <a href="" class="delete-button-api-url" id="` + str_id + `">
			<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
				<path fill-rule="evenodd" clip-rule="evenodd" d="M5.78997 3.33337L5.93819 2.66639C5.97076 2.60665 6.02879 2.5218 6.10562 2.45095C6.19775 2.36599 6.27992 2.33337 6.35185 2.33337H9.31481C9.31449 2.33337 9.31456 2.33338 9.31502 2.33341C9.31797 2.33363 9.33695 2.33504 9.36833 2.34387C9.40259 2.3535 9.44447 2.37001 9.48859 2.39629C9.56583 2.44229 9.65609 2.52156 9.72769 2.66287L9.87669 3.33337H5.78997ZM5.15683 4.33337C5.16372 4.33352 5.17059 4.33352 5.17744 4.33337H10.4892C10.4961 4.33352 10.5029 4.33352 10.5098 4.33337H13.1667C13.4428 4.33337 13.6667 4.10952 13.6667 3.83337C13.6667 3.55723 13.4428 3.33337 13.1667 3.33337H10.9011L10.6918 2.39158L10.6809 2.34271L10.6606 2.29697C10.3311 1.55552 9.67791 1.33337 9.31481 1.33337H6.35185C5.9497 1.33337 5.63682 1.52298 5.42771 1.7158C5.22096 1.90646 5.0796 2.1315 5.00606 2.29697L4.98573 2.34271L4.97487 2.39158L4.76558 3.33337H2.5C2.22386 3.33337 2 3.55723 2 3.83337C2 4.10952 2.22386 4.33337 2.5 4.33337H5.15683ZM3.09959 5.00456C3.37324 4.96751 3.6251 5.15932 3.66215 5.43296L4.65773 12.787C4.7031 12.9453 4.80538 13.1798 4.96108 13.369C5.12181 13.5643 5.29845 13.6667 5.5 13.6667H10.5C10.5571 13.6667 10.6813 13.6397 10.7862 13.543C10.8763 13.46 11 13.2816 11 12.8867V12.853L11.0045 12.8196L12.0045 5.43296C12.0416 5.15932 12.2934 4.96751 12.5671 5.00456C12.8407 5.04161 13.0325 5.29347 12.9955 5.56712L11.9998 12.922C11.9921 13.5331 11.7842 13.9831 11.4638 14.2784C11.1521 14.5657 10.7763 14.6667 10.5 14.6667H5.5C4.90155 14.6667 4.46708 14.3424 4.18892 14.0044C3.9146 13.6711 3.75283 13.2816 3.6828 13.0127L3.67522 12.9836L3.67119 12.9538L2.67119 5.56712C2.63414 5.29347 2.82594 5.04161 3.09959 5.00456Z" fill="#E10E00"/>
			</svg>
        </a>
        </div>
      </div>
    </li>`;
    $(html).appendTo($("#api_collection"));
}

$("#add_enter_api_url").keypress(function(e) {
	var keycode = (e.keyCode ? e.keyCode : e.which);
	if (keycode == '13') {
		value = $("#add_enter_api_url").val();
		add_api_list_url(value);
		$("#add_enter_api_url").val("");
	}
});

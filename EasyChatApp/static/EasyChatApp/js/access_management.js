$(document).ready(function() {

    var location_hash = window.location.hash;
    if (location_hash == "#sandbox-credentials") {
        document.getElementById("sandbox-credentials").style.display = "block";
        document.getElementById("bot-managers").style.display = "none";
    }
    $('#bot-managers-table').DataTable({
        "bPaginate": false,
        "ordering": false,
        initComplete: function() {
            $(this.api().table().container()).find('input').parent().wrap('<form>').parent().attr('autocomplete', 'off');
        }
    });
});

function validateEmail(emailField) {
    const reg = /^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/
    if (reg.test(emailField.value) == false) {
        return false;
    }
    return true;
}

function validateEmailAddr(emailAddress) {
    const reg = /^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/
    if (reg.test(emailAddress) == false) {
        return false;
    }
    return true;
}

function add_bot_manager(element) {

    first_name = document.getElementById("bot-manager-firstname").value.trim();
    last_name = document.getElementById("bot-manager-lastname").value.trim();
    email = document.getElementById("bot-manager-email").value.trim();
    password = document.getElementById("bot-manager-password").value;

    const regName = /^[a-zA-Z]+$/;
    if (first_name.trim() == "" || !regName.test(first_name)) {
        M.toast({
            "html": "Please enter valid first name."
        }, 2000);
        return;
    }

    if (last_name.trim() == "" || !regName.test(last_name)) {
        M.toast({
            "html": "Please enter valid last name."
        }, 2000);
        return;
    }

    if (validateEmail(document.getElementById("bot-manager-email")) == false) {
        M.toast({
            "html": "Provide valid email id for contact information."
        }, 2000);
        return;
    }

    if (password.trim() == "") {
        M.toast({
            "html": "Password cannot be empty."
        }, 2000);
        return;
    }

    password_regex = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z]).{8,32}$/

    if (password_regex.test(password) == false) {
        document.getElementById("password_check_bot_manager").style.display = "block"


        one_upercase_and_lowercase_regex = /(?=.*[a-z])(?=.*[A-Z])/
        if (one_upercase_and_lowercase_regex.test(password) == false) {
            M.toast({
                "html": "Password must contain one upper case letter and one lower case letter"
            }, 2000);
            document.getElementById("bot-manager-password-cap-small-check").style.display = "list-item";
        } else {

            document.getElementById("bot-manager-password-cap-small-check").style.display = "none";
        }
        atleast_one_no_regex = /(?=.*\d)/
        if (atleast_one_no_regex.test(password) == false) {
            M.toast({
                "html": "Password must contain one number"
            }, 2000);
            document.getElementById("bot-manager-password-number-check").style.display = "list-item";
        } else {

            document.getElementById("bot-manager-password-number-check").style.display = "none";
        }
        special_char_regex = /(?=.*[@$!%*?&])/
        if (special_char_regex.test(password) == false) {
            M.toast({
                "html": "Password must contain one special character"
            }, 2000);
            document.getElementById("bot-manager-password-special-char-check").style.display = "list-item";
        } else {

            document.getElementById("bot-manager-password-special-char-check").style.display = "none";
        }

        if (password.length < 8 || password.length > 32) {
            M.toast({
                "html": "Password length must be between 8-32 characters"
            }, 2000);
            document.getElementById("bot-manager-password-length-check").style.display = "list-item";
        } else {

            document.getElementById("bot-manager-password-length-check").style.display = "none";
        }

        return;
    }

    username = email.split('@');
    username = username[0]
    if (password.toLowerCase().includes(username.toLowerCase())) {
        M.toast({
            "html": "Password must not contain user name"
        }, 2000);

        return;
    }

    csrf_token = get_csrf_token();
    json_string = JSON.stringify({
        manager_id: "None",
        first_name: first_name,
        last_name: last_name,
        password: password,
        email: email
    });
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: "/supervisor/create-bot-manager/",
        type: "POST",
        headers: {
            "X-CSRFToken": csrf_token
        },
        data: {
            data: json_string
        },
        success: function(response) {
            response = custom_decrypt(response["response"])
            response = JSON.parse(response);
            if (response["status"] == 200) {
                M.toast({
                    "html": "Bot Manager has been created successfully!"
                }, 2000);
                $("#modal-add-bot-manager").modal("close");
                setTimeout(function() {
                    window.location.hash = "#bot-managers"
                    window.location.reload();
                }, 2000);
            } else {
                M.toast({
                    "html": response["message"]
                }, 2000);
            }
        },
        error: function(jqXHR, exception) {
            console.log(jqXHR, exception);
        }
    });
}

///////////////////////////////// functions related to sandbox users/////////////////////////////////////
function add_sandbox_user(element) {
    username = document.getElementById("sandbox-user-username").value.trim();
    password = document.getElementById("sandbox-user-password").value.trim();

    const regName = /^[a-zA-Z]+$/;
    if (username == "" && password == "") {
        M.toast({
            "html": "Please enter a username and password"
        }, 2000);
        return;
    }

    if (username == "") {
        M.toast({
            "html": "Please enter a username."
        }, 2000);
        return;
    }

    if (!validateEmailAddr(username)) {
        M.toast({
            "html": "Please enter a valid Email Id"
        }, 2000);
        return;
    }
    if (password == "") {
        M.toast({
            "html": "Please enter a password"
        }, 2000);
        return;
    }

    password_regex = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z]).{8,32}$/

    if (password_regex.test(password) == false) {
        document.getElementById("password_check_sandbox_user").style.display = "block"

        one_upercase_and_lowercase_regex = /(?=.*[a-z])(?=.*[A-Z])/
        if (one_upercase_and_lowercase_regex.test(password) == false) {
            M.toast({
                "html": "Password must contain one upper case letter and one lower case letter"
            }, 2000);
            document.getElementById("sandbox-password-cap-small-check").style.display = "list-item";
        } else {

            document.getElementById("sandbox-password-cap-small-check").style.display = "none";
        }

        atleast_one_no_regex = /(?=.*\d)/
        if (atleast_one_no_regex.test(password) == false) {
            M.toast({
                "html": "Password must contain one number"
            }, 2000);
            document.getElementById("sandbox-password-number-check").style.display = "list-item";
        } else {

            document.getElementById("sandbox-password-number-check").style.display = "none";
        }

        special_char_regex = /(?=.*[@$!%*?&])/
        if (special_char_regex.test(password) == false) {
            M.toast({
                "html": "Password must contain one special character"
            }, 2000);
            document.getElementById("sandbox-password-special-char-check").style.display = "list-item";
        } else {

            document.getElementById("sandbox-password-special-char-check").style.display = "none";
        }

        if (password.length < 8 || password.length > 32) {
            M.toast({
                "html": "Password length must be between 8-32 characters"
            }, 2000);
            document.getElementById("sandbox-password-length-check").style.display = "list-item";
        } else {

            document.getElementById("sandbox-password-length-check").style.display = "none";
        }

        return;
    }

    if (password.includes(username)) {
        M.toast({
            "html": "Password must not contain user name"
        }, 2000);

        return;
    }


    csrf_token = get_csrf_token();
    json_string = JSON.stringify({
        user_id: "None",
        username: username,
        password: password,

    });
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: "/supervisor/create-sandbox-user/",
        type: "POST",
        headers: {
            "X-CSRFToken": csrf_token
        },
        data: {
            data: json_string
        },
        success: function(response) {
            response = custom_decrypt(response["response"])
            response = JSON.parse(response);
            if (response["status"] == 200) {
                M.toast({
                    "html": "User has been created successfully!"
                }, 2000);
                $("#modal-add-user").modal("close");
                setTimeout(function() {
                    window.location.hash = '#sandbox-credentials'
                    window.location.reload()

                }, 2000);


            } else {
                M.toast({
                    "html": response["message"]
                }, 2000);
            }
        },
        error: function(jqXHR, exception) {
            console.log(jqXHR, exception);
        }
    });
}

function extend_sandbox_user(user_pk) {

    csrf_token = get_csrf_token();
    json_string = JSON.stringify({
        user_pk: user_pk,
    });
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: "/supervisor/extend-sandbox-user/",
        type: "POST",
        headers: {
            "X-CSRFToken": csrf_token
        },
        data: {
            data: json_string
        },
        success: function(response) {
            response = custom_decrypt(response["response"])
            response = JSON.parse(response);
            if (response["status"] == 200) {
                M.toast({
                    "html": "User credentials have been extended successfully!"
                }, 2000);
                $("#modal-extend-sandbox-user-" + user_pk).modal("close");
                setTimeout(function() {
                    window.location.hash = '#sandbox-credentials'
                    window.location.reload();
                }, 2000);
            } else {
                M.toast({
                    "html": response["message"]
                }, 2000);
            }
        },
        error: function(jqXHR, exception) {
            console.log(jqXHR, exception);
        }
    });
}

////////////////////////////// end of functions related to sandbox users /////////////////////////////////

function unshare(manager_id, bot_id){

        json_string = JSON.stringify({
          "bot_id":bot_id,
          "user_id":manager_id
        });
        json_string = EncryptVariable(json_string)
        $.ajax({
            url:"/chat/bot/unshare/",
            type:"POST",
            headers:{
            "X-CSRFToken":get_csrf_token()
            },
            data:{
             data:json_string
            },
            success: function(response){

                if(response["status"]==200){

                    M.toast({"html":"Bot unshared successfully."}, 2000);
                    window.location.reload();
                }else if(response["status"]==401) {
                    M.toast({"html": response["message"]}, 2000);
                }else{

                    M.toast({"html":"Unable to undo bot share. Please try again later."}, 2000);
                }
            },
            error: function(error){
             console.log("Report this error: ", error);
            }
        });
    }

function edit_bot_manager(element, manager_id) {

    first_name = document.getElementById("bot-manager-firstname-" + manager_id).value.trim();
    last_name = document.getElementById("bot-manager-lastname-" + manager_id).value.trim();

    const regName = /^[a-zA-Z]+$/;
    if (first_name.trim() == "" || !regName.test(first_name)) {
        M.toast({
            "html": "Please enter valid first name."
        }, 2000);
        return;
    }

    if (last_name.trim() == "" || !regName.test(last_name)) {
        M.toast({
            "html": "Please enter valid last name."
        }, 2000);
        return;
    }

    csrf_token = get_csrf_token();
    json_string = JSON.stringify({
        manager_id: manager_id,
        first_name: first_name,
        last_name: last_name,
        password: "",
        email: ""
    });
    json_string = EncryptVariable(json_string);

    $.ajax({
        url: "/supervisor/create-bot-manager/",
        type: "POST",
        headers: {
            "X-CSRFToken": csrf_token
        },
        data: {
            data: json_string
        },
        success: function(response) {
            response = custom_decrypt(response["response"])
            response = JSON.parse(response);
            if (response["status"] == 200) {
                M.toast({
                    "html": "Bot Manager has been saved successfully!"
                }, 2000);
                $("#modal-add-bot-manager").modal("close");
                setTimeout(function() {
                    window.location.hash = "#bot-managers"
                    window.location.reload();
                }, 2000);
            } else {
                M.toast({
                    "html": response["message"]
                }, 2000);
            }
        },
        error: function(jqXHR, exception) {
            console.log(jqXHR, exception);
        }
    });
}

function copy_password(data) {

    if (navigator.clipboard) {

        navigator.clipboard.writeText(data)
    } else {

        var textArea = document.createElement('textarea');
        textArea.textContent = data;
        document.body.append(textArea);
        textArea.select();
        document.execCommand("copy");
        textArea.remove()
    }
    M.toast({
        "html": "Password has been copied"
    }, 2000);
}

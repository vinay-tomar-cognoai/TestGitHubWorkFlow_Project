var canned_modal = document.getElementById("admin-canned-response-modal");
var canned_btn = document.getElementById("myBtnCanned");

if (canned_btn != null && canned_btn != undefined) {
    canned_btn.onclick = function () {
        canned_modal.style.display = "block";
    };
}
window.onclick = function (event) {
    if (event.target == canned_modal) {
        canned_modal.style.display = "none";
    } else if (event.target == category_modal) {
        category_modal.style.display = "none";
    } else if (event.target == keyword_modal) {
        keyword_modal.style.display = "none";
    }
};

var category_modal = document.getElementById("admin-category-modal");
var category_btn = document.getElementById("myBtnCategory");

if (category_btn != null && category_btn != undefined) {
    category_btn.onclick = function () {
        category_modal.style.display = "block";
    };
}

var keyword_modal = document.getElementById("admin-blacklisted-keyword-modal");
var keyword_btn = document.getElementById("myBtnKeyword");
if (keyword_btn != null && keyword_btn != undefined) {
    keyword_btn.onclick = function () {
        keyword_modal.style.display = "block";
    };
}

function deleteAdminCategoryFunction(element) {
    // var responsecheckBox = document.querySelector(".response-checkbox");
    var addResponse = document.getElementById("myBtnCategory");
    var deleteResponse = document.getElementById("deleteBtnCategory");
    if (element.checked == true) {
        deleteResponse.style.display = "inline-block";
        addResponse.style.display = "none";
    } else {
        deleteResponse.style.display = "none";
        addResponse.style.display = "inline-block";
    }
}

function deleteAdminKeywordFunction(element) {
    // var responsecheckBox = document.querySelector(".response-checkbox");
    var addResponse = document.getElementById("myBtnKeyword");
    var deleteResponse = document.getElementById("deleteBtnKeyword");
    if (element.checked == true) {
        deleteResponse.style.display = "inline-block";
        addResponse.style.display = "none";
    } else {
        deleteResponse.style.display = "none";
        addResponse.style.display = "inline-block";
    }
}
try {
    document
        .getElementById("indeterminate-checkbox-all")
        .addEventListener("change", function () {
            if (document.getElementById("indeterminate-checkbox-all").checked) {
                is_checked = true;
            } else {
                is_checked = false;
            }

            for (idx = 0; idx < 7; idx++) {
                document.getElementById(
                    "indeterminate-checkbox-" + idx
                ).checked = is_checked;
            }
        });
    for (var i = 0; i < 7; i++) {
        document
            .getElementById("indeterminate-checkbox-" + i)
            .addEventListener("change", function () {
                var flag = 0;
                for (let idx = 0; idx < 7; idx++) {
                    if (
                        !document.getElementById(
                            "indeterminate-checkbox-" + idx
                        ).checked
                    ) {
                        flag = 1;
                        break;
                    }
                }
                if (flag == 0) {
                    document.getElementById(
                        "indeterminate-checkbox-all"
                    ).checked = true;
                } else {
                    document.getElementById(
                        "indeterminate-checkbox-all"
                    ).checked = false;
                }
            });
    }
} catch (err) {}
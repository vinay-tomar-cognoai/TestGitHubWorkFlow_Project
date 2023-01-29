function check_date_range_validation(start_date, end_date){
    let today = new Date();
    today = today.getFullYear() + "-" + String(today.getMonth() + 1).padStart(2, '0') + "-" + String(today.getDate()).padStart(2, '0');
    let validation_message = "";

    if (!start_date) {
        validation_message = "The start date cannot be empty.";
    }

    else if (!end_date) {
        validation_message = "The end date cannot be empty.";
    }

    else if (start_date > today) {
        validation_message = "The start date cannot be greater than the current date.";
    }

    else if (end_date > today) {
        validation_message = "The end date cannot be greater than the current date.";
    }

    else if (start_date > end_date) {
        validation_message = "The start date cannot be greater than the end date.";
    }

    return validation_message;
}
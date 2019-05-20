function createErrorMessage(element, error_message, id) {
    var message = document.getElementById(id);
    if (message) {
        message.textContent = error_message;
        message.hidden = false;
    } else {
        var new_elem = document.createElement('div');
        new_elem.setAttribute('id', id);
        new_elem.setAttribute('class', "error");
        var t = document.createTextNode(error_message);
        new_elem.appendChild(t);
        element.before(new_elem);
    }
}

function update_img_link(mod, img_link_id) {
    if (mod != undefined) {
        if (post_form_validations[mod]['image_type'] != undefined && post_form_validations[mod]['image_type'].toLocaleLowerCase() == "url") {
            adapt_post_to_channel(img_link_id);
        }
    }
}

function adapt_post_to_channel(img_link_id) {
    document.getElementById(img_link_id).type = "text";
}

function prevalidate_post_or_publishing(title_id, description_id, link_url_id, img_link_id, date_from_id, date_until_id, title_length, descr_length) {
    var toReturn = true;
    var elementToRemove;
    var input_title = document.getElementById(title_id);
    if (input_title.value == "") {
        createErrorMessage(input_title, "the title is empty", "error_" + title_id);
        input_title.classList.add("invalid");
        toReturn = false;
    } else if (input_title.value.length > title_length) {
        createErrorMessage(input_title, "the title is too long", "error_" + title_id);
        input_title.classList.add("invalid");
        toReturn = false;
    } else {
        elementToRemove = document.getElementById("error_" + title_id);
        if (elementToRemove) {
            elementToRemove.hidden = true;
        }
        input_title.classList.remove("invalid");
    }

    var input_descrip = document.getElementById(description_id);
    if (input_descrip.value == "") {
        createErrorMessage(input_descrip, "the description is empty", "error_" + description_id);
        input_descrip.classList.add("invalid");
        toReturn = false;
    } else if (input_descrip.value.length > descr_length) {
        createErrorMessage(input_descrip, "the description is too long", "error_" + description_id);
        input_descrip.classList.add("invalid");
        toReturn = false;
    } else {
        elementToRemove = document.getElementById("error_" + description_id);
        if (elementToRemove) {
            elementToRemove.hidden = true;
        }
        input_descrip.classList.remove("invalid");
    }

    var input_linkUrlPost = document.getElementById(link_url_id);
    var pattern = new RegExp('^(?:(?:https?|http?|wwww?):\\/\\/)?(?:(?!(?:10|127)(?:\\.\\d{1,3}){3})(?!(?:169\\.254|192\\.168)(?:\\.\\d{1,3}){2})(?!172\\.(?:1[6-9]|2\\d|3[0-1])(?:\\.\\d{1,3}){2})(?:[1-9]\\d?|1\\d\\d|2[01]\\d|22[0-3])(?:\\.(?:1?\\d{1,2}|2[0-4]\\d|25[0-5])){2}(?:\\.(?:[1-9]\\d?|1\\d\\d|2[0-4]\\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)(?:\\.(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)*(?:\\.(?:[a-z\u00a1-\uffff]{2,})))(?::\\d{2,5})?(?:\\/\\S*)?$');
    if (input_linkUrlPost.value != "" && !pattern.test(input_linkUrlPost.value)) {
        createErrorMessage(input_linkUrlPost, "insert a valid link", "error_" + link_url_id);
        input_linkUrlPost.classList.add("invalid");
        toReturn = false;
    } else {
        elementToRemove = document.getElementById("error_" + link_url_id);
        if (elementToRemove) {
            elementToRemove.hidden = true;
        }
        input_linkUrlPost.classList.remove("invalid");
    }

    var input_linkImgUrlPost = document.getElementById(img_link_id);
    if (input_linkImgUrlPost.value != "" && !pattern.test(input_linkImgUrlPost.value)) {
        createErrorMessage(input_linkImgUrlPost, "insert a valid picture link ", "error_" + img_link_id);
        input_linkImgUrlPost.classList.add("invalid");
        toReturn = false;
    } else {
        elementToRemove = document.getElementById("error_" + img_link_id);
        if (elementToRemove) {
            elementToRemove.hidden = true;
        }
        input_linkImgUrlPost.classList.remove("invalid");
    }

    var input_datefrompost = document.getElementById(date_from_id);
    if (input_datefrompost.value == "") {
        createErrorMessage(input_datefrompost, "the date from post is empty", "error_" + date_from_id);
        input_datefrompost.classList.add("invalid");
        toReturn = false;
    } else {
        elementToRemove = document.getElementById("error_" + date_from_id);
        if (elementToRemove) {
            elementToRemove.hidden = true;
        }
        input_datefrompost.classList.remove("invalid");
    }

    var input_dateuntilpost = document.getElementById(date_until_id);
    if (input_dateuntilpost.value == "") {
        createErrorMessage(input_dateuntilpost, "the date until post is empty", "error_" + date_until_id);
        input_dateuntilpost.classList.add("invalid");
        toReturn = false;
    } else {
        elementToRemove = document.getElementById("error_" + date_until_id);
        if (elementToRemove) {
            elementToRemove.hidden = true;
        }
        input_dateuntilpost.classList.remove("invalid");
    }
    if (input_datefrompost.value != "" && input_dateuntilpost.value != "") {
        var a = new Date(input_datefrompost.value);
        var b = new Date(input_dateuntilpost.value);

        if (b < a) {
            createErrorMessage(input_dateuntilpost, "the date until post is greater that date from post", "error_" + date_until_id);
            input_dateuntilpost.classList.add("invalid");
            toReturn = false;
        } else {
            elementToRemove = document.getElementById("error_" + date_until_id);
            if (elementToRemove) {
                elementToRemove.hidden = true;
            }
            input_dateuntilpost.classList.remove("invalid");
        }
    }
    return toReturn;
}


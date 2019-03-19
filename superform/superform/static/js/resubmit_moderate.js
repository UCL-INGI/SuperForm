var data_ok = false;
update_img_link(document.getElementsByClassName('row')[0].getAttribute("module-namechan").split('.')[2], "imagepost");
update_img_link(document.getElementsByClassName('row')[0].getAttribute("module-namechan").split('.')[2], "imagepost_old");

$("#yes_button_moderate").click(function () {
    $("#modalResubmitModerate").modal("hide");
    data_ok = true;
    $("#unvalidate, #resubmit").click();
});

$("#publish, #unvalidate, #resubmit").click(function (event) {
    if (data_ok) {
        return true;
    }
    var toReturn = true;
    let mod = document.getElementsByClassName('row')[0].getAttribute("module-namechan").split('.')[2];
    let title_max_length = 100000;
    let descr_max_length = 100000;
    if (mod != undefined) {
        if (post_form_validations[mod]['title_max_length'] != undefined) {
            title_max_length = post_form_validations[mod]['title_max_length'];
        }
        if (post_form_validations[mod]['description_max_length'] != undefined) {
            descr_max_length = post_form_validations[mod]['description_max_length'];
        }
    }
    if ((!prevalidate_post(title_max_length, descr_max_length))) {
        toReturn = false;
    }
    var moderator_comment = $('#moderator_comment');
    var user_comment = $('#user_comment');
    if ($(this).attr('id') == 'publish') {
        return toReturn;
    }
    if (toReturn && ((moderator_comment.length && moderator_comment.val() == "") || (user_comment.length && user_comment.val() == ""))) {
        $("#modalResubmitModerate").modal("show");
        return false;
    }
    return toReturn;
});

function prevalidate_post(title_max_length, descr_max_length) {
    return prevalidate_post_or_publishing("titlepost", "descrpost",
        "linkurlpost", "imagepost",
        "datefrompost", "dateuntilpost", title_max_length, descr_max_length);
}


let height = $('#old_pub').height() - $('#mod_comment').height(); // - $('#pagination_old').height();
$('#chat_box').height(height);
$('#chat_box').show();
$('#chat_box .scroll').scrollTop($('#chat_box .scroll')[0].scrollHeight);

let current = 0;
if (pubs.length > 1) {
    $('#prev_button').removeClass('disabled');
    current = pubs.length - 1;
}
updateFields();

function updateFields() {
    $('#titlepost_old').val(pubs[current].title);
    $('#descrpost_old').val(pubs[current].description);
    $('#linkurlpost_old').val(pubs[current].link_url);
    $('#imagepost_old').val(pubs[current].image_url);
    $('#datefrompost_old').val(pubs[current].date_from);
    $('#dateuntilpost_old').val(pubs[current].date_until);
    $('#current_date').text(coms[current].date_user_comment);

    if (current == 0) {
        $('#prev_button').addClass('disabled');
    }
    else {
        $('#prev_button').removeClass('disabled');
    }
    if (current != pubs.length - 1) {
        $('#next_button').removeClass('disabled');
    }
    else {
        $('#next_button').addClass('disabled');
    }
}

$('#next_button').on('click', function () {
    if (pubs.length > current + 1) {
        current++;
        updateFields();
    }
});

$('#prev_button').on('click', function () {
    if (current - 1 >= 0) {
        current--;
        updateFields();
    }
});

$('.talktext').on('click', function () {
    _this = $(this);
    number = _this.attr('id').split('_')[1] - 1;
    current = number;
    updateFields();
});

function getUpdates() {
    var list = $("#post-list");
    var post_block = $("#post-block");
    var max_time = list.data("max-time");
    if(!max_time) {
        return;
    }
    console.log(max_time);
    $.get("/index/get-update/" + max_time)
        .done(function (data) {
            var obj = jQuery.parseJSON(data);
            list.data('max-time', obj['max-time']);
            for (var i = 0; i < obj['items'].length; i++) {
                addPostItem(list, obj['items'][i]);
            }
        });
}
function addPostItem(list, item) {
    var new_item = $(item.html);
    list.prepend(new_item);
}
function populateList() {
    $.get("/index/get-update/").done(function (data) {
        var obj = JSON.parse(data);
        var list = $("#post-list");

        list.data('max-time', obj['max-time']);
        for (var i = 0; i < obj['items'].length; i++) {
            addPostItem(list, obj["items"][i]);
        }
    })
}

function addItem() {
    var itemField = $("#item-field");
    $.post("/grumblr/post", {"post": itemField.val()})
        .done(function (data) {
            getUpdates();
            itemField.val("").focus();
        });
}

$(document).ready(function () {
    // Add event-handlers
    $("#add-btn").click(addItem);
    $("#item-field").keypress(function (e) {
        if (e.which === 13) addItem();
    });
    // Add delegate to show comment button
    $("ul").on("click", ".comments", function (event) {
        var btn = $(this);
        var postid = btn.attr("id");
        console.log("getting " + "get-comments/" + postid);
        $.get("/get-comments/" + postid, function(data) {
            var obj = jQuery.parseJSON(data);
            for (var i = 0; i < obj['items'].length; i++) {
                btn.parent().append(obj['items'][i].html);
            }
            $.get("comment-input/" + postid, function (data) {
                btn.parent().append(data);
                console.log("comment-input success");
                btn.remove();
            });
        });

    });

    // Add delegate to comment post button
    $("ul").on("click", ".post-comment", function (event) {
        console.log($(this).attr("id") + " was clicked");
        var postid = $(this).attr("id");
        var btn = $(this);
        var body = {}
        console.log($("#"+postid).val());
        body["text"] = $("#"+postid).val();

        $.post("comment-input/" + postid, body, function(data) {
            lastCommentInput= $("#post-comment-" + postid);
            $(data).insertBefore(lastCommentInput);
            if (body["text"].length == 0)
                lastCommentInput.hide();
        });
        $("#"+postid).val("").focus();
    });

    // Set up to-do list with initial DB items and DOM data
    populateList();
    $("#item-field").focus();

    // Periodically refresh to-do list
    window.setInterval(getUpdates, 5000);

    // CSRF set-up copied from Django docs
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrftoken = getCookie('csrftoken');
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    });
});

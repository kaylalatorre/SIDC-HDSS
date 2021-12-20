/**
 * Helper function to prepare AJAX functions with CSRF middleware tokens.
 * This avoids getting 403 (Forbidden) errors.
 */
function ajaxCSRF() {
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
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
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                // Only send the token to relative URLs i.e. locally.
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });
}

function syncNotifs(){
    // ajax call
    ajaxCSRF();
    $.ajax({
        type: 'POST',
        url: '/notifications/sync',
        success: function (response) {
            console.log(response);
            return response;
        }
    }).then(async function(){
        var notifCount = await getNotifsCount();
        updateNotifBadge(notifCount);
    })
    
}

/** 
 * Ajax call for notification count.
 * @return {Integer} Count of all notifications.
 */
function getNotifsCount() {
    // ajax call
    ajaxCSRF();
    return $.ajax({
        type: 'POST',
        url: '/notifications/count',
        success: function (response) {            
            return response;
        }
    });
}


/** 
 * Updates the notification icon badge to reflect current notification count.
 */
function updateNotifBadge(notifCount) {
    switch (
        Boolean(parseInt(notifCount)) + // 1 or 0
        Boolean($('.notif-icon').children('span').length) * 2 // 2 or 0
    ) {
        case 0:
            // do nothing
            console.log('case0');
            break; // no notifs and no span
        case 1:
            // create span
            console.log('case1');
            $('.notif-icon').append('<span>' + notifCount + '</span>');
            break; // with notifs and no span
        case 2:
            // remove span
            console.log('case2');
            $('.notif-icon').children('span').remove();
            break; // no notifs and with span
        case 3:
            // update span
            console.log('case3');
            $('.notif-icon').children('span').text(notifCount);
            break; // with notifs and with span
        default:
            location.reload(true);
    }
}

/*
 *   Toggling to show notif-box
 */
var box = document.getElementById('notification-box');
var down = false;

async function toggleNotif() {
    if (down) {
        syncNotifs();
        box.style.height = '0px';
        box.style.opacity = 0;
        down = false;
    } else {
        $('.notif-list').load('/notifications .notif-list', function (response) {
            $(this).children().unwrap();
        });
        var notifCount = await getNotifsCount();
        box.style.height = "auto";
        box.style.opacity = 1;
        down = true;
        updateNotifBadge(notifCount);
    }
}

$(document).ready(async function () {
    if ($('.notif-icon').length) {
        var notifCount = await getNotifsCount();
        updateNotifBadge(notifCount);
    }
});
/*
*   Toggling to show notif-box
*/
var box = document.getElementById('notification-box');
var down = false;

function toggleNotif() {
    if (down) {
        box.style.height = '0px';
        box.style.opacity = 0;
        down = false;
    } else {
        box.style.height = "auto";
        box.style.opacity = 1;
        down = true;
    }
}
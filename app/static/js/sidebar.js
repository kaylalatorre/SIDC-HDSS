var $toggleBtn = $('#toggleBtn'); // get menu button from topbar
var $pushSelectors = $('.sidebar') // get the sidebar and content
var sidebarIsOpen; // global variable to store sidebar state
var openOnLoad = false; // default state

/**
 * Checking sessionStorage.
 */
function checkStorage() {
    // sidebar state
    if(sessionStorage.getItem('sidebar') === "opened") {
        $(document).ready(function() {
            $($pushSelectors.removeClass('close'));
        });
    } else {
        console.log('Sidebar is closed.');
    }

    // nav-item states
    if(sessionStorage.getItem('listID') != null) {
        var val = sessionStorage.getItem('listID');
        $('#' + val).addClass('nav-current');
    }
}

/**
 * Saving active link to the sessionStorage.
 * @param {id of selected list} id 
 */
function active(id) {
    sessionStorage.removeItem('listID'); //clear previous data
    sessionStorage.setItem("listID", id); //add data to storage
    console.log(id);
}

/**
 * Toggling sidebar and saving state.
 * This saves the sidebar states in a sessionStorage so that
 * it will stay the same even when the page refreshes.
 */
function toggleSidebar() {
    sidebarIsOpen = !sidebarIsOpen; 
    
    // check if the sidebar should be closed/open
    if(sidebarIsOpen) {
        $pushSelectors.removeClass('close');
        sessionStorage.setItem('sidebar', 'opened');
        console.log("Local Storage // sidebar: opened");
    } else {
        $pushSelectors.addClass('close');
        sessionStorage.setItem('sidebar', 'closed');
        console.log('Local Storage // sidebar: closed');
    }

    // check if the storage item exists
    if(sessionStorage.getItem('sidebar') === null) {
        sidebarIsOpen = openOnLoad;
        console.log('The default state is ' + openOnLoad);
    } else {
        // if it exist, set value to open
        if(sessionStorage.getItem('sidebar') === "opened") {
            sidebarIsOpen = true;
            console.log('Local Storage // sidebar: opened');
        } else {
            sidebarIsOpen = false;
            console.log('Local Storage // sidebar: closed');
        }
    }

    if (sidebarIsOpen) {
        $pushSelectors.removeClass('close');
        console.log('The \'close\' class has been removed.')
    }
    else {
        $pushSelectors.addClass('close');
        console.log('The \'close\' class has been added.')
    }
}

$toggleBtn.on('click', toggleSidebar); 

/** 
 * Toggling the sidebar dropdown menu. 
 */ 
 let arrow = document.querySelectorAll('.arrow');
 for(var i =0; i < arrow.length; i++) {
     arrow[i].addEventListener("click", (e)=> {
         let arrowParent = e.target.parentElement.parentElement;
         arrowParent.classList.toggle("showMenu");
     })
 }
/* 
* Tech assignment edit button 
*/
let assignEdit = document.querySelectorAll('.assignEdit');
for(var i = 0; i < assignEdit.length; i++) { 
    assignEdit[i].addEventListener("click", (e)=> {
        let editParent = e.target.parentElement.parentElement.parentElement;
        let editDropdown = editParent.querySelector(".form-select");
        let assignSave = editParent.querySelector(".assignSave");
        let assignEdit = editParent.querySelector(".assignEdit");

        editDropdown.removeAttribute("disabled");
        assignSave.setAttribute("style", "display: block");
        assignEdit.setAttribute("style", "display: none");
    })
}

let assignSave = document.querySelectorAll('.assignSave');
for(var i = 0; i < assignSave.length; i++) { 
    assignSave[i].addEventListener("click", (e)=> {
        let saveParent = e.target.parentElement.parentElement.parentElement;
        let saveDropdown = saveParent.querySelector(".form-select");
        let assignSave = saveParent.querySelector(".assignSave");
        let assignEdit = saveParent.querySelector(".assignEdit");

        saveDropdown.setAttribute("disabled", true);
        assignSave.setAttribute("style", "display: none");
        assignEdit.setAttribute("style", "display: block");
    })
}

/* 
* Biosecurity edit button 
*/
let biosecEdit = document.querySelectorAll('.biosecEdit');
for(var i = 0; i < biosecEdit.length; i++) { 
    biosecEdit[i].addEventListener("click", (e)=> {
        let editParent = e.target.parentElement.parentElement.parentElement;
        let biosecSave = editParent.querySelector(".biosecSave");
        let biosecEdit = editParent.querySelector(".biosecEdit");
        console.log(biosecEdit);
        biosecSave.setAttribute("style", "display: block");
        biosecEdit.setAttribute("style", "display: none");
    })
}

let biosecSave = document.querySelectorAll('.biosecSave');
for(var i = 0; i < biosecSave.length; i++) { 
    biosecSave[i].addEventListener("click", (e)=> {
        let saveParent = e.target.parentElement.parentElement.parentElement;
        let biosecSave = saveParent.querySelector(".biosecSave");
        let biosecEdit = saveParent.querySelector(".biosecEdit");

        biosecSave.setAttribute("style", "display: none");
        biosecEdit.setAttribute("style", "display: block");
    })
}

/**
 * Changing style of statuses
 */
let rowStatus = document.querySelectorAll('.status');
console.log(rowStatus);
for(var i = 0; i < rowStatus.length; i++) { 
    let val = rowStatus[i].innerText;
    if( val === "Resolved") {
        rowStatus[i].classList.add("green");
    }
    else if ( val === "Active") {
        rowStatus[i].classList.add("red");
    }
    else {
        console.log("No status detected/status value invalid.")
    }
}   

/**
 * Toggling view to Member Announcement btn-grp
 */
 let checkbox = document.querySelectorAll('.announce-checkbox');
 for(var i = 0; i < checkbox.length; i++) { 
     checkbox[i].addEventListener('click', (e) => {
        var isChecked = e.target.checked;
        var btnGrp = document.querySelector('#announce-btn-grp');
         console.log(isChecked);
         if(isChecked) {
             btnGrp.classList.remove('hide');
         } else {
             btnGrp.classList.add('hide');
         }
         
     });
 }   
 
/**
 * Toggling view to adding of area
 */
function toggleAreaView() {
    const area = $('.add-new-area');
    const addBtn = $('#add-area');
    const cancelBtn = $('#cancel-area');
    
    if(area.hasClass('hide')) {
        area.removeClass('hide').addClass('show');
        addBtn.addClass('hide').removeClass('show');
        cancelBtn.addClass('show').removeClass('hide');
    }
    else {
        area.removeClass('show').addClass('hide');
        addBtn.addClass('show').removeClass('hide');
        cancelBtn.addClass('hide').removeClass('show');
    }
}

// MGIHT BE BACKEND
function viewFarm(farm) {
    // Note: This links to a temporary navigation to template
        // not sure if this can be used with actual implementation? with data

    try{
        url = "/selected-farm/" + farm.parentNode.parentNode.getElementsByTagName("td")[0].innerHTML;
        console.log(url);
        location.href = url;
    }catch (error){
        console.log("Something went wrong. Restarting...");
        console.log("reloading...");
        location.reload(true);
    }
}

/**
*   - Appends new pigpen row for when adding a new farm
*   
*   input-pgipen = table body that the row will be appended to
*/
function addPigPenRow() {
    const length = document.getElementById('pigpen-length').innerHTML;
    const width = document.getElementById('pigpen-width').innerHTML;
    const num_heads = document.getElementById('pigpen-num-heads').innerHTML;

    $("#input-pigpen").append("<tr> \
        <td data-label='Length'> " + length + " </td> \
        <td data-label='Width'> " + width + " </td> \
        <td data-label='No. of Pigs'> " + num_heads + " </td> \
        </tr>");
}

/**
*   - Appends new activity row to activity table
*   
*   input-act = table body that the row will be appended to
*/
function addActivityRow() {
    const date = document.getElementById('date').innerHTML;
    const trip_type = document.getElementById('trip_type').innerHTML;
    const time_arrival = document.getElementById('time_arrival').innerHTML;
    const time_departure = document.getElementById('time_departure').innerHTML;
    const description = document.getElementById('description').innerHTML;
    const remarks = document.getElementById('remarks').innerHTML;

    $("#input-act").append("<tr> \
        <td data-label='Date'> " + date + " </td> \
        <td data-label='Trip Type'> " + trip_type + " </td> \
        <td data-label='Arrival Time'> " + time_arrival + " </td> \
        <td data-label='Departure Time'> " + time_departure + " </td> \
        <td data-label='Description'> " + description + " </td> \
        <td data-label='Remarks'> " + remarks + " </td> \
        </tr>");
}

function viewForm() {
    // Note: This links to a temporary navigation to template
        // not sure if this can be used with actual implementation? with data
    let viewFarm = document.querySelector('#viewForm');
    viewFarm.onclick = function () {
        location.href = "/selected-form";
    };
}

function viewAnnounce() {
    // Note: This links to a temporary navigation to template
        // not sure if this can be used with actual implementation? with data
    let viewAnnounce = document.querySelector('#viewAnnounce');
    viewAnnounce.onclick = function () {
        location.href = "/view-announcement";
    };
}

/** 
* Filters and search farms client side. Only verified to works for assistant manager. Code modified from: https://www.c-sharpcorner.com/article/custom-search-using-client-side-code/
* @summary Filters and searches farms for assistant manager.
*/
function filterSearch(){ 
    var input, filter, table, tr, raiser, address, area, i;        
    input   = document.getElementById("searchTextBoxid"); //to get typed in keyword    
    filter  = input.value.toUpperCase(); //to avoid case sensitive search, if case sensitive search is required then comment this line    
    table   = document.getElementById("mainTableid"); //to get the html table    
    tr      = table.getElementsByTagName("tr"); //to access rows in the table    
    
    var 
    tiss = document.getElementById("ch_TISS").checked,
    east = document.getElementById("ch_EAST").checked,
    west = document.getElementById("ch_WEST").checked;

    for(i=0;i<tr.length;i++){    
        raiser=tr[i].getElementsByTagName("td")[1];
        address=tr[i].getElementsByTagName("td")[3];
        area = tr[i].getElementsByTagName("td")[4];
        if(raiser && address && area){    
            if(
                (raiser.innerHTML.toUpperCase().indexOf(filter)>-1 || address.innerHTML.toUpperCase().indexOf(filter)>-1) && 
                (
                    (
                        (tiss && area.innerHTML.toUpperCase().indexOf("TISISI")>-1) || 
                        (east && area.innerHTML.toUpperCase().indexOf("EAST")>-1) || 
                        (west && area.innerHTML.toUpperCase().indexOf("WEST")>-1) ||
                        (!tiss && !east && !west)
                    ) 
                )
            ){    
                tr[i].style.display="";        
            }    
            else{    
                tr[i].style.display = "none";   
            }    
        }    
    }
} 

$(document).ready(function(){
    /**
    *   Hides hog raiser fname, lname, and contact input when an existing raiser is selected
    */
    $(function() {
        $('#input-exist-raiser').change(function(){
            $("#div-raiser-name").remove();
            $("#div-raiser-contact").remove();
        });
    });
});
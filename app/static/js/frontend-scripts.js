function formatDate(date) {
    var d = new Date(date),
        month = '' + (d.getMonth() + 1),
        day = '' + d.getDate(),
        year = d.getFullYear();
    
    if (month.length < 2) 
        month = '0' + month;
    if (day.length < 2) 
        day = '0' + day;

    return [year, month, day].join('-');
}

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
 * Symptoms edit button 
 */
 let symptomsEdit = document.querySelectorAll('.symptomsEdit');
 for(var i = 0; i < symptomsEdit.length; i++) { 
    symptomsEdit[i].addEventListener("click", (e)=> {
         let editParent = e.target.parentElement.parentElement.parentElement.parentElement;
         
         let dropdown = editParent.querySelector(".form-select");
         console.log(dropdown);
         let symptomsSave = editParent.querySelector(".symptomsSave");
         let symptomsEdit = editParent.querySelector(".symptomsEdit");
         
         dropdown.removeAttribute("disabled");
         symptomsSave.setAttribute("style", "display: block");
         symptomsEdit.setAttribute("style", "display: none");
     })
 }
 
 let symptomsSave = document.querySelectorAll('.symptomsSave');
 for(var i = 0; i < symptomsSave.length; i++) { 
    symptomsSave[i].addEventListener("click", (e)=> {
         let saveParent = e.target.parentElement.parentElement.parentElement.parentElement;
         let dropdown = saveParent.querySelector(".form-select");
         let symptomsSave = saveParent.querySelector(".symptomsSave");
         let symptomsEdit = saveParent.querySelector(".symptomsEdit");
 
         dropdown.setAttribute("disabled", true);
         symptomsSave.setAttribute("style", "display: none");
         symptomsEdit.setAttribute("style", "display: block");
     })
 }

/**
 * Changing style of statuses
 */
let rowStatus = document.querySelectorAll('.status');
console.log(rowStatus);
for(var i = 0; i < rowStatus.length; i++) { 
    let val = rowStatus[i].innerText;
    if( val === "Resolved" | val === "Approved") {
        rowStatus[i].classList.add("green");
    }
    else if ( val === "Active") {
        rowStatus[i].classList.add("red");
    }
    else if ( val === "Pending") {
        rowStatus[i].classList.add("yellow");
    }
    else {
        console.log("No status detected/status value invalid.")
    }
}  

/**
 * Checking for farms need inspection
 * - Checks farms last updated more than 7 days ago
 * - Highlights row to red
 */
let farmRow = document.querySelectorAll('.farm-row');
for (var i = 0; i < farmRow.length; i++) {
    let farm = farmRow[i];

    var lastUpdated = farm.querySelector('.farm-last-update');
    var date = lastUpdated.innerHTML;
    
    var newDate = new Date(formatDate(date));
    console.log(formatDate(date));
    // console.log(newDate);
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

/**
*   - Redirects user from farm list to selected farm page
*   
*   farm = value of selected farm row
*/
function viewFarm(farm) {

    try{
        url = "/selected-farm/" + farm.parentNode.parentNode.getElementsByTagName("td")[0].innerHTML;
        console.log(url);
        location.href = url;
    }catch (error){
        console.log("Something went wrong. Restarting...");
        console.log(error);
        // location.reload(true);
    }
}

/**
*   - Appends new pigpen row for when adding a new farm
*   
*   pigpen-table = table body that the row will be appended to
*/
function addPigPenRow() {
    const length = document.getElementById('pigpen-length').innerHTML;
    const width = document.getElementById('pigpen-width').innerHTML;
    const num_heads = document.getElementById('pigpen-num-heads').innerHTML;

    $("#pigpen-table").append("<tr> \
        <td data-label='Length' id='pigpen-length'> " + length + " </td> \
        <td data-label='Width' id='pigpen-width'> " + width + " </td> \
        <td data-label='No. of Pigs' id='pigpen-num-heads'> " + num_heads + " </td> \
        <td><button id='remove-pigpen-row' type='button' onclick='removePigpenRow(this)' class='secondary-btn-red'><i class='bx bx-minus'></i></button></td> \
        </tr>");
}

/*
*   - Deletes pigpen row input in Add Farm
*   
*   currRow = selected pigpen row
*   pigpen-table = table body that the row will be deleted from
*/
function removePigpenRow(currRow){

    var row = currRow.parentNode.parentNode; //get row of clicked button
    var rowIndex = row.rowIndex - 1;
    console.log("Row ID: " + rowIndex);

    var table = document.getElementById('pigpen-table');
    table.deleteRow(rowIndex);
}

/**
*   - Appends new activity row to activity table
*   
*   activity-table = table body that the row will be appended to
*/
function addActivityRow() {
    const date = document.getElementById('date').innerHTML;
    const trip_type = document.getElementById('trip_type').innerHTML;
    const time_arrival = document.getElementById('time_arrival').innerHTML;
    const time_departure = document.getElementById('time_departure').innerHTML;
    const description = document.getElementById('description').innerHTML;
    const remarks = document.getElementById('remarks').innerHTML;

    $("#activity-table").append("<tr> \
        <td data-label='Date'> " + date + " </td> \
        <td data-label='Trip Type'> " + trip_type + " </td> \
        <td data-label='Arrival Time'> " + time_arrival + " </td> \
        <td data-label='Departure Time'> " + time_departure + " </td> \
        <td data-label='Description'> " + description + " </td> \
        <td data-label='Remarks'> " + remarks + " </td> \
        <td><button id='remove-activity-row' type='button' onclick='removeActivityRow(this)' class='secondary-btn-red'><i class='bx bx-minus'></i></button></td> \
        </tr>");
}

/*
*   - Deletes activity row input in Add Activity
*   
*   currRow = selected activity row
*   activity-table = table body that the row will be deleted from
*/
function removeActivityRow(currRow){

    var row = currRow.parentNode.parentNode; //get row of clicked button
    var rowIndex = row.rowIndex - 1;
    console.log("Row ID: " + rowIndex);

    var table = document.getElementById('activity-table');
    table.deleteRow(rowIndex);
}

/**
*   - Displays input field when waste mgt option is "Others"
*   
*   option = value of option waste mgt selected (Others)
*/
function wasteMgtOther(option){
    if (option.value == "Other"){
        document.getElementById("option-other").style.display = "block";
    }
}

/**
*   - Redirects user from farm list to selected farm page
*   
*   farm = value of selected farm row
*/
function viewActivityForm(activity) {

    var actDate = activity.parentNode.parentNode.parentNode.getElementsByTagName("td")[0].innerHTML;
    // console.log(actDate);
    console.log(formatDate(actDate));
    var actFormID = activity.parentNode.parentNode.parentNode.id;
    // console.log(actFormID);

    try{
        url = "/selected-activity-form/" + actFormID + "/" + formatDate(actDate);
        console.log(url);
        location.href = url;
    }catch (error){
        console.log("Something went wrong. Restarting...");
        console.log(error);
        location.reload(true);
    }
}

/**
 *   From selected-activity-form.html
 *   - Toggle activity form approve/reject buttons on checkbox toggle
 */
let actitivty_checkbox = document.querySelectorAll('.cb-activity-form');
for(var i = 0; i < actitivty_checkbox.length; i++) { 

    actitivty_checkbox[i].addEventListener('click', (e) => {
        var isChecked = e.target.checked;

        // get activity form approve/reject buttons
        var actFormsBtn = document.getElementsByClassName('act-forms-btn');

        if(isChecked) { // enable buttons when checkbox is selected
            for(var j = 0; j < actFormsBtn.length; j++) {
                actFormsBtn[j].disabled = false;
            }   
        } else { // disable buttons when checkbox is not selected
            for(var j = 0; j < actFormsBtn.length; j++) {
                actFormsBtn[j].disabled = true;
            }
        }
        
    });
 } 

function viewAnnounce(elem) {
    // Note: This links to a temporary navigation to template
        // not sure if this can be used with actual implementation? with data
    id = $(elem).attr('id');
    location.href = "/view-announcement/"+id;
}

/** 
* Filters and search farms client side. Only verified to works for assistant manager. Code modified from: https://www.c-sharpcorner.com/article/custom-search-using-client-side-code/
* @summary Filters and searches farms for assistant manager. (farms.html)
*/
function filterSearch(){ 
    var input, filter, table, tr, raiser, address, area, i;        
    input   = document.getElementById("searchTextBoxid"); //to get typed in keyword    
    filter  = input.value.toUpperCase(); //to avoid case sensitive search, if case sensitive search is required then comment this line    
    table   = document.getElementById("mainTableid"); //to get the html table    
    tr      = table.getElementsByTagName("tr"); //to access rows in the table    

    var checkedValues = $('input:checkbox:checked.ch_area').map(function() {
        return this.id.toUpperCase();
    }).get();
    console.log(checkedValues);

    for(i=0;i<tr.length;i++){    
        raiser=tr[i].getElementsByTagName("td")[1];
        address=tr[i].getElementsByTagName("td")[3];
        area = tr[i].getElementsByTagName("td")[4];
        
        if(raiser && address && area){    
            if(
                (raiser.innerHTML.toUpperCase().indexOf(filter)>-1 || address.innerHTML.toUpperCase().indexOf(filter)>-1) 
                &&(
                    (
                        ($.inArray(area.innerHTML.toUpperCase(), checkedValues) != -1) ||
                        (checkedValues.length == 0)
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
    $('#input-exist-raiser').change(function(){
        $("#div-raiser-name").remove();
        $("#div-raiser-contact").remove();
    });
});

//---- MODULE 2 functions ----//
/** 
* Filters and search farms client side. Only verified to works for assistant manager. Code modified from: https://www.c-sharpcorner.com/article/custom-search-using-client-side-code/
* @summary Filters and searches farms for assistant manager (hogs-health.html)
*/
function filterHogsHealth(){ 
    var input, filter, table, tr, raiser, area, i;        
    input   = document.getElementById("hog_searchTextBoxid"); //to get typed in keyword    
    filter  = input.value.toUpperCase(); //to avoid case sensitive search, if case sensitive search is required then comment this line    
    table   = document.getElementById("hog_mainTableid"); //to get the html table    
    tr      = table.getElementsByTagName("tr"); //to access rows in the table    
    
    // get array of Area names in checkbox filter
    var checkedValues = $('input:checkbox:checked.ch_hog_area').map(function() {
        return this.id.toUpperCase();
    }).get();
    console.log(checkedValues);

    for(i=0;i<tr.length;i++){    
        raiser=tr[i].getElementsByTagName("td")[1];
        area = tr[i].getElementsByTagName("td")[2];
        if(raiser && area){    
            if(
                (raiser.innerHTML.toUpperCase().indexOf(filter)>-1) 
                &&(
                    (
                        ($.inArray(area.innerHTML.toUpperCase(), checkedValues) != -1) ||
                        (checkedValues.length == 0)
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

/** 
* Select all.
*/
$('#select_all').change(function() {
    var checkboxes = $(this).closest('table').find(':checkbox');
    checkboxes.prop('checked', $(this).is(':checked'));
});

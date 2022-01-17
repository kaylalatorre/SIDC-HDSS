/**
 * Helper function to format date objects 
 * for frontend display.
 * @param {date} date 
 * @returns a formatted date YYYY-MM-DD
 */
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

/**
 * Helper function to get the difference 
 * between the date passed as param and
 * the date today
 * @param {date} date 
 * @returns difference of two dates
 */
function getDiffDays(date) {
    var today = new Date();

    const diffTime = Math.abs(today - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)); 

    return diffDays;
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
         let editParent = e.target.parentElement.parentElement.parentElement;
         let dropdown = editParent.querySelector(".form-select");
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
         let saveParent = e.target.parentElement.parentElement.parentElement;
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
// console.log(rowStatus);
for(var i = 0; i < rowStatus.length; i++) { 
    let val = rowStatus[i].innerText;
    if( val === "Resolved" | val === "Approved") {
        rowStatus[i].classList.add("green");
    }
    else if ( val === "Active" | val === "Rejected") {
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
         
     var diffDays = getDiffDays(newDate);
    //  console.log(String(i+1) + " "+ String(diffDays));

     if (diffDays > 8) {
         lastUpdated.parentElement.classList.add("highlight-red");
     }
 }

 /**
 * Checking for farms with active incidents
 * - Checks if farm has more than 0 active incidents
 * - Highlights row to red
 */
  let healthRow = document.querySelectorAll('.health-row');
  for (var i = 0; i < healthRow.length; i++) {
      let farm = healthRow[i];
  
      var activeIncid = farm.querySelector('.active-incid');
      var active = activeIncid.innerText;
      console.log(activeIncid);
      if (active > 0) {
        activeIncid.parentElement.classList.add("highlight-red");
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

/**
*   - Redirects user from farm list to selected farm page
*   
*   farm = value of selected farm row
*/
function viewFarm(farm) {

    try{
        url = "/selected-farm/" + farm.parentNode.parentNode.getElementsByTagName("td")[0].innerHTML;
        location.href = url;
    }catch (error){
        console.log(error);
    }
}

/**
*   - Redirects current user (technician) to the selected farm. 
*   - Appends selected farm ID to url that will display farm details.
*   
*   techFarm = row of selected farm
*/
function viewTechFarm(techFarm) {

    try{
        url = "/tech-selected-farm/" + techFarm.parentNode.parentNode.getElementsByTagName("td")[0].innerHTML;
        location.href = url;
    } catch (error){
        console.log(error);
    }
}

/**
*   - Redirects current user to the selected farm version 
*   - Appends selected farm ID and farm version to URL
*   - Will display pigpens of selected farm version
*/
$('#farm-version').change(function () {

    var value = document.getElementById("farm-version").value;
    // console.log(value);

    var split = value.split("-");
    var farmID = split[0];
    var farmVer = split[1];

    // console.log("Farm ID: " + farmID);
    // console.log("Farm Version: " + formatDate(farmVer));

    try {
        url = "/selected-farm/" + farmID + '/' + formatDate(farmVer);
        location.href = url;
    } catch (error) {
        console.log(error);
    }
})

/**
*   - Redirects current user (technician) to the selected farm version 
*   - Appends selected farm ID and farm version to URL
*   - Will display pigpens of selected farm version
*/
$('#tech-farm-version').change(function () {

    var value = document.getElementById("tech-farm-version").value;
    // console.log(value);

    var split = value.split("-");
    var farmID = split[0];
    var farmVer = split[1];

    // console.log("Farm ID: " + farmID);
    // console.log("Farm Version: " + formatDate(farmVer));

    try {
        url = "/tech-selected-farm/" + farmID + '/' + formatDate(farmVer);
        location.href = url;
    } catch (error) {
        console.log(error);
    }
})

/**
*   - Redirects current technician from biosecurity page to add-checklist page for selected farm.
*   - Appends selected farm ID to url that will display an empty biosecurity checklist.
*   
*   farmID = button value (carries ID of selected farm)
*/
function addBiosecPage(farmID) {

    var techFarm = $(farmID).val(); 
    console.log(techFarm)

    try{
        url = "/add-checklist/" + techFarm;
        location.href = url;
    } catch (error){
        console.log(error);
    }
}

/**
*   - Redirects current technician from biosecurity page to add-activity page for selected farm.
*   - Appends selected farm ID to url that will display an empty activity record.
*   
*   farmID = button value (carries ID of selected farm)
*/
function addActivityPage(farmID) {

    var techFarm = $(farmID).val(); 
    console.log(techFarm)

    try{
        url = "/add-activity/" + techFarm;
        location.href = url;
    } catch (error){
        console.log(error);
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
function removeMortalityRow(currRow){

    var row = currRow.parentNode.parentNode; //get row of clicked button
    var rowIndex = row.rowIndex - 1;
    console.log("Row ID: " + rowIndex);

    var table = document.getElementById('mortality-table');
    table.deleteRow(rowIndex);
}

/**
*   - Appends new activity row to activity table
*   
*   activity-table = table body that the row will be appended to
*/
function addMortalityRow() {
    const mortality_date = document.getElementById('mortality_date').innerHTML;
    const num_begInv = document.getElementById('begInv').innerHTML;
    const num_today = document.getElementById('today').innerHTML;
    // const num_toDate = document.getElementById('num_toDate').innerHTML;
    const source = document.getElementById('source').innerHTML;
    const remarks = document.getElementById('remarks').innerHTML;
    // const mortality_rate = document.getElementById('mortality_rate').innerHTML;

    $("#mortality-table").append("<tr> \
        <td data-label='Mortality Date'> " + mortality_date + " </td> \
        <td data-label='Beg. Inv.' id='begInv' class='num_begInv'> " + num_begInv + " </td> \
        <td data-label='Today' id='today' onchange='computeMortality(this)'> " + num_today + " </td> \
        <td data-label='To Date'> <p class='num_toDate'></p> </td> \
        <td data-label='Source'> " + source + " </td> \
        <td data-label='Remarks'> " + remarks + " </td> \
        <td data-label='Mortality Rate' style='text-align: right;'> <p class='mortality_rate'></p> </td> \
        <td><button id='remove-mortality-row' type='button' onclick='removeMortalityRow(this)' class='secondary-btn-red'><i class='bx bx-minus'></i></button></td> \
        </tr>");
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
*   - Redirects user from forms approval page to selected activity form page
*   
*   activity = selected activity row
*/
function viewActivityForm(activity) {

    var actDate = activity.parentNode.parentNode.parentNode.getElementsByTagName("td")[0].innerHTML;
    var actFormID = activity.parentNode.parentNode.parentNode.id;

    try{
        url = "/selected-activity-form/" + actFormID + "/" + formatDate(actDate);
        location.href = url;
    }catch (error){
        console.log(error);
    }
}

/**
*   - Redirects current user to the selected activity form version
*   - Appends selected activity form ID and form version to URL
*/
$('#actform-version').change(function () {

    var value = document.getElementById("actform-version").value;

    var split = value.split("-");
    var actformID = split[0];
    var actformDate = split[1];

    try {
        url = "/selected-activity-form/" + actformID + '/' + formatDate(actformDate);
        location.href = url;
    } catch (error) {
        console.log(error);
    }
})

function viewAnnounce(elem) {
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

/** 
* Checkbox filters incident reports according to status for technician view (selected-health-symptoms.html)
* Code modified from: https://www.c-sharpcorner.com/article/custom-search-using-client-side-code/
*/
function filterRepStatus(){ 
    var i;
    var repStatus;          

    var incidentRows = document.getElementsByClassName('incident-row');
    
    
    // get array of report_status text in checkbox filter
    var checkedValues = $('input:checkbox:checked.ch_stat').map(function() {
        return this.id.toUpperCase();
    }).get();
    console.log(checkedValues);
    console.log(incidentRows.length)
    // console.log(table);

    for(i=0;i<incidentRows.length;i++){    
        repStatus = incidentRows[i].getElementsByTagName("td")[4].firstElementChild.value;
        // repStatus = repStatusRow

        console.log(repStatus);

        if(repStatus){    
            if(
                (
                    (
                        ($.inArray(repStatus.toUpperCase(), checkedValues) != -1) ||
                        (checkedValues.length == 0)
                    ) 
                )
            ){    
                incidentRows[i].style.display="";        
            }    
            else{    
                incidentRows[i].style.display = "none";   
            }    
        }    
    }
} 

/**
 *   - Redirects current technician from selected health symptoms page to add-case page for selected farm.
 *   - Appends selected farm ID to url that will display an empty symptoms checklist.
 *   
 *   farmID = button value (carries ID of selected farm)
 */
 function addSymptomsPage(farmID) {

    var farmID = $(farmID).val();
    console.log(farmID);

    try {
        url = "/add-case/" + farmID;
        location.href = url;
    } catch (error) {
        location.reload(true);
    }
}

/**
 *   - Redirects current technician from selected health symptoms page to add-mortality page for selected farm.
 *   
 *   farmID = button value (carries ID of selected farm)
 */
 function addMortalityPage(farmID) {

    var farmID = $(farmID).val();

    try {
        url = "/add-mortality/" + farmID;
        location.href = url;
    } catch (error) {
        console.log(error);
    }
}

/**
 *   - Hides current pigpen data
 *   - Display pigpen input (django form)
 */
 function showPigpenInput() {
    var toShow = document.getElementsByClassName("pigpen-input");
    var toHide = document.getElementsByClassName("pigpen-data");

    for (var i = 0; i < toHide.length; i++) {
        toHide[i].style.display = "none";
    }
    for (var i = 0; i < toShow.length; i++) {
        toShow[i].style.display = "block";
    }

}

/**
 *   - Cancel adding of new pigpen
 *   - Hide pigpen input and display current pigpens
 */
 function cancelAddPigpen() {
    var toHide = document.getElementsByClassName("pigpen-input");
    var toShow = document.getElementsByClassName("pigpen-data");

    for (var i = 0; i < toHide.length; i++) {
        toHide[i].style.display = "none";
    }
    for (var i = 0; i < toShow.length; i++) {
        toShow[i].style.display = "block";
    }

}

/**
*   - Redirects current user to the selected hogs health version 
*   - Appends selected farm ID and farm version to URL
*   - Will display weight slips, incidents, and mortality records of selected farm version
*/
$('#hogs-health-version').change(function () {

    var value = document.getElementById("hogs-health-version").value;
    // console.log(value);

    var split = value.split("-");
    var farmID = split[0];
    var farmVer = split[1];

    // console.log("Farm ID: " + farmID);
    // console.log("Farm Version: " + formatDate(farmVer));

    try {
        url = "/selected-hogs-health/" + farmID + '/' + formatDate(farmVer);
        location.href = url;
    } catch (error) {
        console.log(error);
    }
})

/**
*   - Redirects current user (tecnician) to the selected hogs health & symptoms version 
*   - Appends selected farm ID and farm version to URL
*   - Will display incidents, and mortality records of selected farm version
*/
$('#health-symptoms-version').change(function () {

    var value = document.getElementById("health-symptoms-version").value;
    // console.log(value);

    var split = value.split("-");
    var farmID = split[0];
    var farmVer = split[1];

    console.log("Farm ID: " + farmID);
    console.log("Farm Version: " + formatDate(farmVer));

    try {
        url = "/selected-health-symptoms/" + farmID + '/' + formatDate(farmVer);
        location.href = url;
    } catch (error) {
        console.log(error);
    }
})


/**
 * Compute for the toDate and mortality rate
 * @param {*} currRow 
 */
function computeMortality(currRow){
    var row = currRow.parentNode; //get row of clicked button
    // console.log(row)

    var begInv = row.getElementsByClassName('num_begInv')[0].innerHTML;
    var today = row.getElementsByClassName('num_today')[0].value;
    // console.log("today: " + String(begInv));
    // console.log("today: " + String(today));

    var newTotal = parseInt(begInv) - parseInt(today);
    var toDate = row.getElementsByClassName('num_toDate')[0];
    // console.log(toDate);

    toDate.innerText = newTotal;
    console.log("toDate: " + String(toDate));


    var mortRate = newTotal / parseInt(begInv) * 100
    var mortality_rate = row.getElementsByClassName('mortality_rate')[0];
    // console.log(mortality_rate);

    if (parseInt(today) == parseInt(begInv))
        mortRate = 100;
    else
        mortRate = 0;

    mortality_rate.innerText = mortRate.toFixed(2);
    console.log("mortality_rate: " + String(mortalzity_rate));
}
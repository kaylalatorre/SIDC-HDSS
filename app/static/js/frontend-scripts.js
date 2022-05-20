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

//---- MODULE 1 functions ----//

/* 
* Tech assignment edit button 
*/

let pendingAct = document.querySelector('#pending-activities'); // container of pending activities

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

        pendingAct.classList.add("show");
        pendingAct.classList.remove("hide");
        //console.log(pendingAct);
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

        pendingAct.classList.add("hide");
        pendingAct.classList.remove("show");
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
        // console.log(biosecEdit);
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
* Enable submit button when text is inputted for selected-activity
*/
function EnableRejectSave(text) {
    var btnSubmit = document.getElementById("reject-activity");

    if (text.value.trim() != "") {
        //enable the TextBox when TextBox has value
        btnSubmit.disabled = false;
    } else {
        //disable the TextBox when TextBox is empty
        btnSubmit.disabled = true;
    }
};

/**
* Enable save button when text is inputted for selected-health-symptoms
*/
function EnableRecSave(text) {
    var row = text.parentNode.parentNode.parentNode;
    var btnSave = row.getElementsByClassName("secondary-btn showDisInput")[0];
    // console.log(row);
    // console.log(btnSave);

    if (text.value.trim() > 0)
        btnSave.disabled = false;
    else btnSave.disabled = true;
};

function EnableIncidRem(text) {
    var row = text.parentNode.parentNode.parentNode;
    var rowIndex = row.rowIndex - 1;

    var btnSubmit = document.getElementsByClassName("symptomsSave")[rowIndex];

    if (text.value.trim() != "") {
        //enable the TextBox when TextBox has value
        btnSubmit.disabled = false;
    } else {
        //disable the TextBox when TextBox is empty
        btnSubmit.disabled = true;
    }
};

/**
*   - Hide text and update button
*   - Show input and save button
**/ 
function UpdateTotalRec(btnHTML){

    var row = btnHTML.parentNode.parentNode.parentNode;

    // console.log(row);

    var toHide = row.getElementsByClassName('hideDisInfo');
    var toShow = row.getElementsByClassName('showDisInput');

    // console.log(toHide);
    // console.log(toShow);

    for(i = 0; i < toHide.length; i++)
        toHide[i].style.display = "none";
    
    for(j = 0; j < toShow.length; j++)
        toShow[j].style.display = "block";
}

function CancelRecSave(btnHTML){

    var row = btnHTML.parentNode.parentNode.parentNode;

    var toShow = row.getElementsByClassName('hideDisInfo');
    var toHide = row.getElementsByClassName('showDisInput');

    for(i = 0; i < toHide.length; i++)
        toHide[i].style.display = "none";
    
    for(j = 0; j < toShow.length; j++)
        toShow[j].style.display = "block";
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

        //  for onchange of incident case dropdown status
         dropdown.addEventListener("change", (e)=> {
            let remarksInput = e.target.parentElement.parentElement.childNodes[4].nextSibling;
            // console.log(e.target.value);
            // console.log(remarksInput);

            if (e.target.value == "Resolved") {
                // console.log(remarksInput);
                remarksInput.classList.remove("hide");
                remarksInput.classList.add("show");
                symptomsSave.disabled = true;
            }
            else {
                remarksInput.classList.remove("show");
                remarksInput.classList.add("hide");
            }
         })
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
    //   console.log(activeIncid);
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
        //  console.log(isChecked);
         if(isChecked) {
             btnGrp.classList.remove('hide');
         } else {
             btnGrp.classList.add('hide');
         }
         
     });
 }   

 /**
 * Toggling view of Laboratory Results and Reference input for Tentative Diagnosis
 */
let refBtn = document.querySelectorAll('.result-ref-btn');

for(var i = 0; i < refBtn.length; i++) { 
    refBtn[i].addEventListener('click', (e) => {
       var refInput = e.target.parentNode.nextElementSibling;
    //    var refInput = document.querySelector('.diagnosis-result-ref')

       e.target.classList.add('hide');
       refInput.classList.add('show');
       e.target.classList.remove('show');
       refInput.classList.remove('hide');
    });
}

let cancelRefBtn = document.querySelectorAll('.cancel-ref-btn');
for(var i = 0; i < cancelRefBtn.length; i++) { 
    cancelRefBtn[i].addEventListener('click', (e) => {
       var refInput = e.target.parentNode.parentNode.parentElement;
    //    var refInput = document.querySelector('.diagnosis-result-ref')
       var inputBtn = refInput.parentElement.querySelector('.result-ref-btn');
       
       // e.target.classList.add('hide');
       refInput.classList.add('hide');
       refInput.classList.remove('show');
       inputBtn.classList.add('show');
       inputBtn.classList.remove('hide');
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

    try {
        url = "/selected-farm/" + farmID + '/' + farmVer;
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

    try {
        url = "/tech-selected-farm/" + farmID + '/' + farmVer;
        location.href = url;
    } catch (error) {
        console.log(error);
    }
})

$('#tech-farm-version-mobile').change(function () {

    var value = document.getElementById("tech-farm-version-mobile").value;
    // console.log(value);

    var split = value.split("-");
    var farmID = split[0];
    var farmVer = split[1];

    try {
        url = "/tech-selected-farm/" + farmID + '/' + farmVer;
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
    // console.log(techFarm)

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
    // console.log(techFarm)

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
    // console.log("Row ID: " + rowIndex);

    var table = document.getElementById('pigpen-table');
    table.deleteRow(rowIndex);
}

/*
*   Compute for total hogs for every input of num_heads in adding pigpens
*/
function computePigpens(){

    var today = document.getElementsByClassName('num_heads').value;
    console.log(today)
    var total_pigs = document.getElementById('total_pigs').innerHTML;
    console.log(total_pigs)
    var newTotal = parseInt(total_pigs);

    for (var i = 0; i < today.length; i++){
        newTotal += parseInt(today[i]);
    }

    total_pigs.innerText = newTotal;
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
    // console.log("Row ID: " + rowIndex);

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
    const num_pigs_inv = document.getElementById('num_pigs_inv').innerHTML;
    const remarks = document.getElementById('remarks').innerHTML;

    $("#activity-table").append("<tr> \
        <td data-label='Trip Type'> " + trip_type + " </td> \
        <td data-label='Date'> " + date + " </td> \
        <td data-label='Arrival Time'> " + time_arrival + " </td> \
        <td data-label='Departure Time'> " + time_departure + " </td> \
        <td data-label='Num Pigs Involved'> " + num_pigs_inv + " </td> \
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
    // console.log("Row ID: " + rowIndex);

    var table = document.getElementById('mortality-table');
    table.deleteRow(rowIndex);
}

/**
*   - Appends new activity row to activity table
*   
*   activity-table = table body that the row will be appended to
*/
function addMortalityRow() {

    const table = document.getElementById('mortTable');
    var rowNum = table.tBodies[0].rows.length;
    // console.log(rowNum);
    
    const mortality_date = document.getElementById('mortality_date').innerHTML;
    const num_begInv = document.getElementById('begInv').innerHTML;
    const num_today = document.getElementById('today').innerHTML;
    const case_no = document.getElementById('case_no').innerHTML;
    const remarks = document.getElementById('remarks').innerHTML;

    $("#mortality-table").append("<tr> \
        <td data-label='Mortality Date'> " + mortality_date + " </td> \
        <td data-label='Beg. Inv.' id='begInv' class='num_begInv'> " + num_begInv + " </td> \
        <td data-label='Today' id='today' onchange='computeMortality(this)'> " + num_today + " </td> \
        <td data-label='To Date'> <p class='num_toDate'></p> </td> \
        <td data-label='Mortality Rate' style='text-align: right;'> <p class='mortality_rate'></p> </td> \
        <td data-label='Source'> <div class='form-check form-check-inline'> \
                <input class='form-check-input' type='radio' name='sourceOptions-"+rowNum+"' id='src-incident' value='Incident Case' onclick='switchMortCase(this)'> \
                <label class='form-check-label' for='src-incident'>Incident Case</label> </div> \
            <div class='form-check form-check-inline'> \
                <input class='form-check-input' type='radio' name='sourceOptions-"+rowNum+"' id='src-disease' value='Disease Case' onclick='switchMortCase(this)'> \
                <label class='form-check-label' for='src-disease'>Disease Case</label> </div> \
            <div class='form-check form-check-inline'> \
                <input class='form-check-input' type='radio' name='sourceOptions-"+rowNum+"' id='src-unknown' value='Unknown' onclick='switchMortCase(this)'> \
                <label class='form-check-label' for='src-unknown'>Unknown</label> </div> </td> \
        <td data-label='Case-No'> " + case_no + " </td> \
        <td data-label='Remarks'> " + remarks + " </td> \
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
 *  Show/Hide Reason for Rejection input for Activity Form
 */
 function toggleRejectReason() {
    const reason = $('.reject-reason');
    const approve = $('#approveBtn');
    const reject = $('#rejectBtn');
    const cancelBtn = $('#cancelBtn');
    
    if(reason.hasClass('hide')) {
        reason.removeClass('hide').addClass('show');
        approve.addClass('hide').removeClass('show');
        reject.addClass('hide').removeClass('show');
        cancelBtn.addClass('show').removeClass('hide');
    }
    else {
        reason.removeClass('show').addClass('hide');
        approve.addClass('show').removeClass('hide');
        reject.addClass('show').removeClass('hide');
        cancelBtn.addClass('hide').removeClass('show');
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

    var checkedMem = $('input:checkbox:checked.ch_mem').map(function() {
        return this.id.toUpperCase();
    }).get();
    console.log(checkedMem);

    for(i=0;i<tr.length;i++){    
        raiser=tr[i].getElementsByTagName("td")[1];
        address=tr[i].getElementsByTagName("td")[3];
        area = tr[i].getElementsByTagName("td")[4];
        memcode = tr[i].getElementsByTagName("td")[8];
        
        console.log(memcode)

        if(raiser && address && area && memcode){    
            if(
                (raiser.innerHTML.toUpperCase().indexOf(filter)>-1 || address.innerHTML.toUpperCase().indexOf(filter)>-1) 
                &&(
                    (
                        ($.inArray(area.innerHTML.toUpperCase(), checkedValues) != -1) ||
                        (checkedValues.length == 0)
                    )
                )
                &&(
                    (
                        ($.inArray(memcode.innerHTML.toUpperCase(), checkedMem) != -1) ||
                        (checkedMem.length == 0)
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
*   Hides hog raiser fname, lname, and contact input when an existing raiser is selected
*/
$('#input-exist-raiser').change(function(){
    $("#div-raiser-name").remove();
    $("#div-raiser-contact").remove();
    $("#div-mem-code").remove();
});

$(document).ready(function(){
    $(function(){
        // load fattener table rows according to total_pigs
        var list = $("#fattenerTable");
        var rowNum = parseInt($("#total_pigs").text());
        var resultHtml = '';
        
        // console.log($("#total_pigs"));

        for(var i = 0 ; i < rowNum ; i++) {
            resultHtml += ["<li>",
            "<div class='mb3'>", 
            "<label style='font-weight: 600;'>", (i+1), "</label>",
            '<input type="number" class="form-control fattener-weight" onchange="computeWeight(this)" name="input-kls" id="input-kls" placeholder="ex. 100" step=0.01>',
            '</div>',
            '</li>'].join("\n");
        }  
        
        list.html(resultHtml);
        return false; 
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
    // console.log(checkedValues);
    // console.log(incidentRows.length)
    // console.log(table);

    for(i=0;i<incidentRows.length;i++){    
        repStatus = incidentRows[i].getElementsByTagName("td")[4].firstElementChild.value;
        // repStatus = repStatusRow

        // console.log(repStatus);

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
    // console.log(farmID);

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
        toHide[i].style.display = "none"; }

    for (var i = 0; i < toShow.length; i++) {
        toShow[i].style.display = "block"; }

}

/**
 *   - Cancel adding of new pigpen
 *   - Hide pigpen input and display current pigpens
 */
 function cancelAddPigpen() {
    var toHide = document.getElementsByClassName("pigpen-input");
    var toShow = document.getElementsByClassName("pigpen-data");

    for (var i = 0; i < toHide.length; i++) {
        toHide[i].style.display = "none"; }

    for (var i = 0; i < toShow.length; i++) {
        toShow[i].style.display = "block"; }

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

    try {
        url = "/selected-hogs-health/" + farmID + '/' + farmVer;
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

    try {
        url = "/selected-health-symptoms/" + farmID + '/' + farmVer;
        location.href = url;
    } catch (error) {
        console.log(error);
    }
})

$('#health-symptoms-version-mobile').change(function () {

    var value = document.getElementById("health-symptoms-version-mobile").value;
    // console.log(value);

    var split = value.split("-");
    var farmID = split[0];
    var farmVer = split[1];

    try {
        url = "/selected-health-symptoms/" + farmID + '/' + farmVer;
        location.href = url;
    } catch (error) {
        console.log(error);
    }
})

/**
 * Compute for total recovered pigs given a num_recovered input
 * @param {*} currRow 
 */
function computeTotalRec(currRow){
    var row = currRow.parentNode; //get row of clicked button
    // console.log("in computeTotalRec()/n");

    var num_rec = row.getElementsByClassName('input-num-rec')[0].value;
    var total_rec = row.getElementsByClassName('total-rec')[0].innerHTML;
    var displayRec = row.parentNode.nextElementSibling.getElementsByClassName('display-total-rec')[0];
    // console.log("num_rec: " + num_rec);
    // console.log("total_rec: " + total_rec);

    var new_total_rec = parseInt(num_rec) + parseInt(total_rec); 
    // console.log("new_total_rec: " + new_total_rec);

    // console.log(displayRec);
    displayRec.innerHTML = String(new_total_rec);

    // setting input max
    var num_pigs_affect = row.parentNode.childNodes[11].innerHTML;
    var total_died = row.parentNode.nextElementSibling.getElementsByClassName('display-total-died')[0].innerHTML;
    // console.log("num_pigs_affect: " + num_pigs_affect);
    // console.log("total_died: " + total_died);
    
    var maxInput = parseInt(num_pigs_affect) - (parseInt(total_rec) + parseInt(total_died));

    $(".input-num-rec"). attr({
        "max" : maxInput, 
        });
}


/**
 * Compute for the toDate and mortality rate
 * @param {*} currRow 
 */
function computeMortality(currRow){
    var row = currRow.parentNode; //get row of clicked button
    console.log(row.rowIndex);

    var begInv = row.getElementsByClassName('num_begInv')[0].innerHTML;
    var today = row.getElementsByClassName('num_today')[0].value;
    var latest_toDate = document.getElementById('latest_toDate').innerHTML;
    var toDate = row.getElementsByClassName('num_toDate')[0];

    // console.log("begInv: " + String(begInv));
    // console.log("today: " + String(today));
    // console.log(latest_toDate);

    var newTotal = parseInt(today) + parseInt(latest_toDate); 
    // console.log(newTotal);    

    toDate.innerHTML = String(newTotal);
    // console.log("toDate: " + String(toDate));


    var mortality_rate = row.getElementsByClassName('mortality_rate')[0];

    if (parseInt(newTotal) == parseInt(begInv))
        var mortRate = 100;
    else if (parseInt(today) == 0)
        var mortRate = 0;
    else
        var mortRate = parseInt(newTotal) / parseInt(begInv) * 100

    mortality_rate.innerText = mortRate.toFixed(2);
    // console.log("mortality_rate: " + String(mortality_rate));
}

/**
 * Compute for the total weight and average weight for fattener pigs
 */
 function computeWeight(){

    var weight = document.getElementsByClassName('fattener-weight');  
    // console.log(weight);
    
    var total = 0;
    var average = 0;

    for (var i=0; i < weight.length; i++){
        // console.log(weight[i].value);
        if (weight[i].value != ""){
            total += parseFloat(weight[i].value);
            average = parseFloat(total)/(i+1)
        }
    }

    console.log(total);
    console.log(average);

    var totalVal = document.getElementsByClassName('fattener-total')[0];
    var averageVal = document.getElementsByClassName('fattener-average')[0];

    totalVal.innerText = total.toFixed(2);
    averageVal.innerText = average.toFixed(2);
}

/**
 *  Switches the options in add-mortality cases depending on selected source
 *  Will hide and display the corresponding incident or diseases cases
  * @param {*} caseVal = value of selected radio button (source) 
 */
function switchMortCase(caseVal){
    var row = caseVal.parentNode.parentNode.parentNode; //get row of radio button set
    // console.log(row);
    // console.log(row.rowIndex);

    var incidCase = row.getElementsByClassName("incident-case");
    var disCase = row.getElementsByClassName("disease-case");
    var dropDown = row.getElementsByClassName("input-case")[0];

    // console.log(caseVal.value);
    // console.log(dropDown);

    if(String(caseVal.value) === "Incident Case") {
        for(i = 0; i < disCase.length; i++)
            disCase[i].style.display = "none";
    
        for(j = 0; j < disCase.length; j++)
            incidCase[j].style.display = "block";
            dropDown.selectedIndex = "0";
    }
    else if(String(caseVal.value) === "Disease Case") {
        for(i = 0; i < disCase.length; i++)
            disCase[i].style.display = "block";
            dropDown.selectedIndex = "0";

        for(j = 0; j < disCase.length; j++)
            incidCase[j].style.display = "none";
    }
    else { // chosen source is unknown, hide all cases
        for(i = 0; i < disCase.length; i++)
            disCase[i].style.display = "none";
    
        for(j = 0; j < disCase.length; j++){
            incidCase[j].style.display = "none";
            dropDown.selectedIndex = "0";
        }
    }
    
}
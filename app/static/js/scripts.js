/* Tech assignment edit button */
let edit = document.querySelectorAll('.assignEdit');
for(var i = 0; i < edit.length; i++) { 
    edit[i].addEventListener("click", (e)=> {
        let editParent = e.target.parentElement.parentElement.parentElement;
        let editDropdown = editParent.querySelector(".form-select");
        let assignSave = editParent.querySelector(".assignSave");
        let assignEdit = editParent.querySelector(".assignEdit");

        editDropdown.removeAttribute("disabled");
        assignSave.setAttribute("style", "display: block");
        assignEdit.setAttribute("style", "display: none");
    })
}

let save = document.querySelectorAll('.assignSave');
for(var i = 0; i < save.length; i++) { 
    save[i].addEventListener("click", (e)=> {
        let saveParent = e.target.parentElement.parentElement.parentElement;
        let saveDropdown = saveParent.querySelector(".form-select");
        let assignSave = saveParent.querySelector(".assignSave");
        let assignEdit = saveParent.querySelector(".assignEdit");

        saveDropdown.setAttribute("disabled", true);
        assignSave.setAttribute("style", "display: none");
        assignEdit.setAttribute("style", "display: block");
    })
}

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
    const time_departure = document.getElementById('time_departure').innerHTML;
    const time_arrival = document.getElementById('time_arrival').innerHTML;
    const description = document.getElementById('description').innerHTML;
    const remarks = document.getElementById('remarks').innerHTML;

    $("#input-act").append("<tr> \
        <td data-label='Date'> " + date + " </td> \
        <td data-label='Trip Type'> " + trip_type + " </td> \
        <td data-label='Departure Time'> " + time_departure + " </td> \
        <td data-label='Arrival Time'> " + time_arrival + " </td> \
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
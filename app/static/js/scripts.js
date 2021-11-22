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
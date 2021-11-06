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

// MGIHT BE BACKEND
function viewTechFarm() {
    // Note: This links to a temporary navigation to template
        // not sure if this can be used with actual implementation? with data
    let viewFarm = document.querySelector('#viewTechFarm');
    viewFarm.onclick = function () {
        location.href = "/tech-selected-farm";
    };
}

function viewFarm() {
    // Note: This links to a temporary navigation to template
        // not sure if this can be used with actual implementation? with data
    let viewFarm = document.querySelector('#viewFarm');
    viewFarm.onclick = function () {
        location.href = "/selected-farm";
    };
}

function viewForm() {
    // Note: This links to a temporary navigation to template
        // not sure if this can be used with actual implementation? with data
    let viewFarm = document.querySelector('#viewForm');
    viewFarm.onclick = function () {
        location.href = "/selected-form";
    };
}
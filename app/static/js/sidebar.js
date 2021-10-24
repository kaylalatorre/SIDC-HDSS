/* Toggling the dropdown menu */
let arrow = document.querySelectorAll('.arrow');
for(var i =0; i < arrow.length; i++) {
    arrow[i].addEventListener("click", (e)=> {
        let arrowParent = e.target.parentElement.parentElement;
        arrowParent.classList.toggle("showMenu");
    })
}

/* Toggling sidebar */
let sidebar = document.querySelector('.sidebar');
let sidebarBtn = document.querySelector('.bx-menu');
console.log(sidebar);
sidebarBtn.addEventListener("click", ()=> {
    sidebar.classList.toggle("close");
})

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

/* For currently selected nav -- not yet working */
let navItems = document.querySelectorAll('.nav-item');
for(var i =0; i < arrow.length; i++) {
    navItems[i].addEventListener("click", (e)=> {
        let current = e;
        current.classList.toggle("nav-item nav-current");
    })
}
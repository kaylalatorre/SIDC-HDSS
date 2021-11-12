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
sidebarBtn.addEventListener("click", ()=> {
    sidebar.classList.toggle("close");
    sidebar.classList.remove("rp-close");
})

/* Toggling responsive sidebar */
let sidebarClose = document.querySelector('#sidebar-close');
sidebarClose.addEventListener("click", ()=> {
    sidebar.classList.add("rp-close");
    sidebar.classList.add("close");

})

/* For currently selected nav -- not yet working */
let navItems = document.querySelectorAll('.nav-item');
for(var i =0; i < arrow.length; i++) {
    navItems[i].addEventListener("click", (e)=> {
        let current = e;
        current.classList.toggle("nav-item nav-current");
    })
}


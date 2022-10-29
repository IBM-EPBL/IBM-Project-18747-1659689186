// Navbar active toggler
const pathname= window.location.pathname;
window.addEventListener("load", function() {
if(pathname==="/"){
    document.getElementById("dashboard").className="nav-item active";
}else if(pathname==="/products"){
    document.getElementById("products").className="nav-item active";
}else if(pathname==="/people"){
    document.getElementById("people").className="nav-item active";
}
});
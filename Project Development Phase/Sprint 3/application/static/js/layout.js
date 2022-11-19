// Navbar active toggler


const pathname = window.location.pathname;

window.addEventListener("load", function () {


  if ((window.fullScreen) ||
    (window.innerWidth == screen.width && window.innerHeight == screen.height)) {
      console.log("the screen is in fullscreen");
      var expand = document.getElementById("expand");
      const li = document.createElement("li");
      li.className = "nav-item";
      const i = document.createElement("i");
      i.className = "fa-solid fa-expand";
      li.appendChild(i);
      expand.replaceChild(li, expand.childNodes[1]);

  } else {
    console.log("The screen in not in the fullscreen");
    var expand = document.getElementById("expand");
    const li = document.createElement("li");
    li.className = "nav-item";
    const i = document.createElement("i");
    i.className = "fa-solid fa-compress";
    li.appendChild(i);
  }

  if (pathname === "/" || pathname === "/dashboard") {
    document.getElementById("dashboard").className = "nav-item active";
  } else if (pathname === "/products") {
    document.getElementById("products").className = "nav-item active";
  } else if (pathname === "/people") {
    document.getElementById("people").className = "nav-item active";
  }

});

// Fullscreen Option

var elem = document.documentElement;

function expand() {

  var expand = document.getElementById("expand");

  if (window.innerHeight == screen.height) {
    // browser is already in fullscreen

    // closeFullscreen

    if (document.exitFullscreen) {
      document.exitFullscreen();
    } else if (document.webkitExitFullscreen) { /* Safari */
      document.webkitExitFullscreen();
    } else if (document.msExitFullscreen) { /* IE11 */
      document.msExitFullscreen();
    }

    // Changing icon
    const li = document.createElement("li");
    li.className = "nav-item";
    const i = document.createElement("i");
    i.className = "fa-solid fa-expand";
    li.appendChild(i);
    expand.replaceChild(li, expand.childNodes[1]);
  }
  else {
    // openFullscreen
    if (elem.requestFullscreen) {
      elem.requestFullscreen();
    } else if (elem.webkitRequestFullscreen) { /* Safari */
      elem.webkitRequestFullscreen();
    } else if (elem.msRequestFullscreen) { /* IE11 */
      elem.msRequestFullscreen();
    }

    // Changing icon
    const li = document.createElement("li");
    li.className = "nav-item";
    const i = document.createElement("i");
    i.className = "fa-solid fa-compress";
    li.appendChild(i);
    expand.replaceChild(li, expand.childNodes[1]);
  }

}




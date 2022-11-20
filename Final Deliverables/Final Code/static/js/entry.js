window.addEventListener("load", function () {
    const sign_in_btn = document.querySelector("#sign-in-btn");
    const sign_up_btn = document.querySelector("#sign-up-btn");
    const container = document.querySelector(".container");
    const sign_in_btn2 = document.querySelector("#sign-in-btn2");
    const sign_up_btn2 = document.querySelector("#sign-up-btn2");

    sign_up_btn.addEventListener("click", () => {
        container.classList.add("sign-up-mode");
    });

    sign_in_btn.addEventListener("click", () => {
        container.classList.remove("sign-up-mode");
    });

    sign_up_btn2.addEventListener("click", () => {
        container.classList.add("sign-up-mode2");
    });
    sign_in_btn2.addEventListener("click", () => {
        container.classList.remove("sign-up-mode2");
    });
});

function myfunction() {
    const togglePassword = document.querySelector('#togglePassword');
    const password = document.querySelector('#password');
    togglePassword.addEventListener('click', () => {
        const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
        password.setAttribute('type', type);
        if (password.getAttribute('type') !== 'password') {
            togglePassword.className = 'fa-solid fa-eye-slash field-icon toggle-password';
        } else {
            togglePassword.className = 'fa-solid fa-eye field-icon toggle-password';
        }
    });
}

function myfunction1() {
    const togglePassword1 = document.querySelector('#togglePassword1');
    const togglePassword2 = document.querySelector('#togglePassword2');
    const password1 = document.querySelector('#password1');
    const cpassword = document.querySelector('#cpassword');
    togglePassword1.addEventListener('click', () => {
        const type = password1.getAttribute('type') === 'password' ? 'text' : 'password';
        password1.setAttribute('type', type);
        if (password1.getAttribute('type') !== 'password') {
            togglePassword1.className = 'fa-solid fa-eye-slash field-icon toggle-password';
        } else {
            togglePassword1.className = 'fa-solid fa-eye field-icon toggle-password';
        }
        const ctype = cpassword.getAttribute('type') === 'password' ? 'text' : 'password';
        cpassword.setAttribute('type', ctype);
        if (cpassword.getAttribute('type') !== 'password') {
            togglePassword2.className = 'fa-solid fa-eye-slash field-icon toggle-password';
        } else {
            togglePassword2.className = 'fa-solid fa-eye field-icon toggle-password';
        }
    });

    togglePassword2.addEventListener('click', () => {
        const type = password1.getAttribute('type') === 'password' ? 'text' : 'password';
        password1.setAttribute('type', type);
        if (password1.getAttribute('type') !== 'password') {
            togglePassword1.className = 'fa-solid fa-eye-slash field-icon toggle-password';
        } else {
            togglePassword1.className = 'fa-solid fa-eye field-icon toggle-password';
        }
        const ctype = cpassword.getAttribute('type') === 'password' ? 'text' : 'password';
        cpassword.setAttribute('type', ctype);
        if (cpassword.getAttribute('type') !== 'password') {
            togglePassword2.className = 'fa-solid fa-eye-slash field-icon toggle-password';
        } else {
            togglePassword2.className = 'fa-solid fa-eye field-icon toggle-password';
        }
    });

}

function validpswd() {
    var pwd = document.getElementById("password1");
    var cpwd = document.getElementById("cpassword");
    if (pwd.value.length < 6 || cpwd.value.length < 6) {
        alert("Password must be maximum of 6 characters");
        return false;
    }
    else if (pwd.value != cpwd.value) {
        alert("Confirm Password doesn't Match");
        return false;
    }else {
        return true;
    }
    
}

const sign_in_btn = document.querySelector("#sign-in-btn");
const sign_up_btn = document.querySelector("#sign-up-btn");
const container = document.querySelector(".container");

sign_up_btn.addEventListener("click", () => {
    container.classList.add("sign-up-mode");
});

sign_in_btn.addEventListener("click", () => {
    container.classList.remove("sign-up-mode");
});


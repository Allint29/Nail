
var loginLink = document.querySelector(".login-link-item");
var loginPopup = document.querySelector(".modal-login");

if (loginPopup) {
       // alert(loginPopup);
        var loginFieldUserName = loginPopup.querySelector("[name=username]");
        var loginFieldPass = loginPopup.querySelector("[name=password]");
        var loginClose = loginPopup.querySelector(".modal-close");
        var loginStorage = localStorage.getItem("login");

        var overlay = document.querySelector(".modal-overlay");

    if (loginLink) {
        loginLink.addEventListener("click",
            function(evt) {
                if (loginPopup) {
                    evt.preventDefault();
                    overlay.classList.add("modal-overlay-show");
                    loginPopup.classList.add("modal-show");
                    loginFieldUserName.focus();
                    if (loginStorage) {
                        loginFieldUserName.value = loginStorage;
                    }
                }
            });
    }

        loginClose.addEventListener("click",
            function(evt) {
                evt.preventDefault();
                overlay.classList.remove("modal-overlay-show");
                loginPopup.classList.remove("modal-show");

            });


        window.addEventListener("keydown",
            function(evt) {
                if (evt.keyCode === 27) {
                    evt.preventDefault();
                    overlay.classList.remove("modal-overlay-show");
                    loginPopup.classList.remove("modal-show");
                };
            });

    }
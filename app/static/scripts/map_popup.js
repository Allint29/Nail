
    var mapLink = document.querySelector(".js-contact-button-map");
    var mapPopup = document.querySelector(".modal-map");
    var mapClose = mapPopup.querySelector(".modal-close");

    var overlay = document.querySelector(".modal-overlay");

    mapLink.addEventListener("click",
        function(evt) {
            evt.preventDefault();
            //  overlay.classList.add("modal-overlay-show");
            mapPopup.classList.add("modal-show");
        });

    mapClose.addEventListener("click",
        function(evt) {
            evt.preventDefault();
            mapPopup.classList.remove("modal-overlay-show");
            mapPopup.classList.remove("modal-show");
        });

    window.addEventListener("keydown",
        function(evt) {
            if (evt.keyCode === 27) {
                evt.preventDefault();
                //           overlay.classList.remove("modal-overlay-show");
                mapPopup.classList.remove("modal-show");
            };
        });

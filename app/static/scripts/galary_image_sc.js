
var sectionGallary = document.querySelectorAll(".js-image-gallary");

var backGallagyButton = document.querySelector(".js-gallery-button-back");
var nextGallaryButton = document.querySelector(".js-gallery-button-next");
var overlay = document.querySelector(".modal-overlay");


nextGallaryButton.addEventListener("click",
    function (evt) {
        evt.preventDefault();

        var i = sectionGallary.length - 1;
        
        while (i >= 0) {
            var st = sectionGallary[i].style.display;
            //alert("HКme  ккка");
            if (st === "block") {
                if (i === 0) {
                    sectionGallary[i].style.display = "none";
                    sectionGallary[sectionGallary.length - 1].style.display = "block"; //
                    var animation = sectionGallary[i - 1].animate([
                        { opacity: '0' },
                        { opacity: '0.8' }
                    ], 800);
                    animation.addEventListener('finish', function () {
                        sectionGallary[i - 1].style.opacity = '1';
                    });
                    break;
                }
                sectionGallary[i].style.display = "none";
                sectionGallary[i - 1].style.display = "block";
                
                var animation = sectionGallary[i - 1].animate([
                    { opacity: '0' },
                    { opacity: '0.8' }
                ], 1000);
                animation.addEventListener('finish', function () {
                    sectionGallary[i - 1].style.opacity = '1';
                });
                
                break;
            }
            i = i - 1;
        }


    });

backGallagyButton.addEventListener("click",
    function (evt) {
        evt.preventDefault();

        var i = sectionGallary.length - 1;

        while (i >= 0) {
            var st = sectionGallary[i].style.display;
            //alert("HКme  ккка");
            
            if (st === "block") {

                if (i === sectionGallary.length - 1) {
                    sectionGallary[i].style.display = "none";
                    sectionGallary[0].style.display = "block";
                    var animation = sectionGallary[0].animate([
                        { opacity: '0' },
                        { opacity: '0.8' }
                    ], 800);
                    animation.addEventListener('finish', function () {
                        sectionGallary[0].style.opacity = '1';
                    });

                    break;
                }

                sectionGallary[i].style.display = "none";
                sectionGallary[i + 1].style.display = "block";

                var animation = sectionGallary[i + 1].animate([
                    { opacity: '0' },
                    { opacity: '0.8' }
                ], 1000);
                animation.addEventListener('finish', function () {
                    sectionGallary[i + 1].style.opacity = '1';
                });
                break;
            }
            i = i - 1;
        }
    });


//loginClose.addEventListener("click",
//    function(evt) {
//        evt.preventDefault();
//        overlay.classList.remove("modal-overlay-show");
//        loginPopup.classList.remove("modal-show");
//
//    });
//
//
//window.addEventListener("keydown",
//    function(evt) {
//        if (evt.keyCode === 27) {
//            evt.preventDefault();
//            overlay.classList.remove("modal-overlay-show");
//            loginPopup.classList.remove("modal-show");
//        };
//    });
//

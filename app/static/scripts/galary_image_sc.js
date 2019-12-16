

var backGallagyButton = document.querySelector(".js-gallery-button-back");
var nextGallaryButton = document.querySelector(".js-gallery-button-next");
var overlay = document.querySelector(".modal-overlay");

if (nextGallaryButton) {
    nextGallaryButton.addEventListener("click",
        function(evt) {
            evt.preventDefault();
            var sectionGallary = document.querySelectorAll(".js-image-gallary");
            //Выбрал объект содержащий изображения
            var divGallaryContent = document.querySelector("a.gallary-content-a");
            //все изображения в БД
            var listAllIdImages = document.getElementById("listIdImages");
            
            var i = sectionGallary.length - 1;

            while (i >= 0) {
                var st = sectionGallary[i].style.display;
                
                if (st === "block") {
                    if (i === 0) {
                        var str = '';
                        //изображения уже загруженные из БД
                        var listFactImages = document.querySelectorAll(".js-image-gallary");
                        var j = 0;
                        while (j <= listFactImages.length - 1) {
                            if (j < listFactImages.length - 1) {
                                str = str + listFactImages[j].id + ",";
                            } else if (j === listFactImages.length - 1) {
                                str = str + listFactImages[j].id;
                            }
                            j = j + 1;
                        };

                        $.post("/load_image",
                            {
                                idImage: sectionGallary[i].id,
                                listAllImages: listAllIdImages.value,
                                listFactIdImages: str,
                                toForvard: '1' // 1 - пролистываем вперед, 0 - пролистываем назад
                            }
                        ).done(function (response) {
                            //#здесь создаю объект рисунка если не все рисунки еще загружены
                           
                            if (response['listImages'].length > 0) {
                                var j = 0;
                                while (j <= response['listImages'].length - 1) {
                                    var elem = document.createElement("img");
                                    elem.id = response['listImages'][j]['id'];
                                    elem.src = response['listImages'][j]['url'];
                                    elem.className = "js-image-gallary";
                                    if (j === 0) {
                                        sectionGallary[i].style.display = "none";
                                        elem.style.display = "block";
                                        try {
                                            if (elem) {
                                                var animation = elem.animate([
                                                        { opacity: '0' },
                                                        { opacity: '0.8' }
                                                    ],
                                                    800);
                                                animation.addEventListener('finish',
                                                    function() {
                                                        elem.style.opacity = '1';
                                                    });
                                            }
                                        } catch (f) {
                                            //console.log(e); // pass exception object to error handler
                                            elem.style.opacity = '1';

                                        };

                                    } else {
                                        elem.style.display = "none";
                                    }

                                    divGallaryContent.appendChild(elem);
                                    // получаем первый элемент, перед которым будет идти добавление
                                    var firstElem = divGallaryContent.firstChild.nextSibling;
                                    // добавляем элемент в блок div перед первым узлом
                                    divGallaryContent.insertBefore(elem, firstElem);
                                    j = j + 1;
                                }
                            } else {
                                sectionGallary[i].style.display = "none";
                                sectionGallary[sectionGallary.length - 1].style.display = "block"; //
                                if (sectionGallary[i - 1]) {

                                    try {
                                        var animation = sectionGallary[i - 1].animate([
                                            { opacity: '0' },
                                            { opacity: '0.8' }
                                        ],
                                            800);
                                        animation.addEventListener('finish',
                                            function () {
                                                sectionGallary[i - 1].style.opacity = '1';
                                            });
                                    } catch (e){
                                        sectionGallary[i - 1].style.opacity = '1';
                                    }
                                };
                            };

                        }).fail(function () {
                            alert('Error: Could not contact server.');

                        });

                        break;
                    }
                    
                    sectionGallary[i].style.display = "none";
                    sectionGallary[i - 1].style.display = "block";

                    try {
                        var animation = sectionGallary[i - 1].animate([
                                { opacity: '0' },
                                { opacity: '0.8' }
                            ],
                            1000);
                        animation.addEventListener('finish',
                            function() {
                                sectionGallary[i - 1].style.opacity = '1';
                            });
                    } catch (e) {
                        sectionGallary[i - 1].style.opacity = '1';
                    }

                    break;
                }
                i = i - 1;
            }


        });
}

if (backGallagyButton) {
    backGallagyButton.addEventListener("click",
        function(evt) {
            evt.preventDefault();

            var sectionGallary = document.querySelectorAll(".js-image-gallary");
            //Выбрал объект содержащий изображения
            var divGallaryContent = document.querySelector("a.gallary-content-a");
            var listAllIdImages = document.getElementById("listIdImages");

            var i = sectionGallary.length - 1;

            while (i >= 0) {
                var st = sectionGallary[i].style.display;
                //alert("HКme  ккка");
                if (st === "block") {
                    //если дошли до последней картинки в списке
                    if (i === sectionGallary.length - 1) {
                        var str = '';
                        //изображения уже загруженные из БД
                        var listFactImages = document.querySelectorAll(".js-image-gallary");
                        var j = 0;
                        while (j <= listFactImages.length - 1) {
                            if (j < listFactImages.length - 1) {
                                str = str + listFactImages[j].id + ",";
                            } else if (j === listFactImages.length - 1) {
                                str = str + listFactImages[j].id;
                            }
                            j = j + 1;
                        };

                        $.post("/load_image",
                            {
                                idImage: sectionGallary[i].id,
                                listAllImages: listAllIdImages.value,
                                listFactIdImages: str,
                                toForvard: '0' // 1 - пролистываем вперед, 0 - пролистываем назад
                            }).done(function(response) {
                                if (response['listImages'].length > 0) {
                                    var j = 0;
                                    while (j <= response['listImages'].length - 1) {
                                        var elem = document.createElement("img");
                                        elem.id = response['listImages'][j]['id'];
                                        elem.src = response['listImages'][j]['url'];
                                        elem.className = "js-image-gallary";
                                        if (j === 0) {
                                            sectionGallary[i].style.display = "none";
                                            elem.style.display = "block";
                                            try {
                                                if(elem) {
                                                    var animation = elem.animate([
                                                            { opacity: '0' },
                                                            { opacity: '0.8' }
                                                        ],
                                                        800);
                                                    animation.addEventListener('finish',
                                                        function () {
                                                            elem.style.opacity = '1';
                                                        });
                                                }
                                            } catch (f) {
                                                //console.log(e); // pass exception object to error handler
                                                elem.style.opacity = '1';
                                            };
                                        } else {
                                            elem.style.display = "none";
                                        }
                                        divGallaryContent.appendChild(elem);
                                        // Здесь не добавляем элемент перед первым а наоборот добавляем в самый низ

                                        j = j + 1;
                                    }
                                } else {
                                    sectionGallary[i].style.display = "none";
                                    sectionGallary[0].style.display = "block";
                                    if (sectionGallary[0]) {

                                        try {
                                            var animation = sectionGallary[0].animate([
                                                    { opacity: '0' },
                                                    { opacity: '0.8' }
                                                ],
                                                800);
                                            animation.addEventListener('finish',
                                                function () {
                                                    sectionGallary[0].style.opacity = '1';
                                                });
                                        } catch (e) {
                                            sectionGallary[0].style.opacity = '1';
                                        }
                                    };
                                }

                        }).fail(function () {
                            alert('Error: Could not contact server.');
                        });
                        break;
                    }

                    sectionGallary[i].style.display = "none";
                    sectionGallary[i + 1].style.display = "block";
                    try {
                        var animation = sectionGallary[i + 1].animate([
                            { opacity: '0' },
                            { opacity: '0.8' }
                        ],
                            1000);
                        animation.addEventListener('finish',
                            function () {
                                sectionGallary[i + 1].style.opacity = '1';
                            });
                    } catch (e){
                        sectionGallary[i + 1].style.opacity = '1';
                    }

                    break;
                }
                i = i - 1;
            }
        });

}

$(function () {
    var timer = null;
    $('.user_popup').hover(
        function (event) {
            // mouse in event handler
            var elem = event.currentTarget;
            timer = setTimeout(function () {
                timer = null;
                // логика Popup должна быть здесь    
                //alert('!!!!1!!!!');
                xhr = $.ajax('/show_alert').done(
                    function () {
                        xhr = null;
                        var b = '1';
                        //  здесь создаём и отображаем всплывающее окно
                        //  alert('222');
                    }
                );
               // alert('!!!2!!!!!');
               // alert(xhr.text);

            }, 1000);
            
        },
        function (event) {
            //обработчик события mouse out
            var elem = event.currentTarget;
            if (timer) {
                clearTimeout(timer);
                timer = null;
            }
        }
    );
});


function load_image(idImage2, listImages2) {
    alert($(idImage2).value);
    alert($(listImages2));

}

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

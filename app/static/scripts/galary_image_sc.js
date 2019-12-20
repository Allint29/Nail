var backGallagyButton = document.querySelector(".js-gallery-button-back");
var nextGallaryButton = document.querySelector(".js-gallery-button-next");
var overlay = document.querySelector(".modal-overlay");
var listTimeButtons = document.querySelectorAll(".js-schedule-direct");

if (listTimeButtons.length > 0) {
    for (i=0; i < listTimeButtons.length; i++) {
         listTimeButtons[i].addEventListener("click",
             function (evt) {
                 evt.preventDefault();
                 var elem = evt.currentTarget;

                 //var prevElem = listTimeButtons[i];
                 $.post("/master_schedule/js_show_schedule_reserve",
                     {
                         idElem: elem.id
                     }
                 ).done(function (response) {
                     if (response['result'] === 'true') {

                         //изменяю элементы предыдущего времени
                         var idPrevTime = response['time_prev'];
                         var kindPrevToChange = null;
                         var timePrevToChange = null;
                         
                         if (idPrevTime === 'none') {
                             timePrevToChange = null;
                             kindPrevToChange = null;
                         } else {
                             timePrevToChange = document.getElementById("time_" + idPrevTime);
                             kindPrevToChange = document.getElementById("kind_" + idPrevTime);
                         }
                         if (timePrevToChange != null) {
                             timePrevToChange.className = response['time_prev_class_text'];
                             //timePrevToChange.textContent = response['time_prev_kind_text'];
                         }
                         if (kindPrevToChange != null) {
                             kindPrevToChange.className = response['time_prev_class_text'];
                             kindPrevToChange.textContent = response['time_prev_kind_text'];
                         }

                         //изменяю элементы страницы у текущего времени
          
                         var idTime = response['time_id'];
                         var kindThis = null;
                         var timeThis= null;
                         var clientThis = null;
                         var priceThis = null;
                         var typeworkThis = null;
                         var mailThis = null;
                         var phoneThis = null;
                         var contactsThis = null;
                         var noteThis = null;

                         timeThis = document.getElementById("time_" + idTime);
                         kindThis = document.getElementById("kind_" + idTime);
                         clientThis = document.getElementById("client_" + idTime);
                         priceThis = document.getElementById("price_" + idTime);
                         typeworkThis = document.getElementById("typework_" + idTime);
                         mailThis = document.getElementById("mail_" + idTime);
                         phoneThis = document.getElementById("phone_" + idTime);
                         contactsThis = document.getElementById("contacts_" + idTime);
                         noteThis = document.getElementById("note_" + idTime);

                         if (timeThis != null) {
                             timeThis.className = response['time_this_class_text'];
                             //timePrevToChange.textContent = response['time_prev_kind_text'];
                         }
                         if (kindThis != null) {
                             kindThis.className = response['time_this_class_text'];
                             kindThis.textContent = response['time_this_kind_text'];
                         }
                         if (clientThis != null) {
                             clientThis.textContent = response['time_this_client_text'];
                         }
                         if (priceThis != null) {
                             priceThis.textContent = response['time_this_price_text'];
                         }
                         if (typeworkThis != null) {
                             typeworkThis.textContent = response['time_this_typework_text'];
                         }
                         if (mailThis != null) {
                             mailThis.textContent = response['time_this_mail_text'];
                         }
                         if (phoneThis != null) {
                             phoneThis.textContent = response['time_this_phone_text'];
                         }
                         if (contactsThis != null) {
                             contactsThis.textContent = response['time_this_contacts_text'];
                         }
                         if (noteThis != null) {
                             noteThis.textContent = response['time_this_note_text'];
                         }

                         //изменяю кнопки
                         var typeEmpty = response['type_empty'];

                         if (typeEmpty === 'free') {
                             elem.id = "to_reserve_" + idTime;
                             let buttonElem = elem.querySelector(".button");
                             buttonElem.id = "reserve_button";
                             buttonElem.name = "reserve_button";
                             buttonElem.value = "Занять";
                         } else {
                             elem.id = "to_free_" + idTime;
                             let buttonElem = elem.querySelector(".button");
                             buttonElem.id = "delete_button";
                             buttonElem.name = "delete_button";
                             buttonElem.value = "Освободить";
                         }

                     } else {
                         alert(response['text']);
                     }

                 }).fail(function () {
                     alert('Error: Could not contact server.');

                 });

             });
    }
}

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

//function alert_my(alertM) {
//    alert(alertM);
//    console.log('Hello');
//}

//
//if (timeList) {
//    var reserveTimeButton = timeList.querySelectorAll("js-reserve-time-li-to-reserve");
//    reserveTimeButton.addEventListener("click",
//        function(evt) {
//            evt.preventDefault();
//            alert('I am here');
//            //$.post("/load_image",
//            //    {
//            //        idImage: sectionGallary[i].id,
//            //        listAllImages: listAllIdImages.value,
//            //        listFactIdImages: str,
//            //        toForvard: '0' // 1 - пролистываем вперед, 0 - пролистываем назад
//            //    }).done(function (response) {
//            //        //response['listImages'].length
//            //      
//            //
//            //    }).fail(function () {
//            //        alert('Error: Could not contact server.');
//            //    });
//        });
//}




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

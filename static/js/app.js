$(document).ready(function() {
    "use strict";
    // owl-carousel
//    <img src="http://flickholdr.com/640/480/2" alt="placeholder image"/>
    var $slider = $('.owl-carousel');

//    var image_count = 5;
//    for (var i=1; i<image_count; i++) {
//        $slider.append('<img src="http://lorempixel.com/1024/768/'+i+'" alt="placeholder image"/>');
//    }
    $slider.owlCarousel({
        items: 1,
        margin: 100,
        singleItem: true,
        pagination: false,
        navigation: true,
        navigationText: [
            '<span class="glyphicon glyphicon-chevron-left"></span>',
            '<span class="glyphicon glyphicon-chevron-right"></span>'
        ]
    });
});
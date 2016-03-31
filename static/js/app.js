var getCookie = function(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};
var csrftoken = getCookie('csrftoken');

$(document).ready(function() {
    "use strict";

    var $form = $("#supply_form");
    if ($form.length > 0) {
        var get_animals_url = "/get_animals/";
        var get_consumables_url = "/get_consumables/";
        var $extra_fields = $("#extra_fields");
        var $btn_add_animal = $("#add_animal");
        var $btn_add_consumable = $("#add_consumable");

        $('[name="date"]').datepicker({
            format: "dd/mm/yyyy",
            weekStart: 1,
            todayBtn: "linked",
            language: "ru"
        });

        var validator = $form.validate({
            ignore: [],
            errorPlacement:  function(error, element) {
                element.parent().toggleClass("has-error", true);
            },
            success: function(label, element) {
                $(element).parent().toggleClass("has-error", false);
            }
        });

        $btn_add_animal.on("click", function () {
            $.ajax({
                url: get_animals_url,
                type: 'POST',
                data: {
                    csrfmiddlewaretoken: csrftoken
                },

                success: function (data) {
                    if (data["html"]) {
                        var $new_form = $(data["html"]);
                        var $body = $new_form.find('[data-role="form-body"]');
                        $new_form.find('[data-action="remove"]').on("click",function() {
                            $new_form.remove();
                        });
                        $new_form.find('[data-action="collapse"]').on("click", function() {
                            $body.toggleClass("collapse");
                        });
                        $extra_fields.append($new_form);
                    } else {
                        alert("error!");
                    }
                },
                error: function (textStatus) {
                    try {
                        console.log(textStatus)
                    } catch (e) {
                    }
                }
            });
        });

        $btn_add_consumable.on("click", function () {
            $.ajax({
                url: get_consumables_url,
                type: 'POST',
                data: {
                    csrfmiddlewaretoken: csrftoken
                },

                success: function (data) {
                    if (data["html"]) {
                        var $new_form = $(data["html"]);
                        var $body = $new_form.find('[data-role="form-body"]');
                        $new_form.find('[data-action="remove"]').on("click",function() {
                            $new_form.remove();
                        });
                        $new_form.find('[data-action="collapse"]').on("click", function() {
                            $body.toggleClass("collapse");
                        });
                        $extra_fields.append($new_form);
                    } else {
                        alert("error!");
                    }
                },
                error: function (textStatus) {
                    try {
                        console.log(textStatus)
                    } catch (e) {
                    }
                }
            });
        });
    }
});
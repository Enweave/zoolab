"use strict";

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

var bind_supply_form = function($form) {
    var get_animals_url = "/get_animals/";
    var get_consumables_url = "/get_consumables/";

    var $fieldsets_container = $("#extra_fields");

    var $btn_add_animal = $("#add_animal");
    var $btn_add_consumable = $("#add_consumable");

    var validator = $form.validate({
        ignore: [],
        errorPlacement:  function(error, element) {
            element.parent().toggleClass("has-error", true);
        },
        success: function(label, element) {
            $(element).parent().toggleClass("has-error", false);
        }
    });

    var bind_fieldset = function($fieldset) {
        var $body = $fieldset.find('[data-role="form-body"]');
        var $title = $fieldset.find('[data-role="fieldset-title"]');
        var $collapse = $fieldset.find('[data-action="collapse"]');

        var $name_source = $fieldset.find('[data-role="fieldset-name-source"]');

        var $fields = $fieldset.find("input, select");

        if ($name_source.is("select")) {
            $name_source.on("change", function() {
                $title.html($name_source.find(":selected").text());
            });
        } else {
            $name_source.on("change", function(){
                $title.html($name_source.val());
            });
        }

        $fieldset.find('[data-action="remove"]').on("click",function() {
            $fieldset.remove();
        });

        $collapse.on("click", function() {
            var valid = true;
            $fields.each(function(i, el) {
                valid = validator.element($fields.eq(i)) === false ? false : valid;
            });
            if (valid === true) {
                $body.toggleClass("collapse");
                $collapse.toggle();
            }
        });

        $fieldsets_container.append($fieldset);
    };

    var insert_fieldset = function(url) {
        $.ajax({
            url: url,
            type: 'POST',
            data: {
                csrfmiddlewaretoken: csrftoken
            },

            success: function (data) {
                if (data["html"]) {
                    bind_fieldset($(data["html"]));
                } else {
                    alert("Что-то пошло не так!(((");
                }
            },
            error: function (textStatus) {
                try {
                    console.log(textStatus)
                } catch (e) {
                }
            }
        });
    };

    $('[name="date"]').datepicker({
        format: "dd/mm/yyyy",
        weekStart: 1,
        todayBtn: "linked",
        language: "ru"
    });

    $btn_add_animal.on("click", function () {
        insert_fieldset(get_animals_url);
    });

    $btn_add_consumable.on("click", function () {
        insert_fieldset(get_consumables_url);
    });
};

var bind_supplies = function($container) {

    var active_requests = [];
    var $supplies = $container.find('[data-role="supply"]');

    var remove_supply = function(url, request_id) {
        if (typeof active_requests[request_id] === "undefined") {
            active_requests[request_id] = 0;
            $.ajax({
                url: url,
                type: 'POST',
                data: {
                    csrfmiddlewaretoken: csrftoken,
                    confirm: true
                },
                success: function (data) {
                    if (data["success"] === true ) {
                        $supplies.eq(request_id).fadeOut(150, function(){
                            $supplies.eq(request_id).remove();
                        })
                    } else {
                        active_requests[request_id] = undefined;
                        alert("Что-то пошло не так!(((");
                    }
                },
                error: function (textStatus) {
                    active_requests[request_id] = undefined;
                    try {
                        console.log(textStatus)
                    } catch (e) {
                    }
                }
            });
        }


    };


    $supplies.each(function(i){
        $supplies.eq(i).find('[data-action="remove-supply"]').on("click", function(e) {
            e.preventDefault();
            if (confirm("Удалить?")) {
                remove_supply(this.href,i);
            }
        });
    });
};

var rice = function($container, f) {
    if ($container.length>0) {f($container)}
};

$(document).ready(function() {
    rice($("#supply_form"),bind_supply_form);
    rice($("#supplies_container"),bind_supplies);


});
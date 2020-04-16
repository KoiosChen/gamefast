//== Class definition

//== Class definition

var BootstrapDatepicker = function () {

    //== Private functions
    var demos = function () {
        // minimum setup
        $('#m_datepicker_1, #m_datepicker_1_validate').datepicker({
            todayHighlight: true,
            orientation: "bottom left",
            templates: {
                leftArrow: '<i class="la la-angle-left"></i>',
                rightArrow: '<i class="la la-angle-right"></i>'
            }
        });

        // minimum setup for modal demo
        $('#m_datepicker_1_modal').datepicker({
            todayHighlight: true,
            orientation: "bottom left",
            templates: {
                leftArrow: '<i class="la la-angle-left"></i>',
                rightArrow: '<i class="la la-angle-right"></i>'
            }
        });

        // minimum setup for modal demo
        $('#m_datepicker_1_modal_2').datepicker({
            todayHighlight: true,
            orientation: "bottom left",
            templates: {
                leftArrow: '<i class="la la-angle-left"></i>',
                rightArrow: '<i class="la la-angle-right"></i>'
            }
        });

        // input group layout
        $('#m_datepicker_2, #m_datepicker_2_validate').datepicker({
            todayHighlight: true,
            orientation: "bottom left",
            templates: {
                leftArrow: '<i class="la la-angle-left"></i>',
                rightArrow: '<i class="la la-angle-right"></i>'
            }
        });

        // input group layout for modal demo
        $('#m_datepicker_2_modal').datepicker({
            todayHighlight: true,
            orientation: "bottom left",
            templates: {
                leftArrow: '<i class="la la-angle-left"></i>',
                rightArrow: '<i class="la la-angle-right"></i>'
            }
        });

        // enable clear button
        $('#m_datepicker_3, #m_datepicker_3_validate').datepicker({
            todayBtn: "linked",
            clearBtn: true,
            todayHighlight: true,
            templates: {
                leftArrow: '<i class="la la-angle-left"></i>',
                rightArrow: '<i class="la la-angle-right"></i>'
            }
        });

        // enable clear button for modal demo
        $('#m_datepicker_3_modal').datepicker({
            todayBtn: "linked",
            clearBtn: true,
            todayHighlight: true,
            templates: {
                leftArrow: '<i class="la la-angle-left"></i>',
                rightArrow: '<i class="la la-angle-right"></i>'
            }
        });

        // orientation
        $('#m_datepicker_4_1').datepicker({
            orientation: "top left",
            todayHighlight: true,
            templates: {
                leftArrow: '<i class="la la-angle-left"></i>',
                rightArrow: '<i class="la la-angle-right"></i>'
            }
        });

        $('#m_datepicker_4_2').datepicker({
            orientation: "top right",
            todayHighlight: true,
            templates: {
                leftArrow: '<i class="la la-angle-left"></i>',
                rightArrow: '<i class="la la-angle-right"></i>'
            }
        });

        $('#m_datepicker_4_3').datepicker({
            orientation: "bottom left",
            todayHighlight: true,
            templates: {
                leftArrow: '<i class="la la-angle-left"></i>',
                rightArrow: '<i class="la la-angle-right"></i>'
            }
        });

        $('#m_datepicker_4_4').datepicker({
            orientation: "bottom right",
            todayHighlight: true,
            templates: {
                leftArrow: '<i class="la la-angle-left"></i>',
                rightArrow: '<i class="la la-angle-right"></i>'
            }
        });

        // range picker
        $('#m_datepicker_5').datepicker({
            todayHighlight: true,
            templates: {
                leftArrow: '<i class="la la-angle-left"></i>',
                rightArrow: '<i class="la la-angle-right"></i>'
            }
        });

        // inline picker
        $('#m_datepicker_6').datepicker({
            todayHighlight: true,
            templates: {
                leftArrow: '<i class="la la-angle-left"></i>',
                rightArrow: '<i class="la la-angle-right"></i>'
            }
        });

        $('#m_datetimepicker_2_modal').datetimepicker({
            todayHighlight: true,
            autoclose: true,
            pickerPosition: 'bottom-left',
            format: 'yyyy/mm/dd hh:ii'
        });
    }

    return {
        // public functions
        init: function () {
            demos();
        }
    };
}();

var BootstrapDaterangepicker = function () {

    //== Private functions
    var demos = function () {
        // minimum setup

        // date & time
        $('#m_daterangepicker_4').daterangepicker({
            buttonClasses: 'm-btn btn',
            applyClass: 'btn-primary',
            cancelClass: 'btn-secondary',

            timePicker: true,
            timePickerIncrement: 1,
            timePicker24Hour: true,
            timePickerSeconds: true,
            locale: {
                format: 'MM/DD/YYYY h:mm A'
            }
        }, function (start, end, label) {
            let input = $('#m_daterangepicker_4 .form-control');
            input.val(start.format('YYYY/MM/DD HH:mm:ss') + ' - ' + end.format('YYYY/MM/DD HH:mm:ss'));
        });
        // date & time
        $('#m_daterangepicker_fromexcel').daterangepicker({
            buttonClasses: 'm-btn btn',
            applyClass: 'btn-primary',
            cancelClass: 'btn-secondary',
            timePicker: true,
            startDate: new Date(new Date(new Date().toLocaleDateString()).getTime()),
            endDate: new Date(new Date(new Date().toLocaleDateString()).getTime() + 6 * 60 * 60 * 1000),
            timePickerIncrement: 5,
            timePicker24Hour: true,
            timePickerSeconds: false,
            locale: {
                format: 'MM/DD/YYYY h:mm A'
            }
        }, function (start, end, label) {
            let input = $('#m_daterangepicker_fromexcel .form-control');
            input.val(start.format('YYYY/MM/DD HH:mm:00') + ' - ' + end.format('YYYY/MM/DD HH:mm:00'));
        });

        // date & time
        $('#search_m_daterange').daterangepicker({
            buttonClasses: 'm-btn btn',
            applyClass: 'btn-primary',
            cancelClass: 'btn-secondary',
            timePicker: true,
            startDate: new Date(new Date(new Date().toLocaleDateString()).getTime()),
            endDate: new Date(new Date(new Date().toLocaleDateString()).getTime() + 6 * 60 * 60 * 1000),
            timePickerIncrement: 5,
            timePicker24Hour: true,
            timePickerSeconds: false,
            locale: {
                format: 'MM/DD/YYYY h:mm A'
            }
        }, function (start, end, label) {
            let input = $('#search_m_daterange .form-control');
            input.val(start.format('YYYY/MM/DD HH:mm:00') + ' - ' + end.format('YYYY/MM/DD HH:mm:00'));
        });
    }


    return {
        // public functions
        init: function () {
            demos();
        }
    };
}();

jQuery(document).ready(function () {
    BootstrapDaterangepicker.init();
    BootstrapDatepicker.init();
});
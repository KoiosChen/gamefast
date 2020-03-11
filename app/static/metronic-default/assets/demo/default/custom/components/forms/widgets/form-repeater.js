//== Class definition
var FormRepeater = function () {

    //== Private functions
    var demo3 = function () {
        $('#m_repeater_3').repeater({
            initEmpty: false,

            defaultValues: {
                'text-input': 'foo'
            },

            show: function () {
                $("#m_repeater_3 :input").unbind("input propertychange", repeat_input);
                $("#m_repeater_3 :input").bind("input propertychange", repeat_input);
                $(this).slideDown();
            },

            hide: function (deleteElement) {
                if (confirm('是否确定删除此行?')) {
                    $(this).slideUp(deleteElement);
                }
            }
        });
    }
     var repeater_in_excel = function () {
        $('#m_repeater_4').repeater({
            initEmpty: false,

            defaultValues: {
                'text-input': 'foo'
            },

            show: function () {
                $(this).slideDown();
            },

            hide: function (deleteElement) {
                if (confirm('是否确定删除此行?')) {
                    $(this).slideUp(deleteElement);
                }
            }
        });
    }
    return {
        // public functions
        init: function () {
            demo3();
            repeater_in_excel();
        }
    };
}();

function repeat_input() {
    let pops = [];

    $('#m_repeater_3 :input').each(function () {
        let l_name = $(this).attr('name');
        let l_value = $(this).val();
        let res = /^[\u4e00-\u9fa5]+$/;
        if (res.test(l_value)) {
            const aaa = {};
            aaa[l_name] = l_value;
            console.log(aaa);
            pops.push(aaa);
        }
    });
    console.log(pops);
    if (pops) {
        DatatableRemoteAjaxCustomer.init(pops);
        $('#ajax_modal_data').mDatatable().destroy();
        DatatableRemoteAjaxCustomer.init(pops);
    }
}

jQuery(document).ready(function () {
    $("#m_repeater_3 :input").bind("input propertychange", repeat_input);
    FormRepeater.init();
});

    
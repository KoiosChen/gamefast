//== Class definition

var FormControls = function () {
    //== Private functions

    var demo1 = function () {
        $("#m_form_new_templet").validate({
            // define validation rules
            rules: {
                customer_name: {
                    required: true
                }
            },

            //display error alert on form submit  
            invalidHandler: function (event, validator) {
                var alert = $('#m_form_new_templet_msg');
                alert.removeClass('m--hide').show();
                mApp.scrollTo(alert, -200);
            },

            submitHandler: function (form) {
                let templet_name = $('#templet_name').val();
                let templet_desc = $('#templet_desc').val();

                let params = {
                    'templet_name': templet_name,
                    'templet_desc': templet_desc
                };
                $.ajax({
                    type: "POST",          //提交方式          
                    url: "new_templet",  //提交的页面/方法名          
                    dataType: 'json',
                    contentType: "application/json; charset=utf-8",
                    data: JSON.stringify(params, null, '\t'),         //参数（如果没有参数：null）          

                    success: function (msg) {
                        $('#ajax_data').mDatatable().destroy();
                        DatatableRemoteAjaxMailTemplet.init();
                        toastr.info(msg.content);
                        $('#new_templet_model').modal('hide')
                    },
                    error: function (xhr, msg, e) {
                        toastr.warning(msg.content);
                        $('#new_templet_model').modal('hide')
                    }
                });
            }
        });
    }

    var update = function () {
        $("#m_form_update").validate({
            submitHandler: function (form) {
                let update_customer_name = $('#update_customer_name').val();
                let mail_templet_update = $('#mail_templet_update').val();

                let params = {
                    'update_customer_name': update_customer_name,
                    'mail_templet_update': mail_templet_update
                };
                $.ajax({
                    type: "POST",          //提交方式          
                    url: "customer_update",  //提交的页面/方法名          
                    dataType: 'json',
                    contentType: "application/json; charset=utf-8",
                    data: JSON.stringify(params, null, '\t'),         //参数（如果没有参数：null）          

                    success: function (msg) {
                        $('#ajax_data').mDatatable().destroy();
                        DatatableRemoteAjaxMailTemplet.init();
                        toastr.info(msg.content);
                        $('#new_templet_model').modal('hide')
                    },
                    error: function (xhr, msg, e) {
                        toastr.warning(msg.content);
                        $('#new_templet_model').modal('hide')
                    }
                });
            }
        });
    }

    return {
        // public functions
        init: function () {
            demo1();
        },
        update_info: function () {
            update();
        }
    };
}();

jQuery(document).ready(function () {
    FormControls.init();
    FormControls.update_info();
});
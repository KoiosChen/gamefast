//== Class definition

var FormControls = function () {
    //== Private functions

    var demo1 = function () {
        $("#m_form_1").validate({
            // define validation rules
            rules: {
                customer_name: {
                    required: true
                }
            },

            //display error alert on form submit  
            invalidHandler: function (event, validator) {
                var alert = $('#m_form_1_msg');
                alert.removeClass('m--hide').show();
                mApp.scrollTo(alert, -200);
            },

            submitHandler: function (form) {
                let customer_name = $('#customer_name').val();
                let mail_templet = $('#mail_templet').val();

                let params = {
                    'customer_name': customer_name,
                    'mail_templet': mail_templet
                };
                $.ajax({
                    type: "POST",          //提交方式          
                    url: "new_customer",  //提交的页面/方法名          
                    dataType: 'json',
                    contentType: "application/json; charset=utf-8",
                    data: JSON.stringify(params, null, '\t'),         //参数（如果没有参数：null）          

                    success: function (msg) {
                        $('#ajax_data').mDatatable().destroy();
                        DatatableRemoteAjaxCustomer.init();
                        toastr.info(msg.content);
                        $('#new_customer_model').modal('hide')
                    },
                    error: function (xhr, msg, e) {
                        toastr.warning(msg.content);
                        $('#new_customer_model').modal('hide')
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
                        DatatableRemoteAjaxCustomer.init();
                        toastr.info(msg.content);
                        $('#update_customer_model').modal('hide')
                    },
                    error: function (xhr, msg, e) {
                        toastr.warning(msg.content);
                        $('#update_customer_model').modal('hide')
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
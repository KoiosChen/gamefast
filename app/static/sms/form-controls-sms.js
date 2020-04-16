//== Class definition

let FormControlsSMS = function () {
    //== Private functions

    let sms = function () {
        $("#send_sms_form").validate({
            // define validation rules
            rules: {
                targetPhone: {
                    required: true,
                },
            },

            //display error alert on form submit
            invalidHandler: function (event, validator) {
                let alert = $('#send_sms_form_msg');
                alert.removeClass('m--hide').show();
                mApp.scrollTo(alert, -200);
            },

            submitHandler: function (form) {
                let content = $("#template_content").html();
                $("input[id*='send_content_id_']").each(function (i, val) {
                    let re = new RegExp("{" + val.id.split('_')[3] + "}", "g");
                    content = content.replace(re, val.value);
                });
                content = "【北京应通】" + content;
                if (confirm(content)) {
                    let targetPhone = $("#targetPhone").val();
                    let params = {};
                    let data = {};
                    data['phones'] = targetPhone;
                    data['template_id'] = $("#sms_template").val();
                    $("input[id*='send_content_id_']").each(function (i, val) {
                        params[val.id.split('_')[3]] = val.value;
                    });
                    data['params'] = params;

                    $.ajax({
                        type: "POST",
                        url: "send_sms_via_ali",
                        data: JSON.stringify(data),
                        dataType: 'json',
                        contentType: 'application/json; charset=UTF-8',
                        success: function (result) {
                            if (result.code === 'success') {
                                mApp.unblock('#send_sms_modal .modal-content');
                                $("#send_sms_modal").modal('hide');
                                $('#ajax_data').mDatatable().destroy();
                                DatatableRemoteAjaxSMS.init();
                                toastr.info(result.message);
                                //setTimeout("location.reload()", 1000);
                            } else {
                                mApp.unblock('#send_sms_modal .modal-content');
                                $('#send_sms_modal').modal('hide');
                                toastr.warning(result.message);
                            }

                        },
                        error: function (xhr, msg, e) {
                            mApp.unblock('#sendmail2 .modal-content');
                            $('#sendmail2').modal('hide');
                            toastr.warning("系统繁忙");
                        }
                    });
                } else {
                    return false;

                }
            }
        });
    }

    return {
        // public functions
        init: function () {
            sms();
        }
    };
}();

jQuery(document).ready(function () {
    FormControlsSMS.init();
});
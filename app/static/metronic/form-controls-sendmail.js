//== Class definition

var FormControlsSendmail = function () {
    //== Private functions

    var demo1 = function () {
        $("#m_form_excel").validate({
            // define validation rules
            rules: {
                title: {
                    required: true
                },
                daterange: {
                    required: true
                }
            },

            //display error alert on form submit  
            invalidHandler: function (event, validator) {
                var alert = $('#m_form_excel_msg');
                alert.removeClass('m--hide').show();
                mApp.scrollTo(alert, -200);
            },

            submitHandler: function (form) {

                let queued_file_length = myDropzone.getQueuedFiles().length;
                console.log(queued_file_length);
                if (queued_file_length>0) {
                    mApp.block('#sendmail2 .modal-content', {
                        overlayColor: '#000000',
                        type: 'loader',
                        state: 'success',
                        size: 'lg'
                    });
                    myDropzone.processQueue();
                }
                else {
                    toastr.warning("未上传文件");
                }

            }
        });
    }


    return {
        // public functions
        init: function () {
            demo1();
        }
    };
}();

jQuery(document).ready(function () {
    FormControlsSendmail.init();
});
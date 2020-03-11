//== Class definition

var FormControlsMailTemplet = function () {
    //== Private functions

    var demo1 = function () {
        $("#m_form_new_templet").validate({
            // define validation rules
            rules: {
                templet_name: {
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
                let queued_file_length = myDropzone.getQueuedFiles().length;
                console.log(queued_file_length);
                if (queued_file_length>0) {
                    mApp.block('#m_form_new_templet .modal-content', {
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
    FormControlsMailTemplet.init();
});
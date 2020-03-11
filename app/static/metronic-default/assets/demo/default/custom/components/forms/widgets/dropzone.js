//== Class definition

var DropzoneDemo = function () {
    //== Private functions
    var demos = function () {
        // file type validation
        Dropzone.options.mDropzoneThree = {
            paramName: "file", // The name that will be used to transfer the file
            maxFiles: 1,
            maxFilesize: 20, // MB
            addRemoveLinks: true,
            autoProcessQueue: false,
            acceptedFiles: ".doc,.docx,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            url: 'update_mail_templet',
            init: function () {
                myDropzone = this;
                myDropzone.on("complete", function (file) {
                    myDropzone.removeFile(file);
                });
            },
            accept: function (file, done) {
                done();
            },
            success: function (file, result) {
                let hid = $('#hid').html();
                let templet_name = $('#templet_name').val();
                let templet_desc = $('#templet_desc').val();

                let params = {
                    'hid': hid,
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
                        $('#new_templet_model').modal('hide');
                         mApp.unblock('#m_form_new_templet .modal-content');
                    },
                    error: function (xhr, msg, e) {
                        toastr.warning(msg.content);
                        $('#new_templet_model').modal('hide');
                         mApp.unblock('#m_form_new_templet .modal-content');
                    }
                });
            }
        };
    }

    return {
        // public functions
        init: function () {
            demos();
        }
    };
}();

DropzoneDemo.init();
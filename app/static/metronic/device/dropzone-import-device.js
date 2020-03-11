//== Class definition

var DropzoneDevice = function () {
    //== Private functions
    let demos = function () {
        // file type validation
        Dropzone.options.mDropzoneDevice = {
            paramName: "file", // The name that will be used to transfer the file
            maxFiles: 1,
            maxFilesize: 20, // MB
            addRemoveLinks: true,
            acceptedFiles: ".xlsx",
            autoProcessQueue: false,
            url: 'import_device_from_excel',
            init: function () {
                myDropzone = this;
                myDropzone.on("complete", function (file) {
                    myDropzone.removeFile(file);
                });
            },
            accept: function (file, done) {
                done();
            },
            success: function (file, done) {
                console.log("upload device file success, start to sync to db");
                $.ajax({
                    type: "POST",
                    url: "import_device_to_database",
                    dataType: 'json',
                    contentType: 'application/json; charset=UTF-8',
                    success: function (result) {
                        if (result.status === 'true') {
                            mApp.unblock('#file_upload .modal-content');
                            $("#file_upload").modal('hide');
                            $('#ajax_data').mDatatable().destroy();
                            DatatableRemoteAjaxCutover.init();
                            toastr.info(result.content);
                            //setTimeout("location.reload()", 1000);
                        } else {

                            mApp.unblock('#file_upload .modal-content');
                            $('#file_upload').modal('hide');
                            toastr.warning(result.content);
                        }

                    },
                    error: function (xhr, msg, e) {
                        mApp.unblock('#file_upload .modal-content');
                        $('#file_upload').modal('hide');
                        toastr.warning("系统繁忙");
                    }
                });
            }
        };
    };

    return {
        // public functions
        init: function () {
            demos();
        }
    };
}();

DropzoneDevice.init();




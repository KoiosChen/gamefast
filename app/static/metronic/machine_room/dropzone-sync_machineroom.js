//== Class definition

var DropzoneMachineRoom = function () {
    //== Private functions
    let demos = function () {
        // file type validation
        Dropzone.options.mDropzoneMachineroom = {
            paramName: "file", // The name that will be used to transfer the file
            maxFiles: 1,
            maxFilesize: 20, // MB
            addRemoveLinks: true,
            acceptedFiles: ".xlsx",
            autoProcessQueue: false,
            url: 'update_machine_room_from_excel',
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
                console.log("upload machine room file success, start to sync to dab");
                $.ajax({
                    type: "POST",
                    url: "import_machine_room_to_database",
                    dataType: 'json',
                    contentType: 'application/json; charset=UTF-8',
                    success: function (result) {
                        if (result.status === 'true') {
                            mApp.unblock('#machine_room_batch_upload .modal-content');
                            $("#machine_room_batch_upload").modal('hide');
                            $('#ajax_data').mDatatable().destroy();
                            DatatableRemoteAjaxDemo.init();
                            toastr.info(result.content);
                            //setTimeout("location.reload()", 1000);
                        } else {

                            mApp.unblock('#machine_room_batch_upload .modal-content');
                            $('#machine_room_batch_upload').modal('hide');
                            toastr.warning(result.content);
                        }

                    },
                    error: function (xhr, msg, e) {
                        mApp.unblock('#machine_room_batch_upload .modal-content');
                        $('#machine_room_batch_upload').modal('hide');
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

DropzoneMachineRoom.init();



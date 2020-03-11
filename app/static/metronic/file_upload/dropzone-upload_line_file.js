//== Class definition

var DropzoneDemo = function () {
    //== Private functions
    var demos = function () {
        // file type validation
        Dropzone.options.mDropzoneThree = {
            paramName: "file", // The name that will be used to transfer the file
            maxFiles: 10,
            maxFilesize: 10, // MB
            addRemoveLinks: true,
            acceptedFiles: "image/*,application/pdf,.doc,.docx,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            url: 'upload_fileOfLines',
            init: function () {
                this.on("complete", function (file) {
                    $('#file_upload').mDatatable().destroy();
                    DatatableRemoteAjaxCustomer.init();
                });
            },
            accept: function (file, done) {
                done();
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
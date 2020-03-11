//== Class definition

var dropzone_cutover;

var DropzoneCutover = function () {
    //== Private functions
    let demos = function () {
        // file type validation
        Dropzone.options.mDropzoneTwo = {
            paramName: "file", // The name that will be used to transfer the file
            maxFiles: 1,
            maxFilesize: 20, // MB
            addRemoveLinks: true,
            acceptedFiles: ".xlsx",
            autoProcessQueue: false,
            url: 'update_cutover_excel',
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
                let pops = [];
                $('#m_repeater_4 :input').each(function () {
                    let l_name = $(this).attr('name');
                    let l_value = $(this).val();
                    const aaa = {};
                    aaa[l_name] = l_value;
                    console.log(aaa);
                    pops.push(aaa);
                });
                console.log('sending mail from excel');
                let cutover_title = $("#cutover_title_2").val();
                let cutover_duration = $("#cutover_duration_2").val();
                let cutover_datetime = $('#m_daterangepicker_fromexcel .form-control').val();
                let cutover_send_date = $('#m_datepicker_1_modal_2').val();
                if ($('#emergency_2').is(":checked")) {
                    var emergency = 1
                } else {
                    var emergency = 0
                }

                let cutover_reason = $('#cutover_reason_2').val();

                let params = {
                    "cutover_title": cutover_title,
                    "cutover_datetime": cutover_datetime,
                    "cutover_reason": cutover_reason,
                    "cutover_send_date": cutover_send_date,
                    "cutover_emergency": emergency,
                    "pops": pops,
                    "cutover_duration": cutover_duration
                };
                console.log(params);

                $.ajax({
                    type: "POST",
                    url: "send_cutover_mail_from_excel",
                    data: JSON.stringify(params),
                    dataType: 'json',
                    contentType: 'application/json; charset=UTF-8',
                    success: function (result) {
                        if (result.status === 'true') {
                            mApp.unblock('#sendmail2 .modal-content');
                            $("#sendmail2").modal('hide');
                            $('#ajax_data').mDatatable().destroy();
                            DatatableRemoteAjaxCutover.init();
                            toastr.info(result.content);
                            //setTimeout("location.reload()", 1000);
                        } else {

                            mApp.unblock('#sendmail2 .modal-content');
                            $('#sendmail2').modal('hide');
                            toastr.warning(result.content);
                        }

                    },
                    error: function (xhr, msg, e) {
                        mApp.unblock('#sendmail2 .modal-content');
                        $('#sendmail2').modal('hide');
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

DropzoneCutover.init();
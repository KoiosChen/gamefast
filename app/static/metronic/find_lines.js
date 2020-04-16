
//== Class definition

var DatatableRemoteAjaxCustomer = function () {
    //== Private functions

    // basic demo
    var datatable;
    var demo = function (param) {
        datatable = $('#ajax_modal_data').mDatatable({
            // datasource definition
            data: {
                type: 'remote',
                source: {
                    read: {
                        // sample GET method
                        method: 'POST',
                        url: '/find_lines',
                        params: {
                            // custom query params
                            param
                        },
                        map: function (raw) {
                            // sample data mapping
                            var dataSet = raw;
                            if (typeof raw.data !== 'undefined') {
                                dataSet = raw.data;
                            }
                            return dataSet;
                        },
                    },
                },
                pageSize: 10,
                serverPaging: true,
                serverFiltering: true,
                serverSorting: false,
            },

            layout: {
                theme: 'default',
                class: '',
                scroll: false,
                footer: false
            },

            dom: 'Bfrtip',
            select: true,

            // column sorting
            sortable: false,

            pagination: true,

            autoWidth: true,
            footer: true,

            toolbar: {
                // toolbar items
                items: {
                    // pagination
                    pagination: {
                        // page size select
                        pageSizeSelect: [10, 20, 30, 50, 100],
                    },
                },
            },

            // columns definition

            columns: [
                {
                    field: 'RecordID',
                    title: '#',
                    sortable: false,
                    width: 40,
                    textAlign: 'center',
                    selector: {class: 'm-checkbox--solid m-checkbox--brand'},
                },
                {
                    field: 'id',
                    title: 'ID',
                    sortable: false, // disable sort for this column
                    width: 20,
                    selector: false,
                    textAlign: 'center',
                    template: '{{RecordID}}',
                }, {
                    field: 'customer_name',
                    title: '客户名称',
                    // sortable: 'asc', // default sort
                    filterable: false, // disable or enable filtering
                    width: 100,
                    // basic templating support for column rendering,
                }, {
                    field: 'line_code',
                    title: '线路编号',
                    width: 150,
                    responsive: {visible: 'md'}
                }, {
                    field: 'a_to_z',
                    title: '线路内容',
                    width: 150,
                    responsive: {visible: 'lg'}
                }, {
                    field: 'channel',
                    title: '通道',
                    width: 75,
                    responsive: {visible: 'md'}
                }, {
                    field: 'protect',
                    title: '保护',
                    width: 65,
                    responsive: {visible: 'md'}
                }, {
                    field: 'product_model',
                    title: '产品类型',
                    //width: 400,
                }, {
                    field: 'e-route',
                    title: 'E表',
                    width: 300,
                    responsive: {visible: 'lg'}
                }, {
                    field: 'start_date',
                    title: '开始日期',
                    type: 'date',
                    format: 'MM/DD/YYYY',
                }],
        });

    };

    var localSelectorDemo = function () {
        let ids = datatable.rows('.m-datatable__row--active').nodes().find('.m-checkbox--single > [type="checkbox"]').map(function (i, chk) {
            return $(chk).val();
        });
        let lines_ids = [];
        for (var i = 0; i < ids.length; i++) {
            lines_ids.push(ids[i]);
        }
        console.log(ids);
        let cutover_title = $("#cutover_title").val();
        let cutover_duration = $("#cutover_duration").val();
        let cutover_datetime = $('#m_daterangepicker_4 .form-control').val();
        let pops = [];
        let cutover_send_date = $('#m_datepicker_1_modal').val();
        if ($('#emergency').is(":checked")) {
            var emergency = 1
        }
        else {
            var emergency = 0
        }
        $('#m_repeater_3 :input').each(function () {
            let l_name = $(this).attr('name');
            let l_value = $(this).val();
            const aaa = {};
            aaa[l_name] = l_value;
            console.log(aaa);
            pops.push(aaa);
        });

        let cutover_reason = $('#cutover_reason').val();

        let params = {
            "cutover_title": cutover_title,
            "cutover_datetime": cutover_datetime,
            "cutover_reason": cutover_reason,
            "pops": pops,
            "ids": lines_ids,
            "cutover_send_date": cutover_send_date,
            "cutover_emergency": emergency,
            "cutover_duration": cutover_duration
        };
        console.log(params);

        $.ajax({
            type: "POST",
            url: "send_cutover_mail",
            data: JSON.stringify(params),
            dataType: 'json',
            contentType: 'application/json; charset=UTF-8',
            success: function (result) {
                if (result.status === 'true') {

                    $('#ajax_modal_data').mDatatable().destroy();
                    $("#add_machine_room").modal('hide');
                    toastr.info(result.content);
                    //setTimeout("location.reload()", 1000);
                } else {
                    toastr.warning(result.content);
                }

            },
            error: function (xhr, msg, e) {
                toastr.warning("系统繁忙");
            }
        });
        for (var i = 0; i < ids.length; i++) {
            console.log(i);
            console.log(ids[i])
        }

    };

    return {
        // public functions
        init: function (param) {
            demo(param);
        },
        multiselect: function () {
            localSelectorDemo();
        }
    };
}();

$('#submit_search').click(function () {
    $('#ajax_modal_data').mDatatable().destroy();
    let param = '';
    DatatableRemoteAjaxCustomer.init(param);
});

//== Class definition
var tableObj;
let DatatableSendResult = function (rowId) {
    let tableId = $("#send_result_table");
    let table = tableId.DataTable({
        dom: "Bfrtip",
        scrollCollapse: true,
        paging: false,
        "processing": true,
        ajax: {
            url: "/query_send_result_table",
            data: {"row_id": rowId,},
        },
        "order": [[0, 'desc',],],
        columns: [
            {data: "phone",},
            {data: "status",},
            {data: "err_code",},
            {data: "send_date",},
        ],
        select: {
            style: 'os',
            selector: 'td:first-child',
        },
        buttons: [],
    });

    return table
}


let DatatableRemoteAjaxSMS = function () {
    //== Private functions

    // basic demo
    let demo = function () {
        let datatable = $('#ajax_data').mDatatable({
            // data source definition
            data: {
                type: 'remote',
                source: {
                    read: {
                        // sample GET method
                        method: 'POST',
                        url: '/sms_order',
                        map: function (raw) {
                            // sample data mapping
                            let dataSet = raw;
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

            // layout definition
            layout: {
                scroll: false,
                footer: false
            },

            // column sorting
            sortable: false,

            pagination: true,

            autoWidth: true,

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
                    field: 'id',
                    title: '订单号',
                    sortable: false, // disable sort for this column
                    selector: false,
                    width: 400,
                    textAlign: 'center',
                }, {
                    field: 'phones',
                    title: '手机号',
                    width: 200,
                    textAlign: 'center',
                },{
                    field: 'SendResult',
                    title: '查询结果',
                    textAlign: 'center',
                    width: 100,
                    // sortable: 'asc', // default sort
                    filterable: false, // disable or enable filtering
                    template: function (row) {
                        return '<a ' + 'onClick="return CheckResult(\'' + row.id + '\')" class="m-portlet__nav-link btn m-btn m-btn--hover-info m-btn--icon m-btn--icon-only m-btn--pill m-btn--wide" title="发送结果">' + '<i class="fa fa-angle-double-right"></i>' + '</a>';
                    },
                }, {
                    field: 'total',
                    title: '发送数量',
                    textAlign: 'center',
                }, {
                    field: 'sent_content',
                    title: '短信内容',
                    textAlign: 'center',
                }, {
                    field: 'operator',
                    title: '发送人',
                    textAlign: 'center',
                }, {
                    field: 'sent_time',
                    title: '发送时间',
                    type: 'date',
                    textAlign: 'center',
                    format: 'MM/DD/YYYY',
                }],
        });
    };


    return {
        // public functions
        init: function () {
            demo();
        },
    };
}();


jQuery(document).ready(function () {
    DatatableRemoteAjaxSMS.init();
});

// $('#submit_search').click(function () {
//     $('#ajax_data').mDatatable().destroy();
//     DatatableRemoteAjaxCutover.init();
// });

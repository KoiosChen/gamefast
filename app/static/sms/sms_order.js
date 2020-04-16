//== Class definition

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
                    field: 'total',
                    title: '发送数量',
                    textAlign: 'center',
                    width: 50,
                    // sortable: 'asc', // default sort
                    filterable: false, // disable or enable filtering
                    // basic templating support for column rendering,
                }, {
                    field: 'phones',
                    title: '发送手机',
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

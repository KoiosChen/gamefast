//== Class definition

var DatatableRemoteAjaxCutover = function () {
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
                        url: '/cutover_order',
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
                    title: '总数',
                    textAlign: 'center',
                    width: 50,
                    // sortable: 'asc', // default sort
                    filterable: false, // disable or enable filtering
                    // basic templating support for column rendering,
                }, {
                    field: 'cutover_starttime',
                    title: '割接开始时间',
                    textAlign: 'center',
                }, {
                    field: 'cutover_stoptime',
                    title: '割接结束时间',
                    textAlign: 'center',
                }, {
                    field: 'cutover_atoz',
                    title: '割接地点',
                    textAlign: 'center',
                }, {
                    field: 'templet',
                    title: '默认模板',
                    textAlign: 'center',
                }, {
                    field: 'cutover_send_date',
                    title: '邮件发送日期',
                    type: 'date',
                    format: 'YYYY/MM/DD',
                }, {
                    field: 'create_time',
                    title: '创建时间',
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
    DatatableRemoteAjaxCutover.init();
});

// $('#submit_search').click(function () {
//     $('#ajax_data').mDatatable().destroy();
//     DatatableRemoteAjaxCutover.init();
// });

//== Class definition

var DatatableRemoteAjaxCustomer = function () {
    //== Private functions

    // basic demo
    var demo = function () {

        var datatable = $('#ajax_data').mDatatable({
            // datasource definition
            data: {
                type: 'remote',
                source: {
                    read: {
                        // sample GET method
                        method: 'POST',
                        url: '/company',
                        params: {
                            // custom query params
                            query: {
                                search_content: $('#search_content').val()
                            }
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

            // layout definition
            layout: {
                scroll: false,
                footer: false
            },

            // column sorting
            sortable: false,

            pagination: true,

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
                    title: '#',
                    sortable: false, // disable sort for this column
                    width: 50,
                    selector: false,
                    textAlign: 'center'
                }, {
                    field: 'customer_name',
                    title: '客户名称',
                    textAlign: 'center',
                    width: 300
                    // basic templating support for column rendering,
                }, {
                    field: 'mail_templet',
                    title: '邮件模板',
                    textAlign: 'center',
                    width: 250
                }, {
                    field: 'biz_contact',
                    title: '客户商务联系人',
                    textAlign: 'center',
                    width: 150
                }, {
                    field: 'noc_contact',
                    title: '客户技术联系人',
                    textAlign: 'center',
                    width: 150
                }, {
                    field: 'customer_manager',
                    title: '我司客户经理',
                    textAlign: 'center',
                    width: 150
                }, {
                    field: 'Actions',
                    width: 100,
                    textAlign: 'center',
                    title: '操作',
                    sortable: false,
                    overflow: 'visible',
                    template: function (row, index, datatable) {
                        return '<a ' + 'data-toggle="modal" data-target="#update_customer_model" onclick="editInfo(' +  row.id + ', \'' + row.customer_name + '\', \'' + row.mail_templet + '\')" class="m-portlet__nav-link btn m-btn m-btn--hover-accent m-btn--icon m-btn--icon-only m-btn--pill" title="Edit details">\
                                    <i class="la la-edit"></i>\
                                </a>\
                                <a ' + 'onClick="return HTMerDel(' + row.id + ')" class="m-portlet__nav-link btn m-btn m-btn--hover-danger m-btn--icon m-btn--icon-only m-btn--pill" title="Delete">\
                                    <i class="la la-trash"></i>\
                                </a>\
                            ';
                    },
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
    DatatableRemoteAjaxCustomer.init();
});

$('#search_submit').click(function () {
    $('#ajax_data').mDatatable().destroy();
    DatatableRemoteAjaxCustomer.init();
})
//== Class definition


var DatatableRemoteAjaxMailTemplet = function () {
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
                        url: '/mail_templet_manager',
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
                    width: 20,
                    selector: false,
                    textAlign: 'center'
                }, {
                    field: 'templet_name',
                    title: '模板名称',
                    textAlign: 'center',
                    width: 250
                    // basic templating support for column rendering,
                }, {
                    field: 'templet_desc',
                    title: '描述',
                    textAlign: 'center',
                    width: 300
                }, {
                    field: 'bind_company',
                    title: '关联客户数量',
                    textAlign: 'center',
                    width: 250
                }, {
                    field: "status",
                    title: "状态",
                    width: 100,
                    textAlign: 'center',
                    // callback function support for column rendering
                    template: function (row) {
                        let status = {
                            'true': {'title': '正常', 'class': ' m-badge--success'},
                            'false': {'title': '禁用', 'class': ' m-badge--danger'},
                        };
                        return '<span class="m-badge ' + status[row.status].class + ' m-badge--wide">' + status[row.status].title + '</span>';
                    }
                }, {
                    field: 'Actions',
                    width: 100,
                    textAlign: 'center',
                    title: '操作',
                    sortable: false,
                    overflow: 'visible',
                    template: function (row) {
                        console.log(row.id + ' ' + row.status);
                        if (row.status === true) {
                            return '<a ' + 'onClick="return HTMerDel(' + row.id + ')" class="m-portlet__nav-link btn m-btn m-btn--hover-danger m-btn--icon m-btn--icon-only m-btn--pill" title="Delete">\
                                    <i class="la la-ban"></i>\
                                </a>\
                                <a ' + 'data-toggle="modal" data-target="#new_templet_model" onclick="editInfo(' + row.id + ', \'' + row.templet_name + '\', \'' + row.templet_desc + '\')" class="m-portlet__nav-link btn m-btn m-btn--hover-accent m-btn--icon m-btn--icon-only m-btn--pill" title="Edit details">\
                                    <i class="la la-edit"></i>\
                                </a>\
                                <a href="../static/mail_templet/' + row.templet_path + '"target="_Blank"> \
                                   <i class="flaticon-download"></i> \
                                </a>\
                            ';
                        } else if (row.status === false) {
                            return '<a ' + 'onClick="return HTMerEnable(' + row.id + ')" class="m-portlet__nav-link btn m-btn m-btn--hover-danger m-btn--icon m-btn--icon-only m-btn--pill" title="Delete">\
                                    <i class="la la-check-circle"></i>\
                                </a>\
                                <a ' + 'data-toggle="modal" data-target="#new_templet_model" onclick="editInfo(' + row.id + ', \'' + row.templet_name + '\', \'' + row.templet_desc + '\')" class="m-portlet__nav-link btn m-btn m-btn--hover-accent m-btn--icon m-btn--icon-only m-btn--pill" title="Edit details">\
                                    <i class="la la-edit"></i>\
                                </a>\
                                <a href="../static/mail_templet/' + row.templet_path + '"target="_Blank"> \
                                   <i class="flaticon-download"></i> \
                                </a>\
                            ';
                        }

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
    DatatableRemoteAjaxMailTemplet.init();
});

$('#submit_search').click(function () {
    $('#ajax_data').mDatatable().destroy();
    DatatableRemoteAjaxMailTemplet.init();
})
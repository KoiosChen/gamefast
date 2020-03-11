//== Class definition

var DatatableRemoteAjaxFileList = function () {
    //== Private functions

    // basic demo
    var demo = function () {

        var datatable = $('#file_list').mDatatable({
            // datasource definition
            data: {
                type: 'remote',
                source: {
                    read: {
                        // sample GET method
                        method: 'POST',
                        url: '/file_list',
                        params: {
                            // custom query params
                            query: {
                                row_id: $('#row_id2').html()
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
                    width: 20,
                    selector: false,
                    textAlign: 'center'
                }, {
                    field: 'name',
                    title: '文件名',
                    textAlign: 'center',
                    width: 550,
                    template: function (row, index, datatable) {
                        return '<a href="../static/upload_file/' + row.name + '"target="_Blank">' + row.name + '</a>'

                    }
                    // basic templating support for column rendering,
                },{
                    field: 'Actions',
                    width: 100,
                    textAlign: 'center',
                    title: '操作',
                    sortable: false,
                    overflow: 'visible',
                    template: function (row, index, datatable) {
                        return '<a ' + 'onClick="return HTMerDel(' + row.id + ')" class="m-portlet__nav-link btn m-btn m-btn--hover-danger m-btn--icon m-btn--icon-only m-btn--pill" title="Delete">\
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
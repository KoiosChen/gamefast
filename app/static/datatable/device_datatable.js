var DatatableInterface = function (row_id) {
    let int_table_id = $("#device_int_table");
    let table = int_table_id.DataTable({
        dom: "Bfrtip",
        scrollCollapse: true,
        paging: false,
        "processing": true,
        ajax: {
            url: "/query_interface_table",
            data: {"row_id": row_id}
        },
        "order": [[0, 'desc']],
        columns: [
            {data: "interface_name"},
            {data: "interface_desc"},
            {data: "interface_type"},
            {data: "interface_status"}
        ],
        select: {
            style: 'os',
            selector: 'td:first-child',
        },
        buttons: [],
    });

    return table
}

var DatatableDevice = function () {
    var interface_datatable;
    let table_id = $("#device_table");
    let device_table = new $.fn.dataTable.Editor({
        ajax: "/query_device_table",
        table: "#device_table",
        fields: [
            {label: "设备名称*", name: "device_name"},
            {label: "管理IP*", name: "device_ip"},
            {label: "机房*", name: "machine_room_id", type: "select"},
            {label: "平台*", name: "platform_id", type: "select"},
            {label: "厂商*", name: "vendor", type: "select"},
            {label: "型号", name: "device_model", type: "select"},
            {label: "OS", name: "os_version"},
            {label: "PATCH", name: "patch_version"},
            {label: "序列号", name: "serial_number"},
            {label: "community", name: "community", type: "password"},
            {label: "登陆方法", name: "login_method", type: "select"},
            {label: "用户名", name: "login_name"},
            {label: "登陆密码", name: "login_password", type: "password"},
            {label: "enable密码", name: "enable_password", type: "password"},
            {label: "设备归属", name: "device_belong_id", type: "select"},
            {label: "是否立即同步设备信息", name: "sync_device_info", type: "select", options: ['YES', 'NO']}
        ]
    });

    $('button.editor_create').on('click', function (e) {
        e.preventDefault();
        device_table.create({
            buttons: '新增'
        });
    });

    // Delete a record
    table_id.on('click', 'a.editor_remove', function (e) {
        e.preventDefault();
        device_table.remove($(this).closest('tr'), {
            title: '删除设备',
            message: '删除后无法恢复，是否确认?',
            buttons: '删除'
        });
    });

    // device sync
    table_id.on('click', 'a.editor_sync', function (e) {
        e.preventDefault();
        let ip = $(this).closest('tr').find('td').eq(1).text();
        console.log(ip);
        $.ajax({
            url: '/call_api_get_interface',
            data: JSON.stringify({"data": {"ip": ip}}),
            contentType: 'application/json',
            async: false,
            dataType: 'json',
            type: 'post',
            success: function (jsonData) {
                if (jsonData.code === 'success') {
                    alert(jsonData.msg)
                } else {
                    alert("sync error")
                }
            }
        });
    });

    table_id.on('click', 'tbody td', function (e) {
        let index = $(this).index();
        let head_name = table_id.find("thead").eq(0).find("tr").eq(0).find("th").eq(index).text();
        // 备注
        if (head_name !== "设备名称" && head_name !== "操作" && head_name !== "接口") {
            device_table.bubble(this, {
                submit: 'changed'
            });
        } else if (head_name === "接口") {
            if (interface_datatable) {
                interface_datatable.settings()[0].ajax.data = {"row_id": $(this).parent().attr("id")};
                interface_datatable.ajax.reload();
            }
            else {
                interface_datatable = DatatableInterface($(this).parent().attr("id"))
            }
        }
    });

    let table = table_id.DataTable({
        dom: "Bfrtip",
        scrollY: '80vh',
        scrollCollapse: true,
        paging: false,
        "processing": true,
        "scrollX": true,
        ajax: "/query_device_table",
        "order": [[0, 'desc']],
        "columnDefs": [
            {"visible": false, "targets": []}
        ],
        columns: [
            {data: "device_name"},
            {data: "device_ip"},
            {
                data: null, render: function (data, type, row) {
                    return data.machine_room;
                },
                editField: ['machine_room_id']
            },
            {
                data: null, render: function (data, type, row) {
                    return data.platform;
                },
                editField: ['platform_id']
            },
            {data: "vendor"},
            {data: "device_model"},
            {data: "os_version"},
            {data: "patch_version"},
            {data: "serial_number"},
            {
                data: null, render: function (data, type, row) {
                    return "******";
                },
                editField: ['community']
            },
            {data: "login_method"},
            {
                data: null,
                defaultContent: "***",
                className: "center",
                editField: ['login_name', 'login_password', 'enable_password']
            },
            {data: "monitor_status"},
            {
                data: null, render: function (data, type, row) {
                    return data.device_belong;
                },
                editField: ['device_belong_id']
            },
            {
                data: null,
                className: "center",
                render: function (data, type, row) {
                    return '<a data-toggle="modal" data-target="#interface_query" class="m-portlet__nav-link btn m-btn m-btn--hover-accent m-btn--icon m-btn--icon-only m-btn--pill" title="Query Interface">\
                                    <i class="la la-search"></i>\
                                </a>';

                }
            },
            {
                data: null,
                className: "center",
                defaultContent: '<a href="" class="editor_sync">同步</a>/<a href="" class="editor_remove">删除</a>'
            }
        ],
        select: {
            style: 'os',
            selector: 'td:first-child'
        },
        buttons: []
    });

    return table
};

$(document).ready(function () {
    DatatableDevice();

    $.extend(true, $.fn.dataTable.Editor.Field.defaults, {
        attr: {
            autocomplete: 'off'
        }
    });

});


//上传文件
function fileUpload(row_id, name, address) {
    $('#row_id').html(row_id);
    $('#device_name2').val(name);
    $('#device_ip2').val(address);
    DatatableRemoteAjaxFileList.init();
    $("#file_list").mDatatable().destroy();
    DatatableRemoteAjaxFileList.init();
}


// toastr options
toastr.options = {
    "closeButton": true, //是否显示关闭按钮
    "debug": false, //是否使用debug模式
    "progressBar": false,
    "positionClass": "toast-top-center",//弹出窗的位置
    "showDuration": "300",//显示的动画时间
    "hideDuration": "1000",//消失的动画时间
    "timeOut": "2000", //展现时间
    "extendedTimeOut": "1000",//加长展示时间
    "showEasing": "swing",//显示时的动画缓冲方式
    "hideEasing": "linear",//消失时的动画缓冲方式
    "showMethod": "fadeIn",//显示时的动画方式
    "hideMethod": "fadeOut" //消失时的动画方式
};

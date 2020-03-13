var DatatableDevice = function () {
    let table_id = $("#device_table");
    let device_table = new $.fn.dataTable.Editor({
        ajax: "/query_device_table",
        table: "#device_table",
        fields: [
            {label: "设备名称*", name: "device_name"},
            {label: "管理IP*", name: "device_ip"},
            {label: "厂商*", name: "vendor", type: "select"},
            {label: "型号", name: "device_model", type: "select"},
            {label: "机房*", name: "machine_room_id", type: "select"},
            // {label: "OS", name: "os_version"},
            // {label: "PATCH", name: "patch_version"},
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

    table_id.on('click', 'tbody td', function (e) {
        let index = $(this).index();
        let head_name = table_id.find("thead").eq(0).find("tr").eq(0).find("th").eq(index).text();
        // 备注
        if (head_name === "备注") {
            editInfo($(this).parent().attr("id"), $(this).parent().find('td').eq(0).text(), $(this).parent().find('td').eq(1).text())
        }
        // 最后一列处理 备注
        else if (head_name === "文件管理") {
            fileUpload($(this).parent().attr("id"), $(this).parent().find('td').eq(0).text(), $(this).parent().find('td').eq(1).text())
        } else if (head_name !== "设备名称") {
            device_table.bubble(this, {
                submit: 'changed'
            });
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
            // {
            //     // targets用于指定操作的列，从第0列开始，-1为最后一列，这里第六列
            //     // return后边是我们希望在指定列填入的按钮代码
            //     "targets": 13,
            //     "render": function (data, type, full, meta) {
            //         return '<a data-toggle="modal" data-target="#memo_editor" class="m-portlet__nav-link btn m-btn m-btn--hover-accent m-btn--icon m-btn--icon-only m-btn--pill" title="Edit details">\
            //                         <i class="la la-edit"></i>\
            //                     </a>';
            //     }
            // },
            // {
            //     // targets用于指定操作的列，从第0列开始，-1为最后一列
            //     // return后边是我们希望在指定列填入的按钮代码
            //     "targets": 12,
            //     "render": function (data, type, full, meta) {
            //         return '<a data-toggle="modal" data-target="#file_upload" class="m-portlet__nav-link btn m-btn m-btn--hover-accent m-btn--icon m-btn--icon-only m-btn--pill" title="Edit details">\
            //                         <i class="la la-file"></i>\
            //                     </a>';
            //     }
            // },
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
                data: null, render: function (data, type, row) {
                    return "***";
                },
                editField: ['login_name', 'login_password', 'enable_password']
            },
            {data: "monitor_status"},
            {
                data: null, render: function (data, type, row) {
                    return data.device_belong;
                },
                editField: ['device_belong_id']
            },
            // {data: null},
            // {data: null},
            {
                data: null,
                className: "center",
                defaultContent: '<a href="" class="editor_remove">Delete</a>'
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

//编辑备注
function editInfo(row_id, name, ip) {
    console.log(row_id + ' ' + name + ' ' + ip)
    let x = document.getElementsByName('postli');
    if (x.length > 0) {
        for (var i = x.length - 1; i >= 0; i--) {
            x[i].parentNode.removeChild(x[i]);
        }
    }

    document.getElementById('flask-pagedown-body').value = '';
    document.getElementById('itemContainer').style.minHeight = "0px";

    $('#row_id').html(row_id);
    $('#device_name').val(name);
    $('#device_ip').val(ip);

    params = '{"row_id":"' + row_id + '"}';
    $.ajax({
        type: "POST",
        url: "get_memo",
        data: params,
        dataType: 'text',
        contentType: "application/json; charset=utf-8",
        success: function (msg) {
            let msg_json = JSON.parse(msg);
            msg_json = JSON.parse(msg_json);
            $.each(msg_json, function (i) {
                var converter = new showdown.Converter();
                converter.setOption('parseImgDimensions', true);
                let my_li = document.createElement('li');
                my_li.setAttribute('class', 'post');
                my_li.setAttribute('name', 'postli');
                let div1 = document.createElement('div');
                div1.setAttribute('class', 'post-date');
                div1.innerHTML = msg_json[i]['timestamp'];
                let div2 = document.createElement('div');
                div2.setAttribute('class', 'post-author');
                div2.innerHTML = msg_json[i]['username'] + '(' + msg_json[i]['phoneNum'] + ')';
                let div3 = document.createElement('div');
                div3.setAttribute('class', 'post-body');
                let html = converter.makeHtml(msg_json[i]['body_html']);
                div3.innerHTML = html;
                my_li.appendChild(div1);
                my_li.appendChild(div2);
                my_li.appendChild(div3);
                document.getElementById('itemContainer').appendChild(my_li);
            })
        },
        error: function (xhr, msg, e) {
            toastr.warning("系统繁忙");
        }
    });
}

// 备注modal弹出控制
$('#memo_editor').on('shown.bs.modal', function () {
    if (document.getElementsByName('postli').length > 0) {
        setTimeout(show_jpage, 50);
        function show_jpage() {
            $("div.holder").jPages({
                containerID: "itemContainer",
                perPage: 5
            });
        }
    }
});

//提交更改
function update() {
    //获取模态框数据
    let row_id = $('#row_id').html();
    let body = $('#flask-pagedown-body').val();
    if (body) {
        $.ajax({
            type: "POST",
            url: "memo_update",
            data: {"row_id": row_id, "body": body},
            dataType: 'html',
            contentType: "application/x-www-form-urlencoded; charset=utf-8",
            success: function (result) {
                toastr.info('提交成功');
                $("#update").modal('hide');
                //setTimeout("location.reload()", 1000);
            },
            error: function (xhr, msg, e) {
                toastr.warning("系统繁忙");
            }
        });
    } else {
        toastr.warning("未输入任何内容")
    }
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

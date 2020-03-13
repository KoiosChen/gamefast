var DatatableMachineRoom = function () {
    let table_id = $("#machine_room_table");
    let machine_room_table = new $.fn.dataTable.Editor({
        ajax: "/query_machine_room_table",
        table: "#machine_room_table",
        template: "#customForm",
        fields: [
            {label: "机房名称", name: "name"},
            {label: "搜索城镇：", name: "search_city_a",},
            {label: "城镇", name: "a_pop_city_id", type: "select"},
            {label: "地址", name: "address"},
            {
                label: "级别",
                name: "level_id",
                type: "select",
            },
            {
                label: "状态",
                name: "status_id",
                type: "select",
            },
            {
                label: "是否有电梯",
                name: "lift_id",
                type: "select",
            },
            {
                label: "类型",
                name: "type_id",
                type: "select",
            },
            {label: "姓名:", name: "noc_contact_name"},
            {label: "电话:", name: "noc_contact_phone"},
            {label: "邮箱:", name: "noc_contact_email"},
        ]
    });

    $('button.editor_create').on('click', function (e) {
        e.preventDefault();
        search_city(machine_room_table);
        machine_room_table.create({
            title: '新增机房',
            buttons: '新增'
        });
    });

    // Delete a record
    $('#machine_room_table').on('click', 'a.editor_remove', function (e) {
        e.preventDefault();
        machine_room_table.remove($(this).closest('tr'), {
            title: '删除机房',
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
        } else if (head_name === "地址") {
            search_city(machine_room_table);
            machine_room_table.bubble(this, {
                submit: 'changed'
            });
        } else if (head_name !== "机房名称") {
            machine_room_table.bubble(this, {
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
        ajax: "/query_machine_room_table",
        "order": [[0, 'desc']],
        "columnDefs": [
            // {
            //     // targets用于指定操作的列，从第0列开始，-1为最后一列，这里第六列
            //     // return后边是我们希望在指定列填入的按钮代码
            //     "targets": 7,
            //     "render": function (data, type, full, meta) {
            //         return '<a data-toggle="modal" data-target="#memo_editor" class="m-portlet__nav-link btn m-btn m-btn--hover-accent m-btn--icon m-btn--icon-only m-btn--pill" title="Edit details">\
            //                         <i class="la la-edit"></i>\
            //                     </a>';
            //     }
            // },
            // {
            //     // targets用于指定操作的列，从第0列开始，-1为最后一列
            //     // return后边是我们希望在指定列填入的按钮代码
            //     "targets": 6,
            //     "render": function (data, type, full, meta) {
            //         return '<a data-toggle="modal" data-target="#file_upload" class="m-portlet__nav-link btn m-btn m-btn--hover-accent m-btn--icon m-btn--icon-only m-btn--pill" title="Edit details">\
            //                         <i class="la la-file"></i>\
            //                     </a>';
            //     }
            // },
            {"visible": false, "targets": []}
        ],
        columns: [
            {data: "name"},
            {
                data: null, render: function (data, type, row) {
                    return data.city + "/" + data.address;
                },
                editField: ['search_city_a', 'a_pop_city_id', 'address']
            },
            {
                data: null, render: function (data, type, row) {
                    return data.type + data.level;
                },
                editField: ['type_id', 'level_id']
            },
            {
                data: null, render: function (data, type, row) {
                    return data.lift;
                },
                editField: ['lift_id']
            },
            {
                data: null, render: function (data, type, row) {
                    return data.status;
                },
                editField: ['status_id']
            },
            {
                data: null, render: function (data, type, row) {
                    return '姓名: ' + data.noc_contact_name + '<br>' + '电话: ' + data.noc_contact_phone + '<br>' + 'Email: ' + data.noc_contact_email;
                },
                editField: ['noc_contact_name', 'noc_contact_phone', 'noc_contact_email']
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
    DatatableMachineRoom();
    $.extend(true, $.fn.dataTable.Editor.Field.defaults, {
        attr: {
            autocomplete: 'off'
        }
    });

});

//上传文件
function fileUpload(row_id, name, address) {
    $('#row_id').html(row_id);
    $('#machine_room_name2').val(name);
    $('#machine_room_address2').val(address);
    DatatableRemoteAjaxFileList.init();
    $("#file_list").mDatatable().destroy();
    DatatableRemoteAjaxFileList.init();
}

//编辑备注
function editInfo(row_id, name, address) {
    console.log(row_id + ' ' + name + ' ' + address)
    let x = document.getElementsByName('postli');
    if (x.length > 0) {
        for (var i = x.length - 1; i >= 0; i--) {
            x[i].parentNode.removeChild(x[i]);
        }
    }

    document.getElementById('flask-pagedown-body').value = '';
    document.getElementById('itemContainer').style.minHeight = "0px";

    $('#row_id').html(row_id);
    $('#machine_room_name').val(name);
    $('#machine_room_address').val(address);

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

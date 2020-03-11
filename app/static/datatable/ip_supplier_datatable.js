var DatatableIPSupplier = function () {
    let table_id = $("#supplier_table");
    let ip_supplier_table = new $.fn.dataTable.Editor({
        ajax: "/query_ip_supplier_table",
        table: "#supplier_table",
        template: "#customForm",
        fields: [
            {label: "供应商名称", name: "supplier_name"},
            {label: "带宽", name: "bandwidth"},
            {label: "带宽单位", name: "bandwidth_unit", type: "select", options: ['M', 'G', 'T']},
            {label: "搜索A端城市：", name: "search_city_a",},
            {label: "A端城市", name: "a_pop_city_id", type: "select"},
            {label: "A端机房", name: "a_pop_id", type: "select"},
            {label: "A端设备", name: "a_pop_device_id", type: "select"},
            {label: "A端设备端口", name: "a_pop_interface_id", type: "select"},
            {
                label: "接入模式:",
                name: "mode",
                type: "select"
            },
            {label: "互联地址（供应商端）: ", name: "interconnection_supplier"},
            {label: "互联地址（我端）: ", name: "interconnection_us"},
            {label: "互联地址掩码: ", name: "interconnection_netmask"},
            {label: "Vlan: ", name: "vlan"},
            {label: "Vlan desc: ", name: "vlan_desc"},
            {
                label: "VLAN类型:",
                name: "vlan_type",
                type: "select",
                options: ["access", "trunk", "qinq", "vlan_map"],
            },
            {label: "Vlan mapping to: ", name: "vlan_map_to"},
            {label: "QinQ内层", name: "qinq_inside"},
            {label: "供应商商务姓名:", name: "biz_contact_name"},
            {label: "供应商商务电话:", name: "biz_contact_phoneNumber"},
            {label: "供应商商务邮箱:", name: "biz_contact_email"},
            {label: "供应商技术姓名:", name: "noc_contact_name"},
            {label: "供应商技术电话:", name: "noc_contact_phoneNumber"},
            {label: "供应商技术邮箱:", name: "noc_contact_email"},
            {label: "客户经理姓名:", name: "customer_manager_name"},
            {label: "客户经理电话:", name: "customer_manager_phoneNumber"},
            {
                label: "启用时间：",
                name: "start_time",
                type: 'datetime',
                def: function () {
                    return new Date();
                }
            },
            {
                label: "停用时间：",
                name: "stop_time",
                type: 'datetime',
                def: function () {
                    return new Date();
                }
            }
        ]
    });

    $('button.editor_create').on('click', function (e) {
        e.preventDefault();
        vlan_show(ip_supplier_table);
        a_pop_show(ip_supplier_table);
        ip_supplier_table.create({
            title: '新增供应商',
            buttons: 'Add'
        });
    });


    table_id.on('click', 'tbody td', function (e) {
        let index = $(this).index();
        let head_name = table_id.find("thead").eq(0).find("tr").eq(0).find("th").eq(index).text();
        // 备注
        if (head_name === "备注") {
            editInfo($(this).parent().attr("id"), $(this).parent().find('td').eq(0).text(), $(this).parent().find('td').eq(1).text())
        } else if (head_name === "VLAN") {
            vlan_show(ip_supplier_table);
            ip_supplier_table.bubble(this, {
                submit: 'changed'
            });
        }
        // 最后一列处理 备注
        else if (head_name === "文件管理") {
            fileUpload($(this).parent().attr("id"), $(this).parent().find('td').eq(0).text(), $(this).parent().find('td').eq(1).text())
        }
        // A info
        else if (head_name === "接入点信息") {
            a_pop_show(ip_supplier_table);
            ip_supplier_table.bubble(this, {
                submit: 'changed'
            });
        } else if (head_name !== "供应商名称" && head_name !== "线路编号" && head_name !== "带宽") {
            ip_supplier_table.bubble(this, {
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
        ajax: "/query_ip_supplier_table",
        "order": [[11, 'desc']],
        "columnDefs": [
            {
                // targets用于指定操作的列，从第0列开始，-1为最后一列，这里第六列
                // return后边是我们希望在指定列填入的按钮代码
                "targets": 14,
                "render": function (data, type, full, meta) {
                    return '<a data-toggle="modal" data-target="#memo_editor" class="m-portlet__nav-link btn m-btn m-btn--hover-accent m-btn--icon m-btn--icon-only m-btn--pill" title="Edit details">\
                                    <i class="la la-edit"></i>\
                                </a>';
                }
            },
            {
                // targets用于指定操作的列，从第0列开始，-1为最后一列
                // return后边是我们希望在指定列填入的按钮代码
                "targets": 13,
                "render": function (data, type, full, meta) {
                    return '<a data-toggle="modal" data-target="#file_upload" class="m-portlet__nav-link btn m-btn m-btn--hover-accent m-btn--icon m-btn--icon-only m-btn--pill" title="Edit details">\
                                    <i class="la la-file"></i>\
                                </a>';
                }
            },
            {"visible": false, "targets": []}
        ],
        columns: [
            {data: "supplier_name"},
            {data: "line_code"},
            {
                data: null, render: function (data, type, row) {
                    return data.bandwidth + data.bandwidth_unit;
                },
                editField: ['bandwidth', 'bandwidth_unit']
            },
            {
                data: null, render: function (data, type, row) {
                    if (data.vlan_type === 'access' || data.vlan_type === 'trunk') {
                        return data.vlan + '<br>' + data.vlan_desc;
                    } else if (data.vlan_type === 'qinq') {
                        return data.vlan + '(' + data.qinq_inside + ')' + '<br>' + data.vlan_desc;
                    } else if (data.vlan_type === 'vlan_map') {
                        return data.vlan + '-map->' + data.vlan_map_to + '<br>' + data.vlan_desc;
                    }
                },
                editField: ['vlan_type', 'vlan', 'vlan_map_to', 'qinq_inside', 'vlan_desc']
            },
            {
                data: null, render: function (data, type, row) {
                    if (data.a_pop_ip) {
                        return data.a_pop + '<br>' + data.a_pop_device + '(' + data.a_pop_ip + ')<br>' + data.a_pop_interface;
                    } else {
                        return ""
                    }
                },
                editField: ['search_city_a', 'a_pop_city_id', 'a_pop_id', 'a_pop_device_id', 'a_pop_interface_id'],
            },
            {
                data: null, render: function (data, type, row) {
                    //return "供应商侧：" + data.interconnection_supplier + '<br>' + '我司设备地址: ' + data.interconnection_us + '<br>' + '掩码: ' + data.interconnection_netmask;
                    if (data.mode === 1) {
                        return "网关模式"
                    } else if (data.mode === 2) {
                        return "路由模式"
                    }

                },
                editField: ['mode']
            },
            {
                data: null, render: function (data, type, row) {
                    return "供应商侧：" + data.interconnection_supplier + '<br>' + '我司设备地址: ' + data.interconnection_us + '<br>' + '掩码: ' + data.interconnection_netmask;
                },
                editField: ['interconnection_supplier', 'interconnection_us', 'interconnection_netmask']
            },
            {data: "operator"},
            {
                data: null, render: function (data, type, row) {
                    return '姓名: ' + data.biz_contact_name + '<br>' + '电话: ' + data.biz_contact_phoneNumber + '<br>' + 'Email: ' + data.biz_contact_email;
                },
                editField: ['biz_contact_name', 'biz_contact_phoneNumber', 'biz_contact_email']
            },

            {
                data: null, render: function (data, type, row) {
                    return '姓名: ' + data.noc_contact_name + '<br>' + '电话: ' + data.noc_contact_phoneNumber + '<br>' + 'Email: ' + data.noc_contact_email;
                },
                editField: ['noc_contact_name', 'noc_contact_phoneNumber', 'noc_contact_email']
            },
            {
                data: null, render: function (data, type, row) {
                    return '姓名: ' + data.customer_manager_name + '<br>' + '电话: ' + data.customer_manager_phoneNumber;
                },
                editField: ['customer_manager_name', 'customer_manager_phoneNumber']
            },
            {data: "start_time"},
            {data: "stop_time"},
            {data: null},
            {data: null}
        ],
        select: {
            style: 'os',
            selector: 'td:first-child'
        },
        fixedColumns: {//关键是这里了，需要第一列不滚动就设置1
            leftColumns: 2
        },
        buttons: []
    });

    let ipEditor = new $.fn.dataTable.Editor({
        ajax: {
            url: '/edit_supplier_ip',
            data: function (d) {
                var selected = table.row({selected: true});
                if (selected.any()) {
                    d.site = selected.data().DT_RowId;
                }
            }
        },
        table: '#ip',
        fields: [{
            label: "IP",
            name: "ip"
        }, {
            label: "掩码",
            name: "netmask"
        }, {
            label: "网关",
            name: "gateway"
        }, {
            label: "DNS",
            name: "dns"
        }, {
            label: "可用地址段",
            name: "available_ip"
        }, {
            label: "供应商",
            name: "isp"
        }
        ]
    });

    $('#ip').on('click', 'tbody td', function (e) {
        ipEditor.bubble(this);
    });

    var ipTable = $('#ip').DataTable({
        dom: 'Bfrtip',
        ajax: {
            url: 'query_supplier_ip_table',
            type: 'post',
            data: function (d) {
                let selected = table.row({selected: true});

                if (selected.any()) {
                    d.site = selected.data().DT_RowId;
                }
            }
        },
        columnDefs: [{orderable: false, className: 'select-checkbox', targets: 0, defaultContent: '', data: null}],
        columns: [
            {data: null},
            {
                data: null, render: function (data, type, row) {
                    return data.ip + '/' + data.netmask;
                },
                editField: ['ip', 'netmask']
            },
            {data: 'gateway'},
            {data: 'available_ip'},
            {data: 'dns'},
            {data: 'isp'}
        ],
        select: {
            style: 'os',
            selector: 'td:first-child'
        },
        buttons: [
            {extend: 'create', editor: ipEditor},
            {extend: 'remove', editor: ipEditor}]
    });

    table.on('select', function (e) {

        ipTable.ajax.reload();
        // ipEditor
        //     .field('user.site')
        //     .def(table.row({selected: true}).data().DT_RowId);
    });

    table.on('deselect', function () {
        ipTable.ajax.reload();
    });

    ipEditor.on('submitSuccess', function () {
        table.ajax.reload();
    });

    ip_supplier_table.on('submitSuccess', function () {
        ipTable.ajax.reload();
    });

    let results = new Array(table, ipTable)
    return results
};

$(document).ready(function () {

    DatatableIPSupplier();
    $.extend(true, $.fn.dataTable.Editor.Field.defaults, {
        attr: {
            autocomplete: 'off'
        }
    });
});

function fileUpload(row_id, customer, line_code) {
    $('#row_id2').html(row_id);
    $('#customer2').val(customer);
    $('#line_code2').val(line_code);
    DatatableRemoteAjaxFileList.init();
    $("#file_list").mDatatable().destroy();
    DatatableRemoteAjaxFileList.init();
}

function editInfo(row_id, customer, line_code) {
    console.log(row_id + ' ' + customer + ' ' + line_code)
    let x = document.getElementsByName('postli');
    if (x.length > 0) {
        for (var i = x.length - 1; i >= 0; i--) {
            x[i].parentNode.removeChild(x[i]);
        }
    }

    document.getElementById('flask-pagedown-body').value = '';
    document.getElementById('itemContainer').style.minHeight = "0px";

    $('#row_id').html(row_id);
    $('#customer').val(customer);
    $('#line_code').val(line_code);

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

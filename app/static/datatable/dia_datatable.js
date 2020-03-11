var DatatableDIA = function () {
    let table_id = $("#table_dia");
    let dia_table = new $.fn.dataTable.Editor({
        ajax: "/query_dia_table",
        table: "#table_dia",
        fields: [
            {label: "搜索Z端城市：", name: "search_city",},
            {label: "Z端城市", name: "z_pop_city_id", type: "select"},
            {label: "Z端机房", name: "z_pop_id", type: "select"},
            {label: "Z端设备", name: "z_pop_device_id", type: "select"},
            {label: "Z端设备端口", name: "z_pop_interface_id", type: "select"},
            {label: "Z端设备IP", name: "z_pop_ip"},
            {
                label: "接入模式:",
                name: "mode",
                type: "select"
            },
            {label: "Vlan: ", name: "vlan"},
            {label: "Vlan desc: ", name: "vlan_desc"},
            {
                label: "VLAN类型:",
                name: "vlan_type",
                type: "select",
                options: ["access", "trunk"],
            },
            {label: "客户商务联系人姓名:", name: "biz_contact_name"},
            {label: "客户商务联系人电话:", name: "biz_contact_phoneNumber"},
            {label: "客户商务联系人邮箱:", name: "biz_contact_email"},
            {label: "客户技术姓名:", name: "noc_contact_name"},
            {label: "客户技术电话:", name: "noc_contact_phoneNumber"},
            {label: "客户技术邮箱:", name: "noc_contact_email"},
            {label: "客户经理姓名:", name: "customer_manager_name"},
            {label: "客户经理电话:", name: "customer_manager_phoneNumber"},
            {label: "线路描述：", name: "line_desc"},
            {label: "供应商IP：", name: "interconnection_supplier"},
            {label: "我方IP：", name: "interconnection_us"},
            {label: "掩码：", name: "interconnection_netmask"}
        ]
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
        }
        // vlan
        else if (head_name === "Vlan") {
            dia_table.bubble(this, {
                submit: 'changed'
            });
        }
        // A info
        else if (head_name === "Z端信息") {
            z_pop_show(dia_table);
            dia_table.bubble(this, {
                submit: 'changed'
            });
        } else if (head_name !== "客户名称" && head_name !== "线路名称" && head_name !== "线路内容" && head_name !== "通道" && head_name !== "线路属性") {
            dia_table.bubble(this, {
                submit: 'changed'
            });
        }
    });

    let table = table_id.DataTable({
        dom: "Bfrtip",
        scrollY: '100vh',
        scrollCollapse: true,
        "processing": true,
        "scrollX": true,
        serverSide: true,
        ajax: {
            url: "/dia_table_postquery",
            type: "POST"
        },
        "order": [[11, 'desc']],
        language: mylang,
        "columnDefs": [
            {
                // targets用于指定操作的列，从第0列开始，-1为最后一列，这里第六列
                // return后边是我们希望在指定列填入的按钮代码
                "targets": 15,
                "render": function (data, type, full, meta) {
                    return '<a data-toggle="modal" data-target="#memo_editor" class="m-portlet__nav-link btn m-btn m-btn--hover-accent m-btn--icon m-btn--icon-only m-btn--pill" title="Edit details">\
                                    <i class="la la-edit"></i>\
                                </a>';
                }
            },
            {
                // targets用于指定操作的列，从第0列开始，-1为最后一列
                // return后边是我们希望在指定列填入的按钮代码
                "targets": 14,
                "render": function (data, type, full, meta) {
                    return '<a data-toggle="modal" data-target="#file_upload" class="m-portlet__nav-link btn m-btn m-btn--hover-accent m-btn--icon m-btn--icon-only m-btn--pill" title="Edit details">\
                                    <i class="la la-file"></i>\
                                </a>';
                }
            },
            {"visible": false, "targets": []}
        ],
        columns: [
            {
                data: null, render: function (data, type, row) {
                    var status = {
                        0: {'state': 'danger'},
                        1: {'state': 'success'},
                        2: {'state': 'warning'},
                        3: {'state': 'info'}
                    };
                    return '<span class="m-badge m-badge-' + status[data.validate_rrpp_status].state + ' m-badge--dot"></span>&nbsp;<span class="m--font-bold m--font-' + status[data.validate_rrpp_status].state + '">' + data.customer_name + '</span>';
                }
            },
            {
                data: null, render: function (data, type, row) {
                    // Combine the first and last names into a single table field
                    return data.line_code + '<br>' + data.product_type + '-' + data.product_model;
                }
            },
            {data: "channel"},
            {
                data: null, render: function (data, type, row) {
                    if (data.vlan_type === 'access' || 'trunk') {
                        return data.vlan + '<br>' + data.vlan_desc;
                    }
                },
                editField: ['vlan_type', 'vlan', 'vlan_desc']
            },
            {
                data: null, render: function (data, type, row) {
                    if (data.z_pop_ip) {
                        return data.z_pop + '<br>' + data.z_pop_device + '(' + data.z_pop_ip + ')<br>' + data.z_pop_interface;
                    } else {
                        return ""
                    }
                },
                editField: ['search_city', 'z_pop_city_id', 'z_pop_id', 'z_pop_device_id', 'z_pop_interface_id'],
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
            {data: "start_date"},
            {data: "stop_date"},
            {data: "line_desc"},
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
            url: '/edit_dia_ip',
            data: function (d) {
                var selected = table.row({selected: true});
                if (selected.any()) {
                    let dd = d.data;
                    console.log(dd);
                    for (var k in dd){
                        console.log(k);
                        dd[k]['site'] = selected.data().DT_RowId;
                    }
                }
            }
        },
        table: '#ip',
        fields: [
            {label: "供应商", name: 'supplier_id', type: 'select'},
            {label: "地址段", name: 'ip_address', type: 'select'},
            {label: "IP:", name: "ip"},
            {label: "掩码", name: "netmask"},
            {label: "网关", name: "gateway"},
            {label: "可用地址段", name: "available_ip"},
            {label: "DNS", name: "dns"},
        ]
    });


    $('#ip').on('click', 'tbody td', function (e) {
        let index = $(this).index();
        let head_name = $('#ip').find("thead").eq(0).find("tr").eq(0).find("th").eq(index).text();
        if (head_name !== "操作" && head_name !== "供应商" && head_name !== "IP/掩码" && head_name !== "网关") {
            ipEditor.bubble(this, {
                submit: 'changed'
            });
        }
    });

    $('button.editor_create').on('click', function (e) {
        e.preventDefault();
        find_supplier_ip(ipEditor);
        ipEditor.create({
            title: '新增地址段',
            buttons: 'Add'
        });
    });

    // Delete a record
    $('#ip').on('click', 'a.editor_remove', function (e) {
        e.preventDefault();
        ipEditor.remove($(this).closest('tr'), {
            title: '删除IP地址',
            message: '是否确认删除此记录，删除后不能恢复?',
            buttons: 'Delete'
        });
    });

    let ipTable = $('#ip').DataTable({
        dom: 'Bfrtip',
        language: mylang,
        ajax: {
            url: 'query_ip_table',
            type: 'post',
            data: function (d) {
                let selected = table.row({selected: true});
                console.log(d);
                if (selected.any()) {
                    console.log(selected.data().DT_RowId);
                    d.site = selected.data().DT_RowId;
                }
            }
        },
        columns: [
            {
                data: null, render: function (data, type, row) {
                    return data.ip + '/' + data.netmask;
                },
                editField: ['ip', 'netmask']
            },
            {data: 'gateway'},
            {data: 'available_ip'},
            {data: 'dns'},
            {data: 'supplier', editField:['supplier_id']},
            {
                data: null,
                className: "center",
                defaultContent: '<a href="" class="editor_remove m-portlet__nav-link btn m-btn m-btn--hover-danger m-btn--icon m-btn--icon-only m-btn--pill"><i class="la la-trash"></i></a>'
            }
        ],
        select: true,
        buttons: []
    });

    table.on('select', function (e) {

        ipTable.ajax.reload();
        // ipEditor
        //     .field('site')
        //     .def(table.row({selected: true}).data().DT_RowId);
    });

    table.on('deselect', function () {
        ipTable.ajax.reload();
    });

    ipEditor.on('submitSuccess', function () {
        table.ajax.reload();
    });

    dia_table.on('submitSuccess', function () {
        ipTable.ajax.reload();
    });

    let results = new Array(table, ipTable)
    return results
};

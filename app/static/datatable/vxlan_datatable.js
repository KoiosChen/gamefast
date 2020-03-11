var vxlan_table; // use a global for the submit and return data rendering in the examples

var DatatableVXLAN = function () {
    var table_id = $("#table_vxlan");
    console.log('make vxlan table');
    vxlan_table = new $.fn.dataTable.Editor({
        ajax: "/query_vxlan_table",
        table: "#table_vxlan",
        fields: [
            {label: "搜索A端城市：", name: "search_city",},
            {label: "A端城市", name: "a_pop_city_id", type: "select"},
            {label: "A端机房", name: "a_pop_id", type: "select"},
            {label: "A端设备", name: "a_pop_device_id", type: "select"},
            {label: "A端设备端口", name: "a_pop_interface_id", type: "select"},
            {label: "A端设备IP", name: "a_pop_ip"},
            {label: "Vlan: ", name: "vlan"},
            {label: "Vlan desc: ", name: "vlan_desc"},
            {
                label: "VLAN类型:",
                name: "vlan_type",
                type: "select",
                options: ["access", "trunk", "qinq", "vlan_map"],
            },
            {label: "Vlan mapping to: ", name: "vlan_map_to"},
            {label: "QinQ外层2", name: "qinq_outside2"},
            {label: "QinQ内层", name: "qinq_inside"},
            {label: "客户商务联系人姓名:", name: "biz_contact_name"},
            {label: "客户商务联系人电话:", name: "biz_contact_phoneNumber"},
            {label: "客户商务联系人邮箱:", name: "biz_contact_email"},
            {label: "客户技术姓名:", name: "noc_contact_name"},
            {label: "客户技术电话:", name: "noc_contact_phoneNumber"},
            {label: "客户技术邮箱:", name: "noc_contact_email"},
            {label: "客户经理姓名:", name: "customer_manager_name"},
            {label: "客户经理电话:", name: "customer_manager_phoneNumber"},
            {label: "线路描述：", name: "line_desc"},
            {label: "BD: ", name: "bd"}
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
            vxlan_table.dependent('vlan_type', function (val, data, callback) {
                if (val === 'access' || val === 'trunk') {
                    return {hide: ['vlan_map_to', 'qinq_outside2', 'qinq_inside']}
                } else if (val === 'qinq') {
                    return {
                        show: ['qinq_inside'],
                        hide: ['vlan_map_to', 'qinq_outside2']
                    }
                } else if (val === 'multi_qinq') {
                    return {
                        show: ['qinq_outside2', 'qinq_inside'],
                        hide: ['vlan_map_to']
                    }
                } else if (val === 'vlan_map') {
                    return {
                        show: ['vlan_map_to'],
                        hide: ['qinq_outside2', 'qinq_inside']
                    }
                }
            });
            vxlan_table.bubble(this, {
                submit: 'changed'
            });
        }
        // A info
        else if (head_name === "A端信息") {
            vxlan_table.dependent('search_city', function (val, data, callback) {
                $.ajax({
                    url: '/search_city',
                    data: {
                        "data": val
                    },
                    dataType: 'json',
                    type: 'post',
                    success: function (jsonData) {
                        if (jsonData.status === 'true') {
                            let options = {"options": {"a_pop_city_id": jsonData.content}};
                            callback(options)
                        }
                    }
                });
            });


            vxlan_table.dependent('a_pop_city_id', function (val, data, callback) {
                $.ajax({
                    url: '/get_pop',
                    data: {
                        "data": val
                    },
                    dataType: 'json',
                    type: 'post',
                    success: function (jsonData) {
                        let options = {"options": {"a_pop_id": jsonData}};
                        callback(options)
                    }
                });
            });

            vxlan_table.dependent('a_pop_id', function (val, data, callback) {
                $.ajax({
                    url: '/get_device',
                    data: {
                        "data": val
                    },
                    dataType: 'json',
                    type: 'post',
                    success: function (jsonData) {
                        let options = {"options": {"a_pop_device_id": jsonData}};
                        callback(options)
                    }
                });
            });

            vxlan_table.dependent('a_pop_device_id', function (val, data, callback) {
                $.ajax({
                    url: '/get_interface',
                    data: {
                        "data": val
                    },
                    dataType: 'json',
                    type: 'post',
                    success: function (jsonData) {
                        let options = {"options": {"a_pop_interface_id": jsonData}};
                        callback(options)
                    }
                });
            });
            vxlan_table.bubble(this, {
                submit: 'changed'
            });
        } else if (head_name !== "子编号" && head_name !== "客户名称" && head_name !== "线路名称" && head_name !== "线路内容" && head_name !== "通道" && head_name !== "线路属性") {
            vxlan_table.bubble(this, {
                submit: 'changed'
            });
        }
    });


    table1 = table_id.DataTable({
        dom: "Bfrtip",
        scrollY: '100vh',
        scrollCollapse: true,
        serverSide: true,
        language: mylang,
        "processing": true,
        "scrollX": true,
        ajax: {
            url: "/vxlan_table_postquery",
            type: "POST"
        },
        "order": [[12, 'desc']],
        "columnDefs": [
            {
                // targets用于指定操作的列，从第0列开始，-1为最后一列，这里第六列
                // return后边是我们希望在指定列填入的按钮代码
                "targets": 16,
                "render": function (data, type, full, meta) {
                    return '<a data-toggle="modal" data-target="#memo_editor" class="m-portlet__nav-link btn m-btn m-btn--hover-accent m-btn--icon m-btn--icon-only m-btn--pill" title="Edit details">\
                                    <i class="la la-edit"></i>\
                                </a>';
                }
            },
            {
                // targets用于指定操作的列，从第0列开始，-1为最后一列
                // return后边是我们希望在指定列填入的按钮代码
                "targets": 15,
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
            {data: "sub_line_code"},
            {
                data: null, render: function (data, type, row) {
                    // Combine the first and last names into a single table field
                    if (data.product_model === 'SDWAN' || data.product_model === 'DCA') {
                        return "云供应商：" + data.cloud_provider + '<br>' + "云接入点：" + data.cloud_accesspoint;
                    } else {
                        return '-';
                    }
                },
                editField: ['cloud_provider', 'cloud_accesspoint']
            },
            {data: "channel"},
            {data: "bd"},
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
                editField: ['search_city', 'a_pop_city_id', 'a_pop_id', 'a_pop_device_id', 'a_pop_interface_id'],
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
    return table1
};
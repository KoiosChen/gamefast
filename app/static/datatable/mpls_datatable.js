var DatatableMPLS = function () {
    let table_id = $("#table_mpls");
    let mpls_editor = new $.fn.dataTable.Editor({
        ajax: "/query_mpls_table",
        table: "#table_mpls",
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
            {
                label: "接入方式:",
                name: "access_way",
                type: "select",
                options: ["专线", "Internet"],
            },
            {
                label: "路由协议:",
                name: "route_protocol",
                type: "select",
                options: ["BGP", "静态", "OSPF", "IS-IS"],
            },
            {label: "AS", name: "as_number"},
            {label: "VRF", name: "vrf"},
            {label: "RT", name: "rt"},
            {label: "客户地址", name: "interconnect_client"},
            {label: "掩码", name: "interconnect_netmask"},
            {label: "PE地址", name: "interconnect_pe"},
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
        // A info
        else if (head_name === "A端信息") {
            mpls_editor.dependent('search_city', function (val, data, callback) {
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


            mpls_editor.dependent('a_pop_city_id', function (val, data, callback) {
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

            mpls_editor.dependent('a_pop_id', function (val, data, callback) {
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

            mpls_editor.dependent('a_pop_device_id', function (val, data, callback) {
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
            mpls_editor.bubble(this, {
                submit: 'changed'
            });
        } else if (head_name !== "客户名称" && head_name !== "线路名称" && head_name !== "线路内容" && head_name !== "通道") {
            mpls_editor.bubble(this, {
                submit: 'changed'
            });
        }
    });

    let mpls_table = table_id.DataTable({
        dom: "Bfrtip",
        scrollY: '80vh',
        scrollCollapse: true,
        "processing": true,
        "scrollX": true,
        "order": [[16, 'desc']],
        serverSide: true,
        ajax: {
            url: "/mpls_table_postquery",
            type: "POST"
        },
        language: mylang,
        "columnDefs": [
            {
                // targets用于指定操作的列，从第0列开始，-1为最后一列，这里第六列
                // return后边是我们希望在指定列填入的按钮代码
                "targets": 20,
                "render": function (data, type, full, meta) {
                    return '<a data-toggle="modal" data-target="#memo_editor" class="m-portlet__nav-link btn m-btn m-btn--hover-accent m-btn--icon m-btn--icon-only m-btn--pill" title="Edit details">\
                                    <i class="la la-edit"></i>\
                                </a>';
                }
            },
            {
                // targets用于指定操作的列，从第0列开始，-1为最后一列
                // return后边是我们希望在指定列填入的按钮代码
                "targets": 19,
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
            {data: "channel"},
            {
                data: null, render: function (data, type, row) {
                    if (data.vlan_type === 'access' || data.vlan_type === 'trunk') {
                        return data.vlan + '<br>' + data.vlan_desc;
                    } else {
                        return ""
                    }
                },
                editField: ['vlan_type', 'vlan', 'vlan_desc']
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
            {data: 'access_way'},
            {data: 'route_protocol'},
            {data: 'as_number'},
            {data: 'vrf'},
            {data: 'rt'},
            {
                data: null, render: function (data, type, row) {
                    return '客户地址: ' + data.interconnect_client + '/' + data.interconnect_netmask + '<br>' + 'PE: ' + data.interconnect_pe;
                },
                editField: ['interconnect_client', 'interconnect_netmask', 'interconnect_pe']
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

    let mplsAttributeEditor = new $.fn.dataTable.Editor({
        ajax: {
            url: '/edit_mpls_route',
            data: function (d) {
                let selected = mpls_table.row({selected: true});
                if (selected.any()) {
                    d.site = selected.data().DT_RowId;
                }
            }
        },
        table: '#mpls_attribute',
        fields: [
            {label: "IP: ", name: "route_ip"},
            {label: "NETMASK: ", name: "route_netmask"},
        ]
    });

    // Delete a record
    $('#mpls_attribute').on('click', 'a.editor_remove', function (e) {
        e.preventDefault();
        mplsAttributeEditor.remove($(this).closest('tr'), {
            title: '删除IP地址',
            message: '是否确认删除此记录，删除后不能恢复?',
            buttons: 'Delete'
        });
    });

    $('#mpls_attribute').on('click', 'tbody td', function (e) {
        e.preventDefault();
        let index = $(this).index();
        let head_name = $('#mpls_attribute').find("thead").eq(0).find("tr").eq(0).find("th").eq(index).text();
        if (head_name !== "操作") {
            mplsAttributeEditor.bubble(this, {
                submit: 'changed'
            });
        }
    });

    let mplsAttributeTable = $('#mpls_attribute').DataTable({
        dom: 'Bfrtip',
        ajax: {
            url: '/query_mpls_attribute_table',
            type: 'post',
            data: function (d) {
                let selected = mpls_table.row({selected: true});

                if (selected.any()) {
                    d.site = selected.data().DT_RowId;
                }
            }
        },
        columns: [
            {
                data: null, render: function (data, type, row) {
                    return data.route_ip + '/' + data.route_netmask;
                },
                editField: ['route_ip', 'route_netmask']
            },
            {
                data: null,
                className: "center",
                defaultContent: '<a href="" class="editor_remove m-portlet__nav-link btn m-btn m-btn--hover-danger m-btn--icon m-btn--icon-only m-btn--pill"><i class="la la-trash"></i></a>'
            }
        ],
        select: true,
        buttons: [{extend: 'create', editor: mplsAttributeEditor}]
    });

    mpls_table.on('select', function (e) {

        mplsAttributeTable.ajax.reload();
        // mplsAttributeEditor
        //     .field('user.site')
        //     .def(mpls_table.row({selected: true}).data().DT_RowId);
    });

    mpls_table.on('deselect', function () {
        mplsAttributeTable.ajax.reload();
    });

    mplsAttributeEditor.on('submitSuccess', function () {
        mpls_table.ajax.reload();
    });

    mpls_editor.on('submitSuccess', function () {
        mplsAttributeTable.ajax.reload();
    });

    return new Array(mpls_table, mplsAttributeTable)
};

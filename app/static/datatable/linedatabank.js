var editor; // use a global for the submit and return data rendering in the examples

var DatatableDPLC = function () {
    editor = new $.fn.dataTable.Editor({
        ajax: "/editor_test",
        table: "#example",
        fields: [
            {label: "搜索A端城市：", name: "search_city",},
            {label: "A端城市", name: "a_pop_city_id", type: "select"},
            {label: "A端机房", name: "a_pop_id", type: "select"},
            {label: "A端设备", name: "a_pop_device_id", type: "select"},
            {label: "A端设备端口", name: "a_pop_interface_id", type: "select"},
            {label: "A端设备IP", name: "a_pop_ip"},
            {label: "搜索Z端城市：", name: "search_city_z",},
            {label: "Z端城市", name: "z_pop_city_id", type: "select"},
            {label: "Z端机房", name: "z_pop_id", type: "select"},
            {label: "Z端设备", name: "z_pop_device_id", type: "select"},
            {label: "Z端设备端口", name: "z_pop_interface_id", type: "select"},
            {label: "Z端设备IP", name: "z_pop_ip"},
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
            {label: "保护:", name: "protect", type: "select", options: ["是", "否"]},
            {label: "平台:", name: "platform_id", type: "select"},
            {label: "环:", name: "domains", type: "select"},
            {
                label: "是否有城网:",
                name: "man",
                type: "radio",
                options: [
                    {label: "无城网", value: 0},
                    {label: "有城网", value: 1}
                ],
                def: 0
            },
            {label: "A侧(单链/畸形）: ", name: "a_chain", type: "radio"},
            {label: "主路由:", name: "main_route", type: "radio"},
            {label: "Z侧(单链/畸形）： ", name: 'z_chain', type: "radio"},
            {label: "客户商务联系人姓名:", name: "biz_contact_name"},
            {label: "客户商务联系人电话:", name: "biz_contact_phoneNumber"},
            {label: "客户商务联系人邮箱:", name: "biz_contact_email"},
            {label: "客户技术姓名:", name: "noc_contact_name"},
            {label: "客户技术电话:", name: "noc_contact_phoneNumber"},
            {label: "客户技术邮箱:", name: "noc_contact_email"},
            {label: "客户经理姓名:", name: "customer_manager_name"},
            {label: "客户经理电话:", name: "customer_manager_phoneNumber"},
            {label: "云供应商：", name: "cloud_provider"},
            {label: "云接入点：", name: "cloud_accesspoint"},
            {label: "线路描述：", name: "line_desc"},
        ]
    });

    $('#example').on('click', 'tbody td', function (e) {
        let index = $(this).index();
        let product_model = $(this).parent().find('td').eq(1).text().search('DCA|SDWAN');
        let head_name = $('#example').find("thead").eq(0).find("tr").eq(0).find("th").eq(index).text()
        // 路由
        if (head_name === "主用路由") {
            let a_z_chain = [];
            let a_chain = [];
            let z_chain = [];
            $.ajax({
                url: '/get_route',
                async: false,
                data: {
                    "data": $(this).parent().attr("id")
                },
                dataType: 'json',
                type: 'post',
                success: function (jsonData) {
                    if (jsonData.status === "true") {
                        let a_z_option = {};
                        let a_option = {};
                        let z_option = {};
                        let routes = jsonData.content;
                        if (routes.a_chain_routes) {
                            $.each(routes.a_chain_routes, function (i, e) {
                                a_option.label = e;
                                a_option.value = e;
                                a_chain.push(a_option);
                                a_option = {};
                            })
                        }

                        if (routes.z_chain_routes) {
                            $.each(routes.z_chain_routes, function (i, e) {
                                z_option.label = e;
                                z_option.value = e;
                                z_chain.push(z_option);
                                z_option = {};
                            })
                        }
                        if (routes.a_z_routes) {
                            $.each(routes.a_z_routes, function (i, e) {
                                a_z_option.label = e;
                                a_z_option.value = e;
                                a_z_chain.push(a_z_option);
                                a_z_option = {};
                            })
                        }
                    }
                }
            }).done(function () {
                if (a_z_chain) {
                    editor.field('main_route').update(a_z_chain);
                }
                if (a_chain.length >= 1) {
                    editor.field('a_chain').show();
                    editor.field('a_chain').update(a_chain);
                }
                if (z_chain.length >= 1) {
                    editor.field('a_chain').show();
                    editor.field('z_chain').update(z_chain);
                }
                if (a_chain.length < 1) {

                    editor.field('a_chain').hide();
                }
                if (z_chain.length < 1) {
                    editor.field('z_chain').hide();
                }
            });
            if (editor.field('main_route').get()) {
                editor.bubble(this, {
                    submit: 'changed'
                });
            } else {
                alert("计算路由失败")
            }

        }
        // 最后一列处理 备注
        else if (head_name === "备注") {
            editInfo($(this).parent().attr("id"), $(this).parent().find('td').eq(0).text(), $(this).parent().find('td').eq(1).text())
        }
        // 最后一列处理 备注
        else if (head_name === "文件管理") {
            fileUpload($(this).parent().attr("id"), $(this).parent().find('td').eq(0).text(), $(this).parent().find('td').eq(1).text())
        }
        // vlan
        else if (head_name === "Vlan") {
            editor.dependent('vlan_type', function (val, data, callback) {
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
            editor.bubble(this, {
                submit: 'changed'
            });
        }
        // vlan
        else if (head_name === "平台") {
            editor.dependent('man', function (val, data, callback) {
                if (val === 1) {
                    alert('have')
                } else if (val === 0) {
                    alert('no')
                }
            });
            editor.bubble(this, {
                submit: 'changed'
            });
        }
        // A info
        else if (head_name === "A端信息") {
            editor.dependent('search_city', function (val, data, callback) {
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

            editor.dependent('search_city_z', function (val, data, callback) {
                $.ajax({
                    url: '/search_city',
                    data: {
                        "data": val
                    },
                    dataType: 'json',
                    type: 'post',
                    success: function (jsonData) {
                        if (jsonData.status === 'true') {
                            let options = {"options": {"z_pop_city_id": jsonData.content}};
                            callback(options)
                        }

                    }
                });
            });


            editor.dependent('a_pop_city_id', function (val, data, callback) {
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

            editor.dependent('a_pop_id', function (val, data, callback) {
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

            editor.dependent('a_pop_device_id', function (val, data, callback) {
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
            editor.bubble(this, {
                submit: 'changed'
            });
        }
        // Z info
        else if (head_name === "Z端信息") {
            editor.dependent('z_pop_city_id', function (val, data, callback) {
                $.ajax({
                    url: '/get_pop',
                    data: {
                        "data": val
                    },
                    dataType: 'json',
                    type: 'post',
                    success: function (jsonData) {
                        let options = {"options": {"z_pop_id": jsonData}};
                        callback(options)
                    }
                });
            });

            editor.dependent('z_pop_id', function (val, data, callback) {
                $.ajax({
                    url: '/get_device',
                    data: {
                        "data": val
                    },
                    dataType: 'json',
                    type: 'post',
                    success: function (jsonData) {
                        let options = {"options": {"z_pop_device_id": jsonData}};
                        callback(options)
                    }
                });
            });

            editor.dependent('z_pop_device_id', function (val, data, callback) {
                $.ajax({
                    url: '/get_interface',
                    data: {
                        "data": val
                    },
                    dataType: 'json',
                    type: 'post',
                    success: function (jsonData) {
                        let options = {"options": {"z_pop_interface_id": jsonData}};
                        callback(options)
                    }
                });
            });
            editor.bubble(this, {
                submit: 'changed'
            });
        }
        // platform and domain
        else if (head_name === "平台") {
            editor.dependent('platform_id', function (val, data, callback) {
                $.ajax({
                    url: '/get_domain',
                    data: {
                        "data": val
                    },
                    dataType: 'json',
                    type: 'post',
                    success: function (jsonData) {
                        let options = {"options": {"domains": jsonData}};
                        callback(options)
                    }
                });
            });
            editor.bubble(this, {
                submit: 'changed'
            });
        }
        // all others
        else if (head_name !== "客户名称" && head_name !== "线路名称" && head_name !== "线路内容" && head_name !== "通道" && head_name !== "线路属性") {
            editor.bubble(this, {
                submit: 'changed'
            });
        } else if (head_name === '线路属性' && product_model > 0) {
            editor.bubble(this, {
                submit: 'changed'
            });
        }

    });


    table = $('#example').DataTable({
        dom: "Bfrtip",
        scrollY: '100vh',
        scrollCollapse: true,
        // paging: false,
        serverSide: true,
        language: mylang,
        destroy: true,
        "processing": true,
        ajax: {
            url: "/line_data_table_postquery",
            type: "POST"
        },
        "scrollX": true,
        "order": [[15, 'desc']],
        "columnDefs": [
            {
                // targets用于指定操作的列，从第0列开始，-1为最后一列，这里第六列
                // return后边是我们希望在指定列填入的按钮代码
                "targets": 19,
                "render": function (data, type, full, meta) {
                    return '<a data-toggle="modal" data-target="#memo_editor" class="m-portlet__nav-link btn m-btn m-btn--hover-accent m-btn--icon m-btn--icon-only m-btn--pill" title="Edit details">\
                                    <i class="la la-edit"></i>\
                                </a>';
                }
            },
            {
                // targets用于指定操作的列，从第0列开始，-1为最后一列
                // return后边是我们希望在指定列填入的按钮代码
                "targets": -1,
                "render": function (data, type, full, meta) {
                    return '<a data-toggle="modal" data-target="#file_upload" class="m-portlet__nav-link btn m-btn m-btn--hover-accent m-btn--icon m-btn--icon-only m-btn--pill" title="Edit details">\
                                    <i class="la la-file"></i>\
                                </a>';
                }
            },
            {"visible": false, "targets": [3, 10, 16]}
        ],
        columns: [
            {
                data: null, render: function (data, type, row) {
                    var status = {
                        0: {'state': 'danger'},
                        1: {'state': 'success'},
                        2: {'state': 'warning'}
                    };
                    return '<span class="m-badge m-badge--' + status[data.validate_rrpp_status].state + ' m-badge--dot"></span>&nbsp;<span class="m--font-bold m--font-' + status[data.validate_rrpp_status].state + '">' + data.customer_name + '</span>';
                }
            },
            {
                data: null, render: function (data, type, row) {
                    // Combine the first and last names into a single table field
                    return data.line_code + '<br>' + data.product_type + '-' + data.product_model;
                }
            },

            {
                data: null, render: function (data, type, row) {
                    // Combine the first and last names into a single table field
                    return data.a_client_addr + '--><br>-->' + data.z_client_addr;
                }
            }, {
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
            {data: "protect"},
            {
                data: null, render: function (data, type, row) {
                    return '平台: ' + data.platform + '<br>' + '环: ' + data.domains_bind;
                },
                editField: ['platform_id', 'domains', 'man']
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
            {
                data: null, render: function (data, type, row) {
                    if (data.z_pop_ip) {
                        return data.z_pop + '<br>' + data.z_pop_device + '(' + data.z_pop_ip + ')<br>' + data.z_pop_interface;
                    } else {
                        return ""
                    }

                },
                editField: ['search_city_z', 'z_pop_city_id', 'z_pop_id', 'z_pop_device_id', 'z_pop_interface_id']
            },
            {
                data: null, render: function (data, type, row) {
                    return data.a_chain + '<br>' + data.main_route + "<br>" + data.z_chain;
                },
                editField: ['a_chain', 'main_route', 'z_chain']
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

    $('a.toggle-vis').on('click', function (e) {
        e.preventDefault();

        // Get the column API object
        var column = table.column($(this).attr('data-column'));

        // Toggle the visibility
        column.visible(!column.visible());
    });

    return table
};

$(document).ready(function () {
    var dplc_table = DatatableDPLC();
    var vxlan_table = DatatableVXLAN();
    var dia_ip = DatatableDIA();
    var dia_table = dia_ip[0];
    var ip_table = dia_ip[1];
    var the_mpls = DatatableMPLS();
    var mpls_table = the_mpls[0];
    var mpls_attribute_table = the_mpls[1];


    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        let sf = $("#search_field");
        let n = ($(this).attr('href'));
        if (n === "#m_vxlan") {
            console.log('m_vxlan');
            vxlan_table.draw(false);
            $("#search_field option[value='DIA']").remove();
            $("#search_field option[value='MPLS']").remove();
            sf.append("<option value='VXLAN'> VXLAN </option>");
            sf.selectpicker('refresh');
        } else if (n === "#m_line_data") {
            console.log('m_line_data');
            dplc_table.draw(false);
            $("#search_field option[value='VXLAN']").remove();
            $("#search_field option[value='DIA']").remove();
            $("#search_field option[value='MPLS']").remove();
            sf.selectpicker('refresh');
        } else if (n === "#m_dia") {
            console.log('m_dia');
            dia_table.draw(false);
            ip_table.draw(false);
            $("#search_field option[value='VXLAN']").remove();
            $("#search_field option[value='MPLS']").remove();
            sf.append("<option value='DIA'> DIA </option>");
            sf.selectpicker('refresh');
        } else if (n === "#m_mpls") {
            console.log('m_mpls');
            mpls_table.draw(false);
            mpls_attribute_table.draw(false);
            $("#search_field option[value='VXLAN']").remove();
            $("#search_field option[value='DIA']").remove();
            sf.append("<option value='MPLS'> MPLS </option>");
            sf.selectpicker('refresh');
        }

    });

    $("#search_submit").click(function () {
        let search_field = $('#search_field').val();
        console.log(search_field);
        let search_content = $('#search_content').val();
        let search_field_date = $('#search_field_date').val();
        let search_date_range = $('#search_m_daterange .form-control').val();
        let myajax = {
            'search_field': JSON.stringify(search_field),
            'search_content': search_content,
            'search_field_date': search_field_date,
            'search_date_range': search_date_range
        };
        dplc_table.settings()[0].ajax.data = myajax;
        dplc_table.ajax.reload();

        vxlan_table.settings()[0].ajax.data = myajax;
        vxlan_table.ajax.reload();

        dia_table.settings()[0].ajax.data = myajax;
        dia_table.ajax.reload();
        ip_table.clear();
        ip_table.draw();

        mpls_table.settings()[0].ajax.data = myajax;
        mpls_table.ajax.reload();
        mpls_attribute_table.clear();
        mpls_attribute_table.draw();
    });

    $('#search_m_daterange').on('cancel.daterangepicker', function (ev, picker) {
        //do something, like clearing an input
        $('input[name="search_daterange"]').val('');
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
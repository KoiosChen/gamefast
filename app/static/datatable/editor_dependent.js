var search_city = function (editor) {
    editor.dependent('search_city_a', function (val, data, callback) {
        if (val) {
            $.ajax({
                url: '/search_city',
                async: false,
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
        }

    });
}


var a_pop_show = function (editor) {
    editor.dependent('search_city_a', function (val, data, callback) {
        if (val) {
            $.ajax({
                url: '/search_city',
                async: false,
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
        }
    });


    editor.dependent('a_pop_city_id', function (val, data, callback) {
        $.ajax({
            url: '/get_pop',
            async: false,
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
            async: false,
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
            async: false,
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
};


var z_pop_show = function (editor) {
    editor.dependent('search_city_z', function (val, data, callback) {
        if (val) {
            $.ajax({
                url: '/search_city',
                async: false,
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
        }
    });


    editor.dependent('z_pop_city_id', function (val, data, callback) {
        $.ajax({
            url: '/get_pop',
            async: false,
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
            async: false,
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
            async: false,
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
};


var vlan_show = function (editor) {
    editor.dependent('vlan_type', function (val, data, callback) {
        console.log(val);
        if (val === 'access' || val === 'trunk') {
            return {hide: ['vlan_map_to', 'qinq_inside']}
        } else if (val === 'qinq') {
            return {
                show: ['qinq_inside'],
                hide: ['vlan_map_to']
            }
        } else if (val === 'multi_qinq') {
            return {
                show: ['qinq_inside'],
                hide: ['vlan_map_to']
            }
        } else if (val === 'vlan_map') {
            return {
                show: ['vlan_map_to'],
                hide: ['qinq_inside']
            }
        }
    });
};

var find_supplier_ip = function (editor) {
    editor.dependent('supplier_id', function (val, data, callback) {
        $.ajax({
            url: '/find_supplier_ip',
            async: false,
            data: {
                "data": val
            },
            dataType: 'json',
            type: 'post',
            success: function (jsonData) {
                if (jsonData.status === 'true') {
                    let options = {"options": {"ip_address": jsonData.content}};
                    callback(options)
                }
            }
        });
    });
}
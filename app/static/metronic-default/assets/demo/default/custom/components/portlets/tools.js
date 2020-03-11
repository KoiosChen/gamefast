var PortletTools = function () {
    //== Toastr
    var initToastr = function() {
        toastr.options.showDuration = 1000;
    }

    //== Demo 1
    var demo1 = function() {
        // This portlet is lazy initialized using data-portlet="true" attribute. You can access to the portlet object as shown below and override its behavior
        var portlet = $('#m_portlet_tools_1').mPortlet();

        //== Toggle event handlers
        portlet.on('beforeCollapse', function(portlet) {
            setTimeout(function() {
                toastr.info('Before collapse event fired!');
            }, 100);
        });

        portlet.on('afterCollapse', function(portlet) {
            setTimeout(function() {
                toastr.warning('Before collapse event fired!');
            }, 2000);            
        });

        portlet.on('beforeExpand', function(portlet) {
            setTimeout(function() {
                toastr.info('Before expand event fired!');
            }, 100);  
        });

        portlet.on('afterExpand', function(portlet) {
            setTimeout(function() {
                toastr.warning('After expand event fired!');
            }, 2000);
        });

        //== Remove event handlers
        portlet.on('beforeRemove', function(portlet) {
            toastr.info('Before remove event fired!');

            return confirm('Are you sure to remove this portlet ?');  // remove portlet after user confirmation
        });

        portlet.on('afterRemove', function(portlet) {
            setTimeout(function() {
                toastr.warning('After remove event fired!');
            }, 2000);            
        });

        //== Reload event handlers
        portlet.on('reload', function(portlet) {
            toastr.info('Leload event fired!');

            mApp.block(portlet.getSelf(), {
                overlayColor: '#ffffff',
                type: 'loader',
                state: 'accent',
                opacity: 0.3,
                size: 'lg'
            });

            // update the content here

            setTimeout(function() {
                mApp.unblock(portlet.getSelf());
            }, 2000);
        });

        //== Reload event handlers
        portlet.on('afterFullscreenOn', function(portlet) {
            //toastr.info('After fullscreen on event fired!');

            var scrollable = portlet.getBody().find('> .m-scrollable');

            scrollable.data('original-height', scrollable.data('max-height'));
            scrollable.css('height', '100%');
            scrollable.css('max-height', '100%');
            mApp.initScroller(scrollable, {});
        });

        portlet.on('afterFullscreenOff', function(portlet) {
            var scrollable = portlet.getBody().find('> .m-scrollable');

            scrollable.css('height', scrollable.data('original-height'));
            scrollable.data('max-height', scrollable.data('original-height')); 
            mApp.initScroller(scrollable, {});
        });
    }
    return {
        //main function to initiate the module
        init: function () {
            initToastr();

            // init demos
            demo1();
        }
    };
}();

jQuery(document).ready(function() {
    PortletTools.init();
});
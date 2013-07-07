/**
 * MySlice ResourcesSelected plugin
 * Version: 0.1.0
 * URL: http://www.myslice.info
 * Description: display of selected resources
 * Requires: 
 * Author: The MySlice Team
 * Copyright: Copyright 2012 UPMC Sorbonne Universités
 * License: GPLv3
 */

/*
 * It's a best practice to pass jQuery to an IIFE (Immediately Invoked Function
 * Expression) that maps it to the dollar sign so it can't be overwritten by
 * another library in the scope of its execution.
 */
(function( $ ){

    // Routing calls
    jQuery.fn.ResourcesSelected = function( method ) {
        if ( methods[method] ) {
            return methods[ method ].apply( this, Array.prototype.slice.call( arguments, 1 ));
        } else if ( typeof method === 'object' || ! method ) {
            return methods.init.apply( this, arguments );
        } else {
            jQuery.error( 'Method ' +  method + ' does not exist on jQuery.ResourcesSelected' );
        }    

    };

    /***************************************************************************
     * Public methods
     ***************************************************************************/

    var methods = {

        /**
         * @brief Plugin initialization
         * @param options : an associative array of setting values
         * @return : a jQuery collection of objects on which the plugin is
         *     applied, which allows to maintain chainability of calls
         */
        init : function( options ) {

            return this.each(function(){

                var $this = $(this);

                /* An object that will hold private variables and methods */
                var s = new ResourcesSelected(options);
                $(this).data('ResourcesSelected', s);
                var RESULTS_RESOURCES = '/results/' + options.resource_query_uuid + '/changed';
                var UPDATE_RESOURCES  = '/update-set/' + options.resource_query_uuid;
                                 
                $.subscribe(RESULTS_RESOURCES, function(e, resources) { s.set_resources(resources);    });
                $.subscribe(UPDATE_RESOURCES,  function(e, resources, change) { s.update_resources(resources, change); });
                
            }); // this.each
        }, // init

        /**
         * @brief Plugin destruction
         * @return : a jQuery collection of objects on which the plugin is
         *     applied, which allows to maintain chainability of calls
         */
        destroy : function( ) {

            return this.each(function(){
                var $this = jQuery(this), data = $this.data('ResourcesSelected');
                jQuery(window).unbind('ResourcesSelected');
                data.ResourcesSelected.remove();
                $this.removeData('ResourcesSelected');
            })

        }, // destroy

    }; // var methods

    /***************************************************************************
     * ResourcesSelected object
     ***************************************************************************/

    function ResourcesSelected(options)
    {
        /* member variables */

        this.options = options;

        /* The resources that are in the slice */
        this.current_resources = null;

        /* The resources that are in the slice before any edit */
        this.initial_resources = null;

        var rs = this;

        /* constructor */
	    // ioi: resources table id
        var TABLE_NAME = '#table-' + options.plugin_uuid;
        this.table = $(TABLE_NAME).dataTable({
            //sPaginationType: 'full_numbers',  // Use pagination
            sPaginationType: 'bootstrap',
            //bJQueryUI: true,
            //bRetrieve: true,
            sScrollX: '100%',                 // Horizontal scrolling 
            bSortClasses: false,              // Disable style for the sorted column
            aaSorting: [[ 1, "asc" ]],        // Default sorting on URN
            fnDrawCallback: function() {      // Reassociate close click every time the table is redrawn
                /* Prevent to loop on click while redrawing table  */
                jQuery('.ResourceSelectedClose').unbind('click');
                /* Handle clicks on close span */
                /* Reassociate close click every time the table is redrawn */
                $('.ResourceSelectedClose').bind('click',{instance: rs}, close_click);
            }
         });

        /* methods */

        this.set_resources = function(resources)
        {
            console.log("set_resources");
            /* Some sanity checks on the API results */
            if(resources.length==0){
                this.table.html(errorDisplay("No Result"));   
                return;
            }

            if (typeof(resources[0].error) != 'undefined') {
                this.table.html(errorDisplay(resources[0].error));
                return;
            }

            /* Update the table with resources in the slice */
            //var slivers = $.grep(resources, function(i) {return typeof(i['sliver']) != 'undefined';})
            var slivers = resources;
            var sliver_urns = Array();
            // ioi : refubrished
	        $.each(resources, function(i, x) { sliver_urns.push({urn:x.urn, timeslot:"0"}); }); // ioi

            this.initial_resources = sliver_urns; // We make a copy of the object // ioi
	        // ioi
	    
            if (this.current_resources == null) {
                this.current_resources = sliver_urns;

                /* We simply add to the ResourceSelected table */
                var newlines=Array();
                $.each(sliver_urns, function(index, elt) {
                    newlines.push(Array('attached', elt.urn, elt.timeslot, "<span class='ui-icon ui-icon-close ResourceSelectedClose' id='"+elt.urn+"'/>")); // ioi: added last element
                });
                this.table.dataTable().fnAddData(newlines);
            } else {
                alert('Slice updated. Refresh not yet implemented!');
            }
        }

        this.update_resources = function(resources, change) {
            console.log("update_resources");
            var my_oTable = this.table.dataTable();
            var prev_resources = this.current_resources; 
            /*      \ this.initial_resources
             *           \
             * this.          \
             * current_resources  \    YES    |   NO
             * --------------------+----------+---------
             *       YES           | attached | added
             *       NO            | removed  |   /
             */

            /*
             * The first time the query is advertised, don't do anything.  The
             * component will learn nodes in the slice through the manifest
             * received through the other subscription 
             */
             if (!change)
                return;
             // ioi: Refubrished
             var initial = this.initial_resources;
             //var r_removed  = []; //
             /*-----------------------------------------------------------------------
                TODO: remove this dirty hack !!!
             */
             resources = jQuery.map(resources, function(x){
                if(!('timeslot' in x)){x.timeslot=0;}
                return x;
             });
             /*
                TODO: handle generic keys instead of specific stuff
                      ex: urn
                          urn-lease
             */
             var initial_urn = $.map(initial, function(x){return x.urn;});
             var resources_urn = $.map(resources, function(x){return x.urn;});
             var r_removed = $.grep(initial, function (x) { return $.inArray(x.urn, resources_urn) == -1 });
             var r_attached = $.grep(initial, function (x) { return $.inArray(x.urn, resources_urn) > -1 });
             var r_added = $.grep(resources, function (x) { return $.inArray(x.urn, initial_urn) == -1 });
             exists = false; // ioi
             /*-----------------------------------------------------------------------*/

             my_oTable.fnClearTable();
             /*
                TODO: factorization of this code !!!
             */
             $.each(r_added, function(i, r) { 
                //var type = (typeof initial == 'undefined' || r.node != initial.node) ? 'add' : 'attached';
                var type = 'add';  
                // Create the resource objects
                // ioi: refubrished
                var urn = r.urn;
                time = r.timeslot;
                              
                var SPAN = "<span class='ui-icon ui-icon-close ResourceSelectedClose' id='"+urn+"'/>";
                var slot = "<span id='resource_"+urn+"'>" + time + "</span>"; //ioi
                // ioi
                var newline=Array();
                newline.push(type, urn, slot, SPAN); // ioi
                var line = my_oTable.fnAddData(newline);
                var nTr = my_oTable.fnSettings().aoData[ line[0] ].nTr;
                nTr.className = type;
             });
             $.each(r_attached, function(i, r) {  
                //var type = (typeof initial == 'undefined' || r.node != initial.node) ? 'add' : 'attached';
                var type = 'attached';
                // Create the resource objects
                // ioi: refubrished
                var node = r.urn;
                time = r.timeslot;

                var SPAN = "<span class='ui-icon ui-icon-close ResourceSelectedClose' id='"+node+"'/>";
                var slot = "<span id='resource_"+node+"'>" + time + "</span>"; //ioi
                // ioi
                var newline=Array();
                newline.push(type, node, slot, SPAN); // ioi
                var line = my_oTable.fnAddData(newline);
                var nTr = my_oTable.fnSettings().aoData[ line[0] ].nTr;
                nTr.className = type;
             });
             $.each(r_removed, function(i, r) { 
                // The list contains objects
                // ioi: refubrished
                var node = r.urn;
                var time = r.timeslot;
                    
                var SPAN = "<span class='ui-icon ui-icon-close ResourceSelectedClose' id='"+node+"'/>";
                var slot = "<span id='resource_"+node+"'>" + time + "</span>";
                // ioi
                var newline=Array();
                newline.push('remove', node, slot, SPAN); // ioi
                var line = my_oTable.fnAddData(newline);
                var nTr = my_oTable.fnSettings().aoData[ line[0] ].nTr;
                nTr.className = 'remove';
             });

             this.current_resources = $.merge(r_attached,r_added);

             /* Allow the user to update the slice */
             //jQuery('#updateslice-' + data.ResourceSelected.plugin_uuid).prop('disabled', false);

        } // update_resources

    } // ResourcesSelected


    /***************************************************************************
     * Private methods
     ***************************************************************************/

    /* Callbacks */    
    function close_click(event){
        //jQuery.publish('selected', 'add/'+key_value);
        // this.parentNode is <td> this.parentNode.parentNode is <tr> 
        // this.parentNode.parentNode.firstChild is the first cell <td> of this line <tr>
        // this.parentNode.parentNode.firstChild.firstChild is the text in that cell
        //var firstCellVal=this.parentNode.parentNode.firstChild.firstChild.data;
        var remove_urn = this.id; 
        var current_resources = event.data.instance.current_resources;
        var list_resources = $.grep(current_resources, function(x) {return x.urn != remove_urn});
        //jQuery.publish('selected', 'cancel/'+this.id+'/'+get_value(firstCellVal));
        $.publish('/update-set/' + event.data.instance.options.resource_query_uuid, [list_resources, true]);
    }

})(jQuery);

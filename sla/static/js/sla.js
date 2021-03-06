/**
 * MyPlugin:    demonstration plugin
 * Version:     0.1
 * Description: Template for writing new plugins and illustrating the different
 *              possibilities of the plugin API.
 *              This file is part of the Manifold project 
 * Requires:    js/plugin.js
 * URL:         http://www.myslice.info
 * Author:      Jordan Augé <jordan.auge@lip6.fr>
 * Copyright:   Copyright 2012-2013 UPMC Sorbonne Universités
 * License:     GPLv3
 */

(function($){

    var MyPlugin = Plugin.extend({

        /** XXX to check
         * @brief Plugin constructor
         * @param options : an associative array of setting values
         * @param element : 
         * @return : a jQuery collection of objects on which the plugin is
         *     applied, which allows to maintain chainability of calls
         */
        init: function(options, element) {
	    // for debugging tools
	    this.classname="myplugin";
            // Call the parent constructor, see FAQ when forgotten
            this._super(options, element);

            /* Member variables */

            /* Plugin events */

            /* Setup query and record handlers */

            // Explain this will allow query events to be handled
            // What happens when we don't define some events ?
            // Some can be less efficient
            this.listen_query(options.query_uuid);
            this.listen_query(options.query_uuid, 'all');

            /* GUI setup and event binding */
            // call function

        },

        /* PLUGIN EVENTS */
        // on_show like in querytable


        /* GUI EVENTS */

        // a function to bind events here: click change
        // how to raise manifold events


        /* GUI MANIPULATION */

        // We advise you to write function to change behaviour of the GUI
        // Will use naming helpers to access content _inside_ the plugin
        // always refer to these functions in the remaining of the code



         this.id('showEvaluations').click(function() {
         alert("WARNING! The experiments are still running.
             These SLA evaluations could be different at the end of the experiments."  );
            $(".status").css("display","");
         });
         });

        show_hide_button: function() 
        {
            // this.id, this.el, this.cl, this.elts
            // same output as a jquery selector with some guarantees
        },

        /* TEMPLATES */

        // see in the html template
        // How to load a template, use of mustache

        /* QUERY HANDLERS */

        // How to make sure the plugin is not desynchronized
        // He should manifest its interest in filters, fields or records
        // functions triggered only if the proper listen is done

        // no prefix

        on_filter_added: function(filter)
        {

        },

        // ... be sure to list all events here

        /* RECORD HANDLERS */
        on_all_new_record: function(record)
        {
            //
        },

        /* INTERNAL FUNCTIONS */
        _dummy: function() {
            // only convention, not strictly enforced at the moment
        },

    });

    /* Plugin registration */
    $.plugin('MyPlugin', MyPlugin);

    // TODO Here use cases for instanciating plugins in different ways like in the pastie.

})(jQuery);


$(document).ready(function() {
    $(".status-success").addClass("icon-ok-sign").attr("title", "Fulfilled")
    $(".status-error").addClass("icon-remove-sign").attr("title", "Violated")
    $(".status-non-determined").addClass("icon-exclamation-sign").attr("title", "Non determined")

    $(".icon-plus, .icon-minus").click(function(){ $(this).toggleClass("icon-plus icon-minus")});
    console.log("ready")
});

$(".agreement_detail").click(function (ev) { // for each edit contact url
    ev.preventDefault(); // prevent navigation
    var url = $(this).data("form"); // get the contact form url
    $("#sla-modal-agreements-{{ a.agreement_id }}").load(url, function () { // load the url into the modal
        $(this).modal('show'); // display the modal on url load
    });
    return false; // prevent the click propagation
});

$('.agreement-detail').live('submit', function () {
    $.ajax({
        type: $(this).attr('method'),
        url: this.action,
        data: $(this).serialize(),
        context: this,
        success: function (data, status) {
            $('#sla-modal-agreements-{{ a.agreement_id }}').html(data);
        }
    });
    return false;
});

$(document).ready(function() {
    console.log("consumer_agreements ready");
});

$(".violation-detail").click(function(ev) { // for each edit contact url
    ev.preventDefault(); // prevent navigation
    var url = $(this).data("href");
    $("#violation-modal").load(url, function() { // load the url into the modal
        $(this).modal('show'); // display the modal on url load
    });
    return false; // prevent the click propagation
});


 this.elts('showEvaluations').click(function(){displayDate()};



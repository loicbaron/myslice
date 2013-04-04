//
// storing toggle's status in localStorage
// NOTE that localStorage only stores strings, so true becomes "true"
var plugin = {

    debug:false,

    ////////// use local storage to remember open/closed toggles
    store_status : function (domid,status) {
	var key='toggle.'+domid;
	if (plugin.debug) console.log("storing toggle status " + status + " for " + domid + " key=" + key);
	$.localStorage.setItem(key,status);
    },
    // restore last status
    retrieve_last_status : function (domid) {
	var key='toggle.'+domid;
	// don't do anything if nothing stored
	var retrieved=$.localStorage.getItem(key);
	// set default to true
	if (retrieved==null) retrieved="true";
	if (plugin.debug) console.log ("retrieved toggle status for " + domid + " (key=" + key + ") -> " + retrieved);
	return retrieved;
    },
    set_toggle_status : function (domid,status) {
	var plugindiv=$('#'+domid);
	var showbtn=$('#show-'+domid);
	var hidebtn=$('#hide-'+domid);
	if (status=="true")	{ plugindiv.slideDown(); hidebtn.show(); showbtn.hide(); }
	else			{ plugindiv.slideUp();   hidebtn.hide(); showbtn.show(); }
	plugin.store_status(domid,status);
    },
    set_from_saved_status : function (domid) {
	var previous_status=plugin.retrieve_last_status (domid);
	if (plugin.debug) console.log("restoring initial status for domid " + domid + " -> " + previous_status);
	plugin.set_toggle_status (domid,previous_status);
    },
    // triggered upon $(document).ready
    init_all_plugins : function() {
	// plugins marked as persistent start with all 3 parts turned off
	// let us first make sure the right parts are turned on 
	$('.persistent-toggle').each(function() {
	    var domid=this.id.replace('complete-','');
	    plugin.set_from_saved_status(domid);
	});
	// program the hide buttons so they do the right thing
	$('.plugin-hide').each(function() {
	    $(this).click(function () { 
		var domid=this.id.replace('hide-','');
		plugin.set_toggle_status(domid,"false");
	    })});
	// same for show buttons
	$('.plugin-show').each(function() {
	    $(this).click(function () { 
		var domid=this.id.replace('show-','');
		plugin.set_toggle_status(domid,"true");
	    })});
	// arm tooltips
	$('.plugin-tooltip').each(function(){ $(this).tooltip({'selector':'','placement':'right'}); });
    },
} // global var plugin

/* upon document completion, we locate all the hide and show areas, 
 * and configure their behaviour 
 */
$(document).ready(plugin.init_all_plugins)


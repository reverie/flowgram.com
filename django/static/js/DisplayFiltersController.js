/**
 * @author Chris Yap
 * 	Flowgram Display Filters Controller
 */

var DisplayFiltersController = Class.create();

Object.extend(DisplayFiltersController.prototype, {

	initialize: function() {
		initialize("modified", "all", location.href);
	},

	initialize: function(s1, s2, path){
	
		sort_criterion1 = s1
		sort_criterion2 = s2;
		this.results_container = $$('div.results')[0];
		this.btn_results_toggle_list = $('btn_results_toggle_list');
		this.btn_results_toggle_grid = $('btn_results_toggle_grid');
	
		// preload images
		image_array = new Array('/media/images/btn_results_toggle_grid_down.gif','/media/images/btn_results_toggle_grid_up.gif','/media/images/btn_results_toggle_list_down.gif','/media/images/btn_results_toggle_list_up.gif');
		preloadImages(image_array);
	},

	updateSort: function(criterion1){
		newPath = path + "/" + criterion1 + "/" + sort_criterion2;
		window.location.href = newPath;
	},
	
	updateSelectMenu: function(criterion2) {
		newPath = path + "/" + sort_criterion1 + "/" + criterion2;
		window.location.href = newPath;
	},
	
	toggleDisplay: function(display_type) {
		if (display_type == 'list') {
			Element.removeClassName(this.results_container, 'grid');
			Element.addClassName(this.results_container, 'list');
			this.btn_results_toggle_list.src = this.btn_results_toggle_list.src.replace(/_up/, "_down");
			this.btn_results_toggle_grid.src = this.btn_results_toggle_grid.src.replace(/_down/, "_up");
			Cookie.set('flowgram_results_filter_type', 'list', 1, '/');
		}
		
		else if (display_type == 'grid') {
			Element.removeClassName(this.results_container, 'list');
			Element.addClassName(this.results_container, 'grid');
			this.btn_results_toggle_grid.src = this.btn_results_toggle_grid.src.replace(/_up/, "_down");
			this.btn_results_toggle_list.src = this.btn_results_toggle_list.src.replace(/_down/, "_up");
			Cookie.set('flowgram_results_filter_type', 'grid', 1, '/');
		}
		
	}
	
});
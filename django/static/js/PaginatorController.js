/**
 * @author Chris Yap
 * 	Flowgram Paginator Controller
 */

var PaginatorController = Class.create();

Object.extend(PaginatorController.prototype, {
	initialize: function(){
		
		// init paginator
		this.initPaginator();
	},
	
	initPaginator: function() {

		var paginator_width = $('paginator_ul').offsetWidth;
		var paginator_margin = (520 - paginator_width) / 2;
		$('paginator_ul').style.marginLeft = paginator_margin + 'px';
		$('paginator_ul').style.visibility = 'visible';

	}
	
	
});
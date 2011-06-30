<script type="text/javascript">
	var g_importing = false;
	
	function importPhotos(url, albumPhotosetID) {
		if(g_importing) {
			return false;
		}
		
		g_importing = true;
		var statusElement = 'status_' + albumPhotosetID;
		
		Element.removeClassName($(statusElement), 'photoImportStatus-error');
		Element.addClassName($(statusElement), 'photoImportStatus-normal');
		$(statusElement).innerHTML = "&raquo; Importing...";
		
		new Ajax.Request(url, {
			method: 'get',
			
			onSuccess: function(transport) {
				window.parent.g_FlashConnection.flex.reloadCurrentFlowgram();
				$(statusElement).innerHTML = "&raquo; Photos imported!";
				g_importing = false;
			},
			
			onFailure: function(transport) {
				Element.removeClassName($(statusElement), 'photoImportStatus-normal');
				Element.addClassName($(statusElement), 'photoImportStatus-error');
				$(statusElement).innerHTML = "&raquo; There has been an error, please try again later.";
				g_importing = false;
			}
		});
		 
		return false;
	}
</script>

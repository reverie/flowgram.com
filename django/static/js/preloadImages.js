// preload images
function preloadImages(image_array) {
	document.imageArray = new Array(image_array.length);
	for(var i=0; i<image_array.length; i++) {
		document.imageArray[i] = new Image;
		document.imageArray[i].src = image_array[i];
	}
}

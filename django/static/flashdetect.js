//Taken from PPK
var flashinstalled = 0; //0=unknown, 1=no, 2=yes
var flashversion = 0;
if (navigator.plugins && navigator.plugins.length)
{
	var x = navigator.plugins["Shockwave Flash"];
	if (x)
	{
		flashinstalled = 2;
		if (x.description)
		{
			y = x.description;
			flashversion = y.charAt(y.indexOf('.')-1);
		}
	}
	else
		flashinstalled = 1;
	if (navigator.plugins["Shockwave Flash 2.0"])
	{
		flashinstalled = 2;
		flashversion = 2;
	}
}
else if (navigator.mimeTypes && navigator.mimeTypes.length)
{
	var x = navigator.mimeTypes['application/x-shockwave-flash'];
	if (x && x.enabledPlugin)
		flashinstalled = 2;
	else
		flashinstalled = 1;
}
else { //IE:
	for(var i=10; i>0; i--){
		flashVersion = 0;
		try{
			var flash = new ActiveXObject("ShockwaveFlash.ShockwaveFlash." + i);
			flashVersion = i;
            break;
		}
		catch(e){
		}
	}
}

if ((flashinstalled !=2) || (flashversion < 8)) {
    alert("You need to install Flash 8.0 or higher to use this site.");
}

var sniff_br=new Array(4);
var sniff_os=new Array(2);
var sniff_flash=new Array(2);

var sniff_br_id = '';
var sniff_major_version = '';
var sniff_full_client_string = ''
var sniff_os_version = '';
var sniff_has_required_flash = false;

sniff_br=getBrowser();
sniff_os=getOS();
sniff_flash=hasFlashPlugin();

sniff_br_id = sniff_br[0];
sniff_major_version = getMajorVersion(sniff_br[1]);
sniff_os_id = sniff_os[0];
sniff_os_version = sniff_os[1];

sniff_flash=hasFlashPlugin();

if (sniff_br_id=='firefox') {
	if ((sniff_major_version=='1.5') || (sniff_major_version=='15')) {
		sniff_major_version='1_5';
	}
}

if(sniff_br_id=='safari'){
	sniff_full_client_string = sniff_br_id + '_' + sniff_os_id;
}

else {
	sniff_full_client_string = sniff_br_id + '_' + sniff_major_version + '_' + sniff_os_id;
}

if ((sniff_flash[0] == 2) && (sniff_flash[1] >= 9)) {
	sniff_has_required_flash = true;
}

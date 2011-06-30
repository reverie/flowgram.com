var Wildfire = new Object();
Wildfire.LinkedLoading = true;
Wildfire._pixeIframeCreated = false;

Wildfire.Flash={

isIE  : (navigator.appVersion.indexOf("MSIE") != -1) ? true : false,
isWin : (navigator.appVersion.toLowerCase().indexOf("win") != -1) ? true : false,
isOpera : (navigator.userAgent.indexOf("Opera") != -1) ? true : false,

AC_Generateobj:function(objAttrs, params, embedAttrs) { 
	var str = '';
	if (this.isIE && this.isWin && !this.isOpera)	{
		str += '<object ';
		for (var i in objAttrs) {str += i + '="' + objAttrs[i] + '" ';}
		str += '>';
		for (var i in params) {str += '<param name="' + i + '" value="' + params[i] + '" /> ';}
		str += '</object>';
	}
	else {
		str += '<embed ';
		for (var i in embedAttrs) {str += i + '="' + embedAttrs[i] + '" ';}
		str += '> </embed>';
	}
	return str;
},

AC_FL_GetContent:function(){
	var ret = this.AC_GetArgs(arguments);
	return this.AC_Generateobj(ret.objAttrs, ret.params, ret.embedAttrs);
},

AC_GetArgs:function(args, classid, mimeType){
	var ret = {};
	ret.embedAttrs = {};
	ret.params = {};
	ret.objAttrs = {};
	for (var i=0; i < args.length; i=i+2){
		var currArg = args[i].toLowerCase();    
		switch (currArg){	
			case "movie":	
				ret.embedAttrs["src"] = args[i+1];
				ret.params["movie"] = args[i+1];
			break;
			case "id":  
			case "width":
			case "height":
			case "align":
			case "name":
				ret.embedAttrs[args[i]] = ret.objAttrs[args[i]] = args[i+1];
			break;
			default:
				ret.embedAttrs[args[i]] = ret.params[args[i]] = args[i+1];
		}
  }
  ret.objAttrs['codebase']='http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=8,0,0,0';
  ret.objAttrs["classid"] = "clsid:d27cdb6e-ae6d-11cf-96b8-444553540000";
  ret.embedAttrs["type"] ="application/x-shockwave-flash";
  ret.embedAttrs['pluginspage']='http://www.macromedia.com/go/getflashplayer';
  
  return ret;
}

} // Wildfire.Flash

// Event handlers
Wildfire.onClose = Wildfire.onPostProfile = Wildfire.onPostComment = Wildfire.onSend = function(){};

Wildfire.modules = new Object();
Wildfire.modulesArray = new Array();


/*** PUBLIC METHODS ***/
	
Wildfire.initShare = function(partner, targetId, width, height, config)	{   
	return Wildfire._createJSModule("share",partner,targetId,width,height,config,
						'cssURL,cornerRoundness,initialMessageType,domainForCallback,partner,source,partnerData,width,height,emailTabHidden,customCheckboxVisible,customCheckboxChecked,customCheckboxText,' +
						'internalColor,frameColor,externalColor,tabTextColor,textColor,fontType,fontSize,' +
						'headerInternalColor,headerFrameColor'
						);
}

Wildfire.initPost = function(partner, targetId, width, height, config) {	
	return Wildfire._createFlashModule("post",partner,targetId,width,height,config);
}

//DEPRECATED, replaced by initShare */
Wildfire.init = Wildfire.initShare;

//DEPRECATED, replaced by module.applyConfig*/
Wildfire.applyConfig= function(config) {
	if (isnotnull(Wildfire.share)) Wildfire.share.applyConfig(config);
}

/*** Flash Interface ***/
//this is Called from the SWF
Wildfire._GetFlashModuleXMLConfig=function (targetId){
	//hide the js progress indicator -- this is a mac issue fix.;
	var pdiv = document.getElementById(targetId+"_progress");
	if (pdiv!=null) {
		pdiv.innerHTML='&nbsp;';
		pdiv.style.display = "none";
		pdiv.style.visibility = "hidden";
	}
	
	xs= ['config',[], [
			'display',['width','height','showCodeBox','rememberMeVisible','networksToShow','bulletinChecked','showEmail','showPost','showBookmark','showDesktop'],
			'body',['font=fontType','size=fontSize'],[
				'background',['frame-color=frameColor','background-color=internalColor','corner-roundness=cornerRoundness'],
				'controls',[], [
					'textboxes',[],	[
						'inputs',['color=textInputColor','background-color=textInputBackgroundColor','frame-color=textInputBorderColor']
						],
					'snbuttons',['color=tabTextColor|snButtonsTextColor','background-color=snButtonsBackgroundColor','frame-color=snButtonsFrameColor','over-color=tabTextColor|snButtonsOverTextColor','over-background-color=snButtonsOverBackgroundColor','over-frame-color=snButtonsOverFrameColor'],
					'buttons',['font=fontType|buttonFontType','color=buttonTextColor']
					],
				'texts background-color="transparent" ',['color=textColor'],[
					'messages',['color=messageTextColor'],
					'links',['font=linkFontType','color=linkTextColor'],
					'privacy',['color=privacyTextColor']
					]
				]
			]
		];

	var oConfig=Wildfire._GetFlashModuleConfig(targetId);
	var s=Wildfire._BuildXMLConfigFromJSON(oConfig,xs);
	
	return s;

}

Wildfire._GetFlashModuleConfigAttribute=function (targetId,configAttribute,canBeTextareaID){
	//hide the js progress indicator -- this is a mac issue fix.;
	var pdiv = document.getElementById(targetId+"_progress");
	if (pdiv!=null) {
		pdiv.innerHTML='&nbsp;';
		pdiv.style.display = "none";
		pdiv.style.visibility = "hidden";
	}

	var module=Wildfire.modules[targetId];
	if (module!=null) {
		var AttribValue=module.config[configAttribute];
		if (typeof AttribValue=='undefined') return null;
		if (canBeTextareaID==true) {
			if ( isnotnull(AttribValue) ) {
				try {
					var element=document.getElementById(AttribValue);
					
					if ( isnotnull(element) ) {
						return element.value;
					}
					else {
						return AttribValue;
					}
					
				} catch (e) {
					//GIGYAONLY:alert('Unable to get template for module:' + targetId + ', configAttribute :'+ configAttribute + '\n' + ex.description);
					return AttribValue;	
				}
			}
		}
		else {
			return AttribValue;
		}
	}
	else {
		return {error:'Modlue not found',MID:targetId};
	}
}

Wildfire._GetFlashModuleConfig=function (targetId){
	if (Wildfire.modules == null) {
		alert('Wildfire has no modules yet');
	}
	var module=Wildfire.modules[targetId];
	if (module!=null) {
	
		var res=module.config;
		return res;
	}
	else {
		return null;
	}
}
	

/*** PRIVATE METHODS ***/

Wildfire._BuildXMLConfigFromJSON=function (oConfig,xs) {

	var s=new Array();
	try{
	for(var i=0;i<xs.length;i+=2){

		s[s.length]='<'+xs[i]+' ';
		var atts=xs[i+1];

		for (var ia=0;ia<atts.length;ia++) {
		
			var attrAndKeys=atts[ia].split('=');
			var key=attrAndKeys[0];
			var valkeys;
			if (attrAndKeys.length>1) {
				valkeys=attrAndKeys[1]
			}
			else {
				valkeys=attrAndKeys[0];
			}
			
			var arrKeys=valkeys.split('|')
			for (var ikey=0;ikey<arrKeys.length;ikey++) {
				if (typeof oConfig[arrKeys[ikey]] != 'undefined') {
					s[s.length]=key+'="';
					s[s.length]=(''+oConfig[arrKeys[ikey]]).replace('&','&amp;').replace('"','&quot;').replace('<','&lt;').replace('>','&gt;') ;
					s[s.length]='" ';
					break;
				}
			}
		}
		if (i+2==xs.length) { // there are no more nodes
			s[s.length]='/>';						
		}
		else {
			if (typeof xs[i+2]!='string') {
			  s[s.length]='>';
			  s[s.length]=Wildfire._BuildXMLConfigFromJSON(oConfig,xs[i+2]);
			  s[s.length]='</'+xs[i].split(' ')[0]+'>';
			  i++; // skip the array node.
			}
			else {
				s[s.length]='/>';
			}
		}
		
	}
	}
	catch(e){
//			return ('***');
	}
	return s.join('');
}

Wildfire._createJSModule = function (moduleType, partner, targetId, width, height, config, getParams)	
{	
	try {
		config.location = document.location.href;
	} catch(err) {}
	
	config.partner = partner;
	config.width = width;
	config.height = height;

	// validate input params
	if ( undef(moduleType) || undef(partner) || undef(targetId) || undef(width) || undef(height)|| undef(config)) return;

	var module = this[targetId] = this.modules[targetId] = this.modulesArray[this.modulesArray.length] = new Wildfire._JSModule();
	module.copyConfig(config);
	module.ready = false;
	module.type = moduleType;
	module.id = targetId;
	module.partner = partner;
	module.width = width;
	module.height = height;
	module.container = document.getElementById(targetId);		  
	module.container.style.width  = width + "px";
	module.container.style.height = height + "px";

	module.qsParams = new Array();
	var getParamArray = getParams.split(',');
	for (var i=0; i<getParamArray.length ; i++)
		Wildfire._addQSParam(module,getParamArray[i]);
	
	module.init(true); // true means check ping for safe mode
	return module;
};

Wildfire._origOnLoad = null;
Wildfire._onLoad = function(evt)
{
	if (Wildfire._origOnLoad!=null && Wildfire._origOnLoad!=Wildfire._onLoad)
		Wildfire._origOnLoad(evt);
	
	if (evt.ModuleID == Wildfire.modulesArray[0].id)
	{
		for (var i=1;i<Wildfire.modulesArray.length; i++)
		{
			if (!Wildfire.modulesArray[i].ready) 
			{
				try {Wildfire.modulesArray[i].init(true);} catch(e) {}
			}
				
		}
	}
};

Wildfire._createFlashModule = function (moduleType, partner, targetId, width, height, config/*, getParams*/)	
{	
	// set bookmarkURL if not set
	
	try {
		if (typeof config['bookmarkURL'] == 'undefined')
			config['bookmarkURL'] = document.location.href;
	} catch (e) {}


	// hook onLoad 
	if (Wildfire.LinkedLoading) 
	{
		if (Wildfire._origOnLoad==null && typeof Wildfire.onLoad != 'undefined') 
			Wildfire._origOnLoad = Wildfire.onLoad;
	
		Wildfire.onLoad = Wildfire._onLoad;
		// safety valve - if first module never loads, load everything
	}

	var blnRecreate=false;
	var idxInArray;
	if (this.modules[targetId] != null) {
		blnRecreate=true;
		document.getElementById(targetId).innerHTML='&nbsp;';
		idxInArray=this.modules[targetId].idxInArray;
	}
	else {
		idxInArray=this.modulesArray.length;
	}
	try {
		config.location = document.location.href;
	} catch(err) {}
	
	config.partner = partner;
	config.width = width;
	config.height = height;

	// validate input params
	if ( undef(moduleType) || undef(partner) || undef(targetId) || undef(width) || undef(height)|| undef(config)) return;
	
	
	var module = new Wildfire._FlashModule();
	this.modulesArray[idxInArray] = this[targetId] = this.modules[targetId] = module;
	
	module.idxInArray=idxInArray;
	module.copyConfig(config);
	module.queued = false;
	module.ready = false;
	module.type = moduleType;
	module.id = targetId;
	module.partner = partner;
	module.width = width;
	module.height = height;
	module.container = document.getElementById(targetId);		  
	module.container.style.width  = width + "px";
	module.container.style.height = height + "px";
	
	/*
	module.qsParams = new Array();
	var getParamArray = getParams.split(',');
	for (var i=0; i<getParamArray.length ; i++)
		Wildfire._addQSParam(module,getParamArray[i]);
	*/
	if (!Wildfire.LinkedLoading || this.modulesArray.length==1 || this.modulesArray[0].ready)
	{
		module.init(true); // true means check ping for safe mode
	} else {
		module.queued = true;
	}
	return module;
};


Wildfire._raiseModulesUpdate = function() 
{
	var moduleList = "";
	for(var key in this.modules) moduleList += key + ",";
			
	var eventData = {'type':'modulesUpdate','modules':moduleList};

	this._raiseSysEvent(eventData);
}

Wildfire._raiseSysSignoutEvent = function() {
	this._raiseSysEvent({'type':'signout'});
}

Wildfire._raiseSysEvent = function(eventData) 
{
	if (this.modulesArray.length<=1) return;
	
	for(var key in this.modules) {
		var rse=this.modules[key].raiseSysEvent;
		if (rse!=null) {
			rse(eventData);
		}
	}
}

Wildfire._onFrameLoaded = function(moduleId) 
{
	var ui = document.getElementById(moduleId+"_UIFrame");
	if (ui!=null) ui.style.visibility="visible";	

	var pdiv = document.getElementById(moduleId+"_progress");
	if (pdiv!=null) pdiv.style.display = "none";

	this.modules[moduleId].UIFrame.style.visibility="visible";	
	this.modules[moduleId].applyConfig();
	this.modules[moduleId].ready = true;
	
	setTimeout("Wildfire._raiseModulesUpdate()",1500);
};

Wildfire._addQSParam = function(module,pName) {
	if ( def(typeof module.config) && def(module.config[pName]) ) {
		module.qsParams[module.qsParams.length] = pName+'='+Wildfire._URLEncode(module.config[pName]);
	}
};

Wildfire._URLEncode=function (s){
	if (encodeURIComponent) {
		return encodeURIComponent(s);
	}
	else {
		es=escape(s);
		return es.replace(/\+/g,'%2b').replace(/%20/g,'+').replace(/[/]/g,'%2f').replace(/%3D/g,'%3d');
	}
};

Wildfire._onCallback=Wildfire._raiseEvent = function(WFEvent) {
	try {
		switch(WFEvent.type)
		{
			case 'send':
				if (isnotnull(Wildfire.onSend))
					Wildfire.onSend(WFEvent);
				break;
			case 'postComment':
				if (isnotnull(Wildfire.onPostComment))
					Wildfire.onPostComment(WFEvent);
				break;
			case 'postProfile':
				if (isnotnull(Wildfire.onPostProfile))
					Wildfire.onPostProfile(WFEvent);
				break;
			case 'close':
				if (isnotnull(Wildfire.onClose))
					Wildfire.onClose(WFEvent);
				break;
			case 'load':
				
				if (isnotnull(Wildfire.onLoad))
				{
					Wildfire.modules[WFEvent.ModuleID].ready = true; 
					Wildfire.onLoad(WFEvent);
				}
				break;

		}
	} catch (err) {
		//GIGYAONLY:alert('exception in _onCallback: '+err.description);
	}
};

Wildfire._Module=function() {
	// for common functionality of Flash and JS modules
}


Wildfire._JSModule= function () {
	this.formsContainer = null;
	this.pingTimeout = null;
}
Wildfire._JSModule.prototype=new Wildfire._Module();


Wildfire._FlashModule=function(){}
Wildfire._FlashModule.prototype=new Wildfire._Module();


Wildfire._JSModule.prototype.pingOK = function(ok) {
	window.clearTimeout(this.pingTimeout);
	this.config.safeMode = !ok;
	this.init(false);
}


Wildfire._FlashModule.prototype.init = function(checkPing){
	var html='';
		if ((''+this.config.isApply)!='true') {
			html += '<div style="position:relative;top:50%;text-align:center;font-size:12px;z-index:50;" id="'+this.id+'_progress"><center><img  src="'+this.config.progressImageSrc+'"></center></div>';
		}
		html += Wildfire.Flash.AC_FL_GetContent(
		'id', 'wfmodule_'+this.id,
		'name', 'wfmodule_'+this.id,
		'width', this.config.width,
		'height', this.config.height,
		'movie', 'http://cdn.gigya.com/WildFire/swf/wildfire.swf',
		'quality', 'high',  
		'align', 'middle',
		'play', 'true',
		'loop', 'true',
		'scale', 'showall',
		'wmode', (this.config.nowmode?'':'transparent'), 
		'devicefont', 'false',
		'bgcolor', ((this.config.nowmode && this.config.outsideColor)?this.config.outsideColor:'#ffffff'),
		'menu', 'true',
		'allowFullScreen', 'false',
		'allowScriptAccess','always',
		'salign', '',
		'flashvars','ModuleID='+ this.id+'&now='+(new Date()).getTime(),
		'swLiveConnect','true'
		)
	
	window['wfmodule_'+this.id] = null;
	//alert('html =' + html);
	if (!Wildfire._pixeIframeCreated) {
		html += "<iframe src='http://cdn.gigya.com/wildfire/do_not_delete.htm' style='width:0;height:0;visibility:hidden' />";
		Wildfire._pixeIframeCreated = true;
	}
		
	this._injectWFCode(html);
	//alert('Html Code  Injected');
	// ExternalInterface bug workaround - 
	window['wfmodule_'+this.id] = document.getElementById('wfmodule_'+this.id);
	//alert('window attribute set, invoking go()');
	//because the flash needs to do externalInterface calls as soon as it starts
	//we can not have it "autoExecute" or the line above this comment would not
	//be executed by the time it tries to call back.
	//window['wfmodule_'+this.id].SetVariable('_root.ready','1');
}

Wildfire._IsModuleReady=function(targetId) {
	return (window['wfmodule_'+targetId] != null)
}


Wildfire._JSModule.prototype.init = function(checkPing) 
{
	var wfroot='http://wildfire.gigya.com/wildfire';
	var id=this.id;
	var uifid=id+'_UIFrame';
	var cfg=this.config;
	
	if (!cfg.safeMode && checkPing && this.pingTimeout==null)
	{
		var script = document.createElement("script");
		script.src = wfroot+'/jsping.ashx?mid='+id + "&rand=" + Math.random() + Math.random();
		this.container.appendChild(script);
		this.pingTimeout = window.setTimeout("Wildfire.modules['"+id+"'].pingOK(false)",10000);
		return;
	}
	var qs = this.qsParams.join('&');
	qs += ("&mid="+id);
	
	var html = "";
	var formsHTML = "";
	var UIURL = wfroot+'/'+this.type + "Main.aspx?" + qs;
	if (cfg.safeMode){
		UIURL = this.getSafeModeURL();
		if (UIURL==null) {
			Wildfire[id] = Wildfire.modules[id] = Wildfire.modulesArray[Wildfire.modulesArray.length] = null;
			return null;
		}
		html += "<iframe allowtransparency='true' id="+uifid +" name="+uifid+" style='width:" + cfg.width + "px;height:" + cfg.height + "px;display:inherit;visibility:inherit' frameborder=0 scrolling=no></iframe>";
		formsHTML += "<form id='"+id+"_postForm' action='"+UIURL+"' method='POST' target="+uifid+" style='display:none'></form>";
	}
	else if (cfg.simple) {
		if (this.type=="share") UIURL = wfroot+'/shareSimple.aspx';
		if (UIURL==null) {
			Wildfire[id] = Wildfire.modules[id] = Wildfire.modulesArray[Wildfire.modulesArray.length] = null;
			return null;
		}
		html += "<iframe allowtransparency='true' id="+uifid +" name="+uifid+" style='width:" + cfg.width + "px;height:" + cfg.height + "px;display:inherit;visibility:inherit' frameborder=0 scrolling=no></iframe>";
		formsHTML += "<form id='"+id+"_postForm' action='"+UIURL+"' method='POST' target="+uifid+" style='display:none'></form>";
	} else {
		html += "<div style='position:relative;top:50%;text-align:center;font-size:12px;' id='"+id+"_progress'><center><img  src='"+cfg.progressImageSrc+"'></center></div>";
		html += "<iframe allowtransparency='true' onload='Wildfire._onFrameLoaded(\""+id+"\")' id="+uifid+" style='visibility:hidden;width:" + cfg.width + "px;height:" + cfg.height + "px;' src='"+ UIURL + "' frameborder=0 scrolling=no></iframe>";			
		html += '<iframe id="IFREndlessActivityBugFix" style="display:none;width:100px;height:10px"></iframe>';
		html += this._createCBFrame();

		formsHTML += "<form id='"+id+"_postForm' action='"+wfroot+"/WFHandler.ashx?cmd=config' method='POST' target='"+id+"_postTargetFrame' style='display:none'></form>";			
		formsHTML += "<form id='"+id+"_sysEventForm' action='"+wfroot+"/WFHandler.ashx?cmd=sysEvent' method='POST' target='"+id+"_sysEventFrame' style='display:none'></form>";
	}
	
	this._injectWFCode(html,formsHTML);	
	
	// if cant create callback frame, disable callbacks
	if (document.getElementById(id+"_wfCBFrame")==null)	{
		cfg.domainForCallback = null;
	}
		
	this.UIFrame = document.getElementById(id+"_UIFrame");
	this.postForm = document.getElementById(id+"_postForm");
	this.sysEventForm = document.getElementById(id+"_sysEventForm");
	
	if (cfg.simple || cfg.safeMode) this.applyConfig(); // normal modules get config on frame load
}

Wildfire._JSModule.prototype._createCBFrame = function() 
{
	if ( def(this.config.domainForCallback) && document.getElementById(this.id+'_wfCBDiv')==null ) 
	{
		try {
			document.domain = this.config.domainForCallback;	
			return "<iframe name='"+this.id+"_wfCBFrame' style='visibility:hidden;width:0px;height:0px;' src='http://wildfire."+this.config.domainForCallback+"/wildfire/WFHandler.ashx?domain="+escape(this.config.domainForCallback)+"'></iframe>";
			
		} catch(ex) {
			//GIGYAONLY:alert('Unable to create Iframe for callback: '+ex.description);
			return "";
		}
	} else {
		return "";
	}
}

Wildfire._FlashModule.prototype.copyConfig =  Wildfire._JSModule.prototype.copyConfig = function(config) 
{
	// clone config obj to module
	if (config!=null) {
		this.config = {};
		for(var key in config) this.config[key] = config[key];
	}

	// apply default values
	if ( undef(this.config.progressImageSrc) ) 	this.config.progressImageSrc = "http://cdn.gigya.com/WildFire/i/progress_ani.gif";
	//if ( undef(this.config.cornerRoundness) ) 	this.config.cornerRoundness=1;
	if ( undef(this.config.simple) ) this.config.simple = navigator.userAgent.toLowerCase().indexOf('safari')!=-1;
}

Wildfire._JSModule.prototype.getSafeModeURL = function(){
	if (this.type=="share") return "http://backup.gigya.com/WFSimple/share.aspx";
	return null;
}

// check if page already has 'form' tag, if yes, insert div to contain our forms, outside of it.
Wildfire._JSModule.prototype._injectWFCode= function(html,formsHTML){
	var el=this.container;
	for(;((el!=null) && ((''+el.tagName).toLowerCase() !='form'));el=el.parentNode);
	if (el!=null) { 
		this.container.innerHTML = html;
		this.formsContainer = document.createElement('div');
		this.formsContainer.style.display='none';
		el.parentNode.insertBefore(this.formsContainer,el);
		this.formsContainer.innerHTML = formsHTML;
		
	} else
	{
		this.container.innerHTML = html + formsHTML;
	}
};


Wildfire._FlashModule.prototype._injectWFCode= function(html){
	this.container.innerHTML = html;
};

Wildfire._JSModule.prototype.raiseSysEvent = function(eventData){
	if (this.sysEventForm==null || !this.ready)  return;
	
	var s = new Array(); var i=0;
	for(var key in eventData) {
		if (typeof key != 'function' && eventData[key]!=null) {
			s[i++] = "<input type=hidden name='"+key+"'/>"
		}
	}
	
	this.sysEventForm.innerHTML = s.join('');

	//set value (using foo.value handles escaping of strings better...)
	for (var i=0;i<this.sysEventForm.length; i++) {
		this.sysEventForm[i].value = eventData[this.sysEventForm[i].name];
	}
	this.sysEventForm.submit();
};

Wildfire._FlashModule.prototype.applyConfig = function(conf){
	conf.isApply="true";
	return Wildfire._createFlashModule(this.type, this.partner, this.id, this.width, this.height, conf);
};

Wildfire._JSModule.prototype.applyConfig = function(conf){
	if (conf!=null) this.copyConfig(conf);
	var cfg=this.config;
	if (cfg==null) return;
	if (cfg.location==null || cfg.location=="")	{
		try { cfg.location = document.location.href;} catch(err) {}
	}

	cfg.partner = this.partner;
	cfg.width	= this.width;
	cfg.height	= this.height;

	// check if templates are IDs or actual values
	// For Post
	postContent=['default','myspace','hi5','friendster','xanga','livejournal','freewebs','facebook','bebo','blogger','tagged','typepad','blackplanet'];
	for (var pci=0;pci<postContent.length;pci++){
		this._getTemplate(postContent[pci] + 'Content');
	}
	//For Share
	shareTemplates=['default','comment','email','myspace','hi5','friendster','xanga','freewebs'];
	for (var sti=0;sti<shareTemplates.length;sti++){
		this._getTemplate(shareTemplates[sti]+ 'Template');
	}

	// build config fields
	var s = new Array(); var i=0;
	for(var key in cfg) {
		if (typeof key != 'function' && cfg[key]!=null) {
			s[i++] = "<input type=hidden name='"+key+"'/>"
		}
	}

	this.postForm.innerHTML = s.join('');

	//set value (using formfield.value handles escaping of strings better...)
	for (var i=0;i<this.postForm.length; i++) {
		this.postForm[i].value = this.config[this.postForm[i].name];
	}
	this.postForm.submit();
	
	window.setTimeout('Wildfire._EndlessActivityBugFix();',1000);
};

Wildfire._EndlessActivityBugFix=function(){
	var ifr=document.getElementById('IFREndlessActivityBugFix');
	if (ifr!=null) {
		ifr.src='http://cdn.gigya.com/wildfire/i/n.gif';
	}
};

Wildfire._JSModule.prototype._getTemplate = function (key) {
	if ( isnotnull(this.config[key]) ) {
		try {
			if ( isnotnull(document.getElementById(this.config[key])) )
				this.config[key] = document.getElementById(this.config[key]).value;
		} catch (e) {
			//GIGYAONLY:alert('Unable to get template for key :'+ key + '\n' + ex.description);
		}
	}
};

Wildfire._CopyAtts=function(t,s,atts){ for(k in atts.split(',')){ t[atts[k]]=s[atts[k]]; }}
Wildfire._CopyAllAtts=function(t,s){for(k in s) {t[k]=s[k];}}

function undef(o) { return (typeof(o)=='undefined');}
function def(o) { return (typeof(o)!='undefined');}
function isnotnull(o) { return (def(o) && (o!=null));}

function WFQueue(){
  var queue=new Array();
  var queueSpace=0;
  this.count=function()
  {
	return queue.length;
  }
  this.enqueue=function(element){
    queue.push(element);
  }
  this.dequeue=function(){
    if (queue.length){
      var element=queue[queueSpace];
      if (++queueSpace*2 >= queue.length){
        for (var i=queueSpace;i<queue.length;i++) queue[i-queueSpace]=queue[i];
        queue.length-=queueSpace;
        queueSpace=0;
      }
      return element;
    }else{
      return undefined;
    }
  }
}

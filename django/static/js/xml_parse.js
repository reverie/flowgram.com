var XML = {};
XML.getRootNode = function(responseXML){ 
    switch(responseXML.childNodes.length){
        case 1: return responseXML.childNodes[0]; break;
        case 2: return responseXML.childNodes[1]; break;
        default: return false; break;
    }
};
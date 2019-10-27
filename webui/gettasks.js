'use strict';

var request=new XMLHttpRequest();

request.onreadystatechange=function(){
	if (request.readyState===4){
		var res=JSON.parse(request.responseText).data;
		for (let video of res){
			document.write(`<p>${JSON.parse(video).name}</p>`);
		}
	}
}

request.open('GET','http://127.0.0.1:8888/task');
request.send();

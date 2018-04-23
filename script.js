// var scroll_down = 1;

//if(scroll_down)
	//$(function(){window.scrollTo(0,document.body.scrollHeight);});

function main()
{
	$(".comments").hide();
	//alert(window.location)
	if(String(window.location).search(new RegExp('a=mes')) != -1)
		;//setInterval(location.reload(), 3000);
}

$(document).ready(main);

function show_comments(s)
{
	$("#c"+s).toggle();
}

var el;
function like(parent_t, parent, v)
{
	jQuery.get("xx.py?a=like_b&parent_t=" + parent_t + "&parent=" + parent + "&v=" + v, function (data){
		var l = data;
		if(v)
			$("#" + parent + "_l").html("<b>Ty to aprobujesz</b>");
		else
			$("#" + parent + "_dl").html("<b>Ty to dezaprobujesz</b>");
	});
}


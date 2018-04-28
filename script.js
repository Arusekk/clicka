// var scroll_down = 1;

//if(scroll_down)
	//$(function(){window.scrollTo(0,document.body.scrollHeight);});

var z;

function reload_messages()
{
	jQuery.get('xx.py?a=messages&z='+z, function(data) {$('#messages').html(data)});
}

function check_if_new_messages()
{
	jQuery.get('xx.py?a=anm&z='+z, function(data){
		if(data == '1\n')
		{
			reload_messages();
			document.getElementById('e9').play();
		}
	});
}

function main()
{
	$(".comments").hide();
	$('[lt3]').show();
	if($('#messages').length)
	{	
		reload_messages();
		setInterval(function(){check_if_new_messages();}, 15*1000)
	}
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

function comment_onclick(com)
{
	if(com.value ==  " Napisz komentarz…")
		com.value = "";
}

function enterpress(input)
{
	wiad = input.value
	input.value = ''
	jQuery.post('xx.py?a=mes_b&z='+z, {'content': wiad}, function(){reload_messages();})
}

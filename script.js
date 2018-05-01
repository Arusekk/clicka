// var scroll_down = 1;

//if(scroll_down)
	//$(function(){window.scrollTo(0,document.body.scrollHeight);});

var z, id;
var zaz_pol = 0;
var focus = 1;

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

function check_if_new_moves()
{
		jQuery.get('xx.py?a=anm_chess&gameid='+id, function(data){
		if(data == '1\n')
		{
			if(focus == 0)
			{
					document.getElementById('e9').play();
					document.getElementById('e9').onended = function () {location.reload();}
					document.getElementsByTagName('svg')[0].innerHTML = ""
					document.getElementsByTagName('h1')[0].innerHTML = "Ładowanie…"
			}
			else
			{
				location.reload();
			}

		}
		//else
			//alert(data)
	});	
}

function zaznacz_pole(pole)
{
	if (zaz_pol)
	{
		window.location = 'xx.py?a=chess_b&from='+zaz_pol+'&to='+pole + '&id=' + id;
	}
	else
	{
		zaz_pol = pole;
		document.getElementById(pole).setAttribute('opacity', 0.2);
		document.getElementById('tap').play();
	}
}

function main()
{
	$(".comments").hide();
	$('[lt3]').show();
	window.onfocus = function () {focus = 1;}
	window.onblur = function () {focus = 0;}
	if($('#messages').length)
	{	
		reload_messages();
		setInterval(function(){check_if_new_messages();}, 15*1000)
	}
	if($('svg').length)
	{
		setInterval(function(){check_if_new_moves();}, 20*1000)
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
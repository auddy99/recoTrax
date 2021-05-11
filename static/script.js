chosen_ids = ['7qiZfU4dY1lWllzX7mPBI3','1i1fxkWeaMmKEB4T7zqbzK','0e7ipj03S05BNilyu5bRzt','0VjIjW4GlUZAMYd2vXMi3b','2Fxmhks0bxGSBdJ92vM42m','0TK2YIli7K1leLovkQiNik','3KkXRkHbMCARz0aVfEt68P','1rfofaqEpACxVEHIZBJe6W','0pqnGHJpmpxLKifKRmU6WP']
$(".card h4").each(function(){
    $(this).children("br").last().remove()
})
$("#res-button").hover(function(){
	$("#alert-box").css("opacity","80%")
	setTimeout(function(){$("#alert-box").css("opacity","0")},10000)
})

function show_result(){
	$("#alert-box").css("display","none")
	$("#result").css("display","block")
	$("#res-button").css("display","none")
	reco_artists = []
	chosen_artists = []
	$(".card h4").each(function(){
		l = $(this).html().replaceAll("\n","").replaceAll("\t","").split("<br>")
		reco_artists = reco_artists.concat(l)
	})
	$(".chose p").each(function(){
		l = $(this).html().split("<br>")[1].replaceAll("\n","").replaceAll("\t","").split(", ")
		chosen_artists = chosen_artists.concat(l)
	})
	dict = {}
	reco_artists.forEach(function(el){
		if(dict[el])dict[el]++
		else dict[el] = 1
	})
	// chosen_artists.forEach(function(el){
	// 	if(dict[el])dict[el]--
	// 	else dict[el] = -1
	// })

	items = Object.keys(dict).map(function(key) {
	  return [key, dict[key]];
	})
	items.sort(function(first, second) {
	  return second[1] - first[1];
	})

	$("#new-reco div").html("")
	$("#more-reco div").html("")
	new_items = []
	more_items = []
	items.map(function(x){
		if(chosen_artists.includes(x[0])){
			more_items.push(x[0])
		}
		else{
			new_items.push(x[0])
		}
	})
	console.log(new_items)
	console.log(more_items)
	new_items.slice(0,10).map(function(x){
	    $("#new-reco div").append("<h4>"+x+"</h4>")
	})
	more_items.slice(0,10).map(function(x){
	    $("#more-reco div").append("<h4>"+x+"</h4>")
	})
	
}

function close_result(){
	$("#result").css("display","none")
	$("#res-button").css("display","block")
}

$("#cards").on('click', '.card', function(){
	//chosen
	$("#chosen").css("display","grid")
	id = $(this).children("span").text()
	url = $(this).children("img").attr("src")
	name = $(this).children("h3").text()
	artist = $(this).children("h4").html().replace("<br>",", ")

	choseString = `
		<div class="chose">
			<span style="display:none;">`+id+`</span>
			<img src=`+url+`>
			<p><b>`+name+`</b><br>`+artist+`</p>
		</div>
	`
	$("#chosen").append(choseString)

	//submit
	id = $(this).children().first().text()
	$("#main input").eq(-1).attr("value",id)
	$("#main button").click()

	$(this).remove()
})
// $(".card").css("border","2px solid red")


$("#main").on('submit', function(event){
	$.ajax({
		url: "/show",
		type: "post",
		data: {
			// These are params sent to show route
			id: $("#id").val(),
			chosen: String(chosen_ids)
		}
	})
	.done(function(data){
		id_list = String(data.id).split(',')
		name_list = String(data.name).split('$@')
		artist_list = String(data.artist).split('$@')
		url_list = String(data.url).split(',')
		n = id_list.length
		for(i=0;i<n;i++){
			cardString = `
				<div class="card">
					<span style="display:none;">`+id_list[i]+`</span>
					<img src=`+url_list[i]+`>
					<h3>`+name_list[i]+`</h3>
					<h4>
					`+artist_list[i].split(',').join('<br>')+`
					</h4>
				</div>
			`
			$("#cards").append(cardString)
		}
		chosen_ids = (chosen_ids + "," + id_list).split(",")
	})
	event.preventDefault();
});



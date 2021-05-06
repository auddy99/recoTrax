chosen_ids = ['7qiZfU4dY1lWllzX7mPBI3','1i1fxkWeaMmKEB4T7zqbzK','0e7ipj03S05BNilyu5bRzt','0VjIjW4GlUZAMYd2vXMi3b','2Fxmhks0bxGSBdJ92vM42m','0TK2YIli7K1leLovkQiNik','3KkXRkHbMCARz0aVfEt68P','1rfofaqEpACxVEHIZBJe6W','0pqnGHJpmpxLKifKRmU6WP']
$(".card h4").each(function(){
    $(this).children("br").last().remove()
})

$("#cards").on('click', '.card', function(){
	//chosen
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



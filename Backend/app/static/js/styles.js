$(function () {
	$(".favorite-form").on("submit", function (event) {
		event.preventDefault();

		var form = $(this);
		var button = form.find(".toggle-favorite");
		var isFavorite = button.data("is-favorite");
		var recipeId = form.find("input[name='recipe_id']").val();

		$.ajax({
			url: "/toggle_favorite",
			method: "POST",
			data: { recipe_id: recipeId },
			success: function (response) {
				location.reload(true);
				// Update the isFavorite data
				isFavorite = !isFavorite;
				button.data("is-favorite", isFavorite);

				// Toggle the button text based on the current state
				if (isFavorite) {
					button.val("Favorite");
					button.addClass("btn-outline-success");
					button.removeClass("btn-outline-danger");
				} else {
					button.val("Unfavorite");
					button.removeClass("btn-outline-success");
					button.addClass("btn-outline-danger");

					// Remove the recipe card from the DOM
					// 	$("#recipe-card-" + recipeId).remove();
				}

				// Show a flash message if necessary
				var flashMessage = response.flash_message;
				if (flashMessage) {
					// Display the flash message to the user
					alert(flashMessage);
				}
			},
		});
	});

	const modal = $("#recipe-modal");
	const image = modal.find("img");

	modal.on("show.bs.modal", function (event) {
		const button = $(event.relatedTarget);
		const recipeId = button.data("recipe-id");
		const recipeTitle = button.data("recipe-title");
		const imageUrl = button.data("image-url");
		const recipeInstructions = button.data("recipe-instructions");
		const recipeSourceUrl = button.data("recipe-source-url");
		const recipeIngredients = button.data("recipe-ingredients");
		const recipeSummary = button.data("recipe-summary");

		image.attr("src", imageUrl);
		image.attr("alt", "Recipe Image");

		// Set the recipe title and id in the modal
		const titleLink = $("#modal-recipe-title");
		$("#modal-recipe-title").text(recipeTitle + " " + recipeId);
		$("#recipe-instructions").text(recipeInstructions);
		$("#recipe-summary").text(recipeSummary);
		$("#recipe-ingredients").text(recipeIngredients);
		$("#recipe-link").attr("href", recipeSourceUrl);
		titleLink.attr("href", recipeSourceUrl);
	});

	const zoomModal = $("#zoom-modal");
	const zoomImage = zoomModal.find("#zoom-image");

	zoomModal.on("show.bs.modal", function (event) {
		const button = $(event.relatedTarget);
		const imageUrl = button.data("image-url");
		const recipeSummary = button.data("recipe-summary");

		zoomImage.attr("src", imageUrl);
		zoomImage.attr("alt", "Recipe Image");
		$("#recipe-summary").text(recipeSummary);
	});

	$(".highlight-button").click(function () {
		const button = $(this);
		button.addClass("btn-pressed");

		// Remove the highlight effect after 3 seconds
		setTimeout(function () {
			button.removeClass("btn-pressed");
		}, 3000);
	});

	// Hide warning modal when "Back" button or "X" button is clicked
	$("#back-button, .close").on("click", function () {
		$("#warning-modal").modal("hide");
	});

	// Show warning modal when "Recipe" button is clicked
	$(".show-warning-modal").on("click", function (event) {
		event.preventDefault();
		const recipeUrl = $(this).data("recipe-url");
		$("#continue-external").data("recipe-url", recipeUrl);
		$("#warning-recipe-url").attr("href", recipeUrl); // Set the href attribute
		$("#warning-recipe-url").text(recipeUrl); // Set the text of the link to the URL
		$("#warning-modal").modal("show");
	});

	// Redirect the user when the "Continue" button is clicked in the warning modal
	$("#continue-external").on("click", function () {
		const recipeUrl = $(this).data("recipe-url");
		window.open(recipeUrl, "_blank", "noopener noreferrer");
		$("#warning-modal").modal("hide");
	});
});

function showRecipe(recipe) {
	document.getElementById("modal-recipe-title").innerText = recipe.title;
	document.getElementById("modal-recipe-image").src = recipe.image;
	document.getElementById("modal-recipe-instructions").innerText =
		recipe.instructions;
}

// if (document.getElementById("account-page")) {
// 	// Your function here will only run if the element with id 'account-page' exists
// 	$(function () {
// 		$(".favorite-form").on("submit", function (event) {
// 			var form = $(this);
// 			var button = form.find(".toggle-favorite");
// 			var isFavorite = button.data("is-favorite");
// 			var recipeId = form.find("input[name='recipe_id']").val();

// 			$.ajax({
// 				url: "/toggle_favorite",
// 				method: "POST",
// 				data: { recipe_id: recipeId },
// 				success: function (response) {
// 					location.reload(true);
// 					// Update the isFavorite data
// 					isFavorite = !isFavorite;
// 					button.data("is-favorite", isFavorite);

// 					// Toggle the button text based on the current state
// 					if (isFavorite) {
// 						button.val("Favorite");
// 						button.addClass("btn-outline-success");
// 						button.removeClass("btn-outline-danger");
// 					} else {
// 						button.val("Unfavorite");
// 						button.removeClass("btn-outline-success");
// 						button.addClass("btn-outline-danger");

// 						// Remove the recipe card from the DOM
// 						// 	$("#recipe-card-" + recipeId).remove();
// 					}

// 					// Show a flash message if necessary
// 					var flashMessage = response.flash_message;
// 					if (flashMessage) {
// 						// Display the flash message to the user
// 						alert(flashMessage);
// 					}
// 				},
// 			});
// 		});
// 	});
// }

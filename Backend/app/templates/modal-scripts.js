// Modals
// Emphasis Modal Script
$(function () {
	const modal = $("#recipe-modal");
	const image = modal.find("img");

	modal.on("show.bs.modal", function (event) {
		const button = $(event.relatedTarget);
		const recipeId = button.data("recipe-id");
		const recipeTitle = button.data("recipe-title");
		const imageUrl = button.data("image-url");
		const recipeInstructions = button.data("recipe-instructions");
		const recipeSourceUrl = button.data("recipe-source-url");

		$("#recipe-instructions").text(recipeInstructions);
		$("#recipe-link").attr("href", recipeSourceUrl);

		image.attr("src", imageUrl);
		image.attr("alt", "Recipe Image");

		// Set the recipe title and id in the modal
		$("#recipe-instructions").text(recipeInstructions);
		const titleLink = $("#modal-recipe-title");
		$("#modal-recipe-title").text(recipeTitle + " " + recipeId);
		titleLink.attr("href", recipeSourceUrl);
	});
});

// Button Highlight function
$(function () {
	$(".highlight-button").on("click", function () {
		$(this).addClass("btn-pressed");
	});
});

// Remove the highlight effect after 7 seconds
$(function () {
	$("#recipe-modal").on("hidden.bs.modal", function () {
		const button = $(".btn-pressed");
		button.removeClass("btn-pressed");

		setTimeout(function () {
			button.removeClass("btn-pressed");
		}, 7000);
	});
});

// Warning Modal Script
// Warning when clicked
$(".show-warning-modal").on("click", function (event) {
	event.preventDefault();
	const recipeUrl = $(this).data("recipe-url");
	$("#continue-external").data("recipe-url", recipeUrl);
	$("#warning-modal").modal("show");
});

// Continue is clicked
$("#continue-external").on("click", function () {
	const recipeUrl = $(this).data("recipe-url");
	window.open(recipeUrl, "_blank", "noopener noreferrer");
	$("#warning-modal").modal("hide");
});

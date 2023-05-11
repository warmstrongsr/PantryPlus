<script>
$(function() {
  $(".toggle-favorite").click(function(event) {
    event.preventDefault();

    const button = $(this);
    const recipeId = button.data("recipe-id");

    $.ajax({
      url: "/toggle_favorite",
      type: "POST",
      data: {
        recipe_id: recipeId
      },
      success: function(response) {
        // Toggle the favorite/unfavorite button color
        button.toggleClass("btn-outline-success btn-outline-danger");

        // Show a flash message if necessary
        // You can modify this code based on your flash message implementation
        const flashMessage = response.flash_message;
        if (flashMessage) {
          // Display the flash message to the user
          alert(flashMessage);
        }
      }
    });
  });
});
</script>

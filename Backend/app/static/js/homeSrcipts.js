{/* <script>

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
    });
</script>
<script>
    $(function () {
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
    });
</script>

<script>
    function highlightButton(button) {
        button.classList.add("btn-pressed");
    }

    $(function () {
        $("#recipe-modal").on("hidden.bs.modal", function () {
            const button = $(".btn-pressed");
            button.removeClass("btn-pressed");

            // Remove the highlight effect after 3 seconds
            setTimeout(
                function (btn) {
                    btn.removeClass("btn-pressed");
                },
                7000,
                button
            );
        });
    });
</script>

<script>
    // Hide warning modal when "Back" button or "X" button is clicked
    $("#back-button, .close").on("click", function () {
        $("#warning-modal").modal("hide");
    });
</script>

<script>
    // Show warning modal when "Recipe" button is clicked
    $(".show-warning-modal").on("click", function (event) {
        event.preventDefault();
        const recipeUrl = $(this).data("recipe-url");
        $("#continue-external").data("recipe-url", recipeUrl);
        $("#warning-modal").modal("show");
    });

    // Redirect the user when the "Continue" button is clicked in the warning modal
    $("#continue-external").on("click", function () {
        const recipeUrl = $(this).data("recipe-url");
        window.open(recipeUrl, "_blank", "noopener noreferrer");
        $("#warning-modal").modal("hide");
    });
</script>
<script>
    function showRecipe(recipe) {
        document.getElementById("modal-recipe-title").innerText = recipe.title;
        document.getElementById("modal-recipe-image").src = recipe.image;
        document.getElementById("modal-recipe-instructions").innerText =
            recipe.instructions;
    }
</script> */}
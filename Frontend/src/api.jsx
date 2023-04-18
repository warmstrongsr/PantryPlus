const API_BASE_URL = "http://localhost:5000";

const getRecipes = async () => {
	const response = await fetch(`${API_BASE_URL}/recipes`);
	const data = await response.json();
	return data;
};

const addRecipe = async (recipe) => {
	const response = await fetch(`${API_BASE_URL}/recipes`, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify(recipe),
	});
	const data = await response.json();
	return data;
};

export { getRecipes, addRecipe };

// from weather

// console.log(API_KEY);

// // Grab the form
// let form = document.getElementById("weatherForm");
// form.addEventListener("submit", handleFormSubmit);

// async function handleFormSubmit(event) {
// 	event.preventDefault(); // Prevent the event from making a new get request and refreshing page
// 	console.log(event);
// 	let city = event.target.city.value;

// 	let cityInfo = await getcityInfo(city);

// 	// Execute the buildcityCard function with city Info
// 	buildcityCard(cityInfo);

// 	// Clear the input box at end
// 	event.target.city.value = "";
// }

// async function getcityInfo(city) {
// 	try {
// 		let response = await fetch(
// 			`http://api.weatherapi.com/v1/current.json?key=${API_KEY}&q=${city}`
// 		);
// 		let data = await response.json();
// 		return data;
// 	} catch (err) {
// 		console.error(err);
// 	}
// }

// // Function that will take in a city info object and create a card
// function buildcityCard(cityObj) {
// 	// Build a card with city info
// 	let card = document.createElement("div");
// 	card.className = "card h-100";

// 	// Create card body
// 	let cardBody = document.createElement("div");
// 	cardBody.className = "card-body";

// 	// Create city name/location elements
// 	let cityTitle = document.createElement("h5");
// 	cityTitle.innerHTML = `${cityObj.location.name}, ${cityObj.location.region}, ${cityObj.location.country}`;
// 	cityTitle.className = "card-title";

// 	// Create temp elements
// 	let cityTemp = document.createElement("p");
// 	cityTemp.innerHTML = `Tempature: ${cityObj.current.temp_c}C (${cityObj.current.temp_f}F)`;
// 	cityTemp.className = "card-temp";

// 	// Condition element (*my original first)
// 	let cityCondition = document.createElement("p");
// 	cityCondition.innerHTML = `Condition: ${cityObj.current.condition.text}`;
// 	cityCondition.className = "card-text";

// 	// Wind?  might as well since I baselined Chicago
// 	let cityWind = document.createElement("p");
// 	cityWind.innerHTML = `Wind: ${cityObj.current.wind_mph} mph (${cityObj.current.wind_kph} km/h) (${cityObj.current.wind_dir})`;
// 	cityWind.className = "card-text";

// 	// Add elements to the card's body
// 	cardBody.append(cityTitle);
// 	cardBody.append(cityTemp);
// 	cardBody.append(cityCondition);
// 	cardBody.append(cityWind);

// 	// Add card to card body
// 	card.append(cardBody);

// 	// Create a column for the card
// 	let col = document.createElement("div");
// 	col.className = "col-12 col-md-6 col-lg-3 my-3";

// 	// Add the card to the column
// 	col.append(card);

// 	// Get the city display row and add the column
// 	let cityDisplay = document.getElementById("weatherDisplay");
// 	weatherDisplay.prepend(col);

// 	console.log(cityObj);
// }

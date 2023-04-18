import axios from "axios";
import React, { useEffect, useState } from "react";
import { API_KEY } from "../components/secrets/apikey";
import SearchBtn from "../components/SearchBtn";
import RecipeCard from "../components/RecipeCard";
import Sidebar from "../components/Sidebar";

export default function Home({ user, loggedIn }) {
	const dummyData = [
		{
			id: 1,
			title: "Crispy Buttermilk Fried Chicken",
			image: "https://spoonacular.com/recipeImages/640803-312x231.jpg",
			alt: "Crispy Buttermilk Fried Chicken",
			ingredients: [],
			instructions: "",
			sourceUrl:
				"https://spoonacular.com/recipes/Crispy-Buttermilk-Fried-Chicken-640803",
		},
		{
			id: 2,
			title: "Lemon and Garlic Slow Roasted Chicken",
			image: "https://spoonacular.com/recipeImages/715574-312x231.jpg",
			alt: "Homemade Strawberry Shake",
			ingredients: [],
			instructions: "",
			sourceUrl:
				"https://spoonacular.com/recipes/Lemon-and-Garlic-Slow-Roasted-Chicken-649495",
		},
		{
			id: 3,
			title: "Your Basic Low Carb Breakfast",
			image: "https://spoonacular.com/recipeImages/1747693-312x231.jpg",
			alt: "Your Basic Low Carb Breakfast",
			ingredients: [],
			instructions: "",
			sourceUrl:
				"https://spoonacular.com/recipes/Your-Basic-Low-Carb-Breakfast-1747693",
		},
		{
			id: 4,
			title: "Mango Black Tea Skinny Cocktail",
			image: "https://spoonacular.com/recipeImages/650755-312x231.jpg",
			alt: "Mango Black Tea Skinny Cocktail",
			ingredients: [],
			instructions: "",
			sourceUrl:
				"https://spoonacular.com/recipes/Mango-Black-Tea-Skinny-Cocktail-650755",
		},
		{
			id: 5,
			title: "Ham With Bourbon, Molasses, and Pecan Glaze",
			image: "https://spoonacular.com/recipeImages/646216-312x231.jpg",
			alt: "Ham With Bourbon, Molasses, and Pecan Glaze",
			ingredients: [],
			instructions: "",
			sourceUrl:
				"https://spoonacular.com/recipes/Ham-With-Bourbon,-Molasses,-and-Pecan-Glaze-646216",
		},
		{
			id: 6,
			title: "Lemon and Garlic Slow Roasted Chicken",
			image: "https://spoonacular.com/recipeImages/649495-312x231.jpg",
			alt: "Lemon and Garlic Slow Roasted Chicken",
			ingredients: [],
			instructions: "",
			sourceUrl:
				"https://spoonacular.com/recipes/Lemon-and-Garlic-Slow-Roasted-Chicken-649495",
		},
		{
			id: 7,
			title: "Lazy Cobbler",
			image: "https://spoonacular.com/recipeImages/649381-312x231.jpg",
			alt: "Lazy Cobbler",
			ingredients: [],
			instructions: "",
			sourceUrl: "https://spoonacular.com/recipes/Lazy-Cobbler-649381",
		},
		{
			id: 8,
			title: "Duck Rumaki",
			image: "https://spoonacular.com/recipeImages/641717-312x231.jpg",
			alt: "Duck Rumaki",
			ingredients: [],
			instructions: "",
			sourceUrl: "https://spoonacular.com/recipes/Duck-Rumaki-641717",
		},
		{
			id: 9,
			title: "Lemon Pepper Steak",
			image: "https://spoonacular.com/recipeImages/649722-312x231.jpg",
			alt: "Lemon Pepper Steak",
			ingredients: [],
			instructions: "",
			sourceUrl: "https://spoonacular.com/recipes/Lemon-Pepper-Steak-649722",
		},
		{
			id: 10,
			title:
				"Cranberry Fettuccine Tomato Cream Sauce With Shrimps and Scallops",
			image: "https://spoonacular.com/recipeImages/640370-312x231.jpg",
			alt: "Cranberry Fettuccine Tomato Cream Sauce With Shrimps and Scallops",
			ingredients: [],
			instructions: "",
			sourceUrl:
				"https://spoonacular.com/recipes/Cranberry-Fettuccine-Tomato-Cream-Sauce-With-Shrimps-and-Scallops-640370",
		},
		{
			id: 11,
			title: "Bacon Wrapped Filet Mignon",
			image: "https://spoonacular.com/recipeImages/633338-312x231.jpg",
			alt: "Bacon Wrapped Filet Mignon",
			ingredients: [],
			instructions: "",
			sourceUrl:
				"https://spoonacular.com/recipes/Bacon-Wrapped-Filet-Mignon-633338",
		},
	];

	const [posts, setPosts] = useState(dummyData);
	const [page, setPage] = useState(0);
	const [onlyMine, setOnlyMine] = useState(false);
	const handleSubmit = async (inputValue) => {
		try {
			const response = await axios.get(
				`https://api.spoonacular.com/recipes/findByIngredients?ingredients=${inputValue}&apiKey=${API_KEY}`
			);
			setPosts(response.data);
		} catch (error) {
			console.error(error);
		}
	};

// useEffect(() => {
// 	setPosts(dummyData);
// }, []);
// const dummyData = [
// 		useEffect(() => {
// 		async function fetchPostData() {
// 			try {
// 				const response = await axios.get(
// 					`https://spoonacular.com/recipes/sesame-flank-steak-salad-1747701`
// 				);
// 				const recipes = response.data.results;
// 				const recipeData = await Promise.all(
// 					recipes.map(async (recipe) => {
// 						const imageResponse = await axios.get(
// 							`https://spoonacular.com/recipes/bacon-apple-pecan-stuffed-french-toast-1697823`
// 						);
// 						const image = imageResponse.data.image;
// 						return { ...recipe, image };
// 					})
// 				);
// 				setPosts(recipeData);
// 			} catch (error) {
// 				console.error(error);
// 			}
// 		}
// 		fetchPostData();
// 	}, [])

// ];




	const firstPostIndex = page * 10;
	const lastPostIndex = firstPostIndex + 10;

	return (
		<div className="row">
			<div className="col-12 col-lg-8 order-1 order-lg-1">
				{posts
					.filter((post) => !onlyMine || post.author.username === user.username)
					.slice(firstPostIndex, lastPostIndex)
					.map((post) => (
						<RecipeCard
							key={post.id}
							recipe={post}
							user={user}
							image={post.image}
						/>
					))}
			</div>

			<div className="col-12 col-lg-4 order-0 order-lg-1">
				<Sidebar
					posts={posts}
					page={page}
					setPage={setPage}
					onlyMine={onlyMine}
					setOnlyMine={setOnlyMine}
					lastPostIndex={lastPostIndex}
					loggedIn={loggedIn}
				/>
				<SearchBtn
					handleSubmit={handleSubmit}
					user={user}
					loggedIn={loggedIn}
				/>
			</div>
		</div>
	);
}

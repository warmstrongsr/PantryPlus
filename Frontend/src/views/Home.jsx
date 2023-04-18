import axios from "axios";
import React, { useEffect, useState } from "react";
import { API_KEY } from "../components/secrets/apikey";
import SearchBtn from "../components/SearchBtn";
import LinkCard from "../components/LinkCard";
import RecipeCard from "../components/RecipeCard";
import Sidebar from "../components/Sidebar";

export default function Home({ user, loggedIn }) {
	const [posts, setPosts] = useState([]);
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

	useEffect(() => {
		async function fetchPostData() {
			try {
				const response = await axios.get(
					// `https://api.spoonacular.com/recipes/complexSearch?apiKey=${API_KEY}`
				);
				const recipes = response.data.results;
				const recipeData = await Promise.all(
					recipes.map(async (recipe) => {
						const imageResponse = await axios.get(
							// `https://api.spoonacular.com/recipes/${recipe.id}/information?apiKey=${API_KEY}&includeNutrition=false`
						);
						const image = imageResponse.data.image;
						return { ...recipe, image };
					})
				);
				setPosts(recipeData);
			} catch (error) {
				console.error(error);
			}
		}
		fetchPostData();
	}, []);

	const firstPostIndex = page * 5;
	const lastPostIndex = firstPostIndex + 5;

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

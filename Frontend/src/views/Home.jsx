import React, { useEffect, useState } from "react";
import PostCard from "../components/PostCard";
import Sidebar from "../components/Sidebar";

export default function Home({ user, loggedIn }) {
	const [posts, setPosts] = useState([]);
	const [page, setPage] = useState(0);
	const [onlyMine, setOnlyMine] = useState(false);

	useEffect(() => {
		async function fetchPostData() {
			let response = await fetch(
				"https://kekambas-blog-api.onrender.com/api/posts"
			);
			let data = await response.json();
			if (onlyMine) {
				setPosts(data.filter((post) => post.author.id === user.id));
			} else {
				setPosts(data);
			}
		}
		fetchPostData();
	}, [onlyMine, user.id]);

	const firstPostIndex = page * 10;
	const lastPostIndex = firstPostIndex + 10;

	return (
		<div className="row">
			<div className="col-12 col-lg-8 order-1 order-lg-1">
				{posts.slice(firstPostIndex, lastPostIndex).map((post) => (
					<PostCard key={post.id} post={post} user={user} />
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
			</div>
		</div>
	);
}

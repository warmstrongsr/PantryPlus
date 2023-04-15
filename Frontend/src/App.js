import "./App.css";
import React, { useState, useEffect } from "react";
import { Routes, Route } from "react-router-dom";
import AlertMessage from "../components/AlertMessage";
import Navbar from "../components/Navbar";
import CreatePost from "../views/CreatePost";
import Home from "../views/Home";
import Login from "../views/Login";
import Signup from "../views/Signup";
import SinglePost from "../views/SinglePost";
import EditPost from "../views/EditPost";

export default function App() {
	// let name = "Will";
	// const now = new Date();
	const [loggedIn, setLoggedIn] = useState(
		localStorage.getItem("token") ? true : false
	);
	const [message, setMessage] = useState(null);
	const [category, setCategory] = useState(null);
	const [user, setUser] = useState({});

	function flashMessage(message, category) {
		setMessage(message);
		setCategory(category);
	}

	function logUserOut() {
		setLoggedIn(false);
		localStorage.removeItem("token");
		localStorage.removeItem("tokenExp");
		flashMessage("You have logged out", "primary");
	}
	return (
		<>
			<Navbar loggedIn={loggedIn} logUserOut={logUserOut} />
			<div className="container">
				{message ? (
					<AlertMessage
						flashMessage={flashMessage}
						message={message}
						category={category}
					/>
				) : null}
				<Routes>
					<Route path="/" element={<Home user={user} loggedIn={loggedIn} />} />
					<Route
						path="/Frontend/capstone-fe/src/views/Signup.jsx"
						element={<Signup flashMessage={flashMessage} />}
					/>
					<Route
						path="/login"
						element={<Login flashMessage={flashMessage} logUserIn={loggedIn} />}
					/>
					<Route
						path="/create"
						element={
							<CreatePost flashMessage={flashMessage} loggedIn={loggedIn} />
						}
					/>
					<Route
						path="/Frontend/capstone-fe/src/views/EditPost.jsx"
						element={
							<EditPost flashMessage={flashMessage} loggedIn={loggedIn} />
						}
					/>
				</Routes>
			</div>
		</>
	);
}


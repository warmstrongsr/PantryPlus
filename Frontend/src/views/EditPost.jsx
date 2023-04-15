import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function Update_post({ loggedIn, flashMessage}) {

    const navigate = useNavigate();

    useEffect(() => {
        if (!loggedIn){
            flashMessage('You must be logged in to update a post', 'danger');
            navigate('/login');
    }
})

async function handleSubmit(e){
        e.preventDefault();

        // Get the data from the form
        let title = e.target.title.value;
        let content = e.target.content.value;

        // Get the token from localStorage
        let token = localStorage.getItem('token');

        // Set up the request headers
        let myHeaders = new Headers();
        myHeaders.append('Content-Type', 'application/json');
        myHeaders.append('Authorization', `Bearer ${token}`);

        // Set up the request body
        let requestBody = JSON.stringify({ title, content })

        let response = await fetch(`/api/posts/${post.id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify(updatedPostData)
});
import React, { useState, useEffect } from 'react';
import PostCard from '../components/PostCard';
import Sidebar from "../components/Sidebar";

export default function Home() {
    
    const [posts, setPosts] = useState([])

    useEffect(() => {
        // Define async function
        async function fetchPostData(){
            let response = await fetch('http://localhost:5000/api/posts')
            let posts = await response.json()
            setPosts(posts);
        };
        // Execute async function
        fetchPostData();
    }, []);

    return (
        <div>
            <h1 className="text-center">Welcome to the Blog</h1>
            {posts.map( post => <PostCard key={post.id} post={post} />)}
        </div>
    )
}

import React from "react";
import { Link } from "react-router-dom";

export default function PostCard({ post, user }) {
	return (
		<>
			<div className="card mt-3">
				<div className="card-header">{post.title}</div>
				<div className="row g-0">
					<div className="col-md-4">
						<img
							className="card-img-top"
							src={
								post.image_url
									? post.image_url
									: `https://picsum.photos/500?random=${post.id}`
							}
							alt="random"
						/>
					</div>
					<div className="col-md-8">
						<div className="card-body">
							<h6 className="card-subtitle text-muted">{post.date_created}</h6>
							<h6 className="card-subtitle">By: {post.author.username}</h6>
							<p className="card-text">{post.content}</p>
							{post.author.username === user.username ? (
								<>
									<Link
										to={`/edit/${post.id}`}
										className="btn btn-success w-100"
									>
										Edit
									</Link>
								</>
							) : null}
						</div>
					</div>
				</div>
			</div>
		</>
	);
}

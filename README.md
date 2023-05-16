# PantryPlus
CRUD recipe app.  Find by ingredients, database search, user personal menu, and random recipe game all included. 

Users have access to the home page,(and the homepage only) if not signed up and logged in.  All authenticated users have access to current menu search, find by ingredients, database search, and Recipe Roulette. What you see on the home page is a distinct list of recipes that, at the very least have a link, title, and summary, (for some reason the blank covered plate picture counts as a picture so you may still see a few of those here or there.  The current top in point heavy ingredients search has a maximum of 100 results that I have split into 25 per page groupings.

Fellow developers:
If you intend on putting this application together for further testing you will need, (or atleast I reccomend) a virtual environment, access to flask and pip to install requirements.txt. You will also need a spooncular API key and keep in mind that this application is coded to update missing information as the user utilizes the random and find by ingredients search which can be quite costly in the points department.  Any new recipes are added to the database and as such available to users, (again. authenticated) as it grows. With that continued growth I will continue to refactor the usage of the database as it is less costly and I can pick what I would like to make available to the user, (recipe, ingredients, summary, and instructions at the moment).  Spoonacular API disperses these categories in different ways. Find by ingredients will get you a summary and ingredients, random searh will net you instructions and so on. I reccomend the use of Postman for testing these different approaches.  I graduated Coding Temple software engineer boot camp a few weeks ago and my application was okay but it was admittedly a brazen attempt at using as many technologies as possible.  React was certainly under-estimated by most of us.  But that is why I continue to code, because I love it and look forward to the continous learning. I'm a little late to party but this is where Ive  always should have been  I wish you all well.  Be safe.
                                                                                                    William "Will" Armstong SR.

Future Plans:
I intend on implementing React front end and Postgres SQL backend for the larger loads of additional recipes.  Based on my search of random foods daily I was able to accumulate over 2000 recipes.    

![Example GIF](home.Animation.gif)
![Example GIF](find_by_ingredientsgreenbeans.Animation.gif)
![Example GIF](roulette.Animation.gif)
![Pantry Plus2 thumbnail](https://github.com/warmstrongsr/PantryPlus/assets/107271171/7e65e26f-3e0c-40ed-ac9a-cf1bb1223708)
![db_total](https://github.com/warmstrongsr/PantryPlus/assets/107271171/1d34f1a9-174f-4f43-af75-9e377b7380a3)
![db_mushroom_sort](https://github.com/warmstrongsr/PantryPlus/assets/107271171/cd70a39f-79e0-4e55-90dc-e3eee7f503a5)



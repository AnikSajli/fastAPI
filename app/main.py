from typing import Optional
from fastapi import FastAPI, Body, Response, status, HTTPException
from pydantic import BaseModel
from random import randint
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


while True:
    try:
        connection = psycopg2.connect(host = 'localhost', database = 'fastAPI', user = 'postgres',
                                      password = '123456', cursor_factory=RealDictCursor)
        cursor = connection.cursor()
        print("Database connection was successful!")
        break
    except Exception as error:
        print("Connecting to database failed")
        print("Error", error)
        time.sleep(2)


my_posts = [{"id": 1, "title": "title 1", "content": "content 1"},
            {"id": 2, "title": "title 2", "content": "content 2"}]


def find_post(id):
    post_id = int(id)
    for post in my_posts:
        if post['id'] == post_id:
            return post


def find_index_post(id):
    post_id = int(id)
    for index, post in enumerate(my_posts):
        if post['id'] == post_id:
            return index


@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
                   (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    connection.commit()
    return {"data": new_post}


@app.get("/posts/{id}")
def get_post(id, response: Response):
    cursor.execute("""SELECT * FROM posts WHERE id=%s""", (str(id)))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} was not found")
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {'message': 'Post not found'}
    return {"post_detail": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id):
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id)))
    deleted_post = cursor.fetchone()
    connection.commit()

    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} does not exist")

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id, post: Post):
    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
                   (post.title, post.content, post.published, str(id)))
    updated_post = cursor.fetchone()
    connection.commit()
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} does not exist")
    # post_dict = post.dict()
    # post_dict['id'] = id
    # my_posts[post_index] = post_dict
    return {"data": f"Post with id {id} updated successfully!"}


















from flask import Response, request
from flask_restful import Resource
from models import Post, db, Following
from views import get_authorized_user_ids, can_view_post

import json


def get_path():
    return request.host_url + 'api/posts/'


class PostListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
        self.user_ids = get_authorized_user_ids(self.current_user)

    def get(self):
        # get posts created by one of these users:
        # get posts by authorized users:
        posts = Post.query.filter(Post.user_id.in_(self.user_ids))

        # apply limit parameter, if provided:
        try:
            limit = int(request.args.get('limit', 20))
        except ValueError:
            return Response(json.dumps({"message": "Invalid limit parameter"}), mimetype="application/json", status=400)

        if limit > 50:
            return Response(json.dumps({"message": "Invalid limit parameter"}), mimetype="application/json", status=400)
        posts = posts.limit(limit)

        # return response:
        return Response(json.dumps([post.to_dict() for post in posts]), mimetype="application/json", status=200)

    def post(self):
        # create a new post based on the data posted in the body 
        body = request.get_json()
        if not body.get('image_url'):
            return Response(json.dumps({'error': 'image_url required'}), status=400)

        # convert the data that the user sent over HTTP to a SQLAlchemy object
        new_post = Post(
            image_url=body.get('image_url'),
            user_id=self.current_user.id,  # must be a valid user_id or will throw an error
            caption=body.get('caption'),
            alt_text=body.get('alt_text')
        )
        # save it to the database
        db.session.add(new_post)  # issues the insert statement
        db.session.commit()

        # send the new data object to the user
        return Response(json.dumps(new_post.to_dict()), mimetype="application/json", status=201)


class PostDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user

    def patch(self, id):
        body = request.get_json()

        try:
            id = int(id)
        except:
            return Response(json.dumps({"message": "Invalid post id"}), mimetype="application/json", status=400)

        try:
            post = Post.query.get(id)
        except:
            return Response(json.dumps({"message": "Not Found"}), mimetype="application/json", status=404)

        if post is None:
            return Response(json.dumps({"message": "Not Found"}), mimetype="application/json", status=404)
        # only update the data fields that the user wants to change:
        if body.get('image_url'):
            post.image_url = body.get('image_url')
        if body.get('caption'):
            post.caption = body.get('caption')
        if body.get('alt_text'):
            post.alt_text = body.get('alt_text')

            # save back to database:
        db.session.commit()

        return Response(json.dumps(post.to_dict()), mimetype="application/json", status=200)

    def delete(self, id):
        try:
            id = int(id)
        except:
            return Response(json.dumps({"message": "Invalid post id"}), mimetype="application/json", status=400)
        try:
            post = Post.query.get(id)
        except:
            return Response(json.dumps({"message": "Not Found"}), mimetype="application/json", status=404)
        if post is None:
            return Response(json.dumps({"message": "Not Found"}), mimetype="application/json", status=404)
        if post.user_id != self.current_user.id:
            return Response(json.dumps({"message": "Permission Denied"}), mimetype="application/json", status=404)
        Post.query.filter_by(id=id).delete()
        db.session.commit()
        return Response(json.dumps({"message": "OK"}), mimetype="application/json", status=200)

    def get(self, id):
        post = Post.query.filter_by(id=id).first()
        if post is None:
            return Response(json.dumps({"message": "Not Found"}), mimetype="application/json", status=404)
        elif can_view_post(user=self.current_user, post_id=post.id):
            return Response(json.dumps(post.to_dict()), mimetype="application/json", status=200)
        else:
            return Response(json.dumps({"message": "Permission Denied"}), mimetype="application/json", status=404)


def initialize_routes(api):
    api.add_resource(
        PostListEndpoint,
        '/api/posts', '/api/posts/',
        resource_class_kwargs={'current_user': api.app.current_user}
    )
    api.add_resource(
        PostDetailEndpoint,
        '/api/posts/<int:id>', '/api/posts/<int:id>/',
        resource_class_kwargs={'current_user': api.app.current_user}
    )

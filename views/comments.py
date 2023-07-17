from flask import Response, request
from flask_restful import Resource
import json
from models import db, Comment, Post
from views import get_authorized_user_ids, can_view_post


class CommentListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
        self.user_ids = get_authorized_user_ids(self.current_user)
    
    def post(self):
        # create a new "Comment" based on the data posted in the body 
        body = request.get_json()
        print(body)
        try:
            if not body['text'] and not body['post_id']:
                return Response(json.dumps({'error': 'text and post_id required'}), status=400)
            if not can_view_post(body['post_id'], self.current_user):
                return Response(json.dumps({'error': 'You cannot comment on this post'}), status=404)
        except:
            return Response(json.dumps({'error': 'text and post_id required'}), status=400)
        try:
            body['post_id'] = int(body['post_id'])
        except:
            return Response(json.dumps({'error': 'post_id must be an integer'}), status=400)
        comment = Comment(
            post_id=body['post_id'],
            text=body['text'],
            user_id=self.current_user.id
        )
        db.session.add(comment)  # issues the insert statement
        db.session.commit()
        return Response(json.dumps(comment.to_dict()), mimetype="application/json", status=201)

    def get(self):
        comments = Comment.query.filter(can_view_post(Comment.post_id, self.current_user))

        try:
            limit = int(request.args.get('limit', 20))
        except ValueError:
            return Response(json.dumps({"message": "Invalid limit parameter"}), mimetype="application/json", status=400)

        if limit > 50:
            return Response(json.dumps({"message": "Invalid limit parameter"}), mimetype="application/json", status=400)
        comments = comments.limit(limit)

        return Response(json.dumps([comment.to_dict() for comment in comments]), mimetype="application/json", status=200)
        
class CommentDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
        self.user_ids = get_authorized_user_ids(self.current_user)
  
    def delete(self, id):
        # delete "Comment" record where "id"=id
        print(id)
        comment = Comment.query.get(id)
        if comment is None:
            return Response(json.dumps({"message": "Not Found"}), mimetype="application/json", status=404)
        elif comment.user_id == self.current_user.id:
            db.session.delete(comment)
            db.session.commit()
            return Response(json.dumps({"message": "OK"}), mimetype="application/json", status=200)

        return Response(json.dumps({"message": "Forbidden"}), mimetype="application/json", status=404)

    def get(self, id):
        # get "Comment" record where "id"=id
        comment = Comment.query.filter_by(id=id).first()
        if comment is None:
            return Response(json.dumps({"message": "Not Found"}), mimetype="application/json", status=404)
        elif can_view_post(comment.post_id, self.current_user):
            return Response(json.dumps(comment.to_dict()), mimetype="application/json", status=200)
        else:
            return Response(json.dumps({"message": "Forbidden"}), mimetype="application/json", status=404)


def initialize_routes(api):
    api.add_resource(
        CommentListEndpoint, 
        '/api/comments', 
        '/api/comments/',
        resource_class_kwargs={'current_user': api.app.current_user}

    )
    api.add_resource(
        CommentDetailEndpoint, 
        '/api/comments/<int:id>', 
        '/api/comments/<int:id>/',
        resource_class_kwargs={'current_user': api.app.current_user}
    )

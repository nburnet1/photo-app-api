from flask import Response, request
from flask_restful import Resource
from models import Bookmark, db, User
import json

from views import can_view_post


class BookmarksListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
        self.profile = User.query.filter_by(id=self.current_user.id).first()
    
    def get(self):
        # get all bookmarks owned by the current user
        bookmarks = Bookmark.query.filter_by(user_id=self.profile.id)

        # apply limit parameter, if provided:
        try:
            limit = int(request.args.get('limit', 20))
        except ValueError:
            return Response(json.dumps({"message": "Invalid limit parameter"}), mimetype="application/json", status=400)

        if limit > 50:
            return Response(json.dumps({"message": "Invalid limit parameter"}), mimetype="application/json", status=400)
        bookmarks = bookmarks.limit(limit)

        # return response:
        return Response(json.dumps([bookmark.to_dict() for bookmark in bookmarks]), mimetype="application/json", status=200)


    def post(self):
        # create a new "bookmark" based on the data posted in the body 
        body = request.get_json()
        print(body)

        try:
            if not body['post_id']:
                return Response(json.dumps({'error': 'post_id required'}), status=400)
            if not can_view_post(user=self.current_user, post_id=body['post_id']):
                return Response(json.dumps({'error': 'You cannot bookmark this post'}), status=404)
        except:
            return Response(json.dumps({'error': 'post_id required'}), status=400)

        bookmark = Bookmark(
            post_id=body['post_id'],
            user_id=self.current_user.id
        )
        try:
            db.session.add(bookmark)  # issues the insert statement
            db.session.commit()
        except:
            return Response(json.dumps({'error': 'Error creating bookmark'}), status=400)

        return Response(json.dumps(bookmark.to_dict()), mimetype="application/json", status=201)

class BookmarkDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    def delete(self, id):
        # delete "bookmark" record where "id"=id
        print(id)
        try:
            id = int(id)
        except:
            return Response(json.dumps({'error': 'Invalid id'}), status=400)
        if id is None:
            return Response(json.dumps({'error': 'id required'}), status=400)
        bookmark = Bookmark.query.get(id)
        if bookmark is None:
            return Response(json.dumps({'error': 'Not Found'}), status=404)
        if self.current_user.id != bookmark.user_id:
            return Response(json.dumps({'error': 'You cannot view this post'}), status=404)
        Bookmark.query.filter_by(id=id).delete()
        db.session.commit()
        return Response(json.dumps({"message": "OK"}), mimetype="application/json", status=200)

    def get(self, id):
        bookmark = Bookmark.query.filter_by(id=id).first()
        if bookmark is None:
            return Response(json.dumps({"message": "Not Found"}), mimetype="application/json", status=404)
        elif can_view_post(user=self.current_user, post_id=bookmark.post_id):
            return Response(json.dumps(bookmark.to_dict()), mimetype="application/json", status=200)
        else:
            return Response(json.dumps({"message": "Permission Denied"}), mimetype="application/json", status=404)



def initialize_routes(api):
    api.add_resource(
        BookmarksListEndpoint, 
        '/api/bookmarks', 
        '/api/bookmarks/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )

    api.add_resource(
        BookmarkDetailEndpoint, 
        '/api/bookmarks/<int:id>', 
        '/api/bookmarks/<int:id>',
        resource_class_kwargs={'current_user': api.app.current_user}
    )

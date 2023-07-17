from flask import Response, request
from flask_restful import Resource
from models import Following, User, db
import json

def get_path():
    return request.host_url + 'api/posts/'

class FollowingListEndpoint(Resource):
    def __init__(self, current_user):
        self.current_user = current_user
    
    def get(self):
        # return all of the "following" records that the current user is following
        following = Following.query.filter_by(user_id=self.current_user.id)
        return Response(json.dumps([follow.to_dict_following() for follow in following]), mimetype="application/json", status=200)

    def post(self):
        # create a new "following" record based on the data posted in the body 
        body = request.get_json()
        try:
            if body['user_id'] is None or body == {}:
                return Response(json.dumps({'error': 'user_id required'}), status=400)
        except:
            return Response(json.dumps({'error': 'user_id required'}), status=400)
        try:
            body['user_id'] = int(body['user_id'])
        except:
            return Response(json.dumps({'error': 'user_id must be an integer'}), status=400)
        print(body)
        try:
            user = User.query.get(body['user_id'])
            print(user.id)
            if user is None:
                return Response(json.dumps({'error': 'User not found'}), status=404)
        except:
            return Response(json.dumps({'error': 'User not found'}), status=404)
        follow = Following(
            user_id=self.current_user.id,
            following_id=user.id
        )
        try:
            db.session.add(follow)  # issues the insert statement
            db.session.commit()
        except:
            return Response(json.dumps({'error': 'Error creating follow'}), status=400)

        return Response(json.dumps(follow.to_dict_following()), mimetype="application/json", status=201)

class FollowingDetailEndpoint(Resource):
    def __init__(self, current_user):
        self.current_user = current_user
    
    def delete(self, id):
        # delete "following" record where "id"=id
        print(id)
        follow = Following.query.get(id)
        if follow is None:
            return Response(json.dumps({'error': 'Not Found'}), status=404)
        if self.current_user.id != follow.user_id:
            return Response(json.dumps({'error': 'You cannot delete this follow'}), status=404)
        try:
            Following.query.filter_by(id=id).delete()
            db.session.commit()
        except:
            return Response(json.dumps({'error': 'Error deleting follow'}), status=400)
        return Response(json.dumps({"message": "OK"}), mimetype="application/json", status=200)




def initialize_routes(api):
    api.add_resource(
        FollowingListEndpoint, 
        '/api/following', 
        '/api/following/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )
    api.add_resource(
        FollowingDetailEndpoint, 
        '/api/following/<int:id>', 
        '/api/following/<int:id>/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )

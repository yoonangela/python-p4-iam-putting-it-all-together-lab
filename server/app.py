#!/usr/bin/env python3

from flask import request, session, make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        json=request.json
        try:
            user = User(
                username=json['username'],
                image_url=json['image_url'],
                bio=json['bio']
            )
            user.password_hash = json['password']
            db.session.add(user)
            db.session.commit()
   
            session['user.id'] = user.id
            return user.to_dict(), 201
        
        except:
            return {'error': 'Unprocessable Entity'}, 422 



class CheckSession(Resource):
    def get(self):
        user = User.query.filter(User.id == session.get('user_id')).first()
        if user:
            return make_response(user.to_dict(), 200)
        else:
            return {'error': 'Unauthorized'}, 401


class Login(Resource):
    def post(self):
        json=request.json
        user = User.query.filter(User.username == json['username']).first()
        password = json['password']
        if user and user.authenticate(password):
            session['user_id'] = user.id
            return user.to_dict(), 200

        return {'error': 'Invalid username or password'}, 401 


class Logout(Resource):
    def delete(self):
        user = User.query.filter(User.id == session.get('user_id')).first()
        if user:
            session['user_id']=None
            return make_response("", 204)
        else:
            return {'error': 'not logged in'}, 401 
        

class RecipeIndex(Resource):
    def get(self):
        user = User.query.filter(User.id == session.get('user_id')).first()
        if user:
            recipes = user.recipes
            recipeslist = [recipe.to_dict() for recipe in recipes]
            return make_response(recipeslist, 200) 
        else:
            return {'error': 'unauthorized'}, 401 
    def post(self):
        json = request.json
        user = User.query.filter(User.id == session.get('user_id')).first()
        if not user:
            return {'error': 'Unauthorized'}, 401
        try:
            recipe = Recipe(
                title=json["title"], 
                instructions=json["instructions"],
                minutes_to_complete=json["minutes_to_complete"],
                user_id=user.id
            )
            db.session.add(recipe)
            db.session.commit()
            return make_response(recipe.to_dict(), 201)
        except Exception as e:
            return {'errors': [str(e)], 'message': 'Unprocessable Entity'}, 422



api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
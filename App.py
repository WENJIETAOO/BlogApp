#!/usr/bin/env python3
import sys
from flask import Flask, jsonify, abort, request, make_response, session
from flask_restful import reqparse, Resource, Api
from flask_session import Session
import json
from ldap3 import Server, Connection, ALL
import settings # Our server and db settings, stored in settings.py
import pymysql.cursors
from flask_cors import CORS 
import ssl

import cgitb
import cgi
import sys
cgitb.enable()

app = Flask(__name__, static_url_path="")
# Set Server-side session config: Save sessions in the local app directory.
app.secret_key = settings.SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'peanutButter'
app.config['SESSION_COOKIE_DOMAIN'] = settings.APP_HOST
Session(app)

class Root(Resource):
	def get(self):
		return app.send_static_file('index.html')



####################################################################################
#
# Error handlers
#
@app.errorhandler(400) # decorators to add to 400 response
def not_found(error):
	return make_response(jsonify( { 'status': 'Bad request' } ), 400)

@app.errorhandler(404) # decorators to add to 404 response
def not_found(error):
	return make_response(jsonify( { 'status': 'Resource not found' } ), 404)

####################################################################################
#
# Routing: GET and POST using Flask-Session
#
class SignIn(Resource):
	#
	# Login, start a session and set/return a session cookie
	#
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X POST -d '{"username": "wtao", "password": "SHANGhai001!"}' -c cookie-jar http://info3103.cs.unb.ca:35669/signin
	#
	def post(self):
		if not request.json:
			abort(400) # bad request
		# Parse the json
		parser = reqparse.RequestParser()
		try:
			# Check for required attributes in json document, create a dictionary
			parser.add_argument('username', type=str, required=True)
			parser.add_argument('password', type=str, required=True)
			request_params = parser.parse_args()
		except:
			abort(400) # bad request

		# Already logged in
		if request_params['username'] in session:
			response = {'status': 'success'}
			responseCode = 200
		else:
			try:
				ldapServer = Server(host=settings.LDAP_HOST)
				ldapConnection = Connection(ldapServer,
					raise_exceptions=True,
					user='uid='+request_params['username']+', ou=People,ou=fcs,o=unb',
					password = request_params['password'])
				ldapConnection.open()
				ldapConnection.start_tls()
				ldapConnection.bind()
				# At this point we have sucessfully authenticated.
				session['username'] = request_params['username']
				response = {'status': 'success' }
				responseCode = 201
			except:
				response = {'status': 'Access denied'}
				responseCode = 403
			finally:
				ldapConnection.unbind()

		return make_response(jsonify(response), responseCode)

	# GET: Check for a login
	#
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X GET -b cookie-jar http://info3103.cs.unb.ca:36403/signin
	def get(self):
		if 'username' in session:
			username=session.get('username')
			print(username)
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail'}
			responseCode = 403

		return make_response(jsonify(response), responseCode)

	# DELETE: Logout: remove session
	#
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X DELETE -b cookie-jar
	#	http://info3103.cs.unb.ca:61340/signin

	#
	#	Here's your chance to shine!
	#
	def delete(self):
		if 'username' in session:
			session.clear()
			response = {'status': 'success','message':'Bye'}
			responseCode = 200
		else:
			response = {'status': 'fail','message':'you can not logout'}
			responseCode = 403

		return make_response(jsonify(response), responseCode)
class Hello(Resource):
	def get(self):
		if 'username' in session:
			response = {'status': 'success', 'message': 'Hello ' +session['username']}
			responseCode = 200
		else:
			response = {'status': 'fail', 'message': 'Who are you?'}
			responseCode = 403

		return make_response(jsonify(response), responseCode)

####################################################################################
#
# Blog: GET and POST,DELETE
#
class Blog(Resource):
    # GET: Return all school resources
	#
	# Example request: curl -i -H "Content-Type: application/json" -X GET -b cookie-jar http://info3103.cs.unb.ca:36403/Blog
	def get(self):
		if 'username' in session:
			response = {'status': 'success'}
			responseCode = 200
			try:
				dbConnection = pymysql.connect(settings.MYSQL_HOST,
					settings.MYSQL_USER,
					settings.MYSQL_PASSWD,
					settings.MYSQL_DB,
					charset='utf8mb4',
					cursorclass= pymysql.cursors.DictCursor)
				sql = 'getAllBlog'
				cursor = dbConnection.cursor()
				cursor.callproc(sql) # stored procedure, no arguments
				row = cursor.fetchall() # get all the results
				if row is None:
	                		abort(404)
			except:
				abort(500) # Nondescript server error
			finally:
				cursor.close()
				dbConnection.close()
		else:
			response = {'status': 'fail'}
			responseCode = 403
		return make_response(jsonify({'AllBlog': row}), responseCode)
	#
	# Sample command line usage:
	#
	#  curl -i -H "Content-Type: application/json" -X POST -b cookie-jar -d '{"BlogText": "cr*ap"}' http://info3103.cs.unb.ca:36403/Blog
	def post(self):
		if not request.json or not 'BlogText' in request.json:
			abort(400) # bad request

		if 'username' in session:
			username=session.get('username')
			response = {'status': 'success'}
			BlogText = request.json['BlogText'];
			try:
				dbConnection = pymysql.connect(settings.MYSQL_HOST,
					settings.MYSQL_USER,
					settings.MYSQL_PASSWD,
					settings.MYSQL_DB,
					charset='utf8mb4',
					cursorclass= pymysql.cursors.DictCursor)
				sql = 'createBlog'
				cursor = dbConnection.cursor()
				cursor.callproc(sql,(username, BlogText)) # stored procedure, with arguments
				row = cursor.fetchone()
				dbConnection.commit() # database was modified, commit the changes


			except:
				abort(500) # Nondescript server error
			finally:
				cursor.close()

				dbConnection.close()



			uri = 'http://'+settings.APP_HOST+':'+str(settings.APP_PORT)
			uri = uri+str(request.url_rule)+'/'+str(row['LAST_INSERT_ID()'])
#return make_response(jsonify( { "schoolId" : row['LAST_INSERT_ID()'] } ), 201) # successful resource creation
			return make_response(jsonify( { "uri" : uri } ), 201) # successful resource creation

		else:
			response = {'status': 'fail'}
			responseCode = 403
			return make_response(jsonify(response), responseCode)


class Comment(Resource):

	# Sample command line usage:
	#
	#  curl -i -H "Content-Type: application/json" -X POST -b cookie-jar -d '{"BlogID": "", "CommentText": "cUUp"}' http://info3103.cs.unb.ca:36403/Comment
	def post(self):
		if not request.json:
			abort(400) # bad request
		if 'username' in session:
			username=session.get('username')
			response = {'status': 'success'}
			BlogID = request.json['BlogID'];
			CommentText = request.json['CommentText'];
			try:
				dbConnection = pymysql.connect(settings.MYSQL_HOST,
					settings.MYSQL_USER,
					settings.MYSQL_PASSWD,
					settings.MYSQL_DB,
					charset='utf8mb4',
					cursorclass= pymysql.cursors.DictCursor)
				sql = 'createComment'
				cursor = dbConnection.cursor()
				cursor.callproc(sql,(CommentText,BlogID,username))
				row = cursor.fetchone()
				dbConnection.commit()
			except:
				abort(500) # Nondescript server error
			finally:
				cursor.close()
				dbConnection.close()
			uri = 'http://'+settings.APP_HOST+':'+str(settings.APP_PORT)
			uri = uri+str(request.url_rule)+'/'+str(row['LAST_INSERT_ID()'])
	        #return make_response(jsonify( { "schoolId" : row['LAST_INSERT_ID()'] } ), 201) # successful resource creation
			return make_response(jsonify( { "uri" : uri } ), 201) # successful resource creation
		else:
			response = {'status': 'fail'}
			responseCode = 403
			return make_response(jsonify(response), responseCode)

class BlogResource(Resource):
    # GET: Return identified blog resource
	#
	# Example request: curl -i -H "Content-Type: application/json" -X GET -b cookie-jar http://info3103.cs.unb.ca:36403/Blog/3
	def get(self, BlogID):
		if 'username' in session:
			try:
				dbConnection = pymysql.connect(settings.MYSQL_HOST,
					settings.MYSQL_USER,
					settings.MYSQL_PASSWD,
					settings.MYSQL_DB,
					charset='utf8mb4',
					cursorclass= pymysql.cursors.DictCursor)
				sql = 'getBlog'
				cursor = dbConnection.cursor()
				cursor.callproc(sql,[BlogID]) # stored procedure, no arguments
				row = cursor.fetchall() # get all the results
				if row is None:
					abort(404)
			except:
				abort(500) # Nondescript server error
			finally:
				cursor.close()
				dbConnection.close()
			return make_response(jsonify({"blog": row}), 200) # successful
		else:
			response = {'status': 'fail'}
			responseCode = 403
			return make_response(jsonify(response), responseCode)

    # DELETE: Delete identified blog resource
    #
    # Example request: curl -i -H "Content-Type: application/json" -X DELETE -b cookie-jar http://info3103.cs.unb.ca:36403/Blog/2
	def delete(self, BlogID):
		if 'username' in session:
			username=session.get('username')
			response = {'status': 'success'}
			responseCode = 200
			try:
				dbConnection = pymysql.connect(settings.MYSQL_HOST,
					settings.MYSQL_USER,
					settings.MYSQL_PASSWD,
					settings.MYSQL_DB,
					charset='utf8mb4',
					cursorclass= pymysql.cursors.DictCursor)
				sql = 'DeleteBlog'
				cursor = dbConnection.cursor()
				cursor.callproc(sql,([BlogID],username)) # stored procedure, no arguments
				dbConnection.commit()
			except:
				abort(500) # Nondescript server error
			finally:
				cursor.close()
				dbConnection.close()
			return make_response(jsonify(response), responseCode) # turn set into json and return it
		else:
			response = {'status': 'fail'}
			responseCode = 403
			return make_response(jsonify(response), responseCode)

class CommentResource(Resource):
    # GET: Return identified blog resource
	#
	# Example request: curl -i -H "Content-Type: application/json" -X GET -b cookie-jar http://info3103.cs.unb.ca:36403/Comment/3
	def get(self, CommentID):
		if 'username' in session:
			try:
				dbConnection = pymysql.connect(settings.MYSQL_HOST,
					settings.MYSQL_USER,
					settings.MYSQL_PASSWD,
					settings.MYSQL_DB,
					charset='utf8mb4',
					cursorclass= pymysql.cursors.DictCursor)
				sql = 'getComment'
				cursor = dbConnection.cursor()
				cursor.callproc(sql,[CommentID]) # stored procedure, no arguments
				row = cursor.fetchall() # get all the results
				if row is None:
					abort(404)
			except:
				abort(500) # Nondescript server error
			finally:
				cursor.close()
				dbConnection.close()
			return make_response(jsonify({"Comment": row}), 200) # successful
		else:
			response = {'status': 'fail'}
			responseCode = 403
			return make_response(jsonify(response), responseCode)
    # DELETE: Delete identified blog resource
    #
    # Example request: curl -i -H "Content-Type: application/json" -X DELETE -b cookie-jar http://info3103.cs.unb.ca:36403/Comment/2
	def delete(self, CommentID):
		if 'username' in session:
			username=session.get('username')
			response = {'status': 'success'}
			responseCode = 200
			try:
				dbConnection = pymysql.connect(settings.MYSQL_HOST,
					settings.MYSQL_USER,
					settings.MYSQL_PASSWD,
					settings.MYSQL_DB,
					charset='utf8mb4',
					cursorclass= pymysql.cursors.DictCursor)
				sql = 'delComment'
				cursor = dbConnection.cursor()
				cursor.callproc(sql,([CommentID],username)) # stored procedure, no arguments
				dbConnection.commit()
			except:
				abort(500) # Nondescript server error
			finally:
				cursor.close()
				dbConnection.close()
			return make_response(jsonify(response), responseCode) # turn set into json and return it
		else:
			response = {'status': 'fail'}
			responseCode = 403
			return make_response(jsonify(response), responseCode)

class BlogCommentResource(Resource):
    # GET: Return all resources
	#
	# Example request: curl -i -H "Content-Type: application/json" -X GET -b cookie-jar http://info3103.cs.unb.ca:36403/Blog/Comment/13

	def get(self, BlogID):
		if 'username' in session:
			response = {'status': 'success'}
			responseCode = 200
			try:

				dbConnection = pymysql.connect(settings.MYSQL_HOST,
					settings.MYSQL_USER,
					settings.MYSQL_PASSWD,
					settings.MYSQL_DB,
					charset='utf8mb4',
					cursorclass= pymysql.cursors.DictCursor)
				sql = 'getAllComment'
				cursor = dbConnection.cursor()
				cursor.callproc(sql,[BlogID]) # stored procedure, no arguments
				row = cursor.fetchall() # get all the results
				if row is None:
	                		abort(404)
			except:
				abort(500) # Nondescript server error
			finally:
				cursor.close()
				dbConnection.close()
			return make_response(jsonify({'Comments': row}), 200) # turn set into json and return it

		else:
			response = {'status': 'fail'}
			responseCode = 403
			return make_response(jsonify(response), responseCode)

####################################################################################
#
# Identify/create endpoints and endpoint objects
#
api = Api(app)
api.add_resource(SignIn, '/signin')
api.add_resource(Hello, '/hello')
api.add_resource(Blog, '/Blog')
api.add_resource(Comment, '/Comment')
api.add_resource(BlogResource, '/Blog/<int:BlogID>')
api.add_resource(CommentResource, '/Comment/<int:CommentID>')
api.add_resource(BlogCommentResource, '/Blog/Comment/<int:BlogID>')
api.add_resource(Root, '/')
#############################################################################
# xxxxx= last 5 digits of your studentid. If xxxxx > 65535, subtract 30000
if __name__ == "__main__":
	context = ('cert.pem', 'key.pem')
	app.run(host=settings.APP_HOST, port=settings.APP_PORT, ssl_context=context, debug=settings.APP_DEBUG)

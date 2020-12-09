import mariadb
from flask import Flask, request, Response
import json 
import dbcreds
import random
import string
from flask_cors import CORS

def createLoginToken():
    letters = string.ascii_letters
    token_result = ''.join(random.choice(letters) for i in range(20))
    return token_result

app = Flask(__name__)
CORS(app)


@app.route('/api/users', methods=['GET','POST','PATCH','DELETE'])
def users():
    if request.method == 'POST':
        conn = None
        cursor = None
        user_username = request.json.get("username")
        user_email = request.json.get("email")
        user_password = request.json.get("password")
        rows = None

        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user(username,email,password) VALUES (?,?,?)", [user_username,user_email,user_password])
            rows = cursor.rowcount
            
            if(rows == 1):
                token_result = createLoginToken()
                userId = cursor.lastrowid
                cursor.execute("INSERT INTO user_session(loginToken,userId) VALUES (?,?)", [token_result, userId,])
                conn.commit()
                rows = cursor.rowcount

       
        except Exception as error:
            print("Something else went wrong: ")
            print(error)

    
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                user_information = {
                    "userId": userId,
                    "username": user_username,
                    "email":  user_email,
                    "loginToken": token_result,
                }
                return Response(json.dumps(user_information, default=str), mimetype="application/json", status=201)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)


@app.route('/api/login', methods=['POST','DELETE'])
def login():
    if request.method == 'POST':
        conn = None
        cursor = None
        rows = None
        user = None
        user_email = request.json.get("email")
        user_password = request.json.get("password")
        token_result = createLoginToken()
        
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, password, username FROM user WHERE email=? AND password=?",[user_email,user_password,])
            user = cursor.fetchall()
        
            if(len(user) == 1):
                cursor.execute("INSERT INTO user_session(loginToken, userId) VALUES(?,?)", [token_result,user[0][0],])
                conn.commit()
                rows = cursor.rowcount

        except Exception as error:
            print("Something else went wrong: ")
            print(error)

        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if(rows == 1):
                user_info = {
                    "id": user[0][0],
                    "email": user[0][1],
                    "username": user[0][3],
                    "loginToken": token_result,
                }
                return Response(json.dumps(user_info, default=str), mimetype="application/json", status=201)
            else:
                return Response("Login User Failed.", mimetype="text/html", status=500)

    if request.method == 'DELETE':
        conn = None
        cursor = None
        rows = None
        user = None
        user_loginToken = request.json.get("loginToken")
        
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_session WHERE loginToken=?",[user_loginToken,])
            conn.commit()
            rows = cursor.rowcount
            print(rows)

        except Exception as error:
            print("Something else went wrong: ")
            print(error)

        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if(rows == 1):
                return Response("Logged Out Succesfully!", mimetype="text/html", status=204)
            else:
                return Response("Logging Out Failed.", mimetype="text/html", status=500)
    

    
@app.route('/api/boards', methods=['GET','POST','DELETE'])
def boards():

    if request.method == 'POST':
        conn = None
        cursor = None
        login_token = request.json.get("loginToken")
        board_colours = request.json.get("colours")
        board_image = request.json.get("image")
        board_title = request.json.get("title")
        createdAt = datetime.datetime.now().strftime("%Y-%m-%d")
        rows = None

        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor() 
            cursor.execute("SELECT us.userId, u.username FROM user_session us INNER JOIN user u ON us.userId=u.id WHERE loginToken=?",[login_token,])
            user = cursor.fetchone()
            cursor.execute("INSERT INTO board(colours,image,title) VALUES (?,?,?)", [board_colours,board_image,board_title])
            conn.commit()
            rows = cursor.rowcount
            boardId = cursor.lastrowid

        except Exception as error:
            print("Something else went wrong: ")
            print(error)

        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                board_information = {
                    "id": boardId,
                    "title": board_title,
                    "colours": board_colours,
                    "image": board_image,
                    "createdAt": createdAt,
                    "userId": user[0],
                }
                return Response(json.dumps(board_information, default=str), mimetype="application/json", status=201)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)

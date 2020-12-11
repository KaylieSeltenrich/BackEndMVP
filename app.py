import mariadb
from flask import Flask, request, Response
import json 
import dbcreds
import random
import string
from flask_cors import CORS
import datetime

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

    if request.method == 'GET':
        conn = None
        cursor = None
        boards = None
        user_id = request.args.get("userId")
    
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            if(user_id == None):
                cursor.execute("SELECT user.username, b.title, b.image, b.createdAt, b.userId, b.colour1, b.colour2, b.colour3, b.colour4, b.colour5, b.colour6, b.colour7, b.colour8, b.colour9, b.colour10 FROM user INNER JOIN board b ON user.id=b.userId")
                boards = cursor.fetchall()
                print(boards)
    
            else: 
                cursor.execute("SELECT user.username, b.title, b.image, b.createdAt, b.userId, b.colour1, b.colour2, b.colour3, b.colour4, b.colour5, b.colour6, b.colour7, b.colour8, b.colour9, b.colour10 FROM user INNER JOIN board b ON user.id=b.userId WHERE userId=?",[user_id,])
                boards = cursor.fetchall()
                print(boards)
           
        except Exception as error:
            print("Something else went wrong: ")
            print(error)

        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(boards!= None):
                board_info = []
                for board in boards:
                    board_info.append({
                        "userId": board[4],
                        "username": board[0],
                        "title": board[1],
                        "image": board[2],
                        "createdAt": board[3],
                        "colour1": board[5],
                        "colour2": board[6],
                        "colour3": board[7],
                        "colour4": board[8],
                        "colour5": board[9],
                        "colour6": board[10],
                        "colour7": board[11],
                        "colour8": board[12],
                        "colour9": board[13],
                        "colour10": board[14],
                        })
                return Response(json.dumps(board_info, default=str), mimetype="application/json", status=200)
            else: 
                return Response("Something went wrong!", mimetype="text/html", status=500)


    elif request.method == 'POST':
        conn = None
        cursor = None
        login_token = request.json.get("loginToken")
        board_colours = request.json.get("colors")
        board_image = request.json.get("image")
        board_title = request.json.get("title")
        createdAt = datetime.datetime.now().strftime("%Y-%m-%d")
        rows = None

        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor() 
            cursor.execute("SELECT us.userId, u.username FROM user_session us INNER JOIN user u ON us.userId=u.id WHERE loginToken=?",[login_token,])
            user = cursor.fetchone()
            cursor.execute("INSERT INTO board(image,title,colour1,colour2,colour3,colour4,colour5,colour6,colour7,colour8,colour9,colour10,userId) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", [board_image,board_title,board_colours[0],board_colours[1],board_colours[2],board_colours[3],board_colours[4],board_colours[5],board_colours[6],board_colours[7],board_colours[8],board_colours[9],user[0]])
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
                    "image": board_image,
                    "title": board_title,
                    "colors": board_colours,
                    "createdAt": createdAt,
                    "userId": user[0],
                }
                return Response(json.dumps(board_information, default=str), mimetype="application/json", status=201)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
    
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        login_token = request.json.get("loginToken")
        board_id = request.json.get("id")
        rows = None

        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor() 
            cursor.execute("SELECT userId FROM user_session WHERE loginToken=?", [login_token,])
            user = cursor.fetchall()[0][0]
            cursor.execute("SELECT userId FROM board WHERE id=?", [board_id,])
            board_owner = cursor.fetchall()[0][0]
            if(user == board_owner):
                cursor.execute("DELETE FROM board WHERE id=?", [board_id,])
                conn.commit()
                rows = cursor.rowcount
            else:
                print("Unable to delete board.")

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
                return Response("Board Deleted Succesfully!", mimetype="text/html", status=204)
            else:
                return Response("Board not Deleted!", mimetype="text/html", status=500)

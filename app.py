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
    

    
@app.route('/api/boards', methods=['GET','POST','PATCH','DELETE'])
def boards():

    if request.method == 'GET':
        conn = None
        cursor = None
        boards = None
        user_id = request.args.get("userId")
        offset = request.args.get("offset")
    
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            if(user_id == None):
                cursor.execute("SELECT user.username, b.title, b.image, b.createdAt, b.userId, b.id, b.colour1, b.colour2, b.colour3, b.colour4, b.colour5, b.colour6, b.colour7, b.colour8, b.colour9, b.colour10 FROM user INNER JOIN board b ON user.id=b.userId ORDER BY b.id DESC LIMIT 5 OFFSET ?", [offset,])
                boards = cursor.fetchall()
            else: 
                cursor.execute("SELECT user.username, b.title, b.image, b.createdAt, b.userId, b.id, b.colour1, b.colour2, b.colour3, b.colour4, b.colour5, b.colour6, b.colour7, b.colour8, b.colour9, b.colour10 FROM user INNER JOIN board b ON user.id=b.userId WHERE userId=? ORDER BY b.id DESC LIMIT 5 OFFSET ?",[user_id,offset])
                boards = cursor.fetchall()
               
           
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
                        "id": board[5],
                        "username": board[0],
                        "title": board[1],
                        "image": board[2],
                        "createdAt": board[3],
                        "colour1": board[6],
                        "colour2": board[7],
                        "colour3": board[8],
                        "colour4": board[9],
                        "colour5": board[10],
                        "colour6": board[11],
                        "colour7": board[12],
                        "colour8": board[13],
                        "colour9": board[14],
                        "colour10": board[15],
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


    elif request.method == 'PATCH':
        conn = None
        cursor = None
        board_title = request.json.get("title")
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
                cursor.execute("UPDATE board SET title=? WHERE id=?", [board_title,board_id,])
                conn.commit()
                rows = cursor.rowcount
            else:
                print("Unable to update title")

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
                    "id": board_id,
                    "title": board_title
                }
                return Response(json.dumps(board_information, default=str), mimetype="application/json", status=200)
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

@app.route('/api/board-likes', methods=['GET','POST','DELETE'])
def boardLikes():
    if request.method == 'GET':
        conn = None
        cursor = None
        board_likes = None
        board_id = request.args.get("boardId")

        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            if(board_id == None):
                cursor.execute("SELECT u.username, u.id, bl.boardId FROM user u INNER JOIN board_like bl ON u.id=bl.userId")
                board_likes = cursor.fetchall()
            else:
                cursor.execute("SELECT u.username, u.id, bl.boardId FROM user u INNER JOIN board_like bl ON u.id=bl.userId WHERE bl.boardId=?", [board_id,])
                board_likes = cursor.fetchall()
 
        except Exception as error:
            print("Something else went wrong: ")
            print(error)

        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(board_likes != None):
                boardlike_info = []
                for board_like in board_likes:
                    boardlike_info.append({
                        "boardId": board_like[2],
                        "userId": board_like[1],
                        "username": board_like[0],
                        })
                return Response(json.dumps(boardlike_info, default=str), mimetype="application/json", status=200)
            else: 
                return Response("Something went wrong!", mimetype="text/html", status=500)

    elif request.method == 'POST':
        conn = None
        cursor = None
        board_id = request.json.get("id")
        login_token = request.json.get("loginToken")
        rows = None

        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT userId from user_session WHERE loginToken=?", [login_token,])
            user = cursor.fetchone()
            cursor.execute("SELECT username FROM user WHERE id=?", [user[0],])
            username = cursor.fetchone()
            cursor.execute("INSERT INTO board_like(boardId,userId) VALUES (?,?)", [board_id,user[0],])
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
                return Response("Liked Board!", mimetype="text/html", status=201)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
    
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        board_id = request.json.get("id")
        login_token = request.json.get("loginToken")
        rows = None

        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor() 
            cursor.execute("SELECT us.userId FROM user_session us INNER JOIN board_like bl ON us.userId=bl.userId WHERE loginToken=?",[login_token,])
            user = cursor.fetchone()
            cursor.execute("DELETE FROM board_like WHERE boardId=? AND userId=?", [board_id,user[0],])
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
                return Response("Board like removed successfully!", mimetype="text/html", status=204)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)


@app.route('/api/board-favourites', methods=['GET','POST','DELETE'])
def boardFavourites():
    if request.method == 'GET':
        conn = None
        cursor = None
        board_faves = None
        board_id = request.args.get("boardId")
        user_id = request.args.get("userId")
        offset = request.args.get("offset")

        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT u.username, u.id, bf.boardId, b.title, b.image, b.createdAt, b.userId, b.id, b.colour1, b.colour2, b.colour3, b.colour4, b.colour5, b.colour6, b.colour7, b.colour8, b.colour9, b.colour10 FROM user u INNER JOIN board_favourite bf ON u.id=bf.userId INNER JOIN board b ON b.id = bf.boardId WHERE u.id=? ORDER BY b.id DESC LIMIT 5 OFFSET ?", [user_id,offset])
            board_faves = cursor.fetchall()
 
        except Exception as error:
            print("Something else went wrong: ")
            print(error)

        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(board_faves != None):
                boardfave_info = []
                for board_fave in board_faves:
                    boardfave_info.append({
                        "boardId": board_fave[2],
                        "userId": board_fave[1],
                        "username": board_fave[0],
                        "title": board_fave[3],
                        "image": board_fave[4],
                        "createdAt": board_fave[5],
                        "colour1": board_fave[8],
                        "colour2": board_fave[9],
                        "colour3": board_fave[10],
                        "colour4": board_fave[11],
                        "colour5": board_fave[12],
                        "colour6": board_fave[13],
                        "colour7": board_fave[14],
                        "colour8": board_fave[15],
                        "colour9": board_fave[16],
                        "colour10": board_fave[17],
                        })
                return Response(json.dumps(boardfave_info, default=str), mimetype="application/json", status=200)
            else: 
                return Response("Something went wrong!", mimetype="text/html", status=500)

    elif request.method == 'POST':
        conn = None
        cursor = None
        board_id = request.json.get("id")
        login_token = request.json.get("loginToken")
        rows = None

        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT userId from user_session WHERE loginToken=?", [login_token,])
            user = cursor.fetchone()
            cursor.execute("SELECT username FROM user WHERE id=?", [user[0],])
            username = cursor.fetchone()
            cursor.execute("INSERT INTO board_favourite(boardId,userId) VALUES (?,?)", [board_id,user[0],])
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
                return Response("Favourited Board!", mimetype="text/html", status=201)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
    
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        board_id = request.json.get("id")
        login_token = request.json.get("loginToken")
        rows = None

        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor() 
            cursor.execute("SELECT us.userId FROM user_session us INNER JOIN board_favourite bf ON us.userId=bf.userId WHERE loginToken=?",[login_token,])
            user = cursor.fetchone()
            cursor.execute("DELETE FROM board_favourite WHERE boardId=? AND userId=?", [board_id,user[0],])
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
                return Response("Board favourite removed successfully!", mimetype="text/html", status=204)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)

                

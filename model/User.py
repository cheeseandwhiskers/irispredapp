from model.DatabasePool import DatabasePool
from config.Settings import Settings
import datetime
import bcrypt

import jwt
class User:
    @classmethod
    def getUser(cls,email): 
        try:
            dbConn=DatabasePool.getConnection()
            cursor = dbConn.cursor(dictionary=True)

            sql="select * from user where email=%s"

            cursor.execute(sql,(email,))
            users=cursor.fetchall()
            return users
        finally:
            dbConn.close()


    @classmethod
    def getAllUsers(cls): 
        try:
            dbConn=DatabasePool.getConnection()
            cursor = dbConn.cursor(dictionary=True)

            sql="select * from user"

            cursor.execute(sql)
            users=cursor.fetchall()
            return users
        finally:
            dbConn.close()

    @classmethod
    def insertUser(cls,username,email,role,password): 
        try:
            dbConn=DatabasePool.getConnection()
            cursor = dbConn.cursor(dictionary=True)

            # Hash a password for the first time, with a randomly generated salt
            password=password.encode('utf8')
            hashed=bcrypt.hashpw(password,bcrypt.gensalt())

            sql="insert into user(username,email,role,password) values(%s,%s,%s,%s)"
            cursor.execute(sql,(username,email,role,hashed))
            
            dbConn.commit()
            count=cursor.rowcount

            return count
        finally:
            dbConn.close()


    @classmethod
    def updateUser(cls,userid,email): 
        try:
            dbConn=DatabasePool.getConnection()
            cursor = dbConn.cursor(dictionary=True)

            sql="update User set email=%s where userid=%s"
            cursor.execute(sql,(email,userid))
            
            dbConn.commit()
            count=cursor.rowcount

            return count
        finally:
            dbConn.close()



    @classmethod
    def deleteUser(cls,userid): 
        try:
            dbConn=DatabasePool.getConnection()
            cursor = dbConn.cursor(dictionary=True)

            sql="delete from user where userid=%s"
            cursor.execute(sql,(userid,))
            
            dbConn.commit()
            count=cursor.rowcount

            return count
        finally:
            dbConn.close()

    @classmethod
    def loginUser(cls,email,password): 
        try:
            result={}

            dbConn=DatabasePool.getConnection()
            cursor = dbConn.cursor(dictionary=True)

            sql="select * from user where email=%s"

            cursor.execute(sql,(email,))
            founduser=cursor.fetchone()

            print('founduser {}'.format(founduser))
            if(founduser): #User data found for given email
                if bcrypt.checkpw(password.encode('utf8'),founduser['password'].encode('utf8')):
                    print("Password VERIFIED for {}".format(founduser['username']))
                    payload={"username":founduser["username"],"userid":founduser["userid"],"role":founduser["role"],"iat": datetime.datetime.utcnow(),"exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=7200)}
                    token=jwt.encode(payload,Settings.secret,algorithm="HS256")
                    username=founduser["username"]
                else:
                    print("Password does not match for {}".format(founduser['username']))
                    token=''
                    username=''
            else: #No user data found for given email
                token=''
                username=''

            result['token']=token
            result['username']=username
            
            #return token, username
            return result
        
        finally:
            dbConn.close()


    # @classmethod
    # def getPredictionsByUserId(cls,userid):
    #     try:
    #         dbConn=DatabasePool.getConnection()
    #         cursor = dbConn.cursor(dictionary=True)
    #         sql="select * from irisprediction p inner join user u on p.userid=u.userid and p.userid=%s"
            
    #         cursor.execute(sql,(userid,))
    #         furnitures=cursor.fetchall()
    #         return furnitures
    #     finally:
    #         dbConn.close()
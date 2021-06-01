from model.DatabasePool import DatabasePool
from config.Settings import Settings
import datetime
import bcrypt
import jwt

class Prediction:

    @classmethod
    def getPredictionsByPredId(cls,predid):
        try:
            dbConn=DatabasePool.getConnection()
            cursor = dbConn.cursor(dictionary=True)
            #sql="select * from irisprediction p inner join user u on p.userid=u.userid and p.userid=%s"
            sql="select * from irisprediction p where p.predictionId=%s"
            
            cursor.execute(sql,(predid,))
            predictions=cursor.fetchall()
            return predictions
        finally:
            dbConn.close()

    @classmethod
    def getAllPredictionsByUserId(cls,userid): 
        try:
            dbConn=DatabasePool.getConnection()
            cursor = dbConn.cursor(dictionary=True)

            #sql="select * from irisprediction p inner join user u on p.userid=u.userid and p.userid=%s"
            sql="select * from irisprediction p where p.userid=%s and p.deleted=FALSE"

            cursor.execute(sql,(userid,))
            predictions=cursor.fetchall()
            return predictions
        finally:
            dbConn.close()


    @classmethod
    def getPredictionById(cls,predid): 
        try:
            dbConn=DatabasePool.getConnection()
            cursor = dbConn.cursor(dictionary=True)

            sql="select * from irisprediction p where p.predictionId=%s and p.deleted=FALSE"

            cursor.execute(sql,(predid,))
            prediction=cursor.fetchall()
            return prediction
        finally:
            dbConn.close()

    @classmethod
    def insertPrediction(cls,userid,sepalLen,sepalWid,petalLen,petalWid,prediction): 
        try:
            dbConn=DatabasePool.getConnection()
            cursor = dbConn.cursor(dictionary=True)

            sql="insert into irisprediction(userid,sepalLength,sepalWidth,petalLength,petalWidth,prediction) values(%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql,(userid,sepalLen,sepalWid,petalLen,petalWid,prediction))
            
            dbConn.commit()
            count=cursor.rowcount

            return count
        finally:
            dbConn.close()


    @classmethod
    def updatePrediction(cls,userid,predid): 
        try:
            dbConn=DatabasePool.getConnection()
            cursor = dbConn.cursor(dictionary=True)

            sql="update irisprediction set prediction=%s where userid=%s and predictionId=%s and deleted=FALSE"
            cursor.execute(sql,(userid,predid))
            
            dbConn.commit()
            count=cursor.rowcount

            return count
        finally:
            dbConn.close()



    @classmethod
    def deletePrediction(cls,userid,predid): 
        try:
            dbConn=DatabasePool.getConnection()
            cursor = dbConn.cursor(dictionary=True)

            #sql="delete from irisprediction where userid=%s and predid=%s"
            sql="update irisprediction set deleted=TRUE where userid=%s and predictionId=%s and deleted=FALSE"
            cursor.execute(sql,(userid,predid))
            
            dbConn.commit()
            count=cursor.rowcount

            return count
        finally:
            dbConn.close()
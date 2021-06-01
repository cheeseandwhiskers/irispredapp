# AI App Development
# Practical 8
# Python Flask

from flask import Flask,jsonify,request,g,render_template,make_response
from jinja2 import TemplateNotFound
from model.User import User
from model.Prediction import Prediction
from data.DataConfig import DataConfig
from validation.Validator import *
from datetime import datetime
# import numpy as np
# import re #regular expressions
# import bcrypt
import pickle, sklearn
from flask_cors import CORS # For development only

app = Flask(__name__)
CORS(app) # For development only; to overcome Cross Origin Scripting issue

@app.route('/')
def home_page():
    try:
        returnData={'message':'{}'.format(datetime.now())}
        return render_template("home.html",data=returnData)
    except Exception as err:
        # print(err)
        # returnData={"message":"Error!!"}
        # return jsonify(returnData),500
        # #return render_template("home.html",data=returnData),500
        print(err)
        returnData={"message":"Error!!"}
        resp = make_response(render_template("home.html",data=returnData),500)
        resp.delete_cookie('jwt')
        return resp

##Register##
@app.route('/register')
def register_page():
    try:
        returnData={}
        return render_template("register.html",data=returnData),200
    except Exception as err:
        # print(err)
        # returnData={"message":"Error!!"}
        # #return jsonify(returnData),500
        # return render_template("home.html",data=returnData),500
        print(err)
        returnData={"message":"Error!!"}
        resp = make_response(render_template("home.html",data=returnData),500)
        resp.delete_cookie('jwt')
        return resp

@app.route('/registerUser', methods=['POST'])
@validateRegister
def registerUser(*args,**kwargs):
    try:
        returnData={}
        msg=[]
        returnCode=0
        returnPath=''

        #retrieve form input values
        formInput={}
        formInput['username'] = request.form['register_username'].strip()
        formInput['email'] = request.form['register_email'].strip()
        formInput['password'] = request.form['register_password'].strip()
        role='user'
        print('formInput: ',formInput)

        if 'validated' in kwargs:
            print('validation results: {}'.format(kwargs['validated']))
            if kwargs['validated']:
                #Validation was successful

                #check if email has already been registered
                results=User.getUser(formInput['email'])
                print('results',results)
                if results:
                    print(len(results),' users found with email ',formInput['email'])
                    msg.append('E-mail address already registered. Please choose another.')
                    returnCode=400
                    returnPath='register.html'
                    #raise Exception('E-mail address already registered')
                else:
                    print('proceeding with registration')
                    count=User.insertUser(formInput['username'],formInput['email'],role,formInput['password'])
                    if count==1:
                        # insert success
                        print('Registration success for {}'.format(formInput['email']))
                        msg.append("Registration success! {} {} account(s) created".format(str(count),role))
                        returnCode=200
                        returnPath='login.html'
                        #return jsonify(returnData),201
                    else:
                        # insert failed
                        print('Registration failed for {}'.format(formInput['email']))
                        msg.append("Registration failed!")
                        returnCode=500
                        returnPath='home.html'
                        #return jsonify(returnData),200
            else:
                #Validation failed
                msg.append(kwargs['message'])
                returnCode=400
                returnPath='register.html'
                # resp=make_response(render_template("predict.html",data=returnData),400)
                # return resp
        else:
            # Validation status not found
            msg.append('Validation error. Aborted.')
            returnCode=500
            returnPath='home.html'
        
        returnData={
                    "message":'; '.join(msg),
                    #"message":msg,
                    "details":kwargs['details'],
                    "formInput":formInput
                    }
        resp=make_response(render_template(returnPath,data=returnData),returnCode)
        return resp
    except Exception as err:
        # print(err)
        # returnData={"message":"Error!!"}
        # #return jsonify(message),500
        # return render_template("home.html",data=returnData),500
        print(err)
        returnData={"message":"Error!!"}
        resp = make_response(render_template("home.html",data=returnData),500)
        resp.delete_cookie('jwt')
        return resp



    #     print("register form:",request.form)
    #     username = request.form['register_username']
    #     email = request.form['register_email']
    #     password = request.form['register_password']
    #     role="user"

    #     count=User.insertUser(username,email,role,password)
    #     if count==1:
    #         #register success
    #         print('Registration success {}'.format(email))
    #         returnData={"message":"Registration success! "+str(count)+" records modified"}
    #         return jsonify(returnData),201
    #     else:
    #         print('Registration failed {}'.format(email))
    #         returnData={"message":"Registration failed! "+str(count)+" records modified"}
    #         return jsonify(returnData),200
    # except Exception as err:
    #     print(err)
    #     returnData={"message":"Error!!"}
    #     #return jsonify(message),500
    #     return render_template("home.html")






##Login##
@app.route('/login')
def login_page():
    return render_template("login.html")

@app.route('/verifyUser', methods=['POST'])
def login():
    try:
        #print("login form:",request.form)
        # jsonBody=request.json
        # print('jsonBody:',jsonBody)
        # email =jsonBody['login_email']
        # password=jsonBody['login_password']

        email = request.form['login_email']
        password = request.form['login_password']
        #print(email, password)

        result=User.loginUser(email,password)

        token=result['token']
        username=result['username']

        print("token[{}]".format(token))
        if token=="":
            #login failed
            returnData={'message':'Invalid Login Credentials'}
            return render_template("login.html",data=returnData),200
        else:
            #login success
            returnData={'message':'Login success'
                        #,"jwt":token
                        }
            g.username=username
            #return jsonify(message),200
            # #multiplication table
            # data=list(range(1,6))
            # data2=[i * 5 for i in data]
            # data3=list(zip(data,data2))

            #return render_template("mainPage.html",username=username,message=message),200
            
            resp=make_response(render_template("mainPage.html",data=returnData),200)
            resp.set_cookie('jwt', token.encode('utf8'))
            return resp
            
    except Exception as err:
        # print(err)
        # returnData={"message":"Error!!"}
        # #return jsonify(message),500
        # return render_template("home.html")
        print(err)
        returnData={"message":"Error!!"}
        resp = make_response(render_template("home.html",data=returnData),500)
        resp.delete_cookie('jwt')
        return resp

@app.route('/userHome')
@login_required #apply decorator login_required 
def userhome_page():
    returnData={}
    resp = make_response(render_template("mainPage.html",data=returnData),200)
    return resp

##Logout
@app.route('/logout')
def logout():
    returnData={'message':'Logout success'}
    resp = make_response(render_template("login.html",data=returnData),200)
    resp.delete_cookie('jwt')
    return resp

##Prediction
@app.route('/predict')
@login_required #apply decorator login_required 
def predict_page():
    try:
        print('predict_page > userid: ',g.userid)

        # load target_names
        target_names=DataConfig.target_names
        # get user's prediction history
        results=Prediction.getAllPredictionsByUserId(g.userid)
        #print('predict_page > predictions_history: ', results)

        returnData={
                    "message":"{} prediction history records found".format(len(results)),
                    "target_names":target_names,
                    "history_predictions":results
                    }
        resp=make_response(render_template("predict.html",data=returnData),200)
        return resp
        #return jsonify(message),200
    except Exception as err:
        # print(err)
        # returnData={
        #             "message":err
        #             }
        # #return jsonify(message),500
        # return render_template("home.html",data=returnData),500
        print(err)
        returnData={"message":"Error!!"}
        resp = make_response(render_template("home.html",data=returnData),500)
        resp.delete_cookie('jwt')
        return resp

    #return render_template("predict.html")

@app.route('/doPrediction', methods=['POST'])
@login_required #apply decorator login_required 
@validatePrediction
def predict(*args,**kwargs):
    print('inside predict()')
    # print('\nargs',args)
    # print('\nkwargs',kwargs)
    try:
        returnData={}
        msg=[]
        returnCode=0

        #retrieve form input values
        formInput={}
        formInput['sl']=request.form['sepal_length'].strip()
        formInput['sw']=request.form['sepal_width'].strip()
        formInput['pl']=request.form['petal_length'].strip()
        formInput['pw']=request.form['petal_width'].strip()
        print('formInput: ',formInput)

        if 'validated' in kwargs:
            print('validation results: {}'.format(kwargs['validated']))
            if kwargs['validated']:
                #Validation was successful
                #print("doPrediction>prediction form:",request.form)
                sepal_length = float(formInput['sl'])
                sepal_width = float(formInput['sw'])
                petal_length = float(formInput['pl'])
                petal_width = float(formInput['pw'])

                #Load pickle file and perform prediction
                loaded_model = pickle.load( open( "iris_trained_model.pkl", "rb" ) )
                x_test=[[sepal_length, sepal_width, petal_length, petal_width]]
                #Let's do a prediction and compare the results
                y_pred = loaded_model.predict(x_test)
                #print('prediction x_test:',x_test)
                #print('prediction y_pred',y_pred)

                target_names=DataConfig.target_names
                msg.append('Prediction result: {}'.format(target_names[int(y_pred[0])]))

                # insert prediction into database
                count=Prediction.insertPrediction(g.userid,sepal_length,sepal_width,petal_length,petal_width,int(y_pred[0]))

                if count==1:
                    #insert prediction success
                    msg.append('{} Prediction(s) saved.'.format(str(count)))
                    returnCode=200
                else:
                    #insert failure
                    msg.append('{} Prediction(s) failed to save.'.format(str(count)))
                    returnCode=500
            else:
                #Validation failed
                msg.append(kwargs['message'])
                returnCode=400
                # resp=make_response(render_template("predict.html",data=returnData),400)
                # return resp
        else:
            #Validation status not found
            # returnData={
            #             "message":'Validation error. Aborted.',
            #             "target_names":target_names,
            #             "history_predictions":results
            #             }
            msg.append('Validation error. Aborted.')
            returnCode=500
        
        #load target names
        target_names=DataConfig.target_names
        #Load prediction history for user
        results=Prediction.getAllPredictionsByUserId(g.userid)
        #print('predict_page > predictions_history: ', results)
        print('details',kwargs['details'])
        returnData={
                    "message":'; '.join(msg),
                    "details":kwargs['details'],
                    "target_names":target_names,
                    "history_predictions":results,
                    "formInput":formInput
                    }
        resp=make_response(render_template("predict.html",data=returnData),returnCode)
        return resp
    except Exception as err:
        print(err)
        returnData={"message":"Error!!"}
        resp = make_response(render_template("home.html",data=returnData),500)
        resp.delete_cookie('jwt')
        return resp
        #return jsonify(message),500
        #return render_template("home.html",data=returnData),500

@app.route('/deletePrediction/id/<int:predid>', methods=['GET'])
@login_required #apply decorator login_required 
def deletePrediction(predid):
    print('deletePrediction > userid: ',g.userid)
    print('deletePrediction > predid: ',predid)
    try:
        count=Prediction.deletePrediction(g.userid,predid)
        print('deletePrediction > affected rowcount: ', count)
        
        if count<1:
            #delete failed
            print('delete Prediction Failed')
        else:
            print('{} predictions of Id[{}] deleted'.format(str(count),str(predid)))
        
        #load target names
        target_names=DataConfig.target_names
        results=Prediction.getAllPredictionsByUserId(g.userid)
        returnData={
                    "message":"{} prediction history record(s) deleted".format(count),
                    "target_names":target_names,
                    "history_predictions":results
                    }
        resp=make_response(render_template("predict.html",data=returnData),200)
        return resp
        #return jsonify(returnData),200
    except Exception as err:
        print(err)
        returnData={"message":"Error!!"}
        resp = make_response(render_template("home.html",data=returnData),500)
        resp.delete_cookie('jwt')
        return resp
        #return jsonify(message),500
        #return render_template("home.html",data=returnData),500

# Route any direct page links to home page and delete jwt from cookie
@app.route('/<string:filename>')
def default(filename):
    returnData={"message":"Error!!"}
    resp = make_response(render_template("home.html",data=returnData),400)
    resp.delete_cookie('jwt')
    return resp

#Activity: Create a new route which can show the content of any general file the user request
#@app.route('/<string:filename>')
def anypage(filename):
    #Activity: Modify the route to catch templateNotFound Exceptions with try except
    try:
        return render_template(filename)
    except TemplateNotFound as e:
        print('TemplateNotFound Exception! [{}]'.format(e))
        returnData={"message":"Error!!"}
        return render_template("404.html",data=returnData),404
    except Exception as err:
        print(err)
        returnData={"message":"Error!!"}
        #return jsonify(message),500
        return render_template("home.html",data=returnData),500


if __name__ == "__main__":
    app.run(debug=True)

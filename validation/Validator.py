import functools
from flask import jsonify,request,g,make_response,render_template
from config.Settings import Settings
import jwt
import re

def login_required(func):   #func->insertUsers
    @functools.wraps(func)
    def checkLogin(*args, **kwargs):
        auth=False
        # auth=True
        # auth_header = request.headers.get('Authorization') #retrieve authorization bearer token
        # print('auth_header: [{}]'.format(auth_header))
        # # Token JWTValue
        # if auth_header: 
        #     auth_token = auth_header.split(" ")[1]#retrieve the JWT value without the Bearer 
        # else:
        #     auth_token = ''
        #     auth=False #Failed check

        # retrieve jwt token from cookie
        auth_token=request.cookies.get("jwt")
        #print('login_required > auth_token: [{}]'.format(auth_token))
        
        if auth_token:
            try:
                payload = jwt.decode(auth_token,Settings.secret,algorithms=['HS256'])
                #decode may throw an error if the jwt signature is invalid

                # # check for token expiry
                # iat=payload['iat']
                # exp=payload['exp']
                # print('iat',iat)
                # print('exp',exp)

                g.role=payload['role']
                g.userid=payload['userid']
                g.username=payload['username']

                auth=True

            except jwt.exceptions.InvalidSignatureError as err:
                print(err)
                #auth=False #Failed check
            except jwt.exceptions.ExpiredSignatureError as err:
                print(err)
                #auth=False
            except Exception as err:
                print(err)
                #auth=False
        else:
            # jwt token not found in cookie
            print('jwt token not found in cookie')
            #auth=False #failed check

        if(auth==False):
            returnData={"message":"Invalid or missing token. Please login again."}
            # #return jsonify(message),401
            # resp.delete_cookie('jwt')
            # return redirect("/")
            resp = make_response(render_template("login.html",data=returnData),500)
            resp.delete_cookie('jwt')
            return resp
        else:
            print('authorization ok')
            value = func(*args, **kwargs)
            return value
    return checkLogin

#2 Create another new decorator require_admin that checks that the user is an admin (through the data in the JWT payload).
def require_admin(func):
    @functools.wraps(func)
    def checkAdmin(*args, **kwargs):
        
        print('g.role[{}]'.format(g.role))
        if g.role.upper()=='ADMIN':
            value = func(*args, **kwargs)
        else:
            message={"message":"Invalid role!"}
            return jsonify(message),401
        
        return value
    return checkAdmin

#3 Create a new decorator @require_isAdminOrSelf
def require_isAdminOrSelf(func):
    @functools.wraps(func)
    def isAdminOrSelf(*args, **kwargs):
        
        userid=''
        #print(kwargs)
        try:
            userid=kwargs['userid']
        except Exception as e:
            print(e)
        
        print('userid[{}]'.format(userid))
        print('g.role[{}]'.format(g.role))
        print('g.userid[{}]'.format(g.userid))
        if userid==g.userid or g.role.upper()=='ADMIN':
            value = func(*args, **kwargs)
        else:
            message={"message":"Unauthorized access!"}
            return jsonify(message),401
        
        return value
    return isAdminOrSelf

## function used in decorator for validation
def validateRegister(func):
    @functools.wraps(func)
    def validate(*args, **kwargs):
        # username = request.json['username']
        # email = request.json['email']
        # role = request.json['role']
        # password = request.json['password']

        # retrieve input values from form
        username = request.form['register_username'].strip()
        email = request.form['register_email'].strip()
        password = request.form['register_password'].strip()
        role = ''

        # regex to check inputs
        # alphanumeric min:8 max:40 chars
        patternUsername=re.compile('^[a-zA-Z0-9\s]{8,40}$')
        # email min:5 max:100
        patternEmail=re.compile('^(?=.{5,100}$)[\w]+@\w+[\.]{1}\w+$')
        # alphanumeric password min: 8 chars
        patternPassword=re.compile('^[a-zA-Z0-9]{8,16}$')

        # list of string names of problem inputs
        problems=[]
        # list of string descriptions of problem details

        # do the regex matching
        username_match=patternUsername.match(username)
        email_match=patternEmail.match(email)
        password_match=patternPassword.match(password)

        print('username',username,username_match)
        print('email',email,email_match)
        print('password',password,password_match)

        # if regex match fails, add input name to problems list
        if username_match is None:
            problems.append('Username (Valid characters: Letters, numbers, space. Minimum length 8, maximum length 40.)')
        if email_match is None:
            problems.append('E-mail (Must be valid email address. Minimum length 5, maximum length 100.)')
        if password_match is None:
            problems.append('Password (Valid characters: Letters, numbers. Minimum length 8, maximum length 16.)')

        if len(problems)<=0:
            # Validation passed, proceed with prediction
            validationResults={'validated':True,'message':'Input validation OK','details':problems}
        else:
            #validationResults={'validated':False,'message':'Input validation failed. Check inputs ['+(', '.join(problems))+']'}
            validationResults={'validated':False,'message':'Input validation failed. Check inputs.','details':problems}
        
        return func(*args,**validationResults,**kwargs)

        # if (patternUsername.match(username) and patternEmail.match(email) and patternPassword.match(password)):
        #     return func(*args,**kwargs)
        # else:
        #     #return jsonify({'message':'Validation failed'}),403
        #     return redirect("home.html")
    return validate


##Validate Prediction
## function used in decorator for validation
def validatePrediction(func):
    @functools.wraps(func)
    def validate(*args, **kwargs):
        
        # retrieve input values from form
        sepal_length = request.form['sepal_length'].strip()
        sepal_width = request.form['sepal_width'].strip()
        petal_length = request.form['petal_length'].strip()
        petal_width = request.form['petal_width'].strip()

        # regex to check for positive numeric values
        patternMeasurement=re.compile('(?=.+)^[0-9]+[\.]?[0-9]*$')

        # list of string names of problem inputs
        problems=[]

        # do the regex matching
        sl_match=patternMeasurement.match(sepal_length)
        sw_match=patternMeasurement.match(sepal_width) 
        pl_match=patternMeasurement.match(petal_length)
        pw_match=patternMeasurement.match(petal_width)

        # if regex match fails, add input name to problems list
        if sl_match is None:
            problems.append('Sepal Length')
        if sw_match is None:
            problems.append('Sepal Width')
        if pl_match is None:
            problems.append('Petal Length')
        if pw_match is None:
            problems.append('Petal Width')
        
        # print('sepal_length',sepal_length,sl_match)
        # print('sepal_width',sepal_width,sw_match)
        # print('petal_length',petal_length,pl_match)
        # print('petal_width',petal_width,pw_match)
        # print('problems',problems)

        if len(problems)<=0:
            # Validation passed, proceed with prediction
            validationResults={'validated':True,'message':'Input validation OK','details':problems}
        else:
            #validationResults={'validated':False,'message':'Input validation failed. Check inputs ['+(', '.join(problems))+']'}
            validationResults={'validated':False,'message':'Input validation failed. Check inputs.','details':problems}
        
        return func(*args,**validationResults,**kwargs)
        # else:
        #     #return jsonify({'message':'Validation failed'}),403
        #     #message={'message':'Validation failed: Please input positive numeric values only'}
        #     #print(message)
        #     #return jsonify(message)
        #     returnData={
        #             'message':'Validation failed: Please input positive numeric values only'
        #             #,"target_names":target_names
        #             #,"history_predictions":results
        #             }
        #     resp=make_response(render_template("predict.html",data=returnData),200)
        #     return resp
        #     #return redirect("home.html")
    return validate

'''
import functools

def decoratorName(func):
    @functools.wraps(func)
    def wrapper_decoratorName(*args, **kwargs):
        # Do something before
        value = func(*args, **kwargs)
        # Do something after
        return value
    return wrapper_decorator
'''
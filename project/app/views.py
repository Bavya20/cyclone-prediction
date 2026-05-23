from django.shortcuts import render, redirect
from django.contrib import messages 
from app.models import Cyclone
from django.contrib.auth.hashers import make_password, check_password 
from django.contrib.auth import logout 
import pandas as pd 
from imblearn.over_sampling import SMOTE 
from sklearn.model_selection import train_test_split 
from sklearn.ensemble import RandomForestClassifier 
from sklearn.metrics import accuracy_score 
from xgboost import XGBClassifier 
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

# Create your views here.

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirmPassword = request.POST.get('confirmPassword')
        contact = request.POST.get('contact')
        address = request.POST.get('address')
        country = request.POST.get('country')
        print(name, email, password, confirmPassword, contact, address, country)

        if password == confirmPassword:
            if Cyclone.objects.filter(email=email).exists():
                messages.error(request, f"This Email ID Already Exists, Please Try Another")
                return redirect('register')
            else: 
                hash_password = make_password(password)
                queryset = Cyclone(name=name, email=email, password=hash_password, contact=contact, address=address, country=country)
                queryset.save()
                messages.success(request, f"User Registration Successfully Completed, Thank You")
                return redirect('login')
        else: 
            messages.error(request, f"Password and Confirm Password do not match, Try Again")
            return redirect('register')

    return render(request, 'register.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = Cyclone.objects.filter(email=email).first()
        if user:
            if check_password(password, user.password):
                messages.success(request, f"User Login Successfully")
                return redirect('home')
            else: 
                messages.error(request, f"Invalid Password, Try Again")
                return redirect('login')
        else:
            messages.error(request, f"User not found, Please Register")
            return redirect('login')
    return render(request, 'login.html')

def home(request):
    return render(request, 'home.html') 

def view_dataset(request):
    df = pd.read_csv('app/final_dataset.csv')
    column = df.head(200).to_html()
    return render(request, 'view_dataset.html', {'col':column}) 

df = pd.read_csv('app/final_dataset.csv')
x = df.drop('Cyclone Direction', axis=1)
y = df['Cyclone Direction'] 

smote = SMOTE(random_state=42)
x,y = smote.fit_resample(x,y)
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)

def model_train(request):
    if request.method == 'POST':
        algorithm = request.POST.get('algorithm')

        if algorithm == '1':
            rf = RandomForestClassifier()
            rf.fit(x_train, y_train)
            pred = rf.predict(x_test)
            accuracy = accuracy_score(pred, y_test)
            accuracy = round(accuracy, 4)
            msg = f"Accuracy Score of Random Forest is {accuracy}"
            return render(request, 'model_train.html', {'msg':msg})
        
        elif algorithm == '2':
            xgb = XGBClassifier()
            xgb.fit(x_train, y_train)
            pred = xgb.predict(x_test)
            accuracy = accuracy_score(pred, y_test)
            accuracy = round(accuracy, 4)
            msg = f"Accuracy Score of XGBOOST is {accuracy}"
            return render(request, 'model_train.html', {'msg':msg})
        
        elif algorithm == '3':
            X_train = np.array(x_train).reshape((x_train.shape[0], 1, x_train.shape[1]))
            X_test = np.array(x_test).reshape((x_test.shape[0], 1, x_test.shape[1]))

            model = Sequential()
            model.add(LSTM(64, input_shape=(X_train.shape[1], X_train.shape[2]), return_sequences=True))
            model.add(Dropout(0.2))
            model.add(LSTM(32))
            model.add(Dropout(0.2))
            model.add(Dense(32, activation='relu'))
            model.add(Dense(len(np.unique(y)), activation='softmax'))  # Output layer (multi-class classification)

            # Compile the model
            model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

            # Train the model
            history = model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_test, y_test))

            # Evaluate the model
            y_pred_test = model.predict(X_test)
            y_pred_test = np.argmax(y_pred_test, axis=1)
            y_pred_test = model.predict(X_test)
            y_pred_test = np.argmax(y_pred_test, axis=1)
            accuracy = accuracy_score(y_test, y_pred_test)
            accuracy = round(accuracy, 4)
            msg = f"Accuracy Score of LSTM is {accuracy}"
            return render(request, 'model_train.html', {'msg':msg})
        
        elif algorithm == '4':
            model = Sequential()
            model.add(Dense(128, input_dim=x_train.shape[1], activation='relu'))  # First hidden layer with 128 neurons
            model.add(Dropout(0.2))  # Dropout for regularization
            model.add(Dense(64, activation='relu'))  # Second hidden layer with 64 neurons
            model.add(Dropout(0.2))  # Dropout for regularization
            model.add(Dense(32, activation='relu'))  # Third hidden layer with 32 neurons
            model.add(Dense(len(np.unique(y)), activation='softmax'))  # Output layer (multi-class classification)

            # Compile the model
            model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

            # Train the model
            history = model.fit(x_train, y_train, epochs=10, batch_size=32, validation_data=(x_test, y_test))
            y_pred_test = model.predict(x_test)
            y_pred_test = np.argmax(y_pred_test, axis=1)  
            accuracy = accuracy_score(y_test, y_pred_test)
            accuracy = round(accuracy, 4)
            msg = f"Accuracy Score of ANN is {accuracy}"
            return render(request, 'model_train.html', {'msg':msg})
        
    return render(request, 'model_train.html')

def prediction(request):
    msg = None
    suggestion = None
    impact = None
    temporal_details = None
    location_details = None

    if request.method == 'POST':
        num1 = float(request.POST.get('num1'))   # Time
        num2 = float(request.POST.get('num2'))   # Latitude
        num3 = float(request.POST.get('num3'))   # Longitude
        num4 = float(request.POST.get('num4'))   # Wind Speed
        num5 = float(request.POST.get('num5'))   # Wind Direction
        num6 = float(request.POST.get('num6'))   # Pressure
        num7 = float(request.POST.get('num7'))   # Temperature
        num8 = float(request.POST.get('num8'))   # Humidity
        num9 = float(request.POST.get('num9'))   # Distance from Land
        num10 = float(request.POST.get('num10')) # Cyclone Category

        user_input = [[num1, num2, num3, num4, num5, num6, num7, num8, num9, num10]]

        rf = RandomForestClassifier()
        rf.fit(x_train, y_train)
        predicts = rf.predict(user_input)[0]

        location_details = f"The cyclone is currently located near latitude {num2} and longitude {num3}, approximately {num9} km from land."
        temporal_details = f"The prediction is generated for the next {num1} hour(s), based on the given wind, pressure, humidity, and location conditions."

        if num4 >= 120 or num6 <= 960:
            impact = "High impact expected: Strong winds, heavy rainfall, coastal flooding, and possible damage to houses, trees, electric poles, and transport systems."
        elif num4 >= 80 or num6 <= 985:
            impact = "Moderate impact expected: Heavy rain, strong wind, waterlogging, and minor damage in vulnerable areas."
        else:
            impact = "Low impact expected: Light to moderate rainfall and manageable wind conditions, but continuous monitoring is required."

        if predicts == 0:
            msg = "Cyclone Moving Towards East Direction"
            suggestion = "Cyclone heading east. Monitor eastern coastal regions closely and alert nearby communities."
        elif predicts == 1:
            msg = "Cyclone Moving Towards North Direction"
            suggestion = "Cyclone heading north. Prepare for possible flooding and activate evacuation plans in northern regions."
        elif predicts == 2:
            msg = "Cyclone Moving Towards South Direction"
            suggestion = "Cyclone moving south. Coastal and low-lying areas should take necessary precautions."
        elif predicts == 3:
            msg = "Cyclone Moving Towards West Direction"
            suggestion = "Cyclone expected to move west. Prepare emergency support and monitor landfall possibility."

        return render(request, 'prediction.html', {
            'msg': msg,
            'suggestion': suggestion,
            'impact': impact,
            'temporal_details': temporal_details,
            'location_details': location_details
        })

    return render(request, 'prediction.html')

def view_logout(request):
    logout(request)
    messages.success(request, f"User Logout Successfully")
    return redirect('login')
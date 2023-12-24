import os
import requests
import urllib.parse
import datetime

from flask import redirect, render_template, request, session
from functools import wraps

def apology(message, code=400):
    """Render message as an apology to user."""
    return render_template("apology.html", code=code, message=message), code

# Original
def login_required_ddd(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

#Edited
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #store = requests.get("https://my-planner123.vercel.app/login")
        store = requests.get("https://google.com")
        try: 
            #if store.usercookie["user_id"] is None:
            if store.cookies["1P_JAR"] is None:
                return redirect("/login")
            return f(*args, **kwargs)
        except:
            print("cookie absent")
            return redirect("/login")
    return decorated_function

def days_in_month(calendar_month, calendar_year):
    days = 0
    if calendar_month in [0,2,4,6,7,9,11]:
        days = 31
    elif calendar_month == 1:
        if calendar_year%400 == 0:
            days = 29
        elif calendar_year%100 == 0:
            days = 28
        elif calendar_year%4 == 0:
            days = 29
        else:
            days = 28
    else:
        days = 30
    return days


def date(value):
    """Format value as date."""
    value = str(value)
    year = int(value[0] + value[1] + value[2] + value[3])
    month = int(value[5] + value[6])
    day = int(value[8] + value[9])
    return datetime.datetime(year, month, day).strftime("%d %B %Y")


def time12h(value):
    """Format value as 12h time."""
    value = str(value)
    return datetime.time(int(value[0] + value[1]), int(value[3] + value[4])).strftime("%I:%M %p")


def time24h(value):
    """Format value as 24h time."""
    value = str(value)
    return datetime.time(int(value[0] + value[1]), int(value[3] + value[4])).strftime("%H%M")

def tominutes(value):
    value = str(value)
    return (int(value[0] + value[1]) * 60 + int(value[3] + value[4]))

def overdue(value):
    value = str(value)
    year = int(value[0] + value[1] + value[2] + value[3])
    month = int(value[5] + value[6])
    day = int(value[8] + value[9])
    value = datetime.datetime(year, month, day)
    Ndate = datetime.datetime.now()
    if value < Ndate:
        return True
    else:
        return False
import os
import datetime

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, date, time12h, time24h, tominutes, days_in_month

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["tominutes"] = tominutes
app.jinja_env.filters["time12h"] = time12h
app.jinja_env.filters["time24h"] = time24h
app.jinja_env.filters["date"] = date

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
uri = os.getenv("DATABASE_URL")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://")
db = SQL(uri)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def temp():
    """Show today schedule"""
    timestamp = datetime.datetime.now()
    Ndate = timestamp.strftime("%Y-%m-%d")
    Nday = timestamp.strftime("%a")
    weektypes = db.execute("SELECT * FROM weektypes WHERE user_id = ?", session["user_id"])
    if request.method == "POST":
        if not request.form.get("date1"):
            return apology("must provide date", 400)
        elif request.form.get("date1") < Ndate:
            return apology("date has passed", 400)
        elif not request.form.get("weektype1"):
            return apology("must provide week", 400)
        elif not request.form.get("change"):
            return apology("nothing changed??", 400)
        else:
            date = request.form.get("date1")
            day = datetime.datetime(int(date[0] + date[1] + date[2] + date[3]), int(date[5] + date[6]), int(date[8] + date[9])).strftime("%a")
            if request.form.get("change") == "datechange":
                possible_week_id = db.execute("SELECT week_id FROM date WHERE date = ? AND user_id = ?", date, session["user_id"])
                if not possible_week_id:
                    chosen = db.execute("SELECT week_id FROM weektypes WHERE status = 'chosen' AND user_id = ?", session["user_id"])
                    if chosen:
                        week_id = chosen[0]["week_id"]
                    else:
                        week_id = 0
                else:
                    week_id = possible_week_id[0]["week_id"]
            else:
                if request.form.get("weektype1") == "None":
                    week_id = 0
                    if db.execute("SELECT * FROM date WHERE date = ? AND user_id = ?", date, session["user_id"]):
                        db.execute("DELETE FROM date WHERE date = ? AND user_id = ?", date, session["user_id"])
                        db.execute("DELETE FROM temp WHERE date = ? AND user_id = ? AND type = 'fixed'", date, session["user_id"])
                else:
                    week_id = request.form.get("weektype1")

                    #RESET timetable
                    if db.execute("SELECT * FROM temp WHERE date = ? AND user_id = ?", date, session["user_id"]):
                        db.execute("DELETE FROM temp WHERE date = ? AND user_id = ?", date, session["user_id"])

                    # Change week_id from existing
                    if db.execute("SELECT week_id FROM date WHERE date = ? AND user_id = ?", date, session["user_id"]):
                        db.execute("UPDATE date SET week_id = ? WHERE date = ? AND user_id = ?", week_id, date, session["user_id"])
                    else:
                        db.execute("INSERT INTO date(week_id, date, user_id) VALUES (?, ?, ?)", week_id, date, session["user_id"])
    else:
        day = Nday
        date = Ndate
        possible_week_id = db.execute("SELECT week_id FROM date WHERE date = ? AND user_id = ?", date, session["user_id"])
        if not possible_week_id:
            chosen = db.execute("SELECT week_id FROM weektypes WHERE status = 'chosen' AND user_id = ?", session["user_id"])
            if chosen:
                week_id = chosen[0]["week_id"]
            else:
                week_id = 0
        else:
            week_id = possible_week_id[0]["week_id"]
    if week_id == 0:
        fixed = []
        chosen_weektype = []
    else:
        chosen_weektype = db.execute("SELECT name FROM weektypes WHERE user_id = ? AND week_id = ?", session["user_id"], week_id)
        fixed = db.execute("SELECT activity, description, start_time, end_time, duration, week_id, activity_id FROM fixed WHERE user_id = ? AND week_id = ? AND day LIKE ? ORDER BY start_time, end_time", session["user_id"], week_id, f"%{day}%")
    temp = db.execute("SELECT * FROM temp WHERE user_id = ? AND date = ? ORDER BY start_time, end_time", session["user_id"], date)
    if temp:
        fixed = []
    tasks = db.execute("SELECT * FROM tasks WHERE (status = 'incomplete' OR due_date > ?) AND user_id = ? ORDER BY due_date", date, session["user_id"])
    events = db.execute("SELECT event, description, start_time, end_time, event_id FROM events WHERE date = ? AND user_id = ? ORDER BY start_time, end_time", date, session["user_id"])
    return render_template("temp.html", temp=temp, weektypes=weektypes, events=events, tasks=tasks, fixed=fixed, chosen_weektype=chosen_weektype, date=date)


@app.route("/taskstatus", methods=["GET", "POST"])
@login_required
def taskstatus():
    """Update task status"""
    if request.method == "POST":
        if not request.form.get("u_task_id"):
            return apology("task_id?", 400)
        elif not request.form.get("u_status"):
            return apology("status?", 400)
        else:
            db.execute("UPDATE tasks SET status = ? WHERE task_id = ? AND user_id = ?", request.form.get("u_status"), request.form.get("u_task_id"), session["user_id"])
    return redirect("/")


@app.route("/addtask", methods=["GET", "POST"])
@login_required
def addtask():
    """Add task"""
    timestamp = datetime.datetime.now()
    Ndate = timestamp.strftime("%Y-%m-%d")
    if request.method == "POST":
        if not request.form.get("task"):
            return apology("must provide task", 400)
        elif not request.form.get("due_date"):
            return apology("must provide due date", 400)
        elif request.form.get("due_date") < Ndate:
            return apology("due date has passed", 400)
        else:
            db.execute("INSERT INTO tasks(task, due_date, user_id) VALUES (?, ?, ?)", request.form.get("task"), request.form.get("due_date"), session["user_id"])
            newT = db.execute("SELECT MAX(task_id) AS new_t FROM tasks WHERE user_id = ?", session["user_id"])[0]["new_t"]
            if request.form.get("description"):
                db.execute("UPDATE tasks SET description = ? WHERE task_id = ?", request.form.get("description"), newT)
    # redirect
    return redirect("/")


@app.route("/savetemp", methods=["GET", "POST"])
@login_required
def savetemp():
    """save new temp"""
    if request.method == "POST":
        if not request.form.get("s_date"):
            return apology("missing date", 400)
        else:
            temp_date = request.form.get("s_date")

            # DELETE all existing on that date
            if db.execute("SELECT * FROM temp WHERE date = ? AND user_id = ?", temp_date, session["user_id"]):
                db.execute("DELETE FROM temp WHERE date = ? AND user_id = ?", temp_date, session["user_id"])

            # ADD to that date
            name = "s_activity_name{}"
            start = "s_start_time{}"
            end = "s_end_time{}"
            type = "s_type{}"

            for i in range(int(request.form.get("s_limit"))):
                db.execute("INSERT INTO temp(name, start_time, end_time, date, type, user_id) VALUES (?, ?, ?, ?, ?, ?)", request.form.get(name.format(i)), request.form.get(start.format(i)), request.form.get(end.format(i)), temp_date, request.form.get(type.format(i)), session["user_id"])

    return redirect("/")


@app.route("/modify_task", methods=["GET", "POST"])
@login_required
def modify_task():
    """Modify saved tasks"""
    if request.method == "POST":
        if not request.form.get("tomodifyT"):
            return apology ("no input?", 400)
        else:
            task_id = int(request.form.get("tomodifyT"))
            task = db.execute("SELECT task, description, due_date, task_id FROM tasks WHERE task_id = ?", task_id)[0]
            return render_template("modify_task.html", task=task)
    else:
        return redirect("/")


@app.route("/modified_task", methods=["GET", "POST"])
@login_required
def modified_task():
    """Confirm modified saved tasks"""
    timestamp = datetime.datetime.now()
    Ndate = timestamp.strftime("%Y-%m-%d")
    Ntime = timestamp.strftime("%X")
    if request.method == "POST":
        if not request.form.get("Q_delete"):
            return apology("Q_delete missing", 400)
        if not request.form.get("task_id"):
            return apology("must provide task_id", 400)
        if not request.form.get("task"):
            return apology("must provide task", 400)
        elif not request.form.get("due_date"):
            return apology("must provide due date", 400)
        elif request.form.get("due_date") < Ndate:
            return apology("due date has passed", 400)
        else:
            newT = request.form.get("task_id")
            if request.form.get("Q_delete") == "yes":
                db.execute("DELETE FROM tasks WHERE task_id = ?", newT)
            else:
                db.execute("UPDATE tasks SET task = ?, due_date = ? WHERE task_id = ?", request.form.get("task"), request.form.get("due_date"), newT)
                if request.form.get("description"):
                    db.execute("UPDATE tasks SET description = ? WHERE task_id = ?", request.form.get("description"), newT)
                else:
                    db.execute("UPDATE tasks SET description = NULL WHERE event_id = ?", newT)
    return redirect("/")


@app.route("/events", methods=["GET", "POST"])
@login_required
def events():
    """Saves events"""
    timestamp = datetime.datetime.now()
    Ndate = timestamp.strftime("%Y-%m-%d")
    Ntime = timestamp.strftime("%X")
    if request.method == "POST":
        if not request.form.get("event"):
            return apology("must provide event", 400)
        elif not request.form.get("date"):
            return apology("must provide date", 400)
        elif request.form.get("date") < Ndate:
            return apology("date has passed", 400)
        else:
            if request.form.get("start_time"):
                if request.form.get("date") == Ndate and request.form.get("start_time") < Ntime:
                    return apology("time has passed", 400)
                elif request.form.get("end_time"):
                    if request.form.get("end_time") < request.form.get("start_time"):
                        return apology("end time should be after it starts")
            db.execute("INSERT INTO events(event, date, user_id) VALUES (?, ?, ?)", request.form.get("event"), request.form.get("date"), session["user_id"])
            newE = db.execute("SELECT MAX(event_id) AS new_e FROM events WHERE user_id = ?", session["user_id"])[0]["new_e"]
            if request.form.get("description"):
                db.execute("UPDATE events SET description = ? WHERE event_id = ?", request.form.get("description"), newE)
            if request.form.get("start_time"):
                db.execute("UPDATE events SET start_time = ? WHERE event_id = ?", request.form.get("start_time"), newE)
            if request.form.get("end_time"):
                db.execute("UPDATE events SET end_time = ? WHERE event_id = ?", request.form.get("end_time"), newE)

    # return template w current events
    db.execute("UPDATE events SET status = 'passed' WHERE (date < ? OR (date = ? AND end_time < ? AND end_time IS NOT NULL))", Ndate, Ndate, Ntime)
    Upcoming = db.execute("SELECT event, description, date, start_time, end_time, event_id FROM events WHERE (date > ? OR (date = ? AND (end_time > ? OR end_time IS NULL))) AND user_id = ? ORDER BY date, start_time, end_time", Ndate, Ndate, Ntime, session["user_id"])
    return render_template("events.html", Events=Upcoming)


@app.route("/modify_event", methods=["GET", "POST"])
@login_required
def modify_event():
    """Modify saved events"""
    if request.method == "POST":
        if not request.form.get("tomodify"):
            return apology ("no input?", 400)
        else:
            event_id = int(request.form.get("tomodify"))
            event = db.execute("SELECT event, description, date, start_time, end_time, event_id FROM events WHERE event_id = ?", event_id)[0]
            return render_template("modify_event.html", event=event)
    else:
        return redirect("/events")


@app.route("/modified_event", methods=["GET", "POST"])
@login_required
def modified_event():
    """Confirm modified saved events"""
    timestamp = datetime.datetime.now()
    Ndate = timestamp.strftime("%Y-%m-%d")
    Ntime = timestamp.strftime("%X")
    if request.method == "POST":
        if not request.form.get("Q_delete"):
            return apology("Q_delete missing", 400)
        if not request.form.get("event_id"):
            return apology("must provide event_id", 400)
        if not request.form.get("event"):
            return apology("must provide event", 400)
        elif not request.form.get("date"):
            return apology("must provide date", 400)
        elif request.form.get("date") < Ndate:
            return apology("date has passed", 400)
        elif request.form.get("date") == Ndate and request.form.get("end_time") and request.form.get("end_time") < Ntime:
            return apology("time has passed", 400)
        else:
            newE = request.form.get("event_id")
            if request.form.get("Q_delete") == "yes":
                db.execute("DELETE FROM events WHERE event_id = ?", newE)
            else:
                if request.form.get("start_time") and request.form.get("end_time"):
                    if request.form.get("end_time") < request.form.get("start_time"):
                        return apology("end time should be after it starts")
                db.execute("UPDATE events SET event = ?, date = ? WHERE event_id = ?", request.form.get("event"), request.form.get("date"), newE)
                if request.form.get("description"):
                    db.execute("UPDATE events SET description = ? WHERE event_id = ?", request.form.get("description"), newE)
                else:
                    db.execute("UPDATE events SET description = NULL WHERE event_id = ?", newE)
                if request.form.get("start_time"):
                    db.execute("UPDATE events SET start_time = ? WHERE event_id = ?", request.form.get("start_time"), newE)
                else:
                    db.execute("UPDATE events SET start_time = NULL WHERE event_id = ?", newE)
                if request.form.get("end_time"):
                    db.execute("UPDATE events SET end_time = ? WHERE event_id = ?", request.form.get("end_time"), newE)
                else:
                    db.execute("UPDATE events SET end_time = NULL WHERE event_id = ?", newE)
    return redirect("/events")


@app.route("/calendar", methods=["GET", "POST"])
@login_required
def calendar():
    """Show monthly calendar"""
    if request.method == "POST":
        if not request.form.get("month"):
            return apology ("no month?", 400)
        elif not request.form.get("year"):
            return apology ("no year?", 400)
        calendar_month = int(request.form.get("month"))
        calendar_year = int(request.form.get("year"))
    else:
        timestamp = datetime.datetime.now()
        calendar_month = int(timestamp.strftime("%m")) - 1
        calendar_year = int(timestamp.strftime("%Y"))
    days = days_in_month(calendar_month, calendar_year)
    month = datetime.datetime(calendar_year, calendar_month + 1, 1).strftime("%B")
    start_of_month = datetime.datetime(calendar_year, calendar_month + 1, 1).strftime("%Y-%m-%d")
    end_of_month = datetime.datetime(calendar_year, calendar_month + 1, days).strftime("%Y-%m-%d")
    Month_events = db.execute("SELECT event, description, date, start_time, end_time, event_id FROM events WHERE date <= ? AND date >= ? AND user_id = ? ORDER BY date, start_time, end_time", end_of_month, start_of_month, session["user_id"])
    return render_template("calendar.html", events=Month_events, month=month, calendar_month=calendar_month, calendar_year=calendar_year, days=days)


@app.route("/fixed", methods=["GET", "POST"])
@login_required
def fixed():
    """Show fixed weekly schedule"""
    if request.method == "POST":
        if not request.form.get("activity"):
            return apology("must provide activity", 400)
        elif not request.form.get("mon") and request.form.get("tue") and request.form.get("wed") and request.form.get("thu") and request.form.get("fri") and request.form.get("sat") and request.form.get("sun"):
            return apology("must provide a day", 400)
        elif not request.form.get("start_time"):
            return apology("must provide activity start time", 400)
        elif not request.form.get("end_time"):
            return apology("must provide activity end time", 400)
        elif request.form.get("end_time") < request.form.get("start_time"):
            return apology("activity end time should be after it starts")
        elif not request.form.get("weektype"):
            return apology("must provide week", 400)

        else:
            x = "days"
            if request.form.get("mon"):
                x = x + " " + request.form.get("mon")
            if request.form.get("tue"):
                x = x + " " + request.form.get("tue")
            if request.form.get("wed"):
                x = x + " " + request.form.get("wed")
            if request.form.get("thu"):
                x = x + " " + request.form.get("thu")
            if request.form.get("fri"):
                x = x + " " + request.form.get("fri")
            if request.form.get("sat"):
                x = x + " " + request.form.get("sat")
            if request.form.get("sun"):
                x = x + " " + request.form.get("sun")
            start = request.form.get("start_time")
            end = request.form.get("end_time")
            y = int(end[0] + end[1]) - int(start[0] + start[1])
            z = int(end[3] + end[4]) - int(start[3] + start[4])
            duration = y + (z / 60)
            if not db.execute("SELECT week_id FROM weektypes WHERE name = ? AND user_id = ?", request.form.get("weektype"), session["user_id"]):
                db.execute("INSERT INTO weektypes(name, user_id) VALUES (?, ?)", request.form.get("weektype"), session["user_id"])
            week_id = db.execute("SELECT week_id FROM weektypes WHERE name = ? AND user_id = ?", request.form.get("weektype"), session["user_id"])[0]["week_id"]

            #Check for overlaps
            for i in range(len(x)):
                if (i - 1) % 4 == 0 and i > 1:
                    if db.execute("SELECT * FROM fixed WHERE day LIKE ? AND start_time < ? AND end_time > ? AND week_id = ? AND user_id = ?", f"%{x[i:(i+3)]}%", request.form.get("end_time"), request.form.get("start_time"), week_id, session["user_id"]):
                        return apology("overlaps with existing activity", 400)

            #Insert activity
            db.execute("INSERT INTO fixed(activity, day, start_time, end_time, duration, week_id, user_id) VALUES (?, ?, ?, ?, ?, ?, ?)", request.form.get("activity"), x, request.form.get("start_time"), request.form.get("end_time"), duration, week_id, session["user_id"])
            newA = db.execute("SELECT MAX(activity_id) AS new_a FROM fixed WHERE user_id = ?", session["user_id"])[0]["new_a"]
            if request.form.get("description"):
                db.execute("UPDATE fixed SET description = ? WHERE activity_id = ?", request.form.get("description"), newA)

    #Provide weekdata
    weektypes = db.execute("SELECT * FROM weektypes WHERE user_id = ?", session["user_id"])
    countweeks = db.execute("SELECT COUNT(week_id) AS count FROM weektypes WHERE user_id = ?", session["user_id"])
    if not countweeks:
        return render_template("fixed.html")
    else:
        weeks = []
        for i in range(countweeks[0]["count"]):
            x = []
            mon = db.execute("SELECT activity, description, start_time, end_time, duration, activity_id FROM fixed WHERE user_id = ? AND week_id = ? AND day LIKE '%Mon%' ORDER BY start_time, end_time", session["user_id"], weektypes[i]["week_id"])
            tue = db.execute("SELECT activity, description, start_time, end_time, duration, activity_id FROM fixed WHERE user_id = ? AND week_id = ? AND day LIKE '%Tue%' ORDER BY start_time, end_time", session["user_id"], weektypes[i]["week_id"])
            wed = db.execute("SELECT activity, description, start_time, end_time, duration, activity_id FROM fixed WHERE user_id = ? AND week_id = ? AND day LIKE '%Wed%' ORDER BY start_time, end_time", session["user_id"], weektypes[i]["week_id"])
            thu = db.execute("SELECT activity, description, start_time, end_time, duration, activity_id FROM fixed WHERE user_id = ? AND week_id = ? AND day LIKE '%Thu%' ORDER BY start_time, end_time", session["user_id"], weektypes[i]["week_id"])
            fri = db.execute("SELECT activity, description, start_time, end_time, duration, activity_id FROM fixed WHERE user_id = ? AND week_id = ? AND day LIKE '%Fri%' ORDER BY start_time, end_time", session["user_id"], weektypes[i]["week_id"])
            sat = db.execute("SELECT activity, description, start_time, end_time, duration, activity_id FROM fixed WHERE user_id = ? AND week_id = ? AND day LIKE '%Sat%' ORDER BY start_time, end_time", session["user_id"], weektypes[i]["week_id"])
            sun = db.execute("SELECT activity, description, start_time, end_time, duration, activity_id FROM fixed WHERE user_id = ? AND week_id = ? AND day LIKE '%Sun%' ORDER BY start_time, end_time", session["user_id"], weektypes[i]["week_id"])
            startend = db.execute("SELECT MIN(start_time) AS start_time, MAX(end_time) AS end_time FROM fixed WHERE user_id = ? AND week_id = ?", session["user_id"], weektypes[i]["week_id"])
            x.append(mon)
            x.append(tue)
            x.append(wed)
            x.append(thu)
            x.append(fri)
            x.append(sat)
            x.append(sun)
            x.append(startend)
            weeks.append(x)
        return render_template("fixed.html", weektypes=weektypes, weeks=weeks)


@app.route("/confirmfixed", methods=["GET","POST"])
@login_required
def chosen():
    #change weektypes status to chosen
    if request.method == "POST":
        if not request.form.get("chosen"):
            return apology("No specific week selected", 400)
        if not request.form.get("Q_delete"):
            return apology("Q_delete missing", 400)

        selected = request.form.get("chosen")
        if request.form.get("Q_delete") == "yes":
            if selected == 0:
                return apology("No specific week selected", 400)
            else:
                db.execute("DELETE FROM date WHERE week_id = ?", selected)
                db.execute("DELETE FROM fixed WHERE week_id = ?", selected)
                db.execute("DELETE FROM weektypes WHERE week_id = ?", selected)
        else:
            db.execute("UPDATE weektypes SET status = 'option' WHERE user_id = ?", session["user_id"])
            exception_dates = db.execute("SELECT date FROM date WHERE user_id = ?", session["user_id"])
            if int(selected) != 0:
                db.execute("UPDATE weektypes SET status = 'chosen' WHERE week_id = ? AND user_id = ?", request.form.get("chosen"), session["user_id"])
                for i in range(len(exception_dates)):
                    db.execute("DELETE FROM temp WHERE user_id = ? AND NOT date = ?", session["user_id"], exception_dates[i]["date"])
            else:
                for i in range(len(exception_dates)):
                    db.execute("DELETE FROM temp WHERE user_id = ? AND type = 'fixed' AND NOT date = ?", session["user_id"], exception_dates[i]["date"])

    return redirect("/fixed")


@app.route("/modify_activity", methods=["GET", "POST"])
@login_required
def modify_activity():
    """Modify saved activities"""
    if request.method == "POST":
        if not request.form.get("tomodify"):
            return apology ("no input?", 400)
        else:
            activity_id = int(request.form.get("tomodify"))
            activity = db.execute("SELECT activity, description, day, start_time, end_time, week_id, activity_id FROM fixed WHERE activity_id = ?", activity_id)[0]
            #get days,
            days = []
            x = activity["day"]
            for i in range(len(x)):
                if (i - 1) % 4 == 0 and i > 1:
                    days.append(f"{x[i:(i+3)]}")
            activity["weektype"] = db.execute("SELECT name FROM weektypes WHERE user_id = ? AND week_id = ?", session["user_id"], activity["week_id"])[0]["name"]
            weektypes = db.execute("SELECT * FROM weektypes WHERE user_id = ?", session["user_id"])
            return render_template("modify_activity.html", activity=activity, weektypes=weektypes, activity_days=days)
    else:
        return redirect("/fixed")


@app.route("/modified_activity", methods=["GET", "POST"])
@login_required
def modified_activity():
    """Confirm modified saved activities"""
    if request.method == "POST":
        if not request.form.get("Q_delete"):
            return apology("Q_delete missing", 400)
        if not request.form.get("activity_id"):
            return apology("must provide activity_id", 400)
        if not request.form.get("activity"):
            return apology("must provide activity", 400)
        elif not request.form.get("mon") and request.form.get("tue") and request.form.get("wed") and request.form.get("thu") and request.form.get("fri") and request.form.get("sat") and request.form.get("sun"):
            return apology("must provide a day", 400)
        elif not request.form.get("start_time"):
            return apology("must provide activity start time", 400)
        elif not request.form.get("end_time"):
            return apology("must provide activity end time", 400)
        elif request.form.get("end_time") < request.form.get("start_time"):
            return apology("activity end time should be after it starts")
        elif not request.form.get("weektype"):
            return apology("must provide week", 400)

        else:
            newA = request.form.get("activity_id")
            if request.form.get("Q_delete") == "yes":
                db.execute("DELETE FROM fixed WHERE activity_id = ?", newA)
            else:
                x = "days"
                if request.form.get("mon"):
                    x = x + " " + request.form.get("mon")
                if request.form.get("tue"):
                    x = x + " " + request.form.get("tue")
                if request.form.get("wed"):
                    x = x + " " + request.form.get("wed")
                if request.form.get("thu"):
                    x = x + " " + request.form.get("thu")
                if request.form.get("fri"):
                    x = x + " " + request.form.get("fri")
                if request.form.get("sat"):
                    x = x + " " + request.form.get("sat")
                if request.form.get("sun"):
                    x = x + " " + request.form.get("sun")
                start = request.form.get("start_time")
                end = request.form.get("end_time")
                y = int(end[0] + end[1]) - int(start[0] + start[1])
                z = int(end[3] + end[4]) - int(start[3] + start[4])
                duration = y + (z / 60)

                if not db.execute("SELECT week_id FROM weektypes WHERE name = ? AND user_id = ?", request.form.get("weektype"), session["user_id"]):
                    db.execute("INSERT INTO weektypes(name, user_id) VALUES (?, ?)", request.form.get("weektype"), session["user_id"])
                week_id = db.execute("SELECT week_id FROM weektypes WHERE name = ? AND user_id = ?", request.form.get("weektype"), session["user_id"])[0]["week_id"]

                #Check for overlaps
                for i in range(len(x)):
                    if (i - 1) % 4 == 0 and i > 1:
                        print (i)
                        if db.execute("SELECT * FROM fixed WHERE day LIKE ? AND start_time < ? AND end_time > ? AND week_id = ? AND user_id = ? AND NOT activity_id = ?", f"%{x[i:(i+3)]}%", request.form.get("end_time"), request.form.get("start_time"), week_id, session["user_id"], newA):
                            return apology("overlaps with existing activity", 400)

                #Update activity
                db.execute("UPDATE fixed SET activity = ?, day = ?, start_time = ?, end_time = ?, duration = ?, week_id = ? WHERE activity_id = ?", request.form.get("activity"), x, request.form.get("start_time"), request.form.get("end_time"), duration, week_id, newA)
                if request.form.get("description"):
                    db.execute("UPDATE fixed SET description = ? WHERE activity_id = ?", request.form.get("description"), newA)
                else:
                    db.execute("UPDATE fixed SET description = NULL WHERE activity_id = ?", newA)
    return redirect("/fixed")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["color"] = "red"

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        elif db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username")) != []:
            return apology("username already exists", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)

        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("passwords don't match", 400)

        # Query database for username
        db.execute("INSERT INTO users(username, hash) VALUES (?, ?)", request.form.get(
            "username"), generate_password_hash(request.form.get("password")))

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    """Change usernames, provide old username"""
    details = db.execute("SELECT username, hash FROM users WHERE id = ?", session["user_id"])
    username = details[0]["username"]
    password_hash = details[0]["hash"]

    if request.method == "POST":

        # If change username
        if request.form.get("new_username") and username != request.form.get("new_username"):
            if db.execute("SELECT * FROM users WHERE username = ?", request.form.get("new_username")) != []:
                return apology("username already exists", 400)
            else:
                db.execute("UPDATE users SET username = ? WHERE id = ?", request.form.get("new_username"), session["user_id"])
                username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]

        # If change password
        if request.form.get("new_password") or request.form.get("old_password") or request.form.get("new_password"):
            if not request.form.get("old_password"):
                return apology("must provide old password", 400)

            elif not check_password_hash(password_hash, request.form.get("old_password")):
                return apology("old password is wrong", 400)

            elif not request.form.get("new_password"):
                return apology("must provide new password", 400)

            elif not request.form.get("confirmation"):
                return apology("must confirm new password", 400)

            elif request.form.get("confirmation") != request.form.get("new_password"):
                return apology("passwords don't match", 400)

            else:
                db.execute("UPDATE users SET hash = ? WHERE id = ?", generate_password_hash(request.form.get("new_password")), session["user_id"])

    return render_template("settings.html", username=username)

@app.route("/settings_color", methods=["GET", "POST"])
@login_required
def settings_color():
    if request.method == "POST":

        if not request.form.get("new_color"):
            return apology("no new color?", 400)
        else:
            session["color"] = request.form.get("new_color")
            
    return redirect("/settings")
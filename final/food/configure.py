@app.route("/configure", methods=["GET", "POST"])
@login_required
def configure():
    session["test"] = "nope"
    now = dt.datetime.now() - dt.timedelta(hours=7)
    now = dt.datetime.strftime(now,"%H:%M")
    if request.method == "POST":
        test = request.form.get("test")
        date = request.form.get("date")
        session["test"] = test + date
        flash(session["test"])
    return render_template("configure.html", now=now)
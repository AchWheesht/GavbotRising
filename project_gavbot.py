if __name__ == "__main__":
    from flask import Flask, app, request, session, render_template, redirect, send_from_directory
    import gavbot_page_manager
else:
    from philsite import philsite, app, request, session, render_template, redirect, send_from_directory
    import philsite.project_gavbot.gavbot_page_manager as gavbot_page_manager
import os


#Run as Standalone
if __name__ == "__main__":
    app_dir = os.path.dirname(os.path.realpath(__file__))       #Current Directory
    path = "/"                                                  #Path prefix for website
    dir_name="/"                                                #Directory for python ilfe
    static_dir = app_dir + "/static"                            #Directory for static files

    bind = "127.0.0.1"                                          #Local IP
    port = 5000                                                 #Port to run on
    app = Flask(__name__, template_folder="")

#Run as part of main website
else:
    app_dir = philsite.app_dir                                  #Directory of __init__ python file
    path = "/gavbot"                                            #Path prefix for website
    dir_name="project_gavbot/"                                  #Directory of project on website
    static_dir = app_dir + "/project_gavbot/static"             #Directory for static files


script_dir = os.path.dirname(os.path.realpath(__file__))        #Directory for Gavbot class to use
app.jinja_env.autoescape = False                                #Turn off autoescaping for serving files (Sec issue, work on later)
current_bots = {}                                               #Currently active gavbot users
logged_sessions = []                                            #IP sessions logged
app.secret_key = os.urandom(32)                                 #Secert key for sessions

@app.route("/gavbot_static/<path:filename>")
def gavbot_static(filename):
    """Serve static files"""
    return send_from_directory(static_dir, filename)

@app.route(path)
def gavbot_index():
    """Check for login, deliver appropriare page as dictated by gavbot object"""
    if request.remote_addr not in logged_sessions:
        logged_sessions.append(request.remote_addr)
        gavbot_log_addr(request.remote_addr)
    if 'username' in session:
        return render_template(dir_name+"templates/gavbot_index.html", gavbot=current_bots[session['username']], path=path)
    else:
        return render_template(dir_name+"templates/gavbot_index_null.html", path=path)

@app.route(path+"page/<page>")
def gavbot_move_page(page):
    """Process a users choice on a page"""
    if 'username' in session:
        current_bots[session['username']].user_update_page(page)
        return redirect(path)
    else:
        return redirect(path)

@app.route(path+"login", methods=["GET", "POST"])
def gavbot_login():
    """Start a session with the user"""
    if request.method == "POST":
        session["username"] = request.form["username"]
        current_bots[session["username"]] = gavbot_page_manager.Gavbot(session["username"], path=script_dir+"/")
        return redirect(path)

@app.route(path+"logout")
def gavbot_logout():
    """End a users sessions"""
    session.pop("username", None)
    return redirect(path)

@app.route(path+"reset")
def gavbot_reset():
    """Reset a users progress"""
    current_bots[session['username']].reset_gavbot()
    return redirect(path)

def gavbot_log_addr(ip):
    """IP logging test idea"""
    with open(app_dir+"/log/log.txt", "a") as file:
        file.write(ip + "\n")


if __name__ == "__main__":
    app.run(host=bind, port=port) #This line needs to be here apparently

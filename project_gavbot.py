import os, sys
sys.path.append(os.path.dirname(__file__))
import gavbot_page_manager

if __name__ == "__main__":
    from flask import Flask, app, request, session, render_template, redirect, send_from_directory
else:
    from philsite import philsite, app, request, session, render_template, redirect, send_from_directory

class SiteInfo:
    def __init__(self):
        #Run as Standalone
        if __name__ == "__main__":
            self.app_dir = os.path.dirname(os.path.realpath(__file__))       #Current Directory
            self.path = "/"                                                  #Path prefix for website
            self.dir_name="/"                                                #Directory for python files
            self.gav_dir = ""                                                #Directory to look for gav files
            self.static_dir = self.app_dir + "/static"                       #Directory for static files

            self.bind = "127.0.0.1"                                          #Local IP
            self.port = 5000                                                 #Port to run on

        #Run as part of main website
        else:
            self.app_dir = philsite.app_dir                                  #Directory of __init__ python file
            self.path = "/gavbot"                                            #Path prefix for website
            self.dir_name="project_gavbot/"                                  #Directory of project on website
            self.static_dir = self.app_dir + "/project_gavbot/static"        #Directory for static files


        self.script_dir = os.path.dirname(os.path.realpath(__file__))        #Directory for Gavbot class to use
        self.current_bots = {}                                               #Currently active gavbot users
        self.logged_sessions = []                                            #IP sessions logged

site = SiteInfo()

if __name__ == "__main__":
    app = Flask(__name__, template_folder="")

app.jinja_env.autoescape = False                                #Turn off autoescaping for serving files (Sec issue, work on later)
app.secret_key = os.urandom(32)                                 #Secert key for sessions

@app.route("/gavbot_static/<path:filename>")
def gavbot_static(filename):
    """Serve static files"""
    return send_from_directory(site.static_dir, filename)

@app.route(site.path)
def gavbot_index():
    """Check for login, deliver appropriare page as dictated by gavbot object"""
    if request.remote_addr not in site.logged_sessions:
        site.logged_sessions.append(request.remote_addr)
        gavbot_log_addr(request.remote_addr)
    if 'username' in session:
        return render_template(site.dir_name+"templates/gavbot_index.html", gavbot=site.current_bots[session['username']], path=site.path)
    else:
        return render_template(site.dir_name+"templates/gavbot_index_null.html", path=site.path)

@app.route(site.path+"page/<page>")
def gavbot_move_page(page):
    """Process a users choice on a page"""
    if 'username' in session:
        site.current_bots[session['username']].user_update_page(page)
        return redirect(site.path)
    else:
        return redirect(site.path)

@app.route(site.path+"login", methods=["GET", "POST"])
def gavbot_login():
    """Start a session with the user"""
    if request.method == "POST":
        session["username"] = request.form["username"]
        site.current_bots[session["username"]] = gavbot_page_manager.Gavbot(session["username"], site=site)
        return redirect(site.path)

@app.route(site.path+"logout")
def gavbot_logout():
    """End a users sessions"""
    session.pop("username", None)
    return redirect(site.path)

@app.route(site.path+"reset")
def gavbot_reset():
    """Reset a users progress"""
    site.current_bots[session['username']].reset_gavbot()
    return redirect(site.path)

def gavbot_log_addr(ip):
    """IP logging test idea"""
    with open(site.app_dir+"/log/log.txt", "a") as file:
        file.write(ip + "\n")


if __name__ == "__main__":
    app.run(host=site.bind, port=site.port) #This line needs to be here apparently

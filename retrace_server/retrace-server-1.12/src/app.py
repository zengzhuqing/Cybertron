#!/usr/bin/python
from flask import Flask
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask import redirect
from flask import make_response
from functools import update_wrapper
from datetime import timedelta
from retrace import *
import re
import fnmatch
import urlparse
import json
from flask import make_response, request, current_app

from retrace.Bugzilla_webservice import BugzillaServer

BUGZILLA_URL = 'https://bugzilla.eng.vmware.com/xmlrpc.cgi'

LONG_TYPES = { TASK_RETRACE: "Coredump retrace",
               TASK_DEBUG: "Coredump retrace - debug",
               TASK_VMCORE: "VMcore retrace",
               TASK_RETRACE_INTERACTIVE: "Coredump retrace - interactive",
               TASK_VMCORE_INTERACTIVE: "VMcore retrace - interactive" }

def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers
            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            h['Access-Control-Allow-Credentials'] = 'true'
            h['Access-Control-Allow-Headers'] = \
                "Origin, X-Requested-With, Content-Type, Accept, Authorization"
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

application= Flask(__name__)
application.secret_key = 'abc'
def is_local_task(taskid):
    try:
        RetraceTask(taskid)
    except:
        return False
    
    return True

def get_status_for_task_manager(task, _=lambda x: x):
    status = _(STATUS[task.get_status()])
    if task.get_status() == STATUS_DOWNLOADING and task.has(RetraceTask.PROGRESS_FILE):
        status += " %s" % task.get(RetraceTask.PROGRESS_FILE)

    return status

def get_bug_dir(bug_id):
    bug_dir = '/cores/bugs/files/0/'
    if bug_id:
        for i in bug_id:
            bug_dir += i + '/'
        return bug_dir

def get_files(d, fnfilter, dfilter, rel=True):
    d = os.path.expanduser(d)
    dirs = []
    fns = []
    for fn in sorted(os.listdir(d)):
        ffn = os.path.join(d, fn)
        if not rel:
            fn = ffn
        if os.path.isdir(ffn):
            if dfilter(ffn):
                dirs.append(fn)
        else:
            if fnfilter(ffn):
                fns.append(fn)
    return fns, dirs

@application.route('/Logout', methods=['POST'])
def Logout():
    """
    This function helps user to log out.
    All the session will be left
    """

    try:
        logging.warning("%s logout successfully." %(session['username']))
    except:
        pass
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('admin', None)
    
    if "taskid" in request.form:
        url = "/%s" %(request.form["taskid"])
        return redirect(url)
    else:
        return redirect(url_for("Index"))    

@application.route('/Login', methods=['POST'])
def Login():
    """
    This function handles login function.
    The login procedure is connected with bugzilla
    After successfully login, the function will check for the admin privilege and record username into data
    The transmission is crypted, and the password is not recorded in the system
    """
    error = None
    if 'USERPROFILE' in os.environ:
        homepath = os.path.join(os.environ["USERPROFILE"], "Local Settings",
                                "Application Data")
    elif 'HOME' in os.environ:
        homepath = os.environ["HOME"]
    else:
        homepath = ''

    cookie_file = os.path.join(homepath, ".bugzilla-cookies.%s.txt"%str(request.form['BG_account']))
    #bugzilla_url = options.bugzilla_url
    server = BugzillaServer(BUGZILLA_URL, cookie_file)
    login_result = server.login(str(request.form["BG_account"]), str(request.form["BG_password"]))
    if not login_result:
        logging.warning("%s fails to login into the bugzilla." %(str(request.form["BG_account"])))
        return "Your account and pasword is not match, login failed!"    
 #       return render_template('query.html', error = "Error Account/Password, Please Login again")

    session['username'] = request.form['BG_account']
    if session['username']:
        session['username'] = session['username'].split('@')[0]
    session['password'] = request.form['BG_password']
    session['cookie_file'] = cookie_file

    session['logged_in'] = True

    '''
    admin_file_path = open(BAR_ADMINFILE, "r")
    admin_members = []
    for line in admin_file_path:
        admin_members.append(line.rstrip())
    if session['username'] in admin_members:
        session['admin'] = True
    else:
        session['admin'] = False
    '''

    logging.warning("%s login into the bugzilla successfully." %(session['username']))
    if "taskid" in request.form:
        url = "/%s" %(request.form["taskid"])
        return redirect(url)
    else:
        return redirect(url_for("Index"))    

@application.route('/Create_BG', methods=['POST'])
@crossdomain(origin='*')
def Create_BG():
    qs_base = []
    if "debug" in request.form and request.form["debug"] == "on":
        qs_base.append("debug=debug")

    if "vra" in request.form:
        vra = request.form["vra"]

        if len(vra.strip()) > 0:
            try:
                kver = KernelVer(vra)
                if kver.arch is None:
                    raise Exception
            except:
                return "Please use VRA format for kernel version (e.g. 2.6.32-287.el6.x86_64)"

            qs_base.append("kernelver=%s" % urllib.quote(vra))

    try:
        task = RetraceTask()
    except Exception as ex:
        return "Unable to create a new task"

    # ToDo - support more
    task.set_type(TASK_VMCORE_INTERACTIVE)
    task.add_remote(request.form["custom_url"])
    task.set_managed(True)
    task.set_url("/%d" % (task.get_taskid()))

    starturl = "/%d/start" % (task.get_taskid())
    if len(qs_base) > 0:
        starturl = "%s?%s" % (starturl, "&".join(qs_base))

    # Just start the task
    task.start()

    # ugly, ugly, ugly! retrace-server-worker double-forks and needs a while to spawn
    time.sleep(2)

    return "OK"
    
@application.route('/Create', methods=['POST'])
def Create():
    qs_base = []
    if "debug" in request.form and request.form["debug"] == "on":
        qs_base.append("debug=debug")

    if "vra" in request.form:
        vra = request.form["vra"]

        if len(vra.strip()) > 0:
            try:
                kver = KernelVer(vra)
                if kver.arch is None:
                    raise Exception
            except:
                return "Please use VRA format for kernel version (e.g. 2.6.32-287.el6.x86_64)"

            qs_base.append("kernelver=%s" % urllib.quote(vra))

    try:
        task = RetraceTask()
    except Exception as ex:
        return "Unable to create a new task"

    # ToDo - support more
    task.set_type(TASK_VMCORE_INTERACTIVE)
    task.add_remote(request.form["custom_url"])
    task.set_managed(True)
    task.set_url("/%d" % (task.get_taskid()))

    starturl = "/%d/start" % (task.get_taskid())
    if len(qs_base) > 0:
        starturl = "%s?%s" % (starturl, "&".join(qs_base))

    return redirect(starturl)

@application.route('/<task_id>/start')
def Start(task_id):
    get = urlparse.parse_qs(request.query_string)
    ftptask = False
    try:
        task = RetraceTask(task_id)
    except:
        if CONFIG["UseFTPTasks"]:
            ftp = ftp_init()
            files = ftp_list_dir(CONFIG["FTPDir"], ftp)
            if not task_id in files:
                ftp_close(ftp)
                return "There is no such task A"

            try:
                size = ftp.size(task_id)
            except:
                size = 0

            ftp_close(ftp)

            if space - size < (CONFIG["MinStorageLeft"] << 20):
                return "There is not enough free space on the server"

            ftptask = True
        else:
            return "There is no such task B"

    # Set default notification email to the login user's email
    if "logged_in" in session and session["logged_in"]:
        notify_list = []
        email = "%s@vmware.com" %(session["username"])
        notify_list.append(email)
        task.set_notify(notify_list) 

    if ftptask:
        try:
            task = RetraceTask()
            task.set_managed(True)
            # ToDo: determine?
            task.set_type(TASK_VMCORE_INTERACTIVE)
            task.add_remote("FTP %s" % task_id)
            task.set_url("/%d" % (task.get_taskid()))
        except:
            return "Unable to create a new task"

        if "caseno" in get:
            try:
                task.set_caseno(int(get["caseno"][0]))
            except:
                # caseno is invalid number - do nothing, it can be set later
                pass

    if not task.get_managed():
        return "Task does not belong to task manager"

    debug = "debug" in get
    kernelver = None
    arch = None
    if "kernelver" in get:
        try:
            kernelver = KernelVer(get["kernelver"][0])
            if kernelver.arch is None:
                raise Exception
        except Exception as ex:
            return "403 Forbidden! " + "Please use VRA format for kernel version (e.g. 2.6.32-287.el6.x86_64)"

        kernelver = str(kernelver)
        arch = kernelver.arch

    task.start(debug=debug, kernelver=kernelver, arch=arch)

    # ugly, ugly, ugly! retrace-server-worker double-forks and needs a while to spawn
    time.sleep(2)

    redirect_url = "/%d" % (task.get_taskid())
    return redirect(redirect_url)

def get_main_elements():
    _ = parse_http_gettext("%s" % request.accept_languages,
                           "%s" % request.accept_charsets)
    
    title = _("Retrace Server Task Manager")
    sitename = _("Retrace Server Task Manager")

    baseurl = request.url
    if not baseurl.endswith("/"):
        baseurl += "/"
    
    try:
        filterexp = request.GET.getone("filter")
    except:
        filterexp = None

    running = []
    finished = []
    for taskid in sorted(os.listdir(CONFIG["SaveDir"])):
        if not os.path.isdir(os.path.join(CONFIG["SaveDir"], taskid)):
            continue

        try:
            task = RetraceTask(taskid)
        except:
            continue

        if not task.get_managed():
            continue

        if task.has_status():
            tool = {}
            statuscode = task.get_status()
            if statuscode in [STATUS_SUCCESS, STATUS_FAIL]:
                if statuscode == STATUS_SUCCESS:
                    tool["status"] = "success"
                elif statuscode == STATUS_FAIL:
                    tool["status"] = "fail"

                if task.has_finished_time():
                    finishtime = datetime.datetime.fromtimestamp(task.get_finished_time())

                if task.has_caseno():
                    tool["caseno"] = str(task.get_caseno())

                if task.has_downloaded():
                    tool["files"] = task.get_downloaded()

                tool["taskid"] = taskid
                tool["baseurl"] = baseurl
                tool["finishtime"] = finishtime

                finished.append((finishtime, tool))
            else:
                tool["status"] = get_status_for_task_manager(task, _=_)

                if task.has_started_time():
                    starttime = datetime.datetime.fromtimestamp(task.get_started_time())

                if task.has_caseno():
                    tool["caseno"] = str(task.get_caseno())

                if task.has_remote():
                    remote = map(lambda x: x[4:] if x.startswith("FTP ") else x, task.get_remote())
                    tool["files"] = ", ".join(remote)

                if task.has_downloaded():
                    tool["files"] = ", ".join(filter(None, [task.get_downloaded()]))

                tool["taskid"] = taskid
                tool["baseurl"] = baseurl
                tool["starttime"] = starttime

                running.append((starttime, tool))

    finished = [f[1] for f in sorted(finished, key=lambda x: x[0], reverse=True)]
    running = [r[1] for r in sorted(running, key=lambda x: x[0], reverse=True)]

    available_str = _("Available tasks")
    running_str = _("Running tasks")
    finished_str = _("Finished tasks")
    taskid_str = _("Task ID")
    caseno_str = _("Case no.")
    files_str = _("File(s)")
    starttime_str = _("Started")
    finishtime_str = _("Finished")
    status_str = _("Status")

    replace = {}
    replace['title"'] = title
    replace['sitename'] = sitename
    replace['available_str'] = available_str
    replace['running_str'] = running_str
    replace['finished_str'] = finished_str
    replace['taskid_str'] = taskid_str
    replace['caseno_str'] = caseno_str
    replace['files_str'] = files_str
    replace['starttime_str'] = starttime_str
    replace['finishtime_str'] = finishtime_str
    replace['status_str'] = status_str
    # spaces to keep the XML nicely aligned

    ans = {}
    ans["running"] = running
    ans["finish"] = finished
    ans["replace"] = replace
    return ans 

@application.route('/')
def Index():
    main_elements = get_main_elements()
    running = main_elements["running"]
    finished = main_elements["finish"]
    replace = main_elements["replace"]
    return render_template("manager.html", running = running, finish = finished, **replace)

@application.route('/<task_id>')
def taskinfo(task_id):
    _ = parse_http_gettext("%s" % request.accept_languages,
                           "%s" % request.accept_charsets)
    baseurl = request.url
    if not baseurl.endswith("/"):
        baseurl += "/"
    
    # info
    ftptask = False
    filesize = None
    try:
        task = RetraceTask(task_id)
    except:
        if CONFIG["UseFTPTasks"]:
            ftp = ftp_init()
            files = ftp_list_dir(CONFIG["FTPDir"], ftp)
            if not task_id in files:
                ftp_close(ftp)
                return _("There is no such task C")

            ftptask = True
            try:
                filesize = ftp.size(task_id)
            except:
                pass
            ftp_close(ftp)
        else:
            return _("There is no such task D")

    start = ""
    if not ftptask and task.has_status():
        status = get_status_for_task_manager(task, _=_)
    else:
        startcontent = "    <form method=\"get\" action=\"%s/start\">" \
                           "      Kernel version (empty to autodetect): <input name=\"kernelver\" type=\"text\" id=\"kernelver\" /> e.g. <code>2.6.32-287.el6.x86_64</code><br />" \
                           "      Case no.: <input name=\"caseno\" type=\"text\" id=\"caseno\" /><br />" \
                           "      E-mail notification: <input name=\"notify\" type=\"text\" id=\"notify\" /><br />" \
                           "      <input type=\"checkbox\" name=\"debug\" id=\"debug\" checked=\"checked\" />Be more verbose in case of error<br />" \
                           "      <input type=\"submit\" value=\"%s\" id=\"start\" class=\"button\" />" \
                           "    </form>" % (request.url.rstrip("/"), _("Start task"))

        if ftptask:
            status = _("On remote FTP server")
            if filesize:
                status += " (%s)" % human_readable_size(filesize)

            if space - filesize < (CONFIG["MinStorageLeft"] << 20):
                startcontent = _("You can not start the task because there is not enough free space on the server")
            else:
                status = _("Not started")

        start = "<tr>" \
            "  <td colspan=\"2\">" \
            "%s" \
            "  </td>" \
            "</tr>" % startcontent

    title = ""
    interactive = ""
    backtrace = ""
    log_title = ""
    log_content = ""
    kernellog_title = ""
    kernellog_content = ""
    testwindow = ""
    rhkb_matched = []
    vmbugzilla_matched = []
    if not ftptask:
        if task.has_backtrace():
            kernellog_title = "Kernel log"
            kernellog_content = task.get_backtrace()
            if task.get_type() in [TASK_RETRACE_INTERACTIVE, TASK_VMCORE_INTERACTIVE]:
                if task.get_type() == TASK_VMCORE_INTERACTIVE:
                    debugger = "crash"
                else:
                    debugger = "gdb"

            interactive = "<tr><td colspan=\"2\">%s</td></tr>" \
                          "<tr><td colspan=\"2\">%s <code>retrace-server-interact %s shell</code></td></tr>" \
                          "<tr><td colspan=\"2\">%s <code>retrace-server-interact %s %s</code></td></tr>" \
                          "<tr><td colspan=\"2\">%s <code>man retrace-server-interact</code> %s</td></tr>" \
                          % (_("This is an interactive task"), _("You can jump to the chrooted shell with:"), task_id,
                          _("You can jump directly to the debugger with:"), task_id, debugger,
                          _("see"), _("for further information about cmdline flags"))

            # Redhat KB search result parse
            rhkb_search_result = task.get_rhkb_matched()
            if rhkb_search_result != None:
                jans = json.loads(rhkb_search_result)
                for array in jans["hits"]["hits"]:
                    addr = "https://access.redhat.com/solutions/%s" %(array["_id"]) 
                    rhkb_matched.append((addr, array["_source"]["title"]))
            
            # VMware Bugzilla search result parse
            vmbugzilla_search_result = task.get_vmbugzilla_matched()
            if vmbugzilla_search_result != None:
                jans = json.loads(vmbugzilla_search_result)
                for array in jans["hits"]["hits"]:
                    vmbugzilla_matched.append((array["_id"], array["_source"]))
        
        elif task.has_log():
            log_title = "Log"
            log_content = task.get_log()

    if ftptask or task.is_running(readproc=True) or CONFIG["TaskManagerAuthDelete"]:
        delete = ""
    else:
        delete = "<tr><td colspan=\"2\"><a href=\"%s/delete\">%s</a></td></tr>" % (request.url.rstrip("/"), _("Delete task"))

    if ftptask:
        # ToDo: determine?
        tasktype = _(LONG_TYPES[TASK_VMCORE_INTERACTIVE])
        title = "%s '%s' - %s" % (_("Remote file"), task_id, _("Retrace Server Task Manager"))
        taskno = "%s '%s'" % (_("Remote file"), task_id)
    else:
        tasktype = _(LONG_TYPES[task.get_type()])
        title = "%s #%s - %s" % (_("Task"), task_id, _("Retrace Server Task Manager"))
        taskno = "%s #%s" % (_("Task"), task_id)

    misc = ""
    if not ftptask:
        misclist = sorted(task.get_misc_list())
        misc = _("Additional results:")
    
    delete_yesno = ""
    """
    if match.group(6) and match.group(6).startswith("delete") and not CONFIG["TaskManagerAuthDelete"]:
        delete_yesno = "<tr><td colspan=\"2\">%s <a href=\"%s/sure\">Yes</a> - <a href=\"%s/%s\">No</a></td></tr>" \
                       % (_("Are you sure you want to delete the task?"), request.url.rstrip("/"),
                          match.group(1), task_id)
    else:
        delete_yesno = ""
    """

    unknownext = ""
    """
    if ftptask:
        known = any(task_id.endswith(ext) for ext in FTP_SUPPORTED_EXTENSIONS)
        if not known:
            unknownext = "<tr><td colspan=\"2\">%s %s</td></tr>" % \
                         (_("The file extension was not recognized, thus the file will be "
                            "considered a raw vmcore. Known extensions are:"),
                          ", ".join(FTP_SUPPORTED_EXTENSIONS))
    """

    downloaded = ""
    if not ftptask and task.has_downloaded():
        downloaded = task.get_downloaded()

    starttime = ""
    if not ftptask and task.has_started_time():
        starttime = datetime.datetime.fromtimestamp(task.get_started_time())

    finishtime = ""
    if not ftptask and task.has_finished_time():
        finishtime = datetime.datetime.fromtimestamp(task.get_finished_time())

    if not ftptask:
        currentcaseno = ""
        if task.has_caseno():
            currentcaseno = task.get_caseno()

    backstr = "Back to task manager"

    notify = ""
    if not ftptask:
        currentnotify = ""
        if task.has_notify():
            currentnotify = ", ".join(task.get_notify()) 

    replace = {}
    replace['title'] = title
    replace['taskid'] = task_id
    replace['taskno'] = taskno
    replace['str_type'] = _("Type:")
    replace['type'] = tasktype
    replace['str_status'] = _("Status:")
    replace['status'] = status 
    replace['start'] = start
    replace['backstr'] = backstr
    replace['backtrace'] = backtrace
    replace['log_title'] = log_title
    replace['log_content'] = log_content
    replace['kernellog_title'] = kernellog_title
    replace['kernellog_content'] = kernellog_content
    replace['currentcaseno'] = currentcaseno
    replace['currentnotify'] = currentnotify
    replace['delete'] = delete
    replace['delete_yesno'] = delete_yesno
    replace['interactive'] = interactive
    replace['misc'] = misc
    replace['unknownext'] = unknownext
    replace['downloaded'] = downloaded
    replace['starttime'] = starttime
    replace['finishtime'] = finishtime
    replace['vmbugzilla_matched'] = vmbugzilla_matched

    return render_template("managertask.html", misclist=misclist,\
         rhkb_matched = rhkb_matched,  **replace)

@application.route('/<task_id>/kernellog')
def ShowRawKernelLog(task_id): 
    try:
        task = RetraceTask(task_id)
    except:
        return "There is no such task"

    if not task.get_managed():
        return "403 Forbidden" + "Task does not belong to task manager"

    if not task.has_backtrace():
        return "404 Forbidden" + "Task does not have a backtrace"

    response = make_response(task.get_backtrace())
    response.content_type = "text/plain"
    return response

@application.route('/<task_id>/misc/<item>')
def ShowMiscItem(task_id, item):
    try:
        task = RetraceTask(task_id)
    except:
        return "There is no such task"

    if not task.has_misc(item):
        return "There is no such record"

    response = make_response(task.get_misc(item))
    response.content_type = "text/plain"
    return response

@application.route('/<task_id>/delete')
def Delete(task_id):
    try:
        task = RetraceTask(task_id)
    except:
        return "There is no such task"

    if not task.get_managed():
        return "Task does not belong to task manager"

    if CONFIG["TaskManagerAuthDelete"]:
        return "Authorization required to delete tasks"

    task.remove()

    return redirect(url_for("Index"))

@application.route('/<task_id>/updatecaseno', methods=['GET', 'POST'])
def UpdateCaseNo(task_id):
    try:
        task = RetraceTask(task_id)
    except:
        return "There is no such task"

    if "caseno" in request.form:
        if not request.form["caseno"]:
            task.delete(RetraceTask.CASENO_FILE)
        else:
            try:
                caseno = int(request.form["caseno"])
            except Exception as ex:
                return "Case number must be an integer; %s" % ex

            task.set_caseno(caseno)

    url = "/%s" %(task_id)
    return redirect(url)

@application.route('/<task_id>/updatenotify', methods=['GET', 'POST'])
def UpdateNotify(task_id):
    try:
        task = RetraceTask(task_id)
    except:
        return "There is no such task"

    if "notify" in request.form:
        task.set_notify(filter(None, set(n.strip() for n in request.form["notify"].replace(";", ",").split(","))))
   
    url = "/%s" %(task_id)
    return redirect(url)

@application.route('/sfiles', methods=['POST'])
def sfiles():
    r = []
    fnfilter = lambda fn: True
    dfilter = lambda d: True
    try:
        d = urllib.unquote(request.form.get('dir', './'))
        fns, dirs = get_files(d, fnfilter, dfilter, rel=True)
        r = ['<ul class="jqueryFileTree" style="display: none;">']
        for f in dirs:
            ff = os.path.join(d, f)
            r.append('<li class="directory collapsed">' \
                    '<a href="#" rel="%s/">%s</a></li>' % (ff, f))
        for f in fns:
            ff = os.path.join(d, f)
            e = os.path.splitext(f)[1][1:]  # get .ext and remove dot
            r.append('<li class="file ext_%s">' \
            '<a href="#" rel="%s">%s</a></li>' % (e, ff, f))
        r.append('</ul>')
    except Exception as E:
        r.append('Could not load directory: %s' % (str(E)))
    return ''.join(r)
    #return render_template("manager.html", dirlist = ''.join(r))
 
@application.route('/List', methods=['POST'])
def List():
    main_elements = get_main_elements()
    running = main_elements["running"]
    finished = main_elements["finish"]
    replace = main_elements["replace"]
    bug_dir = get_bug_dir(request.form["bugid"])

    return render_template("manager.html", running = running, finish = finished, bug_dir = bug_dir, **replace)
 
if __name__ == '__main__':
    application.debug = True
    application.run(host='0.0.0.0', port=5555)

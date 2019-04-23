from http.server import BaseHTTPRequestHandler, HTTPServer
from http import cookies
from urllib.parse import urlparse, parse_qs
import json
from passlib.hash import pbkdf2_sha256
import sys
from democracy_db import DemocracyDB
from user_db import UserDB
from session_store import SessionStore

gSessionStore = SessionStore()


class MyRequestHandler(BaseHTTPRequestHandler):

    def end_headers(self):
        self.sendCookie()
        # (access control allow origin, *) isn't allowed with (...-credentials, true)
        self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
        print("self.headers[\"Origin\"] -> ", self.headers["Origin"])
        self.send_header("Access-Control-Allow-Credentials", "true")
        BaseHTTPRequestHandler.end_headers(self)

    def load_cookie(self):
        if "Cookie" in self.headers:
            print("self.headers['Cookie'] -> ", self.headers["Cookie"])
            self.cookie = cookies.SimpleCookie(self.headers["Cookie"])
        else:
            self.cookie = cookies.SimpleCookie()
            print("self.cookie -> ", self.cookie)

    def sendCookie(self):
        for morsel in self.cookie.values():
            print("morsel -> ", morsel)
            print("morsel.OutputString() -> ", morsel.OutputString())
            self.send_header("Set-Cookie", morsel.OutputString())

    def load_session(self):
        self.load_cookie()
        if "sessionId" in self.cookie:
            # cookie stores the session Id
            sessionId = self.cookie["sessionId"].value
            self.session = gSessionStore.getSessionData(sessionId)
            if self.session == None:
                # session ID no longer found in the session store
                # create a brand new Session ID
                sessionId = gSessionStore.createSession()
                self.session = gSessionStore.getSessionData(sessionId)
                # put the sessionId into the cookie
                self.cookie["sessionId"] = sessionId
        else:
            # no session Id found in the cookie
            # create a brand new session Id
            sessionId = gSessionStore.createSession()
            self.session = gSessionStore.getSessionData(sessionId)
            self.cookie["sessionId"] = sessionId

    def handleGovernorsList(self):
        db = DemocracyDB()
        governors = db.getAllGovernors()
        print(bytes(json.dumps(governors), "utf-8"))
        if json.dumps(governors) == "null":
            self.handleNotFound()
        else:
            self.send_response(200, "OK")
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(governors), "utf-8"))

    def handleGovernorsRetrieve(self, id):
        db = DemocracyDB()
        governors = db.getGovernorsDuties(id)
        print(json.dumps(governors))
        if json.dumps(governors) == "null":
            self.handleNotFound()
        else:
            self.send_response(200, "OK")
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(governors), "utf-8"))

    def handleGovernorsCreate(self):
        length = self.headers["Content-length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        print("the text body", body)
        parsed_body = parse_qs(body)
        print("parsed body is -> ", parsed_body)
        name = parsed_body["name"][0]
        duty = parsed_body["duty"][0]
        # write to database
        db = DemocracyDB()
        db.createGovernorDuty(name, duty)
        self.send_response(201, "Created")
        self.end_headers()

    def handleUsersCreate(self):
        length = self.headers["Content-length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        print("the text body for creating user --- ", body)
        parsed_body = parse_qs(body)
        print("parsed body for creating user is -> ", parsed_body)

        # save the user
        first_name = parsed_body["fName"][0]
        last_name = parsed_body["lName"][0]
        email = parsed_body["email"][0]
        password = parsed_body["password"][0]

        # write to database
        user = UserDB()
        success = user.createNewUser(first_name, last_name, email, password)
        if not success:
            self.handle422()
        else:
            self.send_response(201, "Created")
            self.end_headers()  # sends a cookie to the client

    def handleSessionCreate(self):
        # self.load_session() ??
        length = self.headers["Content-length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        parsed_body = parse_qs(body)

        email = parsed_body["email"][0]
        password = parsed_body["password"][0]
        print("email and password sent over https -> ", email, password)

        db = UserDB()
        user = db.getUserByEmail(email)
        print("user data -> ", user)

        if user == None:
            print("user wasn't found")
            self.send_response(401)
            self.end_headers()
        else:
            if pbkdf2_sha256.verify(password, user["hash"]):
                # remember the user id in the session
                self.session["userId"] = user["user_id"]
                print(self.session)
                self.send_response(201)
                self.end_headers()
            else:
                print("incorrect password")
                self.send_response(401)
                self.end_headers()

    def handleUpdateDuty(self, id):
        length = self.headers["Content-length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        print("the text body", body)
        parsed_body = parse_qs(body)
        print("parsed body is -> ", parsed_body)
        name = parsed_body["name"][0]
        duty = parsed_body["duty"][0]
        # write to database
        db = DemocracyDB()
        rowcount = db.updateDuty(name, duty, id)
        print("row count is ", rowcount)
        if rowcount == 0:
            self.handleNotFound()
        else:
            self.send_response(200)
            self.end_headers()

    def handleNotFound(self):
        self.send_response(404, "NF")
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes("Not found!\n", "utf-8"))

    def handle422(self):
        self.send_response(422)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes("Validation Error\n", "utf-8"))

    def handleLogOut(self):
        del self.session["userId"]
        self.send_response(201)
        self.end_headers()

    def do_OPTIONS(self):
        self.load_session()
        self.send_response(200)
        self.send_header("Access-Control-Allow-Methods",
                         "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-type")
        self.end_headers()

    def deleteGovrDuty(self, id):
        print(id)
        db = DemocracyDB()
        rowcount = db.deleteGovernorDuty(id)
        if rowcount == 0:
            self.handleNotFound()
        else:
            self.send_response(200)
            self.end_headers()

    def isLoggedIn(self):
        if "userId" in self.session:
            return True
        else:
            return False

    def do_GET(self):
        self.load_session()
        print("The path is -> ", self.path)
        parts = self.path.split('/')[1:]
        print("parsed path is -> ", parts)
        collection = parts[0]
        if len(parts) > 1:
            id = parts[1]
        else:
            id = None

        if self.isLoggedIn():
            if collection == "governors":
                if id == None:
                    print("get all duties")
                    self.handleGovernorsList()
                else:
                    print("retrieve one duty")
                    self.handleGovernorsRetrieve(id)
            else:
                self.handleNotFound()
        else:
            print("you are not logged in")
            self.send_response(401)
            self.end_headers()

    def do_PUT(self):
        self.load_session()
        print("The path for do_PUT is -> ", self.path)
        parts = self.path.split('/')[1:]
        print("parsed path for do_PUT is -> ", parts)
        collection = parts[0]
        if len(parts) > 1:
            id = parts[1]
        else:
            self.handleNotFound()

        if self.isLoggedIn():
            if collection == "governors":
                self.handleUpdateDuty(id)
            else:
                self.handleNotFound()
        else:
            print("you are not logged in")
            self.send_response(401)
            self.end_headers()

    def do_POST(self):
        self.load_session()
        if self.path == "/users":
            print("post request to create users")
            self.handleUsersCreate()
        elif self.path == "/governors":
            print("post request")
            # you can only create a govr resource if you are logged in
            if self.isLoggedIn():
                self.handleGovernorsCreate()
            else:
                print("you are not logged in")
                self.send_response(401)
                self.end_headers()

        elif self.path == "/sessions":
            print("authentication")
            self.handleSessionCreate()
        elif self.path == "/logout":
            self.handleLogOut()
        else:
            self.handleNotFound()

    def do_DELETE(self):
        self.load_session()
        print("The path for do_DELETE is -> ", self.path)
        parts = self.path.split('/')[1:]
        print("parsed path for do_DELETE is -> ", parts)
        collection = parts[0]
        if len(parts) > 1:
            id = parts[1]
        else:
            self.handleNotFound()
        if self.isLoggedIn():
            if collection == "governors":
                self.deleteGovrDuty(id)
            else:
                self.handleNotFound()
        else:
            print("you are not logged in")
            self.send_response(401)
            self.end_headers()


def run():
    # If finally works after switching the order of the creation of the two tables
    # why ???
    db = DemocracyDB()
    db.createGovernorTable()
    db = None

    userdb = UserDB()
    userdb.createUserTable()
    userdb = None

    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    listen = ("0.0.0.0", port)
    server = HTTPServer(listen, MyRequestHandler)
    print("Listening...")
    server.serve_forever()


run()

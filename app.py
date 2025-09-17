from flask import Flask, jsonify, request
import jwt
import datetime
import os

app = Flask(__name__)

# Secret key for signing JWTs (use env var in real apps!)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "mysecret")

@app.route("/")
def home():
    return jsonify({"message": "API Testing!"})

@app.route("/echo", methods=["POST"])
def echo():
    data = request.json or {}
    return jsonify({"you_sent": data})

# --- New Login API ---
@app.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")

    # Dummy authentication (replace with DB lookup later)
    if username == "admin" and password == "password123":
        # Generate token valid for 30 minutes
        token = jwt.encode(
            {
                "user": username,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
            },
            app.config["SECRET_KEY"],
            algorithm="HS256"
        )
        return jsonify({"message": "Login successful!", "token": token})
    else:
        return jsonify({"message": "Invalid credentials"}), 401


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # works on Render too
    app.run(host="0.0.0.0", port=port)

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/resume", methods=["POST"])
def resume_agent():
    data = request.get_json()
    task = data.get("task")
    params = data.get("parameters", {})

    if "revise" in task.lower():
        response = "Your resume has been revised with improved bullet points and formatting."
    else:
        response = "Resume draft created based on role: " + params.get("role", "unspecified")

    return jsonify({"resume_response": response})

if __name__ == "__main__":
    app.run(port=5002)
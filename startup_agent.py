from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/startup", methods=["POST"])
def startup_agent():
    data = request.get_json()
    task = data.get("task", "").lower()
    params = data.get("parameters", {})

    industry = params.get("industry", "tech")
    funding = params.get("funding_stage", "pre-seed")
    goal = params.get("goal", "build MVP")

    if "pitch" in task:
        response = f"Drafting pitch deck for a {industry} startup at {funding} stage focused on {goal}."
    elif "mvp" in task or "build" in task:
        response = f"Recommended MVP tools: Firebase, React, GPT API for your {industry} startup."
    else:
        response = f"Startup advisory initialized for {industry}. Please provide more details."

    return jsonify({"startup_advice": response})

if __name__ == "__main__":
    app.run(port=5003)

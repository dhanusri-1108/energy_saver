"""
EnergySaver AI — Flask backend using Google Gemini API.

Run:
    pip install -r requirements.txt
    set your Gemini API key in .env
    python app.py

Then open:
    http://127.0.0.1:5008
"""

import os
import requests
from flask import Flask, render_template, request, jsonify

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


app = Flask(__name__)


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-3.1-flash-lite:generateContent"
)


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are EnergySaver AI, a helpful and friendly energy-saving assistant.

Your main topics are ONLY:
- Electricity usage
- Energy saving tips
- Appliance efficiency
- Electricity bills
- Solar energy
- Rooftop solar
- Renewable energy
- Power consumption
- Energy-efficient practices
- Household electricity saving
- Energy conservation
- Sustainable energy usage

IMPORTANT LANGUAGE INSTRUCTIONS:

1. Always understand English, Tamil, and Tanglish.
2. The user may type completely in English, Tamil, or Tanglish.
3. Always reply in clear and simple ENGLISH.
4. Do NOT reply in Tamil or Tanglish unless the user explicitly asks
   you to reply in Tamil or Tanglish.
5. Understand Tamil written in English letters naturally.
   Example:
   "current bill romba athigama varuthu" means the user is asking
   about a high electricity bill.
6. Keep normal answers around 2-5 sentences.
7. Use simple words that students and general users can understand.

CONTENT INSTRUCTIONS:

8. Give practical and easy-to-follow energy-saving suggestions.
9. When discussing electricity consumption, explain the reason clearly.
10. When useful, give simple examples involving common household
    appliances such as fans, ACs, refrigerators, TVs, lights,
    washing machines, and water heaters.
11. Do not invent exact electricity tariff rates or current bill amounts.
12. Electricity tariffs and solar policies can vary by location and
    change over time. When exact current information is needed,
    advise the user to check their electricity provider or official
    government source.
13. Do not guarantee a specific amount of money saved because actual
    savings depend on usage, tariff, appliance efficiency, and location.
14. For solar-related questions, provide general guidance and clearly
    mention when current local subsidy, installation cost, or policy
    information needs official verification.
15. If the user asks something unrelated to electricity, energy saving,
    appliances, solar, or renewable energy, politely explain that you
    are focused on EnergySaver AI topics.
"""


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def index():
    return render_template(
        "index.html",
        name="EnergySaver AI",
        emoji="⚡",
        tagline="Electricity usage & energy-saving suggestions",
        accent="#B08900"
    )


# ============================================================
# CHAT API
# ============================================================

@app.route("/api/chat", methods=["POST"])
def chat():

    # Check Gemini API key
    if not GEMINI_API_KEY:
        return jsonify({
            "error": (
                "No Gemini API key configured. "
                "Add GEMINI_API_KEY to your .env file and restart app.py."
            )
        }), 400


    # ========================================================
    # GET REQUEST DATA
    # ========================================================

    try:
        data = request.get_json(force=True) or {}

    except Exception:
        return jsonify({
            "error": "Invalid JSON request."
        }), 400


    history = data.get("history", [])


    if not history:
        return jsonify({
            "error": "No message provided."
        }), 400


    # ========================================================
    # CONVERT FRONTEND HISTORY TO GEMINI FORMAT
    # ========================================================

    contents = []

    for message in history:

        role = message.get("role", "")
        content = message.get("content", "")

        if not content:
            continue


        # Gemini uses:
        # user  -> user
        # assistant -> model

        if role == "assistant":
            gemini_role = "model"
        else:
            gemini_role = "user"


        contents.append({
            "role": gemini_role,
            "parts": [
                {
                    "text": content
                }
            ]
        })


    if not contents:
        return jsonify({
            "error": "No valid message found."
        }), 400


    # ========================================================
    # GEMINI REQUEST PAYLOAD
    # ========================================================

    payload = {
        "system_instruction": {
            "parts": [
                {
                    "text": SYSTEM_PROMPT
                }
            ]
        },

        "contents": contents,

        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 500
        }
    }


    # ========================================================
    # SEND REQUEST TO GEMINI
    # ========================================================

    try:

        response = requests.post(
            GEMINI_URL,

            headers={
                "Content-Type": "application/json"
            },

            params={
                "key": GEMINI_API_KEY
            },

            json=payload,

            timeout=30
        )


    except requests.RequestException as e:

        return jsonify({
            "error": f"Could not reach Gemini API: {e}"
        }), 502


    # ========================================================
    # GEMINI API ERROR
    # ========================================================

    if response.status_code != 200:

        return jsonify({
            "error": (
                f"Gemini API error ({response.status_code}): "
                f"{response.text[:500]}"
            )
        }), response.status_code


    # ========================================================
    # READ GEMINI RESPONSE
    # ========================================================

    try:

        result = response.json()

        candidates = result.get("candidates", [])


        if not candidates:

            return jsonify({
                "error": "Gemini returned no response."
            }), 502


        reply = (
            candidates[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
            .strip()
        )


        if not reply:

            reply = "(empty reply)"


    except Exception as e:

        return jsonify({
            "error": f"Invalid response from Gemini: {e}"
        }), 502


    # ========================================================
    # SEND RESPONSE TO FRONTEND
    # ========================================================

    return jsonify({
        "reply": reply
    })


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5008,
        debug=True
    )
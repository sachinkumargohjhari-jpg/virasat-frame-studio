import os
from flask import Flask, request, render_template_string
from google import genai
from google.genai import types

app = Flask(__name__)

PAGE = """
<!doctype html>

"""

def script_banao(topic):
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    prompt = f"""
    तुम एक पेशेवर यूट्यूब स्क्रिप्ट राइटर और फ़ैक्ट-चेकर हो।
    टॉपिक: {topic}

    पहले इंटरनेट पर इस टॉपिक की गहरी रिसर्च करो। सिर्फ़ भरोसेमंद स्रोतों के तथ्य इस्तेमाल करो।
    अगर किसी बात की पुष्टि न हो पाए तो उसे स्क्रिप्ट में मत डालो।

    फिर हिंदी में आठ से दस मिनट के वीडियो की स्क्रिप्ट लिखो, करीब 1200 से 1500 शब्द।
    शुरुआत में ऐसा हुक रखो जो पहले दस सेकंड में ध्यान खींचे।
    स्क्रिप्ट को छोटे सीन में बाँटो। हर सीन में दो चीज़ें लिखो:
    नैरेशन: जो आवाज़ में बोला जाएगा।
    विज़ुअल: स्क्रीन पर क्या दिखेगा।

    आख़िर में उन सभी स्रोतों की सूची दो जिनसे तथ्य लिए गए।
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        ),
    )
    return response.text

@app.route("/", methods=["GET", "POST"])
def home():
    ctx = dict(topic="", script=None, error=None)
    if request.method == "POST":
        ctx["topic"] = request.form["topic"]
        try:
            ctx["script"] = script_banao(ctx["topic"])
        except Exception as e:
            ctx["error"] = f"कुछ गड़बड़ हुई: {e}"
    return render_template_string(PAGE, **ctx)

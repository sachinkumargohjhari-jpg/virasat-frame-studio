import os
from flask import Flask, request, render_template_string
from google import genai
from google.genai import types

app = Flask(__name__)

PAGE = """
<!doctype html>
<html lang="hi">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>विरासत फ्रेम स्टूडियो</title>
  <style>
    body { font-family: sans-serif; max-width: 700px; margin: auto; padding: 16px; background: #faf6ef; }
    h1 { color: #8a3b12; text-align: center; }
    input, button { width: 100%; padding: 12px; margin: 6px 0; font-size: 16px; box-sizing: border-box; }
    button { background: #d97757; color: white; border: none; border-radius: 8px; }
    textarea { width: 100%; height: 450px; font-size: 15px; box-sizing: border-box; }
  </style>
</head>
<body>
  <h1>विरासत फ्रेम स्टूडियो</h1>
  <form method="post">
    <input name="topic" placeholder="वीडियो का टॉपिक लिखिए" value="{{ topic or '' }}" required>
    <button type="submit">रिसर्च करके स्क्रिप्ट बनाओ</button>
  </form>
  {% if script %}
    <h3>स्क्रिप्ट</h3>
    <textarea readonly>{{ script }}</textarea>
  {% endif %}
  {% if error %}
    <p style="color:red">{{ error }}</p>
  {% endif %}
</body>
</html>
"""

def script_banao(topic):
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    prompt = f"""
    तुम एक पेशेवर यूट्यूब स्क्रिप्ट राइटर और फैक्ट-चेकर हो।
    टॉपिक: {topic}
    पहले इंटरनेट पर इस टॉपिक की गहरी रिसर्च करो। सिर्फ़ विश्वसनीय ऐतिहासिक तथ्य इस्तेमाल करो।
    अगर किसी बात की पुष्टि न हो पाए तो उसे स्क्रिप्ट में मत डालो।
    फिर हिंदी में आठ से दस मिनट की वीडियो की स्क्रिप्ट लिखो, करीब 1200 से 1500 शब्द।
    शुरुआत में ऐसा हुक रखो जो पहले दस सेकंड में ध्यान खींचे।
    स्क्रिप्ट को छोटे सीन में बाँटो। हर सीन में ये चीज़ें लिखो:
    वॉइसओवर: जो आवाज़ में बोला जाएगा।
    विज़ुअल्स: स्क्रीन पर क्या दिखेगा।
    आखिर में उन सभी स्रोतों की सूची दो जहाँ से तथ्य लिए गए।
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
    ctx = {"topic": None, "script": None, "error": None}
    if request.method == "POST":
        ctx["topic"] = request.form["topic"]
        try:
            ctx["script"] = script_banao(ctx["topic"])
        except Exception as e:
            ctx["error"] = f"कुछ गड़बड़ हुई: {e}"
    return render_template_string(PAGE, **ctx)
 

from flask import Flask, jsonify, request, render_template_string
from config import Settings
from chatbot import CreditChatbot

app = Flask(__name__)
PAGE = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>GCP Credit Tracker</title>
<style>body{font:16px system-ui;background:#f3f6fb;color:#17212f;margin:0}main{max-width:850px;margin:42px auto;padding:18px}section{background:white;padding:26px;border-radius:14px;box-shadow:0 3px 16px #0001}h1{margin-top:0}input{width:75%;padding:13px;border:1px solid #bac5d3;border-radius:8px}button{padding:13px 20px;background:#2367ca;color:white;border:0;border-radius:8px;cursor:pointer}pre{white-space:pre-wrap;overflow-wrap:anywhere;line-height:1.6;background:#f7f9fc;padding:20px;border-radius:9px}</style><main><section><h1>GCP Credit Tracker</h1><p>See how billing credits were applied to your projects, services and SKUs. Source: your BigQuery billing export.</p><input id="q" value="Which actions used the most of my promotional credits?" aria-label="Question"><button id="ask">Ask</button><pre id="answer">Ready.</pre><p><small>Export usage does not prove the remaining promotional balance. Check Billing → Credits.</small></p></section></main>
<script>document.getElementById('ask').onclick=async()=>{const out=document.getElementById('answer');out.textContent='Loading billing export…';try{const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:document.getElementById('q').value})});const j=await r.json();out.textContent=j.answer||j.error||'Unknown response';}catch(e){out.textContent='Network error';}};</script></html>'''

@app.get('/')
def home():
    return render_template_string(PAGE)

@app.post('/api/chat')
def chat():
    payload = request.get_json(silent=True) or {}
    question = payload.get('question', '')
    if not isinstance(question, str) or not question.strip():
        return jsonify(error='Provide a nonempty text question'), 400
    try:
        answer = CreditChatbot().ask(question)
        return jsonify(answer=answer)
    except Exception:
        app.logger.exception('Billing request failed')
        return jsonify(error='Unable to retrieve billing data. Check server logs and configuration.'), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=False)

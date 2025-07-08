from flask import Flask, request, jsonify
import requests
import os
import time
import threading
from byte import Encrypt_ID, encrypt_api

app = Flask(__name__)

# 🔐 API Key
API_KEY = "xza-free"

# ✅ بيانات الحسابات (uid + password)
ACCOUNTS = [
    {"uid": "3831627617", "password": "CAC2F2F3E2F28C5F5944D502CD171A8AAF84361CDC483E94955D6981F1CFF3E3", "token": None},
    {"uid": "3994866749", "password": "E47897A0E01A6A1F7DFFEE99C4BFC8C727C89F4D2E1AD69DC618DB017", "token": None},
    {"uid": "3994925650", "password": "2FFAD363ABF1E80E9004090C7263D1EB89B6751A21B2C1DAEA2155788", "token": None}
]

# 🧠 تخزين UIDات التي تم إرسال زيارة لها
USED_UIDS = set()

# 🌐 جلب JWT من API خارجي
def fetch_token(uid, password):
    try:
        url = f"https://aditya-jwt-v12op.onrender.com/token?uid={uid}&password={password}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            token = data.get("token", "").strip()
            if token.count('.') == 2:
                return token
    except Exception as e:
        app.logger.warning(f"🚫 خطأ في جلب التوكن لـ UID {uid}: {e}")
    return None

# ♻️ تحديث التوكنات كل ثانيتين
def update_tokens_loop():
    while True:
        for acc in ACCOUNTS:
            token = fetch_token(acc["uid"], acc["password"])
            if token:
                acc["token"] = token
                app.logger.info(f"✅ تم تحديث التوكن لـ UID {acc['uid']}")
        time.sleep(2)

# 🚀 إرسال زيارة (Friend Request)
def send_friend_request(player_id, token):
    try:
        encrypted_id = Encrypt_ID(player_id)
        payload = f"08a7c4839f1e10{encrypted_id}1801"
        encrypted_payload = encrypt_api(payload)
        url = "https://clientbp.ggblueshark.com/RequestAddingFriend"
        headers = {
            "Authorization": f"Bearer {token}",
            "X-Unity-Version": "2018.4.11f1",
            "X-GA": "v1 1",
            "ReleaseVersion": "OB49",
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": str(len(encrypted_payload)),
            "User-Agent": "Dalvik/2.1.0 (Linux; Android 9)",
            "Host": "clientbp.ggblueshark.com",
            "Connection": "close",
            "Accept-Encoding": "gzip, deflate, br"
        }
        requests.post(url, headers=headers, data=bytes.fromhex(encrypted_payload))
    except Exception as e:
        app.logger.warning(f"❌ فشل إرسال زيارة لـ {player_id}: {str(e)}")

# 🌐 API Endpoint: /send-visit
@app.route("/send-visit", methods=["GET"])
def send_visit():
    player_id = request.args.get("uid")
    key = request.args.get("key")

    if not key or key != API_KEY:
        return jsonify({"status": "error", "message": "🔑 API Key غير صحيح"}), 401

    if not player_id:
        return jsonify({"status": "error", "message": "❌ يرجى تحديد UID"}), 400

    if player_id in USED_UIDS:
        return jsonify({"status": "error", "message": "⚠️ هذا اللاعب تم نكحه مسبقاً"}), 409

    # إرسال الزيارة 30 مرة بالتناوب بين الحسابات
    for i in range(30):
        acc = ACCOUNTS[i % len(ACCOUNTS)]
        if acc["token"]:
            send_friend_request(player_id, acc["token"])

    USED_UIDS.add(player_id)

    return jsonify({
        "status": "success",
        "message": f"""✅ تم نكح اللاعب زيارة 🎯
🎯 الايدي: {player_id}
💣 تم تدمير اللاعب بنجاح 💀
🛡️ الزيارة غير قابلة للرد أو القبول ❌
API by: @DeV_Xzanja"""
    })

# 🏁 تشغيل التطبيق (متوافق مع Render)
if __name__ == "__main__":
    threading.Thread(target=update_tokens_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

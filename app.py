from flask import Flask, request, jsonify
import requests
import os
from byte import Encrypt_ID, encrypt_api

app = Flask(__name__)

# ✅ قائمة التوكنات
TOKENS = [
    {
        "uid": "3831627617",
        "token": "CAC2F2F3E2F28C5F5944D502CD171A8AAF84361CDC483E94955D6981F1CFF3E3"
    },
    {
        "uid": "3994866749",
        "token": "E47897A0E01A6A1F7DFFEE99C4BFC8C727C89F4D2E1AD69DC618DB017"
    },
    {
        "uid": "3994925650",
        "token": "2FFAD363ABF1E80E9004090C7263D1EB89B6751A21B2C1DAEA2155788"
    }
]

# 🔒 API Key المسموح به
API_KEY = "xza-free"

# 🛑 قاعدة بيانات مؤقتة (قائمة UIDs المرسلة)
USED_UIDS = set()

# ✅ دالة إرسال الزيارة
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

        response = requests.post(url, headers=headers, data=bytes.fromhex(encrypted_payload))
        if response.status_code == 200:
            return "✅ تم إرسال الزيارة بنجاح"
        else:
            return f"⚠️ فشل الإرسال: {response.status_code} - {response.text}"

    except Exception as e:
        return f"🚫 خطأ أثناء الإرسال: {str(e)}"

# 🌐 نقطة الوصول الرئيسية
@app.route("/send-visit", methods=["GET"])
def send_visit():
    player_id = request.args.get("uid")
    key = request.args.get("key")

    # التحقق من المفتاح
    if not key or key != API_KEY:
        return jsonify({
            "status": "error",
            "message": "🔑 المفتاح غير صحيح أو مفقود!"
        }), 401

    # التحقق من uid
    if not player_id:
        return jsonify({
            "status": "error",
            "message": "❌ يرجى تحديد معرف اللاعب (uid)"
        }), 400

    # التحقق من التكرار
    if player_id in USED_UIDS:
        return jsonify({
            "status": "error",
            "message": "⚠️ هذا الحساب تم إرسال زيارة له مسبقاً."
        }), 409

    # تنفيذ الإرسال
    results = []
    for token_data in TOKENS:
        result = send_friend_request(player_id, token_data["token"])
        results.append({
            "sender_uid": token_data["uid"],
            "result": result
        })

    # حفظ UID لتجنب التكرار
    USED_UIDS.add(player_id)

    return jsonify({
        "status": "success",
        "target_player": player_id,
        "results": results
    })

# 🚀 تشغيل السيرفر (متوافق مع Render)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
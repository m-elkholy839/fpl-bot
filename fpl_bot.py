import requests
from datetime import datetime, timezone

# --- إعداداتك ---
TOPIC_NAME = "mahmoud2026"
MY_TEAM_ID = 8610005

def send_alert(msg):
    try:
        # شيلنا الـ Title العربي من هنا خالص عشان نتفادى الإيرور
        requests.post(f"https://ntfy.sh/{TOPIC_NAME}", 
                      data=msg.encode('utf-8'),
                      headers={
                          "Priority": "high", 
                          "Tags": "soccer"
                      })
    except Exception as e:
        print(f"فشل في إرسال الإشعار: {e}")

def run_fpl_engine():
    try:
        # 1. سحب البيانات العامة
        r = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
        data = r.json()
        
        # معرفة الجولة الحالية
        current_gw = next((e for e in data['events'] if e['is_current']), data['events'][0])
        
        # 2. سحب تشكيلتك (عشان نراقب أهدافك)
        picks_r = requests.get(f"https://fantasy.premierleague.com/api/entry/{MY_TEAM_ID}/event/{current_gw['id']}/picks/")
        my_picks = [p['element'] for p in picks_r.json().get('picks', [])]
        
        # 3. تجهيز التقرير (العنوان العربي بقى جوه الرسالة)
        top_3 = sorted(data['elements'], key=lambda x: x['event_points'], reverse=True)[:3]
        
        report = f"📌 تحديث فانتازي جديد\n"
        report += f"✅ السيستم شغال يا حودة من السحاب!\n"
        report += f"🌟 توب الجولة حالياً: " + ", ".join([p['web_name'] for p in top_3])
        
        send_alert(report)
        print("تم تشغيل الكود بنجاح!")

    except Exception as e:
        print(f"حصلت مشكلة: {e}")
        # رسالة الخطأ برضه تبقى إنجليزي في الـ Header
        send_alert(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    run_fpl_engine()

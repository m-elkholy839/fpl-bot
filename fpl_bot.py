import requests
from datetime import datetime, timezone

# الإعدادات
TOPIC_NAME = "mahmoud2026"
MY_TEAM_ID = 8610005

def send_alert(title, msg):
    requests.post(f"https://ntfy.sh/{TOPIC_NAME}", 
                  data=msg.encode('utf-8'),
                  headers={"Title": title, "Priority": "high", "Tags": "alarm_clock,soccer"})

def get_fpl_updates():
    url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    data = requests.get(url).json()
    
    # جلب الديدلاين الجاي
    next_event = next(e for e in data['events'] if e['is_next'])
    deadline_str = next_event['deadline_time'] # UTC time
    deadline_dt = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    
    # حساب الفرق بالوقت
    diff = deadline_dt - now
    hours_left = diff.total_seconds() / 3600

    # 1. تنبيه الـ 24 ساعة
    if 23 <= hours_left < 24:
        msg = f"⏰ يا حودة، فاضل 24 ساعة على الديدلاين!\nجهز تشكيلتك يا بطل لماتشات {next_event['name']}."
        send_alert("تنبيه الـ 24 ساعة 🚨", msg)

    # 2. تنبيه الساعة الأخيرة
    elif 0 <= hours_left < 1:
        msg = f"🏃‍♂️ إلحق يا عالمي! فاضل ساعة واحدة والديدلاين يقفل.\nتأكد من الكابتن والدكة فوراً!"
        send_alert("تنبيه الساعة الأخيرة ⚠️", msg)

    # 3. ملخص التألق (لو مفيش ديدلاين قريب)
    # ممكن نخليه يبعت ملخص أفضل لعيبة لو السكريبت اشتغل في ميعاد ثابت
    else:
        top_players = sorted(data['elements'], key=lambda x: x['event_points'], reverse=True)[:3]
        names = [f"{p['web_name']} ({p['event_points']} pt)" for p in top_players]
        msg = f"🌟 وحوش الجولة دي لحد دلوقتي:\n" + "\n".join(names)
        # هنا هيبعت بس لو إنت شغلت البوت يدوي أو في ميعاد ثابت
        print("تشغيل روتيني: " + msg)

if __name__ == "__main__":
    get_fpl_updates()

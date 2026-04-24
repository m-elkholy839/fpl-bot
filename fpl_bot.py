import requests
import sys
from datetime import datetime, timezone

# --- إعداداتك ---
TOPIC_NAME = "mahmoud2026"
MY_TEAM_ID = 8610005

def send_alert(title, msg, tags="soccer"):
    requests.post(f"https://ntfy.sh/{TOPIC_NAME}", 
                  data=msg.encode('utf-8'),
                  headers={"Title": title, "Priority": "high", "Tags": tags})

def run_fpl_engine():
    # 1. سحب البيانات
    data = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/").json()
    player_names = {p['id']: p['web_name'] for p in data['elements']}
    current_gw = next(e for e in data['events'] if e['is_current'])
    
    # 2. سحب تشكيلتك (بتتحدث لوحدها لو غيرت أي حاجة)
    picks_url = f"https://fantasy.premierleague.com/api/entry/{MY_TEAM_ID}/event/{current_gw['id']}/picks/"
    my_picks = [p['element'] for p in requests.get(picks_url).json()['picks']]
    
    # 3. فحص الأهداف والإنذارات (Live)
    live_url = f"https://fantasy.premierleague.com/api/event/{current_gw['id']}/live/"
    live_data = requests.get(live_url).json()['elements']
    alerts = []
    for p in live_data:
        if p['id'] in my_picks:
            stats = p['explain'][0]['stats'] if p['explain'] else []
            for s in stats:
                if s['identifier'] in ['goals_scored', 'assists', 'red_cards'] and s['value'] > 0:
                    action = "جول! ⚽" if s['identifier'] == 'goals_scored' else "أسيست 🅰️"
                    if s['identifier'] == 'red_cards': action = "كارت أحمر 🟥"
                    alerts.append(f"{player_names[p['id']]}: {action}")

    if alerts:
        send_alert("تحديث لايف لفرقتك 🔥", "\n".join(alerts))

    # 4. تنبيهات المواعيد (الديدلاين ونشرة 9 مساءً)
    next_gw = next(e for e in data['events'] if e['is_next'])
    deadline_dt = datetime.strptime(next_gw['deadline_time'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    hours_left = (deadline_dt - datetime.now(timezone.utc)).total_seconds() / 3600
    now_hour = datetime.now(timezone.utc).hour

    # شرط إرسال التقرير: (لو ميعاد ديدلاين) أو (الساعة 9 بالليل) أو (لو إنت شغلته يدوي حالا)
    # إحنا هنخلي أي تشغيل يدوي يبعت "تقرير الحالة"
    is_manual = True # ده افتراضي عشان يبعتلك لما تدوس Run حالا
    
    report_msg = ""
    if 23 <= hours_left < 24:
        report_msg = f"⏰ فاضل 24 ساعة على ديدلاين {next_gw['name']}!"
    elif 0 <= hours_left < 1:
        report_msg = f"⚠️ إلحق! ساعة واحدة والديدلاين يقفل!"
    elif now_hour == 18 or is_manual: # 18 UTC يعني 9 بتوقيت مصر
        top_3 = sorted(data['elements'], key=lambda x: x['event_points'], reverse=True)[:3]
        report_msg = f"📊 وضعك الحالي:\n- جولة: {current_gw['name']}\n🌟 توب الجولة: " + ", ".join([p['web_name'] for p in top_3])

    if report_msg:
        send_alert("تقرير الفانتازي 📋", report_msg, "mag")

if __name__ == "__main__":
    run_fpl_engine()

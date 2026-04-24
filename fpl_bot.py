import requests
import sys
from datetime import datetime, timezone

# --- إعداداتك يا وحش ---
TOPIC_NAME = "mahmoud2026"

def send_alert(msg):
    requests.post(f"https://ntfy.sh/{TOPIC_NAME}", 
                  data=msg.encode('utf-8'),
                  headers={"Priority": "high", "Tags": "white_check_mark,soccer"})

def is_match_day():
    try:
        r = requests.get("https://fantasy.premierleague.com/api/fixtures/").json()
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        return any(f['kickoff_time'].startswith(today) for f in r)
    except: return False

def run_fpl_logic():
    try:
        r_base = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/").json()
        now_hour = datetime.now(timezone.utc).hour
        
        # 1. فحص الديدلاين
        next_gw = next((e for e in r_base['events'] if e['is_next']), r_base['events'][0])
        deadline_dt = datetime.strptime(next_gw['deadline_time'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
        hours_left = (deadline_dt - datetime.now(timezone.utc)).total_seconds() / 3600
        
        if 23 <= hours_left < 24:
            send_alert(f"⏰ يا حودة، فاضل 24 ساعة على ديدلاين {next_gw['name']}!")

        # 2. النشرة اليومية (بتبعت لوحدها الساعة 9 بالليل لو فيه ماتشات)
        if now_hour == 18 and is_match_day():
            top_5 = sorted(r_base['elements'], key=lambda x: x['event_points'], reverse=True)[:5]
            report = "🌟 ملخص ماتشات النهاردة:\n"
            for p in top_5:
                report += f"- {p['web_name']}: {p['event_points']} pt\n"
            send_alert(report)

        # 3. الحتة دي عشانك "عشان لما تدوس Run يدوي" يبعتلك حالا
        # لو الساعة مش 9 بالليل ومش وقت ديدلاين، هيبعتلك رسالة تأكيد
        if now_hour != 18 and not (23 <= hours_left < 24):
            send_alert("✅ السيستم صاحي ومنتظر المواعيد يا هندسة!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_fpl_logic()

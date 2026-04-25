import requests
from datetime import datetime, timezone

TOPIC_NAME = "mahmoud2026"

def send_alert(msg):
    requests.post(f"https://ntfy.sh/{TOPIC_NAME}", 
                  data=msg.encode('utf-8'),
                  headers={"Priority": "high", "Tags": "soccer,star2"})

def run_fpl_logic():
    try:
        r_base = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/").json()
        # توقيت جرينتش (9 مساءً مصر = 18 جرينتش)
        now_hour = datetime.now(timezone.utc).hour 
        
        # 1. الديدلاين (شرط مرن)
        next_gw = next((e for e in r_base['events'] if e['is_next']), None)
        if next_gw:
            deadline_dt = datetime.strptime(next_gw['deadline_time'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
            hours_left = (deadline_dt - datetime.now(timezone.utc)).total_seconds() / 3600
            if 23 <= hours_left <= 25:
                send_alert(f"⏰ Deadline: 24h left for {next_gw['name']}!")

        # 2. النشرة (من 9 لـ 12 بليل بتوقيت مصر)
        if 18 <= now_hour <= 21:
            r_fix = requests.get("https://fantasy.premierleague.com/api/fixtures/").json()
            today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
            if any(f['kickoff_time'].startswith(today) for f in r_fix):
                top_5 = sorted(r_base['elements'], key=lambda x: x['event_points'], reverse=True)[:5]
                if top_5[0]['event_points'] > 0:
                    report = "📊 FPL Matchday Report:\n" + "\n".join([f"- {p['web_name']}: {p['event_points']} pts" for p in top_5])
                    send_alert(report)
                else:
                    print("Matches exist but points not updated yet.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_fpl_logic()

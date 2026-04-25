import requests
from datetime import datetime, timezone

TOPIC_NAME = "mahmoud2026"

def send_alert(msg):
    requests.post(f"https://ntfy.sh/{TOPIC_NAME}", 
                  data=msg.encode('utf-8'),
                  headers={"Priority": "high", "Tags": "soccer,star2,rocket"})

def run_fpl_logic():
    try:
        # بنسحب الداتا الحقيقية حالا
        r_base = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/").json()
        teams = {t['id']: t['name'] for t in r_base['teams']}
        
        # بنجيب وحوش اليوم (السبت)
        top_5 = sorted(r_base['elements'], key=lambda x: x['event_points'], reverse=True)[:5]
        
        if top_5[0]['event_points'] > 0:
            report = "🎁 نشرة السبت (وصلت متأخر بس وصلت):\n"
            for p in top_5:
                p_team = teams[p['team']]
                report += f"- {p['web_name']} ({p_team}): {p['event_points']} pts\n"
            send_alert(report)
        else:
            send_alert("🎮 مفيش نقط اتسجلت لسه، بس البوت شغال يا هندسة!")

    except Exception as e:
        send_alert(f"⚠️ حصل مشكلة: {str(e)}")

if __name__ == "__main__":
    run_fpl_logic()

import requests
from datetime import datetime, timezone

# --- إعداداتك ---
TOPIC_NAME = "mahmoud2026"

def send_alert(msg):
    requests.post(f"https://ntfy.sh/{TOPIC_NAME}", 
                  data=msg.encode('utf-8'),
                  headers={"Priority": "high", "Tags": "star2,soccer,trophy"})

def is_match_day():
    try:
        r = requests.get("https://fantasy.premierleague.com/api/fixtures/").json()
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        return any(f['kickoff_time'].startswith(today) for f in r)
    except: return False

def run_fpl_logic():
    try:
        r_base = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/").json()
        teams = {t['id']: t['name'] for t in r_base['teams']}
        positions = {pt['id']: pt['singular_name_short'] for pt in r_base['element_types']}
        
        next_gw = next((e for e in r_base['events'] if e['is_next']), r_base['events'][0])
        deadline_dt = datetime.strptime(next_gw['deadline_time'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
        hours_left = (deadline_dt - datetime.now(timezone.utc)).total_seconds() / 3600
        now_hour = datetime.now(timezone.utc).hour

        # 1. فحص الديدلاين (رسالة واحدة فقط)
        if 23 <= hours_left < 24:
            send_alert(f"⏰ يا حودة، فاضل 24 ساعة على ديدلاين {next_gw['name']}!")
        
        # 2. النشرة اليومية 9 مساءً (بتتبعت بس لو فيه ماتشات)
        elif now_hour == 18 and is_match_day():
            top_5 = sorted(r_base['elements'], key=lambda x: x['event_points'], reverse=True)[:5]
            top_report = "\n🌟 وحوش الجولة حالياً:\n"
            for p in top_5:
                p_team = teams[p['team_code_next'] if 'team_code_next' in p else p['team']]
                p_pos = positions[p['element_type']]
                top_report += f"- [{p_pos}] {p['web_name']} ({p_team}): {p['event_points']} pt\n"
            
            send_alert(f"📊 ملخص 9 مساءً يا إكسلانس\n{top_report}")

        # الـ else اللي كانت بتزعجك كل ساعة اتمسحت للأبد!

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_fpl_logic()

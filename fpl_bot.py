import requests
from datetime import datetime, timezone, timedelta

# --- إعداداتك يا هندسة ---
TOPIC_NAME = "mahmoud2026"

def send_alert(msg):
    requests.post(f"https://ntfy.sh/{TOPIC_NAME}", 
                  data=msg.encode('utf-8'),
                  headers={"Priority": "high", "Tags": "calendar,soccer"})

def is_match_day():
    # بيعرف لو فيه ماتشات النهاردة
    try:
        r = requests.get("https://fantasy.premierleague.com/api/fixtures/").json()
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        # بيشوف لو أي ماتش ميعاده النهاردة
        return any(f['kickoff_time'].startswith(today) for f in r)
    except:
        return False

def run_fpl_logic():
    try:
        r_base = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/").json()
        
        # 1. فحص الديدلاين (تنبيه الـ 24 ساعة فقط)
        next_gw = next((e for e in r_base['events'] if e['is_next']), r_base['events'][0])
        deadline_dt = datetime.strptime(next_gw['deadline_time'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
        hours_left = (deadline_dt - datetime.now(timezone.utc)).total_seconds() / 3600
        
        if 23 <= hours_left < 24:
            send_alert(f"⏰ يا حودة، فاضل 24 ساعة بالظبط على ديدلاين {next_gw['name']}. ظبط دنيتك!")

        # 2. نشرة 9 مساءً - بتبعت بس لو فيه ماتشات النهاردة
        now_hour = datetime.now(timezone.utc).hour
        if now_hour == 18: # 18 UTC = 9 مساءً بتوقيت مصر
            if is_match_day():
                teams = {t['id']: t['name'] for t in r_base['teams']}
                top_5 = sorted(r_base['elements'], key=lambda x: x['event_points'], reverse=True)[:5]
                
                report = "🌟 ملخص ماتشات النهاردة في الفانتازي:\n"
                for p in top_5:
                    p_team = teams[p['team_code_next'] if 'team_code_next' in p else p['team']]
                    report += f"- {p['web_name']} ({p_team}): {p['event_points']} pt\n"
                send_alert(report)
            else:
                print("مفيش ماتشات النهاردة، مش هبعت نشرة.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_fpl_logic()

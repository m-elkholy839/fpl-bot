import requests
from datetime import datetime, timezone

# --- إعداداتك يا وحش ---
TOPIC_NAME = "mahmoud2026"

def send_alert(msg):
    requests.post(f"https://ntfy.sh/{TOPIC_NAME}", 
                  data=msg.encode('utf-8'),
                  headers={"Priority": "high", "Tags": "star2,soccer,trophy"})

def run_fpl_logic():
    try:
        # 1. سحب البيانات العامة، الأندية، والمراكز
        r_base = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/").json()
        
        teams = {t['id']: t['name'] for t in r_base['teams']}
        # قاموس للمراكز (GKP, DEF, MID, FWD)
        positions = {pt['id']: pt['singular_name_short'] for pt in r_base['element_types']}
        
        # 2. تجهيز التوب 5 بالمركز والنادي والنقط
        top_5 = sorted(r_base['elements'], key=lambda x: x['event_points'], reverse=True)[:5]
        top_report = "\n🌟 وحوش الجولة حالياً:\n"
        for p in top_5:
            p_team = teams[p['team_code_next'] if 'team_code_next' in p else p['team']]
            p_pos = positions[p['element_type']]
            top_report += f"- [{p_pos}] {p['web_name']} ({p_team}): {p['event_points']} pt\n"

        # 3. فحص الديدلاين
        next_gw = next((e for e in r_base['events'] if e['is_next']), r_base['events'][0])
        deadline_dt = datetime.strptime(next_gw['deadline_time'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
        hours_left = (deadline_dt - datetime.now(timezone.utc)).total_seconds() / 3600
        
        now_hour = datetime.now(timezone.utc).hour

        # السيناريوهات:
        if 23 <= hours_left < 24:
            send_alert(f"⏰ يا حودة، فاضل 24 ساعة على ديدلاين {next_gw['name']}!\n{top_report}")
        
        elif now_hour == 18: # نشرة 9 مساءً الأوتوماتيكية
            send_alert(f"📊 ملخص 9 مساءً يا إكسلانس\n{top_report}")
        
        else:
            # لما تدوس Run يدوي في أي وقت
            send_alert(f"✅ السيستم صاحي وبيرسل لك الخلاصة:\n{top_report}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_fpl_logic()

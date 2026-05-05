import csv
import json
import re
import math
from datetime import datetime, timedelta
import urllib.request
import urllib.parse
import os

def get_access_token():
    with open('/Users/claw/.config/gogcli/credentials.json', 'r') as f:
        creds = json.load(f)
    with open('/Users/claw/.openclaw/workspace/token.json', 'r') as f:
        token_info = json.load(f)
    url = "https://oauth2.googleapis.com/token"
    data = urllib.parse.urlencode({
        "client_id": creds["client_id"],
        "client_secret": creds["client_secret"],
        "refresh_token": token_info["refresh_token"],
        "grant_type": "refresh_token"
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        return res["access_token"]

def download_sheet_csv(access_token, sheet_id, out_name):
    url = f"https://www.googleapis.com/drive/v3/files/{sheet_id}/export?mimeType=text/csv"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {access_token}"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = resp.read().decode('utf-8')
            with open(out_name, "w") as f:
                f.write(data)
            print(f"Saved {out_name}")
    except Exception as e:
        print(f"Error fetching {out_name}: {e}")

def parse_val(s, regex):
    if not s: return 0.0
    m = re.search(regex, s)
    if m:
        try:
            return float(m.group(1).replace(',', ''))
        except:
            return 0.0
    return 0.0

def load_workouts(filename):
    workouts = {}
    if not os.path.exists(filename):
        return workouts
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            clean_row = {k.strip() if isinstance(k, str) else k: v for k, v in row.items()}
            
            if 'Date' not in clean_row: continue
            date_str = clean_row['Date'].strip()
            if not date_str: continue
            
            w_type = clean_row.get('Type', '').strip()
            if 'Running' not in w_type and 'Trail' not in w_type and 'Run' not in w_type:
                continue
                
            try:
                dt = datetime.strptime(date_str, '%m/%d/%Y').date()
            except:
                try:
                    dt = datetime.strptime(date_str, '%Y-%m-%d').date()
                except:
                    continue

            dist = parse_val(clean_row.get('Distance', ''), r'([\d\.]+)')
            vert = parse_val(clean_row.get('Elevation Gain', ''), r'([\d\.]+)')
            trimp = parse_val(clean_row.get('TRIMP', ''), r'([\d\.]+)')
            
            tss = trimp if trimp > 0 else dist * 12.0
            
            if dt not in workouts:
                workouts[dt] = {'tss': 0, 'dist': 0, 'vert': 0}
            workouts[dt]['tss'] += tss
            workouts[dt]['dist'] += dist
            workouts[dt]['vert'] += vert
            
    return workouts

def main():
    try:
        at = get_access_token()
        download_sheet_csv(at, '1pklJqakRMo3pDgBVi68ZvLxv5mSgm076y-Xv5M3XG6k', 'workouts_v5.csv')
        download_sheet_csv(at, '1Mev-f-VYgwQq87CtQWQZdBfSow9HBBVc5J8BTx3wodU', 'workouts_v2.csv')
    except Exception as e:
        print("Using local CSVs if fetch failed:", e)

    w1 = load_workouts('workouts_v5.csv')
    w2 = load_workouts('workouts_v2.csv')
    
    combined = {}
    for dt, data in w1.items(): combined[dt] = data
    for dt, data in w2.items():
        if dt not in combined:
            combined[dt] = data
        else:
            combined[dt]['tss'] += data['tss']
            combined[dt]['dist'] += data['dist']
            combined[dt]['vert'] += data['vert']
            
    if not combined:
        print("No workouts parsed.")
        return
        
    dates = sorted(combined.keys())
    start_date = dates[0]
    end_date = dates[-1] + timedelta(days=30)
    
    current_date = start_date
    ctl = 0.0
    atl = 0.0
    pmc_data = []
    weekly_stats = {}
    
    while current_date <= end_date:
        d = combined.get(current_date, {'tss': 0, 'dist': 0, 'vert': 0})
        tss = d['tss']
        
        ctl = ctl + (tss - ctl) * (1.0 - math.exp(-1.0 / 42.0))
        atl = atl + (tss - atl) * (1.0 - math.exp(-1.0 / 7.0))
        tsb = ctl - atl
        
        iso_year, iso_week, _ = current_date.isocalendar()
        week_key = f"{iso_year}-W{iso_week:02d}"
        
        if week_key not in weekly_stats:
            weekly_stats[week_key] = {'dist': 0, 'vert': 0}
        
        weekly_stats[week_key]['dist'] += d['dist']
        weekly_stats[week_key]['vert'] += d['vert']
        
        pmc_data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'tss': round(tss, 1),
            'ctl': round(ctl, 1),
            'atl': round(atl, 1),
            'tsb': round(tsb, 1)
        })
        current_date += timedelta(days=1)
        
    hood_start = datetime(2026, 5, 11).date()
    hood_plan = []
    
    plan_targets = [
        [28, 500], [30, 1000], [32, 1500], [38, 2000], [42, 2500],
        [45, 3000], [28, 1000], [48, 3000], [55, 5000], [35, 1500],
        [35, 2000], [25, 1000], [54, 8700]
    ]
    
    for i, targets in enumerate(plan_targets):
        wk_start = hood_start + timedelta(weeks=i)
        iso_year, iso_week, _ = wk_start.isocalendar()
        week_key = f"{iso_year}-W{iso_week:02d}"
        
        actual = weekly_stats.get(week_key, {'dist': 0, 'vert': 0})
        
        hood_plan.append({
            'week_number': i + 1,
            'week_start': wk_start.strftime('%Y-%m-%d'),
            'target_miles': targets[0],
            'actual_miles': round(actual['dist'], 1),
            'target_vert': targets[1],
            'actual_vert': round(actual['vert'], 1)
        })

    out = {
        'pmc': pmc_data,
        'hood_plan': hood_plan,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    with open('training_data.json', 'w') as f:
        json.dump(out, f, indent=2)
        
    print("Generated training_data.json")

if __name__ == "__main__":
    main()

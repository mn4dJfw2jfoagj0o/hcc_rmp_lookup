import tkinter as tk
from tkinter import ttk, messagebox
import requests
import base64
import re
import threading

BASE_URL = "https://www.ratemyprofessors.com/graphql"
SCHOOL_NUM = "2184"
school_id = base64.b64encode(f"School-{SCHOOL_NUM}".encode()).decode()

JS_CODE = "copy([...new Set(Array.from(document.querySelectorAll(\"span[id^='SSR_CLSRCH_F_WK_SSR_INSTR_LONG']\"), el => el.innerText.trim()))].filter(name => Boolean(name) && !name.includes('Staff') && !name.includes('To be Announced')));"

session = requests.Session()
session.headers.update({
    "Authorization": "Basic dGVzdDp0ZXN0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json"
})

CACHE = {}

def clean_name(name: str) -> str:
    name = re.sub(r'\(.*?\)', '', name)
    name = re.sub(r'[^\w\s]', '', name)
    return re.sub(r'\s+', ' ', name).strip()

def search_by_name(name: str):
    if name in CACHE:
        return CACHE[name]

    data = {
        "query": f'''
        query {{
          newSearch {{
            teachers(query: {{text: "{name}", schoolID: "{school_id}"}}) {{
              edges {{
                node {{
                  firstName
                  lastName
                  avgRating
                  numRatings
                  avgDifficulty
                  wouldTakeAgainPercent
                }}
              }}
            }}
          }}
        }}
        '''
    }
    try:
        res = session.post(BASE_URL, json=data, timeout=5).json()
        teachers = res.get("data", {}).get("newSearch", {}).get("teachers", {}).get("edges", [])
        CACHE[name] = teachers
        return teachers
    except Exception:
        return []

def parse_names(raw_text):
    quoted = re.findall(r'["\']([^"\']+)["\']', raw_text)
    if quoted:
        return [q.strip() for q in quoted if q.strip()]
    raw_text = re.sub(r'[\[\]]', '', raw_text)
    return [s.strip() for s in re.split(r'[\n,]+', raw_text) if s.strip()]

def copy_js_to_clipboard():
    root.clipboard_clear()
    root.clipboard_append(JS_CODE)
    root.update()
    btn_copy_js.config(text="✓ Copied to Clipboard!")
    root.after(1500, lambda: btn_copy_js.config(text="📋 Copy JS Extraction Code"))

def clear_input_block():
    text_input.delete("1.0", tk.END)
    lbl_status.config(text="")

def start_query_thread():
    raw_text = text_input.get("1.0", tk.END).strip()
    names = list(dict.fromkeys(parse_names(raw_text)))
    if not names:
        messagebox.showwarning("Notice", "Please paste professor names into the box first!")
        return
    
    btn_query.config(state=tk.DISABLED)
    for row in tree.get_children():
        tree.delete(row)
    
    threading.Thread(target=run_query, args=(names,), daemon=True).start()

def run_query(names):
    results = []
    total = len(names)
    
    for i, orig_name in enumerate(names):
        root.after(0, lambda idx=i, n=orig_name: lbl_status.config(text=f"Fetching ({idx+1}/{total}): {n}..."))
        
        query_n = clean_name(orig_name)
        teachers = search_by_name(query_n)
        
        if teachers:
            prof = teachers[0]["node"]
            results.append({
                "name": orig_name,
                "rating": prof.get("avgRating") or 0.0,
                "reviews": prof.get("numRatings") or 0,
                "diff": prof.get("avgDifficulty") or 0.0,
                "take_again": prof.get("wouldTakeAgainPercent", -1)
            })
        else:
            results.append({
                "name": orig_name,
                "rating": -1.0,
                "reviews": 0,
                "diff": -1.0,
                "take_again": -1
            })
            
    results.sort(key=lambda x: (x["rating"], x["reviews"]), reverse=True)
    
    root.after(0, lambda: render_results(results, total))

def render_results(results, total):
    for r in results:
        if r["rating"] < 0:
            tree.insert("", tk.END, values=(r["name"], "Not Found", "-", "-", "-"))
        else:
            ta = r["take_again"]
            ta_str = f"{round(ta)}%" if ta is not None and ta >= 0 else "N/A"
            tree.insert("", tk.END, values=(r["name"], f"{r['rating']:.1f}", r["reviews"], f"{r['diff']:.1f}", ta_str))
            
    found_count = len([r for r in results if r['rating'] >= 0])
    lbl_status.config(text=f"Done! Found {found_count} / {total} professors.")
    btn_query.config(state=tk.NORMAL)

# --- GUI Construction ---
root = tk.Tk()
root.title("RateMyProfessors Quick Lookup")
root.geometry("720x600")
root.minsize(640, 460)

# Instructions
frame_guide = tk.LabelFrame(root, text=" Instructions ", font=("Arial", 11, "bold"), padx=12, pady=8)
frame_guide.pack(fill=tk.X, padx=15, pady=8)

guide_text = (
    "1. Go to the course search page showing all sections/instructors.\n"
    "2. Press F12 (Windows: Ctrl+Shift+I | Mac: Cmd+Option+I) → Console.\n"
    "3. Click the button below to copy the JS code, paste into Console & press Enter.\n"
    "4. Paste the copied output into the box below and click 'Search Ratings'."
)
tk.Label(frame_guide, text=guide_text, justify=tk.LEFT, font=("Arial", 10), fg="#333").pack(anchor="w")

btn_copy_js = tk.Button(frame_guide, text="📋 Copy JS Extraction Code", font=("Arial", 10, "bold"), bg="#f0f0f0", command=copy_js_to_clipboard)
btn_copy_js.pack(anchor="w", pady=(6, 2))

# Input Box
frame_input = tk.Frame(root, padx=15, pady=4)
frame_input.pack(fill=tk.X)

tk.Label(frame_input, text="Paste Professor Names (Console format supported):", font=("Arial", 11, "bold")).pack(anchor="w")
text_input = tk.Text(frame_input, height=4, font=("Arial", 10))
text_input.pack(fill=tk.X, pady=4)

# Actions
frame_actions = tk.Frame(root, padx=15, pady=4)
frame_actions.pack(fill=tk.X)

btn_query = tk.Button(frame_actions, text="🔍 Search Ratings", font=("Arial", 11, "bold"), bg="#0066cc", fg="black", padx=10, pady=4, command=start_query_thread)
btn_query.pack(side=tk.LEFT)

btn_clear = tk.Button(frame_actions, text="🗑 Clear Input", font=("Arial", 10), padx=8, pady=4, command=clear_input_block)
btn_clear.pack(side=tk.LEFT, padx=8)

lbl_status = tk.Label(frame_actions, text="", font=("Arial", 10), fg="#555")
lbl_status.pack(side=tk.LEFT, padx=8)

# Table Container (Dedicated Vertical Scrollbar only)
frame_table = tk.Frame(root, padx=15, pady=8)
frame_table.pack(fill=tk.BOTH, expand=True)

columns = ("name", "rating", "reviews", "diff", "take_again")

v_scrollbar = ttk.Scrollbar(frame_table, orient=tk.VERTICAL)
v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

tree = ttk.Treeview(
    frame_table,
    columns=columns,
    show="headings",
    yscrollcommand=v_scrollbar.set
)
v_scrollbar.config(command=tree.yview)

tree.heading("name", text="Professor")
tree.heading("rating", text="Rating")
tree.heading("reviews", text="Reviews")
tree.heading("diff", text="Difficulty")
tree.heading("take_again", text="Take Again")

tree.column("name", width=220, minwidth=160)
tree.column("rating", width=90, minwidth=70, anchor="center")
tree.column("reviews", width=90, minwidth=70, anchor="center")
tree.column("diff", width=90, minwidth=70, anchor="center")
tree.column("take_again", width=120, minwidth=90, anchor="center")

tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

root.mainloop()
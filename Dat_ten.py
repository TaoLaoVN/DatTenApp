import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import unidecode
import unicodedata
import os
import random
import webbrowser
import urllib.parse
import sys, os

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
self.dict_csv = tk.StringVar(value=resource_path("HANVIET.csv"))

# --- CẤU HÌNH NGŨ HÀNH ---
NGU_HANH_SINH = {
    "Kim": "Thủy", "Thủy": "Mộc", "Mộc": "Hỏa", "Hỏa": "Thổ", "Thổ": "Kim"
}
NGU_HANH_KHAC = {
    "Kim": "Mộc", "Mộc": "Thổ", "Thổ": "Thủy", "Thủy": "Hỏa", "Hỏa": "Kim"
}

NUMEROLOGY_MEANINGS = {
    1: "Lãnh đạo, độc lập. Dễ thành công tài chính.",
    2: "Hợp tác, ngoại giao. Tốt bụng, yêu thương.",
    3: "Sáng tạo, hài hước. Có năng khiếu nghệ thuật.",
    4: "Kỷ luật, kiên định. Có óc tổ chức.",
    5: "Tự do, linh hoạt. Thích khám phá.",
    6: "Trách nhiệm, gia đình. Thích chăm sóc.",
    7: "Thông minh, tri thức. Nhà nghiên cứu.",
    8: "Tham vọng, thực tế. Lãnh đạo tài chính.",
    9: "Nhân ái, cống hiến. Hướng tới cộng đồng.",
    11: "Trực giác cao, truyền cảm hứng.",
    22: "Kiến tạo đại tài. Biến ước mơ thành hiện thực."
}

NUM_MAP = {
    'A': 1, 'J': 1, 'S': 1, 'B': 2, 'K': 2, 'T': 2, 'C': 3, 'L': 3, 'U': 3,
    'D': 4, 'M': 4, 'V': 4, 'E': 5, 'N': 5, 'W': 5, 'F': 6, 'O': 6, 'X': 6,
    'G': 7, 'P': 7, 'Y': 7, 'H': 8, 'Q': 8, 'Z': 8, 'I': 9, 'R': 9
}
VOWELS = set(['A', 'E', 'I', 'O', 'U', 'Y'])

# --- HÀM PHỤ TRỢ AN TOÀN ---
def safe_float(value, default=0.0):
    """Chuyển đổi sang số an toàn, tránh lỗi crash app"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

# --- LOGIC TÍNH TOÁN ---

def reduce_sum(n):
    while n > 9 and n not in [11, 22, 33]:
        n = sum(int(d) for d in str(n))
    return n

def calculate_life_path(day, month, year):
    return reduce_sum(reduce_sum(day) + reduce_sum(month) + reduce_sum(year))

def get_numerology_full(full_name):
    clean_name = unidecode.unidecode(full_name).upper().replace(" ", "")
    soul_sum = 0
    personality_sum = 0
    for char in clean_name:
        val = NUM_MAP.get(char, 0)
        if char in VOWELS: soul_sum += val
        else: personality_sum += val
    expression = reduce_sum(soul_sum + personality_sum)
    return {"Expression": expression, "Meaning": NUMEROLOGY_MEANINGS.get(expression, "")}

def get_tone_nature(word):
    normalized = unicodedata.normalize('NFD', word)
    trac_marks = ['\u0301', '\u0309', '\u0303', '\u0323'] 
    return 'T' if any(mark in normalized for mark in trac_marks) else 'B'

def evaluate_yin_yang(name_parts):
    tones = [get_tone_nature(w) for w in name_parts]
    sequence = "-".join(tones)
    num_B, num_T = tones.count('B'), tones.count('T')
    if num_B == 0 or num_T == 0: return 0, sequence, "Mất cân bằng"
    elif num_B == num_T: return 20, sequence, "Cân bằng tuyệt đối"
    else: return 15, sequence, "Hài hòa"

def get_menh_nam_sinh(year):
    can_dict = {4:1, 5:1, 6:2, 7:2, 8:3, 9:3, 0:4, 1:4, 2:5, 3:5}
    rem = year % 12
    val_chi = 0 if rem in [4, 5, 10, 11] else (1 if rem in [6, 7, 0, 1] else 2)
    total = can_dict[year % 10] + val_chi
    if total > 5: total -= 5
    return {1: "Kim", 2: "Thủy", 3: "Hỏa", 4: "Thổ", 5: "Mộc"}.get(total, "Unknown")

def check_element_compatibility(name_element, year_element):
    if not name_element or name_element not in NGU_HANH_SINH: return 10
    
    if NGU_HANH_SINH.get(name_element) == year_element: return 20 # Tên sinh Năm (Vượng)
    if name_element == year_element: return 18 # Tương hòa
    if NGU_HANH_SINH.get(year_element) == name_element: return 15 # Năm sinh Tên
        
    if NGU_HANH_KHAC.get(name_element) == year_element: return 0 # Khắc
    if NGU_HANH_KHAC.get(year_element) == name_element: return 5 # Khắc
        
    return 10

def score_full_name_final(name_parts, hv_dict, life_path, birth_day_num, gender, req1, req2, year_element):
    full_name = " ".join(name_parts)
    score = 0
    detail = {}
    
    han_chars = []
    meanings = []
    total_polarity = 0
    total_element_score = 0
    valid_elements = 0
    
    # Duyệt các chữ trong tên (trừ Họ)
    for word in name_parts[1:]: 
        word_lower = word.lower()
        info = hv_dict.get(word_lower)
        
        if info:
            han_chars.append(str(info.get('han_char', '')))
            meanings.append(str(info.get('meaning_short', '')))
            
            # 1. Điểm Polarity (Dùng safe_float để tránh lỗi)
            pol = safe_float(info.get('polarity', 0))
            total_polarity += pol
            
            # 2. Điểm Ngũ hành
            elem = str(info.get('element_hint', '')).strip()
            if elem:
                e_score = check_element_compatibility(elem, year_element)
                total_element_score += e_score
                valid_elements += 1
                
            # 3. Điểm Priority (Dùng safe_float để tránh lỗi 'Hỏa')
            prio = safe_float(info.get('priority', 3))
            if prio >= 4: score += 5
            
            # 4. Check từ khóa (Vibe tags)
            tags = str(info.get('vibe_tags', '')).lower()
            if req1 != "--- Không chọn ---" and req1.lower() in tags: score += 15
            if req2 != "--- Không chọn ---" and req2.lower() in tags: score += 15
            
        else:
            han_chars.append("?")
            meanings.append("?")
    
    # Tổng hợp điểm
    score += (total_polarity * 8) 
    detail["Năng lượng từ"] = round(total_polarity * 8, 1)

    # Ngũ hành trung bình
    if valid_elements > 0:
        avg_element_score = total_element_score / valid_elements
        score += avg_element_score
        detail["Ngũ Hành"] = round(avg_element_score, 1)
    else:
        detail["Ngũ Hành"] = 0

    # Âm Sắc
    tones = [get_tone_nature(w) for w in name_parts]
    if tones.count('B') == len(tones) or tones.count('T') == len(tones): sound_score = 5
    else:
        if gender == "Nữ" and tones[-1] == 'B': sound_score = 20
        elif gender == "Nam" and tones[-1] == 'T': sound_score = 20
        else: sound_score = 15
    score += sound_score
    detail["Âm Sắc"] = sound_score

    # Thần Số
    num_data = get_numerology_full(full_name)
    exp = num_data["Expression"]
    if exp in [2, 6, 9, 11, 22]: num_score = 20
    elif exp in [1, 3, 5, 8]: num_score = 15
    else: num_score = 10
    score += num_score
    detail["Thần Số"] = num_score

    # Bonus
    bonus = 0
    if exp == life_path: bonus += 10
    if exp == birth_day_num: bonus += 5
    score += bonus
    detail["Thưởng"] = bonus

    han_string = " ".join(han_chars)
    meaning_string = " | ".join([m for m in meanings if m != "?"])

    return {
        "Full Name": full_name,
        "HanViet": han_string,
        "Score": round(score, 1),
        "Breakdown": detail,
        "NumDisplay": f"Số {exp}",
        "Meaning": meaning_string,
        "NameParts": name_parts
    }

# --- GIAO DIỆN ---

class NameAppFinal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Đặt Tên Con - Hán Việt Dictionary (Đã Fix Lỗi Dữ Liệu)")
        self.geometry("1400x900")
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
        style.configure("Treeview", font=('Arial', 10), rowheight=45)
        
        self.dict_csv = tk.StringVar(value="HANVIET.csv")
        self.ho_cha = tk.StringVar()
        self.gioi_tinh = tk.StringVar(value="Nữ")
        
        self.mong_muon_1 = tk.StringVar(value="--- Không chọn ---")
        self.mong_muon_2 = tk.StringVar(value="--- Không chọn ---")
        
        self.day = tk.IntVar(value=1)
        self.month = tk.IntVar(value=1)
        self.year = tk.IntVar(value=2025)
        self.status_var = tk.StringVar(value="Sẵn sàng.")
        
        self.hv_dictionary = {}
        self.create_widgets()
        
    def create_widgets(self):
        panel = ttk.LabelFrame(self, text="Cấu Hình", padding=15)
        panel.pack(fill="x", padx=10, pady=5)
        
        r1 = tk.Frame(panel)
        r1.pack(fill="x", pady=5)
        ttk.Label(r1, text="File Dữ Liệu:").pack(side="left")
        ttk.Entry(r1, textvariable=self.dict_csv, width=30).pack(side="left", padx=5)
        ttk.Button(r1, text="📂 Tải Dữ Liệu", command=self.load_data).pack(side="left")
        
        ttk.Label(r1, text="Họ Cha:").pack(side="left", padx=(30, 5))
        ttk.Entry(r1, textvariable=self.ho_cha, width=15, font=('Arial', 11, 'bold')).pack(side="left")
        
        r2 = tk.Frame(panel)
        r2.pack(fill="x", pady=5)
        ttk.Label(r2, text="Giới tính:").pack(side="left")
        ttk.Radiobutton(r2, text="Nam", variable=self.gioi_tinh, value="Nam").pack(side="left", padx=5)
        ttk.Radiobutton(r2, text="Nữ", variable=self.gioi_tinh, value="Nữ").pack(side="left")
        
        ttk.Label(r2, text="Ngày sinh (DL):").pack(side="left", padx=(30, 5))
        ttk.Spinbox(r2, from_=1, to=31, textvariable=self.day, width=3).pack(side="left")
        ttk.Label(r2, text="/").pack(side="left")
        ttk.Spinbox(r2, from_=1, to=12, textvariable=self.month, width=3).pack(side="left")
        ttk.Label(r2, text="/").pack(side="left")
        ttk.Entry(r2, textvariable=self.year, width=6).pack(side="left", padx=5)
        
        r3 = ttk.LabelFrame(panel, text="Mong muốn (Tự động load từ file)", padding=5)
        r3.pack(fill="x", pady=10)
        self.combo1 = ttk.Combobox(r3, textvariable=self.mong_muon_1, state="readonly", width=25)
        self.combo1.pack(side="left", padx=5)
        ttk.Label(r3, text="+").pack(side="left")
        self.combo2 = ttk.Combobox(r3, textvariable=self.mong_muon_2, state="readonly", width=25)
        self.combo2.pack(side="left", padx=5)
        
        ttk.Button(r3, text="🚀 TÌM TÊN", command=self.generate).pack(side="left", padx=30, fill="x", expand=True)
        
        res_frame = ttk.LabelFrame(self, text="Kết Quả (Kèm Ngũ Hành & Chữ Hán)", padding=10)
        res_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        cols = ("name", "hanviet", "score", "breakdown", "num_id", "meaning")
        self.tree = ttk.Treeview(res_frame, columns=cols, show="headings")
        self.tree.heading("name", text="Họ Tên")
        self.tree.column("name", width=160)
        self.tree.heading("hanviet", text="Hán Tự")
        self.tree.column("hanviet", width=100, anchor="center")
        self.tree.heading("score", text="Điểm")
        self.tree.column("score", width=60, anchor="center")
        self.tree.heading("breakdown", text="Chi Tiết (Năng lượng | Ngũ hành...)")
        self.tree.column("breakdown", width=250, anchor="w")
        self.tree.heading("num_id", text="Thần Số")
        self.tree.column("num_id", width=80, anchor="center")
        self.tree.heading("meaning", text="Ý Nghĩa Ngắn")
        self.tree.column("meaning", width=400)
        
        scroll = ttk.Scrollbar(res_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        
        self.tree.bind("<Double-1>", self.show_popup)
        ttk.Label(self, textvariable=self.status_var, foreground="blue").pack(side="bottom", anchor="w", padx=10)
        
        self.current_data = {}

    def load_data(self):
        fn = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if not fn: return
        self.dict_csv.set(fn)
        
        try:
            df = pd.read_csv(fn)
            df.columns = [c.strip().lower() for c in df.columns]
            
            # --- LOGIC TỰ ĐỘNG SỬA LỖI CỘT BỊ LỆCH ---
            # Kiểm tra nếu cột priority chứa chữ (ví dụ: 'Thổ', 'Kim') thay vì số
            # thì nghĩa là cột đã bị lệch do lỗi file CSV (vibe_tags bị tách đôi)
            if 'priority' in df.columns and df['priority'].dtype == 'O':
                unique_vals = df['priority'].astype(str).unique()
                elements = {'Kim', 'Mộc', 'Thủy', 'Hỏa', 'Thổ'}
                # Nếu tìm thấy ngũ hành trong cột priority -> Chắc chắn bị lệch
                if any(e in unique_vals for e in elements):
                    print("Phát hiện lỗi lệch cột trong CSV. Đang tự động sửa...")
                    # 1. Gộp phần bị tách vào vibe_tags
                    df['vibe_tags'] = df['vibe_tags'].astype(str) + ',' + df['element_hint'].astype(str)
                    # 2. Đẩy các cột về đúng vị trí
                    df['element_hint'] = df['priority']
                    df['priority'] = df['notes'] # Cột notes chứa priority thực
                    # Cột notes coi như trống
            # ----------------------------------------

            self.hv_dictionary = {}
            tags_set = set()
            
            for _, row in df.iterrows():
                if row.get('name_safe', 1) == 0: continue
                
                word = str(row.get('han_viet', '')).strip().lower()
                if word:
                    self.hv_dictionary[word] = row.to_dict()
                    t_str = str(row.get('vibe_tags', ''))
                    for t in t_str.split(','):
                        t = t.strip()
                        if t: tags_set.add(t)
            
            vals = ["--- Không chọn ---"] + sorted(list(tags_set))
            self.combo1['values'] = vals
            self.combo2['values'] = vals
            
            messagebox.showinfo("OK", f"Đã tải {len(self.hv_dictionary)} từ vựng. Đã tự động sửa lỗi lệch cột.")
            
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def generate(self):
        if not self.hv_dictionary:
            self.load_data()
            if not self.hv_dictionary: return
            
        ho = self.ho_cha.get().strip()
        if not ho: 
            messagebox.showwarning("Lỗi", "Chưa nhập Họ cha!")
            return

        gender = self.gioi_tinh.get()
        req1, req2 = self.mong_muon_1.get(), self.mong_muon_2.get()
        d, m, y = self.day.get(), self.month.get(), self.year.get()
        
        menh = get_menh_nam_sinh(y)
        lp = calculate_life_path(d, m, y)
        bd = reduce_sum(d)
        
        self.status_var.set(f"Đang tìm tên cho bé {gender} - Mệnh {menh}...")
        self.update_idletasks()
        
        valid_words = []
        for w, info in self.hv_dictionary.items():
            gh = str(info.get('gender_hint', 'Trung')).strip().title()
            if gender == "Nữ" and gh == "Nam": continue
            if gender == "Nam" and gh == "Nữ": continue
            valid_words.append(w)
            
        if len(valid_words) < 10:
            messagebox.showwarning("Ít dữ liệu", "Không đủ từ vựng phù hợp tiêu chí!")
            return
            
        random.shuffle(valid_words)
        results = []
        seen = set()
        count = 0
        
        priority_words = [w for w in valid_words if 
                          (req1 != "--- Không chọn ---" and req1.lower() in str(self.hv_dictionary[w].get('vibe_tags','')).lower()) or
                          (req2 != "--- Không chọn ---" and req2.lower() in str(self.hv_dictionary[w].get('vibe_tags','')).lower())]
        
        if not priority_words: priority_words = valid_words[:20]
        
        for w1 in priority_words:
            partners = random.sample(valid_words, min(len(valid_words), 15))
            for w2 in partners:
                if w1 == w2: continue
                
                parts = ho.split() + [w1.title(), w2.title()]
                full = " ".join(parts)
                if full in seen: continue
                
                data = score_full_name_final(parts, self.hv_dictionary, lp, bd, gender, req1, req2, menh)
                
                if data['Score'] >= 65:
                    results.append(data)
                    seen.add(full)
                    self.current_data[full] = data
            
            count += 1
            if count > 100: break
            
        results.sort(key=lambda x: x['Score'], reverse=True)
        
        for item in self.tree.get_children(): self.tree.delete(item)
        for r in results[:100]:
            bk = r['Breakdown']
            bk_str = f"NL:{bk['Năng lượng từ']} | NgũHành:{bk['Ngũ Hành']} | Âm:{bk['Âm Sắc']}"
            self.tree.insert("", "end", values=(
                r['Full Name'], r['HanViet'], r['Score'], bk_str, r['NumDisplay'], r['Meaning']
            ))
            
        self.status_var.set(f"Hoàn tất. Tìm thấy {len(results)} tên.")

    def show_popup(self, event):
        item = self.tree.selection()
        if not item: return
        val = self.tree.item(item, "values")
        name = val[0]
        data = self.current_data.get(name)
        
        top = tk.Toplevel(self)
        top.title(name)
        top.geometry("600x450")
        
        tk.Label(top, text=name, font=('Arial', 18, 'bold'), fg="red").pack(pady=10)
        tk.Label(top, text=data['HanViet'], font=('SimSun', 24)).pack()
        
        search = " ".join(data['NameParts'][1:])
        link = f"https://hvdic.thivien.net/hv/{urllib.parse.quote(search)}"
        tk.Button(top, text="🌐 Tra cứu ThiVien.net", command=lambda: webbrowser.open(link), bg="#4CAF50", fg="white").pack(pady=5)
        
        f = ttk.LabelFrame(top, text="Điểm chi tiết", padding=10)
        f.pack(fill="x", padx=10)
        for k,v in data['Breakdown'].items():
            tk.Label(f, text=f"{k}: {v}", font=('Arial', 10, 'bold')).pack(anchor="w")

if __name__ == "__main__":
    app = NameAppFinal()
    app.mainloop()
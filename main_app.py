import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import os
import webbrowser
from datetime import date
import pandas as pd

from seo_core import generate_metadata
from sitemap_management import load_sitemap_mapping, save_sitemap_mapping
from utils import extract_brand_country_and_lancode, collect_alt_texts
# 'generate_final_shareable_report' 임포트 구문 제거
from report_generator import generate_html_report

class SEOAuditApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SEO Audit 실행기")
        self.root.geometry("800x700")

        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, font=("Segoe UI", 10))
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.sitemap_data = load_sitemap_mapping()

        self.create_main_tab()
        self.create_sitemap_tab()

    def log_message(self, message, tag=None):
        self.log_output.config(state='normal')
        self.log_output.insert(tk.END, message, tag)
        self.log_output.see(tk.END)
        self.log_output.config(state='disabled')
        self.root.update_idletasks()

    def create_main_tab(self):
        tab_main = ttk.Frame(self.notebook)
        self.notebook.add(tab_main, text="🔍 실행")

        frame_exec = ttk.LabelFrame(tab_main, text="실행 정보 입력", padding=(20, 10))
        frame_exec.pack(pady=(15, 5), padx=20, fill="x", anchor="center")

        ttk.Label(frame_exec, text="🎫 티켓 이름", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", padx=(0, 10), pady=5)
        self.ticket_entry = ttk.Entry(frame_exec, width=50)
        self.ticket_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(frame_exec, text="🌐 Audit URL 입력", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="nw", padx=(0, 10), pady=5)
        self.url_text = scrolledtext.ScrolledText(frame_exec, height=8, width=50, font=("Segoe UI", 10))
        self.url_text.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        frame_exec.grid_columnconfigure(1, weight=1)

        # 버튼 하나만 있도록 원래대로 수정
        ttk.Button(tab_main, text="🚀 Audit 실행", command=self.on_execute).pack(pady=(5,10))

        log_frame = ttk.LabelFrame(tab_main, text="실행 로그", padding=10)
        log_frame.pack(pady=10, padx=20, fill="both", expand=True)
        self.log_output = scrolledtext.ScrolledText(log_frame, height=10, font=("Consolas", 9), bg="#f0f0f0", fg="#333", state='disabled')
        self.log_output.pack(fill="both", expand=True)
        self.log_output.tag_configure("INFO", foreground="blue")
        self.log_output.tag_configure("WARN", foreground="orange")
        self.log_output.tag_configure("ERROR", foreground="red")

    def create_sitemap_tab(self):
        tab_map = ttk.Frame(self.notebook)
        self.notebook.add(tab_map, text="🗺️ 사이트맵 매핑")

        frame_map = ttk.LabelFrame(tab_map, text="사이트맵 매핑 목록", padding=10)
        frame_map.pack(fill="both", expand=True, padx=15, pady=(15, 5))

        self.tree = ttk.Treeview(frame_map, columns=("domain", "sitemap"), show="headings", height=15)
        self.tree.heading("domain", text="Domain")
        self.tree.heading("sitemap", text="Sitemap URL")
        self.tree.column("domain", width=250)
        self.tree.column("sitemap", width=400)
        self.tree.pack(fill="both", expand=True)

        for domain, sitemap in self.sitemap_data.items():
            self.tree.insert("", "end", values=(domain, sitemap))

        self.tree.bind("<Double-1>", self.on_double_click_sitemap_tree)

        button_frame = ttk.Frame(tab_map)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="➕ 추가", command=self.add_sitemap_row).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="🗑️ 삭제", command=self.delete_sitemap_row).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="✏️ 수정", command=self.edit_sitemap_row).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="💾 저장", command=self.save_sitemap_data).grid(row=0, column=3, padx=5)

    def on_double_click_sitemap_tree(self, event):
        item_id = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        if not item_id or col not in ("#1", "#2"):
            return
        
        column_index = int(col.replace('#', '')) - 1

        x, y, width, height = self.tree.bbox(item_id, col)
        entry_popup = tk.Entry(self.tree)
        entry_popup.place(x=x, y=y, width=width, height=height)
        entry_popup.insert(0, self.tree.set(item_id, col))
        entry_popup.focus()

        def save_edit(event):
            current_values = list(self.tree.item(item_id, 'values'))
            current_values[column_index] = entry_popup.get()
            self.tree.item(item_id, values=current_values)
            entry_popup.destroy()

        entry_popup.bind("<Return>", save_edit)
        entry_popup.bind("<FocusOut>", lambda e: entry_popup.destroy())

    def add_sitemap_row(self):
        self.tree.insert("", "end", values=("", ""))

    def delete_sitemap_row(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("삭제 경고", "삭제할 항목을 선택해주세요.")
            return
        for item in selected_items:
            self.tree.delete(item)

    def edit_sitemap_row(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("수정 경고", "수정할 항목을 선택해주세요.")
            return
        
        item_id = selected_item[0]
        current_domain, current_sitemap = self.tree.item(item_id, 'values')

        new_domain = simpledialog.askstring("수정", "도메인:", initialvalue=current_domain)
        if new_domain is None: 
            return
        
        new_sitemap = simpledialog.askstring("수정", "사이트맵 URL:", initialvalue=current_sitemap)
        if new_sitemap is None: 
            return
            
        self.tree.item(item_id, values=(new_domain, new_sitemap))

    def save_sitemap_data(self):
        updated_mapping = {}
        for i in self.tree.get_children():
            domain, sitemap = self.tree.item(i)["values"]
            if domain and sitemap:
                updated_mapping[domain] = sitemap
        
        save_sitemap_mapping(updated_mapping)
        self.sitemap_data = updated_mapping
        messagebox.showinfo("저장 완료", "사이트맵 매핑이 sitemap_mapping.json 파일로 저장되었습니다.")

    def on_execute(self):
        ticket_name = self.ticket_entry.get().strip()
        urls_raw = self.url_text.get("1.0", "end").strip()
        urls = [u.strip() for u in urls_raw.splitlines() if u.strip()]

        self.log_message("\n--- Audit Started ---\n", "INFO")

        if not urls:
            messagebox.showwarning("입력 오류", "Audit할 URL을 입력해주세요.")
            self.log_message("[ERROR] No URLs provided for audit.\n", "ERROR")
            return
        
        if not ticket_name:
            messagebox.showwarning("입력 오류", "티켓 이름을 입력해주세요.")
            self.log_message("[ERROR] No ticket name provided.\n", "ERROR")
            return

        messagebox.showinfo("Audit 시작", f"티켓명: {ticket_name}\n총 {len(urls)}개 URL Audit을 시작합니다. 로그 창을 확인하세요.")

        all_results = []
        all_alt_data = []

        current_sitemap_mapping = self.sitemap_data 

        for url in urls:
            self.log_message(f"\n[INFO] Processing URL: {url}\n", "INFO")
            meta = generate_metadata(url, current_sitemap_mapping, self.log_output)
            df_url = pd.DataFrame([
                {"URL": url, "항목": k, **v} for k, v in meta.items()
            ])

            audit_url_value = df_url.loc[df_url['항목'] == 'Audit_URL', '현황'].iloc[0] if 'Audit_URL' in df_url['항목'].values else None
            if audit_url_value == url:
                df_url = df_url[df_url['항목'] != 'Audit_URL']
            
            all_results.append(df_url)

            alt_data_for_url = collect_alt_texts(url, self.log_output)
            all_alt_data.extend(alt_data_for_url)
            
        if not all_results:
            messagebox.showerror("Audit 결과", "처리할 URL이 없거나 데이터 추출에 실패했습니다.")
            self.log_message("[ERROR] No audit results generated.\n", "ERROR")
            return

        final_df = pd.concat(all_results, ignore_index=True)
        alt_df = pd.DataFrame(all_alt_data)

        today_date = date.today().strftime("%y%m%d")
        output_dir = "./audit_reports"
        os.makedirs(output_dir, exist_ok=True)
        
        brand, country, lan = extract_brand_country_and_lancode(urls[0])
        lan_suffix = f"_{lan}" if lan else ""
        report_filename = f"SEO-audit_Report_{ticket_name}_{brand}-{country}{lan_suffix}_{today_date}.html"
        output_path = os.path.join(output_dir, report_filename)

        generate_html_report(ticket_name, urls, final_df, alt_df, output_path)

        messagebox.showinfo("Audit 완료", f"Audit이 완료되었으며, 결과가 다음 파일에 저장되었습니다:\n{output_path}")
        self.log_message(f"\n[INFO] Audit completed. Report saved to: {output_path}\n", "INFO")
        
        webbrowser.open(f"file://{os.path.abspath(output_path)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SEOAuditApp(root)
    root.mainloop()
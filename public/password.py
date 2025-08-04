import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import secrets
import string
import hashlib
from cryptography.fernet import Fernet
import pyperclip
import re
from datetime import datetime, timedelta

class PasswordManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("안전한 비밀번호 관리자")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # 데이터 파일 경로
        self.data_file = "passwords.enc"
        self.key_file = "master.key"
        
        # 암호화 관련
        self.cipher = None
        self.master_password = None
        self.data = {}
        
        # UI 초기화
        self.setup_ui()
        
        # 프로그램 시작 시 마스터 비밀번호 확인
        self.authenticate()
        
    def setup_ui(self):
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 제목
        title_label = ttk.Label(main_frame, text="🔐 비밀번호 관리자", 
                               font=('Arial', 18, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 검색 프레임
        search_frame = ttk.Frame(main_frame)
        search_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(search_frame, text="검색:").grid(row=0, column=0, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_entries)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.grid(row=0, column=1, padx=(0, 10))
        
        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=2, sticky=tk.E)
        
        ttk.Button(button_frame, text="새 항목 추가", 
                  command=self.add_entry).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="비밀번호 생성", 
                  command=self.generate_password).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(button_frame, text="보안 점검", 
                  command=self.security_check).grid(row=0, column=2)
        
        # 트리뷰 (목록 표시)
        self.tree = ttk.Treeview(main_frame, columns=('service', 'username', 'email', 'created'), 
                                show='headings', height=15)
        
        # 컬럼 설정
        self.tree.heading('service', text='서비스')
        self.tree.heading('username', text='사용자명')
        self.tree.heading('email', text='이메일')
        self.tree.heading('created', text='생성일')
        
        self.tree.column('service', width=200)
        self.tree.column('username', width=150)
        self.tree.column('email', width=200)
        self.tree.column('created', width=100)
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        scrollbar.grid(row=2, column=2, sticky=(tk.N, tk.S), pady=(10, 0))
        
        # 더블클릭 이벤트
        self.tree.bind('<Double-1>', self.on_item_double_click)
        self.tree.bind('<Button-3>', self.show_context_menu)  # 우클릭
        
        # 컨텍스트 메뉴
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="비밀번호 복사", command=self.copy_password)
        self.context_menu.add_command(label="사용자명 복사", command=self.copy_username)
        self.context_menu.add_command(label="수정", command=self.edit_entry)
        self.context_menu.add_command(label="삭제", command=self.delete_entry)
        
        # 상태바
        self.status_var = tk.StringVar()
        self.status_var.set("준비")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
    def generate_key(self):
        """암호화 키 생성"""
        return Fernet.generate_key()
        
    def get_cipher(self, master_password):
        """마스터 비밀번호로부터 암호화 객체 생성"""
        key_salt = b'password_manager_salt_2024'
        key = hashlib.pbkdf2_hmac('sha256', master_password.encode(), key_salt, 100000)
        fernet_key = key[:32]
        # Fernet 키 형식으로 변환
        import base64
        fernet_key = base64.urlsafe_b64encode(fernet_key)
        return Fernet(fernet_key)
        
    def authenticate(self):
        """마스터 비밀번호 인증"""
        if os.path.exists(self.data_file):
            # 기존 사용자
            while True:
                password = simpledialog.askstring("인증", "마스터 비밀번호를 입력하세요:", show='*')
                if password is None:
                    self.root.quit()
                    return
                    
                try:
                    self.cipher = self.get_cipher(password)
                    self.load_data()
                    self.master_password = password
                    self.status_var.set(f"로그인 완료 - {len(self.data)}개 항목")
                    break
                except:
                    messagebox.showerror("오류", "잘못된 비밀번호입니다.")
        else:
            # 새 사용자
            password = simpledialog.askstring("설정", "새 마스터 비밀번호를 설정하세요:", show='*')
            if password is None:
                self.root.quit()
                return
                
            if len(password) < 8:
                messagebox.showerror("오류", "마스터 비밀번호는 8자 이상이어야 합니다.")
                self.authenticate()
                return
                
            confirm = simpledialog.askstring("확인", "비밀번호를 다시 입력하세요:", show='*')
            if password != confirm:
                messagebox.showerror("오류", "비밀번호가 일치하지 않습니다.")
                self.authenticate()
                return
                
            self.master_password = password
            self.cipher = self.get_cipher(password)
            self.data = {}
            self.save_data()
            self.status_var.set("새 계정이 생성되었습니다.")
            
        self.refresh_tree()
        
    def load_data(self):
        """암호화된 데이터 로드"""
        try:
            with open(self.data_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.cipher.decrypt(encrypted_data)
            self.data = json.loads(decrypted_data.decode())
        except:
            raise Exception("데이터 로드 실패")
            
    def save_data(self):
        """데이터 암호화 저장"""
        try:
            json_data = json.dumps(self.data, ensure_ascii=False, indent=2)
            encrypted_data = self.cipher.encrypt(json_data.encode())
            
            with open(self.data_file, 'wb') as f:
                f.write(encrypted_data)
                
            # 백업 파일도 생성
            backup_file = f"{self.data_file}.backup"
            with open(backup_file, 'wb') as f:
                f.write(encrypted_data)
                
        except Exception as e:
            messagebox.showerror("오류", f"데이터 저장 실패: {e}")
            
    def add_entry(self):
        """새 항목 추가"""
        dialog = EntryDialog(self.root, "새 항목 추가")
        if dialog.result:
            entry_id = str(len(self.data) + 1)
            self.data[entry_id] = dialog.result
            self.data[entry_id]['created'] = datetime.now().strftime("%Y-%m-%d")
            self.save_data()
            self.refresh_tree()
            self.status_var.set("새 항목이 추가되었습니다.")
            
    def edit_entry(self):
        """항목 수정"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("경고", "수정할 항목을 선택하세요.")
            return
            
        item = self.tree.item(selected[0])
        entry_id = item['values'][0]  # 첫 번째 값이 ID
        
        # 현재 데이터로 다이얼로그 초기화
        current_data = None
        for key, value in self.data.items():
            if value.get('service') == entry_id or key == entry_id:
                current_data = value
                entry_key = key
                break
                
        if current_data:
            dialog = EntryDialog(self.root, "항목 수정", current_data)
            if dialog.result:
                self.data[entry_key] = dialog.result
                self.data[entry_key]['created'] = current_data.get('created', datetime.now().strftime("%Y-%m-%d"))
                self.save_data()
                self.refresh_tree()
                self.status_var.set("항목이 수정되었습니다.")
                
    def delete_entry(self):
        """항목 삭제"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("경고", "삭제할 항목을 선택하세요.")
            return
            
        if messagebox.askyesno("확인", "정말로 이 항목을 삭제하시겠습니까?"):
            item = self.tree.item(selected[0])
            service_name = item['values'][0]
            
            # 해당 항목 찾아서 삭제
            to_delete = None
            for key, value in self.data.items():
                if value.get('service') == service_name:
                    to_delete = key
                    break
                    
            if to_delete:
                del self.data[to_delete]
                self.save_data()
                self.refresh_tree()
                self.status_var.set("항목이 삭제되었습니다.")
                
    def copy_password(self):
        """비밀번호 클립보드 복사"""
        selected = self.tree.selection()
        if not selected:
            return
            
        item = self.tree.item(selected[0])
        service_name = item['values'][0]
        
        for value in self.data.values():
            if value.get('service') == service_name:
                pyperclip.copy(value.get('password', ''))
                self.status_var.set("비밀번호가 클립보드에 복사되었습니다. (30초 후 자동 삭제)")
                # 30초 후 클립보드 클리어
                self.root.after(30000, lambda: pyperclip.copy(''))
                break
                
    def copy_username(self):
        """사용자명 클립보드 복사"""
        selected = self.tree.selection()
        if not selected:
            return
            
        item = self.tree.item(selected[0])
        username = item['values'][1]
        pyperclip.copy(username)
        self.status_var.set("사용자명이 클립보드에 복사되었습니다.")
        
    def refresh_tree(self):
        """트리뷰 새로고침"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for entry in self.data.values():
            self.tree.insert('', 'end', values=(
                entry.get('service', ''),
                entry.get('username', ''),
                entry.get('email', ''),
                entry.get('created', '')
            ))
            
    def filter_entries(self, *args):
        """검색 필터링"""
        search_term = self.search_var.get().lower()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for entry in self.data.values():
            if (search_term in entry.get('service', '').lower() or 
                search_term in entry.get('username', '').lower() or
                search_term in entry.get('email', '').lower()):
                self.tree.insert('', 'end', values=(
                    entry.get('service', ''),
                    entry.get('username', ''),
                    entry.get('email', ''),
                    entry.get('created', '')
                ))
                
    def on_item_double_click(self, event):
        """더블클릭 시 비밀번호 복사"""
        self.copy_password()
        
    def show_context_menu(self, event):
        """우클릭 컨텍스트 메뉴"""
        self.context_menu.post(event.x_root, event.y_root)
        
    def generate_password(self):
        """비밀번호 생성기"""
        dialog = PasswordGeneratorDialog(self.root)
        
    def security_check(self):
        """보안 점검"""
        weak_passwords = []
        duplicate_passwords = []
        old_passwords = []
        
        passwords = {}
        for key, entry in self.data.items():
            password = entry.get('password', '')
            service = entry.get('service', '')
            created = entry.get('created', '')
            
            # 약한 비밀번호 체크
            if len(password) < 8:
                weak_passwords.append(service)
            elif not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password) or not re.search(r'\d', password):
                weak_passwords.append(service)
                
            # 중복 비밀번호 체크
            if password in passwords:
                duplicate_passwords.extend([passwords[password], service])
            else:
                passwords[password] = service
                
            # 오래된 비밀번호 체크 (6개월 이상)
            try:
                created_date = datetime.strptime(created, "%Y-%m-%d")
                if datetime.now() - created_date > timedelta(days=180):
                    old_passwords.append(service)
            except:
                pass
                
        # 결과 표시
        report = "🔍 보안 점검 결과\n\n"
        
        if weak_passwords:
            report += f"⚠️ 약한 비밀번호 ({len(weak_passwords)}개):\n"
            for service in weak_passwords:
                report += f"  • {service}\n"
            report += "\n"
            
        if duplicate_passwords:
            unique_duplicates = list(set(duplicate_passwords))
            report += f"🔄 중복 비밀번호 ({len(unique_duplicates)}개):\n"
            for service in unique_duplicates:
                report += f"  • {service}\n"
            report += "\n"
            
        if old_passwords:
            report += f"📅 오래된 비밀번호 ({len(old_passwords)}개):\n"
            for service in old_passwords:
                report += f"  • {service}\n"
            report += "\n"
                
        if not weak_passwords and not duplicate_passwords and not old_passwords:
            report += "✅ 모든 비밀번호가 안전합니다!"
            
        messagebox.showinfo("보안 점검", report)
        
    def run(self):
        """프로그램 실행"""
        self.root.mainloop()

class EntryDialog:
    def __init__(self, parent, title, data=None):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x300")
        self.dialog.grab_set()
        
        # 데이터 초기화
        self.service_var = tk.StringVar(value=data.get('service', '') if data else '')
        self.username_var = tk.StringVar(value=data.get('username', '') if data else '')
        self.email_var = tk.StringVar(value=data.get('email', '') if data else '')
        self.password_var = tk.StringVar(value=data.get('password', '') if data else '')
        self.notes_var = tk.StringVar(value=data.get('notes', '') if data else '')
        
        self.setup_dialog()
        
    def setup_dialog(self):
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 서비스명
        ttk.Label(frame, text="서비스명:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=self.service_var, width=30).grid(row=0, column=1, pady=5)
        
        # 사용자명
        ttk.Label(frame, text="사용자명:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=self.username_var, width=30).grid(row=1, column=1, pady=5)
        
        # 이메일
        ttk.Label(frame, text="이메일:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=self.email_var, width=30).grid(row=2, column=1, pady=5)
        
        # 비밀번호
        ttk.Label(frame, text="비밀번호:").grid(row=3, column=0, sticky=tk.W, pady=5)
        password_frame = ttk.Frame(frame)
        password_frame.grid(row=3, column=1, pady=5, sticky=tk.W)
        
        self.password_entry = ttk.Entry(password_frame, textvariable=self.password_var, 
                                       show='*', width=25)
        self.password_entry.grid(row=0, column=0)
        
        ttk.Button(password_frame, text="생성", 
                  command=self.generate_password).grid(row=0, column=1, padx=(5, 0))
        
        # 메모
        ttk.Label(frame, text="메모:").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=self.notes_var, width=30).grid(row=4, column=1, pady=5)
        
        # 버튼
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="저장", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="취소", command=self.cancel).pack(side=tk.LEFT, padx=5)
        
    def generate_password(self):
        """비밀번호 생성"""
        length = 16
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(characters) for _ in range(length))
        self.password_var.set(password)
        
    def save(self):
        if not self.service_var.get():
            messagebox.showerror("오류", "서비스명을 입력하세요.")
            return
            
        self.result = {
            'service': self.service_var.get(),
            'username': self.username_var.get(),
            'email': self.email_var.get(),
            'password': self.password_var.get(),
            'notes': self.notes_var.get()
        }
        self.dialog.destroy()
        
    def cancel(self):
        self.dialog.destroy()

class PasswordGeneratorDialog:
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("비밀번호 생성기")
        self.dialog.geometry("450x350")
        self.dialog.grab_set()
        
        self.setup_dialog()
        
    def setup_dialog(self):
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 길이 설정
        ttk.Label(frame, text="길이:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.length_var = tk.IntVar(value=16)
        length_spin = ttk.Spinbox(frame, from_=4, to=64, textvariable=self.length_var, width=10)
        length_spin.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # 옵션들
        self.include_upper = tk.BooleanVar(value=True)
        self.include_lower = tk.BooleanVar(value=True)
        self.include_digits = tk.BooleanVar(value=True)
        self.include_symbols = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(frame, text="대문자 (A-Z)", variable=self.include_upper).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=2)
        ttk.Checkbutton(frame, text="소문자 (a-z)", variable=self.include_lower).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=2)
        ttk.Checkbutton(frame, text="숫자 (0-9)", variable=self.include_digits).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=2)
        ttk.Checkbutton(frame, text="특수문자 (!@#$%^&*)", variable=self.include_symbols).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # 생성 버튼
        ttk.Button(frame, text="비밀번호 생성", command=self.generate).grid(row=5, column=0, columnspan=2, pady=20)
        
        # 결과 표시
        ttk.Label(frame, text="생성된 비밀번호:").grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        self.result_var = tk.StringVar()
        result_frame = ttk.Frame(frame)
        result_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        result_entry = ttk.Entry(result_frame, textvariable=self.result_var, width=40, state='readonly')
        result_entry.grid(row=0, column=0, padx=(0, 5))
        
        ttk.Button(result_frame, text="복사", command=self.copy_password).grid(row=0, column=1)
        
        # 강도 표시
        self.strength_var = tk.StringVar()
        strength_label = ttk.Label(frame, textvariable=self.strength_var)
        strength_label.grid(row=8, column=0, columnspan=2, pady=5)
        
    def generate(self):
        """비밀번호 생성"""
        characters = ""
        
        if self.include_upper.get():
            characters += string.ascii_uppercase
        if self.include_lower.get():
            characters += string.ascii_lowercase
        if self.include_digits.get():
            characters += string.digits
        if self.include_symbols.get():
            characters += "!@#$%^&*()_+-=[]{}|;:,.<>?"
            
        if not characters:
            messagebox.showerror("오류", "최소 하나의 문자 유형을 선택하세요.")
            return
            
        length = self.length_var.get()
        password = ''.join(secrets.choice(characters) for _ in range(length))
        self.result_var.set(password)
        
        # 강도 평가
        strength = self.evaluate_strength(password)
        self.strength_var.set(f"강도: {strength}")
        
    def evaluate_strength(self, password):
        """비밀번호 강도 평가"""
        score = 0
        
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if re.search(r'[a-z]', password):
            score += 1
        if re.search(r'[A-Z]', password):
            score += 1
        if re.search(r'\d', password):
            score += 1
        if re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
            score += 1
            
        if score <= 2:
            return "약함 ⚠️"
        elif score <= 4:
            return "보통 🟡"
        else:
            return "강함 ✅"
            
    def copy_password(self):
        """비밀번호 복사"""
        password = self.result_var.get()
        if password:
            pyperclip.copy(password)
            messagebox.showinfo("알림", "비밀번호가 클립보드에 복사되었습니다.")

if __name__ == "__main__":
    # 필요한 라이브러리 설치 안내
    try:
        import pyperclip
        from cryptography.fernet import Fernet
    except ImportError:
        import subprocess
        import sys
        
        print("필요한 라이브러리를 설치하는 중...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyperclip", "cryptography"])
        print("설치 완료! 프로그램을 다시 실행해주세요.")
        sys.exit()
    
    app = PasswordManager()
    app.run()
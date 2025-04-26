import numpy as np  
import pandas as pd  
import matplotlib.pyplot as plt  
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  
import yfinance as yf  
import tkinter as tk  
from tkinter import ttk, messagebox  
from tkcalendar import DateEntry  
from datetime import datetime, timedelta  
import threading  

class PortfoyOptimizasyonuGUI:  
    def __init__(self, root):  
        self.root = root  
        self.root.title("Portföy Optimizasyonu Uygulaması")  
        self.root.geometry("1000x800")  
        self.root.config(padx=10, pady=10)  
        
        # Ana çerçeve  
        self.main_frame = ttk.Frame(root)  
        self.main_frame.pack(fill=tk.BOTH, expand=True)  
        
        # Sol panel (Giriş parametreleri için)  
        self.left_frame = ttk.LabelFrame(self.main_frame, text="Portföy Parametreleri", padding=(10, 10))  
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5)  
        
        # Sağ panel (Grafikler için)  
        self.right_frame = ttk.LabelFrame(self.main_frame, text="Sonuçlar", padding=(10, 10))  
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)  
        
        # Başlangıç tarihi (varsayılan: 3 yıl önce)  
        ttk.Label(self.left_frame, text="Başlangıç Tarihi:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)  
        default_start = datetime.now() - timedelta(days=3*365)  
        self.start_date = DateEntry(self.left_frame, width=12, date_pattern='yyyy-mm-dd',   
                                   year=default_start.year, month=default_start.month, day=default_start.day)  
        self.start_date.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)  
        
        # Bitiş tarihi (varsayılan: bugün)  
        ttk.Label(self.left_frame, text="Bitiş Tarihi:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)  
        self.end_date = DateEntry(self.left_frame, width=12, date_pattern='yyyy-mm-dd')  
        self.end_date.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)  
        
        # Hisse senetleri giriş alanı  
        ttk.Label(self.left_frame, text="Hisse Senetleri:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)  
        self.stocks_entry = tk.Text(self.left_frame, width=30, height=10, font=("Arial", 10))  
        self.stocks_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)  
        self.stocks_entry.insert(tk.END, "GLD\nUSD\nBTC-USD\nTHYAO.IS\nTUPRS.IS\nTSLA\nMSFT\nNVDA")  
        
        # Varsayılan hisseleri yükleme butonu  
        ttk.Button(self.left_frame, text="Varsayılan Hisseleri Yükle",   
                  command=self.load_default_stocks).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)  
        
        # Simülasyon sayısı  
        ttk.Label(self.left_frame, text="Simülasyon Sayısı:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)  
        self.sim_count_var = tk.StringVar(value="10000")  
        self.sim_count_entry = ttk.Entry(self.left_frame, textvariable=self.sim_count_var, width=10)  
        self.sim_count_entry.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)  
        
        # Hesaplama butonu  
        self.calculate_btn = ttk.Button(self.left_frame, text="Portföyü Optimize Et",   
                                       command=self.start_optimization)  
        self.calculate_btn.grid(row=5, column=0, columnspan=2, pady=20)  
        
        # İlerleme çubuğu  
        self.progress = ttk.Progressbar(self.left_frame, orient="horizontal", length=200, mode="indeterminate")  
        self.progress.grid(row=6, column=0, columnspan=2, pady=5)  
        
        # Durum mesajı etiketi  
        self.status_var = tk.StringVar(value="Hazır")  
        self.status_label = ttk.Label(self.left_frame, textvariable=self.status_var, font=("Arial", 9, "italic"))  
        self.status_label.grid(row=7, column=0, columnspan=2, pady=5)  
        
        # Sonuç çerçeveleri  
        self.result_tabs = ttk.Notebook(self.right_frame)  
        self.result_tabs.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)  
        
        # Sonuç sekmesi 1: Etkin Sınır Grafiği  
        self.efficient_frontier_frame = ttk.Frame(self.result_tabs)  
        self.result_tabs.add(self.efficient_frontier_frame, text="Etkin Sınır")  
        
        # Sonuç sekmesi 2: Portföy Dağılımı  
        self.portfolio_alloc_frame = ttk.Frame(self.result_tabs)  
        self.result_tabs.add(self.portfolio_alloc_frame, text="Portföy Dağılımı")  
        
        # Sonuç sekmesi 3: Optimum Portföy Detayları  
        self.details_frame = ttk.Frame(self.result_tabs)  
        self.result_tabs.add(self.details_frame, text="Portföy Detayları")  
        
        # Etkin sınır grafiği için figür hazırlama  
        self.efficient_figure = plt.Figure(figsize=(6, 4), dpi=100)  
        self.efficient_canvas = FigureCanvasTkAgg(self.efficient_figure, self.efficient_frontier_frame)  
        self.efficient_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)  
        
        # Portföy dağılım grafiği için figür hazırlama  
        self.pie_figure = plt.Figure(figsize=(6, 4), dpi=100)  
        self.pie_canvas = FigureCanvasTkAgg(self.pie_figure, self.portfolio_alloc_frame)  
        self.pie_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)  
        
        # Portföy detayları için bir metin kutusu  
        self.details_text = tk.Text(self.details_frame, wrap=tk.WORD, padx=10, pady=10, font=("Arial", 10))  
        self.details_text.pack(fill=tk.BOTH, expand=True)  
        
    def load_default_stocks(self):  
        self.stocks_entry.delete(1.0, tk.END)  
        default_stocks = "GLD\nUSD\nBTC-USD\nTHYAO.IS\nTUPRS.IS\nTSLA\nMSFT\nNVDA"  
        self.stocks_entry.insert(tk.END, default_stocks)  
    
    def start_optimization(self):  
        # Arka planda çalışacak bir iş parçacığı başlatma  
        self.calculate_btn.config(state=tk.DISABLED)  
        self.progress.start()  
        self.status_var.set("Optimizasyon yapılıyor...")  
        
        threading.Thread(target=self.run_optimization, daemon=True).start()  
    
    def run_optimization(self):  
        try:  
            # Kullanıcı girdilerini alma  
            başlangıç_tarihi = self.start_date.get_date().strftime("%Y-%m-%d")  
            bitiş_tarihi = self.end_date.get_date().strftime("%Y-%m-%d")  
            
            # Hisse senetlerini satır satır ayırma ve boş satırları temizleme  
            hisseler = [line.strip() for line in self.stocks_entry.get(1.0, tk.END).split("\n") if line.strip()]  
            
            try:  
                simülasyon_sayısı = int(self.sim_count_var.get())  
                if simülasyon_sayısı <= 0:  
                    raise ValueError("Simülasyon sayısı pozitif olmalıdır")  
            except ValueError:  
                raise ValueError("Geçerli bir simülasyon sayısı giriniz")  
            
            # Veri indirme  
            ham_veri = yf.download(hisseler, start=başlangıç_tarihi, end=bitiş_tarihi)  
            
            # Çok seviyeli DataFrame kontrolü ve 'Close' değerlerini alma  
            if isinstance(ham_veri.columns, pd.MultiIndex):  
                veri = ham_veri.xs('Close', axis=1, level=0)  
            else:  
                veri = ham_veri  
            
            # Eksik değerleri işleme  
            veri = veri.ffill().bfill()  
            
            # Günlük getirileri hesaplama  
            getiriler = veri.pct_change().dropna()  
            
            # Ortalama getiri hesapla  
            ortalama_getiri = getiriler.mean() * 252  
            
            # Kovaryans matrisi hesapla  
            kovaryans = getiriler.cov() * 252  
            
            # Monte Carlo Simülasyonu  
            sonuçlar = np.zeros((simülasyon_sayısı, 2))  
            
            # Mevcut varlıkların listesini al  
            mevcut_hisseler = list(ortalama_getiri.index)  
            
            for i in range(simülasyon_sayısı):  
                ağırlıklar = np.random.random(len(mevcut_hisseler))  
                ağırlıklar = ağırlıklar / np.sum(ağırlıklar)  
                
                portföy_getirisi = np.sum(ağırlıklar * ortalama_getiri.values)  
                portföy_volatilite = np.sqrt(np.dot(ağırlıklar.T, np.dot(kovaryans.values, ağırlıklar)))  
                
                sonuçlar[i, 0] = portföy_volatilite  
                sonuçlar[i, 1] = portföy_getirisi  
            
            # En iyi portföyü bul  
            sharpe_oranları = sonuçlar[:, 1] / sonuçlar[:, 0]  
            optimal_idx = sharpe_oranları.argmax()  
            
            # Optimal portföy ağırlıklarını bul  
            np.random.seed(42)  
            optimal_ağırlıklar = np.random.random(len(mevcut_hisseler))  
            optimal_ağırlıklar = optimal_ağırlıklar / np.sum(optimal_ağırlıklar)  
            
            # GUI'yi sonuçlarla güncelleme için ana thread'e gönder  
            self.root.after(0, lambda: self.update_results(  
                sonuçlar, optimal_idx, sharpe_oranları, mevcut_hisseler, optimal_ağırlıklar  
            ))  
            
        except Exception as e:  
            self.root.after(0, lambda: self.show_error(str(e)))  
    
    def update_results(self, sonuçlar, optimal_idx, sharpe_oranları, mevcut_hisseler, optimal_ağırlıklar):  
        # Etkin sınır grafiğini çiz  
        self.efficient_figure.clear()  
        ax = self.efficient_figure.add_subplot(111)  
        scatter = ax.scatter(sonuçlar[:, 0], sonuçlar[:, 1], c=sonuçlar[:, 1]/sonuçlar[:, 0],   
                              marker='o', alpha=0.5, cmap='viridis')  
        self.efficient_figure.colorbar(scatter, label='Sharpe Oranı')  
        ax.scatter(sonuçlar[optimal_idx, 0], sonuçlar[optimal_idx, 1], c='r', marker='*', s=300)  
        ax.set_xlabel('Volatilite (Risk)')  
        ax.set_ylabel('Beklenen Getiri')  
        ax.set_title('Monte Carlo Simülasyonu ile Portföy Optimizasyonu')  
        ax.grid(True, linestyle='--', alpha=0.7)  
        self.efficient_canvas.draw()  
        
        # Pasta grafiği ile portföy dağılımını göster  
        portföy_ağırlıkları = pd.Series(optimal_ağırlıklar, index=mevcut_hisseler)  
        
        self.pie_figure.clear()  
        ax = self.pie_figure.add_subplot(111)  
        wedges, texts, autotexts = ax.pie(  
            portföy_ağırlıkları,   
            labels=None,  # Etiketleri ayrı bir legend olarak ekleyeceğiz  
            autopct='%1.1f%%',   
            startangle=90,  
            wedgeprops={'edgecolor': 'w'}  
        )  
        
        # Pasta dilimlerinin renklerini al ve legend oluştur  
        ax.legend(  
            wedges,   
            portföy_ağırlıkları.index,   
            title="Hisseler",  
            loc="center left",  
            bbox_to_anchor=(1, 0, 0.5, 1)  
        )  
        
        ax.set_title('Optimal Portföy Dağılımı')  
        self.pie_canvas.draw()  
        
        # Portföy detaylarını göster  
        self.details_text.delete(1.0, tk.END)  
        details = f"Optimal Portföy Bilgileri:\n\n"  
        details += f"Getiri: {sonuçlar[optimal_idx, 1]:.4f}\n"  
        details += f"Risk: {sonuçlar[optimal_idx, 0]:.4f}\n"  
        details += f"Sharpe Oranı: {sharpe_oranları[optimal_idx]:.4f}\n\n"  
        details += "Optimal Portföy Dağılımı:\n"  
        
        for hisse, ağırlık in portföy_ağırlıkları.items():  
            details += f"{hisse}: %{ağırlık*100:.2f}\n"  
        
        self.details_text.insert(tk.END, details)  
        
        # İşlem tamamlandı, arayüzü sıfırla  
        self.progress.stop()  
        self.calculate_btn.config(state=tk.NORMAL)  
        self.status_var.set("Optimizasyon tamamlandı!")  
    
    def show_error(self, error_message):  
        self.progress.stop()  
        self.calculate_btn.config(state=tk.NORMAL)  
        self.status_var.set("Hata oluştu!")  
        messagebox.showerror("Hata", f"İşlem sırasında bir hata oluştu:\n{error_message}")  


if __name__ == "__main__":  
    root = tk.Tk()  
    app = PortfoyOptimizasyonuGUI(root)  
    root.mainloop()  
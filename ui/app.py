"""CustomTkinter desktop application."""
from datetime import datetime
from tkinter import filedialog, messagebox, ttk
import customtkinter as ctk
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from charts import allocation_figure, performance_figure
from database import Database
from portfolio import summary
from stock_data import STOCK_PRICES, COMPANY_NAMES
from utils import EXPORT_DIR, money, validate_stock

BG="#111820"; PANEL="#18232d"; PANEL2="#202d38"; TEXT="#e8eef2"; MUTED="#91a1ad"
GREEN="#43c59e"; RED="#ef6a6a"; BLUE="#68a7ff"

class StockTracker(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Northstar · Portfolio Tracker"); self.geometry("1320x850"); self.minsize(1020,700)
        ctk.set_appearance_mode("dark"); ctk.set_default_color_theme("blue")
        self.configure(fg_color=BG); self.db=Database(); self.page=None; self.filter="All holdings"; self.query=""
        self._style_tree()
        self.grid_columnconfigure(1,weight=1); self.grid_rowconfigure(0,weight=1)
        self._sidebar(); self.content=ctk.CTkFrame(self,fg_color=BG,corner_radius=0); self.content.grid(row=0,column=1,sticky="nsew")
        self.show_page("Dashboard")

    def _style_tree(self):
        style=ttk.Style(); style.theme_use("clam")
        style.configure("Treeview",background=PANEL,foreground=TEXT,fieldbackground=PANEL,rowheight=36,borderwidth=0,font=("Segoe UI",9))
        style.configure("Treeview.Heading",background=PANEL2,foreground="#aebbc4",relief="flat",font=("Segoe UI Semibold",9))
        style.map("Treeview",background=[("selected","#294563")],foreground=[("selected","white")])
        style.map("Treeview.Heading",background=[("active",PANEL2)])

    def _sidebar(self):
        side=ctk.CTkFrame(self,width=218,fg_color="#0c1218",corner_radius=0); side.grid(row=0,column=0,sticky="nsw"); side.grid_propagate(False)
        ctk.CTkLabel(side,text="NORTHSTAR",font=("Segoe UI",11,"bold"),text_color="#82b5e8").pack(anchor="w",padx=24,pady=(27,5))
        ctk.CTkLabel(side,text="Portfolio tracker",font=("Segoe UI",18,"bold"),text_color=TEXT).pack(anchor="w",padx=24,pady=(0,34))
        for title in ("Dashboard","My Portfolio","Transactions","Settings"):
            ctk.CTkButton(side,text=title,anchor="w",height=42,fg_color="transparent",hover_color=PANEL2,
                text_color=TEXT,font=("Segoe UI",12),command=lambda p=title:self.show_page(p)).pack(fill="x",padx=12,pady=3)
        ctk.CTkFrame(side,fg_color="#26343e",height=1).pack(fill="x",padx=20,pady=(25,15))
        ctk.CTkLabel(side,text="MARKET DATA",font=("Segoe UI",9,"bold"),text_color=MUTED).pack(anchor="w",padx=24)
        ctk.CTkLabel(side,text="Sample prices · not live",font=("Segoe UI",10),text_color="#d3a969").pack(anchor="w",padx=24,pady=8)
        self.side_status=ctk.CTkLabel(side,text="Saved locally",font=("Segoe UI",10),text_color=MUTED); self.side_status.pack(side="bottom",anchor="w",padx=24,pady=22)

    def _clear(self):
        for w in self.content.winfo_children(): w.destroy()

    def _heading(self,title,sub):
        ctk.CTkLabel(self.content,text=title,font=("Segoe UI",26,"bold"),text_color=TEXT).pack(anchor="w",padx=30,pady=(26,2))
        ctk.CTkLabel(self.content,text=sub,font=("Segoe UI",11),text_color=MUTED).pack(anchor="w",padx=32,pady=(0,18))

    def show_page(self,page):
        self.page=page; self._clear()
        {"Dashboard":self.dashboard,"My Portfolio":self.portfolio_page,"Transactions":self.transactions_page,"Settings":self.settings_page}[page]()

    def _card(self,parent,label,value,sub=None,color=TEXT):
        box=ctk.CTkFrame(parent,fg_color=PANEL,corner_radius=10); box.pack(side="left",fill="both",expand=True,padx=(0,10))
        ctk.CTkLabel(box,text=label.upper(),font=("Segoe UI",9,"bold"),text_color=MUTED).pack(anchor="w",padx=16,pady=(14,4))
        ctk.CTkLabel(box,text=value,font=("Segoe UI",21,"bold"),text_color=color).pack(anchor="w",padx=16)
        if sub: ctk.CTkLabel(box,text=sub,font=("Segoe UI",9),text_color=MUTED).pack(anchor="w",padx=16,pady=(3,13))
        else: ctk.CTkFrame(box,fg_color="transparent",height=13).pack()

    def _chart(self,parent,figure):
        canvas=FigureCanvasTkAgg(figure,master=parent); canvas.draw()
        canvas.get_tk_widget().configure(bg=PANEL,highlightthickness=0); canvas.get_tk_widget().pack(fill="both",expand=True)

    def dashboard(self):
        self._heading("Dashboard","A clear view of what you own and how it’s performing.")
        s=summary(self.db.holdings()); row=ctk.CTkFrame(self.content,fg_color="transparent"); row.pack(fill="x",padx=30,pady=(0,16))
        self._card(row,"Total investment",money(s['investment']),color=TEXT); self._card(row,"Portfolio value",money(s['value']),color=TEXT)
        self._card(row,"Total profit / loss",money(s['profit']),f"{s['profit_pct']:+.2f}% overall",GREEN if s['profit']>=0 else RED)
        self._card(row,"Stocks owned",f"{s['shares']:,}",f"Across {s['companies']} companies")
        chartrow=ctk.CTkFrame(self.content,fg_color="transparent"); chartrow.pack(fill="both",expand=True,padx=30,pady=(0,15))
        left=ctk.CTkFrame(chartrow,fg_color=PANEL,corner_radius=10); left.pack(side="left",fill="both",expand=True,padx=(0,10))
        right=ctk.CTkFrame(chartrow,fg_color=PANEL,corner_radius=10); right.pack(side="left",fill="both",expand=True,padx=(0,0))
        ctk.CTkLabel(left,text="Portfolio allocation",font=("Segoe UI",14,"bold"),text_color=TEXT).pack(anchor="w",padx=17,pady=(15,0))
        ctk.CTkLabel(right,text="Investment performance",font=("Segoe UI",14,"bold"),text_color=TEXT).pack(anchor="w",padx=17,pady=(15,0))
        self._chart(left,allocation_figure(s['stocks'])); self._chart(right,performance_figure(s['stocks']))
        bottom=ctk.CTkFrame(self.content,fg_color=PANEL,corner_radius=10); bottom.pack(fill="x",padx=30,pady=(0,24))
        ctk.CTkLabel(bottom,text="Performance standouts",font=("Segoe UI",13,"bold"),text_color=TEXT).pack(anchor="w",padx=17,pady=(12,5))
        if s['top']:
            line=f"Top performer   {s['top']['symbol']}  ·  {s['top']['profit_pct']:+.2f}%       |       Needs attention   {s['worst']['symbol']}  ·  {s['worst']['profit_pct']:+.2f}%"
        else: line="Your best and worst performers will appear once you add a holding."
        ctk.CTkLabel(bottom,text=line,font=("Segoe UI",10),text_color=MUTED).pack(anchor="w",padx=17,pady=(0,14))

    def _table(self,parent,columns,headings,widths,height=12):
        outer=ctk.CTkFrame(parent,fg_color=PANEL,corner_radius=8); outer.pack(fill="both",expand=True)
        tree=ttk.Treeview(outer,columns=columns,show="headings",height=height,selectmode="browse")
        vs=ttk.Scrollbar(outer,orient="vertical",command=tree.yview); hs=ttk.Scrollbar(outer,orient="horizontal",command=tree.xview)
        tree.configure(yscrollcommand=vs.set,xscrollcommand=hs.set)
        for col,label,width in zip(columns,headings,widths): tree.heading(col,text=label); tree.column(col,width=width,minwidth=70,anchor="w" if col in ("symbol","company","date","type") else "e",stretch=True)
        tree.pack(fill="both",expand=True,padx=(8,0),pady=(8,0)); vs.pack(side="right",fill="y",pady=(8,0)); hs.pack(fill="x",padx=8,pady=(0,8))
        tree.tag_configure("gain",foreground=GREEN); tree.tag_configure("loss",foreground=RED)
        return tree

    def _filtered(self):
        query=self.query.strip().lower(); rows=summary(self.db.holdings())['stocks']
        if query: rows=[r for r in rows if query in r['symbol'].lower() or query in r['company'].lower()]
        if self.filter=="Profitable": rows=[r for r in rows if r['profit']>0]
        if self.filter=="At a loss": rows=[r for r in rows if r['profit']<0]
        return rows

    def portfolio_page(self):
        self._heading("My Portfolio","Manage holdings, track performance, and keep your records in sync.")
        toolbar=ctk.CTkFrame(self.content,fg_color="transparent"); toolbar.pack(fill="x",padx=30,pady=(0,12))
        ctk.CTkButton(toolbar,text="Add stock",width=115,height=34,command=self.add_stock).pack(side="left",padx=(0,7))
        ctk.CTkButton(toolbar,text="Edit selected",width=112,height=34,fg_color=PANEL2,hover_color="#31424f",command=self.edit_selected).pack(side="left",padx=4)
        ctk.CTkButton(toolbar,text="Delete",width=80,height=34,fg_color="#58353a",hover_color="#754149",command=self.delete_selected).pack(side="left",padx=4)
        ctk.CTkButton(toolbar,text="Refresh",width=80,height=34,fg_color=PANEL2,hover_color="#31424f",command=self.refresh).pack(side="left",padx=4)
        self.search_var=ctk.StringVar(value=self.query)
        search=ctk.CTkEntry(toolbar,textvariable=self.search_var,placeholder_text="Search symbol or company…",width=220,height=34); search.pack(side="right",padx=(6,0)); search.bind("<KeyRelease>",lambda _e:self._populate())
        self.filter_var=ctk.StringVar(value=self.filter)
        select=ctk.CTkOptionMenu(toolbar,values=["All holdings","Profitable","At a loss"],variable=self.filter_var,width=125,height=34,command=lambda _v:self._populate()); select.pack(side="right")
        cols=("symbol","company","quantity","purchase","current","investment","value","profit","percent")
        self.holdings_tree=self._table(self.content,cols,("Symbol","Company","Shares","Avg. cost","Market price","Investment","Value","Profit / loss","Return"),(85,155,65,95,100,110,110,115,75),14)
        self.holdings_tree.bind("<Double-1>",lambda _e:self.edit_selected()); self._populate()
        s=summary(self.db.holdings()); foot=ctk.CTkFrame(self.content,fg_color="transparent"); foot.pack(fill="x",padx=30,pady=12)
        ctk.CTkLabel(foot,text=f"{s['companies']} companies  ·  {s['shares']:,} shares",text_color=MUTED,font=("Segoe UI",10)).pack(side="left")
        ctk.CTkLabel(foot,text=f"Invested  {money(s['investment'])}       Value  {money(s['value'])}       P/L  {money(s['profit'])}",text_color=GREEN if s['profit']>=0 else RED,font=("Segoe UI",11,"bold")).pack(side="right")

    def _populate(self):
        self.query=self.search_var.get() if hasattr(self,"search_var") else ""; self.filter=self.filter_var.get() if hasattr(self,"filter_var") else "All holdings"
        if not hasattr(self,"holdings_tree") or not self.holdings_tree.winfo_exists(): return
        self.holdings_tree.delete(*self.holdings_tree.get_children())
        for r in self._filtered():
            self.holdings_tree.insert("","end",iid=r['symbol'],values=(r['symbol'],r['company'],f"{r['quantity']:,}",money(r['purchase_price']),money(r['current_price']),money(r['investment']),money(r['value']),money(r['profit']),f"{r['profit_pct']:+.2f}%"),tags=("gain" if r['profit']>=0 else "loss",))

    def refresh(self):
        if self.page=="My Portfolio": self._populate()
        else: self.show_page(self.page)

    def _selected_symbol(self):
        if not hasattr(self,"holdings_tree"): return None
        selection=self.holdings_tree.selection()
        if not selection: messagebox.showinfo("Select a holding","Choose a stock from the table first."); return None
        return selection[0]

    def add_stock(self): self._stock_dialog()
    def edit_selected(self):
        symbol=self._selected_symbol()
        if symbol: self._stock_dialog(self.db.get(symbol))

    def delete_selected(self):
        symbol=self._selected_symbol()
        if symbol and messagebox.askyesno("Delete holding",f"Remove {symbol} from your portfolio? Its transaction history will remain."):
            try: self.db.delete(symbol); self._populate()
            except Exception as exc: messagebox.showerror("Could not delete holding",str(exc))

    def _stock_dialog(self,stock=None):
        edit=stock is not None; win=ctk.CTkToplevel(self); win.title("Edit stock" if edit else "Add stock"); win.geometry("430x535"); win.resizable(False,False); win.configure(fg_color=BG); win.transient(self); win.grab_set()
        ctk.CTkLabel(win,text="Edit holding" if edit else "Add a holding",font=("Segoe UI",22,"bold"),text_color=TEXT).pack(anchor="w",padx=26,pady=(22,3))
        ctk.CTkLabel(win,text="Enter your position details below.",font=("Segoe UI",10),text_color=MUTED).pack(anchor="w",padx=26,pady=(0,14))
        fields={}
        for key,label in [("symbol","Stock symbol"),("company","Company name"),("quantity","Shares owned"),("purchase_price","Purchase price per share"),("current_price","Current price per share")]:
            ctk.CTkLabel(win,text=label,font=("Segoe UI",10,"bold"),text_color="#b9c5cd").pack(anchor="w",padx=26,pady=(7,3))
            entry=ctk.CTkEntry(win,height=36,placeholder_text=label); entry.pack(fill="x",padx=26)
            if stock: entry.insert(0,str(stock[key]))
            fields[key]=entry
        note=ctk.CTkLabel(win,text="Supported symbols use sample prices; you can edit the price.",font=("Segoe UI",9),text_color="#d3a969",wraplength=370); note.pack(anchor="w",padx=26,pady=12)
        def price_hint(_event=None):
            symbol=fields['symbol'].get().strip().upper()
            if symbol in STOCK_PRICES:
                fields['current_price'].delete(0,"end"); fields['current_price'].insert(0,str(STOCK_PRICES[symbol]))
                if not fields['company'].get().strip(): fields['company'].insert(0,COMPANY_NAMES.get(symbol,""))
        fields['symbol'].bind("<FocusOut>",price_hint)
        def save():
            try:
                data=validate_stock(*(fields[k].get() for k in ("symbol","company","quantity","purchase_price","current_price")))
                if edit: self.db.edit(stock['symbol'],data)
                else: self.db.add(data)
                win.destroy(); self._populate()
            except Exception as exc: messagebox.showerror("Could not save holding",str(exc),parent=win)
        ctk.CTkButton(win,text="Save changes" if edit else "Add to portfolio",height=38,command=save).pack(fill="x",padx=26,pady=(0,18))

    def transactions_page(self):
        self._heading("Transactions","Your buy and sell activity, recorded as it happens.")
        form=ctk.CTkFrame(self.content,fg_color=PANEL,corner_radius=9); form.pack(fill="x",padx=30,pady=(0,14))
        ctk.CTkLabel(form,text="Record a trade",font=("Segoe UI",14,"bold"),text_color=TEXT).grid(row=0,column=0,columnspan=5,sticky="w",padx=15,pady=(12,6))
        names=[("symbol","Symbol"),("kind","Type"),("quantity","Shares"),("price","Price per share")]; self.trade_fields={}
        for i,(key,label) in enumerate(names):
            ctk.CTkLabel(form,text=label,font=("Segoe UI",9),text_color=MUTED).grid(row=1,column=i,sticky="w",padx=12)
            if key=="kind": field=ctk.CTkOptionMenu(form,values=["BUY","SELL"],width=95,height=34)
            else: field=ctk.CTkEntry(form,width=150,height=34,placeholder_text=label)
            field.grid(row=2,column=i,sticky="ew",padx=10,pady=(3,14)); self.trade_fields[key]=field
        ctk.CTkButton(form,text="Record trade",height=34,command=self._record_trade).grid(row=2,column=4,padx=14,pady=(3,14))
        form.grid_columnconfigure(4,weight=1)
        cols=("date","symbol","type","quantity","price","total")
        self.tx_tree=self._table(self.content,cols,("Date & time","Symbol","Type","Shares","Price / share","Trade total"),(205,100,100,90,135,145),15)
        self._populate_transactions()

    def _record_trade(self):
        try:
            f=self.trade_fields; symbol=f['symbol'].get().strip().upper(); kind=f['kind'].get(); quantity=int(f['quantity'].get()); price=float(f['price'].get())
            self.db.trade(symbol,kind,quantity,price)
            self._populate_transactions(); self.side_status.configure(text="Trade saved locally")
            for key in ("symbol","quantity","price"): f[key].delete(0,"end")
        except (ValueError,TypeError) as exc: messagebox.showerror("Could not record trade",str(exc))
        except Exception as exc: messagebox.showerror("Database error",str(exc))

    def _populate_transactions(self):
        self.tx_tree.delete(*self.tx_tree.get_children())
        for t in self.db.transactions():
            try: date=datetime.fromisoformat(t['created_at']).astimezone().strftime("%b %d, %Y · %I:%M %p")
            except ValueError: date=t['created_at']
            self.tx_tree.insert("","end",values=(date,t['symbol'],t['transaction_type'],f"{t['quantity']:,}",money(t['price']),money(t['quantity']*t['price'])),tags=("gain" if t['transaction_type']=="BUY" else "loss",))

    def settings_page(self):
        self._heading("Settings","Your data stays on this device. Manage files and sample content here.")
        box=ctk.CTkFrame(self.content,fg_color=PANEL,corner_radius=10); box.pack(fill="x",padx=30,pady=(0,14))
        ctk.CTkLabel(box,text="Portfolio files",font=("Segoe UI",16,"bold"),text_color=TEXT).pack(anchor="w",padx=20,pady=(17,4))
        ctk.CTkLabel(box,text="Import or export holdings as CSV, or save a readable summary as TXT.",font=("Segoe UI",10),text_color=MUTED).pack(anchor="w",padx=20,pady=(0,13))
        btns=ctk.CTkFrame(box,fg_color="transparent"); btns.pack(anchor="w",padx=15,pady=(0,17))
        for label,fn in [("Export CSV",self.export_csv),("Import CSV",self.import_csv),("Save summary TXT",self.export_summary)]: ctk.CTkButton(btns,text=label,width=130,height=34,fg_color=PANEL2,hover_color="#31424f",command=fn).pack(side="left",padx=5)
        box=ctk.CTkFrame(self.content,fg_color=PANEL,corner_radius=10); box.pack(fill="x",padx=30,pady=8)
        ctk.CTkLabel(box,text="Try the tracker",font=("Segoe UI",16,"bold"),text_color=TEXT).pack(anchor="w",padx=20,pady=(17,4))
        ctk.CTkLabel(box,text="Load a small sample portfolio to explore the dashboard and charts.",font=("Segoe UI",10),text_color=MUTED).pack(anchor="w",padx=20,pady=(0,13))
        ctk.CTkButton(box,text="Load sample portfolio",width=170,height=34,fg_color=PANEL2,hover_color="#31424f",command=self.load_sample).pack(anchor="w",padx=20,pady=(0,17))
        box=ctk.CTkFrame(self.content,fg_color=PANEL,corner_radius=10); box.pack(fill="x",padx=30,pady=8)
        ctk.CTkLabel(box,text="Reset portfolio",font=("Segoe UI",16,"bold"),text_color=TEXT).pack(anchor="w",padx=20,pady=(17,4))
        ctk.CTkLabel(box,text="Permanently remove holdings and transaction history from this device.",font=("Segoe UI",10),text_color=MUTED).pack(anchor="w",padx=20,pady=(0,13))
        ctk.CTkButton(box,text="Reset all data",width=130,height=34,fg_color="#58353a",hover_color="#754149",command=self.reset_data).pack(anchor="w",padx=20,pady=(0,17))
        box=ctk.CTkFrame(self.content,fg_color="transparent"); box.pack(fill="x",padx=30,pady=12)
        ctk.CTkLabel(box,text="Prices are sample values, not live market data. The database file is stored in data/portfolio.db.",font=("Segoe UI",10),text_color="#d3a969",wraplength=700).pack(anchor="w")

    def export_csv(self):
        path=filedialog.asksaveasfilename(title="Export portfolio",initialdir=EXPORT_DIR,initialfile="portfolio.csv",defaultextension=".csv",filetypes=[("CSV files","*.csv")])
        if not path:return
        try:
            columns=["symbol","company","quantity","purchase_price","current_price"]
            pd.DataFrame([{k:s[k] for k in columns} for s in self.db.holdings()],columns=columns).to_csv(path,index=False,encoding="utf-8-sig")
            messagebox.showinfo("Export complete",f"Portfolio saved to {path}")
        except (OSError,ValueError) as exc: messagebox.showerror("Export failed",str(exc))

    def import_csv(self):
        path=filedialog.askopenfilename(title="Import portfolio CSV",filetypes=[("CSV files","*.csv")])
        if not path:return
        try:
            frame=pd.read_csv(path,dtype=str,keep_default_na=False,encoding="utf-8-sig")
            frame.columns=[str(column).strip().lower() for column in frame.columns]
            required={"symbol","company","quantity","purchase_price","current_price"}
            if not required.issubset(set(frame.columns)): raise ValueError("CSV needs these headers: symbol, company, quantity, purchase_price, current_price.")
            # Normalize heading capitalization and validate every row before committing any.
            stocks=[validate_stock(*(row.get(k,"") for k in ("symbol","company","quantity","purchase_price","current_price"))) for row in frame.to_dict(orient="records")]
            if not stocks: raise ValueError("This CSV contains no stock records.")
            symbols=[stock['symbol'] for stock in stocks]
            if len(symbols)!=len(set(symbols)): raise ValueError("This CSV contains the same stock symbol more than once.")
            self.db.import_holdings(stocks); messagebox.showinfo("Import complete",f"Imported {len(stocks)} holding(s). Existing symbols were updated.")
        except (OSError,ValueError,pd.errors.ParserError,UnicodeError) as exc: messagebox.showerror("Import failed",str(exc))
        except Exception as exc: messagebox.showerror("Import failed",f"Could not update the database: {exc}")

    def export_summary(self):
        path=filedialog.asksaveasfilename(title="Save portfolio summary",initialdir=EXPORT_DIR,initialfile="portfolio-summary.txt",defaultextension=".txt",filetypes=[("Text files","*.txt")])
        if not path:return
        s=summary(self.db.holdings())
        lines=["NORTHSTAR PORTFOLIO SUMMARY",f"Generated {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z')}","",f"Total investment: {money(s['investment'])}",f"Current value: {money(s['value'])}",f"Profit / loss: {money(s['profit'])} ({s['profit_pct']:+.2f}%)",f"Shares owned: {s['shares']:,}",f"Companies: {s['companies']}","","HOLDINGS"]
        lines += [f"{x['symbol']} | {x['company']} | {x['quantity']} shares | cost {money(x['purchase_price'])} | current {money(x['current_price'])} | P/L {money(x['profit'])} ({x['profit_pct']:+.2f}%)" for x in s['stocks']]
        try:
            with open(path,"w",encoding="utf-8") as f:f.write("\n".join(lines)+"\n")
            messagebox.showinfo("Summary saved",f"Portfolio summary saved to {path}")
        except OSError as exc:messagebox.showerror("Save failed",str(exc))

    def load_sample(self):
        stocks=[{"symbol":"AAPL","company":"Apple Inc.","quantity":12,"purchase_price":168.50,"current_price":STOCK_PRICES['AAPL']},
                {"symbol":"MSFT","company":"Microsoft Corp.","quantity":7,"purchase_price":395.00,"current_price":STOCK_PRICES['MSFT']},
                {"symbol":"NVDA","company":"NVIDIA Corp.","quantity":20,"purchase_price":132.00,"current_price":STOCK_PRICES['NVDA']},
                {"symbol":"TSLA","company":"Tesla, Inc.","quantity":4,"purchase_price":275.00,"current_price":STOCK_PRICES['TSLA']}]
        try:
            self.db.seed(stocks); messagebox.showinfo("Sample data loaded","Four sample holdings were added to your portfolio.")
        except ValueError as exc:messagebox.showerror("Could not load sample data",str(exc))
        except Exception as exc:messagebox.showerror("Database error",str(exc))

    def reset_data(self):
        if messagebox.askyesno("Reset all data","Delete every holding and transaction? This cannot be undone."):
            try:self.db.reset(); messagebox.showinfo("Portfolio reset","Holdings and transactions were removed.")
            except Exception as exc:messagebox.showerror("Reset failed",str(exc))

def run(): StockTracker().mainloop()

"""Matplotlib chart builders used by the dashboard."""
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure

BG = "#111820"
PANEL = "#18232d"
TEXT = "#dce5ea"
MUTED = "#8a9aa6"
GREEN = "#43c59e"
RED = "#ef6a6a"
BLUE = "#68a7ff"

def allocation_figure(stocks):
    fig=Figure(figsize=(4.5,3.0),dpi=100,facecolor=PANEL)
    ax=fig.add_subplot(111); ax.set_facecolor(PANEL)
    if stocks:
        colors=[BLUE,"#43c59e","#e8b86d","#a78bfa","#ef6a6a","#55c2d8","#df8da7"]
        wedges,_=ax.pie([s['value'] for s in stocks], startangle=90, counterclock=False,
                        colors=colors, wedgeprops={"width":0.34,"edgecolor":PANEL,"linewidth":2})
        ax.legend(wedges,[s['symbol'] for s in stocks],loc="center left",bbox_to_anchor=(0.82,0.5),
                  frameon=False,labelcolor=TEXT,fontsize=8)
    else:
        ax.text(.5,.5,"Add a holding to see allocation",ha="center",va="center",color=MUTED,transform=ax.transAxes,fontsize=9)
    ax.set(aspect="equal"); fig.subplots_adjust(left=0,right=.98,top=.95,bottom=.03)
    return fig

def performance_figure(stocks):
    fig=Figure(figsize=(6,3.0),dpi=100,facecolor=PANEL)
    ax=fig.add_subplot(111); ax.set_facecolor(PANEL)
    if stocks:
        rows=stocks[-8:]; colors=[GREEN if s['profit']>=0 else RED for s in rows]
        ax.bar([s['symbol'] for s in rows],[s['profit'] for s in rows],color=colors,width=.56)
        ax.axhline(0,color="#52616d",linewidth=.8)
    else:
        ax.text(.5,.5,"Performance will appear once you add holdings",ha="center",va="center",color=MUTED,transform=ax.transAxes,fontsize=9)
    ax.tick_params(colors=MUTED,labelsize=8); ax.spines[:].set_visible(False)
    ax.grid(axis="y",color="#283640",linewidth=.6); ax.set_axisbelow(True)
    fig.subplots_adjust(left=.12,right=.97,top=.96,bottom=.18)
    return fig

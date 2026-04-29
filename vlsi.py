"""
VLSI Design Assistant — Production-Ready Streamlit App
=======================================================
Run:
    pip install streamlit google-genai matplotlib networkx
    streamlit run vlsi_assistant.py

Place "VLSI KNOWLEDGE BASE.txt" in the same directory.
Set your Gemini API key on line marked ← API KEY.
"""

import re
import io
import json
import time
import textwrap
from datetime import datetime

import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from google import genai
# EDA Playground automation
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="VLSI Design Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS — dark industrial + phosphor-green accent
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    background: #eef2fb;
    color: #1a2540;
}
.stApp { background: #eef2fb; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 2px solid #d8e2f4 !important;
    box-shadow: 3px 0 18px rgba(37,99,235,0.07);
}
[data-testid="stSidebar"] * { color: #1e3060 !important; }
[data-testid="stSidebar"] p { color: #3a5080 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stTextInput label,
[data-testid="stSidebar"] .stTextArea label,
[data-testid="stSidebar"] .stFileUploader label {
    color: #5570a0 !important;
    font-size: 0.72rem !important;
    letter-spacing: .09em;
    text-transform: uppercase;
    font-weight: 700 !important;
}
[data-testid="stSidebar"] .stToggle label { color: #1e3060 !important; font-size: 0.88rem !important; font-weight: 600 !important; }
[data-testid="stSidebar"] input {
    background: #f2f6ff !important;
    border: 1.5px solid #b8caea !important;
    border-radius: 8px !important;
    color: #1a2540 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.83rem !important;
}
[data-testid="stSidebar"] input:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.12) !important;
}

/* ── Header banner ── */
.vlsi-header {
    background: linear-gradient(115deg, #1e3a8a 0%, #2563eb 55%, #0ea5e9 100%);
    border-radius: 16px;
    padding: 1.8rem 2.4rem;
    margin-bottom: 1.8rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 10px 40px rgba(37,99,235,0.28);
}
.vlsi-header::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 200px; height: 200px;
    border-radius: 50%;
    background: rgba(255,255,255,0.06);
}
.vlsi-header::after {
    content: '⚡';
    position: absolute;
    right: 2.2rem; top: 50%;
    transform: translateY(-50%);
    font-size: 5rem;
    opacity: 0.12;
    pointer-events: none;
}
.vlsi-header h1 {
    margin: 0;
    font-size: 1.9rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: #ffffff;
}
.vlsi-header h1 span { color: #bae6fd; }
.vlsi-header p { margin: 0.4rem 0 0; color: rgba(255,255,255,0.80); font-size: 0.9rem; font-weight: 500; }

/* ── Stat pills ── */
.stat-row { display: flex; gap: 0.8rem; margin-bottom: 1.6rem; flex-wrap: wrap; }
.stat-pill {
    background: #ffffff;
    border: 1.5px solid #d0dcf4;
    border-radius: 12px;
    padding: 0.65rem 1.2rem;
    font-size: 0.78rem;
    color: #3a5080;
    display: flex; align-items: center; gap: 0.5rem;
    font-weight: 600;
    box-shadow: 0 2px 10px rgba(37,99,235,0.07);
}
.stat-pill b { color: #2563eb; font-size: 1.05rem; font-weight: 800; }

/* ── Section labels ── */
.section-label {
    font-size: 0.68rem;
    letter-spacing: .14em;
    text-transform: uppercase;
    color: #6a88b8;
    font-weight: 700;
    margin-bottom: 0.65rem;
    padding-bottom: 0.4rem;
    border-bottom: 2px solid #d8e2f4;
}

/* ── Chat bubbles ── */
.msg-user {
    background: #dbeafe;
    border: 1.5px solid #93c5fd;
    border-radius: 16px 16px 4px 16px;
    padding: 1rem 1.3rem;
    margin: 0.8rem 0;
    color: #1e3a8a;
    font-size: 0.95rem;
    font-weight: 500;
    box-shadow: 0 2px 10px rgba(37,99,235,0.10);
}
.msg-assistant {
    background: #ffffff;
    border: 1.5px solid #d8e8f8;
    border-left: 5px solid #2563eb;
    border-radius: 4px 16px 16px 16px;
    padding: 1rem 1.3rem;
    margin: 0.8rem 0;
    color: #1a2540;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.95rem;
    box-shadow: 0 3px 14px rgba(37,99,235,0.08);
}
.msg-meta {
    font-size: 0.68rem;
    color: #7a9acc;
    margin-bottom: 0.45rem;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    letter-spacing: 0.04em;
}

/* ── Code blocks ── */
.stCodeBlock, pre, code {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
    background: #f0f6ff !important;
    border: 1.5px solid #c0d4f0 !important;
    border-radius: 8px !important;
    color: #1a2a50 !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    color: #ffffff !important;
    border: none;
    border-radius: 9px;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: .02em;
    padding: 0.52rem 1.4rem;
    transition: all 0.18s ease;
    box-shadow: 0 3px 12px rgba(37,99,235,0.28);
}
.stButton > button:hover {
    background: linear-gradient(135deg, #1d4ed8, #1e40af);
    box-shadow: 0 6px 20px rgba(37,99,235,0.40);
    transform: translateY(-2px);
}
.stButton > button:active { transform: translateY(0); }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #ffffff;
    border-radius: 12px 12px 0 0;
    border-bottom: 2.5px solid #d0dcf4;
    gap: 0;
    padding: 0 0.6rem;
    box-shadow: 0 2px 10px rgba(37,99,235,0.06);
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #7a90b8 !important;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: .07em;
    text-transform: uppercase;
    border-bottom: 3px solid transparent;
    padding: 0.75rem 1.5rem;
    transition: all 0.18s;
}
.stTabs [data-baseweb="tab"]:hover { color: #2563eb !important; }
.stTabs [aria-selected="true"] {
    color: #2563eb !important;
    border-bottom: 3px solid #2563eb !important;
    background: transparent !important;
}

/* ── Text inputs / textareas ── */
.stTextArea textarea, .stTextInput input {
    background: #ffffff !important;
    border: 1.5px solid #c0d0ea !important;
    border-radius: 9px !important;
    color: #1a2540 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
    box-shadow: 0 1px 5px rgba(30,60,120,0.05) !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.14) !important;
}
.stTextArea label, .stTextInput label, .stSelectbox label {
    color: #4a6888 !important;
    font-size: 0.73rem !important;
    text-transform: uppercase;
    letter-spacing: .09em;
    font-weight: 700 !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: #ffffff !important;
    border: 1.5px solid #c0d0ea !important;
    border-radius: 9px !important;
    color: #1a2540 !important;
    font-weight: 500 !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: #f2f6ff !important;
    border: 1.5px solid #d0dcf4 !important;
    border-radius: 9px !important;
    color: #1e3a70 !important;
    font-size: 0.85rem !important;
    font-weight: 700 !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: #f8faff;
    border: 2px dashed #a8c0e8;
    border-radius: 12px;
    padding: 0.5rem;
}
[data-testid="stFileUploader"] * { color: #3a5888 !important; font-weight: 500 !important; }

/* ── Log box ── */
.log-box {
    background: #f2f6ff;
    border: 1.5px solid #d0dcf4;
    border-left: 4px solid #2563eb;
    border-radius: 9px;
    padding: 0.8rem 1rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.74rem;
    color: #1e4aaa;
    max-height: 180px;
    overflow-y: auto;
    font-weight: 500;
    line-height: 1.7;
}

/* ── Download badge ── */
.dl-badge {
    display: inline-block;
    background: #eff6ff;
    border: 1.5px solid #2563eb;
    color: #2563eb;
    border-radius: 6px;
    padding: 0.2rem 0.7rem;
    font-size: 0.72rem;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 0.4rem;
    font-weight: 700;
}

/* ── Hint text ── */
.hint-text { font-size: 0.77rem; color: #4a78cc; font-weight: 500; }

/* ── Info / warning / error boxes ── */
[data-testid="stAlert"] { border-radius: 10px !important; }

/* ── Radio buttons ── */
.stRadio label { color: #1e3060 !important; font-weight: 600 !important; font-size: 0.88rem !important; }
.stRadio div[role="radiogroup"] label { color: #2a4070 !important; }

/* ── Dividers ── */
hr { border-color: #d0dcf4 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #eef2fb; }
::-webkit-scrollbar-thumb { background: #b0c4e8; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #2563eb; }

/* ── Toggle ── */
.stToggle [data-checked="true"] { background-color: #2563eb !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS — diagram generators (pure matplotlib, no external tools)
# ═══════════════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════
# EDA PLAYGROUND INTEGRATION
# ═══════════════════════════════════════════════════════════════════════

def split_design_tb(code: str):
    """Split design and testbench"""
    code_lower = code.lower()

    if "module tb" in code_lower:
        parts = code.split("module tb", 1)
        design = parts[0]
        tb = "module tb" + parts[1]
        return design.strip(), tb.strip()

    if "testbench" in code_lower:
        return "", code

    return code, ""


def create_edaplayground_link(design_code, tb_code=""):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

        driver.get("https://edaplayground.com")

        import time
        time.sleep(6)

        # Design code
        try:
            design_box = driver.find_element(By.ID, "code")
            design_box.clear()
            design_box.send_keys(design_code)
        except:
            pass

        # Testbench
        if tb_code:
            try:
                tb_box = driver.find_element(By.ID, "testbench")
                tb_box.clear()
                tb_box.send_keys(tb_code)
            except:
                pass

        # Click Share
        try:
            share_btn = driver.find_element(By.ID, "share")
            share_btn.click()
        except:
            driver.quit()
            return "Error: Share button not found"

        time.sleep(4)

        # Get link
        try:
            link = driver.find_element(By.CLASS_NAME, "share-link").get_attribute("value")
        except:
            driver.quit()
            return "Error: Could not extract link"

        driver.quit()
        return link

    except Exception as e:
        return f"Error: {str(e)}"


def _dark_fig(w=8, h=4):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor("#f8faff")
    ax.set_facecolor("#f8faff")
    for spine in ax.spines.values():
        spine.set_edgecolor("#c0d0ea")
    ax.tick_params(colors="#3a5080")
    return fig, ax


def generate_waveform(signals: dict, title: str = "Waveform") -> plt.Figure:
    """signals = {'CLK': [...], 'A': [...], ...}  values 0/1"""
    fig, axes = plt.subplots(len(signals), 1, figsize=(10, max(3, len(signals) * 1.2)),
                              sharex=True)
    fig.patch.set_facecolor("#f8faff")
    if len(signals) == 1:
        axes = [axes]

    for ax, (name, vals) in zip(axes, signals.items()):
        ax.set_facecolor("#f8faff")
        ax.step(range(len(vals)), vals, where="post", color="#2563eb", linewidth=2)
        ax.fill_between(range(len(vals)), vals, step="post", alpha=0.12, color="#2563eb")
        ax.set_ylim(-0.3, 1.3)
        ax.set_yticks([0, 1])
        ax.set_yticklabels(["0", "1"], color="#3a5080", fontsize=8,
                            fontfamily="monospace")
        ax.set_ylabel(name, color="#1e3a8a", fontsize=9, rotation=0,
                      labelpad=32, va="center", fontfamily="monospace", fontweight="bold")
        for spine in ax.spines.values():
            spine.set_edgecolor("#c0d0ea")
        ax.tick_params(colors="#3a5080")
        ax.grid(axis="x", color="#d8e4f4", linewidth=0.6)

    axes[-1].set_xlabel("Time (ns)", color="#3a5080", fontsize=8)
    fig.suptitle(title, color="#1a2a50", fontsize=11, fontfamily="monospace",
                 y=1.01, fontweight="bold")
    plt.tight_layout()
    return fig


def generate_fsm_diagram(states: list, transitions: list, title="FSM Diagram") -> plt.Figure:
    """
    states: ['IDLE','RUN','DONE']
    transitions: [('IDLE','RUN','start'),('RUN','DONE','done')]
    """
    G = nx.DiGraph()
    G.add_nodes_from(states)
    edge_labels = {}
    for src, dst, label in transitions:
        G.add_edge(src, dst)
        edge_labels[(src, dst)] = label

    fig, ax = plt.subplots(figsize=(max(7, len(states) * 2), 4))
    fig.patch.set_facecolor("#f8faff")
    ax.set_facecolor("#f8faff")
    ax.axis("off")

    pos = nx.shell_layout(G) if len(states) > 3 else nx.circular_layout(G)

    nx.draw_networkx_nodes(G, pos, ax=ax, node_color="#dbeafe",
                           edgecolors="#2563eb", linewidths=2.5, node_size=2400)
    nx.draw_networkx_labels(G, pos, ax=ax, font_color="#1e3a8a", font_size=9,
                            font_family="monospace", font_weight="bold")
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#2563eb", arrows=True,
                           arrowstyle="-|>", arrowsize=20, width=2,
                           connectionstyle="arc3,rad=0.15")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax,
                                 font_color="#d97706", font_size=8,
                                 font_family="monospace", font_weight="bold")
    ax.set_title(title, color="#1a2a50", fontsize=11, fontfamily="monospace",
                 fontweight="bold")
    plt.tight_layout()
    return fig


def generate_gate_schematic(gate_type: str) -> plt.Figure:
    """Render a simple gate symbol."""
    fig, ax = plt.subplots(figsize=(5, 3))
    fig.patch.set_facecolor("#f8faff")
    ax.set_facecolor("#f8faff")
    ax.set_xlim(0, 5)
    ax.set_ylim(0, 3)
    ax.axis("off")
    ax.set_title(f"{gate_type.upper()} Gate", color="#1a2a50",
                 fontsize=11, fontfamily="monospace", fontweight="bold")

    gate_color = "#2563eb"
    line_kw = dict(color=gate_color, linewidth=2.2, solid_capstyle="round")

    g = gate_type.upper()
    if g in ("AND", "NAND"):
        body = mpatches.FancyBboxPatch((1.8, 1.0), 1.0, 1.0,
                                       boxstyle="round,pad=0.2",
                                       linewidth=2, edgecolor=gate_color,
                                       facecolor="#dbeafe")
        ax.add_patch(body)
        arc = mpatches.Arc((2.8, 1.5), 1.0, 1.0, angle=0,
                            theta1=-90, theta2=90, color=gate_color, linewidth=2)
        ax.add_patch(arc)
        ax.plot([1.0, 1.8], [1.75, 1.75], **line_kw)
        ax.plot([1.0, 1.8], [1.25, 1.25], **line_kw)
        ax.plot([3.3, 4.0], [1.5, 1.5], **line_kw)
        if g == "NAND":
            circ = plt.Circle((3.35, 1.5), 0.12, color=gate_color, fill=False, linewidth=2)
            ax.add_patch(circ)

    elif g in ("OR", "NOR", "XOR"):
        arc1 = mpatches.Arc((1.8, 1.5), 1.2, 1.2, angle=0,
                             theta1=-90, theta2=90, color=gate_color, linewidth=2)
        ax.add_patch(arc1)
        ax.plot([1.0, 1.8], [1.75, 1.75], **line_kw)
        ax.plot([1.0, 1.8], [1.25, 1.25], **line_kw)
        ax.plot([2.4, 4.0], [1.5, 1.5], **line_kw)
        if g == "NOR":
            circ = plt.Circle((2.5, 1.5), 0.12, color=gate_color, fill=False, linewidth=2)
            ax.add_patch(circ)
        if g == "XOR":
            arc2 = mpatches.Arc((1.6, 1.5), 1.0, 1.0, angle=0,
                                 theta1=-90, theta2=90, color="#0ea5e9", linewidth=1.8)
            ax.add_patch(arc2)

    elif g in ("NOT", "BUF"):
        tri = plt.Polygon([[1.5, 1.0], [1.5, 2.0], [3.0, 1.5]],
                          closed=True, edgecolor=gate_color,
                          facecolor="#dbeafe", linewidth=2)
        ax.add_patch(tri)
        ax.plot([1.0, 1.5], [1.5, 1.5], **line_kw)
        ax.plot([3.0, 4.0], [1.5, 1.5], **line_kw)
        if g == "NOT":
            circ = plt.Circle((3.1, 1.5), 0.12, color=gate_color, fill=False, linewidth=2)
            ax.add_patch(circ)

    ax.text(0.7, 1.75, "A", color="#d97706", fontsize=11, ha="center",
            fontfamily="monospace", fontweight="bold")
    if g not in ("NOT", "BUF"):
        ax.text(0.7, 1.25, "B", color="#d97706", fontsize=11, ha="center",
                fontfamily="monospace", fontweight="bold")
    ax.text(4.3, 1.5, "Y", color="#059669", fontsize=11, ha="center",
            fontfamily="monospace", fontweight="bold")
    plt.tight_layout()
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# DIAGRAM AUTO-DETECTION from AI response
# ═══════════════════════════════════════════════════════════════════════════════

GATE_KEYWORDS = {"and", "nand", "or", "nor", "xor", "xnor", "not", "buf",
                 "buffer", "inv", "inverter"}


def detect_gate(text: str):
    words = re.findall(r'\b\w+\b', text.lower())
    for w in words:
        if w in GATE_KEYWORDS:
            return w.replace("inverter", "not").replace("buffer", "buf").replace("inv", "not")
    return None


def detect_fsm(text: str):
    """Very light heuristic: find lines like IDLE -> RUN : condition"""
    transitions, states = [], set()
    for match in re.finditer(
        r'(\w+)\s*[-=]+>\s*(\w+)\s*[:/]?\s*([^\n;]*)', text
    ):
        src, dst, lbl = match.group(1), match.group(2), match.group(3).strip()
        src, dst = src.upper(), dst.upper()
        transitions.append((src, dst, lbl[:12]))
        states |= {src, dst}
    return list(states), transitions


def detect_waveform_context(text: str):
    """Return a demo waveform if timing diagram language is used."""
    kw = ["waveform", "timing", "clk", "clock", "posedge", "negedge",
          "rising", "falling"]
    if any(k in text.lower() for k in kw):
        clk = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
        a   = [0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0]
        b   = [0, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0]
        out = [a[i] & b[i] for i in range(len(a))]
        return {"CLK": clk, "A": a, "B": b, "OUT": out}
    return None


def extract_code_blocks(text: str):
    """Return list of (lang, code) tuples from markdown fences."""
    return re.findall(r'```(\w*)\n(.*?)```', text, re.DOTALL)


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INIT
# ═══════════════════════════════════════════════════════════════════════════════

def _init_state():
    defaults = {
        "messages": [],           # {role, content, ts}
        "history_stack": [],      # for undo
        "log": [],
        "session_stats": {"queries": 0, "code_blocks": 0, "diagrams": 0},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init_state()


def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    st.session_state.log.append(f"[{ts}] {msg}")
    if len(st.session_state.log) > 60:
        st.session_state.log.pop(0)


# ═══════════════════════════════════════════════════════════════════════════════
# KB LOADER
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(show_spinner=False)
def load_kb(path: str = "VLSI KNOWLEDGE BASE.txt") -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


# ═══════════════════════════════════════════════════════════════════════════════
# GEMINI CHAT SESSION
# ═══════════════════════════════════════════════════════════════════════════════

def build_system_prompt(kb: str) -> str:
    return f"""
You are a highly skilled VLSI Design Assistant and Verification Expert.

Your job:
- Generate code in Verilog, SystemVerilog, UVM, or scripting (Perl, Python for VLSI).
- Always use ONLY the knowledge from the provided KB.
- Generate high-level, one-time error-free code.
- Include clear, precise explanations.
- Suggest improvements or optimizations if applicable.
- Provide schematics, waveforms, FSM diagrams if relevant.
- Include inline comments in code.
- Keep your answer concise, accurate, and professional.
- For FSMs, always describe transitions in the format: STATE_A -> STATE_B : condition

Knowledge Base:
{{kb}}

Answer based ONLY on the knowledge base above.
"""


def send_message_to_gemini(api_key: str, kb: str, user_text: str) -> str:
    """
    Creates a fresh client + chat for every message, replaying full
    conversation history so multi-turn context is preserved.
    This avoids the 'client has been closed' error from @st.cache_resource.
    """
    client = genai.Client(api_key="AIzaSyBgs__vC_0R5LXE8WlhnRA76H7qIDRSRGU")

    # Replay prior turns as history (skip figure entries)
    history = []
    for m in st.session_state.messages:
        if m["role"] == "user":
            history.append({"role": "user", "parts": [{"text": m["content"]}]})
        elif m["role"] == "assistant":
            history.append({"role": "model", "parts": [{"text": m["content"]}]})

    chat = client.chats.create(
        model="gemini-2.5-flash",
        config={"system_instruction": build_system_prompt(kb)},
        history=history,
    )
    return chat.send_message(user_text).text


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown('<div class="section-label">⚙ Configuration</div>', unsafe_allow_html=True)

    api_key = st.text_input("Gemini API Key", type="password",
                            placeholder="AIza...")

    kb_file = st.file_uploader("Upload KB (optional override)",
                               type=["txt"], help="Defaults to VLSI KNOWLEDGE BASE.txt")

    st.markdown('<div class="section-label" style="margin-top:1rem">🎛 Generation</div>',
                unsafe_allow_html=True)

    lang_mode = st.selectbox("Language / Mode",
                             ["Auto-detect", "Verilog", "SystemVerilog",
                              "UVM", "Python (VLSI)", "Perl"])

    diagram_on = st.toggle("Auto-generate diagrams", value=True)
    waveform_on = st.toggle("Auto-generate waveforms", value=True)
    opt_hints = st.toggle("Optimization hints", value=True)

    st.markdown('<div class="section-label" style="margin-top:1rem">🗒 Session Log</div>',
                unsafe_allow_html=True)
    log_html = "<br>".join(st.session_state.log[-12:]) or "No activity yet."
    st.markdown(f'<div class="log-box">{log_html}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label" style="margin-top:1rem">🔧 Actions</div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⟳ Reset", use_container_width=True):
            for k in ["messages", "log", "history_stack"]:
                st.session_state[k] = []
            st.session_state["session_stats"] = {"queries": 0, "code_blocks": 0, "diagrams": 0}
            st.rerun()
    with col2:
        if st.button("↩ Undo", use_container_width=True):
            if st.session_state.history_stack:
                st.session_state.messages = st.session_state.history_stack.pop()
                log("Undo performed")
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="vlsi-header">
    <h1>⚡ VLSI <span>Design Assistant</span></h1>
    <p>Verilog · SystemVerilog · UVM · Formal Verification · Waveforms · FSMs</p>
</div>
""", unsafe_allow_html=True)

# Stats row
s = st.session_state.session_stats
st.markdown(f"""
<div class="stat-row">
    <div class="stat-pill">Queries <b>{s['queries']}</b></div>
    <div class="stat-pill">Code Blocks Generated <b>{s['code_blocks']}</b></div>
    <div class="stat-pill">Diagrams Rendered <b>{s['diagrams']}</b></div>
    <div class="stat-pill">Undo Depth <b>{len(st.session_state.history_stack)}</b></div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ────────────────────────────────────────────────────────────────────
tab_chat, tab_tools, tab_history = st.tabs(
    ["💬  CHAT", "🔧  TOOLS & UPLOAD", "📜  HISTORY"]
)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — CHAT
# ═══════════════════════════════════════════════════════════════════════════════
with tab_chat:

    # Load KB (file upload overrides disk)
    if kb_file:
        kb = kb_file.read().decode("utf-8")
        log("KB loaded from upload")
    else:
        kb = load_kb()
        if kb:
            log("KB loaded from disk")
        else:
            st.warning("⚠ VLSI KNOWLEDGE BASE.txt not found. Upload a KB in the sidebar.")

    # Render chat history
    for msg in st.session_state.messages:
        role = msg["role"]
        ts   = msg.get("ts", "")

        # Skip figure entries — rendered separately below
        if role == "_fig":
            continue

        if role == "user":
            st.markdown(
                f'<div class="msg-user"><div class="msg-meta">👤 You · {ts}</div>{msg["content"]}</div>',
                unsafe_allow_html=True,
            )
        elif role == "assistant":
            # Parse markdown code blocks for syntax highlighting
            content = msg["content"]
            blocks  = extract_code_blocks(content)
            plain   = re.sub(r'```\w*\n.*?```', '', content, flags=re.DOTALL).strip()
            st.markdown(
                f'<div class="msg-assistant"><div class="msg-meta">⚡ VLSI Assistant · {ts}</div></div>',
                unsafe_allow_html=True,
            )
            if plain:
                st.markdown(plain)
            for lang, code in blocks:
                code_clean = code.strip()
                st.code(code_clean, language=lang or "verilog")

                # Download button
                dl_name = f"vlsi_{lang or 'code'}_{ts.replace(':', '')}.v"
                st.download_button(
                    label=f"⬇ Download {lang or 'code'}",
                    data=code_clean,
                    file_name=dl_name,
                    mime="text/plain",
                    key=f"dl_{id(code)}_{ts}",
                )

                # 🚀 EDA Playground Button
                if st.button("🚀 Open in EDA Playground", key=f"eda_{id(code)}_{ts}"):
                    with st.spinner("Creating simulation link..."):
                        design_code, tb_code = split_design_tb(code_clean)
                        link = create_edaplayground_link(design_code, tb_code)
                        if link.startswith("http"):
                            st.success("✅ Simulation Ready!")
                            st.markdown(f"👉 [Click here to open simulation]({link})")
                        else:
                            st.error(link)

    # ── Input row ────────────────────────────────────────────────────────────
    st.markdown("---")

    lang_hint = "" if lang_mode == "Auto-detect" else f"[Generate in {lang_mode}] "
    query = st.text_area(
        "Ask the VLSI Assistant",
        placeholder="e.g. Write a 4-bit ripple carry adder in Verilog with testbench",
        height=90,
        key="query_input",
    )

    send_col, hint_col = st.columns([1, 5])
    with send_col:
        send = st.button("▶ Send", use_container_width=True)
    with hint_col:
        if opt_hints and st.session_state.messages:
            st.markdown(
                '<span class="hint-text">💡 Tip: Ask for optimizations, '
                'timing analysis, or testbench coverage to get the most from this assistant.</span>',
                unsafe_allow_html=True,
            )

    if send and query.strip():
        if not api_key:
            st.error("Enter your Gemini API key in the sidebar.")
        elif not kb:
            st.error("Knowledge base not loaded.")
        else:
            full_query = lang_hint + query.strip()

            # Push undo snapshot
            import copy
            st.session_state.history_stack.append(
                copy.deepcopy(st.session_state.messages)
            )
            if len(st.session_state.history_stack) > 20:
                st.session_state.history_stack.pop(0)

            ts_now = datetime.now().strftime("%H:%M:%S")
            st.session_state.messages.append(
                {"role": "user", "content": query.strip(), "ts": ts_now}
            )
            log(f"Query: {query[:60]}…")
            st.session_state.session_stats["queries"] += 1

            with st.spinner("Generating response…"):
                try:
                    answer = send_message_to_gemini(api_key, kb, full_query)
                except Exception as e:
                    answer = f"⚠ API Error: {e}"
                    log(f"ERROR: {e}")

            ts_now2 = datetime.now().strftime("%H:%M:%S")
            st.session_state.messages.append(
                {"role": "assistant", "content": answer, "ts": ts_now2}
            )

            # Count code blocks
            blocks = extract_code_blocks(answer)
            st.session_state.session_stats["code_blocks"] += len(blocks)
            log(f"Response received — {len(blocks)} code block(s)")

            # ── Auto diagrams ────────────────────────────────────────────────
            if diagram_on:
                gate = detect_gate(query + " " + answer)
                if gate:
                    fig = generate_gate_schematic(gate)
                    st.session_state.messages.append(
                        {"role": "_fig", "fig": fig, "label": f"{gate.upper()} Schematic", "ts": ts_now2}
                    )
                    st.session_state.session_stats["diagrams"] += 1
                    log(f"Auto-generated {gate.upper()} schematic")

                states, transitions = detect_fsm(answer)
                if len(states) >= 2 and transitions:
                    fig = generate_fsm_diagram(states, transitions, "FSM Diagram")
                    st.session_state.messages.append(
                        {"role": "_fig", "fig": fig, "label": "FSM Diagram", "ts": ts_now2}
                    )
                    st.session_state.session_stats["diagrams"] += 1
                    log("Auto-generated FSM diagram")

            if waveform_on:
                sigs = detect_waveform_context(query + " " + answer)
                if sigs:
                    fig = generate_waveform(sigs, "Timing Waveform")
                    st.session_state.messages.append(
                        {"role": "_fig", "fig": fig, "label": "Waveform", "ts": ts_now2}
                    )
                    st.session_state.session_stats["diagrams"] += 1
                    log("Auto-generated waveform")

            st.rerun()

    # Render any queued figures
    for msg in st.session_state.messages:
        if msg.get("role") == "_fig":
            st.markdown(
                f'<div class="section-label" style="margin-top:1rem">📐 {msg["label"]}</div>',
                unsafe_allow_html=True,
            )
            st.pyplot(msg["fig"], use_container_width=True)
            buf = io.BytesIO()
            msg["fig"].savefig(buf, format="png", bbox_inches="tight", dpi=150,
                               facecolor="#f8faff")
            buf.seek(0)
            st.download_button(
                f"⬇ Download {msg['label']} PNG",
                data=buf,
                file_name=f"{msg['label'].replace(' ', '_')}.png",
                mime="image/png",
                key=f"figdl_{id(msg)}",
            )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — TOOLS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_tools:
    st.markdown('<div class="section-label">🔨 Manual Diagram Tools</div>',
                unsafe_allow_html=True)

    t1, t2, t3 = st.columns(3)

    with t1:
        st.markdown("**Gate Schematic**")
        gate_sel = st.selectbox("Gate type", ["AND", "NAND", "OR", "NOR", "XOR", "NOT", "BUF"],
                                key="gate_sel")
        if st.button("Generate Gate", key="btn_gate"):
            fig = generate_gate_schematic(gate_sel)
            st.pyplot(fig, use_container_width=True)

    with t2:
        st.markdown("**Waveform Builder**")
        wave_input = st.text_area(
            "JSON  {signal:[0,1,…], …}",
            value='{"CLK":[0,1,0,1,0,1,0,1],"D":[0,0,1,1,0,0,1,1],"Q":[0,0,0,1,1,0,0,1]}',
            height=100, key="wave_input"
        )
        wave_title = st.text_input("Title", "Custom Waveform", key="wave_title")
        if st.button("Render Waveform", key="btn_wave"):
            try:
                sigs = json.loads(wave_input)
                fig = generate_waveform(sigs, wave_title)
                st.pyplot(fig, use_container_width=True)
            except Exception as e:
                st.error(f"JSON error: {e}")

    with t3:
        st.markdown("**FSM Builder**")
        fsm_states = st.text_input("States (comma-sep)", "IDLE,RUN,DONE", key="fsm_states")
        fsm_trans = st.text_area(
            "Transitions (src->dst:label, one per line)",
            "IDLE->RUN:start\nRUN->DONE:finish\nDONE->IDLE:reset",
            height=80, key="fsm_trans"
        )
        if st.button("Render FSM", key="btn_fsm"):
            states = [s.strip().upper() for s in fsm_states.split(",")]
            trans  = []
            for line in fsm_trans.strip().splitlines():
                m = re.match(r'(\w+)\s*-+>\s*(\w+)\s*[:/]?\s*(.*)', line.strip())
                if m:
                    trans.append((m.group(1).upper(), m.group(2).upper(), m.group(3)[:12]))
            if trans:
                fig = generate_fsm_diagram(states, trans, "Custom FSM")
                st.pyplot(fig, use_container_width=True)
            else:
                st.error("No valid transitions found.")

    st.markdown('<div class="section-label" style="margin-top:2rem">📂 Upload Verilog for Review</div>',
                unsafe_allow_html=True)

    vfile = st.file_uploader("Upload .v / .sv / .uvm file", type=["v", "sv", "uvm", "txt"],
                             key="vfile")
    if vfile and api_key:
        code_text = vfile.read().decode("utf-8")
        with st.expander("📄 File contents", expanded=False):
            st.code(code_text, language="verilog")

        action = st.radio("Action", ["Review for bugs", "Optimize", "Generate testbench",
                                     "Explain line-by-line"], horizontal=True, key="vaction")
        if st.button("▶ Analyse", key="btn_analyse"):
            prompt_txt = f"{action} the following code:\n\n```verilog\n{code_text}\n```"
            with st.spinner("Analysing…"):
                try:
                    result = send_message_to_gemini(api_key, kb, prompt_txt)
                except Exception as e:
                    result = f"Error: {e}"
            st.markdown(result)
            log(f"File analysis: {action}")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — HISTORY
# ═══════════════════════════════════════════════════════════════════════════════
with tab_history:
    st.markdown('<div class="section-label">📜 Conversation Export</div>',
                unsafe_allow_html=True)

    chat_msgs = [m for m in st.session_state.messages if m["role"] in ("user", "assistant")]
    if not chat_msgs:
        st.info("No conversation yet.")
    else:
        # Plain text export
        lines = []
        for m in chat_msgs:
            prefix = "YOU" if m["role"] == "user" else "ASSISTANT"
            lines.append(f"[{m.get('ts', '')}] {prefix}:\n{m['content']}\n")
        export_txt = "\n".join(lines)

        st.download_button(
            "⬇ Download conversation (.txt)",
            data=export_txt,
            file_name=f"vlsi_chat_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
        )

        st.markdown('<div class="section-label" style="margin-top:1rem">Messages</div>',
                    unsafe_allow_html=True)
        for m in reversed(chat_msgs):
            role = "👤 You" if m["role"] == "user" else "⚡ Assistant"
            preview = m["content"][:120].replace("\n", " ")
            with st.expander(f"{role}  ·  {m.get('ts', '')}  —  {preview}…"):
                st.write(m["content"])

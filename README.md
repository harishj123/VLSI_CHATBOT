# ⚡ VLSI Design Assistant

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini_2.5_Flash-AI-4285F4?style=flat&logo=google&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat)

An AI-powered VLSI Design & Verification Assistant built with **Google Gemini 2.5 Flash** and **Streamlit**. It generates production-ready Verilog, SystemVerilog, and UVM code, auto-renders FSM diagrams, timing waveforms, and gate schematics — all from natural language prompts.

---

## ✨ Features

- 💬 **AI Chat Interface** — Ask anything about VLSI design and verification
- 🧠 **Knowledge Base (KB) Driven** — Answers grounded in your custom VLSI KB
- ⚙️ **Code Generation** — Verilog, SystemVerilog, UVM, Python, Perl
- 📐 **Auto FSM Diagrams** — Detects FSM descriptions and renders state diagrams
- 📊 **Auto Waveforms** — Detects timing context and renders signal waveforms
- 🔌 **Gate Schematic Tool** — AND, NAND, OR, NOR, XOR, NOT, BUF
- 🚀 **EDA Playground Integration** — One-click simulation link generation
- 📂 **File Upload & Review** — Upload .v/.sv files for bug review, optimization, or testbench generation
- ⬇️ **Code Download** — Download generated code directly from chat
- ↩️ **Undo Support** — Step back through conversation history
- 📜 **Conversation Export** — Download full chat as .txt

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| AI Model | Google Gemini 2.5 Flash |
| Diagram Engine | Matplotlib, NetworkX |
| Browser Automation | Selenium, WebDriver Manager |
| Language | Python 3.10+ |

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/vlsi-design-assistant.git
cd vlsi-design-assistant
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # Linux / Mac
venv\Scripts\activate           # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

```bash
cp .env.example .env
```

Open `.env` and add your Gemini API key:

```
GEMINI_API_KEY=your_actual_api_key_here
```

Get your free Gemini API key at: https://aistudio.google.com/app/apikey

### 5. Add Your Knowledge Base

Place your `VLSI KNOWLEDGE BASE.txt` file in the root directory.
You can also upload it directly from the sidebar at runtime.

### 6. Run the App

```bash
streamlit run vlsi_assistant.py
```

Open your browser at `http://localhost:8501`

---

## 📁 Project Structure

```
vlsi-design-assistant/
│
├── vlsi_assistant.py          # Main Streamlit application
├── VLSI KNOWLEDGE BASE.txt    # Domain knowledge base (add your own)
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variable template
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
└── screenshots/               # App screenshots for README
    ├── chat_demo.png
    └── waveform_demo.png
```

---

## 💡 Example Prompts

```
Write a 4-bit ripple carry adder in Verilog with testbench
Generate a UVM environment for an APB protocol verification
Design a Mealy FSM for a sequence detector (1011)
Write a SystemVerilog constrained-random testbench for FIFO memory
Explain the difference between blocking and non-blocking assignments
Generate a UVM scoreboard for an AXI4 interface
```

---

## Result

https://drive.google.com/file/d/1Eay59DArx25pF3v3Ous8syO58Hm6huwe/view?usp=sharing

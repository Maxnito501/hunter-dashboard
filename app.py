import streamlit as st
import pytesseract
import cv2
import numpy as np
from PIL import Image
import re
from datetime import datetime
import os
import subprocess

# ตั้งค่า Tesseract path
if os.name == 'nt':  # Windows
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
else:  # Linux (Streamlit Cloud)
    possible_paths = [
        '/usr/bin/tesseract',
        '/usr/local/bin/tesseract',
        '/app/.apt/usr/bin/tesseract'
    ]
    for path in possible_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break

# ตรวจสอบ Tesseract
HAS_TESSERACT = False
try:
    result = subprocess.run(['tesseract', '--version'], capture_output=True, text=True)
    HAS_TESSERACT = (result.returncode == 0)
except:
    HAS_TESSERACT = False

st.set_page_config(
    page_title="นายพรานจับจังหวะ",
    page_icon="🐂",
    layout="wide"
)

# CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;700&display=swap');
    
    * {
        font-family: 'Kanit', sans-serif;
    }
    
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .guru-card {
        background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .whale-card { border-left-color: #28a745; }
    .reversal-card { border-left-color: #ffc107; }
    .panic-card { border-left-color: #dc3545; }
    .tired-card { border-left-color: #6c757d; }
    
    .guru-quote {
        font-size: 1.2rem;
        font-style: italic;
        color: #444;
        margin: 0.5rem 0;
        padding-left: 1rem;
        border-left: 3px solid #667eea;
    }
    
    .stat-box {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        text-align: center;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    
    .bid-box {
        background: #dcfce7;
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
    }
    
    .offer-box {
        background: #fee2e2;
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
    }
    
    .stButton button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border: none;
        padding: 0.5rem;
        border-radius: 10px;
    }
    
    .stButton button:hover {
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# Session state
if 'ocr_done' not in st.session_state:
    st.session_state.ocr_done = False
if 'bid_values' not in st.session_state:
    st.session_state.bid_values = [0, 0, 0, 0, 0]
if 'offer_values' not in st.session_state:
    st.session_state.offer_values = [0, 0, 0, 0, 0]
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False
if 'uploaded_image' not in st.session_state:
    st.session_state.uploaded_image = None
if 'debug_info' not in st.session_state:
    st.session_state.debug_info = ""

# Header
st.markdown('<p class="main-header">🐂 นายพรานจับจังหวะ</p>', unsafe_allow_html=True)
st.markdown("---")

# แสดงสถานะ Tesseract
with st.sidebar:
    st.markdown("### 🔧 ระบบ")
    if HAS_TESSERACT:
        st.success("✅ Tesseract พร้อมใช้งาน")
    else:
        st.warning("⚠️ Tesseract ไม่พร้อมใช้งาน (กรุณาป้อนตัวเลขเอง)")
    
    if st.button("🧹 ล้างค่าทั้งหมด"):
        st.session_state.ocr_done = False
        st.session_state.bid_values = [0, 0, 0, 0, 0]
        st.session_state.offer_values = [0, 0, 0, 0, 0]
        st.session_state.analyzed = False
        st.session_state.uploaded_image = None
        st.rerun()

# Layout 2 คอลัมน์
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📸 1. อัปโหลดภาพ")
    uploaded_file = st.file_uploader("เลือกภาพ (PNG/JPG)", type=['png', 'jpg', 'jpeg'], key="uploader")
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.session_state.uploaded_image = image
        st.image(image, caption="ภาพที่อัปโหลด", use_column_width=True)
        
        if HAS_TESSERACT and st.button("🔍 อ่านค่าด้วย OCR", key="ocr_btn"):
            with st.spinner("กำลังอ่านภาพ..."):
                try:
                    # แปลงภาพ
                    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
                    
                    # OCR
                    custom_config = r'--oem 3 --psm 6'
                    text = pytesseract.image_to_string(thresh, config=custom_config)
                    
                    # ดึงตัวเลข
                    numbers = re.findall(r'\d+', text)
                    st.session_state.debug_info = f"OCR found: {numbers}"
                    
                    if len(numbers) >= 10:
                        st.session_state.bid_values = [int(x) for x in numbers[:5]]
                        st.session_state.offer_values = [int(x) for x in numbers[5:10]]
                        st.session_state.ocr_done = True
                        st.success(f"✅ อ่านพบ {len(numbers)} ตัวเลข")
                        st.rerun()
                    else:
                        st.warning(f"⚠️ พบ {len(numbers)} ตัวเลข (ต้องการอย่างน้อย 10)")
                        with st.expander("ดูข้อความที่อ่านได้"):
                            st.text(text)
                except Exception as e:
                    st.error(f"❌ เกิดข้อผิดพลาด: {e}")
    else:
        st.info("👆 กรุณาเลือกภาพก่อน")

with col2:
    st.markdown("### ✏️ 2. ตรวจสอบและแก้ไข")
    
    # Bid
    st.markdown("#### 🟢 Bid (ฝั่งซื้อ)")
    bid_cols = st.columns(5)
    for i in range(5):
        with bid_cols[i]:
            st.markdown(f"<div style='text-align:center; font-weight:bold;'>B{i+1}</div>", unsafe_allow_html=True)
            st.session_state.bid_values[i] = st.number_input(
                f"bid_{i}",
                min_value=0,
                value=st.session_state.bid_values[i],
                step=1000,
                key=f"bid_input_{i}",
                label_visibility="collapsed"
            )
    
    # Offer
    st.markdown("#### 🔴 Offer (ฝั่งขาย)")
    offer_cols = st.columns(5)
    for i in range(5):
        with offer_cols[i]:
            st.markdown(f"<div style='text-align:center; font-weight:bold;'>O{i+1}</div>", unsafe_allow_html=True)
            st.session_state.offer_values[i] = st.number_input(
                f"offer_{i}",
                min_value=0,
                value=st.session_state.offer_values[i],
                step=1000,
                key=f"offer_input_{i}",
                label_visibility="collapsed"
            )
    
    # ปุ่มวิเคราะห์
    st.markdown("---")
    if st.button("📊 วิเคราะห์", key="analyze_btn"):
        st.session_state.analyzed = True
        st.rerun()

# ผลวิเคราะห์
if st.session_state.analyzed:
    st.markdown("---")
    st.markdown("## 🎯 ผลวิเคราะห์")
    
    # คำนวณค่า
    bid_3 = sum(st.session_state.bid_values[:3])
    offer_3 = sum(st.session_state.offer_values[:3])
    ratio = bid_3 / offer_3 if offer_3 > 0 else 0
    
    # สถิติ
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{bid_3:,}</div>
            <div style="color:#666;">Bid 3 ช่อง</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{offer_3:,}</div>
            <div style="color:#666;">Offer 3 ช่อง</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{ratio:.2f}</div>
            <div style="color:#666;">อัตราส่วน</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # แสดงกลยุทธ์
    if ratio >= 2:
        st.markdown(f"""
        <div class="guru-card whale-card">
            <h2 style="margin:0;">🐋 WHALE RIDER</h2>
            <p style="font-size:1.2rem;">วอลุ่มซื้อหนา {ratio:.2f} เท่า</p>
            <p style="font-size:1.1rem;">เจ้ากำลังช้อนของ!</p>
            <div class="guru-quote">⚔️ ซุนวู: "รู้เขา รู้เรา รบร้อยครั้ง ชนะร้อยครั้ง"</div>
            <div class="guru-quote">🛡️ เลโอนิดัส: "THIS IS SPARTA! จัดการได้!"</div>
            <p style="color:#28a745; font-weight:bold; font-size:1.3rem;">✅ ซื้อตาม</p>
        </div>
        """, unsafe_allow_html=True)
    
    elif ratio >= 1.5:
        st.markdown(f"""
        <div class="guru-card reversal-card">
            <h2 style="margin:0;">🎯 REVERSAL</h2>
            <p style="font-size:1.2rem;">วอลุ่มซื้อเริ่มเข้า {ratio:.2f} เท่า</p>
            <div class="guru-quote">🐂 บัฟเฟต์: "ซื้อตอนคนกลัว ขายตอนคนโลภ"</div>
            <div class="guru-quote">⚔️ ซุนวู: "จงรอให้ศึกชัดเจน แล้วค่อยลงมือ"</div>
            <p style="color:#ffc107; font-weight:bold; font-size:1.3rem;">⏳ รอดู</p>
        </div>
        """, unsafe_allow_html=True)
    
    elif ratio <= 0.5:
        inv_ratio = offer_3 / bid_3 if bid_3 > 0 else 0
        st.markdown(f"""
        <div class="guru-card panic-card">
            <h2 style="margin:0;">💀 PANIC</h2>
            <p style="font-size:1.2rem;">วอลุ่มขายหนา {inv_ratio:.2f} เท่า</p>
            <p style="font-size:1.1rem;">เจ้ากำลังเทขาย!</p>
            <div class="guru-quote">⚔️ ซุนวู: "三十六计 หนีคือกลยุทธ์สูงสุด"</div>
            <div class="guru-quote">🛡️ เลโอนิดัส: "วันนี้ถอย พรุ่งนี้ค่อยสู้ใหม่"</div>
            <p style="color:#dc3545; font-weight:bold; font-size:1.3rem;">⚠️ ขาย/ชอร์ต</p>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        st.markdown(f"""
        <div class="guru-card tired-card">
            <h2 style="margin:0;">🎣 TIRED MARKET</h2>
            <p style="font-size:1.2rem;">วอลุ่มสมดุล {ratio:.2f} เท่า</p>
            <div class="guru-quote">💻 บิล เกตส์: "Data เงียบ จงอย่าด่วนตัดสินใจ"</div>
            <div class="guru-quote">🚀 อีลอน: "ตลาดเหนื่อย เราก็พัก รอจังหวะดีกว่า"</div>
            <p style="color:#6c757d; font-weight:bold; font-size:1.3rem;">👀 เฝ้าดู</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("⚔️ ซุนวู - ยุทธการ")
with col2:
    st.caption("🐂 บัฟเฟต์ - มูลค่า")
with col3:
    st.caption("💻 บิล - ระบบ")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🚀 อีลอน - นวัตกรรม")
with col2:
    st.caption("🛡️ เลโอนิดัส - นักรบ")
with col3:
    st.caption(f"อัปเดต {datetime.now().strftime('%d/%m/%Y %H:%M')}")

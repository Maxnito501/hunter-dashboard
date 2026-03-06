import streamlit as st
import pytesseract #
import cv2
import numpy as np
from PIL import Image
import re
import pandas as pd
from datetime import datetime

# ตั้งค่า Tesseract (Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

st.set_page_config(
    page_title="นายพรานจับจังหวะ",
    page_icon="🐂",
    layout="wide"
)

# CSS เพิ่มความสวยงาม
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
    
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
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
    .trend-card { border-left-color: #007bff; }
    .cutloss-card { border-left-color: #fd7e14; }
    
    .guru-name {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .guru-quote {
        font-size: 1.2rem;
        font-style: italic;
        color: #444;
        margin: 0.5rem 0;
        padding-left: 1rem;
        border-left: 3px solid #667eea;
    }
    
    .strategy-box {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
    }
    
    .strategy-emoji {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    
    .strategy-name {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 1rem;
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
    
    .stat-label {
        color: #888;
        font-size: 0.9rem;
    }
    
    .bid-box {
        background: #dcfce7;
        padding: 0.8rem;
        border-radius: 10px;
        text-align: center;
    }
    
    .offer-box {
        background: #fee2e2;
        padding: 0.8rem;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'ocr_done' not in st.session_state:
    st.session_state.ocr_done = False
if 'bid_values' not in st.session_state:
    st.session_state.bid_values = [0, 0, 0, 0, 0]
if 'offer_values' not in st.session_state:
    st.session_state.offer_values = [0, 0, 0, 0, 0]
if 'current_strategy' not in st.session_state:
    st.session_state.current_strategy = None
if 'ratio' not in st.session_state:
    st.session_state.ratio = 0

# Header
st.markdown('<p class="main-header">🐂 นายพรานจับจังหวะ</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">วิเคราะห์ Bid/Offer ด้วยกุนซือทั้ง 5</p>', unsafe_allow_html=True)

# Layout 2 คอลัมน์หลัก
left_col, right_col = st.columns([1, 1.2])

with left_col:
    st.markdown("### 📸 1. อัปโหลดภาพ")
    
    # ตัวเลือกการรับภาพ
    tab1, tab2 = st.tabs(["📤 อัปโหลดไฟล์", "📋 วางข้อความ"])
    
    with tab1:
        uploaded_file = st.file_uploader("ลากหรือเลือกภาพ (PNG/JPG)", type=['png', 'jpg', 'jpeg'])
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="ภาพที่อัปโหลด", use_column_width=True)
            
            if st.button("🔍 อ่านค่าด้วย OCR", type="primary", use_container_width=True):
                with st.spinner("กำลังอ่านภาพ..."):
                    # แปลงภาพ
                    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                    
                    # ปรับแต่งภาพ
                    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
                    
                    # OCR
                    custom_config = r'--oem 3 --psm 6'
                    text = pytesseract.image_to_string(thresh, config=custom_config)
                    
                    # ดึงเฉพาะตัวเลข
                    numbers = re.findall(r'\d+', text)
                    
                    if len(numbers) >= 10:
                        st.session_state.bid_values = [int(x) for x in numbers[:5]]
                        st.session_state.offer_values = [int(x) for x in numbers[5:10]]
                        st.session_state.ocr_done = True
                        st.success(f"✅ อ่านพบ {len(numbers)} ตัวเลข")
                        st.rerun()
                    else:
                        st.warning(f"⚠️ พบตัวเลข {len(numbers)} ตัว (ต้องการอย่างน้อย 10)")
                        st.text(f"ข้อความที่อ่านได้:\n{text}")
    
    with tab2:
        st.markdown("##### วางข้อความจาก OCR อื่นๆ")
        text_input = st.text_area("วางข้อความที่มีตัวเลข", height=150)
        
        if st.button("🔍 ดึงตัวเลข", use_container_width=True):
            numbers = re.findall(r'\d+', text_input)
            if len(numbers) >= 10:
                st.session_state.bid_values = [int(x) for x in numbers[:5]]
                st.session_state.offer_values = [int(x) for x in numbers[5:10]]
                st.session_state.ocr_done = True
                st.success(f"✅ พบ {len(numbers)} ตัวเลข")
                st.rerun()
            else:
                st.warning(f"⚠️ พบ {len(numbers)} ตัวเลข (ต้องการ 10)")

with right_col:
    st.markdown("### 🐋 2. ตรวจสอบและแก้ไข")
    
    if st.session_state.ocr_done:
        st.success("✅ OCR สำเร็จ! กรุณาตรวจสอบความถูกต้อง")
        
        # Bid
        st.markdown("#### 🟢 Bid (ฝั่งซื้อ)")
        bid_cols = st.columns(5)
        for i in range(5):
            with bid_cols[i]:
                st.markdown(f"<div class='bid-box'>B{i+1}</div>", unsafe_allow_html=True)
                st.session_state.bid_values[i] = st.number_input(
                    f"vol_{i+1}",
                    min_value=0,
                    value=st.session_state.bid_values[i],
                    step=100,
                    key=f"bid_{i}",
                    label_visibility="collapsed"
                )
        
        # Offer
        st.markdown("#### 🔴 Offer (ฝั่งขาย)")
        offer_cols = st.columns(5)
        for i in range(5):
            with offer_cols[i]:
                st.markdown(f"<div class='offer-box'>O{i+1}</div>", unsafe_allow_html=True)
                st.session_state.offer_values[i] = st.number_input(
                    f"vol_o{i+1}",
                    min_value=0,
                    value=st.session_state.offer_values[i],
                    step=100,
                    key=f"offer_{i}",
                    label_visibility="collapsed"
                )
        
        # ปุ่มวิเคราะห์
        if st.button("📊 วิเคราะห์", type="primary", use_container_width=True):
            # คำนวณ 3 ช่องแรก
            bid_3 = sum(st.session_state.bid_values[:3])
            offer_3 = sum(st.session_state.offer_values[:3])
            st.session_state.ratio = bid_3 / offer_3 if offer_3 > 0 else 0
            
            # กำหนดกลยุทธ์
            if st.session_state.ratio >= 2:
                st.session_state.current_strategy = "whale"
            elif st.session_state.ratio >= 1.5:
                st.session_state.current_strategy = "reversal"
            elif st.session_state.ratio <= 0.5:
                st.session_state.current_strategy = "panic"
            else:
                st.session_state.current_strategy = "tired"
            
            st.rerun()
    
    else:
        st.info("👆 กรุณาอัปโหลดภาพและกด 'อ่านค่าด้วย OCR' ก่อน")

# ส่วนแสดงผลวิเคราะห์
if st.session_state.current_strategy:
    st.markdown("---")
    st.markdown("## 🎯 ผลวิเคราะห์")
    
    # คำนวณค่า
    bid_3 = sum(st.session_state.bid_values[:3])
    offer_3 = sum(st.session_state.offer_values[:3])
    
    # สร้างสถิติ
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{bid_3:,}</div>
            <div class="stat-label">Bid 3 ช่อง</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{offer_3:,}</div>
            <div class="stat-label">Offer 3 ช่อง</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{st.session_state.ratio:.2f}</div>
            <div class="stat-label">อัตราส่วน</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        action = ""
        if st.session_state.current_strategy == "whale":
            action = "ซื้อ"
        elif st.session_state.current_strategy == "panic":
            action = "ขาย"
        elif st.session_state.current_strategy == "reversal":
            action = "รอ"
        else:
            action = "เฝ้าดู"
        
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{action}</div>
            <div class="stat-label">คำแนะนำ</div>
        </div>
        """, unsafe_allow_html=True)
    
    # แสดงกลยุทธ์และกุนซือ
    st.markdown("---")
    
    if st.session_state.current_strategy == "whale":
        st.markdown(f"""
        <div class="guru-card whale-card">
            <div style="display: flex; align-items: center; gap: 20px;">
                <div style="font-size: 4rem;">🐋</div>
                <div>
                    <div class="strategy-name">WHALE RIDER</div>
                    <div>วอลุ่มซื้อหนา {st.session_state.ratio:.2f} เท่า เจ้ากำลังช้อนของ</div>
                </div>
            </div>
            <div style="margin-top: 20px;">
                <div class="guru-quote">⚔️ ซุนวู: "รู้เขา รู้เรา รบร้อยครั้ง ชนะร้อยครั้ง"</div>
                <div class="guru-quote">🛡️ เลโอนิดัส: "THIS IS SPARTA! จัดการได้!"</div>
            </div>
            <div style="margin-top: 15px; padding: 10px; background: #28a74520; border-radius: 10px;">
                <b>✅ คำแนะนำ:</b> ซื้อตาม ตั้ง Cut Loss 5% 
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    elif st.session_state.current_strategy == "panic":
        inv_ratio = offer_3 / bid_3 if bid_3 > 0 else 0
        st.markdown(f"""
        <div class="guru-card panic-card">
            <div style="display: flex; align-items: center; gap: 20px;">
                <div style="font-size: 4rem;">💀</div>
                <div>
                    <div class="strategy-name">PANIC</div>
                    <div>วอลุ่มขายหนา {inv_ratio:.2f} เท่า เจ้ากำลังเทขาย</div>
                </div>
            </div>
            <div style="margin-top: 20px;">
                <div class="guru-quote">⚔️ ซุนวู: "三十六计 หนีคือกลยุทธ์สูงสุด"</div>
                <div class="guru-quote">🛡️ เลโอนิดัส: "วันนี้ถอย พรุ่งนี้ค่อยสู้ใหม่"</div>
            </div>
            <div style="margin-top: 15px; padding: 10px; background: #dc354520; border-radius: 10px;">
                <b>⚠️ คำแนะนำ:</b> ขาย/ชอร์ต ตั้ง Stop Loss 3%
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    elif st.session_state.current_strategy == "reversal":
        st.markdown(f"""
        <div class="guru-card reversal-card">
            <div style="display: flex; align-items: center; gap: 20px;">
                <div style="font-size: 4rem;">🎯</div>
                <div>
                    <div class="strategy-name">REVERSAL</div>
                    <div>วอลุ่มซื้อเริ่มเข้า {st.session_state.ratio:.2f} เท่า</div>
                </div>
            </div>
            <div style="margin-top: 20px;">
                <div class="guru-quote">🐂 บัฟเฟต์: "ซื้อตอนคนกลัว ขายตอนคนโลภ"</div>
                <div class="guru-quote">⚔️ ซุนวู: "จงรอให้ศึกชัดเจน แล้วค่อยลงมือ"</div>
            </div>
            <div style="margin-top: 15px; padding: 10px; background: #ffc10720; border-radius: 10px;">
                <b>⏳ คำแนะนำ:</b> รอให้ชัดเจน เตรียมซื้อเมื่อ RSI <30
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    elif st.session_state.current_strategy == "tired":
        st.markdown(f"""
        <div class="guru-card tired-card">
            <div style="display: flex; align-items: center; gap: 20px;">
                <div style="font-size: 4rem;">🎣</div>
                <div>
                    <div class="strategy-name">TIRED MARKET</div>
                    <div>วอลุ่มสมดุล {st.session_state.ratio:.2f} เท่า</div>
                </div>
            </div>
            <div style="margin-top: 20px;">
                <div class="guru-quote">💻 บิล เกตส์: "Data เงียบ จงอย่าด่วนตัดสินใจ"</div>
                <div class="guru-quote">🚀 อีลอน: "ตลาดเหนื่อย เราก็พัก รอจังหวะดีกว่า"</div>
            </div>
            <div style="margin-top: 15px; padding: 10px; background: #6c757d20; border-radius: 10px;">
                <b>👀 คำแนะนำ:</b> เฝ้าดู รอให้ Volume เพิ่มก่อน
            </div>
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

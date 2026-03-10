import streamlit as st
import requests
import streamlit.components.v1 as components
import json
import os
import time
import io
from PIL import Image
from dotenv import load_dotenv

# 1. Құпия мәліметтерді оқу
load_dotenv()

URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_KEY")
TABLE_NAME = "submissions"

# Беттің баптаулары міндетті түрде ең жоғарыда тұруы керек
st.set_page_config(page_title="8-СЫНЫП: ФИЗИКА", layout="wide", page_icon="🧲")

def send_data(payload):
    """Supabase-ке дерек жіберу функциясы"""
    headers = {
        "apikey": KEY, 
        "Authorization": f"Bearer {KEY}", 
        "Content-Type": "application/json"
    }
    return requests.post(f"{URL}/rest/v1/{TABLE_NAME}", json=payload, headers=headers)

def main():
    # --- СЕССИЯ ЖАДЫН ҚҰРУ ---
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False
    if 'photos' not in st.session_state:
        st.session_state.photos = [] 
    if 'cam_key' not in st.session_state:
        st.session_state.cam_key = 0 

    # 2. СТИЛЬ (Дизайн)
    st.markdown("""
        <style>
        body { -webkit-user-select: none; user-select: none; }
        input, textarea { -webkit-user-select: text !important; user-select: text !important; }
        .stApp { background-color: #f4f6f9; }
        .main-title { color: #1e3a8a; text-align: center; font-weight: 800; padding: 20px; border-bottom: 3px solid #3b82f6; }
        .search-section { background-color: #e0f2fe; padding: 25px; border-radius: 15px; border: 2px dashed #0284c7; margin-top: 50px; }
        .camera-box { background-color: #fef08a; padding: 20px; border-radius: 10px; border: 2px dashed #eab308; margin-bottom: 20px; }
        </style>
    """, unsafe_allow_html=True)

    # 3. НЕГІЗГІ БЕТ
    st.markdown("<h1 class='main-title'>🧲 ФИЗИКА: 8-СЫНЫП (БЖБ: Электромагниттік құбылыстар)</h1>", unsafe_allow_html=True)

    if st.session_state.submitted:
        st.balloons()
        st.success("🎉 Жұмысың сәтті қабылданды! Төмендегі іздеу бөлімінен нәтижені біле аласың.")
        if st.button("Қайта бастау 🔄"):
            st.session_state.submitted = False
            st.session_state.photos = []
            st.session_state.cam_key += 1
            st.rerun()
    else:
        st.info("📝 **Нұсқаулық:** Жұмысыңыз бірнеше беттен тұрса, әр бетті жеке түсіріп немесе жүктеп, «Тізімге қосу» батырмасын басыңыз. Соңында «Тапсыру» батырмасын басыңыз.")
        
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("👤 Оқушының аты-жөні:", placeholder="Мысалы: Асқаров Нұрлан")
        with col2:
            # ТЕК 8-СЫНЫПТАР ТІЗІМІ
            s_class = st.selectbox("🏫 Сыныбыңыз:", ["8-A", "8-B", "8-C", "8-D", "8-E", "8-F"])

        if name:
            # 🛡️ АҚЫЛДЫ АНТИ-ЧИТ ЖҮЙЕСІ (3 ескерту + қорғаныс)
            components.html(f"""
                <script>
                // Оң жақ батырманы (Right-click) және көшіруді бұғаттау
                document.addEventListener('contextmenu', event => event.preventDefault());
                document.addEventListener('keydown', function(e) {{
                    if (e.ctrlKey && (e.key === 'c' || e.key === 'v' || e.key === 'p' || e.key === 'u' || e.key === 's')) {{
                        e.preventDefault();
                    }}
                }});

                // Ескертулер санын сақтау (Оқушы қайта кірсе де сақталады)
                let cheatCount = sessionStorage.getItem('cheatCount_{name}') || 0;
                cheatCount = parseInt(cheatCount);
                let isSubmitting = false;

                // Басқа терезеге өтуді қадағалау
                document.addEventListener("visibilitychange", function() {{
                    if (document.hidden && !isSubmitting) {{
                        cheatCount++;
                        sessionStorage.setItem('cheatCount_{name}', cheatCount);

                        if (cheatCount < 3) {{
                            // Жай ғана ескерту береміз (1 немесе 2-ші рет)
                            alert("⚠️ АНТИ-ЧИТ ЕСКЕРТУІ (" + cheatCount + "/3):\\n\\nҚұрметті оқушы, тест кезінде басқа терезеге өтуге немесе хабарлама оқуға қатаң тыйым салынады! Егер 3 рет қайталанса, жұмысыңыз автоматты түрде жойылады.");
                        }} else {{
                            // 3 рет бұзды - жұмысты біржолата бұғаттау
                            alert("🚫 ЕРЕЖЕ ӨРЕСКЕЛ БҰЗЫЛДЫ:\\n\\nСіз 3 рет басқа терезеге өттіңіз. Жұмысыңыз нөлденді және мұғалімге хабарланды.");
                            
                            const payload = {{
                                student_name: "{name}",
                                student_class: "{s_class}",
                                status: "cheated",
                                answers: {{ "subject": "physics" }},
                                ai_feedback: "🚫 ЖҰМЫС ЖОЙЫЛДЫ: Оқушы тест барысында басқа терезеге 3 реттен артық өтіп, ережені өрескел бұзды."
                            }};
                            
                            fetch('{URL}/rest/v1/{TABLE_NAME}', {{
                                method: 'POST',
                                headers: {{ 'apikey': '{KEY}', 'Authorization': 'Bearer {KEY}', 'Content-Type': 'application/json' }},
                                body: JSON.stringify(payload)
                            }}).then(() => {{ 
                                isSubmitting = true;
                                sessionStorage.removeItem('cheatCount_{name}'); // Келесі тестке тазалау үшін
                                window.parent.location.reload(); 
                            }});
                        }}
                    }}
                }});
                </script>
            """, height=0)

            st.markdown("<div class='camera-box'><b>📸 Жұмысты суретке түсіру немесе жүктеу:</b></div>", unsafe_allow_html=True)
            
            # Екі бөлек қойынды (вкладка)
            tab1, tab2 = st.tabs(["📂 Дайын суретті жүктеу (Ұсынылады)", "📸 Камерамен түсіру"])
            
            with tab1:
                uploaded_file = st.file_uploader("Телефоннан немесе компьютерден анық суретті таңдаңыз", type=["jpg", "jpeg", "png"], key=f"upload_{st.session_state.cam_key}")
                if uploaded_file:
                    if st.button("➕ Осы файлды жұмысқа тіркеу", use_container_width=True, key="btn_upload"):
                        st.session_state.photos.append(uploaded_file.getvalue())
                        st.session_state.cam_key += 1
                        st.rerun()

            with tab2:
                cam_image = st.camera_input("Дәптер бетін түсіріңіз", key=f"camera_{st.session_state.cam_key}")
                if cam_image:
                    if st.button("➕ Камерадағы суретті тіркеу", use_container_width=True, key="btn_cam"):
                        st.session_state.photos.append(cam_image.getvalue())
                        st.session_state.cam_key += 1 
                        st.rerun() 

            # ТҮСІРІЛГЕН СУРЕТТЕРДІ КӨРСЕТУ ЖӘНЕ ЖОЮ
            if st.session_state.photos:
                st.write("---")
                st.markdown(f"**Сіздің жұмысыңыз ({len(st.session_state.photos)} бет):**")
                cols = st.columns(min(len(st.session_state.photos), 4))
                
                for i, photo_bytes in enumerate(st.session_state.photos):
                    with cols[i % 4]:
                        st.image(photo_bytes, caption=f"{i+1}-бет", use_container_width=True)
                        if st.button(f"🗑️ Өшіру", key=f"delete_{i}"):
                            st.session_state.photos.pop(i)
                            st.rerun()
                
                if st.button("❌ Барлығын қайтадан бастау (Суреттерді өшіру)"):
                    st.session_state.photos = []
                    st.session_state.cam_key += 1
                    st.rerun()

                st.write("---")
                
                # ЖҰМЫСТЫ ТАПСЫРУ (AI-ға жіберу)
                if st.button("ЖҰМЫСТЫ ТАПСЫРУ ✅", type="primary", use_container_width=True):
                    with st.spinner("Суреттер біріктіріліп, мұғалімге жіберілуде..."):
                        images = [Image.open(io.BytesIO(img_bytes)).convert("RGB") for img_bytes in st.session_state.photos]
                        
                        widths, heights = zip(*(i.size for i in images))
                        max_width = max(widths)
                        total_height = sum(heights)

                        stitched_image = Image.new('RGB', (max_width, total_height))
                        y_offset = 0
                        for img in images:
                            stitched_image.paste(img, (0, y_offset))
                            y_offset += img.height

                        file_name = f"physics_student_{int(time.time())}.jpg"
                        
                        # ҰСАҚ МӘТІНДЕР АНЫҚ КӨРІНУІ ҮШІН АЖЫРАТЫМДЫЛЫҚ КӨТЕРІЛДІ (2000px)
                        stitched_image.thumbnail((2000, 2000 * len(images))) 
                        
                        img_byte_arr = io.BytesIO()
                        # СУРЕТ САПАСЫ 95%-ҒА КӨТЕРІЛДІ
                        stitched_image.save(img_byte_arr, format='JPEG', quality=95, optimize=True)
                        compressed_bytes_data = img_byte_arr.getvalue()
                        
                        storage_url = f"{URL}/storage/v1/object/exam_images/{file_name}"
                        storage_headers = {
                            "apikey": KEY,
                            "Authorization": f"Bearer {KEY}",
                            "Content-Type": "image/jpeg"
                        }
                        upload_res = requests.post(storage_url, headers=storage_headers, data=compressed_bytes_data)

                        if upload_res.status_code in [200, 201]:
                            public_image_url = f"{URL}/storage/v1/object/public/exam_images/{file_name}"
                            payload = {
                                "exam_id": 4,  # <--- ФИЗИКА 8-СЫНЫП ҮШІН ИНДЕКС (мысалы 4)
                                "student_name": name, 
                                "student_class": s_class,
                                "answers": {"subject": "physics", "image_url": public_image_url},
                                "status": "pending"
                            }
                            resp = send_data(payload)
                            if resp.status_code in [200, 201, 204]:
                                st.session_state.submitted = True
                                st.rerun()
                            else:
                                st.error(f"⚠️ Базаға сақтау қатесі: {resp.text}")
                        else:
                            st.error(f"⚠️ Қоймаға жүктеу қатесі: {upload_res.text}")

    # 4. НӘТИЖЕНІ ІЗДЕУ ЖӘНЕ КӨРСЕТУ
    st.markdown("<div class='search-section'><h3>🔎 Нәтижеңді тексер</h3></div>", unsafe_allow_html=True)
    search_query = st.text_input("", key="search_input", placeholder="Іздеу үшін есіміңізді жазыңыз...")

    if search_query:
        s_headers = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
        res = requests.get(f"{URL}/rest/v1/{TABLE_NAME}?student_name=ilike.*{search_query}*&select=*&order=id.desc", headers=s_headers)
        
        if res.status_code == 200:
            results = res.json()
            if len(results) > 0:
                for data in results:
                    with st.container():
                        st.markdown(f"#### 👤 {data['student_name']} ({data['student_class']})")
                        if data['status'] == 'cheated':
                            st.error("🚫 Жұмыс жойылды: Анти-чит жүйесі іске қосылған.")
                        elif data['status'] == 'pending':
                            st.warning("⏳ Мұғалім (AI) әлі тексеріп жатыр. Сәл күте тұрыңыз...")
                        else:
                            col_score, col_fb = st.columns([1, 3])
                            with col_score:
                                raw_score = data.get('score', 0)
                                # 8-сынып физикасының макс балы - 12
                                percentage = int((raw_score / 12) * 100)
                                st.metric("Нәтиже", f"{percentage}%", delta=f"{raw_score}/12 балл")
                                st.progress(min(raw_score / 12, 1.0))
                            with col_fb:
                                with st.expander("📝 Мұғалімнің талдауы (AI)", expanded=True):
                                    st.write(data.get('ai_feedback', 'Талдау жасалуда...'))
                        st.markdown("<br>", unsafe_allow_html=True)

# Осы жерде код іске қосылады
if __name__ == "__main__":
    main()
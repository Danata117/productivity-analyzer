import streamlit as st
import requests

st.set_page_config(page_title="Анализатор продуктивности", layout="wide")

st.title("Анализатор продуктивности")
st.markdown("---")

if 'sleep_slider' not in st.session_state: st.session_state.sleep_slider = 7.0
if 'sleep_input' not in st.session_state: st.session_state.sleep_input = 7.0
if 'noise_slider' not in st.session_state: st.session_state.noise_slider = 40.0
if 'noise_input' not in st.session_state: st.session_state.noise_input = 40.0

def sync_sleep_slider(): st.session_state.sleep_slider = st.session_state.sleep_input
def sync_sleep_input(): st.session_state.sleep_input = st.session_state.sleep_slider
def sync_noise_slider(): st.session_state.noise_slider = st.session_state.noise_input
def sync_noise_input(): st.session_state.noise_input = st.session_state.noise_slider

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Физическое состояние")
    st.number_input("Часы сна", 3.0, 10.0, key="sleep_input", on_change=sync_sleep_slider)
    st.slider("Часы сна", 3.0, 10.0, key="sleep_slider", on_change=sync_sleep_input)
    
    sleep_val = st.session_state.sleep_slider
    if sleep_val < 5: sleep_status = "Ты вообще спал? Сочувствую."
    elif sleep_val < 7: sleep_status = "Маловато для гения, но жить можно."
    else: sleep_status = "Режим 'Выспавшийся титан' активирован!"
    st.success(sleep_status)

with col2:
    st.subheader("Кофеиновый заряд")
    drink_type = st.radio("Источник", ["Кофе", "Чай"], horizontal=True)
    cups = st.slider("Количество чашек", 0, 10, 1)
    mg = (95 if drink_type == "Кофе" else 47) * cups
    st.info(f"Принято кофеина: {mg} мг")

with col3:
    st.subheader("Рабочая среда")
    st.number_input("Шум (дБ)", 20.0, 80.0, key="noise_input", on_change=sync_noise_slider)
    st.slider("Шум (дБ)", 20.0, 80.0, key="noise_slider", on_change=sync_noise_input)
    
    noise_val = st.session_state.noise_slider
    if noise_val < 30: status = "Тишина как в библиотеке"
    elif noise_val < 50: status = "Фоновый гул"
    elif noise_val < 70: status = "Шумно как на вокзале"
    else: status = "Аэропорт в комнате!"
    st.warning(status)

env_map = {'Коворкинг': 'Co-working', 'Офис': 'Office', 'Дом': 'Home', 'Кафе': 'Cafe'}
task_map = {'Управленческая': 'Managerial', 'Аналитическая': 'Analytical', 'Рутинная': 'Routine', 'Творческая': 'Creative'}
env = st.selectbox("Тип среды", list(env_map.keys()))
task = st.selectbox("Тип задачи", list(task_map.keys()))

st.markdown("---")
predict_btn = st.button("РАССЧИТАТЬ ПРОГНОЗ", use_container_width=True)

if predict_btn:
    data = {
        'hours_slept': st.session_state.sleep_slider,
        'caffeine_mg': mg,
        'noise_level_db': st.session_state.noise_slider,
        'work_environment': env_map[env],
        'task_type': task_map[task]
    }
    
    try:
        response = requests.post("http://127.0.0.1:5000/predict", json=data)
        result = response.json()
        
        if 'focus_score' in result:
            score = result['focus_score']
            color = "red" if score < 40 else "orange" if score < 70 else "green"
            
            st.markdown(f"""
            <div style="border: 2px solid #555; width: 100%; height: 30px; border-radius: 5px; margin-bottom: 5px;">
                <div style="background-color: {color}; width: {score}%; height: 100%;"></div>
            </div>
            """, unsafe_allow_html=True)
            st.write(f"Уровень продуктивности: **{score:.1f}%**")
            
            if score < 40:
                advice = ["Твой мозг в режиме энергосбережения.", "Ты сегодня как зомби."]
            elif score < 70:
                advice = ["Работать можно, но без фанатизма.", "Ты — крепкий середнячок."]
            else:
                advice = ["Ты сегодня машина!", "Твой мозг работает на 110%."]
            
            st.subheader("Вердикт нейросети:")
            for item in advice:
                st.markdown(f"<p style='font-size: 20px; font-weight: bold;'>— {item}</p>", unsafe_allow_html=True)
        else:
            st.error("Ошибка API")
    except:
        st.error("Сервер не отвечает.")
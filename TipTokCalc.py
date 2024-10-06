import streamlit as st
import requests
from io import BytesIO
from PIL import Image
import pandas as pd
import os

# Подключаем стили
st.markdown("""
    <style>
        @font-face {
            font-family: 'Cascadia Mono';
            src: url('https://cdn.jsdelivr.net/gh/microsoft/cascadia-code@v2009.22/CascadiaMono.woff2') format('woff2');
        }
        body {
            font-family: 'Cascadia Mono', monospace;
            color: #F4B03F;
            background-color: #1e1e1e;
        }
        h1, h3 {
            color: #F4B03F !important;
            text-align: center;
        }
        .stButton button {
            background-color: #F4B03F !important;
            color: #535353 !important;
            font-weight: bold !important;
            font-size: 16px !important;
            border: none !important;
        }
        .stButton button:hover {
            background-color: #F4B03F !important;
        }
        .stTextInput input {
            border: 2px solid #F4B03F !important;
            color: #F4B03F !important;
        }
        .stTextInput input:focus {
            border-color: #F4B03F !important;
            box-shadow: 0 0 5px #F4B03F !important;
        }
        .large-text {
            font-size: 18px;
        }
        img {
            width: 100%;
        }
        @media screen and (max-width: 550px) {
            img {
                width: 100%;
                height: auto;
            }
        }
    </style>
""", unsafe_allow_html=True)

# URL изображения
image_url = "https://i.postimg.cc/vZmHCG8k/big.png"

# Загрузка изображения
response = requests.get(image_url)
image = Image.open(BytesIO(response.content))

# Отображаем изображение
st.image(image)

# Заголовок
st.markdown("<h1>Расчет стоимости услуг</h1>", unsafe_allow_html=True)

# Вопрос о существующей мощности
power_question = st.radio("Есть ли на объекте существующая мощность согласно техническим условиям?", ['⚡️ Да', '❌ Нет'], index=0)

# Поля для ввода мощности
if power_question == '⚡️ Да':
    P = st.number_input("Введите суммарную мощность объекта (P, кВт):", min_value=0, max_value=500000, step=1, value=None)
    Pdop = st.number_input("Введите дополнительную мощность (Pдоп, кВт):", min_value=0, max_value=500000, step=1, value=None)
else:
    P = st.number_input("Введите суммарную мощность объекта (P, кВт):", min_value=0, max_value=500000, step=1, value=None)
    Pdop = None

st.markdown("", unsafe_allow_html=True)  # Разрыв

# Выбор класса напряжения
voltage_classes = {
    "До 1000 В": 1,
    "3 - 35 кВ": 1.1,
    "110 кВ": 1.2,
    "220 кВ": 1.3
}
Ku = st.radio("Класс напряжения в точке присоединения:", list(voltage_classes.keys()))

# Получаем значение Ku_value на основе выбранного класса напряжения
Ku_value = voltage_classes[Ku]

st.markdown("", unsafe_allow_html=True)  # Разрыв

# Вопрос о компенсации реактивной мощности
Ktg = st.radio("Есть ли в технических условиях пункт по компенсации реактивной мощности?", ['✅ Есть', '❌ Нет'])

st.markdown("", unsafe_allow_html=True)  # Разрыв

# Вопрос о схемах питания
schemes = st.radio("Есть ли схемы питания электроприемников на объекте?", ['✅ Есть', '❌ Нет'])

if schemes == '✅ Есть':
    X = st.number_input("Количество участков ЛЭП от центра питания до каждого электроприемника:", min_value=0, max_value=5000, step=1, value=None)
    Y = st.number_input("Количество электроприемников:", min_value=0, max_value=5000, step=1, value=None)
else:
    Y = st.number_input("Количество электроприемников:", min_value=0, max_value=5000, step=1, value=None)
    X = Y * 1.05

st.markdown("", unsafe_allow_html=True)  # Разрыв

# Вопрос о сопровождении согласования
Kc = st.radio("Требуется ли сопровождение согласования РД в электрических сетях?", ['📝 Требуется', '❌ Не требуется'])

st.markdown("", unsafe_allow_html=True)  # Разрыв

# Кнопка расчета
if st.button('РАСЧЁТ'):
    try:
        if P <= 0:
            st.error("Параметры должны быть больше нуля")
        else:
            # Рассчитываем коэффициенты
            Kp = (0.8533 * Pdop ** 0.0599 + (0.8533 * P ** 0.0599 - 0.8533 * Pdop ** 0.0599) * Pdop / P) if Pdop else 0.8533 * P ** 0.0599
            Ktg_value = 1.1 if Ktg == '✅ Есть' else 1
            Kc_value = 1.05 if Kc == '📝 Требуется' else 1

            if schemes == '✅ Есть':
                Gx = 1892.9 * X ** -0.544
                Gy = 379.89 * Y ** -0.271
                Gz = 0  # Gz не рассчитываем
            else:
                Gx = 1892.9 * X ** -0.544
                Gy = 379.89 * Y ** -0.271
                Gz = 966.81 * 2 * X ** -0.424

            # Общая стоимость
            cost = round(((X * Gx + Y * Gy) * Kp * Ku_value * Ktg_value * Kc_value + X * Gz) / 100) * 100
            st.markdown(
                f"""
                <div style='background-color: rgba(46, 139, 87, 0.15); padding: 20px; border-radius: 10px; text-align: center;'>
                    <h1 style='color: #F4B03F;'>Общая стоимость: {cost} рублей</h1>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Сбор статистики
            statistics_file_path = r"C:\Users\wanss\OneDrive\Рабочий стол\TipTok\Calc_stat.xlsx"
            
            if os.path.isfile(statistics_file_path):
                df = pd.read_excel(statistics_file_path)
            else:
                df = pd.DataFrame(columns=["№", "Тип услуги", "P", "Pдоп", "U", "КРМ", "Схемы", "Участки", "ЭП", "Согласование", "Стоимость"])

            new_row = {
                "№": len(df) + 1,
                "Тип услуги": "КЭЭ",
                "P": P,
                "Pдоп": Pdop,
                "U": Ku,
                "КРМ": Ktg,
                "Схемы": schemes,
                "Участки": X,
                "ЭП": Y,
                "Согласование": Kc,
                "Стоимость": cost
            }

            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

            # Проверяем, есть ли ошибки перед записью
            st.write("Данные для записи: ", new_row)

            # Записываем данные в Excel
            try:
                with pd.ExcelWriter(statistics_file_path, engine='openpyxl', mode='w') as writer:
                    df.to_excel(writer, index=False)
                st.success("Данные успешно записаны в файл.")
            except Exception as e:
                st.error(f"Ошибка записи в файл: {e}")

    except Exception as e:
        st.error(f"Ошибка: {e}")

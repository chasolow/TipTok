import streamlit as st
import requests
from io import BytesIO
from PIL import Image

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
        }
        h1, h3 {
            color: #F4B03F !important;
        }
        .stButton button {
            background-color: #F4B03F !important;
            color: #535353 !important;
            font-weight: bold !important;
            font-size: 16px !important;
        }
        img {
            width: 580px;
        }
        @media screen and (max-width: 600px) {
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
st.markdown("<h1 style='text-align: center;'>Рассчет стоимости услуг</h1>", unsafe_allow_html=True)

# Вопрос о мощности с новыми вариантами
power_question = st.radio("Есть ли на объекте существующая мощность согласно техническим условиям?", ['⚡️ Да', '❌ Нет'])

# Поля для ввода мощности в одну строку
col1, col2 = st.columns(2)
if power_question == '⚡️ Да':
    with col1:
        P = st.number_input("Введите суммарную мощность объекта (P, кВт):", min_value=0, max_value=500000, step=0.001, value=0)
    with col2:
        Pdop = st.number_input("Введите дополнительную мощность (Pдоп, кВт):", min_value=0, max_value=500000, step=0.001, value=0)
else:
    with col1:
        P = st.number_input("Введите суммарную мощность объекта (P, кВт):", min_value=0, max_value=500000, step=0.001, value=0)
    Pdop = None

# Преобразуем текст в числа для расчетов
P = float(P)
Pdop = float(Pdop) if Pdop else None

# Выбор класса напряжения с помощью radio
Ku = st.radio("Класс напряжения в точке присоединения:", [("До 1000 В", 1), ("3 - 35 кВ", 1.1), ("110 кВ", 1.2), ("220 кВ", 1.3)])

# Вопрос о компенсации реактивной мощности с новыми вариантами
Ktg = st.radio("Есть ли в технических условиях пункт по компенсации реактивной мощности?", ['✅ Есть', '❌ Нет'])

# Вопрос о схемах питания с новыми вариантами
schemes = st.radio("Есть ли схемы питания электроприемников на объекте?", ['✅ Есть', '❌ Нет'])

# Поля для ввода схем
if schemes == '✅ Есть':
    col3, col4 = st.columns(2)
    with col3:
        X = st.number_input("Количество участков ЛЭП от центра питания до каждого электроприемника:", min_value=0, max_value=5000, step=1, value=0)
    with col4:
        Y = st.number_input("Количество электроприемников:", min_value=0, max_value=5000, step=1, value=0)
else:
    Y = st.number_input("Количество электроприемников:", min_value=0, max_value=5000, step=1, value=0)
    X = Y * 1.05

# Вопрос о сопровождении согласования с новыми вариантами
Kc = st.radio("Требуется ли сопровождение согласования РД в электрических сетях?", ['📝 Требуется', '❌ Не требуется'])

# Кнопка расчета
if st.button('РАССЧЁТ'):
    try:
        if P <= 0:
            st.error("Параметры должны быть больше нуля")
        else:
            # Рассчитываем коэффициенты
            Kp = (0.8533 * Pdop ** 0.0599 + (0.8533 * P ** 0.0599 - 0.8533 * Pdop ** 0.0599) * Pdop / P) if Pdop else 0.8533 * P ** 0.0599
            Ku_value = Ku[1]
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
            st.success(f"Общая стоимость: {cost} рублей")

    except ZeroDivisionError:
        st.error("Ошибка: деление на ноль невозможно.")
    except ValueError as e:
        st.error(f"Ошибка: {e}")

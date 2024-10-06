import streamlit as st
import requests
from io import BytesIO
from PIL import Image
import pandas as pd
import os

# Подключаем стили
st.markdown("""
    <style>
        /* ваши стили */
    </style>
""", unsafe_allow_html=True)

# Загружаем изображение
image_url = "https://i.postimg.cc/vZmHCG8k/big.png"
response = requests.get(image_url)
image = Image.open(BytesIO(response.content))
st.image(image)

# Заголовок
st.markdown("<h1>Расчет стоимости услуг</h1>", unsafe_allow_html=True)

# Ввод данных
power_question = st.radio("Есть ли на объекте существующая мощность согласно техническим условиям?", ['⚡️ Да', '❌ Нет'], index=0)
P = st.number_input("Введите суммарную мощность объекта (P, кВт):", min_value=0, max_value=500000, step=1, value=None)
Pdop = st.number_input("Введите дополнительную мощность (Pдоп, кВт):", min_value=0, max_value=500000, step=1, value=None) if power_question == '⚡️ Да' else None

# Выбор класса напряжения
voltage_classes = {
    "До 1000 В": 1,
    "3 - 35 кВ": 1.1,
    "110 кВ": 1.2,
    "220 кВ": 1.3
}
Ku = st.radio("Класс напряжения в точке присоединения:", list(voltage_classes.keys()))
Ku_value = voltage_classes[Ku]

# Вопрос о компенсации реактивной мощности
Ktg = st.radio("Есть ли в технических условиях пункт по компенсации реактивной мощности?", ['✅ Есть', '❌ Нет'])
schemes = st.radio("Есть ли схемы питания электроприемников на объекте?", ['✅ Есть', '❌ Нет'])

X = st.number_input("Количество участков ЛЭП от центра питания до каждого электроприемника:", min_value=0, max_value=5000, step=1, value=None) if schemes == '✅ Есть' else 0
Y = st.number_input("Количество электроприемников:", min_value=0, max_value=5000, step=1, value=None)

Kc = st.radio("Требуется ли сопровождение согласования РД в электрических сетях?", ['📝 Требуется', '❌ Не требуется'])

# Кнопка расчета
if st.button('РАСЧЁТ'):
    try:
        if P <= 0:
            st.error("Параметры должны быть больше нуля")
        else:
            Kp = (0.8533 * Pdop ** 0.0599 + (0.8533 * P ** 0.0599 - 0.8533 * Pdop ** 0.0599) * Pdop / P) if Pdop else 0.8533 * P ** 0.0599
            Ktg_value = 1.1 if Ktg == '✅ Есть' else 1
            Kc_value = 1.05 if Kc == '📝 Требуется' else 1

            Gx = 1892.9 * X ** -0.544
            Gy = 379.89 * Y ** -0.271
            Gz = 966.81 * 2 * X ** -0.424

            cost = round(((X * Gx + Y * Gy) * Kp * Ku_value * Ktg_value * Kc_value + X * Gz) / 100) * 100
            st.markdown(f"<h1 style='color: #F4B03F;'>Общая стоимость: {cost} рублей</h1>", unsafe_allow_html=True)

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

            st.write("Данные для записи: ", new_row)

            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

            # Запись данных в Excel
            try:
                with pd.ExcelWriter(statistics_file_path, engine='openpyxl', mode='w') as writer:
                    df.to_excel(writer, index=False)
                st.success("Данные успешно записаны в файл.")
            except Exception as e:
                st.error(f"Ошибка записи в файл: {e}")

    except Exception as e:
        st.error(f"Ошибка: {e}")

import streamlit as st
import requests
from io import BytesIO
from PIL import Image
import pandas as pd
import os

# Подключаем стили
st.markdown(""" 
    <style> 
        /* Ваши стили */ 
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

# Используем HTML для увеличенного текста
power_question = st.radio("Есть ли на объекте существующая мощность согласно техническим условиям?", ['⚡️ Да', '❌ Нет'], index=0)

# Поля для ввода мощности с использованием number_input
if power_question == '⚡️ Да':
    P = st.number_input("Введите суммарную мощность объекта (P, кВт):", min_value=0, max_value=500000, step=1, value=None)
    Pdop = st.number_input("Введите дополнительную мощность (Pдоп, кВт):", min_value=0, max_value=500000, step=1, value=None)
else:
    P = st.number_input("Введите суммарную мощность объекта (P, кВт):", min_value=0, max_value=500000, step=1, value=None)
    Pdop = None

# Выбор класса напряжения с помощью radio
voltage_classes = {
    "До 1000 В": 1,
    "3 - 35 кВ": 1.1,
    "110 кВ": 1.2,
    "220 кВ": 1.3
}
Ku = st.radio("Класс напряжения в точке присоединения:", list(voltage_classes.keys()))

# Получаем значение Ku_value на основе выбранного класса напряжения
Ku_value = voltage_classes[Ku]

# Вопрос о компенсации реактивной мощности 
Ktg = st.radio("Есть ли в технических условиях пункт по компенсации реактивной мощности?", ['✅ Есть', '❌ Нет'])

# Вопрос о схемах питания
schemes = st.radio("Есть ли схемы питания электроприемников на объекте?", ['✅ Есть', '❌ Нет'])

if schemes == '✅ Есть':
    X = st.number_input("Количество участков ЛЭП от центра питания до каждого электроприемника:", min_value=0, max_value=5000, step=1, value=None)
    Y = st.number_input("Количество электроприемников:", min_value=0, max_value=5000, step=1, value=None)
else:
    Y = st.number_input("Количество электроприемников:", min_value=0, max_value=5000, step=1, value=None)
    X = Y * 1.05

# Вопрос о сопровождении согласования 
Kc = st.radio("Требуется ли сопровождение согласования РД в электрических сетях?", ['📝 Требуется', '❌ Не требуется'])

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

            # Сбор статистики и запись в Excel
            file_path = r"C:\Users\wanss\OneDrive\Рабочий стол\TipTok\Calc_stat_test.xlsx"  # Сохраняем в новый файл
            if os.path.isfile(file_path):
                df = pd.read_excel(file_path)
                new_index = len(df) + 1
                st.write("Файл существует, добавление новой записи.")
            else:
                df = pd.DataFrame(columns=["№", "Тип услуги", "P", "Pдоп", "U", "КРМ", "Схемы", "Участки", "ЭП", "Согласование", "Стоимость"])
                new_index = 1
                st.write("Создан новый файл.")

            # Проверка перед добавлением
            st.write(f"Проверяем данные для добавления: {new_index}, 'КЭЭ', {P}, {Pdop}, {Ku}, {Ktg}, {schemes}, {X}, {Y}, {Kc}, {cost}")

            new_row = {
                "№": new_index,
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

            # Добавление новой строки
            df = df.append(new_row, ignore_index=True)

            # Попробуем записать в Excel с помощью ExcelWriter
            try:
                with pd.ExcelWriter(file_path, engine='openpyxl', mode='a' if os.path.isfile(file_path) else 'w') as writer:
                    df.to_excel(writer, index=False)
                st.success("Данные успешно записаны в файл.")
            except Exception as e:
                st.error(f"Ошибка записи в файл: {e}")

    except ZeroDivisionError:
        st.error("Ошибка: деление на ноль невозможно.")
    except ValueError as e:
        st.error(f"Ошибка: {e}")

import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(
    page_title="Аналитика магазина",
    layout="wide"
)

st.title("Аналитика интернет-магазина")

conn = sqlite3.connect("shop.db")

df = pd.read_sql_query(
    "SELECT * FROM sales",
    conn
)

conn.close()

df["revenue"] = df["price"] * df["quantity"]

with st.sidebar:
    st.header("Фильтры")

    categories = sorted(df["category"].unique())

    selected = st.multiselect(
        "Выберите категории",
        categories,
        default=categories
    )

    filtered = df[df["category"].isin(selected)]

    products = sorted(df["product"].unique())

    selected_products = st.multiselect(
        "Выберите товары",
        products,
        default=products
    )

    filtered = filtered[filtered["product"].isin(selected_products)]

st.subheader("Ключевые показатели")

avg_price = filtered["price"].mean() if not filtered.empty else 0

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Общая выручка",
        f'{filtered["revenue"].sum():,.0f} ₸'
    )

with col2:
    st.metric(
        "Продано товаров",
        int(filtered["quantity"].sum())
    )

with col3:
    st.metric(
        "Количество записей",
        len(filtered)
    )

with col4:
    st.metric(
        "Средняя цена",
        f'{avg_price:,.0f} ₸'
    )

st.subheader("Визуализация продаж")

if not filtered.empty:
    col_left, col_right = st.columns(2)

    with col_left:
        chart = (
            filtered.groupby("product", as_index=False)
            ["revenue"].sum()
        )

        fig = px.bar(
            chart,
            x="product",
            y="revenue",
            title="Выручка по товарам"
        )
        fig.update_layout(xaxis_title="Товар", yaxis_title="Выручка, ₸")

        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        category_chart = (
            filtered.groupby("category", as_index=False)
            ["revenue"].sum()
        )

        fig_pie = px.pie(
            category_chart,
            names="category",
            values="revenue",
            title="Доля выручки по категориям"
        )

        st.plotly_chart(fig_pie, use_container_width=True)

    daily_chart = (
        filtered.groupby("sale_date", as_index=False)
        ["revenue"].sum()
        .sort_values("sale_date")
    )

    fig_line = px.line(
        daily_chart,
        x="sale_date",
        y="revenue",
        markers=True,
        title="Динамика выручки по датам",
        labels={"sale_date": "Дата", "revenue": "Выручка, ₸"}
    )

    st.plotly_chart(fig_line, use_container_width=True)

    st.subheader("Таблица продаж")
    st.dataframe(filtered, use_container_width=True)
else:
    st.info("Нет данных для выбранных категорий")

st.subheader("Экспорт отчёта")

csv = filtered.to_csv(
    index=False
).encode("utf-8-sig")

st.download_button(
    "Скачать CSV",
    csv,
    file_name="sales_report.csv",
    mime="text/csv"
)

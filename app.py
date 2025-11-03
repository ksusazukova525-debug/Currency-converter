import streamlit as st
from currency_fetcher import CurrencyFetcher

def init_app():
    if 'fetcher' not in st.session_state:
        st.session_state.fetcher = CurrencyFetcher()
        with st.spinner('Загрузка курсов валют...'):
            success = st.session_state.fetcher.fetch_rates()
            if not success:
                st.error('Не удалось загрузить курсы валют. Проверьте подключение к интернету.')
                st.stop()

def main():
    st.set_page_config(
        page_title="Конвертер валют",
        layout="wide"
    )
    init_app()
    fetcher = st.session_state.fetcher
    st.title('💱 Конвертер валют')
    st.markdown('**Курсы валют ЦБ РФ** | Источник: [cbr.ru](https://cbr.ru/currency_base/daily/)')
    st.divider()
    currencies = fetcher.get_all_currencies()
    currency_codes = sorted(currencies.keys())
    col1, col2, col3 = st.columns(3)
    with col1:
        amount = st.number_input(
            'Сумма:',
            min_value=0.0,
            value=100.0,
            step=0.01,
            format="%.2f"
        )
    with col2:
        default_from_index = currency_codes.index('USD') if 'USD' in currency_codes else 0
        from_currency = st.selectbox(
            'Из:',
            currency_codes,
            index=default_from_index,
            format_func=lambda x: f"{x} - {currencies[x]}"
        )
    with col3:
        default_to_index = currency_codes.index('RUB') if 'RUB' in currency_codes else 0
        to_currency = st.selectbox(
            'В:',
            currency_codes,
            index=default_to_index,
            format_func=lambda x: f"{x} - {currencies[x]}"
        )
    st.markdown('<br>', unsafe_allow_html=True)
    if st.button('Конвертировать', type='primary', use_container_width=True):
        if amount <= 0:
            st.warning('Пожалуйста, введите сумму больше нуля.')
        elif from_currency == to_currency:
            st.info('Исходная и целевая валюты совпадают.')
            result_text = f"{amount:.2f} {from_currency} = {amount:.2f} {to_currency}"
            st.success(f"### {result_text}")
        else:
            result = fetcher.convert(amount, from_currency, to_currency)
            if result is not None:
                result_text = f"{amount:.2f} {from_currency} = {result:.2f} {to_currency}"
                st.success(f"### {result_text}")
                from_info = fetcher.get_currency_info(from_currency)
                to_info = fetcher.get_currency_info(to_currency)
                with st.expander("Детали курса"):
                    if from_info and to_info:
                        st.write(f"**{from_currency}:** {from_info}")
                        st.write(f"**{to_currency}:** {to_info}")
            else:
                st.error('Ошибка при конвертации валют.')
    st.divider()
    with st.expander("Показать все курсы валют"):
        if fetcher.df is not None:
            display_df = fetcher.df.copy()
            display_df = display_df.rename(columns={'Курс': 'Курс (руб.)'})
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            st.caption(f'Всего валют: {len(display_df)}')
        else:
            st.warning('Данные о курсах валют не загружены.')
    st.markdown('---')
    st.caption('Данные обновляются при каждой загрузке страницы')

if __name__ == '__main__':
    main()


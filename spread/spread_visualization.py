import streamlit as st
import pandas as pd

from convert import *

def init_state():
    if 'spread_vertical' not in st.session_state:
        # st.session_state.spread_vertical = pd.DataFrame()
        st.session_state.spread_vertical = pd.read_csv('spread/spread_vertical.csv').fillna('')
    if 'spread_butterfly' not in st.session_state:
        # st.session_state.spread_butterfly = pd.DataFrame()
        st.session_state.spread_butterfly = pd.read_csv('spread/spread_butterfly.csv').fillna('')
    if 'vertical_page_number' not in st.session_state:
        st.session_state.vertical_page_number = 0
    if 'butterfly_page_number' not in st.session_state:
        st.session_state.butterfly_page_number = 0

if __name__ == '__main__':
    init_state()

    predict_button = st.sidebar.button('Predict Spreads')
    if predict_button:
        st.session_state.spread_vertical = pd.DataFrame()
        st.session_state.spread_butterfly = pd.DataFrame()
        st.session_state.vertical_page_number = 0
        st.session_state.butterfly_page_number = 0
        st.session_state.spread_vertical = predict_spread('VERTICAL')
        st.session_state.spread_butterfly = predict_spread('BUTTERFLY')
        pass
    spread_option = st.sidebar.selectbox('Spread Type', ['VERTICAL', 'BUTTERFLY'])
    if spread_option == 'VERTICAL':
        if len(st.session_state.spread_vertical) == 0:
            st.subheader("None Vertical Spread")
        else:
            st.subheader("Vertical Spread")
            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
            page_number = st.session_state.vertical_page_number
            length = len(st.session_state.spread_vertical)
            last_number = (length - 1) // 100
            if col3.button('Prev'):
                if page_number == 0:
                    page_number = last_number
                else:   page_number -= 1
                print (page_number)
            if col6.button('Next'):
                if page_number == last_number:
                    page_number = 0
                else:   page_number += 1
                print (page_number)
            st.session_state.vertical_page_number = page_number
            st.text_input('Page Number', value=st.session_state.vertical_page_number, key='readonly', disabled=True)
            if page_number * 100 + 100 > length:
                st.table(st.session_state.spread_vertical[page_number * 100:length])
            else:
                st.table(st.session_state.spread_vertical[page_number * 100:page_number * 100 + 100])
        pass
    if spread_option == 'BUTTERFLY':
        if len(st.session_state.spread_butterfly) == 0:
            st.subheader("None Butterfly Spread")
        else:
            st.subheader("Butterfly Spread")
            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
            page_number = st.session_state.butterfly_page_number
            length = len(st.session_state.spread_butterfly)
            last_number = (length - 1) // 100
            if col3.button('Prev'):
                if page_number == 0:
                    page_number = last_number
                else:   page_number -= 1
                print (page_number)
            if col6.button('Next'):
                if page_number == last_number:
                    page_number = 0
                else:   page_number += 1
                print (page_number)
            st.session_state.butterfly_page_number = page_number
            st.text_input('Page Number', value=st.session_state.butterfly_page_number, key='readonly', disabled=True)
            if page_number * 100 + 100 > length:
                st.table(st.session_state.spread_butterfly[page_number * 100:length])
            else:
                st.table(st.session_state.spread_butterfly[page_number * 100:page_number * 100 + 100])
        pass
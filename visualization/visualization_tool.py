import streamlit as st
import tkinter as tk
from tkinter import filedialog

import pandas as pd
import numpy as np
import os

from tensorflow.keras.models import load_model
from tws_api import *

def init_state():
    if 'database_path' not in st.session_state:
        st.session_state.database_path = ''
    if 'file_list' not in st.session_state:
        st.session_state.file_list = []
    if 'file_index' not in st.session_state:
        st.session_state.file_index = 0
    if 'past_data_count' not in st.session_state:
        st.session_state.past_data_count = 10
    if 'progress_value' not in st.session_state:
        st.session_state.progress_value = 0
    
if __name__ == '__main__':
    init_state()
    
    root = tk.Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)

    page_option = st.sidebar.selectbox('Select Page', ['Database Upload', 'Predict'])
    if page_option == 'Database Upload':
        if st.sidebar.button('Upload Database'):
            st.session_state.database_path = filedialog.askdirectory(master=root)
            options_path = st.session_state.database_path + "/options"
            stocks_path = st.session_state.database_path + "/stocks"
            if os.path.exists(options_path) and os.path.exists(stocks_path):
                if len(os.listdir(options_path)) == len(os.listdir(stocks_path)):
                    st.sidebar.success('Succesfully upload csv files!')
                    st.session_state.file_list.clear()
                    st.session_state.file_index = 0
                    for file in os.listdir(options_path):
                        st.session_state.file_list.append(file[:10])
                else: 
                    st.sidebar.warning("no matching with stock and option data")
            else:
                st.sidebar.error("There is no stock or option data")
        st.sidebar.text_input('Datbase Path:', st.session_state.database_path, disabled=True)
        if len(st.session_state.file_list) > 0:
            view_file_name = st.sidebar.selectbox('Select data', st.session_state.file_list, index = 0)
            st.session_state.file_index = st.session_state.file_list.index(view_file_name)
            
            # options_data = pd.read_csv(st.session_state.database_path + '/options/' + st.session_state.file_list[st.session_state.file_index] + 'options.csv')
            # stocks_data = pd.read_csv(st.session_state.database_path + '/stocks/' + st.session_state.file_list[st.session_state.file_index] + 'stocks.csv')
            options_data = get_historical_option_data
            stocks_data = get_historical_stock_data
            
            st.subheader("Option data")
            st.table(options_data[0:100])
            st.subheader("Stock data")
            st.table(stocks_data[0:100])
        
        # col1, col2 = st.columns(2)
        # with col1:
        #     st.button('Previous')
        # with col2:
        #     st.button('Next')
        
    elif page_option == 'Predict':
        
        show_count = st.sidebar.number_input('Maximum value count', min_value = 10, max_value = 50, value = 10, step = 1)

        if len(st.session_state.file_list) > 0:
            progress_status = st.empty()
            progress_bar = st.progress(0, 'Processing')
            
            model = load_model('model.h5')
            options_path = st.session_state.database_path + '/options'
            past_data = []
            past_data_count = st.session_state.past_data_count
            for file in os.listdir(options_path)[-past_data_count:]:
                df = pd.read_csv(os.path.join(options_path, file))
                st.session_state.progress_value = past_data.append(df[:])
                progress_status.text(f'Loading csv files {len(past_data) / past_data_count * 100}% ...')
                progress_bar.progress(len(past_data) / past_data_count)
            past_data = pd.concat(past_data, ignore_index = True)
            progress_status.text('Loading completed!')

            grouped = past_data.groupby('contract')
            contracts = []
            premium = []

            data_count = 0
            for key, group in grouped:
                if(len(group) == past_data_count):
                    data_count += 1
            print(data_count)
            
            cur = 0
            # data_count = 1000
            underlying = []
            for key, group in grouped:
                if(len(group) == past_data_count):
                    contracts.append(key)
                    premium.append((group['bid'] + group['ask']) / 2)
                    underlying.append(group['underlying'].iloc[0])
                    cur += 1
                    if cur % 1000 == 0:
                        progress_bar.progress(cur / data_count)
                        progress_status.text(f'Data processing {cur / data_count * 100}% ...')
                        # break
            progress_status.text('Data processing Finished!')

            premium = np.array(premium)
            test = premium[:,1:] - premium[:,:-1]
            pred = []
            divide_count = 100
            
            for i in range(divide_count):
                pred.append(model.predict(test[int(data_count / divide_count * i):int(data_count / divide_count * (i + 1))]).round(4))
                progress_bar.progress(i / divide_count)
                progress_status.text(f'Predictin {i / divide_count * 100}% ...')
            pred = np.concatenate(pred)
            print(pred.shape)
            progress_status.text('Prediction Finished!')

            predf = pd.DataFrame()
            predf['underlying'] = underlying
            predf['contract'] = contracts
            predf['premium'] = premium[:,-1]
            predf['predict_value'] = pred.flatten()
            predf['predict_percent'] = predf['predict_value'] / predf['premium'] * 100
            st.table(predf[0:100])

            sorted_predf_top = predf.sort_values(by='predict_value', ascending=False).reset_index(drop=True)
            sorted_predf_bottom = predf.sort_values(by='predict_value', ascending=True).reset_index(drop=True)
            st.table(sorted_predf_top[:show_count])
            st.table(sorted_predf_bottom[:show_count])

            if st.sidebar.button('Donwload csv files!'):
                writer = pd.ExcelWriter('visualization/predict result.xlsx', engine='xlsxwriter')
                predf.to_excel(writer, sheet_name='predict results', index = False)
                sorted_predf_top[:show_count].to_excel(writer, sheet_name=f'maximum {show_count} results', index = False)
                sorted_predf_bottom[:show_count].to_excel(writer, sheet_name=f'minimum {show_count} results', index = False)
                writer.save()
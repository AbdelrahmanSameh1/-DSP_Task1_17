from statistics import mode
from turtle import dot
from numpy import arange
from enum import Enum
from io import BytesIO, StringIO
from typing import Union
from sympy import plot
import xlsxwriter
from io import BytesIO
import streamlit.components.v1 as com
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import scipy.interpolate as int
import pandas as pd
import streamlit as st
import numpy as np
import math
import scipy as sc
import plotly.express as plotly
from streamlit_option_menu import option_menu

st.set_page_config(page_title="Sampling Studio", page_icon=":radio:",layout="wide")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """

st.markdown(hide_st_style, unsafe_allow_html=True)

with open("style.css") as source_des:
    st.markdown(f"""<style>{source_des.read()}</style>""", unsafe_allow_html=True)

com.html("""                 

""")
          
selected =option_menu("Main Menu", ["Home",'Generate', "Upload"],
            icons=[ "house", "play", "cloud-upload"], menu_icon="cast", default_index=0, orientation="horizontal")    


# Start Values
Fs = 1000    #Sampling Freqyency
t = np.arange(0, 1, 1 / Fs)    # Time Domain


if selected=="Home":
    st.title("Welcome")

if selected=="Generate":
    st.title("Sketch Form")
    freq = st.sidebar.slider('Enter Your Frequency',min_value=1,max_value=100)   #frequency of the generated signal
    amp = st.sidebar.slider('Enter Your Amplitude',min_value=1,max_value=100)    #amplitude of the generated signal
    Signal = amp * np.sin(2 * np.pi * freq * t)                                  #generate the sine signal
    figure = plotly.line(Signal, x=t, y=Signal)
    figure.update_layout(template='simple_white',
    yaxis_title='Amplitude (v)',
    title='Generated Signal',
    xaxis_title="Time (sec)" ,
    hovermode="x"
)
    st.plotly_chart(figure,use_container_width=True)
    if st.sidebar.checkbox("Add"):
        freq1 = st.sidebar.number_input('Enter Your Frequency')   #frequency 
        amp1 = st.sidebar.number_input('Enter Your Amplitude')    #amplitude 
        Signal1 = amp1 * np.sin(2 * np.pi * freq1 * t)
        if st.sidebar.button("Add Signal"):
            figure.add_scatter(x=t, y=Signal1, mode='lines')
            figure.update_traces(
             name='Added Signal'
                )
            st.plotly_chart(figure,use_container_width=True)
        if st.sidebar.button("Sum"):
                Sig = Signal + Signal1
                figure.add_scatter(x=t, y=Sig, mode='lines')
                figure.update_traces(
                 name='Sum Signal'
                )
                st.plotly_chart(figure,use_container_width=True)
        if st.sidebar.button("Remove"):
            FinalSignal = Signal - Signal1
            figure.add_scatter(x=t, y=FinalSignal, mode='lines')
            figure.update_traces(
             name='Removed Signal'
                )
            st.plotly_chart(figure, use_container_width=True)
    if st.sidebar.checkbox("Add Noise"):
        SNR = st.sidebar.slider("Enter Your SNR",min_value=0,max_value=50)
        snr = 10.0**(SNR/10.0)
        p1 = Signal.var()   #power signal
        Noise = p1/snr       # power noise
        w = sc.sqrt(Noise)*sc.randn(1000)    #Noise Signal
        # Add noise to signal 
        s1 = Signal + w          #Signal after Noise
        figure = plotly.line(s1, x=t, y=s1)
        figure.update_layout(template='simple_white',
        yaxis_title='Amplitude (v)',
        title='Noise Signal',
        xaxis_title="Time (sec)" ,
        hovermode="x"
)
        st.plotly_chart(figure,use_container_width=True)



    if st.sidebar.checkbox("Sampling"):
        st.title(" Sample View ")
        sample_freq = st.sidebar.slider('Enter Your Sampling Frequency',min_value=1,max_value=50)
        T=1/sample_freq   #Sampling Time
        n=np.arange(0.5, 1/T)
        nt=T*n  
        Signal2 = amp * np.sin(2 * np.pi * freq* nt)
        Signal3 = amp * np.sin(2 * np.pi * freq* t)
        figure_sample = plotly.line(Signal3, x=t, y=Signal3)
        figure_sample.add_scatter(x=nt, y=Signal2, mode='markers')
        figure_sample.update_traces(
             name='Samples'
                )
        figure_sample.update_layout(template='simple_white',
        yaxis_title='Amplitude (v)',
        title='Sampling Signal',
        xaxis_title="Time (sec)" ,
        hovermode="x"
    )
        st.plotly_chart(figure_sample, use_container_width=True) 
        # to interpolate
        sum=0
        for i in n:
            s_sample = amp * np.sin(2 * np.pi * freq *i* T) 
            sum+= np.dot( s_sample , np.sinc((t - i*T)/T) ) 
        figure_sample.add_scatter(x=t, y=sum ,mode="lines")
        figure_sample.update_traces(
             name='Interpolated Signal'
                )
        st.plotly_chart(figure_sample, use_container_width=True)
        

       
    if st.sidebar.button("Download"):
        #download a file as excel
        output = BytesIO()
        # Write files to in-memory strings using BytesIO
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()
        worksheet.write_column(0,0,t)
        worksheet.write_column(0,1,Signal)
        workbook.close()
        st.download_button(
        label="Download",
        data=output.getvalue(),
        file_name="signal.xlsx",
        mime="application/vnd.ms-excel"
        )

 
if selected=="Upload" :
   file=st.file_uploader("Upload Files",type={"csv","txt","xlsx"})
   if file is not None:
    signal_upload=pd.read_excel(file)
    fig2= plotly.line(signal_upload, x=signal_upload.columns[0], y=signal_upload.columns[1], title="Uploaded Signal")
    fig2.update_layout(template='simple_white',
    yaxis_title='Amplitude (v)',
    title='Uploaded Signal',
    xaxis_title="Time (sec)" ,
    hovermode="x"
)
    st.plotly_chart(fig2,use_container_width=True)
    #st.write(signal_upload.describe())
    add_uploaded= st.sidebar.checkbox("Add Signal")
    if add_uploaded:
        f = st.sidebar.number_input('Enter Your Frequency')    #frequency
        a = st.sidebar.number_input('Enter Your Amplitude')    #amplitude
        S = a * np.sin(2 * np.pi * f * t)              #sin_signal
        if st.sidebar.button("Add Signal "):
             fig2.add_scatter(x=t, y=S, mode='lines')
             fig2.update_traces(
             name='Added Signal'
                )
             st.plotly_chart(fig2,use_container_width=True)
        




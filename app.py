from pickle import TRUE
from tkinter.tix import Tree
from turtle import color, onclick, onkeyrelease, width
from typing_extensions import Self
from pyparsing import Or
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as pp
import plotly.express as plotly
from scipy.interpolate import interp1d
from scipy import signal
import scipy as sc
import math
import xlsxwriter
from io import BytesIO


st.set_page_config(page_title="Sampling Studio",
                   page_icon=":radio:", layout="wide")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

if 'time' not in st.session_state:
    st.session_state['time'] = np.linspace(0, 1, 1000)

if 'table' not in st.session_state:
    st.session_state['table'] = []


if 'highest_freq' not in st.session_state:
    st.session_state['highest_freq'] = 0


if 'signal_drawn' not in st.session_state:
    st.session_state['signal_drawn'] = np.zeros(len(st.session_state['time']))
    for i in range(len(st.session_state['time'])):
        Signal = 1*np.sin(2*np.pi*1*st.session_state['time'][i])
        st.session_state['signal_drawn'][i] += Signal
    st.session_state['table'].append(
        [1, 1])


if 'sampled_signal_drawn' not in st.session_state:
    st.session_state['sampled_signal_drawn'] = []

if 'freqsample' not in st.session_state:
    st.session_state['freqsample'] = 0

if 'table' not in st.session_state:
    st.session_state['table'] = []


# get the highest frequency
for item in st.session_state['table']:
    # st.write(item)
    if item[1] > st.session_state['highest_freq']:
        st.session_state['highest_freq'] = item[1]

# st.write(st.session_state['highest_freq'])


figure = plotly.line()

figure = plotly.line(
    x=st.session_state['time'], y=st.session_state['signal_drawn'])
figure.update_layout(width=5000, height=500,
                     template='simple_white',
                     yaxis_title='Amplitude (V)',
                     xaxis_title="Time (Sec)",
                     hovermode="x")


def update_signal(magnitude, frequency):
    for i in range(len(st.session_state['time'])):
        st.session_state['signal_drawn'][i] += magnitude * \
            np.sin(2*np.pi*frequency*st.session_state['time'][i])


# def update_signal2(magnitude, frequency):
#     y = magnitude*np.sin(2*np.pi*frequency*st.session_state['time'])
#     st.session_state['fig2'].add_scatter(
#         x=st.session_state['time'], y=y, name="frequency:"+str(frequency))


def noise(snr, add):
    global figure
    if add:
        SNR = 10.0**(snr/10.0)
        p1 = st.session_state['signal_drawn'].var()
        n = p1/SNR
        noise = sc.sqrt(n)*sc.randn(len(st.session_state['signal_drawn']))
        mixed = st.session_state['signal_drawn']+noise  # signal after Noise

        figure = pp.line(
            x=st.session_state['time'], y=mixed)
        figure.update_layout(width=5000, height=500,
                             template='simple_white',
                             yaxis_title='Amplitude (V)',
                             xaxis_title="Time (Sec)",
                             hovermode="x")
    else:
        figure.add_scatter(
            x=st.session_state['time'], y=st.session_state['signal_drawn'], mode='lines')


def clear_signal():
    global figure

    st.session_state['signal_drawn'] = np.zeros(len(st.session_state['time']))
    for item in st.session_state['table']:
        st.session_state['table'].remove(item)


def reconstruct(time, SampleFrequency):
    sum = 0
    for i in range(0, len(st.session_state['sampled_signal_drawn']), 1):
        sum += np.dot(st.session_state['sampled_signal_drawn'][i], np.sinc(
            (time-i*1/SampleFrequency)/(1/SampleFrequency)))
    return sum


def sampling(SampleFrequency):
    global figure

    # st.write(SampleFrequency)
    # st.write(resultFreq)

    time2 = np.linspace(0, 1, SampleFrequency)

    # if fm == True:
    #     time2 = np.linspace(0, 1, resultFreq)
    # elif fm == False:
    #     time2 = np.linspace(0, 1, SampleFrequency)

    st.session_state['sampled_signal_drawn'] = np.zeros(
        len(st.session_state['time']))
    for i in range(len(time2)):
        for item in st.session_state['table']:
            st.session_state['sampled_signal_drawn'][i] += item[0] * \
                np.sin(2*np.pi*item[1]*time2[i])
    figure.add_scatter(
        x=time2, y=st.session_state['sampled_signal_drawn'], mode='markers', name='Samples')

    # st.session_state['fig3'] = pp.line(
    #     x=st.session_state['time'], y=st.session_state['signal_drawn'])
    # st.session_state['fig3'].add_scatter(
    #     x=time2, y=st.session_state['sampled_signal_drawn'], mode='markers', name='Samples')

    interpolation = reconstruct(st.session_state['time'], SampleFrequency)
    figure.add_scatter(
        x=st.session_state['time'], y=interpolation, mode='lines', name='Recovered Signal')


file = st.sidebar.file_uploader("Upload Files", type={"csv", "txt", "xlsx"})


def change():
    del st.session_state['time']
    del st.session_state['signal_drawn']


col1, col2 = st.sidebar.columns(2)
added_magnitude = col1.slider(
    label="Signal Magnitude:", step=1, min_value=1, max_value=50)
added_frequency = col2.slider(
    label="Signal Frequency:", step=1, min_value=1, max_value=50)

add_btn = st.sidebar.button('Add')
if add_btn:
    update_signal(added_magnitude, added_frequency)
    # update_signal2(added_magnitude, added_frequency)
    st.session_state['table'].append(
        [added_magnitude, added_frequency])
    st.experimental_rerun()

col3, col4 = st.sidebar.columns(2)

SNR = col3.slider(
    label="SNR", min_value=0, step=1, max_value=50)
if SNR != 0:
    noise(SNR, True)


with st.expander("Choose sampling rate:"):
    st.session_state['freqsample'] = col4.slider(
        label="Sampling rate:", min_value=2, max_value=100, step=1)

fm = col4.checkbox("Fm")

resultFreq = st.session_state['freqsample'] * \
    (st.session_state['highest_freq'])

if fm:
    sampling(resultFreq)
else:
    sampling(st.session_state['freqsample'])


# st.write(fm)

undo_signals = st.sidebar.multiselect(
    "Remove signals", options=st.session_state['table'])

col5, col6 = st.sidebar.columns(2)


remove_btn = col5.button('Remove')
if remove_btn:

    st.session_state['highest_freq'] = 0

    for item in undo_signals:
        update_signal(-1.0*item[0], item[1])
        for item2 in st.session_state['table']:
            if item == item2:
                st.session_state['table'].remove(item2)
    st.experimental_rerun()

clear = col6.button('Clear All')
if clear:
    st.session_state['highest_freq'] = 0
    clear_signal()
    st.experimental_rerun()


if file is not None:
    File = pd.read_excel(file)
    apply_btn = st.button('Apply Uploaded signal')
    if apply_btn:
        change()

    if 'time' not in st.session_state:
        st.session_state['time'] = File[File.columns[0]].to_numpy()

    if 'original' not in st.session_state:
        st.session_state['original'] = File[File.columns[1]].to_numpy()

    if 'signal_drawn' not in st.session_state:
        st.session_state['signal_drawn'] = File[File.columns[1]].to_numpy()

# download a file as excel
output = BytesIO()
# Write files to in-memory strings using BytesIO
workbook = xlsxwriter.Workbook(output, {'in_memory': True})
worksheet = workbook.add_worksheet()
worksheet.write_column(0, 0, st.session_state['time'])
worksheet.write_column(0, 1, st.session_state['signal_drawn'])
workbook.close()
st.sidebar.download_button(
    label="Save Generated Signal",
    data=output.getvalue(),
    file_name="signal.xlsx",
    mime="application/vnd.ms-excel"
)

st.plotly_chart(figure, use_container_width=True)

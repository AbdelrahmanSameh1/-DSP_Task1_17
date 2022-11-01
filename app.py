from asyncore import write
from email.policy import default
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

button_style = """
        <style>
        .stButton > button {
            width: 90px;
            height: 35px;
        }
        </style>
        """
st.markdown(button_style, unsafe_allow_html=True)

if 'time' not in st.session_state:
    st.session_state['time'] = np.linspace(0, 1, 5000)

if 'table' not in st.session_state:
    st.session_state['table'] = []


if 'max_freq' not in st.session_state:
    st.session_state['max_freq'] = 0


if 'signal_drawn' not in st.session_state:
    st.session_state['signal_drawn'] = np.zeros(len(st.session_state['time']))
    for i in range(len(st.session_state['time'])):
        Signal = 1*np.sin(2*np.pi*1*st.session_state['time'][i])
        st.session_state['signal_drawn'][i] += Signal
    st.session_state['table'].append(
        [1, 1])


if 'sampled_signal_drawn' not in st.session_state:
    st.session_state['sampled_signal_drawn'] = []


if 'my_sampled_signal_drawn' not in st.session_state:
    st.session_state['my_sampled_signal_drawn'] = []

if 'freqsample' not in st.session_state:
    st.session_state['freqsample'] = 0

if 'table' not in st.session_state:
    st.session_state['table'] = []

if 'noise_number' not in st.session_state:
    st.session_state['noise_number'] = 1


# get the highest frequency
for item in st.session_state['table']:
    # st.write(item)
    if item[1] > st.session_state['max_freq']:
        st.session_state['max_freq'] = item[1]


figure = plotly.line()


figure.add_scatter(
    x=st.session_state['time'], y=st.session_state['signal_drawn'], mode='lines', name='Generated Signal', line=dict(color="blue"))
figure.update_layout(width=5000, height=500,
                     template='simple_white',
                     yaxis_title='Amplitude (V)',
                     xaxis_title="Time (Sec)",
                     hovermode="x")


def update_signal(amplitude, frequency):
    for i in range(len(st.session_state['time'])):
        st.session_state['signal_drawn'][i] += amplitude * \
            np.sin(2*np.pi*frequency*st.session_state['time'][i])


def noise(snr, add):
    global figure
    if add:
        SNR = 10.0**(snr/10.0)
        p1 = st.session_state['signal_drawn'].var()  # get power of signal
        n = p1/SNR  # power of noise
        noise = sc.sqrt(n)*sc.randn(len(st.session_state['signal_drawn']))
        mixed = st.session_state['signal_drawn']+noise  # signal after Noise

        figure = pp.line(
            x=st.session_state['time'], y=mixed)
        # figure.add_scatter(
        #     x=st.session_state['time'], y=mixed, mode='lines', name='Generated Signal', line=dict(color="blue"))
        figure.update_layout(width=5000, height=500,
                             template='simple_white',
                             yaxis_title='Amplitude (V)',
                             xaxis_title="Time (Sec)",
                             hovermode="x")
    else:
        figure.add_scatter(
            x=st.session_state['time'], y=st.session_state['signal_drawn'], mode='lines', name='Generated Signal')


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
        # st.write(sum)
    return sum


def sampling(SampleFrequency):
    global figure

    time2 = np.linspace(0, 1, SampleFrequency)

    st.session_state['sampled_signal_drawn'] = np.zeros(
        len(st.session_state['time']))
    for i in range(len(time2)):
        for item in st.session_state['table']:
            st.session_state['sampled_signal_drawn'][i] += item[0] * \
                np.sin(2*np.pi*item[1]*time2[i])
    figure.add_scatter(
        x=time2, y=st.session_state['sampled_signal_drawn'], mode='markers', name='Samples')

    interpolation = reconstruct(st.session_state['time'], SampleFrequency)
    figure.add_scatter(
        x=st.session_state['time'], y=interpolation, mode='lines', name='Recovered Signal')


file = st.sidebar.file_uploader("Upload Files", type={"csv", "txt", "xlsx"})


def change():

    clear_signal()
    del st.session_state['time']
    del st.session_state['signal_drawn']


up_left_col, up_right_col = st.sidebar.columns(2)
added_magnitude = up_right_col.slider(
    label="Amplitude:", step=1, min_value=1, max_value=50)
added_frequency = up_left_col.slider(
    label="Frequency:", step=1, min_value=1, max_value=50)

add_btn = st.sidebar.button('Add')
if add_btn:
    update_signal(added_magnitude, added_frequency)
    # update_signal2(added_magnitude, added_frequency)
    st.session_state['table'].append(
        [added_magnitude, added_frequency])
    st.experimental_rerun()

down_left_col, down_right_col = st.sidebar.columns(2)


Add_noise = down_right_col.checkbox("Add_Noise")

if Add_noise:
    SNR = down_right_col.slider(
        label="SNR", min_value=1, step=1, max_value=100, value=st.session_state['noise_number'])
    st.session_state['noise_number'] = SNR
    # if SNR != 0:
    noise(SNR, True)


max_freq = down_left_col.checkbox("Normalized_Freq")


with st.expander("Choose sampling frequency:"):
    st.session_state['freqsample'] = down_left_col.slider(
        label="Sampling frequency:", min_value=1, max_value=5000, step=1)


resultFreq = st.session_state['freqsample'] * \
    (st.session_state['max_freq'])

if max_freq:
    sampling(resultFreq)
else:
    sampling(st.session_state['freqsample'])


# st.write(fm)

undo_signals = st.sidebar.multiselect(
    "Remove signals", options=st.session_state['table'])

remove_col, clear_col, download_col = st.sidebar.columns(3)


remove_btn = remove_col.button('Remove')
if remove_btn:

    st.session_state['max_freq'] = 0

    for item in undo_signals:
        update_signal(-1.0*item[0], item[1])
        for item2 in st.session_state['table']:
            if item == item2:
                st.session_state['table'].remove(item2)
    st.experimental_rerun()

clear = clear_col.button('Clear All')
if clear:
    st.session_state['max_freq'] = 0
    clear_signal()
    st.experimental_rerun()


if file is not None:
    # clear_signal()
    # st.experimental_rerun()
    File = pd.read_excel(file)
    apply_btn = st.button('Apply')
    if apply_btn:
        clear_signal()
        st.session_state['freqsample'] = 0
        # st.experimental_rerun()
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
download_col.download_button(
    label="Download",
    data=output.getvalue(),
    file_name="signal.xlsx",
    mime="application/vnd.ms-excel"
)

st.plotly_chart(figure, use_container_width=True)

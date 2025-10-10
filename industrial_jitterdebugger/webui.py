# Copyright (c) 2024 Siemens AG
# This file is subject to the terms and conditions of the MIT License.
# See LICENSE file in the top-level directory.

import os
import time
import json
import requests
import yaml
import streamlit as st

STREAMLIT_STYLE = """
<style>
div[data-testid="stToolbar"] {
visibility: hidden;
height: 0%;
position: fixed;
}
div[data-testid="stDecoration"] {
visibility: hidden;
height: 0%;
position: fixed;
}
div[data-testid="stStatusWidget"] {
visibility: hidden;
height: 0%;
position: fixed;
}
#MainMenu {
visibility: hidden;
height: 0%;
}
header {
visibility: hidden;
height: 0%;
}
footer {
visibility: hidden;
height: 0%;
}
.block-container {
padding-top: 1rem;
padding-bottom: 1rem;
padding-left: 1rem;
padding-right: 1rem;
}
</style>
"""

FOOTER = """
<style>
.footer a:link , .footer a:visited{
color: grey;
background-color: transparent;
text-decoration: underline;
}

.footer a:hover,  .footer a:active {
color: green;
background-color: transparent;
}

.footer {
position: relative;
bottom: 0;
width: 100%;
background-color: transparent;
color: grey;
text-align: left;
white-space: pre;
}
</style>
<div class="footer">
<p style='font-size: 15px;'>Copyright © Siemens 2025
<a href="https://www.siemens.com/global/en/products/automation/topic-areas/industrial-edge.html" target="_blank">
Industrial Edge</a>
<a href="https://code.siemens.com/d2i-hwacc-ie/industrial-jitterdebugger" target="_blank">Source Code</a></p>
</div>
"""

JITTER_SERVICE_URL = "http://jitter:5000"
STRESS_SERVICE_URL = "http://stress:5000"


def asset_path(file_name):
    return os.path.join(os.path.dirname(__file__), "assets", file_name)


def calculate_duration(num, t_unit):
    duration_int = num
    duration_str = ""
    if t_unit == "seconds":
        duration_int = num
        duration_str = f"{num}s"
    elif t_unit == "minutes":
        duration_int = num*60
        duration_str = f"{num}m"
    elif t_unit == "hours":
        duration_int = num*3600
        duration_str = f"{num}h"
    return duration_int, duration_str


def do_test(duration):
    if os.path.isfile("/publish/jitter-results.txt"):
        os.remove("/publish/jitter-results.txt")
    if os.path.isfile("/publish/stress-results.txt"):
        os.remove("/publish/stress-results.txt")
    data = {"duration": duration}
    requests.post(f"{JITTER_SERVICE_URL}/runjitter", json=data, timeout=3)
    requests.post(f"{STRESS_SERVICE_URL}/runstress", json=data, timeout=3)


def read_json_file(path):
    with open(path, "r", encoding="utf-8") as file:
        data = file.read()
        json_data = json.loads(data)
        return json_data


def read_yaml_file(path):
    with open(path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
        json_data = json.dumps(data)
        return json_data


def click_start():
    st.session_state.disabled = not st.session_state.disabled


def is_test_running():
    return not bool(int(requests.get(f"{JITTER_SERVICE_URL}/checkstatus", timeout=3).text))


def get_test_total_time():
    result = requests.get(f"{JITTER_SERVICE_URL}/totaltime", timeout=3).text
    result = result.split(" ")[2]
    tnumber = int(result[:-1])
    tunit = result[-1]
    if tunit == "s":
        tunit = "seconds"
    elif tunit == "m":
        tunit = "minutes"
    elif tunit == "h":
        tunit = "hours"
    return tnumber, tunit


def get_test_running_time():
    result = int(requests.get(f"{JITTER_SERVICE_URL}/runningtime", timeout=3).text)
    return result


def show_test_results(header="Test Results"):
    st.subheader(header)
    if os.path.isfile("/publish/jitter-results.txt"):
        jitter_res = read_json_file("/publish/jitter-results.txt")
        l, r = st.columns(2)
        with l:
            st.image("/publish/jitter-histogram.png", caption="CPU Jitter Histogram")
        with r:
            st.image("/publish/jitter-cdf.png", caption="CPU Cumulative Distribution")
        with st.expander("See jitterdebuger results: "):
            st.json(jitter_res)
        if os.path.isfile("/publish/stress-results.txt"):
            stress_res = read_yaml_file("/publish/stress-results.txt")
            with st.expander("See stress-ng results: "):
                st.json(stress_res)
    else:
        st.write("No results found.")


def main():
    st.set_page_config(
        page_title="Industrial Jitterdebugger",
        page_icon=asset_path("favicon.ico"),
        menu_items=None,
        layout="wide"
    )
    st.markdown(STREAMLIT_STYLE, unsafe_allow_html=True)

    _, center, _ = st.columns([1, 3, 1])
    with center:
        st.image(asset_path("sie-logo-white-rgb.png"), width=150)
        st.title("Industrial Jitterdebugger")
        st.write("This Industrial Edge app can be used for validating a device's real-time behavior. "
                 "It runs two programs simultaneously:")
        st.write("- The first program measures wake-up latencies using `jitterdebugger` "
                 "(https://github.com/igaw/jitterdebugger). For that purpose, it measures the time it takes to "
                 "wake-up a thread by an expiring timer.")
        st.write("- The second program puts load on the available CPUs using `stress-ng` "
                 "(https://github.com/ColinIanKing/stress-ng). Specifically, it runs `stress-ng --cpu \"$(nproc)\" "
                 "--io 2 --vm 2 --vm-bytes 128M --fork 4 --metrics` and prints the measurements.")

        st.subheader("Run Test")
        col1, col2 = st.columns(2)
        with col1:
            number = st.number_input("Enter test duration: ", value=3, format="%d", min_value=1,
                                     placeholder="Type a number...")
        with col2:
            unit = st.selectbox("option", ("seconds", "minutes", "hours"), index=1, label_visibility="hidden")
        if "but_start" not in st.session_state:
            st.session_state.disabled = False
        start = st.button("START TEST", key="but_start", on_click=click_start, disabled=False)

        running_seconds = 0
        duration_seconds, duration_string = calculate_duration(number, unit)
        PROGRESS_TEXT = "please wait..."

        if is_test_running():
            if start:
                st.toast("Please avoid clicking on the button repeatedly, the test is already running", icon="⚠️")
            number, unit = get_test_total_time()
            duration_seconds, _ = calculate_duration(number, unit)
            running_seconds = get_test_running_time()
            st.write("The test is already running and will last for ", number, unit)
        elif start:
            do_test(duration_string)
        else:
            show_test_results(header="Results of Previous Test")
            st.markdown(FOOTER, unsafe_allow_html=True)
            st.stop()

        curr_progress = int((running_seconds/duration_seconds)*100)
        pbar = st.progress(curr_progress, text=PROGRESS_TEXT)

        while running_seconds < duration_seconds:
            time.sleep(10)
            running_seconds += 10
            if not is_test_running():
                break
            curr_progress = int((running_seconds/duration_seconds)*100)
            pbar.progress(curr_progress, text=PROGRESS_TEXT)

        if running_seconds >= duration_seconds:
            PROGRESS_TEXT = "Done!"
            curr_progress = 100
        else:
            requests.post(f"{STRESS_SERVICE_URL}/killstress", timeout=3)
            PROGRESS_TEXT = "Test dead"
        pbar.progress(curr_progress, text=PROGRESS_TEXT)
        time.sleep(3)
        show_test_results()
        st.markdown(FOOTER, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

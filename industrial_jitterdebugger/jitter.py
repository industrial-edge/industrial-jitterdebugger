# Copyright (c) 2024 Siemens AG
# This file is subject to the terms and conditions of the MIT License.
# See LICENSE file in the top-level directory.

import subprocess
from flask import Flask, request, json

app = Flask(__name__)


@app.route("/runjitter", methods=["POST"])
def runjitter():
    data = json.loads(request.data)
    duration = data['duration']
    subprocess.Popen(f"jitterdebugger -D {duration} -o /publish/ && \
                       jitterplot --output /publish/jitter-histogram.png hist /publish && \
                       jitterplot --output /publish/jitter-cdf.png cdf /publish && \
                       mv /publish/results.json /publish/jitter-results.txt", shell=True)
    return "success"


@app.route("/checkstatus", methods=["GET"])
def checkstatus():
    status, _ = subprocess.getstatusoutput("pgrep jitterdebugger")
    return str(status)


@app.route("/totaltime", methods=["GET"])
def totaltime():
    _, result = subprocess.getstatusoutput("ps -p $(pgrep jitterdebugger) -o cmd --no-header")
    return result


@app.route("/runningtime", methods=["GET"])
def runningtime():
    _, result = subprocess.getstatusoutput("ps -p $(pgrep jitterdebugger) -o etimes --no-header")
    return result


if __name__ == "__main__":
    app.run(host="0.0.0.0")

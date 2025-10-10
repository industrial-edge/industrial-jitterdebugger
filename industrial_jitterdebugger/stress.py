# Copyright (c) 2024 Siemens AG
# This file is subject to the terms and conditions of the MIT License.
# See LICENSE file in the top-level directory.

import subprocess
from flask import Flask, request, json

app = Flask(__name__)


@app.route("/runstress", methods=["POST"])
def runstress():
    data = json.loads(request.data)
    duration = data["duration"]
    subprocess.Popen(f"stress-ng --cpu \"$(nproc)\" --io 2 --vm 2 --vm-bytes 128M --fork 4 "
                     f"--metrics --timeout {duration} --timestamp --times -Y /publish/stress-results.txt",
                     shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return "success"


if __name__ == "__main__":
    app.run(host="0.0.0.0")

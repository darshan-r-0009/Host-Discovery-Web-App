from flask import Flask, request, render_template
import subprocess
import ipaddress
import threading
import platform

app = Flask(__name__)
active_hosts = []


def ping_host(ip):
    try:
        # Detect OS and set ping parameters accordingly
        system = platform.system().lower()
        if system == "windows":
            cmd = ["ping", "-n", "1", "-w", "1000", str(ip)]
        else:
            cmd = ["ping", "-c", "1", "-W", "1", str(ip)]

        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode == 0:
            active_hosts.append(str(ip))
    except Exception:
        pass


@app.route("/", methods=["GET", "POST"])
def index():
    global active_hosts
    active_hosts = []

    if request.method == "POST":
        subnet = request.form["subnet"]
        try:
            network = ipaddress.ip_network(subnet, strict=False)
            threads = []

            for ip in network.hosts():
                thread = threading.Thread(target=ping_host, args=(ip,))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            return render_template("index.html", hosts=active_hosts, subnet=subnet)
        except ValueError:
            return render_template("index.html", error="Invalid subnet!")

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
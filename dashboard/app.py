from flask import Flask, render_template, jsonify
from ci_engine.pipeline_runner import run_pipeline
from dashboard.models import init_db
import sqlite3

app = Flask(__name__)
init_db()
# -------- IBST INPUT DATA --------

from ci_engine.test_mapper import generate_test_map

TEST_MAP = generate_test_map(
    "sample_repo/tests",
    "sample_repo/src"
)


DEP_GRAPH = {
    "main.py": []
}

@app.route("/run")
def run_ci():
    print("TEST_MAP:", TEST_MAP)

    try:
        result = run_pipeline(TEST_MAP, DEP_GRAPH)

        conn = sqlite3.connect("ci.db")
        c = conn.cursor()
        c.execute(
            "INSERT INTO runs (tests_run, time_taken, cache_hit) VALUES (?, ?, ?)",
            (len(result["tests"]), float(result["time"]), int(result["cache_hit"]))
        )
        conn.commit()
        conn.close()

        return jsonify({
            "status": "success",
            "tests": result["tests"],
            "time": result["time"],
            "cache_hit": result["cache_hit"]
        })

    except Exception as e:
        print("ERROR IN /run:", e)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/runs")
def runs():
    conn = sqlite3.connect("ci.db")
    c = conn.cursor()
    c.execute(
        "SELECT id, tests_run, time_taken, cache_hit FROM runs ORDER BY id DESC"
    )
    rows = c.fetchall()
    conn.close()

    return render_template("runs.html", runs=rows)

@app.route("/baseline")
def run_baseline():
    result = run_pipeline(TEST_MAP, DEP_GRAPH, baseline=True)
    return jsonify(result)


@app.route("/")
def index():
    conn = sqlite3.connect("ci.db")
    c = conn.cursor()
    c.execute("SELECT time_taken, tests_run FROM runs")
    data = c.fetchall()

    times = [r[0] for r in data]
    tests = [r[1] for r in data]

    c.execute("SELECT AVG(time_taken), AVG(tests_run) FROM runs")
    avg_time, avg_tests = c.fetchone()
    return render_template("index.html", avg_time=avg_time, avg_tests=avg_tests, times=times, tests=tests)

if __name__ == "__main__":
    app.run(debug=True)


from flask import Flask, render_template, jsonify
import asyncio
import db_utils
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_async(coro):
    """Helper to run async db calls in Flask's sync environment."""
    return asyncio.run(coro)

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/stats')
def stats():
    try:
        # Fetch stats using the new helper in db_utils
        summary = run_async(db_utils.get_analytics_summary_db())
        return jsonify(summary)
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run on port 5888 by default
    print("Dashboard starting at http://localhost:5888")
    app.run(host='0.0.0.0', port=5888, debug=True)

from flask import Flask, request, jsonify, send_from_directory
from flask import Flask, request, jsonify, render_template, send_file
import psycopg2

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="virtual_toor",
        user="postgres",
        password="06092003",
        port=5433
    )
    return conn

# Route to update hotspot
@app.route("/update_hotspot", methods=["POST"])
def update_hotspot():
    data = request.json
    scene_id = data.get("scene_id")
    title_filter = data.get("title")       # existing title to filter
    new_title = data.get("new_title")      # new title to update

    if not scene_id:
        return jsonify({"error": "scene_id is required"}), 400

    fields = {}
    for key in ["yaw", "pitch", "text"]:
        if key in data:
            fields[key] = data[key]
    if new_title:
        fields["title"] = new_title

    if not fields:
        return jsonify({"error": "No fields to update"}), 400

    set_clause = ", ".join([f"{k} = %s" for k in fields.keys()])
    values = list(fields.values())

    where_clause = "scene_id = %s"
    values.append(scene_id)
    if title_filter:
        where_clause += " AND title = %s"
        values.append(title_filter)

    sql = f"UPDATE info_hotspots SET {set_clause} WHERE {where_clause} RETURNING *;"

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(sql, values)
    updated_rows = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()

    if updated_rows:
        return jsonify({"message": "Updated successfully", "rows": updated_rows})
    else:
        return jsonify({"message": "No rows matched"}), 404


# Route to get all scene IDs for dropdown
@app.route("/scene_ids", methods=["GET"])
def get_scene_ids():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT scene_id FROM info_hotspots ORDER BY scene_id;")
    scene_ids = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(scene_ids)


# ✅ Route to get all titles for a given scene_id
@app.route("/titles/<scene_id>", methods=["GET"])
def get_titles(scene_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT title FROM info_hotspots WHERE scene_id = %s ORDER BY title;", (scene_id,))
    titles = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(titles)


# Serve frontend
@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4000)

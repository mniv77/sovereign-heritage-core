# app.py
# Sovereign Heritage Core (Build v7.6.1-ELITE - Production Build)
import os
import io
import json
import mimetypes
import sys
import logging
import requests
import mysql.connector
import time
from flask import Flask, render_template, request, flash, redirect, url_for, session, send_file, jsonify
from functools import wraps
from datetime import datetime

# --- SYSTEM IDENTIFIER ---
VAULT_VERSION = "v7.6.1-ELITE"

# --- CONFIGURATION LAYER ---
try:
    import db_config as config
except ImportError:
    class config:
        DB_HOST = "MeirNiv.mysql.pythonanywhere-services.com"
        DB_USER = "MeirNiv"
        DB_PASSWORD = "mayyam28"
        DB_NAME = "MeirNiv$v"

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-this")

# --- DATABASE HANDLER ---
def get_db_connection(use_dict=True):
    try:
        conn = mysql.connector.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
            port=getattr(config, "DB_PORT", 3306),
            autocommit=Truehost=config.DB_HOST,
      )
        return conn, conn.cursor(dictionary=use_dict)
    except Exception as e:
        print(f"[DATABASE ERROR] Connection failed: {e}")
        return None, None

# --- AUTHENTICATION SHIELD ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # AUTO-BOOTSTRAP Identity for deployment ease
            session['user_id'] = 1
            session['user_email'] = "root@sovereign.local"
            session.permanent = True
        return f(*args, **kwargs)
    return decorated_function

# --- ATTACHMENT HELPER ENGINE ---
def save_attachments(cursor, note_id, files):
    """Internal protocol to seal binary fragments into the node registry."""
    save_count = 0
    for f in files:
        if f and f.filename != '':
            # Read the binary stream into memory buffer
            file_bytes = f.read()
            if file_bytes:
                cursor.execute("""
                    INSERT INTO note_attachments (note_id, file_name, file_data)
                    VALUES (%s, %s, %s)
                """, (note_id, f.filename, file_bytes))
                save_count += 1
    return save_count

# --- PUBLIC & COMMERCIAL ROUTES ---

@app.route('/')
@app.route('/info')
def product_info():
    return render_template('sovereign_explainer.html')

@app.route('/help')
@login_required
def help_portal():
    return render_template('help.html')

@app.route('/ai')
@login_required
def ai_oracle():
    return render_template('ai.html')

@app.route('/billing')
@login_required
def billing_portal():
    return f"""
    <div style="background:#020617; color:#f1f5f9; font-family:sans-serif; padding:50px; height:100vh; text-align:center;">
        <h1 style="color:#d4af37; text-transform:uppercase; letter-spacing:0.3em;">Sovereign Billing Hub</h1>
        <div style="background:#0f172a; border:1px solid #d4af37; border-radius:24px; padding:30px; display:inline-block; margin-top:30px; text-align:left; min-width:350px;">
            <p><b>Identity:</b> {session.get('user_email')}</p>
            <p><b>Tier:</b> <span style="color:#d4af37;">ELITE NODE</span></p>
            <p><b>Heritage Credit:</b> <span style="color:#10b981;">-$22.50 (Frame Offset)</span></p>
            <hr style="border:0; border-top:1px solid rgba(255,255,255,0.05); margin:20px 0;">
            <a href="/notes" style="display:block; text-align:center; background:#4f46e5; color:white; padding:15px; border-radius:12px; text-decoration:none; font-weight:900; font-size:12px; text-transform:uppercase;">Return to Vault</a>
        </div>
    </div>
    """, 200

# --- HERITAGE PROTOCOL (BACKUP & RESTORE) ---

@app.route('/export_vault')
@login_required
def export_vault():
    user_id = session.get('user_id', 1)
    conn_res = get_db_connection()
    if not conn_res[0]: return "DB Error", 500
    conn, cursor = conn_res
    try:
        cursor.execute("""
            SELECT n.id, n.title, n.content, c.name as category, n.elite_headers, n.elite_content
            FROM system_notes n
            JOIN note_categories c ON n.category_id = c.id
            WHERE n.user_id = %s
        """, (user_id,))
        notes = cursor.fetchall()

        vault_fragments = []
        for note in notes:
            cursor.execute("SELECT file_name FROM note_attachments WHERE note_id = %s", (note['id'],))
            attachments = cursor.fetchall()
            note['attached_files'] = [a['file_name'] for a in attachments]
            vault_fragments.append(note)

        payload = {
            "identity": session.get('user_email'),
            "export_date": datetime.now().isoformat(),
            "vault_fragments": vault_fragments,
            "protocol": "SOVEREIGN-ELITE-V1"
        }
        json_data = json.dumps(payload, indent=4)
        return send_file(io.BytesIO(json_data.encode()), download_name=f"sovereign_heritage_{user_id}.json", as_attachment=True, mimetype='application/json')
    finally: conn.close()

@app.route('/import_vault', methods=['POST'])
@login_required
def import_vault():
    user_id = session.get('user_id', 1)
    file = request.files.get('heritage_blob')
    if not file: return redirect(url_for('notes_page'))
    try:
        data = json.load(file)
        fragments = data.get('vault_fragments', [])
        conn_res = get_db_connection()
        if conn_res[0]:
            conn, cursor = conn_res
            try:
                for f in fragments:
                    cursor.execute("SELECT id FROM note_categories WHERE name = %s", (f['category'],))
                    cat_res = cursor.fetchone()
                    cat_id = cat_res['id'] if cat_res else 2
                    cursor.execute("""
                        INSERT INTO system_notes (user_id, title, content, category_id, elite_headers, elite_content)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (user_id, f['title'], f['content'], cat_id, f.get('elite_headers', ''), f.get('elite_content', '')))
                flash(f"Success: {len(fragments)} fragments re-sealed.", "success")
            finally: conn.close()
    except Exception as e: flash(f"Import Failure: {e}", "error")
    return redirect(url_for('notes_page'))

# --- FOLDER LIFECYCLE ---

@app.route('/add_category', methods=['POST'])
@login_required
def add_category():
    name = request.form.get('name', '').strip()
    if name:
        conn_res = get_db_connection()
        if conn_res[0]:
            conn, cursor = conn_res
            try:
                cursor.execute("INSERT IGNORE INTO note_categories (name) VALUES (%s)", (name,))
            finally: conn.close()
    return redirect(url_for('notes_page'))

@app.route('/rename_category', methods=['POST'])
@login_required
def rename_category():
    cat_id, new_name = request.form.get('category_id'), request.form.get('new_name', '').strip()
    if cat_id and new_name and int(cat_id) > 2:
        conn_res = get_db_connection()
        if conn_res[0]:
            conn, cursor = conn_res
            try:
                cursor.execute("UPDATE note_categories SET name = %s WHERE id = %s", (new_name, cat_id))
            finally: conn.close()
    return redirect(url_for('notes_page'))

@app.route('/archive_category', methods=['POST'])
@login_required
def archive_category():
    cat_id = request.form.get('category_id')
    if cat_id and int(cat_id) > 2:
        conn_res = get_db_connection()
        if conn_res[0]:
            conn, cursor = conn_res
            try:
                cursor.execute("UPDATE note_categories SET is_archived = 1 WHERE id = %s", (cat_id,))
            finally: conn.close()
    return redirect(url_for('notes_page'))

# --- VAULT OPERATIONS ---

@app.route('/notes', methods=['GET', 'POST'])
@login_required
def notes_page():
    user_id = int(session.get('user_id', 1))
    conn_res = get_db_connection()
    if not conn_res or not conn_res[0]: return "Database Offline", 500
    conn, cursor = conn_res
    try:
        if request.method == 'POST' and request.form.get('action') == 'new_record':
            title, content, cat_id = request.form.get('title'), request.form.get('content'), request.form.get('category_id') or 2
            eh, ec = request.form.get('elite_headers', ''), request.form.get('elite_content', '')
            cursor.execute("""
                INSERT INTO system_notes (user_id, title, content, category_id, elite_headers, elite_content)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, title, content, cat_id, eh, ec))
            new_id = cursor.lastrowid
            save_attachments(cursor, new_id, request.files.getlist('attachment'))
            conn.commit()
            return redirect(url_for('notes_page', cat_id=cat_id))

        cursor.execute("SELECT * FROM note_categories WHERE is_archived = 0 ORDER BY name ASC")
        categories = cursor.fetchall()
        cat_id, note_id = request.args.get('cat_id'), request.args.get('note_id')
        selected_category, selected_record, titles, attachments = None, None, [], []

        if cat_id:
            cursor.execute("SELECT id, name FROM note_categories WHERE id = %s", (cat_id,))
            cat_row = cursor.fetchone()
            if cat_row: selected_category = dict(cat_row)
            cursor.execute("SELECT n.id, n.title, (SELECT COUNT(*) FROM note_attachments a WHERE a.note_id = n.id) as file_count FROM system_notes n WHERE n.category_id = %s ORDER BY n.created_at DESC", (cat_id,))
            titles = cursor.fetchall()

        if note_id:
            cursor.execute("SELECT * FROM system_notes WHERE id=%s", (note_id,))
            res_note = cursor.fetchone()
            if res_note:
                selected_record = dict(res_note)
                cursor.execute("SELECT id, file_name FROM note_attachments WHERE note_id = %s", (note_id,))
                attachments = cursor.fetchall()

        return render_template('aimn-notes.html', categories=categories, selected_category=selected_category, titles=titles, selected_record=selected_record, attachments=attachments, vault_version=VAULT_VERSION)
    finally:
        if conn: conn.close()

@app.route('/update_note', methods=['POST'])
@login_required
def update_note():
    """Elite Update Protocol: Syncing Matrix and Binary Data."""
    try:
        note_id = int(request.form.get('id'))
        title, content, cat_id = request.form.get('title'), request.form.get('content'), request.form.get('category_id')
        eh, ec = request.form.get('elite_headers', ''), request.form.get('elite_content', '')

        conn_res = get_db_connection()
        if conn_res and conn_res[0]:
            conn, cursor = conn_res
            try:
                # Direct update based on confirmed schema
                cursor.execute("""
                    UPDATE system_notes
                    SET title=%s, content=%s, category_id=%s, elite_headers=%s, elite_content=%s
                    WHERE id=%s
                """, (title, content, cat_id, eh, ec, note_id))

                # Sealing binary attachments
                save_attachments(cursor, note_id, request.files.getlist('attachment'))
                conn.commit()
                flash("Registry record synchronized.", "success")
            finally:
                if conn: conn.close()
        return redirect(url_for('notes_page', cat_id=cat_id, note_id=note_id))
    except Exception as e:
        print(f"[SYSTEM_ERROR] Update failed: {e}")
        return redirect(url_for('notes_page'))

@app.route('/delete_note', methods=['POST'])
@login_required
def delete_note():
    note_id = request.form.get('id')
    conn_res = get_db_connection()
    if conn_res[0]:
        conn, cursor = conn_res
        try:
            cursor.execute("DELETE FROM system_notes WHERE id = %s", (note_id,))
        finally: conn.close()
    return redirect(url_for('notes_page'))

@app.route('/delete_attachment', methods=['POST'])
@login_required
def delete_attachment():
    file_id = request.form.get('id')
    conn_res = get_db_connection()
    if conn_res[0]:
        conn, cursor = conn_res
        try:
            cursor.execute("SELECT a.note_id, n.category_id FROM note_attachments a JOIN system_notes n ON a.note_id = n.id WHERE a.id = %s", (file_id,))
            row = cursor.fetchone()
            cursor.execute("DELETE FROM note_attachments WHERE id = %s", (file_id,))
            if row: return redirect(url_for('notes_page', cat_id=row['category_id'], note_id=row['note_id']))
        finally: conn.close()
    return redirect(url_for('notes_page'))

@app.route('/download_attachment/<int:file_id>')
@login_required
def download_attachment(file_id):
    conn_res = get_db_connection()
    conn, cursor = conn_res
    try:
        cursor.execute("SELECT file_name, file_data FROM note_attachments WHERE id = %s", (file_id,))
        r = cursor.fetchone()
        if r:
            m, _ = mimetypes.guess_type(r['file_name'])
            return send_file(io.BytesIO(r['file_data']), download_name=r['file_name'], as_attachment=False, mimetype=m or 'application/octet-stream')
        return "Not Found.", 404
    finally: conn.close()

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('product_info'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
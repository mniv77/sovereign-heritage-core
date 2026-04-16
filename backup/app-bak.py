# app.py - Sovereign Heritage Core (Build v7.1.7-ULTRA - Route Handshake Fix)
import os
import io
import json
import mimetypes
import uuid
import sys
import logging
import traceback
import requests
import mysql.connector
import time
from flask import Flask, render_template, request, flash, redirect, url_for, session, make_response, send_file, jsonify
from functools import wraps

# --- SYSTEM IDENTIFIER ---
VAULT_VERSION = "v7.1.7-ULTRA"

# --- CONFIGURATION LAYER ---
try:
    import db_config as config
except ImportError:
    class config:
        DB_HOST = os.environ.get("DB_HOST", "localhost")
        DB_USER = os.environ.get("DB_USER", "root")
        DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
        DB_NAME = os.environ.get("DB_NAME", "aimn_sovereign")

app = Flask(__name__)
app.secret_key = "sovereign_trust_protocol_v7.1_2024"

# Gemini API Configuration
GEMINI_API_KEY = "" 
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={GEMINI_API_KEY}"

# Logging configuration
logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)

def log_debug(msg):
    formatted_msg = f"[SOVEREIGN_DEBUG] {msg}\n"
    app.logger.error(formatted_msg.strip())

# --- DATABASE HANDLER ---
def get_db_connection(use_dict=True):
    try:
        conn = mysql.connector.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
            autocommit=True 
        )
        return conn, conn.cursor(dictionary=use_dict)
    except Exception as e:
        log_debug(f"DATABASE CONNECTION FAILURE: {e}")
        return None, None

# --- AUTHENTICATION SHIELD ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            session['user_id'] = 1
            session['user_email'] = "root@sovereign.local"
            session.permanent = True
        return f(*args, **kwargs)
    return decorated_function

# --- PUBLIC ROUTES ---

@app.route('/')
@app.route('/info')
def product_info():
    """The Sovereign Explainer."""
    return render_template('sovereign_explainer.html')

@app.route('/billing')
@login_required
def billing_portal():
    return "Billing Portal - Identity Restricted. Please contact Sovereign Concierge.", 200

# --- CATEGORY MANAGEMENT (FIXING THE 404 ERRORS) ---

@app.route('/add_category', methods=['POST'])
@login_required
def add_category():
    """Initializes a new folder in the registry."""
    user_id = session.get('user_id', 1)
    new_name = request.form.get('name', '').strip()
    if not new_name:
        flash("Category name cannot be empty.", "error")
        return redirect(url_for('notes_page'))
    
    conn_res = get_db_connection()
    if conn_res[0]:
        conn, cursor = conn_res
        try:
            cursor.execute("INSERT IGNORE INTO note_categories (name) VALUES (%s)", (new_name,))
            flash(f"Folder '{new_name}' initialized.", "success")
        finally: conn.close()
    return redirect(url_for('notes_page'))

@app.route('/rename_category', methods=['POST'])
@login_required
def rename_category():
    cat_id = request.form.get('id')
    new_name = request.form.get('name', '').strip()
    if cat_id and new_name:
        conn_res = get_db_connection()
        if conn_res[0]:
            conn, cursor = conn_res
            try:
                cursor.execute("UPDATE note_categories SET name = %s WHERE id = %s", (new_name, cat_id))
                flash("Folder identifier updated.", "success")
            finally: conn.close()
    return redirect(url_for('notes_page'))

@app.route('/archive_category', methods=['POST'])
@login_required
def archive_category():
    cat_id = request.form.get('id')
    if cat_id:
        conn_res = get_db_connection()
        if conn_res[0]:
            conn, cursor = conn_res
            try:
                # Heritage Protocol: Archive hides the folder (is_archived logic)
                cursor.execute("UPDATE note_categories SET is_archived = 1 WHERE id = %s", (cat_id,))
                flash("Folder moved to archive.", "success")
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
        if request.method == 'POST':
            # Logic for new records from the main dashboard
            if request.form.get('action') == 'new_record':
                title, content, cat_id = request.form.get('title'), request.form.get('content'), request.form.get('category_id') or 2
                cursor.execute("INSERT INTO system_notes (user_id, title, content, category_id) VALUES (%s, %s, %s, %s)", 
                               (user_id, title, content, cat_id))
                new_id = cursor.lastrowid
                
                attachments = request.files.getlist('attachment')
                for f in attachments:
                    if f and f.filename != '':
                        cursor.execute("INSERT INTO note_attachments (note_id, file_name, file_data) VALUES (%s, %s, %s)", 
                                       (new_id, f.filename, f.read()))
                
                flash("Record sealed in the vault.", "success")
                return redirect(url_for('notes_page', cat_id=cat_id))

        # Fetch active categories (not archived)
        cursor.execute("SELECT * FROM note_categories WHERE is_archived = 0 ORDER BY name ASC")
        categories = cursor.fetchall()
        
        cat_id, note_id = request.args.get('cat_id'), request.args.get('note_id')
        selected_category, selected_record, titles, attachments = None, None, [], []

        if cat_id:
            cursor.execute("SELECT id, name FROM note_categories WHERE id = %s", (cat_id,))
            cat_row = cursor.fetchone()
            if cat_row: selected_category = dict(cat_row)
            
            sql_titles = """
                SELECT n.id AS note_id, n.title AS note_title, 
                       (SELECT COUNT(*) FROM note_attachments a WHERE a.note_id = n.id) AS note_file_count 
                FROM system_notes n WHERE n.category_id = %s ORDER BY n.created_at DESC
            """
            cursor.execute(sql_titles, (cat_id,))
            raw_titles = cursor.fetchall()
            for t in raw_titles:
                row_dict = dict(t)
                titles.append({
                    'id': row_dict.get('note_id'),
                    'title': (row_dict.get('note_title') or 'Untitled').strip(),
                    'file_count': int(row_dict.get('note_file_count') or 0)
                })

        if note_id:
            cursor.execute("SELECT * FROM system_notes WHERE id=%s", (note_id,))
            res_note = cursor.fetchone()
            if res_note:
                selected_record = dict(res_note)
                cursor.execute("SELECT id, file_name FROM note_attachments WHERE note_id = %s", (note_id,))
                attachments = [dict(a) for a in cursor.fetchall()]

        return render_template('aimn-notes.html', 
                             categories=categories, selected_category=selected_category, 
                             titles=titles, selected_record=selected_record, 
                             attachments=attachments, vault_version=VAULT_VERSION)
    finally:
        if conn: conn.close()

@app.route('/update_note', methods=['POST'])
@login_required
def update_note():
    note_id = request.form.get('id')
    title, content, cat_id = request.form.get('title'), request.form.get('content'), request.form.get('category_id')
    conn_res = get_db_connection()
    if conn_res and conn_res[0]:
        conn, cursor = conn_res
        try:
            cursor.execute("UPDATE system_notes SET title=%s, content=%s, category_id=%s WHERE id=%s", (title, content, cat_id, note_id))
            new_attachments = request.files.getlist('attachment')
            for f in new_attachments:
                if f and f.filename != '':
                    cursor.execute("INSERT INTO note_attachments (note_id, file_name, file_data) VALUES (%s, %s, %s)", 
                                   (note_id, f.filename, f.read()))
            flash("Vault record synchronized.", "success")
        finally: conn.close()
    return redirect(url_for('notes_page', cat_id=cat_id, note_id=note_id))

@app.route('/delete_note', methods=['POST'])
@login_required
def delete_note():
    note_id = request.form.get('id')
    conn_res = get_db_connection()
    if conn_res[0]:
        conn, cursor = conn_res
        try:
            cursor.execute("DELETE FROM system_notes WHERE id = %s", (note_id,))
            flash("Record purged.", "success")
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
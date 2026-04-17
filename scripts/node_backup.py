# node_backup.py
# Sovereign Heritage Core - Data Preservation Utility
# Logic: Global SQL Dumps and Individual User Exports

import os
import json
import mysql.connector
from datetime import datetime
import db_config as config

class SovereignBackupManager:
    def __init__(self):
        self.db_params = {
            "host": config.DB_HOST,
            "user": config.DB_USER,
            "password": config.DB_PASSWORD,
            "database": config.DB_NAME
        }

    def global_system_dump(self):
        """Generates a timestamped SQL dump of the entire database."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sovereign_global_backup_{timestamp}.sql"
        
        print(f"--- INITIATING GLOBAL BACKUP: {timestamp} ---")
        # On PythonAnywhere/Linux, we utilize the mysqldump utility
        cmd = f"mysqldump -h {config.DB_HOST} -u {config.DB_USER} -p'{config.DB_PASSWORD}' {config.DB_NAME} > {filename}"
        
        try:
            os.system(cmd)
            print(f"✅ SUCCESS: System state sealed in {filename}")
        except Exception as e:
            print(f"❌ FAILED: Backup error: {e}")

    def individual_user_export(self, user_id):
        """
        Exports all records for a specific user into a JSON 'Heritage Blob'.
        This data remains AES-256 encrypted at the record level.
        """
        try:
            conn = mysql.connector.connect(**self.db_params)
            cursor = conn.cursor(dictionary=True)
            
            # Fetch all user notes and attachments
            sql = """
                SELECT n.title, n.content, n.file_path, c.name as category
                FROM system_notes n
                JOIN note_categories c ON n.category_id = c.id
                WHERE n.user_id = %s
            """
            cursor.execute(sql, (user_id,))
            records = cursor.fetchall()
            
            export_payload = {
                "export_date": datetime.now().isoformat(),
                "identity_id": user_id,
                "vault_fragments": records
            }
            
            filename = f"user_{user_id}_heritage_export.json"
            with open(filename, 'w') as f:
                json.dump(export_payload, f, indent=4)
                
            print(f"✅ User Export Complete: {filename}")
            return filename

        except Exception as e:
            print(f"❌ Export Error: {e}")
        finally:
            if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    manager = SovereignBackupManager()
    
    print("1. Run Global System Backup")
    print("2. Run Individual User Export")
    choice = input("Select Protocol (1 or 2): ")
    
    if choice == "1":
        manager.global_system_dump()
    elif choice == "2":
        uid = input("Enter User ID to export: ")
        manager.individual_user_export(uid)
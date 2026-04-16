# vault_debug.py
# Use this tool from the Bash console to manage identities when locked out.
import mysql.connector
from werkzeug.security import generate_password_hash
import db_config as config

def run_diagnostics():
    print("\n" + "="*60)
    print("--- SOVEREIGN IDENTITY DIAGNOSTICS & RE-KEYING ---")
    print("="*60)
    
    try:
        conn = mysql.connector.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME
        )
        cursor = conn.cursor(dictionary=True)

        # 1. LIST IDENTITIES WITH FULL METADATA
        print("\n[Step 1] Current Registered Identities:")
        cursor.execute("SELECT id, email, trusted_device_id, security_question, security_answer, subscription_status FROM users")
        users = cursor.fetchall()
        
        if not users:
            print("(!) No users found in the registry.")
            return

        for u in users:
            status = "LOCKED" if u['trusted_device_id'] else "OPEN (Bootstrap Mode)"
            print(f" ID: {u['id']} | Email: [{u['email']}] | Tier: {u['subscription_status']}")
            print(f"      Challenge: {u['security_question']} -> Answer: {u['security_answer']}")
            print(f"      Hardware: {status}")
            print("-" * 40)

        # 2. SELECTION
        print("\n[Step 2] Identity Selection")
        target_email = input("Enter the EXACT email to manage (or press Enter to cancel): ").strip()
        if not target_email: 
            print("Operation cancelled.")
            return

        # Check if user exists
        cursor.execute("SELECT id, subscription_status FROM users WHERE email = %s", (target_email,))
        user_check = cursor.fetchone()
        if not user_check:
            print(f"\n❌ ERROR: Email [{target_email}] not found in database.")
            return

        # 3. ACTION MENU
        print(f"\n[Step 3] Management Actions for {target_email}")
        print("1. Re-Key (Reset Password & Device Lock)")
        print("2. Modify Commercial Tier (Upgrade/Downgrade)")
        choice = input("Select Action (1 or 2): ").strip()

        if choice == "1":
            # --- RESET LOGIC ---
            new_pw = input(f"Enter NEW password for {target_email}: ").strip()
            if not new_pw:
                print("❌ ERROR: Password cannot be empty.")
                return

            confirm_pw = input("Confirm NEW password: ").strip()
            if new_pw != confirm_pw:
                print("❌ ERROR: Passwords do not match.")
                return

            new_answer = input("Enter NEW Security Answer (or Enter to keep current): ").strip()

            print("\nApplying protocol...")
            new_hash = generate_password_hash(new_pw)
            
            if new_answer:
                sql = "UPDATE users SET password_hash = %s, security_answer = %s, trusted_device_id = NULL WHERE email = %s"
                cursor.execute(sql, (new_hash, new_answer, target_email))
            else:
                sql = "UPDATE users SET password_hash = %s, trusted_device_id = NULL WHERE email = %s"
                cursor.execute(sql, (new_hash, target_email))
            
            conn.commit()
            print(f"\n✅ SUCCESS: {target_email} identity re-keyed.")

        elif choice == "2":
            # --- COMMERCIAL TIER LOGIC ---
            print(f"Current Tier: {user_check['subscription_status']}")
            print("Tiers: FREE, PRO, ELITE")
            new_tier = input("Enter new tier name: ").strip().upper()
            
            if new_tier in ['FREE', 'PRO', 'ELITE']:
                cursor.execute("UPDATE users SET subscription_status = %s WHERE email = %s", (new_tier, target_email))
                conn.commit()
                print(f"\n✅ SUCCESS: {target_email} promoted to {new_tier} status.")
            else:
                print("❌ ERROR: Invalid Tier Name.")

        # 4. FINAL VERIFICATION
        print("\nNext Steps:")
        print("1. Reload your Web App in PythonAnywhere.")
        print("2. Test the updated parameters in the UI.")

    except Exception as e:
        print(f"\n❌ CRITICAL SYSTEM ERROR: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()
            print("\n" + "="*60)

if __name__ == "__main__":
    run_diagnostics()
import time
from backend.app.core.database import db
from backend.app.core.security import hash_password, verify_password
from backend.app.services.email_service import send_password_reset_email

def run_tests():
    print("--- 1. Testing Database Schema & Methods ---")
    with db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='password_resets'")
        table = cursor.fetchone()
        assert table is not None, "password_resets table does not exist!"
        print("[PASS] password_resets table exists in SQLite database")

    # Clean test entries
    with db._get_connection() as conn:
        conn.cursor().execute("DELETE FROM password_resets WHERE email = 'test_operator@finsecure.io'")
        conn.commit()

    # Create password reset
    rec = db.create_password_reset(
        email='test_operator@finsecure.io',
        token='test_token_abc_xyz_789',
        code='789123',
        expires_at=time.time() + 900,
        ip_address='192.168.1.100',
        user_agent='Mobile / iOS'
    )
    assert rec['id'] is not None
    assert rec['code'] == '789123'
    print("[PASS] db.create_password_reset succeeded")

    # Fetch by code
    found_by_code = db.get_password_reset('789123', 'test_operator@finsecure.io')
    assert found_by_code is not None
    assert found_by_code['token'] == 'test_token_abc_xyz_789'
    print("[PASS] db.get_password_reset by 6-digit code succeeded")

    # Fetch by token
    found_by_token = db.get_password_reset('test_token_abc_xyz_789')
    assert found_by_token is not None
    assert found_by_token['code'] == '789123'
    print("[PASS] db.get_password_reset by token succeeded")

    # Mark used
    db.mark_password_reset_used(rec['id'])
    assert db.get_password_reset('789123') is None
    print("[PASS] db.mark_password_reset_used invalidates subsequent lookups")

    print("\n--- 2. Testing Email Dispatch Service ---")
    dispatch = send_password_reset_email(
        to_email='admin@finsecure.io',
        user_name='Alex Rivera',
        reset_token='token_sec_ops_4488',
        reset_code='482910',
        base_url='http://127.0.0.1:8000',
        client_ip='127.0.0.1',
        user_agent='Chrome / Windows'
    )
    assert dispatch['delivered'] is True
    assert '482910' in dispatch['reset_code']
    assert 'token=token_sec_ops_4488' in dispatch['reset_link']
    assert '#reset' in dispatch['reset_link']
    print(f"[PASS] email_service returned delivery status: {dispatch.get('method')} ({dispatch.get('message')})")
    print(f"       Reset Link: {dispatch.get('reset_link')}")

    print("\n--- 3. Testing User Password Update & Verification ---")
    test_pwd = "UpdatedSecureKey2026!"
    new_h = hash_password(test_pwd)
    upd = db.update_user_password_by_email('admin@finsecure.io', new_h)
    assert upd is True
    user = db.get_user_by_email('admin@finsecure.io')
    assert user is not None, "User admin@finsecure.io was not found in SQLite"
    assert verify_password(user['password_hash'], test_pwd) is True
    print("[PASS] Password hash updated in SQLite and verified with verify_password()")

    # Restore default password
    default_h = hash_password("admin2026")
    db.update_user_password_by_email('admin@finsecure.io', default_h)
    restored_u = db.get_user_by_email('admin@finsecure.io')
    assert restored_u is not None, "User admin@finsecure.io was not found in SQLite"
    assert verify_password(restored_u['password_hash'], "admin2026") is True
    print("[PASS] Default password restored to admin2026")

    print("\n==========================================")
    print("ALL UNIT & INTEGRATION TESTS PASSED 100%!")
    print("==========================================")

if __name__ == '__main__':
    run_tests()


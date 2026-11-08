from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import db
from backend.app.core.security import hash_password

client = TestClient(app)

def test_api_forgot_password_flow():
    print("Testing Full API Password Recovery Flow...")

    # 1. Test forgot-password endpoint with invalid email
    res_bad = client.post("/api/v1/auth/forgot-password", json={"email": "nonexistent_operator_999@finsecure.io"})
    assert res_bad.status_code == 404
    print("[PASS] 404 returned for non-existent email")

    # 2. Test forgot-password endpoint with valid email
    res = client.post("/api/v1/auth/forgot-password", json={"email": "admin@finsecure.io"})
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["status"] == "success"
    assert "admin@finsecure.io" in data["email"]
    assert "reset_code" in data
    assert "reset_link" in data
    otp_code = data["reset_code"]
    print(f"[PASS] /api/v1/auth/forgot-password returned success with OTP: {otp_code}")

    # 3. Test verify-reset-token with the OTP code
    res_verify = client.post("/api/v1/auth/verify-reset-token", json={
        "code": otp_code,
        "email": "admin@finsecure.io"
    })
    assert res_verify.status_code == 200, res_verify.text
    v_data = res_verify.json()
    assert v_data["status"] == "valid"
    assert v_data["email"] == "admin@finsecure.io"
    print("[PASS] /api/v1/auth/verify-reset-token confirmed OTP is valid and active")

    # 4. Test reset-password endpoint
    temp_pass = "TestResetKey2026!"
    res_reset = client.post("/api/v1/auth/reset-password", json={
        "email": "admin@finsecure.io",
        "code": otp_code,
        "new_password": temp_pass
    })
    assert res_reset.status_code == 200, res_reset.text
    r_data = res_reset.json()
    assert r_data["status"] == "success"
    assert "token" in r_data
    print("[PASS] /api/v1/auth/reset-password updated password and returned auth token")

    # 5. Verify the code cannot be used a second time
    res_reuse = client.post("/api/v1/auth/reset-password", json={
        "email": "admin@finsecure.io",
        "code": otp_code,
        "new_password": "ShouldNotWork123!"
    })
    assert res_reuse.status_code == 400
    print("[PASS] Re-using consumed OTP code rejected with 400 Bad Request")

    # 6. Verify logging in with the new password
    res_login = client.post("/api/v1/auth/login", json={
        "username": "admin@finsecure.io",
        "password": temp_pass
    })
    assert res_login.status_code == 200
    print("[PASS] Successfully authenticated with newly reset security passkey")

    # 7. Restore original password
    db.update_user_password_by_email("admin@finsecure.io", hash_password("admin2026"))
    res_orig = client.post("/api/v1/auth/login", json={
        "username": "admin@finsecure.io",
        "password": "admin2026"
    })
    assert res_orig.status_code == 200
    print("[PASS] Original passkey (admin2026) verified and restored")

    # 8. Verify Level 4 audit logs recorded the password recovery events
    res_audit = client.get("/api/v1/auth/audit-logs?limit=10")
    assert res_audit.status_code == 200
    audit_logs = res_audit.json().get("audit_logs", [])
    actions = [a["action"] for a in audit_logs]
    assert "PASSWORD_RESET_REQUESTED" in actions
    assert "PASSWORD_RESET_SUCCESS" in actions
    print("[PASS] Level 4 Full Authority audit log contains PASSWORD_RESET_REQUESTED and PASSWORD_RESET_SUCCESS")

    print("\n=======================================================")
    print("ALL HTTP API LIFECYCLE TESTS COMPLETED SUCCESSFULLY!")
    print("=======================================================")

if __name__ == "__main__":
    test_api_forgot_password_flow()


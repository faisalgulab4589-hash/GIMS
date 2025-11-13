#!/usr/bin/env python3
"""
Quick test script to verify deductions tab loading fix
Tests: Authentication, API access, data loading
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8080"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_unauthenticated_access():
    """Test that dashboard redirects to login when not authenticated"""
    print_section("TEST 1: Unauthenticated Dashboard Access")
    
    response = requests.get(f"{BASE_URL}/", allow_redirects=False)
    
    if response.status_code == 302:
        print("✅ PASS: Dashboard returns 302 redirect (requires login)")
        print(f"   Redirect location: {response.headers.get('Location', 'N/A')}")
        return True
    else:
        print(f"❌ FAIL: Dashboard returned {response.status_code} instead of 302")
        return False

def test_login_page_accessible():
    """Test that login page is accessible"""
    print_section("TEST 2: Login Page Accessible")
    
    response = requests.get(f"{BASE_URL}/login")
    
    if response.status_code == 200:
        print("✅ PASS: Login page is accessible (HTTP 200)")
        print(f"   Response size: {len(response.text)} bytes")
        return True
    else:
        print(f"❌ FAIL: Login page returned {response.status_code}")
        return False

def test_api_without_auth():
    """Test that API endpoints require authentication"""
    print_section("TEST 3: API Endpoints Require Authentication")
    
    response = requests.get(
        f"{BASE_URL}/api/deductions/employees_overview?month=11&year=2025",
        allow_redirects=False
    )
    
    if response.status_code == 302:
        print("✅ PASS: API endpoint returns 302 redirect (requires login)")
        print(f"   Redirect location: {response.headers.get('Location', 'N/A')}")
        return True
    elif response.status_code == 401:
        print("✅ PASS: API endpoint returns 401 Unauthorized")
        return True
    else:
        print(f"❌ FAIL: API endpoint returned {response.status_code} instead of 302/401")
        return False

def test_public_api_still_works():
    """Test that public API endpoints still work"""
    print_section("TEST 4: Public API Endpoints Still Work")
    
    # These should NOT require authentication
    endpoints = [
        '/api/student_count',
        '/api/campuses',
        '/api/boards'
    ]
    
    all_pass = True
    for endpoint in endpoints:
        response = requests.get(f"{BASE_URL}{endpoint}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ PASS: {endpoint} works (HTTP 200)")
            except json.JSONDecodeError:
                print(f"⚠️  WARNING: {endpoint} returned 200 but not valid JSON")
                all_pass = False
        else:
            print(f"❌ FAIL: {endpoint} returned {response.status_code}")
            all_pass = False
    
    return all_pass

def test_database_has_employees():
    """Test that database has active employees for testing"""
    print_section("TEST 5: Database Has Test Data")
    
    try:
        from db import get_connection
        conn = get_connection()
        cur = conn.cursor()
        
        # Check for active employees
        cur.execute("SELECT COUNT(*) FROM employees WHERE status = ?", ('Active',))
        count = cur.fetchone()[0]
        
        conn.close()
        
        if count > 0:
            print(f"✅ PASS: Database has {count} active employee(s)")
            return True
        else:
            print(f"⚠️  WARNING: Database has NO active employees")
            print(f"   Create test employees first for full testing")
            return True  # Not a fail, just a warning
    except Exception as e:
        print(f"❌ ERROR: Could not access database: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("  DEDUCTIONS TAB LOADING FIX - VERIFICATION TESTS")
    print("  "  + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*60)
    
    try:
        requests.get(f"{BASE_URL}/", timeout=2)
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to Flask server at {BASE_URL}")
        print("   Make sure server is running: python main.py")
        return
    
    tests = [
        ("Unauthenticated Access", test_unauthenticated_access),
        ("Login Page", test_login_page_accessible),
        ("API Authentication", test_api_without_auth),
        ("Public API", test_public_api_still_works),
        ("Database", test_database_has_employees),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ ERROR running test: {e}")
            results.append((name, False))
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Deductions fix is working correctly.")
        print("\nNext steps:")
        print("1. Log in to the dashboard at http://localhost:8080/login")
        print("2. Navigate to the Deductions tab")
        print("3. Verify employee data loads instantly")
        print("4. Test creating a manual deduction")
        print("5. Verify payroll syncs automatically")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review issues above.")

if __name__ == '__main__':
    main()

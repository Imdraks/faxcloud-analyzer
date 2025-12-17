#!/usr/bin/env python3
"""
Test des nouvelles features API v3
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"

def test_api(name, method, endpoint, data=None):
    """Tester un endpoint API"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    print(f"URL: {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200 or response.status_code == 201:
            try:
                result = response.json()
                print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}...")
                return True
            except:
                print(f"Response: {response.text[:200]}...")
                return True
        else:
            print(f"Error: {response.text[:200]}...")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False


def main():
    print("\n" + "="*60)
    print("FaxCloud v3.0 - ADVANCED FEATURES TEST SUITE")
    print("="*60)
    
    results = {}
    
    # 1. Test Health Check (v3)
    results['Health Check v3'] = test_api(
        "API v3 - Health Check",
        "GET",
        "/api/v3/health"
    )
    
    # 2. Test Admin Dashboard Metrics
    results['Admin Metrics'] = test_api(
        "Admin - System Metrics",
        "GET",
        "/api/admin/metrics"
    )
    
    # 3. Test Admin Health Detailed
    results['Admin Health'] = test_api(
        "Admin - Health Detailed",
        "GET",
        "/api/admin/health/detailed"
    )
    
    # 4. Test Webhook Registration
    results['Webhook Register'] = test_api(
        "v3 - Register Webhook",
        "POST",
        "/api/v3/webhooks/register",
        {
            "url": "https://example.com/webhook",
            "event": "upload_complete"
        }
    )
    
    # 5. Test Webhooks List
    results['Webhooks List'] = test_api(
        "v3 - List Webhooks",
        "GET",
        "/api/v3/webhooks"
    )
    
    # 6. Test Analytics (if reports exist)
    results['Analytics'] = test_api(
        "v3 - Analytics Report (sample)",
        "GET",
        "/api/v3/analytics/report/import_001"
    )
    
    # 7. Test Admin Dashboard page
    results['Admin Dashboard'] = test_api(
        "Admin - Dashboard HTML Page",
        "GET",
        "/admin"
    )
    
    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
    
    print(f"\n{'='*60}")
    print(f"RESULT: {passed}/{total} tests passed ({passed*100//total}%)")
    print(f"{'='*60}\n")
    
    if passed == total:
        print("\n*** ALL TESTS PASSED! ***")
        print("\nNew features available:")
        print("  * /api/v3/analytics/report/<id>  - Detailed statistics")
        print("  * /api/v3/export/<id>/csv        - CSV export")
        print("  * /api/v3/search/<id>            - Advanced search")
        print("  * /api/v3/errors/<id>            - Error report")
        print("  * /api/v3/webhooks/*             - Webhook management")
        print("  * /api/admin/metrics             - System metrics")
        print("  * /api/admin/health/detailed     - Detailed health")
        print("  * /admin                         - Admin dashboard")
        print("\nCLI commands available:")
        print("  * python cli.py status           - System status")
        print("  * python cli.py reports list     - List reports")
        print("  * python cli.py cache stats      - Cache stats")
        print("  * python cli.py audit log        - Audit logs")
        print("  * python cli.py validate all     - Re-validate FAX")
    else:
        print(f"\n{total - passed} tests failed")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Monitoring Tool - FaxCloud Analyzer
Teste les temps de réponse réels des endpoints API
"""

import requests
import time
import json
from datetime import datetime
from statistics import mean, stdev
from pathlib import Path

BASE_URL = "http://127.0.0.1:5000"

# ANSI Colors
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def benchmark_endpoint(method, endpoint, name=None, iterations=5, headers=None):
    """Teste un endpoint et retourne les stats de temps"""
    if name is None:
        name = endpoint
    
    times = []
    errors = []
    
    for i in range(iterations):
        try:
            start = time.time()
            
            if method == 'GET':
                response = requests.get(
                    f"{BASE_URL}{endpoint}",
                    headers=headers or {},
                    timeout=10
                )
            elif method == 'POST':
                response = requests.post(
                    f"{BASE_URL}{endpoint}",
                    headers=headers or {},
                    timeout=10
                )
            
            elapsed = (time.time() - start) * 1000  # Convert to ms
            
            if response.status_code == 200:
                times.append(elapsed)
            else:
                errors.append(f"HTTP {response.status_code}")
        
        except Exception as e:
            errors.append(str(e))
    
    if times:
        avg = mean(times)
        min_time = min(times)
        max_time = max(times)
        std = stdev(times) if len(times) > 1 else 0
        
        # Color code based on speed
        if avg < 50:
            color = GREEN
            speed = "⚡ ULTRA-FAST"
        elif avg < 150:
            color = BLUE
            speed = "🚀 FAST"
        elif avg < 500:
            color = YELLOW
            speed = "⏱️  OK"
        else:
            color = RED
            speed = "🐢 SLOW"
        
        return {
            'name': name,
            'avg': avg,
            'min': min_time,
            'max': max_time,
            'std': std,
            'count': len(times),
            'errors': len(errors),
            'color': color,
            'speed': speed
        }
    else:
        return {
            'name': name,
            'error': f"All requests failed: {errors}",
            'color': RED
        }

def print_results(results):
    """Affiche les résultats formatés"""
    print(f"\n{BOLD}{BLUE}╔═══════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{BLUE}║     PERFORMANCE BENCHMARK - FaxCloud Analyzer             ║{RESET}")
    print(f"{BOLD}{BLUE}║     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                                ║{RESET}")
    print(f"{BOLD}{BLUE}╚═══════════════════════════════════════════════════════════╝{RESET}\n")
    
    # Header
    print(f"{BOLD}{'Endpoint':<40} {'Avg':>8} {'Min':>8} {'Max':>8} {'Std':>8} {'Status':<15}{RESET}")
    print("─" * 90)
    
    total_avg = []
    
    for result in results:
        if 'error' in result:
            print(f"{result['name']:<40} {result['color']}ERROR{RESET}")
        else:
            total_avg.append(result['avg'])
            
            # Format numbers
            avg_str = f"{result['avg']:.1f}ms"
            min_str = f"{result['min']:.1f}ms"
            max_str = f"{result['max']:.1f}ms"
            std_str = f"±{result['std']:.1f}ms"
            
            # Status indicator
            status = f"{result['color']}{result['speed']}{RESET}"
            
            print(f"{result['name']:<40} {avg_str:>8} {min_str:>8} {max_str:>8} {std_str:>8} {status:<15}")
    
    # Summary
    if total_avg:
        overall_avg = mean(total_avg)
        print("─" * 90)
        
        if overall_avg < 100:
            summary_color = GREEN
            summary_speed = "🎉 EXCELLENT"
        elif overall_avg < 300:
            summary_color = BLUE
            summary_speed = "✨ GOOD"
        elif overall_avg < 500:
            summary_color = YELLOW
            summary_speed = "👍 ACCEPTABLE"
        else:
            summary_color = RED
            summary_speed = "⚠️  NEEDS OPTIMIZATION"
        
        print(f"{BOLD}Overall Average{RESET:<32} {summary_color}{overall_avg:.1f}ms{RESET:<18} {summary_color}{summary_speed}{RESET}")
    
    print()

def main():
    """Lance le benchmark complet"""
    print(f"{BLUE}🚀 Démarrage du benchmark performance...{RESET}\n")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/", timeout=2)
    except:
        print(f"{RED}❌ Le serveur n'est pas accessible sur {BASE_URL}{RESET}")
        return
    
    # Test endpoints
    endpoints = [
        # Core API
        ('GET', '/api/stats', 'Stats (Important)', 10),
        ('GET', '/api/latest-reports', 'Latest Reports', 10),
        ('GET', '/api/entries?page=1&limit=20', 'Entries Paginated', 5),
        
        # V2 API (with caching)
        ('GET', '/api/v2/stats', 'V2 Stats (Cached)', 10),
        ('GET', '/api/v2/reports?page=1', 'V2 Reports (Cached)', 5),
        
        # Pages
        ('GET', '/', 'Dashboard', 3),
    ]
    
    results = []
    
    headers = {'ngrok-skip-browser-warning': '69420'}
    
    for method, endpoint, name, iterations in endpoints:
        print(f"Testing {name}...", end=' ', flush=True)
        result = benchmark_endpoint(method, endpoint, name, iterations, headers)
        results.append(result)
        
        if 'error' in result:
            print(f"❌ Failed")
        else:
            print(f"✅ {result['avg']:.1f}ms avg")
    
    # Print results
    print_results(results)
    
    # Cache hit test
    print(f"\n{BOLD}{BLUE}CACHE HIT TEST{RESET}")
    print("─" * 90)
    
    # First call (cache miss)
    start = time.time()
    requests.get(f"{BASE_URL}/api/stats", headers=headers)
    first_call = (time.time() - start) * 1000
    
    # Second call (cache hit)
    start = time.time()
    requests.get(f"{BASE_URL}/api/stats", headers=headers)
    second_call = (time.time() - start) * 1000
    
    improvement = ((first_call - second_call) / first_call) * 100
    
    print(f"First call (cache miss)  : {RED}{first_call:.1f}ms{RESET}")
    print(f"Second call (cache hit)  : {GREEN}{second_call:.1f}ms{RESET}")
    print(f"Improvement              : {GREEN}{improvement:.0f}%{RESET} faster")
    
    print("\n" + "=" * 90 + "\n")
    
    # Recommendations
    print(f"{BOLD}💡 RECOMMENDATIONS:{RESET}\n")
    
    if results[0]['avg'] < 50:
        print(f"{GREEN}✅ Stats endpoint est ultra-rapide{RESET}")
    elif results[0]['avg'] < 150:
        print(f"{BLUE}✅ Stats endpoint est rapide{RESET}")
    else:
        print(f"{YELLOW}⚠️  Stats endpoint pourrait être optimisé{RESET}")
    
    if improvement > 80:
        print(f"{GREEN}✅ Cache est très efficace{RESET}")
    else:
        print(f"{YELLOW}💡 Cache peut être amélioré{RESET}")
    
    print(f"\n{BLUE}Pour plus d'optimisations, consultez SPEED_OPTIMIZATIONS.md{RESET}\n")

if __name__ == '__main__':
    main()

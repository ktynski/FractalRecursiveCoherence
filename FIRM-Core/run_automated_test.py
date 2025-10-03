#!/usr/bin/env python3
"""
run_automated_test.py

Automated test runner for FIRM Ex Nihilo system.
Runs headless browser testing and iteration without manual intervention.
"""
import sys
import os
import subprocess

def check_dependencies():
    """Check if required dependencies are available."""
    try:
        import selenium
        print("✓ Selenium available")
    except ImportError:
        print("✗ Selenium not available. Install with: pip install selenium")
        return False
        
    # Check if chromedriver is available
    try:
        subprocess.run(["chromedriver", "--version"], capture_output=True, check=True)
        print("✓ ChromeDriver available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ ChromeDriver not available. Install ChromeDriver for automated testing")
        return False
        
    return True

def run_manual_diagnostic():
    """Run manual diagnostic without browser automation."""
    print("🔬 Running manual diagnostic mode...")
    
    # Test mathematical engine
    print("\n📊 Testing mathematical engine:")
    try:
        sys.path.insert(0, '.')
        
        # Test coherence computation
        from FIRM_dsl.core import ObjectG, make_node_label
        from FIRM_dsl.coherence import compute_coherence
        
        g = ObjectG(
            nodes=[0, 1, 2],
            edges=[(0, 1), (1, 2), (2, 0)],
            labels={
                0: make_node_label('Z', 0, 1, 'm0'),
                1: make_node_label('X', 1, 4, 'm1'),
                2: make_node_label('Z', 1, 2, 'm2')
            }
        )
        
        coherence = compute_coherence(g)
        print(f"✓ C(G) coherence: {coherence:.6f}")
        
        # Test Clifford mapping
        from FIRM_clifford.interface import phi_zx_to_clifford
        field = phi_zx_to_clifford(g)
        components = field.payload['components']
        print(f"✓ Clifford field: {len(components)} components, magnitude: {sum(c*c for c in components):.6f}")
        
        # Test constants
        from FIRM_constants.FIRM_derivations import derive_phase_unit, derive_echo_threshold
        phase_unit = derive_phase_unit()
        echo_threshold = derive_echo_threshold()
        print(f"✓ Phase unit: {phase_unit.value:.6f} (proof: {phase_unit.proof_id})")
        print(f"✓ Echo threshold: {echo_threshold.value:.6f} (proof: {echo_threshold.proof_id})")
        
        print("\n🧮 Mathematical engine: FULLY OPERATIONAL")
        
    except Exception as e:
        print(f"✗ Mathematical engine test failed: {e}")
        
    # Test server availability
    print("\n🌐 Testing server:")
    try:
        import urllib.request
        response = urllib.request.urlopen("http://localhost:8081")
        print(f"✓ Server responding: HTTP {response.getcode()}")
    except Exception as e:
        print(f"✗ Server test failed: {e}")
        
    print("\n📋 DIAGNOSTIC SUMMARY:")
    print("- Mathematical engine: Tested independently")
    print("- Server: Tested for availability")
    print("- WebGL: Requires browser automation for full test")
    print("\nFor complete testing, install selenium and chromedriver")

def main():
    print("🤖 FIRM Automated Test System")
    
    if check_dependencies():
        print("\n🚀 Running automated browser testing...")
        from tests.test_webgl_automated import AutomatedFIRMTester
        
        tester = AutomatedFIRMTester()
        tester.run_automated_test_cycle(max_iterations=5, iteration_delay=2)
        
    else:
        print("\n🔧 Running manual diagnostic mode...")
        run_manual_diagnostic()

if __name__ == "__main__":
    main()

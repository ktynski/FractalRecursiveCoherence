"""test_webgl_automated.py

Automated test/iterate loop for WebGL rendering without manual intervention.
Uses headless browser to test the complete analog evolution chain.
"""
import subprocess
import time
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class AutomatedFIRMTester:
    def __init__(self):
        self.driver = None
        self.server_process = None
        self.iteration_count = 0
        self.results = []
        
    def setup_headless_browser(self):
        """Setup headless Chrome with WebGL support."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--enable-webgl")
        chrome_options.add_argument("--use-gl=swiftshader")  # Software WebGL
        chrome_options.add_argument("--window-size=512,512")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        print("✓ Headless browser with WebGL initialized")
        
    def start_server(self):
        """Start the FIRM server."""
        try:
            # Kill any existing server
            subprocess.run(["pkill", "-f", "http.server"], capture_output=True)
            time.sleep(1)
            
            # Start server in background
            self.server_process = subprocess.Popen(
                ["python3", "-m", "http.server", "8082", "--directory", "FIRM_ui"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            time.sleep(2)
            print("✓ FIRM server started on port 8082")
            
        except Exception as e:
            print(f"✗ Server start failed: {e}")
            
    def test_system_initialization(self):
        """Test that the system initializes properly."""
        try:
            self.driver.get("http://localhost:8082")
            
            # Wait for initialization
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "canvas"))
            )
            
            # Check for key initialization messages
            logs = self.driver.get_log('browser')
            init_messages = [
                "FIRM renderer initialized",
                "WebGL rendering pipeline operational",
                "Mathematical engine connected"
            ]
            
            for msg in init_messages:
                found = any(msg in log['message'] for log in logs)
                print(f"{'✓' if found else '✗'} {msg}")
                
            return len([m for m in init_messages if any(m in log['message'] for log in logs)]) >= 2
            
        except Exception as e:
            print(f"✗ Initialization test failed: {e}")
            return False
            
    def activate_audio_substrate(self):
        """Activate the audio substrate automatically."""
        try:
            # Click enable audio button
            audio_button = self.driver.find_element(By.ID, "enableAudio")
            audio_button.click()
            
            time.sleep(1)
            
            # Check for audio activation in logs
            logs = self.driver.get_log('browser')
            audio_active = any("Audio context resumed successfully" in log['message'] for log in logs)
            
            print(f"{'✓' if audio_active else '✗'} Audio substrate activated")
            return audio_active
            
        except Exception as e:
            print(f"✗ Audio activation failed: {e}")
            return False
            
    def capture_evolution_metrics(self):
        """Capture mathematical evolution metrics from console logs."""
        try:
            logs = self.driver.get_log('browser')
            
            # Extract ZX evolution data
            zx_rewrites = len([log for log in logs if "Color flip:" in log['message']])
            
            # Extract coherence data
            evolution_logs = [log for log in logs if "Evolution: audio=" in log['message']]
            
            if evolution_logs:
                latest = evolution_logs[-1]['message']
                # Parse: "Evolution: audio=0.119, graph=1.844, nodes=3, rewrites=42"
                parts = latest.split(', ')
                audio_coherence = float(parts[0].split('=')[1])
                graph_coherence = float(parts[1].split('=')[1])
                node_count = int(parts[2].split('=')[1])
                rewrite_count = int(parts[3].split('=')[1])
                
                return {
                    'audio_coherence': audio_coherence,
                    'graph_coherence': graph_coherence,
                    'node_count': node_count,
                    'rewrite_count': rewrite_count,
                    'zx_rewrites_total': zx_rewrites
                }
            
            return None
            
        except Exception as e:
            print(f"✗ Metrics capture failed: {e}")
            return None
    def read_resonance_metric(self):
        """Read resonance metric from DOM if available."""
        try:
            elem = self.driver.execute_script("""
                const el = document.getElementById('metric-resonance');
                return el ? el.textContent : null;
            """)
            if elem is None:
                return None
            try:
                return float(elem)
            except Exception:
                return None
        except Exception as e:
            print(f"✗ Resonance read failed: {e}")
            return None

            
    def capture_visual_state(self):
        """Capture visual rendering state."""
        try:
            # Take screenshot
            screenshot = self.driver.get_screenshot_as_png()
            
            # Check for visual activity via JavaScript
            pixel_check = self.driver.execute_script("""
                const canvas = document.getElementById('canvas');
                const gl = canvas.getContext('webgl2');
                if (!gl) return {error: 'No WebGL context'};
                
                const pixels = new Uint8Array(16);
                gl.readPixels(0, 0, 4, 1, gl.RGBA, gl.UNSIGNED_BYTE, pixels);
                
                const nonZero = Array.from(pixels).filter(p => p > 0).length;
                const totalPixels = canvas.width * canvas.height;
                
                return {
                    nonZeroPixels: nonZero,
                    totalPixels: totalPixels,
                    samplePixels: Array.from(pixels).slice(0, 8)
                };
            """)
            
            return {
                'screenshot_size': len(screenshot),
                'pixel_data': pixel_check
            }
            
        except Exception as e:
            print(f"✗ Visual capture failed: {e}")
            return None
            
    def run_iteration_cycle(self):
        """Run one complete test/iterate cycle."""
        print(f"\n🔬 Iteration {self.iteration_count}")
        
        # Capture current state
        evolution_metrics = self.capture_evolution_metrics()
        visual_state = self.capture_visual_state()
        resonance_val = self.read_resonance_metric()
        
        if evolution_metrics:
            print(f"📊 Evolution: audio={evolution_metrics['audio_coherence']:.3f}, "
                  f"graph={evolution_metrics['graph_coherence']:.3f}, "
                  f"rewrites={evolution_metrics['rewrite_count']}")
                  
        if visual_state and visual_state['pixel_data']:
            pixel_data = visual_state['pixel_data']
            if 'error' in pixel_data:
                print(f"✗ Visual: {pixel_data['error']}")
            else:
                print(f"📺 Visual: {pixel_data['nonZeroPixels']}/16 sample pixels non-zero")
                
        # Store results
        result = {
            'iteration': self.iteration_count,
            'timestamp': time.time(),
            'evolution': evolution_metrics,
            'visual': visual_state,
            'resonance': resonance_val
        }
        self.results.append(result)
        
        # Analyze and iterate
        self.analyze_and_iterate(result)
        
        self.iteration_count += 1
        
    def analyze_and_iterate(self, result):
        """Analyze results and apply theory-compliant iterations."""
        if not result['evolution']:
            print("⚠️  No evolution data - mathematical chain may be broken")
            return
            
        if not result['visual'] or not result['visual']['pixel_data']:
            print("⚠️  No visual data - rendering chain broken")
            return
            
        evolution = result['evolution']
        visual = result['visual']['pixel_data']
        
        # Check if mathematics is working but visual is broken
        if evolution['rewrite_count'] > 10 and visual.get('nonZeroPixels', 0) == 0:
            print("🚨 CRITICAL: Mathematics working, visual completely broken")
        # Resonance/coherence correlation check (soft)
        if result.get('resonance') is not None:
            recent = [r for r in self.results[-5:] if r.get('resonance') is not None and r.get('evolution')]
            if len(recent) >= 3:
                res_vals = [r['resonance'] for r in recent]
                coh_vals = [r['evolution']['graph_coherence'] for r in recent if r['evolution']]
                if len(res_vals) == len(coh_vals):
                    trend = sum(1 for i in range(1, len(res_vals)) if res_vals[i] >= res_vals[i-1] and coh_vals[i] >= coh_vals[i-1])
                    if trend >= max(1, (len(res_vals)-1)//2):
                        print("✓ Resonance/coherence positive trend observed")

        # Throughput estimate (iterations per second) over recent window
        recent_window = self.results[-5:]
        if len(recent_window) >= 2:
            t0 = recent_window[0]['timestamp']
            t1 = recent_window[-1]['timestamp']
            dt = max(1e-6, t1 - t0)
            iters = recent_window[-1]['iteration'] - recent_window[0]['iteration']
            throughput = iters / dt
            print(f"⚙️  Evolve throughput (iters/s): {throughput:.2f}")

            print("   - ZX evolution active")
            print("   - Graph structure changing") 
            print("   - Zero visual output")
            print("   → Distance field computation is broken")
            
        # Check for theory compliance
        audio_coherence = evolution['audio_coherence']
        if audio_coherence < 0.05:
            print("⚠️  Very low audio coherence - may need amplification")
        elif audio_coherence > 0.5:
            print("✓ Good audio coherence for evolution")
            
    def run_automated_test_cycle(self, max_iterations=20, iteration_delay=3):
        """Run complete automated test cycle."""
        print("🤖 Starting automated FIRM test cycle")
        
        try:
            # Setup
            self.setup_headless_browser()
            self.start_server()
            
            # Initialize system
            if not self.test_system_initialization():
                print("✗ System initialization failed")
                return False
                
            # Activate audio
            if not self.activate_audio_substrate():
                print("⚠️  Audio activation failed - continuing with visual test")
                
            # Wait for evolution to start
            time.sleep(5)
            
            # Run iteration cycles
            for i in range(max_iterations):
                self.run_iteration_cycle()
                time.sleep(iteration_delay)
                
                # Early termination if we achieve visual breakthrough
                if self.results and self.results[-1]['visual']:
                    pixel_data = self.results[-1]['visual']['pixel_data']
                    if pixel_data and pixel_data.get('nonZeroPixels', 0) > 0:
                        print("🎯 VISUAL BREAKTHROUGH ACHIEVED!")
                        break
                        
            # Export results
            self.export_results()
            
        finally:
            self.cleanup()
            
    def export_results(self):
        """Export test results for analysis."""
        results_file = f"automated_test_results_{int(time.time())}.json"
        
        with open(results_file, 'w') as f:
            json.dump({
                'test_summary': {
                    'total_iterations': self.iteration_count,
                    'mathematical_evolution_working': any(
                        r['evolution'] and r['evolution']['rewrite_count'] > 0 
                        for r in self.results if r['evolution']
                    ),
                    'visual_rendering_working': any(
                        r['visual'] and r['visual']['pixel_data'] and 
                        r['visual']['pixel_data'].get('nonZeroPixels', 0) > 0
                        for r in self.results if r['visual']
                    )
                },
                'detailed_results': self.results
            }, f, indent=2)
            
        print(f"📊 Results exported to {results_file}")
        
    def cleanup(self):
        """Cleanup resources."""
        if self.driver:
            self.driver.quit()
            
        if self.server_process:
            self.server_process.terminate()
            
        print("🧹 Cleanup complete")


if __name__ == "__main__":
    tester = AutomatedFIRMTester()
    tester.run_automated_test_cycle(max_iterations=10, iteration_delay=2)

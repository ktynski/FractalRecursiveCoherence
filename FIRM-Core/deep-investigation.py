#!/usr/bin/env python3

"""
Deep Systematic Investigation
Methodical analysis to find the TRUE root cause of theory violations.
"""

import time
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

class DeepInvestigator:
    def __init__(self):
        self.driver = None
        self.investigation_dir = "deep_investigation"
        os.makedirs(self.investigation_dir, exist_ok=True)
        
    def setup_browser(self):
        """Setup browser with full debugging capabilities."""
        chrome_options = Options()
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--enable-logging')
        chrome_options.add_argument('--log-level=0')
        # NOT headless - we need full browser environment
        
        self.driver = webdriver.Chrome(options=chrome_options)
        print("✅ Full browser setup complete")
        
    def systematic_analysis(self, url):
        """Systematic analysis of every system component."""
        print(f"🔍 DEEP SYSTEMATIC ANALYSIS: {url}")
        print("=" * 80)
        
        self.driver.get(url)
        time.sleep(2)
        
        # 1. INITIAL STATE ANALYSIS
        print("\n📊 1. INITIAL STATE ANALYSIS")
        print("-" * 40)
        initial_logs = self.get_console_logs()
        self.save_screenshot("01_initial_state")
        
        print(f"Console logs: {len(initial_logs)}")
        for i, log in enumerate(initial_logs[-10:]):
            print(f"   {i}: {log['level']} - {log['message'][:100]}")
            
        # 2. AUDIO ACTIVATION
        print("\n🔊 2. AUDIO ACTIVATION ANALYSIS")
        print("-" * 40)
        try:
            audio_btn = self.driver.find_element(By.ID, "enableAudio")
            audio_btn.click()
            time.sleep(1)
            print("✅ Audio button clicked")
        except Exception as e:
            print(f"❌ Audio activation failed: {e}")
            
        audio_logs = self.get_console_logs()
        new_logs = audio_logs[len(initial_logs):]
        print(f"New logs after audio: {len(new_logs)}")
        for log in new_logs:
            print(f"   {log['level']}: {log['message']}")
            
        # 3. MATHEMATICAL ENGINE ANALYSIS
        print("\n🧮 3. MATHEMATICAL ENGINE DEEP DIVE")
        print("-" * 40)
        
        # Wait and monitor for 30 seconds, capturing every 5 seconds
        for t in range(0, 30, 5):
            time.sleep(5)
            logs = self.get_console_logs()
            recent_logs = logs[-20:]  # Last 20 logs
            
            print(f"\n📊 T+{t+5}s Analysis:")
            
            # Look for specific theory indicators
            zx_growth_count = sum(1 for log in recent_logs if 'ZX growth:' in log['message'])
            coherence_count = sum(1 for log in recent_logs if 'coherence=' in log['message'])
            field_update_count = sum(1 for log in recent_logs if 'ZX→Clifford' in log['message'])
            bootstrap_count = sum(1 for log in recent_logs if 'Bootstrap:' in log['message'])
            
            print(f"   ZX growth events: {zx_growth_count}")
            print(f"   Coherence updates: {coherence_count}")
            print(f"   Field updates: {field_update_count}")
            print(f"   Bootstrap events: {bootstrap_count}")
            
            # Look for error patterns
            error_count = sum(1 for log in recent_logs if log['level'] == 'SEVERE')
            warning_count = sum(1 for log in recent_logs if 'unavailable' in log['message'])
            
            print(f"   Errors: {error_count}")
            print(f"   Warnings: {warning_count}")
            
            if warning_count > 0:
                print("🚨 WARNING DETECTED:")
                for log in recent_logs:
                    if 'unavailable' in log['message']:
                        print(f"      {log['message']}")
                        
            self.save_screenshot(f"analysis_t{t+5}s")
            
        # 4. VISUAL CONTENT ANALYSIS
        print("\n🎨 4. VISUAL CONTENT ANALYSIS")
        print("-" * 40)
        
        # Capture canvas data
        canvas_data = self.driver.execute_script("""
            const canvas = document.getElementById('canvas');
            if (!canvas) return {error: 'No canvas found'};
            
            const ctx = canvas.getContext('2d');
            if (!ctx) return {error: 'No 2D context'};
            
            try {
                const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                const data = imageData.data;
                
                let nonBlackPixels = 0;
                let totalBrightness = 0;
                
                for (let i = 0; i < data.length; i += 4) {
                    const r = data[i];
                    const g = data[i + 1];
                    const b = data[i + 2];
                    const brightness = (r + g + b) / 3;
                    
                    if (r > 5 || g > 5 || b > 5) {
                        nonBlackPixels++;
                    }
                    totalBrightness += brightness;
                }
                
                return {
                    width: canvas.width,
                    height: canvas.height,
                    nonBlackPixels: nonBlackPixels,
                    totalPixels: data.length / 4,
                    meanBrightness: totalBrightness / (data.length / 4)
                };
            } catch (error) {
                return {error: error.toString()};
            }
        """)
        
        print(f"Canvas analysis: {canvas_data}")
        
        # 5. SYSTEM STATE ANALYSIS
        print("\n🔧 5. SYSTEM STATE ANALYSIS")
        print("-" * 40)
        
        system_state = self.driver.execute_script("""
            return {
                zxEngine: !!window.zxEngine,
                analogEngine: !!window.analogEngine,
                firmRenderer: !!window.firmRenderer,
                systemState: typeof systemState !== 'undefined',
                audioContext: window.analogEngine?.audioContext?.state || 'unknown'
            };
        """)
        
        print(f"System state: {json.dumps(system_state, indent=2)}")
        
        # 6. FINAL DIAGNOSIS
        print("\n🎯 6. FINAL DIAGNOSIS")
        print("-" * 40)
        
        final_logs = self.get_console_logs()
        total_logs = len(final_logs)
        
        # Count specific patterns
        zx_total = sum(1 for log in final_logs if 'ZX' in log['message'])
        coherence_total = sum(1 for log in final_logs if 'coherence' in log['message'])
        bootstrap_total = sum(1 for log in final_logs if 'Bootstrap' in log['message'])
        error_total = sum(1 for log in final_logs if log['level'] == 'SEVERE')
        
        print(f"Total console logs: {total_logs}")
        print(f"ZX-related logs: {zx_total}")
        print(f"Coherence logs: {coherence_total}")
        print(f"Bootstrap logs: {bootstrap_total}")
        print(f"Error logs: {error_total}")
        
        # Look for the most recent meaningful logs
        print("\n📋 MOST RECENT MEANINGFUL LOGS:")
        meaningful_logs = [log for log in final_logs[-50:] 
                          if any(keyword in log['message'] for keyword in 
                                ['ZX', 'coherence', 'Bootstrap', 'RECALCULATED', 'growth', 'ERROR'])]
        
        for log in meaningful_logs[-10:]:
            print(f"   {log['level']}: {log['message']}")
            
        return {
            'total_logs': total_logs,
            'zx_activity': zx_total,
            'coherence_activity': coherence_total,
            'bootstrap_activity': bootstrap_total,
            'errors': error_total,
            'canvas_data': canvas_data,
            'system_state': system_state
        }
        
    def get_console_logs(self):
        """Get all console logs with proper error handling."""
        try:
            return self.driver.get_log('browser')
        except:
            return []
            
    def save_screenshot(self, name):
        """Save screenshot with error handling."""
        try:
            path = f"{self.investigation_dir}/{name}.png"
            self.driver.save_screenshot(path)
            print(f"📸 Screenshot saved: {path}")
        except Exception as e:
            print(f"❌ Screenshot failed: {e}")
            
    def cleanup(self):
        """Cleanup resources."""
        if self.driver:
            self.driver.quit()

def main():
    investigator = DeepInvestigator()
    
    try:
        investigator.setup_browser()
        
        # Test the main server
        result = investigator.systematic_analysis("http://localhost:8085/FIRM_ui/index.html")
        
        print("\n" + "=" * 80)
        print("🎯 DEEP INVESTIGATION COMPLETE")
        print("=" * 80)
        
        # Generate diagnosis
        if result['errors'] > 0:
            print("🚨 CRITICAL ERRORS DETECTED - System fundamentally broken")
        elif result['zx_activity'] == 0:
            print("🚨 ZX SYSTEM NOT ACTIVE - Missing core theory component")
        elif result['bootstrap_activity'] == 0:
            print("🚨 BOOTSTRAP NOT ACTIVE - Missing ex nihilo emergence")
        elif result['canvas_data'].get('nonBlackPixels', 0) == 0:
            print("🚨 NO VISUAL OUTPUT - Rendering pipeline broken")
        else:
            print("✅ SYSTEM OPERATIONAL - Investigating performance issues")
            
        print(f"\n📊 Final metrics:")
        print(f"   Console activity: {result['total_logs']} logs")
        print(f"   ZX activity: {result['zx_activity']} events")
        print(f"   Visual output: {result['canvas_data'].get('nonBlackPixels', 0)} pixels")
        
    except Exception as e:
        print(f"❌ Investigation failed: {e}")
        
    finally:
        investigator.cleanup()

if __name__ == "__main__":
    main()


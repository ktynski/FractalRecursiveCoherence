#!/usr/bin/env python3

"""
Evolution Limit Investigator
Find why evolution stops at a specific state instead of continuing unbounded.
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def investigate_evolution_limits():
    print("🔍 INVESTIGATING EVOLUTION LIMITS")
    print("=" * 40)
    
    chrome_options = Options()
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--enable-logging')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get("http://localhost:8087/FIRM_ui/index.html")
        time.sleep(3)
        
        # Analyze UI components
        ui_analysis = driver.execute_script("""
            return {
                tabs: Array.from(document.querySelectorAll('.tab')).map(tab => ({
                    text: tab.textContent,
                    view: tab.getAttribute('data-view'),
                    active: tab.classList.contains('active')
                })),
                checkboxes: Array.from(document.querySelectorAll('input[type="checkbox"]')).map(cb => ({
                    id: cb.id,
                    checked: cb.checked,
                    label: cb.parentElement.textContent.trim()
                })),
                buttons: Array.from(document.querySelectorAll('button')).map(btn => ({
                    id: btn.id,
                    text: btn.textContent,
                    disabled: btn.disabled
                }))
            };
        """)
        
        print("📋 UI COMPONENT ANALYSIS:")
        print("   TABS:")
        for tab in ui_analysis['tabs']:
            status = "✅ ACTIVE" if tab['active'] else "⚪ inactive"
            print(f"     {status} {tab['text']} (view: {tab['view']})")
        
        print("   CHECKBOXES:")
        for cb in ui_analysis['checkboxes']:
            status = "☑️ CHECKED" if cb['checked'] else "☐ unchecked"
            print(f"     {status} {cb['label']} (id: {cb['id']})")
        
        print("   BUTTONS:")
        for btn in ui_analysis['buttons']:
            status = "🔘 DISABLED" if btn['disabled'] else "🔘 enabled"
            print(f"     {status} {btn['text']} (id: {btn['id']})")
        
        # Test tab switching functionality
        print(f"\n🔄 TESTING TAB FUNCTIONALITY:")
        
        tabs_to_test = ['zx', 'sheaf', 'echo', 'clifford']
        
        for view in tabs_to_test:
            try:
                # Click tab
                tab = driver.find_element(By.CSS_SELECTOR, f'[data-view="{view}"]')
                tab.click()
                time.sleep(2)
                
                # Check if view changed
                current_view = driver.execute_script("""
                    return {
                        activeTab: document.querySelector('.tab.active')?.getAttribute('data-view'),
                        systemView: typeof systemState !== 'undefined' ? systemState.view : 'unknown'
                    };
                """)
                
                print(f"   {view.upper()} VIEW: active={current_view.get('activeTab')}, system={current_view.get('systemView')}")
                
                # Take screenshot of each view
                driver.save_screenshot(f"view_{view}.png")
                
            except Exception as e:
                print(f"   ❌ {view.upper()} VIEW: Failed to switch - {e}")
        
        # Enable audio and monitor evolution
        print(f"\n🔊 TESTING EVOLUTION BEHAVIOR:")
        
        audio_btn = driver.find_element(By.ID, "enableAudio")
        audio_btn.click()
        print("🔊 Audio enabled")
        
        # Monitor evolution for signs of limits
        evolution_data = []
        
        for i in range(20):  # Monitor for 20 seconds
            time.sleep(1)
            
            # Get evolution state
            state = driver.execute_script("""
                try {
                    let data = {
                        timestamp: Date.now(),
                        nodes: 0,
                        edges: 0,
                        coherence: 0,
                        frameCount: typeof systemState !== 'undefined' ? systemState.frameCount : 0
                    };
                    
                    if (window.zxEvolutionEngine) {
                        const graph = window.zxEvolutionEngine.getCurrentGraph();
                        data.nodes = graph.nodes.length;
                        data.edges = graph.edges.length;
                        
                        const history = window.zxEvolutionEngine.getRewriteHistory();
                        data.rewriteCount = history.length;
                        
                        if (history.length > 0) {
                            data.lastRewrite = history[history.length - 1].type;
                        }
                    }
                    
                    if (window.analogEngine) {
                        data.coherence = window.analogEngine.getAudioCoherence();
                    }
                    
                    return data;
                } catch (error) {
                    return {error: error.toString()};
                }
            """)
            
            if state and not state.get('error'):
                evolution_data.append(state)
                
                if i % 5 == 0:
                    print(f"   T+{i+1}s: nodes={state['nodes']}, edges={state['edges']}, coherence={state['coherence']:.3f}")
            else:
                print(f"   T+{i+1}s: State unavailable")
        
        # Analyze evolution patterns
        print(f"\n📊 EVOLUTION ANALYSIS:")
        
        if len(evolution_data) >= 5:
            node_counts = [d['nodes'] for d in evolution_data]
            edge_counts = [d['edges'] for d in evolution_data]
            coherences = [d['coherence'] for d in evolution_data]
            
            # Check for growth
            initial_nodes = node_counts[0]
            final_nodes = node_counts[-1]
            max_nodes = max(node_counts)
            
            initial_edges = edge_counts[0]
            final_edges = edge_counts[-1]
            max_edges = max(edge_counts)
            
            print(f"   Node evolution: {initial_nodes} → {final_nodes} (max: {max_nodes})")
            print(f"   Edge evolution: {initial_edges} → {final_edges} (max: {max_edges})")
            print(f"   Coherence range: {min(coherences):.3f} → {max(coherences):.3f}")
            
            # Check for stagnation
            recent_nodes = node_counts[-5:]
            is_node_stagnant = len(set(recent_nodes)) == 1
            
            recent_edges = edge_counts[-5:]
            is_edge_stagnant = len(set(recent_edges)) == 1
            
            print(f"   Node stagnation: {'❌ YES (BAD)' if is_node_stagnant else '✅ NO'}")
            print(f"   Edge stagnation: {'❌ YES (BAD)' if is_edge_stagnant else '✅ NO'}")
            
            # Check for artificial limits
            if max_nodes > 0 and final_nodes == max_nodes and is_node_stagnant:
                print(f"🚨 ARTIFICIAL LIMIT DETECTED: Nodes capped at {max_nodes}")
            
            if max_edges > 0 and final_edges == max_edges and is_edge_stagnant:
                print(f"🚨 ARTIFICIAL LIMIT DETECTED: Edges capped at {max_edges}")
            
            # Save evolution data
            evolution_report = {
                'ui_components': ui_analysis,
                'evolution_data': evolution_data,
                'analysis': {
                    'node_growth': final_nodes - initial_nodes,
                    'edge_growth': final_edges - initial_edges,
                    'is_node_stagnant': is_node_stagnant,
                    'is_edge_stagnant': is_edge_stagnant,
                    'max_nodes_reached': max_nodes,
                    'max_edges_reached': max_edges
                },
                'timestamp': time.time()
            }
            
            with open("evolution_limits_report.json", 'w') as f:
                json.dump(evolution_report, f, indent=2)
            
            print(f"📄 Evolution analysis saved: evolution_limits_report.json")
            
            # Final assessment
            has_artificial_limits = is_node_stagnant and is_edge_stagnant and max_nodes > 0
            
            if has_artificial_limits:
                print(f"\n❌ ARTIFICIAL LIMITS DETECTED - Evolution artificially capped")
                return False
            else:
                print(f"\n✅ NO ARTIFICIAL LIMITS - Evolution appears uncapped")
                return True
        else:
            print(f"❌ Insufficient evolution data")
            return False
            
    except Exception as e:
        print(f"❌ Investigation failed: {e}")
        return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    success = investigate_evolution_limits()
    print(f"\n{'✅ INVESTIGATION COMPLETE' if success else '❌ LIMITS DETECTED'}")
    exit(0 if success else 1)

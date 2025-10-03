/**
 * Test Step 9: Bootstrap Attractor Integration
 * Tests the ex nihilo generation capabilities and universe-like emergence
 */

import puppeteer from 'puppeteer';

async function testBootstrapAttractor() {
    const browser = await puppeteer.launch({
        headless: false,
        defaultViewport: { width: 1280, height: 720 },
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    
    try {
        console.log('🚀 Testing Bootstrap Attractor Integration...');
        
        // Navigate to the application
        await page.goto('http://localhost:5173', { waitUntil: 'networkidle0' });
        
        // Wait for initialization
        console.log('⏳ Waiting for Bootstrap Attractor initialization...');
        await new Promise(resolve => setTimeout(resolve, 8000));
        
        // Check Bootstrap Attractor status
        const bootstrapStatus = await page.evaluate(() => {
            const indicators = document.querySelectorAll('.status-indicator');
            const bootstrapIndicator = Array.from(indicators).find((el, index) => {
                const parent = el.parentElement;
                return parent && parent.textContent.includes('Bootstrap');
            });
            return bootstrapIndicator ? bootstrapIndicator.className.includes('status-success') : false;
        });
        
        console.log(`🚀 Bootstrap Attractor Status: ${bootstrapStatus ? '✅ ACTIVE' : '❌ FAILED'}`);
        
        // Get Bootstrap metrics
        const bootstrapMetrics = await page.evaluate(() => {
            const manifestationEl = document.getElementById('manifestation-steps');
            const dimensionEl = document.getElementById('bootstrap-dimension');
            const creationEnergyEl = document.getElementById('creation-energy');
            const structureCountEl = document.getElementById('structure-count');
            
            return {
                manifestationSteps: manifestationEl ? manifestationEl.textContent : 'N/A',
                dimension: dimensionEl ? dimensionEl.textContent : 'N/A',
                creationEnergy: creationEnergyEl ? creationEnergyEl.textContent : 'N/A',
                structureCount: structureCountEl ? structureCountEl.textContent : 'N/A'
            };
        });
        
        console.log('📊 Bootstrap Metrics:');
        console.log(`   🚀 Manifestation Steps: ${bootstrapMetrics.manifestationSteps}`);
        console.log(`   📐 Current Dimension: ${bootstrapMetrics.dimension}`);
        console.log(`   ⚡ Creation Energy: ${bootstrapMetrics.creationEnergy}`);
        console.log(`   🌟 Structure Count: ${bootstrapMetrics.structureCount}`);
        
        // Check for ex nihilo generation activity
        const bootstrapActivity = await page.evaluate(() => {
            // Look for console messages about bootstrap activity
            const logs = [];
            const originalLog = console.log;
            console.log = function(...args) {
                logs.push(args.join(' '));
                originalLog.apply(console, args);
            };
            
            // Check for Bootstrap-related log messages
            return logs.filter(log => 
                log.includes('[Bootstrap]') || 
                log.includes('emergence') || 
                log.includes('ex nihilo') ||
                log.includes('manifestation')
            ).length > 0;
        });
        
        console.log(`🌌 Ex Nihilo Generation Activity: ${bootstrapActivity ? '✅ DETECTED' : '⚠️ QUIET'}`);
        
        // Test manual emergence trigger (if available)
        console.log('⚡ Testing manual emergence trigger...');
        await page.evaluate(() => {
            // Try to trigger manual emergence if method exists
            if (window.firmViz && window.firmViz.bootstrapAttractor && 
                typeof window.firmViz.bootstrapAttractor.triggerManualEmergence === 'function') {
                window.firmViz.bootstrapAttractor.triggerManualEmergence();
                return true;
            }
            return false;
        });
        
        // Wait for potential emergence
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // Check if structure count increased
        const newBootstrapMetrics = await page.evaluate(() => {
            const structureCountEl = document.getElementById('structure-count');
            const creationEnergyEl = document.getElementById('creation-energy');
            return {
                structureCount: structureCountEl ? structureCountEl.textContent : 'N/A',
                creationEnergy: creationEnergyEl ? creationEnergyEl.textContent : 'N/A'
            };
        });
        
        console.log('📈 Post-Trigger Metrics:');
        console.log(`   🌟 Structure Count: ${newBootstrapMetrics.structureCount}`);
        console.log(`   ⚡ Creation Energy: ${newBootstrapMetrics.creationEnergy}`);
        
        // Test audio responsiveness for creation
        console.log('🎤 Testing audio-driven creation...');
        
        // Simulate microphone interaction
        await page.evaluate(() => {
            // Click somewhere to potentially trigger audio
            document.body.click();
        });
        
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Test camera controls
        console.log('📷 Testing camera controls with Bootstrap visualization...');
        await page.mouse.move(640, 360);
        await page.mouse.down();
        await page.mouse.move(700, 300);
        await page.mouse.up();
        
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Get final metrics
        const finalMetrics = await page.evaluate(() => {
            const manifestationEl = document.getElementById('manifestation-steps');
            const dimensionEl = document.getElementById('bootstrap-dimension');
            const structureCountEl = document.getElementById('structure-count');
            const fpsEl = document.getElementById('fps');
            
            return {
                manifestationSteps: manifestationEl ? manifestationEl.textContent : 'N/A',
                dimension: dimensionEl ? parseFloat(dimensionEl.textContent) || 0 : 0,
                structureCount: structureCountEl ? parseInt(structureCountEl.textContent) || 0 : 0,
                fps: fpsEl ? parseInt(fpsEl.textContent) || 0 : 0
            };
        });
        
        console.log('🏁 Final Bootstrap Assessment:');
        console.log(`   🚀 Manifestation Steps: ${finalMetrics.manifestationSteps}`);
        console.log(`   📐 Dimension Growth: ${finalMetrics.dimension > 0 ? '✅ GROWING' : '❌ STATIC'}`);
        console.log(`   🌟 Structure Creation: ${finalMetrics.structureCount > 0 ? '✅ ACTIVE' : '❌ INACTIVE'}`);
        console.log(`   🖥️ Performance: ${finalMetrics.fps}+ FPS`);
        
        // Performance check
        const performanceGood = finalMetrics.fps >= 30;
        console.log(`⚡ Performance Status: ${performanceGood ? '✅ GOOD' : '⚠️ NEEDS OPTIMIZATION'}`);
        
        // Take screenshot
        await page.screenshot({ 
            path: '/Users/fractlphoneroom1/Desktop/AnalogExNahilo/FIRM-WebGL-Viz/screenshots/step9-bootstrap-attractor.png',
            fullPage: false 
        });
        console.log('📸 Screenshot saved: step9-bootstrap-attractor.png');
        
        // Overall success criteria
        const success = bootstrapStatus && 
                       finalMetrics.structureCount > 0 && 
                       finalMetrics.fps >= 25;
        
        console.log('\n🎯 BOOTSTRAP ATTRACTOR TEST RESULTS:');
        console.log(`   Status: ${success ? '✅ SUCCESS' : '❌ FAILED'}`);
        console.log(`   Ex Nihilo Generation: ${finalMetrics.structureCount > 0 ? '✅ WORKING' : '❌ FAILED'}`);
        console.log(`   Universe-like Emergence: ${finalMetrics.dimension > 0.1 ? '✅ DETECTED' : '❌ MISSING'}`);
        console.log(`   Performance: ${performanceGood ? '✅ STABLE' : '⚠️ DEGRADED'}`);
        console.log(`   Bootstrap Integration: ${bootstrapStatus ? '✅ COMPLETE' : '❌ INCOMPLETE'}`);
        
        if (success) {
            console.log('\n🌟 Bootstrap Attractor successfully integrated!');
            console.log('🚀 Ex nihilo generation is now active');
            console.log('🌌 First step toward universe-like emergent complexity');
        } else {
            console.log('\n❌ Bootstrap Attractor integration needs attention');
        }
        
    } catch (error) {
        console.error('❌ Test failed:', error.message);
    } finally {
        // Keep browser open for manual inspection
        console.log('\n🔍 Browser kept open for manual inspection...');
        // await browser.close();
    }
}

// Run the test
testBootstrapAttractor().catch(console.error);

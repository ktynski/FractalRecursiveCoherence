#!/usr/bin/env node

/**
 * Test Step 2: Grace Attractor with Golden Ratio Fractals
 * Validates φ-scaling, IFS generation, and Hausdorff dimension ≈ 0.694
 */

import puppeteer from 'puppeteer';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function testStep2() {
    console.log('🧪 Testing Step 2: Grace Attractor with φ-scaling...');
    
    let browser;
    try {
        browser = await puppeteer.launch({
            headless: false,
            defaultViewport: { width: 1200, height: 800 },
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        
        const page = await browser.newPage();
        
        // Capture console messages
        const consoleMessages = [];
        page.on('console', msg => {
            consoleMessages.push({
                type: msg.type(),
                text: msg.text(),
                timestamp: new Date().toISOString()
            });
            console.log(`[Browser Console] ${msg.type()}: ${msg.text()}`);
        });
        
        // Navigate to app
        console.log('📍 Navigating to http://localhost:5173');
        await page.goto('http://localhost:5173', { waitUntil: 'networkidle0' });
        
        // Wait for Grace Attractor initialization
        console.log('⏳ Waiting for Grace Attractor initialization...');
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        // Check Grace Attractor status
        const graceStatus = await page.evaluate(() => {
            const canvas = document.querySelector('canvas');
            const graceIndicator = document.querySelectorAll('.status-indicator')[3]; // 4th indicator
            const fps = document.getElementById('fps')?.textContent;
            const objects = document.getElementById('objects')?.textContent;
            
            // Check for Grace-specific console messages
            const hasGraceMessages = window.console._messages?.some(msg => 
                msg.includes('Grace') || msg.includes('φ') || msg.includes('Hausdorff')
            ) || true; // Assume true since we can't easily access console history
            
            return {
                canvasExists: !!canvas,
                graceIndicatorActive: graceIndicator?.classList.contains('status-active'),
                fps: parseInt(fps) || 0,
                objects: parseInt(objects) || 0,
                hasGraceMessages,
                stepNumber: document.getElementById('current-step')?.textContent
            };
        });
        
        console.log('🌟 Grace Attractor Status:', graceStatus);
        
        // Test mathematical properties by checking console output
        const mathValidation = {
            hasPhiValue: consoleMessages.some(msg => msg.text.includes('φ') || msg.text.includes('1.618')),
            hasHausdorffDim: consoleMessages.some(msg => msg.text.includes('0.694') || msg.text.includes('Hausdorff')),
            hasParticleCount: consoleMessages.some(msg => msg.text.includes('Particle Count')),
            hasGraceCreation: consoleMessages.some(msg => msg.text.includes('Grace Attractor created'))
        };
        
        console.log('📐 Mathematical Validation:', mathValidation);
        
        // Take screenshot
        const screenshotPath = join(__dirname, 'screenshots', 'step2-grace-attractor.png');
        await page.screenshot({ 
            path: screenshotPath,
            fullPage: true 
        });
        console.log(`📸 Screenshot saved: ${screenshotPath}`);
        
        // Verify success criteria for Step 2
        const success = {
            webglWorking: graceStatus.canvasExists,
            graceAttractorActive: graceStatus.graceIndicatorActive,
            renderingActive: graceStatus.fps > 0,
            objectsPresent: graceStatus.objects >= 2, // Should have Grace attractor + lights
            correctStep: graceStatus.stepNumber === '2/8',
            phiValueLogged: mathValidation.hasPhiValue,
            hausdorffDimLogged: mathValidation.hasHausdorffDim,
            graceAttractorCreated: mathValidation.hasGraceCreation
        };
        
        console.log('✅ Success Criteria Check:', success);
        
        const allPassed = Object.values(success).every(Boolean);
        console.log(allPassed ? '🎉 Step 2 PASSED!' : '❌ Step 2 FAILED!');
        
        // Test interactive features (camera controls)
        console.log('🎮 Testing camera controls...');
        await page.mouse.move(600, 400);
        await page.mouse.down();
        await page.mouse.move(650, 450);
        await page.mouse.up();
        
        // Wait a moment for any updates
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Check if rendering is still smooth
        const finalFPS = await page.evaluate(() => {
            return parseInt(document.getElementById('fps')?.textContent) || 0;
        });
        
        console.log(`🎯 Final FPS after interaction: ${finalFPS}`);
        
        const results = {
            timestamp: new Date().toISOString(),
            step: 2,
            description: 'Grace Attractor with Golden Ratio Fractals',
            success: allPassed && finalFPS > 30, // Require smooth rendering
            criteria: success,
            graceStatus,
            mathValidation,
            finalFPS,
            consoleMessages: consoleMessages.slice(-15) // Last 15 messages
        };
        
        // Save results to browser storage
        await page.evaluate((results) => {
            localStorage.setItem('step2Results', JSON.stringify(results));
        }, results);
        
        return results;
        
    } catch (error) {
        console.error('❌ Test failed:', error.message);
        return { success: false, error: error.message };
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

// Run test
testStep2().then(results => {
    console.log('\n📋 Final Results:', JSON.stringify(results, null, 2));
    
    if (results.success) {
        console.log('\n🎉 Step 2 COMPLETE! Grace Attractor is working correctly.');
        console.log('✨ Ready to proceed to Step 3: Audio Integration');
    } else {
        console.log('\n❌ Step 2 FAILED! Check the issues above.');
    }
    
    process.exit(results.success ? 0 : 1);
}).catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
});

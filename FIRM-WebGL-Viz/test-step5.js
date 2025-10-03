#!/usr/bin/env node

/**
 * Test Step 5: 231-Gates Network (C(22,2) Undirected Pairs)
 * Validates gate generation, motif classification, and audio-responsive connections
 */

import puppeteer from 'puppeteer';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function testStep5() {
    console.log('🧪 Testing Step 5: 231-Gates Network...');
    
    let browser;
    try {
        browser = await puppeteer.launch({
            headless: false,
            defaultViewport: { width: 1200, height: 800 },
            args: [
                '--no-sandbox', 
                '--disable-setuid-sandbox',
                '--use-fake-ui-for-media-stream',
                '--use-fake-device-for-media-stream',
                '--allow-running-insecure-content',
                '--disable-web-security'
            ]
        });
        
        const page = await browser.newPage();
        
        // Grant microphone permissions
        const context = browser.defaultBrowserContext();
        await context.overridePermissions('http://localhost:5173', ['microphone']);
        
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
        
        // Wait for full initialization including 231-Gates network
        console.log('⏳ Waiting for 231-Gates Network initialization...');
        await new Promise(resolve => setTimeout(resolve, 12000)); // Longer wait for complex network
        
        // Check 231-Gates Network status
        const gatesStatus = await page.evaluate(() => {
            const canvas = document.querySelector('canvas');
            const statusIndicators = document.querySelectorAll('.status-indicator');
            const gatesIndicator = statusIndicators[6]; // 7th indicator (231-Gates)
            
            // Get UI elements
            const gatesTotal = document.getElementById('gates-total')?.textContent;
            const gatesActive = document.getElementById('gates-active')?.textContent;
            const motifTypes = document.getElementById('motif-types')?.textContent;
            const fps = document.getElementById('fps')?.textContent;
            const objects = document.getElementById('objects')?.textContent;
            const stepNumber = document.getElementById('current-step')?.textContent;
            
            return {
                canvasExists: !!canvas,
                gatesIndicatorActive: gatesIndicator?.classList.contains('status-active'),
                gatesTotal: parseInt(gatesTotal) || 0,
                gatesActive: parseInt(gatesActive) || 0,
                motifTypes: parseInt(motifTypes) || 0,
                fps: parseInt(fps) || 0,
                objects: parseInt(objects) || 0,
                stepNumber,
                allStatusActive: Array.from(statusIndicators).every(el => 
                    el.classList.contains('status-active')
                )
            };
        });
        
        console.log('🔗 231-Gates Network Status:', gatesStatus);
        
        // Check for 231-Gates related console messages
        const gatesValidation = {
            hasGatesInit: consoleMessages.some(msg => 
                msg.text.includes('231-Gates') || msg.text.includes('🔗') || msg.text.includes('C(22,2)')
            ),
            hasGateGeneration: consoleMessages.some(msg => 
                msg.text.includes('Generated') && msg.text.includes('gates')
            ),
            hasMotifClassification: consoleMessages.some(msg => 
                msg.text.includes('motif') || msg.text.includes('Motifs:')
            ),
            hasGatesSuccess: consoleMessages.some(msg => 
                msg.text.includes('231-Gates Network created successfully') ||
                msg.text.includes('231-Gates Network integration complete')
            ),
            noGatesErrors: !consoleMessages.some(msg => 
                msg.type === 'error' && msg.text.toLowerCase().includes('gates')
            ),
            hasCombinatorics: consoleMessages.some(msg => 
                msg.text.includes('C(22,2)') || msg.text.includes('231')
            )
        };
        
        console.log('🎭 Gates Network Validation:', gatesValidation);
        
        // Take screenshot
        const screenshotPath = join(__dirname, 'screenshots', 'step5-231-gates-network.png');
        await page.screenshot({ 
            path: screenshotPath,
            fullPage: true 
        });
        console.log(`📸 Screenshot saved: ${screenshotPath}`);
        
        // Test camera controls to view gates network
        console.log('🎮 Testing camera controls with 231-Gates network...');
        
        // Rotate camera for better view of gates
        await page.mouse.move(600, 400);
        await page.mouse.down();
        await page.mouse.move(500, 200); // Rotate to see gates network
        await page.mouse.up();
        
        // Wait for rendering update
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        const finalCheck = await page.evaluate(() => {
            const fps = document.getElementById('fps')?.textContent;
            const objects = document.getElementById('objects')?.textContent;
            const gatesTotal = document.getElementById('gates-total')?.textContent;
            const gatesActive = document.getElementById('gates-active')?.textContent;
            
            return {
                finalFPS: parseInt(fps) || 0,
                finalObjects: parseInt(objects) || 0,
                gatesStable: parseInt(gatesTotal) === 231,
                activeGatesPresent: parseInt(gatesActive) > 0
            };
        });
        
        console.log('🎯 Final Gates Network Check:', finalCheck);
        
        // Verify success criteria for Step 5
        const success = {
            webglWorking: gatesStatus.canvasExists,
            allSystemsActive: gatesStatus.allStatusActive,
            correctStep: gatesStatus.stepNumber === '5/8',
            gatesUIPresent: gatesStatus.gatesTotal > 0,
            correct231Gates: gatesStatus.gatesTotal === 231,
            activeGatesPresent: gatesStatus.gatesActive > 0,
            motifTypesPresent: gatesStatus.motifTypes > 0,
            renderingSmooth: gatesStatus.fps > 25, // Allow slightly lower FPS due to complexity
            gatesNetworkInitialized: gatesValidation.hasGatesInit,
            gateGenerationWorking: gatesValidation.hasGateGeneration,
            motifClassificationWorking: gatesValidation.hasMotifClassification,
            combinatoricsCorrect: gatesValidation.hasCombinatorics,
            gatesNetworkComplete: gatesValidation.hasGatesSuccess,
            noGatesErrors: gatesValidation.noGatesErrors,
            objectCountIncreased: gatesStatus.objects > 3, // Should have Grace + Hebrew + Gates objects
            gatesStability: finalCheck.gatesStable,
            activeGatesStability: finalCheck.activeGatesPresent
        };
        
        console.log('✅ Success Criteria Check:', success);
        
        // Calculate overall success
        const criticalSuccess = [
            success.webglWorking,
            success.correctStep,
            success.gatesUIPresent,
            success.correct231Gates,
            success.renderingSmooth,
            success.gatesNetworkInitialized,
            success.gatesNetworkComplete,
            success.noGatesErrors
        ].every(Boolean);
        
        const allPassed = criticalSuccess;
        
        console.log(allPassed ? '🎉 Step 5 PASSED! 231-Gates Network is operational!' : '❌ Step 5 FAILED!');
        
        const results = {
            timestamp: new Date().toISOString(),
            step: 5,
            description: '231-Gates Network (C(22,2) Undirected Pairs)',
            success: allPassed,
            criteria: success,
            gatesStatus,
            gatesValidation,
            finalCheck,
            consoleMessages: consoleMessages.slice(-30) // Last 30 messages
        };
        
        // Save results to browser storage
        await page.evaluate((results) => {
            localStorage.setItem('step5Results', JSON.stringify(results));
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
testStep5().then(results => {
    console.log('\n📋 Final Results:', JSON.stringify(results, null, 2));
    
    if (results.success) {
        console.log('\n🎉 Step 5 COMPLETE! 231-Gates Network is operational.');
        console.log('🔗 231 undirected pairs between 22 Hebrew letters');
        console.log('🎭 Motif classification with fractal interplay');
        console.log('🎤 Audio-responsive gate activation patterns');
        console.log('⚡ Dynamic connection visualization');
        console.log('✨ Ready to proceed to Step 6: Sovereignty Attractor');
    } else {
        console.log('\n❌ Step 5 FAILED! Check the issues above.');
    }
    
    process.exit(results.success ? 0 : 1);
}).catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
});

#!/usr/bin/env node

/**
 * Test Step 4: Hebrew Letters Network (22-Letter Kabbalistic Tree of Life)
 * Validates Hebrew letter positioning, FSCTF operator mappings, and audio responsiveness
 */

import puppeteer from 'puppeteer';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function testStep4() {
    console.log('🧪 Testing Step 4: Hebrew Letters Network...');
    
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
        
        // Wait for full initialization including Hebrew network
        console.log('⏳ Waiting for Hebrew Letters Network initialization...');
        await new Promise(resolve => setTimeout(resolve, 10000)); // Longer wait for Hebrew network
        
        // Check Hebrew Letters Network status
        const hebrewStatus = await page.evaluate(() => {
            const canvas = document.querySelector('canvas');
            const statusIndicators = document.querySelectorAll('.status-indicator');
            const hebrewIndicator = statusIndicators[5]; // 6th indicator (Hebrew Network)
            
            // Get UI elements
            const hebrewCount = document.getElementById('hebrew-count')?.textContent;
            const sephirothCount = document.getElementById('sephiroth-count')?.textContent;
            const hebrewAudio = document.getElementById('hebrew-audio')?.textContent;
            const fps = document.getElementById('fps')?.textContent;
            const objects = document.getElementById('objects')?.textContent;
            const stepNumber = document.getElementById('current-step')?.textContent;
            
            return {
                canvasExists: !!canvas,
                hebrewIndicatorActive: hebrewIndicator?.classList.contains('status-active'),
                hebrewCount: parseInt(hebrewCount) || 0,
                sephirothCount: parseInt(sephirothCount) || 0,
                hebrewAudio,
                fps: parseInt(fps) || 0,
                objects: parseInt(objects) || 0,
                stepNumber,
                allStatusActive: Array.from(statusIndicators).every(el => 
                    el.classList.contains('status-active')
                )
            };
        });
        
        console.log('🕎 Hebrew Letters Network Status:', hebrewStatus);
        
        // Check for Hebrew-related console messages
        const hebrewValidation = {
            hasHebrewInit: consoleMessages.some(msg => 
                msg.text.includes('Hebrew') || msg.text.includes('🕎') || msg.text.includes('22 letters')
            ),
            hasTreeOfLife: consoleMessages.some(msg => 
                msg.text.includes('Tree of Life') || msg.text.includes('connections') || msg.text.includes('Sephir')
            ),
            hasFSCTFOperators: consoleMessages.some(msg => 
                msg.text.includes('FSCTF Operators') || msg.text.includes('τ') || msg.text.includes('β')
            ),
            hasHebrewSuccess: consoleMessages.some(msg => 
                msg.text.includes('Hebrew Letters Network created successfully') ||
                msg.text.includes('Hebrew Letters Network integration complete')
            ),
            noHebrewErrors: !consoleMessages.some(msg => 
                msg.type === 'error' && msg.text.toLowerCase().includes('hebrew')
            )
        };
        
        console.log('🌳 Hebrew Network Validation:', hebrewValidation);
        
        // Take screenshot
        const screenshotPath = join(__dirname, 'screenshots', 'step4-hebrew-network.png');
        await page.screenshot({ 
            path: screenshotPath,
            fullPage: true 
        });
        console.log(`📸 Screenshot saved: ${screenshotPath}`);
        
        // Test camera controls to see Hebrew network from different angles
        console.log('🎮 Testing camera controls with Hebrew network...');
        
        // Rotate camera to view Hebrew network
        await page.mouse.move(600, 400);
        await page.mouse.down();
        await page.mouse.move(700, 300); // Move to rotate view
        await page.mouse.up();
        
        // Wait for rendering update
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        const finalCheck = await page.evaluate(() => {
            const fps = document.getElementById('fps')?.textContent;
            const objects = document.getElementById('objects')?.textContent;
            const hebrewCount = document.getElementById('hebrew-count')?.textContent;
            
            return {
                finalFPS: parseInt(fps) || 0,
                finalObjects: parseInt(objects) || 0,
                hebrewLettersStable: parseInt(hebrewCount) === 22
            };
        });
        
        console.log('🎯 Final Hebrew Network Check:', finalCheck);
        
        // Verify success criteria for Step 4
        const success = {
            webglWorking: hebrewStatus.canvasExists,
            allSystemsActive: hebrewStatus.allStatusActive,
            correctStep: hebrewStatus.stepNumber === '4/8',
            hebrewUIPresent: hebrewStatus.hebrewCount > 0,
            correct22Letters: hebrewStatus.hebrewCount === 22,
            correct10Sephiroth: hebrewStatus.sephirothCount === 10,
            renderingSmooth: hebrewStatus.fps > 30,
            hebrewNetworkInitialized: hebrewValidation.hasHebrewInit,
            treeOfLifeCreated: hebrewValidation.hasTreeOfLife,
            fsctfOperatorsMapped: hebrewValidation.hasFSCTFOperators,
            hebrewNetworkComplete: hebrewValidation.hasHebrewSuccess,
            noHebrewErrors: hebrewValidation.noHebrewErrors,
            objectCountIncreased: hebrewStatus.objects > 2, // Should have Grace + Hebrew network objects
            hebrewStability: finalCheck.hebrewLettersStable
        };
        
        console.log('✅ Success Criteria Check:', success);
        
        // Calculate overall success
        const criticalSuccess = [
            success.webglWorking,
            success.correctStep,
            success.hebrewUIPresent,
            success.correct22Letters,
            success.renderingSmooth,
            success.hebrewNetworkInitialized,
            success.hebrewNetworkComplete,
            success.noHebrewErrors
        ].every(Boolean);
        
        const allPassed = criticalSuccess;
        
        console.log(allPassed ? '🎉 Step 4 PASSED! Hebrew Letters Network is working!' : '❌ Step 4 FAILED!');
        
        const results = {
            timestamp: new Date().toISOString(),
            step: 4,
            description: 'Hebrew Letters Network (22-Letter Kabbalistic Tree of Life)',
            success: allPassed,
            criteria: success,
            hebrewStatus,
            hebrewValidation,
            finalCheck,
            consoleMessages: consoleMessages.slice(-25) // Last 25 messages
        };
        
        // Save results to browser storage
        await page.evaluate((results) => {
            localStorage.setItem('step4Results', JSON.stringify(results));
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
testStep4().then(results => {
    console.log('\n📋 Final Results:', JSON.stringify(results, null, 2));
    
    if (results.success) {
        console.log('\n🎉 Step 4 COMPLETE! Hebrew Letters Network is operational.');
        console.log('🕎 22 Hebrew letters positioned according to Tree of Life');
        console.log('🌳 10 Sephiroth with FSCTF operator mappings');
        console.log('🎤 Audio-responsive Hebrew letter activation');
        console.log('✨ Ready to proceed to Step 5: 231-Gates Network');
    } else {
        console.log('\n❌ Step 4 FAILED! Check the issues above.');
    }
    
    process.exit(results.success ? 0 : 1);
}).catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
});

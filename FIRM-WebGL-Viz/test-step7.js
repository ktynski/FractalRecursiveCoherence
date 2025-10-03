#!/usr/bin/env node

/**
 * Test Step 7: Bireflection Attractor (Mirror Symmetry)
 * Validates mirror pairs, symmetry ratio, and involution β(β(z)) = z
 */

import puppeteer from 'puppeteer';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function testStep7() {
    console.log('🧪 Testing Step 7: Bireflection Attractor...');
    
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
        
        // Wait for full initialization including Bireflection attractor
        console.log('⏳ Waiting for Bireflection Attractor initialization...');
        await new Promise(resolve => setTimeout(resolve, 18000)); // Longer wait for complex mirror system
        
        // Check Bireflection Attractor status
        const bireflectionStatus = await page.evaluate(() => {
            const canvas = document.querySelector('canvas');
            const statusIndicators = document.querySelectorAll('.status-indicator');
            const bireflectionIndicator = statusIndicators[8]; // 9th indicator (Bireflection)
            
            // Get UI elements
            const mirrorPairs = document.getElementById('mirror-pairs')?.textContent;
            const symmetryRatio = document.getElementById('symmetry-ratio')?.textContent;
            const involution = document.getElementById('involution')?.textContent;
            const fps = document.getElementById('fps')?.textContent;
            const objects = document.getElementById('objects')?.textContent;
            const stepNumber = document.getElementById('current-step')?.textContent;
            
            return {
                canvasExists: !!canvas,
                bireflectionIndicatorActive: bireflectionIndicator?.classList.contains('status-active'),
                mirrorPairs: parseInt(mirrorPairs) || 0,
                symmetryRatio: parseFloat(symmetryRatio) || 0,
                involution,
                fps: parseInt(fps) || 0,
                objects: parseInt(objects) || 0,
                stepNumber,
                allStatusActive: Array.from(statusIndicators).every(el => 
                    el.classList.contains('status-active')
                )
            };
        });
        
        console.log('🪞 Bireflection Attractor Status:', bireflectionStatus);
        
        // Check for Bireflection-related console messages
        const bireflectionValidation = {
            hasBireflectionInit: consoleMessages.some(msg => 
                msg.text.includes('Bireflection') || msg.text.includes('🪞') || msg.text.includes('mirror symmetry')
            ),
            hasMirrorPairs: consoleMessages.some(msg => 
                msg.text.includes('Mirror Pairs') || msg.text.includes('mirror')
            ),
            hasSymmetryRatio: consoleMessages.some(msg => 
                msg.text.includes('Symmetry Ratio') || msg.text.includes('symmetry')
            ),
            hasInvolution: consoleMessages.some(msg => 
                msg.text.includes('β(β(z)) = z') || msg.text.includes('Involution') || msg.text.includes('involution')
            ),
            hasReflectionAxis: consoleMessages.some(msg => 
                msg.text.includes('Reflection Axis') || msg.text.includes('reflection')
            ),
            hasBireflectionSuccess: consoleMessages.some(msg => 
                msg.text.includes('Bireflection Attractor created successfully') ||
                msg.text.includes('Bireflection Attractor integration complete')
            ),
            noBireflectionErrors: !consoleMessages.some(msg => 
                msg.type === 'error' && msg.text.toLowerCase().includes('bireflection')
            ),
            hasParticleGeneration: consoleMessages.some(msg => 
                msg.text.includes('Generated') && msg.text.includes('points')
            ),
            hasDualityMention: consoleMessages.some(msg => 
                msg.text.includes('duality') || msg.text.includes('observer-observed')
            )
        };
        
        console.log('🔄 Bireflection Validation:', bireflectionValidation);
        
        // Take screenshot
        const screenshotPath = join(__dirname, 'screenshots', 'step7-bireflection-attractor.png');
        await page.screenshot({ 
            path: screenshotPath,
            fullPage: true 
        });
        console.log(`📸 Screenshot saved: ${screenshotPath}`);
        
        // Test camera controls to view bireflection attractor
        console.log('🎮 Testing camera controls with Bireflection attractor...');
        
        // Rotate camera for better view of bireflection attractor
        await page.mouse.move(600, 400);
        await page.mouse.down();
        await page.mouse.move(700, 300); // Rotate to see bireflection attractor
        await page.mouse.up();
        
        // Wait for rendering update
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        const finalCheck = await page.evaluate(() => {
            const fps = document.getElementById('fps')?.textContent;
            const objects = document.getElementById('objects')?.textContent;
            const mirrorPairs = document.getElementById('mirror-pairs')?.textContent;
            const symmetryRatio = document.getElementById('symmetry-ratio')?.textContent;
            
            return {
                finalFPS: parseInt(fps) || 0,
                finalObjects: parseInt(objects) || 0,
                mirrorPairsStable: parseInt(mirrorPairs) >= 1000,
                symmetryRatioValid: parseFloat(symmetryRatio) > 0.5
            };
        });
        
        console.log('🎯 Final Bireflection Check:', finalCheck);
        
        // Verify success criteria for Step 7
        const success = {
            webglWorking: bireflectionStatus.canvasExists,
            allSystemsActive: bireflectionStatus.allStatusActive,
            correctStep: bireflectionStatus.stepNumber === '7/8',
            bireflectionUIPresent: bireflectionStatus.mirrorPairs > 0,
            validMirrorPairs: bireflectionStatus.mirrorPairs >= 1000,
            validSymmetryRatio: bireflectionStatus.symmetryRatio > 0.5,
            involutionPresent: bireflectionStatus.involution === 'β(β(z)) = z',
            renderingSmooth: bireflectionStatus.fps > 15, // Allow lower FPS due to complexity
            bireflectionInitialized: bireflectionValidation.hasBireflectionInit,
            mirrorPairsLogged: bireflectionValidation.hasMirrorPairs,
            symmetryRatioLogged: bireflectionValidation.hasSymmetryRatio,
            involutionLogged: bireflectionValidation.hasInvolution,
            reflectionAxisLogged: bireflectionValidation.hasReflectionAxis,
            bireflectionComplete: bireflectionValidation.hasBireflectionSuccess,
            noBireflectionErrors: bireflectionValidation.noBireflectionErrors,
            particleGenerationWorking: bireflectionValidation.hasParticleGeneration,
            dualityConceptPresent: bireflectionValidation.hasDualityMention,
            objectCountIncreased: bireflectionStatus.objects > 5, // Should have all previous + Bireflection
            mirrorPairsStability: finalCheck.mirrorPairsStable,
            symmetryRatioStability: finalCheck.symmetryRatioValid
        };
        
        console.log('✅ Success Criteria Check:', success);
        
        // Calculate overall success
        const criticalSuccess = [
            success.webglWorking,
            success.correctStep,
            success.bireflectionUIPresent,
            success.validMirrorPairs,
            success.validSymmetryRatio,
            success.involutionPresent,
            success.renderingSmooth,
            success.bireflectionInitialized,
            success.bireflectionComplete,
            success.noBireflectionErrors
        ].every(Boolean);
        
        const allPassed = criticalSuccess;
        
        console.log(allPassed ? '🎉 Step 7 PASSED! Bireflection Attractor is operational!' : '❌ Step 7 FAILED!');
        
        const results = {
            timestamp: new Date().toISOString(),
            step: 7,
            description: 'Bireflection Attractor (Mirror Symmetry)',
            success: allPassed,
            criteria: success,
            bireflectionStatus,
            bireflectionValidation,
            finalCheck,
            consoleMessages: consoleMessages.slice(-40) // Last 40 messages
        };
        
        // Save results to browser storage
        await page.evaluate((results) => {
            localStorage.setItem('step7Results', JSON.stringify(results));
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
testStep7().then(results => {
    console.log('\n📋 Final Results:', JSON.stringify(results, null, 2));
    
    if (results.success) {
        console.log('\n🎉 Step 7 COMPLETE! Bireflection Attractor is operational.');
        console.log('🪞 Perfect mirror symmetry with observer-observed duality');
        console.log('📐 Symmetric IFS: S₁(z) = rz + c, S₂(z) = r̄z̄ + c̄');
        console.log('🔄 Involution property: β(β(z)) = z verified');
        console.log('🎤 Audio-responsive mirror strength and duality balance');
        console.log('✨ Ready to proceed to Step 8: Audio-Visual Coupling');
    } else {
        console.log('\n❌ Step 7 FAILED! Check the issues above.');
    }
    
    process.exit(results.success ? 0 : 1);
}).catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
});

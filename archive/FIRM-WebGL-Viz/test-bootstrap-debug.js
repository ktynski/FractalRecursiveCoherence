import puppeteer from 'puppeteer';

async function testBootstrapDebug() {
    console.log('🔍 Testing Bootstrap Attractor Debug...');
    
    const browser = await puppeteer.launch({ 
        headless: false,
        devtools: true,
        args: ['--disable-web-security', '--disable-features=VizDisplayCompositor']
    });
    
    const page = await browser.newPage();
    
    // Clear cache and disable cache
    await page.setCacheEnabled(false);
    
    // Listen to console messages
    page.on('console', msg => {
        const text = msg.text();
        if (text.includes('PHASE TRANSITION') || 
            text.includes('Bootstrap') || 
            text.includes('performPhaseTransition') ||
            text.includes('selfOrganizeStructures')) {
            console.log('🎯 BOOTSTRAP DEBUG:', text);
        }
    });
    
    try {
        console.log('📱 Navigating to app with cache disabled...');
        await page.goto('http://localhost:5173', { 
            waitUntil: 'networkidle0',
            timeout: 30000 
        });
        
        console.log('⏳ Waiting for Bootstrap initialization...');
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        // Force a Bootstrap step by injecting code
        console.log('🚀 Forcing Bootstrap step...');
        await page.evaluate(() => {
            if (window.firmViz && window.firmViz.bootstrapAttractor) {
                console.log('🔧 Manually triggering Bootstrap step...');
                window.firmViz.bootstrapAttractor.creationEnergy = 1.0; // Force high energy
                window.firmViz.bootstrapAttractor.performBootstrapStep();
                console.log('📊 Bootstrap metrics after manual trigger:', 
                    window.firmViz.bootstrapAttractor.getBootstrapMetrics());
            } else {
                console.log('❌ Bootstrap attractor not found on window.firmViz');
                console.log('Available on window:', Object.keys(window));
            }
        });
        
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        console.log('📷 Taking debug screenshot...');
        await page.screenshot({ path: 'bootstrap-debug.png' });
        
    } catch (error) {
        console.error('❌ Debug test failed:', error.message);
    }
    
    console.log('🔍 Keeping browser open for manual inspection...');
    // Don't close browser for manual inspection
}

testBootstrapDebug().catch(console.error);

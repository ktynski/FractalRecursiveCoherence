import puppeteer from 'puppeteer';

(async () => {
  const browser = await puppeteer.launch({headless: 'new', args: ['--no-sandbox']});
  const page = await browser.newPage();
  await page.setViewport({width: 1920, height: 1080});
  
  const consoleLogs = [];
  const errors = [];
  
  page.on('console', msg => {
    const text = msg.text();
    consoleLogs.push(text);
    console.log('[CONSOLE]', text);
  });
  
  page.on('pageerror', err => {
    errors.push(err.message);
    console.log('[ERROR]', err.message);
  });
  
  console.log('Loading page...');
  await page.goto('http://localhost:8080', {waitUntil: 'networkidle0', timeout: 10000});
  
  console.log('Waiting for initialization...');
  await new Promise(resolve => setTimeout(resolve, 3000));
  
  console.log('Taking screenshot...');
  await page.screenshot({path: 'viewport_debug.png', fullPage: false});
  
  // Check canvas state
  console.log('\n=== CANVAS STATE ===');
  const canvasState = await page.evaluate(() => {
    const canvas = document.getElementById('canvas');
    if (!canvas) return {error: 'Canvas not found'};
    
    const rect = canvas.getBoundingClientRect();
    const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
    
    return {
      exists: true,
      width: canvas.width,
      height: canvas.height,
      styleWidth: canvas.style.width,
      styleHeight: canvas.style.height,
      displayWidth: rect.width,
      displayHeight: rect.height,
      visible: rect.width > 0 && rect.height > 0,
      hasGL: !!gl,
      glError: gl ? gl.getError() : 'No GL context',
      parent: canvas.parentElement ? canvas.parentElement.tagName : 'no parent',
      zIndex: canvas.style.zIndex || 'default'
    };
  });
  
  console.log(JSON.stringify(canvasState, null, 2));
  
  // Check if renderer actually called draw
  console.log('\n=== RENDER STATE ===');
  const renderState = await page.evaluate(() => {
    return {
      hasWindow: typeof window !== 'undefined',
      hasSystemState: typeof systemState !== 'undefined',
      frameCount: typeof systemState !== 'undefined' ? systemState.frameCount : 'N/A',
      hasField: typeof systemState !== 'undefined' && systemState.cliffordField ? true : false,
      fieldType: typeof systemState !== 'undefined' && systemState.cliffordField ? typeof systemState.cliffordField : 'N/A'
    };
  });
  
  console.log(JSON.stringify(renderState, null, 2));
  
  console.log('\n=== ERRORS ===');
  console.log(errors.length ? errors : 'No errors');
  
  await browser.close();
  console.log('\nScreenshot saved to viewport_debug.png');
})();


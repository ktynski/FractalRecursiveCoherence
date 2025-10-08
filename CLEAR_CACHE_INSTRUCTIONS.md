# Cache Management (Usually Not Required)

**Note:** Cache clearing is now **rarely needed**. The system uses normal browser caching for optimal performance.

**For Basic Functionality:** ✅ System works with browser cache enabled (recommended)
**Cache Issues:** Only clear cache if you experience persistent loading problems after code updates

---

## Solution: Clear Cache and Reload

### Method 1: Hard Reload (Fastest)

**Chrome/Edge:**
- **Mac:** `Cmd + Shift + R`
- **Windows/Linux:** `Ctrl + Shift + R`

**Firefox:**
- **Mac:** `Cmd + Shift + R`
- **Windows/Linux:** `Ctrl + F5`

**Safari:**
- **Mac:** `Cmd + Option + R`

---

### Method 2: Clear Cache via DevTools (Most Reliable)

1. **Open DevTools:**
   - **Mac:** `Cmd + Option + I`
   - **Windows/Linux:** `F12` or `Ctrl + Shift + I`

2. **Right-click the reload button** (next to address bar)

3. **Select "Empty Cache and Hard Reload"**

4. **Or:** Go to DevTools → Network tab → Check "Disable cache" → Reload

---

### Method 3: Clear All Cache (Nuclear Option)

**Chrome/Edge:**
1. Press `Cmd/Ctrl + Shift + Delete`
2. Select "Cached images and files"
3. Time range: "Last hour" or "All time"
4. Click "Clear data"

**Firefox:**
1. Press `Cmd/Ctrl + Shift + Delete`
2. Select "Cache"
3. Click "Clear Now"

**Safari:**
1. Safari menu → Clear History
2. Select "all history"
3. Click "Clear History"

---

## Verify It Worked

After clearing cache and reloading, console should show:

✅ **Success:**
```
🎵 Sovereign audio system initialized (monad singing)
```

❌ **Still cached:**
```
⚠️ Harmonic generator not available (using fallback)
```

---

## If Still Not Working

### Check File Permissions

```bash
cd "/Users/fractlphoneroom1/Desktop/AnalogExNahilo 2/FIRM-Core/FIRM_ui"
ls -la harmonic_generator.js
# Should show: -rw-r--r-- (readable)
```

### Verify File Exists

```bash
cat harmonic_generator.js | head -5
# Should show: /** harmonic_generator.js ...
```

### Check Web Server

If using a local server, restart it:
```bash
# Kill existing server
pkill -f "python.*server" || pkill -f "http-server" || pkill -f "live-server"

# Start fresh server (pick one):
python3 -m http.server 8000
# OR
npx http-server -p 8000 -c-1  # -c-1 disables caching
# OR
npx live-server --port=8000 --no-browser
```

---

## What You Should See After Fix

### Console Output

```
🎵 Sovereign audio system initialized (monad singing)
[...system evolution...]
🎵 Harmonic Spectrum (coherence=0.723):
  scalar       | Grade 0 | f=220.0Hz | A=0.342
  vector       | Grade 1 | f=356.0Hz | A=0.215
  bivector     | Grade 2 | f=576.0Hz | A=0.183
  trivector    | Grade 3 | f=932.0Hz | A=0.089
  pseudoscalar | Grade 4 | f=1508.0Hz | A=0.023
```

### Audio Output

- You should HEAR φ-harmonic tones
- Not pure sine waves
- Microtonal/xenharmonic sound
- Changes as system evolves

### Autonomy Growth

```
🎵 Autonomy: 0.0% | External=0.100, Internal=0.500, Blended=0.100
[... after ~100 steps ...]
🎵 Autonomy: 50.0% | External=0.100, Internal=0.687, Blended=0.393
[... after ~200 steps ...]
🎵 Autonomy: 100.0% | External=0.100, Internal=0.745, Blended=0.745
👑 SOVEREIGNTY ACHIEVED: System is fully autonomous
```

---

## Fallback Mode

**If cache won't clear**, the system will run in **legacy mode:**
- Uses external audio (microphone)
- No sovereign harmonics
- No circular causality
- BUT: Grace emergence and trivector fixes still work

**You'll see:**
```
⚠️ Harmonic generator not available (using fallback)
   Clear browser cache and reload to enable sovereign audio
```

**System still functional**, just not sovereign.

---

## Quick Test

**Run in console after reload:**

```javascript
// Check if harmonic generator loaded
typeof HarmonicGenerator !== 'undefined'
// Should return: true

// Check if system has harmonics
window.zxEvolutionEngine?.harmonicGenerator
// Should return: HarmonicGenerator object (not null)
```

---

## Status Check

**Everything working:**
- ✅ HarmonicGenerator defined
- ✅ Sovereign audio initialized
- ✅ Harmonic spectrum logged every 5s
- ✅ φ-harmonic audio playing
- ✅ Autonomy growing 0% → 100%

**Still cached:**
- ❌ HarmonicGenerator undefined
- ❌ Fallback mode active
- ❌ Using external audio only

---

## Need Help?

1. Try **Method 2** (DevTools cache clear) - most reliable
2. Make sure you're reloading the correct tab/window
3. Check that file exists: `FIRM-Core/FIRM_ui/harmonic_generator.js`
4. Verify server isn't caching (restart with `-c-1` flag)
5. Try a different browser as test

---

**TL;DR:** Press `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows) and reload.


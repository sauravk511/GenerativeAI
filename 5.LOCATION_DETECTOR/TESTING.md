# 🧪 Testing Guide - Location Detection

Complete testing scenarios to verify all features work correctly.

## Test Environment Setup

Before testing, ensure servers are running:

```bash
# Terminal 1
cd backend && python main.py

# Terminal 2
cd frontend && python -m http.server 8001
```

Then open **http://localhost:8001** in your browser.

---

## Test Case 1: GPS Detection (Permission Allowed) ✅

**Objective:** Verify GPS coordinates are detected and reverse geocoded correctly.

### Steps:

1. Open http://localhost:8001
2. Click **"🔍 Detect Location"**
3. **Allow** location permission (when browser prompts)
4. Wait 3-5 seconds for GPS lock

### Expected Results:

- ✅ Status badge changes to **"GPS Detected"** (green badge)
- ✅ Latitude/longitude populated (e.g., `37.7749, -122.4194`)
- ✅ City name appears (e.g., `San Francisco`)
- ✅ Region/State appears (e.g., `California`)
- ✅ Accuracy shown in meters (e.g., `±15 meters`)
- ✅ Source shows **"🛰️ GPS (High Accuracy)"`**
- ✅ Google Maps link appears (clickable)
- ✅ `backend/location_output.json` contains:
  ```json
  {
    "source": "gps",
    "latitude": 37.7749,
    "longitude": -122.4194,
    "accuracy": 15,
    ...
  }
  ```

### Notes:

- Accuracy depends on GPS signal (better outdoors, satellite coverage)
- City accuracy very high (within a few meters)
- First detection may take 5-10 seconds (GPS lock)

---

## Test Case 2: IP Fallback (Permission Denied) ⚠️

**Objective:** Verify system gracefully falls back to IP-based geolocation when GPS is denied.

### Steps:

1. Open http://localhost:8001 (refresh if needed)
2. Click **"🔍 Detect Location"**
3. **Deny** permission when browser prompts
4. Wait 2-3 seconds

### Expected Results:

- ✅ Status badge changes to **"IP Fallback"** (blue badge)
- ✅ Warning message: `"⚠️ Location Permission Denied: Using IP-based geolocation..."`
- ✅ City name appears (likely correct)
- ✅ Region appears (may be less accurate)
- ✅ Latitude/longitude shown (approximate, ±5-10km error)
- ✅ Accuracy field shows **"Not available (IP-based)"**
- ✅ Source shows **"🌐 IP-Based (Fallback)"`**
- ✅ No accuracy meter displayed
- ✅ `backend/location_output.json` contains:
  ```json
  {
    "source": "ip",
    "latitude": 37.78,
    "longitude": -122.41,
    "accuracy": null,
    ...
  }
  ```

### Notes:

- IP-based detection is fast (< 1 second)
- City is usually correct
- Accuracy is ±5-10km (neighborhood-level)
- Useful fallback when GPS unavailable

---

## Test Case 3: Manual Entry (Fallback) ⌨️

**Objective:** Verify manual location entry works when automatic detection fails.

### Steps:

1. Open http://localhost:8001
2. Click **"⌨️ Manual Entry"** button
3. Fill in form:
   - **City:** `Tokyo` (required)
   - **Region:** `Tokyo`
   - **Country:** `Japan`
4. Click **"✓ Submit"**

### Expected Results:

- ✅ Form disappears
- ✅ Status badge shows **"Manual"** (red badge)
- ✅ Location data displays:
  - City: `Tokyo`
  - Region: `Tokyo`
  - Country: `Japan`
  - Latitude: `—` (empty, since no coordinates)
  - Longitude: `—` (empty)
  - Accuracy: `—` (empty)
  - Source: **`⌨️ Manual Entry`**
- ✅ `backend/location_output.json` contains:
  ```json
  {
    "source": "manual",
    "city": "Tokyo",
    "region": "Tokyo",
    "country": "Japan",
    "latitude": null,
    "longitude": null,
    ...
  }
  ```

### Notes:

- Manual entry is the final safety net
- No user should ever be blocked
- Useful when automatic detection fails

---

## Test Case 4: Cancel Manual Entry ✕

**Objective:** Verify manual entry form can be cancelled.

### Steps:

1. Click **"⌨️ Manual Entry"**
2. Enter some data
3. Click **"✕ Cancel"** button

### Expected Results:

- ✅ Manual entry form disappears
- ✅ Previously entered data is cleared
- ✅ UI returns to normal state

---

## Test Case 5: Multiple Detections 🔄

**Objective:** Verify location can be re-detected and file is updated.

### Steps:

1. Detect location with GPS (Test Case 1)
2. Verify `location_output.json` has GPS data
3. Click **"🔍 Detect Location"** again
4. Allow permission
5. Check `location_output.json`

### Expected Results:

- ✅ New detection overwrites previous data
- ✅ Timestamp is updated to current time
- ✅ All fields reflect new detection
- ✅ File contains only latest location (not a log)

---

## Test Case 6: API Direct Testing (Curl)

**Objective:** Verify backend API endpoints work correctly.

### Test 6A: GPS Coordinates → Reverse Geocoding

```bash
curl -X POST http://localhost:8000/api/location/detect \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 35.6762,
    "longitude": 139.6503,
    "accuracy": 20
  }'
```

**Expected Response:**
```json
{
  "latitude": 35.6762,
  "longitude": 139.6503,
  "accuracy": 20,
  "city": "Tokyo",
  "region": "Tokyo",
  "country": "Japan",
  "source": "gps",
  "timestamp": "2026-02-09T12:34:56.789Z"
}
```

### Test 6B: Empty Coordinates → IP Fallback

```bash
curl -X POST http://localhost:8000/api/location/detect \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": null,
    "longitude": null,
    "accuracy": null
  }'
```

**Expected Response:** Either IP-based location or error (depending on network).

### Test 6C: Manual Location Submission

```bash
curl -X POST "http://localhost:8000/api/location/manual?city=NewYork&region=NewYork&country=USA"
```

**Expected Response:**
```json
{
  "latitude": null,
  "longitude": null,
  "accuracy": null,
  "city": "NewYork",
  "region": "NewYork",
  "country": "USA",
  "source": "manual",
  "timestamp": "2026-02-09T12:34:56.789Z"
}
```

### Test 6D: Retrieve Last Location

```bash
curl http://localhost:8000/api/location/last
```

**Expected Response:** Most recent location from any source.

### Test 6E: Health Check

```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "Location Detection API"
}
```

---

## Test Case 7: Mobile Browser Testing

**Objective:** Verify location detection works on mobile devices.

### Setup with Local Network:

```bash
# Find your Mac's IP
ifconfig | grep inet
# Example: 192.168.1.100

# Make sure servers are running on all interfaces
# (Already done: 0.0.0.0)
```

### On Mobile Device:

1. Connect to **same Wi-Fi** as Mac
2. Open: `http://192.168.1.100:8001` (replace with your IP)
3. Click **"🔍 Detect Location"**
4. Allow location permission
5. Phone's OS will use best available source:
   - GPS (outdoors, high accuracy)
   - Wi-Fi positioning (indoors)
   - Network triangulation (fallback)

### Expected Results:

- ✅ App loads and displays correctly on mobile screen
- ✅ Location detected using phone's GPS
- ✅ City/region appears accurately
- ✅ Google Maps link works
- ✅ Manual entry works on mobile keyboard
- ✅ All buttons are touch-friendly (48px minimum)

### Advanced: Using ngrok for Internet Tunnel

```bash
brew install ngrok
ngrok http 8001
```

Visit the ngrok URL (`https://abc123.ngrok.io`) from any mobile device, anywhere.

---

## Test Case 8: Edge Cases

### 8A: Very Accurate GPS (Indoors with Good Signal)

**Steps:**
1. Stand near a window with clear sky view
2. Click "Detect Location"
3. Allow permission
4. Wait for GPS lock

**Expected:** Accuracy should be ±5-10 meters.

### 8B: Poor GPS Signal (Dense Urban Area)

**Steps:**
1. Try GPS in concrete-heavy area
2. Click "Detect Location"
3. If timeout occurs, allow fallback

**Expected:** GPS may timeout; system falls back to IP/manual.

### 8C: Rapid Re-Detection

**Steps:**
1. Click "Detect Location" multiple times quickly
2. Cancel between attempts

**Expected:**
- Previous request should be canceled
- Only latest request completes
- No race conditions in UI

### 8D: Very Large Coordinates

**API Test:**
```bash
curl -X POST http://localhost:8000/api/location/detect \
  -H "Content-Type: application/json" \
  -d '{"latitude": 85.0, "longitude": 180.0, "accuracy": 10}'
```

**Expected:** Should gracefully handle without errors.

### 8E: Empty Manual Entry

**Steps:**
1. Click "⌨️ Manual Entry"
2. Leave City field empty
3. Click "✓ Submit"

**Expected:** Error message: "Please enter a city name"

---

## Test Case 9: Browser Compatibility

Test on different browsers to ensure compatibility:

| Browser | Platform | Expected |
|---------|----------|----------|
| Chrome | macOS | ✅ Full support |
| Safari | macOS | ✅ Full support |
| Firefox | macOS | ✅ Full support |
| Edge | macOS | ✅ Full support |
| Chrome | iOS | ✅ Full support |
| Safari | iOS | ✅ Full support |
| Chrome | Android | ✅ Full support |

### Notes:

- All modern browsers support Geolocation API
- HTTPS required in production (not localhost)
- Incognito mode may require permission re-confirmation

---

## Test Case 10: Reverse Geocoding Accuracy

**Objective:** Verify reverse geocoding returns correct city/region.

### Famous Coordinates to Test:

| Location | Latitude | Longitude | Expected City |
|----------|----------|-----------|---|
| Eiffel Tower | 48.8584 | 2.2945 | Paris |
| Big Ben | 51.4975 | -0.1245 | London |
| Statue of Liberty | 40.6892 | -74.0445 | New York |
| Tokyo Tower | 35.6762 | 139.6503 | Tokyo |
| Sydney Opera House | -33.8568 | 151.2153 | Sydney |

### Test Command:

```bash
curl -X POST http://localhost:8000/api/location/detect \
  -H "Content-Type: application/json" \
  -d '{"latitude": 48.8584, "longitude": 2.2945, "accuracy": 50}'
```

**Expected:** Should return Paris.

---

## Verification Checklist

- [ ] GPS detection works with reverse geocoding
- [ ] IP fallback works when permission denied
- [ ] Manual entry works as safety net
- [ ] JSON file saves after each detection
- [ ] All API endpoints return correct JSON
- [ ] UI is responsive on mobile
- [ ] Google Maps links work
- [ ] Accuracy meter displays for GPS only
- [ ] No console errors (check Developer Tools)
- [ ] No race conditions in parallel requests
- [ ] Browser compatibility verified

---

## Performance Metrics

**Expected performance:**

| Operation | Time | Notes |
|-----------|------|-------|
| GPS detection | 3-10 seconds | Depends on signal |
| IP fallback | < 1 second | Fast but less accurate |
| Reverse geocoding | 0.5-1 second | Uses Nominatim API |
| Frontend load | < 1 second | Lightweight HTML |
| API response | < 100ms | Database-free |

---

## Common Issues & Fixes

### Issue: "CORS blocked" Error

**Cause:** Frontend and backend on different ports/hosts

**Fix:**
- Verify backend on `localhost:8000`
- Verify frontend on `localhost:8001`
- Check backend CORS middleware

### Issue: GPS Permission Not Requested

**Cause:** Browser privacy mode or settings

**Fix:**
- Use normal (non-incognito) mode
- Clear site data: Settings → Cookies & Site Data
- Use HTTPS in production

### Issue: IP Lookup Returns Empty

**Cause:** Network blocked or service down

**Fix:**
- Check internet connection
- Backend will return error
- User can fall back to manual entry

### Issue: Reverse Geocoding Returns NULL Cities

**Cause:** Coordinates in ocean or remote area

**Fix:**
- Nominatim may not have data
- Try major cities first
- City field will show "—" (empty)

---

## Success Criteria

✅ **All tests pass if:**

1. GPS detection works with coordinates + city
2. IP fallback works when permission denied
3. Manual entry works as safety net
4. JSON file saves correctly
5. All API endpoints respond correctly
6. UI is responsive and intuitive
7. No console errors
8. Mobile browser works
9. Multiple detections don't interfere
10. Performance meets expectations

---

**🎉 Congratulations! Your location detection system is production-ready! 🌍**

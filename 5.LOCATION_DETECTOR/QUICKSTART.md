# 🌍 Location Detection - Quick Start

Get the demo running in **3 minutes**.

## Prerequisites

- Python 3.8+ (check: `python --version`)
- A modern web browser (Chrome, Firefox, Safari, Edge)

## Setup

### 1️⃣ Install Dependencies

```bash
cd location-demo
pip install -r requirements.txt
```

**On macOS with conda:**
```bash
/opt/homebrew/Caskroom/miniconda/base/bin/python -m pip install -r requirements.txt
```

### 2️⃣ Start the Servers

**Option A: Automatic (Linux/macOS)**
```bash
./start.sh
```

**Option B: Manual**

Terminal 1 - Backend:
```bash
cd backend
python main.py
```

Terminal 2 - Frontend:
```bash
cd frontend
python -m http.server 8001
```

### 3️⃣ Open in Browser

Visit: **http://localhost:8001**

You should see a beautiful purple UI with "🔍 Detect Location" button.

## 🎮 Test It Out

### GPS Detection (Allow Permission)

1. Click **"🔍 Detect Location"**
2. When prompted, **Allow location** access
3. See GPS coordinates + city/region (reverse geocoded)
4. Check `backend/location_output.json` for saved data

### IP Fallback (Deny Permission)

1. Click **"🔍 Detect Location"**
2. When prompted, **Deny location** access
3. Backend falls back to IP-based geolocation
4. See approximate city/region (less accurate)
5. Check `location_output.json` for `"source": "ip"`

### Manual Entry

1. Click **"⌨️ Manual Entry"**
2. Enter city: "Tokyo", region: "Tokyo", country: "Japan"
3. Click **"✓ Submit"**
4. Location saved with `"source": "manual"`

## 📱 Test on Mobile

### Using ngrok (Cloud Tunnel)

```bash
# Terminal 1: Backend
cd backend && python main.py

# Terminal 2: Frontend
cd frontend && python -m http.server 8001

# Terminal 3: Expose to internet
brew install ngrok
ngrok http 8001
```

Open the ngrok URL on your mobile device (e.g., `https://abc123.ngrok.io`).

### Using Local Network (Same Wi-Fi)

```bash
# Find your Mac's IP
ifconfig | grep inet

# Start servers (already running on 0.0.0.0)

# On your phone, visit: http://<YOUR_MAC_IP>:8001
```

## 🔍 API Endpoints (Curl Examples)

### GPS Detection
```bash
curl -X POST http://localhost:8000/api/location/detect \
  -H "Content-Type: application/json" \
  -d '{"latitude": 37.7749, "longitude": -122.4194, "accuracy": 15}'
```

**Response:**
```json
{
  "latitude": 37.7749,
  "longitude": -122.4194,
  "accuracy": 15,
  "city": "San Francisco",
  "area": null,
  "region": "California",
  "country": "United States",
  "source": "gps",
  "timestamp": "2026-02-09T12:34:56.789Z"
}
```

### IP Fallback (Empty GPS)
```bash
curl -X POST http://localhost:8000/api/location/detect \
  -H "Content-Type: application/json" \
  -d '{"latitude": null, "longitude": null, "accuracy": null}'
```

Falls back to IP-based detection.

### Manual Entry
```bash
curl -X POST "http://localhost:8000/api/location/manual?city=Tokyo&region=Tokyo&country=Japan"
```

### Get Last Location
```bash
curl http://localhost:8000/api/location/last
```

### Health Check
```bash
curl http://localhost:8000/health
```

## 📊 Location Output

After detection, view the saved location:

```bash
cat backend/location_output.json
```

**Example output:**
```json
{
  "latitude": 37.7749,
  "longitude": -122.4194,
  "accuracy": 15,
  "city": "San Francisco",
  "area": "SOMA",
  "region": "California",
  "country": "United States",
  "source": "gps",
  "timestamp": "2026-02-09T16:27:34.613873Z"
}
```

## 🐛 Troubleshooting

### CORS Error
- Make sure backend is on `http://localhost:8000`
- Make sure frontend is on `http://localhost:8001`

### "Geolocation not supported"
- Use a modern browser (Chrome, Firefox, Safari, Edge)
- Browsers require HTTPS or localhost

### GPS Timeout (10+ seconds)
- Poor GPS signal (try outdoors)
- Allow fallback to happen
- Check signal/cloud cover

### Port Already in Use
```bash
# Kill process on port 8000
lsof -i :8000
kill -9 <PID>

# Or use different port in main.py
```

## 🚀 Next Steps

- **Read the README**: `README.md` (comprehensive documentation)
- **Modify the code**: Adjust timeouts, services, or UI
- **Deploy**: Use ngrok or cloud hosting
- **Learn more**: See README.md for architecture details

## 📚 Real-World Principles

This demo shows how actual companies detect location:

| Company | Method | Fallback |
|---------|--------|----------|
| **Google Maps** | GPS + Wi-Fi + IP | Manual |
| **Uber** | High-accuracy GPS | Wi-Fi + IP |
| **Social Media** | GPS + IP | Manual entry |

---

**✅ You're all set! Enjoy exploring location detection! 🌍**

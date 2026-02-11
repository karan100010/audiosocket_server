# Go AudioSocket Call Flow Demo

This folder contains a Go implementation for handling Asterisk AudioSocket calls.

---

## 1) What this project provides

The server supports two runtime engines:

1. **basic**
   - JSON node/transition call flow (`flow.sample.json`)
   - Demo keyword-based intent resolver
2. **bhashini**
   - Interactive language-selection + translation loop
   - Bhashini ASR + Translation + TTS APIs

---

## 2) How `engine2.go` works

`internal/flow/engine2.go` runs a stateful translation call:

1. TTS asks source language
2. Captures caller audio and detects language from ASR transcript
3. TTS asks target language
4. Captures caller audio and detects language again
5. Enters continuous loop:
   - listen for utterance window
   - ASR in source language
   - translate to target language
   - TTS translated text back to caller

Audio notes:
- AudioSocket media is **SLIN 8k PCM16**.
- Bhashini ASR requires 16k, so engine2 up-samples captured 8k to 16k.
- Bhashini TTS returns base64 WAV; engine2 decodes WAV and streams PCM as 320-byte / 20ms frames.

---

## 3) Run from scratch (step-by-step)

### Prerequisites

- Linux/macOS terminal
- Go **1.22+** (recommended 1.23+)
- Asterisk with AudioSocket support
- Network route from Asterisk host to this Go server
- (For bhashini engine) Bhashini API key

Check Go:

```bash
go version
```

### Step A: Get the code

If you already have this repository, skip clone.

```bash
git clone <your-repo-url>
cd audiosocket_server/go_callflow_demo
```

### Step B: Install dependencies

```bash
go mod tidy
```

### Step C: Build

```bash
go build ./...
```

### Step D: Run server (basic engine)

```bash
go run ./cmd/server \
  --listen :9092 \
  --engine basic \
  --flow flow.sample.json \
  --listen-window 4s
```

You should see logs similar to:

- `listening on :9092 (engine=basic)`

### Step E: Run server (bhashini engine)

```bash
export BHASHINI_API_KEY="<your-key>"
go run ./cmd/server \
  --listen :9092 \
  --engine bhashini \
  --listen-window 4s \
  --bhashini-url https://103.114.152.23/services/inference/pipeline \
  --bhashini-host dhruva-api.bhashini.gov.in \
  --bhashini-insecure=true
```

> You can also pass `--bhashini-api-key` directly, but environment variable is cleaner.

---

## 4) Minimal Asterisk wiring (example)

Use an extension in `extensions.conf` that dials AudioSocket to your Go server:

```asterisk
exten => 9001,1,NoOp(AudioSocket Go Demo)
 same => n,Answer()
 same => n,Dial(AudioSocket/${UNIQUEID}/<GO_SERVER_IP>:9092)
 same => n,Hangup()
```

Replace `<GO_SERVER_IP>` with the host/IP running this Go process.

When you call extension `9001`, Asterisk should connect to this server and stream audio frames.

---

## 5) Customizing call flow

### For `basic` engine

Edit `flow.sample.json`:

- `start_node`: first node name
- node fields:
  - `prompt_wav`
  - `transitions` (intent -> next)
  - `fallback_node`
  - `action` (`continue`, `hangup`, `transfer`)

Use 8kHz mono PCM16 WAV prompts for clean playback.

### For `bhashini` engine

Tune runtime flags:

- `--listen-window` controls how much audio each capture window gathers
- `--bhashini-*` controls endpoint host, TLS behavior, API key

If you want different Bhashini model/service IDs, update them in:

- `cmd/server/main.go` (where `BhashiniConfig` is constructed)

---

## 6) Troubleshooting

### Server starts but no calls arrive

- Check Asterisk can reach `<GO_SERVER_IP>:9092`
- Verify firewall/security group
- Ensure `Dial(AudioSocket/...)` points to correct port

### Call connects but no audio playback

- Confirm prompt audio is 8k mono PCM16 (for `basic`)
- Check logs for WAV format errors

### Bhashini mode errors

- Verify `BHASHINI_API_KEY`
- Check URL/Host values
- If TLS cert mismatch exists in your environment, keep `--bhashini-insecure=true`

### Very long delay in translation loop

- Reduce `--listen-window`
- Check latency to Bhashini endpoint

---

## 7) Project structure

- `cmd/server/main.go`: AudioSocket TCP server + engine selection (`basic`/`bhashini`)
- `internal/flow/engine.go`: basic JSON call-flow engine
- `internal/flow/engine2.go`: Bhashini-powered translation engine
- `internal/flow/config.go`: call flow config model + loader
- `internal/audio/wav.go`: WAV parser + PCM chunker
- `flow.sample.json`: sample flow for basic engine

package flow

import (
	"bytes"
	"context"
	"crypto/tls"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"strings"
	"time"

	"audiosocket_server/go_callflow_demo/internal/audio"
	"github.com/CyCoreSystems/audiosocket"
)

// BhashiniConfig holds API settings for Bhashini pipeline.
type BhashiniConfig struct {
	PipelineURL        string
	HostHeader         string
	APIKey             string
	ASRServiceID       string
	TranslateServiceID string
	TTSEngServiceID    string
	TTSIndicServiceID  string
	InsecureTLS        bool
	Timeout            time.Duration
}

type bhashiniRequest struct {
	PipelineTasks []map[string]any `json:"pipelineTasks"`
	InputData     map[string]any   `json:"inputData"`
	SamplingRate  int              `json:"samplingRate,omitempty"`
}

type BhashiniClient struct {
	cfg    BhashiniConfig
	client *http.Client
}

func NewBhashiniClient(cfg BhashiniConfig) *BhashiniClient {
	tr := &http.Transport{}
	if cfg.InsecureTLS {
		tr.TLSClientConfig = &tls.Config{InsecureSkipVerify: true}
	}
	if cfg.Timeout == 0 {
		cfg.Timeout = 20 * time.Second
	}
	return &BhashiniClient{
		cfg: cfg,
		client: &http.Client{
			Timeout:   cfg.Timeout,
			Transport: tr,
		},
	}
}

func (b *BhashiniClient) doPipeline(ctx context.Context, reqBody bhashiniRequest) (map[string]any, error) {
	payload, err := json.Marshal(reqBody)
	if err != nil {
		return nil, err
	}
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, b.cfg.PipelineURL, bytes.NewReader(payload))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Accept", "*/*")
	req.Header.Set("Authorization", b.cfg.APIKey)
	req.Header.Set("Content-Type", "application/json")
	if b.cfg.HostHeader != "" {
		req.Host = b.cfg.HostHeader
		req.Header.Set("Host", b.cfg.HostHeader)
	}

	resp, err := b.client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	body, _ := io.ReadAll(resp.Body)
	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return nil, fmt.Errorf("bhashini status=%d body=%s", resp.StatusCode, string(body))
	}
	var out map[string]any
	if err := json.Unmarshal(body, &out); err != nil {
		return nil, fmt.Errorf("decode response: %w", err)
	}
	return out, nil
}

func (b *BhashiniClient) Transcribe(ctx context.Context, pcm16k []byte, lang string) (string, error) {
	audioB64 := base64.StdEncoding.EncodeToString(pcm16k)
	res, err := b.doPipeline(ctx, bhashiniRequest{
		PipelineTasks: []map[string]any{{
			"taskType": "asr",
			"config": map[string]any{
				"language":  map[string]any{"sourceLanguage": lang},
				"serviceId": b.cfg.ASRServiceID,
			},
		}},
		InputData:    map[string]any{"audio": []map[string]any{{"audioContent": audioB64}}},
		SamplingRate: 16000,
	})
	if err != nil {
		return "", err
	}
	return jsonPathString(res, "pipelineResponse", 0, "output", 0, "source"), nil
}

func (b *BhashiniClient) Translate(ctx context.Context, text, sourceLang, targetLang string) (string, error) {
	res, err := b.doPipeline(ctx, bhashiniRequest{
		PipelineTasks: []map[string]any{{
			"taskType": "translation",
			"config": map[string]any{
				"language": map[string]any{
					"sourceLanguage": sourceLang,
					"targetLanguage": targetLang,
				},
				"serviceId": b.cfg.TranslateServiceID,
			},
		}},
		InputData: map[string]any{"input": []map[string]any{{"source": text}}},
	})
	if err != nil {
		return "", err
	}
	return jsonPathString(res, "pipelineResponse", 0, "output", 0, "target"), nil
}

func (b *BhashiniClient) TTS(ctx context.Context, text, lang string) ([]byte, error) {
	serviceID := b.cfg.TTSIndicServiceID
	if lang == "en" {
		serviceID = b.cfg.TTSEngServiceID
	}
	res, err := b.doPipeline(ctx, bhashiniRequest{
		PipelineTasks: []map[string]any{{
			"taskType": "tts",
			"config": map[string]any{
				"language":     map[string]any{"sourceLanguage": lang},
				"serviceId":    serviceID,
				"gender":       "female",
				"samplingRate": 8000,
			},
		}},
		InputData: map[string]any{"input": []map[string]any{{"source": text}}},
	})
	if err != nil {
		return nil, err
	}
	audioB64 := jsonPathString(res, "pipelineResponse", 0, "audio", 0, "audioContent")
	if audioB64 == "" {
		return nil, fmt.Errorf("tts response missing audio content")
	}
	wavBytes, err := base64.StdEncoding.DecodeString(audioB64)
	if err != nil {
		return nil, err
	}
	pcm, err := audio.ReadPCM16MonoWavBytes(wavBytes)
	if err != nil {
		return nil, err
	}
	if pcm.SampleRate != 8000 {
		return nil, fmt.Errorf("tts sample rate expected 8000 got %d", pcm.SampleRate)
	}
	return pcm.PCM, nil
}

// BhashiniEngine2 implements an interactive translation flow.
type BhashiniEngine2 struct {
	Client        *BhashiniClient
	Logger        *log.Logger
	ListenWindow  time.Duration
	SourceLang    string
	TargetLang    string
	EndOnEmptyASR bool
}

func (e *BhashiniEngine2) Run(ctx context.Context, conn Conn) error {
	if e.Client == nil {
		return fmt.Errorf("bhashini client is required")
	}
	if e.ListenWindow <= 0 {
		e.ListenWindow = 4 * time.Second
	}

	if err := e.speakText(ctx, conn, "Welcome. Please say source language. For example, English or Hindi.", "en"); err != nil {
		return err
	}
	srcAudio, err := conn.ListenWindow(ctx, e.ListenWindow)
	if err != nil {
		return err
	}
	sourceLang, sourceName, err := e.detectLanguage(ctx, srcAudio)
	if err != nil {
		e.Logger.Printf("source language detection failed, defaulting en: %v", err)
		sourceLang, sourceName = "en", "English"
	}
	e.SourceLang = sourceLang
	e.Logger.Printf("source language=%s (%s)", sourceName, sourceLang)

	if err := e.speakText(ctx, conn, "Please say target language.", "en"); err != nil {
		return err
	}
	tgtAudio, err := conn.ListenWindow(ctx, e.ListenWindow)
	if err != nil {
		return err
	}
	targetLang, targetName, err := e.detectLanguage(ctx, tgtAudio)
	if err != nil {
		e.Logger.Printf("target language detection failed, defaulting hi: %v", err)
		targetLang, targetName = "hi", "Hindi"
	}
	e.TargetLang = targetLang
	e.Logger.Printf("target language=%s (%s)", targetName, targetLang)

	if err := e.speakText(ctx, conn, "Translation started. Speak now.", "en"); err != nil {
		return err
	}

	for {
		utterance8k, err := conn.ListenWindow(ctx, e.ListenWindow)
		if err != nil {
			return err
		}
		if len(utterance8k) < 320*4 {
			continue
		}
		utterance16k := upsample8kTo16kPCM16(utterance8k)

		text, err := e.Client.Transcribe(ctx, utterance16k, e.SourceLang)
		if err != nil {
			e.Logger.Printf("asr error: %v", err)
			continue
		}
		if strings.TrimSpace(text) == "" {
			e.Logger.Printf("asr empty text")
			if e.EndOnEmptyASR {
				return nil
			}
			continue
		}
		e.Logger.Printf("asr[%s]: %s", e.SourceLang, text)

		translated, err := e.Client.Translate(ctx, text, e.SourceLang, e.TargetLang)
		if err != nil {
			e.Logger.Printf("translation error: %v", err)
			continue
		}
		if strings.TrimSpace(translated) == "" {
			e.Logger.Printf("translation returned empty")
			continue
		}
		e.Logger.Printf("translation[%s->%s]: %s", e.SourceLang, e.TargetLang, translated)

		if err := e.speakText(ctx, conn, translated, e.TargetLang); err != nil {
			return err
		}
	}
}

func (e *BhashiniEngine2) speakText(ctx context.Context, conn Conn, text, lang string) error {
	pcm, err := e.Client.TTS(ctx, text, lang)
	if err != nil {
		return fmt.Errorf("tts failed: %w", err)
	}
	for _, frame := range audio.ChunkPCM(pcm, audiosocket.DefaultSlinChunkSize) {
		if err := conn.WritePCM(frame); err != nil {
			return err
		}
		time.Sleep(20 * time.Millisecond)
	}
	return nil
}

func (e *BhashiniEngine2) detectLanguage(ctx context.Context, audio8k []byte) (string, string, error) {
	audio16k := upsample8kTo16kPCM16(audio8k)
	transcript, err := e.Client.Transcribe(ctx, audio16k, "en")
	if err == nil {
		if code, name := mapLanguageName(transcript); code != "" {
			return code, name, nil
		}
	}
	transcriptHi, errHi := e.Client.Transcribe(ctx, audio16k, "hi")
	if errHi == nil {
		if code, name := mapLanguageName(transcriptHi); code != "" {
			return code, name, nil
		}
	}
	if err != nil {
		return "", "", err
	}
	return "", "", fmt.Errorf("unable to detect language from transcript en=%q hi=%q", transcript, transcriptHi)
}

func mapLanguageName(text string) (string, string) {
	t := strings.ToLower(text)
	mapping := map[string][2]string{
		"english": {"en", "English"},
		"hindi":   {"hi", "Hindi"},
		"tamil":   {"ta", "Tamil"},
		"telugu":  {"te", "Telugu"},
		"bengali": {"bn", "Bengali"},
		"marathi": {"mr", "Marathi"},
	}
	for key, val := range mapping {
		if strings.Contains(t, key) {
			return val[0], val[1]
		}
	}
	return "", ""
}

func upsample8kTo16kPCM16(in []byte) []byte {
	if len(in) < 4 {
		return in
	}
	out := make([]byte, 0, len(in)*2)
	for i := 0; i+3 < len(in); i += 2 {
		s0 := int16(in[i]) | int16(in[i+1])<<8
		s1 := int16(in[i+2]) | int16(in[i+3])<<8
		mid := int16((int32(s0) + int32(s1)) / 2)

		out = append(out, byte(s0), byte(s0>>8))
		out = append(out, byte(mid), byte(mid>>8))
	}
	lastLo := in[len(in)-2]
	lastHi := in[len(in)-1]
	out = append(out, lastLo, lastHi, lastLo, lastHi)
	return out
}

func jsonPathString(v map[string]any, path ...any) string {
	var cur any = v
	for _, p := range path {
		switch k := p.(type) {
		case string:
			m, ok := cur.(map[string]any)
			if !ok {
				return ""
			}
			cur = m[k]
		case int:
			a, ok := cur.([]any)
			if !ok || k < 0 || k >= len(a) {
				return ""
			}
			cur = a[k]
		}
	}
	s, _ := cur.(string)
	return s
}

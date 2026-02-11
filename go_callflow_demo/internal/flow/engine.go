package flow

import (
	"bytes"
	"context"
	"fmt"
	"log"
	"strings"
	"time"

	"audiosocket_server/go_callflow_demo/internal/audio"
	"github.com/CyCoreSystems/audiosocket"
)

// IntentResolver converts captured speech audio into an intent label.
type IntentResolver interface {
	ResolveIntent(ctx context.Context, pcm16 []byte, sampleRate int) (string, error)
}

// KeywordResolver is a demo resolver.
// It converts raw bytes to string and searches for keywords.
// In production replace with ASR+NLU.
type KeywordResolver struct{}

func (k KeywordResolver) ResolveIntent(_ context.Context, pcm16 []byte, _ int) (string, error) {
	t := strings.ToLower(string(bytes.TrimSpace(pcm16)))
	switch {
	case strings.Contains(t, "yes") || strings.Contains(t, "haan"):
		return "positive", nil
	case strings.Contains(t, "no") || strings.Contains(t, "nahi"):
		return "negative", nil
	default:
		return "unknown", nil
	}
}

type SessionEngine struct {
	Config       *Config
	Resolver     IntentResolver
	MaxListenDur time.Duration
	Logger       *log.Logger
}

func (e *SessionEngine) Run(ctx context.Context, conn Conn) error {
	nodeName := e.Config.StartNode
	for {
		node, ok := e.Config.Nodes[nodeName]
		if !ok {
			return fmt.Errorf("node %q not found", nodeName)
		}

		e.Logger.Printf("node=%s action=%s prompt=%s", nodeName, node.Action, node.PromptWav)

		if node.PromptWav != "" {
			if err := playPrompt(conn, node.PromptWav); err != nil {
				return fmt.Errorf("play prompt %s: %w", node.PromptWav, err)
			}
		}

		switch node.Action {
		case "hangup":
			return conn.Hangup()
		case "transfer":
			e.Logger.Printf("transfer requested at node=%s (implement PBX transfer hook)", nodeName)
			return conn.Hangup()
		}

		input, err := conn.ListenWindow(ctx, e.MaxListenDur)
		if err != nil {
			return fmt.Errorf("capture audio: %w", err)
		}

		intent, err := e.Resolver.ResolveIntent(ctx, input, 8000)
		if err != nil {
			return fmt.Errorf("resolve intent: %w", err)
		}
		e.Logger.Printf("node=%s resolved intent=%s", nodeName, intent)

		next := node.FallbackNode
		for _, tr := range node.Transitions {
			if tr.Intent == intent {
				next = tr.Next
				break
			}
		}
		if next == "" {
			return fmt.Errorf("no transition found for node=%s intent=%s", nodeName, intent)
		}
		nodeName = next
	}
}

func playPrompt(conn Conn, wavPath string) error {
	w, err := audio.ReadPCM16MonoWav(wavPath)
	if err != nil {
		return err
	}
	if w.SampleRate != 8000 {
		return fmt.Errorf("prompt sample rate must be 8000, got %d", w.SampleRate)
	}
	for _, frame := range audio.ChunkPCM(w.PCM, audiosocket.DefaultSlinChunkSize) {
		if err := conn.WritePCM(frame); err != nil {
			return err
		}
		time.Sleep(20 * time.Millisecond)
	}
	return nil
}

// Conn is a light adapter around AudioSocket connection operations used by engine.
type Conn interface {
	WritePCM(frame []byte) error
	ListenWindow(ctx context.Context, d time.Duration) ([]byte, error)
	Hangup() error
}

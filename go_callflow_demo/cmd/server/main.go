package main

import (
	"bytes"
	"context"
	"errors"
	"flag"
	"fmt"
	"io"
	"log"
	"net"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"

	"audiosocket_server/go_callflow_demo/internal/flow"
	"github.com/CyCoreSystems/audiosocket"
)

type audioConn struct {
	netConn net.Conn
	logger  *log.Logger
}

func (c *audioConn) WritePCM(frame []byte) error {
	_, err := c.netConn.Write(audiosocket.SlinMessage(frame))
	return err
}

func (c *audioConn) ListenWindow(ctx context.Context, d time.Duration) ([]byte, error) {
	deadline := time.Now().Add(d)
	_ = c.netConn.SetReadDeadline(deadline)
	defer c.netConn.SetReadDeadline(time.Time{})

	var out bytes.Buffer
	for {
		select {
		case <-ctx.Done():
			return out.Bytes(), ctx.Err()
		default:
		}
		msg, err := audiosocket.NextMessage(c.netConn)
		if err != nil {
			if ne, ok := err.(net.Error); ok && ne.Timeout() {
				return out.Bytes(), nil
			}
			if errors.Is(err, io.EOF) {
				return out.Bytes(), io.EOF
			}
			return nil, err
		}
		switch msg.Kind() {
		case audiosocket.KindSlin:
			out.Write(msg.Payload())
		case audiosocket.KindHangup:
			return out.Bytes(), io.EOF
		case audiosocket.KindError:
			c.logger.Printf("asterisk error code=%d", msg.ErrorCode())
		default:
			// ignore non-audio packets in listen window
		}
	}
}

func (c *audioConn) Hangup() error {
	_, err := c.netConn.Write(audiosocket.HangupMessage())
	return err
}

func main() {
	var (
		addr       = flag.String("listen", ":9092", "address to listen for AudioSocket calls")
		flowPath   = flag.String("flow", "go_callflow_demo/flow.sample.json", "path to call flow JSON")
		listenTime = flag.Duration("listen-window", 4*time.Second, "audio capture duration per node")
		engineKind = flag.String("engine", "basic", "engine: basic | bhashini")
		bhURL      = flag.String("bhashini-url", "https://103.114.152.23/services/inference/pipeline", "bhashini pipeline URL")
		bhHost     = flag.String("bhashini-host", "dhruva-api.bhashini.gov.in", "bhashini host header")
		bhAPIKey   = flag.String("bhashini-api-key", os.Getenv("BHASHINI_API_KEY"), "bhashini API key (or BHASHINI_API_KEY env)")
		bhInsecure = flag.Bool("bhashini-insecure", true, "skip TLS verification for bhashini endpoint")
	)
	flag.Parse()

	logger := log.New(os.Stdout, "[go-callflow] ", log.LstdFlags|log.Lmicroseconds)

	cfg, err := flow.LoadConfig(*flowPath)
	if err != nil {
		logger.Fatalf("load flow config: %v", err)
	}

	ln, err := net.Listen("tcp", *addr)
	if err != nil {
		logger.Fatalf("listen %s: %v", *addr, err)
	}
	defer ln.Close()

	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()

	logger.Printf("listening on %s (engine=%s)", *addr, *engineKind)
	for {
		select {
		case <-ctx.Done():
			logger.Println("shutdown requested")
			return
		default:
		}

		_ = ln.(*net.TCPListener).SetDeadline(time.Now().Add(1 * time.Second))
		nc, err := ln.Accept()
		if err != nil {
			if ne, ok := err.(net.Error); ok && ne.Timeout() {
				continue
			}
			logger.Printf("accept error: %v", err)
			continue
		}

		go handleCall(ctx, nc, cfg, *listenTime, *engineKind, bhashiniParams{
			URL:      *bhURL,
			Host:     *bhHost,
			APIKey:   *bhAPIKey,
			Insecure: *bhInsecure,
		}, logger)
	}
}

type bhashiniParams struct {
	URL      string
	Host     string
	APIKey   string
	Insecure bool
}

func handleCall(ctx context.Context, nc net.Conn, cfg *flow.Config, listenWindow time.Duration, engineKind string, bhParams bhashiniParams, logger *log.Logger) {
	defer nc.Close()

	idMsg, err := audiosocket.NextMessage(nc)
	if err != nil {
		logger.Printf("failed to read ID packet from %s: %v", nc.RemoteAddr(), err)
		return
	}
	if idMsg.Kind() != audiosocket.KindID {
		logger.Printf("first packet is not ID from %s (kind=%d)", nc.RemoteAddr(), idMsg.Kind())
		return
	}
	id, err := idMsg.ID()
	if err != nil {
		logger.Printf("invalid ID packet from %s: %v", nc.RemoteAddr(), err)
		return
	}

	logger.Printf("new call remote=%s id=%s", nc.RemoteAddr(), id.String())

	sess := &audioConn{netConn: nc, logger: logger}

	switch engineKind {
	case "bhashini":
		if strings.TrimSpace(bhParams.APIKey) == "" {
			logger.Printf("call %s ended: missing bhashini api key", id.String())
			_ = sess.Hangup()
			return
		}
		bClient := flow.NewBhashiniClient(flow.BhashiniConfig{
			PipelineURL:        bhParams.URL,
			HostHeader:         bhParams.Host,
			APIKey:             bhParams.APIKey,
			InsecureTLS:        bhParams.Insecure,
			ASRServiceID:       "ai4bharat/conformer-multilingual-indo_aryan-gpu--t4",
			TranslateServiceID: "ai4bharat/indictrans-v2-all-gpu--t4",
			TTSEngServiceID:    "ai4bharat/indic-tts-coqui-misc-gpu--t4",
			TTSIndicServiceID:  "ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4",
		})
		engine2 := &flow.BhashiniEngine2{
			Client:        bClient,
			Logger:        logger,
			ListenWindow:  listenWindow,
			EndOnEmptyASR: false,
		}
		if err := engine2.Run(ctx, sess); err != nil && !errors.Is(err, io.EOF) {
			logger.Printf("call %s ended with error: %v", id.String(), err)
		}
	default:
		engine := &flow.SessionEngine{
			Config:       cfg,
			Resolver:     flow.KeywordResolver{},
			MaxListenDur: listenWindow,
			Logger:       logger,
		}
		if err := engine.Run(ctx, sess); err != nil && !errors.Is(err, io.EOF) {
			logger.Printf("call %s ended with error: %v", id.String(), err)
			return
		}
	}

	logger.Printf("call %s completed", id.String())
	if err := sess.Hangup(); err != nil {
		logger.Printf("hangup %s: %v", id.String(), err)
	}
	fmt.Println()
}

package flow

import (
	"encoding/json"
	"fmt"
	"os"
)

// Config is the full call flow configuration.
type Config struct {
	StartNode string          `json:"start_node"`
	Nodes     map[string]Node `json:"nodes"`
}

// Node describes one step in the IVR flow.
type Node struct {
	PromptWav    string       `json:"prompt_wav"`
	Transitions  []Transition `json:"transitions"`
	FallbackNode string       `json:"fallback_node"`
	Action       string       `json:"action"` // continue | hangup | transfer
}

// Transition determines next node based on matched intent name.
type Transition struct {
	Intent string `json:"intent"`
	Next   string `json:"next"`
}

func LoadConfig(path string) (*Config, error) {
	b, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("read config %s: %w", path, err)
	}
	var cfg Config
	if err := json.Unmarshal(b, &cfg); err != nil {
		return nil, fmt.Errorf("parse config %s: %w", path, err)
	}
	if cfg.StartNode == "" {
		return nil, fmt.Errorf("start_node is required")
	}
	if len(cfg.Nodes) == 0 {
		return nil, fmt.Errorf("at least one node is required")
	}
	return &cfg, nil
}

package audio

import (
	"bytes"
	"encoding/binary"
	"fmt"
	"io"
	"os"
)

const DefaultChunkSize = 320 // 20ms @ 8khz, mono, 16-bit PCM

type WavData struct {
	SampleRate    uint32
	NumChannels   uint16
	BitsPerSample uint16
	PCM           []byte
}

// ReadPCM16MonoWav reads a RIFF WAV file and validates 16-bit PCM mono.
func ReadPCM16MonoWav(path string) (*WavData, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	b, err := io.ReadAll(f)
	if err != nil {
		return nil, err
	}
	return ReadPCM16MonoWavBytes(b)
}

func ReadPCM16MonoWavBytes(b []byte) (*WavData, error) {
	r := bytes.NewReader(b)
	head := make([]byte, 12)
	if _, err := io.ReadFull(r, head); err != nil {
		return nil, err
	}
	if string(head[0:4]) != "RIFF" || string(head[8:12]) != "WAVE" {
		return nil, fmt.Errorf("not a valid RIFF/WAVE file")
	}

	var (
		sampleRate uint32
		channels   uint16
		bits       uint16
		data       []byte
	)

	for {
		chunkHeader := make([]byte, 8)
		if _, err := io.ReadFull(r, chunkHeader); err != nil {
			if err == io.EOF || err == io.ErrUnexpectedEOF {
				break
			}
			return nil, err
		}
		chunkID := string(chunkHeader[0:4])
		chunkSize := binary.LittleEndian.Uint32(chunkHeader[4:8])

		chunk := make([]byte, chunkSize)
		if _, err := io.ReadFull(r, chunk); err != nil {
			return nil, err
		}

		switch chunkID {
		case "fmt ":
			if len(chunk) < 16 {
				return nil, fmt.Errorf("invalid fmt chunk")
			}
			audioFormat := binary.LittleEndian.Uint16(chunk[0:2])
			channels = binary.LittleEndian.Uint16(chunk[2:4])
			sampleRate = binary.LittleEndian.Uint32(chunk[4:8])
			bits = binary.LittleEndian.Uint16(chunk[14:16])
			if audioFormat != 1 {
				return nil, fmt.Errorf("wav is not PCM (format=%d)", audioFormat)
			}
		case "data":
			data = chunk
		}

		if chunkSize%2 == 1 {
			_, _ = r.Read(make([]byte, 1))
		}
	}

	if len(data) == 0 {
		return nil, fmt.Errorf("wav has no data chunk")
	}
	if channels != 1 || bits != 16 {
		return nil, fmt.Errorf("wav must be mono 16-bit PCM (got channels=%d bits=%d)", channels, bits)
	}

	return &WavData{
		SampleRate:    sampleRate,
		NumChannels:   channels,
		BitsPerSample: bits,
		PCM:           data,
	}, nil
}

func ChunkPCM(input []byte, chunkSize int) [][]byte {
	if chunkSize <= 0 {
		chunkSize = DefaultChunkSize
	}
	chunks := make([][]byte, 0, len(input)/chunkSize+1)
	for i := 0; i < len(input); i += chunkSize {
		end := i + chunkSize
		if end > len(input) {
			pad := make([]byte, chunkSize)
			copy(pad, input[i:])
			chunks = append(chunks, pad)
			break
		}
		chunks = append(chunks, input[i:end])
	}
	return chunks
}

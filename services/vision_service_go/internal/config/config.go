package config
package config

import (
	"fmt"
	"os"
	"strconv"
)

type Config struct {
	Port     int
	Hostname string
}

func Load() (*Config, error) {
	port := 8003
	if p := os.Getenv("VISION_SERVICE_PORT"); p != "" {
		parsedPort, err := strconv.Atoi(p)
		if err == nil {
			port = parsedPort
		}
	}

	hostname := os.Getenv("VISION_SERVICE_HOSTNAME")
	if hostname == "" {
		hostname = "0.0.0.0"
	}

	return &Config{
		Port:     port,
		Hostname: hostname,
	}, nil
}

func (c *Config) String() string {
	return fmt.Sprintf("VisionService on %s:%d", c.Hostname, c.Port)
}

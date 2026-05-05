package config
package config

import (
	"fmt"
	"os"
	"strconv"
)

type Config struct {
	Port      int
	Hostname  string
	MongoURI  string
	MongoDBName string
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

	mongoURI := os.Getenv("MONGODB_URI")
	if mongoURI == "" {
		mongoURI = "mongodb://localhost:27017"
	}

	mongoDBName := os.Getenv("MONGODB_DATABASE")
	if mongoDBName == "" {
		mongoDBName = "agrovision"
	}

	return &Config{
		Port:       port,
		Hostname:   hostname,
		MongoURI:   mongoURI,
		MongoDBName: mongoDBName,
	}, nil
}

func (c *Config) String() string {
	return fmt.Sprintf("VisionService on %s:%d (MongoDB: %s)", c.Hostname, c.Port, c.MongoURI)
}

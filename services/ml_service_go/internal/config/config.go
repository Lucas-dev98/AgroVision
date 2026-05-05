package config
package config

import (
	"fmt"
	"os"
	"strconv"
)

type Config struct {
	Port       int
	Hostname   string
	MongoURI   string
	MongoDBName string
	JWTSecret  string
}

func Load() (*Config, error) {
	port := 8004
	if p := os.Getenv("ML_SERVICE_PORT"); p != "" {
		parsedPort, err := strconv.Atoi(p)
		if err == nil {
			port = parsedPort
		}
	}

	hostname := os.Getenv("ML_SERVICE_HOSTNAME")
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

	jwtSecret := os.Getenv("JWT_SECRET")
	if jwtSecret == "" {
		jwtSecret = "your-secret-key"
	}

	return &Config{
		Port:        port,
		Hostname:    hostname,
		MongoURI:    mongoURI,
		MongoDBName: mongoDBName,
		JWTSecret:   jwtSecret,
	}, nil
}

func (c *Config) String() string {
	return fmt.Sprintf("MLService on %s:%d (MongoDB: %s)", c.Hostname, c.Port, c.MongoDBName)
}

package db
package db

import (
	"context"
	"fmt"
	"log"
	"time"

	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
	"go.mongodb.org/mongo-driver/mongo/readpref"
)

// MongoConnection manages MongoDB client and database
type MongoConnection struct {
	Client   *mongo.Client
	Database *mongo.Database
}

// NewMongoConnection creates a new MongoDB connection with connection pooling
func NewMongoConnection(uri string, dbName string) (*MongoConnection, error) {
	if uri == "" {
		uri = "mongodb://localhost:27017"
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// Connection pooling options
	opts := options.Client().
		ApplyURI(uri).
		SetMaxPoolSize(100).
		SetMinPoolSize(10).
		SetMaxConnIdleTime(5 * time.Minute).
		SetServerSelectionTimeout(5 * time.Second)

	client, err := mongo.Connect(ctx, opts)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to MongoDB: %w", err)
	}

	// Verify connection
	ctx, cancel = context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err = client.Ping(ctx, readpref.Primary()); err != nil {
		client.Disconnect(context.Background())
		return nil, fmt.Errorf("failed to ping MongoDB: %w", err)
	}

	log.Printf("✓ MongoDB connected successfully to %s\n", uri)

	return &MongoConnection{
		Client:   client,
		Database: client.Database(dbName),
	}, nil
}

// Close closes the MongoDB connection
func (mc *MongoConnection) Close(ctx context.Context) error {
	if mc.Client != nil {
		return mc.Client.Disconnect(ctx)
	}
	return nil
}

// Health checks MongoDB connectivity
func (mc *MongoConnection) Health(ctx context.Context) error {
	if mc.Client == nil {
		return fmt.Errorf("MongoDB client not initialized")
	}

	ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()

	return mc.Client.Ping(ctx, readpref.Primary())
}

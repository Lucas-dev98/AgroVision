# Build stage
FROM golang:1.21-alpine AS builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o nutrition_service ./cmd

# Final stage
FROM alpine:latest

WORKDIR /root/

COPY --from=builder /app/nutrition_service .

EXPOSE 8088

CMD ["./nutrition_service"]

# Build stage
FROM golang:1.21-alpine as builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o api_gateway ./cmd/main

# Final stage
FROM alpine:latest

WORKDIR /root/

COPY --from=builder /app/api_gateway .

EXPOSE 8000

CMD ["./api_gateway"]

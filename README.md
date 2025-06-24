# Morse Code Decoder API

A Flask-based API service that decodes Morse code messages and extracts hidden flags.

## Features

- Decodes standard Morse code messages
- Extracts flag patterns from decoded text
- Supports dots (.), dashes (-), spaces between letters, and slashes (/) for word boundaries
- Configurable Morse code mapping via ConfigMap
- Health check endpoint
- Ready for OpenShift deployment

## API Endpoints

### POST /decode-morse
Decodes a Morse code message and extracts any hidden flags.

**Request Body:**
```json
{
  "message": "... --- ... -.. . -.-. --- -.. . -.-. .... .- .-.. .-.. . -. --. ."
}
```

**Response:**
```json
{
  "decoded_text": "SOS DECODE CHALLENGE",
  "flag_found": true,
  "flag": "FLAG{example_flag}"
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## Deployment

### Prerequisites
- OpenShift CLI (oc)
- Docker
- Access to the OpenShift cluster

### Steps

1. **Build the Docker image:**
   ```bash
   docker build -t morse-decoder:latest .
   ```

2. **Tag and push to registry (if needed):**
   ```bash
   docker tag morse-decoder:latest <registry>/morse-decoder:latest
   docker push <registry>/morse-decoder:latest
   ```

3. **Deploy to OpenShift:**
   ```bash
   # Create ConfigMap
   oc apply -f k8s-configmap.yaml
   
   # Deploy application
   oc apply -f k8s-deployment.yaml
   ```

4. **Update the Route hostname:**
   Replace `playerX` in the Route with your actual player number.

## Configuration

The Morse code mapping is stored in a ConfigMap named `morse-code` with a CSV file containing character-to-Morse mappings. The application will automatically load this mapping on startup.

## Testing

You can test the API locally by running:
```bash
python app.py
```

Then send a POST request to `http://localhost:8080/decode-morse` with a JSON body containing the Morse message.

## Flag Patterns

The API looks for the following flag patterns in decoded text:
- `FLAG{...}`
- `flag{...}`
- `FLAG: ...`
- `flag: ...`
- `CTF{...}`
- `ctf{...}`

## Example Usage

```bash
curl -X POST https://morse-playerX.apps.cluster-fcdlf.fcdlf.sandbox2074.opentlc.com/decode-morse \
  -H "Content-Type: application/json" \
  -d '{"message": "... --- ... -.. . -.-. --- -.. . -.-. .... .- .-.. .-.. . -. --. ."}'
``` 
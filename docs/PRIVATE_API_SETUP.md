# Setting Up Private API for Code Protection

If you want to keep your Selective Salience algorithm private, set up a private API model.

## Architecture

```
┌─────────────────┐         ┌──────────────────┐
│  Public PyPI    │         │  Private API     │
│  Package        │────────▶│  Server          │
│                 │         │                  │
│  - CLI          │         │  - Core          │
│  - Basic utils  │         │    Algorithm     │
│  - API client   │         │  - Advanced      │
└─────────────────┘         │    Features      │
                             └──────────────────┘
```

## Step 1: Create API Service

### API Structure

```python
# instinct8_api/server.py
from fastapi import FastAPI, Header
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI()

class CompressRequest(BaseModel):
    context: List[Dict[str, Any]]
    trigger_point: int
    goal: str
    constraints: List[str]

class CompressResponse(BaseModel):
    compressed: str
    salience_set: List[str]

@app.post("/api/v1/compress")
async def compress(
    request: CompressRequest,
    authorization: str = Header(None)
):
    """Compress context using private Selective Salience algorithm."""
    # Verify API key
    if not verify_api_key(authorization):
        return {"error": "Invalid API key"}, 401
    
    # Use PRIVATE algorithm (not in public package)
    from instinct8_core.selective_salience import SelectiveSalienceStrategy
    
    strategy = SelectiveSalienceStrategy()
    strategy.initialize(request.goal, request.constraints)
    compressed = strategy.compress(request.context, request.trigger_point)
    
    return CompressResponse(
        compressed=compressed,
        salience_set=strategy.salience_set
    )
```

## Step 2: Refactor Public Package

### Thin Client (Published to PyPI)

```python
# selective_salience/api_client.py
import requests
from typing import List, Dict, Any

class Instinct8APIClient:
    def __init__(self, api_key: str, api_url: str = "https://api.instinct8.ai"):
        self.api_key = api_key
        self.api_url = api_url
    
    def compress(
        self,
        context: List[Dict[str, Any]],
        trigger_point: int,
        goal: str,
        constraints: List[str]
    ) -> str:
        """Call private API for compression."""
        response = requests.post(
            f"{self.api_url}/api/v1/compress",
            json={
                "context": context,
                "trigger_point": trigger_point,
                "goal": goal,
                "constraints": constraints
            },
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        response.raise_for_status()
        return response.json()["compressed"]
```

### Updated Agent (Hybrid)

```python
# selective_salience/compressor.py
class SelectiveSalienceCompressor:
    def __init__(self, api_key: Optional[str] = None):
        if api_key:
            self.client = Instinct8APIClient(api_key)  # Use private API
            self.mode = "api"
        else:
            self.client = LocalBasicCompression()  # Basic local version
            self.mode = "local"
    
    def compress(self, context, trigger_point):
        if self.mode == "api":
            return self.client.compress(...)  # Calls private API
        else:
            return self.client.compress_local(...)  # Basic version
```

## Step 3: Deploy API Service

### Using Cloud Services

**Option A: AWS Lambda + API Gateway**
```bash
# Deploy as serverless function
serverless deploy
```

**Option B: Docker + Cloud Run**
```dockerfile
FROM python:3.9
COPY instinct8_api/ /app/
RUN pip install -r requirements.txt
CMD ["uvicorn", "server:app", "--host", "0.0.0.0"]
```

**Option C: Traditional Server**
```bash
# Deploy to your server
gunicorn server:app
```

## Step 4: Update Public Package

### What Goes to PyPI

```
instinct8-agent/  # Public package
├── selective_salience/
│   ├── __init__.py
│   ├── api_client.py      # API client (public)
│   ├── compressor.py      # Hybrid client (public)
│   └── basic_compression.py  # Basic local version (public)
├── cli.py                  # CLI (public)
└── pyproject.toml
```

### What Stays Private

```
instinct8_core/  # Private repository
├── selective_salience.py   # Core algorithm (PRIVATE)
├── advanced_features.py     # Advanced features (PRIVATE)
└── model_prompts.py        # Fine-tuned prompts (PRIVATE)
```

## Step 5: User Experience

### Free Tier (Local Only)

```bash
# Install from PyPI
pip install instinct8-agent

# Use basic features (no API key needed)
instinct8 "create endpoint"
```

### Pro Tier (API Access)

```bash
# Install from PyPI
pip install instinct8-agent

# Use with API key (calls private API)
export INSTINCT8_API_KEY="your-key"
instinct8 "create endpoint"  # Uses private algorithm
```

## Benefits

✅ **Code Protection**: Core algorithm never leaves your servers  
✅ **Monetization**: Can charge for API access  
✅ **Updates**: Update algorithm without republishing  
✅ **Analytics**: Track usage and improve  
✅ **Control**: Can limit/rate limit usage  

## Costs

- API infrastructure costs
- Server maintenance
- More complex architecture
- Need to handle API keys/auth

## Alternative: Gradual Migration

1. **Phase 1**: Publish open source version
2. **Phase 2**: Add API option for advanced features
3. **Phase 3**: Move core algorithm to API
4. **Phase 4**: Keep basic version open source, advanced via API

This lets you:
- Build community with open source
- Protect advanced features
- Monetize premium features

import time
import uuid

import jwt  # PyJWT
from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# ---------- Q3 config ----------
EMAIL = "23f2005605@ds.study.iitm.ac.in"
ALLOWED_ORIGIN = "https://dash-ueec3v.example.com"

# ---------- Q4 config ----------
ISSUER = "https://idp.exam.local"
AUDIENCE = "tds-n1s9moa0.apps.exam.local"
PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2okOHspNjgA+2rTLbeuY
cxiP/hG8C6Sb9iwg3yiLAA4HCnpITcbWCSelbvbYGuc3EbNy4xFyf5Cbj5DHJMID
EkryOgyd2giIIIBOUBj8S63uGcnRpOBh9NFatfNwheKuzsPuVNldu6A9cNteNpXc
WyJjG2axVfmq7i6SuKr1JoWYG7xTTAvKPujSl4OtsQfO3h5NepzdfXpr28oNnzfW
ed+zclR6BcmNNo/WVfJ4xyCLSf0BCOgdTgW6PdaChd1l9VDetJZVEgC5tkyvXsfI
SI6iyrYbKR0NEBSqq4XkadEjsCs4F1RncsS4LlgniT7GlkL9Mce3b0wGLs9/7ZIX
dQIDAQAB
-----END PUBLIC KEY-----
"""

app = FastAPI()

# Strict CORS (Q3). Wildcard NAHI.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
)


# X-Request-ID / X-Process-Time har response par (Q3)
@app.middleware("http")
async def add_headers(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = str(uuid.uuid4())
    response.headers["X-Process-Time"] = f"{time.perf_counter() - start:.6f}"
    return response


# ---------- Q3: /stats ----------
@app.get("/stats")
def stats(values: str = Query("")):
    try:
        nums = [int(v.strip()) for v in values.split(",") if v.strip()]
    except ValueError:
        return JSONResponse({"error": "values must be comma-separated integers"}, status_code=400)
    if not nums:
        return JSONResponse({"error": "no values provided"}, status_code=400)
    return {
        "email": EMAIL,
        "count": len(nums),
        "sum": sum(nums),
        "min": min(nums),
        "max": max(nums),
        "mean": sum(nums) / len(nums),
    }


# ---------- Q4: /verify ----------
def invalid():
    return JSONResponse({"valid": False}, status_code=401)


@app.post("/verify")
async def verify(request: Request):
    try:
        body = await request.json()
        token = body.get("token") if isinstance(body, dict) else None
        if not isinstance(token, str) or not token:
            return invalid()
        claims = jwt.decode(
            token,
            PUBLIC_KEY,
            algorithms=["RS256"],
            audience=AUDIENCE,
            issuer=ISSUER,
            options={"require": ["exp", "iss", "aud"]},
        )
        return {
            "valid": True,
            "email": claims.get("email"),
            "sub": claims.get("sub"),
            "aud": claims.get("aud"),
        }
    except Exception:
        return invalid()


@app.get("/")
def root():
    return {"status": "ok"}

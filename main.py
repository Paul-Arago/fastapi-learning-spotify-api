import secrets
import urllib.parse
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SPOTIFY_CLIENT_ID = "5d036ee143d744b6bad8215c679f7a15"
SPOTIFY_CLIENT_SECRET = "d3b545e6881d41e5809a4623c1cf1c30"
SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8000/callback"
FRONTEND_URL = "http://localhost:5173"
spotify_access_token: str | None = None
spotify_refresh_token: str | None = None
oauth_states = set()

@app.get("/login")
async def login():
    state = secrets.token_urlsafe(16)
    oauth_states.add(state)

    scopes = [
        "user-read-private",
        "user-read-email",
        "playlist-read-private",
        "playlist-read-collaborative",
        "playlist-modify-private",
        "playlist-modify-public"
    ]

    params = {
        "response_type": "code",
        "client_id": SPOTIFY_CLIENT_ID,
        "scope": " ".join(scopes),
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "state": state,
    }

    spotify_url = (
        "https://accounts.spotify.com/authorize?"
        + urllib.parse.urlencode(params)
    )

    return RedirectResponse(url=spotify_url)

@app.get("/callback")
async def callback(
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
):
    global spotify_access_token
    global spotify_refresh_token

    if error is not None:
        raise HTTPException(
            status_code=400,
            detail=f"Autorisation refusé : {error}"
        )

    if code is None:
        raise HTTPException(
            status_code=400,
            detail="Code d'autorisation manquant"
        )

    if state is None or state not in oauth_states:
        raise HTTPException(
            status_code=400,
            detail="State invalide"
        )

    oauth_states.remove(state)

    token_url = "https://accounts.spotify.com/api/token"

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": SPOTIFY_REDIRECT_URI,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            token_url,
            data=data,
            auth=(
                SPOTIFY_CLIENT_ID,
                SPOTIFY_CLIENT_SECRET,
            ),
        )

    if response.status_code != 200:
        print("Erreur Spotify token :", response.text)

        raise HTTPException(
            status_code=500,
            detail="Impossible de récupérer le token Spotify"
        )

    token_data = response.json()

    spotify_access_token = token_data["access_token"]
    spotify_refresh_token = token_data.get("refresh_token")
    return RedirectResponse(
        url=f"{FRONTEND_URL}/mainpage"
    )

@app.get("/playlists")
async def get_playlists():
    if spotify_access_token is None:
        raise HTTPException(
            status_code=401,
            detail="Pas encore connecté à Spotify"
        )

    headers = {
        "Authorization": f"Bearer {spotify_access_token}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.spotify.com/v1/me/playlists",
            headers=headers
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail="Impossible de récupérer les playlists"
        )

    return response.json()

@app.get("/playlists/{id}")
async def get_playlist_details(id: str):
    if spotify_access_token is None:
        raise HTTPException(
            status_code=401,
            detail="Pas encore connecté à Spotify"
        )

    headers = {
        "Authorization": f"Bearer {spotify_access_token}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.spotify.com/v1/playlists/{id}",
            headers=headers
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail="Impossible de récupérer la playlist"
        )

    return response.json()

@app.get("/playlists/{id}/tracks")
async def get_tracks(id: str):
    if spotify_access_token is None:
        raise HTTPException(
            status_code=401,
            detail="Pas encore connecté à Spotify"
        )

    headers = {
        "Authorization": f"Bearer {spotify_access_token}"
    }

    # Pagination avec offset, limit etc...
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.spotify.com/v1/playlists/{id}/tracks",
            headers=headers
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail="Impossible de récupérer les pistes"
        )

    return response.json()

@app.get("/user/info")
async def get_user_info():
    if spotify_access_token is None:
        raise HTTPException(
            status_code=401,
            detail="Pas encore connecté à Spotify"
        )

    headers = {
        "Authorization": f"Bearer {spotify_access_token}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.spotify.com/v1/me",
            headers=headers
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail="Impossible de récupérer les informations de l'utilisateur"
        )

    return response.json()
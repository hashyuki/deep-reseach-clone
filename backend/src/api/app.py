import pathlib

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://smith.langchain.com",
        "https://*.langchain.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def create_frontend_router(build_dir="../../frontend/dist"):
    """Reactフロントエンドを提供するルーターを作成

    Args:
        build_dir: Reactビルドディレクトリのパス（このファイルからの相対パス）

    Returns:
        フロントエンドを提供するStarletteアプリケーション
    """
    # Reactビルドディレクトリのパスを取得
    build_path = pathlib.Path(__file__).parent.parent / build_dir

    if not build_path.is_dir() or not (build_path / "index.html").is_file():
        print(
            f"WARN: Frontend build directory not found or incomplete at {build_path}. Serving frontend will likely fail."
        )
        # ビルドが存在しない場合、ダミーのルートを返す
        from starlette.routing import Route

        async def dummy_frontend(request):
            return Response(
                "Frontend not built. Run 'npm run build' in the frontend directory.",
                media_type="text/plain",
                status_code=503,
            )

        return Route("/{path:path}", endpoint=dummy_frontend)

    # 静的ファイルサーバーを作成
    return StaticFiles(directory=build_path, html=True)


# FastAPIにフロントエンドを /app にマウント
app.mount(
    "/app",
    create_frontend_router(),
    name="frontend",
)

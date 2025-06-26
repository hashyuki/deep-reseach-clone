import type { NextRequest } from 'next/server'
import { NextResponse } from 'next/server'

export function middleware(request: NextRequest) {
  // ルートパス（/）にアクセスした場合、/homeにリダイレクト
  if (request.nextUrl.pathname === '/') {
    return NextResponse.redirect(new URL('/home', request.url))
  }
}

export const config = {
  matcher: [
    // すべてのリクエストパスにマッチ（APIルートと静的ファイルを除く）
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
}

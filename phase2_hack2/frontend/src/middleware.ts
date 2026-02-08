/**
 * Next.js middleware - DISABLED
 * Authentication is handled client-side via protected layout
 * using localStorage tokens from FastAPI backend.
 */
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // Pass through all requests - auth handled client-side
  return NextResponse.next();
}

export const config = {
  matcher: [],
};

/**
 * Better Auth API route handler.
 * Handles all authentication endpoints: /api/auth/sign-in, /api/auth/sign-up, etc.
 */
import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth);

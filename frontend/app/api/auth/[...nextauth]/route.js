import NextAuth from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";

// BACKEND_URL is used server-side (NextAuth runs in Node.js, not the browser).
// In Docker, this should be http://backend:8000/api/v1
// Locally, it falls back to localhost.
const API_URL = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const authOptions = {
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        try {
          const res = await fetch(`${API_URL}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              email: credentials.email,
              password: credentials.password,
            }),
          });

          if (!res.ok) {
            const errorData = await res.json();
            throw new Error(errorData?.detail || "Authentication failed");
          }

          const tokens = await res.json();

          // Fetch user details using the access token
          const userRes = await fetch(`${API_URL}/auth/me`, {
            headers: {
              Authorization: `Bearer ${tokens.access_token}`,
            },
          });

          if (!userRes.ok) {
            throw new Error("Failed to fetch user profile");
          }

          const user = await userRes.json();

          return {
            id: user.id,
            email: user.email,
            name: user.username,
            role: user.role,
            accessToken: tokens.access_token,
            refreshToken: tokens.refresh_token,
          };
        } catch (error) {
          throw new Error(error.message);
        }
      }
    })
  ],
  callbacks: {
    async jwt({ token, user, trigger, session }) {
      // Initial sign in
      if (user) {
        token.id = user.id;
        token.email = user.email;
        token.name = user.name;
        token.role = user.role;
        token.accessToken = user.accessToken;
        token.refreshToken = user.refreshToken;
      }

      // If user updates session (e.g. settings)
      if (trigger === "update" && session) {
        token.name = session.name || token.name;
        // update other fields if passed via session update
      }

      // TODO: Handle token rotation here if token expires, 
      // but we will keep it simple for now or rely on Axios interceptor on the client
      return token;
    },
    async session({ session, token }) {
      session.user.id = token.id;
      session.user.email = token.email;
      session.user.name = token.name;
      session.user.role = token.role;
      session.accessToken = token.accessToken;
      session.refreshToken = token.refreshToken;
      return session;
    }
  },
  pages: {
    signIn: "/login",
  },
  session: {
    strategy: "jwt",
  },
  secret: process.env.NEXTAUTH_SECRET || "your-super-secret-nextauth-key-12345",
};

const handler = NextAuth(authOptions);

export { handler as GET, handler as POST };

import express from "express";
import fetch from "node-fetch";

const app = express();
app.use(express.json({ limit: "10mb" }));

const UPSTREAM = process.env.UPSTREAM; // e.g., http://34.123.45.67
const ALLOWED_ORIGINS = "*";

// Basic, adjustable CORS
app.use((req, res, next) => {
  const origin = req.headers.origin || "";
  if (ALLOWED_ORIGINS.includes("*") || ALLOWED_ORIGINS.includes(origin)) {
    res.set("access-control-allow-origin", origin || "*");
    res.set("vary", "Origin");
  }
  res.set("access-control-allow-headers", "Content-Type, Authorization");
  res.set("access-control-allow-methods", "GET,POST,PUT,PATCH,DELETE,OPTIONS");
  if (req.method === "OPTIONS") return res.status(204).end();
  next();
});

// Transparent proxy
app.all("*", async (req, res) => {
  if (!UPSTREAM) return res.status(500).json({ error: "UPSTREAM not set" });
  try {
    const url = `${UPSTREAM}${req.url}`;
    const upstream = await fetch(url, {
      method: req.method,
      headers: Object.fromEntries(
        Object.entries(req.headers)
          .filter(([k]) => !["host", "content-length"].includes(k.toLowerCase()))
      ),
      body: ["GET","HEAD"].includes(req.method) ? undefined : JSON.stringify(req.body),
      redirect: "manual",
    });

    // Pass through key headers
    for (const [k, v] of upstream.headers) {
      if (["content-type","location","cache-control"].includes(k.toLowerCase())) {
        res.set(k, v);
      }
    }
    res.status(upstream.status);
    const buf = await upstream.arrayBuffer();
    res.send(Buffer.from(buf));
  } catch (e) {
    res.status(502).json({ error: "Upstream error", detail: String(e) });
  }
});

const port = process.env.PORT || 8080;
app.listen(port, () => console.log("edge-proxy on " + port));


import express from "express";
import fetch from "node-fetch";

const app = express();

// Capturar raw body sin parsear - soporta JSON, multipart, cualquier tipo
const rawBodySaver = (req, res, next) => {
  const chunks = [];
  req.on('data', chunk => chunks.push(chunk));
  req.on('end', () => {
    req.rawBody = Buffer.concat(chunks);
    next();
  });
};

app.use(rawBodySaver);

const UPSTREAM = process.env.UPSTREAM; // e.g., http://34.123.45.67
const ALLOWED_ORIGINS = "*";

// Basic, adjustable CORS
app.use((req, res, next) => {
  const origin = req.headers.origin || "";
  if (ALLOWED_ORIGINS === "*" || ALLOWED_ORIGINS.includes(origin)) {
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

    // Filtrar y preparar headers para el upstream
    const upstreamHeaders = {};
    const excludeHeaders = ["host", "content-length", "connection", "upgrade", "transfer-encoding", "x-forwarded-for", "x-forwarded-proto", "x-forwarded-host"];

    for (const [key, value] of Object.entries(req.headers)) {
      const lowerKey = key.toLowerCase();
      // Excluir headers que no deben pasarse al upstream
      if (!excludeHeaders.includes(lowerKey)) {
        upstreamHeaders[key] = value;
      }
    }

    // Extraer el host del UPSTREAM (IP del gateway)
    const upstreamUrl = new URL(UPSTREAM);
    upstreamHeaders["Host"] = upstreamUrl.hostname;

    // Asegurar que tenemos User-Agent si no está presente
    if (!upstreamHeaders["user-agent"] && !upstreamHeaders["User-Agent"]) {
      upstreamHeaders["User-Agent"] = "Mozilla/5.0 (compatible; MediSupply-Edge-Proxy/1.0)";
    }

    // No agregar X-Forwarded-* headers - el gateway ya los maneja internamente
    // Esto puede causar que el gateway rechace la petición

    console.log(`Proxying ${req.method} ${req.url} to ${url}`);
    console.log(`Content-Type: ${req.headers["content-type"] || "none"}`);
    console.log(`Body size: ${req.rawBody ? req.rawBody.length : 0} bytes`);

    // Pasar el body raw sin modificar (soporta JSON, multipart, etc.)
    const bodyToSend = ["GET","HEAD","OPTIONS"].includes(req.method)
      ? undefined
      : (req.rawBody && req.rawBody.length > 0 ? req.rawBody : undefined);

    const upstream = await fetch(url, {
      method: req.method,
      headers: upstreamHeaders,
      body: bodyToSend,
      redirect: "follow",
    });

    console.log(`Upstream responded with status ${upstream.status}`);
    console.log(`Upstream response headers:`, Object.fromEntries(upstream.headers));

    // Pass through all headers from upstream
    for (const [k, v] of upstream.headers) {
      // Evitar headers que pueden causar problemas
      if (!["connection", "transfer-encoding", "content-encoding", "location"].includes(k.toLowerCase())) {
        res.set(k, v);
      }
    }

    res.status(upstream.status);

    // Si el upstream devuelve 403, agregar más información de debug
    if (upstream.status === 403) {
      console.error(`403 Forbidden from upstream for ${url}`);
      console.error(`Request headers sent:`, JSON.stringify(upstreamHeaders, null, 2));
      const text = await upstream.text();
      console.error(`Upstream response: ${text}`);

      // Intentar nuevamente sin algunos headers problemáticos
      console.log(`Retrying request without forwarded headers...`);
      const retryHeaders = { ...upstreamHeaders };
      delete retryHeaders["X-Forwarded-For"];
      delete retryHeaders["X-Forwarded-Proto"];
      delete retryHeaders["X-Forwarded-Host"];

      try {
        const retryBody = ["GET","HEAD","OPTIONS"].includes(req.method)
          ? undefined
          : (req.rawBody && req.rawBody.length > 0 ? req.rawBody : undefined);

        const retry = await fetch(url, {
          method: req.method,
          headers: retryHeaders,
          body: retryBody,
          redirect: "follow",
        });
        
        if (retry.status !== 403) {
          console.log(`Retry succeeded with status ${retry.status}`);
          // Pasar la respuesta exitosa
          for (const [k, v] of retry.headers) {
            if (!["connection", "transfer-encoding", "content-encoding"].includes(k.toLowerCase())) {
              res.set(k, v);
            }
          }
          res.status(retry.status);
          const buf = await retry.arrayBuffer();
          return res.send(Buffer.from(buf));
        }
      } catch (retryError) {
        console.error(`Retry failed: ${retryError.message}`);
      }
      
      return res.status(403).json({ 
        error: "Forbidden from upstream",
        upstream_url: url,
        detail: text || "No detail from upstream",
        message: "The GKE Gateway is rejecting the request. Check gateway configuration."
      });
    }
    
    const buf = await upstream.arrayBuffer();
    res.send(Buffer.from(buf));
  } catch (e) {
    console.error(`Proxy error: ${e.message}`, e);
    res.status(502).json({ error: "Upstream error", detail: String(e) });
  }
});

const port = process.env.PORT || 8080;
app.listen(port, () => console.log("edge-proxy on " + port));


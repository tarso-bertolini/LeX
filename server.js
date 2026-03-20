import express from "express";
import { spawn } from "node:child_process";

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json({ limit: "256kb" }));
app.use(express.static("public"));

app.post("/api/compile", (req, res) => {
  const source = String(req.body?.source || "");

  if (!source.trim()) {
    return res.status(400).json({ error: "Provide at least one expression." });
  }

  const child = spawn("python3", ["compiler.py", "--stdin"], {
    cwd: process.cwd(),
    stdio: ["pipe", "pipe", "pipe"],
  });

  let stdout = "";
  let stderr = "";

  child.stdout.on("data", (chunk) => {
    stdout += chunk.toString("utf8");
  });

  child.stderr.on("data", (chunk) => {
    stderr += chunk.toString("utf8");
  });

  child.on("close", (code) => {
    if (code !== 0) {
      return res.status(400).json({ error: stderr || "Compilation failed." });
    }
    return res.json({ assembly: stdout });
  });

  child.stdin.write(source.endsWith("\n") ? source : `${source}\n`);
  child.stdin.end();
});

app.listen(PORT, () => {
  console.log(`Web demo running on http://localhost:${PORT}`);
});

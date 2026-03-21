const sourceEl = document.getElementById("source");
const asmEl = document.getElementById("assembly");
const statusEl = document.getElementById("status");
const compileBtn = document.getElementById("compileBtn");
const sampleBtn = document.getElementById("sampleBtn");
const copyBtn = document.getElementById("copyBtn");

const SAMPLE = `((3.14 2.0 *) (VAR MEM) +)`;
sourceEl.value = SAMPLE;
asmEl.textContent = "Compile output will appear here.";

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.classList.toggle("error", isError);
}

async function compileSource() {
  const source = sourceEl.value;
  setStatus("Compiling...");
  compileBtn.disabled = true;

  try {
    const response = await fetch("/api/compile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Compilation failed.");
    }

    asmEl.textContent = data.assembly;
    setStatus("Compilation succeeded.");
  } catch (error) {
    asmEl.textContent = "";
    setStatus(String(error.message || error), true);
  } finally {
    compileBtn.disabled = false;
  }
}

compileBtn.addEventListener("click", compileSource);

sampleBtn.addEventListener("click", () => {
  sourceEl.value = SAMPLE;
  setStatus("Sample loaded.");
  sourceEl.focus();
});

sourceEl.addEventListener("keydown", (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
    event.preventDefault();
    compileSource();
  }
});

copyBtn.addEventListener("click", async () => {
  const value = asmEl.textContent;
  if (!value.trim()) {
    setStatus("Nothing to copy yet.", true);
    return;
  }

  try {
    await navigator.clipboard.writeText(value);
    setStatus("Assembly copied to clipboard.");
  } catch {
    setStatus("Clipboard copy failed.", true);
  }
});

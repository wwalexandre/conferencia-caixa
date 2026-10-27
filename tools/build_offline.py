# Monta a versao OFFLINE: um unico HTML com todas as bibliotecas embutidas (base64).
# Uso (dentro de tools/):  npm install  &&  python build_offline.py
# Gera ../offline/conferencia-caixa-offline.html a partir de ../index.html. Nenhuma requisicao de rede no arquivo final.
import base64, re, sys
from pathlib import Path

NM = Path(__file__).parent / "node_modules"  # rode "npm install" dentro de tools/ antes
RAIZ = Path(__file__).resolve().parent.parent
ORIG = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "index.html"
SAIDA = Path(sys.argv[2]) if len(sys.argv) > 2 else RAIZ / "offline" / "conferencia-caixa-offline.html"
s = ORIG.read_text(encoding="utf-8")

def b64(p): return base64.b64encode((NM / p).read_bytes()).decode()

LIBS = [  # carregadas em ordem como <script>
    ("b64-pdf", "pdfjs-dist/build/pdf.min.js"),
    ("b64-pdfworker", "pdfjs-dist/build/pdf.worker.min.js"),   # roda na mesma aba (sem Worker)
    ("b64-xlsx", "xlsx/dist/xlsx.full.min.js"),
    ("b64-exceljs", "exceljs/dist/exceljs.min.js"),
    ("b64-zxing", "zxing-wasm/dist/iife/reader/index.js"),
    ("b64-tess", "tesseract.js/dist/tesseract.min.js"),
]
DADOS = [
    ("b64-zxingwasm", "zxing-wasm/dist/reader/zxing_reader.wasm"),
    ("b64-tesscore", "tesseract.js-core/tesseract-core-simd-lstm.wasm.js"),
    ("b64-tessworker", "tesseract.js/dist/worker.min.js"),
    ("b64-por", "@tesseract.js-data/por/4.0.0_best_int/por.traineddata.gz"),
]

def troca(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:80], s.count(a))
    s = s.replace(a, b)

# 1) tira os <script src> dos CDNs
s, k = re.subn(r'<script src="https://(?:cdnjs\.cloudflare\.com|cdn\.jsdelivr\.net)/[^"]+"></script>\n', "", s)
assert k == 5, k

# 2) configuracao do app para offline
troca('''const TESS = {
  workerPath: "https://cdn.jsdelivr.net/npm/tesseract.js@5.1.1/dist/worker.min.js",
  corePath: "https://cdn.jsdelivr.net/npm/tesseract.js-core@5.1.1",
  langPath: "https://cdn.jsdelivr.net/npm/@tesseract.js-data/por@1.0.0/4.0.0_best_int",
};
const ZXING_WASM = "https://cdn.jsdelivr.net/npm/zxing-wasm@2.2.4/dist/reader/zxing_reader.wasm";
pdfjsLib.GlobalWorkerOptions.workerSrc = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";''',
'''// VERSAO OFFLINE: as bibliotecas vem embutidas neste arquivo (window.OFFLINE), nada e baixado.
// O leitor de PDF roda na propria aba (pdfjsWorker), o OCR num Worker montado a partir dos dados embutidos.
const TESS = { workerPath: window.OFFLINE.tessWorkerURL, workerBlobURL: false,
  langPath: "https://offline.invalid/lang", cacheMethod: "none", gzip: true };''')
troca('''      overrides: { locateFile: (path, prefix) => (path.endsWith(".wasm") ? ZXING_WASM : prefix + path) },''',
      '''      overrides: { wasmBinary: window.OFFLINE.zxingWasm },''')
troca('''Verifique a internet (ou se a rede da empresa bloqueia cdn.jsdelivr.net) e tente de novo.''',
      '''Feche e abra o arquivo de novo; se persistir, use o Edge ou o Chrome atualizados.''')
troca('''<footer>Os arquivos ficam no seu computador: o site só baixa as bibliotecas de leitura (PDF, QR, Excel e OCR) na primeira vez.
    <a class="baixar" href="offline/conferencia-caixa-offline.html" download="Conferencia do Caixa (offline).html">Baixar a versão offline</a>: um arquivo só, abre com dois cliques e funciona sem internet.</footer>''',
      '''<footer>Versão offline: tudo roda neste computador, sem internet. Nenhum arquivo é enviado para lugar nenhum.</footer>''')
troca('''<span class="privacy">🔒 Os arquivos são processados neste navegador. Nada é enviado para a internet.</span>''',
      '''<span class="privacy">🔒 Versão offline: funciona sem internet. Os arquivos não saem deste computador.</span>''')

# 3) o script do app vira texto, executado depois que as bibliotecas carregarem
i = s.rindex("<script>\n\"use strict\";")
s = s[:i] + '<script type="text/plain" id="app">' + s[i + len("<script>"):]

# 4) blocos base64 + carregador
blocos = "".join(f'<script type="application/octet-stream" id="{i}">{b64(p)}</script>\n' for i, p in LIBS + DADOS)
carregador = r'''<script>
"use strict";
(async () => {
  const bytes = (id) => { const t = atob(document.getElementById(id).textContent.trim()); const u = new Uint8Array(t.length);
    for (let i = 0; i < t.length; i++) u[i] = t.charCodeAt(i); return u; };
  const rodar = (conteudo) => new Promise((ok, erro) => {
    const sc = document.createElement("script");
    sc.src = URL.createObjectURL(new Blob([conteudo], { type: "application/javascript" }));
    sc.onload = ok; sc.onerror = () => erro(new Error("falha ao carregar biblioteca embutida"));
    document.body.appendChild(sc);
  });
  const st = document.getElementById("status");
  try {
    st.textContent = "Carregando as bibliotecas embutidas...";
    for (const id of ["b64-pdf", "b64-pdfworker", "b64-xlsx", "b64-exceljs", "b64-zxing", "b64-tess"]) await rodar(bytes(id));
    // OCR: Worker = idioma portugues embutido (no lugar do download) + nucleo do Tesseract + script do worker
    const por = document.getElementById("b64-por").textContent.trim();
    const prefixo = `const __POR="${por}";const __f=self.fetch.bind(self);` +
      `self.fetch=(u,o)=>String(u).indexOf("por.traineddata")>=0?Promise.resolve(new Response(Uint8Array.from(atob(__POR),c=>c.charCodeAt(0)))):__f(u,o);\n`;
    window.OFFLINE = {
      zxingWasm: bytes("b64-zxingwasm"),
      tessWorkerURL: URL.createObjectURL(new Blob([prefixo, bytes("b64-tesscore"), "\n", bytes("b64-tessworker")], { type: "application/javascript" })),
    };
    ["b64-pdf", "b64-pdfworker", "b64-xlsx", "b64-exceljs", "b64-zxing", "b64-tess", "b64-zxingwasm", "b64-tesscore", "b64-tessworker", "b64-por"]
      .forEach((id) => document.getElementById(id).remove()); // libera memoria
    await rodar(document.getElementById("app").textContent);
    st.textContent = "";
  } catch (e) {
    console.error(e);
    st.textContent = "Não consegui carregar as bibliotecas embutidas. Use o Edge ou o Chrome atualizados.";
  }
})();
</script>
'''
troca("</body>", blocos + carregador + "</body>")
SAIDA.write_text(s, encoding="utf-8")
print(SAIDA, f"{SAIDA.stat().st_size / 1e6:.1f} MB")

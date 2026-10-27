# Conferência do Caixa

**[Abrir a ferramenta](https://wwalexandre.github.io/conferencia-caixa/)**

Ferramenta que roda no navegador para tirar do PDF diário do caixa de cada loja os pares **número de transação ↔ código do QR do comprovante da maquininha**, sem precisar ler QR por QR com o celular.

![Tela da Conferência do Caixa com dados fictícios](docs/tela.png)

## O problema

Todo dia cada loja envia o PDF do fechamento do caixa: o resumo do caixa, o recibo da boutique de cada venda (com o número de transação do SAP) e a DANFE com o comprovante da maquininha colado (com o QR do pagamento). Para comprovar que cada transação foi paga, alguém precisava ler cada QR com o celular e anotar o código ao lado da transação no Excel, venda por venda, loja por loja.

## Como funciona

1. Arraste o PDF do caixa. Pode ser de várias lojas de uma vez.
2. A ferramenta classifica cada página:
   - **Resumo do caixa:** usado para conferir se a quantidade de vendas bate.
   - **Recibo da boutique:** lê o "Número de transação" e o número da NF-e (OCR).
   - **DANFE:** lê o número da nota pelo código de barras e o QR do comprovante da maquininha colado nela.
3. Liga o recibo e a DANFE da mesma venda pelo **número da nota**, mesmo que a ordem das páginas varie. O QR da etiqueta do produto é ignorado.
4. Gera a lista transação + QR para copiar e colar no Excel, ou um Excel completo com abas de resultado, pendências e resumo.

**Opcional:** colocando o cash report exportado do SAP, a ferramenta também confere se cada transação está no SAP e se o valor da nota bate com o "Amount".

## O que aparece no resultado

| Status | Significado |
|---|---|
| OK: transação + QR | A venda tem número de transação e código do QR do pagamento |
| QR do comprovante não lido | A DANFE foi encontrada, mas o QR não pôde ser lido |
| DANFE desta venda não encontrada | O recibo não tem a nota correspondente no PDF |
| Nota sem recibo | A DANFE não tem o recibo com o número de transação |
| Transação repetida no PDF | A mesma transação aparece mais de uma vez |
| Transação não está no SAP / Valor diferente do SAP | Só quando o cash report do SAP é usado |

O valor da nota só é usado quando a leitura é confiável (o mesmo valor aparece mais de uma vez na DANFE). Se não for, aparece "não lido", nunca um valor inventado.

## Privacidade

Os arquivos são processados no próprio navegador. Nada é enviado para a internet: a página só baixa as bibliotecas de leitura (PDF, QR, Excel e OCR) na primeira vez. Não suba PDFs ou planilhas reais neste repositório.

## Tecnologias

- HTML, CSS e JavaScript, em um único arquivo
- [PDF.js](https://mozilla.github.io/pdf.js/) para ler os PDFs
- [zxing-wasm](https://github.com/Sec-ant/zxing-wasm) para ler os QR codes e o código de barras da DANFE
- [Tesseract.js](https://tesseract.projectnaptha.com/) para o OCR do recibo e da DANFE
- [SheetJS](https://sheetjs.com/) e [ExcelJS](https://github.com/exceljs/exceljs) para ler o cash report e gerar o Excel

## Como usar

**Online:** https://wwalexandre.github.io/conferencia-caixa/

**Offline (recomendado para uso na empresa):** no rodapé do site, clique em **Baixar a versão offline**, ou baixe [`offline/conferencia-caixa-offline.html`](offline/conferencia-caixa-offline.html). É um arquivo só, com todas as bibliotecas dentro: salve numa pasta, abra com dois cliques no Edge ou no Chrome e use sem internet. Ele não instala nada e não faz nenhum acesso à rede.

## Versão offline: como é gerada

O arquivo offline é montado a partir do `index.html` pelo script `tools/build_offline.py`, que embute as mesmas versões das bibliotecas usadas pelo site:

```
cd tools
npm install
python build_offline.py
```

Sempre que o `index.html` mudar, gere o arquivo offline de novo e publique os dois juntos.

---

Feito por [Alexandre Wang](https://alexandrewang.vercel.app), Supply Chain Analytics e Automação.

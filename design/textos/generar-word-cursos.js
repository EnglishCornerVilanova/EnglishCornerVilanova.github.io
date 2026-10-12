// Word para Sònia: propuestas para ampliar las tarjetas de «Cursos» (SEO, octubre 2026).
// Uso: node generar-word-cursos.js content/ca.json salida.docx   (necesita el paquete docx)
const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType,
  BorderStyle, HeadingLevel } = require('docx');
const ca = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const OUT = process.argv[3];
const items = ca.courses.items;
const plain = s => s.replace(/<\/p><p>/g, '\n').replace(/<[^>]+>/g, '');

// [actual, novetat] · el text entre [[ ]] és un buit a confirmar
const P = [
  { i: 0, add: "Els alumnes s'agrupen per nivell, no només per edat, i fan controls periòdics amb informes d'avaluació per a les famílies. A partir dels 7 anys poden presentar-se als primers exàmens oficials de Cambridge (Young Learners)." },
  { i: 1, add: "Els grups es fan per nivell, amb controls periòdics i informes d'avaluació. Practiquem amb models reals d'examen per preparar l'A2 Key, el B1 Preliminary i el B2 First, útils per a l'institut, els cicles formatius i, més endavant, la universitat." },
  { i: 2, add: "Hi ha grups de tots els nivells, des de principiants fins al C1. Podeu venir per guanyar fluïdesa, per la feina o per certificar el nivell (B1, B2 o C1), útil per a oposicions, promoció interna i màsters." },
  { i: 3, add: "Us orientem sobre quin examen convé i quan presentar-s'hi, i ens encarreguem de la inscripció.", nota: "Aquesta targeta es va decidir deixar-la com està. La frase és opcional: si no la voleu, esborreu-la." },
  { i: 4, add: "Es fan a l'estiu, en grups per nivell i edat. Són ideals per preparar un examen o per no perdre el ritme durant les vacances." },
  { i: 5, add: "Són classes individuals per preparar un examen o una oposició, millorar l'anglès de la feina o recuperar el ritme. Fixem junts els continguts." },
];
const COMMON = "Per començar, fem una prova de nivell sense compromís.";

const grey = t => new TextRun({ text: t, color: '777777', size: 20 });
function runs(text, color) {
  const out = [];
  text.split(/(\[\[[^\]]+\]\])/).forEach(part => {
    if (!part) return;
    const m = part.match(/^\[\[(.+)\]\]$/);
    out.push(m ? new TextRun({ text: '[CONFIRMAR: ' + m[1] + ']', bold: true, highlight: 'yellow', size: 22 })
               : new TextRun({ text: part, color, size: 22 }));
  });
  return out;
}
const cell = (children, w, fill) => new TableCell({ children, width: { size: w, type: WidthType.DXA },
  shading: fill ? { type: ShadingType.CLEAR, fill } : undefined, margins: { top: 100, bottom: 100, left: 140, right: 140 } });

const body = [
  new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun({ text: 'English Corner · Ampliació dels cursos', size: 40, bold: true })] }),
  new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: "Proposta del 12 d'octubre de 2026. Català; després ho passarem al castellà i a l'anglès.", color: '666666' })] }),
  new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: "Per què: Google i els assistents d'IA entenen millor què oferiu si cada curs explica edats, grups, mètode i com començar. Ara les targetes tenen una o dues frases; la proposta n'hi afegeix dues o tres." })] }),
  new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: "Com fer-ho: el Control de canvis està activat. Editeu només la columna «Proposta». El text en ", }), new TextRun({ text: 'negre', bold: true }), new TextRun({ text: " és el que ja surt al web; el text en " }), new TextRun({ text: 'blau', color: '1F4FA8', bold: true }), new TextRun({ text: " és nou. No hi ha xifres d'alumnes ni horaris." })] }),
  new Paragraph({ spacing: { after: 240 }, children: [new TextRun({ text: "Totes les targetes acabarien amb la mateixa frase: «" + COMMON + "»" })] }),
];
for (const p of P) {
  const it = items[p.i];
  body.push(new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 80 },
    children: [new TextRun({ text: it.title + (it.tag ? '  ·  ' + it.tag.replace('→', '–') : ''), bold: true, size: 28 })] }));
  if (p.nota) body.push(new Paragraph({ spacing: { after: 80 }, children: [new TextRun({ text: p.nota, italics: true, color: '9A5B00', size: 20 })] }));
  const actual = plain(it.desc).split('\n');
  body.push(new Table({ width: { size: 9600, type: WidthType.DXA }, columnWidths: [2400, 7200], rows: [
    new TableRow({ children: [cell([new Paragraph({ children: [grey('Proposta')] })], 2400, 'F2F2F0'),
      cell([...actual.map(t => new Paragraph({ spacing: { after: 80 }, children: runs(t, '12151C') })),
            new Paragraph({ spacing: { after: 80 }, children: runs(p.add, '1F4FA8') }),
            new Paragraph({ children: runs(COMMON, '1F4FA8') })], 7200)] }),
  ] }));
}
const doc = new Document({ features: { trackRevisions: true }, styles: { default: { document: { run: { font: 'Calibri' } } } },
  sections: [{ properties: { page: { margin: { top: 1000, bottom: 1000, left: 1100, right: 1100 } } }, children: body }] });
Packer.toBuffer(doc).then(b => { fs.writeFileSync(OUT, b); console.log('ok'); });

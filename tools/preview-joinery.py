
import base64,html,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'flora/src/main/resources/assets/chromusflora'

def image(path,label,klass):
    data=base64.b64encode(path.read_bytes()).decode()
    return f'<img class="{klass}" alt="{html.escape(label)}" src="data:image/png;base64,{data}">'

def main():
    mapping=json.loads((ROOT/'atelier/joinery/species.json').read_text())
    cards=[]
    lang=json.loads((ASSETS/'lang/pt_br.json').read_text())
    for name,spec in mapping['species'].items():
        title=lang['block.chromusflora.'+name+'_door']
        art=image(ASSETS/f'textures/item/door/{name}.png',title,'door')
        art+=image(ASSETS/f'textures/block/trapdoor/{name}/main.png','Alçapão','trap')
        art+=image(ASSETS/f'textures/block/wood/{name}/planks.png','Tábua existente','wood')
        note=spec.get('adaptation','Motivo da referência adaptado à face retangular do jogo.')
        cards.append(f'<article data-search="{html.escape(name+" "+title)}"><h2>{html.escape(title)}</h2><code>{name}</code><div class="art">{art}</div><p>Prancha {spec.get("reference_sheet",spec["sheet"])} · posição {spec["cell"]}</p><small>{html.escape(note)}</small></article>')
    content='''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ChromusFlora 0.1.2 — 83 madeiras</title><style>body{margin:0;background:#161c20;color:#e8e6df;font:16px system-ui}header{padding:32px;max-width:1000px}h1{font-size:30px}p{line-height:1.5;color:#bec9cd}input{padding:12px;width:min(88%,500px);background:#253239;color:white;border:1px solid #62737c;border-radius:8px}main{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px;padding:0 32px 32px}article{background:#222c32;border:1px solid #3c4b53;border-radius:12px;padding:18px}h2{font-size:17px;margin:0 0 8px}.art{height:264px;display:flex;align-items:center;gap:12px;margin-top:16px}.door{width:112px;height:224px}.trap{width:80px;height:80px}.wood{width:48px;height:48px}img{image-rendering:pixelated}small,code{color:#b4c5bd}article[hidden]{display:none}</style><header><h1>83 madeiras · portas e alçapões</h1><p>ChromusFlora 0.1.2. Texturas finais em 64×64 por bloco; porta completa em 64×128. Cada cartão mostra porta, alçapão e a tábua já existente. A arte foi adaptada das seis referências enviadas; os troncos e as tábuas não foram alterados.</p><p>As janelas são ilustradas na textura opaca. Entalhes, molduras e cristais são detalhes visuais; não emitem luz. Esta prévia mostra texturas, não uma captura do Minecraft.</p><input id="search" type="search" placeholder="Buscar madeira ou nome da porta" aria-label="Buscar madeira"></header><main>'''+''.join(cards)+'''</main><script>document.getElementById('search').addEventListener('input',e=>{let q=e.target.value.toLowerCase();document.querySelectorAll('article').forEach(a=>a.hidden=!a.dataset.search.toLowerCase().includes(q))})</script></html>'''
    (ROOT/'docs/Marcenaria_0.1.2.html').write_text(content,encoding='utf-8')
    print('PASS: 83 final texture cards in docs/Marcenaria_0.1.2.html')
if __name__=='__main__':main()

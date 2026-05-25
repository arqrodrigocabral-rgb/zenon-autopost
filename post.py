# Zenon Autopost - publica 1 post no Instagram (roda no GitHub Actions, sem CORS)
import os, json, random, time, urllib.parse, sys
import requests

GEMINI_KEY = os.environ.get("GEMINI_API_KEY","").strip()
IG_TOKEN   = os.environ.get("IG_ACCESS_TOKEN","").strip()
IG_ID      = os.environ.get("IG_USER_ID","").strip()
GRAPH      = "https://graph.facebook.com/v20.0"

IMG_STYLE = ("fotografia arquitetonica realista, arquitetura biofilica e sensorial, "
 "luz natural suave e quente, materiais naturais (madeira, pedra, linho, barro), "
 "vegetacao integrada, paleta terrosa (carvao, creme, terracota, verde-mata), "
 "atmosfera calma e silenciosa, composicao limpa e editorial, profundidade, "
 "sem pessoas, sem texto, foto vertical")

def load_plan():
    with open(os.path.join(os.path.dirname(__file__),"content_plan.json"), encoding="utf-8") as f:
        return json.load(f)

def pick_theme(plan):
    pilares=[]
    for p in plan["pilares"]:
        pilares += [p]*int(p.get("peso",1))
    p=random.choice(pilares)
    return p["id"], random.choice(p["temas"])

def gemini_caption(tema, pilar):
    if not GEMINI_KEY: return None
    instr=("Voce e o social media da marca de arquitetura zenon co. (arquitetura do sentir, "
      "arte de habitar, biofilia; tom sofisticado, calmo e acolhedor; portugues do Brasil; sem emojis). "
      "Escreva sobre o tema. Responda em EXATAMENTE tres partes separadas por uma linha contendo apenas ---. "
      "Parte 1: titulo curto de 3 a 5 palavras. Parte 2: legenda de 4 a 6 linhas envolventes, "
      "terminando com uma linha de 7 a 10 hashtags. Parte 3: um prompt visual rico em portugues para "
      "gerar a imagem do post (sem texto na imagem). Nao use markdown nem rotulos. "
      "Tema: "+tema+". Pilar: "+pilar+".")
    for model in ["gemini-2.0-flash","gemini-2.5-flash","gemini-1.5-flash"]:
        try:
            url="https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent?key=%s"%(model,GEMINI_KEY)
            r=requests.post(url, json={"contents":[{"parts":[{"text":instr}]}]}, timeout=60)
            if r.status_code!=200:
                print("gemini",model,r.status_code,r.text[:120]); continue
            j=r.json()
            parts=j["candidates"][0]["content"]["parts"]
            t="".join(p.get("text","") for p in parts).strip()
            seg=[x.strip() for x in t.split("---") if x.strip()]
            if len(seg)>=3: return {"titulo":seg[0],"legenda":seg[1],"image_prompt":seg[2]}
            if len(seg)==2: return {"titulo":tema,"legenda":seg[0],"image_prompt":seg[1]}
            return {"titulo":tema,"legenda":t,"image_prompt":tema}
        except Exception as e:
            print("gemini erro",model,e)
    return None

def fallback_caption(tema):
    return {"titulo":tema,
      "legenda":tema+".\n\narquitetura do sentir, arte de habitar.\n\n#arquitetura #arquiteturabiofilica #interiores #design #gestaodeobra #zenonco",
      "image_prompt":tema}

def pollinations_url(prompt):
    enc=urllib.parse.quote(prompt)
    return "https://image.pollinations.ai/prompt/%s?width=1080&height=1350&nologo=true&model=flux&seed=%d"%(enc, random.randint(1,999999))

def warmup(url):
    for i in range(4):
        try:
            r=requests.get(url, timeout=120)
            if r.status_code==200 and len(r.content)>2000:
                print("imagem pronta (%d bytes)"%len(r.content)); return True
        except Exception as e:
            print("warmup",i,e)
        time.sleep(4)
    return False

def publish(image_url, caption):
    r=requests.post(GRAPH+"/"+IG_ID+"/media",
        data={"image_url":image_url,"caption":caption,"access_token":IG_TOKEN}, timeout=120)
    j=r.json()
    if r.status_code!=200: raise RuntimeError("criar midia: "+json.dumps(j))
    cid=j["id"]; print("container:",cid)
    for _ in range(12):
        s=requests.get(GRAPH+"/"+cid, params={"fields":"status_code","access_token":IG_TOKEN}, timeout=60).json()
        if s.get("status_code")=="FINISHED": break
        if s.get("status_code")=="ERROR": raise RuntimeError("container ERROR: "+json.dumps(s))
        time.sleep(5)
    r2=requests.post(GRAPH+"/"+IG_ID+"/media_publish",
        data={"creation_id":cid,"access_token":IG_TOKEN}, timeout=120)
    j2=r2.json()
    if r2.status_code!=200: raise RuntimeError("publicar: "+json.dumps(j2))
    return j2

def main():
    if not (IG_TOKEN and IG_ID):
        print("ERRO: faltam os segredos IG_ACCESS_TOKEN / IG_USER_ID"); sys.exit(1)
    plan=load_plan()
    pilar, tema = pick_theme(plan)
    print("== Tema:", tema, "| Pilar:", pilar)
    c = gemini_caption(tema, pilar) or fallback_caption(tema)
    prompt = c["image_prompt"] + ". " + IMG_STYLE + "."
    img = pollinations_url(prompt)
    print("== Imagem:", img)
    print("== Legenda:\n" + c["legenda"])
    warmup(img)
    res = publish(img, c["legenda"])
    print("== PUBLICADO COM SUCESSO:", json.dumps(res))

if __name__ == "__main__":
    main()

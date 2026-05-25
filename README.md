# Zenon Autopost (nuvem / GitHub Actions)

Publica 1 post no Instagram da @zenon_co automaticamente, nos horarios,
de graca, rodando na nuvem do GitHub (mesmo com seu PC desligado).
Fluxo: escolhe um tema -> Gemini escreve a legenda -> Pollinations gera a imagem
-> publica via Instagram Graph API (no servidor, sem a trava CORS do navegador).

--------------------------------------------------------------------
PASSO 1 - Criar conta no GitHub (gratis)
--------------------------------------------------------------------
- Acesse github.com -> Sign up. Confirme o e-mail.

--------------------------------------------------------------------
PASSO 2 - Criar o repositorio e subir estes arquivos
--------------------------------------------------------------------
- No GitHub: botao "+" (canto superior direito) -> "New repository".
- Nome: zenon-autopost  | deixe PRIVADO | clique "Create repository".
- Na pagina do repo: "uploading an existing file".
- Arraste TODOS os arquivos desta pasta, MANTENDO a estrutura:
  post.py, content_plan.json, requirements.txt
  e a pasta .github/workflows/autopost.yml
  (dica: arraste a pasta inteira; o GitHub mantem os caminhos)
- Clique "Commit changes".

--------------------------------------------------------------------
PASSO 3 - Pegar o TOKEN de 60 dias (o do Explorer dura so ~1-2h)
--------------------------------------------------------------------
O seu app e "inst.zenon" (App ID: 157781778391142).
Voce precisa de 3 coisas: APP ID, CHAVE SECRETA do app, e um TOKEN CURTO (EAA...).
  - APP ID: 157781778391142
  - CHAVE SECRETA: developers.facebook.com -> seu app -> Configuracoes -> Basico -> "Chave secreta do app" (mostrar)
  - TOKEN CURTO: gere no Graph API Explorer (como fizemos)

a) Trocar por um token LONGO (60 dias) - cole no navegador (1 linha):
   https://graph.facebook.com/v20.0/oauth/access_token?grant_type=fb_exchange_token&client_id=157781778391142&client_secret=SUA_CHAVE_SECRETA&fb_exchange_token=SEU_TOKEN_CURTO
   -> a resposta traz "access_token":"EAA....." (esse e o token longo)

b) (Melhor) Pegar um token de PAGINA que NAO expira - cole no navegador:
   https://graph.facebook.com/v20.0/me/accounts?access_token=TOKEN_LONGO_DO_PASSO_a
   -> ache a sua Pagina e copie o "access_token" dela. Esse token de Pagina
      normalmente nao expira. Use ele como IG_ACCESS_TOKEN (mais estavel).

--------------------------------------------------------------------
PASSO 4 - Cadastrar os SEGREDOS no repositorio
--------------------------------------------------------------------
No repo: Settings -> Secrets and variables -> Actions -> "New repository secret".
Crie estes 3:
  - GEMINI_API_KEY   = sua chave do Google AI Studio (a "modelo de imagem gemini")
  - IG_ACCESS_TOKEN  = o token do Passo 3 (de preferencia o de Pagina)
  - IG_USER_ID       = 17841472865982410

--------------------------------------------------------------------
PASSO 5 - Testar e ligar o automatico
--------------------------------------------------------------------
- Aba "Actions" -> se pedir, clique para habilitar os workflows.
- Clique no workflow "zenon-autopost" -> botao "Run workflow" (teste manual).
- Veja o log: deve terminar com "PUBLICADO COM SUCESSO" e o post aparece no perfil.
- A partir dai, ele roda sozinho: seg/qua/sex/dom as 19h (horario de Brasilia).

--------------------------------------------------------------------
AJUSTES
--------------------------------------------------------------------
- Horarios/dias: edite a linha "cron" em .github/workflows/autopost.yml
  (formato UTC; 22:00 UTC = 19:00 BRT). Ex.: "30 21 * * *" = todo dia 18:30 BRT.
- Temas: edite content_plan.json.
- Token: o de Pagina costuma nao expirar; se um dia parar, refaca o Passo 3.

Seguranca: nunca coloque os tokens dentro dos arquivos do repo - so nos SECRETS.

# LLM Service

Backend de agentes especialistas, criado para o projeto (ALTomatic)[https://github.com/piratariaonline/bluesky-altomatic].

Modelos usados:
- **(Salesforce/blip-image-captioning-base)[https://huggingface.co/Salesforce/blip-image-captioning-base]:** para criação de descrição de imagens. Modelo leve que usa CPU ao invés de GPU. A saída é mais simplificada e sem detalhes, mas mantém o custo com processamento e RAM baixo, possibilitando uso dos *free tiers* de cloud.

- **(Helsinki-NLP/opus-mt-tc-big-en-pt)[https://huggingface.co/Helsinki-NLP/opus-mt-tc-big-en-pt]:** para traduções inglês-português. O BLIP é treinado no idioma inglês, esse modelo traduz para 'por' ou 'pob'. Também bastante leve e com uma taxa decente de boas traduções. Possui um limite de 512 tokens (500~600 caracteres), mas é suficiente para a saída do BLIP.

## Recursos

- **/caption:** Recebe um arquivo de imagem e retorna uma descrição em inglês e português do Brasil; aceita apenas JPG e PNG;
- **/batchcaption:** Mesmo do caption, mas recebe até 4 imagens (o limite pode ser ajustado em código);
- **/translate:** Traduz texto de inglês para português do Brasil (pode ser trocado para Portugal em código);

## Uso

- Autentique usando **/login**, as seguintes ENVs são necessárias: `AUTH_USERNAME`,`AUTH_PASSWORD` e `JWT_SECRET`, recomendo usar hashes;
- Passe o token JWT em *Authentication: Bearer* do cabeçalho da requisição.
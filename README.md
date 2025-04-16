# LLM Service

Serviço de LLMs especialistas:
- **Salesforce/blip-image-captioning-base:** para criação de descrição de imagens;
- **Helsinki-NLP/opus-mt-tc-big-en-pt:** para traduções en-pt;

## Recursos

- **/caption:** Recebe um arquivo de imagem e retorna uma descrição em inglês e português do Brasil;
- **/translate:** Traduz texto de inglês para português do Brasil;

## Uso

- Realize autenticação no método **/login** passando usuário e senha previamente configurados;
- Passe o JWT Token gerado em *Authentication: Bearer* do cabeçalho da requisição.
- **/caption** aceita apenas JPG e PNG
- **/translate** tem um limite de 10 mil caracteres
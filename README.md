# Parque dos Números

Nove jogos de matemática para o Fundamental 1 em um circo cartunesco, com animações, personagens diversos e narração em português.

## Jogar

Sites públicos no GitHub Pages:

- [Andre-prof](https://andre-prof.github.io/parque-dos-numeros/)
- [Cet-net](https://cet-net.github.io/parque-dos-numeros/)

Abra `dist/index.html` em um navegador moderno. Não é necessário instalar dependências para jogar; as 28 falas gravadas acompanham o projeto.

Para servir por HTTP, execute na raiz:

```sh
python -m http.server 8766 --directory dist --bind 127.0.0.1
```

Abra http://127.0.0.1:8766.

## Atividades

- Carros de Trombada: adição e subtração, direção e colisão animada.
- Palhaços Saltimbancos: completar quantidades.
- Fábrica de Risadas: grupos iguais e multiplicação.
- Blocos de Sequência: padrões e sequências numéricas.
- Mestres da Bolha: contagem, dezenas e centenas.
- Relógio do Espetáculo: horas e minutos.
- Bilheteria do Circo: dinheiro e troco.
- Tenda das Formas: figuras e propriedades geométricas.
- Balões para Todos: divisão exata por um algarismo, quatro alternativas e distribuição animada.

O jogador informa o nome na abertura. Nome, estrelas e conquistas ficam neste navegador. Há três níveis, tentativas ilimitadas, dicas e controle de voz.

## Narração

As instruções, dicas e incentivos usam o mesmo padrão de narrador aprovado. Na versão estática, os valores específicos dos desafios aparecem em texto; as instruções são gravadas. Não há troca automática para a voz do navegador.

Opcionalmente, o servidor `local_server.py` conecta um Chatterbox já instalado para narrar textos variáveis. Consulte `LEIA-ME.txt` e `voice-tools/LEIA-ME.txt`. A amostra original de voz, os caches privados e o programa antigo não estão incluídos.

## Verificação

```sh
node checks.cjs
```

Verifica operações e alternativas em 13.500 desafios aleatórios nas nove atividades e três níveis.

## Conteúdo

O projeto contém HTML, CSS, JavaScript, artes WebP/SVG, áudios WAV e ferramentas opcionais em Python. Não precisa de etapa de compilação. Os prompts e a direção de arte estão em `dist/assets/ARTE.txt`.

Esta é uma criação moderna inspirada no universo circense do programa antigo, com escolhas pedagógicas próprias; não é uma reprodução integral. O ISO e a análise do programa antigo ficam separados.

## Publicação e licença

Cada atualização na branch `main` verifica os desafios e publica o conteúdo de `dist/` no GitHub Pages por GitHub Actions.

Licenciado sob a [licença MIT](LICENSE).

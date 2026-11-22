# Parque dos Números

Um parque de diversões circense para explorar matemática brincando. O projeto reúne **nove jogos educativos voltados aos alunos do Ensino Fundamental 1 (1º ao 5º ano)**, com desafios de contagem, operações, sequências, geometria, horas e dinheiro.

O leão Leo recebe a criança pelo nome e apresenta um mundo de palhaços, carrinhos e balões. Ilustrações cartunescas, animações e narração em português acompanham as atividades, para que cada resposta faça parte de uma brincadeira.

**[Jogar agora no navegador](https://cet-net.github.io/parque-dos-numeros/)**

Não é necessário criar uma conta, baixar o jogo ou instalar programas para jogar pelo site.

## Para quem e para quê?

O parque foi pensado para crianças dos anos iniciais do Ensino Fundamental e para professores e famílias que procuram atividades lúdicas de matemática. Pode apoiar momentos de prática, revisão e exploração em sala de aula ou em casa, individualmente ou com mediação de um adulto.

A proposta é incentivar a observação, a contagem, o raciocínio e a tentativa de diferentes estratégias. Os três níveis ampliam os números e a complexidade dos desafios; o educador pode escolher o ponto de partida. Os níveis não equivalem rigidamente a um ano escolar, e o jogo não substitui a avaliação ou o acompanhamento pedagógico.

## O que a criança encontra

| Atração | Conteúdos e brincadeira |
| --- | --- |
| Carros de Trombada | Resolver adições e subtrações, escolher a pista e dirigir até o carro com a resposta. |
| Palhaços Saltimbancos | Completar quantidades acrescentando e retirando palhaços. |
| Fábrica de Risadas | Explorar grupos iguais e descobrir totais por adição e multiplicação. |
| Blocos de Sequência | Reconhecer padrões visuais e continuar sequências numéricas. |
| Mestres da Bolha | Contar estrelas e relacionar unidades, dezenas e centenas. |
| Relógio do Espetáculo | Interpretar horas e minutos em um relógio com ponteiros. |
| Bilheteria do Circo | Trabalhar valores em reais, compra de ingressos e cálculo de troco. |
| Tenda das Formas | Reconhecer figuras geométricas e observar suas propriedades. |
| Balões para Todos | Resolver divisões exatas por um algarismo, escolher entre quatro respostas e observar a distribuição igual dos balões. |

## Aprender no próprio ritmo

- Tentativas ilimitadas, dicas e incentivos, sem perda de vidas ou cronômetro.
- Três níveis de desafio, com avanço automático opcional após dois acertos de primeira.
- Estrelas e conquistas por jogador, guardadas no navegador utilizado.
- Personagens de diferentes etnias, todos com os mesmos recursos e acesso às atividades.
- Instruções, dicas e incentivos narrados em português, com controle para desligar a voz.

Na abertura, o jogo pede o nome da criança. O nome e o progresso são armazenados localmente no navegador, sem cadastro. Ao trocar de aparelho ou navegador, esse progresso não é transferido automaticamente.

## Voz e animações

As atividades incluem narração em português e animações que dão vida às descobertas. Ao acertar a divisão, por exemplo, a criança vê os balões serem entregues igualmente. Nos carrinhos, a resposta faz parte da direção e da colisão animada.

## Executar uma cópia local

Baixe ou clone este repositório e abra `dist/index.html` em um navegador moderno. Os arquivos do jogo e as falas gravadas acompanham o projeto.

Se preferir servir por HTTP, execute na raiz:

```sh
python -m http.server 8766 --directory dist --bind 127.0.0.1
```

Depois abra http://127.0.0.1:8766.

## Desenvolvimento e verificação

O jogo usa HTML, CSS e JavaScript, com artes WebP/SVG e áudios WAV. Não exige uma etapa de compilação. As ferramentas opcionais de voz usam Python. A direção de arte está em `dist/assets/ARTE.txt`.

```sh
node checks.cjs
```

O comando verifica operações e alternativas em 13.500 desafios aleatórios, distribuídos pelas nove atividades e três níveis. Cada atualização na branch `main` executa essa verificação e publica `dist/` no GitHub Pages desta conta.

## Origem e licença

Esta é uma criação moderna inspirada no universo circense do programa antigo, com escolhas pedagógicas próprias; não é uma reprodução integral. O ISO, a amostra original de voz e os caches privados não fazem parte deste repositório.

Disponível sob a [licença MIT](LICENSE), que permite usar, estudar, modificar e redistribuir o projeto conforme seus termos.

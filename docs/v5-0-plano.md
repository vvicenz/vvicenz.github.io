# Mundo v5 · Plano de construção (rev. 1)

*Um planeta terrestre simulado do zero; um continente grande, todo jogável, do gelo ao trópico; mana como campo lido do mundo físico.*

**Status:** F0 fechada em 2026-10-28. As decisões da seção 22 estão tomadas; este é o doc-guia de todas as fases. Qualquer mudança passa por aprovação e vira uma nova revisão deste doc.

---

## 1 · Objetivo

Um mundo que nasce de simulação e é crível sem explicação: um leitor que sabe como a Terra funciona reconhece este planeta. O continente de jogo é visto de 4 km/px até 1 m/px, sem emenda e sem contradição entre escalas, no celular. Medieval. A mana existe na ecologia como traço, gancho e ferramenta — nunca como explicação da geografia.

## 2 · Princípios

1. **Física terrestre.** Qualquer desvio da Terra custa explicação ao leitor; só se desvia por decisão explícita e com motivo.
2. **Só coerência é requisito.** Não há meta de forma, área ou altura. Checagens são de forma e de plausibilidade, nunca de número a bater.
3. **O que sair saiu — mas a semente é escolha.** Rodamos várias sementes e escolhemos o planeta; não ajustamos constantes para forçar resultado.
4. **Cada camada lê só a de cima.** Astros → planeta → tectônica → clima → água e gelo → costa → solo e bioma → vida → mana → povo. Nada "de baixo" corrige "de cima".
5. **Mana é campo, não estoque.** Propriedade do lugar, lida do mundo físico pronto. Não se gasta, não se acumula, não se extrai; a física não a vê.
6. **Uma semente, coordenadas em metros, determinismo por bloco.**
7. **O mês existe desde o começo** (chuva, neve, cheia, gelo, folha, maré).
8. **Teste terrestre antes do planeta.** Cada módulo que puder rodar sobre dados da Terra roda primeiro nela; se não reproduz a Terra em forma, não roda no mundo.
9. **Entrega visível por fase, aprovação antes de seguir.**

## 3 · Astros e órbita

| Item | Valor |
|---|---|
| Estrela | tipo solar; fluxo no topo da atmosfera igual ao da Terra |
| Órbita | ano de 360 dias; excentricidade 0,017; periélio no inverno do norte (estações do norte e do sul diferem um pouco) |
| Rotação | dia de 24 h, prógrada (sol nasce a leste) |
| Obliquidade | 23,5° |
| Lua | uma, do tamanho e distância da nossa; lunação de 30 dias |
| Calendário | 12 meses × 30 dias, meses em fase com a lua |

Saídas: insolação por latitude, dia e hora; duração do dia; dias e noites polares; fases da lua; eclipses; marés de sizígia e quadratura; calendário.

## 4 · Planeta

| Item | Valor |
|---|---|
| Raio | 6.371 km, 1 g, massa e densidade terrestres |
| Atmosfera | composição, pressão e estufa terrestres |
| Oceano | volume terrestre; nível do mar sai do volume e da hipsometria |
| Terra total | ~20 % da superfície: continente de jogo + continente polar sul sob gelo + 1–2 continentes que nunca aparecem (só em resolução grossa, sem história) + ilhas e arquipélagos |

Os continentes invisíveis existem para dar oceano, correntes e ventos terrestres e um "além-mar" verossímil. Nada jogável depende deles.

## 5 · Continente de jogo

| Item | Valor |
|---|---|
| Área | ~25 M km² (entre América do Norte e África) |
| Latitudes | ~78° N a ~15° S: cruza o equador, dois hemisférios de estações, verão em dezembro no sul |
| Forma | sai da tectônica; a semente escolhida é a que der cobertura de biomas com forma crível (seção 11) |
| Jogável | todo ele, do gelo ao trópico, até 1 m/px |
| Escala humana | a pé 25–35 km/dia pela superfície de custo (seção 16); cruzar de norte a sul leva meses |

## 6 · Tectônica e geologia

Simulação no globo inteiro (grade esférica). Não há borda.

| Entrada | Valor |
|---|---|
| Placas | rotações de Euler na esfera; número sorteado entre 8 e 14 para o planeta |
| Crátons iniciais | 3 a 6 blocos de crosta velha, sorteados; a colisão entre eles faz serras interiores e escudos |
| Tempo | 500 Ma em passos de 1 Ma; campo de forças do manto redesenhado a cada 50 Ma, com transição suave |
| Processos | dorsal, subducção, arco vulcânico, colisão (empilhamento com conservação de volume, teto de 70 km), rifte (fator de estiramento sorteado 1,3–2,5), ciclo de Wilson (rifte → oceano estreito → fechamento → sutura), 2–4 pontos quentes fixos (cadeias de ilhas, traps, domos), velocidade ≤ 8 cm/ano |
| Isostasia | flexural, espessura elástica por idade e temperatura da litosfera (escudo ~80 km, rifte ~15 km): antepaís, ombro de rifte, planície costeira |
| Subsidência térmica | crosta estirada e fundo oceânico afundam com √(idade): plataforma, talude, abissal |
| Erosão de longo prazo | lei de potência de fluxo + difusão de encosta, com **deposição** por conservação de massa (planícies, antepaís, deltas, plataforma, bacias fechadas); chuva de cada época vinda do clima, em duas passadas |
| Litologia | mapa de rocha com idade e tipo (ígnea, sedimentar clástica, carbonato, evaporito, metamórfica, vulcânica); erodibilidade por tipo → escarpas, cuestas, mesas, quedas, carste e cavernas, inselbergs, traps |
| Saídas | relevo, batimetria, rocha, idade, falhas ativas, vulcões (ativos/extintos), fluxo geotérmico, zonas sísmicas, províncias metalogenéticas |

## 7 · Atmosfera

Objetivo: circulação **emergente**, não prescrita.

- **Plano A:** modelo de circulação geral de baixa resolução (~5°, tipo PlaSim) com a topografia e o oceano de placa deste planeta. Células, jatos, monções, trilhas de tempestade e altas de inverno nascem da física. Primeira sessão da fase é um teste de 1 h: compila e roda aqui? **Teste terrestre:** rodar primeiro com a topografia da Terra e comparar o Köppen resultante com o real.
- **Plano B (se A não couber):** balanço de energia por latitude + transporte de umidade + células dimensionadas pela escala do planeta + baixa térmica de verão/alta de inverno sobre terra. Coerente, roda em minutos.
- **Downscaling** sobre o continente a 500 m: lapse rate 6,5 °C/km, subida orográfica, sombra de chuva, continentalidade, brisa, neblina costeira em ressurgência, efeito de lago.
- **Saídas mensais:** temperatura (média, mínima, máxima), chuva, neve, vento (direção e força: moinho, vela, dunas), umidade, evaporação, nebulosidade, dias de geada, estação de crescimento, zonas de ciclone tropical (mar > 26 °C fora do equador), zonas de tornado e granizo, regime de seca.

## 8 · Oceano e gelo

- Oceano de placa + giros por vento (Sverdrup/Stommel): corrente quente de borda oeste (costa leste do continente), ressurgência fria de borda leste (costa oeste), correntes polares; temperatura da superfície do mar por mês.
- Gelo marinho por mês; calota no continente polar; icebergs e limite de navegação por mês.
- Mares interiores: salinidade pela soleira do estreito e por evaporação × rios (do Mediterrâneo ao Báltico); gelo de inverno nos de alta latitude.
- **Ciclos glaciais:** últimos 2 Ma com ciclos de ~100 ka forçados pela órbita; mantos de gelo pela linha de equilíbrio; erosão glacial (vales em U, fiordes, sobreescavação), morenas, planícies de lavagem, loess a sotavento, rebote isostático, baixo-mar de −120 m entalhando a plataforma; refúgios biológicos. O "presente" é um interglacial.

## 9 · Hidrologia

- Balanço hídrico mensal em balde (chuva − evapotranspiração − solo, neve por grau-dia); roteamento; vazão por mês; cheia e seca; largura e profundidade pela geometria hidráulica; navegabilidade por vazão e declividade; planícies de inundação.
- **Água subterrânea:** aquíferos por litologia e recarga; nascentes; profundidade do lençol (poços); oásis em deserto onde o lençol aflora; rios que somem em carste.
- Lagos de cinco origens: rifte, afundamento, bacia fechada (transbordo ou sal por chuva × evaporação), glacial, caldeira. Oxbows e pântanos na escala fina.
- Permafrost (contínuo com média anual < −7 °C), termocarste, linha das árvores (mês mais quente ~10 °C), geleiras de montanha (acumulação > ablação), neve sazonal e avalanche.
- Quedas em knickpoints de litologia e em vales suspensos glaciais.

## 10 · Costa

- Ondas pelo vento e pelo fetch; corrente litorânea; maré da lua (amplitude pela plataforma e pelas baías); aporte de sedimento dos rios.
- Classificação pela física: delta (de onda, maré ou rio) vs estuário; praia, restinga, laguna, barreira; falésia; fiorde e ria; planície de maré, marisma, mangue (águas quentes e abrigadas); recife (água quente, rasa e limpa).
- Portos naturais (abrigo, profundidade, maré), bancos de pesca (ressurgência, plataforma, recife), salinas naturais, risco de tsunami por zona sísmica.
- Também nas costas dos mares e lagos interiores, com fetch menor.

## 11 · Solo, vegetação e biomas

- Solo pelos fatores de formação: rocha-mãe, clima, relevo, tempo, organismos; loess, aluvião, laterita, chernozem, podzol, solos vulcânicos.
- Formação vegetal por clima, solo e **regime de fogo** (savana, chaparral, pinhal); bioma pela combinação; Köppen (~30 classes) e biomas WWF (~16) como linguagem de checagem.
- **Cobertura de biomas:** o requisito "todos os biomas da Terra" é atendido pela **escolha da semente**, nunca por ajuste do modelo. Lista-alvo: 14 biomas terrestres WWF + mangue + biomas de água doce e costeiros. A rodada de sementes é na fase de tectônica, com clima aproximado (seção 21).
- **Variantes raras na Terra, bem-vindas:** deserto de neblina extenso, planalto frio úmido, floresta inundada continental, planície de maré gigante, campos geotermais, deserto polar, floresta de monção seca, savana de altitude.
- **Saídas de aptidão** (para o povoamento, fora deste plano): estação de crescimento, água disponível, fertilidade, declividade → aptidão agrícola e de pasto; madeira por tipo; pesca; argila, pedra, cal, sal.

## 12 · Mana

**Mana é campo, não estoque.** Uma propriedade do lugar, como o calor do solo ou o magnetismo: tem **intensidade** (fraca → intensa) e um **tom** entre cinco afinidades — **fogo, água, terra, vento, cura**. Não se gasta, não se acumula, não se extrai, não varia com estação, lua ou gente. Muda só com a geologia, em tempo geológico. A física não a vê: nenhum rio, serra, clima ou bioma depende dela.

| Tom | De onde a física o dá |
|---|---|
| Fogo | fluxo geotérmico, vulcanismo, rocha ígnea jovem, deserto quente |
| Água | rio grande, delta, lago, mar interior, geleira, chuva abundante |
| Terra | crosta velha, serra, escudo, carste, zonas de falha |
| Vento | cristas, planaltos, trilhas de tempestade, costas de vento, altitude |
| Cura | floresta velha, nascente limpa, alta produtividade biológica |

- **Campo contínuo**, derivado dessas fontes mais ruído da semente, no nível 2 (500 m). Em quase todo o continente é fraco a médio; é intenso em poucos lugares grandes e muitos pequenos.
- **Campo intenso afasta gente, não o contrário:** a aura fica volátil, as bestas são fortes, a flora é hostil. Lugares de campo fraco a médio são habitáveis; os intensos ficam selvagens por natureza. O povoamento não altera o campo.
- **Paisagens de campo intenso:** acento visível sobre o bioma físico, nunca bioma novo de clima. Exemplos que a física pode dar: floresta temperada bioluminescente, campo geotermal com cristais, deserto de vidro vulcânico, mangue de névoa, planalto onde o vento canta, nascente de cura com musgo perene. Onde e quantas, a semente decide.
- **Dungeons:** foco intenso subterrâneo — fenda tectônica, caverna cárstica sobre falha, mina funda. Não carrega nem descarrega; o que muda é a ecologia. Nascem da geologia; a parte humana (mina abandonada) vem no povoamento.
- **Cristais de campo:** minerais que se formam sob campo intenso; condutores e amplificadores para círculos e itens, não baterias. Neutros, sem tom.
- **Limite:** cosmético e ecológico, nunca físico. Sem anomalias que contradigam clima ou relevo.

## 13 · Vida: biogeografia, flora, fauna, bestas

- **Reinos biogeográficos** pelas barreiras (serras, mares interiores, desertos) e há quanto tempo separam, mais refúgios glaciais — endemismo sem simular evolução. Ilhas: regra de ilha (gigantismo/nanismo), empobrecimento.
- **Flora:** formações por bioma; cada espécie com **envelope ecológico** (temperatura, chuva, altitude, solo, luz, fogo, sazonalidade); o mapa decide a distribuição. **Flora de mana:** espécies cujo envelope inclui campo médio a intenso; rendem remédio, poção, tintura e veneno; algumas hostis.
- **Fauna comum:** cadeias tróficas por produtividade; herbívoros, predadores, decompositores por bioma; migrações pelo mês; fauna de água doce por bacia (isolada = endêmica); sem afinidade visível.
- **Bestas:** **espécies de verdade**, não animais mutados — linhagens com afinidade herdada (como as pessoas) que ocupam nichos onde o tom do campo as favorece: a salamandra de fogo vive no campo vulcânico porque consegue; nenhum animal comum consegue. Raras fora de campo intenso; grandes e raras (grifo, troll de pedra, verme de areia) só em campo intenso. Animais, não vilões: fome, território, reprodução. Núcleo de mana no corpo (alquimia).
- Catálogos existentes entram nesse formato; a localização de cada ficha é derivada do mapa.

## 14 · Recursos naturais e geologia econômica

Depósitos por contexto, nunca "colocados": cobre, ouro e prata em arcos e orógenos; estanho e tungstênio em granitos; ferro em escudos velhos; carvão e sal em bacias sedimentares; diamante em crátons; placer de ouro e gemas em rios que drenam serras; argila, calcário, mármore, ardósia e pedra de cantaria pela litologia; fontes termais e enxofre no vulcanismo; cristais de campo pela seção 12. Mais: madeira por bioma, pesca por costa e rio, sal de salina, turfa, âmbar em bacias florestais antigas. Saída: mapa de províncias com abundância, acessibilidade medieval (afloramento, profundidade) e mês (rios congelados, passos fechados).

## 15 · Riscos naturais

Camada única, por lugar e mês, derivada das seções 6–10: terremoto (zonas sísmicas), vulcão ativo, tsunami, cheia, seca, ciclone tropical, tempestade de inverno, granizo e tornado, avalanche, incêndio (regime de fogo), deslizamento (declividade × chuva × solo), gelo de rio e de porto. É o que faz o cotidiano medieval ter risco "do tamanho das pessoas" sem invenção.

## 16 · Escala humana (régua)

Superfície de custo: declividade (função de Tobler), vegetação, pântano, neve e gelo por mês, travessia de rio por largura e vazão, passos de montanha, campo intenso (evitado). Barco: rio por corrente (descida/subida), mar por vento e corrente, gelo de inverno, portos naturais. Resultado: tempo de viagem entre dois pontos por mês. Alimenta estradas, comércio e povoamento (fora deste plano).

## 17 · Níveis, dados e escala

| Nível | Resolução | Cobertura | Como |
|---|---|---|---|
| 1 · Globo | ~25 km | planeta inteiro | grade esférica; tectônica, clima, oceano |
| 2 · Continente | 500 m | continente de jogo + plataforma | downscaling, hidrologia, costa, solo, bioma, mana, riscos |
| 3 · Esqueleto vetorial | contínuo | continente | costa, rios, margens, cristas, escarpas, quedas, geleiras, dunas, falhas, cavernas; atributos por trecho e mês |
| 4 · Bloco fino | 16 m | sob demanda, guardado | só da semente + coordenada + esqueleto; halo de cálculo; distância assinada às feições |
| 5 · Escala real | 1 m | nunca guardado | shader no aparelho; só decora — nada de jogo depende dele |

- Coordenadas: latitude/longitude no globo; no continente, projeção de área igual com metros por bloco; pirâmide de potências de 2 e ladrilhos de 256 px.
- Formatos (int16, cm, PNG) decididos na fase do esqueleto, com regra fixa: precisão vertical ≥ 0,1 m nos níveis 4 e 5; profundidade sem saturar em lago fundo; chuva mensal sem teto de 255 mm.
- Código e dados num repositório GitHub (a máquina de cada chat começa vazia), com manifesto por fase; docs de decisão no projeto; mapas como imagens e páginas publicadas.

## 18 · Orçamento do celular

Primeira tela ≤ 3 MB; ≤ 1,5 MB por passo de zoom somando as camadas obrigatórias; ladrilho ≤ 40 KB (a verificar com o formato); ≤ 200 MB em uso; 60 fps alvo, 30 piso; nível 5 só no shader; ≤ 500 ladrilhos em cache. O teste de desempenho é no seu aparelho, por página publicada.

## 19 · Checagens de coerência (forma, não meta)

**Terrestre (antes do planeta):** erosão sobre um relevo real dá lei de Hack e densidade de drenagem reais; clima com a topografia da Terra dá o Köppen da Terra em forma; costa sobre uma costa real classifica como a real.
**Geologia:** hipsometria sem degraus; espectro sem pico de grade; serras alongadas/arqueadas; escudo velho plano; antepaís na frente de cada cordilheira; plataforma larga em margem passiva, estreita em ativa; rifte parado com piso baixo e ombros altos; determinismo entre rodadas.
**Clima:** perfil de temperatura por latitude no envelope terrestre; desertos onde a circulação põe; costa oeste subtropical seca e fria, leste quente e úmida; interior continental de grande amplitude; monção onde há contraste terra-mar; gelo marinho sazonal; ciclones só sobre mar quente.
**Água:** perfis côncavos; rios chegam ao mar ou a bacia fechada com saldo coerente; lagos glaciais ao norte, de rifte onde houve rifte; aquíferos só em rocha que os permite.
**Costa:** delta onde há sedimento e pouca maré/onda; fiorde onde houve gelo; recife só em água quente e limpa.
**Biomas:** frações de Köppen dentro de ±50 % das terrestres por classe; lista de cobertura completa na semente escolhida; nenhuma classe em lugar fisicamente impossível.
**Vida e mana:** nenhuma espécie fora do envelope; bestas só onde o tom favorece, grandes só em campo intenso; nenhuma feição física explicada por mana; campo intenso ocupa fração pequena do continente.

## 20 · O que não simulamos, e por quê

| Fora | Em vez disso |
|---|---|
| Convecção 3D do manto | placas cinemáticas com campo de forças sorteado |
| Circulação oceânica completa | oceano de placa + giros por vento |
| Evolução biológica | reinos por barreiras e refúgios + envelopes ecológicos |
| Tempo dia a dia | climatologia mensal com variabilidade estatística e riscos por frequência |
| Mana como força física ou estoque | campo derivado, só cosmético e ecológico |
| Gente, história e povoamento | plano próprio, depois do mundo físico; o povoamento lê este mundo e não o altera |

## 21 · Fases e entregas

| Fase | Constrói | Entrega |
|---|---|---|
| F0 · Premissas | este doc; repositório | doc aprovado + repo vazio |
| F1 · Astros e globo | órbita, insolação, grade esférica, calendário, lua e maré | tabelas e gráficos de insolação, dia, maré; calendário |
| F2 · Tectônica e geologia | placas, relevo, rocha, bacias, vulcões, flexura, erosão grossa; **rodada de N sementes com clima aproximado (plano B) e cobertura estimada de biomas; 2–3 finalistas** | mapas globais e do continente por finalista; relatório de checagens; escolha |
| F3 · Atmosfera | teste terrestre; plano A ou B; circulação; downscaling | mapas mensais |
| F4 · Oceano, gelo e glaciações | correntes, gelo marinho, ciclos glaciais, rebote, refúgios | mapas e animação por mês |
| F5 · Hidrologia | rios, lagos, vazão, cheia, aquíferos, permafrost, geleiras | mapas e tabela de bacias |
| F6 · Costa | classes de costa, marés, deltas, recifes, portos, pesca | mapas e amostras |
| F7 · Solo e biomas | solos, fogo, Köppen, biomas, aptidões; **semente final entre os finalistas** | mapas, lista de cobertura, semente final |
| F8 · Mana, vida e recursos | campo de mana e paisagens intensas, dungeons físicas, reinos, envelopes, bestas, flora de mana, províncias de recursos, riscos | mapas e catálogos derivados |
| F9 · Esqueleto vetorial | grafo de rios e costas, cristas, escarpas, cavernas; formatos de dados | vetor + relatório de topologia |
| F10 · Bloco fino | vale, meandro, delta, praia, escarpa, vale glacial, duna, carste a 16 m | 10 alvos a 30, 10 e 3 m/px |
| F11 · Escala real | shader de chão, árvore, pedra, água, neve, por mês; acentos de campo intenso | página de teste no celular com fps |
| F12 · Atlas | motor por ladrilhos, camadas, fichas, busca, régua por mês | atlas publicado |

Ordem: F0 → F1 → F2 → F3 → F4 → F5 → F6 → F7 → F8 → F9 → F10 → F11 → F12. F8 pode andar em paralelo com F9–F11. Uma fase por chat; cada fase começa clonando o repositório, lendo este doc e o doc da fase anterior, e termina gravando o seu doc no projeto e os dados no repo com manifesto. Quem executa cada fase fica em doc de trabalho separado.

## 22 · Decisões tomadas (F0, 2026-10-28)

| # | Decisão | Valor |
|---|---|---|
| 1 | Obliquidade | 23,5° |
| 2 | Excentricidade | 0,017, periélio no inverno do norte |
| 3 | Lua e calendário | uma lua terrestre; lunação de 30 dias; 12 meses × 30 dias |
| 4 | Terra do planeta | ~20 %: continente de jogo + continente polar + 1–2 continentes invisíveis + ilhas |
| 5 | Área do continente | ~25 M km² |
| 6 | Latitudes | ~78° N a ~15° S |
| 7 | Atmosfera | plano A com teste de 1 h; plano B de reserva |
| 8 | Biomas-alvo | 14 WWF + mangue + água doce e costeiros; cobertura por escolha de semente |
| 9 | Mana | campo com intensidade e tom; cosmético e ecológico, nunca físico |
| 10 | Quinta afinidade | vento |
| 11 | Veias de mana | descartadas; substituídas pelo mapa de intensidade |
| 12 | Mana e gente | campo intenso afasta gente; gente não altera o campo; sem acúmulo nem dispersão |
| 13 | Dungeons | foco intenso subterrâneo de origem geológica; sem carga/descarga |
| 14 | Bestas | espécies com afinidade herdada, por nicho e tom do campo |
| 15 | Anomalias físicas | nenhuma |
| 16 | Repositório | GitHub, criado pelo autor |

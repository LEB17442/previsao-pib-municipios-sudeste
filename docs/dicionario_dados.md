# Dicionário da base inicial

Uma linha por município e ano. A chave é composta por `codigo_municipio` e `ano`.

| Campo | Definição |
| --- | --- |
| codigo_municipio | Código IBGE de sete dígitos |
| ano | Ano de referência, de 2010 a 2023 |
| municipio | Nome na publicação do IBGE |
| uf | Sigla do estado, ES, MG, RJ ou SP |
| pib_mil_reais | PIB nominal em milhares de reais |
| vab_agro_mil_reais | Valor adicionado bruto da agropecuária em milhares de reais correntes |
| vab_industria_mil_reais | Valor adicionado bruto da indústria em milhares de reais correntes |
| vab_servicos_mil_reais | Valor adicionado bruto dos serviços, excluída a administração pública, em milhares de reais correntes |

A [pesquisa PIB dos Municípios no SIDRA](https://sidra.ibge.gov.br/pesquisa/pib-munic/tabelas) está indicada no enunciado. O notebook usa a [base consolidada do IBGE de 2010 a 2023](https://ftp.ibge.gov.br/Pib_Municipios/2022_2023/base/). A abertura setorial de 2022 e 2023 está indisponível na edição e os campos vazios representam ausência de dado.

## Indicadores adicionais

O script `integrar_sidra.py` acrescenta os seguintes campos a `base_integrada_sidra.csv` por código do município e ano:

| Campo | Origem | Unidade |
| --- | --- | --- |
| producao_agricola_mil_reais | [PAM 5457](https://sidra.ibge.gov.br/tabela/5457), variável 215, total das lavouras | Mil reais correntes |
| rebanho_bovino_cabecas | [PPM 3939](https://sidra.ibge.gov.br/tabela/3939), variável 105, bovinos | Cabeças |
| populacao_estimada | [Estimativas 6579](https://sidra.ibge.gov.br/tabela/6579), variável 9324 | Pessoas |

A série de estimativas retornou cobertura municipal completa entre 2011 e 2021 e campos vazios em 2010, 2022 e 2023. A tabela integrada registra o ano de referência. A PIA-Empresa e a PAS divulgam resultados até o nível de unidade da Federação e foram excluídas da integração municipal.

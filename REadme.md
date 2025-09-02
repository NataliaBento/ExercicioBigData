# ETL Hipolabs Universities

Este projeto implementa um **processo de ETL simples** para consumir a [API Hipolabs Universities](http://universities.hipolabs.com/), tratar os dados e salvar em um banco **SQLite**.  
Além disso, inclui exemplos de **consultas SQL** para explorar os dados carregados.

---

## Estrutura

- `etl_consultas_universidades.py` → Script Python que executa o ETL.  
- `consultas.txt` → Consultas SQL prontas para validar o banco.  
- `universities.sqlite` → Banco de dados gerado após a carga.  

---

## Como rodar o ETL

1. Clone este repositório:
   ```bash
   git clone https://github.com/NataliaBento/ExercicioBigData.git
   cd BigData

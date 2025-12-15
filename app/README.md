## To run:
```
docker compose up -d 
python ingest_data.py 
conda activate dbt_env 
cd dbt_healthcare 
dbt run
cd ..
cd app
streamlit run app.py
```
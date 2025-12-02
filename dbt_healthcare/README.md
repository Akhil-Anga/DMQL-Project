# dbt Healthcare Project

## To activate:
```
conda activate dbt_env
```

## To run:
```
docker compose up -d 
python ingest_data.py 
conda activate dbt_env 
cd dbt_healthcare 
dbt run
```
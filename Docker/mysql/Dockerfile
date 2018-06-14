FROM mysql:8

COPY data_sources/mysql/01-heartbit.sql /docker-entrypoint-initdb.d/01-heartbit.sql
COPY data_sources/mysql/02-binaryblobapp.sql /docker-entrypoint-initdb.d/02-binaryblobapp.sql
COPY data_sources/mysql/03-imagestorage.sql /docker-entrypoint-initdb.d/03-imagestorage.sql

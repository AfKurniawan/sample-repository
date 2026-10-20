# Looks Sample Vulnerable Service

Repository sample lokal untuk menguji alur repository-to-deployment dan AI analysis Looks.

Service ini sengaja memiliki beberapa issue yang aman untuk dideteksi di lingkungan lokal:

- debug mode aktif dan secret dummy hardcoded;
- SQL query dibangun dengan string interpolation;
- path file berasal langsung dari input request;
- command shell menerima input request;
- CORS terlalu permisif dan endpoint admin tanpa autentikasi;
- upload tidak membatasi ukuran atau tipe file;
- mode error dapat membuat health check dan runtime endpoint gagal.

Issue di sini hanya untuk fixture/security training. Jangan deploy ke internet atau gunakan secret di dalamnya untuk sistem nyata.

## Run normal

```bash
cd Looks/sample-repository
docker compose up --build
```

Service tersedia di `http://127.0.0.1:8091`.

## Run failure mode

Mode ini sengaja membuat `/healthz` mengembalikan HTTP 503 dan `/unstable` mengembalikan HTTP 500:

```bash
cd Looks/sample-repository
docker compose -f docker-compose.yml -f docker-compose.error.yml up --build
```

Hentikan dengan:

```bash
docker compose -f Looks/sample-repository/docker-compose.yml -f Looks/sample-repository/docker-compose.error.yml down
```

## Useful checks

```bash
curl -i http://127.0.0.1:8091/healthz
curl -i 'http://127.0.0.1:8091/api/items?query=sample'
curl -i http://127.0.0.1:8091/admin/config
curl -i http://127.0.0.1:8091/unstable
```

The sample is intentionally local-only and is not connected to the Looks API automatically yet.

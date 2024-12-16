# Movie Recommender System
Sistem rekomendasi film/TV show serupa dari yang dicari oleh user

### Anggota
| Nama                            | NRP          |
| ------------------------------- | ------------ |
| M Arkananta Radithya            | `5027221003` |
| Asadel Naufal Leo               | `5027221009` |
| Marcelinus Alvinanda C.         | `5027221012` |
| Gabriella Erlinda Wijaya        | `5027221018` |
| Nicholas Marco Weinandra        | `5027221042` |

## Workflow
![image](https://github.com/user-attachments/assets/5fd14930-336b-474e-8698-10b0d4b4956b)

## Menjalankan Program
### Docker
```
docker compose up -d
```
Program akan mulai _pulling_ image docker yang dibutuhkan

### Kafka
Untuk melakukan streaming data dari producer, lakukan command:
```
python producer.py
```
![kafka](https://github.com/user-attachments/assets/84a2893e-6289-4af0-9d58-4b16b4e54b91)

### Streamlit
Data yang telah distreaming oleh producer akan di streaming yang prosesnya bisa kita lihat visualisasinya dengan:
```
streamlit run app.py
```
![streamlit](https://github.com/user-attachments/assets/922bcd47-1b7a-47a8-a387-e73d513a0010)

### Minio
Data yang telah distreaming akan disimpan kedalam bentuk batch yang disimpan dalam minio
![minio](https://github.com/user-attachments/assets/42cfb89c-e60f-4597-8181-1c2483ebcfde)

### Spark
Batch data yang telah disimpan dalam minio tadi akan diolah menggunakan spark untuk menghasilkan model ml
![spark](https://github.com/user-attachments/assets/a4948817-d3c3-4094-be46-2fc07c4f8ecf)

### Trino dan Dbeaver
User dapat melakukan query untuk melihat data yang diinginkan menggunakan dbeaver, proses query user dapat dilihat pada trino
![trino](https://github.com/user-attachments/assets/7b4e9a36-648c-4693-a170-680d1a38be09)
![dbeaverquery](https://github.com/user-attachments/assets/78bb40db-b558-400c-8934-2e1173c67376)

### Automation Script
Ketika file `automation.py` dijalankan, maka program akan otomatis menjalankan mulai dari producer kafka, dashboard streamlit, proses spark, dan streamlit
```
    producer_thread = threading.Thread(target=run_producer)
    streamlit_thread = threading.Thread(target=run_streamlit)
    spark_thread = threading.Thread(target=schedule_spark)
    pkl_monitor_thread = threading.Thread(target=monitor_pkl_files)
```

## UI Client
- Client dapat mencari film yang diinginkan, lalu klik Show Recommendations.
- Program akan menampilkan film yang dicari, beserta film-film lain yang direkomendasikan karena serupa dengan film yang dicari
![WhatsApp Image 2024-12-16 at 15 17 01_d0db5dd3](https://github.com/user-attachments/assets/ea5edd77-7ae0-4e25-a3a8-609a7587d366)
![WhatsApp Image 2024-12-16 at 15 17 13_ad3660c0](https://github.com/user-attachments/assets/8eaa61c9-6ee0-42be-885c-d44ade7d0542)
- Ketika user klik "View movie details", user akan diarahkan ke website IMDB untuk detail film yang dicari
![WhatsApp Image 2024-12-16 at 15 18 55_8807f132](https://github.com/user-attachments/assets/fc1b2236-2a59-4019-a0a9-e8a68ec8d544)

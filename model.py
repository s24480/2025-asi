import os
import zipfile
from azure.storage.blob import BlobServiceClient
from autogluon.tabular import TabularPredictor
import shutil


def download_and_load_autogluon_model(
        connection_string: str,
        container_name: str,
        blob_name: str,
        local_model_path: str = "taxi_fare_predictor"
) -> TabularPredictor | None:
    print(f"\n--- Próba załadowania modelu '{blob_name}' ---")

    if os.path.exists(local_model_path) and os.path.isdir(local_model_path):
        print(f"Lokalny katalog modelu '{local_model_path}' już istnieje.")

        try:
            print(f"Ładowanie modelu AutoGluon z istniejącej ścieżki: '{local_model_path}'...")
            predictor = TabularPredictor.load(local_model_path)
            print("Model AutoGluon załadowany pomyślnie z lokalnej ścieżki.")
            return predictor
        except Exception as e:
            print(f"Błąd ładowania modelu z lokalnej ścieżki '{local_model_path}': {e}")
            print("Kontynuuję próbę pobrania i rozpakowania modelu.")
            try:
                if os.path.exists(local_model_path):
                    shutil.rmtree(local_model_path)
                    print(f"Usunięto uszkodzony lokalny katalog modelu: '{local_model_path}'.")
            except Exception as clean_e:
                print(f"Błąd podczas czyszczenia uszkodzonego katalogu: {clean_e}")
    else:
        print(f"Lokalny katalog modelu '{local_model_path}' nie istnieje. Będę pobierać model.")

    try:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    except Exception as e:
        print(f"Błąd inicjalizacji klienta Azure Blob Storage: {e}")
        return None

    local_zip_path = os.path.join(os.getcwd(), blob_name.split('/')[-1])
    try:
        print(f"Pobieranie bloba '{blob_name}' do '{local_zip_path}'...")
        with open(local_zip_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
        print(f"Blob '{blob_name}' pobrany pomyślnie.")
    except Exception as e:
        print(f"Błąd pobierania bloba '{blob_name}': {e}")
        if os.path.exists(local_zip_path):
            os.remove(local_zip_path)
        return None

    try:
        print(f"Rozpakowywanie '{local_zip_path}' do '{local_model_path}'...")
        os.makedirs(local_model_path, exist_ok=True)
        with zipfile.ZipFile(local_zip_path, 'r') as zip_ref:
            zip_ref.extractall(local_model_path)
        print("Model rozpakowany pomyślnie.")
    except zipfile.BadZipFile:
        print(f"Błąd: Plik '{local_zip_path}' nie jest prawidłowym plikiem ZIP.")
        return None
    except Exception as e:
        print(f"Błąd rozpakowywania pliku '{local_zip_path}': {e}")
        return None
    finally:
        if os.path.exists(local_zip_path):
            os.remove(local_zip_path)
            print(f"Usunięto tymczasowy plik zip: '{local_zip_path}'.")

    try:
        print(f"Ładowanie modelu AutoGluon z '{local_model_path}'...")
        predictor = TabularPredictor.load(local_model_path)
        print("Model AutoGluon załadowany pomyślnie.")
        return predictor
    except Exception as e:
        print(f"Błąd ładowania modelu AutoGluon z '{local_model_path}': {e}")
        return None

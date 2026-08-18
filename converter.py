import os
import glob
import pandas as pd

arquivos = glob.glob("*.xlsx") + glob.glob("*.csv")

for arquivo in arquivos:
    if arquivo.startswith("~$") or arquivo.endswith(".json") or arquivo == "converter.py":
        continue

    nome_sem_extensao, _ = os.path.splitext(arquivo)
    json_saida = f"{nome_sem_extensao}.json"

    try:
        if arquivo.endswith(".xlsx"):
            df = pd.read_excel(arquivo)
        else:
            try:
                df = pd.read_csv(arquivo, sep=None, engine='python', encoding='utf-8')
            except (UnicodeDecodeError, pd.errors.EmptyDataError):
                df = pd.read_csv(arquivo, sep=None, engine='python', encoding='latin1')

        df.to_json(json_saida, orient='records', indent=4, force_ascii=False)
        print(f"✅ Convertido: {arquivo}  ➡️  {json_saida}")

    except Exception as e:
        print(f"❌ Erro ao converter {arquivo}: {e}")

print("\n🎉 Conversão concluída!")
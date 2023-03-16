import os
from pymongo import MongoClient
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
MONGO_ADDR = os.environ["MONGO_ADDRESS"]
MONGO_PORT = os.environ["MONGO_PORT"]
DB_NAME = os.environ["MONGO_NOLAN_DB"]

if __name__ == "__main__":
    client = MongoClient(
        f"mongodb://{MONGO_ADDR}:{MONGO_PORT}/{DB_NAME}"
    )
    db = client[DB_NAME]
    while True:
        print("\nRunning data store program...")
        datapath = input("Enter the csv location (q to quit): ")

        if datapath == "q":
            break

        if not os.path.exists(datapath):
            print("Path doesn't exists!")
            continue

        try:
            df = pd.read_csv(datapath)
        except:
            print("Error in reading csv file, please enter appropriate csv file location!")
            continue

        collection_name = input("Please enter the destination collection name (q to quit): ")

        if collection_name in db.list_collection_names():
            force = input("Collection name already exists! Force overwrite (Y/n) (q to quit)? ")
            if force == "q":
                break
            if force != "Y":
                continue

        db[collection_name].insert_many(df.to_dict(orient="records"))
        print(f"Successfully store data {datapath} to {collection_name}")

    client.close()

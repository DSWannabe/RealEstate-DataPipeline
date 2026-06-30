import json

with open("Guland_Details.jsonl") as file:
    with open("gula_info.csv", "w") as csv_file:
        csv_file.write(
            "id,size,price,address,bedroom,bathroom,"
            "floorth,facing_direction,legality\n"
        )
        for line in file.read().splitlines():
            post = json.loads(line)
            id: str = post['id']
            size: str = post['size']
            price: str = post['price']
            address: str = post['address']
            bedroom: str = post['bedroom']
            bathroom: str = post['bathroom']
            floorth: str = post['floorth']
            facing_direction: str = post['facing_direction']
            legality: str = post['legality']
            csv_file.write(
                f'{id},{size},{price},{address},{bedroom},{bathroom},{floorth},{facing_direction},{legality}'
            )

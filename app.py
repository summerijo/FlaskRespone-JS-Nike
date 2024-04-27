from flask import Flask, jsonify
import json

app = Flask(__name__)

def search_key(data, key):
    if isinstance(data, dict):
        if key in data:
            return data[key]
        for value in data.values():
            result = search_key(value, key)
            if result is not None:
                return result
    elif isinstance(data, list):
        for item in data:
            result = search_key(item, key)
            if result is not None:
                return result
            

def search_key_in_file(data, key):
        result = search_key(data, key)
        if result is not None:
            return result
        else:
            return f"Key '{key}' not found in the file."


# Gets the value of the key specified
def search_all_keys_in_file(dictionary, key):

    result = []

    def search_in_dict(d, k):
        for key, value in d.items():
            if key == k:
                result.append(value)
            elif isinstance(value, dict):
                search_in_dict(value, k)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        search_in_dict(item, k)

    if isinstance(dictionary, dict):
        search_in_dict(dictionary, key)
    elif isinstance(dictionary, list):
        for item in dictionary:
            if isinstance(item, dict):
                search_in_dict(item, key)

    return result


# Gets the variants of the product
def get_var_keys(data):

    # The "Threads" key contains the products
    threads = search_key_in_file(data, "Threads")

    # Check if "products" key exists under "Threads"
    if "products" in threads:
        products_data = threads["products"]

        result = [] # Stores the variants of the product

        for var_id, product_dict in products_data.items():

            # The "skus" contains the attributes of a variant
            if "skus" in product_dict:
                sizes = [sku["nikeSize"] for sku in product_dict["skus"]]

            # Check if the variant is available
            if product_dict["status"].upper() == "ACTIVE":
                is_available = True
            else:
                is_available = False


            # Gets the color of the variant
            color_description = product_dict["colorDescription"]
            if "/" in color_description:
                color_description = color_description.split('/')
            else:
                color_description = [color_description]


            # Gets the url of the images of the variant
            url_values = search_all_keys_in_file(product_dict["nodes"], "portraitURL")
           

            result.append({
                "name": f"{product_dict['brand']} {product_dict['fullTitle']}",
                "price": product_dict["currentPrice"],
                "sku_id": product_dict["id"],
                "attributes": [
                    {
                        "color" : color_description,
                        "size": sizes
                    }
                ],
                "url": f"{search_key_in_file(data, "withoutStyleColor")}/{product_dict["styleColor"]}",
                "images":  url_values,
                "is_available": is_available,
            })

        return result
        
    return None


def load_data(file_name):
     with open(file_name, 'r', encoding='utf-8') as file:
        data = json.load(file)

        return data


@app.route('/get_product', methods=['GET'])
def get_data():
    # Load data
    file_name = 'nike_dunk_kids.json'
    data = load_data(file_name)

    # Extract required information
    brand = search_key_in_file(data, "brand")
    product_name = search_key_in_file(data, "fullTitle")
    product_id = search_key_in_file(data, "productId")
    var_keys = get_var_keys(data)


    response_data = {
        "title": f"{brand} {product_name}",
        "product_id": product_id,
        "variants": var_keys
    }

    # Save JSON to file in project directory
    with open("flask_response.json", 'w') as json_file:
        json.dump(response_data, json_file, indent=4)

    # Return JSON response
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)
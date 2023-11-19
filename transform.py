import os
import json
from collections import Counter
import re


# Specify the directory and the element you want to search for
directory_path = 'results_mlb'



dict_subcategory={'Jerseys':'Clothes',
      'Hoodies & Sweatshirts':'Clothes',
      'T-Shirts':'Clothes',
      'T-shirts':'Clothes',
      'Sweatshirts':'Clothes',
      'Vest':'Clothes',
      'Suites':'Clothes',
      'Trousers':'Clothes',
      'Pants':'Clothes',
      'Polos':'Clothes',
      'Shirts':'Clothes',
      'Sweaters':'Clothes',
      'Shorts':'Clothes',
      'Shirts & Sweaters':'Clothes',
      'Sleepwear & Underwear':'Colthes',
      'Swim Collection':'Clothes',
      'Bags':'Bags',
      'Footwear':'Shoes',
       'Hats':'Clothes',
        'Jackets':'Clothes' }

dict_productTypeId=[
'Backpacks',
'Duffels',
'Handbags',
'Luggage',
'Adjustable',
'Bucket',
'Fitted',
'Flex',
'Headbands',
'Knit',
'Snapbacks',
'Visors',
'Boots',
'Sandals',
'Slippers',
'Shoes',
'Socks',
'Sock Set',
'Full-Zip Hoodie',
'Half-Zip Hoodie',
'Quarter-Zip Hoodie',
'Pullover Hoodie',
'Full-Zip Jacket',
'Half-Zip Jacket',
'Quarter-Zip Jacket',
'Pullover Jacket',
'Pullover Sweatshirt',
'Quarter-Zip Top',
'Half-Zip Top',
'Full-Zip Top',
'Full-Snap Jacket',
'Full-Button Jacket',
'Pullover Top',
'Full-Zip Vest',
'Jersey',
'Throwback',
'pants',
'Pants',
'Leggings',
'Long Sleeve Polo'
'Polo',
'Sleeveless Polo',
'Button-Up Shirt',
'Cardigan',
'Full-Snap Shirt',
'Button-Down Shirt',
'V-Neck Pullover Sweater',
'Shirt',
'Sweater',
'Shorts',
'Long Sleeve T-Shirt',
'Long Sleeve Top',
'T-shirt',
'Tank Top',
'Sleepwear',
'Pajama',
'Boxer Briefs',
'Knit Thong',
'Nightdress']



product_types_ids=sorted(list(set(dict_productTypeId)))



def convert_json(original_json):
    full_list = []
    tails=[]

    for product in original_json:
        product_name = product.get("name", "")
        description = product.get("description", "")
        price = product.get("price", "")
        category = product.get("category", [])
        topcategory=dict_subcategory.get(product.get("filter", []), None)

        material_value = next(
            (value.split(":")[1].strip() for key, value in product.get('characteristics').items() if "Material:" in value), None)

        composition = material_value
        brand_value = next((value.split(': ', 1)[1] for value in product.get('characteristics').values() if 'Brand:' in value),
                           None)

        productTypeID=next((substring for substring in product_types_ids  if substring in product_name), None)

        brand = brand_value
        tail = product.get('name')[product.get('name').index(brand_value)+len(brand_value):len(product.get('name'))] if (brand_value is not None) and (brand_value in product.get('name')) else ''

        filtered_characteristics = {key: value for key, value in product.get('characteristics').items() if
                                    "Brand:" not in value and "Material:" not in value}

        filtered_text = '\n'.join(
            f"{key}: {value}" for key, value in filtered_characteristics.items() )




        washing_instruction = next((value for value in product.get('characteristics').values() if any(keyword in value for keyword in ['Machine wash', 'Wipe clean', 'Dry clean', 'Surface washable','Hand wash', 'Spot clean'])), None)



        # Extracting values from characteristics for creating a product for each variant
        for variant in product.get("variants", []):
            output_list=[]
            size_id = variant
            on_size_price = price
            quantity = "30"

            # Forming new keys and values for each variant
            output_list.append({"key": "productName", "value": product_name, "type": "text"})
            output_list.append({"key": "description", "value": description, "type": "text"})
            output_list.append({"key": "price", "value": price, "type": "text"})
            output_list.append({"key": "brandId", "value": brand, "type": "text"})
            output_list.append({"key": "categoryId", "value": topcategory if topcategory else "", "type": "text"})
            output_list.append(
                {"key": "subCategoryId", "value": product.get("filter", None) , "type": "text"})
            output_list.append(
                {"key": "innerCategoryId", "value": category[2] if len(category) > 2 else product.get('filter'), "type": "text"})
            output_list.append({"key": "productTypeId", "value": productTypeID, "type": "text"})
            output_list.append({"key": "composition", "value": composition, "type": "text"})
            output_list.append({"key": "product_ID", "value": product.get("slug", "").replace('Product ID:',''), "type": "text"})
            output_list.append(
                {"key": "highlights", "value": filtered_text, "type": "text"})  # Highlights not provided in the original JSON
            output_list.append(
                {"key": "wearing", "value": "", "type": "text"})
            output_list.append({"key": "washingInstruction", "value": washing_instruction, "type": "text"})
            output_list.append({"key": "isSizeAvailable", "value": "1", "type": "text"})
            output_list.append({"key": "quantity", "value": quantity, "type": "text"})
            output_list.append({"key": "sizeId", "value": size_id, "type": "text", "disabled": True})
            output_list.append({"key": "onSizePrice", "value": on_size_price, "type": "text", "disabled": True})

            full_list.append(output_list)

    return full_list


# Example usage with the provided JSONs

def process_directory(directory_path):
    converted_data = []
    list_tails=[]

    # Loop through each file in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            file_path = os.path.join(directory_path, filename)

            # Read the JSON file
            with open(file_path, 'r') as file:
                json_data = json.load(file)

            # Convert the JSON and append to the result
            converted_data.extend(convert_json(json_data))

    return converted_data


data=process_directory(directory_path)


file_output_path = "mlb_transformed_2.json"

with open(file_output_path, 'w') as json_file:
    json.dump(data, json_file, indent=2)


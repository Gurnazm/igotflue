import re
import cloudscraper
from bs4 import BeautifulSoup
import json

def artist_info():
    artist = input("Enter the artist name: ")
    artist2 = artist.replace(" ", "+").lower()
    return artist2

def get_product_list(artist_name):
    item_list = []
    add_url = f"https://www.juno.co.uk/search/?q%5Ball%5D%5B%5D={artist_name}&hide_forthcoming=1&facet[mirror_artist_facetm][0]={artist_name}"
    r = cloudscraper.create_scraper()
    html =r.get(add_url).text
    soup = BeautifulSoup(html, 'html.parser')
    product_list_div = soup.find('div', class_= "product-list")
    try:
        dv_items = product_list_div.find_all('div', class_="dv-item")
    except:
        print("artist name not found. please check the spelling and try again.")
        return
    for item in dv_items:
        item_id = item['id'].replace('item-', '')
        pl_info = item.find('div', class_="pl-info")
        info_fields = pl_info.find_all('div')
        artist_name_field = info_fields[1]
        album_name_field = info_fields[3]
        artist_names = artist_name_field.find_all('a')
        artist_name = [a.text for a in artist_names]
        artist_name = ' , '.join(artist_name)
        album_name = album_name_field.find('a').text
        text_primary = item.find('span', class_="text-primary")
        add_info = text_primary.text
        final_info = {"item_id": item_id, "artist_name": artist_name, "album_name": album_name, "add_info": add_info}
        item_list.append(final_info)
    return item_list


def add_to_cart(item_list):
    for item in item_list:
        item_id = item['item_id'][:-2]
        add_cart_url = f"https://www.juno.co.uk/cart/add/{item_id}/1/?from=artist%2Frelease&json=1"
        r = cloudscraper.create_scraper()
        sent = r.get(add_cart_url).headers['Set-Cookie']
        match = re.search(r"PHPSESSID=[^;]*", sent)
        phpsessid = match.group().split('=')[1]
        cookies = {'PHPSESSID': phpsessid}
        item['cookies'] = cookies
    return item_list

def get_cart_details(item_list):
    cart_url = "https://www.juno.co.uk/cart/"
    r = cloudscraper.create_scraper()
    for item in item_list:
        shipment_method = r.post("https://www.juno.co.uk/api/1.2/?method=user.setdeliveryservice&output_type=json&output_type=json",data="delivery_service=38",headers={'Content-Type': 'application/x-www-form-urlencoded'},cookies= item['cookies']).status_code
        response = r.get(cart_url, cookies=item['cookies']).text
        soup = BeautifulSoup(response, 'html.parser')
        try:
            cart_subtotal = soup.find('div', class_="cart-subtotal")
            subtotal_value = cart_subtotal.find('strong', id="subtotal_val").text.strip()
            cart_shipping = soup.find('div', class_="cart-table-shipping shipping")
            shipping_value = cart_shipping.find('strong', id="shipping_val").text.strip()
            grand_total = soup.find('div', class_="cart-grand-total")
            grand_total_value = grand_total.find('strong', id="grand_total_val").text.strip()
            item['cart_subtotal'] = subtotal_value
            item['cart_shipping'] = shipping_value
            item['grand_total'] = grand_total_value

            print(f"""
            --------------------ALBUM INFO--------------------
            Item ID: {item['item_id'][:-2]}
            Artist Name: {item['artist_name']}
            Album Name: {item['album_name']}
            Additional Info: {item['add_info']}
            --------------------CART INFO---------------------
            Cart Subtotal: {item['cart_subtotal']}
            Cart Shipping: {item['cart_shipping']}
            Grand Total: {item['grand_total']}
            --------------------------------------------------
            """)
        except:
            print("Error retrieving cart details.")
            continue
artist_name = artist_info()
product_list = get_product_list(artist_name)
item_list = add_to_cart(product_list)
get_cart_details(item_list)


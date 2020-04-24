import mws, os
import pickle # for testing to store results of API calls
from datetime import datetime
from setAwsSecrets import init
import mwsDecodeLabel 

# global data
test_data = {"dataset":"test"}
api_failed = False

def get_timestamp():
    return datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))

def status():
    init()
    access_key = os.getenv('mws_access_key')
    secret_key = os.getenv('mws_secret_key')
    SellerId = os.getenv('mws_account_id')
    orders_api = mws.Orders(access_key=access_key,secret_key=secret_key,account_id=SellerId,region='DE')
    try:
        ss = orders_api.get_service_status()
        mws_status = ss.parsed.Status
    except:
        mws_status = 'RED'
    MWS = {
        "Orders": {
            "status": mws_status,
            "text": "MWS API Call",
            "timestamp": get_timestamp()
        }
    }
    return [MWS[key] for key in sorted(MWS.keys())]

def order_get(OrderId, MwsKey):
    init(key=MwsKey.encode())
    access_key = os.getenv('mws_access_key')
    secret_key = os.getenv('mws_secret_key')
    SellerId = os.getenv('mws_account_id')
    orders_api = mws.Orders(access_key=access_key,secret_key=secret_key,account_id=SellerId,region='DE')
    api_failed = False
    amazon_order_ids = OrderId
    try:
        oh = orders_api.get_order(amazon_order_ids=amazon_order_ids)
        header=oh.parsed.Orders.Order
    except:
        api_failed = True
    try:
        oi = orders_api.list_order_items(amazon_order_id=amazon_order_ids)
        items = oi.parsed.OrderItems.OrderItem
    except:
        api_failed = True
    if api_failed == False:
        try: # n items
            for item in items:
#              print(item.ASIN, item.SellerSKU, item.OrderItemId)
# TEST: This will not include all items in shipment #
                MWS = {
                "Orders": {
                    "LatestShipDate": header.LatestShipDate,
                    "ASIN": item.ASIN,
                    "SellerSKU": item.SellerSKU,
                    "OrderItemId": item.OrderItemId,
                    "QuantityShipped": item.QuantityOrdered,
                    }
                }
        except: # 1 item
 #           print(items.ASIN, items.SellerSKU, items.OrderItemId)
            MWS = {
            "Orders": {
                "LatestShipDate": header.LatestShipDate,
                "ASIN": items.ASIN,
                "SellerSKU": items.SellerSKU,
                "OrderItemId": items.OrderItemId,
                "QuantityShipped": items.QuantityOrdered,
                }
            }
        return [MWS[key] for key in sorted(MWS.keys())]
    else:
        return 'API Call to MWS failed'

def get_shipping_service(amazon_order_id, amazon_pack_length, amazon_pack_width, amazon_pack_height, amazon_pack_dim_unit,
    amazon_pack_weight, amazon_pack_weight_unit, amazon_from_name, amazon_from_street, amazon_from_city,
    amazon_from_pcode, amazon_from_ccode, amazon_from_email, amazon_from_phone, amazon_delivery_exp,
    amazon_pickup, amazon_pack_value_curr, amazon_pack_value, first_order_item_id, first_item_quantity
    ):
    # init()
    access_key = os.getenv('mws_access_key')
    secret_key = os.getenv('mws_secret_key')
    SellerId = os.getenv('mws_account_id')

    shipping_api = mws.MerchantFulfillment(access_key=access_key,secret_key=secret_key,account_id=SellerId,region='DE')
    api_failed = False

    ss = shipping_api.get_shipping_service(amazon_order_id, amazon_pack_length, amazon_pack_width, amazon_pack_height, amazon_pack_dim_unit,
    amazon_pack_weight, amazon_pack_weight_unit, amazon_from_name, amazon_from_street, amazon_from_city,
    amazon_from_pcode, amazon_from_ccode, amazon_from_email, amazon_from_phone, amazon_delivery_exp,
    amazon_pickup, amazon_pack_value_curr, amazon_pack_value, first_order_item_id, first_item_quantity)
    try:
        shipping_service_id = ss.parsed.ShippingServiceList.ShippingService.ShippingServiceId
        shipping_service_offer_id = ss.parsed.ShippingServiceList.ShippingService.ShippingServiceOfferId
        mws_response = ss.original
        api_failed = False
        print('[INFO]: Unique shipping service {} found'.format(shipping_service_id))
    except:
        # more than one shipping service available
        try:
        #   shipping_service_id = ss.parsed.ShippingServiceList.ShippingService[0].ShippingServiceId
            shipping_services = ss.parsed.ShippingServiceList.ShippingService
            for shipping_service in shipping_services:
                shipping_service_id = shipping_service.ShippingServiceId
                shipping_service_offer_id = shipping_service.ShippingServiceOfferId
            mws_response = ss.original
            api_failed = False
            print('[ERROR]: Multiple Services - selecting the first {}'.format(shipping_service_id))
        except:
            print('[ERROR]: No Shipping Service Found at all')  
            shipping_service_id = 'NONE'
            shipping_service_offer_id = 'NONE'
            api_failed = True       
    MWS = {
        "ShippingService": {
            "ShippingServiceId": shipping_service_id,
            "ShippingServiceOfferId": shipping_service_offer_id,
            "text": "MWS API Call",
            "timestamp": get_timestamp()
        }
    }

    return [MWS[key] for key in sorted(MWS.keys())]

def create_shipment(amazon_order_id, amazon_pack_length, amazon_pack_width, amazon_pack_height, amazon_pack_dim_unit,
    amazon_pack_weight, amazon_pack_weight_unit, amazon_from_name, amazon_from_street, amazon_from_city,
    amazon_from_pcode, amazon_from_ccode, amazon_from_email, amazon_from_phone, amazon_delivery_exp,
    amazon_pickup, amazon_pack_value_curr, amazon_pack_value, first_order_item_id, first_item_quantity,
    amazon_ship_service_id, amazon_ship_service_offer_id, amazon_label_format
    ):
    # init()
    access_key = os.getenv('mws_access_key')
    secret_key = os.getenv('mws_secret_key')
    SellerId = os.getenv('mws_account_id')

    shipping_api = mws.MerchantFulfillment(access_key=access_key,secret_key=secret_key,account_id=SellerId,region='DE')
    api_failed = False
    try:
        ss = shipping_api.create_shipment(amazon_order_id, amazon_pack_length, amazon_pack_width, amazon_pack_height, amazon_pack_dim_unit,
        amazon_pack_weight, amazon_pack_weight_unit, amazon_from_name, amazon_from_street, amazon_from_city,
        amazon_from_pcode, amazon_from_ccode, amazon_from_email, amazon_from_phone, amazon_delivery_exp,
        amazon_pickup, amazon_pack_value_curr, amazon_pack_value, first_order_item_id, first_item_quantity,  
        amazon_ship_service_id, amazon_ship_service_offer_id, amazon_label_format
        )
        mws_response = ss.original
#        print(mws_response)
#        print(ss.parsed)
        shipping_service_id = ss.parsed.Shipment.ShippingService.ShippingServiceId
        shipment_id = ss.parsed.Shipment.ShipmentId
        tracking_id = ss.parsed.Shipment.TrackingId
        label = ss.parsed.Shipment.Label.FileContents.Contents
    except:
        shipping_service_id = 'NONE'
        shipment_id = 'NOT CREATED'
        tracking_id = 'NOT CREATED'
        label = 'NOT CREATED'
        api_failed = True       
    MWS = {
        "Shipment": {
            "ShippingServiceId": shipping_service_id,
            "ShipmentId": shipment_id,
            "TrackingId": tracking_id,
            "text": "MWS API Call MerchantFulfillment create_shipment",
            "timestamp": get_timestamp(),
            "label": label
        }
    }
    if api_failed == False:
# SAVE LABEL FOR FUTURE TESTING
        try:
            f = open('~/shipping_api.pkl', 'wb')
            pickle.dump(mws_response,f)
            f.close()
            f = open('~/shipping_api_json.pkl', 'wb')
            pickle.dump(MWS,f)
            f.close()
        except:
            print('[INFO]: could not store pkl files')
# REMOVE TEST CODE IN PRODUCTION
    return [MWS[key] for key in sorted(MWS.keys())]

def print_shipping_label_for_order(OrderId, TestFlag, PrinterIp, PrinterPort, MwsKey):
    get_shipping_test_data()
    api_status=status()[0]["status"]
    if api_status == 'GREEN':
        api_failed = False
# Get order item using order id
#        print(OrderId)
#        print(test_data["amazon_order_id"])
        test_data["amazon_order_id"]=OrderId
        order_mws=order_get(OrderId=test_data["amazon_order_id"], MwsKey=MwsKey)
#        print(order_mws)
        try:
            test_data["first_order_item_id"]=order_mws[0]["OrderItemId"]
            test_data["first_item_quantity"]=order_mws[0]["QuantityShipped"] 
        except:
            print('[ERROR]: Order could not be found')
            api_failed = True
# Get available shipping service for first order item
        if api_failed == False:
            service_mws=get_shipping_service(
                amazon_order_id=test_data["amazon_order_id"],
                amazon_pack_length=test_data["amazon_pack_length"],
                amazon_pack_width=test_data["amazon_pack_width"],
                amazon_pack_height=test_data["amazon_pack_height"],
                amazon_pack_dim_unit=test_data["amazon_pack_dim_unit"],
                amazon_pack_weight=test_data["amazon_pack_weight"],
                amazon_pack_weight_unit=test_data["amazon_pack_weight_unit"],
                amazon_from_name=test_data["amazon_from_name"],
                amazon_from_street=test_data["amazon_from_street"],
                amazon_from_city=test_data["amazon_from_city"],
                amazon_from_pcode=test_data["amazon_from_pcode"],
                amazon_from_ccode=test_data["amazon_from_ccode"],
                amazon_from_email=test_data["amazon_from_email"],
                amazon_from_phone=test_data["amazon_from_phone"],
                amazon_delivery_exp=test_data["amazon_delivery_exp"],
                amazon_pickup=test_data["amazon_pickup"],
                amazon_pack_value_curr=test_data["amazon_pack_value_curr"],
                amazon_pack_value=test_data["amazon_pack_value"],
                first_order_item_id=test_data["first_order_item_id"], 
                first_item_quantity=test_data["first_item_quantity"]
            )
            if api_failed == False:
                shipping_service_id = service_mws[0]["ShippingServiceId"]
                shipping_service_offer_id = service_mws[0]["ShippingServiceOfferId"]
            # if not in test we would now create the shipment
                if TestFlag == False:
#                    shipping_service_id = 'TEST'
                    shipment_mws=create_shipment(
                        amazon_order_id=test_data["amazon_order_id"],
                        amazon_pack_length=test_data["amazon_pack_length"],
                        amazon_pack_width=test_data["amazon_pack_width"],
                        amazon_pack_height=test_data["amazon_pack_height"],
                        amazon_pack_dim_unit=test_data["amazon_pack_dim_unit"],
                        amazon_pack_weight=test_data["amazon_pack_weight"],
                        amazon_pack_weight_unit=test_data["amazon_pack_weight_unit"],
                        amazon_from_name=test_data["amazon_from_name"],
                        amazon_from_street=test_data["amazon_from_street"],
                        amazon_from_city=test_data["amazon_from_city"],
                        amazon_from_pcode=test_data["amazon_from_pcode"],
                        amazon_from_ccode=test_data["amazon_from_ccode"],
                        amazon_from_email=test_data["amazon_from_email"],
                        amazon_from_phone=test_data["amazon_from_phone"],
                        amazon_delivery_exp=test_data["amazon_delivery_exp"],
                        amazon_pickup=test_data["amazon_pickup"],
                        amazon_pack_value_curr=test_data["amazon_pack_value_curr"],
                        amazon_pack_value=test_data["amazon_pack_value"],
                        first_order_item_id=test_data["first_order_item_id"], 
                        first_item_quantity=test_data["first_item_quantity"],
                        amazon_ship_service_id=shipping_service_id,
                        amazon_ship_service_offer_id=shipping_service_offer_id,
                        amazon_label_format=test_data["amazon_label_format"] #'ZPL203'
                    )
                    json_label=shipment_mws[0]["label"]
                    shipping_service_id = shipment_mws[0]["ShippingServiceId"]
                    shipment_id = shipment_mws[0]["ShipmentId"]
                    tracking_id = shipment_mws[0]["TrackingId"]
                    mws_message = shipment_mws[0]["text"]
                    try:
                        gzip_label=mwsDecodeLabel.decode_label(json_label)
                        zpl_label=mwsDecodeLabel.ungzip_label(gzip_label)
                        label = zpl_label
                        mwsDecodeLabel.print_label(zpl_label, PrinterIp, PrinterPort)
                    except:
                        label = 'could not be created'                        
                else: # TEST
                    shipment_id = '123-234-345-567'
                    tracking_id = '123234345456'
                    #
                    try:
                        json_label=mwsDecodeLabel.get_test_label()
                        gzip_label=mwsDecodeLabel.decode_label(json_label)
                        zpl_label=mwsDecodeLabel.ungzip_label(gzip_label)
                        label = zpl_label
                        mwsDecodeLabel.print_label(zpl_label, PrinterIp, PrinterPort)
                        mws_message = "MWS API Label Printed in Test Mode"
                    except:
                        shipping_service_id = 'SERVICE-NOT-AVAILABLE'
                        shipment_id = '123-234-345-567'
                        tracking_id = '123234345456'
                        label = '^XA^FO50,50^A0N50,50^FDMWS API called in test mode - PRINTING FAILED^FS^XZ'
                        mws_message = "MWS API called in test mode - PRINTING FAILED"
            else:
                shipping_service_id = 'SERVICE-NOT-AVAILABLE'
                shipment_id = '123-234-345-567'
                tracking_id = '123234345456'
                label = '^XA^FO50,50^A0N50,50^FDNo matching MWS Shipment Service available^FS^XZ'
                mws_message = 'No matching MWS Shipment Service available'
        else:
            shipping_service_id = 'Order-NOT-AVAILABLE'
            shipment_id = '123-234-345-567'
            tracking_id = '123234345456'
            label = '^XA^FO50,50^A0N50,50^FDNo matching Order found at MWS Order Service^FS^XZ'
            mws_message = 'No matching Order found at MWS Order Service'
    else: # MWS offline
        shipping_service_id = 'MWS-NOT-AVAILABLE'
        shipment_id = '123-234-345-567'
        tracking_id = '123234345456'
        label = '^XA^FO50,50^A0N50,50^FDMWS or client are offline^FS^XZ'
        mws_message = 'MWS or client are offline'
    MWS = {
        "Shipment": {
            "ShippingServiceId": shipping_service_id,
            "ShipmentId": shipment_id,
            "TrackingId": tracking_id,
            "text": mws_message,
            "timestamp": get_timestamp(),
            "label": label
        }
    }
    return [MWS[key] for key in sorted(MWS.keys())]

def get_shipping_test_data():
    test_data["amazon_order_id"]='306-1461823-1799999'
# defaults can remain unchanged during API calls   
    test_data["amazon_pack_length"]='30'
    test_data["amazon_pack_width"]='30'
    test_data["amazon_pack_height"]='30'
    test_data["amazon_pack_dim_unit"]='centimeters'
    test_data["amazon_pack_weight"]='100'
    test_data["amazon_pack_weight_unit"]='g'
    test_data["amazon_from_name"]='ABC GmbH'
    test_data["amazon_from_street"]='Industriestr 25'
    test_data["amazon_from_city"]='Zeven'
    test_data["amazon_from_pcode"]='27404'
    test_data["amazon_from_ccode"]='DE'
    test_data["amazon_from_email"]='info@mail.com'
    test_data["amazon_from_phone"]='+494211234678'
    test_data["amazon_delivery_exp"]='DeliveryConfirmationWithoutSignature'
    test_data["amazon_pickup"]='true'
    test_data["amazon_pack_value_curr"]='EUR'
    test_data["amazon_pack_value"]='5'
    test_data["amazon_label_format"]='ZPL203'
    
# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    print_shipping_label_for_order(OrderId='306-4020692-999999', 
        TestFlag=True, PrinterIp='123.123.123.123', PrinterPort='9999'
        )

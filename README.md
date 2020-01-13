# mws_shipping_rest_api
Simple REST API to encapsulate MWS MerchantFulfillment

This piece of work tries to simplify testing the MWS MerchantFulfillment API
with the purpose to integrate label printing in a seamless flow in backend
applications. "Get a label for a given order"

It will provide a very simplistic web server to call the API with few parameters
potentially bypassing all the nice security features and avoiding ugly XML parsing.

You will need to create a local setAwsSecrets.py file to make it rung and make sure
your secrets remain secret!

Take care when using it - and be warned not use it for industrial purposes as
error handling is at the bare minimum!

There is no planning on any maintenance and improvement but you never know ...

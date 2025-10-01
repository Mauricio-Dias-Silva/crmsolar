# from mercadopago import SDK

# sdk = SDK("TEST-4431513475375313-080812-5f8288d8c117bfd8d6f2679078ce14ef-7503661")
# response = sdk.preference().create({
#     "items": [{"title": "Teste", "quantity": 1, "unit_price": 100.0}],
#     "back_urls": {"success": "https://meusite.com/success"},
#     "auto_return": "approved"
# })

# print(response)




# import mercadopago

# sdk = mercadopago.SDK("TEST-4431513475375313-080812-5f8288d8c117bfd8d6f2679078ce14ef-7503661")  # Use seu token de teste

# data = {
#     "items": [
#         {"title": "Produto Teste", "quantity": 1, "unit_price": 100.0}
#     ],
#     "back_urls": {
#         "success": "https://meusite.com/success",
#         "failure": "https://meusite.com/failure",
#         "pending": "https://meusite.com/pending"
#     },
#     "auto_return": "approved"
# }

# response = sdk.preference().create(data)

# if response["status"] == 201:
#     print("✅ Preferência criada!")
#     print("Link de pagamento:", response["response"]["init_point"])
# else:
#     print("❌ Erro:", response)
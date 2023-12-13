from cinetpay_sdk.s_d_k import Cinetpay

apikey = "125109660063bf19422dc3a1.69792967"
site_id = "617412"

client = Cinetpay(apikey,site_id)

data = { 
    'amount' : 10000,
    'currency' : "XAF",            
    'transaction_id' : "16055552254327",  
    'description' : "TRANSACTION DESCRIPTION",  
    'return_url' : "https://www.exemple.com/return",
    'notify_url' : "https://www.exemple.com/notify", 
    'customer_name' : "Ebot",                              
    'customer_surname' : "Fabien",       
}  
print(client.PaymentInitialization(data))


"""
1.post cmd  creation de un edl
2.put = un edl ajouter a cette commande,'http://195.15.218.172/rdv_app/rdv/<id>',json={edl: "1"}
where id = json of creation de edl with key = id_cmd_id

"""

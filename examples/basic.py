from tccloud import TCClient

client = TCClient()
client.configure()
# See supported compute engines
client.supported_engines
["psi4", "terachem_pbs", ...]
# Test connection to TeraChem Cloud
client.hello_world("Colton")
"Welcome to TeraChem Cloud, Colton"

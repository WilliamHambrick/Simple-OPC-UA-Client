import asyncio
from utility.load_config import load_config
from objects.OPCUAClient import *

config = load_config()

async def task(loop):
    
    time = input("How long should the program loop for event? (time is in milo-seconds)")
    
    url = config["ServerURL"]

    cnf = Config(config["Username"], config["Password"], True) # Non Admin login (access to base tags)

    temp = OPCUA_Client(url, cnf)
    
    # Research the Certificate process further, remaining issues in verification .
    #await temp.load_certificate("./ba03e086b97d309e5bc714f6dfd6e0b2290826b0.der", "./kepware_private_key.pem", "./07b6979ad104b36e058efa89662bfff103dc609c.der")

    await temp.connect()

    root = await temp.get_root()
    
    tag1 = await temp.get_tag_address("Channel1.Device1.Tag1")
        
    print(await temp.get_tag_value(tag1))
    
    tag2 = await temp.get_tag_address("Simulation Examples.Functions.User1")
        
    print(await temp.get_tag_value(tag2))
    
    print(await temp.get_namespace_array())
    
    tag3 = await temp.get_tag_address("Channel2.Device1.MyObject.MyVariable")
        
    print(await temp.get_tag_value(tag3))
    
    #for uri in await temp.get_namespace_array():
    #    print(await temp.get_namespace_index(uri))
    
    handler = temp.SubHandler()
    sub = await temp.client.create_subscription(500, handler)
    handle1 = await sub.subscribe_data_change(tag1)
    handle2 = await sub.subscribe_data_change(tag2)
    handle3 = await sub.subscribe_data_change(tag3)
    
    await asyncio.sleep(float(time))
    await temp.disconnect()

def main():
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    loop.run_until_complete(task(loop))
    loop.close()

if __name__ == "__main__":
    main()
import asyncio, os, time
from utility.load_config import load_config
from objects.OPCUAClient import *

config = load_config()

async def task(loop):
    
    times = input("How long should the program loop for event? (time is in milo-seconds)")
    
    url = config["ServerURL"]

    cnf = Config(config["Username"], config["Password"], True) # Non Admin login (access to base tags)

    kep = OPCUA_Client(url, cnf)
    
    # Research the Certificate process further, remaining issues in verification .
    #await temp.load_certificate("./ba03e086b97d309e5bc714f6dfd6e0b2290826b0.der", "./kepware_private_key.pem", "./07b6979ad104b36e058efa89662bfff103dc609c.der")

    await kep.connect()

    root = await kep.get_root()
    
    temp = await kep.get_tag_address("ns=2;i=3")
        
    print(await kep.get_tag_value(temp))

    runtime = await kep.get_tag_address("ns=2;i=2")
        
    print(await kep.get_tag_value(runtime))
    
    x = await kep.get_tag_address("ns=2;i=4")
    z = await kep.get_tag_address("ns=2;i=6")
    
    #for uri in await temp.get_namespace_array():
    #    print(await temp.get_namespace_index(uri))
    
    #handler = kep.SubHandler()
    #sub = await kep.client.create_subscription(500, handler)
    #handle1 = await sub.subscribe_data_change(temp)
    #handle2 = await sub.subscribe_data_change(runtime)
    #print(handle1)
    
    count_t = 0.0
    last_x = 0
    last_y = 0
    rows, cols = (10, 10) 
    test = [[0 for i in range(cols)] for j in range(rows)] 
    while(count_t <= float(times)):
        count_t+=0.1
        x_val = await kep.get_tag_value(x)
        z_val = await kep.get_tag_value(z)
        
        test[last_y][last_x] = 0
        test[z_val][x_val] = 'X'
        last_x = x_val
        last_y = z_val
        os.system('cls')
        for row in test:
            print(*row, sep="\t")
        print(f"x: {z_val+1}   y: {x_val+1}")
        run = await kep.get_tag_value(runtime)
        print("Server Runtime: ",run)
        temper = await kep.get_tag_value(temp)
        print("Temperature: ",temper)
        print()
        await asyncio.sleep(1)
        
    await kep.disconnect()

def main():
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    loop.run_until_complete(task(loop))
    loop.close()

if __name__ == "__main__":
    main()
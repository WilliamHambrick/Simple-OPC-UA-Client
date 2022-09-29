from http import server
from tokenize import String
import sys
from asyncua import ua, Server
from asyncua.common.methods import uamethod
from asyncua import Client, ua
from asyncua.crypto.security_policies import SecurityPolicyBasic256Sha256
sys.path.insert(0, "..")

"""
 Conifg object to hold the username, password, and other details
 required for connection to the OPC UA server.
"""
class Config:
    
    def __init__(self, username = "", password = "", using_certificate = False):
        self.Username = username
        self.Password = password
        self.Certificate = using_certificate
    
    # returns the username stored in the object
    def Get_User(self):
        return self.Username

    # returns the password stored in the object
    def Get_Password(self):
        return self.Password

"""
Object for simplifying the OPCUA client structure
"""
class OPCUA_Client:
    def __init__(self, url, config):
        self.client = Client(url)
        self._config = config
        self.client.set_user(config.Get_User())
        self.client.set_password(config.Get_Password())
        
    # loads a certificate for passing to the sever during connection
    async def load_certificate(self, client_cert = "", private_key = "", server_cert = ""):
        if(self._config.Certificate):
            await self.client.set_security(
                SecurityPolicyBasic256Sha256,
                certificate=client_cert,
                private_key=private_key,
                server_certificate=server_cert
            )
        
    # initiates connection to the OPC UA server
    async def connect(self):
        await self.client.connect()
        
    async def connect_secure_certification(self):
        await self.client.set_security_string("Basic256Sha256,SignAndEncrypt,"+self._config.Certificate)
        await self.client.connect()
        
    # disconnects the client from the OPC UA Server
    async def disconnect(self):
        await self.client.disconnect()
        
    # Retrieves the root node from the current server connection
    async def get_root(self):
        if(self.client!=None):
            return self.client.nodes.root
    
    # Retrieves targeted tag/node via the path
    async def get_tag_path(self, NodeStrn):
        if(self.client!=None):
            return self.client.get_node(NodeStrn)
            
    # Retrieves targeted tag/node by its address
    async def get_tag_address(self, NodeStrn):
        if(self.client!=None):
                # Assumes production namespace
            return self.client.get_node("ns=2;s="+NodeStrn)

    # Gets the value of the tag passed in the method. 
    async def get_tag_value(self, tag):
        if(self.client!=None):
            return await tag.read_value()
            
    # Monitor tag method WiP
    async def Monitor_Tag(self, tag):
        if(self.client!=None):
            return await tag.read_value()
            
    # Retrieves all namespaces for the connected server
    async def get_namespace_array(self):
        if(self.client!=None):
            return await self.client.get_namespace_array()
            
    # Retrieves the namepsace index for uri of namespace passed 
    async def get_namespace_index(self, uri):
        if(self.client!=None):
            return await self.client.get_namespace_index(uri)
    
    # a WiP method for tracking and indexing the nodes on a server (resource heavy may 86)
    async def browse_nodes(self, node):
        """
        Build a nested node tree dict by recursion (filtered by OPC UA objects and variables).
        """
        node_class = await node.read_node_class()
        children = []
        for child in await node.get_children():
            if await child.read_node_class() in [ua.NodeClass.Object, ua.NodeClass.Variable]:
                children.append(
                    await self.browse_nodes(child)
                )
        if node_class != ua.NodeClass.Variable:
            var_type = None
        else:
            try:
                var_type = (await node.read_data_type_as_variant_type()).value
            except ua.UaError:
                var_type = None
        return {
            'id': node.nodeid.to_string(),
            'name': (await node.read_display_name()).Text,
            'cls': node_class.value,
            'children': children,
            'type': var_type,
        }

    # Creates a tracking agent to catch data change updates on nodes
    class SubHandler(object):

        """
        Subscription Handler. To receive events from server for a subscription
        """

        def datachange_notification(self, node, val, data):
            print("Python: New data change event", node, val)

        def event_notification(self, event):
            print("Python: New event", event)
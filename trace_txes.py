from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import json
from datetime import datetime

rpc_user='quaker_quorum'
rpc_password='franklin_fought_for_continental_cash'
rpc_ip='3.134.159.30'
rpc_port='8332'

rpc_connection = AuthServiceProxy("http://%s:%s@%s:%s"%(rpc_user, rpc_password, rpc_ip, rpc_port))

###################################

class TXO:
    def __init__(self, tx_hash, n, amount, owner, time ):
        self.tx_hash = tx_hash
        self.n = n
        self.amount = amount
        self.owner = owner
        self.time = time
        self.inputs = []

    def __str__(self, level=0):
        ret = "\t"*level+repr(self.tx_hash)+"\n"
        for tx in self.inputs:
            ret += tx.__str__(level+1)
        return ret

    def to_json(self):
        fields = ['tx_hash','n','amount','owner']
        json_dict = { field: self.__dict__[field] for field in fields }
        json_dict.update( {'time': datetime.timestamp(self.time) } )
        if len(self.inputs) > 0:
            for txo in self.inputs:
                json_dict.update( {'inputs': json.loads(txo.to_json()) } )
        return json.dumps(json_dict, sort_keys=True, indent=4)

    @classmethod
    def from_tx_hash(cls,tx_hash,n=0):
        tx = rpc_connection.getrawtransaction(tx_hash, True)
        print(tx)
        vout = tx.get("vout")
        for output in vout:
            if output.get("n") == n:
                amount = int(output.get("value"))
                owner = output.get("addresses")
        time = datetime.fromtimestamp(tx.get("blocktime"))
        ret = TXO(tx_hash, n, amount, owner, time)
        return ret


    def get_inputs(self,d=1):
        if d == 0:
            return
        tx = rpc_connection.getrawtransaction(self.tx_hash, True)
        vin = tx.get("vin")
        for input in vin:
            txid = input.get("txid")
            self.inputs.append(self.from_tx_hash(txid))
        d = d - 1
        if d == 0:
            return
        for item in self.inputs:
            item.get_inputs(d)




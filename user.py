import logging
import time
from tronpy import Tron
from tronpy.keys import PrivateKey


# 模拟用户A地址（执行授权操作的用户）
USER_ADDRESS = "TTTTTTTTTT123456789"

# 模拟用户A地址私钥
USER_PRIVATE_KEY = "模拟用户地址私钥"

# 部署好的合约地址
SPENDER_CONTRACT_ADDRESS = "你的合约地址"

# 测试网 USDT - TRC20合约地址 上线时更换为主网合约地址TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t
USDT_CONTRACT_ADDRESS = "TXYZopYRdj2D9XRtbG411XZZ3kM5VkAeBf"


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)



def main():
    logger.info("开始执行 USDT 授权脚本...")
    
    try:
        # 初始化 Tron 客户端 
        logger.info("正在连接 Tron 节点...")
        # 主网mainnet
        #client = Tron(network='mainnet')
        # 测试网
        client = Tron(network='nile')
        
        # 实例化私钥对象
        priv_key = PrivateKey(bytes.fromhex(USER_PRIVATE_KEY))
        
        logger.info(f"授权用户地址 (From): {USER_ADDRESS}")
        logger.info(f"目标合约地址 (Spender): {SPENDER_CONTRACT_ADDRESS}")
        
        # 获取 USDT 合约实例
        logger.info(f"正在获取 USDT 合约 ABI: {USDT_CONTRACT_ADDRESS} ...")
        usdt_contract = client.get_contract(USDT_CONTRACT_ADDRESS)
        
        # 定义无限额度 (2^256 - 1)
        MAX_UINT256 = (1 << 256) - 1
        logger.info(f"准备授权的额度: 无限大 (MAX_UINT256)")

        # 构建交易 集成到项目时不推荐使用approve方法
        logger.info("正在构建 approve 授权交易...")
        txn = (
            usdt_contract.functions.approve(SPENDER_CONTRACT_ADDRESS, MAX_UINT256)
            .with_owner(USER_ADDRESS)
            .fee_limit(100_000_000) 
            .build()
            .sign(priv_key)
        )
        
        # 广播交易
        logger.info("交易已签名，正在广播...")
        result = txn.broadcast()
        
        if result and result.get("result"):
            txid = result.get("txid")
            logger.info("广播成功！")
            logger.info(f"交易 Hash (TXID): {txid}")
            logger.info(f"可以在 TronScan 上查看此交易: https://nile.tronscan.org/#/transaction/{txid}")
            
            # 等待网络确认 
            logger.info("等待网络确认中 (约需 3-5 秒)...")
            time.sleep(5)
            logger.info("🎉 授权成功，等待链上状态为 SUCCESS，授权生效！")
            
        else:
            logger.error(f"❌ 广播失败。节点返回信息: {result}")

    except Exception as e:
        logger.error(f"❌ 脚本执行过程中发生异常: {e}")

if __name__ == "__main__":
    main()
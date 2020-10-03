pragma solidity ^0.5.0;
pragma experimental ABIEncoderV2;

import "@studydefi/money-legos/dydx/contracts/DydxFlashloanBase.sol";
import "@studydefi/money-legos/dydx/contracts/ICallee.sol";

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import './IUniswapV2Router02.sol';
import './IWeth.sol';

contract MoneyPrinter is ICallee, DydxFlashloanBase {
	address uni_addr = 0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D;
	//address solo_addr = 0x4EC3570cADaAEE08Ae384779B0f3A45EF85289DE; // kovan
	//address weth_addr = 0xd0A1E359811322d97991E03f863a0C30C2cF029C; // kovan
	//address dai_addr = 0xFf795577d9AC8bD7D90Ee22b6C1703490b6512FD; // kovan
	address solo_addr = 0x1E0447b19BB6EcFdAe1e4AE1694b0C3659614e4e;
	address weth_addr = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
	address dai_addr = 0x6B175474E89094C44Da98b954EedeAC495271d0F;
	address usdc_addr = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48;

    IUniswapV2Router02 uni = IUniswapV2Router02(uni_addr);
	ISoloMargin solo = ISoloMargin(solo_addr);

    address owner;

    constructor() public {
		owner = msg.sender;
    }

	modifier onlyOwner() {
		require(msg.sender == owner);
		_;
	}

	function setOwner(address _o) onlyOwner external {
		owner = _o;
	}

	function printMoney(
        address tokenIn,
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path,
        uint256 deadline
    ) onlyOwner external {
        IERC20 erc20 = IERC20(tokenIn);
        erc20.transferFrom(msg.sender, address(this), amountIn);
		erc20.approve(uni_addr, amountIn); // usdt -1 six decimal would fail!
        uni.swapExactTokensForTokens(amountIn, amountOutMin, path, msg.sender, deadline);
    }

    // This is the function that will be called postLoan
    // i.e. Encode the logic to handle your flashloaned funds here
    function callFunction(
        address sender,
        Account.Info memory account,
        bytes memory data
    ) public {
		(address tokenIn, uint amountIn, address[] memory path) = abi.decode(data, (address, uint256, address[]));

		IERC20(tokenIn).approve(uni_addr, amountIn);
		uni.swapExactTokensForTokens(amountIn, amountIn, path, address(this), now + 5 minutes);

		uint256 repayAmount = amountIn + 2;
        uint256 balance = IERC20(tokenIn).balanceOf(address(this));
        require(
            IERC20(tokenIn).balanceOf(address(this)) >= repayAmount,
            "Not enough funds to repay dydx loan!"
        );

        uint profit = IERC20(tokenIn).balanceOf(address(this)) - repayAmount; 
        IERC20(tokenIn).transfer(owner, profit);
    }

    function flashPrintMoney(
      address tokenIn, 
      uint256 amountIn, 
      address[] calldata path
	) onlyOwner external {
        // Get marketId from token address
        uint256 marketId = _getMarketIdFromTokenAddress(solo_addr, tokenIn);

        // Calculate repay amount (_amount + (2 wei))
        // Approve transfer from
        uint256 repayAmount = _getRepaymentAmountInternal(amountIn);
        IERC20(tokenIn).approve(solo_addr, repayAmount);

        Actions.ActionArgs[] memory operations = new Actions.ActionArgs[](3);

        operations[0] = _getWithdrawAction(marketId, amountIn);
        operations[1] = _getCallAction(
            abi.encode(tokenIn, amountIn, path)
        );
        operations[2] = _getDepositAction(marketId, repayAmount);

        Account.Info[] memory accountInfos = new Account.Info[](1);
        accountInfos[0] = _getAccountInfo();

        solo.operate(accountInfos, operations);
    }

    function() external payable {}
}

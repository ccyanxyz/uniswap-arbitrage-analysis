pragma solidity ^0.6.0;

interface IERC20 {
    function totalSupply() external view returns (uint supply);
    function balanceOf(address _owner) external view returns (uint balance);
    function transfer(address _to, uint _value) external returns (bool success);
    function transferFrom(address _from, address _to, uint _value) external returns (bool success);
    function approve(address _spender, uint _value) external returns (bool success);
    function allowance(address _owner, address _spender) external view returns (uint remaining);
    function decimals() external view returns(uint digits);
    event Approval(address indexed _owner, address indexed _spender, uint _value);
}

interface IUniswap {
    function swapExactETHForTokens(
        uint256 amountOutMin,
        address[] calldata path,
        address to,
        uint256 deadline
    ) external payable returns (uint256[] memory amounts);

    function getAmountsOut(uint256 amountIn, address[] calldata path)
        external
        view
        returns (uint256[] memory amounts);
        
        
    function swapETHForExactTokens(uint amountOut, address[] calldata path, address to, uint deadline)
      external
      payable
      returns (uint[] memory amounts);

    function swapExactTokensForTokens(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path,
        address to,
        uint256 deadline
    ) external returns (uint256[] memory amounts);

    function swapExactTokensForETH(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path,
        address to,
        uint256 deadline
    ) external returns (uint256[] memory amounts);
    
  function swapTokensForExactTokens(
      uint amountOut,
      uint amountInMax,
      address[] calldata path,
      address to,
      uint deadline
    ) external returns (uint[] memory amounts);
}

contract PrintMoney {
    address owner;
    address uni_addr = 0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D;
    IUniswap uni = IUniswap(0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D);
    //IERC20 usdt = IERC20(0xdAC17F958D2ee523a2206206994597C13D831ec7);
    //IERC20 weth = IERC20(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2);
    //IERC20 dai = IERC20(0x6B175474E89094C44Da98b954EedeAC495271d0F);
    
    //IERC20 weth = IERC20(0xc778417E063141139Fce010982780140Aa0cD5Ab); // ropsten weth
    //IERC20 dai = IERC20(0xaD6D458402F60fD3Bd25163575031ACDce07538D); // ropsten dai
    
    constructor() public {
        owner = msg.sender;
    }
    
    modifier onlyOwner() {
        require(msg.sender == owner);
        _;
    }
    
    function setOwner(address _newOwner) onlyOwner external {
        owner = _newOwner;
    }
    
    function approveToken(address token) onlyOwner external {
        IERC20 erc20 = IERC20(token);
        erc20.approve(uni_addr, uint(-1)); // usdt six decimal would fail!
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
        uni.swapExactTokensForTokens(amountIn, amountOutMin, path, msg.sender, deadline);
    }
}

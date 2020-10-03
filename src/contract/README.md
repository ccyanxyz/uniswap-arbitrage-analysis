# Defi-Arb-Bot
arbitrage bot, looks for prices differences on uniswap and kyber. Uses flashloan to make a trade between 2 exchanges. **Work in progress, use at your own risk**

    npm install
    
    curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -

    sudo apt-get install -y nodejs

    truffle migrate --network mainnet --reset
    
    node run-arbitrage.js

    1_initial_migration.js
    ======================
       Deploying 'Migrations'
       ----------------------
       > transaction hash:    0x9dcb132884a188d7fa15006bc9b8ce4a5fa203ecb0e2ceb384d7de185ae41301
       > Blocks: 1            Seconds: 12
       > contract address:    0xd8Ee44f8C6cb7AD9714B76077Ad1e3Bd08bdF855
       > block number:        10744238
       > block timestamp:     1598552780
       > account:             0x91Df1a2dA70F5a9085773ea483aA46F7c13a728F
       > balance:             1.143624444
       > gas used:            191943 (0x2edc7)
       > gas price:           92 gwei
       > value sent:          0 ETH
       > total cost:          0.017658756 ETH
       > Saving migration to chain.
       > Saving artifacts
       -------------------------------------
       > Total cost:         0.017658756 ETH
    2_deploy_contracts.js
    =====================
       Replacing 'Flashloan'
       ---------------------
       > transaction hash:    0x2e1f725ec0540ca2917cc018c03c7715b5090c109552ca0de2a20d6a0452abcf
       > Blocks: 1            Seconds: 4
       > contract address:    0x92E52890cfA407D9713A6cFcd7FB6F8d50B99FB2
       > block number:        10744242
       > block timestamp:     1598552813
       > account:             0x91Df1a2dA70F5a9085773ea483aA46F7c13a728F
       > balance:             0.930864232
       > gas used:            2270273 (0x22a441)
       > gas price:           92 gwei
       > value sent:          0 ETH
       > total cost:          0.208865116 ETH
       > Saving migration to chain.
       > Saving artifacts
       -------------------------------------
       > Total cost:         0.208865116 ETH
